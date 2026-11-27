---
name: argocd-official-notes
description: ArgoCD 공식 문서 기반 GitOps 개념, 버전, 아키텍처 정리.
tags:
  - argocd
  - gitops
  - kubernetes
  - cicd
last_checked: 2026-11-27
sources:
  - https://argo-cd.readthedocs.io/en/stable/
  - https://argo-cd.readthedocs.io/en/stable/core_concepts/
  - https://argo-cd.readthedocs.io/en/stable/getting_started/
  - https://argo-cd.readthedocs.io/en/stable/operator-manual/health/
  - https://github.com/argoproj/argo-cd/releases
  - https://github.com/argoproj/argo-cd/blob/v3.6.3/docs/operator-manual/upgrading/3.5-3.6.md
  - https://github.com/argoproj/argo-helm/releases
---

# ArgoCD 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-11-27)

| 항목                | 버전                                                              |
|---------------------|-------------------------------------------------------------------|
| ArgoCD              | v3.6.3 (2026-11-24, 같은 날 v3.5.9·v3.4.15)                       |
| Helm 차트 `argo-cd` | 10.20.0 (2026-11-25, appVersion v3.6.3, kubeVersion `>=1.25.0-0`) |

## 2. 공식 정의

> "Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes.
> Application definitions, configurations, and environments should be
> declarative and version controlled."
> — argo-cd.readthedocs.io

## 3. GitOps 패턴

```
Developer
  │  git push
  v
Git Repository (Single Source of Truth)
  │  detect changes
  v
ArgoCD (auto sync)
  │
  v
Kubernetes Cluster (live state = Git state)
```
- 개발자가 Git에 push → ArgoCD가 변경 감지 → 클러스터 자동 동기화

## 4. 핵심 개념

| 용어           | 설명                                                             |
|----------------|------------------------------------------------------------------|
| Application    | Git 소스 + K8s 클러스터 대상을 연결한 ArgoCD 오브젝트            |
| Sync           | Git 상태를 클러스터에 적용하는 동작                              |
| Sync Status    | Synced / OutOfSync / Unknown                                     |
| Health Status  | Healthy / Progressing / Degraded / Suspended / Missing / Unknown |
| App of Apps    | Application을 관리하는 상위 Application 패턴                     |
| ApplicationSet | 여러 클러스터/환경에 Application 자동 생성                       |

## 5. 지원 소스 타입

- Helm Chart
- Kustomize
- YAML/JSON 디렉토리
- Jsonnet

## 6. 설치

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

- 공식 Getting Started는 `--server-side`를 사용합니다. ApplicationSet 같은 일부 CRD가 client-side apply의 annotation 크기 제한(262KB)을 넘기 때문이며, `--force-conflicts`는 업그레이드 때 다른 도구가 관리하던 필드를 넘겨받습니다(2026-11-09 확인).

## 7. 주의사항

- Auto-sync 활성화 시 Git push만으로 클러스터 변경 — RBAC 설정 필수
- `argocd app sync` 명령으로 수동 sync 가능
- SSO 연동 권장 (Dex 내장)
- 멀티 클러스터 관리 가능 (클러스터별 kubeconfig 등록)

## 8. 판 지원과 업그레이드 (2026-11-27, GitHub 원본 문서 v3.6.3)

- readthedocs가 HTTP 429를 돌려줘 같은 문서를 GitHub 저장소 원본으로 읽음.
- 지원: "Only the three most recent minor versions are eligible for patch releases."(release-process-and-cadence.md)
- 시험된 Kubernetes 판: 3.6 → v1.37·v1.36·v1.35·v1.34, 3.5 → v1.36~v1.33, 3.4 → v1.35~v1.32.
- 3.4→3.5: Helm 4.2.0(plain HTTP OCI 저장소 조치), GnuPG 서명 검증 → Source Integrity, `signatureKeys`·`add-signature-key` 사용 중단 예고, Event-listing gRPC 반환형 변경.
- 3.5→3.6: Server-Side Apply 사용 시 Server-Side Diff, Structured-Merge Diff 제거, repo-server OTLP 헤더 환경 변수 이름 변경, `--local-include` 기본값에 `*.tpl`·`Chart.lock` 추가.

## 9. kind 시험 (2026-11-27, kind v0.33.0, Kubernetes v1.37.0)

- CLI `argocd-linux-amd64` v3.6.3 체크섬(cli_checksums.txt) 일치.
- client-side `kubectl apply -f install.yaml`: `The CustomResourceDefinition "applicationsets.argoproj.io" is invalid: metadata.annotations: Too long: may not be more than 262144 bytes`. server-side `--force-conflicts`로 성공.
- Deployment 6개 + StatefulSet 1개 준비, `argocd-initial-admin-secret` 생성.
- podinfo `kustomize` Application(automated prune·selfHeal, CreateNamespace): Synced, Health Degraded. HPA `ScalingActive False`(`FailedGetResourceMetric`, metrics-server 없음)가 함께 나타남.
- selfHeal: 이미지를 손으로 6.0.0으로 바꾸고 20초 뒤 6.17.0으로 복귀.
- prune: 손으로 만든 ConfigMap은 15초 뒤에도 남음.
- `argocd app list --core`, `argocd app get --core` 동작.
- 미실행: Helm 차트 설치, HA, SSO, 알림.
