# 32_system-engineering-resources 관리 INDEX

관리 문서의 공통 기준 위치는 `.governance/`이며 INDEX·GOVERNANCE·PLAN·TODO·ISSUE·verification·CHANGELOG·HANDOFF의 이름과 역할을 통일합니다. 기존 기록은 보존하고 승인된 현장 전환에서 현행 상태를 한 번 병합하며 이전 위치는 연결 안내로 유지합니다. 이 profile 개정만으로 다른 현장 적용이 완료된 것은 아닙니다.

## 1. 구조와 원본

[규칙](GOVERNANCE.md)·[현행 상태](TODO.md)·[계획](PLAN.md)·[문제](ISSUE.md)·[검증](verification.md)·[완료](CHANGELOG.md)·[재개](HANDOFF.md)의 역할을 구분합니다. 현행 PLAN·TODO·CHANGELOG와 공통 관리 문서는 .governance에 통일합니다. 이전 루트 상태·이력을 실제 적용에서 보존·병합하고 TODO2 상세 설계 과제를 일반 작업에 일괄 적용하지 않습니다.

```text
32_system-engineering-resources/
├── AGENTS.md                    작업 진입
├── README.md                    저장소 안내
├── TODO.md·PLAN.md·CHANGELOG.md 이전 위치 연결 안내
├── TODO2.md                     별도 설계 과제
└── .governance/
    ├── README.md                관리 진입
    ├── INDEX.md                 구조·읽기 조건
    ├── GOVERNANCE.md            운영 규칙
    ├── APPLICATION.md           적용 기록
    ├── PLAN.md                  계획
    ├── TODO.md                  현재 상태
    ├── ISSUE.md                 문제
    ├── verification.md          검증 기준
    ├── HANDOFF.md               인계
    ├── CHANGELOG.md             완료 기록
    ├── REMOVED.md               삭제 기록
    ├── MOVED.md                 옮김 기록
    ├── tracks/                  새 수동 기록(필요한 역할 폴더만)
    │   └── MAIN-20261113-01_ax-reference-docs/
    └── local/                   Git 제외
```

이 tree는 중앙의 기준 틀을 현장의 실제 경로에 맞춘 배치입니다. 현장의 기존 선택·실제 경로·상태·이력을 보존해 필요한 부분만 수동 병합하며 없는 파일이나 빈 폴더 생성을 강제하지 않습니다. 이 현장은 common 계층만 선택해 `.codex/repository-guidance.md`를 두지 않습니다([적용 기록](APPLICATION.md) 4절). 선택한 계층의 catalog 필수·선택 파일 계약은 유지합니다. [관리 공간 배치 안내](https://github.com/siasia86/31_governances/blob/a6afc868cfb5de27e83650104c80efef3a13362c/apply/common/template/governance_layout.md)를 따릅니다.

## 2. 작업별 읽기 조건

아래 기존 문서 경로는 실제 대상 Git 루트 기준이며 source 전체를 이 profile에 복사하지 않습니다. 가장 관련된 한 문서와 직접 연결된 구현부터 읽습니다.

| 조건           | 기존 문서                   | 선택 범위                                                                 |
|----------------|-----------------------------|---------------------------------------------------------------------------|
| 주제별 조사    | `README.md`                 | 주제 색인에서 필요한 자료를 선택합니다.                                   |
| 계획 재개      | `.governance/PLAN.md`       | 해당 작업의 단계·검증 근거만 확인합니다.                                  |
| 현재 상태      | `.governance/TODO.md`       | 현재 지정 작업과 선행 조건을 확인합니다.                                  |
| 별도 설계 과제 | `TODO2.md`                  | 해당 인프라/governance 과제일 때만 읽습니다.                              |
| 문서 작성·수정 | `.governance/GOVERNANCE.md` | [문서 형식](GOVERNANCE.md#5-문서-형식)의 기본값·저장소 예외를 확인합니다. |

추가 문서는 변경이 다른 영역과 이어질 때 선택합니다. 단순 질문에 모든 기록을 읽지 않습니다.

## 3. 도구별 안내

도구별 선택·읽기 조건은 [Git 루트 AGENTS](../AGENTS.md)의 진입 조건을 따릅니다. 선택한 계층과 이번 작업 범위를 먼저 확인하며 파일 존재를 도구 선택·설치·실제 읽기 성공으로 대신하지 않습니다.

## 4. 상세 결과

상태·다음 행동은 TODO 한 곳에서 갱신합니다. 큰 작업의 범위·완료 조건·결과 링크는 PLAN 또는 대상의 기존 TASK에 둡니다. 결과물 배치 기준은 [GOVERNANCE](GOVERNANCE.md)를 따르며 빈 폴더·영역별 형식 문서를 일괄 생성하지 않습니다.

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-11-14

© 2026 siasia86. Licensed under CC BY 4.0.
