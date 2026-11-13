# MAIN-20261113-01 AX 환경 구축 참고 문서 후보

```
CANDIDATES
├── ✅ 검증 완료 후보 28건의 공식 주소·게시일 또는 버전 확인(2026-11-13)
├── ✅ 검증 완료 권장 묶음 4개 문서 작성(사용자 선택, 2026-11-13)
├── 🟡 확인 대기 일부 게시일·라이선스 미확인(5절)
└── 🔵 참고      공개 본문 폴더 미작성, 단계 0 기록만
```

## 1. 요청과 범위

AX-HUB-20 단계 0으로 AX 환경 구축에 참고할 공식 문서 후보를 추천합니다. 이 기록은 후보 목록이며 `07_ai_transformation/`·`_reference/`·`06_career/`의 본문은 쓰지 않았습니다. 사용자가 고른 문서는 단계 1에서 reference 문서로 작성합니다.

놓을 자리는 [07 README](../../../../07_ai_transformation/README.md)의 나누는 기준을 따릅니다. 도구와 무관한 방법은 07, 공식 원문 정리는 `_reference/`, 특정 도구 사용법은 `06_career/ai_tools/`입니다. 이미 같은 도구의 공식 노트가 있으면 새 문서 대신 기존 노트의 절을 넓히는 "기존 갱신"으로 적었습니다.

## 2. 후보 목록

확인일은 모두 2026-11-13입니다. 주소는 공식 사이트에서 직접 열어 확인했고, 버전 표기가 없는 문서는 게시일이나 저장소 최근 갱신일을 적었습니다.

### 2.1. 저장소 지침 파일

