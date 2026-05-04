# Kubernetes 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. k3s 설치 (경량)](#2-k3s-설치-경량) / [3. kubeadm 설치 (풀 클러스터)](#3-kubeadm-설치-풀-클러스터) |
| [4. kubectl 기본 사용법](#4-kubectl-기본-사용법) / [5. 핵심 리소스](#5-핵심-리소스) / [6. 실무 팁](#6-실무-팁) |
| [7. 트러블슈팅](#7-트러블슈팅) |

---

## 1. 개요

### k3s vs kubeadm 선택 기준

| 항목          | k3s                           | kubeadm                       |
|---------------|-------------------------------|-------------------------------|
| 설치 난이도   | 매우 쉬움 (단일 명령)         | 복잡 (단계별 설정 필요)       |
| 리소스 사용   | 적음 (512 MB RAM)             | 많음 (2 GB+ RAM)              |
| 대상 환경     | 개발, 엣지, 소규모 프로덕션   | 엔터프라이즈 프로덕션         |
| HA 구성       | 가능 (임베디드 etcd)          | 가능 (외부 etcd 권장)         |
| 권장 상황     | 빠른 시작, 단일 노드           | 대규모 멀티 노드 클러스터     |

### 시스템 요구사항

| 항목   | k3s (단일 노드)   | kubeadm (노드당)  |
|--------|-------------------|-------------------|
| CPU    | 1 core            | 2 core 이상       |
| RAM    | 512 MB            | 2 GB 이상         |
| 디스크 | 5 GB              | 20 GB 이상        |
| OS     | Ubuntu 20.04+     | Ubuntu 22.04+ / Rocky 9+ |

[⬆ 목차로 돌아가기](#목차)

---

## 2. k3s 설치 (경량)

### 2-1. Server (Control Plane) 설치

```bash
# 단일 명령 설치
curl -sfL https://get.k3s.io | sh -

# 특정 버전 지정
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="v1.31.4+k3s1" sh -

sudo systemctl status k3s --no-pager | head -5
```

### 2-2. kubectl 설정

```bash
# k3s는 kubectl 내장 (k3s kubectl)
# 표준 kubectl로 사용하려면 kubeconfig 복사
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

kubectl get nodes
```

### 2-3. Agent (Worker) 노드 추가

```bash
# Server에서 토큰 확인
sudo cat /var/lib/rancher/k3s/server/node-token

# Agent 노드에서 실행
curl -sfL https://get.k3s.io | \
    K3S_URL=https://10.0.1.10:6443 \
    K3S_TOKEN=<node-token> \
    sh -
```

### 2-4. 제거

```bash
# Server
/usr/local/bin/k3s-uninstall.sh

# Agent
/usr/local/bin/k3s-agent-uninstall.sh
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. kubeadm 설치 (풀 클러스터)

### 3-1. 사전 준비 (모든 노드)

```bash
# swap 비활성화
sudo swapoff -a
sudo sed -i '/swap/d' /etc/fstab

# 커널 모듈 로드
sudo tee /etc/modules-load.d/k8s.conf << 'EOF'
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# sysctl 설정
sudo tee /etc/sysctl.d/k8s.conf << 'EOF'
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system
```

### 3-2. containerd 설치 (모든 노드)

```bash
sudo apt install containerd -y
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
# SystemdCgroup = true 설정
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
```

### 3-3. kubeadm / kubelet / kubectl 설치 (모든 노드)

```bash
sudo apt install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key \
    | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
    https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' \
    | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl   # 자동 업그레이드 방지
```

### 3-4. Control Plane 초기화

```bash
sudo kubeadm init \
    --pod-network-cidr=10.244.0.0/16 \
    --apiserver-advertise-address=10.0.1.10

# kubeconfig 설정
mkdir -p ~/.kube
sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

# CNI 플러그인 설치 (Flannel)
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

### 3-5. Worker 노드 조인

```bash
# kubeadm init 출력에서 join 명령 복사 후 Worker 노드에서 실행
sudo kubeadm join 10.0.1.10:6443 \
    --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash>

# 토큰 만료 시 재생성
kubeadm token create --print-join-command
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. kubectl 기본 사용법

### 클러스터 상태 확인

```bash
kubectl get nodes
kubectl get nodes -o wide
kubectl cluster-info
kubectl get all -n kube-system
```

### 리소스 조회

```bash
# Pod
kubectl get pods -A                          # 전체 네임스페이스
kubectl get pods -n myapp -o wide
kubectl describe pod <pod-name> -n myapp

# 로그
kubectl logs <pod-name> -n myapp
kubectl logs -f --tail=100 <pod-name> -n myapp
kubectl logs <pod-name> -c <container-name>  # 멀티 컨테이너

# 접속
kubectl exec -it <pod-name> -n myapp -- sh
```

### 리소스 적용 / 삭제

```bash
kubectl apply -f deployment.yaml
kubectl delete -f deployment.yaml
kubectl delete pod <pod-name> -n myapp

# 강제 재시작
kubectl rollout restart deployment/<name> -n myapp
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 핵심 리소스

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: nginx:1.27
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc
  namespace: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP   # ClusterIP / NodePort / LoadBalancer
```

```bash
kubectl create namespace myapp
kubectl apply -f deployment.yaml -f service.yaml
kubectl get deploy,svc -n myapp
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실무 팁

### Tip 1: 네임스페이스로 환경 분리

```bash
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace prod

# 기본 네임스페이스 변경
kubectl config set-context --current --namespace=myapp
```

### Tip 2: ConfigMap / Secret으로 설정 분리

```bash
# ConfigMap
kubectl create configmap app-config \
    --from-literal=DB_HOST=10.0.1.10 \
    --from-literal=DB_PORT=5432

# Secret
kubectl create secret generic app-secret \
    --from-literal=DB_PASSWORD=SecurePassword123
```

### Tip 3: Rolling Update / Rollback

```bash
# 이미지 업데이트
kubectl set image deployment/myapp myapp=nginx:1.28 -n myapp

# 롤아웃 상태 확인
kubectl rollout status deployment/myapp -n myapp

# 롤백
kubectl rollout undo deployment/myapp -n myapp

# 히스토리
kubectl rollout history deployment/myapp -n myapp
```

### Tip 4: 리소스 사용량 확인

```bash
# metrics-server 설치 필요
kubectl top nodes
kubectl top pods -n myapp
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                              | 원인                          | 해결 방법                                              |
|-----------------------------------|-------------------------------|--------------------------------------------------------|
| Node `NotReady`                   | CNI 미설치 또는 kubelet 오류  | `kubectl describe node`, `journalctl -u kubelet`       |
| Pod `Pending`                     | 리소스 부족 또는 스케줄링 불가 | `kubectl describe pod` → Events 확인                  |
| Pod `CrashLoopBackOff`            | 컨테이너 시작 실패            | `kubectl logs <pod>` 확인                              |
| Pod `ImagePullBackOff`            | 이미지 없음 또는 인증 실패    | 이미지 태그 확인, imagePullSecrets 설정                |
| `connection refused` (apiserver)  | Control Plane 다운            | `sudo systemctl status kube-apiserver`                 |
| kubeadm init 실패 (swap)          | swap 활성화 상태              | `sudo swapoff -a`                                      |

```bash
# 이벤트 확인
kubectl get events -n myapp --sort-by='.lastTimestamp'

# 노드 상태 상세
kubectl describe node <node-name>

# kubelet 로그
sudo journalctl -u kubelet -f
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Kubernetes Documentation: [kubernetes.io/docs](https://kubernetes.io/docs/) — ★★★☆☆
- k3s Documentation: [docs.k3s.io](https://docs.k3s.io/) — ★★★☆☆
- kubeadm: [Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
