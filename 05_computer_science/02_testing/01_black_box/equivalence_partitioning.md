# 동등 분할 (Equivalence Partitioning)

## 목차

| 섹션                                                                   |
|------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원리](#2-원리) / [3. 분할 방법](#3-분할-방법) |
| [4. 예시](#4-예시) / [5. 다른 기법과의 조합](#5-다른-기법과의-조합)    |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

동등 분할(EP)은 입력 도메인을 동등한 동작을 하는 그룹(파티션)으로 나누고, 각 그룹에서 대표값 1개만 테스트하는 기법입니다.

| 항목          | 내용                                        |
|---------------|---------------------------------------------|
| 분류          | 블랙박스 테스트 기법                        |
| 핵심 아이디어 | 같은 파티션 내 값은 동일하게 처리됨         |
| 목적          | 테스트 케이스 수를 줄이면서 커버리지 유지   |
| 전제          | 한 파티션의 대표값이 통과하면 나머지도 통과 |

[⬆ 목차로 돌아가기](#목차)

## 2. 원리

```
Input Domain
┌────────────┬──────────────────────┬────────────┐
│ Invalid(1) │       Valid (2)      │ Invalid(3) │
│   < min    │   min <= x <= max    │   > max    │
└────────────┴──────────────────────┴────────────┘
      ↑                ↑                   ↑
  1 representative  1 representative  1 representative

- 유효 파티션: 정상 처리되는 입력 그룹
- 무효 파티션: 에러/거부되는 입력 그룹
- 각 파티션에서 **1개 대표값**만 선택하여 테스트

[⬆ 목차로 돌아가기](#목차)

## 3. 분할 방법

### 범위 기반

입력이 범위로 정의된 경우:

```
입력: 1 ≤ quantity ≤ 100

파티션:
  P1 (무효): quantity < 1
  P2 (유효): 1 ≤ quantity ≤ 100
  P3 (무효): quantity > 100
```

### 집합 기반

입력이 특정 값 집합인 경우:

```
입력: color ∈ {red, green, blue}

파티션:
  P1 (유효): color = "red"
  P2 (유효): color = "green"
  P3 (유효): color = "blue"
  P4 (무효): color = "yellow" (집합 외)
```

### 조건 기반

입력이 boolean 조건인 경우:

```
입력: is_admin (true/false)

파티션:
  P1 (유효): is_admin = true
  P2 (유효): is_admin = false
```

### 타입 기반

입력 타입에 따른 분할:

```
입력: age (정수 기대)

파티션:
  P1 (유효): 정수 (25)
  P2 (무효): 문자열 ("abc")
  P3 (무효): 부동소수점 (25.5)
  P4 (무효): NULL/빈값
  P5 (무효): 음수 (-1)
```

[⬆ 목차로 돌아가기](#목차)

## 4. 예시

### 예시 1: 할인율 계산

| 구매 금액         | 할인율 | 파티션 |
|-------------------|--------|--------|
| 0 ~ 9,999원       | 0%     | P1     |
| 10,000 ~ 49,999원 | 5%     | P2     |
| 50,000 ~ 99,999원 | 10%    | P3     |
| 100,000원 이상    | 15%    | P4     |

테스트 대표값:

| 파티션 | 대표값  | 기대 할인율 |
|--------|---------|-------------|
| P1     | 5,000   | 0%          |
| P2     | 30,000  | 5%          |
| P3     | 70,000  | 10%         |
| P4     | 150,000 | 15%         |
| 무효   | -1,000  | 에러        |

### 예시 2: 로그인 입력

| 파티션            | 유형 | 대표값                | 기대 결과 |
|-------------------|------|-----------------------|-----------|
| 유효 ID + 유효 PW | 유효 | `user1` / `Pass1234`  | 성공      |
| 빈 ID             | 무효 | `` / `Pass1234`       | 에러      |
| 빈 PW             | 무효 | `user1` / ``          | 에러      |
| 존재하지 않는 ID  | 무효 | `nouser` / `Pass1234` | 에러      |
| 잘못된 PW         | 무효 | `user1` / `wrong`     | 에러      |

### 예시 3: 파일 업로드

| 파티션        | 유형 | 대표값       | 기대 결과 |
|---------------|------|--------------|-----------|
| 허용 확장자   | 유효 | `report.pdf` | 성공      |
| 허용 확장자   | 유효 | `image.png`  | 성공      |
| 비허용 확장자 | 무효 | `script.exe` | 거부      |
| 크기 초과     | 무효 | 11MB 파일    | 거부      |
| 빈 파일       | 무효 | 0 byte       | 거부      |

[⬆ 목차로 돌아가기](#목차)

## 5. 다른 기법과의 조합

### 동등 분할 + 경계값 분석

```
입력: 1 ≤ quantity ≤ 100

동등 분할 대표값: -5, 50, 150 (3개)
경계값 추가:      0, 1, 2, 99, 100, 101 (6개)

조합: 총 9개 → 중복 제거 → 7~8개 테스트 케이스
```

### 동등 분할 + 결정 테이블

복수 입력의 조합이 결과에 영향을 줄 때:

| 조건 \ 규칙     | R1  | R2  | R3  | R4  |
|-----------------|-----|-----|-----|-----|
| 회원 등급 = VIP | Y   | Y   | N   | N   |
| 구매 금액 ≥ 5만 | Y   | N   | Y   | N   |
| **할인율**      | 20% | 10% | 10% | 0%  |

### 테스트 케이스 수 비교

| 기법            | 테스트 수 (입력 범위 1~100) |
|-----------------|-----------------------------|
| 전수 테스트     | 102개 (0~101)               |
| 동등 분할만     | 3개                         |
| 동등 분할 + BVA | 7~8개                       |

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- ISTQB Foundation Level Syllabus — ★★★☆☆
- Glenford J. Myers. "The Art of Software Testing" — ★★★★☆
- [경계값 분석](boundary_value_analysis.md)
- [Python 테스트 실습](../../../11_python/python_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-08

**마지막 업데이트**: 2026-05-08

© 2026 siasia86. Licensed under CC BY 4.0.
