# Envoy
<!-- reference: _reference/envoy_official_notes.md -->

L4·L7 프록시입니다. 리버스 프록시·로드밸런서로 단독으로 쓰기도 하고, Istio·Consul 같은 서비스 메시와 여러 API 게이트웨이의 데이터 플레인(실제 트래픽을 처리하는 프록시)으로도 쓰입니다. 설정은 YAML(protobuf 구조)로 쓰고, 운영 중에는 관리 API(xDS)로 설정을 바꿀 수 있습니다. 이 문서만으로 정적 설정 작성 → 검증 → 컨테이너 실행 → 경로·가중치 라우팅 → 상태 검사·재시도 → 처리율 제한 → 관리 화면 확인까지 따라 할 수 있게 썼습니다.

- 기준 판: Envoy v1.40.2 (2026-10-27, v1.40.0은 2026-10-13) (2026-11-27 확인)
- 예제 시험: 2026-11-27 2~7절을 `envoyproxy/envoy:v1.40.2` 컨테이너와 whoami 백엔드 4개로 실행해 설정 검증, 경로 라우팅, 80:20 가중치 분배(200회 중 154:46), 능동 상태 검사로 멈춘 백엔드 제외, 처리율 제한 429, 관리 API를 확인. TLS 종료, 동적 설정(xDS), HTTP/3, 외부 인증·외부 처리율 제한 서비스는 미실행

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설정 구조](#2-설정-구조) / [3. 실행과 검증](#3-실행과-검증)                       |
| [4. 라우팅](#4-라우팅) / [5. 상태 검사와 재시도](#5-상태-검사와-재시도) / [6. 처리율 제한](#6-처리율-제한) |
| [7. 관리 API](#7-관리-api) / [8. 판과 지원](#8-판과-지원) / [9. 검증](#9-검증)                             |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기)                                                 |

---

## 1. 개요

```text
client --> [listener :10000] --> [filter chain: http_connection_manager]
                                    │  http filters: local_ratelimit -> router
                                    v
                               [route_config] --/api--> cluster api (api1, api2)
                                    │
                                    └-------/-------> cluster web_v1 (80%) / web_v2 (20%)
admin :9901  (/ready, /stats, /clusters, /config_dump)
```

| 용어     | 뜻                                                                                                       |
|----------|----------------------------------------------------------------------------------------------------------|
| listener | 받을 주소·포트                                                                                           |
| filter   | 연결(network)·요청(http) 단계에서 하는 처리. HTTP는 `http_connection_manager` 안에 http filter를 줄 세움 |
| route    | 요청을 어느 cluster로 보낼지                                                                             |
| cluster  | 같은 역할의 백엔드 묶음(endpoint 목록, 부하 분산, 상태 검사)                                             |
| xDS      | 컨트롤 플레인이 listener·route·cluster·endpoint를 내려보내는 API                                         |

- [Nginx](./nginx_install.md)·[HAProxy](./haproxy_concepts.md)와 비교하면 설정이 길지만, 설정을 API로 바꾸고 통계를 자세히 내는 점 때문에 서비스 메시·게이트웨이의 데이터 플레인으로 많이 쓰입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설정 구조

정적 설정 예시입니다. `/api`는 재시도와 상태 검사가 있는 `api` cluster로, 나머지는 `web_v1`·`web_v2`에 80:20으로 보냅니다.

```yaml
admin:
  address:
    socket_address: { address: 0.0.0.0, port_value: 9901 }

static_resources:
  listeners:
    - name: http_in
      address:
        socket_address: { address: 0.0.0.0, port_value: 10000 }
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                access_log:
                  - name: envoy.access_loggers.stdout
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.access_loggers.stream.v3.StdoutAccessLog
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: app
                      domains: ["*"]
                      routes:
                        - match: { prefix: "/api" }
                          route:
                            cluster: api
                            retry_policy:
                              retry_on: "5xx,connect-failure"
                              num_retries: 2
                        - match: { prefix: "/" }
                          route:
                            weighted_clusters:
                              clusters:
                                - { name: web_v1, weight: 80 }
                                - { name: web_v2, weight: 20 }
                http_filters:
                  - name: envoy.filters.http.local_ratelimit
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
                      stat_prefix: http_local_rate_limiter
                      token_bucket: { max_tokens: 100, tokens_per_fill: 100, fill_interval: 60s }
                      filter_enabled:
                        default_value: { numerator: 100, denominator: HUNDRED }
                      filter_enforced:
                        default_value: { numerator: 100, denominator: HUNDRED }
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
    - name: api
      type: STRICT_DNS
      connect_timeout: 1s
      lb_policy: ROUND_ROBIN
      health_checks:
        - timeout: 1s
          interval: 2s
          unhealthy_threshold: 2
          healthy_threshold: 1
          no_traffic_interval: 2s
          http_health_check: { path: "/health" }
      load_assignment:
        cluster_name: api
        endpoints:
          - lb_endpoints:
              - endpoint: { address: { socket_address: { address: api1, port_value: 80 } } }
              - endpoint: { address: { socket_address: { address: api2, port_value: 80 } } }
    - name: web_v1
      type: STRICT_DNS
      connect_timeout: 1s
      load_assignment:
        cluster_name: web_v1
        endpoints:
          - lb_endpoints:
              - endpoint: { address: { socket_address: { address: web1, port_value: 80 } } }
    - name: web_v2
      type: STRICT_DNS
      connect_timeout: 1s
      load_assignment:
        cluster_name: web_v2
        endpoints:
          - lb_endpoints:
              - endpoint: { address: { socket_address: { address: web2, port_value: 80 } } }
```

- `router`는 http filter 목록의 마지막에 둡니다. 그 앞의 filter가 요청을 처리한 뒤 router가 cluster로 보냅니다.
- `typed_config`의 `@type`은 확장마다 정해진 이름입니다. 오타가 나면 검증 단계에서 실패합니다.
- `STRICT_DNS`는 이름을 주기적으로 풀어 endpoint를 갱신합니다. IP를 고정할 때는 `STATIC`을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 실행과 검증

```bash
# 설정만 검사 (서버를 띄우지 않음)
docker run --rm -v "$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro" \
  envoyproxy/envoy:v1.40.2 --mode validate -c /etc/envoy/envoy.yaml

# 실행 (관리 포트는 로컬에만)
docker run -d --name envoy \
  -p 10000:10000 -p 127.0.0.1:9901:9901 \
  -v "$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro" \
  envoyproxy/envoy:v1.40.2

curl -s http://127.0.0.1:9901/ready      # LIVE
```

- 공식 이미지는 기본으로 `/etc/envoy/envoy.yaml`을 읽고, 프로세스는 `envoy` 사용자로 돕니다(시험 결과).
- 잘못된 설정은 `--mode validate`에서 `error initializing configuration '/etc/envoy/envoy.yaml': Unable to parse JSON as proto (INVALID_ARGUMENT: ...`처럼 실패합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 라우팅

| 방법                | 설정                                     | 시험 결과                      |
|---------------------|------------------------------------------|--------------------------------|
| 경로 접두사         | `match: { prefix: "/api" }`              | `/api`는 api1·api2에 3:3       |
| 가중치(카나리 배포) | `weighted_clusters` 80/20                | 200회 중 web_v1 154, web_v2 46 |
| 헤더 일치           | `match: { prefix: "/", headers: [...] }` | 미시험                         |

- 경로 규칙은 위에서부터 보고 처음 맞는 것을 씁니다. `/`처럼 넓은 규칙은 마지막에 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 상태 검사와 재시도

- 능동 상태 검사(`health_checks`)는 Envoy가 주기적으로 백엔드에 요청을 보내 상태를 봅니다.
- 시험에서 `no_traffic_interval`을 정하지 않았을 때는 30초 동안 검사가 2회뿐이었고, 백엔드 하나를 멈춰도 계속 `healthy`로 남았습니다. `no_traffic_interval: 2s`를 넣자 멈춘 지 5초 안에 `/failed_active_hc/active_hc_timeout`으로 바뀌고 요청이 남은 백엔드로만 갔습니다(6회 모두 200).
- `no_traffic_interval`은 cluster에 트래픽이 없다고 보는 동안 쓰는 검사 간격이며 기본값은 60초입니다. 트래픽이 적은 서비스는 장애 감지가 늦어질 수 있으므로 값을 정해 둡니다.
- `retry_policy`의 `retry_on`은 `5xx`, `connect-failure`, `reset`, `retriable-4xx` 등을 쉼표로 줍니다. 재시도는 같은 요청을 다시 보내므로 멱등이 아닌 요청(결제 등)에는 주의합니다.

```bash
curl -s http://127.0.0.1:9901/clusters | grep health_flags
curl -s http://127.0.0.1:9901/stats | grep -E "cluster.api.(health_check|membership_healthy)"
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 처리율 제한

`local_ratelimit`은 Envoy 인스턴스마다 토큰 버킷으로 요청 수를 제한합니다. 여러 인스턴스 전체 합계로 제한하려면 외부 처리율 제한 서비스(`ratelimit` filter)를 씁니다.

- 시험에서 버킷을 60초에 20개로 두고 25회 요청하자 20회 200, 5회 `429 Too Many Requests`였습니다.
- 통계 `http_local_rate_limiter.http_local_rate_limit.rate_limited`로 막힌 수를 봅니다.
- 버킷은 listener 전체에 걸리므로 시험할 때 다른 경로 요청도 함께 막힙니다. 경로마다 다르게 하려면 route의 `typed_per_filter_config`로 나눕니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 관리 API

| 경로           | 내용                                                     |
|----------------|----------------------------------------------------------|
| `/ready`       | 준비 여부(`LIVE`)                                        |
| `/server_info` | 판, 기동 옵션                                            |
| `/stats`       | 카운터·게이지(`/stats/prometheus`는 Prometheus 형식)     |
| `/clusters`    | endpoint별 상태(`health_flags`), 연결 수                 |
| `/config_dump` | 현재 적용된 bootstrap·listener·route·cluster·secret 설정 |
| `/logging`     | 로그 수준 바꾸기(POST)                                   |

- 관리 포트는 설정 확인과 변경이 모두 되므로 외부에 열지 않습니다. 컨테이너 포트 공개도 `127.0.0.1:9901:9901`처럼 로컬로 묶습니다.
- 기본 접근 로그 형식 예: `[2026-11-27T03:06:03.890Z] "GET / HTTP/1.1" 200 - 0 294 0 0 "-" "curl/8.5.0" "<request-id>" "127.0.0.1:18000" "172.20.0.5:80"`(마지막이 실제 백엔드 주소).

[⬆ 목차로 돌아가기](#목차)

---

## 8. 판과 지원

- 메이저(minor) 판은 분기마다 나오고, 출시 뒤 12개월 동안 보안·버그 수정 판을 받습니다. v1.40.0의 지원 종료는 2027-10-13입니다.
- v1.40.0의 호환되지 않는 변경 중 운영에 닿는 것: 로컬 처리율 제한의 shadow 모드 우회 수정으로 "Requests that were previously allowed by this bypass may now be rate limited.", mcp_router가 클라이언트 `authorization` 헤더를 기본으로 넘기지 않음, SSL 라이브러리에서 AWS-LC 제거. 그 밖에 QUIC/HTTP/3이 stable이 됐습니다.
- 서비스 메시·게이트웨이 제품에 들어 있는 Envoy는 제품이 정한 판을 씁니다. 따로 올리지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용   | 방법                            | 기대 결과                        |
|------|-------------|---------------------------------|----------------------------------|
| 1    | 설정        | `--mode validate`               | 오류 없음                        |
| 2    | 기동        | `curl 127.0.0.1:9901/ready`     | `LIVE`                           |
| 3    | 판          | `/server_info`                  | `1.40.2/Clean/RELEASE/BoringSSL` |
| 4    | 라우팅      | 경로별 요청 반복                | 정한 cluster·비율대로            |
| 5    | 상태 검사   | 백엔드 하나 정지 뒤 `/clusters` | `failed_active_hc`, 요청은 성공  |
| 6    | 처리율 제한 | 버킷보다 많이 요청              | 초과분 429                       |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                            | 원인                                          | 조치                                            |
|---------------------------------|-----------------------------------------------|-------------------------------------------------|
| `Unable to parse JSON as proto` | 필드 이름·형식·`@type` 오류                   | 오류 문구의 필드 확인, `--mode validate`로 반복 |
| 멈춘 백엔드가 계속 `healthy`    | `no_traffic_interval` 기본 60초               | `no_traffic_interval` 지정                      |
| 갑자기 429가 많음               | `local_ratelimit` 버킷이 listener 전체에 걸림 | 버킷 크기·경로별 설정 확인                      |
| `503 no healthy upstream`       | cluster의 모든 endpoint가 unhealthy           | `/clusters`의 `health_flags`, 백엔드 상태 확인  |
| 설정 바꿨는데 반영 안 됨        | 정적 설정은 재시작해야 반영                   | 재시작 또는 xDS·`--hot-restart` 구성 검토       |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [리버스 프록시](./reverse_proxy.md) — 개념과 도구 비교
- [HAProxy 개념](./haproxy_concepts.md) — 다른 L4·L7 로드밸런서

---

## 참고 자료

- Envoy Docs: [Version history v1.40](https://www.envoyproxy.io/docs/envoy/latest/version_history/v1.40/v1.40) · [Health checking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/health_checking) · [Local rate limit](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter) · [Admin interface](https://www.envoyproxy.io/docs/envoy/latest/operations/admin) — ★★★☆☆
- GitHub: [envoyproxy/envoy releases](https://github.com/envoyproxy/envoy/releases) · [RELEASES.md](https://github.com/envoyproxy/envoy/blob/main/RELEASES.md) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
