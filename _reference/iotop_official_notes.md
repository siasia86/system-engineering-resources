---
name: iotop-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man8/iotop.8.html
  - https://github.com/Tomas-M/iotop
---

# iotop 공식 참조 노트

## 1. iotop 개요

### 공식 소스

| 소스    | URL                                                | 용도            |
|---------|----------------------------------------------------|-----------------|
| iotop.8 | https://man7.org/linux/man-pages/man8/iotop.8.html | 옵션, 동작 설명 |
| GitHub  | https://github.com/Tomas-M/iotop                   | 최신 버전 확인  |

### 검증된 사실 (2026-08-01)

| 항목             | 값                                                                                            | 출처       |
|------------------|-----------------------------------------------------------------------------------------------|------------|
| 최신 stable 버전 | v1.31 (2026-01-21)                                                                            | GitHub API |
| 최소 커널 버전   | Linux 2.6.20 이상 필요                                                                        | iotop.8    |
| 필요 커널 설정   | CONFIG_TASK_DELAY_ACCT, CONFIG_TASK_IO_ACCOUNTING, CONFIG_TASKSTATS, CONFIG_VM_EVENT_COUNTERS | iotop.8    |
| 비-root 실행     | `cap_net_admin` capability 부여 시 가능                                                       | iotop.8    |
| Total vs Current | Total: 프로세스↔커널 블록 서브시스템, Current: 블록 서브시스템↔하드웨어                       | iotop.8    |

## 2. 주요 옵션 (iotop.8 man page 기반)

### 공식 소스

| 소스    | URL                                                | 용도      |
|---------|----------------------------------------------------|-----------|
| iotop.8 | https://man7.org/linux/man-pages/man8/iotop.8.html | 옵션 목록 |

### 검증된 사실 (2026-08-01)

| 옵션                     | 동작                                  | 출처    |
|--------------------------|---------------------------------------|---------|
| `-o`, `--only`           | 실제 I/O를 발생시키는 프로세스만 표시 | iotop.8 |
| `-b`, `--batch`          | 배치 모드 (스크립팅/파이프 사용 시)   | iotop.8 |
| `-n NUM`, `--iter=NUM`   | 반복 횟수 지정 후 종료                | iotop.8 |
| `-d SEC`, `--delay=SEC`  | 샘플링 간격(초) 설정                  | iotop.8 |
| `-p PID`, `--pid=PID`    | 특정 프로세스 PID 지정                | iotop.8 |
| `-u USER`, `--user=USER` | 특정 사용자의 프로세스만 표시         | iotop.8 |
| `-P`, `--processes`      | 스레드 대신 프로세스 단위로 표시      | iotop.8 |
| `-a`, `--accumulated`    | 누적 I/O 표시 (시작 이후 전체 합계)   | iotop.8 |
| `-A`, `--accum-bw`       | 누적 대역폭 표시                      | iotop.8 |
| `-v`, `--version`        | 버전 출력                             | iotop.8 |

🟡 `--accumulated`와 `--accum-bw`는 상호 배타적 옵션입니다.

## 3. 키보드 단축키 (인터랙티브 모드)

### 검증된 사실 (2026-08-01)

| 키            | 동작                                            | 출처    |
|---------------|-------------------------------------------------|---------|
| `←` / `→`     | 정렬 컬럼 선택                                  | iotop.8 |
| `r` / `space` | 정렬 순서 반전                                  | iotop.8 |
| `o`           | `--only` 옵션 토글                              | iotop.8 |
| `p`           | `--processes` 옵션 토글                         | iotop.8 |
| `a`           | `--accumulated` / `--accum-bw` / 일반 모드 순환 | iotop.8 |
| `i`           | 프로세스 I/O 우선순위 변경                      | iotop.8 |
| `q`           | 종료                                            | iotop.8 |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
