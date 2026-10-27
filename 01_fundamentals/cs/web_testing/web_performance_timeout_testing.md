# 웹 성능·Timeout 테스트 (Web Performance and Timeout Testing)
<!-- reference: _reference/web_testing_official_notes.md, _reference/load_testing_official_notes.md -->

웹 성능·Timeout 테스트는 웹 서버와 프록시가 부하·느린 클라이언트·느린 upstream 조건에서 연결을 재사용하고, 정해진 timeout에 맞춰 연결을 정리하며, 연결과 대기열이 고갈될 때 예측 가능한 방식으로 실패하는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                        |
|-----------|-----------------------------------------------------------------------------|
| 목적      | 연결·timeout·대기열 설정이 부하와 지연 조건에서 설계대로 작동하는지 확인    |
| 실행 시점 | timeout·worker·연결 수 설정 변경 후, 용량 계획 전, 장애 재현 시             |
| 핵심 질문 | 느리거나 많은 요청이 와도 정상 요청을 계속 처리하고, 실패는 빠르고 명확한가 |
| 판정 근거 | 서비스 SLO, 제품 timeout 문서, 부하 테스트 유형 기준                        |

부하 유형(평균·스트레스·스파이크·내구성)과 일반 지표는 [성능 테스트](../testing/03_test_levels/performance_testing.md)를 따르고, 이 문서는 HTTP 연결과 timeout에 고유한 관점을 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
client ──(connect)──> [server / proxy]
         header read     client_header_timeout / timeout http-request
         body read       client_body_timeout
         idle keep-alive keepalive_timeout / timeout http-keep-alive
                              │
                              v
                         [upstream]
                connect      proxy_connect_timeout / timeout connect
                response     proxy_read_timeout / timeout server
                queue        timeout queue
```

### 구간별 timeout 대응

| 구간               | nginx 지시어 (기본값)         | HAProxy 키워드            | 만료 시 일반 결과  |
|--------------------|-------------------------------|---------------------------|--------------------|
| 요청 헤더 수신     | `client_header_timeout` (60s) | `timeout http-request`    | 408                |
| 요청 본문 수신     | `client_body_timeout` (60s)   | `timeout client`          | 408 또는 연결 종료 |
| keep-alive 유휴    | `keepalive_timeout` (75s)     | `timeout http-keep-alive` | 연결 종료          |
| 응답 송신          | `send_timeout` (60s)          | `timeout client`          | 연결 종료          |
| upstream 연결      | `proxy_connect_timeout` (60s) | `timeout connect`         | 502 또는 재시도    |
| upstream 응답 대기 | `proxy_read_timeout` (60s)    | `timeout server`          | 504                |
| 서버 슬롯 대기     | 해당 없음                     | `timeout queue`           | 503                |

nginx의 `client_body_timeout`·`send_timeout`·`proxy_read_timeout`은 전체 시간이 아니라 연속된 두 읽기·쓰기 사이의 간격입니다. 데이터가 조금씩 계속 오가면 전체 처리 시간은 timeout보다 길어질 수 있으므로, 전체 시간 상한이 필요하면 별도 장치로 검증합니다.

HAProxy는 `timeout client`·`timeout server`·`timeout connect`를 지정하지 않으면 무한 대기가 되며 경고를 출력합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 연결 재사용

| 케이스                | 입력                                | 기대 결과                                 | 실패 판정                              |
|-----------------------|-------------------------------------|-------------------------------------------|----------------------------------------|
| 클라이언트 keep-alive | 같은 연결로 연속 요청               | 연결 재사용, 연결 수립 시간이 첫 요청에만 | 요청마다 새 연결·TLS handshake         |
| 유휴 연결 정리        | keep-alive 후 timeout보다 오래 대기 | 서버가 연결 종료                          | 유휴 연결이 계속 남음                  |
| upstream 연결 재사용  | 프록시 뒤에서 연속 요청             | 설계 시 upstream 연결 재사용              | 요청마다 upstream 연결, TIME_WAIT 급증 |
| HTTP/2 다중화         | 한 연결에서 동시 stream 여러 개     | 한 연결로 병렬 처리                       | stream이 순차 처리되어 지연 누적       |

### timeout과 느린 클라이언트

| 케이스             | 입력                                     | 기대 결과                                | 실패 판정                                     |
|--------------------|------------------------------------------|------------------------------------------|-----------------------------------------------|
| 헤더를 천천히 전송 | 헤더를 몇 초 간격으로 한 줄씩 전송       | 헤더 timeout에서 408 또는 종료           | 연결이 무기한 유지                            |
| 본문을 천천히 전송 | 본문을 timeout 직전 간격으로 조금씩 전송 | 설계된 상한에서 종료                     | 연결이 무기한 유지                            |
| 응답을 천천히 수신 | 클라이언트가 응답을 매우 느리게 읽음     | 송신 timeout에서 종료                    | worker·버퍼가 장시간 점유                     |
| 느린 연결 다수     | 느린 클라이언트 연결을 동시에 다수 생성  | 정상 요청 응답 시간 유지, 느린 연결 정리 | 정상 요청까지 대기·거부                       |
| upstream 응답 지연 | upstream 지연이 read timeout을 초과      | timeout 시점에 504                       | 클라이언트 쪽 timeout이 먼저 발생해 원인 불명 |
| timeout 순서       | 클라이언트·프록시·upstream timeout 비교  | 바깥 계층 timeout이 안쪽보다 김          | 바깥 계층이 먼저 끊어 안쪽 작업만 남음        |

느린 연결 다수 케이스는 Slowloris 유형 공격의 재현이므로 운영 환경이 아닌 격리된 테스트 환경에서만 실행합니다.

### 부하와 고갈

| 케이스               | 입력                                | 기대 결과                              | 실패 판정                               |
|----------------------|-------------------------------------|----------------------------------------|-----------------------------------------|
| 기준선               | 낮은 부하의 대표 요청               | 지연 분포와 오류율 기준선 확보         | 기준선 없이 비교                        |
| 처리량 한계          | 동시 연결을 단계적으로 증가         | 한계 지점에서 지연 증가 후 명확한 거부 | 한계 이전부터 오류, 거부 없이 무한 지연 |
| 연결 수 고갈         | worker 연결 한도 근처까지 연결 생성 | 한도 초과 연결만 거부, 기존 연결 정상  | 프로세스 장애, 전체 응답 중단           |
| 파일 디스크립터 한도 | 연결 수가 FD 한도에 근접            | 로그에 한도 경고, 설계된 거부          | `Too many open files` 후 회복 불가      |
| upstream 대기열 포화 | upstream 처리량보다 많은 요청       | 대기열 timeout에서 503                 | 대기열이 계속 길어지며 전체 지연 증가   |
| 부하 해소 후 회복    | 고부하 뒤 정상 부하로 복귀          | 지연·오류율이 기준선으로 복귀          | 연결·메모리가 반환되지 않음             |

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구             | 용도                                                       |
|------------------|------------------------------------------------------------|
| `curl -w`        | 단일 요청의 연결·TLS·첫 바이트·전체 시간 분해              |
| `h2load`         | HTTP/1.1·HTTP/2 부하, 연결·stream 수 지정                  |
| `k6`             | 시나리오 기반 부하, threshold로 합격 판정 자동화           |
| `ss`             | 서버 연결 상태(ESTABLISHED·TIME_WAIT 등) 집계              |
| 서버 상태 페이지 | nginx `stub_status`, HAProxy stats의 활성 연결·대기열 확인 |

### 명령 예시

```bash
# 요청 구간별 시간 분해
curl -sS -o /dev/null -w \
  'connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total}\n' \
  https://www.example.com/

