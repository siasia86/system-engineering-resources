# Property-based Testing (속성 기반 테스트)
<!-- reference: _reference/software_testing_official_notes.md, _reference/advanced_testing_official_notes.md -->

Property-based Testing은 특정 예시 입력 몇 개를 검증하는 대신, 입력 공간에서 항상 유지되어야 하는 속성(Property)을 정의하고 다양한 입력을 생성하여 그 속성을 검증하는 테스트 기법입니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 예시 기반 테스트와 비교](#2-예시-기반-테스트와-비교) / [3. 속성 설계](#3-속성-설계) |
| [4. 입력 생성](#4-입력-생성) / [5. 실패 분석](#5-실패-분석) / [6. 체크리스트](#6-체크리스트)                 |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

속성은 입력값 자체가 아니라 실행 결과가 만족해야 하는 일반 규칙입니다.

| 구분           | 검증 방식                              |
|----------------|----------------------------------------|
| 예시 기반      | 미리 정한 입력과 기대 결과 비교        |
| 속성 기반      | 다양한 입력에 대해 불변 조건·관계 검증 |
| 참조 모델 비교 | 독립 구현·계산 결과와 비교             |
| 변환 관계 검증 | 입력 변환 전후 결과 관계 검증          |

Property-based Testing은 예시 기반 테스트를 대체하지 않습니다. 대표적인 업무 예시는 예시 기반으로, 넓은 입력 공간의 일반 규칙은 속성 기반으로 보완합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 예시 기반 테스트와 비교

| 항목      | 예시 기반 테스트           | Property-based Testing           |
|-----------|----------------------------|----------------------------------|
| 입력 선택 | 사람이 지정한 대표 입력    | 전략·생성기가 다양한 입력 생성   |
| 기대 결과 | 입력별 기대값              | 불변 조건·관계·오류 조건         |
| 강점      | 읽기 쉽고 업무 사례에 적합 | 예상하지 못한 조합과 경계 탐색   |
| 주의점    | 입력 공간 누락 가능        | 속성·생성기 품질에 결과가 좌우됨 |
| 실패 분석 | 해당 입력과 기대값 비교    | 실패 입력 축소와 재현 정보 확인  |

[⬆ 목차로 돌아가기](#목차)

## 3. 속성 설계

### 속성 유형

| 속성 유형   | 의미                                       | 예시                                |
|-------------|--------------------------------------------|-------------------------------------|
| 불변 조건   | 실행 전후 또는 실행 중 계속 유지되는 조건  | 정렬 결과가 순서를 만족             |
| 보존 관계   | 변환 전후 보존되어야 하는 값·관계          | encode 후 decode 결과가 원본과 일치 |
| 멱등성      | 같은 작업을 반복해도 결과가 더 변하지 않음 | 동일 요청 재실행 후 최종 상태 동일  |
| 교환 관계   | 순서를 바꾸어도 결과가 같아야 하는 조건    | 독립 항목의 처리 순서               |
| 역변환 관계 | 한 변환의 역변환이 원래 값을 복원          | serialize·deserialize               |
| 오류 경계   | 잘못된 입력은 정의된 오류로 처리           | 허용되지 않는 형식 거부             |

좋은 속성은 입력 범위와 예외 조건이 명확하고, 구현 코드와 동일한 계산을 반복하지 않으며, 실패 시 원인을 좁힐 수 있어야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 입력 생성

### 생성 전략

- 유효·무효·경계 입력을 구분합니다.
- 빈 값·최소 구조·최대 구조·특수 문자를 포함합니다.
- 서로 의존하는 필드는 생성 순서와 관계를 함께 정의합니다.
- 난수 seed·도구 버전·생성 설정을 기록하여 실패를 재현합니다.
- 도메인 제약을 위반하는 입력은 의도적으로 생성할지 분리합니다.

### 의사 코드

```python
@given(values=lists(integers()))
def test_sort_preserves_values(values):
    result = sort(values)
    assert is_sorted(result)
    assert multiset(result) == multiset(values)
```

위 예시는 개념 표현입니다. 실제 생성기와 판정 함수는 테스트 대상의 타입·도메인·도구에 맞게 구현합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 실패 분석

1. 실패 입력·seed·도구 설정·코드 버전을 저장합니다.
2. 생성된 입력을 최소화하여 핵심 실패 조건을 찾습니다.
3. 속성 자체가 요구사항과 맞는지 확인합니다.
4. 테스트 코드와 제품 코드가 같은 계산을 복제하지 않았는지 검토합니다.
5. 결함 수정 후 축소된 입력과 원래 생성 조건을 재실행합니다.
6. 재현 가능한 실패는 회귀 케이스로 승격합니다.

속성 기반 테스트가 통과했다는 사실만으로 모든 입력이 검증되었다고 해석하지 않습니다. 생성 전략·속성·실행 범위를 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 속성이 요구사항·불변 조건·오류 정책과 연결됩니다.
- [ ] 예시 기반 케이스와 중복·누락 관계를 확인했습니다.
- [ ] 유효·무효·경계·빈 입력 전략이 있습니다.
- [ ] 의존 필드의 생성 제약이 정의되었습니다.
- [ ] 실패 입력·seed·설정·버전을 기록합니다.
- [ ] 실패 입력을 축소하고 재현할 수 있습니다.
- [ ] 동등 변환·참조 구현과의 차이를 구분합니다.
- [ ] 안정된 실패 사례를 회귀 테스트로 관리합니다.

## 참고 자료

- Hypothesis Documentation: [hypothesis.readthedocs.io](https://hypothesis.readthedocs.io/en/latest/) — ★★★☆☆
- [테스트 오라클](test_oracle.md)
- [경계값 분석](../01_black_box/boundary_value_analysis.md)
- [Edge Case Testing](edge_case_testing.md)

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
