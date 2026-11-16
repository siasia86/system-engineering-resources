# 에이전트 실행 관측과 감사 기록

AX 환경에서 에이전트가 무엇을 했는지 나중에 확인할 수 있도록 실행 기록·지표·감사 기록을 남기는 방법입니다. 표준 형식은 OpenTelemetry GenAI 의미 규약(semantic conventions)을 기준으로 하고, 특정 관측 제품이나 에이전트 도구에 묶이지 않는 설계만 다룹니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 무엇을 남기나](#1-무엇을-남기나) / [2. 의미 규약의 상태](#2-의미-규약의-상태)                            |
| [3. 실행 단위(span)](#3-실행-단위span) / [4. 핵심 속성](#4-핵심-속성) / [5. 지표](#5-지표)                   |
| [6. 내용 기록과 민감 정보](#6-내용-기록과-민감-정보) / [7. 감사 기록 설계](#7-감사-기록-설계)                |
| [8. 경보와 정지 조건](#8-경보와-정지-조건) / [9. 점검표](#9-점검표) / [10. 한계와 미확인](#10-한계와-미확인) |

## 1. 무엇을 남기나

에이전트 실행은 "모델 호출 → 도구 실행 → 모델 호출"이 여러 번 이어지는 흐름입니다. 결과만 남기면 실패 원인과 비용이 어디서 생겼는지 알 수 없습니다. 기록은 목적에 따라 셋으로 나눕니다.

| 종류                 | 답하는 질문                               | 보존 성격                   |
|----------------------|-------------------------------------------|-----------------------------|
| 추적(trace)          | 이 한 번의 실행이 어떤 단계를 거쳤나      | 디버깅용, 짧게 보존해도 됨  |
| 지표(metric)         | 전체적으로 얼마나 오래 걸리고 얼마나 쓰나 | 추세용, 집계값만 길게 보존  |
| 감사 기록(audit log) | 누가 언제 무엇을 승인했고 무엇이 바뀌었나 | 책임 추적용, 변조 방지 필요 |

추적과 지표는 운영 개선에, 감사 기록은 사고 조사와 책임 확인에 씁니다. 평가(eval)에서 말하는 기록(transcript)은 추적에 해당하며 [에이전트 평가 설계](agent_evaluation_design.md)의 7단계 "기록 읽기"의 재료가 됩니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 의미 규약의 상태

OpenTelemetry는 추적·지표·로그를 수집하는 공개 표준이고, 의미 규약은 "어떤 이름의 속성에 무엇을 담는지"를 정한 약속입니다. 이름을 맞춰 두면 수집 도구를 바꿔도 대시보드와 질의를 다시 쓰지 않아도 됩니다.

2026-11-16 확인 기준 상태입니다.

- GenAI 의미 규약은 OpenTelemetry 본 규약 사이트에서 별도 저장소 `open-telemetry/semantic-conventions-genai`로 옮겨졌습니다. 옛 주소(`opentelemetry.io/docs/specs/semconv/gen-ai/`)는 이동 안내만 보여 줍니다.
- 문서 상태는 Development(개발 중)입니다. 속성 이름과 의미가 바뀔 수 있습니다.
- 다루는 범위는 모델 추론 호출, 에이전트·워크플로 호출, 도구 실행, 임베딩, 검색(retrieval), MCP, 공급자별 규약(Anthropic, OpenAI, AWS Bedrock 등)입니다.

🟡 Development 단계이므로 수집기·계측 라이브러리를 올릴 때 속성 이름 변경을 확인하고, 대시보드 질의는 한곳에 모아 두어 바꾸기 쉽게 합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 실행 단위(span)

span은 추적 안의 작업 하나로, 시작·끝 시각과 속성을 가집니다. 에이전트 실행은 다음과 같은 부모·자식 구조가 됩니다.

```text
invoke_agent ops-helper                    (agent run, one user request)
 +-- chat <model>                          (inference call)
 +-- execute_tool run_shell                (tool call)
 +-- chat <model>
 +-- execute_tool tools/call search_docs   (MCP tool call)
 +-- chat <model>
```

| 작업 이름(`gen_ai.operation.name`) | 쓰는 때                                        | span 이름 형식                                   |
|------------------------------------|------------------------------------------------|--------------------------------------------------|
| `invoke_agent`                     | 모델이 도구 호출로 흐름을 정하는 에이전트 실행 | `invoke_agent {gen_ai.agent.name}`               |
| `invoke_workflow`                  | 응용이 흐름을 정하는 워크플로 실행             | `invoke_workflow {gen_ai.agent.name}`            |
| `create_agent`                     | 에이전트를 만드는 작업                         | `create_agent {gen_ai.agent.name}`               |
| `chat` 등                          | 모델 추론 호출                                 | `{gen_ai.operation.name} {gen_ai.request.model}` |
| `execute_tool`                     | 도구 실행                                      | `execute_tool {gen_ai.tool.name}`                |

`invoke_agent`와 `invoke_workflow`의 구분은 [에이전트 설계 원칙](agent_design_principles.md) 2.1절의 "자율 에이전트와 고정 흐름" 구분과 같습니다. 규약은 다른 작업 안에서 내부적으로 생기는 실행은 별도 span으로 보고하지 않고, 응용이 정의한 워크플로는 중첩돼도 보고하라고 권합니다.

MCP 호출은 별도 규약이 있어 `mcp.method.name`(예: `tools/call`)을 필수로 기록합니다. 도구 호출이면 `gen_ai.operation.name`도 함께 채워 다른 도구 호출과 같은 방식으로 볼 수 있게 하라고 권합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 핵심 속성

요구 수준(Required·Conditionally Required·Recommended·Opt-In)은 규약 표기를 따릅니다.

| 속성                         | 뜻                        | 요구 수준                       |
|------------------------------|---------------------------|---------------------------------|
| `gen_ai.operation.name`      | 작업 종류                 | Required                        |
| `gen_ai.provider.name`       | 모델 공급자               | Required(에이전트 생성·추론)    |
| `gen_ai.agent.name`          | 사람이 읽는 에이전트 이름 | Conditionally Required          |
| `gen_ai.agent.id`            | 에이전트의 고정 식별자    | Conditionally Required          |
| `gen_ai.conversation.id`     | 대화·세션 식별자          | Conditionally Required          |
| `gen_ai.request.model`       | 요청한 모델 이름          | 작업별로 다름                   |
| `gen_ai.usage.input_tokens`  | 입력 토큰 수              | Recommended(`invoke_agent`)     |
| `gen_ai.usage.output_tokens` | 출력 토큰 수              | Recommended(`invoke_agent`)     |
| `gen_ai.tool.name`           | 실행한 도구 이름          | Required(`execute_tool`)        |
| `gen_ai.tool.call.id`        | 모델이 준 도구 호출 ID    | Conditionally Required          |
| `error.type`                 | 오류 종류                 | Conditionally Required(오류 시) |
| `gen_ai.input.messages` 등   | 입력·출력 메시지 본문     | Opt-In                          |

`gen_ai.agent.name`은 값 종류가 적어야(low cardinality) 합니다. 요청마다 바뀌는 값을 넣으면 지표 집계가 무너지므로, 실행마다 다른 값은 `gen_ai.conversation.id`에 둡니다.

AX 환경에서는 표준 속성에 더해 작업 ID·저장소·branch를 사용자 정의 속성으로 붙이면 Git 이력과 추적을 이을 수 있습니다. 사용자 정의 속성은 `gen_ai.` 접두어를 쓰지 않고 조직 접두어(예: `ax.task.id`)를 씁니다. 이 접두어 규칙은 이 문서의 권장이며 규약 원문이 정한 이름이 아닙니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 지표

규약이 정한 지표 중 에이전트 운영에서 자주 볼 것입니다. 모두 Development 상태입니다.

| 지표                                                    | 종류      | 단위 | 보는 것                         |
|---------------------------------------------------------|-----------|------|---------------------------------|
| `gen_ai.invoke_agent.duration`                          | Histogram | s    | 에이전트 한 번 실행의 전체 시간 |
| `gen_ai.invoke_agent.inference_calls`                   | Histogram | 회   | 실행 한 번의 모델 호출 수       |
| `gen_ai.invoke_agent.tool_calls`                        | Histogram | 회   | 실행 한 번의 도구 호출 수       |
| `gen_ai.client.inference.duration`                      | Histogram | s    | 모델 호출 한 번의 시간          |
| `gen_ai.client.inference.usage.input_tokens`            | Counter   | 토큰 | 입력 토큰 사용량                |
| `gen_ai.client.inference.usage.output_tokens`           | Counter   | 토큰 | 출력 토큰 사용량                |
| `gen_ai.client.inference.usage.cache_read.input_tokens` | Counter   | 토큰 | 캐시에서 읽은 입력 토큰         |
| `mcp.client.operation.duration`                         | Histogram | s    | MCP 요청 한 번의 시간           |

`gen_ai.invoke_agent.duration`의 권장 버킷 경계는 0.1초부터 86400초(하루)까지로, 몇 초짜리 응답부터 하루 넘게 도는 작업까지 담도록 잡혀 있습니다.

활용 예입니다.

- 실행당 도구 호출 수 분포가 갑자기 오른쪽으로 길어지면 반복 루프나 도구 오류 재시도를 의심합니다.
- 캐시 읽기 토큰 비율이 떨어지면 지침 파일·도구 목록이 자주 바뀌어 캐시가 깨지는지 봅니다.
- 비용은 토큰 지표에 공급자 공식 가격을 곱해 별도로 계산합니다. 가격은 바뀌므로 지표에 금액을 박아 두지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 내용 기록과 민감 정보

프롬프트·응답·도구 인자·도구 결과·시스템 지침·메모리 기록은 규약상 Opt-In입니다. 규약은 이런 내용 기록을 사용자가 명시적으로 켜야 하고, 계측 도구는 내용 기록 여부와 어느 신호로 보낼지를 정하는 설정을 제공해야 한다(MUST)고 적습니다. 일부 속성에는 개인정보(PII)가 들어갈 수 있다는 경고가 붙어 있습니다.

| 선택                           | 장점                        | 위험·조건                                                                                     |
|--------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------|
| 내용 기록 끔(기본)             | 유출 위험이 낮음            | 실패 원인을 추적만으로 알기 어려움                                                            |
| 내용을 span 속성에 기록        | 한곳에서 바로 봄            | 관측 백엔드 접근자가 모두 내용을 봄                                                           |
| 외부 저장소에 두고 참조만 기록 | 접근 권한을 따로 둘 수 있음 | `*_ref` 속성(예: `gen_ai.input.messages_ref`)으로 URI만 남김, 저장소 권한·보존 기간 관리 필요 |

권장 순서입니다.

1. 운영 기본값은 내용 기록 끔으로 둡니다.
2. 평가·디버깅 환경에서만 켜고, 그 환경에는 운영 자격 증명과 실제 고객 자료를 넣지 않습니다.
3. 켜야 한다면 외부 저장소 참조 방식을 쓰고 접근 권한을 좁힙니다.
4. 수집 경로에 비밀 정보 가리기(masking)를 두고, 저장 전에 토큰·키 형태 문자열을 검사합니다.

에이전트 기록은 도구 결과에 담긴 파일 내용·환경 변수가 그대로 들어가기 쉽습니다. [에이전트 보안 위협 점검](agent_security_risks.md)의 ASI03(자격 증명)·ASI06(메모리 오염) 관점으로 보존 대상을 정합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 감사 기록 설계

추적은 표본 추출·짧은 보존을 해도 되지만, 감사 기록은 빠짐없이 남아야 합니다. 아래 필드 구성은 이 문서의 권장 예이며 표준 형식이 아닙니다.

| 필드      | 내용                                        | 예                                               |
|-----------|---------------------------------------------|--------------------------------------------------|
| 시각      | UTC 기준, 초 단위 이상                      | `2026-11-16T05:12:30Z`                           |
| 주체      | 실행을 요청한 사람, 에이전트 이름·세션 ID   | `user=<USER> agent=ops-helper`                   |
| 대상      | 호스트·저장소·branch·자원                   | `repo=infra branch=main`                         |
| 행동      | 도구 이름과 요약된 인자                     | `execute_tool run_shell systemctl restart nginx` |
| 승인      | 사람 확인 여부, 승인자, 자동 허용 규칙 이름 | `approved_by=<USER>` 또는 `rule=allow-readonly`  |
| 결과      | 성공·실패, 종료 코드, 바뀐 파일·commit SHA  | `exit=0 commit=<SHA>`                            |
| 추적 연결 | trace ID, `gen_ai.conversation.id`          | `trace=<TRACE_ID>`                               |

운영 원칙입니다.

- 되돌리기 어려운 행동(삭제, push, 배포, 권한 변경)은 승인 필드를 반드시 채웁니다.
- 감사 기록은 에이전트가 쓸 수 있는 위치와 분리해 중앙 로그 서버로 보냅니다. 에이전트가 자기 기록을 고칠 수 있으면 감사 기록이 아닙니다.
- 시스템 변경 감사는 운영체제 감사 도구(예: Linux auditd)와 함께 봅니다. 에이전트 기록은 "무엇을 의도했나", 운영체제 기록은 "실제로 무엇이 실행됐나"를 보여 줍니다.
- 저장소 작업은 commit 메시지에 작업 ID를 넣어 감사 기록·추적과 연결합니다.
- 보존 기간은 조직의 로그 보존 정책을 따르고, 내용 기록을 켠 추적보다 감사 기록을 길게 둡니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 경보와 정지 조건

관측은 사람이 보는 대시보드만이 아니라 자동 정지의 근거로 씁니다.

| 신호                                | 의심할 원인                       | 대응                                    |
|-------------------------------------|-----------------------------------|-----------------------------------------|
| 실행당 도구 호출 수가 상한 초과     | 같은 도구 반복, 정지 조건 누락    | 실행 중단, 기록 확인 뒤 정지 조건 보강  |
| 같은 도구의 `error.type` 연속 발생  | 권한 변경, 외부 서비스 장애       | 해당 도구 끄기, 의존 서비스 확인        |
| 실행 시간이 평소 분포를 크게 벗어남 | 대기·재시도 루프, 모델 응답 지연  | 시간 상한으로 중단, 공급자 상태 확인    |
| 토큰 사용량 급증                    | 큰 파일 반복 읽기, 문맥 요약 실패 | 예산 상한 설정, 문맥 관리 방식 점검     |
| 승인 없는 쓰기 행동 기록            | 허용 규칙이 넓음, 우회 경로       | 즉시 권한 축소, 감사 기록으로 범위 조사 |

상한값은 평소 분포를 몇 주 모은 뒤 정합니다. 처음부터 낮게 잡으면 정상 작업이 자주 멈추고, 높게 잡으면 잡아야 할 반복을 놓칩니다. 경보 설계 일반은 [SLO와 오류 예산](../03_engineering/reliability/slo_error_budget.md)을, 지표 수집 구성은 [Prometheus·Grafana](../02_infrastructure/monitoring/prometheus_grafana.md)를 함께 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 9. 점검표

- [ ] 추적·지표·감사 기록의 목적과 보존 기간을 나눠 정했는가
- [ ] 속성 이름을 GenAI 의미 규약에 맞추고, 사용자 정의 속성은 별도 접두어를 쓰는가
- [ ] 의미 규약이 Development 상태임을 알고 갱신 때 이름 변경을 확인하는가
- [ ] `gen_ai.agent.name`처럼 집계에 쓰는 속성의 값 종류가 적은가
- [ ] 운영 환경의 내용 기록이 기본으로 꺼져 있는가
- [ ] 내용 기록을 켠 환경에 비밀 정보 가리기와 접근 제한이 있는가
- [ ] 되돌리기 어려운 행동마다 승인 정보가 감사 기록에 남는가
- [ ] 감사 기록을 에이전트가 고칠 수 없는 곳에 보관하는가
- [ ] 도구 호출 수·시간·토큰에 상한과 경보가 있는가
- [ ] 추적 ID와 작업 ID·commit을 서로 찾을 수 있는가

[⬆ 목차로 돌아가기](#목차)

## 10. 한계와 미확인

- GenAI 의미 규약은 Development 상태라 속성 이름·요구 수준이 바뀔 수 있습니다. 이 문서는 2026-11-16 저장소 `main` 기준입니다.
- 새 저장소의 정식 배포판 번호와 날짜는 확인하지 못했습니다(GitHub 배포 목록이 비어 있었음).
- 본 규약에서 쓰이던 `OTEL_SEMCONV_STABILITY_OPT_IN` 환경 변수가 새 저장소에서 어떻게 쓰이는지 확인하지 못했습니다.
- 7절 감사 기록 필드와 4절의 사용자 정의 접두어는 이 문서의 권장이며 표준이 아닙니다.
- 에이전트 도구마다 OpenTelemetry 내보내기 지원 여부와 설정 방법이 다릅니다. 도구별 설정은 각 도구 문서를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- OpenTelemetry: [semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) — 문서 상태 Development — ★★★☆☆ (확인일 2026-11-16)
- OpenTelemetry: [GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md), [Execute tool](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/execute-tool.md), [Client inference](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/client-inference.md) — ★★★☆☆ (확인일 2026-11-16)
- OpenTelemetry: [GenAI metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md), [GenAI token metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-token-metrics.md), [GenAI spans(내용 기록 설정)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md), [MCP](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md) — ★★★☆☆ (확인일 2026-11-16)
- OpenTelemetry: [Document status](https://opentelemetry.io/docs/specs/otel/document-status/) — ★★★☆☆ (확인일 2026-11-16)
- [에이전트 평가 설계](agent_evaluation_design.md), [MCP 서버 도입·운영 점검](mcp_server_adoption_checklist.md), [에이전트 보안 위협 점검](agent_security_risks.md)

[⬆ 07 README로 돌아가기](README.md)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
