---
name: suse-linux-official-notes
description: SUSE Linux Enterprise Server와 openSUSE(Leap·Tumbleweed)의 판·수명 주기, zypper, SLES 16 설치·관리 도구의 공식 출처 기준 사실 정리.
tags:
  - linux
  - suse
  - sles
  - opensuse
  - zypper
last_checked: 2026-11-23
sources:
  - https://www.suse.com/lifecycle/
  - https://documentation.suse.com/sles/16.0/
  - https://get.opensuse.org/leap/16.0/
  - https://get.opensuse.org/tumbleweed/
  - https://manpages.opensuse.org/Tumbleweed/zypper/zypper.8.en.html
  - https://endoflife.date/opensuse
---

# SUSE Linux 공식 참조 노트

## 1. 공식 소스

| 소스                    | URL                                                              | 용도                           |
|-------------------------|------------------------------------------------------------------|--------------------------------|
| SUSE product lifecycle  | https://www.suse.com/lifecycle/                                  | SLES 판별 출시일·지원 종료     |
| SLES 16.0 documentation | https://documentation.suse.com/sles/16.0/                        | 설치(Agama)·관리(Cockpit) 안내 |
| openSUSE Leap 16.0      | https://get.opensuse.org/leap/16.0/                              | Leap 판과 지원 기간            |
| openSUSE Tumbleweed     | https://get.opensuse.org/tumbleweed/                             | 롤링 릴리스                    |
| zypper(8) man page      | https://manpages.opensuse.org/Tumbleweed/zypper/zypper.8.en.html | zypper 명령                    |
| endoflife.date          | https://endoflife.date/opensuse                                  | Leap 출시일 교차 확인(보조)    |

## 2. 판과 수명 주기

### 검증된 사실 (2026-11-23)

| 항목               | 값                                                     | 출처                                     |
|--------------------|--------------------------------------------------------|------------------------------------------|
| SLES 16.0          | 2025-11-04 출시, 일반 지원 2027-11-30, LTSS 2030-11-30 | suse.com/lifecycle                       |
| SLES 16.1          | 2026-11-10 출시, 일반 지원 2028-11-30, LTSS 2031-11-30 | suse.com/lifecycle                       |
| SLES 16 제품군     | 일반 지원 2035-11-30, LTS 2038-11-30                   | suse.com/lifecycle                       |
| SLES 15 SP7        | 2025-06-17 출시                                        | suse.com/lifecycle, endoflife.date(보조) |
| openSUSE Leap 16.0 | 24개월 지원                                            | get.opensuse.org                         |
| Leap 16.0 출시일   | 2025-10-01                                             | endoflife.date(보조)                     |
| Tumbleweed         | 판 번호 없이 계속 갱신되는 롤링 릴리스                 | get.opensuse.org                         |

## 3. 패키지와 관리

| 항목             | 내용                                                                        |
|------------------|-----------------------------------------------------------------------------|
| 패키지 관리자    | `zypper` (Leap 16.0 컨테이너에서 1.14.101), 저수준은 `rpm`                  |
| 저장소           | `zypper lr`(목록), `zypper ar`(추가), `zypper ref`(메타데이터 갱신)         |
| 검색·정보·설치   | `zypper se`, `zypper if`, `zypper in`(`--no-recommends`로 추천 패키지 제외) |
| 업데이트         | `zypper lu`(목록), `zypper up`(갱신), Tumbleweed는 `zypper dup`             |
| 패치             | `zypper lp`·`zypper patch` (SLES 보안 패치 단위)                            |
| 재시작 필요 확인 | `zypper ps -s` (lsof 패키지 필요)                                           |
| SLES 등록        | `SUSEConnect`로 등록해야 SUSE 저장소를 씀                                   |
| SLES 16 설치     | Agama 설치 프로그램. AutoYaST 프로필은 Agama JSON 프로필로 변환             |
| SLES 16 웹 관리  | Cockpit                                                                     |

## 4. 검증 기록

- 1차: suse.com lifecycle 표, SLES 16.0 문서 목록, get.opensuse.org에서 판·날짜·도구를 확인했습니다.
- 2차: `opensuse/leap:16.0` 컨테이너에서 `/etc/os-release`, `zypper lr`·`se`·`in`·`if`·`lu`·`ps`를 실행해 대조했습니다(`zypper ps`는 lsof가 없으면 실패함을 확인).
- SLES 자체는 구독이 필요해 컨테이너로 시험하지 않았고, 명령은 openSUSE Leap과 같은 zypper 기준입니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
