# PgBouncer 연결 풀링
<!-- reference: _reference/postgresql_official_notes.md -->

PostgreSQL 앞단에 두는 경량 연결 풀러(connection pooler) PgBouncer의 동작 방식, 풀 모드 선택, 설정, 운영 명령을 다룹니다. 기준 판은 PgBouncer 1.26.1(2026-10-14 릴리스, 2026-11-16 확인)과 PostgreSQL 18 문서입니다.

## 목차

| 섹션                                                                                    |
|-----------------------------------------------------------------------------------------|
| [1. 왜 연결 풀러가 필요한가](#1-왜-연결-풀러가-필요한가) / [2. 풀 모드](#2-풀-모드)     |
| [3. 설치와 기본 설정](#3-설치와-기본-설정) / [4. 인증 설정](#4-인증-설정)               |
| [5. 풀 크기 산정](#5-풀-크기-산정) / [6. 관리 콘솔과 모니터링](#6-관리-콘솔과-모니터링) |
| [7. 무중단 작업](#7-무중단-작업) / [8. 문제 해결과 점검표](#8-문제-해결과-점검표)       |

---

## 1. 왜 연결 풀러가 필요한가

PostgreSQL은 클라이언트 연결마다 백엔드 프로세스를 하나씩 만듭니다. 연결 수가 많아지면 프로세스 생성 비용, 연결별 메모리(`work_mem` 등), 잠금·스냅샷 관리 부담이 함께 커집니다. `max_connections` 기본값은 보통 100이며 바꾸려면 서버 재시작이 필요합니다.

```text
 app servers (many short connections)
   |  |  |  |  |  |  |  |      max_client_conn (e.g. 1000)
   v  v  v  v  v  v  v  v
 +---------------------------+
 |  PgBouncer :6432          |
 |  pool per (db, user)      |
 +---------------------------+
          |  |  |  |           default_pool_size (e.g. 20)
          v  v  v  v
 +---------------------------+
 |  PostgreSQL :5432         |
 +---------------------------+
```

| 상황                                                             | 풀러 효과                               |
|------------------------------------------------------------------|-----------------------------------------|
| 웹·서버리스 등 짧은 연결이 매우 많음                             | 연결 생성 비용 제거                     |
| 애플리케이션 인스턴스 수 × 내장 풀 크기가 `max_connections` 초과 | 실제 DB 연결 수를 상한으로 고정         |
| 유휴 연결이 대부분                                               | 소수 서버 연결을 여러 클라이언트가 공유 |
| DB 재시작·전환 시 클라이언트 재접속 폭주                         | `PAUSE`/`RESUME`으로 흡수               |

애플리케이션 내장 풀(HikariCP 등)과 PgBouncer는 함께 쓸 수 있습니다. 내장 풀은 앱 인스턴스 안에서, PgBouncer는 여러 인스턴스를 합쳐 DB 연결 수를 제한합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 풀 모드

`pool_mode`는 서버 연결을 클라이언트에게 언제 돌려받는지를 정합니다. 기본값은 `session`입니다.

| 모드          | 서버 연결 반환 시점                      | 공유 효율 | 세션 기능 호환 |
|---------------|------------------------------------------|-----------|----------------|
| `session`     | 클라이언트 연결 종료 시                  | 낮음      | 모두 가능      |
| `transaction` | 트랜잭션 종료 시                         | 높음      | 일부 제한      |
| `statement`   | 쿼리 하나 종료 시 (다중문 트랜잭션 금지) | 가장 높음 | 크게 제한      |

### transaction 모드에서 쓸 수 없는 기능

트랜잭션마다 다른 서버 연결에 붙을 수 있으므로, 세션 상태에 기대는 기능은 동작이 깨집니다. 공식 문서의 호환표 기준입니다.

| 기능                                         | transaction 모드                            |
|----------------------------------------------|---------------------------------------------|
| `SET` / `RESET` (세션 변수)                  | 지원 안 함                                  |
| `LISTEN`                                     | 지원 안 함                                  |
| `WITH HOLD` 커서                             | 지원 안 함                                  |
| SQL 수준 `PREPARE` / `DEALLOCATE`            | 지원 안 함                                  |
| 프로토콜 수준 prepared statement             | `max_prepared_statements`가 0이 아니면 지원 |
| `ON COMMIT PRESERVE/DELETE ROWS` 임시 테이블 | 지원 안 함                                  |
| `LOAD` 문                                    | 지원 안 함                                  |
| 세션 수준 advisory lock                      | 지원 안 함                                  |

- 세션 변수는 `SET LOCAL`(트랜잭션 범위)로 바꾸거나, 롤·DB 수준 기본값(`ALTER ROLE ... SET`)으로 옮깁니다.
- PgBouncer 1.26.0부터 `search_path`와 `default_transaction_read_only`를 기본으로 추적합니다(릴리스 소식 기준). 그 밖의 시작 파라미터 처리는 `track_extra_parameters`, `ignore_startup_parameters` 문서를 확인합니다.
- `LISTEN/NOTIFY`가 필요한 컴포넌트는 별도 `session` 모드 DB 항목이나 PostgreSQL 직접 연결로 분리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설치와 기본 설정

```bash
# Debian/Ubuntu
sudo apt install pgbouncer
# RHEL 계열 (PGDG 저장소 등록 후)
sudo dnf install pgbouncer

pgbouncer --version
```

배포판 패키지 판은 최신 릴리스보다 낮을 수 있습니다. 1.26.1은 SCRAM 인증 우회를 포함한 보안 결함 수정이 들어 있으므로, 설치된 판이 그보다 낮으면 해당 배포판의 보안 업데이트 여부를 확인합니다.

### pgbouncer.ini

```ini
[databases]
; 클라이언트가 appdb로 접속하면 PostgreSQL의 appdb로 연결
appdb = host=127.0.0.1 port=5432 dbname=appdb
; 보고서 전용: session 모드, 작은 풀
appdb_report = host=127.0.0.1 port=5432 dbname=appdb pool_mode=session pool_size=5

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
unix_socket_dir = /var/run/postgresql

auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 5
max_db_connections = 50

server_idle_timeout = 600
query_wait_timeout = 120
max_prepared_statements = 200

admin_users = pgb_admin
stats_users = pgb_monitor

logfile = /var/log/postgresql/pgbouncer.log
pidfile = /var/run/postgresql/pgbouncer.pid
```

`listen_addr`를 지정하지 않으면 Unix 소켓으로만 받습니다. 외부에서 받을 때는 방화벽으로 애플리케이션 대역만 허용합니다.

### 주요 설정 기본값

| 설정                      | 기본값      | 의미                                             |
|---------------------------|-------------|--------------------------------------------------|
| `listen_port`             | 6432        | 수신 포트                                        |
| `pool_mode`               | session     | 풀 모드                                          |
| `max_client_conn`         | 100         | 받을 수 있는 클라이언트 연결 수                  |
| `default_pool_size`       | 20          | (DB, 사용자) 쌍마다 서버 연결 수                 |
| `min_pool_size`           | 0           | 풀에 미리 유지할 최소 서버 연결                  |
| `reserve_pool_size`       | 0           | 대기가 길어질 때 추가로 쓰는 연결 수             |
| `reserve_pool_timeout`    | 5.0초       | 이 시간 넘게 기다리면 예비 연결 사용             |
| `max_db_connections`      | 0 (무제한)  | DB별 서버 연결 상한                              |
| `server_reset_query`      | DISCARD ALL | 연결 반환 시 실행 (transaction 모드에서는 안 씀) |
| `server_idle_timeout`     | 600.0초     | 유휴 서버 연결 종료                              |
| `server_lifetime`         | 3600.0초    | 사용하지 않는 서버 연결의 최대 수명              |
| `query_wait_timeout`      | 120.0초     | 서버 연결을 기다릴 수 있는 최대 시간             |
| `client_idle_timeout`     | 0 (끔)      | 유휴 클라이언트 연결 종료                        |
| `max_prepared_statements` | 200         | 프로토콜 수준 prepared statement 캐시 크기       |
| `auth_type`               | md5         | 인증 방식                                        |

```bash
sudo systemctl enable --now pgbouncer
psql -h 127.0.0.1 -p 6432 -U app appdb -c 'SELECT 1'
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 인증 설정

PgBouncer는 클라이언트를 직접 인증한 뒤, 같은 사용자로 PostgreSQL에 접속합니다.

### 방법 1: auth_file

```text
# /etc/pgbouncer/userlist.txt  (chmod 600, owner postgres)
"app" "SCRAM-SHA-256$4096:<SALT>$<STORED_KEY>:<SERVER_KEY>"
```

SCRAM 비밀값은 PostgreSQL의 `pg_authid.rolpassword` 값을 그대로 씁니다(superuser로 조회). 평문 비밀번호를 파일에 두지 않습니다.

```sql
SELECT rolname, rolpassword FROM pg_authid WHERE rolname = 'app';
```

### 방법 2: auth_query

사용자가 많으면 `auth_user`로 접속해 `auth_query`로 비밀값을 조회합니다. 기본 `auth_query`는 `pg_authid`를 읽으므로 superuser가 필요해집니다. 권한을 줄이려면 `SECURITY DEFINER` 함수를 만들어 `auth_user`에게 실행 권한만 줍니다.

```sql
CREATE ROLE pgbouncer_auth LOGIN PASSWORD '<PASSWORD>';

CREATE SCHEMA pgbouncer AUTHORIZATION postgres;
CREATE FUNCTION pgbouncer.get_auth(p_usename text)
RETURNS TABLE(usename name, passwd text)
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog AS $$
  SELECT rolname, CASE WHEN rolvaliduntil < now() THEN NULL ELSE rolpassword END
  FROM pg_authid WHERE rolname = p_usename AND rolcanlogin;
$$;
REVOKE ALL ON FUNCTION pgbouncer.get_auth(text) FROM PUBLIC;
GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;
GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(text) TO pgbouncer_auth;
```

```ini
[pgbouncer]
auth_user = pgbouncer_auth
auth_query = SELECT usename, passwd FROM pgbouncer.get_auth($1)
```

`auth_user` 자신의 비밀값은 `auth_file`에 둡니다. 함수는 PgBouncer가 접속하는 각 DB에 있어야 합니다(또는 `auth_dbname` 설정 확인).

🟡 주의: `auth_type = trust`나 `any`는 비밀번호 확인을 하지 않습니다. 시험 환경 외에는 쓰지 않습니다. `plain`은 deprecated입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 풀 크기 산정

서버 연결 수 상한은 대략 다음과 같습니다.

```text
server connections <= sum over (db, user) pools of (pool_size + reserve_pool_size)
                      and per db <= max_db_connections
```

PgBouncer 여러 대를 두면 대수만큼 곱해집니다. 이 합계가 PostgreSQL `max_connections - superuser_reserved_connections`(기본 3)보다 작아야 하고, 관리·복제·백업용 연결 여유도 남겨야 합니다.

| 판단 요소                    | 방향                                                      |
|------------------------------|-----------------------------------------------------------|
| DB 서버 CPU 코어 수          | 동시에 실제로 일하는 연결은 코어 수의 몇 배 이내가 효율적 |
| 쿼리가 주로 I/O 대기         | 코어 수보다 조금 크게                                     |
| `cl_waiting`이 자주 0보다 큼 | 풀 크기 상향 또는 느린 쿼리 개선                          |
| DB CPU가 이미 포화           | 풀 크기를 키워도 효과 없음. 쿼리 개선이 우선              |

정확한 최적값은 부하 시험으로 정합니다. 처음에는 작게 두고 `SHOW POOLS`의 대기 지표를 보며 늘리는 편이 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 관리 콘솔과 모니터링

가상 DB `pgbouncer`로 접속하면 관리 콘솔입니다. `admin_users`(전체), `stats_users`(조회만)에 있는 사용자만 접속할 수 있습니다.

```bash
psql -h 127.0.0.1 -p 6432 -U pgb_admin pgbouncer
```

```sql
SHOW POOLS;      -- 풀별 클라이언트·서버 연결 상태
SHOW STATS;      -- DB별 트랜잭션·쿼리 수, 평균 시간
SHOW CLIENTS;    -- 클라이언트 연결 목록
SHOW SERVERS;    -- 서버 연결 목록
SHOW DATABASES;  -- [databases] 항목과 풀 설정
SHOW CONFIG;     -- 현재 설정값, 기본값, 실행 중 변경 가능 여부
```

### SHOW POOLS 주요 열

| 열           | 의미                                                | 볼 점                  |
|--------------|-----------------------------------------------------|------------------------|
| `cl_active`  | 서버 연결에 붙은 클라이언트 (또는 대기 없는 유휴)   |                        |
| `cl_waiting` | 쿼리를 보냈지만 서버 연결을 아직 못 받은 클라이언트 | 꾸준히 0보다 크면 부족 |
| `sv_active`  | 클라이언트에 붙어 사용 중인 서버 연결               | 풀 크기에 계속 닿는지  |
| `sv_idle`    | 바로 쓸 수 있는 유휴 서버 연결                      |                        |
| `sv_used`    | 재사용 전 확인 쿼리가 필요한 유휴 서버 연결         |                        |
| `maxwait`    | 가장 오래 기다린 클라이언트의 대기 초               | 계속 오르면 과부하     |

`maxwait`가 계속 오르면 DB 서버가 과부하이거나 풀 크기가 작은 상태입니다. 공식 문서도 이 값을 핵심 지표로 설명합니다. Prometheus를 쓰는 환경에서는 관리 콘솔을 읽는 exporter로 이 값을 수집합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 무중단 작업

### 설정 변경

```sql
RELOAD;            -- 설정·auth_file 다시 읽기 (SIGHUP과 같음)
SHOW CONFIG;       -- changeable 열로 실행 중 변경 가능 여부 확인
```

### DB 재시작·전환 시

```sql
PAUSE appdb;       -- 진행 중 쿼리가 끝나면 서버 연결을 끊고 새 쿼리는 대기
-- PostgreSQL 재시작 또는 주소 변경 후
RESUME appdb;      -- 대기 중이던 클라이언트 진행
```

`PAUSE` 동안 클라이언트는 연결이 끊기지 않고 기다립니다. 대기가 `query_wait_timeout`보다 길어지면 오류가 나므로 작업 시간을 그 안에 맞춥니다.

### 점진 전환

```sql
-- [databases]의 host를 새 서버로 바꾸고 RELOAD 후
RECONNECT appdb;   -- 반환되는 서버 연결부터 차례로 새 주소로 재연결
WAIT_CLOSE appdb;  -- 옛 연결이 모두 닫힐 때까지 대기
```

### 종료와 신호

| 명령·신호                             | 동작                                                                           |
|---------------------------------------|--------------------------------------------------------------------------------|
| `SHUTDOWN`                            | 즉시 종료                                                                      |
| `SHUTDOWN WAIT_FOR_SERVERS` / SIGINT  | 새 연결 거부, 서버 연결 반환 후 종료                                           |
| `SHUTDOWN WAIT_FOR_CLIENTS` / SIGTERM | 새 연결 거부, 클라이언트가 모두 끊긴 뒤 종료 (1.23.0 이전 SIGTERM은 즉시 종료) |
| `KILL db`                             | 해당 DB의 클라이언트·서버 연결 즉시 끊기                                       |
| `DISABLE db` / `ENABLE db`            | 새 클라이언트 연결 거부 / 허용                                                 |

🟡 주의: `KILL`과 `SHUTDOWN`(인자 없음)은 진행 중 트랜잭션을 끊습니다. 정기 작업에는 `PAUSE`/`RESUME`이나 `WAIT_FOR_*` 옵션을 씁니다.

1.26.0부터 온라인 재시작 옵션(`-R`)이 제거되었습니다. 무중단 교체가 필요하면 여러 프로세스를 같은 포트로 띄우는 `so_reuseport` 방식이나 앞단 부하 분산을 공식 문서에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 문제 해결과 점검표

### 증상별 확인

| 증상                                            | 원인 후보                             | 확인·조치                                            |
|-------------------------------------------------|---------------------------------------|------------------------------------------------------|
| `no more connections allowed (max_client_conn)` | 클라이언트 연결 상한 도달             | `max_client_conn` 상향, OS 파일 디스크립터 한도 확인 |
| `query_wait_timeout` 오류                       | 서버 연결을 오래 못 받음              | `SHOW POOLS`의 `cl_waiting`, 느린 쿼리 확인          |
| `prepared statement "S_1" does not exist`       | transaction 모드 + prepared statement | `max_prepared_statements` 0 아님 확인                |
| 세션 변수가 가끔 사라짐                         | transaction 모드에서 `SET` 사용       | `SET LOCAL` 또는 롤 기본값                           |
| PostgreSQL `too many clients`                   | 풀 합계가 `max_connections` 초과      | 5절 계산 재확인                                      |
| 인증 실패 (`SASL authentication failed`)        | auth_file 비밀값 불일치               | `pg_authid` 값과 비교, `RELOAD`                      |

### 점검표

| 점검 항목                                                       | 확인 |
|-----------------------------------------------------------------|------|
| 설치된 PgBouncer 판이 보안 수정이 반영된 판이다                 | [ ]  |
| `auth_type`이 `scram-sha-256` 또는 `hba`이고 trust/any가 아니다 | [ ]  |
| `userlist.txt` 권한이 600이다                                   | [ ]  |
| 풀 합계 × PgBouncer 대수 < PostgreSQL 가용 연결 수              | [ ]  |
| 애플리케이션이 transaction 모드 제한 기능을 쓰지 않는다         | [ ]  |
| `SHOW POOLS`의 `cl_waiting`, `maxwait`를 감시한다               | [ ]  |
| 관리 콘솔 사용자(`admin_users`)를 최소로 둔다                   | [ ]  |
| PgBouncer 자체가 단일 장애점이 되지 않게 이중화했다             | [ ]  |
| DB 작업 절차에 `PAUSE`/`RESUME`이 들어 있다                     | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [postgresql_install.md](./postgresql_install.md) — PostgreSQL 설치와 pg_hba.conf
- [rdbms_server_config.md](./rdbms_server_config.md) — postgresql.conf 설정
- [rdbms_replication.md](./rdbms_replication.md) — 복제와 Failover
- PgBouncer 홈 (릴리스 소식): [pgbouncer.org](https://www.pgbouncer.org/) — ★★★☆☆ (확인일 2026-11-16)
- PgBouncer Configuration: [pgbouncer.org/config.html](https://www.pgbouncer.org/config.html) — ★★★☆☆ (확인일 2026-11-16)
- PgBouncer Usage: [pgbouncer.org/usage.html](https://www.pgbouncer.org/usage.html) — ★★★☆☆ (확인일 2026-11-16)
- PgBouncer Features (풀 모드 호환표): [pgbouncer.org/features.html](https://www.pgbouncer.org/features.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL Connection Settings: [postgresql.org/docs/current/runtime-config-connection.html](https://www.postgresql.org/docs/current/runtime-config-connection.html) — ★★★☆☆ (확인일 2026-11-16)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
