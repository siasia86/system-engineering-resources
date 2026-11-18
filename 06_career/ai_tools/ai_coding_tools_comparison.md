# AI 코딩 도구 비교
<!-- reference: _reference/ai_coding_tools_official_notes.md, _reference/claude_code_official_notes.md -->

주요 AI 코딩 도구 9종의 형태·기능·요금·기반 모델을 비교하고, 상황별·직무별 선택 기준을 정리합니다. 요금과 모델은 2026-11-18에 각 공식 페이지에서 다시 확인했으며, 확인일이 다른 항목은 그 자리에 날짜를 적었습니다. 검증 근거는 [AI 코딩 도구 참조 노트](../../_reference/ai_coding_tools_official_notes.md)에 있습니다.

## 목차

| 섹션                                                                                                                                      |
|-------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 도구별 정리](#2-도구별-정리) / [3. 기능 비교](#3-기능-비교)                                                      |
| [4. 가격 비교](#4-가격-비교) / [5. 벤치마크](#5-벤치마크) / [6. 선택 가이드](#6-선택-가이드) / [7. 직무별 권장 도구](#7-직무별-권장-도구) |

---

## 1. 개요

| 도구                         | 제조사                   | 형태                                    | 기반 모델                              |
|------------------------------|--------------------------|-----------------------------------------|----------------------------------------|
| Kiro                         | AWS                      | AI IDE / CLI / Web / Mobile             | Claude Opus 5.5·Sonnet 5.5, GPT-5.6 등 |
| Claude Code                  | Anthropic                | AI 코딩 에이전트 (CLI/IDE/Web/Desktop)  | Claude 계열                            |
| OpenAI Agents SDK            | OpenAI                   | 멀티에이전트 프레임워크 (Python/TS SDK) | GPT-6 계열 등 여러 제공자              |
| Cursor                       | Anysphere                | AI IDE (VS Code fork)                   | Claude / GPT / Gemini / Grok 멀티모델  |
| GitHub Copilot               | Microsoft                | IDE 플러그인 + CLI                      | GPT / Claude 등 멀티모델               |
| Devin (Desktop, 구 Windsurf) | Cognition AI             | 자율 에이전트 + AI IDE                  | SWE 계열(자체) + Claude / GPT / Gemini |
| Amp                          | Amp Frontier Corp.       | AI 코딩 에이전트 (CLI/Web/Mobile)       | Claude / GPT / Gemini 멀티모델         |
| Aider                        | Paul Gauthier (오픈소스) | 터미널 CLI                              | API 키 방식 멀티모델                   |
| v0 / Bolt.new                | Vercel / StackBlitz      | UI·풀스택 생성 (웹)                     | 제공사 선택 모델                       |

2026-11-18 변경 요약:

- Windsurf는 **Devin Desktop**으로 이름이 바뀌었습니다. 공식 페이지는 "이름과 브랜딩만 바뀌며 플랜과 가격은 유지"라고 안내합니다. `windsurf.com`은 `devin.ai/desktop`으로 영구 이동(308)합니다.
- OpenAI 공식 모델 목록의 주력이 GPT-6 계열(GPT-6.2 Astra·6.2 Sol·6.1 Terra·6 Luna)로 바뀌었습니다.
- GitHub Copilot 사용량 단위가 GitHub AI Credits(1크레딧 = $0.01)로 표기됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 도구별 정리

### Kiro

AWS가 만든 AI 개발 도구입니다. VS Code 기반 IDE(`kiro`), 터미널 CLI(`kiro-cli`), 웹, 모바일 네 가지 형태로 제공됩니다. Agents / Skills / Hooks / Steering files를 마크다운·JSON 파일로 정의하는 방식이 특징입니다.

| 기능             | 내용                                                                            |
|------------------|---------------------------------------------------------------------------------|
| Spec-driven 개발 | 요구사항 → 설계 → 구현 흐름                                                     |
| Agents           | `.kiro/agents/*.json`으로 역할·도구·시스템 프롬프트 정의                        |
| Skills           | `.kiro/skills/SKILL.md`로 작업 패턴 재사용                                      |
| Hooks            | 파일 저장, 명령 실행 등 이벤트 기반 자동화                                      |
| Steering files   | 프로젝트 전반 규칙                                                              |
| 기타             | 병렬 에이전트, MCP, ACP(Agent Client Protocol), AWS 계정 통합, CI headless 모드 |

#### 지원 모델 (일부)

공식 모델 페이지(2026-11-16 갱신)에서 골랐습니다. 배율은 Auto(1.0x) 기준 크레딧 소모 배수입니다.

| 모델                                  | 크레딧 배율        | 플랜               |
|---------------------------------------|--------------------|--------------------|
| Claude Opus 5.5                       | 2.0x               | Pro 이상           |
| Claude Sonnet 5.5                     | 1.3x               | Pro 이상           |
| Claude Haiku 5.5                      | 0.06x              | Pro 이상           |
| Claude Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | 2.2x               | Pro 이상           |
| Claude Sonnet 5 / 4.6                 | 1.3x               | Pro 이상           |
| Claude Sonnet 4.5 / 4.0               | 1.3x               | Free 이상          |
| GPT-5.6 Sol / Terra / Luna            | 4.4x / 2.2x / 0.6x | Pro 이상           |
| Claude Haiku 4.5                      | 0.4x               | Pro 이상           |
| DeepSeek 3.2                          | 0.25x              | Free 이상 (미국만) |
| Qwen3 Coder Next                      | 0.05x              | Free 이상          |
| Auto                                  | 1.0x               | Free 이상          |

🟡 GPT-5.6은 272K 토큰, Haiku 5.5는 100K 토큰을 넘으면 더 높은 배율이 적용됩니다. Claude Fable 5.1(6x)은 모델 거버넌스를 켠 Enterprise 조직, US East에서만 제공됩니다. Kiro 목록에는 아직 GPT-6 계열이 없습니다.

### Claude Code

Anthropic이 만든 AI 코딩 에이전트입니다. 터미널 CLI, IDE 확장(VS Code·JetBrains), 데스크톱 앱, 웹, 모바일에서 동작합니다. 유료 플랜(Pro·Max·Ultra·Team·Enterprise)에 포함되며 채팅과 사용량 한도를 공유합니다. 무료 플랜에는 포함되지 않습니다. 상세 내용은 [Claude Code 공통 개념](claude/claude_code_concepts.md)을 참고합니다.

| 기능            | 내용                                                                                         |
|-----------------|----------------------------------------------------------------------------------------------|
| 작업 방식       | 코드베이스 파일을 직접 읽고 편집, Git·테스트·셸 명령 실행                                    |
| 지침 파일       | `CLAUDE.md` (없으면 `AGENTS.md`를 읽음)                                                      |
| 권한 모드       | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`                     |
| 확장            | Skills(`.claude/skills/`), Hooks(이벤트 30여 종), Subagents(`.claude/agents/`), Plugins, MCP |
| 연동            | GitHub Actions, GitLab CI/CD, Slack, Chrome                                                  |
| 클라우드 제공자 | Amazon Bedrock, Google Cloud, Microsoft Foundry (모델은 Claude 계열)                         |

| 접근 방법                          | 조건                                     |
|------------------------------------|------------------------------------------|
| Pro·Max·Ultra·Team·Enterprise 구독 | 구독에 포함 (채팅과 사용량 한도 공유)    |
| Claude Console API 키              | `ANTHROPIC_API_KEY` 환경 변수, 종량제    |
| Bedrock·Google Cloud·Foundry       | `CLAUDE_CODE_USE_BEDROCK=1` 등 환경 변수 |

🟡 기능 항목은 2026-10-14 공식 문서 기준이며, 요금은 2026-11-18에 다시 확인했습니다(4절).

### OpenAI Agents SDK

OpenAI가 제공하는 오픈소스(MIT) 멀티에이전트 프레임워크입니다. Python/TypeScript 코드로 에이전트·도구·가드레일을 정의하며 여러 LLM 제공자와 연동할 수 있습니다. Python 판 최신 릴리스는 v0.25.0(2026-11-18)입니다.

| 기능              | 내용                                   |
|-------------------|----------------------------------------|
| Agents            | 코드로 에이전트·도구·가드레일 정의     |
| SandboxAgent      | 파일·명령·Git 작업을 컨테이너에서 실행 |
| Handoffs          | 에이전트 간 작업 위임                  |
| Guardrails        | 입출력 유효성 검사                     |
| Sessions          | 실행 간 대화 이력 자동 관리            |
| Human in the loop | 실행 중 사람 개입                      |
| Tracing           | 실행 추적·디버깅                       |
| 기타              | 음성 에이전트, MCP, Function Calling   |

#### OpenAI 주력 모델 (2026-11-18)

| 모델          | 입력 가격 | 출력 가격 | 컨텍스트 |
|---------------|-----------|-----------|----------|
| GPT-6.2 Astra | $8/1M     | $40/1M    | 1.05M    |
| GPT-6.2 Sol   | $2/1M     | $10/1M    | 1.05M    |
| GPT-6.1 Terra | $1/1M     | $5/1M     | 1.05M    |
| GPT-6 Luna    | $0.10/1M  | $0.50/1M  | 1.05M    |

🟡 공식 모델 목록의 주력 표에 GPT-5.6 일반 모델은 더 이상 나오지 않습니다. 2026-11-09 확인 당시 GPT-5.6 Sol 가격은 $5.00/$30.00이었습니다.

### Cursor

Anysphere가 만든 VS Code fork 기반 AI IDE입니다. 여러 회사 모델을 함께 지원하며 코드 인식 채팅과 에이전트 모드를 제공합니다.

| 기능                      | 내용                                                                |
|---------------------------|---------------------------------------------------------------------|
| Tab                       | 다음 코드 예측 자동완성                                             |
| Agent 모드                | 파일 생성·수정·실행 자동 수행                                       |
| Cloud Agents              | 원격 서버에서 에이전트 자율 실행 (이전 Background Agent)            |
| Parallel Agents·Subagents | 여러 에이전트 동시 실행                                             |
| Rules                     | `.cursor/rules` (`.cursorrules`는 deprecated)                       |
| Skills                    | Agent Skills 표준(`SKILL.md`). Notepads는 Cursor 2.0에서 deprecated |
| Bugbot                    | PR 코드 리뷰 자동화                                                 |
| Cursor CLI                | 터미널·CI에서 에이전트 실행                                         |
| 기타                      | MCP, Marketplace, Automations                                       |

### GitHub Copilot

GitHub이 만든 AI 코딩 도구입니다. VS Code, JetBrains, Vim 등 대부분의 IDE와 터미널에서 동작합니다.

| 기능               | 내용                                                                                        |
|--------------------|---------------------------------------------------------------------------------------------|
| 자동완성           | 인라인 코드 완성, 다음 편집 제안 (유료 플랜은 크레딧 차감 없음)                             |
| Copilot Chat       | 코드 설명·리팩터링·테스트 생성                                                              |
| Coding Agent       | Issue → PR 자동 생성 (GitHub Actions 위에서 실행)                                           |
| Copilot CLI        | 터미널 코딩 에이전트(`copilot`). 이전 `gh copilot explain`·`suggest` 확장은 2025-10-25 종료 |
| Agent Skills·Hooks | `.github/skills/`의 `SKILL.md`, 이벤트 기반 자동화                                          |
| 기타               | MCP Registry, GitHub 생태계 통합, 기업 정책·콘텐츠 필터링                                   |

### Devin (Desktop, 구 Windsurf)

Cognition AI의 제품입니다. 2026-11-18 공식 페이지 기준으로 Windsurf IDE는 **Devin Desktop**으로 이름이 바뀌었고, 자율 에이전트 Devin과 같은 제품군·같은 요금표를 씁니다. JetBrains용 Windsurf 플러그인은 계속 내려받을 수 있습니다.

| 구성                        | 내용                                                                      |
|-----------------------------|---------------------------------------------------------------------------|
| Devin Desktop (구 Windsurf) | VS Code fork 기반 AI IDE. Tab 자동완성, 에이전트 작업, 로컬 에이전트 관리 |
| Devin Cloud                 | 클라우드에서 에이전트 자율 실행 (작성·테스트·PR)                          |
| Devin CLI                   | 터미널 접근                                                               |
| Devin Review                | PR 코드 리뷰 자동화                                                       |
| 모델                        | 자체 SWE 계열 + Claude / GPT / Gemini                                     |
| 기타                        | MCP, ACP 호환, 여러 에이전트 동시 관리                                    |

요금: Free $0, Pro $20/월, Max $200/월, Teams $80/월 + 정식 좌석당 $40/월, Enterprise 별도 문의(2026-11-18).

### Amp

Sourcegraph가 만들고 2025-12에 분사한 Amp Frontier Corporation의 AI 코딩 에이전트입니다. 웹, 터미널 CLI, 모바일로 제공되며 orbs(원격 컨테이너)에서 에이전트가 독립 실행됩니다.

| 기능   | 내용                                                                |
|--------|---------------------------------------------------------------------|
| Orbs   | 원격 컨테이너에서 에이전트 자율 실행. 자체 호스팅 orb·runner는 무료 |
| 플랫폼 | 웹, 터미널 CLI, 모바일                                              |
| 모델   | Claude / GPT / Gemini 등, BYOK 지원                                 |
| 연동   | GitHub, PR 자동화                                                   |

| 플랜       | 가격 (2026-11-18)                                                 |
|------------|-------------------------------------------------------------------|
| Hobby      | 무료 (Amp 호스팅 orb는 사용량 과금)                               |
| Megawatt   | $20/월 (Amp 호스팅 orb 45,000분 = 750시간 포함). 학생·교사 $10/월 |
| Gigawatt   | 공식 페이지에 별도 가격 표기 없음 (2026-07-27 확인 당시 $200/월)  |
| Teams      | 추가 요금 없음 (멤버별 플랜, 크레딧 공유)                         |
| Enterprise | 별도 문의                                                         |

### Aider

오픈소스(Apache-2.0) 터미널 AI 페어 프로그래밍 도구입니다. 로컬 git 저장소와 직접 연동해 코드 변경·커밋을 수행합니다. GitHub stars 약 50K, 최신 릴리스 v0.86.0(2025-08-09)입니다(2026-11-18 확인).

| 기능     | 내용                                                                 |
|----------|----------------------------------------------------------------------|
| 동작     | 터미널 CLI, 기존 에디터와 병행                                       |
| Git      | diff·commit 자동                                                     |
| 모델     | Claude / GPT / DeepSeek / Gemini 등 API 키 방식, Ollama 등 로컬 모델 |
| 벤치마크 | 자체 [LLM 코딩 리더보드](https://aider.chat/docs/leaderboards/) 운영 |
| 비용     | 무료. 사용하는 LLM API 비용만 발생                                   |

### v0 / Bolt.new

UI 컴포넌트와 풀스택 앱을 프롬프트로 생성하는 웹 기반 도구입니다. 범용 코딩 에이전트가 아니라 **웹 UI·앱 프로토타이핑** 특화 도구이며, 브라우저에서 바로 실행·배포할 수 있습니다.

| 도구     | 제조사     | 특화 영역                             | Free                  | 유료 (2026-11-18)                              |
|----------|------------|---------------------------------------|-----------------------|------------------------------------------------|
| v0       | Vercel     | React/Next.js UI 생성, Vercel 배포    | 하루 메시지 7개       | Plus $30/사용자/월, Business $100/사용자/월    |
| Bolt.new | StackBlitz | 풀스택 웹앱, 브라우저 내 Node.js 실행 | 월 1M 토큰(하루 300K) | Pro $25/월(월 10M 토큰부터), Teams $30/멤버/월 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기능 비교

### 핵심 기능

| 기능                 | Kiro          | Claude Code   | Cursor               | Copilot          |
|----------------------|---------------|---------------|----------------------|------------------|
| IDE 통합             | ✅ (기본)     | 🟡 (플러그인) | ✅ (기본)            | ✅ (플러그인)    |
| 터미널 CLI           | ✅            | ✅ (주력)     | ✅ (Cursor CLI)      | ✅ (Copilot CLI) |
| 자동완성 (Tab)       | ✅            | ❌            | ✅                   | ✅               |
| 에이전트 모드        | ✅            | ✅            | ✅                   | ✅               |
| 멀티에이전트         | 🟡            | ✅            | ✅                   | ❌               |
| MCP 지원             | ✅            | ✅            | ✅                   | ✅               |
| 커스텀 에이전트 정의 | ✅ (파일)     | ✅ (agents/)  | ✅ (.cursor/agents/) | 🟡               |
| Skills               | ✅            | ✅            | ✅                   | ✅               |
| Hooks                | ✅            | ✅            | ✅                   | ✅               |
| Git / PR 연동        | ✅            | ✅            | ✅                   | ✅ (주력)        |
| 멀티모델 선택        | ✅            | 🟡 (Claude만) | ✅                   | ✅               |
| AWS 통합             | ✅ (강점)     | ✅ (Bedrock)  | ❌                   | ❌               |
| GitHub Actions 통합  | ✅ (headless) | ✅            | ✅ (Cursor CLI)      | ✅ (강점)        |

✅ 지원, 🟡 부분 지원·별도 구성, ❌ 미지원입니다.

### 커스터마이징 방식

| 도구        | 방식                   | 진입 장벽 | 유연성 |
|-------------|------------------------|-----------|--------|
| Kiro        | 마크다운·JSON 파일     | 낮음      | 중간   |
| Claude Code | CLAUDE.md·Skills·Hooks | 낮음      | 중간   |
| Agents SDK  | Python/TS 코드         | 높음      | 높음   |
| Cursor      | .cursor/rules·Skills   | 낮음      | 중간   |
| Copilot     | 설정 UI + Skills       | 낮음      | 중간   |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 가격 비교

출처: 각 공식 요금 페이지 (2026-11-18 확인). 세금 별도, 월 결제 기준입니다.

### 개인 플랜

| 도구        | Free                 | 기본 유료                     | 고급 유료                            |
|-------------|----------------------|-------------------------------|--------------------------------------|
| Kiro        | $0 (월 50 크레딧)    | Pro $20 (월 1,000 크레딧)     | Pro+ $40 / Pro Max $100 / Power $200 |
| Claude Code | — (Free 플랜 미포함) | Pro $20 (연간 결제 시 월 $17) | Max $100 / Ultra $200                |
| Cursor      | 제한적 무료          | Plus $8 / Premium $30         | Super $100 / Ultra $200              |
| Copilot     | 월 2,000 completions | Pro $10                       | Pro+ $39 / Max $100                  |
| Devin       | $0                   | Pro $20                       | Max $200                             |

### 팀 플랜

| 도구          | 가격                                                                                                         |
|---------------|--------------------------------------------------------------------------------------------------------------|
| Kiro          | 좌석당 $20 (좌석당 500 크레딧, 2좌석 이상, 크레딧 공유)                                                      |
| Claude (Team) | Standard 좌석 $25 (연간 $20), Premium 좌석 $125 (연간 $100). Enterprise는 좌석당 $20(20좌석 이상) + API 요금 |
| Cursor        | Teams $30/사용자부터                                                                                         |
| Copilot       | Business·Enterprise는 영업 문의 (요금 페이지에 금액 미표기)                                                  |
| Devin         | $80/월 + 정식 좌석당 $40/월                                                                                  |

🟡 Kiro 유료 플랜의 추가 크레딧은 $0.04/크레딧입니다. Cursor Plus는 공유 사용량 풀이며 요금 페이지에 "Grok 모델만"으로 표기되어 있습니다. Copilot 유료 플랜의 포함 사용량은 GitHub AI Credits로 표기됩니다(Pro $15, Pro+ $70, Max $200 상당).

🟡 OpenAI Agents SDK는 IDE형 도구가 아니므로 이 표에서 뺐습니다. 비용은 사용한 모델의 API 토큰 종량제입니다(2절 모델 표).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 벤치마크

도구가 아니라 **기반 모델** 기준 순위입니다. 실제 도구 성능은 기반 모델, 시스템 프롬프트, 컨텍스트 처리 방식에 따라 달라집니다.

### 코딩

출처: [benchlm.ai/best/coding](https://benchlm.ai/best/coding) (페이지 표기 "Last verified: November 18, 2026")

| 순위 | 모델              | 제조사    | 점수 |
|------|-------------------|-----------|------|
| 1    | Claude Fable 5.2  | Anthropic | 89.7 |
| 2    | Gemini 4 Carbon   | Google    | 83.4 |
| 3    | Claude Opus 5.5   | Anthropic | 82.9 |
| 4    | Claude Sonnet 5.5 | Anthropic | 80.6 |
| 5    | GPT-6 Astra       | OpenAI    | 78.4 |

### Computer Use (GUI 에이전트)

출처: [benchlm.ai/best/computer-use](https://benchlm.ai/best/computer-use) (2026-11-18 갱신)

| 순위 | 모델            | 제조사    | 점수 |
|------|-----------------|-----------|------|
| 1    | Claude Opus 4.8 | Anthropic | 85.2 |
| 2    | Qwen3.8 Max     | Alibaba   | 82.7 |
| 3    | GPT-5.4         | OpenAI    | 79.2 |
| 4    | Qwen3.8-27B     | Alibaba   | 78.9 |
| 5    | Claude Opus 4.6 | Anthropic | 76.9 |

🟡 BenchLM은 여러 공개 벤치마크를 묶은 제3자 집계입니다. 순위는 자주 바뀌므로 도구 선택의 참고 자료로만 씁니다. Claude 모델 라인업은 [Claude 모델 가이드](claude/claude_models_guide.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 선택 가이드

| 상황                                    | 추천 도구                                  | 이유                                                   |
|-----------------------------------------|--------------------------------------------|--------------------------------------------------------|
| AWS 인프라 작업 + 에이전트 커스터마이징 | **Kiro**                                   | AWS 통합, Skills/Hooks, 파일 기반 설정                 |
| 터미널 중심 + 코드베이스 전체 수정      | **Claude Code**                            | CLI 주력, CLAUDE.md, 구독에 포함                       |
| 멀티에이전트 프로덕션 시스템 구축       | **Agents SDK**                             | Handoffs·Guardrails, 코드 기반 유연성, 여러 LLM 제공자 |
| 자동완성 + 멀티모델 + IDE               | **Cursor**                                 | Tab 자동완성, 여러 회사 모델                           |
| GitHub 중심 + PR 자동화 + 기업 정책     | **Copilot**                                | Issue→PR, GitHub Actions 통합, 기업 정책               |
| 작업을 통째로 맡기는 자율 위임          | **Devin**                                  | 클라우드 에이전트가 PR까지 수행                        |
| 비용 최소화 (개인·학습)                 | **Copilot Free**, **Kiro Free**, **Aider** | 무료로 시작 가능                                       |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 직무별 권장 도구

작업 유형이 아닌 **직무 관점**의 권장 조합입니다. 단일 도구보다 주력 + 보조 조합이 실용적입니다.

### 주력 + 보조 조합

| 직무                        | 주력 도구       | 보조 도구                  | 이유                                                                   |
|-----------------------------|-----------------|----------------------------|------------------------------------------------------------------------|
| 시스템 엔지니어 (SE/SRE)    | **Kiro**        | Claude Code                | AWS/인프라 통합, Skills·Hooks로 반복 작업 자동화, CLI로 서버 직접 작업 |
| DevOps / 플랫폼 엔지니어    | **Kiro**        | Copilot + Agents SDK       | CI headless 모드, GitHub Actions 통합, 멀티에이전트 파이프라인         |
| 백엔드 개발자               | **Cursor**      | Claude Code                | Tab 자동완성 + 멀티모델, 코드베이스 전체 리팩터링은 Claude Code        |
| 프론트엔드 개발자           | **Cursor**      | v0                         | React/Next.js 자동완성, UI 초안은 v0로 생성 후 편집                    |
| 풀스택 개발자               | **Cursor**      | Bolt.new + Devin           | 프로토타입은 Bolt.new, 구현은 Cursor, 반복 태스크는 Devin 위임         |
| DBA                         | **Claude Code** | Kiro                       | SQL 분석·쿼리 최적화, 스크립트 자동화는 Kiro                           |
| 데이터 엔지니어             | **Cursor**      | Agents SDK                 | Python/SQL 자동완성, 파이프라인 에이전트는 Agents SDK                  |
| ML / AI 엔지니어            | **Cursor**      | Amp + Agents SDK           | 모델 코드 편집, Amp orbs로 장시간 스크립트 실행                        |
| 보안 엔지니어               | **Claude Code** | Copilot                    | 취약점 분석·코드 리뷰, IDE 내 빠른 수정은 Copilot                      |
| 개인 사이드 프로젝트 / 학습 | **Aider**       | Cursor Free 또는 Kiro Free | 무료 오픈소스, API 키로 모델 직접 선택                                 |

### 직무별 핵심 기능

| 직무                  | 필요 기능                       | 적합한 도구      |
|-----------------------|---------------------------------|------------------|
| SE/SRE                | Hooks, AWS 통합, CI/CD, IaC     | Kiro             |
| 백엔드/풀스택         | Tab 자동완성, 멀티모델, PR 통합 | Cursor + Copilot |
| 프론트엔드            | UI 생성, React/Next.js          | v0 + Cursor      |
| DBA                   | SQL 최적화, 복잡한 추론         | Claude Code      |
| 데이터/ML             | 장시간 실행, 원격 컨테이너      | Amp (orbs)       |
| 보안                  | 코드 취약점 분석, 정밀 추론     | Claude Code      |
| 자율 위임 (모든 직무) | 태스크 지시 → 자율 완성         | Devin            |
| 비용 최소화           | 무료 오픈소스, 자체 API 키      | Aider            |

🟡 6·7절은 기능·요금 비교를 바탕으로 한 권장 조합이며, 팀의 기존 도구·보안 정책·예산에 따라 달라집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [AI 코딩 도구 참조 노트](../../_reference/ai_coding_tools_official_notes.md) — 가격·모델·벤치마크 검증 기록
- [Claude Code 참조 노트](../../_reference/claude_code_official_notes.md) — Claude Code·Claude 모델 검증 기록
- Kiro Pricing: [kiro.dev/pricing](https://kiro.dev/pricing) — ★★★☆☆
- Kiro Models: [kiro.dev/docs/models](https://kiro.dev/docs/models/) — ★★★☆☆
- Kiro Headless (CI) 모드: [kiro.dev/docs/cli/headless](https://kiro.dev/docs/cli/headless/) — ★★★☆☆
- Claude Pricing: [claude.com/pricing](https://claude.com/pricing) — ★★★☆☆
- OpenAI Agents SDK: [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) — ★★★☆☆
- OpenAI Models: [developers.openai.com/api/docs/models](https://developers.openai.com/api/docs/models) — ★★★☆☆
- Cursor Pricing: [cursor.com/pricing](https://cursor.com/pricing) — ★★★☆☆
- Cursor CLI: [cursor.com/docs/cli/overview](https://cursor.com/docs/cli/overview) — ★★★☆☆
- Cursor Subagents: [cursor.com/docs/subagents](https://cursor.com/docs/subagents) — ★★★☆☆
- Cursor 2.0 변경 이력(Notepads deprecated): [cursor.com/changelog/2-0](https://cursor.com/changelog/2-0) — ★★★☆☆
- GitHub Copilot 플랜: [github.com/features/copilot/plans](https://github.com/features/copilot/plans) — ★★★☆☆
- GitHub Copilot CLI 확장 종료 공지: [github.blog/changelog](https://github.blog/changelog/2025-09-25-upcoming-deprecation-of-gh-copilot-cli-extension/) — ★★★☆☆
- GitHub Copilot Agent Skills: [docs.github.com](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) — ★★★☆☆
- Devin Pricing: [devin.ai/pricing](https://devin.ai/pricing) — ★★★☆☆
- Devin Desktop(구 Windsurf): [devin.ai/desktop](https://devin.ai/desktop) — ★★★☆☆
- Amp Pricing: [ampcode.com/pricing](https://ampcode.com/pricing) — ★★★☆☆
- Amp 분사 공지: [ampcode.com/news/amp-inc](https://ampcode.com/news/amp-inc) — ★★★☆☆
- Aider: [github.com/Aider-AI/aider](https://github.com/Aider-AI/aider) — ★★★☆☆
- v0 Pricing: [v0.app/pricing](https://v0.app/pricing) — ★★★☆☆
- Bolt.new Pricing: [bolt.new/pricing](https://bolt.new/pricing) — ★★★☆☆
- BenchLM Coding: [benchlm.ai/best/coding](https://benchlm.ai/best/coding) — ★★☆☆☆
- BenchLM Computer Use: [benchlm.ai/best/computer-use](https://benchlm.ai/best/computer-use) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-27

**마지막 업데이트**: 2026-11-18

© 2026 siasia86. Licensed under CC BY 4.0.
