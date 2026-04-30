# RDBMS JOIN

## 목차

| 단계 | 섹션                                                                                                                                              |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. JOIN 종류](#1-join-종류) / [2. JOIN 문법](#2-join-문법)                                                                                        |
| 원리 | [3. JOIN 실행 방식](#3-join-실행-방식) / [4. 실행 계획 분석](#4-실행-계획-분석)                                                                    |
| 고급 | [5. JOIN 최적화 팁](#5-join-최적화-팁) / [6. 실전 패턴](#6-실전-패턴) |

---

## 1. JOIN 종류

```
Table A        Table B
┌───┐          ┌───┐
│ 1 │          │ 1 │
│ 2 │          │ 3 │
│ 3 │          │ 4 │
└───┘          └───┘

INNER JOIN     LEFT JOIN      RIGHT JOIN     FULL OUTER JOIN
  ┌─┐           ┌───┐          ┌───┐           ┌─────┐
  │2│3│         │1│2│3│        │1│3│4│          │1│2│3│4│
  └─┘           └───┘          └───┘           └─────┘
  (교집합)      (A 전체)       (B 전체)        (합집합)
```

| JOIN 종류 | 결과 | NULL 포함 |
|-----------|------|-----------|
| INNER JOIN | 양쪽 모두 일치하는 행 | 없음 |
| LEFT JOIN | 왼쪽 전체 + 오른쪽 일치 | 오른쪽 불일치 시 NULL |
| RIGHT JOIN | 오른쪽 전체 + 왼쪽 일치 | 왼쪽 불일치 시 NULL |
| FULL OUTER JOIN | 양쪽 전체 | 불일치 시 양쪽 NULL |
| CROSS JOIN | 카테시안 곱 (A행 × B행) | 없음 |
| SELF JOIN | 같은 테이블 자기 참조 | 없음 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. JOIN 문법

### INNER JOIN

```sql
SELECT o.order_id, u.username, o.amount
FROM orders o
INNER JOIN users u ON o.user_id = u.user_id
WHERE o.status = 'completed';
```

### LEFT JOIN (NULL 체크로 미매칭 행 찾기)

```sql
-- 주문이 없는 사용자 찾기
SELECT u.user_id, u.username
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE o.order_id IS NULL;
```

### FULL OUTER JOIN (MySQL은 미지원 → UNION으로 대체)

```sql
-- PostgreSQL
SELECT * FROM a FULL OUTER JOIN b ON a.id = b.id;

-- MySQL (UNION으로 구현)
SELECT a.*, b.*
FROM a LEFT JOIN b ON a.id = b.id
UNION
SELECT a.*, b.*
FROM a RIGHT JOIN b ON a.id = b.id
WHERE a.id IS NULL;
```

### SELF JOIN

```sql
-- 직원-관리자 관계
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;
```

### 다중 JOIN

```sql
SELECT o.order_id, u.username, p.product_name, oi.quantity
FROM orders o
JOIN users u        ON o.user_id    = u.user_id
JOIN order_items oi ON o.order_id   = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.created_at >= '2026-01-01';
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. JOIN 실행 방식

옵티마이저가 선택하는 3가지 물리적 JOIN 알고리즘.

### Nested Loop Join

```
for each row in outer_table:
    for each row in inner_table:
        if join_condition: output
```

- 소규모 테이블, 인덱스 있을 때 효율적
- 복잡도: O(N × M)

### Hash Join

```
1. Build phase: 작은 테이블을 해시 테이블로 메모리에 적재
2. Probe phase: 큰 테이블을 스캔하며 해시 테이블 조회
```

- 대용량 테이블, 인덱스 없을 때 효율적
- MySQL 8.0+, PostgreSQL 지원
- 복잡도: O(N + M)

### Merge Join (Sort-Merge Join)

```
1. 양쪽 테이블을 JOIN 키 기준으로 정렬
2. 정렬된 두 테이블을 순차 병합
```

- 이미 정렬된 데이터(인덱스)에 효율적
- 복잡도: O(N log N + M log M)

### 비교

| 방식 | 적합한 경우 | 메모리 | 인덱스 필요 |
|------|------------|--------|-------------|
| Nested Loop | 소규모, 인덱스 있음 | 적음 | 권장 |
| Hash Join | 대용량, 인덱스 없음 | 많음 | 불필요 |
| Merge Join | 정렬된 대용량 | 중간 | 있으면 유리 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 실행 계획 분석

```sql
EXPLAIN SELECT o.order_id, u.username
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.status = 'completed';
```

### MySQL EXPLAIN 주요 컬럼

| 컬럼 | 의미 |
|------|------|
| `type` | 접근 방식 (ref, range, ALL 등) |
| `key` | 사용된 인덱스 |
| `rows` | 예상 스캔 행 수 |
| `Extra` | `Using index`, `Using temporary`, `Using filesort` |

⚠️ `Using temporary` + `Using filesort` 동시 출현 시 성능 위험 신호.

### PostgreSQL EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT o.order_id, u.username
FROM orders o
JOIN users u ON o.user_id = u.user_id;
```

```
Hash Join  (cost=125.00..890.00 rows=5000)
  Hash Cond: (o.user_id = u.user_id)
  -> Seq Scan on orders o
  -> Hash
       -> Seq Scan on users u
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. JOIN 최적화 팁

### Tip 1: JOIN 컬럼에 인덱스

```sql
-- orders.user_id에 인덱스 없으면 Full Table Scan
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

### Tip 2: 드라이빙 테이블은 작은 쪽으로

```sql
-- 나쁜 예: 큰 테이블(orders)이 드라이빙
SELECT * FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE u.status = 'active';

-- 좋은 예: WHERE 조건으로 작은 결과셋이 드라이빙
SELECT * FROM users u JOIN orders o ON u.user_id = o.user_id
WHERE u.status = 'active';
```

### Tip 3: SELECT * 대신 필요한 컬럼만

```sql
-- 나쁜 예
SELECT * FROM orders o JOIN users u ON o.user_id = u.user_id;

-- 좋은 예: Covering Index 활용 가능
SELECT o.order_id, o.amount, u.username
FROM orders o JOIN users u ON o.user_id = u.user_id;
```

### Tip 4: 서브쿼리 대신 JOIN

```sql
-- 나쁜 예: 상관 서브쿼리 (행마다 실행)
SELECT * FROM users u
WHERE (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.user_id) > 5;

-- 좋은 예: JOIN + GROUP BY
SELECT u.*
FROM users u
JOIN (
    SELECT user_id FROM orders
    GROUP BY user_id HAVING COUNT(*) > 5
) o ON u.user_id = o.user_id;
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실전 패턴

### 패턴 1: 최근 주문 1건만 JOIN

```sql
-- MySQL 8.0+ (ROW_NUMBER)
SELECT u.username, o.order_id, o.amount
FROM users u
JOIN (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM orders
) o ON u.user_id = o.user_id AND o.rn = 1;
```

### 패턴 2: 집계 후 JOIN

```sql
-- 사용자별 총 주문금액과 사용자 정보
SELECT u.username, s.total_amount, s.order_count
FROM users u
JOIN (
    SELECT user_id,
           SUM(amount)  AS total_amount,
           COUNT(*)     AS order_count
    FROM orders
    GROUP BY user_id
) s ON u.user_id = s.user_id;
```

### 패턴 3: 계층 구조 (재귀 CTE)

```sql
-- PostgreSQL / MySQL 8.0+
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY depth, id;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [JOIN Syntax](https://dev.mysql.com/doc/refman/8.0/en/join.html) — ★★★☆☆
- PostgreSQL Documentation: [Joins Between Tables](https://www.postgresql.org/docs/current/tutorial-join.html) — ★★★☆☆
- Use The Index, Luke: [Join](https://use-the-index-luke.com/sql/join) — ★★★☆☆

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
