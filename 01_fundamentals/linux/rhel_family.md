# RHEL 계열 (RHEL·Rocky Linux·AlmaLinux)
<!-- reference: _reference/rhel_family_official_notes.md -->

Red Hat Enterprise Linux(RHEL)와 RHEL을 다시 빌드한 Rocky Linux·AlmaLinux의 판 체계, 지원 기간, 패키지 관리(dnf), 저장소(BaseOS·AppStream·CRB·EPEL), 보안 업데이트, 판 업그레이드를 다룹니다. 이 문서만으로 서버의 판 확인 → 패키지 설치·갱신 → 추가 저장소 → 업그레이드 준비와 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: RHEL 10.3(2026-11-10), Rocky Linux 10.3, AlmaLinux 10.3
- 예제 시험: 2026-11-23, `rockylinux/rockylinux:10`(10.3, dnf 4.20.0) 컨테이너에서 3·4·5절 명령과 `needs-restarting`을 실행해 확인. 6절 자동 업데이트와 7절 주판 업그레이드는 실제 서버에서 실행하지 않았음

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 판과 지원 기간](#2-판과-지원-기간) / [3. 판 확인](#3-판-확인)                   |
| [4. dnf 패키지 관리](#4-dnf-패키지-관리) / [5. 저장소](#5-저장소) / [6. 보안 업데이트](#6-보안-업데이트) |
| [7. 판 업그레이드](#7-판-업그레이드) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)               |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                        |

---

## 1. 개요

| 배포판        | 성격                                                     | 저장소 사용 조건            |
|---------------|----------------------------------------------------------|-----------------------------|
| RHEL          | Red Hat의 상용 배포판                                    | `subscription-manager` 등록 |
| Rocky Linux   | RHEL 소스로 다시 빌드한 무료 배포판                      | 없음                        |
| AlmaLinux     | RHEL과 호환되는 무료 배포판                              | 없음                        |
| CentOS Stream | RHEL 다음 부판의 개발 흐름(업스트림). 운영 안정판이 아님 | 없음                        |
| Fedora        | 새 기술이 먼저 들어가는 커뮤니티 배포판. RHEL의 먼 상류  | 없음                        |

같은 주판(예: 10)이면 RHEL·Rocky·Alma의 패키지와 명령이 같습니다. 이 문서의 명령은 세 배포판에서 그대로 쓸 수 있고, RHEL만 다른 부분은 따로 적었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 판과 지원 기간

| 항목      | 내용                                                                                  |
|-----------|---------------------------------------------------------------------------------------|
| 판 번호   | `주판.부판` (10.3). 부판은 약 6개월마다                                               |
| 현재 주판 | 10 (10.0은 2025-05-20, 커널 6.12), 이전 주판 9·8도 지원 중                            |
| 지원 기간 | 주판마다 10년. RHEL 10·Rocky 10은 2035-05-31까지                                      |
| 부판 지원 | 일반적으로 최신 부판만 갱신을 받음. 부판을 따로 오래 유지하려면 RHEL의 유료 연장 지원 |

지원 종료일은 서버에서 바로 확인할 수 있습니다.

```bash
grep SUPPORT_END /etc/os-release      # Rocky 10: SUPPORT_END="2035-05-31"
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 판 확인

```bash
cat /etc/os-release
# PRETTY_NAME="Rocky Linux 10.3 (Red Quartz)"
# ID="rocky"
# ID_LIKE="rhel centos fedora"
# PLATFORM_ID="platform:el10"

cat /etc/redhat-release        # Rocky Linux release 10.3 (Red Quartz)
rpm -E %rhel                   # 10  (주판 번호, 스크립트에서 편리)
uname -r                       # 커널 판
```

스크립트에서는 `ID_LIKE`에 `rhel`이 있는지로 계열을 판별합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. dnf 패키지 관리

```bash
sudo dnf check-update                          # 갱신 가능 목록 (있으면 종료 코드 100)
sudo dnf upgrade                               # 전체 갱신 (부판도 올라감)
sudo dnf upgrade --security                    # 보안 갱신만 (RHEL처럼 보안 정보가 있는 저장소)

dnf search nginx                               # 검색
dnf info nginx                                 # 정보
sudo dnf install --setopt=install_weak_deps=False nginx   # 약한 의존성(추천) 없이 설치
sudo dnf remove nginx                          # 제거
sudo dnf autoremove                            # 필요 없어진 의존 패키지 제거

dnf history list                               # 작업 이력
sudo dnf history undo <ID>                     # 해당 작업 되돌리기
```

```bash
rpm -q tar                     # 설치 판
rpm -qf /usr/bin/tar           # 이 파일을 설치한 패키지
rpm -ql tar                    # 패키지가 설치한 파일 목록
sudo dnf versionlock add nginx # 판 고정 (python3-dnf-plugin-versionlock 필요)
```

스크립트에서는 `dnf -y -q`로 질문과 출력을 줄입니다. `yum` 명령도 dnf로 연결되어 있어 그대로 동작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 저장소

| 저장소    | 내용                                               | 기본 활성 |
|-----------|----------------------------------------------------|-----------|
| BaseOS    | OS 핵심 패키지                                     | 예        |
| AppStream | 응용, 언어 런타임, 데이터베이스 (판별 스트림 제공) | 예        |
| Extras    | Rocky·Alma의 추가 패키지 (`epel-release` 등)       | 예        |
| CRB       | 개발용 라이브러리·헤더. EPEL의 일부 패키지가 의존  | 아니요    |
| EPEL      | Fedora 프로젝트의 추가 패키지 (htop 등)            | 설치 필요 |

```bash
dnf repolist                                   # 활성 저장소
dnf repolist --all                             # 꺼진 것 포함

# Rocky·AlmaLinux: CRB 켜기 + EPEL
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --set-enabled crb
sudo dnf install -y epel-release

# RHEL: 등록 후 CodeReady Builder + EPEL
sudo subscription-manager register
sudo subscription-manager repos --enable codeready-builder-for-rhel-10-$(arch)-rpms
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
```

외부 저장소는 `/etc/yum.repos.d/*.repo`에 두고 `gpgcheck=1`과 `gpgkey=`로 서명 검사를 켭니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안 업데이트

### 6-1. 자동 업데이트 (dnf-automatic)

```bash
sudo dnf install -y dnf-automatic
sudo vi /etc/dnf/automatic.conf
#   [commands]
#   upgrade_type = security     # 보안 갱신만 (기본값 default = 전체)
#   apply_updates = yes         # 실제 적용 (기본값 no = 내려받기만)
sudo systemctl enable --now dnf-automatic.timer
systemctl list-timers dnf-automatic.timer
```

### 6-2. 재부팅이 필요한지 확인

```bash
sudo dnf install -y dnf-plugins-core
dnf needs-restarting -r          # 필요 없으면 종료 코드 0, 필요하면 1
dnf needs-restarting -s          # 다시 시작해야 할 서비스
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 판 업그레이드

| 종류                      | 방법                                                                |
|---------------------------|---------------------------------------------------------------------|
| 부판 (10.2 → 10.3)        | `sudo dnf upgrade` 후 재부팅                                        |
| 주판 (9 → 10), RHEL       | Red Hat이 지원하는 Leapp 제자리 업그레이드                          |
| 주판 (9 → 10), Rocky·Alma | 배포판이 안내하는 도구(AlmaLinux ELevate 등) 또는 새로 설치 후 이전 |

주판 업그레이드 전 준비:

1. 백업·스냅샷을 만들고, 새 서버에 새 주판을 설치해 이전하는 방법과 비교합니다.
2. 현재 판을 최신 부판까지 올리고 재부팅합니다.
3. 외부 저장소(EPEL 등)와 직접 설치한 RPM의 새 주판 지원 여부를 확인합니다.
4. Leapp는 먼저 `leapp preupgrade`로 막히는 항목 보고서를 만들고, 보고서를 해결한 뒤 `leapp upgrade`를 실행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용         | 명령                                       | 기대 결과                             |
|------|-------------------|--------------------------------------------|---------------------------------------|
| 1    | 판·지원 종료일    | `cat /etc/os-release`                      | 의도한 판, `SUPPORT_END`              |
| 2    | 저장소            | `dnf repolist`                             | 필요한 저장소만 활성                  |
| 3    | 저장소 메타데이터 | `sudo dnf makecache`                       | 오류 없음                             |
| 4    | 남은 갱신         | `sudo dnf check-update; echo $?`           | `0` (100이면 갱신 남음)               |
| 5    | 설치              | `rpm -q <패키지>`                          | 판 출력                               |
| 6    | 자동 업데이트     | `systemctl is-enabled dnf-automatic.timer` | `enabled`                             |
| 7    | 재부팅 필요       | `dnf needs-restarting -r; echo $?`         | `0`                                   |
| 8    | 패키지 무결성     | `rpm -Va <패키지>`                         | 출력 없음 (설정 파일 변경은 `c` 표시) |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                         | 원인                        | 해결 방법                                         |
|----------------------------------------------|-----------------------------|---------------------------------------------------|
| RHEL에서 `This system is not registered`     | 구독 등록 안 됨             | `subscription-manager register`                   |
| EPEL 패키지 설치 중 의존성 없음              | CRB(CodeReady Builder) 꺼짐 | 5절대로 CRB 활성                                  |
| `dnf config-manager: command not found`      | dnf-plugins-core 없음       | `dnf install dnf-plugins-core`                    |
| `GPG check FAILED`                           | 저장소 키가 없거나 다름     | `.repo`의 `gpgkey` 확인, `rpm --import`로 키 등록 |
| 스크립트가 `dnf check-update` 뒤 실패로 끝남 | 갱신이 있으면 종료 코드 100 | 100을 "갱신 있음"으로 처리                        |
| 갱신 뒤 문제 발생                            | 새 패키지의 동작 변경       | `dnf history undo <ID>`, 또는 이전 판 지정 설치   |
| 메타데이터 오류·느림                         | 미러 문제, 캐시 손상        | `sudo dnf clean all && sudo dnf makecache`        |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ubuntu·Debian](./ubuntu_debian.md) — apt를 쓰는 배포판
- [SUSE Linux](./suse_linux.md) — zypper를 쓰는 배포판
- [systemd 유닛 관리](./systemd_unit_management.md) — 서비스와 타이머
- [Docker 설치와 초기 설정](../../02_infrastructure/containers/docker_install.md) — RHEL 계열 외부 저장소 등록 예
- [방화벽 iptables·nftables](../../04_security/hardening/firewall_iptables_nftables.md) — firewalld의 바탕

---

## 참고 자료

- Red Hat: [Red Hat Enterprise Linux Release Dates](https://access.redhat.com/articles/3078) — ★★★☆☆
- Red Hat: [Red Hat Enterprise Linux Life Cycle](https://access.redhat.com/support/policy/updates/errata) — ★★★☆☆
- Red Hat: [Upgrading from RHEL 9 to RHEL 10](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/upgrading_from_rhel_9_to_rhel_10/index) — ★★★☆☆
- Rocky Linux: [Download](https://rockylinux.org/download) — ★★★☆☆
- AlmaLinux: [Release Notes](https://wiki.almalinux.org/release-notes/) — ★★★☆☆
- Fedora: [EPEL Getting Started](https://docs.fedoraproject.org/en-US/epel/getting-started/) — ★★★☆☆
- endoflife.date: [RHEL](https://endoflife.date/rhel) — 날짜 교차 확인 — ★★☆☆☆

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
