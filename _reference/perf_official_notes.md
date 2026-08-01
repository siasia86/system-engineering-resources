---
name: perf-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man1/perf.1.html
  - https://perf.wiki.kernel.org/index.php/Main_Page
---

# perf 공식 참조 노트

## 1. perf 개요

### 공식 소스

| 소스        | URL                                               | 용도                      |
|-------------|---------------------------------------------------|---------------------------|
| perf.1      | https://man7.org/linux/man-pages/man1/perf.1.html | 서브커맨드, 옵션          |
| kernel wiki | https://perf.wiki.kernel.org/index.php/Main_Page  | 튜토리얼, PMU 이벤트 개요 |

### 검증된 사실 (2026-08-01)

| 항목            | 값                                              | 출처   |
|-----------------|-------------------------------------------------|--------|
| 버전 확인 방법  | `perf --version` 또는 `perf -v`                 | perf.1 |
| 커널 연계       | perf 버전은 커널 버전과 연동 (커널 소스에 포함) | perf.1 |
| 기본 사용법     | `perf [OPTIONS] COMMAND [ARGS]`                 | perf.1 |
| 서브커맨드 목록 | `perf --list-cmds`로 출력 가능                  | perf.1 |
| 라이브러리 상태 | `perf -vv`로 컴파일된 라이브러리 지원 여부 출력 | perf.1 |

## 2. 주요 서브커맨드 (perf.1 man page 기반)

### 공식 소스

| 소스   | URL                                               | 용도            |
|--------|---------------------------------------------------|-----------------|
| perf.1 | https://man7.org/linux/man-pages/man1/perf.1.html | 서브커맨드 목록 |

### 검증된 사실 (2026-08-01)

| 서브커맨드      | 동작                                    | 출처   |
|-----------------|-----------------------------------------|--------|
| `perf stat`     | 명령어 또는 프로세스의 성능 이벤트 집계 | perf.1 |
| `perf record`   | 성능 데이터를 `perf.data` 파일로 기록   | perf.1 |
| `perf report`   | `perf.data` 파일 분석 및 출력           | perf.1 |
| `perf top`      | 실시간 커널/사용자 함수 핫스팟 출력     | perf.1 |
| `perf list`     | 사용 가능한 이벤트 목록 출력            | perf.1 |
| `perf annotate` | 심볼에 대한 어셈블리 주석 출력          | perf.1 |
| `perf diff`     | 두 `perf.data` 파일 비교                | perf.1 |
| `perf script`   | `perf.data`를 텍스트 형식으로 출력      | perf.1 |
| `perf trace`    | strace 유사 syscall 추적 (perf 기반)    | perf.1 |
| `perf probe`    | 동적 추적 포인트 추가                   | perf.1 |

## 3. perf 전역 옵션 (perf.1 man page 기반)

### 검증된 사실 (2026-08-01)

| 옵션               | 동작                               | 출처   |
|--------------------|------------------------------------|--------|
| `-v`, `--version`  | perf 버전 출력                     | perf.1 |
| `-vv`              | 컴파일된 라이브러리 상태 출력      | perf.1 |
| `-h`, `--help`     | 도움말 출력                        | perf.1 |
| `-p`, `--paginate` | 페이저 설정                        | perf.1 |
| `--no-pager`       | 페이저 사용 안 함                  | perf.1 |
| `--buildid-dir`    | buildid 캐시 디렉토리 설정         | perf.1 |
| `--exec-path`      | exec 경로 출력 또는 설정           | perf.1 |
| `--list-cmds`      | 자주 사용되는 서브커맨드 목록 출력 | perf.1 |
| `--list-opts`      | 사용 가능한 옵션 목록 출력         | perf.1 |
| `--debugfs-dir`    | debugfs 디렉토리 설정              | perf.1 |

## 4. deprecated / 주의사항

| 항목               | 상태                                                     | 출처   |
|--------------------|----------------------------------------------------------|--------|
| `--debugfs-dir`    | sysfs 기반 tracing으로 이전 권장 (debugfs 마운트 불필요) | perf.1 |
| `perf.data` 호환성 | 커널 버전이 다르면 `perf.data` 파싱 실패 가능            | perf.1 |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.
