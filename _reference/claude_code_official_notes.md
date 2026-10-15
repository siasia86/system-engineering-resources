---
name: claude-code-official-notes
description: Anthropic Claude 모델 라인업·가격과 Claude Code의 설치·인증·권한·설정·확장·비대화형 실행 공식 참조 노트
tags:
  - claude
  - claude-code
  - anthropic
  - ai-agent
  - cli
last_checked: 2026-10-15
sources:
  - https://code.claude.com/docs/llms.txt
  - https://code.claude.com/docs/en/overview.md
  - https://code.claude.com/docs/en/setup.md
  - https://code.claude.com/docs/en/authentication.md
  - https://code.claude.com/docs/en/platforms.md
  - https://code.claude.com/docs/en/permission-modes.md
  - https://code.claude.com/docs/en/settings.md
  - https://code.claude.com/docs/en/memory.md
  - https://code.claude.com/docs/en/skills.md
  - https://code.claude.com/docs/en/hooks-guide.md
  - https://code.claude.com/docs/en/sub-agents.md
  - https://code.claude.com/docs/en/mcp.md
  - https://code.claude.com/docs/en/headless.md
  - https://code.claude.com/docs/en/model-config.md
  - https://code.claude.com/docs/en/costs.md
  - https://platform.claude.com/docs/en/about-claude/models/overview.md
  - https://platform.claude.com/docs/en/about-claude/pricing.md
  - https://platform.claude.com/docs/en/about-claude/model-deprecations.md
  - https://claude.com/pricing
  - https://code.claude.com/docs/en/quickstart.md
  - https://code.claude.com/docs/en/interactive-mode.md
  - https://code.claude.com/docs/en/common-workflows.md
  - https://code.claude.com/docs/en/best-practices.md
  - https://code.claude.com/docs/en/checkpointing.md
  - https://code.claude.com/docs/en/commands.md
  - https://code.claude.com/docs/en/desktop.md
  - https://code.claude.com/docs/en/claude-projects.md
  - https://github.com/anthropics/claude-code/releases
---

# Claude Code 공식 참조 노트

## 1. 버전 상태

- 2026-10-14 확인한 GitHub 최신 릴리스: `v2.1.299` (2026-10-14 게시, `gh api repos/anthropics/claude-code/releases/latest`).
- 공식 문서의 설치 확인 예시 출력은 `2.1.211 (Claude Code)`이며, 이는 형식 예시입니다.
- 작성 서버의 `PATH`에는 `claude` CLI가 없습니다. 2026-10-15 데스크톱 앱이 SSH 세션용으로 설치한 `~/.claude/remote/ccd-cli/2.1.295-<빌드>`에서 `--version`을 실행해 `2.1.295 (Claude Code)`를 확인했습니다. 그 밖의 CLI 도움말·실제 실행 대조는 하지 않았고 명령·옵션은 공식 문서 기준입니다.
- 문서에 버전 조건이 붙은 기능은 해당 버전을 함께 기록합니다. 예: 내장 기본 권한 모드 `auto`는 v2.1.283 이상.

## 2. 모델 라인업 (platform.claude.com, 2026-10-14)

| 모델              | API ID              | 입력 / 출력 (1M 토큰당)                 | 컨텍스트 | 최대 출력 | 기본 effort | 지연      |
|-------------------|---------------------|-----------------------------------------|----------|-----------|-------------|-----------|
| Claude Fable 5.1  | `claude-fable-5-1`  | $10 / $50                               | 1M       | 128K      | `high`      | 느림      |
| Claude Opus 5.5   | `claude-opus-5-5`   | $4 / $20                                | 1M       | 128K      | `medium`    | 보통      |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10                                | 1M       | 128K      | `high`      | 빠름      |
| Claude Haiku 5.5  | `claude-haiku-5-5`  | $0.10 / $0.50 (프롬프트 100K 토큰 이하) | 1M       | 128K      | `medium`    | 가장 빠름 |

