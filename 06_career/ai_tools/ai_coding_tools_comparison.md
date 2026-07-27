# AI 코딩 도구 비교

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 도구별 정리](#2-도구별-정리) / [3. 기능 비교](#3-기능-비교)                                               |
| [4. 가격 비교](#4-가격-비교) / [5. 벤치마크](#5-벤치마크) / [6. 선택 가이드](#6-선택-가이드) / [7. 직무별 권장 도구](#7-직무별-권장-도구) |

---

## 1. 개요

2026년 7월 기준 주요 AI 코딩 도구 5종 비교입니다.

| 도구              | 제조사        | 카테고리                              | 기반 모델                                  |
|-------------------|---------------|---------------------------------------|---------------------------------------------|
| Kiro              | AWS           | AI IDE / CLI / Web / Mobile           | Claude Sonnet 4.6 / Opus 4.8 등             |
| Claude Code       | Anthropic     | AI 코딩 에이전트 (CLI/IDE/Web/Desktop) | Claude Mythos 5 / Opus 4.8 등              |
| OpenAI Agents SDK | OpenAI        | 멀티에이전트 프레임워크 (Python/TS SDK) | GPT-5.6 Sol / Terra 등                    |
| Cursor            | Anysphere     | AI IDE (VS Code fork)                 | Claude / GPT / Gemini 멀티모델              |
| GitHub Copilot    | Microsoft     | IDE 플러그인                          | GPT-5.6 / Claude Sonnet 등                  |
| Windsurf          | Cognition AI  | AI IDE (VS Code fork)                 | Claude / GPT / Gemini / SWE 멀티모델        |
| Devin             | Cognition AI  | 자율 AI 소프트웨어 엔지니어           | SWE 1.7 (자체) + Claude / GPT / Gemini      |
| Amp               | Sourcegraph   | AI 코딩 에이전트 (CLI/Web/Mobile)     | Claude / GPT / Gemini 멀티모델              |
| Aider             | Paul Gauthier | 오픈소스 터미널 CLI                   | Claude / GPT / DeepSeek 등 멀티모델         |
| v0 / Bolt.new     | Vercel / StackBlitz | UI·풀스택 생성 특화 (웹 기반)   | GPT-5.6 / Claude 등                         |

---

## 2. 도구별 정리

### Kiro

AWS가 만든 AI 개발 도구입니다. VS Code 기반 IDE(`kiro`), 터미널 CLI(`kiro-cli`), 웹, 모바일 네 가지 형태로 제공됩니다. Agents / Skills / Hooks / Steering files를 마크다운·JSON 파일로 커스터마이징하는 방식이 특징입니다.

#### 주요 특징

- Spec-driven 개발: 요구사항 → 설계 → 구현 흐름 자동화
- Agents: `.kiro/agents/*.json`으로 역할·도구·시스템 프롬프트 정의
- Skills: `.kiro/skills/SKILL.md`로 작업 패턴 재사용
- Hooks: 파일 저장, 명령어 실행 등 이벤트 기반 자동화
- Steering files: 에이전트 동작 전반에 적용되는 프로젝트 규칙 정의
- Parallel agents: 대형 코드베이스에서 여러 에이전트 병렬 실행
- MCP 서버 연동 지원
- ACP(Agent Client Protocol) 호환
- AWS 계정과 통합 (Bedrock, SSO)
- CI/CD headless 모드: PR 리뷰·버그 수정 자동화

#### 지원 모델 (2026-07-27 기준)

| 모델              | 크레딧 배율 |
|-------------------|-------------|
| claude-sonnet-4.6 | 1.30x       |
| claude-opus-4.5   | 2.20x       |
| claude-haiku-4.5  | 0.40x       |
| deepseek-3.2      | 0.25x       |
| qwen3-coder-next  | 0.05x       |
| auto              | 1.00x       |

🟡 Claude Sonnet 5 / Opus 5는 Seoul region에서 In-Region 미지원으로 현재 미제공.

---

### Claude Code

Anthropic이 만든 AI 코딩 에이전트입니다. 터미널 CLI, IDE 확장(VS Code·JetBrains), 데스크탑 앱, 웹 브라우저 네 가지 플랫폼에서 동작합니다. Claude.ai Pro/Max 구독에 포함되며, 별도 API 비용 없이 사용 가능합니다.

#### 주요 특징

- 코드베이스 파일을 직접 읽고 편집 (파일 참조·검색 내장)
- Git 연동, 테스트 실행, bash 명령 실행 등 직접 수행
- CLAUDE.md: 프로젝트별 컨텍스트·규칙 정의 파일
- Permission 모드: 작업별 승인 범위 설정 (Auto / Manual)
- MCP 서버 연동 지원
- GitHub Actions, VS Code, JetBrains, 웹, 데스크탑 앱 통합

#### 접근 방법

| 방법             | 조건                                |
|------------------|-------------------------------------|
| Claude Pro/Max   | 구독에 포함 (사용량 제한)           |
| API 직접 연결    | `ANTHROPIC_API_KEY` 환경 변수 설정  |
| Amazon Bedrock   | AWS 계정 연동                       |

---

### OpenAI Agents SDK

OpenAI가 제공하는 오픈소스 멀티에이전트 프레임워크입니다. Python/TypeScript로 에이전트·툴·가드레일을 코드로 정의하며, GPT-5.6 시리즈를 포함한 100개 이상의 LLM을 지원합니다.

#### 주요 특징

- Agents SDK: 코드로 에이전트·툴·가드레일 정의
- SandboxAgent: 파일·명령어·Git 작업을 컨테이너에서 실행
- Handoffs: 에이전트 간 작업 위임
- Guardrails: 입출력 유효성 검사
- Sessions: 에이전트 실행 간 대화 이력 자동 관리
- Human in the loop: 실행 중 사람 개입 메커니즘 내장
- Tracing: 에이전트 실행 추적·디버깅·최적화
- Realtime Voice Agent: `gpt-realtime-2.1` 기반 음성 지원
- MCP, Function Calling 지원
- 멀티에이전트 오케스트레이션 지원

#### GPT-5.6 라인업

| 모델           | 포지셔닝              | 입력 가격   | 출력 가격   | 컨텍스트   |
|----------------|-----------------------|-------------|-------------|------------|
| GPT-5.6 Sol    | 복잡한 추론·코딩 최고 | $5.00/1M    | $30.00/1M   | 1,050,000  |
| GPT-5.6 Terra  | 성능·비용 균형        | $2.50/1M    | $15.00/1M   | 1,050,000  |
| GPT-5.6 Luna   | 대량 처리 최적화      | $1.00/1M    | $6.00/1M    | 1,050,000  |

---

### Cursor

Anysphere가 만든 VS Code fork 기반 AI IDE입니다. 멀티모델(Claude / GPT / Gemini)을 동시에 지원하며, 코드 인식 채팅과 에이전트 모드를 제공합니다.

#### 주요 특징

- Tab 자동완성: 다음 코드 예측
- Chat: 코드베이스 컨텍스트 인식 대화
- Agent 모드 (Composer): 파일 생성·수정·실행을 자동으로 수행
- Background Agent (Cloud): 원격 서버에서 에이전트 자율 실행
- `.cursor/rules`: 프로젝트·글로벌 AI 동작 규칙 정의 (`.cursorrules`는 deprecated)
- Notepads: 재사용 가능한 컨텍스트 스니펫
- Bugbot: PR 코드 리뷰 자동화
- MCP 지원, Marketplace 확장 가능
- Automations: 반복 작업 자동화

---

### GitHub Copilot

Microsoft / GitHub이 만든 IDE 플러그인 형태의 AI 코딩 도구입니다. VS Code, JetBrains, Vim 등 대부분의 IDE에서 동작합니다.

#### 주요 특징

- 인라인 코드 자동완성 (원조)
- Copilot Chat: 코드 설명·리팩토링·테스트 생성
- Copilot Agent: Issue → PR 자동 생성 (GitHub Actions 연동)
- Workspace Agents: ChatGPT 내에서 GitHub 작업 트리거
- MCP Registry 지원
- GitHub 전체 생태계 통합 (Actions, PR, Security)
- 기업 정책·콘텐츠 필터링 관리 지원

---

### Windsurf

Cognition AI(구 Codeium)가 만든 VS Code fork 기반 AI IDE입니다. Cascade 에이전트 모드와 멀티파일 편집이 특징이며, Devin과 같은 회사 제품입니다.

#### 주요 특징

- Cascade: 멀티파일·멀티스텝 에이전트 작업
- Tab 자동완성 (Codeium 기반)
- Chat: 코드베이스 컨텍스트 인식 대화
- 멀티모델 지원 (Claude / GPT / Gemini / SWE)
- MCP 지원
- Flows: 반복 작업 자동화

#### 가격 (2026-07-27 기준)

| 플랜  | 가격                          |
|-------|-------------------------------|
| Free  | $0/월                         |
| Pro   | $20/월                        |
| Max   | $200/월                       |
| Teams | $80/월 + $40/월 per full user |

---

### Devin

Cognition AI가 만든 자율 AI 소프트웨어 엔지니어입니다. 사람이 태스크를 지시하면 에이전트가 코드 작성·테스트·PR까지 자율적으로 수행합니다. Desktop IDE와 Cloud 에이전트를 통합한 형태가 특징입니다.

#### 주요 특징

- Devin Desktop: 로컬 에이전트 플릿 관리 IDE
- Devin Cloud: 클라우드에서 에이전트 자율 실행
- Devin CLI: 터미널 기반 접근
- Devin Review: PR 코드 리뷰 자동화
- 자체 모델 SWE 1.7 + Claude / GPT / Gemini 멀티모델
- Agent Command Center: 여러 에이전트 동시 관리
- ACP 호환

#### 가격 (2026-07-27 기준)

| 플랜  | 가격                          |
|-------|-------------------------------|
| Free  | $0/월 (제한적 quota)          |
| Pro   | $20/월                        |
| Max   | $200/월 (높은 quota)          |
| Teams | $80/월 + $40/월 per full user |

---

### Amp

Sourcegraph가 만든 AI 코딩 에이전트입니다. 웹, 터미널 CLI, 모바일 세 가지 형태로 제공되며, orbs(원격 컨테이너)에서 에이전트가 독립적으로 실행됩니다.

#### 주요 특징

- Orbs: 원격 컨테이너에서 에이전트 자율 실행 (로컬 머신 불필요)
- 웹, 터미널 CLI, 모바일 세 가지 플랫폼
- 멀티모델 지원 (Claude / GPT / Gemini 등)
- ChatGPT Pro, xAI Premium+ 구독 연동 가능
- GitHub 연동, PR 자동화

#### 가격 (2026-07-27 기준)

| 플랜      | 가격                          |
|-----------|-------------------------------|
| Megawatt  | $20/월 (orbs 750시간 포함)    |
| Gigawatt  | $200/월 (높은 quota)          |

---

### Aider

오픈소스 터미널 CLI 기반 AI 페어 프로그래밍 도구입니다. GitHub 47K stars의 커뮤니티 프로젝트로, 로컬 git 저장소와 직접 연동하여 코드 변경·커밋을 수행합니다.

#### 주요 특징

- 100% 오픈소스 (MIT), 무료
- 터미널 CLI로 동작, 기존 에디터와 병행 사용
- 로컬 git 저장소 직접 연동 (diff, commit 자동)
- 멀티모델 지원 (Claude / GPT / DeepSeek / Gemini 등 API key 방식)
- 로컬 모델(Ollama 등) 지원
- 자체 [LLM 코딩 벤치마크 리더보드](https://aider.chat/docs/leaderboards/) 운영

#### 가격

무료 (오픈소스). 사용하는 LLM API 비용만 발생.

---

### v0 / Bolt.new

UI 컴포넌트 및 풀스택 앱을 프롬프트로 생성하는 웹 기반 도구입니다. 코드 에디터가 아닌 **브라우저에서 즉시 실행·배포**가 가능한 형태가 특징입니다.

| 도구    | 제조사     | 특화 영역                         | 비고                               |
|---------|------------|-----------------------------------|------------------------------------|
| v0      | Vercel     | React/Next.js UI 컴포넌트 생성    | Vercel 배포 통합                   |
| Bolt.new| StackBlitz | 풀스택 웹앱 (Node.js/React 등)    | 브라우저 내 Node.js 런타임 실행    |

#### 가격

| 도구    | Free                             | 유료                        |
|---------|----------------------------------|-----------------------------|
| v0      | $0 (300K tokens/일, 1M tokens/월)| Pro $30/월, Premium $100/월 |
| Bolt.new| $0 ($5 크레딧 포함)              | Pro $30/월 + $2 daily 크레딧|

🟡 v0·Bolt.new는 범용 코딩 에이전트가 아니라 **웹 UI·앱 프로토타이핑** 특화 도구입니다.


---

## 3. 기능 비교

### 핵심 기능

| 기능                       | Kiro         | Claude Code   | Agents SDK    | Cursor        | Copilot       |
|----------------------------|--------------|---------------|---------------|---------------|---------------|
| IDE 통합                   | ✅ (기본)    | 🟡 (플러그인) | ❌ (CLI/SDK)  | ✅ (기본)     | ✅ (플러그인) |
| 터미널 CLI                 | ✅           | ✅ (주력)     | ✅            | ❌            | ❌            |
| 자동완성 (Tab)             | ✅           | ❌            | ❌            | ✅            | ✅            |
| 에이전트 모드              | ✅           | ✅            | ✅            | ✅            | ✅            |
| 멀티에이전트               | 🟡           | 🟡            | ✅            | ❌            | ❌            |
| MCP 지원                   | ✅           | ✅            | ✅            | ✅            | ✅            |
| 커스텀 에이전트 정의       | ✅ (파일)    | ✅ (CLAUDE.md)| ✅ (코드)     | ✅ (.cursorrules) | 🟡       |
| Skills / 재사용 패턴       | ✅ (SKILL.md)| ❌            | ✅ (SDK)      | ✅ (Notepads) | ❌            |
| Hooks / 이벤트 자동화      | ✅           | ❌            | ❌            | ✅            | ❌            |
| Git / PR 연동              | ✅           | ✅            | ✅            | ✅            | ✅ (주력)     |
| 음성 에이전트              | ❌           | ❌            | ✅            | ❌            | ❌            |
| 멀티모델 선택              | ✅           | ❌            | ❌            | ✅            | 🟡            |
| AWS 통합                   | ✅ (강점)    | ✅ (Bedrock)  | ❌            | ❌            | ❌            |
| GitHub Actions 통합        | ❌           | ✅            | ❌            | ❌            | ✅ (강점)     |

### 커스터마이징 방식 비교

| 도구         | 방식               | 진입 장벽 | 유연성 |
|--------------|-------------------|-----------|--------|
| Kiro         | 마크다운·JSON 파일 | 낮음      | 중간   |
| Claude Code  | CLAUDE.md 텍스트  | 낮음      | 중간   |
| Agents SDK   | Python/TS 코드    | 높음      | 높음   |
| Cursor       | .cursorrules 텍스트| 낮음     | 중간   |
| Copilot      | 설정 UI 위주      | 낮음      | 낮음   |

---

## 4. 가격 비교

출처: 각 공식 사이트 (2026-07-27 기준)

### 개인 플랜

| 도구         | Free                       | 기본 유료                  | 고급 유료                         |
|--------------|----------------------------|----------------------------|-----------------------------------|
| Kiro         | $0 (50 크레딧/월)          | Pro $20 (1,000 크레딧/월)  | Pro+ $40 / Pro Max $100 / Power $200 |
| Claude Code  | —                          | Pro $20/월 (포함)          | Max $100/월 (포함)                |
| Agents SDK   | —                          | API 종량제 (GPT-5.6 Sol $5/$30 per 1M) | —               |
| Cursor       | Hobby (무료, 제한적)        | Individual $20/월          | Teams $40/user/월                 |
| Copilot      | Free (2,000 completions/월)| Pro $10/월                 | Pro+ $39/월 / Max $100/월         |

🟡 Claude Code는 별도 요금 없이 Claude Pro/Max 구독에 포함됩니다.
🟡 OpenAI Agents SDK는 API 토큰 사용량 기반 종량제입니다. ChatGPT 내 Codex 기능(Pro/Team)은 별도 구독 포함입니다.

---

## 5. 벤치마크

### Computer Use (GUI 에이전트)

출처: [benchlm.ai/best/computer-use](https://benchlm.ai/best/computer-use) (2026-07-27 기준)

| 순위 | 모델             | 제조사    | BenchLM 점수 |
|------|------------------|-----------|--------------|
| 1    | Claude Opus 4.8  | Anthropic | 85.2         |
| 2    | GPT-5.4          | OpenAI    | 79.2         |
| 3    | Claude Opus 4.6  | Anthropic | 76.9         |
| 4    | Qwen3.7 Plus     | Alibaba   | 75.6         |
| 5    | Claude Opus 4.5  | Anthropic | 58.1         |

- Computer Use는 모두 독점(Closed) 모델. 오픈 웨이트 대안 없음.
- 데스크탑 자동화: GPT-5.4 (OSWorld-Verified 최고)
- 화면 읽기·그라운딩: Claude Opus 4.6 (ScreenSpot Pro 강점)

### 코딩 벤치마크

출처: [benchlm.ai/best/coding](https://benchlm.ai/best/coding) (2026-07-27 기준)

| 순위 | 모델             | 제조사    | BenchLM 점수 |
|------|------------------|-----------|--------------|
| 1    | Claude Mythos 5  | Anthropic | 79.8         |
| 2    | Claude Fable 5   | Anthropic | 79.5         |
| 3    | GPT-5.6 Sol      | OpenAI    | 78.2         |

- 오픈 웨이트 최고: MiniMax M3 (68.8)
- 코딩 가성비: GPT-5.6 Sol ($30 output / 1M tokens)
- 최고 속도: Grok 4.2 (233 tokens/sec)

🟡 도구(Kiro, Claude Code 등)가 아닌 **기반 모델** 기준 벤치마크입니다. 실제 도구 성능은 기반 모델 + 시스템 프롬프트 + 컨텍스트 처리 방식에 따라 달라집니다.

---

## 6. 선택 가이드

| 상황                                              | 추천 도구      | 이유                                                      |
|---------------------------------------------------|----------------|-----------------------------------------------------------|
| AWS 인프라 작업 + 에이전트 커스터마이징           | **Kiro**       | AWS 통합, Skills/Hooks, 마크다운 기반 설정                |
| 터미널 중심 + 코드베이스 전체 수정 작업           | **Claude Code** | CLI 주력, CLAUDE.md, Pro/Max 구독 포함                   |
| 멀티에이전트 워크플로우 프로덕션 시스템 구축      | **Agents SDK**   | Handoffs·Guardrails, 코드 기반 최고 유연성, 100+ LLM 지원 |
| 빠른 자동완성 + 멀티모델 선택 + IDE 환경          | **Cursor**     | Tab 자동완성, .cursorrules, Claude·GPT 동시 지원          |
| GitHub 중심 + PR 자동화 + 기업 정책 관리          | **Copilot**    | GitHub Actions 통합, Issue→PR, 기업 보안·정책 지원        |
| 비용 최소화 (개인·학습)                           | **Copilot Free** or **Kiro Free** | 무료 플랜으로 시작 가능                 |

---

## 7. 직무별 권장 도구

작업 유형이 아닌 **직무 관점**의 권장 조합입니다. 단일 도구보다 주력 + 보조 조합이 실용적입니다.

### 주력 + 보조 권장 조합

| 직무                         | 주력 도구       | 보조 도구               | 이유                                                                        |
|------------------------------|-----------------|-------------------------|-----------------------------------------------------------------------------|
| 시스템 엔지니어 (SE/SRE)     | **Kiro**        | Claude Code             | AWS/인프라 통합, Skills·Hooks로 반복 작업 자동화, CLI로 서버 직접 작업      |
| DevOps / 플랫폼 엔지니어     | **Kiro**        | Copilot + Agents SDK    | CI/CD headless 모드, GitHub Actions 통합, 멀티에이전트 파이프라인 구성     |
| 백엔드 개발자                | **Cursor**      | Claude Code             | Tab 자동완성 + 멀티모델, 코드베이스 전체 리팩토링은 Claude Code 활용       |
| 프론트엔드 개발자            | **Cursor**      | v0                      | React/Next.js 자동완성, UI 컴포넌트 초안은 v0로 빠르게 생성 후 편집        |
| 풀스택 개발자                | **Cursor**      | Bolt.new + Devin        | 프로토타입은 Bolt.new, 복잡한 기능 구현은 Cursor, 반복 태스크는 Devin 위임 |
| DBA                          | **Claude Code** | Kiro                    | SQL 분석·쿼리 최적화에 Claude 추론 강점, 스크립트 자동화는 Kiro 활용       |
| 데이터 엔지니어              | **Cursor**      | Agents SDK              | Python/SQL 자동완성, 데이터 파이프라인 에이전트는 Agents SDK로 구축        |
| ML / AI 엔지니어             | **Cursor**      | Amp + Agents SDK        | 모델 코드 편집, Amp orbs로 장시간 학습 스크립트 자율 실행                  |
| 보안 엔지니어                | **Claude Code** | Copilot                 | 취약점 분석·코드 리뷰에 Claude 추론 강점, IDE 내 빠른 수정은 Copilot       |
| 개인 사이드 프로젝트 / 학습  | **Aider**       | Cursor Hobby or Kiro Free | 무료 오픈소스, API key 방식으로 원하는 모델 직접 선택 가능                |

### 직무별 핵심 기능 매핑

| 직무                   | 필요 기능                              | 최적 도구              |
|------------------------|----------------------------------------|------------------------|
| SE/SRE                 | Hooks, AWS 통합, CI/CD, IaC 지원      | Kiro                   |
| 백엔드/풀스택          | Tab 자동완성, 멀티모델, PR 통합       | Cursor + Copilot       |
| 프론트엔드             | UI 생성, React/Next.js 특화           | v0 + Cursor            |
| DBA                    | SQL 최적화, 복잡한 추론               | Claude Code            |
| 데이터/ML              | 장시간 실행, 원격 컨테이너            | Amp (orbs)             |
| 보안                   | 코드 취약점 분석, 정밀 추론           | Claude Code            |
| 자율 위임 (모든 직무)  | 태스크 지시 → 자율 완성               | Devin                  |
| 비용 최소화            | 무료 오픈소스, 자체 API key           | Aider                  |

🟡 도구는 조합해서 사용하는 것이 일반적입니다. "주력 하나 + 보조 하나" 구성이 비용 대비 효율이 높습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/ai_coding_tools_official_notes.md](../../_reference/ai_coding_tools_official_notes.md) — 가격·모델·벤치마크 검증 근거 노트

- BenchLM Computer Use: [benchlm.ai/best/computer-use](https://benchlm.ai/best/computer-use) — ★★★☆☆
- BenchLM Coding: [benchlm.ai/best/coding](https://benchlm.ai/best/coding) — ★★★☆☆
- Kiro Pricing: [kiro.dev/pricing](https://kiro.dev/pricing) — ★★★☆☆
- OpenAI Agents SDK: [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) — ★★★☆☆
- OpenAI Codex (ChatGPT): [platform.openai.com/docs/codex](https://platform.openai.com/docs/codex) — ★★★☆☆
- OpenAI Models: [platform.openai.com/docs/models](https://platform.openai.com/docs/models) — ★★★☆☆
- GitHub Copilot: [github.com/features/copilot](https://github.com/features/copilot) — ★★★☆☆
- Cursor Pricing: [cursor.com/pricing](https://www.cursor.com/pricing) — ★★★☆☆

---

**작성일**: 2026-07-27

**마지막 업데이트**: 2026-07-27

© 2026 siasia86. Licensed under CC BY 4.0.
