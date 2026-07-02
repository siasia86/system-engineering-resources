# Loop Engineering

에이전트에게 매번 프롬프트하는 대신, 에이전트를 프롬프트하는 시스템을 설계하는 작업 방식입니다. Harness Engineering이 "에이전트가 작업할 환경"을 설계한다면, Loop Engineering은 "그 환경에서 에이전트가 자율적으로 반복 실행되는 루프"를 설계합니다.

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 루프의 구성 요소](#2-루프의-구성-요소) / [3. 메모리](#3-메모리)                             |
| [4. 도구별 구현](#4-도구별-구현) / [5. 루프 설계 예시](#5-루프-설계-예시) / [6. 한계와 주의사항](#6-한계와-주의사항) |
| [7. Harness Engineering과의 관계](#7-harness-engineering과의-관계) / [8. 용어 정리](#8-용어-정리)                    |

---

## 1. 개요

| 항목      | 값                                                                                 |
|-----------|------------------------------------------------------------------------------------|
| 정의      | 에이전트를 자동으로 반복 실행하며, 작업 발견·분배·검증·기록을 수행하는 시스템 설계 |
| 등장 시기 | 2026년 6월 (Addy Osmani 블로그, Peter Steinberger, Boris Cherny)                   |
| 핵심 전환 | "에이전트에 프롬프트" → "에이전트에 프롬프트하는 루프를 설계"                      |
| 전제 조건 | 코딩 에이전트 (Codex, Claude Code 등) + Skills + CI/CD 환경                        |
| 주의      | 초기 단계, 토큰 비용 주의 필수                                                     |

### 핵심 인용

> "더 이상 코딩 에이전트에 프롬프트하지 말고, 에이전트에 프롬프트하는 루프를 설계하라" — Peter Steinberger

> "이제 Claude에 프롬프트하지 않고, Claude에 프롬프트하고 무엇을 할지 정하는 루프를 돌린다. 내 일은 루프를 작성하는 것" — Boris Cherny (Anthropic)

### 이전 방식과의 비교

| 이전 (2024~2025)               | Loop Engineering (2026~)          |
|--------------------------------|-----------------------------------|
| 사람이 매 턴마다 직접 프롬프트 | 시스템이 에이전트를 프롬프트      |
| 한 세션 내 주고받기            | 스케줄/이벤트 기반 자동 실행      |
| 사람이 도구를 직접 쥐고 있음   | 루프가 작업을 찾아 분배·검증·기록 |
| 컨텍스트를 매번 재설명         | Skills + Memory로 누적            |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 루프의 구성 요소

루프에는 다섯 가지 필수 요소가 있습니다.

### 2.1 Automations — 루프의 심장 박동

| 항목         | 설명                                                   |
|--------------|--------------------------------------------------------|
| 역할         | 스케줄에 따라 발동하여 작업을 발견·분류(triage)        |
| 동작         | 매일/매시간 실행 → 이슈 탐색 → 결과를 인박스에 분류    |
| 결과 없을 때 | 스스로 아카이브 (불필요한 알림 없음)                   |
| 활용 예시    | 일일 이슈 triage, CI 실패 요약, 커밋 브리핑, 버그 사냥 |

### 2.2 Worktrees — 병렬 충돌 방지

| 항목 | 설명                                                               |
|------|--------------------------------------------------------------------|
| 역할 | 여러 에이전트가 같은 repo에서 동시에 작업해도 충돌하지 않도록 격리 |
| 원리 | git worktree — 같은 히스토리를 공유하면서 각자 별도 작업 디렉토리  |
| 한계 | 기계적 충돌은 해결하지만 실제 병렬 수는 사람의 리뷰 대역폭이 결정  |

### 2.3 Skills — 반복 설명 제거

| 항목    | 설명                                                                     |
|---------|--------------------------------------------------------------------------|
| 역할    | 에이전트가 매 세션 프로젝트를 0에서 재유도하지 않도록 의도를 외부에 기록 |
| 포맷    | SKILL.md 파일 (지시문 + 메타데이터) + 선택적 스크립트·참조·에셋          |
| 효과    | 한 번 적어두면 매 실행마다 읽힘 → 복리처럼 누적                          |
| 없을 때 | 매 사이클마다 프로젝트 전체를 다시 설명해야 함 (intent debt 발생)        |

### 2.4 Plugins / Connectors — 외부 도구 연결

| 항목     | 설명                                                                             |
|----------|----------------------------------------------------------------------------------|
| 역할     | 파일시스템 밖의 도구(이슈 트래커, DB, API, Slack)에 에이전트를 연결              |
| 프로토콜 | MCP (Model Context Protocol) 기반                                                |
| 호환성   | Codex용 connector가 Claude Code에서도 동작 (동일 프로토콜)                       |
| 차이점   | "수정안이 있다"고 말하는 에이전트 vs PR 열고 티켓 연결하고 채널에 핑 보내는 루프 |

### 2.5 Sub-agents — Maker와 Checker 분리

| 항목 | 설명                                                                  |
|------|-----------------------------------------------------------------------|
| 역할 | 코드를 쓰는 쪽과 검사하는 쪽을 분리하여 자기 채점 방지                |
| 원리 | 다른 지시문·다른 모델을 가진 두 번째 에이전트가 첫 번째의 결과를 검증 |
| 구조 | 탐색 에이전트 + 구현 에이전트 + 검증 에이전트                         |
| 비용 | 토큰 추가 소모 → 검증이 가치 있는 곳에 선별 사용                      |

### 구성 요소 비교 (Codex vs Claude Code)

| 구성 요소   | Codex                                        | Claude Code                            |
|-------------|----------------------------------------------|----------------------------------------|
| Automations | Automations 탭 (프로젝트·프롬프트·주기 설정) | /loop + cron + GitHub Actions          |
| Worktrees   | 내장 worktree 지원                           | --worktree 플래그, isolation: worktree |
| Skills      | $skill-name 호출, /skills                    | SKILL.md, 자동 로드                    |
| Plugins     | MCP connector                                | MCP connector (동일 프로토콜)          |
| Sub-agents  | .codex/agents/ TOML 정의                     | .claude/agents/ + agent teams          |
| 정지 조건   | /goal (pause·resume·clear)                   | /goal (별도 모델이 완료 판단)          |

### Kiro CLI 매핑

Kiro는 Claude 모델 기반 CLI 에이전트로, Loop Engineering 구성 요소를 다음과 같이 구현합니다.

| 구성 요소   | Kiro 구현                                                     | 파일/경로                                          |
|-------------|---------------------------------------------------------------|----------------------------------------------------|
| Skills      | `~/.kiro/skills/*/SKILL.md` (전역) + 프로젝트 `.kiro/skills/` | 세션 시작 시 자동 로드                             |
| Memory      | `~/.kiro/memory.md`                                           | 세션 간 유지 정보 (환경, 프로젝트 경로, 작업 규칙) |
| Automations | context entries + 사용자 정의 prompt (md 파일)                | `doc-consistency-review`, `md-review` 등           |
| Sub-agents  | skill 기반 분리 (`code-review`, `doubt-driven-infra`)         | 검증/리뷰 역할을 skill로 정의                      |
| Worktrees   | git branch + 수동 격리                                        | 아직 내장 worktree 미지원                          |
| Connectors  | `execute_bash` + `use_aws` + 파일 도구                        | MCP 대신 내장 도구로 외부 연결                     |
| 정지 조건   | `md-style-check 0건`, `ast.parse OK`, 테스트 통과             | skill에 검증 규칙 명시                             |

#### 현재 우리 프로젝트의 루프 구조

```
~/.kiro/
├── memory.md                    # Memory (환경, 경로, 규칙 요약)
├── skills/
│   ├── work-rules/SKILL.md      # Automation 규칙 (삭제 전 확인, 즉시 PLAN 기재)
│   ├── code-review/SKILL.md     # Sub-agent: 코드 리뷰 체크리스트
│   ├── doubt-driven-infra/      # Sub-agent: 인프라 결정 검증
│   ├── python-script-template/  # Skill: Python 작성 규칙
│   ├── readme-template/         # Skill: 푸터 템플릿
│   └── md-link-check/           # Skill: 링크 검증
└── markdown/STYLE.md            # Skill: 마크다운 스타일

/opt/00_chobo_ansible/
├── TODO.md                      # Memory: 전체 할 일 (세션 시작 진입점)
├── PLAN.md (각 디렉토리)         # Memory: 이슈 기록 + 상태
└── scripts/CHANGELOG.md         # Memory: 변경 이력
```

#### Kiro에서의 루프 동작 흐름

```
[session start]
      │
      v
[memory.md + skills 자동 로드]
      │
      v
[TODO.md 확인 → 다음 작업 결정]
      │
      v
[skill 기반 작업 수행]
  - python-script-template → 스크립트 작성
  - code-review → 검증
  - md-style-check → 문서 품질
      │
      v
[검증 통과 확인]
  - ast.parse OK
  - md-style-check 0건
  - aws_security_check.sh 통과
      │
      v
[PLAN.md 이슈 기록 + TODO.md 상태 갱신]
      │
      v
[session end → memory.md 자동 갱신]
```

🟡 Kiro CLI는 현재 단일 세션 내 루프입니다. Codex/Claude Code의 `/loop`(세션 간 자동 반복)은 아직 미지원이지만, `memory.md` + `TODO.md` + `PLAN.md` 조합으로 세션 간 상태 연속성을 확보하고 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 메모리

여섯 번째 요소로, 단일 대화 밖에서 상태를 보존합니다.

| 항목 | 설명                                                              |
|------|-------------------------------------------------------------------|
| 형태 | markdown 파일, Linear 보드, 상태 파일 등                          |
| 위치 | 디스크 (컨텍스트가 아님) — 에이전트는 잊어도 repo는 잊지 않음     |
| 역할 | 완료된 것과 다음 할 것을 보관                                     |
| 핵심 | 모델은 실행 사이에 모든 것을 잊으므로 메모리가 디스크에 있어야 함 |

### 메모리 설계 패턴

```
project-root/
├── .memory/
│   ├── state.md          # 현재 진행 상태 (뭘 시도했고, 뭐가 통과했고, 뭐가 열려있나)
│   ├── decisions.md      # 설계 결정 기록 (왜 이렇게 했는지)
│   └── triage.md         # 오늘의 작업 목록 (automation이 작성)
├── .kiro/skills/         # 프로젝트 컨벤션, 빌드 단계
└── TODO.md               # 전체 할 일 목록
```

🟡 메모리가 없으면 루프가 매 사이클마다 "처음부터" 시작합니다. 단순해 보이지만 모든 장기 실행 에이전트가 의존하는 핵심입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 도구별 구현

### Codex (OpenAI)

```
Automations 탭:
  - 프로젝트 선택
  - 실행할 프롬프트 작성
  - 주기 설정 (매일, 매시간 등)
  - 로컬 체크아웃 / 백그라운드 worktree 선택

결과 처리:
  - 발견한 실행 → Triage 인박스
  - 아무것도 없는 실행 → 자동 아카이브

/goal:
  - 검증 가능한 정지 조건 설정
  - 조건 충족까지 자동 반복
  - pause / resume / clear 지원
```

### Claude Code (Anthropic)

🟡 아래 `/loop`, `/goal` 명령은 Addy Osmani 블로그 (2026-06) 및 Boris Cherny 인터뷰 기반입니다. 공식 릴리즈 문서와 차이가 있을 수 있습니다.

```
/loop:
  - 정해진 주기마다 프롬프트 재실행
  - cron 작업 스케줄링
  - hooks로 라이프사이클 특정 시점에 셸 명령 발사

/goal:
  - 조건이 참이 될 때까지 계속 실행
  - 매 턴 후 별도 모델이 완료 여부 검사 (maker != checker)
  - 예: "test/auth의 모든 테스트 통과, lint clean"

장기 실행:
  - GitHub Actions로 위임 가능 (노트북 닫은 뒤에도 계속)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 루프 설계 예시

### 일일 triage + 자동 수정 루프

```
[daily morning automation]
      │
      v
[triage skill invoked]
  - check yesterday CI failures
  - check open issues
  - read recent commits
      │
      v
[write results to state.md]
      │
      v
[for each actionable item]
  ┌────────────────────────────────────────┐
  │  open worktree (isolated)              │
  │  sub-agent 1: draft fix                │
  │  sub-agent 2: review against skills +  │
  │               existing tests           │
  └────────────────────────────────────────┘
      │
      v
[connector: open PR + update ticket]
      │
      v
[unresolved items → triage inbox]
      │
      v
[update state.md → resume tomorrow]
```

### 핵심 포인트

- 위 단계 중 어느 것도 사람이 프롬프트하지 않음
- 한 번 설계하면 Codex든 Claude Code든 동일 루프
- state.md가 전체의 척추 — 다음 날 실행이 오늘 멈춘 지점에서 이어감

[⬆ 목차로 돌아가기](#목차)

---

## 6. 한계와 주의사항

### 루프가 해결하지 않는 세 가지

| 문제                            | 설명                                                                 | 대응                                            |
|---------------------------------|----------------------------------------------------------------------|-------------------------------------------------|
| 검증은 여전히 사람 몫           | 무인 루프 = 무인 실수. "done"은 증명이 아니라 주장                   | 리뷰 시간 확보, CI 게이트 필수                  |
| Comprehension Debt (이해 부채)  | 루프가 만든 코드를 읽지 않으면 존재하는 것과 이해하는 것의 간극 확대 | 정기적으로 생성된 코드 읽기, 아키텍처 이해 유지 |
| Cognitive Surrender (인지 포기) | 루프가 돌면 의견 갖기를 멈추고 결과를 그대로 수용                    | 판단을 갖고 설계 (사고를 피하려고 쓰면 가속제)  |

### 비용 주의

| 항목            | 영향                                                     |
|-----------------|----------------------------------------------------------|
| Sub-agent       | 각각 모델·도구 호출 → 토큰 2~3배                         |
| /goal 반복      | 조건 불충족 시 계속 반복 → 예산 초과 가능                |
| Automation 주기 | 매시간 실행 시 일일 비용 24배                            |
| Token rich/poor | 사용 가능 토큰 예산에 따라 루프 설계가 근본적으로 달라짐 |

### 적용 기준

| 상황                               | 루프 적합도 | 이유                           |
|------------------------------------|-------------|--------------------------------|
| 반복적 triage (CI 실패, 이슈 분류) | ✅ 높음     | 판단 단순, 검증 쉬움           |
| 코드 리팩토링 (일괄)               | ✅ 높음     | 패턴화 가능, 테스트로 검증     |
| 새로운 아키텍처 설계               | ❌ 낮음     | 창의적 판단, 이해 필수         |
| 보안 민감 변경                     | ❌ 낮음     | 검증 비용 > 자동화 이점        |
| 문서 생성/갱신                     | 🟡 중간     | 구조화 가능하나 품질 검증 필요 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. Harness Engineering과의 관계

```
┌─────────────────────────────────────────────────────┐
│  Loop Engineering                                   │
│  "auto-repeat agent execution loop design"          │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  Harness Engineering                          │  │
│  │  "agent environment design"                   │  │
│  │  (repo, CI, sandbox, observability)           │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  Prompt Engineering                     │  │  │
│  │  │  "what to say to the agent"             │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

| 레벨 | 이름                | 초점                                 | 범위             |
|------|---------------------|--------------------------------------|------------------|
| L0   | Prompt Engineering  | 단일 프롬프트 품질                   | 1 턴             |
| L1   | Harness Engineering | 에이전트 환경 (도구, 컨텍스트, 검증) | 1 세션           |
| L2   | Loop Engineering    | 자율 반복 실행 + 검증 루프           | 세션 이상 (지속) |

🟡 Loop Engineering은 Harness Engineering을 전제로 합니다. 좋은 하네스 없이 루프만 돌리면 실패를 자동으로 반복합니다.

🟡 L0/L1/L2 넘버링은 이 문서의 정리이며, 기사 원문에는 "이전 글의 상위에 위치"라는 관계만 언급됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 용어 정리

| 용어                | 정의                                                          |
|---------------------|---------------------------------------------------------------|
| Loop                | 목적을 정의하면 AI가 완료될 때까지 반복하는 재귀적 목표       |
| Automation          | 스케줄에 따라 발동하여 작업을 발견·분류하는 트리거            |
| Worktree            | git worktree 기반 격리 작업 디렉토리 (에이전트 간 충돌 방지)  |
| Skill               | 프로젝트 지식을 SKILL.md로 기록 (매 세션 자동 로드)           |
| Connector           | MCP 기반으로 외부 도구(이슈 트래커, DB, Slack)에 연결         |
| Sub-agent           | 별도 지시문·모델을 가진 보조 에이전트 (Maker-Checker 분리)    |
| Memory              | 단일 대화 밖에서 상태를 보존하는 디스크 기반 파일             |
| /goal               | 검증 가능한 정지 조건이 참이 될 때까지 자동 반복하는 명령     |
| /loop               | 정해진 주기마다 프롬프트를 재실행하는 명령                    |
| Triage              | 발견된 작업의 우선순위 분류 (자동화의 출력)                   |
| Intent Debt         | 에이전트가 의도의 빈틈을 추측으로 메우면서 발생하는 품질 저하 |
| Comprehension Debt  | 직접 쓰지 않은 코드가 늘면서 이해도가 떨어지는 현상           |
| Cognitive Surrender | 루프 결과를 비판 없이 수용하는 인지적 포기 상태               |
| Orchestration Tax   | 병렬 에이전트 관리에 드는 사람의 오버헤드                     |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Addy Osmani — Loop Engineering: [addyo.substack.com](https://addyo.substack.com/) — ★★★☆☆
- [Harness Engineering](./harness_engineering.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-02

**마지막 업데이트**: 2026-07-02

© 2026 siasia86. Licensed under CC BY 4.0.
