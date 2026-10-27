# 32_system-engineering-resources 작업 지침

관리 문서의 공통 기준 위치는 `.governance/`이며 INDEX·GOVERNANCE·PLAN·TODO·ISSUE·verification·CHANGELOG·HANDOFF의 이름과 역할을 통일합니다. 기존 기록은 보존하고 승인된 현장 전환에서 현행 상태를 한 번 병합하며 이전 위치는 연결 안내로 유지합니다. 이 profile 개정만으로 다른 현장 적용이 완료된 것은 아닙니다.

기존 root AGENTS에 필요한 연결을 병합할 원본입니다. 기존 지침·하위 override·사용자 변경을 보존하며 현재 사용자 요청과 실제 Git 루트·branch·변경부터 확인합니다.

## 1. 대상과 경계

공식·웹·저장소 자료 조사와 기술 문서를 대상으로 합니다. 32에서 출처·확인일·버전·지원 근거·미확인을 기록합니다. 필요한 실제 참고 clone은 41, agent/skill 구현·설치는 35의 담당 범위입니다. 조사 기록을 운영 호스트 변경 승인으로 해석하지 않습니다.

전체 문서나 다른 저장소 profile을 자동 적용하지 않고 현재 작업의 직접 근거를 선택합니다.

## 2. 필요한 문서와 기록

기존 소스 탐색 지침을 먼저 따르고 관리 구조·작업별 읽기 조건은 [관리 INDEX](.governance/INDEX.md)에서 필요한 부분만 확인합니다. 상태는 [TODO](.governance/TODO.md), 실행·검증·복구 순서는 [PLAN](.governance/PLAN.md), 원인·영향은 [ISSUE](.governance/ISSUE.md)에 둡니다.

현행 PLAN·TODO·CHANGELOG와 공통 관리 문서는 .governance에 통일합니다. 이전 루트 상태·이력을 실제 적용에서 보존·병합하고 TODO2 상세 설계 과제를 일반 작업에 일괄 적용하지 않습니다. 관리 공간 배치를 skill 설치·자동 선택 성공으로 대신하지 않습니다.

소유 적용 기록이나 이번 배정에서 `common+codex`를 선택해 수동 병합한 Codex 작업은 Git 루트 기준 `.codex/repository-guidance.md`를 이 작업 문맥에서 한 번 읽습니다. 파일이 있다는 사실만으로 선택한 조합을 판정하지 않습니다. 선택한 안내가 없으면 실패로 기록하고 관련 도구 구간을 대기하며 재개 조건을 남깁니다.

`common`만 선택한 경우에는 없는 Codex 안내를 필수로 요구하지 않습니다. 선택 기록용 새 파일이나 별도 승인 단계를 추가하지 않으며 안내 파일 이름만으로 도구의 자동 탐색·실제 읽기 성공을 판단하지 않습니다.

## 3. 검증과 게시

[검증 기준](.governance/verification.md)에서 최소 검사를 선택하고 실행·부분 검사·실패·미실행을 구분합니다. 현재 사용자 요청과 실제 대상 지침으로 branch·게시 범위를 정합니다. 조회 당시 branch나 옛 계획의 게시 규칙을 자동 고정하지 않습니다.

담당 파일만 stage하고 기존 코드·기록·private 자료를 보존합니다. 자세한 운영·결과물 기준은 [GOVERNANCE](.governance/GOVERNANCE.md), 완료 근거는 [완료 기록](.governance/CHANGELOG.md)에서 확인합니다.

## 4. 저장소 지침 수정 경로

이 저장소의 AGENTS·운영 문서는 `31_governances/common/profile/32_system-engineering-resources/`에서 수정·검증·게시한 뒤 대상에 병합합니다. 일반 작업은 실제 적용된 지침을 따르며 중앙 조회는 출처 확인·개정·배포가 필요한 때 수행합니다. 상세 수정 workflow는 31의 `common/skill-maintenance.md`에서 확인합니다.

현장의 PLAN/TODO·완료 이력·사용자 차이를 보존합니다. 현재 수동 반영하며 31 변경의 CI/CD 자동 적용은 후속 예정입니다.

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.
