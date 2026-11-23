---
name: text-processing-official-notes
description: GNU grep·sed·gawk·coreutils(cut·sort·uniq·tr·wc·head·tail) 텍스트 처리 도구의 공식 매뉴얼 기준 사실 정리.
tags:
  - linux
  - grep
  - sed
  - awk
  - coreutils
last_checked: 2026-11-23
sources:
  - https://www.gnu.org/software/grep/manual/grep.html
  - https://www.gnu.org/software/sed/manual/sed.html
  - https://www.gnu.org/software/gawk/manual/gawk.html
  - https://www.gnu.org/software/coreutils/manual/coreutils.html
  - https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html
  - https://ftp.gnu.org/gnu/
---

# 텍스트 처리 도구 공식 참조 노트

## 1. 판과 공식 소스

### 공식 소스

| 소스                 | URL                                                                 | 용도                         |
|----------------------|---------------------------------------------------------------------|------------------------------|
| GNU grep 매뉴얼      | https://www.gnu.org/software/grep/manual/grep.html                  | 옵션, 정규식 종류, 종료 코드 |
| GNU sed 매뉴얼       | https://www.gnu.org/software/sed/manual/sed.html                    | 명령, 주소, `-i`, `-E`       |
| GNU awk 매뉴얼       | https://www.gnu.org/software/gawk/manual/gawk.html                  | 필드, 패턴-동작, 내장 변수   |
| GNU coreutils 매뉴얼 | https://www.gnu.org/software/coreutils/manual/coreutils.html        | cut, sort, uniq, tr, wc 등   |
| POSIX awk            | https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html | 이식 가능한 awk 기능         |
| GNU 배포처           | https://ftp.gnu.org/gnu/                                            | 최신 판 확인                 |

### 검증된 사실 (2026-11-23)

| 항목                  | 값                    | 출처                      |
|-----------------------|-----------------------|---------------------------|
| GNU grep 최신 판      | 3.12 (2025-04-10)     | ftp.gnu.org/gnu/grep      |
| GNU sed 최신 판       | 4.10 (2026-04-21)     | ftp.gnu.org/gnu/sed       |
| GNU awk(gawk) 최신 판 | 5.4.2 (2026-11-16)    | ftp.gnu.org/gnu/gawk      |
| GNU coreutils 최신 판 | 9.12 (2026-09-14)     | ftp.gnu.org/gnu/coreutils |
| 판 확인               | 각 명령의 `--version` | 각 매뉴얼                 |

검증 방법: 1차로 설치된 GNU 도구의 `--help` 원문, 2차로 설치된 GNU man 페이지와 대조했습니다(2026-11-23). 같은 날 gawk·coreutils 매뉴얼 페이지는 응답이 없어 주소 응답은 다음 확인 때 다시 봅니다. grep·sed 매뉴얼과 POSIX awk 페이지는 응답 200을 확인했습니다.

배포판 패키지는 위 최신 판보다 낮을 수 있습니다. Ubuntu 24.04 계열에서 확인한 판은 grep 3.11, sed 4.9, gawk 5.2.1, coreutils 9.4입니다.

## 2. grep

| 항목            | 내용                                                                                                                |
|-----------------|---------------------------------------------------------------------------------------------------------------------|
| 정규식 종류     | 기본 BRE, `-E` ERE, `-F` 고정 문자열, `-P` Perl 호환(PCRE, GNU 확장)                                                |
| 자주 쓰는 옵션  | `-i` 대소문자 무시, `-v` 반전, `-c` 개수, `-n` 행 번호, `-o` 일치 부분만, `-w` 단어, `-x` 줄 전체, `-l` 파일 이름만 |
| 재귀 검색       | `-r`(심볼릭 링크는 명령줄에 준 것만 따라감), `-R`(모두 따라감), `--include`·`--exclude`                             |
| 종료 코드       | 일치하는 줄이 있으면 0, 없으면 1, 오류면 2. 단 `-q`를 주면 오류가 있어도 일치가 있을 때 0                           |
| `egrep`·`fgrep` | 옛 이름. `grep -E`·`grep -F`를 씀                                                                                   |

## 3. sed

| 항목           | 내용                                                                                               |
|----------------|----------------------------------------------------------------------------------------------------|
| 기본 동작      | 입력을 한 줄씩 읽어 명령을 적용하고 결과를 표준 출력으로 보냄                                      |
| `-n`           | 자동 출력을 끔. `p` 명령으로 고른 줄만 출력                                                        |
| `-E`           | ERE 사용 (`-r`과 같음, GNU)                                                                        |
| `-i[SUFFIX]`   | 파일을 직접 고침. SUFFIX를 주면 그 이름으로 원본 백업 (GNU 확장)                                   |
| 주소           | 행 번호(`3`), 마지막 행(`$`), 정규식(`/re/`), 범위(`a,b`), 반전(`!`)                               |
| 자주 쓰는 명령 | `s/re/대치/플래그`(`g` 전체, `I` 대소문자 무시), `d` 삭제, `p` 출력, `a`·`i`·`c` 줄 추가·삽입·교체 |
| 이식성         | BSD·macOS sed의 `-i`는 백업 접미사 인자가 필수라 `sed -i '' ...` 형태가 다름                       |

## 4. awk (gawk·POSIX)

| 항목          | 내용                                                                            |
|---------------|---------------------------------------------------------------------------------|
| 프로그램 구조 | `패턴 { 동작 }`의 나열. 패턴이 없으면 모든 줄, 동작이 없으면 줄 출력            |
| 특수 패턴     | `BEGIN`(입력 전), `END`(입력 후)                                                |
| 필드          | `$1`~`$NF`, `$0`은 줄 전체. 기본 구분은 공백 연속                               |
| 내장 변수     | `NR` 전체 줄 번호, `NF` 필드 수, `FS`·`OFS` 입출력 구분자, `FNR` 파일별 줄 번호 |
| 옵션          | `-F 구분자`, `-v 변수=값`                                                       |
| 출력          | `print`, `printf "형식", 값...`                                                 |
| 연관 배열     | `count[$1]++` 후 `for (k in count)`로 집계                                      |
| gawk 확장     | `-i inplace`, `gensub()`, `asort()` 등은 POSIX에 없음                           |

## 5. coreutils 텍스트 명령

| 명령          | 핵심                                                                              |
|---------------|-----------------------------------------------------------------------------------|
| `cut`         | `-d 구분자 -f 필드목록`, 바이트·문자 단위는 `-b`·`-c`                             |
| `sort`        | `-k` 키, `-t` 구분자, `-n` 숫자, `-h` 사람 단위(K·M·G), `-r` 역순, `-u` 중복 제거 |
| `uniq`        | 이웃한 같은 줄만 합침. 전체 중복을 보려면 먼저 `sort`. `-c` 개수, `-d` 중복만     |
| `tr`          | 문자 단위 변환·삭제. `-d` 삭제, `-s` 연속 압축                                    |
| `wc`          | `-l` 줄, `-w` 단어, `-c` 바이트                                                   |
| `head`·`tail` | `-n N`, `tail -n +N`은 N번째 줄부터, `tail -f`는 추가되는 내용 따라감             |

`sort`·`uniq`의 비교 순서는 로캘(`LC_COLLATE`)에 따라 달라집니다. 바이트 순서로 고정하려면 `LC_ALL=C`를 붙입니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
