# OpenTelemetry
<!-- reference: _reference/opentelemetry_official_notes.md -->

트레이스·지표·로그를 특정 업체에 묶이지 않는 형식(OTLP)으로 만들고 보내는 표준입니다. 앱에는 OpenTelemetry SDK를 넣고, 중간에 Collector를 두어 받은 데이터를 가공한 뒤 Jaeger·Prometheus 같은 자체 도구나 SaaS로 보냅니다. 이 문서만으로 구성 이해 → Collector 컨테이너 실행 → Python 앱 계측 → 샘플링 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Collector v0.166.0(contrib 배포판, 2026-11-24), Python SDK 1.45.2, 시맨틱 규약 1.45.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26 3~6절 설정과 코드를 컨테이너로 실행해 설정 검증, OTLP/HTTP 수신, 속성 추가, Jaeger 전달, tail sampling, 예전 구성 요소 이름의 경고를 확인. 지표·로그 파이프라인은 debug 출력까지만 확인했고 Kubernetes 배포, 자동 계측(zero-code), TLS 수신은 미실행

## 목차

| 섹션                                                                                                           |
|----------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Collector 구성 요소](#2-collector-구성-요소) / [3. Collector 실행](#3-collector-실행) |
| [4. 앱 계측 (Python)](#4-앱-계측-python) / [5. 샘플링](#5-샘플링) / [6. 검증](#6-검증)                         |
| [7. 운영 팁](#7-운영-팁) / [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기)                            |

---

## 1. 개요

```text
[앱 + SDK] --OTLP--> [Collector] --> 트레이스: Jaeger, Tempo, SaaS
 (span 생성)          수신·가공·전달  --> 지표: Prometheus, SaaS
                                      --> 로그: Loki, SaaS
```

| 용어             | 뜻                                                              |
|------------------|-----------------------------------------------------------------|
| 신호(signal)     | 트레이스, 지표, 로그(그리고 개발 중인 프로파일)                 |
| 트레이스·span    | 요청 하나의 전체 경로가 트레이스, 그 안의 작업 단위 하나가 span |
| 리소스(resource) | 데이터를 만든 주체의 속성. `service.name`, `service.version` 등 |
| OTLP             | OpenTelemetry 전송 규약. gRPC(포트 4317)와 HTTP(포트 4318)      |
| SDK              | 언어별 라이브러리. span을 만들고 내보냄                         |
| Collector        | 받은 데이터를 처리해 여러 곳으로 보내는 별도 프로그램           |
| 시맨틱 규약      | 속성 이름 표준. 예 `http.request.method`, `db.system.name`      |

- 앱은 OTLP로만 내보내고 보낼 곳은 Collector에서 정하면, 백엔드를 바꿔도 앱 코드를 고치지 않습니다.
- Collector 없이 SDK에서 백엔드로 바로 보낼 수도 있습니다. 작은 구성에서는 그렇게 시작하고, 샘플링·가공·여러 곳 전송이 필요해지면 Collector를 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Collector 구성 요소

설정 파일은 구성 요소를 정의하는 부분과 `service.pipelines`에서 그것을 연결하는 부분으로 나뉩니다. 정의만 하고 파이프라인에 넣지 않은 구성 요소는 동작하지 않습니다.

| 구분       | 하는 일                                       | 예                                                     |
|------------|-----------------------------------------------|--------------------------------------------------------|
| receivers  | 데이터를 받음                                 | `otlp`, `prometheus`, `file_log`, `host_metrics`       |
| processors | 거르기·속성 변경·묶기·샘플링                  | `memory_limiter`, `batch`, `resource`, `tail_sampling` |
| exporters  | 데이터를 보냄                                 | `otlp_grpc`, `otlp_http`, `debug`, `prometheus`        |
| connectors | 한 파이프라인 출력을 다른 파이프라인 입력으로 | `span_metrics`(span으로 지표 생성)                     |
| extensions | 데이터 흐름 밖의 기능                         | `health_check`, `pprof`, 인증                          |

배포판(distribution)은 들어 있는 구성 요소 묶음이 다릅니다.

| 배포판          | 이미지                                 | 용도                                  |
|-----------------|----------------------------------------|---------------------------------------|
| otelcol (core)  | `otel/opentelemetry-collector`         | 핵심 구성 요소만                      |
| otelcol-contrib | `otel/opentelemetry-collector-contrib` | 커뮤니티 구성 요소 포함(이 문서 기준) |
| otelcol-k8s     | `otel/opentelemetry-collector-k8s`     | Kubernetes용 묶음                     |
| otelcol-otlp    | -                                      | OTLP 수신·전송만                      |

- 들어 있는 구성 요소는 `otelcol-contrib components`로 확인합니다.
- 0.166.0의 구성 요소 이름은 밑줄 형식입니다(`host_metrics`, `file_log`, `span_metrics`, `load_balancing`, `otlp_grpc`). 예전 이름(`hostmetrics` 등)도 동작하지만 시작할 때 `"hostmetrics" alias is deprecated; use "host_metrics" instead` 같은 경고가 나옵니다. 인터넷의 예전 예시를 옮길 때 이름을 바꿉니다.
- 필요한 것만 넣은 배포판은 OpenTelemetry Collector Builder(`ocb`)로 만듭니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Collector 실행

OTLP로 받아 트레이스는 Jaeger로, 지표는 화면 출력(debug)으로 보내는 설정입니다. Jaeger 쪽 구성은 [Jaeger](./jaeger.md) 문서를 봅니다.

```yaml
# otelcol.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:            # 메모리 한도를 넘으면 데이터를 거절해 프로세스를 보호
    check_interval: 1s
    limit_percentage: 80
    spike_limit_percentage: 25
  batch: {}                  # 묶어서 보냄
  resource:
    attributes:
      - key: deployment.environment.name
        value: test
        action: upsert

exporters:
  otlp_grpc/jaeger:          # 형식: 종류/이름
    endpoint: jaeger:4317
    tls:
      insecure: true         # 같은 내부 네트워크 시험용. 운영은 TLS
  debug:
    verbosity: basic

extensions:
  health_check:
    endpoint: 0.0.0.0:13133

service:
  extensions: [health_check]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [otlp_grpc/jaeger, debug]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
```

```bash
# 설정 검증 (오류가 있으면 종료 코드 1)
docker run --rm -v "$PWD/otelcol.yaml:/etc/otelcol.yaml:ro" \
  otel/opentelemetry-collector-contrib:0.166.0 validate --config=/etc/otelcol.yaml

# 실행 (Jaeger와 같은 Docker 네트워크에 둠)
docker network create otel
docker run -d --name otelcol --network otel \
  -p 127.0.0.1:4318:4318 -p 127.0.0.1:13133:13133 \
  -v "$PWD/otelcol.yaml:/etc/otelcol.yaml:ro" \
  otel/opentelemetry-collector-contrib:0.166.0 --config=/etc/otelcol.yaml

curl -s 127.0.0.1:13133/      # {"status":"Server available",...}
docker logs otelcol 2>&1 | grep "Everything is ready"
```

- processor 순서는 `memory_limiter`를 맨 앞, `batch`를 샘플링 뒤 맨 끝에 둡니다.
- 내보내기 이름은 0.166.0에서 `otlp_grpc`·`otlp_http`입니다. 예전 이름 `otlp`도 동작하지만 시작할 때 `"otlp" alias is deprecated; use "otlp_grpc" instead` 경고가 나옵니다(받는 쪽 receiver 이름은 `otlp` 그대로).
- 포트를 밖에 열 때는 `127.0.0.1`에 묶거나 방화벽으로 출발지를 제한합니다. OTLP 수신은 기본으로 인증이 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 앱 계측 (Python)

```bash
pip install opentelemetry-sdk==1.45.2 opentelemetry-exporter-otlp-proto-http==1.45.2
```

```python
# app.py
import time
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import Status, StatusCode

provider = TracerProvider(resource=Resource.create(
    {"service.name": "order-api", "service.version": "1.0.0"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("demo")

with tracer.start_as_current_span("POST /orders") as root:
    root.set_attribute("http.request.method", "POST")
    with tracer.start_as_current_span("db.insert") as s:
        s.set_attribute("db.system.name", "postgresql")
        time.sleep(0.05)
    with tracer.start_as_current_span("payment.charge") as s:
        try:
            raise TimeoutError("payment gateway timeout")
        except TimeoutError as e:
            s.record_exception(e)
            s.set_status(Status(StatusCode.ERROR, str(e)))
    print("trace_id", format(root.get_span_context().trace_id, "032x"))

provider.shutdown()   # 남은 span을 보내고 끝냄
```

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318 python app.py
# trace_id bc0b9633...
```

- `OTEL_EXPORTER_OTLP_ENDPOINT`에 기본 주소만 주면 HTTP 내보내기가 신호별 경로(`/v1/traces`)를 붙입니다.
- 짧게 끝나는 프로그램은 `provider.shutdown()`을 부르지 않으면 묶여 있던 span이 보내지기 전에 끝날 수 있습니다.
- 자주 쓰는 표준 환경 변수(사양에 정의, 이 문서에서는 첫 번째만 시험):

| 변수                          | 뜻                                              |
|-------------------------------|-------------------------------------------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | 보낼 주소                                       |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc`, `http/protobuf`, `http/json`            |
| `OTEL_EXPORTER_OTLP_HEADERS`  | 인증 헤더(`키=값`, 쉼표로 구분)                 |
| `OTEL_SERVICE_NAME`           | `service.name`                                  |
| `OTEL_RESOURCE_ATTRIBUTES`    | 리소스 속성(`키=값`, 쉼표로 구분)               |
| `OTEL_TRACES_SAMPLER`         | 앞단 샘플링 방식(예 `parentbased_traceidratio`) |

- 웹 프레임워크·DB 드라이버는 계측 라이브러리(`opentelemetry-instrumentation-*`)나 자동 계측으로 span을 만들 수 있습니다. 이 문서에서는 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 샘플링

| 방식          | 위치      | 판단 시점          | 특징                                       |
|---------------|-----------|--------------------|--------------------------------------------|
| head sampling | SDK       | 트레이스 시작 때   | 가볍지만 오류 여부를 모르고 버림           |
| tail sampling | Collector | 트레이스가 모인 뒤 | 오류·느린 요청만 남길 수 있음, 메모리 필요 |

오류가 있는 트레이스만 남기는 tail sampling 예입니다. 3절 설정의 `processors`에 추가하고 파이프라인에 넣습니다.

```yaml
processors:
  tail_sampling:
    decision_wait: 5s          # 첫 span을 받은 뒤 판단까지 기다리는 시간
    policies:
      - name: errors-only
        type: status_code
        status_code:
          status_codes: [ERROR]

service:
  pipelines:
    traces:
      processors: [memory_limiter, resource, tail_sampling, batch]
```

시험 결과(정상 트레이스 1개, 오류 트레이스 1개 전송):

| 트레이스 | Jaeger 조회  |
|----------|--------------|
| 정상     | 404 (버려짐) |
| 오류     | 200 (남음)   |

- 한 트레이스의 span이 여러 Collector로 나뉘면 tail sampling이 전체를 보지 못합니다. 여러 대로 늘릴 때는 앞단에서 trace ID 기준으로 같은 Collector에 보내는 구성(`load_balancing` exporter)을 씁니다.
- 실제 운영에서는 "오류 전부 + 느린 요청 전부 + 나머지 일부 비율"처럼 정책을 여러 개 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용       | 방법                                              | 기대 결과                                     |
|------|-----------------|---------------------------------------------------|-----------------------------------------------|
| 1    | 설정 문법       | `otelcol-contrib validate --config=...`           | 종료 코드 0                                   |
| 2    | 기동            | `curl 127.0.0.1:13133/`                           | `Server available`                            |
| 3    | 수신            | 앱 실행 뒤 `docker logs otelcol` (debug exporter) | `Traces ... "resource spans": 1, "spans": 3`  |
| 4    | 속성 가공       | Jaeger에서 트레이스의 프로세스 속성 확인          | `deployment.environment.name=test`            |
| 5    | 부모·자식, 오류 | Jaeger에서 span 관계와 상태 확인                  | 자식 2개 `CHILD_OF`, `payment.charge`가 ERROR |
| 6    | 경고            | 시작 로그에서 `deprecated` 검색                   | 0줄                                           |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 운영 팁

- 앱 옆(사이드카·노드마다)에 가벼운 Collector를 두고, 중앙 Collector에서 샘플링·전송을 하는 2단 구성이 흔합니다.
- `service.name`은 반드시 정합니다. 없으면 백엔드에서 서비스별로 나뉘지 않습니다.
- 속성 값에 개인정보·토큰이 들어가지 않게 합니다. Collector의 `attributes`·`redaction` processor로 지울 수 있습니다.
- SaaS로 보낼 때 API 키는 Collector 설정 파일에 직접 쓰지 않고 `${env:변수}`로 환경 변수에서 읽습니다.
- Collector 판은 대략 2~3주마다 나옵니다(0.165.0 11-07, 0.166.0 11-24). 올리기 전에 릴리스 노트의 breaking change와 deprecated 경고를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                | 원인                                    | 조치                                                         |
|-----------------------------------------------------|-----------------------------------------|--------------------------------------------------------------|
| `references exporter "..." which is not configured` | 파이프라인에 적은 이름이 정의와 다름    | `exporters` 아래 이름과 `종류/이름`을 맞춤                   |
| 시작 때 `"..." alias is deprecated` 경고            | 0.166.0에서 바뀐 예전 구성 요소 이름    | 경고에 나온 새 이름(`otlp_grpc`, `host_metrics` 등)으로 바꿈 |
| 앱은 끝났는데 트레이스가 없음                       | 짧은 프로그램이 span을 보내기 전에 종료 | `provider.shutdown()` 호출                                   |
| 앱에서 연결 거부                                    | 주소·포트·프로토콜 불일치               | HTTP는 4318, gRPC는 4317. 환경 변수와 exporter 종류 대조     |
| tail sampling 뒤 일부 span만 남음                   | span이 여러 Collector로 나뉨            | trace ID 기준 부하 분산                                      |
| Collector 메모리가 계속 늘어남                      | 백엔드 장애로 재시도 대기열이 쌓임      | `memory_limiter` 설정, 백엔드 상태 확인                      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Jaeger](./jaeger.md) — 트레이스 저장·조회
- [Prometheus + Grafana](./prometheus_grafana.md) — 지표 저장·대시보드
- [Grafana Loki](../data_pipeline/loki.md) — 로그 저장
- [모니터링 SaaS 비교](./monitoring_saas_comparison.md) — OTLP를 받는 SaaS 비교

---

## 참고 자료

- OpenTelemetry Docs: [Collector](https://opentelemetry.io/docs/collector/) · [Configuration](https://opentelemetry.io/docs/collector/configuration/) — ★★★☆☆
- OpenTelemetry Docs: [Python](https://opentelemetry.io/docs/languages/python/) · [SDK Environment Variables](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/) — ★★★☆☆
- GitHub: [opentelemetry-collector-releases](https://github.com/open-telemetry/opentelemetry-collector-releases/releases) · [tail_sampling processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor) — ★★★☆☆
- OpenTelemetry: [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-26

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
