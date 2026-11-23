# Graylog
<!-- reference: _reference/graylog_official_notes.md -->

Syslog, GELF, Beats 같은 여러 입력으로 로그를 받아 저장·검색하고 알림을 거는 로그 관리 도구입니다. 저장은 OpenSearch 기반 Data Node가, 설정은 MongoDB가 맡습니다. 이 문서만으로 구성 이해 → 공식 Docker Compose로 설치와 초기 구성(preflight) → 입력 만들기와 로그 보내기 → 보존 설정 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Graylog Open 7.2.2 (2026-11-23 확인)
- 예제 시험: 2026-11-23 공식 compose(태그만 7.2.2로 고정)를 컨테이너로 실행해 preflight 완료, GELF UDP 입력 생성, 메시지 전송·검색, 기본 인덱스 세트를 API로 확인. 웹 화면 조작과 Forwarder·여러 노드 구성은 미실행

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 구성 요소](#1-구성-요소) / [2. 설치](#2-설치) / [3. 초기 구성 (preflight)](#3-초기-구성-preflight) |
| [4. 입력과 로그 보내기](#4-입력과-로그-보내기) / [5. 보존 기간](#5-보존-기간) / [6. 검증](#6-검증)     |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                     |

---

## 1. 구성 요소

```text
[서버 syslog] ----5140----+
[앱 GELF] -------12201----+--> [Graylog :9000] --> [Data Node (OpenSearch)]
[Filebeat] ------5044-----+          |
                                     +--> [MongoDB] (설정·사용자·입력 정의)
```

| 구성 요소 | 역할                                         | 포트      |
|-----------|----------------------------------------------|-----------|
| Graylog   | 입력 수신, 처리 규칙, 검색 화면·API, 알림    | 9000      |
| Data Node | 로그 저장·검색 (OpenSearch를 Graylog가 관리) | 8999·9200 |
| MongoDB   | 설정 저장                                    | 27017     |

| 입력   | 포트  | 쓰는 곳                                          |
|--------|-------|--------------------------------------------------|
| Syslog | 5140  | 리눅스 rsyslog·네트워크 장비                     |
| GELF   | 12201 | 앱이 JSON 구조로 직접 보냄, Docker 로그 드라이버 |
| Beats  | 5044  | Filebeat로 파일 로그                             |
| Raw    | 5555  | 한 줄 텍스트                                     |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

공식 compose 저장소(Graylog2/docker-compose)의 `open-core`를 씁니다. 이미지 태그는 판을 고정합니다.

```bash
git clone https://github.com/Graylog2/docker-compose.git
cd docker-compose/open-core
sed -i 's#graylog-datanode:7.2}#graylog-datanode:7.2.2}#; s#graylog/graylog:7.2}#graylog/graylog:7.2.2}#' docker-compose.yml

# 비밀값 두 개 (없으면 시작하지 않음)
read -rsp 'admin 비밀번호: ' ROOT_PW; echo
printf 'GRAYLOG_PASSWORD_SECRET=%s\nGRAYLOG_ROOT_PASSWORD_SHA2=%s\n' \
  "$(openssl rand -hex 48)" "$(printf %s "$ROOT_PW" | sha256sum | cut -d' ' -f1)" > .env
chmod 600 .env

sysctl vm.max_map_count          # 262144 이상이어야 함 (Data Node의 OpenSearch)
docker compose up -d
```

- 공식 compose는 모든 포트를 `127.0.0.1`에만 엽니다. 다른 서버에서 보내려면 필요한 입력 포트만 바꾸고 방화벽으로 보내는 쪽 주소만 허용합니다.
- 메모리는 시험에서 Data Node 약 1.8 GB, Graylog 약 0.6 GB, MongoDB 약 0.2 GB를 썼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 초기 구성 (preflight)

Data Node를 쓰는 첫 기동은 일반 화면 대신 초기 구성 화면이 뜹니다.

```bash
docker compose logs graylog | grep -A2 'initial configuration is accessible'
# Try clicking on http://admin:<임시 비밀번호>@0.0.0.0:9000
```

1. 브라우저로 `http://127.0.0.1:9000`에 접속해 `admin`과 로그의 임시 비밀번호로 들어갑니다.
2. 화면 순서대로 CA를 만들고, 인증서 갱신 정책을 정한 뒤, Data Node 인증서를 발급합니다.
3. Data Node가 연결되면 구성 완료를 눌러 일반 기동으로 넘어갑니다. 화면 문구는 판마다 다를 수 있어 아래 API 순서와 같은 단계로 보면 됩니다.
4. Graylog가 다시 뜨면 `admin`과 `.env`를 만들 때 넣은 비밀번호로 로그인합니다.

같은 절차를 API로 할 수도 있습니다(시험에서 확인한 순서, 헤더 `X-Requested-By` 필요).

```bash
A="curl -s -u admin:<임시 비밀번호> -H X-Requested-By:cli -H Content-Type:application/json"
$A http://127.0.0.1:9000/api/data_nodes                                  # UNCONFIGURED
$A -X POST http://127.0.0.1:9000/api/ca/create -d '{"organization":"Graylog CA"}'
$A -X POST http://127.0.0.1:9000/api/renewal_policy -d '{"mode":"AUTOMATIC","certificate_lifetime":"P30D"}'
$A -X POST http://127.0.0.1:9000/api/generate
$A http://127.0.0.1:9000/api/data_nodes                                  # CONNECTED가 될 때까지
$A -X POST http://127.0.0.1:9000/api/status/finish-config                # {"result":"FINISHED"}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 입력과 로그 보내기

입력은 System > Inputs에서 만듭니다. GELF UDP 입력을 API로 만드는 예입니다.

```bash
A="curl -s -u admin:<비밀번호> -H X-Requested-By:cli -H Content-Type:application/json"
$A -X POST http://127.0.0.1:9000/api/system/inputs -d '{
  "title": "gelf-udp", "type": "org.graylog2.inputs.gelf.udp.GELFUDPInput", "global": true,
  "configuration": {"bind_address": "0.0.0.0", "port": 12201, "recv_buffer_size": 262144}
}'
```

GELF 메시지는 JSON이고, 밑줄(`_`)로 시작하는 키는 추가 필드가 됩니다(`_service` → `service`). 같은 compose 네트워크에서 보내는 예입니다.

```bash
printf '{"version":"1.1","host":"web01","short_message":"payment timeout","level":3,"_service":"api"}' \
  | docker run --rm -i --network open-core_graylog busybox nc -u -w1 server 12201
```

| 보내는 쪽       | 방법                                                                                      |
|-----------------|-------------------------------------------------------------------------------------------|
| rsyslog         | `*.* @graylog.example.com:5140;RSYSLOG_SyslogProtocol23Format` (UDP 예)                   |
| Docker 컨테이너 | `docker run --log-driver gelf --log-opt gelf-address=udp://graylog.example.com:12201 ...` |
| Filebeat        | `output.logstash.hosts: ["graylog.example.com:5044"]` + Beats 입력                        |

검색은 Search 화면에서 `service:api AND level:3`처럼 필드 이름으로 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 보존 기간

로그는 인덱스 세트(System > Indices) 단위로 보존합니다. 7.2.2 기본 인덱스 세트는 다음과 같습니다.

| 항목        | 기본값                                                            |
|-------------|-------------------------------------------------------------------|
| 회전        | 크기를 보며 시간 기준으로 회전 (인덱스 수명 최소 30일, 최대 40일) |
| 보존        | 기간이 지난 인덱스 삭제                                           |
| 데이터 계층 | hot만 사용                                                        |

로그 종류마다 보존 기간이 다르면 인덱스 세트를 따로 만들고, Streams에서 규칙(예: `service`가 `audit`)으로 메시지를 그 세트로 보냅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용 | 명령·방법                                                         | 기대 결과                        |
|------|-----------|-------------------------------------------------------------------|----------------------------------|
| 1    | 컨테이너  | `docker compose ps`                                               | 3개 모두 실행 중                 |
| 2    | 판·상태   | `curl -s -u admin:… http://127.0.0.1:9000/api/system`             | `7.2.2`, `"lifecycle":"running"` |
| 3    | Data Node | `curl -s -u admin:… http://127.0.0.1:9000/api/data_nodes`         | `CONNECTED`                      |
| 4    | 입력      | `curl -s -u admin:… http://127.0.0.1:9000/api/system/inputstates` | `gelf-udp` `RUNNING`             |
| 5    | 수신·검색 | 4절 메시지 전송 후 Search에서 `service:api`                       | 보낸 메시지가 보임               |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                                                        | 원인                                            | 해결 방법                                                       |
|-----------------------------------------------------------------------------|-------------------------------------------------|-----------------------------------------------------------------|
| `docker compose up`이 `Please configure GRAYLOG_PASSWORD_SECRET ...`로 멈춤 | `.env`의 비밀값 미설정                          | 2절처럼 `.env` 작성                                             |
| 로그인 화면 대신 인증 창이 계속 뜸                                          | preflight 단계라 임시 비밀번호가 필요           | 로그의 `initial configuration is accessible` 아래 비밀번호 사용 |
| Data Node가 `STARTING`에서 넘어가지 않음                                    | `vm.max_map_count` 부족, 메모리 부족            | 호스트 값을 262144 이상으로, 메모리 여유 확인                   |
| 메시지를 보냈는데 검색되지 않음                                             | 입력이 없음·중지, 포트가 127.0.0.1에만 열림     | `inputstates` 확인, compose 포트 바인딩 확인                    |
| API 쓰기 요청이 거부됨                                                      | `X-Requested-By` 헤더 없음                      | 헤더 추가                                                       |
| 두 비밀값 중 하나를 바꾼 뒤 Data Node 연결 실패                             | `GRAYLOG_PASSWORD_SECRET`과 Data Node 값이 다름 | 두 컨테이너에 같은 값 사용                                      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Elastic Stack 로그 수집](./elastic_stack.md) · [Grafana Loki](./loki.md) — 다른 로그 저장소
- [로그 수집 100 GB 규모](./log_aggregation_100gb.md) — 규모별 설계
- [ufw·firewalld](../../04_security/hardening/ufw_firewalld.md) — 입력 포트 열기

---

## 참고 자료

- GitHub: [Graylog2/docker-compose](https://github.com/Graylog2/docker-compose) — ★★★☆☆
- Graylog Docs: [Docker installation](https://go2docs.graylog.org/current/downloading_and_installing_graylog/docker_installation.htm) — ★★★☆☆
- Docker Hub: [graylog/graylog tags](https://hub.docker.com/r/graylog/graylog/tags) — 7.2.2 확인 2026-11-23 — ★★★☆☆

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
