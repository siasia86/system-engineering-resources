# TODO

레포 잔여 이슈 및 향후 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                                       |
|--------------------------------------------|
| [1. 잔여 이슈](#1-잔여-이슈)               |
| [2. 테스트 문서 확장](#2-테스트-문서-확장) |

---

## 1. 잔여 이슈

기존 잔여 이슈는 없습니다. 개인정보 보호법 가이드의 제34조 통지 기한·통지 항목 fact-check는 2026-09-14에 완료했으며, 상세 내용은 `CHANGELOG.md`에 기록했습니다.

### 검사 예외 파일

| 파일                                               | 사유                                   |
|----------------------------------------------------|----------------------------------------|
| `01_fundamentals/linux/vim_airline.md`             | 외부 프로젝트(vim-airline) README 원본 |
| `06_career/ai_tools/kiro_cli_command_reference.md` | Kiro CLI 문서 (다이어그램 한글 의도적) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 테스트 문서 확장

테스트 문서는 범용 테스트 케이스 개념, 게임 도메인 테스트 개념, 게임 서비스 실행 계획으로 분리하여 작성합니다. 각 문서군의 목적과 적용 범위를 섞지 않습니다.

### 2-1. 범용 테스트 케이스 개념 문서

대상 경로: `01_fundamentals/cs/testing/`

- [ ] `04_test_design/test_case_design.md` — 테스트 케이스 구성 요소와 작성 규칙
- [ ] `04_test_design/test_oracle.md` — 기대 결과와 합격·실패 판단 기준
- [ ] `04_test_design/scenario_based_testing.md` — 사용자·업무 시나리오 기반 테스트 설계
- [ ] `04_test_design/risk_based_testing.md` — 위험도 기반 테스트 범위와 우선순위
- [ ] `04_test_design/test_traceability.md` — 요구사항·위험·케이스·결과 간 추적성
- [ ] `04_test_design/test_data_management.md` — 테스트 데이터 생성·격리·초기화·정리
- [ ] `04_test_design/concurrency_testing.md` — 동시 실행·경쟁 조건·교착 상태 검증
- [ ] `04_test_design/fault_injection_testing.md` — 장애 주입 기반 테스트 설계
- [ ] `04_test_design/exploratory_testing.md` — 탐색적 테스트의 목적과 실행 전략
- [ ] `04_test_design/property_based_testing.md` — 속성·불변 조건 기반 테스트
- [ ] `02_white_box/mutation_testing.md` — 코드 변형 기반 테스트 품질 평가

### 2-2. 게임 도메인 테스트 개념 문서

대상 경로: `01_fundamentals/cs/game_testing/`

- [ ] `README.md` — 게임 테스트 개념 문서의 범위와 문서 목록
- [ ] `game_test_case_design.md` — 게임 테스트 케이스의 공통 구성과 설계 기준
- [ ] `game_state_testing.md` — 게임 상태·상태 전이·복구 검증
- [ ] `gameplay_scenario_testing.md` — 게임 플레이 흐름과 사용자 시나리오 검증
- [ ] `save_load_testing.md` — 저장·불러오기·중단 후 복구 검증
- [ ] `matchmaking_testing.md` — 매칭·방·세션 규칙 검증
- [ ] `game_economy_testing.md` — 재화·보상·인벤토리 정합성 검증
- [ ] `game_performance_testing.md` — 게임 도메인의 성능 지표와 테스트 관점

### 2-3. 게임 서비스 실행 계획 문서

대상 경로: `03_engineering/delivery/game_service_testing/`

- [ ] `03_engineering/delivery/game_service_testing/` 디렉토리 생성
- [ ] `97_misc/mobile_game_load_testing_plan.md`를 목표 경로로 `git mv` 후 보완 — 모바일 게임 사전 오픈 부하 테스트 계획
- [ ] `97_misc/mobile_game_device_testing_solutions.md`의 문서 성격을 확인하고 목표 경로 이관 또는 `97_misc/` 유지 결정
- [ ] 이관 시 기존 내부 링크·README inventory 갱신
- [ ] 이관 후 `97_misc/`에 불필요한 원본이 남지 않았는지 확인
- [ ] 이관 실패 시 이전 경로로 복구할 수 있는 rollback 절차 기록
- [ ] 게임 사용자 여정별 부하 시나리오 — 로그인·로비·매칭·게임·보상 흐름
- [ ] 실시간 연결 및 재연결 시나리오 — 장기 연결·재접속 폭주·세션 복구
- [ ] 게임 데이터 정합성 시나리오 — 재화·보상·랭킹·결제 중복 처리
- [ ] Node.js·C#·Unity 런타임별 관측 지표 — Event Loop·GC·ThreadPool·Frame/Tick
- [ ] 실제 서비스 기준 부하 모델·SLO·모니터링·실행 절차 정리

### 2-4. 문서군별 공통 `_reference` 선행 작업

문서마다 별도 reference 파일을 복제하지 않고, 같은 기술·도메인을 다루는 여러 문서가 공통 reference note를 참조합니다. 공통 reference note가 없으면 공식 홈페이지·표준·공식 문서로 먼저 작성한 뒤 `_reference/INDEX.md`에 한 번 등록합니다.

#### 공통 reference note 매핑

- [ ] 범용 테스트 개념 문서 → `_reference/software_testing_official_notes.md`
  - 대상: `test_case_design`, `test_oracle`, `scenario_based`, `risk_based`, `test_traceability`, `test_data_management`, `concurrency`, `exploratory`
- [ ] 게임 도메인 테스트 개념 문서 → `_reference/game_testing_official_notes.md`
  - 대상: `game_test_case_design`, `game_state`, `gameplay_scenario`, `save_load`, `matchmaking`, `game_economy`
- [ ] 범용 고급 테스트 문서 → `_reference/software_testing_official_notes.md` + 주제별 공식 출처
  - 대상: `fault_injection`, `property_based`, `mutation_testing`
- [ ] 게임 서비스 부하 계획 → `_reference/load_testing_official_notes.md`
  - 추가 참조: `_reference/api_styles_official_notes.md`, `_reference/mobile_device_testing_official_notes.md`
- [ ] 게임 도메인 성능 문서 → `_reference/game_testing_official_notes.md` + `_reference/load_testing_official_notes.md`
- [ ] `01_fundamentals/cs/game_testing/README.md` → `N/A (문서 목록용 README)`

#### 공통 참조 절차

- [ ] 공통 reference note마다 `last_checked`, 공식 `sources`, 권장사항·변경사항 기록
- [ ] 공통 reference note마다 `_reference/INDEX.md`에 한 번만 등록
- [ ] 각 본문 문서의 H1 제목 바로 아래에 실제 사용하는 공통 reference 파일의 `reference` HTML 주석 추가
- [ ] `N/A (문서 목록용 README)`는 reference 생성·본문 fact-check를 생략하고 링크·헤딩·Markdown 검사만 수행
- [ ] 공통 `_reference` 파일별 `@fact-check` 1회차 실행 — 공식 URL 접근 및 원문 내용 대조
- [ ] 1회차 결과 반영 후 공통 `_reference` 파일별 `@fact-check` 2회차 실행 — 수정사항 재검증 및 잔여 오류 확인
- [ ] 각 `@fact-check` 회차의 검증 결과·출처·수정 사항 기록
- [ ] 공통 reference를 연결한 본문 `.md`는 문서 대상 fact-check 회차 규칙(3회)을 별도로 적용
- [ ] 공통 reference 작성·INDEX 등록·`@fact-check` 2회 완료 후 본문 작성
- [ ] 본문 작성 후 Markdown style·heading·link 검사를 실행

### 2-5. 컨텍스트 분할 작업 및 재개 규칙

문서 작성은 컨텍스트 사용량을 고려하여 기본 3개 문서 이하 단위의 배치(Batch)로 분리합니다. 각 배치는 독립적으로 완료·검증한 뒤 다음 배치로 진행합니다.

#### 배치별 공통 절차

1. 미완료 문서 3개 이하를 배치 대상으로 확정합니다.
2. 대상 문서군의 공통 `_reference` 확인·생성 및 `_reference/INDEX.md` 등록을 먼저 완료합니다.
3. 대상 공통 `_reference`별 `@fact-check` 2회 실행과 결과 기록을 완료합니다.
4. 참조 작업이 완료된 문서만 본문을 작성합니다.
5. `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check`, `git diff --check`를 실행합니다.
6. 문서별 commit·push 성공을 확인합니다.
7. 저장소 루트 `TODO.md`에 배치 결과와 남은 작업을 기록하고 다음 배치로 이동합니다.

#### 배치 시작·종료 출력

- 배치 시작 시 `=== Batch N: items A~B ===` 형식으로 대상·`_reference` 상태·검증 단계를 출력합니다.
- 배치 종료 시 `=== Batch N complete ===` 형식으로 문서별 검사·fact-check·commit·push 결과를 출력합니다.
- Pre/Post 결과에 README·CHANGELOG 처리 상태를 `deferred` 또는 `updated`로 기록합니다.

#### 권장 배치 순서

| 배치 | 상태 | 대상                                                        | 목적                         |
|------|------|-------------------------------------------------------------|------------------------------|
| 1    | [ ]  | 범용 `test_case_design`, `test_oracle`, `scenario_based`    | 테스트 케이스 기본 구조 확립 |
| 2    | [ ]  | 범용 `risk_based`, `test_traceability`, `test_data`         | 위험·추적성·데이터 관리 정리 |
| 3    | [ ]  | 범용 `concurrency`, `fault_injection`, `exploratory`        | 예외·장애·동시성 설계 정리   |
| 4    | [ ]  | 범용 `property_based`, `mutation_testing`                   | 고급 테스트 기법 정리        |
| 5    | [ ]  | 게임 도메인 `README`, `game_test_case_design`, `game_state` | 게임 테스트 개념의 범위 확정 |
| 6    | [ ]  | 게임 도메인 `gameplay_scenario`, `save_load`, `matchmaking` | 게임 상태·플레이 흐름 정리   |
| 7    | [ ]  | 게임 도메인 `game_economy`, `game_performance`              | 게임 정합성·성능 개념 정리   |
| 8-1  | [ ]  | 부하 테스트 계획·디바이스 테스트 솔루션                     | 실행 문서 이관·분류          |
| 8-2  | [ ]  | 사용자 여정·실시간 연결·재연결 시나리오                     | 서비스 부하 시나리오 정리    |
| 8-3  | [ ]  | 데이터 정합성·런타임 지표·SLO·모니터링                      | 실행 기준과 관측 항목 정리   |

#### 중단·재개 규칙

- 배치 중단 시 완료 항목은 `[x]`, 미완료 항목은 `[ ]`로 즉시 표시합니다.
- 다음 세션에서는 TODO의 첫 번째 미완료 배치부터 재개합니다.
- 이전 배치의 `_reference`, `@fact-check`, Markdown 검증, commit·push가 완료되지 않았으면 다음 배치로 넘어가지 않습니다.
- 컨텍스트가 부족하면 현재 문서의 부분 작성보다 배치 종료·상태 기록을 우선합니다.
- 각 배치 완료 후 문서별 검증 결과와 잔여 이슈를 TODO 또는 `CHANGELOG.md`에 기록합니다.

### 2-6. TODO 완료 후 문서별 commit·push 규칙

각 TODO 항목은 해당 문서와 공통 reference note, 검증, 문서별 commit·push가 모두 완료된 뒤 `[x]`로 변경합니다.

#### 문서별 완료 절차

1. 대상 문서의 본문 작성과 필요한 공통 reference note 연결을 완료합니다.
2. 공통 `_reference`의 `@fact-check` 2회와 본문 문서 fact-check를 완료합니다.
3. `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check`, `git diff --check`를 통과합니다.
4. 대상 문서와 관련 참조 파일을 명시적으로 stage하고 `git diff --cached` 및 `git diff --cached --check`를 확인합니다.
5. 문서 단위 commit을 생성합니다.
6. `git push origin yunli`로 push하고 원격 반영을 확인합니다.
7. push 성공 후 해당 문서 TODO 항목과 배치 상태를 `[x]`로 변경합니다.
8. TODO 변경을 별도 commit하고 `git push origin yunli`로 push합니다.
9. TODO commit과 원격 반영 상태를 확인합니다.

#### 파일 단위 예외

- 본문 문서와 공통 `_reference` 파일은 각각 독립적으로 검증 가능한 경우 파일 단위로 별도 commit·push합니다.
- 하나의 공통 `_reference` 파일은 여러 본문 문서가 공유하므로 문서마다 중복 commit·push하지 않습니다.
- `_reference` 파일과 `_reference/INDEX.md`는 인덱스 정합성을 위해 하나의 논리적 commit으로 묶습니다.
- 본문 문서가 아직 원격에 없는 공통 `_reference`를 참조하지 않도록 참조 노트 commit·push를 먼저 완료합니다.
- 디렉토리 이관은 `refactor` commit으로 분리하고, 이관 대상 파일·링크·README만 포함합니다.
- 한 commit에 unrelated 문서나 다른 배치의 파일을 포함하지 않습니다.

#### Git 안전 규칙

- commit 전 `git branch --show-current`로 `yunli` 브랜치를 확인합니다.
- `yunli`가 아니면 작업을 중단하고 브랜치를 확인합니다.
- 작업 브랜치에만 push하며 `main`·`master`에는 직접 push하지 않습니다.
- `git add .` 대신 대상 파일만 명시적으로 stage합니다.
- commit 메시지는 `git-commit-rule` 형식(`<type>: <한글 설명>`, 50자 이내, 마침표 없음)을 따릅니다.
- push 실패 시 원인을 기록하고, 성공할 때까지 TODO 완료 상태로 표시하지 않습니다.
- 최종 배치에서는 관련 README inventory와 `CHANGELOG.md`를 갱신한 뒤 최종 검증·commit·push를 진행합니다.

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-09-15

© 2026 siasia86. Licensed under CC BY 4.0.
