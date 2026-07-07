# E2E 테스트 (End-to-End Testing)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 범위](#2-범위) / [3. 전략](#3-전략) |
| [4. 도구](#4-도구) / [5. 실전 가이드](#5-실전-가이드) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

E2E 테스트는 사용자 관점에서 전체 시스템을 처음부터 끝까지 검증하는 테스트입니다.

| 항목        | 내용                                      |
|-------------|-------------------------------------------|
| 테스트 대상 | 전체 시스템 (UI → API → DB → 외부 서비스) |
| 실행 속도   | 분 단위 (가장 느림)                       |
| 실행 주체   | QA 또는 CI/CD 파이프라인                  |
| 목적        | 실제 사용자 시나리오 검증                 |

### 테스트 피라미드에서의 위치

```
        /\        E2E (소수, 느림, 비용 높음)
       /  \
      /----\
     /      \     Integration
    /--------\
   /          \   Unit (다수, 빠름, 비용 낮음)
  /____________\
```

[⬆ 목차로 돌아가기](#목차)

## 2. 범위

### 검증 대상

| 계층          | 검증 항목                        |
|---------------|----------------------------------|
| UI            | 렌더링, 사용자 인터랙션, 폼 제출 |
| API           | 엔드포인트 응답, 인증/인가       |
| 비즈니스 로직 | 워크플로우 전체 흐름             |
| 데이터        | DB 저장/조회 정합성              |
| 외부 연동     | 결제, 이메일, SMS 등             |

### 유닛/통합/E2E 비교

| 항목      | 유닛      | 통합      | E2E           |
|-----------|-----------|-----------|---------------|
| 범위      | 함수 1개  | 모듈 2개+ | 전체 시스템   |
| Mock      | 대부분    | 일부      | 최소 (실제)   |
| 속도      | ms        | 초        | 분            |
| 유지보수  | 낮음      | 중간      | 높음          |
| 결함 유형 | 로직 오류 | 연동 오류 | 시나리오 오류 |

[⬆ 목차로 돌아가기](#목차)

## 3. 전략

### 핵심 시나리오 우선

모든 경로를 E2E로 테스트하지 않습니다. 핵심 사용자 여정(Critical User Journey)만 선별합니다.

```
우선순위:
  1. 회원가입 → 로그인 → 상품 조회 → 결제 → 주문 확인
  2. 비밀번호 변경 → 재로그인
  3. 관리자 로그인 → 상품 등록 → 노출 확인
```

### 테스트 데이터 관리

| 방식           | 장점      | 단점             |
|----------------|-----------|------------------|
| 시드 데이터    | 재현 가능 | 유지보수 필요    |
| API로 생성     | 독립적    | 테스트 시간 증가 |
| DB 스냅샷 복원 | 빠름      | 스냅샷 관리 필요 |

[⬆ 목차로 돌아가기](#목차)

## 4. 도구

### 웹 UI E2E

| 도구       | 특징                           |
|------------|--------------------------------|
| Playwright | Microsoft, 멀티 브라우저, 빠름 |
| Cypress    | JS 생태계, 디버깅 우수         |
| Selenium   | 오래된 표준, 다양한 언어 지원  |

### API E2E

| 도구         | 특징             |
|--------------|------------------|
| pytest       | Python, 유연함   |
| Postman      | GUI + Newman CLI |
| REST Assured | Java, BDD 스타일 |

### 인프라 E2E

```bash
# 인프라 E2E 예시: 배포 후 헬스체크
curl -sf http://app.example.com/health || exit 1
curl -sf http://app.example.com/api/version | jq .version
```

[⬆ 목차로 돌아가기](#목차)

## 5. 실전 가이드

### E2E 테스트 안티패턴

| 안티패턴         | 문제점            | 해결                 |
|------------------|-------------------|----------------------|
| 모든 것을 E2E로  | 느림, 불안정      | 피라미드 비율 유지   |
| UI 세부사항 검증 | 깨지기 쉬움       | 비즈니스 결과만 검증 |
| 테스트 간 의존성 | 순서 의존         | 각 테스트 독립 실행  |
| 하드코딩된 대기  | `sleep(5)` 불안정 | 조건 기반 대기 사용  |

### 실행 전략

```bash
# PR 시: smoke test (핵심 3~5개)
pytest tests/e2e/ -m smoke --timeout=120

# 배포 전: full E2E
pytest tests/e2e/ --timeout=300

# 정기 실행: 야간 전체 스위트
# cron: 0 2 * * * pytest tests/e2e/
```

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Playwright docs: [playwright.dev](https://playwright.dev/) — ★★★☆☆
- Martin Fowler. "Test Pyramid" — ★★★★☆
- [유닛 테스트](unit_testing.md)
- [통합 테스트](integration_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-08

**마지막 업데이트**: 2026-05-08

© 2026 siasia86. Licensed under CC BY 4.0.
