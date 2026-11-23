# BSD 계열 (FreeBSD·OpenBSD·NetBSD)
<!-- reference: _reference/freebsd_official_notes.md, _reference/openbsd_official_notes.md, _reference/netbsd_official_notes.md -->

BSD Unix에서 이어진 세 운영체제 FreeBSD·OpenBSD·NetBSD가 무엇이고 Linux와 어떻게 다른지, 셋은 서로 어떻게 다른지를 정리한 개념 문서입니다. 방화벽·저장 장치·네트워크 장비에서 BSD를 만났을 때 판을 확인하고 기본 도구를 알아볼 수 있는 정도를 목표로 합니다.

- 기준 판: FreeBSD 15.1, OpenBSD 8.0, NetBSD 11.1 (각 공식 사이트, 2026-11-23 확인)
- 예제 시험: 미실행. BSD는 Linux 컨테이너로 실행할 수 없어 명령은 각 OS의 공식 문서와 대조했습니다

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Linux와 다른 점](#2-linux와-다른-점) / [3. 세 OS 비교](#3-세-os-비교)               |
| [4. 판과 지원](#4-판과-지원) / [5. 기본 명령 대응표](#5-기본-명령-대응표) / [6. 고르는 기준](#6-고르는-기준) |
| [7. 확인 방법](#7-확인-방법) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                             |

---

## 1. 개요

BSD는 캘리포니아 대학교 버클리에서 만든 Unix 배포판(Berkeley Software Distribution)에서 갈라져 나온 운영체제들입니다. Linux가 커널만 따로 만들고 배포판이 사용자 프로그램을 모으는 것과 달리, BSD는 커널과 기본 사용자 프로그램(셸, 기본 명령, 라이브러리)을 한 프로젝트가 함께 만들어 "기본 시스템(base system)"으로 배포합니다.

| 운영체제 | 중심 목표                           | 자주 보이는 곳                                |
|----------|-------------------------------------|-----------------------------------------------|
| FreeBSD  | 성능과 기능, 서버·네트워크 장비     | 서버, 스토리지 장비, 방화벽 제품, 콘텐츠 전송 |
| OpenBSD  | 보안과 코드 정확성                  | 방화벽, VPN 게이트웨이, 보안 장비             |
| NetBSD   | 이식성(아주 많은 하드웨어에서 실행) | 임베디드·옛 하드웨어, 연구                    |

세 OS에서 나온 기술은 다른 곳에서도 많이 씁니다. OpenSSH와 PF는 OpenBSD 프로젝트에서 나왔고, pkgsrc는 NetBSD에서 시작해 여러 OS에서 쓰입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Linux와 다른 점

| 항목            | Linux                                | BSD                                              |
|-----------------|--------------------------------------|--------------------------------------------------|
| 구성            | 커널 + 배포판이 고른 사용자 프로그램 | 커널과 기본 시스템을 한 프로젝트가 함께 관리     |
| 라이선스        | 커널은 GPLv2                         | BSD 라이선스 (상용 제품에 넣기 쉬움)             |
| 추가 소프트웨어 | 배포판 저장소 (apt, dnf 등)          | 기본 시스템과 분리된 패키지·ports (`/usr/local`) |
| 서비스 관리     | 대부분 systemd                       | rc 스크립트 (`/etc/rc.conf`, `/etc/rc.d/`)       |
| 기본 셸·명령    | GNU coreutils, bash                  | BSD 판 명령 (옵션이 GNU와 다른 경우가 있음), sh  |
| 방화벽          | netfilter (nftables·iptables)        | PF, IPFW(FreeBSD), NPF(NetBSD)                   |

GNU 옵션에 익숙하면 `sed -i`, `grep -P`, `date -d` 같은 옵션이 BSD에서 다르거나 없다는 점에 주의합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 세 OS 비교

| 항목             | FreeBSD                        | OpenBSD    | NetBSD                   |
|------------------|--------------------------------|------------|--------------------------|
| 패키지 설치      | `pkg install`                  | `pkg_add`  | `pkgin install` (pkgsrc) |
| 소스 빌드        | ports (`/usr/ports`)           | ports      | pkgsrc                   |
| 기본 시스템 갱신 | `freebsd-update fetch install` | `syspatch` | 새 판 설치·빌드          |
| 방화벽           | PF, IPFW, IPF                  | PF         | NPF                      |
| 파일 시스템      | UFS, ZFS                       | FFS        | FFS, 그 밖에 여러 가지   |
| 가상화·격리      | jail, bhyve                    | vmm        | -                        |
| 릴리스 주기      | 부판을 계획에 따라 출시        | 6개월마다  | 주판과 그 갱신판         |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 판과 지원

| 운영체제 | 현재 판           | 지원 정책                                                                                                     |
|----------|-------------------|---------------------------------------------------------------------------------------------------------------|
| FreeBSD  | 15.1 (2026-06-16) | 15부터 각 stable 계열을 x.0 출시일로부터 4년 지원(15 계열은 2029-12-31). 부판은 다음 부판이 나온 뒤 3개월까지 |
| OpenBSD  | 8.0 (2026-10-20)  | 가장 최근 두 릴리스만 보안·안정성 수정. 6개월마다 새 판이라 판당 약 1년                                       |
| NetBSD   | 11.1 (2026-11-02) | 11.x와 10.x 계열이 지원 중. 그보다 오래된 판은 보안 수정 없음                                                 |

OpenBSD처럼 지원 기간이 짧은 OS는 판 업그레이드를 정기 작업으로 잡아 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 명령 대응표

| 작업             | Linux (예)               | FreeBSD                                            | OpenBSD                        | NetBSD                        |
|------------------|--------------------------|----------------------------------------------------|--------------------------------|-------------------------------|
| OS·판 확인       | `cat /etc/os-release`    | `freebsd-version`, `uname -a`                      | `uname -a`                     | `uname -a`                    |
| 패키지 검색      | `apt search`             | `pkg search`                                       | `pkg_info -Q`                  | `pkgin search`                |
| 패키지 설치      | `apt install`            | `pkg install`                                      | `pkg_add`                      | `pkgin install`               |
| 서비스 켜기      | `systemctl enable --now` | `sysrc 서비스_enable=YES` + `service 서비스 start` | `rcctl enable` + `rcctl start` | `/etc/rc.conf`에 `서비스=YES` |
| 네트워크 설정    | `ip addr`                | `ifconfig`                                         | `ifconfig`                     | `ifconfig`                    |
| 방화벽 규칙 적용 | `nft -f`                 | `pfctl -f /etc/pf.conf` (PF)                       | `pfctl -f /etc/pf.conf`        | `npfctl reload`               |

BSD의 서비스 설정은 `/etc/rc.conf`가 중심입니다. FreeBSD의 `sysrc`와 OpenBSD의 `rcctl`은 이 파일을 대신 고쳐 주는 도구입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 고르는 기준

| 상황                                                    | 후보                                 |
|---------------------------------------------------------|--------------------------------------|
| ZFS 스토리지 서버, jail 기반 격리, 높은 네트워크 처리량 | FreeBSD                              |
| 작은 방화벽·VPN 게이트웨이, 보안이 최우선               | OpenBSD                              |
| 특이하거나 오래된 하드웨어에서 Unix 실행                | NetBSD                               |
| 일반 서버·컨테이너·Kubernetes                           | Linux (BSD는 컨테이너 생태계가 작음) |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 확인 방법

BSD 장비를 처음 받았을 때 아래 순서로 확인합니다.

| 순서 | 확인 내용             | 명령                                                  | 기대 결과             |
|------|-----------------------|-------------------------------------------------------|-----------------------|
| 1    | OS와 판               | `uname -a` (FreeBSD는 `freebsd-version -ku`도)        | OS 이름, 판, 아키텍처 |
| 2    | 지원 여부             | 4절 표와 공식 사이트의 지원 판 비교                   | 지원 중인 판          |
| 3    | 남은 기본 시스템 패치 | FreeBSD `freebsd-update fetch`, OpenBSD `syspatch -c` | 적용할 패치 없음      |
| 4    | 켜진 서비스           | `/etc/rc.conf` 확인, OpenBSD `rcctl ls on`            | 의도한 서비스만       |
| 5    | 방화벽 규칙           | PF `pfctl -sr`, NetBSD `npfctl show`                  | 의도한 규칙이 적용됨  |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ubuntu·Debian](./ubuntu_debian.md) · [RHEL 계열](./rhel_family.md) · [SUSE Linux](./suse_linux.md) — Linux 배포판
- [텍스트 처리](./text_processing.md) — GNU 도구와 BSD 도구의 옵션 차이
- [netfilter·tc](./netfilter_tc.md) — Linux 쪽 패킷 필터
- [SSH 보안](../../04_security/hardening/ssh_security.md) — OpenBSD 프로젝트에서 나온 OpenSSH

---

## 참고 자료

- FreeBSD: [Releases](https://www.freebsd.org/releases/) · [Security Information](https://www.freebsd.org/security/) — ★★★☆☆
- FreeBSD: [Handbook — Packages and Ports](https://docs.freebsd.org/en/books/handbook/ports/) · [Firewalls](https://docs.freebsd.org/en/books/handbook/firewalls/) — ★★★☆☆
- OpenBSD: [OpenBSD](https://www.openbsd.org/) · [FAQ — Flavors](https://www.openbsd.org/faq/faq5.html) — ★★★☆☆
- OpenBSD: [syspatch(8)](https://man.openbsd.org/syspatch) · [PF User's Guide](https://www.openbsd.org/faq/pf/) — ★★★☆☆
- NetBSD: [NetBSD](https://www.netbsd.org/) · [Releases](https://www.netbsd.org/releases/) — ★★★☆☆
- NetBSD: [pkgsrc guide](https://www.netbsd.org/docs/pkgsrc/) · [npf(7)](https://man.netbsd.org/npf.7) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
