# Claude Code CLI Linux 가이드
<!-- reference: _reference/claude_code_official_notes.md -->

Linux 서버와 WSL에서 Claude Code CLI를 설치·인증하고, 권한을 제한해 대화형·비대화형으로 사용하는 방법을 정리합니다. 개념은 [Claude Code 공통 개념](claude_code_concepts.md), 매일 쓰는 흐름은 [기본 사용법](claude_code_basics_guide.md), 지침 파일과 확장 기능은 [확장 기능 가이드](claude_code_extensions_guide.md)를 참고합니다.

🟡 이 문서의 명령과 옵션은 2026-10-14 공식 문서 기준입니다. 2026-10-15 작성 서버에서는 데스크톱 앱이 SSH 세션용으로 설치한 Claude Code 2.1.295의 `--version`만 실행해 확인했고, 설치·인증·권한 명령은 실제 실행 결과로 확인하지 않았습니다. 최신 GitHub 릴리스는 v2.1.299(2026-10-14)입니다.

## 목차

| 단계 | 섹션                                                                                  |
|------|---------------------------------------------------------------------------------------|
| 준비 | [1. 사전 점검](#1-사전-점검) / [2. 설치](#2-설치) / [3. 인증](#3-인증)                |
| 사용 | [4. 대화형 사용](#4-대화형-사용) / [5. 권한 설정](#5-권한-설정)                       |
| 자동 | [6. 비대화형 실행과 CI](#6-비대화형-실행과-ci) / [7. 업데이트 관리](#7-업데이트-관리) |
| 운영 | [8. 운영 체크리스트와 문제 해결](#8-운영-체크리스트와-문제-해결)                      |

---

## 1. 사전 점검

| 항목     | 요구 사항                                                        |
|----------|------------------------------------------------------------------|
| OS       | Ubuntu 20.04+, Debian 10+, Alpine 3.19+, RHEL·Fedora(dnf 저장소) |
| 하드웨어 | RAM 4GB 이상, x64 또는 ARM64                                     |
| 네트워크 | 인터넷 연결 필요                                                 |
| 셸       | Bash 또는 Zsh                                                    |
| 계정     | Pro·Max·Team·Enterprise 구독 또는 Claude Console 계정            |

```bash
# OS·아키텍처 확인
cat /etc/os-release
uname -m

# 기존 설치 여부 확인
command -v claude && claude --version
```

데스크톱 앱의 SSH 세션으로 접속한 서버에는 앱이 `~/.claude/remote/ccd-cli/<버전>`에 Claude Code를 따로 설치합니다. 이 파일은 `PATH`에 추가되지 않으므로 `command -v claude`로는 보이지 않습니다. 터미널에서 직접 쓰려면 아래 방법으로 별도 설치합니다. 데스크톱 앱 사용법은 [데스크톱 앱 가이드](claude_code_desktop_guide.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### Native 설치 (권장)

```bash
curl -fsSL https://claude.ai/install.sh | bash

# 새 터미널에서 확인
claude --version
```

- 설치 위치: `~/.local/bin/claude`가 `~/.local/share/claude/versions/` 아래 실제 버전을 가리키는 symlink입니다.
- 백그라운드에서 자동 업데이트됩니다.
- 원격 스크립트를 바로 실행하므로, 운영 서버에서는 스크립트를 내려받아 검토한 뒤 실행하거나 아래 패키지 저장소를 사용합니다.

### 패키지 저장소 (apt·dnf)

서명된 저장소에는 `stable`(약 1주 지연, 큰 회귀 제외)과 `latest` 채널이 있습니다. 패키지 설치는 자동 업데이트되지 않습니다.

```bash
# Debian·Ubuntu: 서명 키 등록 후 fingerprint 확인
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
  -o /etc/apt/keyrings/claude-code.asc
gpg --show-keys /etc/apt/keyrings/claude-code.asc
# 기대값: 31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE

echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-code.list
sudo apt update
sudo apt install claude-code
```

```bash
# RHEL·Fedora
sudo tee /etc/yum.repos.d/claude-code.repo <<'EOF'
[claude-code]
name=Claude Code
baseurl=https://downloads.claude.ai/claude-code/rpm/stable
enabled=1
gpgcheck=1
gpgkey=https://downloads.claude.ai/keys/claude-code.asc
EOF
sudo dnf install claude-code
```

### npm 설치

```bash
# Node.js 22 이상 필요
node --version
npm install -g @anthropic-ai/claude-code
```

### 설치 진단

```bash
# 세션을 열지 않고 설치·설정 상태를 읽기 전용으로 점검
claude doctor
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 인증

### 구독 계정 로그인

```bash
cd ~/project
claude
# 첫 실행 시 브라우저 로그인 안내 → 로그인 후 터미널로 돌아옴
```

브라우저가 없는 서버에서는 표시되는 URL을 다른 기기의 브라우저에서 열어 인증합니다.

### API 키·토큰

| 방식                         | 설정                                             | 용도                                 |
|------------------------------|--------------------------------------------------|--------------------------------------|
| Console API 키               | `ANTHROPIC_API_KEY`                              | 종량제 직접 연결                     |
| 장기 OAuth 토큰              | `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN` | 구독 계정으로 CI·스크립트 실행 (1년) |
| Bedrock·Google Cloud·Foundry | `CLAUDE_CODE_USE_BEDROCK=1` 등                   | 조직 클라우드 계정                   |
| LLM gateway                  | `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`     | 사내 프록시 경유                     |

```bash
# 현재 사용 중인 인증 방식 확인 (세션 안에서)
/status

# 구독으로 쓰려는데 API 키가 우선 적용될 때
unset ANTHROPIC_API_KEY
```

### 자격 증명 보호

- Linux 저장 위치: `~/.claude/.credentials.json` (권한 `0600`).
- 공용 계정이나 공유 홈 디렉터리에서는 로그인하지 않습니다.
- `claude setup-token`은 토큰을 화면에 한 번만 출력하고 저장하지 않습니다. CI secret에 바로 등록하고 셸 history·로그에 남기지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 대화형 사용

```bash
claude                          # 새 세션
claude -c                       # 현재 디렉터리의 최근 대화 이어가기
claude -r                       # 세션 목록에서 골라 재개
claude --model opus             # 모델 지정
claude --permission-mode plan   # 분석 전용 모드로 시작
claude --add-dir ../shared-lib  # 작업 디렉터리 추가
```

### 자주 쓰는 slash 명령

| 명령           | 용도                                          |
|----------------|-----------------------------------------------|
| `/init`        | 프로젝트를 분석해 `CLAUDE.md` 초안 생성       |
| `/model`       | 모델과 effort 변경                            |
| `/permissions` | 허용·확인·거부 규칙 관리                      |
| `/status`      | 버전, 모델, 계정, 연결 상태 확인              |
| `/usage`       | 세션 비용과 플랜 사용량 확인 (`/cost`는 별칭) |
| `/context`     | 컨텍스트 사용량 확인                          |
| `/compact`     | 대화를 요약해 컨텍스트 확보                   |
| `/clear`       | 새 대화 시작                                  |
| `/rewind`      | 이전 시점으로 대화·코드 되돌리기              |
| `/memory`      | `CLAUDE.md`와 auto memory 편집                |
| `/mcp`         | MCP 서버 연결·인증 관리                       |
| `/config`      | 설정 화면 열기                                |

### 단축키

- `Shift+Tab`: 권한 모드 순환
- `Esc`: 진행 중인 응답 중단

[⬆ 목차로 돌아가기](#목차)

---

## 5. 권한 설정

### 권한 모드 선택

| 상황                      | 시작 방법                                    |
|---------------------------|----------------------------------------------|
| 처음 보는 코드, 운영 서버 | `claude --permission-mode default`           |
| 변경 전 분석              | `claude --permission-mode plan`              |
| 검토하며 반복 수정        | `claude --permission-mode acceptEdits`       |
| 긴 작업, 승인 줄이기      | `claude --permission-mode auto`              |
| 격리된 컨테이너·VM        | `claude --permission-mode bypassPermissions` |

v2.1.283 이상의 대화형 세션은 기본으로 `auto` 모드로 시작합니다. 기본값을 바꾸려면 설정 파일에 지정합니다.

```json
{
  "permissions": {
    "defaultMode": "default"
  }
}
```

### 허용·거부 규칙

규칙은 `Tool` 또는 `Tool(specifier)` 형식이며 **deny → ask → allow** 순서로 평가됩니다. 먼저 일치한 규칙이 결과를 결정합니다.

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git commit *)"
    ],
    "deny": [
      "Bash(git push *)",
      "Read(./.env)",
      "Read(./secrets/**)"
    ]
  }
}
```

- `*`는 하위 명령 뒤에 둡니다. `Bash(git log *)`는 `git log`만, `Bash(git *)`는 모든 git 명령을 허용합니다.
- Bash 규칙은 명령 문자열 기준입니다. `Bash(git push *)`는 `git -C . push`나 `bash -c '...'`처럼 다른 형태로 쓴 명령을 막지 못합니다. 반드시 막아야 하는 작업은 샌드박스·OS 권한·자격 증명 분리로 함께 막습니다.
- 설정 파일 위치와 우선순위는 [확장 기능 가이드](claude_code_extensions_guide.md#2-설정-파일)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 비대화형 실행과 CI

### 기본 실행

```bash
# 결과만 출력
claude -p "README.md를 세 줄로 요약"

# 허용 도구를 지정해 승인 없이 실행
claude -p "auth.py의 버그를 찾아 수정" --allowedTools "Read,Edit,Bash"

# 표준 입력으로 데이터 전달
cat build-error.txt | claude -p "빌드 실패 원인을 설명"
```

### 출력 형식

| 옵션                          | 결과                                          |
|-------------------------------|-----------------------------------------------|
| `--output-format text`        | 일반 텍스트 (기본)                            |
| `--output-format json`        | 결과·세션 ID·비용(`total_cost_usd`) 포함 JSON |
| `--output-format stream-json` | 실시간 줄 단위 JSON                           |
| `--json-schema '<schema>'`    | 지정한 JSON Schema 형식의 결과 (json과 함께)  |

```bash
claude -p "프로젝트 요약" --output-format json | jq -r '.result'
```

### CI에서 안전하게 실행

```bash
claude --bare -p "테스트 실행 후 실패 요약" \
  --permission-mode dontAsk \
  --allowedTools "Bash(npm test)" "Read" \
  --max-turns 10
```

- `--bare`: 저장소나 `~/.claude`의 hook·skill·plugin·MCP·CLAUDE.md를 자동으로 읽지 않아 모든 머신에서 같은 결과를 냅니다. 구독 로그인을 쓰지 않으므로 `ANTHROPIC_API_KEY`가 필요합니다.
- 🟡 `--bare` 없이 `-p`를 실행하면 신뢰 확인 없이 프로젝트 `.claude/settings.json`의 hook과 `.mcp.json` 서버가 실행됩니다. 외부 PR 코드처럼 신뢰할 수 없는 저장소에서는 반드시 `--bare`를 씁니다.
- `dontAsk`: 사전 허용한 도구 외에는 묻지 않고 거부합니다.
- `--max-turns`: 반복 횟수 상한. 도달하면 오류로 종료합니다.
- API 키·토큰은 CI secret으로 주입하고 로그에 출력하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 업데이트 관리

```bash
# 즉시 업데이트
claude update

# 업데이트 결과·자동 업데이트 상태 확인
claude doctor
```

| 설정 (`settings.json`)                | 효과                                        |
|---------------------------------------|---------------------------------------------|
| `"autoUpdatesChannel": "stable"`      | 약 1주 지연된 안정 채널 사용                |
| `"minimumVersion": "2.1.283"`         | 이 버전 아래로 내려가지 않음                |
| `"env": {"DISABLE_AUTOUPDATER": "1"}` | 백그라운드 자동 업데이트 끄기 (수동은 가능) |
| `"env": {"DISABLE_UPDATES": "1"}`     | 수동 포함 모든 업데이트 차단                |

운영 서버에서는 `stable` 채널과 `minimumVersion`을 함께 지정해 검증된 버전 범위를 유지합니다. apt·dnf 설치는 패키지 관리자로 업그레이드합니다(`sudo apt upgrade claude-code`, `sudo dnf upgrade claude-code`).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 운영 체크리스트와 문제 해결

### 설치·실행 확인

- [ ] `claude --version`이 버전을 출력하는지
- [ ] `claude doctor`에 설정 파일 오류나 경고가 없는지
- [ ] `/status`의 인증 방식이 의도한 계정인지 (구독 / API 키)
- [ ] 운영 서버의 기본 권한 모드가 `default` 또는 `plan`으로 지정되었는지
- [ ] `.env`·secret 경로에 `Read` deny 규칙이 있는지
- [ ] CI 실행에 `--bare`와 `dontAsk`, 허용 도구 목록을 지정했는지

### 문제별 확인

| 증상                            | 확인                                                            |
|---------------------------------|-----------------------------------------------------------------|
| `claude: command not found`     | 새 터미널을 열고 `~/.local/bin`이 `PATH`에 있는지 확인          |
| 설치 스크립트가 `403`·HTML 오류 | 공식 지원 국가·프록시 확인, 패키지 저장소 설치로 전환           |
| `apt update`에서 `NO_PUBKEY`    | 서명 키 다운로드 실패, 키 파일과 fingerprint 재확인             |
| 구독인데 종량제 과금            | `ANTHROPIC_API_KEY` 설정 여부 확인 후 `unset`, `/status` 재확인 |
| 검색이 동작하지 않음            | 포함된 ripgrep 문제, 공식 troubleshooting의 검색 항목 확인      |
| 컨텍스트 부족·응답 품질 저하    | `/context`로 사용량 확인, `/compact` 또는 `/clear`              |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 설치·인증·권한 검증 근거 노트
- Advanced setup: [code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup) — ★★★☆☆
- Authentication: [code.claude.com/docs/en/authentication](https://code.claude.com/docs/en/authentication) — ★★★☆☆
- Permissions: [code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions) — ★★★☆☆
- Permission modes: [code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes) — ★★★☆☆
- Headless: [code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless) — ★★★☆☆
- CLI reference: [code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference) — ★★★☆☆
- Commands: [code.claude.com/docs/en/commands](https://code.claude.com/docs/en/commands) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-14

**마지막 업데이트**: 2026-10-15

© 2026 siasia86. Licensed under CC BY 4.0.
