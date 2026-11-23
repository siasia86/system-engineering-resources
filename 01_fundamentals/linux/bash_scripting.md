# Bash 스크립트
<!-- reference: _reference/bash_shell_official_notes.md -->

운영 작업을 자동화하는 Bash 스크립트의 기본 문법, 안전하게 쓰는 방법(따옴표, 엄격 모드, 정리 작업), 인자 처리, 시작 설정 파일, 정적 검사(ShellCheck)를 다룹니다. 이 문서만으로 첫 스크립트 작성 → 문법 → 실전 예제 → 검사·검증까지 따라 할 수 있게 썼습니다.

- 기준 판: GNU Bash 5.3, ShellCheck 0.11.0 (2026-11-23 확인)
- 예제 시험: 2026-11-23, Bash 5.2.21과 ShellCheck 0.9.0에서 3~7절 예제를 실행하고 ShellCheck 경고 0건을 확인

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 첫 스크립트](#2-첫-스크립트) / [3. 변수와 따옴표](#3-변수와-따옴표)                     |
| [4. 조건·반복·함수](#4-조건반복함수) / [5. 엄격 모드와 정리](#5-엄격-모드와-정리) / [6. 인자 처리](#6-인자-처리) |
| [7. 실전 예제](#7-실전-예제) / [8. 시작 설정 파일](#8-시작-설정-파일) / [9. 검증](#9-검증)                       |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                             |

---

## 1. 개요

| 언제 Bash를 쓰나                             | 언제 다른 언어를 고려하나                   |
|----------------------------------------------|---------------------------------------------|
| 명령 몇 개를 순서대로 실행, 파일·서비스 조작 | 복잡한 자료 구조, JSON·API 처리가 중심      |
| 서버에 바로 있는 도구로 끝내야 할 때         | 수백 줄이 넘어가고 시험 코드가 필요할 때    |
| 배포·백업·점검 같은 짧은 운영 작업           | 여러 OS에서 같게 동작해야 할 때 (Python 등) |

`#!/bin/sh`로 시작하는 스크립트는 POSIX sh로 실행되어(Debian·Ubuntu는 dash) 배열 같은 Bash 기능이 없습니다. Bash 기능을 쓰면 `#!/usr/bin/env bash`로 시작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 첫 스크립트

```bash
cat > hello.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "hello, ${1:-world}"
EOF
chmod +x hello.sh
./hello.sh ops          # hello, ops
bash -n hello.sh        # 실행하지 않고 문법만 검사
bash -x hello.sh        # 명령을 하나씩 출력하며 실행 (디버깅)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 변수와 따옴표

```bash
name="web 01"                 # = 앞뒤에 공백 없음
echo "quoted: $name"          # 변수는 항상 큰따옴표 안에서
today=$(date +%F)             # 명령 결과 넣기
arr=(alpha "beta gamma" delta)
echo "${#arr[@]} ${arr[1]}"   # 3 beta gamma
for x in "${arr[@]}"; do printf '[%s]\n' "$x"; done
declare -A port=([web]=80 [db]=5432)   # 연관 배열
echo "${port[db]}"            # 5432
```

| 표기             | 결과 (`f=/var/log/app/server.log`)  |
|------------------|-------------------------------------|
| `${f##*/}`       | `server.log` (파일 이름)            |
| `${f%/*}`        | `/var/log/app` (디렉터리)           |
| `${f%.log}`      | `/var/log/app/server` (확장자 제거) |
| `${VAR:-기본값}` | 없거나 비면 기본값                  |
| `${VAR:?메시지}` | 없거나 비면 메시지와 함께 종료      |

따옴표 없이 쓴 변수는 공백에서 나뉘고 `*`가 파일 이름으로 바뀝니다. `rm $file`은 이름에 공백이 있으면 엉뚱한 파일을 지울 수 있으므로 `rm -- "$file"`처럼 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 조건·반복·함수

```bash
if [[ -f /etc/os-release && "$USER" == root ]]; then echo "root on linux"; fi
if (( count > 10 )); then echo "many"; fi           # 산술 비교
[[ "$host" == web* ]] && echo "web server"           # 패턴 비교
[[ "$ver" =~ ^[0-9]+\.[0-9]+$ ]] && echo "x.y"       # 정규식

for f in /var/log/*.log; do echo "$f"; done          # ls 결과 대신 glob
while IFS= read -r line; do echo "> $line"; done < hosts.txt   # 줄 단위 읽기

case "$1" in
  start|stop) systemctl "$1" myapp ;;
  *) echo "unknown: $1" >&2; exit 2 ;;
esac

greet() {
  local who="$1"              # 함수 안 변수는 local
  echo "hi $who"
  return 0                    # 함수의 종료 코드
}
greet ops
```

| 파일 검사 | 뜻        | 문자열 검사 | 뜻        |
|-----------|-----------|-------------|-----------|
| `-f`      | 일반 파일 | `-z`        | 빈 문자열 |
| `-d`      | 디렉터리  | `-n`        | 비지 않음 |
| `-e`      | 존재      | `==` `!=`   | 같음·다름 |
| `-x`      | 실행 가능 | `=~`        | 정규식    |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 엄격 모드와 정리

```bash
set -euo pipefail
```

| 옵션          | 효과                                                        |
|---------------|-------------------------------------------------------------|
| `-e`          | 명령이 실패(0이 아닌 종료)하면 스크립트를 멈춤              |
| `-u`          | 설정하지 않은 변수를 쓰면 오류                              |
| `-o pipefail` | 파이프라인 중간 명령이 실패해도 파이프라인 전체를 실패로 봄 |

`set -e`는 `if`·`while`의 조건, `&&`·`||` 앞의 명령, `!`로 뒤집은 명령에서는 멈추지 않습니다. 실패해도 되는 명령은 `cmd || true`처럼 의도를 드러냅니다.

```bash
bash -c 'false | true; echo $?'                  # 0  (pipefail 없음)
bash -c 'set -o pipefail; false | true; echo $?' # 1
```

임시 파일은 `trap`으로 끝날 때 지웁니다.

```bash
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT      # 정상 종료·오류 종료 모두 실행
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 인자 처리

```bash
while getopts ":s:d:k:h" opt; do
  case "$opt" in
    s) src="$OPTARG" ;;
    d) dest="$OPTARG" ;;
    k) keep="$OPTARG" ;;
    h|*) usage ;;
  esac
