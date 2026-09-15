# 게임 서비스 테스트 실행 계획

게임 서비스의 실제 오픈 전 부하·성능·복구 실행 계획을 관리하는 디렉토리입니다. 범용 테스트 개념은 `01_fundamentals/cs/testing/`, 게임 도메인 개념은 `01_fundamentals/cs/game_testing/`에서 관리합니다.

## 목차

| 섹션                         |
|------------------------------|
| [1. 범위](#1-범위)           |
| [2. 문서 목록](#2-문서-목록) |

[⬆ 목차로 돌아가기](#목차)

## 1. 범위

### 포함

- 모바일 게임 사전 오픈 부하 테스트 계획
- 실제 서비스 기준 부하 모델·SLO·모니터링·실행 절차
- 부하 생성기·테스트 데이터·중단·rollback 절차
- 테스트 결과 보고와 오픈 승인 기준

### 제외

- 범용 테스트 케이스 설계 이론
- 특정 게임의 운영 credential·실제 사용자 데이터
- 승인되지 않은 production 부하·장애 주입
- 모바일 기기 솔루션 비교와 도구 조사

[⬆ 목차로 돌아가기](#목차)

## 2. 문서 목록

| 문서                                                                                       | 설명                                        |
|--------------------------------------------------------------------------------------------|---------------------------------------------|
| [모바일 게임 사전 오픈 부하 테스트 계획서](mobile_game_load_testing_plan.md)               | 부하·성능·복구 실행 계획                    |
| [모바일 게임 기기 테스트 솔루션](../../../97_misc/mobile_game_device_testing_solutions.md) | 기기 테스트 도구 비교는 `97_misc/`에서 관리 |

## 참고 자료

- [Load Testing 공식 참조 노트](../../../_reference/load_testing_official_notes.md)
- [API Styles 공식 참조 노트](../../../_reference/api_styles_official_notes.md)
- [모바일 기기 테스트 공식 참조 노트](../../../_reference/mobile_device_testing_official_notes.md)

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
