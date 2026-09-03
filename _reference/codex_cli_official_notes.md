---
name: codex-cli-official-notes
last_checked: 2026-09-03
sources:
  - https://developers.openai.com/codex/cli.md
  - https://learn.chatgpt.com/docs/auth.md
  - https://learn.chatgpt.com/docs/developer-commands.md
  - https://learn.chatgpt.com/docs/non-interactive-mode.md
  - https://learn.chatgpt.com/docs/config-file/config-basic.md
  - https://learn.chatgpt.com/docs/agent-approvals-security.md
  - https://learn.chatgpt.com/docs/extend/mcp.md
  - https://learn.chatgpt.com/docs/agent-configuration/agents-md.md
  - https://github.com/openai/codex/releases/latest
---

## 1. 버전 상태

- 최신 GitHub 릴리스 확인일: 2026-09-03.
- 최신 릴리스 태그: `rust-v0.153.0`.
- 공식 설치 경로: standalone installer, npm, Homebrew.
- Linux 공식 지원 범위: Ubuntu 20.04 이상 또는 Debian 10 이상.
- Windows 사용 시 공식 소스는 Windows 11 + WSL2 경로를 안내합니다.

## 2. 설치 및 인증

- macOS/Linux standalone installer:
  `curl -fsSL https://chatgpt.com/codex/install.sh | sh`
- npm 설치:
  `npm install -g @openai/codex`
- Homebrew 설치:
  `brew install --cask codex`
- ChatGPT 인증: `codex login` 후 브라우저 인증.
- API key 인증: `printenv OPENAI_API_KEY | codex login --with-api-key`.
- 인증 상태: `codex login status`.
- 인증 해제: `codex logout`.
- 자동화에서는 API key를 명령행 인자로 넣지 않고, 제한된 프로세스 범위의 환경 변수 또는 단기 수명 workload identity를 사용합니다.

## 3. 사용 및 자동화

- 인자 없이 `codex`를 실행하면 대화형 터미널 UI가 시작됩니다.
- `codex exec`는 CI와 스크립트용 비대화형 실행 모드입니다.
- 기본 `codex exec` 샌드박스는 읽기 전용입니다.
- 파일 수정이 필요하면 `--sandbox workspace-write`를 명시합니다.
- `--json`은 JSON Lines 출력을 사용합니다.
- `--ephemeral`은 세션 rollout 파일의 디스크 저장을 방지합니다.
- `codex exec resume --last`로 현재 작업 디렉토리의 마지막 세션을 이어갈 수 있습니다.
- Codex 실행에는 기본적으로 Git 저장소가 필요하며, 안전성을 확인한 경우에만 `--skip-git-repo-check`를 사용합니다.

## 4. 보안 및 권한

- 기본적으로 네트워크 접근은 비활성화됩니다.
- `workspace-write`는 작업 디렉토리 중심의 쓰기 권한을 제공하며, 승인 정책과 함께 사용합니다.
- 일반 권장 조합은 `--sandbox workspace-write --ask-for-approval on-request`입니다.
- `danger-full-access`와 `--ask-for-approval never`는 통제된 환경에서만 사용합니다.
- `~/.codex/auth.json`은 자격증명 저장 파일이 될 수 있으므로 커밋·공유하지 않습니다.
- `cli_auth_credentials_store = "keyring"`으로 OS 자격증명 저장소 사용을 설정할 수 있습니다.

## 5. 설정 및 확장

- 사용자 설정: `~/.codex/config.toml`.
- 프로젝트 설정: 신뢰된 저장소의 `.codex/config.toml`.
- CLI 플래그와 `--config`가 가장 높은 우선순위를 가집니다.
- 기본 모델, 승인 정책, 샌드박스, MCP 서버, reasoning effort를 설정할 수 있습니다.
- MCP 서버는 `codex mcp add`, `codex mcp list`, `codex mcp login`으로 관리합니다.
- Codex는 전역·저장소·하위 디렉토리의 `AGENTS.md` 지침을 계층적으로 읽습니다.

## 6. 공식 자료 검증 범위

- 설치·업데이트 명령은 OpenAI Codex CLI 공식 문서와 공식 GitHub 저장소 README를 대조했습니다.
- 인증·보안·자동화·MCP·`AGENTS.md` 항목은 OpenAI의 ChatGPT/Codex 공식 문서에서 확인했습니다.
- 릴리스 버전은 GitHub API의 `openai/codex` 최신 릴리스 응답으로 확인했습니다.
