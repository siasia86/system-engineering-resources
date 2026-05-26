---
name: protocol-error-codes-official-notes
description: HTTP/SMTP/FTP/DNS 응답 코드 공식 문서 기반 참조 노트.
last_checked: 2026-05-26
sources:
  - https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
  - https://datatracker.ietf.org/doc/html/rfc9110
  - https://datatracker.ietf.org/doc/html/rfc5321
  - https://datatracker.ietf.org/doc/html/rfc959
  - https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
  - https://curl.se/libcurl/c/libcurl-errors.html
---

# 프로토콜 에러 코드 공식 문서 참조 노트

## 1. HTTP 상태 코드 (확인일: 2026-05-26)

출처: IANA HTTP Status Code Registry + RFC 9110

| 범위 | 의미          | 비고                     |
|------|---------------|--------------------------|
| 1xx  | Informational | 100~103 공식 등록        |
| 2xx  | Success       | 200~226 (일부 WebDAV)    |
| 3xx  | Redirection   | 300~308 (305 deprecated) |
| 4xx  | Client Error  | 400~451                  |
| 5xx  | Server Error  | 500~511                  |

### 주요 변경사항 (RFC 9110 기준)

- 413: `Request Entity Too Large` → `Content Too Large`
- 422: `Unprocessable Entity` → `Unprocessable Content`
- 418: `(Unused)` — "I'm a teapot"(RFC 2324)는 공식 표준 아님, IANA에서 Unused로 등록
- 510: `Not Extended` — OBSOLETED 처리됨

## 2. SMTP 응답 코드 (확인일: 2026-05-26)

출처: RFC 5321

- 4xx: 일시적 오류 — 재시도 가능
- 5xx: 영구 오류 — 재시도 불가
- 535: AUTH 실패 (RFC 4954)
- 521: 메일 수신 거부 호스트 (RFC 7504)

## 3. FTP 응답 코드 (확인일: 2026-05-26)

출처: RFC 959

- 1xx: 예비 응답 (작업 시작)
- 2xx: 완료
- 3xx: 추가 정보 필요
- 4xx: 일시적 오류
- 5xx: 영구 오류

## 4. DNS RCODE (확인일: 2026-05-26)

출처: IANA DNS Parameters

- 0~11: 기본 RCODE (RFC 1035, RFC 2136, RFC 2671)
- 16~23: TSIG/TKEY 관련 확장 RCODE (RFC 2845, RFC 2930)

## 5. 비공식 확장 코드

| 코드    | 출처       | 공식 여부 |
|---------|------------|-----------|
| 444     | Nginx      | 비공식    |
| 499     | Nginx      | 비공식    |
| 520~530 | Cloudflare | 비공식    |

- Nginx 비공식 코드: Nginx 공식 문서에 명시됨 (http://nginx.org/en/docs/http/ngx_http_log_module.html)
- Cloudflare 코드: Cloudflare 지원 문서에 명시됨 (https://developers.cloudflare.com/support/troubleshooting/cloudflare-errors/)
