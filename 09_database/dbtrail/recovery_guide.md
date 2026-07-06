# dbtrail 복구 가이드

시나리오별 복구 방법을 상세히 설명합니다. 행 단위 복구, CASCADE 복구, 테이블 재구성, Time-Travel 쿼리를 다룹니다.

## 목차

| 섹션                                                                                                                                  |
|---------------------------------------------------------------------------------------------------------------------------------------|
| [1. 복구 흐름](#1-복구-흐름) / [2. 행 단위 복구](#2-행-단위-복구) / [3. CASCADE 복구](#3-cascade-복구)                                |
| [4. 테이블 재구성](#4-테이블-재구성) / [5. Time-Travel SQL](#5-time-travel-sql) / [6. 검증](#6-검증) / [7. 시나리오별](#7-시나리오별) |

---

## 1. 복구 흐름

### 사고 대응 순서

```
1. 사고 인지
   "DELETE FROM orders WHERE customer_id = 100 실행됨"

2. 갭 확인 (복구 가능 여부)
   bintrail status → gaps: 0 ✓

3. 삭제 범위 파악
   bintrail query --table orders --type DELETE --since '2026-07-06 14:00'

4. 복구 SQL 생성
   bintrail recover --table orders --pk 100,101,102

5. 검증
   bintrail verify --table orders

6. 적용
   mysql -h prod < recover.sql
```

### 복구 가능 조건

| 조건                  | 확인 방법                           |
|-----------------------|-------------------------------------|
| 스트리밍 갭 없음      | `bintrail status` → gaps: 0         |
| 해당 시점 인덱싱 완료 | `bintrail status` → index 시간 확인 |
| binlog_row_image=FULL | `bintrail doctor`                   |
| 스키마 스냅샷 존재    | `bintrail baseline list`            |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 행 단위 복구

### 삭제된 행 복구

```bash
# 특정 PK의 삭제 이벤트 확인
bintrail query --schema shop --table orders --pk 123 --event-type DELETE

# 복구 SQL 생성 (INSERT문)
bintrail recover --schema shop --table orders --pk 123
# 출력:
# INSERT INTO `shop`.`orders` (`id`, `customer_id`, `amount`, `status`, `created_at`)
# VALUES (123, 456, 50000, 'active', '2026-07-01 10:00:00');
```

### 변경된 행 롤백

```bash
# 변경 이력 확인
bintrail query --schema shop --table orders --pk 123 --event-type UPDATE

# 특정 시점 이전 값으로 되돌리기
bintrail recover --schema shop --table orders --pk 123 --before '2026-07-06 14:00'
# 출력:
# UPDATE `shop`.`orders` SET `amount` = 50000, `status` = 'active'
# WHERE `id` = 123;
```

### 여러 행 일괄 복구

```bash
# PK 여러 개 지정
bintrail recover --schema shop --table orders --pk 123,124,125,126

# 시간 범위 내 모든 DELETE 복구
bintrail recover --schema shop --table orders \
  --event-type DELETE \
  --since '2026-07-06 14:00' --until '2026-07-06 14:05'

# 파일로 출력
bintrail recover --schema shop --table orders --pk 123,124,125 > recover.sql
```

### 출력 형식

| 이벤트 타입 | 생성되는 SQL                                         |
|-------------|------------------------------------------------------|
| DELETE 복구 | `INSERT INTO ...` (삭제 전 데이터로 재삽입)          |
| UPDATE 롤백 | `UPDATE ... SET ... WHERE pk=...` (이전 값으로 변경) |
| INSERT 취소 | `DELETE FROM ... WHERE pk=...` (삽입 취소)           |

[⬆ 목차로 돌아가기](#목차)

---

## 3. CASCADE 복구

### 문제 상황

```sql
-- 부모 테이블 삭제
DELETE FROM customers WHERE id = 456;
-- → ON DELETE CASCADE로 자식 행도 삭제됨:
--   orders (customer_id=456): 5건 삭제
--   payments (order_id IN (...)): 12건 삭제
--   shipping (order_id IN (...)): 5건 삭제
```

InnoDB가 CASCADE 삭제를 binlog **아래**에서 처리하므로, 일반적인 binlog 기반 도구로는 자식 행 복구가 불가합니다. dbtrail은 FK 관계를 추적하여 자식 행까지 재구성합니다.

### 복구 방법

```bash
bintrail recover-cascade --schema shop --table customers --pk 456

# 출력:
# -- Parent row:
# INSERT INTO `shop`.`customers` (id, name, email) VALUES (456, 'kim', 'kim@example.com');
#
# -- Child rows (orders):
# INSERT INTO `shop`.`orders` (id, customer_id, amount) VALUES (1001, 456, 50000);
# INSERT INTO `shop`.`orders` (id, customer_id, amount) VALUES (1002, 456, 30000);
# ...
#
# -- Grandchild rows (payments):
# INSERT INTO `shop`.`payments` (id, order_id, amount) VALUES (2001, 1001, 50000);
# ...
```

### ON DELETE SET NULL 복구

```sql
-- FK가 SET NULL인 경우:
--   orders.customer_id = NULL (으)로 변경됨
```

```bash
bintrail recover-cascade --schema shop --table customers --pk 456
# → SET NULL된 컬럼도 원래 값으로 복원하는 UPDATE 생성
# UPDATE `shop`.`orders` SET `customer_id` = 456 WHERE `id` = 1001;
```

### 주의사항

| 항목            | 설명                                          |
|-----------------|-----------------------------------------------|
| FK 관계 확인    | 스키마 스냅샷에 FK 정보 포함 필수             |
| 적용 순서       | 부모 → 자식 순서로 INSERT (FK 제약 위반 방지) |
| 자식 행 PK 충돌 | 이미 다른 데이터가 같은 PK를 사용 중이면 실패 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 테이블 재구성

### reconstruct (특정 시점 테이블 상태)

baseline(스냅샷) + 이후 변경 이벤트를 적용하여 특정 시점의 테이블 전체를 재구성합니다.

```bash
# 특정 시점의 테이블 전체 상태
bintrail reconstruct --schema shop --table orders --at '2026-07-06 14:00'

# 특정 행만
bintrail reconstruct --schema shop --table orders --pk 123 --at '2026-07-06 14:00'

# mydumper 호환 형식으로 출력
bintrail reconstruct --schema shop --table orders --at '2026-07-06 14:00' --format mydumper
```

### 동작 원리

```
baseline (2026-07-05 02:00 스냅샷)
    │
    │ + INSERT events (07-05 02:00 ~ 07-06 14:00)
    │ + UPDATE events (변경 적용)
    │ - DELETE events (삭제 적용)
    │
    v
2026-07-06 14:00 시점의 테이블 상태
```

### baseline 관리

```bash
# baseline 생성 (현재 시점 스냅샷)
bintrail baseline --schema shop --table orders

# baseline 목록
bintrail baseline list

# baseline 없으면? → 인덱스 시작 시점부터의 모든 이벤트를 합산 (느림)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Time-Travel SQL

ProxySQL을 경유하면 일반 SQL 문법으로 과거 시점 데이터를 조회할 수 있습니다.

### 구성

```
Application → ProxySQL (6033) → dbtrail shim → MySQL (3306)
                                     │
                                     └─ AS OF 감지 → DuckDB index 조회
```

### 사용

```sql
-- 과거 시점 조회
SELECT * FROM orders WHERE id = 123 AS OF '2026-07-06 14:00:00';

-- 현재 vs 과거 비교
SELECT
  curr.amount AS current_amount,
  past.amount AS past_amount
FROM orders curr
JOIN orders AS OF '2026-07-01' past ON curr.id = past.id
WHERE curr.id = 123;
```

### 제약

| 제약             | 설명                                 |
|------------------|--------------------------------------|
| ProxySQL 필수    | AS OF 구문을 dbtrail shim이 인터셉트 |
| 읽기 전용        | AS OF 쿼리는 SELECT만 가능           |
| 인덱싱 완료 필요 | 아직 인덱싱 안 된 시점은 조회 불가   |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

### verify (복구 무결성)

```bash
# baseline + 이벤트 적용 결과가 현재 DB와 일치하는지 확인
bintrail verify --schema shop --table orders
# ✓ 1,234,567 rows verified, 0 mismatches, 0 gaps

# 특정 시점까지만 검증
bintrail verify --schema shop --table orders --at '2026-07-06 14:00'
```

### 검증 대상

| 검증 항목   | 설명                        |
|-------------|-----------------------------|
| 행 수 일치  | reconstruct 결과 vs 실제 DB |
| 값 일치     | 모든 컬럼 값 비교           |
| 갭 없음     | 스트리밍 누락 구간 없음     |
| 스키마 일치 | 스냅샷 vs 현재 스키마       |

### status (실시간 상태)

```bash
bintrail status
# server: mysql-prod (192.0.2.1:3306)
# stream: 2026-07-06 17:30:00 (lag: 2s, gaps: 0)
# index:  2026-07-06 17:29:55 (5s behind stream)
# baseline: 2026-07-06 02:00:00 (shop.orders, shop.customers)
# storage: s3://my-bucket/dbtrail/ (12.5 GB, 847 files)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 시나리오별

### 시나리오 A: 실수로 WHERE 없이 UPDATE

```sql
-- 사고: 모든 주문 금액이 0으로 변경됨
UPDATE orders SET amount = 0;  -- WHERE 빠뜨림
```

```bash
# 1. 변경 범위 확인
bintrail query --table orders --event-type UPDATE --since '2026-07-06 14:30' \
  --changed-column amount | wc -l
# 50,000건

# 2. 복구 SQL 생성 (원래 amount로 되돌리기)
bintrail recover --table orders --event-type UPDATE \
  --since '2026-07-06 14:30' --until '2026-07-06 14:31' > recover_amount.sql

# 3. 확인
head -5 recover_amount.sql
# UPDATE `shop`.`orders` SET `amount` = 50000 WHERE `id` = 1;
# UPDATE `shop`.`orders` SET `amount` = 30000 WHERE `id` = 2;

# 4. 적용
mysql -h prod shop < recover_amount.sql
```

### 시나리오 B: 특정 고객 데이터 삭제 (CASCADE)

```bash
# 1. 삭제된 부모 행 확인
bintrail query --table customers --pk 456 --event-type DELETE

# 2. CASCADE 포함 전체 복구
bintrail recover-cascade --table customers --pk 456 > recover_customer.sql

# 3. FK 순서 확인 (부모 먼저)
head -3 recover_customer.sql
# INSERT INTO customers ...  (부모)
# INSERT INTO orders ...     (자식)
# INSERT INTO payments ...   (손자)

# 4. 적용
mysql -h prod shop < recover_customer.sql
```

### 시나리오 C: "어제 이 시점에 이 데이터가 어땠어?"

```bash
# CLI
bintrail reconstruct --table orders --pk 123 --at '2026-07-05 09:00'

# SQL (ProxySQL 경유)
mysql -h proxy -P 6033 -e "SELECT * FROM orders WHERE id=123 AS OF '2026-07-05 09:00'"
```

### 시나리오 D: "이 행을 누가 변경했어?"

```bash
bintrail whochanged --table orders --pk 123
# event_timestamp: 2026-07-06 14:32:11
# event_type: UPDATE
# user: admin@10.200.90.155
# program: python3
# confidence: corroborated (identity cache)
# query_text: UPDATE orders SET amount=0 WHERE id=123
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [README.md](./README.md)
- [architecture.md](./architecture.md)
- dbtrail Query & Recovery: [github.com/dbtrail/dbtrail/blob/main/docs/query-and-recovery.md](https://github.com/dbtrail/dbtrail/blob/main/docs/query-and-recovery.md) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-06

**마지막 업데이트**: 2026-07-06

© 2026 siasia86. Licensed under CC BY 4.0.
