# 클라우드 사업자 비교 (AWS · Azure · Google Cloud · DigitalOcean · Alibaba Cloud · Hetzner)
<!-- reference: _reference/cloud_providers_official_notes.md -->

여러 클라우드 사업자를 규모(리전), 체험 조건, 작은 VM 가격, 관리형 Kubernetes, 객체 저장소, 나가는 트래픽 조건으로 비교합니다. 대형 3사(AWS·Azure·Google Cloud)와 단순한 가격 체계의 사업자(DigitalOcean·Hetzner), 아시아 중심의 Alibaba Cloud를 함께 봅니다.

- 확인일: 2026-11-27, 각 사업자의 공식 페이지 기준. 가격은 페이지에 표시된 통화·세금 기준이며 바뀔 수 있습니다
- 예제 시험: 계정이 필요해 실행하지 않음. 일부 가격 표는 페이지 내용을 읽지 못해 미확인으로 표시

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 한눈에 비교](#1-한눈에-비교) / [2. 사업자별 메모](#2-사업자별-메모) / [3. 고르는 기준](#3-고르는-기준) |
| [4. 비교할 때 주의](#4-비교할-때-주의) / [함께 보기](#함께-보기)                                           |

---

## 1. 한눈에 비교

| 항목              | AWS                         | Azure                                             | Google Cloud               | DigitalOcean                                                     | Alibaba Cloud               | Hetzner                                                         |
|-------------------|-----------------------------|---------------------------------------------------|----------------------------|------------------------------------------------------------------|-----------------------------|-----------------------------------------------------------------|
| 리전·영역         | 39 리전, 124 AZ             | 미확인(리전 목록에 예정 포함)                     | 43 리전, 130 zone          | 13 리전, 20 데이터센터(신규 생성 16)                             | 31 리전, 106 AZ             | 6 위치, 4 네트워크 영역                                         |
| 체험              | 6개월 최대 $200 크레딧      | 30일 $200 크레딧, 12개월 무료 항목, 65+ 항상 무료 | $300 크레딧, 20+ 항상 무료 | 신규 프로모션 크레딧(조건 미확인)                                | ECS 최대 12개월 등 80+ 제품 | 미확인                                                          |
| 2 vCPU·4GB VM     | 미확인                      | 미확인                                            | 미확인                     | Basic $24/월($0.03571/시간)                                      | 미확인                      | CPX22 €16.99~19.99/월(VAT 별도, 위치별)                         |
| 관리형 Kubernetes | EKS(클러스터당 $0.10/시간)  | AKS(Free 티어 무료)                               | GKE(요금 미확인)           | DOKS(컨트롤 플레인 무료, HA $40/월)                              | ACK(미확인)                 | 없음(찾지 못함)                                                 |
| 객체 저장소       | S3                          | 미확인                                            | Cloud Storage              | Spaces                                                           | OSS(미확인)                 | Object Storage(S3 호환, 3개 위치)                               |
| 나가는 트래픽     | 구간 요금, 들어오는 것 무료 | 표준 요금 적용                                    | 미확인                     | Droplet 요금제마다 포함량(2 vCPU·4GB는 4,000GiB), 초과 $0.01/GiB | 미확인                      | 서버당 EU 20TB·미국 1TB·싱가포르 0.5TB 포함, 초과 EU·미국 €1/TB |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사업자별 메모

### 2.1 AWS

- 리전마다 AZ가 최소 3개입니다. 서비스 수가 가장 많고, 관리형 서비스 선택지가 넓습니다. 자세한 바탕은 [AWS 개요](./aws_overview.md)를 봅니다.

### 2.2 Azure

- 공식 지역 페이지는 리전 총수를 적지 않고, 이용 가능·예정 리전을 함께 나열합니다.
- 새 계정은 30일 동안 $200 크레딧과 12개월 무료 서비스, 65개 이상 항상 무료 서비스가 있습니다. Linux VM 가격 페이지에는 "Standard egress charges apply."라고 적혀 있습니다.
- AKS Free 티어는 클러스터 관리가 무료입니다(Standard 티어 금액은 표시되지 않아 미확인).

### 2.3 Google Cloud

- 43개 리전, 130개 zone입니다(2026-03-27 갱신 페이지). 신규 크레딧 $300과 20개 이상 항상 무료 제품이 있습니다. 무료 한도 상세 페이지는 읽지 못했습니다.

### 2.4 DigitalOcean

- Droplet 가격이 월·시간 고정이고 요금제마다 나가는 트래픽 포함량이 있습니다. Basic 2 vCPU·4GiB는 월 $24, 트래픽 4,000GiB, SSD 80GiB입니다.
- 초과 트래픽은 GiB당 $0.01, 들어오는 트래픽은 무료입니다. Spaces는 1,024GiB 나가는 트래픽을 포함합니다.
- DOKS 컨트롤 플레인은 무료이고, 컨트롤 플레인 고가용성은 월 $40입니다.

### 2.5 Alibaba Cloud

- 31개 리전, 106개 AZ입니다. 무료 체험 페이지는 가입 창만 표시돼 조건을 확인하지 못했고, 지역 페이지에 "up to 12 months usage for Elastic Compute Service"가 있습니다.

### 2.6 Hetzner

- 위치: fsn1(Falkenstein), nbg1(Nuremberg), hel1(Helsinki), ash(Ashburn), hil(Hillsboro), sin(Singapore). 네트워크 영역마다 가격이 다릅니다.
- 공유 vCPU CPX22(2 vCPU, 4GB, NVMe 80GB)는 월 €16.99(HEL1)~€19.99(NBG1), 시간당 €0.0272(VAT 별도)이고, EU에서 서버당 20TB 트래픽이 포함됩니다.
- 관리형 Kubernetes는 공식 클라우드 페이지에서 찾지 못했습니다. 직접 [k3s](../containers/k3s.md) 등으로 구성하는 경우가 많습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고르는 기준

| 상황                                                         | 먼저 볼 것                         |
|--------------------------------------------------------------|------------------------------------|
| 관리형 서비스(DB, 메시지, 분석)를 많이 쓰고 규정 준수가 중요 | AWS, Azure, Google Cloud           |
| Microsoft 365·Entra ID·Windows 자산이 많음                   | Azure                              |
| 데이터 분석·BigQuery 중심                                    | Google Cloud                       |
| VM 몇 대와 단순한 월 고정 비용, 트래픽이 많음                | DigitalOcean, Hetzner              |
| 중국 본토·아시아 사용자 중심                                 | Alibaba Cloud(현지 규제 별도 확인) |

- 위 표의 "상황→사업자"는 일반적인 경향이며 공식 자료로 대조하지 않았습니다. 실제 선택은 쓸 서비스의 리전 제공 여부와 견적으로 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 비교할 때 주의

- VM 가격만 비교하면 틀리기 쉽습니다. 나가는 트래픽, 디스크, 공인 IP, 로드밸런서, 백업, 지원 요금을 함께 계산합니다.
- 같은 이름의 인스턴스도 CPU 세대·공유 여부가 다릅니다. Hetzner CPX22처럼 공유 vCPU인지 전용인지 확인합니다.
- 통화와 세금 기준이 다릅니다(Hetzner는 EUR·VAT 별도).
- 체험 크레딧 조건(기간, 쓸 수 있는 서비스)은 자주 바뀝니다. 가입 직전에 공식 페이지로 다시 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [AWS 개요](./aws_overview.md) — 리전, 계정 구조, 요금 방식
- [관리형 컨테이너 플랫폼 비교](../containers/managed_container_platforms.md) — EKS, GKE, AKS
- [클라우드 백업 비용 비교](./cloud_backup_cost_comparison.md) — 저장 비용 비교

---

## 참고 자료

- AWS: [Global infrastructure](https://aws.amazon.com/about-aws/global-infrastructure/) · [Free Tier](https://aws.amazon.com/free/) — ★★★☆☆
- Azure: [Geographies](https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/) · [Free services](https://azure.microsoft.com/en-us/pricing/free-services/) · [Linux VM pricing](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/) — ★★★☆☆
- Google Cloud: [Locations](https://cloud.google.com/about/locations) — ★★★☆☆
- DigitalOcean: [Droplet pricing](https://www.digitalocean.com/pricing/droplets) · [Regional availability](https://docs.digitalocean.com/platform/regional-availability/) · [Kubernetes pricing](https://www.digitalocean.com/pricing/kubernetes) · [Bandwidth billing](https://docs.digitalocean.com/products/billing/bandwidth/) — ★★★☆☆
- Alibaba Cloud: [Global locations](https://www.alibabacloud.com/global-locations) — ★★★☆☆
- Hetzner: [Cloud](https://www.hetzner.com/cloud/) · [Regular performance](https://www.hetzner.com/cloud/regular-performance/) · [Locations](https://docs.hetzner.com/cloud/general/locations/) — ★★★☆☆

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
