---
name: ai-agent-workspace-tools-official-notes
description: AI 코딩 에이전트를 실행·관리·병렬화하는 도구(herdr, omp, Orca, pi, OpenCode, cmux, Claude Squad, container-use, ccusage)의 공식 저장소·README 기반 참조 노트.
tags:
  - ai-tools
  - coding-agent
  - herdr
  - oh-my-pi
  - orca
  - worktree
last_checked: 2026-10-27
sources:
  - https://github.com/herdrdev/herdr
  - https://herdr.dev/docs/
  - https://github.com/can1357/oh-my-pi
  - https://omp.sh/
  - https://github.com/stablyai/orca
  - https://www.onorca.dev/docs
  - https://github.com/earendil-works/pi
  - https://github.com/anomalyco/opencode
  - https://github.com/manaflow-ai/cmux
  - https://github.com/smtg-ai/claude-squad
  - https://github.com/dagger/container-use
  - https://github.com/ccusage/ccusage
  - https://github.com/BloopAI/vibe-kanban
  - https://github.com/stravu/crystal
---

# AI 에이전트 운영 도구 참조 노트

## 1. 확인 범위

2026-10-27에 각 도구의 공식 GitHub 저장소 정보(GitHub API)와 README를 직접 확인했습니다. 같은 이름의 fork·mirror 저장소가 여럿 있으므로 아래 저장소를 공식 원본으로 봅니다. 별 수·버전은 확인 시점 값이며 빠르게 바뀝니다.

## 2. 저장소 정보 (2026-10-27)

| 도구           | 공식 저장소                                 | 라이선스                         | 최신 릴리스           | 저장소 생성 | GitHub 별 |
|----------------|---------------------------------------------|----------------------------------|-----------------------|-------------|-----------|
| herdr          | `herdrdev/herdr`                            | Apache-2.0                       | v0.9.5 (2026-10-14)   | 2026-03-27  | 약 4.6만  |
| omp (Oh My Pi) | `can1357/oh-my-pi`                          | MIT                              | v18.13.1 (2026-10-27) | 2025-12-31  | 약 3.7만  |
| Orca           | `stablyai/orca`                             | MIT                              | v1.4.242 (2026-10-27) | 2026-03-17  | 약 10.7만 |
| pi             | `earendil-works/pi` (옛 `badlogic/pi-mono`) | MIT                              | v1.4.0 (2026-10-21)   | 2025-08-09  | 약 11.8만 |
| OpenCode       | `anomalyco/opencode` (옛 `sst/opencode`)    | MIT                              | v1.19.4 (2026-10-22)  | -           | 약 22.2만 |
| cmux           | `manaflow-ai/cmux`                          | 자체 라이선스(GitHub 분류 Other) | v0.65.2 (2026-10-16)  | -           | 약 2.9만  |
| Claude Squad   | `smtg-ai/claude-squad`                      | AGPL-3.0                         | v1.0.20 (2026-08-20)  | -           | 약 0.9만  |
| container-use  | `dagger/container-use`                      | Apache-2.0                       | v0.4.2 (2025-08-19)   | -           | 약 0.4만  |
| ccusage        | `ccusage/ccusage`                           | MIT(LICENSE 파일)                | v20.0.45 (2026-10-26) | -           | 약 1.9만  |

## 3. 도구별 README 확인 사항

### herdr

- 설명: "the runtime your coding agents live on". Rust 단일 바이너리이며 Electron을 쓰지 않습니다.
- 클라이언트를 닫거나 SSH가 끊겨도 터미널은 백그라운드 서버에서 계속 실행됩니다. 서버·기기 재시작 뒤에는 저장된 배치를 복원하고 지원 agent의 세션을 재개할 수 있지만 원래 프로세스는 살아남지 않습니다.
- 각 pane을 working·blocked·idle로 표시합니다. agent는 CLI와 socket API로 pane을 만들고 다른 agent에 지시하며, 다른 agent가 막힐 때까지 기다릴 수 있습니다.
- Claude Code·Codex·Cursor·OpenCode·Grok 등 기존 agent를 감싸거나 바꾸지 않고 터미널만 맡습니다. 저장한 SSH 기기를 한 창에서 함께 다룹니다. tmux식 prefix 키와 마우스를 모두 지원하며 plugin marketplace가 있습니다.
- 설치: `curl -fsSL https://herdr.dev/install.sh | sh`, `brew install herdr`, `mise use -g herdr`, Windows는 PowerShell 설치 스크립트(beta). 실행은 `herdr`, 분리는 `ctrl+b q`, 재연결은 `herdr`입니다.

### omp (Oh My Pi)

