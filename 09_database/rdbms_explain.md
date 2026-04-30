# RDBMS 실행 계획 분석 (EXPLAIN)

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 실행 계획 개념](#1-실행-계획-개념) / [2. MySQL EXPLAIN](#2-mysql-explain)                                                                                      |
| 분석 | [3. PostgreSQL EXPLAIN](#3-postgresql-explain) / [4. 슬로우 쿼리 탐지](#4-슬로우-쿼리-탐지)                                                                        |
| 고급 | [5. 튜닝 패턴](#5-튜닝-패턴) / [6. 실전 체크리스트](#6-실전-체크리스트) |

---

## 1. 실행 계획 개념

옵티마이저가 쿼리를 어떻게 실행할지 결정한 계획.
인덱스 사용 여부, JOIN 순서, 스캔 방식 등을 확인할 수 있다.

```
쿼리 → 파서 → 옵티마이저 → 실행 계획 → 실행 엔진 → 결과
                    ↑
              통계 정보 (행 수, 카디널리티, 히스토그램)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. MySQL EXPLAIN

```sql
EXPLAIN SELECT u.username, COUNT(o.order_id) AS order_count
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.status = 'active'
GROUP BY u.user_id;
```

### 출력 컬럼 설명

| 컬럼 | 설명 |
|------|------|
| `id` | 쿼리 단계 번호 (높을수록 먼저 실행) |
| `select_type` | SIMPLE, PRIMARY, SUBQUERY, DERIVED 등 |
| `table` | 접근 테이블 |
| `type` | 접근 방식 (아래 참조) |
| `possible_keys` | 사용 가능한 인덱스 목록 |
| `key` | 실제 사용된 인덱스 |
| `key_len` | 사용된 인덱스 바이트 수 |
| `rows` | 예상 스캔 행 수 |
| `filtered` | 조건 필터링 후 남는 행 비율 (%) |
| `Extra` | 추가 정보 |

### type 컬럼 (성능 순)

| type | 설명 | 성능 |
|------|------|------|
| `system` | 1행짜리 테이블 | ★★★★★ |
| `const` | PK/Unique 상수 조회 | ★★★★★ |
| `eq_ref` | JOIN에서 PK/Unique 사용 | ★★★★☆ |
| `ref` | Non-Unique 인덱스 조회 | ★★★☆☆ |
| `range` | 인덱스 범위 스캔 | ★★★☆☆ |
| `index` | 인덱스 Full Scan | ★★☆☆☆ |
| `ALL` | Full Table Scan | ★☆☆☆☆ |

### Extra 주요 값

| Extra | 의미 | 조치 |
|-------|------|------|
| `Using index` | 커버링 인덱스 (테이블 미접근) | ✅ 최적 |
| `Using where` | WHERE 필터링 | 일반적 |
| `Using filesort` | 정렬을 위한 추가 작업 | ⚠️ 인덱스 정렬 검토 |
| `Using temporary` | 임시 테이블 사용 | ⚠️ 쿼리 최적화 필요 |
| `Using index condition` | ICP (Index Condition Pushdown) | ✅ 양호 |

### EXPLAIN FORMAT=JSON (상세 분석)

```sql
EXPLAIN FORMAT=JSON
SELECT * FROM orders WHERE user_id = 1 AND status = 'pending';
```

```json
{
  "query_block": {
    "select_id": 1,
    "cost_info": { "query_cost": "1.20" },
    "table": {
      "access_type": "ref",
      "key": "idx_user_status",
      "rows_examined_per_scan": 3,
      "filtered": "100.00"
    }
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. PostgreSQL EXPLAIN

```sql
-- 예상 비용만
EXPLAIN SELECT * FROM orders WHERE user_id = 1;

-- 실제 실행 시간 포함
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1;

-- 버퍼 사용량 포함
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE user_id = 1;
```

### 출력 해석

```
Index Scan using idx_orders_user on orders
  (cost=0.43..8.45 rows=5 width=64)
  (actual time=0.023..0.031 rows=5 loops=1)
  Index Cond: (user_id = 1)
  Buffers: shared hit=3
Planning Time: 0.1 ms
Execution Time: 0.05 ms
```

| 항목 | 설명 |
|------|------|
| `cost=0.43..8.45` | 시작 비용..총 비용 (상대값) |
| `rows=5` | 예상 행 수 |
| `actual time=0.023..0.031` | 실제 첫 행..마지막 행 시간 (ms) |
| `loops=1` | 반복 횟수 (Nested Loop에서 중요) |
| `shared hit=3` | 버퍼 캐시 히트 수 |
| `shared read=10` | 디스크 읽기 수 |

### 노드 종류

| 노드 | 설명 |
|------|------|
| `Seq Scan` | Full Table Scan |
| `Index Scan` | 인덱스 + 테이블 접근 |
| `Index Only Scan` | 인덱스만 접근 (커버링) |
| `Bitmap Index Scan` | 비트맵 인덱스 스캔 |
| `Hash Join` | 해시 조인 |
| `Nested Loop` | 중첩 루프 조인 |
| `Merge Join` | 정렬 병합 조인 |
| `Sort` | 정렬 |
| `Aggregate` | 집계 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 슬로우 쿼리 탐지

### MySQL 슬로우 쿼리 로그

```bash
# my.cnf 설정
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 1        # 1초 이상
log_queries_not_using_indexes = 1

# 런타임 설정
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 0.5;
```

```bash
# mysqldumpslow로 분석
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log
# -s t: 실행 시간 기준 정렬
# -t 10: 상위 10개
```

### PostgreSQL 슬로우 쿼리

```bash
# postgresql.conf
log_min_duration_statement = 1000   # 1000ms 이상
log_statement = 'none'
```

```sql
-- pg_stat_statements 확장 (상위 슬로우 쿼리)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Performance Schema (MySQL)

```sql
-- 슬로우 쿼리 상위 10개
SELECT digest_text, count_star, avg_timer_wait/1e9 AS avg_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY avg_timer_wait DESC
LIMIT 10;
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 튜닝 패턴

### 패턴 1: Full Table Scan → Index Scan

```sql
-- Before: type=ALL
EXPLAIN SELECT * FROM orders WHERE status = 'pending';

-- 인덱스 추가
CREATE INDEX idx_orders_status ON orders (status);

-- After: type=ref
```

### 패턴 2: Using filesort 제거

```sql
-- Before: Using filesort
SELECT * FROM orders WHERE user_id = 1 ORDER BY created_at DESC;

-- 복합 인덱스로 정렬 제거
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at DESC);

-- After: Using index
```

### 패턴 3: Using temporary 제거

```sql
-- Before: Using temporary; Using filesort
SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY COUNT(*) DESC;

-- 인덱스 추가
CREATE INDEX idx_orders_status ON orders (status);
```

### 패턴 4: 서브쿼리 → JOIN

```sql
-- Before: DEPENDENT SUBQUERY (행마다 실행)
SELECT * FROM users
WHERE user_id IN (SELECT user_id FROM orders WHERE amount > 10000);

-- After: JOIN (한 번 실행)
SELECT DISTINCT u.*
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.amount > 10000;
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실전 체크리스트

```sql
-- 1. 실행 계획 확인
EXPLAIN SELECT ...;

-- 2. type=ALL 확인 → 인덱스 추가 검토
-- 3. rows 값 확인 → 예상보다 많으면 인덱스/조건 검토
-- 4. Extra 확인
--    Using filesort → ORDER BY 컬럼 인덱스 추가
--    Using temporary → GROUP BY/DISTINCT 최적화
--    Using index → 커버링 인덱스 (최적)

-- 5. 통계 갱신 (실행 계획이 이상할 때)
ANALYZE TABLE orders;          -- MySQL
VACUUM ANALYZE orders;         -- PostgreSQL
```

| 체크 항목 | 기준 | 조치 |
|-----------|------|------|
| `type` | `ALL` 또는 `index` | 인덱스 추가 |
| `rows` | 전체 행의 20% 이상 | 조건/인덱스 검토 |
| `Extra` | `Using filesort` | ORDER BY 인덱스 |
| `Extra` | `Using temporary` | 쿼리 재작성 |
| `filtered` | 10% 미만 | 선택도 높은 인덱스 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [EXPLAIN Statement](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
- PostgreSQL Documentation: [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)
- Use The Index, Luke: [Execution Plans](https://use-the-index-luke.com/sql/explain-plan)

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
