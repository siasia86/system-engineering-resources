---
name: valgrind-official-notes
last_checked: 2026-08-01
sources:
  - https://valgrind.org/docs/manual/manual.html
  - https://valgrind.org/docs/manual/mc-manual.html
  - https://sourceware.org/pub/valgrind/
---

# Valgrind 공식 참조 노트

## 1. Valgrind 개요

### 공식 소스

| 소스            | URL                                             | 용도                   |
|-----------------|-------------------------------------------------|------------------------|
| valgrind manual | https://valgrind.org/docs/manual/manual.html    | 전체 도구 개요, 사용법 |
| memcheck manual | https://valgrind.org/docs/manual/mc-manual.html | 메모리 오류 검사 상세  |
| sourceware FTP  | https://sourceware.org/pub/valgrind/            | 최신 버전 확인         |

### 검증된 사실 (2026-08-01)

| 항목             | 값                                                     | 출처            |
|------------------|--------------------------------------------------------|-----------------|
| 최신 stable 버전 | 3.27.1 (2026-05-20)                                    | sourceware FTP  |
| 기본 도구        | Memcheck (기본값, 메모리 오류 검사)                    | valgrind manual |
| 주요 도구 목록   | Memcheck, Callgrind, Cachegrind, Helgrind, DRD, Massif | valgrind manual |
| 도구 선택 옵션   | `--tool=<toolname>` (기본값: memcheck)                 | valgrind manual |
| 실행 방식        | `valgrind [options] <program> [args]`                  | valgrind manual |

## 2. Memcheck 오류 분류 (mc-manual 기반)

### 공식 소스

| 소스            | URL                                             | 용도            |
|-----------------|-------------------------------------------------|-----------------|
| memcheck manual | https://valgrind.org/docs/manual/mc-manual.html | 오류 유형, 출력 |

### 검증된 사실 (2026-08-01)

| 오류 유형                          | 설명                                                 | 출처           |
|------------------------------------|------------------------------------------------------|----------------|
| uninitialised value use            | 초기화되지 않은 값 사용 시 보고                      | mc-manual §4.2 |
| invalid read / invalid write       | 할당 범위 밖 메모리 접근                             | mc-manual      |
| definitely lost                    | 여전히 메모리가 사용 가능하지만 포인터가 없는 경우   | mc-manual      |
| indirectly lost                    | 직접 접근 불가 구조체의 내부 포인터                  | mc-manual      |
| possibly lost                      | 포인터가 블록 시작이 아닌 내부를 가리키는 경우       | mc-manual      |
| still reachable                    | 종료 시 포인터가 남아있는 메모리 (누수 아닐 수 있음) | mc-manual      |
| system call with unaddressable arg | syscall 인수로 접근 불가 메모리 전달                 | mc-manual §4.2 |

## 3. 주요 Memcheck 옵션

### 검증된 사실 (2026-08-01)

| 옵션                      | 동작                                             | 출처      |
|---------------------------|--------------------------------------------------|-----------|
| `--leak-check=full`       | 누수 블록 상세 출력 (definitely/indirectly 포함) | mc-manual |
| `--track-origins=yes`     | 초기화되지 않은 값의 원본 추적 (느려짐)          | mc-manual |
| `--error-exitcode=<n>`    | 오류 발생 시 지정 종료 코드 반환                 | mc-manual |
| `--show-leak-kinds=all`   | 모든 누수 종류 출력                              | mc-manual |
| `--undef-value-errors=no` | 초기화 오류 무시 (성능 향상 목적)                | mc-manual |

## 4. 기타 주요 도구

### 검증된 사실 (2026-08-01)

| 도구       | 목적                                        | 출처            |
|------------|---------------------------------------------|-----------------|
| Callgrind  | 함수 호출 그래프 및 캐시 프로파일링         | valgrind manual |
| Cachegrind | 캐시 및 분기 예측 시뮬레이션                | valgrind manual |
| Helgrind   | POSIX 스레드 오류 검사 (데이터 경쟁 등)     | valgrind manual |
| DRD        | 멀티스레드 데이터 경쟁 검사 (Helgrind 대안) | valgrind manual |
| Massif     | 힙 메모리 사용량 프로파일링                 | valgrind manual |

## 5. deprecated / 주의사항

| 항목               | 상태                                               | 출처            |
|--------------------|----------------------------------------------------|-----------------|
| 실행 속도          | Memcheck 기준 10~30배 느린 것이 일반적             | valgrind manual |
| --tool=exp-sgcheck | 실험적 스택/전역 배열 검사 도구 (안정성 보장 없음) | valgrind manual |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
