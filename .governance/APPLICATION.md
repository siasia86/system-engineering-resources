# 32_system-engineering-resources 관리 공간 적용 기록

## 1. 적용

P31-SKILL-ROUTES-20261004-01에서 사용자의 실제 저장소 적용 요청에 따라 .governance 진입·관리 문서를 추가했습니다. 중앙 출발점은 31의 59279f9이며 이번 개정 후보 파일의 적용 해시는 Git 제외 local/P31-SKILL-ROUTES-20261004-01/application.json에 보존했습니다. 기존 운영 기록은 유지하며 개인 skill·제품 소스·DB·runtime은 변경하지 않았습니다.

## 2. 검증과 복구

새 문서의 링크·헤딩·문체와 공개/비공개 ignore를 검사합니다. 기존 관리 문서의 bytes와 적용 전 HEAD·branch·index 및 다른 변경을 대조합니다. 새 세션 선택·행동이나 원격 CI를 문서 적용으로 대신하지 않습니다. 대상 commit/push는 수행하지 않습니다.

복구 시 Git 제외 local/P31-SKILL-ROUTES-20261004-01/before의 원문과 application.json을 현재 파일에 대조하여 이번 추가·병합만 되돌립니다. 이후 사용자 변경과 기존 작업 기록은 유지합니다.

## 3. 위치 전환 — 2026-10-27

MAIN-20261027-05에서 중앙 profile(31 `aaa48f2`)의 관리 문서 위치 기준에 맞춰 루트 `TODO.md`·`PLAN.md`·`CHANGELOG.md`를 `git mv`로 `.governance/`에 옮겼습니다. 이동 문서의 상대 링크 42개와 관리 문서·TODO2·`asd_ste100_codex_communication.md`의 링크를 새 위치로 고치고, GOVERNANCE·INDEX·README의 위치 문구를 중앙 profile 문장으로 바꿨습니다. 루트에는 같은 이름의 연결 안내 문서를 별도 commit으로 두었습니다. `TODO2.md`는 루트에 유지합니다.

AGENTS·INDEX·GOVERNANCE의 나머지 구성과 설정 4개, Codex 안내는 병합하지 않았으며 [ISSUE](ISSUE.md)의 ISS-05로 관리합니다. 31의 적용 이력은 변경하지 않았습니다. 복구는 이번 두 commit을 역순으로 `git revert`합니다.

## 4. 공통 계층 병합 — 2026-10-27

MAIN-20261027-06에서 중앙 profile(31 `origin/main` `e6ada74` 기준, 32 profile 마지막 변경 `aaa48f2`)의 common 계층을 병합했습니다. AGENTS·GOVERNANCE·INDEX는 중앙 원문으로 바꾸고, `.governance/README.md`는 중앙 첫 문단만 추가하고 현장 사실 문장을 유지했습니다.

설정 4개는 중앙 공통 구간에 현장 구간을 합쳤습니다. 검사 TOML 2개는 `exclude_dirs`를 합치고 파일별 예외 6개를 보존했으며, `.gitignore`는 31 COMMON 구간 뒤 CONSUMER LOCAL 구간에 현장 패턴을 옮겼습니다. `.gitleaks.toml`은 중앙 허용 목록에 현장 허용 목록·경로와 탐지 규칙 3개를 보존해 이전과 같은 탐지 결과를 확인했습니다. Codex 계층(`.codex/repository-guidance.md`)은 적용하지 않았으며 ISS-06으로 관리합니다. 복구는 이번 commit을 `git revert`합니다.

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.
