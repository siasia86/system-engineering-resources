# gdb - GNU Debugger

## gdb란?

**GNU Debugger** - 프로그램을 소스 코드 레벨에서 디버깅할 수 있는 강력한 도구입니다.

## 주요 기능

- 브레이크포인트 설정
- 변수 값 확인 및 수정
- 스택 추적
- 메모리 검사
- 코어 덤프 분석
- 원격 디버깅

## 설치

```bash
# Ubuntu/Debian
sudo apt-get install gdb

# CentOS/RHEL
sudo yum install gdb

# 버전 확인
gdb --version
```

## 기본 사용법

### 프로그램 시작

```bash
# 프로그램 로드
gdb ./myapp

# 인자와 함께
gdb --args ./myapp arg1 arg2

# 실행 중인 프로세스
gdb -p <PID>

# 코어 덤프 분석
gdb ./myapp core
```

### 기본 명령어

```gdb
# 프로그램 실행
(gdb) run
(gdb) r

# 인자와 함께 실행
(gdb) run arg1 arg2

# 브레이크포인트 설정
(gdb) break main
(gdb) b function_name
(gdb) b file.c:10

# 계속 실행
(gdb) continue
(gdb) c

# 한 줄 실행 (함수 내부로)
(gdb) step
(gdb) s

# 한 줄 실행 (함수 건너뛰기)
(gdb) next
(gdb) n

# 함수 끝까지 실행
(gdb) finish

# 종료
(gdb) quit
(gdb) q
```

## 브레이크포인트

### 설정

```gdb
# 함수에 설정
(gdb) break main
(gdb) break calculate_sum

# 파일:라인에 설정
(gdb) break main.c:42

# 조건부 브레이크포인트
(gdb) break main.c:42 if x > 10

# 임시 브레이크포인트 (한 번만)
(gdb) tbreak main
```

### 관리

```gdb
# 브레이크포인트 목록
(gdb) info breakpoints
(gdb) i b

# 브레이크포인트 삭제
(gdb) delete 1
(gdb) d 1

# 모두 삭제
(gdb) delete

# 비활성화/활성화
(gdb) disable 1
(gdb) enable 1
```

## 변수 검사

### 출력

```gdb
# 변수 값 출력
(gdb) print variable
(gdb) p variable

# 포인터 역참조
(gdb) print *pointer

# 배열
(gdb) print array[0]@10  # 10개 요소

# 구조체
(gdb) print struct_var
(gdb) print struct_var.member

# 16진수로
(gdb) print/x variable

# 2진수로
(gdb) print/t variable
```

### 변수 수정

```gdb
# 값 변경
(gdb) set variable x = 10
(gdb) set x = 10

# 포인터 변경
(gdb) set *pointer = 100
```

### 감시

```gdb
# 변수 감시 (값 변경 시 중단)
(gdb) watch variable

# 읽기 감시
(gdb) rwatch variable

# 읽기/쓰기 감시
(gdb) awatch variable

# 감시 목록
(gdb) info watchpoints
```

## 스택 추적

```gdb
# 백트레이스 (콜 스택)
(gdb) backtrace
(gdb) bt

# 전체 백트레이스
(gdb) bt full

# 프레임 이동
(gdb) frame 0
(gdb) f 0

# 상위 프레임
(gdb) up

# 하위 프레임
(gdb) down

# 현재 프레임 정보
(gdb) info frame
```

## 메모리 검사

```gdb
# 메모리 덤프
(gdb) x/10x 0x12345678  # 16진수 10개
(gdb) x/10d address     # 10진수 10개
(gdb) x/10s address     # 문자열 10개

# 형식:
# x/[개수][형식][크기] 주소
# 형식: x(16진수), d(10진수), s(문자열), i(명령어)
# 크기: b(byte), h(halfword), w(word), g(giant)

# 예시
(gdb) x/10xb 0x12345678  # 10바이트를 16진수로
(gdb) x/5i $pc           # 현재 위치부터 5개 명령어
```

## 소스 코드 보기

```gdb
# 현재 위치 소스
(gdb) list
(gdb) l

# 특정 함수
(gdb) list function_name

# 특정 라인
(gdb) list main.c:42

# 범위
(gdb) list 10,20
```

## 스레드 디버깅

```gdb
# 스레드 목록
(gdb) info threads

# 스레드 전환
(gdb) thread 2

# 모든 스레드 백트레이스
(gdb) thread apply all bt

# 특정 스레드에 명령 실행
(gdb) thread apply 2 print variable
```

## 실전 예제

### 예제 1: Segmentation Fault 디버깅

```c
// crash.c
#include <stdio.h>

int main() {
    int *ptr = NULL;
    *ptr = 42;  // Segmentation fault
    return 0;
}
```

**디버깅:**
```bash
# 컴파일 (디버그 심볼 포함)
gcc -g crash.c -o crash

# gdb 실행
gdb ./crash

(gdb) run
# Program received signal SIGSEGV, Segmentation fault.
# 0x... in main () at crash.c:5
# 5        *ptr = 42;

(gdb) backtrace
# #0  0x... in main () at crash.c:5

(gdb) print ptr
# $1 = (int *) 0x0

# → NULL 포인터 역참조 문제 발견!
```

