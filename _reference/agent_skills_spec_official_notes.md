---
name: agent-skills-spec-official-notes
description: Agent Skills 공개 규격(SKILL.md 필드·폴더·단계적 로딩·검증)과 Anthropic 설계 글 요약
tags:
  - agent-skills
  - skill-md
  - specification
  - ax
last_checked: 2026-11-13
sources:
  - https://agentskills.io/specification
  - https://github.com/agentskills/agentskills
  - https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
---

# Agent Skills 규격 공식 노트

| 항목               | 내용                                                                        |
|--------------------|-----------------------------------------------------------------------------|
| 출처               | agentskills.io Specification, Anthropic 글(2025-10-16 게시)                 |
| 확인일             | 2026-11-13                                                                  |
| 버전               | 규격 버전 표기 없음, agentskills 저장소 최근 갱신 2026-11-04                |
| 라이선스·인용 범위 | 규격 저장소 Apache-2.0, 필드 제한은 사실로 정리. Anthropic 글은 요약·링크만 |

## 1. 요약

Agent Skill은 `SKILL.md` 하나를 반드시 둔 폴더입니다. 에이전트는 시작할 때 이름과 설명만 읽고, 작업에 맞으면 본문을, 필요할 때 동봉 파일을 읽습니다. Anthropic이 처음 공개했고 2025-12-18에 여러 도구가 함께 쓰는 공개 규격으로 내놓았습니다.

## 2. SKILL.md 필드

| 필드            | 필수   | 제한                                                                         |
|-----------------|--------|------------------------------------------------------------------------------|
| `name`          | 예     | 1~64자, 소문자·숫자·하이픈, 양끝 하이픈과 연속 하이픈 금지, 폴더 이름과 같음 |
| `description`   | 예     | 1~1024자, 무엇을 하고 언제 쓰는지 적음                                       |
| `license`       | 아니오 | 라이선스 이름 또는 동봉 파일                                                 |
| `compatibility` | 아니오 | 1~500자, 필요한 환경이 있을 때만                                             |
| `metadata`      | 아니오 | 문자열 키와 문자열 값의 사전                                                 |
| `allowed-tools` | 아니오 | 미리 허용할 도구를 공백으로 구분, 실험 단계라 도구마다 지원이 다름           |

## 3. 폴더와 로딩

| 항목      | 규격 내용                                                                       |
|-----------|---------------------------------------------------------------------------------|
| 선택 폴더 | `scripts/`(실행 코드), `references/`(필요할 때 읽는 문서), `assets/`(양식·자료) |
| 1단계     | 시작 때 이름·설명만 읽음(약 100 토큰)                                           |
| 2단계     | 사용할 때 본문 전체를 읽음(5000 토큰 미만 권장)                                 |
| 3단계     | 동봉 파일은 필요할 때만 읽음                                                    |
| 본문 길이 | `SKILL.md`는 500줄 이하, 긴 내용은 별도 파일                                    |
| 파일 참조 | skill 폴더 기준 상대 경로, `SKILL.md`에서 한 단계 깊이까지                      |
| 검증      | 참조 도구 `skills-ref validate <폴더>`                                          |

## 4. 설계 의도와 보안 (Anthropic 글)

작성 권고는 네 가지입니다. 대표 과제를 먼저 돌려 막히는 곳을 찾고, 본문이 커지면 파일을 나누고, 실제 사용을 보며 이름·설명을 다듬고, 성공과 실수를 skill에 다시 반영합니다.

보안 권고는 믿을 수 있는 출처의 skill만 설치하고, 그렇지 않은 skill은 동봉 스크립트·의존성·외부 접속 지시까지 읽은 뒤 쓰라는 것입니다.

## 5. 도구별 세부

- Claude Code skill 위치·호출: [Claude Code 노트 8절 Skills](claude_code_official_notes.md#skills-skills), [Claude Code 확장 가이드 4절](../06_career/ai_tools/claude/claude_code_extensions_guide.md#4-skills)
- Codex skill 설정·배포: [Codex CLI 노트 8절](codex_cli_official_notes.md#8-skills-설정과-배포), [Codex Skills 설정 가이드](../06_career/ai_tools/codex/codex_skills_setup_guide.md)
- 규격을 따르는 공개 skill 저장소: [GitHub 참고 목록 1.3절](github_references.md#13-공식-명세-설치-도구와-탐색-목록)

## 6. 미확인

- 규격 문서에 판 번호나 변경 이력 표기가 없어, 필드 제한이 언제 바뀌었는지 확인하지 못했습니다.
- `allowed-tools`를 Claude Code·Codex가 각각 어떻게 해석하는지는 이 노트에서 대조하지 않았습니다.

## 7. 공식 자료

- Agent Skills Specification: https://agentskills.io/specification
- 규격 저장소: https://github.com/agentskills/agentskills
- Equipping agents for the real world with Agent Skills (Anthropic): https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills

---

**작성일**: 2026-11-13

**마지막 업데이트**: 2026-11-13

© 2026 siasia86. Licensed under CC BY 4.0.