done
shift $((OPTIND - 1))         # 옵션을 뺀 나머지 인자는 "$@"
```

| 변수   | 뜻                           |
|--------|------------------------------|
| `$0`   | 스크립트 이름                |
| `$1`…  | 위치 인자                    |
| `$#`   | 인자 개수                    |
| `"$@"` | 모든 인자 (각각 따옴표 유지) |
| `$?`   | 직전 명령의 종료 코드        |
| `$$`   | 현재 셸 PID                  |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 예제

디렉터리를 날짜 이름으로 압축 백업하고 오래된 백업을 지우는 스크립트입니다.

`backup.sh`

```bash
#!/usr/bin/env bash
# 디렉터리를 날짜 이름의 tar.gz로 백업하고 오래된 백업을 지웁니다.
set -euo pipefail

usage() {
  echo "usage: $0 -s SRC -d DEST [-k KEEP_DAYS]" >&2
  exit 2
}

keep=7
src="" dest=""
while getopts ":s:d:k:h" opt; do
  case "$opt" in
    s) src="$OPTARG" ;;
    d) dest="$OPTARG" ;;
    k) keep="$OPTARG" ;;
    h|*) usage ;;
  esac
done
[[ -n "$src" && -n "$dest" ]] || usage
[[ -d "$src" ]] || { echo "not a directory: $src" >&2; exit 1; }

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

mkdir -p "$dest"
name="$(basename "$src")_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$tmp" -C "$(dirname "$src")" "$(basename "$src")"
mv "$tmp" "$dest/$name"
echo "created: $dest/$name"

find "$dest" -name "$(basename "$src")_*.tar.gz" -mtime +"$keep" -print -delete
```

```bash
./backup.sh -s /etc/nginx -d /backup -k 14   # created: /backup/nginx_20261123_101500.tar.gz
./backup.sh -s /nope -d /backup; echo $?     # not a directory: /nope → 1
./backup.sh; echo $?                         # usage 출력 → 2
```

압축이 끝난 뒤에만 최종 이름으로 옮기므로(`mv`), 중간에 실패해도 반쯤 만든 백업 파일이 남지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 시작 설정 파일

