---
name: agent-instruction-files-official-notes
description: AGENTS.md 공통 형식과 Codex·Claude Code 지침 파일 탐색 규칙의 도구 간 비교 노트
tags:
  - agents-md
  - claude-md
  - codex
  - claude-code
  - ax
last_checked: 2026-11-13
sources:
  - https://agents.md/
  - https://learn.chatgpt.com/docs/agent-configuration/agents-md
  - https://code.claude.com/docs/en/memory
---

# 에이전트 지침 파일 공식 노트

| 항목               | 내용                                                                                     |
|--------------------|------------------------------------------------------------------------------------------|
| 출처               | agents.md, OpenAI Codex 문서(AGENTS.md), Claude Code 문서(memory)                        |
| 확인일             | 2026-11-13                                                                               |
| 버전               | 세 문서 모두 버전 표기 없음, agents.md 저장소 최근 갱신 2026-09-10                       |
| 라이선스·인용 범위 | agents.md 사이트는 LF Projects 저작권, 저장소는 MIT. OpenAI·Anthropic 문서는 요약·링크만 |

## 1. 요약

AGENTS.md는 코딩 에이전트에게 저장소 맥락을 전하는 Markdown 형식이며 필수 항목이 없습니다. Codex는 AGENTS.md를 직접 읽고, Claude Code는 CLAUDE.md를 기본으로 읽되 CLAUDE.md가 없으면 AGENTS.md를 읽습니다. 이 노트는 두 도구의 차이만 비교하고, 도구별 세부 설정은 기존 노트를 따릅니다.

## 2. 도구 간 비교

| 항목               | AGENTS.md 공통 관례              | Codex                                                 | Claude Code                                                      |
|--------------------|----------------------------------|-------------------------------------------------------|------------------------------------------------------------------|
| 기본 파일          | `AGENTS.md`                      | `AGENTS.md`, 같은 폴더의 `AGENTS.override.md`가 우선  | `CLAUDE.md` 또는 `.claude/CLAUDE.md`, 개인용 `CLAUDE.local.md`   |
| 전역·조직 파일     | 정의 없음                        | `~/.codex`(`CODEX_HOME`)의 전역 파일                  | 사용자 `~/.claude/CLAUDE.md`, 조직 관리 정책 파일                |
| 여러 파일 처리     | 가장 가까운 파일이 우선          | 루트부터 현재 폴더까지 합치고 가까운 파일이 뒤에 놓임 | 덮어쓰지 않고 합치며 루트에서 작업 폴더 순으로 놓임              |
| 하위 폴더          | 중첩 파일 허용                   | 현재 폴더까지의 경로만 포함                           | 하위 폴더 파일은 그 폴더 파일을 다룰 때 읽음                     |
| 다른 파일 가져오기 | 정의 없음                        | 정의 없음                                             | `@경로` 가져오기, 최대 4단계                                     |
| 크기               | 정의 없음                        | 합계 기본 32 KiB(`project_doc_max_bytes`)             | 파일당 200줄 이하 권장                                           |
| 상대 우선순위      | 사용자 채팅 지시가 파일보다 우선 | 문서에 별도 표기 없음                                 | 지침은 강제 설정이 아닌 문맥이며, 반드시 막을 일은 hook으로 처리 |

## 3. 함께 쓰는 방법

두 도구를 같은 저장소에서 쓸 때 Claude Code 문서가 정한 조합은 다음과 같습니다(Claude Code v2.1.277 이상).

| 저장소에 있는 파일                    | Claude Code가 읽는 것            |
|---------------------------------------|----------------------------------|
| `AGENTS.md`만 있음                    | `AGENTS.md`                      |
| `AGENTS.md`와 `CLAUDE.md`가 함께 있음 | `CLAUDE.md`만                    |
| `CLAUDE.md`가 `AGENTS.md`를 가져옴    | `CLAUDE.md`와 가져온 `AGENTS.md` |

공통 규칙을 `AGENTS.md` 한 곳에 두고 `CLAUDE.md`에서 가져오면 두 도구가 같은 원본을 읽습니다. Claude Code 전용 내용만 `CLAUDE.md`에 더합니다.

## 4. 도구별 세부

- Codex 지침 파일·설정: [Codex CLI 노트 7절](codex_cli_official_notes.md#7-설정-및-지침-파일)
- Claude Code 지침 파일·설정: [Claude Code 노트 7절](claude_code_official_notes.md#7-설정과-지침-파일-settings-memory)
- Claude Code 지침 파일 사용법: [Claude Code 확장 가이드 1절](../06_career/ai_tools/claude/claude_code_extensions_guide.md#1-지침-파일)

## 5. 미확인

- Codex 문서에서 사용자 채팅 지시와 AGENTS.md의 우선순위를 직접 적은 문장은 찾지 못했습니다.
- agents.md 사이트 본문의 라이선스는 사이트에 따로 표기되지 않았고 저장소 MIT만 확인했습니다.

## 6. 공식 자료

- AGENTS.md: https://agents.md/
- Custom instructions with AGENTS.md (OpenAI): https://learn.chatgpt.com/docs/agent-configuration/agents-md
- How Claude remembers your project (Anthropic): https://code.claude.com/docs/en/memory

---

**작성일**: 2026-11-13

**마지막 업데이트**: 2026-11-13

© 2026 siasia86. Licensed under CC BY 4.0.
