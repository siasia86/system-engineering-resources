---
name: graylog-official-notes
description: Graylog Open 7.2 구성(MongoDB·Data Node), 공식 compose, preflight 절차, 기본 인덱스 세트, 컨테이너 확인 결과 정리.
tags:
  - graylog
  - logging
  - gelf
  - opensearch
last_checked: 2026-11-23
sources:
  - https://github.com/Graylog2/graylog2-server/tags
  - https://github.com/Graylog2/docker-compose
  - https://hub.docker.com/r/graylog/graylog/tags
  - https://go2docs.graylog.org/current/downloading_and_installing_graylog/docker_installation.htm
---

# Graylog 공식 자료 참조 노트

## 1. 판 (2026-11-23)

| 항목            | 내용                                                      | 근거                    |
|-----------------|-----------------------------------------------------------|-------------------------|
| Graylog         | 7.2.2 (태그 기준 최신 안정판, 7.3.0-alpha.1 존재)         | GitHub tags, Docker Hub |
| 이미지          | `graylog/graylog:7.2.2`, `graylog/graylog-datanode:7.2.2` | Docker Hub              |
| MongoDB         | 공식 compose는 `mongo:7.0`                                | Graylog2/docker-compose |
| GitHub releases | `latest` release API는 404 (태그만 게시)                  | 직접 조회               |

## 2. 공식 compose (Graylog2/docker-compose `open-core`)

- 구성: `mongodb`, `datanode`(OpenSearch를 감싼 Graylog Data Node), `graylog`.
- 필수 환경 변수: `GRAYLOG_PASSWORD_SECRET`(Data Node의 `GRAYLOG_DATANODE_PASSWORD_SECRET`과 같은 값), `GRAYLOG_ROOT_PASSWORD_SHA2`. 없으면 시작하지 않음(README).
- 공개 포트(모두 127.0.0.1): 9000(웹·API), 5044(Beats), 5140(Syslog TCP·UDP), 5555(Raw), 12201(GELF TCP·UDP), 13301·13302(Forwarder), Data Node 8999·9200·9300.
- compose 주석은 호스트 `vm.max_map_count=262144` 이상을 요구.
- Data Node를 쓰는 첫 기동은 preflight(초기 구성) 화면이 먼저 뜨고, 로그에 나온 임시 비밀번호로 접속. 구성이 끝나면 `GRAYLOG_ROOT_PASSWORD_SHA2`의 비밀번호를 씀. OpenSearch에 직접 연결하도록 설정하면 preflight 화면은 나오지 않음(README).

## 3. 컨테이너 시험 (2026-11-23)

- 공식 compose의 이미지 태그를 7.2.2로 고정해 기동. 로그에 `http://admin:<임시 비밀번호>@0.0.0.0:9000` 형식으로 preflight 접속 안내가 나옴.
- preflight를 REST API로 진행(헤더 `X-Requested-By` 필요):
  - `GET /api/data_nodes` → 상태 `UNCONFIGURED`
  - `POST /api/ca/create` `{"organization":"Graylog CA"}` → 201
  - `POST /api/renewal_policy` `{"mode":"AUTOMATIC","certificate_lifetime":"P30D"}` → 204
  - `POST /api/generate` → 204, Data Node 상태 `STARTING` → `CONNECTED`
  - `POST /api/status/finish-config` → `{"result":"FINISHED"}`
- 그 뒤 `admin`과 SHA2로 설정한 비밀번호로 `/api/system` → `7.2.2+94adc86`, `running`.
- GELF UDP 입력(`org.graylog2.inputs.gelf.udp.GELFUDPInput`, 12201)을 API로 만들어 `RUNNING`, GELF 메시지 3건 전송 후 `service:api AND level:3` 검색 결과 2건(`_service` 추가 필드가 `service`로 저장됨).
- 기본 인덱스 세트: 회전 `TimeBasedSizeOptimizingStrategy`(index_lifetime_min `P30D`, max `P40D`), 보존 `DeletionRetentionStrategy`, data tiering `hot_only`.
- 메모리 관찰값: Data Node 약 1.8 GiB, Graylog 약 0.6 GiB, MongoDB 약 0.2 GiB.

## 4. 확인하지 못한 것

- 웹 화면 조작(API로 대신함)과 Graylog Forwarder·Enterprise 기능
- 여러 노드 구성(`cluster` 디렉터리 예)과 지원 종료 일정
