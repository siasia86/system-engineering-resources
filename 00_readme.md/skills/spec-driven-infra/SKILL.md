---
name: spec-driven-infra
description: Creates infrastructure specs before applying changes. Use when starting a new infra project, adding significant resources, or when requirements are unclear. Use when the change affects production or spans multiple services.
---

# Spec-Driven Infra

## Overview

인프라 변경 전에 구조화된 스펙을 작성하는 워크플로우입니다.
스펙은 무엇을, 왜, 어떻게 변경하는지의 합의 문서이며, 변경의 블래스트 레디어스와 롤백 계획을 포함합니다.

## When to Use

- 새로운 인프라 구성 (VPC, 클러스터, 서비스)
- 프로덕션 환경 변경
- 여러 서비스에 영향을 주는 변경
- 요구사항이 모호하거나 불완전할 때
- 아키텍처 결정이 필요할 때

**적용하지 않는 경우:** 태그 변경, 단일 파라미터 수정, 명확한 버그 수정.

## Gated Workflow

```
SPECIFY ──→ PLAN ──→ TASKS ──→ IMPLEMENT
   │          │        │          │
   v          v        v          v
 Review     Review   Review    Verify
```

각 단계를 검증 없이 넘어가지 않습니다.

## Phase 1: Specify

### Assumptions 먼저 명시

```
ASSUMPTIONS:
1. VPC CIDR은 10.0.0.0/16 사용 (기존 네트워크와 충돌 없음)
2. Multi-AZ 구성 (ap-northeast-2a, 2c)
3. NAT Gateway는 AZ당 1개
4. Terraform backend는 기존 S3 + DynamoDB 사용
→ 확인 필요한 항목이 있으면 지적해 주세요.
```

### Spec Template

```markdown
# Infra Spec: [제목]

## 목적
[무엇을 왜 구축/변경하는지. 비즈니스 요구사항.]

## 현재 상태
[현재 인프라 구성. 다이어그램 포함 권장.]

## 목표 상태
[변경 후 인프라 구성. 다이어그램 포함.]

## 기술 스택
- IaC: Terraform 1.x / Ansible 2.x
- Provider: AWS (ap-northeast-2)
- 모듈: [사용할 모듈 목록]

## 리소스 목록

| 리소스              | 이름 규칙                    | 수량 |
|---------------------|------------------------------|------|
| VPC                 | prd-vpc-main                 | 1    |
| Subnet (Private)    | prd-subnet-private-{az}      | 2    |
| Security Group      | prd-sg-{service}             | N    |

## 네트워크 설계

| CIDR            | 용도              | AZ   |
|-----------------|-------------------|------|
| 10.0.0.0/16     | VPC               | -    |
| 10.0.1.0/24     | Public Subnet     | 2a   |
| 10.0.2.0/24     | Public Subnet     | 2c   |
| 10.0.11.0/24    | Private Subnet    | 2a   |
| 10.0.12.0/24    | Private Subnet    | 2c   |

## 보안 요구사항
- [ ] 최소 권한 원칙 (IAM)
- [ ] 암호화 (at rest + in transit)
- [ ] 네트워크 격리 (Private Subnet)
- [ ] 감사 로그 (CloudTrail, VPC Flow Logs)

## 모니터링 요구사항
- [ ] CloudWatch Alarm: CPU, Memory, Disk
- [ ] 로그 수집: CloudWatch Logs / 외부 시스템
- [ ] 알림 채널: Slack / Email

## 블래스트 레디어스
- 영향 서비스: [목록]
- 다운타임: [예상 시간]
- 영향 사용자: [범위]

## 비용 추정
- 월간 예상 비용: [AWS Pricing Calculator 또는 infracost 결과]
- 기존 대비 증감: [+/- 금액]
- 비용 최적화: [Reserved/Spot/Savings Plan 적용 여부]

## Boundaries
- Always: IaC로만 변경, plan 확인 후 apply, 롤백 계획 수립
- Ask first: 프로덕션 apply, 데이터 마이그레이션, SG 삭제
- Never: 콘솔 수동 변경, 시크릿 하드코딩, 롤백 계획 없이 적용

## 성공 기준
- [ ] terraform plan → 예상 리소스만 생성
- [ ] 서비스 health check 통과
- [ ] 모니터링 알림 정상 동작
- [ ] 보안 감사 통과

## 미결 사항
- [확인 필요한 항목]
```

## Ansible Spec Template

