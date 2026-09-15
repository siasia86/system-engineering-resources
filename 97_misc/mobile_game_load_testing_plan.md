# 모바일 게임 사전 오픈 부하 테스트 계획서
<!-- reference: _reference/csharp_official_notes.md, _reference/api_styles_official_notes.md, _reference/mobile_device_testing_official_notes.md -->

게임 클라이언트가 Unity 기반이고 Node.js·C# 서버와 웹/API 계층으로 구성된 서비스를 대상으로, 정식 서비스 오픈 전에 부하·성능·복구 능력을 검증하기 위한 계획서입니다. 실제 수치와 운영 정책은 서비스별 SLO와 인프라 사양을 입력하여 확정합니다.

## 목차

| 섹션                                                                                                                                             |
|--------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 목적과 범위](#1-목적과-범위) / [2. 사전 입력 정보](#2-사전-입력-정보) / [3. 부하 모델과 테스트 기법](#3-부하-모델과-테스트-기법)             |
| [4. 테스트 케이스](#4-테스트-케이스) / [5. 도구와 테스트 데이터](#5-도구와-테스트-데이터) / [6. 관측 지표와 판정 기준](#6-관측-지표와-판정-기준) |
| [7. 실행 절차와 롤백](#7-실행-절차와-롤백) / [8. 결과 보고와 오픈 승인](#8-결과-보고와-오픈-승인)                                                |

---

## 1. 목적과 범위

### 테스트 목적

- 예상 최대 동시 접속자 수와 피크 트래픽에서 서비스가 SLO를 만족하는지 확인합니다.
- Node.js API의 이벤트 루프 지연, C# 게임 서버의 처리량·스레드풀·GC, DB·캐시·메시지 큐의 병목을 확인합니다.
- 로그인 폭주, 매칭·방 생성, 게임 명령, 저장·랭킹, 재접속 등 실제 사용자 여정을 검증합니다.
- 오토스케일링, 장애 전환, 연결 재수립, 부하 종료 후 회복 시간을 검증합니다.
- 서비스 오픈 전에 중단 기준과 롤백 절차를 합의합니다.

### 대상 아키텍처 모델

```text
Unity Mobile Client
        │ HTTPS / WebSocket
        v
CDN / WAF / Load Balancer
        │
        ├── Node.js Web / BFF / Auth API
        │       ├── Cache
        │       ├── Session Store
        │       └── Message Queue
        │
        ├── C# Game Server / Match / Room
        │       └── Game State Store
        │
        └── Database / Object Storage / External Provider
```

다이어그램은 일반적인 범위를 나타냅니다. 실제 테스트에서는 인증, 웹 API, 실시간 연결, 게임 서버, 저장 계층을 분리하여 각 계층의 포화 지점을 식별합니다.

### 범위와 제외 범위

| 구분       | 포함 범위                                              | 제외 또는 별도 검증 범위                  |
|------------|--------------------------------------------------------|-------------------------------------------|
| 클라이언트 | Unity 프로토콜 흐름, 재접속, 소수 실기기 성능          | 수천 대의 실제 모바일 기기 동시 실행      |
| 웹/API     | 로그인, 토큰, 로비, 매칭, 인벤토리, 랭킹, 결제 sandbox | 실제 결제 승인과 환불                     |
| 게임 서버  | 방 생성, 입장, 게임 명령, 상태 동기화, 이탈·재접속     | 운영 데이터에 대한 파괴적 명령            |
| 인프라     | LB, 오토스케일링, DB, 캐시, 큐, CDN, 모니터링          | 승인 없는 운영 환경 장애 주입             |
| 외부 연동  | 허용된 sandbox 또는 mock의 지연·오류 응답              | 외부 사업자 production endpoint 직접 부하 |

> CCU(Concurrent Users): 특정 시점에 동시에 접속 중인 사용자 수입니다. CCU는 초당 요청 수(RPS)와 같지 않으며, 사용자의 행동 빈도·연결 방식·세션 길이에 따라 실제 서버 부하가 달라집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사전 입력 정보

테스트 실행 전에 다음 정보를 서비스 오너·개발·인프라·QA가 함께 확정합니다. 값이 비어 있으면 테스트 결과를 오픈 승인 근거로 사용하지 않습니다.

### 필수 입력 체크리스트

| 영역        | 필요한 정보                                                             | 담당자·상태 |
|-------------|-------------------------------------------------------------------------|-------------|
| 서비스 목표 | 목표 CCU, 최대 CCU, 피크 지속 시간, 지역별 사용자 비율                  | [TBD]       |
| 사용자 행동 | 로그인 비율, 분당 API 호출, 매칭·게임·저장·채팅 비율                    | [TBD]       |
| API 계약    | endpoint, method, 인증 방식, 요청·응답 크기, rate limit, idempotency    | [TBD]       |
| 실시간 통신 | WebSocket 또는 기타 연결 방식, heartbeat, 메시지 빈도, 방당 인원        | [TBD]       |
| 서버 구성   | Node.js·C# 인스턴스 수와 사양, 프로세스 모델, 오토스케일 정책           | [TBD]       |
| 데이터 계층 | DB 종류·pool, cache, queue, read replica, 샤딩·파티션, 백업 정책        | [TBD]       |
| 외부 의존성 | 인증·결제·푸시·광고·분석 provider의 sandbox, quota, timeout, mock 정책  | [TBD]       |
| 성공 기준   | endpoint별 P95/P99, 오류율, 회복시간, 허용 resource headroom            | [TBD]       |
| 운영 안전   | 테스트 시간, source IP allowlist, kill switch, 담당자 연락망, 중단 권한 | [TBD]       |
| 관측 가능성 | Grafana/Zabbix/ELK 대시보드, 로그 correlation ID, tracing, 알림 조건    | [TBD]       |

### 환경 기준

- 테스트 환경은 production과 동일한 주요 설정·배포 artifact·DB schema를 사용합니다.
- 불가피하게 축소한 환경은 CPU·메모리·인스턴스 수와 실제 환경의 비율을 문서에 기록합니다.
- 테스트 계정과 테스트 데이터는 별도 namespace 또는 prefix를 사용합니다.
- 실제 사용자, 실제 결제, 실제 푸시 대상, 실제 운영 DB를 사용하지 않습니다.
- 부하 생성기 source IP는 allowlist에 등록하고, 테스트 종료 후 규칙을 제거합니다.
- 테스트 중 생성된 데이터와 토큰을 식별할 수 있도록 `test_run_id`를 모든 요청과 로그에 전달합니다.

### 오픈 전 위험 승인

다음 항목은 부하 테스트 계획 승인 없이 실행하지 않습니다.

- 운영 환경에 직접 부하를 보내는 테스트.
- DB failover, cache flush, queue 중단 등 장애 주입.
- 외부 결제·인증·푸시 provider에 요청을 보내는 테스트.
- 대량 계정 생성, 데이터 삭제, 토큰 무효화가 포함된 테스트.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 부하 모델과 테스트 기법

### CCU와 요청량 계산

간단한 초기 추정은 다음과 같이 계산합니다.

```text
API RPS = 활성 사용자 수 × 사용자 1명당 분당 요청 수 ÷ 60
피크 RPS = 피크 CCU × 행동별 요청 비율을 반영한 가중 요청량
연결 수 = 활성 사용자 수 × 사용자당 동시 연결 수
```

실제 테스트에서는 평균값만 사용하지 않고 로그인·매칭·게임 시작·보상 지급처럼 순간적으로 집중되는 행동을 별도 모델링합니다. CCU, RPS, WebSocket 연결 수, 메시지율은 각각 독립적인 입력값으로 관리합니다.

### 테스트 기법

| 기법             | 목적                                  | 부하 형태                    | 종료 조건                      |
|------------------|---------------------------------------|------------------------------|--------------------------------|
| 기준선 테스트    | 무부하·저부하 정상 동작과 기준값 확보 | 소수 사용자                  | 기준 지표와 로그 확보          |
| 부하 테스트      | 예상 정상 피크에서 SLO 확인           | 목표 부하 ramp-up·steady     | 목표 시간과 성공 기준 충족     |
| 스트레스 테스트  | 한계점과 오류 양상 확인               | 목표 초과 점진 증가          | 사전 중단 기준 도달            |
| 스파이크 테스트  | 로그인·이벤트 폭증 대응 확인          | 짧은 시간 급격한 증가·감소   | 오류·queue·scale-out 상태 확인 |
| 내구성 테스트    | 장시간 누수·누적 지연 확인            | 일정 부하 장시간 유지        | 메모리·GC·연결 수 추세 안정    |
| 확장성 테스트    | 인스턴스 추가 효과와 병목 확인        | 인스턴스 수별 동일 부하 비교 | 선형성·비선형 병목 확인        |
| 복구 테스트      | 부하 종료·재시작·장애 후 회복 확인    | 장애 전후 부하 유지          | RTO와 데이터 정합성 충족       |
| 연결 수명 테스트 | WebSocket heartbeat·재접속 확인       | 장시간 연결과 동시 재접속    | 연결 누수·재접속 폭주 없음     |

### 권장 실행 순서

```text
1. 기준선
   │ 정상 응답·로그·대시보드 확인
   v
2. 목표 부하
   │ ramp-up → steady → ramp-down
   v
3. 피크·스파이크
   │ 로그인 폭주와 재접속 집중 검증
   v
4. 스트레스
   │ 중단 기준을 지키며 한계점 확인
   v
5. 내구성
   │ 장시간 누수·성능 저하 확인
   v
6. 복구
   │ 부하 종료·장애 복구·데이터 정합성 확인
```

각 단계가 실패하면 다음 단계로 진행하지 않고 원인 분석과 재현 테스트를 먼저 수행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 테스트 케이스

다음 표는 초안입니다. 실제 endpoint와 사용자 행동 비율을 입력하여 테스트 스크립트와 연결합니다.

| ID    | 시나리오                  | 부하 모델                     | 핵심 검증 항목                                  | 중단·판정 기준                 |
|-------|---------------------------|-------------------------------|-------------------------------------------------|--------------------------------|
| LT-01 | 서비스 기준선             | 소수 계정, 10분               | 정상 응답, 로그, trace, 대시보드                | 기준값 미확보 시 중단          |
| LT-02 | 로그인·토큰 발급 폭주     | 짧은 ramp-up 후 피크          | 인증 latency, rate limit, DB·cache, 실패 재시도 | 인증 장애 또는 계정 잠금 폭증  |
| LT-03 | 로비·heartbeat            | 목표 CCU, 장시간 연결         | 연결 수, heartbeat, 세션 TTL, event loop        | 연결 누수·재접속 폭주          |
| LT-04 | 매칭·방 생성·입장         | 행동 비율 기반 동시 요청      | queue 대기, 매칭 latency, room capacity         | 매칭 queue 무한 증가           |
| LT-05 | 게임 명령·상태 동기화     | 방 수·방당 인원·메시지율 기반 | C# 처리량, tick 지연, 메시지 loss, 순서 보장    | 상태 불일치·지연 급증          |
| LT-06 | 인벤토리·퀘스트 저장      | 게임 중 일정 비율의 write     | DB write, transaction, lock, retry              | 데이터 유실·중복 지급          |
| LT-07 | 랭킹·리더보드             | 조회 집중 + 갱신 혼합         | read replica, cache hit, 정렬 latency           | stale data 정책 위반           |
| LT-08 | 채팅·알림                 | 방·채널별 메시지 burst        | queue lag, fan-out, moderation path             | 메시지 유실·중복·지연          |
| LT-09 | 결제 sandbox·보상 지급    | 승인된 test product만 사용    | idempotency, timeout, 보상 중복 방지            | 실제 결제 endpoint 호출        |
| LT-10 | 패치·정적 리소스 다운로드 | 지역·기기별 동시 다운로드     | CDN hit, origin load, bandwidth, cache policy   | origin 과부하·캐시 우회        |
| LT-11 | 네트워크 단절·재접속      | 연결 중 단절 후 동시 재접속   | reconnect storm, session recovery, token        | 중복 세션·데이터 충돌          |
| LT-12 | 장애 전환·복구            | 목표 부하 중 제한된 failover  | RTO, 오류 전파, 데이터 정합성, 알림             | 승인된 중단 기준 초과          |
| LT-13 | 오토스케일링              | 목표 피크 ramp-up·ramp-down   | scale-out 지연, warm-up, scale-in 안전성        | 새 instance 준비 전 queue 고갈 |
| LT-14 | 장시간 내구성             | 일정 CCU를 장시간 유지        | heap, GC, fd, connection, queue, DB pool        | 지속 증가 추세·누수            |

### Unity 클라이언트 별도 검증

수천 개의 Unity 앱을 단일 부하 생성기에서 실행하는 방식은 서버 부하와 모바일 기기 부하를 혼합하므로 해석이 어렵습니다. 다음 두 계층을 분리합니다.

- 프로토콜 부하: 부하 생성기로 HTTP·WebSocket·게임 메시지를 재현하여 서버 처리량과 응답을 검증합니다.
- 실기기 검증: 대표 OS·기기 등급·네트워크별 소수 기기로 로그인, 플레이, 재접속, 패치, 발열·배터리·메모리를 검증합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 도구와 테스트 데이터

### 도구 선택 기준

| 대상        | 필요한 기능                                  | 도구 선택 기준                           |
|-------------|----------------------------------------------|------------------------------------------|
| HTTP/API    | 시나리오, 인증, payload, percentile          | 스크립트 관리·분산 실행·CI 연동          |
| WebSocket   | 연결 유지, heartbeat, 메시지율, 재접속       | 장시간 연결과 custom protocol 지원       |
| 부하 분산   | 여러 worker, 목표 RPS·CCU 제어               | generator 자체가 병목이 되지 않는지 확인 |
| 관측        | metrics, logs, traces, correlation ID        | Grafana·Zabbix·ELK와 시간축 통합         |
| 실기기      | FPS, memory, battery, crash, network profile | 대표 기기군과 자동 수집 지원             |
| 데이터 검증 | 중복·유실·순서·잔여 세션 확인                | DB read-only 조회와 test_run_id 필터     |

`k6`, `Locust`, `JMeter`, `Artillery` 등은 HTTP·WebSocket 지원 범위와 팀 운영 경험을 비교하여 선택합니다. 단일 도구를 먼저 정하기보다 프로토콜, 시나리오 재현성, 분산 실행, 결과 보존을 기준으로 결정합니다.

### 테스트 데이터 설계

- 계정 pool은 목표 CCU보다 충분히 크게 준비하여 동일 계정 경합을 방지합니다.
- 계정 상태를 신규, 튜토리얼 완료, 고레벨, 아이템 보유, 결제 sandbox 사용자로 분류합니다.
- 모든 생성 데이터에 `test_run_id`, `user_type`, `region`, `device_profile`을 기록합니다.
- 요청 ID와 결제·보상·저장 작업에는 idempotency key를 사용하여 재시도 중복을 검증합니다.
- 랜덤 행동은 seed를 기록하여 동일 시나리오를 재현할 수 있게 합니다.
- 개인정보·실제 계정·실제 결제수단은 사용하지 않습니다.

### 부하 생성기 배치

```text
Load Generator Workers
  ├── Region A / Network profile 1
  ├── Region B / Network profile 2
  └── Region C / Network profile 3
             │
             v
      Test Gateway / Allowlist
             │
             v
       Game Service Stack
```

부하 생성기 CPU·메모리·네트워크와 대상 서비스의 지표를 같은 시간축으로 저장합니다. 생성기 포화로 인해 대상 서비스가 느려진 것처럼 보이는 false positive를 방지해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 관측 지표와 판정 기준

### 사용자 경험 지표

| 영역        | 지표                                                    |
|-------------|---------------------------------------------------------|
| 인증        | 로그인 성공률, login P50/P95/P99, token refresh latency |
| API         | endpoint별 RPS, P50/P95/P99, timeout, 4xx·5xx           |
| 실시간 연결 | 연결 성공률, 연결 수, heartbeat 지연, reconnect rate    |
| 게임 플레이 | 명령 처리 latency, tick 지연, 방 입장 시간, 상태 불일치 |
| 데이터      | 저장 성공률, 중복·유실·순서 오류, 보상 지급 정합성      |
| 패치        | 다운로드 성공률, CDN hit ratio, origin 응답 시간        |

### 계층별 운영 지표

| 계층          | 필수 지표                                                         |
|---------------|-------------------------------------------------------------------|
| Load Balancer | active connection, request count, target error, queue, latency    |
| Node.js       | event loop delay, heap, GC, active handle, process restart        |
| C# / .NET     | CPU, heap, GC pause, thread pool, exception, queue, tick time     |
| Database      | CPU, memory, connection pool, lock, slow query, IOPS, replica lag |
| Cache         | hit ratio, memory, eviction, connection, command latency          |
| Message Queue | publish·consume rate, lag, retry, dead letter, consumer health    |
| Network·CDN   | bandwidth, packet loss, RTT, cache hit, origin traffic            |
| Mobile client | FPS, memory, battery, thermal, crash, app response                |

### 판정 기준 템플릿

절대값은 서비스 오너가 SLO와 business impact를 기준으로 승인합니다. 아래 값은 문서 작성용 입력 양식입니다.

| 판정 항목              | 목표값                                  | 측정 범위               | 승인 상태 |
|------------------------|-----------------------------------------|-------------------------|-----------|
| 목표 CCU               | `[예: peak CCU]`                        | 전체·지역별             | [TBD]     |
| 핵심 API P95/P99       | `[endpoint별 SLO]`                      | steady·spike 각각       | [TBD]     |
| 핵심 게임 명령 latency | `[명령별 SLO]`                          | 방·지역·기기 프로파일별 | [TBD]     |
| 5xx·timeout 오류율     | `[허용률]`                              | 전체·핵심 endpoint별    | [TBD]     |
| 데이터 정합성          | 중복·유실·순서 오류 없음 또는 승인 기준 | test_run_id 전체        | [TBD]     |
| Resource headroom      | `[CPU·memory·pool 여유 기준]`           | peak steady 구간        | [TBD]     |
| 오토스케일             | `[scale-out 시간·최소 instance]`        | ramp-up·ramp-down       | [TBD]     |
| 복구 시간              | `[RTO]`                                 | 장애·부하 종료 후       | [TBD]     |

P95와 P99는 평균 응답 시간만으로 보이지 않는 꼬리 지연을 확인하기 위한 백분위 지표입니다. 평균이 정상이어도 P99가 급증하면 일부 사용자에게 심각한 지연이 발생할 수 있습니다.

### 중단 기준

다음 조건 중 하나라도 발생하면 즉시 부하를 동결하거나 ramp-down하고 담당자에게 알립니다.

- 실제 운영 데이터 또는 실제 결제·푸시 대상에 접근하는 징후가 발생합니다.
- 데이터 유실, 중복 지급, 인증 우회, 개인정보 노출이 발견됩니다.
- 핵심 API의 오류·timeout이 승인된 한도를 초과합니다.
- DB connection pool, queue, cache, 파일 디스크립터가 회복되지 않고 증가합니다.
- 서비스의 autoscale·failover가 예상과 다르게 동작하거나 운영 알림이 발생합니다.
- 부하 생성기 또는 네트워크가 대상 서비스와 구분되지 않을 정도로 포화됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실행 절차와 롤백

### 실행 절차

1. 테스트 승인자, 실행자, 개발·인프라·DB 담당자, 중단 권한자를 지정합니다.
2. 테스트 환경·artifact·schema·feature flag·외부 provider sandbox를 확인합니다.
3. 대시보드와 알림을 먼저 활성화하고 기준선 테스트를 실행합니다.
4. 낮은 부하에서 계정·데이터·로그·trace 정합성을 확인합니다.
5. 목표 부하를 단계적으로 올리고 각 단계마다 checkpoint를 기록합니다.
6. 목표 부하, 스파이크, 스트레스, 내구성, 복구 테스트를 승인된 순서로 실행합니다.
7. 테스트 종료 후 오류·queue·연결·resource가 기준선으로 회복되는지 확인합니다.
8. 테스트 데이터와 토큰을 정리하고 결과 보고서를 작성합니다.

### 실행 기록

```text
Test run ID       : [예: preopen-YYYYMMDD-01]
Environment       : [dev / qa / stg]
Build / image     : [artifact digest 또는 build ID]
Start / end       : [UTC 또는 KST를 명시]
Target CCU       : [값]
Target RPS       : [값]
Load generator   : [도구·버전·worker 수]
Scenario set     : [LT-01, LT-02, ...]
Approver         : [담당자]
Stop authority   : [담당자]
Result           : [PASS / FAIL / BLOCKED]
```

### 롤백과 정리

부하 테스트는 먼저 부하 생성기를 중단하고, 이후 테스트 환경을 원상 복구합니다.

1. 부하 생성기의 ramp-down 또는 즉시 중단을 실행합니다.
2. 테스트 전용 feature flag, allowlist, route, mock provider를 원복합니다.
3. 테스트 계정의 token·session·queue·cache·DB 데이터를 `test_run_id` 기준으로 정리합니다.
4. 오토스케일된 instance와 임시 리소스가 정상 정책으로 돌아왔는지 확인합니다.
5. 변경된 설정과 dashboard·alert를 baseline으로 복원합니다.
6. 오류 로그와 결과 artifact는 보존하되, credential·개인정보·실제 payload는 제거합니다.

테스트 중 서비스가 비정상 상태가 되면 원인 분석 전 반복 실행하지 않습니다. 마지막 정상 checkpoint, 변경 내역, 로그·메트릭·trace를 보존한 뒤 실패 지점을 줄여 재현합니다.

### 실제 운영 환경 테스트 원칙

정식 오픈 전 production 부하 테스트가 불가피한 경우에는 별도 승인과 제한 조건이 필요합니다.

- 사전 승인된 시간·지역·source IP·endpoint만 사용합니다.
- 실제 결제·푸시·광고·외부 provider는 mock 또는 sandbox로 격리합니다.
- 고객 트래픽과 테스트 트래픽을 `test_run_id`로 분리합니다.
- 점진적 canary부터 시작하고, 자동 kill switch와 담당자 대기를 준비합니다.
- 장애 주입과 데이터 파괴 테스트는 production에서 실행하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 결과 보고와 오픈 승인

### 결과 보고서 구성

| 항목        | 기록 내용                                                     |
|-------------|---------------------------------------------------------------|
| 요약        | 테스트 목적, 실행 기간, 최종 결과, 주요 발견사항              |
| 환경        | build, instance, DB·cache·queue 사양, 지역, 네트워크 프로파일 |
| 부하        | CCU, RPS, 연결 수, 메시지율, ramp-up, steady, spike 구간      |
| 사용자 지표 | endpoint·시나리오별 P50/P95/P99, 오류·timeout, 성공률         |
| 계층 지표   | Node.js, C# / .NET, DB, cache, queue, network, CDN, client    |
| 병목과 원인 | 증상, 근거 metric·log·trace, root cause, 영향 범위            |
| 조치        | 수정 내용, 담당자, 완료일, 재테스트 결과                      |
| 잔여 위험   | 미해결 항목, 우회책, 모니터링, 오픈 후 대응                   |
| 승인        | QA·개발·인프라·서비스 오너의 PASS 또는 조건부 승인            |

### 오픈 승인 기준

다음 항목을 모두 충족해야 정식 오픈 승인 대상으로 올립니다.

- [ ] 목표 CCU와 피크 부하에서 핵심 사용자 여정이 승인된 SLO를 충족합니다.
- [ ] 핵심 API·게임 명령의 오류율과 P99가 승인 기준 이내입니다.
- [ ] 로그인 폭주·재접속 폭주·오토스케일링이 검증되었습니다.
- [ ] DB·cache·queue의 병목과 용량 여유가 설명되었습니다.
- [ ] 장시간 테스트에서 memory·GC·connection·queue의 누수 증거가 없습니다.
- [ ] 테스트 종료 후 서비스와 데이터가 baseline으로 회복되었습니다.
- [ ] 알림·대시보드·runbook·중단 권한자가 준비되었습니다.
- [ ] 미해결 위험에 담당자·기한·완화책이 지정되었습니다.

### 미결 사항

- 실제 목표 CCU와 지역별 피크 분포: `[TBD]`
- 핵심 사용자 여정과 endpoint별 행동 비율: `[TBD]`
- Node.js·C# 서버별 인스턴스 사양과 오토스케일 정책: `[TBD]`
- Unity 지원 기기군·네트워크 프로파일: `[TBD]`
- DB·cache·queue 용량 및 failover 정책: `[TBD]`
- endpoint별 SLO, 오류 허용률, RTO: `[TBD]`
- 테스트 승인자와 즉시 중단 권한자: `[TBD]`

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- [성능/부하 테스트](../01_fundamentals/cs/testing/03_test_levels/performance_testing.md) — 기존 테스트 유형·지표·도구 정리
- [게임 서버 아키텍처](game_server_architecture.md) — 서버 처리 구조와 유형
- [게임 서비스 인프라 운영 핵심 지표](../02_infrastructure/monitoring/game_infra_kpi_presentation.md) — 가용성·지연·CCU·리소스 지표
- [C# / .NET 공식 참조 노트](../_reference/csharp_official_notes.md) — C#·.NET 버전과 비동기 처리 참고
- [API Styles 공식 참조 노트](../_reference/api_styles_official_notes.md) — REST·WebSocket 등 API 스타일 참고

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-15

**마지막 업데이트**: 2026-09-15

© 2026 siasia86. Licensed under CC BY 4.0.
