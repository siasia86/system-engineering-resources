---
name: http-official-notes
description: HTTP 의미·판(1.1·2·3), HTTPS 관련 RFC(TLS 1.3, ALPN, HSTS, TLS 1.0·1.1 중단)와 컨테이너 확인 결과 정리.
tags:
  - http
  - https
  - tls
  - rfc
last_checked: 2026-11-23
sources:
  - https://www.rfc-editor.org/rfc/rfc9110
  - https://www.rfc-editor.org/rfc/rfc9111
  - https://www.rfc-editor.org/rfc/rfc9112
  - https://www.rfc-editor.org/rfc/rfc9113
  - https://www.rfc-editor.org/rfc/rfc9114
  - https://www.rfc-editor.org/rfc/rfc9846
  - https://www.rfc-editor.org/rfc/rfc7301
  - https://www.rfc-editor.org/rfc/rfc6797
  - https://www.rfc-editor.org/rfc/rfc8996
---

# HTTP·HTTPS 공식 자료 참조 노트

## 1. 기준 RFC (rfc-editor.org 메타데이터, 2026-11-23)

| RFC  | 발행    | 제목                                                    | 비고                                   |
|------|---------|---------------------------------------------------------|----------------------------------------|
| 9110 | 2022-06 | HTTP Semantics                                          | 메서드·상태 코드·헤더 의미 (판과 무관) |
| 9111 | 2022-06 | HTTP Caching                                            |                                        |
| 9112 | 2022-06 | HTTP/1.1                                                | 메시지 문법                            |
| 9113 | 2022-06 | HTTP/2                                                  |                                        |
| 9114 | 2022-06 | HTTP/3                                                  | QUIC 위                                |
| 9846 | 2026-07 | The Transport Layer Security (TLS) Protocol Version 1.3 | RFC 8446·5246 등을 대체(obsoletes)     |
| 7301 | 2014-07 | TLS Application-Layer Protocol Negotiation (ALPN)       | h2·http/1.1 협상                       |
| 6797 | 2012-11 | HTTP Strict Transport Security (HSTS)                   |                                        |
| 8996 | 2021-03 | Deprecating TLS 1.0 and TLS 1.1                         |                                        |

## 2. 컨테이너 확인 (2026-11-23)

구성: `nginx:1.30`(80은 301로 HTTPS 전환, 443은 `http2 on`, `ssl_protocols TLSv1.2 TLSv1.3`, HSTS 헤더), 자체 서명 P-256 인증서, 클라이언트 `curlimages/curl:8.23.0`, `alpine/openssl`.

| 확인                                     | 결과                                                                                                 |
|------------------------------------------|------------------------------------------------------------------------------------------------------|
| `http://` 요청                           | `301`, `Location: https://.../a`                                                                     |
| 기본 HTTPS 요청                          | `200`, `http_version` 2                                                                              |
| `--http1.1`                              | `200`, 1.1                                                                                           |
| 응답 헤더                                | `HTTP/2 200`, `strict-transport-security: max-age=31536000`                                          |
| CA 지정 없이 요청                        | curl 종료 코드 60, `self-signed certificate (18)`                                                    |
| `openssl s_client -alpn h2`              | `ALPN protocol: h2`, `TLSv1.3`, `TLS_AES_256_GCM_SHA384`                                             |
| `openssl s_client -tls1_1` (보안 수준 0) | 서버가 `alert protocol version` (alert 70)으로 거절                                                  |
| `openssl s_client -tls1_2`               | `TLSv1.2` 협상 성공                                                                                  |
| curl `--tls-max 1.1`                     | 종료 코드 35, `no protocols available` — 서버가 아니라 클라이언트(OpenSSL 3.5 기본 보안 수준)가 거절 |

- `curlimages/curl:8.23.0`·`8.17.0` 모두 Features에 HTTP3이 없어 HTTP/3은 확인하지 못했습니다.
