# 2026-06-18 01_re 미사용 리소스 정리
<!--
작업 지침:

[사전 확인 — Live 환경 삭제 시 필수]
  - 작업 개요의 환경(Live/Dev/Test) 항목을 반드시 기재합니다.
  - Live 계정/리전 작업은 담당자 승인 후 진행합니다.
  - EIP 삭제 전: 해당 IP가 DNS에 등록되어 있거나 서비스에서 사용 중인지 확인합니다.
  - EBS/스냅샷 삭제 전: 연결된 AMI 또는 실행 중인 인스턴스가 없는지 확인합니다.
  - terraform destroy 전: 반드시 terraform plan -destroy 출력을 먼저 확인합니다.

[기본 프로세스 — 모든 삭제 작업 공통]
  1. 출력: 삭제 대상 리소스를 먼저 조회하여 출력하고 작업자가 확인합니다.
  2. 승인: 작업자가 목록을 검토한 후 삭제를 승인합니다.
  3. 삭제: 승인 후 삭제를 진행합니다.
  4. 정리: tfstate/잔여 리소스 정리, 로그 기록, 문서 업데이트를 진행합니다.

[이슈 기록]
  - 작업 중 발생한 모든 오류/예외 상황은 즉시 §4 트러블슈팅에 기재합니다.
  - 기재 형식: 이슈 N — 제목 / 증상 / 원인 / 해결 명령어
  - 작업 완료 후 **마지막 업데이트** 날짜를 갱신합니다.
-->

