# Bash trap 가이드

## trap이란?

`trap`은 **시그널이나 특정 이벤트를 감지해서 명령을 실행**하는 Bash 내장 명령어입니다.

스크립트가 종료되거나, 에러가 발생하거나, 사용자가 Ctrl+C를 누를 때 자동으로 정리 작업을 수행할 수 있습니다.

---

## 기본 문법

```bash
trap '명령어' 시그널
trap '명령어' 시그널1 시그널2 시그널3
trap 함수명 시그널
trap - 시그널  # trap 해제
```

---

## 주요 시그널

| 시그널 | 의미 | 발생 시점 |
|--------|------|-----------|
| `EXIT` | 스크립트 종료 | 정상 종료, 에러 종료, exit 호출 시 |
| `ERR` | 에러 발생 | 명령어 실행 실패 시 (set -e 필요) |
| `INT` | 인터럽트 | Ctrl+C 입력 시 (SIGINT) |
| `TERM` | 종료 요청 | kill 명령 시 (SIGTERM) |
| `DEBUG` | 디버그 | 모든 명령 실행 직전 |
| `RETURN` | 함수 리턴 | 함수나 source 종료 시 |
| `HUP` | 연결 끊김 | 터미널 세션 종료 시 (SIGHUP) |

---

## 실용 예제

### 1. 임시 파일 자동 정리 (가장 흔한 용도)

```bash
#!/bin/bash

# 임시 파일 생성
TEMP_FILE=$(mktemp)

# 스크립트 종료 시 자동 삭제
trap "rm -f $TEMP_FILE" EXIT

# 작업 수행
echo "Working..." > "$TEMP_FILE"
cat "$TEMP_FILE"

# 스크립트가 어떻게 종료되든 자동으로 rm 실행됨
```

**왜 유용한가?**
- 스크립트가 중간에 에러로 종료되어도 임시 파일 삭제 보장
- Ctrl+C로 중단해도 정리됨
- 수동으로 cleanup 코드 여러 곳에 넣을 필요 없음

---

### 2. 에러 발생 시 라인 번호 출력

```bash
#!/bin/bash
set -e  # 에러 시 즉시 종료

trap 'echo "Error on line $LINENO"' ERR

echo "Step 1: OK"
echo "Step 2: OK"
false  # 에러 발생 → trap 실행
echo "Step 3: Never executed"
```

**출력:**
```
Step 1: OK
Step 2: OK
Error on line 7
```

---

### 3. Ctrl+C 우아하게 처리

```bash
#!/bin/bash

trap 'echo -e "\nInterrupted! Cleaning up..."; exit 130' INT

echo "Press Ctrl+C to interrupt"
count=0

while true; do
    count=$((count + 1))
    echo "Running... ($count)"
    sleep 1
done
```

**참고**: `exit 130`은 관례적으로 SIGINT(Ctrl+C)로 종료되었음을 나타냅니다 (128 + 2).

**실행 결과:**
```
Press Ctrl+C to interrupt
Running... (1)
Running... (2)
^C
Interrupted! Cleaning up...
```

---

### 4. 스크립트 종료 시 정리 작업

```bash
#!/bin/bash

cleanup() {
    echo "Cleaning up..."
    
    # 백그라운드 프로세스 종료
    if [ -n "$BG_PID" ]; then
        kill $BG_PID 2>/dev/null
        echo "  ✓ Stopped background process"
    fi
    
    # 임시 디렉토리 삭제
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        echo "  ✓ Removed temp directory"
    fi
    
    echo "Cleanup completed"
}

trap cleanup EXIT

# 백그라운드 작업 시작
sleep 100 &
BG_PID=$!

# 임시 디렉토리 생성
TEMP_DIR=$(mktemp -d)
echo "Temp dir: $TEMP_DIR"

echo "Working for 5 seconds..."
sleep 5

# 스크립트 종료 시 cleanup 자동 실행
```

---

### 5. 여러 시그널 동시 처리

```bash
#!/bin/bash

handle_signal() {
    local signal=$1
    echo ""
    echo "Received signal: $signal"
    echo "Shutting down gracefully..."
    exit 1
}

trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM
trap 'echo "Script finished normally"' EXIT

echo "Running... (Ctrl+C or 'kill $BASHPID' to stop)"
echo "PID: $$"

for i in {1..30}; do
    echo "Tick $i"
    sleep 1
done
```

