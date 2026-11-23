# Grafana Loki
<!-- reference: _reference/loki_official_notes.md -->

로그 본문은 색인하지 않고 라벨(job, host 같은 이름표)만 색인해 저장 비용을 줄이는 로그 저장소입니다. Prometheus처럼 라벨로 고르고 Grafana에서 봅니다. 이 문서만으로 구성 이해 → Docker Compose로 Loki와 수집기(Alloy) 띄우기 → LogQL 조회 → 보존 기간 설정 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Loki 3.7.10, Grafana Alloy v1.22.0 (2026-11-23 확인)
- 예제 시험: 2026-11-23 3절 compose와 5절 설정 파일을 컨테이너로 실행해 수집, 라벨, LogQL 조회, 보존 설정 반영을 확인. 객체 저장소(S3 등)와 분산 배포, 보존 기간 경과 뒤 삭제는 미실행

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 수집기](#2-수집기) / [3. Docker Compose로 구성](#3-docker-compose로-구성) |
| [4. LogQL](#4-logql) / [5. 보존 기간과 저장소](#5-보존-기간과-저장소) / [6. 검증](#6-검증)         |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                 |

---

## 1. 개요

```text
[앱 로그 파일] --> [Alloy] --push--> [Loki :3100] <--LogQL-- [Grafana]
                   (라벨 붙임)        (라벨만 색인, 본문은 압축 chunk)
```

| 항목      | Loki                                    | Elasticsearch         |
|-----------|-----------------------------------------|-----------------------|
| 색인      | 라벨만                                  | 본문 전체 (역색인)    |
| 저장 비용 | 낮음 (객체 저장소에 chunk)              | 높음 (색인 크기만큼)  |
| 조회      | 라벨로 범위를 좁힌 뒤 본문 필터         | 본문 검색이 빠름      |
| 맞는 경우 | Grafana·Prometheus를 이미 씀, 대량 로그 | 본문 검색·분석이 많음 |

라벨은 값의 종류가 적은 것(서비스, 환경, 수준)만 씁니다. 사용자 ID·요청 ID처럼 값이 계속 늘어나는 것을 라벨로 만들면 스트림이 폭증해 성능이 떨어집니다. 그런 값은 본문에 두고 필터로 찾습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 수집기

| 수집기   | 상태                                                               |
|----------|--------------------------------------------------------------------|
| Alloy    | 현재 공식 수집기. 로그·지표·추적을 한 에이전트로                   |
| Promtail | 2026-03-02 지원 종료. 새로 쓰지 않고 Alloy로 옮김 (변환 도구 있음) |
| 그 밖    | Fluent Bit, OpenTelemetry Collector도 Loki로 보낼 수 있음          |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Docker Compose로 구성

```yaml
# compose.yaml
services:
  loki:
    image: grafana/loki:3.7.10
    command: ["-config.file=/etc/loki/config.yaml"]
    ports:
      - "127.0.0.1:3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/config.yaml:ro   # 5절 설정
      - loki_data:/loki

  alloy:
    image: grafana/alloy:v1.22.0
    command: ["run", "--server.http.listen-addr=0.0.0.0:12345", "/etc/alloy/config.alloy"]
    ports:
      - "127.0.0.1:12345:12345"   # Alloy 상태 화면
    volumes:
      - ./config.alloy:/etc/alloy/config.alloy:ro
      - ./logs:/var/log/app:ro
    depends_on:
      - loki

volumes:
  loki_data:
```

```text
// config.alloy
local.file_match "app" {
  path_targets = [{"__path__" = "/var/log/app/*.log", "job" = "app"}]
}

loki.source.file "app" {
  targets    = local.file_match.app.targets
  forward_to = [loki.process.app.receiver]
}

loki.process "app" {
  stage.json {
    expressions = { level = "level" }   // JSON 로그의 level 값을 꺼냄
  }
  stage.labels {
    values = { level = "" }             // 꺼낸 값을 라벨로
  }
  forward_to = [loki.write.default.receiver]
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

```bash
docker compose up -d
curl -s http://127.0.0.1:3100/ready        # ready
```

Grafana에서는 Connections > Data sources에 Loki를 추가하고 URL에 `http://loki:3100`(같은 compose 네트워크일 때)을 넣습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. LogQL

| 하려는 일          | LogQL                                                        |
|--------------------|--------------------------------------------------------------|
| 스트림 고르기      | `{job="app"}`                                                |
| 라벨로 좁히기      | `{job="app", level="error"}`                                 |
| 본문에 문자열 포함 | `{job="app"} \|= "timeout"`                                  |
| 문자열 제외        | `{job="app"} != "healthcheck"`                               |
| JSON 필드로 거르기 | `{job="app"} \| json \| service="api"`                       |
| 수준별 건수 (지표) | `sum by (level) (count_over_time({job="app"} \| json [5m]))` |
| 초당 에러 줄 수    | `sum(rate({job="app", level="error"}[5m]))`                  |

명령줄에서는 HTTP API로 같은 질의를 보낼 수 있습니다.

```bash
curl -s -G http://127.0.0.1:3100/loki/api/v1/query_range \
  --data-urlencode 'query={job="app", level="error"} |= "timeout"' \
  --data-urlencode 'since=1h'
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 보존 기간과 저장소

이미지 기본 설정은 보존이 꺼져 있어(`retention_enabled: false`) 로그가 지워지지 않습니다. 보존 기간을 정한 단일 노드 설정입니다.

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: "2026-01-01"
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h          # 보존은 24h 주기에서만 동작

compactor:
  working_directory: /loki/compactor
  retention_enabled: true
  delete_request_store: filesystem

limits_config:
  retention_period: 720h     # 30일
```

- 스트림별로 다르게 두려면 `limits_config.retention_stream`에 선택자와 기간(24h 이상)을 적습니다.
- 로그가 많으면 `object_store`를 S3 같은 객체 저장소로 바꿉니다. 이때 스키마 `from` 날짜를 새로 더해 바꾸고, 이미 있는 항목은 고치지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용 | 명령                                                                    | 기대 결과                        |
|------|-----------|-------------------------------------------------------------------------|----------------------------------|
| 1    | 기동      | `curl -s http://127.0.0.1:3100/ready`                                   | `ready`                          |
| 2    | 판        | `curl -s http://127.0.0.1:3100/loki/api/v1/status/buildinfo`            | `"version":"3.7.10"`             |
| 3    | 수집기    | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:12345/-/ready` | `200`                            |
| 4    | 라벨      | `curl -s http://127.0.0.1:3100/loki/api/v1/labels`                      | `job`, `level`, `filename` 등    |
| 5    | 조회      | 4절 curl 예                                                             | 넣은 error 줄                    |
| 6    | 보존 설정 | `curl -s http://127.0.0.1:3100/config \| grep retention`                | `retention_enabled: true`, `30d` |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                                      | 원인                              | 해결 방법                                               |
|-----------------------------------------------------------|-----------------------------------|---------------------------------------------------------|
| 기동 직후 `error getting ingester clients ... empty ring` | 링 구성이 끝나기 전               | 몇 초 뒤 `/ready`가 `ready`면 무시                      |
| 조회 결과가 비어 있음                                     | 라벨 이름·값이 다름, 시간 범위 밖 | `/loki/api/v1/labels`로 실제 라벨 확인, `since` 늘리기  |
| `too many outstanding requests`, 느린 조회                | 라벨 범위가 넓음, 스트림 폭증     | 라벨로 먼저 좁히고, 값이 많은 라벨을 없앰               |
| 디스크가 계속 참                                          | 보존 꺼짐 (기본)                  | 5절 compactor·`retention_period` 설정                   |
| 컨테이너 안에서 설정 파일을 보려는데 `cat` 없음           | 최소 이미지                       | `curl http://127.0.0.1:3100/config`로 적용된 값 확인    |
| Promtail 설정이 남아 있음                                 | 지원 종료된 수집기                | Alloy로 옮김 (`alloy convert --source-format=promtail`) |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Elastic Stack 로그 수집](./elastic_stack.md) · [Graylog](./graylog.md) — 본문 색인형 로그 저장소
- [로깅 도구 비교](./logging_saas_comparison.md) — Splunk·Papertrail 등 상용 제품과 비교
- [Prometheus + Grafana](../monitoring/prometheus_grafana.md) — 같은 라벨 방식의 지표 수집
- [로그 수집 100 GB 규모](./log_aggregation_100gb.md) — 규모별 설계

---

## 참고 자료

- Grafana Loki Docs: [Retention](https://grafana.com/docs/loki/latest/operations/storage/retention/) · [LogQL](https://grafana.com/docs/loki/latest/query/) — ★★★☆☆
- Grafana Loki Docs: [Promtail (EOL)](https://grafana.com/docs/loki/latest/send-data/promtail/) — ★★★☆☆
- Grafana Alloy Docs: [loki components](https://grafana.com/docs/alloy/latest/reference/components/loki/) — ★★★☆☆
- GitHub: [grafana/loki releases](https://github.com/grafana/loki/releases) — 3.7.10 확인 2026-11-23 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
