# strace - 시스템 콜 추적 도구

> **내부 공유 자료**  
> 작성일: 2026-01-29  
> 버전: 1.0  
> 대상: 개발자, SRE, 시스템 엔지니어

## 목차
- [개요](#strace란)
- [빠른 참조](#빠른-참조)
- [기본 사용법](#strace-ls-실행)
- [실전 예제](#실전-디버깅-시나리오)
- [프로덕션 주의사항](#성능-오버헤드-비교)

## 빠른 참조

```bash
# 가장 많이 사용하는 명령어
strace ./myapp                    # 기본 추적
strace -c ./myapp                 # 통계만
strace -e trace=file ./myapp      # 파일 관련만
strace -p <PID>                   # 실행 중인 프로세스
strace -o output.log ./myapp      # 파일로 저장
strace -T ./myapp                 # 시간 측정
strace -f ./myapp                 # 자식 프로세스 포함
```

## strace란?

**System Call Trace** - 프로그램이 호출하는 시스템 콜(커널 인터페이스)을 추적하는 도구입니다.

### strace vs ltrace

| 도구       | 추적 대상                   | 레벨         |
|------------|-----------------------------|--------------|
| **strace** | 시스템 콜 (커널 인터페이스) | Kernel Space |
| **ltrace** | 라이브러리 함수 (libc 등)   | User Space   |

```
Application (ls)
    v
Library Functions (libc)  ← ltrace
    v
System Calls (kernel)     ← strace
    v
Linux Kernel
    v
Hardware
```

## strace ls 실행

```bash
strace ls
```

## 출력 분석

### 1. 프로그램 실행

```c
execve("/usr/bin/ls", ["ls"], 0x7ffd8b1756f0 /* 16 vars */) = 0
```
- **시스템 콜**: `execve()` - 프로그램 실행
- **인자**:
  - `"/usr/bin/ls"`: 실행할 프로그램 경로
  - `["ls"]`: 명령줄 인자 배열 (argv)
  - `0x7ffd8b1756f0`: 환경 변수 배열 (16개)
- **반환**: `0` - 성공
- **의미**: 쉘이 ls 프로그램을 실행

### 2. 메모리 관리

#### 힙 초기화
```c
brk(NULL) = 0x56b0ff638000
```
- **시스템 콜**: `brk()` - 힙 메모리 경계 설정
- **인자**: `NULL` - 현재 힙 끝 주소 조회
- **반환**: `0x56b0ff638000` - 현재 힙 끝 주소
- **의미**: 프로그램 힙 메모리 시작점 확인

#### 메모리 매핑
```c
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7309343d5000
```
- **시스템 콜**: `mmap()` - 메모리 매핑
- **인자**:
  - `NULL`: 커널이 주소 선택
  - `8192`: 크기 (8KB)
  - `PROT_READ|PROT_WRITE`: 읽기/쓰기 권한
  - `MAP_PRIVATE|MAP_ANONYMOUS`: 프라이빗, 익명 매핑
  - `-1`: 파일 디스크립터 없음
  - `0`: 오프셋
- **반환**: `0x7309343d5000` - 매핑된 메모리 주소
- **의미**: 8KB 메모리 할당

### 3. 동적 라이브러리 로딩

#### ld.so.preload 확인
```c
access("/etc/ld.so.preload", R_OK) = -1 ENOENT (No such file or directory)
```
- **시스템 콜**: `access()` - 파일 접근 가능 여부 확인
- **인자**:
  - `"/etc/ld.so.preload"`: 미리 로드할 라이브러리 목록
  - `R_OK`: 읽기 권한 확인
- **반환**: `-1 ENOENT` - 파일 없음
- **의미**: 사전 로드 라이브러리 없음

#### 라이브러리 캐시 열기
```c
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
```
- **시스템 콜**: `openat()` - 파일 열기
- **인자**:
  - `AT_FDCWD`: 현재 작업 디렉토리 기준
  - `"/etc/ld.so.cache"`: 라이브러리 캐시 파일
  - `O_RDONLY`: 읽기 전용
  - `O_CLOEXEC`: exec 시 자동 닫기
- **반환**: `3` - 파일 디스크립터
- **의미**: 동적 라이브러리 위치 정보 로드

#### 파일 정보 확인
```c
fstat(3, {st_mode=S_IFREG|0644, st_size=19247, ...}) = 0
```
- **시스템 콜**: `fstat()` - 파일 상태 확인
- **인자**:
  - `3`: 파일 디스크립터
  - 구조체 포인터
- **반환**: `0` - 성공
- **정보**:
  - `S_IFREG`: 일반 파일
  - `0644`: 권한 (rw-r--r--)
  - `st_size=19247`: 크기 19247바이트

#### 캐시 파일 매핑
```c
mmap(NULL, 19247, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7309343d0000
```
- **의미**: 캐시 파일을 메모리에 매핑

#### 파일 닫기
```c
close(3) = 0
```
- **시스템 콜**: `close()` - 파일 디스크립터 닫기
- **인자**: `3` - 파일 디스크립터
- **반환**: `0` - 성공

### 4. libselinux.so.1 로딩

```c
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libselinux.so.1", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\0\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\0\0\0\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0644, st_size=174472, ...}) = 0
```
- **동작**:
  1. SELinux 라이브러리 열기
  2. ELF 헤더 읽기 (`\177ELF` = ELF 매직 넘버)
  3. 파일 정보 확인

#### 라이브러리 메모리 매핑
```c
mmap(NULL, 181960, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7309343a3000
mmap(0x7309343a9000, 118784, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x6000) = 0x7309343a9000
mmap(0x7309343c6000, 24576, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x23000) = 0x7309343c6000
mmap(0x7309343cc000, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x29000) = 0x7309343cc000
```
- **의미**: 라이브러리를 여러 세그먼트로 메모리에 매핑
  - 읽기 전용 세그먼트
  - 실행 가능 세그먼트 (코드)
  - 읽기/쓰기 세그먼트 (데이터)

```c
close(3) = 0
```

### 5. libc.so.6 로딩 (C 표준 라이브러리)

```c
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\220\243\2\0\0\0\0\0"..., 832) = 832
```
- **의미**: C 표준 라이브러리 로딩 시작

#### pread64 사용
```c
pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
```
- **시스템 콜**: `pread64()` - 특정 위치에서 읽기
- **인자**:
  - `3`: 파일 디스크립터
  - 버퍼
  - `784`: 읽을 바이트 수
  - `64`: 오프셋
- **의미**: 파일의 특정 위치(64바이트)부터 읽기

```c
fstat(3, {st_mode=S_IFREG|0755, st_size=2125328, ...}) = 0
```
- **크기**: 2,125,328 바이트 (약 2MB)

#### libc 메모리 매핑
```c
mmap(NULL, 2170256, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x730934000000
mmap(0x730934028000, 1605632, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x28000) = 0x730934028000
mmap(0x7309341b0000, 323584, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1b0000) = 0x7309341b0000
mmap(0x7309341ff000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1fe000) = 0x7309341ff000
```
- **의미**: libc를 여러 세그먼트로 매핑 (약 2MB)

```c
close(3) = 0
```

### 6. libpcre2 로딩 (정규표현식 라이브러리)

```c
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libpcre2-8.so.0", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\0\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\0\0\0\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0644, st_size=625344, ...}) = 0
mmap(NULL, 627472, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x730934309000
close(3) = 0
```
- **의미**: 정규표현식 처리 라이브러리 로딩 (ls의 패턴 매칭용)

### 7. 스레드 및 프로세스 설정

#### 스레드 로컬 스토리지 설정
```c
arch_prctl(ARCH_SET_FS, 0x730934306800) = 0
```
- **시스템 콜**: `arch_prctl()` - 아키텍처별 프로세스 제어
- **의미**: 스레드별 데이터 저장 공간 설정

#### TID 주소 설정
```c
set_tid_address(0x730934306ad0) = 173365
```
- **반환**: `173365` - 현재 스레드 ID (TID)

#### Robust Futex 설정
```c
set_robust_list(0x730934306ae0, 24) = 0
```
- **의미**: 스레드 동기화 메커니즘 (뮤텍스)

#### Restartable Sequences
```c
rseq(0x730934307120, 0x20, 0, 0x53053053) = 0
```
- **의미**: CPU 마이그레이션 시 성능 최적화

### 8. 메모리 보호

```c
mprotect(0x7309341ff000, 16384, PROT_READ) = 0
mprotect(0x7309343a1000, 4096, PROT_READ) = 0
```
- **시스템 콜**: `mprotect()` - 메모리 영역 보호 속성 변경
- **의미**: 쓰기 가능했던 메모리를 읽기 전용으로 변경 (보안)

### 9. 리소스 제한 확인

```c
prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
```
- **반환**: 스택 크기 제한 8MB, 최대 무제한

### 10. 캐시 정리

```c
munmap(0x7309343d0000, 19247) = 0
```
- **의미**: ld.so.cache 파일 매핑 해제

### 11. SELinux 확인

```c
statfs("/sys/fs/selinux", 0x7ffcf0b4a740) = -1 ENOENT (No such file or directory)
statfs("/selinux", 0x7ffcf0b4a740) = -1 ENOENT (No such file or directory)
```
- **의미**: SELinux가 비활성화됨

### 12. 난수 생성

```c
getrandom("\x5b\x98\x60\xd6\x85\xf3\xf6\xe6", 8, GRND_NONBLOCK) = 8
```
- **의미**: 보안 관련 난수 생성 (ASLR 등)

### 13. 힙 확장

```c
brk(NULL) = 0x56b0ff638000
brk(0x56b0ff659000) = 0x56b0ff659000
```
- **크기**: 약 132KB 확장

### 14. 파일시스템 정보 확인

```c
openat(AT_FDCWD, "/proc/filesystems", O_RDONLY|O_CLOEXEC) = 3
read(3, "nodev\tsysfs\nnodev\ttmpfs\nnodev\tbd"..., 1024) = 405
close(3) = 0
```
- **의미**: 시스템에서 지원하는 파일시스템 확인

### 15. 로케일 데이터 로딩

```c
openat(AT_FDCWD, "/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=5584640, ...}) = 0
mmap(NULL, 5584640, PROT_READ, MAP_PRIVATE, 3, 0) = 0x730933a00000
close(3) = 0
```
- **크기**: 5.3MB
- **의미**: 다국어 지원 데이터 로딩

### 16. 터미널 확인

```c
ioctl(1, TCGETS, 0x7ffcf0b4a5e0) = -1 ENOTTY (Inappropriate ioctl for device)
```
- **의미**: 출력이 파이프나 리다이렉션됨 (컬러 출력 비활성화)

### 17. 디렉토리 열기

```c
openat(AT_FDCWD, ".", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 3
fstat(3, {st_mode=S_IFDIR|0750, st_size=4096, ...}) = 0
```
- **의미**: 현재 디렉토리 열기

### 18. 디렉토리 항목 읽기

```c
getdents64(3, 0x56b0ff63ece0 /* 66 entries */, 32768) = 2624
getdents64(3, 0x56b0ff63ece0 /* 0 entries */, 32768) = 0
close(3) = 0
```
- **정보**: 66개 파일/디렉토리 읽음
- **의미**: 디렉토리 읽기 완료

### 19. 출력

```c
fstat(1, {st_mode=S_IFIFO|0600, st_size=0, ...}) = 0
write(1, "03_AWS\n04_zabbix_haproxy_setup.s"..., 952) = 952
```
- **크기**: 952바이트 출력
- **의미**: 파일 목록 출력

### 20. 프로그램 종료

```c
close(1) = 0
close(2) = 0
exit_group(0) = ?
+++ exited with 0 +++
```
- **의미**: 프로그램 정상 종료

## 전체 실행 흐름

```
1. 프로그램 시작
   └─ execve() - ls 실행

2. 메모리 초기화
   ├─ brk() - 힙 초기화
   └─ mmap() - 메모리 할당

3. 동적 라이브러리 로딩
   ├─ libselinux.so.1 (SELinux)
   ├─ libc.so.6 (C 표준 라이브러리)
   └─ libpcre2-8.so.0 (정규표현식)

4. 프로세스 설정
   ├─ arch_prctl() - 스레드 로컬 스토리지
   ├─ set_tid_address() - TID 설정
   └─ set_robust_list() - Futex 설정

5. 보안 설정
   ├─ mprotect() - 메모리 보호
   └─ getrandom() - 난수 생성

6. 환경 확인
   ├─ statfs() - SELinux 확인
   └─ ioctl() - 터미널 확인

7. 디렉토리 처리
   ├─ openat() - 디렉토리 열기
   ├─ getdents64() - 항목 읽기
   └─ close() - 디렉토리 닫기

8. 출력 및 종료
   ├─ write() - 파일 목록 출력
   └─ exit_group() - 프로세스 종료
```

## strace 유용한 옵션

### 기본 사용
```bash
# 기본 추적
strace ls

# 특정 시스템 콜만 추적
strace -e openat,read,write ls

# 파일 관련만
strace -e trace=file ls

# 네트워크 관련만
strace -e trace=network curl google.com
```

### 출력 제어
```bash
# 시간 측정
strace -T ls

# 타임스탬프 표시
strace -t ls

# 상대 시간 표시
strace -r ls

# 출력 파일로 저장
strace -o output.txt ls
```

### 통계
```bash
# 시스템 콜 통계
strace -c ls
```

**출력 예시:**
```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 35.71    0.000050          50         1           openat
 28.57    0.000040          40         1           getdents64
 14.29    0.000020          20         1           write
```

### 프로세스 추적
```bash
# 실행 중인 프로세스 추적
strace -p <PID>

# 자식 프로세스도 추적
strace -f bash -c "ls | grep test"

# 새 프로세스 추적
strace -ff -o trace bash -c "ls"
```

### 필터링
```bash
# 여러 시스템 콜
strace -e open,openat,read,write ls

# 정규표현식
strace -e trace=/open ls

# 제외
strace -e '!mmap,mprotect' ls
```

### 상세 출력
```bash
# 문자열 길이 증가
strace -s 200 ls

# 구조체 상세 출력
strace -v ls

# 시그널 추적
strace -e signal=all ls
```

## 실용 예제

### 1. 파일 접근 추적
```bash
strace -e trace=file ls
```

### 2. 네트워크 디버깅
```bash
strace -e trace=network curl google.com
```

### 3. 성능 분석
```bash
strace -c -S time ls
```

### 4. 에러 찾기
```bash
strace -e trace=open,openat ls 2>&1 | grep ENOENT
```

### 5. 프로세스 생성 추적
```bash
strace -e trace=process bash -c "ls | wc -l"
```

### 6. 메모리 할당 추적
```bash
strace -e trace=memory ls
```

### 7. IPC 추적
```bash
strace -e trace=ipc myapp
```

## 시스템 콜 카테고리

| 카테고리     | 시스템 콜 예시                         |
|--------------|----------------------------------------|
| **파일**     | open, openat, read, write, close, stat |
| **프로세스** | fork, execve, exit, wait, kill         |
| **메모리**   | mmap, munmap, brk, mprotect            |
| **네트워크** | socket, connect, send, recv, bind      |
| **IPC**      | pipe, msgget, semget, shmget           |
| **시그널**   | signal, sigaction, kill, sigprocmask   |
| **디렉토리** | openat, getdents, mkdir, rmdir         |

## 트러블슈팅

### 문제 1: 출력이 너무 많음
```bash
# 특정 시스템 콜만
strace -e openat,read,write ls

# 통계만
strace -c ls
```

### 문제 2: 권한 부족
```bash
# sudo 사용
sudo strace -p <PID>
```

### 문제 3: 프로그램이 느려짐
```bash
# 버퍼링 사용
strace -b ls
```

### 문제 4: 자식 프로세스 추적 안 됨
```bash
# -f 옵션 사용
strace -f bash -c "ls | grep test"
```

## strace 내부 동작

**strace는 어떻게 작동하나?**

1. **ptrace 시스템 콜 사용**
   - 프로세스를 추적하고 제어
   - 시스템 콜 진입/종료 시점에 중단

2. **시스템 콜 가로채기**
   - 커널 진입 시점에서 중단
   - 인자와 반환값 기록

3. **시그널 처리**
   - SIGTRAP 시그널 사용
   - 프로세스 상태 확인

## 제한사항

**strace가 추적하지 못하는 것:**

1. **라이브러리 함수**
   - ltrace 사용 필요

2. **커널 내부 동작**
   - ftrace, perf 사용 필요

3. **최적화된 시스템 콜**
   - vDSO (virtual Dynamic Shared Object)
   - 일부 시스템 콜은 커널 진입 없이 실행

## 관련 도구

| 도구         | 용도                 |
|--------------|----------------------|
| **ltrace**   | 라이브러리 함수 추적 |
| **perf**     | 성능 프로파일링      |
| **ftrace**   | 커널 함수 추적       |
| **bpftrace** | eBPF 기반 추적       |
| **lsof**     | 열린 파일 확인       |

## 실무 활용

### 1. 파일 접근 문제
```bash
strace -e trace=file myapp 2>&1 | grep ENOENT
```

### 2. 성능 병목 찾기
```bash
strace -c -S time myapp
```

### 3. 네트워크 연결 문제
```bash
strace -e trace=network myapp
```

### 4. 권한 문제
```bash
strace -e trace=file myapp 2>&1 | grep EACCES
```

### 5. 메모리 할당 추적
```bash
strace -e trace=memory myapp
```

## 요약

**strace ls는 다음을 보여줍니다:**

1. **프로그램 실행**: execve()
2. **라이브러리 로딩**: openat(), mmap()
3. **프로세스 설정**: arch_prctl(), set_tid_address()
4. **보안 설정**: mprotect(), getrandom()
5. **디렉토리 읽기**: openat(), getdents64()
6. **출력**: write()
7. **종료**: exit_group()

**핵심 가치:**
- 프로그램이 커널과 어떻게 상호작용하는지 확인
- 시스템 콜 레벨에서 디버깅
- 성능 분석 및 최적화

**언제 사용?**
- 파일 접근 문제 디버깅
- 성능 병목 찾기
- 시스템 콜 에러 확인
- 프로그램 동작 이해

## ltrace vs strace 실전 선택 가이드

### 언제 어떤 도구를 사용할까?

| 상황                     | 도구   | 이유                           |
|--------------------------|--------|--------------------------------|
| **파일을 못 찾음**       | strace | 시스템 콜 에러 (ENOENT) 확인   |
| **라이브러리 버전 문제** | ltrace | 함수 호출 및 심볼 확인         |
| **성능 병목**            | 둘 다  | 전체 흐름 파악 후 분석         |
| **메모리 누수 의심**     | ltrace | malloc/free 추적               |
| **권한 문제**            | strace | 시스템 콜 에러 (EACCES, EPERM) |
| **네트워크 연결 실패**   | strace | socket, connect 시스템 콜      |
| **설정 파일 로딩**       | 둘 다  | ltrace(fopen), strace(openat)  |
| **프로세스 생성 문제**   | strace | fork, execve 시스템 콜         |
| **디스크 I/O 느림**      | strace | read, write 시스템 콜          |
| **라이브러리 함수 버그** | ltrace | 함수 인자 및 반환값 확인       |

### 동시 사용 예제

**ltrace와 strace 함께 사용:**
```bash
# 방법 1: ltrace에서 시스템 콜도 추적
ltrace -S myapp 2>&1 | tee combined.log

# 방법 2: 별도 파일로 저장
ltrace -o ltrace.log myapp &
strace -o strace.log -p $(pgrep myapp)

# 방법 3: 타임스탬프로 비교
ltrace -t myapp > ltrace.log 2>&1 &
strace -t -p $(pgrep myapp) > strace.log 2>&1
```

### 실전 디버깅 워크플로우

**1단계: 빠른 진단**
```bash
# 통계로 병목 확인
strace -c myapp
ltrace -c myapp
```

**2단계: 문제 영역 집중**
```bash
# 파일 문제
strace -e trace=file myapp 2>&1 | grep -E "ENOENT|EACCES"

# 메모리 문제
ltrace -e 'malloc,free' myapp

# 네트워크 문제
strace -e trace=network myapp
```

**3단계: 타임라인 분석**
```bash
# 시간 순서로 추적
strace -tt -T myapp > strace.log
ltrace -tt -T myapp > ltrace.log
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
# openat(AT_FDCWD, "/usr/local/etc/myapp.conf", O_RDONLY) = -1 ENOENT
```

**해결:**
```bash
# 올바른 경로에 파일 생성
sudo mkdir -p /etc/myapp
sudo cp config.ini /etc/myapp/
```

### 시나리오 2: 라이브러리 함수 호출 실패

**증상:**
```
Segmentation fault (core dumped)
```

**디버깅:**
```bash
# ltrace로 마지막 함수 호출 확인
ltrace myapp 2>&1 | tail -30

# 출력 예시:
# malloc(1024) = 0x55555556b2a0
# strcpy(0x55555556b2a0, NULL) = <no return ...>
# +++ killed by SIGSEGV +++
```

**원인:** NULL 포인터를 strcpy에 전달

### 시나리오 3: 성능 저하 분석

**증상:**
```
프로그램이 예상보다 10배 느림
```

**디버깅:**
```bash
# 시스템 콜 통계
strace -c -S time myapp

# 출력:
# % time     seconds  usecs/call     calls    errors syscall
# ------ ----------- ----------- --------- --------- ----------------
#  99.50    5.234567      523456        10           read
#   0.30    0.015678        1567        10           write
#   0.20    0.010456        1045        10           openat
```

**분석:** read 시스템 콜이 99.5% 시간 소비 → I/O 병목

**해결:**
```bash
# 버퍼 크기 증가 또는 비동기 I/O 사용
```

### 시나리오 4: 메모리 누수 확인

**증상:**
```
메모리 사용량이 시간이 지날수록 증가
```

**디버깅:**
```bash
# malloc/free 추적
ltrace -e 'malloc,calloc,realloc,free' myapp > mem.log

# 분석
echo "Allocations: $(grep -c malloc mem.log)"
echo "Frees: $(grep -c free mem.log)"

# 출력:
# Allocations: 1523
# Frees: 1245
# → 278개 메모리 블록 누수!
```

### 시나리오 5: 권한 문제

**증상:**
```
Permission denied
```

**디버깅:**
```bash
# 권한 관련 에러 추적
strace myapp 2>&1 | grep -E "EACCES|EPERM"

# 출력:
# openat(AT_FDCWD, "/var/log/myapp.log", O_WRONLY|O_CREAT, 0644) = -1 EACCES
# → /var/log에 쓰기 권한 없음
```

**해결:**
```bash
# 권한 부여 또는 다른 경로 사용
sudo chmod 666 /var/log/myapp.log
# 또는
# 로그를 /tmp나 홈 디렉토리에 저장
```

## 성능 오버헤드 비교

### 실행 시간 비교

```bash
# 일반 실행
time ls -R /usr > /dev/null
# real    0m0.150s

# ltrace 사용
time ltrace ls -R /usr > /dev/null 2>&1
# real    0m2.250s (약 15배 느림)

# strace 사용
time strace ls -R /usr > /dev/null 2>&1
# real    0m1.200s (약 8배 느림)
```

**오버헤드 요약:**
- **ltrace**: 10-20배 느림 (함수 호출마다 중단)
- **strace**: 5-10배 느림 (시스템 콜마다 중단)
- **프로덕션**: 짧은 시간만 사용 권장
- **개발/테스트**: 자유롭게 사용

## 자주 발생하는 문제와 해결책

### 문제 1: "Cannot attach to process"

**에러:**
```
Could not attach to process. ptrace: Operation not permitted
```

**원인:**
- 권한 부족
- ptrace_scope 설정
- 다른 프로세스가 이미 추적 중

**해결:**
```bash
# 1. sudo 사용
sudo strace -p <PID>

# 2. ptrace_scope 확인
cat /proc/sys/kernel/yama/ptrace_scope
# 0 = 제한 없음
# 1 = 부모-자식만 (기본값)
# 2 = admin만
# 3 = 완전 비활성화

# 3. 임시 해제 (주의!)
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope

# 4. 영구 설정
echo "kernel.yama.ptrace_scope = 0" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 문제 2: "Too many open files"

**에러:**
```
strace: open: Too many open files
```

**해결:**
```bash
# 현재 제한 확인
ulimit -n

# 임시 증가
ulimit -n 4096

# 영구 설정 (/etc/security/limits.conf)
* soft nofile 4096
* hard nofile 8192
```

### 문제 3: 출력이 섞임

**문제:**
- stdout과 stderr가 섞여서 읽기 어려움

**해결:**
```bash
# 방법 1: 분리 저장
strace myapp > stdout.log 2> strace.log

# 방법 2: 합쳐서 저장
strace myapp 2>&1 | tee combined.log

# 방법 3: strace만 파일로
strace -o strace.log myapp
```

### 문제 4: 프로그램이 멈춤

**원인:**
- 버퍼링 문제
- 데드락

**해결:**
```bash
# 버퍼링 비활성화
strace -o output.log myapp

# 또는 unbuffer 사용
unbuffer strace myapp | tee output.log
```

## 에러 코드 해석 가이드

### 파일 관련 에러

| 에러 코드   | 의미                      | 일반적인 원인        | 해결 방법            |
|-------------|---------------------------|----------------------|----------------------|
| **ENOENT**  | No such file or directory | 파일/디렉토리 없음   | 경로 확인, 파일 생성 |
| **EACCES**  | Permission denied         | 권한 부족            | chmod, chown, sudo   |
| **EISDIR**  | Is a directory            | 파일 대신 디렉토리   | 경로 확인            |
| **ENOTDIR** | Not a directory           | 디렉토리 대신 파일   | 경로 확인            |
| **EEXIST**  | File exists               | 파일이 이미 존재     | 다른 이름 사용       |
| **EROFS**   | Read-only file system     | 읽기 전용 파일시스템 | 마운트 옵션 확인     |

### 메모리 관련 에러

| 에러 코드  | 의미          | 해결 방법              |
|------------|---------------|------------------------|
| **ENOMEM** | Out of memory | 메모리 확보, swap 증가 |
| **EFAULT** | Bad address   | 포인터 확인            |

### 프로세스 관련 에러

| 에러 코드  | 의미                    | 해결 방법        |
|------------|-------------------------|------------------|
| **EPERM**  | Operation not permitted | root 권한 필요   |
| **ESRCH**  | No such process         | PID 확인         |
| **ECHILD** | No child processes      | wait() 호출 확인 |

### 네트워크 관련 에러

| 에러 코드        | 의미                   | 해결 방법            |
|------------------|------------------------|----------------------|
| **ECONNREFUSED** | Connection refused     | 서버 실행 확인       |
| **ETIMEDOUT**    | Connection timed out   | 네트워크/방화벽 확인 |
| **ENETUNREACH**  | Network is unreachable | 라우팅 확인          |

## 전체 출력 예시

### strace ls 전체 흐름 (요약)

```
프로그램 실행 → 라이브러리 로딩 → 프로세스 설정 → 디렉토리 열기 → 파일 읽기 → 출력 → 종료
      v              v                v               v            v         v       v
   execve         openat           arch_prctl       openat      getdents64  write  exit_group
                  mmap             set_tid_address  fstat
                  close            mprotect
```

**실제 출력 (축약):**
```
execve("/usr/bin/ls", ["ls"], ...) = 0
brk(NULL) = 0x...
mmap(NULL, 8192, PROT_READ|PROT_WRITE, ...) = 0x...
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=19247, ...}) = 0
close(3) = 0
openat(AT_FDCWD, ".", O_RDONLY|O_DIRECTORY) = 3
getdents64(3, /* 66 entries */, 32768) = 2624
getdents64(3, /* 0 entries */, 32768) = 0
close(3) = 0
write(1, "file1\nfile2\nfile3\n", 18) = 18
exit_group(0) = ?
+++ exited with 0 +++
```

## 고급 활용 팁

### 1. 특정 시간대만 추적

```bash
# 5초 후 추적 시작
sleep 5 && strace -p $(pgrep myapp) -o trace.log &

# 10초간만 추적
timeout 10 strace -p $(pgrep myapp)
```

### 2. 여러 프로세스 동시 추적

```bash
# 모든 nginx worker 추적
for pid in $(pgrep nginx); do
    strace -p $pid -o nginx-$pid.log &
done
```

### 3. 조건부 추적

```bash
# 에러만 추적
strace -e trace=all -e fault=all myapp 2>&1 | grep -E "= -1"

# 느린 시스템 콜만
strace -T myapp 2>&1 | awk '$NF > 0.1'
```

### 4. 실시간 모니터링

```bash
# 실시간으로 파일 접근 모니터링
strace -e trace=file -p $(pgrep myapp) 2>&1 | grep --line-buffered openat
```

## 추가 학습 자료

**공식 문서:**
- `man strace`
- `man ptrace`
- `man syscalls`

**관련 도구:**
- `ltrace` - 라이브러리 함수 추적
- `gdb` - 소스 레벨 디버거
- `perf` - 성능 프로파일링
- `bpftrace` - eBPF 기반 추적
- `ftrace` - 커널 함수 추적

**온라인 리소스:**
- strace GitHub: https://github.com/strace/strace
- Linux man pages: https://man7.org/
- System call table: https://syscalls.kernelgrok.com/

---

## 프로덕션 환경 사용 시 주의사항

### ⚠️ 중요 경고

1. **성능 영향**
   - 5-10배 느려짐
   - 짧은 시간만 사용 (< 10분)
   - 피크 시간대 피하기

2. **보안 고려사항**
   - 시스템 콜 인자에 민감 정보 포함 가능
   - 로그 파일 권한 600으로 설정
   - 완료 후 즉시 로그 검토 및 삭제

3. **시스템 안정성**
   - 중요 서비스는 테스트 환경에서 먼저
   - `-f` 옵션 사용 시 주의 (많은 프로세스 추적)
   - 디스크 공간 확인 (로그 크기 클 수 있음)

### 권장 사용 패턴

```bash
# 1. 통계만 (오버헤드 최소)
strace -c -p <PID>

# 2. 특정 시스템 콜만
strace -e trace=file -p <PID>

# 3. 시간 제한
timeout 300 strace -o /tmp/trace.log -p <PID>

# 4. 로그 크기 제한
strace -o /tmp/trace.log -s 128 -p <PID>
```

---

## 문서 변경 이력

| 버전 | 날짜       | 변경 내용 |
|------|------------|-----------|
| 1.0  | 2026-01-29 | 초기 작성 |

---

**문서 관리자:** siasia86
**피드백:** siasia.linux@gmail.com
