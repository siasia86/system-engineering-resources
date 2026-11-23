---
name: procps-official-notes
description: procps-ng(ps·top·vmstat·free·pgrep)와 htop의 판, 출력 항목, 프로세스 상태 코드의 공식 출처 기준 사실 정리.
tags:
  - linux
  - process
  - procps
  - htop
last_checked: 2026-11-23
sources:
  - https://gitlab.com/procps-ng/procps
  - https://man7.org/linux/man-pages/man1/ps.1.html
  - https://man7.org/linux/man-pages/man1/top.1.html
  - https://man7.org/linux/man-pages/man8/vmstat.8.html
  - https://man7.org/linux/man-pages/man5/proc_pid_status.5.html
  - https://github.com/htop-dev/htop
---

# procps·htop 공식 참조 노트

## 1. 공식 소스

| 소스               | URL                                                          | 용도                         |
|--------------------|--------------------------------------------------------------|------------------------------|
| procps-ng 저장소   | https://gitlab.com/procps-ng/procps                          | 판, ps·top·vmstat·free·pgrep |
| ps(1)              | https://man7.org/linux/man-pages/man1/ps.1.html              | 출력 형식, 상태 코드         |
| top(1)             | https://man7.org/linux/man-pages/man1/top.1.html             | 요약 영역, 배치 모드         |
| vmstat(8)          | https://man7.org/linux/man-pages/man8/vmstat.8.html          | 열 의미                      |
| proc_pid_status(5) | https://man7.org/linux/man-pages/man5/proc_pid_status.5.html | /proc/PID/status 항목        |
| htop 저장소        | https://github.com/htop-dev/htop                             | htop 판                      |

## 2. 검증된 사실 (2026-11-23)

| 항목              | 값                                                                                                              | 출처               |
|-------------------|-----------------------------------------------------------------------------------------------------------------|--------------------|
| procps-ng 최신 판 | 4.0.7 (2026-08-12)                                                                                              | procps-ng releases |
| htop 최신 판      | 3.5.3 (2026-08-16)                                                                                              | htop releases      |
| ps 상태 코드      | `R` 실행 가능, `S` 깨울 수 있는 대기, `D` 깨울 수 없는 대기(주로 I/O), `Z` 좀비, `T` 정지, `I` 유휴 커널 스레드 | ps(1)              |
| ps 출력 지정      | `-o` 또는 `-eo`로 열 지정, `--sort`로 정렬                                                                      | ps(1)              |
| top 배치 모드     | `-b`(배치), `-n 횟수`로 스크립트·로그용 출력                                                                    | top(1)             |
| load average      | 1·5·15분 평균의 실행 가능(R)과 깨울 수 없는 대기(D) 상태 작업 수                                                | proc(5) loadavg    |
| vmstat 주요 열    | `r` 실행 대기, `b` 깨울 수 없는 대기, `si`·`so` 스왑 입출력, `us`·`sy`·`id`·`wa`·`st` CPU 비율                  | vmstat(8)          |
| free `available`  | 스왑 없이 새 프로그램이 쓸 수 있다고 추정한 메모리                                                              | free(1)            |

배포판 판은 위보다 낮을 수 있습니다. Ubuntu 24.04 계열에서 확인한 판은 procps 4.0.4, htop 3.3.0입니다.

## 3. 검증 기록

- 1차: procps-ng·htop 저장소의 release와 man7.org man 페이지에서 판과 항목을 확인했습니다.
- 2차: 설치된 procps 4.0.4·htop 3.3.0에서 `ps -eo`, `top -b -n 1`, `vmstat`, `free`, `/proc/1/status`를 실행해 출력 항목을 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
