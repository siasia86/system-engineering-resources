---
name: ai-coding-tools-official-notes
description: AI 코딩 도구(Kiro, Claude Code, OpenAI Agents SDK, Cursor, Copilot, Windsurf, Devin, Amp, Aider, v0, Bolt.new) 공식 문서 기반 가격·기능·벤치마크 참조 노트.
tags:
  - ai-tools
  - kiro
  - claude-code
  - cursor
  - copilot
  - windsurf
  - devin
  - aider
  - agents-sdk
last_checked: 2026-11-09
sources:
  - https://kiro.dev/pricing
  - https://code.claude.com/docs/en/overview
  - https://github.com/openai/openai-agents-python
  - https://platform.openai.com/docs/models
  - https://www.cursor.com/pricing
  - https://github.com/features/copilot
  - https://windsurf.com/pricing
  - https://devin.ai/pricing
  - https://ampcode.com/pricing
  - https://aider.chat
  - https://v0.dev/pricing
  - https://bolt.new/pricing
  - https://benchlm.ai/best/computer-use
  - https://benchlm.ai/best/coding
  - https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json
  - https://claude.com/pricing
  - https://kiro.dev/docs/models/available-models/
  - https://developers.openai.com/api/docs/models/gpt-5.6-sol
  - https://ampcode.com/news/amp-inc
---

# AI 코딩 도구 공식 문서 참조 노트

## 1. 가격 정보 (2026-07-27 직접 확인)

### Kiro (kiro.dev/pricing)

| 플랜    | 가격         | 크레딧/월 | 비고                            |
|---------|--------------|-----------|---------------------------------|
| Free    | $0           | 50        | Claude Sonnet 4.5 + 오픈 웨이트 |
| Pro     | $20/user/월  | 1,000     | 프리미엄 모델 포함              |
| Pro+    | $40/user/월  | 2,000     | 프리미엄 모델 포함              |
| Pro Max | $100/user/월 | 5,000     | 프리미엄 모델 포함              |
| Power   | $200/user/월 | 10,000    | 프리미엄 모델 포함              |

- Add-on credits: $0.04/credit
- Free 플랜 소셜 로그인/AWS Builder ID 가입 시 $20 크레딧 지급
- 프리미엄 모델: Auto, Claude Sonnet 4.6, Claude Opus 4.8 포함
- 국가/지역에 따라 일부 프리미엄 모델 미제공

### GitHub Copilot (github.com/features/copilot)

| 플랜     | 가격         | 포함 크레딧 | 비고                  |
|----------|--------------|-------------|-----------------------|
| Free     | $0/user/월   | —           | 2,000 completions/월  |
| Pro      | $10/user/월  | $15/월      | Unlimited completions |
| Pro+     | $39/user/월  | $70/월      | 4x+ usage than Pro    |
| Max      | $100/user/월 | $200/월     | 2.9x+ usage than Pro+ |
| Business | $19/user/월  | —           | 팀 관리 기능          |

### Cursor (cursor.com/pricing)

| 플랜       | 가격        | 비고                     |
|------------|-------------|--------------------------|
| Hobby      | Free        | 제한적 Agent 요청        |
| Individual | $20/월      | Pro / Pro+ / Ultra 선택  |
| Teams      | $40/user/월 | 팀 공유 컨텍스트, Bugbot |
| Enterprise | Custom      | SSO, SCIM, Audit logs    |

- 2026-11-09 확인: 개인 플랜은 Free $0 / Plus $8 / Premium $30 / Super $100 / Ultra $200(월), Teams는 $30/user/월부터, Enterprise는 Custom입니다.
- `.cursorrules`는 deprecated → `.cursor/rules`로 변경됨 (공식 docs 확인)
- Continue.dev는 Cursor에 인수됨 (2026년, continue.dev 공식 발표)

### Claude Code (code.claude.com, 2026-10-14 재확인)

