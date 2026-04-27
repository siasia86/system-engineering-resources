# AI 에이전트용 Markdown 디자인 패턴

AI 코딩 에이전트(Kiro, Claude Code, Gemini CLI, Cursor 등)에서 사용하는
마크다운 파일의 설계 패턴과 작성 규칙을 정리합니다.

---

## 1. 4-파일 패턴 (멀티 에이전트 시스템)

에이전트 시스템을 4개의 마크다운 파일로 구조화하는 패턴입니다.

```
repo/
├── AGENTS.md                  ← 시스템 전체 구조 (조직도)
└── agents/
    └── analyst/
        ├── Agent.md           ← 에이전트 정체성
        ├── INSTRUCTIONS.md    ← 행동 규칙 + 워크플로우
        └── skills/
            └── SKILL.md       ← 특정 기술 수행 절차
```

| 파일              | 역할                       | 비유        | 변경 빈도 |
|-------------------|----------------------------|-------------|-----------|
| `AGENTS.md`       | 전체 에이전트 관계도       | 조직도      | 낮음      |
| `Agent.md`        | 개별 에이전트 정체성/역할  | 사원증      | 매우 낮음 |
| `INSTRUCTIONS.md` | 행동 규칙, 워크플로우 순서 | 업무 매뉴얼 | 중간      |
| `SKILL.md`        | 특정 기술 수행 절차        | 자격증      | 높음      |

### AGENTS.md 예시

```markdown
# Agents System Overview

| Agent              | Role           | Hands off to              |
|--------------------|----------------|---------------------------|
| orchestrator-agent | Router / entry | analyst, writer, viz      |
| analyst-agent      | Data analysis  | viz-agent, writer-agent   |
| writer-agent       | Prose & reports| human review              |

## Orchestration rules
- All user requests enter through orchestrator-agent only
- Failures bubble up to the orchestrator, not to the user
```

### Agent.md 예시

```markdown
# analyst-agent

## Who I am
I am the data analyst agent. I receive datasets and return
structured AnalysisResult dicts.

## My place in the system
- Spawned by: orchestrator-agent
- I hand off to: viz-agent and writer-agent

## What I do NOT do          ← 가장 중요한 섹션
- Write reports (→ writer-agent)
- Build charts (→ viz-agent)
- Make business recommendations (→ human review)
```

> ⚠️ "하지 않는 것" 섹션이 없으면 AI가 역할을 넘어서 행동합니다.

---

## 2. 3단계 로딩 패턴 (Progressive Disclosure)

토큰을 절약하면서 대규모 지식을 관리하는 핵심 패턴입니다.

```
┌───────────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│ Level 1: Metadata │────>│ Level 2: 본문       │────>│ Level 3: 리소스   │
│ (항상 로드)       │     │ (트리거 시 로드)    │     │ (필요 시 로드)    │
│ ~100 토큰/스킬    │     │ ~5,000 토큰 이하    │     │ 무제한            │
└───────────────────┘     └─────────────────────┘     └───────────────────┘
```

| 단계    | 로드 시점      | 토큰 비용      | 내용                       |
|---------|----------------|----------------|----------------------------|
| Level 1 | 항상 (시작 시) | ~100 토큰/스킬 | YAML frontmatter만         |
| Level 2 | 스킬 트리거 시 | ~5,000 토큰    | SKILL.md 본문              |
| Level 3 | 필요할 때만    | 무제한         | references/, scripts/ 파일 |

### YAML Frontmatter (Level 1)

```yaml
---
name: infra-operation
description: >
  Infrastructure operation rules for server management,
  deployment, and monitoring. Use when user asks about
  server tasks, ansible, terraform, or monitoring setup.
---
```

작성 규칙:
- 3인칭으로 작성 ("Processes files" ✅ / "I can help" ❌)
- 트리거 키워드 포함 (사용자가 쓸 법한 단어)
- 1,024자 이내
- 구체적 동사 사용 (analyze, generate, extract, deploy)

---

## 3. 스킬 디렉토리 패턴

하나의 스킬을 디렉토리로 구조화하는 패턴입니다.

```
my-skill/
├── SKILL.md           ← 필수: 메타데이터 + 지시사항 (500줄 이하)
├── scripts/           ← 실행 가능한 스크립트 (토큰 소비 없음)
├── references/        ← 참조 문서 (도메인별 분리)
└── assets/            ← 템플릿, 정적 리소스
```

