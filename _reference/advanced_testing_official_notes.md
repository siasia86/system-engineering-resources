---
name: advanced-testing-official-notes
description: Property-based Testing과 Mutation Testing의 공식 도구·개념 참조 노트.
tags:
  - advanced-testing
  - property-based-testing
  - mutation-testing
  - hypothesis
  - pit
last_checked: 2026-09-15
sources:
  - https://hypothesis.readthedocs.io/en/latest/
  - https://pitest.org/
  - https://pitest.org/quickstart/basic_concepts/
---

# Advanced Testing 공식 참조 노트

## 1. 확인 범위

Property-based Testing과 Mutation Testing의 기본 개념과 공식 도구 설명을 2026-09-15에 Hypothesis와 PIT 공식 문서 기준으로 확인했습니다.

## 2. Property-based Testing

Hypothesis 공식 문서는 속성(Property)을 만족해야 하는 테스트를 작성하고, 생성된 다양한 입력으로 속성을 검증하는 Python 라이브러리로 설명합니다. 테스트는 특정 예시 하나보다 입력 공간에서 유지되어야 하는 조건을 중심으로 작성합니다.

공식 문서에는 생성 전략·실패 입력 재현·stateful test 등의 기능이 포함됩니다. 입력 생성기와 속성은 테스트 대상의 도메인에 맞게 정의해야 하며, 모든 가능한 입력을 자동으로 증명하는 것으로 해석하지 않습니다.

## 3. Mutation Testing

PIT 공식 문서는 코드에 변형(mutant)을 주입하고 테스트를 실행하여 변형을 감지하는지 확인하는 방식으로 Mutation Testing을 설명합니다.

- 테스트가 mutant에서 실패하면 mutant가 killed 된 것으로 봅니다.
- 테스트가 mutant에서도 통과하면 mutant가 살아남은 것으로 봅니다.
- 동등 변형(equivalent mutation)은 동작 차이가 없거나 테스트 범위 밖의 변형일 수 있습니다.
- Line·statement·branch coverage는 코드 실행 여부를 보여주지만 결함 감지 능력 자체를 보장하지 않습니다.

PIT는 Java/JVM 대상의 공식 도구입니다. 다른 언어·도구에는 변형 연산자와 결과 해석이 다를 수 있으므로 동일한 수치나 동작을 일반화하지 않습니다.

## 4. 공통 검증 원칙

- 속성·변형·생성 전략의 의미를 테스트 대상의 요구사항과 연결합니다.
- 생성된 입력이나 변형 수를 테스트 품질의 절대 지표로 사용하지 않습니다.
- 실패 입력과 mutant를 재현할 수 있는 seed·코드 버전·도구 설정을 기록합니다.
- 실행 비용과 동등 변형을 고려하여 범위와 제외 기준을 명시합니다.