- 모든 유료 플랜(Pro $20/월, Max $100/월부터 5x·20x, Team, Enterprise)에 포함, 채팅과 사용량 한도 공유. 무료 플랜 미포함
- API 직접 연결 시: `ANTHROPIC_API_KEY` 환경 변수 (Claude Console 종량제)
- Amazon Bedrock·Google Cloud·Microsoft Foundry 연동 가능
- 플랫폼: 터미널 CLI, VS Code 확장, JetBrains 확장, 데스크탑 앱, 웹, 모바일
- 2026-11-09 확인(claude.com/pricing): Ultra $200/월(주간 Pro의 10배, 인증된 계정은 5시간 한도 없음)이 추가되었고 Max는 $100/월·Pro의 5배로 표시됩니다. Ultra에도 Claude Code가 포함됩니다.
- 상세 근거: `_reference/claude_code_official_notes.md`

### Windsurf (windsurf.com/pricing)

| 플랜  | 가격                          |
|-------|-------------------------------|
| Free  | $0/월                         |
| Pro   | $20/월                        |
| Max   | $200/월                       |
| Teams | $80/월 + $40/월 per full user |

- 2026-11-09 확인: windsurf.com/pricing은 devin.ai/pricing으로 이동합니다.

### Devin (devin.ai/pricing)

| 플랜  | 가격                          | 비고                                     |
|-------|-------------------------------|------------------------------------------|
| Free  | $0/월                         | 제한적 quota, 일부 모델만                |
| Pro   | $20/월                        | Claude / GPT / Gemini 프론티어 모델 포함 |
| Max   | $200/월                       | 높은 quota                               |
| Teams | $80/월 + $40/월 per full user | —                                        |

- 자체 모델: SWE 1.7 (2026-11-09 확인: 요금 페이지는 SWE-2를 최신 자체 모델로 안내)
- Devin Cloud, Devin Desktop, Devin CLI, Devin Review 제품군
- Windsurf와 동일 회사 (Cognition AI)

### Amp (ampcode.com/pricing)

| 플랜     | 가격    | 포함 내용                      |
|----------|---------|--------------------------------|
| Megawatt | $20/월  | orbs 750시간 + $20 agent usage |
| Gigawatt | $200/월 | 높은 quota                     |

- 제조사: 2025-12-02 Sourcegraph에서 분사한 Amp Frontier Corporation (2026-11-09 공식 공지 확인)
- ChatGPT Pro, xAI Premium+/SuperGrok 구독 연동으로 GPT-5.6 / Grok 사용 가능
- orbs: 원격 컨테이너 (로컬 머신 없이 에이전트 자율 실행)

### Aider (aider.chat)

- 오픈소스 (Apache-2.0 라이선스), 무료
- GitHub: github.com/paul-gauthier/aider — **47,719 stars** (2026-07-27 확인, 2026-11-09 확인: 저장소 이름 Aider-AI/aider, 약 50,000 stars)
- 설치 수: 6.8M+
- 사용 비용: 연결하는 LLM API 비용만 발생

### v0 (v0.dev/pricing)

🟡 실제 플랜명은 Free / Plus / Business (노트 이전 버전의 "Pro/Premium" 명칭은 오기).

| 플랜     | 가격         | 포함 내용                                                |
|----------|--------------|----------------------------------------------------------|
| Free     | $0/월        | $5 크레딧/월                                             |
| Plus     | $30/user/월  | 전체 모델 접근, $30 크레딧/월 + 로그인 시 $2 무료 크레딧 |
| Business | $100/user/월 | 전체 모델 접근, $30 크레딧/월 + 로그인 시 $2 무료 크레딧 |

- 2026-11-09 확인(v0.app/pricing): Free는 하루 메시지 7개 제한이며, $5는 신규 사용자에게 한 번 주는 크레딧입니다.

### Bolt.new (bolt.new/pricing)

🟡 Pro 플랜 실제 가격은 $25/월 (노트 이전 버전의 $30/월은 오기 — $30/월은 Teams 플랜 가격).

