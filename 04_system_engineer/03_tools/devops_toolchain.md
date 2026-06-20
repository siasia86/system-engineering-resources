# DevOps 툴체인 전체 그림

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 전체 흐름](#2-전체-흐름) / [3. 카테고리별 도구](#3-카테고리별-도구) |
| [4. IaC 도구](#4-iac-도구) / [5. 컨테이너 도구](#5-컨테이너-도구) / [6. CI/CD](#6-cicd) |
| [7. 모니터링·관측성](#7-모니터링관측성) / [8. 규모별 스택 선택](#8-규모별-스택-선택) |

---

## 1. 개요

DevOps 툴체인은 소프트웨어 개발부터 운영까지 전 과정을 자동화하는 도구들의 집합입니다.
IaC(Infrastructure as Code)는 그 중 인프라를 코드로 정의·관리하는 부분을 담당합니다.

### IaC vs DevOps 툴체인

| 개념              | 범위                          | 포함 도구                          |
|-------------------|-------------------------------|------------------------------------|
| IaC               | 인프라를 코드로 정의·관리     | Terraform, Ansible, K8s YAML, Helm |
| CI/CD             | 빌드·테스트·배포 자동화       | Jenkins, GitHub Actions, ArgoCD    |
| Container         | 앱 패키징·실행·오케스트레이션 | Docker, Kubernetes                 |
| Observability     | 메트릭·로그·알림              | Prometheus, Grafana, Zabbix        |
| **DevOps 툴체인** | **위 전체를 아우르는 개념**   | **전부**                           |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 전체 흐름

```
개발자                 CI/CD                  인프라                  운영
─────                 ─────                  ────                   ────  
코드 작성                                                                 
    │                                                                     
    v                                                                     
Git push                                                                  
    │                                                                     
    v                                                                     
GitHub Actions  ──>  테스트/빌드                                          
Jenkins              │                                                    
                     v                                                    
                  Docker 이미지 빌드                                      
                     │                                                    
                     v                                                    
                  이미지 레지스트리 push                                  
                  (ECR / Docker Hub)                                      
                     │                                                    
          ┌──────────┴──────────┐                                         
          │                     │                                         
          v                     v                                         
    Terraform              Ansible                                        
    (인프라 생성)          (서버 설정)                                    
    VPC/EC2/RDS            패키지 설치                                    
          │                     │                                         
          └──────────┬──────────┘                                         
                     │                                                    
                     v                                                    
               Kubernetes 클러스터                                        
               Helm으로 앱 배포                                           
               ArgoCD (GitOps)                                            
                     │                                                    
                     v                                                    
            Prometheus + Grafana                                          
            메트릭 수집·시각화                                            
            Zabbix 알림                                                   
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 카테고리별 도구

| 카테고리          | 도구                     | 최신 버전 | 공식 설명                                           |
|-------------------|--------------------------|-----------|-----------------------------------------------------|
| 인프라 프로비저닝 | Terraform                | v1.15.4   | Infrastructure as code tool                         |
| 서버 구성 자동화  | Ansible                  | v2.21.0   | Open source IT automation engine                    |
| 컨테이너 런타임   | Docker Engine            | v29.5.2   | Build, share, and run containerized applications    |
| 컨테이너 구성     | Docker Compose           | v5.1.4    | Multi-container application definition              |
| 오케스트레이션    | Kubernetes               | v1.36.1   | Automated container deployment, scaling, management |
| K8s 패키지 관리   | Helm                     | v4.2.0    | The package manager for Kubernetes                  |
| GitOps CD         | ArgoCD                   | v3.4.2    | Declarative GitOps CD tool for Kubernetes           |
| CI/CD             | GitHub Actions / Jenkins | —         | Automate any workflow / Build great things          |
| 메트릭 수집       | Prometheus               | v3.11.3   | Open source monitoring and alerting toolkit         |
| 시각화            | Grafana                  | v13.0.1   | Full-stack observability platform                   |
| 인프라 모니터링   | Zabbix                   | 7.4       | Enterprise-class monitoring solution                |

[⬆ 목차로 돌아가기](#목차)

---

## 4. IaC 도구

### Terraform — 인프라 프로비저닝

클라우드/온프레미스 자원(서버, 네트워크, DB 등)을 코드로 생성·변경·삭제합니다.

```hcl
# 예시: AWS EC2 인스턴스 생성
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
}
```

- 선언적(declarative): 원하는 최종 상태만 기술
- Provider: AWS, GCP, Azure, VMware 등 1,000개 이상
- State 파일로 현재 인프라 상태 추적
- 공식: [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform)

---

### Ansible — 서버 구성 자동화

에이전트 없이 SSH로 서버에 접속해 패키지 설치, 설정 파일 배포, 서비스 관리를 자동화합니다.

```yaml
# 예시: nginx 설치
- name: Install nginx
  ansible.builtin.package:
    name: nginx
    state: present
```

- Agentless: 대상 서버에 별도 소프트웨어 불필요
- 멱등성(idempotent): 여러 번 실행해도 결과 동일
- Playbook: YAML로 작업 순서 정의
- 공식: [ansible.com](https://www.ansible.com)

---

### Kubernetes YAML / Helm — 앱 배포 상태 정의

```yaml
# 예시: Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web
        image: nginx:1.27
```

Helm은 위 YAML을 템플릿화해 재사용 가능한 Chart로 패키징합니다.

- 공식 Kubernetes: [kubernetes.io](https://kubernetes.io)
- 공식 Helm: [helm.sh](https://helm.sh)

[⬆ 목차로 돌아가기](#목차)

---

## 5. 컨테이너 도구

### Docker — 컨테이너 빌드·실행

앱과 의존성을 이미지로 패키징해 어디서든 동일하게 실행합니다.

```dockerfile
FROM python:3.12-slim
COPY app.py .
CMD ["python", "app.py"]
```

```bash
docker build -t myapp:1.0 .
docker run -d -p 8080:8080 myapp:1.0
```

- 공식: [docker.com](https://www.docker.com)

---

### Kubernetes — 컨테이너 오케스트레이션

다수의 노드에서 컨테이너를 자동으로 배포·스케일링·복구합니다.

| 기능              | 설명                               |
|-------------------|------------------------------------|
| Self-healing      | 컨테이너 장애 시 자동 재시작       |
| Auto-scaling      | 부하에 따라 Pod 수 자동 조정 (HPA) |
| Rolling update    | 무중단 배포                        |
| Service discovery | 내부 DNS로 서비스 간 통신          |
| Secret 관리       | 민감 정보 암호화 저장              |

- 공식: [kubernetes.io](https://kubernetes.io)

[⬆ 목차로 돌아가기](#목차)

---

## 6. CI/CD

코드 변경 → 자동 테스트 → 빌드 → 배포까지 파이프라인을 자동화합니다.

### GitHub Actions

```yaml
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp .
      - run: docker push myapp
```

- 공식: [github.com/features/actions](https://github.com/features/actions)

### ArgoCD — GitOps

Git 저장소를 단일 진실 공급원(Single Source of Truth)으로 삼아 K8s 클러스터 상태를 자동 동기화합니다.

```
Git repo (YAML) ──> ArgoCD ──> Kubernetes 클러스터
     변경 감지          자동 sync
```

- 공식: [argoproj.github.io/cd](https://argoproj.github.io/cd/)

[⬆ 목차로 돌아가기](#목차)

---

## 7. 모니터링·관측성

### Prometheus + Grafana

```
앱/서버/K8s                    
    │  메트릭 노출 (/metrics)  
    v                          
Prometheus (수집·저장·알림)    
    │                          
    v                          
Grafana (대시보드 시각화)      
    │                          
    v                          
AlertManager (Slack/Email 알림)
```

- Prometheus: 시계열 메트릭 수집, PromQL 쿼리 언어
- Grafana: 다양한 데이터소스 시각화 (Prometheus, Loki, CloudWatch 등)
- 공식 Prometheus: [prometheus.io](https://prometheus.io)
- 공식 Grafana: [grafana.com](https://grafana.com)

### Zabbix

에이전트 기반 인프라 모니터링. 서버·네트워크 장비·DB 등 전통적 인프라에 강합니다.

- 공식: [zabbix.com](https://www.zabbix.com)

[⬆ 목차로 돌아가기](#목차)

---

## 8. 규모별 스택 선택

| 규모                       | 권장 스택                                                    |
|----------------------------|--------------------------------------------------------------|
| 소규모 (서버 ~50대)        | Ansible + Docker Compose + Zabbix + Grafana                  |
| 중규모 (서버 ~500대)       | Terraform + Ansible + Kubernetes + Helm + Prometheus/Grafana |
| 대규모 (클라우드 네이티브) | 중규모 전체 + ArgoCD + GitHub Actions + Loki + Istio         |

### 학습 순서 권장

```
1. Linux 기초
2. Git
3. Docker
4. Ansible
5. Terraform
6. Kubernetes + Helm
7. CI/CD (GitHub Actions / Jenkins)
8. Prometheus + Grafana
9. ArgoCD (GitOps)
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Terraform: [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform) — ★★★☆☆
- Ansible: [ansible.com](https://www.ansible.com) — ★★★☆☆
- Docker: [docs.docker.com](https://docs.docker.com) — ★★★☆☆
- Kubernetes: [kubernetes.io/docs](https://kubernetes.io/docs/home/) — ★★★☆☆
- Helm: [helm.sh/docs](https://helm.sh/docs/) — ★★★☆☆
- ArgoCD: [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/) — ★★★☆☆
- Prometheus: [prometheus.io/docs](https://prometheus.io/docs/introduction/overview/) — ★★★☆☆
- Grafana: [grafana.com/docs](https://grafana.com/docs/) — ★★★☆☆

---

**작성일**: 2026-05-26

**마지막 업데이트**: 2026-05-26

© 2026 siasia86. Licensed under CC BY 4.0.
