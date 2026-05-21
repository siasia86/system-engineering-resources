# Process Lifecycle — fork / exec / wait / exit

## 목차

| 섹션                                                                                        |
|---------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. fork()](#2-fork) / [3. exec()](#3-exec)                            |
| [4. wait()](#4-wait) / [5. exit()](#5-exit) / [6. 전체 흐름](#6-전체-흐름)                  |
| [7. Zombie & Orphan](#7-zombie--orphan) / [8. 실전 예시](#8-실전-예시) / [9. Tips](#9-tips) |

---

## 1. 개요

Linux에서 모든 프로세스는 `fork()` → `exec()` → `exit()` 사이클로 생성되고 종료됩니다. 커널은 이 과정을 시스템 콜로 제공합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                  Process Lifecycle                           │
│                                                              │
│  fork()  →  exec()  →  running  →  exit()                    │
│    │                                    │                    │
│  create child                        wait() (parent)         │
└──────────────────────────────────────────────────────────────┘
```

| 시스템 콜 | 역할                                          |
|-----------|-----------------------------------------------|
| `fork()`  | 현재 프로세스를 복제하여 자식 프로세스 생성   |
| `exec()`  | 자식 프로세스의 메모리를 새 프로그램으로 교체 |
| `wait()`  | 부모가 자식 종료를 기다림                     |
| `exit()`  | 프로세스 종료 및 자원 반환                    |

[⬆ 목차로 돌아가기](#목차)

---

## 2. fork()

### 동작 원리

```
┌──────────────────────────┐
│  Parent  │  PID: 1000
└──────────────────────────┘
     │ fork()
     v
┌──────────────────────────┐
│  Parent  │    │  Child   │  PID: 1001
│ PID:1000 │    │ PID:1001 │  (copy of parent)
│ ret: 1001│    │ ret: 0   │
└──────────────────────────┘
```

- 부모: `fork()` 반환값 = 자식 PID (양수)
- 자식: `fork()` 반환값 = 0
- 실패: `fork()` 반환값 = -1

### Copy-on-Write (COW)

fork 직후 부모/자식은 메모리를 공유합니다. 실제 쓰기가 발생할 때만 복사합니다.

```
after fork():
  Parent ──┐
           ├── shared memory pages (read-only)
  Child  ──┘

on write:
  Parent ── own copy (writable)
  Child  ── own copy (writable)
```

### C 코드 예시

```c
#include <stdio.h>
#include <unistd.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return 1;
    } else if (pid == 0) {
        // child process
        printf("Child: PID=%d, Parent PID=%d\n", getpid(), getppid());
    } else {
        // parent process
        printf("Parent: PID=%d, Child PID=%d\n", getpid(), pid);
    }
    return 0;
}
```

```bash
gcc -o fork_example fork_example.c
./fork_example
# Parent: PID=1000, Child PID=1001
# Child: PID=1001, Parent PID=1000
```

### Shell에서 확인

```bash
# bash가 명령어 실행 시 fork + exec 사용
bash -c 'echo "parent: $$"'

# pstree로 fork 결과 확인
pstree -p $$
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. exec()

fork로 생성된 자식 프로세스의 메모리를 새 프로그램으로 교체합니다. PID는 유지됩니다.

```
Child (PID:1001, copy of bash)
    │ exec("nginx")
    v
nginx (PID:1001)  <- same PID, different program
```

### exec 계열 함수

| 함수       | 설명                           |
|------------|--------------------------------|
| `execl()`  | 인자를 가변 인수로 전달        |
| `execv()`  | 인자를 배열로 전달             |
| `execle()` | 환경변수 포함                  |
| `execve()` | 커널 시스템 콜 (나머지는 래퍼) |
| `execlp()` | PATH 환경변수로 실행 파일 탐색 |

### C 코드 예시

```c
#include <stdio.h>
#include <unistd.h>

int main() {
    pid_t pid = fork();

    if (pid == 0) {
        // 자식: ls -la 실행
        execlp("ls", "ls", "-la", NULL);
        perror("exec failed");  // exec 성공 시 이 줄은 실행 안 됨
    } else {
        wait(NULL);  // 자식 wait for exit
    }
    return 0;
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. wait()

부모 프로세스가 자식 종료를 기다립니다. 자식이 종료되면 종료 상태를 수집합니다.

```c
#include <sys/wait.h>

pid_t pid = fork();
if (pid == 0) {
    // 자식 작업
    exit(0);
} else {
    int status;
    waitpid(pid, &status, 0);  // 특정 자식 대기

    if (WIFEXITED(status)) {
        printf("Child exited with: %d\n", WEXITSTATUS(status));
    }
}
```

| 함수                  | 설명                     |
|-----------------------|--------------------------|
| `wait()`              | 임의의 자식 종료 대기    |
| `waitpid(pid, ...)`   | 특정 자식 종료 대기      |
| `WIFEXITED(status)`   | 정상 종료 여부 확인      |
| `WEXITSTATUS(status)` | 종료 코드 추출           |
| `WIFSIGNALED(status)` | 시그널로 종료됐는지 확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. exit()

프로세스를 종료하고 자원을 반환합니다.

```c
#include <stdlib.h>

exit(0);   // 정상 종료 (0)
exit(1);   // 오류 종료 (1 이상)
```

| 종료 방식 | 설명                                  |
|-----------|---------------------------------------|
| `exit(0)` | 정상 종료. 부모에게 0 전달            |
| `exit(1)` | 오류 종료. 부모에게 1 전달            |
| `_exit()` | stdio 버퍼 flush 없이 즉시 종료       |
| 시그널    | `SIGKILL`, `SIGTERM` 등으로 강제 종료 |

```bash
# 종료 코드 확인
./program
echo $?   # 0 = 성공, 1 이상 = 오류
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 전체 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                   fork + exec + wait                        │
│                                                             │
│  Parent (bash, PID:1000)                                    │
│      │                                                      │
│      │ fork()                                               │
│      ├──────────────────────────────────┐                   │
│      │                                  │                   │
│      │ wait()                    Child (PID:1001)           │
│      │ (blocking)                    │                      │
│      │                           exec("ls")                 │
│      │                               │                      │
│      │                           ls running                 │
│      │                               │                      │
│      │                           exit(0)                    │
│      │                               │                      │
│      │<──────────── SIGCHLD ─────────┘                      │
│      │                                                      │
│      │ wait() returns (collect exit code)                   │
│      │                                                      │
│  Parent continues                                           │
└─────────────────────────────────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Zombie & Orphan

### Zombie 프로세스

자식이 종료됐지만 부모가 `wait()`를 호출하지 않은 상태입니다. 프로세스 테이블에 항목이 남아있습니다.

```bash
# Zombie 확인
ps aux | grep Z
# Z 상태 = Zombie

# 프로세스 테이블 확인
ps -eo pid,ppid,stat,comm | grep Z
```

```
┌──────────┐         ┌──────────┐
│  Parent  │         │  Child   │ ← exit() complete
│ (running)│         │ (Zombie) │   wait() not called
└──────────┘         └──────────┘
                     PID entry remains
```

**해결:** 부모가 `wait()`를 호출하거나, 부모를 종료하면 init(PID 1)이 자동으로 수거합니다.

### Orphan 프로세스

부모가 먼저 종료된 자식 프로세스입니다. init(PID 1) 또는 subreaper가 새 부모가 됩니다.

```bash
# Orphan 확인 (PPID가 1인 프로세스)
ps -eo pid,ppid,comm | awk '$2 == 1'
```

| 상태   | 원인                 | 결과                      |
|--------|----------------------|---------------------------|
| Zombie | 부모가 wait() 미호출 | 프로세스 테이블 항목 잔류 |
| Orphan | 부모 먼저 종료       | init이 새 부모로 입양     |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실전 예시

### Apache MPM과 fork

```
httpd master (PID:1000)
    │ fork() × N
    ├── httpd worker (PID:1001)  <- prefork: handles 1 request
    ├── httpd worker (PID:1002)
    └── httpd worker (PID:1003)
```

```bash
# Apache worker 프로세스 확인
ps aux | grep apache2
pstree -p $(pgrep -o apache2)
```

### Shell 명령어 실행

```bash
# bash가 ls를 실행하는 과정
# 1. bash가 fork() → 자식 bash 생성
# 2. 자식 bash가 exec("ls") → ls로 교체
# 3. ls 실행 후 exit()
# 4. 부모 bash가 wait()로 종료 코드 수집
ls -la
echo "exit code: $?"
```

### 백그라운드 실행

```bash
# & = 부모가 wait() 없이 계속 실행
sleep 10 &
echo "PID: $!"   # 자식 PID

# 명시적 wait
wait $!
echo "sleep 완료"
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Tips

```bash
# 현재 프로세스 PID
echo $$

# parent process PID
echo $PPID

# 마지막 백그라운드 자식 PID
echo $!

# 마지막 명령어 종료 코드
echo $?

# 프로세스 트리 확인
pstree -p $$

# fork bomb 방지 (최대 프로세스 수 제한)
ulimit -u 1000
```

⚠️ fork bomb: `:(){ :|:& };:` — 재귀적으로 fork를 반복하여 시스템 자원을 고갈시킵니다. `ulimit -u`로 방지합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- TheLinuxCode: [thelinuxcode.com/fork-system-call-linux](https://thelinuxcode.com/fork-system-call-linux/) — ★★☆☆☆
- Linux man page fork(2): [man7.org/linux/man-pages/man2/fork.2.html](https://man7.org/linux/man-pages/man2/fork.2.html) — ★★★★☆
- Linux man page exec(3): [man7.org/linux/man-pages/man3/exec.3.html](https://man7.org/linux/man-pages/man3/exec.3.html) — ★★★★☆
- [apache_install.md](../01_install/apache_install.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일** : 2026-05-15

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
