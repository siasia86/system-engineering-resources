# RDBMS Index (인덱스)

## 목차

| 단계 | 섹션                                                                                                                   |
|------|------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. Index 개념](#1-index-개념) / [2. Index 종류](#2-index-종류) / [3. Index 생성과 삭제](#3-index-생성과-삭제)         |
| 원리 | [4. B-Tree / B+Tree 구조](#4-b-tree--b+tree-구조) / [5. 실행 계획 분석](#5-실행-계획-분석)                             |
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

### 인덱스 갱신은 자동으로 발생합니다

DML(INSERT/UPDATE/DELETE) 실행 시 RDBMS 엔진이 해당 테이블의 **모든 인덱스를 자동으로 갱신**합니다. 별도 명령이 필요 없습니다.

```sql
-- 인덱스 3개 있는 테이블
CREATE INDEX idx_email ON users (email);
CREATE INDEX idx_name ON users (name);
CREATE INDEX idx_created ON users (created_at);

-- INSERT 1건 실행 → 내부적으로 4번 쓰기 자동 발생
INSERT INTO users (id, email, name, created_at)
VALUES (1001, 'new@example.com', 'Alice', '2026-06-30');
-- 1. Clustered Index (PK)에 행 삽입         ← 자동
-- 2. idx_email B+Tree에 엔트리 삽입         ← 자동
-- 3. idx_name B+Tree에 엔트리 삽입          ← 자동
-- 4. idx_created B+Tree에 엔트리 삽입       ← 자동
```

UPDATE는 인덱스된 컬럼 변경 시 DELETE + INSERT(2배 비용), DELETE는 모든 인덱스에서 엔트리 제거가 발생합니다. 인덱스를 많이 만들수록 쓰기가 느려지므로 불필요한 인덱스를 정리해야 합니다.

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

### Hash Index 상세

```sql
-- MySQL (MEMORY 엔진 전용)
CREATE TABLE sessions (
    session_id VARCHAR(64),
    INDEX USING HASH (session_id)
) ENGINE=MEMORY;

-- PostgreSQL (모든 테이블)
CREATE INDEX idx_sessions_hash ON sessions USING hash (session_id);
```

내부 구조: 해시 함수로 키 값을 버킷 번호로 변환하여 해당 버킷에서 직접 꺼냅니다.

| 항목                 | B-Tree   | Hash                |
|----------------------|----------|---------------------|
| 등치 검색 (`=`)      | O(log n) | **O(1)**            |
| 범위 검색 (`>`, `<`) | ✅ 가능  | ❌ 불가             |
| 정렬 (`ORDER BY`)    | ✅ 가능  | ❌ 불가             |
| `LIKE 'abc%'`        | ✅ 가능  | ❌ 불가             |
| 디스크 저장          | ✅ 지원  | ❌ MEMORY만 (MySQL) |

실무에서 Hash를 거의 안 쓰는 이유:

- MySQL: InnoDB 미지원, MEMORY 엔진 전용 (서버 재시작 시 데이터 소멸)
- B-Tree로 충분: 등치 검색도 O(log n)으로 충분히 빠릅니다 (100만 행 ≈ 20회 비교)
- 대부분의 쿼리는 범위/정렬을 함께 사용합니다

세션 키, 캐시 키 같은 순수 등치 검색 전용이 아니면 B-Tree가 범용적입니다.

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

### CREATE INDEX 상세 분석

```sql
CREATE INDEX idx_users_email ON users (email);
```

| 구성 요소         | 값             | 설명                               |
|-------------------|----------------|------------------------------------|
| `CREATE INDEX`    | DDL 명령       | 인덱스 생성                        |
| `idx_users_email` | 인덱스 이름    | 네이밍: `idx_` + 테이블명 + 컬럼명 |
| `ON users`        | 대상 테이블    | `users` 테이블에 생성              |
| `(email)`         | 인덱스 키 컬럼 | `email` 컬럼 값으로 B+Tree 구성    |

실행 시 내부 동작:

1. `users` 테이블의 모든 행에서 `email` 값을 읽습니다
2. `email` 값을 정렬하여 B+Tree 구조로 구성합니다
3. 각 Leaf Node에 (email 값, PK값) 쌍을 저장합니다
4. 시스템 카탈로그에 인덱스 메타데이터를 등록합니다

생성 시 주의사항:

| 항목      | 내용                                                                              |
|-----------|-----------------------------------------------------------------------------------|
| 잠금      | MySQL 기본: 읽기 허용, 쓰기 차단 (`ALGORITHM=INPLACE, LOCK=NONE`으로 온라인 가능) |
| 시간      | 데이터 양에 비례 (100만 행 ≈ 수 초, 1억 행 ≈ 수 분)                               |
| 공간      | email 평균 30바이트 × 100만 행 ≈ 인덱스 ~50MB 추가                                |
| 중복 허용 | `CREATE INDEX`는 중복값 허용. 유니크 강제는 `CREATE UNIQUE INDEX`                 |

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

## 4. B-Tree / B+Tree 구조

대부분의 RDBMS 기본 인덱스 구조입니다. 공식 문서에서 "B-Tree"라고 부르지만 **내부 구현은 B+Tree**입니다.

### B-Tree vs B+Tree

| 항목             | B-Tree                         | B+Tree                                   |
|------------------|--------------------------------|------------------------------------------|
| 데이터 저장 위치 | 모든 노드 (Root, Branch, Leaf) | **Leaf 노드에만**                        |
| Internal 노드    | 키 + 데이터 + 자식 포인터      | **키 + 자식 포인터만** (가이드 역할)     |
| Leaf 연결        | 없음                           | **Linked List로 연결**                   |
| 범위 검색        | 트리 재탐색 필요               | Leaf에서 순차 이동 (빠름)                |
| Fan-out (분기도) | 낮음 (노드에 데이터 포함)      | **높음** (키만 → 한 페이지에 더 많은 키) |
| 디스크 I/O       | 많음                           | **적음** (트리 높이 낮음)                |

MySQL `SHOW INDEX`에서는 `BTREE`, PostgreSQL에서는 `btree`로 표시되지만 모두 B+Tree(PostgreSQL은 Lehman-Yao 변형)입니다.

### B+Tree가 RDBMS에 적합한 이유

**1. Fan-out이 높아 트리가 낮습니다**

Internal 노드에 데이터가 없으므로 한 페이지(16KB)에 키를 더 많이 저장합니다.

| 항목                   | 값                                                 |
|------------------------|----------------------------------------------------|
| InnoDB 페이지 크기     | 16KB                                               |
| BIGINT 키 기준 Fan-out | ~1200 (데이터 없이 키+포인터만)                    |
| 1억 행 기준 트리 높이  | 3~4 (디스크 I/O 3~4회로 탐색 완료)                 |
| Full Scan 대비         | 100만 행: ~20회 비교 vs 100만 회 비교 (5만배 차이) |

**2. 범위 검색이 빠릅니다**

시작 Leaf를 찾은 후 Linked List로 순차 이동합니다 (Sequential I/O).

**3. Full Scan도 효율적입니다**

Leaf 레벨만 왼쪽→오른쪽 순회하면 정렬 결과를 얻습니다.

### B+Tree 구조 다이어그램

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
| id | select_type | table | type | possible_keys | key | key_len | ref | rows | Extra |
+----+-------------+--------+------+------------------+------------------+---------+-------+------+-------------+
| 1 | SIMPLE | orders | ref | idx_user_date | idx_user_date | 4 | const | 150 | Using index |
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
