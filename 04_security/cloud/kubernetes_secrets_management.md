# Kubernetes 비밀값 관리 (Sealed Secrets · External Secrets · CSI Driver)
<!-- reference: _reference/sealed_secrets_official_notes.md, _reference/external_secrets_official_notes.md -->

Kubernetes Secret은 base64로 인코딩될 뿐 암호화가 아니어서 Git에 그대로 둘 수 없습니다. 이 문서는 GitOps 저장소와 클러스터에서 비밀값을 다루는 세 방식(암호화한 채 Git에 두기, 외부 비밀 저장소에서 가져오기, 볼륨으로 붙이기)을 비교하고, Sealed Secrets와 External Secrets Operator(ESO)를 시험한 절차와 결과를 정리합니다.

- 기준 판: Sealed Secrets v0.41.2 (2026-10-26), External Secrets Operator v2.15.0 (2026-11-10, Helm 차트 2.15.0) (2026-11-27 확인)
- 예제 시험: 2026-11-27 3·4절을 kind v0.33.0(Kubernetes v1.37.0)에서 실행해 Sealed Secrets 봉인·복원·범위 제한·오프라인 봉인과 ESO Fake provider 연결·갱신·오류 시 동작·삭제 연동을 확인. 클라우드 비밀 저장소(AWS·GCP·Azure·Vault)와 Secrets Store CSI Driver, etcd 저장 암호화는 계정·클러스터 설정이 필요해 미실행

## 목차

