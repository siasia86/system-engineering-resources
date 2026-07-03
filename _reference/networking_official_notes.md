---
name: networking-official-notes
description: BGP/DDoS/CDN/VPC 관련 RFC, AWS, Cloudflare 공식 문서 참조 노트. 04_system_engineer/02_operations/ 네트워크 문서 생성/검토 시 참조.
tags:
  - bgp
  - ddos
  - cdn
  - vpc
  - cloudflare
  - aws
  - reference
last_checked: 2026-07-03
sources:
  - https://datatracker.ietf.org/doc/html/rfc4271
  - https://datatracker.ietf.org/doc/html/rfc5575
  - https://datatracker.ietf.org/doc/html/rfc5635
  - https://datatracker.ietf.org/doc/html/rfc7239
  - https://developers.cloudflare.com/spectrum/
  - https://developers.cloudflare.com/magic-transit/
  - https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html
  - https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html
---

# 네트워킹 공식 참조 노트

## 1. BGP (확인일: 2026-07-03)

### 공식 소스

| RFC      | 제목                                            | 용도                     |
|----------|-------------------------------------------------|--------------------------|
| RFC 4271 | A Border Gateway Protocol 4 (BGP-4)             | BGP 프로토콜 사양        |
| RFC 5575 | Dissemination of Flow Specification Rules       | BGP FlowSpec (DDoS 필터) |
| RFC 5635 | Remote Triggered Black Hole Filtering with uRPF | RTBH (블랙홀 라우팅)     |

### 검증된 사실 (2026-07-03)

| 항목                | 값                                            | 출처                 |
|---------------------|-----------------------------------------------|----------------------|
| RFC 4271 = BGP-4    | 경로 벡터 프로토콜, AS 간 라우팅              | datatracker.ietf.org |
| RFC 5575 = FlowSpec | BGP NLRI로 트래픽 필터 전파                   | datatracker.ietf.org |
| RFC 5635 = RTBH     | 원격 트리거 블랙홀 (DDoS 완화)                | datatracker.ietf.org |
| ASN 할당 체계       | IANA → RIR(APNIC 등) → NIR(KISA) → ISP/사용자 | 표준 체계            |

## 2. Cloudflare (확인일: 2026-07-03)

### 공식 소스

| 제품          | URL                                              | 설명                            |
|---------------|--------------------------------------------------|---------------------------------|
| Spectrum      | https://developers.cloudflare.com/spectrum/      | TCP/UDP proxy + DDoS 보호       |
| Magic Transit | https://developers.cloudflare.com/magic-transit/ | L3 DDoS, BGP + GRE/IPsec tunnel |

### 검증된 사실 (2026-07-03)

| 항목               | 값                                            | 출처                      |
|--------------------|-----------------------------------------------|---------------------------|
| Spectrum           | "Proxy and protect TCP and UDP applications"  | developers.cloudflare.com |
| Spectrum 용도      | MQTT, email, file transfer, games 등 non-HTTP | developers.cloudflare.com |
| Magic Transit      | L3/L4 DDoS 보호, 자체 IP prefix 대상          | cloudflare.com            |
| Magic Transit 요구 | BGP 피어링 + GRE/IPsec tunnel + ASN 필요      | cloudflare.com            |

## 3. CDN / Proxy (확인일: 2026-07-03)

### 공식 소스

| RFC      | 제목                     | 용도                   |
|----------|--------------------------|------------------------|
| RFC 7239 | Forwarded HTTP Extension | X-Forwarded-For 표준화 |

### 검증된 사실 (2026-07-03)

| 항목            | 값                                             | 출처                 |
|-----------------|------------------------------------------------|----------------------|
| RFC 7239        | Forwarded 헤더 (X-Forwarded-For 대체 표준)     | datatracker.ietf.org |
| X-Forwarded-For | 비표준이지만 사실상 표준, 클라이언트 위조 가능 | 공통 지식            |

## 4. AWS VPC (확인일: 2026-07-03)

### 공식 소스

| 문서              | URL                                                                       | 용도                  |
|-------------------|---------------------------------------------------------------------------|-----------------------|
| Gateway Endpoints | https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html | S3/DynamoDB 무료 접근 |
| VPC Peering       | https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html   | 리전 간 VPC 연결      |

### 검증된 사실 (2026-07-03)

| 항목                     | 값                                      | 출처                |
|--------------------------|-----------------------------------------|---------------------|
| Gateway Endpoint 비용    | "There is no additional charge" (무료)  | docs.aws.amazon.com |
| VPC Peering inter-Region | "The VPCs can be in different Regions"  | docs.aws.amazon.com |
| inter-Region 암호화      | "All inter-Region traffic is encrypted" | docs.aws.amazon.com |
