# tmux 운영 가이드

tmux는 하나의 터미널 안에서 여러 session·window·pane을 관리하는 터미널 multiplexer입니다. SSH 연결이 끊겨도 서버의 tmux session은 유지되므로 장시간 작업과 장애 대응에 유용합니다.

Neovim 내부 window 분할과 tmux pane 분할은 별개입니다. Neovim 분할은 [Neovim 활용 가이드](neovim_guide.md)를 참고합니다.

## 목차

| 섹션                                                                            |
|---------------------------------------------------------------------------------|
| [1. 구조와 키 표기](#1-구조와-키-표기) / [2. 설치와 session](#2-설치와-session) |
| [3. pane 분할](#3-pane-분할) / [4. window 관리](#4-window-관리)                 |
| [5. 복사 모드](#5-복사-모드) / [6. 설정 파일](#6-설정-파일)                     |
| [7. SSH 운영](#7-ssh-운영) / [8. 안전한 종료와 롤백](#8-안전한-종료와-롤백)     |

---

## 1. 구조와 키 표기

tmux의 기본 계층은 다음과 같습니다.

```text
Tmux server
└── Session
    ├── Window 1
    │   ├── Pane 1
    │   └── Pane 2
    └── Window 2
        └── Pane 1
```

- **Session**: 작업 전체를 보존하는 단위입니다.
- **Window**: 하나의 session 안에서 전환하는 탭입니다.
- **Pane**: 하나의 window를 나눈 터미널 영역입니다.

기본 prefix는 `Ctrl-b`입니다. `Ctrl-b %`는 세 키를 동시에 누르는 것이 아니라 다음 순서로 입력합니다.

```text
Ctrl-b를 누르고 손을 뗌 → %를 누름
```

이 문서에서 `C-b`는 `Ctrl-b`, `C-d`는 `Ctrl-d`를 의미합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치와 session

### 설치

Ubuntu·Debian:

```bash
sudo apt-get update
sudo apt-get install tmux
```

RHEL 계열:

```bash
sudo dnf install tmux
```

버전 확인:

```bash
tmux -V
```

### session 생성과 재접속

```bash
tmux new-session -s ops
```

`ops`라는 이름의 session을 생성하고 연결합니다.

```text
C-b d                  session에서 detach
```

detach는 tmux를 종료하지 않고 현재 터미널만 빠져나오는 동작입니다.

```bash
tmux list-sessions
tmux attach-session -t ops
```

현재 session을 확인하고 `ops`에 다시 연결합니다.

이미 있으면 연결하고 없으면 새로 생성하려면 다음과 같이 실행합니다.

```bash
tmux new-session -A -s ops
```

session을 명시적으로 종료할 때는 실행 중인 명령을 확인한 뒤 사용합니다.

```bash
tmux kill-session -t ops
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. pane 분할

pane은 하나의 tmux window 안에서 나뉜 터미널 영역입니다.

### 분할과 이동

```text
C-b %                  좌우 pane 분할
C-b "                  상하 pane 분할
C-b 방향키             인접 pane으로 이동
C-b o                  다음 pane으로 이동
C-b q                  pane 번호 표시
C-b x                  현재 pane 종료
```

`C-b %`의 결과는 좌우로 나뉘는 pane입니다. 여기서 `%`는 tmux가 처리하며 Neovim에는 전달되지 않습니다.

### 크기 조정과 확대

```text
C-b z                  현재 pane 확대·복원
C-b C-방향키           pane 크기를 조금씩 조정
```

정확한 크기 조정은 command mode에서 수행할 수 있습니다.

```bash
tmux resize-pane -L 10
tmux resize-pane -R 10
tmux resize-pane -U 5
tmux resize-pane -D 5
```

### Neovim과의 구분

```text
tmux pane 분할        C-b % 또는 C-b "
Neovim window 분할   C-w v 또는 C-w s
```

Neovim을 tmux 안에서 실행하면 바깥쪽 tmux pane과 안쪽 Neovim window를 함께 사용할 수 있습니다. 먼저 어느 계층을 나누려는지 확인해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. window 관리

window은 하나의 session 안에서 전환하는 탭과 같은 단위입니다.

```text
C-b c                  새 window 생성
C-b n                  다음 window
C-b p                  이전 window
C-b 0                  번호 0 window
C-b 1                  번호 1 window
C-b ,                  현재 window 이름 변경
C-b &                  현재 window 종료
```

command line에서 window을 생성하거나 이름을 지정할 수도 있습니다.

```bash
tmux new-window -t ops -n logs
tmux rename-window -t ops:0 editor
tmux list-windows -t ops
```

현재 window과 pane 목록을 확인합니다.

```bash
tmux list-windows -a
tmux list-panes -a
```

운영 작업에서는 다음처럼 역할별 window을 나누면 관리하기 쉽습니다.

```text
ops session
├── editor   설정·문서 편집
├── logs     로그 확인
└── monitor  상태 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 복사 모드

tmux의 scrollback 기록을 검색하거나 복사할 때 복사 모드를 사용합니다.

```text
C-b [                  복사 모드 진입
Space                  선택 시작
Enter                  선택 영역 복사
q                      복사 모드 종료
C-b ]                  붙여넣기
```

vi 스타일 이동을 사용하려면 `~/.tmux.conf`에 다음을 추가합니다.

```tmux
setw -g mode-keys vi
```

복사 모드에서 사용할 수 있는 예시는 다음과 같습니다.

```text
h j k l                커서 이동
/문자열                 검색
n                      다음 검색 결과
N                      이전 검색 결과
q                      종료
```

스크롤백을 파일로 저장해야 하는 경우 다음과 같이 현재 pane의 내용을 출력할 수 있습니다.

```bash
tmux capture-pane -p -S -100 -t ops:logs.0 > /tmp/tmux_logs.txt
```

민감정보가 포함된 pane을 파일로 저장하거나 공유하지 않도록 주의합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 설정 파일

사용자 설정 파일은 다음 경로에 둡니다.

```text
~/.tmux.conf
```

### 기본 설정 예시

```tmux
set -g mouse on
set -g history-limit 10000
set -g base-index 1
setw -g pane-base-index 1
setw -g mode-keys vi

bind r source-file ~/.tmux.conf \; display-message "tmux.conf reloaded"
```

- `mouse on`: 마우스 스크롤과 pane 선택을 활성화합니다.
- `history-limit`: pane scrollback 보관 줄 수를 설정합니다.
- `base-index`: window 번호를 1부터 시작합니다.
- `pane-base-index`: pane 번호를 1부터 시작합니다.
- `bind r`: 설정을 다시 읽습니다.

설정을 수정한 뒤 tmux 내부에서 다시 읽습니다.

```text
C-b r
```

또는 command line에서 실행합니다.

```bash
tmux source-file ~/.tmux.conf
```

설정 변경 전에는 기존 설정을 백업합니다.

```bash
cp ~/.tmux.conf ~/.tmux.conf.bak
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. SSH 운영

SSH 연결이 끊겨도 session을 유지하려면 원격 호스트에 접속한 뒤 tmux를 먼저 시작합니다.

```bash
ssh Secureuser123@example.com
tmux new-session -A -s ops
```

이후 작업을 수행하고 SSH 연결이 불안정해지면 다음을 실행합니다.

```text
C-b d
```

다시 접속한 뒤 session에 연결합니다.

```bash
ssh Secureuser123@example.com
tmux attach-session -t ops
```

장시간 로그 확인 예시:

```bash
tmux new-session -A -s monitor
# tmux 안에서
journalctl -fu example.service
```

SSH가 끊어져도 `journalctl` 명령과 tmux pane은 원격 호스트에서 계속 실행됩니다. 단, 호스트가 재부팅되면 기존 tmux server도 종료되므로 tmux는 백업이나 서비스 관리 도구가 아닙니다.

운영 배포 자체는 tmux의 수동 입력보다 Ansible·CI 같은 재현 가능한 자동화를 우선합니다. tmux는 진행 중인 로그 확인, 장애 대응, 긴급 복구 세션 보존에 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 안전한 종료와 롤백

### 종료 전 확인

다음 명령으로 session, window, pane의 실행 상태를 확인합니다.

```bash
tmux list-sessions
tmux list-windows -a
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_command}'
```

실행 중인 편집기·배포·로그 추적 명령을 확인한 뒤 종료합니다.

### session 종료

```bash
tmux kill-session -t ops
```

전체 tmux server를 종료하는 명령은 모든 session을 종료하므로 운영 중에는 사용하지 않습니다.

```bash
tmux kill-server
```

### 설정 롤백

`~/.tmux.conf` 변경이 문제를 일으키면 다음 순서로 되돌립니다.

```bash
cp ~/.tmux.conf.bak ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

현재 실행 중인 명령과 session을 먼저 확인하고 설정을 reload합니다. 설정 reload는 실행 중인 pane의 명령을 종료하지 않지만, key binding과 옵션은 즉시 변경될 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- tmux Manual: [man7.org/linux/man-pages/man1/tmux.1.html](https://man7.org/linux/man-pages/man1/tmux.1.html) — ★★★☆☆
- tmux GitHub: [github.com/tmux/tmux](https://github.com/tmux/tmux) — ★★★☆☆
- [Neovim 활용 가이드](neovim_guide.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-28

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.
