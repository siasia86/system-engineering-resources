---
name: external-secrets-official-notes
description: External Secrets Operator v2.15.0 판, 지원 정책, 공급자 안정도, creationPolicy·deletionPolicy, 클라우드 CSI 도구, kind 시험 결과 정리.
tags:
  - external-secrets
  - kubernetes
  - secrets
last_checked: 2026-11-27
sources:
  - https://github.com/external-secrets/external-secrets/releases
  - https://external-secrets.io/latest/introduction/stability-support/
  - https://external-secrets.io/latest/api/externalsecret/
  - https://secrets-store-csi-driver.sigs.k8s.io/
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html
  - https://docs.cloud.google.com/secret-manager/docs/secret-manager-managed-csi-component
  - https://learn.microsoft.com/en-us/azure/aks/csi-secrets-store-driver
  - https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
---

# External Secrets Operator 공식 자료 참조 노트

## 1. 판과 지원 (2026-11-27 확인)

- 최신 v2.15.0(2026-11-10, Helm 차트 2.15.0), 이전 v2.14.0(10-23). 라이선스 Apache-2.0.
- "external-secrets only supports the most-up-to date, current minor version." 표: 2.15·2.14 → Kubernetes 1.37, 2.13~2.9 → 1.36.
- Deprecation Policy: "The project is currently in `beta` state." 예시 API는 `external-secrets.io/v1`(ExternalSecret), PushSecret은 `v1alpha1`.
- 공급자 안정도: stable(AWS Secrets Manager, AWS Parameter Store, Akeyless, Azure Keyvault, CyberArk, GCP Secret Manager, HashiCorp Vault, IBM Cloud, Oracle Vault, Previder), beta(Kubernetes, SecretServer), 그 밖 alpha. Fake는 표에 없음.

## 2. ExternalSecret

- `target.creationPolicy`: Owner(기본, ownerReferences), Merge(Secret이 있어야 함), Orphan, None(예약). 본문에 CreateOrMerge 언급이 있으나 enum 목록에는 없음.
- `target.deletionPolicy`: Retain(기본), Delete, Merge.
- `refreshInterval` 0이면 한 번만. `refreshPolicy` 기본 Periodic(CreatedOnce, OnChange).
- PushSecret 문서: Kubernetes Secret 데이터를 외부 저장소로 밀어 넣는 대상을 정함("what data should be pushed to the secret provider").

## 3. CSI Driver와 클라우드

- Secrets Store CSI Driver: 외부 저장소 값을 pod 볼륨으로. "Sync with Kubernetes Secrets"는 alpha. 공급자 Akeyless, AWS, Azure, Conjur, GCP, OpenBao, Vault.
- AWS ASCP: 문서 제목 IRSA 기준, "The ASCP retrieves the Amazon EKS Pod Identity and exchanges it for an IAM role." 언급.
- GKE Secret Manager 애드온: 드라이버 `secrets-store-gke.csi.k8s.io`, Kubernetes Secret 동기화 미지원, 회전 `--enable-secret-manager-rotation`(기본 120초, 최소 60초, GKE 1.32.2-gke.1059000 이상). GA 여부 표기 없음.
- AKS 애드온 `azure-keyvault-secrets-provider`: Kubernetes Secret 동기화, 자동 회전 지원(예시 출력 `enableSecretRotation` false, `rotationPollInterval` 2m). subPath 마운트는 회전 반영 안 됨.
- Kubernetes 저장 암호화(요약 근거): "By default, the API server stores plain-text representations of resources into etcd, with no at-rest encryption." KMS v2는 1.29부터 stable.

## 4. kind 시험 (2026-11-27, Kubernetes v1.37.0, Helm v3.19.2)

- Helm 설치: Deployment 3개(external-secrets, cert-controller, webhook), CRD 25개.
- Fake ClusterSecretStore `Valid`, ExternalSecret `SecretSynced`, Secret ownerReference ExternalSecret.
- 저장소 값 변경 → refreshInterval 10s 안에 Secret 갱신. 경고 `store fake isn't currently maintained`.
- 없는 property: `SecretSyncedError: could not get secret data from provider`, Secret은 마지막 값 유지.
- ExternalSecret 삭제 → Secret 삭제(Owner).
- 미실행: 클라우드 공급자, PushSecret, CSI Driver.
