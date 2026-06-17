# AWS Network Firewall

AWS VPC Network Firewall 생성, 설정, 삭제 가이드입니다.

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 구성 요소](#2-구성-요소) / [3. 생성 순서](#3-생성-순서)                           |
| [4. 삭제 순서](#4-삭제-순서) / [5. 운영 팁](#5-운영-팁) / [6. 비용](#6-비용)                             |

## 1. 개요

AWS Network Firewall은 VPC 인바운드/아웃바운드 트래픽을 Stateful/Stateless 규칙으로 필터링하는 관리형 방화벽 서비스입니다.

트래픽 흐름:

```
인터넷
  │
  v
IGW
  │
  v
Firewall Endpoint (VPC Endpoint)   ← Network Firewall이 여기서 패킷 검사
  │
  v
EC2 / 서브넷
```

라우팅 테이블에서 `0.0.0.0/0` next-hop을 Firewall Endpoint(`vpce-xxx`)로 지정하여 트래픽을 우회시킵니다.

## 2. 구성 요소

| 구성 요소         | 설명                                            |
|-------------------|-------------------------------------------------|
| Firewall          | 실제 방화벽 리소스 (VPC + 서브넷에 배치)        |
| Firewall Policy   | Rule Group을 묶는 정책 (비용 없음)              |
| Stateless RG      | 5-tuple 기반 패킷 필터링 (순서 있음)            |
| Stateful RG       | 연결 상태 추적, Suricata 규칙 지원              |
| Firewall Endpoint | 각 AZ에 생성되는 VPC Endpoint (과금 대상)       |
| Logging Config    | FLOW / ALERT / TLS 로그 → CloudWatch/S3/Kinesis |


## 3. 생성 순서

### Rule Group 생성

```bash
# Stateless Rule Group 예시
aws network-firewall create-rule-group \
  --rule-group-name "GameWhitelist-RuleGroup-shield-1" \
  --type STATELESS \
  --capacity 100 \
  --rule-group file://stateless-rules.json \
  --region ap-northeast-3
```

### Firewall Policy 생성

```bash
aws network-firewall create-firewall-policy \
  --firewall-policy-name "anf-policy" \
  --firewall-policy '{
    "StatelessDefaultActions": ["aws:forward_to_sfe"],
    "StatelessFragmentDefaultActions": ["aws:forward_to_sfe"],
    "StatelessRuleGroupReferences": [
      {"ResourceArn": "arn:aws:...:stateless-rulegroup/GameWhitelist-RuleGroup-shield-1", "Priority": 1}
    ],
    "StatefulRuleGroupReferences": [
      {"ResourceArn": "arn:aws:...:stateful-rulegroup/ip-policy"}
    ]
  }' \
  --region ap-northeast-3
```

### Firewall 생성

```bash
aws network-firewall create-firewall \
  --firewall-name "anf-fw" \
  --firewall-policy-arn "arn:aws:network-firewall:ap-northeast-3:ACCOUNT:firewall-policy/anf-policy" \
  --vpc-id "vpc-047cbd5548e38a136" \
  --subnet-mappings SubnetId=subnet-0c10c04f4a40f8665 \
  --region ap-northeast-3
```

상태 확인 (`READY` 될 때까지 대기):

```bash
aws network-firewall describe-firewall \
  --firewall-name anf-fw \
  --query "FirewallStatus.Status" \
  --region ap-northeast-3
```

### 로깅 설정

```bash
aws network-firewall update-logging-configuration \
  --firewall-name anf-fw \
  --logging-configuration '{
    "LogDestinationConfigs": [
      {"LogType": "FLOW",  "LogDestinationType": "CloudWatchLogs", "LogDestination": {"logGroup": "nfw-log"}},
      {"LogType": "ALERT", "LogDestinationType": "CloudWatchLogs", "LogDestination": {"logGroup": "nfw-log"}},
      {"LogType": "TLS",   "LogDestinationType": "CloudWatchLogs", "LogDestination": {"logGroup": "nfw-log"}}
    ]
  }' \
  --region ap-northeast-3
```

🟡 여러 로그 타입은 단일 API 호출에 모두 포함해야 합니다. 개별 호출로 추가하면 `InvalidRequestException`이 발생합니다.

### 라우팅 테이블 연결

Firewall Endpoint ID 확인:

```bash
aws network-firewall describe-firewall \
  --firewall-name anf-fw \
  --query "FirewallStatus.SyncStates" \
  --region ap-northeast-3
```

라우팅 테이블에 Firewall Endpoint 추가:

```bash
aws ec2 create-route \
  --route-table-id rtb-00ce5067ba2939098 \
  --destination-cidr-block 0.0.0.0/0 \
  --vpc-endpoint-id vpce-0cf1955108b5564ac \
  --region ap-northeast-3
```

## 4. 삭제 순서

삭제는 생성 역순으로 진행합니다.

```
1. 라우팅 테이블에서 Firewall Endpoint 라우트 제거
2. 로깅 설정 제거 (로그 타입을 순서대로 하나씩 줄임)
3. Firewall 삭제
4. Firewall Policy 삭제 (선택)
5. Rule Group 삭제 (선택)
```

### 1단계 — 라우팅 테이블 라우트 제거

```bash
aws ec2 delete-route \
  --route-table-id rtb-00ce5067ba2939098 \
  --destination-cidr-block 0.0.0.0/0 \
  --region ap-northeast-3
```

### 2단계 — 로깅 설정 제거

🟡 빈 배열로 한 번에 제거할 수 없습니다. 로그 타입 수만큼 순차 호출이 필요합니다.

```bash
# FLOW 제거
aws network-firewall update-logging-configuration \
  --firewall-name anf-fw \
  --logging-configuration '{
    "LogDestinationConfigs": [
      {"LogType": "TLS",   "LogDestinationType": "CloudWatchLogs", "LogDestination": {"logGroup": "nfw-log"}},
      {"LogType": "ALERT", "LogDestinationType": "CloudWatchLogs", "LogDestination": {"logGroup": "nfw-log"}}
    ]
  }' --region ap-northeast-3

# TLS 제거
aws network-firewall update-logging-configuration \
  --firewall-name anf-fw \
  --logging-configuration '{
    "LogDestinationConfigs": [
      {"LogType": "ALERT", "LogDestinationType": "CloudWatchLogs", "LogDestination": {"logGroup": "nfw-log"}}
    ]
  }' --region ap-northeast-3

# 전체 제거
aws network-firewall update-logging-configuration \
  --firewall-name anf-fw \
  --logging-configuration '{"LogDestinationConfigs": []}' \
  --region ap-northeast-3
```

### 3단계 — Firewall 삭제

```bash
aws network-firewall delete-firewall \
  --firewall-name anf-fw \
  --region ap-northeast-3
```

상태 확인 (`DELETING` → 리소스 사라짐):

```bash
aws network-firewall describe-firewall \
  --firewall-name anf-fw \
  --query "FirewallStatus.Status" \
  --region ap-northeast-3
```

### 4단계 — Firewall Policy 삭제 (선택)

```bash
aws network-firewall delete-firewall-policy \
  --firewall-policy-name anf-policy \
  --region ap-northeast-3
```

### 5단계 — Rule Group 삭제 (선택)

```bash
aws network-firewall delete-rule-group \
  --rule-group-name GameWhitelist-RuleGroup-shield-1 \
  --type STATELESS \
  --region ap-northeast-3
```

## 5. 운영 팁

### 삭제 전 체크리스트

```bash
# 라우팅 테이블에서 vpce 라우트 사용 여부 확인
aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=<VPC_ID>" \
  --query "RouteTables[].[RouteTableId, Routes[?VpcEndpointId!=null].[DestinationCidrBlock,VpcEndpointId]]" \
  --region ap-northeast-3

# DeleteProtection 확인 (true이면 삭제 불가)
aws network-firewall describe-firewall \
  --firewall-name anf-fw \
  --query "Firewall.DeleteProtection" \
  --region ap-northeast-3
```


### 실전 이슈 기록 (2026-06-17, ap-northeast-3)

#### 이슈 1 — 로깅 설정 동시 제거 불가

- 발생: `anf-fw` 삭제 시 로깅 설정 제거 단계

**증상:**

```
InvalidRequestException: Given logging configuration attempts to
create/modify multiple log destination configs
```

**원인:** AWS API는 로그 타입(FLOW/TLS/ALERT) 여러 개를 단일 호출로 제거하는 것을 허용하지 않습니다.

**해결:** 로그 타입 수만큼 순차 호출하여 하나씩 줄입니다. ([4단계 참고](#4-삭제-순서))

---

#### 이슈 2 — 라우팅 테이블 DependencyViolation

- 발생: 서브넷 삭제 후 라우팅 테이블 삭제 단계

**증상:**

```
DependencyViolation: The routeTable 'rtb-0c3cd0507f0ed6714'
has dependencies and cannot be deleted.
```

**원인:** 서브넷 삭제 후에도 라우팅 테이블의 association 레코드가 잔존합니다.

**해결:** `disassociate-route-table`로 association을 명시적으로 해제한 후 삭제합니다.

```bash
# association ID 확인
aws ec2 describe-route-tables   --route-table-ids rtb-xxx   --query "RouteTables[0].Associations[0].RouteTableAssociationId"   --output text

# association 해제
aws ec2 disassociate-route-table --association-id rtbassoc-xxx

# 라우팅 테이블 삭제
aws ec2 delete-route-table --route-table-id rtb-xxx
```

---

#### 이슈 3 — VPC DependencyViolation (비동기 삭제 미완료)

- 발생: 서브넷/라우팅 테이블 삭제 후 VPC 삭제 단계

**증상:**

```
DependencyViolation: The vpc 'vpc-xxx' has dependencies and cannot be deleted.
```

**원인:** Firewall(`anf-fw`)과 NAT Gateway는 **비동기 삭제**입니다. 삭제 요청 후 내부 리소스(VPC Endpoint 등)가 완전히 정리되기 전에 VPC 삭제를 시도하면 실패합니다.

**해결:** 삭제 상태가 `DELETED`/`deleted`로 바뀐 것을 확인 후 다음 단계로 진행합니다.

```bash
# Firewall 삭제 완료 확인
aws network-firewall list-firewalls   --query "Firewalls[?FirewallName=='anf-fw']" --output text
# 결과 없음 = 삭제 완료

# NAT Gateway 삭제 완료 확인
aws ec2 describe-nat-gateways   --nat-gateway-ids nat-xxx   --query "NatGateways[0].State" --output text
# deleted = 삭제 완료
```

🟡 올바른 삭제 전체 순서:

```
1.  라우팅 테이블 vpce 라우트 제거
2.  로깅 설정 순차 제거 (이슈 1)
3.  Firewall 삭제 → DELETED 확인 대기
4.  NAT GW 삭제 → deleted 확인 대기
5.  EIP 해제
6.  서브넷 삭제
7.  라우팅 테이블 disassociate → 삭제 (이슈 2)
8.  IGW detach → 삭제
9.  VPC 삭제
```

### 오류 대응

| 오류                                                        | 원인                          | 해결                              |
|-------------------------------------------------------------|-------------------------------|-----------------------------------|
| `Cannot delete firewall with a logging configuration`       | 로깅 설정이 남아있음          | 2단계 로깅 설정 제거 후 재시도    |
| `InvalidRequestException: multiple log destination configs` | 로그 타입 동시 추가/제거 시도 | 한 번에 하나씩 줄여가며 순차 호출 |
| `InvalidRoute.NotFound`                                     | 라우트가 이미 없음            | 무시하고 다음 단계 진행           |
| `ResourceNotFoundException`                                 | 이미 삭제됨                   | 무시하고 다음 단계 진행           |


## 6. 비용

| 항목              | 단가 (ap-northeast-3 기준) |
|-------------------|----------------------------|
| Firewall Endpoint | $0.395 / 시간 / AZ         |
| 트래픽 처리       | $0.065 / GB                |
| Firewall Policy   | 무료                       |
| Rule Group        | 무료                       |


🟡 Firewall Endpoint는 AZ별 과금입니다. 멀티 AZ 구성 시 AZ 수만큼 비용이 발생합니다.

## 참고 자료

- AWS Documentation: [docs.aws.amazon.com/network-firewall](https://docs.aws.amazon.com/network-firewall/latest/developerguide/) — ★★★☆☆
- AWS CLI Reference: [awscli.amazonaws.com](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/network-firewall/index.html) — ★★★☆☆

---

**작성일**: 2026-06-17

**마지막 업데이트**: 2026-06-17

© 2026 siasia86. Licensed under CC BY 4.0.
