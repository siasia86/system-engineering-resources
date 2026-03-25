# Python 프로그래밍

Python 기초부터 고급 기능까지 다루는 학습 자료입니다.

---

## 문서 목록

### 기초
- **[Print 함수](python_print.md)** - print() 함수 사용법과 매개변수
- **[제어문](python_control_flow.md)** - if/elif/else, for, while, break/continue
- **[함수](python_functions.md)** - 함수 정의, 매개변수, 람다, 기본 데코레이터

### 객체지향 프로그래밍
- **[클래스 튜토리얼](python_class.md)** - 클래스 기초부터 실전 예제까지
- **[클래스 구성 요소](python_class_components.md)** - 생성자, 메서드, 프로퍼티, 매직 메서드 레퍼런스
- **[상속](python_inheritance.md)** - 상속, super(), 다중 상속, 추상 클래스
- **[모듈 속성](python_magic_attributes.md)** - `__name__`, `__file__` 등 모듈/패키지 속성

### 중급
- **[파일 입출력](python_file_io.md)** - 파일 읽기/쓰기, with문, 경로 처리
- **[예외 처리](python_exceptions.md)** - try/except/finally, raise, 사용자 정의 예외
- **[컴프리헨션](python_comprehensions.md)** - 리스트/딕셔너리/집합 컴프리헨션

### 고급
- **[데코레이터](python_decorators.md)** - 데코레이터 개념과 활용, functools
- **[제너레이터](python_generators.md)** - 제너레이터, yield, 이터레이터
- **[컨텍스트 매니저](python_context_managers.md)** - with문, __enter__/__exit__, contextlib

### 실전
- **[패키지](python_packages.md)** - 패키지 구조, __init__.py, import
- **[Python 로깅](python_logging.md)** - logging 모듈 완벽 가이드

---

## 학습 순서

### 초보자
1. [Print 함수](python_print.md) - 기본 출력
2. [제어문](python_control_flow.md) - 조건문과 반복문
3. [함수](python_functions.md) - 함수 기초
4. [클래스 튜토리얼](python_class.md) - 객체지향 기초
5. [상속](python_inheritance.md) - 클래스 확장

### 중급자
1. [클래스 구성 요소](python_class_components.md) - 클래스 심화
2. [파일 입출력](python_file_io.md) - 파일 처리
3. [예외 처리](python_exceptions.md) - 에러 핸들링
4. [컴프리헨션](python_comprehensions.md) - 간결한 코드 작성
5. [Python 로깅](python_logging.md) - 실무 로깅

### 고급자
1. [데코레이터](python_decorators.md) - 함수 확장
2. [제너레이터](python_generators.md) - 메모리 효율적 처리
3. [컨텍스트 매니저](python_context_managers.md) - 리소스 관리
4. [패키지](python_packages.md) - 모듈 구조화
5. [모듈 속성](python_magic_attributes.md) - 모듈 시스템 이해

---

## 빠른 참조

### Print 함수
```python
print("Hello", "World", sep=",", end="!\n")  # Hello,World!
```

### 제어문
```python
# 조건문
if age >= 18:
    print("성인")
elif age >= 13:
    print("청소년")
else:
    print("어린이")

# 반복문
for i in range(5):
    print(i)

# 컴프리헨션
squares = [x**2 for x in range(5)]
```

### 함수
```python
def greet(name, greeting="안녕하세요"):
    return f"{greeting}, {name}님!"

# 람다
add = lambda x, y: x + y

# 데코레이터
@timer
def slow_function():
    time.sleep(1)
```

### 클래스
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"안녕하세요, {self.name}입니다"

person = Person("홍길동", 30)
```

### 상속
```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "멍멍!"
```

### 파일 입출력
```python
# 읽기
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 쓰기
with open("file.txt", "w", encoding="utf-8") as f:
    f.write("Hello")
```

### 예외 처리
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"에러: {e}")
finally:
    print("정리 작업")
```

### 제너레이터
```python
def count_up(n):
    for i in range(n):
        yield i

for num in count_up(5):
    print(num)
```

### 로깅
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("작업 시작")
```

---

## 주요 개념

### 클래스 vs 인스턴스
- **클래스**: 객체를 만드는 설계도
- **인스턴스**: 클래스로 만든 실제 객체

### 메서드 종류
- **인스턴스 메서드**: 인스턴스 데이터 사용 (`self`)
- **클래스 메서드**: 클래스 데이터 사용 (`@classmethod`, `cls`)
- **정적 메서드**: 독립적인 유틸리티 (`@staticmethod`)

### 매직 메서드
- `__init__`: 생성자
- `__str__`: 문자열 표현 (사용자용)
- `__repr__`: 문자열 표현 (개발자용)
- `__eq__`: `==` 연산자
- `__add__`: `+` 연산자

---

## 관련 문서

- [시스템 엔지니어링](../04_system_engineer/) - Python 활용

---

© 2026. Licensed under CC BY 4.0.
