# Python 테스트

## 목차

| 섹션                                                                           |
|--------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. pytest](#2-pytest) / [3. unittest](#3-unittest)       |
| [4. Mock](#4-mock) / [5. 커버리지](#5-커버리지) / [6. 실전 패턴](#6-실전-패턴) |

## 1. 개요

Python 테스트 프레임워크와 실전 사용법을 정리합니다.

| 프레임워크 | 특징                          | 사용 시점                |
|------------|-------------------------------|--------------------------|
| `pytest`   | 간결한 문법, 플러그인 풍부    | 신규 프로젝트 (권장)     |
| `unittest` | 표준 라이브러리, xUnit 스타일 | 외부 의존성 없이 사용 시 |
| `doctest`  | docstring 내 예제 실행        | 간단한 함수 검증         |

## 2. pytest

### 설치

```bash
pip install pytest pytest-cov
```

### 기본 구조

```python
# test_calculator.py
def test_add():
    assert 1 + 1 == 2

def test_divide():
    assert 10 / 2 == 5.0

def test_divide_by_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

### 실행

```bash
# 전체 실행
pytest

# 특정 파일
pytest test_calculator.py

# 특정 함수
pytest test_calculator.py::test_add

# 상세 출력
pytest -v

# 첫 실패 시 중단
pytest -x

# 마지막 실패 테스트만 재실행
pytest --lf
```

### fixture

```python
import pytest

@pytest.fixture
def db_connection():
    """테스트 전 DB 연결, 테스트 후 정리"""
    conn = create_connection()
    yield conn
    conn.close()

def test_query(db_connection):
    result = db_connection.execute("SELECT 1")
    assert result == 1
```

### parametrize

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (-1, 1),
    (0, 0),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

### 경계값 테스트 예시

```python
import pytest

def validate_age(age):
    if not 0 <= age <= 150:
        raise ValueError("invalid age")
    return age

@pytest.mark.parametrize("age", [-1, 0, 1, 149, 150, 151])
def test_age_boundary(age):
    if age < 0 or age > 150:
        with pytest.raises(ValueError):
            validate_age(age)
    else:
        assert validate_age(age) == age
```

## 3. unittest

### 기본 구조

```python
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        """각 테스트 전 실행"""
        self.calc = Calculator()

    def tearDown(self):
        """각 테스트 후 실행"""
        pass

    def test_add(self):
        self.assertEqual(self.calc.add(1, 2), 3)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(1, 0)

if __name__ == '__main__':
    unittest.main()
```

### 주요 assert 메서드

| 메서드                    | 검증 내용          |
|---------------------------|--------------------|
| `assertEqual(a, b)`       | `a == b`           |
| `assertNotEqual(a, b)`    | `a != b`           |
| `assertTrue(x)`           | `bool(x) is True`  |
| `assertFalse(x)`          | `bool(x) is False` |
| `assertIs(a, b)`          | `a is b`           |
| `assertIsNone(x)`         | `x is None`        |
| `assertIn(a, b)`          | `a in b`           |
| `assertRaises(exc)`       | 예외 발생 확인     |
| `assertAlmostEqual(a, b)` | 부동소수점 비교    |

## 4. Mock

### unittest.mock

```python
from unittest.mock import patch, MagicMock

# 함수 패치
@patch('module.requests.get')
def test_api_call(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"key": "value"}

    result = fetch_data()
    assert result == {"key": "value"}
    mock_get.assert_called_once()

# 객체 메서드 패치
@patch.object(Database, 'connect')
def test_db(mock_connect):
    mock_connect.return_value = MagicMock()
    # ...
```

### side_effect

```python
from unittest.mock import patch

@patch('module.api_call')
def test_retry(mock_api):
    # 첫 호출 실패, 두 번째 성공
    mock_api.side_effect = [ConnectionError, {"data": "ok"}]
    result = retry_api_call()
    assert result == {"data": "ok"}
    assert mock_api.call_count == 2
```

## 5. 커버리지

### 설치 및 실행

```bash
# pytest-cov 사용
pytest --cov=src --cov-report=term-missing

# HTML 리포트
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### 출력 예시

```
---------- coverage: ----------
Name              Stmts   Miss  Cover   Missing
------------------------------------------------
src/calc.py          20      2    90%   15, 22
src/utils.py         35      0   100%
------------------------------------------------
TOTAL                55      2    96%
```

### .coveragerc 설정

```ini
[run]
source = src
omit =
    */test_*
    */__pycache__/*

[report]
fail_under = 80
show_missing = true
```

## 6. 실전 패턴

### 테스트 디렉토리 구조

```
project/
├── src/
│   ├── __init__.py
│   ├── calculator.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # shared fixtures
│   ├── test_calculator.py
│   └── test_utils.py
├── pytest.ini
└── requirements-dev.txt
```

### pytest.ini

```ini
[pytest]
testpaths = tests
addopts = -v --tb=short
markers =
    slow: 느린 테스트
    integration: 통합 테스트
```

### conftest.py (공통 fixture)

```python
import pytest

@pytest.fixture(scope="session")
def app_config():
    return {"db_host": "localhost", "db_port": 5432}

@pytest.fixture
def tmp_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    return f
```

### 마커로 테스트 분류

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    # 시간이 오래 걸리는 테스트
    pass

@pytest.mark.integration
def test_db_connection():
    # 외부 의존성 필요
    pass
```

```bash
# slow 제외하고 실행
pytest -m "not slow"

# integration만 실행
pytest -m integration
```

## 참고 자료

- pytest docs: [docs.pytest.org](https://docs.pytest.org/) — ★★★☆☆
- unittest docs: [docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html) — ★★★☆☆
- [테스트 기법 이론](../05_computer_science/02_testing/)

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
