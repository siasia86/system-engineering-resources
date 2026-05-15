# Terraform

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. HCL 문법](#4-hcl-문법) / [5. 주요 명령어](#5-주요-명령어) / [6. 상태 관리](#6-상태-관리) |
| [7. 모듈](#7-모듈) / [8. 워크스페이스](#8-워크스페이스) / [9. AWS 실전 예시](#9-aws-실전-예시) |
| [10. 보안](#10-보안) / [11. Tips](#11-tips) |

---

## 1. 개요

Terraform은 HashiCorp의 오픈소스 IaC(Infrastructure as Code) 도구. HCL(HashiCorp Configuration Language)로 인프라를 선언적으로 정의하고, 클라우드/온프레미스 리소스를 코드로 관리합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                    Terraform Workflow                        │
│                                                              │
│  Write (HCL) -> terraform init -> plan -> apply -> destroy   │
│                                                              │
│  .tf files -> State File -> Real Infrastructure              │
└──────────────────────────────────────────────────────────────┘
```

- **선언형**: 원하는 최종 상태를 정의하면 Terraform이 현재 상태와 비교하여 변경 사항을 적용합니다.
- **멱등성**: 동일한 코드를 여러 번 실행해도 결과가 동일합니다.
- **멀티 클라우드**: AWS, GCP, Azure, Kubernetes 등 900개 이상의 Provider를 지원합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Terraform Core                           │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐   │
│  │  .tf files   │   │  State File  │   │  Plan/Apply    │   │
│  │  (HCL code)  │   │  (tfstate)   │   │  Engine        │   │
│  └──────────────┘   └──────────────┘   └────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                                        │
         v                                        v
┌─────────────────┐                   ┌───────────────────────┐
│   Providers     │                   │   Real Infrastructure │
│  ┌───────────┐  │                   │  ┌──────┐  ┌───────┐  │
│  │   AWS     │  │ ─── API calls ──> │  │  EC2 │  │  RDS  │  │
│  │   GCP     │  │                   │  └──────┘  └───────┘  │
│  │   Azure   │  │                   │  ┌──────┐  ┌───────┐  │
│  └───────────┘  │                   │  │  VPC │  │  S3   │  │
└─────────────────┘                   │  └──────┘  └───────┘  │
                                      └───────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념           | 설명                                                        |
|----------------|-------------------------------------------------------------|
| Provider       | 클라우드/서비스 API 연동 플러그인 (aws, google, azurerm 등) |
| Resource       | 관리할 인프라 객체 (EC2, S3, VPC 등)                        |
| Data Source    | 기존 리소스 정보 조회 (읽기 전용)                           |
| Variable       | 입력 변수 (재사용성, 환경별 분리)                           |
| Output         | 리소스 속성 출력 (다른 모듈/스택에서 참조)                  |
| Local          | 모듈 내부 임시 값 (표현식 재사용)                           |
| Module         | 재사용 가능한 리소스 묶음                                   |
| State          | 실제 인프라와 코드의 매핑 정보 (terraform.tfstate)          |
| Workspace      | 동일 코드로 여러 환경(dev/stg/prod) 관리                    |
| Backend        | State 파일 저장 위치 (로컬, S3, Terraform Cloud 등)         |

[⬆ 목차로 돌아가기](#목차)

---

## 4. HCL 문법

### 기본 구조

```hcl
# Provider 설정
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote Backend (S3)
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Resource

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  tags = {
    Name        = "${var.env}-web-server"
    Environment = var.env
  }

  lifecycle {
    create_before_destroy = true   # 교체 시 새 리소스 먼저 생성
    prevent_destroy       = false  # true 시 destroy 차단
    ignore_changes        = [tags] # 특정 속성 변경 무시
  }
}
```

### Variable

```hcl
# variables.tf
variable "env" {
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.env)
    error_message = "env must be dev, stg, or prod."
  }
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "allowed_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/8"]
}

