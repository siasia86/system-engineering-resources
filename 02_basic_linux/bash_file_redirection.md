# Bash File Input/Output Redirections

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. File Descriptor 기본](#2-file-descriptor-기본) / [3. Output Redirection](#3-output-redirection) |
| [4. Input Redirection](#4-input-redirection) / [5. 조합 패턴](#5-조합-패턴) / [6. 실무 예시](#6-실무-예시) |

---

## 1. 개요

Bash에서 모든 프로세스는 File Descriptor(FD)를 통해 입출력을 처리합니다.
Redirection은 이 FD의 방향을 변경하여 파일, 파이프, 또는 다른 FD로 연결합니다.

---

## 2. File Descriptor 기본

| FD | 이름   | 풀 네임         | 기본 방향         | 용도      |
|----|--------|-----------------|-------------------|-----------|
| 0  | stdin  | Standard Input  | 키보드 → 프로세스 | 입력      |
| 1  | stdout | Standard Output | 프로세스 → 터미널 | 일반 출력 |
| 2  | stderr | Standard Error  | 프로세스 → 터미널 | 에러 출력 |

```
                ┌──────────────┐
  keyboard ───> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │
                │ 1 (stdout) ──┼───> terminal
                │ 2 (stderr) ──┼───> terminal
                └──────────────┘
```

---

## 3. Output Redirection

### `>` — stdout을 파일로 (덮어쓰기)

```bash
command > file.txt
```

```
                ┌──────────────┐
  keyboard ───> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │
                │ 1 (stdout) ──┼───> file.txt  (덮어쓰기)
                │ 2 (stderr) ──┼───> terminal
                └──────────────┘
```

### `>>` — stdout을 파일로 (추가)

```bash
command >> file.txt
```

```
                ┌──────────────┐
  keyboard ───> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │
                │ 1 (stdout) ──┼───> file.txt  (기존 내용 유지, 끝에 추가)
                │ 2 (stderr) ──┼───> terminal
                └──────────────┘

  file.txt 상태:
  before: [line1][line2]
  after:  [line1][line2][new output]
```

### `2>` — stderr을 파일로

```bash
command 2> error.log
```

```
                ┌──────────────┐
  keyboard ───> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │
                │ 1 (stdout) ──┼───> terminal
                │ 2 (stderr) ──┼───> error.log
                └──────────────┘
```

### `2>&1` — stderr을 stdout과 같은 곳으로

`&`는 **"다음 숫자를 파일명이 아닌 FD 번호로 해석하라"** 는 의미입니다.

```
2  >  &  1
│  │  │  │
│  │  │  └── FD 번호 1 (stdout)
│  │  └───── 다음 숫자는 파일명이 아닌 FD 번호
│  └──────── 리다이렉트 연산자
└─────────── 리다이렉트할 FD (stderr)
```

`&` 없으면 `1`은 FD가 아닌 파일명 `"1"`로 해석됩니다:

```bash
command 2> 1     # "1" 이라는 파일 생성 (FD 1이 아님)
command 2>&1     # FD 1(stdout)이 가리키는 곳으로 연결
```

```bash
command > output.log 2>&1
```

```
                ┌──────────────┐
  keyboard ───> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │
                │ 1 (stdout) ──┼───> output.log
                │ 2 (stderr) ──┼──┘
                └──────────────┘
                                    2>&1 = "FD2를 FD1이 가리키는 곳으로"
```

⚠️ 순서가 중요합니다:

```bash
# ✅ 올바른 순서: stdout을 파일로 → stderr을 stdout으로
command > file.log 2>&1

# ❌ 잘못된 순서: stderr을 stdout(터미널)으로 → stdout을 파일로
command 2>&1 > file.log    # stderr은 여전히 터미널로 출력
```

순서별 동작 다이어그램:

```
# command > file.log 2>&1 (올바른 순서)

  Step 1: > file.log       Step 2: 2>&1
  FD1 ───> file.log        FD2 ───> (FD1이 가리키는 곳) ───> file.log

  Result:
  FD1 ───> file.log
  FD2 ───> file.log


# command 2>&1 > file.log (잘못된 순서)

  Step 1: 2>&1             Step 2: > file.log
  FD2 ───> (FD1 = terminal)   FD1 ───> file.log

  Result:
  FD1 ───> file.log
  FD2 ───> terminal        ← stderr이 파일로 안 감
```

### `&>` — stdout + stderr 모두 파일로 (bash 전용 단축)

```bash
command &> output.log       # bash 4.0+
command > output.log 2>&1   # 동일, POSIX 호환
```

### `>/dev/null` — 출력 버리기

```bash
command > /dev/null 2>&1    # stdout + stderr 모두 버림
command &> /dev/null        # 동일 (bash 단축)
```

---

## 4. Input Redirection

### `<` — 파일을 stdin으로

```bash
command < input.txt
```

```
                ┌──────────────┐
  input.txt ──> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │
                │ 1 (stdout) ──┼───> terminal
                │ 2 (stderr) ──┼───> terminal
                └──────────────┘
```

### `<<` — Here Document

```bash
cat << EOF
line 1
line 2
EOF
```

### `<<<` — Here String

문자열을 직접 stdin으로 전달합니다. 파이프 없이 단일 명령어에 문자열 입력 시 사용합니다.

```bash
grep "pattern" <<< "search in this string"

# 단어 수 세기
wc -w <<< "hello world foo"       # → 3

# base64 인코딩
base64 <<< "hello"                 # → aGVsbG8K

# 변수 내용을 stdin으로
data="192.168.1.1 server01"
awk '{print $2}' <<< "${data}"    # → server01
```

---

## 5. 조합 패턴

### `exec` — 현재 쉘의 FD 변경

```bash
exec >> /var/log/script.log 2>&1
# 이후 모든 stdout/stderr이 로그 파일로
echo "이 메시지는 파일로"
```

```
  exec 실행 전:                    exec 실행 후:
  FD1 ───> terminal                FD1 ───> /var/log/script.log
  FD2 ───> terminal                FD2 ───> /var/log/script.log
```

### FD 복제 및 복원

FD 0/1/2는 시스템 예약 FD이고, **FD 3 이상은 사용자가 자유롭게 사용할 수 있는 FD**입니다.

```
FD 0 — stdin   (시스템 예약)
FD 1 — stdout  (시스템 예약)
FD 2 — stderr  (시스템 예약)
FD 3 — 사용자 정의 (비어있음, 필요할 때 열어서 사용)
FD 4, 5, ... — 사용자 정의
```

FD3을 쓰는 이유는 stdout(FD1)을 파일로 바꾸기 전에 원래 터미널을 백업해두기 위해서입니다.
FD3이 아니어도 되며, 3 이상 아무 번호나 사용 가능합니다. 관례적으로 3부터 씁니다.

**FD 최대 번호:**

```bash
ulimit -n          # 프로세스당 최대 FD 수 (기본 1024)
                   # → FD 0 ~ 1023 사용 가능
```

| 환경 | 기본값 |
|------|--------|
| 일반 Linux 프로세스 | 1024 (soft limit) |
| 서버 최적화 환경 | 65536 ~ 1048576 |
| 시스템 전체 | `/proc/sys/fs/file-max` (수백만) |

실무에서는 FD 3~9 정도만 사용합니다. 번호가 클수록 파일/소켓 등 다른 용도로 이미 사용 중인 번호와 충돌할 수 있습니다.

현재 열린 FD 확인:

```bash
ls -la /proc/$$/fd
# 0 → /dev/pts/0  (터미널)
# 1 → /dev/pts/0
# 2 → /dev/pts/0
# 3 → (없음, 기본 상태)
```

```bash
exec 3>&1              # FD3에 원래 stdout 백업
exec > /tmp/out.log    # stdout을 파일로 변경
echo "파일로 출력"
exec 1>&3              # stdout 복원
exec 3>&-              # FD3 닫기
echo "터미널로 출력"
```

```
  Step 1: exec 3>&1        FD3 ───> terminal (백업)
  Step 2: exec > file      FD1 ───> file
  Step 3: exec 1>&3        FD1 ───> terminal (복원)
  Step 4: exec 3>&-        FD3 닫힘  (3>&- : FD3을 닫음, 열린 FD는 명시적으로 닫아야 누수 방지)
```

### 파이프 + Redirection

파이프(`|`)는 왼쪽 명령어의 **stdout(FD1)만** 오른쪽 명령어의 stdin으로 연결합니다.
stderr(FD2)는 파이프를 통과하지 않고 터미널로 출력됩니다.

```
  ┌─────────┐              ┌─────────┐
  │ command │              │  grep   │
  │         │              │         │
  │ FD1 ────┼───pipe──────>│ FD0     │  stdout만 전달
  │ FD2 ────┼──────────────┼─────────┼──> terminal  (파이프 통과 안 함)
  └─────────┘              └─────────┘
```

stderr도 파이프로 전달하려면 `2>&1`로 FD2를 FD1에 합쳐야 합니다:

```bash
command 2>&1 | grep "error"    # stderr도 파이프로 전달
command |& grep "error"        # 동일 (bash 4.0+ 단축)
```

```
  ┌─────────┐              ┌─────────┐
  │ command │              │  grep   │
  │         │              │         │
  │ FD1 ────┼──┐           │         │
  │ FD2 ────┼──┴──pipe────>│ FD0     │  stdout + stderr 모두 전달
  └─────────┘  2>&1        └─────────┘
```

**파이프와 `$?` (exit code):**

파이프에서 `$?`는 **마지막 명령어**의 exit code입니다.

```bash
false | true
echo $?    # → 0 (true의 exit code, false 실패는 무시됨)

# 파이프 전체 exit code 확인
false | true
echo "${PIPESTATUS[@]}"    # → 1 0  (각 명령어 exit code)
```

**`pipefail` 옵션:**

```bash
set -o pipefail    # 파이프 중 하나라도 실패하면 전체 실패로 처리
false | true
echo $?            # → 1 (pipefail 없으면 0)
```

### `>(...)` — Process Substitution + tee (화면 + 파일 동시 출력)

`exec >> LOG 2>&1`은 파일에만 저장되어 화면 출력이 없습니다.
`>(tee -a LOG)`를 사용하면 파일 저장과 터미널 출력을 동시에 할 수 있습니다.

```bash
exec > >(tee -a "${LOG_FILE_01}") 2>&1
```

```
                ┌──────────────┐
  keyboard ───> │ 0 (stdin)    │
                │              │
                │   Process    │
                │              │     ┌─────────────┐
                │ 1 (stdout) ──┼────>│ tee -a log  ├──> LOG_FILE_01 (파일)
                │              │     │             ├──> terminal    (화면)
                │ 2 (stderr) ──┼──┘  └─────────────┘
                └──────────────┘
                         2>&1 = stderr도 tee로
```

| 패턴 | 파일 저장 | 터미널 출력 |
|------|-----------|------------|
| `exec >> "${LOG}" 2>&1` | ✅ | ❌ |
| `exec > >(tee -a "${LOG}") 2>&1` | ✅ | ✅ |

**`>(...)` 동작 원리:**

`tee`를 별도 프로세스로 실행하고 그 stdin을 받는 임시 FD(`/dev/fd/63` 등)를 생성합니다.
`>` 뒤에 파일 대신 프로세스를 연결하는 Process Substitution입니다.

**버퍼 문제와 `wait`:**

`tee`는 별도 프로세스로 실행되므로 스크립트 종료 시 버퍼가 flush되기 전에 종료될 수 있습니다.

```bash
# ❌ 마지막 출력이 잘릴 수 있음
exec > >(tee -a "${LOG_FILE_01}") 2>&1
echo "마지막 줄"
# 스크립트 종료 → tee가 flush 전에 종료될 수 있음

# ✅ wait로 tee 완료 보장
exec > >(tee -a "${LOG_FILE_01}") 2>&1
TEE_PID=$!          # 마지막 백그라운드 프로세스(tee) PID 저장
# ... 작업 ...
wait "${TEE_PID}"   # tee가 모든 출력을 flush할 때까지 대기
```

**`wait` 명령어:**

| 사용법 | 동작 |
|--------|------|
| `wait` | 현재 쉘의 모든 백그라운드 프로세스 완료 대기 |
| `wait PID` | 특정 PID 프로세스 완료 대기 |
| `wait $!` | 마지막 백그라운드 프로세스 대기 |


---

## 6. 실무 예시

### 로그 파일에 stdout/stderr 모두 기록

```bash
LOG_FILE="/var/log/deploy.log"
exec >> "${LOG_FILE}" 2>&1
echo "deploy start"       # 파일로
ls /nonexist 2>&1         # 에러도 파일로
```

### 에러만 별도 파일로 분리

```bash
command > stdout.log 2> stderr.log
```

### 화면 출력 + 파일 동시 기록 (tee)

```bash
command 2>&1 | tee output.log          # 화면 + 파일
command 2>&1 | tee -a output.log       # 화면 + 파일 (추가)
```

### /dev/null 활용

```bash
# 성공 여부만 확인 (출력 불필요)
if command > /dev/null 2>&1; then
    echo "success"
fi

# stderr만 버리기
command 2>/dev/null
```

### 스크립트 전체 로깅 패턴

```bash
#!/bin/bash
LOG="/var/log/$(basename "$0" .sh).log"
exec >> "${LOG}" 2>&1

echo "$(date) script start"
apt-get update -qq
echo "$(date) script end"
```

---

## 참고 자료

- Bash One-Liners Explained Part III: [catonmat.net](https://catonmat.net/bash-one-liners-explained-part-three) — ★★☆☆☆
- Bash Manual — Redirections: [gnu.org](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) — ★★★☆☆
- Advanced Bash-Scripting Guide: [tldp.org](https://tldp.org/LDP/abs/html/io-redirection.html) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-21

**마지막 업데이트**: 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
