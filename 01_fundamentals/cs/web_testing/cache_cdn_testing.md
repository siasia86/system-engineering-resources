# Cache/CDN 테스트 (Cache and CDN Testing)
<!-- reference: _reference/web_testing_official_notes.md, _reference/networking_official_notes.md -->

Cache/CDN 테스트는 프록시 캐시와 CDN이 캐시해도 되는 응답만 저장하고, 요청마다 올바른 캐시 항목을 돌려주며, 만료·검증·삭제(purge)가 설계대로 반영되는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                 |
|-----------|----------------------------------------------------------------------|
| 목적      | 캐시 정확성(다른 사용자 응답 노출 없음)과 신선도·적중률을 함께 확인  |
| 실행 시점 | 캐시 규칙·CDN 설정·응답 헤더 변경, 로그인·개인화 기능 추가 후        |
| 핵심 질문 | 이 응답을 다른 사용자가 받아도 되는가, 원본이 바뀌면 언제 반영되는가 |
| 판정 근거 | RFC 9111(HTTP 캐시), RFC 5861(stale 확장), CDN 제품 문서             |

TTL 권장값, 캐시 무효화 운영, CDN 디버깅 헤더는 [CDN·Proxy와 Origin IP](../../networking/cdn_proxy_origin_ip.md)를 참조합니다. 이 문서는 캐시가 맞게 동작하는지 판정하는 방법을 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
request ──> [cache key: method + host + path + query (+ Vary headers)]
                 │
        ┌────────┴────────┐
       HIT               MISS
        │                 │
  fresh? ── yes ──> serve │
        │                 v
       no ──> revalidate (If-None-Match / If-Modified-Since)
                 │
          304 -> serve stored    200 -> store if cacheable -> serve
```

| 판정 요소      | 확인 내용                                              |
|----------------|--------------------------------------------------------|
| 저장 가능 여부 | `Cache-Control`·`Set-Cookie`·`Authorization`·상태 코드 |
| 캐시 키        | 경로·쿼리·Host, `Vary`로 나뉘는 보조 키                |
| 신선도         | `max-age`·`s-maxage`·`Expires`·`Age`                   |
| 검증           | `ETag`·`Last-Modified`와 조건부 요청                   |
| stale 제공     | `stale-while-revalidate`·`stale-if-error`, 제품별 설정 |

공유 캐시는 `Authorization` 헤더가 있는 요청에 저장된 응답을 쓰면 안 되며, 응답에 `public`·`s-maxage`·`must-revalidate`처럼 공유 캐시 저장을 허용하는 지시어가 있을 때만 예외입니다(RFC 9111 3.5).

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 캐시 정확성 (가장 먼저 확인)

| 케이스                 | 입력                                             | 기대 결과                 | 실패 판정                              |
|------------------------|--------------------------------------------------|---------------------------|----------------------------------------|
| 개인화 응답 누출       | 사용자 A로 로그인 페이지 요청 후 사용자 B가 요청 | B는 자신의 응답을 받음    | B가 A의 이름·정보가 담긴 응답을 받음   |
| `Set-Cookie` 응답 저장 | 세션 쿠키를 발급하는 응답                        | 공유 캐시에 저장하지 않음 | 다른 사용자에게 같은 세션 쿠키 전달    |
| `private`·`no-store`   | 해당 지시어가 붙은 응답                          | 공유 캐시 MISS 유지       | HIT 발생                               |
| `Vary` 처리            | `Accept-Encoding`·`Accept-Language`가 다른 요청  | 변형별로 맞는 응답        | 압축 안 된 클라이언트가 gzip 응답 수신 |
| 쿼리 문자열 키         | 쿼리만 다른 요청                                 | 설계대로 구분 또는 무시   | 다른 검색 결과가 섞임                  |
| 오류 응답 캐시         | 원본이 일시적으로 500 반환                       | 오류를 길게 캐시하지 않음 | 원본 복구 후에도 오류 응답 지속        |

### 신선도와 검증

| 케이스          | 입력                               | 기대 결과                    | 실패 판정                         |
|-----------------|------------------------------------|------------------------------|-----------------------------------|
| `max-age` 만료  | TTL이 지난 뒤 재요청               | 원본에 재검증 또는 새로 받음 | 만료 후에도 오래된 응답 계속 제공 |
| `s-maxage` 우선 | `max-age`와 `s-maxage`가 다른 응답 | 공유 캐시는 `s-maxage` 적용  | `max-age`로 판단                  |
| ETag 검증       | `If-None-Match`에 현재 ETag        | 304, 본문 없음               | 매번 200 전체 전송                |
| ETag 불일치     | `If-None-Match`에 오래된 ETag      | 200과 새 ETag                | 304로 오래된 내용 유지            |
| `Age` 헤더      | HIT 응답                           | 저장 후 경과 시간과 일치     | `Age` 누락, TTL보다 큰 값         |

### stale 제공과 삭제

| 케이스                  | 입력                               | 기대 결과                                | 실패 판정                          |
|-------------------------|------------------------------------|------------------------------------------|------------------------------------|
| 원본 장애 시 stale 제공 | 원본 중지 후 만료된 항목 요청      | 설계 시 stale 응답 제공, 상한 후 오류    | 즉시 5xx 또는 상한 없이 stale 지속 |
| 백그라운드 재검증       | `stale-while-revalidate` 구간 요청 | 즉시 stale 응답, 이후 요청은 새 내용     | 요청이 원본 응답을 기다림          |
| 동시 MISS               | 같은 항목에 동시 요청 다수         | 원본 요청이 적게 발생(요청 병합 설정 시) | 동시 요청 수만큼 원본 요청         |
| purge                   | 특정 경로 삭제 요청                | 다음 요청이 MISS, 새 내용                | 일부 엣지·변형에 이전 내용 남음    |
| 배포 후 반영            | 정적 파일 교체                     | 파일명 버전 또는 purge로 새 내용 제공    | 브라우저·CDN에 이전 파일 고정      |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구                 | 용도                                                |
|----------------------|-----------------------------------------------------|
| `curl` 헤더 비교     | `Cache-Control`·`Age`·`ETag`·캐시 상태 헤더 확인    |
| 캐시 상태 헤더       | nginx `$upstream_cache_status`, CDN의 HIT/MISS 헤더 |
| 테스트 계정 2개 이상 | 개인화 응답 누출 확인                               |
| 원본 접근 로그       | 원본까지 도달한 요청 수 집계                        |

### 명령 예시

```bash
# 같은 요청 두 번: 캐시 상태와 Age 비교 (X-Cache-Status는 테스트 서버에서 지정한 헤더)
for i in 1 2; do
  curl -sS -o /dev/null -D - https://www.example.com/static/app.js \
    | grep -iE '^(x-cache-status|age|cache-control|etag):'
  echo ---
