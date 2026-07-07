# RDBMS 트랜잭션 (Transaction)

## 목차

| 단계 | 섹션                                                                                |
|------|-------------------------------------------------------------------------------------|
| 기초 | [1. 트랜잭션 개념](#1-트랜잭션-개념) / [2. ACID](#2-acid)                           |
| 격리 | [3. 격리 수준](#3-격리-수준) / [4. 격리 수준별 문제 현상](#4-격리-수준별-문제-현상) |
| 고급 | [5. 데드락](#5-데드락) / [6. MVCC](#6-mvcc) / [7. 실무 팁](#7-실무-팁)              |

---

## 1. 트랜잭션 개념

트랜잭션은 **하나의 논리적 작업 단위**로 처리되어야 하는 SQL 집합입니다.
전부 성공하거나 전부 실패해야 합니다.

```sql
START TRANSACTION;
    UPDATE accounts SET balance = balance - 10000 WHERE id = 1;
    UPDATE accounts SET balance = balance + 10000 WHERE id = 2;
COMMIT;
-- 중간에 오류 발생 시
ROLLBACK;
```

### SAVEPOINT

트랜잭션 내 부분 롤백 지점을 설정합니다.

```sql
START TRANSACTION;
    INSERT INTO orders (user_id, amount) VALUES (1, 5000);
    SAVEPOINT sp1;

    INSERT INTO order_items (order_id, product_id) VALUES (LAST_INSERT_ID(), 99);
    -- 실패 시 sp1 이후만 롤백
    ROLLBACK TO SAVEPOINT sp1;
COMMIT;
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. ACID

| 속성       | 영문        | 설명                             | 보장 방법        |
|------------|-------------|----------------------------------|------------------|
| **원자성** | Atomicity   | 전부 성공 또는 전부 실패         | Undo Log         |
| **일관성** | Consistency | 트랜잭션 전후 데이터 무결성 유지 | 제약조건, 트리거 |
| **격리성** | Isolation   | 동시 트랜잭션 간 간섭 없음       | Lock, MVCC       |
| **지속성** | Durability  | 커밋된 데이터는 영구 저장        | Redo Log, WAL    |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 격리 수준

낮을수록 동시성 높음, 높을수록 정합성 높음.

| 격리 수준        | Dirty Read | Non-Repeatable Read | Phantom Read            | 성능      |
|------------------|------------|---------------------|-------------------------|-----------|
| READ UNCOMMITTED | ✅ 발생    | ✅ 발생             | ✅ 발생                 | 가장 높음 |
| READ COMMITTED   | ❌ 방지    | ✅ 발생             | ✅ 발생                 | 높음      |
| REPEATABLE READ  | ❌ 방지    | ❌ 방지             | ✅ 발생 (InnoDB는 방지) | 중간      |
| SERIALIZABLE     | ❌ 방지    | ❌ 방지             | ❌ 방지                 | 최저      |

### 기본값

| DBMS         | 기본 격리 수준  |
|--------------|-----------------|
| MySQL InnoDB | REPEATABLE READ |
| PostgreSQL   | READ COMMITTED  |
| Oracle       | READ COMMITTED  |

```sql
-- MySQL: 격리 수준 확인/변경
SELECT @@transaction_isolation;
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- PostgreSQL
SHOW transaction_isolation;
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 격리 수준별 문제 현상

### Dirty Read

커밋되지 않은 데이터를 읽는 현상.

```
T1: UPDATE balance = 0 (미커밋)
T2: SELECT balance → 0 읽음  ← Dirty Read
T1: ROLLBACK → balance 원복
T2: 잘못된 데이터로 처리
```

### Non-Repeatable Read

같은 쿼리를 두 번 실행했을 때 결과가 다른 현상.

```
T1: SELECT balance → 1000
T2: UPDATE balance = 500; COMMIT
T1: SELECT balance → 500  ← 다른 결과
```

### Phantom Read

같은 조건의 쿼리를 두 번 실행했을 때 행 수가 다른 현상.

```
T1: SELECT COUNT(*) WHERE age > 20 → 5건
T2: INSERT (age=25); COMMIT
T1: SELECT COUNT(*) WHERE age > 20 → 6건  ← Phantom
```

### InnoDB REPEATABLE READ에서 Phantom Read 방지

InnoDB는 REPEATABLE READ에서 **Gap Lock**으로 Phantom Read를 방지합니다.

```sql
-- T1
SELECT * FROM users WHERE age > 20 FOR UPDATE;
-- age > 20 범위에 Gap Lock 설정

-- T2
INSERT INTO users (age) VALUES (25);
-- Gap Lock으로 인해 대기
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 데드락

두 트랜잭션이 서로 상대방의 Lock을 기다리는 상태.

```
T1: LOCK A → LOCK B 대기
T2: LOCK B → LOCK A 대기
→ 무한 대기 (Deadlock)
```

### 탐지 및 해결

```sql
-- MySQL: 데드락 로그 확인
SHOW ENGINE INNODB STATUS\G
-- LATEST DETECTED DEADLOCK 섹션 확인

-- PostgreSQL: 데드락 로그
-- postgresql.conf: log_lock_waits = on, deadlock_timeout = 1s
SELECT * FROM pg_locks WHERE NOT granted;
```

### 데드락 방지 패턴

```sql
-- 나쁜 예: 트랜잭션마다 다른 순서로 Lock
-- T1: UPDATE users → UPDATE orders
-- T2: UPDATE orders → UPDATE users

-- 좋은 예: 항상 동일한 순서로 Lock
-- T1, T2 모두: UPDATE users → UPDATE orders (낮은 PK 순)
UPDATE users SET ... WHERE id = 1;
UPDATE orders SET ... WHERE user_id = 1;
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. MVCC

Multi-Version Concurrency Control. 읽기와 쓰기가 서로 블로킹하지 않도록 데이터의 여러 버전을 유지합니다.

```
Undo Log (버전 체인):
현재: balance = 500 (T2 커밋)
이전: balance = 1000 (T1 시작 시점)

T1 (REPEATABLE READ): 자신의 시작 시점 스냅샷 읽음 → 1000
T3 (새 트랜잭션): 최신 커밋 읽음 → 500
```

| 항목           | Lock 기반 | MVCC                     |
|----------------|-----------|--------------------------|
| 읽기-쓰기 충돌 | 블로킹    | 비블로킹                 |
| 저장 공간      | 적음      | Undo Log 필요            |
| 구현 DBMS      | -         | MySQL InnoDB, PostgreSQL |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: 트랜잭션은 짧게

```sql
-- 나쁜 예: 트랜잭션 내 외부 API 호출
START TRANSACTION;
    UPDATE orders SET status = 'processing';
    -- 외부 결제 API 호출 (수 초 소요) ← Lock 점유 중
COMMIT;

-- 좋은 예: 외부 호출 후 트랜잭션
-- 1. 외부 API 호출
-- 2. START TRANSACTION → UPDATE → COMMIT
```

### Tip 2: autocommit 주의

```sql
-- MySQL 기본값: autocommit = ON (각 쿼리가 자동 커밋)
SELECT @@autocommit;

-- 배치 INSERT 성능 향상
SET autocommit = 0;
INSERT INTO logs ... (반복);
COMMIT;
SET autocommit = 1;
```

### Tip 3: FOR UPDATE vs FOR SHARE

```sql
-- FOR UPDATE: 배타 Lock (다른 FOR UPDATE/FOR SHARE 대기, 일반 SELECT는 MVCC로 허용)
SELECT * FROM inventory WHERE product_id = 1 FOR UPDATE;

-- FOR SHARE (FOR KEY SHARE): 읽기 Lock (다른 트랜잭션 읽기는 허용)
SELECT * FROM inventory WHERE product_id = 1 FOR SHARE;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [InnoDB Transaction Model](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-model.html) — ★★★☆☆
- PostgreSQL Documentation: [Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — ★★★☆☆
- RFC 그 외: Bernstein, Philip A. "Concurrency Control and Recovery in Database Systems" — ★★★★☆

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
