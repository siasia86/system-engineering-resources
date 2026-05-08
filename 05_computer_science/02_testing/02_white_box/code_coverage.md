# 코드 커버리지 (Code Coverage)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 커버리지 유형](#2-커버리지-유형) / [3. 측정 방법](#3-측정-방법) |
| [4. 예시](#4-예시) / [5. 실전 가이드](#5-실전-가이드) |

## 1. 개요

코드 커버리지는 테스트가 소스 코드의 어느 부분을 실행했는지 측정하는 화이트박스 테스트 지표입니다.

| 항목          | 내용                                    |
|---------------|-----------------------------------------|
| 분류          | 화이트박스 테스트 기법                  |
| 핵심 아이디어 | 실행된 코드 비율로 테스트 충분성 판단   |
| 목적          | 테스트되지 않은 코드 영역 식별          |
| 한계          | 100% 커버리지 ≠ 버그 없음               |

## 2. 커버리지 유형

### 구문 커버리지 (Statement Coverage)

모든 실행 가능한 코드 라인이 최소 1회 실행되었는지 측정합니다.

```python
def calculate(x, y):
    result = x + y        # 라인 1
    if result > 100:      # 라인 2
        result = 100      # 라인 3
    return result         # 라인 4
```

- `calculate(50, 60)` → 라인 1,2,3,4 실행 → 구문 커버리지 100%
- `calculate(10, 20)` → 라인 1,2,4 실행 → 구문 커버리지 75%

### 분기 커버리지 (Branch Coverage)

모든 조건문의 True/False 분기가 최소 1회 실행되었는지 측정합니다.

```python
def calculate(x, y):
    result = x + y
    if result > 100:       # 분기: True / False
        result = 100
    return result
```

- TC1: `calculate(50, 60)` → if True ✅
- TC2: `calculate(10, 20)` → if False ✅
- 분기 커버리지 100% (2개 TC 필요)

### 조건 커버리지 (Condition Coverage)

복합 조건 내 각 개별 조건이 True/False를 모두 가졌는지 측정합니다.

```python
if age >= 18 and has_id:    # 조건1: age>=18, 조건2: has_id
    allow_entry()
```

| TC  | age>=18 | has_id | 복합 결과 |
|-----|---------|--------|-----------|
| TC1 | True    | True   | True      |
| TC2 | False   | False  | False     |

조건 커버리지 100% (각 조건이 T/F 모두 경험)이지만, 분기 커버리지는 `(True, False)`, `(False, True)` 조합을 놓칠 수 있습니다.

### MC/DC (Modified Condition/Decision Coverage)

각 조건이 독립적으로 결과에 영향을 미치는지 검증합니다. 항공/의료 등 안전 필수 시스템에서 요구됩니다.

```python
if A and B:
```

| TC  | A     | B     | 결과  | 검증                |
|-----|-------|-------|-------|---------------------|
| TC1 | True  | True  | True  |                     |
| TC2 | False | True  | False | A가 결과에 영향     |
| TC3 | True  | False | False | B가 결과에 영향     |

3개 TC로 MC/DC 달성 (전수 4개 대비 1개 감소).

## 3. 측정 방법

### 커버리지 수준 비교

```
MC/DC ⊃ 분기 커버리지 ⊃ 구문 커버리지

MC/DC 100% → 분기 100% 보장
분기 100% → 구문 100% 보장
구문 100% → 분기 100% 보장하지 않음
```

### 강도 순서

| 수준               | 강도 | 요구 사항                    |
|--------------------|------|------------------------------|
| 구문 커버리지      | 낮음 | 모든 라인 실행               |
| 분기 커버리지      | 중간 | 모든 분기 T/F 실행           |
| 조건 커버리지      | 중간 | 각 조건 T/F 경험             |
| 조건/분기 커버리지 | 높음 | 조건 + 분기 동시 만족        |
| MC/DC              | 최고 | 각 조건의 독립적 영향 검증   |

## 4. 예시

### 예시: 할인 계산

```python
def get_discount(age, is_member):
    if age < 18 or is_member:     # 분기 1
        discount = 20
    elif age >= 65:                # 분기 2
        discount = 15
    else:                          # 분기 3
        discount = 0
    return discount
```

#### 구문 커버리지 100% 달성

| TC  | age | is_member | 경로   |
|-----|-----|-----------|--------|
| TC1 | 15  | False     | 분기 1 |
| TC2 | 70  | False     | 분기 2 |
| TC3 | 30  | False     | 분기 3 |

#### 분기 커버리지 100% 달성

위 3개 TC + 추가:

| TC  | age | is_member | 분기 1 조건 |
|-----|-----|-----------|-------------|
| TC4 | 30  | True      | or 우측 True |

## 5. 실전 가이드

### 권장 커버리지 목표

| 프로젝트 유형      | 권장 목표 | 비고                    |
|--------------------|-----------|-------------------------|
| 일반 웹 서비스     | 70~80%    | 비즈니스 로직 중심      |
| 라이브러리/SDK     | 90%+      | 공개 API 전체 커버      |
| 안전 필수 시스템   | MC/DC     | DO-178C, IEC 61508      |
| 인프라 스크립트    | 60~70%    | 핵심 경로 위주          |

### 커버리지가 높아도 부족한 경우

- 경계값 미검증 (라인은 실행했지만 경계 입력 미사용)
- 예외 경로 미검증 (try 블록만 실행, except 미실행)
- 동시성 문제 (단일 스레드에서만 테스트)
- 환경 의존 코드 (특정 OS에서만 실행되는 분기)

### 커버리지 도구

| 언어   | 도구                        |
|--------|-----------------------------|
| Python | `coverage.py`, `pytest-cov` |
| Java   | JaCoCo, Cobertura           |
| Go     | `go test -cover`            |
| C/C++  | gcov, lcov                  |
| JS/TS  | Istanbul (nyc), c8          |

## 참고 자료

- ISTQB Foundation Level Syllabus — ★★★☆☆
- DO-178C: Software Considerations in Airborne Systems — ★★★★☆
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
