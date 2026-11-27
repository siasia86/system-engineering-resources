# ArgoCD
<!-- reference: _reference/argocd_official_notes.md -->

- 기준 판: Argo CD v3.6.3 (2026-11-24), Helm 차트 `argo/argo-cd` 10.20.0 (2026-11-27 확인)
- 예제 시험: 2026-11-27 4절 매니페스트 설치(server-side)와 5·6절 자동 동기화·selfHeal, `argocd --core` 조회를 kind v0.33.0(Kubernetes v1.37.0)에서 확인. Helm 차트 설치, HA 구성, SSO·RBAC·알림, App of Apps, Image Updater는 미실행

## 목차

| 섹션                                                                                              |
|---------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념)                    |
| [4. 설치](#4-설치) / [5. Application 관리](#5-application-관리) / [6. Sync 전략](#6-sync-전략)    |
| [7. App of Apps 패턴](#7-app-of-apps-패턴) / [8. RBAC & 보안](#8-rbac--보안) / [9. 알림](#9-알림) |
| [10. Tips](#10-tips) / [11. 판과 업그레이드](#11-판과-업그레이드) / [함께 보기](#함께-보기)       |

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
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │  API Server     │  │  Repo Server │  │  Application   │   │
│  │  (UI/CLI/API)   │  │  (Git clone) │  │  Controller    │   │
│  └─────────────────┘  └──────────────┘  └────────────────┘   │
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

| 컴포넌트               | 역할                                           |
|------------------------|------------------------------------------------|
| API Server             | UI, CLI, gRPC/REST API 제공. 인증/인가 처리    |
| Repository Server      | Git 저장소 클론 및 매니페스트 생성 (캐시 포함) |
| Application Controller | 실제 상태 vs 원하는 상태 비교 및 동기화        |
| Redis                  | 캐시 및 상태 저장                              |
| Dex (선택)             | SSO/OIDC 연동                                  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념          | 설명                                                             |
|---------------|------------------------------------------------------------------|
| Application   | Git 소스 + K8s 클러스터/네임스페이스 매핑 단위                   |
| Project       | Application 그룹. 소스/대상 클러스터/네임스페이스 제한 가능      |
| Sync          | Git 상태를 클러스터에 적용하는 작업                              |
| Sync Status   | Synced / OutOfSync / Unknown                                     |
| Health Status | Healthy / Progressing / Degraded / Missing / Suspended / Unknown |
| Drift         | Git 정의와 실제 클러스터 상태의 차이                             |
| Auto Sync     | 변경 감지 시 자동으로 Sync 실행                                  |
| Self Heal     | 클러스터에서 직접 변경된 내용을 Git 상태로 되돌림                |
| Prune         | Git에서 삭제된 리소스를 클러스터에서도 삭제                      |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

### 매니페스트로 설치

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.6.3/manifests/install.yaml
kubectl -n argocd rollout status deploy/argocd-server
```

- `--server-side`를 빼면 `The CustomResourceDefinition "applicationsets.argoproj.io" is invalid: metadata.annotations: Too long: may not be more than 262144 bytes`로 실패합니다(v3.6.3 시험). 공식 설치·업그레이드 명령도 `--server-side --force-conflicts`를 씁니다.
- `install.yaml`은 시험·평가용 단일 replica 구성입니다. 운영은 `manifests/ha/install.yaml`을 씁니다. API 서버·UI 없이 컨트롤러만 두는 `core-install.yaml`도 있습니다.
- 시험에서 Deployment 6개(applicationset-controller, dex-server, notifications-controller, redis, repo-server, server)와 StatefulSet `argocd-application-controller`가 떴습니다.

### Helm으로 설치

```bash
# 네임스페이스 생성
kubectl create namespace argocd

# Helm 설치
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# 차트 10.20.0 = Argo CD v3.6.3 (판 목록: helm search repo argo/argo-cd --versions)
helm install argocd argo/argo-cd \
  --namespace argocd \
  --version 10.20.0 \
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
    # Bitnami 공식 안내는 OCI 저장소: repoURL: registry-1.docker.io/bitnamicharts (oci:// 없이)
    repoURL: https://charts.bitnami.com/bitnami
    chart: redis
    targetRevision: 23.1.1
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

| 옵션        | 설명                                        | 권장 환경 |
|-------------|---------------------------------------------|-----------|
| Auto Sync   | Git 변경 감지 시 자동 적용                  | dev/stg   |
| Manual Sync | 수동으로 Sync 실행                          | prod      |
| Self Heal   | 클러스터 직접 변경 시 Git 상태로 복원       | 모든 환경 |
| Prune       | Git에서 삭제된 리소스를 클러스터에서도 삭제 | 주의 필요 |

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

| Hook 타입 | 실행 시점                    |
|-----------|------------------------------|
| PreSync   | Sync 시작 전                 |
| Sync      | Sync 중 (일반 리소스와 함께) |
| PostSync  | Sync 완료 후                 |
| SyncFail  | Sync 실패 시                 |

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

  # Sync 허용 시간대 (매일 01:10부터 1시간)
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
    - when: app.status.operationState != nil and app.status.operationState.phase in ['Succeeded']
      oncePer: app.status.operationState?.syncResult?.revision
      send: [app-sync-succeeded]
```

`app.status.sync.status == 'Synced'`처럼 상태만 보는 조건은 Synced가 유지되는 동안 계속 참이라 알림이 반복될 수 있습니다. 공식 카탈로그는 sync 작업 결과(`operationState.phase`)와 `oncePer`(revision당 1회)를 씁니다. 아래 `on-sync-failed` 구독은 카탈로그의 `trigger.on-sync-failed`·`template.app-sync-failed`를 함께 설치했다고 가정합니다.

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

🟡 Argo CD Image Updater v1.0부터 설정 방식이 Application 어노테이션에서 `ImageUpdater` CRD로 바뀌었습니다. 아래 어노테이션 예시는 v0.x 방식입니다.

```yaml
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: myapp=123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/myapp
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver
    argocd-image-updater.argoproj.io/write-back-method: git
```

### 주의사항

🟡 `prune: true`와 `selfHeal: true`를 프로덕션에서 활성화할 때는 Git 저장소 접근 제어를 먼저 강화합니다. Git이 단일 진실 공급원이므로 잘못된 커밋이 즉시 프로덕션에 반영됩니다.

🟡 ArgoCD UI/API는 외부에 노출하지 않습니다. VPN 또는 내부 네트워크에서만 접근하도록 설정합니다.

🟡 Sync가 `Synced`인데 Health가 `Degraded`이면 리소스 하나의 상태 문제입니다. 시험에서 metrics-server가 없는 kind 클러스터에 HPA가 들어간 앱은 HPA가 `ScalingActive False`(`FailedGetResourceMetric`)로 남아 앱 전체가 `Degraded`로 표시됐습니다. `kubectl describe`로 해당 리소스의 조건을 봅니다.

🟡 `prune: true`는 Argo CD가 관리하던 리소스 중 Git에서 빠진 것만 지웁니다. 같은 namespace에 손으로 만든 리소스(시험에서 ConfigMap)는 지우지 않았습니다.

### CLI만으로 조회 (core 모드)

```bash
# API 서버 로그인 없이 현재 kubeconfig 권한으로 조회
kubectl config set-context --current --namespace=argocd
argocd app list --core
argocd app get podinfo --core
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 판과 업그레이드

| Argo CD | 시험된 Kubernetes 판       |
|---------|----------------------------|
| 3.6     | v1.37, v1.36, v1.35, v1.34 |
| 3.5     | v1.36, v1.35, v1.34, v1.33 |
| 3.4     | v1.35, v1.34, v1.33, v1.32 |

- 최근 minor 판 세 개만 patch를 받고, 그보다 오래된 판은 EOL입니다. 2026-11-24에 v3.6.3·v3.5.9·v3.4.15가 함께 나왔습니다.
- minor 판을 건너뛰어 올릴 때는 사이의 업그레이드 문서를 모두 읽습니다. 3.4 → 3.6에서 볼 점:

| 구간      | 주요 변경                                                                                                                                                                               |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3.4 → 3.5 | Helm 4.2로 올라 plain HTTP OCI 저장소는 `--insecure-oci-force-http` 등 조치 필요, GnuPG 서명 검증이 Source Integrity로 바뀌고 `signatureKeys` 사용 중단 예고                            |
| 3.5 → 3.6 | Server-Side Apply를 쓰면 Server-Side Diff를 쓰고 Structured-Merge Diff는 제거, repo-server OTLP 헤더 환경 변수 이름 변경, `app diff --local` 기본 포함 파일에 `*.tpl`·`Chart.lock` 추가 |

```bash
# 업그레이드도 같은 방식 (판만 바꿈)
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.6.3/manifests/install.yaml
```

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [FluxCD](./fluxcd.md) — 컨트롤러 기반 GitOps, Argo CD 비교
- [Helm](../containers/helm.md) — 차트와 릴리스
- [kind](../containers/kind.md) — 시험용 로컬 클러스터

---

## 참고 자료

- ArgoCD Documentation: [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/) — ★★★☆☆
- ArgoCD Best Practices: [argo-cd.readthedocs.io/best_practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) — ★★★☆☆
- Argo CD Image Updater: [argocd-image-updater.readthedocs.io](https://argocd-image-updater.readthedocs.io/) — ★★★☆☆
- Argo CD Helm (OCI 차트 repoURL 형식): [argo-cd.readthedocs.io/user-guide/helm](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/) — ★★★☆☆
- Argo Helm argo-cd-10.20.0 릴리스 (appVersion v3.6.3): [github.com/argoproj/argo-helm](https://github.com/argoproj/argo-helm/releases/tag/argo-cd-10.20.0) — ★★★☆☆
- 업그레이드 문서 (GitHub 원본): [3.4-3.5](https://github.com/argoproj/argo-cd/blob/v3.6.3/docs/operator-manual/upgrading/3.4-3.5.md) · [3.5-3.6](https://github.com/argoproj/argo-cd/blob/v3.6.3/docs/operator-manual/upgrading/3.5-3.6.md) · [시험된 Kubernetes 판](https://github.com/argoproj/argo-cd/blob/v3.6.3/docs/operator-manual/tested-kubernetes-versions.md) — ★★★☆☆
- Bitnami Charts README (OCI 설치 안내): [github.com/bitnami/charts](https://github.com/bitnami/charts) — ★★★☆☆
- Argo CD Notifications 트리거 카탈로그 (notifications_catalog/install.yaml): [github.com/argoproj/argo-cd](https://github.com/argoproj/argo-cd/blob/stable/notifications_catalog/install.yaml) — ★★★☆☆ (확인일 2026-11-16)

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

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
