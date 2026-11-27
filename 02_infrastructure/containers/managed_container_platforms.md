# 관리형 컨테이너 플랫폼 비교 (EKS · GKE · AKS · ECS/Fargate · OpenShift)
<!-- reference: _reference/managed_container_platforms_official_notes.md -->

클라우드 사업자가 컨트롤 플레인(또는 오케스트레이터 전체)을 운영해 주는 컨테이너 플랫폼을 비교합니다. Kubernetes 계열(EKS, GKE, AKS, OpenShift)과 AWS 전용 오케스트레이터(ECS, 실행 환경 Fargate)로 나눠 요금 구조, 판 지원 기간, 운영 범위를 정리했습니다. 도구를 고를 때 보는 문서이며 설치 가이드가 아닙니다.

- 확인일: 2026-11-27, 각 사업자의 공식 요금·문서 페이지 기준
- 예제 시험: 계정과 비용이 필요해 실행하지 않음. GKE 요금 페이지와 AKS Standard·Premium 시간당 요금은 페이지 내용을 읽지 못해 미확인

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 한눈에 비교](#2-한눈에-비교) / [3. Kubernetes 판 지원](#3-kubernetes-판-지원) |
| [4. 요금 구조](#4-요금-구조) / [5. OpenShift](#5-openshift) / [6. 고르는 기준](#6-고르는-기준)         |
| [7. 옮길 때 확인할 것](#7-옮길-때-확인할-것) / [함께 보기](#함께-보기)                                 |

---

## 1. 개요

```text
self-managed K8s       managed control plane        managed nodes too           serverless containers
(kubeadm, k3s)    ->   EKS / GKE Standard / AKS  ->  EKS Auto Mode, GKE         ->  Fargate, Cloud Run,
you run everything     you run worker nodes          Autopilot, AKS Automatic       Azure Container Apps
```

| 구분                 | 사업자가 맡는 것                       | 사용자가 맡는 것                                      |
|----------------------|----------------------------------------|-------------------------------------------------------|
| 관리형 컨트롤 플레인 | API 서버, etcd, 스케줄러의 가용성·패치 | 워커 노드 판·패치, 노드 크기, 애드온, 업그레이드 시점 |
| 노드까지 관리        | 노드 생성·크기·패치                    | 워크로드 정의, 리소스 요청량                          |
| ECS + Fargate        | 오케스트레이터와 실행 서버 전체        | 작업 정의(task definition), 서비스 설정               |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 항목               | EKS                              | GKE                            | AKS                                                | ECS / Fargate                     | OpenShift (ROSA·ARO 등)                    |
|--------------------|----------------------------------|--------------------------------|----------------------------------------------------|-----------------------------------|--------------------------------------------|
| 오케스트레이터     | Kubernetes                       | Kubernetes                     | Kubernetes                                         | ECS(AWS 전용)                     | Kubernetes + Red Hat 구성 요소             |
| 컨트롤 플레인 요금 | 클러스터당 시간 $0.10(표준 지원) | 미확인(요금 페이지 읽지 못함)  | Free 티어 무료, Standard·Premium 유료(금액 미확인) | ECS 오케스트레이션 추가 요금 없음 | ROSA HCP 클러스터 시간당 $0.25             |
| 노드 관리 모드     | EKS Auto Mode                    | Autopilot                      | AKS Automatic                                      | Fargate                           | 관리형 서비스는 Red Hat·클라우드 공동 운영 |
| 판 지원            | 표준 14개월 + 연장 12개월        | 채널별, Extended는 최대 24개월 | GA minor 3개(N~N-2), LTS 24개월(Premium)           | 해당 없음                         | 미확인                                     |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Kubernetes 판 지원

| 서비스 | 지원 방식                                                                                                                     | 2026-11-27 기준                                                               |
|--------|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| EKS    | minor 판 출시 뒤 14개월 표준 지원, 이어서 12개월 연장 지원(연장 기간은 요금 추가)                                             | 표준 1.37·1.36·1.35·1.34, 연장 1.33·1.32·1.31(1.31 연장 종료 2026-11-26)      |
| GKE    | 릴리스 채널 Rapid, Regular(기본), Stable, Extended. Extended는 한 minor 판에 최대 24개월. "No channel"은 2027-06-14 제거 예정 | Regular 채널 생성 기본 판 `1.36.4-gke.2377000`, 사용 가능 minor 1.34~1.37     |
| AKS    | GA minor 판 3개(N, N-1, N-2) 지원, N-3은 플랫폼 지원(60일 유예). LTS는 Premium 티어에서 24개월                                | 1.34 EOL 2026-11-30, 1.35 2027-03, 1.36 2027-06, 1.37 2027-10, 1.38 미리 보기 |

- 업그레이드를 미루면 EKS는 연장 지원 요금(클러스터당 시간 $0.60)이 붙고, AKS는 지원 범위를 벗어납니다. 판 일정은 운영 계획에 넣어 둡니다.
- GKE Autopilot 클러스터는 릴리스 채널에만 등록할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 요금 구조

### 4.1 EKS

| 항목                      | 요금(공식 페이지)                                                                                    |
|---------------------------|------------------------------------------------------------------------------------------------------|
| 클러스터(표준 지원)       | $0.10 / 클러스터·시간                                                                                |
| 클러스터(연장 지원)       | $0.60 / 클러스터·시간 (표준 + $0.50)                                                                 |
| Auto Mode                 | EC2 요금에 관리 요금 추가, 초 단위·최소 1분 (예: c6a.2xlarge EC2 $0.306 + Auto Mode $0.03672 / 시간) |
| Hybrid Nodes              | vCPU·시간 단위 구간 요금, 첫 576,000 vCPU-시간 $0.020                                                |
| Provisioned Control Plane | XL $1.65 / 클러스터·시간부터                                                                         |

- 워커 노드(EC2), 로드밸런서, EBS, 데이터 전송은 따로 청구됩니다.

### 4.2 ECS와 Fargate

- ECS 오케스트레이션 자체는 추가 요금이 없습니다("There is no additional charge for Amazon ECS orchestration."). 실행하는 EC2나 Fargate 요금만 냅니다. ECS Anywhere는 등록 인스턴스당 시간 $0.01025, ECS Managed Instances는 인스턴스별 관리 요금이 있습니다.
- Fargate는 vCPU와 메모리를 초 단위로 청구하고 최소 1분입니다(Windows 컨테이너는 최소 5분).

| us-east-1 Linux/x86 | 초당 요금(공식)                   | 시간당 환산(계산값) |
|---------------------|-----------------------------------|---------------------|
| vCPU                | $0.000011244 / vCPU·초            | 약 $0.0405          |
| 메모리              | $0.000001235 / GB·초              | 약 $0.00445         |
| 임시 저장소         | 20GB 초과분 $0.0000000308 / GB·초 | -                   |

- ARM(Graviton)은 vCPU $0.0000089944, 메모리 $0.0000009889(초당)로 x86보다 쌉니다. Fargate Spot은 최대 70% 할인, Savings Plans는 최대 50% 절감(Fargate 페이지 기준)입니다.

### 4.3 AKS

| 티어     | 내용                                                                            |
|----------|---------------------------------------------------------------------------------|
| Free     | 클러스터 관리 무료, 금융 보상 SLA 없음, 노드 10개 미만 권장(최대 1,000)         |
| Standard | API 서버 가동률 SLA(가용 영역 사용 99.95%, 미사용 99.9%), 최대 5,000 노드, 유료 |
| Premium  | Standard + 24개월 LTS                                                           |

- AKS Automatic은 Standard 티어로 만들어지고 pod 준비 SLA(적격 pod 준비 작업의 99.9%가 5분 안에 완료)가 더해집니다.
- Standard·Premium의 시간당 금액은 Azure 요금 페이지에서 숫자가 표시되지 않아 확인하지 못했습니다. Azure 가격 계산기로 확인합니다.

### 4.4 GKE

- 요금 페이지 본문을 읽지 못해 클러스터 관리 요금, 무료 크레딧, Autopilot 청구 기준을 확인하지 못했습니다. GKE 공식 요금 페이지에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. OpenShift

| 형태                    | 제품                                                                                                                                     |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| 관리형(클라우드)        | ROSA(AWS, Red Hat·AWS 공동 운영), ARO(Azure, Red Hat·Microsoft 공동 운영), OpenShift Dedicated(AWS·Google Cloud), OpenShift on IBM Cloud |
| 직접 설치(self-managed) | OpenShift Platform Plus, OpenShift Container Platform, OpenShift Kubernetes Engine, OpenShift Virtualization Engine                      |

- ROSA 요금: 워커 노드 4 vCPU당 시간 $0.171, HCP 클러스터는 시간당 $0.25 클러스터 요금 추가, AWS 인프라 요금은 따로. 1년·3년 약정은 33~55% 절감.
- 제품 페이지 머리에 "Red Hat OpenShift 5 is here."라고 나오지만, 문서 사이트가 403을 돌려줘 현재 문서 판은 확인하지 못했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 고르는 기준

| 상황                                                | 먼저 볼 것                                        | 이유                                      |
|-----------------------------------------------------|---------------------------------------------------|-------------------------------------------|
| AWS만 쓰고 Kubernetes 경험이 적음, 서비스 수가 적음 | ECS + Fargate                                     | 오케스트레이터 요금 없음, 노드 관리 없음  |
| 여러 클라우드·온프레미스에 같은 방식으로 배포       | EKS·GKE·AKS 중 주 사업자 + Helm·GitOps            | Kubernetes API가 같음                     |
| 노드 관리를 줄이고 싶은 Kubernetes                  | EKS Auto Mode, GKE Autopilot, AKS Automatic       | 노드 생성·패치를 사업자가 맡음            |
| 판을 오래 유지해야 함                               | GKE Extended, AKS LTS, EKS 연장 지원              | 최대 24~26개월. 연장 기간은 요금이 늘어남 |
| Red Hat 구독·지원 체계, 온프레미스와 같은 플랫폼    | OpenShift(ROSA·ARO·직접 설치)                     | 같은 제품을 여러 곳에                     |
| 작은 팀, 몇 대의 서버                               | [Docker Swarm](./docker_swarm.md)·[k3s](./k3s.md) | 관리형 요금 없이 단순하게                 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 옮길 때 확인할 것

이번에 공식 문서와 대조하지 않은 일반 점검 목록입니다. 실제 이전 전에는 각 사업자 문서로 확인합니다.

- 인증·권한: EKS는 IAM과 Kubernetes RBAC 연결(액세스 엔트리), GKE는 Google 계정·Workload Identity, AKS는 Microsoft Entra ID. 서비스 계정에 클라우드 권한을 주는 방식이 사업자마다 다릅니다.
- 네트워크: CNI(파드 IP를 VPC에서 받는지), 로드밸런서·Ingress 컨트롤러 종류, 사설 클러스터 구성.
- 저장소: 기본 StorageClass(EBS, Persistent Disk, Azure Disk)와 접근 모드.
- 비용: 컨트롤 플레인 요금보다 노드·로드밸런서·데이터 전송·로그 수집 비용이 크게 나오는 경우가 많습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Kubernetes 기초](./kubernetes_basic.md) — 관리형이든 아니든 같은 API
- [Docker Swarm](./docker_swarm.md) — Docker 내장 오케스트레이션
- [k3s](./k3s.md) — 직접 운영하는 경량 Kubernetes

---

## 참고 자료

- AWS: [EKS pricing](https://aws.amazon.com/eks/pricing/) · [EKS Kubernetes versions](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html) · [ECS pricing](https://aws.amazon.com/ecs/pricing/) · [Fargate pricing](https://aws.amazon.com/fargate/pricing/) · [ROSA pricing](https://aws.amazon.com/rosa/pricing/) — ★★★☆☆
- Google Cloud: [GKE release channels](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/release-channels) · [GKE release notes](https://docs.cloud.google.com/kubernetes-engine/docs/release-notes) · [GKE pricing](https://cloud.google.com/kubernetes-engine/pricing) — ★★★☆☆
- Microsoft: [AKS pricing tiers](https://learn.microsoft.com/en-us/azure/aks/free-standard-pricing-tiers) · [AKS supported versions](https://learn.microsoft.com/en-us/azure/aks/supported-kubernetes-versions) — ★★★☆☆
- Red Hat: [OpenShift](https://www.redhat.com/en/technologies/cloud-computing/openshift) — ★★★☆☆

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
