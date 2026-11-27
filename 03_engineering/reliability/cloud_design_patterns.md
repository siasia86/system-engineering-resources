# 클라우드 설계 패턴 (Cloud Design Patterns)
<!-- reference: _reference/cloud_design_patterns_official_notes.md -->

분산·클라우드 시스템에서 반복해서 나오는 문제(가용성, 데이터 관리, 설계와 구현, 관리와 모니터링)에 쓰는 설계 패턴을 정리합니다. Microsoft Azure Architecture Center의 패턴 카탈로그(44개)를 바탕으로, 각 패턴이 무엇을 풀고 언제 쓰는지와 운영에서 만나는 도구를 연결했습니다. 패턴 이름은 클라우드 사업자와 관계없이 통용됩니다.

- 확인일: 2026-11-27, Azure Architecture Center 패턴 카탈로그(2026-11-24 갱신)와 2014년판 Cloud Design Patterns(보관 문서) 대조
- 예제 시험: 개념 문서라 실행하지 않음. 재시도·circuit breaker·bulkhead의 설정과 시험은 [Resilience Patterns](./resilience_patterns.md), 상태 검사와 처리율 제한 시험은 [Envoy](../../02_infrastructure/web_server/envoy.md) 문서에 있음

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 분류 기준](#1-분류-기준) / [2. 가용성](#2-가용성) / [3. 데이터 관리](#3-데이터-관리)                         |
| [4. 설계와 구현](#4-설계와-구현) / [5. 관리와 모니터링](#5-관리와-모니터링) / [6. 그 밖의 패턴](#6-그-밖의-패턴) |
| [7. 패턴 고르기](#7-패턴-고르기) / [8. 주의](#8-주의) / [함께 보기](#함께-보기)                                  |

---

## 1. 분류 기준

- 현재 카탈로그는 영역 분류 없이 패턴마다 관련된 Well-Architected 기둥(Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency)을 표시합니다.
- 2014년판은 문제 영역 8개(Availability, Data Management, Design and Implementation, Messaging, Management and Monitoring, Performance and Scalability, Resiliency, Security)로 나눴습니다. 옛 영역 주소(`patterns/category/availability`)는 지금 Well-Architected의 "Reliability 설계 패턴" 문서로 이어집니다.
- 이 문서는 요청 범위인 4개 영역(가용성, 데이터 관리, 설계와 구현, 관리와 모니터링)으로 묶었습니다. 어느 영역에 넣을지는 이 문서의 판단이며, 표의 "기둥" 열은 현재 카탈로그 표기입니다.

| 기호 | 기둥                   |
|------|------------------------|
| R    | Reliability            |
| S    | Security               |
| CO   | Cost Optimization      |
| OE   | Operational Excellence |
| PE   | Performance Efficiency |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 가용성

장애가 나도 서비스가 계속 응답하게 하는 패턴입니다.

| 패턴                       | 푸는 문제와 방법                                              | 기둥         | 운영에서 만나는 곳                                  |
|----------------------------|---------------------------------------------------------------|--------------|-----------------------------------------------------|
| Health Endpoint Monitoring | 외부 도구가 주기적으로 부르는 상태 확인 엔드포인트를 둠       | R, OE, PE    | 로드밸런서 상태 검사, Kubernetes probe              |
| Queue-Based Load Leveling  | 작업과 서비스 사이에 큐를 둬 순간 부하를 평탄하게             | R, CO, PE    | SQS·Kafka 앞단 버퍼                                 |
| Throttling                 | 앱·테넌트·서비스가 쓰는 자원량을 제한                         | R, S, CO, PE | API 게이트웨이 한도, Envoy 처리율 제한              |
| Rate Limiting              | 자원 소비를 조절해 상대 쪽 throttling 오류를 피하거나 줄임    | R            | 외부 API 호출 클라이언트                            |
| Deployment Stamps          | 데이터 저장소까지 포함한 독립 사본을 여러 벌 배포             | OE, PE       | 리전·고객군별 셀(cell) 구조                         |
| Geode                      | 백엔드를 지리적으로 분산된 노드에 배포, 어느 노드나 요청 처리 | R, PE        | 다중 리전 액티브-액티브                             |
| Retry                      | 예상되는 일시 장애를 재시도로 처리                            | R            | [Resilience Patterns](./resilience_patterns.md) 3절 |
| Circuit Breaker            | 고치는 데 시간이 걸리는 장애에 호출을 잠시 끊음               | R, PE        | [Resilience Patterns](./resilience_patterns.md) 5절 |
| Bulkhead                   | 요소를 풀로 격리해 하나가 실패해도 나머지는 동작              | R, S, PE     | [Resilience Patterns](./resilience_patterns.md) 6절 |
| Leader Election            | 인스턴스 하나를 리더로 뽑아 분산 작업 조정                    | R            | etcd·Raft, Swarm manager                            |

- Health Endpoint Monitoring은 "살아 있음"과 "요청 받을 준비 됨"을 나눠 둡니다. [Envoy](../../02_infrastructure/web_server/envoy.md) 시험에서는 상태 검사 간격 설정에 따라 멈춘 백엔드를 늦게 빼는 경우가 있었습니다.
- Throttling(내가 받는 양 제한)과 Rate Limiting(내가 보내는 양 조절)은 방향이 다릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 데이터 관리

여러 서비스·저장소에 걸친 데이터를 빠르고 일관되게 다루는 패턴입니다.

| 패턴                     | 푸는 문제와 방법                                           | 기둥      | 운영에서 만나는 곳            |
|--------------------------|------------------------------------------------------------|-----------|-------------------------------|
| Cache-Aside              | 필요할 때 저장소에서 읽어 캐시에 넣음                      | R, PE     | Redis 앞단 캐시               |
| CQRS                     | 읽기와 쓰기를 다른 인터페이스로 분리                       | PE        | 읽기 전용 복제본, 검색 인덱스 |
| Event Sourcing           | 현재 상태 대신 일어난 일(이벤트)을 추가 전용 저장소에 기록 | R, PE     | 감사 로그, Kafka 토픽         |
| Sharding                 | 저장소를 수평 분할(shard)                                  | R, CO     | DB 샤딩, 파티션 키            |
| Materialized View        | 조회에 맞게 미리 계산한 뷰를 만듦                          | PE        | 집계 테이블, 통계 대시보드    |
| Index Table              | 자주 조회하는 필드에 인덱스 테이블을 둠                    | R, PE     | NoSQL 보조 인덱스             |
| Valet Key                | 토큰으로 특정 자원에 제한된 직접 접근을 줌                 | S, CO, PE | S3 미리 서명된 URL            |
| Static Content Hosting   | 정적 콘텐츠를 클라우드 저장소에서 바로 제공                | CO        | S3 + CDN 정적 호스팅          |
| Compensating Transaction | 결과적 일관성 작업의 단계들을 되돌리는 보상 작업           | R         | 결제 취소, 주문 롤백          |
| Saga                     | 마이크로서비스 사이 분산 트랜잭션의 일관성 관리            | R         | 주문·재고·결제 연동           |

- Cache-Aside는 캐시와 저장소 값이 잠시 어긋날 수 있습니다. 만료 시간과 쓰기 때 캐시 무효화를 함께 정합니다.
- Valet Key는 서버가 큰 파일을 대신 전달하지 않게 해 비용과 부하를 줄이지만, 토큰 만료 시간과 권한 범위를 좁게 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설계와 구현

서비스 구조를 나누고, 오래된 시스템을 옮기고, 공통 기능을 떼어내는 패턴입니다.

| 패턴                           | 푸는 문제와 방법                                     | 기둥             | 운영에서 만나는 곳               |
|--------------------------------|------------------------------------------------------|------------------|----------------------------------|
| Strangler Fig                  | 레거시 기능을 조금씩 새 시스템으로 바꿔 점진 이전    | R, CO, OE        | 프록시 경로별로 새 서비스로 전환 |
| Anti-Corruption Layer          | 새 앱과 레거시 사이에 변환 계층(façade·adapter)을 둠 | OE               | 레거시 API 래퍼                  |
| Sidecar                        | 부가 기능을 별도 프로세스·컨테이너로 분리            | S, OE            | 서비스 메시 프록시, 로그 수집기  |
| Ambassador                     | 소비자 대신 네트워크 요청을 보내는 도우미 서비스     | R, S             | 외부 API 호출 프록시             |
| Backends for Frontends         | 프런트엔드(웹·모바일)마다 전용 백엔드                | R, S, PE         | 모바일 전용 API 서버             |
| Gateway Routing                | 단일 엔드포인트로 여러 서비스에 라우팅               | R, OE, PE        | API 게이트웨이, Ingress          |
| Gateway Aggregation            | 여러 요청을 게이트웨이에서 하나로 묶음               | R, S, OE, PE     | GraphQL·BFF 집계                 |
| Gateway Offloading             | 공통·특수 기능(TLS, 인증)을 게이트웨이 프록시로 넘김 | R, S, CO, OE, PE | TLS 종료, 인증 프록시            |
| Compute Resource Consolidation | 여러 작업을 하나의 계산 단위로 합침                  | CO, OE, PE       | 작은 작업을 한 컨테이너·노드에   |
| Pipes and Filters              | 복잡한 처리를 재사용 가능한 단계들로 나눔            | R                | 로그 파이프라인                  |

- Strangler Fig은 [리버스 프록시](../../02_infrastructure/web_server/reverse_proxy.md)·[Envoy](../../02_infrastructure/web_server/envoy.md)의 경로·가중치 라우팅으로 구현하는 경우가 많습니다.
- Sidecar는 [서비스 메시](../../02_infrastructure/containers/service_mesh_comparison.md)의 sidecar 프록시가 대표 예입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 관리와 모니터링

운영 중인 시스템의 설정을 바꾸고 상태를 지켜보는 패턴입니다.

| 패턴                         | 푸는 문제와 방법                                               | 기둥      | 운영에서 만나는 곳                        |
|------------------------------|----------------------------------------------------------------|-----------|-------------------------------------------|
| External Configuration Store | 설정을 배포 패키지 밖의 중앙 저장소로 옮김                     | OE        | Consul KV, AWS Parameter Store, ConfigMap |
| Health Endpoint Monitoring   | (2절) 외부 도구가 상태 엔드포인트를 주기적으로 확인            | R, OE, PE | Prometheus blackbox, 로드밸런서           |
| Scheduler Agent Supervisor   | 분산 서비스·자원에 걸친 작업 묶음을 조정·감시                  | R, PE     | 작업 오케스트레이터, 재시도 감독          |
| Quarantine                   | 외부 자산(이미지·패키지)이 합의한 품질 기준을 넘은 뒤에만 사용 | S, OE     | 이미지 검사 뒤 승인 레지스트리로 승격     |
| Sidecar                      | (4절) 모니터링·로깅 agent를 앱과 분리                          | S, OE     | 로그 수집 sidecar                         |

- External Configuration Store에 비밀값을 넣을 때는 [Kubernetes 비밀값 관리](../../04_security/cloud/kubernetes_secrets_management.md)나 [SOPS](../../02_infrastructure/iac/sops.md)처럼 암호화한 저장소를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 그 밖의 패턴

요청 범위 4개 영역 밖(주로 2014년판의 Messaging, Security 영역)에 속하는 카탈로그 패턴입니다.

| 영역(2014년판 기준) | 패턴                                                                                                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 메시징              | Asynchronous Request-Reply, Choreography, Claim Check, Competing Consumers, Idempotent Consumer, Messaging Bridge, Priority Queue, Publisher-Subscriber, Sequential Convoy |
| 보안                | Federated Identity, Gatekeeper                                                                                                                                             |

- 메시징 패턴 가운데 Idempotent Consumer(같은 메시지를 여러 번 처리해도 결과가 같게)는 재시도·큐를 쓰는 모든 시스템에 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 패턴 고르기

| 증상                                   | 먼저 볼 패턴                                  |
|----------------------------------------|-----------------------------------------------|
| 순간 트래픽에 백엔드가 넘어감          | Queue-Based Load Leveling, Throttling         |
| 의존 서비스 장애가 전체로 번짐         | Circuit Breaker, Bulkhead, Retry(백오프 포함) |
| 같은 데이터를 반복 조회해 DB 부하가 큼 | Cache-Aside, Materialized View, CQRS          |
| 레거시를 한 번에 바꾸기 어려움         | Strangler Fig, Anti-Corruption Layer          |
| 리전 장애에도 서비스해야 함            | Geode, Deployment Stamps                      |
| 설정 변경마다 재배포                   | External Configuration Store                  |
| 큰 파일 업로드·다운로드가 서버를 거침  | Valet Key, Static Content Hosting             |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 주의

- 패턴은 복잡도를 더합니다. CQRS·Event Sourcing·Saga는 운영·디버깅 부담이 커서, 문제가 실제로 있을 때 도입합니다.
- 재시도(Retry)는 멱등이 보장될 때만 안전합니다. Idempotent Consumer와 함께 설계합니다.
- 카탈로그에는 피해야 할 설계를 모은 Antipatterns와 AI 에이전트 조정 패턴 문서도 따로 있습니다.
- 7·8절의 "증상→패턴"과 주의 사항은 이 문서의 정리이며, 카탈로그 문장을 옮긴 것은 아닙니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Resilience Patterns](./resilience_patterns.md) — Timeout, Retry, Circuit Breaker, Bulkhead 구현과 설정
- [SLO와 Error Budget](./slo_error_budget.md) — 신뢰성 목표
- [Chaos Engineering](./chaos_engineering.md) — 패턴이 실제로 견디는지 시험
- [AWS 개요](../../02_infrastructure/cloud_aws/aws_overview.md) — Well-Architected 6개 기둥

---

## 참고 자료

- Microsoft: [Cloud design patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/) · [Reliability design patterns](https://learn.microsoft.com/en-us/azure/well-architected/reliability/design-patterns) — ★★★☆☆
- Microsoft(보관): [Cloud Design Patterns (2014)](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/dn568099(v=pandp.10)) · [Problem Areas in the Cloud](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/dn589772(v=pandp.10)) — ★★☆☆☆

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
