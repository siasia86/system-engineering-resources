# Codex CLI 설치 및 사용 가이드
<!-- reference: _reference/codex_cli_official_notes.md -->

Codex CLI는 OpenAI의 코딩 에이전트(Coding Agent)로, 터미널에서 저장소를 탐색하고 파일을 수정하며 명령어와 테스트를 실행합니다. 대화형 작업은 `codex`, CI와 스크립트 작업은 `codex exec`를 사용합니다.

기준일은 2026-09-03이며, 최신 공식 GitHub 릴리스는 `rust-v0.153.0`입니다.

## 목차

| 섹션                                                                                                                               |
|------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 인증](#3-인증)                                                                       |
| [4. 기본 사용법](#4-기본-사용법) / [5. 권한과 샌드박스](#5-권한과-샌드박스) / [6. 비대화형 실행](#6-비대화형-실행)                 |
| [7. 설정](#7-설정) / [8. MCP 연동](#8-mcp-연동) / [9. AGENTS.md 지침](#9-agentsmd-지침)                                            |
| [10. 코드 리뷰](#10-코드-리뷰) / [11. 업데이트와 문제 해결](#11-업데이트와-문제-해결) / [12. 운영 체크리스트](#12-운영-체크리스트) |

## 1. 개요

### 지원 환경

| 항목    | 공식 기준                                      |
|---------|------------------------------------------------|
| macOS   | macOS 12 이상                                  |
| Linux   | Ubuntu 20.04 이상 또는 Debian 10 이상          |
| Windows | Windows 11 + WSL2                              |
| Git     | 선택 사항이지만 PR 기능 사용 시 2.23 이상 권장 |
| 메모리  | 최소 4GB, 8GB 이상 권장                        |

Codex는 로컬 작업 디렉토리의 파일과 설치된 개발 도구를 사용합니다. 따라서 실행 전에 Git 작업 트리를 확인하고, 에이전트가 변경할 범위를 명확히 지정하는 것이 안전합니다.

> Codex CLI: 터미널에서 파일 읽기·수정, 명령 실행, 자동화를 수행하는 OpenAI의 로컬 코딩 에이전트입니다. 모델 요청은 인증 방식에 따라 ChatGPT 구독 또는 OpenAI API 과금에 연결됩니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치

### 2-1. Linux/macOS standalone installer

공식 설치 스크립트는 플랫폼에 맞는 실행 파일을 내려받아 설치합니다.

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

설치 후 셸에서 실행 파일을 인식하도록 새 셸을 열거나 `PATH`를 갱신합니다.

```bash
codex --version
command -v codex
codex --help
```

### 2-2. npm 설치

Node.js 환경에서 npm을 사용하려면 확인한 릴리스 버전을 고정하여 설치합니다.

```bash
npm install -g @openai/codex@0.153.0
codex --version
```

최신 버전으로 갱신할 때도 설치 전에 변경 사항과 릴리스 노트를 확인합니다.

```bash
npm install -g @openai/codex@0.153.0
```

### 2-3. Homebrew 설치

macOS에서 Homebrew를 사용하면 다음 명령어로 설치합니다.

```bash
brew install --cask codex
codex --version
```

### 2-4. 설치 검증

```bash
codex --version
codex doctor
```

`codex doctor`는 설치, 설정, 인증, 런타임, Git, 터미널 상태를 진단합니다. 출력에 API key, access token, `auth.json`의 전체 내용이 포함되지 않는지 확인하고, 진단 결과를 외부에 공유하기 전에 민감정보를 검토합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 인증

Codex CLI는 ChatGPT 계정 인증과 API key 인증을 지원합니다. 인증 방식에 따라 사용량 한도, 보존 정책, 조직 정책이 달라질 수 있습니다.

### 3-1. ChatGPT 계정 인증

브라우저 기반 인증을 시작합니다.

```bash
codex login
```

브라우저에서 ChatGPT 계정과 워크스페이스를 선택합니다. 로그인 상태는 다음과 같이 확인합니다.

```bash
codex login status
```

### 3-2. API key 인증

API key를 셸 명령행에 직접 작성하지 않고 표준 입력으로 전달합니다.

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
codex login status
```

자동화에서 1회 실행만 필요하면 저장된 로그인보다 프로세스 범위의 자격증명을 우선 고려합니다.

```bash
CODEX_API_KEY="$OPENAI_API_KEY" codex exec --json "summarize the repository"
```

공개 저장소나 신뢰할 수 없는 빌드 스크립트와 같은 프로세스에 API key를 함께 노출하지 않습니다. CI에서는 저장소 코드가 실행되는 단계와 자격증명을 사용하는 단계를 분리하고, 가능하면 단기 수명 workload identity를 사용합니다.

### 3-3. 로그아웃과 자격증명 저장

```bash
codex logout
```

Codex는 기본적으로 `~/.codex/auth.json` 또는 운영체제의 자격증명 저장소에 로그인 정보를 저장할 수 있습니다. OS 자격증명 저장소를 우선하려면 `~/.codex/config.toml`에 다음을 설정합니다.

```toml
cli_auth_credentials_store = "keyring"
```

`auth.json`은 비밀번호처럼 취급하며 Git에 추가하거나 티켓·채팅·로그에 붙여 넣지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 기본 사용법

### 4-1. 대화형 실행

Git 저장소로 이동한 뒤 `codex`를 실행합니다.

```bash
cd /path/to/repository
codex
```

첫 요청 예시는 다음과 같습니다.

```text
이 저장소의 구조를 요약하고, 먼저 읽어야 할 문서와 테스트 명령어를 알려줘.
```

Codex가 파일을 수정하기 전에 요구사항·대상 파일·검증 방법을 명시합니다.

```text
src/auth.py의 만료 토큰 검증 오류를 수정해줘.
변경 범위는 해당 파일과 관련 테스트로 제한하고, 수정 후 테스트 명령어를 실행해 결과를 요약해줘.
```

### 4-2. 세션 내 주요 명령

| 명령어         | 용도                                |
|----------------|-------------------------------------|
| `/permissions` | 샌드박스·승인 권한 확인 및 변경     |
| `/status`      | 현재 세션과 작업 디렉토리 상태 확인 |
| `/review`      | 변경 사항 코드 리뷰 시작            |
| `/mcp`         | 연결된 MCP 서버와 도구 확인         |
| `/help`        | 사용 가능한 슬래시 명령어 확인      |
| `Ctrl+C`       | 현재 작업 중단                      |

### 4-3. 작업 디렉토리 지정

현재 디렉토리와 다른 저장소에서 실행할 때는 `--cd`를 사용합니다.

```bash
codex --cd /path/to/repository
```

작업 시작 전 변경 사항을 확인합니다.

```bash
git status --short
git diff --stat
```

[⬆ 목차로 돌아가기](#목차)

## 5. 권한과 샌드박스

Codex의 **샌드박스(Sandbox)** 는 에이전트가 명령어를 실행할 수 있는 파일 시스템·네트워크 범위를 제한하는 실행 격리입니다.

기본적으로 네트워크 접근은 비활성화되고, 자동화용 `codex exec`는 읽기 전용 샌드박스에서 시작합니다. 작업 목적에 필요한 최소 권한만 부여합니다.

### 권한 모드

| 모드                 | 용도                      | 권장 범위                   |
|----------------------|---------------------------|-----------------------------|
| `read-only`          | 분석·계획·리뷰            | 읽기만 필요한 작업          |
| `workspace-write`    | 저장소 수정·테스트        | 일반적인 개발 작업          |
| `danger-full-access` | 격리 환경의 광범위한 작업 | 통제된 임시 환경에서만 사용 |

대화형 개발의 일반적인 권장 조합입니다.

```bash
codex --sandbox workspace-write --ask-for-approval on-request
```

자동화에서 파일 수정이 필요한 경우에도 같은 원칙을 적용합니다.

```bash
codex exec --sandbox workspace-write "implement the requested change and run the focused tests"
```

`--ask-for-approval never`와 `danger-full-access`를 함께 사용하면 승인 없이 넓은 범위의 작업이 가능해집니다. 운영 저장소, 개인 홈 디렉토리, 인터넷 연결이 필요한 환경에서는 사용하지 않습니다.

### 네트워크 접근

`workspace-write`에서 명령어 네트워크 접근은 기본적으로 꺼져 있습니다. 패키지 설치나 외부 API 호출이 필요한 경우에도 전체 네트워크를 열기보다 필요한 호스트만 허용합니다.

```toml
[sandbox_workspace_write]
network_access = true

[features.network_proxy]
enabled = true
domains = { "registry.npmjs.org" = "allow" }
```

네트워크를 열면 저장소의 스크립트가 외부로 데이터를 전송할 수 있으므로, 실행 전에 저장소 코드와 의존성 설치 스크립트를 검토합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 비대화형 실행

`codex exec`는 CI, 배치 작업, 파이프라인에서 사용합니다. 기본 출력은 진행 정보를 표준 오류로 보내고 최종 답변을 표준 출력으로 보냅니다.

### 6-1. 기본 실행

```bash
codex exec "summarize the repository structure and list the top five risky areas"
```

파일 수정이 필요하면 샌드박스를 명시합니다.

```bash
codex exec \
  --sandbox workspace-write \
  "find the failing test, implement the minimal fix, and run the focused test"
```

세션 파일을 보존하지 않으려면 `--ephemeral`을 사용합니다.

```bash
codex exec --ephemeral "inspect the repository and suggest next steps"
```

### 6-2. JSON Lines 출력

JSONL(JSON Lines) 은 한 줄마다 하나의 JSON 객체를 출력하는 형식입니다.

> JSONL(JSON Lines): 스트림 처리에 적합하도록 각 줄을 독립적인 JSON 객체로 구성하는 형식입니다. 전체 문서가 하나의 JSON 배열일 필요가 없어 CI 로그와 파이프라인에서 처리하기 쉽습니다.

```bash
codex exec --json "summarize the repository structure" | jq
```

최종 메시지만 파일에 저장하려면 `--output-last-message`를 사용합니다.

```bash
codex exec \
  --output-last-message ./codex-result.md \
  "review the latest changes and summarize risks"
```

### 6-3. 표준 입력과 구조화된 출력

```bash
cat errors.log \
  | codex exec "group these errors by root cause and return a markdown table" \
  > error-summary.md
```

JSON Schema가 필요한 자동화에서는 스키마 파일을 별도로 관리합니다.

```json
{
  "type": "object",
  "properties": {
    "risk": { "type": "string" },
    "recommendations": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["risk", "recommendations"],
  "additionalProperties": false
}
```

```bash
codex exec \
  --output-schema ./schema.json \
  --output-last-message ./result.json \
  "analyze the deployment risk and return structured recommendations"
```

### 6-4. 세션 이어가기

```bash
codex exec "review the change for race conditions"
codex exec resume --last "fix the race conditions you found"
```

특정 세션 ID를 알고 있으면 `codex exec resume <SESSION_ID>`를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 설정

Codex의 사용자 설정은 `~/.codex/config.toml`, 저장소별 설정은 신뢰된 저장소의 `.codex/config.toml`에 둡니다.

### 설정 우선순위

1. CLI 플래그와 `--config` 오버라이드.
2. 저장소의 `.codex/config.toml`.
3. 선택한 프로파일 설정.
4. 사용자 설정 `~/.codex/config.toml`.
5. 시스템 설정 `/etc/codex/config.toml`.
6. 기본값.

기본 모델과 권한을 설정하는 예시입니다.

```toml
model = "gpt-5.6"
model_reasoning_effort = "high"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"
```

`web_search`는 `cached`, `indexed`, `live`, `disabled` 값을 사용할 수 있습니다. 최신 자료가 꼭 필요한 작업만 `live`를 사용하고, 웹 결과는 신뢰할 수 없는 입력으로 취급합니다.

일회성 설정은 `-c`로 지정할 수 있습니다.

```bash
codex -c 'model_reasoning_effort="high"' "analyze this module"
```

[⬆ 목차로 돌아가기](#목차)

## 8. MCP 연동

MCP(Model Context Protocol) 는 모델이 외부 도구와 컨텍스트에 연결되는 표준 프로토콜입니다.

> MCP(Model Context Protocol): 에이전트가 문서 검색, 개발 도구, 사내 시스템과 같은 외부 기능을 정해진 인터페이스로 호출하도록 연결하는 프로토콜입니다. 연결한 서버의 도구 권한과 자격증명은 별도로 관리해야 합니다.

### MCP 서버 추가

로컬 STDIO 서버를 추가하는 예시입니다.

```bash
codex mcp add local-tools -- ./tools/mcp-server
codex mcp list
```

환경 변수가 필요한 서버는 값을 명령어에 직접 쓰지 않습니다.

```bash
codex mcp add internal-docs \
  --env DOCS_TOKEN \
  -- python3 ./tools/internal_docs_mcp.py
```

원격 Streamable HTTP 서버는 공식 문서의 전송 방식을 사용합니다.

```bash
codex mcp add internal-http --url https://mcp.example.com
codex mcp list
```

OAuth를 지원하는 서버는 다음과 같이 인증합니다.

```bash
codex mcp login internal-http
```

MCP 서버는 에이전트에 추가 도구와 데이터 접근 권한을 부여합니다. 신뢰할 수 있는 서버만 연결하고, 도구별 승인 정책·토큰 범위·네트워크 허용 목록을 검토합니다.

[⬆ 목차로 돌아가기](#목차)

## 9. AGENTS.md 지침

Codex는 실행 전에 `AGENTS.md`와 `AGENTS.override.md`를 찾아 프로젝트 지침으로 읽습니다. 전역 지침은 `~/.codex/AGENTS.md`, 저장소 지침은 Git 루트와 하위 디렉토리에 둘 수 있습니다.

### 전역 지침 예시

```bash
mkdir -p ~/.codex
cat > ~/.codex/AGENTS.md <<'EOF'
# Global instructions

- Run focused tests after code changes.
- Do not modify generated files directly.
- Explain risky or destructive operations before running them.
EOF
```

### 저장소 지침 예시

```markdown
# AGENTS.md

## Repository expectations

- Run `make test` after modifying application code.
- Keep changes limited to the requested scope.
- Do not commit credentials or generated build output.
```

지침 파일은 상위 디렉토리에서 하위 디렉토리 순서로 결합되며, 가까운 디렉토리의 지침이 더 구체적인 기준으로 적용됩니다. 내용이 길면 `project_doc_max_bytes` 제한에 걸릴 수 있으므로 핵심 규칙을 짧게 유지합니다.

지침이 실제로 로드되는지 확인합니다.

```bash
codex --ask-for-approval never "summarize the active project instructions"
```

[⬆ 목차로 돌아가기](#목차)

## 10. 코드 리뷰

Codex는 작업 트리를 변경하지 않고 변경 사항의 위험과 개선점을 검토할 수 있습니다.

대화형 세션에서 다음을 입력합니다.

```text
/review
```

검토 범위는 다음과 같습니다.

| 범위                | 설명                                  |
|---------------------|---------------------------------------|
| Base branch         | 기준 브랜치와 현재 브랜치의 차이 검토 |
| Uncommitted changes | 스테이지·언스테이지·미추적 변경 검토  |
| Commit              | 지정 커밋의 변경 세트 검토            |
| Custom instructions | 사용자가 지정한 기준으로 검토         |

CLI에서 직접 실행할 수도 있습니다.

```bash
codex review --uncommitted
codex review --base main
codex review --commit HEAD
```

리뷰 결과를 확인한 뒤 수정이 필요하면 별도 요청으로 범위를 제한합니다.

```text
방금 리뷰의 High·Medium 위험만 수정하고, 각 수정 후 관련 테스트를 실행해줘.
```

리뷰 전후로 diff를 보존합니다.

```bash
git diff --check
git diff --stat
git status --short
```

[⬆ 목차로 돌아가기](#목차)

## 11. 업데이트와 문제 해결

### 업데이트

standalone installer와 npm 설치는 공식 최신 설치 경로를 다시 실행하여 업데이트할 수 있습니다.

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

```bash
npm install -g @openai/codex@0.153.0
```

업데이트 전 현재 버전과 설정 파일을 백업합니다.

```bash
codex --version
cp -a ~/.codex/config.toml ~/.codex/config.toml.backup.$(date +%Y%m%d_%H%M%S)
```

### 문제 해결 순서

1. `codex --version`으로 실행 파일과 버전을 확인합니다.
2. `command -v codex`로 PATH가 올바른지 확인합니다.
3. `codex login status`로 인증 상태를 확인합니다.
4. `codex doctor`로 설치·설정·런타임을 진단합니다.
5. Git 저장소 내부에서 실행하는지 확인합니다.
6. `codex --help`와 공식 릴리스 노트로 옵션 변경을 확인합니다.
7. 필요하면 새 셸에서 다시 실행합니다.

### 자주 발생하는 문제

| 증상                       | 점검 및 조치                                          |
|----------------------------|-------------------------------------------------------|
| `codex: command not found` | 설치 경로와 `PATH`, 새 셸 시작 여부 확인              |
| 로그인 실패                | `codex login` 재실행, 브라우저 계정·워크스페이스 확인 |
| 인증은 됐지만 실행 실패    | `codex login status`, API 사용량·조직 정책 확인       |
| 저장소를 찾지 못함         | Git 루트에서 실행, 필요 시 안전성을 확인 후 옵션 검토 |
| 파일 수정이 거부됨         | 샌드박스와 승인 정책을 `workspace-write`로 확인       |
| MCP 서버 초기화 실패       | `codex mcp list`, 명령어·환경 변수·서버 로그 확인     |

인증 파일이나 API key를 삭제·재발급하기 전에 먼저 상태와 로그를 확인합니다. 자격증명 유출이 의심되면 해당 key를 즉시 폐기하고 새 key를 발급합니다.

[⬆ 목차로 돌아가기](#목차)

## 12. 운영 체크리스트

### 설치 직후

- [ ] `codex --version`으로 버전 확인.
- [ ] `codex doctor` 결과 확인.
- [ ] `codex login status`로 올바른 계정 확인.
- [ ] `~/.codex/auth.json`과 API key가 Git·로그에 노출되지 않는지 확인.
- [ ] `~/.codex/config.toml`의 샌드박스·승인·네트워크 기본값 확인.

### 작업 전

- [ ] `git status --short`로 기존 변경 사항 확인.
- [ ] 요청 범위, 대상 파일, 검증 명령어를 Codex에 명시.
- [ ] `workspace-write`와 `on-request` 등 최소 권한 적용.
- [ ] 외부 네트워크·MCP가 필요한지 판단.

### 작업 후

- [ ] `git diff --check`와 `git diff --stat` 실행.
- [ ] 변경된 파일과 테스트 결과 확인.
- [ ] 민감정보·불필요한 파일 변경 여부 확인.
- [ ] 필요하면 `codex review --uncommitted`로 별도 리뷰 실행.
- [ ] 커밋·배포 전 사람이 최종 검토.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- OpenAI Codex CLI: [developers.openai.com/codex/cli](https://developers.openai.com/codex/cli/) — ★★★☆☆
- Codex CLI GitHub: [github.com/openai/codex](https://github.com/openai/codex) — ★★★☆☆
- Codex 인증: [learn.chatgpt.com/docs/auth](https://learn.chatgpt.com/docs/auth) — ★★★☆☆
- Codex 명령어: [learn.chatgpt.com/docs/developer-commands](https://learn.chatgpt.com/docs/developer-commands) — ★★★☆☆
- 비대화형 실행: [learn.chatgpt.com/docs/non-interactive-mode](https://learn.chatgpt.com/docs/non-interactive-mode) — ★★★☆☆
- 보안·승인·샌드박스: [learn.chatgpt.com/docs/agent-approvals-security](https://learn.chatgpt.com/docs/agent-approvals-security) — ★★★☆☆
- 설정: [learn.chatgpt.com/docs/config-file/config-basic](https://learn.chatgpt.com/docs/config-file/config-basic) — ★★★☆☆
- MCP: [learn.chatgpt.com/docs/extend/mcp](https://learn.chatgpt.com/docs/extend/mcp) — ★★★☆☆
- AGENTS.md: [learn.chatgpt.com/docs/agent-configuration/agents-md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-03

**마지막 업데이트**: 2026-09-03

© 2026 siasia86. Licensed under CC BY 4.0.
