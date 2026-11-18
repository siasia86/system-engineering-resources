# MCP(Model Context Protocol) 개념과 운영 점검

MCP는 AI 애플리케이션이 외부 데이터와 도구에 연결하는 방식을 표준화한 공개 프로토콜입니다. 이 문서는 특정 도구의 설정 방법이 아니라, 시스템 엔지니어가 MCP 서버를 도입·운영·검토할 때 알아야 할 구조, 전송 방식, 인증, 보안 점검 항목을 공식 사양 기준으로 정리합니다. 도구별 등록 명령은 [Claude Code 확장 기능](./claude/claude_code_extensions_guide.md#7-mcp)과 각 도구 문서를 참고합니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요와 판 번호](#1-개요와-판-번호) / [2. 구성 요소](#2-구성-요소) / [3. 기능 단위](#3-기능-단위)         |
| [4. 전송 방식](#4-전송-방식) / [5. 인증과 권한](#5-인증과-권한) / [6. 보안 위협과 대응](#6-보안-위협과-대응) |
| [7. 점검과 디버깅](#7-점검과-디버깅) / [8. 도입 점검표](#8-도입-점검표)                                      |

---

## 1. 개요와 판 번호

MCP는 [JSON-RPC 2.0](https://www.jsonrpc.org/specification) 메시지로 통신합니다. JSON-RPC는 `method`·`params`·`id`를 담은 JSON 객체로 원격 호출을 표현하는 가벼운 규약입니다. 사양은 언어 서버 프로토콜(LSP, 편집기와 언어 분석기를 잇는 규약)에서 영향을 받았다고 밝히며, 여러 AI 애플리케이션이 같은 서버를 재사용할 수 있게 하는 것이 목적입니다.

사양은 날짜 형식의 판 번호를 씁니다. 2026-11-16 확인 기준 최신 판은 `2026-07-28`이고, 직전 판은 `2025-11-25`입니다.

| 판           | 주요 특징                                                               |
|--------------|-------------------------------------------------------------------------|
| `2024-11-05` | 첫 공개 판, HTTP+SSE 전송                                               |
| `2025-03-26` | Streamable HTTP 도입, HTTP+SSE는 폐기 예정으로 전환                     |
| `2025-11-25` | `initialize` 핸드셰이크와 `Mcp-Session-Id` 세션을 쓰는 마지막 판        |
| `2026-07-28` | 상태 없는(stateless) 구조, `server/discover` 추가, 세션·GET 스트림 제거 |

`2026-07-28` 판의 핵심 변화는 다음과 같습니다(공식 changelog 기준).

- 연결 단위 세션과 `initialize`/`notifications/initialized` 핸드셰이크를 없애고, 모든 요청의 `_meta`에 프로토콜 판과 클라이언트 기능을 싣습니다.
- 서버는 `server/discover`를 구현해야 하며, 클라이언트는 이를 호출해 지원 판과 기능을 먼저 확인할 수 있습니다.
- 서버가 클라이언트에게 먼저 요청을 보내던 방식(`sampling/createMessage`, `elicitation/create`, `roots/list`)을 MRTR(Multi Round-Trip Requests)로 바꿨습니다. 서버는 `resultType: "input_required"` 결과를 돌려주고, 클라이언트는 필요한 응답을 붙여 원래 요청을 다시 보냅니다.
- Roots·Sampling·Logging 기능은 폐기 예정(Deprecated)으로 분류되었고, 동적 클라이언트 등록(RFC 7591)도 폐기 예정으로 바뀌었습니다.

🟡 주의: 사용 중인 클라이언트·서버·SDK가 어느 판을 구현했는지는 제품마다 다르며, 이 문서는 개별 제품의 지원 판을 확인하지 않았습니다(미확인). 이전 판과 상호 운용하는 방법은 사양의 Backward Compatibility 절에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 구성 요소

MCP는 세 역할로 나뉩니다.

| 역할   | 설명                                                 | 예                              |
|--------|------------------------------------------------------|---------------------------------|
| Host   | 사용자가 쓰는 LLM 애플리케이션, 연결을 시작하는 쪽   | AI 코딩 도구, 채팅 앱, IDE      |
| Client | Host 안에서 서버 하나와 통신하는 연결 담당 구성 요소 | Host가 서버마다 하나씩 생성     |
| Server | 데이터와 기능을 제공하는 프로그램                    | 파일 조회, 이슈 트래커, DB 조회 |

```text
+-----------------------------+
| Host (LLM application)      |
|  +---------+  +---------+   |
|  | Client  |  | Client  |   |
|  +----+----+  +----+----+   |
+-------|------------|--------+
        | stdio      | Streamable HTTP
        v            v
  +-----------+  +------------------+
  | Server A  |  | Server B         |
  | (local    |  | (remote, behind  |
  |  process) |  |  OAuth)          |
  +-----------+  +------------------+
```

운영 관점에서 기억할 점은 다음과 같습니다.

- 로컬 서버는 Host와 같은 사용자 권한으로 실행됩니다. 서버가 읽을 수 있는 파일과 네트워크 범위가 곧 노출 범위입니다.
- 원격 서버는 일반 웹 서비스와 같은 방식으로 인증·로깅·속도 제한을 설계해야 합니다.
- 한 Host가 여러 서버에 연결하면 도구 이름이 겹칠 수 있습니다. 사양은 서버 식별자를 접두사로 붙이는 식의 구분 전략을 권합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기능 단위

서버가 제공하는 기능은 세 가지입니다.

| 기능      | 누가 쓰는가                          | 용도                              | 대표 메서드                        |
|-----------|--------------------------------------|-----------------------------------|------------------------------------|
| Tools     | 모델이 판단해 호출(model-controlled) | 외부 시스템 조회·변경 실행        | `tools/list`, `tools/call`         |
| Resources | 사용자 또는 모델이 참조              | 파일·문서·레코드 같은 읽기용 맥락 | `resources/list`, `resources/read` |
| Prompts   | 사용자가 골라 실행                   | 정해진 형식의 메시지·작업 흐름 틀 | `prompts/list`, `prompts/get`      |

클라이언트가 서버에 제공하는 기능으로는 Elicitation(서버가 사용자에게 추가 입력을 요청)이 있습니다. Sampling·Roots는 `2026-07-28`에서 폐기 예정입니다.

### 도구 정의 구조

도구는 `name`, `description`, `inputSchema`(JSON Schema), 선택 항목 `outputSchema`·`annotations`로 정의합니다. 매개변수가 없는 도구는 `{"type": "object", "additionalProperties": false}`를 권장합니다.

```json
{
  "name": "get_disk_usage",
  "description": "Return disk usage for a mount point (read only)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "mount": { "type": "string", "description": "Mount point such as /var" }
    },
    "required": ["mount"],
    "additionalProperties": false
  }
}
```

### 오류의 두 종류

| 종류           | 표현 방식                 | 예                               |
|----------------|---------------------------|----------------------------------|
| 프로토콜 오류  | JSON-RPC `error` 객체     | 없는 도구 이름, 형식이 틀린 요청 |
| 도구 실행 오류 | 결과 안의 `isError: true` | 외부 API 실패, 입력값 범위 초과  |

도구 실행 오류는 모델이 읽고 매개변수를 고쳐 다시 시도할 수 있도록 구체적인 문장으로 돌려주는 것이 좋습니다.

🟡 주의: `annotations`(예: 읽기 전용 여부를 알리는 힌트)는 서버가 스스로 적는 설명입니다. 사양은 신뢰할 수 있는 서버가 아니면 annotations를 신뢰하지 말라고 요구합니다. 승인 정책을 annotations에만 기대지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 전송 방식

표준 전송은 두 가지입니다.

| 항목        | stdio                                    | Streamable HTTP                              |
|-------------|------------------------------------------|----------------------------------------------|
| 실행 형태   | 클라이언트가 서버를 하위 프로세스로 실행 | 서버가 독립 프로세스로 여러 클라이언트 처리  |
| 메시지 경계 | 줄바꿈 하나에 메시지 하나                | 요청마다 HTTP POST 하나                      |
| 응답        | 같은 stdout 채널                         | `application/json` 또는 요청 단위 SSE 스트림 |
| 인증        | 환경 변수 등에서 자격증명을 읽음         | OAuth 기반 인증 사양 적용 권장               |
| 주 용도     | 개인 PC의 로컬 도구                      | 팀 공용·원격 서비스                          |

SSE(Server-Sent Events)는 HTTP 응답을 열어 둔 채 서버가 이벤트를 이어서 보내는 방식입니다.

### stdio 규칙

- 서버는 stdin에서 메시지를 읽고 stdout에 메시지를 씁니다. 메시지 안에 줄바꿈이 들어가면 안 됩니다.
- 서버는 stdout에 유효한 MCP 메시지 외에는 아무것도 쓰면 안 됩니다. 로그는 stderr로 보냅니다.
- 종료는 클라이언트가 stdin을 닫고 기다린 뒤, 응답이 없으면 SIGTERM, 그다음 SIGKILL 순서로 진행합니다.

운영에서 자주 보는 장애는 서버 프로그램이 시작 메시지나 디버그 출력을 stdout에 찍어 클라이언트가 메시지를 해석하지 못하는 경우입니다. 직접 만든 서버라면 로그 출력 대상부터 확인합니다.

```bash
# 서버가 stdout에 MCP 메시지 외 문자열을 찍는지 빠르게 확인하는 예
# (실제 서버 실행 명령으로 바꾸어 사용, 3초 뒤 종료)
timeout 3 ./my-mcp-server < /dev/null 2>/dev/null | head -c 500
```

출력이 비어 있거나 JSON 한 줄씩만 보이면 정상 범위입니다. 사람이 읽는 문장이 보이면 stderr로 옮겨야 합니다.

### Streamable HTTP 규칙

- 서버는 POST를 받는 단일 엔드포인트(예: `https://example.com/mcp`)를 둡니다.
- 클라이언트는 `Accept: application/json, text/event-stream`과 `MCP-Protocol-Version` 헤더를 보내야 하며, `2026-07-28` 판에서는 `Mcp-Method`와(도구 호출 등에서) `Mcp-Name` 헤더도 필요합니다.
- 헤더 값과 본문 값이 다르면 서버는 `400 Bad Request`와 `HeaderMismatch`(`-32020`) 오류로 거부해야 합니다. 로드밸런서는 헤더로, 서버는 본문으로 판단하는 불일치를 막기 위한 규칙입니다.
- 서버는 모든 연결에서 `Origin` 헤더를 검증해야 하고, 잘못된 값이면 403으로 응답해야 합니다. DNS 리바인딩(DNS rebinding, 외부 웹 페이지가 DNS 응답을 바꿔 사용자 PC의 로컬 서버에 접근하는 공격)을 막기 위해서입니다.
- 로컬에서 실행할 때는 `0.0.0.0`이 아니라 `127.0.0.1`에만 바인딩하는 것이 권장됩니다.

리버스 프록시 뒤에 둘 때는 SSE 버퍼링을 끕니다. 사양은 서버가 SSE 응답에 `X-Accel-Buffering: no`를 넣도록 권합니다. nginx에서 직접 설정한다면 다음과 같습니다.

```nginx
location /mcp {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_read_timeout 1h;
}
```

`proxy_read_timeout`은 오래 열려 있는 알림 스트림을 고려한 예시 값입니다. 실제 값은 서비스 특성에 맞춰 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 인증과 권한

인증은 사양상 선택 사항이지만, 원격 서버라면 사실상 필요합니다.

- HTTP 전송은 인증 사양을 따르는 것이 권장되고, stdio 전송은 이 사양 대신 환경에서 자격증명을 읽습니다.
- MCP 서버는 OAuth 2.1의 리소스 서버(resource server, 토큰을 받아 요청을 처리하는 쪽) 역할을 합니다.
- 서버는 [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728) Protected Resource Metadata를 구현해 어느 인가 서버를 쓰는지 알려야 합니다.
- 클라이언트는 [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html) `resource` 매개변수로 토큰을 쓸 대상 서버를 명시해야 하고, PKCE를 사용합니다.
- 토큰은 `Authorization: Bearer <access-token>` 헤더로만 보내고 URL 쿼리에 넣지 않습니다.
- 서버는 토큰이 자기 자신을 대상으로 발급되었는지(audience) 검증해야 하며, 다른 서비스용 토큰을 받거나 그대로 하위 API에 넘기면 안 됩니다(token passthrough 금지).

### 흐름 요약

```text
Client                    MCP Server               Authorization Server
  |  request (no token)       |                              |
  |-------------------------->|                              |
  |  401 + WWW-Authenticate   |                              |
  |<--------------------------|                              |
  |  GET protected resource metadata                         |
  |-------------------------->|                              |
  |  GET authorization server metadata                       |
  |--------------------------------------------------------->|
  |  authorize (PKCE + resource) / token                     |
  |<-------------------------------------------------------->|
  |  request + Bearer token   |                              |
  |-------------------------->|                              |
```

### 권한 범위(scope) 설계

사양의 보안 권고는 처음에는 읽기 위주의 최소 scope만 주고, 쓰기 같은 권한은 필요할 때 `403 insufficient_scope` 응답으로 추가 요청하게(step-up) 하라고 권합니다. 흔한 실수는 다음과 같습니다.

- `*`, `all`, `full-access` 같은 포괄 scope
- 모든 scope를 `scopes_supported`에 올려 처음부터 전부 받게 하는 설계
- 토큰에 적힌 scope만 믿고 서버 쪽 권한 검사를 생략하는 구현

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안 위협과 대응

공식 Security Best Practices 문서가 다루는 위협을 운영 관점으로 묶으면 다음과 같습니다.

| 위협              | 내용                                                           | 대응                                                   |
|-------------------|----------------------------------------------------------------|--------------------------------------------------------|
| 로컬 서버 악용    | 설정에 넣은 실행 명령이나 서버 패키지 자체가 악성인 경우       | 실행 명령 전체를 확인 후 승인, 샌드박스·최소 권한 실행 |
| Confused deputy   | 프록시 서버가 고정 client ID로 제3자 API에 접근할 때 동의 우회 | 클라이언트별 동의 저장, redirect URI 정확 일치 검사    |
| Token passthrough | 다른 대상용 토큰을 받아 하위 API로 그대로 전달                 | audience 검증, 서버 전용 토큰만 수락                   |
| SSRF              | 악성 서버가 메타데이터 URL을 내부 주소로 지정                  | HTTPS 강제, 사설·링크 로컬 대역 차단, egress 프록시    |
| 상태 핸들 탈취    | 서버가 발급한 작업 ID를 추측·탈취해 다른 사용자 상태 접근      | 무작위 핸들, 사용자와 서버 쪽 결합, 만료 설정          |
| 인가 URL 조작     | `javascript:` 등 위험한 스킴이나 셸 해석 문자를 담은 URL       | http(s)만 허용, 셸을 거치지 않고 URL 열기              |
| 과도한 scope      | 넓은 토큰 유출 시 피해 범위 확대                               | 최소 scope와 단계적 상향                               |

SSRF(Server-Side Request Forgery)는 공격자가 서버나 클라이언트를 시켜 내부 주소로 요청을 보내게 하는 공격입니다. 클라우드 메타데이터 주소(`169.254.169.254`)가 대표적인 목표입니다.

MCP 사양 밖이지만 함께 봐야 할 위험이 있습니다.

- 도구 결과·리소스 내용에 섞인 지시문이 모델 행동을 바꾸는 간접 프롬프트 주입(prompt injection)
- 도구 설명이 나중에 바뀌어 다른 동작을 하게 되는 경우
- 같은 세션에 연결된 다른 서버로 데이터가 흘러가는 경우

이 항목들은 저장소의 [AI 에이전트 보안 위험](../../07_ai_transformation/agent_security_risks.md)에서 함께 다룹니다. 사양은 도구 호출 전에 사람이 거부할 수 있는 단계(human in the loop)를 두라고 권합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 점검과 디버깅

공식 점검 도구는 MCP Inspector입니다. 하나의 패키지(`@modelcontextprotocol/inspector`)로 웹 UI, CLI, TUI 세 가지 클라이언트를 제공합니다. 공식 문서 기준 Node.js 22.23.4 이상, 24.22.1 이상, 또는 26.12.1 이상이 필요합니다(2026-11-16 확인).

```bash
# 로컬 stdio 서버를 웹 UI로 점검
npx @modelcontextprotocol/inspector node path/to/server/index.js

# CLI로 도구 목록만 받아 종료 (CI·스크립트용)
npx @modelcontextprotocol/inspector --cli node path/to/server/index.js --method tools/list

# 원격 HTTP 서버 점검
npx @modelcontextprotocol/inspector --server-url https://mcp.example.com/mcp --transport http
```

🟡 주의: 공식 문서에 따르면 Inspector는 OAuth 토큰과 stdio `env:` 값을 OS 키체인에 저장하며, 키체인이 없는 Linux 서버·컨테이너·SSH 세션에서는 `~/.mcp-inspector/secrets.json`에 저장합니다. 암호화 키를 따로 주지 않으면 이 파일은 암호화되지 않습니다. 공용 서버에서 Inspector를 쓴 뒤에는 이 파일의 존재와 권한을 확인합니다.

증상별 확인 순서는 다음과 같습니다.

| 증상                        | 먼저 볼 곳                                                  |
|-----------------------------|-------------------------------------------------------------|
| stdio 서버가 연결 직후 끊김 | 서버가 stdout에 로그를 쓰는지, 실행 경로·인터프리터 판 번호 |
| HTTP 서버가 400 반환        | `MCP-Protocol-Version`·`Mcp-Method` 헤더, 판 번호 불일치    |
| HTTP 서버가 403 반환        | `Origin` 검증 규칙, 토큰 scope                              |
| 응답이 늦게 몰려서 도착     | 프록시 버퍼링, `X-Accel-Buffering` 헤더                     |
| 도구가 목록에 보이지 않음   | 도구 정의의 스키마 오류, 클라이언트 쪽 허용 목록            |
| 401 반복                    | Protected Resource Metadata URL, 토큰 audience              |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 도입 점검표

새 MCP 서버를 팀 환경에 넣기 전에 확인할 항목입니다.

### 출처와 실행

- [ ] 서버 저장소·배포자·최근 유지 보수 상태를 확인했다
- [ ] 실행 명령 전체(인자 포함)를 읽고, `sudo`·네트워크 전송·홈 디렉터리 접근이 없는지 확인했다
- [ ] 패키지 판 번호를 고정했다(`npx -y 패키지` 같은 최신판 자동 실행을 피함)
- [ ] 컨테이너·별도 사용자 등으로 파일 시스템과 네트워크 접근 범위를 줄였다

### 권한과 데이터

- [ ] 도구 목록을 Inspector로 확인하고, 쓰기·삭제 도구가 무엇인지 표시했다
- [ ] 쓰기 도구는 호출 전 사용자 승인을 받도록 클라이언트 정책을 설정했다
- [ ] 서버에 넘기는 자격증명은 읽기 전용 또는 최소 권한 계정으로 만들었다
- [ ] 자격증명을 설정 파일에 평문으로 저장하지 않고 환경 변수·비밀 저장소를 사용했다

### 원격 서버 운영

- [ ] HTTPS와 OAuth 인증을 적용했고 토큰 audience 검증을 확인했다
- [ ] `Origin` 검증과 로컬 바인딩 규칙을 확인했다
- [ ] 도구 호출 로그(누가, 어떤 도구, 어떤 인자, 결과)를 남기고 보존 기간을 정했다
- [ ] 도구 호출 속도 제한과 시간 제한을 설정했다
- [ ] 사양 판 번호와 SDK 판 번호를 기록하고 갱신 주기를 정했다

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MCP: [Specification (latest)](https://modelcontextprotocol.io/specification/latest) — ★★★☆☆ (확인일 2026-11-16)
- MCP: [Key Changes 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog) — ★★★☆☆ (확인일 2026-11-16)
- MCP: [Transports: stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio), [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) — ★★★☆☆ (확인일 2026-11-16)
- MCP: [Server Features: Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) — ★★★☆☆ (확인일 2026-11-16)
- MCP: [Authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) — ★★★☆☆ (확인일 2026-11-16)
- MCP: [Security Best Practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices) — ★★★☆☆ (확인일 2026-11-16)
- MCP: [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) — ★★★☆☆ (확인일 2026-11-16)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) — ★★★☆☆ (확인일 2026-11-16)
- IETF: [RFC 9728 OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728) — ★★★★☆ (확인일 2026-11-16)
- IETF: [RFC 8707 Resource Indicators for OAuth 2.0](https://www.rfc-editor.org/rfc/rfc8707.html) — ★★★★☆ (확인일 2026-11-16)
- 관련 문서: [Claude Code 확장 기능](./claude/claude_code_extensions_guide.md), [AI 에이전트 보안 위험](../../07_ai_transformation/agent_security_risks.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-18

© 2026 siasia86. Licensed under CC BY 4.0.
