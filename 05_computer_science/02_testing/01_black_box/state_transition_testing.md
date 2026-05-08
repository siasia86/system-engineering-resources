# 상태 전이 테스트 (State Transition Testing)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 구성 요소](#2-구성-요소) / [3. 다이어그램](#3-다이어그램) |
| [4. 테스트 설계](#4-테스트-설계) / [5. 예시](#5-예시) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

상태 전이 테스트는 시스템이 이벤트에 따라 상태를 변경하는 동작을 검증하는 기법입니다.

| 항목          | 내용                                          |
|---------------|-----------------------------------------------|
| 분류          | 블랙박스 테스트 기법                          |
| 핵심 아이디어 | 상태 + 이벤트 → 전이 + 동작                   |
| 적용 대상     | 로그인 시도, 주문 상태, 네트워크 연결, ATM    |
| 장점          | 유효/무효 전이를 체계적으로 식별              |

[⬆ 목차로 돌아가기](#목차)

## 2. 구성 요소

| 요소       | 설명                          | 예시                    |
|------------|-------------------------------|-------------------------|
| 상태       | 시스템의 현재 조건            | 잠금, 활성, 만료        |
| 이벤트     | 상태 변경을 유발하는 입력     | 로그인 시도, 타임아웃   |
| 전이       | 상태 A → 상태 B 이동          | 잠금 → 활성             |
| 동작       | 전이 시 수행되는 행위         | 세션 생성, 알림 발송    |
| 가드 조건  | 전이 발생 조건                | 실패 횟수 < 3           |

[⬆ 목차로 돌아가기](#목차)

## 3. 다이어그램

### 상태 전이 다이어그램

```
                 login_success
  ┌────────┐ ──────────────────> ┌────────┐
  │ Locked │                     │ Active │
  └────────┘ <────────────────── └────────┘
       ^         timeout/logout       │
       │                              │ 3 failures
       │         3 failures            v
       └───────────────────── ┌──────────┐
                              │ Suspended│
                              └──────────┘
```

### 상태 전이 표

| 현재 상태  | 이벤트          | 다음 상태  | 동작            |
|------------|-----------------|------------|-----------------|
| Locked     | login_success   | Active     | 세션 생성       |
| Locked     | login_fail      | Locked     | 실패 카운트 +1  |
| Active     | logout          | Locked     | 세션 삭제       |
| Active     | timeout         | Locked     | 세션 만료       |
| Active     | login_fail [>=3]| Suspended  | 계정 잠금       |
| Suspended  | admin_unlock    | Locked     | 카운트 초기화   |

[⬆ 목차로 돌아가기](#목차)

## 4. 테스트 설계

### 커버리지 수준

| 수준              | 설명                              | 테스트 수 |
|-------------------|-----------------------------------|-----------|
| 모든 상태 커버    | 각 상태를 최소 1회 방문           | 적음      |
| 모든 전이 커버    | 각 유효 전이를 최소 1회 실행      | 중간      |
| 무효 전이 커버    | 허용되지 않는 전이 시도 검증      | 많음      |
| N-switch 커버     | N번 연속 전이 시퀀스 검증         | 매우 많음 |

### 유효 전이 테스트

정상적인 상태 변경 경로를 검증합니다.

```
TC1: Locked → login_success → Active → logout → Locked
TC2: Locked → login_fail → Locked → login_fail → Locked → login_fail → Suspended
TC3: Suspended → admin_unlock → Locked → login_success → Active
```

### 무효 전이 테스트

허용되지 않는 이벤트가 발생했을 때 시스템이 올바르게 거부하는지 검증합니다.

```
TC4: Suspended 상태에서 login_success 시도 → 거부 (전이 불가)
TC5: Locked 상태에서 logout 시도 → 무시 또는 에러
```

[⬆ 목차로 돌아가기](#목차)

## 5. 예시

### 예시 1: TCP 연결 상태

```
CLOSED → SYN_SENT → ESTABLISHED → FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED
```

### 예시 2: 주문 상태

| 현재 상태 | 이벤트     | 다음 상태 |
|-----------|------------|-----------|
| 장바구니  | 결제       | 결제완료  |
| 결제완료  | 배송시작   | 배송중    |
| 배송중    | 배송완료   | 완료      |
| 결제완료  | 취소요청   | 취소      |
| 배송중    | 취소요청   | 배송중 (거부) |

### 예시 3: ATM

| 현재 상태 | 이벤트       | 다음 상태 | 동작          |
|-----------|--------------|-----------|---------------|
| 대기      | 카드 삽입    | PIN 입력  | PIN 요청      |
| PIN 입력  | PIN 정확     | 메뉴      | 메뉴 표시     |
| PIN 입력  | PIN 오류 ×3  | 카드 회수 | 카드 삼킴     |
| 메뉴      | 출금 선택    | 출금      | 금액 입력     |
| 출금      | 완료         | 대기      | 카드 반환     |

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- ISTQB Foundation Level Syllabus — ★★★☆☆
- [TCP 상태 전이](../../TCP_state.md)
- [결정 테이블 테스트](decision_table_testing.md)

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
