---
name: codex-cli-official-notes
description: OpenAI Codex CLI의 Linux 설치·인증·권한·자동화·Skills 설정 공식 참조 노트
tags:
  - codex
  - cli
  - linux
  - openai
last_checked: 2026-10-03
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
  - https://learn.chatgpt.com/docs/config-file/config-basic
  - https://learn.chatgpt.com/docs/config-file/config-advanced
  - https://learn.chatgpt.com/docs/config-file/config-reference
  - https://learn.chatgpt.com/docs/agent-configuration/agents-md
  - https://learn.chatgpt.com/docs/agent-approvals-security
  - https://learn.chatgpt.com/docs/build-skills
  - https://learn.chatgpt.com/docs/extend/mcp
  - https://developers.openai.com/learn/docs-mcp
  - https://developers.openai.com/plugins/build/skills
  - https://developers.openai.com/plugins/build/plugins
  - https://github.com/openai/skills
  - https://github.com/openai/plugins
  - https://github.com/vercel-labs/skills
---

# Codex CLI 공식 참조 노트

## 1. 버전 상태

- 2026-09-14 당시 확인한 OpenAI Codex GitHub 릴리스 태그: `rust-v0.154.0`.
- 2026-10-01 설정·지침·MCP·Skills 문서와 CLI 인수 문법을 재검증했습니다. 로컬 검증 버전은 `codex-cli 0.159.3`이며, 이 버전이 현재 GitHub 최신 릴리스라는 뜻은 아닙니다.
- 2026-10-03 Skills 설정·plugin 배포 안내를 재확인하고 8절에 정리했습니다. 로컬 `codex-cli 0.160.0`에서 `plugin`·`plugin add`·`plugin marketplace add`의 도움말만 확인했습니다. 실제 skill·plugin 설치와 암묵적 호출은 검증하지 않았으며, 그 밖의 CLI 항목은 기존 확인일을 유지합니다.
- 공식 설치 경로: macOS/Linux standalone installer, npm, Homebrew.
- Linux 샌드박스 의존성: `bubblewrap` 패키지의 `bwrap` 실행 파일.
- 설치·인증·릴리스 항목은 2026-09-14 검증 기록을 유지합니다. 2026-10-01 재검증은 설정 관련 항목과 CLI 문법에 한정하며, 실제 모델 호출·OAuth 로그인·배포는 실행하지 않았습니다.

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

- `read-only`: 파일 읽기와 샌드박스 안의 명령 실행은 허용하고 파일 수정을 제한. 승인 필요 여부는 별도 승인 정책에 따라 결정.
- `workspace-write`: 작업 디렉토리 안에서 수정과 일반 명령을 허용하는 기본적인 로컬 작업 모드.
- `danger-full-access`: 파일시스템·네트워크 경계를 제거하므로 통제된 환경에서만 사용.
- 일반 권장 조합: `--sandbox workspace-write --ask-for-approval on-request`.
- `approval_policy = "never"`는 승인 프롬프트를 생략하며 샌드박스를 해제하지 않음. 추가 권한이 필요한 작업은 거부될 수 있음.
- `approvals_reviewer`는 승인 요청의 검토 주체이며, `user`와 `auto_review`를 구분. 자동 검토는 샌드박스 안의 일반 작업마다 실행되지 않음.
- `--ask-for-approval never`와 `danger-full-access`의 조합은 격리된 runner·container 등에서만 사용.
- Linux/WSL2에서 샌드박스 안정성을 위해 `bubblewrap` 설치:
  `sudo apt install bubblewrap` 또는 `sudo dnf install bubblewrap`.

## 6. 비대화형 실행 및 CI

- 기본 실행: `codex exec "<task>"`.
- 기본 `codex exec` 샌드박스: read-only.
- 파일 수정: `codex exec --sandbox workspace-write "<task>"`.
- 사용자 입력 없는 CI 예시: `codex exec --sandbox read-only -c approval_policy=never "<task>"`.
- 로컬 `0.159.3`에서는 `codex exec --ask-for-approval ...`가 인수 오류를 발생시킴. `exec` 예제에서는 `-c approval_policy=...`를 사용하며, `--help`로 인수 파싱만 확인했음.
- JSON Lines 출력: `codex exec --json "<task>"`.
- 세션 파일 미저장: `codex exec --ephemeral "<task>"`.
- 최근 세션 재개: `codex exec resume --last "<task>"`.
- Git 저장소 확인을 건너뛰는 `--skip-git-repo-check`는 안전성을 직접 확인한 경우에만 사용.
- 기존 `--full-auto`는 deprecated compatibility flag이므로 새 자동화에는 명시적 sandbox·approval 옵션 사용.
- CI에서는 저장소 코드가 credential을 읽지 못하도록 `OPENAI_API_KEY`를 job 전체 환경변수로 두지 않으며, 가능하면 공식 Codex GitHub Action을 사용.

