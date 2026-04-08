# LSP (Language Server Protocol) 가이드

## 1. 개념과 정의

### LSP란?

Microsoft가 2016년 VSCode를 위해 설계한 오픈 표준 프로토콜.  
에디터(클라이언트)와 언어 분석 도구(서버)를 분리하여, 어떤 에디터든 동일한 방식으로 코드 인텔리전스를 제공한다.

### LSP 이전 vs 이후

```
# LSP 이전: N x M 문제
VSCode + Python 플러그인 (VSCode 전용)
Vim    + Python 플러그인 (Vim 전용)
Emacs  + Python 플러그인 (Emacs 전용)
→ 에디터 수 × 언어 수만큼 플러그인 필요

# LSP 이후: N + M 구조
VSCode ─┐
Vim    ─┼─→ pyright (Python Language Server)
Emacs  ─┘
→ 언어 서버 하나로 모든 에디터에서 동작
```

### 동작 구조

```
+----------------+   JSON-RPC over stdio   +------------------+
│  에디터/클라이언트 │ ──────────────────────→ │  Language Server  │
│  (VSCode, Vim) │ ←────────────────────── │  (pyright, gopls) │
+----------------+                         +------------------+
```

클라이언트와 서버는 JSON-RPC 프로토콜로 통신하며, 서버는 언어별로 독립 프로세스로 실행된다.

### 제공 기능

| 기능 | 설명 |
|------|------|
| 자동완성 | 변수, 함수, 속성 목록 제안 |
| 정의로 이동 | 함수/클래스 선언부로 이동 |
| 참조 찾기 | 심볼이 사용된 모든 위치 표시 |
| 오류 진단 | 타입 오류, 미정의 변수 실시간 표시 |
| 타입 정보 | 커서 위치의 타입/문서 표시 |
| 심볼 이름 변경 | 코드베이스 전체 일괄 변경 |

---

## 2. 인프라 관련 주요 LSP

### 2-1. Terraform (`terraform-ls`)

HashiCorp 공식 Language Server.

**설치**

```bash
# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform-ls

# 또는 직접 바이너리 다운로드
# https://github.com/hashicorp/terraform-ls/releases
```

**VSCode 사용**

```
확장 설치: HashiCorp Terraform (hashicorp.terraform)
→ terraform-ls 자동 연동
```

**주요 기능**

```hcl
# 리소스 속성 자동완성
resource "aws_instance" "web" {
  ami           = "ami-xxxxxxxx"
  instance_type = "t3.micro"   # ← t3. 입력 시 타입 목록 자동완성
}

# 변수 참조 추적
variable "region" {}
provider "aws" {
  region = var.region   # ← var. 입력 시 정의된 변수 목록 표시
}
```

**팁**

- `terraform init` 후 LSP가 provider 스키마를 읽어 정확한 자동완성 제공
- 모듈 내부 변수도 추적 가능

---

### 2-2. Bash (`bash-language-server`)

Shell 스크립트 작성 시 문법 오류 및 자동완성 제공.

**설치**

```bash
npm install -g bash-language-server

# Node.js 없을 경우
sudo apt install nodejs npm
```

**주요 기능**

```bash
#!/bin/bash

# 미정의 변수 경고
echo $UNDEFINED_VAR   # ← 경고 표시

# 함수 정의 추적
deploy_app() {
  echo "deploying..."
}
deploy_app   # ← 정의로 이동 가능
```

**팁**

- `shellcheck` 연동 시 더 강력한 린팅 가능
  ```bash
  sudo apt install shellcheck
  ```
- `set -euo pipefail` 누락 등 베스트 프랙티스 위반도 감지

---

### 2-3. YAML (`yaml-language-server`)

Kubernetes, Docker Compose, GitHub Actions, Ansible 등 YAML 파일 지원.

**설치**

```bash
npm install -g yaml-language-server
```

**스키마 연동 (핵심 기능)**

YAML 파일 상단에 주석으로 스키마를 지정하면 해당 스키마 기반 자동완성/검증 제공.

```yaml
# Kubernetes Deployment
# yaml-language-server: $schema=https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/v1.29.0/deployment.json
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3   # ← 타입 검증, 자동완성 동작
```

```yaml
# GitHub Actions
# yaml-language-server: $schema=https://json.schemastore.org/github-workflow.json
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest   # ← 유효한 값 목록 자동완성
```