# HTTP/2: 요청 10만 개, 클라이언트 100개, 클라이언트당 동시 stream 10개
h2load -n100000 -c100 -m10 https://www.example.com/

# HTTP/1.1 강제 비교
h2load -n100000 -c100 --h1 https://www.example.com/

# 서버 연결 상태 집계
ss -Htan state time-wait | wc -l
ss -Htan state established '( sport = :443 )' | wc -l
```

k6에서는 threshold로 합격 기준을 코드에 두고, 기준을 넘으면 0이 아닌 종료 코드로 끝나게 하여 CI에서 판정합니다.

```javascript
import http from 'k6/http';

export const options = {
  vus: 50,
  duration: '5m',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<300', 'p(99)<800'],
  },
};

export default function () {
  http.get('https://www.example.com/');
}
```

위 수치는 예시이며 실제 기준은 서비스 SLO로 정합니다. `http_req_duration`은 DNS 조회와 연결 수립을 포함하지 않으므로, 연결 비용은 `http_req_connecting`·`http_req_tls_handshaking`으로 따로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                           | 우선 확인 대상                                 |
|--------------------------------|------------------------------------------------|
| 평균은 정상인데 p99만 증가     | 연결 수립 비율, upstream 대기열, GC·디스크 I/O |
| 부하 중 TIME_WAIT 급증         | 연결 재사용 실패, upstream keepalive 미설정    |
| 간헐적 502                     | upstream keepalive timeout이 프록시보다 짧은지 |
| 일정 시간 지점에서 일제히 오류 | 계층별 timeout 값, 클라이언트·LB idle timeout  |
| 부하 생성기 CPU가 먼저 포화    | 부하 생성기 병목, 생성기 수 증설 또는 분산     |
| 부하 종료 후에도 지연 지속     | 대기열 잔량, 연결·메모리 누수, 재시도 폭주     |

### 분석 원칙

- 부하 생성기의 CPU·네트워크를 함께 기록하여 생성기 병목과 대상 병목을 구분합니다.
- 평균값만 보지 않고 p95·p99와 오류율, 시간에 따른 변화를 함께 봅니다.
- 계층별 timeout 값을 한 표로 정리하고, 클라이언트에서 upstream으로 갈수록 짧아지는지 확인합니다.
- 재시도는 부하를 늘리므로 재시도 횟수와 대상 요청 수를 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 계층별 timeout 값과 기본값 적용 여부를 표로 정리했습니다.
- [ ] 클라이언트·upstream 연결 재사용을 확인했습니다.
- [ ] 느린 헤더·본문·응답 수신 케이스를 격리 환경에서 확인했습니다.
- [ ] upstream 지연 시 504가 설계 시점에 반환되는지 확인했습니다.
- [ ] 연결 수·FD·대기열 고갈 시 거부 방식과 회복을 확인했습니다.
- [ ] p95·p99·오류율과 부하 생성기 자원을 함께 기록했습니다.
- [ ] 합격 기준을 서비스 SLO에서 가져왔습니다.

## 참고 자료

- nginx ngx_http_core_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_core_module.html) — ★★★☆☆
- nginx ngx_http_proxy_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) — ★★★☆☆
- HAProxy Configuration Manual 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/configuration.html) — ★★★☆☆
- h2load how-to: [nghttp2.org](https://nghttp2.org/documentation/h2load-howto.html) — ★★★☆☆
- k6 Thresholds: [grafana.com/docs/k6](https://grafana.com/docs/k6/latest/using-k6/thresholds/) — ★★★☆☆
- k6 Built-in metrics: [grafana.com/docs/k6](https://grafana.com/docs/k6/latest/using-k6/metrics/reference/) — ★★★☆☆
- [성능 테스트](../testing/03_test_levels/performance_testing.md)
- [TCP 상태](../../networking/tcp_state_concepts.md)
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