01_re 계정 전 리전 미사용 리소스 정리 작업 기록입니다.

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. 작업 개요](#1-작업-개요) / [2. 사전 조사](#2-사전-조사) / [3. 삭제 리소스 목록](#3-삭제-리소스-목록)             |
| [4. 트러블슈팅](#4-트러블슈팅) / [5. 비용 절감 효과](#5-비용-절감-효과) / [6. 잔여 과금 리소스](#6-잔여-과금-리소스) |

## 1. 작업 개요

| 항목     | 값                               |
|----------|----------------------------------|
| 작업일시 | 2026-06-18 15:13 ~ 16:40 (KST)   |
| 계정     | 01_re                            |
| 리전     | 전체 (도쿄/서울/버지니아/오레곤) |
| 환경     | Dev / Test                       |
| 작업자   | sjyun                            |
| 승인자   | self                             |
| 작업목적 | 미사용 리소스 정리               |

## 2. 사전 조사

### 조사 결과

| 리전           | 리소스 유형       | 상세                                       | 월 비용 (USD) |
|----------------|-------------------|--------------------------------------------|---------------|
| ap-northeast-1 | EIP 미연결        | 52.199.51.188 (yhkim-eip1)                 | ~4            |
| ap-northeast-1 | EBS available × 2 | 16GB × 2 (2025-04)                         | ~3            |
| ap-northeast-2 | EBS available × 2 | 30GB × 2 (2025-11)                         | ~5            |
| us-east-1      | EIP 미연결 × 3    | 3.229.60.122, 52.54.201.100, 52.72.233.251 | ~11           |
| us-west-2      | EBS available × 1 | 8GB                                        | ~1            |

## 3. 삭제 리소스 목록

| 리전           | 리소스 유형                     | 상세                                       | 결과 |
|----------------|---------------------------------|--------------------------------------------|------|
| ap-northeast-1 | EC2 (game-server-windows-sjyun) | i-0bde26bb2269c41a6, t3.large              | ✅   |
| ap-northeast-1 | EBS available × 2               | 16GB × 2 (2025-04)                         | ✅   |
| ap-northeast-1 | EIP (yhkim-eip1)                | 52.199.51.188                              | ✅   |
| ap-northeast-1 | VPC + 네트워크                  | vpc-016880b95b5c8579c (83_gz_amazon)       | ✅   |
| ap-northeast-2 | EC2 × 3 + EIP × 3               | haproxy-kr-fixed-1~3, t3.medium (72_gz)    | ✅   |
| ap-northeast-2 | NLB + SG + VPC                  | haproxy-nlb, vpc-0cb4cbe1150fa9f78 (72_gz) | ✅   |
| ap-northeast-2 | EBS available × 2               | 30GB × 2 (2025-11)                         | ✅   |
| us-east-1      | EIP 미연결 × 3                  | 3.229.60.122, 52.54.201.100, 52.72.233.251 | ✅   |
| us-west-2      | EBS available × 1               | 8GB                                        | ✅   |
| ap-northeast-1 | RDS kr-an1-live-auth            | db.t3.small, MariaDB, 100GB                | ✅   |
| ap-northeast-1 | RDS kr-an1-live-common          | db.t3.small, MariaDB, 100GB                | ✅   |
| ap-northeast-1 | RDS kr-an1-live-global-rank     | db.t3.small, MariaDB, 200GB                | ✅   |
| ap-northeast-1 | RDS kr-an1-live-gms             | db.t3.small, MariaDB, 99GB                 | ✅   |
| ap-northeast-1 | RDS kr-an1-live-mail            | db.t3.small, MariaDB, 1000GB               | ✅   |
| ap-northeast-1 | RDS kr-an1-live-player          | db.t3.small, MariaDB, 1000GB               | ✅   |
| ap-northeast-1 | RDS logdb-aurora-new2           | db.t3.small, Aurora MySQL, 1GB             | ✅   |

## 4. 트러블슈팅

#### 이슈 1 — terraform destroy 응답 없음 (01-network)

- 발생일: 2026-06-18
- 상태: ✅ 해결

**증상:**

```
terraform destroy -auto-approve 실행 후 응답 없음 (83_gz_amazon, 72_gz 양쪽 동일)
```

**원인:**

VPC 삭제 시 네트워크 리소스 정리에 시간이 소요되며 terraform이 응답을 기다리는 상태였습니다.

**해결:**

```bash
# AWS CLI로 직접 삭제 후 state 정리
aws --profile 01_re --region ap-northeast-1 ec2 delete-vpc --vpc-id vpc-016880b95b5c8579c
terraform state rm module.vpc.aws_vpc.this
```

#### 이슈 2 — VPC DependencyViolation (72_gz)

- 발생일: 2026-06-18
- 상태: ✅ 해결

**증상:**

```
DependencyViolation: The vpc 'vpc-0cb4cbe1150fa9f78' has dependencies and cannot be deleted.
```

**원인:**

tfstate 외 리소스가 잔존했습니다.
- `launch-wizard-9` Security Group
- S3 VPC Endpoint (`vpce-0849851808ebf7bf0`)

**해결:**

```bash
aws --profile 01_re --region ap-northeast-2 ec2 delete-security-group \
  --group-id sg-0d0d19f52cc08e07b
aws --profile 01_re --region ap-northeast-2 ec2 delete-vpc-endpoints \
  --vpc-endpoint-ids vpce-0849851808ebf7bf0
aws --profile 01_re --region ap-northeast-2 ec2 delete-vpc \
  --vpc-id vpc-0cb4cbe1150fa9f78
```

#### 이슈 3 — prevent_destroy 차단 (83_gz_amazon 13-ec2-game)

- 발생일: 2026-06-18
- 상태: ✅ 해결

**증상:**

```
lifecycle.prevent_destroy is set, refusing to destroy
```

**원인:**

`main.tf`에 `lifecycle { prevent_destroy = true }` 설정이 있었습니다.

**해결:**

`prevent_destroy = false`로 변경 후 `terraform destroy` 진행했습니다.

## 5. 비용 절감 효과

| 항목                                   | 절감액 (월, USD) |
|----------------------------------------|------------------|
| ap-northeast-1 EIP                     | ~4               |
| ap-northeast-1 EBS 2개                 | ~3               |
| ap-northeast-1 EC2 + VPC 관련          | ~100             |
| ap-northeast-2 EC2 × 3 + EIP × 3 + NLB | ~150             |
| ap-northeast-2 EBS 2개                 | ~5               |
| us-east-1 EIP × 3                      | ~11              |
| us-west-2 EBS 1개                      | ~1               |
| 합계                                   | **~274**         |

## 6. 잔여 과금 리소스

삭제하지 않은 리소스입니다.

| 리전           | 리소스                           | 상세                             | 월 비용 (USD) |
|----------------|----------------------------------|----------------------------------|---------------|
| ap-northeast-1 | EBS 스냅샷 22개                  | 합계 ~1,459GB                    | ~44           |
| ap-northeast-2 | EBS 스냅샷 9개                   | 합계 544GB (AMI 포함)            | ~16           |
| ap-northeast-2 | RDS dev-jellybfan-db             | db.t4g.micro, PostgreSQL, 20GB   | ~12           |
| ap-northeast-2 | RDS dev-kings-event-rds-20241127 | db.t3.small, MySQL, 20GB         | ~25           |
| ap-northeast-2 | RDS dev-vespa-web-rds-20241127   | db.t3.small, MySQL, 20GB         | ~25           |
| ap-northeast-2 | RDS knowledgebase (Bedrock)      | db.serverless, Aurora PostgreSQL | 사용량 기반   |
| ap-northeast-2 | RDS kr-an2-research-integrate    | db.t3.medium, Aurora MySQL       | ~50           |
| ap-northeast-2 | RDS live-kings-event-rds         | db.t3.small, MySQL, 100GB        | ~37           |
| ap-northeast-2 | RDS live-kingsraid-web-rds       | db.t3.small, MySQL, 100GB        | ~37           |
| ap-northeast-2 | RDS live-vespainc-web-rds        | db.t3.small, MySQL, 100GB        | ~37           |
| us-west-2      | RDS cs-pgvector-db (Bedrock)     | db.serverless, Aurora PostgreSQL | 사용량 기반   |
| us-west-2      | RDS database-1                   | db.t3.small, MySQL, 20GB         | ~25           |
| us-west-2      | RDS knowledgebase (Bedrock)      | db.serverless, Aurora PostgreSQL | 사용량 기반   |

🟡 Live 서비스 RDS는 유지합니다. dev/test RDS와 EBS 스냅샷은 필요 시 삭제 검토를 권장합니다.

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-06-18

© 2026 siasia86. Licensed under CC BY 4.0.