---

### 6. 디버깅: 모든 명령 추적

```bash
#!/bin/bash

trap 'echo ">>> Executing: $BASH_COMMAND"' DEBUG

echo "Hello World"
x=10
y=20
result=$((x + y))
echo "Result: $result"
```

**출력:**
```
>>> Executing: echo "Hello World"
Hello World
>>> Executing: x=10
>>> Executing: y=20
>>> Executing: result=$((x + y))
>>> Executing: echo "Result: $result"
Result: 30
```

---

### 7. 실전: 데이터베이스 백업 스크립트

```bash
#!/bin/bash
set -euo pipefail

BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
LOCK_FILE="/tmp/backup.lock"
SUCCESS=false

cleanup() {
    local exit_code=$?
    
    echo ""
    echo "Cleanup started..."
    
    # 백업 실패 시 불완전한 파일 삭제
    if [ "$SUCCESS" = false ] && [ -f "$BACKUP_FILE" ]; then
        echo "  Backup failed! Removing incomplete file..."
        rm -f "$BACKUP_FILE"
    fi
    
    # 락 파일 제거
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        echo "  ✓ Lock file removed"
    fi
    
    if [ $exit_code -eq 0 ]; then
        echo "Cleanup completed successfully"
    else
        echo "Cleanup completed with errors (exit code: $exit_code)"
    fi
}

trap cleanup EXIT
trap 'echo "Interrupted by user"; exit 130' INT

# 중복 실행 방지
if [ -f "$LOCK_FILE" ]; then
    echo "Backup already running (lock file exists)"
    exit 1
fi

touch "$LOCK_FILE"
echo "Lock acquired"

echo "Starting backup..."
echo "   Target: $BACKUP_FILE"

# 백업 실행 (예시)
mysqldump -u root -p database > "$BACKUP_FILE" 2>/dev/null || {
    echo "mysqldump failed"
    exit 1
}

SUCCESS=true
echo "Backup completed: $BACKUP_FILE"
echo "   Size: $(du -h "$BACKUP_FILE" | cut -f1)"
```

---

### 8. 에러 상세 정보 출력

```bash
#!/bin/bash
set -euo pipefail

error_handler() {
    local line=$1
    local command=$2
    local code=$3
    
    echo ""
    echo "Error occurred!"
    echo "   Line:     $line"
    echo "   Command:  $command"
    echo "   Exit code: $code"
    echo ""
    
    # 스택 트레이스 (함수 호출 스택)
    echo "Call stack:"
    local frame=0
    while caller $frame; do
        ((frame++))
    done
}

trap 'error_handler $LINENO "$BASH_COMMAND" $?' ERR

echo "Step 1: Creating directory"
mkdir /tmp/test_dir

echo "Step 2: Writing file"
echo "data" > /tmp/test_dir/file.txt

echo "Step 3: This will fail"
cat /nonexistent/file.txt  # 에러 발생

echo "Step 4: Never reached"
```

---

### 9. 락 파일로 중복 실행 방지

```bash
#!/bin/bash

LOCK_FILE="/tmp/myscript.lock"

cleanup() {
    rm -f "$LOCK_FILE"
    echo "Lock released"
}

trap cleanup EXIT

# 이미 실행 중인지 확인
if [ -f "$LOCK_FILE" ]; then
    echo "Script is already running"
    exit 1
fi

# 락 파일 생성
echo $$ > "$LOCK_FILE"
echo "Lock acquired (PID: $$)"

# 실제 작업
echo "Working..."
sleep 10

echo "Done"
```

---

### 10. 함수 내에서 trap 사용

```bash
#!/bin/bash

process_data() {
    local temp_file=$(mktemp)
    
    # 함수 종료 시 정리 (RETURN 시그널)
    trap "rm -f $temp_file" RETURN
    
    echo "Processing data..."
    echo "temp data" > "$temp_file"
    
    # 작업 수행
    cat "$temp_file"
    
    # 함수 종료 시 자동으로 temp_file 삭제됨
}

process_data
echo "Function completed"
```

---

## trap 해제

