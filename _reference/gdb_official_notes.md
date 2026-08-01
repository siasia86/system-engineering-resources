---
name: gdb-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man1/gdb.1.html
  - https://ftp.gnu.org/gnu/gdb/
  - https://sourceware.org/gdb/documentation/
---

# GDB 공식 참조 노트

## 1. GDB 개요

### 공식 소스

| 소스       | URL                                              | 용도              |
|------------|--------------------------------------------------|-------------------|
| gdb.1      | https://man7.org/linux/man-pages/man1/gdb.1.html | 옵션, 주요 명령어 |
| GNU FTP    | https://ftp.gnu.org/gnu/gdb/                     | 최신 버전 확인    |
| sourceware | https://sourceware.org/gdb/documentation/        | 공식 매뉴얼       |

### 검증된 사실 (2026-08-01)

| 항목             | 값                                              | 출처    |
|------------------|-------------------------------------------------|---------|
| 최신 stable 버전 | 17.2 (2026-05-10)                               | GNU FTP |
| 지원 언어        | C, C++, Fortran (man page 명시)                 | gdb.1   |
| 기본 실행 방법   | `gdb` / `gdb <program>` / `gdb <program> <pid>` | gdb.1   |
| 종료 명령어      | `quit` 또는 `exit`                              | gdb.1   |
| 온라인 도움말    | `help` 또는 `help <command>`                    | gdb.1   |

## 2. 주요 명령어 (gdb.1 man page 기반)

### 공식 소스

| 소스  | URL                                              | 용도        |
|-------|--------------------------------------------------|-------------|
| gdb.1 | https://man7.org/linux/man-pages/man1/gdb.1.html | 명령어 목록 |

### 검증된 사실 (2026-08-01)

| 명령어                   | 동작                                    | 출처  |
|--------------------------|-----------------------------------------|-------|
| `break <function\|line>` | 함수 또는 줄 번호에 브레이크포인트 설정 | gdb.1 |
| `run [arglist]`          | 프로그램 실행 (인수 선택)               | gdb.1 |
| `bt`                     | 스택 백트레이스 출력                    | gdb.1 |
| `print <expr>`           | 표현식 값 출력                          | gdb.1 |
| `continue`               | 브레이크포인트 이후 실행 재개           | gdb.1 |
| `next`                   | 다음 줄 실행 (함수 호출 step over)      | gdb.1 |
| `step`                   | 다음 줄 실행 (함수 호출 step into)      | gdb.1 |
| `list`                   | 현재 위치 주변 소스 코드 출력           | gdb.1 |
| `help [name]`            | 명령어 도움말 또는 전체 도움말          | gdb.1 |
| `quit` / `exit`          | GDB 종료                                | gdb.1 |

## 3. 시작 옵션 (gdb.1 man page 기반)

### 검증된 사실 (2026-08-01)

| 옵션                         | 동작                                | 출처  |
|------------------------------|-------------------------------------|-------|
| `-p <pid>`                   | 실행 중인 프로세스에 attach         | gdb.1 |
| `gdb <program> <pid>`        | 프로그램 + pid 동시 지정으로 attach | gdb.1 |
| `-x <file>`                  | 시작 시 파일에서 GDB 명령어 읽기    | gdb.1 |
| `--args <program> [args...]` | 프로그램에 인수 전달                | gdb.1 |
| `-q` / `--quiet`             | 배너 메시지 출력 안 함              | gdb.1 |
| `--batch`                    | 배치 모드 (스크립팅용)              | gdb.1 |

## 4. 약어(Abbreviation) 규칙

### 검증된 사실 (2026-08-01)

| 항목               | 값                                        | 출처  |
|--------------------|-------------------------------------------|-------|
| 옵션 약어 허용     | 고유하게 식별 가능한 약어는 모두 허용     | gdb.1 |
| 옵션 접두사 형식   | `--symbol=`, `-symbol=`, `--s=` 모두 허용 | gdb.1 |
| 단일 대시 + 전체명 | `--option`과 동일하게 동작                | gdb.1 |

## 5. deprecated / 주의사항

| 항목     | 상태                                                       | 출처  |
|----------|------------------------------------------------------------|-------|
| `attach` | 일부 시스템에서 `ptrace_scope` 설정으로 제한될 수 있습니다 | gdb.1 |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
