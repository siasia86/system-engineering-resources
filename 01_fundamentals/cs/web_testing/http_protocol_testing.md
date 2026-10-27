# HTTP 프로토콜 테스트 (HTTP Protocol Testing)
<!-- reference: _reference/web_testing_official_notes.md -->

HTTP 프로토콜 테스트는 웹 서버가 요청 형식·메서드·상태 코드·헤더·연결 재사용·프로토콜 협상을 규격과 설정대로 처리하는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                      |
|-----------|-----------------------------------------------------------|
| 목적      | 요청 처리와 응답 의미가 RFC와 서버 설정에 맞는지 확인     |
| 실행 시점 | 웹 서버 설치·버전 변경·설정 변경 후, 프록시 계층 추가 후  |
| 핵심 질문 | 같은 요청에 항상 같은 의미의 응답을 돌려주는가            |
| 판정 근거 | RFC 9110(의미), RFC 9112(HTTP/1.1 연결), RFC 9113(HTTP/2) |

메서드와 상태 코드의 정의 자체는 [HTTP 메서드](../../networking/http_methods.md)와 [에러 코드](../../networking/error_codes.md)를 참조하고, 이 문서는 그 정의를 검증하는 방법을 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
request line   GET /path HTTP/1.1
headers        Host, Content-Length, Transfer-Encoding, Connection
body           (optional)
      │
      v
[parser] ──> reject: 400 / 414 / 431 / 413
      │
      v
[virtual host select by Host / SNI]
      │
      v
[method + route] ──> 405 / 404 / 3xx / 2xx
      │
      v
[connection] keep-alive reuse or close
```

HTTP 처리는 요청 해석, 가상 호스트 선택, 메서드·경로 처리, 연결 유지의 네 단계로 나누어 각 단계의 거부 조건과 정상 조건을 따로 검증합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 요청 해석

| 케이스               | 입력                                             | 기대 결과          | 실패 판정                             |
|----------------------|--------------------------------------------------|--------------------|---------------------------------------|
| Host 누락 (HTTP/1.1) | `Host` 없는 HTTP/1.1 요청                        | 400                | 2xx 응답 또는 기본 가상 호스트로 처리 |
| 긴 URI               | 서버 한도를 넘는 경로                            | 414                | 5xx 또는 연결 강제 종료만 발생        |
| 큰 헤더              | 헤더 버퍼 한도를 넘는 Cookie                     | 400 또는 431       | 5xx, 응답 없이 대기                   |
| 큰 본문              | 본문 크기 한도 초과 업로드                       | 413                | upstream까지 본문 전달 후 처리        |
| 길이 헤더 충돌       | `Content-Length`와 `Transfer-Encoding` 동시 지정 | 400 또는 연결 종료 | 두 계층이 서로 다른 길이로 해석       |

`Content-Length`와 `Transfer-Encoding` 충돌은 Request Smuggling의 원인이 되므로 프록시와 origin을 함께 놓고 두 계층의 해석이 같은지 확인합니다.

### 메서드와 상태 코드

| 케이스               | 입력                          | 기대 결과                         | 실패 판정                            |
|----------------------|-------------------------------|-----------------------------------|--------------------------------------|
| HEAD 응답            | 같은 경로에 GET과 HEAD        | 같은 상태·헤더, HEAD는 본문 없음  | HEAD에 본문 포함, 헤더 불일치        |
| 허용되지 않은 메서드 | 정적 경로에 DELETE            | 405와 `Allow` 헤더                | 2xx 또는 `Allow` 누락                |
| OPTIONS              | `OPTIONS *` 또는 경로 OPTIONS | 허용 메서드 안내                  | 5xx                                  |
| TRACE 차단           | TRACE 요청                    | 405 또는 501 (운영 정책상 비활성) | 요청 헤더가 본문으로 반사            |
| 멱등성               | 같은 PUT·DELETE 반복          | 두 번째 이후에도 같은 최종 상태   | 반복할수록 상태가 누적               |
| 리다이렉트           | 슬래시 없는 디렉터리 경로     | 301/308과 올바른 `Location`       | 내부 포트·호스트명이 노출된 Location |

### 헤더와 연결

| 케이스              | 입력                       | 기대 결과                        | 실패 판정              |
|---------------------|----------------------------|----------------------------------|------------------------|
| 연결 재사용         | 한 연결에서 요청 여러 개   | 같은 연결로 연속 처리            | 요청마다 새 연결       |
| `Connection: close` | 요청에 `Connection: close` | 응답 후 서버가 연결 종료         | 연결 유지              |
| 요청 수 한도        | 한 연결에서 한도 이상 요청 | 한도 도달 시 정상 응답 후 종료   | 응답 중간 절단         |
| 서버 정보 노출      | 일반 요청                  | 정책에 맞는 `Server` 헤더        | 버전 정보 노출         |
| 압축 협상           | `Accept-Encoding: gzip`    | `Content-Encoding`과 `Vary` 일치 | 압축했는데 `Vary` 누락 |

### 프로토콜 협상

| 케이스        | 입력                   | 기대 결과              | 실패 판정                    |
|---------------|------------------------|------------------------|------------------------------|
| HTTP/2 협상   | ALPN `h2` 제시         | HTTP/2로 응답          | 설정했는데 HTTP/1.1로만 응답 |
| HTTP/1.1 강제 | ALPN `http/1.1`만 제시 | HTTP/1.1로 정상 응답   | 협상 실패·연결 종료          |
| HTTP/3 안내   | HTTPS 응답 확인        | 지원 시 `Alt-Svc` 헤더 | 미지원인데 `Alt-Svc` 광고    |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구               | 용도                                |
|--------------------|-------------------------------------|
| `curl`             | 요청 생성, 헤더 확인, 프로토콜 지정 |
| `openssl s_client` | ALPN 협상 결과 확인                 |
| `nc` (netcat)      | 형식이 잘못된 원시 요청 전송        |
| `h2load`           | HTTP/2 연결·stream 동작 확인        |

### 명령 예시

대상 주소는 `--resolve`로 고정하여 DNS 경로 차이를 제외합니다. 아래 주소는 문서용 예시입니다.

```bash
# 상태 코드·헤더만 확인
curl -sS -o /dev/null -D - --resolve www.example.com:443:192.0.2.10 \
  https://www.example.com/

