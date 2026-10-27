# 요청 보안 테스트 (Request Security Testing)
<!-- reference: _reference/web_testing_official_notes.md, _reference/web_server_official_notes.md -->

요청 보안 테스트는 웹 서버·프록시 계층의 방어 설정(보안 헤더, 요청 속도 제한, 민감 경로 차단, Host·CORS 검증, 오류 페이지 정보 노출 제한)이 의도대로 작동하는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                     |
|-----------|--------------------------------------------------------------------------|
| 목적      | 서버 계층의 방어 설정이 빠짐없이 적용되고 정상 사용을 막지 않는지 확인   |
| 실행 시점 | 보안 설정 변경, 새 가상 호스트·경로 추가, 정기 점검                      |
| 핵심 질문 | 모든 호스트·경로에 같은 방어가 적용되고, 거부는 설계한 코드로 일어나는가 |
| 판정 근거 | OWASP Secure Headers, 제품 문서, 조직 보안 정책                          |

이 문서는 방어 설정의 작동 여부만 확인하며 공격 재현 입력값은 다루지 않습니다. 취약점 원리와 실습은 [웹 CWE](../../../04_security/web_cwe/README.md), L7 차단 구조는 [DDoS 방어 아키텍처](../../../04_security/cloud/ddos_defense_architecture.md)를 참조합니다.

모든 점검은 소유자가 승인한 대상과 범위에서만 수행합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
request
  │
  v
[Host check] ── unknown host ──> reject (default server)
  │
  v
[rate limit] ── over limit ────> 429 / 503
  │
  v
[path rules] ── hidden file, listing ──> 403 / 404
  │
  v
[CORS] ──────── preflight / origin check
  │
  v
response ── security headers added, server info removed, error page sanitized
```

| 방어 영역      | 대표 설정                                                 |
|----------------|-----------------------------------------------------------|
| 응답 헤더      | CSP, HSTS, `X-Content-Type-Options`, `X-Frame-Options` 등 |
| 정보 노출 제한 | `server_tokens off`, `Server`·`X-Powered-By` 제거         |
| 요청 속도 제한 | nginx `limit_req` (거부 기본 503), HAProxy stick-table    |
| 경로 차단      | 숨김 파일·백업 파일 차단, `autoindex off`(nginx 기본값)   |
| Host 검증      | 알 수 없는 Host를 거부하는 기본 서버                      |
| CORS           | 허용 Origin 목록, 자격 증명 포함 요청 처리                |

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 보안 헤더

| 케이스           | 입력                       | 기대 결과                                         | 실패 판정                             |
|------------------|----------------------------|---------------------------------------------------|---------------------------------------|
| 필수 헤더 존재   | 대표 페이지 요청           | 정책에서 정한 헤더 모두 존재                      | 일부 누락                             |
| 오류 응답의 헤더 | 404·500 응답               | 정상 응답과 같은 보안 헤더                        | 오류 응답에서만 누락                  |
| 경로별 상속      | 별도 설정 블록이 있는 경로 | 상위 설정의 헤더 유지                             | 하위 블록 설정으로 상위 헤더가 사라짐 |
| 서버 정보 노출   | 일반 요청                  | `Server`에 버전 없음, `X-Powered-By` 없음         | 버전·프레임워크 정보 노출             |
| 폐기된 헤더      | 응답 헤더 확인             | 정책에서 제외한 헤더(예: `X-XSS-Protection`) 없음 | 근거 없이 남아 있음                   |

nginx의 `add_header`는 하위 블록에 `add_header`가 하나라도 있으면 상위 블록의 `add_header`를 상속하지 않습니다. 1.29.3부터는 `add_header_inherit merge`로 상위 값을 이어 붙일 수 있으므로, 대상 버전과 설정에 따라 기대 결과를 정합니다. 또한 `always`를 지정하지 않은 `add_header`는 200·204·301·302·304 등 일부 응답 코드에만 붙습니다.

### 요청 속도 제한

| 케이스    | 입력                             | 기대 결과                           | 실패 판정                              |
|-----------|----------------------------------|-------------------------------------|----------------------------------------|
| 한도 이하 | 한도보다 낮은 속도의 요청        | 모두 정상 처리                      | 정상 사용자 거부                       |
| 한도 초과 | 한도를 넘는 속도의 요청          | 설계한 코드(429 또는 503)로 거부    | 제한 없음, 다른 코드로 거부            |
| burst     | 순간 몰림 후 정상 속도           | burst 범위 안은 처리, 초과분만 거부 | burst 무시, 정상 속도 복귀 후에도 거부 |
| 키 기준   | 프록시 뒤 여러 클라이언트        | 실제 클라이언트 IP 기준 제한        | 프록시 IP 하나로 묶여 전체 차단        |
| 시험 모드 | `limit_req_dry_run on` 적용 상태 | 차단 없이 초과 건수만 기록          | 실제 차단 발생                         |

nginx `limit_req`의 거부 기본 코드는 503이며 `limit_req_status`로 바꿀 수 있습니다. 클라이언트 재시도 정책과 맞추려면 429 사용 여부를 정책으로 정합니다.

### 경로와 Host

| 케이스           | 입력                                          | 기대 결과                         | 실패 판정               |
|------------------|-----------------------------------------------|-----------------------------------|-------------------------|
| 숨김 파일        | `/.git/HEAD`, `/.env` 요청                    | 403 또는 404                      | 200과 파일 내용         |
| 백업·임시 파일   | `index.php.bak`, `*.swp` 요청                 | 403 또는 404                      | 200과 원본 코드         |
| 디렉터리 목록    | 인덱스 파일 없는 디렉터리                     | 403 또는 404                      | 파일 목록 표시          |
| 알 수 없는 Host  | 등록되지 않은 Host로 요청                     | 기본 서버가 거부(예: 444·400·421) | 대표 사이트 응답        |
| Host로 만든 링크 | 위조 Host로 비밀번호 재설정 등 링크 생성 요청 | 설정된 공식 도메인 사용           | 위조 Host가 링크에 반영 |
| 메서드 제한      | 정적 경로에 PUT·DELETE                        | 405                               | 2xx                     |

### CORS와 오류 페이지

| 케이스         | 입력                                        | 기대 결과                                     | 실패 판정                           |
|----------------|---------------------------------------------|-----------------------------------------------|-------------------------------------|
| 허용 Origin    | 허용 목록의 Origin                          | 해당 Origin을 `Access-Control-Allow-Origin`에 | 거부                                |
| 비허용 Origin  | 목록에 없는 Origin                          | CORS 헤더 없음                                | 요청 Origin을 그대로 반사           |
| 자격 증명 포함 | `credentials` 사용 요청                     | `*`와 자격 증명 허용을 함께 쓰지 않음         | 임의 Origin에 자격 증명 허용        |
| preflight      | `OPTIONS`와 `Access-Control-Request-Method` | 허용 메서드·헤더만 응답                       | 모든 메서드 허용                    |
| 오류 페이지    | 404·500 유발                                | 일반 안내 문구                                | 스택 트레이스, 내부 경로, 버전 노출 |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구               | 용도                                                    |
|--------------------|---------------------------------------------------------|
| `curl`             | 헤더 확인, Host·Origin 지정 요청, 경로별 응답 코드 확인 |
| 반복 요청 스크립트 | 속도 제한 한도 확인                                     |
| `testssl.sh -h`    | HTTPS 응답의 보안 헤더 점검                             |
| 서버 오류 로그     | 속도 제한 거부·차단 기록 확인                           |

### 명령 예시

```bash
# 보안 헤더 존재 확인
curl -sS -o /dev/null -D - https://www.example.com/ \
  | grep -iE '^(strict-transport-security|content-security-policy|x-content-type-options|x-frame-options|referrer-policy|permissions-policy|server|x-powered-by):'

