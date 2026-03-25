# ltrace - 라이브러리 함수 추적 도구

> **내부 공유 자료**  
> 작성일: 2026-01-29  
> 버전: 1.0  
> 대상: 개발자, SRE, 시스템 엔지니어

## 목차
- [개요](#ltrace란)
- [빠른 참조](#빠른-참조)
- [기본 사용법](#ltrace-ls-실행)
- [실전 예제](#실전-디버깅-시나리오)
- [프로덕션 주의사항](#성능-오버헤드-비교)

## 빠른 참조

```bash
# 가장 많이 사용하는 명령어
ltrace ./myapp                    # 기본 추적
ltrace -c ./myapp                 # 통계만
ltrace -e malloc,free ./myapp     # 특정 함수만
ltrace -p <PID>                   # 실행 중인 프로세스
ltrace -o output.log ./myapp      # 파일로 저장
ltrace -T ./myapp                 # 시간 측정
```

## ltrace란?

**Library Trace** - 프로그램이 호출하는 동적 라이브러리 함수를 추적하는 도구입니다.

### ltrace vs strace

| 도구 | 추적 대상 | 레벨 |
|------|----------|------|
| **ltrace** | 라이브러리 함수 (libc 등) | User Space |
| **strace** | 시스템 콜 (커널 인터페이스) | Kernel Space |

```
Application (ls)
    ↓
Library Functions (libc)  ← ltrace가 추적
    ↓
System Calls (kernel)     ← strace가 추적
    ↓
Linux Kernel
```

## ltrace ls 실행

```bash
ltrace ls
```

## 출력 분석

### 1. 초기화 단계

#### 프로그램 이름 파싱
```c
strrchr("ls", '/')  = nil
```
- **함수**: `strrchr()` - 문자열에서 마지막 문자 위치 찾기
- **목적**: 프로그램 경로에서 실행 파일 이름 추출
- **결과**: `nil` - 경로 없이 `ls`만 실행됨

#### 로케일 설정
```c
setlocale(LC_ALL, "")  = "en_US.UTF-8"
```
- **함수**: `setlocale()` - 프로그램의 로케일 설정
- **목적**: 언어, 문자 인코딩, 날짜/시간 형식 등 지역화
- **결과**: `en_US.UTF-8` - 영어(미국), UTF-8 인코딩

#### 다국어 지원
```c
bindtextdomain("coreutils", "/usr/share/locale")  = "/usr/share/locale"
textdomain("coreutils")  = "coreutils"
```
- **함수**: `bindtextdomain()`, `textdomain()` - 번역 파일 설정
- **목적**: 다국어 메시지 지원 (gettext)
- **경로**: `/usr/share/locale/` 아래 번역 파일 사용

#### 종료 핸들러 등록
```c
__cxa_atexit(0x647c21305880, 0, 0x647c2131d008, 0)  = 0
```
- **함수**: `__cxa_atexit()` - 프로그램 종료 시 실행할 함수 등록
- **목적**: 정리 작업 (메모리 해제, 파일 닫기 등)

### 2. 옵션 파싱

```c
getopt_long(1, 0x7ffe9157bd78, "abcdfghiklmnopqrstuvw:xABCDFGHI:...", 0x647c2131c340, -1)  = -1
```
- **함수**: `getopt_long()` - 명령줄 옵션 파싱
- **인자**:
  - `1`: argc (인자 개수)
  - `0x7ffe9157bd78`: argv (인자 배열)
  - `"abcdfghiklmnopqrstuvw:xABCDFGHI:..."`: 지원하는 옵션들
- **반환**: `-1` - 더 이상 옵션 없음

**지원 옵션 예시:**
- `-a`: 숨김 파일 포함
- `-l`: 상세 정보
- `-h`: 사람이 읽기 쉬운 크기
- `-t`: 시간순 정렬

### 3. 환경 변수 확인

```c
getenv("LS_BLOCK_SIZE")  = nil
getenv("BLOCK_SIZE")     = nil
getenv("BLOCKSIZE")      = nil
getenv("POSIXLY_CORRECT") = nil
getenv("QUOTING_STYLE")  = nil
getenv("TZ")             = nil
```
- **함수**: `getenv()` - 환경 변수 값 가져오기
- **목적**: ls 동작에 영향을 주는 환경 변수 확인
- **결과**: 모두 `nil` - 설정되지 않음

**환경 변수 의미:**
- `LS_BLOCK_SIZE`: 블록 크기 단위
- `BLOCK_SIZE`: 기본 블록 크기
- `POSIXLY_CORRECT`: POSIX 표준 준수 모드
- `QUOTING_STYLE`: 파일명 인용 스타일
- `TZ`: 타임존

### 4. 터미널 확인

```c
isatty(1)  = 0
```
- **함수**: `isatty()` - 파일 디스크립터가 터미널인지 확인
- **인자**: `1` - 표준 출력 (stdout)
- **반환**: `0` - 터미널 아님 (파이프나 리다이렉션)

**동작 차이:**
```bash
# 터미널 출력 (isatty = 1)
ls
# → 컬러 출력, 여러 열

# 파이프 출력 (isatty = 0)
ls | cat
# → 흑백 출력, 한 열
```

### 5. 에러 처리 준비

```c
__errno_location()  = 0x7f34490696a0
```
- **함수**: `__errno_location()` - errno 변수 주소 반환
- **목적**: 에러 코드 저장 위치 확인
- **사용**: 시스템 콜 실패 시 에러 코드 확인

### 6. 메모리 할당

```c
reallocarray(0, 100, 208, 0x647c31e47b00)  = 0x647c31e47b10
```
- **함수**: `reallocarray()` - 배열 메모리 재할당
- **인자**:
  - `0`: 기존 포인터 (NULL)
  - `100`: 요소 개수
  - `208`: 각 요소 크기 (바이트)
- **목적**: 파일 목록 저장할 메모리 할당
- **반환**: 할당된 메모리 주소

### 7. 디렉토리 열기

```c
strlen(".")  = 1
```
- **함수**: `strlen()` - 문자열 길이 계산
- **인자**: `"."` - 현재 디렉토리
- **반환**: `1` - 1바이트

```c
__memcpy_chk(0x647c31e4cc90, 0x647c21314edc, 2, 2)  = 0x647c31e4cc90
```
- **함수**: `__memcpy_chk()` - 안전한 메모리 복사 (버퍼 오버플로우 방지)
- **목적**: `"."` 문자열 복사

```c
opendir(".")  = 0x647c31e4ccb0
```
- **함수**: `opendir()` - 디렉토리 열기
- **인자**: `"."` - 현재 디렉토리
- **반환**: `0x647c31e4ccb0` - 디렉토리 스트림 포인터 (DIR*)

### 8. 파일 읽기

```c
readdir(0x647c31e4ccb0)  = 0x647c31e4cce0
readdir(0x647c31e4ccb0)  = 0x647c31e4ccf8
readdir(0x647c31e4ccb0)  = 0x647c31e4cd10
...
```
- **함수**: `readdir()` - 디렉토리 항목 읽기
- **인자**: `0x647c31e4ccb0` - opendir()에서 반환된 포인터
- **반환**: `struct dirent*` - 디렉토리 항목 정보
- **동작**: 반복 호출로 모든 파일/디렉토리 읽음

**readdir 구조체:**
```c
struct dirent {
    ino_t          d_ino;       // inode 번호
    off_t          d_off;       // 오프셋
    unsigned short d_reclen;    // 레코드 길이
    unsigned char  d_type;      // 파일 타입
    char           d_name[256]; // 파일명
};
```

### 9. 파일명 처리

```c
strlen("check_windows_logs.sh")  = 21
__memcpy_chk(0x647c31e54cf0, 0x647c31e4ce2b, 22, 22)  = 0x647c31e54cf0
```
- **동작**:
  1. `strlen()` - 파일명 길이 계산 (21바이트)
  2. `__memcpy_chk()` - 파일명 복사 (null 포함 22바이트)

```c
strlen("2026-01-26.pcapng")  = 17
__memcpy_chk(0x647c31e54d10, 0x647c31e4cec3, 18, 18)  = 0x647c31e54d10
```
- 각 파일에 대해 동일한 과정 반복

```c
strlen("03_AWS")  = 6
__memcpy_chk(0x647c31e54d30, 0x647c31e4cf0b, 7, 7)  = 0x647c31e54d30
```
- 디렉토리도 동일하게 처리

```c
strlen("proxy_protocol_v2_test.ps1")  = 26
__memcpy_chk(0x647c31e54d70, 0x647c31e4cf53, 27, 27)  = 0x647c31e54d70
```

### 10. 이후 단계 (출력에서 생략됨)

**정렬:**
- `qsort()` - 파일 목록 정렬
- 알파벳순, 시간순 등

**파일 정보 가져오기 (ls -l 시):**
- `stat()` / `lstat()` - 파일 메타데이터
- 크기, 권한, 소유자, 시간 등

**출력:**
- `write()` / `fwrite()` - 표준 출력으로 출력
- 포맷팅 및 컬러 적용

**정리:**
- `closedir()` - 디렉토리 닫기
- `free()` - 메모리 해제

## 전체 실행 흐름

```
1. 초기화
   ├─ strrchr()         - 프로그램 이름 추출
   ├─ setlocale()       - 로케일 설정
   ├─ bindtextdomain()  - 다국어 지원
   └─ __cxa_atexit()    - 종료 핸들러

2. 설정
   ├─ getopt_long()     - 옵션 파싱
   ├─ getenv()          - 환경 변수 확인
   └─ isatty()          - 터미널 확인

3. 메모리 준비
   └─ reallocarray()    - 메모리 할당

4. 디렉토리 처리
   ├─ strlen()          - 경로 길이
   ├─ __memcpy_chk()    - 경로 복사
   └─ opendir()         - 디렉토리 열기

5. 파일 읽기 (반복)
   ├─ readdir()         - 파일 항목 읽기
   ├─ strlen()          - 파일명 길이
   └─ __memcpy_chk()    - 파일명 복사

6. 정렬 및 출력
   ├─ qsort()           - 정렬
   ├─ stat()            - 파일 정보 (ls -l)
   └─ write()           - 출력

7. 정리
   ├─ closedir()        - 디렉토리 닫기
   └─ free()            - 메모리 해제
```

## ltrace 유용한 옵션

### 기본 사용
```bash
# 기본 추적
ltrace ls

# 특정 함수만 추적
ltrace -e opendir,readdir ls

# 시스템 콜도 함께 추적
ltrace -S ls
```

### 출력 제어
```bash
# 시간 측정
ltrace -T ls

# 타임스탬프 표시
ltrace -t ls

# 상대 시간 표시
ltrace -r ls

# 출력 파일로 저장
ltrace -o output.txt ls
```

### 필터링
```bash
# 특정 라이브러리만
ltrace -l /lib/x86_64-linux-gnu/libc.so.6 ls

# 함수 제외
ltrace -e '!strlen' ls

# 여러 함수 추적
ltrace -e 'open*,read*,write*' ls
```

### 프로세스 추적
```bash
# 실행 중인 프로세스 추적
ltrace -p <PID>

# 자식 프로세스도 추적
ltrace -f bash -c "ls | grep test"
```

### 디버깅
```bash
# 상세 출력
ltrace -d ls

# 호출 횟수 카운트
ltrace -c ls
```

## 실용 예제

### 1. 성능 분석
```bash
# 각 함수 실행 시간 측정
ltrace -T ls 2>&1 | grep -E '\[.*\]$'
```

### 2. 메모리 할당 추적
```bash
ltrace -e 'malloc,calloc,realloc,free' ls
```

### 3. 파일 작업 추적
```bash
ltrace -e 'open*,read*,write*,close*' ls
```

### 4. 문자열 처리 추적
```bash
ltrace -e 'str*,mem*' ls
```

### 5. 통계 보기
```bash
ltrace -c ls
```

**출력 예시:**
```
% time     seconds  usecs/call     calls      function
------ ----------- ----------- --------- --------------------
 28.57    0.000040          40         1 opendir
 21.43    0.000030          10         3 strlen
 14.29    0.000020          20         1 setlocale
 ...
```

## 트러블슈팅

### 문제 1: 출력이 너무 많음
```bash
# 특정 함수만 추적
ltrace -e opendir,readdir,closedir ls
```

### 문제 2: 권한 부족
```bash
# sudo 사용
sudo ltrace -p <PID>
```

### 문제 3: 프로그램이 느려짐
```bash
# 버퍼링 사용
ltrace -b ls
```

## ltrace 내부 동작

**ltrace는 어떻게 작동하나?**

1. **ptrace 시스템 콜 사용**
   - 프로세스를 추적하고 제어
   - 함수 호출 시점에 중단

2. **PLT (Procedure Linkage Table) 후킹**
   - 동적 라이브러리 함수 호출 가로채기
   - 함수 진입/종료 시점 기록

3. **심볼 테이블 읽기**
   - ELF 바이너리의 심볼 정보 사용
   - 함수 이름과 주소 매핑

## 제한사항

**ltrace가 추적하지 못하는 것:**

1. **정적 링크된 함수**
   ```bash
   # 정적 링크 확인
   ldd /bin/ls
   # 동적 라이브러리 목록 표시
   ```

2. **인라인 함수**
   - 컴파일러 최적화로 인라인된 함수

3. **시스템 콜**
   - strace 사용 필요

4. **내부 함수**
   - 라이브러리 내부에서만 호출되는 함수

## 관련 도구

| 도구 | 용도 |
|------|------|
| **strace** | 시스템 콜 추적 |
| **gdb** | 소스 레벨 디버깅 |
| **perf** | 성능 프로파일링 |
| **valgrind** | 메모리 분석 |
| **lsof** | 열린 파일 확인 |

## 실무 활용

### 1. 라이브러리 의존성 확인
```bash
ltrace -l /lib/x86_64-linux-gnu/libc.so.6 myapp
```

### 2. 성능 병목 찾기
```bash
ltrace -T -c myapp
```

### 3. 메모리 누수 의심
```bash
ltrace -e 'malloc,free' myapp | grep -c malloc
ltrace -e 'malloc,free' myapp | grep -c free
```

### 4. 설정 파일 로딩 확인
```bash
ltrace -e 'fopen,fread,fclose' myapp
```

### 5. 네트워크 함수 추적
```bash
ltrace -e 'socket,connect,send,recv' myapp
```

## 요약

**ltrace ls는 다음을 보여줍니다:**

1. **초기화**: 로케일, 다국어 지원 설정
2. **옵션 파싱**: 명령줄 옵션 처리
3. **환경 확인**: 환경 변수, 터미널 여부
4. **디렉토리 처리**: opendir, readdir로 파일 읽기
5. **파일명 처리**: strlen, memcpy로 파일명 복사
6. **정렬 및 출력**: 파일 목록 정렬 후 출력

**핵심 가치:**
- 프로그램이 어떤 라이브러리 함수를 호출하는지 확인
- 성능 분석 및 디버깅
- 프로그램 동작 이해

**언제 사용?**
- 프로그램 동작 원리 이해
- 성능 병목 찾기
- 라이브러리 의존성 확인
- 디버깅 및 트러블슈팅

## ltrace vs strace 실전 선택 가이드

### 언제 어떤 도구를 사용할까?

| 상황 | 도구 | 이유 |
|------|------|------|
| **파일을 못 찾음** | strace | 시스템 콜 에러 (ENOENT) 확인 |
| **라이브러리 버전 문제** | ltrace | 함수 호출 및 심볼 확인 |
| **성능 병목** | 둘 다 | 전체 흐름 파악 후 분석 |
| **메모리 누수 의심** | ltrace | malloc/free 추적 |
| **권한 문제** | strace | 시스템 콜 에러 (EACCES, EPERM) |
| **네트워크 연결 실패** | strace | socket, connect 시스템 콜 |
| **설정 파일 로딩** | ltrace | fopen, fread 함수 추적 |
| **프로세스 생성 문제** | strace | fork, execve 시스템 콜 |
| **문자열 처리 버그** | ltrace | strcmp, strcpy 등 함수 |
| **디스크 I/O 느림** | strace | read, write 시스템 콜 |

### 동시 사용 예제

**ltrace와 strace 함께 사용:**
```bash
# 터미널 1: ltrace
ltrace -o ltrace.log myapp

# 터미널 2: strace
strace -o strace.log -p $(pgrep myapp)

# 또는 한 번에
ltrace -S myapp 2>&1 | tee combined.log
```

### 실전 디버깅 워크플로우

**1단계: 문제 파악**
```bash
# 빠른 확인
strace -c myapp
ltrace -c myapp
```

**2단계: 상세 분석**
```bash
# 의심 영역 집중 추적
strace -e trace=file myapp 2>&1 | grep ENOENT
ltrace -e 'fopen,fread' myapp
```

**3단계: 타임라인 분석**
```bash
# 시간 순서로 추적
strace -t -T myapp > strace.log
ltrace -t -T myapp > ltrace.log
```

## 실전 디버깅 시나리오

### 시나리오 1: 설정 파일을 못 찾는 문제

**증상:**
```
Error: Configuration file not found
```

**디버깅:**
```bash
# strace로 파일 접근 추적
strace -e openat,access myapp 2>&1 | grep -i config

# 출력 예시:
# access("/etc/myapp/config.ini", F_OK) = -1 ENOENT
# access("/home/user/.myapp/config.ini", F_OK) = -1 ENOENT
# → 파일 경로 확인!
```

### 시나리오 2: 라이브러리 함수 호출 실패

**증상:**
```
Segmentation fault
```

**디버깅:**
```bash
# ltrace로 마지막 함수 호출 확인
ltrace myapp 2>&1 | tail -20

# 출력 예시:
# malloc(1024) = 0x55555556b2a0
# strcpy(0x55555556b2a0, NULL) = <no return ...>
# → NULL 포인터 전달 문제!
```

### 시나리오 3: 성능 저하

**증상:**
```
프로그램이 느려짐
```

**디버깅:**
```bash
# 시스템 콜 통계
strace -c myapp

# 출력 예시:
# % time     seconds  usecs/call     calls    errors syscall
# ------ ----------- ----------- --------- --------- ----------------
#  99.50    5.234567      523456        10           read
# → read 시스템 콜이 병목!

# 라이브러리 함수 통계
ltrace -c myapp

# 출력 예시:
# % time     seconds  usecs/call     calls      function
# ------ ----------- ----------- --------- --------------------
#  95.23    3.456789      345678        10 fread
# → fread 함수가 병목!
```

### 시나리오 4: 메모리 누수

**증상:**
```
메모리 사용량이 계속 증가
```

**디버깅:**
```bash
# malloc/free 추적
ltrace -e 'malloc,calloc,realloc,free' myapp > mem.log

# 분석
grep malloc mem.log | wc -l  # 할당 횟수
grep free mem.log | wc -l    # 해제 횟수

# 할당 > 해제 → 메모리 누수!
```

## 성능 오버헤드 비교

### 실행 시간 비교

```bash
# 일반 실행
time ls
# real    0m0.003s

# ltrace 사용
time ltrace ls > /dev/null 2>&1
# real    0m0.045s (약 15배 느림)

# strace 사용
time strace ls > /dev/null 2>&1
# real    0m0.025s (약 8배 느림)
```

**결론:**
- ltrace가 strace보다 약 2배 느림
- 프로덕션 환경에서는 짧은 시간만 사용
- 개발/테스트 환경에서 주로 사용

## 자주 발생하는 문제와 해결책

### 문제 1: "Cannot attach to process"

**원인:**
- 권한 부족
- ptrace_scope 설정

**해결:**
```bash
# sudo 사용
sudo ltrace -p <PID>

# ptrace_scope 확인
cat /proc/sys/kernel/yama/ptrace_scope
# 1 = 제한됨

# 임시 해제 (주의!)
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

### 문제 2: "Too many open files"

**원인:**
- 파일 디스크립터 제한

**해결:**
```bash
# 제한 확인
ulimit -n

# 제한 증가
ulimit -n 4096
```

### 문제 3: 출력이 섞임

**원인:**
- stdout과 stderr 혼재

**해결:**
```bash
# 분리 저장
ltrace myapp > ltrace.out 2> ltrace.err

# 또는 합쳐서
ltrace myapp 2>&1 | tee ltrace.log
```

## 에러 코드 해석 가이드

### 일반적인 에러

| 에러 코드 | 의미 | 해결 방법 |
|----------|------|----------|
| **ENOENT** | 파일/디렉토리 없음 | 경로 확인 |
| **EACCES** | 권한 거부 | 권한 확인 (chmod, chown) |
| **ENOMEM** | 메모리 부족 | 메모리 확보 또는 제한 증가 |
| **EINVAL** | 잘못된 인자 | 함수 인자 확인 |
| **EBADF** | 잘못된 파일 디스크립터 | 파일 열기/닫기 확인 |
| **EPERM** | 작업 허용 안 됨 | root 권한 필요 |

## 전체 출력 예시

### ltrace ls 전체 흐름 (요약)

```
초기화 → 옵션 파싱 → 환경 확인 → 디렉토리 열기 → 파일 읽기 → 정렬 → 출력 → 종료
   ↓         ↓           ↓            ↓            ↓         ↓       ↓       ↓
setlocale getopt_long  getenv      opendir      readdir   qsort   write  closedir
```

**실제 출력 (축약):**
```
strrchr("ls", '/') = nil
setlocale(LC_ALL, "") = "en_US.UTF-8"
getopt_long(1, ...) = -1
getenv("LS_BLOCK_SIZE") = nil
isatty(1) = 0
opendir(".") = 0x...
readdir(0x...) = 0x...  (file1)
readdir(0x...) = 0x...  (file2)
readdir(0x...) = 0x...  (file3)
strlen("file1") = 5
memcpy(...) = ...
closedir(0x...) = 0
+++ exited (status 0) +++
```

## 추가 학습 자료

**공식 문서:**
- `man ltrace`
- `man ptrace`

**관련 도구:**
- `strace` - 시스템 콜 추적
- `gdb` - 디버거
- `valgrind` - 메모리 분석
- `perf` - 성능 프로파일링

**온라인 리소스:**
- ltrace GitHub: https://github.com/dkogan/ltrace
- Linux man pages: https://man7.org/

---

## 프로덕션 환경 사용 시 주의사항

### ⚠️ 중요 경고

1. **성능 영향**
   - 10-20배 느려짐
   - 짧은 시간만 사용 (< 5분)
   - 피크 시간대 피하기

2. **보안 고려사항**
   - 민감한 정보 노출 가능 (패스워드, API 키)
   - 로그 파일 권한 주의
   - 완료 후 로그 삭제

3. **시스템 안정성**
   - 중요 서비스는 테스트 환경에서 먼저
   - 모니터링과 함께 사용
   - 비상 중단 계획 준비

### 권장 사용 패턴

```bash
# 1. 짧은 시간 캡처
timeout 60 ltrace -o /tmp/trace.log -p <PID>

# 2. 특정 함수만
ltrace -e 'malloc,free' -p <PID>

# 3. 통계만 (오버헤드 최소)
ltrace -c -p <PID>
```

---

## 문서 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-01-29 | 초기 작성 |

---

**문서 관리자:** SRE Team  
**피드백:** siasia.linux@gmail.com
