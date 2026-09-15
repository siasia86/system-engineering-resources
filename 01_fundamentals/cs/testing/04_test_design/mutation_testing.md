# Mutation Testing (변형 테스트)
<!-- reference: _reference/software_testing_official_notes.md, _reference/advanced_testing_official_notes.md -->

Mutation Testing은 소스 코드에 의도적인 작은 변형(Mutant)을 주입하고 기존 테스트를 실행하여 테스트가 결함을 감지하는지 평가하는 기법입니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 변형과 판정](#2-변형과-판정) / [3. 실행 절차](#3-실행-절차)             |
| [4. 결과 해석](#4-결과-해석) / [5. 범위와 한계](#5-범위와-한계) / [6. 체크리스트](#6-체크리스트) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

코드 커버리지는 코드가 실행되었는지를 보여주지만, 실행된 코드의 결함을 테스트가 발견하는지까지 직접 보여주지는 않습니다. Mutation Testing은 코드에 변형을 만들고 테스트 실패 여부를 관찰하여 테스트의 결함 감지 능력을 평가합니다.

| 구분       | 의미                                             |
|------------|--------------------------------------------------|
| Original   | 변형하지 않은 원래 코드                          |
| Mutant     | 결함을 모사하도록 변형한 코드                    |
| Killed     | 테스트가 mutant의 동작 차이를 감지한 상태        |
| Survived   | 테스트가 mutant에서도 통과한 상태                |
| Equivalent | 변형했지만 관찰 가능한 동작이 달라지지 않는 상태 |

[⬆ 목차로 돌아가기](#목차)

## 2. 변형과 판정

### 변형 예시

| 변형 유형 | 예시                         |
|-----------|------------------------------|
| 조건 경계 | `<`와 `<=`의 변경            |
| 논리 연산 | `and`와 `or`의 변경          |
| 산술 연산 | `+`와 `-`의 변경             |
| 반환값    | 반환값·조건 결과의 변경      |
| 상수      | 상수·문자열·불리언 값의 변경 |
| 예외 처리 | 예외 발생·처리 경로의 변경   |

변형 연산자는 언어·도구마다 다릅니다. 변형이 실제 결함을 의미하는지와 테스트가 관찰할 수 있는 동작 차이를 확인해야 합니다.

### 판정 흐름

```text
Original 코드에서 테스트 통과
              │
              v
Mutant 생성 후 동일 테스트 실행
       ┌──────┴──────┐
       v             v
테스트 실패       테스트 통과
  Killed          Survived
                      │
                      v
             테스트 누락 또는 Equivalent 검토
```

[⬆ 목차로 돌아가기](#목차)

## 3. 실행 절차

1. 대상 코드·테스트·언어·도구 버전을 고정합니다.
2. 기존 테스트가 정상적으로 통과하는지 먼저 확인합니다.
3. 적용할 변형 연산자와 제외 범위를 정의합니다.
4. mutant를 생성하고 테스트를 실행합니다.
5. Killed·Survived·Equivalent 결과를 분류합니다.
6. Survived mutant를 테스트 누락·오라클 부족·동등 변형으로 분석합니다.
7. 필요한 테스트를 추가하고 동일 mutant를 재실행합니다.
8. 결과와 설정을 기록하여 이후 비교 가능한 기준을 만듭니다.

Mutation Testing은 모든 코드에 항상 적용하기보다 핵심 로직·변경 영역·테스트 품질을 점검할 영역을 우선 선택합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 결과 해석

| 결과        | 해석                                          | 대응                                 |
|-------------|-----------------------------------------------|--------------------------------------|
| Killed      | 테스트가 해당 변형을 감지함                   | 기존 테스트와 변형 결과 기록         |
| Survived    | 테스트가 변형을 감지하지 못했거나 동등 변형임 | 오라클·분기·경계·케이스 검토         |
| Equivalent  | 관찰 가능한 동작 차이가 없는 변형             | 근거와 함께 제외 또는 별도 표시      |
| Timeout     | 변형으로 실행이 종료되지 않음                 | 성능·무한 루프·환경 원인 분석        |
| No coverage | 대상 코드를 실행하는 테스트가 없음            | 기본 테스트와 요구사항 추적부터 보완 |

Mutation 결과는 테스트 품질의 하나의 신호입니다. Survived 수치만으로 테스트 품질을 단정하지 않고, 변형 위치와 생존 원인을 함께 분석합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 범위와 한계

### 적용 범위

- 핵심 비즈니스 규칙과 계산 로직
- 경계·분기·오류 처리 로직
- 최근 변경된 코드와 결함이 반복된 영역
- 테스트 오라클의 충분성을 확인할 영역

### 한계

- Equivalent mutant를 자동으로 완벽히 판정하기 어렵습니다.
- 변형 생성과 테스트 실행 비용이 큽니다.
- 변형 연산자가 실제 결함을 충분히 대표하지 않을 수 있습니다.
- 테스트가 감지하지 않아도 실제 영향이 없는 변형이 있을 수 있습니다.
- 코드 커버리지를 대체하지 않고 보완합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 원래 테스트가 먼저 정상 통과합니다.
- [ ] 언어·도구·변형 연산자·제외 범위를 기록합니다.
- [ ] Killed·Survived·Equivalent·Timeout을 구분합니다.
- [ ] Survived mutant마다 원인을 분석합니다.
- [ ] 테스트 오라클이 변형을 관찰할 수 있는지 확인합니다.
- [ ] 핵심 로직과 변경 영역을 우선 대상으로 선정합니다.
- [ ] 결과를 코드 버전·테스트 버전과 함께 보관합니다.
- [ ] Mutation 결과를 단일 품질 수치로 과장하지 않습니다.

## 참고 자료

- PIT Mutation Testing: [pitest.org](https://pitest.org/) — ★★★☆☆
- PIT Basic Concepts: [pitest.org/quickstart/basic_concepts](https://pitest.org/quickstart/basic_concepts/) — ★★★☆☆
- [테스트 오라클](test_oracle.md)
- [코드 커버리지](../02_white_box/code_coverage.md)

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
