# Reverse Proxy 테스트 (Reverse Proxy Testing)
<!-- reference: _reference/web_testing_official_notes.md, _reference/web_server_official_notes.md -->

Reverse Proxy 테스트는 프록시가 요청을 올바른 upstream으로, 올바른 헤더와 경로로 전달하고, upstream 오류·지연을 정해진 상태 코드와 재시도 정책으로 처리하는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                |
|-----------|---------------------------------------------------------------------|
| 목적      | 요청 전달 경로와 오류 처리가 설계대로인지 확인                      |
| 실행 시점 | 라우팅 규칙·upstream 구성·timeout·재시도 설정 변경 후               |
| 핵심 질문 | upstream이 받은 요청이 클라이언트가 보낸 요청과 의도대로 대응되는가 |
| 판정 근거 | RFC 9110(502·503·504·Via), 프록시 제품 문서, 라우팅 설계 문서       |

프록시 테스트의 핵심은 클라이언트 쪽 응답만 보지 않고 upstream이 실제로 받은 요청을 함께 관찰하는 것입니다. 이를 위해 요청 내용을 그대로 돌려주는 echo upstream을 테스트 환경에 둡니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
Client ──> [Reverse Proxy] ──> upstream A (echo)
              │   │
              │   └──────────> upstream B (slow / error injection)
              │
              ├─ route: Host + path -> upstream
              ├─ rewrite: path / header
              ├─ forward: X-Forwarded-For, X-Forwarded-Proto, Host
              └─ on failure: retry / 502 / 504
```

| 관찰 지점       | 확인 내용                                        |
|-----------------|--------------------------------------------------|
| 클라이언트 응답 | 상태 코드·헤더·본문·응답 시간                    |
| 프록시 로그     | 선택된 upstream·upstream 상태·upstream 응답 시간 |
| upstream 수신   | 경로·Host·전달 헤더·본문·요청 횟수               |

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 라우팅과 경로 재작성

| 케이스           | 입력                        | 기대 결과                                      | 실패 판정                          |
|------------------|-----------------------------|------------------------------------------------|------------------------------------|
| Host 기반 라우팅 | Host만 다른 요청 두 개      | 각 Host에 지정된 upstream 도달                 | 기본 upstream으로 몰림             |
| 경로 기반 라우팅 | `/api/`와 `/static/` 요청   | 경로별 upstream 도달                           | 접두어 겹침으로 다른 upstream 선택 |
| 접두어 제거      | `/api/v1/users`             | upstream이 설계된 경로(예: `/v1/users`)를 받음 | 슬래시 중복·누락                   |
| 인코딩된 경로    | `%2F`·`..%2F`가 포함된 경로 | 설계된 정규화 후 전달 또는 거부                | 정규화 차이로 다른 경로 접근       |
| 쿼리 문자열      | 쿼리 포함 요청              | 쿼리가 변형 없이 전달                          | 쿼리 유실·이중 인코딩              |

### 헤더 전달

| 케이스               | 입력                                     | 기대 결과                               | 실패 판정                                |
|----------------------|------------------------------------------|-----------------------------------------|------------------------------------------|
| 원래 Host 보존       | 공개 도메인으로 요청                     | upstream이 설계된 Host 값을 받음        | 내부 upstream 이름이 Host로 전달         |
| 클라이언트 IP 전달   | 일반 요청                                | `X-Forwarded-For`에 클라이언트 IP 추가  | 프록시 IP만 기록                         |
| 위조 헤더 처리       | 클라이언트가 `X-Forwarded-For` 직접 지정 | 신뢰 경계 정책대로 덮어쓰거나 뒤에 추가 | 위조 값을 그대로 신뢰                    |
| 원래 스킴 전달       | HTTPS 요청                               | `X-Forwarded-Proto: https`              | upstream이 http로 인식해 리다이렉트 반복 |
| hop-by-hop 헤더 제거 | `Connection`·`Upgrade` 등                | 프록시 정책대로 제거·재설정             | 클라이언트 값이 upstream 연결에 적용     |
| 응답 헤더 정리       | upstream이 내부 헤더 반환                | 정책상 숨길 헤더 제거                   | 내부 버전·호스트 정보 노출               |

nginx의 `proxy_set_header` 기본값은 `Host $proxy_host`이므로 원래 Host를 upstream에 넘기려면 명시 설정이 필요합니다. 설정 변경 후 이 케이스를 다시 확인합니다.

### upstream 오류와 재시도

| 케이스             | 입력                               | 기대 결과                                     | 실패 판정                              |
|--------------------|------------------------------------|-----------------------------------------------|----------------------------------------|
| upstream 중지      | upstream 프로세스 중지             | 다른 upstream으로 재시도 또는 502             | 무한 대기, 200과 빈 본문               |
| upstream 응답 지연 | 응답 전 지연이 read timeout보다 김 | 504                                           | 502로 표시되어 원인 구분 불가          |
| 잘못된 응답        | upstream이 형식 오류 응답 반환     | 502                                           | 손상된 응답을 그대로 전달              |
| 비멱등 요청 재시도 | POST 전송 후 upstream 연결 끊김    | 재시도하지 않고 오류 반환 (명시 허용 시 제외) | 같은 POST가 upstream에 두 번 도달      |
| 재시도 횟수 상한   | 모든 upstream 실패                 | 설정된 횟수 안에서 종료                       | 재시도가 timeout 합계를 넘겨 지연 누적 |
| 과부하 대기열      | 대기열 한도 초과                   | 503 (가능하면 `Retry-After`)                  | 대기열 무한 증가                       |

nginx는 POST·LOCK·PATCH를 upstream에 보낸 뒤에는 기본적으로 다음 서버로 넘기지 않습니다. HAProxy는 `timeout server` 만료 시 504, `timeout queue` 만료 시 503을 반환합니다.

### 업그레이드와 스트리밍

| 케이스               | 입력                            | 기대 결과               | 실패 판정                    |
|----------------------|---------------------------------|-------------------------|------------------------------|
| WebSocket 업그레이드 | `Upgrade: websocket` 요청       | 101 응답 후 양방향 통신 | 400 또는 즉시 종료           |
| 장기 연결 유지       | 메시지 간격이 read timeout 근처 | 설계된 timeout까지 유지 | 짧은 기본 timeout으로 끊김   |
| 스트리밍 응답        | upstream이 조금씩 응답 전송     | 버퍼링 정책대로 전달    | 버퍼링 때문에 첫 바이트 지연 |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구                               | 용도                                           |
|------------------------------------|------------------------------------------------|
| echo upstream                      | upstream이 받은 경로·헤더·본문을 응답으로 반환 |
| `curl`                             | 요청 생성, 헤더 위조, 응답 시간 측정           |
| 프록시 접근 로그                   | upstream 주소·상태·응답 시간 기록              |
| `tc netem`·지연 주입 upstream      | 지연·손실 주입                                 |
| `nginx -t`, `haproxy -c -f <파일>` | 배포 전 설정 문법 검사                         |

### 명령 예시

```bash
# echo upstream이 받은 헤더 확인 (응답 본문에 수신 헤더가 담기는 테스트 서버 기준)
curl -sS --resolve app.example.com:443:192.0.2.10 https://app.example.com/api/v1/echo

