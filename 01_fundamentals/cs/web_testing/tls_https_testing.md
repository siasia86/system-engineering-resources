# TLS/HTTPS 테스트 (TLS/HTTPS Testing)
<!-- reference: _reference/web_testing_official_notes.md, _reference/web_server_official_notes.md -->

TLS/HTTPS 테스트는 웹 서버의 TLS 종료 지점이 허용된 프로토콜과 암호 조합만 협상하고, 올바른 인증서 체인을 SNI에 맞게 제공하며, HTTP에서 HTTPS로의 전환과 HSTS 정책을 의도대로 적용하는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                              |
|-----------|-----------------------------------------------------------------------------------|
| 목적      | TLS 설정이 보안 정책과 클라이언트 호환 범위를 함께 만족하는지 확인                |
| 실행 시점 | 인증서 발급·갱신, TLS 설정 변경, OpenSSL 등 라이브러리 업데이트 후                |
| 핵심 질문 | 허용한 것만 협상되고, 모든 호스트명에 유효한 인증서가 제공되는가                  |
| 판정 근거 | RFC 8446(TLS 1.3), RFC 8996(TLS 1.0·1.1 사용 중단), RFC 6797(HSTS), 조직 TLS 정책 |

TLS 설정 권장값(Mozilla Intermediate 프로필 등)은 `_reference/web_server_official_notes.md`를 기준으로 하고, 이 문서는 적용 결과를 확인하는 방법을 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
ClientHello (SNI, ALPN, versions, cipher suites)
      │
      v
[TLS termination]
  ├─ select certificate by SNI
  ├─ negotiate version + cipher
  ├─ negotiate ALPN (h2 / http/1.1)
  └─ optional: OCSP stapling, session resumption
      │
      v
HTTP layer: HTTP -> HTTPS redirect, HSTS header
```

| 검증 영역 | 확인 내용                                  |
|-----------|--------------------------------------------|
| 프로토콜  | 허용 버전 협상, 사용 중단 버전 거부        |
| 암호 조합 | 정책에 맞는 cipher suite만 협상            |
| 인증서    | 체인·호스트명·유효 기간·키 종류            |
| SNI       | 호스트명별 인증서 선택, SNI 없는 요청 처리 |
| HTTP 계층 | HTTPS 리다이렉트, HSTS, 혼합 콘텐츠        |

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 프로토콜과 암호 조합

| 케이스              | 입력                                | 기대 결과                | 실패 판정          |
|---------------------|-------------------------------------|--------------------------|--------------------|
| TLS 1.3 협상        | TLS 1.3만 허용한 클라이언트         | 정책상 허용 시 협상 성공 | 허용했는데 실패    |
| TLS 1.2 협상        | TLS 1.2까지만 지원하는 클라이언트   | 호환 정책상 허용 시 성공 | 호환 대상인데 실패 |
| 구버전 거부         | TLS 1.0·1.1 클라이언트              | handshake 실패           | 협상 성공          |
| 약한 암호 조합 거부 | CBC·RC4·3DES 등 정책 외 조합만 제시 | handshake 실패           | 협상 성공          |
| 전방 비밀성         | 기본 협상                           | ECDHE 계열 키 교환       | 정적 RSA 키 교환   |

### 인증서와 SNI

| 케이스        | 입력                             | 기대 결과                               | 실패 판정                        |
|---------------|----------------------------------|-----------------------------------------|----------------------------------|
| 체인 완전성   | 일반 연결                        | leaf와 중간 인증서 전체 제공, 검증 성공 | 중간 인증서 누락                 |
| 호스트명 일치 | 서비스하는 모든 호스트명         | SAN에 포함, 검증 성공                   | 일부 호스트명 불일치             |
| 유효 기간     | 인증서 만료일 확인               | 갱신 기준일보다 많이 남음               | 갱신 기준일 이내, 이미 만료      |
| SNI별 인증서  | 서로 다른 SNI로 연결             | 각 호스트명의 인증서 제공               | 기본 인증서가 잘못 제공          |
| SNI 없는 요청 | SNI 없이 IP로 연결               | 정책대로 기본 인증서 또는 거부          | 내부 호스트명이 담긴 인증서 노출 |
| 갱신 후 반영  | 인증서 교체 후 reload            | 새 인증서 제공                          | 프로세스 일부가 이전 인증서 제공 |
| OCSP stapling | CA가 OCSP를 제공하고 설정한 경우 | 유효한 OCSP 응답 포함                   | 설정했는데 응답 없음             |

### HTTP 계층

| 케이스           | 입력                        | 기대 결과                                    | 실패 판정                          |
|------------------|-----------------------------|----------------------------------------------|------------------------------------|
| HTTPS 리다이렉트 | `http://` 요청              | 301/308로 같은 호스트·경로의 `https://` 이동 | 다른 호스트로 이동, 경로·쿼리 유실 |
| HSTS 헤더        | HTTPS 응답                  | 정책에 맞는 `max-age`·`includeSubDomains`    | 누락, 평문 HTTP 응답에 포함        |
| HSTS 범위 영향   | `includeSubDomains` 사용 시 | 모든 하위 도메인이 HTTPS 제공                | HTTPS 없는 하위 도메인 접속 불가   |
| ALPN             | `h2,http/1.1` 제시          | 정책상 지원 프로토콜 선택                    | ALPN 미응답으로 HTTP/2 불가        |