- 공식 권장: 대부분의 작업은 Opus 5.5로 시작하고, 어려운 추론·장시간 에이전트 작업은 Fable 5.1을 사용합니다.
- Haiku 5.5는 프롬프트가 100,000 토큰을 넘으면 $0.50 / $2.50으로 가격이 올라갑니다.
- 네 모델 모두 지식 기준일(reliable knowledge cutoff)은 2026년 6월입니다.
- Bedrock ID는 `anthropic.` 접두사를 붙입니다(예: `anthropic.claude-opus-5-5`). Google Cloud·Microsoft Foundry·Claude Platform on AWS는 API ID를 그대로 씁니다.
- 4.6 세대부터 날짜 없는 ID 자체가 고정 스냅샷입니다.
- Batch API는 50% 할인, 캐시 읽기는 기본 입력가의 10%입니다(Fable 5.1 2.5%, Opus 5.5·Sonnet 5.5 5%).
- Claude Mythos 5.1·5는 제한 제공(limited availability) 모델로 공개 라인업 표에는 없습니다. 가격은 Fable과 같습니다.
- 사용 가능한 이전 모델(legacy): Fable 5, Opus 5, Opus 4.8·4.7·4.6·4.5, Sonnet 5, Sonnet 4.6, Haiku 4.5.
- 폐기 일정: Claude Sonnet 4.5(`claude-sonnet-4-5-20250929`)는 2026-09-30 폐기 예고, 2026-11-30 API 종료, 대체 모델 `claude-sonnet-5-5`. Sonnet 4·Opus 4는 Claude API에서 종료(Bedrock·Google Cloud 일부 예외).

## 3. 구독과 비용 (claude.com/pricing, code.claude.com/costs)

- Claude Code는 모든 유료 플랜에 포함되며, 채팅과 사용량 한도를 공유합니다. 무료 플랜에는 포함되지 않습니다.
- 사용 가능 계정: Pro, Max, Team, Enterprise, Claude Console(API 종량제). Bedrock·Google Cloud·Microsoft Foundry 같은 클라우드 제공자로도 사용할 수 있습니다.

| 플랜       | 가격                                                        | 사용량                         |
|------------|-------------------------------------------------------------|--------------------------------|
| Pro        | 월 $20 (연간 결제 시 월 $17)                                | Free 대비 5시간당 5배 이상     |
| Max        | 월 $100부터                                                 | Pro 대비 5배 또는 20배 중 선택 |
| Team       | Standard 좌석 $25 (연간 $20), Premium 좌석 $125 (연간 $100) | Premium은 Standard의 5배       |
| Enterprise | 좌석당 월 $20 + API 요금 기준 사용량                        | 연간 계약                      |

- 사용량 한도는 5시간 단위로 초기화되고, 유료 플랜에는 주간 한도가 추가됩니다.
- 기업 배포 평균 비용: 활성일 기준 개발자당 약 $13, 월 $150~250, 사용자 90%가 활성일당 $30 미만(costs 문서).

## 4. 설치와 업데이트 (setup)

- 지원 OS: macOS 13.0+, Windows 10 1809+ / Server 2019+, Ubuntu 20.04+, Debian 10+, Alpine 3.19+. RAM 4GB 이상, x64·ARM64.
- 권장 설치(native): `curl -fsSL https://claude.ai/install.sh | bash` (macOS·Linux·WSL). 자동 업데이트됩니다.
- 패키지 관리자: Homebrew `brew install --cask claude-code`(stable) 또는 `claude-code@latest`, WinGet `Anthropic.ClaudeCode`, apt·dnf·apk 저장소(`downloads.claude.ai/claude-code/{apt,rpm,apk}/{stable,latest}`). 패키지 관리자 설치는 기본적으로 자동 업데이트되지 않습니다.
- 저장소 서명 키 fingerprint: `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`.
- npm 설치: `npm install -g @anthropic-ai/claude-code` (Node.js 22 이상).
- 확인: `claude --version`, 진단: `claude doctor`(세션 없이 읽기 전용 점검).
- 업데이트 채널: `autoUpdatesChannel`을 `latest`(기본) 또는 `stable`(약 1주 지연, 큰 회귀 제외)로 설정. `minimumVersion`으로 하한 고정. 자동 업데이트 끄기는 `DISABLE_AUTOUPDATER=1`, 모든 업데이트 차단은 `DISABLE_UPDATES`.
- native 설치는 `~/.local/bin/claude`를 `~/.local/share/claude/versions/` 안으로 연결하는 symlink로 관리합니다.

## 5. 인증 (authentication)

