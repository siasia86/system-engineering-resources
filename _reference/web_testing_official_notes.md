---
name: web-testing-official-notes
description: 웹 서버 테스트 문서(HTTP·Reverse Proxy·TLS·성능·reload·LB·캐시·요청 보안·관측성)에서 공통으로 쓰는 RFC·nginx·HAProxy·W3C·OWASP·측정 도구 공식 기준 노트.
tags:
  - web-testing
  - http
  - reverse-proxy
  - tls
  - timeout
  - load-balancer
  - cache
  - observability
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
  - https://raw.githubusercontent.com/haproxy/haproxy/v3.2.0/doc/management.txt
  - https://nginx.org/en/docs/control.html
  - https://nginx.org/en/docs/ngx_core_module.html
  - https://nginx.org/en/docs/http/ngx_http_upstream_module.html
  - https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
  - https://nginx.org/en/docs/http/ngx_http_autoindex_module.html
  - https://nginx.org/en/docs/http/ngx_http_headers_module.html
  - https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
  - https://www.rfc-editor.org/rfc/rfc9111.html
  - https://www.rfc-editor.org/rfc/rfc5861.html
  - https://www.w3.org/TR/trace-context/
  - https://github.com/OWASP/www-project-secure-headers/tree/master/ci
  - https://grafana.com/docs/k6/latest/using-k6/thresholds/
  - https://grafana.com/docs/k6/latest/using-k6/metrics/reference/
  - https://nghttp2.org/documentation/h2load-howto.html
  - https://github.com/testssl/testssl.sh/blob/3.2/doc/testssl.1.md
---

# Web Testing 공식 참조 노트

## 1. 확인 범위

`01_fundamentals/cs/web_testing/` 문서에서 쓰는 HTTP 의미·연결 관리·TLS·프록시 timeout·측정 도구 기준과, 2차 문서의 reload·Load Balancer·HTTP 캐시·요청 보안·관측성 기준을 2026-10-27에 공식 문서로 확인했습니다. 웹 서버 설치·설정 권장값은 `_reference/web_server_official_notes.md`, 부하 테스트 유형은 `_reference/load_testing_official_notes.md`를 재사용합니다.

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

## 7. 설정 다시 읽기와 종료

### nginx

| 신호      | 의미                                                      |
|-----------|-----------------------------------------------------------|
| TERM, INT | 빠른 종료                                                 |
| QUIT      | graceful 종료                                             |
| HUP       | 설정 다시 읽기, 새 worker 시작, 이전 worker graceful 종료 |
| USR1      | 로그 파일 다시 열기                                       |
| USR2      | 실행 파일 교체                                            |
| WINCH     | worker graceful 종료                                      |

- HUP을 받으면 master는 설정 문법을 검사하고 새 설정(로그 파일, listen 소켓)을 적용해 봅니다. 실패하면 변경을 되돌리고 이전 설정으로 계속 동작합니다.
- 성공하면 이전 worker는 listen 소켓을 닫고 기존 클라이언트를 끝까지 처리한 뒤 종료합니다.
- `worker_shutdown_timeout`(1.11.11 이후, 기본값 없음)을 지정하면 그 시간이 지난 뒤 남은 연결을 닫습니다.

### HAProxy

- master-worker 모드에서는 master에 SIGUSR2를 보내 설정을 다시 읽습니다(`management.txt`).
- `hard-stop-after <time>`은 soft-stop(SIGUSR1) 후 이전 프로세스가 살아 있을 최대 시간입니다. 긴 timeout의 연결이 남아도 종료를 보장합니다.

## 8. Load Balancer

### nginx upstream

| 항목              | 기본값·동작                                                            |
|-------------------|------------------------------------------------------------------------|
| 분산 방식         | 가중 round-robin (`hash`, `ip_hash`, `least_conn`, `random` 선택 가능) |
| `weight`          | 1                                                                      |
| `max_fails`       | 1 (`0`이면 실패 집계 안 함)                                            |
| `fail_timeout`    | 10초                                                                   |
| 전체 서버 실패    | 마지막 서버와의 통신 결과를 클라이언트에 반환                          |
| 서버 1대인 그룹   | `max_fails`·`fail_timeout`·`slow_start`를 무시                         |
| 능동 health check | `health_check`(별도 모듈)는 상용 구독 기능                             |

오픈소스 nginx의 서버 제외는 실제 요청 실패에 따른 수동(passive) 판정입니다. `sticky`·`drain` 등 일부 파라미터는 버전에 따라 상용·오픈소스 구분이 바뀌었으므로 대상 버전 문서를 확인합니다.

### HAProxy 서버 점검과 상태

| 항목                                        | 기본값·동작                                             |
|---------------------------------------------|---------------------------------------------------------|
| `inter`                                     | 2000ms                                                  |
| `rise`                                      | 2회 연속 성공 시 정상                                   |
| `fall`                                      | 3회 연속 실패 시 장애                                   |
| `weight`                                    | 1, 최대 256                                             |
| `set server <backend>/<server> state drain` | 분산 대상에서만 제외, 점검과 기존 세션 고정 연결은 유지 |
| `set server <backend>/<server> state maint` | 모든 트래픽과 점검 중단                                 |