variable "tags" {
  type    = map(string)
  default = {}
}
```

```hcl
# terraform.tfvars
env           = "prod"
instance_type = "t3.small"
allowed_cidrs = ["10.0.0.0/8", "172.16.0.0/12"]
```

### Output

```hcl
# outputs.tf
output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_instance.web.public_ip
  sensitive   = false
}

output "db_password" {
  value     = random_password.db.result
  sensitive = true   # terraform output 시 마스킹
}
```

### Data Source

```hcl
# 최신 Amazon Linux 2023 AMI 조회
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# 기존 VPC 조회
data "aws_vpc" "main" {
  tags = {
    Name = "main-vpc"
  }
}
```

### Local & 표현식

```hcl
locals {
  common_tags = merge(var.tags, {
    Environment = var.env
    ManagedBy   = "terraform"
  })

  name_prefix = "${var.project}-${var.env}"
}

# 조건식
resource "aws_instance" "web" {
  instance_type = var.env == "prod" ? "t3.medium" : "t3.micro"
}

# for_each
resource "aws_subnet" "private" {
  for_each = toset(["ap-northeast-1a", "ap-northeast-1c"])

  vpc_id            = aws_vpc.main.id
  availability_zone = each.key
}

# count
resource "aws_instance" "worker" {
  count         = var.worker_count
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  tags = {
    Name = "${local.name_prefix}-worker-${count.index + 1}"
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령어

### 기본 워크플로우

```bash
# 초기화 (Provider 다운로드, Backend 설정)
terraform init

# 변경 계획 확인 (dry-run)
terraform plan

# 변경 계획을 파일로 저장
terraform plan -out=tfplan

# 적용
terraform apply
terraform apply tfplan          # 저장된 plan 적용
terraform apply -auto-approve   # 확인 없이 적용 (CI/CD용)

# 특정 리소스만 적용
terraform apply -target=aws_instance.web

# 삭제
terraform destroy
terraform destroy -target=aws_instance.web
```

### 상태 조회

```bash
# 관리 중인 리소스 목록
terraform state list

# 특정 리소스 상태 상세 조회
terraform state show aws_instance.web

# Output 값 조회
terraform output
terraform output public_ip
```

### 상태 조작

```bash
# 기존 리소스를 State에 import (코드 없이 생성된 리소스)
terraform import aws_instance.web i-0123456789abcdef0

# State에서 리소스 제거 (실제 리소스는 삭제 안 함)
terraform state rm aws_instance.web

# 리소스 이름 변경
terraform state mv aws_instance.web aws_instance.app

# State 새로고침 (v1.5+ deprecated → terraform apply -refresh-only 권장)
terraform refresh
```

### 기타

```bash
# 코드 포맷팅
terraform fmt
terraform fmt -recursive

# 유효성 검사
terraform validate

# Provider 버전 업데이트
terraform init -upgrade

# 특정 리소스 재생성
terraform apply -replace=aws_instance.web
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 상태 관리

### Remote Backend (S3 + DynamoDB)

팀 협업 시 State를 S3에 저장하고 DynamoDB로 잠금(Lock)을 관리합니다.

```hcl
# S3 버킷 및 DynamoDB 테이블 생성 (bootstrap)
resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state"
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### State 잠금

```bash
# 잠금 강제 해제 (비정상 종료 후)
terraform force-unlock <LOCK_ID>
```

### State 분리 전략

| 전략              | 설명                                      | 적합한 경우              |
|-------------------|-------------------------------------------|--------------------------|
| 환경별 디렉토리   | `envs/dev/`, `envs/prod/` 분리            | 소규모 팀, 단순 구조     |
| 워크스페이스      | `terraform workspace new prod`            | 동일 코드, 환경만 다를 때 |
| 컴포넌트별 분리   | `network/`, `compute/`, `database/` 분리  | 대규모, 변경 영향 최소화 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 모듈

### 모듈 구조

```
modules/
└── ec2_instance/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

### 모듈 작성 (modules/ec2_instance/main.tf)

```hcl
resource "aws_instance" "this" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids

  tags = merge(var.tags, {
    Name = var.name
  })
}
```

### 모듈 호출

```hcl
module "web_server" {
  source = "./modules/ec2_instance"

  name               = "web-server"
  ami_id             = data.aws_ami.amazon_linux.id
  instance_type      = "t3.small"
  subnet_id          = aws_subnet.public.id
  security_group_ids = [aws_security_group.web.id]
  tags               = local.common_tags
}

# 모듈 Output 참조
output "web_server_ip" {
  value = module.web_server.public_ip
}
```

### 공개 레지스트리 모듈 사용

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name = "main-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-northeast-1a", "ap-northeast-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 워크스페이스

동일한 코드로 여러 환경을 관리합니다.

```bash
# 워크스페이스 목록
terraform workspace list

# 새 워크스페이스 생성
terraform workspace new dev
terraform workspace new prod

# 전환
terraform workspace select prod

# 현재 워크스페이스 확인
terraform workspace show
```

```hcl
# 워크스페이스별 설정 분기
locals {
  env_config = {
    dev = {
      instance_type = "t3.micro"
      min_size      = 1
    }
    prod = {
      instance_type = "t3.medium"
      min_size      = 2
    }
  }

  config = local.env_config[terraform.workspace]
}

resource "aws_instance" "web" {
  instance_type = local.config.instance_type
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. AWS 실전 예시

### VPC + EC2 + RDS 기본 구성

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "${local.name_prefix}-vpc" }
}