| 셸 종류                           | 읽는 파일                                                                                |
|-----------------------------------|------------------------------------------------------------------------------------------|
| 로그인 셸 (SSH 접속, `bash -l`)   | `/etc/profile` 다음 `~/.bash_profile`·`~/.bash_login`·`~/.profile` 가운데 처음 찾은 하나 |
| 비로그인 대화형 셸 (터미널 새 창) | `~/.bashrc` (Debian 계열은 `/etc/bash.bashrc`도)                                         |
| 스크립트 (비대화형)               | `BASH_ENV`가 가리키는 파일만                                                             |

보통 `~/.bash_profile`(또는 `~/.profile`)에서 `~/.bashrc`를 불러 두 경우를 맞춥니다. 스크립트는 사용자 설정 파일에 기대지 않고 필요한 `PATH`·변수를 스크립트 안에서 정합니다. 특히 cron에서는 `PATH`가 짧아 명령을 찾지 못하는 일이 많습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

ShellCheck는 따옴표 누락, `ls` 결과 반복 같은 흔한 실수를 찾아 줍니다.

```bash
sudo apt-get install -y shellcheck     # RHEL 계열은 EPEL의 ShellCheck
shellcheck backup.sh                   # 경고가 없으면 출력 없음
shellcheck -f gcc bad.sh               # 파일:행:열: 등급: 설명 [SC번호]
# bad.sh:2:10: error: Iterating over ls output is fragile. Use globs. [SC2045]
# bad.sh:3:6: note: Double quote to prevent globbing and word splitting. [SC2086]
```

| 순서 | 확인 내용   | 명령                               | 기대 결과                                  |
|------|-------------|------------------------------------|--------------------------------------------|
| 1    | 문법        | `bash -n script.sh`                | 출력 없음                                  |
| 2    | 정적 검사   | `shellcheck script.sh`             | 출력 없음 (경고 0건)                       |
| 3    | 정상 실행   | `./script.sh <정상 인자>; echo $?` | `0`                                        |
| 4    | 잘못된 인자 | `./script.sh; echo $?`             | 사용법 출력, `0`이 아닌 값                 |
| 5    | 실패 처리   | 없는 경로 등을 주고 실행           | 오류 메시지, `0`이 아닌 값, 임시 파일 없음 |
| 6    | 흐름 확인   | `bash -x script.sh ...`            | 의도한 순서로 명령 실행                    |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                 | 원인                                            | 해결 방법                                      |
|--------------------------------------|-------------------------------------------------|------------------------------------------------|
| `syntax error near unexpected token` | `#!/bin/sh`로 Bash 문법 실행, 따옴표 짝 안 맞음 | `#!/usr/bin/env bash`, `bash -n`으로 위치 확인 |
| `$'\r': command not found`           | Windows 줄바꿈(CRLF)                            | `sed -i 's/\r$//' script.sh` 또는 `dos2unix`   |
| 공백 있는 파일 이름에서 오동작       | 변수에 따옴표 없음                              | `"$var"`, `"${arr[@]}"`                        |
| `unbound variable`                   | `set -u`에서 설정 안 된 변수                    | `${VAR:-}` 또는 기본값 지정                    |
| 실패했는데 스크립트가 계속 진행      | `set -e` 예외 위치(조건·`\|\|` 앞)·파이프 중간  | `set -o pipefail`, 종료 코드 직접 확인         |
| cron에서만 명령을 못 찾음            | cron의 `PATH`가 짧음, 설정 파일을 안 읽음       | 스크립트 안에서 `PATH` 지정, 절대 경로 사용    |
| `Permission denied`                  | 실행 권한 없음, `noexec` 마운트                 | `chmod +x`, 또는 `bash script.sh`              |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Bash 파일 리다이렉션](./bash_file_redirection.md) — 입출력 연결
- [Bash trap](./bash_trap_complete_guide.md) — 신호 처리와 정리 패턴
- [Bash 수학 연산](./bash_math.md) — 산술과 bc
- [셸 대화형 모드](./shell_interactive_mode.md) — 대화형·비대화형 차이와 profile.d
- [텍스트 처리](./text_processing.md) — grep·sed·awk와 함께 쓰기

---

## 참고 자료

- GNU: [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html) — ★★★☆☆
- Linux man-pages: [bash(1)](https://man7.org/linux/man-pages/man1/bash.1.html) — ★★★☆☆
- ShellCheck: [shellcheck.net](https://www.shellcheck.net/) · [koalaman/shellcheck](https://github.com/koalaman/shellcheck) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
