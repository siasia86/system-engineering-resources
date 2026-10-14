# Claude Code 지침 파일과 확장 기능 가이드
<!-- reference: _reference/claude_code_official_notes.md -->

Claude Code의 동작을 프로젝트에 맞게 고정하는 방법을 정리합니다. 지침 파일(`CLAUDE.md`·`AGENTS.md`), 설정 파일, Skills, Hooks, Subagents, MCP, Plugins의 역할과 위치, 작성 예시를 다룹니다. 설치와 권한 모드는 [Linux CLI 가이드](claude_code_cli_linux_guide.md)를 참고합니다.

## 목차

| 단계 | 섹션                                                                                       |
|------|--------------------------------------------------------------------------------------------|
| 기준 | [1. 지침 파일](#1-지침-파일) / [2. 설정 파일](#2-설정-파일) / [3. 기능 선택](#3-기능-선택) |
| 확장 | [4. Skills](#4-skills) / [5. Hooks](#5-hooks) / [6. Subagents](#6-subagents)               |
| 연동 | [7. MCP](#7-mcp) / [8. Plugins](#8-plugins) / [9. 운영 원칙](#9-운영-원칙)                 |

---

## 1. 지침 파일

| 범위            | 위치                                     | 공유 대상              |
|-----------------|------------------------------------------|------------------------|
| 조직            | Linux `/etc/claude-code/CLAUDE.md`       | 조직 전체 (IT 배포)    |
| 사용자          | `~/.claude/CLAUDE.md`                    | 나 (모든 프로젝트)     |
| 프로젝트        | `./CLAUDE.md` 또는 `./.claude/CLAUDE.md` | 팀 (버전 관리)         |
| 개인 프로젝트용 | `./CLAUDE.local.md`                      | 나 (현재 프로젝트)     |
| 파일 유형별     | `.claude/rules/*.md`                     | 팀, 특정 경로에만 적용 |

### `AGENTS.md`와 함께 쓰기

| 저장소 상태                           | Claude Code가 읽는 파일   |
|---------------------------------------|---------------------------|
| `AGENTS.md`만 있음                    | `AGENTS.md`               |
| `AGENTS.md`와 `CLAUDE.md`가 함께 있음 | `CLAUDE.md`만             |
| `CLAUDE.md`가 `AGENTS.md`를 import    | `CLAUDE.md` + `AGENTS.md` |

Codex 등 다른 도구와 같이 쓰는 저장소는 공통 규칙을 `AGENTS.md`에 두고, `CLAUDE.md`에서 import한 뒤 Claude 전용 내용만 추가합니다.

```markdown
# CLAUDE.md
@AGENTS.md

## Claude Code 전용
- 문서 수정 후 `sia-md-style-check`와 `sia-md-link-check`를 실행합니다.
```

- `@path/to/file` 형식으로 다른 파일을 import하면 세션 시작 시 함께 로드됩니다.
- 처음 만들 때는 `/init`으로 초안을 생성한 뒤 다듬습니다.
- 지침끼리 모순되면 Claude가 임의로 하나를 고를 수 있으므로, 하위 디렉터리 `CLAUDE.md`와 rules까지 함께 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설정 파일

| 우선순위 | 위치                            | 용도                              |
|----------|---------------------------------|-----------------------------------|
| 1 (최고) | Managed settings                | 조직 강제 정책 (사용자 변경 불가) |
| 2        | 명령행 `--settings <파일/JSON>` | 이번 세션만                       |
| 3        | `.claude/settings.local.json`   | 개인 프로젝트 설정 (git 제외)     |
| 4        | `.claude/settings.json`         | 팀 공유 프로젝트 설정 (커밋)      |
| 5        | `~/.claude/settings.json`       | 개인 전역 설정                    |

- 같은 키는 우선순위가 높은 값이 적용되고, `permissions.allow` 같은 목록 값은 병합됩니다.
- `.claude/settings.local.json`은 Claude Code가 처음 만들 때 전역 git exclude에 추가합니다. 직접 만들면 `.gitignore`에 추가합니다.
- 설정 화면은 `/config`, 권한 규칙은 `/permissions`로 엽니다.

```json
{
  "permissions": {
    "defaultMode": "default",
    "allow": ["Bash(git status)", "Bash(git diff *)"],
    "deny": ["Read(./.env)", "Bash(git push *)"]
  },
  "autoUpdatesChannel": "stable"
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기능 선택

| 필요                               | 기능        | 특징                                 |
|------------------------------------|-------------|--------------------------------------|
| 항상 지켜야 할 프로젝트 규칙       | `CLAUDE.md` | 매 세션 자동 로드                    |
| 필요할 때만 쓰는 작업 절차         | Skills      | 설명만 먼저 로드, 필요 시 본문 로드  |
| 반드시 실행되어야 하는 검사·자동화 | Hooks       | 모델 판단과 무관하게 이벤트마다 실행 |
| 독립된 컨텍스트로 맡길 하위 작업   | Subagents   | 별도 컨텍스트·도구·모델로 실행       |
| 외부 시스템 데이터·도구            | MCP         | DB, 이슈 트래커, 사내 API 연결       |
| 위 구성을 팀에 묶어서 배포         | Plugins     | skill·agent·hook·MCP 묶음            |

지침 파일과 Skills는 모델이 읽고 따르는 **요청**이고, Hooks와 권한 규칙은 Claude Code가 실행하는 **강제 장치**입니다. 반드시 지켜야 하는 규칙은 Hooks나 deny 규칙으로 구현합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Skills

| 위치     | 경로                               | 적용 범위              |
|----------|------------------------------------|------------------------|
| 개인     | `~/.claude/skills/<이름>/SKILL.md` | 내 모든 프로젝트       |
| 프로젝트 | `.claude/skills/<이름>/SKILL.md`   | 이 저장소 (커밋 시 팀) |
| Plugin   | `<plugin>/skills/<이름>/SKILL.md`  | `/plugin-name:이름`    |

같은 이름이면 조직 > 개인 > 프로젝트 순으로 우선합니다. 이전 형식인 `.claude/commands/*.md`도 skill로 동작합니다.

```markdown
---
name: md-check
description: Markdown 문서를 수정한 뒤 style·heading·link 검사를 실행합니다. 문서 변경 후 커밋 전에 사용합니다.
disable-model-invocation: true
allowed-tools: Bash(sia-md-style-check *) Bash(sia-md-heading-check *) Bash(sia-md-link-check *)
---

변경된 Markdown 파일을 대상으로 다음을 실행하고 결과를 요약합니다.

1. `sia-md-style-check <파일>`
2. `sia-md-heading-check <파일>`
3. `sia-md-link-check <파일>`
```

| 필드                       | 의미                                               |
|----------------------------|----------------------------------------------------|
| `description`              | Claude가 언제 쓸지 판단하는 기준 (권장)            |
| `disable-model-invocation` | `true`면 Claude가 자동 실행하지 않고 `/이름`으로만 |
| `user-invocable`           | `false`면 `/` 메뉴에서 숨기고 Claude만 사용        |
| `allowed-tools`            | 이 skill 실행 중 묻지 않고 쓸 도구                 |
| `model`, `effort`          | 이 skill 실행 중 모델·effort 변경                  |
| `context: fork`            | 별도 subagent 컨텍스트에서 실행                    |
| `paths`                    | 특정 파일 경로 작업 시에만 자동 로드               |

Claude Code Skills는 [Agent Skills](https://agentskills.io) 공개 표준을 따르므로 기본 필드는 다른 도구와 호환됩니다. Codex의 skill 작성은 [Codex Skills 설정 가이드](../codex/codex_skills_setup_guide.md)와 비교해 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Hooks

Hooks는 특정 이벤트에서 셸 명령 등을 실행합니다. 설정 파일의 `hooks` 키에 이벤트별로 정의합니다.

| 이벤트             | 시점                     | 활용 예                       |
|--------------------|--------------------------|-------------------------------|
| `SessionStart`     | 세션 시작·재개           | 환경 정보 주입                |
| `UserPromptSubmit` | 프롬프트 제출 직후       | 금지어·민감정보 검사          |
| `PreToolUse`       | 도구 실행 전 (차단 가능) | 위험 명령·보호 파일 수정 차단 |
| `PostToolUse`      | 도구 실행 성공 후        | 편집 파일 자동 포맷·검사      |
| `Notification`     | 알림 발생 시             | 데스크톱·메신저 알림          |
| `Stop`             | 응답 완료 시             | 작업 종료 후 검증 실행        |
| `PreCompact`       | 컨텍스트 요약 전         | 중요 상태 저장                |
| `SessionEnd`       | 세션 종료                | 정리 작업                     |

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm-rf.sh" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs sia-md-style-check" }]
      }
    ]
  }
}
```

- hook은 이벤트 정보를 표준 입력 JSON으로 받습니다.
- 종료 코드 `2`는 작업을 차단하며, 표준 오류에 쓴 이유가 Claude나 사용자에게 전달됩니다.
- 유형: `command`(셸), `http`(URL로 POST), `mcp_tool`, `prompt`(LLM 단일 평가), `agent`(실험적).
- PreToolUse hook이 허용을 반환해도 deny·ask 권한 규칙은 그대로 적용됩니다.
- hook은 내 계정 권한으로 실행됩니다. 다른 사람이 커밋한 hook은 실행 전에 내용을 확인합니다. 설정 확인은 `/hooks`.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Subagents

Subagent는 별도 컨텍스트에서 하위 작업을 맡는 에이전트입니다. 긴 탐색이나 리뷰를 맡기면 주 대화의 컨텍스트를 아낄 수 있습니다.

| 위치                | 적용 범위        | 우선순위 |
|---------------------|------------------|----------|
| Managed settings    | 조직             | 1 (최고) |
| `--agents` 플래그   | 현재 세션        | 2        |
| `.claude/agents/`   | 현재 프로젝트    | 3        |
| `~/.claude/agents/` | 내 모든 프로젝트 | 4        |
| Plugin `agents/`    | plugin 활성 범위 | 5        |

```markdown
---
name: md-reviewer
description: Markdown 문서 변경을 검토할 때 사용합니다. 링크·표·사실 근거를 확인하고 문제 목록만 보고합니다.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
---

변경된 문서를 읽고 깨진 링크, 표 정렬, 출처 없는 수치, 날짜 불일치를 찾아 파일:줄 형식으로 보고합니다. 파일은 수정하지 않습니다.
```

- 필수 필드는 `name`, `description`입니다. `tools`를 생략하면 사용 가능한 도구를 모두 상속합니다.
- `model`: `sonnet`·`opus`·`haiku`·`fable`·전체 모델 ID·`inherit`.
- `isolation: worktree`를 지정하면 임시 git worktree에서 실행되어 주 작업 트리와 분리됩니다.
- `memory`(`user`·`project`·`local`)로 세션 간 기억을 둘 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. MCP

| scope   | 적용 범위     | 팀 공유   | 저장 위치                 |
|---------|---------------|-----------|---------------------------|
| local   | 현재 프로젝트 | 아니오    | `~/.claude.json`          |
| project | 현재 프로젝트 | 예 (커밋) | 프로젝트 루트 `.mcp.json` |
| user    | 모든 프로젝트 | 아니오    | `~/.claude.json`          |

```bash
# 원격 HTTP 서버 (SSE만 지원하는 서버도 같은 명령으로 자동 전환)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 로컬 stdio 서버, 환경 변수 전달
claude mcp add --transport stdio --env API_KEY=... myserver -- npx my-mcp-server

# 팀 공유용으로 .mcp.json에 기록
claude mcp add --transport http shared-server --scope project https://example.com/mcp

# 관리
claude mcp list
claude mcp get notion
claude mcp remove notion
```

- 세션 안에서는 `/mcp`로 연결 상태와 OAuth 인증을 관리합니다.
- API 키를 `.mcp.json`에 직접 쓰지 않습니다. 커밋되는 파일이므로 환경 변수로 전달합니다.
- MCP 서버는 내 권한으로 외부 시스템에 접근하므로 출처가 확인된 서버만 연결합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Plugins

Plugin은 skill·subagent·hook·MCP 서버를 하나로 묶어 배포하는 단위입니다.

```bash
# 세션 안에서: 공식 marketplace의 plugin 설치 (상세 화면에서 검토 후 설치)
/plugin install commit-commands@claude-plugins-official

# 셸에서 세션 없이 설치 (설치 스크립트용)
claude plugin install commit-commands@claude-plugins-official
```

- 공식 marketplace는 처음 시작할 때 자동으로 추가됩니다. 다른 marketplace는 먼저 추가해야 합니다.
- 프로젝트 범위로 설치하면 `.claude/settings.json`에 기록되어, 커밋 후 저장소 사용자 모두에게 활성화됩니다.
- plugin skill은 `/plugin-name:skill-name`으로 호출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 원칙

- 팀 규칙은 `AGENTS.md`·`CLAUDE.md`·`.claude/settings.json`에 두고 버전 관리합니다. 개인 설정은 `~/.claude/`와 `*.local.*` 파일에 둡니다.
- 반드시 지켜야 하는 규칙(비밀 파일 접근 금지, 원격 push 금지 등)은 지침 문장이 아니라 deny 규칙과 PreToolUse hook으로 강제합니다.
- 다른 사람이 커밋한 hook·MCP·plugin은 실행 전에 내용을 검토합니다. 비대화형 `claude -p`는 신뢰 확인 없이 프로젝트 hook과 MCP를 실행하므로 외부 코드에서는 `--bare`를 씁니다.
- skill과 subagent는 `description`을 구체적으로 써야 Claude가 적절한 시점에 사용합니다.
- 컨텍스트가 커지면 품질이 떨어지므로 `CLAUDE.md`는 핵심 규칙만 두고, 세부 절차는 skill이나 rules로 분리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 설정·확장 기능 검증 근거 노트
- Memory (CLAUDE.md): [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) — ★★★☆☆
- Settings: [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) — ★★★☆☆
- Skills: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) — ★★★☆☆
- Hooks guide: [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide) — ★★★☆☆
- Subagents: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents) — ★★★☆☆
- MCP: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp) — ★★★☆☆
- Plugins: [code.claude.com/docs/en/plugins/overview](https://code.claude.com/docs/en/plugins/overview) — ★★★☆☆
- Agent Skills 표준: [agentskills.io](https://agentskills.io) — ★★☆☆☆

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

**마지막 업데이트**: 2026-10-14

© 2026 siasia86. Licensed under CC BY 4.0.