# X-Forwarded-For 위조 시도
curl -sS -H 'X-Forwarded-For: 203.0.113.99' https://app.example.com/api/v1/echo

# 상태 코드와 응답 시간
curl -sS -o /dev/null -w 'code=%{http_code} total=%{time_total}\n' \
  https://app.example.com/slow

# 설정 문법 검사
nginx -t
haproxy -c -f /etc/haproxy/haproxy.cfg
```

nginx 접근 로그에 `$upstream_addr`·`$upstream_status`·`$upstream_response_time`을 포함하면 재시도 경로와 upstream별 응답 시간을 요청 단위로 확인할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                       | 우선 확인 대상                                         |
|----------------------------|--------------------------------------------------------|
| 응답 지연인데 504 대신 502 | upstream이 연결을 먼저 끊었는지, keepalive 연결 재사용 |
| 같은 POST가 두 번 처리     | 비멱등 재시도 허용 설정, 클라이언트 재시도             |
| 리다이렉트 반복            | `X-Forwarded-Proto` 전달, upstream의 HTTPS 판단 방식   |
| 로그에 프록시 IP만 기록    | `X-Forwarded-For` 전달, upstream의 신뢰 프록시 설정    |
| 특정 경로만 다른 upstream  | location·ACL 우선순위, 접두어 겹침                     |
| 간헐적 502                 | upstream keepalive timeout이 프록시보다 짧은지         |

### 분석 원칙

- 프록시 로그의 upstream 상태와 클라이언트가 받은 상태를 대조해 오류가 생긴 계층을 구분합니다.
- 재시도는 응답 시간을 늘리므로 timeout 합계와 재시도 횟수를 함께 계산합니다.
- upstream 쪽 keepalive timeout은 프록시 쪽보다 길게 두는지 설정을 비교합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] Host·경로 기반 라우팅 결과를 upstream 수신 기록으로 확인했습니다.
- [ ] 접두어 제거·인코딩된 경로·쿼리 전달을 확인했습니다.
- [ ] 원래 Host·클라이언트 IP·스킴 전달을 확인했습니다.
- [ ] 위조된 `X-Forwarded-For`의 처리 정책을 확인했습니다.
- [ ] upstream 중지·지연·잘못된 응답의 상태 코드를 구분했습니다.
- [ ] 비멱등 요청이 중복 전달되지 않는지 확인했습니다.
- [ ] WebSocket·장기 연결·스트리밍 동작을 확인했습니다.
- [ ] 배포 전 설정 문법 검사를 실행했습니다.

## 참고 자료

- RFC 9110 HTTP Semantics: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9110.html)
- RFC 7239 Forwarded HTTP Extension: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc7239.html)
- nginx ngx_http_proxy_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) — ★★★☆☆
- HAProxy Configuration Manual 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/configuration.html) — ★★★☆☆
- [Nginx 설치 가이드](../../../02_infrastructure/web_server/nginx_install.md)
- [HAProxy 설치 가이드](../../../02_infrastructure/web_server/haproxy_install.md)
- [CDN·Proxy와 Origin IP](../../networking/cdn_proxy_origin_ip.md)

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