### 핵심 규칙

| 규칙                            | 이유                                 |
|---------------------------------|--------------------------------------|
| SKILL.md 본문 500줄 이하        | Level 2 로드 시 토큰 폭증 방지       |
| 상세 내용은 references/ 로 분리 | 필요한 파일만 Level 3 로드           |
| 참조는 1단계 깊이만             | A→B→C 체인은 AI가 잘 못 따라감       |
| 파일명에 내용 반영              | AI가 디렉토리 탐색 시 힌트로 활용    |
| 긴 참조 파일에 목차 추가        | AI가 구조 파악 후 필요한 부분만 읽음 |

### references/ 분리 예시

```markdown
<!-- SKILL.md 에서 -->
## Available References
- **Server setup**: [references/server_setup.md](references/server_setup.md)
- **Monitoring**: [references/monitoring_config.md](references/monitoring_config.md)
- **Deployment**: [references/deploy_procedure.md](references/deploy_procedure.md)
```

AI는 사용자 질문에 맞는 파일만 읽습니다. 나머지는 토큰을 소비하지 않습니다.

---

## 4. 마크다운 프롬프트 구조 패턴

### 헤딩 계층 패턴

AI는 마크다운 헤딩(`#`, `##`, `###`)을 구조적 경계로 인식합니다.

```markdown
# Role (최상위: 역할 정의)
## Context (중간: 상황 설명)
### Instructions (하위: 구체적 지시)
### Constraints (하위: 제약 조건)
## Output Format (중간: 출력 형식)
```

### XML + Markdown 하이브리드 패턴

복잡한 프롬프트에서 섹션 경계를 명확히 하는 패턴입니다.

```markdown
<role>
You are an infrastructure engineer specializing in Linux servers.
</role>

<context>
- Environment: Rocky Linux 9
- Tools: Ansible, Terraform, zabbix
</context>

<instructions>
## Step 1: Analyze
Review the current server configuration.

## Step 2: Plan
Create a migration plan with rollback steps.

## Step 3: Execute
Apply changes with confirmation at each step.
</instructions>

<constraints>
- Never modify prd environment without confirmation
- Always create backup before changes
</constraints>
```

### 체크리스트 워크플로우 패턴

AI가 복잡한 절차를 순서대로 따르게 하는 패턴입니다.

```markdown
## Release Workflow

Copy this checklist to track progress:
- [ ] Step 1: Run and verify tests
- [ ] Step 2: Bump version
- [ ] Step 3: Update CHANGELOG
- [ ] Step 4: Commit and tag
- [ ] Step 5: Execute deployment
- [ ] Step 6: Verify operation
```

> 산문형 지시보다 번호 매긴 단계가 훨씬 정확하게 따릅니다.

---

## 5. 토큰 효율 패턴

### 언어별 토큰 효율

| 언어   | 토큰당 글자 수 | 같은 의미 토큰 비용 | 용도           |
|--------|----------------|---------------------|----------------|
| 영어   | 3~4글자        | 1x (기준)           | 스킬, 프롬프트 |
| 한글   | 1~2글자        | 2~3x                | 출력만         |
| 일본어 | 1~2글자        | 2~3x                | 출력만         |

### 효율적 작성 패턴

```markdown
<!-- 비효율: 한글 설명 (~25 토큰) -->
모든 작업 전에 수행할 내용을 명확히 출력합니다

<!-- 효율: 영어 키워드 (~7 토큰) -->
Print task summary before execution

<!-- 비효율: 장황한 예시 -->
## 예시
다음과 같이 작성합니다:
- 서버 이름은 prd-app-web-frontend 형식으로 작성합니다
- 개발 환경은 dev-db-rds-postgresql 형식으로 작성합니다

<!-- 효율: 패턴만 제시 -->
format: `[env]-[category]-[service]-[detail]`
ex: prd-app-web-frontend, dev-db-rds-postgresql
```

### 토큰 절약 체크리스트

| 방법                    | 절약 효과 | 적용 대상                     |
|-------------------------|-----------|-------------------------------|
| 스킬/프롬프트 영어 작성 | 30~50%    | SKILL.md, agent prompt        |
| YAML frontmatter 추가   | 가변      | 3단계 로딩 활성화             |
| 불필요한 예시 제거      | 20~30%    | AI는 패턴만 알면 됨           |
| references/ 분리        | 가변      | 상세 내용 필요 시만 로드      |
| scripts/ 활용           | 높음      | 코드는 실행만, 토큰 소비 없음 |

