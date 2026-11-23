---
name: rhel-family-official-notes
description: RHEL과 재빌드 배포판(Rocky Linux·AlmaLinux), CentOS Stream의 판·수명 주기, dnf·EPEL·업그레이드의 공식 출처 기준 사실 정리.
tags:
  - linux
  - rhel
  - rocky
  - almalinux
  - dnf
last_checked: 2026-11-23
sources:
  - https://access.redhat.com/articles/3078
  - https://access.redhat.com/support/policy/updates/errata
  - https://rockylinux.org/download
  - https://wiki.almalinux.org/release-notes/
  - https://docs.fedoraproject.org/en-US/epel/getting-started/
  - https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/upgrading_from_rhel_9_to_rhel_10/index
  - https://endoflife.date/rhel
---

# RHEL 계열 공식 참조 노트

## 1. 공식 소스

| 소스                    | URL                                                                                                              | 용도                    |
|-------------------------|------------------------------------------------------------------------------------------------------------------|-------------------------|
| RHEL release dates      | https://access.redhat.com/articles/3078                                                                          | 판별 GA 날짜, 커널 판   |
| RHEL life cycle         | https://access.redhat.com/support/policy/updates/errata                                                          | 수명 주기 단계          |
| Rocky Linux download    | https://rockylinux.org/download                                                                                  | 현재 판                 |
| AlmaLinux release notes | https://wiki.almalinux.org/release-notes/                                                                        | 현재 판                 |
| EPEL getting started    | https://docs.fedoraproject.org/en-US/epel/getting-started/                                                       | EPEL 사용 절차          |
| RHEL 9 → 10 upgrade     | https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/upgrading_from_rhel_9_to_rhel_10/index | Leapp 제자리 업그레이드 |
| endoflife.date          | https://endoflife.date/rhel                                                                                      | 날짜 교차 확인(보조)    |

## 2. 판과 수명 주기

### 검증된 사실 (2026-11-23)

| 항목                   | 값                                                                         | 출처                                                           |
|------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------|
| RHEL 10.0 GA           | 2025-05-20, 커널 6.12                                                      | access.redhat.com 3078                                         |
| RHEL 최신 부판         | 10.3 (2026-11-10), 이전 10.2 (2026-05-19), 10.1 (2025-11-11)               | access.redhat.com 3078                                         |
| 부판 주기              | 약 6개월마다 부판                                                          | access.redhat.com 3078                                         |
| 수명 주기              | 주판마다 10년(Full Support → Maintenance Support), 이후 유료 Extended Life | life cycle 정책                                                |
| RHEL 10 Maintenance 끝 | 2035-05-31                                                                 | Rocky 10 `/etc/os-release` `SUPPORT_END`, endoflife.date(보조) |
| Rocky Linux 현재 판    | 10.3 (컨테이너 `/etc/os-release`), 9.9·8.10 (endoflife.date 보조)          | 컨테이너, endoflife.date(보조)                                 |
| AlmaLinux 현재 판      | 10.3, 9.9, 8.10                                                            | AlmaLinux wiki                                                 |
| CentOS Stream          | RHEL 다음 부판의 개발 흐름(업스트림). 운영 안정판이 아님                   | endoflife.date(보조)                                           |

## 3. 패키지와 저장소

| 항목          | 내용                                                                                                                                      |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| 패키지 관리자 | `dnf` (Rocky 10.3 컨테이너에서 4.20.0), `yum`은 dnf로 연결된 이름                                                                         |
| 기본 저장소   | BaseOS(핵심 OS), AppStream(응용·언어 런타임, 모듈·스트림), Rocky·Alma는 Extras도 있음                                                     |
| 업데이트 확인 | `dnf check-update`는 업데이트가 있으면 종료 코드 100, 없으면 0                                                                            |
| 이력·되돌리기 | `dnf history list`, `dnf history undo <ID>`                                                                                               |
| 파일 소속     | `rpm -qf 경로`, 패키지 정보 `dnf info`                                                                                                    |
| CRB           | 개발용 패키지 저장소. Rocky·Alma는 `dnf config-manager --set-enabled crb` (dnf-plugins-core 필요)                                         |
| EPEL          | Fedora 프로젝트의 추가 패키지. Rocky·Alma는 CRB를 켠 뒤 `dnf install epel-release`, RHEL은 `epel-release-latest-10.noarch.rpm` URL로 설치 |
| RHEL 등록     | `subscription-manager register`로 등록해야 Red Hat 저장소를 씀                                                                            |

## 4. 업그레이드

| 항목             | 내용                                                                                           |
|------------------|------------------------------------------------------------------------------------------------|
| 부판 갱신        | `dnf upgrade` (예: 10.2 → 10.3)                                                                |
| 주판 업그레이드  | Red Hat 지원 도구는 Leapp(9 → 10 제자리 업그레이드). 새로 설치 후 이전이 더 단순한 경우가 많음 |
| 재부팅 필요 확인 | `dnf needs-restarting -r` (dnf-plugins-core)                                                   |

## 5. 검증 기록

- 1차: Red Hat 공식 페이지(release dates, life cycle), Rocky 내려받기 페이지·Alma wiki, Fedora EPEL 문서에서 판·날짜·절차를 확인했습니다.
- 2차: `rockylinux/rockylinux:10` 컨테이너(10.3)에서 `dnf repolist`, `check-update` 종료 코드, `history`, CRB·EPEL 사용, `SUPPORT_END` 값을 실행해 대조했습니다.
- Full Support와 Maintenance의 단계별 기간은 공식 페이지 본문에서 숫자를 추출하지 못해, 10년 합계와 종료일만 적었습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
