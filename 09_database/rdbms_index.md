# RDBMS Index (인덱스)

## 목차

| 단계 | 섹션                                                                                                                   |
|------|------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. Index 개념](#1-index-개념) / [2. Index 종류](#2-index-종류) / [3. Index 생성과 삭제](#3-index-생성과-삭제)         |
| 원리 | [4. B-Tree 구조](#4-b-tree-구조) / [5. 실행 계획 분석](#5-실행-계획-분석)                                              |
| 고급 | [6. 복합 인덱스 설계](#6-복합-인덱스-설계) / [7. Index 최적화 팁](#7-index-최적화-팁) / [8. Index 관리](#8-index-관리) |

---

## 1. Index 개념

Index는 테이블의 특정 컬럼에 대한 **검색 속도를 높이기 위한 자료구조**입니다.
책의 색인처럼 원하는 데이터의 위치를 빠르게 찾아줍니다.

### 트레이드오프

| 항목        | 인덱스 있음             | 인덱스 없음                  |
|-------------|-------------------------|------------------------------|
| SELECT 속도 | 빠름 (O(log n))         | 느림 (Full Table Scan, O(n)) |
| INSERT 속도 | 느림 (인덱스 갱신 필요) | 빠름                         |
| UPDATE 속도 | 느림 (인덱스 갱신 필요) | 빠름                         |
| DELETE 속도 | 느림 (인덱스 갱신 필요) | 빠름                         |
| 저장 공간   | 추가 공간 필요          | 없음                         |

### 인덱스가 효과적인 경우

- WHERE 절에 자주 사용되는 컬럼
- JOIN ON 조건에 사용되는 컬럼
- ORDER BY, GROUP BY에 사용되는 컬럼
- 카디널리티(Cardinality)가 높은 컬럼 (값의 종류가 많을수록 효과적)

[⬆ 목차로 돌아가기](#목차)

---

## 2. Index 종류

### 구조에 따른 분류

| 종류                 | 설명                                          | 지원 DBMS                 |
|----------------------|-----------------------------------------------|---------------------------|
| **B-Tree**           | 기본 인덱스. 범위 검색, 정렬에 효과적         | MySQL, PostgreSQL, Oracle |
| **Hash**             | 등치(=) 검색에 최적화. 범위 검색 불가         | MySQL(Memory), PostgreSQL |
| **Full-Text**        | 텍스트 전문 검색 (LIKE '%word%' 대체)         | MySQL, PostgreSQL         |
| **Spatial (R-Tree)** | 공간 데이터(좌표, 지리) 검색                  | MySQL, PostgreSQL         |
| **Bitmap**           | 카디널리티 낮은 컬럼에 효과적 (성별, 상태 등) | Oracle, PostgreSQL        |

### 특성에 따른 분류

| 종류                    | 설명                                                    |
|-------------------------|---------------------------------------------------------|
| **Clustered Index**     | 테이블 데이터 자체가 인덱스 순서로 정렬됨. 테이블당 1개 |
| **Non-Clustered Index** | 별도 인덱스 구조. 테이블당 여러 개 가능                 |
| **Unique Index**        | 중복값 허용 안 함. PRIMARY KEY, UNIQUE 제약에 자동 생성 |
| **Composite Index**     | 2개 이상 컬럼으로 구성된 인덱스                         |
| **Covering Index**      | 쿼리에 필요한 모든 컬럼을 포함하는 인덱스               |
| **Partial Index**       | 조건을 만족하는 행에만 인덱스 생성 (PostgreSQL)         |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Index 생성과 삭제

### 기본 문법

```sql
-- 단일 컬럼 인덱스
CREATE INDEX idx_users_email ON users (email);

-- 유니크 인덱스
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);

-- 복합 인덱스
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at);

-- 내림차순 인덱스 (MySQL 8.0+, PostgreSQL)
CREATE INDEX idx_orders_date_desc ON orders (created_at DESC);

-- 삭제
DROP INDEX idx_users_email ON users;          -- MySQL
DROP INDEX idx_users_email;                   -- PostgreSQL
```

### Partial Index (PostgreSQL)

```sql
-- 활성 사용자만 인덱싱 (전체 대비 인덱스 크기 감소)
CREATE INDEX idx_active_users ON users (email)
WHERE status = 'active';
```

### Covering Index (Include)

```sql
-- PostgreSQL: INCLUDE로 커버링 인덱스 생성
CREATE INDEX idx_orders_covering ON orders (user_id)
INCLUDE (order_date, amount);

-- 아래 쿼리는 테이블 접근 없이 인덱스만으로 처리 가능
SELECT order_date, amount FROM orders WHERE user_id = 1;
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. B-Tree 구조

대부분의 RDBMS 기본 인덱스 구조.

```
                    ┌─────────────────┐
                    │   Root Node     │
                    │   [50 | 100]    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          v                  v                  v
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ Branch Node │   │ Branch Node │   │ Branch Node │
   │  [20 | 35]  │   │  [65 | 80]  │   │ [110 | 130] │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                 │                 │
    ┌─────┴─────┐     ┌─────┴─────┐     ┌─────┴─────┐
    v     v     v     v     v     v     v     v     v
  [10]  [25]  [40]  [55]  [70]  [90] [105] [120] [140]
  Leaf  Leaf  Leaf  Leaf  Leaf  Leaf  Leaf  Leaf  Leaf
    │─────────────────────────────────────────────────>
                  (Leaf nodes linked list)
```

- Leaf Node: 실제 인덱스 키 + 행 위치(ROWID/PK) 저장
- Leaf Node는 연결 리스트로 연결 → 범위 검색에 효율적
- 검색 복잡도: O(log n)

### Clustered vs Non-Clustered

```
Clustered Index (InnoDB Primary Key)
┌──────────────────────────────────────┐
│ Leaf Node = Actual Data Row          │
│ [PK=1 | name='Alice' | email='...']  │
│ [PK=2 | name='Bob'   | email='...']  │
└──────────────────────────────────────┘

Non-Clustered Index (Secondary Index)
┌──────────────────────────────────────┐
│ Leaf Node = Index Key + PK Value     │
│ [email='alice@...' | PK=1]           │
│ [email='bob@...'   | PK=2]           │
└──────────────────────────────────────┘
         │
         └─> Double Lookup via PK on Clustered Index
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실행 계획 분석

### MySQL EXPLAIN

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 1 AND created_at >= '2026-01-01';
```

```
+----+-------------+--------+------+------------------+------------------+---------+-------+------+-------------+
| id | select_type | table  | type | possible_keys    | key              | key_len | ref   | rows | Extra       |
+----+-------------+--------+------+------------------+------------------+---------+-------+------+-------------+
|  1 | SIMPLE      | orders | ref  | idx_user_date    | idx_user_date    | 4       | const |  150 | Using index |
+----+-------------+--------+------+------------------+------------------+---------+-------+------+-------------+
```

### type 컬럼 해석 (성능 순서)

| type     | 설명                                 | 성능  |
|----------|--------------------------------------|-------|
| `system` | 테이블에 행이 1개                    | ★★★★★ |
| `const`  | PK/Unique로 1행 조회                 | ★★★★★ |
| `eq_ref` | JOIN에서 PK/Unique 사용              | ★★★★☆ |
| `ref`    | Non-Unique 인덱스로 조회             | ★★★☆☆ |
| `range`  | 인덱스 범위 스캔 (BETWEEN, >, <, IN) | ★★★☆☆ |
| `index`  | 인덱스 Full Scan                     | ★★☆☆☆ |
| `ALL`    | Full Table Scan (인덱스 미사용)      | ★☆☆☆☆ |

### PostgreSQL EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 1;
```

```
Index Scan using idx_orders_user on orders  (cost=0.43..8.45 rows=5 width=64)
                                            (actual time=0.023..0.031 rows=5 loops=1)
  Index Cond: (user_id = 1)
Planning Time: 0.1 ms
Execution Time: 0.05 ms
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 복합 인덱스 설계

### 선두 컬럼 원칙 (Leftmost Prefix Rule)

복합 인덱스 `(A, B, C)`는 아래 조건에서만 사용됩니다.

| WHERE 조건                  | 인덱스 사용 여부 | 사용 컬럼 |
|-----------------------------|------------------|-----------|
| `A = ?`                     | ✅               | A         |
| `A = ? AND B = ?`           | ✅               | A, B      |
| `A = ? AND B = ? AND C = ?` | ✅               | A, B, C   |
| `B = ?`                     | ❌               | -         |
| `B = ? AND C = ?`           | ❌               | -         |
| `A = ? AND C = ?`           | ✅ (부분)        | A만 사용  |

### 컬럼 순서 결정 원칙

1. **등치(=) 조건 컬럼을 앞에** 배치.
2. **카디널리티 높은 컬럼을 앞에** 배치 (선택도 향상).
3. **범위 조건 컬럼은 뒤에** 배치 (범위 이후 컬럼은 인덱스 미사용).

```sql
-- 나쁜 예: 범위 조건이 앞에 있어 status 인덱스 미사용
CREATE INDEX idx_bad ON orders (created_at, status);
SELECT * FROM orders WHERE created_at >= '2026-01-01' AND status = 'pending';

-- 좋은 예: 등치 조건 먼저
CREATE INDEX idx_good ON orders (status, created_at);
SELECT * FROM orders WHERE status = 'pending' AND created_at >= '2026-01-01';
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Index 최적화 팁

### Tip 1: 인덱스를 무력화하는 패턴

```sql
-- 컬럼에 함수 적용 → 인덱스 미사용
SELECT * FROM users WHERE YEAR(created_at) = 2026;
-- 개선: 범위 조건으로 변환
SELECT * FROM users WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';

-- 묵시적 형변환 → 인덱스 미사용
SELECT * FROM users WHERE user_id = '123';  -- user_id가 INT인 경우
-- 개선: 타입 일치
SELECT * FROM users WHERE user_id = 123;

-- LIKE 앞 와일드카드 → 인덱스 미사용
SELECT * FROM users WHERE username LIKE '%alice%';
-- 개선: Full-Text Index 사용 또는 앞 와일드카드 제거
SELECT * FROM users WHERE username LIKE 'alice%';
```

### Tip 2: Covering Index로 Double Lookup 제거

```sql
-- Non-Clustered Index 조회 후 PK로 재탐색 발생
CREATE INDEX idx_user_id ON orders (user_id);
SELECT user_id, order_date, amount FROM orders WHERE user_id = 1;
-- Extra: Using index condition (테이블 재탐색 발생)

-- Covering Index: 필요한 컬럼을 모두 포함
CREATE INDEX idx_user_covering ON orders (user_id, order_date, amount);
-- Extra: Using index (테이블 재탐색 없음)
```

### Tip 3: 인덱스 선택도 (Selectivity) 확인

```sql
-- 선택도 = 고유값 수 / 전체 행 수 (1에 가까울수록 효과적)
SELECT
    COUNT(DISTINCT status) / COUNT(*) AS status_selectivity,
    COUNT(DISTINCT email)  / COUNT(*) AS email_selectivity
FROM users;
-- status: 0.0001 (낮음, 인덱스 효과 낮음)
-- email:  1.0000 (높음, 인덱스 효과 높음)
```

### Tip 4: 불필요한 인덱스 제거

인덱스가 많을수록 INSERT/UPDATE/DELETE 성능이 저하됩니다.

```sql
-- MySQL: 사용되지 않는 인덱스 확인
SELECT * FROM sys.schema_unused_indexes
WHERE object_schema = 'mydb';

-- PostgreSQL: 사용되지 않는 인덱스 확인
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Tip 5: 인덱스 힌트 (강제 지정)

옵티마이저가 잘못된 인덱스를 선택할 때 사용.

```sql
-- MySQL: 인덱스 강제 사용
SELECT * FROM orders USE INDEX (idx_user_date)
WHERE user_id = 1 AND created_at >= '2026-01-01';

-- MySQL: 인덱스 제외
SELECT * FROM orders IGNORE INDEX (idx_status)
WHERE status = 'pending';

-- PostgreSQL: 인덱스 스캔 비활성화 (테스트용)
SET enable_indexscan = off;
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. Index 관리

### 인덱스 단편화 (Fragmentation)

INSERT/UPDATE/DELETE가 반복되면 인덱스 페이지가 단편화되어 성능이 저하됩니다.

```sql
-- MySQL: 인덱스 재구성
ALTER TABLE orders ENGINE=InnoDB;  -- 테이블 재구성 (잠금 발생)
OPTIMIZE TABLE orders;             -- 단편화 해소

-- MySQL 8.0+: 온라인 인덱스 재구성
ALTER TABLE orders ALGORITHM=INPLACE, LOCK=NONE,
    DROP INDEX idx_old,
    ADD INDEX idx_new (user_id, created_at);

-- PostgreSQL: 인덱스 재구성
REINDEX INDEX idx_orders_user;
REINDEX TABLE orders;

-- PostgreSQL 12+: 잠금 없이 재구성
REINDEX INDEX CONCURRENTLY idx_orders_user;
```

### 인덱스 통계 갱신

옵티마이저는 통계 정보를 기반으로 실행 계획을 수립합니다.
대량 데이터 변경 후 통계를 갱신해야 정확한 실행 계획이 생성됩니다.

```sql
-- MySQL
ANALYZE TABLE orders;

-- PostgreSQL
ANALYZE orders;
VACUUM ANALYZE orders;  -- 불필요한 행 정리 + 통계 갱신
```

### 인덱스 현황 조회

```sql
-- MySQL: 테이블 인덱스 목록
SHOW INDEX FROM orders;

-- MySQL: 인덱스 크기 확인
SELECT
    index_name,
    ROUND(stat_value * @@innodb_page_size / 1024 / 1024, 2) AS size_mb
FROM mysql.innodb_index_stats
WHERE table_name = 'orders' AND stat_name = 'size';

-- PostgreSQL: 인덱스 크기 및 사용 통계
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 'orders'
ORDER BY pg_relation_size(indexrelid) DESC;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [Optimization and Indexes](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html) — ★★★☆☆
- PostgreSQL Documentation: [Indexes](https://www.postgresql.org/docs/current/indexes.html) — ★★★☆☆
- Use The Index, Luke: [use-the-index-luke.com](https://use-the-index-luke.com/) — ★★☆☆☆

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
