# HashiCorp Vault 설치 가이드
<!-- reference: _reference/hashicorp_vault_official_notes.md -->

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치)                   |
| [4. 초기화 및 Unseal](#4-초기화-및-unseal) / [5. 기본 사용법](#5-기본-사용법) / [6. 시크릿 엔진](#6-시크릿-엔진) |
| [7. Docker Compose로 구성](#7-docker-compose로-구성) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

Vault는 패스워드, API 키, 인증서 등의 시크릿을 중앙에서 저장하고 접근을 제어하는 도구입니다. 개념과 구성요소는 [HashiCorp Vault 개념](hashicorp_vault_concepts.md), 설치·운영 절차는 이 문서를 참고합니다.

### 핵심 개념

| 개념               | 설명                                                  |
|--------------------|-------------------------------------------------------|
| **Secrets Engine** | 시크릿을 저장하거나 생성하는 플러그인입니다.          |
| **Auth Method**    | Token, AppRole, AWS, Kubernetes 등의 인증 방식입니다. |
| **Policy**         | 경로별 `read`, `write`, `list` 권한을 정의합니다.     |
| **Seal/Unseal**    | Vault의 암호화 키 접근을 잠금 또는 해제합니다.        |
| **Lease**          | 동적 시크릿의 유효 기간과 갱신 정보를 관리합니다.     |

### 시스템 요구사항

아래 CPU와 RAM 값은 HashiCorp가 고정한 공식 최소 요구사항이 아닙니다. 단일 노드 학습 환경을 시작하기 위한 예시이며, 실제 용량은 시크릿 규모, 플러그인, 요청량, HA 구성 여부를 기준으로 산정합니다.

| 항목    | 단일 노드 시작 예시 | 비고                                  |
|---------|---------------------|---------------------------------------|
| CPU     | 1 core              | 실제 부하는 요청량에 따라 측정합니다. |
| RAM     | 512 MB 이상         | 운영 환경은 부하 테스트가 필요합니다. |
| API     | 8200/tcp            | Vault API와 UI 기본 포트입니다.       |
| Cluster | 8201/tcp            | HA 클러스터 통신 시 사용합니다.       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

HashiCorp 공식 APT 저장소를 등록한 뒤 `vault` 패키지를 설치합니다. 공식 설치 문서 기준 최신 버전은 2026-08-20 확인 시 `2.0.4`입니다.

```bash
sudo apt-get update
sudo apt-get install -y gnupg

wget -O - https://apt.releases.hashicorp.com/gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" \
    | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt-get update
sudo apt-get install -y vault
vault --version
```

🟡 운영 환경에서는 설치 후 `apt` 저장소와 패키지 버전을 고정하거나 승인된 업그레이드 절차로 관리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

HashiCorp 공식 RPM 저장소를 등록한 뒤 `vault` 패키지를 설치합니다.

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install vault
vault --version
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기화 및 Unseal

### 4-1. 설정 파일

패키지 설치 시 `/etc/vault.d/vault.hcl`과 `/opt/vault/tls/`가 생성됩니다. 운영 환경에서는 신뢰할 수 있는 CA가 서명한 인증서를 사용하고, 방화벽에서 허용한 주소에만 listener를 바인딩합니다.

아래는 단일 호스트에서 로컬 접근만 허용하는 TLS 설정 예시입니다. 원격 접근이 필요하면 `127.0.0.1` 대신 승인된 사설 주소를 사용하고, 인증서의 SAN과 `api_addr`를 일치시켜야 합니다.

```hcl
ui = true

storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address       = "127.0.0.1:8200"
  tls_cert_file = "/opt/vault/tls/tls.crt"
  tls_key_file  = "/opt/vault/tls/tls.key"
}

api_addr = "https://127.0.0.1:8200"
```

```bash
sudo install -d -o vault -g vault -m 0750 /opt/vault/data
sudo chown -R vault:vault /opt/vault
sudo systemctl enable --now vault

export VAULT_ADDR='https://127.0.0.1:8200'
export VAULT_CACERT='/opt/vault/tls/tls.crt'
vault status
```

🟡 `tls_disable = true`와 `address = "0.0.0.0:8200"` 조합은 평문 트래픽과 전체 인터페이스 노출을 발생시키므로 운영 환경에 사용하지 않습니다. 개발 모드도 메모리 저장과 평문 로컬 listener를 사용하므로 운영 환경에 사용하지 않습니다.

### 4-2. 초기화 (최초 1회)

`operator init`은 스토리지를 초기화하고 루트 키를 생성합니다. 동일 스토리지를 사용하는 HA 클러스터에서는 한 번만 실행합니다. 기본값은 `key-shares=5`, `key-threshold=3`이지만 초기화 옵션으로 변경할 수 있습니다.

```bash
export VAULT_ADDR='https://127.0.0.1:8200'
export VAULT_CACERT='/opt/vault/tls/tls.crt'
umask 077

vault operator init
```

```text
# 출력 예시입니다. 실제 키와 토큰을 문서나 채팅에 기록하지 않습니다.
Unseal Key 1: <unseal-key-1>
Unseal Key 2: <unseal-key-2>
Unseal Key 3: <unseal-key-3>
Unseal Key 4: <unseal-key-4>
Unseal Key 5: <unseal-key-5>

Initial Root Token: <initial-root-token>
```

🟡 필요한 threshold 수의 Unseal Key를 분리 보관합니다. threshold에 필요한 키를 잃으면 일반적인 Shamir 방식으로 Vault를 Unseal할 수 없습니다. 초기 Root Token은 최초 설정에만 사용한 뒤 폐기하고, 운영용 토큰은 최소 권한과 짧은 TTL로 발급합니다.

### 4-3. Unseal

Unseal Key를 명령행 인자로 전달하면 셸 히스토리나 프로세스 정보에 노출될 수 있습니다. 인자를 생략하고 대화형 입력을 사용하며, 설정된 threshold 수만큼 반복합니다.

```bash
vault operator unseal
vault operator unseal
vault operator unseal

vault status
```

Auto Unseal을 사용하는 경우에는 Unseal Key 대신 구성된 KMS 등의 Seal 방식에 따라 Recovery Key를 관리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 사용법

TLS를 사용하는 서버에서는 `VAULT_ADDR`와 `VAULT_CACERT`를 함께 설정합니다.

```bash
export VAULT_ADDR='https://127.0.0.1:8200'
export VAULT_CACERT='/opt/vault/tls/tls.crt'
```

### 로그인

Root Token을 환경 변수에 장기간 저장하지 않고, 대화형 입력으로 최초 설정을 수행합니다.

```bash
vault login
```

`userpass` 인증은 먼저 활성화하고 사용자를 생성해야 합니다.

```bash
vault auth enable userpass
vault write auth/userpass/users/Secureuser123 \
    password=SecurePassword123 \
    policies=myapp-policy
vault login -method=userpass username=Secureuser123
```

🟡 예시 패스워드는 플레이스홀더입니다. 실제 패스워드를 명령행에 직접 입력하면 셸 히스토리나 프로세스 목록에 노출될 수 있으므로 승인된 시크릿 주입 절차를 사용합니다.

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

# 시크릿 삭제: KV v2의 soft delete
vault kv delete secret/myapp/db

# 버전 히스토리와 메타데이터
vault kv metadata get secret/myapp/db
vault kv list secret/myapp
```

KV v2에서 실제 데이터 경로는 `secret/data/...`이고, 목록과 메타데이터 경로는 `secret/metadata/...`입니다. 영구 삭제가 필요한 경우에는 soft delete와 구분하여 `vault kv destroy`를 사용합니다.

### 정책 관리

```bash
# 정책 파일 작성
cat > myapp-policy.hcl << 'EOF'
path "secret/data/myapp/*" {
  capabilities = ["read"]
}

path "secret/metadata/myapp/*" {
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
    token_ttl=1h \
    token_max_ttl=24h

vault read auth/approle/role/myapp/role-id
vault write -f auth/approle/role/myapp/secret-id
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 시크릿 엔진

### Database 시크릿 엔진 (동적 자격증명)

Database Secrets Engine은 역할에 정의한 SQL로 단기 데이터베이스 계정을 발급합니다. 아래 MySQL 예시는 공식 문서의 `mysql-database-plugin` 구성 형식을 따릅니다.

```bash
vault secrets enable database

vault write database/config/mydb \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(192.0.2.10:3306)/" \
    allowed_roles="myapp-role" \
    username=Secureuser123 \
    password=SecurePassword123

vault write database/roles/myapp-role \
    db_name=mydb \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON mydb.* TO '{{name}}'@'%';" \
    default_ttl=1h \
    max_ttl=24h

# 동적 자격증명 발급
vault read database/creds/myapp-role
```

🟡 `192.0.2.10`과 자격증명은 예시 값입니다. 실제 DB 주소와 관리자 자격증명은 명령행·소스 코드·문서에 하드코딩하지 않고 별도 시크릿 주입 절차로 관리합니다. 발급된 계정은 Lease 만료와 폐기 정책을 함께 검증합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Docker Compose로 구성

Docker Compose는 개발·테스트에만 사용하고, 운영 환경에서는 영속 스토리지·TLS·백업·Unseal·방화벽을 별도로 설계합니다. 2026-08-20 확인 최신 태그는 `2.0.4`이며, 아래는 해당 멀티 아키텍처 이미지의 확인된 digest를 고정한 예시입니다.

```yaml
# compose.yaml
services:
  vault:
    image: hashicorp/vault:2.0.4@sha256:5be49781ecf78bfe775c5309c6a4d9f4e9e040b6c885c99eb2b12fb69855e1a2
    ports:
      - "127.0.0.1:8200:8200"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: SecureToken123   # 개발 모드 전용
      VAULT_DEV_LISTEN_ADDRESS: 127.0.0.1:8200
    cap_add:
      - IPC_LOCK
    command: server -dev
    restart: unless-stopped
```

🟡 `-dev` 모드는 자동 초기화·Unseal, 메모리 저장, 평문 로컬 listener를 사용합니다. 재시작하면 데이터가 사라지므로 개발·테스트 외의 용도로 사용하지 않습니다. `VAULT_DEV_ROOT_TOKEN_ID`도 개발 환경에서만 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: Auto Unseal (AWS KMS)

AWS KMS Auto Unseal은 재시작 시 수동 Unseal 절차를 줄입니다. Vault 호스트에는 장기 액세스 키를 저장하지 않고 AWS IAM Instance Profile, ECS Task Role 등 워크로드 자격증명을 사용합니다.

```hcl
# vault.hcl
seal "awskms" {
  region     = "ap-northeast-2"
  kms_key_id = "alias/vault-unseal-key"
}
```

Vault가 사용하는 IAM 주체에는 최소한 `kms:Encrypt`, `kms:Decrypt`, `kms:DescribeKey` 권한이 필요합니다. KMS 키 정책과 IAM 정책을 함께 검토합니다.

#### KMS 키 정책·감사·복구 운영

Auto Unseal은 Vault 설정만으로 끝나지 않습니다. KMS Key Policy와 IAM Role을 분리 검토하고, Vault Role에는 지정한 KMS 키의 사용 권한만 허용합니다. Key Admin 권한과 Key User 권한을 같은 Role에 묶지 않으며, 장기 Access Key 대신 EC2 Instance Profile·ECS Task Role·EKS IRSA 또는 Pod Identity를 사용합니다.

CloudTrail에서는 정상적인 Vault Role의 `kms:Decrypt`, `kms:Encrypt`, `kms:DescribeKey` 호출과 다음과 같은 고위험 변경을 구분해 감사합니다.

- `DisableKey`, `ScheduleKeyDeletion`, `CancelKeyDeletion`
- `PutKeyPolicy`, `CreateGrant`, `RetireGrant`
- 예상하지 않은 Principal·리전·시간대의 KMS API 호출

```bash
KEY_ID="alias/vault-unseal-key"
REGION="ap-northeast-2"

# 키 상태와 현재 Key Policy 확인
aws kms describe-key --key-id "$KEY_ID" --region "$REGION"
aws kms get-key-policy \
    --key-id "$KEY_ID" \
    --policy-name default \
    --region "$REGION"

# 최근 KMS Decrypt와 키 삭제 관련 이벤트 확인
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=Decrypt \
    --region "$REGION" \
    --max-results 50
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=ScheduleKeyDeletion \
    --region "$REGION" \
    --max-results 50
```

CloudTrail Event History는 보존 기간이 제한되므로 장기 감사가 필요하면 조직 단위 Trail과 중앙 로그 저장소를 구성합니다. Vault가 실행되는 Role의 `Decrypt` 호출이 예상한 리전과 Principal에서 발생하는지 확인하고, KMS Key Policy 변경에는 별도 승인과 알림을 적용합니다.

AWS KMS 키의 영구 삭제는 일반적인 백업 복원으로 되돌릴 수 없습니다. 삭제가 예약된 상태라면 삭제 대기 기간 안에 다음 명령으로 취소할 수 있지만, 영구 삭제 후 새 KMS 키를 같은 별칭으로 만들어도 기존 Vault 암호문을 복호화할 수 없습니다.

```bash
# 삭제 예약 상태에서만 취소 가능 — 승인된 복구 절차에서 실행
aws kms cancel-key-deletion \
    --key-id "$KEY_ID" \
    --region "$REGION"

# 비활성화된 키를 활성화 — 원인과 승인 상태를 먼저 확인
aws kms enable-key \
    --key-id "$KEY_ID" \
    --region "$REGION"
```

복구 절차는 다음 순서로 별도 검증합니다.

1. KMS 키가 삭제 예약·비활성화되지 않았는지 확인합니다.
2. Vault 실행 Role의 IAM Policy와 KMS Key Policy 양쪽의 `kms:Decrypt` 권한을 확인합니다.
3. KMS 키가 살아 있는 상태에서 Vault 스토리지 백업을 격리 환경에 복원하고 자동 Unseal을 테스트합니다.
4. KMS 키가 영구 삭제된 경우에는 기존 Vault 데이터를 복구할 수 없으므로, 키 삭제 방지·백업 보존·재해 복구 환경을 사전에 검증합니다.

KMS 키 정책, 별칭, 삭제 방지 설정은 IaC로 관리하되 기존 키를 삭제하고 재생성하지 않도록 `prevent_destroy`와 변경 승인 절차를 적용합니다. Recovery Key는 운영자 복구 작업에 필요하지만, 영구 삭제된 KMS 키를 대체하지 않습니다.

### Tip 2: 환경 변수로 시크릿 주입 (애플리케이션)

```bash
# vault agent 또는 envconsul 사용
DB_PASSWORD=$(vault kv get -field=password secret/myapp/db)
export DB_PASSWORD
```

애플리케이션에서는 가능한 경우 Vault Agent의 파일 템플릿이나 런타임 시크릿 주입 방식을 사용하여 시크릿의 셸 노출을 줄입니다.

### Tip 3: 감사 로그 활성화

Vault 프로세스가 로그 파일을 생성할 수 있도록 디렉토리 권한을 먼저 설정합니다.

```bash
sudo install -d -o vault -g vault -m 0750 /var/log/vault
vault audit enable file file_path=/var/log/vault/audit.log
vault audit list
```

감사 로그에는 민감한 요청 메타데이터가 포함될 수 있으므로 접근 권한을 제한하고, 로그 로테이션과 중앙 수집을 구성합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                           | 원인                        | 해결 방법                                            |
|--------------------------------|-----------------------------|------------------------------------------------------|
| `Error initializing core: ...` | 스토리지 경로 권한 오류     | `chown -R vault:vault /opt/vault`                    |
| `Vault is sealed`              | Unseal threshold 미충족     | 설정된 threshold 수만큼 `vault operator unseal` 실행 |
| `permission denied`            | 토큰 정책 미설정            | `vault token capabilities <token> <path>` 확인       |
| `connection refused`           | Vault 미실행 또는 포트 오류 | `systemctl status vault`, `VAULT_ADDR` 확인          |

```bash
# 상태 확인
vault status

# 최근 로그 확인
sudo journalctl -u vault --no-pager -n 100
```

Unseal Key를 명령행 인자로 전달하지 말고 `vault operator unseal`을 인자 없이 실행합니다. 초기화·Unseal 키를 잃은 경우에는 구성한 Seal 방식과 백업·복구 절차를 확인해야 하며, threshold에 필요한 키가 없는 Shamir 구성은 일반적인 방식으로 복구할 수 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HashiCorp Vault Install: [developer.hashicorp.com/vault/install](https://developer.hashicorp.com/vault/install) — ★★★☆☆
- Vault TCP Listener Configuration: [developer.hashicorp.com/vault/docs/configuration/listener/tcp](https://developer.hashicorp.com/vault/docs/configuration/listener/tcp) — ★★★☆☆
- Vault Production Hardening: [developer.hashicorp.com/vault/docs/concepts/production-hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) — ★★★★☆
- Vault Operator Init: [developer.hashicorp.com/vault/docs/commands/operator/init](https://developer.hashicorp.com/vault/docs/commands/operator/init) — ★★★☆☆
- Vault KV v2: [developer.hashicorp.com/vault/docs/secrets/kv](https://developer.hashicorp.com/vault/docs/secrets/kv) — ★★★☆☆
- Vault Policies: [developer.hashicorp.com/vault/docs/concepts/policies](https://developer.hashicorp.com/vault/docs/concepts/policies) — ★★★☆☆
- Vault Database Secrets Engine: [developer.hashicorp.com/vault/docs/secrets/databases](https://developer.hashicorp.com/vault/docs/secrets/databases) — ★★★☆☆
- Vault Audit Devices: [developer.hashicorp.com/vault/docs/audit](https://developer.hashicorp.com/vault/docs/audit) — ★★★☆☆
- Vault AWS KMS Seal: [developer.hashicorp.com/vault/docs/configuration/seal/awskms](https://developer.hashicorp.com/vault/docs/configuration/seal/awskms) — ★★★☆☆
- AWS KMS Key Policies: [docs.aws.amazon.com/kms/latest/developerguide/key-policies.html](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html) — ★★★☆☆
- AWS KMS Key Deletion: [docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html) — ★★★☆☆
- AWS KMS CloudTrail Logging: [docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html](https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html) — ★★★☆☆
- Vault Releases: [github.com/hashicorp/vault/releases](https://github.com/hashicorp/vault/releases) — ★★★☆☆
- Vault Docker Images: [hub.docker.com/r/hashicorp/vault/tags](https://hub.docker.com/r/hashicorp/vault/tags) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-08-21

© 2026 siasia86. Licensed under CC BY 4.0.
