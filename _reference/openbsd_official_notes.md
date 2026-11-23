---
name: openbsd-official-notes
description: OpenBSD의 현재 판, 릴리스·지원 주기, 패키지(pkg_add), 기본 시스템 패치(syspatch), PF의 공식 출처 기준 사실 정리.
tags:
  - bsd
  - openbsd
last_checked: 2026-11-23
sources:
  - https://www.openbsd.org/
  - https://www.openbsd.org/faq/faq5.html
  - https://www.openbsd.org/faq/faq15.html
  - https://man.openbsd.org/syspatch
  - https://www.openbsd.org/faq/pf/
---

# OpenBSD 공식 참조 노트

## 1. 공식 소스

| 소스              | URL                                    | 용도                                 |
|-------------------|----------------------------------------|--------------------------------------|
| OpenBSD 홈        | https://www.openbsd.org/               | 현재 판                              |
| FAQ 5 (flavors)   | https://www.openbsd.org/faq/faq5.html  | -current·-release·-stable, 지원 범위 |
| FAQ 15 (packages) | https://www.openbsd.org/faq/faq15.html | pkg_add 등 패키지 도구               |
| syspatch(8)       | https://man.openbsd.org/syspatch       | 기본 시스템 바이너리 패치            |
| PF User's Guide   | https://www.openbsd.org/faq/pf/        | 패킷 필터                            |

## 2. 검증된 사실 (2026-11-23)

| 항목             | 값                                                                                      | 출처        |
|------------------|-----------------------------------------------------------------------------------------|-------------|
| 현재 판          | 8.0 (2026-10-20, 61번째 릴리스)                                                         | openbsd.org |
| 릴리스 주기      | 6개월마다 -current를 태그해 다음 릴리스로 만듦                                          | FAQ 5       |
| 지원 범위        | 가장 최근 두 릴리스가 기본 시스템의 보안·안정성 수정을 받음. ports 갱신은 최신 릴리스만 | FAQ 5       |
| 패키지           | `pkg_add`(설치·갱신), `pkg_delete`, `pkg_info`, `pkg_check`                             | FAQ 15      |
| 기본 시스템 패치 | `syspatch`가 빠진 패치를 받아 검증·설치하고 되돌릴 묶음을 만듦                          | syspatch(8) |
| 방화벽           | PF                                                                                      | PF guide    |

## 3. 검증 기록

- 1차: openbsd.org 홈과 FAQ 5·15에서 판·주기·지원 범위·패키지 도구를 확인했습니다.
- 2차: syspatch(8) man 페이지와 PF 안내서로 패치·방화벽 사실을 다시 대조했습니다.
- OpenBSD는 Linux 컨테이너로 실행할 수 없어 명령은 실행 시험하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
