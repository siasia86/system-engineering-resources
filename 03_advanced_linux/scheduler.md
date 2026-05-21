# Linux Scheduler — CPU 스케줄러

Linux CFS(Completely Fair Scheduler)와 CPU 스케줄링 메커니즘을 정리합니다.

## 목차

| 섹션                                                                                                           |
|----------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. CFS 동작 원리](#2-cfs-동작-원리) / [3. 스케줄링 정책](#3-스케줄링-정책)               |
| [4. CPU 친화성](#4-cpu-친화성) / [5. 우선순위와 nice](#5-우선순위와-nice) / [6. 확인 및 튜닝](#6-확인-및-튜닝) |

---

## 1. 개요

Linux 스케줄러는 여러 프로세스가 CPU를 공정하게 나눠 쓰도록 관리합니다.

```
Run Queue (per CPU)
┌─────────────────────────────┐
│  Red-Black Tree             │
│  (sorted by vruntime)       │
│                             │
│  P1(vrt=100) P2(vrt=150)    │
│  P3(vrt=200) ...            │
└─────────────────────────────┘
         │
         v
    select process with smallest vruntime -> assign CPU
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. CFS 동작 원리

### vruntime (가상 실행 시간)

CFS는 각 프로세스의 **vruntime** (가상 실행 시간)을 추적합니다. vruntime이 가장 작은 프로세스를 다음에 실행합니다.

```
vruntime 증가량 = 실제 실행 시간 × (기본 가중치 / 프로세스 가중치)

nice=0  (기본): vruntime 증가 = 실제 시간 × 1.0
nice=-5 (높은 우선순위): vruntime 증가 = 실제 시간 × 0.5  (더 오래 실행)
nice=+5 (낮은 우선순위): vruntime 증가 = 실제 시간 × 2.0  (더 짧게 실행)
```

### 타임슬라이스

```bash
# 스케줄링 레이턴시 (모든 프로세스가 한 번씩 실행되는 목표 시간)
cat /proc/sys/kernel/sched_latency_ns        # 기본 6ms~24ms

# 최소 실행 시간 (너무 잦은 컨텍스트 스위치 방지)
cat /proc/sys/kernel/sched_min_granularity_ns  # 기본 0.75ms
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 스케줄링 정책

```bash
# 프로세스 스케줄링 정책 확인
chrt -p <pid>
# pid 1234's current scheduling policy: SCHED_OTHER
# pid 1234's current scheduling priority: 0
```

| 정책                | 값   | 대상          | 특징                             |
|---------------------|------|---------------|----------------------------------|
| `SCHED_OTHER` (CFS) | 0    | 일반 프로세스 | nice 기반 공정 분배              |
| `SCHED_BATCH`       | 0    | 배치 작업     | CPU 집약적, 인터랙티브 양보      |
| `SCHED_IDLE`        | 0    | 백그라운드    | 가장 낮은 우선순위               |
| `SCHED_FIFO`        | 1~99 | 실시간        | 선점 없음, 우선순위 높은 것 먼저 |
| `SCHED_RR`          | 1~99 | 실시간        | FIFO + 타임슬라이스              |
| `SCHED_DEADLINE`    | 0    | 실시간        | 데드라인 기반 (별도 attr 설정)   |

```bash
# 실시간 정책으로 변경 (우선순위 50)
chrt -f -p 50 <pid>   # SCHED_FIFO
chrt -r -p 50 <pid>   # SCHED_RR

# 배치 정책으로 변경 (백업 스크립트 등)
chrt -b -p 0 <pid>
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. CPU 친화성

특정 프로세스를 특정 CPU 코어에 고정합니다.

```bash
# 현재 CPU 친화성 확인
taskset -p <pid>
# pid 1234's current affinity mask: ff  (모든 코어)

# CPU 0,1 에만 실행
taskset -p 0x3 <pid>      # 비트마스크 방식
taskset -cp 0,1 <pid>     # 코어 번호 방식

# 처음부터 특정 CPU에서 실행
taskset -c 0,1 ./myapp

# NUMA 노드 고려 (멀티소켓 서버)
numactl --cpunodebind=0 --membind=0 ./myapp
```

```bash
# CPU 토폴로지 확인
lscpu | grep -E "CPU\(s\)|Thread|Core|Socket|NUMA"
cat /proc/cpuinfo | grep "processor\|physical id\|core id" | head -20
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 우선순위와 nice

```bash
# nice 값 확인 (-20 ~ +19, 낮을수록 높은 우선순위)
ps -o pid,ni,pri,comm -p <pid>

# nice 값으로 실행
nice -n 10 ./backup.sh      # 낮은 우선순위로 실행
nice -n -5 ./critical.sh    # 높은 우선순위 (root 필요)

# 실행 중인 프로세스 nice 변경
renice -n 10 -p <pid>
renice -n 10 -u username    # 특정 사용자 전체

# nice vs priority 관계
# priority = 20 + nice  (nice=0 → priority=20)
# 커널 내부 priority: 0~139 (0~99=실시간, 100~139=일반)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 확인 및 튜닝

### 스케줄러 통계

```bash
# CPU 사용률 및 컨텍스트 스위치
vmstat 1
# cs 컬럼 = 초당 컨텍스트 스위치 수

# 프로세스별 컨텍스트 스위치
cat /proc/<pid>/status | grep ctxt
# voluntary_ctxt_switches:    100   <- 자발적 (I/O 대기 등)
# nonvoluntary_ctxt_switches:  10   <- 비자발적 (타임슬라이스 만료)

# CPU별 실행 큐 길이
mpstat -P ALL 1
sar -q 1 5   # runq-sz 컬럼

# 실시간 스케줄러 통계
cat /proc/schedstat
```

### 스케줄러 튜닝

```bash
# 컨텍스트 스위치 과다 시 — 타임슬라이스 늘리기
echo 12000000 > /proc/sys/kernel/sched_latency_ns      # 12ms
echo 1500000  > /proc/sys/kernel/sched_min_granularity_ns

# 실시간 프로세스가 CPU 독점 방지
cat /proc/sys/kernel/sched_rt_runtime_us   # 기본 950000 (95%)
# -1 로 설정 시 실시간 프로세스 무제한 (위험)
```

### 자주 하는 실수

| 실수                       | 결과               | 올바른 방법             |
|----------------------------|--------------------|-------------------------|
| 모든 프로세스 `SCHED_FIFO` | 시스템 hang        | 실시간 필요한 것만 적용 |
| `nice -20` 남용            | 다른 프로세스 기아 | 필요한 경우만           |
| CPU 친화성 고정 과다       | NUMA 불균형        | 토폴로지 파악 후 적용   |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux Kernel Docs: [kernel.org/doc/html/latest/scheduler](https://www.kernel.org/doc/html/latest/scheduler/) — ★★★☆☆
- [cgroup.md](cgroup.md)

---

**작성일** : 2026-05-21

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
