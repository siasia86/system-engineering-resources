# SE를 위한 GraphQL 가이드
<!-- reference: _reference/graphql_official_notes.md -->

시스템 엔지니어 관점에서 GraphQL을 설계·운영하는 가이드입니다. 스키마 계약, query·mutation·subscription 실행 모델, resolver와 하위 시스템 부하, 인증·인가·캐시·관측성에 초점을 맞춥니다.

GraphQL은 REST의 상위 호환판이 아닙니다. REST가 HTTP resource와 method 의미론을 중심으로 계약을 표현한다면, GraphQL은 타입이 있는 schema와 client가 선택하는 selection set을 중심으로 응답을 구성합니다. 따라서 도입 여부는 성능 비교 하나가 아니라 client 다양성, 캐시·보안 경계, 운영 도구, 계약 수명을 함께 평가해 결정합니다.

## 목차

| 섹션                                                                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. GraphQL 개요](#1-graphql-개요) / [2. SE 활용 판단](#2-se-활용-판단) / [3. Schema와 Type](#3-schema와-type)                                                              |
| [4. Query·Mutation·Subscription](#4-querymutationsubscription) / [5. HTTP 요청·응답·오류](#5-http-요청응답오류) / [6. Resolver·N+1·페이지네이션](#6-resolvern1페이지네이션) |
| [7. 보안·인증·인가·캐시](#7-보안인증인가캐시) / [8. 관측성·스키마 운영](#8-관측성스키마-운영) / [9. 단계별 학습과 실무 프로젝트](#9-단계별-학습과-실무-프로젝트)            |
| [10. CI·운영 검증](#10-ci운영-검증)                                                                                                                                         |

---

## 1. GraphQL 개요

GraphQL은 schema를 기준으로 client가 필요한 field를 질의하고, server가 그 질의를 검증·실행하는 언어이자 실행 환경입니다. GraphQL 사양은 특정 전송 프로토콜을 강제하지 않지만, query와 mutation에는 HTTP를 흔히 사용하고 subscription에는 WebSocket 또는 SSE 같은 장기 연결 방식을 조합합니다.

> Schema: client가 질의할 수 있는 type, field, argument와 operation을 정의한 계약입니다. 데이터베이스 schema와 달리 API의 외부 표현과 실행 가능한 capability를 설명합니다.

### REST와 GraphQL의 모델 차이

| 구분           | REST API                        | GraphQL API                                  |
|----------------|---------------------------------|----------------------------------------------|
| 중심 모델      | resource와 representation       | type과 entity graph                          |
| endpoint       | resource별 URI                  | 일반적으로 하나의 GraphQL endpoint           |
| 응답 형태      | server가 정의한 representation  | client selection set에 따른 응답             |
| 계약           | URI·method·status·media type    | schema·operation·field·argument              |
| 캐시 기본 단위 | URI와 HTTP cache                | operation·응답·객체 식별자                   |
| 오류 판단      | HTTP status와 오류 body         | `data`·`errors`·HTTP transport 결과의 조합   |
| 실시간 처리    | 별도 SSE·WebSocket·Webhook 조합 | subscription과 별도 장기 연결 transport 조합 |

GraphQL은 여러 backend resource를 한 화면의 데이터 모양으로 조합하는 데 강점이 있습니다. 반면 운영자가 `curl`과 HTTP status만으로 확인해야 하는 단순 관리 API, 공개 CRUD API, URI 기반 CDN 캐시가 핵심인 API에는 REST가 더 단순할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. SE 활용 판단

### GraphQL을 우선 검토할 상황

| 상황                           | GraphQL의 이점                       | 운영상 확인할 항목                      |
|--------------------------------|--------------------------------------|-----------------------------------------|
| 화면별 응답 field가 다름       | client가 필요한 field만 선택         | query 비용·응답 크기·client별 operation |
| 여러 backend 조합              | 한 operation에서 중첩 graph 조회     | downstream timeout·부분 실패·권한 전파  |
| 다수 client와 빠른 schema 진화 | add field 중심의 점진적 계약 변경    | deprecation·schema registry·문서 생성   |
| 모바일·저대역폭 client         | 불필요한 field 전송 감소             | 압축·pagination·최대 응답 크기          |
| 내부 포털·inventory 화면       | 화면 데이터 조합을 API 계층에서 통합 | resolver latency·N+1·캐시 정책          |

### REST 또는 gRPC가 더 적절할 수 있는 상황

- 운영 자동화와 외부 사용자가 단순 HTTP 도구로 호출해야 하는 resource API는 REST를 우선 검토합니다.
- 강한 고정 계약, 생성 코드, deadline, streaming RPC가 핵심인 내부 서비스 간 통신은 gRPC를 우선 검토합니다.
- 파일 자체 업로드, 대용량 다운로드, 장기 작업 제어처럼 HTTP semantics와 object storage가 중심인 기능은 REST·signed URL·event API 조합이 단순할 수 있습니다.
- GraphQL gateway를 추가해도 backend의 부하와 권한 문제가 사라지지 않습니다. gateway가 연결하는 각 시스템의 timeout, rate limit, audit 정책을 그대로 설계해야 합니다.

### 역할 분담 예시

```text
Public resource API      REST + OpenAPI + Webhook
Web and mobile BFF       GraphQL + persisted queries
Internal service contract gRPC + Protobuf
Large file transfer      REST + object storage signed URL
Realtime notification    GraphQL subscription + SSE/WebSocket
```

기존 [SE를 위한 REST API 가이드](rest_api_guide_for_se.md)와 [SE를 위한 gRPC 가이드](grpc_guide_for_se.md)를 함께 읽고 외부 API, 화면 조합 계층, 내부 서비스 계약을 분리해 판단합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Schema와 Type

GraphQL schema는 client가 볼 수 있는 API 계약입니다. schema definition language(SDL)로 type과 field를 표현하고, 각 field의 반환 type과 argument를 명시합니다.

### 기본 schema 예시

```graphql
type Query {
  host(id: ID!): Host
  hosts(first: Int!, after: String): HostConnection!
}

type Mutation {
  restartHost(input: RestartHostInput!): RestartHostPayload!
}

type Host {
  id: ID!
  hostname: String!
  maintenanceNote: String
  status: HostStatus!
  addresses: [String!]!
}

enum HostStatus {
  ACTIVE
  DRAINING
  OFFLINE
}

input RestartHostInput {
  hostId: ID!
  reason: String!
}

type RestartHostPayload {
  host: Host
  accepted: Boolean!
  requestId: ID!
}
```

### 설계 기준

- 외부 계약에는 내부 DB column명과 운영용 secret을 그대로 노출하지 않습니다.
- `String`, `Int`, `Float`, `Boolean`, `ID` 같은 scalar와 object, enum, input을 용도에 맞게 구분합니다.
- `!`를 사용한 Non-Null은 client가 의존하는 강한 계약이므로 실제 데이터 결손·권한 실패·부분 응답 정책을 먼저 확인합니다.
- 목록은 `[Host!]!`처럼 list 자체와 원소의 nullability를 분리해 정의합니다.
- mutation 입력은 여러 argument보다 목적별 input object로 묶어 validation과 확장을 쉽게 합니다.
- 이름은 도메인 용어를 사용하고, field 이름만 보고도 비용과 권한 경계를 추정할 수 있게 합니다.
- schema에 추가한 field는 기존 client와 공존시키고, 제거가 필요하면 deprecation·사용량 확인·migration 기간을 둡니다.

> Resolver: client가 요청한 field를 실제 값으로 계산·조회하는 실행 함수입니다. resolver가 DB, 다른 API, queue 같은 하위 시스템을 호출하므로 schema의 field 수가 곧 backend 호출 수가 되지 않도록 관리해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Query·Mutation·Subscription

GraphQL operation은 실행 의도를 `query`, `mutation`, `subscription`으로 구분합니다. operation name과 variable을 사용하면 로그·권한·재현 테스트에서 요청을 식별하기 쉽습니다.

### Query

```graphql
query HostDetail($id: ID!) {
  host(id: $id) {
    id
    hostname
    status
    addresses
  }
}
```

```json
{
  "id": "host-42"
}
```

- query는 읽기 operation으로 설계하고, 호출자가 선택한 field만 반환합니다.
- 목록 query에는 `first`·`after` 또는 서비스가 정한 cursor pagination을 적용합니다.
- 무제한 목록, 임의 깊이의 중첩 graph, 한 operation의 과도한 alias를 허용하지 않습니다.

### Mutation

```graphql
mutation RestartHost($input: RestartHostInput!) {
  restartHost(input: $input) {
    accepted
    requestId
    host {
      id
      status
    }
  }
}
```

```json
{
  "input": {
    "hostId": "host-42",
    "reason": "scheduled-maintenance"
  }
}
```

- mutation은 command의 결과와 비동기 작업 식별자를 명시적으로 반환합니다.
- 재시도될 수 있는 mutation은 idempotency key 또는 client mutation ID를 계약에 포함합니다.
- 부작용의 순서, 중복 요청, timeout 이후 실제 작업 상태를 별도 상태 조회로 확인할 수 있게 합니다.
- mutation 안에 지나치게 많은 부작용을 숨기지 않고 도메인 command 단위로 분리합니다.

### Subscription

```graphql
subscription HostEvents($hostId: ID!) {
  hostEvents(hostId: $hostId) {
    eventId
    hostId
    status
    occurredAt
  }
}
```

- subscription은 이벤트의 전달 모델이지 자동으로 durable queue나 exactly-once 처리를 제공하는 기능이 아닙니다.
- 연결 수, heartbeat, idle timeout, 재연결, 중복 이벤트, 마지막 event cursor와 backpressure를 정의합니다.
- WebSocket과 SSE 중 하나를 선택하고 proxy timeout, load balancer, 인증 갱신, graceful shutdown을 검증합니다.
- 최신 상태가 필요한지, 모든 이벤트를 유실 없이 처리해야 하는지에 따라 subscription과 별도 event stream·queue를 구분합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. HTTP 요청·응답·오류

GraphQL 사양은 transport를 강제하지 않지만, HTTP를 사용할 때는 endpoint, media type, method, status code와 GraphQL response의 역할을 분리합니다.

### HTTP 요청 예시

```bash
curl --request POST 'https://api.example.com/graphql' \
  --header 'Authorization: Bearer SecureToken123' \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/graphql-response+json' \
  --data '{
    "operationName": "HostDetail",
    "query": "query HostDetail($id: ID!) { host(id: $id) { id hostname status } }",
    "variables": {"id": "host-42"}
  }'
```

- production에서는 원문 query를 직접 전달하는 대신 trusted document 또는 persisted query를 검토합니다.
- query operation에 GET을 허용할 수 있지만 mutation은 POST로 제한합니다.
- HTTP `Content-Type`, `Accept`, payload 크기, timeout과 압축 정책을 명시합니다.
- bearer token과 query variable에 포함될 수 있는 민감정보는 access log·trace·오류 응답에서 마스킹합니다.

### 응답 예시

정상 응답은 요청의 selection set과 같은 구조로 `data`를 반환합니다.

```json
{
  "data": {
    "host": {
      "id": "host-42",
      "hostname": "node-42.example.com",
      "status": "ACTIVE"
    }
  }
}
```

필드 실행 중 오류가 발생하면 부분 응답이 반환될 수 있습니다.

```json
{
  "data": {
    "host": {
      "id": "host-42",
      "hostname": "node-42.example.com",
      "maintenanceNote": null,
      "status": "ACTIVE"
    }
  },
  "errors": [
    {
      "message": "field unavailable",
      "path": ["host", "maintenanceNote"]
    }
  ]
}
```

> Partial response: 일부 field는 성공했지만 다른 field의 validation·resolver·권한 오류가 `errors`에 기록된 응답입니다. client는 HTTP status가 성공이어도 `errors`와 업무 결과를 함께 확인해야 합니다.

### 오류 분류

| 단계             | 예시                                  | 처리 기준                             |
|------------------|---------------------------------------|---------------------------------------|
| Network error    | TLS 오류·connection timeout           | transport retry와 endpoint 상태 확인  |
| Parse error      | 잘못된 GraphQL 문법                   | client 수정, 일반 retry 금지          |
| Validation error | schema에 없는 field·잘못된 type       | schema·client version 확인            |
| Field error      | resolver 실패·권한 거부·null 위반     | `errors.path`와 부분 응답 정책 확인   |
| Business error   | 작업 거부·quota 초과·대상 상태 불일치 | 도메인 오류 code와 재시도 가능성 확인 |

HTTP status만으로 GraphQL operation의 성공을 단정하지 않습니다. 반대로 모든 실패를 HTTP 200과 임의의 문자열로 숨기지도 말고, transport 오류·요청 오류·실행 오류의 계약을 문서화합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Resolver·N+1·페이지네이션

### N+1 문제

중첩 graph를 실행할 때 상위 object를 가져오는 1회 호출 뒤 각 하위 object마다 별도 호출이 반복되면 N+1 문제가 발생합니다.

> N+1 문제: 목록의 N개 항목을 처리하면서 목록 조회 1회와 항목별 조회 N회를 수행하는 패턴입니다. 데이터베이스 round trip과 downstream 부하가 항목 수에 따라 증가합니다.

```text
query hosts {                    backend calls
  hosts {                        1. list hosts
    owner {                      N. load one owner per host
      name
    }
  }
}
```

`hosts` 100개를 반환하는데 `owner`를 항목마다 조회하면 101회 호출이 발생할 수 있습니다. resolver를 단순히 비동기화하는 것만으로 호출 수가 줄어들지는 않습니다.

### batching과 caching

- 요청 단위로 같은 key의 하위 조회를 모아 batch query로 변환합니다.
- DataLoader 계열 구현을 사용할 때 cache 수명, tenant 경계, 권한 주체, 오류 전파를 명시합니다.
- 전역 cache에 사용자별 결과를 섞지 않고, 민감한 값은 private cache 또는 no-store를 적용합니다.
- batch 크기·동시성·downstream timeout·실패 시 부분 응답을 측정합니다.
- DataLoader가 rate limit, DB connection pool, circuit breaker를 우회하지 않도록 하위 client 정책을 공유합니다.

> DataLoader: 여러 resolver가 요청한 key를 한 번에 모아 batch 조회하고, 같은 실행 단위의 중복 key를 재사용하는 패턴입니다. 특정 언어 라이브러리의 필수 구성요소가 아니라 resolver 부하를 줄이는 구현 방식입니다.

### Cursor pagination

```graphql
type HostConnection {
  edges: [HostEdge!]!
  pageInfo: PageInfo!
}

type HostEdge {
  cursor: String!
  node: Host!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}
```

- `first`와 `after`의 최대값을 서버에서 제한합니다.
- cursor가 정렬 기준과 snapshot 경계를 안정적으로 표현하는지 확인합니다.
- 데이터 변경 중 페이지 중복·누락, cursor 만료, 권한 변경을 테스트합니다.
- offset pagination이 필요한 경우에도 최대 offset과 query cost를 제한합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 보안·인증·인가·캐시

### Query 수요 제어

GraphQL은 client가 중첩 구조와 alias를 조합할 수 있으므로 고정 endpoint의 rate limit만으로는 충분하지 않습니다.

| 통제 항목        | 기본 정책                                           |
|------------------|-----------------------------------------------------|
| depth limit      | operation과 list의 최대 중첩 깊이 제한              |
| breadth limit    | top-level field·alias·batch 개수 제한               |
| complexity limit | field별 비용 합산과 최대 budget 적용                |
| size limit       | query 문서·variable·response 최대 크기 제한         |
| rate limit       | 주체·token·IP·operation별 요청률 제한               |
| trusted document | first-party production client의 허용 operation 제한 |
| introspection    | 개발·운영 환경과 인증 주체별 노출 정책              |

> Introspection: `__schema`, `__type` 같은 meta field를 통해 실행 중인 GraphQL schema를 조회하는 기능입니다. 개발 도구와 자동 문서화에는 유용하지만, 공개 운영 endpoint의 내부 구조 노출 범위를 별도로 판단해야 합니다.

### 인증과 인가

- TLS와 인증 middleware로 요청 주체를 확인한 뒤 GraphQL context에 검증된 identity를 전달합니다.
- 인증(authentication)은 주체 확인이고, 인가(authorization)는 해당 주체가 특정 type·field·object·operation을 사용할 수 있는지 판단하는 과정입니다.
- 인가 판단은 resolver에만 흩어놓지 않고 business logic·repository 계층에서 일관되게 수행합니다.
- field별 접근 제어가 필요한 경우 `null`, 오류, 객체 필터링 중 어떤 결과를 반환할지 계약에 명시합니다.
- tenant ID, user ID, role을 client 입력만으로 신뢰하지 말고 인증 context와 서버 측 정책에서 결정합니다.
- 오류 message·path·extensions에 내부 table명, stack trace, token, secret, 다른 tenant의 식별자를 포함하지 않습니다.

### 캐시와 파일 업로드

- GraphQL response는 operation과 변수에 따라 달라지므로 cache key와 사용자·tenant 권한 범위를 함께 구성합니다.
- query에 GET을 사용하고 persisted query hash를 결합하면 HTTP cache·CDN을 검토할 수 있지만, private data가 공유 cache에 저장되지 않도록 합니다.
- client cache가 필요하면 안정적인 전역 object ID와 객체 갱신·무효화 규칙을 schema에 둡니다.
- GraphQL 언어 사양은 파일 전송 프로토콜을 하나로 정하지 않습니다. 대용량 파일은 GraphQL mutation으로 업로드하기보다 signed URL로 object storage에 직접 전송하고, mutation은 업로드 완료와 metadata만 확정하는 방식을 우선 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 관측성·스키마 운영

### 관측 필드

| 영역      | 기록할 값                                           | 주의사항                                   |
|-----------|-----------------------------------------------------|--------------------------------------------|
| 요청 식별 | request ID·trace ID·tenant ID                       | 외부에서 전달한 ID는 형식과 신뢰 경계 검증 |
| operation | operation name·normalized query hash·schema version | 원문 query·variable의 민감정보 마스킹      |
| 실행      | 전체 latency·resolver latency·error path            | field cardinality와 sampling 관리          |
| 하위 호출 | DB·HTTP·RPC 호출 수·latency·retry·timeout           | N+1과 retry storm 탐지                     |
| 자원      | CPU·memory·DB pool·queue·active subscription        | tenant·operation별 비용 분해               |
| 보안      | 인증 실패·depth 거부·complexity 초과·rate limit     | query 내용 자체를 무제한 로그하지 않음     |

### Schema lifecycle

- schema 변경을 additive change, deprecation, breaking change로 분류합니다.
- field를 추가하기 전에 nullable 여부와 resolver의 초기 운영 비용을 확인합니다.
- field를 deprecated 처리하면 client 사용량과 마지막 호출 시점을 추적하고 migration 기한을 공지합니다.
- schema snapshot과 실제 운영 endpoint의 차이를 CI에서 검출합니다.
- query corpus와 persisted document를 새 schema에 실행해 validation·authorization·성능 회귀를 확인합니다.
- gateway나 federation을 사용하는 경우 subgraph 소유자, schema composition 실패, 배포 순서와 rollback 기준을 별도로 정의합니다.

### 장애 대응 순서

```text
request ID / operation 확인
          │
          v
HTTP transport와 GraphQL errors 분리
          │
          v
query depth·cost·response size 확인
          │
          v
resolver와 downstream latency 확인
          │
          v
DB pool·rate limit·queue·subscription 상태 확인
          │
          v
문제 operation 차단 또는 persisted document rollback
```

운영자는 전체 endpoint 평균 latency만 보지 말고 operation name·query hash·field path별 p95/p99와 오류율을 확인합니다. 특정 query가 정상적인 다른 client의 capacity를 잠식하지 않도록 operation별 budget과 차단 절차를 준비합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 단계별 학습과 실무 프로젝트

### 단계별 학습

| 단계 | 학습 목표                            | 결과물                               |
|------|--------------------------------------|--------------------------------------|
| 1    | schema·scalar·object·query 이해      | `Host` 조회 schema와 query           |
| 2    | variable·input·mutation 이해         | idempotent 작업 요청과 결과 payload  |
| 3    | resolver·context·field authorization | tenant·role 기반 field 접근 제어     |
| 4    | pagination·N+1·DataLoader            | cursor pagination과 batch 호출       |
| 5    | HTTP·error·cache·subscription 운영   | timeout·partial response·재연결 정책 |
| 6    | query cost·observability·schema CI   | production guardrail과 회귀 검증     |

### 실무 프로젝트: 인벤토리 GraphQL gateway

#### 목표

여러 backend의 host, agent, task 상태를 운영 포털에 필요한 형태로 조합하는 read-heavy GraphQL gateway를 구현합니다. 변경 작업은 별도 mutation과 비동기 task 상태 조회로 분리합니다.

#### 구성

```text
Browser / CLI
     │ HTTPS POST /graphql
     v
GraphQL gateway
     ├── schema validation
     ├── authentication context
     ├── depth / complexity / rate limit
     ├── resolver + request-scoped DataLoader
     └── operation metrics and trace
          ├── inventory REST API
          ├── agent gRPC service
          └── task queue / status store
```

#### 완료 기준

- [ ] schema snapshot과 operation 문서가 저장소에서 review됩니다.
- [ ] tenant·role별 field authorization과 오류 응답이 테스트됩니다.
- [ ] 목록 query에 cursor와 최대 page size가 적용됩니다.
- [ ] N+1 호출 전후의 downstream 호출 수와 latency를 비교합니다.
- [ ] depth·breadth·complexity·payload size·rate limit 초과가 안전하게 거부됩니다.
- [ ] mutation retry와 timeout 이후 작업 상태 확인이 idempotent합니다.
- [ ] operation별 trace·metric·structured log에서 token과 민감한 variable이 마스킹됩니다.
- [ ] schema 변경 rollback과 deprecated field 제거 절차가 문서화됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. CI·운영 검증

### CI 검증 항목

| 단계                 | 검증 내용                                             |
|----------------------|-------------------------------------------------------|
| schema parse         | SDL 구문과 type reference 검사                        |
| schema compatibility | 기존 client query와 breaking change 검사              |
| query validation     | 저장된 operation의 field·argument·variable 검사       |
| security             | depth·breadth·alias·complexity·payload limit 검사     |
| resolver contract    | 권한·nullability·부분 응답·오류 path 검사             |
| performance          | representative query의 p95·호출 수·응답 크기 기준     |
| transport            | HTTPS·media type·HTTP method·timeout·compression 검사 |
| observability        | request ID·trace·operation metric·secret masking 검사 |

### HTTP smoke test

```bash
curl --fail-with-body --silent --show-error \
  --request POST 'https://api.example.com/graphql' \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/graphql-response+json' \
  --data '{"operationName":"HostDetail","query":"query HostDetail($id: ID!) { host(id: $id) { id status } }","variables":{"id":"host-42"}}'
```

검증 스크립트는 HTTP status만 확인하지 말고 JSON의 `errors` 존재 여부, 필수 field, `requestId`, 응답 크기와 latency budget을 함께 확인합니다. 운영 배포 전에는 대표 query corpus, 권한이 없는 field, 만료된 cursor, downstream timeout, 재시도 mutation, subscription 재연결을 포함한 통합 검증을 수행합니다.

### 운영 전환 체크리스트

- [ ] GraphQL schema 버전과 GraphQL over HTTP draft 지원 범위를 기록합니다.
- [ ] endpoint authentication, field authorization, tenant isolation을 검증합니다.
- [ ] query depth·breadth·complexity·rate·payload·timeout 한도를 설정합니다.
- [ ] persisted query 또는 trusted document의 등록·폐기·rollback 절차를 준비합니다.
- [ ] HTTP cache와 client cache의 민감정보 격리 정책을 확인합니다.
- [ ] resolver·DB·REST·gRPC·queue의 timeout과 전체 request budget을 연결합니다.
- [ ] operation별 SLO, 알림 임계값, 용량 상한과 차단 절차를 정의합니다.
- [ ] schema breaking change와 deprecated field의 client 영향 및 rollback을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- GraphQL Specification: [spec.graphql.org/September2025](https://spec.graphql.org/September2025/) — ★★★★☆
- GraphQL Learn: [graphql.org/learn](https://graphql.org/learn/) — ★★★☆☆
- GraphQL Serving over HTTP: [graphql.org/learn/serving-over-http](https://graphql.org/learn/serving-over-http/) — ★★★☆☆
- GraphQL Response: [graphql.org/learn/response](https://graphql.org/learn/response/) — ★★★☆☆
- GraphQL Security: [graphql.org/learn/security](https://graphql.org/learn/security/) — ★★★☆☆
- GraphQL Authorization: [graphql.org/learn/authorization](https://graphql.org/learn/authorization/) — ★★★☆☆
- GraphQL Performance: [graphql.org/learn/performance](https://graphql.org/learn/performance/) — ★★★☆☆
- GraphQL Caching: [graphql.org/learn/caching](https://graphql.org/learn/caching/) — ★★★☆☆
- GraphQL over HTTP Draft: [graphql.github.io/graphql-over-http](https://graphql.github.io/graphql-over-http/draft/) — ★★★☆☆
- [SE를 위한 REST API 가이드](rest_api_guide_for_se.md)
- [SE를 위한 gRPC 가이드](grpc_guide_for_se.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-14

**마지막 업데이트**: 2026-09-14

© 2026 siasia86. Licensed under CC BY 4.0.
