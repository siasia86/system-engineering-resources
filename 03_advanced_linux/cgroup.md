# cgroup

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. v1 vs v2](#3-v1-vs-v2)                         |
| [4. 주요 컨트롤러](#4-주요-컨트롤러) / [5. 실습](#5-실습) / [6. Docker와 cgroup](#6-docker와-cgroup) |
| [7. systemd와 cgroup](#7-systemd와-cgroup) / [8. 트러블슈팅](#8-트러블슈팅) / [9. Tips](#9-tips)     |
| [10. cgroup 파일시스템](#10-cgroup-파일시스템) / [11. 실 테스트 (Docker)](#11-실-테스트-docker)      |
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

| 기능                      | 설명                              |
|---------------------------|-----------------------------------|
| 제한 (Limiting)           | CPU, 메모리, I/O 사용량 상한 설정 |
| 우선순위 (Prioritization) | 그룹 간 리소스 배분 비율 설정     |
| 계측 (Accounting)         | 그룹별 리소스 사용량 측정         |

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
├── cgroup.procs          # list of PIDs in this cgroup
├── cgroup.controllers    # available controllers
├── cpu.max               # CPU quota/period
├── cpu.weight            # CPU weight
├── cpu.stat              # CPU usage stats
├── memory.max            # memory limit
├── memory.current        # current memory usage
├── memory.high           # soft limit (throttle on exceed)
├── io.max                # I/O bandwidth limit
├── pids.max              # max process count
└── pids.current          # current process count
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. v1 vs v2

| 항목          | v1                                              | v2                               |
|---------------|-------------------------------------------------|----------------------------------|
| 구조          | 컨트롤러별 별도 트리                            | 단일 통합 트리                   |
| 경로          | `/sys/fs/cgroup/cpu/`, `/sys/fs/cgroup/memory/` | `/sys/fs/cgroup/`                |
| 프로세스 소속 | 컨트롤러마다 다른 그룹 가능                     | 하나의 그룹에만 소속             |
| 기본 OS       | CentOS 7, Ubuntu 18.04                          | Ubuntu 22.04+, Rocky 9+, RHEL 9+ |
| 권장          | 레거시                                          | 현재 표준                        |

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
├── cgroup.procs                         # PIDs in root cgroup
├── cgroup.subtree_control               # controllers delegated to children
├── cgroup.stat                          # cgroup stats
├── cpu.stat                             # CPU stats (exists in root too)
├── cpu.pressure                         # CPU pressure stall info
├── memory.stat                          # memory stats (exists in root too)
├── memory.pressure                      # memory pressure stall info
├── io.stat                              # I/O stats (exists in root too)
├── io.pressure                          # I/O pressure stall info
├── system.slice/                        # systemd service group
│   ├── memory.max                       # <- limit files exist from subtree
│   ├── cpu.max
│   └── cron.service/                    # individual service
│       ├── memory.max
│       ├── cpu.max
│       └── pids.max
└── user.slice/                          # user session group
    └── user-1000.slice/                 # UID 1000 user
```

🟡 root cgroup에는 `memory.max`, `cpu.max`, `pids.max` 등 **제한 설정 파일이 없습니다** . 통계/pressure 파일만 존재합니다. 제한은 하위 cgroup(`system.slice/`, `user.slice/` 이하)에서만 설정 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 컨트롤러

### 계산식 참조

설정값 입력 전 단위 변환 공식입니다.

#### CPU % → quota/period

```
cpu.max 형식: "quota period" (단위: 마이크로초)

CPU % = quota / period × 100

예시:
  50%  → 50000 100000   (50000 / 100000 = 0.5 = 50%)
  25%  → 25000 100000
  200% → 200000 100000  (코어 2개 사용)
  제한없음 → "max 100000"

공식: quota = (CPU% / 100) × period
      period 기본값 = 100000 (100ms)
```

```bash
# 원하는 CPU% → quota 계산
CPU_PCT=30; PERIOD=100000
echo "$((CPU_PCT * PERIOD / 100)) $PERIOD" > /sys/fs/cgroup/mygroup/cpu.max
```

#### Memory MB/GB → bytes

```
bytes = MB × 1024 × 1024
bytes = GB × 1024 × 1024 × 1024

예시:
  512MB → 536870912    (512 × 1024 × 1024)
  1GB   → 1073741824   (1 × 1024 × 1024 × 1024)
  2GB   → 2147483648
```

```bash
# 단위별 변환
echo $((512 * 1024 * 1024))        # 512MB = 536870912
echo $((1 * 1024 * 1024 * 1024))   # 1GB   = 1073741824
echo $((2 * 1024 * 1024 * 1024))   # 2GB   = 2147483648

# 또는 systemd 단위 문자열 사용 (systemctl set-property 시)
# MemoryMax=512M  MemoryMax=1G  (자동 변환)
```

#### IO MB/s → bytes/s (rbps/wbps)

```
bytes/s = MB/s × 1024 × 1024

예시:
  50MB/s  → 52428800    (50 × 1024 × 1024)
  100MB/s → 104857600
  200MB/s → 209715200
```

```bash
# 원하는 MB/s → bytes/s 계산
MBps=100
echo "8:0 rbps=$((MBps * 1024 * 1024)) wbps=$((MBps * 1024 * 1024))"   > /sys/fs/cgroup/mygroup/io.max
```

#### cpu.stat 출력 해석

```bash
cat /sys/fs/cgroup/mygroup/cpu.stat
# usage_usec 5000000    ← 누적 CPU 사용 시간 (마이크로초)
# user_usec  3000000    ← user space 사용 시간
# system_usec 2000000   ← kernel space 사용 시간
# nr_throttled 10       ← quota 초과로 throttle된 횟수
# throttled_usec 500000 ← throttle된 총 시간 (마이크로초)

# usage_usec → 초 변환: 5000000 / 1000000 = 5초
# throttled_usec가 크면 CPU 제한이 너무 낮은 것
```

---

### cpu

```bash
# CPU 사용량 제한 (v2)
# 형식: quota period (마이크로초)
# 50% 제한: 50000 100000
echo "50000 100000" > /sys/fs/cgroup/mygroup/cpu.max

# CPU weight (기본값 100, 범위 1~10000)
echo 200 > /sys/fs/cgroup/mygroup/cpu.weight

# 현재 CPU 사용 통계
cat /sys/fs/cgroup/mygroup/cpu.stat
```

### memory

```bash
# 메모리 상한 설정 (512MB = 512 × 1024 × 1024 = 536870912 bytes)
echo $((512 * 1024 * 1024)) > /sys/fs/cgroup/mygroup/memory.max

# current usage 확인 (bytes → MB: 값 / 1024 / 1024)
cat /sys/fs/cgroup/mygroup/memory.current

# OOM 발생 시 kill 대신 throttle (swap 1GB = 1073741824 bytes)
echo $((1024 * 1024 * 1024)) > /sys/fs/cgroup/mygroup/memory.swap.max

# memory stats
cat /sys/fs/cgroup/mygroup/memory.stat
```

### io (blkio)

cgroup v2의 I/O 컨트롤러입니다. 디바이스별로 대역폭(bps)과 IOPS를 제한하거나 가중치(weight)로 우선순위를 조정합니다.

#### 디바이스 번호 확인

```bash
# major:minor 번호 확인 — io.max 설정에 필요
ls -al /dev/sdb
# brw-rw---- 1 root disk 8, 16 May 20 11:24 /dev/sdb
#                         ^  ^^
#                         major=8, minor=16 → "8:16"

lsblk -o NAME,MAJ:MIN,SIZE,TYPE
```

#### io.max — 속도/IOPS 상한 (하드 제한)

```bash
# 형식: "major:minor rbps=<bytes> wbps=<bytes> riops=<count> wiops=<count>"
# 값 생략 시 해당 항목은 제한 없음 (max)

# 읽기/쓰기 100MB/s 제한
echo "8:16 rbps=104857600 wbps=104857600" > /sys/fs/cgroup/mygroup/io.max

# IOPS 제한 (읽기 1000, 쓰기 500)
echo "8:16 riops=1000 wiops=500" > /sys/fs/cgroup/mygroup/io.max

# 읽기 속도 + 쓰기 IOPS 혼합
echo "8:16 rbps=52428800 wiops=200" > /sys/fs/cgroup/mygroup/io.max

# 제한 해제
echo "8:16 rbps=max wbps=max riops=max wiops=max" > /sys/fs/cgroup/mygroup/io.max

# 현재 설정 확인
cat /sys/fs/cgroup/mygroup/io.max
```

#### io.weight — 우선순위 (소프트 제한)

```bash
# 기본값 100, 범위 1~10000
# 값이 높을수록 I/O 경합 시 더 많은 대역폭 할당

# 전체 디바이스 기본 가중치 설정
echo "default 200" > /sys/fs/cgroup/mygroup/io.weight

# 특정 디바이스만 가중치 설정
echo "8:16 500" > /sys/fs/cgroup/mygroup/io.weight

# 현재 설정 확인
cat /sys/fs/cgroup/mygroup/io.weight
```

#### io.stat — I/O 통계

```bash
cat /sys/fs/cgroup/mygroup/io.stat
# 출력 예시:
# 8:16 rbytes=1073741824 wbytes=536870912 rios=10240 wios=5120 dbytes=0 dios=0
#       읽기 바이트       쓰기 바이트       읽기 횟수   쓰기 횟수
```

| 필드                | 설명                      |
|---------------------|---------------------------|
| `rbytes` / `wbytes` | 누적 읽기/쓰기 바이트     |
| `rios` / `wios`     | 누적 읽기/쓰기 I/O 횟수   |
| `dbytes` / `dios`   | discard(trim) 바이트/횟수 |

#### io.pressure — I/O 압박 지표

```bash
cat /sys/fs/cgroup/mygroup/io.pressure
# some avg10=0.00 avg60=0.00 avg300=0.00 total=0
# full avg10=0.00 avg60=0.00 avg300=0.00 total=0
# some: 일부 태스크가 I/O 대기 중인 시간 비율 (%)
# full: 모든 태스크가 I/O 대기 중인 시간 비율 (%)
```

#### systemd 서비스에 적용

```bash
# IOReadBandwidthMax / IOWriteBandwidthMax
systemctl set-property myapp.service IOReadBandwidthMax="/dev/sdb 100M"
systemctl set-property myapp.service IOWriteBandwidthMax="/dev/sdb 100M"

# IOReadIOPSMax / IOWriteIOPSMax
systemctl set-property myapp.service IOReadIOPSMax="/dev/sdb 1000"

# IOWeight (우선순위)
systemctl set-property myapp.service IOWeight=200

# 확인
systemctl show myapp.service | grep -i io
```

#### cgroup v1 (blkio) vs v2 (io) 비교

| 항목      | v1 blkio                          | v2 io           |
|-----------|-----------------------------------|-----------------|
| 속도 제한 | `blkio.throttle.read_bps_device`  | `io.max rbps=`  |
| IOPS 제한 | `blkio.throttle.read_iops_device` | `io.max riops=` |
| 가중치    | `blkio.weight`                    | `io.weight`     |
| 통계      | `blkio.io_service_bytes`          | `io.stat`       |
| 설정 형식 | 파일별 분리                       | 한 줄에 모든 값 |

#### 프로세스에 I/O 제한 적용

`io.max` 설정만으로는 제한이 걸리지 않습니다. 대상 프로세스를 해당 cgroup에 등록해야 합니다.

```bash
# 1. cgroup 생성
mkdir /sys/fs/cgroup/mygroup

# 2. io.max 설정
echo "8:16 rbps=104857600 wbps=104857600" > /sys/fs/cgroup/mygroup/io.max

# 3. 프로세스 등록 ← 없으면 제한 안 걸림
echo <pid> > /sys/fs/cgroup/mygroup/cgroup.procs

# 등록된 프로세스 확인
cat /sys/fs/cgroup/mygroup/cgroup.procs
```

- 등록된 PID만 제한됨 — 같은 서버의 다른 프로세스는 영향 없음
- 자식 프로세스 자동 상속 — fork된 프로세스도 같은 cgroup에 속함
- systemd 서비스는 자동 배치 — 별도 등록 불필요

```bash
# nginx → /sys/fs/cgroup/system.slice/nginx.service/ 에 자동 배치
# 자세한 systemd 적용 방법은 위 '#### systemd 서비스에 적용' 참고
cat /sys/fs/cgroup/system.slice/nginx.service/cgroup.procs
```


#### 적용 확인

```bash
# 1. 프로세스가 cgroup에 등록됐는지 확인
cat /sys/fs/cgroup/mygroup/cgroup.procs
# 출력: 등록된 PID 목록

# 특정 프로세스가 어느 cgroup에 속하는지 역방향 확인
cat /proc/<pid>/cgroup
# 출력 예시:
# 0::/mygroup

# 2. io.max 설정값 확인
cat /sys/fs/cgroup/mygroup/io.max
# 출력 예시:
# 8:16 rbps=104857600 wbps=104857600 riops=max wiops=max

# 3. I/O 제한이 실제로 걸리는지 dd로 테스트
#    현재 shell을 cgroup에 넣은 뒤 실행
echo $$ > /sys/fs/cgroup/mygroup/cgroup.procs
dd if=/dev/zero of=/tmp/testfile bs=1M count=500 oflag=direct 2>&1
# 제한 전: 수백 MB/s
# 제한 후: ~100MB/s (io.max 설정값 근처)

# 4. io.stat으로 실시간 I/O 사용량 확인
watch -n 1 'cat /sys/fs/cgroup/mygroup/io.stat'
# 출력 예시:
# 8:16 rbytes=0 wbytes=157286400 rios=0 wios=150 dbytes=0 dios=0
#                ^^^^^^^^^^^^^^^ wbytes가 증가하면 쓰기 I/O 발생 중
```

🟡 `dd` 테스트 시 `oflag=direct`를 붙여야 page cache를 우회하여 실제 디스크 I/O가 발생합니다. 없으면 cache에 쓰여 제한이 안 걸린 것처럼 보입니다.

### pids

```bash
# max process count 제한
echo 100 > /sys/fs/cgroup/mygroup/pids.max

# current process count
cat /sys/fs/cgroup/mygroup/pids.current
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실습

### cgroup 수동 생성 (v2)

cgroup = 디렉토리입니다. 디렉토리를 만들면 cgroup이 생성되고, 파일에 값을 쓰면 제한이 설정됩니다.

```
mkdir (create cgroup)
    │
    v
subtree_control (delegate controllers -- memory.max won't appear without this)
    │
    v
echo <value> > memory.max (set limit)
    │
    v
echo PID > cgroup.procs (attach process -- limit applies from here)
    │
    v
echo PID > parent/cgroup.procs (move process)
    │
    v
rmdir (delete cgroup)
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

🟡 `rmdir`은 cgroup 안에 프로세스가 남아있으면 실패합니다. 반드시 프로세스를 먼저 이동시킵니다.

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

Ubuntu 22.04+, Rocky 9+ 등 cgroupv2 기본 환경에서 systemd를 PID 1로 실행하는 컨테이너가 실패하는 경우 아래 설정이 필요합니다.

#### 실패 원인

```
Failed to connect to bus: No such file or directory
System has not been booted with systemd as init system (PID 1)
```

systemd는 PID 1로 실행되어야 하며, cgroup 파일시스템에 직접 접근해야 합니다. 일반 컨테이너는 이 두 조건을 충족하지 못합니다.

#### docker-compose.yml 설정

```yaml
services:
  ubuntu22:
    image: geerlingguy/docker-ubuntu2204-ansible
    privileged: true                           # Linux capability 전체 부여
    command: /lib/systemd/systemd              # systemd를 PID 1로 실행
    cgroupns_mode: host                        # 호스트 cgroup 네임스페이스 공유
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw       # cgroup 파일시스템 마운트
    tmpfs:
      - /run                                   # systemd runtime 디렉토리
      - /run/lock                              # lock 파일 디렉토리
```

| 옵션                            | 필요 이유                                                |
|---------------------------------|----------------------------------------------------------|
| `privileged: true`              | systemd가 cgroup, mount, 네트워크 등 커널 기능 접근 필요 |
| `command: /lib/systemd/systemd` | systemd를 PID 1로 실행 (없으면 bash 등이 PID 1)          |
| `cgroupns_mode: host`           | 컨테이너가 호스트 cgroup 트리를 직접 보고 쓸 수 있게 함  |
| `/sys/fs/cgroup` 마운트         | systemd가 서비스별 cgroup 생성/관리에 필요               |
| `tmpfs: /run`                   | systemd가 `/run`에 소켓, PID 파일 생성                   |

#### OS별 systemd 경로

```yaml
# Ubuntu 22.04 / 24.04
command: /lib/systemd/systemd

# Rocky 9 / AlmaLinux 9 / CentOS Stream 9
command: /usr/lib/systemd/systemd

# AmazonLinux 2023
command: /usr/lib/systemd/systemd
```

#### 동작 확인

```bash
# 컨테이너 접속 후 systemd 상태 확인
docker exec -it <container> bash
systemctl status          # 서비스 목록
systemctl is-system-running  # running / degraded

# PID 1 확인
ps -p 1 -o comm=
# 출력: systemd
```

#### cgroupv1 강제 사용 (비권장)

```bash
# 호스트 부팅 옵션에 추가 — 재부팅 필요
# /etc/default/grub
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=0"
update-grub && reboot

# 확인
stat -fc %T /sys/fs/cgroup/
# tmpfs → v1, cgroup2fs → v2
```

🟡 cgroupv1 강제 사용은 보안 패치 및 신규 기능 미지원으로 권장하지 않습니다. `privileged + cgroupns_mode: host` 방식을 사용합니다.

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

| 지시어       | 설명                           | 예시   |
|--------------|--------------------------------|--------|
| `MemoryMax`  | 메모리 상한                    | `512M` |
| `MemoryHigh` | 소프트 상한 (초과 시 throttle) | `400M` |
| `CPUQuota`   | CPU 사용률 상한                | `50%`  |
| `CPUWeight`  | CPU 우선순위 가중치            | `200`  |
| `IOWeight`   | I/O 우선순위                   | `100`  |
| `TasksMax`   | 최대 프로세스/스레드 수        | `100`  |

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

🟡 `/sys/fs/cgroup` 파일을 직접 수정하면 재부팅 시 초기화됩니다. 영구 설정은 systemd unit 파일 또는 `/etc/cgconfig.conf`를 사용합니다.

🟡 cgroupv2 환경에서 `--privileged` 없이 systemd 컨테이너를 실행하면 Exit 255로 즉시 종료됩니다.

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

| 파일                     | 위치        | 역할                              |
|--------------------------|-------------|-----------------------------------|
| `cgroup.procs`           | root + 하위 | 소속 PID 목록. 쓰면 프로세스 이동 |
| `cgroup.controllers`     | root + 하위 | 사용 가능한 컨트롤러 목록         |
| `cgroup.subtree_control` | root + 하위 | 하위 그룹에 위임할 컨트롤러       |
| `cpu.stat`               | root + 하위 | CPU 사용 통계                     |
| `memory.stat`            | root + 하위 | 메모리 사용 통계                  |
| `memory.pressure`        | root + 하위 | 메모리 pressure stall info (PSI)  |
| `memory.max`             | 하위만      | 메모리 상한                       |
| `memory.current`         | 하위만      | 현재 메모리 사용량                |
| `memory.high`            | 하위만      | 소프트 상한 (초과 시 throttle)    |
| `cpu.max`                | 하위만      | CPU quota/period                  |
| `cpu.weight`             | 하위만      | CPU 가중치 (1~10000)              |
| `io.max`                 | 하위만      | I/O 속도 상한                     |
| `pids.max`               | 하위만      | 최대 프로세스 수                  |
| `pids.current`           | 하위만      | 현재 프로세스 수                  |

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

## 11. 실 테스트 (Docker)

cgroupv2 환경(Ubuntu 22.04 컨테이너)에서 실제 검증한 결과입니다.

### 테스트 환경

| 항목          | 내용                                      |
|---------------|-------------------------------------------|
| 호스트 cgroup | `cgroup2fs` (cgroupv2)                    |
| 컨테이너      | `02_compose-ubuntu22-1`                   |
| 컨테이너 설정 | `privileged: true`, `cgroupns_mode: host` |
| PID 1         | `systemd`                                 |

### systemd 동작 확인

```bash
docker exec -it 02_compose-ubuntu22-1 bash

# PID 1 확인
ps -p 1 -o pid,comm=
# 출력: 1 systemd

# systemd 상태
systemctl is-system-running
# 출력: running

# 실행 중인 서비스 목록
systemctl list-units --type=service --state=running --no-pager
```

```
UNIT                     LOAD   ACTIVE SUB     DESCRIPTION
dbus.service             loaded active running D-Bus System Message Bus
systemd-journald.service loaded active running Journal Service
systemd-logind.service   loaded active running User Login Management
```

### io.max I/O 제한 테스트

```bash
# 1. cgroup 생성 및 io.max 설정 (10MB/s)
mkdir -p /sys/fs/cgroup/testgroup
echo '8:0 rbps=10485760 wbps=10485760' > /sys/fs/cgroup/testgroup/io.max

# 설정 확인
cat /sys/fs/cgroup/testgroup/io.max
# 8:0 rbps=10485760 wbps=10485760 riops=max wiops=max

# 2. 프로세스 등록 및 소속 cgroup 확인
echo $$ > /sys/fs/cgroup/testgroup/cgroup.procs
cat /proc/$$/cgroup | grep '0::'
# 0::/testgroup

# 3. 제한 전 (testgroup 밖)
dd if=/dev/zero of=/tmp/testfile bs=1M count=100 oflag=direct 2>&1
# 104857600 bytes copied, 0.036 s, 2.9 GB/s

# 4. 제한 후 (testgroup 안 — echo $$ 로 등록 후)
dd if=/dev/zero of=/tmp/testfile bs=1M count=100 oflag=direct 2>&1
# 104857600 bytes copied, 10.002 s, 10.5 MB/s
```

| 구분    | 속도      | 비고                          |
|---------|-----------|-------------------------------|
| 제한 전 | 2.9 GB/s  | page cache 우회(oflag=direct) |
| 제한 후 | 10.5 MB/s | io.max 10MB/s 설정값 근접     |

🟡 `oflag=direct` 없이 실행하면 page cache에 쓰여 제한이 걸리지 않은 것처럼 보입니다.

### 정리

```bash
# testgroup에서 빠져나오기 (root cgroup으로 이동)
echo $$ > /sys/fs/cgroup/cgroup.procs

# cgroup 삭제 (프로세스가 없어야 삭제 가능)
rmdir /sys/fs/cgroup/testgroup

# 테스트 파일 삭제
rm -f /tmp/testfile
```

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

**작성일** : 2026-05-15

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
