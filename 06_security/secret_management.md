# 시크릿 관리

## 목차

| 섹션 |
|------|
| [1. Ansible Vault](#1-ansible-vault) / [2. AWS Secrets Manager](#2-aws-secrets-manager) / [3. HashiCorp Vault](#3-hashicorp-vault) |
| [4. 도구 비교](#4-도구-비교) / [5. 공통 원칙](#5-공통-원칙) |

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
echo "SecurePassword123" > ~/.vault_pass
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
# 시크릿 생성
aws secretsmanager create-secret \
    --name "prod/app/db" \
    --secret-string '{"username":"Secureuser123","password":"SecurePassword123"}'

# 시크릿 조회
aws secretsmanager get-secret-value --secret-id "prod/app/db" \
    --query SecretString --output text

# 시크릿 업데이트
aws secretsmanager update-secret \
    --secret-id "prod/app/db" \
    --secret-string '{"username":"Secureuser123","password":"NewPassword456"}'

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
password = 'SecurePassword123'  # secret['password']
```

```bash
# EC2/ECS에서 사용 시 IAM 정책 (최소 권한)
{
    "Effect": "Allow",
    "Action": ["secretsmanager:GetSecretValue"],
    "Resource": "arn:aws:secretsmanager:ap-northeast-2:*:secret:prod/app/*"
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
export VAULT_TOKEN='SecureToken123'
```

```bash
# KV 시크릿 엔진 사용 (kv-v2: 내부 저장 경로는 secret/data/<path>)
vault secrets enable -path=secret kv-v2

# 시크릿 저장
vault kv put secret/prod/db \
    username=Secureuser123 \
    password=SecurePassword123

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
    username=Secureuser123 \
    password=SecurePassword123

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

## 4. 도구 비교

| 구분        | Ansible Vault    | AWS Secrets Manager    | HashiCorp Vault            |
|-------------|------------------|------------------------|----------------------------|
| 사용 환경   | Ansible 플레이북 | AWS 전용               | 온프레미스/멀티클라우드    |
| 동적 시크릿 | ❌               | ❌ (교체만 지원)       | ✅                         |
| 자동 교체   | ❌               | ✅ (Lambda 연동)       | ✅                         |
| 감사 로그   | ❌               | ✅ (CloudTrail)        | ✅ (Audit Log)             |
| 비용        | 무료             | 유료 ($0.40/시크릿/월) | OSS 무료 / Enterprise 유료 |
| 운영 복잡도 | 낮음             | 낮음 (관리형)          | 높음 (자체 운영)           |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 공통 원칙

- 코드/설정 파일에 시크릿 하드코딩 금지 — `.gitignore` 에 `.env`, `*.key`, `secrets.*` 추가.
- 시크릿은 환경 변수 또는 전용 관리 도구로만 주입.
- 최소 권한 원칙 — 서비스별로 필요한 시크릿만 접근 허용.
- 주기적 교체 — DB 패스워드 90일, API 키 180일 기준.
- 유출 시 즉시 교체 후 감사 로그 확인.

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

**마지막 업데이트**: 2026-05-03

© 2026 siasia86. Licensed under CC BY 4.0.
