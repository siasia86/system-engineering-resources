# RDBMS View (뷰)

## 목차

| 단계 | 섹션                                                                                                                                                 |
|------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. View 개념](#1-view-개념) / [2. View 생성과 삭제](#2-view-생성과-삭제)                                                                            |
| 활용 | [3. View 종류](#3-view-종류) / [4. View를 통한 DML](#4-view를-통한-dml)                                                                              |
| 고급 | [5. Materialized View](#5-materialized-view) / [6. View 최적화 팁](#6-view-최적화-팁) / [7. 실전 패턴](#7-실전-패턴) |

---

## 1. View 개념

View는 하나 이상의 테이블에서 파생된 **가상 테이블(Virtual Table)**이다.
실제 데이터를 저장하지 않고, 정의된 SELECT 쿼리를 실행한 결과를 테이블처럼 사용한다.

### 특징

| 항목       | 설명                                              |
|------------|---------------------------------------------------|
| 저장 방식  | 쿼리 정의만 저장 (데이터 미저장)                  |
| 갱신       | 기반 테이블 변경 시 View 결과도 자동 반영         |
| 보안       | 특정 컬럼/행만 노출하여 접근 제어 가능            |
| 재사용     | 복잡한 쿼리를 단순화하여 반복 사용                |

### View가 필요한 상황

- 복잡한 JOIN 쿼리를 단순화할 때
- 민감한 컬럼(주민번호, 급여 등)을 숨길 때
- 여러 애플리케이션에서 동일한 쿼리 로직을 공유할 때

[⬆ 목차로 돌아가기](#목차)

---

## 2. View 생성과 삭제

### 기본 문법

```sql
-- 생성
CREATE VIEW view_name AS
SELECT column1, column2
FROM table_name
WHERE condition;

-- 수정 (재정의)
CREATE OR REPLACE VIEW view_name AS
SELECT ...;

-- 삭제
DROP VIEW view_name;
```

### 예시: 활성 사용자 View

```sql
CREATE VIEW active_users AS
SELECT user_id, username, email, created_at
FROM users
WHERE status = 'active'
  AND deleted_at IS NULL;

-- 사용
SELECT * FROM active_users WHERE created_at >= '2026-01-01';
```

### 예시: 민감 정보 마스킹 View

```sql
CREATE VIEW users_public AS
SELECT
    user_id,
    username,
    CONCAT(LEFT(email, 3), '***@', SUBSTRING_INDEX(email, '@', -1)) AS email_masked,
    created_at
FROM users;
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. View 종류

### Simple View vs Complex View

| 구분              | Simple View                    | Complex View                          |
|-------------------|--------------------------------|---------------------------------------|
| 기반 테이블 수    | 1개                            | 2개 이상 (JOIN 포함)                  |
| 집계 함수         | 없음                           | GROUP BY, HAVING 포함 가능            |
| DML 가능 여부     | INSERT/UPDATE/DELETE 가능      | 제한적 (DBMS마다 다름)                |
| 예시              | `SELECT col FROM table`        | `SELECT ... FROM a JOIN b GROUP BY c` |

### WITH CHECK OPTION

View를 통한 DML 시 View 조건을 벗어나는 데이터 변경을 차단한다.

```sql
CREATE VIEW active_users AS
SELECT * FROM users WHERE status = 'active'
WITH CHECK OPTION;

-- 아래 UPDATE는 실패 (status = 'inactive'로 변경 시 View 조건 위반)
UPDATE active_users SET status = 'inactive' WHERE user_id = 1;
-- ERROR: CHECK OPTION failed
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. View를 통한 DML

### DML 가능 조건 (Simple View 기준)

| 조건                          | INSERT | UPDATE | DELETE |
|-------------------------------|--------|--------|--------|
| 단일 테이블 기반              | ✅     | ✅     | ✅     |
| DISTINCT 없음                 | ✅     | ✅     | ✅     |
| 집계 함수 없음                | ✅     | ✅     | ✅     |
| GROUP BY / HAVING 없음        | ✅     | ✅     | ✅     |
| UNION 없음                    | ✅     | ✅     | ✅     |
| NOT NULL 컬럼 모두 포함       | ✅     | -      | -      |

### INSTEAD OF Trigger (Complex View DML 우회)

Oracle, PostgreSQL에서 Complex View에 DML을 허용하는 방법.

```sql
-- PostgreSQL 예시
CREATE RULE view_insert AS ON INSERT TO order_summary_view
DO INSTEAD
INSERT INTO orders (user_id, product_id, amount)
VALUES (NEW.user_id, NEW.product_id, NEW.amount);
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Materialized View

일반 View와 달리 **쿼리 결과를 실제 디스크에 저장**한다.
조회 성능이 중요하고 데이터 실시간성이 덜 중요한 경우에 사용한다.

### 일반 View vs Materialized View

| 구분          | View                    | Materialized View              |
|---------------|-------------------------|--------------------------------|
| 데이터 저장   | 미저장 (쿼리만 저장)    | 저장 (스냅샷)                  |
| 조회 속도     | 기반 쿼리 실행 속도     | 빠름 (저장된 데이터 직접 조회) |
| 데이터 최신성 | 항상 최신               | 갱신 주기에 따라 지연 가능     |
| 인덱스 생성   | 불가                    | 가능                           |
| 사용 목적     | 쿼리 단순화, 보안       | 집계 성능 최적화, 리포팅       |

### PostgreSQL 예시

```sql
-- 생성
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT
    DATE_TRUNC('month', order_date) AS month,
    product_id,
    SUM(amount)                     AS total_sales,
    COUNT(*)                        AS order_count
FROM orders
GROUP BY 1, 2;

-- 인덱스 생성 가능
CREATE INDEX ON monthly_sales (month, product_id);

-- 수동 갱신
REFRESH MATERIALIZED VIEW monthly_sales;

-- 갱신 중 조회 허용 (잠금 없이 갱신)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

### Oracle 예시

```sql
-- 자동 갱신 설정
CREATE MATERIALIZED VIEW monthly_sales
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
AS
SELECT product_id, SUM(amount) AS total_sales
FROM orders
GROUP BY product_id;
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. View 최적화 팁

### Tip 1: View 중첩 최소화

View 위에 View를 쌓으면 옵티마이저가 최적화하기 어렵다.

```sql
-- 나쁜 예: View 3단 중첩
CREATE VIEW v3 AS SELECT * FROM v2 WHERE ...;
CREATE VIEW v2 AS SELECT * FROM v1 WHERE ...;
CREATE VIEW v1 AS SELECT * FROM base_table WHERE ...;

-- 좋은 예: 단일 View로 통합
CREATE VIEW v_final AS
SELECT ... FROM base_table WHERE ... AND ... AND ...;
```

### Tip 2: View Merging 확인

DBMS 옵티마이저는 View를 인라인으로 병합(merge)하여 실행한다.
병합이 안 되면 임시 테이블로 처리되어 성능 저하가 발생한다.

```sql
-- MySQL: EXPLAIN으로 View 병합 여부 확인
EXPLAIN SELECT * FROM active_users WHERE user_id = 1;
-- select_type이 SIMPLE이면 병합 성공, DERIVED이면 임시 테이블 사용
```

### Tip 3: Materialized View 갱신 전략

| 갱신 방식          | 설명                              | 적합한 경우                  |
|--------------------|-----------------------------------|------------------------------|
| ON COMMIT          | 트랜잭션 커밋 시 자동 갱신        | 데이터 변경 빈도 낮음        |
| ON DEMAND (수동)   | 명시적 REFRESH 호출 시 갱신       | 배치 처리, 야간 갱신         |
| FAST REFRESH       | 변경분(delta)만 갱신              | 대용량 테이블, 빈번한 변경   |
| COMPLETE REFRESH   | 전체 재계산                       | 집계 구조 변경 후            |

### Tip 4: View에 인덱스 힌트 적용 (MySQL)

```sql
SELECT /*+ NO_MERGE(v) */ *
FROM active_users v
WHERE v.created_at >= '2026-01-01';
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 패턴

### 패턴 1: 권한 분리 (Row-Level Security 대체)

```sql
-- 부서별 데이터 접근 제한
CREATE VIEW my_dept_employees AS
SELECT e.*
FROM employees e
WHERE e.dept_id = (
    SELECT dept_id FROM users WHERE user_id = CURRENT_USER_ID()
);
```

### 패턴 2: API 레이어 안정화

테이블 스키마가 변경되어도 View 정의만 수정하면 애플리케이션 코드 변경 불필요.

```sql
-- 테이블에 컬럼 추가/변경 후 View만 수정
CREATE OR REPLACE VIEW user_profile AS
SELECT
    user_id,
    CONCAT(first_name, ' ', last_name) AS full_name,  -- 컬럼 통합
    email,
    phone
FROM users;
```

### 패턴 3: 리포팅 전용 Materialized View

```sql
-- 매일 새벽 갱신되는 대시보드용 집계 View
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT
    DATE(created_at)    AS date,
    COUNT(*)            AS new_users,
    SUM(order_amount)   AS revenue
FROM users
JOIN orders USING (user_id)
GROUP BY 1;

-- cron으로 매일 새벽 2시 갱신
-- 0 2 * * * psql -c "REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- PostgreSQL Documentation: [CREATE VIEW](https://www.postgresql.org/docs/current/sql-createview.html) — ★★★☆☆
- PostgreSQL Documentation: [CREATE MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-creatematerializedview.html) — ★★★☆☆
- MySQL Documentation: [CREATE VIEW Statement](https://dev.mysql.com/doc/refman/8.0/en/create-view.html) — ★★★☆☆
- Oracle Documentation: [Materialized Views](https://docs.oracle.com/en/database/oracle/oracle-database/19/refrn/about-materialized-views.html) — ★★★☆☆

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
