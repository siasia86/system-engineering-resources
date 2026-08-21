# Top 8 API Styles 비교 가이드
<!-- reference: _reference/api_styles_official_notes.md -->

API(Application Programming Interface) 스타일은 클라이언트와 서버가 기능·데이터를 교환하는 방식의 설계 패턴입니다. 이 문서는 REST, GraphQL, gRPC, SOAP, WebSocket, Webhook, JSON-RPC, SSE(Server-Sent Events)를 비교하고 선택 기준을 정리합니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 비교 기준](#2-비교-기준) / [3. REST](#3-rest)                     |
| [4. GraphQL](#4-graphql) / [5. gRPC](#5-grpc) / [6. SOAP](#6-soap)                         |
| [7. WebSocket](#7-websocket) / [8. Webhook](#8-webhook) / [9. JSON-RPC](#9-json-rpc)       |
| [10. SSE](#10-sse) / [11. 선택 기준](#11-선택-기준) / [12. 보안 및 운영](#12-보안-및-운영) |
| [13. 결론](#13-결론)                                                                       |

---



## 1. 개요

API 스타일은 상호 배타적인 제품 분류가 아닙니다. 예를 들어 외부 공개 API는 REST로 제공하면서 이벤트 알림은 Webhook으로 전달하고, 내부 서비스 간 통신은 gRPC로 구성할 수 있습니다.

### 분류 관점

| 분류                    | 해당 스타일          | 핵심 질문                                   |
|-------------------------|----------------------|---------------------------------------------|
| 리소스 중심             | REST                 | 어떤 리소스를 어떤 HTTP 의미로 다룰까요?    |
| 질의 중심               | GraphQL              | 필요한 필드를 클라이언트가 선택할까요?      |
| 함수·서비스 호출 중심   | gRPC, SOAP, JSON-RPC | 원격 함수를 계약에 따라 호출할까요?         |
| 양방향·스트림 중심      | WebSocket            | 연결을 유지하며 양방향 메시지를 교환할까요? |
| 서버 이벤트·비동기 전달 | Webhook, SSE         | 서버 이벤트를 어떤 방향으로 전달할까요?     |

> RPC(Remote Procedure Call): 네트워크 반대편의 함수를 로컬 함수처럼 호출하는 통신 모델입니다.
> 호출 방식은 함수 중심이지만, 실제로는 직렬화·전송·타임아웃·오류 처리를 함께 설계해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 비교 기준

스타일을 선택할 때 단순한 처리량보다 계약 관리, 통신 방향, 브라우저 호환성, 운영 복잡도를 함께 평가합니다.

| 기준            | 확인할 질문                                               |
|-----------------|-----------------------------------------------------------|
| 데이터 모델     | 리소스, 그래프, 메시지, 함수 중 무엇이 자연스러운가요?    |
| 통신 방향       | 요청·응답, 서버 푸시, 양방향 중 무엇이 필요한가요?        |
| 계약 관리       | 스키마·IDL·WSDL 등 계약을 어떻게 배포하고 검증하나요?     |
| 클라이언트 범위 | 브라우저, 모바일, 내부 서비스, 외부 파트너 중 어디인가요? |
| 성능 특성       | 지연시간, 메시지 크기, 연결 수, 스트리밍이 중요한가요?    |
| 운영 특성       | 캐시, 재시도, 관측성, 버전 호환성을 어떻게 관리하나요?    |
| 보안 경계       | 인증·인가·서명 검증·재전송 방지를 어디서 수행하나요?      |

> IDL(Interface Definition Language): 서비스 메서드와 메시지 구조를 언어에 독립적으로 정의하는 형식입니다.
> gRPC의 Protocol Buffers가 대표적인 IDL이며, 코드 생성과 계약 검증의 입력으로 사용됩니다.

[⬆ 목차로 돌아가기](#목차)

## 3. REST

REST(Representational State Transfer)는 리소스와 그 표현을 중심으로 상호작용하는 설계 스타일입니다. HTTP를 사용할 때 URI, 메서드, 상태 코드, 헤더, 표현 형식을 조합해 일관된 인터페이스를 구성합니다.

### 핵심 모델

- 리소스는 URI로 식별합니다.
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE` 등 HTTP 메서드의 의미를 지킵니다.
- JSON, XML 등 표현 형식과 리소스 자체를 구분합니다.
- HTTP 캐시, 프록시, 상태 코드 등 웹 인프라를 활용하기 쉽습니다.
- 서버 세션에 의존하지 않는 무상태(stateless) 요청을 기본으로 설계합니다.

### 장점과 주의사항

| 장점                         | 주의사항                                         |
|------------------------------|--------------------------------------------------|
| 웹 인프라·도구 호환성이 높음 | 복잡한 화면별 데이터 조합에 호출이 늘 수 있음    |
| 캐시·상태 코드 활용이 쉬움   | 리소스 모델과 HTTP 의미론을 일관되게 유지해야 함 |
| 브라우저·외부 파트너에 적합  | 실시간 양방향 통신에는 별도 방식이 필요함        |

### 요청 예시

```http
GET /v1/users/42 HTTP/1.1
Host: api.example.com
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 42,
  "name": "Secureuser123",
  "status": "active"
}
```

### 적합한 상황

공개 API, CRUD 중심 서비스, 캐시 가능한 조회 API, 다양한 언어·도구가 접속하는 통합 API에 우선 검토합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. GraphQL

GraphQL은 스키마와 타입을 기준으로 클라이언트가 필요한 필드를 질의하는 API 질의 언어이자 실행 환경입니다. 일반적으로 단일 엔드포인트에서 `query`, `mutation`, `subscription`을 구분합니다.

### 핵심 모델

- 스키마가 타입·필드·인자를 정의합니다.
- 클라이언트가 응답에 필요한 필드를 선택합니다.
- `query`는 조회, `mutation`은 변경, `subscription`은 실시간 이벤트에 사용합니다.
- 응답은 질의 구조에 맞춰 중첩 데이터를 반환합니다.
- 스키마 검증으로 일부 오류를 실행 전에 발견할 수 있습니다.

### 장점과 주의사항

| 장점                            | 주의사항                                              |
|---------------------------------|-------------------------------------------------------|
| 화면별 필요한 데이터만 요청     | 쿼리 복잡도·깊이·비용 제한이 필요함                   |
| 여러 리소스 조합을 한 번에 처리 | HTTP 캐시와 CDN 캐시 전략이 REST보다 복잡할 수 있음   |
| 타입 기반 문서화와 탐색 지원    | 필드별 인증·인가와 데이터 로더를 세밀하게 설계해야 함 |

### 질의 예시

```graphql
query UserProfile($id: ID!) {
  user(id: $id) {
    id
    name
    orders(limit: 10) {
      id
      total
    }
  }
}
```

### 적합한 상황

모바일·웹 화면마다 필요한 데이터 모양이 다르거나, 여러 백엔드 리소스를 하나의 화면 응답으로 조합해야 하는 경우에 적합합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. gRPC

gRPC는 서비스의 메서드와 메시지 계약을 정의하고, 생성된 클라이언트 스텁을 통해 원격 메서드를 호출하는 RPC 프레임워크입니다. 기본적으로 Protocol Buffers를 계약과 메시지 형식으로 사용하며, HTTP/2 스트림 위에서 통신합니다.

### 핵심 모델

- `.proto` 파일로 서비스, 메서드, 요청·응답 메시지를 정의합니다.
- 코드 생성기가 언어별 클라이언트·서버 코드를 생성합니다.
- 단일 요청·응답, 서버 스트리밍, 클라이언트 스트리밍, 양방향 스트리밍을 지원합니다.
- deadline, 상태 코드, metadata, channel을 운영 모델에 포함합니다.
- 내부 서비스 간 통신에서 명시적인 계약과 낮은 직렬화 비용을 활용하기 좋습니다.

### 서비스 계약 예시

```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc WatchUserEvents(WatchUserRequest) returns (stream UserEvent);
}

message GetUserRequest {
  int64 user_id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
}
```

### 장점과 주의사항

| 장점                     | 주의사항                                          |
|--------------------------|---------------------------------------------------|
| 강한 계약과 코드 생성    | 브라우저 직접 호출에는 gRPC-Web 등 별도 고려 필요 |
| 스트리밍과 deadline 지원 | 프록시·로드밸런서의 HTTP/2 지원을 확인해야 함     |
| 서비스 간 통신에 효율적  | 사람이 직접 읽는 디버깅과 범용 도구 접근성이 낮음 |

### 적합한 상황

내부 마이크로서비스, 고빈도 서비스 간 호출, 다중 언어 환경, 스트리밍 RPC가 필요한 시스템에 적합합니다. 외부 공개 API는 브라우저·파트너 호환성을 먼저 검토합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. SOAP

SOAP은 XML 기술을 사용해 구조화된 정보를 교환하는 확장 가능한 메시징 프레임워크입니다. W3C SOAP 1.2는 메시지 구조와 처리 모델을 정의하며, 다양한 하위 프로토콜 바인딩을 허용합니다.

### 핵심 모델

- `Envelope`가 메시지의 외곽 구조를 제공합니다.
- 선택적인 `Header`에 확장 제어 정보를 담을 수 있습니다.
- `Body`에 업무 메시지와 오류 정보를 담습니다.
- XML 스키마와 엔터프라이즈 표준을 활용하는 통합 환경에 적합합니다.
- WS-* 계열 정책을 사용하는 기존 파트너 시스템과의 호환성이 중요합니다.

### 메시지 예시

```xml
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header/>
  <soap:Body>
    <GetUser xmlns="https://api.example.com/user">
      <UserId>42</UserId>
    </GetUser>
  </soap:Body>
</soap:Envelope>
```

### 장점과 주의사항

| 장점                          | 주의사항                                |
|-------------------------------|-----------------------------------------|
| 표준화된 XML 메시지 구조      | 메시지 크기와 처리 비용이 커질 수 있음  |
| 기존 엔터프라이즈 통합에 강함 | XML 네임스페이스·스키마 관리가 복잡함   |
| 확장 헤더와 오류 모델 제공    | 신규 웹·모바일 API에는 과한 경우가 많음 |

### 적합한 상황

금융·공공·대기업 파트너 연계처럼 기존 SOAP 계약과 XML 기반 표준을 반드시 유지해야 하는 환경에 적합합니다. 신규 시스템은 상호운용성 요구사항과 운영 조직의 기존 자산을 확인한 뒤 선택합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. WebSocket

WebSocket은 초기 핸드셰이크 후 하나의 연결에서 클라이언트와 서버가 양방향 메시지를 주고받는 프로토콜입니다. RFC 6455는 메시지 프레이밍과 브라우저의 origin 기반 보안 모델을 정의합니다.

### 핵심 모델

- 연결을 수립한 뒤 양쪽이 모두 메시지를 보낼 수 있습니다.
- 서버가 임의 시점에 클라이언트로 이벤트를 보낼 수 있습니다.
- 연결 수명, 재연결, heartbeat, backpressure를 애플리케이션이 관리해야 합니다.
- `wss://`를 사용해 TLS로 보호하고 origin·인증·인가를 검증합니다.

> Backpressure: 생산자가 소비자보다 빠르게 데이터를 생성할 때 전송 속도나 버퍼를 조절하는 제어입니다.
> WebSocket에서는 무제한 버퍼링을 피하고 연결별 메시지·큐 상한을 정의해야 합니다.

### 클라이언트 예시

```javascript
const socket = new WebSocket('wss://api.example.com/v1/events');

socket.addEventListener('open', () => {
  socket.send(JSON.stringify({type: 'subscribe', topic: 'orders'}));
});

socket.addEventListener('message', (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
});
```

### 적합한 상황

협업 편집, 게임 상태, 채팅, 실시간 대시보드처럼 낮은 지연의 양방향 상호작용이 필요한 경우에 적합합니다. 단방향 서버 알림만 필요하면 SSE가 더 단순할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 8. Webhook

Webhook은 특정 이벤트가 발생했을 때 제공자가 구독자의 HTTP 엔드포인트로 요청을 보내는 비동기 전달 방식입니다. 주기적으로 API를 조회하는 polling보다 이벤트 중심 시스템에 적합합니다.

### 핵심 모델

- 수신자가 이벤트 종류와 callback URL을 등록합니다.
- 제공자는 이벤트 발생 시 HTTP 요청과 payload를 전송합니다.
- 수신자는 빠르게 수락한 뒤 실제 처리는 큐나 백그라운드 작업으로 넘깁니다.
- 실패 재전송, 중복 이벤트, 순서 뒤바뀜, 지연 도착을 고려해야 합니다.
- 요청 서명 검증, timestamp·event ID 확인, allowlist와 TLS를 적용합니다.

### 전달 예시

```http
POST /hooks/orders HTTP/1.1
Host: receiver.example.com
Content-Type: application/json
X-Event-Type: order.created
X-Event-Id: evt_20260821_0001
X-Signature: SecureToken123

{
  "id": "evt_20260821_0001",
  "type": "order.created",
  "data": {
    "order_id": "ord_42",
    "status": "created"
  }
}
```

### 적합한 상황

결제 완료, 저장소 push, CI 트리거, 배포 이벤트처럼 특정 사건이 발생했을 때 다른 시스템을 실행해야 하는 경우에 적합합니다. Webhook은 조회 API를 대체하기보다 이벤트 알림을 보완하는 방식으로 설계합니다.

[⬆ 목차로 돌아가기](#목차)

## 9. JSON-RPC

JSON-RPC는 JSON으로 원격 메서드 호출을 표현하는 가볍고 전송 독립적인 RPC 프로토콜입니다. HTTP, 소켓, 메시지 전달 등 여러 전송 수단 위에서 사용할 수 있습니다.

### 핵심 모델

- 요청에 JSON-RPC 버전, `method`, 선택적 `params`, 상관관계용 `id`를 담습니다.
- 응답의 `id`로 요청과 결과를 연결합니다.
- 알림(notification)은 `id`가 없어 응답을 요구하지 않습니다.
- 오류 응답과 batch 요청을 표준 구조로 표현할 수 있습니다.
- 리소스보다 동작·메서드 중심의 인터페이스에 자연스럽습니다.

### 요청 예시

```json
{
  "jsonrpc": "2.0",
  "method": "user.get",
  "params": {
    "id": 42
  },
  "id": 1
}
```

```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": 42,
    "name": "Secureuser123"
  },
  "id": 1
}
```

### 적합한 상황

내부 도구, 자동화 에이전트, IDE·개발 도구 연계처럼 메서드 호출과 JSON의 단순성이 중요한 경우에 적합합니다. 공개 웹 API에서는 메서드 명명·권한·버전·오류 규칙을 별도로 엄격하게 문서화해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 10. SSE

SSE는 서버가 HTTP 연결을 유지하면서 클라이언트로 이벤트를 단방향 스트리밍하는 방식입니다. WHATWG HTML 표준의 `EventSource` API와 `text/event-stream` 형식을 사용하며, 브라우저가 연결 종료 후 재연결을 지원합니다.

### 핵심 모델

- 통신 방향은 서버에서 클라이언트로 단방향입니다.
- 이벤트 스트림은 UTF-8 텍스트 형식으로 전달합니다.
- 이벤트 이름, 데이터, `id`, 재연결 지연 등을 스트림 필드로 표현할 수 있습니다.
- 클라이언트의 이벤트 전송은 별도 HTTP 요청이나 다른 채널이 필요합니다.
- 프록시 timeout, 연결 수, heartbeat, 재연결 시 중복 처리를 확인해야 합니다.

### 서버 스트림 예시

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

id: 42
event: order.updated
data: {"order_id":"ord_42","status":"paid"}

```

### 브라우저 예시

```javascript
const events = new EventSource('https://api.example.com/v1/events');

events.addEventListener('order.updated', (event) => {
  const update = JSON.parse(event.data);
  console.log(update.order_id, update.status);
});
```

### 적합한 상황

알림, 진행률, 로그 tail, 대시보드 갱신처럼 서버에서 브라우저로 지속적인 업데이트를 보내야 하지만 클라이언트→서버 실시간 메시지는 필요하지 않은 경우에 적합합니다.

[⬆ 목차로 돌아가기](#목차)

## 11. 선택 기준

| 요구사항                        | 우선 검토 스타일 | 선택 이유                                 |
|---------------------------------|------------------|-------------------------------------------|
| 공개 CRUD API                   | REST             | HTTP 도구·캐시·브라우저 호환성이 높음     |
| 화면별 응답 조합                | GraphQL          | 클라이언트가 필요한 필드를 선택함         |
| 내부 서비스 간 고성능 호출      | gRPC             | 계약·코드 생성·스트리밍을 제공함          |
| 기존 XML 엔터프라이즈 계약      | SOAP             | W3C 메시지 구조와 기존 표준을 유지함      |
| 양방향 저지연 상호작용          | WebSocket        | 연결을 유지하며 양방향 메시지를 교환함    |
| 이벤트 발생 후 외부 시스템 호출 | Webhook          | polling 없이 이벤트를 전달함              |
| 메서드 호출 중심의 JSON 통신    | JSON-RPC         | `method`·`params` 기반 호출 모델이 단순함 |
| 단방향 서버 이벤트 스트림       | SSE              | 표준 `EventSource`와 HTTP 스트림을 활용함 |

### 조합 예시

```text
Public API: REST + OAuth 2.0 + Webhook
Web application: GraphQL + SSE
Internal services: gRPC + REST gateway
Legacy partner: SOAP + message queue
Developer tooling: JSON-RPC over stdio or HTTP
```

[⬆ 목차로 돌아가기](#목차)

## 12. 보안 및 운영

스타일과 관계없이 다음 항목을 공통 운영 기준으로 적용합니다.

| 영역        | 기본 통제                                           |
|-------------|-----------------------------------------------------|
| 전송 보안   | 외부 통신은 TLS를 사용하고 인증서를 검증함          |
| 인증·인가   | 인증과 권한 검사를 분리하고 최소 권한을 적용함      |
| 입력 검증   | 스키마·크기·깊이·메서드·콘텐츠 타입을 검증함        |
| 재전송 방지 | 요청 ID, timestamp, nonce 또는 idempotency key 사용 |
| 속도 제한   | 사용자·토큰·IP·메서드별 rate limit을 적용함         |
| 타임아웃    | connect, read, write, 전체 처리 deadline을 분리함   |
| 실패 처리   | 재시도 횟수·backoff·dead-letter 경로를 정의함       |
| 관측성      | request ID, latency, status, payload 크기를 기록함  |
| 비밀 관리   | API 키·서명 키를 코드와 문서에 하드코딩하지 않음    |

### 운영 체크리스트

- [ ] 계약 변경 시 하위 호환성, deprecation, migration 기간을 정의합니다.
- [ ] Webhook·메시지 재처리는 idempotent하게 설계합니다.
- [ ] GraphQL query depth와 비용, WebSocket 연결 수, SSE 동시 연결 수를 제한합니다.
- [ ] gRPC deadline과 상태 코드, REST HTTP 상태 코드의 의미를 문서화합니다.
- [ ] 인증 실패·비정상 payload·재전송 폭증을 모니터링하고 알림 기준을 설정합니다.

[⬆ 목차로 돌아가기](#목차)

## 13. 결론

기본 선택은 리소스 중심의 공개 API에는 REST, 화면별 데이터 조합에는 GraphQL, 내부 서비스 계약에는 gRPC입니다. SOAP은 기존 XML 엔터프라이즈 계약을 유지해야 할 때, WebSocket은 양방향 실시간 상호작용에, Webhook은 이벤트 전달에, JSON-RPC는 메서드 호출에, SSE는 단방향 서버 스트림에 적합합니다.

최종 결정은 성능 벤치마크 하나가 아니라 클라이언트 종류, 계약 수명, 보안 경계, 운영 도구, 재시도·순서·중복 처리 요구를 함께 평가하여 내립니다.


---

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- HTTP Semantics: [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110) — ★★★★☆
- GraphQL Documentation: [graphql.org/learn](https://graphql.org/learn/) — ★★★☆☆
- gRPC Documentation: [Introduction to gRPC](https://grpc.io/docs/what-is-grpc/introduction/) — ★★★☆☆
- gRPC Documentation: [Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) — ★★★☆☆
- gRPC Official Blog: [gRPC on HTTP/2](https://grpc.io/blog/grpc-on-http2/) — ★★☆☆☆
- W3C Recommendation: [SOAP Version 1.2 Part 1](https://www.w3.org/TR/soap12-part1/) — ★★★☆☆
- WebSocket Protocol: [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) — ★★★★☆
- GitHub Docs: [About webhooks](https://docs.github.com/en/webhooks/about-webhooks) — ★★★☆☆
- JSON-RPC: [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) — ★★★☆☆
- WHATWG HTML: [Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-21

**마지막 업데이트**: 2026-08-21

© 2026 siasia86. Licensed under CC BY 4.0.
