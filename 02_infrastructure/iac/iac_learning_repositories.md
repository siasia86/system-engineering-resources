# 순수 IaC 학습·테스트용 GitHub 저장소 비교
<!-- reference: _reference/github_references.md, _reference/docker_official_notes.md, _reference/terraform_official_notes.md, _reference/ansible_official_notes.md, _reference/kubernetes_official_notes.md, _reference/hashicorp_vault_official_notes.md -->

이 문서는 애플리케이션 도메인이나 특정 가상화 플랫폼이 아닌 **순수 IaC 학습·테스트**를 목적으로 합니다. Docker, Ansible, Vault, Kubernetes, Terraform을 조합하여 인프라를 코드로 정의하고, 로컬 또는 테스트 환경에서 반복 검증할 수 있는 GitHub 저장소를 비교합니다.

> IaC(Infrastructure as Code): 서버·네트워크·권한·애플리케이션 인프라의 원하는 상태를 코드로 정의하고 반복적으로 재현하는 방식입니다. Terraform은 리소스 프로비저닝, Ansible은 OS·애플리케이션 설정에 주로 사용합니다.

> GitOps: Git 저장소를 인프라와 애플리케이션의 원하는 상태 저장소로 사용하고, 배포 도구가 실제 환경을 Git 상태에 맞추는 운영 방식입니다.

## 목차

