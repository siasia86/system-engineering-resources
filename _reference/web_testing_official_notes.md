---
name: web-testing-official-notes
description: 웹 서버·Reverse Proxy·TLS·HTTP 성능 테스트 문서에서 공통으로 쓰는 RFC·nginx·HAProxy·k6·h2load·testssl.sh 공식 기준 노트.
tags:
  - web-testing
  - http
  - reverse-proxy
  - tls
  - timeout
last_checked: 2026-10-27
sources:
  - https://www.rfc-editor.org/rfc/rfc9110.html
  - https://www.rfc-editor.org/rfc/rfc9112.html
  - https://www.rfc-editor.org/rfc/rfc9113.html
  - https://www.rfc-editor.org/rfc/rfc8446.html
  - https://www.rfc-editor.org/rfc/rfc6797.html
  - https://nginx.org/en/docs/http/ngx_http_core_module.html
  - https://nginx.org/en/docs/http/ngx_http_proxy_module.html
  - https://raw.githubusercontent.com/haproxy/haproxy/v3.2.0/doc/configuration.txt
  - https://grafana.com/docs/k6/latest/using-k6/thresholds/
  - https://grafana.com/docs/k6/latest/using-k6/metrics/reference/
  - https://nghttp2.org/documentation/h2load-howto.html
  - https://github.com/testssl/testssl.sh/blob/3.2/doc/testssl.1.md
---

# Web Testing 공식 참조 노트

## 1. 확인 범위

`01_fundamentals/cs/web_testing/` 문서에서 쓰는 HTTP 의미·연결 관리·TLS·프록시 timeout·측정 도구 기준을 2026-10-27에 공식 문서로 확인했습니다. 웹 서버 설치·설정 권장값은 `_reference/web_server_official_notes.md`, 부하 테스트 유형은 `_reference/load_testing_official_notes.md`를 재사용합니다.

## 2. HTTP 의미 (RFC 9110)

| 항목                    | RFC 9110 절 | 테스트에서 쓰는 의미                                   |
|-------------------------|-------------|--------------------------------------------------------|
| Safe methods            | 9.2.1       | GET·HEAD·OPTIONS·TRACE는 서버 상태를 바꾸지 않아야 함  |
| Idempotent methods      | 9.2.2       | Safe methods와 PUT·DELETE는 반복 요청 결과가 같아야 함 |
| Host와 :authority       | 7.2         | 가상 호스트 선택과 프록시 Host 전달 검증의 기준        |
| Via                     | 7.6.3       | 중간 프록시 경유 표시                                  |
| Retry-After             | 10.2.3      | 503 등에서 재시도 시점 안내                            |
| 408 Request Timeout     | 15.5.9      | 서버가 요청 수신을 기다리다 시간 초과                  |
| 413 Content Too Large   | 15.5.14     | 요청 본문이 서버 한도 초과                             |
| 414 URI Too Long        | 15.5.15     | 요청 대상 URI가 서버 한도 초과                         |
| 502 Bad Gateway         | 15.6.3      | 게이트웨이·프록시가 upstream에서 잘못된 응답 수신      |
| 503 Service Unavailable | 15.6.4      | 일시적 과부하·점검으로 처리 불가                       |
| 504 Gateway Timeout     | 15.6.5      | 게이트웨이·프록시가 upstream 응답을 제때 받지 못함     |

431 Request Header Fields Too Large는 RFC 9110이 아니라 RFC 6585에 정의되어 있습니다.

## 3. 연결·프로토콜 협상

- HTTP/1.1 연결 관리와 지속 연결은 RFC 9112 9장(Connection Management)에서 정의합니다.
- `https` URI에서 HTTP/2는 TLS ALPN 식별자 `h2`로 협상합니다(RFC 9113 3.2, ALPN 자체는 RFC 7301).
- TLS 1.3은 RFC 8446, TLS 1.0·1.1 사용 중단은 RFC 8996입니다.
- HSTS(`Strict-Transport-Security`)는 RFC 6797입니다.

## 4. nginx 기본값

nginx 공식 모듈 문서에서 확인한 기본값입니다.