| 플랜  | 가격        | 포함 내용                                 |
|-------|-------------|-------------------------------------------|
| Free  | $0          | Public/private 프로젝트                   |
| Pro   | $25/월      | 일일 토큰 제한 없음, 월 10M 토큰부터 시작 |
| Teams | $30/월/멤버 | Pro의 모든 항목 + 중앙 청구, 팀 관리 기능 |

- 2026-11-09 확인: Free는 하루 300K·월 1M 토큰을 제공합니다.

---

## 2. 모델 가격 (2026-07-27 litellm JSON 확인)

### GPT-5.6 시리즈

| 모델          | Model ID        | 입력 가격 | 출력 가격 | 컨텍스트  |
|---------------|-----------------|-----------|-----------|-----------|
| GPT-5.6 Sol   | gpt-5.6-sol     | $5.00/1M  | $30.00/1M | 1,050,000 |
| GPT-5.6 Terra | gpt-5.6-terra   | $2.50/1M  | $15.00/1M | 1,050,000 |
| GPT-5.6 Luna  | gpt-5.6-luna    | $1.00/1M  | $6.00/1M  | 1,050,000 |
| GPT-5.6       | gpt-5.6 (alias) | $5.00/1M  | $30.00/1M | 1,050,000 |

출처: litellm model_prices_and_context_window.json, platform.openai.com/docs/models

🟡 2026-11-09 OpenAI 공식 모델 페이지 기준 GPT-5.6 Terra는 $2.00/$12.00, Luna는 $0.20/$1.20입니다. Sol은 $5.00/$30.00이며 2026-11-30까지 프로모션 가격 $4.00/$20.00이 적용됩니다.

### Claude Opus 4.6

| 항목 | 값           |
|------|--------------|
| 입력 | $5.00/1M     |
| 출력 | $25.00/1M    |
| 출처 | litellm JSON |

---

## 3. Kiro 지원 모델 목록 (2026-07-27 kiro-cli 직접 확인)

| 모델              | 크레딧 배율 | 비고                   |
|-------------------|-------------|------------------------|
| claude-sonnet-4.6 | 1.30x       | 기본 선택 모델         |
| auto              | 1.00x       | 작업별 자동 선택       |
| claude-opus-4.5   | 2.20x       | —                      |
| claude-sonnet-4.5 | 1.30x       | —                      |
| claude-sonnet-4   | 1.30x       | extended thinking 지원 |
| claude-haiku-4.5  | 0.40x       | —                      |
| deepseek-3.2      | 0.25x       | 실험적 미리보기        |
| minimax-m2.5      | 0.25x       | —                      |
| minimax-m2.1      | 0.15x       | 실험적 미리보기        |
| glm-5             | 0.50x       | —                      |
| qwen3-coder-next  | 0.05x       | 실험적 미리보기        |

