# /proc & /sys — Linux 가상 파일시스템

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. /proc 구조](#2-proc-구조) / [3. /proc 주요 파일](#3-proc-주요-파일) |
| [4. /sys 구조](#4-sys-구조) / [5. /sys 주요 경로](#5-sys-주요-경로) / [6. proc vs sys](#6-proc-vs-sys) |
| [7. 실전 활용](#7-실전-활용) / [8. 주의사항](#8-주의사항) / [9. Tips](#9-tips) |

---

## 1. 개요

`/proc`와 `/sys`는 디스크에 존재하지 않는 가상 파일시스템입니다. 커널이 런타임에 생성하며, 파일 읽기/쓰기로 커널 상태를 조회하고 설정합니다.

```
┌─────────────────────────────────────────────────────────────┐
│              Linux Virtual Filesystem                       │
│                                                             │
│  /proc  (procfs)   kernel/process state  read/write        │
│  /sys   (sysfs)    hardware/driver info  read/write        │
│  /sys/fs/cgroup    cgroup control        read/write        │
│                                                             │
│  all virtual — cleared on reboot                           │
└─────────────────────────────────────────────────────────────┘
```

```bash
mount | grep -E "proc|sysfs|cgroup"
# proc on /proc type proc
# sysfs on /sys type sysfs
# cgroup2 on /sys/fs/cgroup type cgroup2
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. /proc 구조

```
/proc/
├── 1/                    # PID 1 (systemd) 프로세스 정보
│   ├── cmdline           # 실행 명령어
│   ├── environ           # 환경변수
│   ├── fd/               # 열린 파일 디스크립터
│   ├── maps              # 메모리 맵
│   ├── net/              # 네트워크 정보
│   ├── status            # 프로세스 상태 요약
│   └── cgroup            # 소속 cgroup
├── <PID>/                # 각 프로세스별 디렉토리
├── cpuinfo               # CPU 정보
├── meminfo               # 메모리 정보
├── net/                  # 네트워크 통계
├── sys/                  # 커널 파라미터 (sysctl)
├── mounts                # 마운트 목록
├── filesystems           # 지원 파일시스템
├── interrupts            # IRQ 통계
├── loadavg               # 로드 평균
├── uptime                # 부팅 후 경과 시간
└── version               # 커널 버전
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. /proc 주요 파일

### 시스템 정보

```bash
# CPU 정보
cat /proc/cpuinfo | grep -E "model name|cpu cores|processor" | head -10

# 메모리 정보
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable|SwapTotal"

# 커널 버전
cat /proc/version

# 부팅 후 경과 시간 (초)
cat /proc/uptime

# 로드 평균 (1분/5분/15분)
cat /proc/loadavg

# 마운트 목록
cat /proc/mounts
```

### 프로세스 정보

```bash
# 프로세스 실행 명령어 (null 구분자 → 공백 변환)
cat /proc/<PID>/cmdline | tr '\0' ' '

# 프로세스 환경변수
cat /proc/<PID>/environ | tr '\0' '\n'

# 프로세스 메모리 맵
cat /proc/<PID>/maps

# 열린 파일 디스크립터
ls -la /proc/<PID>/fd

# 프로세스 상태
cat /proc/<PID>/status

# 실행 파일 경로
readlink /proc/<PID>/exe

# 작업 디렉토리
readlink /proc/<PID>/cwd
```

### 네트워크 정보

```bash
# TCP 연결 상태
cat /proc/net/tcp
cat /proc/net/tcp6

# 네트워크 인터페이스 통계
cat /proc/net/dev

# ARP 테이블
cat /proc/net/arp

# 라우팅 테이블
cat /proc/net/route
```

### 커널 파라미터 (sysctl)

```bash
# /proc/sys/ 아래가 sysctl 파라미터
# 읽기
cat /proc/sys/net/ipv4/ip_forward
cat /proc/sys/vm/swappiness

# 쓰기 (즉시 적용, 재부팅 시 초기화)
echo 1 > /proc/sys/net/ipv4/ip_forward

# 영구 적용은 /etc/sysctl.conf 또는 sysctl 명령어 사용
sysctl -w net.ipv4.ip_forward=1
sysctl -p  # /etc/sysctl.conf 적용
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. /sys 구조

```
/sys/
├── block/                # 블록 디바이스 (sda, nvme0n1 등)
├── bus/                  # 버스별 디바이스 (pci, usb, i2c 등)
│   ├── pci/
│   └── usb/
├── class/                # 디바이스 클래스별
│   ├── net/              # 네트워크 인터페이스
│   ├── block/            # 블록 디바이스
│   └── input/            # 입력 디바이스
├── devices/              # 실제 디바이스 트리 (전체 하드웨어 계층)
├── fs/                   # 파일시스템 관련
│   └── cgroup/           # cgroup 마운트 포인트
├── kernel/               # 커널 파라미터
├── module/               # 로드된 커널 모듈 파라미터
└── power/                # 전원 관리
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. /sys 주요 경로

### 네트워크

```bash
# 인터페이스 목록
ls /sys/class/net/

# 인터페이스 속도 (Mbps)
cat /sys/class/net/eth0/speed

# MTU
cat /sys/class/net/eth0/mtu

# MAC 주소
cat /sys/class/net/eth0/address

# 인터페이스 활성화 여부
cat /sys/class/net/eth0/operstate
```

### 디스크/블록

```bash
# 디스크 스케줄러 확인
cat /sys/block/sda/queue/scheduler

# 디스크 스케줄러 변경
echo mq-deadline | sudo tee /sys/block/sda/queue/scheduler

# Read-ahead 크기 (KB)
cat /sys/block/sda/queue/read_ahead_kb

# 디스크 회전 여부 (0=SSD, 1=HDD)
cat /sys/block/sda/queue/rotational
```

### CPU

```bash
# CPU 코어 수
ls /sys/devices/system/cpu/ | grep -c "cpu[0-9]"

# 특정 코어 온/오프 (cpu0은 불가)
echo 0 | sudo tee /sys/devices/system/cpu/cpu3/online
echo 1 | sudo tee /sys/devices/system/cpu/cpu3/online

# CPU 주파수 (kHz)
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# CPU 거버너 (performance/powersave/ondemand)
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

### 커널 모듈

```bash
# 모듈 파라미터 확인
ls /sys/module/
cat /sys/module/tcp_cubic/parameters/

# 예: nf_conntrack 최대 연결 수
cat /sys/module/nf_conntrack/parameters/hashsize
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. proc vs sys

| 항목 | `/proc` | `/sys` |
|------|---------|--------|
| 목적 | 프로세스/커널 상태 조회 | 하드웨어/드라이버 설정 |
| 구조 | 비정형 (역사적 누적) | 계층적 (디바이스 모델 반영) |
| 도입 | 커널 초기 | 커널 2.6 (sysfs) |
| 프로세스 정보 | ✅ (`/proc/<PID>/`) | ❌ |
| 하드웨어 제어 | 제한적 | ✅ |
| sysctl 파라미터 | ✅ (`/proc/sys/`) | ❌ |
| cgroup | ❌ | ✅ (`/sys/fs/cgroup/`) |
| 재부팅 후 유지 | ❌ (가상) | ❌ (가상) |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 활용

### 장애 대응 — 프로세스 조사

```bash
# 특정 포트를 사용하는 프로세스 찾기
grep -r ":1F90" /proc/net/tcp  # 0x1F90 = 8080

# 프로세스가 열고 있는 파일 확인
ls -la /proc/<PID>/fd | grep -v "^total"

# 삭제됐지만 열려있는 파일 (디스크 공간 미반환)
ls -la /proc/<PID>/fd | grep "(deleted)"

# 프로세스 메모리 사용량 상세
cat /proc/<PID>/status | grep -E "VmRSS|VmSize|VmSwap"
```

### 성능 튜닝

```bash
# 스왑 사용 최소화 (SSD 서버)
echo 10 | sudo tee /proc/sys/vm/swappiness

# 파일 디스크립터 최대값 확인/변경
cat /proc/sys/fs/file-max
echo 1000000 | sudo tee /proc/sys/fs/file-max

# TCP TIME_WAIT 재사용 (클라이언트 outbound 연결에만 적용)
echo 1 | sudo tee /proc/sys/net/ipv4/tcp_tw_reuse

# 디스크 I/O 스케줄러 (NVMe는 none 권장)
echo none | sudo tee /sys/block/nvme0n1/queue/scheduler
```

### 보안 점검

```bash
# IP 포워딩 비활성화 확인 (라우터가 아닌 서버)
cat /proc/sys/net/ipv4/ip_forward  # 0이어야 정상

# SYN 쿠키 활성화 확인 (SYN Flood 방어)
cat /proc/sys/net/ipv4/tcp_syncookies  # 1이어야 정상

# ICMP 리다이렉트 비활성화 확인
cat /proc/sys/net/ipv4/conf/all/accept_redirects  # 0이어야 정상

# 커널 포인터 노출 방지
cat /proc/sys/kernel/kptr_restrict  # 1 또는 2 권장
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 주의사항

⚠️ **재부팅 시 초기화** — `/proc`, `/sys` 직접 수정은 재부팅 시 사라집니다. 영구 적용은 반드시 설정 파일을 사용합니다.

```bash
# 임시 (재부팅 시 초기화)
echo 1 > /proc/sys/net/ipv4/ip_forward

# 영구 (/etc/sysctl.conf 또는 /etc/sysctl.d/*.conf)
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/99-custom.conf
sudo sysctl -p /etc/sysctl.d/99-custom.conf
```

⚠️ **잘못된 값 쓰기** — 일부 파일은 잘못된 값을 쓰면 커널 패닉이 발생할 수 있습니다. 프로덕션 환경에서는 테스트 후 적용합니다.

⚠️ **`/proc/<PID>/mem` 직접 접근** — 프로세스 메모리를 직접 읽고 쓸 수 있어 보안상 위험합니다. `ptrace` 권한이 필요합니다.

⚠️ **`/proc/sysrq-trigger`** — 커널 긴급 명령어 트리거입니다. 실수로 쓰면 시스템이 즉시 재부팅/패닉됩니다.

```bash
# 절대 실수로 실행하지 말 것
# echo b > /proc/sysrq-trigger  # 즉시 재부팅
# echo c > /proc/sysrq-trigger  # 커널 패닉
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Tips

```bash
# 현재 프로세스의 cgroup 확인
cat /proc/$$/cgroup

# 시스템 전체 열린 파일 수
cat /proc/sys/fs/file-nr

# 커널 메시지 스트리밍 (블로킹, syslogd가 사용 — dmesg -w 와 유사하나 동일하지 않음)
cat /proc/kmsg

# NUMA 노드 정보
cat /proc/buddyinfo

# 인터럽트 통계 (IRQ 분산 확인)
watch -n1 cat /proc/interrupts

# /sys 파일 변경 감지 (inotify)
inotifywait -m /sys/block/sda/queue/scheduler
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux Kernel Documentation: [kernel.org/doc/html/latest/filesystems/proc.html](https://www.kernel.org/doc/html/latest/filesystems/proc.html) — ★★★★☆
- sysfs Documentation: [kernel.org/doc/html/latest/filesystems/sysfs.html](https://www.kernel.org/doc/html/latest/filesystems/sysfs.html) — ★★★★☆
- Brendan Gregg Linux Performance: [brendangregg.com/linuxperf.html](https://www.brendangregg.com/linuxperf.html) — ★★★☆☆
- [cgroup.md](./cgroup.md)

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