```bash
#!/bin/bash

# trap 설정
trap 'echo "Exiting..."' EXIT

echo "Trap is active"

# trap 해제
trap - EXIT

echo "Trap is removed"
# 이제 EXIT 시 아무것도 실행 안됨
```

---

## 현재 설정된 trap 확인

```bash
# 모든 trap 확인
trap -p

# 특정 시그널의 trap 확인
trap -p EXIT
trap -p INT
```

---

## 고급 패턴

### 1. 여러 cleanup 함수 체인

```bash
#!/bin/bash

cleanup_stack=()

add_cleanup() {
    cleanup_stack+=("$1")
}

run_cleanups() {
    echo "Running cleanups..."
    # 역순으로 실행 (LIFO)
    for ((i=${#cleanup_stack[@]}-1; i>=0; i--)); do
        eval "${cleanup_stack[$i]}"
    done
}

trap run_cleanups EXIT

# cleanup 등록
add_cleanup "echo '  ✓ Cleanup 1'"
add_cleanup "rm -f /tmp/file1"
add_cleanup "echo '  ✓ Cleanup 2'"
add_cleanup "rm -f /tmp/file2"

echo "Working..."
sleep 2
```

---

### 2. 타임아웃 구현

```bash
#!/bin/bash

TIMEOUT=5

timeout_handler() {
    echo "Timeout after $TIMEOUT seconds!"
    exit 124
}

# 백그라운드에서 타이머 시작
(sleep $TIMEOUT; kill -TERM $$) 2>/dev/null &
TIMER_PID=$!

trap timeout_handler TERM
trap "kill $TIMER_PID 2>/dev/null" EXIT

echo "Starting long task (timeout: ${TIMEOUT}s)..."

# 긴 작업 시뮬레이션
sleep 10  # 타임아웃보다 길면 중단됨

# 성공 시 타이머 취소
kill $TIMER_PID 2>/dev/null
echo "Task completed"
```

**참고**: `exit 124`는 `timeout` 명령의 관례를 따른 것입니다.

---

### 3. 진행 상황 표시

```bash
#!/bin/bash

show_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    local bar_length=50
    local filled=$((bar_length * current / total))
    
    printf "\r["
    printf "%${filled}s" | tr ' ' '='
    printf "%$((bar_length - filled))s" | tr ' ' ' '
    printf "] %3d%%" $percent
}

cleanup() {
    echo ""
    echo "Cleanup completed"
}

trap cleanup EXIT

total=100
for i in $(seq 1 $total); do
    show_progress $i $total
    sleep 0.05
done

echo ""
echo "Done"
```

---

## 실전 팁

### 권장 사항

1. **항상 EXIT trap 사용** - 임시 파일/디렉토리 정리
2. **set -e와 ERR trap 조합** - 에러 추적
3. **함수로 cleanup 구현** - 가독성 향상
4. **여러 시그널 처리** - INT, TERM, EXIT

### 주의사항

1. **trap 내에서 에러 발생 주의** - cleanup이 실패하면 안됨

2. **변수 인용 주의** - 큰따옴표 vs 작은따옴표
   ```bash
   FILE="test.txt"
   trap "rm -f $FILE" EXIT    # 즉시 평가: rm -f test.txt (권장)
   trap 'rm -f $FILE' EXIT    # 나중 평가: 실행 시점의 $FILE 값 사용
   ```
   **권장**: 대부분의 경우 큰따옴표(`"`)를 사용하여 trap 설정 시점의 값을 고정

3. **서브셸에서는 trap 상속 안됨** - `( )` 내부는 별도 처리 필요

4. **DEBUG trap은 성능 영향** - 프로덕션에서는 제거

5. **ERR trap은 set -e 필요** - set -e 없이는 동작하지 않음

---

## 실전 템플릿