🟡 "기본 선택 모델"은 2026-07-27 kiro-cli 화면 기준입니다. 2026-11-09 공식 [Available models](https://kiro.dev/docs/models/available-models/)는 Auto를 권장(recommended)으로 표시하고 기본 모델을 따로 정하지 않습니다. 같은 날 [모델 목록](https://kiro.dev/docs/models/)(2026-10-24 갱신)에는 Claude Opus 5.5(2.0x)·Sonnet 5.5(1.3x)·Haiku 5.5(0.06x)와 GPT-5.6 Sol·Terra·Luna(4.4x·2.2x·0.6x)가 추가되었고, claude-sonnet-4(Claude Sonnet 4.0)는 2026-10-14에 지원 종료(EOL)되었습니다.

🟡 Claude Sonnet 5 / Opus 5: Seoul region (ap-northeast-2)에서 In-Region 미지원.
Global Cross-Region은 지원되나 Kiro가 In-Region 정책 사용 → 미제공.
(Bedrock 공식 문서: model-card-anthropic-claude-sonnet-5.md 직접 확인)

---

## 4. 벤치마크 (2026-07-27 benchlm.ai 직접 확인)

### Computer Use (benchlm.ai/best/computer-use)

| 순위 | 모델            | 제조사    | BenchLM 점수 | 비고                        |
|------|-----------------|-----------|--------------|-----------------------------|
| 1    | Claude Opus 4.8 | Anthropic | 85.2         | sourced avg                 |
| 2    | GPT-5.4         | OpenAI    | 79.2         | OSWorld-Verified 1위        |
| 3    | Claude Opus 4.6 | Anthropic | 76.9         | ScreenSpot Pro 강점         |
| 4    | Qwen3.7 Plus    | Alibaba   | 75.6         | —                           |
| 5    | Claude Opus 4.5 | Anthropic | 58.1         | JSON displayScore 직접 확인 |

- 전체 5개 모델 모두 독점(Closed) 모델
- 오픈 웨이트 대안 없음 (benchlm 명시)
- benchlm 설명: "Claude Opus 4.5 holds third with solid OSWorld coverage" (순위 표현 불일치, 실제 4위)

### 코딩 (benchlm.ai/best/coding)

| 순위 | 모델            | 제조사    | BenchLM 점수 |
|------|-----------------|-----------|--------------|
| 1    | Claude Mythos 5 | Anthropic | 79.8         |
| 2    | Claude Fable 5  | Anthropic | 79.5         |
| 3    | GPT-5.6 Sol     | OpenAI    | 78.2         |

- 오픈 웨이트 최고: MiniMax M3 (68.8)
- 속도 1위(Fastest measured): Grok 4.2 (233 tokens/sec)
- 코딩 가성비: GPT-5.6 Sol ($30 output/1M)

---

## 5. 제품 형태 및 플랫폼 (공식 사이트 확인)

| 도구        | 플랫폼                                                         | 출처                                   |
|-------------|----------------------------------------------------------------|----------------------------------------|
| Kiro        | IDE(VS Code), CLI(`kiro-cli`), Web, Mobile                     | kiro.dev                               |
| Claude Code | 터미널 CLI, VS Code 확장, JetBrains 확장, 데스크탑, 웹, 모바일 | code.claude.com                        |
| Agents SDK  | Python/TypeScript 코드 (웹서비스, CLI 모두 가능)               | github.com/openai/openai-agents-python |
| Cursor      | VS Code fork IDE                                               | cursor.com                             |
| Copilot     | VS Code, JetBrains, Vim, CLI 플러그인                          | github.com/features/copilot            |
| Windsurf    | VS Code fork IDE                                               | windsurf.com                           |
| Devin       | Desktop IDE, Cloud, CLI, Review                                | devin.ai                               |
| Amp         | Web, 터미널 CLI, Mobile                                        | ampcode.com                            |
| Aider       | 터미널 CLI                                                     | aider.chat                             |
| v0          | 웹 브라우저                                                    | v0.dev                                 |
| Bolt.new    | 웹 브라우저 (StackBlitz WebContainers)                         | bolt.new                               |

---

## 6. 미검증 항목

| 항목                                  | 상태 | 비고                                |
|---------------------------------------|------|-------------------------------------|
| Windsurf 지원 모델 상세 목록          | 🟡   | 공식 페이지 JS 렌더링으로 확인 불가 |
| Devin SWE 1.7 벤치마크 점수           | 🟡   | 공개 벤치마크 미확인                |
| Amp orbs 요금 상세 (시간당 비용)      | 🟡   | 가입 후 확인 필요                   |
| Cursor Background Agent 지역별 가용성 | 🟡   | Pro+ 이상 필요 여부 미확인          |
| v0 / Bolt.new 기반 모델 버전          | 🟡   | 공식 발표 없음                      |
| Kiro Web/Mobile 기능 범위             | 🟡   | IDE와 동일 기능 여부 미확인         |
