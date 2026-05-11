# 기술 스택 가이드

CI/CD, 워크플로우 자동화, 인프라 관리 도구 실무 가이드 모음.

## 목차

| 섹션 |
|------|
| [문서 목록](#문서-목록) |

---

## 문서 목록

| 문서 | 설명 |
|------|------|
| [Apache Airflow](airflow.md) | DAG 기반 워크플로우 자동화, Operator, 스케줄링, XCom |
| [Ansible 기초 가이드](ansible_basic_guide.md) | Inventory, Playbook, Role, 변수 우선순위, 동적 Inventory |
| [Ansible Vault](ansible_vault.md) | AES-256 암호화, vault-id, CI/CD 연동, 키 관리 |
| [AWS Step Functions](aws_step_functions.md) | 상태 머신, ASL, 에러 처리, CDK/Terraform 연동 |
| [Git 실무 가이드](git_guide.md) | Stage/Commit, rebase vs merge, stash, safe.directory |
| [Jenkins Pipeline](jenkins_pipeline.md) | Declarative/Scripted Pipeline, 공유 라이브러리, Docker 빌드 |
| [ArgoCD](argocd.md) | GitOps CD, Application 동기화, Sync Policy, RBAC |
| [GitHub Actions](github_actions.md) | 워크플로우 자동화, 트리거, Runner, 재사용 가능 워크플로우 |
| [Helm](helm.md) | Kubernetes 패키지 매니저, Chart, Values, 템플릿 |
| [Apache Kafka](kafka.md) | 분산 메시지 스트리밍, Topic, Consumer Group, 파티셔닝 |
| [Kubernetes 기본](kubernetes_basic.md) | Pod/Deployment/Service, kubectl, ConfigMap, 스케줄링 |
| [Prometheus & Grafana](prometheus_grafana.md) | 메트릭 수집, PromQL, AlertManager, 대시보드 |
| [Terraform](terraform.md) | IaC, HCL 문법, State 관리, Module, 워크스페이스 |

---

## 참고 자료

- Ansible Documentation: [docs.ansible.com](https://docs.ansible.com/) — ★★★☆☆
- Apache Airflow Documentation: [airflow.apache.org](https://airflow.apache.org/docs/) — ★★★☆☆
- Jenkins Documentation: [jenkins.io/doc](https://www.jenkins.io/doc/) — ★★★☆☆
- AWS Step Functions Documentation: [docs.aws.amazon.com](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) — ★★★☆☆
- Pro Git Book: [git-scm.com/book](https://git-scm.com/book/ko/v2) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-01

**마지막 업데이트**: 2026-05-11

© 2026 siasia86. Licensed under CC BY 4.0.
