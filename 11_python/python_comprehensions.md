# Python 컴프리헨션 (Comprehensions)

Python의 리스트, 딕셔너리, 집합 컴프리헨션과 제너레이터 표현식에 대한 완벽 가이드입니다.

## 목차
- [어원과 역사](#어원과-역사)
- [리스트 컴프리헨션](#리스트-컴프리헨션)
- [딕셔너리 컴프리헨션](#딕셔너리-컴프리헨션)
- [집합 컴프리헨션](#집합-컴프리헨션)
- [제너레이터 표현식](#제너레이터-표현식)
- [중첩 컴프리헨션](#중첩-컴프리헨션)
- [실전 예제](#실전-예제)
- [성능 비교](#성능-비교)
- [실전 팁](#실전-팁)

---

## 어원과 역사

**Comprehension**은 수학의 **집합 조건제시법(Set-builder notation)**에서 유래했습니다.

### 수학적 배경

```
수학 표기법:
S = {x² | x ∈ ℕ, x < 5}
"x가 자연수이고 5보다 작을 때, x의 제곱으로 이루어진 집합"

Python 표기법:
S = [x**2 for x in range(5)]
```

### 용어 설명

- **Comprehension**: "포괄", "이해", "내포"
- 수학에서 "집합을 조건으로 포괄적으로 정의한다"는 의미
- 프로그래밍에서는 "반복과 조건을 하나의 표현식으로 포괄한다"는 의미

### 역사

- **1990년대**: Haskell 등 함수형 언어에서 List Comprehension 개념 도입
- **2000년**: Python 2.0에서 리스트 컴프리헨션 추가 (PEP 202)
- **2003년**: Python 2.4에서 제너레이터 표현식 추가 (PEP 289)
- **2007년**: Python 3.0에서 딕셔너리/세트 컴프리헨션 추가 (PEP 274, PEP 3100)

---

## 리스트 컴프리헨션

### 기본 문법

```python
# 기본 형태
squares = [x**2 for x in range(5)]
print(squares)  # [0, 1, 4, 9, 16]

# 일반 for문과 비교
squares = []
for x in range(5):
    squares.append(x**2)
```

### 조건문 포함

```python
# if 조건 (필터링)
evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8]

# if-else (변환)
result = [x if x % 2 == 0 else -x for x in range(5)]
print(result)  # [0, -1, 2, -3, 4]

# 복수 조건
nums = [x for x in range(20) if x % 2 == 0 if x % 3 == 0]
print(nums)  # [0, 6, 12, 18]
```

### 문자열 처리

```python
# 대문자 변환
words = ["hello", "world", "python"]
upper = [w.upper() for w in words]
print(upper)  # ['HELLO', 'WORLD', 'PYTHON']

# 길이 필터링
long_words = [w for w in words if len(w) > 5]
print(long_words)  # ['python']

# 첫 글자만
initials = [w[0] for w in words]
print(initials)  # ['h', 'w', 'p']
```

### 중첩 리스트

```python
# 2차원 리스트 평탄화
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 조건 포함
even_flat = [num for row in matrix for num in row if num % 2 == 0]
print(even_flat)  # [2, 4, 6, 8]
```

---

## 딕셔너리 컴프리헨션

### 기본 문법

```python
# 기본 형태
squares = {x: x**2 for x in range(5)}
print(squares)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 일반 for문과 비교
squares = {}
for x in range(5):
    squares[x] = x**2
```

### 조건문 포함

```python
# 짝수만
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
print(even_squares)  # {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}

# 값 조건
positive = {x: x**2 for x in range(-5, 6) if x**2 > 10}
print(positive)  # {-5: 25, -4: 16, 4: 16, 5: 25}
```

### 딕셔너리 변환

```python
# 키-값 교환
original = {'a': 1, 'b': 2, 'c': 3}
swapped = {v: k for k, v in original.items()}
print(swapped)  # {1: 'a', 2: 'b', 3: 'c'}

# 값 변환
doubled = {k: v*2 for k, v in original.items()}
print(doubled)  # {'a': 2, 'b': 4, 'c': 6}

# 키 필터링
filtered = {k: v for k, v in original.items() if k != 'b'}
print(filtered)  # {'a': 1, 'c': 3}
```

### 리스트에서 딕셔너리 생성

```python
# 두 리스트 결합
keys = ['name', 'age', 'city']
values = ['홍길동', 30, '서울']
person = {k: v for k, v in zip(keys, values)}
print(person)  # {'name': '홍길동', 'age': 30, 'city': '서울'}

# enumerate 활용
words = ['apple', 'banana', 'cherry']
indexed = {i: word for i, word in enumerate(words)}
print(indexed)  # {0: 'apple', 1: 'banana', 2: 'cherry'}
```

---

## 집합 컴프리헨션

### 기본 문법

```python
# 기본 형태
squares = {x**2 for x in range(5)}
print(squares)  # {0, 1, 4, 9, 16}

# 중복 자동 제거
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = {x for x in numbers}
print(unique)  # {1, 2, 3, 4}
```

### 조건문 포함

```python
# 짝수만
evens = {x for x in range(10) if x % 2 == 0}
print(evens)  # {0, 2, 4, 6, 8}

# 문자열 길이
words = ['apple', 'banana', 'kiwi', 'pear']
lengths = {len(w) for w in words}
print(lengths)  # {4, 5, 6}
```

### 실용 예제

```python
# 고유 문자 추출
text = "hello world"
unique_chars = {c for c in text if c.isalpha()}
print(unique_chars)  # {'h', 'e', 'l', 'o', 'w', 'r', 'd'}

# 배수 찾기
multiples = {x for x in range(1, 51) if x % 3 == 0 or x % 5 == 0}
print(len(multiples))  # 23
```

---

## 제너레이터 표현식

### 기본 개념

```python
# 리스트 컴프리헨션 (메모리에 전체 저장)
squares_list = [x**2 for x in range(1000000)]

# 제너레이터 표현식 (필요할 때 생성)
squares_gen = (x**2 for x in range(1000000))

print(type(squares_list))  # <class 'list'>
print(type(squares_gen))   # <class 'generator'>
```

### 사용법

```python
# 순회
gen = (x**2 for x in range(5))
for num in gen:
    print(num)  # 0, 1, 4, 9, 16

# 한 번만 순회 가능
gen = (x**2 for x in range(3))
print(list(gen))  # [0, 1, 4]
print(list(gen))  # [] (이미 소진됨)
```

### 메모리 효율

```python
import sys

# 리스트 컴프리헨션
list_comp = [x for x in range(10000)]
print(sys.getsizeof(list_comp))  # ~85KB

# 제너레이터 표현식
gen_exp = (x for x in range(10000))
print(sys.getsizeof(gen_exp))    # ~128 bytes
```

### 함수와 함께 사용

```python
# sum
total = sum(x**2 for x in range(10))
print(total)  # 285

# max/min
maximum = max(x**2 for x in range(10))
print(maximum)  # 81

# any/all
has_even = any(x % 2 == 0 for x in range(5))
print(has_even)  # True
```

---

## 중첩 컴프리헨션

### 2차원 리스트 생성

```python
# 3x3 행렬
matrix = [[i*3 + j for j in range(3)] for i in range(3)]
print(matrix)
# [[0, 1, 2],
#  [3, 4, 5],
#  [6, 7, 8]]

# 체스판 패턴
board = [['B' if (i+j) % 2 == 0 else 'W' for j in range(8)] for i in range(8)]
```

### 행렬 전치

```python
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
print(transposed)
# [[1, 4],
#  [2, 5],
#  [3, 6]]
```

### 복잡한 중첩

```python
# 구구단
multiplication = [[f"{i}x{j}={i*j}" for j in range(1, 10)] for i in range(2, 10)]

# 조합 생성
pairs = [(x, y) for x in range(3) for y in range(3) if x != y]
print(pairs)
# [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
```

---

## 실전 예제

### 예제 1: 데이터 정제

```python
# CSV 데이터 파싱
data = "name:홍길동,age:30,city:서울"
parsed = {k: v for item in data.split(',') for k, v in [item.split(':')]}
print(parsed)  # {'name': '홍길동', 'age': '30', 'city': '서울'}

# 빈 값 제거
values = ['a', '', 'b', None, 'c', '']
cleaned = [v for v in values if v]
print(cleaned)  # ['a', 'b', 'c']
```

### 예제 2: 파일 처리

```python
# 파일명 필터링
files = ['doc.txt', 'image.png', 'data.csv', 'photo.jpg']
text_files = [f for f in files if f.endswith('.txt')]
images = [f for f in files if f.endswith(('.png', '.jpg'))]

# 확장자 추출
extensions = {f.split('.')[-1] for f in files}
print(extensions)  # {'txt', 'png', 'csv', 'jpg'}
```

### 예제 3: 통계 계산

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 기본 통계
stats = {
    'sum': sum(numbers),
    'avg': sum(numbers) / len(numbers),
    'max': max(numbers),
    'min': min(numbers)
}

# 조건별 개수
counts = {
    'even': sum(1 for n in numbers if n % 2 == 0),
    'odd': sum(1 for n in numbers if n % 2 == 1),
    'gt5': sum(1 for n in numbers if n > 5)
}
print(counts)  # {'even': 5, 'odd': 5, 'gt5': 5}
```

### 예제 4: 텍스트 분석

```python
text = "Python is powerful and Python is easy"

# 단어 빈도
words = text.lower().split()
freq = {word: words.count(word) for word in set(words)}
print(freq)  # {'python': 2, 'is': 2, 'powerful': 1, 'and': 1, 'easy': 1}

# 길이별 그룹화
by_length = {length: [w for w in words if len(w) == length] 
             for length in {len(w) for w in words}}
```

### 예제 5: 좌표 변환

```python
# 극좌표 -> 직교좌표
import math
polar = [(1, 0), (1, math.pi/2), (1, math.pi)]
cartesian = [(r*math.cos(theta), r*math.sin(theta)) for r, theta in polar]

# 거리 계산
points = [(0, 0), (3, 4), (1, 1)]
distances = [math.sqrt(x**2 + y**2) for x, y in points]
print(distances)  # [0.0, 5.0, 1.414...]
```

---

## 성능 비교

```python
import timeit

# 리스트 컴프리헨션 (빠름)
timeit.timeit('[x**2 for x in range(100)]', number=10000)

# 일반 for 루프 (느림)
timeit.timeit('''
result = []
for x in range(100):
    result.append(x**2)
''', number=10000)

# 리스트 컴프리헨션이 약 20-30% 빠름
```

---

## 실전 팁

### Tip 1: 가독성 우선

```python
# 나쁜 예 (너무 복잡)
result = [x for x in [y**2 for y in range(10) if y % 2 == 0] if x > 10]

# 좋은 예 (단계별 분리)
evens = [y for y in range(10) if y % 2 == 0]
squares = [x**2 for x in evens]
result = [x for x in squares if x > 10]
```

### Tip 2: 적절한 선택

```python
# 리스트 컴프리헨션: 전체 결과 필요
squares = [x**2 for x in range(10)]

# 제너레이터: 큰 데이터, 한 번만 순회
total = sum(x**2 for x in range(1000000))

# 일반 for문: 복잡한 로직
results = []
for x in range(10):
    if x % 2 == 0:
        results.append(x**2)
    else:
        results.append(-x)
```

### Tip 3: 조건문 위치

```python
# 필터링: if는 뒤에
evens = [x for x in range(10) if x % 2 == 0]

# 변환: if-else는 앞에
result = [x if x % 2 == 0 else -x for x in range(10)]

# 복수 필터: if 여러 개
nums = [x for x in range(20) if x % 2 == 0 if x % 3 == 0]
```

### Tip 4: 성능 고려

```python
# 나쁜 예 (중복 계산)
result = [expensive_func(x) for x in data if expensive_func(x) > 10]

# 좋은 예 (한 번만 계산)
result = [val for x in data if (val := expensive_func(x)) > 10]

# 또는 제너레이터 활용
values = (expensive_func(x) for x in data)
result = [v for v in values if v > 10]
```

### Tip 5: 중첩 순서 이해

```python
# 중첩 컴프리헨션 순서
result = [x*y for x in range(3) for y in range(3)]

# 동일한 일반 for문
result = []
for x in range(3):
    for y in range(3):
        result.append(x*y)

# 조건 포함 시
result = [x*y for x in range(3) for y in range(3) if x != y]
```

### Tip 6: dict.get() 활용

```python
# 기본값 있는 딕셔너리
data = [('a', 1), ('b', 2), ('a', 3)]
result = {}
for k, v in data:
    result[k] = result.get(k, 0) + v
print(result)  # {'a': 4, 'b': 2}

# 컴프리헨션으로는 어려움 (defaultdict 사용 권장)
```

### Tip 7: 언제 사용하지 말아야 할까

```python
# 부작용이 있는 경우 (나쁜 예)
[print(x) for x in range(5)]  # 리스트 생성은 불필요

# 좋은 예
for x in range(5):
    print(x)

# 너무 복잡한 경우 (나쁜 예)
result = [[y*2 if y > 5 else y for y in row if y % 2 == 0] 
          for row in matrix if sum(row) > 10]

# 좋은 예 (함수로 분리)
def process_row(row):
    return [y*2 if y > 5 else y for y in row if y % 2 == 0]

result = [process_row(row) for row in matrix if sum(row) > 10]
```

---

## 요약

| 타입 | 문법 | 결과 타입 | 메모리 |
|------|------|-----------|--------|
| 리스트 | `[x for x in ...]` | list | 전체 저장 |
| 딕셔너리 | `{k: v for ...}` | dict | 전체 저장 |
| 집합 | `{x for x in ...}` | set | 전체 저장 |
| 제너레이터 | `(x for x in ...)` | generator | 지연 평가 |

**핵심 포인트:**
- 간결하고 읽기 쉬운 코드 작성
- 조건문으로 필터링/변환
- 제너레이터로 메모리 효율 향상
- 복잡하면 일반 for문 사용
- 가독성이 최우선

**관련 문서:**
- [제어문](./python_control_flow.md) - 기본 반복문
- [함수](./python_functions.md) - 함수와 컴프리헨션 조합
