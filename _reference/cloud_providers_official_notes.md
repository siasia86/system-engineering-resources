---
name: cloud-providers-official-notes
description: AWS 글로벌 인프라·프리 티어·계정 권장과 Azure·Google Cloud·DigitalOcean·Alibaba Cloud·Hetzner의 리전·체험·가격·트래픽 조건을 공식 페이지 기준으로 정리, 미확인 표시.
tags:
  - aws
  - azure
  - gcp
  - digitalocean
  - alibaba-cloud
  - hetzner
last_checked: 2026-11-27
sources:
  - https://aws.amazon.com/about-aws/global-infrastructure/
  - https://aws.amazon.com/free/
  - https://aws.amazon.com/compliance/shared-responsibility-model/
  - https://aws.amazon.com/pricing/
  - https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html
  - https://azure.microsoft.com/en-us/pricing/free-services/
  - https://cloud.google.com/about/locations
  - https://www.digitalocean.com/pricing/droplets
  - https://docs.digitalocean.com/products/billing/bandwidth/
  - https://www.alibabacloud.com/global-locations
  - https://docs.hetzner.com/cloud/general/locations/
---

# 클라우드 사업자 공식 자료 참조 노트

## 1. AWS (2026-11-27)

- "The AWS Cloud spans 124 Availability Zones within 39 Geographic Regions, with announced plans for 7 more Availability Zones and 2 more AWS Regions in the Kingdom of Saudi Arabia, and Chile." 리전마다 최소 3개 AZ. Wavelength Zone 33개.
- 프리 티어: "you get $100 in credits immediately ... you can earn up to $100 more. That's up to $200 over 6 months". 계정은 6개월 뒤 또는 크레딧 소진 시 닫힘. Free 플랜(일부 서비스, 업그레이드 전 청구 없음)과 Paid 플랜. "30+ AWS services are always free within monthly usage limits".
- 책임 분담: Security "of" the Cloud(AWS) / "in" the Cloud(고객, 고른 서비스에 따라 범위가 정해짐).
- Organizations: 조직을 만든 계정이 관리 계정. OU, SCP(서비스·리소스·리전 접근 제어), RCP(리소스 의도하지 않은 사용 차단).
- 루트 사용자: 필요한 작업에만, MFA(최대 8개, 여러 개 권장), 루트 액세스 키 만들지 않기, 여러 계정은 IAM Identity Center workforce 사용자.
- 요금: 쓴 만큼, Savings Plans(1·3년 $/hour 약정, Compute·ML), 들어오는 전송 무료, EC2 나가는 전송 구간 요금. RI 설명은 pricing 페이지에서 찾지 못함.
- Well-Architected 6개 기둥: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability.

## 2. Azure

- 지역 페이지에 총수 없음(이용 가능·예정 리전 목록).
- "$200 credit to explore Azure for 30 days", "Free for your first 12 months", "65+ always-free services". VM 가격 표 렌더링 안 됨, "Standard egress charges apply."
- AKS Free 티어 무료, Standard 금액 미확인.

## 3. Google Cloud

- "43 Regions 130 Zones"(2026-03-27 갱신), "$300 in free credits and 20+ always free products". cloud.google.com/free 본문 읽기 실패. GKE 요금 미확인.

## 4. DigitalOcean

- "DigitalOcean operates 20 datacenters across 13 regions. You can create new resources in the 16 listed below."(2026-10-28)
- Basic 2 vCPU/4 GiB $24/월, $0.03571/시간, 트래픽 4,000 GiB, SSD 80 GiB. CPU-Optimized 2 vCPU/4 GiB $42/월.
- "Additional outbound transfer is billed at $0.01 per GiB. Inbound transfer to Droplets is free." Spaces 1,024 GiB 포함.
- DOKS: "the DigitalOcean control plane is free", HA $40/월. 신규 크레딧은 FAQ의 예시($5, 90일)만, 현재 조건 미확인.

## 5. Alibaba Cloud

- "Alibaba Cloud operates 106 availability zones in 31 regions around the world", "up to 12 months usage for Elastic Compute Service". 무료 페이지는 가입 창만 표시. VM·ACK·OSS 조건 미확인.

## 6. Hetzner

- "There are currently four network zones and six locations"(fsn1, nbg1, hel1, ash, hil, sin, 2026-11-11 갱신).
- CPX22(공유 AMD 2 vCPU, 4 GB, 80 GB NVMe): €16.99/월(HEL1), €19.99/월(NBG1), €0.0272/시간, VAT 별도, EU 트래픽 20 TB 포함. 포함 트래픽 미국 1 TB, 싱가포르 0.5 TB, 초과 EU·미국 €1/TB.
- Object Storage(S3 호환) FSN1·NBG1·HEL1. 관리형 Kubernetes와 신규 크레딧은 찾지 못함.