done

# 조건부 요청: 현재 ETag로 304 확인
etag=$(curl -sS -o /dev/null -D - https://www.example.com/static/app.js \
  | awk 'tolower($1)=="etag:" {print $2}' | tr -d '\r')
curl -sS -o /dev/null -w '%{http_code}\n' -H "If-None-Match: ${etag}" \
  https://www.example.com/static/app.js

# Vary 확인: 압축 협상 유무에 따른 응답 비교
curl -sS -o /dev/null -D - -H 'Accept-Encoding: gzip' https://www.example.com/ | grep -i '^content-encoding:'
curl -sS -o /dev/null -D - https://www.example.com/ | grep -i '^content-encoding:'
```

nginx에서는 `add_header X-Cache-Status $upstream_cache_status;`처럼 캐시 상태를 응답 헤더나 로그에 남기면 `MISS`·`HIT`·`EXPIRED`·`STALE`·`UPDATING`·`REVALIDATED`·`BYPASS`를 요청 단위로 확인할 수 있습니다. 이 헤더는 내부 정보이므로 운영 노출 여부를 정책으로 정합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                   | 우선 확인 대상                                              |
|------------------------|-------------------------------------------------------------|
| 다른 사용자 정보 노출  | 캐시 규칙의 경로 범위, `Set-Cookie`·`private` 처리, 캐시 키 |
| 적중률이 낮음          | 쿼리·쿠키가 캐시 키에 포함되는지, `Vary` 범위, 짧은 TTL     |
| 배포 후 이전 내용 지속 | 파일명 버전 관리, purge 대상 범위, 브라우저 캐시 TTL        |
| 원본 장애 시 즉시 오류 | stale 제공 설정, 오류 응답 캐시 시간                        |
| 304가 나오지 않음      | ETag 생성 방식(서버마다 다른 ETag), 압축 변형의 ETag        |

### 분석 원칙

- 정확성 실패(누출)는 성능 지표와 무관하게 즉시 차단 대상으로 분류합니다.
- 캐시 계층(브라우저·CDN·프록시)마다 따로 측정하고, 어느 계층에서 HIT했는지 기록합니다.
- 서버가 여러 대이면 ETag가 서버마다 같은지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 두 개 이상의 테스트 계정으로 개인화 응답 누출을 확인했습니다.
- [ ] `Set-Cookie`·`Authorization`·`private`·`no-store` 응답이 공유 캐시에 저장되지 않음을 확인했습니다.
- [ ] `Vary`와 쿼리 문자열의 캐시 키 처리를 확인했습니다.
- [ ] 만료·`s-maxage`·조건부 요청(304)을 확인했습니다.
- [ ] 원본 장애 시 stale 제공과 상한을 확인했습니다.
- [ ] purge와 배포 후 반영을 모든 캐시 계층에서 확인했습니다.

## 참고 자료

- RFC 9111 HTTP Caching: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc9111.html)
- RFC 5861 HTTP Cache-Control Extensions for Stale Content: [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc5861.html)
- nginx ngx_http_proxy_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) — ★★★☆☆
- [CDN·Proxy와 Origin IP](../../networking/cdn_proxy_origin_ip.md)
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
