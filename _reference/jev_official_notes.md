---
name: jev-official-notes
description: TypeSafe AI Jev의 질문 유형, API, Python SDK, 모델 제한과 운영 기준 공식 참조 노트
tags:
  - ai-tools
  - jev
  - typesafe-ai
  - system-one
  - decision-model
last_checked: 2026-10-01
sources:
  - https://docs.typesafe.ai/introduction
  - https://docs.typesafe.ai/introduction/coding-agents
  - https://docs.typesafe.ai/introduction/quickstart
  - https://docs.typesafe.ai/concepts/state
  - https://docs.typesafe.ai/primitives/choice
  - https://docs.typesafe.ai/primitives/score
  - https://docs.typesafe.ai/primitives/noul
  - https://docs.typesafe.ai/confidence
  - https://docs.typesafe.ai/models
  - https://docs.typesafe.ai/api
  - https://docs.typesafe.ai/sdk/python
  - https://docs.typesafe.ai/sdk/python/api/clients/sync
  - https://docs.typesafe.ai/sdk/python/api/retries
  - https://docs.typesafe.ai/model-jaggedness/jev-1.13
---

# Jev 공식 참조 노트

## 1. 확인 범위

2026-10-01에 TypeSafe AI의 공식 문서를 확인했습니다. Jev는 입력 상태에 대한 구조화된 판단을 반환하는 System One 모델입니다. 자유로운 문장 생성과 코드 편집은 제공하지 않으며, 애플리케이션이 판단 결과를 받아 후속 동작을 수행합니다. [Introduction](https://docs.typesafe.ai/introduction), [Coding agents](https://docs.typesafe.ai/introduction/coding-agents).

본문 문서 2개가 이 참조 노트를 공통으로 사용합니다.

- [Jev 개념](../06_career/ai_tools/jev_concepts.md)
- [Jev 사용 가이드](../06_career/ai_tools/jev_guide.md)

## 2. 모델과 제공 조건

다음 값은 확인일의 공식 모델 페이지 기준입니다. 가격·별칭·제한은 변경될 수 있습니다. [Models](https://docs.typesafe.ai/models).

| 항목           | 확인 결과                                         |
|----------------|---------------------------------------------------|
| 버전 ID        | `jev-1.13.0`                                      |
| 별칭           | `jev-latest`, `jev-preview` 모두 위 버전을 가리킴 |
| 입력 가격      | 100만 입력 토큰당 USD 0.042                       |
| 출력 가격      | 출력 토큰 무료                                    |
| 전체 요청 길이 | `state`와 모든 질문을 합쳐 64k 토큰               |
| 개별 질문 길이 | `state`와 가장 긴 질문을 합쳐 32k 토큰            |
| 입력 매체      | 텍스트; 이미지·음성·영상 직접 입력 미지원         |

속도 제한은 공식 문서에서도 유동적인 값으로 설명하므로 배포 시 재확인합니다. 별칭 대신 버전 ID를 지정하면 모델 변경에 따른 회귀 평가 시점을 관리할 수 있습니다.

## 3. 질문과 응답

| 유형   | 판단                       | 응답 필드                                        | 공식 출처                                            |
|--------|----------------------------|--------------------------------------------------|------------------------------------------------------|
| Choice | 정의한 선택지 중 하나 선택 | `choice`, `probabilities`, `confidence`          | [Choice](https://docs.typesafe.ai/primitives/choice) |
| Score  | 순서가 있는 수준별 평가    | `score`, `legend`, `probabilities`, `confidence` | [Score](https://docs.typesafe.ai/primitives/score)   |
| Noul   | 명제가 참인지 평가         | `noul`                                           | [Noul](https://docs.typesafe.ai/primitives/noul)     |

Score 수준은 0부터 시작합니다. `score`는 수준 인덱스의 확률 가중 평균이므로 소수일 수 있습니다. Noul은 참일 확률을 0~1로 반환하며 별도의 `confidence`가 없습니다.

Choice와 Score의 `confidence`는 확률 분포에서 계산한 요약값입니다. 선택된 항목의 확률과 동일한 값으로 취급하지 않습니다. [Confidence](https://docs.typesafe.ai/confidence).

## 4. HTTP와 SDK 계약

- 평가: `POST https://api.typesafe.ai/v1/systemone`.
- 인증: `Authorization: Bearer <API_KEY>`.
- 요청: `state`, `model`, `questions`.
- 응답: `model`, `answers`, `usage`; 질문 ID와 응답 ID가 대응합니다.
- 오류: `401` 인증, `422` 요청 검증, `429` 속도 제한, `529` 과부하.

출처: [API reference](https://docs.typesafe.ai/api).

Python Quick start는 Python 3.10 이상과 `typesafe-sdk` 패키지를 안내합니다. `TypeSafeClient`는 환경 변수 `TYPESAFE_API_KEY`를 읽으며 `Choice`, `Score`, `Noul` 객체를 사용할 수 있습니다. [Quick start](https://docs.typesafe.ai/introduction/quickstart), [Python SDK](https://docs.typesafe.ai/sdk/python).

HTTP 요청 타임아웃과 전체 재시도 시간 예산은 구분합니다. `RetryPolicy.timeout`은 재시도 대기까지 포함하는 호출 예산입니다. SDK 로그는 비밀 헤더를 가리지만 요청·응답 본문은 가리지 않습니다. [Synchronous client](https://docs.typesafe.ai/sdk/python/api/clients/sync), [Retries](https://docs.typesafe.ai/sdk/python/api/retries).

## 5. 입력과 알려진 한계

`state`는 문자열, JSON 객체 또는 배열로 구성합니다. 질문별로 필요한 사실을 명시하고 관련 없는 긴 로그는 줄입니다. 공식 문서는 영어 중심 학습과 다른 언어의 정확도 차이를 설명하므로 한국어 입력을 별도로 평가합니다. [State](https://docs.typesafe.ai/concepts/state).

Jev 1.13의 알려진 한계에는 문자 그대로의 해석, 수치 계산, 날짜 비교, 복잡한 간접 참조, 불필요하게 큰 상태, 적대적 입력이 있습니다. 계산·정렬·권한 검증은 코드에서 처리하고 모델에는 의미 판단을 맡깁니다. [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

## 6. 검증 기록

- 1차 대조: Introduction·질문별 문서·State를 기준으로 모델 역할과 응답 의미 확인.
- 2차 대조: API·Models·Python SDK를 기준으로 필드명, 버전 ID, 호출 예제와 제한 확인.
- 로컬 검증: Python·Bash·JSON 구문, 큐 분기 경계값 확인.
- SDK 실행과 인증된 API 호출은 수행하지 않았습니다. 실측 정확도·지연·비용은 별도로 검증합니다.
