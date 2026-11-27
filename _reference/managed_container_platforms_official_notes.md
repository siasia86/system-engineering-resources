---
name: managed-container-platforms-official-notes
description: EKS·GKE·AKS·ECS/Fargate·OpenShift(ROSA)의 요금과 Kubernetes 판 지원 정책을 공식 페이지 기준으로 정리, 미확인 항목 표시.
tags:
  - eks
  - gke
  - aks
  - ecs
  - fargate
  - openshift
last_checked: 2026-11-27
sources:
  - https://aws.amazon.com/eks/pricing/
  - https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
  - https://aws.amazon.com/ecs/pricing/
  - https://aws.amazon.com/fargate/pricing/
  - https://aws.amazon.com/rosa/pricing/
  - https://docs.cloud.google.com/kubernetes-engine/docs/concepts/release-channels
  - https://docs.cloud.google.com/kubernetes-engine/docs/release-notes
  - https://learn.microsoft.com/en-us/azure/aks/free-standard-pricing-tiers
  - https://learn.microsoft.com/en-us/azure/aks/supported-kubernetes-versions
  - https://www.redhat.com/en/technologies/cloud-computing/openshift
---

# 관리형 컨테이너 플랫폼 공식 자료 참조 노트

## 1. EKS (2026-11-27)

- 요금: 표준 지원 "$0.10 per cluster per hour", 연장 지원 "$0.60 per cluster per hour (Standard Kubernetes version support + $0.50 per cluster per hour)".
- Auto Mode: EC2 요금 + 관리 요금, 초 단위·최소 1분(예 c6a.2xlarge EC2 $0.306/h, Auto Mode $0.03672/h). Hybrid Nodes: vCPU-시간 구간 요금(첫 576,000 $0.020 ~ 11,520,000 초과 $0.006), 노드당 최대 32 vCPU 청구. Provisioned Control Plane XL $1.65/h, 2XL $3.40, 4XL $6.90, 8XL $13.90.
- 판: "A minor version is under standard support in Amazon EKS for the first 14 months after it's released.", 이어서 12개월 연장. 표준 1.37·1.36·1.35·1.34, 연장 1.33·1.32·1.31. 1.31 연장 종료 2026-11-26(페이지에는 아직 연장 목록에 있음), 1.34 표준 종료 2026-12-02.

## 2. ECS·Fargate

- "There is no additional charge for Amazon ECS orchestration." ECS Anywhere $0.01025/등록 인스턴스·시간, ECS Managed Instances는 인스턴스별 관리 요금.
- Fargate: "Pricing is calculated per second with a 1-minute minimum."(Windows 5분). us-east-1 Linux/x86 vCPU $0.000011244/초, 메모리 $0.000001235/GB·초, 20GB 초과 저장소 $0.0000000308/GB·초. ARM vCPU $0.0000089944, 메모리 $0.0000009889. Spot 최대 70%, Savings Plans 최대 50%(Fargate 페이지), ECS 페이지는 3년 Compute Savings Plans 최대 52%.

## 3. GKE

- 릴리스 채널: Rapid, Regular(default), Stable, Extended("you can stay on a minor version for up to 24 months"), No channel(deprecated, 2027-06-14 제거). Autopilot은 채널 등록만 가능.
- 릴리스 노트 현재 판 표(2026-11-16 항목까지): Regular 생성 기본 `1.36.4-gke.2377000`, 권장 자동 업그레이드 대상 `1.35.8-gke.1796000`, 사용 가능 minor 1.34~1.37.
- 요금 페이지(cloud.google.com/kubernetes-engine/pricing): 본문 약 88자만 읽혀 관리 요금·무료 크레딧·Autopilot 청구 기준 미확인.

## 4. AKS

- 티어: Free("Free cluster management", 금융 보상 SLA 없음, 10노드 미만 권장, 최대 1,000), Standard(SLA 가용 영역 99.95%·미사용 99.9%, 최대 5,000), Premium(Standard + 24개월 LTS). AKS Automatic은 Standard 티어, pod 준비 SLA 99.9%(5분 안).
- 요금 페이지: Free는 "Free (only pay for underlying resources)". Standard·Premium·LTS 금액은 `$-`로 표시돼 미확인.
- 판: "AKS supports three GA minor versions of Kubernetes"(N, N-1, N-2), N-3 플랫폼 지원 60일 유예. EOL은 표의 달 마지막 날: 1.34 2026-11, 1.35 2027-03, 1.36 2027-06, 1.37 2027-10, 1.38 미리 보기 2026-11·GA 2027-02. LTS 종료: 1.34 2027-11, 1.37 2028-10.

## 5. OpenShift

- 제품: 관리형 ROSA(Red Hat·AWS 공동), ARO(Red Hat·Microsoft 공동), OpenShift Dedicated(AWS·Google Cloud), OpenShift on IBM Cloud. 직접 설치 Platform Plus, Container Platform, Kubernetes Engine, Virtualization Engine. 제품 페이지 머리 "Red Hat OpenShift 5 is here."
- docs.redhat.com 문서 목록은 403으로 현재 판 미확인.
- ROSA: "hourly rate of $0.171 per 4 vCPU used by worker nodes", HCP "a $0.25 per hour cluster fee", 1·3년 약정 33~55% 절감, AWS 인프라 별도.
