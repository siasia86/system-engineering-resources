# Cloud Cost Optimization

클라우드 비용을 체계적으로 관리하고 최적화하는 FinOps 프레임워크와 실무 전략입니다. FinOps Foundation 공식 프레임워크를 기반으로 합니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. FinOps 프레임워크](#2-finops-프레임워크) / [3. RI/SP 전략](#3-risp-전략)            |
| [4. Spot 활용](#4-spot-활용) / [5. Right-sizing](#5-right-sizing) / [6. 아키텍처 최적화](#6-아키텍처-최적화) |
| [7. 거버넌스](#7-거버넌스) / [8. 도구](#8-도구) / [9. 트러블슈팅](#9-트러블슈팅)                             |

## 1. 개요

| 항목 | 값                                                           |
|------|--------------------------------------------------------------|
| 정의 | 클라우드 비용의 가시성, 최적화, 운영을 위한 문화적 실천      |
| 출처 | FinOps Foundation (finops.org)                               |
| 핵심 | Inform → Optimize → Operate 사이클                           |
| 원칙 | 6대 원칙 (Teams collaborate, Everyone owns, etc.)            |
| 연관 | Capacity Planning (용량 산정), Platform Engineering (표준화) |

## 2. FinOps 프레임워크

### 3 Phase

| Phase    | 목표        | 활동                                   |
|----------|-------------|----------------------------------------|
| Inform   | 가시성 확보 | 태깅, 비용 할당, 대시보드, 예산 알림   |
| Optimize | 비용 절감   | RI/SP, Spot, Right-sizing, 미사용 정리 |
| Operate  | 지속적 운영 | 예산 관리, 이상 탐지, 팀별 책임        |

### 6대 원칙 (FinOps Foundation 원문)

| 번호 | 원칙                                                    |
|------|---------------------------------------------------------|
| 1    | Teams need to collaborate                               |
| 2    | Business value drives technology decisions              |
| 3    | Everyone takes ownership for their technology usage     |
| 4    | FinOps data should be accessible, timely, and accurate  |
| 5    | FinOps should be enabled centrally                      |
| 6    | Take advantage of the variable cost model of the cloud. |

> FinOps Foundation 공식 6 Principles 원문입니다.
> — https://www.finops.org/framework/principles/

## 3. RI/SP 전략

### Reserved Instances vs Savings Plans

| 항목      | Reserved Instances    | Savings Plans        |
|-----------|-----------------------|----------------------|
| 할인율    | 최대 72%              | 최대 72%             |
| 유연성    | 인스턴스 유형 고정    | 컴퓨팅 유형 유연     |
| 적용 범위 | EC2, RDS, ElastiCache | EC2, Fargate, Lambda |
| 기간      | 1년/3년               | 1년/3년              |
| 결제 옵션 | 전액/부분/무선납      | 전액/부분/무선납     |

> AWS 공식: RI는 최대 72% 할인, Savings Plans는 동일 할인율에 인스턴스 유형 유연성을 제공합니다.
> — https://aws.amazon.com/savingsplans/pricing/
> — https://aws.amazon.com/ec2/pricing/reserved-instances/

### 커버리지 전략

| 계층          | 할당 비율 | 대상                            |
|---------------|-----------|---------------------------------|
| Base load     | 60~70%    | RI/SP (항상 사용하는 최소 용량) |
| Variable load | 20~30%    | On-demand (일반 변동)           |
| Peak load     | 5~10%     | Spot/On-demand (피크 시)        |

> AWS Well-Architected Cost Optimization Pillar: "Use a mix of pricing models" — Base(RI/SP) + Variable(On-demand) + Peak(Spot) 계층 구조를 권장합니다.
> — https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/select-the-best-pricing-model.html

### RI 구매 의사결정

| 조건                         | 권장               |
|------------------------------|--------------------|
| 사용량 6개월+ 안정적         | 3년 RI (최대 할인) |
| 사용량 3개월+ 안정적         | 1년 RI             |
| 사용량 변동 크지만 총량 안정 | Savings Plans      |
| 사용량 예측 불가             | On-demand 유지     |

## 4. Spot 활용

### Spot 적합 워크로드

| 적합                     | 부적합            |
|--------------------------|-------------------|
| Stateless 웹 서버 (ASG)  | 단일 인스턴스 DB  |
| Batch/ETL 작업           | Stateful 서비스   |
| CI/CD 빌드 러너          | 장시간 트랜잭션   |
| 데이터 분석 (EMR, Spark) | 실시간 금융 거래  |
| 테스트/QA 환경           | SLA 99.99% 서비스 |

> AWS 공식: Spot Instance는 On-Demand 대비 최대 90% 할인이며, 2분 전 중단 알림(interruption notice)을 제공합니다.
> — https://aws.amazon.com/ec2/spot/

### Spot 안정성 확보

| 전략                  | 방법                             |
|-----------------------|----------------------------------|
| Diversification       | 여러 인스턴스 유형/AZ에 분산     |
| Capacity-optimized    | 가용 용량 기반 배치 전략         |
| Grace period handling | 2분 중단 알림 활용 → 정상 종료   |
| Fallback to On-demand | Spot 부족 시 자동 On-demand 전환 |

> AWS의 "capacity-optimized" 배치 전략은 Spot 중단 확률이 가장 낮은 풀을 선택합니다. AWS 공식 best practice입니다.
> — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html

## 5. Right-sizing

### 분석 기준

| 지표         | 과대 프로비저닝 기준        | 권장 행동          |
|--------------|-----------------------------|--------------------|
| CPU 평균     | < 20% (2주 평균)            | 인스턴스 축소      |
| Memory 평균  | < 30% (2주 평균)            | 인스턴스 축소      |
| Network      | 거의 미사용                 | 작은 타입 전환     |
| Storage IOPS | Provisioned 대비 < 10% 사용 | gp3 전환 또는 축소 |

> AWS Compute Optimizer는 14일간의 CloudWatch 메트릭을 분석하여 right-sizing을 권장합니다. CPU < 20% 기준은 Trusted Advisor의 "Low Utilization" 임계값입니다.
> — https://docs.aws.amazon.com/compute-optimizer/latest/ug/what-is-compute-optimizer.html

### Right-sizing 절차

| 단계 | 활동                          | 도구                               |
|------|-------------------------------|------------------------------------|
| 1    | 메트릭 수집 (2~4주)           | CloudWatch, Datadog                |
| 2    | 과대 프로비저닝 인스턴스 식별 | AWS Cost Explorer, Trusted Advisor |
| 3    | 권장 타입 확인                | AWS Compute Optimizer              |
| 4    | 테스트 환경에서 검증          | Load test                          |
| 5    | 프로덕션 적용 (Canary)        | ASG rolling update                 |

## 6. 아키텍처 최적화

### 비용 절감 패턴

| 패턴               | 절감 방법                       | 예상 절감   |
|--------------------|---------------------------------|-------------|
| Serverless 전환    | Lambda/Fargate (idle 비용 0)    | 30~70%      |
| Storage tiering    | S3 Intelligent-Tiering, Glacier | 40~80%      |
| Cache 레이어 추가  | ElastiCache → DB 호출 감소      | DB 비용 50% |
| NAT Gateway 대체   | VPC Endpoint, NAT Instance      | 30~60%      |
| 데이터 전송 최적화 | 같은 AZ 배치, CloudFront 활용   | 20~50%      |

> AWS 데이터 전송 요금: 같은 AZ 내 전송은 무료, AZ 간 $0.01/GB, 리전 간 $0.02/GB입니다. VPC Endpoint 사용 시 NAT Gateway 처리 비용($0.045/GB)을 절감합니다.
> — https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer

## 7. 거버넌스

### 태깅 전략

| 태그 키     | 예시 값          | 용도          |
|-------------|------------------|---------------|
| Environment | prd / stg / dev  | 환경별 비용   |
| Team        | payment / search | 팀별 할당     |
| Service     | api-gateway      | 서비스별 추적 |
| CostCenter  | CC-1234          | 부서 차지백   |
| Owner       | user@example.com | 책임자 식별   |

> AWS는 최소 태그 키로 Environment, Team/Project, CostCenter를 권장합니다. 미태깅 리소스는 AWS Cost Categories에서 "Untagged" 그룹으로 자동 분류됩니다.
> — https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html

### 예산 알림

| 임계값 | 행동                       |
|--------|----------------------------|
| 80%    | Slack/Email 알림           |
| 100%   | 경고 + 팀 리드 통보        |
| 120%   | 긴급 리뷰 + 비용 원인 분석 |

## 8. 도구

| 도구                  | 유형         | 특징                      |
|-----------------------|--------------|---------------------------|
| AWS Cost Explorer     | 네이티브     | 비용 분석, RI 권장, 예측  |
| AWS Compute Optimizer | 네이티브     | Right-sizing 권장         |
| Infracost             | OSS          | Terraform PR 비용 표시    |
| Kubecost              | K8s 비용     | Pod/Namespace별 비용 할당 |
| CloudHealth           | 멀티클라우드 | 비용 관리, 거버넌스, 보고 |

> Infracost는 Terraform plan에서 비용 변화를 PR 코멘트로 표시합니다 (OSS, 2020~). OpenCost(Kubecost의 오픈소스 코어)는 CNCF Sandbox 프로젝트(2022)입니다.
> — https://www.infracost.io/docs/
> — https://www.cncf.io/projects/opencost/

## 9. 트러블슈팅

| 증상                      | 원인                     | 해결                                    |
|---------------------------|--------------------------|-----------------------------------------|
| 월 비용 급증              | 태깅 미비 → 원인 불명    | 태깅 의무화 + 미태깅 리소스 알림        |
| RI 활용률 낮음            | 워크로드 변경, 과다 구매 | 분기별 RI 리뷰, Savings Plans 전환      |
| Spot 중단 빈번            | 단일 인스턴스 타입 사용  | 다양한 타입/AZ 분산, capacity-optimized |
| Right-sizing 후 성능 저하 | 피크 미고려              | p99 기준 분석, 2주+ 데이터 확보         |
| 팀별 비용 책임 불분명     | 비용 할당 미설정         | 태깅 + CostCenter 기반 차지백 도입      |

> 클라우드 비용 최적화 원칙은 AWS Well-Architected Framework (Cost Optimization Pillar)와 FinOps Foundation의 FinOps Framework에 기반합니다.
> — https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/
> — https://www.finops.org/framework/

## 참고 자료

- FinOps Foundation: [finops.org/framework](https://www.finops.org/framework/) — ★★★★☆
- AWS Well-Architected Cost Optimization: [docs.aws.amazon.com](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/) — ★★★☆☆
- Infracost: [infracost.io](https://www.infracost.io/) — ★★☆☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
