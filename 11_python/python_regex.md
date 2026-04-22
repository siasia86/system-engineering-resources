# Python 정규표현식 (re 모듈)

문자열 패턴 매칭과 텍스트 처리를 위한 정규표현식 가이드입니다.

## 목차
- [기본 함수](#기본-함수)
- [패턴 문법](#패턴-문법)
- [그룹](#그룹)
- [Greedy vs Lazy](#greedy-vs-lazy)
- [Lookahead / Lookbehind](#lookahead--lookbehind)
- [re.compile()](#recompile)
- [공통 패턴](#공통-패턴)
- [실전 예제](#실전-예제)
- [요약](#요약)

---

## 기본 함수

### re.match() - 문자열 시작부터 매칭

```python
import re

result = re.match(r'\d+', '123abc')
print(result.group())  # '123'

result = re.match(r'\d+', 'abc123')
print(result)  # None (시작이 숫자가 아님)
```

### re.search() - 문자열 전체에서 첫 매칭

```python
result = re.search(r'\d+', 'abc123def456')
print(result.group())  # '123'
print(result.start())  # 3
print(result.end())    # 6
```

### re.findall() - 모든 매칭 리스트

```python
result = re.findall(r'\d+', 'abc123def456ghi789')
print(result)  # ['123', '456', '789']
```

### re.finditer() - 모든 매칭 이터레이터

```python
for match in re.finditer(r'\d+', 'abc123def456'):
    print(f"{match.group()} at {match.start()}-{match.end()}")
# 123 at 3-6
# 456 at 9-12
```

### re.sub() - 치환

```python
result = re.sub(r'\d+', 'NUM', 'abc123def456')
print(result)  # 'abcNUMdefNUM'

# 함수로 치환
def double(match):
    return str(int(match.group()) * 2)

result = re.sub(r'\d+', double, 'price: 100, tax: 10')
print(result)  # 'price: 200, tax: 20'
```

### re.split() - 분할

```python
result = re.split(r'[,;\s]+', 'a,b; c  d')
print(result)  # ['a', 'b', 'c', 'd']
```

---

## 패턴 문법

### 문자 클래스

```python
# 기본
r'\d'    # 숫자 [0-9]
r'\D'    # 숫자 아닌 것
r'\w'    # 단어 문자 [a-zA-Z0-9_]
r'\W'    # 단어 문자 아닌 것
r'\s'    # 공백 문자
r'\S'    # 공백 아닌 것
r'.'     # 줄바꿈 제외 모든 문자
```

### 수량자

```python
r'a*'     # 0회 이상
r'a+'     # 1회 이상
r'a?'     # 0 또는 1회
r'a{3}'   # 정확히 3회
r'a{2,4}' # 2~4회
r'a{2,}'  # 2회 이상
```

### 앵커

```python
r'^start'   # 문자열 시작
r'end$'     # 문자열 끝
r'\bword\b' # 단어 경계
```

### 문자 집합

```python
r'[abc]'    # a, b, c 중 하나
r'[a-z]'    # 소문자
r'[^abc]'   # a, b, c 제외
r'[a-zA-Z]' # 모든 영문자
```

---

## 그룹

### 기본 그룹

```python
result = re.search(r'(\d{4})-(\d{2})-(\d{2})', '2026-04-19')
print(result.group())   # '2026-04-19'
print(result.group(1))  # '2026'
print(result.group(2))  # '04'
print(result.group(3))  # '19'
print(result.groups())  # ('2026', '04', '19')
```

### 네임드 그룹

```python
pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
result = re.search(pattern, '2026-04-19')
print(result.group('year'))   # '2026'
print(result.group('month'))  # '04'
print(result.groupdict())     # {'year': '2026', 'month': '04', 'day': '19'}
```

### 비캡처 그룹

```python
# (?:...) - 그룹화하되 캡처하지 않음
result = re.findall(r'(?:https?|ftp)://(\S+)', 'visit https://example.com')
print(result)  # ['example.com']
```

### findall과 그룹

```python
# 그룹이 있으면 그룹 내용만 반환
result = re.findall(r'(\d+)-(\d+)', '10-20, 30-40')
print(result)  # [('10', '20'), ('30', '40')]
```

---

## Greedy vs Lazy

```python
text = '<div>hello</div><div>world</div>'

# Greedy (기본) - 최대한 많이 매칭
result = re.search(r'<div>.*</div>', text)
print(result.group())  # '<div>hello</div><div>world</div>'

# Lazy (?) - 최소한으로 매칭
result = re.search(r'<div>.*?</div>', text)
print(result.group())  # '<div>hello</div>'
```

```python
# 수량자별 Lazy 버전
r'*?'   # 0회 이상 (최소)
r'+?'   # 1회 이상 (최소)
r'??'   # 0 또는 1회 (최소)
r'{m,n}?'  # m~n회 (최소)
```

---

## Lookahead / Lookbehind

### Lookahead (전방 탐색)

```python
# (?=...) - 긍정 전방 탐색
result = re.findall(r'\w+(?=@)', 'user@example.com admin@test.com')
print(result)  # ['user', 'admin']

# (?!...) - 부정 전방 탐색 (단위가 없는 숫자)
prices = '100원 200달러 300 400엔'
result = re.findall(r'\d+(?!\w)', prices)
print(result)  # ['300']

# .py가 아닌 파일명
files = 'main.py config.json data.csv'
result = re.findall(r'\b\w+\.(?!py\b)\w+', files)
print(result)  # ['config.json', 'data.csv']
```

### Lookbehind (후방 탐색)

```python
# (?<=...) - 긍정 후방 탐색
result = re.findall(r'(?<=\$)\d+', '$100 $200 300')
print(result)  # ['100', '200']

# (?<!...) - 부정 후방 탐색
result = re.findall(r'(?<!\$)\b\d+', '$100 200 $300 400')
print(result)  # ['200', '400']
```

---

## re.compile()

```python
# 패턴을 미리 컴파일 (반복 사용 시 성능 향상)
pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

log_lines = [
    '192.168.1.1 - GET /index.html',
    '10.0.0.5 - POST /api/data',
    'invalid line without ip',
]

for line in log_lines:
    match = pattern.search(line)
    if match:
        print(match.group())

# 플래그 사용
pattern = re.compile(r'error', re.IGNORECASE)  # 대소문자 무시
pattern = re.compile(r'^line', re.MULTILINE)    # 각 줄 시작에서 매칭
pattern = re.compile(r'a.b', re.DOTALL)         # .이 줄바꿈도 매칭
```

---

## 공통 패턴

```python
# IPv4 주소
r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# 이메일 (간단)
r'[\w.-]+@[\w.-]+\.\w+'

# URL
r'https?://[\w./\-?=&#]+'

# 날짜 (YYYY-MM-DD)
r'\d{4}-\d{2}-\d{2}'

# 시간 (HH:MM:SS)
r'\d{2}:\d{2}:\d{2}'

# MAC 주소
r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'

# 한글
r'[가-힣]+'
```

---

## 실전 예제

### 로그 파싱

```python
log = '2026-04-19 10:30:45 ERROR [nginx] Connection refused from 192.168.1.100'

pattern = re.compile(
    r'(?P<date>\d{4}-\d{2}-\d{2})\s+'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
    r'(?P<level>\w+)\s+'
    r'\[(?P<service>\w+)\]\s+'
    r'(?P<message>.*)'
)

match = pattern.search(log)
if match:
    data = match.groupdict()
    # {'date': '2026-04-19', 'time': '10:30:45', 'level': 'ERROR',
    #  'service': 'nginx', 'message': 'Connection refused from 192.168.1.100'}
```

### Apache 액세스 로그

```python
log = '192.168.1.1 - - [19/Apr/2026:10:30:45 +0900] "GET /index.html HTTP/1.1" 200 1234'

pattern = re.compile(
    r'(?P<ip>\S+)\s+\S+\s+\S+\s+'
    r'\[(?P<date>[^\]]+)\]\s+'
    r'"(?P<method>\w+)\s+(?P<path>\S+)\s+\S+"\s+'
    r'(?P<status>\d+)\s+(?P<size>\d+)'
)

match = pattern.search(log)
if match:
    print(match.group('ip'))      # 192.168.1.1
    print(match.group('status'))  # 200
```

### IP 추출 및 집계

```python
from collections import Counter

def count_ips(log_file):
    ip_pattern = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')
    ips = []
    with open(log_file) as f:
        for line in f:
            ips.extend(ip_pattern.findall(line))
    return Counter(ips).most_common(10)
```

### 민감 정보 마스킹

```python
def mask_sensitive(text):
    # 이메일 마스킹
    text = re.sub(r'[\w.-]+@[\w.-]+', '<email>', text)
    # IP 마스킹
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<ip>', text)
    return text
```

---

## 요약

| 함수            | 용도             | 반환            |
|-----------------|------------------|-----------------|
| `re.match()`    | 시작부터 매칭    | Match 또는 None |
| `re.search()`   | 전체에서 첫 매칭 | Match 또는 None |
| `re.findall()`  | 모든 매칭        | 리스트          |
| `re.finditer()` | 모든 매칭        | 이터레이터      |
| `re.sub()`      | 치환             | 문자열          |
| `re.split()`    | 분할             | 리스트          |

**관련 문서:**
- [문자열 처리](./python_string.md) - 문자열 메서드
- [파일 입출력](./python_file_io.md) - 파일 읽기
- [로깅](./python_logging.md) - 로그 처리