**VSCode 설정 (settings.json)**

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/v1.29.0/deployment.json": "k8s/**/*.yaml",
    "https://json.schemastore.org/github-workflow.json": ".github/workflows/*.yml"
  }
}
```

**팁**

- SchemaStore(https://www.schemastore.org)에서 대부분의 인프라 도구 스키마 제공
- `yaml-language-server`는 SchemaStore 자동 감지 기능 내장

---

### 2-4. Ansible (`ansible-language-server`)

Ansible playbook, role, task 작성 지원.

**설치**

```bash
pip install ansible-language-server
# 또는
npm install -g @ansible/ansible-language-server
```

**주요 기능**

```yaml
# 모듈 파라미터 자동완성
- name: Install nginx
  ansible.builtin.apt:
    name: nginx
    state: present   # ← present/absent/latest 목록 자동완성
    update_cache: true

# 변수 참조
- name: Deploy app
  template:
    src: "{{ app_template }}"   # ← 정의된 변수 목록 표시
```

**팁**

- `ansible-lint` 연동으로 베스트 프랙티스 검사 가능
  ```bash
  pip install ansible-lint
  ```

---

### 2-5. Python (`pyright`)

인프라 자동화 스크립트, boto3, Ansible 모듈 개발 등에 활용.

**설치**

```bash
pip install pyright
# 또는 격리 환경 권장
pipx install pyright
```

**주요 기능**

```python
import boto3

ec2 = boto3.client('ec2')
response = ec2.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': ['running']   # ← 타입 검증
        }
    ]
)
# response['Reservations']   ← 반환 타입 추론 및 자동완성
```

**팁**

- `boto3-stubs` 설치 시 AWS SDK 자동완성 대폭 향상
  ```bash
  pip install boto3-stubs[ec2,s3,iam]
  ```

---

## 3. 에디터별 LSP 설정

### VSCode

확장 설치만으로 대부분 자동 설정됨.

| 확장 | LSP 서버 |
|------|----------|
| HashiCorp Terraform | terraform-ls |
| YAML | yaml-language-server |
| Ansible | ansible-language-server |
| Python | pyright (Pylance) |
| Bash IDE | bash-language-server |

### Neovim (`nvim-lspconfig`)

```lua
-- ~/.config/nvim/init.lua
require('lspconfig').terraformls.setup{}
require('lspconfig').bashls.setup{}
require('lspconfig').yamlls.setup{
  settings = {
    yaml = {
      schemas = {
        ["https://json.schemastore.org/github-workflow.json"] = ".github/workflows/*.yml",
      }
    }
  }
}
require('lspconfig').pyright.setup{}
require('lspconfig').ansiblels.setup{}
```

---

## 4. 주요 팁 정리

### ✅ 공통

- LSP 서버는 프로젝트 루트에서 실행해야 정확한 컨텍스트 분석 가능
- 대규모 코드베이스는 초기 인덱싱에 시간이 걸림 (이후 빠름)
- LSP 서버가 응답 없으면 재시작으로 해결되는 경우가 많음

### ✅ Terraform

- `terraform init` 먼저 실행해야 provider 스키마 기반 자동완성 동작
- `.terraform` 디렉토리가 있어야 모듈 내부 변수 추적 가능

### ✅ YAML

- 스키마 지정이 핵심 — 스키마 없으면 기본 YAML 문법만 검사
- k8s 버전별 스키마가 다르므로 클러스터 버전에 맞는 스키마 사용

### ✅ Bash

- `shellcheck` 함께 설치하면 보안 취약점, 이식성 문제까지 감지
- `#!/bin/bash` shebang 필수 (LSP가 파일 타입 인식에 사용)

### ✅ Python

- 가상환경(venv) 사용 시 해당 인터프리터 경로를 LSP에 지정해야 정확한 타입 분석
- `pyrightconfig.json`으로 프로젝트별 설정 가능

```json
{
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.11"
}
```

---

## 5. 참고 링크

- [LSP 공식 스펙](https://microsoft.github.io/language-server-protocol/)
- [SchemaStore (YAML 스키마 모음)](https://www.schemastore.org/json/)
- [terraform-ls](https://github.com/hashicorp/terraform-ls)
- [yaml-language-server](https://github.com/redhat-developer/yaml-language-server)
- [ansible-language-server](https://github.com/ansible/ansible-language-server)
- [pyright](https://github.com/microsoft/pyright)
- [bash-language-server](https://github.com/bash-lsp/bash-language-server)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-08

© 2026 siasia86. Licensed under CC BY 4.0.
