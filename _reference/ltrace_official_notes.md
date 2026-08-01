---
name: ltrace-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man1/ltrace.1.html
  - https://gitlab.com/cespedes/ltrace
---

# ltrace 공식 참조 노트

## 1. ltrace 개요

### 공식 소스

| 소스     | URL                                                 | 용도            |
|----------|-----------------------------------------------------|-----------------|
| ltrace.1 | https://man7.org/linux/man-pages/man1/ltrace.1.html | 옵션, 동작 설명 |
| GitLab   | https://gitlab.com/cespedes/ltrace                  | 최신 버전 확인  |

### 검증된 사실 (2026-08-01)

| 항목             | 값                                                   | 출처       |
|------------------|------------------------------------------------------|------------|
| 최신 stable 버전 | 0.8.1 (2025-09-16)                                   | GitLab API |
| 추적 대상        | 동적 라이브러리 호출, 프로세스가 수신하는 시그널     | ltrace.1   |
| strace와 차이    | strace는 syscall 추적, ltrace는 라이브러리 함수 추적 | ltrace.1   |
| 출력 시점        | 프로그램 종료 시 (또는 `-c`로 요약)                  | ltrace.1   |

## 2. 주요 옵션 (ltrace.1 man page 기반)

### 공식 소스

| 소스     | URL                                                 | 용도      |
|----------|-----------------------------------------------------|-----------|
| ltrace.1 | https://man7.org/linux/man-pages/man1/ltrace.1.html | 옵션 목록 |

### 검증된 사실 (2026-08-01)

| 옵션                   | 동작                                                  | 출처     |
|------------------------|-------------------------------------------------------|----------|
| `-p <pid>`             | 실행 중인 프로세스에 attach                           | ltrace.1 |
| `-f`                   | fork/clone된 자식 프로세스도 추적                     | ltrace.1 |
| `-o <file>`            | 출력 파일 지정                                        | ltrace.1 |
| `-e <filter>`          | 추적할 라이브러리 함수 필터 지정                      | ltrace.1 |
| `-l <library_pattern>` | 추적할 라이브러리 패턴 지정                           | ltrace.1 |
| `-x <filter>`          | 추적할 함수 필터 (라이브러리 내부 포함)               | ltrace.1 |
| `-L`                   | 기본 라이브러리 함수 추적 비활성화 (`-e`와 함께 사용) | ltrace.1 |
| `-S`                   | 시스템 콜도 함께 출력 (strace와 유사)                 | ltrace.1 |
| `-c`                   | 호출별 시간 및 횟수 집계 후 요약 출력                 | ltrace.1 |
| `-T`                   | 각 라이브러리 호출 소요 시간 출력                     | ltrace.1 |
| `-t` / `-tt` / `-ttt`  | 타임스탬프 출력 (단계별 정밀도 증가)                  | ltrace.1 |
| `-r`                   | 상대 타임스탬프 출력                                  | ltrace.1 |
| `-i`                   | 명령어 포인터 출력                                    | ltrace.1 |
| `-w <nr>`              | 스택 트레이스 nr 프레임 출력                          | ltrace.1 |
| `-D <mask>`            | 디버그 마스크 설정                                    | ltrace.1 |
| `-b` / `--no-signals`  | 수신 시그널 출력 비활성화                             | ltrace.1 |
| `-u <username>`        | 지정 사용자 권한으로 명령어 실행                      | ltrace.1 |
| `--demangle`           | C++ 심볼 이름 디맹글링                                | ltrace.1 |

## 3. deprecated / 주의사항

| 항목                  | 상태                                                     | 출처     |
|-----------------------|----------------------------------------------------------|----------|
| ltrace vs strace 혼용 | 시스템 콜 추적은 strace, 라이브러리 추적은 ltrace로 구분 | ltrace.1 |
| 동적 링크 필수        | 정적 링크 바이너리는 라이브러리 호출 추적 불가           | ltrace.1 |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
