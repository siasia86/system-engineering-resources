# kind

kind(Kubernetes IN Docker)는 Docker 컨테이너를 Kubernetes 노드로 써서 PC 한 대에 클러스터를 만드는 도구입니다. 몇 분 안에 만들고 지울 수 있어 Kubernetes 학습, manifest·Helm chart 시험, CI에 맞습니다. 이 문서만으로 설치 → 클러스터 만들기 → 앱 배포 → 검증 → 삭제까지 따라 할 수 있게 썼습니다.

- 기준 판: kind v0.33.0(2026-08-26 release), 기본 노드 이미지 `kindest/node:v1.37.0`
- 예제 시험: 2026-11-27 설치(체크섬 일치)와 단일 노드 클러스터 생성·삭제를 실행(`kind create cluster --wait 180s` 약 36초, 노드 `v1.37.0`, 노드 OS Debian 13). 여러 노드 구성, 포트 매핑, 이미지 로드 등 나머지 명령은 미실행이며 kind 공식 문서 원본(kubernetes-sigs/kind `site/content/docs/user/`, 2026-11-23 확인)과 대조했습니다

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 첫 클러스터](#3-첫-클러스터)                                         |
| [4. 설정 파일](#4-설정-파일) / [5. 앱 배포와 접속](#5-앱-배포와-접속) / [6. 로컬 이미지 쓰기](#6-로컬-이미지-쓰기) |
| [7. 여러 클러스터](#7-여러-클러스터) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                         |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                                  |

---

## 1. 개요

```
host (Docker Engine)
  ├── container: kind-control-plane   ← API server, etcd, kubelet
  ├── container: kind-worker          ← kubelet
  └── container: kind-worker2         ← kubelet
       (each container runs containerd + kubelet inside)
```

| 항목      | kind             | k3s                   | minikube         |
|-----------|------------------|-----------------------|------------------|
| 노드      | Docker 컨테이너  | 실제 서버·VM 프로세스 | VM 또는 컨테이너 |
| 여러 노드 | 설정 파일로 쉽게 | 서버를 늘려야 함      | 지원 (`--nodes`) |
| 주 용도   | 시험, CI, 학습   | 경량 운영, 엣지       | 로컬 개발        |
| 운영 사용 | 하지 않음        | 가능                  | 하지 않음        |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### 2-1. 사전 조건

| 항목    | 확인                                             |
|---------|--------------------------------------------------|
| Docker  | `docker version`에 Server가 나옴 (Podman도 지원) |
| kubectl | `kubectl version --client` (클러스터 조작용)     |
| 자원    | 노드 하나에 메모리 2 GB 이상 여유 권장           |
| inotify | 노드가 여럿이면 한도를 올려야 할 수 있음 (9절)   |

### 2-2. kind 설치 (Linux)

```bash
VER=v0.33.0
[ "$(uname -m)" = x86_64 ]  && curl -Lo ./kind "https://kind.sigs.k8s.io/dl/${VER}/kind-linux-amd64"
[ "$(uname -m)" = aarch64 ] && curl -Lo ./kind "https://kind.sigs.k8s.io/dl/${VER}/kind-linux-arm64"
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind version
# kind v0.33.0 go1.26.7 linux/amd64
```

그 밖의 방법: macOS `brew install kind`, Windows `choco install kind`, Go 개발 환경 `go install sigs.k8s.io/kind@v0.33.0`.

### 2-3. kubectl 설치

kubectl이 없으면 Kubernetes 공식 안내대로 설치합니다. 판은 클러스터 Kubernetes 판과 앞뒤 한 단계 안에서 맞춥니다.

```bash
KVER=$(curl -Ls https://dl.k8s.io/release/stable.txt)
curl -LO "https://dl.k8s.io/release/${KVER}/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/release/${KVER}/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo install -m 0755 kubectl /usr/local/bin/kubectl
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 클러스터

```bash
kind create cluster                          # 이름 kind, 노드 1개 (control-plane)
kubectl cluster-info --context kind-kind     # API 서버 주소 확인
kubectl get nodes                            # kind-control-plane  Ready
docker ps --filter name=kind                 # 노드 컨테이너
```

- `kind create cluster`는 kubeconfig(`~/.kube/config`)에 `kind-<클러스터 이름>` context를 추가하고 그 context로 바꿉니다.
- Kubernetes 판을 고르려면 `--image kindest/node:v1.36.4@sha256:...`처럼 release 안내에 적힌 다이제스트까지 붙인 이미지를 지정합니다. 각 kind 판은 함께 빌드된 노드 이미지만 보장합니다.

삭제:

```bash
kind delete cluster                          # 이름 kind 클러스터 삭제 (없어도 오류 없음)
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설정 파일

`kind-config.yaml` — control-plane 1대, worker 2대, 호스트 포트 연결

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: lab
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080      # 노드 컨테이너 안 포트 (NodePort)
        hostPort: 8080            # 호스트 포트
        listenAddress: "127.0.0.1"
  - role: worker
  - role: worker
```

```bash
kind create cluster --config kind-config.yaml
kubectl get nodes                            # lab-control-plane, lab-worker, lab-worker2
```

| 설정                      | 용도                                                     |
|---------------------------|----------------------------------------------------------|
| `nodes[].role`            | `control-plane` 또는 `worker`                            |
| `nodes[].image`           | 노드별 이미지 (판 고정)                                  |
| `extraPortMappings`       | 호스트 포트 → 노드 컨테이너 포트 (NodePort·Ingress 접속) |
| `extraMounts`             | 호스트 디렉터리를 노드 컨테이너에 연결                   |
| `networking.podSubnet` 등 | Pod·Service 대역 (사내 대역과 겹칠 때)                   |
| `kubeadmConfigPatches`    | 노드 라벨 등 kubeadm 설정 덧붙이기                       |

포트 연결과 노드 수는 클러스터를 만들 때만 정할 수 있습니다. 바꾸려면 지우고 다시 만듭니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 앱 배포와 접속

4절 `lab` 클러스터 기준입니다.

```bash
kubectl create deployment web --image=nginx:1.29-alpine --replicas=2
kubectl rollout status deployment/web
```

`web-svc.yaml` — 4절에서 호스트 8080에 연결한 NodePort 30080으로 공개

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

```bash
kubectl apply -f web-svc.yaml
curl http://127.0.0.1:8080/                  # nginx 시작 페이지
```

포트 연결 없이 잠깐 확인할 때는 `kubectl port-forward`를 씁니다.

```bash
kubectl port-forward deployment/web 8081:80
curl http://127.0.0.1:8081/
```

LoadBalancer 형식 Service와 Ingress는 kind 공식 문서의 LoadBalancer(cloud-provider-kind)·Ingress 안내대로 추가 구성이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 로컬 이미지 쓰기

kind 노드는 호스트 Docker의 이미지를 직접 보지 못하므로, 빌드한 이미지를 노드로 넣어 줍니다.

```bash
docker build -t my-app:0.1.0 .
kind load docker-image my-app:0.1.0 --name lab
docker exec lab-control-plane crictl images | grep my-app     # 노드 안 이미지 확인
```

- 태그를 `latest`로 쓰거나 생략하면 Kubernetes가 매번 원격에서 받으려고 해서(`imagePullPolicy: Always`) 넣어 둔 이미지를 쓰지 않습니다. `0.1.0`처럼 고정 태그를 쓰거나 `imagePullPolicy: IfNotPresent`를 지정합니다.
- 이미지 파일은 `kind load image-archive my-app.tar`로 넣습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 여러 클러스터

```bash
kind create cluster --name dev
kind create cluster --name test
kind get clusters                            # dev, test
kubectl config get-contexts                  # kind-dev, kind-test
kubectl config use-context kind-dev
kind delete cluster --name test
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용     | 명령                                             | 기대 결과                          |
|------|---------------|--------------------------------------------------|------------------------------------|
| 1    | 설치          | `kind version`, `kubectl version --client`       | 판 번호                            |
| 2    | 클러스터 존재 | `kind get clusters`                              | 만든 클러스터 이름                 |
| 3    | context       | `kubectl config current-context`                 | `kind-<이름>`                      |
| 4    | 노드          | `kubectl get nodes -o wide`                      | 모든 노드 `Ready`                  |
| 5    | 시스템 Pod    | `kubectl get pods -n kube-system`                | 모두 `Running`                     |
| 6    | 배포          | `kubectl rollout status deployment/web`          | `successfully rolled out`          |
| 7    | 접속          | `curl http://127.0.0.1:8080/`                    | 앱 응답                            |
| 8    | 로컬 이미지   | `docker exec <노드> crictl images`               | 넣은 이미지가 있음                 |
| 9    | 삭제          | `kind delete cluster --name <이름>`, `docker ps` | 노드 컨테이너 없음, context 제거됨 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                          | 원인                                          | 해결 방법                                              |
|-----------------------------------------------|-----------------------------------------------|--------------------------------------------------------|
| 노드 여럿일 때 Pod 오류 `too many open files` | 호스트 inotify 한도 (namespace로 나뉘지 않음) | 아래 sysctl 값으로 올림                                |
| `permission denied` (Docker 소켓)             | 사용자가 docker 그룹이 아님                   | docker 그룹 추가 후 재로그인, 또는 rootless 구성       |
| `ErrImagePull` (로컬에서 빌드한 이미지)       | 노드에 이미지가 없음                          | `kind load docker-image`, 고정 태그 사용 (6절)         |
| 호스트에서 NodePort로 접속 안 됨              | 포트 연결을 만들지 않음                       | `extraPortMappings`로 다시 만들기, 또는 `port-forward` |
| 클러스터 생성 중 시간 초과                    | 메모리 부족, 노드 이미지 받는 중              | `docker stats` 확인, 노드 수 줄이기                    |
| AppArmor 환경에서 이상 동작                   | AppArmor 프로필이 노드 컨테이너를 제한        | kind known issues의 AppArmor 항목 참고                 |
| 클러스터 대역이 사내망과 겹침                 | 기본 Pod·Service·Docker 대역 충돌             | `networking.podSubnet`·`serviceSubnet` 지정            |

inotify 한도 (kind 공식 known issues의 권장 값):

```bash
sudo sysctl fs.inotify.max_user_watches=524288
sudo sysctl fs.inotify.max_user_instances=512
# 계속 적용하려면 /etc/sysctl.d/ 아래 파일에 같은 두 줄을 넣음
```

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Kubernetes 기본](./kubernetes_basic.md) — Pod, Deployment, Service
- [Kubernetes 설치](./kubernetes_install.md) — kubeadm, k3s로 실제 클러스터
- [Kubernetes 장애 진단](./kubernetes_troubleshooting.md) — Pod 상태별 원인
- [k3s](./k3s.md) — 경량 Kubernetes
- [Helm](./helm.md) — chart 배포
- [Docker 네트워크](./docker_network.md) — 노드 컨테이너가 붙는 Docker 네트워크
- [systemd 포함 컨테이너](./systemd_container.md) — kind 노드처럼 systemd를 돌리는 컨테이너와 inotify 한도

---

## 참고 자료

- kind Documentation: [Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/) — ★★★☆☆
- kind Documentation: [Configuration](https://kind.sigs.k8s.io/docs/user/configuration/) — ★★★☆☆
- kind Documentation: [Known Issues](https://kind.sigs.k8s.io/docs/user/known-issues/) — ★★★☆☆
- kind Documentation: [LoadBalancer](https://kind.sigs.k8s.io/docs/user/loadbalancer/) · [Ingress](https://kind.sigs.k8s.io/docs/user/ingress/) — ★★★☆☆
- Kubernetes Documentation: [Install kubectl on Linux](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) — ★★★☆☆
- GitHub: [kubernetes-sigs/kind releases](https://github.com/kubernetes-sigs/kind/releases) — v0.33.0 확인 2026-11-23 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
