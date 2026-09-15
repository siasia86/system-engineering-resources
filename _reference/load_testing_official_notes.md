---
name: load-testing-official-notes
description: 성능·부하 테스트 유형과 서비스 용량·부하 관리의 공식 참조 노트.
tags:
  - load-testing
  - performance-testing
  - stress-testing
  - soak-testing
  - capacity-planning
last_checked: 2026-09-15
sources:
  - https://grafana.com/docs/k6/latest/testing-guides/test-types/
  - https://sre.google/workbook/managing-load/
---

# Load Testing 공식 참조 노트

## 1. 확인 범위

성능·부하 테스트 문서와 게임 서비스 실행 계획에서 사용할 테스트 유형·부하 패턴·용량 관리 원칙을 2026-09-15에 Grafana k6 공식 문서와 Google SRE Workbook 공식 페이지 기준으로 확인했습니다.

## 2. k6 공식 테스트 유형

k6 공식 문서는 다음 테스트 유형을 구분합니다.

| 유형         | 공식 목적                                   |
|--------------|---------------------------------------------|
| Smoke        | 스크립트와 최소 부하에서의 기본 동작 확인   |
| Average-load | 예상되는 정상 부하에서의 성능 확인          |
| Stress       | 평균 또는 예상 부하를 초과한 한계 동작 확인 |
| Soak         | 장시간 부하에서의 안정성과 성능 확인        |
| Spike        | 갑작스럽고 큰 부하 증가에 대한 동작 확인    |
| Breakpoint   | 부하를 점진적으로 늘려 용량 한계 식별       |

k6 공식 문서는 테스트 유형별로 부하 설정과 반복 로직을 분리하고, 낮은 부하의 Smoke Test부터 점진적으로 확장할 것을 설명합니다.

## 3. Google SRE 부하 관리 기준

Google SRE Workbook의 Managing Load 장은 수요 증가·트래픽 급증·서비스 장애에 대응하기 위해 단일 기법이 아닌 부하 분산·용량·트래픽 관리 전략의 조합이 필요하다고 설명합니다.

서비스 실행 계획에서는 다음 항목을 별도로 정의합니다.

- 예상 부하와 피크 부하
- 처리량·지연시간·오류율 목표
- 자동 확장과 확장 지연
- 과부하 시 graceful degradation
- 복구 시간과 잔여 backlog
- 부하 테스트와 실제 트래픽의 차이

## 4. 적용 범위와 제한

이 노트는 부하 테스트 유형과 용량 관리의 공통 기준입니다. HTTP·WebSocket·게임 메시지의 프로토콜별 동작은 `_reference/api_styles_official_notes.md` 또는 해당 프로토콜 공식 문서를 함께 참조합니다.

부하 테스트 수치와 합격 기준은 서비스 환경·사용자 행동·데이터 크기·인프라 구성에 따라 별도로 정합니다. 공식 문서의 테스트 유형을 특정 서비스의 SLO 수치로 직접 변환하지 않습니다.
