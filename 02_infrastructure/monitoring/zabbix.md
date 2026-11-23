# Zabbix
<!-- reference: _reference/zabbix_official_notes.md -->

서버·네트워크 장비·애플리케이션을 에이전트, SNMP, HTTP 등으로 수집하고 웹 화면에서 알림까지 관리하는 오픈소스 모니터링 도구입니다. 이 문서만으로 구성 요소 이해 → Docker Compose로 서버 설치 → 호스트에 에이전트 설치 → 호스트 등록과 알림 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Zabbix 8.0 LTS (`zabbix/*:ubuntu-8.0.0` 이미지, 2026-11-23 확인)
- 예제 시험: 2026-11-23 컨테이너에서 실행. 3절 compose(PostgreSQL 17)로 서버·웹·agent2를 띄워 API 로그인, 에이전트 연결(available), `zabbix_get`을 확인했고, 4절 패키지 설치는 `ubuntu:24.04`와 `rockylinux/rockylinux:10` 컨테이너에서 agent2 8.0.0 설치까지 확인. 메일 알림 발송(5절)과 프록시는 미실행

## 목차

| 섹션                                                                                                  |
|-------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 구성 요소와 요구 사항](#2-구성-요소와-요구-사항)                             |
| [3. Docker Compose로 서버 설치](#3-docker-compose로-서버-설치) / [4. 에이전트 설치](#4-에이전트-설치) |
| [5. 호스트 등록과 알림](#5-호스트-등록과-알림) / [6. 운영](#6-운영) / [7. 검증](#7-검증)              |
| [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                    |

---

## 1. 개요

| 항목      | 내용                                                                         |
|-----------|------------------------------------------------------------------------------|
| 수집 방식 | 에이전트(passive·active), SNMP, IPMI, HTTP, JMX, 스크립트                    |
| 저장      | 관계형 DB(PostgreSQL·MySQL 계열)에 이력·추세 저장                            |
| 설정      | 웹 화면과 API로 호스트·템플릿·트리거·알림을 관리                             |
| 판 정책   | LTS는 5년 지원(일반 3년 + 연장 2년), Standard는 짧은 주기. 운영은 LTS를 고름 |
| 맞는 경우 | 장비 종류가 다양하고 SNMP 장비가 많은 환경, 웹 화면 중심의 운영 조직         |

Prometheus와의 차이는 [Zabbix vs Prometheus](./zabbix_vs_prometheus.md)에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 구성 요소와 요구 사항

```text
  [호스트: agent2] --10050(passive)--+        +--------------+
  [호스트: agent2] --10051(active)---+------> | Zabbix server | ----> [PostgreSQL]
  [SNMP 장비] <--------- 161 --------+        +--------------+
                                                  ^
                                [웹 화면 (Nginx + PHP)] ---- 사용자·API
```

| 구성 요소     | 역할                                       | 기본 포트 |
|---------------|--------------------------------------------|-----------|
| Zabbix server | 수집·트리거 계산·알림                      | 10051     |
| 웹 화면       | 설정과 조회 화면, API(`api_jsonrpc.php`)   | 80·443    |
| Zabbix agent2 | 호스트 지표 수집. Go로 작성, 플러그인 지원 | 10050     |
| Zabbix proxy  | 원격 구간 수집을 모아 서버로 전달 (선택)   | 10051     |
| DB            | 설정·이력 저장                             | 5432 등   |

| 항목       | 8.0 기준                                               |
|------------|--------------------------------------------------------|
| PostgreSQL | 15.0 ~ 18.x (TimescaleDB를 쓰면 2.20 ~ 2.31)           |
| PHP        | 8.2 ~ 8.5 (공식 이미지에는 포함)                       |
| 규모 예    | 지표 1,000개 안팎: 2 vCPU·8 GB, 10,000개: 4 vCPU·16 GB |

passive는 서버가 에이전트의 10050에 접속해 값을 묻고, active는 에이전트가 서버 10051에 접속해 값을 보냅니다. 방화벽은 쓰는 방향만 엽니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Docker Compose로 서버 설치

공식 저장소(zabbix-docker)에도 compose 파일이 있지만, 구성 요소를 이해하기 쉽게 최소 구성을 직접 씁니다.

```yaml
# compose.yaml
services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: zabbix
    volumes:
      - pg_data:/var/lib/postgresql/data
    restart: unless-stopped

  zabbix-server:
    image: zabbix/zabbix-server-pgsql:ubuntu-8.0.0
    environment:
      DB_SERVER_HOST: postgres
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: zabbix
    ports:
      - "10051:10051"            # active 에이전트가 접속
    depends_on:
      - postgres
    restart: unless-stopped

  zabbix-web:
    image: zabbix/zabbix-web-nginx-pgsql:ubuntu-8.0.0
    environment:
      DB_SERVER_HOST: postgres
      POSTGRES_USER: zabbix
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: zabbix
      ZBX_SERVER_HOST: zabbix-server
      PHP_TZ: Asia/Seoul
    ports:
      - "127.0.0.1:8080:8080"    # 외부 공개는 리버스 프록시·TLS 뒤에서
    depends_on:
      - zabbix-server
    restart: unless-stopped

  zabbix-agent:                  # 서버 자신을 감시하는 에이전트
    image: zabbix/zabbix-agent2:ubuntu-8.0.0
    hostname: zabbix-agent
    environment:
      ZBX_HOSTNAME: Zabbix server
      ZBX_SERVER_HOST: zabbix-server
    restart: unless-stopped

volumes:
  pg_data:
```

```bash
printf 'DB_PASSWORD=%s\n' "$(openssl rand -hex 16)" > .env && chmod 600 .env
docker compose up -d
docker compose logs zabbix-server | grep -E 'schema|Starting Zabbix Server'
# ** Database schema successfully created!
# Starting Zabbix Server. Zabbix 8.0.0 (revision ...)
```

- 첫 기동 때 서버 컨테이너가 DB 스키마를 만듭니다. DB가 준비되기 전에는 `connection refused`를 몇 번 남기고 다시 시도합니다.
- 이미지 태그는 `latest`나 `8.0-latest` 대신 판을 고정합니다. 이미지는 `ubuntu`·`alpine`·`ol`(Oracle Linux) 기반이 있습니다.
- `.env`는 저장소에 올리지 않습니다.

첫 로그인과 기본 호스트 정리입니다.

1. 브라우저로 `http://127.0.0.1:8080`에 접속해 `Admin` / `zabbix`로 로그인하고 바로 비밀번호를 바꿉니다(오른쪽 위 User settings).
2. 기본 `Zabbix server` 호스트는 에이전트 주소가 `127.0.0.1`이라 컨테이너 구성에서는 연결되지 않습니다. Data collection > Hosts에서 `Zabbix server`를 열어 Agent 인터페이스를 Connect to `DNS`, DNS name `zabbix-agent`로 바꿉니다.
3. 1~2분 뒤 호스트 목록의 ZBX 표시가 초록색이 되면 수집이 시작된 것입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 에이전트 설치

감시할 서버에는 공식 저장소에서 agent2를 설치합니다. 서버와 같은 메이저 판을 쓰는 것이 기본입니다.

```bash
# Ubuntu 24.04 (Debian은 경로의 ubuntu → debian, 파일 이름의 ubuntu24.04 → debian13 등)
wget https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest+ubuntu24.04_all.deb
sudo dpkg -i zabbix-release_latest+ubuntu24.04_all.deb
sudo apt-get update && sudo apt-get install -y zabbix-agent2

# RHEL·Rocky·Alma 10 (9는 el10 → el9, rhel/10 → rhel/9)
sudo rpm -Uvh https://repo.zabbix.com/zabbix/8.0/release/rhel/10/noarch/zabbix-release-latest-8.0.el10.noarch.rpm
sudo dnf install -y zabbix-agent2
```

EPEL을 쓰는 RHEL 계열은 EPEL의 Zabbix 패키지가 섞이지 않도록 `/etc/yum.repos.d/epel.repo`의 `[epel]` 절에 `excludepkgs=zabbix*`를 넣습니다.

`/etc/zabbix/zabbix_agent2.conf`에서 세 값을 바꿉니다. 설치 직후 기본값은 `Server=127.0.0.1`, `ServerActive=127.0.0.1`, `Hostname=Zabbix server`입니다.

```text
Server=zabbix.example.com          # passive: 이 주소에서 오는 요청만 받음
ServerActive=zabbix.example.com    # active: 이 서버로 값을 보냄
Hostname=web01                     # 웹 화면에 등록할 호스트 이름과 같게
```

```bash
sudo systemctl enable --now zabbix-agent2
sudo systemctl status zabbix-agent2 --no-pager
```

- Amazon Linux 2는 agent2 패키지가 없어 `zabbix-agent`(C 판)를 씁니다.
- 호스트 방화벽은 passive를 쓰면 서버 주소에서 오는 10050/tcp만 엽니다([ufw·firewalld](../../04_security/hardening/ufw_firewalld.md)).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 호스트 등록과 알림

| 순서 | 화면 위치                             | 할 일                                                                |
|------|---------------------------------------|----------------------------------------------------------------------|
| 1    | Data collection > Hosts > Create host | Host name은 에이전트 `Hostname`과 같게, Agent 인터페이스(주소·10050) |
| 2    | 같은 화면 Templates                   | `Linux by Zabbix agent` 연결 (active만 쓰면 `... agent active`)      |
| 3    | Alerts > Media types                  | Email 등 발송 수단 설정 후 Test                                      |
| 4    | Users > Users > 사용자 > Media        | 받을 주소와 심각도 지정                                              |
| 5    | Alerts > Actions                      | 조건(심각도·호스트 그룹)과 받을 사용자 지정                          |

같은 작업은 API로도 할 수 있습니다. 토큰은 Users > API tokens에서 만들고, 아래처럼 `Authorization: Bearer` 헤더로 보냅니다.

```bash
curl -s -H 'Content-Type: application/json-rpc' -H "Authorization: Bearer $ZBX_TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["host"]},"id":1}' \
  http://127.0.0.1:8080/api_jsonrpc.php
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영

| 작업       | 방법                                                                                       |
|------------|--------------------------------------------------------------------------------------------|
| 백업       | DB 덤프(`pg_dump`)와 compose 파일·`.env`. 이력이 크면 Housekeeping 보존 기간부터 정함      |
| 보존 기간  | Administration > Housekeeping에서 이력(history)·추세(trends) 기간 설정                     |
| 업그레이드 | 같은 메이저 안의 패치는 이미지 태그만 올림. 메이저 업그레이드는 릴리스 노트의 DB 변경 확인 |
| 부하       | Reports > System information, 서버 내부 지표(`zabbix[...]` 항목)로 큐·캐시 사용량 확인     |
| 원격 구간  | 지점·다른 망은 Zabbix proxy를 두어 수집을 모음                                             |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 검증

| 순서 | 확인 내용     | 명령·방법                                                                       | 기대 결과                         |
|------|---------------|---------------------------------------------------------------------------------|-----------------------------------|
| 1    | 컨테이너      | `docker compose ps`                                                             | 4개 모두 `Up`                     |
| 2    | 서버 기동     | `docker compose logs zabbix-server \| grep 'Starting Zabbix Server'`            | `Zabbix 8.0.0`                    |
| 3    | API           | `apiinfo.version` 호출 (5절 curl에서 method만 바꾸고 토큰 헤더 없이)            | `"result":"8.0.0"`                |
| 4    | 에이전트 응답 | `docker compose exec zabbix-server zabbix_get -s zabbix-agent -k agent.version` | `8.0.0`                           |
| 5    | 호스트 가용성 | Hosts 목록의 ZBX 표시                                                           | 초록색                            |
| 6    | 원격 호스트   | 서버에서 `zabbix_get -s <호스트> -k system.uptime`                              | 숫자 (거부되면 `Server=` 값 확인) |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                                    | 원인                                    | 해결 방법                                                       |
|-------------------------------------------------------------------------|-----------------------------------------|-----------------------------------------------------------------|
| API·웹에서 `table "dbversion" was not found`                            | 서버가 아직 스키마를 만드는 중          | 서버 로그에 `schema successfully created`가 나올 때까지 기다림  |
| `Cannot establish TCP connection to [[127.0.0.1]:10050]`                | 기본 호스트 인터페이스가 127.0.0.1      | 인터페이스를 에이전트 컨테이너 DNS 이름으로 변경 (3절)          |
| 에이전트 로그에 `connection from "<주소>" rejected, allowed hosts: ...` | 에이전트 `Server=`에 서버 주소가 없음   | `Server=`에 서버 주소(프록시를 쓰면 프록시 주소) 추가 후 재시작 |
| active 항목만 수집되지 않음                                             | `Hostname`이 웹 화면 호스트 이름과 다름 | 두 이름을 같게 맞춤 (대소문자 포함)                             |
| RHEL에서 Zabbix 패키지 판이 섞임                                        | EPEL의 Zabbix 패키지                    | EPEL에 `excludepkgs=zabbix*` (4절)                              |
| DB가 빠르게 커짐                                                        | 이력 보존 기간이 긺, 수집 주기가 짧음   | Housekeeping 기간 단축, 항목 주기 조정                          |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Zabbix vs Prometheus](./zabbix_vs_prometheus.md) — 수집 방식과 운영 비교
- [Prometheus + Grafana](./prometheus_grafana.md) — 지표 기반 모니터링
- [Docker Compose](../containers/docker_compose.md) — compose 파일 관리
- [ufw·firewalld](../../04_security/hardening/ufw_firewalld.md) — 10050·10051 포트 열기

---

## 참고 자료

- Zabbix Documentation 8.0: [Installation from containers](https://www.zabbix.com/documentation/current/en/manual/installation/containers) — ★★★☆☆
- Zabbix Documentation 8.0: [Requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements) — ★★★☆☆
- Zabbix: [Life cycle and release policy](https://www.zabbix.com/life_cycle_and_release_policy) — ★★★☆☆
- Zabbix: [Package repository](https://repo.zabbix.com/zabbix/8.0/release/) — ★★★☆☆

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
