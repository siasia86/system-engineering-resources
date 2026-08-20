# HashiCorp Vault 개념
<!-- reference: _reference/hashicorp_vault_official_notes.md -->

HashiCorp Vault는 온프레미스·클라우드·하이브리드 환경에서 Secret을 중앙 관리하고, 인증된 주체에 필요한 권한만 부여하는 서비스입니다. 이 문서는 설치 명령보다 구성요소·보안 경계·Secret 수명주기·도입 판단을 설명합니다.

`Ansible Vault`는 파일 또는 변수값을 암호화하는 도구이고, HashiCorp Vault는 실행 시점에 Secret을 제공하고 접근을 통제하는 서비스입니다.

## 목차

| 단계 | 섹션                                                                                                                   |
|------|------------------------------------------------------------------------------------------------------------------------|
| 기본 | [1. 목적과 범위](#1-목적과-범위) / [2. 도구 간 역할](#2-도구-간-역할) / [3. 핵심 구성요소](#3-핵심-구성요소)           |
| 설계 | [4. Secret 수명주기](#4-secret-수명주기) / [5. 인증과 Policy](#5-인증과-policy) / [6. Secret Engine](#6-secret-engine) |
| 운영 | [7. 운영 모델](#7-운영-모델) / [8. 도입 판단 기준](#8-도입-판단-기준) / [9. 관련 문서](#9-관련-문서)                   |
| 참고 | [10. 참고 자료](#10-참고-자료)                                                                                         |

---

## 1. 목적과 범위

이 문서는 다음 질문에 답하기 위해 작성합니다.

- HashiCorp Vault가 Ansible Vault와 무엇이 다른지 설명합니다.
- Secret 저장·발급·사용·회수 흐름을 구성요소 단위로 이해합니다.
- 정적 KV Secret과 동적 Credential·PKI의 적용 범위를 구분합니다.
- 자체 운영에 필요한 TLS, Storage, Seal·Unseal, Audit, Backup, Upgrade를 식별합니다.
- AWS Secrets Manager와 비교하여 Vault 도입이 필요한 조건을 판단합니다.

다음 항목은 이 문서의 범위가 아닙니다.

- 운영 환경에 바로 적용할 설치 명령 실행.
- 실제 비밀번호, Token, Unseal Key, Client Certificate 저장.
- 특정 조직의 법무·비용·컴플라이언스 결론.

🟡 Vault를 자체 운영하면 Secret 기능뿐 아니라 HA, Storage, Backup, Unseal, Audit, Upgrade까지 운영해야 합니다. 개발용 단일 노드와 운영용 구성은 같은 기준으로 취급하지 않습니다.

## 2. 도구 간 역할

### Ansible Vault

Ansible playbook과 변수 파일에 포함된 민감 정보를 암호화합니다. Git에 암호화 파일을 보관하고, 실행 시 Vault Password로 복호화하는 파일 중심 방식입니다.

- 장점: Ansible과의 결합이 간단하고 추가 서버가 필요하지 않습니다.
- 한계: 실행 주체 인증, 중앙 감사, 동적 Credential 발급, 자동 Rotation을 별도로 설계해야 합니다.

### HashiCorp Vault

실행 주체가 인증한 뒤 Policy에 허용된 Secret을 API로 가져가는 중앙 서비스입니다. Secret을 저장하는 KV Engine뿐 아니라 Database Credential 발급, PKI 인증서 발급 등 동적 기능을 제공할 수 있습니다.

- 장점: 중앙 Policy, Audit, TTL·Lease, Dynamic Secret, 다양한 Auth Method를 구성할 수 있습니다.
- 한계: Vault Server, Storage, TLS, Seal·Unseal, Backup·Restore, HA와 Upgrade를 운영해야 합니다.

### AWS Secrets Manager

AWS 단일 환경에서 Secret 저장·접근 제어·Rotation을 관리형 서비스로 제공하는 선택지입니다. AWS 밖의 시스템, 멀티클라우드, Vault Plugin·Dynamic Secret·PKI 요구가 없다면 운영 부담과 비용을 비교해야 합니다.

> Dynamic Secret: 요청 시점에 짧은 유효기간의 Credential을 발급하고, Lease 만료 또는 폐기 시 사용을 끝내는 방식입니다. 정적으로 오래 보관하는 Password와 위협 모델이 다릅니다.

## 3. 핵심 구성요소

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

Vault Server는 API 요청을 받고 인증·Policy·Secret Engine을 처리합니다. Listener는 API와 Cluster 통신을 수신하므로 주소·포트·TLS·방화벽 범위를 함께 설계해야 합니다.

- API 접근과 Cluster 통신의 주소·포트를 구분합니다.
- 필요한 사설 네트워크에서만 접근하도록 제한합니다.
- 운영 환경에서 평문 HTTP와 전체 인터페이스 노출을 기본값으로 사용하지 않습니다.

### Storage

Storage는 암호화된 Vault 데이터를 보관합니다. 개발용 단일 노드와 운영용 HA Storage의 가용성·복구·백업 요구는 다릅니다.

- Storage 장애가 Secret API 장애로 이어지는 범위를 평가합니다.
- Backup Snapshot의 암호화·보존·복구 권한을 분리합니다.
- 동일한 장애 도메인에 원본과 Backup을 함께 두지 않습니다.

### Seal·Unseal

Vault는 시작 후 암호화된 데이터에 접근하기 전에 Seal 상태를 해제해야 합니다. 수동 Unseal 또는 KMS 기반 자동 Unseal을 선택하며, Unseal 자료와 복구 권한의 분리 보관이 필요합니다.

> Seal·Unseal: Vault의 암호화 데이터 접근을 잠그거나 해제하는 운영 상태입니다. 서버가 실행 중이어도 Seal 상태에서는 일반적인 Secret 읽기·쓰기를 수행할 수 없습니다.

### Auth Method와 Policy

Auth Method는 Client가 누구인지 확인하고 Token 또는 Identity를 발급합니다. Policy는 인증된 주체가 어떤 경로에서 어떤 capability를 수행할 수 있는지 제한합니다.

- 사람·Ansible·CI/CD·애플리케이션의 Auth 주체를 분리합니다.
- Policy는 기본적으로 접근을 허용하지 않으며, 필요한 path와 capability만 명시적으로 부여합니다.
- Root Token은 초기 설정 또는 비상 절차 외의 일반 자동화에 사용하지 않습니다.
- Policy는 전체 경로 권한 대신 서비스·환경·동작 단위로 작성합니다.

### Audit

Audit은 Vault 요청과 응답의 메타데이터를 기록하여 누가 언제 어떤 경로에 접근했는지 조사할 수 있도록 합니다. Secret 값과 Token이 로그에 남지 않는지 별도로 검증해야 합니다.

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

Rotation은 새 Credential을 발급하고 사용 주체를 전환한 뒤 이전 Credential을 폐기하는 절차입니다. Dynamic Secret은 발급된 Credential의 만료·폐기와 갱신 실패를 처리해야 합니다.

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

환경별 접근 주체와 Policy를 분리하고, 개발 주체가 운영 경로를 조회하지 못하도록 명시적으로 거부·검증합니다.

## 6. Secret Engine

### KV Secret Engine

Key/Value 형태의 정적 Secret을 저장합니다. 버전 관리가 필요한 경우 데이터 버전·삭제·복구·영구 삭제의 차이를 운영 절차에 반영합니다.

- mount path와 환경·서비스별 naming을 정합니다.
- Secret 값과 Metadata의 접근 권한을 구분합니다.
- 변경 이력과 폐기 기준을 정합니다.

### Database Secret Engine

Database Secret Engine은 데이터베이스에 임시 Credential을 발급하는 동적 방식입니다.

- Vault가 데이터베이스에 연결할 관리자 권한의 범위를 제한합니다.
- 생성 SQL·권한·TTL·Max TTL·Revoke 동작을 검증합니다.
- 애플리케이션 Connection Pool이 Credential 만료를 처리하는지 확인합니다.

### PKI Secret Engine

PKI Secret Engine은 인증서 발급과 갱신 workflow를 자동화할 수 있는 영역입니다.

- Root CA와 Intermediate CA의 역할을 분리합니다.
- 발급 가능한 SAN·TTL·Role 범위를 제한합니다.
- 인증서 갱신 실패와 폐기·신뢰 배포 절차를 운영합니다.

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

## 10. 참고 자료

- HashiCorp Vault 공식 문서: [developer.hashicorp.com/vault/docs/what-is-vault](https://developer.hashicorp.com/vault/docs/what-is-vault) — ★★★☆☆
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

**마지막 업데이트**: 2026-08-20

© 2026 siasia86. Licensed under CC BY 4.0.