| 지시어                        | 기본값                                 | 비고                                                         |
|-------------------------------|----------------------------------------|--------------------------------------------------------------|
| `keepalive_timeout`           | `75s`                                  | 두 번째 인자로 `Keep-Alive: timeout=` 응답 헤더 값 지정      |
| `keepalive_requests`          | `1000`                                 | 1.19.10 이전 기본값은 `100`                                  |
| `client_header_timeout`       | `60s`                                  | 만료 시 408                                                  |
| `client_body_timeout`         | `60s`                                  | 연속된 두 읽기 사이 간격, 만료 시 408                        |
| `send_timeout`                | `60s`                                  | 연속된 두 쓰기 사이 간격                                     |
| `client_max_body_size`        | `1m`                                   | 초과 시 413, `0`이면 검사 안 함                              |
| `large_client_header_buffers` | `4 8k`                                 | 요청 줄·헤더 크기 한도                                       |
| `proxy_connect_timeout`       | `60s`                                  | upstream 연결 수립                                           |
| `proxy_read_timeout`          | `60s`                                  | 응답 전체가 아니라 연속된 두 읽기 사이 간격                  |
| `proxy_send_timeout`          | `60s`                                  | 연속된 두 쓰기 사이 간격                                     |
| `proxy_http_version`          | `1.1`                                  | 1.29.7 이전 기본값은 `1.0`                                   |
| `proxy_next_upstream`         | `error timeout`                        | POST·LOCK·PATCH는 upstream에 보낸 뒤 다음 서버로 넘기지 않음 |
| `proxy_next_upstream_tries`   | `0`                                    | 횟수 제한 없음                                               |
| `proxy_set_header`            | `Host $proxy_host`, `Connection close` | 원래 Host 보존은 명시 설정 필요                              |

비멱등 요청 재시도는 `proxy_next_upstream`에 `non_idempotent`를 명시해야 허용됩니다(1.9.13 이후).

## 5. HAProxy 3.2 timeout

HAProxy 3.2.0 `doc/configuration.txt`에서 확인했습니다.

| 키워드                    | 의미                                     | 만료 시 동작                 |
|---------------------------|------------------------------------------|------------------------------|
| `timeout client`          | 클라이언트 쪽 최대 비활성 시간           | 연결 종료                    |
| `timeout server`          | 서버 쪽 최대 비활성 시간                 | 응답 전 만료 시 504          |
| `timeout connect`         | 서버 연결 수립 대기 시간                 | 재시도 또는 오류             |
| `timeout http-request`    | HTTP 요청 전체를 받을 때까지의 대기 시간 | 408                          |
| `timeout http-keep-alive` | keep-alive 연결에서 다음 요청 대기 시간  | 연결 종료                    |
| `timeout queue`           | 대기열에서 서버 슬롯을 기다리는 시간     | 503                          |
| `retries`                 | 실패 후 재시도 횟수                      | 기본은 새 연결 시도에만 적용 |

- `timeout client`·`timeout server`·`timeout connect`를 지정하지 않으면 무한 대기가 되며, 동작은 하지만 경고가 출력됩니다.
- 문서는 요청 수신 단계에서 Slowloris 같은 공격을 막으려면 `timeout http-request`를 따로 설정하는 편이 낫다고 설명합니다.
- `timeout http-keep-alive`를 지정하지 않으면 `timeout http-request` 값을 사용합니다.

## 6. 측정 도구

### k6

- 내장 HTTP 지표: `http_reqs`, `http_req_blocked`, `http_req_connecting`, `http_req_tls_handshaking`, `http_req_sending`, `http_req_waiting`(TTFB), `http_req_receiving`, `http_req_duration`, `http_req_failed`
- `http_req_duration`은 sending·waiting·receiving의 합이며 DNS 조회와 연결 수립을 포함하지 않습니다.
- threshold가 실패하면 k6는 0이 아닌 종료 코드로 끝납니다.

### h2load (nghttp2)

- `-n` 전체 요청 수, `-c` 동시 클라이언트 수, `-m` 클라이언트당 최대 동시 stream 수, `-t` 스레드 수
- `--duration`을 쓰면 `-n`은 무시됩니다.
- `--h1`은 HTTP/1.1 강제, `--alpn-list`는 ALPN 협상 목록(`h3`로 HTTP/3)입니다.
- 출력에 time for request·time for connect·time to 1st byte·req/s의 min·max·mean·sd가 포함됩니다.

### testssl.sh

- 안정판은 3.2입니다(3.3dev는 개발 branch).
- 사용법: `testssl.sh [OPTIONS] <URI>`
- `-p`(protocols), `-S`(`--server_defaults`), `-P`(server preference), `-s`(`--std`), `-h`(headers), `-U`(vulnerabilities), `--jsonfile`(`-oj`)

## 7. 적용 범위와 제한

- 기본값은 확인일 기준 공식 문서 값이며, 배포판 패키지·운영 설정은 다를 수 있으므로 대상 서버의 실제 설정을 우선합니다.
- 상태 코드는 서버 구현이 RFC 정의와 다른 코드를 쓸 수 있습니다(예: nginx는 413을 "Request Entity Too Large"로 표기).
- 이 노트는 판정 기준을 제공할 뿐 특정 서비스의 SLO 수치를 정하지 않습니다.
