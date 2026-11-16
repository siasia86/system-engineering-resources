# Python 동시성 (threading, concurrent.futures, multiprocessing)

여러 서버 점검·파일 처리·API 호출을 동시에 실행할 때 쓰는 표준 라이브러리 세 가지(threading, concurrent.futures, multiprocessing)를 다룹니다. asyncio는 [비동기 프로그래밍](python_async.md) 문서에서 따로 설명합니다.

## 목차

| 섹션                                                                                                    |
|---------------------------------------------------------------------------------------------------------|
| [1. 동시성 모델 선택](#1-동시성-모델-선택) / [2. GIL과 free-threaded 빌드](#2-gil과-free-threaded-빌드) |
| [3. threading 기초](#3-threading-기초) / [4. 동기화 도구](#4-동기화-도구)                               |
| [5. concurrent.futures](#5-concurrentfutures) / [6. multiprocessing](#6-multiprocessing)                |
| [7. 실전 예제](#7-실전-예제) / [8. 점검표](#8-점검표)                                                   |

---

## 1. 동시성 모델 선택

동시성(concurrency)은 여러 작업이 겹쳐서 진행되도록 구성하는 것이고, 병렬성(parallelism)은 여러 작업이 실제로 같은 순간에 서로 다른 CPU 코어에서 실행되는 것입니다. Python에서는 작업 성격에 따라 도구를 고릅니다.

| 작업 성격                         | 예시                           | 권장 도구                           |
|-----------------------------------|--------------------------------|-------------------------------------|
| I/O 대기 위주, 작업 수십~수백 개  | SSH 점검, HTTP 호출, 파일 복사 | `ThreadPoolExecutor`                |
| I/O 대기 위주, 연결 수천 개 이상  | 대량 소켓 연결, 웹 크롤링      | `asyncio`                           |
| CPU 계산 위주                     | 로그 압축 해제·파싱, 해시 계산 | `ProcessPoolExecutor`               |
| 오래 도는 백그라운드 작업 한두 개 | 진행률 표시, 주기적 상태 보고  | `threading.Thread`                  |
| 외부 명령 병렬 실행               | `rsync`, `ping` 여러 개        | `subprocess` + `ThreadPoolExecutor` |

판단 기준은 다음과 같습니다.

- 작업 시간 대부분이 네트워크·디스크 응답을 기다리는 시간이면 스레드로 충분합니다. 기다리는 동안 GIL이 풀리기 때문입니다.
- 작업 시간 대부분이 Python 코드 계산이면 기본(GIL) 빌드에서는 스레드를 늘려도 빨라지지 않습니다. 프로세스를 씁니다.
- 처음에는 고수준 API인 `concurrent.futures`로 시작하고, 세밀한 제어가 필요할 때만 `threading`·`multiprocessing`을 직접 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. GIL과 free-threaded 빌드

GIL(Global Interpreter Lock)은 CPython 인터프리터에서 한 번에 한 스레드만 Python 바이트코드를 실행하도록 막는 잠금입니다. I/O 대기·`time.sleep()`·많은 C 확장 함수는 실행 중 GIL을 풀기 때문에 I/O 위주 작업은 스레드로도 동시에 진행됩니다.

CPython 3.13부터 GIL을 끈 free-threaded 빌드가 별도로 제공됩니다(PEP 703). PEP 779에 따라 3.14에서 공식 지원 단계(phase II)로 올라갔지만 여전히 선택 사항이며 기본 빌드는 GIL이 있는 빌드입니다(2026-11-16 확인).

```bash
# free-threaded 빌드 여부 확인
python3 -VV                     # 출력에 "free-threading build"가 있으면 해당 빌드
```

```python
import sys
import sysconfig

# 1이면 free-threaded 빌드 (권장 확인 방법)
print(sysconfig.get_config_var("Py_GIL_DISABLED"))
# 실행 중 GIL이 실제로 꺼져 있으면 False (3.13+)
print(sys._is_gil_enabled())
```

| 항목                 | 기본 빌드   | free-threaded 빌드                                             |
|----------------------|-------------|----------------------------------------------------------------|
| CPU 계산 스레드 병렬 | 안 됨       | 됨                                                             |
| 단일 스레드 성능     | 기준        | 공식 문서 기준 평균 약 1%(macOS aarch64)~8%(x86-64 Linux) 느림 |
| C 확장 호환          | 대부분 호환 | 미지원 확장을 import하면 GIL이 다시 켜짐                       |
| GIL 강제 활성화      | 해당 없음   | `PYTHON_GIL=1` 또는 `python -X gil=1`                          |

🟡 주의: free-threaded 빌드에서도 공유 자료의 경쟁 조건(race condition)은 그대로 생깁니다. GIL 유무와 관계없이 공유 상태는 잠금이나 큐로 보호합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. threading 기초

### 스레드 생성과 대기

```python
import threading
import time

def worker(name: str, delay: float) -> None:
    time.sleep(delay)
    print(f"{name} done ({threading.current_thread().name})")

threads = [
    threading.Thread(target=worker, args=(f"job-{i}", 0.5), name=f"T{i}")
    for i in range(3)
]
for t in threads:
    t.start()
for t in threads:
    t.join()          # 끝날 때까지 대기
print("all done")
```

### 데몬 스레드

`daemon=True`로 만든 스레드는 메인 스레드가 끝날 때 기다리지 않고 함께 종료됩니다. 정리 작업(파일 닫기, 버퍼 flush)이 실행되지 않을 수 있으므로 결과를 기록하는 작업에는 쓰지 않습니다.

```python
def heartbeat(stop: threading.Event) -> None:
    while not stop.wait(5):        # 5초마다 깨어나고, stop이 set되면 종료
        print("alive")

stop = threading.Event()
threading.Thread(target=heartbeat, args=(stop,), daemon=True).start()
# ... 주 작업 ...
stop.set()
```

### 스레드에서 난 예외

스레드 안에서 처리되지 않은 예외는 메인 스레드로 전달되지 않고 `threading.excepthook`이 표준 에러에 출력만 합니다. 결과와 예외를 모두 받아야 하면 `concurrent.futures`를 쓰는 편이 간단합니다.

```python
def log_thread_exc(args):
    print(f"[thread {args.thread.name}] {args.exc_type.__name__}: {args.exc_value}")

threading.excepthook = log_thread_exc
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 동기화 도구

경쟁 조건은 두 스레드가 같은 값을 읽고 고치는 순서가 섞여 결과가 틀어지는 현상입니다. `counter += 1`도 읽기·더하기·쓰기로 나뉘므로 안전하지 않습니다.

| 도구           | 용도                                      |
|----------------|-------------------------------------------|
| `Lock`         | 한 번에 한 스레드만 구간 진입             |
| `RLock`        | 같은 스레드가 여러 번 획득 가능한 잠금    |
| `Event`        | 한 스레드가 신호를 보내고 나머지가 대기   |
| `Semaphore(n)` | 동시에 n개까지만 진입 (동시 접속 수 제한) |
| `Condition`    | 조건이 만족될 때까지 대기·통지            |
| `queue.Queue`  | 스레드 간 작업 전달 (내부에서 잠금 처리)  |

### Lock

```python
import threading

counter = 0
lock = threading.Lock()

def add(n: int) -> None:
    global counter
    for _ in range(n):
        with lock:            # with 문으로 획득·해제를 짝지음
            counter += 1
```

### Semaphore로 동시 접속 수 제한

```python
import threading

api_slots = threading.BoundedSemaphore(5)   # 동시에 5개까지

def call_api(host: str) -> None:
    with api_slots:
        ...  # 외부 API 호출
```

### queue.Queue 생산자-소비자

```python
import queue
import threading

q: queue.Queue[str | None] = queue.Queue(maxsize=100)

def consumer() -> None:
    while True:
        item = q.get()
        if item is None:           # 종료 신호
            q.task_done()
            break
        print("processing", item)
        q.task_done()

workers = [threading.Thread(target=consumer) for _ in range(4)]
for w in workers:
    w.start()
for path in ["/var/log/a.log", "/var/log/b.log"]:
    q.put(path)
for _ in workers:
    q.put(None)
q.join()                           # 모든 항목의 task_done()까지 대기
```

교착 상태(deadlock)를 피하려면 잠금 여러 개를 항상 같은 순서로 획득하고, 잠금을 쥔 채로 네트워크 호출처럼 오래 걸리는 일을 하지 않습니다. `lock.acquire(timeout=5)`로 대기 시간 상한을 두면 문제 위치를 찾기 쉬워집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. concurrent.futures

`concurrent.futures`는 스레드 풀과 프로세스 풀을 같은 인터페이스(`Executor`)로 다룹니다. `submit()`은 작업 하나를 넣고 `Future`(나중에 결과가 채워지는 객체)를 돌려줍니다.

### 기본값 (3.15 문서 기준, 2026-11-16 확인)

| 항목                                        | 기본값·동작                                          |
|---------------------------------------------|------------------------------------------------------|
| `ThreadPoolExecutor` max_workers            | `min(32, (os.process_cpu_count() or 1) + 4)` (3.13+) |
| `ProcessPoolExecutor` max_workers           | `os.process_cpu_count()` (Windows는 최대 61)         |
| `shutdown(wait=True, cancel_futures=False)` | `cancel_futures`는 3.9+                              |
| `map(..., buffersize=None)`                 | `buffersize`는 3.14+                                 |
| `InterpreterPoolExecutor`                   | 3.14+, 작업자마다 별도 인터프리터                    |

### submit과 as_completed

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket

HOSTS = ["example.com", "example.org", "example.net"]

def check_port(host: str, port: int = 443, timeout: float = 3.0) -> tuple[str, bool]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return host, True
    except OSError:
        return host, False

with ThreadPoolExecutor(max_workers=10) as pool:
    futures = {pool.submit(check_port, h): h for h in HOSTS}
    for fut in as_completed(futures, timeout=30):   # 끝난 순서대로
        host = futures[fut]
        try:
            name, ok = fut.result()
            print(f"{name}: {'OPEN' if ok else 'CLOSED'}")
        except Exception as exc:                     # 작업 안의 예외가 여기서 다시 발생
            print(f"{host}: error {exc}")
```

### map

`map()`은 입력 순서대로 결과를 돌려줍니다. 작업 하나가 예외를 내면 그 결과를 꺼내는 시점에 예외가 발생하므로, 실패를 개별로 다루려면 `submit()`을 씁니다.

```python
with ThreadPoolExecutor(max_workers=8) as pool:
    for host, ok in pool.map(check_port, HOSTS):
        print(host, ok)
```

### wait로 완료 조건 지정

```python
from concurrent.futures import wait, FIRST_EXCEPTION

done, not_done = wait(futures, timeout=60, return_when=FIRST_EXCEPTION)
for fut in not_done:
    fut.cancel()        # 아직 시작하지 않은 작업만 취소됨
```

🟡 주의: 이미 실행 중인 스레드 작업은 `cancel()`로 멈추지 않습니다. 작업 함수 안에서 `threading.Event`를 확인하는 방식으로 직접 멈춤 신호를 처리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. multiprocessing

### 시작 방식

자식 프로세스를 만드는 방식(start method)이 세 가지 있고, 기본값이 버전·플랫폼에 따라 다릅니다.

| 방식         | 동작                                      | 기본인 곳                     |
|--------------|-------------------------------------------|-------------------------------|
| `spawn`      | 새 인터프리터를 띄워 필요한 것만 전달     | Windows, macOS(3.8+)          |
| `fork`       | `os.fork()`로 부모를 그대로 복제          | 3.14부터 어디에서도 기본 아님 |
| `forkserver` | 단일 스레드 서버 프로세스에서 자식을 복제 | POSIX(3.14+)                  |

- 3.12부터 여러 스레드가 있는 프로세스에서 `fork`를 쓰면 `DeprecationWarning`이 납니다. 스레드를 쓰는 프로그램에서 `fork`는 잠금 상태가 복제되어 멈출 수 있습니다.
- `spawn`·`forkserver`는 자식이 메인 모듈을 import하므로 진입점을 `if __name__ == "__main__":`로 보호해야 합니다. 보호하지 않으면 자식이 다시 프로세스를 만들려고 합니다.
- 작업 함수와 인자는 pickle(직렬화)되어 전달되므로 모듈 최상위에 정의한 함수만 쓸 수 있습니다. 람다·중첩 함수는 전달되지 않습니다.

```python
import multiprocessing as mp

def square(x: int) -> int:
    return x * x

if __name__ == "__main__":
    ctx = mp.get_context("spawn")       # 시작 방식을 명시하면 플랫폼 차이가 줄어듦
    with ctx.Pool(processes=4) as pool:
        print(pool.map(square, range(10)))
```

### ProcessPoolExecutor로 CPU 작업 나누기

```python
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
from pathlib import Path

def sha256_of_gz(path: str) -> tuple[str, str]:
    h = hashlib.sha256()
    with gzip.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return path, h.hexdigest()

if __name__ == "__main__":
    files = [str(p) for p in Path("/var/log").glob("*.gz")]
    with ProcessPoolExecutor() as pool:
        for path, digest in pool.map(sha256_of_gz, files, chunksize=4):
            print(digest, path)
```

`chunksize`는 작업을 몇 개씩 묶어 자식에게 보낼지 정합니다. 작업 하나가 짧고 개수가 많을 때 값을 키우면 프로세스 간 통신 비용이 줄어듭니다.

### 프로세스 간 자료 공유

| 방법             | 특징                                                 |
|------------------|------------------------------------------------------|
| `Queue`, `Pipe`  | 객체를 pickle해서 주고받음. 가장 일반적              |
| `Value`, `Array` | 공유 메모리. 단순 숫자·배열에 빠름                   |
| `Manager()`      | 별도 서버 프로세스가 dict·list를 보관. 느리지만 유연 |
| `shared_memory`  | 큰 바이너리 버퍼를 복사 없이 공유                    |

자식이 `Queue`에 넣은 항목을 부모가 꺼내지 않은 채 `join()`하면 자식이 끝나지 않아 교착 상태가 될 수 있습니다. 큐를 먼저 비운 뒤 `join()`합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 예제

### 여러 서버에 명령 병렬 실행

```python
#!/usr/bin/env python3
"""여러 호스트에서 uptime을 병렬로 수집합니다."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

HOSTS = ["192.0.2.10", "192.0.2.11", "192.0.2.12"]

def run_remote(host: str) -> tuple[str, int, str]:
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", host, "uptime"],
        capture_output=True, text=True, timeout=30,
    )
    return host, proc.returncode, (proc.stdout or proc.stderr).strip()

def main() -> int:
    failed = 0
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(run_remote, h) for h in HOSTS]
        for fut in as_completed(futures):
            try:
                host, rc, out = fut.result()
            except subprocess.TimeoutExpired as exc:
                failed += 1
                print(f"TIMEOUT {exc.cmd[-2]}")
                continue
            if rc != 0:
                failed += 1
            print(f"{'OK  ' if rc == 0 else 'FAIL'} {host}: {out}")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### 스레드 풀과 로깅

`logging` 모듈의 핸들러는 내부 잠금을 쓰므로 여러 스레드에서 같은 로거에 써도 줄이 섞이지 않습니다. 포맷에 `%(threadName)s`를 넣으면 어느 작업자가 남긴 로그인지 구분됩니다. 여러 프로세스가 한 파일에 쓰는 경우는 [Python 로깅](python_logging.md)의 QueueHandler 방식을 참고합니다.

```python
import logging
logging.basicConfig(format="%(asctime)s %(threadName)s %(levelname)s %(message)s",
                    level=logging.INFO)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 점검표

| 점검 항목                                                   | 확인 |
|-------------------------------------------------------------|------|
| 작업이 I/O 위주인지 CPU 위주인지 먼저 측정했는가            | [ ]  |
| 작업자 수에 상한을 두었는가 (상대 서버·API 제한 고려)       | [ ]  |
| 모든 네트워크·외부 명령 호출에 timeout을 주었는가           | [ ]  |
| `future.result()`에서 작업 예외를 받아 기록하는가           | [ ]  |
| 공유 상태를 Lock·Queue로 보호했는가                         | [ ]  |
| 프로세스 사용 시 `if __name__ == "__main__":` 보호가 있는가 | [ ]  |
| 프로세스에 넘기는 함수·인자가 pickle 가능한가               | [ ]  |
| 스레드와 `fork`를 함께 쓰지 않는가                          | [ ]  |
| 종료 신호(Ctrl+C) 때 풀이 정리되는가 (`with` 문 사용)       | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Python Documentation: [threading](https://docs.python.org/3/library/threading.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [Python support for free threading](https://docs.python.org/3/howto/free-threading-python.html) — ★★★☆☆ (확인일 2026-11-16)
- PEP 703: [Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/) — ★★★☆☆ (확인일 2026-11-16)
- PEP 779: [Criteria for supported status for free-threaded Python](https://peps.python.org/pep-0779/) — ★★★☆☆ (확인일 2026-11-16)
- Python.org: [Python Releases](https://www.python.org/downloads/) (3.15.2, 3.14.10 확인) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
