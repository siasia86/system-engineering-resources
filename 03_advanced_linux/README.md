# 고급 Linux 시스템 관리

고급 Linux 시스템 관리, 성능 튜닝, eBPF 기반 추적 도구에 대한 문서입니다.

## 목차

| 섹션 |
|------|
| [문서 목록](#문서-목록) / [학습 가이드](#학습-가이드) / [실전 활용](#실전-활용) |

---

## 문서 목록

### 프로세스 & 메모리
- **[Process Lifecycle](process_lifecycle.md)** - fork / exec / wait / exit
- **[Linux Scheduler](scheduler.md)** - CPU 스케줄러
- **[Virtual Memory](virtual_memory.md)** - 가상 메모리
- **[IPC](ipc.md)** - 프로세스 간 통신

### 커널 & 격리
- **[cgroup](cgroup.md)** - 리소스 제한 및 격리
- **[Linux Namespace](namespace.md)** - 프로세스 격리 (PID, NET, MNT 등)
- **[Seccomp / Capabilities](seccomp_capabilities.md)** - 컨테이너 보안

### 파일시스템 & 네트워크
- **[/proc & /sys](linux_virtual_fs.md)** - Linux 가상 파일시스템
- **[netfilter / tc](netfilter_tc.md)** - 네트워크 제어

### eBPF & 추적
- **[eBPF](ebpf.md)** - Extended Berkeley Packet Filter
- **[bpftrace](bpftrace.md)** - eBPF 기반 동적 추적 도구

[⬆ 목차로 돌아가기](#목차)

---

## 학습 가이드

### eBPF란?
Extended Berkeley Packet Filter의 약자로, Linux 커널에서 안전하게 프로그램을 실행할 수 있는 기술입니다.

**주요 용도:**
- 성능 분석
- 네트워크 모니터링
- 보안 감사
- 시스템 추적

### bpftrace 시작하기

```bash
# 설치 (Ubuntu/Debian)
sudo apt install bpftrace

# 간단한 예제: 시스템 콜 추적
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# 파일 열기 추적
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'
```

[⬆ 목차로 돌아가기](#목차)

---

## 실전 활용

### 성능 병목 찾기

```bash
# CPU 사용률이 높은 함수 찾기
sudo bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'

# 디스크 I/O 지연 측정
sudo bpftrace -e 'tracepoint:block:block_rq_issue { @start[args->dev, args->sector] = nsecs; }
tracepoint:block:block_rq_complete /@start[args->dev, args->sector]/ {
    @usecs = hist((nsecs - @start[args->dev, args->sector]) / 1000);
    delete(@start[args->dev, args->sector]);
}'
```

---

## 참고 자료

- bpftrace GitHub: [github.com/iovisor/bpftrace](https://github.com/iovisor/bpftrace) — ★★☆☆☆
- eBPF 공식 문서: [ebpf.io](https://ebpf.io/) — ★★☆☆☆
- Gregg, Brendan. "BPF Performance Tools" — ★★★☆☆

---

[문서 전체 로드맵](../README.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-11

**마지막 업데이트**: 2026-05-25

© 2026 siasia86. Licensed under CC BY 4.0.
