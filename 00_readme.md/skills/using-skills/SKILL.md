---
name: using-skills
description: Maps incoming work to the right skill workflow. Use when starting a session, when deciding which skill applies, or when the task type is unclear.
---

# Using Skills

## Overview

작업이 도착하면 적절한 스킬을 식별하여 적용하는 메타 스킬입니다.

## Skill Discovery

```
Task arrives
    │
    ├── 새 인프라 구축/대규모 변경?  → spec-driven-infra
    ├── 작업 분해 필요?              → planning-and-breakdown
    ├── IaC 코드 작성/수정?          → incremental-change
    ├── 장애/오류 발생?              → debugging-and-recovery
    ├── Python 스크립트 작성?          → python-script-template
    ├── Bash 스크립트 작성?            → bash-script-template
    ├── 협업 디렉토리 파일 수정?      → kiro-lock (현재 disabled — 협업 시 enable 필요)
    ├── 코드/스크립트 리뷰?          → code-review
    ├── 보안 검토/마스킹?            → security-tools
    ├── 프로덕션/비가역 변경?        → doubt-driven-infra
    ├── 배포/런칭?                   → shipping-checklist
    ├── 테스트 작성?                 → testing-guide
    ├── Git 커밋/PR?                 → git-commit-rule
    ├── 마크다운 문서 작성?          → work-rules + STYLE.md
    ├── 마크다운 링크/목차 검증?     → md-link-check
    ├── README 푸터/배지 적용?       → readme-template
    └── 위 해당 없음?               → work-rules 기본 규칙 적용
```

## Skill Composition

스킬은 단독 또는 조합으로 사용합니다.

| 시나리오           | 스킬 체인                                                       |
|--------------------|-----------------------------------------------------------------|
| 새 인프라 프로젝트 | spec-driven-infra → planning-and-breakdown → incremental-change |
| 프로덕션 변경      | doubt-driven-infra → incremental-change → shipping-checklist    |
| 장애 대응          | debugging-and-recovery → incremental-change                     |
| 코드 리뷰 후 수정  | code-review → incremental-change → testing-guide                |

## Rules

- 스킬이 적용 가능하면 반드시 사용합니다
- "작아서 스킬 불필요"는 잘못된 판단입니다
- 여러 스킬이 해당되면 체인으로 연결합니다
- 스킬 내 verification 단계를 건너뛰지 않습니다
