---
name: rest-api-official-notes
description: HTTP 의미론·Problem Details·PATCH·OpenAPI 공식 문서 기반 REST API 참조 노트.
tags:
  - rest
  - api
  - http
  - openapi
  - problem-details
last_checked: 2026-09-11
sources:
  - https://www.rfc-editor.org/rfc/rfc9110
  - https://www.rfc-editor.org/rfc/rfc9457
  - https://www.rfc-editor.org/rfc/rfc5789
  - https://www.iana.org/assignments/http-methods/http-methods.xhtml
  - https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
  - https://spec.openapis.org/oas/latest.html
---

# REST API 공식 참조 노트

## 1. 범위와 버전 기준

- REST는 단일 제품이나 단일 wire protocol의 버전명이 아니라 분산 시스템을 위한 아키텍처 스타일입니다.
- HTTP 기반 REST API의 공통 의미론은 HTTP Semantics인 RFC 9110을 기준으로 확인합니다.
- 부분 수정 메서드 `PATCH`는 RFC 5789를 기준으로 확인합니다.
- HTTP API 오류의 표준 표현은 RFC 9457의 Problem Details를 기준으로 확인합니다. RFC 9457은 RFC 7807을 대체합니다.
- 최신 OpenAPI Specification 페이지에서 확인되는 버전은 `3.2.0`입니다. OpenAPI는 HTTP API의 계약·문서화 형식이며 REST 자체의 필수 규격은 아닙니다.

## 2. HTTP와 REST API의 관계

- HTTP 요청은 method, target resource, header field, content로 구성됩니다.
- HTTP 응답은 status code, header field, content로 구성됩니다.
- URI는 대상 resource를 식별하고, representation은 해당 resource의 상태를 표현합니다.
- HTTP method 의미론은 URI 이름보다 우선합니다. URI에 동사처럼 보이는 문자열이 있어도 method의 안전성·멱등성 규칙을 임의로 바꾸지 않습니다.
- REST API 설계에서는 resource 식별, representation, method semantics, status code, content negotiation, cache semantics를 함께 정의합니다.

> representation: resource의 현재 또는 특정 시점 상태를 전달하는 표현입니다. JSON만을 의미하지 않으며 media type과 content negotiation에 따라 XML, binary 등 다른 형식도 사용할 수 있습니다.

## 3. 주요 HTTP 메서드 의미론

| 메서드  | 공식 의미                            | Safe | Idempotent  | REST API 주요 사용              |
|---------|--------------------------------------|------|-------------|---------------------------------|
| GET     | 현재 representation 조회             | O    | O           | collection·resource 조회        |
| HEAD    | GET과 같은 header 확인, content 없음 | O    | O           | 존재·메타데이터 확인            |
| POST    | 대상 resource에 데이터 처리 요청     | X    | X           | 생성·명령·하위 resource 처리    |
| PUT     | 대상 resource 상태 대체              | X    | O           | 전체 상태 대체·멱등 upsert      |
| PATCH   | 대상 resource 부분 수정              | X    | 설계에 따라 | 부분 변경 문서 적용             |
| DELETE  | 대상 resource 삭제                   | X    | O           | resource 삭제                   |
| OPTIONS | 대상 통신 옵션 확인                  | O    | O           | 지원 method·CORS preflight 확인 |

- safe는 서버 상태 변경이 없다는 뜻이 아니라, 클라이언트가 의도한 의미상 상태 변경을 요청하지 않는다는 의미입니다. 서버는 로깅·통계 같은 부수 효과를 가질 수 있습니다.
- idempotent는 동일 요청을 한 번 또는 여러 번 수행한 결과의 의도된 효과가 같다는 의미이며, 모든 응답이 동일하다는 뜻은 아닙니다.
- `PATCH`를 재시도할 때는 patch 문서와 서버 구현이 멱등인지 별도로 판단합니다.

## 4. Representation·content negotiation·cache

