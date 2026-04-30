# RDBMS 정규화 (Normalization)

## 목차

| 단계 | 섹션                                                                                                                                                    |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 정규화 개념](#1-정규화-개념) / [2. 이상 현상](#2-이상-현상)                                                                                          |
| 정규형 | [3. 1NF](#3-1nf) / [4. 2NF](#4-2nf) / [5. 3NF](#5-3nf) / [6. BCNF](#6-bcnf)                                                                          |
| 실무 | [7. 반정규화](#7-반정규화) / [8. 정규화 vs 반정규화 판단 기준](#8-정규화-vs-반정규화-판단-기준) |

---

## 1. 정규화 개념

정규화는 **데이터 중복을 제거**하고 **이상 현상을 방지**하기 위해 테이블을 분리하는 설계 과정이다.

```
비정규화 테이블 (문제 있음)
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ order_id │ user_id  │ username │ product  │ category │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│ 1        │ 101      │ Alice    │ Laptop   │ IT       │
│ 2        │ 101      │ Alice    │ Mouse    │ IT       │  ← username 중복
│ 3        │ 102      │ Bob      │ Desk     │ Furniture│
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 이상 현상

| 이상 현상 | 설명 | 예시 |
|-----------|------|------|
| **삽입 이상** | 불필요한 데이터 없이 삽입 불가 | 주문 없이 사용자 등록 불가 |
| **삭제 이상** | 삭제 시 의도치 않은 데이터 손실 | 마지막 주문 삭제 시 사용자 정보도 삭제 |
| **갱신 이상** | 중복 데이터 일부만 수정 시 불일치 | username 변경 시 모든 행 수정 필요 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 1NF

**원자값(Atomic Value)**: 각 컬럼은 하나의 값만 가져야 한다.

```
위반 예시:
┌──────────┬──────────────────────┐
│ order_id │ products             │
├──────────┼──────────────────────┤
│ 1        │ Laptop, Mouse, Desk  │  ← 다중값
└──────────┴──────────────────────┘

1NF 적용:
┌──────────┬──────────┐
│ order_id │ product  │
├──────────┼──────────┤
│ 1        │ Laptop   │
│ 1        │ Mouse    │
│ 1        │ Desk     │
└──────────┴──────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 2NF

**부분 함수 종속 제거**: 복합 기본키에서 일부 키에만 종속된 컬럼을 분리한다.

```
위반 예시 (PK: order_id + product_id):
┌──────────┬────────────┬──────────────┬───────────────┐
│ order_id │ product_id │ product_name │ quantity      │
│ (PK)     │ (PK)       │              │               │
├──────────┼────────────┼──────────────┼───────────────┤
│ 1        │ 10         │ Laptop       │ 2             │
└──────────┴────────────┴──────────────┴───────────────┘
product_name은 product_id에만 종속 → 부분 종속

2NF 적용:
order_items (order_id PK, product_id PK, quantity)
products    (product_id PK, product_name)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 3NF

**이행 함수 종속 제거**: 기본키 → A → B 형태의 이행 종속을 분리한다.

```
위반 예시 (PK: order_id):
┌──────────┬─────────┬──────────────┐
│ order_id │ user_id │ user_city    │
├──────────┼─────────┼──────────────┤
│ 1        │ 101     │ Seoul        │
└──────────┴─────────┴──────────────┘
order_id → user_id → user_city (이행 종속)

3NF 적용:
orders (order_id PK, user_id FK)
users  (user_id PK, user_city)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. BCNF

**모든 결정자가 후보키**: 3NF를 만족하지만 결정자가 후보키가 아닌 경우를 분리한다.

```
위반 예시 (PK: student_id + course):
┌────────────┬────────┬──────────┐
│ student_id │ course │ teacher  │
├────────────┼────────┼──────────┤
│ 1          │ Math   │ Kim      │
│ 2          │ Math   │ Kim      │
└────────────┴────────┴──────────┘
teacher → course (teacher가 후보키가 아님에도 결정자)

BCNF 적용:
student_course (student_id PK, teacher FK)
teacher_course (teacher PK, course)
```

### 정규형 요약

| 정규형 | 조건 |
|--------|------|
| 1NF | 원자값 |
| 2NF | 1NF + 부분 함수 종속 제거 |
| 3NF | 2NF + 이행 함수 종속 제거 |
| BCNF | 3NF + 모든 결정자가 후보키 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 반정규화

성능을 위해 의도적으로 정규화를 되돌리는 기법.

### 컬럼 중복

```sql
-- orders 테이블에 username 컬럼 추가 (users JOIN 제거)
ALTER TABLE orders ADD COLUMN username VARCHAR(100);
```

### 집계 컬럼 추가

```sql
-- users 테이블에 order_count 컬럼 추가
ALTER TABLE users ADD COLUMN order_count INT DEFAULT 0;

-- 주문 생성 시 트리거로 갱신
CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
    UPDATE users SET order_count = order_count + 1
    WHERE user_id = NEW.user_id;
```

### 테이블 병합

```sql
-- 1:1 관계 테이블을 하나로 합침
-- users + user_profiles → users (컬럼 추가)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 정규화 vs 반정규화 판단 기준

| 기준 | 정규화 선택 | 반정규화 선택 |
|------|------------|--------------|
| 쓰기 빈도 | 높음 | 낮음 |
| 읽기 빈도 | 낮음 | 높음 |
| 데이터 정합성 | 중요 | 다소 허용 |
| JOIN 비용 | 감수 가능 | 병목 발생 |
| 데이터 크기 | 소규모 | 대규모 |

### 실무 원칙

1. **설계는 정규화로 시작** — 이상 현상 없는 구조 확보
2. **성능 문제 발생 시 반정규화** — EXPLAIN으로 병목 확인 후 적용
3. **반정규화 시 데이터 동기화 전략 필수** — 트리거, 배치, 애플리케이션 레벨

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Codd, E.F. "A Relational Model of Data for Large Shared Data Banks" (1970)
- Date, C.J. "An Introduction to Database Systems"
- MySQL Documentation: [Database Design](https://dev.mysql.com/doc/refman/8.0/en/database-use.html) — ★★★☆☆

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