| 번호 | 제목·발행처                                                                                                 | 게시일·버전                                 | AX 환경에서 쓰는 곳                                   | 자리                 | 우선 | 32 기존 문서와 겹침                                    |
|------|-------------------------------------------------------------------------------------------------------------|---------------------------------------------|-------------------------------------------------------|----------------------|------|--------------------------------------------------------|
| 1    | [AGENTS.md](https://agents.md/) — Agentic AI Foundation(Linux Foundation)                                   | 버전 표기 없음, 저장소 최근 갱신 2026-09-10 | 도구 공통 지침 파일 관례, 하위 파일 우선, 사용자 우선 | `_reference/` 묶음 1 | 상   | harness 6절 AGENTS.md 예시, markdown patterns 1절 일부 |
| 2    | [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) — OpenAI | 버전 표기 없음                              | Codex 탐색 순서, `AGENTS.override.md`, 32 KiB 한도    | `_reference/` 묶음 1 | 상   | Codex CLI 노트 7절, harness 참고 자료 링크             |
| 3    | [Store instructions and memories](https://code.claude.com/docs/en/memory) — Anthropic                       | 버전 표기 없음                              | CLAUDE.md 계층, `@` import, rules, 자동 메모리        | `_reference/` 묶음 1 | 상   | Claude Code 노트 7절, Claude 확장 가이드 1절           |

### 2.2. Agent skill

| 번호 | 제목·발행처                                                                                                                                                   | 게시일·버전                                 | AX 환경에서 쓰는 곳                                  | 자리                    | 우선 | 32 기존 문서와 겹침                                       |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|------------------------------------------------------|-------------------------|------|-----------------------------------------------------------|
| 4    | [Agent Skills Specification](https://agentskills.io/specification) — agentskills                                                                              | 버전 표기 없음, 저장소 최근 갱신 2026-11-04 | `SKILL.md` 필드 제한, 동봉 폴더, 단계적 로딩, 검증기 | `_reference/`           | 상   | GitHub 참고 목록 1.3 저장소 행, markdown patterns 2·3·6절 |
| 5    | [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) — Anthropic | 2025-10-16                                  | skill 설계 의도, 신뢰하지 않는 skill의 위험          | `_reference/` 묶음 2    | 중   | markdown patterns 2절                                     |
| 6    | [Skills](https://code.claude.com/docs/en/skills)(Anthropic), [Build skills](https://learn.chatgpt.com/docs/build-skills)(OpenAI)                              | 버전 표기 없음                              | 도구별 skill 위치·호출 방식                          | `_reference/` 기존 갱신 | 하   | 두 노트 8절, Claude 확장 가이드 4절, Codex skill 가이드   |

### 2.3. Hook·권한·설정

| 번호 | 제목·발행처                                                                                                                                                                                                  | 게시일·버전    | AX 환경에서 쓰는 곳                                | 자리                    | 우선 | 32 기존 문서와 겹침                                      |
|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|----------------------------------------------------|-------------------------|------|----------------------------------------------------------|
| 7    | [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — Anthropic                                                                                                                          | 버전 표기 없음 | 지침·skill·hook·subagent·MCP 선택 기준과 문맥 비용 | `_reference/` 기존 갱신 | 상   | Claude 확장 가이드 3절 기능 선택                         |
| 8    | [Hooks](https://code.claude.com/docs/en/hooks), [Permissions](https://code.claude.com/docs/en/permissions), [Settings](https://code.claude.com/docs/en/settings) — Anthropic                                 | 버전 표기 없음 | 도구 호출 전 차단, 권한 규칙, 설정 계층            | `_reference/` 기존 갱신 | 상   | Claude Code 노트 6~8절(hooks reference·permissions 없음) |
| 9    | [Hooks](https://learn.chatgpt.com/docs/hooks), [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules), [Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) — OpenAI | 버전 표기 없음 | Codex hook 이벤트, 명령 규칙, 승인·샌드박스        | `_reference/` 기존 갱신 | 상   | Codex CLI 노트 5절(hook 없음)                            |

### 2.4. 하위 에이전트·여러 세션

| 번호 | 제목·발행처                                                                                                                                                                                                         | 게시일·버전    | AX 환경에서 쓰는 곳                               | 자리                    | 우선 | 32 기존 문서와 겹침                     |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|---------------------------------------------------|-------------------------|------|-----------------------------------------|
| 10   | [Subagents](https://code.claude.com/docs/en/sub-agents), [Agent teams](https://code.claude.com/docs/en/agent-teams), [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) — Anthropic | 버전 표기 없음 | 문맥 분리, 병렬 작업, 세션 간 메시지와 권한 경계  | `_reference/` 기존 갱신 | 중   | Claude 확장 가이드 6절, 노트 8절 링크만 |
| 11   | [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) — OpenAI                                                                                                                                  | 버전 표기 없음 | Codex 에이전트 정의 파일, 동시 실행 수, 승인 상속 | `_reference/` 기존 갱신 | 중   | 없음                                    |
| 12   | [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system) — Anthropic                                                                                          | 2025-06-13     | 지휘·하위 에이전트 구성의 효과와 토큰 비용        | 07                      | 중   | loop 2.5절 Maker·Checker 일부           |

### 2.5. 모델·추론 단계 선택

| 번호 | 제목·발행처                                                                                                                                                                              | 게시일·버전    | AX 환경에서 쓰는 곳                           | 자리                    | 우선 | 32 기존 문서와 겹침                             |
|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|-----------------------------------------------|-------------------------|------|-------------------------------------------------|
| 13   | [Choosing the right model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model), [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) — Anthropic | 버전 표기 없음 | 모델 선택 기준, effort 5단계와 모델별 기본값  | `_reference/` 기존 갱신 | 중   | Claude 모델 가이드 3절, Claude Code 노트 2·10절 |
| 14   | [Model selection](https://learn.chatgpt.com/docs/model-selection) — OpenAI                                                                                                               | 버전 표기 없음 | 합격 기준을 먼저 정하고 가장 가벼운 설정 선택 | `_reference/` 기존 갱신 | 중   | Codex CLI 노트 Models 링크만                    |

### 2.6. 문맥 관리

| 번호 | 제목·발행처                                                                                                                               | 게시일·버전    | AX 환경에서 쓰는 곳                                | 자리                    | 우선 | 32 기존 문서와 겹침                           |
|------|-------------------------------------------------------------------------------------------------------------------------------------------|----------------|----------------------------------------------------|-------------------------|------|-----------------------------------------------|
| 15   | [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) — Anthropic | 2025-09-29     | 문맥 부패, 요약, 구조화된 메모, 하위 에이전트 분리 | 07                      | 상   | loop 3절 메모리 일부, GitHub 참고 목록 1.1 행 |
| 16   | [Explore the context window](https://code.claude.com/docs/en/context-window) — Anthropic                                                  | 버전 표기 없음 | 요약 뒤 다시 읽히는 것과 사라지는 것               | `_reference/` 기존 갱신 | 상   | 없음                                          |

### 2.7. 에이전트 설계 일반

| 번호 | 제목·발행처                                                                                                                                            | 게시일·버전    | AX 환경에서 쓰는 곳                                 | 자리                    | 우선 | 32 기존 문서와 겹침                   |
|------|--------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|-----------------------------------------------------|-------------------------|------|---------------------------------------|
| 17   | [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic                                                  | 2024-12-19     | 단순성 우선, workflow와 agent 구분, 도구 설계       | 07                      | 상   | harness 4절 Anthropic 접근법(다른 글) |
| 18   | [Writing effective tools for AI agents](https://www.anthropic.com/research/writing-tools-for-agents) — Anthropic                                       | 2025-09-11     | 도구 수 줄이기, 평가로 도구 개선                    | 07                      | 하   | 없음                                  |
| 19   | [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) — OpenAI         | 게시일 미확인  | 모델·도구·지침 구성, 지휘 형태, 안전장치, 사람 확인 | 07                      | 중   | 없음                                  |
| 20   | [Best practices](https://code.claude.com/docs/en/best-practices)(Anthropic), [Best practices](https://learn.chatgpt.com/guides/best-practices)(OpenAI) | 버전 표기 없음 | 두 도구의 권장 작업 방식 비교                       | `_reference/` 기존 갱신 | 중   | Claude Code 노트 링크만               |

### 2.8. Codex CLI 지침·설정

| 번호 | 제목·발행처                                                                                   | 게시일·버전    | AX 환경에서 쓰는 곳             | 자리                    | 우선 | 32 기존 문서와 겹침                        |
|------|-----------------------------------------------------------------------------------------------|----------------|---------------------------------|-------------------------|------|--------------------------------------------|
| 21   | [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced) — OpenAI | 버전 표기 없음 | profile, 저장소별 설정, 고급 키 | `_reference/` 기존 갱신 | 중   | Codex CLI 노트 7절(basic·reference만 링크) |

### 2.9. 계획의 단계·관문과 교차 검토

| 번호 | 제목·발행처                                                                                                                                 | 게시일·버전             | AX 환경에서 쓰는 곳                      | 자리                    | 우선 | 32 기존 문서와 겹침            |
|------|---------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|------------------------------------------|-------------------------|------|--------------------------------|
| 22   | [Spec Kit](https://github.com/github/spec-kit) — GitHub                                                                                     | v1.4.0(2026-11-10), MIT | 명세 → 계획 → 작업 단계와 관문           | 07                      | 중   | AI 개발 요청 양식 일부         |
| 23   | [Plan mode](https://code.claude.com/docs/en/permission-modes)(Anthropic), [Code review](https://learn.chatgpt.com/docs/code-review)(OpenAI) | 버전 표기 없음          | 실행 전 계획 확인, 다른 도구로 결과 검토 | `_reference/` 기존 갱신 | 중   | Claude Code 노트 6절 권한 모드 |

### 2.10. Git 운영과 검사

| 번호 | 제목·발행처                                                                                                                  | 게시일·버전                            | AX 환경에서 쓰는 곳            | 자리          | 우선 | 32 기존 문서와 겹침         |
|------|------------------------------------------------------------------------------------------------------------------------------|----------------------------------------|--------------------------------|---------------|------|-----------------------------|
| 24   | [About secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning) — GitHub          | 버전 표기 없음                         | 원격 저장소의 비밀 정보 검출   | `_reference/` | 하   | Gitleaks 노트               |
| 25   | [markdownlint](https://github.com/DavidAnson/markdownlint)(MIT), [pre-commit](https://github.com/pre-commit/pre-commit)(MIT) | markdownlint 미확인, pre-commit v4.7.0 | commit 전 Markdown 검사 자동화 | `_reference/` | 하   | 없음(32는 자체 검사기 사용) |

### 2.11. 32 관점에서 더한 주제

| 번호 | 제목·발행처                                                                                                                                                                            | 게시일·버전    | AX 환경에서 쓰는 곳                                   | 자리                    | 우선 | 32 기존 문서와 겹침                        |
|------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|-------------------------------------------------------|-------------------------|------|--------------------------------------------|
| 26   | [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2026-07-28) — MCP 프로젝트                                                                        | 2026-07-28     | 외부 도구 연결 규격, 사용자 동의·도구 안전 원칙       | `_reference/`           | 중   | Claude Code 노트 MCP 링크, 확장 가이드 7절 |
| 27   | [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — OWASP GenAI Security Project                      | 2025-12-09     | 목표 탈취·도구 오용·메모리 오염 등 에이전트 위협 점검 | 07                      | 상   | markdown patterns 7절 보안 규칙 일부       |
| 28   | [Security](https://code.claude.com/docs/en/security), [Sandboxing](https://code.claude.com/docs/en/sandboxing)(Anthropic), [Security](https://learn.chatgpt.com/docs/security)(OpenAI) | 버전 표기 없음 | 두 도구의 격리·권한 보호 수단 비교                    | `_reference/` 기존 갱신 | 중   | Codex CLI 노트 5절 일부                    |

보고 양식은 일반 공식 자료로 맞는 후보를 찾지 못했습니다. 짧고 명확한 문장 기준이 필요하면 기존 [ASD-STE100 노트](../../../../_reference/asd_ste100_official_notes.md)를 씁니다.

## 3. 먼저 쓸 묶음

후보 7건을 문서 4개로 묶어 먼저 쓰기를 권합니다. 모든 AX 저장소가 처음 정하는 지침 파일과 skill 형식, 설계 원칙, 보안 점검을 덮습니다. 모두 1차 출처이고 32 기존 문서와 겹침이 적습니다.

| 순서 | 문서(가칭)                                             | 묶는 후보 | 이유                                             |
|------|--------------------------------------------------------|-----------|--------------------------------------------------|
| 1    | `_reference/agent_instruction_files_official_notes.md` | 1·2·3     | 도구별 지침 파일 탐색 규칙을 한 표로 비교        |
| 2    | `_reference/agent_skills_spec_official_notes.md`       | 4·5       | 공개 규격과 설계 의도, 32 skill 문서의 기준 출처 |
| 3    | `07_ai_transformation/agent_design_principles.md`      | 15·17     | 도구와 무관한 설계·문맥 관리 원칙                |
| 4    | `07_ai_transformation/agent_security_risks.md`         | 27        | 에이전트 위협 10개를 AX 환경 점검표로 바꿈       |

"기존 갱신" 후보(6~11·13·14·16·20·21·23·28)는 새 문서보다 해당 공식 노트의 절을 넓히는 편이 중복이 적습니다. 별도 묶음으로 고르면 됩니다.

2026-11-13 사용자가 묶음 1~4를 골라 작성했습니다. 작성 전 검토 지적에 따라 후보 1·2·3을 묶음 1, 5를 묶음 2의 `_reference/` 자리로 맞췄습니다. 새 노트에는 도구 간 비교와 규격만 두고 도구별 세부는 기존 Claude·Codex 노트를 가리킵니다. 20번은 07이 아닌 기존 갱신 후보로 옮겼고, 넘어가는 주소(Anthropic 글, GitHub Docs)는 최종 주소로, MCP 규격은 날짜 판 주소로 바꿨습니다.

## 4. 문서 하나의 양식 예시

```markdown
# Agent Skills 규격 공식 노트

| 항목   | 내용                                             |
|--------|--------------------------------------------------|
| 출처   | agentskills.io/specification                     |
| 확인일 | 2026-11-13                                       |
| 버전   | 표기 없음(저장소 최근 갱신 2026-11-04)           |

## 1. 요약

(3줄 이내, 원문 문장 복제 없이 자기 말로)

## 2. 핵심

(필드 제한 등 사실만 표로, 짧은 인용은 따옴표와 출처)

## 3. AX 환경 적용 방법

(32·각 저장소에서 어떻게 쓰는지, 검사 방법)

## 4. 출처

- 원문 링크와 확인일

## 5. 미확인

- 확인하지 못한 항목과 이유
```

## 5. 인용·저작권 메모와 미확인

| 출처 묶음                        | 확인한 표기                                  | 32에서 쓰는 방식               |
|----------------------------------|----------------------------------------------|--------------------------------|
| Anthropic·OpenAI 문서와 글       | 문서별 라이선스 표기 확인하지 않음           | 요약·링크, 한두 문장 인용만    |
| agents.md                        | 사이트 저작권 LF Projects, 저장소 MIT        | 요약·링크                      |
| agentskills                      | 저장소 Apache-2.0                            | 요약·링크, 필드 표는 사실 정리 |
| MCP 규격                         | 저장소 라이선스 판별 불가(NOASSERTION)       | 요약·링크                      |
| OWASP                            | 사이트 기본 CC BY-SA 4.0, 문서별 예외 미확인 | 항목 이름과 요약만, 출처 표기  |
| Spec Kit·markdownlint·pre-commit | MIT                                          | 요약·링크                      |
| GitHub Docs                      | 라이선스 확인하지 않음                       | 요약·링크                      |

미확인 항목:

- 19번 OpenAI PDF의 게시일과 판
- 25번 markdownlint 최신 버전(GitHub release 없음)
- OWASP 문서 자체의 라이선스 예외와 ASI01~ASI10 공식 항목 이름(다운로드 원문 미열람)
- Anthropic·OpenAI 문서의 문서별 이용 조건
- Codex 문서(2·9·11·14·21·23·28)는 공식 목록과 일부 본문만 확인했고 전체 본문은 단계 1에서 읽습니다.

---

**작성일**: 2026-11-13

**마지막 업데이트**: 2026-11-13

© 2026 siasia86. Licensed under CC BY 4.0.
