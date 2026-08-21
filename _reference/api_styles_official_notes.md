---
name: api-styles-official-notes
description: REST, GraphQL, gRPC, SOAP, WebSocket, Webhook, JSON-RPC, SSE의 공식 정의와 핵심 특성 참조 노트.
tags:
  - api
  - rest
  - graphql
  - grpc
  - soap
  - websocket
  - webhook
  - json-rpc
  - sse
last_checked: 2026-08-21
sources:
  - https://www.rfc-editor.org/rfc/rfc9110
  - https://graphql.org/learn/
  - https://grpc.io/docs/what-is-grpc/introduction/
  - https://grpc.io/docs/what-is-grpc/core-concepts/
  - https://grpc.io/blog/grpc-on-http2/
  - https://www.w3.org/TR/soap12-part1/
  - https://www.rfc-editor.org/rfc/rfc6455
  - https://docs.github.com/en/webhooks/about-webhooks
  - https://www.jsonrpc.org/specification
  - https://html.spec.whatwg.org/multipage/server-sent-events.html
---

# API Styles 공식 참조 노트

## 1. 확인 범위

2026-08-21 기준으로 주요 API 스타일의 공식 표준·공식 문서를 확인했습니다. REST는 독립적인 단일 프로토콜 규격이라기보다 HTTP의 리소스·표현·메서드 의미론을 활용하는 설계 스타일로 정리했습니다.

## 2. 공식 정의 요약

| 스타일    | 공식 자료                   | 검증된 핵심 사실                                      |
|-----------|-----------------------------|-------------------------------------------------------|
| REST      | RFC 9110                    | 리소스와 표현을 URI·HTTP 의미론으로 다루는 구조       |
| GraphQL   | graphql.org                 | 강한 타입 스키마를 기준으로 필요한 필드를 질의        |
| gRPC      | grpc.io                     | 서비스·메서드·메시지를 정의하고 원격 호출을 수행      |
| SOAP      | W3C SOAP 1.2                | XML 기반의 확장 가능한 메시징 프레임워크              |
| WebSocket | RFC 6455                    | 핸드셰이크 후 양방향 메시지 통신과 프레이밍 제공      |
| Webhook   | GitHub Docs                 | 이벤트 발생 시 구독자의 HTTP 서버로 데이터를 전달     |
| JSON-RPC  | JSON-RPC 2.0 Specification  | JSON 요청의 `method`, `params`, `id`로 원격 호출 표현 |
| SSE       | WHATWG HTML Living Standard | `text/event-stream`을 이용한 서버→클라이언트 스트림   |

## 3. 설계 시 주의

- 공식 문서가 정의하는 범위가 서로 다릅니다. REST·GraphQL·gRPC·SOAP·JSON-RPC는 요청 처리 모델 또는 메시지 모델에 가깝고, WebSocket·SSE·Webhook은 실시간성·이벤트 전달 방식에 가깝습니다.
- 한 시스템에서 REST와 Webhook을 함께 사용하거나, GraphQL과 SSE·WebSocket을 조합할 수 있습니다.
- 성능 수치는 네트워크 지연, 직렬화, 데이터 크기, 구현 언어, 프록시와 로드밸런서 설정에 따라 달라지므로 특정 스타일의 절대적인 우열로 해석하지 않습니다.
