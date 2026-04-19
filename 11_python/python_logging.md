# Python logging 가이드

## 목차
1. [기초 사용법](#기초-사용법)
2. [로그 레벨](#로그-레벨)
3. [basicConfig 매개변수](#basicconfig-매개변수)
4. [포맷 설정](#포맷-설정)
5. [로거 객체 사용](#로거-객체-사용)
6. [핸들러](#핸들러)
7. [로그 로테이션](#로그-로테이션)
8. [고급 기능](#고급-기능)
9. [실무 베스트 프랙티스](#실무-베스트-프랙티스)
10. [설정 파일 사용](#설정-파일-사용)
11. [자주 사용하는 패턴](#자주-사용하는-패턴)
12. [문제 해결](#문제-해결)
13. [요약](#요약)

---

## 기초 사용법

### 가장 간단한 사용
```python
import logging

logging.basicConfig(level=logging.INFO)
logging.info("작업 시작")
logging.error("에러 발생")
```

**실행 결과:**
```
INFO:root:작업 시작
ERROR:root:에러 발생
```

### 파일로 저장
```python
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("작업 완료")
```

**실행 결과 (app.log 파일 내용):**
```
2026-03-03 16:42:38,959 - INFO - 작업 완료
```

---

## 로그 레벨

### 레벨 종류 (낮은 순서 → 높은 순서)
```python
logging.debug("디버그 정보")      # 10 - 개발 중 상세 정보
logging.info("일반 정보")         # 20 - 진행 상황
logging.warning("경고")           # 30 - 주의 필요 (기본값)
logging.error("에러")             # 40 - 오류 발생
logging.critical("심각한 에러")   # 50 - 시스템 중단급
```

### 레벨 설정
```python
import logging

# INFO 이상만 출력 (DEBUG는 무시)
logging.basicConfig(level=logging.INFO)

logging.debug("안 보임")
logging.info("보임")
logging.error("보임")
```

**실행 결과:**
```
INFO:root:보임
ERROR:root:보임
```
> DEBUG 레벨은 INFO보다 낮으므로 출력되지 않음

---

## basicConfig 매개변수

### 전체 매개변수
```python
logging.basicConfig(
    filename="app.log",      # 로그 파일 경로
    filemode="a",            # 파일 모드 ("a": 추가, "w": 덮어쓰기)
    level=logging.INFO,      # 로그 레벨
    format="%(asctime)s - %(levelname)s - %(message)s",  # 포맷
    datefmt="%Y-%m-%d %H:%M:%S",  # 날짜 포맷
    encoding="utf-8",        # 파일 인코딩
    force=True               # 기존 설정 덮어쓰기 (Python 3.8+)
)
```

### 주요 매개변수 설명

#### filename
```python
filename="app.log"        # 파일에 저장
filename=None             # 화면 출력 (기본값)
```

#### filemode
```python
filemode="a"  # append (추가, 기본값)
filemode="w"  # write (덮어쓰기)
```

#### level
```python
level=logging.DEBUG      # 모든 로그
level=logging.INFO       # 일반 정보 이상
level=logging.WARNING    # 경고 이상 (기본값)
level=logging.ERROR      # 에러 이상
level=logging.CRITICAL   # 심각한 에러만
```

#### encoding
```python
encoding="utf-8"   # UTF-8 (한글 지원)
encoding="cp949"   # Windows 한글
```

---

## 포맷 설정

### 주요 포맷 변수
| 변수 | 설명 | 예시 |
|------|------|------|
| `%(asctime)s` | 시간 | 2026-03-03 14:06:45 |
| `%(levelname)s` | 레벨 | INFO, ERROR 등 |
| `%(message)s` | 로그 메시지 | 작업 시작 |
| `%(name)s` | 로거 이름 | root, __main__ |
| `%(filename)s` | 파일명 | app.py |
| `%(funcName)s` | 함수명 | my_function |
| `%(lineno)d` | 줄 번호 | 10 |
| `%(process)d` | 프로세스 ID | 12345 |
| `%(thread)d` | 스레드 ID | 67890 |
| `%(pathname)s` | 전체 경로 | /home/user/app.py |
| `%(module)s` | 모듈명 | app |

### 포맷 예제

#### 간단한 포맷
```python
format="%(levelname)s: %(message)s"
# 출력: INFO: 작업 시작
```

#### 상세 포맷
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.info("작업 시작")
```

**실행 결과:**
```
2026-03-03 16:42:38,959 - root - INFO - 작업 시작
```

#### 디버깅용 포맷
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
)
logging.info("작업 시작")
```

**실행 결과:**
```
2026-03-03 16:42:56,303 [INFO] test_debug_format.py:7 - 작업 시작
```
> 파일명과 줄 번호가 포함되어 디버깅에 유용

### 날짜 포맷 (datefmt)
```python
datefmt="%Y-%m-%d %H:%M:%S"        # 2026-03-03 14:06:45
datefmt="%Y/%m/%d %I:%M:%S %p"     # 2026/03/03 02:06:45 PM
datefmt="%Y-%m-%d"                 # 2026-03-03
datefmt="%H:%M:%S"                 # 14:06:45
```

---

## 로거 객체 사용

### 기본 사용 (권장)
```python
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 핸들러 추가
handler = logging.FileHandler("app.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

logger.info("모듈별 로그")
```

### 왜 로거 객체를 사용하나?
- 모듈별로 독립적인 로그 관리
- 여러 핸들러 동시 사용 가능
- 더 세밀한 제어 가능

---

## 핸들러

### 파일 + 화면 동시 출력
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 파일 핸들러
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 포맷 설정
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.debug("파일에만 저장")
logger.info("파일 + 화면 출력")
```

**실행 결과 (화면):**
```
2026-03-03 16:43:00,123 - INFO - 파일 + 화면 출력
```
> DEBUG는 콘솔 레벨(INFO)보다 낮아서 화면에 안 보임

**실행 결과 (app.log 파일):**
```
2026-03-03 16:43:00,123 - DEBUG - 파일에만 저장
2026-03-03 16:43:00,123 - INFO - 파일 + 화면 출력
```

### 여러 파일에 로그 분리
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 모든 로그
all_handler = logging.FileHandler("all.log", encoding="utf-8")
all_handler.setLevel(logging.DEBUG)

# 에러만
error_handler = logging.FileHandler("error.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
all_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

logger.addHandler(all_handler)
logger.addHandler(error_handler)

logger.info("일반 로그")    # all.log에만
logger.error("에러 로그")   # all.log + error.log 둘 다
```

### basicConfig로 여러 핸들러
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
```

---

## 로그 로테이션

### 크기별 로테이션
```python
from logging.handlers import RotatingFileHandler
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 10MB마다 새 파일, 최대 5개 보관
handler = RotatingFileHandler(
    "app.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("로그 메시지")
# 파일: app.log, app.log.1, app.log.2, ..., app.log.5
```

### 날짜별 로테이션
```python
from logging.handlers import TimedRotatingFileHandler
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 매일 자정에 새 파일, 7일치 보관
handler = TimedRotatingFileHandler(
    "app.log",
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("로그 메시지")
# 파일: app.log, app.log.2026-03-02, app.log.2026-03-01, ...
```

### when 옵션
| 옵션 | 설명 |
|------|------|
| `S` | 초 |
| `M` | 분 |
| `H` | 시간 |
| `D` | 일 |
| `midnight` | 자정 |
| `W0`~`W6` | 요일 (월~일) |

---

## 고급 기능

### 예외 로깅
```python
import logging

logging.basicConfig(level=logging.ERROR)

try:
    result = 10 / 0
except Exception as e:
    # 방법 1: exc_info=True
    logging.error("계산 에러", exc_info=True)
    
    # 방법 2: exception() - 자동으로 exc_info=True
    logging.exception("계산 에러")
```

**실행 결과:**
```
ERROR:root:계산 에러
Traceback (most recent call last):
  File "test.py", line 6, in <module>
    result = 10 / 0
             ~~~^~~
ZeroDivisionError: division by zero
```
> 스택 트레이스가 자동으로 포함됨

### 변수 포함 로깅
```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

username = "홍길동"
count = 100

# 방법 1: % 포맷 (권장 - lazy evaluation)
logging.info("사용자: %s, 개수: %d", username, count)

# 방법 2: f-string
logging.info(f"사용자: {username}, 개수: {count}")

# 방법 3: .format()
logging.info("사용자: {}, 개수: {}".format(username, count))
```

**실행 결과:**
```
INFO: 사용자: 홍길동, 개수: 100
INFO: 사용자: 홍길동, 개수: 100
INFO: 사용자: 홍길동, 개수: 100
```

### 성능 최적화 (lazy evaluation)
```python
# 나쁜 예 (항상 문자열 생성)
logging.debug("값: " + str(expensive_function()))

# 좋은 예 (DEBUG 레벨일 때만 실행)
logging.debug("값: %s", expensive_function())
```
> % 포맷은 로그 레벨이 맞을 때만 문자열 변환 수행

### 컨텍스트 정보 추가
```python
import logging

# 먼저 핸들러 설정 필요
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LoggerAdapter 사용
adapter = logging.LoggerAdapter(logger, {"user": "admin", "ip": "192.168.1.1"})
adapter.info("로그인")

# extra 사용 (포맷에 해당 필드 추가 필요)
logger.info("작업 완료", extra={"user_id": 123, "action": "upload"})
```

### 커스텀 필터
```python
import logging

class IPFilter(logging.Filter):
    def filter(self, record):
        record.ip = "192.168.1.1"  # 추가 정보
        return True  # True: 로그 출력, False: 무시

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addFilter(IPFilter())

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(ip)s - %(message)s"))
logger.addHandler(handler)

logger.info("접속")
```

**실행 결과:**
```
192.168.1.1 - 접속
```

### JSON 로그 (구조화된 로그)
```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }
        return json.dumps(log_data, ensure_ascii=False)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

logger.info("JSON 로그")
```

**실행 결과:**
```json
{"timestamp": "2026-03-03 16:43:48", "level": "INFO", "message": "JSON 로그", "module": "test_json", "line": 22}
```
> ELK 스택, CloudWatch 등 로그 분석 도구와 연동 시 유용

---

## 설정 파일 사용

### INI 파일 설정

**logging.conf:**
```ini
[loggers]
keys=root

[handlers]
keys=fileHandler,consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=fileHandler,consoleHandler

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=("app.log", "a", "utf-8")

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

**사용:**
```python
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)
logger.info("설정 파일 사용")
```

### 딕셔너리 설정 (Python 3.2+)
```python
import logging.config

config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    }
}

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
logger.info("딕셔너리 설정 사용")
```

---

## 실무 베스트 프랙티스

### 재사용 가능한 로거 설정 함수
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """로거 설정 함수"""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# 사용
logger = setup_logger("myapp", "app.log")
logger.info("애플리케이션 시작")
```

### 모듈별 로거 사용
```python
# module1.py
import logging
logger = logging.getLogger(__name__)

def function1():
    logger.info("module1 실행")

# module2.py
import logging
logger = logging.getLogger(__name__)

def function2():
    logger.info("module2 실행")

# main.py
import logging
import module1
import module2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

module1.function1()  # 2026-03-03 14:06:45 - module1 - INFO - module1 실행
module2.function2()  # 2026-03-03 14:06:45 - module2 - INFO - module2 실행
```

### 개발/프로덕션 환경 분리
```python
import logging
import os

# 환경 변수로 레벨 설정
log_level = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.debug("디버그 정보")  # 개발 환경에서만
logger.info("일반 정보")
```

**사용 예:**
```bash
# 개발 환경
LOG_LEVEL=DEBUG python app.py

# 프로덕션 환경
LOG_LEVEL=WARNING python app.py
```

### 멀티프로세싱 로깅
```python
from logging.handlers import QueueHandler, QueueListener
import multiprocessing
import logging

def worker(queue):
    logger = logging.getLogger(__name__)
    logger.addHandler(QueueHandler(queue))
    logger.setLevel(logging.INFO)
    logger.info("작업 시작")

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    handler = logging.FileHandler("multi.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    listener = QueueListener(queue, handler)
    listener.start()
    
    processes = []
    for i in range(4):
        p = multiprocessing.Process(target=worker, args=(queue,))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
    
    listener.stop()
```

---

## 자주 사용하는 패턴

### 패턴 1: 간단한 스크립트
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("시작")
logging.error("에러")
```

### 패턴 2: 파일 + 화면 출력
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
```

### 패턴 3: 로그 로테이션
```python
from logging.handlers import RotatingFileHandler
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "app.log",
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding="utf-8"
)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)
```

### 패턴 4: 모듈별 로거
```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("함수 실행")
```

---

## 문제 해결

### 로그가 중복 출력될 때
```python
# 문제: 핸들러가 중복 추가됨
logger = logging.getLogger(__name__)
logger.addHandler(handler)  # 여러 번 호출 시 중복

# 해결 1: 핸들러 확인
if not logger.handlers:
    logger.addHandler(handler)

# 해결 2: 기존 핸들러 제거
logger.handlers.clear()
logger.addHandler(handler)
```

### basicConfig가 작동 안 할 때
```python
# 문제: 이미 로거가 설정됨
logging.info("첫 호출")  # 기본 설정 적용
logging.basicConfig(...)  # 무시됨

# 해결: force=True 사용 (Python 3.8+)
logging.basicConfig(..., force=True)
```

### 한글이 깨질 때
```python
# 해결: encoding 지정
logging.basicConfig(
    filename="app.log",
    encoding="utf-8"
)

# 또는 핸들러에서
handler = logging.FileHandler("app.log", encoding="utf-8")
```

---

## 요약

### 언제 무엇을 사용할까?

| 상황 | 방법 |
|------|------|
| 간단한 스크립트 | `logging.basicConfig()` |
| 파일 저장 | `filename="app.log"` |
| 파일 + 화면 | `handlers=[FileHandler, StreamHandler]` |
| 로그 로테이션 | `RotatingFileHandler` 또는 `TimedRotatingFileHandler` |
| 모듈별 관리 | `logger = logging.getLogger(__name__)` |
| 에러 추적 | `logging.exception()` 또는 `exc_info=True` |
| 프로덕션 | 로그 로테이션 + 레벨 분리 + 설정 파일 |

### 추천 설정 (실무)
```python
import logging
from logging.handlers import RotatingFileHandler

# 로거 생성
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 파일: 모든 로그
file_handler = RotatingFileHandler(
    "app.log",
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)

# 파일: 에러만
error_handler = RotatingFileHandler(
    "error.log",
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)

# 화면: INFO 이상
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 포맷
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

# 사용
logger.info("애플리케이션 시작")
logger.error("에러 발생")
```
