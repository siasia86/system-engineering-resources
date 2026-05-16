---
name: shipping-checklist
description: Pre-deployment checklist for infrastructure changes. Use when deploying to production, launching new services, or performing staged rollouts.
---

# Shipping Checklist

## Overview

인프라 변경을 프로덕션에 배포하기 전 수행하는 체크리스트입니다.
배포는 코드 작성보다 위험하므로, 구조화된 검증 없이 진행하지 않습니다.

## When to Use

- terraform apply to prd
- 새 서비스 런칭
- 인프라 마이그레이션 완료 단계
- feature flag 활성화
- DNS 변경, 인증서 교체

**적용하지 않는 경우:** dev/stg 환경 변경, 태그/설명 수정.

## Pre-Deploy Checklist

### 1. 코드 준비

- [ ] 모든 변경 사항 커밋 완료
- [ ] code-review 스킬 적용 완료
- [ ] terraform plan → 예상 변경만 표시
- [ ] 불필요한 리소스 삭제/변경 없음 확인

### 2. 보안 검증

- [ ] IAM 최소 권한 확인
- [ ] SG 규칙 검토 (0.0.0.0/0 없음)
- [ ] 시크릿 하드코딩 없음
- [ ] 암호화 설정 확인 (at rest + in transit)

### 3. 롤백 계획

- [ ] 롤백 방법 문서화
- [ ] 롤백 소요 시간 추정
- [ ] 롤백 트리거 조건 정의
- [ ] state 백업 완료

```bash
# Terraform state 백업
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate
```

### 4. 모니터링 준비

- [ ] CloudWatch Alarm 설정 확인
- [ ] 로그 수집 경로 확인
- [ ] 알림 채널 동작 확인 (Slack/Email)
- [ ] 대시보드 준비

### 5. 배포 실행

- [ ] 유지보수 윈도우 확인 (필요 시)
- [ ] 관련 팀 사전 공지 (필요 시)
- [ ] 단계별 적용 (`skill://incremental-change`)
- [ ] 각 단계 후 health check

### 6. Post-Deploy 검증

```bash
# 서비스 health check
curl -f http://endpoint/health

# 리소스 상태
aws ec2 describe-instance-status --instance-ids <id>
aws ecs describe-services --cluster <cluster> --services <svc>

# Terraform 정합성
terraform plan  # "No changes"

# 모니터링 정상
# CloudWatch 대시보드 확인, 알림 없음
```

## Staged Rollout

대규모 변경 시 단계별 배포:

```
Phase 1: Canary (1개 인스턴스/AZ)
    → 30분 관찰 → 이상 없으면 진행

Phase 2: 50% 배포
    → 1시간 관찰 → 이상 없으면 진행

Phase 3: 100% 배포
    → 모니터링 안정화 확인
```

## Rollback Decision

| 조건 | 조치 |
|------|------|
| 배포 후 5분 이내 장애 | 즉시 롤백 |
| 메트릭 이상 (에러율 증가) | 즉시 롤백 |
| 부분 장애 | feature flag OFF → 조사 |
| 데이터 마이그레이션 포함 | forward fix (롤백 불가) |

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "dev에서 됐으니 바로 prd 적용합니다" | 환경 차이가 있습니다. 체크리스트를 수행합니다. |
| "급해서 롤백 계획은 나중에 세웁니다" | 롤백 계획 없이 배포하면 장애 시 복구 시간이 배로 늘어납니다. |
| "모니터링은 배포 후 설정합니다" | 배포 시점에 모니터링이 없으면 장애를 감지할 수 없습니다. |

## Red Flags

- 체크리스트 미수행 상태에서 prd apply
- 롤백 계획 없음
- state 백업 없음
- 모니터링/알림 미설정
- 단계별 검증 없이 전체 한 번에 배포

## Verification

배포 완료 후:

- [ ] 서비스 정상 동작 (health check 통과)
- [ ] terraform plan → "No changes"
- [ ] 모니터링 정상 (알림 없음)
- [ ] 롤백 계획 유효성 확인
- [ ] 배포 완료 기록 (커밋, 시간, 담당자)
