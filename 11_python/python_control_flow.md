# Python 제어문 (Control Flow)

Python의 조건문과 반복문에 대한 완벽 가이드입니다.

## 목차
- [조건문 (if/elif/else)](#조건문-ifelifelse)
- [반복문 (for)](#반복문-for)
- [반복문 (while)](#반복문-while)
- [제어 키워드](#제어-키워드)
- [컴프리헨션](#컴프리헨션)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [요약](#요약)

---

## 조건문 (if/elif/else)

### 기본 if문

```python
age = 20

if age >= 18:
    print("성인입니다")
```

### if-else

```python
age = 15

if age >= 18:
    print("성인입니다")
else:
    print("미성년자입니다")
```

### if-elif-else

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("D")
```

### 중첩 if

```python
age = 25
has_license = True

if age >= 18:
    if has_license:
        print("운전 가능")
    else:
        print("면허 필요")
else:
    print("나이 미달")
```

### 삼항 연산자

```python
age = 20
status = "성인" if age >= 18 else "미성년자"
print(status)  # 성인
```

### 논리 연산자

```python
age = 25
has_license = True

# and
if age >= 18 and has_license:
    print("운전 가능")

# or
if age < 18 or not has_license:
    print("운전 불가")

# not
if not has_license:
    print("면허 없음")
```

---

## 반복문 (for)

### 기본 for문

```python
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4
```

### 리스트 순회

```python
fruits = ["사과", "바나나", "오렌지"]

for fruit in fruits:
    print(fruit)
```

### enumerate 사용

```python
fruits = ["사과", "바나나", "오렌지"]

for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
# 0: 사과
# 1: 바나나
# 2: 오렌지
```

### 딕셔너리 순회

```python
person = {"name": "홍길동", "age": 30, "city": "서울"}

# 키만
for key in person:
    print(key)

# 값만
for value in person.values():
    print(value)

# 키와 값
for key, value in person.items():
    print(f"{key}: {value}")
```

### range 활용

```python
# 0부터 9까지
for i in range(10):
    print(i)

# 1부터 10까지
for i in range(1, 11):
    print(i)

# 2씩 증가
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# 역순
for i in range(10, 0, -1):
    print(i)  # 10, 9, 8, ..., 1
```

---

## 반복문 (while)

### 기본 while문

```python
count = 0

while count < 5:
    print(count)
    count += 1
```

### 무한 루프

```python
while True:
    user_input = input("종료하려면 'q' 입력: ")
    if user_input == 'q':
        break
    print(f"입력: {user_input}")
```

### 조건부 while

```python
password = ""

while password != "1234":
    password = input("비밀번호 입력: ")
    if password == "1234":
        print("로그인 성공")
    else:
        print("비밀번호 오류")
```

---

## 제어 키워드

### break - 반복 중단

```python
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4
```

### continue - 다음 반복으로

```python
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4 (2 제외)
```

### else - 정상 종료 시

```python
# for-else
for i in range(5):
    if i == 10:
        break
else:
    print("break 없이 정상 종료")  # 출력됨

# while-else
count = 0
while count < 3:
    print(count)
    count += 1
else:
    print("while 정상 종료")  # 출력됨
```

### pass - 아무것도 안 함

```python
for i in range(5):
    if i == 2:
        pass  # 나중에 구현
    print(i)  # 0, 1, 2, 3, 4
```

---

## 컴프리헨션

### 리스트 컴프리헨션

```python
# 기본
squares = [x**2 for x in range(5)]
print(squares)  # [0, 1, 4, 9, 16]

# 조건 포함
evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8]

# if-else
result = [x if x % 2 == 0 else -x for x in range(5)]
print(result)  # [0, -1, 2, -3, 4]
```

### 딕셔너리 컴프리헨션

```python
# 기본
squares = {x: x**2 for x in range(5)}
print(squares)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 조건 포함
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
print(even_squares)  # {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}
```

### 집합 컴프리헨션

```python
unique_lengths = {len(word) for word in ["apple", "banana", "kiwi"]}
print(unique_lengths)  # {4, 5, 6}
```

---

## 실전 예제

### 예제 1: 구구단

```python
for i in range(2, 10):
    print(f"\n{i}단:")
    for j in range(1, 10):
        print(f"{i} x {j} = {i*j}")
```

### 예제 2: 소수 찾기

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [n for n in range(2, 50) if is_prime(n)]
print(primes)
```

### 예제 3: 피보나치 수열

```python
def fibonacci(n):
    a, b = 0, 1
    result = []
    while len(result) < n:
        result.append(a)
        a, b = b, a + b
    return result

print(fibonacci(10))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 예제 4: 패턴 출력

```python
# 삼각형
for i in range(1, 6):
    print('*' * i)

# 역삼각형
for i in range(5, 0, -1):
    print('*' * i)

# 피라미드
for i in range(1, 6):
    print(' ' * (5-i) + '*' * (2*i-1))
```

---

## 실전 팁

### Tip 1: enumerate 활용

```python
# 나쁜 예
items = ['a', 'b', 'c']
for i in range(len(items)):
    print(f"{i}: {items[i]}")

# 좋은 예
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

### Tip 2: zip으로 병렬 순회

```python
names = ["홍길동", "김철수", "이영희"]
ages = [30, 25, 28]

for name, age in zip(names, ages):
    print(f"{name}: {age}세")
```

### Tip 3: any/all 활용

```python
numbers = [1, 2, 3, 4, 5]

# 하나라도 짝수?
has_even = any(n % 2 == 0 for n in numbers)

# 모두 양수?
all_positive = all(n > 0 for n in numbers)
```

### Tip 4: else 절 활용

```python
def find_item(items, target):
    for item in items:
        if item == target:
            print(f"{target} 찾음")
            break
    else:
        print(f"{target} 없음")
```

### Tip 5: 중첩 루프 탈출

```python
# 플래그 사용
found = False
for i in range(10):
    for j in range(10):
        if i * j == 24:
            found = True
            break
    if found:
        break

# 함수로 감싸기 (권장)
def find_product():
    for i in range(10):
        for j in range(10):
            if i * j == 24:
                return i, j
```

---

## 요약

| 구문 | 용도 | 예시 |
|------|------|------|
| if/elif/else | 조건 분기 | `if x > 0:` |
| for | 반복 (횟수 정해짐) | `for i in range(10):` |
| while | 반복 (조건 기반) | `while x < 10:` |
| break | 반복 중단 | `break` |
| continue | 다음 반복 | `continue` |
| pass | 빈 블록 | `pass` |

**핵심 포인트:**
- 조건문으로 분기 처리
- for는 횟수, while은 조건
- break/continue로 흐름 제어
- 컴프리헨션으로 간결한 코드
- enumerate, zip 활용

**관련 문서:**
- [함수](./python_functions.md) - 제어문과 함수 조합
- [컴프리헨션](./python_comprehensions.md) - 컴프리헨션 심화
