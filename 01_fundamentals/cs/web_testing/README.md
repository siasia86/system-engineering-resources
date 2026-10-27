# 웹 서버 테스트 (Web Server Testing)
<!-- reference: _reference/web_testing_official_notes.md -->

웹 서버 테스트는 HTTP 요청이 클라이언트에서 TLS 종료·Reverse Proxy·Load Balancer·애플리케이션까지 전달되는 과정에서 프로토콜 동작·보안 설정·연결 관리·성능이 기대대로인지 확인하는 도메인 테스트 영역입니다. 이 디렉토리는 특정 서비스의 운영 절차가 아닌 재사용 가능한 테스트 관점과 판정 기준을 다룹니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. 범위](#1-범위) / [2. 웹 서버 역할 모델](#2-웹-서버-역할-모델) / [3. 문서 목록](#3-문서-목록) |
| [4. 다른 문서와의 경계](#4-다른-문서와의-경계) / [5. 공통 판정 원칙](#5-공통-판정-원칙)          |

[⬆ 목차로 돌아가기](#목차)

## 1. 범위

### 포함

- HTTP 메서드·상태 코드·헤더·연결 재사용의 프로토콜 동작
- Reverse Proxy의 요청 전달·헤더 보존·upstream 오류 판정
- TLS 프로토콜·인증서·SNI·HSTS 설정 검증
- 웹 성능과 timeout·연결 고갈·느린 클라이언트 대응
- 역할별 테스트 케이스·검증 도구·실패 판정 기준

### 제외

- 특정 서비스의 실제 도메인·서버 주소·계정·운영 데이터
- 웹 서버 설치와 설정 설명 (`02_infrastructure/web_server/`에서 관리)
- 일반 테스트 기법 설명 (`01_fundamentals/cs/testing/`에서 관리)
- 게임 서비스 부하 테스트 계획 (`03_engineering/delivery/game_service_testing/`에서 관리)
- 웹 애플리케이션 취약점 공격 절차 (`04_security/web_cwe/`에서 관리)

[⬆ 목차로 돌아가기](#목차)

## 2. 웹 서버 역할 모델

웹 서버는 한 프로세스가 여러 역할을 겸하기도 하므로, 테스트는 제품이 아니라 역할을 기준으로 나눕니다.

```text
Client
  │
  v
[TLS termination] ── certificate, protocol, SNI, HSTS
  │
  v
[Reverse Proxy] ──── header forwarding, rewrite, timeout, retry
  │
  v
[Load Balancer] ──── health check, distribution, failover
  │
  v
[Origin / App] ───── status code, body, cache header
```

| 역할           | 주요 검증 질문                                           | 담당 문서                                                    |
|----------------|----------------------------------------------------------|--------------------------------------------------------------|
| HTTP 처리      | 요청 형식·메서드·상태 코드·연결 재사용이 규격대로인가    | [HTTP 프로토콜 테스트](http_protocol_testing.md)             |
| TLS 종료       | 허용 프로토콜·인증서·SNI·HSTS가 의도대로인가             | [TLS/HTTPS 테스트](tls_https_testing.md)                     |
| Reverse Proxy  | 요청이 올바른 upstream에 올바른 헤더로 전달되는가        | [Reverse Proxy 테스트](reverse_proxy_testing.md)             |
| 성능·연결 관리 | 부하·느린 클라이언트·upstream 지연에서 기대대로 버티는가 | [웹 성능·Timeout 테스트](web_performance_timeout_testing.md) |

[⬆ 목차로 돌아가기](#목차)

## 3. 문서 목록

| 문서                                                         | 설명                                                |
|--------------------------------------------------------------|-----------------------------------------------------|
| [HTTP 프로토콜 테스트](http_protocol_testing.md)             | 메서드·상태 코드·헤더·Keep-Alive·프로토콜 협상 검증 |
| [Reverse Proxy 테스트](reverse_proxy_testing.md)             | 라우팅·헤더 전달·경로 재작성·502/504·재시도 검증    |
| [TLS/HTTPS 테스트](tls_https_testing.md)                     | 프로토콜·암호 조합·인증서 체인·SNI·HSTS 검증        |
| [웹 성능·Timeout 테스트](web_performance_timeout_testing.md) | 연결 재사용·timeout·느린 클라이언트·연결 고갈 검증  |

### 예정 주제

다음 주제는 후속 작업에서 문서화합니다.

- Graceful Reload 테스트
- Load Balancer 테스트
- Cache/CDN 테스트
- 요청 보안 테스트
- 관측성 테스트

[⬆ 목차로 돌아가기](#목차)

## 4. 다른 문서와의 경계

| 기존 문서                                                                | 기존 문서가 다루는 내용 | 이 디렉토리가 다루는 내용         |
|--------------------------------------------------------------------------|-------------------------|-----------------------------------|
| [성능 테스트](../testing/03_test_levels/performance_testing.md)          | 부하 유형과 일반 지표   | HTTP 연결·timeout·대기열 판정     |
| [HTTP 메서드](../../networking/http_methods.md)                          | 메서드 정의와 API 설계  | 멱등성·메서드 처리의 검증 방법    |
| [에러 코드](../../networking/error_codes.md)                             | 상태 코드 정의          | 역할별 상태 코드 합격·불합격 판정 |
| [TCP 상태](../../networking/tcp_state_concepts.md)                       | TCP 상태와 TIME_WAIT    | 연결 고갈의 증상과 측정           |
| [장애 주입 테스트](../testing/04_test_design/fault_injection_testing.md) | 장애 주입 일반 기법     | upstream 장애·지연 주입 시나리오  |
| [Nginx](../../../02_infrastructure/web_server/nginx_install.md)          | 설치와 설정             | 설정 검증 절차와 판정             |

[⬆ 목차로 돌아가기](#목차)

## 5. 공통 판정 원칙

- 기대 결과는 RFC 정의와 대상 서버의 실제 설정을 함께 근거로 정합니다.
- 상태 코드만으로 판정하지 않고 응답 헤더·본문·로그·upstream 도달 여부를 함께 확인합니다.
- 테스트 대상 주소는 `--resolve`·`--connect-to`로 고정하여 DNS·CDN 경로 차이를 분리합니다.
- 제품 기본값은 버전에 따라 바뀌므로 대상 버전과 실제 설정을 결과와 함께 기록합니다.
- 운영 환경에 대한 부하·장애 주입은 사전 승인된 범위와 시간에만 수행합니다.

## 참고 자료

- RFC 9110 HTTP Semantics: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9110.html)
- nginx documentation: [nginx.org/en/docs](https://nginx.org/en/docs/) — ★★★☆☆
- HAProxy Configuration Manual 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/configuration.html) — ★★★☆☆
- [테스트 기법](../testing/README.md)
- [게임 테스트](../game_testing/README.md)

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
