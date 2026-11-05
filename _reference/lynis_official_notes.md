---
name: lynis-official-notes
description: Lynis 공식 릴리스, 설치·서명, 명령·옵션, 프로필, 보고서 형식, Hardening index 계산을 3.1.7 소스와 CISOfy 공식 자료로 확인한 노트.
tags:
  - lynis
  - security-audit
  - hardening
last_checked: 2026-11-05
sources:
  - https://github.com/CISOfy/lynis/tree/3.1.7
  - https://github.com/CISOfy/lynis/blob/3.1.7/CHANGELOG.md
  - https://github.com/CISOfy/lynis/blob/3.1.7/default.prf
  - https://github.com/CISOfy/lynis/blob/3.1.7/include/report
  - https://github.com/CISOfy/lynis/blob/3.1.7/include/parameters
  - https://github.com/CISOfy/lynis/blob/3.1.7/db/tests.db
  - https://cisofy.com/downloads/lynis/
  - https://packages.cisofy.com/community/
---

# Lynis Official Notes

## 1. 확인 범위

2026-11-05에 GitHub API, 3.1.7 태그 소스(실행하지 않고 읽기만 함), CISOfy 다운로드 페이지와 공식 저장소 안내를 확인했습니다. 공식 tarball은 내려받아 SHA256과 GPG 서명만 검증했으며 Lynis 자체는 실행하지 않았습니다.

## 2. Version status

- 최신 릴리스: `3.1.7`(2026-06-25, CachyOS 감지와 EOL DB 갱신). 직전 `3.1.6`(2025-10-22), `3.1.5`(2025-07-29). 라이선스 GPL-3.0, 저장소 archive 아님.
- 3.1.6 변경: 6개월 이상 지난 릴리스를 오래된 것으로 보고 화면에 표시, EOL 상태가 불명확하면 알림.
- GitHub 릴리스에는 첨부 파일이 없고 immutable release가 아닙니다. 태그 `3.1.7`이 가리키는 commit `2e99f92265760b73fd6b139868eb8d4116624030`은 GitHub에서 서명 검증됨(verified)으로 표시됩니다.
- 작업 서버(Ubuntu 24.04) 기본 저장소의 후보 버전은 `3.0.9-1`입니다(`apt-cache policy lynis`).

## 3. 설치와 무결성

- 공식 tarball: `https://downloads.cisofy.com/lynis/lynis-3.1.7.tar.gz`와 `.asc`. 다운로드 페이지 게시 SHA256 `b5314a07fd85fa3ffc7da57b508f0108ec3280d84e4af823f805d95cbbc2428c`와 내려받은 파일이 일치했습니다.
- GPG: `https://packages.cisofy.com/keys/cisofy-software-public.key`를 임시 키링에 넣고 `gpg --verify` 결과 `Good signature from "CISOfy software signing <software@cisofy.com>"`. 서명 subkey `3E82FB7C68F57341349ED2C17A9A1D9D5B27C6D3`, 주 키 지문 `84FA A998 3B24 AEF2 4D6C 87F1 FEBB 7D18 1257 6482`(rsa4096, 2021-06-22 생성, 2030-10-21 만료).
- 공식 저장소 안내: Debian 계열은 키를 `gpg --dearmor`로 `/etc/apt/trusted.gpg.d/cisofy-software-public.gpg`에 두고 `deb [arch=amd64,arm64 signed-by=...] https://packages.cisofy.com/community/lynis/deb/ stable main`. 같은 페이지에 `apt-key add` 방식도 남아 있습니다. RHEL·Fedora는 `baseurl=https://packages.cisofy.com/community/lynis/rpm/`, `gpgkey=https://packages.cisofy.com/keys/cisofy-software-rpms-public.key`, `gpgcheck=1`. 서버가 많으면 사내 저장소·프록시를 두라는 fair-use 정책과 HTTP 429 차단 안내가 있습니다.
- README: Git으로 받아 설치 없이 실행할 수 있으며, root로 실행하려면 `chown -R 0:0`으로 소유자를 바꾸라고 안내합니다.