```bash
#!/bin/bash
set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 전역 변수
TEMP_DIR=""
LOCK_FILE="/tmp/$(basename $0).lock"
SUCCESS=false

# 로깅 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# Cleanup 함수
cleanup() {
    local exit_code=$?
    
    log_info "Cleanup started..."
    
    # 임시 디렉토리 삭제
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        log_info "Removed temp directory"
    fi
    
    # 락 파일 제거
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        log_info "Released lock"
    fi
    
    if [ $exit_code -eq 0 ] && [ "$SUCCESS" = true ]; then
        log_info "Script completed successfully"
    else
        log_error "Script failed (exit code: $exit_code)"
    fi
}

# 에러 핸들러
error_handler() {
    log_error "Error on line $1: $2"
}

# Trap 설정
trap cleanup EXIT
trap 'error_handler $LINENO "$BASH_COMMAND"' ERR
trap 'log_warn "Interrupted by user"; exit 130' INT TERM

# 중복 실행 방지
if [ -f "$LOCK_FILE" ]; then
    log_error "Script is already running"
    exit 1
fi

echo $$ > "$LOCK_FILE"

# 임시 디렉토리 생성
TEMP_DIR=$(mktemp -d)
log_info "Created temp directory: $TEMP_DIR"

# ========================================
# 여기에 실제 작업 코드 작성
# ========================================

log_info "Starting main task..."
sleep 2
log_info "Task completed"

SUCCESS=true
```

---

## 시그널 상세 정보

### 사용 가능한 모든 시그널 확인

```bash
# 시스템의 모든 시그널 목록
kill -l

# 출력 예시:
# 1) SIGHUP   2) SIGINT   3) SIGQUIT  4) SIGILL   5) SIGTRAP
# 6) SIGABRT  7) SIGBUS   8) SIGFPE   9) SIGKILL 10) SIGUSR1
# ...
```

### 주요 시그널 번호

| 번호 | 이름 | trap 사용 | 설명 |
|------|------|-----------|------|
| 1 | SIGHUP | `HUP` | 터미널 연결 끊김 |
| 2 | SIGINT | `INT` | Ctrl+C (인터럽트) |
| 3 | SIGQUIT | `QUIT` | Ctrl+\ (코어 덤프와 함께 종료) |
| 9 | SIGKILL | 불가 | 강제 종료 (trap 불가) |
| 15 | SIGTERM | `TERM` | 정상 종료 요청 (기본 kill) |
| 19 | SIGSTOP | 불가 | 프로세스 일시 정지 (trap 불가) |

**중요**: `SIGKILL(9)`과 `SIGSTOP(19)`는 trap으로 잡을 수 없습니다!

```bash
# 이것은 동작하지 않음
trap 'echo "Cannot catch this"' KILL  # 무시됨
```

---

## trap 동작 원리

### 1. 여러 trap 설정 시 동작

```bash
#!/bin/bash

# 첫 번째 trap
trap 'echo "First trap"' EXIT

# 두 번째 trap (첫 번째를 덮어씀)
trap 'echo "Second trap"' EXIT

echo "Exiting..."
# 출력: Second trap (첫 번째는 실행 안됨)
```

**해결책: 여러 명령을 하나의 trap에 넣기**

```bash
#!/bin/bash

trap 'echo "First"; echo "Second"; echo "Third"' EXIT

# 또는 함수 사용 (권장)
cleanup() {
    echo "First"
    echo "Second"
    echo "Third"
}

trap cleanup EXIT
```

### 2. 여러 시그널을 한 번에 처리

```bash
#!/bin/bash

handle_exit() {
    echo "Cleaning up..."
}

# 여러 시그널에 동일한 핸들러 적용
trap handle_exit EXIT INT TERM HUP

echo "Running... (Ctrl+C to stop)"
sleep 30
```

### 3. 현재 설정된 trap 확인

```bash
# 모든 trap 확인
trap -p

# 특정 시그널만 확인
trap -p EXIT
trap -p INT

# 출력 예시:
# trap -- 'echo "Cleaning up..."' EXIT
# trap -- 'echo "Interrupted"' SIGINT
```

---

## 서브셸과 trap

### 서브셸에서 trap은 상속되지 않음

```bash
#!/bin/bash

trap 'echo "Parent EXIT"' EXIT

echo "Parent shell"

# 서브셸 (괄호)
(
    echo "Subshell"
    trap 'echo "Child EXIT"' EXIT
    # 서브셸 종료 시 "Child EXIT"만 출력
)

echo "Back to parent"
# 스크립트 종료 시 "Parent EXIT" 출력
```

**출력:**
```
Parent shell
Subshell
Child EXIT
Back to parent
Parent EXIT
```

### 백그라운드 프로세스와 trap

