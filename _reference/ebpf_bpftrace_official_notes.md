---
name: ebpf-bpftrace-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man2/bpf.2.html
  - https://docs.kernel.org/bpf/libbpf/index.html
  - https://ebpf.io/what-is-ebpf/
  - https://github.com/bpftrace/bpftrace
  - https://github.com/libbpf/libbpf
---

# eBPF / bpftrace 공식 참조 노트

## 1. eBPF 개요

### 공식 소스

| 소스            | URL                                              | 용도                       |
|-----------------|--------------------------------------------------|----------------------------|
| bpf.2 man page  | https://man7.org/linux/man-pages/man2/bpf.2.html | BPF syscall, 프로그램 타입 |
| kernel BPF docs | https://docs.kernel.org/bpf/libbpf/index.html    | libbpf API                 |
| ebpf.io         | https://ebpf.io/what-is-ebpf/                    | eBPF 개념, verifier, JIT   |

### 검증된 사실 (2026-08-01)

| 항목              | 값                                                          | 출처            |
|-------------------|-------------------------------------------------------------|-----------------|
| verifier          | 프로그램 로드 시 커널 내 정적 검증 수행                     | bpf.2 man page  |
| JIT 컴파일        | verifier 통과 후 native 코드로 컴파일                       | ebpf.io         |
| libbpf 최신 버전  | v1.7.0 (2026-03-16)                                         | GitHub API      |
| bpftrace 최신버전 | v0.26.1 (2026-06-02)                                        | GitHub API      |
| kernel 버전       | docs.kernel.org 기준 7.2.0-rc5 (최신 stable 별도 확인 필요) | docs.kernel.org |

## 2. BPF Map 타입 (bpf.2 man page 기반)

### 공식 소스

| 소스           | URL                                              | 용도          |
|----------------|--------------------------------------------------|---------------|
| bpf.2 man page | https://man7.org/linux/man-pages/man2/bpf.2.html | Map 타입 목록 |

### 검증된 사실 (2026-08-01)

| BPF_MAP_TYPE                  | 설명                         | 출처           |
|-------------------------------|------------------------------|----------------|
| BPF_MAP_TYPE_HASH             | 해시 테이블                  | bpf.2 man page |
| BPF_MAP_TYPE_ARRAY            | 배열 (고정 크기)             | bpf.2 man page |
| BPF_MAP_TYPE_PERCPU_HASH      | CPU별 해시                   | bpf.2 man page |
| BPF_MAP_TYPE_PERCPU_ARRAY     | CPU별 배열                   | bpf.2 man page |
| BPF_MAP_TYPE_PROG_ARRAY       | 프로그램 배열 (tail call)    | bpf.2 man page |
| BPF_MAP_TYPE_PERF_EVENT_ARRAY | perf 이벤트 버퍼             | bpf.2 man page |
| BPF_MAP_TYPE_STACK_TRACE      | 스택 트레이스 저장           | bpf.2 man page |
| BPF_MAP_TYPE_QUEUE            | FIFO 큐                      | bpf.2 man page |
| BPF_MAP_TYPE_STACK            | LIFO 스택                    | bpf.2 man page |
| BPF_MAP_TYPE_LRU_HASH         | LRU 해시 (자동 eviction)     | bpf.2 man page |
| BPF_MAP_TYPE_LPM_TRIE         | 최장 접두사 매칭 (IP 라우팅) | bpf.2 man page |
| BPF_MAP_TYPE_SOCKMAP          | 소켓 맵 (socket redirect)    | bpf.2 man page |

## 3. bpftrace 프로브 타입

### 공식 소스

| 소스            | URL                                  | 용도              |
|-----------------|--------------------------------------|-------------------|
| bpftrace GitHub | https://github.com/bpftrace/bpftrace | 공식 레포, README |

### 검증된 사실 (2026-08-01)

| 프로브 타입 | 문법                           | 설명                       | 출처            |
|-------------|--------------------------------|----------------------------|-----------------|
| kprobe      | `kprobe:함수명`                | 커널 함수 진입 추적        | bpftrace GitHub |
| kretprobe   | `kretprobe:함수명`             | 커널 함수 리턴 추적        | bpftrace GitHub |
| uprobe      | `uprobe:바이너리:함수`         | 유저스페이스 함수 추적     | bpftrace GitHub |
| tracepoint  | `tracepoint:서브시스템:이벤트` | 커널 정적 추적점           | bpftrace GitHub |
| software    | `software:이벤트:횟수`         | 소프트웨어 이벤트          | bpftrace GitHub |
| hardware    | `hardware:이벤트:횟수`         | 하드웨어 PMU 이벤트        | bpftrace GitHub |
| profile     | `profile:hz:N`                 | N Hz 주기 샘플링           | bpftrace GitHub |
| interval    | `interval:s:N`                 | N초 주기 실행              | bpftrace GitHub |
| BEGIN/END   | `BEGIN`, `END`                 | 스크립트 시작/종료 시 실행 | bpftrace GitHub |

## 4. eBPF 활용 도구

### 검증된 사실 (2026-08-01)

| 도구     | 기반 | 주요 용도                            | 출처            |
|----------|------|--------------------------------------|-----------------|
| bpftrace | eBPF | 동적 추적, 원라이너                  | bpftrace GitHub |
| libbpf   | eBPF | C 언어 eBPF 프로그래밍 라이브러리    | libbpf GitHub   |
| Cilium   | eBPF | 컨테이너 네트워크 (netfilter bypass) | ebpf.io         |
| Falco    | eBPF | 런타임 보안 감사                     | ebpf.io         |
| Katran   | eBPF | Facebook L4 로드밸런서               | ebpf.io         |

🟡 Cilium은 eBPF/XDP 기반으로 netfilter를 bypass합니다 (출처: ebpf.io).

## 5. deprecated / removed

| 항목                          | 상태                                         | 출처     |
|-------------------------------|----------------------------------------------|----------|
| classic BPF(cBPF)             | 소켓 필터 용도로만 유지, 신규 개발 eBPF 권장 | bpf.2    |
| bcc (BPF Compiler Collection) | bpftrace/libbpf로 대체 권장                  | 커뮤니티 |

## 6. Security recommendations

| 항목                 | 권장 사항                                          | 출처    |
|----------------------|----------------------------------------------------|---------|
| CAP_BPF (Linux 5.8+) | eBPF 프로그램 로드에 CAP_SYS_ADMIN 대신 사용 권장  | bpf.2   |
| unprivileged BPF     | /proc/sys/kernel/unprivileged_bpf_disabled 로 제어 | bpf.2   |
| verifier             | 무한루프/잘못된 메모리 접근 정적 차단              | ebpf.io |
