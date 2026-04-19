# Python 제너레이터 (Generators)

Python 제너레이터의 개념부터 실전 활용까지 다루는 완벽 가이드입니다.

## 목차
- [제너레이터란?](#제너레이터란)
- [yield 키워드](#yield-키워드)
- [이터레이터와 제너레이터](#이터레이터와-제너레이터)
- [제너레이터 표현식](#제너레이터-표현식)
- [고급 제너레이터](#고급-제너레이터)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)
- [요약](#요약)

---

## 제너레이터란?

값을 필요할 때마다 하나씩 생성하는 이터레이터를 만드는 함수입니다.

### 왜 사용하나?

- **메모리 효율**: 전체 데이터를 메모리에 저장하지 않음
- **지연 평가**: 필요할 때만 값 생성
- **무한 시퀀스**: 끝없는 데이터 스트림 처리
- **파이프라인**: 데이터 처리 단계 연결

### 일반 함수 vs 제너레이터

```python
# 일반 함수 (메모리에 전체 저장)
def get_numbers():
    result = []
    for i in range(5):
        result.append(i)
    return result

print(get_numbers())  # [0, 1, 2, 3, 4]

# 제너레이터 (필요할 때 생성)
def gen_numbers():
    for i in range(5):
        yield i

print(gen_numbers())  # <generator object>
print(list(gen_numbers()))  # [0, 1, 2, 3, 4]
```

---

## yield 키워드

### 기본 사용법

```python
def simple_gen():
    yield 1
    yield 2
    yield 3

gen = simple_gen()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
# print(next(gen))  # StopIteration 에러
```

### yield의 동작 원리

```python
def counter():
    print("시작")
    yield 1
    print("첫 번째 yield 이후")
    yield 2
    print("두 번째 yield 이후")
    yield 3
    print("끝")

gen = counter()
print(next(gen))  # 시작 -> 1
print(next(gen))  # 첫 번째 yield 이후 -> 2
print(next(gen))  # 두 번째 yield 이후 -> 3
# print(next(gen))  # 끝 -> StopIteration
```

### for 문과 함께 사용

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for num in countdown(5):
    print(num)  # 5, 4, 3, 2, 1
```

### yield vs return

```python
# return: 함수 종료
def with_return():
    return 1
    return 2  # 실행 안 됨

# yield: 일시 중지 후 재개
def with_yield():
    yield 1
    yield 2  # 실행됨

print(with_return())  # 1
print(list(with_yield()))  # [1, 2]
```

---

## 이터레이터와 제너레이터

### 이터레이터 프로토콜

```python
# 이터레이터 클래스
class Counter:
    def __init__(self, max):
        self.max = max
        self.current = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current < self.max:
            self.current += 1
            return self.current
        raise StopIteration

counter = Counter(3)
print(list(counter))  # [1, 2, 3]
```

### 제너레이터로 간단히

```python
# 동일한 기능을 제너레이터로
def counter(max):
    current = 0
    while current < max:
        current += 1
        yield current

print(list(counter(3)))  # [1, 2, 3]
```

### iter()와 next()

```python
# 리스트는 이터러블
numbers = [1, 2, 3]
iterator = iter(numbers)
print(next(iterator))  # 1
print(next(iterator))  # 2

# 제너레이터는 이터레이터
gen = (x for x in range(3))
print(next(gen))  # 0
print(next(gen))  # 1
```

### 이터러블 vs 이터레이터

```python
# 이터러블: __iter__() 있음
numbers = [1, 2, 3]
for n in numbers:
    print(n)
for n in numbers:  # 다시 순회 가능
    print(n)

# 이터레이터: __iter__()와 __next__() 있음
gen = (x for x in range(3))
for n in gen:
    print(n)
for n in gen:  # 빈 결과 (이미 소진)
    print(n)
```

---

## 제너레이터 표현식

### 기본 문법

```python
# 리스트 컴프리헨션
squares_list = [x**2 for x in range(5)]

# 제너레이터 표현식 (괄호 사용)
squares_gen = (x**2 for x in range(5))

print(type(squares_list))  # <class 'list'>
print(type(squares_gen))   # <class 'generator'>
```

### 메모리 비교

```python
import sys

# 큰 데이터셋
list_comp = [x for x in range(1000000)]
gen_exp = (x for x in range(1000000))

print(sys.getsizeof(list_comp))  # ~8MB
print(sys.getsizeof(gen_exp))    # ~128 bytes
```

### 함수 인자로 사용

```python
# 괄호 생략 가능
total = sum(x**2 for x in range(10))
print(total)  # 285

# 최댓값
maximum = max(x**2 for x in range(10))
print(maximum)  # 81

# 조건 검사
has_even = any(x % 2 == 0 for x in range(5))
print(has_even)  # True

all_positive = all(x > 0 for x in range(1, 5))
print(all_positive)  # True
```

### 조건문 포함

```python
# 필터링
evens = (x for x in range(10) if x % 2 == 0)
print(list(evens))  # [0, 2, 4, 6, 8]

# 변환
result = (x if x % 2 == 0 else -x for x in range(5))
print(list(result))  # [0, -1, 2, -3, 4]
```

---

## 고급 제너레이터

### yield from

```python
# 중첩 제너레이터
def gen1():
    yield 1
    yield 2

def gen2():
    yield 3
    yield 4

def combined():
    yield from gen1()
    yield from gen2()

print(list(combined()))  # [1, 2, 3, 4]

# 리스트도 가능
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

nested = [1, [2, 3, [4, 5]], 6]
print(list(flatten(nested)))  # [1, 2, 3, 4, 5, 6]
```

### send() 메서드

```python
def echo():
    while True:
        value = yield
        if value is not None:
            print(f"받은 값: {value}")

gen = echo()
next(gen)  # 제너레이터 시작
gen.send(10)  # 받은 값: 10
gen.send(20)  # 받은 값: 20
```

### 양방향 통신

```python
def running_average():
    total = 0
    count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count

avg = running_average()
next(avg)  # 시작
print(avg.send(10))  # 10.0
print(avg.send(20))  # 15.0
print(avg.send(30))  # 20.0
```

### close()와 throw()

```python
def gen_with_cleanup():
    try:
        yield 1
        yield 2
        yield 3
    finally:
        print("정리 작업")

gen = gen_with_cleanup()
print(next(gen))  # 1
gen.close()  # 정리 작업

# 예외 전달
def gen_with_error():
    try:
        yield 1
        yield 2
    except ValueError:
        print("ValueError 처리")

gen = gen_with_error()
print(next(gen))  # 1
gen.throw(ValueError)  # ValueError 처리
```

---

## 실전 예제

### 예제 1: 파일 읽기

```python
# 메모리 효율적인 파일 읽기
def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.strip()

# 사용
for line in read_large_file('large.txt'):
    if 'ERROR' in line:
        print(line)

# 특정 조건만
def filter_lines(file_path, keyword):
    for line in read_large_file(file_path):
        if keyword in line:
            yield line
```

### 예제 2: 무한 시퀀스

```python
# 무한 카운터
def infinite_counter(start=0):
    while True:
        yield start
        start += 1

# 처음 10개만
counter = infinite_counter()
first_ten = [next(counter) for _ in range(10)]
print(first_ten)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 피보나치 수열
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
print([next(fib) for _ in range(10)])
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 예제 3: 데이터 파이프라인

```python
# 단계별 처리
def read_data():
    for i in range(10):
        yield i

def filter_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n

def square(numbers):
    for n in numbers:
        yield n ** 2

# 파이프라인 구성
pipeline = square(filter_even(read_data()))
print(list(pipeline))  # [0, 4, 16, 36, 64]
```

### 예제 4: 배치 처리

```python
def batch(iterable, size):
    batch_data = []
    for item in iterable:
        batch_data.append(item)
        if len(batch_data) == size:
            yield batch_data
            batch_data = []
    if batch_data:
        yield batch_data

# 사용
data = range(10)
for batch_data in batch(data, 3):
    print(batch_data)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]
```

### 예제 5: 윈도우 슬라이딩

```python
def sliding_window(iterable, size):
    from collections import deque
    window = deque(maxlen=size)
    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield list(window)

# 사용
data = [1, 2, 3, 4, 5]
for window in sliding_window(data, 3):
    print(window)
# [1, 2, 3]
# [2, 3, 4]
# [3, 4, 5]
```

### 예제 6: 트리 순회

```python
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

def traverse(node):
    yield node.value
    for child in node.children:
        yield from traverse(child)

# 사용
tree = Node(1, [
    Node(2, [Node(4), Node(5)]),
    Node(3, [Node(6)])
])

print(list(traverse(tree)))  # [1, 2, 4, 5, 3, 6]
```

### 예제 7: 로그 파싱

```python
def parse_logs(file_path):
    with open(file_path) as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) == 3:
                timestamp, level, message = parts
                yield {
                    'timestamp': timestamp,
                    'level': level,
                    'message': message
                }

def filter_errors(logs):
    for log in logs:
        if log['level'] == 'ERROR':
            yield log

# 사용
errors = filter_errors(parse_logs('app.log'))
for error in errors:
    print(error['message'])
```

### 예제 8: 페이지네이션

```python
def paginate(items, page_size):
    items = list(items)
    for i in range(0, len(items), page_size):
        yield items[i:i + page_size]

# API 페이지네이션
def fetch_all_pages(api_url):
    page = 1
    while True:
        response = fetch_page(api_url, page)
        if not response:
            break
        yield from response
        page += 1

def fetch_page(url, page):
    # API 호출 시뮬레이션
    if page > 3:
        return []
    return [f"item_{page}_{i}" for i in range(5)]

print(list(fetch_all_pages('api.com')))
```

---

## 실전 팁

### Tip 1: 언제 제너레이터를 사용할까

```python
# 사용하기 좋은 경우
# 1. 큰 데이터셋
def read_big_file(path):
    with open(path) as f:
        for line in f:
            yield line

# 2. 무한 시퀀스
def infinite_sequence():
    n = 0
    while True:
        yield n
        n += 1

# 3. 파이프라인
def process_data(data):
    for item in data:
        yield transform(item)

# 사용하지 말아야 할 경우
# 1. 여러 번 순회 필요
# 2. 랜덤 액세스 필요
# 3. 전체 크기 필요
```

### Tip 2: 제너레이터 재사용

```python
# 나쁜 예 (한 번만 사용 가능)
gen = (x for x in range(5))
print(list(gen))  # [0, 1, 2, 3, 4]
print(list(gen))  # []

# 좋은 예 (함수로 감싸기)
def make_gen():
    return (x for x in range(5))

print(list(make_gen()))  # [0, 1, 2, 3, 4]
print(list(make_gen()))  # [0, 1, 2, 3, 4]
```

### Tip 3: 조기 종료

```python
def find_first(iterable, condition):
    for item in iterable:
        if condition(item):
            return item
    return None

# 제너레이터는 자동으로 정리됨
def expensive_gen():
    for i in range(1000000):
        yield i

result = find_first(expensive_gen(), lambda x: x > 100)
print(result)  # 101 (나머지는 생성 안 됨)
```

### Tip 4: itertools 활용

```python
from itertools import islice, chain, cycle

# 처음 n개
gen = (x for x in range(100))
first_five = list(islice(gen, 5))
print(first_five)  # [0, 1, 2, 3, 4]

# 여러 제너레이터 연결
gen1 = (x for x in range(3))
gen2 = (x for x in range(3, 6))
combined = chain(gen1, gen2)
print(list(combined))  # [0, 1, 2, 3, 4, 5]

# 무한 반복
counter = cycle([1, 2, 3])
print(list(islice(counter, 7)))  # [1, 2, 3, 1, 2, 3, 1]
```

### Tip 5: 제너레이터 체이닝

```python
# 여러 단계 연결
def numbers():
    for i in range(10):
        yield i

def filter_even(gen):
    for n in gen:
        if n % 2 == 0:
            yield n

def square(gen):
    for n in gen:
        yield n ** 2

# 체인 구성
result = square(filter_even(numbers()))
print(list(result))  # [0, 4, 16, 36, 64]

# 또는 함수로
def process():
    return square(filter_even(numbers()))
```

### Tip 6: 상태 유지

```python
def stateful_gen():
    state = {'count': 0}
    
    def inner():
        while True:
            state['count'] += 1
            yield state['count']
    
    return inner()

gen = stateful_gen()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
```

### Tip 7: 예외 처리

```python
def safe_gen(iterable):
    for item in iterable:
        try:
            yield process(item)
        except Exception as e:
            print(f"에러 발생: {e}")
            continue

def process(item):
    if item < 0:
        raise ValueError("음수 불가")
    return item * 2

data = [1, -2, 3, -4, 5]
print(list(safe_gen(data)))
# 에러 발생: 음수 불가
# 에러 발생: 음수 불가
# [2, 6, 10]
```

### Tip 8: 성능 측정

```python
import time

def measure_gen():
    start = time.time()
    gen = (x**2 for x in range(1000000))
    print(f"생성 시간: {time.time() - start:.6f}초")
    
    start = time.time()
    result = list(gen)
    print(f"소비 시간: {time.time() - start:.6f}초")

measure_gen()
# 생성 시간: 0.000002초 (즉시)
# 소비 시간: 0.15초 (실제 계산)
```

---

## 자주하는 실수

### 실수 1: 제너레이터 재사용

```python
# 나쁜 예
gen = (x for x in range(5))
print(sum(gen))  # 10
print(sum(gen))  # 0 (이미 소진)

# 좋은 예
def make_gen():
    return (x for x in range(5))

print(sum(make_gen()))  # 10
print(sum(make_gen()))  # 10
```

### 실수 2: 리스트로 변환 후 순회

```python
# 나쁜 예 (메모리 낭비)
gen = (x**2 for x in range(1000000))
data = list(gen)
for item in data:
    process(item)

# 좋은 예
gen = (x**2 for x in range(1000000))
for item in gen:
    process(item)
```

### 실수 3: yield 위치

```python
# 나쁜 예
def bad_gen():
    result = []
    for i in range(5):
        result.append(i)
    yield result  # 리스트 하나만 반환

# 좋은 예
def good_gen():
    for i in range(5):
        yield i  # 값을 하나씩 반환
```

### 실수 4: 부작용 있는 제너레이터

```python
# 나쁜 예
def bad_gen():
    for i in range(5):
        print(i)  # 부작용
        yield i

# 좋은 예
def good_gen():
    for i in range(5):
        yield i

for item in good_gen():
    print(item)  # 사용하는 쪽에서 처리
```

### 실수 5: 제너레이터 길이 확인

```python
# 나쁜 예
gen = (x for x in range(5))
# length = len(gen)  # TypeError

# 좋은 예
data = list(range(5))
length = len(data)

# 또는 카운트
gen = (x for x in range(5))
count = sum(1 for _ in gen)
```

---

## 요약

| 특징 | 일반 함수 | 제너레이터 |
|------|-----------|------------|
| 반환 | return | yield |
| 메모리 | 전체 저장 | 필요시 생성 |
| 재사용 | 가능 | 한 번만 |
| 상태 | 없음 | 유지됨 |

**핵심 포인트:**
- yield로 값을 하나씩 생성
- 메모리 효율적인 데이터 처리
- 무한 시퀀스와 파이프라인 구현
- 한 번만 순회 가능 (재사용 불가)
- 지연 평가로 성능 향상

**관련 문서:**
- [컴프리헨션](./python_comprehensions.md) - 제너레이터 표현식
- [함수](./python_functions.md) - 함수 기초
- [이터레이터](./python_iterators.md) - 이터레이터 프로토콜
