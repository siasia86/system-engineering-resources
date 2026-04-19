# Python 문자열 처리

문자열 메서드, 포맷팅, 인코딩에 대한 가이드입니다.

## 목차
- [문자열 메서드](#문자열-메서드)
- [f-string 포맷팅](#f-string-포맷팅)
- [format() 메서드](#format-메서드)
- [슬라이싱](#슬라이싱)
- [인코딩/디코딩](#인코딩디코딩)
- [Raw 문자열과 멀티라인](#raw-문자열과-멀티라인)
- [요약](#요약)
- [실전 예제](#실전-예제)

---

## 문자열 메서드

### 검색

```python
s = "Hello, World!"

s.find('World')       # 7 (인덱스, 없으면 -1)
s.index('World')      # 7 (없으면 ValueError)
s.rfind('l')          # 10 (오른쪽부터 검색)
s.count('l')          # 3
s.startswith('Hello')  # True
s.endswith('!')        # True
'World' in s           # True
```

### 변환

```python
s = "  Hello, World!  "

s.strip()       # 'Hello, World!' (양쪽 공백 제거)
s.lstrip()      # 'Hello, World!  '
s.rstrip()      # '  Hello, World!'
s.strip('! ')   # 'Hello, World' (지정 문자 제거)

"hello".upper()       # 'HELLO'
"HELLO".lower()       # 'hello'
"hello world".title()  # 'Hello World'
"hello world".capitalize()  # 'Hello world'
"Hello".swapcase()    # 'hELLO'
```

### 분할/결합

```python
# split
"a,b,c".split(',')           # ['a', 'b', 'c']
"a  b  c".split()            # ['a', 'b', 'c'] (공백 자동)
"a,b,c,d".split(',', 2)      # ['a', 'b', 'c,d'] (최대 2회)
"line1\nline2\nline3".splitlines()  # ['line1', 'line2', 'line3']

# join
','.join(['a', 'b', 'c'])    # 'a,b,c'
'\n'.join(['line1', 'line2'])  # 'line1\nline2'
' '.join(str(i) for i in range(5))  # '0 1 2 3 4'
```

### 치환/정렬

```python
# replace
"hello world".replace('world', 'Python')  # 'hello Python'
"aabaa".replace('a', 'x', 2)              # 'xxbaa' (최대 2회)

# 정렬
"hello".center(20)     # '       hello        '
"hello".ljust(20)      # 'hello               '
"hello".rjust(20)      # '               hello'
"42".zfill(5)          # '00042'
```

### 판별

```python
"123".isdigit()      # True
"abc".isalpha()      # True
"abc123".isalnum()   # True
"   ".isspace()      # True
"Hello".isupper()    # False
"hello".islower()    # True
```

---

## f-string 포맷팅

### 기본 사용법 (Python 3.6+)

```python
name = "홍길동"
age = 30

# 변수 삽입
f"이름: {name}, 나이: {age}"

# 표현식
f"내년 나이: {age + 1}"
f"대문자: {name.upper()}"
```

### 숫자 포맷

```python
pi = 3.141592

f"{pi:.2f}"        # '3.14' (소수점 2자리)
f"{1000000:,}"     # '1,000,000' (천 단위 쉼표)
f"{0.85:.1%}"      # '85.0%' (퍼센트)
f"{255:08b}"       # '11111111' (2진수, 8자리)
f"{255:04x}"       # '00ff' (16진수, 4자리)
f"{42:05d}"        # '00042' (0 채우기)
```

### 정렬

```python
s = "hello"

f"{s:<20}"   # 'hello               ' (왼쪽 정렬)
f"{s:>20}"   # '               hello' (오른쪽 정렬)
f"{s:^20}"   # '       hello        ' (가운데 정렬)
f"{s:*^20}"  # '*******hello********' (채우기 문자)
```

### 디버깅 (Python 3.8+)

```python
x = 10
y = 20
f"{x=}, {y=}"          # 'x=10, y=20'
f"{x + y=}"            # 'x + y=30'
f"{name=!r}"           # "name='홍길동'"
```

---

## format() 메서드

```python
# 위치 인자
"{} {}".format("Hello", "World")     # 'Hello World'
"{0} {1} {0}".format("Hello", "World")  # 'Hello World Hello'

# 키워드 인자
"{name}은 {age}세".format(name="홍길동", age=30)

# 딕셔너리 언패킹
data = {'name': '홍길동', 'age': 30}
"{name}은 {age}세".format(**data)
```

---

## 슬라이싱

```python
s = "Hello, World!"

s[0:5]     # 'Hello'
s[7:]      # 'World!'
s[:5]      # 'Hello'
s[-6:]     # 'orld!'
s[::2]     # 'Hlo ol!'
s[::-1]    # '!dlroW ,olleH' (역순)
```

---

## 인코딩/디코딩

```python
# 문자열 → 바이트
text = "안녕하세요"
encoded = text.encode('utf-8')
print(encoded)  # b'\xec\x95\x88\xeb\x85\x95\xed\x95\x98\xec\x84\xb8\xec\x9a\x94'
print(len(encoded))  # 15 (한글 1자 = 3바이트)

# 바이트 → 문자열
decoded = encoded.decode('utf-8')
print(decoded)  # '안녕하세요'

# 파일 읽기/쓰기 시 인코딩 지정
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 인코딩 에러 처리
b'\xff\xfe'.decode('utf-8', errors='ignore')    # 무시
b'\xff\xfe'.decode('utf-8', errors='replace')   # '��' 대체
```

---

## Raw 문자열과 멀티라인

### Raw 문자열

```python
# 이스케이프 무시 (정규표현식, 파일 경로에 유용)
path = r'C:\Users\name\documents'
regex = r'\d+\.\d+'

# 일반 문자열과 비교
print('hello\nworld')   # 줄바꿈 적용
print(r'hello\nworld')  # hello\nworld (그대로)
```

### 멀티라인 문자열

```python
# 삼중 따옴표
text = """첫 번째 줄
두 번째 줄
세 번째 줄"""

# 들여쓰기 제거 (textwrap)
import textwrap
text = textwrap.dedent("""\
    첫 번째 줄
    두 번째 줄
    세 번째 줄""")
```

---

## 실전 예제

### 로그 라인 파싱

```python
log = "2026-04-20 10:30:45 ERROR nginx: connection refused"
parts = log.split(' ', 3)
date, time_, level, message = parts
print(f"레벨: {level}, 메시지: {message}")
```

### 설정 파일 파싱

```python
config_line = "  db_host = localhost  "
key, value = config_line.strip().split('=', 1)
print(f"{key.strip()!r}: {value.strip()!r}")
# 'db_host': 'localhost'
```

### 테이블 형식 출력

```python
headers = ['서비스', '상태', 'CPU']
rows = [('nginx', 'running', '2.1%'), ('redis', 'stopped', '0%')]

print(f"{'서비스':<12} {'상태':<10} {'CPU':>6}")
print('-' * 30)
for name, status, cpu in rows:
    print(f"{name:<12} {status:<10} {cpu:>6}")
```

### 경로 문자열 처리

```python
path = "/var/log/nginx/access.log"
parts = path.rsplit('/', 1)
print(parts[0])   # '/var/log/nginx'
print(parts[1])   # 'access.log'

# 확장자 제거
name = 'access.log'
stem = name.rsplit('.', 1)[0]  # 'access'
```

---

## 요약

| 메서드 | 용도 | 예시 |
|--------|------|------|
| `split()` | 분할 | `"a,b".split(',')` → `['a','b']` |
| `join()` | 결합 | `','.join(['a','b'])` → `'a,b'` |
| `strip()` | 공백 제거 | `" hi ".strip()` → `'hi'` |
| `replace()` | 치환 | `"ab".replace('a','x')` → `'xb'` |
| `find()` | 검색 | `"abc".find('b')` → `1` |
| `upper/lower()` | 대소문자 | `"hi".upper()` → `'HI'` |
| `startswith()` | 시작 확인 | `"abc".startswith('a')` → `True` |
| `encode()` | 인코딩 | `"한글".encode('utf-8')` |

**관련 문서:**
- [정규표현식](./python_regex.md) - 패턴 매칭
- [파일 입출력](./python_file_io.md) - 파일 처리
- [Print 함수](./python_print.md) - 출력
