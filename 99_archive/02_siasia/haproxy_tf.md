# HAProxy 3중화 인프라 (Terraform)

AWS에서 HAProxy를 이용한 고가용성 로드밸런서 인프라를 구축하는 Terraform 프로젝트입니다.

## 개요

- **목적**: NLB + Auto Scaling Group을 통한 HAProxy 3중화 구성
- **구조**: Client → NLB → Auto Scaling Group (HAProxy) → Game Server
- **지원 리전**: ap-northeast-1 (도쿄), ap-northeast-2 (서울)
- **고가용성**: Multi-AZ 배포, Auto Scaling (Min: 3, Max: 10)

## 아키텍처

```
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   Client    │───>│     NLB     │───>│ Auto Scaling    │───>│ Game Server │
│             │    │             │    │ Group (HAProxy) │    │             │
└─────────────┘    └─────────────┘    └─────────────────┘    └─────────────┘
                                              │
                                 ┌────────────┼────────────┐
                                 v            v            v
                            ┌────────┐  ┌────────┐  ┌────────┐
                            │HAProxy │  │HAProxy │  │HAProxy │
                            │   01   │  │   02   │  │   03   │
                            │(AZ-1a) │  │(AZ-1c) │  │(AZ-1d) │
                            └────────┘  └────────┘  └────────┘
```

## 디렉토리 구조

```
haproxy-project/
├── ap-northeast-1/              # 도쿄 리전
│   ├── network/                 # VPC, 서브넷, IGW
│   ├── sg/                      # 보안 그룹
│   ├── nlb/                     # Network Load Balancer
│   └── ec2/                     # Auto Scaling Group, EC2
├── ap-northeast-2/              # 서울 리전
│   ├── network/
│   ├── sg/
│   ├── nlb/
│   └── ec2/
└── modules/                     # 공통 모듈
    ├── vpc/                     # VPC 모듈
    ├── sg/                      # Security Group 모듈
    ├── nlb/                     # NLB 모듈
    └── ec2/                     # EC2 Auto Scaling 모듈
```

## 배포 순서

### 필수 순서 (의존성 있음)

각 리전별로 다음 순서대로 배포해야 합니다:

```bash
# 1. Network (VPC, 서브넷, IGW)
cd haproxy-project/ap-northeast-1/network
terraform init
terraform plan
terraform apply

# 2. Security Group (Network 의존)
cd ../sg
terraform init
terraform plan
terraform apply

# 3. NLB (Network 의존)
cd ../nlb
terraform init
terraform plan
terraform apply

# 4. EC2 Auto Scaling (모든 리소스 의존)
cd ../ec2
terraform init
terraform plan
terraform apply
```

## 주요 설정

### Network 설정
- **VPC CIDR**: 
  - ap-northeast-1: `10.210.0.0/16`
  - ap-northeast-2: `10.220.0.0/16`
- **서브넷**: 각 리전당 3개 AZ에 `/24` 서브넷
- **가용 영역**: 
  - ap-northeast-1: 1a, 1c, 1d
  - ap-northeast-2: 2a, 2b, 2c

### Auto Scaling 설정
- **최소**: 3대 (기본 3중화)
- **최대**: 10대 (DDoS 공격 시 확장)
- **원하는 용량**: 3대
- **인스턴스 타입**: t3.medium
- **AMI**: Amazon Linux 2023 (자동 선택)

### 보안 그룹 규칙
- **게임 포트**: 7777, 16101-16102, 16201, 16301 (TCP/UDP)
- **웹 포트**: 80, 443 (TCP)
- **헬스체크**: 8080 (VPC 내부만)
- **HAProxy 통계**: 8404 (VPC 내부만)
- **SSH**: 22 (특정 IP 대역만)

## Auto Scaling 정책

### Scale-Out (확장)
- **조건**: CPU 사용률 60% 이상 (2분간 지속)
- **동작**: +2대 추가
- **쿨다운**: 5분

### Scale-In (축소)
- **조건**: CPU 사용률 30% 이하 (2분간 지속)
- **동작**: -1대 제거
- **쿨다운**: 5분

## IAM 권한

