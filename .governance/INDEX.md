# 32_system-engineering-resources 관리 INDEX

## 1. 구조와 원본

[규칙](GOVERNANCE.md)·[현행 상태](../TODO.md)·[계획](../PLAN.md)·[문제](ISSUE.md)·[검증](verification.md)·[완료](../CHANGELOG.md)·[재개](HANDOFF.md)의 역할을 구분합니다. 기존 루트 PLAN·TODO·TODO2·CHANGELOG 위치를 유지합니다. 새 공통 진입·규칙·이슈 후보는 .governance에서 연결하며 TODO2의 별도 설계 과제를 일반 작업에 일괄 적용하지 않습니다.

## 2. 작업별 읽기 조건

아래 기존 문서 경로는 실제 대상 Git 루트 기준이며 source 전체를 이 profile에 복사하지 않습니다. 가장 관련된 한 문서와 직접 연결된 구현부터 읽습니다.

| 조건           | 기존 문서   | 선택 범위                                    |
|----------------|-------------|----------------------------------------------|
| 주제별 조사    | `README.md` | 주제 색인에서 필요한 자료를 선택합니다.      |
| 계획 재개      | `PLAN.md`   | 해당 작업의 단계·검증 근거만 확인합니다.     |
| 현재 상태      | `TODO.md`   | 현재 지정 작업과 선행 조건을 확인합니다.     |
| 별도 설계 과제 | `TODO2.md`  | 해당 인프라/governance 과제일 때만 읽습니다. |

추가 문서는 변경이 다른 영역과 이어질 때 선택합니다. 단순 질문에 모든 기록을 읽지 않습니다.

## 3. Skill과 도구

현재 Codex 세션에서 실제 제공되는 skill만 작업 조건에 따라 선택합니다.

| 조건                 | 선택할 수 있는 skill   |
|----------------------|------------------------|
| 지속 작업·재개·기록  | work-rules             |
| 큰 작업 분해·의존성  | planning-and-breakdown |
| 코드·스크립트 검토   | code-review            |
| 실패 원인·복구       | debugging-and-recovery |
| Markdown 구조·일관성 | markdown-review        |
| 링크·헤딩·앵커       | md-link-check          |
| 담당 파일 commit     | git-commit-rule        |

이 표는 설치나 전체 skill 로드 지시가 아닙니다. 제공되지 않는 도구·skill은 사용 불가를 기록하고 현재 대상의 검증 기준을 따릅니다.

## 4. 상세 결과

상태·다음 행동은 TODO 한 곳에서 갱신합니다. 큰 작업의 범위·완료 조건·결과 링크는 PLAN 또는 대상의 기존 TASK에 둡니다. 결과물 경로와 날짜 규칙은 [GOVERNANCE](GOVERNANCE.md)를 따르며 빈 폴더·영역별 형식 문서를 일괄 생성하지 않습니다.

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-10-03

© 2026 siasia86. Licensed under CC BY 4.0.