Terraform/AWS가 아닌 Ansible role/playbook 설계 시 사용합니다.

```markdown
# Ansible Spec: [제목]

## 목적
[무엇을 왜 자동화하는지. 수동 작업 대비 이점.]

## 대상 환경

| 항목          | 내용                                      |
|---------------|-------------------------------------------|
| 대상 OS       | Ubuntu 22/24, Rocky 9, AmazonLinux 2023   |
| 연결 방식     | SSH / docker / winrm                      |
| 권한 상승     | become: true (sudo/runas)                 |
| Ansible 버전  | 2.15+                                     |

## Inventory 구조

    [group_name]
    host1 ansible_host=10.x.x.x

    [group_name:vars]
    ansible_user=ansible
    ansible_ssh_private_key_file=~/.ssh/id_ed25519

## Role / Playbook 구조

    playbooks/
    ├── site.yml              # 전체 진입점
    ├── vars/
    │   ├── common.yml        # 평문 변수
    │   └── secrets.yml       # vault 암호화
    └── roles/
        └── role_name/
            ├── tasks/main.yml
            ├── handlers/main.yml
            ├── defaults/main.yml
            └── templates/

## 멱등성 보장 계획

| Task | 멱등성 방법 |
|------|-------------|
| 패키지 설치 | `state: present` |
| 파일 생성 | `creates:` 또는 `stat` 선행 체크 |
| 서비스 시작 | `state: started` |
| 설정 변경 | `lineinfile` / `template` |

## OS별 분기 계획

| 작업 | Debian | RedHat |
|------|--------|--------|
| 패키지 | `apt` | `dnf`/`yum` |
| 서비스명 | `ssh` | `sshd` |
| 그룹 | `sudo` | `wheel` |

## 시크릿 관리
- vault 암호화 대상: [목록]
- vault password 관리 방법: [파일/환경변수/CI Secret]

## 테스트 계획
- [ ] `--syntax-check` 통과
- [ ] `--check` dry-run 통과
- [ ] Molecule 테스트 (대상 OS별)
- [ ] 실제 환경 적용 후 재실행 → changed=0 확인

## 롤백 계획
- 설정 파일: `backup: true` 옵션으로 자동 백업
- 패키지: `state: absent`로 제거
- 전체 롤백: [방법]

## 성공 기준
- [ ] 전체 OS `failed=0`
- [ ] 재실행 시 `changed=0` (멱등성)
- [ ] `--check` 모드 호환
- [ ] vault 시크릿 평문 노출 없음
```

## Phase 2: Plan

스펙 확정 후 기술 구현 계획을 작성합니다.

- 모듈 구조 결정
- 의존성 그래프 작성
- 환경별 적용 순서 결정
- 리스크 식별 및 대응 방안

## Phase 3: Tasks

`skill://planning-and-breakdown` 스킬을 사용하여 태스크로 분해합니다.

## Phase 4: Implement

`skill://incremental-change` 스킬을 사용하여 점진적으로 적용합니다.

## Spec as Living Document

- 결정 변경 시 스펙 먼저 업데이트
- 범위 변경 시 스펙에 반영
- 스펙을 버전 관리에 포함
- PR에서 스펙 섹션 참조

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "간단한 변경이라 스펙 불필요합니다" | 간단해도 블래스트 레디어스와 롤백 계획은 필요합니다. |
| "코드 먼저 작성하고 문서화하겠습니다" | 그건 문서화이지 스펙이 아닙니다. 스펙의 가치는 사전 합의입니다. |
| "요구사항이 바뀔 텐데 스펙을 왜 씁니까" | 바뀌면 스펙을 업데이트합니다. 없는 것보다 낫습니다. |
| "시간이 없습니다" | 15분 스펙이 수 시간 장애 복구를 방지합니다. |

## Red Flags

- 스펙 없이 terraform 코드 작성 시작
- 블래스트 레디어스 미파악
- 롤백 계획 없음
- 보안 요구사항 누락
- 모니터링 계획 없음
- "당연히 알겠지" 가정으로 진행

## Verification

구현 시작 전 확인:

- [ ] 스펙 6개 핵심 영역 작성 완료
- [ ] 블래스트 레디어스 파악
- [ ] 롤백 계획 수립
- [ ] 보안 요구사항 명시
- [ ] 성공 기준 구체적이고 검증 가능
- [ ] Boundaries 정의 완료
- [ ] 스펙 파일 저장소에 커밋
