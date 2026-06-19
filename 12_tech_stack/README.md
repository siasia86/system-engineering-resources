# 기술 스택 가이드

CI/CD, 워크플로우 자동화, 인프라 관리 도구 실무 가이드 모음입니다.

## 문서 목록

| 문서                                                      | 설명                                           |
|-----------------------------------------------------------|------------------------------------------------|
| [Apache Airflow](airflow.md)                              | DAG 기반 워크플로우 자동화, Operator, 스케줄링 |
| [ArgoCD](argocd.md)                                       | GitOps CD, Application 동기화, Sync Policy     |
| [AWS Network Firewall](aws_network_firewall.md)           | 생성/삭제 가이드, 로깅, 비용                   |
| [AWS Step Functions](aws_step_functions.md)               | 상태 머신, ASL, 에러 처리                      |
| [Container Runtime](container_runtime.md)                 | 컨테이너 런타임 비교                           |
| [Docker](docker.md)                                       | 컨테이너 아키텍처, Dockerfile, 네트워크, 볼륨  |
| [Docker Compose Cheatsheet](docker_compose_cheatsheet.md) | Compose 명령어 레퍼런스                        |
| [Git 실무 가이드](git_guide.md)                           | Stage/Commit, rebase vs merge, stash           |
| [GitHub Actions](github_actions.md)                       | 워크플로우 자동화, 트리거, Runner              |
| [Grafana + GitLab Heatmap](grafana_gitlab_heatmap.md)     | Grafana 히트맵 연동                            |
| [Gstack](gstack.md)                                       | Claude 기반 AI 코딩 에이전트 CLI               |
| [Harness Engineering](harness_engineering.md)             | AI 에이전트 환경 설계 (하네스 엔지니어링)      |
| [Harness Inc.](harness_inc.md)                            | CI/CD 플랫폼 Harness 사용법                    |
| [Helm](helm.md)                                           | K8s 패키지 매니저, Chart, Values               |
| [Jenkins Pipeline](jenkins_pipeline.md)                   | Declarative/Scripted Pipeline                  |
| [k3s](k3s.md)                                             | 경량 Kubernetes 배포                           |
| [Apache Kafka](kafka.md)                                  | 분산 메시지 스트리밍, Topic, Consumer Group    |
| [Kubernetes 기본](kubernetes_basic.md)                    | Pod/Deployment/Service, kubectl                |
| [Prometheus + Grafana](prometheus_grafana.md)             | 메트릭 수집, PromQL, AlertManager              |
| [Terraform](terraform.md)                                 | IaC, HCL 문법, State 관리, Module              |
| [Vagrant](vagrant.md)                                     | VM 프로비저닝, Vagrantfile, Provider           |

## 데이터 파이프라인 (01_data_pipeline/)

| 문서                                                            | 설명                                     |
|-----------------------------------------------------------------|------------------------------------------|
| [게임 로그 파이프라인](01_data_pipeline/game_log_pipeline.md)   | Kafka-Flink/Spark-Parquet-Snowflake 패턴 |
| [로그 통합 100GB/일](01_data_pipeline/log_aggregation_100gb.md) | Filebeat-Logstash-OpenSearch-Athena      |
| [로그 통합 100TB/일](01_data_pipeline/log_aggregation_100tb.md) | MSK-Glue-Snowflake 대규모 아키텍처       |

## 참고 자료

- Ansible Documentation: [docs.ansible.com](https://docs.ansible.com/) — ★★★☆☆
- Apache Airflow Documentation: [airflow.apache.org](https://airflow.apache.org/docs/) — ★★★☆☆
- Jenkins Documentation: [jenkins.io/doc](https://www.jenkins.io/doc/) — ★★★☆☆
- Pro Git Book: [git-scm.com/book](https://git-scm.com/book/ko/v2) — ★★★☆☆

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

**마지막 업데이트**: 2026-06-19

© 2026 siasia86. Licensed under CC BY 4.0.
