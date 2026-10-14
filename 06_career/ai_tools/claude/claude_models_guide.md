# Claude 모델 선택 가이드
<!-- reference: _reference/claude_code_official_notes.md -->

Anthropic Claude 모델의 현재 라인업, 가격, 선택 기준과 Claude Code에서 모델·effort를 지정하는 방법을 정리합니다. 수치는 2026-10-14 공식 문서 기준이며, 가격과 제공 모델은 자주 바뀌므로 사용 전 공식 문서를 확인합니다.

## 목차

| 섹션                                                                                              |
|---------------------------------------------------------------------------------------------------|
| [1. 현재 라인업](#1-현재-라인업) / [2. 가격과 비용 요소](#2-가격과-비용-요소)                     |
| [3. 작업별 선택](#3-작업별-선택) / [4. Claude Code에서 지정](#4-claude-code에서-지정)             |
| [5. 제공자별 모델 ID](#5-제공자별-모델-id) / [6. 이전 모델과 폐기 일정](#6-이전-모델과-폐기-일정) |

---

## 1. 현재 라인업

| 모델              | 성격                                        | 지연      | 컨텍스트 | 최대 출력 | 기본 effort |
|-------------------|---------------------------------------------|-----------|----------|-----------|-------------|
| Claude Fable 5.1  | 가장 높은 성능, 어려운 추론·장시간 에이전트 | 느림      | 1M       | 128K      | `high`      |
| Claude Opus 5.5   | 장시간 에이전트 코딩·지식 작업 (기본 권장)  | 보통      | 1M       | 128K      | `medium`    |
| Claude Sonnet 5.5 | 속도와 성능의 균형                          | 빠름      | 1M       | 128K      | `high`      |
| Claude Haiku 5.5  | 대량·저지연 처리 (분류, 추출, 라우팅)       | 가장 빠름 | 1M       | 128K      | `medium`    |

- 공식 권장: 대부분의 작업은 **Opus 5.5**로 시작하고, `xhigh`·`max` effort로도 부족한 어려운 추론·장시간 작업만 **Fable 5.1**로 올립니다.
- 네 모델 모두 adaptive thinking(모델이 생각할 양을 스스로 정함)을 사용하며, 지식 기준일은 2026년 6월입니다.
- Claude Mythos 5.1·5는 제한 제공 모델로 일반 라인업에는 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 가격과 비용 요소

API 종량제 가격(1M 토큰당)입니다. 구독(Pro·Max 등)으로 Claude Code를 쓰면 토큰 요금 대신 플랜 사용량 한도가 적용됩니다.

| 모델              | 입력  | 출력  | 캐시 읽기 |
|-------------------|-------|-------|-----------|
| Claude Fable 5.1  | $10   | $50   | $0.25     |
| Claude Opus 5.5   | $4    | $20   | $0.20     |
| Claude Sonnet 5.5 | $2    | $10   | $0.10     |
| Claude Haiku 5.5  | $0.10 | $0.50 | $0.01     |

- Haiku 5.5는 프롬프트가 100,000 토큰을 넘으면 입력 $0.50, 출력 $2.50으로 올라갑니다.
- Batch API는 50% 할인됩니다.
- 4.7 세대 이후 tokenizer는 같은 텍스트에서 이전보다 약 30% 많은 토큰을 만듭니다. 이전 모델과 비용을 비교할 때 단가만 보지 않습니다.
- 모델을 바꾸기 전에 effort를 조정하는 것이 비용·속도 조절에 더 효과적인 경우가 많습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 작업별 선택

| 작업                                          | 권장 모델  | effort   |
|-----------------------------------------------|------------|----------|
| 일반 기능 구현, 버그 수정                     | Opus 5.5   | `medium` |
| 대규모 리팩토링, 장애 근본 원인 분석          | Opus 5.5   | `high`   |
| 수 시간 걸리는 자율 작업, 깊은 조사·분석 문서 | Fable 5.1  | `high`   |
| 스크립트 작성, 문서 작성, 일상 코딩           | Sonnet 5.5 | `medium` |
| 이름 변경 같은 작은 수정, 빠른 질문           | Sonnet 5.5 | `low`    |
| 로그 분류·추출, subagent의 단순 탐색          | Haiku 5.5  | `low`    |
| CI에서 대량 반복 처리                         | Haiku 5.5  | `medium` |

🟡 위 표는 공식 모델 선택 기준(Opus 5.5 기본, Fable 5.1은 상위 단계, Haiku 5.5는 저지연·대량 처리)과 effort 설명을 바탕으로 정리한 이 문서의 권장 출발점입니다. 실제 선택은 자기 작업으로 비교해 정합니다.

- 설계는 강한 모델로, 실행은 빠른 모델로 나누려면 Claude Code의 `opusplan` 별칭을 씁니다(plan 모드는 Opus, 실행은 Sonnet).
- subagent마다 `model`을 지정하면 탐색은 Haiku, 리뷰는 Opus처럼 나눠 쓸 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Claude Code에서 지정

### 별칭

| 별칭       | 의미                                       |
|------------|--------------------------------------------|
| `default`  | 계정의 기본 모델로 되돌림                  |
| `best`     | 사용 가능하면 Fable, 아니면 Opus           |
| `fable`    | Fable 모델                                 |
| `opus`     | 최신 Opus (Anthropic API에서 Opus 5.5)     |
| `sonnet`   | 최신 Sonnet (Anthropic API에서 Sonnet 5.5) |
| `haiku`    | Haiku (Anthropic API에서 Haiku 5.5)        |
| `opusplan` | plan 모드는 Opus, 실행은 Sonnet            |

### 지정 방법

```bash
# 시작 시 지정
claude --model opus
claude --model claude-sonnet-5-5

# 세션 중 변경 (effort는 좌우 화살표로 조정)
/model sonnet
```

```json
{
  "model": "opus"
}
```

- 별칭이 가리키는 모델은 제공자마다 다릅니다. Bedrock·Google Cloud에서는 `sonnet`이 Sonnet 4.5, `haiku`가 Haiku 4.5를 가리킵니다. 특정 모델을 고정하려면 `ANTHROPIC_DEFAULT_OPUS_MODEL`·`ANTHROPIC_DEFAULT_SONNET_MODEL` 등 환경 변수나 전체 모델 ID를 사용합니다.
- effort 단계: Fable·Opus 5.5·Sonnet 5.5·Haiku 5.5는 `low`·`medium`·`high`·`xhigh`·`max`, Opus 4.6·Sonnet 4.6은 `xhigh`가 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 제공자별 모델 ID

| 제공자                 | Opus 5.5 ID                 | 형식                |
|------------------------|-----------------------------|---------------------|
| Claude API             | `claude-opus-5-5`           | 날짜 없는 ID        |
| Amazon Bedrock         | `anthropic.claude-opus-5-5` | `anthropic.` 접두사 |
| Google Cloud           | `claude-opus-5-5`           | API ID와 같음       |
| Microsoft Foundry      | `claude-opus-5-5`           | 배포 이름으로 호출  |
| Claude Platform on AWS | `claude-opus-5-5`           | API ID와 같음       |

- 4.6 세대부터는 날짜 없는 ID 자체가 고정 스냅샷입니다. 이전 모델은 별칭이 날짜 붙은 ID(예: `claude-sonnet-4-5-20250929`)를 가리킵니다.
- Bedrock·Google Cloud는 리전과 엔드포인트(global, regional)에 따라 제공 여부와 폐기 일정이 다를 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 이전 모델과 폐기 일정

| 모델                       | 상태                                             | 대체 모델             |
|----------------------------|--------------------------------------------------|-----------------------|
| Fable 5, Opus 5, Sonnet 5  | 사용 가능 (legacy)                               | 5.5·5.1 세대          |
| Opus 4.8·4.7·4.6·4.5       | 사용 가능 (legacy)                               | Opus 5.5              |
| Sonnet 4.6, Haiku 4.5      | 사용 가능 (legacy)                               | Sonnet 5.5, Haiku 5.5 |
| Sonnet 4.5                 | 폐기 예고, 2026-11-30 Claude API 종료            | Sonnet 5.5            |
| Sonnet 4, Opus 4, Opus 4.1 | Claude API 종료 (Bedrock·Google Cloud 일부 예외) | 5.5 세대              |

- Anthropic은 현행 모델의 종료를 최소 2027년 9월 이후로 약속하고 있습니다(Fable 5.1 2027-09-01, Opus 5.5 2027-09-22, Sonnet 5.5 2027-09-28, Haiku 5.5 2027-10-07 이후).
- 스크립트·CI에 모델 ID를 고정했다면 폐기 일정 페이지를 주기적으로 확인합니다.
- Kiro 등 다른 도구에서 Claude 모델을 쓸 때는 그 도구가 제공하는 모델 목록과 이름을 따릅니다. 예: [Kiro 모델 가이드](../kiro/kiro_model_guide.md).

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 모델·가격 검증 근거 노트
- Models overview: [platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview) — ★★★☆☆
- Choosing a model: [platform.claude.com/docs/en/about-claude/models/choosing-a-model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) — ★★★☆☆
- Pricing: [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing) — ★★★☆☆
- Model deprecations: [platform.claude.com/docs/en/about-claude/model-deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) — ★★★☆☆
- Claude Code model configuration: [code.claude.com/docs/en/model-config](https://code.claude.com/docs/en/model-config) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-14

**마지막 업데이트**: 2026-10-14

© 2026 siasia86. Licensed under CC BY 4.0.
