---
name: elastic-stack-official-notes
description: Elastic Stack(Elasticsearch·Kibana·Filebeat·Logstash·Elastic Agent) 로그 수집 구성, 판, data stream·ILM 기본값 정리.
tags:
  - elasticsearch
  - kibana
  - filebeat
  - logging
last_checked: 2026-11-23
sources:
  - https://github.com/elastic/elasticsearch/releases
  - https://github.com/elastic/beats/releases
  - https://www.elastic.co/docs/manage-data/ingest/tools
  - https://www.elastic.co/docs/reference/beats/filebeat
  - https://www.elastic.co/docs/reference/beats/filebeat/filebeat-input-filestream
  - https://www.elastic.co/docs/reference/beats/filebeat/ilm
---

# Elastic Stack 공식 문서 참조 노트

Elasticsearch 설치·보안 설정은 기존 `05_database/nosql/elasticsearch_install.md`가 다루고, 이 노트는 로그 수집 구성에 필요한 사실만 기록합니다.

## 1. 판 (2026-11-23)

| 구성 요소             | 판    | 근거                                                       |
|-----------------------|-------|------------------------------------------------------------|
| Elasticsearch         | 9.5.6 | GitHub releases (2026-11-02)                               |
| Beats (Filebeat 포함) | 9.5.6 | GitHub releases (2026-11-02)                               |
| Kibana                | 9.5.6 | `docker.elastic.co/kibana/kibana:9.5.6` 컨테이너 기동 확인 |

스택 구성 요소는 같은 판 번호로 함께 올립니다.

## 2. 수집 도구 (Ingest tools 문서)

| 도구                  | 공식 설명 요지                                                       |
|-----------------------|----------------------------------------------------------------------|
| Fleet와 Elastic Agent | 호스트에 Elastic Agent를 두고 로그·지표 수집을 Fleet로 중앙 관리     |
| Logstash              | 여러 소스의 데이터를 정규화해 원하는 목적지로 보냄                   |
| Beats                 | 운영 데이터를 Elasticsearch로 직접 또는 Logstash를 거쳐 보냄         |
| 애플리케이션 로그     | Filebeat·Elastic Agent·APM agent로 수집, 또는 ECS 형식으로 바꿔 수집 |

- Filebeat의 `filestream` 입력은 옛 `log` 입력을 개선한 대안입니다(filestream 문서 설명).

## 3. data stream과 ILM (Filebeat ILM 문서, 컨테이너 확인)

- ILM이 켜져 있으면(보통 기본) `setup.template.name`·`setup.template.pattern`은 무시됩니다.
- 기본 정책 이름은 `filebeat`입니다.
- 2026-11-23 9.5.6 컨테이너에서 확인한 값:
  - data stream 이름 `filebeat-9.5.6`, 첫 backing index `.ds-filebeat-9.5.6-2026.11.23-000001`
  - 기본 정책 `filebeat`: hot 단계 rollover `max_age: 30d`, `max_primary_shard_size: 50gb`, 삭제 단계 없음

## 4. 컨테이너 시험 (2026-11-23)

- 구성: Elasticsearch(단일 노드, 힙 512 MB, HTTP TLS 끔) + Kibana + Filebeat, 모두 9.5.6.
- 메모리 관찰값: Elasticsearch 약 0.96 GiB, Kibana 약 1.7 GiB, Filebeat 약 70 MiB.
- `filebeat test config` → `Config OK`, `filebeat test output` → `talk to server... OK`, `version: 9.5.6`.
- NDJSON 로그의 최상위 `"service":"api"`(문자열)는 색인되지 않고 버려졌습니다(`Failed to index 4 events ... events were dropped!`). ECS에서 `service`는 객체(`service.name`)라 매핑과 충돌한 것으로 판단했고, `{"service":{"name":"api"},"log":{"level":"error"}}` 형식은 3건 모두 색인·검색됐습니다.
- Kibana `/api/status`의 `overall.level`이 `available`.

## 5. 확인하지 못한 것

- 지원 종료 일정(EOL 페이지가 스크립트로 그려져 본문을 읽지 못함)
- Logstash·Elastic Agent(Fleet) 실행
