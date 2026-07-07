---
name: chaos-finops-official-notes
description: Chaos Engineering 및 FinOps 공식 문서 참조 노트.
last_checked: 2026-07-07
sources:
  - https://principlesofchaos.org/
  - https://litmuschaos.io/
  - https://docs.aws.amazon.com/fis/latest/userguide/
  - https://www.finops.org/framework/
  - https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/
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

| 항목       | 값                                      |
|------------|-----------------------------------------|
| 유형       | CNCF Incubating Project                 |
| 실행 환경  | Kubernetes                              |
| 언어       | Go                                      |
| 실험 정의  | ChaosEngine, ChaosExperiment CRD (YAML) |
| 관찰       | Prometheus metrics, Resilience Score    |

### AWS Fault Injection Service (FIS)

출처: docs.aws.amazon.com/fis/

| 항목        | 값                                          |
|-------------|---------------------------------------------|
| 유형        | AWS 관리형 서비스                           |
| 대상        | EC2, ECS, EKS, RDS, Network                |
| 실험 정의   | Experiment template (JSON)                  |
| Stop 조건   | CloudWatch alarm 기반 자동 중단             |
| IAM         | fis:CreateExperimentTemplate 권한 필요      |

## 2. FinOps (확인일: 2026-07-07)

### FinOps Foundation 정의

출처: finops.org/framework/

정의: "FinOps is an evolving cloud financial management discipline and cultural practice that enables organizations to get maximum business value by helping engineering, finance, technology and business teams to collaborate on data-driven spending decisions."

### FinOps Lifecycle (3 Phase)

| Phase    | 목적                       | 활동                                    |
|----------|----------------------------|-----------------------------------------|
| Inform   | 비용 가시성 확보           | 태깅, 할당, 대시보드, 예산 알림         |
| Optimize | 비용 효율화                | RI/SP, Right-sizing, Spot, 유휴 제거    |
| Operate  | 지속적 거버넌스            | Policy, 자동화, 팀별 예산 책임          |

### FinOps Principles

1. Teams need to collaborate
2. Everyone takes ownership for their cloud usage
3. A centralized team drives FinOps
4. Reports should be accessible and timely
5. Decisions are driven by the business value of cloud
6. Take advantage of the variable cost model of cloud

### AWS Cost Optimization Pillar

출처: docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/

핵심 질문:
- COST 1: How do you implement cloud financial management?
- COST 2: How do you govern usage? (Budgets, SCPs)
- COST 3: How do you monitor usage and cost?
- COST 4: How do you decommission resources?
- COST 5: How do you evaluate cost when selecting services?

### 절감 도구 비교

| 도구               | 약정 기간 | 절감율  | 유연성   |
|--------------------|-----------|---------|----------|
| Reserved Instances | 1~3년    | 30~72%  | 낮음     |
| Savings Plans      | 1~3년    | 20~66%  | 중간     |
| Spot Instances     | 없음     | 60~90%  | 중단 위험 |
