# Python 비동기 프로그래밍 (asyncio)
<!-- reference: https://docs.python.org/3/library/asyncio.html -->

Python의 asyncio 기반 비동기 프로그래밍 — async/await, Task, 동시 실행, 비동기 I/O를 정리합니다.

## 목차

| 섹션                                                                                                                            |
|---------------------------------------------------------------------------------------------------------------------------------|
| [1. 비동기 개념](#1-비동기-개념) / [2. async def / await](#2-async-def--await) / [3. asyncio 실행](#3-asyncio-실행)             |
| [4. Task와 동시 실행](#4-task와-동시-실행) / [5. 비동기 I/O 패턴](#5-비동기-io-패턴) / [6. 취소와 타임아웃](#6-취소와-타임아웃) |
| [7. 동기 코드와 연동](#7-동기-코드와-연동) / [8. 안티패턴](#8-안티패턴)                                                         |

---

## 1. 비동기 개념

### 동기 vs 비동기

```
동기 (Synchronous)
  작업1 ──────────────────────────►
                                   작업2 ─────────────────────────►
  총 시간 = 작업1 + 작업2

비동기 (Asynchronous)
  작업1 시작 ──── 대기 ─────────── 작업1 완료►
               작업2 시작 ─── 대기 ──── 작업2 완료►
  총 시간 = max(작업1, 작업2) + 오버헤드
```

asyncio는 단일 스레드에서 이벤트 루프로 여러 I/O 작업을 동시에 처리합니다.
CPU 집약적 작업(연산)이 아닌 I/O 대기(네트워크, 파일, DB)에 효과적입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. async def / await

### 코루틴(coroutine) 기본

```python
import asyncio

# async def 로 정의한 함수 = 코루틴 함수
async def fetch_data(url: str) -> str:
    print(f"요청 시작: {url}")
    await asyncio.sleep(1)   # I/O 대기 시뮬레이션 (실제로는 aiohttp 등 사용)
    print(f"요청 완료: {url}")
    return f"data from {url}"

# 코루틴 함수 호출 → 코루틴 객체 (아직 실행 안 됨)
coro = fetch_data("https://example.com")

# 실행하려면 await 또는 asyncio.run()
async def main():
    result = await fetch_data("https://example.com")
    print(result)

asyncio.run(main())
```

### await 가능한 객체

| 객체               | 설명                               |
|--------------------|------------------------------------|
| coroutine          | `async def` 함수 호출 결과         |
| `Task`             | `asyncio.create_task()` 로 생성    |
| `Future`           | 저수준 비동기 연산 결과 컨테이너   |
| `asyncio.sleep(n)` | n초 대기 (이벤트 루프 제어권 반환) |

[⬆ 목차로 돌아가기](#목차)

---

## 3. asyncio 실행

### asyncio.run() — 진입점 (Python 3.7+)

```python
import asyncio

async def main():
    print("시작")
    await asyncio.sleep(0.1)
    print("완료")

# 새 이벤트 루프를 생성하고 코루틴 실행 후 닫음
asyncio.run(main())
```

🟡 `asyncio.run()`은 프로그램 진입점에서 한 번만 호출합니다. 이미 실행 중인 루프 안에서 호출하면 오류가 발생합니다. 주피터 노트북처럼 이미 루프가 있는 환경에서는 `await main()` 을 직접 사용합니다.

### 이벤트 루프 직접 접근 (고급)

```python
import asyncio

loop = asyncio.get_event_loop()

# 현재 실행 중인 루프 확인
try:
    loop = asyncio.get_running_loop()  # 없으면 RuntimeError
except RuntimeError:
    loop = asyncio.new_event_loop()
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. Task와 동시 실행

### asyncio.create_task() — 백그라운드 실행

```python
import asyncio

async def worker(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} 완료"

async def main():
    # Task 생성 → 즉시 스케줄링 (await 없이 백그라운드에서 시작)
    task1 = asyncio.create_task(worker("A", 1.0))
    task2 = asyncio.create_task(worker("B", 0.5))
    task3 = asyncio.create_task(worker("C", 0.8))

    # 모두 완료 대기
    result1 = await task1
    result2 = await task2
    result3 = await task3
    print(result1, result2, result3)
    # 총 시간 ≈ 1.0초 (최장 task 기준)

asyncio.run(main())
```

### asyncio.gather() — 동시 실행 + 결과 수집

```python
import asyncio

async def main():
    results = await asyncio.gather(
        worker("A", 1.0),
        worker("B", 0.5),
        worker("C", 0.8),
    )
    print(results)  # ['A 완료', 'B 완료', 'C 완료'] (순서 보장)

# return_exceptions=True — 일부 실패해도 나머지 결과 수집
async def main_safe():
    results = await asyncio.gather(
        worker("A", 1.0),
        worker("B", 0.5),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"오류: {r}")
        else:
            print(f"성공: {r}")
```

### asyncio.wait() — 완료 조건 제어

```python
import asyncio

async def main():
    tasks = [asyncio.create_task(worker(str(i), i * 0.3)) for i in range(5)]

    # 하나라도 완료되면 반환
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        print(f"완료: {task.result()}")

    # 남은 태스크 취소
    for task in pending:
        task.cancel()
```

### asyncio.as_completed() — 완료 순서대로 처리

```python
import asyncio

async def main():
    tasks = [worker(str(i), (5 - i) * 0.2) for i in range(5)]

    # 완료된 순서대로 처리 (빠른 것 먼저)
    async for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"처리: {result}")
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 비동기 I/O 패턴

### 비동기 컨텍스트 매니저 (async with)

```python
import asyncio
import aiofiles  # pip install aiofiles

async def read_file(path: str) -> str:
    async with aiofiles.open(path, encoding="utf-8") as f:
        return await f.read()

async def write_file(path: str, content: str) -> None:
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(content)
```

### 비동기 이터레이터 (async for)

```python
import asyncio

async def async_range(n: int):
    for i in range(n):
        await asyncio.sleep(0)  # 이벤트 루프에 제어권 반환
        yield i

async def main():
    async for i in async_range(5):
        print(i)
```

### HTTP 비동기 요청 (aiohttp)

```python
import asyncio
import aiohttp  # pip install aiohttp

async def fetch(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.json()

async def fetch_all(urls: list[str]) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    urls = [
        "https://httpbin.org/get?q=1",
        "https://httpbin.org/get?q=2",
    ]
    results = await fetch_all(urls)
    for r in results:
        print(r)

asyncio.run(main())
```

### asyncio.Queue — 생산자-소비자 패턴

```python
import asyncio

async def producer(queue: asyncio.Queue, n: int) -> None:
    for i in range(n):
        await asyncio.sleep(0.1)
        await queue.put(i)
        print(f"생산: {i}")
    await queue.put(None)  # 종료 신호

async def consumer(queue: asyncio.Queue) -> None:
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"소비: {item}")
        queue.task_done()

async def main():
    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=5)
    await asyncio.gather(
        producer(queue, 10),
        consumer(queue),
    )

asyncio.run(main())
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 취소와 타임아웃

### asyncio.timeout() (Python 3.11+)

```python
import asyncio

async def slow_operation() -> str:
    await asyncio.sleep(10)
    return "완료"

async def main():
    try:
        async with asyncio.timeout(3.0):  # 3초 타임아웃
            result = await slow_operation()
    except TimeoutError:
        print("타임아웃 — 3초 초과")

asyncio.run(main())
```

```python
# Python 3.10 이하 — asyncio.wait_for()
async def main():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=3.0)
    except asyncio.TimeoutError:
        print("타임아웃")
```

### Task 취소

```python
import asyncio

async def long_task() -> None:
    try:
        await asyncio.sleep(100)
    except asyncio.CancelledError:
        print("취소됨 — 정리 작업 실행")
        raise  # 반드시 재던지기 (취소 전파)

async def main():
    task = asyncio.create_task(long_task())
    await asyncio.sleep(1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("태스크 취소 확인")

asyncio.run(main())
```

🟡 `CancelledError`는 `asyncio.CancelledError` (Python 3.8+: `BaseException` 상속) 입니다. `except Exception`으로는 잡히지 않으므로 `except BaseException` 또는 별도 처리가 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 동기 코드와 연동

### loop.run_in_executor() — 블로킹 코드 비동기로 실행

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def blocking_io(n: int) -> int:
    """동기 블로킹 함수 (예: DB 드라이버, 파일 I/O)"""
    time.sleep(n)
    return n * 2

def cpu_intensive(n: int) -> int:
    """CPU 집약적 연산"""
    return sum(range(n))

async def main():
    loop = asyncio.get_running_loop()

    # 스레드 풀 — I/O 블로킹 작업
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_io, 1)
        print(f"I/O 결과: {result}")

    # 프로세스 풀 — CPU 집약 작업 (GIL 우회)
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_intensive, 10_000_000)
        print(f"CPU 결과: {result}")

asyncio.run(main())
```

### asyncio.to_thread() (Python 3.9+) — 간편 버전

```python
import asyncio
import time

def blocking_task(seconds: float) -> str:
    time.sleep(seconds)
    return f"{seconds}초 완료"

async def main():
    # 스레드에서 실행 (run_in_executor 단축형)
    result = await asyncio.to_thread(blocking_task, 1.0)
    print(result)

asyncio.run(main())
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 안티패턴

### 이벤트 루프 안에서 블로킹 호출

```python
import asyncio
import time
import requests  # 동기 HTTP 라이브러리

# ❌ 이벤트 루프 블로킹 — 다른 코루틴 모두 멈춤
async def bad_fetch(url: str) -> str:
    resp = requests.get(url)   # 블로킹! 이벤트 루프 멈춤
    return resp.text

# ✅ 비동기 라이브러리 사용
import aiohttp
async def good_fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

# ✅ 부득이한 경우 스레드 풀로 offload
async def offload_fetch(url: str) -> str:
    return await asyncio.to_thread(requests.get, url)
```

### 안티패턴 요약

| 안티패턴                        | 문제                            | 대안                                  |
|---------------------------------|---------------------------------|---------------------------------------|
| `asyncio.run()` 중첩            | RuntimeError (루프 재진입 불가) | 이미 실행 중인 루프에서 `await` 사용  |
| 동기 `time.sleep()` 사용        | 이벤트 루프 블로킹              | `await asyncio.sleep()`               |
| 동기 `requests` 사용            | 이벤트 루프 블로킹              | `aiohttp`, `httpx` 사용               |
| `CancelledError` 무시           | 취소 전파 안 됨, 리소스 누수    | `except CancelledError: raise`        |
| CPU 작업을 코루틴에서 직접 실행 | 이벤트 루프 블로킹              | `ProcessPoolExecutor` 사용            |
| Task 결과를 `await` 없이 버림   | 예외 손실, UnraisableException  | `await task` 또는 `add_done_callback` |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- asyncio docs: [docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html) — ★★★☆☆
- aiohttp docs: [docs.aiohttp.org](https://docs.aiohttp.org/) — ★★★☆☆
- aiofiles: [github.com/Tinche/aiofiles](https://github.com/Tinche/aiofiles) — ★★☆☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-09

**마지막 업데이트**: 2026-08-09

© 2026 siasia86. Licensed under CC BY 4.0.
