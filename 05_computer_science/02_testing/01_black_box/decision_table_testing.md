# 결정 테이블 테스트 (Decision Table Testing)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 구조](#2-구조) / [3. 작성 방법](#3-작성-방법) |
| [4. 예시](#4-예시) / [5. 최적화](#5-최적화) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

결정 테이블 테스트는 복수 조건의 조합에 따라 다른 동작이 수행되는 시스템을 체계적으로 검증하는 기법입니다.

| 항목            | 내용                                        |
|-----------------|---------------------------------------------|
| 분류            | 블랙박스 테스트 기법                        |
| 핵심 아이디어   | 조건 조합 → 동작 매핑을 표로 정리           |
| 적용 대상       | 비즈니스 규칙, 권한 체계, 요금 정책         |
| 장점            | 누락된 조합 발견, 요구사항 모호성 제거      |

[⬆ 목차로 돌아가기](#목차)

## 2. 구조

```
┌──────────────┬──────┬──────┬──────┬────────┐
│        Decision Table                      │
├──────────────┬──────┬──────┬──────┬────────┤
│ Condition    │ R1   │ R2   │ R3   │ R4     │
├──────────────┼──────┼──────┼──────┼────────┤
│ Cond 1       │ Y    │ Y    │ N    │ N      │
│ Cond 2       │ Y    │ N    │ Y    │ N      │
├──────────────┼──────┼──────┼──────┼────────┤
│ Action       │ R1   │ R2   │ R3   │ R4     │
├──────────────┼──────┼──────┼──────┼────────┤
│ Action 1     │ X    │      │ X    │        │
│ Action 2     │      │ X    │      │ X      │
└──────────────┴──────┴──────┴──────┴────────┘
```

- **조건(Condition)**: 입력 또는 상태 (Y/N 또는 값)
- **규칙(Rule)**: 조건 조합 1개 = 테스트 케이스 1개
- **동작(Action)**: 해당 규칙에서 수행되는 결과

[⬆ 목차로 돌아가기](#목차)

## 3. 작성 방법

1. 조건 식별 (N개)
2. 가능한 조합 나열 (2^N개, boolean 기준)
3. 각 조합에 대한 동작 결정
4. 불가능한 조합 제거
5. 동일 동작 규칙 병합 (최적화)

[⬆ 목차로 돌아가기](#목차)

## 4. 예시

### 예시 1: 온라인 쇼핑 할인

| 조건 \ 규칙        | R1  | R2  | R3  | R4  |
|--------------------|-----|-----|-----|-----|
| VIP 회원           | Y   | Y   | N   | N   |
| 구매 금액 ≥ 5만원  | Y   | N   | Y   | N   |
| **할인율**         | 20% | 10% | 10% | 0%  |
| **무료 배송**      | Y   | Y   | N   | N   |

테스트 케이스 4개로 모든 조합을 커버합니다.

### 예시 2: 로그인 정책

| 조건 \ 규칙          | R1     | R2     | R3       | R4     |
|----------------------|--------|--------|----------|--------|
| ID 존재              | Y      | Y      | Y        | N      |
| PW 일치              | Y      | N      | N        | -      |
| 실패 횟수 < 5        | -      | Y      | N        | -      |
| **동작**             | 로그인 | 실패+1 | 계정잠금 | 에러   |

### 예시 3: 파일 권한

| 조건 \ 규칙    | R1   | R2   | R3   | R4   | R5   |
|----------------|------|------|------|------|------|
| 파일 소유자    | Y    | N    | N    | N    | N    |
| 그룹 멤버      | -    | Y    | Y    | N    | N    |
| 읽기 권한      | -    | Y    | N    | Y    | N    |
| **접근 허용**  | Y    | Y    | N    | Y    | N    |

[⬆ 목차로 돌아가기](#목차)

## 5. 최적화

### 규칙 병합

동작이 동일하고 조건 1개만 다른 규칙은 병합 가능합니다.

```
R1: VIP=Y, 금액≥5만=Y → 할인 20%
R2: VIP=Y, 금액≥5만=N → 할인 10%

→ 병합 불가 (동작이 다름)

R1: VIP=Y, 금액≥5만=Y → 무료배송
R2: VIP=Y, 금액≥5만=N → 무료배송

→ 병합 가능: VIP=Y → 무료배송 (금액 무관)
```

### 조건 수에 따른 규칙 수

| 조건 수 | 최대 규칙 수 | 비고                |
|---------|--------------|---------------------|
| 2       | 4            | 수동 작성 가능      |
| 3       | 8            | 수동 작성 가능      |
| 4       | 16           | 병합/최적화 필요    |
| 5       | 32           | 페어와이즈 고려     |

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- ISTQB Foundation Level Syllabus — ★★★☆☆
- [경계값 분석](boundary_value_analysis.md)
- [동등 분할](equivalence_partitioning.md)

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
