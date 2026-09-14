---
name: codex-cli-official-notes
description: OpenAI Codex CLI의 Linux 설치·인증·권한·자동화 공식 참조 노트
tags:
  - codex
  - cli
  - linux
  - openai
last_checked: 2026-09-14
sources:
  - https://developers.openai.com/codex/cli.md
  - https://developers.openai.com/codex/auth.md
  - https://developers.openai.com/codex/sandboxing.md
  - https://developers.openai.com/codex/non-interactive-mode.md
  - https://developers.openai.com/codex/config-file/config-basic.md
  - https://developers.openai.com/codex/config-file/config-reference.md
  - https://developers.openai.com/codex/agent-configuration/agents-md.md
  - https://developers.openai.com/codex/developer-commands.md
  - https://github.com/openai/codex/releases/latest
---

## 1. 버전 상태

- 최신 OpenAI Codex GitHub 릴리스 확인일: 2026-09-14.
- 최신 릴리스 태그: `rust-v0.154.0`.
- 공식 설치 경로: macOS/Linux standalone installer, npm, Homebrew.
- Linux 샌드박스 의존성: `bubblewrap` 패키지의 `bwrap` 실행 파일.
- 현재 문서는 공식 문서의 Markdown 원문과 GitHub 최신 릴리스를 대조했습니다.

## 2. Linux 설치 및 업데이트

- standalone installer:
  `curl -fsSL https://chatgpt.com/codex/install.sh | sh`
- npm 설치:
  `npm install -g @openai/codex`
- Homebrew 설치:
  `brew install --cask codex`
- Homebrew 업데이트:
  `brew upgrade --cask codex`
- 설치 확인:
  `codex --version`

공식 설치 명령은 원격 스크립트를 표준 입력으로 실행하므로 운영 환경에서는 다운로드한 스크립트를 별도 검토한 후 실행하거나, 조직 패키지 정책에 맞는 npm·Homebrew 경로를 사용합니다.

## 3. 인증

- ChatGPT 인증: `codex login` 후 브라우저 인증.
- API key 인증: `printenv OPENAI_API_KEY | codex login --with-api-key`.
- 인증 상태: `codex login status`.
- 저장된 인증정보 제거: `codex logout`.
- 엔터프라이즈 access token: `printenv CODEX_ACCESS_TOKEN | codex login --with-access-token`.

API key와 `~/.codex/auth.json`은 자격증명으로 취급하며 commit·채팅·로그에 기록하지 않습니다. CI/CD에서는 short-lived workload identity 또는 실행 순간에만 주입되는 제한된 환경변수를 우선합니다.

## 4. 대화형 CLI

- `codex`: 현재 프로젝트에서 대화형 TUI 시작.
- `/model`: 모델과 reasoning effort 선택.
- `/status`: 모델, 승인 정책, writable roots, token usage 확인.
- `/permissions`: 활성 권한 프로필 변경.
- `/diff`: Git 변경 확인.
- `/review`: working tree·commit·base branch 검토.
- `/compact`: 대화 이력을 요약해 context token 절약.
- `/resume`: 저장된 세션 재개.
- `codex resume --last`: 현재 작업 디렉토리의 최근 세션 재개.
- `codex fork --last`: 최근 세션을 새 대화로 분기.
- `/exit` 또는 `/quit`: CLI 종료.

## 5. 샌드박스 및 승인

- `read-only`: 파일을 읽을 수 있으나 수정과 승인 없는 명령 실행을 제한.
- `workspace-write`: 작업 디렉토리 안에서 수정과 일반 명령을 허용하는 기본적인 로컬 작업 모드.
- `danger-full-access`: 파일시스템·네트워크 경계를 제거하므로 통제된 환경에서만 사용.
- 일반 권장 조합: `--sandbox workspace-write --ask-for-approval on-request`.
- `--ask-for-approval never`와 `danger-full-access`의 조합은 격리된 runner·container 등에서만 사용.
- Linux/WSL2에서 샌드박스 안정성을 위해 `bubblewrap` 설치:
  `sudo apt install bubblewrap` 또는 `sudo dnf install bubblewrap`.

## 6. 비대화형 실행 및 CI

- 기본 실행: `codex exec "<task>"`.
- 기본 `codex exec` 샌드박스: read-only.
- 파일 수정: `codex exec --sandbox workspace-write "<task>"`.
- JSON Lines 출력: `codex exec --json "<task>"`.
- 세션 파일 미저장: `codex exec --ephemeral "<task>"`.
- 최근 세션 재개: `codex exec resume --last "<task>"`.
- Git 저장소 확인을 건너뛰는 `--skip-git-repo-check`는 안전성을 직접 확인한 경우에만 사용.
- 기존 `--full-auto`는 deprecated compatibility flag이므로 새 자동화에는 명시적 sandbox·approval 옵션 사용.
- CI에서는 저장소 코드가 credential을 읽지 못하도록 `OPENAI_API_KEY`를 job 전체 환경변수로 두지 않으며, 가능하면 공식 Codex GitHub Action을 사용.

## 7. 설정 및 지침 파일

- 사용자 설정: `~/.codex/config.toml`.
- 신뢰된 프로젝트 설정: `.codex/config.toml`.
- 설정 우선순위: CLI flag·`--config` → 프로젝트 설정 → profile → 사용자 설정 → system 설정 → 기본값.
- 주요 키: `model`, `approval_policy`, `sandbox_mode`, `sandbox_workspace_write.writable_roots`.
- 자동 compaction threshold: `model_auto_compact_token_limit`.
- 프로젝트 지침: 전역 `~/.codex/AGENTS.md`와 Git root부터 현재 디렉토리까지의 `AGENTS.md` 계층.
- `AGENTS.md` 결합 기본 상한: `project_doc_max_bytes` 32 KiB.
- MCP 설정: `codex mcp add`, `codex mcp list`, `codex mcp login`.

## 8. 공식 자료

- Codex CLI: https://developers.openai.com/codex/cli.md
- Authentication: https://developers.openai.com/codex/auth.md
- Sandbox: https://developers.openai.com/codex/sandboxing.md
- Non-interactive mode: https://developers.openai.com/codex/non-interactive-mode.md
- Configuration basics: https://developers.openai.com/codex/config-file/config-basic.md
- Configuration reference: https://developers.openai.com/codex/config-file/config-reference.md
- Developer commands: https://developers.openai.com/codex/developer-commands.md
- OpenAI Codex releases: https://github.com/openai/codex/releases/latest
