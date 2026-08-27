# Repository Governance 분리 계획

`01_repository_governance/`를 `/root/32_system-engineering-resources` 단일 저장소에서 분리하여, 여러 repository의 운영 정책과 문서 체계를 독립적으로 관리할 수 있는 저장소로 전환할지 재검토하는 계획입니다. 현재는 분리를 실행하지 않고, 결정에 필요한 조사·호환성·검증·롤백 조건을 먼저 확정합니다.

## 목차

| 구분 | 섹션                                                                                                         |
|------|--------------------------------------------------------------------------------------------------------------|
| 기본 | [1. 계획 목적](#1-계획-목적) / [2. 현재 상태](#2-현재-상태) / [3. 목표 상태와 선택지](#3-목표-상태와-선택지) |
| 실행 | [4. 영향 범위](#4-영향-범위) / [5. 실행 단계](#5-실행-단계) / [6. 리스크와 대응](#6-리스크와-대응)           |
| 검증 | [7. 롤백 계획](#7-롤백-계획) / [8. 검증 기준](#8-검증-기준) / [9. 결정 게이트](#9-결정-게이트)               |

---

## 1. 계획 목적

`01_repository_governance/`의 본질을 여러 repository에 공통 적용하는 운영 정책·템플릿·검증 기준의 중앙 원본으로 정의하고, 이 역할이 현재 monorepo 안에 계속 있어야 하는지 독립 저장소로 분리해야 하는지 판단합니다.

### 범위

- 대상: `00_governance/01_repository_governance/`
- 포함: 정책 문서, 템플릿, 분리 계획, 자체 TODO와 검증 기준
- 검토 대상: 현재 저장소의 링크, `02_kiro/` skill, `03_claude/` 문서, CI·검사 도구

### 범위 제외

- `02_kiro/`와 `03_claude/`의 즉시 분리
- 각 대상 repository의 `.governance/` 문서 이관 자체
- 정책 의미를 바꾸는 작업
- 분리 승인 전 원본 디렉토리 삭제 또는 remote 변경

## 2. 현재 상태

현재 `01_repository_governance/`는 `/root/32_system-engineering-resources`의 하위 디렉토리이며, 저장소별 governance 정책의 원본과 템플릿을 보유합니다. 2026-08-27 결정 기록에서는 규모, 링크 결합도, 루트 검증 도구 중복을 근거로 분리를 보류했습니다. 이 계획은 기존 결정을 삭제하지 않고 재검토합니다.

| 항목            | 현재 상태                                              | 판단                             |
|-----------------|--------------------------------------------------------|----------------------------------|
| 대상 디렉토리   | `00_governance/01_repository_governance/`              | 정책 원본 역할                   |
| 규모 측정값     | 계획 문서 추가 전 약 60K, Markdown 9개                 | 단독 저장소로는 작음             |
| 상위 governance | `00_governance/` 약 428K, Markdown 50개                | 하위 영역 간 정책·미러 연계 존재 |
| 전체 저장소     | 약 42M, Markdown 426개                                 | 전체 대비 governance 비중은 작음 |
| 외부 결합       | 루트 README·CHANGELOG·`02_kiro/`·`03_claude/`에서 참조 | 링크와 skill 경로 수정 필요      |
| 검증 도구       | Markdown 검사·보안 검사·CI가 루트에 위치               | 분리 저장소용 검증 체계 필요     |

위 규모 수치는 2026-08-27 기존 분리 검토 당시의 측정값입니다. 분리 실행 전에는 계획 문서를 포함한 현재 파일 목록과 링크를 다시 측정하며, 과거 결정 기록의 링크 측정값과 현재 파일 검색 결과가 다를 수 있으므로 정식 인벤토리를 별도 산출합니다.

## 3. 목표 상태와 선택지

### 목표 상태

분리하는 경우 신규 repository는 다음 책임을 가집니다.

- 여러 repository에 적용할 governance 정책의 단일 원본
- `GOVERNANCE`, `ISSUE`, `TODO`, `PLAN`, `CHANGELOG`, `verification` 템플릿 관리
- 정책 우선순위·문서 생명주기·도구 미러 규칙 관리
- 자체 Markdown·링크·보안 검증과 변경 이력 관리
- 대상 repository로 배포·참조하는 안정적인 경로 제공

### 선택지

| 선택지                          | 구조                                                 | 장점                                    | 단점                                        |
|---------------------------------|------------------------------------------------------|-----------------------------------------|---------------------------------------------|
| A. 독립 저장소                  | `01_repository_governance/`를 별도 repository로 추출 | 정책 원본과 대상 repository의 경계 명확 | 링크·CI·검증 체계 재구성 필요               |
| B. `00_governance/` 통합 저장소 | governance 하위 전체를 함께 추출                     | 정책과 도구 미러의 연계 보존            | 정책과 AI 도구 자료가 한 저장소에 계속 결합 |
| C. 현행 유지                    | 단일 저장소 내부에서 계속 운영                       | 변경 비용과 링크 위험 최소              | 중앙 정책 repository라는 본질이 경로상 약함 |

현재 검토 우선순위는 **A를 기준안으로 검증하고, B와 C를 비교하는 방식**입니다. A가 검증 도구·배포 방식·운영 비용을 감당하지 못하면 C를 유지하고, 도구 미러와 정책의 결합 이점이 더 크면 B를 재검토합니다.

## 4. 영향 범위

분리 자체는 파일 이동이지만, 정책 원본의 위치가 바뀌므로 다음 계층에 영향을 줍니다.

```text
Standalone governance repository
        │
        ├── Policy documents and templates
        │       │
        │       ├── repo-governance skill references
        │       ├── root README and CHANGELOG links
        │       └── target repositories' .governance documents
        │
        └── CI and Markdown/security validation
```

### 영향 대상

- 링크: 루트 `README.md`, `CHANGELOG.md`, `00_governance/README.md`, `03_claude/README.md`
- skill: `02_kiro/skills/repo-governance/SKILL.md`의 정책 경로와 생성 절차
- 미러 정책: `sync_policy.md`와 `02_kiro/`의 동기화 관계
- 검증: `md-style-check.py`, `md-heading-check.py`, `md-link-check.py`, `readme_inventory_check.py`, `gitleaks`, CI workflow
- 운영: 신규 repository가 정책 원본을 찾는 URL과 버전 기준

## 5. 실행 단계

### Phase 1: 인벤토리와 설계

- [ ] 현재 파일·링크·skill·workflow·검사 설정의 전체 참조 목록 생성
- [ ] 신규 repository 이름, remote 소유자, 공개 범위, 관리자 결정
- [ ] Git history 보존 방식 결정: 전체 history, 경로 history, 신규 시작
- [ ] 정책 배포 방식 결정: 외부 링크, release archive, subtree 또는 별도 sync
- [ ] 분리 대상과 유지 대상의 최종 목록 확정

**Checkpoint: 설계 승인**

- [ ] 참조 목록에 활성 링크와 역사적 기록을 구분
- [ ] 정책 원본과 미러의 단일 source of truth 확정
- [ ] 신규 repository의 CI·보안 검사 실행 가능
- [ ] 분리하지 않을 때의 C 선택지와 비교 기록

### Phase 2: 독립 repository 준비

- [ ] 신규 repository에 README, governance 정책, 템플릿, TODO, 계획 문서 배치
- [ ] Markdown·heading·link·inventory·gitleaks 검증을 독립 실행하도록 구성
- [ ] 기존 상대 링크를 신규 repository 기준으로 변환
- [ ] 버전·release·변경 기록 정책 정의
- [ ] 원본 history 보존 여부에 따른 migration 결과 확인

**Checkpoint: 병행 검증**

- [ ] 원본과 신규 repository의 문서 목록·내용 차이를 설명
- [ ] 신규 repository의 전체 검증 통과
- [ ] 외부에서 정책 문서와 템플릿을 접근할 수 있음
- [ ] rollback용 기존 commit·tag·백업 위치 확인

### Phase 3: 참조 전환과 분리 실행

- [ ] 루트 README와 활성 문서 링크를 신규 repository URL로 전환
- [ ] `repo-governance` skill의 정책 경로와 생성 절차 전환
- [ ] `03_claude/`와 도구 미러 정책의 참조 경로 전환
- [ ] 전환 기간 동안 기존 경로의 안내 문서 또는 신규 위치 forwarding link 유지
- [ ] 별도 승인 후 monorepo에서 대상 디렉토리 제거

### Phase 4: 사후 안정화

- [ ] 전체 저장소 링크·heading·style·inventory·secret 검증
- [ ] 대상 repository에서 신규 정책 URL과 템플릿 접근 확인
- [ ] 첫 변경의 release·동기화·rollback 절차 실행
- [ ] 분리 완료를 신규 repository의 `CHANGELOG.md`와 monorepo의 변경 기록에 기록
- [ ] 30일 후 운영 비용과 링크 실패 여부 재검토

## 6. 리스크와 대응

| 리스크                        | 영향                               | 대응                                             |
|-------------------------------|------------------------------------|--------------------------------------------------|
| 정책 원본 URL 변경            | 대상 repository가 규칙을 찾지 못함 | 병행 기간과 명시적 redirect·전환 안내 유지       |
| 상대 링크 대량 손상           | 문서 탐색과 CI 실패                | 참조 인벤토리 작성 후 전환, 전체 link check 실행 |
| 검증 도구 중복·누락           | 신규 repository 품질 저하          | 독립 CI를 먼저 통과시킨 뒤 원본 제거             |
| `02_kiro/` 미러와 정책 불일치 | skill 동작과 정책 해석 차이        | source of truth와 release 버전 고정              |
| history·저작권 정보 손실      | 변경 추적과 감사성 저하            | migration 방식 사전 결정, 원본 tag 보존          |
| 분리 이득보다 운영 비용이 큼  | 관리 복잡도 증가                   | 30일 후 비용·실패율 검토, C로 rollback           |

## 7. 롤백 계획

분리 실행 전 다음 보존물을 확보합니다.

- 원본 저장소의 분리 직전 commit과 tag
- 신규 repository의 최초 migration commit
- 전환 전·후 참조 인벤토리
- CI와 검사 설정의 전환 diff

문제 발생 시 다음 순서로 복구합니다.

1. 신규 repository를 정책 원본으로 사용하지 않도록 활성 링크와 skill 참조를 이전 경로로 되돌립니다.
2. 분리 직전 commit에서 원본 디렉토리를 복원하거나 revert commit으로 되돌립니다.
3. 루트 및 관련 문서의 링크 검증과 skill 경로 검증을 실행합니다.
4. 원인·영향·복구 결과를 `ISSUE.md`와 `CHANGELOG.md`에 기록합니다.
5. 문제 해결 전까지 원본 monorepo를 정책 source of truth로 유지합니다.

`reset --hard`, 강제 push, 기존 remote 삭제는 사용하지 않습니다. 신규 repository 생성과 monorepo 경로 제거는 별도 승인 후 실행합니다. 복구 시에는 전환 commit을 `git revert`로 되돌리고, 새 repository의 원본은 삭제하지 않고 보존합니다.

## 8. 검증 기준

### 정적 검증

- [ ] `md-style-check.py` 통과
- [ ] `md-heading-check.py` 통과
- [ ] `md-link-check.py` 통과
- [ ] `readme_inventory_check.py` 통과
- [ ] `git diff --check` 통과
- [ ] `gitleaks` 통과

### 기능 검증

- [ ] 신규 repository에서 정책 문서와 모든 템플릿 접근 가능
- [ ] `repo-governance` skill이 신규 정책 위치를 참조
- [ ] 신규 repository 생성 절차가 실제 경로와 일치
- [ ] 대상 repository에서 `.governance/` 적용과 검증 절차가 동작
- [ ] 미러 동기화 정책이 원본·미러 관계를 정확히 설명

### 운영 검증

- [ ] 새 정책 변경의 release·전파 담당자 지정
- [ ] version pin 또는 호환성 기준 지정
- [ ] 30일 사후 점검 일정 등록
- [ ] 장애 시 연락·복구 경로 문서화

## 9. 결정 게이트

다음 항목을 모두 확인하기 전에는 실제 분리를 실행하지 않습니다.

- [ ] 독립 repository의 이름·remote·소유자 확정
- [ ] A·B·C 선택지 비교와 기준안 승인
- [ ] 전체 참조 인벤토리와 전환 diff 검토
- [ ] 독립 CI와 보안 검증 통과
- [ ] 정책 source of truth와 배포 방식 확정
- [ ] history 보존·rollback·병행 기간 확정
- [ ] monorepo에서 대상 디렉토리를 제거할 별도 승인 획득

현재 결론은 **분리 실행 전 재검토 계획을 수립한 상태**입니다. 결정 게이트가 충족되기 전까지 `/root/32_system-engineering-resources/00_governance/01_repository_governance/`를 현행 정책 원본으로 유지합니다.

---

## 참고 자료

- [Repository Governance README](README.md)
- [Governance TODO](governance_todo.md)
- [Repository Governance Precedence](governance_precedence.md)
- [Documentation Policy](documentation_policy.md)
- [Tool Mirror Sync Policy](sync_policy.md)

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.