| 섹션                                                     | 내용                    |
|----------------------------------------------------------|-------------------------|
| [1. 검색 범위와 결론](#1-검색-범위와-결론)               | 검색 기준과 핵심 판단   |
| [2. 후보 저장소 비교](#2-후보-저장소-비교)               | IaC·DevOps 학습 후보    |
| [3. 일반 IaC 학습 기준 추천](#3-일반-iac-학습-기준-추천) | 도구 체인별 선택        |
| [4. 학습 목적별 선택](#4-학습-목적별-선택)               | 목적별 우선순위         |
| [5. 권장 통합 실습 구조](#5-권장-통합-실습-구조)         | 자체 학습 저장소 구성안 |
| [6. 실행 전 검증과 보안](#6-실행-전-검증과-보안)         | 비용·자격증명·코드 검토 |
| [7. 롤백과 운영 주의사항](#7-롤백과-운영-주의사항)       | 변경 복구와 유지관리    |

## 1. 검색 범위와 결론

### 문서 범위

#### 포함 범위

- Terraform 기반 인프라 프로비저닝
- Ansible 기반 OS·서비스 설정
- Docker·Docker Compose 기반 로컬 실습
- Kubernetes 클러스터와 애플리케이션 배포
- HashiCorp Vault 또는 OpenBao 기반 Secret 관리
- CI 검증, GitOps, 재현 가능한 테스트 환경

#### 제외 범위

- 게임·웹 애플리케이션 자체의 기능 구현
- 특정 운영체제나 가상화 플랫폼에 종속된 운영 가이드
- 단순 도구 소개만 있고 실행 가능한 IaC 예제가 없는 저장소
- 운영 환경에 바로 적용하기 위한 상용 아키텍처 설계

Homelab 저장소는 순수 IaC 핵심 후보가 아니라, IaC·GitOps·검증 구조를 보완하는 운영 사례로만 분류합니다.

### 검색 기준

2026-09-17 기준으로 GitHub 공개 저장소를 검색하고 다음 항목을 확인했습니다.

- 저장소 설명과 README의 학습·실습 목적
- Terraform, Ansible, Docker, Kubernetes, Vault 관련 실제 파일 존재 여부
- 로컬·클라우드 실행 환경과 Provider 지원 여부
- GitHub 최근 갱신일과 저장소의 실습 범위
- 클라우드 비용이나 수동 작업 등 실행상의 제약

GitHub Stars나 저장소 규모는 품질을 보장하지 않습니다. 공개 저장소의 스크립트와 Terraform은 실행 전에 직접 검토해야 합니다.

### 핵심 결론

이번 검색에서는 다섯 도구를 모두 최신 방식으로 묶은 단일 학습 저장소를 확인하지 못했습니다. 후보 저장소는 다음과 같이 도구 범위가 나뉩니다.

- 일부 후보는 HashiCorp Vault 대신 OpenBao 또는 Kubernetes Secret을 사용합니다.
- 일부 후보는 로컬 환경보다 AWS, GCP, Proxmox 등 특정 플랫폼을 대상으로 합니다.
Kubernetes는 CRI 호환 컨테이너 런타임을 사용하므로 Docker Engine을 클러스터 런타임으로 직접 설치할 필요가 없습니다. Docker는 이미지 빌드와 Compose 기반 로컬 실습에 사용할 수 있으며, Kubernetes 노드는 `containerd` 또는 CRI-O 같은 CRI 구현체를 사용할 수 있습니다.

일반적인 IaC 학습 목적에는 다음 조합이 가장 적합합니다.

```text
전체 도구 체인 학습
└── inno-devops-labs/DevOps-Core-Course
    ├── Docker
    ├── Terraform / OpenTofu
    ├── Ansible
    ├── Kubernetes
    ├── OpenBao
    └── GitOps / Observability

구성 요소별 보강
├── m-aboud/infra-automation-lab  → Terraform·Ansible·Docker·Kubernetes
├── sethvargo/vault-on-gke        → HashiCorp Vault·Terraform·Kubernetes
└── khuedoan/homelab              → GitOps·Secret·모니터링·백업

```

## 2. 후보 저장소 비교

### 전체 비교

1~4번은 순수 IaC 학습·테스트에 직접 사용하는 핵심 후보입니다. 5~6번은 IaC와 GitOps 운영 구조를 보완하는 Homelab 사례입니다.

| 우선순위 | 저장소                                                                                                    | 주요 구성                                                | 최근 갱신  | 판단            |
|----------|-----------------------------------------------------------------------------------------------------------|----------------------------------------------------------|------------|-----------------|
| 1        | [inno-devops-labs/DevOps-Core-Course](https://github.com/inno-devops-labs/DevOps-Core-Course)             | Docker, Terraform, Ansible, Kubernetes, OpenBao, Argo CD | 2026-09-10 | 핵심 학습 후보  |
| 2        | [m-aboud/infra-automation-lab](https://github.com/m-aboud/infra-automation-lab)                           | Terraform, Ansible, Docker Compose, Kubernetes           | 2026-05-26 | 핵심 구조 후보  |
| 3        | [sethvargo/vault-on-gke](https://github.com/sethvargo/vault-on-gke)                                       | HashiCorp Vault, Terraform, Kubernetes, GKE              | 2026-09-01 | Vault 보강 후보 |
| 4        | [Artemmkin/infrastructure-as-code-tutorial](https://github.com/Artemmkin/infrastructure-as-code-tutorial) | Packer, Terraform, Ansible, Vagrant, Docker, Kubernetes  | 2026-09-16 | 개념 보강 후보  |
| 5        | [khuedoan/homelab](https://github.com/khuedoan/homelab)                                                   | Ansible, Docker, K3s, Terraform, GitOps, Secret 관리     | 2026-09-17 | 보완 운영 사례  |
| 6        | [lisenet/kubernetes-homelab](https://github.com/lisenet/kubernetes-homelab)                               | kubeadm, Ansible, Docker, Helm, Terraform                | 2026-09-16 | 보완 운영 사례  |

표의 최근 갱신은 GitHub API의 `repository.updated_at` 값이며, 코드 품질이나 최신 호환성을 의미하지 않습니다.

### 도구 지원 범위

| 저장소                            | Docker | Terraform | Ansible | Vault/OpenBao    | Kubernetes | GitOps |
|-----------------------------------|--------|-----------|---------|------------------|------------|--------|
| `DevOps-Core-Course`              | ✅     | ✅        | ✅      | OpenBao          | ✅         | ✅     |
| `infra-automation-lab`            | ✅     | ✅        | ✅      | ❌               | ✅         | ❌     |
| `vault-on-gke`                    | ❌     | ✅        | ❌      | Vault            | ✅         | ❌     |
| `infrastructure-as-code-tutorial` | ✅     | ✅        | ✅      | ❌               | ✅         | ❌     |
| `khuedoan/homelab`                | ✅     | ✅        | ✅      | External Secrets | ✅         | ✅     |
| `kubernetes-homelab`              | ✅     | ✅        | ✅      | ❌               | ✅         | 🟡     |

이 표에서 `❌`는 저장소의 README·구성 파일에서 해당 도구의 학습 구성을 확인하지 못했다는 의미입니다. 도구 자체를 사용할 수 없다는 의미는 아닙니다.

### 라이선스와 재현성

| 저장소                            | 라이선스     | 기본 브랜치 | 재현성 주의사항                              |
|-----------------------------------|--------------|-------------|----------------------------------------------|
| `DevOps-Core-Course`              | 확인 필요    | `master`    | Fork 후 학습자 파일을 별도 관리              |
| `infra-automation-lab`            | MIT          | `main`      | AWS Provider와 자격증명 필요                 |
| `vault-on-gke`                    | Apache-2.0   | `master`    | GKE 비용과 오래된 Terraform 요구사항 확인    |
| `infrastructure-as-code-tutorial` | Apache-2.0   | `master`    | README에서 2018년 작성 및 유지보수 주의 명시 |
| `khuedoan/homelab`                | GPL-3.0      | `master`    | README에서 Alpha 상태 명시                   |
| `kubernetes-homelab`              | BSD-3-Clause | `master`    | 환경별 버전·네트워크 차이 확인               |

학습 환경을 재현할 때는 저장소의 기본 브랜치를 그대로 사용하지 말고 검증한 Commit SHA와 도구 버전을 기록합니다.

```bash
git rev-parse HEAD
git log -1 --format='%H %cs %s'
terraform version
ansible --version
kubectl version --client
```

### 2.1 `inno-devops-labs/DevOps-Core-Course`

링크: [github.com/inno-devops-labs/DevOps-Core-Course](https://github.com/inno-devops-labs/DevOps-Core-Course)

16주 형식의 단계별 DevOps 실습 과정입니다.

```text
Docker
  │
  v
CI/CD
  │
  v
Terraform / OpenTofu
  │
  v
Ansible + OpenBao
  │
  v
Kubernetes + Helm
  │
  v
Argo CD + Observability
```

> OpenBao: 이 저장소가 사용하는 Secret 관리 도구입니다. HashiCorp Vault 자체가 아니므로 두 제품의 라이선스·운영·버전 차이를 별도로 확인해야 합니다.

#### 장점

- Docker부터 Kubernetes까지 학습 순서가 명확합니다.
- Terraform과 Ansible을 별도 랩으로 다룹니다.
- Secret 관리, Helm, Argo CD, Prometheus, Loki를 함께 다룹니다.
- 학습자가 자신의 Fork에서 IaC 파일과 Kubernetes 매니페스트를 작성하는 구조입니다.
- 저장소 설명과 학습 구성이 비교적 최신입니다.

#### 제약

- HashiCorp Vault가 아니라 OpenBao입니다.
- VM 프로비저닝보다 전체 DevOps 학습 흐름에 초점을 둡니다.
- 로컬 Kubernetes는 Docker 기반 `k3d` 실습이 중심입니다.
- 특정 운영체제 VM이나 GPU 운영을 다루지 않습니다.

**전체 IaC와 DevOps 도구 체인을 학습하는 목적에는 가장 적합한 후보**입니다.

### 2.5 `khuedoan/homelab`

링크: [github.com/khuedoan/homelab](https://github.com/khuedoan/homelab)

실제 Homelab을 코드로 구축·운영하는 구조를 참고하기 좋은 저장소입니다.

포함 범위는 다음과 같습니다.

- Ansible 기반 설치와 설정
- Docker 기반 PXE 서비스
- K3s/Kubernetes
- Terraform 모듈
- Argo CD 기반 GitOps
- Prometheus, Grafana, Loki
- External Secrets 계열의 Secret 관리
- 백업·복구와 인프라 테스트

HashiCorp Vault를 직접 사용하는 저장소는 아니며 자체 Secret Generator와 External Secrets 구성이 중심입니다. README에는 프로젝트 상태가 Alpha로 표시되어 있으므로 실제 운영에 그대로 복사하기보다 다음 구조를 학습하는 용도로 사용합니다.

- GitOps 디렉터리 구성
- Kubernetes 설치 자동화
- Secret 관리 분리
- 모니터링과 백업 자동화
- 테스트와 검증 단계

### 2.2 `m-aboud/infra-automation-lab`

링크: [github.com/m-aboud/infra-automation-lab](https://github.com/m-aboud/infra-automation-lab)

작은 규모의 IaC 구조를 빠르게 읽고 실행하기 좋은 후보입니다.

```text
terraform/
├── modules/
└── environments/dev/

ansible/
├── roles/
└── site.yml

docker/
└── docker-compose.yml

kubernetes/
└── manifests/
```

포함 내용은 다음과 같습니다.

- Terraform AWS VPC
- Ansible Linux baseline
- Docker Compose
- Kubernetes Deployment, Service, HPA, NetworkPolicy
- Terraform, Ansible, Kubernetes 매니페스트, Dockerfile CI 검사

Vault는 포함되지 않으며 Terraform 예제가 AWS VPC 기반입니다. AWS 자격증명과 비용이 필요하므로 특정 로컬 환경의 직접 기반보다는 **구조와 CI 검증 패턴을 참고하는 저장소**로 보는 것이 적절합니다.

### 2.3 `sethvargo/vault-on-gke`

링크: [github.com/sethvargo/vault-on-gke](https://github.com/sethvargo/vault-on-gke)

HashiCorp Vault와 Terraform·Kubernetes의 연동을 별도로 학습할 때 참고합니다.

- GKE 클러스터
- Terraform 리소스
- Kubernetes 배포
- Vault 초기 구성
- TLS 설정

GKE 사용에 따른 클라우드 비용이 발생할 수 있습니다. 전체 도구 체인보다 Vault와 Kubernetes를 연결하는 예제로 사용합니다.

### 2.4 `Artemmkin/infrastructure-as-code-tutorial`

링크: [github.com/Artemmkin/infrastructure-as-code-tutorial](https://github.com/Artemmkin/infrastructure-as-code-tutorial)

다음 순서로 IaC 도구의 역할을 설명합니다.

```text
수동 작업
  → Script
  → Packer
  → Terraform
  → Ansible
  → Vagrant
  → Docker
  → Kubernetes
```

Packer, Terraform, Ansible, Vagrant, Docker, Docker Compose, Kubernetes를 모두 다루지만 Vault는 포함하지 않습니다. README에 2018년에 작성되어 최신 API나 이미지가 동작하지 않을 수 있다고 명시되어 있으므로, 명령어를 그대로 실행하기보다 **도구 간 역할과 학습 순서**를 이해하는 용도로 사용합니다.

### 2.6 `lisenet/kubernetes-homelab`

링크: [github.com/lisenet/kubernetes-homelab](https://github.com/lisenet/kubernetes-homelab)

Linux 기반 Homelab에서 kubeadm, Ansible, Docker, Helm, Terraform을 조합하는 예제입니다. Vault는 포함되지 않지만 다음을 참고할 수 있습니다.

- Ansible Role 구조
- Kubernetes 클러스터 설치
- Docker 설치 플레이북
- Helm 기반 부가 구성
- Terraform과 Ansible의 역할 분리

## 3. 일반 IaC 학습 기준 추천

특정 하이퍼바이저보다 **도구가 담당하는 계층과 상태 관리 흐름**을 먼저 학습하는 것이 좋습니다.

### 전체 도구 체인

`inno-devops-labs/DevOps-Core-Course`를 1순위 학습 과정으로 사용합니다. Docker로 애플리케이션을 만들고, Terraform·Ansible로 인프라와 설정을 관리한 뒤, Kubernetes·Helm·OpenBao·Argo CD로 운영 범위를 확장합니다.

### Secret 관리 도구 구분

| 구분            | HashiCorp Vault                | OpenBao                        | Ansible Vault                        |
|-----------------|--------------------------------|--------------------------------|--------------------------------------|
| 유형            | 중앙 Secret 관리 서버          | 중앙 Secret 관리 서버          | Ansible 파일·변수 암호화 기능        |
| 주요 대상       | 자격증명·인증·동적 Secret      | 자격증명·암호화·정책           | Playbook 변수·Secret 파일            |
| Kubernetes 연동 | 인증·Secret 주입 구성          | 인증·Secret 주입 구성          | 직접적인 중앙 서버 연동 없음         |
| 운영 형태       | 별도 서버·스토리지·Unseal·백업 | 별도 서버·스토리지·Unseal·백업 | Ansible 실행 환경에서 암호화 키 관리 |

> Ansible Vault는 중앙 Secret 서버가 아니라 민감한 변수와 파일을 암호화하는 Ansible 기능입니다. HashiCorp Vault와 OpenBao는 인증·정책·Secret 저장을 제공하는 별도 서비스이므로 운영 방식이 다릅니다.

### 구성 요소별 보강

| 학습 영역                                       | 추천 저장소                       | 보완할 내용                                      |
|-------------------------------------------------|-----------------------------------|--------------------------------------------------|
| Terraform·Ansible·Docker·Kubernetes 기본 구조   | `m-aboud/infra-automation-lab`    | 작은 디렉터리와 CI 검증 구조                     |
| Vault와 Kubernetes 연동                         | `sethvargo/vault-on-gke`          | Terraform·TLS·Vault 초기 구성                    |
| Homelab·GitOps·운영 자동화                      | `khuedoan/homelab`                | 보완 운영 사례: K3s·Argo CD·Secret·모니터링·백업 |
| Packer·Terraform·Ansible·Docker·Kubernetes 순서 | `infrastructure-as-code-tutorial` | 오래된 튜토리얼이므로 개념 중심 활용             |

### IaC와 인접 운영 영역

```text
IaC 핵심
├── Terraform / OpenTofu  → 인프라 프로비저닝
└── Ansible               → OS·서비스 설정

실행·검증 기반
├── Docker / Compose      → 로컬 컨테이너 실행
└── Kubernetes             → 컨테이너 오케스트레이션

Secret 관리
├── HashiCorp Vault
├── OpenBao
└── Ansible Vault

인접 운영 영역
├── Argo CD / GitOps
├── Prometheus / Grafana
└── Loki
```

Packer와 Vagrant는 핵심 도구라기보다 이미지 생성과 개발 환경 재현을 보완하는 선택 도구입니다.

### 최종 선택

| 목적                       | 1순위                  | 이유                                            |
|----------------------------|------------------------|-------------------------------------------------|
| 일반적인 IaC 전체 흐름     | `DevOps-Core-Course`   | Docker부터 GitOps까지 단계별 구성               |
| 작은 예제로 도구 역할 확인 | `infra-automation-lab` | Terraform·Ansible·Docker·Kubernetes 구조가 단순 |
| HashiCorp Vault 연동       | `vault-on-gke`         | Vault·Terraform·Kubernetes 연결에 집중          |
| 실제 Homelab 운영 패턴     | `khuedoan/homelab`     | GitOps·Secret·모니터링·백업 포함                |

## 4. 학습 목적별 선택

### 전체 IaC 도구 체인 학습

`inno-devops-labs/DevOps-Core-Course`를 중심으로 다음 순서를 따릅니다.

```text
Lab 1~3   → Docker와 CI
Lab 4     → Terraform / OpenTofu
Lab 5~6   → Ansible와 Compose
Lab 7~8   → 로그·메트릭
Lab 9~10  → Kubernetes와 Helm
Lab 11    → OpenBao와 External Secrets
Lab 13~16 → Argo CD·Progressive Delivery·운영
```

학습자는 자신의 Fork에서 Terraform, Ansible, Kubernetes 매니페스트를 작성하므로 도구 간 연결을 확인하기 좋습니다. 다만 OpenBao를 사용하므로 HashiCorp Vault 자체를 학습하려면 별도 자료를 보완합니다.

### 로컬 환경에서 작게 시작

처음부터 클라우드 리소스를 생성하지 않고 Docker Compose로 애플리케이션과 Vault 또는 OpenBao를 실행합니다.

```bash
docker compose config
docker compose up -d
docker compose ps
```

이후 Terraform은 로컬 테스트 리소스 또는 테스트용 클라우드 리소스에 적용하고, Ansible은 생성된 대상을 구성합니다.

### 클라우드 없는 학습 경로

```text
1단계  Docker Compose
       └── 샘플 애플리케이션·Vault/OpenBao 실행

2단계  kind 또는 k3d
       └── Docker 기반 로컬 Kubernetes

3단계  Terraform
       └── 로컬·테스트 Provider의 계획과 상태 확인

4단계  Ansible
       └── 테스트 대상의 OS·서비스 설정

5단계  Kubernetes Secret 연동
       └── Vault/OpenBao·External Secrets 검증

6단계  클라우드 Provider
       └── AWS·GCP·Azure는 마지막에 선택적으로 사용
```

처음부터 클라우드 리소스를 생성하지 않아도 Docker·Ansible·Secret·Kubernetes의 연결 흐름을 검증할 수 있습니다.

### HashiCorp Vault 학습

`sethvargo/vault-on-gke`는 Vault·Terraform·Kubernetes 연동 구조를 참고합니다. 단, GKE를 사용하므로 클라우드 비용이 발생할 수 있습니다. 로컬에서는 단일 노드나 Docker Compose로 다음 흐름을 먼저 검증합니다.

```text
Vault / OpenBao
      │
      v
Kubernetes authentication
      │
      v
External Secrets 또는 Vault Agent
      │
      v
Application Pod
```

Vault dev mode는 학습용이며 운영용으로 사용하지 않습니다. 운영 전환 시 스토리지, 백업, Unseal, HA, Audit, Upgrade를 별도로 설계합니다.

## 5. 권장 통합 실습 구조

검색한 저장소를 그대로 합치기보다 다음과 같이 실행 백엔드와 도구별 책임을 분리한 자체 학습 저장소를 구성하는 편이 좋습니다.

```text
iac-learning-lab/
├── docker/
│   └── compose/
│       ├── app/
│       ├── vault/
│       └── monitoring/
├── terraform/
│   ├── local/
│   └── cloud/                  # 선택 사항
├── ansible/
│   ├── inventory/
│   ├── roles/
│   │   ├── common/
│   │   ├── container_runtime/
│   │   └── kubernetes/
│   └── site.yml
├── vault/
│   ├── policies/
│   └── auth/
├── kubernetes/
│   ├── namespaces/
│   ├── applications/
│   └── external-secrets/
├── .github/
│   └── workflows/
└── Makefile
```

### 도구별 책임

| 계층                    | 도구               | 관리 대상                            |
|-------------------------|--------------------|--------------------------------------|
| 애플리케이션 이미지     | Docker             | Dockerfile·이미지·Compose            |
| 인프라 프로비저닝       | Terraform          | VM·네트워크·스토리지·클라우드 리소스 |
| OS·서비스 설정          | Ansible            | 패키지·사용자·서비스·방화벽          |
| Secret 관리             | Vault 또는 OpenBao | 자격증명·정책·동적 Secret            |
| 컨테이너 오케스트레이션 | Kubernetes         | Pod·Service·Deployment·Secret        |
| 선언 상태 배포          | Argo CD            | Kubernetes 매니페스트와 Helm         |

### 단계별 구현

| 단계 | 구현 내용                                               | 검증                                        |
|------|---------------------------------------------------------|---------------------------------------------|
| 1    | Docker Compose로 샘플 애플리케이션과 Vault/OpenBao 실행 | `docker compose config`                     |
| 2    | Terraform Provider로 로컬 또는 테스트 인프라 계획 생성  | `terraform validate`, `terraform plan`      |
| 3    | Ansible로 생성된 호스트의 OS와 서비스를 구성            | `ansible --syntax-check`, `ansible --check` |
| 4    | Kubernetes 클러스터에 샘플 애플리케이션 배포            | `kubectl get nodes`, `kubectl get pods -A`  |
| 5    | Vault/OpenBao와 Kubernetes 인증 연동                    | Secret 조회·회전 테스트                     |
| 6    | Argo CD로 GitOps 배포 구성                              | 동기화·롤백 테스트                          |

## 6. 실행 전 검증과 보안

### 저장소 코드 검토

공개 저장소를 실행하기 전에 다음을 확인합니다.

```bash
git log -1 --format=fuller
git branch -a
find . -maxdepth 3 -type f | sort

grep -RInE 'password|token|secret|access_key|private_key' \
  --exclude-dir=.git .
```

자격증명이나 의심스러운 문자열은 실제 환경에 연결하기 전에 제거하거나 플레이스홀더로 교체합니다. 저장소에 토큰을 직접 넣지 말고 Ansible Vault, Vault/OpenBao, AWS Secrets Manager 또는 SSM Parameter Store를 사용합니다.

### Terraform 검증

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
terraform plan
```

`terraform apply`와 `terraform destroy`는 실제 VM·클라우드 리소스를 변경하거나 삭제할 수 있으므로 대상과 계획을 확인한 뒤 실행합니다.

### Ansible 검증

```bash
ansible-inventory -i inventory/hosts.ini --graph
ansible-playbook -i inventory/hosts.ini site.yml --syntax-check
ansible-playbook -i inventory/hosts.ini site.yml --check --diff
```

원격 대상은 SSH 또는 대상 플랫폼에 맞는 연결 방식을 확인합니다.

### Docker 검증

```bash
docker compose config

docker compose ps
docker image ls
```

Docker Compose를 중지할 때 `docker compose down -v`는 볼륨까지 삭제할 수 있으므로 데이터가 필요한 실습에서는 실행하지 않습니다.

### Kubernetes 검증

```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get --raw='/readyz?verbose'
```

Kubernetes 노드의 컨테이너 런타임과 운영체제를 확인합니다.

```bash
kubectl get nodes \
  -o custom-columns='NAME:.metadata.name,OS:.status.nodeInfo.operatingSystem,RUNTIME:.status.nodeInfo.containerRuntimeVersion'
```

### 도구별 통과 기준

| 도구           | 기본 검증                                                      | 통과 기준                 |
|----------------|----------------------------------------------------------------|---------------------------|
| Docker Compose | `docker compose config`                                        | 구성 파일 오류 없음       |
| Terraform      | `terraform fmt -check`, `terraform validate`, `terraform plan` | 문법·Provider·계획 정상   |
| Ansible        | `ansible-playbook --syntax-check`, `--check`                   | 문법 정상·변경 예상 확인  |
| Vault/OpenBao  | 정책·인증·Secret 조회 테스트                                   | 허용된 경로만 접근        |
| Kubernetes     | `kubectl diff`, `kubectl get pods -A`                          | 매니페스트 정상·Pod Ready |
| GitOps         | Argo CD 동기화·롤백                                            | 원하는 Revision으로 복원  |

### 비용과 자격증명

다음 저장소는 클라우드 리소스를 생성할 수 있으므로 로컬 Docker 실습과 구분합니다.

| 저장소                                      | 비용 위험                       |
|---------------------------------------------|---------------------------------|
| `sethvargo/vault-on-gke`                    | GKE·디스크·로드밸런서 비용 가능 |
| `m-aboud/infra-automation-lab`              | AWS VPC 리소스 생성 가능        |
| `Artemmkin/infrastructure-as-code-tutorial` | GCP 리소스 사용 전제            |
| `khuedoan/homelab`                          | 자체 하드웨어·스토리지 필요     |

실습 전에는 AWS·GCP 자격증명을 환경 변수, IAM Role 또는 SSO로 제공하고 저장소 파일에 저장하지 않습니다. 클라우드 실습 종료 후 리소스와 상태를 확인합니다.

## 7. 롤백과 운영 주의사항

### 롤백 계획

| 변경 대상             | 롤백 방법                                             |
|-----------------------|-------------------------------------------------------|
| Packer 이미지         | 이전 이미지 버전 또는 이전 이미지 파일 사용           |
| Terraform 리소스 구성 | 이전 Git Revision으로 복원 후 `terraform plan` 재확인 |
| Ansible 설정          | 이전 Playbook Revision 재적용                         |
| Kubernetes 배포       | 이전 Helm Release 또는 Argo CD Revision 복원          |
| Vault 정책            | 이전 정책 버전 복원 후 접근 테스트                    |

테스트 환경 스냅샷은 백업을 대체하지 않습니다. 특히 애플리케이션 데이터, Vault 데이터, Terraform State는 별도 백업 정책을 둡니다.

### 저장소 사용 원칙

- Provider와 모듈 버전을 고정합니다.
- `terraform.tfstate`, `.tfvars`, SSH 키, Vault Token을 Git에 커밋하지 않습니다.
- `latest` 이미지 대신 검증된 태그를 사용합니다.
- 원격 Terraform Backend를 사용할 때 State 암호화와 State Lock을 설정합니다.
- Ansible 실행 전 `--syntax-check`와 `--check`를 사용합니다.
- Kubernetes 매니페스트는 `kubectl diff` 또는 `kubeconform`으로 확인합니다.
- 공개 저장소의 설치 스크립트는 내용을 읽은 뒤 실행합니다.
- 초기 검증은 Snapshot 또는 별도 테스트 VM에서 수행합니다.

### 최종 추천

일반적인 IaC 도구 학습에는 다음 순서를 권장합니다.

```text
1. DevOps-Core-Course
   └── Docker + Terraform + Ansible + Kubernetes + OpenBao

2. infra-automation-lab
   └── 작은 Terraform·Ansible·Docker·Kubernetes 실행 구조

3. vault-on-gke
   └── HashiCorp Vault와 Kubernetes 연동 참고

4. khuedoan/homelab
   └── GitOps·Secret·모니터링·백업 운영 구조 참고
```

먼저 Docker 기반 로컬 실습으로 도구 간 흐름을 익힌 뒤 Terraform·Ansible·Kubernetes를 연결합니다. 이후 필요에 따라 Proxmox, libvirt, AWS, GCP, Azure 등 원하는 실행 백엔드를 추가합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

### GitHub 저장소

아래 별점은 GitHub Stars가 아니라 공식성·학습 직접성·재현성을 기준으로 한 편집 평가입니다.

- DevOps Core Course: [github.com/inno-devops-labs/DevOps-Core-Course](https://github.com/inno-devops-labs/DevOps-Core-Course) — ★★★☆☆
- Khue's Homelab: [github.com/khuedoan/homelab](https://github.com/khuedoan/homelab) — ★★★☆☆
- Infrastructure Automation Lab: [github.com/m-aboud/infra-automation-lab](https://github.com/m-aboud/infra-automation-lab) — ★★☆☆☆
- Vault on GKE: [github.com/sethvargo/vault-on-gke](https://github.com/sethvargo/vault-on-gke) — ★★★☆☆
- Infrastructure as Code Tutorial: [github.com/Artemmkin/infrastructure-as-code-tutorial](https://github.com/Artemmkin/infrastructure-as-code-tutorial) — ★★☆☆☆
- Kubernetes Homelab: [github.com/lisenet/kubernetes-homelab](https://github.com/lisenet/kubernetes-homelab) — ★★★☆☆

### 공식 문서와 내부 문서

- Docker Documentation: [docs.docker.com](https://docs.docker.com/) — ★★★☆☆
- Terraform Documentation: [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/) — ★★★☆☆
- Ansible Documentation: [docs.ansible.com](https://docs.ansible.com/ansible/latest/) — ★★★☆☆
- HashiCorp Vault Documentation: [developer.hashicorp.com/vault](https://developer.hashicorp.com/vault/docs) — ★★★☆☆
- GitHub REST API: [docs.github.com/en/rest/repos/repos](https://docs.github.com/en/rest/repos/repos) — ★★★☆☆
- OpenBao Documentation: [openbao.org/docs](https://openbao.org/docs/) — ★★★☆☆
- [Terraform 가이드](./terraform.md)
- [Ansible 기초 가이드](./ansible_basic_guide.md)
- [Vault 설치 가이드](../../04_security/hardening/vault_install.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-17

**마지막 업데이트**: 2026-09-17

© 2026 siasia86. Licensed under CC BY 4.0.
