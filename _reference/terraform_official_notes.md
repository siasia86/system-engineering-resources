---
name: terraform-official-notes
description: Terraform 공식 문서 기반 권장사항, 버전별 변경사항 정리. 문서 작성/검토 시 참조.
tags:
  - terraform
  - iac
  - aws
  - infrastructure
last_checked: 2026-11-09
sources:
  - https://developer.hashicorp.com/terraform/language
  - https://developer.hashicorp.com/terraform/language/backend/s3
  - https://developer.hashicorp.com/terraform/language/expressions/version-constraints
  - https://developer.hashicorp.com/terraform/language/style
  - https://github.com/hashicorp/terraform/releases
  - https://developer.hashicorp.com/terraform/language/manage-sensitive-data
---

# Terraform 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-11-05)

| 컴포넌트     | 최신 버전 | 비고          |
|--------------|-----------|---------------|
| Terraform    | v1.17.1   | stable        |
| AWS Provider | v6.72.0   | hashicorp/aws |

## 2. required_version 권장 문법

```hcl
terraform {
  required_version = ">= 1.9.0"  # 최소 버전 지정
  # 또는
  required_version = "~> 1.9"    # 1.9.x 허용, 2.0 차단 (pessimistic constraint)
}
```

### version constraint 연산자

| 연산자 | 예시       | 의미                               |
|--------|------------|------------------------------------|
| `=`    | `= 1.9.0`  | 정확히 해당 버전만                 |
| `!=`   | `!= 1.8.0` | 해당 버전 제외                     |
| `>=`   | `>= 1.9.0` | 이상                               |
| `~>`   | `~> 1.9`   | 1.9.x 허용, 2.0 차단 (pessimistic) |
| `~>`   | `~> 1.9.0` | 1.9.0~1.9.x 허용, 1.10 차단        |

## 3. S3 Backend 권장 설정

```hcl
terraform {
  backend "s3" {
    bucket       = "my-terraform-state"
    key          = "env/prd/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true  # v1.10+: S3 네이티브 락 (DynamoDB 불필요)
    # dynamodb_table = "terraform-lock"  # use_lockfile 이전 방식
  }
}
```

🟡 `use_lockfile` (v1.10+): S3 네이티브 조건부 쓰기로 락 구현. DynamoDB 테이블 불필요.
🟡 `encrypt = true` 필수 — 상태 파일에 민감 정보 포함 가능.

## 4. 버전별 주요 변경사항

| 버전 | 주요 변경                                                   |
|------|-------------------------------------------------------------|
| 1.15 | `variable`/`output`에 `deprecated` 속성 추가                |
| 1.14 | `terraform query` 명령어 추가                               |
| 1.11 | Write-only attributes 추가, S3 `use_lockfile` 정식(GA)      |
| 1.10 | Ephemeral resources·values 추가, S3 `use_lockfile` 추가     |
| 1.9  | Input variable validation이 다른 객체 참조 가능             |
| 1.8  | Provider-defined functions 지원                             |
| 1.7  | `removed` 블록 추가 (state에서 리소스 제거, 실제 삭제 없음) |
| 1.6  | `terraform test` 정식(GA)                                   |
| 1.5  | `import` 블록 추가 (HCL로 import 선언), `check` 블록 추가   |

## 5. 코드 스타일 권장사항 (공식)

- `terraform fmt` — 커밋 전 반드시 실행
- `terraform validate` — 커밋 전 반드시 실행
- 리소스 이름: 명사·밑줄 구분, 이름에 리소스 유형을 넣지 않음 (예: `resource "aws_instance" "web_api"`)
- 변수명: snake_case
- 모듈 입력 변수에 `description`, `type` 필수
- `count` vs `for_each`: 리소스 목록은 `for_each` 권장 (삭제 시 인덱스 재정렬 방지)

## 6. 보안 권장사항

- 상태 파일 암호화: S3 backend `encrypt = true`
- 민감 변수: `sensitive = true` — CLI 출력에서만 가림. state·plan 파일에는 평문으로 저장되고 `terraform output -raw`·`-json`은 값을 그대로 출력(확인일 2026-11-05, manage-sensitive-data)
- ephemeral 변수·출력·블록(1.10+)과 write-only 인수(1.11+)는 state·plan 파일에 저장되지 않음. 루트 모듈 output에는 `ephemeral`을 쓸 수 없음
- IAM 최소 권한: provider에 필요한 권한만 부여
- 시크릿 하드코딩 금지 — `var.*`, AWS Secrets Manager, SSM Parameter Store 사용
- `.terraform/`, `*.tfstate`, `*.tfvars` — `.gitignore`에 반드시 추가

## 7. 알려진 주의사항

- `count` 사용 시 중간 요소 삭제 → 이후 인덱스 전체 재생성 위험 → `for_each` 권장
- `depends_on` 남용 시 불필요한 재생성 발생
- provider 버전 `~>` 고정 권장 (`version = "~> 6.0"`, AWS Provider 현행 주 버전 6)
- 상태 파일 직접 편집 금지 — `terraform state` 명령어 사용
- `terraform destroy` — 프로덕션 실행 전 반드시 plan 확인
