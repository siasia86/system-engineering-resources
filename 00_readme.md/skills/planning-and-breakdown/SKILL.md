---
name: planning-and-breakdown
description: Breaks infrastructure work into ordered tasks. Use when you have requirements and need to decompose into implementable steps. Use when an infra change feels too large, when you need to estimate blast radius, or when changes span multiple environments.
---

# Planning and Breakdown

## Overview

인프라 작업을 작고 검증 가능한 단위로 분해하는 워크플로우입니다.
각 태스크는 명확한 완료 조건과 검증 방법을 가지며, 의존성 순서대로 정렬됩니다.

## When to Use

- 요구사항이 있고 구현 단위로 분해가 필요할 때
- 작업이 너무 크거나 모호하여 시작하기 어려울 때
- 여러 환경(dev/stg/prd)에 걸친 변경
- 블래스트 레디어스 파악이 필요할 때
- 작업 순서가 명확하지 않을 때

**적용하지 않는 경우:** 단일 리소스 변경, 범위가 명확한 단순 작업.

## The Planning Process

### Step 1: Read-Only Mode

코드를 작성하기 전에 읽기 전용으로 조사합니다.

- 현재 인프라 상태 확인 (terraform state, AWS 콘솔)
- 기존 모듈/패턴 파악
- 의존성 관계 매핑
- 리스크와 미지수 식별

### Step 2: Dependency Graph

의존성을 매핑합니다.

```
VPC / Network
    │
    ├── Subnet (Public / Private)
    │       │
    │       ├── Security Group
    │       │       │
    │       │       ├── EC2 / ECS
    │       │       │       │
    │       │       │       └── ALB Target Group
    │       │       │               │
    │       │       │               └── ALB Listener
    │       │       │
    │       │       └── RDS
    │       │
    │       └── NAT Gateway
    │
    └── Route Table
```

### Step 3: Vertical Slicing

수평(계층별)이 아닌 수직(기능별)으로 분할합니다.

```
나쁨 (수평):
  Task 1: 모든 SG 생성
  Task 2: 모든 EC2 생성
  Task 3: 모든 ALB 설정

좋음 (수직):
  Task 1: Web tier 전체 (SG + EC2 + ALB + health check)
  Task 2: App tier 전체 (SG + ECS + Service Discovery)
  Task 3: DB tier 전체 (SG + RDS + 백업 설정)
```

### Step 4: Write Tasks

각 태스크 구조:

```markdown
## Task [N]: [제목]

**설명:** 이 태스크가 완료하는 것.

**완료 조건:**
- [ ] 리소스 생성/변경 완료
- [ ] terraform plan → 예상 변경만 표시
- [ ] 서비스 정상 동작 확인

**검증:**
- [ ] terraform apply 성공
- [ ] health check 통과
- [ ] 모니터링 정상

**의존성:** Task N (또는 없음)

**영향 범위:**
- 리소스: aws_instance, aws_security_group
- 환경: dev
- 블래스트 레디어스: 해당 서비스만

**롤백:** terraform apply 이전 커밋 코드

**예상 소요:** [10분 / 30분 / 1시간]
```

### Step 5: Order and Checkpoint

정렬 기준:

1. 의존성 순서 (기반부터)
2. 각 태스크 후 시스템 정상 상태 유지
3. 2~3개 태스크마다 체크포인트
4. 고위험 태스크를 앞에 배치 (fail fast)

```markdown
## Checkpoint: Task 1-3 완료 후
- [ ] terraform plan → "No changes"
- [ ] 모든 서비스 health check 통과
- [ ] 모니터링 알림 없음
- [ ] 다음 단계 진행 전 확인
```

## Task Sizing

| 크기 | 리소스 수 | 범위                    | 예시                        |
|------|-----------|-------------------------|-----------------------------|
| S    | 1-3       | 단일 서비스             | SG 규칙 추가                |
| M    | 4-8       | 한 tier                 | Web tier 전체 구성          |
| L    | 9-15      | 여러 tier               | VPC + 서브넷 + NAT 전체     |
| XL   | 15+       | **분할 필요**           | —                           |

L 이상은 반드시 더 작은 단위로 분할합니다.

## Plan Template

```markdown
# 인프라 변경 계획: [제목]

## 개요
[무엇을 왜 변경하는지 1문단]

## 현재 상태
[현재 인프라 구성 요약]

## 목표 상태
[변경 후 인프라 구성]

## 블래스트 레디어스
- 영향 서비스: [목록]
- 영향 환경: [dev/stg/prd]
- 다운타임 예상: [있음/없음, 시간]

## Task List

### Phase 1: 기반
- [ ] Task 1: ...
- [ ] Task 2: ...

### Checkpoint: 기반 완료
- [ ] terraform plan → No changes
- [ ] 서비스 정상

### Phase 2: 서비스
- [ ] Task 3: ...
- [ ] Task 4: ...

### Checkpoint: 전체 완료
- [ ] 모든 검증 통과

## 리스크 및 대응

| 리스크              | 영향 | 대응                          |
|---------------------|------|-------------------------------|
| RDS 다운타임        | High | 유지보수 윈도우 예약          |
| SG 변경 시 접근 차단 | Med  | 기존 규칙 유지 후 추가        |

## 롤백 계획
[단계별 롤백 방법]

## 미결 사항
[확인 필요한 항목]
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "간단한 변경이라 계획 불필요합니다" | 간단해도 블래스트 레디어스 파악은 필요합니다. |
| "머릿속에 다 있습니다" | 문서화된 계획은 롤백 시 필수입니다. |
| "계획은 오버헤드입니다" | 10분 계획이 수 시간 장애 복구를 방지합니다. |
| "한 번에 다 하면 빠릅니다" | 장애 시 원인 파악이 불가능합니다. |

## Red Flags

- 계획 없이 terraform apply 실행
- 완료 조건 없는 태스크
- 검증 단계 누락
- 모든 태스크가 XL 크기
- 체크포인트 없이 연속 적용
- 롤백 계획 미수립

## Verification

구현 시작 전 확인:

- [ ] 모든 태스크에 완료 조건 있음
- [ ] 모든 태스크에 검증 방법 있음
- [ ] 의존성 순서 정렬 완료
- [ ] 블래스트 레디어스 파악 완료
- [ ] 체크포인트 배치 완료
- [ ] 롤백 계획 수립 완료

구현 시 `skill://incremental-change` 워크플로우를 적용합니다.
