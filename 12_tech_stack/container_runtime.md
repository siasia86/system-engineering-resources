# 컨테이너 런타임 (Container Runtime)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. CRI와 아키텍처](#2-cri와-아키텍처) / [3. cgroup 드라이버](#3-cgroup-드라이버) |
| [4. 런타임 종류](#4-런타임-종류) / [5. 사전 설정](#5-사전-설정) / [6. 런타임 비교](#6-런타임-비교) |

---

## 1. 개요

컨테이너 런타임은 컨테이너를 실제로 실행하는 소프트웨어입니다.
Kubernetes는 각 노드에 컨테이너 런타임이 설치되어 있어야 Pod를 실행할 수 있습니다.

```
┌─────────────────────────────────────────────┐
│                  kubelet                    │
│                     │                       │
│              CRI (gRPC socket)              │
│                     │                       │
│         ┌───────────┴───────────┐           │
│         │   Container Runtime   │           │
│         │  (containerd / CRI-O) │           │
│         └───────────┬───────────┘           │
│                     │                       │
│              OCI Runtime (runc)             │
│                     │                       │
│              Linux Kernel (cgroup/namespace)│
└─────────────────────────────────────────────┘
```

### 용어 정리

| 용어 | 설명                                                                   |
|------|------------------------------------------------------------------------|
| CRI  | Container Runtime Interface — kubelet과 런타임 간 gRPC 표준 인터페이스 |
| OCI  | Open Container Initiative — 컨테이너 이미지/런타임 표준 규격           |
| runc | OCI 표준 구현체, 실제 컨테이너 프로세스를 생성하는 저수준 런타임       |
| shim | 런타임과 kubelet 사이의 중간 프로세스 (containerd-shim 등)             |

[⬆ 목차로 돌아가기](#목차)

---

## 2. CRI와 아키텍처

Kubernetes v1.24부터 dockershim이 제거됐습니다.
Docker Engine을 사용하려면 `cri-dockerd` 어댑터가 별도로 필요합니다.

```
Kubernetes v1.24 이전          Kubernetes v1.24 이후
─────────────────────          ─────────────────────
kubelet                        kubelet
  └── dockershim (내장)          └── CRI socket
        └── Docker Engine              ├── containerd  (/run/containerd/containerd.sock)
              └── runc                 ├── CRI-O       (/var/run/crio/crio.sock)
                                       └── cri-dockerd (/run/cri-dockerd.sock)
                                             └── Docker Engine
```

### CRI 버전 요구사항

- Kubernetes v1.26+ → CRI API **v1** 필수
- CRI v1 미지원 런타임은 kubelet이 노드 등록 거부

[⬆ 목차로 돌아가기](#목차)

---

## 3. cgroup 드라이버

cgroup(control group)은 프로세스의 CPU/메모리 등 자원을 제한하는 Linux 커널 기능입니다.
kubelet과 컨테이너 런타임은 **반드시 동일한 cgroup 드라이버**를 사용해야 합니다.

### 드라이버 비교

| 드라이버   | 설명                                          | 권장 여부                   |
|------------|-----------------------------------------------|-----------------------------|
| `cgroupfs` | kubelet이 cgroup 파일시스템을 직접 조작       | ❌ systemd 환경에서 비권장  |
| `systemd`  | systemd가 cgroup 관리, kubelet은 systemd 경유 | ✅ 권장 (systemd init 환경) |

systemd를 init으로 사용하는 배포판(Ubuntu, RHEL 등)에서 `cgroupfs`를 쓰면
cgroup 관리자가 2개(systemd + kubelet)가 되어 리소스 압박 시 노드 불안정 발생합니다.

### cgroup v2

cgroup v2 환경에서는 `systemd` 드라이버 사용이 필수입니다.

```bash
# cgroup v2 여부 확인
stat -fc %T /sys/fs/cgroup/
# 출력: cgroup2fs → v2 / tmpfs → v1
```

### kubelet cgroup 드라이버 설정

```yaml
# KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
```

🟡 kubeadm v1.22+는 `cgroupDriver` 미설정 시 자동으로 `systemd`로 설정합니다.
🟡 Kubernetes v1.37부터 containerd 1.x(RuntimeConfig CRI RPC 미지원)는 kubelet과 호환 불가 예정입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 런타임 종류

### containerd

Kubernetes 환경에서 가장 널리 사용되는 런타임입니다. Docker Engine 내부에서도 사용됩니다.

```bash
# 설치 후 설정 파일 위치
/etc/containerd/config.toml

# 기본 설정 생성
containerd config default | sudo tee /etc/containerd/config.toml

# CRI 플러그인 활성화 확인 (disabled_plugins에 "cri" 없어야 함)
grep disabled_plugins /etc/containerd/config.toml
```

#### systemd cgroup 드라이버 설정

```toml
# containerd 2.x
[plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc]
  [plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]
    SystemdCgroup = true

# containerd 1.x
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true
```

```bash
sudo systemctl restart containerd
```

#### sandbox(pause) 이미지 변경

```toml
# containerd 2.x
[plugins.'io.containerd.cri.v1.runtime']
  sandbox_image = "registry.k8s.io/pause:3.10"

# containerd 1.x
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.10"
```

- CRI 소켓: `/run/containerd/containerd.sock`

### CRI-O

Kubernetes 전용으로 설계된 경량 런타임입니다. Red Hat 계열(OpenShift)에서 주로 사용합니다.

```bash
# 설정 파일
/etc/crio/crio.conf
/etc/crio/crio.conf.d/  # drop-in 디렉토리
```

#### cgroup 드라이버 설정 (cgroupfs로 변경 시)

```toml
# /etc/crio/crio.conf.d/02-cgroup-manager.conf
[crio.runtime]
conmon_cgroup = "pod"
cgroup_manager = "cgroupfs"
```

🟡 cgroupfs 사용 시 `conmon_cgroup = "pod"` 함께 설정 필요합니다.

#### sandbox 이미지 변경

```toml
[crio.image]
pause_image = "registry.k8s.io/pause:3.10"
```

```bash
# 설정 reload (재시작 불필요)
systemctl reload crio
```

- CRI 소켓: `/var/run/crio/crio.sock`

### Docker Engine (cri-dockerd)

v1.24 이후 직접 지원이 제거됐습니다. `cri-dockerd` 어댑터를 통해 사용 가능합니다.

```bash
# 설치 순서
# 1. Docker Engine 설치
# 2. cri-dockerd 설치 (https://github.com/Mirantis/cri-dockerd)
```

- CRI 소켓: `/run/cri-dockerd.sock`

### Mirantis Container Runtime (MCR)

구 Docker Enterprise Edition의 상용 후속 제품입니다. `cri-dockerd` 컴포넌트를 포함합니다.

- CRI 소켓: `cri-docker.socket` systemd unit으로 확인

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사전 설정

Kubernetes 노드 공통 사전 설정입니다.

```bash
# IPv4 패킷 포워딩 활성화
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system

# 확인
sysctl net.ipv4.ip_forward
# 출력: net.ipv4.ip_forward = 1
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 런타임 비교

| 항목            | containerd                        | CRI-O                     | Docker + cri-dockerd     |
|-----------------|-----------------------------------|---------------------------|--------------------------|
| 주요 사용처     | 범용 (EKS, GKE, AKS)              | OpenShift, RHEL 계열      | 레거시 환경 마이그레이션 |
| 경량성          | ★★★★☆                             | ★★★★★                     | ★★★☆☆                    |
| Kubernetes 전용 | 아니오 (Docker 내장)              | 예                        | 아니오                   |
| cgroup 기본값   | cgroupfs (설정 필요)              | systemd                   | cgroupfs (설정 필요)     |
| CRI 소켓        | `/run/containerd/containerd.sock` | `/var/run/crio/crio.sock` | `/run/cri-dockerd.sock`  |
| 공식 권장       | ✅                                | ✅                        | 🟡 어댑터 필요           |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Kubernetes Docs: [kubernetes.io/docs/setup/production-environment/container-runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/) — ★★★☆☆
- containerd: [containerd.io/docs/getting-started](https://containerd.io/docs/getting-started/) — ★★★☆☆
- CRI-O: [cri-o.io](https://cri-o.io/) — ★★★☆☆
- cri-dockerd: [github.com/Mirantis/cri-dockerd](https://github.com/Mirantis/cri-dockerd) — ★★☆☆☆

---

**작성일**: 2026-05-26

**마지막 업데이트**: 2026-05-26

© 2026 siasia86. Licensed under CC BY 4.0.
