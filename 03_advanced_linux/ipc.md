# IPC — 프로세스 간 통신

Linux에서 프로세스 간 데이터를 주고받는 메커니즘을 정리합니다.

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 파이프](#2-파이프) / [3. 시그널](#3-시그널)                                                 |
| [4. System V IPC](#4-system-v-ipc) / [5. POSIX IPC](#5-posix-ipc) / [6. 소켓](#6-소켓)                               |
| [7. IPC namespace](#7-ipc-namespace) / [8. 트러블슈팅](#8-트러블슈팅) / [9. 비교 및 선택 기준](#9-비교-및-선택-기준) |

---

## 1. 개요

IPC(Inter-Process Communication)는 프로세스 간 데이터 교환 및 동기화 방법입니다.

```
┌──────────────────────────────────────────────────────────┐
│  IPC Mechanisms                                          │
│                                                          │
│  Unidirectional ── pipe (pipe, FIFO)                     │
│  Signal         ── signal                                │
│  Shared         ── shared memory (shm)  ┐                │
│  Sync           ── semaphore            ├── SysV / POSIX │
│  Message        ── message queue (mq)   ┘                │
│  Bidirectional  ── socket (Unix Domain)                  │
└──────────────────────────────────────────────────────────┘
```
- Unidirectional: 단방향 / Signal: 시그널 / Shared: 공유 메모리
- Sync: 동기화(세마포어) / Message: 메시지 큐 / Bidirectional: 양방향

| 방식        | 속도 | 복잡도 | 적합한 상황                |
|-------------|------|--------|----------------------------|
| 파이프      | 중간 | 낮음   | 부모-자식, 단방향 스트림   |
| 공유 메모리 | 빠름 | 높음   | 대용량 데이터, 같은 호스트 |
| 메시지 큐   | 중간 | 중간   | 구조화된 메시지, 비동기    |
| 세마포어    | 빠름 | 중간   | 동기화, 뮤텍스             |
| Unix 소켓   | 빠름 | 중간   | 같은 호스트, 양방향        |
| TCP 소켓    | 느림 | 낮음   | 네트워크, 범용             |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 파이프

### 익명 파이프 (pipe)

부모-자식 프로세스 간 단방향 통신입니다.

```bash
# 쉘에서 파이프
ls -al | grep ".md"

# 파이프 버퍼 크기 확인 (기본 64KB)
cat /proc/sys/fs/pipe-max-size
```

```c
#include <unistd.h>

int fd[2];
pipe(fd);
// fd[0] = 읽기 끝, fd[1] = 쓰기 끝

if (fork() == 0) {
    close(fd[1]);
    read(fd[0], buf, sizeof(buf));   // 자식: 읽기
} else {
    close(fd[0]);
    write(fd[1], "hello", 5);        // 부모: 쓰기
}
```

### Named 파이프 (FIFO)

파일시스템에 이름을 가진 파이프입니다. 관계없는 프로세스 간 통신 가능합니다.

```bash
# FIFO 생성
mkfifo /tmp/myfifo

# 프로세스 A (쓰기)
echo "hello" > /tmp/myfifo

# 프로세스 B (읽기) — A가 쓸 때까지 블록
cat /tmp/myfifo

# 확인
ls -al /tmp/myfifo
# prw-r--r-- 1 user user 0 ... /tmp/myfifo
# p = pipe 파일 타입
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 시그널

프로세스에 비동기 이벤트를 전달합니다. 데이터 전달보다 제어 목적으로 사용합니다.

```bash
# 주요 시그널
kill -l

# 시그널 전송
kill -SIGTERM <pid>   # 정상 종료 요청 (15)
kill -SIGKILL <pid>   # 강제 종료 (9, 무시 불가)
kill -SIGHUP  <pid>   # 설정 재로드 (1)
kill -SIGUSR1 <pid>   # 사용자 정의 (10)

# 프로세스 그룹 전체에 전송
kill -SIGTERM -<pgid>
```

| 시그널    | 번호  | 기본 동작           | 무시 가능 |
|-----------|-------|---------------------|-----------|
| SIGTERM   | 15    | 종료                | ✅         |
| SIGKILL   | 9     | 강제 종료           | ❌         |
| SIGHUP    | 1     | 종료/재로드         | ✅         |
| SIGINT    | 2     | 종료 (Ctrl+C)       | ✅         |
| SIGCHLD   | 17    | 자식 상태 변경 알림 | ✅         |
| SIGUSR1/2 | 10/12 | 사용자 정의         | ✅         |

[⬆ 목차로 돌아가기](#목차)

---

## 4. System V IPC

커널이 관리하는 IPC 객체입니다. 프로세스 종료 후에도 커널에 남습니다.

### 공통 명령어

```bash
# 전체 IPC 객체 조회
ipcs
ipcs -a   # 상세

# 종류별 조회
ipcs -m   # 공유 메모리 (shared memory)
ipcs -s   # 세마포어 (semaphore)
ipcs -q   # 메시지 큐 (message queue)

# 삭제
ipcrm -m <shmid>   # 공유 메모리 삭제
ipcrm -s <semid>   # 세마포어 삭제
ipcrm -q <msqid>   # 메시지 큐 삭제

# 전체 삭제 (주의)
ipcs -m | awk 'NR>3 {print $2}' | xargs -I{} ipcrm -m {}
```

### 공유 메모리 (shmget)

가장 빠른 IPC 방식입니다. 커널을 거치지 않고 메모리를 직접 공유합니다.

```bash
# 공유 메모리 상태 확인
ipcs -m
# ------ Shared Memory Segments --------
# key        shmid      owner      perms      bytes      nattch
# 0x00000000 131072     postgres   600        56         6
#                                             ^^^^       ^^^^^
#                                             크기(bytes) 연결 프로세스 수
```

```c
#include <sys/shm.h>

// 생성 (key, size, flags)
int shmid = shmget(IPC_PRIVATE, 4096, IPC_CREAT | 0666);

// 연결 (attach)
void *ptr = shmat(shmid, NULL, 0);

// 사용
strcpy(ptr, "hello");

// 분리 (detach)
shmdt(ptr);

// 삭제
shmctl(shmid, IPC_RMID, NULL);
```

### 세마포어 (semget)

프로세스 간 동기화 및 상호 배제(mutex)에 사용합니다.

```bash
# 세마포어 확인
ipcs -s
# ------ Semaphore Arrays --------
# key        semid      owner      perms      nsems
# 0x00000000 0          postgres   600        17
#                                             ^^^^^
#                                             세마포어 개수
```

```c
#include <sys/sem.h>

int semid = semget(IPC_PRIVATE, 1, IPC_CREAT | 0666);

struct sembuf sb = {0, -1, 0};  // 세마포어 0번, -1 (P 연산, 잠금)
semop(semid, &sb, 1);

// 임계 구역
// ...

sb.sem_op = 1;  // +1 (V 연산, 해제)
semop(semid, &sb, 1);
```

### 메시지 큐 (msgget)

구조화된 메시지를 비동기로 전달합니다.

```bash
# 메시지 큐 확인
ipcs -q
# ------ Message Queues --------
# key        msqid      owner      perms      used-bytes   messages
```

```c
#include <sys/msg.h>

struct msgbuf {
    long mtype;    // 메시지 타입 (> 0)
    char mtext[256];
};

int msqid = msgget(IPC_PRIVATE, IPC_CREAT | 0666);

// 전송
struct msgbuf msg = {1, "hello"};
msgsnd(msqid, &msg, strlen(msg.mtext), 0);

// 수신 (타입 1인 메시지)
msgrcv(msqid, &msg, sizeof(msg.mtext), 1, 0);
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. POSIX IPC

System V IPC의 현대적 대안입니다. 파일 경로 기반 이름을 사용합니다.

### POSIX 공유 메모리

```bash
# /dev/shm 에 파일로 존재
ls /dev/shm/

# Python 예시
python3 -c "
import mmap, os
fd = os.open('/dev/shm/test', os.O_CREAT | os.O_RDWR)
os.ftruncate(fd, 4096)
m = mmap.mmap(fd, 4096)
m.write(b'hello')
m.seek(0)
print(m.read(5))
m.close()
os.close(fd)
"
```

```c
#include <fcntl.h>
#include <sys/mman.h>

// 생성
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0666);
ftruncate(fd, 4096);

// 매핑
void *ptr = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

// 삭제
shm_unlink("/myshm");
```

### POSIX 메시지 큐

```bash
# 메시지 큐 목록 (/dev/mqueue 마운트 필요)
ls /dev/mqueue/

# 마운트
mount -t mqueue none /dev/mqueue
```

### System V vs POSIX 비교

| 항목      | System V              | POSIX                         |
|-----------|-----------------------|-------------------------------|
| 이름 방식 | 정수 key              | 문자열 (`/name`)              |
| API       | `shmget/shmat`        | `shm_open/mmap`               |
| 잔존 여부 | 프로세스 종료 후 남음 | 프로세스 종료 후 남음         |
| 확인 방법 | `ipcs`                | `ls /dev/shm`                 |
| 삭제 방법 | `ipcrm`               | `shm_unlink` / `rm /dev/shm/` |
| 권장 여부 | 레거시                | 현대적 권장                   |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 소켓

### Unix Domain Socket

같은 호스트 내 프로세스 간 통신입니다. TCP보다 빠르고 파일 권한으로 접근 제어합니다.

```bash
# Unix 소켓 확인
ss -xl
ls -al /var/run/*.sock

# 예시: Docker, MySQL, Nginx
ls -al /var/run/docker.sock
ls -al /var/run/mysqld/mysqld.sock
```

```bash
# socat으로 Unix 소켓 테스트
socat - UNIX-CONNECT:/var/run/docker.sock
```

### Unix vs TCP 소켓 비교

| 항목      | Unix Domain Socket | TCP Socket           |
|-----------|--------------------|----------------------|
| 범위      | 같은 호스트        | 네트워크             |
| 속도      | 빠름 (커널 내부)   | 느림 (네트워크 스택) |
| 주소      | 파일 경로          | IP:Port              |
| 접근 제어 | 파일 권한          | iptables/방화벽      |
| 용도      | DB, Docker, Nginx  | 범용                 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. IPC namespace

IPC namespace는 System V IPC와 POSIX 메시지 큐를 격리합니다.

```bash
# 현재 IPC namespace 확인
ls -al /proc/$$/ns/ipc

# 새 IPC namespace에서 실행
unshare --ipc bash

# 격리 확인 — 호스트에서 만든 공유 메모리가 보이지 않음
ipcs -m   # 비어있음
```

### Docker IPC 옵션

```bash
# 기본: 컨테이너별 독립 IPC namespace
docker run ubuntu ipcs -m   # 비어있음

# 호스트 IPC namespace 공유 (성능 최적화, 보안 주의)
docker run --ipc=host ubuntu ipcs -m   # 호스트 IPC 객체 보임

# 다른 컨테이너와 IPC 공유
docker run --ipc=container:<name> ubuntu
```

⚠️ `--ipc=host`는 컨테이너가 호스트의 공유 메모리에 접근할 수 있어 보안 위험이 있습니다. 성능이 중요한 경우(예: GPU 공유 메모리)에만 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

### 공유 메모리 누수

프로세스가 비정상 종료 시 공유 메모리가 커널에 남습니다.

```bash
# 좀비 IPC 객체 확인 (nattch=0 이면 연결된 프로세스 없음)
ipcs -m | awk 'NR>3 && $6==0 {print $2}'

# 일괄 정리
ipcs -m | awk 'NR>3 && $6==0 {print $2}' | xargs -I{} ipcrm -m {}

# /dev/shm 잔존 파일 확인
ls -alh /dev/shm/
```

### IPC 한도 확인 및 조정

```bash
# 공유 메모리 최대 크기
cat /proc/sys/kernel/shmmax    # 단일 세그먼트 최대 (bytes)
cat /proc/sys/kernel/shmall    # 전체 공유 메모리 최대 (pages)

# 세마포어 한도
cat /proc/sys/kernel/sem
# 250 32000 32 128
# ^   ^     ^  ^
# 최대값 전체수 oops 배열수

# 메시지 큐 한도
cat /proc/sys/kernel/msgmax    # 단일 메시지 최대 크기
cat /proc/sys/kernel/msgmnb    # 큐 최대 크기

# PostgreSQL 등 DB 서버에서 자주 조정
echo "kernel.shmmax=68719476736" >> /etc/sysctl.conf  # 64GB
sysctl -p
```

### strace로 IPC 호출 추적

```bash
strace -e trace=ipc -p <pid>
# shmget, shmat, semop, msgsnd, msgrcv 등 추적
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 비교 및 선택 기준

```
Large data (MB+)
    └── shared memory (shm)  -- fastest

Structured message, async
    └── message queue (mq)

Sync only
    └── semaphore (sem)

Unidirectional stream, parent-child
    └── pipe

Bidirectional, same host
    └── Unix Domain Socket

Network
    └── TCP Socket
```
- Large data: 대용량 데이터 → 공유 메모리
- Structured message: 구조화된 메시지, 비동기 → 메시지 큐
- Sync only: 동기화만 필요 → 세마포어
- Unidirectional: 단방향 스트림, 부모-자식 → 파이프

| 방식         | 지속성           | 커널 잔존 | 네트워크 | 권장          |
|--------------|------------------|-----------|----------|---------------|
| 파이프       | 프로세스 생존 시 | ❌         | ❌        | ✅ 단순 스트림 |
| System V shm | 명시적 삭제 전   | ✅         | ❌        | ⚠️ 레거시     |
| POSIX shm    | 명시적 삭제 전   | ✅         | ❌        | ✅ 현대적      |
| Unix Socket  | 프로세스 생존 시 | ❌         | ❌        | ✅ 범용        |
| TCP Socket   | 프로세스 생존 시 | ❌         | ✅        | ✅ 네트워크    |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux man pages: [man7.org/linux/man-pages](https://man7.org/linux/man-pages/man7/ipc_namespaces.7.html) — ★★★☆☆
- Linux man pages — svipc: [man7.org/linux/man-pages/man7/svipc.7.html](https://man7.org/linux/man-pages/man7/svipc.7.html) — ★★★☆☆
- [namespace.md](namespace.md)
- [strace.md](strace.md)

---

**작성일** : 2026-05-21

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
