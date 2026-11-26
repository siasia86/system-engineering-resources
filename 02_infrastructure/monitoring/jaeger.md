# Jaeger
<!-- reference: _reference/jaeger_official_notes.md -->

분산 트레이스를 저장하고 화면에서 요청 경로를 따라가 보는 오픈소스 도구입니다. v2부터 OpenTelemetry Collector를 바탕으로 만들어져 OTLP를 바로 받고, 설정도 Collector와 같은 YAML 형식입니다. 이 문서만으로 단일 컨테이너 실행 → OpenTelemetry Collector와 연결 → Badger 저장소로 보존 → API 조회 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Jaeger v2.23.0 (2026-11-05), 함께 쓴 Collector v0.166.0 (2026-11-26 확인)
- 예제 시험: 2026-11-26 2~5절을 컨테이너로 실행해 OTLP 수신, Collector 경유 전달, Badger 저장소 재시작 뒤 보존, v3 API 조회, 볼륨 권한 오류를 확인. Elasticsearch·OpenSearch·Cassandra·ClickHouse 저장소, Kafka 구성, 보존 기간(TTL) 경과 뒤 삭제는 미실행. 웹 화면은 브라우저로 열어 보지 않았고 API로만 확인

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 단일 컨테이너 실행](#2-단일-컨테이너-실행) / [3. Collector와 연결](#3-collector와-연결) |
| [4. 저장소](#4-저장소) / [5. API로 조회](#5-api로-조회) / [6. 검증](#6-검증)                                     |
| [7. 운영 팁](#7-운영-팁) / [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기)                              |

---

## 1. 개요

```text
[앱 + OTel SDK] --OTLP--> [OTel Collector] --OTLP--> [Jaeger] --> [저장소]
                           (샘플링·가공)              :4317/4318    메모리, Badger,
                                                      UI :16686     Elasticsearch 등
```

| 항목     | 내용                                                                                       |
|----------|--------------------------------------------------------------------------------------------|
| 하는 일  | 트레이스 저장, 검색, span 타임라인 화면, 서비스 의존 관계                                  |
| 수신     | OTLP gRPC 4317, HTTP 4318                                                                  |
| 화면·API | 16686 (UI, `/api/v3/...`)                                                                  |
| 설정     | OpenTelemetry Collector 형식 YAML. 저장소·조회는 `jaeger_storage`·`jaeger_query` extension |
| v1       | 마지막 판 v1.76.0(2025-12-03). 새 구성은 v2로 함                                           |

- Jaeger는 트레이스만 다룹니다. 지표·로그는 Prometheus·Loki 같은 도구를 따로 씁니다.
- 앱 계측은 Jaeger 전용 클라이언트가 아니라 OpenTelemetry SDK로 합니다([OpenTelemetry](./opentelemetry.md) 4절).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 단일 컨테이너 실행

인수 없이 실행하면 메모리 저장소를 쓰는 올인원 구성으로 뜹니다. 재시작하면 데이터가 사라지므로 시험용입니다.

```bash
docker network create otel
docker run -d --name jaeger --network otel \
  -p 127.0.0.1:16686:16686 \
  jaegertracing/jaeger:2.23.0

docker logs jaeger 2>&1 | grep "Everything is ready"
```

- 브라우저에서 `http://127.0.0.1:16686`을 엽니다.
- 앱이 Jaeger로 바로 보내려면 `-p 127.0.0.1:4318:4318`도 열고 `OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318`로 보냅니다.
- 이미지는 사용자 `10001:10001`로 실행됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Collector와 연결

OpenTelemetry Collector에서 Jaeger의 OTLP gRPC 포트로 보냅니다. 두 컨테이너를 같은 Docker 네트워크에 둡니다.

```yaml
# otelcol.yaml 중 exporter 부분
exporters:
  otlp_grpc/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true      # 같은 내부 네트워크 시험용
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp_grpc/jaeger]
```

시험에서 Python 앱이 보낸 트레이스(span 3개)가 다음과 같이 저장됐습니다.

| span             | 관계            | 상태                           |
|------------------|-----------------|--------------------------------|
| `POST /orders`   | 루트            | 정상                           |
| `db.insert`      | `CHILD_OF` 루트 | 정상, 약 50ms                  |
| `payment.charge` | `CHILD_OF` 루트 | `error=true`, 예외 이벤트 기록 |

- Collector에서 붙인 리소스 속성(`deployment.environment.name`)도 그대로 보입니다.
- Collector를 거치면 Jaeger 앞에서 tail sampling으로 오류 트레이스만 남길 수 있습니다([OpenTelemetry](./opentelemetry.md) 5절).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 저장소

| 저장소                   | 용도                        | 이 문서 시험 |
|--------------------------|-----------------------------|--------------|
| memory                   | 시험. 재시작하면 사라짐     | 실행         |
| Badger                   | 단일 노드에 파일로 저장     | 실행         |
| Elasticsearch·OpenSearch | 운영에서 많이 씀, 여러 노드 | 미실행       |
| Cassandra                | 쓰기량이 많은 대규모        | 미실행       |
| ClickHouse               | 대규모 저장·SQL 조회        | 미실행       |

Badger로 저장하는 최소 설정입니다. 저장소 예시 파일은 Jaeger 저장소의 `cmd/jaeger/config-*.yaml`에 있습니다.

```yaml
# jaeger.yaml
service:
  extensions: [jaeger_storage, jaeger_query, healthcheckv2]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger_storage_exporter]

extensions:
  healthcheckv2:
    use_v2: true
    http:
      endpoint: 0.0.0.0:13133
  jaeger_query:
    storage:
      traces: main_store
  jaeger_storage:
    backends:
      main_store:
        badger:
          directories:
            keys: /badger/keys
            values: /badger/values
          ephemeral: false
          ttl:
            spans: 72h        # 보존 기간

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:

exporters:
  jaeger_storage_exporter:
    trace_storage: main_store
```

```bash
docker volume create jaeger-badger
# 이미지 사용자(10001)가 쓸 수 있게 볼륨 소유자를 맞춤
docker run --rm -v jaeger-badger:/badger alpine chown 10001:10001 /badger

docker run -d --name jaeger --network otel \
  -p 127.0.0.1:16686:16686 \
  -v jaeger-badger:/badger \
  -v "$PWD/jaeger.yaml:/etc/jaeger.yaml:ro" \
  jaegertracing/jaeger:2.23.0 --config=/etc/jaeger.yaml
```

- 시험에서 트레이스를 넣고 `docker restart jaeger` 뒤에도 같은 trace ID가 200으로 조회됐습니다.
- `jaeger_query.storage.traces`, `jaeger_storage.backends`의 이름, `jaeger_storage_exporter.trace_storage`가 모두 같은 이름(`main_store`)이어야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. API로 조회

v2.21.0(2026-09-14)에서 화면이 쓰지 않는 v1 HTTP 경로가 제거됐습니다. 스크립트는 v3 API를 씁니다.

```bash
# 서비스 목록
curl -s 127.0.0.1:16686/api/v3/services
# {"services":["order-api"]}

# 서비스의 작업(operation) 목록
curl -s "127.0.0.1:16686/api/v3/operations?service=order-api"

# trace ID로 조회 (OTLP JSON 형식으로 돌려줌)
curl -s 127.0.0.1:16686/api/v3/traces/<trace_id>
```

시험한 경로의 응답(v2.23.0):

| 경로                                | 응답 |
|-------------------------------------|------|
| `/api/v3/services`                  | 200  |
| `/api/v3/operations?service=...`    | 200  |
| `/api/v3/traces/<id>`               | 200  |
| `/api/traces/<id>` (v1)             | 200  |
| `/api/services` (v1)                | 404  |
| `/api/traces?service=...` (v1 검색) | 404  |

- 예전 블로그·스크립트의 `/api/services`는 v2.21.0 이상에서 404입니다.
- v3의 트레이스 응답은 OTLP JSON(`resourceSpans`) 형식이라 v1 응답(`data[].spans`)과 구조가 다릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용     | 방법                                             | 기대 결과                           |
|------|---------------|--------------------------------------------------|-------------------------------------|
| 1    | 기동          | `docker logs jaeger`                             | `Everything is ready`               |
| 2    | 수신          | 앱 실행 뒤 `/api/v3/services`                    | 앱의 `service.name`이 목록에 있음   |
| 3    | 트레이스 구조 | `/api/v3/traces/<id>` 또는 화면                  | span 3개, 부모·자식, 오류 span 표시 |
| 4    | 보존          | `docker restart jaeger` 뒤 같은 ID 조회 (Badger) | 200                                 |
| 5    | 화면          | `http://127.0.0.1:16686`에서 서비스 선택·검색    | 타임라인과 span 속성이 보임         |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 운영 팁

- UI·API에는 기본 인증이 없습니다. 밖에 열 때는 리버스 프록시(인증·TLS) 뒤에 둡니다.
- 트레이스는 양이 많습니다. Collector의 tail sampling으로 저장량을 줄이고, 저장소 TTL로 보존 기간을 정합니다.
- 운영 규모에서는 수집(collector 역할)과 조회(query 역할)를 나눠 띄우고, 저장소는 Elasticsearch·OpenSearch·Cassandra·ClickHouse 중 하나를 씁니다. 역할별 예시 설정은 Jaeger 저장소의 `cmd/jaeger/config-query.yaml` 등에 있습니다.
- Grafana에서 Jaeger를 데이터 소스로 붙여 지표·로그 화면과 함께 볼 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                | 원인                                       | 조치                                              |
|-----------------------------------------------------|--------------------------------------------|---------------------------------------------------|
| `mkdir /badger/keys: permission denied`로 바로 종료 | 볼륨 소유자가 root, 이미지 사용자는 10001  | 볼륨을 `10001:10001`로 `chown`                    |
| 재시작하면 트레이스가 사라짐                        | 기본 메모리 저장소                         | Badger 등 영속 저장소 설정, 볼륨 연결             |
| `/api/services`가 404                               | v2.21.0에서 v1 HTTP 경로 제거              | `/api/v3/services` 사용                           |
| 서비스 목록에 앱이 없음                             | Collector 전달 실패, `service.name` 없음   | Collector 로그의 exporter 오류, SDK 리소스 확인   |
| `cannot find factory for trace storage ...`         | 저장소 이름 불일치 또는 저장소 초기화 실패 | 세 곳의 저장소 이름 대조, 뒤따르는 오류 문구 확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [OpenTelemetry](./opentelemetry.md) — 앱 계측과 Collector
- [Prometheus + Grafana](./prometheus_grafana.md) — 지표와 대시보드
- [모니터링 SaaS 비교](./monitoring_saas_comparison.md) — 트레이스를 SaaS에 맡길 때

---

## 참고 자료

- Jaeger Docs: [Getting Started](https://www.jaegertracing.io/docs/latest/getting-started/) · [Configuration](https://www.jaegertracing.io/docs/latest/configuration/) — ★★★☆☆
- GitHub: [jaegertracing/jaeger releases](https://github.com/jaegertracing/jaeger/releases) · [CHANGELOG](https://github.com/jaegertracing/jaeger/blob/main/CHANGELOG.md) — ★★★☆☆
- GitHub: [cmd/jaeger 예시 설정](https://github.com/jaegertracing/jaeger/tree/main/cmd/jaeger) — ★★★☆☆

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
