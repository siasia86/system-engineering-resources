# 시크릿 관리
<!-- reference: _reference/aws_sts_iam_s3_kms_official_notes.md, _reference/aws_secrets_manager_official_notes.md, _reference/gitlab_ci_variables_official_notes.md, _reference/hashicorp_vault_official_notes.md -->

## 목차

| 섹션                                                                                                                               |
|------------------------------------------------------------------------------------------------------------------------------------|
| [1. Ansible Vault](#1-ansible-vault) / [2. AWS Secrets Manager](#2-aws-secrets-manager) / [3. HashiCorp Vault](#3-hashicorp-vault) |
| [4. CI Protected Variable](#4-ci-protected-variable) / [5. AWS KMS](#5-aws-kms) / [6. 참조 아키텍처](#6-참조-아키텍처)             |
| [7. 위협 모델과 실패 사례](#7-위협-모델과-실패-사례) / [8. 도구 비교](#8-도구-비교) / [9. 공통 원칙](#9-공통-원칙)                 |

---

## 1. Ansible Vault

Ansible 플레이북 내 민감 정보 암호화.

```bash
# 파일 암호화
ansible-vault encrypt vars/secrets.yml

# 파일 복호화
ansible-vault decrypt vars/secrets.yml

# 암호화된 파일 편집
ansible-vault edit vars/secrets.yml

# 암호화된 값 생성 (인라인)
ansible-vault encrypt_string 'SecurePassword123' --name 'db_password'

# 플레이북 실행 시 패스워드 입력
ansible-playbook site.yml --ask-vault-pass

# 패스워드 파일 사용 (자동화)
# 실제 값은 외부 Secret Store 또는 CI Protected Variable에서 주입
chmod 600 ~/.vault_pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

```yaml
# vars/secrets.yml (암호화 전)
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...

# 플레이북에서 사용
- name: configure db
  template:
    src: db.conf.j2
    dest: /etc/app/db.conf
  vars:
    password: "{{ db_password }}"
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. AWS Secrets Manager

AWS 환경에서 자격증명 중앙 관리 및 자동 교체.

```bash
# 시크릿 생성: 실제 값은 보호된 파일로 준비하고 CLI 인자에 직접 넣지 않음
aws secretsmanager create-secret \
    --name "prod/app/db" \
    --secret-string file://secret.json \
    --region ap-northeast-2

# secret.json은 저장소에 커밋하지 않고 사용 후 즉시 삭제
rm -f secret.json

# 시크릿 조회: 결과를 터미널에 출력하지 않고 보호된 임시 파일로 전달
secret_file=$(mktemp)
trap 'rm -f "$secret_file"' EXIT
aws secretsmanager get-secret-value --secret-id "prod/app/db" \
    --query SecretString --output text > "$secret_file"

# 시크릿 업데이트: 실제 값은 보호된 파일로 준비하고 CLI 인자에 직접 넣지 않음
aws secretsmanager update-secret \
    --secret-id "prod/app/db" \
    --secret-string file://secret.json

# 자동 교체 활성화 (Lambda 사용)
aws secretsmanager rotate-secret \
    --secret-id "prod/app/db" \
    --rotation-lambda-arn arn:aws:lambda:ap-northeast-2:123456789012:function:rotate-db
```

```python
# Python에서 조회
import boto3, json

client = boto3.client('secretsmanager', region_name='ap-northeast-2')
response = client.get_secret_value(SecretId='prod/app/db')
secret = json.loads(response['SecretString'])
password = secret['password']
```

```bash
# EC2/ECS에서 사용 시 IAM 정책 (최소 권한)
{
    "Effect": "Allow",
    "Action": ["secretsmanager:GetSecretValue"],
    "Resource": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:prod/app/*"
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. HashiCorp Vault

온프레미스/멀티클라우드 환경의 시크릿 관리.

```bash
# 설치 (Ubuntu)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault

# 개발 서버 시작 (테스트용)
vault server -dev

# 환경 변수 설정
export VAULT_ADDR='http://127.0.0.1:8200'
# 실제 Token은 외부 Secret Store 또는 CI Protected Variable에서 주입
export VAULT_TOKEN="${VAULT_TOKEN:?VAULT_TOKEN is required}"
```

```bash
# KV 시크릿 엔진 사용 (kv-v2: 내부 저장 경로는 secret/data/<path>)
vault secrets enable -path=secret kv-v2

# 시크릿 저장: 실제 값은 외부에서 주입하고 코드에 기록하지 않음
vault kv put secret/prod/db \
    username="${DB_USERNAME:?DB_USERNAME is required}" \
    password="${DB_PASSWORD:?DB_PASSWORD is required}"

# 시크릿 조회
vault kv get secret/prod/db
vault kv get -field=password secret/prod/db

# 시크릿 삭제
vault kv delete secret/prod/db
```

```bash
# 동적 시크릿 (DB 자격증명 자동 생성)
vault secrets enable database
vault write database/config/my-db \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(db.example.com:3306)/" \
    allowed_roles="app-role" \
    username="${DB_USERNAME:?DB_USERNAME is required}" \
    password="${DB_PASSWORD:?DB_PASSWORD is required}"

# role 생성 (발급 전 필수)
vault write database/roles/app-role \
    db_name=my-db \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON *.* TO '{{name}}'@'%';" \
    default_ttl=1h \
    max_ttl=24h

# 임시 자격증명 발급 (TTL 1시간)
vault read database/creds/app-role
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. CI Protected Variable

GitLab CI/CD Variable은 Pipeline과 Job 실행 시 필요한 값을 전달하는 기능입니다. 민감한 Token·Password를 `.gitlab-ci.yml`에 직접 저장하지 않고 GitLab Project 또는 Group 설정에서 관리합니다.

### Protected와 Masked 구분

- `Protected`: Protected Branch 또는 Protected Tag의 Pipeline에만 변수를 제공합니다.
- `Masked`: Job 로그에서 값이 노출되는 것을 줄이는 기능입니다. 파일·Artifact·외부 시스템으로의 유출까지 차단하지 않습니다.
- `File`: private key나 설정 파일을 임시 파일로 주입할 때 사용합니다. Job 종료 시 파일을 삭제합니다.
- `Environment scope`: `production` 등 특정 배포 환경에만 변수를 연결합니다.

🟡 주의: `Masked`는 Secret Store가 아니며, `Protected`는 별도의 암호화·접근통제 정책을 대체하지 않습니다.

### CI 보안 원칙

- `echo`, `env`, `printenv`, `set -x`, Debug Trace로 Secret을 출력하지 않습니다.
- Fork·비신뢰 Merge Request·공유 Runner에 운영 Secret을 전달하지 않습니다.
- Artifact·Cache·dotenv 파일에 Secret이 남지 않도록 합니다.
- 장기 AWS Access Key 대신 GitLab OIDC와 AWS STS 임시 자격증명을 사용합니다.
- CI에는 Secret 값보다 `SECRET_ID`, `AWS_ROLE_ARN`, `AWS_REGION` 같은 식별자·비밀이 아닌 설정을 우선 전달합니다.

> OIDC(OpenID Connect): CI Job이 발급한 ID Token으로 외부 서비스가 Job의 신원을 확인하는 표준입니다.
> GitLab과 AWS IAM을 연동하면 장기 AWS Access Key를 CI Variable에 저장하지 않고 STS 임시 자격증명을 받을 수 있습니다.

### 권장 흐름

```yaml
deploy:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.example.com
  variables:
    SECRET_ID: "prod/app/db"
    AWS_REGION: "ap-northeast-2"
  script:
    - ./deploy.sh
```

`deploy.sh`는 OIDC로 얻은 단기 AWS 자격증명으로 AWS Secrets Manager를 조회하며, 값을 로그에 출력하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. AWS KMS

AWS KMS는 Secret 저장소가 아니라 암호화 키를 생성·보호·사용·감사하는 서비스입니다. AWS Secrets Manager, S3, SSM Parameter Store, 암호화된 설정 파일 등에 사용할 수 있습니다.

### 핵심 구분

```text
KMS Key Rotation       ≠       DB·FTP Password Rotation
암호화 키 재료 교체              애플리케이션 자격증명 교체
```

- IAM Policy와 KMS Key Policy를 함께 검토합니다.
- `kms:Decrypt`는 필요한 Role과 리소스에만 허용합니다.
- Key Admin과 Key User 권한을 분리합니다.
- `kms:ViaService`, Encryption Context, CloudTrail을 검토합니다.
- KMS 키 삭제 예약과 복구 절차를 문서화합니다.

### AWS Secrets Manager와 KMS 연동

Customer managed key로 Secret을 암호화하면 Secret 조회 권한과 KMS 복호화 권한을 함께 확인해야 합니다.

```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:GetSecretValue"
  ],
  "Resource": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:prod/app/*"
}
```

```json
{
  "Effect": "Allow",
  "Action": [
    "kms:Decrypt"
  ],
  "Resource": "arn:aws:kms:ap-northeast-2:123456789012:key/KEY_ID"
}
```

두 권한 모두를 무조건 `*`로 허용하지 않고 애플리케이션별 Role과 키를 분리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 참조 아키텍처

AWS와 자체 IDC를 함께 운영하는 경우 Secret 저장소와 CI 인증 경로를 분리합니다.

```text
┌────────────────────────────────────────────────────────────┐
│ Private GitLab                                             │
│ IaC, templates, and CI pipelines                           │
│ CI OIDC token                                              │
│                         │                                  │
│                         v                                  │
│ AWS IAM: short-lived STS credentials                       │
│                         │                                  │
│                         v                                  │
│ AWS Secrets Manager: runtime secrets                       │
│ AWS KMS: encryption keys and audit                         │
│ AWS and IDC workloads: least-privilege access              │
└────────────────────────────────────────────────────────────┘
```

- AWS 전용 애플리케이션은 AWS Secrets Manager와 IAM Role을 사용합니다.
- IDC가 AWS에 접근할 때는 Direct Connect·VPN과 단기 STS 자격증명을 발급하는 연동 방식을 검토합니다.
- AWS 단절 시에도 독립 운영해야 하는 IDC는 별도 Secret Store 또는 암호화된 배포 파일을 검토합니다.
- 동일 Secret을 여러 저장소에 복제하면 노출 지점이 늘어나므로 단일 원본과 동기화 책임을 정의합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 위협 모델과 실패 사례

### 주요 위협

- Git 이력·Issue·Merge Request·Wiki에 평문 Secret이 남는 경우.
- CI 로그·Debug Trace·Artifact·Cache에 Secret이 남는 경우.
- 보호되지 않은 Runner에서 악성 Pipeline이 실행되는 경우.
- Secret Store 또는 KMS 권한이 전체 Secret·키로 확장된 경우.
- Secret Rotation 후 애플리케이션이 이전 값을 계속 사용하는 경우.
- IDC와 AWS 네트워크 단절로 Secret을 조회하지 못하는 경우.

### 안티패턴

```text
❌ Private GitLab이므로 평문 Secret 저장
❌ 장기 AWS Access Key를 CI Variable에 저장
❌ Masked Variable이면 유출이 완전히 차단된다고 판단
❌ KMS Decrypt 권한을 전체 계정에 부여
❌ 암호화 파일과 복호화 키를 같은 저장소에 저장
❌ CI Artifact에 복호화된 설정 파일 업로드
❌ Git 파일만 삭제하고 이미 노출된 자격증명을 재사용
```

Secret이 Git 이력이나 로그에 노출되면 먼저 자격증명을 폐기·교체하고, 그 다음 이력·Artifact·Cache를 정리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 도구 비교

| 구분        | Ansible Vault | AWS Secrets Manager  | HashiCorp Vault       | GitLab CI Variable | AWS KMS         |
|-------------|---------------|----------------------|-----------------------|--------------------|-----------------|
| 주 역할     | 파일 암호화   | Secret 저장·Rotation | 중앙 Secret·동적 발급 | CI 값 주입         | 키 관리·암호화  |
| 사용 환경   | Ansible 배포  | AWS·연동 환경        | IDC·멀티클라우드      | GitLab Pipeline    | AWS 리소스·파일 |
| 동적 Secret | ❌            | 일부 Rotation        | ✅                    | ❌                 | ❌              |
| 감사        | 제한적        | CloudTrail           | Audit Log             | Pipeline·변경 이력 | CloudTrail      |
| 운영 부담   | 낮음          | 낮음 (관리형)        | 높음 (자체 운영)      | 낮음               | 낮음 (관리형)   |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 공통 원칙

- 코드/설정 파일에 시크릿 하드코딩 금지 — `.gitignore` 에 `.env`, `*.key`, `secrets.*` 추가.
- 시크릿은 환경 변수 또는 전용 관리 도구로만 주입하며 로그·Artifact에 출력하지 않습니다.
- 최소 권한 원칙 — 서비스별로 필요한 Secret만 접근 허용합니다.
- CI에는 장기 자격증명 대신 OIDC·STS 등 단기 자격증명을 사용합니다.
- 주기적 교체 — 조직의 위험도·외부 정책·서비스 지원 범위를 기준으로 정합니다.
- 유출 시 먼저 자격증명을 폐기·교체하고 감사 로그와 Git 이력을 확인합니다.
- KMS Key Rotation과 애플리케이션 Secret Rotation을 별도 통제로 관리합니다.

```bash
# git 커밋 전 시크릿 스캔 (gitleaks)
gitleaks detect --source . --verbose

# pre-commit hook 등록
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
gitleaks protect --staged --verbose
EOF
chmod +x .git/hooks/pre-commit
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HashiCorp Vault Documentation: [developer.hashicorp.com/vault](https://developer.hashicorp.com/vault/docs) — ★★★☆☆
- Vault Dynamic Secrets (DB): [developer.hashicorp.com/vault/docs/secrets/databases](https://developer.hashicorp.com/vault/docs/secrets/databases) — ★★★☆☆
- AWS Secrets Manager: [docs.aws.amazon.com/secretsmanager](https://docs.aws.amazon.com/secretsmanager/) — ★★★☆☆
- AWS KMS: [docs.aws.amazon.com/kms](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html) — ★★★☆☆
- GitLab CI/CD variables: [docs.gitlab.com/ci/variables](https://docs.gitlab.com/ci/variables/) — ★★★☆☆
- GitLab AWS OIDC: [docs.gitlab.com/ci/cloud_services/aws](https://docs.gitlab.com/ci/cloud_services/aws/) — ★★★☆☆
- Ansible Vault: [docs.ansible.com](https://docs.ansible.com/ansible/latest/vault_guide/) — ★★★☆☆
- gitleaks (시크릿 스캔): [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★☆☆☆

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

**마지막 업데이트**: 2026-08-19

© 2026 siasia86. Licensed under CC BY 4.0.
