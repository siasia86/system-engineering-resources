# 2026-06-17 anf-fw 삭제 작업 기록

오사카(ap-northeast-3) 리전 AWS Network Firewall `anf-fw` 및 연관 VPC 리소스 전체 삭제 작업 기록입니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 작업 개요](#1-작업-개요) / [2. 삭제 전 리소스 현황](#2-삭제-전-리소스-현황)                       |
| [3. 작업 순서 및 결과](#3-작업-순서-및-결과) / [4. 트러블슈팅](#4-트러블슈팅)                         |
| [5. 삭제 후 상태](#5-삭제-후-상태)                                                                    |

## 1. 작업 개요

| 항목     | 값                                  |
|----------|-------------------------------------|
| 작업일시 | 2026-06-17 14:26 ~ 14:39 (KST)      |
| 계정     | 01_re (980527594869)                |
| 리전     | ap-northeast-3 (오사카)             |
| 작업자   | sjyun                               |
| 작업목적 | anf-fw 및 연관 VPC 리소스 전체 삭제 |
| 결과     | ✅ 전체 삭제 완료                   |


## 2. 삭제 전 리소스 현황

### Network Firewall

| 항목     | 값                      |
|----------|-------------------------|
| 작업일시 | 2026-06-17 (KST)        |
| 계정     | 01_re (980527594869)    |
| 리전     | ap-northeast-3 (오사카) |
| 삭제방법 | 콘솔 또는 CLI terminate |


### 로깅 설정

| LogType | 대상                 | LogDestinationType |
|---------|----------------------|--------------------|
| FLOW    | nfw-log (CloudWatch) | CloudWatchLogs     |
| TLS     | nfw-log (CloudWatch) | CloudWatchLogs     |
| ALERT   | nfw-log (CloudWatch) | CloudWatchLogs     |

### 연결된 Rule Group (6개, 삭제 제외)

| 유형      | 이름                             |
|-----------|----------------------------------|
| Stateful  | ip-policy                        |
| Stateless | GameWhitelist-RuleGroup-shield-1 |
| Stateless | GameWhitelist-RuleGroup-shield-2 |
| Stateless | GameWhitelist-RuleGroup-shield-3 |
| Stateless | GameWhitelist-RuleGroup-shield-4 |
| Stateless | GameWhitelist-RuleGroup-shield-5 |

### VPC 및 네트워크 리소스

| 리소스       | ID                         | Name      | 비고             |
|--------------|----------------------------|-----------|------------------|
| VPC          | vpc-047cbd5548e38a136      | -         | 10.0.0.0/16      |
| IGW          | igw-0410ee400a06575dd      | anw-igw   | -                |
| NAT GW       | nat-1447a6028114ef6d1      | -         | 16.209.8.241     |
| EIP          | eipalloc-0e3345d04469221db | -         | 16.209.8.241     |
| Subnet pub-1 | subnet-06cd61c2b59a6a3ec   | anw-pub-1 | 10.0.10.0/24, 3a |
| Subnet pub-2 | subnet-090f23fe24ebd280a   | anw-pub-2 | 10.0.11.0/24, 3b |
| Subnet pri-1 | subnet-0657d36e245b49e50   | anw-pri-1 | 10.0.20.0/24, 3a |
| Subnet pri-2 | subnet-0df23808f2ba71e54   | anw-pri-2 | 10.0.21.0/24, 3b |
| Subnet fw-1  | subnet-0c10c04f4a40f8665   | anw-fw-1  | 10.0.0.0/24, 3a  |
| Subnet fw-2  | subnet-0a17f13b4556b30d6   | anw-fw-2  | 10.0.1.0/24, 3b  |

### 라우팅 테이블 (삭제 전)

| RouteTableId          | 연결 서브넷 | 0.0.0.0/0 next-hop          |
|-----------------------|-------------|-----------------------------|
| rtb-00ce5067ba2939098 | anw-pri-2   | vpce-0cf1955108b5564ac (FW) |
| rtb-0d953ff368bafe53a | anw-pub-1   | igw-0410ee400a06575dd       |
| rtb-0670d263350dd4cb6 | main        | (없음)                      |
| rtb-0b0d0465e782f626d | (미연결)    | igw-0410ee400a06575dd       |
| rtb-0c3cd0507f0ed6714 | (미연결)    | (없음)                      |
| rtb-060bd50e833b4da68 | anw-fw-1    | (None, 블랙홀)              |

### EC2 / Security Group

- EC2 인스턴스: 없음
- Security Group: `sg-007bec4a83761c8c4` (default) — 삭제 제외

## 3. 작업 순서 및 결과

| 단계 | 작업                                | 결과 |
|------|-------------------------------------|------|
| 1    | 로깅 설정 FLOW 제거                 | ✅   |
| 2    | 로깅 설정 TLS 제거                  | ✅   |
| 3    | 로깅 설정 ALERT 제거 (빈 배열)      | ✅   |
| 4    | anf-fw 삭제 요청 (DELETING)         | ✅   |
| 5    | NAT GW nat-1447a6028114ef6d1 삭제   | ✅   |
| 6    | EIP eipalloc-0e3345d04469221db 해제 | ✅   |
| 7    | 서브넷 6개 삭제                     | ✅   |
| 8    | 라우팅 테이블 5개 삭제              | ✅   |
| 9    | IGW detach 후 삭제                  | ✅   |
| 10   | VPC vpc-047cbd5548e38a136 삭제      | ✅   |

### 유지된 리소스 (요청에 의해 삭제 제외)

| 리소스          | 이름/ID                          |
|-----------------|----------------------------------|
| Firewall Policy | anf-policy                       |
| Stateful RG     | ip-policy                        |
| Stateless RG    | GameWhitelist-RuleGroup-shield-1 |
| Stateless RG    | GameWhitelist-RuleGroup-shield-2 |
| Stateless RG    | GameWhitelist-RuleGroup-shield-3 |
| Stateless RG    | GameWhitelist-RuleGroup-shield-4 |
| Stateless RG    | GameWhitelist-RuleGroup-shield-5 |

🟡 Firewall Policy와 Rule Group은 비용이 발생하지 않습니다.

## 4. 트러블슈팅

#### 이슈 1 — 로깅 설정 동시 제거 불가

**오류:**

```
InvalidRequestException: Given logging configuration attempts to
create/modify multiple log destination configs
```

**원인:** AWS API는 로그 타입 여러 개를 단일 호출로 제거하는 것을 허용하지 않습니다.

**해결:** FLOW → TLS → ALERT 순서로 하나씩 줄여가며 3회 순차 호출합니다.

#### 이슈 2 — 라우팅 테이블 DependencyViolation

**오류:**

```
DependencyViolation: The routeTable 'rtb-0c3cd0507f0ed6714'
has dependencies and cannot be deleted.
```

**원인:** 서브넷 삭제 후에도 association 레코드(`rtbassoc-05a7c2abd639b7f56`)가 잔존합니다.

**해결:**

```bash
aws ec2 disassociate-route-table \
  --association-id rtbassoc-05a7c2abd639b7f56 --region ap-northeast-3
aws ec2 delete-route-table \
  --route-table-id rtb-0c3cd0507f0ed6714 --region ap-northeast-3
```

#### 이슈 3 — VPC DependencyViolation (비동기 삭제 미완료)

**오류:**

```
DependencyViolation: The vpc 'vpc-047cbd5548e38a136'
has dependencies and cannot be deleted.
```

**원인:** Firewall과 NAT GW는 비동기 삭제입니다. 내부 리소스(VPC Endpoint 등)가 완전히 정리되기 전에 VPC 삭제를 시도했습니다.

**해결:** 삭제 상태를 확인 후 VPC 삭제를 재시도합니다.

```bash
# Firewall 삭제 완료 확인 (결과 없음 = 완료)
aws network-firewall list-firewalls \
  --query "Firewalls[?FirewallName=='anf-fw']" --output text --region ap-northeast-3

# NAT GW 삭제 완료 확인
aws ec2 describe-nat-gateways \
  --nat-gateway-ids nat-1447a6028114ef6d1 \
  --query "NatGateways[0].State" --output text --region ap-northeast-3
# deleted = 완료
```

## 5. 삭제 후 상태

ap-northeast-3 리전 확인 결과:

- EC2: 없음
- VPC vpc-047cbd5548e38a136: 삭제됨
- Network Firewall anf-fw: 삭제됨
- anf-policy / Rule Group 6개: 유지 중
- 과금 발생 리소스: 없음


## 6. Windows EC2 인스턴스 삭제 (추가 작업)

| 항목     | 값                      |
|----------|-------------------------|
| 작업일시 | 2026-06-17 (KST)        |
| 계정     | 01_re (980527594869)    |
| 리전     | ap-northeast-3 (오사카) |
| 삭제방법 | 콘솔 또는 CLI terminate |

### 삭제된 인스턴스

| Name        | InstanceId          | Type      | 삭제 시각 (UTC)         |
|-------------|---------------------|-----------|-------------------------|
| test-remote | i-09e7abb19cd2059af | t3.medium | 2026-06-17 05:12:15 GMT |
| test-pub    | i-0886b0b9e8aa5832d | t3.medium | 2026-06-17 05:12:15 GMT |
| test-pri    | i-0859ade44caa03b18 | t3.medium | 2026-06-17 05:12:15 GMT |



---

**작성일**: 2026-06-17

**마지막 업데이트**: 2026-06-17

© 2026 siasia86. Licensed under CC BY 4.0.
