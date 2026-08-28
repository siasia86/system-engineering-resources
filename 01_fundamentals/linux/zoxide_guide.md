# zoxide 설치 및 사용 가이드

`zoxide`는 자주 방문하는 디렉토리를 학습하고, 경로 일부만 입력해 빠르게 이동할 수 있게 해주는 command-line 도구입니다. `zoxide` 자체는 실행 파일이고, shell 초기화 후 사용하는 명령은 보통 `z`입니다.

```text
zoxide       설치되는 실행 파일
z            학습된 경로로 이동하는 shell function
zi           대화형 경로 선택 명령
```

`zoxide`는 `zsh`가 아닙니다. `zsh`는 shell이고, zoxide는 zsh·Bash·Fish에서 사용할 수 있는 디렉토리 이동 도구입니다.

## 목차

| 섹션                                                                                      |
|-------------------------------------------------------------------------------------------|
| [1. 설치](#1-설치) / [2. Shell 초기화](#2-shell-초기화)                                   |
| [3. 기본 사용법](#3-기본-사용법) / [4. 경로 데이터 관리](#4-경로-데이터-관리)             |
| [5. 대화형 선택](#5-대화형-선택) / [6. 설정과 진단](#6-설정과-진단)                       |
| [7. 운영 스크립트 주의사항](#7-운영-스크립트-주의사항) / [8. 제거와 롤백](#8-제거와-롤백) |

---

## 1. 설치

### Ubuntu·Debian

```bash
sudo apt-get update
sudo apt-get install zoxide
```

### Fedora·RHEL 계열

```bash
sudo dnf install zoxide
```

### Arch Linux

```bash
sudo pacman -S zoxide
```

배포판 저장소에 원하는 버전이 없을 때는 Rust toolchain이 설치된 사용자 환경에서 다음 방법을 사용할 수 있습니다.

```bash
cargo install zoxide --locked
```

패키지 설치 후 실행 파일을 확인합니다.

```bash
command -v zoxide
zoxide --version
```

외부 설치 script를 무조건 `curl | sh` 형태로 실행하지 않습니다. 패키지 저장소나 검토 가능한 고정 버전 artifact를 우선 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Shell 초기화

zoxide는 shell hook을 등록해야 디렉토리 이동 기록을 학습합니다.

### zsh

`~/.zshrc` 마지막에 추가합니다.

```zsh
eval "$(zoxide init zsh)"
```

현재 shell에 다시 적용합니다.

```bash
source ~/.zshrc
```

### Bash

`~/.bashrc` 마지막에 추가합니다.

```bash
eval "$(zoxide init bash)"
```

적용합니다.

```bash
source ~/.bashrc
```

### Fish

Fish shell에서는 다음을 사용합니다.

```fish
zoxide init fish | source
```

정상 등록 여부를 확인합니다.

```bash
type z
type zi
```

정상적으로 초기화되면 `z`와 `zi`가 shell function 또는 shell command로 표시됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 사용법

먼저 평소처럼 여러 디렉토리를 방문합니다.

```bash
cd ~/projects
cd ~/work/company/project
cd ~/documents
```

zoxide는 shell hook을 통해 디렉토리 이동을 기록합니다. 이후 경로의 일부만 입력합니다.

```bash
z project
```

이름에 `project`가 포함된 경로 중 사용 빈도와 최근 사용 시점을 기준으로 적합한 경로로 이동합니다.

여러 단어를 지정하면 검색 범위를 좁힐 수 있습니다.

```bash
z company project
z work
z documents
```

자주 쓰는 기본 명령은 다음과 같습니다.

```bash
z -                  이전 디렉토리로 이동
zoxide query -l      학습된 경로 목록 출력
zoxide add ~/project 경로를 직접 등록
zoxide remove ~/project 경로를 제거
```

`z`는 directory name 일부를 사용하는 interactive shortcut이고, 명확한 경로 이동이 필요한 작업에는 일반 `cd`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 경로 데이터 관리

### `zoxide query` — 검색 결과 확인

실제 이동 전에 검색 결과만 확인할 수 있습니다.

```bash
zoxide query project
zoxide query company project
zoxide query -l
```

`-l`은 학습된 전체 경로를 출력합니다. 결과가 예상과 다르면 후보 경로와 사용 빈도를 확인합니다.

### `zoxide add` — 경로 직접 등록

아직 방문하지 않은 경로를 직접 등록할 수 있습니다.

```bash
zoxide add ~/work/company/project
```

### `zoxide remove` — 경로 제거

더 이상 사용하지 않는 경로를 제거합니다.

```bash
zoxide remove ~/old-project
```

경로가 여러 개라면 shell glob이 의도하지 않은 값을 확장하지 않는지 확인한 뒤 실행합니다.

### 데이터베이스 위치 확인

운영체제와 설정에 따라 데이터베이스 위치가 달라질 수 있으므로 환경변수와 설정을 먼저 확인합니다.

```bash
printenv _ZO_DATA_DIR
printenv XDG_DATA_HOME
zoxide query -l
```

데이터베이스 파일을 직접 편집하지 않고 `add`, `remove`, `query` 명령으로 관리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대화형 선택

`zi`는 검색 후보를 목록으로 표시하고 선택하게 해줍니다.

```bash
zi project
```

대화형 선택 기능을 사용하려면 보통 `fzf`가 필요합니다.

Ubuntu·Debian:

```bash
sudo apt-get install fzf
```

`zi`가 동작하지 않으면 다음을 확인합니다.

```bash
command -v fzf
type zi
```

대화형 terminal이 없는 CI·Ansible task·cron에서는 `zi`를 사용하지 않습니다. 자동화 환경에서는 절대경로 또는 명시적인 `cd`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 설정과 진단

### 명령과 shell 구분

`zoxide` 설치 후 `z`가 없으면 실행 파일만 설치되고 shell 초기화가 누락되었을 가능성이 큽니다.

```bash
command -v zoxide
command -v z
type z
```

다음 설정이 현재 shell에 적용되어 있는지 확인합니다.

```bash
grep -n "zoxide init" ~/.zshrc ~/.bashrc 2>/dev/null
```

### 자주 발생하는 문제

- `z: command not found`: `zoxide init` 설정을 shell 설정 파일에 추가하지 않은 상태입니다.
- 후보가 없음: 해당 경로를 방문하지 않았거나 `zoxide add`가 필요합니다.
- 잘못된 경로 선택: `zoxide query -l`로 학습 목록을 정리합니다.
- `zi` 실행 실패: `fzf` 설치와 interactive terminal 여부를 확인합니다.
- 새 terminal에서 동작하지 않음: `.zshrc` 또는 `.bashrc`를 다시 읽거나 새 login shell을 시작합니다.

### 선택적 환경변수

검색 결과 수나 명령 동작을 변경하기 전에 현재 zoxide 버전의 공식 문서를 확인합니다.

```bash
zoxide --help
zoxide init --help
```

환경변수는 shell 설정 파일에 기록할 때 팀 표준과 충돌하지 않는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 운영 스크립트 주의사항

zoxide는 interactive 사용성을 위한 도구입니다. 운영 자동화에서는 결과가 사용자의 학습 데이터와 shell 상태에 의존하지 않도록 해야 합니다.

### 운영 스크립트에서 사용하지 않을 패턴

```bash
#!/usr/bin/env bash
z project
```

이 코드는 실행 사용자의 zoxide database와 현재 shell hook에 따라 다른 경로로 이동할 수 있습니다.

### 명시적 경로 사용

```bash
#!/usr/bin/env bash
set -euo pipefail

project_dir="/opt/example/project"
cd "$project_dir"
```

Ansible에서는 `z` 대신 `ansible.builtin.command`의 `chdir` 또는 task의 명시적 경로를 사용합니다.

```yaml
- name: Run command in project directory
  ansible.builtin.command: ./check.sh
  args:
    chdir: /opt/example/project
```

zoxide는 개발 PC의 interactive shell과 수동 장애 대응에 사용하고, CI·cron·배포 script의 경로 결정에는 사용하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 제거와 롤백

### Shell 설정 제거

`~/.zshrc` 또는 `~/.bashrc`에서 다음 줄을 제거합니다.

```zsh
eval "$(zoxide init zsh)"
```

현재 shell에 다시 적용합니다.

```bash
source ~/.zshrc
```

### 패키지 제거

Ubuntu·Debian:

```bash
sudo apt-get remove zoxide
```

Fedora·RHEL 계열:

```bash
sudo dnf remove zoxide
```

패키지 제거 후 기존 `cd`는 계속 사용할 수 있습니다. zoxide가 기록한 경로 데이터는 필요 여부를 확인한 뒤 별도로 정리합니다.

설정 변경 전 백업이 있다면 다음처럼 복구합니다.

```bash
cp ~/.zshrc.bak ~/.zshrc
source ~/.zshrc
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- zoxide Documentation: [github.com/ajeetdsouza/zoxide](https://github.com/ajeetdsouza/zoxide) — ★★★☆☆
- zoxide Manual: [zoxide.1](https://man.archlinux.org/man/zoxide.1) — ★★★☆☆
- fzf: [github.com/junegunn/fzf](https://github.com/junegunn/fzf) — ★★★☆☆

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
