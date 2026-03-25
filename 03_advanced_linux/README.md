# 고급 Linux 시스템 관리

고급 Linux 시스템 관리, 성능 튜닝, eBPF 기반 추적 도구에 대한 문서입니다.

## 문서 목록

### eBPF & 추적
- **[bpftrace](bpftrace.md)** - eBPF 기반 동적 추적 도구

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

## 관련 문서

- [Linux 디버깅 도구](../08_debugging_linux/) - strace, perf 등
- [시스템 엔지니어링](../04_system_engineer/) - 로드맵

---

## 참고 자료

- [bpftrace GitHub](https://github.com/iovisor/bpftrace)
- [eBPF 공식 문서](https://ebpf.io/)
- [BPF Performance Tools](http://www.brendangregg.com/bpf-performance-tools-book.html)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)

---

**마지막 업데이트**: 2026-03-25

© 2026 siasia86. Licensed under CC BY 4.0.
