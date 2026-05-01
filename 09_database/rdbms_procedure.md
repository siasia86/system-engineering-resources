# RDBMS Stored Procedure (저장 프로시저)

## 목차

| 단계 | 섹션                                                                                                                                                                   |
|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. Procedure 개념](#1-procedure-개념) / [2. 기본 문법](#2-기본-문법)                                                                                                  |
| 활용 | [3. 제어 구조](#3-제어-구조) / [4. 커서 (Cursor)](#4-커서-cursor) / [5. 예외 처리](#5-예외-처리)                                                                       |
| 고급 | [6. Function vs Procedure](#6-function-vs-procedure) / [7. 성능 최적화 팁](#7-성능-최적화-팁) / [8. 실전 패턴](#8-실전-패턴) |

---

## 1. Procedure 개념

Stored Procedure는 **데이터베이스 서버에 저장된 SQL 코드 블록**이다.
이름을 지정하고 필요할 때 호출하여 실행한다.

### 특징

| 항목          | 설명                                                    |
|---------------|---------------------------------------------------------|
| 저장 위치     | DB 서버 내부 (컴파일된 형태로 캐싱)                     |
| 반환값        | 없음 (OUT 파라미터로 값 전달) — Function과의 차이       |
| 트랜잭션      | 내부에서 COMMIT/ROLLBACK 가능                           |
| 재사용        | 여러 애플리케이션에서 동일 로직 공유                    |
| 보안          | 테이블 직접 접근 없이 Procedure 실행 권한만 부여 가능   |

### Procedure가 필요한 상황

- 여러 테이블에 걸친 복잡한 비즈니스 로직을 DB에서 처리할 때
- 네트워크 왕복(round-trip)을 줄여야 할 때
- 배치 처리, 데이터 마이그레이션
- 권한 제어가 필요한 민감한 데이터 처리

[⬆ 목차로 돌아가기](#목차)

---

## 2. 기본 문법

### MySQL / MariaDB

```sql
DELIMITER $$

CREATE PROCEDURE procedure_name(
    IN  param1 INT,
    IN  param2 VARCHAR(100),
    OUT result INT
)
BEGIN
    -- 로직
    SET result = param1 + 1;
END$$

DELIMITER ;

-- 호출
CALL procedure_name(10, 'test', @result);
SELECT @result;
```

### PostgreSQL (PL/pgSQL)

```sql
CREATE OR REPLACE PROCEDURE procedure_name(
    IN  param1  INT,
    IN  param2  VARCHAR,
    INOUT result INT DEFAULT 0
)
LANGUAGE plpgsql
AS $$
BEGIN
    result := param1 + 1;
END;
$$;

-- 호출
CALL procedure_name(10, 'test', NULL);
```

### 파라미터 종류

| 종류    | 설명                              | MySQL | PostgreSQL |
|---------|-----------------------------------|-------|------------|
| `IN`    | 입력 전용 (기본값)                | ✅    | ✅         |
| `OUT`   | 출력 전용                         | ✅    | ✅         |
| `INOUT` | 입력 + 출력                       | ✅    | ✅         |

### 삭제

```sql
DROP PROCEDURE IF EXISTS procedure_name;
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 제어 구조

### IF / ELSEIF / ELSE

```sql
-- MySQL
IF score >= 90 THEN
    SET grade = 'A';
ELSEIF score >= 80 THEN
    SET grade = 'B';
ELSE
    SET grade = 'C';
END IF;
```

### CASE

```sql
CASE status
    WHEN 'active'   THEN SET label = '활성';
    WHEN 'inactive' THEN SET label = '비활성';
    ELSE                 SET label = '알 수 없음';
END CASE;
```

### LOOP / WHILE / REPEAT

```sql
-- WHILE (MySQL)
SET i = 1;
WHILE i <= 10 DO
    INSERT INTO log_table (val) VALUES (i);
    SET i = i + 1;
END WHILE;

-- LOOP + LEAVE (MySQL)
my_loop: LOOP
    IF i > 10 THEN LEAVE my_loop; END IF;
    SET i = i + 1;
END LOOP my_loop;
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 커서 (Cursor)

SELECT 결과를 **행 단위로 순회**할 때 사용한다.

```sql
-- MySQL 커서 전체 패턴
DELIMITER $$

CREATE PROCEDURE process_users()
BEGIN
    DECLARE done     INT DEFAULT FALSE;
    DECLARE uid      INT;
    DECLARE uname    VARCHAR(100);

    -- 1. 커서 선언
    DECLARE cur CURSOR FOR
        SELECT user_id, username FROM users WHERE status = 'active';

    -- 2. NOT FOUND 핸들러 (루프 종료 조건)
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- 3. 커서 열기
    OPEN cur;

    read_loop: LOOP
        -- 4. 행 가져오기
        FETCH cur INTO uid, uname;
        IF done THEN LEAVE read_loop; END IF;

        -- 5. 처리 로직
        UPDATE user_stats SET last_processed = NOW() WHERE user_id = uid;
    END LOOP;

    -- 6. 커서 닫기
    CLOSE cur;
END$$

DELIMITER ;
```

⚠️ 커서는 행 단위 처리로 성능이 낮다. 가능하면 집합 기반(SET-based) SQL로 대체할 것.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 예외 처리

### MySQL HANDLER

```sql
DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
BEGIN
    ROLLBACK;
    SET error_msg = 'SQL Error occurred';
END;

DECLARE EXIT HANDLER FOR SQLSTATE '23000'  -- Duplicate entry
BEGIN
    SET result = -1;
END;
```

### PostgreSQL EXCEPTION

```sql
BEGIN
    INSERT INTO orders (user_id, amount) VALUES (p_user_id, p_amount);
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Duplicate order detected for user %', p_user_id;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Unexpected error: %', SQLERRM;
END;
```

### 트랜잭션과 예외 처리 패턴

```sql
-- MySQL
DELIMITER $$
CREATE PROCEDURE transfer_funds(
    IN from_id INT,
    IN to_id   INT,
    IN amount  DECIMAL(10,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        UPDATE accounts SET balance = balance - amount WHERE id = from_id;
        UPDATE accounts SET balance = balance + amount WHERE id = to_id;
    COMMIT;
END$$
DELIMITER ;
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Function vs Procedure

| 구분              | Function                          | Procedure                         |
|-------------------|-----------------------------------|-----------------------------------|
| 반환값            | 반드시 1개 반환 (`RETURN`)        | 없음 (OUT 파라미터 사용)          |
| 호출 방식         | SELECT 절, 표현식 내 사용 가능    | `CALL` 명령어로만 호출            |
| 트랜잭션 제어     | 불가 (MySQL 기준)                 | COMMIT/ROLLBACK 가능              |
| 사용 목적         | 값 계산, 변환                     | 비즈니스 로직, 배치 처리          |
| 예시              | `SELECT get_tax(price) FROM ...`  | `CALL process_monthly_billing();` |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 성능 최적화 팁

### Tip 1: 커서 대신 집합 기반 처리

```sql
-- 나쁜 예: 커서로 행 단위 UPDATE
FETCH cur INTO uid;
UPDATE stats SET count = count + 1 WHERE user_id = uid;

-- 좋은 예: 단일 UPDATE로 처리
UPDATE stats s
JOIN users u ON s.user_id = u.user_id
SET s.count = s.count + 1
WHERE u.status = 'active';
```

### Tip 2: 임시 테이블 활용

복잡한 중간 결과를 임시 테이블에 저장하면 반복 계산을 줄일 수 있다.

```sql
CREATE TEMPORARY TABLE tmp_active_orders AS
SELECT order_id, user_id, amount
FROM orders
WHERE status = 'pending' AND created_at >= CURDATE();

-- 이후 tmp_active_orders를 여러 번 참조
```

### Tip 3: Procedure 캐시 활용

DBMS는 Procedure를 파싱/컴파일한 결과를 캐시한다.
동적 SQL(`PREPARE` / `EXECUTE`)은 캐시 효율이 낮으므로 정적 SQL 우선 사용.

```sql
-- 나쁜 예: 동적 SQL (매번 파싱)
SET @sql = CONCAT('SELECT * FROM ', table_name);
PREPARE stmt FROM @sql;
EXECUTE stmt;

-- 좋은 예: 정적 SQL (캐시 활용)
SELECT * FROM orders WHERE status = p_status;
```

### Tip 4: 불필요한 COMMIT 최소화

루프 내 매 행마다 COMMIT하면 I/O 오버헤드가 크다.
배치 단위(예: 1000건)로 COMMIT하는 것이 효율적이다.

```sql
SET batch_count = 0;
WHILE ... DO
    -- 처리
    SET batch_count = batch_count + 1;
    IF batch_count % 1000 = 0 THEN
        COMMIT;
    END IF;
END WHILE;
COMMIT;  -- 나머지 처리
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실전 패턴

### 패턴 1: 소프트 삭제 (Soft Delete)

```sql
DELIMITER $$
CREATE PROCEDURE delete_user(IN p_user_id INT)
BEGIN
    UPDATE users
    SET deleted_at = NOW(), status = 'deleted'
    WHERE user_id = p_user_id AND deleted_at IS NULL;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found or already deleted';
    END IF;
END$$
DELIMITER ;
```

### 패턴 2: 페이지네이션

```sql
CREATE PROCEDURE get_users_paged(
    IN p_page     INT,
    IN p_per_page INT
)
BEGIN
    DECLARE p_offset INT DEFAULT (p_page - 1) * p_per_page;

    SELECT SQL_CALC_FOUND_ROWS  -- deprecated since MySQL 8.0.17; use COUNT(*) OVER() instead
        user_id, username, email
    FROM users
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT p_per_page OFFSET p_offset;

    SELECT FOUND_ROWS() AS total_count;
END;
```

### 패턴 3: 감사 로그 (Audit Log)

```sql
CREATE PROCEDURE update_salary(
    IN p_emp_id    INT,
    IN p_new_salary DECIMAL(10,2)
)
BEGIN
    DECLARE v_old_salary DECIMAL(10,2);

    SELECT salary INTO v_old_salary FROM employees WHERE emp_id = p_emp_id;

    UPDATE employees SET salary = p_new_salary WHERE emp_id = p_emp_id;

    INSERT INTO salary_audit (emp_id, old_salary, new_salary, changed_at, changed_by)
    VALUES (p_emp_id, v_old_salary, p_new_salary, NOW(), CURRENT_USER());
END;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [Stored Procedures](https://dev.mysql.com/doc/refman/8.0/en/stored-programs-defining.html) — ★★★☆☆
- PostgreSQL Documentation: [PL/pgSQL](https://www.postgresql.org/docs/current/plpgsql.html) — ★★★☆☆
- Oracle Documentation: [PL/SQL Subprograms](https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/plsql-subprograms.html) — ★★★☆☆

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
