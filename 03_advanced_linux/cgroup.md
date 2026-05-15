# cgroup

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. v1 vs v2](#3-v1-vs-v2) |
| [4. 주요 컨트롤러](#4-주요-컨트롤러) / [5. 실습](#5-실습) / [6. Docker와 cgroup](#6-docker와-cgroup) |
| [7. systemd와 cgroup](#7-systemd와-cgroup) / [8. 트러블슈팅](#8-트러블슈팅) / [9. Tips](#9-tips) |
| [10. cgroup 파일시스템](#10-cgroup-파일시스템) |
---

## 1. 개요

cgroup(Control Groups)은 Linux 커널이 프로세스 그룹별로 리소스를 제한·격리·계측하는 기능입니다. Docker, Kubernetes, systemd 모두 cgroup을 기반으로 동작합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    cgroup role                              │
│                                                             │
│  Process Group A  →  CPU 50% / Memory 1GB / IO 100MB/s      │
│  Process Group B  →  CPU 20% / Memory 512MB                 │
│  Process Group C  →  no limit                               │
└─────────────────────────────────────────────────────────────┘
```

**3가지 핵심 기능:**

| 기능 | 설명 |
|------|------|
| 제한 (Limiting) | CPU, 메모리, I/O 사용량 상한 설정 |
| 우선순위 (Prioritization) | 그룹 간 리소스 배분 비율 설정 |
| 계측 (Accounting) | 그룹별 리소스 사용량 측정 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                   cgroup v2 hierarchy                       │
│                                                             │
│  /sys/fs/cgroup/          (root cgroup)                     │
│  ├── system.slice/        (systemd services)                │
│  │   ├── nginx.service/                                     │
│  │   └── mysql.service/                                     │
│  ├── user.slice/          (user sessions)                   │
│  │   └── user-1000.slice/                                   │
│  └── docker/              (containers)                      │
│      ├── <container_id>/                                    │
│      └── <container_id>/                                    │
└─────────────────────────────────────────────────────────────┘
```

각 디렉토리 안에 컨트롤 파일이 있습니다:

```
/sys/fs/cgroup/system.slice/cron.service/
├── cgroup.procs          # 소속 PID 목록
├── cgroup.controllers    # 사용 가능한 컨트롤러
├── cpu.max               # CPU 상한 (quota period)
├── cpu.weight            # CPU 가중치
├── cpu.stat              # CPU 사용 통계
├── memory.max            # 메모리 상한
├── memory.current        # 현재 메모리 사용량
├── memory.high           # 소프트 상한 (초과 시 throttle)
├── io.max                # I/O 속도 상한
├── pids.max              # 최대 프로세스 수
└── pids.current          # 현재 프로세스 수
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. v1 vs v2

| 항목 | v1 | v2 |
|------|----|----|
| 구조 | 컨트롤러별 별도 트리 | 단일 통합 트리 |
| 경로 | `/sys/fs/cgroup/cpu/`, `/sys/fs/cgroup/memory/` | `/sys/fs/cgroup/` |
| 프로세스 소속 | 컨트롤러마다 다른 그룹 가능 | 하나의 그룹에만 소속 |
| 기본 OS | CentOS 7, Ubuntu 18.04 | Ubuntu 22.04+, Rocky 9+, RHEL 9+ |
| 권장 | 레거시 | 현재 표준 |

### 현재 버전 확인

```bash
# v2 사용 중이면 cgroup2fs 출력
stat -fc %T /sys/fs/cgroup/
# cgroup2fs → v2
# cgroup    → v1 (hybrid 포함)

# 또는
mount | grep cgroup
```

### v1 경로 예시

```
/sys/fs/cgroup/
├── cpu/
├── memory/
├── blkio/
└── pids/
```

### v2 경로 예시

```
/sys/fs/cgroup/                          (root cgroup)
├── cgroup.controllers                   # cpuset cpu io memory hugetlb pids rdma misc
├── cgroup.procs                         # root 소속 PID
├── cgroup.subtree_control               # 하위에 위임할 컨트롤러
├── cgroup.stat                          # cgroup 통계
├── cpu.stat                             # CPU 통계 (root에도 존재)
├── cpu.pressure                         # CPU pressure stall info
├── memory.stat                          # 메모리 통계 (root에도 존재)
├── memory.pressure                      # 메모리 pressure stall info
├── io.stat                              # I/O 통계 (root에도 존재)
├── io.pressure                          # I/O pressure stall info
├── system.slice/                        # systemd 서비스 그룹
│   ├── memory.max                       # ← 하위부터 제한 파일 존재
│   ├── cpu.max
│   └── cron.service/                    # 개별 서비스
│       ├── memory.max
│       ├── cpu.max
│       └── pids.max
└── user.slice/                          # 사용자 세션 그룹
    └── user-1000.slice/                 # UID 1000 사용자
```

⚠️ root cgroup에는 `memory.max`, `cpu.max`, `pids.max` 등 **제한 설정 파일이 없습니다**. 통계/pressure 파일만 존재합니다. 제한은 하위 cgroup(`system.slice/`, `user.slice/` 이하)에서만 설정 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 컨트롤러

### cpu

```bash
# CPU 사용량 제한 (v2)
# 형식: quota period (마이크로초)
# 50% 제한: 50000 100000
echo "50000 100000" > /sys/fs/cgroup/mygroup/cpu.max

# CPU 가중치 (기본값 100, 범위 1~10000)
echo 200 > /sys/fs/cgroup/mygroup/cpu.weight

# 현재 CPU 사용 통계
cat /sys/fs/cgroup/mygroup/cpu.stat
```

### memory

```bash
# 메모리 상한 설정 (512MB)
echo $((512 * 1024 * 1024)) > /sys/fs/cgroup/mygroup/memory.max

# 현재 사용량 확인
cat /sys/fs/cgroup/mygroup/memory.current

# OOM 발생 시 kill 대신 throttle (swap 사용)
echo $((1024 * 1024 * 1024)) > /sys/fs/cgroup/mygroup/memory.swap.max

# 메모리 통계
cat /sys/fs/cgroup/mygroup/memory.stat
```

### io (blkio)

```bash
# 디바이스 번호 확인
ls -la /dev/sda  # 8:0

# 읽기/쓰기 속도 제한 (100MB/s)
echo "8:0 rbps=104857600 wbps=104857600" > /sys/fs/cgroup/mygroup/io.max

# I/O 통계
cat /sys/fs/cgroup/mygroup/io.stat
```

### pids

```bash
# 최대 프로세스 수 제한
echo 100 > /sys/fs/cgroup/mygroup/pids.max

# 현재 프로세스 수
cat /sys/fs/cgroup/mygroup/pids.current
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실습

### cgroup 수동 생성 (v2)

cgroup = 디렉토리입니다. 디렉토리를 만들면 cgroup이 생성되고, 파일에 값을 쓰면 제한이 설정됩니다.

```
mkdir (cgroup 생성)
    │
    v
subtree_control (컨트롤러 위임 — 이게 없으면 memory.max 파일이 안 나타남)
    │
    v
echo 값 > memory.max (제한 설정)
    │
    v
echo PID > cgroup.procs (프로세스 배치 — 이 순간부터 제한 적용)
    │
    v
echo PID > 상위/cgroup.procs (프로세스 이동)
    │
    v
rmdir (cgroup 삭제)
```

#### 1단계: cgroup 생성 (디렉토리 생성)

```bash
sudo mkdir /sys/fs/cgroup/mytest

# 커널이 자동으로 컨트롤 파일 생성
ls /sys/fs/cgroup/mytest/
# cgroup.procs  cgroup.controllers  ...
```

#### 2단계: 컨트롤러 위임 (가장 중요)

root cgroup이 하위에 어떤 컨트롤러를 허용할지 결정합니다. 이 설정이 없으면 `memory.max` 파일이 나타나지 않습니다.

```bash
# 현재 위임 상태 확인
cat /sys/fs/cgroup/cgroup.subtree_control
# cpu io memory pids  ← 이것들만 하위에서 사용 가능

# memory가 없으면 추가
echo "+memory +cpu +pids" | sudo tee /sys/fs/cgroup/cgroup.subtree_control

# 이제 mytest에 memory.max가 나타남
ls /sys/fs/cgroup/mytest/ | grep memory
# memory.current  memory.max  memory.high  ...
```

#### 3단계: 제한 설정

```bash
# 메모리 100MB 제한
echo $((100 * 1024 * 1024)) | sudo tee /sys/fs/cgroup/mytest/memory.max
# 104857600

# 확인
cat /sys/fs/cgroup/mytest/memory.max
# 104857600
```

#### 4단계: 프로세스를 cgroup에 배치

```bash
# 현재 쉘의 PID를 mytest cgroup에 넣기
echo $$ | sudo tee /sys/fs/cgroup/mytest/cgroup.procs

# 확인 — 이 쉘은 이제 메모리 100MB 제한을 받음
cat /proc/$$/cgroup
# 0::/mytest
```

#### 5단계: 테스트

```bash
# 50MB 할당 → 성공
python3 -c "x = bytearray(50 * 1024 * 1024); print('50MB OK')"

# 150MB 할당 → OOM kill (제한 초과)
python3 -c "x = bytearray(150 * 1024 * 1024); print('150MB OK')"
# Killed
```

#### 6단계: 정리

```bash
# 프로세스를 root cgroup으로 되돌리기 (안 하면 rmdir 실패)
echo $$ | sudo tee /sys/fs/cgroup/cgroup.procs

# cgroup 삭제
sudo rmdir /sys/fs/cgroup/mytest
```

⚠️ `rmdir`은 cgroup 안에 프로세스가 남아있으면 실패합니다. 반드시 프로세스를 먼저 이동시킵니다.

### systemd-run으로 간편 실행 (v2 권장)

수동 생성 대신 `systemd-run`을 사용하면 cgroup 생성/삭제를 자동으로 처리합니다.

```bash
# 메모리 256MB, CPU 50% 제한으로 stress 실행
sudo systemd-run --scope -p MemoryMax=256M -p CPUQuota=50% stress --cpu 4

# 종료 시 cgroup 자동 삭제
```

### cgexec (v1 전용)

```bash
# cgexec는 cgroupv1 전용 도구 — v2 환경에서는 동작하지 않음
sudo apt install cgroup-tools
sudo cgexec -g cpu,memory:mytest stress --cpu 4 --vm 1 --vm-bytes 512M
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Docker와 cgroup

Docker는 컨테이너마다 cgroup을 자동 생성합니다.

```bash
# 컨테이너 메모리 512MB 제한
docker run -m 512m nginx

# CPU 1코어 제한
docker run --cpus=1 nginx

# 실제 cgroup 경로 확인
docker inspect <container_id> | grep -i cgroup
ls /sys/fs/cgroup/system.slice/docker-<container_id>.scope/
```

### cgroupv2 환경에서 systemd 컨테이너 실행

Ubuntu 22.04+, Rocky 9+ 등 cgroupv2 기본 환경에서 systemd 컨테이너가 실패하는 경우:

```yaml
# docker-compose.yml
services:
  ubuntu22:
    image: geerlingguy/docker-ubuntu2204-ansible
    privileged: true
    command: /lib/systemd/systemd
    cgroupns_mode: host                        # cgroup 네임스페이스 호스트 공유
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw       # cgroup 파일시스템 마운트
```

| 옵션 | 설명 |
|------|------|
| `privileged: true` | 모든 Linux capability 부여 |
| `cgroupns_mode: host` | 호스트 cgroup 네임스페이스 사용 |
| `/sys/fs/cgroup` 마운트 | systemd가 cgroup 직접 접근 가능 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. systemd와 cgroup

systemd는 서비스별로 cgroup을 자동 관리합니다.

```bash
# 서비스별 리소스 사용량 확인
systemd-cgtop

# 특정 서비스 cgroup 경로
systemctl status nginx | grep CGroup

# 서비스 메모리 제한 설정
sudo systemctl edit nginx
```

```ini
# /etc/systemd/system/nginx.service.d/override.conf
[Service]
MemoryMax=512M
CPUQuota=50%
TasksMax=100
```

```bash
# 적용
sudo systemctl daemon-reload
sudo systemctl restart nginx

# 확인
systemctl show nginx | grep -E "Memory|CPU|Tasks"
```

### 주요 systemd 리소스 지시어

| 지시어 | 설명 | 예시 |
|--------|------|------|
| `MemoryMax` | 메모리 상한 | `512M` |
| `MemoryHigh` | 소프트 상한 (초과 시 throttle) | `400M` |
| `CPUQuota` | CPU 사용률 상한 | `50%` |
| `CPUWeight` | CPU 우선순위 가중치 | `200` |
| `IOWeight` | I/O 우선순위 | `100` |
| `TasksMax` | 최대 프로세스/스레드 수 | `100` |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

### OOM Killer 발생 확인

```bash
# 커널 로그에서 OOM 확인
dmesg | grep -i "oom\|killed"
journalctl -k | grep -i oom

# 어떤 프로세스가 kill됐는지
dmesg | grep "Out of memory"
```

### 컨테이너가 즉시 종료되는 경우

```bash
# 종료 코드 확인
docker inspect <container_id> | grep ExitCode

# 255: systemd 실패 (cgroupv2 환경)
# 137: OOM kill (메모리 부족)
# 1:   일반 오류

# cgroupv2 여부 확인
stat -fc %T /sys/fs/cgroup/
```

### 메모리 제한 초과 확인

```bash
# 컨테이너 메모리 사용량
docker stats <container_id>

# cgroup 직접 확인
cat /sys/fs/cgroup/system.slice/docker-<id>.scope/memory.events
# oom: OOM 발생 횟수
# oom_kill: OOM kill 발생 횟수
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Tips

```bash
# 전체 cgroup 트리 시각화
systemd-cgls

# 실시간 리소스 사용량 (top과 유사)
systemd-cgtop

# 프로세스가 속한 cgroup 확인
cat /proc/<PID>/cgroup

# cgroup v2 컨트롤러 목록
cat /sys/fs/cgroup/cgroup.controllers

# 특정 서비스 cgroup 경로
systemctl show <service> -p ControlGroup
```

⚠️ `/sys/fs/cgroup` 파일을 직접 수정하면 재부팅 시 초기화됩니다. 영구 설정은 systemd unit 파일 또는 `/etc/cgconfig.conf`를 사용합니다.

⚠️ cgroupv2 환경에서 `--privileged` 없이 systemd 컨테이너를 실행하면 Exit 255로 즉시 종료됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. cgroup 파일시스템

`/sys/fs/cgroup/`은 디스크에 존재하지 않는 가상 파일시스템입니다. 커널이 런타임에 생성하며 재부팅 시 초기화됩니다.

```bash
mount | grep cgroup
# cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime)
```

### 파일 읽기/쓰기 = 커널 명령

```bash
# 파일 쓰기 → 커널에 설정 전달
echo 512M > /sys/fs/cgroup/mygroup/memory.max

# 파일 읽기 → 커널에서 실시간 값 조회
cat /sys/fs/cgroup/mygroup/memory.current
```

### 주요 컨트롤 파일

| 파일 | 위치 | 역할 |
|------|------|------|
| `cgroup.procs` | root + 하위 | 소속 PID 목록. 쓰면 프로세스 이동 |
| `cgroup.controllers` | root + 하위 | 사용 가능한 컨트롤러 목록 |
| `cgroup.subtree_control` | root + 하위 | 하위 그룹에 위임할 컨트롤러 |
| `cpu.stat` | root + 하위 | CPU 사용 통계 |
| `memory.stat` | root + 하위 | 메모리 사용 통계 |
| `memory.pressure` | root + 하위 | 메모리 pressure stall info (PSI) |
| `memory.max` | 하위만 | 메모리 상한 |
| `memory.current` | 하위만 | 현재 메모리 사용량 |
| `memory.high` | 하위만 | 소프트 상한 (초과 시 throttle) |
| `cpu.max` | 하위만 | CPU quota/period |
| `cpu.weight` | 하위만 | CPU 가중치 (1~10000) |
| `io.max` | 하위만 | I/O 속도 상한 |
| `pids.max` | 하위만 | 최대 프로세스 수 |
| `pids.current` | 하위만 | 현재 프로세스 수 |

### 영구 설정

`/sys/fs/cgroup` 직접 수정은 재부팅 시 초기화됩니다. 영구 설정은 systemd unit 파일을 사용합니다.

```ini
# /etc/systemd/system/nginx.service.d/override.conf
[Service]
MemoryMax=512M
CPUQuota=50%
```

> 💡 `/proc`, `/sys`, `/sys/fs/cgroup` 상세 비교는 [linux_virtual_fs.md](./linux_virtual_fs.md) 참고

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Kernel Documentation: [kernel.org/doc/html/latest/admin-guide/cgroup-v2.html](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html) — ★★★★☆
- Red Hat cgroup v2: [access.redhat.com](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_monitoring_and_updating_the_kernel/assembly_using-cgroups-v2-to-control-distribution-of-cpu-time-for-applications_managing-monitoring-and-updating-the-kernel) — ★★★☆☆
- Brendan Gregg: [brendangregg.com/linuxperf.html](https://www.brendangregg.com/linuxperf.html) — ★★★☆☆

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
