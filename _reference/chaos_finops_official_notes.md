---
name: chaos-finops-official-notes
description: Chaos Engineering 및 FinOps 공식 문서 참조 노트.
tags:
  - chaos-engineering
  - finops
  - cost
  - reliability
last_checked: 2026-11-09
sources:
  - https://principlesofchaos.org/
  - https://litmuschaos.io/
  - https://docs.aws.amazon.com/fis/latest/userguide/
  - https://www.finops.org/framework/
  - https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/
  - https://aws.amazon.com/savingsplans/compute-pricing/
---

# Chaos Engineering & FinOps 공식 문서 참조 노트

## 1. Chaos Engineering (확인일: 2026-07-07)

### Principles of Chaos Engineering

출처: principlesofchaos.org

정의: "Chaos Engineering is the discipline of experimenting on a system in order to build confidence in the system's capability to withstand turbulent conditions in production."

4대 원칙:
1. Build a Hypothesis around Steady State Behavior
2. Vary Real-world Events
3. Run Experiments in Production
4. Automate Experiments to Run Continuously

### Advanced Principles

- Minimize Blast Radius — 실험 범위를 최소화하여 실제 장애 방지
- Start with known good behavior — 정상 상태 정의 후 실험 시작

### LitmusChaos (CNCF Incubating)

출처: litmuschaos.io

| 항목      | 값                                      |
|-----------|-----------------------------------------|
| 유형      | CNCF Incubating Project                 |
| 실행 환경 | Kubernetes                              |
| 언어      | Go                                      |
| 실험 정의 | ChaosEngine, ChaosExperiment CRD (YAML) |
| 관찰      | Prometheus metrics, Resilience Score    |

### AWS Fault Injection Service (FIS)

출처: docs.aws.amazon.com/fis/

| 항목      | 값                                     |
|-----------|----------------------------------------|
| 유형      | AWS 관리형 서비스                      |
| 대상      | EC2, ECS, EKS, RDS, Network            |
| 실험 정의 | Experiment template (JSON)             |
| Stop 조건 | CloudWatch alarm 기반 자동 중단        |
| IAM       | fis:CreateExperimentTemplate 권한 필요 |

## 2. FinOps (확인일: 2026-07-07)

### FinOps Foundation 정의

출처: finops.org/framework/

정의: "FinOps is an operational framework and cultural practice which maximizes the business value of technology, enables timely data-driven decision making, and creates financial accountability through collaboration between engineering, finance, and business teams."

- 2026-11-09 finops.org/framework 기준 정의입니다. 이전 정의("FinOps is an evolving cloud financial management discipline and cultural practice ...")는 현행 페이지에 없습니다.

### FinOps Lifecycle (3 Phase)

| Phase    | 목적             | 활동                                 |
|----------|------------------|--------------------------------------|
| Inform   | 비용 가시성 확보 | 태깅, 할당, 대시보드, 예산 알림      |
| Optimize | 비용 효율화      | RI/SP, Right-sizing, Spot, 유휴 제거 |
| Operate  | 지속적 거버넌스  | Policy, 자동화, 팀별 예산 책임       |

### FinOps Principles (원문 그대로, 2026-11-09 확인)

1. Teams need to collaborate
2. Business value drives technology decisions
3. Everyone takes ownership for their technology usage
4. FinOps data should be accessible, timely, and accurate
5. FinOps should be enabled centrally
6. Take advantage of the variable cost model of the cloud

- 이전 판의 "A centralized FinOps function drives best practices"는 현행 페이지에서 "FinOps should be enabled centrally"로 바뀌었습니다.

### AWS Cost Optimization Pillar

출처: docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/

핵심 질문:
- COST 1: How do you implement cloud financial management?
- COST 2: How do you govern usage? (Budgets, SCPs)
- COST 3: How do you monitor usage and cost?
- COST 4: How do you decommission resources?
- COST 5: How do you evaluate cost when selecting services?

### 절감 도구 비교

| 도구               | 약정 기간 | 절감율 | 유연성    |
|--------------------|-----------|--------|-----------|
| Reserved Instances | 1~3년     | 30~72% | 낮음      |
| Savings Plans      | 1~3년     | 20~66% | 중간      |
| Spot Instances     | 없음      | 60~90% | 중단 위험 |

- AWS 공식 최대 할인율: Savings Plans는 EC2 Instance SP 최대 72%, Compute SP 최대 66%입니다(2026-11-09 확인).
