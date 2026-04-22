# HTTP Methods 가이드

## 목차

| 단계 | 섹션                                                                                                                      |
|------|---------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. CRUD 매핑](#1-crud-매핑) / [2. 주요 메서드](#2-주요-메서드) / [3. 추가 메서드](#3-추가-메서드)                        |
| 비교 | [4. 속성 비교](#4-속성-비교) / [5. PUT vs PATCH](#5-put-vs-patch-차이) / [6. 멱등성](#6-멱등성-idempotent)                |
| 실전 | [7. RESTful API 설계](#7-restful-api-설계-예시) / [8. 상태 코드](#8-상태-코드와-함께-사용) / [9. 실전 예제](#9-실전-예제) |
| 보안 | [10. 보안 고려사항](#10-보안-고려사항)                                                                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 1. CRUD 매핑

| CRUD   | HTTP Method | 설명        |
|--------|-------------|-------------|
| SELECT | GET         | 리소스 조회 |
| INSERT | POST        | 리소스 생성 |
| UPDATE | PUT / PATCH | 리소스 수정 |
| DELETE | DELETE      | 리소스 삭제 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 주요 메서드

### GET
- **목적**: 리소스 조회
- **안전(Safe)**: 서버 상태 변경 없음
- **멱등성(Idempotent)**: 여러 번 호출해도 결과 동일
- **캐시 가능**: 브라우저/프록시 캐싱 지원
- **Body**: 없음 (쿼리 파라미터 사용)

```http
GET /api/products/123
GET /api/products?category=electronics&page=1&limit=20
GET /api/users/456/orders
```

**응답 예시:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "name": "노트북",
  "price": 1500000,
  "stock": 50
}
```

### POST
- **목적**: 리소스 생성
- **안전**: 아니오 (서버 상태 변경)
- **멱등성**: 없음 (여러 번 호출 시 중복 생성 가능)
- **캐시**: 일반적으로 불가능
- **Body**: 생성할 데이터 포함

```http
POST /api/products
Content-Type: application/json

{
  "name": "무선 마우스",
  "price": 35000,
  "category": "electronics"
}
```

**응답 예시:**
```http
HTTP/1.1 201 Created
Location: /api/products/124
Content-Type: application/json

{
  "id": 124,
  "name": "무선 마우스",
  "price": 35000,
  "category": "electronics",
  "createdAt": "2026-02-25T08:00:00Z"
}
```

### PUT
- **목적**: 리소스 전체 교체
- **멱등성**: 있음 (같은 요청 반복 시 결과 동일)
- **특징**: 모든 필드 필수 (누락 시 null/삭제)

```http
PUT /api/products/123
Content-Type: application/json

{
  "name": "노트북 Pro",
  "price": 2000000,
  "category": "electronics",
  "stock": 30,
  "description": "고성능 노트북"
}
```

**주의**: 필드 누락 시 해당 필드가 삭제되거나 null로 설정됨

### PATCH
- **목적**: 리소스 부분 수정
- **멱등성**: 구현에 따라 다름 (일반적으로 있음)
- **특징**: 변경할 필드만 전송

```http
PATCH /api/products/123
Content-Type: application/json

{
  "price": 1800000,
  "stock": 45
}
```

**장점**: 네트워크 대역폭 절약, 의도하지 않은 필드 변경 방지

### DELETE
- **목적**: 리소스 삭제
- **멱등성**: 있음 (이미 삭제된 리소스 재삭제 시 동일 결과)
- **Body**: 선택적 (일반적으로 없음)

```http
DELETE /api/products/123
```

**응답 예시:**
```http
HTTP/1.1 204 No Content
```

또는

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "상품이 삭제되었습니다",
  "deletedId": 123
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 추가 메서드

### HEAD
- **목적**: 메타데이터만 조회
- GET과 동일하지만 body 없이 헤더만 반환
- **사용 사례**:
  - 리소스 존재 확인
  - 파일 크기 확인 (Content-Length)
  - 최종 수정 시간 확인 (Last-Modified)
  - 대용량 파일 다운로드 전 사전 확인

```http
HEAD /api/files/report.pdf

Response:
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Length: 5242880
Last-Modified: Wed, 25 Feb 2026 08:00:00 GMT
```

### OPTIONS
- **목적**: 서버가 지원하는 메서드 확인
- CORS preflight 요청에 사용
- API 탐색 및 문서화

```http
OPTIONS /api/products/123

Response:
HTTP/1.1 200 OK
Allow: GET, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Methods: GET, PUT, PATCH, DELETE
Access-Control-Allow-Origin: *
```

**CORS Preflight 예시:**
```http
OPTIONS /api/products
Origin: https://example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

### CONNECT
- **목적**: 프록시를 통한 터널링
- 주로 HTTPS 연결에 사용
- 일반 RESTful API에서는 사용하지 않음

### TRACE
- **목적**: 요청 경로 추적 (디버깅)
- **보안 이슈**: XST(Cross-Site Tracing) 공격 가능
- **권장**: 프로덕션 환경에서 비활성화

[⬆ 목차로 돌아가기](#목차)

---

## 4. 속성 비교

| Method  | Safe | Idempotent | Cacheable | Body |
|---------|------|------------|-----------|------|
| GET     | ✓    | ✓          | ✓         | ✗    |
| POST    | ✗    | ✗          | △         | ✓    |
| PUT     | ✗    | ✓          | ✗         | ✓    |
| PATCH   | ✗    | △          | ✗         | ✓    |
| DELETE  | ✗    | ✓          | ✗         | △    |
| HEAD    | ✓    | ✓          | ✓         | ✗    |
| OPTIONS | ✓    | ✓          | ✗         | ✗    |

[⬆ 목차로 돌아가기](#목차)

---

## 5. PUT vs PATCH 차이

### PUT (전체 교체)
```http
PUT /api/products/123
Content-Type: application/json

{
  "name": "노트북 Pro",
  "price": 2000000,
  "category": "electronics",
  "stock": 30,
  "description": "고성능 노트북"
}
```
- **모든 필드 필수**
- 누락된 필드는 null 또는 기본값으로 설정됨
- 리소스 전체를 새 데이터로 교체

### PATCH (부분 수정)
```http
PATCH /api/products/123
Content-Type: application/json

{
  "price": 1800000,
  "stock": 28
}
```
- **변경할 필드만 전송**
- 나머지 필드는 기존 값 유지
- 네트워크 효율적

### 실무 선택 가이드

| 상황             | 권장 메서드 | 이유             |
|------------------|-------------|------------------|
| 전체 데이터 교체 | PUT         | 명확한 의도 표현 |
| 일부 필드만 수정 | PATCH       | 효율적, 안전     |
| 상태 변경        | PATCH       | 부분 업데이트    |
| 폼 전체 제출     | PUT         | 모든 필드 포함   |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 멱등성 (Idempotent)

**정의**: 같은 요청을 여러 번 보내도 결과가 동일한 성질

### 멱등성이 있는 메서드

```http
# GET - 항상 같은 데이터 반환
GET /api/products/123
→ 1번 호출: {id: 123, name: "노트북"}
→ 100번 호출: {id: 123, name: "노트북"} (동일)

# PUT - 최종 상태 동일
PUT /api/products/123 {"price": 2000000}
→ 1번 호출: price = 2000000
→ 100번 호출: price = 2000000 (동일)

# DELETE - 삭제 후 상태 동일
DELETE /api/products/123
→ 1번 호출: 삭제됨 (204 No Content)
→ 2번 호출: 이미 없음 (404 Not Found)
→ 결과: 리소스가 없는 상태로 동일
```

### 멱등성이 없는 메서드

```http
# POST - 호출할 때마다 새 리소스 생성
POST /api/products {"name": "마우스"}
→ 1번 호출: id=124 생성
→ 2번 호출: id=125 생성
→ 3번 호출: id=126 생성 (매번 다른 결과)
```

### 실무 적용

**재시도 로직 설계:**
- GET, PUT, DELETE: 안전하게 재시도 가능
- POST: 중복 생성 방지 필요 (Idempotency Key 사용)

**Idempotency Key 패턴 (POST):**
```http
POST /api/orders
Idempotency-Key: unique-request-id-12345
Content-Type: application/json

{
  "productId": 123,
  "quantity": 2
}
```
- 같은 Key로 재요청 시 기존 결과 반환
- 네트워크 오류 시 안전한 재시도 가능

[⬆ 목차로 돌아가기](#목차)

---

## 7. RESTful API 설계 예시

### 기본 리소스 CRUD

```http
# 상품 목록 조회 (필터링, 페이징)
GET /api/products?category=electronics&page=1&limit=20

# 특정 상품 조회
GET /api/products/123

# 상품 생성
POST /api/products

# 상품 전체 수정
PUT /api/products/123

# 상품 부분 수정 (가격만 변경)
PATCH /api/products/123

# 상품 삭제
DELETE /api/products/123
```

### 중첩 리소스 (Nested Resources)

```http
# 특정 사용자의 주문 목록
GET /api/users/456/orders

# 특정 사용자의 주문 생성
POST /api/users/456/orders

# 특정 주문의 상세 정보
GET /api/users/456/orders/789

# 주문 상태 변경
PATCH /api/users/456/orders/789
```

### 컬렉션 작업

```http
# 여러 상품 일괄 생성
POST /api/products/batch

# 여러 상품 일괄 삭제
DELETE /api/products/batch
Body: {"ids": [123, 124, 125]}

# 검색
GET /api/products/search?q=노트북&minPrice=1000000
```

### 액션 기반 엔드포인트

```http
# 주문 취소 (상태 변경)
POST /api/orders/789/cancel

# 비밀번호 재설정
POST /api/users/password-reset

# 파일 업로드
POST /api/files/upload

# 데이터 내보내기
POST /api/reports/export
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 상태 코드와 함께 사용

### GET 요청
```http
GET /api/products/123

# 성공
→ 200 OK (리소스 반환)
→ 304 Not Modified (캐시 유효)

# 실패
→ 404 Not Found (리소스 없음)
→ 401 Unauthorized (인증 필요)
→ 403 Forbidden (권한 없음)
```

### POST 요청
```http
POST /api/products

# 성공
→ 201 Created (생성 성공, Location 헤더 포함)
→ 200 OK (생성 성공, 응답 body 포함)
→ 202 Accepted (비동기 처리 시작)

# 실패
→ 400 Bad Request (잘못된 요청 데이터)
→ 409 Conflict (중복 리소스)
→ 422 Unprocessable Entity (유효성 검증 실패)
```

### PUT/PATCH 요청
```http
PUT /api/products/123
PATCH /api/products/123

# 성공
→ 200 OK (수정 성공, 응답 body 포함)
→ 204 No Content (수정 성공, body 없음)

# 실패
→ 404 Not Found (리소스 없음)
→ 400 Bad Request (잘못된 데이터)
→ 412 Precondition Failed (조건부 요청 실패)
```

### DELETE 요청
```http
DELETE /api/products/123

# 성공
→ 204 No Content (삭제 성공)
→ 200 OK (삭제 성공, 메시지 포함)

# 실패
→ 404 Not Found (이미 없음 또는 존재하지 않음)
→ 409 Conflict (삭제 불가능한 상태)
```

### 일반적인 에러 코드
```http
→ 500 Internal Server Error (서버 오류)
→ 503 Service Unavailable (서비스 일시 중단)
→ 429 Too Many Requests (요청 제한 초과)
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 실전 예제

### 예제 1: 전자상거래 상품 관리

```http
# 1. 상품 목록 조회 (페이징, 필터링)
GET /api/products?category=laptop&minPrice=1000000&page=1&limit=20

Response: 200 OK
{
  "data": [
    {"id": 1, "name": "노트북 A", "price": 1500000},
    {"id": 2, "name": "노트북 B", "price": 2000000}
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45
  }
}

# 2. 상품 상세 조회
GET /api/products/1

Response: 200 OK
{
  "id": 1,
  "name": "노트북 A",
  "price": 1500000,
  "stock": 50,
  "description": "고성능 노트북"
}

# 3. 새 상품 등록
POST /api/products
Content-Type: application/json

{
  "name": "무선 키보드",
  "price": 89000,
  "category": "accessories",
  "stock": 100
}

Response: 201 Created
Location: /api/products/3
{
  "id": 3,
  "name": "무선 키보드",
  "price": 89000,
  "category": "accessories",
  "stock": 100,
  "createdAt": "2026-02-25T08:30:00Z"
}

# 4. 재고 수량만 업데이트 (PATCH)
PATCH /api/products/3
Content-Type: application/json

{
  "stock": 95
}

Response: 200 OK
{
  "id": 3,
  "stock": 95,
  "updatedAt": "2026-02-25T09:00:00Z"
}

# 5. 상품 전체 정보 교체 (PUT)
PUT /api/products/3
Content-Type: application/json

{
  "name": "무선 키보드 Pro",
  "price": 129000,
  "category": "accessories",
  "stock": 95,
  "description": "프리미엄 무선 키보드"
}

# 6. 상품 삭제
DELETE /api/products/3

Response: 204 No Content
```

### 예제 2: 사용자 인증 및 프로필 관리

```http
# 1. 회원가입
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123!",
  "name": "홍길동"
}

Response: 201 Created
{
  "userId": 456,
  "email": "user@example.com",
  "name": "홍길동"
}

# 2. 로그인
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123!"
}

Response: 200 OK
{
  "accessToken": "eyJhbGc...",
  "refreshToken": "dGhpc2lz...",
  "expiresIn": 3600
}

# 3. 프로필 조회
GET /api/users/456
Authorization: Bearer eyJhbGc...

Response: 200 OK
{
  "id": 456,
  "email": "user@example.com",
  "name": "홍길동",
  "createdAt": "2026-01-15T10:00:00Z"
}

# 4. 프로필 부분 수정
PATCH /api/users/456
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "name": "홍길동(수정)"
}

Response: 200 OK

# 5. 비밀번호 변경
POST /api/users/456/change-password
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "currentPassword": "securePassword123!",
  "newPassword": "newSecurePass456!"
}

Response: 200 OK
{
  "message": "비밀번호가 변경되었습니다"
}
```

### 예제 3: 파일 업로드 및 관리

```http
# 1. 파일 업로드
POST /api/files/upload
Authorization: Bearer eyJhbGc...
Content-Type: multipart/form-data

file: [binary data]

Response: 201 Created
{
  "fileId": "abc123",
  "filename": "document.pdf",
  "size": 2048576,
  "url": "/api/files/abc123"
}

# 2. 파일 메타데이터 조회 (HEAD)
HEAD /api/files/abc123

Response: 200 OK
Content-Type: application/pdf
Content-Length: 2048576
Last-Modified: Wed, 25 Feb 2026 10:00:00 GMT

# 3. 파일 다운로드
GET /api/files/abc123

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
[binary data]

# 4. 파일 삭제
DELETE /api/files/abc123

Response: 204 No Content
```

- GET: URL에 민감 정보 노출 주의 (로그에 기록됨)
- POST/PUT/PATCH: HTTPS 사용 권장
- DELETE: 인증/권한 확인 필수
- TRACE: XST 공격 가능, 비활성화 권장
- OPTIONS: CORS 설정 확인

[⬆ 목차로 돌아가기](#목차)

---

## 10. 보안 고려사항

### 1. GET 요청 보안
```http
# 나쁜 예: URL에 민감 정보 노출
GET /api/users?password=secret123&ssn=123-45-6789

# 좋은 예: 인증 토큰 사용
GET /api/users/profile
Authorization: Bearer eyJhbGc...
```

**주의사항:**
- URL은 서버 로그, 브라우저 히스토리, 프록시 로그에 기록됨
- 민감한 정보는 절대 쿼리 파라미터로 전송 금지
- 인증 정보는 Authorization 헤더 사용

### 2. POST/PUT/PATCH 보안
```http
# HTTPS 사용 필수
POST https://api.example.com/api/users
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "hashed_password"
}
```

**권장사항:**
- 모든 데이터 전송 시 HTTPS 사용
- 비밀번호는 클라이언트에서 해싱하지 말고 서버에서 처리
- SQL Injection 방지: 파라미터 바인딩 사용
- XSS 방지: 입력 데이터 검증 및 이스케이프

### 3. DELETE 보안
```http
# 인증 및 권한 확인 필수
DELETE /api/products/123
Authorization: Bearer eyJhbGc...
```

**체크리스트:**
- 인증된 사용자만 삭제 가능
- 소유자 또는 관리자 권한 확인
- 중요 리소스는 소프트 삭제 고려
- 삭제 전 확인 단계 추가 (2단계 인증)

### 4. CORS 설정
```javascript
// 서버 설정 예시 (Node.js/Express)
app.use(cors({
  origin: 'https://trusted-domain.com',  // 특정 도메인만 허용
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));
```

**주의사항:**
- `Access-Control-Allow-Origin: *` 사용 지양
- 신뢰할 수 있는 도메인만 허용
- credentials 사용 시 와일드카드 불가

### 5. Rate Limiting
```http
# 요청 제한 초과 시
Response: 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1708851600
```

**구현 권장:**
- API 키 또는 IP 기반 제한
- 인증된 사용자: 시간당 1000회
- 비인증 사용자: 시간당 100회

### 6. 입력 검증
```javascript
// 서버 측 검증 예시
app.post('/api/products', (req, res) => {
  const { name, price, stock } = req.body;
  
  // 필수 필드 검증
  if (!name || !price) {
    return res.status(400).json({
      error: 'name과 price는 필수입니다'
    });
  }
  
  // 타입 검증
  if (typeof price !== 'number' || price < 0) {
    return res.status(400).json({
      error: 'price는 0 이상의 숫자여야 합니다'
    });
  }
  
  // 길이 검증
  if (name.length > 100) {
    return res.status(400).json({
      error: 'name은 100자를 초과할 수 없습니다'
    });
  }
  
  // 처리...
});
```

### 7. TRACE 메서드 비활성화
```nginx
# Nginx 설정
location / {
    limit_except GET POST PUT PATCH DELETE HEAD OPTIONS {
        deny all;
    }
}
```

**이유:**
- XST(Cross-Site Tracing) 공격 방지
- 민감한 헤더 정보 노출 방지

### 8. 인증 토큰 관리
```http
# Bearer 토큰 사용
GET /api/protected-resource
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 쿼리 파라미터로 토큰 전송 금지
GET /api/protected-resource?token=eyJhbGc...
```

**권장사항:**
- JWT 사용 시 짧은 만료 시간 설정 (15분~1시간)
- Refresh Token으로 갱신
- HttpOnly 쿠키 사용 고려 (XSS 방지)

### 9. API 버전 관리
```http
# URL 버전
GET /api/v1/products

# 헤더 버전
GET /api/products
Accept: application/vnd.api.v1+json
```

**장점:**
- 하위 호환성 유지
- 점진적 마이그레이션 가능

### 10. 에러 메시지 처리
```http
# 나쁜 예: 내부 정보 노출
Response: 500 Internal Server Error
{
  "error": "SQL Error: SELECT * FROM users WHERE id=123 failed",
  "stack": "at Database.query (/app/db.js:45:12)..."
}

# 좋은 예: 일반적인 메시지
Response: 500 Internal Server Error
{
  "error": "서버 오류가 발생했습니다",
  "errorCode": "INTERNAL_ERROR",
  "requestId": "req-abc123"
}
```

**원칙:**
- 클라이언트에게 최소한의 정보만 제공
- 상세 에러는 서버 로그에만 기록
- 에러 코드로 문제 추적 가능하게 설계

[⬆ 목차로 돌아가기](#목차)

---

## 11. 추가 학습 자료

### HTTP 명세

| RFC      | 내용                           |
|----------|--------------------------------|
| RFC 7231 | HTTP/1.1 Semantics and Content |
| RFC 5789 | PATCH Method for HTTP          |
| RFC 7540 | HTTP/2                         |

### 실습 도구

| 도구     | 설명                          |
|----------|-------------------------------|
| Postman  | API 테스트 도구               |
| curl     | 커맨드라인 HTTP 클라이언트    |
| HTTPie   | 사용자 친화적 HTTP 클라이언트 |
| Insomnia | REST API 클라이언트           |

[⬆ 목차로 돌아가기](#목차)

---

## 12. 요약

| 메서드  | 용도        | 멱등성 | 안전 | Body | 주요 상태 코드 |
|---------|-------------|--------|------|------|----------------|
| GET     | 조회        | ✓      | ✓    | ✗    | 200, 404       |
| POST    | 생성        | ✗      | ✗    | ✓    | 201, 400       |
| PUT     | 전체 수정   | ✓      | ✗    | ✓    | 200, 204       |
| PATCH   | 부분 수정   | ✓      | ✗    | ✓    | 200, 204       |
| DELETE  | 삭제        | ✓      | ✗    | △    | 204, 404       |
| HEAD    | 메타데이터  | ✓      | ✓    | ✗    | 200            |
| OPTIONS | 메서드 확인 | ✓      | ✓    | ✗    | 200            |

[⬆ 목차로 돌아가기](#목차)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---
**작성일**: 2026-04-22
**마지막 업데이트**: 2026-04-22

© 2026 siasia86. Licensed under CC BY 4.0.
