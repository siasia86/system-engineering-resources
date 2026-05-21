# OOM / Hang 트러블슈팅

Linux 시스템에서 발생하는 OOM(Out of Memory)과 Hang(응답 없음) 현상의 개념, 원인, 대처 방안을 정리합니다.

## 목차

| 섹션 |
|------|
| [1. OOM 개념](#1-oom-개념) / [2. Hang 개념](#2-hang-개념) / [3. 원인 분석](#3-원인-분석) |
| [4. 대처 방안](#4-대처-방안) / [5. 예방 설정](#5-예방-설정) / [6. 실무 TIP](#6-실무-tip) |

---

## 1. OOM 개념

OOM(Out of Memory)은 커널이 메모리 할당 요청을 처리할 수 없을 때 발생합니다.

### 발생 흐름

```
메모리 부족 감지
       │
       v
  OOM killer 실행
       │
       v
  oom_score 계산 (프로세스별)
       │
       v
  점수 가장 높은 프로세스 kill
```

### oom_score 계산

커널이 각 프로세스에 0~1000 점수를 부여합니다. 점수가 높을수록 먼저 kill됩니다.

```bash
# 현재 점수 확인
cat /proc/<pid>/oom_score        # 커널 계산 점수 (0~1000)
cat /proc/<pid>/oom_score_adj    # 관리자 조정값 (-1000~+1000)
```

| `oom_score_adj` 값 | 의미 |
|--------------------|------|
| `-1000` | OOM killer 대상 제외 (절대 kill 안 함) |
| `-500` | kill 가능성 낮춤 |
| `0` | 기본값 |
| `+500` | kill 가능성 높임 |
| `+1000` | 가장 먼저 kill |

### OOM 발생 확인

```bash
dmesg | grep -i "oom\|killed\|out of memory"
journalctl -k | grep -i oom
grep -i "oom killer" /var/log/syslog
```

출력 예시:

```
Out of memory: Kill process 1234 (java) score 892 or sacrifice child
Killed process 1234 (java) total-vm:2048000kB, anon-rss:1024000kB
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Hang 개념

Hang은 프로세스 또는 시스템이 응답하지 않는 상태입니다. OOM과 달리 프로세스가 살아있지만 진행이 멈춥니다.

### Hang 유형

| 유형 | 원인 | 특징 |
|------|------|------|
| D state (Uninterruptible Sleep) | I/O 대기, NFS hang | `kill -9`도 안 됨 |
| Deadlock | 락 경합 | CPU 0%, 진행 없음 |
| Livelock | 무한 재시도 | CPU 100%, 진행 없음 |
| Swap thrashing | 메모리 부족 + swap 과다 | 극심한 I/O, 응답 불가 |
| OOM 후 hang | `-1000` 설정 프로세스 메모리 누수 | 시스템 전체 응답 불가 |

### D state 프로세스 확인

```bash
# D 상태 프로세스 목록
ps aux | awk '$8 == "D"'

# 상세 확인
cat /proc/<pid>/wchan    # 어떤 커널 함수에서 대기 중인지
cat /proc/<pid>/status | grep State
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 원인 분석

### 메모리 현황 파악

```bash
# 전체 메모리 현황
free -h
vmstat -s | head -20

# 프로세스별 메모리 사용량 (상위 10개)
ps aux --sort=-%mem | head -11

# 메모리 상세 (캐시/버퍼 포함)
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree|Cached|Buffers"

# cgroup 메모리 확인
cat /sys/fs/cgroup/<service>/memory.current
cat /sys/fs/cgroup/<service>/memory.max
```

### 메모리 누수 의심 프로세스 추적

```bash
# 시간별 메모리 증가 추적
watch -n 5 'ps aux --sort=-%mem | head -6'

# smaps로 상세 메모리 맵 확인
cat /proc/<pid>/smaps | grep -E "^(Rss|Pss|Swap):" | awk '{sum+=$2} END {print sum/1024 " MB"}'
```

### I/O hang 원인 파악

```bash
# I/O 대기 확인
iostat -x 1 5
iotop -o

# 어떤 파일/소켓에서 대기 중인지
lsof -p <pid>
strace -p <pid> -e trace=read,write,open
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 대처 방안

### OOM 발생 시

```bash
# 1. 원인 프로세스 확인
dmesg | grep -i "killed process"

# 2. 즉시 메모리 확보 (캐시 해제)
sync && echo 3 > /proc/sys/vm/drop_caches

# 3. 메모리 많이 쓰는 프로세스 재시작 또는 kill
kill -9 <pid>

# 4. swap 임시 추가
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### 중요 프로세스 OOM kill 방지

```bash
# 임시 (재부팅 시 초기화)
echo -1000 > /proc/<pid>/oom_score_adj

# 영구 (systemd 서비스)
# /etc/systemd/system/<service>.service
# [Service]
# OOMScoreAdjust=-500
systemctl daemon-reload
```

⚠️ `-1000` 설정 시 해당 프로세스가 메모리 누수를 일으키면 시스템 전체 hang으로 이어질 수 있습니다.

### cgroup으로 메모리 제한 (OOM 격리)

```bash
# 특정 서비스 메모리 한도 설정 (systemd)
systemctl set-property <service> MemoryMax=512M
systemctl set-property <service> MemorySwapMax=1G

# 직접 cgroup 설정
echo $((512 * 1024 * 1024)) > /sys/fs/cgroup/<group>/memory.max
echo $((1024 * 1024 * 1024)) > /sys/fs/cgroup/<group>/memory.swap.max  # swap 전용 1GB 한도
```

### Hang 프로세스 대처

```bash
# D state는 kill -9도 안 됨 — I/O 완료 대기 필요
# NFS hang이면 마운트 해제 시도
umount -f -l /mnt/nfs

# sysrq로 hang 상태 덤프 (커널 레벨)
echo w > /proc/sysrq-trigger   # D state 프로세스 전체 출력
echo t > /proc/sysrq-trigger   # 모든 태스크 스택 덤프
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 예방 설정

### vm.overcommit 설정

```bash
# 현재 설정 확인
cat /proc/sys/vm/overcommit_memory
# 0: 휴리스틱 (기본) — 어느 정도 overcommit 허용
# 1: 항상 허용 — OOM 위험 높음
# 2: 엄격 제한 — swap + RAM * ratio 초과 불가

# 권장 (운영 서버)
echo 2 > /proc/sys/vm/overcommit_memory
echo 80 > /proc/sys/vm/overcommit_ratio   # RAM의 80%까지만 허용

# 영구 적용
echo "vm.overcommit_memory=2" >> /etc/sysctl.conf
echo "vm.overcommit_ratio=80" >> /etc/sysctl.conf
sysctl -p
```

### vm.swappiness 조정

```bash
# 기본값 60 — 메모리 여유 있어도 swap 사용
# 낮출수록 RAM 우선 사용
echo 10 > /proc/sys/vm/swappiness

# 영구 적용
echo "vm.swappiness=10" >> /etc/sysctl.conf
```

### OOM 발생 시 자동 재부팅 (최후 수단)

```bash
# sysctl 설정
echo "kernel.panic_on_oom=1" >> /etc/sysctl.conf
echo "kernel.panic=30" >> /etc/sysctl.conf   # 30초 후 재부팅
sysctl -p
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실무 TIP

### 모니터링 명령 모음

```bash
# 실시간 메모리 + swap 사용률
watch -n 2 'free -h && echo "---" && swapon --show'

# OOM 발생 실시간 감시
journalctl -kf | grep -i oom

# 프로세스별 실제 메모리 사용량 (PSS 기준, 공유 메모리 포함)
# smem 설치: apt install smem / dnf install smem
sudo smem -r -k | head -15
```

### 자주 하는 실수

| 실수 | 결과 | 올바른 방법 |
|------|------|-------------|
| 중요 프로세스 전부 `-1000` 설정 | 시스템 hang | 핵심 1~2개만 설정 |
| swap 없이 운영 | OOM 즉시 kill | 최소 RAM의 50% swap 확보 |
| `drop_caches` 남용 | 성능 저하 | 캐시는 커널이 관리, 긴급 시만 사용 |
| `overcommit=1` 운영 서버 적용 | OOM 빈발 | `overcommit=2` + ratio 조정 |

### cgroup v2 메모리 관련 파일 정리

| 파일 | 단위 | 설명 |
|------|------|------|
| `memory.current` | bytes | 현재 사용량 |
| `memory.max` | bytes | 하드 한도 (초과 시 OOM) |
| `memory.high` | bytes | 소프트 한도 (초과 시 throttle) |
| `memory.swap.max` | bytes | swap 전용 한도 (memory 제외, swap만 계산) |
| `memory.oom_control` | - | OOM killer 동작 제어 |
| `pids.current` | 개수 | 현재 프로세스+스레드 수 |
| `pids.max` | 개수 | 최대 허용 수 |

### 장애 대응 순서

```
1. dmesg / journalctl 로 OOM 로그 확인
2. 어떤 프로세스가 kill 됐는지 확인
3. 해당 프로세스 메모리 사용 추이 확인 (누수 여부)
4. 임시: swap 추가 또는 메모리 확보
5. 근본: 메모리 누수 수정 또는 서버 스케일업
6. 예방: cgroup 한도 설정, 모니터링 알람 추가
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux Kernel Docs: [kernel.org/doc/html/latest/admin-guide/mm/concepts.html](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html) — ★★★☆☆
- Red Hat: [access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_monitoring_and_updating_the_kernel/](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_monitoring_and_updating_the_kernel/) — ★★★☆☆
- [lsof.md](lsof.md)
- [perf.md](perf.md)

---

**작성일**: 2026-05-21

**마지막 업데이트**: 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
