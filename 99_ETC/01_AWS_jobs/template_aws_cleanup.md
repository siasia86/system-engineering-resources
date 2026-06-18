# YYYY-MM-DD [계정명] 미사용 리소스 정리
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

[terraform destroy 응답 없음 시]
  1. 출력: terraform plan -destroy 및 terraform state list 로 삭제 대상 확인
  2. 승인: 작업자가 CLI 직접 삭제를 승인
  3. 삭제: AWS CLI로 리소스 직접 삭제
  4. 정리: terraform state rm 으로 state 정리

[이슈 기록]
  - 작업 중 발생한 모든 오류/예외 상황은 즉시 §4 트러블슈팅에 기재합니다.
  - 기재 형식: 이슈 N — 제목 / 증상 / 원인 / 해결 명령어
  - 해결하지 못한 경우에도 상태를 🟡 (우회) 또는 ❌ (미해결)로 표시합니다.
  - 작업 완료 후 **마지막 업데이트** 날짜를 갱신합니다.
-->

[계정명] 계정 [리전/전체] 미사용 리소스 정리 작업 기록입니다.

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. 작업 개요](#1-작업-개요) / [2. 사전 조사](#2-사전-조사) / [3. 삭제 리소스 목록](#3-삭제-리소스-목록)             |
| [4. 트러블슈팅](#4-트러블슈팅) / [5. 비용 절감 효과](#5-비용-절감-효과) / [6. 잔여 과금 리소스](#6-잔여-과금-리소스) |

## 1. 작업 개요

| 항목     | 값                                 |
|----------|------------------------------------|
| 작업일시 | YYYY-MM-DD HH:MM (KST)             |
| 계정     | [계정명]                           |
| 리전     | [리전 또는 전체]                   |
| 환경     | Live / Dev / Test (해당 항목 선택) |
| 작업자   | [작업자명]                         |
| 승인자   | [승인자명 또는 self]               |
| 작업목적 | 미사용 리소스 정리                 |

## 2. 사전 조사

조사 명령어:

```bash
# [사전 확인] EC2 running 목록 (EIP/EBS가 서비스 중인지 확인)
aws --profile [profile] --region [region] ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key=='Name']|[0].Value,PublicIpAddress]" \
  --output text

# [사전 확인] 스냅샷 → AMI 연결 여부 확인 (삭제 전 필수)
# AMI에 연결된 스냅샷이 있으면 먼저 AMI를 deregister 후 스냅샷 삭제
aws --profile [profile] --region [region] ec2 describe-images \
  --owners self \
  --query "Images[].[ImageId,Name,BlockDeviceMappings[0].Ebs.SnapshotId]" \
  --output text
# 여러 볼륨이 연결된 AMI는 아래로 확인
# aws ... describe-images --owners self --output json | grep SnapshotId

# EIP 미연결
aws --profile [profile] --region [region] ec2 describe-addresses \
  --query "Addresses[?AssociationId==null].[AllocationId,PublicIp]" --output text

# EBS available
aws --profile [profile] --region [region] ec2 describe-volumes \
  --filters "Name=status,Values=available" \
  --query "Volumes[].[VolumeId,Size,CreateTime]" --output text

# 스냅샷
aws --profile [profile] --region [region] ec2 describe-snapshots \
  --owner-ids self \
  --query "Snapshots[].[SnapshotId,VolumeSize,StartTime,Description]" --output text

# NAT GW
aws --profile [profile] --region [region] ec2 describe-nat-gateways \
  --filter "Name=state,Values=available" \
  --query "NatGateways[].[NatGatewayId,State]" --output text

# NLB/ALB
aws --profile [profile] --region [region] elbv2 describe-load-balancers \
  --query "LoadBalancers[].[LoadBalancerName,Type,State.Code]" --output text
```

### 조사 결과

| 리전   | 리소스 유형 | 상세   | 월 비용 (USD) |
|--------|-------------|--------|---------------|
| [리전] | [유형]      | [상세] | [금액]        |

## 3. 삭제 리소스 목록

| 리전   | 리소스 유형 | 상세   | 결과   |
|--------|-------------|--------|--------|
| [리전] | [유형]      | [상세] | [결과] |

### 삭제 명령어

```bash
# EIP 해제
aws --profile [profile] --region [region] ec2 release-address \
  --allocation-id [alloc-id]

# EBS 삭제
aws --profile [profile] --region [region] ec2 delete-volume \
  --volume-id [vol-id]

# 스냅샷 삭제
aws --profile [profile] --region [region] ec2 delete-snapshot \
  --snapshot-id [snap-id]

# NAT GW 삭제 (삭제 후 상태가 deleted 될 때까지 대기 필요)
aws --profile [profile] --region [region] ec2 delete-nat-gateway \
  --nat-gateway-id [nat-id]
# NAT GW에 연결된 EIP는 삭제 완료 후 별도 해제 필요
# aws ... ec2 release-address --allocation-id [alloc-id]
```

## 4. 트러블슈팅

발생한 이슈가 없으면 이 섹션은 생략합니다.

#### 이슈 N — [제목]

- 발생일: YYYY-MM-DD
- 상태: ✅ 해결 / 🟡 우회 / ❌ 미해결

**증상:**

```
[오류 메시지]
```

**원인:**

[원인 설명]

**해결:**

```bash
[해결 명령어]
```

---

자주 발생하는 이슈 참고:

#### 참고 — VPC DependencyViolation

VPC 삭제 시 tfstate 외 리소스가 잔존하면 발생합니다.

```bash
# 잔여 리소스 확인
aws --profile [profile] --region [region] ec2 describe-network-interfaces \
  --filters "Name=vpc-id,Values=[vpc-id]" --output text
aws --profile [profile] --region [region] ec2 describe-vpc-endpoints \
  --filters "Name=vpc-id,Values=[vpc-id]" "Name=vpc-endpoint-state,Values=available" \
  --query "VpcEndpoints[].[VpcEndpointId,ServiceName]" --output text
aws --profile [profile] --region [region] ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=[vpc-id]" \
  --query "SecurityGroups[?GroupName!='default'].[GroupId,GroupName]" --output text
```

#### 참고 — terraform destroy 응답 없음

프로세스: 출력 → 작업자 확인/승인 → 삭제 → state 정리

```bash
# 1. 출력: 삭제 대상 미리 확인 (작업자 검토, Terraform 1.0+)
terraform plan -destroy
terraform state list

# 2. 승인: 작업자가 목록 확인 후 CLI 직접 삭제 결정

# 3. 삭제: AWS CLI로 직접 삭제 (예시)
aws --profile [profile] --region [region] ec2 delete-volume --volume-id vol-xxx
aws --profile [profile] --region [region] ec2 delete-subnet --subnet-id subnet-xxx
aws --profile [profile] --region [region] ec2 delete-vpc --vpc-id vpc-xxx

# 4. 정리: tfstate에서 제거
terraform state rm [resource.name]
```

## 5. 비용 절감 효과

| 항목   | 절감액 (월, USD) |
|--------|------------------|
| [항목] | [금액]           |
| 합계   | [합계]           |

## 6. 잔여 과금 리소스

삭제하지 않은 리소스입니다.

| 리전   | 리소스   | 상세   | 월 비용 (USD) |
|--------|----------|--------|---------------|
| [리전] | [리소스] | [상세] | [금액]        |

🟡 잔여 리소스 삭제 여부는 별도 확인 후 결정합니다.

---

**작성일**: YYYY-MM-DD

**마지막 업데이트**: YYYY-MM-DD

© 2026 siasia86. Licensed under CC BY 4.0.
