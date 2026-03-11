# Python 프로그래밍

Python 기초부터 고급 기능까지 다루는 학습 자료입니다.

## 문서 목록

### 기초
- **[Print 함수](python_print.md)** - print() 함수 사용법

### 객체지향
- **[클래스](python_class.md)** - 클래스 정의 및 사용법
- **[Magic Attributes](python_magic_attributes.md)** - `__init__`, `__str__` 등

### 로깅
- **[Python 로깅](python_logging.md)** - logging 모듈 가이드

---

## 학습 순서

1. **기초** → [Print 함수](python_print.md)
2. **객체지향** → [클래스](python_class.md) → [Magic Attributes](python_magic_attributes.md)
3. **실전** → [로깅](python_logging.md)

---

## 빠른 참조

### 기본 문법

```python
# 변수
name = "Python"
age = 30

# 조건문
if age >= 18:
    print("Adult")

# 반복문
for i in range(5):
    print(i)

# 함수
def greet(name):
    return f"Hello, {name}!"
```

### 클래스

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name}"

person = Person("Alice", 30)
print(person.greet())
```

---

## 관련 문서

- [시스템 엔지니어링](../07_system_enginner/) - Python 활용

---

© 2026. Licensed under CC BY 4.0.
