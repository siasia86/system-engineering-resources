# RDBMS 파티셔닝 (Partitioning)

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 파티셔닝 개념](#1-파티셔닝-개념) / [2. 파티션 종류](#2-파티션-종류)                                                                                            |
| 활용 | [3. MySQL 파티셔닝](#3-mysql-파티셔닝) / [4. PostgreSQL 파티셔닝](#4-postgresql-파티셔닝)                                                                          |
| 고급 | [5. 파티션 프루닝](#5-파티션-프루닝) / [6. 파티션 관리](#6-파티션-관리) / [7. 실무 팁](#7-실무-팁) |

---

## 1. 파티셔닝 개념

하나의 큰 테이블을 물리적으로 여러 조각(파티션)으로 나누는 기법.
논리적으로는 하나의 테이블처럼 보이지만 내부적으로 분리 저장된다.

### 장점과 단점

| 항목 | 장점 | 단점 |
|------|------|------|
| 쿼리 성능 | 파티션 프루닝으로 스캔 범위 축소 | 파티션 키 미포함 쿼리는 전체 스캔 |
| 관리 | 파티션 단위 삭제/아카이브 빠름 | 설계 복잡도 증가 |
| 인덱스 | 파티션별 로컬 인덱스 | 글로벌 유니크 인덱스 제한 |
| 병렬 처리 | 파티션별 병렬 스캔 가능 | 파티션 간 JOIN 비용 |

### 파티셔닝 vs 샤딩

| 항목 | 파티셔닝 | 샤딩 |
|------|----------|------|
| 위치 | 단일 서버 내 | 여러 서버 분산 |
| 투명성 | 애플리케이션 투명 | 라우팅 로직 필요 |
| 확장성 | 수직 확장 | 수평 확장 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 파티션 종류

### Range 파티셔닝

연속된 범위 기준으로 분할. 날짜/시간 데이터에 가장 많이 사용.

```
created_at < 2025-01-01  → p2024
created_at < 2026-01-01  → p2025
created_at < 2027-01-01  → p2026
```

### List 파티셔닝

특정 값 목록 기준으로 분할. 지역, 상태 코드 등에 사용.

```
region IN ('KR', 'JP')  → p_asia
region IN ('US', 'CA')  → p_america
region IN ('DE', 'FR')  → p_europe
```

### Hash 파티셔닝

해시 함수 결과로 균등 분할. 특정 컬럼 기준이 없을 때 사용.

```
HASH(user_id) % 4
→ p0, p1, p2, p3 (균등 분산)
```

### Key 파티셔닝

MySQL 내부 해시 함수 사용. PK/Unique 컬럼에 적합.

```
KEY(user_id) PARTITIONS 4
```

### Composite 파티셔닝 (서브파티셔닝)

Range + Hash 등 두 가지 방식 결합.

```
Range(year) → Hash(user_id)
p2025 → p2025_h0, p2025_h1, p2025_h2, p2025_h3
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. MySQL 파티셔닝

### Range 파티셔닝

```sql
CREATE TABLE orders (
    order_id    INT NOT NULL,
    user_id     INT NOT NULL,
    amount      DECIMAL(10,2),
    created_at  DATE NOT NULL
)
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### List 파티셔닝

```sql
CREATE TABLE users (
    user_id INT NOT NULL,
    region  VARCHAR(10) NOT NULL,
    name    VARCHAR(100)
)
PARTITION BY LIST COLUMNS (region) (
    PARTITION p_asia    VALUES IN ('KR', 'JP', 'CN'),
    PARTITION p_america VALUES IN ('US', 'CA', 'MX'),
    PARTITION p_europe  VALUES IN ('DE', 'FR', 'GB')
);
```

### Hash 파티셔닝

```sql
CREATE TABLE logs (
    log_id  BIGINT NOT NULL,
    user_id INT NOT NULL,
    message TEXT
)
PARTITION BY HASH (user_id)
PARTITIONS 8;
```

### 파티션 확인

```sql
SELECT partition_name, table_rows, data_length
FROM information_schema.partitions
WHERE table_name = 'orders' AND table_schema = 'mydb';
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. PostgreSQL 파티셔닝

PostgreSQL 10+에서 선언적 파티셔닝 지원.

### Range 파티셔닝

```sql
-- 부모 테이블
CREATE TABLE orders (
    order_id   BIGINT NOT NULL,
    user_id    INT NOT NULL,
    amount     NUMERIC(10,2),
    created_at DATE NOT NULL
) PARTITION BY RANGE (created_at);

-- 파티션 테이블
CREATE TABLE orders_2024
    PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025
    PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE orders_2026
    PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

### List 파티셔닝

```sql
CREATE TABLE users (
    user_id INT NOT NULL,
    region  VARCHAR(10) NOT NULL,
    name    VARCHAR(100)
) PARTITION BY LIST (region);

CREATE TABLE users_asia    PARTITION OF users FOR VALUES IN ('KR', 'JP', 'CN');
CREATE TABLE users_america PARTITION OF users FOR VALUES IN ('US', 'CA', 'MX');
```

### 파티션 인덱스

```sql
-- 각 파티션에 자동 적용되는 인덱스
CREATE INDEX ON orders (user_id);
CREATE INDEX ON orders (created_at);
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 파티션 프루닝

쿼리 조건에 맞는 파티션만 스캔하는 최적화.

```sql
-- 파티션 프루닝 동작 확인 (MySQL)
EXPLAIN SELECT * FROM orders WHERE created_at >= '2026-01-01';
-- partitions 컬럼에 p2026만 표시되면 프루닝 성공

-- 파티션 프루닝 동작 확인 (PostgreSQL)
EXPLAIN SELECT * FROM orders WHERE created_at >= '2026-01-01';
-- orders_2026만 스캔
```

### 프루닝이 동작하지 않는 경우

```sql
-- 나쁜 예: 파티션 키에 함수 적용
SELECT * FROM orders WHERE YEAR(created_at) = 2026;
-- → 전체 파티션 스캔

-- 좋은 예: 범위 조건 사용
SELECT * FROM orders
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';
-- → p2026만 스캔
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 파티션 관리

### 파티션 추가

```sql
-- MySQL
ALTER TABLE orders ADD PARTITION (
    PARTITION p2027 VALUES LESS THAN (2028)
);

-- PostgreSQL
CREATE TABLE orders_2027
    PARTITION OF orders
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
```

### 파티션 삭제 (빠른 대용량 삭제)

```sql
-- MySQL: 파티션 전체 삭제 (DELETE보다 수백 배 빠름)
ALTER TABLE orders DROP PARTITION p2023;

-- PostgreSQL: 파티션 테이블 삭제
DROP TABLE orders_2023;
-- 또는 분리 후 삭제
ALTER TABLE orders DETACH PARTITION orders_2023;
DROP TABLE orders_2023;
```

### 파티션 분할/병합

```sql
-- MySQL: 파티션 분할
ALTER TABLE orders REORGANIZE PARTITION p_future INTO (
    PARTITION p2027 VALUES LESS THAN (2028),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- MySQL: 파티션 병합
ALTER TABLE orders REORGANIZE PARTITION p2023, p2024 INTO (
    PARTITION p2023_2024 VALUES LESS THAN (2025)
);
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: 날짜 기반 파티셔닝 자동화

```sql
-- 매월 새 파티션 추가 (이벤트 스케줄러)
CREATE EVENT add_monthly_partition
ON SCHEDULE EVERY 1 MONTH
STARTS '2026-12-01 00:00:00'
DO
    ALTER TABLE logs ADD PARTITION (
        PARTITION p_next VALUES LESS THAN (UNIX_TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 2 MONTH)))
    );
```

### Tip 2: 파티션 키 선택 기준

| 기준 | 권장 파티션 키 |
|------|---------------|
| 시계열 데이터 | `created_at` (Range) |
| 지역별 분리 | `region` (List) |
| 균등 분산 | `user_id` (Hash) |
| 복합 조건 | Range + Hash (Composite) |

### Tip 3: 파티션과 인덱스

```sql
-- MySQL: 파티션 테이블의 유니크 인덱스는 파티션 키 포함 필수
CREATE UNIQUE INDEX idx_order_unique
ON orders (order_id, created_at);  -- created_at(파티션 키) 포함

-- 파티션 키 미포함 시 오류
-- ERROR 1503: A UNIQUE INDEX must include all columns in the table's partitioning function
```

### Tip 4: 파티셔닝 적합 기준

파티셔닝은 테이블이 충분히 클 때 효과적이다.

| 기준 | 설명 |
|------|------|
| 테이블 크기 | 수억 건 이상 또는 수백 GB |
| 쿼리 패턴 | 특정 범위/값 조건이 자주 사용 |
| 관리 필요성 | 오래된 데이터 주기적 삭제 |
| 소규모 테이블 | 파티셔닝 오버헤드가 더 클 수 있음 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [Partitioning](https://dev.mysql.com/doc/refman/8.0/en/partitioning.html) — ★★★☆☆
- PostgreSQL Documentation: [Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) — ★★★☆☆
- MySQL Documentation: [Partition Pruning](https://dev.mysql.com/doc/refman/8.0/en/partitioning-pruning.html) — ★★★☆☆

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
