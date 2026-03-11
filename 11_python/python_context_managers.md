# Python 컨텍스트 매니저 (Context Managers)

Python 컨텍스트 매니저의 개념부터 고급 활용까지 다루는 완벽 가이드입니다.

## 목차
- [컨텍스트 매니저란?](#컨텍스트-매니저란)
- [with 문 기본](#with-문-기본)
- [__enter__와 __exit__](#__enter__와-__exit__)
- [contextlib 모듈](#contextlib-모듈)
- [중첩과 다중 컨텍스트](#중첩과-다중-컨텍스트)
- [비동기 컨텍스트 매니저](#비동기-컨텍스트-매니저)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)

---

## 컨텍스트 매니저란?

리소스를 안전하게 획득하고 해제하는 프로토콜입니다.

### 왜 사용하나?

- **자동 정리**: 리소스 자동 해제
- **예외 안전**: 오류 발생해도 정리 보장
- **가독성**: 명확한 리소스 범위
- **누수 방지**: 메모리/파일 누수 차단

### 기본 개념

```python
# 수동 관리 (위험)
file = open("data.txt")
try:
    content = file.read()
finally:
    file.close()

# 컨텍스트 매니저 (안전)
with open("data.txt") as file:
    content = file.read()
# 자동으로 닫힘
```

---

## with 문 기본

### 파일 처리

```python
# 읽기
with open("data.txt", "r") as f:
    content = f.read()
    print(content)

# 쓰기
with open("output.txt", "w") as f:
    f.write("Hello, World!")

# 예외 발생해도 파일 자동 닫힘
```

### 여러 파일 동시 처리

```python
with open("input.txt", "r") as infile, open("output.txt", "w") as outfile:
    for line in infile:
        outfile.write(line.upper())
```

### 락(Lock) 관리

```python
import threading

lock = threading.Lock()

with lock:
    # 임계 영역
    shared_resource += 1
# 자동으로 락 해제
```

---

## __enter__와 __exit__

### 기본 구현

```python
class MyContext:
    def __enter__(self):
        print("리소스 획득")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("리소스 해제")
        return False  # 예외 전파

with MyContext() as ctx:
    print("작업 수행")
# 리소스 획득
# 작업 수행
# 리소스 해제
```

### 반환값 활용

```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = self.connect()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False
    
    def connect(self):
        print("DB 연결")
        return "connection"

with DatabaseConnection() as conn:
    print(f"사용: {conn}")
# DB 연결
# 사용: connection
```

### 예외 처리

```python
class ErrorHandler:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print("정상 종료")
        else:
            print(f"예외 발생: {exc_type.__name__}: {exc_val}")
            return True  # 예외 억제

with ErrorHandler():
    raise ValueError("테스트 오류")
# 예외 발생: ValueError: 테스트 오류
# (프로그램 계속 실행)
```

### 타이머 구현

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.elapsed = self.end - self.start
        print(f"실행 시간: {self.elapsed:.4f}초")
        return False

with Timer():
    time.sleep(0.5)
# 실행 시간: 0.5001초
```

---

## contextlib 모듈

### @contextmanager 데코레이터

```python
from contextlib import contextmanager

@contextmanager
def managed_file(filename):
    f = open(filename, "w")
    try:
        yield f
    finally:
        f.close()

with managed_file("test.txt") as f:
    f.write("Hello!")
```

### 간단한 타이머

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(name):
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{name}: {elapsed:.4f}초")

with timer("작업"):
    time.sleep(0.1)
# 작업: 0.1001초
```

### suppress - 예외 무시

```python
from contextlib import suppress
import os

# FileNotFoundError 무시
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# 여러 예외 무시
with suppress(ValueError, TypeError):
    risky_operation()
```

### redirect_stdout - 출력 리다이렉트

```python
from contextlib import redirect_stdout
import io

f = io.StringIO()
with redirect_stdout(f):
    print("Hello")
    print("World")

output = f.getvalue()
print(output)  # "Hello\nWorld\n"
```

### closing - 자동 close 호출

```python
from contextlib import closing
from urllib.request import urlopen

with closing(urlopen("http://example.com")) as page:
    content = page.read()
```

### ExitStack - 동적 컨텍스트

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(f"file{i}.txt", "w")) for i in range(3)]
    for i, f in enumerate(files):
        f.write(f"File {i}")
# 모든 파일 자동 닫힘
```

---

## 중첩과 다중 컨텍스트

### 중첩 컨텍스트

```python
with open("input.txt") as infile:
    with open("output.txt", "w") as outfile:
        outfile.write(infile.read())
```

### 다중 컨텍스트 (한 줄)

```python
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    outfile.write(infile.read())
```

### 조건부 컨텍스트

```python
from contextlib import nullcontext

def process(use_lock=True):
    lock = threading.Lock() if use_lock else nullcontext()
    
    with lock:
        # 작업 수행
        pass
```

### ExitStack으로 동적 관리

```python
from contextlib import ExitStack

def process_files(filenames):
    with ExitStack() as stack:
        files = [stack.enter_context(open(fn)) for fn in filenames]
        
        for f in files:
            print(f.read())
```

---

## 비동기 컨텍스트 매니저

### async with 기본

```python
class AsyncResource:
    async def __aenter__(self):
        print("비동기 획득")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("비동기 해제")
        return False

async def main():
    async with AsyncResource() as resource:
        print("작업 수행")

# asyncio.run(main())
```

### @asynccontextmanager

```python
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def async_timer(name):
    start = asyncio.get_event_loop().time()
    yield
    elapsed = asyncio.get_event_loop().time() - start
    print(f"{name}: {elapsed:.4f}초")

async def main():
    async with async_timer("비동기 작업"):
        await asyncio.sleep(0.1)

# asyncio.run(main())
```

---

## 실전 예제

### 예제 1: 데이터베이스 트랜잭션

```python
class Transaction:
    def __init__(self, connection):
        self.conn = connection
    
    def __enter__(self):
        self.conn.begin()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        return False

# 사용
with Transaction(db_connection) as conn:
    conn.execute("INSERT INTO users VALUES (?)", ("홍길동",))
    conn.execute("UPDATE balance SET amount = amount - 100")
# 성공 시 커밋, 실패 시 롤백
```

### 예제 2: 임시 디렉토리

```python
import os
import tempfile
import shutil
from contextlib import contextmanager

@contextmanager
def temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

with temp_directory() as tmpdir:
    filepath = os.path.join(tmpdir, "test.txt")
    with open(filepath, "w") as f:
        f.write("임시 파일")
# 디렉토리 자동 삭제
```

### 예제 3: 환경 변수 임시 변경

```python
import os
from contextlib import contextmanager

@contextmanager
def temp_env(**kwargs):
    old_env = {}
    for key, value in kwargs.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        yield
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

with temp_env(DEBUG="true", LOG_LEVEL="info"):
    print(os.environ["DEBUG"])  # "true"
# 원래 값으로 복원
```

### 예제 4: 작업 디렉토리 변경

```python
import os
from contextlib import contextmanager

@contextmanager
def change_dir(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)

with change_dir("/tmp"):
    print(os.getcwd())  # /tmp
# 원래 디렉토리로 복원
```

### 예제 5: 성능 모니터링

```python
from contextlib import contextmanager
import time
import psutil
import os

@contextmanager
def monitor_performance(name):
    process = psutil.Process(os.getpid())
    
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024
    
    yield
    
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024
    
    print(f"\n=== {name} 성능 ===")
    print(f"시간: {end_time - start_time:.4f}초")
    print(f"메모리: {end_memory - start_memory:.2f}MB")

with monitor_performance("데이터 처리"):
    data = [i ** 2 for i in range(1000000)]
```

### 예제 6: 재시도 로직

```python
from contextlib import contextmanager
import time

@contextmanager
def retry_on_error(max_attempts=3, delay=1):
    for attempt in range(max_attempts):
        try:
            yield attempt
            break
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            print(f"시도 {attempt + 1} 실패: {e}")
            time.sleep(delay)

with retry_on_error(max_attempts=3) as attempt:
    print(f"시도 {attempt + 1}")
    # 작업 수행
```

### 예제 7: 로깅 컨텍스트

```python
import logging
from contextlib import contextmanager

@contextmanager
def log_context(name, level=logging.INFO):
    logging.log(level, f"{name} 시작")
    start = time.time()
    
    try:
        yield
    except Exception as e:
        logging.error(f"{name} 실패: {e}")
        raise
    else:
        elapsed = time.time() - start
        logging.log(level, f"{name} 완료 ({elapsed:.4f}초)")

with log_context("데이터 처리"):
    process_data()
```

### 예제 8: 리소스 풀

```python
from contextlib import contextmanager
from queue import Queue

class ResourcePool:
    def __init__(self, create_resource, size=5):
        self.pool = Queue(maxsize=size)
        for _ in range(size):
            self.pool.put(create_resource())
    
    @contextmanager
    def acquire(self):
        resource = self.pool.get()
        try:
            yield resource
        finally:
            self.pool.put(resource)

# 사용
pool = ResourcePool(lambda: "connection", size=3)

with pool.acquire() as conn:
    print(f"사용: {conn}")
```

---

## 실전 팁

### Tip 1: 항상 예외 안전하게

```python
@contextmanager
def safe_context():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        # 예외 발생해도 실행
        release_resource(resource)
```

### Tip 2: __exit__ 반환값 주의

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    cleanup()
    return False  # 예외 전파 (기본)
    # return True  # 예외 억제 (신중히 사용)
```

### Tip 3: contextlib 우선 사용

```python
# 간단한 경우 @contextmanager 사용
@contextmanager
def simple_context():
    setup()
    yield
    cleanup()

# 복잡한 경우 클래스 사용
class ComplexContext:
    def __enter__(self):
        # 복잡한 초기화
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 복잡한 정리
        pass
```

### Tip 4: 중첩보다 다중 사용

```python
# 가독성 좋음
with open("a.txt") as f1, open("b.txt") as f2:
    process(f1, f2)

# 가독성 나쁨
with open("a.txt") as f1:
    with open("b.txt") as f2:
        process(f1, f2)
```

### Tip 5: ExitStack으로 동적 관리

```python
from contextlib import ExitStack

with ExitStack() as stack:
    # 조건부로 컨텍스트 추가
    if need_file:
        f = stack.enter_context(open("data.txt"))
    
    if need_lock:
        stack.enter_context(lock)
    
    # 작업 수행
```

### Tip 6: 예외 정보 활용

```python
class DebugContext:
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"예외: {exc_type.__name__}")
            print(f"값: {exc_val}")
            # exc_tb로 트레이스백 접근 가능
        return False
```

### Tip 7: 재사용 가능하게 설계

```python
class ReusableContext:
    def __enter__(self):
        self.resource = acquire()
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        release(self.resource)
        return False

ctx = ReusableContext()

with ctx:
    # 첫 번째 사용
    pass

with ctx:
    # 재사용 가능
    pass
```

### Tip 8: nullcontext로 조건부 처리

```python
from contextlib import nullcontext

def process(use_lock=True):
    lock = threading.Lock() if use_lock else nullcontext()
    
    with lock:
        # 락 필요 여부에 관계없이 동일한 코드
        shared_resource += 1
```

---

## 자주하는 실수

### 실수 1: finally 누락

```python
# 나쁜 예
@contextmanager
def bad_context():
    resource = acquire()
    yield resource
    release(resource)  # 예외 시 실행 안 됨!

# 좋은 예
@contextmanager
def good_context():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

### 실수 2: __exit__에서 예외 발생

```python
# 나쁜 예
def __exit__(self, exc_type, exc_val, exc_tb):
    self.resource.close()  # 예외 발생 가능
    return False

# 좋은 예
def __exit__(self, exc_type, exc_val, exc_tb):
    try:
        self.resource.close()
    except Exception as e:
        logging.error(f"정리 실패: {e}")
    return False
```

### 실수 3: yield 여러 번

```python
# 나쁜 예
@contextmanager
def bad_context():
    yield 1
    yield 2  # 오류!

# 좋은 예
@contextmanager
def good_context():
    yield (1, 2)  # 튜플로 반환
```

### 실수 4: 컨텍스트 외부에서 리소스 사용

```python
# 나쁜 예
with open("data.txt") as f:
    content = f

print(content.read())  # 파일 이미 닫힘!

# 좋은 예
with open("data.txt") as f:
    content = f.read()

print(content)
```

### 실수 5: 예외 억제 남용

```python
# 나쁜 예
def __exit__(self, exc_type, exc_val, exc_tb):
    return True  # 모든 예외 숨김!

# 좋은 예
def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is SpecificError:
        return True  # 특정 예외만 억제
    return False
```

### 실수 6: 상태 초기화 누락

```python
# 나쁜 예
class BadContext:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        # 상태 초기화 안 함

# 재사용 시 문제 발생

# 좋은 예
class GoodContext:
    def __enter__(self):
        self.state = "active"
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        self.state = "inactive"
```

---

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| with 문 | 컨텍스트 매니저 사용 | `with open(...) as f:` |
| __enter__ | 리소스 획득 | `def __enter__(self):` |
| __exit__ | 리소스 해제 | `def __exit__(self, ...):` |
| @contextmanager | 간단한 구현 | `@contextmanager` |
| suppress | 예외 무시 | `with suppress(Error):` |
| ExitStack | 동적 관리 | `with ExitStack():` |
| async with | 비동기 컨텍스트 | `async with resource:` |

**핵심 포인트:**
- 리소스는 항상 컨텍스트 매니저로 관리
- finally로 정리 보장
- 간단하면 @contextmanager, 복잡하면 클래스
- 예외 억제는 신중히 사용
- ExitStack으로 동적 관리
- nullcontext로 조건부 처리

**관련 문서:**
- [예외 처리 튜토리얼](./python_exceptions.md) - 예외와 컨텍스트
- [파일 I/O 튜토리얼](./python_file_io.md) - 파일 컨텍스트
- [데코레이터 튜토리얼](./python_decorators.md) - @contextmanager
