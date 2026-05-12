# AWS Network Firewall 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 구성 요소](#3-구성-요소) |
| [4. 기본 설정](#4-기본-설정) / [5. 규칙 작성](#5-규칙-작성) / [6. 로깅 및 모니터링](#6-로깅-및-모니터링) |
| [7. 고급 설정](#7-고급-설정) / [8. 트러블슈팅](#8-트러블슈팅) |

## 1. 개요

AWS Network Firewall은 VPC 수준의 관리형 네트워크 방화벽 서비스입니다.
Stateful/Stateless 패킷 필터링, IPS(침입 방지), 도메인 필터링을 지원합니다.

| 항목          | 내용                                              |
|---------------|---------------------------------------------------|
| 유형          | 관리형 네트워크 방화벽 (L3~L7)                    |
| 배포 위치     | VPC 내 전용 서브넷 (Firewall Subnet)              |
| 처리 방식     | Stateless → Stateful 순서로 평가                  |
| 기본 정책     | 명시적 PASS 없으면 DROP (Default Deny)            |
| 비활성화      | ❌ 불가 — 삭제 또는 규칙 수정으로 우회            |

### 주요 기능

| 기능                  | 설명                                              |
|-----------------------|---------------------------------------------------|
| Stateless 필터링      | 5-tuple 기반 패킷 단위 필터링 (빠름)              |
| Stateful 필터링       | 연결 상태 추적, Suricata 규칙 지원                |
| IPS                   | AWS 관리형 위협 시그니처 자동 업데이트            |
| 도메인 필터링         | FQDN/도메인 기반 아웃바운드 제어                  |
| TLS 검사              | SSL/TLS 복호화 후 검사 (별도 설정 필요)           |

[⬆ 목차로 돌아가기](#목차)

## 2. 아키텍처

### 트래픽 흐름

```
Internet Gateway
       |
       v
  ┌─────────────────────────────────────────┐
  │              Public Subnet              │
  │  (Route: 0.0.0.0/0 → Firewall Endpoint)│
  └─────────────────────────────────────────┘
       |
       v
  ┌─────────────────────────────────────────┐
  │           Firewall Subnet               │
  │         (Network Firewall)              │
  │   Stateless Rules → Stateful Rules      │
  └─────────────────────────────────────────┘
       |
       v
  ┌─────────────────────────────────────────┐
  │           Private Subnet                │
  │  (Route: 0.0.0.0/0 → Firewall Endpoint)│
  │           EC2 Instances                 │
  └─────────────────────────────────────────┘
```

### 서브넷 구성 요구사항

| 서브넷 유형      | 용도                              | 권장 크기  |
|------------------|-----------------------------------|------------|
| Firewall Subnet  | Firewall Endpoint 전용            | /28 이상   |
| Public Subnet    | IGW → Firewall 경유 라우팅        | 기존 서브넷 |
| Private Subnet   | 보호 대상 리소스                  | 기존 서브넷 |

⚠️ Firewall Subnet은 AZ당 1개 필요합니다. 멀티 AZ 구성 시 AZ별로 생성합니다.

### Route Table 설정

```
# IGW Route Table (Ingress Routing)
Destination        Target
10.0.1.0/24   →   vpce-xxxxxxxx (Firewall Endpoint)  ← Private Subnet 트래픽

# Public Subnet Route Table
Destination        Target
0.0.0.0/0     →   vpce-xxxxxxxx (Firewall Endpoint)

# Private Subnet Route Table
Destination        Target
0.0.0.0/0     →   vpce-xxxxxxxx (Firewall Endpoint)
```

[⬆ 목차로 돌아가기](#목차)

## 3. 구성 요소

```
Network Firewall
├── Firewall Policy          ← 규칙 그룹 조합
│   ├── Stateless Rule Group (우선순위 순 평가)
│   │   ├── Rule 1: PASS  tcp 443
│   │   └── Rule 2: Forward to Stateful
│   └── Stateful Rule Group
│       ├── Domain List
│       ├── Standard Rules (5-tuple)
│       └── Suricata Rules
└── Firewall (VPC에 연결)
    └── Firewall Endpoint (AZ별 생성)
```

| 구성 요소             | 설명                                              |
|-----------------------|---------------------------------------------------|
| Firewall              | VPC에 연결되는 실제 방화벽 인스턴스               |
| Firewall Policy       | Rule Group 을 조합한 정책                         |
| Stateless Rule Group  | 패킷 단위 필터 (PASS / DROP / Forward to Stateful)|
| Stateful Rule Group   | 연결 추적 기반 필터 (PASS / DROP / ALERT)         |
| Rule Group            | 재사용 가능한 규칙 묶음 (Policy에 연결)           |

[⬆ 목차로 돌아가기](#목차)

## 4. 기본 설정

### 4-1. Firewall Subnet 생성

```bash
# AWS CLI
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxx \
  --cidr-block 10.0.3.0/28 \
  --availability-zone ap-northeast-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=firewall-subnet-2a}]'
```

### 4-2. Rule Group 생성

#### Stateless Rule Group

```bash
aws network-firewall create-rule-group \
  --rule-group-name "stateless-basic" \
  --type STATELESS \
  --capacity 100 \
  --rule-group '{
    "RulesSource": {
      "StatelessRulesAndCustomActions": {
        "StatelessRules": [
          {
            "Priority": 10,
            "RuleDefinition": {
              "MatchAttributes": {
                "Protocols": [6],
                "DestinationPorts": [{"FromPort": 443, "ToPort": 443}]
              },
              "Actions": ["aws:pass"]
            }
          },
          {
            "Priority": 100,
            "RuleDefinition": {
              "MatchAttributes": {},
              "Actions": ["aws:forward_to_sfe"]
            }
          }
        ]
      }
    }
  }'
```

#### Stateful Rule Group (Domain List)

```bash
aws network-firewall create-rule-group \
  --rule-group-name "allow-domains" \
  --type STATEFUL \
  --capacity 100 \
  --rule-group '{
    "RulesSource": {
      "RulesSourceList": {
        "Targets": [".example.com", "api.github.com"],
        "TargetTypes": ["HTTP_HOST", "TLS_SNI"],
        "GeneratedRulesType": "ALLOWLIST"
      }
    }
  }'
```

### 4-3. Firewall Policy 생성

```bash
aws network-firewall create-firewall-policy \
  --firewall-policy-name "main-policy" \
  --firewall-policy '{
    "StatelessDefaultActions": ["aws:forward_to_sfe"],
    "StatelessFragmentDefaultActions": ["aws:drop"],
    "StatelessRuleGroupReferences": [
      {
        "ResourceArn": "arn:aws:network-firewall:ap-northeast-2:123456789012:stateless-rulegroup/stateless-basic",
        "Priority": 10
      }
    ],
    "StatefulRuleGroupReferences": [
      {
        "ResourceArn": "arn:aws:network-firewall:ap-northeast-2:123456789012:stateful-rulegroup/allow-domains"
      }
    ]
  }'
```

### 4-4. Firewall 생성

```bash
aws network-firewall create-firewall \
  --firewall-name "main-firewall" \
  --firewall-policy-arn "arn:aws:network-firewall:ap-northeast-2:123456789012:firewall-policy/main-policy" \
  --vpc-id vpc-xxxxxxxx \
  --subnet-mappings '[{"SubnetId": "subnet-xxxxxxxx"}]'
```

### 4-5. Firewall Endpoint ID 확인 (Route Table 설정용)

```bash
aws network-firewall describe-firewall \
  --firewall-name "main-firewall" \
  --query 'FirewallStatus.SyncStates'
```

[⬆ 목차로 돌아가기](#목차)

## 5. 규칙 작성

### Stateless 규칙 액션

| 액션                    | 설명                              |
|-------------------------|-----------------------------------|
| `aws:pass`              | 허용 (Stateful 검사 생략)         |
| `aws:drop`              | 차단                              |
| `aws:forward_to_sfe`    | Stateful 엔진으로 전달            |

### Stateful 규칙 유형

#### 1. Standard (5-tuple)

```json
{
  "Action": "PASS",
  "Header": {
    "Protocol": "TCP",
    "Source": "192.168.10.0/24",
    "SourcePort": "ANY",
    "Direction": "FORWARD",
    "Destination": "10.102.0.0/16",
    "DestinationPort": "ANY"
  },
  "RuleOptions": [{"Keyword": "sid", "Settings": ["1"]}]
}
```

#### 2. Suricata 규칙

```bash
# PASS: VPN 클라이언트 대역 → 내부망 전체 허용
pass tcp 192.168.10.0/24 any -> 10.102.0.0/16 any (sid:1001; rev:1;)
pass icmp 192.168.10.0/24 any -> 10.102.0.0/16 any (sid:1002; rev:1;)

# DROP: 특정 포트 차단
drop tcp any any -> any 22 (msg:"Block SSH from outside"; sid:2001; rev:1;)

# ALERT: 의심 트래픽 로깅
alert tcp any any -> any 3389 (msg:"RDP access detected"; sid:3001; rev:1;)
```

#### 3. Domain List

```
# ALLOWLIST: 허용 도메인만 통과
Targets: [".amazonaws.com", ".example.com"]
TargetTypes: ["HTTP_HOST", "TLS_SNI"]
GeneratedRulesType: ALLOWLIST

# DENYLIST: 차단 도메인
Targets: ["malware.example.com"]
GeneratedRulesType: DENYLIST
```

### 규칙 평가 순서

```
패킷 수신
    |
    v
Stateless Rules (Priority 낮을수록 먼저)
    |
    ├── aws:pass    → 허용 (종료)
    ├── aws:drop    → 차단 (종료)
    └── aws:forward_to_sfe
            |
            v
    Stateful Rules
            |
            ├── PASS  → 허용
            ├── DROP  → 차단
            └── ALERT → 로깅 후 허용
                    |
                    v
            Default Action (정책 기본값)
```

[⬆ 목차로 돌아가기](#목차)

## 6. 로깅 및 모니터링

### 로그 유형

| 로그 유형  | 내용                              | 대상                        |
|------------|-----------------------------------|-----------------------------|
| ALERT      | Stateful ALERT 규칙 매칭 트래픽   | CloudWatch Logs / S3 / Firehose |
| FLOW       | 모든 허용 트래픽 흐름             | CloudWatch Logs / S3 / Firehose |
| TLS        | TLS 검사 결과                     | CloudWatch Logs / S3 / Firehose |

### 로깅 활성화

```bash
aws network-firewall update-logging-configuration \
  --firewall-name "main-firewall" \
  --logging-configuration '{
    "LogDestinationConfigs": [
      {
        "LogType": "ALERT",
        "LogDestinationType": "CloudWatchLogs",
        "LogDestination": {"logGroup": "/aws/network-firewall/alert"}
      },
      {
        "LogType": "FLOW",
        "LogDestinationType": "CloudWatchLogs",
        "LogDestination": {"logGroup": "/aws/network-firewall/flow"}
      }
    ]
  }'
```

### CloudWatch에서 DROP 트래픽 확인

```bash
# AWS CLI로 로그 조회
aws logs filter-log-events \
  --log-group-name "/aws/network-firewall/alert" \
  --filter-pattern "DROP"
```

```json
// ALERT 로그 예시
{
  "firewall_name": "main-firewall",
  "availability_zone": "ap-northeast-2a",
  "event": {
    "timestamp": "2026-05-12T10:00:00Z",
    "flow_id": 123456789,
    "event_type": "alert",
    "src_ip": "192.168.10.12",
    "src_port": 54321,
    "dest_ip": "10.102.100.245",
    "dest_port": 80,
    "proto": "TCP",
    "alert": {
      "action": "blocked",
      "signature": "Block unauthorized access",
      "signature_id": 2001
    }
  }
}
```

[⬆ 목차로 돌아가기](#목차)

## 7. 고급 설정

### 7-1. AWS 관리형 규칙 그룹 (Managed Rule Groups)

별도 규칙 작성 없이 AWS가 관리하는 위협 시그니처를 사용합니다.

| 규칙 그룹                                      | 설명                        |
|------------------------------------------------|-----------------------------|
| `AWSManagedRulesCommonRuleSet`                 | 일반 위협 차단              |
| `AWSManagedRulesThreatIntelligenceRuleSet`     | 알려진 악성 IP 차단         |
| `AWSManagedRulesBotControlRuleSet`             | 봇 트래픽 차단              |

```bash
# Firewall Policy에 관리형 규칙 추가
aws network-firewall update-firewall-policy \
  --firewall-policy-name "main-policy" \
  --firewall-policy '{
    "StatefulRuleGroupReferences": [
      {
        "ResourceArn": "arn:aws:network-firewall:ap-northeast-2:aws-managed:stateful-rulegroup/ThreatSignaturesMalware"
      }
    ]
  }'
```

### 7-2. TLS 검사 (TLS Inspection)

암호화된 트래픽을 복호화하여 검사합니다.

```bash
# TLS Inspection Configuration 생성
aws network-firewall create-tls-inspection-configuration \
  --tls-inspection-configuration-name "tls-inspect" \
  --tls-inspection-configuration '{
    "ServerCertificateConfigurations": [
      {
        "Scopes": [
          {
            "Sources": [{"AddressDefinition": "0.0.0.0/0"}],
            "Destinations": [{"AddressDefinition": "0.0.0.0/0"}],
            "SourcePorts": [{"FromPort": 0, "ToPort": 65535}],
            "DestinationPorts": [{"FromPort": 443, "ToPort": 443}],
            "Protocols": [6]
          }
        ]
      }
    ]
  }'
```

### 7-3. 멀티 AZ 고가용성 구성

```bash
# AZ별 Firewall Subnet 생성 후 Firewall에 추가
aws network-firewall associate-subnets \
  --firewall-name "main-firewall" \
  --subnet-mappings '[
    {"SubnetId": "subnet-aaa"},
    {"SubnetId": "subnet-bbb"}
  ]'
```

⚠️ AZ별로 Firewall Endpoint가 생성되며, 각 AZ의 Route Table에 해당 AZ의 Endpoint를 지정해야 합니다.

### 7-4. Terraform으로 관리

```hcl
resource "aws_networkfirewall_firewall" "main" {
  name                = "main-firewall"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.main.arn
  vpc_id              = aws_vpc.main.id

  subnet_mapping {
    subnet_id = aws_subnet.firewall.id
  }
}

resource "aws_networkfirewall_firewall_policy" "main" {
  name = "main-policy"

  firewall_policy {
    stateless_default_actions          = ["aws:forward_to_sfe"]
    stateless_fragment_default_actions = ["aws:drop"]

    stateful_rule_group_reference {
      resource_arn = aws_networkfirewall_rule_group.stateful.arn
    }
  }
}

resource "aws_networkfirewall_rule_group" "stateful" {
  capacity = 100
  name     = "stateful-rules"
  type     = "STATEFUL"

  rule_group {
    rules_source {
      rules_string = <<-EOT
        pass tcp 192.168.10.0/24 any -> 10.102.0.0/16 any (sid:1001; rev:1;)
      EOT
    }
  }
}
```

[⬆ 목차로 돌아가기](#목차)

## 8. 트러블슈팅

### No route to host / 연결 안 됨

```bash
# 1. FLOW 로그에서 트래픽 확인
aws logs filter-log-events \
  --log-group-name "/aws/network-firewall/flow" \
  --filter-pattern "{ $.event.src_ip = \"192.168.10.12\" }"

# 2. ALERT 로그에서 DROP 확인
aws logs filter-log-events \
  --log-group-name "/aws/network-firewall/alert" \
  --filter-pattern "blocked"
```

### Route Table 설정 오류

```
증상: 트래픽이 Firewall을 경유하지 않음
원인: Route Table이 Firewall Endpoint가 아닌 IGW/NAT를 직접 가리킴
해결: 각 서브넷 Route Table의 0.0.0.0/0 → Firewall Endpoint(vpce-xxx)로 수정
```

### Firewall Endpoint ID 확인

```bash
aws network-firewall describe-firewall \
  --firewall-name "main-firewall" \
  --query 'FirewallStatus.SyncStates.*.Attachment.EndpointId' \
  --output text
```

### 규칙 즉시 적용 안 됨

```
증상: 규칙 추가 후에도 트래픽 차단/허용 안 됨
원인: Rule Group 업데이트 후 Policy 반영까지 수십 초 소요
해결: 1~2분 대기 후 재테스트
```

### 특정 트래픽만 허용 (Default Deny 환경)

```bash
# Stateful Rule Group에 PASS 규칙 추가
pass tcp 192.168.10.0/24 any -> 10.102.0.0/16 80 (sid:1001; rev:1;)
pass tcp 192.168.10.0/24 any -> 10.102.0.0/16 443 (sid:1002; rev:1;)
pass icmp 192.168.10.0/24 any -> 10.102.0.0/16 any (sid:1003; rev:1;)
```

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- AWS Network Firewall: [docs.aws.amazon.com](https://docs.aws.amazon.com/network-firewall/latest/developerguide/) — ★★★☆☆
- Suricata Rule Language: [suricata.readthedocs.io](https://suricata.readthedocs.io/en/latest/rules/) — ★★★☆☆
- AWS Network Firewall Workshop: [catalog.workshops.aws](https://catalog.workshops.aws/networkfirewall) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-12

**마지막 업데이트**: 2026-05-12

© 2026 siasia86. Licensed under CC BY 4.0.
