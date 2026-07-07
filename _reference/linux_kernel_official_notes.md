---
name: linux-kernel-official-notes
description: Linux Kernel 내부 (namespace, cgroup, scheduler, netfilter, capabilities) 문서 작성 시 참조할 공식 소스. 02_basic_linux/, 03_advanced_linux/ 문서 생성/검토 시 참조.
tags:
  - kernel
  - namespace
  - cgroup
  - scheduler
  - netfilter
  - capabilities
  - reference
last_checked: 2026-07-03
sources:
  - https://man7.org/linux/man-pages/man7/namespaces.7.html
  - https://man7.org/linux/man-pages/man2/clone.2.html
  - https://man7.org/linux/man-pages/man7/capabilities.7.html
  - https://docs.kernel.org/admin-guide/cgroup-v2.html
  - https://docs.kernel.org/scheduler/sched-design-CFS.html
  - https://kernelnewbies.org/LinuxVersions
  - https://man7.org/linux/man-pages/man8/iptables.8.html
  - https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
---

# Linux Kernel 공식 참조 노트

## 1. Namespace

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| namespaces.7 | https://man7.org/linux/man-pages/man7/namespaces.7.html | 8가지 namespace 목록, 커널 버전 |
| clone.2 | https://man7.org/linux/man-pages/man2/clone.2.html | CLONE_NEW* 플래그, since 버전 |
| unshare.2 | https://man7.org/linux/man-pages/man2/unshare.2.html | unshare 시스템 콜 |

### 검증된 사실 (2026-07-03)

| Namespace | 플래그 | since | 출처 |
|-----------|--------|-------|------|
| mnt | CLONE_NEWNS | 2.4.19 | clone.2 |
| uts | CLONE_NEWUTS | 2.6.19 | clone.2 |
| ipc | CLONE_NEWIPC | 2.6.19 | clone.2 |
| pid | CLONE_NEWPID | 2.6.24 | clone.2 |
| net | CLONE_NEWNET | 2.6.24 (기능 완성 2.6.29) | clone.2 + namespaces.7 |
| user | CLONE_NEWUSER | 3.8 | clone.2 |
| cgroup | CLONE_NEWCGROUP | 4.6 | clone.2 |
| time | CLONE_NEWTIME | 5.6 | namespaces.7 |

## 2. cgroup v2

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| cgroup-v2 docs | https://docs.kernel.org/admin-guide/cgroup-v2.html | 컨트롤러, 인터페이스 파일 |

### 검증된 사실 (2026-07-03)

| 항목 | 값 | 출처 |
|------|------|------|
| cpu.max 형식 | "$MAX $PERIOD" (마이크로초) | docs.kernel.org/cgroup-v2 |
| cpu.max 기본값 | "max 100000" | docs.kernel.org/cgroup-v2 |
| cpu.max 위치 | non-root cgroup에만 존재 | docs.kernel.org/cgroup-v2 |
| v2 기본 OS | Ubuntu 22.04+, RHEL 9+, Rocky 9+ | 각 배포판 릴리즈 노트 |

## 3. Scheduler

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| CFS design | https://docs.kernel.org/scheduler/sched-design-CFS.html | CFS 아키텍처 |
| kernel source | kernel/sched/fair.c (v6.5) | sysctl 기본값 |
| kernelnewbies 6.6 | https://kernelnewbies.org/Linux_6.6 | EEVDF 교체 |

### 검증된 사실 (2026-07-03)

| 항목 | 값 | 출처 |
|------|------|------|
| sysctl_sched_latency | 6000000 (6ms) | kernel/sched/fair.c v6.5 |
| sysctl_sched_min_granularity | 750000 (0.75ms) | kernel/sched/fair.c v6.5 |
| EEVDF 도입 | Linux 6.6 (2023-10) | kernelnewbies.org |
| EEVDF 풀네임 | Earliest Eligible Virtual Deadline First | kernelnewbies.org |

## 4. netfilter

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| iptables.8 | https://man7.org/linux/man-pages/man8/iptables.8.html | 테이블, 체인 |
| netfilter.org | https://www.netfilter.org/ | nftables, conntrack |

### 검증된 사실 (2026-07-03)

| 테이블 | 체인 | 출처 |
|--------|------|------|
| filter | INPUT, FORWARD, OUTPUT | iptables.8 man page |
| nat | PREROUTING, INPUT, OUTPUT, POSTROUTING | iptables.8 man page |
| mangle | 모든 체인 | iptables.8 man page |
| raw | PREROUTING, OUTPUT | iptables.8 man page |

### Cilium과 netfilter

- Cilium은 eBPF/XDP 기반으로 netfilter를 **bypass** 합니다
- 출처: Wikipedia eBPF ("bypassing it"), GitHub description ("eBPF-based Networking")
- iptables/nftables는 netfilter 위에서 동작합니다

## 5. Capabilities

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| capabilities.7 | https://man7.org/linux/man-pages/man7/capabilities.7.html | capability 목록, 설명 |

### 검증된 사실 (2026-07-03)

| Capability | 설명 | 출처 |
|------------|------|------|
| CAP_NET_BIND_SERVICE | 1024 미만 포트 바인딩 | capabilities.7 |
| CAP_NET_ADMIN | 네트워크 설정 변경 | capabilities.7 |
| CAP_SYS_ADMIN | 시스템 관리 (마운트 등) | capabilities.7 |
| CAP_SYS_PTRACE | 프로세스 추적 | capabilities.7 |

## 6. Bash

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| bash.1 | https://man7.org/linux/man-pages/man1/bash.1.html | 문법, 변수, 내장 명령 |
| stdin.3 | https://man7.org/linux/man-pages/man3/stdin.3.html | FD 0/1/2 |

### 검증된 사실 (2026-07-03)

| 항목 | 값 | 출처 |
|------|------|------|
| FD 0 | stdin | stdin.3 |
| FD 1 | stdout | stdin.3 |
| FD 2 | stderr | stdin.3 |
| $- | current set of options | bash.1 |
| $((expr)) | arithmetic expansion | bash.1 |
| trap 의사시그널 | EXIT, ERR, DEBUG, RETURN | bash.1 |
| $- 플래그 h | hashall | bash.1 |
| $- 플래그 i | interactive | bash.1 |
| $- 플래그 m | monitor (job control) | bash.1 |
| $- 플래그 B | braceexpand | bash.1 |
| $- 플래그 H | histexpand | bash.1 |

## 7. 배포판 EOL

### 공식 소스

| 소스 | URL | 용도 |
|------|-----|------|
| endoflife.date API | https://endoflife.date/api/{product}.json | EOL 날짜 |

### 검증된 사실 (2026-07-03)

| 배포판 | EOL | 출처 |
|--------|-----|------|
| CentOS 5 | 2017-03-31 | endoflife.date API |
| CentOS 7 | 2024-06-30 | endoflife.date API |
