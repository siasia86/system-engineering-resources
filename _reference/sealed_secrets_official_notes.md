---
name: sealed-secrets-official-notes
description: Sealed Secrets v0.41.2 판, 범위(strict·namespace-wide·cluster-wide), 30일 키 갱신과 백업·복원, kind 시험 결과 정리.
tags:
  - sealed-secrets
  - kubernetes
  - secrets
last_checked: 2026-11-27
sources:
  - https://github.com/bitnami-labs/sealed-secrets/releases
  - https://github.com/bitnami-labs/sealed-secrets/blob/v0.41.2/README.md
---

# Sealed Secrets 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- 최신 v0.41.2(2026-10-26), 이전 v0.41.1(10-23). Helm 차트 helm-v2.22.0(10-26). 라이선스 Apache-2.0.
- 릴리스 자산: `controller.yaml`, `controller-norbac.yaml`, `kubeseal-<판>-linux-amd64.tar.gz`, `sealed-secrets_<판>_checksums.txt`. 시험한 kubeseal 압축판 체크섬 일치.
- CRD API `bitnami.com/v1alpha1`.

## 2. README (v0.41.2)

- "Since v0.9.x certificates get automatically renewed every 30 days."
- 범위: `strict`(기본) "the secret must be sealed with exactly the same *name* and *namespace*", `namespace-wide`, `cluster-wide`. 주석 `sealedsecrets.bitnami.com/namespace-wide`·`cluster-wide`, 둘 다 있으면 cluster-wide 우선.
- "SealedSecret key renewal and re-encryption features are **not a substitute** for periodical rotation of your actual secret values."
- 백업: `kubectl get secret -n kube-system -l sealedsecrets.bitnami.com/sealed-secrets-key -o yaml`. "After sealing key renewal you should recreate your backup." 복원은 컨트롤러 시작 전에 적용하거나, 적용 뒤 컨트롤러 재시작.
- Helm 저장소 `https://bitnami.github.io/sealed-secrets`.

## 3. kind 시험 (2026-11-27, Kubernetes v1.37.0)

- controller.yaml 적용, 이미지 `docker.io/bitnami/sealed-secrets-controller:0.41.2`.
- `kubeseal -f db.yaml -w db-sealed.yaml` → 적용 뒤 Secret 복원, 상태 `Synced=True`.
- strict 봉인을 다른 namespace에 적용: Secret 없음, 상태 메시지 `no key could decrypt secret (password)`.
- `--fetch-cert`로 PEM 인증서, `--cert`로 오프라인 봉인 성공. `--raw` 동작. `--scope cluster-wide`는 주석 추가.
- 키 Secret 1개, 형식 `kubernetes.io/tls`. `kubeseal --validate` 종료 코드 0.
- 미실행: Helm 설치, 키 복원, 재암호화.
