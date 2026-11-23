# 리버스 프록시 개념
<!-- reference: _reference/reverse_proxy_official_notes.md -->

클라이언트와 서버 사이에서 서버 쪽 대신 요청을 받아 뒤쪽 서버로 넘기는 리버스 프록시의 역할, 원래 클라이언트 정보를 전달하는 헤더, 구현 도구 비교를 정리한 개념 문서입니다. 도구별 설치·설정은 함께 보기 문서에 있습니다.

- 기준: RFC 9110(HTTP Semantics), RFC 7239(Forwarded) (2026-11-23 확인)
- 예제 시험: 해당 없음(개념 문서). 도구별 설정은 각 문서에서 시험함

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 역할](#1-역할) / [2. 원래 클라이언트 정보 전달](#2-원래-클라이언트-정보-전달) / [3. 도구 비교](#3-도구-비교) |
| [4. 설계할 때 확인할 것](#4-설계할-때-확인할-것) / [5. 확인 방법](#5-확인-방법) / [함께 보기](#함께-보기)        |

---

## 1. 역할

```text
client ──> reverse proxy (TLS, routing, cache) ──> app server 1
                                              └──> app server 2
```

| 역할        | 설명                                                       |
|-------------|------------------------------------------------------------|
| TLS 종료    | 인증서를 한곳에서 관리하고 뒤쪽은 평문 또는 내부 TLS       |
| 부하 분산   | 여러 뒤쪽 서버로 요청을 나눔, 장애 서버 제외               |
| 경로 라우팅 | `/api`는 API 서버, `/`는 웹 서버처럼 경로·호스트별로 전달  |
| 캐시·압축   | 정적 응답 캐시, 응답 압축                                  |
| 보호        | 뒤쪽 서버를 외부에 직접 노출하지 않음, 요청 크기·속도 제한 |

RFC 9110은 클라이언트 쪽 중계를 proxy, 서버 쪽에서 원 서버처럼 동작하는 중계를 gateway(reverse proxy)로 구분합니다. 클라이언트 쪽 프록시는 [Squid](./squid.md) 문서를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 원래 클라이언트 정보 전달

리버스 프록시를 거치면 뒤쪽 서버에는 프록시 주소가 클라이언트로 보입니다. 원래 정보는 헤더로 전달합니다.

| 헤더                | 내용                                         | 표준 여부         |
|---------------------|----------------------------------------------|-------------------|
| `Forwarded`         | `for=`(클라이언트), `proto=`, `host=`, `by=` | RFC 7239 표준     |
| `X-Forwarded-For`   | 거친 클라이언트·프록시 주소 목록             | 비표준(널리 사용) |
| `X-Forwarded-Proto` | 원래 프로토콜 (`https`)                      | 비표준(널리 사용) |
| `X-Forwarded-Host`  | 원래 Host                                    | 비표준(널리 사용) |
| `Via`               | 거친 중계 장치                               | RFC 9110          |

```text
Forwarded: for=192.0.2.60;proto=https;by=203.0.113.43
X-Forwarded-For: 192.0.2.60, 198.51.100.17
```

클라이언트도 이 헤더를 직접 보낼 수 있으므로, 앱은 믿을 수 있는 프록시가 덧붙인 값만 써야 합니다. 프록시는 들어온 헤더를 지우거나 덮어쓰고, 앱 쪽에는 신뢰할 프록시 주소 목록을 설정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 도구 비교

| 도구    | 강점                                 | 32 문서                               |
|---------|--------------------------------------|---------------------------------------|
| Nginx   | 정적 파일 + 프록시, 세밀한 설정      | [Nginx 설치](./nginx_install.md)      |
| HAProxy | 부하 분산 전용, 헬스체크·통계가 풍부 | [HAProxy 개념](./haproxy_concepts.md) |
| Caddy   | 자동 HTTPS, 짧은 설정                | [Caddy](./caddy.md)                   |
| Apache  | 모듈이 많고 기존 환경 호환           | [Apache 설치](./apache_install.md)    |
| Varnish | HTTP 캐시 전용 (TLS는 앞단이 처리)   | [Varnish](./varnish.md)               |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설계할 때 확인할 것

| 항목        | 확인 내용                                                                      |
|-------------|--------------------------------------------------------------------------------|
| 시간 제한   | 프록시·앱의 연결·응답 시간 제한을 맞춤 (프록시가 먼저 끊으면 504)              |
| 요청 크기   | 업로드 크기 제한을 프록시와 앱 모두에서 맞춤 (Nginx `client_max_body_size` 등) |
| WebSocket   | `Upgrade`·`Connection` 헤더 전달 설정                                          |
| 헬스체크    | 장애 서버를 자동으로 빼는 주기와 기준                                          |
| 로그        | 프록시 로그에 원래 클라이언트 주소와 응답 시간 남기기                          |
| 단일 장애점 | 프록시 자체를 이중화 (keepalived 등)                                           |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 확인 방법

| 순서 | 확인 내용      | 방법                                                              | 기대 결과                    |
|------|----------------|-------------------------------------------------------------------|------------------------------|
| 1    | 전달 동작      | `curl -sI https://<서비스>/`                                      | 뒤쪽 앱의 응답               |
| 2    | 원래 주소 전달 | 앱 로그 또는 헤더 출력 페이지에서 `X-Forwarded-For` 확인          | 실제 클라이언트 주소         |
| 3    | 헤더 위조 차단 | `curl -H 'X-Forwarded-For: 1.2.3.4' https://<서비스>/` 후 앱 로그 | 위조 값이 그대로 쓰이지 않음 |
| 4    | 장애 서버 제외 | 뒤쪽 서버 하나 중지 후 반복 요청                                  | 오류 없이 다른 서버가 응답   |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [리버스 프록시 시험](../../01_fundamentals/cs/web_testing/reverse_proxy_testing.md) — 동작 시험 항목
- [HAProxy·keepalived 이중화](./haproxy_keepalived_ha.md) — 프록시 이중화
- [Squid](./squid.md) — 클라이언트 쪽 전달 프록시

---

## 참고 자료

- IETF: [RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) — ★★★★☆
- IETF: [RFC 7239 Forwarded HTTP Extension](https://www.rfc-editor.org/rfc/rfc7239) — ★★★★☆

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
