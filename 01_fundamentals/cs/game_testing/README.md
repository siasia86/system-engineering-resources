# 게임 테스트 (Game Testing)

게임 테스트는 게임의 규칙·상태·플레이 흐름·저장·복구를 검증하는 도메인 테스트 영역입니다. 이 디렉토리는 특정 회사·게임·엔진의 운영 절차가 아닌 재사용 가능한 개념을 다룹니다.

## 목차

| 섹션                                              |
|---------------------------------------------------|
| [1. 범위](#1-범위) / [2. 문서 목록](#2-문서-목록) |

[⬆ 목차로 돌아가기](#목차)

## 1. 범위

### 포함

- 게임 테스트 케이스의 공통 구조
- 게임 상태·상태 전이·복구
- 플레이 시나리오와 사용자 흐름
- 저장·불러오기·중단 후 재실행
- 매칭·방·세션의 일반 테스트 관점
- 재화·보상·인벤토리의 정합성
- 게임 기능과 성능을 분리한 테스트 관점

### 제외

- 특정 게임의 실제 서버 주소·계정·운영 데이터
- 특정 회사의 출시 일정·담당자·SLO
- Node.js·C#·Unity 특정 버전의 구현 절차
- 실제 부하 테스트 실행 계획과 인프라 배포 명령

게임 서비스 실행 계획은 `03_engineering/delivery/game_service_testing/`에서 별도로 관리합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 문서 목록

| 문서                                                 | 설명                                     |
|------------------------------------------------------|------------------------------------------|
| [게임 테스트 케이스 설계](game_test_case_design.md)  | 게임 규칙·상태·흐름을 반영한 케이스 설계 |
| [게임 상태 테스트](game_state_testing.md)            | 상태·이벤트·전이·복구 검증               |
| [게임 플레이 시나리오](gameplay_scenario_testing.md) | 플레이 목표·흐름·분기·복구 시나리오      |
| [저장·불러오기 테스트](save_load_testing.md)         | 저장·복구·호환성·정합성 검증             |
| [매칭 테스트](matchmaking_testing.md)                | 조건·대기열·방·세션·재시도 검증          |
| [게임 경제 테스트](game_economy_testing.md)          | 재화·보상·거래·정합성 검증               |
| [게임 성능 테스트](game_performance_testing.md)      | 게임 루프·네트워크·서버·데이터 성능      |

## 참고 자료

- Unity Test Framework: [docs.unity3d.com](https://docs.unity3d.com/Packages/com.unity.test-framework@1.3/manual/index.html) — ★★★☆☆
- Firebase Test Lab Game Loop: [firebase.google.com](https://firebase.google.com/docs/test-lab/game-loop) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-15

**마지막 업데이트**: 2026-09-15

© 2026 siasia86. Licensed under CC BY 4.0.
