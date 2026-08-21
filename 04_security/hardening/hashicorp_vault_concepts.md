# HashiCorp Vault 개념
<!-- reference: _reference/hashicorp_vault_official_notes.md -->

## 목차

| 단계 | 섹션                                                                                                                   |
|------|------------------------------------------------------------------------------------------------------------------------|
| 기본 | [1. 개요](#1-개요) / [2. 핵심 구성요소](#2-핵심-구성요소)                                                              |
| 내부 | [3. Barrier와 Shamir Secret Sharing](#3-barrier와-shamir-secret-sharing)                                               |
| 설계 | [4. Secret 수명주기](#4-secret-수명주기) / [5. 인증과 Policy](#5-인증과-policy) / [6. Secret Engine](#6-secret-engine) |
| 운영 | [7. 운영 모델](#7-운영-모델) / [8. 도입 판단 기준](#8-도입-판단-기준) / [9. 관련 문서](#9-관련-문서)                   |
| 참고 | [10. 용어 정리](#10-용어-정리)                                                                                         |

---

## 1. 개요

HashiCorp Vault는 인증된 Client와 Workload에 Secret을 런타임으로 제공하는 중앙 서비스입니다.

Ansible Vault가 파일·변수에 포함된 값을 암호화하는 도구라면, HashiCorp Vault는 실행 시점에 Secret에 접근하게 하고 Dynamic Secret Engine에서는 Credential을 발급하며 접근을 통제하는 서비스입니다.

Auth Method와 Policy로 접근 범위를 통제합니다.

KV 저장뿐 아니라 Database Dynamic Credential과 PKI 인증서 발급도 Secret Engine으로 구성할 수 있습니다.

```text
Client / Workload
        │  authenticate
        v
Auth Method ──▶ Token / Identity
        │
        │  request Secret path
        v
Policy ──▶ allow / deny
        │
        v
Secret Engine ──▶ KV / Database / PKI
        │
        v
Barrier ──▶ encrypted Storage Backend
```

| 구성요소      | 핵심 역할                                                  |
|---------------|------------------------------------------------------------|
| Auth Method   | Client의 신원을 확인하고 Token 또는 Identity를 발급합니다. |
| Policy        | 경로별 capability로 허용·거부 동작을 결정합니다.           |
| Secret Engine | KV 저장, Database Credential, PKI 인증서를 처리합니다.     |
| Lease         | 동적 Credential의 TTL·갱신·폐기를 추적합니다.              |
| Barrier       | Storage에 기록되는 Vault 데이터를 암호화·복호화합니다.     |
| Seal          | Unseal 전까지 암호화 데이터 접근을 차단합니다.             |

> Secret Engine: Vault의 특정 경로에서 Secret을 저장하거나 동적으로 생성하는 플러그인 단위입니다. Engine 종류에 따라 KV 데이터, DB Credential, X.509 인증서처럼 처리 방식이 달라집니다.

🟡 자체 운영 Vault는 Secret 외에 HA, Storage, Backup, Unseal, Audit, Upgrade도 운영해야 합니다.

개발용 단일 노드와 운영용 구성은 같은 기준으로 취급하지 않습니다.

## 2. 핵심 구성요소

```text
Client / Ansible / CI
        │
        │  Auth Method
        v
  Vault API + TLS Listener
        │
        ├── Policy       path + capability authorization
        ├── Secret Engine KV / Database / PKI
        ├── Lease        TTL + renewal + revoke
        ├── Audit        request and response metadata
        └── Storage      encrypted data + HA backend
```

### Vault Server와 Listener

Vault Server는 API 요청을 받아 인증·Policy·Secret Engine을 처리합니다.

Listener는 API와 Cluster 통신을 수신하므로 주소·포트·TLS·방화벽을 함께 설계합니다.

- API 접근과 Cluster 통신의 주소·포트를 구분합니다.
- 필요한 사설 네트워크에서만 접근하도록 제한합니다.
- 운영 환경에서 평문 HTTP와 전체 인터페이스 노출을 기본값으로 사용하지 않습니다.

### Storage

Storage는 암호화된 Vault 데이터를 보관합니다.

개발용 단일 노드와 운영용 HA Storage는 가용성·복구·백업 요구가 다릅니다.

Storage는 Barrier 밖의 비신뢰 영역이므로 Vault는 기록 전에 데이터를 암호화합니다.

- Storage 장애가 Secret API 장애로 이어지는 범위를 평가합니다.
- Backup Snapshot의 암호화·보존·복구 권한을 분리합니다.
- 동일한 장애 도메인에 원본과 Backup을 함께 두지 않습니다.

### Seal·Unseal

Vault는 시작 후 Seal 상태에서 암호화된 데이터를 복호화하거나 일반적인 Secret API 요청을 처리할 수 없습니다. 물리 Storage 접근과 상태 확인·Unseal 작업은 가능합니다.

수동 Unseal 또는 KMS 기반 자동 Unseal을 선택합니다. Unseal 자료와 복구 권한은 분리 보관해야 합니다.

Seal·Unseal의 내부 동작은 [3장](#3-barrier와-shamir-secret-sharing)에서 다룹니다.

> Seal·Unseal: Vault의 암호화 데이터 접근을 잠그거나 해제하는 운영 상태입니다. 서버가 실행 중이어도 Seal 상태에서는 일반적인 Secret 읽기·쓰기를 수행할 수 없습니다.

### Auth Method와 Policy

Auth Method는 Client가 누구인지 확인하고 Token 또는 Identity를 발급합니다. Policy는 인증된 주체가 어떤 경로에서 어떤 capability를 수행할 수 있는지 제한합니다.

- 사람·Ansible·CI/CD·애플리케이션의 Auth 주체를 분리합니다.
- Policy는 기본적으로 접근을 허용하지 않으며, 필요한 path와 capability만 명시적으로 부여합니다.
- Root Token은 초기 설정 또는 비상 절차 외의 일반 자동화에 사용하지 않습니다.
- Policy는 전체 경로 권한 대신 서비스·환경·동작 단위로 작성합니다.

### Audit

Audit은 Vault 요청과 응답의 메타데이터를 기록하여 누가 언제 어떤 경로에 접근했는지 조사할 수 있도록 합니다. Secret 값과 Token이 로그에 남지 않는지 별도로 검증해야 합니다.

> ACL(Access Control List): 인증된 주체가 어떤 경로에 어떤 동작을 수행할 수 있는지 정의하는 권한 목록입니다. Vault의 Policy는 ACL 형태로 평가되며, Audit Device와 Auth Method의 설정 변경도 이 ACL 시스템의 보호를 받습니다.

## 3. Barrier와 Shamir Secret Sharing

이 장은 Vault가 데이터를 어떻게 암호화하고, Seal 상태에서 어떻게 벗어나는지 내부 동작을 설명합니다. 운영 절차가 아니라 원리 이해를 목적으로 합니다.

### Barrier — 암호화 계층

Barrier는 Vault Core와 Storage Backend 사이에 위치하는 암호화 계층입니다.

Storage Backend는 Barrier 밖의 비신뢰 영역입니다. Vault는 Storage에 기록하기 전에 모든 데이터를 암호화합니다.

```text
Vault Core (processes requests only when unsealed)
        │
        │  plaintext read/write
        v
┌───────────────────────────────┐
│  Barrier (encryption layer)   │   encrypts/decrypts Vault data
└───────────────────────────────┘
        │
        │  ciphertext only
        v
Storage Backend (untrusted, stores encrypted data only)
```

- Vault Core는 Barrier 안쪽에서만 평문 데이터를 다룹니다.
- Storage Backend가 손상되어도 공격자는 암호화된 데이터만 확인할 수 있습니다.
- Storage는 서버 재시작 후에도 데이터를 유지하는 영속 계층 역할만 수행하며, 암호화·복호화 책임은 지지 않습니다.

### Encryption Key와 Root Key

Encryption Key는 Barrier가 실제 Vault 데이터를 암호화·복호화할 때 사용하는 키입니다.

Encryption Key는 다른 Vault 데이터와 함께 Storage에 저장되지만, Root Key로 다시 암호화되어 있어 그대로 사용할 수 없습니다.

```text
Unseal Key(s)
    │  Shamir reconstruction
    v
Root Key            ← encrypted by Unseal Key, stored in Storage
    │  decrypt
    v
Encryption Key       ← used to encrypt/decrypt actual Vault data
    │
    v
Vault data (KV, Policy, Auth config, ...)
```

> Root Key: Encryption Key를 보호하는 상위 키입니다. Root Key 자체도 Storage에 저장되지만 Unseal Key로 암호화된 상태이므로, Unseal Key 없이는 복호화할 수 없습니다.

### Shamir's Secret Sharing

Vault는 기본적으로 Unseal Key를 Shamir's Secret Sharing 알고리즘으로 여러 share로 분할합니다.

`key-shares`만큼 share를 생성하고, `key-threshold` 이상을 모아야 원래 키를 재구성할 수 있습니다.

```text
operator init (default: shares=5, threshold=3)

Unseal Key generated
        │
        │  Shamir split
        v
┌───────┬───────┬───────┬───────┬───────┐
│ share1│ share2│ share3│ share4│ share5│   split into 5 shares
└───────┴───────┴───────┴───────┴───────┘
        │
        │  any 3 or more combined
        v
   share1 + share3 + share5  ──▶  Unseal Key reconstructed
   share1 + share2           ──▶  reconstruction fails (below threshold)
```

- 조각 하나만 유출되어도 Unseal Key를 복원할 수 없습니다. threshold 개수 이상이 모여야 위협이 됩니다.
- 운영자 여러 명에게 조각을 분산 보관시키면, 한 명의 단독 판단으로 Unseal할 수 없는 구조를 만들 수 있습니다.
- threshold에 필요한 조각을 잃으면 해당 Shamir Seal로 Root Key를 복원할 수 없습니다. Snapshot만으로 복구된다고 가정하지 말고, Unseal Key 또는 Auto Unseal용 Seal Mechanism의 백업·복구 절차를 별도로 검증해야 합니다. Seal Mechanism이 영구적으로 삭제되면 Snapshot이 있어도 클러스터를 복구할 수 없습니다.

> Shamir's Secret Sharing: 하나의 비밀 값을 여러 조각으로 나누고, 정해진 개수 이상을 모아야만 원본을 복원할 수 있게 하는 비밀 분산 알고리즘입니다. 조각 일부만으로는 원본에 대한 정보를 얻을 수 없습니다.

### Auto Unseal과의 차이

Auto Unseal에서는 외부 KMS·HSM이 Root Key 복호화를 대행하므로 Shamir 조각을 사람이 직접 입력하지 않습니다.

Auto Unseal에서는 내부 Recovery Key를 Shamir Secret Sharing으로 share 분할하며, 평상시 Unseal 절차에는 Shamir share를 사용하지 않습니다.

| 방식        | Unseal 주체              | Shamir 사용 시점            | 복구 키 이름 |
|-------------|--------------------------|-----------------------------|--------------|
| Shamir Seal | 운영자가 조각 직접 입력  | 매 Unseal 시                | Unseal Key   |
| Auto Unseal | 외부 KMS/HSM이 자동 처리 | 초기화 시 Recovery Key 생성 | Recovery Key |

🟡 Auto Unseal 구성에서 KMS 키가 영구 삭제되면 Root Key를 복호화할 방법이 없어 데이터를 복구할 수 없습니다. KMS 키 삭제 방지·백업 정책을 Vault 운영 절차와 함께 검토해야 합니다.

## 4. Secret 수명주기

Secret 관리는 저장만으로 끝나지 않고 다음 흐름 전체를 포함합니다.

```text
Classify
   │
   v
Store or Issue
   │
   v
Authenticate + Authorize
   │
   v
Read at runtime
   │
   v
Lease / Rotate / Revoke
   │
   v
Audit + Backup + Destroy
```

### 분류

- 정적 설정값: KV Secret Engine 적용 여부와 Rotation 주기를 결정합니다.
- Database Credential: 동적 발급·TTL·Lease·DB 권한 범위를 함께 설계합니다.
- 인증서: 발급자·유효기간·갱신·폐기·신뢰 배포를 PKI workflow로 정의합니다.
- 운영 자격증명: 소유자·사용 서비스·접근 경로·비상 폐기 절차를 기록합니다.

### Runtime 접근

애플리케이션과 Ansible은 Secret을 이미지·Git·평문 변수 파일에 포함하지 않고 실행 시점에 가져옵니다.

- 요청 주체가 먼저 Auth Method로 인증합니다.
- Policy가 요청 경로와 capability를 허용하는지 확인합니다.
- Secret은 필요한 시점에만 메모리 또는 보호된 임시 경로로 전달합니다.
- 로그·Debug 출력·Ansible facts·Artifact·Cache에 값이 남지 않는지 확인합니다.

### Rotation과 Revoke

Rotation은 새 Credential을 발급하고 사용 주체를 전환한 뒤 이전 Credential을 폐기하는 절차입니다.

Dynamic Secret은 발급된 Credential의 만료·폐기와 갱신 실패를 처리해야 합니다.

> Lease: Vault가 발급한 동적 Credential의 유효기간과 갱신·폐기 정보를 추적하는 단위입니다. Lease 만료가 실제 애플리케이션 연결 종료까지 보장하는지는 대상 시스템별로 검증해야 합니다.

## 5. 인증과 Policy

### 인증 계층

인증 방식은 실행 환경과 신뢰 가능한 외부 Identity에 따라 선택합니다.

- AWS 환경: AWS IAM 기반 Auth를 우선 검토합니다.
- Kubernetes 환경: ServiceAccount Identity 기반 Auth를 검토합니다.
- CI/CD: OIDC 또는 짧은 TTL의 workload identity를 우선 검토합니다.
- 외부 Identity 연계가 어려운 경우: AppRole을 제한된 대안으로 검토합니다.
- 사람용 접근: 조직의 승인된 사용자 인증과 MFA·접근기록 정책을 연결합니다.

장기 Root Token이나 공유 Token을 애플리케이션 설정에 고정하는 방식은 사용하지 않습니다.

인증부터 Secret 응답까지의 요청 흐름은 다음과 같습니다.

```text
Client
   │  1. authenticate (AWS IAM / K8s SA / OIDC / AppRole, etc.)
   v
Auth Method
   │  2. verify identity, issue Token
   v
Client (holds Token)
   │  3. request Secret path with Token
   v
Policy evaluation
   │  4. check path + capability bound to the Token's Policy
   ├── deny (default) ──▶ 403 response
   └── allow ──▶ Secret Engine reads/issues value ──▶ response to Client
```

> AppRole: 사람이 아닌 애플리케이션·자동화 도구가 Role ID와 Secret ID로 인증하는 Auth Method입니다. AWS IAM이나 Kubernetes ServiceAccount처럼 신뢰 가능한 외부 Identity가 없을 때 제한된 대안으로 사용합니다.

### Policy 설계

Policy는 다음 질문에 답할 수 있어야 합니다.

- 어떤 주체가 접근합니까?
- 어떤 환경과 서비스 경로입니까?
- `read`, `create`, `update`, `delete`, `list` 중 무엇이 필요합니까?
- Token의 TTL과 갱신 범위는 얼마입니까?
- 접근이 끝났을 때 어떻게 폐기합니까?

예시 경로는 실제 Secret 값 없이 다음처럼 설계합니다.

```text
secret/data/dev/app
secret/data/stg/app
secret/data/prd/app
```

환경별 접근 주체와 Policy를 분리하고, 개발 주체가 운영 경로를 조회하지 못하도록 명시적으로 거부·검증합니다. capability는 HTTP 메서드에 대략 대응하지만, 실제 권한 요구사항은 Endpoint와 Secret Engine별 공식 문서를 확인해야 합니다. 예를 들어 Database Secret Engine의 Credential 발급은 GET 요청이므로 `read` capability가 필요합니다. 또한 많은 Endpoint에서는 초기 생성에도 `create`와 `update`가 함께 필요할 수 있습니다.

| Capability | 대응 동작       | 설명                                                                         |
|------------|-----------------|------------------------------------------------------------------------------|
| `create`   | POST/PUT (생성) | 해당 경로에 새 데이터를 생성합니다. 많은 API에서 `update`와 함께 필요합니다. |
| `read`     | GET             | 해당 경로의 데이터를 조회할 수 있습니다.                                     |
| `update`   | POST/PUT (갱신) | 기존 데이터를 변경하며, 일부 API에서는 초기 생성도 포함합니다.               |
| `patch`    | PATCH           | 기존 데이터의 일부 필드를 변경할 수 있습니다.                                |
| `delete`   | DELETE          | 데이터를 삭제할 수 있습니다.                                                 |
| `list`     | LIST            | 경로 하위 키 목록을 조회할 수 있습니다.                                      |
| `deny`     | 없음            | 다른 capability와 무관하게 접근을 차단합니다.                                |

🟡 `deny`는 다른 Policy가 동일 경로에 더 넓은 권한을 허용하더라도 항상 우선합니다. 여러 Policy가 겹치는 경로에서는 `deny`가 있는지 먼저 확인해야 합니다.

## 6. Secret Engine

### KV Secret Engine

Key/Value 형태의 정적 Secret을 저장합니다. 버전 관리가 필요한 경우 데이터 버전·삭제·복구·영구 삭제의 차이를 운영 절차에 반영합니다.

- mount path와 환경·서비스별 naming을 정합니다.
- Secret 값과 Metadata의 접근 권한을 구분합니다.
- 변경 이력과 폐기 기준을 정합니다.

KV v2는 삭제 시 실제 데이터를 즉시 지우지 않고 버전 상태만 전환합니다.

| 명령                       | 동작                         | 데이터 상태                       |
|----------------------------|------------------------------|-----------------------------------|
| `vault kv delete`          | 최신 버전을 soft delete 처리 | 데이터 보존, undelete로 복구 가능 |
| `vault kv undelete`        | soft delete된 버전을 복구    | 삭제 전 상태로 되돌아감           |
| `vault kv destroy`         | 지정 버전을 영구 삭제        | 복구 불가                         |
| `vault kv metadata delete` | 모든 버전과 Metadata를 삭제  | 복구 불가                         |

> soft delete: 데이터를 즉시 제거하지 않고 삭제된 것으로 표시만 하는 방식입니다. 실수로 삭제한 경우 `undelete`로 복구할 여지를 남깁니다.

### Database Secret Engine

Database Secret Engine은 데이터베이스에 임시 Credential을 발급하는 동적 방식입니다.

```text
Client
   │  1. request database/creds/<role>
   v
Vault (Database Secret Engine)
   │  2. connect to DB with registered admin credential
   │  3. execute creation_statements defined in Role
   v
Database
   │  4. create new user (short TTL)
   v
Client ◀── 5. returns issued Credential + Lease
```

- Vault가 데이터베이스에 연결할 관리자 권한의 범위를 제한합니다.
- 생성 SQL·권한·TTL·Max TTL·Revoke 동작을 검증합니다.
- 애플리케이션 Connection Pool이 Credential 만료를 처리하는지 확인합니다.
- Static Role은 기존 DB 계정의 비밀번호를 주기적으로 Rotation하는 방식이며, Root Credential 자체에는 사용하지 않습니다.

### PKI Secret Engine

PKI Secret Engine은 인증서 발급과 갱신 workflow를 자동화할 수 있는 영역입니다.

- Root CA와 Intermediate CA의 역할을 분리합니다.
- 발급 가능한 SAN·TTL·Role 범위를 제한합니다.
- 인증서 갱신 실패와 폐기·신뢰 배포 절차를 운영합니다.
- TTL을 짧게 유지하면 폐기(Revocation) 필요성과 CRL 크기가 줄어들어 대규모 발급에 유리합니다.

## 7. 운영 모델

### 개발 환경

개발 환경은 실제 운영 Secret과 분리하고, 표준 placeholder와 폐기 가능한 데이터를 사용합니다.

- 단일 노드는 개념·연동·기본 복구 검증에 사용합니다.
- 개발용 Storage와 운영용 Storage를 공유하지 않습니다.
- 개발 환경에서 평문 Listener나 Dev Mode를 사용하더라도 운영 기준으로 승격하지 않습니다.

### 운영 환경

운영 환경은 다음 운영요소를 함께 설계해야 합니다.

- TLS 인증서 발급·갱신·폐기.
- HA와 Storage 장애 도메인.
- Seal·Unseal 또는 KMS 자동 Unseal.
- Audit 로그 보존·접근·알림.
- Snapshot Backup·Restore와 RTO·RPO.
- 버전 고정·취약점 대응·Upgrade·Rollback.
- Secret Rotation과 Dynamic Credential Lease 만료.

### 자체 운영 판단

Vault를 선택하면 관리형 Secret Store보다 더 많은 운영 책임이 생깁니다. 다음 조건이 있는 경우 도입 타당성을 검토할 수 있습니다.

- 온프레미스·멀티클라우드 환경을 통합해야 합니다.
- Database Dynamic Secret이나 PKI가 핵심 요구사항입니다.
- 중앙 Policy·Audit·Auth 연계가 필요합니다.
- Storage·HA·Backup·Unseal을 운영할 담당자와 절차가 있습니다.

AWS 단일 환경에서 일반 Secret만 관리한다면 AWS Secrets Manager의 IAM 통합·운영 부담·비용을 함께 비교합니다.

## 8. 도입 판단 기준

다음 기준을 만족하지 못하면 Vault 설치보다 요구사항과 운영 책임을 먼저 정리합니다.

- [ ] 운영 환경과 개발 환경이 분리됩니다.
- [ ] 실제 운영 Secret을 저장할 필요성과 대상이 확정됩니다.
- [ ] Auth Method와 최소 권한 Policy가 정의됩니다.
- [ ] TLS와 네트워크 접근 범위가 정의됩니다.
- [ ] Seal·Unseal 또는 자동 Unseal 복구가 검증됩니다.
- [ ] Audit·Backup·Restore·Upgrade 절차가 있습니다.
- [ ] Ansible·CI/CD·애플리케이션 로그에 Secret이 노출되지 않습니다.
- [ ] RTO·RPO, 비용, 운영 담당자, 라이선스 검토가 완료됩니다.

## 9. 관련 문서

- 설치·초기화·TLS 절차: [HashiCorp Vault 설치 가이드](vault_install.md)
- Secret Store 비교와 위협 모델: [시크릿 관리](secret_management.md)
- 공식 문서 검증 노트: [_reference/hashicorp_vault_official_notes.md](../../_reference/hashicorp_vault_official_notes.md)

## 10. 용어 정리

| 용어                       | 정의                                                                                                |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| Barrier                    | Vault Core와 Storage Backend 사이의 암호화 계층입니다.                                              |
| Seal / Unseal              | Vault의 암호화 데이터 접근을 잠그거나 해제하는 상태와 절차입니다.                                   |
| Shamir Secret Sharing      | Unseal Key를 여러 share로 나누고 threshold 이상을 모아야 복원하는 방식입니다.                       |
| Key Share / Threshold      | 분할된 Unseal Key 조각과 복원에 필요한 최소 조각 수입니다.                                          |
| Root Key                   | 실제 데이터 암호화에 사용하는 Encryption Key를 보호하는 상위 키입니다.                              |
| Encryption Key             | Vault 데이터를 암호화·복호화하는 키입니다.                                                          |
| Recovery Key               | Auto Unseal 환경에서 특정 관리자 작업을 승인하는 키입니다. Root Key를 직접 복호화하지 않습니다.     |
| Auth Method                | Client의 신원을 확인하고 Token 또는 Identity를 발급하는 인증 방식입니다.                            |
| Root Token                 | 모든 경로에 접근 가능한 Token입니다. 초기 설정·비상 절차 외의 일반 자동화에는 사용하지 않습니다.    |
| AppRole                    | 애플리케이션이 Role ID와 Secret ID로 인증하는 Auth Method입니다.                                    |
| Policy Capability          | 특정 Vault 경로에서 허용하는 `read`, `create`, `update`, `patch`, `delete`, `list` 등의 동작입니다. |
| Secret Engine / Mount Path | Secret을 저장·발급하는 기능과 그 기능이 연결된 Vault 경로입니다.                                    |
| Lease / TTL                | 동적 Credential의 유효기간과 갱신·폐기를 추적하는 단위와 기간입니다.                                |
| Dynamic Secret             | 요청 시 생성되고 Lease 만료 또는 폐기 시 사용이 끝나는 임시 Credential입니다.                       |
| KV v2 Soft Delete          | 버전 데이터를 즉시 제거하지 않고 삭제 상태로 표시해 복구할 수 있게 하는 동작입니다.                 |
| PKI Role / SAN             | 인증서 발급 조건과 인증서에 허용되는 주체 이름 범위입니다.                                          |
| Root CA / Intermediate CA  | PKI Secret Engine에서 인증서 신뢰 체계의 최상위·중간 발급자입니다.                                  |
| CRL                        | 폐기된 인증서 목록(Certificate Revocation List)입니다.                                              |
| Audit Device               | Vault 요청·응답의 감사 메타데이터를 기록하는 출력 장치입니다.                                       |
| HA (High Availability)     | 여러 노드로 장애를 견디도록 구성하는 고가용성 방식입니다.                                           |
| HSM                        | Root Key 복호화를 대행할 수 있는 하드웨어 기반 보안 장치입니다.                                     |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HashiCorp Vault 공식 문서: [developer.hashicorp.com/vault/docs/what-is-vault](https://developer.hashicorp.com/vault/docs/what-is-vault) — ★★★☆☆
- Ansible Vault Guide: [docs.ansible.com](https://docs.ansible.com/ansible/latest/vault_guide/) — ★★★☆☆
- Vault Architecture (Barrier·Seal 내부 동작): [developer.hashicorp.com/vault/docs/internals/architecture](https://developer.hashicorp.com/vault/docs/internals/architecture) — ★★★☆☆
- Vault Seal/Unseal: [developer.hashicorp.com/vault/docs/concepts/seal](https://developer.hashicorp.com/vault/docs/concepts/seal) — ★★★☆☆
- Vault Production Hardening: [developer.hashicorp.com/vault/docs/concepts/production-hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) — ★★★☆☆
- Vault Policies: [developer.hashicorp.com/vault/docs/concepts/policies](https://developer.hashicorp.com/vault/docs/concepts/policies) — ★★★☆☆
- Vault KV Secret Engine: [developer.hashicorp.com/vault/docs/secrets/kv](https://developer.hashicorp.com/vault/docs/secrets/kv) — ★★★☆☆
- Vault Database Secret Engine: [developer.hashicorp.com/vault/docs/secrets/databases](https://developer.hashicorp.com/vault/docs/secrets/databases) — ★★★☆☆
- Vault PKI Secret Engine: [developer.hashicorp.com/vault/docs/secrets/pki](https://developer.hashicorp.com/vault/docs/secrets/pki) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-20

**마지막 업데이트**: 2026-08-21

© 2026 siasia86. Licensed under CC BY 4.0.