## 7. 설정 및 지침 파일

- 사용자 설정: `$CODEX_HOME/config.toml`. 기본 `CODEX_HOME`은 `~/.codex`이며 사용자는 명령을 실행하는 OS 계정.
- 신뢰된 프로젝트 설정: 프로젝트 루트부터 현재 작업 디렉토리까지의 `.codex/config.toml`. 같은 키는 현재 디렉토리에 가까운 설정이 우선.
- 설정 profile: `$CODEX_HOME/<name>.config.toml`을 `--profile <name>`으로 선택. 권한 profile 선택과는 별도.
- 기본값 우선순위: CLI flag·`--config` → 프로젝트 설정 → 선택한 profile → 사용자 설정 → 전달된 클라우드 관리 기본값 → system 설정 → 내장 기본값. 조직의 강제 요구사항은 별도 적용.
- 프로젝트 설정에서는 `model_provider`, `model_providers`, `notify`, `profile`, `otel` 등 일부 키를 덮어쓸 수 없음. 전체 목록은 [공식 설정 레퍼런스](https://learn.chatgpt.com/docs/config-file/config-reference) 확인.
- 주요 키: `model`, `approval_policy`, `sandbox_mode`, `sandbox_workspace_write.writable_roots`.
- 자동 compaction threshold: `model_auto_compact_token_limit`. 미지정 시 모델 기본값 사용. `/status`가 모든 설정 키를 표시한다고 가정하지 않음.
- 사용자 지침: `$CODEX_HOME`의 `AGENTS.override.md`를 우선 탐색하고 없으면 `AGENTS.md` 탐색.
- 프로젝트 지침: 프로젝트 루트(보통 Git root)부터 현재 디렉토리까지 탐색. 루트를 찾지 못하면 현재 디렉토리만 확인.
- 각 디렉토리에서 `AGENTS.override.md` → `AGENTS.md` → 설정한 fallback 이름 순으로 최대 한 파일 선택. 빈 파일 제외. 상위 지침 뒤에 하위 지침 결합.
- `project_doc_max_bytes`는 지침 읽기 제한. 2026-10-01 [AGENTS.md 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)는 결합 크기 제한과 기본값 32 KiB를, [고급 설정 안내](https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery)는 파일별 제한을 설명하여 공식 문서 간 표현이 다름. 프로젝트 지침 합계를 32 KiB 이내로 유지하도록 권장하며, 더 큰 지침은 설치 버전의 탐색·절단 동작을 별도 검증.
- Skills: 시스템 Skills는 기본 제공. 추가 Skills는 별도 설치·배치. 시작 시 이름·설명 등 메타데이터를 읽고, 선택한 Skill의 본문을 로드. 로컬 경로는 repository `.agents/skills/`, 사용자 `$HOME/.agents/skills/`, admin `/etc/codex/skills/`.
- MCP: 로컬 프로세스는 STDIO, URL 서버는 Streamable HTTP. `codex mcp add`는 사용자 설정에 등록. 프로젝트 전용 설정은 신뢰된 프로젝트의 `.codex/config.toml`에 배치.
- Docs MCP 등록: `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`. 공식 문서 검색·읽기용이며 OpenAI API를 대신 호출하지 않음.
- MCP 상태 확인: `codex mcp list`, 새 TUI 세션의 `/mcp`. `codex mcp login <server-name>`은 OAuth를 지원하고 로그인이 필요한 서버에 사용. Docs MCP에는 OAuth 로그인 불필요.
- 같은 Codex 호스트의 CLI·IDE 확장·데스크톱 앱은 MCP 설정을 공유. ChatGPT 웹은 로컬 Codex 설정을 읽지 않음.

설정·지침 탐색은 [설정 기본](https://learn.chatgpt.com/docs/config-file/config-basic), [고급 설정](https://learn.chatgpt.com/docs/config-file/config-advanced), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)를 기준으로 확인했습니다. 승인·Skills·MCP의 적용 범위는 [승인 정책](https://learn.chatgpt.com/docs/agent-approvals-security), [Skills](https://learn.chatgpt.com/docs/build-skills), [MCP](https://learn.chatgpt.com/docs/extend/mcp), [Docs MCP](https://developers.openai.com/learn/docs-mcp)를 기준으로 확인했습니다.

## 8. Skills 설정과 배포

- 작성 형식: skill 폴더의 `SKILL.md`에 필수 `name`·`description`과 작업 절차를 작성합니다. 상세 배경은 `references/`, 템플릿은 `assets/`, 필요한 실행 코드는 `scripts/`에 둡니다.
- 호출: Codex CLI·IDE에서는 `/skills`로 확인하거나 `$skill-name`으로 명시적으로 선택합니다. 암묵적 선택은 `description`에 의존하므로 적용할 요청과 제외할 요청을 구체적으로 작성합니다.
- 로컬 위치: repository `.agents/skills/`, 사용자 `$HOME/.agents/skills/`, admin `/etc/codex/skills/`, Codex 기본 제공 system skill. repository는 현재 디렉토리부터 Git root까지 탐색합니다. 동일한 `name`은 자동 병합하지 않습니다.
- 경로 차이: 공식 Build skills 문서의 사용자 위치는 `~/.agents/skills/`이지만 Vercel skills CLI README의 Codex global 목적지는 `~/.codex/skills/`입니다. 도구의 설치 목적지와 Codex의 실제 발견 결과를 각각 확인합니다.
- 선택 메타데이터: `agents/openai.yaml`에서 표시 이름·기본 요청·도구 의존성을 설정합니다. `policy.allow_implicit_invocation: false`는 암묵적 선택을 막으며 명시적 호출은 유지합니다.
- 로컬 비활성화: 공식 Build skills 예제는 `~/.codex/config.toml`의 `[[skills.config]]`에 skill의 `SKILL.md` 절대 경로와 `enabled = false`를 지정합니다. 설정 파일 변경 후 Codex를 재시작합니다.
- 검증: 명시적 요청, 간접 요청, 입력 부족, 범위 밖 요청, 도구 실패를 각각 확인합니다. 목록 표시만 확인한 결과를 작업 수행 검증으로 보고하지 않습니다.
- 배포: 로컬 작성·저장소 작업에는 skill 폴더를 사용하고, 다른 사람에게 skill과 MCP 연결을 함께 제공할 때는 plugin으로 패키징합니다. 현재 공식 패키징 문서는 root `plugin.json`을 안내하고 `.codex-plugin/plugin.json`은 compatibility fallback으로 지원합니다.
- 카탈로그 상태: 2026-10-03 `openai/skills` README는 deprecated를 표시하고 `openai/plugins`를 후속 예제로 연결합니다. Build skills 문서에는 과거 `openai/skills` 링크가 남아 있으므로 두 자료의 안내 시점을 구분합니다.

1차로 [Build skills](https://learn.chatgpt.com/docs/build-skills)와 GitHub README를 대조했습니다. 2차로 [skill 작성·검증 안내](https://developers.openai.com/plugins/build/skills), [plugin 패키징 안내](https://developers.openai.com/plugins/build/plugins), 로컬 CLI 도움말을 대조했습니다. 사용자·repository skill 검색과 암묵적 호출의 실제 실행 결과는 미검증입니다.

## 9. 공식 자료

- Codex CLI: https://developers.openai.com/codex/cli.md
- Authentication: https://developers.openai.com/codex/auth.md
- Sandbox: https://developers.openai.com/codex/sandboxing.md
- Non-interactive mode: https://developers.openai.com/codex/non-interactive-mode.md
- Configuration basics: https://developers.openai.com/codex/config-file/config-basic.md
- Configuration reference: https://developers.openai.com/codex/config-file/config-reference.md
- Developer commands: https://developers.openai.com/codex/developer-commands.md
- OpenAI Codex releases: https://github.com/openai/codex/releases/latest
- Build skills: https://learn.chatgpt.com/docs/build-skills
- Skill authoring: https://developers.openai.com/plugins/build/skills
- Plugin packaging: https://developers.openai.com/plugins/build/plugins
- Current plugin examples: https://github.com/openai/plugins
