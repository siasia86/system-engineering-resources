# 웹 관측성 테스트 (Web Observability Testing)
<!-- reference: _reference/web_testing_official_notes.md, _reference/prometheus_official_notes.md -->

웹 관측성 테스트는 웹 서버·프록시의 로그·지표·추적 정보가 실제 요청과 장애를 빠짐없이, 올바른 값으로 기록하고, 문제가 생겼을 때 경보까지 이어지는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                           |
|-----------|--------------------------------------------------------------------------------|
| 목적      | 장애 분석에 필요한 정보가 실제로 남고, 지표·경보가 실제 상태와 일치하는지 확인 |
| 실행 시점 | 로그 형식·수집 경로·지표·경보 규칙 변경 후, 장애 대응 훈련 전                  |
| 핵심 질문 | 사용자가 오류를 겪은 요청 하나를 로그·지표·추적에서 찾아낼 수 있는가           |
| 판정 근거 | SLI 정의, 경보 기준, 로그 형식 명세                                            |

SLI·SLO 설계는 [SLO와 Error Budget](../../../03_engineering/reliability/slo_error_budget.md), 지표 수집 구성은 [Prometheus와 Grafana](../../../02_infrastructure/monitoring/prometheus_grafana.md)를 참조합니다. 이 문서는 그 결과가 실제 요청과 맞는지 판정하는 방법을 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
known test request (marked: request id / traceparent)
        │
        v
[proxy] ── access log: request id, status, upstream addr/status/time
        │
        v
[app]   ── app log + trace span (same request id / trace id)
        │
        v
[metrics] ── request count, status ratio, latency histogram
        │
        v
[alert rule] ──> notification
```

관측성 테스트는 알려진 요청이나 알려진 장애를 일부러 만들고, 그 흔적이 각 단계에 기대한 값으로 남는지 역으로 찾아가는 방식으로 진행합니다.

| 기록 대상      | nginx 변수·기능                                               | HAProxy 기능               |
|----------------|---------------------------------------------------------------|----------------------------|
| 요청 식별자    | `$request_id` (16바이트 난수, 16진수)                         | `unique-id-format`         |
| 전체 처리 시간 | `$request_time`                                               | 로그 형식의 시간 필드      |
| upstream 정보  | `$upstream_addr`·`$upstream_status`·`$upstream_response_time` | 로그의 백엔드·서버 필드    |
| 지표           | `stub_status` 또는 외부 exporter                              | 내장 `prometheus-exporter` |

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 로그

| 케이스             | 입력                            | 기대 결과                                           | 실패 판정                     |
|--------------------|---------------------------------|-----------------------------------------------------|-------------------------------|
| 필수 필드          | 대표 요청                       | 시각·클라이언트 IP·Host·경로·상태·시간·요청 ID 기록 | 필드 누락, 빈 값              |
| 실제 클라이언트 IP | 프록시 뒤에서 요청              | 신뢰 경계 정책에 맞는 클라이언트 IP                 | 프록시 IP만 기록              |
| 재시도 기록        | upstream 재시도가 일어나는 요청 | 여러 upstream 주소·상태가 모두 기록                 | 마지막 시도만 기록            |
| 거부 요청 기록     | 속도 제한·Host 거부·408         | 거부 사유를 구분할 수 있게 기록                     | 거부 요청이 로그에 없음       |
| 민감 정보 제외     | 쿼리·헤더에 토큰이 담긴 요청    | 토큰이 마스킹 또는 미기록                           | 비밀번호·토큰이 평문으로 기록 |
| 시각 일치          | 같은 요청의 프록시·앱 로그      | 같은 시간대·같은 시계 기준                          | 시간대 불일치로 대조 불가     |

### 요청 식별자와 추적

| 케이스               | 입력                                  | 기대 결과                                      | 실패 판정                            |
|----------------------|---------------------------------------|------------------------------------------------|--------------------------------------|
| 식별자 전파          | 요청 1건                              | 프록시·앱 로그에 같은 요청 ID                  | 계층마다 다른 ID                     |
| 응답 헤더 노출       | 요청 1건                              | 정책에 따라 응답 헤더로 요청 ID 제공           | 사용자 문의 시 요청을 찾을 수단 없음 |
| 외부 식별자 처리     | 클라이언트가 요청 ID 헤더를 직접 지정 | 신뢰 경계 정책대로 새로 발급 또는 검증 후 사용 | 임의 값이 그대로 로그 키로 사용      |
| Trace Context 전달   | `traceparent` 헤더가 있는 요청        | 형식이 맞으면 trace-id를 유지해 하위로 전달    | 프록시가 헤더를 버려 추적이 끊김     |
| 잘못된 `traceparent` | 형식이 틀린 값                        | 무시하고 새 추적 시작                          | 오류 응답, 잘못된 값 전파            |

`traceparent`는 `version-trace-id-parent-id-trace-flags` 형식(소문자 16진수, 총 55자)이며 예시는 `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`입니다.

### 지표와 경보

| 케이스         | 입력                             | 기대 결과                             | 실패 판정                           |
|----------------|----------------------------------|---------------------------------------|-------------------------------------|
| 요청 수 일치   | 알려진 수의 테스트 요청          | 지표 증가량이 요청 수와 일치          | 누락·중복 집계                      |
| 상태 코드 분류 | 2xx·4xx·5xx를 정해진 수만큼 발생 | 코드별 지표가 각각 일치               | 5xx가 다른 범주로 집계              |
| 지연 분포      | 지연을 주입한 요청               | 히스토그램 상위 구간에 반영           | 평균만 있어 tail 지연이 보이지 않음 |
| 외부 점검      | 외부 점검(Blackbox) 대상 중지    | 점검 실패 지표와 경보 발생            | 내부 지표만 보고 정상 판정          |
| 경보 도달      | 경보 조건을 만족하는 장애 주입   | 정해진 시간 안에 담당자에게 알림 도달 | 경보 규칙은 발동했지만 알림 미도달  |
| 지표 수집 중단 | exporter 중지                    | 수집 중단 자체가 경보                 | 지표가 없어 "오류 0"으로 보임       |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구                          | 용도                                      |
|-------------------------------|-------------------------------------------|
| `curl`                        | 식별자·`traceparent`를 지정한 테스트 요청 |
| 로그 검색(`grep`·로그 수집기) | 테스트 요청의 흔적 추적                   |
| 지표 조회(PromQL 등)          | 테스트 전후 지표 증가량 비교              |
| 장애 주입                     | upstream 중지·지연으로 경보 발생 확인     |

### 명령 예시

```bash
# 식별 가능한 테스트 요청 (추적 헤더 지정)
curl -sS -o /dev/null -D - \
  -H 'traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01' \
  https://www.example.com/api/health