- 최초 실행 시 브라우저 로그인. `ANTHROPIC_API_KEY`가 있고 사용을 승인하면 로그인을 건너뜁니다.
- Linux 자격 증명 저장 위치: `~/.claude/.credentials.json` (파일 권한 `0600`). macOS는 Keychain, `CLAUDE_CONFIG_DIR` 지정 시 그 아래.
- 인증 우선순위(높은 순):
  1. 클라우드 제공자(`CLAUDE_CODE_USE_BEDROCK` / `_VERTEX` / `_FOUNDRY`)
  2. `ANTHROPIC_AUTH_TOKEN` (Bearer, LLM gateway용)
  3. `ANTHROPIC_API_KEY` (Console API 키)
  4. `apiKeyHelper` 스크립트 출력
  5. `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`으로 발급한 1년짜리 토큰, CI용)
  6. Anthropic profile·Workload Identity Federation 자격 증명
  7. `/login`으로 받은 구독 OAuth 자격 증명
- 구독 사용 중 `ANTHROPIC_API_KEY`가 설정돼 있으면 승인 후 API 키가 쓰입니다. `/status`로 현재 인증 방식을 확인합니다.

## 6. 권한 모드 (permission-modes)

| 모드                | 묻지 않고 실행하는 범위                                   | 용도                    |
|---------------------|-----------------------------------------------------------|-------------------------|
| `default` (Manual)  | 읽기만                                                    | 모든 작업 직접 검토     |
| `acceptEdits`       | 읽기, 파일 편집, `mkdir`·`touch`·`mv`·`cp` 등 파일 명령   | 검토하며 반복 수정      |
| `plan`              | 읽기 (+ auto 사용 가능 시 분류기가 승인한 명령)           | 변경 전 분석            |
| `auto`              | 전부, 별도 분류기(classifier) 모델이 백그라운드 안전 점검 | 장시간 작업             |
| `dontAsk`           | 작업 디렉터리 읽기와 사전 허용 도구만, 나머지는 거부      | 고정 허용 목록의 CI     |
| `bypassPermissions` | 전부                                                      | 격리된 컨테이너·VM 전용 |

- 시작 모드 결정 순서: `--permission-mode` 플래그 → 설정 파일 `permissions.defaultMode` → 내장 기본값.
- 내장 기본값: v2.1.283 이상의 대화형 터미널·VS Code 세션은 `auto`. `claude -p`는 feature flag를 받는 세션에서 `default`. 설정에서 `disableAutoMode`를 `"disable"`로 두면 `default`.
- auto 모드를 쓸 수 없는 조건이면 Manual로 시작합니다. 세션 중 `Shift+Tab`으로 모드를 순환합니다.

## 7. 설정과 지침 파일 (settings, memory)