- request와 response content의 의미는 method와 status code에 의해 결정됩니다.
- `Content-Type`은 content의 media type을 나타내고, `Accept` 등 request header는 선호 representation 선택에 사용됩니다.
- 여러 representation을 제공하는 API는 content negotiation 결과와 오류 시 반환 형식을 문서화합니다.
- HTTP cache는 동일한 요청에 사용할 수 있는 이전 response를 저장해 지연과 네트워크 사용량을 줄입니다.
- `Cache-Control`, `ETag`, `Last-Modified`, conditional request를 resource의 변경 빈도와 일관성 요구에 맞게 설계합니다.
- 인증 정보나 사용자별 응답은 cache 공유 가능성과 개인정보 노출을 확인한 뒤 cache 정책을 설정합니다.

## 5. Status code와 오류 표현

- HTTP status code는 응답의 일반적인 처리 결과와 의미를 전달합니다.
- API는 성공·리다이렉션·클라이언트 오류·서버 오류를 표준 status code 의미에 맞게 사용하고, 기존 status code의 의미를 재정의하지 않습니다.
- RFC 9457 Problem Details는 HTTP API 오류의 machine-readable 세부 정보를 전달하기 위한 공통 형식입니다.

주요 Problem Details 멤버는 다음과 같습니다.

| 멤버       | 의미                                      |
|------------|-------------------------------------------|
| `type`     | 문제 유형을 식별하는 URI                  |
| `title`    | 문제 유형의 사람이 읽을 수 있는 요약      |
| `status`   | 발생한 HTTP status code                   |
| `detail`   | 해당 발생 건에 대한 상세 설명             |
| `instance` | 특정 문제 발생을 식별하는 URI             |
| 확장 멤버  | API가 정의하는 추가 machine-readable 정보 |

- JSON 표현의 media type은 `application/problem+json`입니다.
- Problem Details를 사용할 때도 HTTP status code를 올바르게 설정합니다. 오류 세부 정보를 위해 status code 의미를 바꾸지 않습니다.
- validation 오류처럼 여러 세부 오류가 필요한 경우 확장 멤버의 구조와 민감정보 노출 범위를 계약으로 정의합니다.

## 6. 계약·문서화와 OpenAPI

- OpenAPI는 HTTP API의 paths, operations, parameters, request body, responses, security schemes 등을 기계 판독 가능한 형식으로 설명합니다.
- OpenAPI 문서와 실제 서버 동작의 차이를 줄이기 위해 schema, status code, content type, authentication, pagination, error response를 함께 검증합니다.
- OpenAPI의 `3.2.0` 버전을 사용하더라도 대상 언어·gateway·validator·code generator의 지원 범위를 확인합니다.
- OpenAPI는 API 계약 문서화 도구이며, 모든 API가 REST 제약 조건을 충족한다는 보증은 아닙니다.

## 7. 보안과 운영 확인 항목

| 확인 항목 | 확인 기준                                         |
|-----------|---------------------------------------------------|
| 전송 보호 | 운영 환경의 HTTPS·인증서·TLS 설정                 |
| 인증·인가 | authentication과 resource 권한 검증               |
| 입력 검증 | schema·크기·content type·경로 parameter 검증      |
| 오류 응답 | 표준 status code·Problem Details·민감정보 제거    |
| 재시도    | method 멱등성·request 중복 처리·backoff           |
| 캐시      | `Cache-Control`·validator·사용자별 응답 분리      |
| 계약 검증 | OpenAPI와 실제 request·response의 지속적 대조     |
| 관측성    | status·latency·request ID·rate limit·trace        |
| 호환성    | 기존 field·URI·status·media type 변경의 영향 분석 |

## 8. 공식 확인 항목

- HTTP method와 status code의 의미는 RFC 9110 및 IANA registry에서 확인합니다.
- 부분 수정 semantics는 RFC 5789와 대상 API의 patch 문서 형식에서 확인합니다.
- 오류 응답 형식은 RFC 9457 적용 여부와 `application/problem+json` 계약을 확인합니다.
- OpenAPI 문서의 specification version과 구현 도구의 지원 범위를 릴리스별로 확인합니다.
