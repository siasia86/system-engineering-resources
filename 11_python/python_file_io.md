# Python 파일 입출력 (File I/O)

Python에서 파일을 읽고 쓰는 모든 방법을 다루는 실용 가이드입니다.

## 목차
- [파일 입출력이란?](#파일-입출력이란)
- [파일 열기와 닫기](#파일-열기와-닫기)
- [파일 읽기](#파일-읽기)
- [파일 쓰기](#파일-쓰기)
- [with 문](#with-문)
- [파일 모드](#파일-모드)
- [경로 처리](#경로-처리)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)

---

## 파일 입출력이란?

파일에 데이터를 저장하거나 읽어오는 작업입니다.

### 왜 사용하나?

- **데이터 영구 저장**: 프로그램 종료 후에도 데이터 유지
- **대용량 처리**: 메모리에 올리지 않고 처리
- **데이터 공유**: 다른 프로그램과 데이터 교환
- **로그 기록**: 실행 기록 저장

---

## 파일 열기와 닫기

### 기본 방법

```python
# 파일 열기
file = open('data.txt', 'r')
content = file.read()
file.close()  # 반드시 닫아야 함
```

### 파일을 닫지 않으면?

```python
# 나쁜 예: 파일을 닫지 않음
file = open('data.txt', 'r')
content = file.read()
# 메모리 누수, 파일 잠금 문제 발생
```

---

## 파일 읽기

### 전체 읽기

```python
with open('data.txt', 'r') as file:
    content = file.read()
    print(content)
```

### 한 줄씩 읽기

```python
with open('data.txt', 'r') as file:
    line = file.readline()
    print(line)
```

### 모든 줄을 리스트로

```python
with open('data.txt', 'r') as file:
    lines = file.readlines()
    for line in lines:
        print(line.strip())
```

### 반복문으로 읽기 (권장)

```python
with open('data.txt', 'r') as file:
    for line in file:
        print(line.strip())
```

### 인코딩 지정

```python
with open('data.txt', 'r', encoding='utf-8') as file:
    content = file.read()
```

---

## 파일 쓰기

### 새로 쓰기 (덮어쓰기)

```python
with open('output.txt', 'w') as file:
    file.write('Hello, World!\n')
    file.write('Python File I/O')
```

### 이어쓰기

```python
with open('output.txt', 'a') as file:
    file.write('추가 내용\n')
```

### 여러 줄 쓰기

```python
lines = ['첫 번째 줄\n', '두 번째 줄\n', '세 번째 줄\n']

with open('output.txt', 'w') as file:
    file.writelines(lines)
```

### print로 파일에 쓰기

```python
with open('output.txt', 'w') as file:
    print('Hello, World!', file=file)
    print('Python File I/O', file=file)
```

---

## with 문

파일을 자동으로 닫아주는 안전한 방법입니다.

### 기본 사용

```python
# with 사용 (권장)
with open('data.txt', 'r') as file:
    content = file.read()
# 자동으로 file.close() 호출됨
```

### 여러 파일 동시에

```python
with open('input.txt', 'r') as infile, open('output.txt', 'w') as outfile:
    content = infile.read()
    outfile.write(content.upper())
```

### 예외 발생 시에도 안전

```python
try:
    with open('data.txt', 'r') as file:
        content = file.read()
        # 예외 발생해도 파일은 닫힘
        result = 1 / 0
except ZeroDivisionError:
    print("에러 발생")
# 파일은 이미 닫혔음
```

---

## 파일 모드

### 주요 모드

| 모드 | 설명 | 파일 없으면 | 기존 내용 |
|------|------|-------------|-----------|
| `r` | 읽기 | 에러 | 유지 |
| `w` | 쓰기 | 생성 | 삭제 |
| `a` | 이어쓰기 | 생성 | 유지 |
| `x` | 배타적 생성 | 생성 | 에러 |
| `r+` | 읽기+쓰기 | 에러 | 유지 |
| `w+` | 읽기+쓰기 | 생성 | 삭제 |
| `a+` | 읽기+이어쓰기 | 생성 | 유지 |

### 바이너리 모드

```python
# 텍스트 모드 (기본)
with open('data.txt', 'r') as file:
    content = file.read()  # str

# 바이너리 모드
with open('image.png', 'rb') as file:
    content = file.read()  # bytes
```

### 모드 예제

```python
# 읽기 전용
with open('data.txt', 'r') as file:
    content = file.read()

# 쓰기 (덮어쓰기)
with open('data.txt', 'w') as file:
    file.write('새 내용')

# 이어쓰기
with open('data.txt', 'a') as file:
    file.write('추가 내용')

# 파일이 없을 때만 생성
with open('data.txt', 'x') as file:
    file.write('새 파일')
```

---

## 경로 처리

### pathlib 사용 (권장)

```python
from pathlib import Path

# 경로 생성
path = Path('data.txt')
path = Path('folder') / 'subfolder' / 'data.txt'

# 파일 읽기
content = path.read_text(encoding='utf-8')

# 파일 쓰기
path.write_text('Hello, World!', encoding='utf-8')

# 파일 존재 확인
if path.exists():
    print('파일 있음')

# 디렉토리 확인
if path.is_file():
    print('파일입니다')
if path.is_dir():
    print('디렉토리입니다')
```

### 경로 정보

```python
from pathlib import Path

path = Path('/home/user/documents/data.txt')

print(path.name)        # data.txt
print(path.stem)        # data
print(path.suffix)      # .txt
print(path.parent)      # /home/user/documents
print(path.absolute())  # 절대 경로
```

### 디렉토리 생성

```python
from pathlib import Path

# 디렉토리 생성
path = Path('new_folder')
path.mkdir(exist_ok=True)  # 이미 있어도 에러 안남

# 중첩 디렉토리 생성
path = Path('parent/child/grandchild')
path.mkdir(parents=True, exist_ok=True)
```

### 파일 목록

```python
from pathlib import Path

# 현재 디렉토리의 모든 파일
for file in Path('.').iterdir():
    print(file)

# 특정 패턴 파일
for file in Path('.').glob('*.txt'):
    print(file)

# 재귀적 검색
for file in Path('.').rglob('*.py'):
    print(file)
```

### os.path 사용

```python
import os

# 경로 결합
path = os.path.join('folder', 'subfolder', 'data.txt')

# 경로 존재 확인
if os.path.exists(path):
    print('존재함')

# 파일/디렉토리 확인
if os.path.isfile(path):
    print('파일')
if os.path.isdir(path):
    print('디렉토리')

# 경로 분리
dirname = os.path.dirname(path)   # 디렉토리
basename = os.path.basename(path) # 파일명
```

---

## 실전 예제

### 예제 1: 로그 파일 작성

```python
from datetime import datetime
from pathlib import Path

def write_log(message):
    log_file = Path('app.log')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'[{timestamp}] {message}\n'
    
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(log_entry)

write_log('애플리케이션 시작')
write_log('사용자 로그인')
```

### 예제 2: CSV 파일 읽기

```python
def read_csv(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            row = line.strip().split(',')
            data.append(row)
    return data

users = read_csv('users.csv')
for user in users:
    print(user)
```

### 예제 3: 설정 파일 읽기/쓰기

```python
import json
from pathlib import Path

def save_config(config, filename='config.json'):
    path = Path(filename)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False))

def load_config(filename='config.json'):
    path = Path(filename)
    if path.exists():
        return json.loads(path.read_text())
    return {}

# 사용
config = {'host': 'localhost', 'port': 8080}
save_config(config)

loaded = load_config()
print(loaded)  # {'host': 'localhost', 'port': 8080}
```

### 예제 4: 대용량 파일 처리

```python
def process_large_file(filename):
    line_count = 0
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:  # 한 줄씩 읽어서 메모리 절약
            line_count += 1
            # 처리 로직
            if line_count % 10000 == 0:
                print(f'{line_count}줄 처리 완료')
    return line_count

total = process_large_file('large_data.txt')
print(f'총 {total}줄')
```

### 예제 5: 파일 복사

```python
from pathlib import Path

def copy_file(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        raise FileNotFoundError(f'{src} 파일이 없습니다')
    
    dst_path.write_bytes(src_path.read_bytes())

copy_file('source.txt', 'destination.txt')
```

### 예제 6: 텍스트 파일 검색

```python
from pathlib import Path

def search_in_file(filename, keyword):
    results = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            if keyword in line:
                results.append((line_num, line.strip()))
    return results

matches = search_in_file('data.txt', 'Python')
for line_num, line in matches:
    print(f'{line_num}: {line}')
```

### 예제 7: 백업 파일 생성

```python
from pathlib import Path
from datetime import datetime
import shutil

def backup_file(filename):
    src = Path(filename)
    if not src.exists():
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'{src.stem}_{timestamp}{src.suffix}'
    dst = src.parent / backup_name
    
    shutil.copy2(src, dst)
    return dst

backup_path = backup_file('important.txt')
print(f'백업 완료: {backup_path}')
```

---

## 실전 팁

### Tip 1: 항상 with 문 사용

```python
# 나쁜 예
file = open('data.txt', 'r')
content = file.read()
file.close()

# 좋은 예
with open('data.txt', 'r') as file:
    content = file.read()
```

### Tip 2: pathlib 사용

```python
# 나쁜 예
import os
path = os.path.join('folder', 'file.txt')

# 좋은 예
from pathlib import Path
path = Path('folder') / 'file.txt'
```

### Tip 3: 인코딩 명시

```python
# 나쁜 예
with open('data.txt', 'r') as file:  # 시스템 기본 인코딩
    content = file.read()

# 좋은 예
with open('data.txt', 'r', encoding='utf-8') as file:
    content = file.read()
```

### Tip 4: 파일 존재 확인

```python
from pathlib import Path

path = Path('data.txt')
if path.exists():
    content = path.read_text()
else:
    print('파일이 없습니다')
```

### Tip 5: 대용량 파일은 한 줄씩

```python
# 나쁜 예: 전체를 메모리에
with open('large.txt', 'r') as file:
    lines = file.readlines()  # 메모리 부족 가능

# 좋은 예: 한 줄씩 처리
with open('large.txt', 'r') as file:
    for line in file:
        process(line)
```

### Tip 6: 임시 파일 사용

```python
import tempfile

# 임시 파일 자동 삭제
with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp:
    temp.write('임시 데이터')
    temp.flush()
    # 작업 수행
# 자동으로 삭제됨
```

### Tip 7: 파일 잠금 처리

```python
from pathlib import Path
import time

def safe_write(filename, content, max_retries=3):
    path = Path(filename)
    for attempt in range(max_retries):
        try:
            with open(path, 'w') as file:
                file.write(content)
            return True
        except IOError:
            time.sleep(0.1)
    return False
```

### Tip 8: 바이너리 파일 처리

```python
# 이미지 복사
with open('image.png', 'rb') as src:
    with open('copy.png', 'wb') as dst:
        dst.write(src.read())

# 또는 pathlib
from pathlib import Path
Path('copy.png').write_bytes(Path('image.png').read_bytes())
```

---

## 자주하는 실수

### 실수 1: 파일을 닫지 않음

```python
# 나쁜 예
file = open('data.txt', 'r')
content = file.read()
# file.close() 누락

# 좋은 예
with open('data.txt', 'r') as file:
    content = file.read()
```

### 실수 2: 인코딩 문제

```python
# 나쁜 예
with open('한글.txt', 'r') as file:  # UnicodeDecodeError 가능
    content = file.read()

# 좋은 예
with open('한글.txt', 'r', encoding='utf-8') as file:
    content = file.read()
```

### 실수 3: 파일 존재 확인 안함

```python
# 나쁜 예
with open('data.txt', 'r') as file:  # FileNotFoundError
    content = file.read()

# 좋은 예
from pathlib import Path
path = Path('data.txt')
if path.exists():
    content = path.read_text()
```

### 실수 4: 경로 구분자 하드코딩

```python
# 나쁜 예
path = 'folder/subfolder/file.txt'  # Windows에서 문제

# 좋은 예
from pathlib import Path
path = Path('folder') / 'subfolder' / 'file.txt'
```

### 실수 5: 전체 파일을 메모리에

```python
# 나쁜 예: 대용량 파일
with open('huge.txt', 'r') as file:
    lines = file.readlines()  # 메모리 부족

# 좋은 예
with open('huge.txt', 'r') as file:
    for line in file:  # 한 줄씩
        process(line)
```

### 실수 6: 쓰기 모드 혼동

```python
# 나쁜 예: 기존 내용 삭제됨
with open('data.txt', 'w') as file:
    file.write('새 내용')  # 기존 내용 사라짐

# 좋은 예: 이어쓰기
with open('data.txt', 'a') as file:
    file.write('추가 내용')
```

### 실수 7: 상대 경로 문제

```python
# 나쁜 예
with open('data.txt', 'r') as file:  # 현재 디렉토리 의존
    content = file.read()

# 좋은 예: 절대 경로
from pathlib import Path
script_dir = Path(__file__).parent
data_file = script_dir / 'data.txt'
content = data_file.read_text()
```

---

## 요약

| 작업 | 코드 | 설명 |
|------|------|------|
| 읽기 | `open('f.txt', 'r')` | 파일 읽기 |
| 쓰기 | `open('f.txt', 'w')` | 덮어쓰기 |
| 이어쓰기 | `open('f.txt', 'a')` | 끝에 추가 |
| with 문 | `with open() as f:` | 자동 닫기 |
| 전체 읽기 | `file.read()` | 전체 내용 |
| 한 줄 읽기 | `file.readline()` | 한 줄만 |
| 모든 줄 | `file.readlines()` | 리스트로 |
| 경로 처리 | `Path('f.txt')` | pathlib 사용 |

**핵심 포인트:**
- 항상 with 문 사용
- 인코딩 명시 (utf-8)
- pathlib로 경로 처리
- 대용량은 한 줄씩
- 파일 존재 확인

**관련 문서:**
- [예외 처리](./python_exceptions.md) - 파일 에러 처리
- [JSON 처리](./python_json.md) - JSON 파일 다루기
