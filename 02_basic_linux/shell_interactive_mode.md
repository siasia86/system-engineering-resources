# Shell Interactive / Non-interactive 모드

## 목차

| 단계   | 섹션                                                                                                                           |
|--------|--------------------------------------------------------------------------------------------------------------------------------|
| 기본   | [1. $- 변수](#1---변수) / [2. Interactive vs Non-interactive](#2-interactive-vs-non-interactive)                                |
| 실전   | [3. 동작 차이](#3-동작-차이) / [4. /etc/profile.d 로딩 원리](#4-etcprofiled-로딩-원리) / [5. 실무 패턴](#5-실무-패턴)         |
| 참고   | [6. Tips](#6-tips)                                                                                                             |

---

## 1. $- 변수

현재 쉘에 활성화된 옵션 플래그 문자열입니다.

```bash
echo $-
# 터미널(interactive): himBH
# 스크립트(non-interactive): hB
```

### 주요 플래그

| 플래그 | 의미                          |
|--------|-------------------------------|
| `i`    | interactive shell             |
| `h`    | hashall (명령어 경로 캐싱)    |
| `m`    | monitor (job control)         |
| `B`    | brace expansion 활성화        |
| `H`    | history expansion 활성화      |
| `e`    | 오류 시 즉시 종료 (`set -e`)  |
| `x`    | 명령어 trace 출력 (`set -x`)  |

### interactive 여부 확인

```bash
# 방법 1: $- 에 i 포함 여부
if [[ $- == *i* ]]; then
    echo "interactive"
else
    echo "non-interactive"
fi

# 방법 2: $PS1 존재 여부 (interactive면 프롬프트 변수 존재)
if [ -n "$PS1" ]; then
    echo "interactive"
fi

# 방법 3: tty 연결 여부
if tty -s; then
    echo "interactive"
fi
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Interactive vs Non-interactive

| 구분                  | Interactive                         | Non-interactive                     |
|-----------------------|-------------------------------------|-------------------------------------|
| 정의                  | 사용자가 직접 입력하는 쉘           | 자동으로 실행되는 쉘                |
| 예시                  | SSH 접속, 터미널                    | 쉘 스크립트, cron, `bash script.sh` |
| 프롬프트              | `$`, `#` 표시                       | 없음                                |
| `~/.bashrc` 로드      | ✅                                   | ❌                                   |
| `/etc/profile` 로드   | ✅ (login shell)                     | ❌                                   |
| job control           | ✅ (`Ctrl+Z`, `fg`, `bg`)           | ❌                                   |
| alias 사용            | ✅                                   | ❌ (별도 source 필요)               |
| `$-` 의 `i` 플래그   | 포함                                | 미포함                              |

### 쉘 종류 조합

```
login + interactive     : SSH login, su - user
login + non-interactive : ssh user@host 'command'
non-login + interactive : run bash in terminal
non-login + non-interactive : bash script.sh, cron
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 동작 차이

### alias

```bash
# ~/.bashrc
alias ll='ls -la'

# interactive (SSH 접속) → 동작
ll /var/log   # OK

# non-interactive (cron, script) → 실패
ll /var/log   # command not found
```

### 환경변수

```bash
# ~/.bashrc 에 설정한 환경변수
export MY_VAR="value"

# interactive → 사용 가능
echo $MY_VAR   # value

# cron → ~/.bashrc 로드 안 됨
echo $MY_VAR   # (빈 값)
```

### PATH

```bash
# 터미널
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin

# cron 기본 PATH (매우 제한적)
# /usr/bin:/bin
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. /etc/profile.d 로딩 원리

`/etc/profile` 내부에서 `profile.d/*.sh` 를 순회하며 source 합니다.

```bash
# /etc/profile 발췌
for i in /etc/profile.d/*.sh /etc/profile.d/sh.local; do
    if [ -r "$i" ]; then
        if [ "${-#*i}" != "$-" ]; then
            . "$i"             # interactive: 출력 그대로
        else
            . "$i" >/dev/null  # non-interactive: 출력 숨김
        fi
    fi
done
```

### `${-#*i}` 분석

```bash
# $- = "himBH" (interactive, i 포함)
${-#*i}  →  "mBH"   ≠  "himBH"  →  interactive

# $- = "hBH" (non-interactive, i 없음)
${-#*i}  →  "hBH"   =  "hBH"    →  non-interactive
```

`${변수#패턴}` — 변수 앞에서 패턴과 일치하는 부분 제거 (최소 매칭).
`*i` — `i` 앞의 모든 문자. `i` 가 없으면 제거 대상 없음 → 원본과 동일.

### PATH 영구 등록 방법

```bash
# /etc/profile.d/ 에 파일 추가 (권장)
echo 'export PATH=$PATH:/usr/local/bin' | sudo tee /etc/profile.d/local_bin.sh
chmod +x /etc/profile.d/local_bin.sh

# 현재 세션 즉시 적용
source /etc/profile.d/local_bin.sh
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실무 패턴

### cron에서 alias/환경변수 사용

```bash
#!/bin/bash
# cron 스크립트 상단에 명시적으로 source
source /etc/profile
source ~/.bashrc 2>/dev/null || true

# 또는 필요한 것만
export PATH=$PATH:/usr/local/bin
```

### cron PATH 직접 지정

```bash
# crontab -e 상단에 PATH 선언
PATH=/usr/local/bin:/usr/bin:/bin
0 2 * * * /opt/scripts/backup.sh
```

### su - 로 login shell 환경 로드

`su -` (또는 `su -l`) 는 login shell 을 시작하므로 `/etc/profile`, `~/.bash_profile`, `~/.bashrc` 가 모두 로드됩니다.

```bash
# crontab -e
# su - root 로 실행하면 root 의 login shell 환경 전체 로드
0 2 * * * su - root -c '/opt/scripts/backup.sh'

# 특정 사용자로 실행
0 2 * * * su - deploy -c '/opt/scripts/deploy.sh'
```

주의사항:
- root crontab(`sudo crontab -e`)에서는 `su -` 없이도 root 권한으로 실행됨
- `su -` 는 PAM 인증을 거치므로 환경에 따라 추가 설정 필요할 수 있음
- 보안상 불필요한 `su -` 사용은 지양

### non-interactive에서 alias 강제 로드

```bash
# bash -i 로 interactive 강제 (출력 주의)
bash -i -c 'your_alias_command'

# 권장: alias 대신 함수 사용
# ~/.bashrc
my_func() { ls -la "$@"; }
# 스크립트에서
source ~/.bashrc && my_func /var/log
```

### SSH 원격 명령 실행 시 환경변수

```bash
# non-interactive라 ~/.bashrc 로드 안 됨
ssh user@host 'echo $MY_VAR'   # 빈 값

# 해결 1: bash -l (login shell)
ssh user@host 'bash -l -c "echo $MY_VAR"'

# 해결 2: 명시적 export
ssh user@host 'export MY_VAR=value; your_command'

# 해결 3: /etc/profile.d 에 등록 (전역 적용)
```

### 스크립트에서 interactive 여부 분기

```bash
#!/bin/bash
if [[ $- == *i* ]]; then
    # interactive: 컬러 출력
    RED='\033[0;31m'
    NC='\033[0m'
    echo -e "${RED}Warning${NC}"
else
    # non-interactive: 순수 텍스트
    echo "Warning"
fi
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Tips

### 디버깅

```bash
# 현재 쉘 상태 한눈에 확인
echo "flags: $-"
echo "login: $(shopt -q login_shell && echo yes || echo no)"
echo "tty: $(tty 2>/dev/null || echo none)"

# 어떤 파일이 로드됐는지 추적
bash -x -l -c 'exit' 2>&1 | grep "^\+"
```

### cron 디버깅 황금 패턴

```bash
# crontab에서 환경 덤프
* * * * * env > /tmp/cron_env.txt

# 실제 cron 환경 확인 후 스크립트에 동일하게 적용
cat /tmp/cron_env.txt
```

### source vs sh 실행 차이

| 실행 방식          | 프로세스       | 환경변수 적용    |
|--------------------|----------------|------------------|
| `bash script.sh`   | 자식 프로세스  | 부모에 미적용    |
| `source script.sh` | 현재 프로세스  | 현재 쉘에 적용   |
| `. script.sh`      | 현재 프로세스  | 현재 쉘에 적용   |

`export`, `cd`, `alias` 처럼 현재 쉘 환경을 바꾸는 명령은 반드시 `source` 로 실행합니다.

### /etc/profile.d 파일 관리

```bash
# 추가
sudo tee /etc/profile.d/my_setting.sh << 'EOF'
export MY_VAR="value"
export PATH=$PATH:/usr/local/bin
EOF

# 제거
sudo rm /etc/profile.d/my_setting.sh

# /etc/profile 직접 수정은 비권장
# → 시스템 업데이트 시 덮어써질 수 있음
# → 실수 시 모든 사용자 로그인에 영향
```

⚠️ cron 스크립트에서 `~/.bashrc` 의존은 금지. 필요한 PATH/환경변수는 스크립트 상단에 명시적으로 선언합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- GNU Bash Manual - Interactive Shells: [bash.info](https://www.gnu.org/software/bash/manual/bash.html#Interactive-Shells) — ★★★☆☆
- Linux man pages - bash: [man7.org](https://man7.org/linux/man-pages/man1/bash.1.html) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-28

**마지막 업데이트**: 2026-04-28

© 2026 siasia86. Licensed under CC BY 4.0.