---

## 6. 스킬 작성 규칙

### 필수 규칙

| 규칙                             | 이유                                       |
|----------------------------------|--------------------------------------------|
| description에 트리거 키워드 포함 | AI가 스킬 선택 정확도 향상                 |
| "하지 않는 것" 명시              | 역할 침범 방지 (가장 중요)                 |
| 번호 매긴 워크플로우 사용        | 산문형보다 정확하게 따름                   |
| 실패 시나리오 포함               | 정상 경로만 쓰면 오류 시 혼란              |
| 참조는 1단계 깊이만              | A→B→C 체인은 AI가 잘 못 따라감             |
| 규칙과 워크플로우 분리           | 규칙="항상/절대", 워크플로우="먼저/그다음" |

### 스킬 범위 선택

| 기준               | Workspace 스킬 | User 스킬 (글로벌) |
|--------------------|----------------|--------------------|
| 팀원이 사용        | ✅             | ❌                 |
| Git 추적 필요      | ✅             | 선택               |
| 프로젝트 한정      | ✅             | ❌                 |
| 모든 프로젝트 공통 | ❌             | ✅                 |
| 개인 취향          | ❌             | ✅                 |

```
Workspace: .kiro/skills/     ← 프로젝트별, Git 관리
Global:    ~/.kiro/skills/   ← 개인 전역, 모든 프로젝트
```

---

## 7. 보안 규칙

### 스킬 감사 체크리스트

외부 스킬 도입 전 확인 사항:

```
- [ ] SKILL.md에 의심스러운 명령이 없는가?
- [ ] scripts/ 가 외부 서비스로 데이터를 전송하지 않는가?
- [ ] 예상치 못한 네트워크 호출이 없는가?
- [ ] 파일 접근 범위가 스킬 목적에 맞는가?
- [ ] 환경 변수나 인증 정보에 접근하지 않는가?
```

### 신뢰도 기준

| 출처                    | 신뢰도 | 조치              |
|-------------------------|--------|-------------------|
| 직접 작성               | ★★★★★  | 바로 사용         |
| 공식 저장소 (Anthropic) | ★★★★☆  | 내용 확인 후 사용 |
| 신뢰 조직               | ★★★☆☆  | 리뷰 후 사용      |
| 출처 불명               | ★☆☆☆☆  | 감사 필수         |

---

## 8. 실전 적용 예시 (Kiro CLI)

### 현재 work-rules 스킬에 frontmatter 적용

```markdown
---
name: work-rules
description: >
  Operation rules for infrastructure work. Covers confirmation
  before action, dangerous ops safety, delete procedures,
  markdown formatting, naming conventions, and code policies.
  Use for all infrastructure and server management tasks.
---
# Work Rules
(이하 기존 내용)
```

### 인프라 운영 스킬 디렉토리 구성 예시

```
~/.kiro/skills/
├── work-rules/
│   └── SKILL.md                ← 공통 작업 규칙
├── infra-ops/
│   ├── SKILL.md                ← 인프라 운영 절차 (500줄 이하)
│   ├── references/
│   │   ├── server_setup.md     ← 서버 초기 설정
│   │   ├── monitoring.md       ← 모니터링 설정
│   │   └── deploy_procedure.md ← 배포 절차
│   └── scripts/
│       ├── health_check.sh     ← 서버 상태 점검
│       └── log_collect.sh      ← 로그 수집
└── naming-rules/
    └── SKILL.md                ← 네이밍 규칙
```

---

## 참고 자료

- 10 Practical Techniques for Mastering Agent Skills
  https://shibuiyusuke.medium.com/10-practical-techniques-for-mastering-agent-skills-in-ai-coding-agents-6070e4038cf1
- Instructions.md vs Skills.md vs Agent.md vs Agents.md
  https://priyankavergadia.substack.com/p/how-to-structure-skillmd-agentsmd
- How to Develop SKILL.md for AI Coding Agents
  https://www.mtechzilla.com/guides/how-to-develop-skill-md-production-guide-engineering-teams
- Agent Skills 101: a practical guide for engineers
  https://blog.serghei.pl/posts/agent-skills-101/


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-11

© 2026 siasia86. Licensed under CC BY 4.0.
