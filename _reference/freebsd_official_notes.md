---
name: freebsd-official-notes
description: FreeBSD의 현재 판, 지원 모델, 패키지(pkg·ports), 기본 시스템 갱신(freebsd-update), 기본 방화벽의 공식 출처 기준 사실 정리.
tags:
  - bsd
  - freebsd
last_checked: 2026-11-23
sources:
  - https://www.freebsd.org/releases/
  - https://www.freebsd.org/security/
  - https://docs.freebsd.org/en/books/handbook/ports/
  - https://docs.freebsd.org/en/books/handbook/cutting-edge/
  - https://docs.freebsd.org/en/books/handbook/firewalls/
---

# FreeBSD 공식 참조 노트

## 1. 공식 소스

| 소스                     | URL                                                      | 용도                      |
|--------------------------|----------------------------------------------------------|---------------------------|
| FreeBSD releases         | https://www.freebsd.org/releases/                        | 운영 판·이전 판·예정 판   |
| FreeBSD security         | https://www.freebsd.org/security/                        | 지원 모델, 판별 지원 종료 |
| Handbook: packages·ports | https://docs.freebsd.org/en/books/handbook/ports/        | pkg, ports                |
| Handbook: updating       | https://docs.freebsd.org/en/books/handbook/cutting-edge/ | freebsd-update            |
| Handbook: firewalls      | https://docs.freebsd.org/en/books/handbook/firewalls/    | PF·IPFW·IPF               |

## 2. 검증된 사실 (2026-11-23)

| 항목             | 값                                                                                             | 출처               |
|------------------|------------------------------------------------------------------------------------------------|--------------------|
| 운영 판          | 15.1 (2026-06-16 출시, 지원 끝 2027-03-31)                                                     | releases, security |
| 이전 판          | 15.0, 14.5 (2026-09-08), 14.4                                                                  | releases, security |
| 예정 판          | 15.2, 14.6                                                                                     | releases           |
| 계열 지원        | stable/15는 2029-12-31, stable/14는 2028-11-30까지                                             | security           |
| 지원 모델        | 15부터 각 stable 계열은 x.0 출시일로부터 4년. 부판은 같은 계열의 다음 부판이 나온 뒤 3개월까지 | security           |
| 패키지           | 바이너리 패키지는 `pkg`, 소스에서 빌드는 ports                                                 | Handbook ports     |
| 기본 시스템 갱신 | `freebsd-update fetch` → `freebsd-update install`, 커널 패치면 재부팅                          | Handbook updating  |
| 기본 방화벽      | PF, IPFW, IPFILTER(IPF) 세 가지가 기본 시스템에 포함                                           | Handbook firewalls |

## 3. 검증 기록

- 1차: freebsd.org releases·security 페이지와 Handbook에서 판·날짜·정책·명령을 확인했습니다.
- 2차: 같은 사실을 Handbook의 다른 장(ports, cutting-edge, firewalls)과 security 표의 판별 행으로 다시 대조했습니다.
- FreeBSD는 Linux 컨테이너로 실행할 수 없어 명령은 실행 시험하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