| 섹션                                                                                                                                                      |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 왜 따로 관리하나](#1-왜-따로-관리하나) / [2. 방식 비교](#2-방식-비교) / [3. Sealed Secrets](#3-sealed-secrets)                                        |
| [4. External Secrets Operator](#4-external-secrets-operator) / [5. Secrets Store CSI Driver와 클라우드 도구](#5-secrets-store-csi-driver와-클라우드-도구) |
| [6. etcd 저장 암호화](#6-etcd-저장-암호화) / [7. 고르는 기준](#7-고르는-기준) / [8. 검증](#8-검증)                                                        |
| [9. 트러블슈팅](#9-트러블슈팅) / [함께 보기](#함께-보기)                                                                                                  |

---

## 1. 왜 따로 관리하나

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db
data:
  password: <BASE64_VALUE>     # base64 -d 하면 바로 원문
```

- Secret 매니페스트를 Git에 올리면 저장소를 읽을 수 있는 모든 사람이 값을 봅니다.
- 클러스터 안에서도 Secret을 읽는 RBAC 권한이 있으면 값을 봅니다. Secret 조회 권한은 최소로 줍니다.
- Kubernetes API 서버는 기본으로 etcd에 리소스를 평문으로 저장합니다(6절).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 방식 비교

| 방식                          | 도구                                                               | Git에 두는 것               | 원본 위치              | 맞는 곳                                      |
|-------------------------------|--------------------------------------------------------------------|-----------------------------|------------------------|----------------------------------------------|
| 암호화한 채 Git에 두기        | Sealed Secrets, [SOPS](../../02_infrastructure/iac/sops.md)(+Flux) | 암호문                      | Git                    | 외부 비밀 저장소가 없음, 클러스터 수가 적음  |
| 외부 저장소에서 Secret 만들기 | External Secrets Operator                                          | 참조(어느 저장소의 어느 키) | AWS·GCP·Azure·Vault 등 | 이미 비밀 저장소가 있음, 여러 클러스터       |
| 볼륨으로 붙이기               | Secrets Store CSI Driver + 공급자                                  | 참조(SecretProviderClass)   | 외부 저장소            | Secret 객체를 만들지 않고 파일로만 쓰고 싶음 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Sealed Secrets

클러스터 안 컨트롤러가 비밀키를 갖고, 사용자는 공개키로 암호화한 `SealedSecret`을 Git에 둡니다. 컨트롤러가 이를 풀어 일반 Secret을 만듭니다.

### 3.1 설치

```bash
SSV=0.41.2
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v${SSV}/controller.yaml
kubectl -n kube-system rollout status deploy/sealed-secrets-controller

# kubeseal CLI (체크섬 대조)
curl -sSLO https://github.com/bitnami-labs/sealed-secrets/releases/download/v${SSV}/kubeseal-${SSV}-linux-amd64.tar.gz
curl -sSLO https://github.com/bitnami-labs/sealed-secrets/releases/download/v${SSV}/sealed-secrets_${SSV}_checksums.txt
grep " kubeseal-${SSV}-linux-amd64.tar.gz\$" sealed-secrets_${SSV}_checksums.txt | sha256sum -c -
sudo tar xzf kubeseal-${SSV}-linux-amd64.tar.gz -C /usr/local/bin kubeseal
```

- Helm 차트(`helm repo add sealed-secrets https://bitnami.github.io/sealed-secrets`)도 있습니다(미시험). 시험한 컨트롤러 이미지는 `docker.io/bitnami/sealed-secrets-controller:0.41.2`였습니다.

### 3.2 봉인과 적용

```bash
kubectl -n app create secret generic db \
  --from-literal=password='<DB_PASSWORD>' --dry-run=client -o yaml > db.yaml
kubeseal -f db.yaml -w db-sealed.yaml     # 암호화 (클러스터의 공개키 사용)
rm db.yaml                                 # 평문은 남기지 않음
git add db-sealed.yaml                     # 암호문만 커밋
kubectl apply -f db-sealed.yaml            # 컨트롤러가 Secret db 생성
```

- 시험에서 적용 뒤 Secret `db`가 만들어졌고 원래 값으로 복원됐으며, SealedSecret 상태는 `Synced=True`였습니다.
- 클러스터에 접속하지 않고 봉인하려면 공개 인증서를 받아 둡니다: `kubeseal --fetch-cert > pub.pem`, `kubeseal --cert pub.pem ...`.
- 값 하나만 봉인: `kubeseal --raw --namespace app --name db --from-file=값파일`.
- 봉인한 파일 확인: `kubeseal --validate -f db-sealed.yaml`(시험에서 종료 코드 0).

### 3.3 범위(scope)

| 범위             | 조건                                     | 지정                                                                          |
|------------------|------------------------------------------|-------------------------------------------------------------------------------|
| `strict`(기본)   | 봉인할 때의 이름·namespace와 같아야 풀림 | 없음                                                                          |
| `namespace-wide` | 같은 namespace 안에서 이름을 바꿔도 됨   | `--scope namespace-wide`                                                      |
| `cluster-wide`   | 어느 namespace·이름이든 풀림             | `--scope cluster-wide`(주석 `sealedsecrets.bitnami.com/cluster-wide: "true"`) |

- 시험에서 `strict`로 봉인한 것을 다른 namespace에 적용하자 Secret이 만들어지지 않고 상태에 `no key could decrypt secret (password)`가 남았습니다. 이름·namespace가 암호문의 일부라서, 남의 namespace로 옮겨 값을 빼내는 것을 막습니다.

### 3.4 키 갱신과 백업

- 컨트롤러는 봉인 키(인증서)를 30일마다 새로 만듭니다. 옛 키도 보관하므로 예전 SealedSecret도 계속 풀립니다. 새로 봉인할 때는 최신 공개키를 받아 씁니다.
- 키가 갱신돼도 기존 SealedSecret이 자동으로 다시 암호화되지는 않습니다(수동 재암호화 기능은 따로 있음). README는 "SealedSecret key renewal and re-encryption features are **not a substitute** for periodical rotation of your actual secret values."라고 밝힙니다. 비밀값이 새었다면 값 자체(DB 비밀번호 등)를 바꾸고 다시 봉인합니다.
- 클러스터를 다시 만들면 새 키가 생겨 기존 SealedSecret을 못 풉니다. 키 Secret을 백업해 둡니다(시험에서 키는 `kube-system`의 `kubernetes.io/tls` 형식 Secret 하나).

```bash
kubectl -n kube-system get secret -l sealedsecrets.bitnami.com/sealed-secrets-key -o yaml > sealed-secrets-keys.yaml
# 이 파일은 클러스터의 모든 SealedSecret을 풀 수 있으므로 Git에 두지 않고 비밀 저장소에 보관
```

- 키가 30일마다 갱신되므로 백업도 갱신 뒤 다시 만듭니다. 옛 백업으로는 새로 봉인한 SealedSecret을 못 풉니다.
- 복원: 컨트롤러를 띄우기 전에 키 Secret을 적용하거나, 이미 떠 있으면 `kubectl apply -f 백업파일` 뒤 컨트롤러 pod를 다시 시작합니다(README 절차, 미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 4. External Secrets Operator

외부 비밀 저장소의 값을 주기적으로 읽어 Kubernetes Secret을 만들고 갱신합니다. Git에는 "어느 저장소의 어느 키를 어떤 Secret으로"라는 참조만 둡니다.

### 4.1 설치

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace --version 2.15.0 --wait
```

- 시험에서 Deployment 3개(external-secrets, cert-controller, webhook)와 CRD 25개가 만들어졌습니다.
- ESO는 가장 최신 minor 판만 지원합니다. 2.15·2.14는 Kubernetes 1.37 기준으로 표시돼 있습니다.

### 4.2 SecretStore와 ExternalSecret

```yaml
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: fake
spec:
  provider:
    fake:                          # 시험용. 실제는 aws, gcpsm, azurekv, vault 등
      data:
        - key: /prod/db
          value: '{"username":"app","password":"<DB_PASSWORD>"}'
---
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: db
  namespace: app
spec:
  refreshInterval: 10s
  secretStoreRef:
    kind: ClusterSecretStore
    name: fake
  target:
    name: db-from-eso
  data:
    - secretKey: password
      remoteRef:
        key: /prod/db
        property: password
```

| 항목                    | 뜻                                                                              |
|-------------------------|---------------------------------------------------------------------------------|
| `SecretStore`           | namespace 안에서 쓰는 저장소 연결(인증 정보 포함)                               |
| `ClusterSecretStore`    | 모든 namespace에서 쓰는 저장소 연결                                             |
| `refreshInterval`       | 다시 읽는 주기. 0이면 한 번만 만듦                                              |
| `target.creationPolicy` | `Owner`(기본, ExternalSecret을 지우면 Secret도 지움), `Orphan`, `Merge`, `None` |
| `target.deletionPolicy` | 저장소에서 데이터가 모두 사라졌을 때 `Retain`(기본), `Delete`, `Merge`          |

- 시험 결과:
  - ClusterSecretStore `Valid`, ExternalSecret `SecretSynced`, Secret `db-from-eso`에 값이 들어가고 ownerReference가 ExternalSecret이었습니다.
  - 저장소 값을 바꾸자 10초 주기 안에 Secret 값이 바뀌었습니다.
  - 없는 속성을 가리키자 `SecretSyncedError: could not get secret data from provider`가 됐고, Secret은 마지막 값을 유지했습니다.
  - ExternalSecret을 지우자 Secret도 지워졌습니다(`creationPolicy: Owner`).
  - Fake provider를 쓰면 `Warning: store fake isn't currently maintained`가 나왔습니다. 시험용으로만 씁니다.
- 공급자 안정도(공식 표): AWS Secrets Manager·Parameter Store, Azure Key Vault, GCP Secret Manager, HashiCorp Vault 등은 stable, Kubernetes 공급자는 beta, 그 밖의 다수는 alpha입니다.
- 반대로 Kubernetes Secret을 외부 저장소로 밀어 넣는 `PushSecret`도 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Secrets Store CSI Driver와 클라우드 도구

Secrets Store CSI Driver는 외부 저장소의 비밀값을 pod에 볼륨(파일)으로 붙입니다. Kubernetes Secret으로 동기화하는 기능은 alpha입니다. 공급자로 AWS, Azure, GCP, Vault, OpenBao, Akeyless, Conjur가 있습니다.

| 클라우드 | 도구                                                      | 특징(공식 문서)                                                                                                      |
|----------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| AWS      | AWS Secrets and Configuration Provider(ASCP)              | Secrets Manager·Parameter Store 값을 CSI 볼륨으로. 설정 절차는 IRSA 기준, EKS Pod Identity도 언급                    |
| GCP      | GKE Secret Manager 애드온(`secrets-store-gke.csi.k8s.io`) | Secret Manager 값을 볼륨으로. Kubernetes Secret 동기화 미지원, 회전은 `--enable-secret-manager-rotation`(기본 120초) |
| Azure    | AKS `azure-keyvault-secrets-provider` 애드온              | Key Vault 값을 볼륨으로, Kubernetes Secret 동기화와 자동 회전 지원(기본 꺼짐, 주기 2분)                              |

- ESO와 CSI Driver 모두 pod가 외부 저장소에 접근할 클라우드 권한(IRSA·Pod Identity, Workload Identity, 관리 ID)이 필요합니다. 권한은 필요한 비밀값 경로로만 좁힙니다.
- AWS 쪽 비밀값 서비스는 [AWS 보안](./aws_security.md) 문서를 함께 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. etcd 저장 암호화

- 공식 문서에 따르면 API 서버는 기본으로 리소스를 etcd에 평문으로 저장합니다. Secret 저장 암호화는 API 서버의 `EncryptionConfiguration`으로 켭니다.
- 운영에서는 KMS 공급자(KMS v2, Kubernetes 1.29부터 stable)로 외부 키를 써서 봉투 암호화를 합니다. 관리형 Kubernetes는 사업자 설정(EKS·GKE·AKS의 KMS 연동)으로 켭니다.
- 저장 암호화는 etcd 파일·백업이 새는 경우를 막을 뿐, Secret 조회 권한이 있는 사용자를 막지는 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 고르는 기준

| 상황                                                     | 먼저 볼 것                                                         |
|----------------------------------------------------------|--------------------------------------------------------------------|
| 외부 비밀 저장소가 없고 GitOps로 클러스터 한두 개        | Sealed Secrets, 또는 Flux + SOPS                                   |
| AWS Secrets Manager·Vault 같은 저장소가 이미 있음        | External Secrets Operator                                          |
| 앱이 파일로 비밀값을 읽고 Secret 객체를 남기고 싶지 않음 | Secrets Store CSI Driver + 클라우드 공급자                         |
| 여러 클러스터에 같은 비밀값                              | ESO(원본 한 곳), Sealed Secrets는 클러스터마다 키가 달라 각각 봉인 |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용      | 방법                                                                  | 기대 결과             |
|------|----------------|-----------------------------------------------------------------------|-----------------------|
| 1    | Sealed Secrets | `kubectl get sealedsecret 이름 -o jsonpath='{.status.conditions[0]}'` | `Synced` True         |
| 2    | 복원           | `kubectl get secret 이름`                                             | 존재                  |
| 3    | 키 백업        | 키 Secret 목록                                                        | 백업 파일과 개수 일치 |
| 4    | ESO 저장소     | `kubectl get clustersecretstore`                                      | `Valid`               |
| 5    | ESO 동기화     | `kubectl get externalsecret`                                          | `SecretSynced`        |
| 6    | Git            | 저장소 전체에서 `kind: Secret` 검색                                   | 평문 Secret 0건       |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                                         | 원인                                                | 조치                                                   |
|--------------------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------|
| `no key could decrypt secret`                                | 다른 이름·namespace(strict), 다른 클러스터의 키     | 대상 namespace·이름으로 다시 봉인, 키 백업 복원        |
| 클러스터 재구축 뒤 SealedSecret 전부 실패                    | 새 컨트롤러가 새 키를 만듦                          | 백업한 키 Secret을 먼저 적용하고 컨트롤러 재시작       |
| `SecretSyncedError: could not get secret data from provider` | 키·속성 이름 오류, 권한 부족                        | `kubectl describe externalsecret`, 저장소 권한 확인    |
| ExternalSecret을 지웠더니 앱 Secret도 사라짐                 | `creationPolicy: Owner`(기본)                       | 남겨야 하면 `Orphan`                                   |
| 저장소 값을 바꿨는데 pod 환경 변수가 그대로                  | Secret은 바뀌어도 이미 뜬 pod의 환경 변수는 안 바뀜 | pod 재시작(Reloader 같은 도구) 또는 파일 마운트로 읽기 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [SOPS](../../02_infrastructure/iac/sops.md) — 파일 단위 암호화, Flux 복호화
- [FluxCD](../../02_infrastructure/cicd/fluxcd.md) — SOPS 복호화를 쓰는 GitOps
- [HashiCorp Vault 개념](../hardening/hashicorp_vault_concepts.md) — 외부 비밀 저장소
- [AWS 보안](./aws_security.md) — Secrets Manager, KMS

---

## 참고 자료

- Sealed Secrets: [README](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md) · [releases](https://github.com/bitnami-labs/sealed-secrets/releases) — ★★★☆☆
- External Secrets: [Overview](https://external-secrets.io/latest/) · [Stability and support](https://external-secrets.io/latest/introduction/stability-support/) · [ExternalSecret API](https://external-secrets.io/latest/api/externalsecret/) — ★★★☆☆
- Secrets Store CSI Driver: [docs](https://secrets-store-csi-driver.sigs.k8s.io/) · AWS [ASCP](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html) · GCP [Secret Manager add-on](https://docs.cloud.google.com/secret-manager/docs/secret-manager-managed-csi-component) · Azure [Key Vault provider](https://learn.microsoft.com/en-us/azure/aks/csi-secrets-store-driver) — ★★★☆☆
- Kubernetes: [Encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
