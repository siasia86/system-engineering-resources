---
name: ubuntu-debian-official-notes
description: Ubuntu·Debian 릴리스 주기, 지원 기간, 현재 판, apt·deb822 저장소 형식의 공식 출처 기준 사실 정리.
tags:
  - linux
  - ubuntu
  - debian
  - apt
last_checked: 2026-11-23
sources:
  - https://ubuntu.com/about/release-cycle
  - https://changelogs.ubuntu.com/meta-release
  - https://changelogs.ubuntu.com/meta-release-lts
  - https://www.debian.org/releases/
  - https://wiki.debian.org/LTS
  - https://manpages.debian.org/trixie/apt/sources.list.5.en.html
  - https://endoflife.date/ubuntu
  - https://endoflife.date/debian
---

# Ubuntu·Debian 공식 참조 노트

## 1. 공식 소스

| 소스                 | URL                                                           | 용도                        |
|----------------------|---------------------------------------------------------------|-----------------------------|
| Ubuntu release cycle | https://ubuntu.com/about/release-cycle                        | LTS·중간 판 지원 기간       |
| Ubuntu meta-release  | https://changelogs.ubuntu.com/meta-release                    | 판별 지원 여부(기계 판독용) |
| Debian releases      | https://www.debian.org/releases/                              | 안정판 이름·판·출시일       |
| Debian LTS           | https://wiki.debian.org/LTS                                   | 안정판 이후 장기 지원       |
| sources.list(5)      | https://manpages.debian.org/trixie/apt/sources.list.5.en.html | deb822 저장소 형식          |
| endoflife.date       | https://endoflife.date/ubuntu, https://endoflife.date/debian  | 날짜 교차 확인(보조)        |

## 2. Ubuntu

### 검증된 사실 (2026-11-23)

| 항목                   | 값                                                                  | 출처                     |
|------------------------|---------------------------------------------------------------------|--------------------------|
| 출시 주기              | 4월·10월 연 2회, 판 번호는 `연.월`(예: 26.04)                       | release cycle            |
| LTS                    | 짝수 해 4월 판. 표준 보안 유지 5년                                  | release cycle            |
| Ubuntu Pro             | LTS의 Main·Universe 저장소 보안 업데이트 10년                       | release cycle            |
| Legacy 추가 구독       | ESM과 합쳐 15년                                                     | release cycle            |
| 지원 중인 LTS          | 26.04.1 LTS (resolute, 2026-04-23), 24.04.5 LTS (noble, 2024-04-25) | meta-release-lts         |
| 26.04 LTS 표준 지원 끝 | 2031-05 (Pro 포함 2036-04)                                          | endoflife.date (보조)    |
| 개발 판                | 27.04 (tenacious)                                                   | meta-release-development |
| 업그레이드 도구        | `do-release-upgrade` (update-manager-core)                          | release cycle 안내       |

## 3. Debian

### 검증된 사실 (2026-11-23)

| 항목                | 값                                                               | 출처                 |
|---------------------|------------------------------------------------------------------|----------------------|
| 현재 안정판         | Debian 13 "trixie", 2025-08-09 13.0 출시, 최신 13.8(2026-11-21)  | debian.org/releases  |
| 이전 안정판         | Debian 12 "bookworm"                                             | debian.org/releases  |
| 보안 지원           | 안정판 약 3년 + LTS로 합계 약 5년                                | Debian LTS wiki      |
| Debian 13 지원 기간 | 정규 보안 지원 2028-08-09까지, LTS 2030-06-30까지                | Debian LTS wiki      |
| 업그레이드          | 저장소의 판 이름을 바꾼 뒤 `apt full-upgrade` (릴리스 노트 절차) | Debian release notes |

## 4. apt와 저장소 형식

| 항목               | 내용                                                                                                                         |
|--------------------|------------------------------------------------------------------------------------------------------------------------------|
| 저장소 파일        | Ubuntu 24.04 이후 `/etc/apt/sources.list.d/ubuntu.sources`, Debian 13 `/etc/apt/sources.list.d/debian.sources` (deb822 형식) |
| deb822 필드        | `Types`, `URIs`, `Suites`, `Components`, `Signed-By`                                                                         |
| 서명 키            | 저장소마다 `Signed-By`로 키 파일 지정 (`apt-key`는 폐기)                                                                     |
| 패키지 관리        | `apt`(대화형), `apt-get`·`apt-cache`(스크립트용, 출력이 안정적)                                                              |
| 저수준 도구        | `dpkg -l`(설치 목록), `dpkg -S 경로`(파일 소속 패키지), `dpkg -L 패키지`(파일 목록)                                          |
| 자동 보안 업데이트 | `unattended-upgrades` 패키지                                                                                                 |

## 5. 검증 기록

- 1차: 공식 출처(ubuntu.com release cycle, changelogs.ubuntu.com meta-release, debian.org releases)에서 판·날짜·지원 기간 문구를 확인했습니다.
- 2차: `ubuntu:24.04`(24.04.5 LTS)·`debian:13` 컨테이너에서 `/etc/os-release`, deb822 저장소 파일, `apt-get`·`apt-cache`·`dpkg` 명령을 실행해 대조했습니다.
- 지원 종료 날짜 일부는 endoflife.date를 보조로 썼고, 표에 "보조"로 표시했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
