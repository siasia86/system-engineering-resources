# HashiCorp Vault 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기화 및 Unseal](#4-초기화-및-unseal) / [5. 기본 사용법](#5-기본-사용법) / [6. 시크릿 엔진](#6-시크릿-엔진) |
| [7. Docker Compose로 구성](#7-docker-compose로-구성) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

Vault는 시크릿(패스워드, API 키, 인증서 등)을 중앙에서 안전하게 저장하고 접근을 제어하는 도구다.

### 핵심 개념

| 개념              | 설명                                              |
|-------------------|---------------------------------------------------|
| **Secret Engine** | 시크릿 저장/생성 플러그인 (KV, Database, PKI 등)  |
| **Auth Method**   | 인증 방식 (Token, AppRole, AWS, Kubernetes 등)    |
| **Policy**        | 경로 기반 접근 제어 (read/write/list)             |
| **Seal/Unseal**   | 마스터 키로 Vault 잠금/해제                       |
| **Lease**         | 동적 시크릿의 유효 기간                           |

### 시스템 요구사항

| 항목   | 최소          | 권장                  |
|--------|---------------|-----------------------|
| CPU    | 1 core        | 2 core 이상           |
| RAM    | 512 MB        | 2 GB 이상             |
| 포트   | 8200/tcp      | 8200/tcp              |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

```bash
sudo apt update && sudo apt install -y gpg

wget -O - https://apt.releases.hashicorp.com/gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update
sudo apt install vault -y
vault --version
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

```bash
sudo dnf install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo dnf install vault -y
vault --version
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기화 및 Unseal

### 4-1. 설정 파일

```bash
sudo tee /etc/vault.d/vault.hcl << 'EOF'
ui = true

storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true   # 프로덕션에서는 TLS 활성화 필수
}
EOF

sudo mkdir -p /opt/vault/data
sudo chown -R vault:vault /opt/vault
sudo systemctl enable --now vault
```

### 4-2. 초기화 (최초 1회)

```bash
export VAULT_ADDR='http://127.0.0.1:8200'

vault operator init
```

```
# 출력 예시 (반드시 안전하게 보관)
Unseal Key 1: xxxx
Unseal Key 2: xxxx
Unseal Key 3: xxxx
Unseal Key 4: xxxx
Unseal Key 5: xxxx

Initial Root Token: hvs.xxxx
```

⚠️ Unseal Key와 Root Token은 분리 보관 필수. 분실 시 복구 불가.

### 4-3. Unseal (재시작 시마다 필요)

```bash
# 5개 중 3개(기본 threshold) 입력
vault operator unseal <Unseal Key 1>
vault operator unseal <Unseal Key 2>
vault operator unseal <Unseal Key 3>

vault status
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 사용법

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='hvs.xxxx'   # Root Token 또는 발급된 Token
```

### 로그인

```bash
vault login <token>
vault login -method=userpass username=Secureuser123
```

### 시크릿 읽기/쓰기

```bash
# KV v2 시크릿 엔진 활성화
vault secrets enable -path=secret kv-v2

# 시크릿 저장
vault kv put secret/myapp/db \
    username=Secureuser123 \
    password=SecurePassword123

# 시크릿 조회
vault kv get secret/myapp/db
vault kv get -field=password secret/myapp/db

# 시크릿 삭제
vault kv delete secret/myapp/db

# 버전 히스토리
vault kv metadata get secret/myapp/db
```

### 정책 관리

```bash
# 정책 파일 작성
cat > myapp-policy.hcl << 'EOF'
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}
EOF

# 정책 등록
vault policy write myapp-policy myapp-policy.hcl

# 정책 확인
vault policy list
vault policy read myapp-policy
```

### 토큰 발급

```bash
# 정책 적용 토큰 발급
vault token create -policy=myapp-policy -ttl=24h

# AppRole 인증 (애플리케이션용)
vault auth enable approle
vault write auth/approle/role/myapp \
    token_policies=myapp-policy \
    token_ttl=1h

vault read auth/approle/role/myapp/role-id
vault write -f auth/approle/role/myapp/secret-id
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 시크릿 엔진

### Database 시크릿 엔진 (동적 자격증명)

```bash
vault secrets enable database

vault write database/config/mydb \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(10.0.1.10:3306)/" \
    allowed_roles="myapp-role" \
    username=Secureuser123 \
    password=SecurePassword123

vault write database/roles/myapp-role \
    db_name=mydb \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON mydb.* TO '{{name}}'@'%';" \
    default_ttl=1h \
    max_ttl=24h

# 동적 자격증명 발급 (매번 새로운 계정 생성)
vault read database/creds/myapp-role
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Docker Compose로 구성

```yaml
# compose.yaml
services:
  vault:
    image: hashicorp/vault:1.17
    ports:
      - "8200:8200"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: SecureToken123   # 개발 모드 전용
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
    cap_add:
      - IPC_LOCK
    command: server -dev
    restart: unless-stopped
```

⚠️ `-dev` 모드는 메모리 저장, 재시작 시 데이터 초기화. 개발/테스트 전용.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: Auto Unseal (AWS KMS)

재시작 시 수동 Unseal 없이 자동으로 해제됩니다.

```hcl
# vault.hcl
seal "awskms" {
  region     = "ap-northeast-2"
  kms_key_id = "alias/vault-unseal-key"
}
```

### Tip 2: 환경 변수로 시크릿 주입 (애플리케이션)

```bash
# vault agent 또는 envconsul 사용
DB_PASSWORD=$(vault kv get -field=password secret/myapp/db)
export DB_PASSWORD
```

### Tip 3: 감사 로그 활성화

```bash
vault audit enable file file_path=/var/log/vault/audit.log
vault audit list
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                              | 원인                          | 해결 방법                                              |
|-----------------------------------|-------------------------------|--------------------------------------------------------|
| `Error initializing core: ...`    | 스토리지 경로 권한 오류       | `chown -R vault:vault /opt/vault`                      |
| `Vault is sealed`                 | 재시작 후 Unseal 미완료       | `vault operator unseal` 3회 실행                       |
| `permission denied`               | 토큰 정책 미설정              | `vault token capabilities <token> <path>` 확인         |
| `connection refused`              | Vault 미실행 또는 포트 오류   | `systemctl status vault`, `VAULT_ADDR` 확인            |

```bash
# 상태 확인
vault status

# 로그 확인
sudo journalctl -u vault -f
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HashiCorp Vault Documentation: [developer.hashicorp.com/vault](https://developer.hashicorp.com/vault/docs) — ★★★☆☆
- Vault Tutorials: [developer.hashicorp.com/vault/tutorials](https://developer.hashicorp.com/vault/tutorials) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
