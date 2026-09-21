# Codex CLI Linux 설치 및 사용 가이드
<!-- reference: _reference/codex_cli_official_notes.md -->

OpenAI Codex CLI를 Linux 터미널에서 설치하고, 안전한 권한으로 대화형 작업과 자동화를 수행하는 가이드입니다.

## 목차

| 섹션                                                                                                  |
|-------------------------------------------------------------------------------------------------------|
| [1. 개요와 사전 점검](#1-개요와-사전-점검) / [2. 설치](#2-설치) / [3. 인증](#3-인증)                  |
| [4. 대화형 사용](#4-대화형-사용) / [5. 권한과 샌드박스](#5-권한과-샌드박스)                           |
| [6. 비대화형 실행](#6-비대화형-실행) / [7. 설정과 AGENTS.md](#7-설정과-agentsmd)                      |
| [8. 핵심 사용 팁](#8-핵심-사용-팁) / [9. 운영 체크리스트와 문제 해결](#9-운영-체크리스트와-문제-해결) |

---

## 1. 개요와 사전 점검

Codex CLI는 현재 Git 저장소의 파일을 읽고, 변경하고, 로컬 명령을 실행하는 터미널 기반 코딩 에이전트입니다. 대화형 TUI와 `codex exec` 비대화형 모드를 모두 제공합니다.

> TUI(Terminal User Interface): 터미널 안에서 키보드와 명령어로 사용하는 대화형 화면입니다. GUI 없이 모델·권한·세션을 조작할 수 있습니다.

### 사전 점검

```bash
uname -srm
command -v curl
command -v git
git rev-parse --show-toplevel
```

- Linux 호스트와 `git`을 확인합니다.
- Codex 작업은 기본적으로 Git 저장소 안에서 실행합니다.
- 현재 저장소가 없다면 먼저 안전한 작업 디렉토리를 만들고 Git 초기화를 검토합니다.
- 설치 후 Linux 샌드박스를 사용할 예정이면 `bubblewrap`도 확인합니다.

```bash
command -v bwrap || true
```

## 2. 설치

### Linux standalone installer

OpenAI 공식 설치 명령은 macOS와 Linux에서 사용할 수 있습니다.

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

원격 스크립트를 표준 입력으로 바로 실행하므로 운영 환경에서는 다음처럼 검토 가능한 절차를 우선합니다.

```bash
curl -fsSL https://chatgpt.com/codex/install.sh -o /tmp/codex-install.sh
less /tmp/codex-install.sh
sh /tmp/codex-install.sh
rm -f /tmp/codex-install.sh
```

🟡 `/tmp/codex-install.sh`는 공식 URL에서 직접 받은 파일인지 확인한 뒤 실행합니다. 조직 정책상 임시 파일 실행이 허용되지 않으면 패키지 저장소 또는 npm 경로를 사용합니다.

### npm 설치

Node.js와 npm을 이미 관리하고 있다면 npm 경로를 사용할 수 있습니다.

```bash
npm install -g @openai/codex
```

버전 확인과 실행 파일 위치를 확인합니다.

```bash
codex --version
command -v codex
```

### Homebrew 설치

Linuxbrew를 운영 중인 환경에서는 Homebrew Cask를 사용할 수 있습니다.

```bash
brew install --cask codex
brew upgrade --cask codex
```

### Linux 샌드박스 의존성

Codex가 Linux에서 명령을 제한된 환경에서 실행하도록 하려면 `bubblewrap`을 설치합니다.

> `bubblewrap`: Linux user namespace 기반으로 프로세스의 파일시스템·권한 경계를 만드는 샌드박스 도구입니다. Codex는 `bwrap` 실행 파일을 사용합니다.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install bubblewrap
```

Fedora:

```bash
sudo dnf install bubblewrap
```

설치 후 확인합니다.

```bash
command -v bwrap
bwrap --version
```

Ubuntu 24.04에서 user namespace 또는 AppArmor 경고가 계속되면 [공식 Sandbox 문서](https://developers.openai.com/codex/sandboxing.md)의 해당 배포판 절차를 검토합니다. 전역 AppArmor 제한을 무조건 해제하지 말고, 영향 범위와 보완 통제를 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 인증

### ChatGPT 계정 인증

대화형 브라우저 인증을 시작합니다.

```bash
codex login
```

인증 상태를 확인합니다.

```bash
codex login status
```

공유 호스트에서 작업을 끝냈다면 저장된 인증정보를 삭제합니다.

```bash
codex logout
```

### API key 인증

API key는 명령행 인자나 문서에 직접 쓰지 않고 표준 입력으로 전달합니다.

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

API key를 파일·shell history·CI 전체 환경에 남기지 않습니다. 자동화에서는 작업에 필요한 한 번의 실행 범위로만 주입하고, 가능하면 short-lived workload identity를 사용합니다.

Enterprise access token을 사용하는 자동화에서는 다음 공식 경로를 사용합니다.

```bash
printenv CODEX_ACCESS_TOKEN | codex login --with-access-token
```

`OPENAI_API_KEY`는 `codex login --with-api-key`에 표준 입력으로 전달할 때 사용합니다. 비대화형 `codex exec` 실행에서는 `CODEX_API_KEY`를 실행 단위로 주입할 수 있습니다. API key와 access token은 파일·shell history·로그에 남기지 않습니다.

### 인증 파일 보호

```bash
ls -l ~/.codex/auth.json 2>/dev/null || true
grep -RniE 'OPENAI_API_KEY|CODEX_API_KEY|CODEX_ACCESS_TOKEN' . --exclude-dir=.git || true
```

`~/.codex/auth.json`이 존재하면 자격증명 저장 파일로 취급합니다. Git에 추가하지 않고, 백업·로그·화면 공유 대상에서도 제외합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 대화형 사용

Git 저장소에서 Codex를 시작합니다.

```bash
cd /path/to/repository
codex
```

첫 프롬프트는 작업 범위와 검증 방법을 함께 지정하는 방식이 안전합니다.

```text
이 저장소의 구조를 요약하고, 변경하지 않은 상태에서 테스트 실행 방법과 위험 요소를 제시해.
```

### 자주 사용하는 명령

| 명령어                | 용도                                           |
|-----------------------|------------------------------------------------|
| `/model`              | 현재 모델과 reasoning effort 선택              |
| `/status`             | 모델·승인 정책·writable roots·token usage 확인 |
| `/permissions`        | 세션 권한 프로필 변경                          |
| `/diff`               | 현재 Git 변경 확인                             |
| `/review`             | working tree·commit·base branch 코드 리뷰      |
| `/compact`            | 대화 이력 요약으로 context token 절약          |
| `/resume`             | 저장된 세션 선택                               |
| `/exit`, `/quit`      | CLI 종료                                       |
| `?`                   | TUI 단축키 도움말 표시                         |
| `codex resume --last` | 현재 디렉토리의 최근 대화 재개                 |
| `codex fork --last`   | 최근 대화를 새 세션으로 분기                   |

장시간 작업에서는 `/status`로 현재 권한과 context 사용량을 확인하고, 중간 결과·결정·다음 작업을 파일에 기록한 후 `/compact`를 실행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 권한과 샌드박스

샌드박스는 명령이 접근할 수 있는 파일과 네트워크 범위를 제한하고, 승인 정책은 경계를 넘을 때 사용자의 확인을 요구할지 결정합니다. 두 통제는 서로 대체하지 않습니다.

| 모드                 | 기본 의미                           | 사용 기준                     |
|----------------------|-------------------------------------|-------------------------------|
| `read-only`          | 읽기 중심, 파일 수정 제한           | 분석·리뷰·탐색                |
| `workspace-write`    | 작업 디렉토리 중심의 파일 수정 허용 | 일반 개발·문서 작성           |
| `danger-full-access` | 파일시스템·네트워크 제한 제거       | 격리된 runner·container에서만 |

일반적인 로컬 작업은 다음 조합으로 시작합니다.

```bash
codex --sandbox workspace-write --ask-for-approval on-request
```

읽기 전용 리뷰는 권한을 더 낮춥니다.

```bash
codex --sandbox read-only --ask-for-approval on-request
```

비대화형 실행도 동일한 원칙을 적용합니다.

```bash
codex exec --sandbox read-only --ask-for-approval on-request "변경 없이 저장소의 위험 요소를 점검해"
codex exec --sandbox workspace-write --ask-for-approval on-request "테스트 실패의 최소 수정안을 적용해"
```

🟡 `--ask-for-approval never`와 `--sandbox danger-full-access`는 임의의 저장소 코드가 실행될 수 있는 환경에서 사용하지 않습니다. 자동화가 필요하면 격리된 runner, 최소 권한 토큰, 변경 검토 단계를 함께 둡니다.

설정 파일 예시:

```toml
# ~/.codex/config.toml
# Choose a model shown by `/model` for this account.
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 비대화형 실행

`codex exec`는 CI, scheduled job, shell pipeline에서 사용하는 비대화형 모드입니다.

### 기본 실행

```bash
codex exec "저장소 구조를 요약하고 위험 영역 5개를 제시해"
```

진행 정보는 `stderr`, 최종 응답은 `stdout`으로 출력되므로 파이프라인에 연결할 수 있습니다.

```bash
codex exec "최근 10개 commit의 release note를 작성해" | tee release-notes.md
```

### JSON Lines 출력

자동화에서 이벤트를 처리하려면 JSON Lines를 사용합니다.

```bash
codex exec --json "저장소 구조를 JSON 이벤트로 분석해" | jq
```

### 세션·출력 관리

```bash
codex exec --ephemeral "저장소를 분석하고 다음 단계를 제시해"
codex exec "동시성 문제를 검토해"
codex exec resume --last "발견한 동시성 문제의 최소 수정안을 제시해"
```

`--ephemeral`은 세션 rollout 파일을 디스크에 저장하지 않는 옵션입니다. 장기 작업의 재개가 필요하면 사용하지 않고 세션 보존 정책을 확인합니다.

### Git 저장소 안전 확인

Codex는 기본적으로 Git 저장소 안에서 실행하도록 요구합니다.

```bash
git rev-parse --show-toplevel
```

`--skip-git-repo-check`는 작업 디렉토리와 변경 영향 범위를 직접 확인한 경우에만 사용합니다.

### CI 자격증명 원칙

- 공개 저장소 또는 저장소 제어 코드가 실행되는 job에 API key를 전역 환경변수로 노출하지 않습니다.
- 공식 GitHub Actions를 사용할 수 있으면 직접 설치·인증보다 우선 검토합니다.
- API key가 필요한 경우 Codex 실행 단계에만 최소 범위로 주입합니다.
- `auth.json`, API key, access token을 artifact·로그·PR에 포함하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 설정과 AGENTS.md

### 설정 파일

- 사용자 설정: `~/.codex/config.toml`.
- 프로젝트 설정: 신뢰된 저장소의 `.codex/config.toml`.
- 한 번만 적용할 설정: `-c key=value` 또는 `--config key=value`.
- 우선순위: CLI 옵션·일회성 override → 프로젝트 설정 → profile → 사용자 설정 → system 설정 → 기본값.

```toml
# ~/.codex/config.toml
# Choose a model shown by `/model` for this account.
approval_policy = "on-request"
sandbox_mode = "workspace-write"
model_auto_compact_token_limit = 120000
```

`model_auto_compact_token_limit`은 자동 대화 요약을 시작할 token threshold입니다. 설정 변경 후 `/status`로 실제 적용 상태를 확인합니다. `project_doc_max_bytes`는 각 `AGENTS.md` 파일에서 읽을 최대 바이트 수를 설정하며, 기본값과 실제 적용 범위는 설치 버전의 공식 설정 레퍼런스를 확인합니다.

### AGENTS.md 지침

Codex는 전역 `~/.codex/AGENTS.md`와 Git root부터 현재 작업 디렉토리까지의 `AGENTS.md`를 계층적으로 읽습니다. 하위 디렉토리의 지침이 뒤에 결합되므로 저장소별 규칙을 범위에 맞게 배치합니다.

```bash
mkdir -p ~/.codex
cat > ~/.codex/AGENTS.md <<'EOF'
# Global instructions

- Run the relevant tests after modifying files.
- Do not expose secrets in command output or documentation.
EOF
```

프로젝트 지침은 저장소 루트에 둡니다.

```bash
cat > AGENTS.md <<'EOF'
# Repository instructions

- Read the repository contribution guide before editing.
- Run the documented lint and test commands before committing.
EOF
```

### MCP 연결

MCP(Model Context Protocol) 서버는 외부 도구를 Codex에 연결하는 프로토콜입니다.

```bash
codex mcp add <server-name> -- <server-command> <arg>
codex mcp list
codex mcp login <server-name>
```

외부 MCP 서버는 도구 권한과 전송 데이터 범위를 먼저 검토하고, 필요하지 않은 서버는 활성화하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 핵심 사용 팁

### 요청은 목표·범위·검증을 함께 지정

Codex에게 작업을 맡길 때 목표만 전달하지 말고 변경 범위, 제약 조건, 검증 방법을 함께 지정합니다.

```text
목표:
- Ansible 역할의 SSH 설정을 개선해.

범위:
- ansible/roles/ssh_hardening/ 내부만 수정해.

제약:
- 비밀번호 인증은 비활성화하되 기존 SSH 포트는 변경하지 마.
- 비밀정보를 파일이나 출력에 기록하지 마.

검증:
- YAML 문법 검사와 ansible-lint를 실행해.
- 변경 파일, 테스트 결과, rollback 방법을 보고해.

먼저 현재 구조와 위험 요소를 분석하고, 승인 없이 수정하지 마.
```

### 분석·수정·검증을 분리

처음에는 읽기 전용으로 분석한 뒤, 계획을 검토하고 수정 권한을 부여합니다.

```bash
codex exec --sandbox read-only "저장소 구조와 변경 위험을 분석하고 수정 계획만 제시해"
codex --sandbox workspace-write --ask-for-approval on-request
```

수정 후에는 `/status`, `/diff`, `/review`와 프로젝트의 테스트·lint 명령을 차례로 실행합니다. `Codex가 완료했다고 보고한 것`과 실제 검증 통과 여부를 구분합니다.

### `AGENTS.md`와 Skills로 반복 규칙 고정

- 저장소 공통 규칙은 루트 `AGENTS.md`에 둡니다.
- 반복 작업은 `/skills`로 목록을 확인하고 `$skill-name`으로 명시적으로 호출합니다.
- npm 또는 standalone 설치만으로 Skills가 자동 설치되지는 않습니다.
- Codex 공식 Skills 문서에 따라 repository·user·admin·system 위치에서 skills를 찾습니다. 실제 검색 경로와 활성화 상태는 설치 버전·client·관리 정책에 따라 `/skills`와 `config.toml`에서 확인합니다.
- 일반적인 local 경로는 repository의 `.agents/skills/`, 사용자 `$HOME/.agents/skills/`, admin `/etc/codex/skills/`입니다. `~/.kiro/skills/`는 Codex의 자동 검색 경로로 가정하지 않고, 필요한 경우 skill을 명시적으로 등록·호출합니다.

### 최소 권한과 자격증명 보호

- 일반 작업은 `workspace-write`와 `on-request`로 시작합니다.
- `danger-full-access`와 `--ask-for-approval never`는 격리된 runner·container에서만 사용합니다.
- API key, `~/.codex/auth.json`, access token을 프롬프트·`AGENTS.md`·로그·commit에 기록하지 않습니다.
- 외부 Skill과 MCP는 지침 및 실행 스크립트를 검토한 후 최소 권한으로 활성화합니다.

### 긴 작업은 요약·재개 단위로 관리

대화가 길어지면 `/compact` 전에 목표, 변경 파일, 완료된 검증, 남은 작업을 요약하도록 요청합니다. 작업을 이어갈 때는 다음 명령을 사용합니다.

```bash
codex resume --last
```

## 9. 운영 체크리스트와 문제 해결

### 설치·실행 확인

```bash
codex --version
codex login status
command -v bwrap
codex --help
```

### 문제별 확인

| 증상                       | 확인 항목                                                      |
|----------------------------|----------------------------------------------------------------|
| `codex: command not found` | `command -v codex`, PATH, 설치 방식과 shell 재시작             |
| 로그인 실패                | `codex login status`, 브라우저 인증, 조직 workspace 권한       |
| Linux sandbox 경고         | `command -v bwrap`, `bwrap --version`, user namespace·AppArmor |
| 파일 수정이 거부됨         | `/permissions`, `--sandbox`, writable roots, 승인 정책         |
| 세션을 찾지 못함           | 같은 작업 디렉토리에서 `codex resume --last` 실행              |
| CI가 대화 입력에서 멈춤    | `codex exec`, 명시적 sandbox·approval, `--json` 출력           |

### 변경 전후 운영 순서

1. `git status`와 `git diff`로 현재 변경을 확인합니다.
2. 요청 범위와 writable directory를 최소화합니다.
3. `workspace-write`와 `on-request`로 시작합니다.
4. Codex 변경 후 테스트·lint·보안 검사를 직접 재실행합니다.
5. `git diff`를 검토한 뒤 별도 commit 또는 PR 절차를 진행합니다.
6. 실패 시 변경을 무조건 자동 되돌리지 말고 diff와 로그를 확인한 후 필요한 범위만 rollback합니다.

> `codex exec`는 자동화 도구이지 승인된 배포 절차를 대체하지 않습니다. 운영 환경 변경은 별도 IaC plan·review·rollback 절차를 적용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OpenAI Codex CLI: [developers.openai.com/codex/cli.md](https://developers.openai.com/codex/cli.md) — ★★★☆☆
- OpenAI Authentication: [developers.openai.com/codex/auth.md](https://developers.openai.com/codex/auth.md) — ★★★☆☆
- OpenAI Sandbox: [developers.openai.com/codex/sandboxing.md](https://developers.openai.com/codex/sandboxing.md) — ★★★☆☆
- OpenAI Non-interactive mode: [developers.openai.com/codex/non-interactive-mode.md](https://developers.openai.com/codex/non-interactive-mode.md) — ★★★☆☆
- OpenAI Configuration reference: [developers.openai.com/codex/config-file/config-reference.md](https://developers.openai.com/codex/config-file/config-reference.md) — ★★★☆☆
- OpenAI Skills & Plugins: [developers.openai.com/codex/skills-and-plugins.md](https://developers.openai.com/codex/skills-and-plugins.md) — ★★★☆☆
- OpenAI Build skills: [developers.openai.com/codex/build-skills.md](https://developers.openai.com/codex/build-skills.md) — ★★★☆☆
- OpenAI Codex releases: [github.com/openai/codex/releases](https://github.com/openai/codex/releases) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-14

**마지막 업데이트**: 2026-09-16

© 2026 siasia86. Licensed under CC BY 4.0.
