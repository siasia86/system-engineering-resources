# HTTP와 HTTPS
<!-- reference: _reference/http_official_notes.md -->

웹과 API가 쓰는 HTTP의 메시지 구조, 판(1.1·2·3)의 차이, 그리고 TLS로 보호하는 HTTPS의 흐름을 한 문서로 정리했습니다. 이 문서만으로 요청·응답 읽기 → 판 차이 이해 → HTTPS 설정 요소(인증서, TLS 판, HTTPS 전환, HSTS) → curl·openssl로 검증까지 따라 할 수 있게 썼습니다. 메서드별 상세와 테스트 설계는 함께 보기 문서에 있습니다.

- 기준: RFC 9110~9114(HTTP), RFC 9846(TLS 1.3), RFC 6797(HSTS)
- 예제 시험: 2026-11-23 `nginx:1.30`과 `curlimages/curl:8.23.0`·`alpine/openssl` 컨테이너로 5·6절 설정과 명령을 실행해 결과를 확인. HTTP/3은 시험한 curl 이미지가 지원하지 않아 미실행

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 요청과 응답](#1-요청과-응답) / [2. 상태 코드와 주요 헤더](#2-상태-코드와-주요-헤더)    |
| [3. HTTP 판 비교](#3-http-판-비교) / [4. HTTPS 흐름](#4-https-흐름)                        |
| [5. HTTPS 설정 예](#5-https-설정-예) / [6. 검증](#6-검증) / [7. 트러블슈팅](#7-트러블슈팅) |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                          |

---

## 1. 요청과 응답

HTTP는 클라이언트가 요청을 보내고 서버가 응답하는 구조입니다. 의미(메서드·상태 코드·헤더)는 RFC 9110이 판과 상관없이 정의하고, 판마다 전송 형식만 다릅니다.

```text
GET /api/users/1 HTTP/1.1          <- 요청 줄: 메서드, 대상, 판
Host: api.example.com              <- 헤더 (HTTP/1.1에서 Host는 필수)
Accept: application/json

HTTP/1.1 200 OK                    <- 상태 줄: 판, 상태 코드, 설명
Content-Type: application/json
Content-Length: 27

{"id":1,"name":"example"}         <- 본문
```

`curl -v`로 보면 `>`는 보낸 요청, `<`는 받은 응답입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 상태 코드와 주요 헤더

| 범위 | 뜻          | 자주 보는 코드                                                    |
|------|-------------|-------------------------------------------------------------------|
| 1xx  | 진행 중     | 101 Switching Protocols (WebSocket)                               |
| 2xx  | 성공        | 200 OK, 201 Created, 204 No Content                               |
| 3xx  | 다른 곳으로 | 301 영구 이동, 302·307 임시 이동, 304 Not Modified(캐시 사용)     |
| 4xx  | 요청 문제   | 400, 401 인증 필요, 403 금지, 404, 429 요청 과다                  |
| 5xx  | 서버 문제   | 500, 502 Bad Gateway(뒤 서버 응답 오류), 503, 504 Gateway Timeout |

| 헤더                           | 쓰임                                  |
|--------------------------------|---------------------------------------|
| `Host`                         | 같은 IP의 여러 사이트 구분            |
| `Content-Type`                 | 본문 형식                             |
| `Cache-Control`, `ETag`        | 캐시 기간과 변경 여부 확인 (RFC 9111) |
| `Authorization`                | 인증 정보 (`Bearer <토큰>` 등)        |
| `Location`                     | 3xx 이동 대상                         |
| `Strict-Transport-Security`    | 이후 HTTPS로만 접속하라는 지시 (HSTS) |
| `Forwarded`, `X-Forwarded-For` | 프록시 뒤에서 원래 클라이언트 정보    |

[⬆ 목차로 돌아가기](#목차)

---

## 3. HTTP 판 비교

| 항목           | HTTP/1.1 (RFC 9112)                 | HTTP/2 (RFC 9113)                     | HTTP/3 (RFC 9114)                    |
|----------------|-------------------------------------|---------------------------------------|--------------------------------------|
| 전송           | TCP                                 | TCP (+ TLS)                           | QUIC (UDP 위, TLS 1.3 내장)          |
| 형식           | 텍스트                              | 바이너리 프레임                       | 바이너리 프레임                      |
| 동시 요청      | 연결 하나에 하나씩 (여러 연결 사용) | 연결 하나에 여러 스트림               | 연결 하나에 여러 스트림              |
| 헤더 압축      | 없음                                | HPACK                                 | QPACK                                |
| 패킷 손실 영향 | 해당 연결이 멈춤                    | TCP 손실 시 모든 스트림이 같이 기다림 | 손실된 스트림만 기다림               |
| 협상           | -                                   | TLS의 ALPN(`h2`)                      | `Alt-Svc` 헤더 또는 DNS HTTPS 레코드 |
| 방화벽         | TCP 80·443                          | TCP 443                               | UDP 443도 열어야 함                  |

브라우저는 HTTP/2를 TLS 위에서만 씁니다. 서버가 HTTP/2를 켜도 클라이언트가 지원하지 않으면 HTTP/1.1로 자동으로 내려갑니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. HTTPS 흐름

HTTPS는 HTTP를 TLS 연결 안에서 보내는 것입니다. TLS 1.3(RFC 9846) 기준 흐름입니다.

```text
클라이언트                                              서버
  | -- ClientHello (지원 판, 암호, SNI, ALPN: h2) -------> |
  | <------- ServerHello (선택한 판·암호, ALPN: h2) ------ |
  | <------- 인증서, 서명 (암호화됨) --------------------- |
  |   (인증서 체인을 신뢰하는 CA로 검증, 이름이 SNI와 맞는지 확인)
  | -- Finished ----------------------------------------> |
  | == 암호화된 HTTP/2 요청·응답 ======================== |
```

| 요소   | 확인할 것                                                                   |
|--------|-----------------------------------------------------------------------------|
| 인증서 | 신뢰하는 CA가 발급, 이름(SAN)이 접속 이름과 일치, 만료 전, 중간 인증서 포함 |
| TLS 판 | 1.2·1.3만 허용. 1.0·1.1은 RFC 8996으로 사용 중단                            |
| SNI    | 한 IP에서 여러 인증서를 쓸 때 서버가 어느 인증서를 줄지 정하는 이름         |
| ALPN   | TLS 협상 안에서 HTTP/2(`h2`)·HTTP/1.1을 정함                                |
| HSTS   | 한 번 받은 브라우저는 정한 기간 동안 HTTP로 접속하지 않음                   |

[⬆ 목차로 돌아가기](#목차)

---

## 5. HTTPS 설정 예

Nginx에서 80은 HTTPS로 보내고, 443은 TLS 1.2·1.3과 HTTP/2, HSTS를 켜는 예입니다.

```nginx
server {
    listen 80;
    server_name web.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name web.example.com;

    ssl_certificate     /etc/nginx/tls/fullchain.pem;   # 서버 인증서 + 중간 인증서
    ssl_certificate_key /etc/nginx/tls/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}
```

- HSTS는 HTTPS가 모든 하위 경로에서 문제없이 동작하는 것을 확인한 뒤 켭니다. 처음에는 짧은 `max-age`로 시작해 늘립니다.
- 인증서 발급·갱신은 [TLS/SSL 가이드](../../04_security/hardening/tls_ssl_guide.md)를 따릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용     | 명령                                                                                         | 기대 결과                                      |
|------|---------------|----------------------------------------------------------------------------------------------|------------------------------------------------|
| 1    | HTTPS 전환    | `curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://web.example.com/a`          | `301 https://web.example.com/a`                |
| 2    | HTTP/2        | `curl -s -o /dev/null -w '%{http_code} %{http_version}\n' https://web.example.com/`          | `200 2`                                        |
| 3    | HTTP/1.1 폴백 | 같은 명령에 `--http1.1`                                                                      | `200 1.1`                                      |
| 4    | HSTS          | `curl -sI https://web.example.com/ \| grep -i strict`                                        | `strict-transport-security: max-age=...`       |
| 5    | ALPN·TLS 판   | `echo \| openssl s_client -connect web.example.com:443 -servername web.example.com -alpn h2` | `ALPN protocol: h2`, `TLSv1.3`                 |
| 6    | 옛 TLS 거부   | `openssl s_client ... -tls1_1 -cipher 'DEFAULT:@SECLEVEL=0'`                                 | `alert protocol version`                       |
| 7    | 인증서 검증   | CA 옵션 없이 `curl https://...`                                                              | 공인 인증서면 성공, 자체 서명이면 종료 코드 60 |

6번에서 `-cipher 'DEFAULT:@SECLEVEL=0'`를 빼면 최신 OpenSSL 클라이언트가 스스로 TLS 1.1을 거부해(`no protocols available`) 서버 설정을 확인한 것이 되지 않습니다. curl `--tls-max 1.1`도 같은 이유로 클라이언트 쪽에서 실패합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                                   | 원인                                           | 해결 방법                                              |
|--------------------------------------------------------|------------------------------------------------|--------------------------------------------------------|
| curl 종료 코드 60, `self-signed certificate`           | 신뢰하지 않는 CA, 중간 인증서 누락             | 공인 인증서 사용, `fullchain` 지정, 시험은 `--cacert`  |
| `SSL: no alternative certificate subject name matches` | 인증서 SAN에 접속 이름 없음                    | 이름을 포함해 재발급, SNI 이름 확인                    |
| HTTP/2가 아니라 1.1로 접속됨                           | `http2 on` 없음, 클라이언트 미지원, TLS 없음   | 설정 확인, `curl -v`의 `ALPN` 줄 확인                  |
| 리디렉션이 반복됨                                      | 프록시 뒤 앱이 HTTP로 들어온 줄 알고 다시 보냄 | `X-Forwarded-Proto`·`Forwarded`를 앱이 신뢰하도록 설정 |
| HSTS를 끄고 싶은데 브라우저가 계속 HTTPS로 감          | 브라우저가 `max-age` 동안 기억                 | `max-age=0`을 HTTPS로 보내 지움, 처음부터 짧게 시작    |
| 502 Bad Gateway                                        | 리버스 프록시 뒤 서버가 응답하지 않음          | 뒤 서버 상태·포트, 프록시 오류 로그                    |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [HTTP 메서드](./http_methods.md) — 메서드별 의미, 멱등성, REST 설계
- [HTTP 프로토콜 테스트](../cs/web_testing/http_protocol_testing.md) · [TLS/HTTPS 테스트](../cs/web_testing/tls_https_testing.md) — 테스트 설계
- [TLS/SSL 가이드](../../04_security/hardening/tls_ssl_guide.md) — 인증서, openssl, Let's Encrypt
- [네트워크 헤더](./network_headers.md) — HTTP·TLS·QUIC 헤더 구조
- [OSI 모델](./osi_model.md) — 계층별 진단 순서

---

## 참고 자료

- IETF: [RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) · [RFC 9113 HTTP/2](https://www.rfc-editor.org/rfc/rfc9113) · [RFC 9114 HTTP/3](https://www.rfc-editor.org/rfc/rfc9114) — ★★★★☆
- IETF: [RFC 9846 TLS 1.3](https://www.rfc-editor.org/rfc/rfc9846) · [RFC 6797 HSTS](https://www.rfc-editor.org/rfc/rfc6797) · [RFC 8996](https://www.rfc-editor.org/rfc/rfc8996) — ★★★★☆
- nginx: [ngx_http_v2_module](https://nginx.org/en/docs/http/ngx_http_v2_module.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
