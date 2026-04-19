# Python 자료구조

Python 내장 자료구조와 collections 모듈 가이드입니다.

## 목차
- [리스트 (list)](#리스트-list)
- [딕셔너리 (dict)](#딕셔너리-dict)
- [튜플 (tuple)](#튜플-tuple)
- [집합 (set)](#집합-set)
- [collections 모듈](#collections-모듈)
- [요약](#요약)
- [실전 예제](#실전-예제)

---

## 리스트 (list)

### 기본 메서드

```python
lst = [1, 2, 3]

lst.append(4)        # [1, 2, 3, 4]
lst.extend([5, 6])   # [1, 2, 3, 4, 5, 6]
lst.insert(0, 0)     # [0, 1, 2, 3, 4, 5, 6]
lst.remove(3)        # [0, 1, 2, 4, 5, 6] (첫 번째 3 제거)
lst.pop()            # 6 반환, [0, 1, 2, 4, 5]
lst.pop(0)           # 0 반환, [1, 2, 4, 5]
lst.index(4)         # 2 (값 4의 인덱스)
lst.count(2)         # 1 (값 2의 개수)
lst.reverse()        # [5, 4, 2, 1]
lst.clear()          # []
```

### 슬라이싱

```python
lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

lst[2:5]     # [2, 3, 4]
lst[:3]      # [0, 1, 2]
lst[7:]      # [7, 8, 9]
lst[-3:]     # [7, 8, 9]
lst[::2]     # [0, 2, 4, 6, 8] (짝수 인덱스)
lst[::-1]    # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (역순)
lst[1:8:2]   # [1, 3, 5, 7] (1~7, 2칸씩)
```

### 정렬

```python
# 원본 변경
lst = [3, 1, 4, 1, 5]
lst.sort()                    # [1, 1, 3, 4, 5]
lst.sort(reverse=True)        # [5, 4, 3, 1, 1]

# 새 리스트 반환
lst = [3, 1, 4, 1, 5]
sorted_lst = sorted(lst)     # [1, 1, 3, 4, 5]

# key 함수
words = ['banana', 'apple', 'cherry']
words.sort(key=len)           # ['apple', 'banana', 'cherry']
words.sort(key=str.lower)     # 대소문자 무시 정렬

# 복합 정렬
data = [('홍길동', 30), ('김철수', 25), ('이영희', 30)]
data.sort(key=lambda x: (x[1], x[0]))  # 나이순, 같으면 이름순
```

### 복사

```python
import copy

lst = [[1, 2], [3, 4]]

# 얕은 복사
shallow = lst.copy()       # 또는 lst[:]
shallow[0][0] = 99         # 원본도 변경됨!

# 깊은 복사
deep = copy.deepcopy(lst)
deep[0][0] = 99            # 원본 변경 안 됨
```

---

## 딕셔너리 (dict)

### 기본 메서드

```python
d = {'name': '홍길동', 'age': 30}

d['city'] = '서울'          # 추가/수정
d.get('name')               # '홍길동'
d.get('phone', 'N/A')       # 'N/A' (기본값)
d.pop('age')                # 30 반환, 키 제거
d.setdefault('city', '부산') # '서울' (이미 존재)
d.update({'age': 31, 'job': '개발자'})  # 여러 키 업데이트

d.keys()    # dict_keys(['name', 'city', 'age', 'job'])
d.values()  # dict_values([...])
d.items()   # dict_items([('name', '홍길동'), ...])
```

### 순회

```python
d = {'a': 1, 'b': 2, 'c': 3}

# 키 순회
for key in d:
    print(key, d[key])

# 키-값 순회
for key, value in d.items():
    print(f"{key}: {value}")
```

### 딕셔너리 병합 (Python 3.9+)

```python
a = {'x': 1, 'y': 2}
b = {'y': 3, 'z': 4}

merged = a | b       # {'x': 1, 'y': 3, 'z': 4}
a |= b               # a 자체를 업데이트
```

---

## 튜플 (tuple)

### 기본 사용법

```python
t = (1, 2, 3)
t[0]        # 1
t.count(2)  # 1
t.index(3)  # 2
len(t)      # 3

# 단일 요소 튜플
single = (1,)   # 쉼표 필수
not_tuple = (1)  # 이건 정수 1
```

### 언패킹

```python
# 기본 언패킹
a, b, c = (1, 2, 3)

# 확장 언패킹
first, *rest = [1, 2, 3, 4, 5]
# first=1, rest=[2, 3, 4, 5]

first, *middle, last = [1, 2, 3, 4, 5]
# first=1, middle=[2, 3, 4], last=5

# 함수 반환값
def get_user():
    return '홍길동', 30, '서울'

name, age, city = get_user()

# 변수 교환
a, b = b, a
```

### namedtuple

```python
from collections import namedtuple

# 정의
Server = namedtuple('Server', ['name', 'ip', 'port'])

# 생성
web = Server('web-01', '192.168.1.10', 80)
print(web.name)  # 'web-01'
print(web.ip)    # '192.168.1.10'
print(web[2])    # 80 (인덱스 접근도 가능)

# _asdict()
print(web._asdict())  # {'name': 'web-01', 'ip': '192.168.1.10', 'port': 80}
```

---

## 집합 (set)

### 기본 연산

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b    # 합집합: {1, 2, 3, 4, 5, 6}
a & b    # 교집합: {3, 4}
a - b    # 차집합: {1, 2}
a ^ b    # 대칭차집합: {1, 2, 5, 6}
```

### 메서드

```python
s = {1, 2, 3}

s.add(4)          # {1, 2, 3, 4}
s.discard(2)      # {1, 3, 4} (없어도 에러 안 남)
s.remove(3)       # {1, 4} (없으면 KeyError)
s.pop()           # 임의 요소 제거 및 반환

# 부분집합/상위집합
{1, 2}.issubset({1, 2, 3})      # True
{1, 2, 3}.issuperset({1, 2})    # True
{1, 2}.isdisjoint({3, 4})       # True (교집합 없음)
```

### frozenset

```python
# 불변 집합 (딕셔너리 키로 사용 가능)
fs = frozenset([1, 2, 3])
# fs.add(4)  # AttributeError

# 집합의 집합
sets = {frozenset([1, 2]), frozenset([3, 4])}
```

---

## collections 모듈

### Counter

```python
from collections import Counter

# 빈도 계산
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']
count = Counter(words)
print(count)                  # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(count.most_common(2))   # [('apple', 3), ('banana', 2)]

# 문자열 빈도
Counter('hello')  # Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})

# 연산
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
c1 + c2  # Counter({'a': 4, 'b': 3})
c1 - c2  # Counter({'a': 2})
```

### defaultdict

```python
from collections import defaultdict

# 기본값 자동 생성
dd = defaultdict(list)
dd['fruits'].append('apple')
dd['fruits'].append('banana')
dd['vegs'].append('carrot')
print(dd)  # {'fruits': ['apple', 'banana'], 'vegs': ['carrot']}

# 그룹화
data = [('dev', '홍길동'), ('ops', '김철수'), ('dev', '이영희')]
groups = defaultdict(list)
for dept, name in data:
    groups[dept].append(name)
# {'dev': ['홍길동', '이영희'], 'ops': ['김철수']}

# 카운터
counter = defaultdict(int)
for word in ['a', 'b', 'a', 'c', 'a']:
    counter[word] += 1
```

### deque

```python
from collections import deque

dq = deque([1, 2, 3])
dq.append(4)       # 오른쪽 추가: [1, 2, 3, 4]
dq.appendleft(0)   # 왼쪽 추가: [0, 1, 2, 3, 4]
dq.pop()            # 오른쪽 제거: 4
dq.popleft()        # 왼쪽 제거: 0
dq.rotate(1)        # 오른쪽 회전: [3, 1, 2]

# 최대 길이 제한 (최근 N개 유지)
recent = deque(maxlen=3)
for i in range(5):
    recent.append(i)
print(recent)  # deque([2, 3, 4], maxlen=3)
```

### OrderedDict

```python
from collections import OrderedDict

# Python 3.7+ dict도 순서 보장하지만, 순서 비교가 필요할 때
od1 = OrderedDict([('a', 1), ('b', 2)])
od2 = OrderedDict([('b', 2), ('a', 1)])
print(od1 == od2)  # False (순서가 다름)

d1 = {'a': 1, 'b': 2}
d2 = {'b': 2, 'a': 1}
print(d1 == d2)    # True (일반 dict는 순서 무시)
```

---

## 실전 예제

### 서버 목록 관리

```python
from collections import defaultdict, Counter

# 서버 상태 집계
servers = [
    {'name': 'web-01', 'status': 'running', 'region': 'ap-northeast-2'},
    {'name': 'web-02', 'status': 'stopped', 'region': 'ap-northeast-2'},
    {'name': 'db-01',  'status': 'running', 'region': 'us-east-1'},
]

# 상태별 집계
status_count = Counter(s['status'] for s in servers)
print(status_count)  # Counter({'running': 2, 'stopped': 1})

# 리전별 그룹화
by_region = defaultdict(list)
for s in servers:
    by_region[s['region']].append(s['name'])
print(dict(by_region))
```

### 중복 IP 제거

```python
raw_ips = ['192.168.1.1', '10.0.0.1', '192.168.1.1', '172.16.0.1']
unique_ips = list(dict.fromkeys(raw_ips))  # 순서 유지
# 또는
unique_ips = list(set(raw_ips))            # 순서 무시
```

### 딕셔너리 중첩 안전 접근

```python
config = {'database': {'host': 'localhost', 'port': 5432}}

# 중첩 get
host = config.get('database', {}).get('host', 'default')
print(host)  # 'localhost'
```

---

## 요약

| 자료구조 | 순서 | 변경 | 중복 | 용도 |
|----------|------|------|------|------|
| list | ✅ | ✅ | ✅ | 순서 있는 데이터 |
| tuple | ✅ | ❌ | ✅ | 불변 데이터, 딕셔너리 키 |
| dict | ✅ | ✅ | 키 ❌ | 키-값 매핑 |
| set | ❌ | ✅ | ❌ | 중복 제거, 집합 연산 |
| frozenset | ❌ | ❌ | ❌ | 불변 집합 |

**관련 문서:**
- [컴프리헨션](./python_comprehensions.md) - 자료구조 생성
- [함수](./python_functions.md) - 함수와 자료구조
- [제어문](./python_control_flow.md) - 반복문