```bash
#!/bin/bash

trap 'echo "Main EXIT"' EXIT

# 백그라운드 프로세스는 trap을 상속하지 않음
(
    sleep 2
    echo "Background done"
) &

echo "Main process"
sleep 1
```

---

## set 옵션과 trap 조합

### 필수 set 옵션들

```bash
#!/bin/bash

# 에러 시 즉시 종료
set -e

# 미정의 변수 사용 시 에러
set -u

# 파이프라인에서 하나라도 실패하면 에러
set -o pipefail

# 한 줄로
set -euo pipefail

trap 'echo "Error on line $LINENO"' ERR

# 이제 모든 에러를 잡을 수 있음
```

### set 옵션 상세 설명

```bash
#!/bin/bash

# -e: 에러 시 즉시 종료
set -e
false  # 여기서 스크립트 종료
echo "Never executed"

# -u: 미정의 변수 에러
set -u
echo $UNDEFINED_VAR  # 에러 발생

# -o pipefail: 파이프 에러 감지
set -o pipefail
cat nonexistent.txt | grep "pattern"  # 에러 발생 (cat 실패)
```

### errexit과 trap ERR 차이

```bash
#!/bin/bash

# set -e만 사용
set -e
false
echo "Not executed"

# trap ERR 사용
trap 'echo "Error caught!"' ERR
false
echo "Still executed!"  # trap은 스크립트를 멈추지 않음

# 둘 다 사용 (권장)
set -e
trap 'echo "Error on line $LINENO"; exit 1' ERR
```

---

## 고급 패턴

### 1. 롤백 메커니즘

```bash
#!/bin/bash
set -euo pipefail

BACKUP_DIR=""
ORIGINAL_FILE=""

rollback() {
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Operation failed! Rolling back..."
        
        if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
            echo "  Restoring from backup..."
            cp -r "$BACKUP_DIR"/* /target/dir/
            rm -rf "$BACKUP_DIR"
            echo "  ✓ Rollback completed"
        fi
    else
        echo "Operation successful"
        # 백업 삭제
        [ -n "$BACKUP_DIR" ] && rm -rf "$BACKUP_DIR"
    fi
}

trap rollback EXIT

# 백업 생성
BACKUP_DIR=$(mktemp -d)
echo "Creating backup..."
cp -r /target/dir/* "$BACKUP_DIR/"

# 위험한 작업 수행
echo "Performing operation..."
# ... 작업 ...

# 실패하면 자동으로 롤백됨
```

### 2. 진행 상황 저장 및 복구

```bash
#!/bin/bash
set -euo pipefail

STATE_FILE="/tmp/script_state.txt"
CURRENT_STEP=0

save_state() {
    echo "$CURRENT_STEP" > "$STATE_FILE"
}

cleanup() {
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Failed at step $CURRENT_STEP"
        echo "State saved. Run again to resume."
    else
        rm -f "$STATE_FILE"
        echo "All steps completed"
    fi
}

trap cleanup EXIT

# 이전 상태 복구
if [ -f "$STATE_FILE" ]; then
    CURRENT_STEP=$(cat "$STATE_FILE")
    echo "Resuming from step $CURRENT_STEP"
fi

# 단계별 실행
if [ $CURRENT_STEP -lt 1 ]; then
    echo "Step 1: Downloading..."
    # download_files
    CURRENT_STEP=1
    save_state
fi

if [ $CURRENT_STEP -lt 2 ]; then
    echo "Step 2: Processing..."
    # process_files
    CURRENT_STEP=2
    save_state
fi

if [ $CURRENT_STEP -lt 3 ]; then
    echo "Step 3: Uploading..."
    # upload_files
    CURRENT_STEP=3
    save_state
fi
```

### 3. 타임스탬프 로깅

```bash
#!/bin/bash

LOG_FILE="/tmp/script.log"
START_TIME=$(date +%s)

log_with_time() {
    local current_time=$(date +%s)
    local elapsed=$((current_time - START_TIME))
    echo "[+${elapsed}s] $*" | tee -a "$LOG_FILE"
}

cleanup() {
    local exit_code=$?
    local end_time=$(date +%s)
    local total_time=$((end_time - START_TIME))
    
    log_with_time "Script finished in ${total_time}s (exit code: $exit_code)"
}

trap cleanup EXIT

log_with_time "Starting script"
sleep 2
log_with_time "Step 1 completed"
sleep 1
log_with_time "Step 2 completed"
```

