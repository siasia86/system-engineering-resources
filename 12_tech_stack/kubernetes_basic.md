# Kubernetes 기본

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 오브젝트](#3-핵심-오브젝트) |
| [4. kubectl 기본 명령어](#4-kubectl-기본-명령어) / [5. Pod & Deployment](#5-pod--deployment) / [6. Service & Ingress](#6-service--ingress) |
| [7. ConfigMap & Secret](#7-configmap--secret) / [8. Storage](#8-storage) / [9. 리소스 관리](#9-리소스-관리) |
| [10. 네임스페이스 & RBAC](#10-네임스페이스--rbac) / [11. 헬스체크](#11-헬스체크) / [12. Tips](#12-tips) |

---

## 1. 개요

Kubernetes(K8s)는 컨테이너화된 애플리케이션의 배포, 스케일링, 운영을 자동화하는 오픈소스 오케스트레이션 플랫폼입니다.

```
┌──────────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                         │
│                                                              │
│  Control Plane ──> Worker Nodes ──> Pods ──> Containers      │
│                                                              │
│  Desired State (YAML) ──> Actual State (Running)             │
└──────────────────────────────────────────────────────────────┘
```

- **선언형 관리**: YAML로 원하는 상태를 정의하면 K8s가 실제 상태를 맞춥니다.
- **자가 복구**: Pod 장애 시 자동 재시작, 노드 장애 시 다른 노드로 재스케줄링합니다.
- **수평 확장**: HPA(Horizontal Pod Autoscaler)로 부하에 따라 자동 스케일링합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        Control Plane                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  API Server  │  │  etcd        │  │  Scheduler         │    │
│  │  (kube-api)  │  │  (state DB)  │  │  (pod placement)   │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Controller Manager (Deployment, ReplicaSet, Node, ...)  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              v               v               v
   ┌──────────────────┐  ┌──────────────────┐  ...
   │   Worker Node 1  │  │   Worker Node 2  │
   │                  │  │                  │
   │  ┌────────────┐  │  │  ┌────────────┐  │
   │  │  kubelet   │  │  │  │  kubelet   │  │
   │  │  kube-proxy│  │  │  │  kube-proxy│  │
   │  │  Container │  │  │  │  Container │  │
   │  │  Runtime   │  │  │  │  Runtime   │  │
   │  └────────────┘  │  │  └────────────┘  │
   └──────────────────┘  └──────────────────┘
```

| 컴포넌트           | 역할                                              |
|--------------------|---------------------------------------------------|
| API Server         | 모든 K8s 오브젝트의 CRUD API 제공. 인증/인가 처리 |
| etcd               | 클러스터 상태 저장소 (분산 KV 스토어)             |
| Scheduler          | 새 Pod를 적합한 노드에 배치                       |
| Controller Manager | 오브젝트 상태를 원하는 상태로 유지                |
| kubelet            | 노드에서 Pod 실행/모니터링                        |
| kube-proxy         | 노드 네트워크 규칙 관리 (Service 라우팅)          |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 오브젝트

| 오브젝트        | 설명                                                      |
|-----------------|-----------------------------------------------------------|
| Pod             | K8s 최소 배포 단위. 1개 이상의 컨테이너 묶음              |
| ReplicaSet      | 지정된 수의 Pod 복제본 유지                               |
| Deployment      | ReplicaSet 관리 + 롤링 업데이트/롤백                      |
| StatefulSet     | 상태 있는 애플리케이션 (DB 등). 고정 네트워크 ID, 스토리지 |
| DaemonSet       | 모든 노드에 Pod 1개씩 실행 (로그 수집, 모니터링 에이전트) |
| Job             | 일회성 작업 실행 후 완료                                  |
| CronJob         | 스케줄 기반 Job 실행                                      |
| Service         | Pod 집합에 대한 안정적인 네트워크 엔드포인트              |
| Ingress         | HTTP/HTTPS 라우팅 규칙 (L7 로드밸런서)                    |
| ConfigMap       | 설정 데이터 저장 (비민감 정보)                            |
| Secret          | 민감 데이터 저장 (비밀번호, 토큰 등)                      |
| PersistentVolume| 클러스터 수준 스토리지 리소스                             |
| Namespace       | 클러스터 내 논리적 격리 단위                              |
| HPA             | CPU/메모리 기반 Pod 자동 수평 확장                        |

[⬆ 목차로 돌아가기](#목차)

---

## 4. kubectl 기본 명령어

### 조회

```bash
# 오브젝트 목록
kubectl get pods
kubectl get pods -n kube-system          # 네임스페이스 지정
kubectl get pods -A                      # 전체 네임스페이스
kubectl get pods -o wide                 # 노드 정보 포함
kubectl get pods -o yaml                 # YAML 출력
kubectl get pods -l app=my-app           # 레이블 셀렉터

# 상세 정보
kubectl describe pod my-pod
kubectl describe node my-node

# 로그
kubectl logs my-pod
kubectl logs my-pod -c my-container      # 멀티 컨테이너
kubectl logs my-pod -f                   # 실시간 스트리밍
kubectl logs my-pod --previous           # 이전 컨테이너 로그

# 이벤트
kubectl get events --sort-by='.lastTimestamp'
kubectl get events -n my-namespace
```

### 실행 & 접속

```bash
# Pod 내 명령 실행
kubectl exec my-pod -- ls /app
kubectl exec -it my-pod -- /bin/bash

# 포트 포워딩 (로컬 테스트용)
kubectl port-forward pod/my-pod 8080:80
kubectl port-forward svc/my-service 8080:80

# 파일 복사
kubectl cp my-pod:/app/log.txt ./log.txt
kubectl cp ./config.yaml my-pod:/app/config.yaml
```

### 생성 & 수정 & 삭제

```bash
# 적용 (생성 또는 업데이트)
kubectl apply -f deployment.yaml
kubectl apply -f ./k8s/                  # 디렉토리 전체

# 즉시 생성 (테스트용)
kubectl run nginx --image=nginx:1.25

# 수정
kubectl edit deployment my-app
kubectl set image deployment/my-app my-app=myapp:v2.0

# 스케일
kubectl scale deployment my-app --replicas=3

# 삭제
kubectl delete pod my-pod
kubectl delete -f deployment.yaml
kubectl delete pod my-pod --grace-period=0 --force   # 강제 삭제
```

### 컨텍스트 관리

```bash
# 컨텍스트 목록
kubectl config get-contexts

# 컨텍스트 전환
kubectl config use-context my-cluster

# 현재 컨텍스트
kubectl config current-context

# 기본 네임스페이스 변경
kubectl config set-context --current --namespace=my-namespace
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Pod & Deployment

### Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: my-app
    version: v1
spec:
  containers:
    - name: app
      image: myapp:1.0.0
      ports:
        - containerPort: 8080
      env:
        - name: APP_ENV
          value: production
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
  restartPolicy: Always
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 최대 추가 Pod 수
      maxUnavailable: 0  # 최대 불가용 Pod 수 (무중단 배포)

  template:
    metadata:
      labels:
        app: my-app
        version: v1.2.3
    spec:
      containers:
        - name: my-app
          image: 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/my-app:v1.2.3
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          envFrom:
            - configMapRef:
                name: my-app-config
            - secretRef:
                name: my-app-secret
```

### 롤아웃 관리

```bash
# 롤아웃 상태 확인
kubectl rollout status deployment/my-app

# 롤아웃 이력
kubectl rollout history deployment/my-app

# 롤백
kubectl rollout undo deployment/my-app
kubectl rollout undo deployment/my-app --to-revision=2

# 일시 중지 / 재개
kubectl rollout pause deployment/my-app
kubectl rollout resume deployment/my-app
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Service & Ingress

### Service 유형

| 유형          | 설명                                              |
|---------------|---------------------------------------------------|
| ClusterIP     | 클러스터 내부 통신 (기본값)                       |
| NodePort      | 노드 IP:포트로 외부 접근 (30000-32767)            |
| LoadBalancer  | 클라우드 LB 프로비저닝 (AWS ELB 등)               |
| ExternalName  | 외부 DNS 이름으로 매핑                            |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
spec:
  type: ClusterIP
  selector:
    app: my-app        # 레이블이 일치하는 Pod로 트래픽 전달
  ports:
    - port: 80         # Service 포트
      targetPort: 8080 # Pod 포트
      protocol: TCP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app.example.com
      secretName: tls-secret
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-svc
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-svc
                port:
                  number: 80
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. ConfigMap & Secret

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  APP_ENV: production
  LOG_LEVEL: info
  config.yaml: |
    server:
      port: 8080
      timeout: 30s
```

### Secret

```bash
# 명령어로 생성
kubectl create secret generic my-app-secret \
  --from-literal=DB_PASSWORD=SecurePassword123 \
  --from-literal=API_KEY=SecureKey123

# 파일에서 생성
kubectl create secret generic tls-secret \
  --from-file=tls.crt=./cert.pem \
  --from-file=tls.key=./key.pem \
  --type=kubernetes.io/tls
```

```yaml
# YAML로 생성 (base64 인코딩 필요)
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secret
type: Opaque
data:
  DB_PASSWORD: U2VjdXJlUGFzc3dvcmQxMjM=   # base64
stringData:
  API_KEY: SecureKey123   # 평문 (자동 인코딩)
```

### Pod에서 사용

```yaml
spec:
  containers:
    - name: app
      # 환경변수로 주입
      envFrom:
        - configMapRef:
            name: my-app-config
        - secretRef:
            name: my-app-secret

      # 볼륨으로 마운트
      volumeMounts:
        - name: config-vol
          mountPath: /app/config
          readOnly: true

  volumes:
    - name: config-vol
      configMap:
        name: my-app-config
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. Storage

### PersistentVolume & PersistentVolumeClaim

```yaml
# PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce   # RWO: 단일 노드 읽기/쓰기
  storageClassName: gp3
  resources:
    requests:
      storage: 20Gi
```

```yaml
# Pod에서 PVC 사용
spec:
  containers:
    - name: app
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: my-pvc
```

### Access Mode

| 모드  | 설명                          | 지원 스토리지          |
|-------|-------------------------------|------------------------|
| RWO   | ReadWriteOnce (단일 노드 R/W) | EBS, 로컬 디스크       |
| ROX   | ReadOnlyMany (다중 노드 R)    | NFS, EFS               |
| RWX   | ReadWriteMany (다중 노드 R/W) | NFS, EFS, CephFS       |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 리소스 관리

### Resource Requests & Limits

```yaml
resources:
  requests:
    cpu: "200m"      # 0.2 vCPU (스케줄링 기준)
    memory: "256Mi"  # 256 MiB (스케줄링 기준)
  limits:
    cpu: "1000m"     # 1 vCPU (초과 시 스로틀링)
    memory: "1Gi"    # 1 GiB (초과 시 OOMKilled)
```

### HPA (Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### LimitRange & ResourceQuota

```yaml
# 네임스페이스 기본 리소스 제한
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
```

```yaml
# 네임스페이스 전체 리소스 할당량
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 네임스페이스 & RBAC

### 네임스페이스

```bash
# 생성
kubectl create namespace my-app

# 기본 네임스페이스 변경
kubectl config set-context --current --namespace=my-app
```

### RBAC

```yaml
# Role (네임스페이스 범위)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: my-app
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "update", "patch"]
```

```yaml
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: my-app
subjects:
  - kind: ServiceAccount
    name: my-service-account
    namespace: my-app
  - kind: User
    name: developer@example.com
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 헬스체크

```yaml
spec:
  containers:
    - name: app
      # 시작 완료 확인 (초기화 시간이 긴 앱)
      startupProbe:
        httpGet:
          path: /health
          port: 8080
        failureThreshold: 30
        periodSeconds: 10

      # 생존 확인 (실패 시 컨테이너 재시작)
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8080
        initialDelaySeconds: 10
        periodSeconds: 15
        failureThreshold: 3

      # 트래픽 수신 준비 확인 (실패 시 Service에서 제외)
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 10
        failureThreshold: 3
```

| Probe 유형    | 실패 시 동작                  | 용도                        |
|---------------|-------------------------------|-----------------------------|
| startupProbe  | 컨테이너 재시작               | 느린 초기화 앱 보호         |
| livenessProbe | 컨테이너 재시작               | 데드락, 무한루프 감지       |
| readinessProbe| Service 엔드포인트에서 제외   | 배포 중 트래픽 차단         |

[⬆ 목차로 돌아가기](#목차)

---

## 12. Tips

### 자주 쓰는 패턴

```bash
# 특정 레이블의 Pod 로그 한번에 보기 (stern 도구)
stern -l app=my-app -n production

# 리소스 사용량 확인
kubectl top pods
kubectl top nodes

# 노드 상태 확인
kubectl get nodes -o wide
kubectl describe node my-node | grep -A5 "Conditions:"

# Pod가 Pending인 이유 확인
kubectl describe pod my-pod | grep -A10 "Events:"

# 강제 재시작 (이미지 변경 없이)
kubectl rollout restart deployment/my-app
```

### 디버깅용 임시 Pod

```bash
# 네트워크 디버깅
kubectl run debug --image=nicolaka/netshoot -it --rm -- bash

# 특정 Pod와 같은 네임스페이스에서 실행
kubectl debug -it my-pod --image=busybox --target=my-app
```

### 주의사항

⚠️ `resources.limits.memory`를 설정하지 않으면 메모리 누수 시 노드 전체에 영향을 줍니다. 반드시 설정합니다.

⚠️ `kubectl delete pod --force --grace-period=0`은 StatefulSet Pod에서 데이터 손상을 유발할 수 있습니다.

⚠️ Secret은 기본적으로 etcd에 base64 인코딩(암호화 아님)으로 저장됩니다. etcd 암호화 또는 외부 시크릿 관리자(AWS Secrets Manager, Vault) 사용을 권장합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Kubernetes Documentation: [kubernetes.io/docs](https://kubernetes.io/docs/home/) — ★★★☆☆
- kubectl Cheat Sheet: [kubernetes.io/docs/reference/kubectl/cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) — ★★★☆☆
- Kubernetes Patterns: [k8spatterns.io](https://k8spatterns.io/) — ★★☆☆☆

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
