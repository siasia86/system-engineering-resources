---
name: loki-official-notes
description: Grafana Loki·Alloy 판, Promtail 지원 종료, 저장·보존 설정, 컨테이너 확인 결과 정리.
tags:
  - loki
  - alloy
  - logging
  - grafana
last_checked: 2026-11-23
sources:
  - https://github.com/grafana/loki/releases
  - https://github.com/grafana/alloy/releases
  - https://grafana.com/docs/loki/latest/send-data/promtail/
  - https://grafana.com/docs/loki/latest/operations/storage/retention/
  - https://grafana.com/docs/loki/latest/query/
  - https://grafana.com/docs/alloy/latest/reference/components/loki/
---

# Grafana Loki 공식 문서 참조 노트

## 1. 판과 지원 (2026-11-23)

| 항목     | 내용                                                                                        | 근거            |
|----------|---------------------------------------------------------------------------------------------|-----------------|
| Loki     | 3.7.10 (2026-11-13), 이미지 `grafana/loki:3.7.10`                                           | GitHub releases |
| Alloy    | v1.22.0 (2026-11-13), 이미지 `grafana/alloy:v1.22.0`                                        | GitHub releases |
| Promtail | 2026-03-02 지원 종료(EOL). 이후 기능 개발은 Alloy에서만. 설정 변환 도구가 Alloy 문서에 있음 | Promtail 문서   |

## 2. 저장과 보존 (Retention 문서, 컨테이너 확인)

- 보존 기간은 `limits_config`의 `retention_period`(전체) 또는 `retention_stream`(선택자별)로 정합니다. `retention_stream` 규칙은 24시간 이상이어야 합니다.
- 보존은 Compactor가 처리하며 `compactor.retention_enabled: true`가 필요하고, 인덱스 주기가 24h일 때만 동작합니다.
- 이미지 기본 설정(`/etc/loki/local-config.yaml`)으로 띄우면 `/config`에서 `retention_enabled: false`, `retention_period: 0s`였습니다. 스키마는 `tsdb`·`filesystem`·`v13`, 인덱스 주기 `1d`.
- 3.7.10 이미지에는 `cat` 같은 셸 도구가 없어 `docker exec`로 파일을 볼 수 없고, 실제 값은 HTTP `/config`로 확인했습니다.

## 3. 컨테이너 시험 (2026-11-23)

- Loki(기본 설정) + Alloy(`local.file_match` → `loki.source.file` → `loki.process`(json·labels) → `loki.write`)로 NDJSON 로그 3줄 수집.
  - `/ready` → `ready`, `/loki/api/v1/status/buildinfo` → `3.7.10`
  - 스트림 라벨: `job`, `filename`, `level`(json에서 뽑음), `service_name`, `detected_level`
  - `sum by (level) (count_over_time({job="app"} | json [1h]))` → error 2, info 1
  - `{job="app", level="error"} |= "timeout"` → 2줄
  - Alloy `/-/ready` → 200
- 보존 30일 설정 파일(compactor `retention_enabled: true`, `delete_request_store: filesystem`, `retention_period: 720h`)로 기동 → `/config`에 `retention_period: 30d`, push API 204, 조회 성공.
- 기동 직후 로그에 `msg="error getting ingester clients" err="empty ring"`가 한 번 나왔고 이후 동작에는 영향이 없었습니다.
- 메모리 관찰값: Loki 약 46 MiB, Alloy 약 239 MiB.

## 4. 확인하지 못한 것

- 객체 저장소(S3 등) 구성과 분산(simple scalable·microservices) 배포
- 보존 기간 경과 뒤 실제 삭제 동작(시간이 필요해 미확인)
