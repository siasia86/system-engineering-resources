# Harness Engineering

AI 에이전트가 실제 작업을 안정적으로 수행할 수 있도록 주변 환경(scaffolding)을 설계하는 엔지니어링 분야입니다. 프롬프트 엔지니어링이 "무엇을 말할지"에 집중한다면, 하네스 엔지니어링은 "에이전트가 작업할 환경을 어떻게 구성할지"에 집중합니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 핵심 구성 요소](#2-핵심-구성-요소) / [3. 아키텍처](#3-아키텍처)             |
| [4. 주요 원칙](#4-주요-원칙) / [5. 관련 도구 비교](#5-관련-도구-비교) / [6. 실전 적용](#6-실전-적용) |
| [7. Prompt Engineering과의 차이](#7-prompt-engineering과의-차이) / [8. 트러블슈팅](#8-트러블슈팅)    |

## 1. 개요

| 항목        | 값                                                                        |
|-------------|---------------------------------------------------------------------------|
| 정의        | AI 에이전트의 컨텍스트, 도구, 검증 루프, 메모리, 샌드박스를 설계하는 분야 |
| 등장 시기   | 2025년 말 ~ 2026년 본격화                                                 |
| 주요 제안자 | OpenAI (Codex팀), Anthropic (Claude팀), Martin Fowler                     |
| 핵심 철학   | 모델이 아닌 환경(harness)에 투자하여 에이전트 성공률을 높임               |
| 전제 조건   | AI 코딩 에이전트 (Codex, Claude Code, Cursor 등) 사용 환경                |

### 용어 정의

| 용어           | 의미                                                    |
|----------------|---------------------------------------------------------|
| Harness        | AI 에이전트를 둘러싼 환경 전체 (도구 + 컨텍스트 + 제약) |
| Scaffolding    | 에이전트가 작업을 수행하기 위한 구조물/보조 장치        |
| Agent Loop     | 에이전트의 관찰 → 판단 → 행동 → 검증 반복 사이클        |
| Context Window | 에이전트가 한 번에 참고할 수 있는 정보의 한계           |
| Verification   | 에이전트 출력물의 정확성을 자동으로 확인하는 과정       |

## 2. 핵심 구성 요소

```
┌────────────────────────────────────────────────────────────────┐
│                  Harness (Agent Environment)                   │
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐        │
│  │  Context   │  │   Tools    │  │ Verification Loop  │        │
│  │  Delivery  │  │ Interface  │  │  (CI/Linter/Test)  │        │
│  └────────────┘  └────────────┘  └────────────────────┘        │
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐        │
│  │  Memory &  │  │  Sandbox   │  │ Planning Artifacts │        │
│  │   State    │  │(Isolation) │  │ (Exec Plans/Specs) │        │
│  └────────────┘  └────────────┘  └────────────────────┘        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

| 구성 요소        | 역할                                     | 예시                                    |
|------------------|------------------------------------------|-----------------------------------------|
| Context Delivery | 에이전트에게 필요한 정보를 적시에 제공   | AGENTS.md, docs/, ARCHITECTURE.md       |
| Tool Interface   | 에이전트가 사용할 도구의 API/스키마 설계 | MCP 서버, CLI 래퍼, 파일 시스템 접근    |
| Verification     | 출력물을 자동으로 검증하는 피드백 루프   | 커스텀 린터, 구조 테스트, CI 파이프라인 |
| Memory & State   | 세션 간 지식 유지, 장기 기억             | 실행 계획, 의사결정 로그, 품질 점수     |
| Sandbox          | 안전한 격리 실행 환경                    | Docker, git worktree, 임시 환경         |
| Planning         | 작업 분해 및 진행 추적을 위한 문서       | Plan.md, exec-plans/, tech-debt-tracker |

## 3. 아키텍처

### Agent Loop 구조

```
Human (Engineer)
       │
       │  Task Prompt
       v
┌────────────────────────────────────────────┐
│             Agent Loop                     │
│                                            │
│  Observe ──> Plan ──> Act ──> Verify       │
│      ^                          │          │
│      └──────── Feedback ────────┘          │
│                                            │
└────────────────────────────────────────────┘
       │
       v
   Output (PR, Code, Docs)
       │
       v
┌────────────────────────────────────────────┐
│         Verification Layer                 │
│   Linter / Test / CI / Agent Review        │
└────────────────────────────────────────────┘
       │
       ├── Pass ──> Merge
       └── Fail ──> Feedback to Agent Loop
```

### Repository Knowledge 구조 (OpenAI 방식)

```
repo/
├── AGENTS.md              # Entry point (map, not manual)
├── ARCHITECTURE.md        # Domain/layer map
├── docs/
│   ├── design-docs/
│   │   ├── index.md
│   │   └── core-beliefs.md
│   ├── exec-plans/
│   │   ├── active/
│   │   └── completed/
│   ├── product-specs/
│   ├── references/
│   │   └── *-llms.txt
│   ├── DESIGN.md
│   ├── QUALITY_SCORE.md
│   ├── RELIABILITY.md
│   └── SECURITY.md
└── src/
```

핵심 원칙: AGENTS.md는 백과사전이 아닌 **목차(table of contents)**입니다. 짧게 유지하고(~100줄) 깊은 정보는 별도 문서로 분리합니다.

## 4. 주요 원칙

### OpenAI (Codex팀) 원칙

| 원칙                            | 설명                                                   |
|---------------------------------|--------------------------------------------------------|
| Humans steer, Agents execute    | 인간은 설계/방향 제시, 에이전트는 코드 작성            |
| Map, not manual                 | AGENTS.md는 짧은 목차, 상세 내용은 별도 문서           |
| Agent legibility first          | 에이전트가 읽을 수 있는 형태로 모든 지식을 레포에 저장 |
| Enforce architecture, not style | 아키텍처 경계는 기계적으로 강제, 스타일은 자유         |
| Entropy management              | 정기적으로 기술 부채를 청소하는 에이전트를 운영        |
| Corrections are cheap           | 빠른 처리량 환경에서 수정 비용은 대기 비용보다 낮음    |

### Anthropic (Claude팀) 원칙

| 원칙                                 | 설명                                                            |
|--------------------------------------|-----------------------------------------------------------------|
| Harness components have expiry dates | 모델 성능 향상에 따라 하네스 구성 요소가 불필요해질 수 있음     |
| Tool design is agent UX              | 도구 인터페이스 설계 = 에이전트를 위한 UX 설계                  |
| Structured permissions               | 자연어 허가 대신 구조적 권한 시스템을 구축                      |
| Eval-driven development              | 단위 테스트 방식의 평가는 에이전트에 부적합, 시나리오 기반 평가 |

### Martin Fowler 정의 — 3가지 시스템

| 시스템                    | 설명                                       |
|---------------------------|--------------------------------------------|
| Context Engineering       | 에이전트가 알아야 할 정보를 큐레이션       |
| Architectural Constraints | 린터, 구조 테스트로 결정론적 경계를 강제   |
| Entropy Management        | 문서 drift를 수리하는 주기적 에이전트 운영 |

## 5. 관련 도구 비교

| 도구/프레임워크           | 유형            | 하네스 엔지니어링 관련성                    |
|---------------------------|-----------------|---------------------------------------------|
| AGENTS.md                 | 컨텍스트 파일   | 에이전트에 레포 구조/규칙을 전달하는 진입점 |
| CLAUDE.md                 | 컨텍스트 파일   | Claude Code 전용 에이전트 지시 파일         |
| MCP (Model Context Proto) | 프로토콜        | 에이전트-도구 인터페이스 표준               |
| LangChain/LangGraph       | 프레임워크      | 에이전트 루프/메모리/도구 조합 프레임워크   |
| Google ADK                | 프레임워크      | 멀티 에이전트 토폴로지 + 평가 파이프라인    |
| Kiro CLI                  | 에이전트 런타임 | skills, context, agents로 하네스 구성       |

### Prompt Engineering vs Harness Engineering

| 구분   | Prompt Engineering           | Harness Engineering                        |
|--------|------------------------------|--------------------------------------------|
| 초점   | 에이전트에게 "무엇을 말할지" | 에이전트가 "작업할 환경을 어떻게 구성할지" |
| 대상   | 단일 프롬프트/응답           | 전체 작업 사이클                           |
| 지속성 | 일회성                       | 레포에 버전 관리되는 영구 아티팩트         |
| 검증   | 수동 확인                    | 자동화된 피드백 루프                       |
| 확장성 | 프롬프트 수만큼 선형 확장    | 한 번 설계하면 모든 작업에 적용            |

## 6. 실전 적용

### 최소 하네스 구성 (시작점)

```
project/
├── AGENTS.md          # Agent entry point (max 100 lines)
├── ARCHITECTURE.md    # Domain/layer map
├── .cursorrules       # Cursor (or .claude/settings.json)
├── docs/
│   └── decisions/     # Architecture decision records
├── scripts/
│   └── lint-arch.sh   # Architecture boundary linter
└── tests/
    └── structural/    # Structural tests (dependency direction)
```

### AGENTS.md 예시

```markdown
# AGENTS.md

## Repository Map
- Architecture: see ARCHITECTURE.md
- Design decisions: see docs/decisions/
- Quality grades: see docs/QUALITY_SCORE.md

## Rules
- All code must pass `scripts/lint-arch.sh` before PR
- Parse data at boundaries (use Zod or equivalent)
- No cross-domain imports without explicit interface

## When stuck
1. Read docs/decisions/ for prior art
2. Check ARCHITECTURE.md for layer constraints
3. If still unclear, ask the human
```

### 검증 루프 구현 패턴

```bash
# scripts/lint-arch.sh — Architecture boundary linter
#!/bin/bash
set -euo pipefail

# Detect cross-domain direct imports
VIOLATIONS=$(grep -rn "from.*domains/" src/ \
  | grep -v "from.*domains/shared" \
  | grep -v "__tests__" || true)

if [ -n "$VIOLATIONS" ]; then
  echo "ERROR: Cross-domain import detected."
  echo "Fix: Use shared interfaces in domains/shared/"
  echo "$VIOLATIONS"
  exit 1
fi
```

## 7. Prompt Engineering과의 차이

```
┌────────────────────────────────────────────────────────────┐
│                    Engineering Spectrum                    │
│                                                            │
│  Prompt Eng.     Context Eng.     Harness Eng.             │
│  (what to say)   (what to know)   (how to work)            │
│                                                            │
│  ├── Single ──── Session ──────── Multi-session ────────►  │
│  │   turn        context          persistent env           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

| 레벨 | 분야                | 지속성 | 관심사                     |
|------|---------------------|--------|----------------------------|
| L1   | Prompt Engineering  | 일회성 | 프롬프트 문구 최적화       |
| L2   | Context Engineering | 세션   | RAG, 컨텍스트 윈도우 관리  |
| L3   | Harness Engineering | 영구   | 환경, 도구, 검증, 아키텍처 |

## 8. 트러블슈팅

| 증상                             | 원인                                     | 해결                                       |
|----------------------------------|------------------------------------------|--------------------------------------------|
| 에이전트가 같은 실수를 반복      | 검증 루프 부재                           | 린터/구조 테스트 추가, CI에서 자동 차단    |
| 에이전트가 아키텍처를 무시       | AGENTS.md에 규칙만 있고 기계적 강제 없음 | 커스텀 린터로 경계를 강제                  |
| 컨텍스트 윈도우 초과             | AGENTS.md가 너무 길음                    | 목차 방식으로 전환, progressive disclosure |
| 코드 스타일 일관성 저하          | 모델이 기존 패턴을 복제하여 drift        | 정기 cleanup 에이전트 운영                 |
| 에이전트가 외부 지식에 접근 불가 | Slack/Docs의 암묵지가 레포에 없음        | 모든 결정을 레포 내 마크다운으로 기록      |

## 참고 자료

- OpenAI: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — ★★★★☆
- Anthropic: [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) — ★★★★☆
- Martin Fowler: [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) — ★★★★☆
- GitHub: [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) — ★★★☆☆
- GitHub: [walkinglabs/awesome-harness-engineering](https://github.com/walkinglabs/awesome-harness-engineering) — ★★★☆☆
- Learn Harness Engineering: [walkinglabs.github.io](https://walkinglabs.github.io/learn-harness-engineering/en/) — ★★☆☆☆

---

**작성일**: 2026-06-19

**마지막 업데이트**: 2026-06-19

© 2026 siasia86. Licensed under CC BY 4.0.
