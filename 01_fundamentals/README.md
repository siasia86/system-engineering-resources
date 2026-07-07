# Fundamentals

시스템 엔지니어링의 기초 지식. OS, 네트워크, 자료구조/알고리즘, 프로그래밍 언어를 다룹니다.

## 구조

| 디렉토리                       | 설명                                                         | 문서 수 |
|--------------------------------|--------------------------------------------------------------|---------|
| [linux/](./linux/)             | Linux 관리 — bash, cgroup, systemd, 파일시스템, 커널, vim 등 | 29      |
| [networking/](./networking/)   | 네트워크 기초 — TCP/IP, HTTP, DNS, CDN, VPN, IPv4/IPv6       | 13      |
| [cs/](./cs/)                   | 컴퓨터 과학 — 자료구조, 알고리즘, CPU 아키텍처, 테스트 설계  | 21      |
| [programming/](./programming/) | 프로그래밍 언어 — Python, Bash, C/C++, Go 비교, LSP          | 26      |

## 주요 문서

- [bash_trap_complete_guide.md](./linux/bash_trap_complete_guide.md) — 시그널 핸들링과 cleanup 패턴
- [virtual_memory.md](./linux/virtual_memory.md) — 페이지 테이블, TLB, OOM 원리
- [TCP_state.md](./networking/TCP_state.md) — TCP 상태 전이, TIME_WAIT 문제
- [ipv4_addressing_guide.md](./networking/ipv4_addressing_guide.md) — 서브넷팅, CIDR, AWS VPC 매핑
- [process_lifecycle.md](./linux/process_lifecycle.md) — fork/exec, zombie/orphan 처리

## 추천 학습 순서

`linux (기초)` → `networking (IPv4/TCP)` → `cs (자료구조)` → `programming (Python)`

## 전제 조건

없음. 시스템 엔지니어링 학습의 시작점입니다.

## 관련 섹션

- 디버깅 도구 실습: [02_infrastructure/monitoring/](../02_infrastructure/monitoring/)
- 보안 강화 적용: [04_security/hardening/](../04_security/hardening/)

[⬆ 루트 README로 돌아가기](../README.md)

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
