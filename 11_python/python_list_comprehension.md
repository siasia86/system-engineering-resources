# Python 리스트 컴프리헨션 (List Comprehension)

리스트를 간결하게 생성하는 Python 문법입니다.

## 정의

리스트 컴프리헨션은 기존 반복 가능한 객체(iterable)로부터 새로운 리스트를 생성하는 간결한 표현식입니다. 
for 루프와 조건문을 한 줄로 압축하여 가독성과 성능을 동시에 향상시킵니다.

## 어원 (Etymology)

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

## 기본 문법

```python
[표현식 for 변수 in 반복가능객체]
```

## 기본 사용법

### 일반 for 루프 vs 리스트 컴프리헨션

```python
# 일반 for 루프
result = []
for i in range(5):
    result.append(i * 2)
print(result)  # [0, 2, 4, 6, 8]

# 리스트 컴프리헨션
result = [i * 2 for i in range(5)]
print(result)  # [0, 2, 4, 6, 8]
```

### 기본 예시

```python
# 제곱 리스트
squares = [x**2 for x in range(5)]
# [0, 1, 4, 9, 16]

# 문자열 대문자 변환
words = ['hello', 'world']
upper = [word.upper() for word in words]
# ['HELLO', 'WORLD']

# 숫자 2배
numbers = [1, 2, 3, 4, 5]
doubled = [n * 2 for n in numbers]
# [2, 4, 6, 8, 10]
```

## 조건문 추가

### if 조건 (필터링)

```python
[표현식 for 변수 in 반복가능객체 if 조건]
```

```python
# 짝수만 필터링
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# 양수만 필터링
numbers = [-2, -1, 0, 1, 2]
positives = [n for n in numbers if n > 0]
# [1, 2]

# 길이 5 이상인 단어만
words = ['hi', 'hello', 'world', 'python']
long_words = [w for w in words if len(w) >= 5]
# ['hello', 'world', 'python']
```

### if-else (값 변환)

```python
[표현식1 if 조건 else 표현식2 for 변수 in 반복가능객체]
```

```python
# 짝수는 그대로, 홀수는 0
result = [x if x % 2 == 0 else 0 for x in range(5)]
# [0, 0, 2, 0, 4]

# 양수는 그대로, 음수는 0
numbers = [-2, -1, 0, 1, 2]
result = [n if n > 0 else 0 for n in numbers]
# [0, 0, 0, 1, 2]

# 짝수는 'even', 홀수는 'odd'
labels = ['even' if x % 2 == 0 else 'odd' for x in range(5)]
# ['even', 'odd', 'even', 'odd', 'even']
```

## 중첩 루프

```python
# 일반 for 루프
result = []
for i in range(3):
    for j in range(2):
        result.append((i, j))
# [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]

# 리스트 컴프리헨션
result = [(i, j) for i in range(3) for j in range(2)]
# [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]

# 구구단
multiplication = [f"{i}x{j}={i*j}" for i in range(2, 4) for j in range(1, 4)]
# ['2x1=2', '2x2=4', '2x3=6', '3x1=3', '3x2=6', '3x3=9']

# 2차원 리스트 평탄화
nested = [[1, 2], [3, 4], [5, 6]]
flat = [num for sublist in nested for num in sublist]
# [1, 2, 3, 4, 5, 6]
```

## 다른 컴프리헨션

### 딕셔너리 컴프리헨션

```python
# 기본
squares_dict = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 키-값 뒤집기
original = {'a': 1, 'b': 2, 'c': 3}
reversed_dict = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}

# 조건 포함
numbers = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
evens = {k: v for k, v in numbers.items() if v % 2 == 0}
# {'b': 2, 'd': 4}
```

### 세트 컴프리헨션

```python
# 중복 제거
unique_lengths = {len(word) for word in ['hi', 'hello', 'hey', 'hi']}
# {2, 5, 3}

# 제곱 (중복 자동 제거)
squares = {x**2 for x in [-2, -1, 0, 1, 2]}
# {0, 1, 4}
```

### 제너레이터 표현식

```python
# 괄호 사용 (메모리 효율적, 한 번만 순회 가능)
gen = (x**2 for x in range(5))
print(list(gen))  # [0, 1, 4, 9, 16]

# 큰 데이터 처리 시 유용
sum_of_squares = sum(x**2 for x in range(1000000))
```

## 실전 예시

```python
# 파일 확장자 추출
files = ['data.txt', 'image.png', 'script.py', 'doc.pdf']
extensions = [f.split('.')[-1] for f in files]
# ['txt', 'png', 'py', 'pdf']

# 문자열에서 숫자만 추출
text = "abc123def456"
digits = [c for c in text if c.isdigit()]
# ['1', '2', '3', '4', '5', '6']

# 리스트에서 None 제거
data = [1, None, 2, None, 3]
cleaned = [x for x in data if x is not None]
# [1, 2, 3]

# 중첩 리스트 평탄화
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 좌표 생성
coordinates = [(x, y) for x in range(3) for y in range(3)]
# [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]

# 파일명 생성
filenames = [f"file_{i:03d}.txt" for i in range(5)]
# ['file_000.txt', 'file_001.txt', 'file_002.txt', 'file_003.txt', 'file_004.txt']
```

## 부작용 활용 (비권장이지만 가능)

```python
import time

# print는 None을 반환하므로, or로 다음 표현식 실행
[print(i) or time.sleep(1) for i in range(3)]
# 0 출력 → 1초 대기 → 1 출력 → 1초 대기 → 2 출력 → 1초 대기
# 결과 리스트: [None, None, None]

# 더 명확한 방법 (권장)
for i in range(3):
    print(i)
    time.sleep(1)
```

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

## 언제 사용하지 말아야 하나?

```python
# ❌ 너무 복잡하면 가독성 떨어짐
result = [x*y if x % 2 == 0 else x+y for x in range(10) for y in range(10) if x != y and x > 5]

# ✅ 일반 for 루프가 더 명확
result = []
for x in range(10):
    if x > 5:
        for y in range(10):
            if x != y:
                if x % 2 == 0:
                    result.append(x * y)
                else:
                    result.append(x + y)
```

## 빠른 참조

```python
# 기본
[x for x in items]

# 변환
[x * 2 for x in items]

# 필터링
[x for x in items if x > 0]

# 변환 + 필터링
[x * 2 for x in items if x > 0]

# if-else
[x if x > 0 else 0 for x in items]

# 중첩
[(x, y) for x in range(3) for y in range(3)]

# 딕셔너리
{k: v for k, v in items}

# 세트
{x for x in items}

# 제너레이터
(x for x in items)
```

## 핵심 정리

- 리스트를 한 줄로 간결하게 생성
- for 루프보다 빠르고 Pythonic
- 너무 복잡하면 일반 for 루프 사용
- 딕셔너리, 세트, 제너레이터에도 동일한 문법 적용
