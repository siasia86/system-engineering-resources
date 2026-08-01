---
name: strace-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man1/strace.1.html
  - https://strace.io/
  - https://github.com/strace/strace
---

# strace 공식 참조 노트

## 1. strace 개요

### 공식 소스

| 소스      | URL                                                 | 용도            |
|-----------|-----------------------------------------------------|-----------------|
| strace.1  | https://man7.org/linux/man-pages/man1/strace.1.html | 옵션, 동작 설명 |
| strace.io | https://strace.io/                                  | 공식 사이트     |
| GitHub    | https://github.com/strace/strace                    | 최신 버전 확인  |

### 검증된 사실 (2026-08-01)

| 항목               | 값                                        | 출처       |
|--------------------|-------------------------------------------|------------|
| 최신 stable 버전   | v7.1 (2026-06-15)                         | GitHub API |
| 추적 대상          | 시스템 콜, 프로세스가 수신하는 시그널     | strace.1   |
| 출력 형식          | 시스템 콜명, 인수, 반환값 (man page 명시) | strace.1   |
| 알 수 없는 syscall | `syscall_0x<num>` 형식으로 출력           | strace.1   |
| 시그널 출력 형식   | 시그널 심볼 + 디코딩된 siginfo            | strace.1   |

## 2. 주요 옵션 (strace.1 man page 기반)

### 공식 소스

| 소스     | URL                                                 | 용도      |
|----------|-----------------------------------------------------|-----------|
| strace.1 | https://man7.org/linux/man-pages/man1/strace.1.html | 옵션 목록 |

### 검증된 사실 (2026-08-01)

| 옵션              | 동작                                          | 출처     |
|-------------------|-----------------------------------------------|----------|
| `-p <pid>`        | 실행 중인 프로세스에 attach                   | strace.1 |
| `-f`              | fork/clone된 자식 프로세스도 추적             | strace.1 |
| `-o <file>`       | 출력 파일 지정                                | strace.1 |
| `-e trace=<set>`  | 추적할 syscall 집합 지정 (`-e t=<set>` 약어)  | strace.1 |
| `-e signal=<set>` | 추적할 시그널 집합 지정 (`-e s=<set>` 약어)   | strace.1 |
| `-T`              | 각 syscall 소요 시간 출력                     | strace.1 |
| `-c`              | syscall별 호출 횟수 및 시간 집계 후 요약 출력 | strace.1 |
| `-tt`             | 마이크로초 단위 타임스탬프 출력               | strace.1 |
| `-ttt`            | epoch 기준 초 + 마이크로초 출력               | strace.1 |
| `-r`              | 상대 타임스탬프 출력                          | strace.1 |
| `-s <size>`       | 출력 문자열 최대 길이 지정 (기본 32)          | strace.1 |
| `-x`              | 문자열 인수를 16진수로 출력                   | strace.1 |
| `-v`              | verbose (abbrev 없이 상세 출력)               | strace.1 |
| `-b <syscall>`    | 해당 syscall 도달 시 detach                   | strace.1 |
| `-E <var>=<val>`  | 환경 변수 추가/수정 후 실행                   | strace.1 |
| `-u <username>`   | 지정 사용자 권한으로 명령어 실행              | strace.1 |
| `--seccomp-bpf`   | seccomp-BPF 필터로 추적 가속                  | strace.1 |

## 3. -e trace 필터 문법

### 검증된 사실 (2026-08-01)

| 표현식              | 의미                            | 출처     |
|---------------------|---------------------------------|----------|
| `-e trace=open`     | `open` syscall만 추적           | strace.1 |
| `-e trace=file`     | 파일 관련 syscall 그룹 추적     | strace.1 |
| `-e trace=network`  | 네트워크 관련 syscall 그룹 추적 | strace.1 |
| `-e trace=process`  | 프로세스 관련 syscall 그룹 추적 | strace.1 |
| `-e trace=signal`   | 시그널 관련 syscall 그룹 추적   | strace.1 |
| `-e trace=ipc`      | IPC 관련 syscall 그룹 추적      | strace.1 |
| `-e trace=desc`     | fd 관련 syscall 그룹 추적       | strace.1 |
| `-e trace-fd=<set>` | 특정 fd 관련 syscall 추적       | strace.1 |

## 4. deprecated / 주의사항

| 항목                       | 상태                                             | 출처     |
|----------------------------|--------------------------------------------------|----------|
| `-e trace-fd` 구 옵션      | `-e trace-fds`, `-e fd`, `-e fds` 모두 동일 동작 | strace.1 |
| `-e verbose` / `-e abbrev` | `-e v`, `-e a` 약어 동일 동작                    | strace.1 |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
