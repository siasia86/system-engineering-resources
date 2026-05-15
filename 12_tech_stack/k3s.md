# k3s

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 설치](#4-설치) / [5. 주요 명령어](#5-주요-명령어) / [6. 네트워킹](#6-네트워킹) |
| [7. 스토리지](#7-스토리지) / [8. 멀티 노드 클러스터](#8-멀티-노드-클러스터) / [9. Tips](#9-tips) |

---

## 1. 개요

k3s는 Rancher Labs(SUSE)가 개발한 경량 Kubernetes 배포판. 단일 바이너리(~70MB)로 제공되며, 엣지/IoT/온프레미스 환경에 적합합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                     k3s vs k8s                               │
│                                                              │
│  k8s: etcd + kube-apiserver + kube-scheduler + ...           │
│  k3s: All-in-one single binary                               │
│       SQLite (기본) or etcd/PostgreSQL/MySQL                 │
│       Flannel CNI + Traefik Ingress + CoreDNS 내장           │
└──────────────────────────────────────────────────────────────┘
```

- 표준 Kubernetes API 100% 호환
- 메모리 요구사항: 512MB RAM (k8s 대비 약 50%)
- 제거된 컴포넌트: 클라우드 프로바이더 드라이버, 레거시 API, alpha 기능

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                      k3s Architecture                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Server (Control Plane)                │   │
│  │  kube-apiserver + kube-scheduler + kube-controller       │   │
│  │  + SQLite/etcd + Flannel + CoreDNS + Traefik             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                    │
│              ┌─────────────┴─────────────┐                      │
│              v                           v                      │
│  ┌───────────────────┐       ┌───────────────────┐              │
│  │   Agent (Worker)  │       │   Agent (Worker)  │              │
│  │  kubelet + kube-  │       │  kubelet + kube-  │              │
│  │  proxy + Flannel  │       │  proxy + Flannel  │              │
│  └───────────────────┘       └───────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

| 컴포넌트       | 설명                                              |
|----------------|---------------------------------------------------|
| k3s server     | Control Plane + 내장 컴포넌트 통합 프로세스       |
| k3s agent      | Worker 노드 프로세스 (kubelet + kube-proxy)       |
| SQLite         | 기본 데이터스토어 (단일 노드용)                   |
| Flannel        | 기본 CNI (VXLAN)                                  |
| Traefik        | 기본 Ingress Controller                           |
| local-path     | 기본 StorageClass (hostPath 기반)                 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념              | k8s              | k3s                              |
|-------------------|------------------|----------------------------------|
| 데이터스토어      | etcd (필수)      | SQLite (기본) / etcd 선택 가능   |
| CNI               | 별도 설치        | Flannel 내장                     |
| Ingress           | 별도 설치        | Traefik 내장                     |
| StorageClass      | 별도 설치        | local-path-provisioner 내장      |
| 설치 방법         | kubeadm 등       | 단일 스크립트                    |
| kubeconfig 위치   | ~/.kube/config   | /etc/rancher/k3s/k3s.yaml        |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

### Server (Control Plane) 설치

```bash
# 기본 설치 (최신 stable)
curl -sfL https://get.k3s.io | sh -

# 특정 버전 설치
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -

# Traefik 비활성화 (Nginx Ingress 사용 시)
curl -sfL https://get.k3s.io | sh -s - --disable traefik

# 외부 데이터스토어 (HA 구성용)
curl -sfL https://get.k3s.io | sh -s - \
  --datastore-endpoint="postgres://user:SecurePassword123@192.0.2.1:5432/k3s"
```

### Agent (Worker) 노드 추가

```bash
# Server에서 토큰 확인
sudo cat /var/lib/rancher/k3s/server/node-token

# Agent 노드에서 실행
curl -sfL https://get.k3s.io | K3S_URL=https://<SERVER_IP>:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -
```

### kubeconfig 설정

```bash
# root 외 사용자 접근
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# 또는 환경변수로 지정
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

### 제거

```bash
# Server 제거
/usr/local/bin/k3s-uninstall.sh

# Agent 제거
/usr/local/bin/k3s-agent-uninstall.sh
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령어

k3s는 kubectl을 내장하고 있어 `k3s kubectl` 또는 `kubectl`(kubeconfig 설정 후) 모두 사용 가능합니다.

```bash
# 노드 상태 확인
kubectl get nodes -o wide

# 전체 파드 확인
kubectl get pods -A

# k3s 서비스 상태
sudo systemctl status k3s
sudo systemctl status k3s-agent

# 로그 확인
sudo journalctl -u k3s -f
sudo journalctl -u k3s-agent -f

# 내장 컴포넌트 확인
kubectl get pods -n kube-system

# 클러스터 정보
kubectl cluster-info
kubectl get nodes --show-labels
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 네트워킹

### Flannel CNI

```bash
# Flannel 백엔드 변경 (설치 시 옵션)
curl -sfL https://get.k3s.io | sh -s - \
  --flannel-backend=wireguard-native   # 암호화 터널

# 기본 백엔드: vxlan
# 옵션: vxlan, wireguard-native, host-gw, none(CNI 직접 설치)
```

### Traefik Ingress

```yaml
# Ingress 예시
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-svc
                port:
                  number: 80
```

### MetalLB (온프레미스 LoadBalancer)

```bash
# k3s 기본 ServiceLB(klipper) 비활성화 후 MetalLB 사용
curl -sfL https://get.k3s.io | sh -s - --disable servicelb

kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 스토리지

### local-path-provisioner (기본)

```yaml
# PVC 예시 (기본 StorageClass 사용)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  # storageClassName 생략 시 local-path 사용
```

```bash
# 기본 StorageClass 확인
kubectl get storageclass

# 데이터 저장 경로 (기본값)
ls /var/lib/rancher/k3s/storage/
```

### Longhorn (분산 스토리지)

```bash
# Longhorn 설치 (멀티 노드 환경)
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.1/deploy/longhorn.yaml

# 기본 StorageClass 변경
kubectl patch storageclass local-path -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
kubectl patch storageclass longhorn -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 멀티 노드 클러스터

### HA 구성 (임베디드 etcd)

```bash
# 첫 번째 Server 노드 (클러스터 초기화)
curl -sfL https://get.k3s.io | sh -s - \
  --cluster-init \
  --tls-san <LOAD_BALANCER_IP>

# 두 번째, 세 번째 Server 노드
curl -sfL https://get.k3s.io | sh -s - \
  --server https://<FIRST_SERVER_IP>:6443 \
  --token <NODE_TOKEN> \
  --tls-san <LOAD_BALANCER_IP>

# Worker 노드
curl -sfL https://get.k3s.io | K3S_URL=https://<LOAD_BALANCER_IP>:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -
```

### 노드 구성 확인

```bash
kubectl get nodes -o wide
# NAME       STATUS   ROLES                       AGE
# server-1   Ready    control-plane,etcd,master   10m
# server-2   Ready    control-plane,etcd,master   8m
# server-3   Ready    control-plane,etcd,master   6m
# worker-1   Ready    <none>                      4m
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Tips

### 자주 쓰는 패턴

```bash
# 특정 노드에 파드 스케줄링 방지
kubectl taint nodes <NODE_NAME> key=value:NoSchedule

# 노드 레이블 추가 (nodeSelector 활용)
kubectl label nodes <NODE_NAME> role=worker

# k3s 설정 파일로 관리 (/etc/rancher/k3s/config.yaml)
# 설치 후 옵션을 파일로 관리 가능
cat /etc/rancher/k3s/config.yaml
```

```yaml
# /etc/rancher/k3s/config.yaml 예시
disable:
  - traefik
tls-san:
  - 192.0.2.1
  - k3s.example.com
node-label:
  - "role=master"
```

```bash
# 이미지 사전 로드 (에어갭 환경)
sudo k3s ctr images import my-image.tar

# 클러스터 백업 (SQLite)
sudo cp /var/lib/rancher/k3s/server/db/state.db ~/k3s-backup.db

# 클러스터 백업 (etcd)
sudo k3s etcd-snapshot save --name k3s-snapshot
```

### 주의사항

⚠️ 단일 노드 SQLite 구성은 HA가 아닙니다. 프로덕션에서는 임베디드 etcd 또는 외부 데이터스토어를 사용합니다.

⚠️ `/etc/rancher/k3s/k3s.yaml`은 클러스터 admin 자격증명을 포함합니다. 권한을 `600`으로 유지합니다.

⚠️ k3s 업그레이드 전 etcd 스냅샷 또는 DB 백업을 먼저 수행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- k3s Documentation: [docs.k3s.io](https://docs.k3s.io/) — ★★★☆☆
- k3s GitHub: [github.com/k3s-io/k3s](https://github.com/k3s-io/k3s) — ★★☆☆☆
- Rancher k3s: [rancher.com/docs/k3s](https://www.rancher.com/docs/k3s/latest/en/) — ★★☆☆☆
- [kubernetes_basic.md](./kubernetes_basic.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-13

**마지막 업데이트**: 2026-05-13

© 2026 siasia86. Licensed under CC BY 4.0.
