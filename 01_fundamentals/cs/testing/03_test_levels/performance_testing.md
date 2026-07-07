# 성능/부하 테스트 (Performance Testing)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 유형](#2-유형) / [3. 지표](#3-지표) |
| [4. 도구](#4-도구) / [5. 실전 가이드](#5-실전-가이드) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

성능 테스트는 시스템의 응답 시간, 처리량, 안정성을 측정하고 병목을 식별하는 테스트입니다.

| 항목      | 내용                                |
|-----------|-------------------------------------|
| 목적      | 성능 요구사항 충족 여부 확인        |
| 실행 시점 | 릴리스 전, 인프라 변경 후           |
| 핵심 질문 | "동시 사용자 N명일 때 응답 시간은?" |

[⬆ 목차로 돌아가기](#목차)

## 2. 유형

| 유형            | 목적                          | 부하 패턴             |
|-----------------|-------------------------------|-----------------------|
| 부하 테스트     | 예상 부하에서 성능 확인       | 정상 트래픽           |
| 스트레스 테스트 | 한계점 및 복구 능력 확인      | 정상 초과 트래픽      |
| 스파이크 테스트 | 급격한 부하 증가 대응 확인    | 순간 폭증             |
| 내구성 테스트   | 장시간 운영 시 안정성 확인    | 일정 부하 장시간 유지 |
| 확장성 테스트   | 리소스 추가 시 성능 향상 확인 | 점진적 증가           |

### 부하 패턴 다이어그램

```
Users
  ^
  │     Spike
  │      /\
  │     /  \     Stress
  │    /    \   /────────
  │   /      \_/
  │  / Load
  │ /──────────
  └──────────────────────> Time
```

[⬆ 목차로 돌아가기](#목차)

## 3. 지표

| 지표                | 설명                | 기준 예시   |
|---------------------|---------------------|-------------|
| 응답 시간 (Latency) | 요청~응답 소요 시간 | P95 < 200ms |
| 처리량 (Throughput) | 초당 처리 요청 수   | > 1000 RPS  |
| 에러율 (Error Rate) | 실패 요청 비율      | < 0.1%      |
| 동시 사용자         | 동시 접속 가능 수   | > 5000      |
| CPU/메모리 사용률   | 서버 리소스 소비    | < 80%       |
| P50/P95/P99         | 백분위 응답 시간    | P99 < 500ms |

[⬆ 목차로 돌아가기](#목차)

## 4. 도구

| 도구    | 언어   | 특징                             |
|---------|--------|----------------------------------|
| k6      | Go/JS  | 스크립트 기반, CI 친화적         |
| Locust  | Python | Python 스크립트, 분산 실행       |
| JMeter  | Java   | GUI, 다양한 프로토콜             |
| wrk     | C      | 경량, HTTP 벤치마크              |
| Gatling | Scala  | 코드 기반, 상세 리포트           |
| ab      | C      | Apache Bench, 간단한 HTTP 테스트 |

### k6 예시

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 },  // ramp up
    { duration: '1m',  target: 100 },  // steady
    { duration: '10s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('http://localhost:8080/api/health');
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

### Locust 예시

```python
from locust import HttpUser, task, between

class WebUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/api/health")

    @task(3)
    def get_items(self):
        self.client.get("/api/items")
```

[⬆ 목차로 돌아가기](#목차)

## 5. 실전 가이드

### 테스트 환경

- 프로덕션과 동일한 스펙 (또는 비율 축소)
- 네트워크 격리 (외부 트래픽 영향 제거)
- 모니터링 병행 (Grafana, CloudWatch)

### 결과 분석

```
응답 시간 증가 원인:
  1. DB 쿼리 느림 → slow query log 확인
  2. CPU 포화 → 스케일 아웃 필요
  3. 메모리 부족 → GC 빈도 증가
  4. 네트워크 병목 → 대역폭 확인
  5. 커넥션 풀 고갈 → 풀 크기 조정
```

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- k6 docs: [k6.io/docs](https://k6.io/docs/) — ★★★☆☆
- Locust docs: [docs.locust.io](https://docs.locust.io/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-08

**마지막 업데이트**: 2026-05-08

© 2026 siasia86. Licensed under CC BY 4.0.
