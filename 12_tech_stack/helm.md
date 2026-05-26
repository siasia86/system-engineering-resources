# Helm

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 주요 명령어](#4-주요-명령어) / [5. Chart 구조](#5-chart-구조) / [6. 템플릿 문법](#6-템플릿-문법) |
| [7. Values 관리](#7-values-관리) / [8. 의존성 관리](#8-의존성-관리) / [9. 실전 예시](#9-실전-예시) |
| [10. Tips](#10-tips) |

---

## 1. 개요

Helm은 Kubernetes 패키지 매니저. 복잡한 K8s 매니페스트를 Chart로 패키징하여 배포, 업그레이드, 롤백을 관리합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                      Helm Flow                               │
│                                                              │
│  Chart (템플릿) + Values (설정) -> Manifest -> K8s 배포      │
│                                                              │
│  helm install / upgrade / rollback / uninstall               │
└──────────────────────────────────────────────────────────────┘
```

- **패키지 관리**: 여러 K8s 리소스를 하나의 Chart로 묶어 배포합니다.
- **버전 관리**: Release 이력을 관리하여 이전 버전으로 롤백이 가능합니다.
- **재사용성**: Values 파일로 동일한 Chart를 환경별로 다르게 배포합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                    Helm v3 Architecture                      │
│                                                              │
│  helm CLI ──> Kubernetes API Server                          │
│                      │                                       │
│                       v                                      │
│              Release (Secret으로 저장)                       │
│              ┌─────────────────────────┐                     │
│              │  Release History        │                     │
│              │  revision 1: v1.0.0     │                     │
│              │  revision 2: v1.1.0     │                     │
│              │  revision 3: v1.2.0 ◄── │ current             │
│              └─────────────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

> Helm v2는 Tiller 서버가 필요했으나, v3부터 제거되어 kubectl 권한으로 직접 동작합니다.

> 🟡 **Helm v4 출시 (2025)**: v4는 v3와 대부분 호환되나 일부 CLI 플래그/SDK 변경이 있습니다. 기존 apiVersion v2 차트는 v4에서도 동작합니다. 주요 변경: WebAssembly 플러그인 시스템, Server-side Apply 기본 지원, 재현 가능한 차트 빌드.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념       | 설명                                                          |
|------------|---------------------------------------------------------------|
| Chart      | K8s 리소스 템플릿 묶음 (패키지)                               |
| Release    | Chart를 클러스터에 설치한 인스턴스. 이름으로 식별             |
| Repository | Chart를 저장/배포하는 저장소 (Artifact Hub 등)                |
| Values     | Chart 템플릿에 주입하는 설정 값                               |
| Template   | Go 템플릿 기반 K8s 매니페스트 파일                            |
| Revision   | Release의 버전 번호. 업그레이드/롤백 시 증가                  |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 명령어

### 저장소 관리

```bash
# 저장소 추가
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add argo https://argoproj.github.io/argo-helm

# 저장소 목록
helm repo list

# 저장소 업데이트
helm repo update

# Chart 검색
helm search repo redis
helm search repo redis --versions   # 모든 버전
helm search hub nginx               # Artifact Hub 검색
```

### 설치 & 업그레이드

```bash
# 설치
helm install my-redis bitnami/redis
helm install my-redis bitnami/redis --namespace my-ns --create-namespace
helm install my-redis bitnami/redis -f values.yaml
helm install my-redis bitnami/redis --set auth.password=SecurePassword123

# 업그레이드 (없으면 설치)
helm upgrade --install my-redis bitnami/redis -f values.yaml

# 특정 버전 설치
helm install my-redis bitnami/redis --version 23.1.1

# dry-run (실제 적용 없이 렌더링 확인)
helm install my-redis bitnami/redis --dry-run --debug
```

### 조회

```bash
# Release 목록
helm list
helm list -A                         # 전체 네임스페이스
helm list -n my-namespace

# Release 상태
helm status my-redis

# Release 이력
helm history my-redis

# 렌더링된 매니페스트 확인
helm get manifest my-redis

# 적용된 Values 확인
helm get values my-redis
helm get values my-redis --all       # 기본값 포함
```

### 롤백 & 삭제

```bash
# 롤백
helm rollback my-redis 1             # revision 1로 롤백
helm rollback my-redis               # 이전 revision으로 롤백

# 삭제
helm uninstall my-redis
helm uninstall my-redis --keep-history   # 이력 유지
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Chart 구조

```
my-app/
├── Chart.yaml           # Chart 메타데이터
├── values.yaml          # 기본 Values
├── values-dev.yaml      # 환경별 Values (관례)
├── values-prod.yaml
├── charts/              # 의존 Chart (서브차트)
├── templates/
│   ├── _helpers.tpl     # 재사용 템플릿 (named templates)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   ├── serviceaccount.yaml
│   └── NOTES.txt        # 설치 후 출력 메시지
└── .helmignore
```

### Chart.yaml

```yaml
apiVersion: v2
name: my-app
description: My application Helm chart
type: application   # application 또는 library
version: 1.2.3      # Chart 버전 (SemVer)
appVersion: "2.0.0" # 애플리케이션 버전

dependencies:
  - name: redis
    version: "18.6.1"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 템플릿 문법

### 기본 템플릿 (templates/deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
          {{- if .Values.resources }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- end }}
          {{- if .Values.env }}
          env:
            {{- range $key, $val := .Values.env }}
            - name: {{ $key }}
              value: {{ $val | quote }}
            {{- end }}
          {{- end }}
```

### _helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.chart" . }}
{{ include "my-app.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### 조건문 & 반복문

```yaml
# 조건문
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}

# 조건부 값
replicas: {{ if eq .Values.env "prod" }}3{{ else }}1{{ end }}

# 반복문 (리스트)
{{- range .Values.ingress.hosts }}
- host: {{ .host | quote }}
{{- end }}

# 반복문 (맵)
{{- range $key, $value := .Values.configMap }}
{{ $key }}: {{ $value | quote }}
{{- end }}

# with (컨텍스트 변경)
{{- with .Values.nodeSelector }}
nodeSelector:
  {{- toYaml . | nindent 8 }}
{{- end }}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Values 관리

### values.yaml (기본값)

```yaml
replicaCount: 1

image:
  repository: 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/my-app
  tag: ""   # 비워두면 Chart.AppVersion 사용
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: false
  className: nginx
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

env: {}

redis:
  enabled: false
```

### 환경별 Values 오버라이드

```yaml
# values-prod.yaml
replicaCount: 3

image:
  tag: v1.2.3

ingress:
  enabled: true
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20

env:
  APP_ENV: production
  LOG_LEVEL: warn
```

```bash
# 환경별 배포
helm upgrade --install my-app ./my-app \
  -f values.yaml \
  -f values-prod.yaml \
  --namespace production
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 의존성 관리

```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: "18.6.1"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
  - name: postgresql
    version: "13.2.0"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

```bash
# 의존성 다운로드
helm dependency update ./my-app

# 의존성 목록 확인
helm dependency list ./my-app
```

```yaml
# values.yaml에서 서브차트 설정
redis:
  enabled: true
  auth:
    password: SecurePassword123
  master:
    persistence:
      size: 8Gi
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 실전 예시

### CI/CD에서 Helm 배포

```bash
# GitHub Actions / Jenkins에서 사용
helm upgrade --install my-app ./charts/my-app \
  --namespace production \
  --create-namespace \
  --set image.tag=${IMAGE_TAG} \
  --set env.APP_ENV=production \
  -f ./charts/my-app/values-prod.yaml \
  --wait \          # 배포 완료까지 대기
  --timeout 5m \
  --atomic                    # 실패 시 자동 롤백
```

### Chart 생성 & 패키징

```bash
# 새 Chart 생성 (boilerplate)
helm create my-app

# Chart 유효성 검사
helm lint ./my-app

# 렌더링 테스트
helm template my-app ./my-app -f values-prod.yaml

# Chart 패키징
helm package ./my-app

# OCI 레지스트리(ECR)에 푸시
aws ecr create-repository --repository-name helm-charts/my-app --region ap-northeast-1

helm push my-app-1.2.3.tgz oci://123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/helm-charts

# OCI 레지스트리에서 설치
helm install my-app oci://123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/helm-charts/my-app --version 1.2.3
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Tips

### 자주 쓰는 패턴

```bash
# 설치 전 렌더링 확인
helm template my-app ./my-app -f values-prod.yaml | kubectl apply --dry-run=client -f -

# 현재 배포된 Values와 새 Values 비교
helm get values my-app > current-values.yaml
diff current-values.yaml new-values.yaml

# 업그레이드 전 변경 사항 확인 (helm-diff 플러그인)
helm plugin install https://github.com/databus23/helm-diff
helm diff upgrade my-app ./my-app -f values-prod.yaml
```

### 주의사항

🟡 `--atomic` 플래그는 배포 실패 시 자동 롤백하지만, 롤백도 실패할 수 있습니다. 프로덕션에서는 `helm history`로 이력을 확인하고 수동 롤백을 병행합니다.

🟡 Secret 값을 values.yaml에 평문으로 저장하지 않습니다. `helm-secrets` 플러그인 또는 외부 시크릿 관리자를 사용합니다.

🟡 Chart 버전(`version`)과 앱 버전(`appVersion`)을 구분합니다. Chart 구조 변경 시 Chart 버전을 올립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Helm Documentation: [helm.sh/docs](https://helm.sh/docs/) — ★★★☆☆
- Artifact Hub: [artifacthub.io](https://artifacthub.io/) — ★★☆☆☆
- Helm Best Practices: [helm.sh/docs/chart_best_practices](https://helm.sh/docs/chart_best_practices/) — ★★★☆☆

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

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.
