# Python 함수 (Functions)

Python 함수의 정의부터 고급 활용까지 다루는 완벽 가이드입니다.

## 목차
- [함수란?](#함수란)
- [함수 정의와 호출](#함수-정의와-호출)
- [매개변수와 인자](#매개변수와-인자)
- [반환값](#반환값)
- [람다 함수](#람다-함수)
- [데코레이터](#데코레이터)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)
- [요약](#요약)

---

## 함수란?

특정 작업을 수행하는 재사용 가능한 코드 블록입니다.

### 왜 사용하나?

- **코드 재사용**: 같은 코드 반복 방지
- **모듈화**: 복잡한 문제를 작은 단위로 분해
- **가독성**: 코드 이해 쉬움
- **유지보수**: 수정이 용이

---

## 함수 정의와 호출

### 기본 함수

```python
def greet():
    print("안녕하세요!")

# 호출
greet()  # 안녕하세요!
```

### 매개변수가 있는 함수

```python
def greet(name):
    print(f"안녕하세요, {name}님!")

greet("홍길동")  # 안녕하세요, 홍길동님!
```

### 반환값이 있는 함수

```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)  # 8
```

---

## 매개변수와 인자

### 위치 인자 (Positional Arguments)

```python
def introduce(name, age):
    return f"{name}은(는) {age}살입니다"

print(introduce("홍길동", 30))  # 홍길동은(는) 30살입니다
```

### 키워드 인자 (Keyword Arguments)

```python
def introduce(name, age):
    return f"{name}은(는) {age}살입니다"

# 순서 상관없음
print(introduce(age=30, name="홍길동"))
```

### 기본값 매개변수

```python
def greet(name, greeting="안녕하세요"):
    return f"{greeting}, {name}님!"

print(greet("홍길동"))              # 안녕하세요, 홍길동님!
print(greet("홍길동", "반갑습니다"))  # 반갑습니다, 홍길동님!
```

### 가변 위치 인자 (*args)

```python
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3))        # 6
print(sum_all(1, 2, 3, 4, 5))  # 15
```

### 가변 키워드 인자 (**kwargs)

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="홍길동", age=30, city="서울")
# name: 홍길동
# age: 30
# city: 서울
```

### 모든 매개변수 조합

```python
def complex_function(a, b, *args, default=10, **kwargs):
    print(f"a: {a}")
    print(f"b: {b}")
    print(f"args: {args}")
    print(f"default: {default}")
    print(f"kwargs: {kwargs}")

complex_function(1, 2, 3, 4, 5, default=20, x=100, y=200)
# a: 1
# b: 2
# args: (3, 4, 5)
# default: 20
# kwargs: {'x': 100, 'y': 200}
```

### 키워드 전용 인자 (Keyword-Only)

```python
def greet(name, *, greeting="안녕하세요"):
    return f"{greeting}, {name}님!"

# greet("홍길동", "반갑습니다")  # TypeError!
greet("홍길동", greeting="반갑습니다")  # OK
```

### 위치 전용 인자 (Positional-Only, Python 3.8+)

```python
def divide(a, b, /):
    return a / b

print(divide(10, 2))  # 5.0
# divide(a=10, b=2)  # TypeError!
```

---

## 반환값

### 단일 반환값

```python
def square(x):
    return x ** 2

result = square(5)
print(result)  # 25
```

### 여러 반환값 (튜플)

```python
def get_user_info():
    name = "홍길동"
    age = 30
    city = "서울"
    return name, age, city

name, age, city = get_user_info()
print(name, age, city)  # 홍길동 30 서울
```

### 조건부 반환

```python
def divide(a, b):
    if b == 0:
        return None
    return a / b

result = divide(10, 2)
print(result)  # 5.0

result = divide(10, 0)
print(result)  # None
```

### 반환값 없음 (None)

```python
def print_message(msg):
    print(msg)
    # return 없음 = return None

result = print_message("안녕")
print(result)  # None
```

---

## 람다 함수

한 줄로 작성하는 익명 함수입니다.

### 기본 사용

```python
# 일반 함수
def add(x, y):
    return x + y

# 람다 함수
add = lambda x, y: x + y

print(add(3, 5))  # 8
```

### 정렬에 활용

```python
students = [
    {"name": "홍길동", "age": 30},
    {"name": "김철수", "age": 25},
    {"name": "이영희", "age": 28}
]

# age로 정렬
sorted_students = sorted(students, key=lambda x: x["age"])
print(sorted_students)
# [{'name': '김철수', 'age': 25}, ...]
```

### map, filter와 함께

```python
# map: 모든 요소에 함수 적용
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# filter: 조건에 맞는 요소만
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4]
```

---

## 데코레이터

함수를 수정하지 않고 기능을 추가하는 방법입니다.

### 기본 데코레이터

```python
def my_decorator(func):
    def wrapper():
        print("함수 실행 전")
        func()
        print("함수 실행 후")
    return wrapper

@my_decorator
def say_hello():
    print("안녕하세요!")

say_hello()
# 함수 실행 전
# 안녕하세요!
# 함수 실행 후
```

### 인자가 있는 함수 데코레이팅

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"함수 호출: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"함수 종료: {func.__name__}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

result = add(3, 5)
# 함수 호출: add
# 함수 종료: add
print(result)  # 8
```

### 실용 데코레이터: 실행 시간 측정

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "완료"

slow_function()
# slow_function 실행 시간: 1.0001초
```

### 매개변수가 있는 데코레이터

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"안녕하세요, {name}님!")

greet("홍길동")
# 안녕하세요, 홍길동님!
# 안녕하세요, 홍길동님!
# 안녕하세요, 홍길동님!
```

### 여러 데코레이터 적용

```python
def bold(func):
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def greet(name):
    return f"안녕하세요, {name}님!"

print(greet("홍길동"))
# <b><i>안녕하세요, 홍길동님!</i></b>
```

---

## 실전 예제

### 예제 1: 계산기

```python
def calculator(operation):
    def add(a, b):
        return a + b
    
    def subtract(a, b):
        return a - b
    
    def multiply(a, b):
        return a * b
    
    def divide(a, b):
        if b == 0:
            return "0으로 나눌 수 없습니다"
        return a / b
    
    operations = {
        '+': add,
        '-': subtract,
        '*': multiply,
        '/': divide
    }
    
    return operations.get(operation, lambda a, b: "잘못된 연산")

add_func = calculator('+')
print(add_func(10, 5))  # 15

div_func = calculator('/')
print(div_func(10, 2))  # 5.0
```

### 예제 2: 캐싱 데코레이터

```python
def memoize(func):
    cache = {}
    
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
            print(f"계산: {args}")
        else:
            print(f"캐시 사용: {args}")
        return cache[args]
    
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(5))
# 계산: (0,)
# 계산: (1,)
# 계산: (2,)
# 계산: (3,)
# 계산: (4,)
# 계산: (5,)
# 5
```

### 예제 3: 유효성 검사 데코레이터

```python
def validate_positive(func):
    def wrapper(*args):
        for arg in args:
            if arg < 0:
                raise ValueError("음수는 허용되지 않습니다")
        return func(*args)
    return wrapper

@validate_positive
def calculate_area(width, height):
    return width * height

print(calculate_area(5, 3))  # 15
# print(calculate_area(-5, 3))  # ValueError!
```

### 예제 4: 로깅 데코레이터

```python
import logging

logging.basicConfig(level=logging.INFO)

def log_function_call(func):
    def wrapper(*args, **kwargs):
        logging.info(f"함수 호출: {func.__name__}")
        logging.info(f"인자: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"반환값: {result}")
        return result
    return wrapper

@log_function_call
def process_data(data, multiplier=2):
    return data * multiplier

process_data(10, multiplier=3)
# INFO:root:함수 호출: process_data
# INFO:root:인자: args=(10,), kwargs={'multiplier': 3}
# INFO:root:반환값: 30
```

---

## 실전 팁

### Tip 1: 함수는 한 가지 일만

```python
# 나쁜 예: 여러 일을 함
def process_user(name, age):
    # 검증
    if not name:
        return None
    # 변환
    name = name.upper()
    # 저장
    save_to_db(name, age)
    # 이메일 발송
    send_email(name)

# 좋은 예: 분리
def validate_name(name):
    return bool(name)

def format_name(name):
    return name.upper()

def save_user(name, age):
    save_to_db(name, age)

def notify_user(name):
    send_email(name)
```

### Tip 2: 기본값은 불변 객체로

```python
# 나쁜 예: 가변 기본값
def add_item(item, items=[]):  # 위험!
    items.append(item)
    return items

# 좋은 예
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Tip 3: 타입 힌트 사용

```python
def greet(name: str, age: int) -> str:
    return f"{name}은(는) {age}살입니다"

# IDE에서 타입 체크 가능
result = greet("홍길동", 30)
```

### Tip 4: Docstring 작성

```python
def calculate_area(width: float, height: float) -> float:
    """직사각형의 넓이를 계산합니다.
    
    Args:
        width: 가로 길이
        height: 세로 길이
    
    Returns:
        넓이 (float)
    
    Examples:
        >>> calculate_area(5, 3)
        15.0
    """
    return width * height
```

### Tip 5: functools.wraps 사용

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # 원본 함수 정보 유지
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """인사 함수"""
    return f"안녕, {name}!"

print(greet.__name__)  # greet (wraps 없으면 wrapper)
print(greet.__doc__)   # 인사 함수
```

### Tip 6: 부분 함수 (Partial)

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

# 제곱 함수
square = partial(power, exponent=2)
print(square(5))  # 25

# 세제곱 함수
cube = partial(power, exponent=3)
print(cube(5))  # 125
```

### Tip 7: 클로저 활용

```python
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

times_3 = make_multiplier(3)
times_5 = make_multiplier(5)

print(times_3(10))  # 30
print(times_5(10))  # 50
```

### Tip 8: 제너레이터 함수

```python
def count_up_to(n):
    count = 1
    while count <= n:
        yield count
        count += 1

for num in count_up_to(5):
    print(num)  # 1, 2, 3, 4, 5
```

---

## 자주하는 실수

### 실수 1: 가변 기본값

```python
# 나쁜 예
def append_to(element, to=[]):
    to.append(element)
    return to

list1 = append_to(1)  # [1]
list2 = append_to(2)  # [1, 2] - 공유됨!

# 좋은 예
def append_to(element, to=None):
    if to is None:
        to = []
    to.append(element)
    return to
```

### 실수 2: 람다에서 변수 캡처

```python
# 나쁜 예
functions = []
for i in range(3):
    functions.append(lambda: i)

for f in functions:
    print(f())  # 2, 2, 2 (모두 마지막 값)

# 좋은 예
functions = []
for i in range(3):
    functions.append(lambda x=i: x)

for f in functions:
    print(f())  # 0, 1, 2
```

### 실수 3: 반환값 무시

```python
# 나쁜 예
def process_data(data):
    data.sort()  # 반환값 없음 (None)

result = process_data([3, 1, 2])
print(result)  # None

# 좋은 예
def process_data(data):
    return sorted(data)  # 새 리스트 반환

result = process_data([3, 1, 2])
print(result)  # [1, 2, 3]
```

### 실수 4: 전역 변수 수정

```python
count = 0

# 나쁜 예
def increment():
    count += 1  # UnboundLocalError!

# 좋은 예 1: global 사용
def increment():
    global count
    count += 1

# 좋은 예 2: 반환값 사용 (권장)
def increment(count):
    return count + 1

count = increment(count)
```

### 실수 5: 데코레이터에서 원본 함수 정보 손실

```python
# 나쁜 예
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet():
    """인사 함수"""
    pass

print(greet.__name__)  # wrapper

# 좋은 예
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet():
    """인사 함수"""
    pass

print(greet.__name__)  # greet
```

---

## 요약

| 개념       | 설명              | 예시                  |
|------------|-------------------|-----------------------|
| 함수 정의  | `def` 키워드 사용 | `def func():`         |
| 매개변수   | 함수 입력값       | `def func(a, b):`     |
| 반환값     | `return`으로 반환 | `return result`       |
| *args      | 가변 위치 인자    | `def func(*args):`    |
| **kwargs   | 가변 키워드 인자  | `def func(**kwargs):` |
| 람다       | 익명 함수         | `lambda x: x * 2`     |
| 데코레이터 | 함수 기능 확장    | `@decorator`          |

**핵심 포인트:**
- 함수는 한 가지 일만 수행
- 가변 기본값 사용 금지
- 타입 힌트와 docstring 작성
- 데코레이터로 기능 확장
- functools.wraps 사용

**관련 문서:**
- [클래스 튜토리얼](./python_class.md) - 메서드는 클래스 내부 함수
- [데코레이터](./python_decorators.md) - 데코레이터 심화
