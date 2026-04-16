# Inter-Region VPC Peering 가이드

같은 AWS 계정 내 서로 다른 리전의 VPC를 연결하는 방법입니다.

## 목차

- [사전 조건](#사전-조건)
- [구성도](#구성도)
- [웹 콘솔 방법](#웹-콘솔-방법)
- [CLI 방법](#cli-방법)
- [통신 확인](#통신-확인)
- [체크리스트](#체크리스트)
- [주의사항](#주의사항)
- [기존 라우팅 테이블에 Peering 경로 추가](#기존-라우팅-테이블에-peering-경로-추가)

## 사전 조건

| 항목             | 조건                                    |
|-----------------|----------------------------------------|
| VPC CIDR        | 양쪽 VPC의 CIDR이 겹치지 않아야 함       |
| 리전            | 양쪽 리전 모두 VPC Peering 지원 리전      |
| 계정            | 같은 계정 또는 다른 계정 모두 가능        |

## 구성도

```
+---------------------------+                        +---------------------------+
| us-east-1 (버지니아)       |                        | ap-northeast-2 (서울)      |
|                           |    VPC Peering (pcx-)   |                           |
|  VPC: 10.0.0.0/16        | <=====================> |  VPC: 10.1.0.0/16         |
|  +---------------------+ |                        |  +---------------------+  |
|  | Subnet: 10.0.1.0/24 | |                        |  | Subnet: 10.1.1.0/24 |  |
|  | EC2: 10.0.1.10      | |                        |  | EC2: 10.1.1.10      |  |
|  +---------------------+ |                        |  +---------------------+  |
+---------------------------+                        +---------------------------+

라우팅:
  버지니아 RTB: 10.1.0.0/16 -> pcx-xxxxxxxxx
  서울 RTB:     10.0.0.0/16 -> pcx-xxxxxxxxx
```

## 웹 콘솔 방법

### Step 1: Peering 연결 생성 (요청 측 리전)

1. AWS 콘솔 → 버지니아 리전 선택
2. VPC → Peering connections → Create peering connection
3. 설정 입력:

| 항목                          | 값                        |
|------------------------------|--------------------------|
| Name tag                     | `virginia-to-seoul`      |
| VPC ID (Requester)           | 버지니아 VPC 선택          |
| Account                      | My account               |
| Region                       | Another Region → `ap-northeast-2` |
| VPC ID (Accepter)            | 서울 VPC ID 직접 입력      |

4. Create peering connection 클릭

### Step 2: Peering 수락 (수락 측 리전)

1. AWS 콘솔 → 서울 리전으로 전환
2. VPC → Peering connections
3. 상태가 `Pending acceptance`인 연결 선택
4. Actions → Accept request → Accept

### Step 3: 라우팅 테이블 추가 (양쪽 모두)

버지니아 측:

1. VPC → Route tables → 버지니아 VPC의 라우팅 테이블 선택
2. Routes 탭 → Edit routes → Add route

| Destination      | Target                |
|-----------------|-----------------------|
| `10.1.0.0/16`  | Peering Connection 선택 |

3. Save changes

서울 측:

1. 서울 리전으로 전환
2. VPC → Route tables → 서울 VPC의 라우팅 테이블 선택
3. Routes 탭 → Edit routes → Add route

| Destination      | Target                |
|-----------------|-----------------------|
| `10.0.0.0/16`  | Peering Connection 선택 |

4. Save changes

### Step 3-1: 기존 라우팅 테이블에 Peering 경로만 추가

이미 라우팅 테이블이 존재하는 경우, 기존 경로를 건드리지 않고 Peering 경로만 추가한다.

1. VPC → Route tables → 대상 라우팅 테이블 선택
2. Routes 탭에서 상대 VPC CIDR로 향하는 경로가 있는지 확인
3. 경로가 없으면: Edit routes → Add route

| Destination      | Target                |
|-----------------|-----------------------|
| `상대 VPC CIDR` | Peering Connection 선택 |

4. 경로가 이미 있으면 (다른 Target으로 설정된 경우): 해당 경로의 Target을 Peering Connection으로 변경
5. Save changes

⚠️ 서브넷별로 라우팅 테이블이 다를 수 있다. Peering 통신이 필요한 서브넷의 라우팅 테이블에만 추가한다.

확인 방법:
1. VPC → Subnets → 대상 서브넷 선택
2. Route table 탭에서 연결된 라우팅 테이블 확인
3. 해당 라우팅 테이블에 Peering 경로가 있는지 확인

### Step 4: 보안 그룹 수정 (양쪽 모두)

1. EC2 → Security Groups → 대상 보안 그룹 선택
2. Inbound rules → Edit inbound rules → Add rule

| Type         | Source          | 설명              |
|-------------|-----------------|------------------|
| All traffic | `상대 VPC CIDR` | VPC Peering 허용  |

3. Save rules

### Step 5: DNS 해석 활성화 (선택)

1. VPC → Peering connections → 해당 Peering 선택
2. Actions → Edit DNS settings
3. 양쪽 모두 `Allow DNS resolution` 체크
4. Save

## CLI 방법

### Step 1: Peering 연결 생성

```bash
aws ec2 create-vpc-peering-connection \
  --vpc-id <버지니아-vpc-id> \
  --peer-vpc-id <서울-vpc-id> \
  --peer-region ap-northeast-2 \
  --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=virginia-to-seoul}]' \
  --region us-east-1
```

출력에서 `VpcPeeringConnectionId` (pcx-xxxxxxxxx) 를 기록합니다.

### Step 2: Peering 수락

```bash
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --region ap-northeast-2
```

### Step 3: 라우팅 테이블 추가

```bash
# 버지니아 -> 서울 방향
aws ec2 create-route \
  --route-table-id <버지니아-rtb-id> \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --region us-east-1

# 서울 -> 버지니아 방향
aws ec2 create-route \
  --route-table-id <서울-rtb-id> \
  --destination-cidr-block 10.0.0.0/16 \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --region ap-northeast-2
```

### Step 4: 보안 그룹 수정

```bash
# 버지니아 측 (서울 CIDR 허용)
aws ec2 authorize-security-group-ingress \
  --group-id <버지니아-sg-id> \
  --protocol -1 \
  --cidr 10.1.0.0/16 \
  --region us-east-1

# 서울 측 (버지니아 CIDR 허용)
aws ec2 authorize-security-group-ingress \
  --group-id <서울-sg-id> \
  --protocol -1 \
  --cidr 10.0.0.0/16 \
  --region ap-northeast-2
```

### Step 5: DNS 해석 활성화 (선택)

```bash
# 버지니아 측
aws ec2 modify-vpc-peering-connection-options \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --requester-peering-connection-options AllowDnsResolutionFromRemoteVpc=true \
  --region us-east-1

# 서울 측
aws ec2 modify-vpc-peering-connection-options \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --accepter-peering-connection-options AllowDnsResolutionFromRemoteVpc=true \
  --region ap-northeast-2
```

## 통신 확인

```bash
# Peering 상태 확인
aws ec2 describe-vpc-peering-connections \
  --filters "Name=status-code,Values=active" \
  --query "VpcPeeringConnections[].{ID:VpcPeeringConnectionId,Status:Status.Code,Requester:RequesterVpcInfo.{VpcId:VpcId,Region:Region,CIDR:CidrBlock},Accepter:AccepterVpcInfo.{VpcId:VpcId,Region:Region,CIDR:CidrBlock}}" \
  --region us-east-1

# 라우팅 확인
aws ec2 describe-route-tables \
  --route-table-ids <rtb-id> \
  --query "RouteTables[].Routes[?VpcPeeringConnectionId!=null]" \
  --region us-east-1

# 통신 테스트 (버지니아 EC2에서)
ping 10.1.1.10
traceroute 10.1.1.10
```

## 체크리스트

| 항목                        | 버지니아 | 서울 | 확인 |
|----------------------------|---------|------|------|
| CIDR 겹침 없음              | ✅      | ✅   |      |
| Peering 상태 active         | ✅      | ✅   |      |
| 라우팅 테이블 경로 추가       | ✅      | ✅   |      |
| 보안 그룹 인바운드 허용       | ✅      | ✅   |      |
| NACL 인바운드/아웃바운드 허용  | ✅      | ✅   |      |
| DNS 해석 활성화 (필요 시)     | ✅      | ✅   |      |
| ping/traceroute 통신 확인    | ✅      | ✅   |      |

## 주의사항

| 항목                  | 내용                                                    |
|----------------------|--------------------------------------------------------|
| 전이적 라우팅 불가     | A-B, B-C Peering이 있어도 A-C 직접 통신 불가              |
| CIDR 겹침 불가        | 겹치면 Peering 생성 자체가 실패                           |
| 비용                  | Peering 자체는 무료, 리전 간 데이터 전송 비용 발생          |
| 대역폭               | 제한 없음 (인스턴스 네트워크 성능에 의존)                   |
| 보안 그룹 참조        | Inter-Region Peering에서는 상대 보안 그룹 ID 참조 불가     |
| IPv6                 | Inter-Region Peering에서 IPv6 지원                      |


## 기존 라우팅 테이블에 Peering 경로 추가

이미 라우팅 테이블이 존재하는 환경에서 Peering 경로만 추가하는 방법이다.
VPC Peering을 생성/수락해도 라우트 엔트리는 자동으로 추가되지 않는다.

### 현재 라우팅 테이블 확인

```bash
# 대상 VPC의 라우팅 테이블과 기존 경로 확인
aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=<vpc-id>" \
  --query "RouteTables[].{RTB:RouteTableId,Routes:Routes[].{Dest:DestinationCidrBlock,Target:GatewayId||VpcPeeringConnectionId||NatGatewayId}}" \
  --region us-east-1 \
  --output table
```

### Peering 경로가 이미 있는지 확인

```bash
# 상대 CIDR로 향하는 경로가 있는지 확인
aws ec2 describe-route-tables \
  --route-table-ids <rtb-id> \
  --query "RouteTables[].Routes[?DestinationCidrBlock=='<상대-vpc-cidr>']" \
  --region us-east-1
```

결과가 비어 있으면 (`[]`) 경로 추가가 필요하다.

### 경로 추가 (create-route)

```bash
# 기존 라우팅 테이블에 Peering 경로만 추가
aws ec2 create-route \
  --route-table-id <rtb-id> \
  --destination-cidr-block <상대-vpc-cidr> \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --region us-east-1
```

⚠️ 동일 destination이 이미 존재하면 `RouteAlreadyExists` 에러가 발생한다. 이 경우 `replace-route`를 사용한다.

### 기존 경로 변경 (replace-route)

```bash
# 동일 destination의 target만 Peering으로 변경
aws ec2 replace-route \
  --route-table-id <rtb-id> \
  --destination-cidr-block <상대-vpc-cidr> \
  --vpc-peering-connection-id <pcx-xxxxxxxxx> \
  --region us-east-1
```

### 서브넷별 라우팅 테이블이 다른 경우

Peering 통신이 필요한 서브넷의 라우팅 테이블에만 추가하면 된다.

```bash
# VPC 내 모든 서브넷과 연결된 라우팅 테이블 확인
aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=<vpc-id>" \
  --query "RouteTables[].{RTB:RouteTableId,Subnets:Associations[].SubnetId}" \
  --region us-east-1 \
  --output table

# 필요한 라우팅 테이블에만 경로 추가
for rtb in rtb-aaa rtb-bbb; do
  aws ec2 create-route \
    --route-table-id $rtb \
    --destination-cidr-block <상대-vpc-cidr> \
    --vpc-peering-connection-id <pcx-xxxxxxxxx> \
    --region us-east-1
done
```

### 추가 후 확인

```bash
aws ec2 describe-route-tables \
  --route-table-ids <rtb-id> \
  --query "RouteTables[].Routes[?VpcPeeringConnectionId!=null].{Dest:DestinationCidrBlock,Peering:VpcPeeringConnectionId,Status:State}" \
  --region us-east-1 \
  --output table
```
---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-16

© 2026 siasia86. Licensed under CC BY 4.0.
