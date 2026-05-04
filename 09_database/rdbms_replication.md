# RDBMS 복제 (Replication)

## 목차

| 단계 | 섹션                                                                                                                                                                          |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 복제 개념](#1-복제-개념) / [2. MySQL 복제 구조](#2-mysql-복제-구조)                                                                                                        |
| 설정 | [3. MySQL 복제 설정](#3-mysql-복제-설정) / [4. GTID 복제](#4-gtid-복제) / [5. 반동기 복제](#5-반동기-복제)                                                                     |
| 운영 | [6. 복제 지연 모니터링](#6-복제-지연-모니터링) / [7. Failover](#7-failover) / [8. 복제 필터링](#8-복제-필터링)                                                                 |
| 고급 | [9. 복제 토폴로지](#9-복제-토폴로지) / [10. PostgreSQL 복제](#10-postgresql-복제) / [11. AWS RDS Read Replica](#11-aws-rds-read-replica) / [12. 실무 팁](#12-실무-팁) |

---

## 1. 복제 개념

Primary(Master)의 변경사항을 Replica(Slave)에 자동으로 전파하는 기능.

### 목적

| 목적           | 설명                                        |
|----------------|---------------------------------------------|
| **읽기 분산**  | Read Replica로 SELECT 부하 분산             |
| **고가용성**   | Primary 장애 시 Replica로 Failover          |
| **백업**       | Replica에서 백업 수행 (Primary 부하 없음)   |
| **지리적 분산**| 다른 리전에 Replica 배치                    |

### 복제 방식

| 방식             | 설명                                          | 일관성               |
|------------------|-----------------------------------------------|----------------------|
| **비동기 복제**  | Primary 커밋 후 Replica에 비동기 전송         | 복제 지연 가능       |
| **반동기 복제**  | 최소 1개 Replica 수신 확인 후 커밋            | 지연 최소화          |
| **동기 복제**    | 모든 Replica 적용 확인 후 커밋                | 완전 일관성, 성능 저하|

[⬆ 목차로 돌아가기](#목차)

---

## 2. MySQL 복제 구조

```
Primary                              Replica
┌──────────────┐                    ┌──────────────────┐
│  Binary Log  │ <-- I/O Thread --> │   Relay Log      │
│  (binlog)    │                    │                  │
└──────────────┘                    └────────┬─────────┘
                                             │ SQL Thread
                                             v
                                        Data Applied
```

### Binary Log 형식

| 형식          | 설명                          | 권장                          |
|---------------|-------------------------------|-------------------------------|
| `STATEMENT`   | SQL 문 그대로 기록            | 비권장 (비결정적 함수 문제)   |
| `ROW`         | 변경된 행 데이터 기록         | ✅ 권장                       |
| `MIXED`       | 상황에 따라 자동 선택         | 일반적                        |

```sql
-- binlog 형식 확인
SHOW VARIABLES LIKE 'binlog_format';

-- Primary 상태 확인
SHOW MASTER STATUS\G

-- Replica 상태 확인
SHOW REPLICA STATUS\G   -- MySQL 8.0+
SHOW SLAVE STATUS\G     -- 구버전
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. MySQL 복제 설정

### Primary 설정

```ini
# my.cnf
[mysqld]
server_id       = 1
binlog_format   = ROW
log_bin         = /var/log/mysql/mysql-bin.log
binlog_expire_logs_seconds = 604800   # 7일
max_binlog_size = 100M
```

```sql
-- 복제 전용 계정 생성
CREATE USER 'repl'@'10.0.1.%' IDENTIFIED BY 'SecurePassword123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'10.0.1.%';
FLUSH PRIVILEGES;

-- 현재 binlog 위치 확인 (초기 데이터 덤프 전)
FLUSH TABLES WITH READ LOCK;
SHOW MASTER STATUS\G
-- File: mysql-bin.000003, Position: 154
```

### 초기 데이터 동기화

```bash
# Primary에서 덤프
mysqldump \
    --single-transaction \
    --master-data=2 \
    --all-databases \
    -u root -p > dump.sql

# Replica로 전송 및 복원
scp dump.sql replica:/tmp/
mysql -u root -p < /tmp/dump.sql
```

### Replica 설정 (binlog position 기반)

```ini
# my.cnf
[mysqld]
server_id        = 2
relay_log        = /var/log/mysql/relay-bin
log_replica_updates = ON
read_only        = ON
```

```sql
-- Replica에서 실행
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST     = '10.0.1.10',
    SOURCE_PORT     = 3306,
    SOURCE_USER     = 'repl',
    SOURCE_PASSWORD = 'SecurePassword123',
    SOURCE_LOG_FILE = 'mysql-bin.000003',
    SOURCE_LOG_POS  = 154;

START REPLICA;
SHOW REPLICA STATUS\G
-- Replica_IO_Running: Yes
-- Replica_SQL_Running: Yes
-- Seconds_Behind_Source: 0
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. GTID 복제

GTID(Global Transaction Identifier)는 각 트랜잭션에 고유 ID를 부여하여 복제 위치를 명확히 추적한다.

```
GTID 형식: source_id:transaction_id
예시: 3E11FA47-71CA-11E1-9E33-C80AA9429562:1-100
```

### GTID 활성화

```ini
# my.cnf (Primary, Replica 모두)
gtid_mode               = ON
enforce_gtid_consistency = ON
binlog_format           = ROW
log_replica_updates     = ON
```

### GTID 기반 복제 설정

```sql
-- Replica에서 실행
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST         = '10.0.1.10',
    SOURCE_USER         = 'repl',
    SOURCE_PASSWORD     = 'SecurePassword123',
    SOURCE_AUTO_POSITION = 1;   -- GTID 자동 위치

START REPLICA;
```

### GTID vs 전통 복제 비교

| 항목           | 전통 복제                  | GTID 복제       |
|----------------|----------------------------|-----------------|
| 위치 추적      | binlog 파일명 + 오프셋     | 트랜잭션 ID     |
| Failover       | 수동 위치 계산 필요        | 자동            |
| 복제 재설정    | 복잡                       | 단순            |
| 권장 여부      | 레거시                     | ✅ 권장         |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 반동기 복제

Primary가 커밋 후 최소 1개 Replica의 수신 확인(ACK)을 받은 뒤 클라이언트에 응답한다.
Replica 장애 시 `rpl_semi_sync_source_timeout` 초과 후 비동기로 자동 전환된다.

```
Primary                              Replica
   │                                    │
   ├── COMMIT ──────────────────────>   │
   │                                    │  Relay Log 기록
   │   <──────────────── ACK ───────────┤
   │                                    │
   └── 클라이언트 응답
```

### 설정

```sql
-- Primary
INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';
SET GLOBAL rpl_semi_sync_source_enabled = ON;
SET GLOBAL rpl_semi_sync_source_timeout = 1000;  -- 1초 후 비동기 전환

-- Replica
INSTALL PLUGIN rpl_semi_sync_replica SONAME 'semisync_replica.so';
SET GLOBAL rpl_semi_sync_replica_enabled = ON;
```

```sql
-- 반동기 상태 확인
SHOW STATUS LIKE 'Rpl_semi_sync%';
-- Rpl_semi_sync_source_status: ON
-- Rpl_semi_sync_source_clients: 1
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 복제 지연 모니터링

### MySQL

```sql
-- Replica 지연 확인
SHOW REPLICA STATUS\G
-- Seconds_Behind_Source: 복제 지연 초

-- Performance Schema (병렬 복제 워커별 상태)
SELECT * FROM performance_schema.replication_applier_status_by_worker\G
```

### 복제 지연 원인과 해결

| 원인                  | 해결                          |
|-----------------------|-------------------------------|
| 단일 스레드 적용      | 병렬 복제 활성화              |
| 대용량 트랜잭션       | 트랜잭션 분할                 |
| 네트워크 지연         | 네트워크 대역폭 확인          |
| Replica 서버 부하     | 읽기 쿼리 분산                |

```sql
-- 병렬 복제 활성화 (MySQL 5.7+)
SET GLOBAL replica_parallel_workers = 4;
SET GLOBAL replica_parallel_type    = 'LOGICAL_CLOCK';
```

### 복제 지연 알림 (Prometheus)

```yaml
# mysqld_exporter 알림 규칙
- alert: ReplicationLag
  expr: mysql_slave_status_seconds_behind_master > 30
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "Replication lag {{ $value }}s on {{ $labels.instance }}"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Failover

### 수동 Failover (전통 복제)

```sql
-- 1. Primary 중단 확인 후 Replica에서 실행
STOP REPLICA IO_THREAD;
-- SQL Thread가 Relay Log를 모두 소진할 때까지 대기
SHOW REPLICA STATUS\G
-- Relay_Log_File, Relay_Log_Pos 확인

-- 2. Replica를 새 Primary로 승격
STOP REPLICA;
RESET REPLICA ALL;
SET GLOBAL read_only = OFF;

-- 3. 다른 Replica들을 새 Primary로 재연결
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST = '10.0.1.11',   -- 새 Primary IP
    SOURCE_AUTO_POSITION = 1;
START REPLICA;
```

### 수동 Failover (GTID)

GTID 환경에서는 binlog 위치 계산이 불필요하다.

```sql
-- 새 Primary 승격
STOP REPLICA;
RESET REPLICA ALL;
SET GLOBAL read_only = OFF;

-- 나머지 Replica → 새 Primary 재연결
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST         = '10.0.1.11',
    SOURCE_AUTO_POSITION = 1;
START REPLICA;
```

### 자동 Failover 도구

| 도구                    | 설명                                          |
|-------------------------|-----------------------------------------------|
| **MHA**                 | MySQL Master HA. 30초 내 자동 Failover        |
| **Orchestrator**        | 토폴로지 시각화 + 자동 Failover               |
| **MySQL Router**        | InnoDB Cluster 전용 라우팅 + Failover         |
| **AWS RDS Multi-AZ**    | 자동 Failover (60~120초)                      |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 복제 필터링

특정 DB/테이블만 복제하거나 제외할 때 사용한다.

### Primary 측 필터 (binlog 기록 제어)

```ini
# my.cnf
binlog_do_db     = mydb          # 해당 DB만 binlog 기록
binlog_ignore_db = test_db       # 해당 DB는 binlog 제외
```

### Replica 측 필터 (적용 제어)

```ini
# my.cnf
replicate_do_db      = mydb
replicate_ignore_db  = test_db
replicate_do_table   = mydb.orders
replicate_ignore_table = mydb.logs
replicate_wild_do_table    = mydb.order%
replicate_wild_ignore_table = mydb.tmp%
```

⚠️ `binlog_do_db` / `replicate_do_db`는 기본 DB(`USE db`) 기준으로 동작한다.
크로스 DB 쿼리(`INSERT INTO other_db.table`)는 필터링이 의도대로 동작하지 않을 수 있다.
ROW 형식 binlog + Replica 측 필터 조합을 권장한다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 복제 토폴로지

### Single Primary (기본)

```
Primary ──> Replica 1
        ──> Replica 2
        ──> Replica 3
```

### Chain (릴레이)

```
Primary ──> Replica 1 ──> Replica 2
```

- `log_replica_updates = ON` 필요 (Replica 1이 binlog 기록)
- Primary 부하 감소, 복제 지연 누적 위험

### Multi-Source (MySQL 5.7+)

```
Primary A ──┐
            ├──> Replica (aggregation)
Primary B ──┘
```

```sql
-- 채널 이름으로 구분
CHANGE REPLICATION SOURCE TO ... FOR CHANNEL 'primary_a';
CHANGE REPLICATION SOURCE TO ... FOR CHANNEL 'primary_b';
START REPLICA FOR CHANNEL 'primary_a';
START REPLICA FOR CHANNEL 'primary_b';
```

### Group Replication (MySQL InnoDB Cluster)

```
┌──────────────────────────────────┐
│  Node 1 (Primary)                │
│  Node 2 (Secondary)  <──Paxos──> │
│  Node 3 (Secondary)              │
└──────────────────────────────────┘
```

- 쓰기는 Primary 1개, 읽기는 모든 노드
- 자동 Failover (Paxos 합의)
- 최소 3노드 권장

[⬆ 목차로 돌아가기](#목차)

---

## 10. PostgreSQL 복제

### Streaming Replication 구조

```
Primary (WAL sender)              Standby (WAL receiver)
┌──────────────────┐              ┌──────────────────┐
│  WAL (Write-     │ <-- TCP -->  │  WAL receiver    │
│  Ahead Log)      │              │  pg_wal/         │
└──────────────────┘              └──────────────────┘
```

### Primary 설정

```ini
# postgresql.conf
wal_level           = replica
max_wal_senders     = 5
wal_keep_size       = 1GB
synchronous_commit  = on        # 동기: remote_write / 비동기: off
```

```ini
# pg_hba.conf
host  replication  repl  10.0.1.0/24  scram-sha-256
```

```sql
-- 복제 전용 계정
CREATE USER repl WITH REPLICATION ENCRYPTED PASSWORD 'SecurePassword123';
```

### Standby 초기화 및 설정

```bash
# pg_basebackup으로 초기 데이터 복사
pg_basebackup \
    -h 10.0.1.10 \
    -U repl \
    -D /var/lib/postgresql/data \
    -P -Xs -R
# -R: standby.signal + postgresql.auto.conf 자동 생성
```

```ini
# postgresql.auto.conf (pg_basebackup -R 생성)
primary_conninfo = 'host=10.0.1.10 user=repl password=SecurePassword123'
```

```bash
# Standby 시작
pg_ctl start -D /var/lib/postgresql/data
```

### 복제 상태 확인

```sql
-- Primary에서
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       write_lag, flush_lag, replay_lag
FROM pg_stat_replication;

-- Standby에서
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

### 동기 복제 설정

```ini
# postgresql.conf (Primary)
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'
# FIRST 1: 최소 1개 Standby 확인 후 커밋
```

### Failover (PostgreSQL)

```bash
# Standby를 Primary로 승격
pg_ctl promote -D /var/lib/postgresql/data
# 또는
touch /var/lib/postgresql/data/failover.signal
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. AWS RDS Read Replica

```
RDS Primary (Multi-AZ)
    │
    ├──> Read Replica (same region)
    └──> Read Replica (cross-region)
```

### 생성

```bash
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica \
    --source-db-instance-identifier mydb-primary \
    --db-instance-class db.r6g.large \
    --region ap-northeast-2
```

### 특징

| 항목              | MySQL RDS              | Aurora                  |
|-------------------|------------------------|-------------------------|
| 복제 방식         | 비동기 (binlog)        | 공유 스토리지 (즉시)    |
| 최대 Replica 수   | 5개                    | 15개                    |
| 복제 지연         | 수 초 가능             | 수십 ms                 |
| Failover 승격     | 수동                   | 자동 (수십 초)          |
| Cross-Region      | 지원 (추가 비용)       | 지원                    |

```bash
# Read Replica를 독립 Primary로 승격
aws rds promote-read-replica \
    --db-instance-identifier mydb-replica

# 복제 지연 확인 (CloudWatch)
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name ReplicaLag \
    --dimensions Name=DBInstanceIdentifier,Value=mydb-replica \
    --start-time 2026-05-04T10:00:00Z \
    --end-time 2026-05-04T11:00:00Z \
    --period 60 \
    --statistics Average
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 실무 팁

### Tip 1: 읽기/쓰기 분리

```python
import pymysql

write_conn = pymysql.connect(host='primary.db.internal',  db='mydb', ...)
read_conn  = pymysql.connect(host='replica.db.internal',  db='mydb', ...)

# 쓰기
write_conn.cursor().execute("INSERT INTO orders ...")

# 읽기
read_conn.cursor().execute("SELECT * FROM orders ...")
```

### Tip 2: 복제 지연 허용 범위 설정

```python
def get_connection(allow_replica=True):
    if allow_replica:
        lag = get_replica_lag()   # SHOW REPLICA STATUS 파싱
        if lag < 5:               # 5초 이내만 Replica 사용
            return read_conn
    return write_conn
```

### Tip 3: 복제 오류 처리

```sql
-- 복제 오류 확인
SHOW REPLICA STATUS\G
-- Last_Error, Last_SQL_Error 확인

-- GTID 기반 오류 건너뛰기 (데이터 불일치 주의)
SET GTID_NEXT = '3E11FA47-71CA-11E1-9E33-C80AA9429562:101';
BEGIN; COMMIT;
SET GTID_NEXT = 'AUTOMATIC';
START REPLICA;
```

⚠️ `SQL_REPLICA_SKIP_COUNTER`는 GTID 모드에서 사용 불가. GTID 환경에서는 위 방법 사용.

### Tip 4: SSL/TLS 복제 채널 보안

```sql
-- Replica에서 SSL 적용
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST     = '10.0.1.10',
    SOURCE_USER     = 'repl',
    SOURCE_PASSWORD = 'SecurePassword123',
    SOURCE_SSL      = 1,
    SOURCE_SSL_CA   = '/etc/mysql/ssl/ca.pem',
    SOURCE_SSL_CERT = '/etc/mysql/ssl/client-cert.pem',
    SOURCE_SSL_KEY  = '/etc/mysql/ssl/client-key.pem',
    SOURCE_AUTO_POSITION = 1;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html) — ★★★☆☆
- MySQL Documentation: [GTID-Based Replication](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html) — ★★★☆☆
- PostgreSQL Documentation: [Streaming Replication](https://www.postgresql.org/docs/current/warm-standby.html) — ★★★☆☆
- AWS Documentation: [RDS Read Replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-30

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
