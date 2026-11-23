# Elastic Stack 로그 수집
<!-- reference: _reference/elastic_stack_official_notes.md -->

Elasticsearch에 로그를 모으고 Kibana로 찾아보는 구성을 수집 경로 중심으로 정리한 문서입니다. 이 문서만으로 구성 요소 고르기 → Docker Compose로 Elasticsearch·Kibana·Filebeat 띄우기 → 로그 형식과 보존 정책 → 검증까지 따라 할 수 있게 썼습니다. Elasticsearch 자체의 패키지 설치·보안 설정·검색 문법은 함께 보기 문서에 있습니다.

- 기준 판: Elasticsearch·Kibana·Filebeat 9.5.6 (2026-11-23 확인)
- 예제 시험: 2026-11-23 3절 compose를 컨테이너로 실행해 Filebeat 출력 연결, data stream 생성, 색인·검색, Kibana 상태를 확인. Logstash·Elastic Agent(Fleet)는 미실행

## 목차

| 섹션                                                                                          |
|-----------------------------------------------------------------------------------------------|
| [1. 구성 요소](#1-구성-요소) / [2. 수집기 고르기](#2-수집기-고르기)                           |
| [3. Docker Compose로 구성](#3-docker-compose로-구성) / [4. 로그 형식 (ECS)](#4-로그-형식-ecs) |
| [5. 보존 기간 (ILM)](#5-보존-기간-ilm) / [6. 검증](#6-검증) / [7. 트러블슈팅](#7-트러블슈팅)  |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                             |

---

## 1. 구성 요소

```text
[앱 로그 파일] --> [Filebeat] ----------------------> [Elasticsearch] <-- [Kibana]
                       \                                   ^
                        +--> [Logstash] (가공이 많을 때) --+
```

| 구성 요소     | 역할                                                | 기본 포트 |
|---------------|-----------------------------------------------------|-----------|
| Elasticsearch | 저장·검색. 로그는 data stream으로 쌓임              | 9200      |
| Kibana        | 검색(Discover)·대시보드·관리 화면                   | 5601      |
| Filebeat      | 호스트의 로그 파일을 읽어 전송                      | -         |
| Logstash      | 여러 소스를 받아 가공·변환 후 전송                  | 5044 등   |
| Elastic Agent | 로그·지표 수집을 한 에이전트로, Fleet에서 중앙 관리 | -         |

구성 요소는 같은 판 번호로 맞춰 함께 올립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 수집기 고르기

| 상황                                             | 고를 것                  |
|--------------------------------------------------|--------------------------|
| 서버 몇 대의 로그 파일을 그대로 보냄             | Filebeat                 |
| 여러 형식을 파싱·필드 변환·여러 목적지로 분기    | Filebeat → Logstash      |
| 에이전트가 수백 대이고 설정을 화면에서 일괄 관리 | Elastic Agent + Fleet    |
| 이미 Kafka로 로그를 모음                         | Logstash 또는 Kafka 입력 |

Filebeat는 파일 입력으로 `filestream`을 씁니다. 옛 `log` 입력을 개선한 대안입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Docker Compose로 구성

실습·소규모용 단일 노드 구성입니다. 운영에서는 HTTP TLS를 켜고 노드를 여러 대로 둡니다.

```yaml
# compose.yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.5.6
    environment:
      - discovery.type=single-node
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=false   # 실습용. 운영은 TLS 사용
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "127.0.0.1:9200:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -s -u \"elastic:$${ELASTIC_PASSWORD}\" http://localhost:9200/_cluster/health | grep -q -E '\"status\":\"(green|yellow)\"'"]
      interval: 10s
      retries: 30

  kibana:
    image: docker.elastic.co/kibana/kibana:9.5.6
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=kibana_system
      - ELASTICSEARCH_PASSWORD=${KIBANA_PASSWORD}
    ports:
      - "127.0.0.1:5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy

  filebeat:
    image: docker.elastic.co/beats/filebeat:9.5.6
    user: root
    command: ["filebeat", "-e", "--strict.perms=false"]
    environment:
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./logs:/var/log/app:ro
    depends_on:
      elasticsearch:
        condition: service_healthy

volumes:
  es_data:
```

```yaml
# filebeat.yml
filebeat.inputs:
  - type: filestream
    id: app-logs                 # 입력마다 고유한 id
    paths:
      - /var/log/app/*.log
    parsers:
      - ndjson:                  # 한 줄에 JSON 하나인 로그
          target: ""
          add_error_key: true

output.elasticsearch:
  hosts: ["http://elasticsearch:9200"]
  username: "elastic"            # 운영은 전송 전용 권한 사용자를 따로 만듦
  password: "${ELASTIC_PASSWORD}"
```

```bash
printf 'ELASTIC_PASSWORD=%s\nKIBANA_PASSWORD=%s\n' "$(openssl rand -hex 12)" "$(openssl rand -hex 12)" > .env
chmod 600 .env
. ./.env
docker compose up -d elasticsearch
# 상태가 green·yellow가 되면 kibana_system 비밀번호를 지정 (ELASTIC_PASSWORD로는 설정되지 않음)
curl -s -u "elastic:$ELASTIC_PASSWORD" -X POST http://127.0.0.1:9200/_security/user/kibana_system/_password \
  -H 'Content-Type: application/json' -d "{\"password\":\"$KIBANA_PASSWORD\"}"
docker compose up -d
```

- 메모리는 Elasticsearch 힙 512 MB 기준으로 Elasticsearch 약 1 GB, Kibana 약 1.7 GB를 썼습니다. 여유가 4 GB 이상인 곳에서 띄웁니다.
- Kibana는 `http://127.0.0.1:5601`에서 `elastic` 계정으로 로그인하고, Discover에서 data view를 `filebeat-*`로 만들어 로그를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 로그 형식 (ECS)

Filebeat가 만드는 인덱스 템플릿은 ECS(Elastic Common Schema) 필드 정의를 따릅니다. 앱이 JSON 로그를 쓸 때 ECS와 같은 이름의 필드를 다른 형태로 쓰면 그 이벤트는 색인되지 않습니다.

```text
# 색인되지 않음: ECS에서 service는 객체(service.name)인데 문자열로 씀
{"@timestamp":"2026-11-23T09:01:00Z","level":"error","message":"payment timeout","service":"api"}

# 색인됨: ECS 필드 이름과 형태를 따름
{"@timestamp":"2026-11-23T09:11:00Z","log":{"level":"error"},"message":"payment timeout","service":{"name":"api"}}
```

| 쓰려는 값    | ECS 필드       |
|--------------|----------------|
| 로그 수준    | `log.level`    |
| 서비스 이름  | `service.name` |
| 호스트 이름  | `host.name`    |
| 요청 추적 ID | `trace.id`     |
| 본문         | `message`      |

ECS를 따르기 어려우면 `ndjson`의 `target`을 `app` 같은 이름으로 정해 앱 필드를 한 객체 아래로 모읍니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 보존 기간 (ILM)

Filebeat는 data stream(`filebeat-<판>`)으로 쓰고, 기본 ILM 정책 `filebeat`를 붙입니다. 9.5.6에서 확인한 기본 정책은 hot 단계에서 30일 또는 주 샤드 50 GB마다 rollover하고, **삭제 단계가 없습니다**. 그대로 두면 로그가 계속 쌓이므로 보존 기간을 정합니다.

```bash
curl -s -u "elastic:$ELASTIC_PASSWORD" -X PUT http://127.0.0.1:9200/_ilm/policy/filebeat \
  -H 'Content-Type: application/json' -d '{
  "policy": {
    "phases": {
      "hot":    { "actions": { "rollover": { "max_age": "1d", "max_primary_shard_size": "50gb" } } },
      "delete": { "min_age": "30d", "actions": { "delete": {} } }
    }
  }
}'
```

- `min_age`는 rollover된 시점부터 셉니다. 위 예는 하루 단위로 나누고 30일 뒤 지웁니다.
- 정책을 바꾸면 이미 있는 backing index에도 다음 단계부터 적용됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용     | 명령                                                                       | 기대 결과                         |
|------|---------------|----------------------------------------------------------------------------|-----------------------------------|
| 1    | 클러스터 상태 | `curl -s -u elastic:… http://127.0.0.1:9200/_cluster/health`               | `green` 또는 `yellow`(단일 노드)  |
| 2    | 설정 문법     | `docker compose exec filebeat filebeat test config`                        | `Config OK`                       |
| 3    | 출력 연결     | `docker compose exec filebeat filebeat test output`                        | `talk to server... OK`            |
| 4    | data stream   | `curl … /_data_stream/filebeat-*`                                          | `filebeat-9.5.6`, 정책 `filebeat` |
| 5    | 색인 건수     | `curl … /filebeat-*/_count`                                                | 넣은 로그 줄 수                   |
| 6    | 검색          | `curl … /filebeat-*/_search` 에 `{"query":{"term":{"log.level":"error"}}}` | error 줄만 나옴                   |
| 7    | Kibana        | `curl -s http://127.0.0.1:5601/api/status`                                 | `overall.level`이 `available`     |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                                                | 원인                                 | 해결 방법                                                            |
|---------------------------------------------------------------------|--------------------------------------|----------------------------------------------------------------------|
| Filebeat 로그에 `Failed to index N events ... events were dropped!` | 로그 필드가 ECS 매핑과 충돌 (4절)    | 필드 이름을 ECS에 맞추거나 `target`으로 따로 모음                    |
| Kibana가 계속 `Kibana server is not ready yet`                      | `kibana_system` 비밀번호 미지정      | 3절의 비밀번호 지정 후 `docker compose restart kibana`               |
| Elasticsearch가 바로 종료                                           | 메모리 부족, `vm.max_map_count` 낮음 | 힙·호스트 메모리 확인, 운영 호스트는 `vm.max_map_count=1048576` 이상 |
| 같은 로그가 다시 들어옴                                             | filestream `id`를 바꿈               | 입력 `id`는 한 번 정하면 바꾸지 않음                                 |
| 디스크가 가득 참                                                    | 기본 ILM 정책에 삭제 단계 없음       | 5절처럼 delete 단계 추가                                             |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Elasticsearch 설치](../../05_database/nosql/elasticsearch_install.md) — 패키지 설치, 보안 초기 설정
- [Elasticsearch](../../05_database/nosql/nosql_elasticsearch.md) — 인덱스, 매핑, 검색 쿼리
- [로그 수집 100 GB 규모](./log_aggregation_100gb.md) · [100 TB 규모](./log_aggregation_100tb.md) — 규모별 설계
- [Kafka](./kafka.md) — 수집 앞단의 버퍼
- [Grafana Loki](./loki.md) · [Graylog](./graylog.md) — 다른 로그 저장소
- [로깅 도구 비교](./logging_saas_comparison.md) — Splunk·Papertrail 등 상용 제품과 비교

---

## 참고 자료

- Elastic Docs: [Ingest tools overview](https://www.elastic.co/docs/manage-data/ingest/tools) — ★★★☆☆
- Elastic Docs: [Filebeat filestream input](https://www.elastic.co/docs/reference/beats/filebeat/filebeat-input-filestream) · [Filebeat ILM](https://www.elastic.co/docs/reference/beats/filebeat/ilm) — ★★★☆☆
- Elastic Docs: [Elastic Common Schema](https://www.elastic.co/docs/reference/ecs) — ★★★☆☆
- GitHub: [elastic/elasticsearch releases](https://github.com/elastic/elasticsearch/releases) — 9.5.6 확인 2026-11-23 — ★★★☆☆

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
