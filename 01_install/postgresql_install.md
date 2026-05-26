# PostgreSQL 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 보안 설정](#4-초기-보안-설정) / [5. 기본 설정 (postgresql.conf)](#5-기본-설정-postgresqlconf) / [6. 접속 제어 (pg_hba.conf)](#6-접속-제어-pg_hbaconf) |
| [7. 복제 설정](#7-복제-설정) / [8. 방화벽 설정](#8-방화벽-설정) / [9. 설치 검증](#9-설치-검증) / [10. 트러블슈팅](#10-트러블슈팅) |
| [11. 기본 사용법](#11-기본-사용법) |

---

## 1. 개요

### 시스템 요구사항

| 항목   | 최소          | 권장 (프로덕션)                          |
|--------|---------------|------------------------------------------|
| CPU    | 1 core        | 4 core 이상                              |
| RAM    | 1 GB          | 8 GB 이상                                |
| 디스크 | 5 GB          | SSD 100 GB 이상                          |
| OS     | Ubuntu 20.04+ | Ubuntu 22.04 / Rocky 9 / Alma 9 / RHEL 9 |
| 포트   | 5432/tcp      | 5432/tcp                                 |

### 버전 선택 기준

| 버전          | EOL     | 권장 여부            |
|---------------|---------|----------------------|
| PostgreSQL 14 | 2026-11 | 🟡 EOL 임박, 비권장  |
| PostgreSQL 16 | 2028-11 | ✅ 안정적, 현재 권장 |
| PostgreSQL 17 | 2029-11 | ✅ 신규 구축 권장    |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### Ubuntu 버전별 차이

| 항목                   | Ubuntu 22.04 (Jammy)            | Ubuntu 24.04 (Noble)                    |
|------------------------|---------------------------------|-----------------------------------------|
| 기본 저장소 PostgreSQL | 14.x                            | 16.x                                    |
| PGDG 최신 버전         | 17                              | 17 (18 출시 시 자동 반영)               |
| DB 생성 로케일         | `LC_COLLATE 'en_US.UTF-8'` 가능 | `LOCALE 'C.UTF-8'` 사용 권장 (ICU 기반) |
| 설정 파일 경로         | `/etc/postgresql/14/main/`      | `/etc/postgresql/17/main/`              |
| 로그 경로              | `/var/log/postgresql/`          | `/var/log/postgresql/`                  |

🟡 Ubuntu 24.04는 PostgreSQL 17 기준으로 ICU 로케일을 사용합니다.
`LC_COLLATE 'en_US.UTF-8'` 방식으로 DB 생성 시 오류가 발생하므로 `LOCALE 'C.UTF-8'`을 사용합니다.

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치 방법 A: APT (Ubuntu 기본 저장소)

Ubuntu 22.04 / 24.04 모두 동일하게 적용됩니다.

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable --now postgresql
```

🟡 Ubuntu 기본 저장소 버전은 최신이 아닐 수 있습니다. 특정 버전이 필요하면 방법 B를 사용합니다.

### 2-3. 설치 방법 B: PostgreSQL 공식 저장소 (PGDG)

Ubuntu 22.04 / 24.04 모두 동일하게 적용됩니다.

```bash
# 저장소 키 및 소스 추가
sudo apt install curl ca-certificates -y
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc

sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] \
    https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list'

sudo apt update
sudo apt install postgresql-17 -y
sudo systemctl enable --now postgresql
```

### 2-4. Ubuntu 24.04 특이사항: DB 생성 로케일

```sql
-- Ubuntu 22.04: 아래 방식 모두 가능
CREATE DATABASE mydb
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

-- Ubuntu 24.04 (PostgreSQL 17 + ICU): LOCALE 사용 필수
CREATE DATABASE mydb
    ENCODING 'UTF8'
    LOCALE 'C.UTF-8'
    TEMPLATE template0;
```

### 2-5. 설치 확인

```bash
psql --version
sudo systemctl status postgresql
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

Rocky Linux, AlmaLinux, RHEL, CentOS Stream에서 동일하게 적용됩니다.

### 배포판별 EL 버전 대응

| 배포판                    | EL 버전 | PGDG RPM 경로 키워드 |
|---------------------------|---------|----------------------|
| RHEL 8 / Rocky 8 / Alma 8 | EL-8    | `EL-8`               |
| RHEL 9 / Rocky 9 / Alma 9 | EL-9    | `EL-9`               |
| CentOS Stream 9           | EL-9    | `EL-9`               |

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. PostgreSQL 공식 저장소 (PGDG)

```bash
# EL9 (Rocky 9 / Alma 9 / RHEL 9 / CentOS Stream 9)
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# EL8 (Rocky 8 / Alma 8 / RHEL 8)
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# AppStream 내장 PostgreSQL 모듈 비활성화 (충돌 방지)
sudo dnf -qy module disable postgresql

# PostgreSQL 17 설치
sudo dnf install -y postgresql17-server postgresql17-contrib

# DB 클러스터 초기화
sudo /usr/pgsql-17/bin/postgresql-17-setup initdb

sudo systemctl enable --now postgresql-17
```

### 3-3. SELinux 설정

RHEL 계열은 SELinux가 기본 활성화되어 있습니다.

```bash
# SELinux 상태 확인
getenforce

# 기본 포트(5432) 사용 시 추가 설정 불필요
# 비표준 포트(예: 5433) 사용 시
sudo semanage port -a -t postgresql_port_t -p tcp 5433

# 데이터 디렉토리 변경 시 컨텍스트 설정
sudo semanage fcontext -a -t postgresql_db_t "/data/pgsql(/.*)?"
sudo restorecon -Rv /data/pgsql
```

### 3-4. 설치 확인

```bash
psql --version
sudo systemctl status postgresql-17
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 보안 설정

### 4-1. postgres 계정으로 접속

PostgreSQL 설치 시 OS 계정 `postgres`와 DB 슈퍼유저 `postgres`가 자동 생성됩니다.

```bash
sudo -u postgres psql
```

### 4-2. postgres 슈퍼유저 패스워드 설정

```sql
ALTER USER postgres WITH ENCRYPTED PASSWORD 'SecurePassword123';
\q
```

### 4-3. 애플리케이션 전용 계정 및 DB 생성

```sql
-- DB 생성
-- PostgreSQL 17+: LOCALE 'C.UTF-8' 사용 (LC_COLLATE/LC_CTYPE은 ICU 환경에서 오류 발생)
CREATE DATABASE mydb
    ENCODING 'UTF8'
    LOCALE 'C.UTF-8'
    TEMPLATE template0;

-- 전용 계정 생성 (따옴표 없이 생성 시 소문자로 저장됨)
CREATE USER secureuser123 WITH ENCRYPTED PASSWORD 'SecurePassword123';

-- 권한 부여
GRANT CONNECT ON DATABASE mydb TO secureuser123;
\c mydb
GRANT USAGE ON SCHEMA public TO secureuser123;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO secureuser123;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO secureuser123;
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 설정 (postgresql.conf)

```bash
# Ubuntu (버전에 따라 경로 다름)
sudo vi /etc/postgresql/17/main/postgresql.conf

# RHEL 계열 (Rocky / Alma / RHEL)
sudo vi /var/lib/pgsql/17/data/postgresql.conf
```

```ini
# 연결
listen_addresses = '*'          # 원격 접속 허용 (기본: localhost)
port             = 5432
max_connections  = 200

# 메모리
shared_buffers          = 2GB   # RAM의 25% 권장
effective_cache_size    = 6GB   # RAM의 75% 권장
work_mem                = 64MB  # 정렬/해시 작업당 메모리
maintenance_work_mem    = 512MB # VACUUM, CREATE INDEX 등

# WAL / 내구성
wal_level               = replica       # 복제 사용 시 (기본: replica)
synchronous_commit      = on
checkpoint_completion_target = 0.9
wal_buffers             = 64MB

# 쿼리 최적화
random_page_cost        = 1.1   # SSD 사용 시 (HDD: 4.0)
effective_io_concurrency = 200  # SSD 사용 시

# 로그
logging_collector       = on
log_directory           = 'log'
log_filename            = 'postgresql-%Y-%m-%d.log'
log_min_duration_statement = 1000   # 1초 이상 쿼리 기록
log_line_prefix         = '%t [%p] %u@%d '

# 자동 VACUUM
autovacuum              = on
```

```bash
sudo systemctl restart postgresql      # Ubuntu
sudo systemctl restart postgresql-17   # RHEL 계열
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 접속 제어 (pg_hba.conf)

클라이언트 인증 방식을 제어하는 파일.

```bash
# Ubuntu
sudo vi /etc/postgresql/17/main/pg_hba.conf

# RHEL 계열 (Rocky / Alma / RHEL)
sudo vi /var/lib/pgsql/17/data/pg_hba.conf
```

```
# TYPE  DATABASE   USER           ADDRESS          METHOD
# 로컬 소켓 접속
local   all        postgres                        peer
local   all        all                             md5

# 로컬 TCP 접속
host    all        all            127.0.0.1/32     scram-sha-256

# 애플리케이션 서버 접속 허용
host    mydb       secureuser123  10.0.1.0/24      scram-sha-256

# 복제 전용 계정
host    replication repl          10.0.1.0/24      scram-sha-256

# 원격 접속 전면 차단 (명시적)
# host  all        all            0.0.0.0/0        reject
```

🟡 `trust` 방식은 패스워드 없이 접속을 허용하므로 프로덕션에서 사용 금지.

```bash
# 설정 반영 (재시작 없이)
sudo -u postgres psql -c "SELECT pg_reload_conf();"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 복제 설정

복제 상세 설정은 [rdbms_replication.md](../09_database/rdbms_replication.md) 참고.

### 복제 전용 계정 생성

```sql
CREATE USER repl WITH REPLICATION ENCRYPTED PASSWORD 'SecurePassword123';
```

### postgresql.conf (Primary)

```ini
wal_level           = replica
max_wal_senders     = 5
wal_keep_size       = 1GB
```

### Standby 초기화

```bash
pg_basebackup \
    -h 10.0.1.10 \
    -U repl \
    -D /var/lib/postgresql/17/main \
    -P -Xs -R
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 방화벽 설정

### Ubuntu (ufw)

```bash
sudo ufw allow from 10.0.1.0/24 to any port 5432
sudo ufw reload
sudo ufw status
```

### Rocky Linux (firewalld)

```bash
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.1.0/24" port port="5432" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 설치 검증

```bash
# 서비스 상태
sudo systemctl status postgresql      # Ubuntu
sudo systemctl status postgresql-17   # RHEL 계열

# 포트 리스닝 확인
ss -tlnp | grep 5432

# 접속 테스트
psql -h localhost -U secureuser123 -d mydb -c "SELECT version(), now();"

# 슬로우 쿼리 로그 확인
sudo tail -f /var/lib/postgresql/17/main/log/postgresql-$(date +%Y-%m-%d).log
```

```sql
-- 주요 설정 확인
SHOW shared_buffers;
SHOW max_connections;
SHOW wal_level;
SHOW listen_addresses;

-- 현재 접속 확인
SELECT client_addr, usename, datname, state
FROM pg_stat_activity
WHERE state IS NOT NULL;
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                              | 원인                                         | 해결 방법                                           |
|---------------------------------------------------|----------------------------------------------|-----------------------------------------------------|
| `FATAL: role "user" does not exist`               | DB 계정 미생성                               | `CREATE USER` 실행                                  |
| `FATAL: password authentication failed`           | 패스워드 불일치 또는 pg_hba 설정             | pg_hba.conf 인증 방식 확인, 패스워드 재설정         |
| `could not connect to server: Connection refused` | 서비스 미실행 또는 포트 차단                 | `systemctl status postgresql`, 방화벽 확인          |
| `FATAL: no pg_hba.conf entry for host`            | pg_hba.conf 허용 규칙 없음                   | 해당 IP/계정 규칙 추가 후 `pg_reload_conf()`        |
| `FATAL: database "mydb" does not exist`           | DB 미생성                                    | `CREATE DATABASE mydb;`                             |
| `out of shared memory`                            | `shared_buffers` 또는 `max_connections` 과다 | 값 조정 후 재시작                                   |
| Rocky: `initdb` 미실행                            | 클러스터 초기화 누락                         | `sudo /usr/pgsql-17/bin/postgresql-17-setup initdb` |

### 디버깅 명령

```bash
# 에러 로그 확인
sudo tail -100 /var/log/postgresql/postgresql-17-main.log   # Ubuntu
sudo tail -100 /var/lib/pgsql/17/data/log/postgresql-*.log  # RHEL 계열

# 현재 Lock 대기 확인
sudo -u postgres psql -c "
SELECT pid, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE wait_event IS NOT NULL;"

# DB 크기 확인
sudo -u postgres psql -c "
SELECT datname, pg_size_pretty(pg_database_size(datname))
FROM pg_database ORDER BY pg_database_size(datname) DESC;"
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 기본 사용법

### 접속

```bash
# OS postgres 계정으로 접속 (peer 인증)
sudo -u postgres psql

# 특정 DB 접속
sudo -u postgres psql -d mydb

# 패스워드 인증 (TCP)
psql -h localhost -U secureuser123 -d mydb

# 원격 접속
psql -h 10.0.1.10 -U secureuser123 -d mydb
```

### psql 주요 메타 명령

| 명령어     | 설명                     |
|------------|--------------------------|
| `\l`       | DB 목록                  |
| `\c mydb`  | DB 전환                  |
| `\dt`      | 테이블 목록              |
| `\d users` | 테이블 구조              |
| `\du`      | 사용자 목록              |
| `\timing`  | 쿼리 실행 시간 표시 토글 |
| `\q`       | 종료                     |

### DB / 테이블 기본 조작

```sql
-- DB 생성 / 삭제
CREATE DATABASE mydb ENCODING 'UTF8' LOCALE 'C.UTF-8' TEMPLATE template0;
DROP DATABASE mydb;

-- 테이블 생성
CREATE TABLE users (
    id         SERIAL       PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- CRUD
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
SELECT * FROM users WHERE id = 1;
UPDATE users SET email = 'new@example.com' WHERE id = 1;
DELETE FROM users WHERE id = 1;
```

### 사용자 관리

```sql
-- 계정 목록
\du

-- 권한 확인
\dp users

-- 패스워드 변경
ALTER USER secureuser123 WITH ENCRYPTED PASSWORD 'NewPassword123';

-- 계정 삭제
DROP USER secureuser123;
```

### 백업 / 복원

```bash
# 단일 DB 백업 (plain SQL)
pg_dump -U postgres mydb > mydb_$(date +%Y%m%d).sql

# 단일 DB 백업 (custom 형식, 압축)
pg_dump -U postgres -Fc mydb > mydb_$(date +%Y%m%d).dump

# 전체 백업
pg_dumpall -U postgres > all_$(date +%Y%m%d).sql

# 복원 (plain SQL)
psql -U postgres -d mydb < mydb_20260504.sql

# 복원 (custom 형식)
pg_restore -U postgres -d mydb mydb_20260504.dump
```

### 서비스 관리

```bash
sudo systemctl start|stop|restart|status postgresql

# 설정 반영 (재시작 없이)
sudo -u postgres psql -c "SELECT pg_reload_conf();"

# 현재 접속 세션 확인
sudo -u postgres psql -c "SELECT pid, usename, datname, state, query FROM pg_stat_activity WHERE state IS NOT NULL;"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- PostgreSQL Documentation: [Installation](https://www.postgresql.org/docs/current/installation.html) — ★★★☆☆
- PostgreSQL Documentation: [Client Authentication](https://www.postgresql.org/docs/current/client-authentication.html) — ★★★☆☆
- PostgreSQL Documentation: [Server Configuration](https://www.postgresql.org/docs/current/runtime-config.html) — ★★★☆☆
- [rdbms_replication.md](../09_database/rdbms_replication.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
