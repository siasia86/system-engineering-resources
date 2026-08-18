# Linux 기초 문서

Linux 운영체제의 기본 개념과 시스템 운영 도구를 단계적으로 학습하는 문서 모음입니다. Shell, 프로세스, 메모리, 파일시스템, 저장장치, 커널, 디버깅과 보안 기초를 다룹니다.

## 목차

| 섹션                                                                  |
|-----------------------------------------------------------------------|
| [1. 문서 구성](#1-문서-구성) / [2. 추천 학습 순서](#2-추천-학습-순서) |
| [3. 주제별 문서](#3-주제별-문서) / [4. 관련 섹션](#4-관련-섹션)       |

---

## 1. 문서 구성

현재 Linux 문서는 `README.md`를 제외하고 47개입니다. 개념 문서와 실습·분석 도구 문서를 함께 배치하여 개념 학습 후 실제 시스템 관찰로 이어지도록 구성합니다.

| 주제                     | 범위                                  |
|--------------------------|---------------------------------------|
| Shell·CLI                | Bash, 셸 모드, 리다이렉션, 신호 처리  |
| 프로세스·메모리·스케줄러 | 프로세스 수명, IPC, 가상 메모리, OOM  |
| 파일시스템·저장장치      | VFS, 파일시스템, 디스크·I/O 도구      |
| 디버깅·프로파일링        | strace, perf, GDB, eBPF, 메모리 분석  |
| 커널·보안·격리           | cgroup, namespace, seccomp, netfilter |
| 편집기·운영 도구         | Vim, lsof, tcpdump 등                 |

문서는 주제별 탐색을 위해 관련 분류에 중복 링크할 수 있습니다.

## 2. 추천 학습 순서

### 2.1 기본 개념

1. [Linux 프로세스 수명](./process_lifecycle.md) — `fork`, `exec`, zombie, orphan.
2. [Linux 시스템 프로세스](./linux_system_processes.md) — 프로세스와 시스템 상태의 관계.
3. [가상 메모리 개념](./virtual_memory_concepts.md) — 페이지 테이블, TLB, OOM.
4. [Linux 파일시스템](./linux_filesystem.md) — 파일시스템 구조와 운영 개념.
5. [Virtual File System](./linux_virtual_fs.md) — VFS와 경로 처리.

### 2.2 시스템 관찰

1. [저장장치 도구](./storage_tools.md) — 장치, 공간, 프로세스·디바이스 I/O 확인.
2. [프로세스별 I/O](./iotop.md) — 실시간 프로세스 I/O 관찰.
3. [I/O 지연시간](./ioping.md) — 파일시스템·저장장치 응답시간 측정.
4. [시스템 콜 추적](./strace.md) — 프로세스의 시스템 콜과 신호 확인.
5. [성능 분석](./perf.md) — CPU와 커널 성능 분석.
6. [eBPF·bpftrace](./ebpf.md) — 커널 관찰과 추적 기초.

### 2.3 운영 심화

1. [cgroup 개념](./cgroup_concepts.md) — 자원 제어와 격리.
2. [namespace 개념](./namespace_concepts.md) — 프로세스·네트워크·마운트 격리.
3. [seccomp·capabilities](./seccomp_capabilities.md) — 시스템 콜과 권한 제한.
4. [OOM과 hang](./oom_hang.md) — 메모리 부족과 응답 정지 분석.
5. [netfilter·tc](./netfilter_tc.md) — Linux 네트워크 필터링과 트래픽 제어.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 주제별 문서

### 3.1 Shell·CLI

- [Bash 파일 리다이렉션](./bash_file_redirection.md) — 표준 입출력과 리다이렉션.
- [Bash 수학](./bash_math.md) — 셸 산술 연산과 계산.
- [Bash trap 가이드](./bash_trap_complete_guide.md) — 신호 처리와 정리 작업.
- [Shell 인터랙티브 모드](./shell_interactive_mode.md) — 인터랙티브·비인터랙티브 셸.

### 3.2 프로세스·메모리·스케줄러

- [프로세스 수명](./process_lifecycle.md) — `fork`, `exec`, `wait`, `exit`.
- [Linux 시스템 프로세스](./linux_system_processes.md) — 프로세스 상태와 관리.
- [IPC 개념](./ipc_concepts.md) — 프로세스 간 통신.
- [가상 메모리](./virtual_memory_concepts.md) — 주소 변환과 메모리 관리.
- [OOM·hang](./oom_hang.md) — 메모리 부족과 응답 정지.
- [스케줄러 개념](./scheduler_concepts.md) — CPU 스케줄링과 실행 흐름.
- [cgroup 개념](./cgroup_concepts.md) — 자원 제한과 그룹 관리.
- [namespace 개념](./namespace_concepts.md) — 커널 네임스페이스 격리.

### 3.3 파일시스템·저장장치

- [Linux 파일시스템](./linux_filesystem.md) — 파일시스템 구조와 운영.
- [Linux Virtual File System](./linux_virtual_fs.md) — VFS 계층과 경로 처리.
- [저장장치 도구](./storage_tools.md) — 장치·마운트·공간·I/O·상태 도구 선택.
- [lsblk](./lsblk.md) — 블록 장치 계층 확인.
- [findmnt](./findmnt.md) — 마운트 정보 조회.
- [blkid](./blkid.md) — 블록 장치 식별 정보 조회.
- [df](./df.md) — 파일시스템 공간 확인.
- [du](./du.md) — 파일·디렉토리 공간 사용량 확인.
- [ncdu](./ncdu.md) — 대화형 디스크 사용량 분석.
- [pidstat](./pidstat.md) — 프로세스별 I/O 통계.
- [iostat](./iostat.md) — 디바이스 I/O 통계.
- [dstat](./dstat.md) — 통합 시스템 자원 통계.
- [atop](./atop.md) — 종합 시스템·프로세스 모니터링.
- [nmon](./nmon.md) — 시스템 자원 관찰.
- [fio](./fio.md) — 통제된 블록 I/O 성능 테스트.
- [hdparm](./hdparm.md) — ATA/SATA 장치 정보와 읽기 테스트.
- [smartctl](./smartctl.md) — 저장장치 SMART 상태 확인.
- [nvme-cli](./nvme_cli.md) — NVMe 장치 관리와 로그 확인.
- [ioping](./ioping.md) — 저장장치 I/O 지연시간 측정.

### 3.4 디버깅·프로파일링

- [strace](./strace.md) — 시스템 콜과 신호 추적.
- [ltrace](./ltrace.md) — 동적 라이브러리 호출 추적.
- [GDB](./gdb.md) — 프로세스 디버깅.
- [perf](./perf.md) — CPU·커널 성능 분석.
- [eBPF](./ebpf.md) — 커널 관찰 기초.
- [bpftrace](./bpftrace.md) — eBPF 추적 스크립트.
- [Valgrind](./valgrind.md) — 메모리·스레드 분석.

### 3.5 커널·보안·격리

- [cgroup](./cgroup_concepts.md) — 자원 제어.
- [namespace](./namespace_concepts.md) — 실행 환경 격리.
- [seccomp·capabilities](./seccomp_capabilities.md) — 권한과 시스템 콜 제한.
- [netfilter·tc](./netfilter_tc.md) — 패킷 필터링과 트래픽 제어.
- [Linux 파일시스템](./linux_filesystem.md) — 파일시스템 운영 경계.
- [Virtual File System](./linux_virtual_fs.md) — 커널 파일시스템 계층.

### 3.6 편집기·운영 도구

- [Vim](./vim.md) — Linux 운영 환경의 편집기 사용.
- [Vim airline](./vim_airline.md) — Vim 상태 표시줄 설정.
- [lsof](./lsof.md) — 열린 파일과 소켓 조회.
- [tcpdump](./tcpdump.md) — 패킷 캡처와 필터링.
- [Bash 파일 리다이렉션](./bash_file_redirection.md) — 명령 입출력 연결.
- [Bash trap](./bash_trap_complete_guide.md) — 운영 스크립트 정리 패턴.
- [root password recovery](./root_password_recovery.md) — 복구 환경에서의 계정 접근 복구.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 관련 섹션

- 상위 분류: [01_fundamentals README](../README.md)
- 인프라 모니터링: [02_infrastructure/monitoring](../../02_infrastructure/monitoring/)
- 보안 강화: [04_security/hardening](../../04_security/hardening/)

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux Kernel Documentation: [docs.kernel.org](https://docs.kernel.org/) — ★★★☆☆
- Linux man-pages: [man7.org/linux/man-pages](https://man7.org/linux/man-pages/) — ★★★☆☆

---

**작성일**: 2026-08-18

**마지막 업데이트**: 2026-08-18

© 2026 siasia86. Licensed under CC BY 4.0.