# 404 응답에도 같은 헤더가 있는지
curl -sS -o /dev/null -D - https://www.example.com/not-found-check | grep -ic 'x-content-type-options'

# 민감 경로 응답 코드
for p in /.git/HEAD /.env /index.php.bak /static/; do
  printf '%s %s\n' "$(curl -sS -o /dev/null -w '%{http_code}' "https://www.example.com${p}")" "$p"
done

# 알 수 없는 Host
curl -sS -o /dev/null -w '%{http_code}\n' --resolve unknown.example.net:443:192.0.2.10 -k \
  https://unknown.example.net/

# 속도 제한: 짧은 시간에 30번 요청한 응답 코드 분포
for i in $(seq 1 30); do
  curl -sS -o /dev/null -w '%{http_code}\n' https://www.example.com/api/search
done | sort | uniq -c

# CORS: 허용되지 않은 Origin
curl -sS -o /dev/null -D - -H 'Origin: https://untrusted.example.org' https://api.example.com/ \
  | grep -i '^access-control-'
```

알 수 없는 Host 예시의 `-k`는 기본 서버 인증서가 해당 Host와 다른 경우에도 HTTP 응답 코드를 보기 위한 것이며, 인증서 판정에는 사용하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                               | 우선 확인 대상                                                  |
|------------------------------------|-----------------------------------------------------------------|
| 특정 경로에서만 헤더 누락          | 하위 블록의 `add_header`로 상속이 끊겼는지, `always` 사용 여부  |
| 오류 응답에서만 헤더 누락          | 오류 응답에도 헤더를 붙이는 설정(nginx `add_header ... always`) |
| 정상 사용자가 속도 제한에 걸림     | 제한 키가 프록시 IP인지, burst 설정                             |
| 알 수 없는 Host에 대표 사이트 응답 | 기본 서버 지정, 와일드카드 server_name                          |
| CORS가 모든 Origin 허용            | Origin 반사 설정, 자격 증명 허용과의 조합                       |

### 분석 원칙

- 모든 가상 호스트와 대표 경로를 목록으로 만들어 같은 점검을 반복합니다.
- 차단 확인과 함께 정상 사용이 막히지 않는지(오탐)를 같은 비중으로 확인합니다.
- 권장 헤더 값은 애플리케이션 기능과 충돌할 수 있으므로 서비스별 예외를 근거와 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 모든 가상 호스트의 정상·오류 응답에서 보안 헤더를 확인했습니다.
- [ ] 서버 버전·프레임워크 정보가 노출되지 않음을 확인했습니다.
- [ ] 속도 제한의 한도·burst·거부 코드·제한 키를 확인했습니다.
- [ ] 숨김 파일·백업 파일·디렉터리 목록 차단을 확인했습니다.
- [ ] 알 수 없는 Host 거부와 Host 기반 링크 생성을 확인했습니다.
- [ ] CORS 허용 범위와 자격 증명 처리를 확인했습니다.
- [ ] 오류 페이지에 내부 정보가 없음을 확인했습니다.

## 참고 자료

- OWASP Secure Headers Project: [owasp.org](https://owasp.org/www-project-secure-headers/) — ★★★☆☆
- nginx ngx_http_limit_req_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html) — ★★★☆☆
- nginx ngx_http_headers_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_headers_module.html) — ★★★☆☆
- MDN CORS: [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS) — ★★★☆☆
- [웹 CWE](../../../04_security/web_cwe/README.md)
- [TLS/SSL 가이드](../../../04_security/hardening/tls_ssl_guide.md)

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
