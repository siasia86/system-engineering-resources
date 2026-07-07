# eBPF — Extended Berkeley Packet Filter

커널 코드 수정 없이 커널 내부를 동적으로 추적·필터링하는 기술을 정리합니다.

## 목차

| 섹션                                                                                     |
|------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 동작 원리](#2-동작-원리) / [3. 프로그램 타입](#3-프로그램-타입) |
| [4. 주요 도구](#4-주요-도구) / [5. bpftool](#5-bpftool) / [6. 실무 활용](#6-실무-활용)   |

---

## 1. 개요

eBPF는 커널 소스 수정이나 모듈 로드 없이 커널 이벤트에 훅을 걸어 코드를 실행하는 기술입니다.

```
User Space                    Kernel Space
┌──────────────┐              ┌─────────────────────────┐
│ eBPF program │  load/verify │  eBPF VM (JIT compiled) │
│ (C or Python)│ ──────────>  │                         │
└──────────────┘              │  hook points:           │
                              │  - syscall entry/exit   │
                              │  - kprobe/tracepoint    │
                              │  - network packet       │
                              │  - perf event           │
                              └─────────────────────────┘
```

| 특징     | 설명                                         |
|----------|----------------------------------------------|
| 안전성   | 로드 전 verifier가 무한루프·메모리 오류 검사 |
| 성능     | JIT 컴파일로 네이티브 코드 수준              |
| 범용성   | 네트워킹, 보안, 추적, 프로파일링 모두 가능   |
| 비침투적 | 커널 재컴파일·재부팅 불필요                  |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 동작 원리

```
1. write eBPF program (C or Python/Go wrapper)
        │
        v
2. compile to eBPF bytecode (LLVM/clang)
        │
        v
3. load into kernel via bpf() syscall
        │
        v
4. Verifier check (safety guaranteed)
        │
        v
5. JIT compile (x86/ARM native code)
        │
        v
6. attach to hook point -> execute on event
        │
        v
7. exchange data with user space via Map
```

### eBPF Map

커널과 유저 공간 간 데이터 공유 구조체입니다.

| Map 타입                        | 용도             |
|---------------------------------|------------------|
| `BPF_MAP_TYPE_HASH`             | 키-값 저장       |
| `BPF_MAP_TYPE_ARRAY`            | 인덱스 기반 배열 |
| `BPF_MAP_TYPE_PERF_EVENT_ARRAY` | 이벤트 스트림    |
| `BPF_MAP_TYPE_RINGBUF`          | 고성능 링 버퍼   |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 프로그램 타입

| 타입         | 훅 위치                | 주요 용도          |
|--------------|------------------------|--------------------|
| `kprobe`     | 커널 함수 진입/반환    | 함수 호출 추적     |
| `tracepoint` | 커널 정적 추적점       | 안정적 이벤트 추적 |
| `uprobe`     | 유저 함수 진입/반환    | 앱 레벨 추적       |
| `XDP`        | 네트워크 드라이버 수신 | 고성능 패킷 처리   |
| `TC`         | 네트워크 트래픽 제어   | 패킷 필터링/수정   |
| `LSM`        | 보안 훅                | 접근 제어          |
| `perf_event` | 하드웨어 카운터        | CPU 프로파일링     |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 도구

### bpftrace

고수준 추적 언어입니다. 자세한 내용은 [bpftrace.md](bpftrace.md) 참고.

```bash
# 시스템 콜 빈도
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# 프로세스별 read() 크기 분포
bpftrace -e 'tracepoint:syscalls:sys_exit_read /args->ret > 0/ { @[comm] = hist(args->ret); }'
```

### BCC (BPF Compiler Collection)

Python 래퍼로 eBPF 프로그램을 작성합니다.

```bash
# 설치
apt install bpfcc-tools linux-headers-$(uname -r)

# 주요 도구
execsnoop-bpfcc          # 프로세스 실행 추적
opensnoop-bpfcc          # 파일 open() 추적
tcpconnect-bpfcc         # TCP 연결 추적
biolatency-bpfcc         # 블록 I/O 지연 분포
runqlat-bpfcc            # CPU 실행 큐 대기 시간
```

### Cilium / Falco

```bash
# Cilium: eBPF 기반 Kubernetes 네트워킹/보안
# Falco: eBPF 기반 런타임 보안 감사
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. bpftool

로드된 eBPF 프로그램과 맵을 관리합니다.

```bash
# 설치
apt install linux-tools-$(uname -r)

# 로드된 eBPF 프로그램 목록
bpftool prog list

# eBPF 맵 목록
bpftool map list

# 맵 내용 조회
bpftool map dump id <map_id>

# 프로그램 상세 (JIT 코드 포함)
bpftool prog dump xlated id <prog_id>

# 네트워크 인터페이스에 연결된 eBPF 확인
bpftool net list
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실무 활용

### 성능 분석

```bash
# CPU 프로파일링 (60초)
profile-bpfcc -F 99 60 > /tmp/profile.txt

# 블록 I/O 지연 분포
biolatency-bpfcc -D 10

# TCP 재전송 추적
tcpretrans-bpfcc
```

### 보안 감사

```bash
# 파일 접근 감사
opensnoop-bpfcc -p <pid>

# 네트워크 연결 감사
tcpconnect-bpfcc
tcpaccept-bpfcc

# 권한 상승 시도 감사
capable-bpfcc
```

### 커널 버전 요구사항

| 기능            | 최소 커널 버전 |
|-----------------|----------------|
| eBPF 기본       | 3.18           |
| kprobe          | 4.1            |
| tracepoint      | 4.7            |
| XDP             | 4.8            |
| BTF (타입 정보) | 4.18           |
| CO-RE (이식성)  | 5.2            |

```bash
# 현재 커널 eBPF 지원 확인
uname -r
bpftool feature probe
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- eBPF.io: [ebpf.io/what-is-ebpf](https://ebpf.io/what-is-ebpf/) — ★★★☆☆
- BCC Tools: [github.com/iovisor/bcc](https://github.com/iovisor/bcc) — ★★★☆☆
- [bpftrace.md](bpftrace.md)

---

**작성일** : 2026-05-21

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