### 예제 2: 무한 루프 디버깅

```c
// loop.c
#include <stdio.h>

int main() {
    int i = 0;
    while (i < 10) {
        printf("%d\n", i);
        // i++; 누락!
    }
    return 0;
}
```

**디버깅:**
```bash
gcc -g loop.c -o loop
gdb ./loop

(gdb) break main
(gdb) run
(gdb) next  # 여러 번 실행
(gdb) print i
# $1 = 0  (계속 0)

# → i++ 누락 발견!
```

### 예제 3: 변수 값 추적

```bash
gdb ./myapp

(gdb) break calculate_sum
(gdb) run

(gdb) print x
# $1 = 10

(gdb) next
(gdb) print x
# $2 = 15

# 값 변경 테스트
(gdb) set x = 100
(gdb) continue
```

### 예제 4: 코어 덤프 분석

```bash
# 코어 덤프 활성화
ulimit -c unlimited

# 프로그램 실행 (크래시 발생)
./myapp
# Segmentation fault (core dumped)

# 코어 덤프 분석
gdb ./myapp core

(gdb) backtrace
# 크래시 위치 확인

(gdb) frame 0
(gdb) print variable
# 크래시 시점의 변수 값 확인
```

### 예제 5: 조건부 브레이크포인트

```bash
gdb ./myapp

# 특정 조건에서만 중단
(gdb) break process_data if id == 12345
(gdb) run

# id가 12345일 때만 중단됨
```

## 고급 기능

### TUI 모드

```bash
# TUI 모드 시작
gdb -tui ./myapp

# 또는 gdb 내에서
(gdb) tui enable
(gdb) layout src    # 소스 코드
(gdb) layout asm    # 어셈블리
(gdb) layout split  # 소스 + 어셈블리
(gdb) layout regs   # 레지스터
```

### 자동화 (스크립트)

```bash
# 명령어 파일 생성
cat > commands.gdb << EOF
break main
run
print argc
backtrace
quit
EOF

# 실행
gdb -x commands.gdb ./myapp
```

### Python 스크립팅

```python
# gdb_script.py
import gdb

class HelloWorld(gdb.Command):
    def __init__(self):
        super(HelloWorld, self).__init__("hello", gdb.COMMAND_USER)
    
    def invoke(self, arg, from_tty):
        print("Hello, World!")

HelloWorld()
```

```bash
# 사용
gdb -x gdb_script.py ./myapp
(gdb) hello
# Hello, World!
```

### 원격 디버깅

**서버 (타겟 시스템):**
```bash
gdbserver :1234 ./myapp
```

**클라이언트:**
```bash
gdb ./myapp
(gdb) target remote 192.168.1.100:1234
(gdb) continue
```

## 유용한 설정

### .gdbinit 파일

```bash
# ~/.gdbinit
set print pretty on
set print array on
set print array-indexes on
set pagination off
set history save on
set history size 10000
```

### 단축키

```gdb
# 명령어 약어
(gdb) b = break
(gdb) r = run
(gdb) c = continue
(gdb) s = step
(gdb) n = next
(gdb) p = print
(gdb) bt = backtrace
(gdb) q = quit
```

## 트러블슈팅

### 문제 1: "No debugging symbols found"

```bash
# 원인: -g 옵션 없이 컴파일
# 해결: 디버그 심볼 포함하여 재컴파일
gcc -g -O0 myapp.c -o myapp
```

### 문제 2: "Cannot access memory"

```bash
# 원인: 최적화로 인한 변수 제거
# 해결: 최적화 비활성화
gcc -g -O0 myapp.c -o myapp
```

### 문제 3: "ptrace: Operation not permitted"

```bash
# 원인: ptrace_scope 설정
# 해결:
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

## 실무 팁

### 1. 효율적인 디버깅

```bash
# 빠른 재시작
(gdb) run
# 프로그램 종료 후
(gdb) run  # 자동으로 재시작

# 마지막 명령 반복
(gdb) <Enter>
```

### 2. 로그 저장

```bash
# 출력 로깅
(gdb) set logging on
(gdb) set logging file debug.log
```

### 3. 조건부 명령

```bash
# 브레이크포인트에서 자동 실행
(gdb) break main
(gdb) commands 1
> print argc
> continue
> end
```

## 관련 도구

| 도구 | 용도 |
|------|------|
| **gdb** | 소스 디버깅 |
| **lldb** | LLVM 디버거 |
| **cgdb** | gdb + 컬러 |
| **ddd** | gdb GUI |
| **valgrind** | 메모리 디버깅 |

## 요약

**gdb의 강점:**
- 소스 레벨 디버깅
- 강력한 브레이크포인트
- 변수 검사 및 수정
- 코어 덤프 분석

**주요 명령어:**
- `run` - 실행
- `break` - 브레이크포인트
- `step/next` - 단계 실행
- `print` - 변수 출력
- `backtrace` - 스택 추적

**언제 사용?**
- 크래시 원인 찾기
- 로직 버그 수정
- 변수 값 추적
- 코어 덤프 분석