## 9. HTTP 캐시 (RFC 9111, RFC 5861)

| 항목                                                 | 절                                                |
|------------------------------------------------------|---------------------------------------------------|
| 인증 요청 응답의 저장                                | RFC 9111 3.5                                      |
| `Vary`에 따른 캐시 키                                | RFC 9111 4.1                                      |
| 신선도(freshness)                                    | RFC 9111 4.2                                      |
| stale 응답 제공                                      | RFC 9111 4.2.4                                    |
| 검증(조건부 요청)                                    | RFC 9111 4.3                                      |
| `Age`                                                | RFC 9111 5.1                                      |
| `max-age`·`no-cache`·`no-store`·`private`·`s-maxage` | RFC 9111 5.2.2.1·5.2.2.4·5.2.2.5·5.2.2.7·5.2.2.10 |
| `stale-while-revalidate`                             | RFC 5861 3                                        |
| `stale-if-error`                                     | RFC 5861 4                                        |

- 공유 캐시는 `Authorization` 헤더가 있는 요청에 캐시된 응답을 쓰면 안 됩니다. 응답에 `public`·`s-maxage`·`must-revalidate` 등 공유 캐시 저장을 허용하는 지시어가 있을 때만 예외입니다.
- RFC 5861은 Informational 문서이며 `stale-if-error`의 오류로 500·502·503·504를 듭니다.
- nginx `$upstream_cache_status` 값: `MISS`, `BYPASS`, `EXPIRED`, `STALE`, `UPDATING`, `REVALIDATED`, `HIT`

## 10. 요청 보안

### nginx

| 항목                | 기본값·동작                                       |
|---------------------|---------------------------------------------------|
| `limit_req_status`  | 503 (1.3.15 이후 변경 가능)                       |
| `limit_req` `burst` | 기본 0, 초과분은 지연 처리, `nodelay`면 즉시 처리 |
| `limit_req_dry_run` | 1.17.1 이후, 실제 제한 없이 초과 요청만 집계      |
| `server_tokens`     | `on` (버전 노출)                                  |
| `autoindex`         | `off`                                             |

- `add_header`는 현재 블록에 `add_header`가 없을 때만 상위 블록 값을 상속합니다. 1.29.3부터 `add_header_inherit`(`on`·`off`·`merge`)로 상속 방식을 바꿀 수 있습니다.
- `always`(1.7.5 이후)를 지정하지 않으면 200·201·204·206·301·302·303·304·307·308 응답에만 헤더를 추가합니다.

### OWASP Secure Headers (ci 목록, 2026-10-18 갱신본)

추가 권장 헤더: `Cache-Control`, `Clear-Site-Data`, `Content-Security-Policy`, `Cross-Origin-Embedder-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy`, `Permissions-Policy`, `Referrer-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `X-DNS-Prefetch-Control`, `X-Frame-Options`, `X-Permitted-Cross-Domain-Policies`

- 제거 권장 목록에는 `Server`, `X-AspNet-Version`, `X-Powered-By` 등 88개가 있습니다.
- `X-XSS-Protection`은 추가 권장 목록에 없습니다.
- 권장 값은 애플리케이션 기능과 충돌할 수 있으므로(예: `Clear-Site-Data`, `Cross-Origin-Embedder-Policy`) 서비스 정책으로 적용 범위를 정합니다.

## 11. 관측성

- nginx `$request_id`(1.11.0 이후): 16바이트 난수의 16진수 요청 식별자
- nginx `$request_time`: 클라이언트에서 첫 바이트를 읽은 뒤 경과 시간(초, ms 해상도)
- nginx `$upstream_addr`·`$upstream_status`·`$upstream_response_time`: 재시도 시 쉼표로 구분된 여러 값
- HAProxy는 `http-request use-service prometheus-exporter`로 내장 Prometheus 지표를 제공합니다.
- HAProxy `unique-id-format`으로 요청 식별자를 만들 수 있습니다.
- W3C Trace Context Level 1(W3C Recommendation, 2021-11-23): `traceparent`·`tracestate` 헤더. `traceparent`는 `version-trace-id-parent-id-trace-flags`(2·32·16·2자리 소문자 16진수, 총 55자) 형식이며 예시는 `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`입니다.

## 12. 적용 범위와 제한

- 기본값은 확인일 기준 공식 문서 값이며, 배포판 패키지·운영 설정은 다를 수 있으므로 대상 서버의 실제 설정을 우선합니다.
- 상태 코드는 서버 구현이 RFC 정의와 다른 코드를 쓸 수 있습니다(예: nginx는 413을 "Request Entity Too Large"로 표기).
- 이 노트는 판정 기준을 제공할 뿐 특정 서비스의 SLO 수치를 정하지 않습니다.
