---
name: doubt-driven-infra
description: Subjects non-trivial infrastructure decisions to adversarial review before they stand. Use when making production changes, security-sensitive modifications, irreversible operations, or working in unfamiliar infrastructure code.
---

# Doubt-Driven Infra

## Overview

확신은 정확성이 아닙니다. 인프라 변경은 비가역적이고 블래스트 레디어스가 크므로, 비자명한 결정에 대해 fresh-context adversarial review를 수행합니다.

이 스킬은 `/review`가 아닙니다. `/review`는 완성된 산출물에 대한 판정입니다. 이 스킬은 **진행 중인 결정**에 대한 교차 검증입니다.

## When to Use

결정이 **비자명(non-trivial)** 한 경우:

- 프로덕션 환경 변경 (terraform apply to prd)
- IAM 정책 수정 (권한 확대/축소)
- Security Group 규칙 변경
- 네트워크 구조 변경 (VPC, Subnet, Route Table)
- 데이터베이스 변경 (엔진 업그레이드, 파라미터 변경)
- 비가역적 작업 (리소스 삭제, 데이터 마이그레이션)
- 익숙하지 않은 인프라 코드 수정

**적용하지 않는 경우:**

- 태그 변경, 설명 수정
- dev 환경 단일 리소스 변경
- terraform fmt, 변수명 리네이밍
- 사용자가 명시적으로 속도 우선을 요청한 경우

## The Process

```
Doubt cycle:
- [ ] Step 1: CLAIM — 변경 내용 + 왜 안전한지 주장 작성
- [ ] Step 2: EXTRACT — 변경 코드/plan 결과만 분리 (추론 과정 제거)
- [ ] Step 3: DOUBT — adversarial 관점에서 반박 시도
- [ ] Step 4: RECONCILE — 발견 사항 분류 및 대응
- [ ] Step 5: STOP — 종료 조건 충족 확인
```

### Step 1: CLAIM

변경 내용과 안전성 주장을 명시합니다.

```
CLAIM:
- 변경: prd-sg-web에 443 포트 인바운드 규칙 추가
- 안전성 주장: ALB에서만 접근하므로 source를 ALB SG로 제한
- 블래스트 레디어스: web tier만 영향
- 롤백: 규칙 제거 (terraform apply 이전 코드)
```

### Step 2: EXTRACT

terraform plan 결과 또는 변경 코드만 분리합니다. 자신의 추론 과정은 제거합니다.

```
ARTIFACT:
  resource "aws_security_group_rule" "web_https" {
    type              = "ingress"
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    source_security_group_id = aws_security_group.alb.id
    security_group_id = aws_security_group.web.id
  }

CONTRACT:
  - 443 포트만 허용
  - source는 ALB SG만
  - web SG에만 적용
```

### Step 3: DOUBT

adversarial 관점에서 반박합니다.

질문 목록:

| 검증 항목   | 질문                                        |
|-------------|---------------------------------------------|
| 범위 초과   | 이 규칙이 의도하지 않은 접근을 허용하는가?  |
| 의존성      | ALB SG가 이미 과도하게 열려 있지 않은가?    |
| 순서        | 이 변경 전에 필요한 선행 조건이 있는가?     |
| 롤백        | 롤백 시 서비스 중단이 발생하는가?           |
| State       | terraform state와 실제 리소스가 일치하는가? |
| 암묵적 가정 | "ALB에서만 접근"이라는 가정이 검증되었는가? |

### Step 4: RECONCILE

발견 사항을 분류합니다.

| 분류        | 조치                      |
|-------------|---------------------------|
| 실제 위험   | 변경 중단, 수정 후 재시도 |
| 검증 필요   | 명령어로 확인 후 진행     |
| 사소한 우려 | 기록 후 진행              |

### Step 5: STOP

종료 조건:

- 모든 "실제 위험" 해소
- 모든 "검증 필요" 항목 확인 완료
- 3회 사이클 초과 시 사용자에게 판단 위임
- 사용자가 명시적으로 진행 승인

## Verification Commands

DOUBT 단계에서 사용하는 검증 명령어:

```bash
# SG 현재 상태 확인
aws ec2 describe-security-groups --group-ids <sg-id> \
  --query 'SecurityGroups[].IpPermissions'

# IAM 정책 시뮬레이션
aws iam simulate-principal-policy --policy-source-arn <role-arn> \
  --action-names <action> --resource-arns <resource>

# Terraform state vs 실제 비교
terraform plan -detailed-exitcode

# 네트워크 도달성 확인
aws ec2 describe-network-interfaces --filters Name=group-id,Values=<sg-id>
```

## Common Rationalizations

| Rationalization                    | Reality                                                                  |
|------------------------------------|--------------------------------------------------------------------------|
| "plan 확인했으니 안전합니다"       | plan은 논리적 정합성만 보여줍니다. 보안/의존성은 별도 검증이 필요합니다. |
| "dev에서 테스트했습니다"           | prd는 네트워크, 권한, 데이터가 다릅니다. 환경 차이를 검증합니다.         |
| "작은 변경이라 doubt 불필요합니다" | SG 규칙 1줄이 전체 네트워크를 노출할 수 있습니다.                        |
| "시간이 없습니다"                  | 5분 doubt가 수 시간 장애 복구를 방지합니다.                              |
| "이전에도 이렇게 했습니다"         | 이전 결정이 올바른지도 검증 대상입니다.                                  |

## Red Flags

- terraform apply 전에 DOUBT 사이클 미수행
- "안전하다"는 주장에 검증 명령어 결과가 없음
- 블래스트 레디어스 미파악 상태에서 진행
- 암묵적 가정을 명시하지 않음
- DOUBT 단계에서 발견된 위험을 무시하고 진행
- 롤백 계획 없이 비가역적 변경 수행

## Verification

DOUBT 사이클 완료 후:

- [ ] 모든 CLAIM에 대해 DOUBT 수행
- [ ] "실제 위험" 항목 0건
- [ ] "검증 필요" 항목 모두 명령어로 확인
- [ ] 블래스트 레디어스 명시
- [ ] 롤백 계획 수립
- [ ] 사용자 승인 획득 (prd 변경 시)
