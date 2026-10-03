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
| 전제 조건 | 실행 도구와 목표·검증·정지 조건; Skills·CI/CD는 필요에 따라 선택                   |
| 주의      | 초기 단계, 토큰 비용 주의 필수                                                     |

### 원문에서 참고할 설계 관점

Addy Osmani는 에이전트를 다시 호출하는 외부 루프를 설계 대상으로 설명하며, 후속 글에서 검증 가능한 목표·제약·정지 조건과 결과 검토를 강조합니다. 아래 예시는 이 관점을 문서 조사에 맞춘 정리입니다. [Loop Engineering](https://addyosmani.com/blog/loop-engineering/), [Practical Loop Engineering](https://addyosmani.com/blog/practical-loop-engineering/)

### 이전 방식과의 비교

| 사람이 이끄는 반복             | 자동 호출을 포함한 반복           |
|--------------------------------|-----------------------------------|
| 사람이 매 턴마다 직접 프롬프트 | 시스템이 에이전트를 프롬프트      |
| 한 세션 내 주고받기            | 스케줄/이벤트 기반 자동 실행      |
| 사람이 도구를 직접 쥐고 있음   | 루프가 작업을 찾아 분배·검증·기록 |
| 컨텍스트를 매번 재설명         | Skills + Memory로 누적            |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 루프의 구성 요소

아래 다섯 가지는 작업에 따라 선택하는 구성 요소입니다. 작은 자료 조사에는 목표·검사·정지 조건·상태 기록으로 시작할 수 있으며, scheduler·worktree·skill·connector·sub-agent를 모두 갖출 필요는 없습니다.

### 2.1 Automations — 루프의 심장 박동

| 항목         | 설명                                                   |
|--------------|--------------------------------------------------------|
| 역할         | 스케줄에 따라 발동하여 작업을 발견·분류(triage)        |
| 동작         | 매일/매시간 실행 → 이슈 탐색 → 결과를 인박스에 분류    |
| 결과 없을 때 | 스스로 아카이브 (불필요한 알림 없음)                   |
| 활용 예시    | 일일 이슈 triage, CI 실패 요약, 커밋 브리핑, 버그 사냥 |

### 2.2 Worktrees — 병렬 충돌 방지

| 항목 | 설명                                                              |
|------|-------------------------------------------------------------------|
| 역할 | agent별 작업 디렉토리를 나누어 같은 파일의 동시 수정 충돌을 줄임  |
| 원리 | git worktree — 같은 히스토리를 공유하면서 각자 별도 작업 디렉토리 |
| 한계 | 기계적 충돌은 해결하지만 실제 병렬 수는 사람의 리뷰 대역폭이 결정 |

### 2.3 Skills — 반복 설명 제거

| 항목    | 설명                                                                     |
|---------|--------------------------------------------------------------------------|
| 역할    | 에이전트가 매 세션 프로젝트를 0에서 재유도하지 않도록 의도를 외부에 기록 |
| 포맷    | SKILL.md 파일 (지시문 + 메타데이터) + 선택적 스크립트·참조·에셋          |
| 효과    | 이름·설명으로 발견하고, 선택한 Skill의 본문을 필요할 때 읽어 재사용      |
| 없을 때 | 재사용할 절차가 없으면 같은 작업 규칙을 반복 설명해야 할 수 있음         |

Codex는 시작 시 Skill 메타데이터를 읽고, 명시적 호출 또는 작업과 설명의 일치로 선택한 Skill의 `SKILL.md` 본문을 읽습니다. 설치한 모든 Skill의 본문을 매 실행마다 읽는다는 뜻은 아닙니다. [공식 Skills 설명](https://learn.chatgpt.com/docs/build-skills)

### 2.4 Plugins / Connectors — 외부 도구 연결

| 항목     | 설명                                                                             |
|----------|----------------------------------------------------------------------------------|
| 역할     | 파일시스템 밖의 도구(이슈 트래커, DB, API, Slack)에 에이전트를 연결              |
| 프로토콜 | MCP (Model Context Protocol) 기반                                                |
| 호환성   | MCP 규격의 서버는 연결 후보지만, 클라이언트별 transport·인증·도구 지원 확인 필요 |
| 차이점   | "수정안이 있다"고 말하는 에이전트 vs PR 열고 티켓 연결하고 채널에 핑 보내는 루프 |

### 2.5 Sub-agents — Maker와 Checker 분리

| 항목 | 설명                                                                       |
|------|----------------------------------------------------------------------------|
| 역할 | 구현 agent와 검토 agent를 분리하여 자기 검토의 한계를 줄임                 |
| 원리 | 별도 작업 지침과 context를 가진 agent가 결과를 검증; 모델은 같을 수도 있음 |
| 구조 | 탐색 에이전트 + 구현 에이전트 + 검증 에이전트                              |
| 비용 | 토큰 추가 소모 → 검증이 가치 있는 곳에 선별 사용                           |

### 목표 유지와 주기 실행의 구분

| 방식               | Codex                           | Claude Code                                                         |
|--------------------|---------------------------------|---------------------------------------------------------------------|
| 목표까지 계속 작업 | thread에 목표를 유지하는 /goal  | 세션의 완료 조건을 평가하는 /goal                                   |
| 주기 실행          | Automations 등 별도 스케줄 기능 | /loop 등 세션 스케줄 기능                                           |
| 결과 검증          | 실행한 검사 결과와 산출물 확인  | evaluator는 대화에 제시된 증거를 평가; 파일·명령의 독립 검사는 별도 |

두 도구의 `/goal`은 같은 상태·명령·수명 주기를 보장하지 않습니다. 공식 설명과 사용 중인 버전을 확인하며, MCP 서버를 공유할 수 있어도 plugin 패키지·인증 설정이 그대로 호환되는 것은 아닙니다. [Codex Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex), [Claude Code Goals](https://code.claude.com/docs/en/goal)

### 파일 기반 운영 예시 (Kiro 계열 프로젝트)

아래는 파일로 지침·상태를 연결하는 운영 예시입니다. 특정 Kiro 버전의 기능 지원표나 현재 작업공간에 적용된 설정이라는 뜻은 아닙니다. 자동 발견·호출·hook은 해당 버전과 실제 실행 결과로 확인합니다.

| 관심사    | 예시                                         | 확인할 사항                             |
|-----------|----------------------------------------------|-----------------------------------------|
| 지침      | 프로젝트의 .kiro/skills/ 등 도구별 지침 경로 | 설치 버전의 발견·호출 방식              |
| 상태      | memory.md·TODO.md·PLAN.md                    | 저장 위치와 다음 실행에서 읽을 경로     |
| 역할 분리 | 작성과 검토를 다른 작업으로 분리             | skill 선택과 실제 sub-agent 실행을 구분 |
| 작업 분리 | 별도 clone 또는 git worktree                 | 같은 파일·branch의 동시 변경 방지       |
| 외부 도구 | 필요한 CLI·MCP 연결                          | 사용 가능 도구·인증·실행 범위           |
| 검증      | Markdown 검사·문법 검사·관련 테스트          | 실제 명령·결과·미실행 기록              |

#### 프로젝트 구조 예시

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

example-project/
├── TODO.md                      # Memory: 전체 할 일 (세션 시작 진입점)
├── PLAN.md (각 디렉토리)         # Memory: 이슈 기록 + 상태
└── scripts/CHANGELOG.md         # Memory: 변경 이력
```

#### Kiro에서의 루프 동작 흐름

```
[session start]
      │
      v
[read configured guidance and state]
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
[session end → memory.md 갱신 절차 실행]
```

🟡 위 구조는 단일 세션 운영 예시이며 현재 32·41의 설치·자동 로드 증거가 아닙니다. `memory.md` + `TODO.md` + `PLAN.md`에 상태를 기록하고 다음 실행에서 읽도록 연결해 세션 간 연속성을 확보합니다. `/goal`의 목표 유지와 주기 실행 스케줄은 별도 기능이며, 도구별 지원 명령은 사용 중인 버전에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 메모리

단일 대화 밖에서 상태를 보존합니다. 장기 작업에서는 완료 항목·검증·다음 행동을 새 실행에 전달하는 경로를 함께 정합니다.

| 항목 | 설명                                                                 |
|------|----------------------------------------------------------------------|
| 형태 | markdown 파일, Linear 보드, 상태 파일 등                             |
| 위치 | 디스크 (컨텍스트가 아님) — 에이전트는 잊어도 repo는 잊지 않음        |
| 역할 | 완료된 것과 다음 할 것을 보관                                        |
| 핵심 | 새 실행에 필요한 상태를 저장하고, 다음 실행에서 불러오는 경로를 정함 |

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

🟡 상태 파일을 저장하는 것만으로 다음 실행에 자동 로드되지는 않습니다. 프롬프트·지침·실행기에서 해당 파일을 읽도록 연결하고, 재개된 세션의 대화 이력과도 구분합니다.

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
  - 목표가 활성 상태이고 예산 안에 있을 때 후속 작업 진행
  - 완료·사용자 중단·예산 한도·진행을 막는 조건에서 정지
  - pause / resume / clear 지원
```

`/goal`은 현재 thread에 목표를 유지하는 기능이며, 정해진 시각에 새 작업을 실행하는 스케줄과는 구분합니다. [공식 Goals 설명](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)

### Claude Code (Anthropic)

`/goal`은 완료 조건을 설정하고 후속 턴을 진행합니다. 별도 evaluator는 대화에 나타난 증거로 조건을 판단하며 독립적으로 파일을 읽거나 명령을 실행하지 않습니다. 조건에 검사 방법과 턴·시간 상한을 포함하고 실제 결과물 검토를 별도로 수행합니다. [공식 Goals 설명](https://code.claude.com/docs/en/goal)

`/loop`는 주기에 따른 재호출 기능입니다. 공식 문서의 반복 예약은 생성 후 7일 만료가 있으며 실행 중인 세션·재개 방식에 제약이 있습니다. 지속 예약은 별도 scheduling 기능을 확인합니다. hooks·목표 유지·주기 실행을 같은 기능으로 묶지 않습니다. [공식 Scheduled tasks 설명](https://code.claude.com/docs/en/scheduled-tasks)

[⬆ 목차로 돌아가기](#목차)

---

## 5. 루프 설계 예시

### 자료 조사에 사용하는 제한된 루프

아래는 설계 예시입니다. 실제 `32 조사 → 41 clone·기록 → 35 도구별 구현`의 행동 기준과 공용·개인 범위는 [31 중앙 workflow](https://github.com/siasia86/31_governances/blob/yunli/.governance/repository/agent_skill_improvement_workflow.md)에서 관리합니다.

| 항목   | 예시                                                               |
|--------|--------------------------------------------------------------------|
| 목표   | 참고 저장소 하나의 목적·지원 근거·의존성을 출처와 함께 기록        |
| 입력   | 공식 문서·README·license·확인한 commit                             |
| 행동   | 필요한 파일을 읽고 해당 조사 문서만 갱신                           |
| 검증   | 출처 대조·local link·heading/fragment·style·diff 검사              |
| 정지   | 필수 검사와 요청한 branch의 원격 반영 확인; 한도 종료는 미완료     |
| 재시도 | 같은 원인에 새 수정이나 근거 없이 재실행하지 않고 상한을 사전 지정 |
| 재개   | 상태 기록을 읽고 현재 Git 상태·출처 commit·미완료와 대조           |

상태에는 `대상/출처/확인 commit/실행/검증/미실행/다음 작업`을 남깁니다. 읽을 경로를 지침·프롬프트·인계에 연결해야 하며 파일 저장만으로 자동 재개가 구현되는 것은 아닙니다. 처음에는 현재 세션에서 순차 진행하고 필요가 확인된 구성 요소를 추가합니다.

### 참고할 실행 구현

[Harness/Loop GitHub 목록](../../_reference/github_references.md#4-harnessloop)에 Symphony·Ralph·autonomous-coding·Deep Agents·mini-swe-agent와 자료 모음을 정리했습니다. 실행기 전체 도입과 그 안의 상태 저장·작은 작업·검증 패턴을 참고하는 선택은 각각의 작업 범위에서 판단합니다.

### 일일 triage + 자동 수정 루프

아래는 scheduler·인증·외부 갱신 범위가 설정된 경우의 설계 예시이며, 현재 저장소에서 실행 중인 automation이 아닙니다.

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

- 사전에 정한 작업·검증·정지·외부 갱신 범위 안에서 후속 단계를 실행
- 발견·수정·검증·기록 흐름을 재사용하되 도구별 실행·인증·정지 설정은 조정
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

| 항목            | 영향                                                             |
|-----------------|------------------------------------------------------------------|
| Sub-agent       | agent별 작업량·모델·도구 호출에 따라 사용량 증가; 고정 배수 아님 |
| Codex /goal     | 후속 작업만큼 사용량 증가; 지정한 예산 한도 도달 시 정지         |
| Automation 주기 | 매시간이면 하루 최대 24회 예약; 실제 비용은 실행별 사용량에 좌우 |
| Token rich/poor | 사용 가능 토큰 예산에 따라 루프 설계가 근본적으로 달라짐         |

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

단일 계층 번호 대신 어떤 실행을 반복하는지 구분합니다.

```text
Outer loop: select task -> run agent -> check evidence -> stop / retry
                              |
                              v
Harness: guidance + tools + state + checks + execution boundaries
                              |
                              v
Inner loop: observe -> act -> inspect feedback -> next action
```

하네스에는 실행 중 관찰·행동 루프가 있고, 외부 오케스트레이터는 그 실행을 여러 번 호출할 수 있습니다. 하네스 지침·상태도 여러 세션에 유지될 수 있으므로 하네스는 1세션, 루프는 항상 그 상위라는 고정 관계로 정의하지 않습니다. [Harness Engineering](./harness_engineering.md#7-prompt-engineering과의-차이), [Addy Osmani의 외부 루프 설명](https://addyosmani.com/blog/loop-engineering/)

검사·상태 전달이 부족한 환경을 반복 호출하면 같은 실패가 누적됩니다. 반복 횟수보다 무엇을 검사하고 어느 증거로 다음 행동을 바꿀지 먼저 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 용어 정리

| 용어                | 정의                                                               |
|---------------------|--------------------------------------------------------------------|
| Loop                | 목표·입력·검증·정지 조건에 따라 에이전트 작업을 반복하는 흐름      |
| Automation          | 스케줄에 따라 발동하여 작업을 발견·분류하는 트리거                 |
| Worktree            | git worktree 기반 격리 작업 디렉토리 (에이전트 간 충돌 방지)       |
| Skill               | SKILL.md에 절차를 기록하고, 이름·설명으로 발견해 선택 시 본문 로드 |
| Connector           | MCP 기반으로 외부 도구(이슈 트래커, DB, Slack)에 연결              |
| Sub-agent           | 별도 작업 지침·context로 작업을 수행하는 보조 agent                |
| Memory              | 단일 대화 밖에서 상태를 보존하는 디스크 기반 파일                  |
| /goal               | thread에 목표를 유지하고 완료·중단·예산 등 정지 조건까지 진행      |
| /loop               | Claude Code의 세션 내 주기 재호출 명령; 수명·재개 제약 확인        |
| Triage              | 발견된 작업의 우선순위 분류 (자동화의 출력)                        |
| Intent Debt         | 에이전트가 의도의 빈틈을 추측으로 메우면서 발생하는 품질 저하      |
| Comprehension Debt  | 직접 쓰지 않은 코드가 늘면서 이해도가 떨어지는 현상                |
| Cognitive Surrender | 루프 결과를 비판 없이 수용하는 인지적 포기 상태                    |
| Orchestration Tax   | 병렬 에이전트 관리에 드는 사람의 오버헤드                          |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Addy Osmani: [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) — ★★★☆☆
- Addy Osmani: [Practical Loop Engineering](https://addyosmani.com/blog/practical-loop-engineering/) — ★★★☆☆
- Anthropic: [Goals](https://code.claude.com/docs/en/goal), [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) — ★★★☆☆
- [Harness/Loop 참고 저장소](../../_reference/github_references.md#4-harnessloop)
- OpenAI Skills: [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills) — ★★★☆☆
- OpenAI Goals: [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) — ★★★☆☆
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

**마지막 업데이트**: 2026-10-03

© 2026 siasia86. Licensed under CC BY 4.0.
