# TODO2

문서 검사 도구와 저장소 규칙 체계 작업의 임시 후속 문서입니다. 완료된 작업은
`CHANGELOG.md`와 `governance_todo.md`에 기록했으며, 이 문서에는 현재 미완료 작업과
예정 재검토만 유지합니다.

## 목차

| 섹션                             |
|----------------------------------|
| [1. 남은 작업](#1-남은-작업)     |
| [2. 예정 재검토](#2-예정-재검토) |
| [3. 종료 조건](#3-종료-조건)     |

---

## 1. 남은 작업

### 1.1 Ansible profile 정리 (병행 기간 후)

- [ ] 병행 기간 후 `profiles/chobo_ansible.md` 제거
      - `.governance/GOVERNANCE.md`와 `.governance/verification.md`가 기존 profile 없이
        정상적으로 사용되는지 먼저 확인합니다.
      - profile을 참조하는 에이전트·문서·자동화가 없는지 확인한 뒤 삭제합니다.
- [ ] 제거 후 `profiles/` 디렉토리 존치 여부 결정
      - 디렉토리 내 잔여 파일과 참조를 확인합니다.
      - 저장소 자체 profile이 필요하면 유지하고, 비어 있으면 제거 여부를 결정합니다.

현재는 병행 기간이므로 두 항목을 실행하지 않습니다. 삭제 시에는 대상 목록을 먼저
출력하고 승인한 뒤 실행합니다.

## 2. 예정 재검토

- 2026-11-30: `network_headers.md`의 `box-chars` 예외를 도구 개선 후 해제할 수 있는지 확인합니다.
- 2026-11-30: `ddos_defense_architecture.md`의 `diagram-width` 예외를 도구 개선 후 해제할 수 있는지 확인합니다.
- 조건 충족 시: `00_governance/` 하위 영역을 별도 저장소로 분리할 필요가 있는지 재검토합니다.

## 3. 종료 조건

다음 조건을 모두 충족하면 `TODO2.md`를 제거하거나 정식 `TODO.md` 체계로 통합합니다.

- Ansible profile 병행 기간이 종료됩니다.
- profile 참조와 잔여 파일을 확인합니다.
- `profiles/chobo_ansible.md`와 `profiles/` 존치 여부를 결정합니다.
- 예정 재검토 항목은 결과를 CHANGELOG 또는 해당 정책 문서에 기록합니다.

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.
