# n8n + PostgreSQL Docker Compose Cheat Sheet

n8n 2.x와 PostgreSQL 기준입니다(2026-11-10 확인 stable 2.46.7). n8n 2.0부터 MySQL·MariaDB는 n8n 저장소로 쓸 수 없습니다.

## 목차

| 섹션                                                                                     |
|------------------------------------------------------------------------------------------|
| [1. 컨테이너 관리](#1-컨테이너-관리)                                                     |
| [2. 컨테이너 내부 접속](#2-컨테이너-내부-접속)                                           |
| [3. 이미지 관리](#3-이미지-관리)                                                         |
| [4. 데이터 초기화 / 볼륨 관리](#4-데이터-초기화--볼륨-관리)                              |
| [5. n8n 관리 명령어](#5-n8n-관리-명령어)                                                 |
| [6. n8n 환경 변수 (PostgreSQL / HTTP / HTTPS)](#6-n8n-환경-변수-postgresql--http--https) |
| [7. PostgreSQL 연결 확인](#7-postgresql-연결-확인)                                       |
| [8. 전체 초기화 (컨테이너 + 볼륨 + 네트워크)](#8-전체-초기화-컨테이너--볼륨--네트워크)   |

---

## 1. 컨테이너 관리
```bash
docker compose up -d                # 모든 서비스 시작 (백그라운드)
docker compose up                    # 모든 서비스 시작 (포그라운드)
docker compose down                  # 모든 서비스 중지 + 네트워크 제거
docker compose stop n8n              # 특정 서비스 중지
docker compose start n8n             # 특정 서비스 시작
docker compose restart n8n           # 특정 서비스 재시작
docker compose ps                    # 서비스 상태 확인
docker compose logs                  # 서비스 로그 확인
docker compose logs -f n8n           # 특정 서비스 실시간 로그
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 컨테이너 내부 접속
```bash
docker compose exec n8n sh                               # n8n 컨테이너 셸 접속 (Alpine 기반, 기본 셸 /bin/sh)
docker compose exec postgres bash                        # PostgreSQL 컨테이너 bash 접속 (Debian 기반 postgres 이미지)
docker compose exec postgres psql -U Secureuser123 -d n8n   # psql로 n8n 데이터베이스 접속
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 이미지 관리
```bash
docker compose pull                  # docker-compose.yml 기준 이미지 다운로드
docker compose build                 # Dockerfile 빌드
docker compose images                # 서비스별 이미지 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 데이터 초기화 / 볼륨 관리
```bash
# 이 프로젝트의 볼륨 확인 (기본 이름: <프로젝트 이름>_<volumes 키>)
docker compose volumes

# n8n + PostgreSQL 볼륨 초기화 후 재시작 (6절 예시의 volumes 키 n8n_storage·db_storage 기준)
docker compose down
docker volume rm <프로젝트 이름>_n8n_storage <프로젝트 이름>_db_storage
docker compose up -d

# 특정 서비스 컨테이너 + 익명 볼륨 삭제 (-s: 먼저 중지, 이름 있는 볼륨은 유지)
docker compose rm -s -v n8n
docker compose rm -s -v postgres

# 사용하지 않는 익명 볼륨 삭제 (-a: 이름 있는 볼륨 포함)
docker volume prune -f
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. n8n 관리 명령어
```bash
docker compose exec n8n n8n --version                                   # 실행 중 n8n 버전 확인
docker compose exec n8n n8n export:workflow --all --output=/home/node/.n8n/workflows/backup.json  # 모든 워크플로우 백업
docker compose exec n8n n8n export:credentials --all --output=/home/node/.n8n/credentials/backup.json  # 모든 credentials 백업
docker compose exec n8n n8n import:workflow --input=/home/node/.n8n/workflows/backup.json       # 워크플로우 복원 (가져온 워크플로우는 기본 비활성)
docker compose exec n8n n8n import:credentials --input=/home/node/.n8n/credentials/backup.json   # credentials 복원
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. n8n 환경 변수 (PostgreSQL / HTTP / HTTPS)
```yaml
services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: Secureuser123
      POSTGRES_PASSWORD: SecurePassword123
      POSTGRES_DB: n8n
    volumes:
      - db_storage:/var/lib/postgresql   # 18부터 마운트 위치 (17 이하는 /var/lib/postgresql/data)
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -U Secureuser123 -d n8n"]
      interval: 5s
      timeout: 5s
      retries: 10

  n8n:
    image: docker.n8n.io/n8nio/n8n:${N8N_VERSION}   # .env에서 판 고정 (예: N8N_VERSION=2.46.7)
    environment:
      DB_TYPE: postgresdb                # 2.x 허용 값: postgresdb / sqlite (기본값 sqlite)
      DB_POSTGRESDB_HOST: postgres       # compose 서비스 이름
      DB_POSTGRESDB_PORT: 5432
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: Secureuser123
      DB_POSTGRESDB_PASSWORD: SecurePassword123
      DB_POSTGRESDB_SCHEMA: public       # 기본값 public
      N8N_HOST: example.com
      N8N_PORT: 5678
      N8N_PROTOCOL: http                 # http / https
      N8N_SECURE_COOKIE: "false"         # 기본값 true. HTTP 환경에서는 false, HTTPS 환경에서는 true
    ports:
      - "5678:5678"
    volumes:
      - n8n_storage:/home/node/.n8n      # PostgreSQL을 써도 암호화 키(config) 보존을 위해 유지
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  db_storage:
  n8n_storage:
```

로그인은 처음 접속할 때 만드는 소유자 계정(User Management)으로 합니다. `N8N_BASIC_AUTH_*` 변수는 n8n 1.0에서 제거되었습니다.

### n8n 1.x MySQL·MariaDB에서 옮기기

1.x에서 MySQL·MariaDB를 쓰던 경우 2.0으로 올리기 전에 데이터 이전 도구(`export:entities`·`import:entities`)로 PostgreSQL이나 SQLite로 옮깁니다. 내보낸 파일은 인스턴스 암호화 키로 암호화되고, 가져오기는 대상 데이터베이스의 migration 상태가 내보낸 쪽과 같은지 검사합니다. 따라서 같은 1.x 판과 같은 `/home/node/.n8n` 볼륨(또는 같은 `N8N_ENCRYPTION_KEY`)을 유지한 채 DB 설정만 PostgreSQL로 바꿔 가져오고, 결과를 확인한 뒤 2.x로 올립니다. 공식 문서는 이 도구의 지원 데이터베이스를 SQLite·PostgreSQL로 적고 있으며 암호화·migration 상태 검사와 MySQL·MariaDB 내보내기 지원은 1.123.92 소스에서 확인한 내용이므로, 운영 데이터에 쓰기 전에 복사본에서 먼저 시험합니다.

```bash
# 1) 1.x + MySQL 상태에서 내보내기 (실행 이력은 기본 제외, 포함하려면 --includeExecutionHistoryDataTables=true)
docker compose exec n8n n8n export:entities --outputDir=/home/node/.n8n/entities

# 2) 같은 1.x 판에서 DB 설정만 PostgreSQL로 바꿔 시작한 뒤 가져오기 (--truncateTables: 대상 테이블을 비우고 가져옴)
docker compose exec n8n n8n import:entities --inputDir=/home/node/.n8n/entities --truncateTables true
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. PostgreSQL 연결 확인
```bash
# n8n 이미지에는 PostgreSQL 클라이언트가 없으므로 postgres 컨테이너에서 확인
docker compose exec postgres pg_isready -h localhost -U Secureuser123 -d n8n   # 서버 응답 확인

# 서비스 이름과 비밀번호 인증으로 접속 (n8n과 같은 연결 정보 확인)
docker compose exec -e PGPASSWORD=SecurePassword123 postgres \
  psql -h postgres -U Secureuser123 -d n8n -c 'SELECT 1;'

# n8n이 처음 시작할 때 만든 테이블 목록
docker compose exec postgres psql -U Secureuser123 -d n8n -c '\dt'
```

같은 컨테이너 안에서 `-h` 없이(로컬 소켓) 접속하면 공식 postgres 이미지의 `trust` 설정 때문에 비밀번호를 묻지 않습니다. 비밀번호까지 확인하려면 위처럼 서비스 이름(`-h postgres`)으로 접속합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 전체 초기화 (컨테이너 + 볼륨 + 네트워크)
```bash
# 컨테이너·네트워크 + compose 파일에 선언한 이름 있는 볼륨·익명 볼륨 삭제, 정의에서 빠진 서비스 컨테이너도 삭제
docker compose down -v --remove-orphans
docker compose up -d
```
>  주의: 실행 중인 모든 데이터 삭제. 백업 필수

---

## 참고 자료

- n8n Documentation: [docs.n8n.io](https://docs.n8n.io/) — ★★★☆☆
- n8n Docker Installation: [docs.n8n.io/hosting/installation/docker](https://docs.n8n.io/hosting/installation/docker/) — ★★★☆☆
- n8n 2.0 Breaking Changes: [docs.n8n.io/2-0-breaking-changes](https://docs.n8n.io/2-0-breaking-changes/) — ★★★☆☆
- n8n 1.0 Migration Checklist: [docs.n8n.io/1-0-migration-checklist](https://docs.n8n.io/1-0-migration-checklist/) — ★★★☆☆
- n8n 데이터베이스 환경 변수(`DB_TYPE`·`DB_POSTGRESDB_*`): [Database environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/database) — ★★★☆☆
- n8n 배포 환경 변수(`N8N_HOST`·`N8N_PORT`·`N8N_PROTOCOL`·`N8N_ENCRYPTION_KEY`): [Deployment environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/deployment) — ★★★☆☆
- n8n 보안 환경 변수(`N8N_SECURE_COOKIE`): [Security environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/security) — ★★★☆☆
- n8n Server CLI(export·import, `export:entities`·`import:entities`): [Use the command line](https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line) — ★★★☆☆
- n8n 1.116.0 데이터 이전 도구 공지: [n8n 1.x release notes](https://docs.n8n.io/changelog/release-notes-1.x) — ★★★☆☆
- n8n 1.123.92 entities 명령 지원 데이터베이스 목록: [validate-database-type.ts](https://github.com/n8n-io/n8n/blob/n8n%401.123.92/packages/cli/src/utils/validate-database-type.ts) — ★★★☆☆
- n8n 공식 PostgreSQL compose 예시: [n8n-hosting withPostgres](https://github.com/n8n-io/n8n-hosting/tree/main/docker-compose/withPostgres) — ★★★☆☆
- n8n 릴리스(stable·beta 태그): [GitHub n8n-io/n8n releases](https://github.com/n8n-io/n8n/releases) — ★★★☆☆
- postgres 공식 이미지(18의 볼륨 위치, 로컬 `trust` 인증): [Docker Hub postgres](https://hub.docker.com/_/postgres) — ★★★☆☆
- pg_isready: [PostgreSQL Documentation](https://www.postgresql.org/docs/current/app-pg-isready.html) — ★★★☆☆
- docker compose down(`-v`·`--remove-orphans`): [Docker Docs](https://docs.docker.com/reference/cli/docker/compose/down/) — ★★★☆☆
- docker compose volumes: [Docker Docs](https://docs.docker.com/reference/cli/docker/compose/volumes/) — ★★★☆☆
- Compose 볼륨 기본 이름(`{project_name}_` 접두사): [Compose file volumes](https://docs.docker.com/reference/compose-file/volumes/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-25

**마지막 업데이트**: 2026-11-10

© 2026 siasia86. Licensed under CC BY 4.0.
