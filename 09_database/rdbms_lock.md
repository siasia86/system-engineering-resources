# RDBMS Lock (잠금)

## 목차

| 단계 | 섹션                                                                              |
|------|-----------------------------------------------------------------------------------|
| 기초 | [1. Lock 개념](#1-lock-개념) / [2. Lock 종류](#2-lock-종류)                       |
| 심화 | [3. InnoDB Lock](#3-innodb-lock) / [4. 데드락 탐지와 해결](#4-데드락-탐지와-해결) |
| 고급 | [5. Lock 모니터링](#5-lock-모니터링) / [6. Lock 최소화 팁](#6-lock-최소화-팁)     |

---

## 1. Lock 개념

동시에 여러 트랜잭션이 같은 데이터에 접근할 때 정합성을 보장하기 위한 메커니즘.

### Lock 호환성 매트릭스

| 요청 \ 보유       | Shared (S) | Exclusive (X) |
|-------------------|------------|---------------|
| **Shared (S)**    | ✅ 호환    | ❌ 대기       |
| **Exclusive (X)** | ❌ 대기    | ❌ 대기       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Lock 종류

### 범위에 따른 분류

| Lock           | 범위          | 획득 시점                         |
|----------------|---------------|-----------------------------------|
| **Table Lock** | 테이블 전체   | DDL, LOCK TABLES, MyISAM DML      |
| **Row Lock**   | 특정 행       | InnoDB DML (SELECT FOR UPDATE 등) |
| **Page Lock**  | 데이터 페이지 | 일부 DBMS                         |

### 성격에 따른 분류

| Lock                   | 설명                               | SQL                                         |
|------------------------|------------------------------------|---------------------------------------------|
| **Shared Lock (S)**    | 읽기 Lock. 다른 S Lock과 공존 가능 | `SELECT ... FOR SHARE`                      |
| **Exclusive Lock (X)** | 쓰기 Lock. 다른 Lock과 공존 불가   | `SELECT ... FOR UPDATE`, `UPDATE`, `DELETE` |
| **Intention Lock**     | 테이블 레벨에서 Row Lock 의도 표시 | 자동 획득                                   |

### InnoDB 전용 Lock

| Lock                      | 설명                                                      |
|---------------------------|-----------------------------------------------------------|
| **Record Lock**           | 인덱스 레코드 자체에 대한 Lock                            |
| **Gap Lock**              | 인덱스 레코드 사이의 간격에 대한 Lock (Phantom Read 방지) |
| **Next-Key Lock**         | Record Lock + Gap Lock 결합 (InnoDB 기본)                 |
| **Insert Intention Lock** | INSERT 전 Gap에 대한 의도 Lock                            |

[⬆ 목차로 돌아가기](#목차)

---

## 3. InnoDB Lock

### Record Lock vs Gap Lock

```sql
-- 테이블: id = 1, 5, 10, 20

-- Record Lock: id=5 행에만 Lock
SELECT * FROM t WHERE id = 5 FOR UPDATE;

-- Gap Lock: (5, 10) 사이 간격에 Lock → id=7 INSERT 차단
SELECT * FROM t WHERE id > 5 AND id < 10 FOR UPDATE;

-- Next-Key Lock: (-∞, 1], (1, 5], (5, 10], (10, 20], (20, +∞)
-- REPEATABLE READ 기본 동작
SELECT * FROM t WHERE id BETWEEN 5 AND 10 FOR UPDATE;
```

### Gap Lock 비활성화

```sql
-- READ COMMITTED에서는 Gap Lock 미사용
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 또는 innodb_locks_unsafe_for_binlog=1 (deprecated)
```

### Table Lock

```sql
-- 명시적 Table Lock
LOCK TABLES orders READ;   -- Shared
LOCK TABLES orders WRITE;  -- Exclusive
UNLOCK TABLES;

-- DDL은 묵시적 Table Lock (MDL: Metadata Lock)
ALTER TABLE orders ADD COLUMN note TEXT;
-- 실행 중 다른 DML 대기
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 데드락 탐지와 해결

### 데드락 발생 패턴

```
T1: UPDATE users WHERE id=1  → Lock A 획득
T2: UPDATE users WHERE id=2  → Lock B 획득
T1: UPDATE users WHERE id=2  → Lock B 대기
T2: UPDATE users WHERE id=1  → Lock A 대기 → DEADLOCK
```

### MySQL 데드락 확인

```sql
-- 최근 데드락 정보
SHOW ENGINE INNODB STATUS\G
-- LATEST DETECTED DEADLOCK 섹션 확인

-- 데드락 로그 활성화
SET GLOBAL innodb_print_all_deadlocks = 1;
-- /var/log/mysql/error.log 에서 확인
```

### PostgreSQL 데드락 확인

```sql
-- 현재 Lock 대기 상황
SELECT
    blocked.pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE blocked.wait_event_type = 'Lock';
```

### 데드락 방지 전략

```sql
-- 1. 항상 동일한 순서로 Lock 획득
-- 나쁜 예
-- T1: UPDATE users id=1 → UPDATE orders id=100
-- T2: UPDATE orders id=100 → UPDATE users id=1

-- 좋은 예: 낮은 PK 순서로 통일
-- T1, T2 모두: 낮은 id → 높은 id 순서

-- 2. 트랜잭션 짧게 유지
-- 3. SELECT FOR UPDATE 범위 최소화
-- 4. 인덱스 사용으로 Lock 범위 축소
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Lock 모니터링

### MySQL

```sql
-- MySQL 8.0+ (권장)
SELECT * FROM performance_schema.data_lock_waits;
SELECT * FROM performance_schema.data_locks;

-- MySQL 5.7 이하 (8.0에서 innodb_lock_waits 뷰 제거됨)
-- SELECT r.trx_id AS waiting_trx, b.trx_id AS blocking_trx
-- FROM information_schema.innodb_lock_waits w
-- JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
-- JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;

-- 오래된 트랜잭션 확인
SELECT trx_id, trx_started, trx_query
FROM information_schema.innodb_trx
WHERE trx_started < NOW() - INTERVAL 60 SECOND;
```

### PostgreSQL

```sql
-- Lock 현황
SELECT pid, mode, granted, relation::regclass, query
FROM pg_locks l
JOIN pg_stat_activity a USING (pid)
WHERE relation IS NOT NULL;

-- Lock 대기 강제 종료
SELECT pg_cancel_backend(pid);   -- 쿼리만 취소
SELECT pg_terminate_backend(pid); -- 연결 종료
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Lock 최소화 팁

### Tip 1: 인덱스로 Lock 범위 축소

```sql
-- 인덱스 없으면 Full Table Scan → Table Lock에 가까운 효과
UPDATE orders SET status = 'done' WHERE user_id = 1;
-- user_id 인덱스 없으면 전체 행 Lock

CREATE INDEX idx_orders_user_id ON orders (user_id);
-- 인덱스 있으면 해당 행만 Lock
```

### Tip 2: SELECT FOR UPDATE 범위 최소화

```sql
-- 나쁜 예: 불필요하게 넓은 범위
SELECT * FROM orders WHERE created_at > '2026-01-01' FOR UPDATE;

-- 좋은 예: 실제 수정할 행만
SELECT * FROM orders WHERE order_id = 1001 FOR UPDATE;
```

### Tip 3: NOWAIT / SKIP LOCKED

```sql
-- Lock 획득 실패 시 즉시 오류 반환 (대기 없음)
SELECT * FROM orders WHERE order_id = 1 FOR UPDATE NOWAIT;

-- Lock된 행 건너뛰기 (큐 처리에 유용)
SELECT * FROM jobs WHERE status = 'pending'
LIMIT 10 FOR UPDATE SKIP LOCKED;
```

### Tip 4: Optimistic Lock (낙관적 잠금)

```sql
-- version 컬럼으로 충돌 감지
UPDATE orders
SET status = 'done', version = version + 1
WHERE order_id = 1 AND version = 3;
-- 영향받은 행이 0이면 다른 트랜잭션이 먼저 수정 → 재시도
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [InnoDB Locking](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking.html) — ★★★☆☆
- PostgreSQL Documentation: [Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html) — ★★★☆☆
- MySQL Documentation: [Deadlocks](https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks.html) — ★★★☆☆

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