### 4. 리소스 사용량 모니터링

```bash
#!/bin/bash

monitor_resources() {
    local pid=$$
    while true; do
        ps -p $pid -o %cpu,%mem,vsz,rss | tail -1 >> /tmp/resource_usage.log
        sleep 5
    done
}

cleanup() {
    # 모니터링 프로세스 종료
    kill $MONITOR_PID 2>/dev/null
    
    echo "Resource usage summary:"
    awk '{cpu+=$1; mem+=$2; count++} END {
        printf "  Avg CPU: %.2f%%\n", cpu/count;
        printf "  Avg MEM: %.2f%%\n", mem/count;
    }' /tmp/resource_usage.log
    
    rm -f /tmp/resource_usage.log
}

trap cleanup EXIT

# 백그라운드에서 모니터링 시작
monitor_resources &
MONITOR_PID=$!

# 실제 작업
echo "Running tasks..."
sleep 10
```

---

## 일반적인 실수와 해결책

### 실수 1: trap 내에서 exit 호출 시 무한 루프

```bash
#!/bin/bash

# 잘못된 예
trap 'echo "Exiting..."; exit 1' EXIT
exit 0
# "Exiting..."이 무한 반복될 수 있음
```

**해결책:**
```bash
#!/bin/bash

# 올바른 예
EXITING=false

cleanup() {
    if [ "$EXITING" = true ]; then
        return
    fi
    EXITING=true
    
    echo "Cleaning up..."
    # cleanup 작업
}

trap cleanup EXIT
```

### 실수 2: 변수 스코프 문제

```bash
#!/bin/bash

# 잘못된 예
function do_work() {
    local temp_file=$(mktemp)
    trap "rm -f $temp_file" EXIT  # 함수 종료 시 실행됨 (스크립트 종료 시 아님)
}

do_work
# temp_file이 이미 삭제됨
```

**해결책:**
```bash
#!/bin/bash

# 올바른 예 1: RETURN 사용
function do_work() {
    local temp_file=$(mktemp)
    trap "rm -f $temp_file" RETURN  # 함수 종료 시
}

# 올바른 예 2: 전역 trap
TEMP_FILES=()

cleanup() {
    for f in "${TEMP_FILES[@]}"; do
        rm -f "$f"
    done
}

trap cleanup EXIT

function do_work() {
    local temp_file=$(mktemp)
    TEMP_FILES+=("$temp_file")
}
```

### 실수 3: 따옴표 처리 실수

```bash
#!/bin/bash

# 잘못된 예
FILE="my file.txt"  # 공백 포함
trap "rm -f $FILE" EXIT  # rm -f my file.txt (두 개 파일로 인식)
```

**해결책:**
```bash
#!/bin/bash

# 올바른 예
FILE="my file.txt"
trap "rm -f \"$FILE\"" EXIT  # 따옴표 이스케이프

# 또는
trap 'rm -f "$FILE"' EXIT  # 작은따옴표 사용 (변수는 실행 시 평가)
```

### 실수 4: ERR trap이 모든 에러를 잡지 못함

```bash
#!/bin/bash

# 잘못된 예
trap 'echo "Error!"' ERR

false  # trap 실행 안됨 (set -e가 없어서)
echo "Still running"
```

**해결책:**
```bash
#!/bin/bash

# 올바른 예
set -e  # 필수!
trap 'echo "Error on line $LINENO"' ERR

false  # 이제 trap 실행됨
```

### 실수 5: 파이프라인에서 에러 무시

```bash
#!/bin/bash
set -e

# 잘못된 예
cat nonexistent.txt | grep "pattern"  # cat 실패해도 계속 실행
echo "Still running"
```

**해결책:**
```bash
#!/bin/bash
set -e
set -o pipefail  # 필수!

trap 'echo "Pipeline failed"' ERR

cat nonexistent.txt | grep "pattern"  # 이제 에러 감지됨
```

---

## 성능 고려사항

### DEBUG trap의 오버헤드

