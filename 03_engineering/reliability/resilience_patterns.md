# Resilience Patterns
<!-- reference: _reference/grpc_official_notes.md, _reference/rest_api_official_notes.md -->

분산 시스템에서 한 의존 서비스의 지연이나 장애가 호출자 전체로 번지지 않게 막는 설계 기법들입니다. 이 문서는 timeout과 deadline, 재시도와 backoff·jitter, retry budget, circuit breaker, bulkhead, load shedding을 다루고 gRPC·Envoy 설정 예시와 점검표를 정리합니다.

## 목차

| 섹션                                                                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Timeout과 Deadline](#2-timeout과-deadline) / [3. 재시도와 Backoff](#3-재시도와-backoff)                                                     |
| [4. Retry Budget](#4-retry-budget) / [5. Circuit Breaker](#5-circuit-breaker) / [6. Bulkhead](#6-bulkhead)                                                           |
| [7. Load Shedding과 Graceful Degradation](#7-load-shedding과-graceful-degradation) / [8. 설정 예시](#8-설정-예시) / [9. 점검표와 트러블슈팅](#9-점검표와-트러블슈팅) |

## 1. 개요

| 항목      | 값                                                                                                                                                                                                       |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 목적      | 부분 장애가 연쇄 장애(cascading failure)로 커지는 것을 막음                                                                                                                                              |
| 핵심 질문 | 얼마나 기다릴 것인가, 몇 번 다시 할 것인가, 언제 호출을 멈출 것인가, 무엇을 버릴 것인가                                                                                                                  |
| 출처      | Google SRE Book Ch.21·22, AWS Builders' Library, Martin Fowler "CircuitBreaker", gRPC·Envoy 문서                                                                                                         |
| 연관 문서 | [Chaos Engineering](./chaos_engineering.md), [Capacity Planning](../delivery/capacity_planning.md), [Fault Injection 테스트](../../01_fundamentals/cs/testing/04_test_design/fault_injection_testing.md) |

SRE Book은 연쇄 장애를 "양의 피드백(positive feedback) 때문에 시간이 갈수록 커지는 장애"로 정의합니다. 전형적인 흐름은 다음과 같습니다.

```text
backend slows down
  -> callers wait longer, threads and connections pile up
  -> callers retry, load on backend grows
  -> some backend replicas crash, remaining replicas get more load
  -> more replicas crash (positive feedback)
```

이 문서의 기법은 위 고리의 각 단계를 끊는 역할을 합니다.

| 기법                        | 끊는 지점                                           |
|-----------------------------|-----------------------------------------------------|
| Timeout·Deadline            | 무한정 기다리며 자원을 붙잡는 것                    |
| Backoff·Jitter·Retry budget | 재시도가 부하를 몇 배로 키우는 것                   |
| Circuit breaker             | 이미 실패 중인 대상에 계속 호출하는 것              |
| Bulkhead                    | 한 의존성 문제가 다른 기능의 자원까지 고갈시키는 것 |
| Load shedding·Degradation   | 처리 못 할 요청을 받아 전부 느려지는 것             |

[⬆ 목차로 돌아가기](#목차)

## 2. Timeout과 Deadline

### Timeout 값 정하기

AWS Builders' Library는 허용할 거짓 timeout 비율(예: 0.1%)을 먼저 정하고, 의존 서비스 지연 분포에서 그 비율에 해당하는 백분위(0.1%면 p99.9)를 timeout으로 삼는 방법을 설명합니다. 지연 한계가 빡빡한 서비스는 여유를 더하고, 인터넷을 거치는 클라이언트는 최악의 네트워크 지연을 고려합니다.

| 종류          | 의미                                | 설정 기준                                                      |
|---------------|-------------------------------------|----------------------------------------------------------------|
| 연결 timeout  | TCP·TLS 연결 수립까지               | 짧게 (같은 데이터센터면 수백 ms 수준에서 시작해 측정으로 조정) |
| 요청 timeout  | 요청 전송부터 응답 완료까지         | 의존 서비스 p99.9 지연 + 여유                                  |
| 전체 deadline | 사용자 요청 하나가 끝나야 하는 시각 | 사용자 SLO의 지연 목표                                         |

모든 원격 호출에 timeout을 둡니다. 라이브러리 기본값이 "무제한"인 경우가 있으므로 확인이 필요합니다. 예를 들어 gRPC 클라이언트는 기본 deadline이 없으므로 호출마다 명시해야 합니다(gRPC Deadlines 문서).

### Deadline 전파

SRE Book Ch.22는 다음을 권합니다.

- 상위 요청의 남은 시간을 하위 호출에 넘깁니다(deadline propagation). 하위 호출은 자기 고정 timeout과 남은 시간 중 짧은 값을 씁니다.
- 각 처리 단계를 시작하기 전에 남은 시간을 확인하고, 이미 지났으면 일을 하지 않습니다.
- 클라이언트가 포기한 요청은 취소(cancellation)를 하위로 전파해 쓸모없는 작업을 멈춥니다.

```text
client deadline 800ms
  -> API (spent 50ms)       passes 750ms
     -> service A (spent 100ms) passes 650ms
        -> DB call: min(fixed 300ms, remaining 650ms) = 300ms
```

🟡 하위 호출의 timeout 합이 상위 timeout보다 길면, 상위가 이미 포기한 뒤에도 하위가 계속 일합니다. 계층별 timeout은 안쪽으로 갈수록 짧게 둡니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 재시도와 Backoff

AWS Builders' Library는 재시도가 "이기적(selfish)"이라고 표현합니다. 클라이언트는 성공 확률을 높이려고 서버 시간을 더 씁니다. 일시적 오류에는 도움이 되지만 과부하 상황에서는 부하를 키웁니다.

### 무엇을 재시도할까

| 오류                                          | 재시도                | 이유                                      |
|-----------------------------------------------|-----------------------|-------------------------------------------|
| 연결 거부·연결 재설정, 일시적 네트워크 오류   | 함                    | 다른 인스턴스·다음 시도에서 성공 가능     |
| HTTP 503, 429 (Retry-After 있으면 그 값 존중) | 함 (backoff 필수)     | 서버가 일시적으로 거절                    |
| gRPC `UNAVAILABLE`                            | 함                    | gRPC 문서 예시의 재시도 대상              |
| HTTP 4xx (400, 401, 403, 404 등)              | 하지 않음             | 같은 요청은 다음에도 실패                 |
| timeout                                       | 조건부                | 서버가 이미 처리했을 수 있음. 멱등할 때만 |
| 부작용 있는 쓰기 (결제, 생성)                 | 멱등성 키가 있을 때만 | 중복 처리 위험                            |

AWS는 "부작용이 있는 API는 멱등성(idempotency)을 제공하지 않는 한 재시도에 안전하지 않다"고 설명합니다. 멱등성은 같은 요청을 여러 번 보내도 결과가 한 번 보낸 것과 같은 성질입니다. 생성 API는 클라이언트가 만든 요청 토큰(idempotency key)을 받아 중복을 걸러내는 방식으로 멱등하게 만듭니다.

### Exponential backoff와 jitter

재시도 간격을 시도마다 배수로 늘리는 것이 exponential backoff이고, 그 간격에 무작위성을 더하는 것이 jitter입니다. jitter가 없으면 같은 순간 실패한 클라이언트들이 같은 순간 다시 몰려옵니다. AWS Architecture Blog의 시뮬레이터 코드에 있는 방식은 다음과 같습니다.

| 방식                      | 대기 시간 계산 (n = 시도 번호)                         |
|---------------------------|--------------------------------------------------------|
| Exponential (jitter 없음) | `min(cap, base * 2**n)`                                |
| Full Jitter               | `random(0, min(cap, base * 2**n))`                     |
| Equal Jitter              | `v/2 + random(0, v/2)`, 단 `v = min(cap, base * 2**n)` |
| Decorrelated Jitter       | `min(cap, random(base, prev_sleep * 3))`               |

같은 글은 jitter 없는 방식이 가장 나쁘고, Equal Jitter가 jitter 방식 중 가장 나쁘며, Full과 Decorrelated 사이의 선택은 분명하지 않다고 결론짓습니다. 특별한 이유가 없으면 단순한 Full Jitter부터 씁니다.

```python
import random
import time

def call_with_retry(func, max_attempts=3, base=0.1, cap=2.0,
                    retryable=(ConnectionError, TimeoutError)):
    """Call func() with capped exponential backoff and full jitter."""
    for attempt in range(max_attempts):
        try:
            return func()
        except retryable:
            if attempt == max_attempts - 1:
                raise
            sleep = random.uniform(0, min(cap, base * (2 ** attempt)))
            time.sleep(sleep)
```

### 재시도는 한 계층에서만

SRE Book은 계층마다 재시도하면 시도 수가 곱해진다고 경고합니다. 세 계층이 각각 4번 시도하면 가장 아래 DB에는 최대 4×4×4 = 64번이 갑니다. AWS 글도 깊은 호출 스택에서 계층마다 재시도하면 DB 부하가 243배(3의 5제곱)까지 늘 수 있다고 들며, "호출 스택의 한 지점에서만 재시도"하는 것을 모범 사례로 듭니다.

| 계층                 | 재시도 정책 예                             |
|----------------------|--------------------------------------------|
| 모바일·웹 클라이언트 | 사용자 동작 기준 재시도 (자동 재시도 최소) |
| API gateway·edge     | 재시도 담당 계층 (멱등 요청만)             |
| 내부 서비스 간       | 재시도하지 않음, 오류를 그대로 전달        |
| DB 드라이버          | 연결 단계 오류만 재시도                    |

[⬆ 목차로 돌아가기](#목차)

## 4. Retry Budget

요청당 시도 횟수를 제한해도, 장애 중에는 모든 요청이 최대 횟수만큼 재시도해 부하가 곱절이 됩니다. 이를 막기 위해 클라이언트·서버 단위로 재시도 총량을 제한합니다.

| 방식                 | 내용                                                                                                                    | 출처                  |
|----------------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 요청당 상한          | 요청 하나는 최대 3번 시도 후 호출자에게 오류 전달                                                                       | SRE Book Ch.21        |
| 클라이언트별 비율    | 재시도 비율이 전체 요청의 10% 미만일 때만 재시도                                                                        | SRE Book Ch.21        |
| Token bucket         | 토큰이 남아 있을 때만 재시도, 토큰이 떨어지면 정해진 속도로만 재시도                                                    | AWS Builders' Library |
| gRPC retryThrottling | 서버별 토큰 수(`maxTokens`), 성공 시 `tokenRatio`만큼 증가·실패 시 1 감소, 토큰이 `maxTokens`의 절반 아래면 재시도 중지 | gRPC Retry 문서       |
| Envoy retry_budget   | 동시 재시도를 활성·대기 요청 합의 일정 비율로 제한 (`budget_percent` 기본 20%, `min_retry_concurrency` 기본 3)          | Envoy API 문서        |

### 클라이언트 측 적응형 throttling

SRE Book Ch.21은 클라이언트가 최근 2분 동안 보낸 요청 수(`requests`)와 백엔드가 받아들인 수(`accepts`)를 세고, `requests`가 `accepts`의 K배를 넘으면 새 요청 일부를 로컬에서 바로 거절하는 방식을 소개합니다. 거절 확률은 다음과 같이 알려져 있습니다(책 본문 수식 그림, 여러 오픈소스 구현에서 같은 식 사용).

```text
reject_probability = max(0, (requests - K * accepts) / (requests + 1))
```

책은 K를 보통 2로 두며, K를 줄이면 더 강하게, 늘리면 더 약하게 throttling한다고 설명합니다. 백엔드가 거의 모든 요청을 거절하는 상황에서 클라이언트가 계속 요청을 보내 백엔드의 거절 처리 비용까지 늘리는 것을 막는 장치입니다.

[⬆ 목차로 돌아가기](#목차)

## 5. Circuit Breaker

Circuit breaker는 실패가 일정 기준을 넘은 의존 대상에 대한 호출을 잠시 즉시 실패시키는 장치입니다. 응답 없는 대상을 기다리며 스레드·연결이 고갈되는 것을 막고, 실패 중인 대상에 회복할 시간을 줍니다.

### 상태

```text
          failures >= threshold
 +--------+ -------------------> +------+
 | CLOSED |                      | OPEN | (fail fast, no calls)
 +--------+ <---+                +------+
     ^          |                    |
     |   trial  |                    | reset timeout elapsed
     |  success |                    v
     |          |              +-----------+
     +----------+------------- | HALF-OPEN | (allow trial call)
                  trial fail   +-----------+
                  -> back to OPEN
```

| 상태      | 동작                                          | 전이                                |
|-----------|-----------------------------------------------|-------------------------------------|
| Closed    | 호출을 그대로 보내고 실패를 셈                | 실패가 기준을 넘으면 Open           |
| Open      | 호출하지 않고 즉시 오류 반환 (또는 대체 응답) | reset timeout이 지나면 Half-open    |
| Half-open | 시험 호출을 일부 허용                         | 성공하면 Closed, 실패하면 다시 Open |

### 설계 판단

| 결정           | 고려                                                                                                 |
|----------------|------------------------------------------------------------------------------------------------------|
| 실패 기준      | 연속 실패 수보다 일정 창(window) 안의 실패 비율이 트래픽 변화에 덜 민감. 최소 요청 수 조건을 함께 둠 |
| 실패로 셀 오류 | timeout·5xx·연결 실패. 4xx는 호출자 잘못이므로 세지 않음                                             |
| Open 시 응답   | 오류, 캐시된 값, 기본값, 기능 숨김 중 기능별로 정함                                                  |
| reset timeout  | 너무 짧으면 회복 중인 대상을 다시 쓰러뜨림, 너무 길면 회복 후에도 기능 중단                          |
| 범위           | 대상 서비스 전체 단위인지, 인스턴스 단위인지 (인스턴스 단위는 outlier detection과 유사)              |

Fowler는 상태 변화를 모두 로그로 남기고, 차단기가 열리면 경보를 보내고, 운영자가 수동으로 열고 닫을 수 있게 하라고 권합니다. 차단기가 열린 것은 더 깊은 문제의 초기 신호일 수 있습니다.

🟡 Envoy의 "circuit breaking" 설정은 위 상태 기계가 아니라 클러스터별 최대 연결·대기 요청·동시 요청·동시 재시도 수를 제한하는 동시성 상한입니다. 응답 오류가 많은 개별 호스트를 일정 시간 빼는 기능은 Envoy에서 outlier detection이라고 부릅니다. 같은 이름이라도 도구마다 의미가 다르므로 문서를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. Bulkhead

Bulkhead(격벽)는 배의 격벽처럼 자원을 칸으로 나누어 한 칸의 문제가 다른 칸으로 번지지 않게 하는 설계입니다(Azure Architecture Center "Bulkhead pattern").

| 나누는 자원    | 예                                                                                  |
|----------------|-------------------------------------------------------------------------------------|
| 스레드·연결 풀 | 의존 서비스마다 별도 연결 풀. 느린 추천 서비스가 결제 호출용 연결까지 점유하지 않게 |
| 프로세스·Pod   | 중요 API와 배치 작업을 다른 Deployment로 분리                                       |
| 큐             | 고객 등급·작업 종류별 큐 분리                                                       |
| 인프라         | 셀(cell) 단위 분리, 다른 노드 풀·가용 영역                                          |
| 테넌트         | 큰 고객을 전용 자원으로 격리해 다른 고객 영향 차단                                  |

```text
             +--------------------- service ---------------------+
 requests -->| pool A (20 conns) -> payment API                  |
             | pool B (10 conns) -> recommendation API (slow)    |
             | pool C (5 conns)  -> email API                    |
             +---------------------------------------------------+
   recommendation slowdown exhausts pool B only; payment keeps working
```

칸을 너무 잘게 나누면 전체 자원 활용률이 떨어지므로, 중요도와 장애 가능성이 다른 경로만 나눕니다.

[⬆ 목차로 돌아가기](#목차)

## 7. Load Shedding과 Graceful Degradation

### Load shedding

SRE Book Ch.22는 서버가 과부하에 가까워지면 일부 요청을 "일찍, 싸게(early and cheaply)" 거절하라고 권합니다. 모든 요청을 받아 전부 느려지는 것보다, 일부를 즉시 거절하고 나머지를 정상 속도로 처리하는 편이 전체 성공 요청이 많습니다.

| 방법               | 설명                                                                             |
|--------------------|----------------------------------------------------------------------------------|
| 동시 처리 수 상한  | 처리 중 요청이 기준을 넘으면 HTTP 503 반환                                       |
| 짧은 큐            | 큐가 길면 대기 중 deadline이 지난 요청까지 처리하게 됨. 큐를 스레드 풀 대비 작게 |
| LIFO·CoDel 큐      | 오래 기다린 요청을 먼저 버려 이미 포기됐을 요청에 자원을 쓰지 않음               |
| 상위 계층에서 거절 | 역방향 프록시·로드 밸런서에서 미리 거절해 백엔드 보호                            |
| 중요도 기반        | 요청에 중요도를 붙이고 낮은 것부터 버림                                          |

SRE Book Ch.21은 요청 중요도를 네 단계로 나누는 Google 사례를 소개합니다.

| 중요도         | 의미                                                                  |
|----------------|-----------------------------------------------------------------------|
| CRITICAL_PLUS  | 실패하면 사용자에게 심각한 영향이 가는 가장 중요한 요청               |
| CRITICAL       | 운영 작업의 기본값. 이 트래픽을 감당할 용량을 확보해야 함             |
| SHEDDABLE_PLUS | 일부 실패를 예상하는 요청. 나중에 재시도할 수 있는 배치 작업의 기본값 |
| SHEDDABLE      | 잦은 부분 실패와 가끔의 전체 실패를 예상하는 요청                     |

중요도는 요청을 처리하면서 만드는 하위 호출로 전파됩니다.

### Graceful degradation

과부하나 의존성 장애 때 품질을 낮춘 응답으로 핵심 기능을 유지합니다.

| 기능      | 정상             | 저하 모드                             |
|-----------|------------------|---------------------------------------|
| 검색      | 전체 색인 검색   | 캐시 결과 또는 일부 색인만 검색       |
| 추천      | 개인화 추천      | 인기 상품 고정 목록                   |
| 상품 상세 | 실시간 재고 표시 | "재고 확인 중" 표시, 주문 시점에 확인 |
| 이미지    | 고해상도         | 저해상도                              |

SRE Book은 저하 모드가 평소 쓰이지 않으면 고장 난 채로 남기 쉬우므로 정기적으로 실행해 보고, 저하 모드에 들어간 서버 수를 모니터링하라고 권합니다. [Chaos Engineering](./chaos_engineering.md) 실험이나 [Feature Flag](../delivery/feature_flag_management.md)의 Ops 플래그로 저하 모드를 주기적으로 켜 보는 방법이 있습니다.

### Cold start 주의

재시작한 서버는 캐시가 비어 있어 같은 요청도 비용이 큽니다. SRE Book은 캐시에 기대는 서비스는 지연뿐 아니라 용량 관점에서도 여유를 두고, 트래픽을 천천히 늘려 캐시가 데워지게 하라고 권합니다. 장애 복구 후 트래픽을 한꺼번에 되돌리면 두 번째 장애가 날 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 설정 예시

### gRPC service config 재시도

gRPC 문서의 예시 형식입니다. 재시도 간격에는 ±20% jitter가 적용됩니다.

```json
{
  "methodConfig": [
    {
      "name": [{ "service": "example.OrderService" }],
      "timeout": "1s",
      "retryPolicy": {
        "maxAttempts": 3,
        "initialBackoff": "0.1s",
        "maxBackoff": "1s",
        "backoffMultiplier": 2,
        "retryableStatusCodes": ["UNAVAILABLE"]
      }
    }
  ],
  "retryThrottling": {
    "maxTokens": 10,
    "tokenRatio": 0.1
  }
}
```

### Envoy 클러스터 동시성 상한과 retry budget

Envoy API 문서 기준 기본값은 `max_connections`·`max_pending_requests`·`max_requests` 1024, `max_retries` 3입니다(확인일 2026-11-16). 기본값은 대규모 서비스에는 작고 소규모 서비스에는 클 수 있으므로 측정으로 정합니다.

```yaml
clusters:
  - name: order_service
    connect_timeout: 0.5s
    circuit_breakers:
      thresholds:
        - priority: DEFAULT
          max_connections: 512
          max_pending_requests: 256
          max_requests: 1024
          retry_budget:
            budget_percent:
              value: 20.0
            min_retry_concurrency: 3
          track_remaining: true
    outlier_detection:
      consecutive_5xx: 5
      interval: 10s
      base_ejection_time: 30s
      max_ejection_percent: 50
```

`track_remaining: true`를 켜면 상한까지 남은 자원 수가 통계로 노출되어, 상한에 가까워지는지 경보를 걸 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 9. 점검표와 트러블슈팅

### 설계 점검표

- [ ] 모든 원격 호출에 연결 timeout과 요청 timeout이 있는가 (라이브러리 기본값 확인)
- [ ] 안쪽 계층의 timeout이 바깥 계층보다 짧은가, deadline을 하위로 전파하는가
- [ ] 재시도하는 계층이 하나로 정해져 있는가
- [ ] 재시도에 exponential backoff, jitter, 최대 횟수, budget이 있는가
- [ ] 재시도하는 쓰기 요청이 멱등한가 (멱등성 키)
- [ ] 4xx처럼 다시 해도 실패할 오류를 재시도하지 않는가
- [ ] 주요 의존성마다 circuit breaker 또는 동시성 상한이 있고, 열림 상태를 경보로 받는가
- [ ] 중요 경로와 부가 기능이 연결 풀·프로세스 수준에서 분리되어 있는가
- [ ] 과부하 시 거절 기준(동시 처리 수·큐 길이)과 거절 응답(503, Retry-After)이 정해져 있는가
- [ ] 저하 모드를 최근에 실제로 실행해 보았는가

### 트러블슈팅

| 증상                                      | 가능한 원인                               | 확인·조치                                              |
|-------------------------------------------|-------------------------------------------|--------------------------------------------------------|
| 의존 서비스 하나가 느려지자 전체 API 지연 | timeout 없음 또는 너무 김, 연결 풀 공유   | timeout 추가, 의존성별 연결 풀 분리                    |
| 장애 복구 직후 다시 장애                  | 재시도 폭주, 캐시 cold start              | retry budget, 트래픽 점진 복구, 캐시 warm-up           |
| DB 부하가 평소의 수십 배                  | 여러 계층에서 동시에 재시도               | 재시도 계층을 하나로, 내부 계층 재시도 제거            |
| 주기적으로 요청이 한꺼번에 몰림           | jitter 없는 재시도·cron 작업              | backoff에 jitter, 정기 작업 시작 시각 분산             |
| 결제·주문 중복 생성                       | 멱등성 없는 쓰기 요청 재시도              | 멱등성 키 도입, 중복 확인                              |
| circuit breaker가 너무 자주 열림          | 기준이 연속 실패 수라 트래픽 적을 때 민감 | 비율 기준 + 최소 요청 수 조건                          |
| circuit breaker가 열리지 않아 계속 대기   | 실패로 세는 오류에 timeout이 빠짐         | timeout을 실패로 집계                                  |
| Envoy `upstream_rq_pending_overflow` 증가 | `max_pending_requests` 상한 도달          | 백엔드 용량·지연 확인 후 상한 조정, 상한만 올리지 않음 |
| 503이 늘었는데 서버 CPU는 낮음            | 동시성 상한·큐 상한이 너무 작음           | 부하 시험으로 처리 한계를 다시 측정해 상한 조정        |

[⬆ 목차로 돌아가기](#목차)

## 함께 보기

- [클라우드 설계 패턴](./cloud_design_patterns.md) — 가용성·데이터 관리·설계·모니터링 패턴 전체 지도

## 참고 자료

- Google SRE Book Ch.21: [Handling Overload](https://sre.google/sre-book/handling-overload/) — ★★★★☆ (확인일 2026-11-16)
- Google SRE Book Ch.22: [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) — ★★★★☆ (확인일 2026-11-16)
- AWS Builders' Library: [Timeouts, retries, and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) — ★★★☆☆ (확인일 2026-11-16)
- AWS Architecture Blog: [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — ★★☆☆☆ (확인일 2026-11-16)
- awslabs: [aws-arch-backoff-simulator](https://github.com/awslabs/aws-arch-backoff-simulator) (jitter 계산식) — ★★★☆☆ (확인일 2026-11-16)
- Martin Fowler: [CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html) — ★★☆☆☆ (확인일 2026-11-16)
- Azure Architecture Center: [Bulkhead pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead) — ★★★☆☆ (확인일 2026-11-16)
- gRPC: [Retry](https://grpc.io/docs/guides/retry/), [Deadlines](https://grpc.io/docs/guides/deadlines/) — ★★★☆☆ (확인일 2026-11-16)
- Envoy: [Circuit breaking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking), [circuit_breaker.proto](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/circuit_breaker.proto), [Outlier detection](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/outlier) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
