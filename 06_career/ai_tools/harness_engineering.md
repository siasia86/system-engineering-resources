# Harness Engineering

<!-- reference: _reference/harness_loop_engineering_sources_notes.md -->

AI 에이전트가 실제 작업을 안정적으로 수행할 수 있도록 주변 환경(scaffolding)을 설계하는 엔지니어링 분야입니다. 프롬프트 엔지니어링이 "무엇을 말할지"에 집중한다면, 하네스 엔지니어링은 "에이전트가 작업할 환경을 어떻게 구성할지"에 집중합니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 핵심 구성 요소](#2-핵심-구성-요소) / [3. 아키텍처](#3-아키텍처)             |
| [4. 주요 원칙](#4-주요-원칙) / [5. 관련 도구 비교](#5-관련-도구-비교) / [6. 실전 적용](#6-실전-적용) |
| [7. Prompt Engineering과의 차이](#7-prompt-engineering과의-차이) / [8. 트러블슈팅](#8-트러블슈팅)    |

---

## 1. 개요

| 항목      | 값                                                                                                                 |
|-----------|--------------------------------------------------------------------------------------------------------------------|
| 정의      | 모델을 뺀 에이전트의 나머지(지침·도구·상태·검사·권한·실행 환경)를 설계·개선하는 분야 (출처 종합)                   |
| 등장 시기 | 2026년 2월 (Hashimoto가 2026-02-05 이름 붙임, OpenAI 게시 2026-02-11)                                              |
| 주요 자료 | Mitchell Hashimoto, OpenAI (Codex팀), Anthropic, Birgitta Böckeler (Thoughtworks), LangChain                       |
| 핵심 철학 | 모델이 아닌 환경(harness)에 투자하여 에이전트 성공률을 높임                                                        |
| 전제 조건 | AI 코딩 에이전트 (Codex, Claude Code, Cursor 등) 사용 환경                                                         |
| 사례 수치 | 엔지니어 3명→7명, 약 5개월, 직접 쓴 코드 0줄, 약 100만 줄·PR 약 1,500개, 1인 하루 평균 PR 3.5개 (OpenAI 자체 보고) |

### 용어 정의

| 용어           | 의미                                                    |
|----------------|---------------------------------------------------------|
| Harness        | AI 에이전트를 둘러싼 환경 전체 (도구 + 컨텍스트 + 제약) |
| Scaffolding    | 에이전트가 작업을 수행하기 위한 구조물/보조 장치        |
| Agent Loop     | 에이전트의 관찰 → 판단 → 행동 → 검증 반복 사이클        |
| Context Window | 에이전트가 한 번에 참고할 수 있는 정보의 한계           |
| Verification   | 에이전트 출력물의 정확성을 자동으로 확인하는 과정       |

### 용어의 기원과 범위

- Mitchell Hashimoto는 2026-02-05 글에서 이 일을 "harness engineering"이라고 불렀습니다. 에이전트가 실수할 때마다 같은 실수를 다시 하지 않도록 해결책을 만들어 두는 일이며, 방법은 지침 파일(AGENTS.md 등)에 한 줄을 더하거나 실제 도구(화면 캡처, 일부 테스트만 돌리는 스크립트 등)를 만드는 것입니다. [My AI Adoption Journey](https://mitchellh.com/writing/my-ai-adoption-journey)
- 같은 달 11일 OpenAI가 Codex 사례를 같은 이름으로 발표하면서 널리 쓰이기 시작했습니다.
- LangChain은 "Agent = Model + Harness"로 정리합니다. 모델이 아닌 코드·설정·실행 논리가 모두 하네스입니다. [The Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness)
- 표준 정의는 없습니다. 출처마다 범위가 달라, 이 문서는 "에이전트를 쓰는 쪽이 저장소와 작업 환경에 더하는 것"을 중심으로 다룹니다.

| 헷갈리기 쉬운 이름               | 뜻                                                                                                      |
|----------------------------------|---------------------------------------------------------------------------------------------------------|
| 에이전트 하네스 (이 문서)        | 에이전트가 일하는 환경: 지침·도구·상태·검사·권한                                                        |
| 평가 하네스 (evaluation harness) | 모델·에이전트의 성능을 재는 시험 틀. [평가 설계](../../07_ai_transformation/agent_evaluation_design.md) |
| 테스트 하네스 (test harness)     | 소프트웨어 시험용 실행 틀(드라이버·stub)                                                                |
| Harness (회사·제품)              | CI/CD 플랫폼. [Harness](../../02_infrastructure/cicd/harness_inc.md)                                    |

[⬆ 목차로 돌아가기](#목차)

---

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

[⬆ 목차로 돌아가기](#목차)

---

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
│   ├── FRONTEND.md
│   ├── PLANS.md
│   ├── PRODUCT_SENSE.md
│   ├── QUALITY_SCORE.md
│   ├── RELIABILITY.md
│   └── SECURITY.md
└── src/
```

핵심 원칙: AGENTS.md는 백과사전이 아닌 **목차**(table of contents)입니다. OpenAI 사례의 약 100줄은 해당 팀의 운영 예시이며 공통 제한이 아닙니다. 진입점은 짧게 유지하고 작업별 상세 기준은 한 곳에서 관리합니다. [OpenAI 원문](https://openai.com/index/harness-engineering/)

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 원칙

### OpenAI (Codex팀) 원칙

| 원칙                                | 설명                                                                                                                                                 |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Humans steer, Agents execute        | 인간은 설계/방향 제시, 에이전트는 코드 작성                                                                                                          |
| Map, not manual                     | AGENTS.md는 짧은 목차, 상세 내용은 별도 문서                                                                                                         |
| Agent legibility first              | 에이전트가 읽을 수 있는 형태로 모든 지식을 레포에 저장                                                                                               |
| Enforcing architecture and taste    | 아키텍처 경계와 취향(taste)을 린터/원칙으로 인코딩하여 강제                                                                                          |
| Entropy management                  | 매주 금요일(20%)에 하던 정리를 원칙 검사·리팩터링 PR을 여는 배경 작업으로 바꿈(garbage collection 비유), 오래된 문서는 doc-gardening 에이전트가 고침 |
| Throughput changes merge philosophy | 고처리량 환경에서 수정 비용이 대기 비용보다 낮아 빠른 머지를 우선                                                                                    |
| Long-running autonomy               | Codex 1회 실행이 한 작업에 6시간 넘게 무인으로 동작하는 일이 잦음 (OpenAI 원문)                                                                      |

### Anthropic 접근법

🟡 아래는 Anthropic 두 글(2025-11-26, 2026-03-24)의 교훈을 요약한 것이며, 원문이 "원칙"으로 이름 붙인 것은 아닙니다.

| 교훈                    | 설명                                                                                                                      |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------|
| 준비와 진척을 나눔      | 첫 실행의 initializer가 기능 목록·진행 기록·`init.sh`·첫 commit을 만들고, 이후 coding 에이전트가 한 번에 하나씩 진척      |
| 구조화된 인계 자료      | 기능 목록은 JSON, 진행은 `claude-progress.txt`, 이력은 설명이 있는 git commit                                             |
| 끝에서 끝까지 확인      | 시험 없이 완료로 표시하는 일을 브라우저 자동화(Puppeteer·Playwright MCP)로 줄임                                           |
| 역할 분리               | planner(짧은 요청 → 명세), generator(구현), evaluator(실제 앱을 조작해 평가)                                              |
| 완료 기준을 먼저 합의   | 작업 묶음마다 generator와 evaluator가 "완료"를 먼저 정함(sprint contract)                                                 |
| 평가자 보정             | 점수 분해가 있는 few-shot 예시로 evaluator를 보정                                                                         |
| 문맥 초기화와 요약 구분 | reset은 새 에이전트로 깨끗이 시작, compaction은 요약해 이어감. compaction은 서두르는 경향(context anxiety)이 남을 수 있음 |
| 모델이 좋아지면 걷어냄  | 하네스의 각 부분은 "모델이 혼자 못 하는 일"에 대한 가정이므로 새 모델이 나오면 필요 없는 부분을 뺌                        |

### Birgitta Böckeler (Thoughtworks) 프레임워크

martinfowler.com 글 "Harness engineering for coding agent users"(2026-04-02, 2026-02-17 메모를 대체)의 틀입니다.

| 개념                     | 설명                                                                            |
|--------------------------|---------------------------------------------------------------------------------|
| Guides (feedforward)     | 행동하기 전에 방향을 잡음: 지침, 규칙, 예시, 템플릿                             |
| Sensors (feedback)       | 행동한 뒤 관찰해 스스로 고치게 함: 테스트, 린터, 리뷰                           |
| Computational            | 린터, 테스트, 타입 검사, 구조 분석 등 결정적이고 빠른 통제                      |
| Inferential              | LLM 기반 의미 분석, AI 코드 리뷰, LLM as judge (결정적이지 않음)                |
| 조절 영역                | Maintainability, Architecture fitness(fitness function), Behaviour(가장 어려움) |
| 쓰는 쪽 하네스           | 모델 → 도구 제작사의 builder 하네스 → 사용자가 더하는 user 하네스의 바깥 고리   |
| Keep quality left        | 문제는 일찍 찾을수록 고치기 싸므로 검사를 배포 경로의 앞쪽에 둠                 |
| Steering loop            | 같은 문제가 다시 나오면 사람이 사전·사후 통제를 고쳐 에이전트를 조종            |
| Harnessability           | 강한 타입·분명한 모듈 경계가 있는 코드일수록 통제를 걸기 쉬움                   |
| Context Engineering 연관 | 코딩 에이전트의 사용자 하네스는 컨텍스트 엔지니어링의 특정 형태라고 설명        |

### Mitchell Hashimoto의 반복 방식

| 단계 | 할 일                                                              |
|------|--------------------------------------------------------------------|
| 1    | 에이전트의 잘못된 행동을 발견                                      |
| 2    | 단순한 것이면 지침 파일에 그 행동을 막는 한 줄을 더함              |
| 3    | 반복되거나 확인이 필요한 것이면 스크립트·도구를 만들고 지침에 연결 |
| 4    | 다음 실행에서 같은 실수가 없어졌는지 확인                          |

그가 예로 든 Ghostty 저장소의 AGENTS.md는 각 줄이 실제로 관찰한 나쁜 행동에서 나왔다고 적었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 관련 도구 비교

| 도구/프레임워크              | 유형            | 하네스 엔지니어링 관련성                      |
|------------------------------|-----------------|-----------------------------------------------|
| AGENTS.md                    | 컨텍스트 파일   | 에이전트에 레포 구조/규칙을 전달하는 진입점   |
| CLAUDE.md                    | 컨텍스트 파일   | Claude Code 지시 파일 (없으면 AGENTS.md 읽음) |
| MCP (Model Context Protocol) | 프로토콜        | 에이전트-도구 인터페이스 표준                 |
| LangChain/LangGraph          | 프레임워크      | 에이전트 루프/메모리/도구 조합 프레임워크     |
| Google ADK                   | 프레임워크      | 멀티 에이전트 토폴로지 + 평가 파이프라인      |
| Kiro CLI                     | 에이전트 런타임 | skills, context, agents로 하네스 구성         |

### Prompt Engineering vs Harness Engineering

| 구분   | Prompt Engineering           | Harness Engineering                        |
|--------|------------------------------|--------------------------------------------|
| 초점   | 에이전트에게 "무엇을 말할지" | 에이전트가 "작업할 환경을 어떻게 구성할지" |
| 대상   | 단일 프롬프트/응답           | 전체 작업 사이클                           |
| 지속성 | 일회성                       | 레포에 버전 관리되는 영구 아티팩트         |
| 검증   | 수동 확인                    | 자동화된 피드백 루프                       |
| 확장성 | 프롬프트 수만큼 선형 확장    | 한 번 설계하면 모든 작업에 적용            |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실전 적용

### 최소 하네스 구성 (시작점)

```
project/
├── AGENTS.md          # Short entry point linking detailed guidance
├── ARCHITECTURE.md    # Domain/layer map
├── CLAUDE.md          # Claude Code (@AGENTS.md import)
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
#!/bin/bash
# scripts/lint-arch.sh — Architecture boundary linter
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

### 통제 점검표

Böckeler의 두 축을 겹쳐 빈 칸을 찾습니다. 칸마다 하나 이상 있으면 최소 하네스로 봅니다.

| 구분           | Computational (결정적)                   | Inferential (LLM 판단)              |
|----------------|------------------------------------------|-------------------------------------|
| Guides (사전)  | 코드 생성 템플릿, 스키마, 형식 도구 설정 | AGENTS.md 규칙, skill, 예시 코드    |
| Sensors (사후) | 린터, 타입 검사, 구조 테스트, 링크 검사  | AI 리뷰, 평가자 모델, 시나리오 판정 |

- 결정적 검사로 확인할 수 있는 것(파일 존재, 링크, 빌드, 테스트)은 LLM 판단에 맡기지 않습니다.
- 지침 한 줄로 막은 실수가 다시 나오면 같은 내용을 검사 도구로 옮깁니다.
- 새 모델로 바꾸면 각 통제가 아직 필요한지 다시 봅니다. 필요 없는 통제는 문맥과 시간을 씁니다.

### 향후 도입 검토

| 항목            | 내용                                              | 시점                        |
|-----------------|---------------------------------------------------|-----------------------------|
| AGENTS.md       | 프로젝트별 에이전트 진입점 (목차 방식, ~100줄)    | 멀티 에이전트/협업 필요 시  |
| Eval 파이프라인 | 에이전트 출력물 자동 평가 (시나리오 기반)         | 에이전트 작업 비중 증가 시  |
| 실행 격리       | Docker 등 실행 sandbox와 git worktree의 작업 분리 | 실제 권한·작업 분리 필요 시 |

### 문서·참고 저장소 조사에 적용할 최소 구성

아래는 앞의 제품 개발 사례를 문서 조사에 맞춘 예시입니다. 실제 개선 작업의 행동 기준은 31 중앙 저장소에서 관리하며, 이 문서는 기술적 구성과 출처를 설명합니다.

| 파일                      | 역할                                          | 확인할 증거                                    |
|---------------------------|-----------------------------------------------|------------------------------------------------|
| AGENTS.md                 | 상세 절차와 현재 상태로 연결하는 진입점       | 기존 지침을 보존하고 링크가 실제 파일을 가리킴 |
| README.md의 중앙 안내     | 31에서 관리하는 workflow·행동 지침으로 연결   | 해당 작업의 대상·완료 조건·검사 범위를 확인    |
| .codex/REFERENCE_STATE.md | 확인한 출처, 실행·검증·미실행, 남은 작업 기록 | 다음 세션에서 Git 상태와 대조한 뒤 재개        |

`REFERENCE_STATE.md`를 만드는 것만으로 자동 로드가 되지는 않습니다. 진입 지침에서 읽도록 연결하고, 새 실행에서 해당 안내를 실제로 읽었는지 확인합니다. [Codex AGENTS.md 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

작업 완료는 출처 기록, 변경 내용 검토, 관련 검사 통과, 요청된 브랜치의 commit/push 확인으로 판단합니다. 설치 안내를 읽은 상태와 설치·실행을 검증한 상태는 따로 기록합니다. 구체적인 반복·정지 조건은 [Loop Engineering의 자료 조사 예시](./loop_engineering.md#자료-조사에-사용하는-제한된-루프)를 참고합니다.

### 실행기·오케스트레이터를 검토할 때

[Harness/Loop 참고 저장소 목록](../../_reference/github_references.md#4-harnessloop)에서 구현체와 자료 모음을 구분합니다. 짧은 지침과 검사만 필요한 작업에 외부 실행기 전체를 바로 도입할 필요는 없습니다.

Anthropic의 장기 실행 사례는 초기 환경 준비와 후속 작업을 나누고, 기능 목록·진행 기록·실제 동작 검사를 통해 세션을 연결합니다. 문서 조사에서는 이를 조사 목록·출처 기록·링크 검사로 바꿔 사용할 수 있습니다. [장기 실행 하네스 사례](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

평가자 모델을 추가할 때는 검증 가능한 기준과 사례를 먼저 정합니다. 단순한 파일 존재·링크·빌드 검사는 결정론적 도구를 사용하고, 의미나 사용성 판단이 필요한 곳에 별도 평가를 선택합니다. [Anthropic의 하네스 설계 사례](https://www.anthropic.com/engineering/harness-design-long-running-apps)

git worktree는 작업 파일을 분리하는 수단입니다. OS 권한·네트워크·비밀 접근을 제한하는 보안 sandbox와는 역할이 다릅니다. 위 Bash 린터도 구조를 설명하는 예시이며, 실제 프로젝트에서는 언어별 import 규칙과 Windows 실행 환경에 맞춰 검증해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

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

🟡 아래는 관심사를 비교한 정리이며 공식 계층이나 성숙도 순서가 아닙니다.

| 분야                | 질문                               | 산출물 예시                                 |
|---------------------|------------------------------------|---------------------------------------------|
| Prompt Engineering  | 어떤 지시를 전달할 것인가          | 작업 요청과 제약                            |
| Context Engineering | 어떤 정보를 언제 읽게 할 것인가    | 필요한 문서·상태의 전달 경로                |
| Harness Engineering | 어떤 환경과 피드백을 제공할 것인가 | 도구, 지침, 검사, 상태 저장, 격리           |
| Loop Engineering    | 무엇을 반복하고 언제 멈출 것인가   | 다음 행동 선택, 결과 평가, 재시도·정지 조건 |

하네스 안의 관찰·행동 루프와 여러 실행을 다시 호출하는 외부 루프는 서로 다른 범위입니다. Addy Osmani는 후자를 중심으로 설명합니다. 하네스와 루프를 항상 한쪽이 다른 쪽을 포함하는 단일 계층으로 고정하지 않고, [Loop Engineering의 관계 설명](./loop_engineering.md#7-harness-engineering과의-관계)처럼 실행 범위를 명시합니다. [Loop Engineering 원문](https://addyosmani.com/blog/loop-engineering/)

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                              | 원인                                     | 해결                                               |
|-----------------------------------|------------------------------------------|----------------------------------------------------|
| 에이전트가 같은 실수를 반복       | 검증 루프 부재                           | 린터/구조 테스트 추가, CI에서 자동 차단            |
| 에이전트가 아키텍처를 무시        | AGENTS.md에 규칙만 있고 기계적 강제 없음 | 커스텀 린터로 경계를 강제                          |
| 컨텍스트 윈도우 초과              | AGENTS.md가 너무 길음                    | 목차 방식으로 전환, progressive disclosure         |
| 코드 스타일 일관성 저하           | 모델이 기존 패턴을 복제하여 drift        | 정기 cleanup 에이전트 운영                         |
| 에이전트가 외부 지식에 접근 불가  | Slack/Docs의 암묵지가 레포에 없음        | 모든 결정을 레포 내 마크다운으로 기록              |
| 일이 남았는데 완료라고 보고       | 진척만 보고 끝났다고 판단, 시험 생략     | 기능 목록에 통과 여부를 두고 끝에서 끝까지 확인    |
| 한 번에 전부 만들다 중간에 무너짐 | 작업 단위가 큼                           | 한 실행에 기능 하나, 끝날 때 commit·진행 기록      |
| 문맥이 차면 서둘러 마무리         | context anxiety                          | 요약 대신 새 실행으로 시작하고 인계 자료를 읽게 함 |
| 모델을 바꾼 뒤 오히려 느려짐      | 옛 모델 한계를 메우던 통제가 남음        | 통제별로 빼 보고 결과가 같으면 걷어냄              |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Mitchell Hashimoto: [My AI Adoption Journey](https://mitchellh.com/writing/my-ai-adoption-journey) (2026-02-05) — ★★☆☆☆
- OpenAI: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11) — ★★★☆☆
- Anthropic: [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) — ★★★☆☆
- Anthropic: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — ★★★☆☆
- OpenAI: [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) — ★★★☆☆
- [Harness/Loop 참고 저장소](../../_reference/github_references.md#4-harnessloop)
- martinfowler.com: [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) (2026-04-02) — ★★☆☆☆
- LangChain: [The Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) (2026-03-10) — ★★☆☆☆
- [1차 자료 대조 노트](../../_reference/harness_loop_engineering_sources_notes.md) (확인일 2026-11-28)
- GitHub: [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) — ★★☆☆☆
- GitHub: [walkinglabs/awesome-harness-engineering](https://github.com/walkinglabs/awesome-harness-engineering) — ★★☆☆☆
- Learn Harness Engineering: [walkinglabs.github.io](https://walkinglabs.github.io/learn-harness-engineering/en/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-06-19

**마지막 업데이트**: 2026-11-28

© 2026 siasia86. Licensed under CC BY 4.0.
