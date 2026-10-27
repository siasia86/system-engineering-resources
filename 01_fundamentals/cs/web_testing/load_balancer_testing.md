# Load Balancer 테스트 (Load Balancer Testing)
<!-- reference: _reference/web_testing_official_notes.md -->

Load Balancer 테스트는 요청이 설계한 방식으로 백엔드에 분산되고, 장애 백엔드가 정해진 시간 안에 제외·복귀되며, 백엔드를 빼거나 가중치를 바꾸는 운영 작업이 사용자 요청을 잃지 않는지 확인하는 테스트입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 테스트 대상 모델](#2-테스트-대상-모델) / [3. 테스트 케이스](#3-테스트-케이스) |
| [4. 검증 도구](#4-검증-도구) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트)           |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

| 항목      | 내용                                                                  |
|-----------|-----------------------------------------------------------------------|
| 목적      | 분산·장애 감지·복귀·운영 작업이 설계대로 동작하는지 확인              |
| 실행 시점 | 백엔드 증설·축소, 분산 방식·health check 변경, 배포 방식 변경 후      |
| 핵심 질문 | 백엔드 하나가 죽거나 빠질 때 사용자 오류가 얼마나, 얼마 동안 생기는가 |
| 판정 근거 | 제품 문서의 health check 기본값, 서비스 가용성 목표                   |

분산 설정 방법은 [Nginx 설치 가이드](../../../02_infrastructure/web_server/nginx_install.md)와 [HAProxy 설치 가이드](../../../02_infrastructure/web_server/haproxy_install.md)를 참조하고, 이 문서는 동작을 판정하는 방법을 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 테스트 대상 모델

```text
                     ┌──> backend A (weight 1)
client ──> [LB] ─────┼──> backend B (weight 1)
            │        └──> backend C (weight 2)
            │
            ├─ algorithm: round-robin / least_conn / hash
            ├─ active check: interval, rise, fall
            ├─ passive check: max_fails, fail_timeout
            └─ admin state: ready / drain / maint
```

### 장애 감지 방식

| 방식      | 동작                                       | 대표 설정                                            |
|-----------|--------------------------------------------|------------------------------------------------------|
| 능동 점검 | LB가 주기적으로 점검 요청을 보내 상태 판정 | HAProxy `check` (`inter` 2000ms, `rise` 2, `fall` 3) |
| 수동 판정 | 실제 요청 실패를 세어 일정 시간 제외       | nginx `max_fails` 1, `fail_timeout` 10초             |

오픈소스 nginx는 수동 판정만 제공하므로(능동 `health_check`는 상용 구독 기능) 장애 백엔드로 실제 사용자 요청이 한 번 이상 전달된 뒤에 제외됩니다. 이 차이가 장애 시 오류 수에 그대로 나타납니다.

HAProxy 기본값 기준으로 장애 감지는 대략 `inter × fall`(약 6초), 복귀는 `inter × rise`(약 4초)가 걸립니다. 실제 시간은 점검 timeout과 점검 시점에 따라 달라지므로 측정으로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 케이스

### 분산

| 케이스           | 입력                                   | 기대 결과                         | 실패 판정                      |
|------------------|----------------------------------------|-----------------------------------|--------------------------------|
| 균등 분산        | 같은 가중치 백엔드에 요청 다수         | 백엔드별 요청 수가 비슷함         | 한 백엔드에 몰림               |
| 가중치           | 가중치 1:1:2                           | 요청 비율이 가중치에 근접         | 가중치와 무관한 분포           |
| least_conn       | 응답 시간이 다른 백엔드                | 느린 백엔드에 활성 연결이 덜 배정 | round-robin과 같은 분포        |
| hash 분산        | 같은 키(예: URI)로 반복 요청           | 같은 백엔드 도달                  | 요청마다 다른 백엔드           |
| 세션 고정        | 고정 쿠키를 가진 반복 요청             | 같은 백엔드 도달                  | 세션 유실, 로그인 풀림         |
| 연결 재사용 영향 | keep-alive 클라이언트 소수가 대량 요청 | 설계한 단위(연결·요청)로 분산     | 소수 연결이 특정 백엔드에 고정 |

### 장애와 복귀

| 케이스               | 입력                             | 기대 결과                                | 실패 판정                               |
|----------------------|----------------------------------|------------------------------------------|-----------------------------------------|
| 백엔드 프로세스 중지 | 백엔드 하나 중지                 | 감지 시간 안에 제외, 이후 오류 없음      | 계속 요청 전달, 감지 시간 초과          |
| 응답 지연            | 백엔드 하나가 느리게 응답        | 점검 timeout으로 제외 또는 설계대로 유지 | 전체 응답 지연                          |
| 점검만 통과          | 점검 경로는 200, 실제 경로는 500 | 점검 경로가 실제 의존성을 반영해 제외    | 장애 백엔드가 계속 분산 대상            |
| 복귀                 | 중지한 백엔드 재시작             | 연속 성공 횟수 후 복귀                   | 첫 성공에 바로 복귀해 상태가 흔들림     |
| 전체 장애            | 모든 백엔드 중지                 | 설계된 오류 응답(503 등)·대체 백엔드     | 무한 대기, 내부 정보가 담긴 오류 페이지 |
| 상태 진동(flapping)  | 점검이 성공·실패를 반복          | `rise`·`fall`로 상태 변화 억제           | 짧은 주기로 제외·복귀 반복              |

### 운영 작업

| 케이스           | 입력                              | 기대 결과                            | 실패 판정                  |
|------------------|-----------------------------------|--------------------------------------|----------------------------|
| drain            | 백엔드를 drain 상태로 변경        | 새 요청 배정 중단, 처리 중 요청 완료 | 처리 중 요청 절단          |
| 점검 모드(maint) | 백엔드를 maint 상태로 변경        | 모든 트래픽과 점검 중단              | 트래픽 계속 유입           |
| 가중치 변경      | 운영 중 가중치 0으로 변경         | 새 요청 배정 중단                    | 변경 미반영                |
| 순차 배포        | 백엔드를 하나씩 빼고 배포 후 복귀 | 배포 내내 오류율 변화 없음           | 교체 순간마다 오류 발생    |
| 증설             | 백엔드 추가                       | 점검 통과 후 분산 대상 포함          | 준비 전 요청 수신으로 오류 |

HAProxy의 `drain` 상태는 분산 대상에서만 빠지고 점검과 기존 세션 고정 연결은 계속 받습니다. `maint`는 모든 트래픽과 점검을 멈춥니다. 두 상태의 차이를 운영 절차에 반영했는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 검증 도구

| 도구                | 용도                                               |
|---------------------|----------------------------------------------------|
| 백엔드 식별 응답    | 응답 헤더·본문에 백엔드 이름을 넣어 분산 결과 집계 |
| `curl` 반복 요청    | 분산 분포와 세션 고정 확인                         |
| HAProxy Runtime API | 서버 상태 조회, drain·maint·가중치 변경            |
| LB 접근 로그        | 요청별 선택 백엔드와 재시도 기록                   |
| 부하 도구           | 장애·배포 중 오류율 측정                           |

### 명령 예시

```bash
# 새 연결로 100번 요청해 백엔드별 분포 집계 (응답 헤더 X-Backend 기준 테스트 서버)
for i in $(seq 1 100); do
  curl -sS -o /dev/null -D - https://www.example.com/ | grep -i '^x-backend:'
done | sort | uniq -c

# 쿠키를 유지하며 세션 고정 확인
curl -sS -c /tmp/lb_cookie.txt -b /tmp/lb_cookie.txt -o /dev/null -D - https://www.example.com/ \
  | grep -i '^x-backend:'

# HAProxy Runtime API: 서버 상태 조회와 drain
echo "show servers state web_backend" | socat stdio /run/haproxy/admin.sock
echo "set server web_backend/app1 state drain" | socat stdio /run/haproxy/admin.sock
echo "set server web_backend/app1 state ready" | socat stdio /run/haproxy/admin.sock
```

장애 감지 시간은 백엔드를 중지한 시각과 LB 로그에서 마지막으로 그 백엔드에 요청이 간 시각의 차이로 측정합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

| 증상                        | 우선 확인 대상                                          |
|-----------------------------|---------------------------------------------------------|
| 가중치와 다른 분포          | 연결 재사용 단위, 여러 LB 인스턴스의 독립 계산          |
| 장애 백엔드로 계속 요청     | 점검 경로가 실제 의존성을 반영하는지, 수동 판정 설정    |
| 장애 시 오류가 수 초간 지속 | `inter`·`fall`·점검 timeout, 재시도(`redispatch`) 설정  |
| 복귀 직후 오류              | 백엔드 준비 완료 전 점검 통과, 점검 경로가 너무 단순    |
| drain 중 요청 절단          | drain 대기 시간, 백엔드 종료 순서                       |
| 세션 고정 실패              | 쿠키 속성(도메인·경로·Secure), 백엔드 변경 후 쿠키 처리 |

### 분석 원칙

- 분포는 새 연결 기준과 keep-alive 연결 기준을 따로 측정합니다.
- 장애 시나리오에서는 오류 수와 오류 지속 시간을 함께 기록합니다.
- 점검 경로의 응답 조건(의존성 포함 여부)을 문서화하고 그 조건으로 케이스를 만듭니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 분산 방식·가중치·hash·세션 고정 결과를 집계로 확인했습니다.
- [ ] 능동 점검과 수동 판정 중 실제 사용 방식을 확인했습니다.
- [ ] 백엔드 중지·지연·부분 장애의 감지 시간과 오류 수를 측정했습니다.
- [ ] 복귀 조건과 상태 진동 억제를 확인했습니다.
- [ ] 전체 장애 시 응답을 확인했습니다.
- [ ] drain·maint·가중치 변경·순차 배포 중 오류율을 확인했습니다.

## 참고 자료

- nginx ngx_http_upstream_module: [nginx.org](https://nginx.org/en/docs/http/ngx_http_upstream_module.html) — ★★★☆☆
- HAProxy Configuration Manual 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/configuration.html) — ★★★☆☆
- HAProxy Management Guide 3.2: [docs.haproxy.org](https://docs.haproxy.org/3.2/management.html) — ★★★☆☆
- [Reverse Proxy 테스트](reverse_proxy_testing.md)
- [Graceful Reload 테스트](graceful_reload_testing.md)
- [장애 주입 테스트](../testing/04_test_design/fault_injection_testing.md)

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
