# AI 코딩 에이전트 운영 도구 (herdr·omp·Orca 외)
<!-- reference: _reference/ai_agent_workspace_tools_official_notes.md -->

Claude Code·Codex 같은 coding agent를 여러 개 띄우고, 끊기지 않게 유지하고, 병렬로 맡기고, 결과를 검토하는 데 쓰는 도구를 정리합니다. 2026-10-27에 각 도구의 공식 GitHub 저장소와 README를 확인한 조사 문서이며, 도구를 설치하거나 실행해 본 결과는 아닙니다. Agent 자체의 비교는 [AI 코딩 도구 비교](ai_coding_tools_comparison.md)를 참조합니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. herdr](#2-herdr) / [3. omp (Oh My Pi)](#3-omp-oh-my-pi)           |
| [4. Orca](#4-orca) / [5. 함께 볼 도구](#5-함께-볼-도구) / [6. 선택 가이드](#6-선택-가이드) |
| [7. 도입 전 확인 사항](#7-도입-전-확인-사항)                                               |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

coding agent를 오래, 여러 개 쓰기 시작하면 agent 성능보다 운영 문제가 먼저 커집니다. 터미널이 끊기면 작업이 멈추고, 어느 agent가 질문을 기다리는지 놓치고, 같은 파일을 여러 agent가 동시에 고칩니다. 이 문서의 도구는 그 문제를 계층별로 나눠 맡습니다.

```text
[Agent]        Claude Code, Codex, OpenCode, pi, omp ...   - 실제로 코드를 읽고 고침
    │
[Workspace]    herdr, cmux, Claude Squad                    - 터미널 유지, 상태 표시, 여러 agent 관리
    │
[Orchestrator] Orca                                         - worktree 병렬 실행, 결과 비교, 리뷰
    │
[Isolation]    git worktree, container-use                  - 작업 파일·실행 환경 분리
    │
[Observe]      ccusage                                      - 토큰 사용량·비용 확인
```

| 도구  | 계층           | 형태                      | 라이선스   | 한 줄 요약                                         |
|-------|----------------|---------------------------|------------|----------------------------------------------------|
| herdr | Workspace      | 터미널 다중화기(Rust CLI) | Apache-2.0 | agent 터미널을 백그라운드에서 유지하고 상태를 표시 |
| omp   | Agent(harness) | 터미널 coding agent       | MIT        | LSP·디버거·subagent를 갖춘 pi 기반 agent           |
| Orca  | Orchestrator   | 데스크톱 앱 + 모바일 앱   | MIT        | 한 작업을 여러 agent에 worktree로 나눠 맡기고 비교 |

별 수·버전은 [참조 노트](../../_reference/ai_agent_workspace_tools_official_notes.md)의 2026-10-27 값을 참고합니다. 세 도구 모두 2025-12 이후 만들어져 매일 가까이 릴리스되므로 기능과 명령이 자주 바뀝니다.

[⬆ 목차로 돌아가기](#목차)

## 2. herdr

herdr는 coding agent를 위한 터미널 작업 공간 관리자입니다. 공식 설명은 "the runtime your coding agents live on"이며, tmux처럼 터미널을 백그라운드 서버에 두되 agent 상태를 알아보는 기능을 더했습니다.

| 항목       | 내용                                                                         |
|------------|------------------------------------------------------------------------------|
| 공식       | [herdr.dev](https://herdr.dev), `herdrdev/herdr`                             |
| 형태       | Rust 단일 바이너리, 기존 터미널 안에서 실행(Electron 아님)                   |
| 지원 agent | Claude Code·Codex·Cursor·OpenCode·Grok 등. agent를 감싸지 않고 터미널만 맡음 |
| 플랫폼     | macOS·Linux, Windows는 beta                                                  |

### 주요 기능

- **분리해도 계속 실행:** 클라이언트를 닫거나 SSH가 끊겨도 작업이 이어집니다. 서버·기기를 재시작하면 배치를 복원하고 지원 agent의 세션을 재개할 수 있지만, 원래 프로세스는 남지 않습니다.
- **상태 표시:** 각 pane을 working·blocked·idle로 표시해, 답을 기다리는 agent를 바로 찾습니다.
- **여러 기기:** 로컬과 저장한 SSH 기기를 한 창에서 보고 각각 다시 연결합니다.
- **agent가 직접 조작:** agent가 CLI와 socket API로 pane을 만들고, 다른 agent에 지시하고, 다른 agent가 막힐 때까지 기다립니다.
- **조작 방식:** tmux식 prefix 키와 마우스 클릭·드래그·분할을 모두 지원하며 plugin을 추가할 수 있습니다.

### 시작

```bash
# 설치 (스크립트 내용을 먼저 확인한 뒤 실행)
curl -fsSL https://herdr.dev/install.sh | sh
# 또는
brew install herdr

# 작업 폴더에서 시작, ctrl+b q로 분리, herdr로 다시 연결
herdr
```

**잘 맞는 경우:** SSH로 서버에 접속해 agent를 오래 돌리는 경우, tmux를 이미 쓰면서 agent 상태 표시가 필요한 경우.

[⬆ 목차로 돌아가기](#목차)

## 3. omp (Oh My Pi)

omp는 pi를 바탕으로 IDE 기능을 붙인 터미널 coding agent입니다. 공식 설명은 "Coding agent with the IDE wired in"이며, herdr·Orca와 달리 agent 자체입니다.

| 항목 | 내용                                            |
|------|-------------------------------------------------|
| 공식 | [omp.sh](https://omp.sh), `can1357/oh-my-pi`    |
| 바탕 | [pi](https://github.com/earendil-works/pi)(MIT) |
| 명령 | `omp`                                           |
| 모델 | 여러 공급자 모델을 역할별로 연결                |

### 주요 기능

| 기능           | 내용                                                                 |
|----------------|----------------------------------------------------------------------|
| LSP 연동       | 쓰기마다 언어 서버를 거쳐 이름 바꾸기·import 갱신을 IDE처럼 처리     |
| 디버거 구동    | lldb·dlv·debugpy 등 DAP 디버거를 붙여 중단점·변수를 직접 확인        |
| 코드 실행      | 지속되는 Python·Bun 실행 환경에서 agent 도구를 다시 호출             |
| Subagent       | 작업을 격리된 worktree의 worker로 나누고 schema로 검증한 결과를 받음 |
| Advisor        | 다른 모델이 매 턴을 읽고 우려·차단 의견을 넣음                       |
| Hashline 편집  | 줄 내용 hash로 편집 위치를 지정해 재입력과 오래된 파일 편집을 줄임   |
| 기존 규칙 읽기 | Cursor MDC·Cline 규칙·Codex `AGENTS.md` 등 8종을 변환 없이 읽음      |
| 편집기 연동    | ACP로 Zed 안에서 같은 agent 사용                                     |

토큰 절감률 같은 성능 수치는 제작사·제3자 글의 주장이며 이 문서에서 검증하지 않았습니다.

### 시작

```bash
# 권장: bun 전역 설치
bun install -g @oh-my-pi/pi-coding-agent
# 또는 설치 스크립트 / Homebrew
curl -fsSL https://omp.sh/install | sh
brew install can1357/tap/omp
```

**잘 맞는 경우:** 터미널에서 디버거·LSP까지 agent에 맡기고 싶은 경우, 여러 모델을 역할별로 섞어 쓰는 경우.

[⬆ 목차로 돌아가기](#목차)

## 4. Orca

Orca는 여러 coding agent를 병렬로 다루는 데스크톱 작업 공간입니다. 소개 글에서는 ADE(Agent Development Environment)라고 부르며, 각 agent에 별도 git worktree를 주는 것이 핵심입니다.

| 항목       | 내용                                                          |
|------------|---------------------------------------------------------------|
| 공식       | [onorca.dev](https://www.onorca.dev), `stablyai/orca`         |
| 형태       | 데스크톱(macOS·Windows·Linux) + 모바일 동반 앱(iOS·Android)   |
| 지원 agent | 터미널에서 실행되는 모든 CLI agent, 각자의 구독을 그대로 사용 |

### 주요 기능

- **병렬 worktree:** 한 prompt를 여러 agent에 나눠 각자 worktree에서 실행하고, 결과를 비교해 하나를 병합합니다.
- **리뷰:** AI가 만든 diff의 줄마다 주석을 달아 agent에 돌려보내고 앱 안에서 commit합니다.
- **연동:** GitHub PR·issue와 Linear 보드를 앱에서 보고, 작업에서 바로 worktree를 엽니다.
- **원격:** SSH worktree로 원격 서버에서 agent를 실행하며 자동 재연결과 포트 전달을 지원합니다.
- **UI 작업:** Design Mode에서 Chromium 창의 요소를 클릭하면 HTML·CSS·캡처가 prompt에 들어갑니다.
- **자동화:** agent가 `orca worktree create` 등 Orca CLI로 작업 공간을 직접 만듭니다.
- **사용량:** Claude·Codex 사용량과 한도 초기화 시각을 보고 계정을 바꿉니다.
- **모바일:** 휴대폰에서 완료 알림을 받고 후속 지시를 보냅니다.

### 시작

```bash
# macOS (이름 orca만 쓰면 다른 Plotly cask가 설치됨)
brew install --cask stablyai/orca/orca
# Arch Linux
yay -S stably-orca-bin
```

그 밖의 OS는 [onorca.dev/download](https://onorca.dev/download)나 GitHub 릴리스에서 받습니다.

**잘 맞는 경우:** 같은 작업을 여러 agent·모델에 시켜 비교하는 경우, GUI에서 diff 리뷰와 PR 흐름을 함께 다루는 경우.

[⬆ 목차로 돌아가기](#목차)

## 5. 함께 볼 도구

세 도구와 같은 문제를 다루거나 함께 쓰기 좋은 도구입니다. 모두 2026-10-27에 공식 저장소를 확인했습니다.

| 도구          | 계층      | 라이선스      | 용도                                                                                 |
|---------------|-----------|---------------|--------------------------------------------------------------------------------------|
| pi            | Agent     | MIT           | omp의 바탕인 agent toolkit. 통합 LLM API·agent loop·TUI·coding agent CLI             |
| OpenCode      | Agent     | MIT           | 오픈소스 coding agent. `build`(전체 권한)와 `plan`(읽기 전용) agent를 `Tab`으로 전환 |
| cmux          | Workspace | 자체 라이선스 | Ghostty 기반 macOS 터미널. 응답 대기 알림·브라우저 분할·PR 상태 사이드바             |
| Claude Squad  | Workspace | AGPL-3.0      | 한 터미널에서 여러 agent를 작업별 git workspace로 관리(`cs`)                         |
| container-use | Isolation | Apache-2.0    | agent마다 자기 branch의 컨테이너 환경을 주는 MCP 서버(Dagger 기반)                   |
| ccusage       | Observe   | MIT           | Claude Code·Codex·OpenCode·Amp 등의 로컬 기록으로 토큰 사용량·비용 집계              |

`npx ccusage@latest`는 설치 없이 바로 일별 사용량을 보여 주므로, 여러 agent를 병렬로 돌리기 전 비용 기준선을 잡는 데 유용합니다.

### 상태 주의

| 도구          | 상태                                                              |
|---------------|-------------------------------------------------------------------|
| Vibe Kanban   | README에 서비스 종료(sunsetting)를 알림. 새로 도입하지 않음       |
| Crystal       | Nimbalyst로 바뀌었다고 안내하며 2026-02 이후 저장소 갱신 없음     |
| container-use | 마지막 릴리스가 2025-08. 저장소 활동은 이어지나 도입 전 상태 확인 |

[⬆ 목차로 돌아가기](#목차)

## 6. 선택 가이드

| 상황                                                  | 우선 검토                    |
|-------------------------------------------------------|------------------------------|
| SSH로 서버에 붙어 agent를 오래 돌리고 끊김이 잦음     | herdr                        |
| macOS에서 터미널 중심으로 여러 agent 알림을 받고 싶음 | cmux                         |
| 같은 작업을 여러 agent·모델로 동시에 시켜 비교        | Orca                         |
| GUI에서 diff 리뷰·PR·Linear까지 한 곳에서             | Orca                         |
| 터미널 agent에 디버거·LSP를 붙이고 싶음               | omp                          |
| 가볍고 확장 가능한 오픈소스 agent 기반이 필요         | pi, OpenCode                 |
| agent마다 실행 환경까지 분리해야 함                   | container-use, 별도 컨테이너 |
| 병렬 실행 전후 비용을 확인                            | ccusage                      |

조합 예시는 다음과 같습니다.

- **서버 작업:** herdr 안에서 Claude Code·Codex를 pane별로 실행하고, ccusage로 하루 사용량을 확인합니다.
- **기능 비교:** Orca로 같은 이슈를 두세 agent에 worktree로 맡기고, diff 주석으로 수정을 요청한 뒤 하나를 병합합니다.
- **디버깅 위임:** omp에 재현 명령과 디버거 사용을 허용하고, advisor 모델을 붙여 결과를 함께 검토합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 도입 전 확인 사항

- **설치 스크립트:** `curl ... | sh` 방식은 실행 전에 스크립트 내용과 도메인을 확인합니다. 패키지 관리자(Homebrew·bun·AUR)를 쓸 수 있으면 그쪽을 우선합니다.
- **같은 이름 주의:** GitHub에 같은 이름의 fork·mirror가 많습니다. 공식 저장소는 `herdrdev/herdr`, `can1357/oh-my-pi`, `stablyai/orca`입니다. Homebrew에서 `orca`만 쓰면 다른 프로그램이 설치됩니다.
- **worktree는 보안 경계가 아님:** git worktree는 작업 파일만 나눕니다. 권한·네트워크·비밀 정보 접근을 막으려면 컨테이너 등 별도 격리가 필요합니다. 자세한 구분은 [Harness Engineering](harness_engineering.md)을 참조합니다.
- **자동 수락 모드:** 백그라운드 자동 수락(예: Claude Squad의 yolo 모드)은 격리된 환경과 되돌릴 수 있는 작업에만 씁니다.
- **비용과 한도:** agent를 병렬로 돌리면 사용량·한도가 그만큼 빨리 찹니다. 실행 전후로 사용량을 확인합니다.
- **라이선스:** Claude Squad(AGPL-3.0)와 cmux(자체 라이선스)는 회사 배포·수정 전에 조건을 확인합니다.
- **변화 속도:** 세 도구 모두 생긴 지 1년이 안 됐고 거의 매일 릴리스됩니다. 명령·기능은 공식 문서에서 다시 확인합니다.

## 참고 자료

- herdr: [GitHub](https://github.com/herdrdev/herdr), [문서](https://herdr.dev/docs/) — ★★★☆☆
- omp (Oh My Pi): [GitHub](https://github.com/can1357/oh-my-pi), [omp.sh](https://omp.sh/) — ★★★☆☆
- Orca: [GitHub](https://github.com/stablyai/orca), [문서](https://www.onorca.dev/docs) — ★★★☆☆
- pi: [GitHub](https://github.com/earendil-works/pi) — ★★★☆☆
- OpenCode: [GitHub](https://github.com/anomalyco/opencode) — ★★★☆☆
- cmux: [GitHub](https://github.com/manaflow-ai/cmux) — ★★★☆☆
- Claude Squad: [GitHub](https://github.com/smtg-ai/claude-squad) — ★★★☆☆
- container-use: [GitHub](https://github.com/dagger/container-use) — ★★★☆☆
- ccusage: [GitHub](https://github.com/ccusage/ccusage) — ★★★☆☆
- herdr 소개 기사: [TecMint](https://www.tecmint.com/herdr-run-ai-coding-agents-in-linux-terminal/) — ★★☆☆☆
- omp 소개 기사: [Better Stack](https://betterstack.com/community/guides/ai/oh-my-pi-ai-coding-agent/) — ★★☆☆☆
- Orca 소개 기사: [AgentConn](https://agentconn.com/blog/orca-ade-agent-fleet-parallel-coding-agents-2026/) — ★★☆☆☆
- [공식 참조 노트](../../_reference/ai_agent_workspace_tools_official_notes.md)
- [AI 코딩 도구 비교](ai_coding_tools_comparison.md)
- [Harness Engineering](harness_engineering.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-27

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.
