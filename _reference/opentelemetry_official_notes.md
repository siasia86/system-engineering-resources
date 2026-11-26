---
name: opentelemetry-official-notes
description: OpenTelemetry Collector·Python SDK·시맨틱 규약 판, 0.166.0 구성 요소 이름 변경(밑줄 형식), 배포판, 컨테이너 시험 결과 정리.
tags:
  - opentelemetry
  - otlp
  - collector
  - tracing
last_checked: 2026-11-26
sources:
  - https://github.com/open-telemetry/opentelemetry-collector-releases/releases
  - https://github.com/open-telemetry/opentelemetry-collector-contrib/releases
  - https://github.com/open-telemetry/opentelemetry-python/releases
  - https://github.com/open-telemetry/semantic-conventions/releases
  - https://github.com/open-telemetry/opentelemetry-specification/releases
  - https://opentelemetry.io/docs/collector/configuration/
  - https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/
---

# OpenTelemetry 공식 자료 참조 노트

## 1. 판 (GitHub 릴리스, 2026-11-26 확인)

| 대상                       | 판                | 날짜       |
|----------------------------|-------------------|------------|
| Collector 배포판(releases) | v0.166.0          | 2026-11-24 |
| Collector contrib          | v1.5.0 / v0.166.0 | 2026-11-24 |
| Python SDK                 | 1.45.2 / 0.66b2   | 2026-10-29 |
| 시맨틱 규약                | v1.45.0           | 2026-11-02 |
| 사양(specification)        | v1.63.0           | 2026-11-23 |

- 0.166.0 배포판 변경: 배포판마다 설정 스키마 생성, otelcol-k8s Windows 386·arm64 바이너리 추가.
- 이전 판: 0.165.0(11-07), contrib 0.165.1(11-09), 0.164.1(10-26).

## 2. 배포판 (releases 저장소 `distributions/`, v0.166.0)

- otelcol, otelcol-contrib, otelcol-k8s, otelcol-otlp, otelcol-prometheus, otelcol-ebpf-profiler.
- 이미지 `otel/opentelemetry-collector`, `-contrib`, `-k8s`, `-otlp`의 0.166.0 태그가 있음(`docker manifest inspect`로 확인). contrib 이미지 크기 529MB.

## 3. 구성 요소 이름 (contrib 0.166.0 `components` 출력)

- 밑줄 형식: `otlp_grpc`, `otlp_http`(exporter), `host_metrics`, `file_log`(receiver), `span_metrics`(connector), `load_balancing`(exporter).
- 예전 이름은 동작하지만 경고: `"otlp" alias is deprecated; use "otlp_grpc" instead`, `"hostmetrics" alias is deprecated; use "host_metrics" instead`.
- receiver `otlp`는 이름 그대로이며 경고 없음.
- `attributes`, `resource`, `redaction`, `tail_sampling`, `health_check`, `pprof`, `prometheus`는 이름 그대로 목록에 있음.

## 4. 컨테이너 시험 (2026-11-26)

| 항목                            | 결과                                                                      |
|---------------------------------|---------------------------------------------------------------------------|
| `validate` 정상 설정            | 종료 코드 0                                                               |
| `validate` 틀린 이름            | 종료 코드 1, `references exporter "otlp/jaegerx" which is not configured` |
| health_check                    | `{"status":"Server available",...}`                                       |
| Python SDK → OTLP/HTTP          | span 3개 수신(debug `"resource spans": 1, "spans": 3`)                    |
| resource processor              | `deployment.environment.name=test`가 Jaeger에 보임                        |
| tail_sampling status_code ERROR | 정상 트레이스 버려짐(Jaeger 404), 오류 트레이스 남음(200)                 |

- `OTEL_EXPORTER_OTLP_ENDPOINT=http://<collector>:4318`만 주어 HTTP 내보내기가 동작함(신호별 경로는 SDK가 붙임).
- 미실행: Kubernetes 배포, 자동 계측, TLS 수신, 지표·로그의 실제 백엔드 저장.
