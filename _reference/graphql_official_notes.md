---
name: graphql-official-notes
description: GraphQL 사양과 공식 학습 문서의 스키마·실행·HTTP·보안·운영 참조 노트.
tags:
  - graphql
  - api
  - schema
  - security
  - http
last_checked: 2026-09-14
sources:
  - https://spec.graphql.org/September2025/
  - https://graphql.org/learn/
  - https://graphql.org/learn/schema/
  - https://graphql.org/learn/queries/
  - https://graphql.org/learn/serving-over-http/
  - https://graphql.org/learn/response/
  - https://graphql.org/learn/security/
  - https://graphql.org/learn/authorization/
  - https://graphql.org/learn/performance/
  - https://graphql.org/learn/caching/
  - https://graphql.github.io/graphql-over-http/draft/
---

# GraphQL 공식 참조 노트

## 1. 확인 범위

2026-09-14 기준으로 GraphQL 공식 사양과 `graphql.org`의 학습·운영 문서를 확인했습니다. GraphQL 사양은 질의 언어와 실행 엔진의 규범을 정의하며, 특정 전송 프로토콜이나 구현 라이브러리의 버전을 하나로 고정하지 않습니다.

## 2. 버전 상태

- `graphql/graphql-spec`의 최신 공식 릴리스 태그는 `September2025`입니다.
- 최신 작업 초안은 `https://spec.graphql.org/draft`에서 제공됩니다. 사양이 향후 에디션에서 변경될 수 있으므로 구현체와 문서에서 사양 버전을 함께 기록합니다.
- GraphQL over HTTP 사양은 확인일 기준 초안입니다. GraphQL 언어 사양과 달리 HTTP 상호운용성에 관한 권고가 아직 최종 규범은 아니므로 서버·클라이언트 구현의 준수 범위를 확인합니다.

## 3. 핵심 개념

| 항목          | 공식 문서에서 확인한 내용                                   |
|---------------|-------------------------------------------------------------|
| GraphQL       | 스키마를 기준으로 질의하고 실행하는 언어·실행 엔진          |
| Schema        | 질의 가능한 데이터의 타입·필드·인자와 서비스 능력 정의      |
| Query         | 데이터를 읽기 위한 operation type                           |
| Mutation      | 데이터를 변경하기 위한 operation type                       |
| Subscription  | 장기 실행 연결을 통해 이벤트를 전달하기 위한 operation type |
| Response      | `data`, `errors`, `extensions`를 사용할 수 있는 응답 구조   |
| Introspection | GraphQL 스키마 자체를 질의하는 기능                         |

- 질의의 selection set이 응답의 데이터 모양을 결정합니다.
- 서버는 스키마에 대한 구문·검증을 통과한 operation을 실행합니다.
- GraphQL의 개념 모델은 URL로 식별하는 리소스보다 entity graph에 가깝습니다.

## 4. HTTP와 전송

- GraphQL 사양은 client-server 요청·응답에 특정 전송 프로토콜을 요구하지 않습니다.
- HTTP는 범용성이 높아 query와 mutation의 일반적인 전송 방식이며, 보통 하나의 `/graphql` endpoint를 사용합니다.
- HTTP 지침은 stateless query·mutation에 적용합니다. subscription은 WebSocket이나 SSE 같은 장기 연결 전송을 별도로 검토합니다.
- GraphQL over HTTP 초안은 JSON 직렬화와 `Accept: application/graphql-response+json` 사용을 권고합니다. 실제 지원 범위는 서버·클라이언트 조합별로 확인합니다.
- GET은 query operation에 사용할 수 있고 HTTP 캐시·CDN과 연계할 수 있습니다. mutation을 GET으로 처리하지 않도록 operation 종류와 서버 정책을 분리합니다.

## 5. 응답과 오류

- 요청 오류는 문서 구문 분석·스키마 검증 단계에서 발생하며, resolver 실행 전에 응답될 수 있습니다.
- 필드 오류는 실행 중 발생하며, 다른 필드의 결과와 함께 부분 응답이 반환될 수 있습니다.
- 부분 응답에서는 `data`와 `errors`가 함께 나타날 수 있으므로 client는 HTTP status만으로 업무 성공 여부를 판단하지 않습니다.
- `errors`의 `message`와 선택적 `locations`, `path`를 운영 진단에 활용하되 내부 구현·비밀정보를 외부에 노출하지 않습니다.
- `extensions`는 구현체가 추가 정보를 담을 수 있는 영역이며, 제공 내용과 운영 노출 여부를 서비스가 결정합니다.

## 6. 보안·신뢰성 권고

### 요청 수요 제어

공식 보안 문서는 악의적이거나 과도한 operation이 서버와 하위 데이터 소스를 소모할 수 있다고 설명합니다. 다음 방어 계층을 조합합니다.

- 최대 query depth와 list depth 제한
- top-level field·alias·batch 요청 수 제한
- 사용자·토큰·IP·operation 기준 rate limit
- query complexity 또는 비용 분석과 예산 초과 거부
- 인자 값의 검증·정규화·sanitization
- first-party client라면 trusted document 또는 persisted query 사용
- introspection을 환경·인증·허용 목록 정책에 따라 제한
- HTTP 사용 시 HTTPS, timeout, private cache 정책 적용

### 인증과 인가

- 인증 middleware를 GraphQL 실행 앞에 배치해 요청의 사용자·세션 정보를 context로 전달합니다.
- 인가는 resolver에 임시로 흩뿌리기보다 business logic 계층이 수행하도록 설계합니다.
- 필드 단위 인가 실패가 부분 응답으로 이어질 수 있으므로 `nullability`, 오류 정책, 민감 필드의 노출 기준을 함께 정의합니다.
- 인증(authentication)과 인가(authorization)를 분리하고, 하위 저장소·서비스 호출에도 주체와 권한을 전달합니다.

## 7. 성능·캐시·스키마 운영

- 중첩 field resolver가 데이터 소스를 반복 호출하는 N+1 문제를 만들 수 있습니다. 데이터 로더의 batching과 caching으로 하위 호출을 묶되, depth·breadth·complexity 제한을 별도로 유지합니다.
- 단일 endpoint 자체가 캐시 불가능하다는 뜻은 아닙니다. query operation의 GET, persisted query, 응답·객체 식별자 전략을 HTTP 캐시·CDN 정책과 함께 설계합니다.
- GraphQL에는 REST URI와 같은 전역 객체 식별자가 자동으로 제공되지 않으므로, client cache가 필요하면 안정적인 전역 `id` 필드 정책을 스키마에 둡니다.
- schema 변경은 field 추가·deprecation·삭제가 사용하는 client와 문서 생성 도구에 미치는 영향을 확인한 뒤 단계적으로 진행합니다.
- operation name, normalized query hash, schema version, resolver latency, downstream 호출 수와 오류를 관측 필드로 기록합니다. 원문 query와 변수에는 민감정보가 포함될 수 있으므로 마스킹·보존 기간을 정의합니다.

## 8. 공식 문서와 구현의 경계

- GraphQL 언어 사양은 schema, validation, execution, response의 의미를 정의하지만 인증, rate limit, cache backend, DataLoader 같은 운영 구현을 하나로 정하지 않습니다.
- HTTP endpoint, JSON media type, subscription 전송 방식, 파일 업로드는 사용하는 HTTP·subscription·파일 업로드 규격과 서버 구현의 지원 범위를 별도로 확인합니다.
- 특정 GraphQL 서버 프레임워크의 설정값이나 DataLoader API를 일반 GraphQL 사양의 요구사항으로 기술하지 않습니다.