# Public Subnet
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet("10.0.0.0/16", 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "${local.name_prefix}-public-${count.index + 1}" }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.name_prefix}-igw" }
}

# Security Group
resource "aws_security_group" "web" {
  name   = "${local.name_prefix}-web-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS
resource "aws_db_instance" "main" {
  identifier        = "${local.name_prefix}-db"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "appdb"
  username = "admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  skip_final_snapshot = var.env != "prod"
  deletion_protection = var.env == "prod"

  tags = local.common_tags
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 보안

### 시크릿 관리

```hcl
# 방법 1: 환경변수 (권장)
# export TF_VAR_db_password="SecurePassword123"

# 방법 2: AWS Secrets Manager에서 조회
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/db/password"
}

locals {
  db_password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}

# 방법 3: sensitive 변수 (tfstate에 암호화 저장)
variable "db_password" {
  type      = string
  sensitive = true
}
```

### .gitignore

```gitignore
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars
crash.log
override.tf
# .terraform.lock.hcl  # 팀 협업 시 커밋 권장 (제외하지 않음)
```

### IAM 최소 권한

```hcl
resource "aws_iam_policy" "terraform_deploy" {
  name = "terraform-deploy-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ec2:*", "rds:*", "s3:*"]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = "ap-northeast-1"
          }
        }
      }
    ]
  })
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. Tips

### 디렉토리 구조 (환경별 분리)

```
infra/
├── modules/
│   ├── vpc/
│   ├── ec2/
│   └── rds/
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
└── bootstrap/
    └── main.tf
```

### 자주 쓰는 패턴

```bash
# plan 결과를 파일로 저장 후 apply (CI/CD 표준 패턴)
terraform plan -out=tfplan -var-file=prod.tfvars
terraform apply tfplan

# 변수 오버라이드
terraform plan -var="env=prod" -var="instance_type=t3.medium"

# JSON 형식 출력 (파싱용)
terraform output -json
terraform show -json
```

⚠️ `terraform destroy`는 되돌릴 수 없습니다. 프로덕션 환경에서는 `prevent_destroy = true` 설정을 권장합니다.

⚠️ State 파일에는 민감 정보가 포함될 수 있습니다. S3 Backend 사용 시 버킷 암호화와 접근 제어를 반드시 설정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Terraform Documentation: [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/docs) — ★★★☆☆
- Terraform AWS Provider: [registry.terraform.io/providers/hashicorp/aws](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) — ★★★☆☆
- Terraform AWS Modules: [registry.terraform.io/namespaces/terraform-aws-modules](https://registry.terraform.io/namespaces/terraform-aws-modules) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-10

**마지막 업데이트**: 2026-05-10

© 2026 siasia86. Licensed under CC BY 4.0.
