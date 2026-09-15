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

테스트 문서는 범용 테스트 케이스 개념과 게임 서비스에 종속된 실전 테스트 문서로 분리하여 작성합니다. 두 문서군의 목적과 적용 범위를 섞지 않습니다.

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

### 2-2. 게임 서비스 특화 테스트 문서

대상 경로: `97_misc/`

- [ ] `97_misc/mobile_game_load_testing_plan.md` 검토·보완 — 모바일 게임 사전 오픈 부하 테스트 계획
- [ ] `97_misc/mobile_game_device_testing_solutions.md` 검토·보완 — 모바일 게임 디바이스 테스트 솔루션 비교
- [ ] 게임 사용자 여정별 부하 시나리오 — 로그인·로비·매칭·게임·보상 흐름
- [ ] 실시간 연결 및 재연결 시나리오 — 장기 연결·재접속 폭주·세션 복구
- [ ] 게임 데이터 정합성 시나리오 — 재화·보상·랭킹·결제 중복 처리
- [ ] Node.js·C#·Unity 런타임별 관측 지표 — Event Loop·GC·ThreadPool·Frame/Tick

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-09-15

© 2026 siasia86. Licensed under CC BY 4.0.

