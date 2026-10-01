# Jev 사용 가이드
<!-- reference: _reference/jev_official_notes.md -->

TypeSafe AI Jev를 Playground, HTTP API, Python SDK로 사용하는 방법을 정리합니다. 담당 팀 분류·영향도 평가·우회 방법 확인을 예제로 사용하며, 명령어 실행 권한이나 실제 인프라 변경은 포함하지 않습니다.

## 목차

| 섹션                                                                               |
|------------------------------------------------------------------------------------|
| [1. 준비](#1-준비) / [2. Playground](#2-playground) / [3. HTTP 호출](#3-http-호출) |
| [4. Python SDK](#4-python-sdk) / [5. 결과 분기](#5-결과-분기)                      |
| [6. 오류 대응](#6-오류-대응) / [7. 운영 검증](#7-운영-검증)                        |

---

## 1. 준비

[개념 문서](./jev_concepts.md)를 읽고 [TypeSafe 콘솔](https://console.typesafe.ai/)에서 로그인과 API 키 발급을 진행합니다. 공식 Quick start는 Python 3.10 이상을 안내합니다. 아래 실습은 Bash와 Python을 사용합니다. [Quick start](https://docs.typesafe.ai/introduction/quickstart).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install typesafe-sdk

# 키를 화면과 셸 이력에 직접 기록하지 않고 입력
read -r -s -p 'TypeSafe API key: ' TYPESAFE_API_KEY
printf '\n'
export TYPESAFE_API_KEY
```

API 호출은 계정 사용량을 소비합니다. 실습에는 비민감 예시 데이터를 사용하고, 성공한 환경은 SDK 버전을 기록해 재현합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. Playground

1. 콘솔의 Playground를 엽니다.
2. `state`에 “Several users cannot sign in after a configuration change.”를 입력합니다.
3. Noul 질문 “Does the report explicitly mention a user-facing failure?”를 추가합니다.
4. Choice·Score 질문을 추가하고 응답 필드를 비교합니다.

이는 공식 Playground 흐름에 맞춘 자체 예시입니다. Noul의 출력은 Boolean이 아닌 확률입니다. [Quick start](https://docs.typesafe.ai/introduction/quickstart), [Noul](https://docs.typesafe.ai/primitives/noul).

[⬆ 목차로 돌아가기](#목차)

## 3. HTTP 호출

필수 요청 필드는 `state`, `model`, `questions`입니다. 아래 예시는 `request.json`을 만들고 Noul 질문 하나를 전송합니다. [API reference](https://docs.typesafe.ai/api).

```bash
cat > request.json <<'JSON'
{
  "model": "jev-1.13.0",
  "state": "Several users cannot sign in after a configuration change.",
  "questions": {
    "user_impact": {
      "type": "noul",
      "instructions": "Does the report explicitly mention a user-facing failure?"
    }
  }
}
JSON

# JSON 구문을 먼저 확인
python -m json.tool request.json >/dev/null

curl --fail-with-body --silent --show-error \
  --connect-timeout 5 --max-time 30 \
  https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer ${TYPESAFE_API_KEY:?API key is required}" \
  -H 'Content-Type: application/json' \
  --data-binary @request.json \
  --output response.json
```

`response.json`의 `answers.user_impact.noul`을 읽습니다. 응답의 `model`은 실제 처리한 모델이며, `usage`는 토큰 사용량입니다. 값은 실행마다 확인하고 문서 예시를 실제 응답으로 간주하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 4. Python SDK

다음 내용을 `jev_example.py`로 저장합니다. `TypeSafeClient`와 질문 객체 사용법은 공식 SDK에 맞추고 입력·분류 기준은 자체 예시로 작성했습니다. [Python SDK](https://docs.typesafe.ai/sdk/python), [Synchronous client](https://docs.typesafe.ai/sdk/python/api/clients/sync).

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

state = {
    "service": "example-api",
    "report": "Several users cannot sign in after an application config change.",
    "workaround": "No workaround has been confirmed.",
}

questions = {
    "owner": Choice(
        instructions="Which team should investigate the reported symptom first?",
        criteria={
            "application": "Application behavior or application configuration",
            "network": "Connectivity, DNS, or network transport failures",
            "storage": "Disk, filesystem, or storage service failures",
            "unknown": "Insufficient evidence or none of the listed teams fits",
        },
    ),
    "impact": Score(
        instructions="Rate the reported user-facing impact, using explicit evidence.",
        criteria=[
            "No user-facing failure is reported",
            "Some users or features are affected",
            "The report explicitly states the entire service is unavailable",
        ],
    ),
    "has_workaround": Noul(
        instructions="Does the report describe a confirmed usable workaround?",
    ),
}

with TypeSafeClient(model="jev-1.13.0", timeout=15.0) as client:
    response = client.system_one(state=state, questions=questions)

owner = response.choices["owner"]
impact = response.scores["impact"]
workaround = response.nouls["has_workaround"]

print("model:", response.model)
print("owner:", owner.choice, "confidence:", owner.confidence)
print("owner probabilities:", owner.probabilities)
print("impact:", impact.score, "confidence:", impact.confidence)
print("confirmed workaround probability:", workaround.noul)
```

```bash
python jev_example.py
python -m pip show typesafe-sdk
```

`timeout=15.0`はHTTPタイムアウトです。再試行を含む全体の時間上限が必要なら `RetryPolicy.timeout`も設定します。 [Retries](https://docs.typesafe.ai/sdk/python/api/retries).

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분기

앞의 Python 예제에 다음 분기 코드를 추가할 수 있습니다. 0.85는 실습용 임계값이며 검증 데이터로 조정합니다. [Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing).

```python
allowed_queues = {"application", "network", "storage"}
threshold = 0.85

if owner.choice not in allowed_queues or owner.confidence < threshold:
    destination = "manual_review"
else:
    destination = owner.choice

print("suggested queue:", destination)
```

이 코드는 추천 큐만 출력합니다. 실제 큐 배정은 애플리케이션에서 별도로 구현합니다. Noul 결과는 예·아니요·검토 구간으로 나눌 수 있습니다. 낮은 `noul`은 강한 아니요이므로 낮은 신뢰도로 취급하지 않습니다. [Noul](https://docs.typesafe.ai/primitives/noul).

[⬆ 목차로 돌아가기](#목차)

## 6. 오류 대응

| 증상            | 대응                                     |
|-----------------|------------------------------------------|
| `401`           | 키와 인증 헤더 확인                      |
| `422`           | 필수 필드·질문 유형·`criteria` 형식 확인 |
| `429`           | 호출량을 줄이고 지수 백오프로 재시도     |
| `529`           | 과부하 응답에 지수 백오프 적용           |
| 낮은 신뢰도     | 상태·기준 보완 또는 검토 큐로 전달       |
| SDK import 실패 | 가상환경·패키지 설치·Python 버전 확인    |

공식 SDK는 기본 재시도 정책을 제공합니다. 재시도 대상, 횟수와 전체 예산은 실제 설치 버전의 `RetryPolicy`를 확인합니다. [API 오류](https://docs.typesafe.ai/api), [Retries](https://docs.typesafe.ai/sdk/python/api/retries).

[⬆ 목차로 돌아가기](#목차)

## 7. 운영 검증

실서비스에 적용하기 전 다음 항목을 검증합니다.

- 정상·모호·정보 부족·복합 장애·한국어 티켓을 정답과 함께 준비합니다.
- 자동 분류율, 잘못된 자동 분류율, 검토 비율, 지연과 입력 토큰을 기록합니다.
- 모델 ID, SDK 버전, 질문·기준 버전, 임계값을 함께 기록합니다.
- API 실패 시 검토 큐에 보관하고, 예외를 임의의 기본 담당 팀으로 처리하지 않습니다.
- 입력 내 지시문·모순·숫자·날짜 경계 사례를 평가합니다.

숫자 비교와 날짜 계산은 코드로 수행합니다. [알려진 한계](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

SDK의 로그는 요청·응답 본문을 가리지 않으므로 운영 로그 수준과 저장 내용을 검토합니다. [SDK logging](https://docs.typesafe.ai/sdk/python/api/clients/sync).

문서 작성 시 Python·Bash·JSON 구문과 큐 분기 경계값을 로컬에서 검증했습니다. SDK 실행과 인증된 API 호출은 수행하지 않았으며, 실제 Jev 추론의 정확도·성능은 별도로 측정해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [TypeSafe Quick start](https://docs.typesafe.ai/introduction/quickstart) — ★★★★☆
- [TypeSafe API reference](https://docs.typesafe.ai/api) — ★★★★☆
- [TypeSafe Python SDK](https://docs.typesafe.ai/sdk/python) — ★★★★☆
- [TypeSafe Models](https://docs.typesafe.ai/models) — ★★★★☆
- [Jev 개념](./jev_concepts.md)
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