# 프록시 접근 로그에서 같은 추적 ID 찾기 (로그 형식에 해당 헤더를 기록한 경우)
grep '4bf92f3577b34da6a3ce929d0e0e4736' /var/log/nginx/access.log

# 테스트 요청 100건 전후로 지표 증가량 비교 (지표 이름은 수집 구성에 따라 다름)
curl -sS http://192.0.2.10:8405/metrics | grep -E '^haproxy_frontend_http_responses_total' > /tmp/metrics_before.txt
for i in $(seq 1 100); do curl -sS -o /dev/null https://www.example.com/; done
curl -sS http://192.0.2.10:8405/metrics | grep -E '^haproxy_frontend_http_responses_total' > /tmp/metrics_after.txt
diff /tmp/metrics_before.txt /tmp/metrics_after.txt
```

로그 형식 예시(nginx)는 다음과 같습니다. 필드 이름은 수집 시스템과 맞춰 정합니다.

```nginx
log_format web_test 'ts=$time_iso8601 rid=$request_id ip=$remote_addr host=$host '
                    'req="$request" status=$status rt=$request_time '
                    'ua=$upstream_addr us=$upstream_status urt=$upstream_response_time '
                    'tp="$http_traceparent"';
```

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                         | 우선 확인 대상                                      |
|------------------------------|-----------------------------------------------------|
| 로그로 요청을 찾을 수 없음   | 요청 ID 전파, 로그 수집 누락, 시간대                |
| 지표와 로그의 요청 수 불일치 | 집계 범위(헬스체크·거부 요청 포함 여부), 수집 간격  |
| 장애인데 지표는 정상         | 지표 수집 위치가 장애 지점 뒤쪽인지, 외부 점검 유무 |
| 경보가 늦게 도달             | 평가 주기·대기 시간(for), 알림 경로                 |
| 로그에 민감 정보             | 쿼리 문자열·헤더 기록 범위, 마스킹 규칙             |

### 분석 원칙

- 테스트 요청은 식별 가능한 값으로 표시해 운영 트래픽과 구분합니다.
- 지표는 절댓값이 아니라 테스트 전후 증가량으로 비교합니다.
- "오류 0"과 "지표 없음"을 구분할 수 있는지 반드시 확인합니다.
- 경보 테스트는 담당자에게 사전 공지한 시간에 수행합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 접근 로그의 필수 필드와 실제 클라이언트 IP 기록을 확인했습니다.
- [ ] 재시도·거부 요청이 구분되어 기록됨을 확인했습니다.
- [ ] 로그에 비밀번호·토큰이 남지 않음을 확인했습니다.
- [ ] 요청 ID와 `traceparent`가 계층 사이에 전달됨을 확인했습니다.
- [ ] 알려진 요청 수와 지표 증가량이 일치함을 확인했습니다.
- [ ] 외부 점검과 수집 중단 경보를 확인했습니다.
- [ ] 장애 주입부터 알림 도달까지 걸린 시간을 기록했습니다.

## 참고 자료

- W3C Trace Context Level 1: [w3.org](https://www.w3.org/TR/trace-context/) — ★★★★☆
- nginx ngx_http_core_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_core_module.html) — ★★★☆☆
- nginx ngx_http_log_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_log_module.html) — ★★★☆☆
- HAProxy Configuration Manual 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/configuration.html) — ★★★☆☆
- [SLO와 Error Budget](../../../03_engineering/reliability/slo_error_budget.md)
- [Prometheus와 Grafana](../../../02_infrastructure/monitoring/prometheus_grafana.md)
- [Reverse Proxy 테스트](reverse_proxy_testing.md)

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