- 설명: "Coding agent with the IDE wired in. Built by Stencil Labs." pi를 바탕으로 기능을 더한 coding agent이며 명령은 `omp`입니다.
- README의 주요 기능: 도구를 다시 호출할 수 있는 지속 Python·Bun 실행, 쓰기마다 LSP 연동(이름 바꾸기 등), 실제 디버거 구동(lldb, dlv, debugpy 등 DAP), schema로 검증한 결과를 돌려주는 subagent(격리된 worktree), 매 턴을 읽고 의견을 넣는 advisor 모델, 내용 hash로 편집 위치를 가리키는 Hashline 편집, Zed에서 쓰는 ACP, Cursor MDC·Cline·Codex `AGENTS.md` 등 기존 규칙 파일 8종 읽기, `omp commit`.
- 설치: `curl -fsSL https://omp.sh/install | sh`, `brew install can1357/tap/omp`, `bun install -g @oh-my-pi/pi-coding-agent`(권장), Nix. bun이 없으면 설치 스크립트가 미리 빌드한 바이너리를 받아 SHA-256을 확인합니다.

### Orca

- 설명: 여러 agent를 함께 다루는 데스크톱 작업 공간이며 자기 구독으로 어떤 coding agent든 실행합니다. 데스크톱(macOS·Windows·Linux)과 모바일 동반 앱(iOS·Android)이 있습니다.
- README의 주요 기능: 한 prompt를 여러 agent에 나눠 각자 git worktree에서 실행하고 결과를 비교해 고르는 병렬 worktree, 재시작 뒤에도 남는 터미널 분할, Chromium 창의 UI 요소를 prompt에 넣는 Design Mode, GitHub·Linear 연동, SSH worktree, AI diff 줄 단위 주석, `orca worktree create` 등을 쓰는 Orca CLI, Claude·Codex 사용량·한도 표시와 계정 전환, Computer Use.
- 지원 agent: 터미널에서 실행되는 CLI agent라면 모두 지원합니다.
- 설치: onorca.dev 내려받기 또는 GitHub 릴리스, `brew install --cask stablyai/orca/orca`(이름 `orca`만 쓰면 다른 Plotly cask), Arch는 `yay -S stably-orca-bin`.

### pi

- 설명: AI agent toolkit(통합 LLM API, agent loop, TUI, coding agent CLI). omp의 바탕입니다.
- 설치: `curl -fsSL https://pi.dev/install.sh | sh`, Windows PowerShell 설치 스크립트, 또는 `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`. Node.js 22.19 이상이 필요합니다.

### OpenCode

- 설명: "The open source coding agent." 내장 agent 두 개를 `Tab`으로 바꿉니다. `build`는 기본 전체 권한, `plan`은 읽기 전용(파일 편집 거부, bash 실행 전 확인)입니다.
- 설치: `curl -fsSL https://opencode.ai/v2/install | bash`, `npm i -g @opencode/cli@latest`, `brew install anomalyco/tap/opencode-v2`, mise, Nix, 데스크톱 앱 `brew install --cask opencode-desktop`.

### cmux

- 설명: Ghostty 기반 macOS 터미널. agent가 응답을 기다리면 pane과 탭에 표시하고 알림을 모아 보여 줍니다. 터미널 옆 브라우저 분할, git branch·PR·포트를 보여 주는 사이드바, CLI·socket API를 제공합니다. Swift·AppKit으로 만든 macOS 전용 앱입니다.

### Claude Squad

- 설명: Claude Code·Codex·Gemini 등 터미널 agent 여러 개를 한 터미널 창에서 관리합니다. 작업마다 격리된 git workspace를 쓰고 적용 전 변경을 검토합니다. 백그라운드 자동 수락(yolo) 모드가 있습니다. 명령은 `cs`입니다.

### container-use

- 설명: coding agent에 컨테이너 기반 개발 환경을 주는 MCP 서버이자 CLI입니다. 각 agent가 자기 git branch의 새 컨테이너에서 일하며 명령 기록과 로그를 봅니다. Dagger 기반입니다. 마지막 릴리스는 2025-08이며 저장소 갱신은 2026-09입니다.

### ccusage

- 설명: coding agent CLI의 로컬 기록에서 토큰 사용량과 비용을 분석합니다. `npx ccusage@latest`로 실행하며 `daily`·`weekly`·`monthly`·`session` 보고서와 Codex·OpenCode·Amp 등 출처별 명령(`ccusage codex daily` 등)을 제공합니다.

### 상태 주의

- Vibe Kanban(`BloopAI/vibe-kanban`)은 README 첫머리에 서비스 종료(sunsetting)를 알렸습니다.
- Crystal(`stravu/crystal`)은 저장소 설명에 Nimbalyst로 바뀌었다고 적었고 2026-02 이후 갱신이 없습니다.

## 4. 적용 범위와 제한

- 기능 설명은 각 README의 주장이며 성능 수치(예: 토큰 절감률)는 독립 검증하지 않았습니다.
- 설치 스크립트를 `curl | sh`로 실행하는 방식은 실행 전에 스크립트 내용과 출처를 확인합니다.
- 별 수·버전은 수시로 바뀌므로 문서에서 인용할 때 확인일을 함께 적습니다.