## 4. 명령과 옵션 (3.1.7 소스)

- 명령: `audit system`, `audit system remote <host>`, `audit dockerfile <file>`, `show ...`, `update info`, `generate hostids`, `generate systemd-units`.
- `audit system remote`는 tarball 생성·scp·ssh 실행·결과 회수 단계를 화면에 출력할 뿐 직접 실행하지 않습니다(`include/helper_system_remote_scan`).
- `--cronjob`은 `audit system`, quick 모드, 색 없음을 함께 켭니다. `--warnings-only`는 경고만 표시하고 나머지 출력을 끕니다. `--tests`는 지정 문자열 안에 테스트 ID가 있는지로 실행 여부를 정합니다.
- 경로: root 실행 기본 `/var/log/lynis.log`, `/var/log/lynis-report.dat`. 일반 사용자는 `$HOME/lynis.log`, `$HOME/lynis-report.dat`. 보고서는 실행 시작 때 새로 씁니다(`echo "# Lynis Report" > REPORTFILE`). symlink면 실행을 멈춥니다. 파일 생성 umask 027.
- `error-on-warnings=yes`이고 경고가 1개 이상이면 종료 코드 78.
- `db/tests.db` 테스트 447개: 분류 security 442, performance 4, basics 1. 그룹 39개(ports_packages 41, authentication 36, boot_services 27, nameservices 23, logging 22, filesystems 20, file_integrity 18, ssh 5 등).

## 5. 프로필

- `default.prf`는 고치지 말고 바꿀 값만 같은 디렉토리의 `custom.prf`에 두라고 파일 머리말에 적혀 있습니다. 프로필 탐색 순서 `/usr/local/etc/lynis`, `/etc/lynis`, `/usr/local/lynis`, `.`(`include/functions`의 DiscoverProfiles). 프로필은 엄격하게 검사합니다.
- 기본값: `error-on-warnings=no`, `machine-role=server`, `quick=yes`, `test-scan-mode=full`, `skip-plugins=no`, `upload=no`. `skip-test=SSH-7408` 또는 `skip-test=SSH-7408:permitrootlogin` 형식. `config-data=sysctl;...` 줄로 기대 커널 값 정의.

## 6. 보고서와 Hardening index

- 보고서 항목: `hostname`, `lynis_version`, `os_name`, `os_version`, `report_datetime_start`·`report_datetime_end`(`YYYY-MM-DD HH:MM:SS`), `hardening_index`, `lynis_tests_done`, `tests_executed`, `tests_skipped`, `warning[]`·`suggestion[]`(`테스트ID|메시지|상세|해결 방법|`), `vulnerable_package[]`, `manual[]`, `details[]`.
- 계산: 테스트마다 `AddHP <점수> <최대>`로 합산하고 `HPINDEX = HPPOINTS * 100 / HPTOTAL`. 점수가 0이면 1/100으로 둡니다.
- 화면 설명 구간: 50 미만 "System has not or a low amount been hardened", 50~79 "...could use additional hardening", 80~89 "...decent hardened", 90 이상 "...well hardened".
- 소스 주석: 첫인상이나 비슷한 시스템 비교용이며 최고점이어도 보안 문제가 없다는 뜻은 아님("Getting the maximum score ... does not indicate that the system is fully secured").
- 화면 요약 순서: Warnings, Suggestions, Lynis security scan details.

## 7. 적용 범위와 제한

- Lynis 실행 결과 화면과 실제 보고서는 관찰하지 않았습니다. 가이드 7절 집계 스크립트는 위 형식대로 만든 예시 보고서 파일로만 시험했습니다.
- README의 준수 점검(ISO27001, PCI-DSS, HIPAA) 언급과 달리 준수 보고서는 Enterprise판 기능으로 안내됩니다. 오픈소스판 결과를 특정 규정 준수 판정으로 쓰지 않습니다.
