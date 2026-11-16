# Python 디버깅과 프로파일링 (pdb, faulthandler, cProfile, tracemalloc)

운영 중인 Python 스크립트·서비스가 오류를 내거나, 멈추거나, 느려지거나, 메모리를 계속 늘릴 때 표준 라이브러리로 원인을 좁히는 방법을 정리합니다. 판 번호와 기능 추가 판은 Python 3.15.2 문서 기준입니다(2026-11-16 확인).

## 목차

| 섹션                                                                                                              |
|-------------------------------------------------------------------------------------------------------------------|
| [1. 증상별 도구 선택](#1-증상별-도구-선택) / [2. traceback 읽기와 기록](#2-traceback-읽기와-기록)                 |
| [3. pdb 대화형 디버거](#3-pdb-대화형-디버거) / [4. 실행 중 프로세스 붙기](#4-실행-중-프로세스-붙기)               |
| [5. faulthandler로 멈춤과 충돌 진단](#5-faulthandler로-멈춤과-충돌-진단) / [6. CPU 프로파일링](#6-cpu-프로파일링) |
| [7. 메모리 추적 tracemalloc](#7-메모리-추적-tracemalloc) / [8. 점검표](#8-점검표)                                 |

---

## 1. 증상별 도구 선택

| 증상                              | 먼저 쓸 도구                                        | 얻는 정보                    |
|-----------------------------------|-----------------------------------------------------|------------------------------|
| 예외로 종료                       | traceback, `python -m pdb`(사후 분석)               | 실패 위치와 그 시점 변수 값  |
| 응답 없이 멈춤                    | `faulthandler` + `SIGUSR1`, `python -m pdb -p`      | 모든 스레드의 현재 호출 위치 |
| Segmentation fault 등 비정상 종료 | `python -X faulthandler`                            | 충돌 직전 Python·C 스택      |
| 느림                              | `profiling.sampling`(3.15+), `cProfile`             | 시간을 많이 쓰는 함수        |
| 메모리 증가                       | `tracemalloc`                                       | 메모리를 할당한 코드 줄      |
| 운영 서버라 코드 수정 불가        | `python -m pdb -p PID`, `profiling.sampling attach` | 재시작 없이 상태 확인        |

원칙은 "재현 → 관찰 → 가설 → 확인" 순서입니다. 로그와 traceback으로 위치를 좁힌 뒤에 디버거를 붙이고, 느림은 추측 대신 프로파일러 결과로 판단합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. traceback 읽기와 기록

traceback은 예외가 난 지점까지의 호출 경로입니다. 맨 아래 줄이 예외 종류와 메시지, 그 바로 위가 실제로 실패한 코드입니다. `During handling of the above exception, another exception occurred:`가 보이면 예외 처리 중에 또 다른 예외가 난 것이므로 위쪽 원래 예외부터 봅니다.

```python
import logging
import traceback

log = logging.getLogger(__name__)

try:
    run_job()
except Exception:
    log.exception("job failed")            # ERROR 수준 + traceback 자동 포함
    # 또는 문자열로 받기
    text = traceback.format_exc()
```

| 방법                      | 용도                                          |
|---------------------------|-----------------------------------------------|
| `log.exception("msg")`    | except 블록 안에서 traceback까지 로그에 기록  |
| `traceback.format_exc()`  | traceback을 문자열로 받아 알림·파일에 저장    |
| `traceback.print_stack()` | 예외 없이 현재 호출 경로만 출력               |
| `sys.excepthook` 교체     | 처리되지 않은 예외를 한곳에서 기록            |
| `python -X dev script.py` | 개발 모드. 경고·자원 누수 경고를 더 많이 표시 |

`except Exception: pass`처럼 예외를 삼키면 원인을 찾을 근거가 사라집니다. 무시해야 한다면 최소한 `log.debug(..., exc_info=True)`로 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. pdb 대화형 디버거

pdb는 표준 라이브러리 디버거입니다. 실행을 멈추고 변수 값을 보거나 한 줄씩 실행할 수 있습니다.

### 시작 방법

```python
def parse(line):
    breakpoint()          # 여기서 멈춤 (3.7+), import pdb; pdb.set_trace()와 같음
    return line.split()
```

```bash
# 처음부터 디버거로 실행 (첫 줄에서 멈춤)
python3 -m pdb script.py --config prod.yaml

# 모듈 실행
python3 -m pdb -m mypackage.cli

# 시작하자마자 계속 실행하고, 예외가 나면 그 위치에서 멈춤
python3 -m pdb -c continue script.py

# breakpoint() 호출을 모두 무시 (운영 환경에서 실수로 남은 경우 대비)
PYTHONBREAKPOINT=0 python3 script.py
```

`python -m pdb`로 실행한 프로그램이 예외로 끝나면 사후 분석(post-mortem) 모드로 들어가 실패 시점의 변수를 볼 수 있습니다. 대화형 셸에서는 예외 직후 `import pdb; pdb.pm()`으로 같은 일을 합니다.

### 주요 명령

| 명령                   | 동작                                         |
|------------------------|----------------------------------------------|
| `n` (next)             | 다음 줄 실행, 함수 호출 안으로 들어가지 않음 |
| `s` (step)             | 호출되는 함수 안으로 들어감                  |
| `c` (continue)         | 다음 중단점까지 실행                         |
| `r` (return)           | 현재 함수가 반환할 때까지 실행               |
| `b 파일:줄` / `b 함수` | 중단점 설정, 인자 없이 `b`는 목록            |
| `b 42, count > 100`    | 조건부 중단점                                |
| `tbreak 42`            | 한 번만 멈추는 중단점                        |
| `l` / `ll`             | 주변 11줄 / 현재 함수 전체 소스              |
| `p 식` / `pp 식`       | 값 출력 / 보기 좋게 출력                     |
| `w` (where)            | 호출 스택 출력                               |
| `u` / `d`              | 스택 위·아래 프레임으로 이동                 |
| `display 식`           | 값이 바뀔 때마다 표시                        |
| `interact`             | 현재 범위에서 Python 대화형 셸 시작          |
| `q` (quit)             | 디버거 종료와 함께 프로그램 중단             |

빈 줄을 입력하면 직전 명령을 반복합니다. 명령 이름과 겹치는 변수(예: `n`)를 보려면 `p n` 또는 `!n`을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 실행 중 프로세스 붙기

3.14부터 `python -m pdb -p PID`로 이미 실행 중인 Python 프로세스에 디버거를 붙일 수 있습니다(PEP 768 원격 디버깅 인터페이스). 서비스를 재시작하지 않고 멈춘 위치를 확인할 때 씁니다.

```bash
pgrep -af 'python.*worker.py'       # 대상 PID 확인
sudo python3 -m pdb -p 12345        # 대상과 같은 Python 판(3.14+) 필요
```

- 시스템 호출이나 I/O에서 막혀 있는 프로세스는 다음 바이트코드를 실행하거나 시그널을 받은 뒤에야 응답합니다.
- 한 프로세스에는 추적기(tracer)가 하나만 붙습니다. `strace`나 `gdb`가 이미 붙어 있으면 실패합니다.
- 리눅스에서 Yama `ptrace_scope` 설정이 다른 프로세스 추적을 막을 수 있습니다. 현재 값은 `cat /proc/sys/kernel/yama/ptrace_scope`로 확인합니다.
- 컨테이너에서는 seccomp 정책이 `ptrace`를 막을 수 있습니다.

🟡 주의: `ptrace_scope`를 0으로 낮추거나 `CAP_SYS_PTRACE`를 주면 시스템 보안 수준이 낮아집니다. 공식 문서도 보안 요구가 낮은 환경에서만 쓰라고 안내합니다. 운영 서버에서는 작업 후 원래 값으로 되돌립니다.

### 원격 디버깅 차단 (보안 강화)

원격 디버깅 인터페이스를 쓰지 않는 서비스는 아래 중 하나로 끌 수 있습니다. 운영체제 수준의 `ptrace`·`/proc` 접근 자체를 막지는 않으므로 심층 방어 수단으로 봅니다.

| 방법                             | 적용 시점                    |
|----------------------------------|------------------------------|
| `PYTHON_DISABLE_REMOTE_DEBUG=1`  | 인터프리터 시작 전 환경 변수 |
| `python -X disable-remote-debug` | 명령줄 옵션                  |
| `--without-remote-debug`         | 소스 빌드 옵션               |

[⬆ 목차로 돌아가기](#목차)

---

## 5. faulthandler로 멈춤과 충돌 진단

`faulthandler`는 C로 구현되어 인터프리터가 충돌하거나 교착 상태일 때도 traceback을 출력합니다.

### 충돌 시 스택 출력

```bash
python3 -X faulthandler app.py
# 또는
PYTHONFAULTHANDLER=1 python3 app.py
```

SIGSEGV·SIGFPE·SIGABRT·SIGBUS·SIGILL을 받으면 모든 스레드의 Python traceback을 표준 에러에 씁니다. 3.14부터는 C 스택도 함께 출력합니다(`backtrace(3)` 지원 시스템).

### 멈춘 서비스의 현재 위치 보기

```python
import faulthandler
import signal

faulthandler.register(signal.SIGUSR1)       # Windows 미지원
```

```bash
kill -USR1 12345                            # 표준 에러(또는 지정 파일)에 스택 출력
journalctl -u myworker.service -n 100       # systemd 서비스라면 로그에서 확인
```

### 일정 시간 넘으면 자동 출력

```python
import faulthandler

faulthandler.dump_traceback_later(300, repeat=True)   # 300초마다 전체 스레드 스택
try:
    long_batch()
finally:
    faulthandler.cancel_dump_traceback_later()
```

- `exit=True`를 주면 출력 뒤 `_exit(1)`로 즉시 종료하며 파일 버퍼를 비우지 않습니다.
- 출력 파일을 지정했다면 핸들러를 끄기 전까지 그 파일을 닫지 않습니다.
- 출력은 ASCII만, 문자열은 500자까지로 잘립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. CPU 프로파일링

프로파일러는 어떤 함수가 시간을 얼마나 쓰는지 측정합니다. 3.15에서 내장 프로파일러가 `profiling` 패키지로 묶였습니다.

| 도구                    | 방식                                | 부하      | 판                             |
|-------------------------|-------------------------------------|-----------|--------------------------------|
| `profiling.sampling`    | 일정 간격으로 호출 스택을 표본 수집 | 낮음      | 3.15+                          |
| `profiling.tracing`     | 모든 호출·반환을 기록 (결정적)      | 높음      | 3.15+                          |
| `cProfile`              | `profiling.tracing`의 별칭          | 높음      | 기존 코드 그대로 동작          |
| `profile` (순수 Python) | 결정적, 매우 느림                   | 매우 높음 | 3.15 사용 중단, 3.17 제거 예정 |

### cProfile (모든 지원 판)

```bash
# 누적 시간 기준 상위 함수 출력
python3 -m cProfile -s cumulative script.py | head -30

# 결과를 파일로 저장한 뒤 분석
python3 -m cProfile -o out.prof script.py
python3 -m pstats out.prof        # 대화형: sort cumulative / stats 20
```

```python
import cProfile
import pstats

with cProfile.Profile() as pr:          # 3.8+ 컨텍스트 매니저
    run_job()
pstats.Stats(pr).sort_stats("cumulative").print_stats(15)
```

| 열        | 뜻                                     |
|-----------|----------------------------------------|
| `ncalls`  | 호출 횟수                              |
| `tottime` | 함수 자체에서 쓴 시간 (하위 호출 제외) |
| `cumtime` | 하위 호출을 포함한 누적 시간           |
| `percall` | 호출 1회당 시간                        |

`cumtime`이 큰 함수에서 출발해 `tottime`이 큰 함수를 찾으면 실제 병목에 가까워집니다.

### profiling.sampling (3.15+)

```bash
python3 -m profiling.sampling run script.py
python3 -m profiling.sampling run --flamegraph script.py   # 대화형 flame graph
sudo python3 -m profiling.sampling attach 12345            # 실행 중 프로세스
```

표본 수집 방식은 부하가 낮아 운영 중인 프로세스에 붙여 보기 좋습니다. `attach`는 4절과 같은 `ptrace` 권한 조건을 따릅니다. 이 밖의 옵션(`--mode`, `-a` 등)은 공식 문서에서 사용하는 판의 설명을 확인합니다.

### 짧은 코드 비교

```bash
python3 -m timeit -s 'data = list(range(10000))' 'sum(data)'
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 메모리 추적 tracemalloc

`tracemalloc`은 Python 객체 메모리를 어느 코드 줄이 할당했는지 기록합니다. 장시간 실행 서비스의 메모리 증가(누수 의심)를 볼 때 두 시점의 스냅숏을 비교합니다.

```python
import tracemalloc

tracemalloc.start(10)                    # 호출 스택 10단계까지 기록

snap1 = tracemalloc.take_snapshot()
for _ in range(1000):
    handle_request()
snap2 = tracemalloc.take_snapshot()

for stat in snap2.compare_to(snap1, "lineno")[:10]:
    print(stat)                          # 증가량이 큰 줄부터 출력

current, peak = tracemalloc.get_traced_memory()
print(f"current={current/1024:.0f}KiB peak={peak/1024:.0f}KiB")
```

```bash
# 코드 수정 없이 시작부터 추적
PYTHONTRACEMALLOC=10 python3 app.py
python3 -X tracemalloc=10 app.py
```

- 추적 중에는 메모리와 속도 부하가 생깁니다. 재현 환경에서 쓰고 운영에서는 짧게만 켭니다.
- C 확장이 Python 할당자를 거치지 않고 직접 잡은 메모리는 보이지 않습니다. 프로세스 RSS(`ps -o rss= -p PID`)와 함께 봅니다.
- 흔한 원인은 끝없이 커지는 전역 dict·list 캐시, 해제되지 않는 순환 참조, 닫지 않은 파일·소켓입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 점검표

| 점검 항목                                                            | 확인 |
|----------------------------------------------------------------------|------|
| 예외를 삼키지 않고 traceback을 로그에 남기는가                       | [ ]  |
| 운영 코드에 `breakpoint()`가 남아 있지 않은가 (`PYTHONBREAKPOINT=0`) | [ ]  |
| 장시간 서비스에 `faulthandler.register(SIGUSR1)`를 넣었는가          | [ ]  |
| 멈춤 조사 전에 스택(`kill -USR1`, `pdb -p`)을 먼저 확보했는가        | [ ]  |
| 성능 판단을 프로파일 결과로 했는가                                   | [ ]  |
| 메모리 조사 때 두 시점 스냅숏을 비교했는가                           | [ ]  |
| `ptrace` 권한 완화를 작업 후 되돌렸는가                              | [ ]  |
| 원격 디버깅이 필요 없는 서비스에서 차단 옵션을 검토했는가            | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Python Documentation: [pdb — The Python Debugger](https://docs.python.org/3/library/pdb.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [Remote debugging attachment protocol](https://docs.python.org/3/howto/remote_debugging.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [faulthandler](https://docs.python.org/3/library/faulthandler.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [profiling — Python profilers](https://docs.python.org/3/library/profiling.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [tracemalloc](https://docs.python.org/3/library/tracemalloc.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [traceback](https://docs.python.org/3/library/traceback.html) — ★★★☆☆ (확인일 2026-11-16)
- PEP 768: [Safe external debugger interface for CPython](https://peps.python.org/pep-0768/) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
