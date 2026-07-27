# S3 Backup Script - Python 개념 분석

## 목차

| 섹션                                                                                           |
|------------------------------------------------------------------------------------------------|
| [1. 데코레이터 (Decorator)](#1-데코레이터-decorator)                                           |
| [2. 이터레이터 (Iterator)](#2-이터레이터-iterator)                                             |
| [3. 제너레이터 (Generator)](#3-제너레이터-generator)                                           |
| [4. 컨텍스트 매니저 (Context Manager) - with 문](#4-컨텍스트-매니저-context-manager---with-문) |
| [5. 예외 처리 (Exception Handling)](#5-예외-처리-exception-handling)                           |
| [6. 언패킹 (Unpacking)](#6-언패킹-unpacking)                                                   |
| [7. dict 활용](#7-dict-활용)                                                                   |
| [8. set 활용](#8-set-활용)                                                                     |
| [9. f-string 포맷팅](#9-f-string-포맷팅)                                                       |
| [10. 조건부 import](#10-조건부-import)                                                         |
| [11. 환경 변수 조작](#11-환경-변수-조작)                                                       |
| [12. 정규표현식 (re 모듈)](#12-정규표현식-re-모듈)                                             |
| [13. subprocess - 외부 명령 실행](#13-subprocess---외부-명령-실행)                             |
| [14. argparse - 커맨드라인 인자](#14-argparse---커맨드라인-인자)                               |
| [15. 사용되지 않은 개념](#15-사용되지-않은-개념)                                               |

---


`s3_file_upload.py`에 사용된 Python 개념을 분석합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 1. 데코레이터 (Decorator)

이 스크립트에는 데코레이터가 사용되지 않았습니다.

데코레이터를 적용할 수 있는 부분 (참고):

```python
# 현재 코드: upload_to_s3에서 직접 재시도 구현
for attempt in range(retries + 1):
    result = subprocess.run(cmd, ...)
    if result.returncode == 0:
        return

# 데코레이터 방식이라면:
@retry(max_retries=2, delay=5)
def upload_to_s3(local_path, s3_key):
    result = subprocess.run(cmd, ...)
    if result.returncode != 0:
        raise Exception(result.stderr)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 이터레이터 (Iterator)

### os.walk() - 디렉토리 트리 이터레이터

```python
# find_files_grouped_by_date, do_s3_upload, do_cleanup에서 사용
for root, _, files in os.walk(LOG_DIR):
    for filename in files:
        ...
```

`os.walk()`는 제너레이터 기반 이터레이터입니다.
디렉토리를 재귀 탐색하면서 `(dirpath, dirnames, filenames)` 튜플을 하나씩 반환합니다.
전체 파일 목록을 메모리에 올리지 않고 순회합니다.

### psutil.process_iter() - 프로세스 이터레이터

```python
# get_locked_files에서 사용
for proc in psutil.process_iter(['pid', 'name']):
    for f in proc.open_files():
        locked[os.path.abspath(f.path)] = (proc.pid, proc.name())
```

시스템의 모든 프로세스를 하나씩 순회하는 이터레이터입니다.
`['pid', 'name']`은 캐시할 속성을 지정하여 성능을 최적화합니다.

### glob.glob() - 파일 패턴 매칭

```python
# load_config, setup_logger에서 사용
config_files = glob.glob(os.path.join(SCRIPT_DIR, '*config.toml'))
```

패턴에 매칭되는 파일 경로 리스트를 반환합니다.

### str.splitlines() - 문자열 이터레이션

```python
# get_s3_file_list에서 사용
for line in result.stdout.strip().splitlines():
    parts = line.split()
```

문자열을 줄 단위로 분리하여 리스트로 반환합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 제너레이터 (Generator)

### 제너레이터 표현식 (Generator Expression)

```python
# any()와 함께 사용 - should_process_file
any(name_lower.endswith(ext) for ext in FILE_EXTENSIONS)
any(fnmatch.fnmatch(name_lower, p) for p in FILE_PATTERNS)
any(re.search(p, name_lower) for p in FILE_REGEX)
```

`any()` 안의 `for ... in ...`은 제너레이터 표현식입니다.
리스트를 만들지 않고 하나씩 평가하며, 첫 번째 True를 만나면 즉시 중단합니다 (short-circuit).

```python
# sum()과 함께 사용 - compress_group
original_size = sum(os.path.getsize(f) for f in file_paths)

# sum()과 함께 사용 - do_compress
total = sum(len(v) for v in date_groups.values())
```

리스트 컴프리헨션 `[...]`과 달리 `(...)`는 메모리를 절약합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 컨텍스트 매니저 (Context Manager) - with 문

### 파일 I/O

```python
# 여러 곳에서 사용
with open(config_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

with open(LOCK_FILE, 'w') as f:
    f.write(str(os.getpid()))
```

`with`문은 블록 종료 시 자동으로 `f.close()`를 호출합니다.
예외가 발생해도 파일이 안전하게 닫힙니다.

### 중첩 컨텍스트 매니저 - compress_group

```python
with zstd.open(output_path, 'wb', level=COMPRESSION_LEVEL) as zf:
    with tarfile.open(fileobj=zf, mode='w|') as tar:
        for fp in file_paths:
            tar.add(fp, arcname=os.path.relpath(fp, LOG_DIR))
```

zstd 압축 스트림 안에 tar 아카이브를 생성하는 중첩 구조입니다.
안쪽 `with`가 먼저 닫히고, 바깥쪽 `with`가 나중에 닫힙니다.
`mode='w|'`는 스트리밍 모드로, 파일을 순차적으로 추가합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 예외 처리 (Exception Handling)

### try-except-finally 패턴

```python
# 엔트리 포인트
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"[E{ERR_UNEXPECTED}] unexpected error: {e}")
        write_status({ERR_UNEXPECTED})
        raise
    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
```

- `try`: 정상 실행
- `except`: 예외 발생 시 에러 기록 후 `raise`로 재발생
- `finally`: 정상/예외 모두 실행 (lock 파일 정리)

### 다중 예외 타입

```python
# get_skip_count
except (FileNotFoundError, ValueError):
    return 0

# get_locked_files
except (psutil.AccessDenied, psutil.NoSuchProcess):
    continue
```

튜플로 여러 예외를 한 번에 처리합니다.

### SystemExit

```python
# config 에러 시
raise SystemExit(ERR_CONFIG)
```

`sys.exit()`와 동일. 종료 코드를 지정하여 프로세스를 종료합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 언패킹 (Unpacking)

### 튜플 언패킹

```python
# os.walk 반환값
for root, _, files in os.walk(LOG_DIR):

# compress_group 반환값
orig, comp, ratio, elapsed = compress_group(file_paths, output_path)

# locked_files dict 값
pid, pname = locked_files[abs_path]
```

`_`는 사용하지 않는 값을 무시하는 관례입니다.

### 함수 반환값 언패킹

```python
# load_config
CFG, CONFIG_PATH = load_config(args.config)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. dict 활용

### dict.setdefault() - 기본값 설정

```python
# find_files_grouped_by_date
groups.setdefault(date, []).append(file_path)
```

`date` 키가 없으면 빈 리스트를 생성하고, 있으면 기존 리스트에 추가합니다.
`if date not in groups: groups[date] = []` 와 동일하지만 한 줄로 처리합니다.

### dict.get() - 안전한 값 조회

```python
# config 선택 키
STABILITY_WAIT = CFG.get('STABILITY_WAIT', 2)

# S3 파일 사이즈 비교
if s3_files.get(s3_key) == local_size:
```

키가 없으면 기본값을 반환합니다. `KeyError` 방지.

### dict comprehension (리스트 컴프리헨션 활용)

```python
# load_config - 필수 키 검증
missing = [k for k in required if k not in cfg]
```

리스트 컴프리헨션으로 누락된 키를 한 줄로 추출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. set 활용

### set.add() - 에러 코드 수집

```python
error_codes = set()
error_codes.add(ERR_COMPRESS)
error_codes.add(ERR_S3_UPLOAD)
```

중복 없이 에러 코드를 수집합니다. 같은 에러가 여러 번 발생해도 1개만 저장됩니다.

### min() - 최소값

```python
# write_status
f.write(str(min(error_codes)))
```

set에서 가장 작은 값(가장 먼저 발생하는 단계의 에러)을 추출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. f-string 포맷팅

### 기본 포맷

```python
logger.info(f"config loaded: {os.path.basename(CONFIG_PATH)} (PRODUCT: {PRODUCT_NAME})")
```

### 숫자 포맷

```python
# 천 단위 콤마
f"{orig:,} -> {comp:,} bytes"
# 출력: 16,957,189 -> 1,348,297 bytes

# 소수점 자릿수
f"{ratio:.1f}% reduced, {elapsed:.2f}s"
# 출력: 92.0% reduced, 0.03s

# 디스크 용량
f"disk free: {free_gb:.1f}GB"
# 출력: disk free: 15.3GB
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 조건부 import

```python
# TOML은 사용할 때만 import
if config_path.endswith('.toml'):
    import tomllib
    with open(config_path, 'rb') as f:
        cfg = tomllib.load(f)
```

JSON config만 사용하는 환경에서 `tomllib` import를 피합니다.
Python 3.11 미만에서도 JSON으로는 동작 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 환경 변수 조작

```python
# OS 판별
if os.name == 'nt':
    _aws_home = os.path.join(os.environ['USERPROFILE'], '.aws')
else:
    _aws_home = '/home/sjyun/.aws'

# 환경 변수 설정
os.environ['AWS_CONFIG_FILE'] = os.path.join(_aws_home, 'config')
```

`os.environ`은 dict처럼 동작하며, 자식 프로세스(`subprocess.run`)에 전달됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 12. 정규표현식 (re 모듈)

### re.search() - 패턴 검색

```python
# extract_date
m = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
if m:
    return m.group(1) + m.group(2) + m.group(3)
```

`()` 그룹으로 캡처한 값을 `m.group(N)`으로 추출합니다.

### re.split() - 패턴 기반 분리

```python
# make_group_name
prefix = re.split(r'[_\-]?\d', name, maxsplit=1)[0].rstrip('_-')
```

첫 번째 숫자 앞에서 문자열을 분리하여 prefix를 추출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 13. subprocess - 외부 명령 실행

```python
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    raise Exception(result.stderr.strip())
```

- `capture_output=True`: stdout/stderr 캡처
- `text=True`: 바이트가 아닌 문자열로 반환
- `result.returncode`: 종료 코드 (0=성공)

[⬆ 목차로 돌아가기](#목차)

---

## 14. argparse - 커맨드라인 인자

```python
parser = argparse.ArgumentParser(description='S3 backup script')
parser.add_argument('--config', help='config 파일 경로')
args = parser.parse_args()
```

`--config` 옵션을 정의하고, `args.config`로 값을 가져옵니다.
`--help` 자동 생성, 잘못된 인자 시 에러 메시지 자동 출력.

[⬆ 목차로 돌아가기](#목차)

---

## 15. 사용되지 않은 개념

이 스크립트에서 사용하지 않은 Python 개념:

| 개념        | 미사용 이유                                   |
|-------------|-----------------------------------------------|
| 데코레이터  | 재시도 로직이 1곳뿐이라 직접 구현이 간결      |
| 클래스      | 절차적 스크립트로 충분                        |
| async/await | I/O 병렬 처리 불필요 (순차 실행)              |
| dataclass   | config를 dict로 처리하여 불필요               |
| typing      | 타입 힌트 미적용 (스크립트 규모에서 선택사항) |
| yield       | 제너레이터 함수 미사용 (표현식만 사용)        |

---

## 참고 자료

- Python Documentation: [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) — ★★★☆☆
- AWS SDK for Python: [boto3.amazonaws.com](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-03

**마지막 업데이트**: 2026-04-03

© 2026 siasia86. Licensed under CC BY 4.0.