# HEAD와 GET 헤더 비교
curl -sS -I https://www.example.com/index.html
curl -sS -o /dev/null -D - https://www.example.com/index.html

# 허용되지 않은 메서드
curl -sS -o /dev/null -w '%{http_code}\n' -X DELETE https://www.example.com/

# 협상된 HTTP 버전 확인
curl -sS -o /dev/null -w '%{http_version}\n' --http2 https://www.example.com/
curl -sS -o /dev/null -w '%{http_version}\n' --http1.1 https://www.example.com/

# 한 연결에서 두 요청 (verbose 출력의 "Re-using existing connection" 확인)
curl -sS -v -o /dev/null -o /dev/null \
  https://www.example.com/a https://www.example.com/b 2>&1 | grep -i 're-using'

# Host 헤더 누락 원시 요청 (평문 테스트 서버)
printf 'GET / HTTP/1.1\r\nConnection: close\r\n\r\n' | nc 192.0.2.10 80
```

ALPN 결과는 `openssl s_client -connect 192.0.2.10:443 -servername www.example.com -alpn h2,http/1.1 -brief`로도 확인할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                         | 우선 확인 대상                                       |
|------------------------------|------------------------------------------------------|
| 기대와 다른 가상 호스트 응답 | `Host`·SNI 일치 여부, 기본 서버 지정                 |
| 큰 헤더 요청에 5xx           | 헤더 버퍼 설정, 프록시와 origin의 한도 차이          |
| HEAD와 GET 헤더 불일치       | 애플리케이션이 HEAD를 별도로 처리하는지              |
| 연결이 재사용되지 않음       | `keepalive_timeout`·요청 수 한도, 프록시의 연결 정책 |
| HTTP/2 협상 실패             | TLS 종료 지점의 ALPN 설정, 중간 장비의 TLS 처리      |
| 계층마다 다른 길이 해석      | 프록시·origin의 `Transfer-Encoding` 처리 방식        |

### 분석 원칙

- 클라이언트가 본 응답과 서버 접근 로그를 요청 단위로 대조합니다.
- 프록시를 거친 결과와 origin에 직접 보낸 결과를 비교하여 어느 계층의 동작인지 구분합니다.
- 서버 제품과 버전마다 거부 코드가 다를 수 있으므로 RFC 정의와 실제 설정을 함께 판정 근거로 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 요청 해석 단계의 거부 조건(400·413·414·431)을 확인했습니다.
- [ ] `Content-Length`와 `Transfer-Encoding` 충돌을 프록시와 origin에서 함께 확인했습니다.
- [ ] HEAD·OPTIONS·허용되지 않은 메서드의 응답을 확인했습니다.
- [ ] 리다이렉트 `Location`에 내부 정보가 없는지 확인했습니다.
- [ ] 연결 재사용과 `Connection: close` 동작을 확인했습니다.
- [ ] HTTP/2·HTTP/1.1 협상 결과를 확인했습니다.
- [ ] 결과에 서버 제품·버전·설정을 함께 기록했습니다.

## 참고 자료

- RFC 9110 HTTP Semantics: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9110.html)
- RFC 9112 HTTP/1.1: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9112.html)
- RFC 9113 HTTP/2: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9113.html)
- nginx ngx_http_core_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_core_module.html) — ★★★☆☆
- curl man page: [curl.se/docs/manpage.html](https://curl.se/docs/manpage.html) — ★★★☆☆
- [HTTP 메서드](../../networking/http_methods.md)
- [에러 코드](../../networking/error_codes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-27

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.
