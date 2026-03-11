# Python 데코레이터 (Decorators)

Python 데코레이터의 개념부터 고급 활용까지 다루는 완벽 가이드입니다.

## 목차
- [데코레이터란?](#데코레이터란)
- [함수 데코레이터](#함수-데코레이터)
- [클래스 데코레이터](#클래스-데코레이터)
- [매개변수 있는 데코레이터](#매개변수-있는-데코레이터)
- [functools 활용](#functools-활용)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)

---

## 데코레이터란?

함수나 클래스를 수정하지 않고 기능을 추가하는 디자인 패턴입니다.

### 왜 사용하나?

- **코드 재사용**: 공통 기능을 여러 함수에 적용
- **관심사 분리**: 핵심 로직과 부가 기능 분리
- **가독성**: 깔끔한 코드 작성
- **유지보수**: 기능 추가/제거 용이

### 기본 개념

```python
# 데코레이터 없이
def say_hello():
    print("안녕하세요!")

say_hello = my_decorator(say_hello)

# 데코레이터 사용 (@)
@my_decorator
def say_hello():
    print("안녕하세요!")
```

---

## 함수 데코레이터

### 기본 함수 데코레이터

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
        print(f"반환값: {result}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

result = add(3, 5)
# 함수 호출: add
# 반환값: 8
```

### 실행 시간 측정

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

### 로깅 데코레이터

```python
import logging

logging.basicConfig(level=logging.INFO)

def log_calls(func):
    def wrapper(*args, **kwargs):
        logging.info(f"호출: {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        logging.info(f"반환: {result}")
        return result
    return wrapper

@log_calls
def multiply(a, b):
    return a * b

multiply(3, 5)
# INFO:root:호출: multiply((3, 5), {})
# INFO:root:반환: 15
```

### 예외 처리 데코레이터

```python
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"에러 발생: {e}")
            return None
    return wrapper

@handle_errors
def divide(a, b):
    return a / b

print(divide(10, 2))  # 5.0
print(divide(10, 0))  # 에러 발생: division by zero
```

### 재시도 데코레이터

```python
import time

def retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"시도 {attempt + 1} 실패: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unstable_function():
    import random
    if random.random() < 0.7:
        raise ValueError("실패!")
    return "성공!"
```

---

## 클래스 데코레이터

### 클래스를 데코레이터로 사용

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"호출 횟수: {self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("안녕하세요!")

say_hello()  # 호출 횟수: 1
say_hello()  # 호출 횟수: 2
```

### 클래스 데코레이팅

```python
def add_str_method(cls):
    def __str__(self):
        return f"{cls.__name__} 인스턴스"
    cls.__str__ = __str__
    return cls

@add_str_method
class MyClass:
    pass

obj = MyClass()
print(obj)  # MyClass 인스턴스
```

### 싱글톤 패턴

```python
def singleton(cls):
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class Database:
    def __init__(self):
        print("데이터베이스 연결")

db1 = Database()  # 데이터베이스 연결
db2 = Database()  # 출력 없음
print(db1 is db2)  # True
```

### 속성 추가 데코레이터

```python
def add_timestamp(cls):
    import time
    cls.created_at = time.time()
    return cls

@add_timestamp
class User:
    def __init__(self, name):
        self.name = name

user = User("홍길동")
print(user.created_at)  # 1234567890.123
```

---

## 매개변수 있는 데코레이터

### 반복 실행 데코레이터

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

### 권한 검사 데코레이터

```python
def require_permission(permission):
    def decorator(func):
        def wrapper(user, *args, **kwargs):
            if permission not in user.get("permissions", []):
                raise PermissionError(f"{permission} 권한 필요")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@require_permission("admin")
def delete_user(user, user_id):
    print(f"사용자 {user_id} 삭제")

admin = {"name": "관리자", "permissions": ["admin"]}
user = {"name": "사용자", "permissions": ["read"]}

delete_user(admin, 123)  # 사용자 123 삭제
# delete_user(user, 123)  # PermissionError!
```

### 캐시 크기 제한

```python
def cache_with_limit(max_size):
    def decorator(func):
        cache = {}
        
        def wrapper(*args):
            if args in cache:
                return cache[args]
            
            if len(cache) >= max_size:
                cache.pop(next(iter(cache)))
            
            result = func(*args)
            cache[args] = result
            return result
        
        return wrapper
    return decorator

@cache_with_limit(max_size=3)
def expensive_operation(n):
    print(f"계산: {n}")
    return n * n

expensive_operation(1)  # 계산: 1
expensive_operation(2)  # 계산: 2
expensive_operation(1)  # 캐시 사용
```

### 타입 검사 데코레이터

```python
def validate_types(**expected_types):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg_name, expected_type in expected_types.items():
                if arg_name in kwargs:
                    value = kwargs[arg_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{arg_name}은(는) {expected_type} 타입이어야 합니다"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}

create_user(name="홍길동", age=30)  # OK
# create_user(name="홍길동", age="30")  # TypeError!
```

---

## functools 활용

### functools.wraps

원본 함수의 메타데이터를 보존합니다.

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """래퍼 함수"""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """인사 함수"""
    return f"안녕, {name}!"

print(greet.__name__)  # greet (wraps 없으면 wrapper)
print(greet.__doc__)   # 인사 함수
```

### functools.lru_cache

자동 메모이제이션을 제공합니다.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # 빠르게 계산
print(fibonacci.cache_info())  # CacheInfo(hits=98, misses=101, ...)
```

### functools.cache (Python 3.9+)

무제한 캐시를 제공합니다.

```python
from functools import cache

@cache
def factorial(n):
    return n * factorial(n-1) if n else 1

print(factorial(10))  # 3628800
```

### functools.partial

부분 함수를 생성합니다.

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125
```

### functools.singledispatch

타입별 함수 오버로딩을 제공합니다.

```python
from functools import singledispatch

@singledispatch
def process(data):
    raise NotImplementedError("지원하지 않는 타입")

@process.register(int)
def _(data):
    return data * 2

@process.register(str)
def _(data):
    return data.upper()

@process.register(list)
def _(data):
    return len(data)

print(process(5))           # 10
print(process("hello"))     # HELLO
print(process([1, 2, 3]))   # 3
```

---

## 실전 예제

### 예제 1: API 속도 제한

```python
import time
from functools import wraps

def rate_limit(max_calls, period):
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                raise Exception(f"{period}초당 {max_calls}회 제한 초과")
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@rate_limit(max_calls=3, period=10)
def api_call():
    print("API 호출")

for i in range(5):
    try:
        api_call()
    except Exception as e:
        print(f"에러: {e}")
```

### 예제 2: 디버깅 데코레이터

```python
from functools import wraps
import inspect

def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        print(f"\n호출: {func.__name__}")
        for name, value in bound.arguments.items():
            print(f"  {name} = {value!r}")
        
        result = func(*args, **kwargs)
        print(f"반환: {result!r}")
        return result
    
    return wrapper

@debug
def calculate(x, y, operation="add"):
    if operation == "add":
        return x + y
    return x - y

calculate(5, 3)
# 호출: calculate
#   x = 5
#   y = 3
#   operation = 'add'
# 반환: 8
```

### 예제 3: 비동기 재시도

```python
import asyncio
from functools import wraps

def async_retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"시도 {attempt + 1} 실패: {e}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

@async_retry(max_attempts=3, delay=0.5)
async def fetch_data(url):
    # 네트워크 요청 시뮬레이션
    import random
    if random.random() < 0.7:
        raise ConnectionError("연결 실패")
    return f"데이터: {url}"

# asyncio.run(fetch_data("https://api.example.com"))
```

### 예제 4: 성능 프로파일링

```python
import time
from functools import wraps
from collections import defaultdict

class Profiler:
    stats = defaultdict(lambda: {"calls": 0, "total_time": 0})
    
    @classmethod
    def profile(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            cls.stats[func.__name__]["calls"] += 1
            cls.stats[func.__name__]["total_time"] += elapsed
            
            return result
        return wrapper
    
    @classmethod
    def report(cls):
        print("\n=== 성능 리포트 ===")
        for name, data in cls.stats.items():
            avg = data["total_time"] / data["calls"]
            print(f"{name}:")
            print(f"  호출: {data['calls']}회")
            print(f"  총 시간: {data['total_time']:.4f}초")
            print(f"  평균: {avg:.4f}초")

@Profiler.profile
def slow_function():
    time.sleep(0.1)

@Profiler.profile
def fast_function():
    time.sleep(0.01)

for _ in range(5):
    slow_function()
    fast_function()

Profiler.report()
```

### 예제 5: 메모이제이션 (수동 구현)

```python
from functools import wraps

def memoize(func):
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))
print(f"캐시 크기: {len(fibonacci.cache)}")
fibonacci.cache_clear()
```

### 예제 6: 컨텍스트 주입

```python
from functools import wraps
from contextvars import ContextVar

request_id = ContextVar("request_id", default=None)

def with_request_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import uuid
        token = request_id.set(str(uuid.uuid4())[:8])
        try:
            return func(*args, **kwargs)
        finally:
            request_id.reset(token)
    return wrapper

def log(message):
    rid = request_id.get()
    print(f"[{rid}] {message}")

@with_request_id
def process_request():
    log("요청 시작")
    log("처리 중...")
    log("요청 완료")

process_request()
# [a1b2c3d4] 요청 시작
# [a1b2c3d4] 처리 중...
# [a1b2c3d4] 요청 완료
```

---

## 실전 팁

### Tip 1: 여러 데코레이터 순서

```python
@decorator1
@decorator2
@decorator3
def func():
    pass

# 실행 순서: decorator1(decorator2(decorator3(func)))
# 안쪽부터 바깥쪽으로 적용
```

### Tip 2: 데코레이터 체이닝

```python
def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def greet(name):
    return f"안녕, {name}!"

print(greet("홍길동"))
# <b><i>안녕, 홍길동!</i></b>
```

### Tip 3: 조건부 데코레이터

```python
def conditional_decorator(condition):
    def decorator(func):
        if condition:
            @wraps(func)
            def wrapper(*args, **kwargs):
                print("데코레이터 활성화")
                return func(*args, **kwargs)
            return wrapper
        return func
    return decorator

DEBUG = True

@conditional_decorator(DEBUG)
def process():
    print("처리 중")

process()
# 데코레이터 활성화
# 처리 중
```

### Tip 4: 데코레이터 매개변수 기본값

```python
def smart_decorator(func=None, *, param="default"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(f"매개변수: {param}")
            return f(*args, **kwargs)
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

# 매개변수 없이 사용
@smart_decorator
def func1():
    pass

# 매개변수와 함께 사용
@smart_decorator(param="custom")
def func2():
    pass
```

### Tip 5: 클래스 메서드 데코레이팅

```python
from functools import wraps

def method_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"메서드 호출: {func.__name__}")
        return func(self, *args, **kwargs)
    return wrapper

class MyClass:
    @method_decorator
    def method(self):
        print("메서드 실행")

obj = MyClass()
obj.method()
# 메서드 호출: method
# 메서드 실행
```

### Tip 6: 데코레이터 비활성화

```python
def optional_decorator(enabled=True):
    def decorator(func):
        if not enabled:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("데코레이터 실행")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@optional_decorator(enabled=False)
def my_function():
    print("함수 실행")

my_function()  # 함수 실행 (데코레이터 무시)
```

### Tip 7: 데코레이터 상태 관리

```python
class StatefulDecorator:
    def __init__(self, func):
        self.func = func
        self.calls = 0
        self.errors = 0
    
    def __call__(self, *args, **kwargs):
        self.calls += 1
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            self.errors += 1
            raise
    
    def stats(self):
        return {
            "calls": self.calls,
            "errors": self.errors,
            "success_rate": (self.calls - self.errors) / self.calls
        }

@StatefulDecorator
def risky_function(x):
    if x < 0:
        raise ValueError("음수 불가")
    return x * 2

risky_function(5)
try:
    risky_function(-1)
except ValueError:
    pass

print(risky_function.stats())
# {'calls': 2, 'errors': 1, 'success_rate': 0.5}
```

### Tip 8: 데코레이터 합성

```python
from functools import wraps

def compose(*decorators):
    def decorator(func):
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"시간: {time.time() - start:.4f}초")
        return result
    return wrapper

def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"호출: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@compose(timer, logger)
def process():
    import time
    time.sleep(0.1)

process()
# 호출: process
# 시간: 0.1001초
```

---

## 자주하는 실수

### 실수 1: functools.wraps 누락

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
print(greet.__doc__)   # None

# 좋은 예
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### 실수 2: 매개변수 데코레이터 구조 오류

```python
# 나쁜 예
def repeat(times):
    def wrapper(*args, **kwargs):
        for _ in range(times):
            func(*args, **kwargs)  # func가 정의되지 않음!
    return wrapper

# 좋은 예
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

### 실수 3: 반환값 무시

```python
# 나쁜 예
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("실행 전")
        func(*args, **kwargs)  # 반환값 무시!
        print("실행 후")
    return wrapper

# 좋은 예
def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("실행 전")
        result = func(*args, **kwargs)
        print("실행 후")
        return result
    return wrapper
```

### 실수 4: 클래스 데코레이터에서 self 누락

```python
# 나쁜 예
def method_decorator(func):
    def wrapper(*args, **kwargs):
        print("메서드 호출")
        return func(*args, **kwargs)  # self가 args에 포함됨
    return wrapper

class MyClass:
    @method_decorator
    def method(self):
        print(self)  # 정상 작동하지만 명시적이지 않음

# 좋은 예
def method_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print("메서드 호출")
        return func(self, *args, **kwargs)
    return wrapper
```

### 실수 5: 가변 객체를 데코레이터 기본값으로

```python
# 나쁜 예
def cache_decorator(func, cache={}):  # 위험!
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

# 좋은 예
def cache_decorator(func):
    cache = {}  # 함수 내부에서 생성
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper
```

### 실수 6: 데코레이터 순서 혼동

```python
# 잘못된 이해
@timer
@cache
def expensive_function(n):
    # timer가 먼저 실행된다고 착각
    pass

# 실제: cache(timer(expensive_function))
# cache가 안쪽, timer가 바깥쪽
# 캐시된 결과도 타이머에 포함됨

# 올바른 순서
@cache
@timer
def expensive_function(n):
    # timer(cache(expensive_function))
    # 실제 계산 시간만 측정
    pass
```

---

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 함수 데코레이터 | 함수에 기능 추가 | `@decorator` |
| 클래스 데코레이터 | 클래스에 기능 추가 | `@add_method` |
| 매개변수 데코레이터 | 설정 가능한 데코레이터 | `@repeat(3)` |
| functools.wraps | 메타데이터 보존 | `@wraps(func)` |
| lru_cache | 자동 캐싱 | `@lru_cache` |
| singledispatch | 타입별 오버로딩 | `@singledispatch` |

**핵심 포인트:**
- functools.wraps 항상 사용
- 반환값 잊지 말고 전달
- 데코레이터 순서 주의
- 클래스 데코레이터로 상태 관리
- lru_cache로 성능 최적화

**관련 문서:**
- [함수 튜토리얼](./python_functions.md) - 함수 기초
- [클래스 튜토리얼](./python_class.md) - 클래스 데코레이터