- 설정 우선순위(높은 순): Managed settings → 명령행 `--settings` → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`. 목록 값은 덮어쓰지 않고 병합됩니다.
- `.claude/settings.local.json`은 Claude Code가 처음 쓸 때 전역 git exclude에 추가합니다.
- 지침 파일(CLAUDE.md) 위치:
  - 조직: Linux `/etc/claude-code/CLAUDE.md`
  - 사용자: `~/.claude/CLAUDE.md`
  - 프로젝트: `./CLAUDE.md` 또는 `./.claude/CLAUDE.md`
  - 개인 프로젝트용: `./CLAUDE.local.md` (`.gitignore` 대상)
- `AGENTS.md`: 작업 디렉터리나 상위에 `CLAUDE.md`·`CLAUDE.local.md`가 없으면 `AGENTS.md`를 프로젝트 지침으로 읽습니다. 둘 다 있으면 `CLAUDE.md`만 읽고, `CLAUDE.md`에서 `AGENTS.md`를 import하면 함께 읽습니다.
- Auto memory: Claude가 직접 기록하는 저장소별 메모리로, 세션마다 앞 200줄 또는 25KB까지 로드합니다.

## 8. 확장 기능

### Skills (skills)

- 위치: 조직(managed 디렉터리), 개인 `~/.claude/skills/<이름>/SKILL.md`, 프로젝트 `.claude/skills/<이름>/SKILL.md`, 하위 디렉터리, `--add-dir` 디렉터리, plugin, claude.ai 계정.
- 같은 이름이면 조직 > 개인 > 프로젝트 순으로 우선합니다.
- `.claude/commands/*.md`(이전 custom command 형식)는 skill로 통합되었으며 계속 동작합니다.
- [Agent Skills](https://agentskills.io) 공개 표준을 따르고 Claude Code 전용 frontmatter를 추가합니다. 주요 필드: `name`, `description`, `when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context: fork`, `paths`.

### Hooks (hooks-guide)

- 이벤트 예: `SessionStart`, `UserPromptSubmit`, `PreToolUse`(차단 가능), `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `Notification`, `SubagentStart`·`SubagentStop`, `Stop`, `PreCompact`·`PostCompact`, `ConfigChange`, `FileChanged`, `SessionEnd` 등 30여 종.
- hook 유형: `command`(셸), `http`(URL로 POST), `mcp_tool`, `prompt`(단일 LLM 평가), `agent`(실험적).

### Subagents (sub-agents)

- 정의 위치(우선순위 순): managed settings → `--agents` 플래그 → `.claude/agents/` → `~/.claude/agents/` → plugin `agents/`.
- 필수 frontmatter: `name`, `description`. 선택: `tools`, `disallowedTools`, `model`(`sonnet`·`opus`·`haiku`·`fable`·전체 ID·`inherit`), `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `memory`, `isolation: worktree` 등.

### MCP (mcp)

| scope   | 적용 범위     | 팀 공유        | 저장 위치                 |
|---------|---------------|----------------|---------------------------|
| local   | 현재 프로젝트 | 아니오         | `~/.claude.json`          |
| project | 현재 프로젝트 | 예 (버전 관리) | 프로젝트 루트 `.mcp.json` |
| user    | 모든 프로젝트 | 아니오         | `~/.claude.json`          |

- 추가: `claude mcp add --transport http <name> <url>`, `claude mcp add --transport stdio <name> -- <command>`. 관리: `claude mcp list|get|remove`.

### Plugins

- skill·subagent·hook·MCP 서버를 묶어 배포하는 단위입니다. plugin skill은 `/plugin-name:skill-name`으로 호출합니다.

## 9. 비대화형 실행 (headless)

- `claude -p "<prompt>"`: 비대화형 실행. `--allowedTools`, `--continue`, `--resume`, `--output-format text|json|stream-json`, `--json-schema` 지원.
- `--output-format json` 결과에는 `total_cost_usd`와 모델별 비용이 포함됩니다.
- `--bare`: hook·skill·subagent·plugin·MCP·auto memory·CLAUDE.md 자동 탐색을 건너뜁니다. 스크립트·SDK 호출 권장 모드이며 향후 `-p`의 기본값이 될 예정입니다. bare 모드는 구독 로그인을 쓰지 않으므로 `ANTHROPIC_API_KEY`가 필요합니다.
- 보안 주의: `--bare` 없이 `-p`를 실행하면 신뢰 확인 대화상자 없이 프로젝트 `.claude/settings.json`의 hook과 `.mcp.json` 서버가 실행됩니다.

## 10. 모델 설정 (model-config)

- 별칭: `default`, `best`, `fable`, `opus`, `sonnet`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`(plan 모드는 opus, 실행은 sonnet).
- Anthropic API에서 별칭이 가리키는 모델: `opus` → Opus 5.5, `sonnet` → Sonnet 5.5, `haiku` → Haiku 5.5. Bedrock·Google Cloud에서는 `sonnet` → Sonnet 4.5, `haiku` → Haiku 4.5로 제공자마다 다릅니다.
- effort 단계: Fable·Opus 5.5·Sonnet 5.5·Haiku 5.5 등은 `low`·`medium`·`high`·`xhigh`·`max`. Opus 4.6·Sonnet 4.6은 `xhigh` 없음.
- 별칭 대상 고정: `ANTHROPIC_DEFAULT_{SONNET,OPUS,HAIKU,FABLE}_MODEL`.

## 11. 사용 환경 (platforms)

| 환경      | 용도                                   |
|-----------|----------------------------------------|
| CLI       | 터미널·스크립트·원격 서버, 전체 기능   |
| Desktop   | diff 검토, 병렬 세션, 예약 작업        |
| VS Code   | 편집기 안 inline diff                  |
| JetBrains | IntelliJ 계열 IDE 통합                 |
| Web       | 클라우드에서 장시간 작업               |
| Mobile    | 이동 중 작업 시작·확인, Remote Control |

- 연동: Chrome, GitHub Actions, GitLab CI/CD, Code Review, Slack, Claude Tag.
- Desktop 앱은 macOS·Windows를 지원하며 Ubuntu·Debian은 apt 설치 베타입니다. 유료 구독이 필요하고 CLI를 따로 설치하지 않아도 됩니다.

- Projects (claude-projects, 2026-10-15): Pro·Max 공개 beta, 단계적 제공(Team·Enterprise 미제공). 대화 하나가 스레드(기본 클라우드 세션)를 시작·추적하고 프로젝트 지침·메모리를 공유합니다. claude.ai/code·데스크톱 앱·모바일 앱에서만 쓰며 터미널 CLI·VS Code·JetBrains·Bedrock·Agent Platform·Foundry에서는 쓸 수 없습니다. 직접 시작한 로컬 세션은 프로젝트에 넣을 수 없고, 로컬 폴더 작업은 Remote Control(v2.1.280 이상)로 연결한 폴더에서 **Work locally** 스레드로 실행합니다(auto 모드, 프로젝트 지침은 적용·메모리 파일은 미적용). 클라우드 sandbox를 다시 열지 못하면 새 clone에서 이어가 commit하지 않은 변경이 사라질 수 있습니다. 한 사용자 전용이며 공유할 수 없습니다. 코드 작업은 github.com 저장소와 Claude GitHub App·push 권한이 필요합니다.

## 12. 검증 기록

- 1차 대조(2026-10-14): code.claude.com의 overview·setup·authentication·permission-modes·settings·memory·skills·hooks-guide·sub-agents·mcp·headless·model-config·platforms 문서 원문을 내려받아 항목별로 확인했습니다.
- 2차 대조(2026-10-14): platform.claude.com의 models overview·pricing·model-deprecations와 claude.com/pricing, GitHub 릴리스 API로 모델 ID·가격·플랜·버전을 교차 확인했습니다. setup 문서의 "Pro, Max, Team, Enterprise, Console 계정 필요"와 pricing 페이지의 "모든 유료 플랜 포함"이 일치함을 확인했습니다.
- 3차 대조(2026-10-15): quickstart·interactive-mode·common-workflows·best-practices·checkpointing·commands·desktop·skills 원문을 내려받아 기본 사용법·데스크톱 앱·스킬 목록 문서의 단축키·명령·plan 모드·되돌리기 한계·SSH 요구 사항·스킬 우선순위를 확인했습니다. 사이드바 섹션 구성(Pinned·Routines·Sessions·사용자 그룹)은 공식 문서에 없어 같은 날 데스크톱 앱 SSH 세션에서 관찰한 결과로 적었습니다.
- 미검증: `claude --version` 외의 터미널 명령, 직접 설치·로그인, 단축키 동작은 실행하지 않았습니다. Max 20배 요금제의 정확한 가격은 pricing 페이지 본문에서 확인하지 못했습니다.

## 13. 공식 자료

- Claude Code 문서 색인: https://code.claude.com/docs/llms.txt
- Advanced setup: https://code.claude.com/docs/en/setup
- Authentication: https://code.claude.com/docs/en/authentication
- Permission modes: https://code.claude.com/docs/en/permission-modes
- Settings: https://code.claude.com/docs/en/settings
- Memory: https://code.claude.com/docs/en/memory
- Skills: https://code.claude.com/docs/en/skills
- Hooks guide: https://code.claude.com/docs/en/hooks-guide
- Subagents: https://code.claude.com/docs/en/sub-agents
- MCP: https://code.claude.com/docs/en/mcp
- Headless: https://code.claude.com/docs/en/headless
- Model configuration: https://code.claude.com/docs/en/model-config
- Models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Pricing (API): https://platform.claude.com/docs/en/about-claude/pricing
- Pricing (plans): https://claude.com/pricing
- Releases: https://github.com/anthropics/claude-code/releases
- Quickstart: https://code.claude.com/docs/en/quickstart
- Interactive mode: https://code.claude.com/docs/en/interactive-mode
- Common workflows: https://code.claude.com/docs/en/common-workflows
- Best practices: https://code.claude.com/docs/en/best-practices
- Checkpointing: https://code.claude.com/docs/en/checkpointing
- Commands: https://code.claude.com/docs/en/commands
- Desktop: https://code.claude.com/docs/en/desktop
- Projects: https://code.claude.com/docs/en/claude-projects

---

**작성일**: 2026-10-14

**마지막 업데이트**: 2026-10-15

© 2026 siasia86. Licensed under CC BY 4.0.