### Auto Scaling에 필요한 권한
HAProxy 인스턴스가 Auto Scaling과 Load Balancer와 정상적으로 연동되기 위해 다음 IAM 권한이 설정되어 있습니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateTags",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus",
        "cloudwatch:PutMetricData",
        "autoscaling:SetInstanceHealth",
        "autoscaling:TerminateInstanceInAutoScalingGroup",
        "elasticloadbalancing:DescribeTargetHealth",
        "elasticloadbalancing:RegisterTargets",
        "elasticloadbalancing:DeregisterTargets"
      ],
      "Resource": "*"
    }
  ]
}
```

### 권한별 용도
- **ec2:CreateTags**: 인스턴스 이름 태그 설정
- **ec2:DescribeInstances**: 인스턴스 정보 조회
- **ec2:DescribeInstanceStatus**: 인스턴스 상태 확인
- **cloudwatch:PutMetricData**: CloudWatch 메트릭 전송
- **autoscaling:SetInstanceHealth**: 헬스체크 상태 보고
- **autoscaling:TerminateInstanceInAutoScalingGroup**: 안전한 인스턴스 종료
- **elasticloadbalancing:*****: NLB 타겟 등록/해제 및 헬스체크

## HAProxy 설정

### 주요 기능
- **로드밸런싱**: Round Robin
- **헬스체크**: `/health` 엔드포인트
- **통계 페이지**: `/stats` (포트 8404)
- **프로토콜**: TCP 모드 (게임 서버용)
- **Proxy Protocol**: 지원 (실제 클라이언트 IP 전달)

### 인스턴스 네이밍
- **패턴**: `01_sjyun_amazonlinux2023_haproxy_XX`
- **AZ별 번호**: 
  - ap-northeast-1a → 01
  - ap-northeast-1c → 02
  - ap-northeast-1d → 03

## 멀티 리전 배포

### 새 리전 추가 방법

1. **디렉토리 복사**
```bash
cp -r haproxy-project/ap-northeast-1 haproxy-project/us-east-1
```

2. **설정 수정**
- `provider.tf`: 리전 변경
- `haproxy-network.tf`: AZ 및 CIDR 변경
- `scripts/haproxy-userdata.sh`: AZ 매핑 및 리전 변경

3. **순차 배포**
```bash
cd haproxy-project/us-east-1
# network → sg → nlb → ec2 순서로 배포
```

## 사용 예시

### 기본 배포
```bash
# 도쿄 리전 배포
cd haproxy-project/ap-northeast-1/network
terraform apply -auto-approve

cd ../sg
terraform apply -auto-approve

cd ../nlb
terraform apply -auto-approve

cd ../ec2
terraform apply -auto-approve
```

### 특정 리소스만 수정
```bash
# 보안 그룹만 수정
cd haproxy-project/ap-northeast-1/sg
terraform plan
terraform apply
```

### 인프라 제거
```bash
# 역순으로 제거 (ec2 → nlb → sg → network)
cd haproxy-project/ap-northeast-1/ec2
terraform destroy -auto-approve

cd ../nlb
terraform destroy -auto-approve

cd ../sg
terraform destroy -auto-approve

cd ../network
terraform destroy -auto-approve
```

## 커스터마이징

### 인스턴스 타입 변경
```terraform
# haproxy-project/ap-northeast-1/ec2/haproxy-ec2.tf
instance_type = "t3.large"  # 기본: t3.medium
```

### Auto Scaling 정책 변경
```terraform
# haproxy-project/ap-northeast-1/ec2/haproxy-ec2.tf
min_size         = 5   # 기본: 3
max_size         = 20  # 기본: 10
desired_capacity = 5   # 기본: 3
```

### 게임 서버 IP 변경
```bash
# haproxy-project/ap-northeast-1/ec2/scripts/haproxy-userdata.sh
server gameserver1 YOUR_GAME_SERVER_IP:7777 check
server gameserver2 YOUR_GAME_SERVER_IP:7777 check backup
```

## 🟡 주의사항

1. **배포 순서**: 반드시 network → sg → nlb → ec2 순서로 배포
2. **리전별 CIDR**: 다른 리전 배포 시 CIDR 충돌 방지
3. **State 파일**: 각 디렉토리별로 독립적인 terraform state 관리
4. **의존성**: Remote State를 통한 모듈 간 의존성 관리
5. **비용**: Auto Scaling으로 인한 예상치 못한 비용 발생 가능

## 문제 해결

### 일반적인 문제

1. **Remote State 오류**
```bash
Error: Unable to find remote state
```
**해결**: 의존성 순서 확인 (network 먼저 배포)

2. **AZ 오류**
```bash
Error: availability zone not available
```
**해결**: 리전별 사용 가능한 AZ 확인 후 수정

3. **CIDR 충돌**
```bash
Error: CIDR block conflicts
```
**해결**: 다른 CIDR 대역 사용 (예: 10.220.0.0/16)

## 참고 자료

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [HAProxy Documentation](https://www.haproxy.org/download/2.4/doc/configuration.txt)
- [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/)
- [AWS Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/)

---

**작성일**: 2026-01-13  
**버전**: 1.0  
**관리자**: sjyun
