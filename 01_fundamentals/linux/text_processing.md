# 텍스트 처리 (grep·sed·awk·sort·uniq·cut·tr)
<!-- reference: _reference/text_processing_official_notes.md -->

로그·설정 파일·명령 출력에서 원하는 줄을 찾고, 바꾸고, 필드를 뽑아 집계하는 Linux 기본 도구 사용법입니다. 이 문서만으로 설치 확인 → 도구별 기본 사용 → 파이프 조합 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: GNU grep 3.12, sed 4.10, gawk 5.4.2, coreutils 9.12(최신 판, 2026-11-23 확인)
- 예제 시험: 2026-11-23, GNU grep 3.11·sed 4.9·gawk 5.2.1·coreutils 9.4에서 3~8절 예제를 실행해 결과를 확인

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 확인](#2-설치-확인) / [3. 예제 파일](#3-예제-파일)                     |
| [4. grep](#4-grep) / [5. sed](#5-sed) / [6. awk](#6-awk)                                             |
| [7. cut·sort·uniq·tr·wc](#7-cutsortuniqtrwc) / [8. 파이프 조합](#8-파이프-조합) / [9. 검증](#9-검증) |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                 |

---

## 1. 개요

| 도구   | 하는 일                    | 고르는 기준                             |
|--------|----------------------------|-----------------------------------------|
| `grep` | 패턴에 맞는 줄 찾기        | 줄을 고르기만 할 때                     |
| `sed`  | 줄 단위 치환·삭제·추출     | 정해진 규칙으로 고칠 때, 파일 직접 수정 |
| `awk`  | 필드 단위 처리, 조건, 집계 | 열을 뽑거나 합계·개수를 낼 때           |
| `cut`  | 구분자 기준 열 자르기      | 구분자가 일정한 단순한 열 추출          |
| `sort` | 정렬                       | 숫자·사람 단위·특정 열 기준 정렬        |
| `uniq` | 이웃한 중복 줄 합치기·세기 | `sort` 다음에 써서 빈도 집계            |
| `tr`   | 문자 단위 변환·삭제        | 대소문자 변환, 공백 압축                |
| `wc`   | 줄·단어·바이트 수          | 개수 확인                               |

모두 표준 입력을 받아 표준 출력으로 내보내므로 `|`로 이어 붙여 씁니다. JSON은 이 도구들로 다루기 어렵기 때문에 `jq`를 씁니다(8-4).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치 확인

대부분의 배포판에 기본으로 들어 있습니다.

```bash
grep --version | head -1     # grep (GNU grep) 3.x
sed --version | head -1      # sed (GNU sed) 4.x
awk --version | head -1      # GNU Awk 5.x  (mawk·busybox awk는 출력이 다름)
sort --version | head -1     # sort (GNU coreutils) 9.x
```

없거나 GNU 판이 아니면 설치합니다.

```bash
sudo apt-get install -y grep sed gawk coreutils     # Ubuntu / Debian
sudo dnf install -y grep sed gawk coreutils         # RHEL 계열
sudo apt-get install -y jq                          # JSON 처리 (8-4)
```

macOS와 BSD 계열의 기본 도구는 GNU 판이 아니라 옵션이 다를 수 있습니다(10절).

[⬆ 목차로 돌아가기](#목차)

---

## 3. 예제 파일

아래 세 파일로 4~8절을 따라 합니다.

```bash
mkdir -p ~/textlab && cd ~/textlab

cat > access.log <<'EOF'
192.0.2.10 - - [23/Nov/2026:10:00:01 +0900] "GET /index.html HTTP/1.1" 200 512
192.0.2.11 - - [23/Nov/2026:10:00:02 +0900] "GET /api/users HTTP/1.1" 500 120
192.0.2.10 - - [23/Nov/2026:10:00:03 +0900] "POST /api/login HTTP/1.1" 200 64
198.51.100.7 - - [23/Nov/2026:10:00:04 +0900] "GET /admin HTTP/1.1" 403 32
192.0.2.11 - - [23/Nov/2026:10:00:05 +0900] "GET /api/users HTTP/1.1" 500 118
EOF

printf 'name,role,port\nweb01,web,80\ndb01,db,5432\nweb02,web,8080\n' > hosts.csv
printf 'host=web01\n#host=old\nport=80\n' > app.conf
```

`access.log`의 필드는 공백 기준으로 `$1` 클라이언트 IP, `$6`~`$8` 요청, `$9` 상태 코드, `$10` 응답 크기입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. grep

```bash
grep ' 500 ' access.log                 # 500 응답 줄
grep -c ' 500 ' access.log              # 개수만: 2
grep -v -E '^\s*(#|$)' app.conf         # 주석·빈 줄을 뺀 실제 설정
grep -E -o '"(GET|POST) [^ ]+' access.log   # 일치한 부분만
grep -rn 'listen' /etc/nginx/ --include='*.conf'   # 디렉터리 재귀, 행 번호
```

| 옵션        | 뜻                                        |
|-------------|-------------------------------------------|
| `-E`        | 확장 정규식 (`\|`, `+`, `?`, `()`)        |
| `-F`        | 정규식이 아닌 고정 문자열 (`.` 등 그대로) |
| `-i`        | 대소문자 무시                             |
| `-v`        | 맞지 않는 줄                              |
| `-c` / `-l` | 개수 / 파일 이름만                        |
| `-n`        | 행 번호                                   |
| `-o`        | 일치한 부분만                             |
| `-w` / `-x` | 단어 단위 / 줄 전체 일치                  |
| `-r`        | 디렉터리 재귀 (`--include`로 파일 거르기) |
| `-q`        | 출력 없이 종료 코드만                     |

종료 코드는 일치하면 0, 없으면 1, 오류면 2입니다. 스크립트에서는 이것으로 분기합니다.

```bash
if grep -q '^port=' app.conf; then echo "port 설정 있음"; fi
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. sed

```bash
sed -n '/^#/!p' app.conf                          # 주석이 아닌 줄만 출력
sed 's/web01/web03/' app.conf                     # 줄마다 첫 번째만 치환 (출력만, 파일은 그대로)
sed -n '2,4p' access.log                          # 2~4행만
sed '/^$/d' file.txt                              # 빈 줄 삭제
sed -E 's/^([0-9.]+) .*"([A-Z]+) ([^ ]+).* ([0-9]{3}) [0-9]+$/\1 \2 \3 \4/' access.log
# 192.0.2.10 GET /index.html 200  처럼 필요한 필드만 남김
```

파일을 직접 고칠 때는 백업 접미사를 붙입니다.

```bash
sed -i.bak 's/^port=.*/port=8080/' app.conf       # app.conf 수정, 원본은 app.conf.bak
diff app.conf.bak app.conf                        # 바뀐 줄 확인
```

| 요소            | 뜻                                                      |
|-----------------|---------------------------------------------------------|
| `-n` + `p`      | 고른 줄만 출력                                          |
| `-E`            | 확장 정규식 (`\1`로 묶음 참조)                          |
| `s/찾기/바꿈/g` | 치환. `g`는 줄 안 전체, 없으면 첫 번째만                |
| 주소            | `3`, `$`, `/정규식/`, `2,4`, `/a/,/b/`, 뒤에 `!`는 반전 |
| `d`             | 줄 삭제                                                 |
| `-i[접미사]`    | 파일 직접 수정 (GNU). 접미사를 주면 원본 백업           |

[⬆ 목차로 돌아가기](#목차)

---

## 6. awk

```bash
awk '{print $1}' access.log                              # 첫 필드(IP)
awk '$9 >= 500 {n++} END {print n+0}' access.log         # 5xx 개수: 2
awk -F, 'NR>1 && $2=="web" {print $1":"$3}' hosts.csv    # CSV에서 조건 추출
awk '{bytes+=$NF} END {printf "%d requests, %d bytes\n", NR, bytes}' access.log
# 5 requests, 846 bytes
awk '{c[$9]++} END {for (s in c) print s, c[s]}' access.log   # 상태 코드별 개수
```

| 요소             | 뜻                                      |
|------------------|-----------------------------------------|
| `패턴 { 동작 }`  | 패턴에 맞는 줄에만 동작 실행            |
| `BEGIN` / `END`  | 입력 전 / 입력을 다 읽은 뒤 한 번       |
| `$1`…`$NF`, `$0` | 필드, 마지막 필드, 줄 전체              |
| `NR` / `NF`      | 지금까지 읽은 줄 수 / 현재 줄의 필드 수 |
| `-F 구분자`      | 필드 구분자 (기본은 공백 연속)          |
| `-v 변수=값`     | 셸 값을 awk 변수로 넘김                 |
| `c[키]++`        | 연관 배열로 키별 집계                   |

셸 변수는 따옴표 안에 직접 넣지 말고 `-v`로 넘깁니다.

```bash
code=500
awk -v c="$code" '$9 == c' access.log
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. cut·sort·uniq·tr·wc

```bash
cut -d, -f1,3 hosts.csv | tail -n +2        # 1·3열, 머리글 제외
sort -t, -k3 -n hosts.csv                   # 3열 숫자 기준 정렬
printf '10\n9\n100\n' | sort                # 10 100 9  (문자열 정렬)
printf '10\n9\n100\n' | sort -n             # 9 10 100  (숫자 정렬)
printf '10K\n2M\n500\n' | sort -h           # 500 10K 2M (사람 단위)
echo 'Hello World' | tr 'a-z' 'A-Z'         # HELLO WORLD
echo 'a  b   c' | tr -s ' '                 # a b c
wc -l access.log                            # 5 access.log
```

`uniq`는 이웃한 같은 줄만 합칩니다. 전체에서 중복을 세려면 먼저 정렬합니다.

```bash
printf 'b\na\nb\n' | uniq | wc -l           # 3  (떨어진 b는 합치지 않음)
printf 'b\na\nb\n' | sort | uniq | wc -l    # 2
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 파이프 조합

### 8-1. IP별 요청 수 (많은 순)

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn
#       2 192.0.2.11
#       2 192.0.2.10
#       1 198.51.100.7
```

### 8-2. 요청 경로별 빈도

```bash
grep -E -o '"(GET|POST) [^ ]+' access.log | sort | uniq -c | sort -rn
```

### 8-3. 실제 설정만 보기

```bash
grep -v -E '^\s*(#|$)' /etc/ssh/sshd_config
```

### 8-4. JSON은 jq

```bash
printf '{"items":[{"n":"a","v":1},{"n":"b","v":2}]}' | jq -r '.items[] | "\(.n)=\(.v)"'
# a=1
# b=2
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

3절 예제 파일 기준의 기대 결과입니다. 명령을 바꾼 뒤에도 같은 결과가 나오는지로 확인합니다.

| 순서 | 확인 내용      | 명령                                                         | 기대 결과                               |
|------|----------------|--------------------------------------------------------------|-----------------------------------------|
| 1    | GNU 판         | `grep --version`, `sed --version`, `awk --version`           | GNU 판 번호                             |
| 2    | 줄 찾기        | `grep -c ' 500 ' access.log`                                 | `2`                                     |
| 3    | 종료 코드      | `grep -q nomatch app.conf; echo $?`                          | `1`                                     |
| 4    | 필드 집계      | `awk '$9 >= 500 {n++} END {print n+0}' access.log`           | `2`                                     |
| 5    | 빈도 집계      | `awk '{print $1}' access.log \| sort \| uniq -c \| sort -rn` | 192.0.2.10·.11이 각 2                   |
| 6    | 파일 직접 수정 | `sed -i.bak 's/^port=.*/port=8080/' app.conf` 후 `diff`      | `port=80` → `port=8080`, 백업 파일 있음 |
| 7    | 정렬 기준      | `printf '10\n9\n100\n' \| sort -n`                           | `9 10 100` 순서                         |
| 8    | 중복 처리      | `printf 'b\na\nb\n' \| sort \| uniq \| wc -l`                | `2`                                     |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                       | 원인                                      | 해결 방법                                       |
|--------------------------------------------|-------------------------------------------|-------------------------------------------------|
| `grep 'a\|b'`가 아무것도 찾지 못함         | 기본 정규식(BRE)에서 `\|`는 일반 문자     | `grep -E 'a\|b'`                                |
| `.`이 들어간 IP·버전 검색 결과가 너무 많음 | `.`은 아무 문자 하나                      | `grep -F '10.0.0.1'` 또는 `\.`                  |
| macOS에서 `sed -i 's/a/b/' f`가 오류       | BSD sed는 `-i` 뒤 백업 접미사 인자가 필요 | `sed -i '' 's/a/b/' f`, 또는 GNU sed 설치       |
| `uniq -c` 결과에 같은 값이 여러 번 나옴    | 정렬하지 않아 같은 줄이 떨어져 있음       | `sort \| uniq -c`                               |
| 숫자 정렬 결과가 `10, 100, 9` 순서         | 문자열 정렬                               | `sort -n` 또는 `sort -h`                        |
| 정렬·비교 결과가 서버마다 다름             | 로캘(`LC_COLLATE`) 차이                   | `LC_ALL=C sort`로 바이트 순서 고정              |
| awk 필드가 하나씩 밀림                     | 값 안에 공백이 있음, 구분자가 다름        | `-F` 지정, CSV에 따옴표가 있으면 전용 파서 사용 |
| 셸 변수가 awk 안에서 비어 있음             | 작은따옴표 안에서는 셸 변수가 바뀌지 않음 | `awk -v 변수="$값"`                             |
| `sed -i`로 줄바꿈이 CRLF인 파일이 깨짐     | Windows 줄바꿈(`\r`)                      | `sed -i 's/\r$//' f` 또는 `dos2unix`            |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Bash 파일 리다이렉션](./bash_file_redirection.md) — `>`, `>>`, `2>&1`, 파이프
- [journald와 logrotate](./journald_logrotate_guide.md) — 로그 파일과 `journalctl` 출력
- [Vim](./vim.md) — 편집기 안에서의 치환
- [YAML 문법](../../02_infrastructure/iac/yaml_syntax.md) — 설정 파일 형식

---

## 참고 자료

- GNU: [GNU grep manual](https://www.gnu.org/software/grep/manual/grep.html) — ★★★☆☆
- GNU: [GNU sed manual](https://www.gnu.org/software/sed/manual/sed.html) — ★★★☆☆
- GNU: [GNU Awk User's Guide](https://www.gnu.org/software/gawk/manual/gawk.html) — ★★★☆☆
- GNU: [GNU Coreutils manual](https://www.gnu.org/software/coreutils/manual/coreutils.html) — ★★★☆☆
- The Open Group: [POSIX awk](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html) — ★★★☆☆
- jq: [jq Manual](https://jqlang.org/manual/) — ★★★☆☆

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