```bash
#!/bin/bash

# DEBUG trap은 모든 명령마다 실행됨
trap 'echo "Command: $BASH_COMMAND"' DEBUG

# 루프에서는 엄청난 오버헤드
for i in {1..10000}; do
    x=$((i * 2))  # 각 반복마다 trap 실행
done
```

**성능 비교:**
```bash
# DEBUG trap 없이
time bash -c 'for i in {1..100000}; do x=$((i*2)); done'
# 약 0.5초

# DEBUG trap 사용
time bash -c 'trap ":" DEBUG; for i in {1..100000}; do x=$((i*2)); done'
# 약 5초 (10배 느림!)
```

**권장사항:**
- 프로덕션 코드에서는 DEBUG trap 제거
- 디버깅 시에만 조건부로 활성화

```bash
#!/bin/bash

if [ "${DEBUG:-0}" = "1" ]; then
    trap 'echo ">>> $BASH_COMMAND"' DEBUG
fi

# 사용: DEBUG=1 ./script.sh
```

### trap 함수는 간단하게 유지

```bash
#!/bin/bash

# 나쁜 예: 복잡한 cleanup
trap 'for f in $(find /tmp -name "*.tmp"); do rm -f "$f"; done' EXIT

# 좋은 예: 간단한 cleanup
TEMP_FILES=()
trap 'rm -f "${TEMP_FILES[@]}"' EXIT
```

---

## 실전 팁 모음

### Tip 1: 디버그 모드 토글

```bash
#!/bin/bash

# 환경 변수로 디버그 모드 제어
if [ "${DEBUG:-0}" = "1" ]; then
    set -x  # 명령어 출력
    trap 'echo ">>> Line $LINENO: $BASH_COMMAND"' DEBUG
fi

# 사용:
# DEBUG=1 ./script.sh  # 디버그 모드
# ./script.sh          # 일반 모드
```

### Tip 2: 안전한 임시 파일 관리

```bash
#!/bin/bash

# 임시 파일 배열로 관리
declare -a TEMP_FILES

create_temp() {
    local temp_file=$(mktemp)
    TEMP_FILES+=("$temp_file")
    echo "$temp_file"
}

cleanup() {
    for f in "${TEMP_FILES[@]}"; do
        [ -f "$f" ] && rm -f "$f"
    done
}

trap cleanup EXIT

# 사용
file1=$(create_temp)
file2=$(create_temp)
echo "data" > "$file1"
```

### Tip 3: 스크립트 실행 시간 측정

```bash
#!/bin/bash

START_TIME=$SECONDS

show_duration() {
    local duration=$((SECONDS - START_TIME))
    local hours=$((duration / 3600))
    local minutes=$(((duration % 3600) / 60))
    local seconds=$((duration % 60))
    
    printf "⏱️  Duration: %02d:%02d:%02d\n" $hours $minutes $seconds
}

trap show_duration EXIT

# 작업 수행
sleep 5
```

### Tip 4: 중요한 작업 전 확인

```bash
#!/bin/bash

confirm_action() {
    echo "This will delete all files in /tmp/data"
    read -p "Continue? (yes/no): " response
    
    if [ "$response" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
}

cleanup() {
    echo "Cleanup completed"
}

trap cleanup EXIT

confirm_action

# 위험한 작업
rm -rf /tmp/data/*
```

### Tip 5: 로그 파일 자동 로테이션

```bash
#!/bin/bash

LOG_FILE="/var/log/myscript.log"
MAX_LOG_SIZE=$((10 * 1024 * 1024))  # 10MB

rotate_log() {
    if [ -f "$LOG_FILE" ]; then
        local size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE")
        if [ $size -gt $MAX_LOG_SIZE ]; then
            mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d_%H%M%S)"
            gzip "$LOG_FILE".* 2>/dev/null || true
        fi
    fi
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

trap rotate_log EXIT

log "Script started"
```

### Tip 6: 네트워크 연결 정리

```bash
#!/bin/bash

SSH_PIDS=()

cleanup_connections() {
    echo "Closing connections..."
    for pid in "${SSH_PIDS[@]}"; do
        kill $pid 2>/dev/null && echo "  ✓ Closed connection (PID: $pid)"
    done
}

trap cleanup_connections EXIT INT TERM

# SSH 터널 생성
ssh -f -N -L 8080:localhost:80 server1 &
SSH_PIDS+=($!)

ssh -f -N -L 3306:localhost:3306 server2 &
SSH_PIDS+=($!)

echo "Connections established"
sleep 30
```

