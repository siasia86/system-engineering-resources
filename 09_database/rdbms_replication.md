# RDBMS 복제 (Replication)

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 복제 개념](#1-복제-개념) / [2. MySQL 복제 구조](#2-mysql-복제-구조)                                                                                            |
| 설정 | [3. GTID 복제](#3-gtid-복제) / [4. 복제 지연 모니터링](#4-복제-지연-모니터링)                                                                                      |
| 고급 | [5. 복제 토폴로지](#5-복제-토폴로지) / [6. AWS RDS Read Replica](#6-aws-rds-read-replica) / [7. 실무 팁](#7-실무-팁) |

---

## 1. 복제 개념

Primary(Master)의 변경사항을 Replica(Slave)에 자동으로 전파하는 기능.

### 목적

| 목적 | 설명 |
|------|------|
| **읽기 분산** | Read Replica로 SELECT 부하 분산 |
| **고가용성** | Primary 장애 시 Replica로 Failover |
| **백업** | Replica에서 백업 수행 (Primary 부하 없음) |
| **지리적 분산** | 다른 리전에 Replica 배치 |

### 복제 방식

| 방식 | 설명 | 일관성 |
|------|------|--------|
| **비동기 복제** | Primary 커밋 후 Replica에 비동기 전송 | 복제 지연 가능 |
| **반동기 복제** | 최소 1개 Replica 수신 확인 후 커밋 | 지연 최소화 |
| **동기 복제** | 모든 Replica 적용 확인 후 커밋 | 완전 일관성, 성능 저하 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. MySQL 복제 구조

```
Primary                          Replica
┌─────────────┐                 ┌─────────────┐
│  Binary Log │ ──── I/O ────>  │  Relay Log  │
│  (binlog)   │    Thread       │             │
└─────────────┘                 └──────┬──────┘
                                       │ SQL Thread
                                       v
                                  데이터 적용
```

### Binary Log 형식

| 형식 | 설명 | 권장 |
|------|------|------|
| `STATEMENT` | SQL 문 그대로 기록 | 비권장 (비결정적 함수 문제) |
| `ROW` | 변경된 행 데이터 기록 | ✅ 권장 |
| `MIXED` | 상황에 따라 자동 선택 | 일반적 |

```sql
-- 현재 binlog 형식 확인
SHOW VARIABLES LIKE 'binlog_format';

-- Primary 상태 확인
SHOW MASTER STATUS\G

-- Replica 상태 확인
SHOW REPLICA STATUS\G  -- MySQL 8.0+
SHOW SLAVE STATUS\G    -- 구버전
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. GTID 복제

GTID(Global Transaction Identifier)는 각 트랜잭션에 고유 ID를 부여하여 복제 위치를 명확히 추적한다.

```
GTID 형식: source_id:transaction_id
예시: 3E11FA47-71CA-11E1-9E33-C80AA9429562:1-100
```

### GTID 활성화

```ini
# my.cnf
gtid_mode = ON
enforce_gtid_consistency = ON
binlog_format = ROW
log_replica_updates = ON
```

### GTID 기반 복제 설정

```sql
-- Replica에서 실행
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST = '10.0.1.10',
    SOURCE_USER = 'repl',
    SOURCE_PASSWORD = 'SecurePassword123',
    SOURCE_AUTO_POSITION = 1;  -- GTID 자동 위치

START REPLICA;
```

### GTID vs 전통 복제 비교

| 항목 | 전통 복제 | GTID 복제 |
|------|-----------|-----------|
| 위치 추적 | binlog 파일명 + 오프셋 | 트랜잭션 ID |
| Failover | 수동 위치 계산 필요 | 자동 |
| 복제 재설정 | 복잡 | 단순 |
| 권장 여부 | 레거시 | ✅ 권장 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 복제 지연 모니터링

### MySQL

```sql
-- Replica 지연 확인
SHOW REPLICA STATUS\G
-- Seconds_Behind_Source: 복제 지연 초

-- Performance Schema
SELECT * FROM replication_applier_status_by_worker\G
```

### 복제 지연 원인과 해결

| 원인 | 해결 |
|------|------|
| 단일 스레드 적용 | 병렬 복제 활성화 |
| 대용량 트랜잭션 | 트랜잭션 분할 |
| 네트워크 지연 | 네트워크 대역폭 확인 |
| Replica 서버 부하 | 읽기 쿼리 분산 |

```sql
-- 병렬 복제 활성화 (MySQL 5.7+)
SET GLOBAL replica_parallel_workers = 4;
SET GLOBAL replica_parallel_type = 'LOGICAL_CLOCK';
```

### 복제 지연 알림 (Prometheus)

```yaml
# mysql_exporter 메트릭
mysql_slave_status_seconds_behind_master > 30
→ 알림 발송
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 복제 토폴로지

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

### Multi-Source (MySQL 5.7+)

```
Primary A ──┐
            ├──> Replica (집계용)
Primary B ──┘
```

### Group Replication (MySQL InnoDB Cluster)

```
┌─────────────────────────────┐
│  Node 1 (Primary)           │
│  Node 2 (Secondary)  ◄────► │  Paxos 합의
│  Node 3 (Secondary)         │
└─────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. AWS RDS Read Replica

```
RDS Primary (Multi-AZ)
    │
    ├──> Read Replica (같은 리전)
    └──> Read Replica (다른 리전, Cross-Region)
```

### 생성

```bash
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica \
    --source-db-instance-identifier mydb-primary \
    --db-instance-class db.r6g.large
```

### 특징

| 항목 | 설명 |
|------|------|
| 복제 방식 | 비동기 (MySQL binlog 기반) |
| 최대 Replica 수 | 5개 (MySQL), 15개 (Aurora) |
| Failover 승격 | 수동 (`promote-read-replica`) |
| Cross-Region | 지원 (추가 비용) |
| 스토리지 | Primary와 독립 |

```bash
# Read Replica를 독립 Primary로 승격
aws rds promote-read-replica \
    --db-instance-identifier mydb-replica
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: 읽기/쓰기 분리

```python
# 애플리케이션에서 분리
import pymysql

write_conn = pymysql.connect(host='primary.db.internal', ...)
read_conn  = pymysql.connect(host='replica.db.internal', ...)

# 쓰기
write_conn.cursor().execute("INSERT INTO ...")

# 읽기
read_conn.cursor().execute("SELECT ...")
```

### Tip 2: 복제 지연 허용 범위 설정

```python
# 복제 지연이 허용 범위 초과 시 Primary로 폴백
def get_connection(allow_replica=True):
    if allow_replica:
        lag = get_replica_lag()
        if lag < 5:  # 5초 이내
            return read_conn
    return write_conn
```

### Tip 3: 복제 오류 처리

```sql
-- 복제 오류 확인
SHOW REPLICA STATUS\G
-- Last_Error, Last_SQL_Error 확인

-- 특정 오류 건너뛰기 (주의: 데이터 불일치 가능)
SET GLOBAL SQL_REPLICA_SKIP_COUNTER = 1;
START REPLICA;

-- GTID 기반 건너뛰기
SET GTID_NEXT = '3E11FA47:101';
BEGIN; COMMIT;
SET GTID_NEXT = 'AUTOMATIC';
START REPLICA;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html) — ★★★☆☆
- MySQL Documentation: [GTID-Based Replication](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html) — ★★★☆☆
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

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
