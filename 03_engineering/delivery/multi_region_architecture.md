# Multi-Region Architecture

서비스의 가용성과 재해 복구를 위해 다수의 지리적 리전에 인프라를 배치하는 아키텍처 설계 패턴입니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 패턴 비교](#2-패턴-비교) / [3. RPO/RTO 설계](#3-rporto-설계)                    |
| [4. 데이터 동기화](#4-데이터-동기화) / [5. 트래픽 라우팅](#5-트래픽-라우팅) / [6. Failover](#6-failover) |
| [7. 비용 고려사항](#7-비용-고려사항) / [8. 체크리스트](#8-체크리스트) / [9. 트러블슈팅](#9-트러블슈팅)   |

## 1. 개요

| 항목         | 값                                                 |
|--------------|----------------------------------------------------|
| 목적         | 리전 장애 시에도 서비스 연속성 보장                |
| 핵심         | 데이터 동기화 + 트래픽 전환 + Failover 자동화      |
| 트레이드오프 | 가용성 vs 복잡도 vs 비용 vs 데이터 일관성          |
| 전제         | 단일 리전의 SLO로 충분하지 않을 때만 도입          |
| 연관         | SLO (가용성 목표), Capacity Planning (리전별 용량) |

### 도입 판단 기준

| 질문                                                | Yes → Multi-Region | No → Single-Region |
|-----------------------------------------------------|--------------------|--------------------|
| 리전 장애 시 비즈니스 영향이 치명적?                | ✅                 |                    |
| SLO 99.99% 이상 요구? (= 연간 52.6분 이하 다운타임) | ✅                 |                    |
| 규제/법적으로 데이터 지역 분산 필요?                | ✅                 |                    |
| 글로벌 사용자 latency 중요?                         | ✅                 |                    |
| 운영 팀 규모가 충분? (복잡도 감당)                  | ✅                 |                    |

## 2. 패턴 비교

🟡 비용 배수는 일반적 추정치입니다. 실제 비용은 리전별 서비스 구성, DB 크기, 전송량에 따라 편차가 큽니다.

| 패턴           | 정상 상태           | 장애 시                 | RTO     | 비용 배수 |
|----------------|---------------------|-------------------------|---------|-----------|
| Active-Passive | 1 리전 서빙, 1 대기 | DNS 전환 → Passive 활성 | 분~시간 | 1.3~1.5x  |
| Active-Active  | 2+ 리전 동시 서빙   | 장애 리전 트래픽 제외   | 초~분   | 1.8~2.0x  |
| Pilot Light    | 최소 인프라만 대기  | Scale-up 후 전환        | 분~시간 | 1.1~1.3x  |
| Warm Standby   | 축소 인프라 운영 중 | Scale-up + 전환         | 분      | 1.3~1.5x  |

### 아키텍처 비교

```
Active-Passive:
  Region A (Active)          Region B (Passive)
  ┌──────────────┐           ┌──────────────┐
  │  App + DB    │ ──CDC──>  │  App + DB    │
  │  (serving)   │           │  (standby)   │
  └──────────────┘           └──────────────┘

Active-Active:
  Region A (Active)           Region B (Active)
  ┌──────────────┐            ┌──────────────┐
  │  App + DB    │ <──sync──> │  App + DB    │
  │ (50% traffic)│            │ (50% traffic)│
  └──────────────┘            └──────────────┘
```

## 3. RPO/RTO 설계

### 용어

| 용어 | 정의                                               | 단위 |
|------|----------------------------------------------------|------|
| RPO  | Recovery Point Objective — 허용 가능 데이터 손실량 | 시간 |
| RTO  | Recovery Time Objective — 허용 가능 복구 시간      | 시간 |

### RPO/RTO vs 비용

| RPO/RTO 수준               | 복제 방식                 | 비용 영향 |
|----------------------------|---------------------------|-----------|
| RPO=0, RTO < 1분           | 동기 복제 + 자동 failover | 매우 높음 |
| RPO < 5분, RTO < 15분      | 비동기 복제 + 자동 전환   | 높음      |
| RPO < 1시간, RTO < 4시간   | 비동기 복제 + 수동 전환   | 중간      |
| RPO < 24시간, RTO < 24시간 | 백업 복원                 | 낮음      |

### 서비스 등급별 권장

| 등급   | 예시                  | RPO      | RTO      | 패턴           |
|--------|-----------------------|----------|----------|----------------|
| Tier 1 | 결제, 인증            | 0        | < 1분    | Active-Active  |
| Tier 2 | 메인 API, 게임 서버   | < 5분    | < 15분   | Active-Passive |
| Tier 3 | 관리자 도구, 내부 API | < 1시간  | < 4시간  | Warm Standby   |
| Tier 4 | 배치, 리포트          | < 24시간 | < 24시간 | Backup Restore |

## 4. 데이터 동기화

### 동기화 방식 비교

| 방식           | RPO   | 성능 영향        | 일관성        | 예시                             |
|----------------|-------|------------------|---------------|----------------------------------|
| Synchronous    | 0     | 높음 (latency +) | Strong        | Aurora Global (write forwarding) |
| Asynchronous   | > 0   | 낮음             | Eventual      | RDS Cross-Region Read Replica    |
| CDC Stream     | 초~분 | 낮음             | Eventual      | DMS, Debezium                    |
| Backup/Restore | 시간  | 없음             | Point-in-time | S3 Cross-Region Replication      |

### 데이터 충돌 해결 (Active-Active)

| 전략                | 설명                          | 적합 상황            |
|---------------------|-------------------------------|----------------------|
| Last Writer Wins    | 타임스탬프 기반 최신 승리     | 낮은 충돌 빈도       |
| Application Resolve | 애플리케이션이 충돌 판단      | 비즈니스 로직 의존   |
| CRDTs               | 자동 병합 가능 데이터 구조    | 카운터, 집합 연산    |
| Region Ownership    | 데이터를 소유 리전에서만 쓰기 | 사용자 기반 파티셔닝 |

## 5. 트래픽 라우팅

### 라우팅 전략

| 전략         | 방법                           | RTO      | 장점             |
|--------------|--------------------------------|----------|------------------|
| DNS Failover | Route 53 Health Check          | TTL 의존 | 단순             |
| Weighted DNS | Route 53 Weighted + Health     | TTL 의존 | Canary 전환 가능 |
| Global LB    | CloudFront, Global Accelerator | 즉시     | TTL 무관         |
| Anycast      | IP 기반 라우팅                 | 즉시     | 게임/UDP 서비스  |

### DNS TTL 고려사항

| TTL   | Failover 속도 | 평시 부하     |
|-------|---------------|---------------|
| 60s   | 빠름          | DNS 쿼리 많음 |
| 300s  | 5분           | 보통          |
| 3600s | 느림          | DNS 쿼리 적음 |

## 6. Failover

### Failover 유형

| 유형      | 방법                              | RTO   | 위험                  |
|-----------|-----------------------------------|-------|-----------------------|
| Automatic | Health check + 자동 전환          | 초~분 | False positive (오판) |
| Semi-auto | 알림 → 운영자 확인 → 1-click 전환 | 분    | 인력 의존             |
| Manual    | Runbook 기반 수동 절차            | 시간  | 실수, 지연            |

### Failover 판단 기준

```
Health Check Failure
     │
     ├── Single instance? ──> Auto-heal (ASG replace)
     │
     ├── Multiple instances? ──> Investigate (AZ issue?)
     │
     └── Entire region? ──> Failover decision
              │
              ├── Automated: if health fail > 3min ──> switch
              │
              └── Semi-auto: page IC ──> confirm ──> execute
```

### Failback (복구 후 원복)

| 단계 | 행동                              |
|------|-----------------------------------|
| 1    | Primary 리전 복구 확인            |
| 2    | 데이터 동기화 완료 확인 (lag = 0) |
| 3    | Canary 트래픽 (1%) Primary로 전환 |
| 4    | 모니터링 30분                     |
| 5    | 점진적 증가 (10% → 50% → 100%)    |
| 6    | Secondary를 standby로 복귀        |

## 7. 비용 고려사항

### 주요 비용 항목

| 항목                   | Active-Passive | Active-Active |
|------------------------|----------------|---------------|
| Compute (대기)         | 0~50%          | 100%          |
| Database 복제          | 읽기 복제본    | Multi-write   |
| Cross-region transfer  | CDC 트래픽     | 양방향 동기화 |
| Global Accelerator/CDN | 선택           | 필수          |
| 운영 복잡도 (인력)     | 낮음           | 높음          |

### 비용 절감 팁

- Pilot Light: 최소 인프라만 유지하고 장애 시 scale-up
- Warm Standby: 50% 축소 운영 → 비용 절감 but RTO 증가
- 스토리지: S3 Cross-Region Replication (저비용)
- 컴퓨팅: Auto-scaling + Spot (Secondary 리전)

## 8. 체크리스트

### 설계 시

- [ ] RPO/RTO 요구사항 확정
- [ ] 데이터 동기화 방식 결정 (동기/비동기/CDC)
- [ ] 충돌 해결 전략 정의 (Active-Active 시)
- [ ] Failover 트리거 + 판단 기준 정의
- [ ] Failback 절차 문서화
- [ ] 비용 산정 + 승인

### 운영 시

- [ ] 분기별 DR 훈련 (Failover 리허설)
- [ ] Replication lag 모니터링 (lag > RPO 시 알림)
- [ ] Health check 정상 동작 확인
- [ ] Runbook 최신화 (담당자, 절차, 연락처)
- [ ] Cross-region 비용 월간 리뷰

## 9. 트러블슈팅

| 증상                      | 원인                  | 해결                                     |
|---------------------------|-----------------------|------------------------------------------|
| Failover 시 데이터 손실   | Async replication lag | RPO 기준 재설정 또는 동기화 방식 변경    |
| False failover (오판)     | Health check 과민     | 다단계 확인 (3회 연속 실패), 쿨다운 설정 |
| Failback 후 데이터 불일치 | Split-brain 발생      | 충돌 해결 전략 적용, 수동 검증           |
| Cross-region latency 과다 | 동기 복제 성능 영향   | Write forwarding 또는 비동기 전환        |
| DR 훈련 시 실제 장애 발생 | 훈련 범위 초과        | 별도 환경 또는 canary 범위로 제한        |

> Multi-Region 아키텍처 패턴(Active-Active, Active-Passive, Pilot Light)은 AWS Disaster Recovery 백서에서 분류합니다. RPO/RTO 매트릭스 기반으로 패턴을 선택합니다.
> — https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html

> AWS DR 전략 4단계: Backup & Restore(RPO 시간) < Pilot Light(RPO 분) < Warm Standby(RPO 초) < Active-Active(RPO ~0). 비용은 RPO/RTO 요구사항에 비례합니다.
> — https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html

> Route 53의 Health Check + Failover Routing은 DNS 기반 Multi-Region failover의 기본 메커니즘입니다. TTL 설정이 failover 시간을 결정합니다.
> — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html

> Global Accelerator는 Anycast IP 기반으로 DNS TTL 의존 없이 즉시 failover를 제공합니다 (AWS 공식: "instant failover").
> — https://aws.amazon.com/global-accelerator/

## 참고 자료

- AWS Disaster Recovery: [docs.aws.amazon.com](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html) — ★★★☆☆
- AWS Global Accelerator: [docs.aws.amazon.com](https://docs.aws.amazon.com/global-accelerator/latest/dg/) — ★★★☆☆
- Google SRE Workbook Ch.9: [Incident Response](https://sre.google/workbook/incident-response/) — ★★★★☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
