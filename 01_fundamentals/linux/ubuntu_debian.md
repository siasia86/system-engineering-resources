# Ubuntu·Debian
<!-- reference: _reference/ubuntu_debian_official_notes.md -->

Debian과 그 파생 배포판인 Ubuntu의 판 체계, 지원 기간, 패키지 관리(apt), 저장소 설정, 보안 업데이트, 판 업그레이드를 다룹니다. 이 문서만으로 서버의 판 확인 → 패키지 설치·갱신 → 자동 보안 업데이트 → 업그레이드 준비와 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Ubuntu 26.04.1 LTS·24.04.5 LTS, Debian 13 "trixie"(13.8)
- 예제 시험: 2026-11-23, `ubuntu:24.04`(24.04.5)와 `debian:13` 컨테이너에서 3·4·5절 명령을 실행해 확인. 6절 자동 업데이트와 7절 판 업그레이드는 실제 서버에서 실행하지 않았음

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 판과 지원 기간](#2-판과-지원-기간) / [3. 판 확인](#3-판-확인)                             |
| [4. apt 패키지 관리](#4-apt-패키지-관리) / [5. 저장소 설정](#5-저장소-설정) / [6. 보안 업데이트](#6-보안-업데이트) |
| [7. 판 업그레이드](#7-판-업그레이드) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                         |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                                  |

---

## 1. 개요

| 항목         | Debian                             | Ubuntu                                       |
|--------------|------------------------------------|----------------------------------------------|
| 만드는 곳    | 자원봉사 커뮤니티 (Debian Project) | Canonical (Debian 기반)                      |
| 출시         | 준비되면 출시, 대략 2년마다 안정판 | 4월·10월 연 2회, 짝수 해 4월은 LTS           |
| 판 이름      | 번호 + 이름 (13 "trixie")          | `연.월` + 이름 (26.04 "Resolute Raccoon")    |
| 패키지       | `.deb`, apt                        | `.deb`, apt (snap도 기본 제공)               |
| 상용 지원    | 없음 (LTS는 별도 조직)             | Ubuntu Pro (보안 업데이트 10년, Legacy 15년) |
| 주로 쓰는 곳 | 보수적인 서버, 다른 배포판의 기반  | 클라우드 이미지, 서버, 개발 PC               |

두 배포판은 패키지 형식과 도구가 같아 이 문서의 명령은 대부분 둘 다에서 그대로 동작합니다. 다른 점은 해당 절에 따로 적었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 판과 지원 기간

| 판                        | 출시       | 지원                                      |
|---------------------------|------------|-------------------------------------------|
| Ubuntu 26.04 LTS          | 2026-04-23 | 표준 5년, Ubuntu Pro 10년                 |
| Ubuntu 24.04 LTS          | 2024-04-25 | 표준 5년, Ubuntu Pro 10년                 |
| Ubuntu 중간 판 (26.10 등) | 4월·10월   | 약 9개월. 서버 운영에는 LTS를 씀          |
| Debian 13 "trixie"        | 2025-08-09 | 정규 보안 지원 2028-08-09, LTS 2030-06-30 |
| Debian 12 "bookworm"      | 2023-06-10 | LTS 기간                                  |

운영 서버는 Ubuntu LTS 또는 Debian 안정판을 쓰고, 지원 종료 전에 다음 판으로 올립니다. 판별 정확한 종료일은 참고 자료의 공식 페이지에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 판 확인

```bash
cat /etc/os-release
# PRETTY_NAME="Ubuntu 24.04.5 LTS"
# ID=ubuntu
# ID_LIKE=debian
# VERSION_CODENAME=noble

cat /etc/debian_version        # Debian: 13.x  (Ubuntu에도 있으나 Debian 기준 이름이 나옴)
lsb_release -a                 # lsb-release 패키지가 있으면
uname -r                       # 커널 판
```

스크립트에서는 `/etc/os-release`의 `ID`와 `ID_LIKE`로 계열을 판별합니다.

```bash
. /etc/os-release
case "$ID $ID_LIKE" in
  *debian*) echo "apt 계열" ;;
esac
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. apt 패키지 관리

```bash
sudo apt update                                   # 저장소 목록 갱신 (설치 전 항상)
apt list --upgradable                             # 갱신 가능한 패키지
sudo apt upgrade                                  # 설치된 패키지 갱신 (패키지 제거 없음)
sudo apt full-upgrade                             # 의존성 변경에 따른 설치·제거 포함

apt search nginx                                  # 검색
apt show nginx                                    # 정보
apt-cache policy curl                             # 설치 판·후보 판·저장소 우선순위
sudo apt install --no-install-recommends curl     # 추천 패키지 없이 설치
sudo apt remove curl                              # 제거 (설정 파일은 남음)
sudo apt purge curl                               # 설정 파일까지 제거
sudo apt autoremove                               # 더 이상 필요 없는 의존 패키지 제거
```

| 도구                  | 용도                                              |
|-----------------------|---------------------------------------------------|
| `apt`                 | 사람이 쓰는 명령. 출력 형식이 바뀔 수 있음        |
| `apt-get`·`apt-cache` | 스크립트용. 출력이 안정적. 자동화에서는 이쪽을 씀 |
| `dpkg`                | 설치된 `.deb` 직접 다루기                         |

```bash
dpkg -l curl                   # 설치 여부와 판 (ii = 설치됨)
dpkg -S /usr/bin/curl          # 이 파일을 설치한 패키지: curl
dpkg -L curl                   # 패키지가 설치한 파일 목록
apt-mark hold nginx            # 판 고정 (갱신 제외), 해제는 unhold
```

자동화 스크립트에서는 대화형 질문을 막습니다.

```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 저장소 설정

Ubuntu 24.04와 Debian 13부터 기본 저장소는 deb822 형식 파일로 설정합니다.

| 배포판        | 파일                                          |
|---------------|-----------------------------------------------|
| Ubuntu 24.04+ | `/etc/apt/sources.list.d/ubuntu.sources`      |
| Debian 13     | `/etc/apt/sources.list.d/debian.sources`      |
| 옛 형식       | `/etc/apt/sources.list` (한 줄에 저장소 하나) |

```text
# /etc/apt/sources.list.d/debian.sources
Types: deb
URIs: http://deb.debian.org/debian
Suites: trixie trixie-updates
Components: main
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
```

외부 저장소를 더할 때는 서명 키를 따로 두고 `Signed-By`로 그 저장소에만 연결합니다. `apt-key`는 더 이상 쓰지 않습니다.

```bash
sudo install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://example.com/repo.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/example.gpg
sudo tee /etc/apt/sources.list.d/example.sources >/dev/null <<'EOF'
Types: deb
URIs: https://example.com/apt
Suites: stable
Components: main
Signed-By: /etc/apt/keyrings/example.gpg
EOF
sudo apt update
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안 업데이트

### 6-1. 자동 보안 업데이트

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades      # 켜기 (/etc/apt/apt.conf.d/20auto-upgrades 생성)
sudo unattended-upgrade --dry-run --debug | tail     # 실제로 무엇을 갱신할지 미리 보기
```

설정은 `/etc/apt/apt.conf.d/50unattended-upgrades`에서 합니다. 기본값은 보안 저장소만 자동 갱신이며, 자동 재부팅(`Unattended-Upgrade::Automatic-Reboot`)은 꺼져 있습니다.

### 6-2. 재부팅이 필요한지 확인

```bash
ls /var/run/reboot-required 2>/dev/null && cat /var/run/reboot-required.pkgs
```

### 6-3. Ubuntu Pro (Ubuntu만)

```bash
pro status                  # 구독 상태와 ESM 저장소
sudo pro attach <토큰>      # 개인 사용은 5대까지 무료
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 판 업그레이드

업그레이드 전 공통 준비:

1. 백업과 스냅샷을 만듭니다.
2. `sudo apt update && sudo apt full-upgrade`로 현재 판을 최신으로 맞추고 재부팅합니다.
3. 외부 저장소(PPA 등)는 끄고, 업그레이드 뒤 새 판용으로 다시 켭니다.
4. 원격으로 할 때는 연결이 끊겨도 계속되도록 `tmux` 안에서 실행합니다.

```bash
# Ubuntu: LTS → 다음 LTS
sudo apt install -y update-manager-core
sudo do-release-upgrade               # LTS 간 업그레이드는 보통 새 LTS의 첫 부판(.1) 뒤에 제안됨

# Debian: 저장소의 판 이름을 바꾼 뒤 단계적으로
sudo sed -i 's/bookworm/trixie/g' /etc/apt/sources.list.d/*.sources /etc/apt/sources.list 2>/dev/null
sudo apt update
sudo apt upgrade --without-new-pkgs
sudo apt full-upgrade
```

Debian은 판마다 릴리스 노트에 따로 확인할 사항이 있으므로 업그레이드 전에 해당 판의 릴리스 노트를 읽습니다. 한 번에 두 판 이상 건너뛰지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용       | 명령                                                                                  | 기대 결과                             |
|------|-----------------|---------------------------------------------------------------------------------------|---------------------------------------|
| 1    | 판              | `cat /etc/os-release`                                                                 | 의도한 배포판·판·코드 이름            |
| 2    | 저장소          | `apt-get update`                                                                      | `Err`·`NO_PUBKEY` 없음                |
| 3    | 저장소 우선순위 | `apt-cache policy <패키지>`                                                           | 의도한 저장소의 후보 판               |
| 4    | 설치            | `dpkg -l <패키지>`                                                                    | `ii` 상태                             |
| 5    | 남은 갱신       | `apt list --upgradable`                                                               | 보안 갱신이 남아 있지 않음            |
| 6    | 자동 업데이트   | `systemctl status apt-daily-upgrade.timer`, `cat /etc/apt/apt.conf.d/20auto-upgrades` | 타이머 활성, `Unattended-Upgrade "1"` |
| 7    | 재부팅 필요     | `ls /var/run/reboot-required`                                                         | 파일 없음 (있으면 재부팅 계획)        |
| 8    | 망가진 패키지   | `sudo dpkg --audit`, `sudo apt-get check`                                             | 출력 없음                             |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                             | 원인                                           | 해결 방법                                                    |
|--------------------------------------------------|------------------------------------------------|--------------------------------------------------------------|
| `Could not get lock /var/lib/dpkg/lock-frontend` | 다른 apt·자동 업데이트가 실행 중               | `ps aux \| grep -E 'apt\|dpkg'`로 확인 후 끝날 때까지 기다림 |
| `NO_PUBKEY ...`                                  | 외부 저장소 서명 키 없음                       | 키 파일을 받아 `Signed-By`로 연결 (5절)                      |
| `dpkg was interrupted`                           | 설치 도중 중단                                 | `sudo dpkg --configure -a`                                   |
| `held broken packages`                           | 의존성 충돌, 고정된 패키지                     | `apt-mark showhold`, `apt-cache policy`로 원인 확인          |
| 판 업그레이드가 "새 판 없음"                     | LTS 간 업그레이드는 보통 `.1` 부판 뒤에 제안됨 | `/etc/update-manager/release-upgrades`의 `Prompt=lts` 확인   |
| 지원이 끝난 판에서 `apt update` 404              | 저장소가 old-releases로 이동                   | 새 판으로 업그레이드 (임시로는 old-releases 저장소)          |
| 설치 중 대화형 질문으로 자동화가 멈춤            | debconf 질문                                   | `DEBIAN_FRONTEND=noninteractive`                             |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [RHEL 계열](./rhel_family.md) — dnf를 쓰는 배포판
- [SUSE Linux](./suse_linux.md) — zypper를 쓰는 배포판
- [systemd 유닛 관리](./systemd_unit_management.md) — 서비스와 타이머
- [tmux](./tmux_guide.md) — 원격 업그레이드 중 연결 끊김 대비
- [Docker 설치와 초기 설정](../../02_infrastructure/containers/docker_install.md) — 외부 저장소 등록의 실제 예

---

## 참고 자료

- Ubuntu: [Ubuntu release cycle](https://ubuntu.com/about/release-cycle) — ★★★☆☆
- Ubuntu: [meta-release](https://changelogs.ubuntu.com/meta-release) — ★★★☆☆
- Debian: [Debian Releases](https://www.debian.org/releases/) — ★★★☆☆
- Debian: [Debian LTS](https://wiki.debian.org/LTS) — ★★★☆☆
- Debian: [sources.list(5)](https://manpages.debian.org/trixie/apt/sources.list.5.en.html) — ★★★☆☆
- endoflife.date: [Ubuntu](https://endoflife.date/ubuntu) · [Debian](https://endoflife.date/debian) — 날짜 교차 확인 — ★★☆☆☆

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
