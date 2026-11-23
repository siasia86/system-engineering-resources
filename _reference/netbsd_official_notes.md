---
name: netbsd-official-notes
description: NetBSD의 현재 판, 지원 계열, 패키지(pkgsrc·pkgin), 방화벽(NPF)의 공식 출처 기준 사실 정리.
tags:
  - bsd
  - netbsd
last_checked: 2026-11-23
sources:
  - https://www.netbsd.org/
  - https://www.netbsd.org/releases/
  - https://www.netbsd.org/docs/pkgsrc/
  - https://www.netbsd.org/docs/pkgsrc/using.html
  - https://man.netbsd.org/npf.7
---

# NetBSD 공식 참조 노트

## 1. 공식 소스

| 소스            | URL                                           | 용도                 |
|-----------------|-----------------------------------------------|----------------------|
| NetBSD 홈       | https://www.netbsd.org/                       | 현재 판              |
| NetBSD releases | https://www.netbsd.org/releases/              | 지원 중인 계열       |
| pkgsrc guide    | https://www.netbsd.org/docs/pkgsrc/           | 패키지 체계          |
| Using pkgsrc    | https://www.netbsd.org/docs/pkgsrc/using.html | 바이너리 패키지 설치 |
| npf(7)          | https://man.netbsd.org/npf.7                  | 패킷 필터            |

## 2. 검증된 사실 (2026-11-23)

| 항목          | 값                                                             | 출처         |
|---------------|----------------------------------------------------------------|--------------|
| 현재 판       | 11.1 (2026-11-02, 11 계열 첫 갱신)                             | netbsd.org   |
| 지원 계열     | 11.x와 10.x(10.2)가 지원 중. 그보다 오래된 판은 보안 수정 없음 | releases     |
| 개발 판       | NetBSD-current                                                 | releases     |
| 패키지 체계   | pkgsrc: 여러 Unix 계열 OS에서 쓰는 중앙 패키지 관리 체계       | pkgsrc guide |
| 바이너리 설치 | `pkg_add`, 저장소 관리 도구 `pkgin`                            | Using pkgsrc |
| 방화벽        | NPF: IPv4·IPv6와 TCP·UDP·ICMP를 다루는 3계층 패킷 필터         | npf(7)       |

## 3. 검증 기록

- 1차: netbsd.org 홈과 releases 페이지에서 판·지원 계열을 확인했습니다.
- 2차: pkgsrc 안내서와 npf(7) man 페이지로 패키지·방화벽 사실을 다시 대조했습니다.
- NetBSD는 Linux 컨테이너로 실행할 수 없어 명령은 실행 시험하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
