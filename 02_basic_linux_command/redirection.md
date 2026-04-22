# 표준 입출력과 리다이렉션 (Redirection)

## 목차

- [파일 디스크립터 (File Descriptor)](#파일-디스크립터-file-descriptor)
- [표준 입출력](#표준-입출력)
- [출력 리다이렉션](#출력-리다이렉션)
- [입력 리다이렉션](#입력-리다이렉션)
- [Here Document / Here String](#here-document--here-string)
- [파이프 (Pipe)](#파이프-pipe)
- [FD 조합과 순서](#fd-조합과-순서)
- [축약 문법 (bash 전용)](#축약-문법-bash-전용)
- [고급: FD 3 이상 사용](#고급-fd-3-이상-사용)
- [/dev/null, /dev/zero, /dev/urandom](#devnull-devzero-devurandom)
- [crontab 리다이렉션 패턴](#crontab-리다이렉션-패턴)
- [실전 패턴](#실전-패턴)

---

## 파일 디스크립터 (File Descriptor)

프로세스가 열어둔 I/O 채널의 번호. 커널이 프로세스별로 관리한다.

| FD  | 이름   | 용도      | 기본 대상 |
|-----|--------|-----------|-----------|
| 0   | stdin  | 표준 입력 | 키보드    |
| 1   | stdout | 표준 출력 | 터미널    |
| 2   | stderr | 에러 출력 | 터미널    |

```
┌──────────┐     FD 0 (stdin)  ← 키보드
│ 프로세스  | →   FD 1 (stdout) → 터미널
│          │ →   FD 2 (stderr) → 터미널
└──────────┘
```

- FD 3 이상은 프로세스가 파일/소켓을 열 때 자동 할당
- 확인: `ls -l /proc/$$/fd/`

---

## 표준 입출력

```bash
# stdout (FD 1) - 일반 출력
echo "hello"              # → 터미널

# stderr (FD 2) - 에러 출력
ls /nonexistent            # → 터미널 (에러 메시지)

# stdin (FD 0) - 입력
read -p "name: " name      # ← 키보드
```

stdout과 stderr는 둘 다 터미널에 출력되지만 별개의 스트림이다.

```bash
# 확인: stderr만 빨간색으로 보기
ls /nonexistent 2> >(while read l; do echo -e "\e[31m$l\e[0m"; done)
```

---

## 출력 리다이렉션

### 덮어쓰기 (`>`)

```bash
echo "hello" > file.txt       # stdout → file.txt (1> 와 동일)
ls /nonexistent 2> error.log  # stderr → error.log
```

### 추가 (`>>`)

```bash
echo "line1" >> file.txt      # 기존 내용 뒤에 추가
echo "line2" >> file.txt
```

### stdout과 stderr 분리

```bash
command > stdout.log 2> stderr.log
```

### noclobber (덮어쓰기 방지)

```bash
set -o noclobber
echo "test" > file.txt        # file.txt 이미 존재하면 에러
echo "test" >| file.txt       # noclobber 무시하고 강제 덮어쓰기
set +o noclobber              # 해제
```

---

## 입력 리다이렉션

### 파일에서 입력 (`<`)

```bash
wc -l < file.txt              # file.txt 내용을 stdin으로
sort < unsorted.txt > sorted.txt
```

### 파일 디스크립터 복제

```bash
# FD 0을 FD 3에서 읽기
exec 3< file.txt
read line <&3
exec 3<&-                     # FD 3 닫기
```

---

## Here Document / Here String

### Here Document (`<<`)

```bash
cat << EOF
이름: sjyun
날짜: $(date +%Y-%m-%d)
EOF

# 변수 치환 방지: 구분자를 따옴표로 감싸기
cat << 'EOF'
변수 $HOME 은 치환되지 않음
EOF

# 들여쓰기 탭 제거: <<-
cat <<- EOF
	탭으로 들여쓴 내용
	탭이 제거되어 출력됨
EOF
```

### Here String (`<<<`)

```bash
grep "pattern" <<< "search in this string"
read a b c <<< "1 2 3"
```

---

## 파이프 (Pipe)

앞 명령의 stdout을 뒤 명령의 stdin으로 연결한다.

```bash
# 기본
ls -la | grep ".log"

# 여러 개 연결
cat access.log | grep "ERROR" | sort | uniq -c | sort -rn

# stderr는 파이프로 전달되지 않음
ls /nonexistent | grep "No"    # grep에 아무것도 안 들어옴

# stderr도 파이프로 보내기
ls /nonexistent 2>&1 | grep "No"

# bash 전용: |&  (stdout + stderr 모두 파이프)
ls /nonexistent |& grep "No"
```

### PIPESTATUS

```bash
false | true | false
echo "${PIPESTATUS[@]}"        # 1 0 1 (각 명령의 종료 코드)

# set -o pipefail: 파이프 중 하나라도 실패하면 전체 실패
set -o pipefail
false | true
echo $?                        # 1
```

### 파이프와 서브셸

```bash
# 파이프 뒤 명령은 서브셸에서 실행 → 변수 변경이 부모에 반영 안 됨
count=0
echo -e "a\nb\nc" | while read line; do ((count++)); done
echo $count                    # 0 (서브셸에서 변경됨)

# 해결: process substitution
count=0
while read line; do ((count++)); done < <(echo -e "a\nb\nc")
echo $count                    # 3
```

---

## FD 조합과 순서

리다이렉션은 왼쪽에서 오른쪽으로 순서대로 처리된다.

```bash
# ✅ stdout→file, stderr→stdout(=file)
command > file 2>&1
# 결과: stdout, stderr 모두 file

# ❌ stderr→stdout(=터미널), stdout→file
command 2>&1 > file
# 결과: stdout만 file, stderr는 터미널
```

처리 순서 도식:

```
# command > file 2>&1
┌──────────┐
│ 초기 상태 |  FD 1 → 터미널    FD 2 → 터미널
└──────────┐
      |
  > file        FD 1 → file      FD 2 → 터미널
      |
  2>&1          FD 1 → file      FD 2 → file     ← FD 1이 가리키는 곳
      |
  결과: 둘 다 file
```

```
# command 2>&1 > file
┌──────────┐
│ 초기 상태 |  FD 1 → 터미널    FD 2 → 터미널
└──────────┐
      |
  2>&1          FD 1 → 터미널    FD 2 → 터미널   ← FD 1이 가리키는 곳(터미널)
      |
  > file        FD 1 → file      FD 2 → 터미널
      |
  결과: stdout만 file, stderr는 터미널
```

---

## 축약 문법 (bash 전용)

```bash
command &> file          # > file 2>&1 과 동일
command &>> file         # >> file 2>&1 과 동일 (append)
command |& next          # 2>&1 | next 와 동일
```

⚠️ POSIX sh에서는 사용 불가. 이식성이 필요하면 `> file 2>&1` 사용.

---

## 고급: FD 3 이상 사용

```bash
# FD 3을 파일에 연결
exec 3> custom.log
echo "custom message" >&3
echo "another line" >&3
exec 3>&-                      # FD 3 닫기

# FD 3으로 읽기
exec 3< input.txt
while read -u 3 line; do
    echo "$line"
done
exec 3<&-

# stdout 백업 후 복원
exec 3>&1                      # FD 3에 stdout 백업
exec 1> output.log             # stdout을 파일로
echo "이건 파일로"
exec 1>&3                      # stdout 복원
exec 3>&-
echo "이건 터미널로"
```

---

## /dev/null, /dev/zero, /dev/urandom

| 장치           | 용도                           |
|----------------|--------------------------------|
| `/dev/null`    | 블랙홀 (쓰면 버림, 읽으면 EOF) |
| `/dev/zero`    | 무한 null 바이트 출력          |
| `/dev/urandom` | 무한 랜덤 바이트 출력          |

```bash
# 출력 버리기
command > /dev/null 2>&1

# 파일 비우기 (0바이트)
> file.txt                     # 가장 간단
cat /dev/null > file.txt       # 동일

# 1GB 더미 파일 생성
dd if=/dev/zero of=dummy bs=1M count=1024

# 랜덤 문자열 생성
tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32
```

---

## crontab 리다이렉션 패턴

### 기본 형식

```
분 시 일 월 요일 명령
```

### 출력 처리 패턴

```bash
# 모든 출력 버리기 (가장 흔함)
0 3 * * * /usr/local/bin/backup.sh > /dev/null 2>&1

# 에러만 메일로 받기 (stdout만 버림)
0 3 * * * /usr/local/bin/backup.sh > /dev/null

# 로그 파일에 기록 (덮어쓰기)
0 3 * * * /usr/local/bin/backup.sh > /var/log/backup.log 2>&1

# 로그 파일에 추가 (append)
*/10 * * * * /usr/local/bin/monitor.sh >> /var/log/monitor.log 2>&1

# stdout/stderr 분리
0 4 * * * /usr/local/bin/deploy.sh >> /var/log/deploy.log 2>> /var/log/deploy_error.log

# 날짜별 로그
0 3 * * * /usr/local/bin/backup.sh >> /var/log/backup_$(date +\%Y\%m\%d).log 2>&1
```

⚠️ crontab에서 `%`는 개행으로 해석되므로 `\%`로 이스케이프 필요.

### 출력을 안 버리면?

cron은 명령의 stdout/stderr 출력이 있으면 `MAILTO`에 설정된 주소로 메일을 보낸다. 미설정 시 crontab 소유자에게 발송.

```bash
# 메일 수신 설정
MAILTO="admin@example.com"
0 3 * * * /usr/local/bin/backup.sh

# 메일 비활성화
MAILTO=""
0 3 * * * /usr/local/bin/backup.sh
```

---

## 실전 패턴

```bash
# 로그 분리 (stdout → 일반 로그, stderr → 에러 로그)
./deploy.sh > deploy.log 2> deploy_error.log

# 에러만 로그, 일반 출력은 터미널
tar czf backup.tar.gz /data 2> tar_error.log

# 명령 존재 여부 확인 (출력 불필요)
if command -v docker > /dev/null 2>&1; then
    echo "docker installed"
fi

# tee: stdout을 터미널 + 파일 동시 출력
command | tee output.log              # stdout만
command 2>&1 | tee output.log         # stdout + stderr

# tee -a: 추가 모드
command | tee -a output.log

# process substitution: 두 파일에 동시 출력
command | tee >(grep ERROR > errors.log) > all.log

# 파일 존재 확인 후 리다이렉트
[ -d /var/log/app ] && command >> /var/log/app/output.log 2>&1
```

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-15

© 2026 siasia86. Licensed under CC BY 4.0.
