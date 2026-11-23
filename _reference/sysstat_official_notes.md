---
name: sysstat-official-notes
description: sysstat(sar·sadc·mpstat·iostat·pidstat)의 판, 수집 방식, 기록 위치의 공식 출처 기준 사실 정리.
tags:
  - linux
  - performance
  - sysstat
  - sar
last_checked: 2026-11-23
sources:
  - https://sysstat.github.io/
  - https://github.com/sysstat/sysstat
  - https://man7.org/linux/man-pages/man1/sar.1.html
  - https://man7.org/linux/man-pages/man1/mpstat.1.html
  - https://man7.org/linux/man-pages/man1/iostat.1.html
---

# sysstat 공식 참조 노트

## 1. 공식 소스

| 소스           | URL                                                 | 용도            |
|----------------|-----------------------------------------------------|-----------------|
| sysstat 홈     | https://sysstat.github.io/                          | 판, 구성 도구   |
| sysstat 저장소 | https://github.com/sysstat/sysstat                  | 태그, 변경 이력 |
| sar(1)         | https://man7.org/linux/man-pages/man1/sar.1.html    | 보고 종류, 옵션 |
| mpstat(1)      | https://man7.org/linux/man-pages/man1/mpstat.1.html | CPU별 통계      |
| iostat(1)      | https://man7.org/linux/man-pages/man1/iostat.1.html | 장치 I/O 통계   |

## 2. 검증된 사실 (2026-11-23)

| 항목             | 값                                                                                                                              | 출처                |
|------------------|---------------------------------------------------------------------------------------------------------------------------------|---------------------|
| 최신 판          | 12.8.1                                                                                                                          | sysstat 홈, 태그    |
| 구성 도구        | `sar`(보고), `sadc`·`sa1`·`sa2`(수집·일일 요약), `sadf`(기록 내보내기), `mpstat`, `iostat`, `pidstat`, `cifsiostat`, `tapestat` | sysstat 홈          |
| 수집 방식        | systemd 타이머(`sysstat-collect.timer`)가 `sa1`을 실행해 기록 파일에 저장                                                       | 설치된 단위 파일    |
| 기록 위치        | Debian·Ubuntu `/var/log/sysstat/saDD`, RHEL 계열 `/var/log/sa/saDD`                                                             | 설치된 패키지       |
| Debian `ENABLED` | `/etc/default/sysstat`의 `ENABLED`는 cron용 `debian-sa1`에서만 확인. systemd 타이머 수집과는 별개                               | Ubuntu 24.04 패키지 |
| 주요 sar 보고    | `-u` CPU, `-r` 메모리, `-b` I/O, `-n DEV` 네트워크 인터페이스, `-q` 실행 큐·load, `-f 파일` 과거 기록                           | sar(1)              |

## 3. 검증 기록

- 1차: sysstat 홈·저장소 태그와 man7.org man 페이지에서 판·도구·보고 종류를 확인했습니다.
- 2차: Ubuntu 24.04의 sysstat 12.6.1과 `rockylinux/rockylinux:10` 컨테이너의 sysstat에서 단위 파일, 기록 위치, `sar`·`mpstat`·`iostat` 출력을 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
