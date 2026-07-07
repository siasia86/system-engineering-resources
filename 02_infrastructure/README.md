# Infrastructure

인프라 구축과 운영 도구. 컨테이너, CI/CD 파이프라인, IaC, 모니터링, 클라우드를 다룹니다.

## 구조

| 디렉토리                           | 설명                                                       | 문서 수 |
|------------------------------------|------------------------------------------------------------|---------|
| [containers/](./containers/)       | 컨테이너 — Docker, Compose, 런타임, Kubernetes, Helm       | 10      |
| [cicd/](./cicd/)                   | CI/CD — ArgoCD, Ansible, Jenkins, GitHub Actions, Airflow  | 13      |
| [iac/](./iac/)                     | Infrastructure as Code — Ansible, Terraform, Playbook 운영 | 11      |
| [monitoring/](./monitoring/)       | 모니터링 — Prometheus, Grafana, Zabbix, 시스템 메트릭      | 7       |
| [cloud_aws/](./cloud_aws/)         | AWS 클라우드 — VPC, S3, Network Firewall, 백업             | 6       |
| [data_pipeline/](./data_pipeline/) | 데이터 파이프라인 — Kafka, 로그 수집(100GB~100TB)          | 4       |
| [web_server/](./web_server/)       | 웹 서버 — Nginx, Apache, HAProxy 설치 및 설정              | 4       |

## 주요 문서

- [container_architecture.md](./containers/container_architecture.md) — namespace/cgroup 기반 컨테이너 구조
- [ansible_basic_guide.md](./iac/ansible_basic_guide.md) — Ansible 기초부터 팀 운영까지
- [prometheus_grafana.md](./monitoring/prometheus_grafana.md) — Prometheus + Grafana 아키텍처
- [kafka.md](./data_pipeline/kafka.md) — Kafka 클러스터 구성과 운영
- [argocd.md](./cicd/argocd.md) — GitOps 기반 배포

## 추천 학습 순서

`containers (Docker)` → `iac (Ansible)` → `cicd (ArgoCD)` → `monitoring` → `cloud_aws`

## 전제 조건

[01_fundamentals/linux/](../01_fundamentals/linux/) 기본 명령어, 네트워크 기초.

## 관련 섹션

- 기초 Linux 지식: [01_fundamentals/linux/](../01_fundamentals/linux/)
- 운영 신뢰성: [03_engineering/reliability/](../03_engineering/reliability/)
- 클라우드 보안: [04_security/cloud/](../04_security/cloud/)

[⬆ 루트 README로 돌아가기](../README.md)

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
