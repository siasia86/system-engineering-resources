# Capacity Planning

트래픽 예측, 리소스 산정, 비용 계산을 통해 서비스가 요구 부하를 안정적으로 처리할 수 있도록 용량을 계획하는 프레임워크입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 계획 절차](#2-계획-절차) / [3. 트래픽 예측](#3-트래픽-예측)                   |
| [4. 리소스 산정](#4-리소스-산정) / [5. Headroom 설계](#5-headroom-설계) / [6. 비용 계산](#6-비용-계산) |
| [7. Load Testing](#7-load-testing) / [8. 운영 주기](#8-운영-주기) / [9. 트러블슈팅](#9-트러블슈팅)     |

## 1. 개요

| 항목 | 값                                                       |
|------|----------------------------------------------------------|
| 목적 | 수요 대비 적정 용량 확보 (과소 = 장애, 과대 = 비용 낭비) |
| 출처 | Google SRE Workbook Ch.11, AWS Well-Architected          |
| 핵심 | N+1/N+2 용량 확보, 30~50% headroom, 계절성 분해          |
| 주기 | 분기별 재평가 + 이벤트 전 임시 계획                      |
| 연관 | SLO (성능 목표), Cost Optimization (비용 제약)           |

### Google 원칙

- **Plan to fail**: N+1 또는 N+2 capacity (Google은 N+1 사용, 금융/게임 등 고가용성 환경은 N+2)
- **Demand forecasting**: Linear regression 부족 → Seasonal decomposition
- **Load testing**: 실제 트래픽의 2x~3x로 stress test
- **Headroom**: 30~50% headroom 유지 (burst 대비, 워크로드에 따라 조정)

> Google SRE Workbook Ch.11 "Managing Load"에서 redundancy와 load balancing 전략을 다룹니다.
> N+1은 Google SRE 표준, N+2는 금융/게임 등 보수적 환경 기준입니다. 30~50% headroom은 업계 통용 관행이며, 공식 문서에서 특정 수치를 명시하지는 않습니다.
> — https://sre.google/workbook/managing-load/

## 2. 계획 절차

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  1. Measure  │──>│ 2. Forecast  │──>│ 3. Allocate  │──>│  4. Validate │
│ (curr. load) │   │  (predict)   │   │  (resource)  │   │ (Load Test)  │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
       │                                                         │
       └─────────────── Feedback Loop ───────────────────────────┘
```

## 3. 트래픽 예측

### 예측 입력 데이터

| 데이터         | 출처                      | 용도           |
|----------------|---------------------------|----------------|
| Historical RPS | ALB/CDN 로그, Prometheus  | 기본 추세선    |
| 계절성 패턴    | 월별/요일별/시간대별 분석 | 피크 타임 예측 |
| 비즈니스 계획  | PM/마케팅 (이벤트, 출시)  | 급증 예측      |
| 사용자 성장률  | MAU/DAU 추이              | 장기 용량 계획 |

### 예측 방법

| 방법                   | 적합 상황                 | 정확도 |
|------------------------|---------------------------|--------|
| Linear Extrapolation   | 안정적 성장 서비스        | 낮음   |
| Seasonal Decomposition | 주기성 있는 트래픽        | 중간   |
| Business-driven        | 이벤트/마케팅 기반 급증   | 높음   |
| Load Test 기반         | 신규 서비스 (데이터 부족) | 높음   |

### 피크 산정

```
Peak RPS = Average RPS * Peak Multiplier * Growth Factor * Safety Margin

Example:
  Average RPS: 1,000
  Peak Multiplier: 3x (이벤트 기간)
  Growth Factor: 1.5x (6개월 성장 예측)
  Safety Margin: 1.3x

  Peak RPS = 1,000 * 3 * 1.5 * 1.3 = 5,850 RPS
```

## 4. 리소스 산정

### 서버 산정 공식

```
Required Instances = Peak RPS / (Single Instance Capacity * Target Utilization)

Example:
  Peak RPS: 5,850
  Single Instance Capacity: 500 RPS (load test 기준)
  Target Utilization: 70%

  Required = 5,850 / (500 * 0.7) = 16.7 → 17 instances
  N+2 적용: 17 + 2 = 19 instances
```

### 리소스 유형별 산정

| 리소스   | 산정 기준                   | 주의 사항                 |
|----------|-----------------------------|---------------------------|
| CPU      | RPS 기준, p99 latency 유지  | Burst 허용 vs Guaranteed  |
| Memory   | Working set + GC overhead   | OOM 여유 20% 확보         |
| Disk I/O | IOPS + Throughput (MB/s)    | EBS gp3 vs io2 선택       |
| Network  | Bandwidth + PPS (packets/s) | AZ 간 전송 비용 고려      |
| DB       | Connections + Query latency | Connection pool 크기 연동 |

### 인스턴스 타입 선정 기준

| 워크로드 유형   | 권장 인스턴스 패밀리 | 이유                 |
|-----------------|----------------------|----------------------|
| API Server      | M (범용)             | 균형 잡힌 CPU/Memory |
| Worker/Batch    | C (컴퓨팅 최적화)    | CPU bound 처리       |
| Cache/In-memory | R (메모리 최적화)    | 대용량 메모리 필요   |
| ML Inference    | G (GPU)              | GPU 가속 필요        |
| Storage-heavy   | I (스토리지 최적화)  | 높은 IOPS 필요       |

> AWS EC2 인스턴스 패밀리 분류: General Purpose(M), Compute Optimized(C), Memory Optimized(R), Storage Optimized(I), Accelerated Computing(G/P).
> — https://aws.amazon.com/ec2/instance-types/

## 5. Headroom 설계

### Headroom 비율 가이드

| 상황             | 권장 Headroom | 근거                           |
|------------------|---------------|--------------------------------|
| 정상 운영        | 30~50%        | Burst 흡수 + 배포 여유         |
| 이벤트 전        | 50~100%       | 예측 불확실성 + Auto-scale lag |
| AZ 장애 대비     | N+1 (33%)     | 3-AZ 중 1개 손실 시            |
| Region 장애 대비 | N+1 (50%)     | 2-Region 중 1개 손실 시        |

> AWS Well-Architected Framework (Reliability Pillar)에서 Multi-AZ는 N+1, Multi-Region은 Active-Active 또는 N+1 구성을 권장합니다.
> — https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/

### Auto-scaling으로 대체 가능한 범위

| 구간             | Auto-scale | 사전 확보 | 이유                       |
|------------------|------------|-----------|----------------------------|
| 일상 변동 (1~2x) | ✅         | ❌        | Scale-out 시간 충분        |
| 점진적 증가 (3x) | ✅         | 🟡        | Warm-up 시간 필요 (JVM 등) |
| 급격 spike (5x+) | ❌         | ✅        | Scale-out lag > SLO 허용치 |

## 6. 비용 계산

### TCO 구성 요소

🟡 아래 비율은 일반적인 AWS 워크로드 기준 추정치입니다. 서비스 구성에 따라 편차가 큽니다.

| 항목       | 비율 (일반적) | 상세                       |
|------------|---------------|----------------------------|
| Compute    | 50~65%        | EC2, ECS, Lambda           |
| Storage    | 10~20%        | EBS, S3, RDS storage       |
| Network    | 10~15%        | Data transfer, NAT Gateway |
| Database   | 15~25%        | RDS, ElastiCache, DynamoDB |
| Monitoring | 3~5%          | CloudWatch, Datadog        |

### 절감 전략

| 전략              | 절감율 | 적합 대상                   |
|-------------------|--------|-----------------------------|
| Reserved Instance | 30~60% | Baseline (항상 사용하는 양) |
| Savings Plans     | 30~40% | Compute 전반 (유연성 높음)  |
| Spot Instance     | 60~90% | Stateless worker, Batch     |
| Right-sizing      | 20~40% | 과잉 프로비저닝된 리소스    |

> AWS에 따르면 RI는 On-Demand 대비 최대 72% 절감, Spot은 최대 90% 절감이 가능합니다.
> — https://aws.amazon.com/ec2/pricing/reserved-instances/

## 7. Load Testing

### 테스트 유형

| 유형     | 목적                       | 부하 패턴               |
|----------|----------------------------|-------------------------|
| Baseline | 단일 인스턴스 처리량 측정  | 점진 증가 → 한계 도달   |
| Stress   | 한계점 및 장애 모드 확인   | 예상 피크의 2~3x        |
| Soak     | 장시간 안정성 확인         | 정상 부하 8~24시간 유지 |
| Spike    | 급격한 부하 증가 대응 확인 | 0 → 피크 즉시 전환      |

> 부하 테스트 4유형(Baseline/Stress/Soak/Spike)은 k6 공식 문서의 분류를 따릅니다.
> — https://grafana.com/docs/k6/latest/testing-guides/test-types/

### Load Test Checklist

- [ ] 프로덕션과 동일한 인스턴스 타입/설정 사용
- [ ] DB, Cache, 외부 의존성 포함 (mock 최소화)
- [ ] 점진적 증가로 병목 구간 식별
- [ ] p50, p95, p99 latency + error rate 측정
- [ ] Auto-scaling 동작 검증 (scale-out 시간 측정)
- [ ] 테스트 후 리소스 정리

### AWS Well-Architected 점검 질문

용량 계획 리뷰 시 다음 질문을 확인합니다 (Performance Efficiency Pillar):

- **PERF 1**: 최적 아키텍처를 어떻게 선택하는가?
- **PERF 2**: 컴퓨팅 솔루션을 어떻게 선택하는가?
- **PERF 4**: 리소스 성능을 어떻게 모니터링하는가?

> AWS Well-Architected Performance Efficiency Pillar
> — https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/

## 8. 운영 주기

| 주기      | 활동                         | 산출물                   |
|-----------|------------------------------|--------------------------|
| Monthly   | 리소스 사용률 리뷰           | 사용률 보고서            |
| Quarterly | 용량 계획 재평가 + 비용 리뷰 | Capacity Plan 문서       |
| Pre-event | 이벤트 용량 계획 (2주 전)    | Scale-up 계획, 롤백 기준 |
| Annual    | 아키텍처 수준 용량 재설계    | 연간 인프라 예산         |

## 9. 트러블슈팅

| 증상                     | 원인                         | 해결                                  |
|--------------------------|------------------------------|---------------------------------------|
| 피크 시 장애 반복        | Headroom 부족 또는 예측 오류 | Peak multiplier 재산정, Headroom 확대 |
| 비용 초과                | 과잉 프로비저닝              | Right-sizing + RI/SP 적용             |
| Auto-scale 지연으로 장애 | Scale-out lag > 허용치       | Pre-warming 또는 Predictive scaling   |
| Load test와 실제 차이 큼 | 테스트 환경 불일치           | Prod 동일 환경 + 실제 데이터 사용     |
| 분기 계획 무용지물       | 비즈니스 변동 미반영         | PM/마케팅과 월간 동기화 추가          |

## 참고 자료

- Google SRE Workbook Ch.11: [Managing Load](https://sre.google/workbook/managing-load/) — ★★★★☆
- AWS Well-Architected Performance Efficiency: [docs.aws.amazon.com](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/) — ★★★☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