HSTS는 브라우저가 지정한 기간 동안 HTTPS만 사용하게 하므로, `max-age`를 늘리거나 `includeSubDomains`를 추가하기 전에 모든 하위 도메인의 HTTPS 제공 여부를 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구               | 용도                                            |
|--------------------|-------------------------------------------------|
| `openssl s_client` | 버전·암호 조합·SNI·ALPN·인증서 체인 확인        |
| `openssl x509`     | 인증서 주체·발급자·유효 기간·만료 임박 확인     |
| `curl`             | HTTPS 리다이렉트·HSTS·TLS 버전 제한 요청        |
| `testssl.sh`       | 프로토콜·암호 조합·헤더·알려진 취약점 종합 점검 |

### 명령 예시

아래 주소는 문서용 예시입니다. 외부 서비스 점검은 소유자 승인 범위에서만 실행합니다.

```bash
# 협상 결과 요약 (버전, 암호 조합, ALPN)
openssl s_client -connect 192.0.2.10:443 -servername www.example.com \
  -alpn h2,http/1.1 -brief </dev/null

# 특정 버전 강제
openssl s_client -connect 192.0.2.10:443 -servername www.example.com -tls1_2 </dev/null
openssl s_client -connect 192.0.2.10:443 -servername www.example.com -tls1_3 </dev/null

# 인증서 체인 전체 출력
openssl s_client -connect 192.0.2.10:443 -servername www.example.com -showcerts </dev/null

# 유효 기간과 30일 이내 만료 여부 (만료 임박이면 종료 코드 1)
openssl s_client -connect 192.0.2.10:443 -servername www.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -checkend 2592000

# HTTPS 리다이렉트와 HSTS
curl -sS -o /dev/null -D - http://www.example.com/path?q=1
curl -sS -o /dev/null -D - https://www.example.com/ | grep -i strict-transport-security

# TLS 1.2 이하로 제한한 요청
curl -sS -o /dev/null -w '%{http_code}\n' --tls-max 1.2 https://www.example.com/

# 종합 점검 (프로토콜, 서버 기본값, 헤더)
testssl.sh -p -S -h https://www.example.com
```

로컬 OpenSSL이 구버전 프로토콜을 빌드에서 제외했으면 구버전 거부 테스트가 클라이언트 쪽에서 실패하므로, 결과를 판정하기 전에 클라이언트 지원 범위를 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                             | 우선 확인 대상                                       |
|----------------------------------|------------------------------------------------------|
| 일부 클라이언트만 검증 실패      | 중간 인증서 누락, 클라이언트 신뢰 저장소 차이        |
| 호스트명마다 다른 인증서 문제    | SNI별 서버 블록, 기본 서버 지정                      |
| 갱신했는데 이전 인증서 제공      | reload 누락, 여러 TLS 종료 지점 중 일부 미갱신       |
| HTTP/2가 협상되지 않음           | TLS 종료 지점의 ALPN 설정, 앞단 장비의 TLS 종료 여부 |
| 구버전 거부 결과가 일정하지 않음 | 테스트 클라이언트의 지원 범위, 앞단 장비의 별도 정책 |

### 분석 원칙

- TLS 종료 지점이 CDN·Load Balancer·웹 서버 중 어디인지 먼저 확인하고, 그 지점을 대상으로 테스트합니다.
- 서버가 여러 대이면 각 서버 주소를 직접 지정해 같은 결과인지 확인합니다.
- 보안 정책 위반(구버전·약한 암호 조합 허용)과 호환성 문제(필요한 클라이언트 거부)를 구분해 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] TLS 종료 지점을 확인했습니다.
- [ ] 허용 버전 협상과 사용 중단 버전 거부를 확인했습니다.
- [ ] 정책 외 암호 조합 거부를 확인했습니다.
- [ ] 인증서 체인·호스트명·유효 기간을 확인했습니다.
- [ ] SNI별 인증서와 SNI 없는 요청 처리를 확인했습니다.
- [ ] 인증서 갱신 후 모든 서버에 반영되었는지 확인했습니다.
- [ ] HTTPS 리다이렉트와 HSTS 정책을 확인했습니다.
- [ ] 테스트 클라이언트의 지원 범위를 결과와 함께 기록했습니다.

## 참고 자료

- RFC 8446 TLS 1.3: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc8446.html)
- RFC 8996 Deprecating TLS 1.0 and TLS 1.1: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc8996.html)
- RFC 6797 HTTP Strict Transport Security: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc6797.html)
- Mozilla SSL Configuration Generator: [ssl-config.mozilla.org](https://ssl-config.mozilla.org/) — ★★★☆☆
- testssl.sh: [github.com/testssl/testssl.sh](https://github.com/testssl/testssl.sh) — ★★★☆☆
- OpenSSL s_client: [docs.openssl.org](https://docs.openssl.org/3.0/man1/openssl-s_client/) — ★★★☆☆
- [HTTP 프로토콜 테스트](http_protocol_testing.md)

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
