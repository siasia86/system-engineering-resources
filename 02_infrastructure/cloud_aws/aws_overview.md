# AWS 개요
<!-- reference: _reference/cloud_providers_official_notes.md -->

AWS를 처음 맡을 때 알아야 할 바탕(리전·가용 영역, 계정 구조, 책임 분담, 요금 방식)과 자주 쓰는 서비스를 한 장으로 정리하고, 이 저장소의 AWS 문서로 연결합니다. 개별 서비스 설정은 연결된 문서에서 다룹니다.

- 확인일: 2026-11-27, AWS 공식 페이지 기준
- 예제 시험: 계정이 필요해 실행하지 않음

## 목차

| 섹션                                                                                                          |
|---------------------------------------------------------------------------------------------------------------|
| [1. 글로벌 인프라](#1-글로벌-인프라) / [2. 계정과 권한](#2-계정과-권한) / [3. 책임 분담](#3-책임-분담)        |
| [4. 서비스 지도](#4-서비스-지도) / [5. 요금](#5-요금) / [6. 설계 기준](#6-설계-기준)                          |
| [7. 처음 할 일](#7-처음-할-일) / [8. 이 저장소의 AWS 문서](#8-이-저장소의-aws-문서) / [함께 보기](#함께-보기) |

---

## 1. 글로벌 인프라

| 단위                    | 내용(2026-11-27 공식 페이지)                                          |
|-------------------------|-----------------------------------------------------------------------|
| 리전(Region)            | 39개, 사우디아라비아·칠레에 2개 추가 예정                             |
| 가용 영역(AZ)           | 124개, 7개 추가 예정. 리전마다 물리적으로 떨어진 AZ가 최소 3개        |
| Local Zones, Wavelength | 사용자 가까이 두는 작은 거점. Wavelength는 통신사 데이터센터 안(33개) |

- 서비스 대부분은 리전 단위입니다. 리전을 바꾸면 리소스·가격·쓸 수 있는 서비스가 달라집니다.
- 한 AZ 장애에 견디려면 서버·DB를 AZ 두 곳 이상에 나눕니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 계정과 권한

| 항목                | 내용                                                                                      |
|---------------------|-------------------------------------------------------------------------------------------|
| 루트 사용자         | 계정을 만든 이메일. 일상 작업에 쓰지 않음, MFA 필수, 액세스 키 만들지 않음                |
| AWS Organizations   | 여러 계정을 묶음. 조직을 만든 계정이 관리 계정, 나머지는 멤버 계정                        |
| OU                  | 계정 묶음(조직 단위). 예: prod, dev, security                                             |
| SCP / RCP           | SCP는 조직 안 서비스·리전 사용 범위 제한, RCP는 리소스 쪽에서 의도하지 않은 사용 차단     |
| IAM Identity Center | 사람 사용자의 로그인(SSO). 여러 계정이면 이것으로 workforce 사용자를 관리                 |
| IAM 역할            | 서비스·다른 계정이 임시 자격 증명으로 권한을 받음([STS AssumeRole](./sts_assume_role.md)) |

- 공식 권장: 루트 사용자는 루트가 꼭 필요한 작업에만 쓰고, MFA 장치를 여러 개 등록하며, 루트 액세스 키는 만들지 않습니다.
- 운영·개발·보안 로그를 계정으로 나누면 사고 범위와 비용을 나눠 볼 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 책임 분담

- AWS는 클라우드 자체의 보안("Security of the Cloud": 데이터센터, 하드웨어, 서비스 기반)을 맡습니다.
- 고객은 클라우드 안의 보안("Security in the Cloud")을 맡고, 범위는 고른 서비스에 따라 달라집니다. EC2는 OS 패치·방화벽·데이터까지, 관리형 서비스는 설정·권한·데이터 위주입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 서비스 지도

| 영역         | 대표 서비스                                 | 이 저장소 문서                                                                                           |
|--------------|---------------------------------------------|----------------------------------------------------------------------------------------------------------|
| 네트워크     | VPC, Route 53, CloudFront, Network Firewall | [VPC 리전 간 피어링](./vpc_peering_inter_region_guide.md), [Network Firewall](./aws_network_firewall.md) |
| 컴퓨팅       | EC2, Lambda, ECS·EKS(컨테이너)              | [관리형 컨테이너 플랫폼 비교](../containers/managed_container_platforms.md)                              |
| 스토리지     | S3, EBS, EFS                                | [S3 버킷 생성 옵션](./s3_bucket_create_options.md), [S3 Object Lock](./s3_object_lock.md)                |
| 데이터베이스 | RDS, Aurora, DynamoDB                       | -                                                                                                        |
| 보안·권한    | IAM, KMS, Secrets Manager, GuardDuty        | [AWS 보안](../../04_security/cloud/aws_security.md)                                                      |
| 관측         | CloudWatch, CloudTrail                      | [CloudWatch Agent·알람](./cloudwatch_agent_alarms.md)                                                    |
| IaC          | CloudFormation, CDK                         | [AWS CDK와 CloudFormation](../iac/aws_cdk_cloudformation.md)                                             |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 요금

- 쓴 만큼 냅니다. 장기 계약 없이 서비스별로 쓴 시간·양만큼 청구됩니다.
- Savings Plans: 1년·3년 동안 시간당 사용 금액($/hour)을 약정하면 온디맨드보다 할인됩니다(컴퓨팅·머신러닝).
- 데이터 전송: 들어오는 전송(IN)은 무료, EC2에서 나가는 전송(OUT)은 구간 요금입니다. 나가는 트래픽이 많은 서비스는 CloudFront·같은 리전 배치로 줄입니다.
- 프리 티어: 새 계정은 가입 즉시 크레딧 $100, 주요 서비스를 써 보며 최대 $100을 더 받아 6개월 동안 최대 $200입니다. Free 플랜은 일부 서비스만 쓰고 유료 플랜으로 올리기 전에는 청구되지 않으며, 계정은 6개월이 지나거나 크레딧을 다 쓰면 닫힙니다. 30개 이상 서비스는 월 사용 한도 안에서 항상 무료입니다.
- 예산 알림(AWS Budgets)과 비용 탐색기를 계정을 만들자마자 켜 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 설계 기준

Well-Architected Framework의 6개 기둥으로 설계를 점검합니다.

| 기둥                   | 보는 것                          |
|------------------------|----------------------------------|
| Operational Excellence | 배포·운영 자동화, 장애 대응 절차 |
| Security               | 권한 최소화, 암호화, 추적        |
| Reliability            | 다중 AZ, 백업·복구, 할당량       |
| Performance Efficiency | 알맞은 인스턴스·서비스 선택      |
| Cost Optimization      | 쓰지 않는 리소스 정리, 약정 할인 |
| Sustainability         | 자원 사용량과 낭비 줄이기        |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 처음 할 일

1. 루트 사용자에 MFA를 걸고 루트 액세스 키가 없는지 확인합니다.
2. IAM Identity Center(여러 계정이면 Organizations와 함께)로 관리자 사용자를 만들고 이후 작업은 그 사용자로 합니다.
3. CloudTrail을 켜서 API 호출 기록을 남깁니다.
4. AWS Budgets로 예산 알림을 겁니다.
5. 쓸 리전을 정하고, 쓰지 않는 리전은 SCP로 막는 것을 검토합니다.

- 3~5는 이번에 공식 문서와 따로 대조하지 않은 일반 권장입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 이 저장소의 AWS 문서

- [VPC 리전 간 피어링](./vpc_peering_inter_region_guide.md)
- [S3 Gateway Endpoint 계정 간 접근](./s3_gateway_endpoint_cross_account.md)
- [S3 버킷 생성 옵션](./s3_bucket_create_options.md) · [S3 Object Lock](./s3_object_lock.md) · [S3 백업 팁](./s3_backup_tips.md)
- [STS AssumeRole](./sts_assume_role.md)
- [CloudWatch Agent·알람](./cloudwatch_agent_alarms.md)
- [AWS Network Firewall](./aws_network_firewall.md)
- [클라우드 백업 비용 비교](./cloud_backup_cost_comparison.md)

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [클라우드 사업자 비교](./cloud_provider_comparison.md) — Azure, Google Cloud, DigitalOcean, Alibaba Cloud, Hetzner
- [AWS CDK와 CloudFormation](../iac/aws_cdk_cloudformation.md) — AWS IaC
- [AWS 보안](../../04_security/cloud/aws_security.md) — IAM, SG, WAF

---

## 참고 자료

- AWS: [Global infrastructure](https://aws.amazon.com/about-aws/global-infrastructure/) · [Free Tier](https://aws.amazon.com/free/) · [Shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/) · [Pricing](https://aws.amazon.com/pricing/) · [Well-Architected](https://aws.amazon.com/architecture/well-architected/) — ★★★☆☆
- AWS Docs: [Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) · [IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) · [Root user best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html) — ★★★☆☆

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
