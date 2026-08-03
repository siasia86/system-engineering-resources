# Chaos Engineering

프로덕션 환경에서 의도적으로 장애를 주입하여 시스템의 약점을 사전에 발견하는 엔지니어링 분야입니다. principlesofchaos.org를 기반으로 합니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원칙](#2-원칙) / [3. 실험 설계](#3-실험-설계)                           |
| [4. 폭발 반경 제어](#4-폭발-반경-제어) / [5. 실험 유형](#5-실험-유형) / [6. 도구](#6-도구)       |
| [7. 운영 절차](#7-운영-절차) / [8. 성숙도 모델](#8-성숙도-모델) / [9. 트러블슈팅](#9-트러블슈팅) |

## 1. 개요

| 항목 | 값                                                            |
|------|---------------------------------------------------------------|
| 정의 | 시스템이 혼란 상황을 견딜 수 있다는 확신을 구축하기 위한 실험 |
| 출처 | principlesofchaos.org (Netflix 기원, 2011)                    |
| 핵심 | 가설 기반 실험, 프로덕션 수행, 폭발 반경 최소화               |
| 전제 | 모니터링 + 알림 + 자동 중단 조건이 준비된 후 시작             |
| 연관 | Incident Management (실험 실패 시), SLO (정상 상태 정의 기준) |

## 2. 원칙

### Principles of Chaos Engineering (공식)

| 원칙                                     | 설명                                            |
|------------------------------------------|-------------------------------------------------|
| Build Hypothesis around Steady State     | 정상 상태를 정량적으로 정의 (SLI 활용)          |
| Vary Real-world Events                   | 실제 일어날 수 있는 장애를 주입                 |
| Run Experiments in Production            | 스테이징은 프로덕션과 다름 — 실제 환경에서 수행 |
| Automate Experiments to Run Continuously | 일회성이 아닌 지속적 실험으로 회귀 방지         |
| Minimize Blast Radius                    | 실험 범위를 최소화하여 실제 장애 방지           |

> 위 5원칙은 principlesofchaos.org에 명시된 공식 원칙입니다. Netflix의 Chaos Monkey(2011)에서 시작되어 커뮤니티가 정립했습니다.
> — https://principlesofchaos.org/

### Chaos Engineering이 아닌 것

| 오해                 | 실제                                        |
|----------------------|---------------------------------------------|
| 무작위로 서버 끄기   | 가설 기반의 통제된 실험                     |
| 장애 유발 놀이       | 시스템 신뢰성을 증명하기 위한 과학적 방법론 |
| 프로덕션 테스트 대체 | 기존 테스트를 보완하는 추가 레이어          |

## 3. 실험 설계

### 실험 구조

```
1. Define Steady State (정상 상태 정의)
     │
     v
2. Hypothesize (가설 수립)
   "System will maintain steady state during X failure"
     │
     v
3. Inject Failure (장애 주입)
     │
     v
4. Observe (관찰)
   SLI deviation? Alert fired? Auto-recovery?
     │
     v
5. Conclude (결론)
   Hypothesis confirmed or disproved
     │
     v
6. Fix (수정 — 가설 반증 시)
```

### 가설 예시

| 가설                          | 주입 장애               | 기대 결과                       |
|-------------------------------|-------------------------|---------------------------------|
| "AZ 1개 손실 시 서비스 유지"  | AZ-a 인스턴스 전체 종료 | Error rate < 1%, latency < 2x   |
| "DB failover 시 30초 내 복구" | Primary DB 강제 종료    | Replica 승격, 연결 30초 내 복구 |
| "DNS 장애 시 캐시로 지속"     | DNS 응답 차단           | TTL 내 정상 서비스              |

## 4. 폭발 반경 제어

### 제어 레벨

| 레벨    | 범위            | 적합 단계        |
|---------|-----------------|------------------|
| Canary  | 단일 인스턴스   | 첫 실험          |
| Subset  | 10% 트래픽/서버 | 검증된 실험 확장 |
| Full AZ | AZ 단위         | 성숙 단계        |
| Region  | 리전 단위       | 고급 (DR 검증)   |

### 자동 중단 조건 (Stop Condition)

```yaml
# AWS FIS 예시
stopConditions:
  - source: "aws:cloudwatch:alarm"
    value: "arn:aws:cloudwatch:...:alarm:HighErrorRate"

# 기준 예시
abort_if:
  error_rate: "> 5% for 2min"
  latency_p99: "> 5s for 2min"
  customer_impact: "any support ticket"
```

### 롤백 보장

- 모든 실험은 자동 롤백 메커니즘 필수
- 수동 중단 버튼 (Kill Switch) 항상 대기
- 실험 최대 지속 시간 설정 (timeout)

> AWS FIS의 Stop Condition은 CloudWatch Alarm 기반으로 자동 중단을 보장합니다. 모든 FIS 실험에 필수 설정입니다.
> — https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html

## 5. 실험 유형

### 인프라 레벨

| 실험                 | 도구              | 검증 대상               |
|----------------------|-------------------|-------------------------|
| Instance termination | FIS, Chaos Monkey | Auto-scaling, LB health |
| AZ failure           | FIS, Gremlin      | Multi-AZ resiliency     |
| Network latency      | tc netem, FIS     | Timeout 설정, retry     |
| Packet loss          | tc netem, Litmus  | 재전송, circuit breaker |
| Disk full            | FIS, stress-ng    | Alert, graceful degrade |
| CPU stress           | stress-ng, Litmus | Throttling, auto-scale  |

### 애플리케이션 레벨

| 실험               | 방법                      | 검증 대상                  |
|--------------------|---------------------------|----------------------------|
| Dependency failure | Service mesh fault inject | Circuit breaker, fallback  |
| Slow dependency    | Envoy delay injection     | Timeout, bulkhead          |
| Database failover  | RDS reboot, FIS           | Connection retry, failover |
| Cache failure      | ElastiCache node 종료     | Cache miss handling        |
| DNS failure        | Route 53 health fail      | DNS cache, failover        |

## 6. 도구

| 도구         | 유형           | 환경        | 특징                           |
|--------------|----------------|-------------|--------------------------------|
| AWS FIS      | 관리형 서비스  | AWS         | Stop condition, IAM 통합       |
| LitmusChaos  | CNCF Graduated | Kubernetes  | CRD 기반, Resilience Score     |
| Chaos Monkey | Netflix OSS    | Cloud 범용  | 랜덤 인스턴스 종료 (원조)      |
| Gremlin      | 상용 SaaS      | 멀티 환경   | GUI, 안전 장치, 팀 관리        |
| tc netem     | Linux 내장     | Linux       | 네트워크 지연/손실/대역폭 제한 |
| toxiproxy    | Shopify OSS    | Application | TCP 프록시 기반 장애 주입      |

> LitmusChaos는 2022년 CNCF Incubating 승격, 2025년 CNCF Graduated로 졸업되었습니다. AWS FIS는 2021년 GA로 출시되었습니다.
> — https://www.cncf.io/projects/litmus/
> — https://aws.amazon.com/fis/

## 7. 운영 절차

### Game Day 프로세스

```
Before (1주 전):
  - 실험 설계 + 가설 문서화
  - Stop condition 설정
  - 참여자 공지 + 역할 배정
  - Rollback plan 확인

During:
  - IC 지정 (실험 관리자)
  - 실험 시작 공지
  - 모니터링 실시간 관찰
  - 이상 발견 시 즉시 중단

After:
  - 결과 정리 (가설 확인/반증)
  - Action items 도출
  - 다음 실험 계획
```

### 실험 빈도

| 성숙도 | 빈도          | 범위           |
|--------|---------------|----------------|
| 시작   | 분기 1회      | 단일 서비스    |
| 발전   | 월 1회        | 팀 전체 서비스 |
| 성숙   | 주 1회 (자동) | 전체 프로덕션  |

## 8. 성숙도 모델

| 단계 | 이름       | 특징                               |
|------|------------|------------------------------------|
| L1   | Initial    | 수동 Game Day, 비프로덕션 환경     |
| L2   | Repeatable | 프로덕션 실험, 문서화된 절차       |
| L3   | Defined    | 자동화된 실험, CI/CD 연동          |
| L4   | Managed    | 지속적 실험, Resilience Score 추적 |
| L5   | Optimized  | 자동 발견 + 자동 실험 + 자동 수정  |

> Chaos Engineering 성숙도 모델은 Gremlin의 "Chaos Maturity Model"을 참고한 것입니다.
> — https://www.gremlin.com/community/tutorials/chaos-engineering-the-history-principles-and-practice/

## 9. 트러블슈팅

| 증상                      | 원인                  | 해결                                |
|---------------------------|-----------------------|-------------------------------------|
| 실험이 실제 장애로 확대   | Stop condition 미설정 | 모든 실험에 자동 중단 필수화        |
| 팀이 실험을 거부          | 위험 인식, 문화 부재  | 비프로덕션부터 시작, 경영진 지원    |
| 실험 결과를 활용 안 함    | Action item 미추적    | Postmortem과 동일한 추적 프로세스   |
| 항상 가설이 확인됨        | 실험이 너무 약함      | 폭발 반경 점진 확대, 복합 장애 시도 |
| 실험 환경과 프로덕션 차이 | 스테이징에서만 수행   | 프로덕션 canary 범위로 전환         |

## 참고 자료

- Principles of Chaos Engineering: [principlesofchaos.org](https://principlesofchaos.org/) — ★★★★☆
- LitmusChaos: [litmuschaos.io](https://litmuschaos.io/) — ★★★☆☆
- AWS FIS: [docs.aws.amazon.com/fis](https://docs.aws.amazon.com/fis/latest/userguide/) — ★★★☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