### Tip 7: 실패한 명령어 재시도

```bash
#!/bin/bash
set -euo pipefail

retry() {
    local max_attempts=3
    local attempt=1
    local delay=2
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt/$max_attempts..."
        
        if "$@"; then
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            echo "Failed. Retrying in ${delay}s..."
            sleep $delay
            delay=$((delay * 2))
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "All attempts failed"
    return 1
}

trap 'echo "Script failed"' ERR

# 사용
retry curl -f https://example.com/api
```

### Tip 8: 병렬 작업 관리

```bash
#!/bin/bash

PIDS=()

cleanup() {
    echo "Stopping all background jobs..."
    for pid in "${PIDS[@]}"; do
        kill $pid 2>/dev/null
    done
    wait
    echo "All jobs stopped"
}

trap cleanup EXIT INT TERM

# 병렬 작업 시작
for i in {1..5}; do
    (
        echo "Job $i started"
        sleep $((RANDOM % 10 + 5))
        echo "Job $i completed"
    ) &
    PIDS+=($!)
done

echo "Waiting for all jobs..."
wait
echo "All jobs completed"
```

### Tip 9: 설정 파일 검증

```bash
#!/bin/bash

CONFIG_FILE="config.conf"
CONFIG_BACKUP=""

validate_config() {
    # 설정 파일 검증 로직
    if ! grep -q "required_setting" "$CONFIG_FILE"; then
        return 1
    fi
    return 0
}

rollback_config() {
    if [ -n "$CONFIG_BACKUP" ] && [ -f "$CONFIG_BACKUP" ]; then
        echo "Rolling back configuration..."
        mv "$CONFIG_BACKUP" "$CONFIG_FILE"
    fi
}

trap rollback_config ERR

# 설정 백업
CONFIG_BACKUP="${CONFIG_FILE}.backup.$$"
cp "$CONFIG_FILE" "$CONFIG_BACKUP"

# 설정 수정
echo "new_setting=value" >> "$CONFIG_FILE"

# 검증
if ! validate_config; then
    echo "Invalid configuration"
    exit 1
fi

# 성공 시 백업 삭제
rm -f "$CONFIG_BACKUP"
echo "Configuration updated"
```

### Tip 10: 멀티 스테이지 빌드

```bash
#!/bin/bash
set -euo pipefail

STAGES=("download" "compile" "test" "package")
CURRENT_STAGE=0

cleanup() {
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Build failed at stage: ${STAGES[$CURRENT_STAGE]}"
        
        # 실패한 스테이지의 로그 저장
        if [ -f "/tmp/build.log" ]; then
            cp /tmp/build.log "/tmp/failed_${STAGES[$CURRENT_STAGE]}.log"
            echo "Log saved to: /tmp/failed_${STAGES[$CURRENT_STAGE]}.log"
        fi
    else
        echo "Build completed successfully"
        rm -f /tmp/build.log
    fi
}

trap cleanup EXIT

for stage in "${STAGES[@]}"; do
    echo "Stage: $stage"
    
    case $stage in
        download)
            # 다운로드 로직
            ;;
        compile)
            # 컴파일 로직
            ;;
        test)
            # 테스트 로직
            ;;
        package)
            # 패키징 로직
            ;;
    esac
    
    CURRENT_STAGE=$((CURRENT_STAGE + 1))
done
```

---

## 요약

| 용도 | trap 명령 |
|------|-----------|
| 임시 파일 정리 | `trap "rm -f $TEMP_FILE" EXIT` |
| 에러 추적 | `trap 'echo "Error on line $LINENO"' ERR` |
| Ctrl+C 처리 | `trap 'cleanup; exit' INT` |
| 디버깅 | `trap 'echo "$BASH_COMMAND"' DEBUG` |
| 락 파일 관리 | `trap "rm -f $LOCK_FILE" EXIT` |

**핵심**: `trap`을 사용하면 스크립트가 어떻게 종료되든 (정상, 에러, Ctrl+C) 정리 작업을 보장할 수 있습니다!


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-03-29

© 2026 siasia86. Licensed under CC BY 4.0.
