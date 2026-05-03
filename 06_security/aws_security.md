# AWS 보안

## 목차

| 섹션 |
|------|
| [1. IAM 최소 권한](#1-iam-최소-권한) / [2. Security Group](#2-security-group) / [3. WAF](#3-waf) |
| [4. GuardDuty](#4-guardduty) / [5. CloudTrail](#5-cloudtrail) / [6. 보안 점검 체크리스트](#6-보안-점검-체크리스트) |

---

## 1. IAM 최소 권한

### 원칙

- 역할(Role) 기반 — 사용자에게 직접 정책 부여 금지.
- 필요한 리소스/액션만 허용 — `*` 와일드카드 최소화.
- 임시 자격증명 우선 — 장기 Access Key 발급 지양.

```json
// 나쁜 예 — 과도한 권한
{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
}

// 좋은 예 — 최소 권한
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::my-bucket/app/*"
}
```

```bash
# IAM Access Analyzer — 미사용 권한 탐지
aws accessanalyzer create-analyzer \
    --analyzer-name "account-analyzer" \
    --type ACCOUNT

# 마지막 사용 기록 확인 (미사용 권한 정리)
aws iam generate-service-last-accessed-details --arn arn:aws:iam::123456789012:role/MyRole
aws iam get-service-last-accessed-details --job-id <job-id>

# Access Key 마지막 사용 확인
aws iam list-access-keys --user-name Secureuser123
aws iam get-access-key-last-used --access-key-id AKIAIOSFODNN7EXAMPLE
```

### IAM 모범 사례

```json
// MFA 강제 정책 (MFA 없으면 모든 작업 거부)
{
    "Effect": "Deny",
    "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "sts:GetSessionToken"
    ],
    "Resource": "*",
    "Condition": {
        "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Security Group

상태 기반(Stateful) 방화벽. Inbound 허용 시 응답 트래픽 자동 허용.

```bash
# Security Group 생성
aws ec2 create-security-group \
    --group-name "web-sg" \
    --description "Web server security group" \
    --vpc-id vpc-12345678

# Inbound 규칙 추가 (HTTPS만 허용)
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# SSH는 특정 IP만 허용
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 22 \
    --cidr 192.0.2.0/24

# 규칙 확인
aws ec2 describe-security-groups --group-ids sg-12345678
```

### 계층별 Security Group 구조

```
Internet
    │
    v
[ALB SG]  — 80, 443 from 0.0.0.0/0
    │
    v
[App SG]  — 8080 from ALB SG only
    │
    v
[DB SG]   — 3306 from App SG only
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. WAF

L7 웹 애플리케이션 방화벽. SQL Injection, XSS, 봇 차단.

```bash
# Web ACL 생성
aws wafv2 create-web-acl \
    --name "prod-web-acl" \
    --scope REGIONAL \
    --default-action Allow={} \
    --rules file://waf-rules.json \
    --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=prod-web-acl \
    --region ap-northeast-2
```

```json
// waf-rules.json — AWS 관리형 규칙 사용
[
    {
        "Name": "AWSManagedRulesCommonRuleSet",
        "Priority": 1,
        "OverrideAction": {"None": {}},
        "Statement": {
            "ManagedRuleGroupStatement": {
                "VendorName": "AWS",
                "Name": "AWSManagedRulesCommonRuleSet"
            }
        },
        "VisibilityConfig": {
            "SampledRequestsEnabled": true,
            "CloudWatchMetricsEnabled": true,
            "MetricName": "CommonRuleSet"
        }
    }
]
```

```bash
# ALB에 Web ACL 연결
aws wafv2 associate-web-acl \
    --web-acl-arn arn:aws:wafv2:ap-northeast-2:123456789012:regional/webacl/prod-web-acl/xxx \
    --resource-arn arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:loadbalancer/app/my-alb/xxx
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. GuardDuty

머신러닝 기반 위협 탐지. VPC Flow Logs, CloudTrail, DNS 로그 분석.

```bash
# 활성화
aws guardduty create-detector --enable --region ap-northeast-2

# Detector ID 확인
aws guardduty list-detectors --region ap-northeast-2

# 탐지 결과 조회 (HIGH 이상)
aws guardduty list-findings \
    --detector-id <detector-id> \
    --finding-criteria '{"Criterion":{"severity":{"Gte":7}}}' \
    --region ap-northeast-2

# 결과 상세 조회
aws guardduty get-findings \
    --detector-id <detector-id> \
    --finding-ids <finding-id> \
    --region ap-northeast-2
```

### 주요 탐지 유형

| 유형                              | 설명                                    |
|-----------------------------------|-----------------------------------------|
| `UnauthorizedAccess:EC2/SSHBruteForce` | SSH brute-force 시도              |
| `Recon:EC2/PortProbeUnprotectedPort`   | 포트 스캔 탐지                    |
| `CryptoCurrency:EC2/BitcoinTool`       | 암호화폐 채굴 탐지                |
| `Trojan:EC2/BlackholeTraffic`          | C&C 서버 통신 탐지                |
| `UnauthorizedAccess:IAMUser/ConsoleLogin` | 비정상 콘솔 로그인             |

[⬆ 목차로 돌아가기](#목차)

---

## 5. CloudTrail

AWS API 호출 감사 로그. 누가, 언제, 무엇을 했는지 추적.

```bash
# Trail 생성 (전 리전)
aws cloudtrail create-trail \
    --name "org-trail" \
    --s3-bucket-name my-bucket \
    --is-multi-region-trail \
    --enable-log-file-validation

# 로깅 시작
aws cloudtrail start-logging --name "org-trail"

# 최근 이벤트 조회
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket \
    --start-time 2026-05-01 \
    --max-results 10

# 특정 사용자 활동 조회
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=Username,AttributeValue=Secureuser123
```

```bash
# CloudWatch Logs 연동 — 루트 계정 사용 알람
aws cloudwatch put-metric-alarm \
    --alarm-name "RootAccountUsage" \
    --metric-name "RootAccountUsage" \
    --namespace "CloudTrailMetrics" \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:security-alerts
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안 점검 체크리스트

```bash
# AWS Security Hub 활성화 (통합 보안 점검)
aws securityhub enable-security-hub --region ap-northeast-2

# 점검 결과 조회 (CRITICAL)
aws securityhub get-findings \
    --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}]}' \
    --region ap-northeast-2
```

| 항목                              | 확인 방법                                                    |
|-----------------------------------|--------------------------------------------------------------|
| 루트 계정 MFA 활성화              | IAM 콘솔 → 보안 자격증명                                    |
| 미사용 Access Key 삭제            | `aws iam list-access-keys`                                   |
| 공개 S3 버킷 없음                 | `aws s3api list-buckets` + Public Access Block 확인          |
| Security Group 0.0.0.0/0 SSH 없음 | `aws ec2 describe-security-groups`                           |
| CloudTrail 활성화                 | `aws cloudtrail get-trail-status --name org-trail`           |
| GuardDuty 활성화                  | `aws guardduty list-detectors`                               |
| Config 규칙 준수 여부             | `aws configservice describe-compliance-by-config-rule`       |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- AWS Security Best Practices: [docs.aws.amazon.com/security](https://docs.aws.amazon.com/security/) — ★★★☆☆
- AWS Well-Architected Security Pillar: [docs.aws.amazon.com/wellarchitected](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) — ★★★☆☆
- CIS AWS Foundations Benchmark: [cisecurity.org](https://www.cisecurity.org/benchmark/amazon_web_services) — ★★★☆☆
- AWS IAM Best Practices: [docs.aws.amazon.com/IAM/latest/UserGuide/best-practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — ★★★☆☆
- Amazon GuardDuty Finding Types: [docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html) — ★★★☆☆
- AWS CloudTrail User Guide: [docs.aws.amazon.com/awscloudtrail/latest/userguide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-03

**마지막 업데이트**: 2026-05-03

© 2026 siasia86. Licensed under CC BY 4.0.
