---
name: hashicorp-vault-official-notes
description: HashiCorp Vault의 중앙 Secret 관리·KV·Database Dynamic Secret·라이선스 공식 문서 검증 노트.
tags:
  - vault
  - secrets
  - dynamic-secrets
  - hybrid
last_checked: 2026-08-20
sources:
  - https://developer.hashicorp.com/vault/docs/what-is-vault
  - https://developer.hashicorp.com/vault/docs/secrets/kv
  - https://developer.hashicorp.com/vault/docs/secrets/databases
  - https://developer.hashicorp.com/vault/docs/secrets/pki
  - https://developer.hashicorp.com/vault/docs/concepts/production-hardening
  - https://raw.githubusercontent.com/hashicorp/vault/main/LICENSE
---

# HashiCorp Vault 공식 문서 참조 노트

## 1. 서비스 목적

- Vault는 온프레미스·클라우드·하이브리드 환경에서 중앙 Secret 관리와 권한 있는 접근 관리를 제공합니다.
- 모듈형 구조와 Plugin 생태계를 통해 기존 시스템과 통합할 수 있습니다.

## 2. Secret Engine

- KV Secret Engine은 Key/Value 형태의 Secret 저장에 사용합니다.
- Database Secret Engine은 데이터베이스 계정과 Credential을 동적으로 발급하는 용도로 사용할 수 있습니다.
- 동적 Credential은 TTL과 Lease 정책을 함께 설계해야 합니다.

## 3. 적용 범위

- AWS 단일 환경에서 일반 Secret만 관리할 때는 AWS Secrets Manager와 운영 부담을 비교합니다.
- 온프레미스·멀티클라우드·Dynamic Secret·PKI가 필요할 때 Vault를 검토할 수 있습니다.
- Vault를 자체 운영하면 HA, Storage, Backup, Unseal, Audit, Upgrade를 별도로 관리해야 합니다.

## 4. 라이선스 확인

- HashiCorp Vault upstream repository의 `LICENSE`는 Vault Version 1.15.0 이상에 대해
  Business Source License 1.1과 Additional Use Grant를 규정합니다.
- 조직 내부 사용이 경쟁형 유료 호스팅 제공에 해당하지 않는지 현재 라이선스 원문과 법무 기준으로 확인합니다.
- HCP Vault와 Vault Enterprise의 제공 범위·요금은 별도 확인이 필요합니다.
