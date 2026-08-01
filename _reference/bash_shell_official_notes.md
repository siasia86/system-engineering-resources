---
name: bash-shell-official-notes
last_checked: 2026-08-01
sources:
  - https://www.gnu.org/software/bash/manual/bash.html
  - https://man7.org/linux/man-pages/man1/bash.1.html
  - https://ftp.gnu.org/gnu/bash/
---

# Bash Shell 공식 참조 노트

## 1. Bash 개요

### 공식 소스

| 소스        | URL                                                | 용도                |
|-------------|----------------------------------------------------|---------------------|
| bash manual | https://www.gnu.org/software/bash/manual/bash.html | 전체 기능 공식 참조 |
| bash.1      | https://man7.org/linux/man-pages/man1/bash.1.html  | 옵션, 내장 명령어   |
| GNU FTP     | https://ftp.gnu.org/gnu/bash/                      | 최신 버전 확인      |

### 검증된 사실 (2026-08-01)

| 항목                  | 값                                                                         | 출처        |
|-----------------------|----------------------------------------------------------------------------|-------------|
| 최신 stable 버전      | 5.3 (2025-07-30)                                                           | GNU FTP     |
| 공식 설명             | GNU Bourne-Again SHell                                                     | bash manual |
| 기본 설정 파일        | 인터랙티브 로그인: `~/.bash_profile` / `~/.bash_login` / `~/.profile` 순서 | bash manual |
| 비로그인 인터랙티브   | `~/.bashrc` 읽음                                                           | bash manual |
| 비인터랙티브 스크립트 | `BASH_ENV` 변수가 지정된 파일 읽음 (없으면 무시)                           | bash manual |

## 2. Interactive vs Non-interactive Shell (§6.3 기반)

### 공식 소스

| 소스        | URL                                                | 용도                    |
|-------------|----------------------------------------------------|-------------------------|
| bash manual | https://www.gnu.org/software/bash/manual/bash.html | §6.3 Interactive Shells |

### 검증된 사실 (2026-08-01)

| 항목                        | 값                                                     | 출처        |
|-----------------------------|--------------------------------------------------------|-------------|
| 인터랙티브 셸 판별          | `$-`에 `i` 포함 여부 또는 `$PS1` 설정 여부로 확인      | bash manual |
| 인터랙티브 판별 방법 (공식) | `bash -i`, `-c` 없이 터미널 연결 시 인터랙티브         | bash manual |
| PS1 설정                    | 인터랙티브 셸에서만 기본 설정됨                        | bash manual |
| BASH_ENV 사용               | 쉘 스크립트 실행 시 참조 (비인터랙티브 스크립트)       | bash manual |
| 인터랙티브 동작             | job control, history, `interactive_comments` 옵션 활성 | bash manual |
| SIGHUP 처리                 | 인터랙티브 셸 종료 시 자식에게 SIGHUP 재전송           | bash manual |
| 에러 처리 차이              | 비인터랙티브 셸에서 syntax error 발생 시 종료          | bash manual |

## 3. Bash 시작 옵션 (bash.1 man page 기반)

### 공식 소스

| 소스   | URL                                               | 용도      |
|--------|---------------------------------------------------|-----------|
| bash.1 | https://man7.org/linux/man-pages/man1/bash.1.html | 옵션 목록 |

### 검증된 사실 (2026-08-01)

| 옵션          | 동작                                           | 출처   |
|---------------|------------------------------------------------|--------|
| `-c <string>` | 문자열을 명령어로 실행 (비인터랙티브)          | bash.1 |
| `-i`          | 인터랙티브 모드로 강제 실행                    | bash.1 |
| `-l`          | 로그인 셸로 동작                               | bash.1 |
| `-s`          | 표준 입력에서 명령어 읽기                      | bash.1 |
| `-n`          | 명령어 읽기만 하고 실행하지 않음 (문법 검사용) | bash.1 |
| `-x`          | 실행 전 명령어 출력 (디버깅용)                 | bash.1 |
| `-e`          | 명령어 실패(exit code != 0) 시 즉시 종료       | bash.1 |
| `-u`          | 미설정 변수 참조 시 에러                       | bash.1 |
| `-o pipefail` | 파이프라인 중 하나라도 실패 시 전체 실패       | bash.1 |
| `--norc`      | `~/.bashrc` 읽지 않음 (비로그인 인터랙티브)    | bash.1 |
| `--noprofile` | `~/.bash_profile` 등 읽지 않음 (로그인 셸)     | bash.1 |

## 4. 파일 리다이렉션 (bash manual §3.6 기반)

### 공식 소스

| 소스        | URL                                                | 용도              |
|-------------|----------------------------------------------------|-------------------|
| bash manual | https://www.gnu.org/software/bash/manual/bash.html | §3.6 Redirections |

### 검증된 사실 (2026-08-01)

| 리다이렉션 | 의미                                         | 출처        |
|------------|----------------------------------------------|-------------|
| `>`        | 표준 출력을 파일로 (덮어쓰기)                | bash manual |
| `>>`       | 표준 출력을 파일로 (추가)                    | bash manual |
| `<`        | 파일을 표준 입력으로                         | bash manual |
| `2>`       | 표준 오류를 파일로                           | bash manual |
| `2>&1`     | 표준 오류를 표준 출력으로 합치기             | bash manual |
| `&>`       | 표준 출력 + 표준 오류를 파일로               | bash manual |
| `<<EOF`    | Here-document (EOF까지를 표준 입력으로 전달) | bash manual |
| `<<<`      | Here-string (문자열을 표준 입력으로 전달)    | bash manual |

## 5. deprecated / 주의사항

| 항목           | 상태                                                          | 출처        |
|----------------|---------------------------------------------------------------|-------------|
| `#!/bin/sh`    | POSIX sh 호환, bash 전용 기능(`[[ ]]`, `$'...'` 등) 사용 불가 | bash manual |
| `let` / `expr` | 산술 연산은 `$(( ))` 또는 `(( ))` 사용 권장                   | bash manual |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
