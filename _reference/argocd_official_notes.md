---
name: argocd-official-notes
description: ArgoCD 공식 문서 기반 GitOps 개념, 버전, 아키텍처 정리.
last_checked: 2026-05-26
sources:
  - https://argo-cd.readthedocs.io/en/stable/
  - https://argo-cd.readthedocs.io/en/stable/core_concepts/
---

# ArgoCD 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-26)

| 항목   | 버전   |
|--------|--------|
| ArgoCD | v3.4.2 |

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

| 용어           | 설명                                                  |
|----------------|-------------------------------------------------------|
| Application    | Git 소스 + K8s 클러스터 대상을 연결한 ArgoCD 오브젝트 |
| Sync           | Git 상태를 클러스터에 적용하는 동작                   |
| Sync Status    | Synced / OutOfSync / Unknown                          |
| Health Status  | Healthy / Degraded / Progressing / Missing            |
| App of Apps    | Application을 관리하는 상위 Application 패턴          |
| ApplicationSet | 여러 클러스터/환경에 Application 자동 생성            |

## 5. 지원 소스 타입

- Helm Chart
- Kustomize
- YAML/JSON 디렉토리
- Jsonnet

## 6. 설치

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## 7. 주의사항

- Auto-sync 활성화 시 Git push만으로 클러스터 변경 — RBAC 설정 필수
- `argocd app sync` 명령으로 수동 sync 가능
- SSO 연동 권장 (Dex 내장)
- 멀티 클러스터 관리 가능 (클러스터별 kubeconfig 등록)
