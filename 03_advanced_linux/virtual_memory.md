# Virtual Memory — 가상 메모리

Linux 가상 메모리 시스템의 구조, 동작 원리, 트러블슈팅을 정리합니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 페이지와 페이지 테이블](#2-페이지와-페이지-테이블) / [3. Page fault](#3-page-fault) |
| [4. Page cache](#4-page-cache) / [5. Swap](#5-swap) / [6. Copy-on-Write](#6-copy-on-write)                   |
| [7. 메모리 확인 명령어](#7-메모리-확인-명령어) / [8. 트러블슈팅](#8-트러블슈팅)                              |

---

## 1. 개요

각 프로세스는 독립된 가상 주소 공간을 가집니다. 실제 물리 메모리와 1:1 대응이 아니며, MMU(Memory Management Unit)가 가상 → 물리 주소를 변환합니다.

```
Process A          Process B
┌──────────┐       ┌──────────┐
│ 0x0000   │       │ 0x0000   │  <- same virtual address
│ ...      │       │ ...      │     different physical address
│ 0xFFFF   │       │ 0xFFFF   │
└──────────┘       └──────────┘
      │                  │
      v                  v
┌─────────────────────────────┐
│     Physical Memory         │
│  [A pages] [B pages]        │
└─────────────────────────────┘
```

| 장점   | 설명                                       |
|--------|--------------------------------------------|
| 격리   | 프로세스 간 메모리 침범 불가               |
| 과할당 | 물리 메모리보다 많은 가상 메모리 사용 가능 |
| 단순화 | 프로세스는 연속된 주소 공간으로 인식       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 페이지와 페이지 테이블

### 페이지 크기

```bash
# 기본 페이지 크기 확인 (보통 4KB)
getconf PAGE_SIZE
# 4096

# Huge Page 크기
cat /proc/meminfo | grep Huge
# HugePages_Total: 0
# Hugepagesize:    2048 kB  (2MB)
```

### 프로세스 메모리 맵

```bash
# 프로세스 가상 주소 공간 확인
cat /proc/<pid>/maps
# 주소범위           권한  오프셋  장치  inode  경로
# 7f8a00000000-7f8a01000000 rw-p 00000000 00:00 0

# 상세 (PSS 포함)
cat /proc/<pid>/smaps

# 요약
cat /proc/<pid>/smaps_rollup
```

### 메모리 영역 구조

```
High Address
┌─────────────────┐
│   kernel space  │  <- kernel only (no user access)
├─────────────────┤ 0xFFFF...
│   stack         │  <- grows down, local vars
│       v         │
│                 │
│       ^         │
│   heap          │  <- grows up, malloc()
├─────────────────┤
│   BSS           │  <- uninitialized global vars
│   data          │  <- initialized global vars
│   text          │  <- executable code (read-only)
└─────────────────┘
Low Address  0x0000
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Page fault

가상 주소에 접근했을 때 물리 메모리가 없으면 커널이 처리합니다.

### 종류

| 종류          | 원인                                | 처리                     |
|---------------|-------------------------------------|--------------------------|
| Minor fault   | 페이지가 메모리에 있지만 매핑 안 됨 | 페이지 테이블만 업데이트 |
| Major fault   | 페이지가 디스크(swap)에 있음        | 디스크에서 읽어옴 (느림) |
| Invalid fault | 잘못된 주소 접근                    | SIGSEGV 발생             |

```bash
# 프로세스 page fault 통계
cat /proc/<pid>/stat | awk '{print "minor:", $10, "major:", $12}'

# 시스템 전체
vmstat 1
# pgfault  = minor fault/s
# pgmajfault = major fault/s
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. Page cache

디스크 I/O를 줄이기 위해 커널이 파일 내용을 메모리에 캐싱합니다.

```bash
# 캐시 사용량 확인
free -h
#               total   used   free   shared  buff/cache  available
# Mem:           15Gi   3.2Gi  8.1Gi   512Mi       4.1Gi       11Gi
#                                               ^^^^^^^^^^
#                                               page cache + buffer

cat /proc/meminfo | grep -E "Cached|Buffers|Dirty|Writeback"
# Buffers:        512 kB   <- 블록 디바이스 버퍼
# Cached:       4096 MB    <- 파일 page cache
# Dirty:          64 MB    <- 수정됐지만 미기록 페이지
# Writeback:       0 kB    <- 현재 디스크에 쓰는 중
```

### Dirty page 제어

```bash
# dirty page 비율 한도 (전체 메모리 대비 %)
cat /proc/sys/vm/dirty_ratio          # 기본 20% — 초과 시 쓰기 블록
cat /proc/sys/vm/dirty_background_ratio  # 기본 10% — 초과 시 백그라운드 flush

# flush 주기 (100분의 1초 단위, 기본 500 = 5초)
cat /proc/sys/vm/dirty_writeback_centisecs

# 캐시 강제 해제 (긴급 시만 사용)
sync && echo 3 > /proc/sys/vm/drop_caches
# 1=page cache, 2=dentries/inodes, 3=전체
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Swap

물리 메모리 부족 시 사용 빈도 낮은 페이지를 디스크로 이동합니다.

```bash
# swap 확인
swapon --show
free -h

# swap 파일 생성
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 영구 적용
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# swappiness — 낮을수록 RAM 우선 사용 (기본 60)
cat /proc/sys/vm/swappiness
echo 10 > /proc/sys/vm/swappiness
```

### swap 사용량 프로세스별 확인

```bash
# 프로세스별 swap 사용량
for pid in /proc/[0-9]*; do
    swap=$(grep VmSwap $pid/status 2>/dev/null | awk '{print $2}')
    [ "${swap:-0}" -gt 0 ] && echo "$swap kB $(cat $pid/comm 2>/dev/null)"
done | sort -rn | head -10
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Copy-on-Write

`fork()` 후 부모/자식이 같은 물리 페이지를 공유하다가, 쓰기 발생 시 복사합니다.

```
after fork():
  parent ──┐
           ├── same physical page (shared, read-only)
  child  ──┘

child modifies page:
  parent ──── original page (unchanged)
  child  ──── new copy page (modified)
```

```bash
# CoW 효과 확인 — fork 직후 RSS가 거의 증가 안 함
python3 -c "
import os, time
print('before fork:', open('/proc/self/status').read().split('VmRSS')[1].split()[1], 'kB')
pid = os.fork()
if pid == 0:
    time.sleep(1)
    os._exit(0)
print('after fork:', open('/proc/self/status').read().split('VmRSS')[1].split()[1], 'kB')
os.wait()
"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 메모리 확인 명령어

```bash
# 전체 현황
free -h
vmstat -s | head -15

# 프로세스별 실제 사용량 (PSS 기준)
# PSS = 프로세스 고유 메모리 + 공유 메모리 / 공유 프로세스 수
sudo smem -r -k | head -15   # apt install smem

# /proc/meminfo 주요 항목
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable|Cached|SwapTotal|SwapFree"
# MemAvailable: 실제 사용 가능한 메모리 (캐시 회수 가능분 포함)

# 메모리 누수 추적
watch -n 2 'ps aux --sort=-%mem | head -10'
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

### 메모리 부족 징후

```bash
# OOM 발생 확인
dmesg | grep -i "oom\|killed"

# swap 과다 사용 (major fault 증가)
vmstat 1 | awk '{print $7, $8, $9, $10}'
# si(swap in) so(swap out) 값이 크면 swap thrashing

# 메모리 압박 지표
cat /proc/pressure/memory
# some avg10=5.00 avg60=2.00 avg300=1.00
# full avg10=0.00 avg60=0.00 avg300=0.00
```

### 자주 하는 실수

| 실수                       | 결과                 | 올바른 방법            |
|----------------------------|----------------------|------------------------|
| `free` 의 `free` 컬럼만 봄 | 메모리 부족으로 오해 | `available` 컬럼 확인  |
| `drop_caches` 남용         | 성능 저하            | 긴급 시만 사용         |
| swap 없이 운영             | OOM 즉시 kill        | 최소 RAM 50% swap 확보 |
| `swappiness=0` 설정        | swap 비활성화 위험   | `10` 권장              |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux Kernel Docs: [kernel.org/doc/html/latest/admin-guide/mm](https://www.kernel.org/doc/html/latest/admin-guide/mm/) — ★★★☆☆
- [oom_hang.md](../08_debugging_linux/oom_hang.md)
- [cgroup.md](cgroup.md)

---

**작성일** : 2026-05-21

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
