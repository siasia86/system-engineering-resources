# AI 코딩 도구 비교

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 도구별 정리](#2-도구별-정리) / [3. 기능 비교](#3-기능-비교)                                               |
| [4. 가격 비교](#4-가격-비교) / [5. 벤치마크](#5-벤치마크) / [6. 선택 가이드](#6-선택-가이드) |

---

## 1. 개요

2026년 7월 기준 주요 AI 코딩 도구 5종 비교입니다.

| 도구           | 제조사      | 카테고리              | 기반 모델                          |
|----------------|-------------|-----------------------|------------------------------------|
| Kiro           | AWS         | AI IDE                | Claude Sonnet 4.6 / Opus 4.8 등    |
| Claude Code    | Anthropic   | AI 코딩 에이전트 CLI  | Claude Mythos 5 / Opus 4.8 등      |
| OpenAI Codex   | OpenAI      | AI 코딩 에이전트 CLI  | GPT-5.6 Sol / Terra 등             |
| Cursor         | Anysphere   | AI IDE (VS Code fork) | Claude / GPT / Gemini 멀티모델     |
| GitHub Copilot | Microsoft   | IDE 플러그인          | GPT-5.6 / Claude Sonnet 등         |

---

## 2. 도구별 정리

### Kiro

AWS가 만든 AI IDE입니다. VS Code 기반으로 동작하며, Agents / Skills / Prompts를 마크다운·JSON 파일로 커스터마이징하는 방식이 특징입니다.

#### 주요 특징

- Spec-driven 개발: 요구사항 → 설계 → 구현 흐름 자동화
- Agents: `.kiro/agents/*.json`으로 역할·도구·시스템 프롬프트 정의
- Skills: `.kiro/skills/SKILL.md`로 작업 패턴 재사용
- Hooks: 파일 저장, 명령어 실행 등 이벤트 기반 자동화
- MCP 서버 연동 지원
- AWS 계정과 통합 (Bedrock, SSO)

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

Anthropic이 만든 터미널 기반 AI 코딩 에이전트입니다. Claude.ai Pro/Max 구독에 포함되며, 별도 API 비용 없이 사용 가능합니다.

#### 주요 특징

- 터미널 CLI (`claude`) 방식으로 동작
- 코드베이스 전체를 컨텍스트로 인식
- Git 연동, 테스트 실행, 파일 편집 등 직접 수행
- CLAUDE.md: 프로젝트별 컨텍스트·규칙 정의 파일
- MCP 서버 연동 지원
- GitHub Actions, VS Code, JetBrains 통합

#### 접근 방법

| 방법             | 조건                                |
|------------------|-------------------------------------|
| Claude Pro/Max   | 구독에 포함 (사용량 제한)           |
| API 직접 연결    | `ANTHROPIC_API_KEY` 환경 변수 설정  |
| Amazon Bedrock   | AWS 계정 연동                       |

---

### OpenAI Codex (Agents SDK)

OpenAI의 코딩 에이전트 CLI 및 SDK입니다. GPT-5.6 시리즈를 기반으로 동작하며, Python/TypeScript로 멀티에이전트 워크플로우를 구성합니다.

#### 주요 특징

- Agents SDK: 코드로 에이전트·툴·가드레일 정의
- SandboxAgent: 파일·명령어·Git 작업을 컨테이너에서 실행
- Handoffs: 에이전트 간 작업 위임
- Realtime Voice Agent: `gpt-realtime-2.1` 기반 음성 지원
- MCP, Function Calling, Skills 지원
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
- Agent 모드: 파일 생성·수정·실행을 자동으로 수행
- `.cursorrules`: 프로젝트별 AI 동작 규칙 정의
- Notepads: 재사용 가능한 컨텍스트 스니펫
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

## 3. 기능 비교

### 핵심 기능

| 기능                       | Kiro         | Claude Code   | OpenAI Codex  | Cursor        | Copilot       |
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
| OpenAI Codex | Python/TS 코드    | 높음      | 높음   |
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
| OpenAI Codex | —                          | API 종량제 (GPT-5.6 Sol $5/$30 per 1M) | —               |
| Cursor       | Hobby (무료, 제한적)        | Individual $20/월          | Teams $40/user/월                 |
| Copilot      | Free (2,000 completions/월)| Pro $10/월                 | Pro+ $39/월 / Max $100/월         |

🟡 Claude Code는 별도 요금 없이 Claude Pro/Max 구독에 포함됩니다.
🟡 OpenAI Codex (Agents SDK)는 API 토큰 사용량 기반 종량제입니다.

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
| 멀티에이전트 워크플로우 프로덕션 시스템 구축      | **OpenAI Codex** | Agents SDK, Handoffs, 코드 기반 최고 유연성              |
| 빠른 자동완성 + 멀티모델 선택 + IDE 환경          | **Cursor**     | Tab 자동완성, .cursorrules, Claude·GPT 동시 지원          |
| GitHub 중심 + PR 자동화 + 기업 정책 관리          | **Copilot**    | GitHub Actions 통합, Issue→PR, 기업 보안·정책 지원        |
| 비용 최소화 (개인·학습)                           | **Copilot Free** or **Kiro Free** | 무료 플랜으로 시작 가능                 |

---

## 참고 자료

- BenchLM Computer Use: [benchlm.ai/best/computer-use](https://benchlm.ai/best/computer-use) — ★★★☆☆
- BenchLM Coding: [benchlm.ai/best/coding](https://benchlm.ai/best/coding) — ★★★☆☆
- Kiro Pricing: [kiro.dev/pricing](https://kiro.dev/pricing) — ★★★☆☆
- OpenAI Agents SDK: [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) — ★★★☆☆
- OpenAI Models: [platform.openai.com/docs/models](https://platform.openai.com/docs/models) — ★★★☆☆
- GitHub Copilot: [github.com/features/copilot](https://github.com/features/copilot) — ★★★☆☆
- Cursor Pricing: [cursor.com/pricing](https://www.cursor.com/pricing) — ★★★☆☆

---

**작성일**: 2026-07-27

**마지막 업데이트**: 2026-07-27

© 2026 siasia86. Licensed under CC BY 4.0.
