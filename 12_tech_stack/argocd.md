# ArgoCD

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 설치](#4-설치) / [5. Application 관리](#5-application-관리) / [6. Sync 전략](#6-sync-전략) |
| [7. App of Apps 패턴](#7-app-of-apps-패턴) / [8. RBAC & 보안](#8-rbac--보안) / [9. 알림](#9-알림) |
| [10. Tips](#10-tips) |

---

## 1. 개요

ArgoCD는 Kubernetes를 위한 GitOps 기반 CD(Continuous Delivery) 도구. Git 저장소를 단일 진실 공급원(Single Source of Truth)으로 삼아 클러스터 상태를 자동으로 동기화합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                     GitOps Flow                              │
│                                                              │
│  Developer ──> Git Push ──> ArgoCD detects diff              │
│                                    │                         │
│                                    v                         │
│                          Sync to Kubernetes                  │
│                          (Desired == Actual)                 │
└──────────────────────────────────────────────────────────────┘
```

- **Pull 방식**: ArgoCD가 Git을 주기적으로 폴링하여 변경 감지 (Push 방식 대비 보안 우수)
- **드리프트 감지**: 실제 클러스터 상태가 Git과 다를 경우 자동 또는 수동으로 동기화
- **멀티 클러스터**: 단일 ArgoCD 인스턴스로 여러 K8s 클러스터 관리 가능

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                    ArgoCD Components                         │
│                                                              │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  API Server     │  │  Repo Server │  │  Application   │  │
│  │  (UI/CLI/API)   │  │  (Git clone) │  │  Controller    │  │
│  └─────────────────┘  └──────────────┘  └────────────────┘  │
│           │                  │                  │            │
│           └──────────────────┴──────────────────┘            │
│                              │                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              v                v                v
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Git Repo    │  │  K8s Cluster │  │  K8s Cluster │
   │  (Source)    │  │  (Target 1)  │  │  (Target 2)  │
   └──────────────┘  └──────────────┘  └──────────────┘
```

| 컴포넌트               | 역할                                              |
|------------------------|---------------------------------------------------|
| API Server             | UI, CLI, gRPC/REST API 제공. 인증/인가 처리       |
| Repository Server      | Git 저장소 클론 및 매니페스트 생성 (캐시 포함)    |
| Application Controller | 실제 상태 vs 원하는 상태 비교 및 동기화           |
| Redis                  | 캐시 및 상태 저장                                 |
| Dex (선택)             | SSO/OIDC 연동                                     |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념              | 설명                                                          |
|-------------------|---------------------------------------------------------------|
| Application       | Git 소스 + K8s 클러스터/네임스페이스 매핑 단위               |
| Project           | Application 그룹. 소스/대상 클러스터/네임스페이스 제한 가능  |
| Sync              | Git 상태를 클러스터에 적용하는 작업                           |
| Sync Status       | Synced / OutOfSync / Unknown                                  |
| Health Status     | Healthy / Progressing / Degraded / Missing / Suspended        |
| Drift             | Git 정의와 실제 클러스터 상태의 차이                          |
| Auto Sync         | 변경 감지 시 자동으로 Sync 실행                               |
| Self Heal         | 클러스터에서 직접 변경된 내용을 Git 상태로 되돌림             |
| Prune             | Git에서 삭제된 리소스를 클러스터에서도 삭제                   |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

### Helm으로 설치

```bash
# 네임스페이스 생성
kubectl create namespace argocd

# Helm 설치
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm install argocd argo/argo-cd \
  --namespace argocd \
  --version 6.7.3 \
  --set server.service.type=LoadBalancer
```

### 초기 비밀번호 확인

```bash
# admin 초기 비밀번호
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath="{.data.password}" | base64 -d

# 비밀번호 변경
argocd account update-password
```

### CLI 설치

```bash
# Linux
curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd
sudo mv argocd /usr/local/bin/

# 로그인
argocd login <ARGOCD_SERVER> --username admin --password <PASSWORD>
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Application 관리

### Application 생성 (YAML)

```yaml
# application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io   # 삭제 시 K8s 리소스도 삭제
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: main
    path: k8s/overlays/prod

  destination:
    server: https://kubernetes.default.svc   # 동일 클러스터
    namespace: my-app

  syncPolicy:
    automated:
      prune: true      # Git에서 삭제된 리소스 제거
      selfHeal: true   # 클러스터 직접 변경 시 되돌림
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - ApplyOutOfSyncOnly=true
```

```bash
kubectl apply -f application.yaml
```

### CLI로 Application 관리

```bash
# Application 목록
argocd app list

# 상태 확인
argocd app get my-app

# 수동 Sync
argocd app sync my-app

# Sync 강제 (리소스 재생성)
argocd app sync my-app --force

# 특정 리소스만 Sync
argocd app sync my-app --resource apps:Deployment:my-app

# 롤백
argocd app rollback my-app <REVISION>

# 삭제 (K8s 리소스 포함)
argocd app delete my-app --cascade
```

### Helm Chart 소스

```yaml
spec:
  source:
    repoURL: https://charts.bitnami.com/bitnami
    chart: redis
    targetRevision: 18.6.1
    helm:
      releaseName: redis
      values: |
        auth:
          enabled: true
          password: "SecurePassword123"
      valueFiles:
        - values-prod.yaml
```

### Kustomize 소스

```yaml
spec:
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: main
    path: k8s/base
    kustomize:
      images:
        - myapp=123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/myapp:v1.2.3
      commonLabels:
        env: prod
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Sync 전략

### Sync 옵션 비교

| 옵션              | 설명                                              | 권장 환경  |
|-------------------|---------------------------------------------------|------------|
| Auto Sync         | Git 변경 감지 시 자동 적용                        | dev/stg    |
| Manual Sync       | 수동으로 Sync 실행                                | prod       |
| Self Heal         | 클러스터 직접 변경 시 Git 상태로 복원             | 모든 환경  |
| Prune             | Git에서 삭제된 리소스를 클러스터에서도 삭제       | 주의 필요  |

### Sync Wave (순서 제어)

```yaml
# 리소스에 어노테이션 추가
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"   # 낮은 숫자 먼저 실행
```

```
Wave -1: Namespace, CRD
Wave  0: ConfigMap, Secret (기본값)
Wave  1: Deployment, Service
Wave  2: Ingress, HPA
```

### Sync Hook

```yaml
# Pre-sync Job (DB 마이그레이션 등)
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: myapp:latest
          command: ["python", "manage.py", "migrate"]
      restartPolicy: Never
```

| Hook 타입    | 실행 시점                    |
|--------------|------------------------------|
| PreSync      | Sync 시작 전                 |
| Sync         | Sync 중 (일반 리소스와 함께) |
| PostSync     | Sync 완료 후                 |
| SyncFail     | Sync 실패 시                 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. App of Apps 패턴

여러 Application을 하나의 부모 Application으로 관리합니다.

```
apps/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── frontend.yaml
    ├── backend.yaml
    └── database.yaml
```

```yaml
# apps/templates/backend.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: backend
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: main
    path: services/backend
  destination:
    server: https://kubernetes.default.svc
    namespace: backend
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```bash
# 부모 Application 생성
argocd app create apps \
  --repo https://github.com/myorg/myrepo.git \
  --path apps \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace argocd \
  --sync-policy automated
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. RBAC & 보안

### Project 설정

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production environment

  # 허용 소스 저장소
  sourceRepos:
    - 'https://github.com/myorg/*'

  # 허용 대상 클러스터/네임스페이스
  destinations:
    - namespace: 'prod-*'
      server: https://kubernetes.default.svc

  # 허용 K8s 리소스 종류
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace

  namespaceResourceWhitelist:
    - group: 'apps'
      kind: Deployment
    - group: ''
      kind: Service

  # 배포 전 수동 승인
  syncWindows:
    - kind: allow
      schedule: '10 1 * * *'
      duration: 1h
      applications:
        - '*'
```

### RBAC 설정

```yaml
# argocd-rbac-cm ConfigMap
data:
  policy.csv: |
    # 역할 정의
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, dev/*, allow
    p, role:developer, applications, sync, stg/*, allow

    p, role:ops, applications, *, */*, allow
    p, role:ops, clusters, get, *, allow

    # 그룹 매핑 (SSO)
    g, myorg:developers, role:developer
    g, myorg:ops, role:ops

  policy.default: role:readonly
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 알림

### Notifications Controller 설정

```yaml
# argocd-notifications-cm ConfigMap
data:
  service.slack: |
    token: $slack-token

  template.app-sync-succeeded: |
    slack:
      attachments: |
        [{
          "title": "{{.app.metadata.name}}",
          "color": "#18be52",
          "fields": [{
            "title": "Sync Status",
            "value": "{{.app.status.sync.status}}",
            "short": true
          }]
        }]

  trigger.on-sync-succeeded: |
    - when: app.status.sync.status == 'Synced'
      send: [app-sync-succeeded]
```

```yaml
# Application에 어노테이션 추가
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: my-channel
    notifications.argoproj.io/subscribe.on-sync-failed.slack: alerts-channel
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Tips

### GitOps 저장소 구조

```
gitops-repo/
├── apps/                    # App of Apps
│   └── templates/
├── clusters/
│   ├── dev/
│   │   └── values.yaml
│   └── prod/
│       └── values.yaml
└── services/
    ├── frontend/
    │   ├── base/
    │   └── overlays/
    │       ├── dev/
    │       └── prod/
    └── backend/
        ├── base/
        └── overlays/
```

### 이미지 업데이트 자동화 (Argo CD Image Updater)

```yaml
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: myapp=123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/myapp
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver
    argocd-image-updater.argoproj.io/write-back-method: git
```

### 주의사항

⚠️ `prune: true`와 `selfHeal: true`를 프로덕션에서 활성화할 때는 Git 저장소 접근 제어를 먼저 강화합니다. Git이 단일 진실 공급원이므로 잘못된 커밋이 즉시 프로덕션에 반영됩니다.

⚠️ ArgoCD UI/API는 외부에 노출하지 않습니다. VPN 또는 내부 네트워크에서만 접근하도록 설정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- ArgoCD Documentation: [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/) — ★★★☆☆
- ArgoCD Best Practices: [argo-cd.readthedocs.io/best_practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) — ★★★☆☆
- Argo CD Image Updater: [argocd-image-updater.readthedocs.io](https://argocd-image-updater.readthedocs.io/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-10

**마지막 업데이트**: 2026-05-10

© 2026 siasia86. Licensed under CC BY 4.0.
