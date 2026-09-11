# SE를 위한 REST API 가이드
<!-- reference: _reference/rest_api_official_notes.md -->

시스템 엔지니어 관점에서 REST API를 설계·운영하는 가이드입니다. HTTP 의미론, resource와 representation, 오류 계약, OpenAPI, 인증·캐시·재시도에 초점을 맞춥니다.

## 목차

| 섹션                                                                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. REST API 개요](#1-rest-api-개요) / [2. SE 활용 판단](#2-se-활용-판단) / [3. Resource와 URI 설계](#3-resource와-uri-설계)                                       |
| [4. HTTP 메서드와 상태 코드](#4-http-메서드와-상태-코드) / [5. Representation·캐시·조건부 요청](#5-representation캐시조건부-요청) / [6. 오류 계약](#6-오류-계약)   |
| [7. OpenAPI와 버전 관리](#7-openapi와-버전-관리) / [8. 보안·신뢰성·관측성](#8-보안신뢰성관측성) / [9. 단계별 학습과 실무 프로젝트](#9-단계별-학습과-실무-프로젝트) |
| [10. CI·운영 검증](#10-ci운영-검증)                                                                                                                                |

---

## 1. REST API 개요

REST는 단일 제품이나 단일 프로토콜 버전이 아니라 분산 시스템을 설계하는 아키텍처 스타일입니다. HTTP 기반 API에서는 RFC 9110의 method, status code, header, content와 representation 의미론을 설계의 기준으로 삼습니다.

> Representation: resource의 상태를 전달하는 표현입니다. JSON만을 뜻하지 않으며 media type과 content negotiation에 따라 XML, text, binary 등으로 제공될 수 있습니다.

### HTTP API의 기본 흐름

```text
Client
  │  method + URI + headers + content
  v
API Gateway / Load Balancer
  │
  v
Origin Server
  │  status + headers + representation
  v
Client
```

### 핵심 구성

| 구성           | 설계 질문                                                |
|----------------|----------------------------------------------------------|
| resource       | 무엇을 식별하고 수명주기를 관리하는가?                   |
| URI            | resource identity와 계층을 어떻게 표현하는가?            |
| method         | 조회·생성·대체·부분 수정·삭제 의미가 무엇인가?           |
| representation | 어떤 media type과 schema를 제공하는가?                   |
| status         | 성공·실패·재시도 가능성을 어떤 상태 코드로 표현하는가?   |
| contract       | client가 의존할 field·header·status를 어디에 기록하는가? |

[⬆ 목차로 돌아가기](#목차)

---

## 2. SE 활용 판단

### 적합한 영역

| 영역          | REST API 활용            | 운영상 핵심                    |
|---------------|--------------------------|--------------------------------|
| 관리 API      | 서버·계정·정책·작업 CRUD | 권한·감사·idempotency          |
| 자동화 API    | 배포·백업·점검 실행      | timeout·job status·재시도      |
| 외부 연동     | cloud·SaaS·파트너 API    | contract·rate limit·호환성     |
| 진단 endpoint | health·metrics·debug     | 노출 범위·인증·cache           |
| 비동기 작업   | 요청 접수 후 job 조회    | `202 Accepted`와 상태 resource |

### 다른 API 스타일과 역할 분담

| 요구사항                            | 우선 검토                 |
|-------------------------------------|---------------------------|
| 브라우저·운영자·외부 개발자 접근    | REST API                  |
| 강한 타입 내부 RPC와 streaming      | gRPC                      |
| 단일 endpoint에서 선택적 field 조회 | GraphQL 검토              |
| 서버 이벤트의 비동기 전달           | webhook·SSE·message queue |

REST API를 사용한다고 해서 endpoint를 단순히 동사 목록으로 만들면 안 됩니다. HTTP method의 의미, 상태 코드, resource lifecycle, 인증 경계를 함께 정의해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Resource와 URI 설계

### Resource 모델

서버 inventory API를 예로 들면 다음처럼 resource와 하위 관계를 나눌 수 있습니다.

```text
/accounts/{account_id}
/accounts/{account_id}/hosts
/accounts/{account_id}/hosts/{host_id}
/accounts/{account_id}/hosts/{host_id}/jobs
/accounts/{account_id}/jobs/{job_id}
```

```bash
curl --fail-with-body \
  -H 'Accept: application/json' \
  https://api.example.com/v1/accounts/Secureuser123/hosts
```

- URI는 안정적인 identity를 표현하고, 동작은 method와 request content로 표현합니다.
- collection과 개별 resource의 response schema를 구분합니다.
- 하위 resource를 무한히 중첩하지 않고 실제 수명주기와 권한 경계를 반영합니다.
- URI에 password, token, 개인정보를 넣지 않습니다.
- public URI를 변경해야 한다면 redirect, alias, deprecation 기간을 계약으로 정의합니다.

### Pagination과 filtering

| 기능            | 계약 항목                                                 |
|-----------------|-----------------------------------------------------------|
| pagination      | cursor 또는 page 방식, page size 최대값, 다음 페이지 표현 |
| filtering       | 허용 field·연산자·기본 범위·입력 검증                     |
| sorting         | 허용 sort key·방향·동일 key tie-breaker                   |
| field selection | 반환 field 제한과 권한 처리                               |
| bulk request    | 부분 성공·실패 항목·재시도 기준                           |

페이지 결과의 전체 개수가 expensive하거나 변동하는 경우 cursor 기반 방식을 검토합니다. pagination token에 내부 DB 정보나 권한 우회에 사용할 수 있는 값을 직접 노출하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. HTTP 메서드와 상태 코드

### 메서드 의미론

| 메서드    | 의미                      | Safe | Idempotent  | 주요 사용                    |
|-----------|---------------------------|------|-------------|------------------------------|
| `GET`     | representation 조회       | O    | O           | collection·resource 조회     |
| `HEAD`    | GET의 header 확인         | O    | O           | 존재·metadata 확인           |
| `POST`    | 대상 resource에 처리 요청 | X    | X           | 생성·명령·하위 resource 처리 |
| `PUT`     | 대상 resource 상태 대체   | X    | O           | 전체 대체·멱등 upsert        |
| `PATCH`   | 대상 resource 부분 수정   | X    | 설계에 따라 | 부분 변경 적용               |
| `DELETE`  | 대상 resource 삭제        | X    | O           | resource 삭제                |
| `OPTIONS` | 통신 옵션 확인            | O    | O           | 지원 method·preflight        |

- safe는 부수 효과가 전혀 없다는 뜻이 아니라, client가 상태 변경을 의도하지 않는 method라는 의미입니다.
- idempotent는 같은 요청의 의도된 효과를 여러 번 적용해도 같다는 뜻이며, 응답 body와 status가 매번 같다는 뜻은 아닙니다.
- `PATCH`는 patch 문서 형식과 서버 구현이 멱등인지 확인한 뒤 자동 재시도를 허용합니다.

### 상태 코드 설계

| 범주        | 예시                                            | 운영 의미                      |
|-------------|-------------------------------------------------|--------------------------------|
| 성공        | `200`, `201`, `202`, `204`                      | 조회·생성·접수·content 없음    |
| 리다이렉션  | `301`, `302`, `304`                             | resource 이동·cache 재사용     |
| client 오류 | `400`, `401`, `403`, `404`, `409`, `422`, `429` | 입력·인증·권한·충돌·rate limit |
| server 오류 | `500`, `502`, `503`, `504`                      | 서버·gateway·upstream 장애     |

기존 HTTP status code의 의미를 API 전용 오류 코드처럼 재정의하지 않습니다. 애플리케이션별 세부 원인은 response body의 오류 계약으로 전달합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Representation·캐시·조건부 요청

### Content negotiation

```http
GET /v1/hosts/host-001 HTTP/1.1
Host: api.example.com
Accept: application/json
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "host-001-v7"
Cache-Control: private, max-age=30

{
  "id": "host-001",
  "hostname": "node-01.example.com",
  "status": "ready"
}
```

- `Content-Type`은 현재 content의 media type을 나타냅니다.
- `Accept`는 client가 선호하는 response representation을 표현합니다.
- 지원하지 않는 media type, version, encoding에 대한 응답을 계약으로 정의합니다.
- response schema 변경 시 기존 client가 알 수 없는 field를 만났을 때의 처리도 확인합니다.

### Cache와 조건부 요청

| 항목            | 활용                                      |
|-----------------|-------------------------------------------|
| `Cache-Control` | public·private·no-store·max-age 정책 지정 |
| `ETag`          | representation version validator          |
| `Last-Modified` | 시간 기반 변경 검증                       |
| `If-None-Match` | 변경되지 않은 경우 `304` 활용             |
| `If-Match`      | 동시 수정 방지와 optimistic concurrency   |

인증된 사용자별 응답이나 민감한 운영 정보는 공유 cache에 저장되지 않도록 cache 정책을 명시합니다. `ETag`나 `Last-Modified`만으로 접근 권한을 대체하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 오류 계약

### Problem Details

RFC 9457은 HTTP API 오류의 machine-readable 세부 정보를 전달하는 Problem Details 형식을 정의합니다.

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/invalid-host",
  "title": "Host validation failed",
  "status": 422,
  "detail": "hostname is required",
  "instance": "/v1/problems/req-7f8a"
}
```

| 멤버       | 용도                                       |
|------------|--------------------------------------------|
| `type`     | 문제 유형을 식별하는 URI                   |
| `title`    | 사람이 읽을 수 있는 문제 요약              |
| `status`   | 발생한 HTTP status code                    |
| `detail`   | 해당 요청의 상세 설명                      |
| `instance` | 특정 문제 발생을 식별하는 URI              |
| extension  | validation field, retry hint 등 API별 정보 |

### 오류 설계 기준

- status code는 HTTP 의미론에 맞추고 세부 원인은 Problem Details로 전달합니다.
- `detail`에 token, password, 내부 stack trace, SQL query, host secret을 넣지 않습니다.
- validation 오류의 field path와 오류 코드 형식을 안정적인 contract로 정의합니다.
- 오류 response도 `Content-Type`, correlation ID, cache 정책을 명시합니다.
- retry 가능한 오류와 client 수정이 필요한 오류를 구분합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. OpenAPI와 버전 관리

### OpenAPI 계약

OpenAPI는 HTTP API의 path, operation, parameter, request body, response, security scheme를 기계 판독 가능한 문서로 표현합니다.

```yaml
openapi: 3.2.0
info:
  title: Host Inventory API
  version: 1.0.0
paths:
  /v1/hosts/{host_id}:
    get:
      parameters:
        - name: host_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Host returned
        '404':
          description: Host not found
```

OpenAPI는 계약·문서화 형식이지 REST 제약 조건을 자동으로 보장하는 도구는 아닙니다. 실제 server behavior와 schema, status code, content type, authentication을 지속적으로 대조합니다.

### 버전 관리

| 변경                           | 권장 처리                                    |
|--------------------------------|----------------------------------------------|
| response에 optional field 추가 | 구형 client의 unknown field 처리 확인        |
| required request field 추가    | 새 version 또는 호환 가능한 기본값 검토      |
| field 의미 변경                | 기존 field 재사용 대신 새 field·version 사용 |
| URI 구조 변경                  | alias·redirect·deprecation 기간 운영         |
| status code 변경               | client retry·error branching 영향 분석       |
| media type 변경                | content negotiation과 client capability 확인 |

URI에 `v1`을 넣는 방식은 하나의 선택일 뿐입니다. header·media type versioning을 사용하더라도 routing, documentation, deprecation, rollback 정책이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 보안·신뢰성·관측성

### 보안

- 운영 API는 HTTPS와 인증서 검증을 사용합니다.
- authentication과 resource authorization을 분리해 모든 resource 접근을 검증합니다.
- request body, query, path parameter의 schema와 크기를 검증합니다.
- rate limit, pagination limit, upload size, timeout을 명시합니다.
- API key·token·개인정보를 URI, access log, 오류 body에 기록하지 않습니다.
- CORS, CSRF, SSRF, request smuggling 등 배치 환경에 맞는 웹 공격 경계를 검토합니다.

### 신뢰성과 재시도

- method의 idempotency와 작업의 중복 처리 방식을 기준으로 retry 가능 여부를 정합니다.
- 긴 작업은 요청을 오래 유지하기보다 job resource를 만들고 `202 Accepted`와 상태 조회를 사용합니다.
- client timeout, gateway timeout, upstream timeout을 하나의 요청 예산으로 조정합니다.
- `429`, `503`, `Retry-After` 정책을 문서화하고 exponential backoff를 적용합니다.
- optimistic concurrency가 필요하면 `ETag`와 `If-Match`를 사용해 lost update를 줄입니다.

### 관측성

| 항목    | 기록·측정                                  |
|---------|--------------------------------------------|
| request | method·route template·status·request ID    |
| latency | gateway·application·upstream 구간별 시간   |
| traffic | request rate·response size·rate limit 거부 |
| error   | Problem type·status·dependency 오류        |
| trace   | trace ID·span ID·upstream 연계             |
| audit   | actor·resource·action·결과·시각            |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 단계별 학습과 실무 프로젝트

| 단계  | 학습 주제                              | 산출물                         |
|-------|----------------------------------------|--------------------------------|
| 1단계 | HTTP method·status·header·content      | curl 기반 조회·수정 API        |
| 2단계 | resource·pagination·filter·idempotency | inventory management API       |
| 3단계 | Problem Details·OpenAPI·contract test  | 문서와 실제 응답 검증 pipeline |
| 4단계 | auth·TLS·cache·conditional request     | 운영 보안과 동시성 적용        |
| 5단계 | gateway·rate limit·trace·deprecation   | 장기 운영 가능한 public API    |

### SE 실무 프로젝트

- host inventory 조회·등록·상태 변경 API 작성.
- 비동기 patch 작업을 job resource로 분리하고 상태 조회 API 구현.
- `ETag`·`If-Match`를 사용한 동시 설정 변경 방지.
- Problem Details와 OpenAPI를 기준으로 client contract test 작성.
- `429`, `502`, `503`, `504` 장애를 주입해 timeout·retry 동작 확인.

[⬆ 목차로 돌아가기](#목차)

---

## 10. CI·운영 검증

```bash
curl --fail-with-body \
  -H 'Accept: application/json' \
  https://api.example.com/v1/health
```

CI와 배포 검증에는 다음 항목을 포함합니다.

1. OpenAPI 문서의 syntax와 schema 검증.
2. 실제 route·method·parameter·status code와 문서의 일치 확인.
3. 정상·입력 오류·권한 오류·충돌·rate limit 응답의 contract test.
4. Problem Details의 media type과 필수 멤버 확인.
5. 인증서·authentication·authorization 실패 동작 확인.
6. cache validator, conditional request, `ETag` 충돌 검증.
7. timeout·retry·upstream 장애와 rollback 동작 확인.
8. access log·trace·audit log의 민감정보 노출 여부 확인.

문서 변경을 코드 변경과 동일한 review·release gate에서 검증하면 client가 의존하는 계약의 drift를 줄일 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [REST API 공식 참조 노트](../../_reference/rest_api_official_notes.md)
- REST API Semantics: [rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110) — ★★★★☆
- Problem Details for HTTP APIs: [rfc-editor.org/rfc/rfc9457](https://www.rfc-editor.org/rfc/rfc9457) — ★★★★☆
- PATCH Method: [rfc-editor.org/rfc/rfc5789](https://www.rfc-editor.org/rfc/rfc5789) — ★★★☆☆
- OpenAPI Specification: [spec.openapis.org/oas/latest](https://spec.openapis.org/oas/latest.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-11

**마지막 업데이트**: 2026-09-11

© 2026 siasia86. Licensed under CC BY 4.0.
