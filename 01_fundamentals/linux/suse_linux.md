# SUSE Linux (SLES·openSUSE)
<!-- reference: _reference/suse_linux_official_notes.md -->

SUSE Linux Enterprise Server(SLES)와 커뮤니티 배포판 openSUSE(Leap·Tumbleweed)의 관계, 판과 지원 기간, 패키지 관리(zypper)를 다룹니다. 다른 배포판을 쓰던 사람이 SUSE 서버를 만났을 때 판을 확인하고 패키지를 다룰 수 있도록 개념과 기본 명령 중심으로 썼습니다.

- 기준 판: SLES 16.1(2026-11-10), openSUSE Leap 16.0
- 예제 시험: 2026-11-23, `opensuse/leap:16.0` 컨테이너(zypper 1.14.101)에서 3·4절 명령을 실행해 확인. SLES는 구독이 필요해 시험하지 않았고, 명령은 같은 zypper 기준

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 판과 지원 기간](#2-판과-지원-기간) / [3. 판 확인](#3-판-확인)             |
| [4. zypper 패키지 관리](#4-zypper-패키지-관리) / [5. 관리 도구](#5-관리-도구) / [6. 검증](#6-검증) |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                 |

---

## 1. 개요

| 배포판              | 성격                                                        | 판 체계                     |
|---------------------|-------------------------------------------------------------|-----------------------------|
| SLES                | SUSE의 상용 서버 배포판. 등록(`SUSEConnect`) 뒤 저장소 사용 | 16.0, 16.1 … (매년 부판)    |
| openSUSE Leap       | SLES와 같은 바탕으로 만든 무료 배포판                       | 16.0 … (판마다 24개월 지원) |
| openSUSE Tumbleweed | 계속 최신 패키지로 갱신되는 롤링 릴리스                     | 판 번호 없음                |

패키지는 RPM이지만 RHEL 계열과 저장소·도구가 달라 패키지 이름과 명령이 다릅니다. 패키지 관리자는 `zypper`입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 판과 지원 기간

| 판                  | 출시       | 지원                                  |
|---------------------|------------|---------------------------------------|
| SLES 16.1           | 2026-11-10 | 일반 지원 2028-11-30, LTSS 2031-11-30 |
| SLES 16.0           | 2025-11-04 | 일반 지원 2027-11-30, LTSS 2030-11-30 |
| SLES 16 제품군 전체 | -          | 일반 지원 2035-11-30, LTS 2038-11-30  |
| SLES 15 SP7         | 2025-06-17 | 15 계열                               |
| openSUSE Leap 16.0  | 2025-10    | 24개월                                |

SLES는 부판마다 지원이 끝나므로, 제품군 지원 기간 안에서도 부판을 따라 올려야 합니다. LTSS는 부판을 더 오래 쓰기 위한 유료 연장입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 판 확인

```bash
cat /etc/os-release
# NAME="openSUSE Leap"
# VERSION="16.0"
# PRETTY_NAME="openSUSE Leap 16.0"

zypper --version               # zypper 1.14.x
SUSEConnect --status-text      # SLES: 등록 상태와 활성 모듈
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. zypper 패키지 관리

```bash
sudo zypper refresh                        # 저장소 메타데이터 갱신 (줄여서 ref)
zypper repos                               # 저장소 목록 (lr)
zypper search -x tar                       # 이름이 정확히 같은 패키지 검색 (se)
zypper info tar                            # 정보 (if)
sudo zypper install --no-recommends tar    # 추천 패키지 없이 설치 (in)
sudo zypper remove tar                     # 제거 (rm)

zypper list-updates                        # 갱신 목록 (lu)
sudo zypper update                         # 갱신 (up)
zypper list-patches                        # 보안·버그 패치 목록 (lp)
sudo zypper patch                          # 패치 적용
sudo zypper dist-upgrade                   # Tumbleweed 갱신 (dup)

sudo zypper addlock nginx                  # 판 고정 (al), 해제는 removelock (rl)
zypper ps -s                               # 재시작이 필요한 프로세스 (lsof 필요)
```

| RHEL 계열 (dnf)          | SUSE (zypper)                      |
|--------------------------|------------------------------------|
| `dnf makecache`          | `zypper refresh`                   |
| `dnf repolist`           | `zypper repos`                     |
| `dnf install`            | `zypper install`                   |
| `dnf upgrade`            | `zypper update`                    |
| `dnf upgrade --security` | `zypper patch --category security` |
| `dnf versionlock add`    | `zypper addlock`                   |
| `dnf needs-restarting`   | `zypper ps`                        |

자동화에서는 `zypper -n`(질문하지 않음)과 `-q`(조용히)를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 관리 도구

| 도구        | 용도                                                                      |
|-------------|---------------------------------------------------------------------------|
| Agama       | SLES 16의 설치 프로그램. 자동 설치는 JSON 프로필 (AutoYaST 프로필은 변환) |
| Cockpit     | SLES 16 문서가 안내하는 웹 관리 화면                                      |
| SUSEConnect | SLES 등록, 모듈·확장 저장소 활성                                          |
| YaST        | 이전 판(SLES 15, Leap 15)의 설치·관리 도구                                |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용   | 명령                        | 기대 결과                  |
|------|-------------|-----------------------------|----------------------------|
| 1    | 판          | `cat /etc/os-release`       | 의도한 배포판·판           |
| 2    | 등록 (SLES) | `SUSEConnect --status-text` | `Registered`               |
| 3    | 저장소      | `sudo zypper refresh`       | 오류 없음                  |
| 4    | 남은 패치   | `zypper list-patches`       | 보안 패치가 남아 있지 않음 |
| 5    | 설치        | `rpm -q <패키지>`           | 판 출력                    |
| 6    | 재시작 필요 | `zypper ps -s`              | 재시작할 프로세스 없음     |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                        | 원인                              | 해결 방법                                       |
|---------------------------------------------|-----------------------------------|-------------------------------------------------|
| SLES에서 저장소가 비어 있음                 | 등록 안 됨                        | `SUSEConnect -r <등록 코드>`                    |
| `zypper ps`가 `install package 'lsof'` 오류 | lsof 없음                         | `zypper install lsof`                           |
| 다른 zypper가 잠금을 잡고 있다는 메시지     | 다른 패키지 작업이 실행 중        | 실행 중인 zypper·자동 갱신이 끝날 때까지 기다림 |
| RHEL용 RPM 설치 시 의존성 오류              | 패키지 이름·배치가 다름           | SUSE 저장소의 패키지 사용 (`zypper search`)     |
| Tumbleweed에서 `zypper up` 뒤 문제          | 롤링 릴리스는 `dup`로 갱신해야 함 | `zypper dup`                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ubuntu·Debian](./ubuntu_debian.md) — apt를 쓰는 배포판
- [RHEL 계열](./rhel_family.md) — dnf를 쓰는 배포판
- [systemd 유닛 관리](./systemd_unit_management.md) — 서비스와 타이머

---

## 참고 자료

- SUSE: [Product Support Lifecycle](https://www.suse.com/lifecycle/) — ★★★☆☆
- SUSE: [SLES 16.0 Documentation](https://documentation.suse.com/sles/16.0/) — ★★★☆☆
- openSUSE: [Leap 16.0](https://get.opensuse.org/leap/16.0/) · [Tumbleweed](https://get.opensuse.org/tumbleweed/) — ★★★☆☆
- openSUSE: [zypper(8)](https://manpages.opensuse.org/Tumbleweed/zypper/zypper.8.en.html) — ★★★☆☆
- openSUSE: [Managing software with command line tools](https://doc.opensuse.org/documentation/leap/reference/html/book-reference/cha-sw-cl.html) — ★★★☆☆

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
