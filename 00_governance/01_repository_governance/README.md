# Repository Governance

이 디렉토리는 저장소 문서 운영 정책과 작업 템플릿을 관리합니다. 실제 AI 도구 자료 미러는 [`../02_kiro/`](../02_kiro/)와 향후 추가될 도구별 디렉토리에서 관리합니다.

## 목차

| 섹션                                                                       |
|----------------------------------------------------------------------------|
| [1. 목적](#1-목적) / [2. 문서 운영 구조](#2-문서-운영-구조)                |
| [3. 정책 문서](#3-정책-문서) / [4. 저장소별 규칙](#4-저장소별-규칙)        |
| [5. 템플릿](#5-템플릿) / [6. 개선 항목](#6-개선-항목) / [7. 검증](#7-검증) |

---

## 1. 목적

`01_repository_governance/`는 이 저장소의 문서 생명주기, 변경 절차, 동기화 규칙을 정의합니다.

`../02_kiro/`와 달리 특정 AI 도구의 실행 환경을 미러링하지 않으며, 저장소 자체의 운영 기준만 기록합니다.

## 2. 문서 운영 구조

| 문서                   | 역할                     | 처리 기준                                |
|------------------------|--------------------------|------------------------------------------|
| `.governance/ISSUE.md` | 원인 분석이 필요한 문제  | 재현·영향·원인을 기록합니다.             |
| `.governance/TODO.md`  | 아직 시작하지 않은 작업  | 완료 시 항목을 제거합니다.               |
| `.governance/PLAN.md`  | 현재 진행 중인 복합 작업 | 완료 시 정리하고 CHANGELOG에 기록합니다. |
| `CHANGELOG.md`         | 완료된 변경 기록         | 릴리스 단위로 변경 내용을 보존합니다.    |

## 3. 정책 문서

- [문서 운영 정책](documentation_policy.md): 문서별 역할과 생명주기를 정의합니다.
- [도구 미러 동기화 정책](sync_policy.md): AI 도구별 원본과 공개 미러의 허용 범위를 정의합니다.
- [저장소 규칙 우선순위 정책](governance_precedence.md): 저장소별 규칙과 전역 규칙의 적용 순서를 정의합니다.

## 4. 저장소별 규칙

저장소별 규칙은 해당 저장소 최상위의 `.governance/` 에 두는 것을 기준으로 합니다. 적용 순서와 기술 범위는 [저장소 규칙 우선순위 정책](governance_precedence.md)에서 정의합니다.

Ansible 학습·자동화 저장소에는 `.governance/GOVERNANCE.md`와 `verification.md`를 적용했으며, 중앙 profile에서의 이관을 완료했습니다. 저장소별 규칙은 중앙 문서가 아니라 대상 저장소 안에서 관리합니다.

`.governance/` 문서에는 내부 IP, 사용자명, 개인 경로, 자격증명, 실제 인프라 구성값을 기록하지 않습니다.

## 5. 템플릿

| 템플릿                                             | 대상 문서                     | 용도                    |
|----------------------------------------------------|-------------------------------|-------------------------|
| [PLAN](templates/plan_template.md)                 | `PLAN.md`                     | 복합 작업 계획          |
| [ISSUE](templates/issue_template.md)               | `ISSUE.md`                    | 원인 분석이 필요한 문제 |
| [TODO](templates/todo_template.md)                 | `TODO.md`                     | 앞으로 수행할 작업      |
| [CHANGELOG](templates/changelog_template.md)       | `CHANGELOG.md`                | 완료된 변경             |
| [README](templates/readme_template.md)             | `README.md`                   | 저장소·디렉토리 인덱스  |
| [RUNBOOK](templates/runbook_template.md)           | 운영 문서                     | 점검·장애 대응 절차     |
| [GOVERNANCE](templates/governance_template.md)     | `.governance/GOVERNANCE.md`   | 저장소별 규칙과 예외    |
| [ISSUE](templates/issue_template.md)               | `.governance/ISSUE.md`        | 원인 분석이 필요한 문제 |
| [TODO](templates/todo_template.md)                 | `.governance/TODO.md`         | 앞으로 수행할 작업      |
| [PLAN](templates/plan_template.md)                 | `.governance/PLAN.md`         | 복합 작업 계획          |
| [VERIFICATION](templates/verification_template.md) | `.governance/verification.md` | 저장소별 검증 절차      |

신규 저장소의 `.governance/` 기본 문서(`GOVERNANCE.md`, `ISSUE.md`, `TODO.md`, `PLAN.md`)와 `CHANGELOG.md`에 템플릿이 대응합니다. 기존 저장소의 루트 작업 문서는 migration 전까지 legacy로 허용합니다.

## 6. 개선 항목

- [governance TODO](governance_todo.md): 이 디렉토리 자체의 개선 항목을 관리합니다.
- [분리 계획](repository_governance_split_plan.md): 독립 repository 분리 여부와 실행·검증·롤백 조건을 관리합니다.

신규 저장소의 저장소 전역 작업은 `.governance/TODO.md`에서 관리합니다. 기존 저장소의 루트 `TODO.md`는 migration 전까지 legacy로 허용합니다.

## 7. 검증

문서 변경 후 다음 검증을 실행합니다.

```bash
sia-md-link-check .
sia-md-heading-check .
sia-md-style-check .
sia-readme-inventory-check README.md
git diff --check
```

---

**작성일**: 2026-08-20

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.
