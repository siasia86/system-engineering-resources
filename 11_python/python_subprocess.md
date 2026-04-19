# Python subprocess 모듈

외부 명령어 실행과 프로세스 관리를 위한 subprocess 모듈 가이드입니다.

## 목차
- [subprocess.run()](#subprocessrun)
- [입출력 캡처](#입출력-캡처)
- [shell 옵션](#shell-옵션)
- [Popen](#popen)
- [실전 예제](#실전-예제)
- [요약](#요약)

---

## subprocess.run()

### 기본 사용법

```python
import subprocess

# 기본 실행
result = subprocess.run(['ls', '-la'])
print(result.returncode)  # 0 (성공)

# 문자열 결과 받기
result = subprocess.run(['hostname'], capture_output=True, text=True)
print(result.stdout.strip())  # 호스트명 출력
```

### 주요 매개변수

```python
result = subprocess.run(
    ['command', 'arg1', 'arg2'],
    capture_output=True,   # stdout/stderr 캡처
    text=True,             # 바이트 대신 문자열 반환
    timeout=30,            # 타임아웃 (초)
    check=True,            # 실패 시 CalledProcessError 발생
    cwd='/tmp',            # 작업 디렉토리
    env={'PATH': '/usr/bin'}  # 환경변수
)
```

### returncode

```python
result = subprocess.run(['grep', 'pattern', 'file.txt'], capture_output=True, text=True)

if result.returncode == 0:
    print("패턴 발견")
elif result.returncode == 1:
    print("패턴 없음")
else:
    print(f"에러 발생: {result.stderr}")
```

---

## 입출력 캡처

### stdout / stderr

```python
# 개별 캡처
result = subprocess.run(['ls', '/nonexistent'], capture_output=True, text=True)
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")

# PIPE 직접 사용
result = subprocess.run(
    ['cat', '/etc/hostname'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# stderr를 stdout으로 합치기
result = subprocess.run(
    ['command'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)
```

### stdin 전달

```python
# 문자열 입력
result = subprocess.run(
    ['grep', 'error'],
    input="line1\nerror found\nline3\n",
    capture_output=True, text=True
)
print(result.stdout)  # error found
```

---

## shell 옵션

### shell=True vs shell=False

```python
# shell=False (기본값, 권장)
# 명령어와 인자를 리스트로 전달
result = subprocess.run(['ls', '-la', '/tmp'], capture_output=True, text=True)

# shell=True (파이프, 리다이렉션 필요 시)
# 문자열로 전달
result = subprocess.run('ls -la /tmp | grep log', shell=True, capture_output=True, text=True)

# ⚠️ shell=True + 사용자 입력 = 보안 위험 (Shell Injection)
# 절대 사용자 입력을 shell=True와 함께 사용하지 말 것
```

### 파이프라인 구현

```python
# shell=True 방식
result = subprocess.run(
    'cat /var/log/syslog | grep error | wc -l',
    shell=True, capture_output=True, text=True
)

# 안전한 방식 (Popen 체이닝)
p1 = subprocess.Popen(['cat', '/var/log/syslog'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', 'error'], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
output = p2.communicate()[0]
```

---

## Popen

### 기본 사용법

```python
# 비동기 실행
proc = subprocess.Popen(['long_running_command'], stdout=subprocess.PIPE, text=True)

# 실시간 출력 읽기
for line in proc.stdout:
    print(line, end='')

proc.wait()
print(f"종료 코드: {proc.returncode}")
```

### communicate()

```python
proc = subprocess.Popen(
    ['sort'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)
stdout, stderr = proc.communicate(input="banana\napple\ncherry\n")
print(stdout)  # apple\nbanana\ncherry\n
```

### 타임아웃

```python
try:
    result = subprocess.run(['sleep', '60'], timeout=5)
except subprocess.TimeoutExpired:
    print("타임아웃 발생")

# Popen에서 타임아웃
proc = subprocess.Popen(['sleep', '60'])
try:
    proc.wait(timeout=5)
except subprocess.TimeoutExpired:
    proc.kill()
    print("프로세스 강제 종료")
```


### 환경변수 전달

```python
import os

# 현재 환경변수에 추가
env = os.environ.copy()
env['MY_VAR'] = 'hello'
result = subprocess.run(['printenv', 'MY_VAR'], capture_output=True, text=True, env=env)
print(result.stdout.strip())  # 'hello'
```

### CalledProcessError 처리

```python
try:
    result = subprocess.run(
        ['ls', '/nonexistent'],
        capture_output=True, text=True, check=True
    )
except subprocess.CalledProcessError as e:
    print(f"종료 코드: {e.returncode}")
    print(f"stderr: {e.stderr}")
```

---

## 실전 예제

### 디스크 사용량 확인

```python
def check_disk_usage(threshold=80):
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    for line in result.stdout.strip().split('\n')[1:]:
        parts = line.split()
        usage = int(parts[4].replace('%', ''))
        if usage >= threshold:
            print(f"⚠️ {parts[5]}: {parts[4]} 사용 중")
```

### 서비스 상태 확인

```python
def check_service(service_name):
    result = subprocess.run(
        ['systemctl', 'is-active', service_name],
        capture_output=True, text=True
    )
    status = result.stdout.strip()
    return status == 'active'

services = ['nginx', 'postgresql', 'redis']
for svc in services:
    status = "🟢" if check_service(svc) else "🔴"
    print(f"{status} {svc}")
```

### Ping 체크

```python
def ping_host(host, count=3):
    result = subprocess.run(
        ['ping', '-c', str(count), '-W', '2', host],
        capture_output=True, text=True
    )
    return result.returncode == 0

hosts = ['8.8.8.8', '1.1.1.1', '192.168.1.1']
for host in hosts:
    status = "🟢" if ping_host(host) else "🔴"
    print(f"{status} {host}")
```

### 로그 검색

```python
def search_log(log_file, pattern, lines=10):
    result = subprocess.run(
        ['grep', '-i', '-n', pattern, log_file],
        capture_output=True, text=True
    )
    matches = result.stdout.strip().split('\n')
    return matches[-lines:] if matches[0] else []
```

---

## 요약

| 함수 | 용도 | 동기/비동기 |
|------|------|-------------|
| `subprocess.run()` | 명령 실행 후 결과 반환 | 동기 |
| `subprocess.Popen()` | 세밀한 프로세스 제어 | 비동기 |

**핵심 포인트:**
- 기본적으로 `subprocess.run()` 사용
- `shell=True`는 보안상 최소한으로 사용
- 사용자 입력은 반드시 `shell=False`로 처리
- 장시간 명령은 `timeout` 설정 필수

**관련 문서:**
- [파일 입출력](./python_file_io.md) - 파일 처리
- [예외 처리](./python_exceptions.md) - 에러 핸들링
- [로깅](./python_logging.md) - 로그 기록
