# Jev 개념
<!-- reference: _reference/jev_official_notes.md -->

TypeSafe AI의 Jev가 제공하는 구조화된 판단, 질문 유형과 애플리케이션의 역할을 정리합니다. 입력 상태에서 담당 팀·영향도·명제의 참 여부를 판단하는 시스템을 설계하는 독자를 대상으로 합니다.

## 목차

| 섹션                                                                |
|---------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 상태와 질문](#2-상태와-질문)               |
| [3. 질문 유형](#3-질문-유형) / [4. 확률과 신뢰도](#4-확률과-신뢰도) |
| [5. 시스템 구성](#5-시스템-구성) / [6. 한계와 평가](#6-한계와-평가) |

---

## 1. 개요

Jev는 TypeSafe AI가 System One 모델로 소개한 판단 모델입니다. 상태와 형식이 지정된 질문을 받아 코드에서 사용할 선택·점수·확률을 반환합니다. 여러 질문은 같은 상태에 대해 독립적으로 평가됩니다. [공식 소개](https://docs.typesafe.ai/introduction).

| 구성 요소         | 역할                              |
|-------------------|-----------------------------------|
| Jev               | 입력에 대한 제한된 의미 판단      |
| 생성형 LLM        | 설명·코드·문장 생성과 복잡한 계획 |
| 애플리케이션 코드 | 계산·입력 검증·분기·실행·기록     |

Jev 자체는 대화나 파일 편집을 수행하지 않습니다. 코딩 에이전트의 기본 모델 교체와 앱 내부의 Jev API 연동은 다른 작업입니다. [코딩 에이전트와 Jev](https://docs.typesafe.ai/introduction/coding-agents).

[⬆ 목차로 돌아가기](#목차)

## 2. 상태와 질문

**State**는 판단할 메시지·기록·애플리케이션 상태입니다. **Instructions**는 무엇을 판단할지 정의하며, **Criteria**는 선택지나 평가 수준의 의미를 지정합니다. [State](https://docs.typesafe.ai/concepts/state).

예를 들어 장애 티켓에는 다음 정보를 전달할 수 있습니다. 아래 구조는 이 문서의 설계 예시입니다.

```json
{
  "service": "example-api",
  "symptom": "Requests fail after the latest configuration change.",
  "impact": "Several customers cannot sign in.",
  "workaround": "No workaround has been confirmed."
}
```

이 상태에 대해 담당 팀, 사용자 영향 수준, 우회 방법의 언급 여부를 각각 질문합니다. 정확한 실패율 계산은 원본 메트릭을 처리하는 코드에서 수행합니다.

앞 질문의 답이 다음 질문의 입력이어야 한다면 호출을 나누고 코드에서 상태를 갱신합니다. 같은 요청의 질문들이 서로의 답을 순차적으로 읽는다고 가정하지 않습니다. [공식 소개](https://docs.typesafe.ai/introduction).

[⬆ 목차로 돌아가기](#목차)

## 3. 질문 유형

### 3.1 Choice

담당 팀처럼 순서가 없는 선택지에 사용합니다. `criteria`는 선택지 ID와 설명을 연결하는 객체입니다. 응답은 선택 ID, 선택지별 확률, 신뢰도를 포함합니다. [Choice](https://docs.typesafe.ai/primitives/choice).

`network`, `application`, `storage`, `unknown`을 정의하면 코드가 선택 ID를 처리할 수 있습니다. `unknown`의 의미에는 정보 부족과 어느 선택지에도 해당하지 않는 경우를 명시합니다.

### 3.2 Score

영향도처럼 낮은 수준에서 높은 수준으로 정렬할 수 있는 판단에 사용합니다. `criteria` 배열의 위치가 0부터 시작하는 수준 번호입니다. [Score](https://docs.typesafe.ai/primitives/score).

3개 수준의 확률이 각각 0.1, 0.6, 0.3이면 다음과 같습니다.

```text
score = 0 * 0.1 + 1 * 0.6 + 2 * 0.3 = 1.2
```

이 점수는 정의한 수준에 대한 평가값입니다. 1.2라는 값을 장애 시간이나 실패율의 실측값으로 해석하지 않습니다.

### 3.3 Noul

예/아니요로 판단할 명제에 사용합니다. `noul`은 예일 확률이며, 0에 가까우면 아니요, 1에 가까우면 예, 0.5 부근이면 불확실한 판단입니다. 별도의 `confidence`는 없습니다. [Noul](https://docs.typesafe.ai/primitives/noul).

“우회 방법이 명시돼 있는가?”와 “사용자 영향이 명시돼 있는가?”를 분리하면 각 결과를 코드에서 조합할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 확률과 신뢰도

`probabilities`는 선택지 또는 수준별 확률 분포입니다. Choice·Score의 `confidence`는 그 분포를 요약한 0~1 값이며, 선택된 항목의 확률과 구분합니다. [Confidence](https://docs.typesafe.ai/confidence).

애플리케이션은 결과와 신뢰도를 함께 사용해 자동 분류, 추가 정보 요청, 담당자 검토를 선택할 수 있습니다. [Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing).

임계값은 오류 비용과 검증 데이터에 맞춰 결정합니다. 예를 들어 `confidence >= 0.85`를 자동 분류 기준으로 사용하더라도 이는 애플리케이션의 예시 정책이며 공식 정확도 보장이 아닙니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 시스템 구성

다음은 장애 티켓 분류를 위한 설계 예시입니다.

```text
Ticket -> Input validation -> Jev evaluation -> Routing policy -> Queue
```

- 입력 검증: 비어 있는 티켓 처리, 필요한 필드 구성, 민감 정보 제거.
- Jev 평가: 담당 영역 Choice, 영향 수준 Score, 우회 방법 Noul.
- 분기 정책: 낮은 신뢰도·`unknown`·API 실패는 검토 큐로 전달.
- 실행: 큐 배정은 코드가 수행하고 결과를 감사 가능한 형태로 기록.

분류 결과를 서버 재시작 명령으로 직접 연결하기보다 담당 큐 배정부터 평가할 수 있습니다. 모델의 높은 신뢰도와 실행 권한은 별도의 조건입니다.

관련 설계는 [Harness Engineering](./harness_engineering.md), [장애 대응](../../03_engineering/reliability/incident_management.md)을 참고합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 한계와 평가

공식 Jev 1.13 한계 문서는 수치 계산·날짜 비교·간접 참조·적대적 입력을 주의 대상으로 설명합니다. 문장 생성은 생성형 모델을 사용하고, 정확한 계산과 정책 불변조건은 코드로 구현합니다. [알려진 한계](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

한국어 티켓, 축약어, 정보 부족, 서로 모순되는 내용, 입력 내 지시문을 포함한 사례를 평가합니다. 자동 분류 비율과 잘못된 자동 분류 비율을 함께 측정하면 신뢰도 임계값을 조정할 수 있습니다.

실습은 [Jev 사용 가이드](./jev_guide.md), 확인된 공식 계약은 [참조 노트](../../_reference/jev_official_notes.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [TypeSafe Introduction](https://docs.typesafe.ai/introduction) — ★★★★☆
- [TypeSafe Primitives](https://docs.typesafe.ai/primitives) — ★★★★☆
- [TypeSafe Confidence](https://docs.typesafe.ai/confidence) — ★★★★☆
- [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13) — ★★★★☆
- [Jev 공식 참조 노트](../../_reference/jev_official_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-01

**마지막 업데이트**: 2026-10-01

© 2026 siasia86. Licensed under CC BY 4.0.
