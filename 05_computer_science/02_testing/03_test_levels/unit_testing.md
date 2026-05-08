# 유닛 테스트 (Unit Testing)

## 목차

| 섹션                                                                    |
|-------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원칙](#2-원칙) / [3. 구조](#3-구조)            |
| [4. 좋은 유닛 테스트](#4-좋은-유닛-테스트) / [5. 안티패턴](#5-안티패턴) |

## 1. 개요

유닛 테스트는 소프트웨어의 가장 작은 단위(함수, 메서드, 클래스)를 독립적으로 검증하는 테스트입니다.

| 항목        | 내용                           |
|-------------|--------------------------------|
| 테스트 대상 | 함수, 메서드, 클래스 단위      |
| 실행 속도   | 밀리초 단위 (외부 의존성 없음) |
| 실행 주체   | 개발자 (코드 작성 시)          |
| 목적        | 로직 정확성 검증, 회귀 방지    |

### 테스트 피라미드

```
        /\
       /  \       E2E (소수)
      /----\
     /      \     Integration (중간)
    /--------\
   /          \   Unit (다수, 빠름)
  /____________\
```

유닛 테스트는 피라미드 하단에 위치하며, 가장 많은 수를 차지합니다.

## 2. 원칙

### FIRST 원칙

| 원칙                | 설명                                     |
|---------------------|------------------------------------------|
| **F**ast            | 빠르게 실행 (외부 I/O 없음)              |
| **I**solated        | 다른 테스트에 의존하지 않음              |
| **R**epeatable      | 몇 번을 실행해도 동일 결과               |
| **S**elf-validating | 성공/실패를 자동 판단 (수동 확인 불필요) |
| **T**imely          | 프로덕션 코드와 함께 작성                |

### 단일 책임

하나의 테스트는 하나의 동작만 검증합니다.

```
❌ test_user_creation_and_email_send()
✅ test_user_creation()
✅ test_email_send_on_creation()
```

## 3. 구조

### AAA 패턴 (Arrange-Act-Assert)

```python
def test_withdraw():
    # Arrange (준비)
    account = Account(balance=1000)

    # Act (실행)
    account.withdraw(200)

    # Assert (검증)
    assert account.balance == 800
```

### Given-When-Then (BDD 스타일)

```python
def test_withdraw():
    # Given: 잔액 1000원 계좌
    account = Account(balance=1000)

    # When: 200원 출금
    account.withdraw(200)

    # Then: 잔액 800원
    assert account.balance == 800
```

## 4. 좋은 유닛 테스트

### 테스트 이름 규칙

```
test_<대상>_<조건>_<기대결과>
```

```python
def test_withdraw_sufficient_balance_reduces_balance():
    ...

def test_withdraw_insufficient_balance_raises_error():
    ...

def test_transfer_same_account_raises_error():
    ...
```

### 테스트 독립성

```python
# ❌ 테스트 간 상태 공유
balance = 1000

def test_deposit():
    global balance
    balance += 500
    assert balance == 1500

def test_withdraw():
    global balance
    balance -= 200  # 이전 테스트 결과에 의존
    assert balance == 1300

# ✅ 각 테스트가 독립적
def test_deposit():
    account = Account(balance=1000)
    account.deposit(500)
    assert account.balance == 1500

def test_withdraw():
    account = Account(balance=1000)
    account.withdraw(200)
    assert account.balance == 800
```

### 경계값 포함

```python
@pytest.mark.parametrize("amount,expected", [
    (0, 1000),       # 최소값
    (1, 999),        # 최소값 + 1
    (999, 1),        # 최대값 - 1
    (1000, 0),       # 최대값 (잔액 전부)
])
def test_withdraw_valid(amount, expected):
    account = Account(balance=1000)
    account.withdraw(amount)
    assert account.balance == expected
```

## 5. 안티패턴

| 안티패턴             | 문제점                           | 해결                    |
|----------------------|----------------------------------|-------------------------|
| 테스트 없음          | 회귀 버그 발견 불가              | 코드와 함께 테스트 작성 |
| 구현 세부사항 테스트 | 리팩토링 시 테스트 깨짐          | 동작(입출력)만 검증     |
| 느린 테스트          | 실행 빈도 감소                   | 외부 의존성 Mock 처리   |
| 테스트 간 의존성     | 실행 순서에 따라 결과 변동       | 각 테스트 독립 setup    |
| 과도한 Mock          | 실제 동작과 괴리                 | 통합 테스트로 보완      |
| 하나의 assert만 강제 | 관련 검증을 분리하면 가독성 저하 | 논리적 단위로 그룹핑    |

## 참고 자료

- Martin Fowler. "Unit Test" — ★★★★☆
- Kent Beck. "Test Driven Development: By Example" — ★★★★☆
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
