# Linux Namespace

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 7가지 Namespace](#2-7가지-namespace) / [3. 시스템 콜](#3-시스템-콜)               |
| [4. /proc/[pid]/ns/](#4-procpidns) / [5. unshare 명령어](#5-unshare-명령어) / [6. 실전 예시](#6-실전-예시) |
| [7. cgroup Namespace](#7-cgroup-namespace) / [8. Tips](#8-tips)                                            |

---

## 1. 개요

Namespace는 커널이 제공하는 프로세스 격리 메커니즘입니다. 각 namespace는 시스템 자원의 독립된 뷰를 제공하여, 프로세스가 자신만의 환경에서 실행되는 것처럼 보이게 합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                        Host Kernel                          │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Container A     │    │  Container B     │              │
│  │  ┌────────────┐  │    │  ┌────────────┐  │              │
│  │  │ PID ns     │  │    │  │ PID ns     │  │              │
│  │  │ NET ns     │  │    │  │ NET ns     │  │              │
│  │  │ MNT ns     │  │    │  │ MNT ns     │  │              │
│  │  │ UTS ns     │  │    │  │ UTS ns     │  │              │
│  │  │ IPC ns     │  │    │  │ IPC ns     │  │              │
│  │  │ USER ns    │  │    │  │ USER ns    │  │              │
│  │  │ CGROUP ns  │  │    │  │ CGROUP ns  │  │              │
│  │  └────────────┘  │    │  └────────────┘  │              │
│  └──────────────────┘    └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

Docker, LXC, Podman 등 컨테이너 런타임은 namespace + cgroup 조합으로 격리를 구현합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 7가지 Namespace

| Namespace | 플래그            | 격리 대상                            | 커널 버전 |
|-----------|-------------------|--------------------------------------|-----------|
| mnt       | `CLONE_NEWNS`     | 마운트 포인트 (파일시스템)           | 2.4.19    |
| pid       | `CLONE_NEWPID`    | 프로세스 ID                          | 2.6.24    |
| net       | `CLONE_NEWNET`    | 네트워크 스택 (인터페이스, 라우팅)   | 2.6.29    |
| uts       | `CLONE_NEWUTS`    | 호스트명, 도메인명                   | 2.6.19    |
| ipc       | `CLONE_NEWIPC`    | IPC (세마포어, 메시지큐, 공유메모리) | 2.6.19    |
| user      | `CLONE_NEWUSER`   | UID/GID 매핑                         | 3.8       |
| cgroup    | `CLONE_NEWCGROUP` | cgroup 루트 디렉토리                 | 4.6       |

### mnt (Mount)

파일시스템 마운트 포인트를 격리합니다. 컨테이너마다 독립된 `/`, `/proc`, `/sys`를 가집니다.

### pid (Process ID)

프로세스 ID 공간을 격리합니다. 컨테이너 안에서 PID 1은 init 프로세스입니다.

```
Host:       PID 1 (systemd) → PID 1234 (containerd) → PID 1235 (container)
Container:  PID 1 (container init) ← PID 1235 on host
```

### net (Network)

네트워크 인터페이스, IP, 라우팅 테이블, iptables를 격리합니다.

```
Host:       eth0 (192.168.1.10)
Container:  eth0 (172.17.0.2) ← connected via veth pair
```

### uts (Unix Time-Sharing)

호스트명을 격리합니다. 컨테이너마다 독립된 hostname을 가집니다.

```bash
# 컨테이너 안에서
hostname    # container-abc123
# 호스트에서
hostname    # myserver
```

### ipc (Inter-Process Communication)

System V IPC, POSIX 메시지큐를 격리합니다. 컨테이너 간 IPC 통신을 차단합니다.

### user (User ID)

UID/GID 매핑을 격리합니다. 컨테이너 안의 root(UID 0)를 호스트의 비특권 사용자로 매핑할 수 있습니다.

```
Container:  root (UID 0)  →  Host: nobody (UID 65534)
```

### cgroup

cgroup 루트 디렉토리를 격리합니다. 컨테이너가 자신의 cgroup 트리만 볼 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 시스템 콜

| 시스템 콜   | 역할                                              |
|-------------|---------------------------------------------------|
| `clone()`   | 새 프로세스 생성 + 지정한 namespace 격리          |
| `unshare()` | 현재 프로세스를 새 namespace로 이동               |
| `setns()`   | 기존 namespace에 합류 (다른 프로세스의 ns에 진입) |

### clone()

`fork()`의 확장판입니다. namespace 플래그를 지정하여 격리된 자식 프로세스를 생성합니다.

```c
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

static int child_fn(void *arg) {
    printf("Child PID (inside ns): %d\n", getpid());  // PID 1
    return 0;
}

int main() {
    char stack[1024 * 1024];
    int flags = CLONE_NEWPID | CLONE_NEWUTS | SIGCHLD;

    pid_t pid = clone(child_fn, stack + sizeof(stack), flags, NULL);
    printf("Child PID (outside ns): %d\n", pid);  // 실제 PID
    waitpid(pid, NULL, 0);
    return 0;
}
```

### unshare()

현재 프로세스를 새 namespace로 분리합니다.

```c
#define _GNU_SOURCE
#include <sched.h>

// 현재 프로세스의 네트워크 namespace 분리
unshare(CLONE_NEWNET);
```

### setns()

`/proc/[pid]/ns/` 파일 디스크립터를 통해 기존 namespace에 합류합니다.

```c
#include <fcntl.h>
#include <sched.h>

int fd = open("/proc/1234/ns/net", O_RDONLY);
setns(fd, CLONE_NEWNET);  // PID 1234의 네트워크 namespace에 합류
close(fd);
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. /proc/[pid]/ns/

각 프로세스의 namespace 정보는 `/proc/[pid]/ns/`에서 확인할 수 있습니다.

```bash
ls -la /proc/$$/ns/
```

```
lrwxrwxrwx 1 root root 0 ... cgroup -> 'cgroup:[4026531835]'
lrwxrwxrwx 1 root root 0 ... ipc -> 'ipc:[4026531839]'
lrwxrwxrwx 1 root root 0 ... mnt -> 'mnt:[4026531841]'
lrwxrwxrwx 1 root root 0 ... net -> 'net:[4026531840]'
lrwxrwxrwx 1 root root 0 ... pid -> 'pid:[4026531836]'
lrwxrwxrwx 1 root root 0 ... user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 ... uts -> 'uts:[4026531838]'
```

- 숫자(inode)가 같으면 같은 namespace를 공유합니다.
- 숫자가 다르면 격리된 namespace입니다.

```bash
# 호스트와 컨테이너의 namespace 비교
sudo ls -la /proc/1/ns/pid          # 호스트 init
sudo docker inspect --format '{{.State.Pid}}' rocky9
sudo ls -la /proc/<container_pid>/ns/pid  # 컨테이너
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. unshare 명령어

`unshare(2)` 시스템 콜의 CLI 래퍼입니다. 새 namespace에서 명령어를 실행합니다.

```bash
# 새 UTS namespace에서 hostname 변경
sudo unshare --uts bash
hostname test-container
hostname   # test-container
exit
hostname   # 원래 호스트명 유지

# 새 PID namespace에서 실행
sudo unshare --pid --fork --mount-proc bash
ps aux     # PID 1 = bash (격리된 PID 공간)
exit

# 새 네트워크 namespace
sudo unshare --net bash
ip addr    # lo만 존재 (격리된 네트워크)
exit
```

| 옵션             | namespace                      |
|------------------|--------------------------------|
| `--mount`, `-m`  | mnt                            |
| `--pid`, `-p`    | pid                            |
| `--net`, `-n`    | net                            |
| `--uts`, `-u`    | uts                            |
| `--ipc`, `-i`    | ipc                            |
| `--user`, `-U`   | user                           |
| `--cgroup`, `-C` | cgroup                         |
| `--fork`, `-f`   | fork 후 실행 (pid ns에 필수)   |
| `--mount-proc`   | /proc 재마운트 (pid ns에 필수) |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실전 예시

### Docker 컨테이너 namespace 확인

```bash
# 컨테이너 PID 확인
CPID=$(sudo docker inspect --format '{{.State.Pid}}' rocky9)

# 호스트 vs 컨테이너 namespace 비교
sudo ls -la /proc/1/ns/ | awk '{print $NF}'
sudo ls -la /proc/$CPID/ns/ | awk '{print $NF}'
```

### nsenter — 컨테이너 namespace에 진입

```bash
# 컨테이너의 모든 namespace에 진입
sudo nsenter -t $CPID -m -u -i -n -p -- bash

# 네트워크 namespace만 진입 (네트워크 디버깅)
sudo nsenter -t $CPID -n -- ip addr
sudo nsenter -t $CPID -n -- ss -tlnp
```

### ip netns — 네트워크 namespace 관리

```bash
# 네트워크 namespace 생성
sudo ip netns add test_ns

# namespace 안에서 명령 실행
sudo ip netns exec test_ns ip addr
sudo ip netns exec test_ns ping 127.0.0.1

# veth pair로 호스트와 연결
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth1 netns test_ns
sudo ip addr add 10.0.0.1/24 dev veth0
sudo ip netns exec test_ns ip addr add 10.0.0.2/24 dev veth1
sudo ip link set veth0 up
sudo ip netns exec test_ns ip link set veth1 up

# 통신 확인
sudo ip netns exec test_ns ping 10.0.0.1

# 정리
sudo ip netns del test_ns
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. cgroup Namespace

cgroup namespace는 프로세스가 볼 수 있는 cgroup 트리의 루트를 격리합니다.

```
Host cgroup tree:
/sys/fs/cgroup/
└── system.slice/
    └── docker-abc123.scope/   ← 컨테이너의 실제 위치
        ├── memory.max
        └── cpu.max

Container view (cgroup ns 격리 시):
/sys/fs/cgroup/                ← 컨테이너는 여기가 루트로 보임
├── memory.max
└── cpu.max
```

### cgroupns host vs private

| 모드      | 동작                                      | 용도                 |
|-----------|-------------------------------------------|----------------------|
| `host`    | 호스트의 cgroup 트리 전체가 보임          | systemd 컨테이너     |
| `private` | 자신의 cgroup 경로가 루트로 보임 (기본값) | 일반 컨테이너 (보안) |

```bash
# host 모드 (systemd 실행 필요 시)
docker run --cgroupns host --privileged ...

# private 모드 (기본값, 격리)
docker run --cgroupns private ...
```

⚠️ Docker Compose v5.x에서 `cgroupns_mode` 키가 제거되었습니다. `daemon.json`으로 기본값을 설정합니다. 상세 내용은 [docker.md 섹션 11](../12_tech_stack/docker.md#11-cgroup-namespace)을 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Tips

```bash
# 현재 프로세스의 모든 namespace 확인
ls -la /proc/$$/ns/

# 시스템 전체 namespace 목록
lsns

# 특정 타입만 확인
lsns -t pid
lsns -t net

# 컨테이너가 사용하는 namespace 수 확인
sudo find /proc/*/ns -name 'pid' 2>/dev/null | wc -l
```

⚠️ user namespace를 활성화하면 비특권 사용자도 다른 namespace를 생성할 수 있습니다. 보안 정책에 따라 `kernel.unprivileged_userns_clone=0`으로 제한할 수 있습니다.

```bash
# user namespace 비활성화 (보안 강화)
sudo sysctl -w kernel.unprivileged_userns_clone=0

# 영구 적용
echo "kernel.unprivileged_userns_clone=0" | sudo tee /etc/sysctl.d/99-userns.conf
sudo sysctl --system
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux man page namespaces(7): [man7.org/linux/man-pages/man7/namespaces.7.html](https://man7.org/linux/man-pages/man7/namespaces.7.html) — ★★★★☆
- Linux man page unshare(1): [man7.org/linux/man-pages/man1/unshare.1.html](https://man7.org/linux/man-pages/man1/unshare.1.html) — ★★★☆☆
- LWN.net Namespaces series: [lwn.net/Articles/531114](https://lwn.net/Articles/531114/) — ★★★★☆
- [cgroup.md](./cgroup.md)
- [process_lifecycle.md](./process_lifecycle.md)
- [docker.md 섹션 11](../12_tech_stack/docker.md#11-cgroup-namespace)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-15

**마지막 업데이트**: 2026-05-15

© 2026 siasia86. Licensed under CC BY 4.0.
