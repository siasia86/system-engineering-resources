# 시스템 엔지니어링 학습 자료 모음

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Linux, 네트워크, 보안, 데이터베이스, 프로그래밍 등 시스템 엔지니어링 관련 학습 자료 저장소.

## 목차

| 섹션 |
|------|
| [1. 설치](#1-설치) / [2. 기본 Linux](#2-기본-linux) / [3. 고급 Linux](#3-고급-linux) |
| [4. 시스템 엔지니어링](#4-시스템-엔지니어링) / [5. 컴퓨터 과학](#5-컴퓨터-과학) / [6. 보안](#6-보안) |
| [7. 오픈소스](#7-오픈소스) / [8. Linux 디버깅](#8-linux-디버깅) / [9. 데이터베이스](#9-데이터베이스) |
| [10. NoSQL](#10-nosql) / [11. Python](#11-python) / [12. 기술 스택](#12-기술-스택) |
| [추천 학습 순서](#추천-학습-순서) / [기타 문서](#기타-문서) / [문서 트리](#문서-트리) |

---

## 1. 설치

설치 및 환경 구성 가이드.

| 문서 | 설명 |
|------|------|
| [Ansible 설치 및 팀 운영](01_install/ansible_install_and_team_operation.md) | Ansible 설치, AWX, 팀 운영 가이드 |
| [MySQL 설치](01_install/mysql_install.md) | Ubuntu/RHEL, 초기 설정, 보안 |
| [PostgreSQL 설치](01_install/postgresql_install.md) | Ubuntu/RHEL, pg_hba.conf, 보안 |
| [Docker + Compose](01_install/docker_install_and_compose.md) | 설치, Compose 운영, 실무 팁 |
| [Kubernetes](01_install/kubernetes_install.md) | k3s, kubeadm, kubectl 기본 사용법 |
| [Nginx](01_install/nginx_install.md) | 설치, 가상 호스트, 리버스 프록시, SSL |
| [Apache](01_install/apache_install.md) | 설치, MPM(prefork/worker/event), SSL |
| [Redis](01_install/redis_install.md) | 설치, 보안 설정, 자료형, 실무 팁 |
| [Prometheus + Grafana](01_install/prometheus_grafana_install.md) | 설치, Node Exporter, 알림, Compose |
| [Elasticsearch](01_install/elasticsearch_install.md) | 설치, ELK 스택, ILM, Compose |
| [HAProxy](01_install/haproxy_install.md) | L4/L7 LB, SSL 터미네이션, 통계 |
| [Vault](01_install/vault_install.md) | 설치, KV/DB 엔진, AppRole, Auto Unseal |
| [MongoDB](01_install/mongodb_install.md) | 설치, 보안 설정, CRUD, 백업 |
| [Jenkins](01_install/jenkins_install.md) | 설치, Pipeline, Docker Compose |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 기본 Linux

자주 사용하는 Linux 명령어 및 스크립팅.

| 문서 | 설명 |
|------|------|
| [Bash 수학 연산](02_basic_linux/bash_math.md) | 산술 연산, bc, awk |
| [Bash trap 가이드](02_basic_linux/bash_trap_complete_guide.md) | 시그널 처리, 정리 작업 |
| [리다이렉션](02_basic_linux/bash_file_redirection.md) | stdin/stdout/stderr, 파이프 |
| [Root 패스워드 복구](02_basic_linux/root_password_recovery.md) | 복구 모드, single user mode |
| [Shell 인터랙티브 모드](02_basic_linux/shell_interactive_mode.md) | interactive/non-interactive 차이 |
| [Vim 사용법](02_basic_linux/vim.md) | 기본 명령어, 모드, 설정 |
| [vim-airline](02_basic_linux/vim_airline.md) | 상태바 플러그인 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고급 Linux

고급 Linux 시스템 관리 및 성능 분석.

| 문서 | 설명 |
|------|------|
| [bpftrace](03_advanced_linux/bpftrace.md) | eBPF 기반 동적 추적, 커널 분석 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 시스템 엔지니어링

SE/SRE/DBA 로드맵, 실무 운영, 도구, AI 활용, 법률.

### 로드맵

| 문서 | 설명 |
|------|------|
| [SE 로드맵](04_system_engineer/01_roadmap/se_roadmap.md) | 시스템 엔지니어 커리어 경로 |
| [SRE 로드맵](04_system_engineer/01_roadmap/sre_roadmap.md) | Site Reliability Engineer 경로 |
| [SE 로드맵 - 언어](04_system_engineer/01_roadmap/se_complete_roadmap_programming_languages.md) | 언어별 학습 가이드 |
| [DBA 로드맵](04_system_engineer/01_roadmap/dba_roadmap.md) | DBA 역할, 학습 순서, 자격증 |

### 실무 운영

| 문서 | 설명 |
|------|------|
| [게임 인프라 KPI](04_system_engineer/02_operations/game_infra_kpi_presentation.md) | 인프라 운영 핵심 지표 |
| [리소스 모니터링](04_system_engineer/02_operations/resource_utilization_monitoring.md) | CPU/메모리/디스크/네트워크 |
| [백업 도구 비교](04_system_engineer/02_operations/backup_tools_comparison.md) | rsync, BorgBackup 등 |
| [ASN 및 DDoS 대응](04_system_engineer/02_operations/asn_and_cloudflare_ddos.md) | ASN 운영, Cloudflare DDoS |
| [CDN/Proxy/Origin IP](04_system_engineer/02_operations/cdn_proxy_origin_ip.md) | CDN 구조, Origin IP 보호 |
| [S3 Gateway Endpoint](04_system_engineer/02_operations/s3_gateway_endpoint_cross_account.md) | 크로스 계정 S3 접근 |
| [VPC Peering](04_system_engineer/02_operations/vpc_peering_inter_region_guide.md) | Inter-Region VPC Peering |
| [인프라 Monorepo](04_system_engineer/02_operations/infra_monorepo_and_boilerplate.md) | 모노레포 구조 |

### 도구

| 문서 | 설명 |
|------|------|
| [언어 비교](04_system_engineer/03_tools/c_cpp_csharp_go_python_bash_comparison.md) | C/C++/C#/Go/Python/Bash |
| [LSP 가이드](04_system_engineer/03_tools/lsp_guide.md) | Language Server Protocol |
| [ADR 가이드](04_system_engineer/03_tools/adr_guide.md) | Architecture Decision Record |

### AI 활용

| 문서 | 설명 |
|------|------|
| [Kiro CLI 레퍼런스](04_system_engineer/04_ai/kiro_cli_command_reference.md) | Kiro CLI 명령어 전체 정리 |
| [Kiro 모델 가이드](04_system_engineer/04_ai/kiro_model_guide.md) | 모델 선택 기준 |
| [AI 개발 요청 템플릿](04_system_engineer/04_ai/ai_development_request_template.md) | AI 활용 개발 요청 양식 |
| [AI Markdown 패턴](04_system_engineer/04_ai/ai_markdown_design_patterns.md) | AI 에이전트용 문서 패턴 |

### 법률 & 라이선스

| 문서 | 설명 |
|------|------|
| [DRM 가이드](04_system_engineer/05_legal/drm_guide.md) | DRM 개념, Tivoization, DMCA |
| [업무 외 저작물 귀속](04_system_engineer/05_legal/ip_ownership_guide.md) | 저작권법 제9조, 귀속 조항 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 컴퓨터 과학

네트워크 프로토콜, CPU 아키텍처, 자료구조.

| 문서 | 설명 |
|------|------|
| [IPv4 주소 체계](05_computer_science/ipv4_addressing_guide.md) | 서브넷, CIDR, AWS VPC |
| [IPv6 주소 체계](05_computer_science/ipv6_addressing_guide.md) | 주소 구조, 표기법, SLAAC |
| [TCP 상태 전이](05_computer_science/TCP_state.md) | 3/4-Way Handshake, TIME_WAIT |
| [패킷 분석](05_computer_science/packet_analysis.md) | IP/TCP/UDP 헤더, PROXY Protocol |
| [네트워크 헤더](05_computer_science/network_headers.md) | Ethernet, ARP, DNS, TLS, QUIC |
| [HTTP 메서드](05_computer_science/http_methods.md) | GET/POST/PUT/DELETE/PATCH |
| [tcpdump 예제](05_computer_science/tcpdump_examples.md) | 패킷 캡처 실전 예제 |
| [Switch VLAN Mode](05_computer_science/switch_vlan_mode.md) | Access/Trunk/Dynamic, VLAN Hopping |
| [CPU CISC vs RISC](05_computer_science/cpu_cisc_risc.md) | 명령어 집합 아키텍처 비교 |
| [자료구조](05_computer_science/01_data_structures/) | Array, Stack, Queue, Tree, Graph 등 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안

시스템 보안, 방화벽, 인증, 취약점 관리.

| 문서                                                                    | 설명                                              |
|-------------------------------------------------------------------------|---------------------------------------------------|
| [DDoS 방어 아키텍처](06_security/ddos_defense_architecture.md)         | XDP/nftables/CrowdSec/HAProxy 계층별 방어 전략   |
| [Linux 서버 보안 강화](06_security/linux_hardening.md)                 | sysctl, auditd, 불필요 서비스 제거, umask         |
| [방화벽 - iptables/nftables](06_security/firewall_iptables_nftables.md) | 체인/규칙, nftables 문법, 실전 룰셋               |
| [SSH 보안](06_security/ssh_security.md)                                 | 키 기반 인증, sshd_config 강화, fail2ban          |
| [TLS/SSL 가이드](06_security/tls_ssl_guide.md)                         | 인증서 구조, Let's Encrypt, openssl, mTLS         |
| [시크릿 관리](06_security/secret_management.md)                        | Ansible Vault, AWS Secrets Manager, Vault 비교    |
| [AWS 보안](06_security/aws_security.md)                                 | IAM, Security Group, WAF, GuardDuty, CloudTrail   |
| [취약점 스캔](06_security/vulnerability_scanning.md)                   | nmap, trivy, lynis, CVE 대응 흐름                 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 오픈소스

컨테이너, 자동화, 오픈소스 도구 활용.

| 문서 | 설명 |
|------|------|
| [Docker & Docker Compose](12_tech_stack/docker_compose_cheatsheet.md) | 명령어 치트시트 |
| [n8n Docker Compose](07_opensource/n8n_docker_cheatsheet.md) | n8n + MySQL 구성 |
| [컨테이너 아키텍처](07_opensource/container_architecture.md) | Namespace, Cgroup, OCI |
| [Percona XtraBackup](07_opensource/percona_xtrabackup_guide.md) | MySQL 온라인 백업 |
| [Ansible vs Jenkins](07_opensource/ansible_vs_jenkins.md) | 자동화 도구 비교 |

[⬆ 목차로 돌아가기](#목차)

---

## 8. Linux 디버깅

Linux 시스템 디버깅 및 성능 분석 도구.

| 문서 | 설명 |
|------|------|
| [strace](08_debugging_linux/strace.md) | 시스템 콜 추적 |
| [ltrace](08_debugging_linux/ltrace.md) | 라이브러리 함수 추적 |
| [gdb](08_debugging_linux/gdb.md) | GNU 디버거 |
| [perf](08_debugging_linux/perf.md) | 성능 분석 |
| [valgrind](08_debugging_linux/valgrind.md) | 메모리 디버깅 |
| [lsof](08_debugging_linux/lsof.md) | 열린 파일 확인 |
| [iotop](08_debugging_linux/iotop.md) | I/O 모니터링 |
| [tcpdump](08_debugging_linux/tcpdump.md) | 네트워크 패킷 캡처 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 데이터베이스

RDBMS 설계, 쿼리 최적화, 운영.

| 문서 | 설명 |
|------|------|
| [정규화](09_database/rdbms_normalization.md) | 1NF~BCNF, 반정규화 |
| [JOIN](09_database/rdbms_join.md) | JOIN 종류, 실행 방식 |
| [Index](09_database/rdbms_index.md) | B-Tree, 복합/커버링 인덱스 |
| [EXPLAIN](09_database/rdbms_explain.md) | 실행 계획 분석, 슬로우 쿼리 |
| [Transaction](09_database/rdbms_transaction.md) | ACID, 격리 수준, MVCC |
| [Lock](09_database/rdbms_lock.md) | Row/Gap Lock, 데드락 |
| [View](09_database/rdbms_view.md) | View, Materialized View |
| [Procedure](09_database/rdbms_procedure.md) | 저장 프로시저, 커서 |
| [Replication](09_database/rdbms_replication.md) | binlog, GTID, RDS Read Replica |
| [Partition](09_database/rdbms_partition.md) | Range/List/Hash 파티셔닝 |
| [Schema Migration](09_database/rdbms_schema_migration.md) | pt-osc, gh-ost, 무중단 변경 |

[⬆ 목차로 돌아가기](#목차)

---

## 10. NoSQL

MongoDB, Redis, Elasticsearch.

| 문서 | 설명 |
|------|------|
| [MongoDB](10_nosql/nosql_mongodb.md) | Document DB, Aggregation Pipeline |
| [Redis](10_nosql/nosql_redis.md) | 인메모리, 캐시, 분산 락, 랭킹 |
| [Elasticsearch](10_nosql/nosql_elasticsearch.md) | 전문 검색, 로그 분석, ELK |

[⬆ 목차로 돌아가기](#목차)

---

## 11. Python

Python 프로그래밍 가이드.

| 문서 | 설명 |
|------|------|
| [클래스](11_python/python_class.md) | 클래스 기초 |
| [클래스 구성 요소](11_python/python_class_components.md) | 속성, 메서드, 프로퍼티 |
| [상속](11_python/python_inheritance.md) | 단일/다중 상속, MRO |
| [함수](11_python/python_functions.md) | 정의, 인자, 클로저 |
| [제어문](11_python/python_control_flow.md) | if/for/while/match |
| [예외 처리](11_python/python_exceptions.md) | try/except, 커스텀 예외 |
| [데코레이터](11_python/python_decorators.md) | functools, 클래스 데코레이터 |
| [제너레이터](11_python/python_generators.md) | yield, 이터레이터 |
| [컴프리헨션](11_python/python_comprehensions.md) | list/dict/set/generator |
| [컨텍스트 매니저](11_python/python_context_managers.md) | with, contextlib |
| [파일 입출력](11_python/python_file_io.md) | open, pathlib, shutil |
| [자료구조](11_python/python_data_structures.md) | list, dict, set, tuple |
| [패키지](11_python/python_packages.md) | 모듈, 패키지, pip |
| [가상환경](11_python/python_virtual_env.md) | venv, pip, requirements |
| [로깅](11_python/python_logging.md) | logging 모듈, 핸들러 |
| [정규표현식](11_python/python_regex.md) | re 모듈, 패턴 |
| [문자열](11_python/python_string.md) | 포맷, 메서드, f-string |
| [JSON/YAML](11_python/python_json_yaml.md) | 직렬화/역직렬화 |
| [subprocess](11_python/python_subprocess.md) | 외부 명령 실행 |
| [argparse](11_python/python_argparse.md) | CLI 도구 제작 |
| [os/pathlib](11_python/python_os_pathlib.md) | 파일/디렉토리 조작 |
| [모듈 속성](11_python/python_magic_attributes.md) | `__name__`, `__file__` 등 |
| [print()](11_python/python_print.md) | 출력 포맷, sep/end |

[⬆ 목차로 돌아가기](#목차)

---

## 12. 기술 스택

주요 인프라/DevOps 도구 가이드.

| 문서 | 설명 |
|------|------|
| [Ansible 기초](13_iac/01_ansible/ansible_basic_guide.md) | 인벤토리, 플레이북, 롤 |
| [Ansible Vault](13_iac/01_ansible/ansible_vault.md) | 시크릿 암호화 |
| [Jenkins Pipeline](12_tech_stack/jenkins_pipeline.md) | Declarative/Scripted Pipeline |
| [Apache Airflow](12_tech_stack/airflow.md) | DAG, Operator, 스케줄링 |
| [AWS Step Functions](12_tech_stack/aws_step_functions.md) | 상태 머신, 워크플로우 |
| [Git 실무 가이드](12_tech_stack/git_guide.md) | diff, log, fetch, stash, rebase |
| [ArgoCD](12_tech_stack/argocd.md) | GitOps CD, Application 동기화 |
| [GitHub Actions](12_tech_stack/github_actions.md) | 워크플로우 자동화, Runner |
| [Helm](12_tech_stack/helm.md) | Kubernetes 패키지 매니저, Chart |
| [Apache Kafka](12_tech_stack/kafka.md) | 분산 메시지 스트리밍, Topic |
| [Kubernetes 기본](12_tech_stack/kubernetes_basic.md) | Pod/Deployment/Service, kubectl |
| [Prometheus & Grafana](12_tech_stack/prometheus_grafana.md) | 메트릭 수집, PromQL, 대시보드 |
| [Terraform](12_tech_stack/terraform.md) | IaC, HCL, State 관리, Module |

[⬆ 목차로 돌아가기](#목차)

---

## 기타 문서

| 문서 | 설명 |
|------|------|
| [라이선스 가이드](license_guide.md) | MIT/Apache/GPL/CC 라이선스 비교, 선택 가이드 |

---

## 추천 학습 순서

```
초급 (Linux 입문)
  02_basic_linux → 05_computer_science (IPv4/TCP) → 07_opensource (Docker)

중급 (시스템 관리)
  08_debugging_linux → 09_database (Index/Transaction) → 12_tech_stack

고급 (성능 최적화 & 보안)
  03_advanced_linux → 06_security → 09_database (Replication/Partition)
  → 10_nosql → 04_system_engineer (SE/SRE 로드맵)
```

---

## 문서 트리

- 01_install/
  - [ansible_install_and_team_operation.md](01_install/ansible_install_and_team_operation.md)
  - [mysql_install.md](01_install/mysql_install.md) / [postgresql_install.md](01_install/postgresql_install.md) / [mongodb_install.md](01_install/mongodb_install.md)
  - [docker_install_and_compose.md](01_install/docker_install_and_compose.md) / [kubernetes_install.md](01_install/kubernetes_install.md)
  - [nginx_install.md](01_install/nginx_install.md) / [apache_install.md](01_install/apache_install.md) / [haproxy_install.md](01_install/haproxy_install.md)
  - [redis_install.md](01_install/redis_install.md) / [elasticsearch_install.md](01_install/elasticsearch_install.md)
  - [prometheus_grafana_install.md](01_install/prometheus_grafana_install.md) / [vault_install.md](01_install/vault_install.md) / [jenkins_install.md](01_install/jenkins_install.md)
- 02_basic_linux/
  - [bash_math.md](02_basic_linux/bash_math.md) / [bash_trap_complete_guide.md](02_basic_linux/bash_trap_complete_guide.md) / [redirection.md](02_basic_linux/bash_file_redirection.md)
  - [root_password_recovery.md](02_basic_linux/root_password_recovery.md) / [shell_interactive_mode.md](02_basic_linux/shell_interactive_mode.md)
  - [vim.md](02_basic_linux/vim.md) / [vim_airline.md](02_basic_linux/vim_airline.md)
- 03_advanced_linux/
  - [bpftrace.md](03_advanced_linux/bpftrace.md)
- 04_system_engineer/
  - 01_roadmap/
    - [se_roadmap.md](04_system_engineer/01_roadmap/se_roadmap.md) / [sre_roadmap.md](04_system_engineer/01_roadmap/sre_roadmap.md) / [dba_roadmap.md](04_system_engineer/01_roadmap/dba_roadmap.md)
    - [se_complete_roadmap_programming_languages.md](04_system_engineer/01_roadmap/se_complete_roadmap_programming_languages.md)
  - 02_operations/
    - [game_infra_kpi_presentation.md](04_system_engineer/02_operations/game_infra_kpi_presentation.md) / [resource_utilization_monitoring.md](04_system_engineer/02_operations/resource_utilization_monitoring.md)
    - [backup_tools_comparison.md](04_system_engineer/02_operations/backup_tools_comparison.md) / [asn_and_cloudflare_ddos.md](04_system_engineer/02_operations/asn_and_cloudflare_ddos.md)
    - [cdn_proxy_origin_ip.md](04_system_engineer/02_operations/cdn_proxy_origin_ip.md) / [s3_gateway_endpoint_cross_account.md](04_system_engineer/02_operations/s3_gateway_endpoint_cross_account.md)
    - [vpc_peering_inter_region_guide.md](04_system_engineer/02_operations/vpc_peering_inter_region_guide.md) / [infra_monorepo_and_boilerplate.md](04_system_engineer/02_operations/infra_monorepo_and_boilerplate.md)
  - 03_tools/
    - [c_cpp_csharp_go_python_bash_comparison.md](04_system_engineer/03_tools/c_cpp_csharp_go_python_bash_comparison.md) / [lsp_guide.md](04_system_engineer/03_tools/lsp_guide.md) / [adr_guide.md](04_system_engineer/03_tools/adr_guide.md)
  - 04_ai/
    - [kiro_cli_command_reference.md](04_system_engineer/04_ai/kiro_cli_command_reference.md) / [kiro_model_guide.md](04_system_engineer/04_ai/kiro_model_guide.md)
    - [ai_development_request_template.md](04_system_engineer/04_ai/ai_development_request_template.md) / [ai_markdown_design_patterns.md](04_system_engineer/04_ai/ai_markdown_design_patterns.md)
  - 05_legal/
    - [drm_guide.md](04_system_engineer/05_legal/drm_guide.md) / [ip_ownership_guide.md](04_system_engineer/05_legal/ip_ownership_guide.md)
- 05_computer_science/
  - [cpu_cisc_risc.md](05_computer_science/cpu_cisc_risc.md) / [http_methods.md](05_computer_science/http_methods.md) / [ipv4_addressing_guide.md](05_computer_science/ipv4_addressing_guide.md)
  - [ipv6_addressing_guide.md](05_computer_science/ipv6_addressing_guide.md) / [network_headers.md](05_computer_science/network_headers.md) / [packet_analysis.md](05_computer_science/packet_analysis.md)
  - [switch_vlan_mode.md](05_computer_science/switch_vlan_mode.md) / [tcpdump_examples.md](05_computer_science/tcpdump_examples.md) / [TCP_state.md](05_computer_science/TCP_state.md)
  - 01_data_structures/
    - [array.md](05_computer_science/01_data_structures/array.md) / [stack.md](05_computer_science/01_data_structures/stack.md) / [queue.md](05_computer_science/01_data_structures/queue.md)
    - [linked_list.md](05_computer_science/01_data_structures/linked_list.md) / [binary_tree.md](05_computer_science/01_data_structures/binary_tree.md) / [graph.md](05_computer_science/01_data_structures/graph.md)
    - [heap.md](05_computer_science/01_data_structures/heap.md) / [hash_table.md](05_computer_science/01_data_structures/hash_table.md)
- 06_security/
  - [ddos_defense_architecture.md](06_security/ddos_defense_architecture.md) / [linux_hardening.md](06_security/linux_hardening.md) / [firewall_iptables_nftables.md](06_security/firewall_iptables_nftables.md)
  - [ssh_security.md](06_security/ssh_security.md) / [tls_ssl_guide.md](06_security/tls_ssl_guide.md) / [secret_management.md](06_security/secret_management.md)
  - [aws_security.md](06_security/aws_security.md) / [vulnerability_scanning.md](06_security/vulnerability_scanning.md)
- 07_opensource/
  - [docker_docker_compose_cheatsheet.md](12_tech_stack/docker_compose_cheatsheet.md) / [n8n_docker_cheatsheet.md](07_opensource/n8n_docker_cheatsheet.md)
  - [container_architecture.md](07_opensource/container_architecture.md) / [percona_xtrabackup_guide.md](07_opensource/percona_xtrabackup_guide.md)
  - [ansible_vs_jenkins.md](07_opensource/ansible_vs_jenkins.md)
- 08_debugging_linux/
  - [strace.md](08_debugging_linux/strace.md) / [ltrace.md](08_debugging_linux/ltrace.md) / [gdb.md](08_debugging_linux/gdb.md)
  - [perf.md](08_debugging_linux/perf.md) / [valgrind.md](08_debugging_linux/valgrind.md) / [lsof.md](08_debugging_linux/lsof.md)
  - [iotop.md](08_debugging_linux/iotop.md) / [tcpdump.md](08_debugging_linux/tcpdump.md)
- 09_database/
  - [rdbms_normalization.md](09_database/rdbms_normalization.md) / [rdbms_join.md](09_database/rdbms_join.md) / [rdbms_index.md](09_database/rdbms_index.md)
  - [rdbms_explain.md](09_database/rdbms_explain.md) / [rdbms_transaction.md](09_database/rdbms_transaction.md) / [rdbms_lock.md](09_database/rdbms_lock.md)
  - [rdbms_view.md](09_database/rdbms_view.md) / [rdbms_procedure.md](09_database/rdbms_procedure.md) / [rdbms_replication.md](09_database/rdbms_replication.md)
  - [rdbms_partition.md](09_database/rdbms_partition.md) / [rdbms_schema_migration.md](09_database/rdbms_schema_migration.md)
- 10_nosql/
  - [nosql_mongodb.md](10_nosql/nosql_mongodb.md) / [nosql_redis.md](10_nosql/nosql_redis.md) / [nosql_elasticsearch.md](10_nosql/nosql_elasticsearch.md)
- 11_python/
  - [python_class.md](11_python/python_class.md) / [python_class_components.md](11_python/python_class_components.md) / [python_inheritance.md](11_python/python_inheritance.md)
  - [python_functions.md](11_python/python_functions.md) / [python_control_flow.md](11_python/python_control_flow.md) / [python_exceptions.md](11_python/python_exceptions.md)
  - [python_decorators.md](11_python/python_decorators.md) / [python_generators.md](11_python/python_generators.md) / [python_comprehensions.md](11_python/python_comprehensions.md)
  - [python_context_managers.md](11_python/python_context_managers.md) / [python_file_io.md](11_python/python_file_io.md) / [python_data_structures.md](11_python/python_data_structures.md)
  - [python_packages.md](11_python/python_packages.md) / [python_virtual_env.md](11_python/python_virtual_env.md) / [python_logging.md](11_python/python_logging.md)
  - [python_regex.md](11_python/python_regex.md) / [python_string.md](11_python/python_string.md) / [python_json_yaml.md](11_python/python_json_yaml.md)
  - [python_subprocess.md](11_python/python_subprocess.md) / [python_argparse.md](11_python/python_argparse.md) / [python_os_pathlib.md](11_python/python_os_pathlib.md)
  - [python_magic_attributes.md](11_python/python_magic_attributes.md) / [python_print.md](11_python/python_print.md)
- 12_tech_stack/
  - [ansible_basic_guide.md](13_iac/01_ansible/ansible_basic_guide.md) / [ansible_vault.md](13_iac/01_ansible/ansible_vault.md) / [jenkins_pipeline.md](12_tech_stack/jenkins_pipeline.md)
  - [airflow.md](12_tech_stack/airflow.md) / [aws_step_functions.md](12_tech_stack/aws_step_functions.md) / [git_guide.md](12_tech_stack/git_guide.md)
  - [argocd.md](12_tech_stack/argocd.md) / [github_actions.md](12_tech_stack/github_actions.md) / [helm.md](12_tech_stack/helm.md)
  - [kafka.md](12_tech_stack/kafka.md) / [kubernetes_basic.md](12_tech_stack/kubernetes_basic.md) / [prometheus_grafana.md](12_tech_stack/prometheus_grafana.md)
  - [terraform.md](12_tech_stack/terraform.md)
- [license_guide.md](license_guide.md)
- [CHANGELOG.md](CHANGELOG.md)


## 참고 자료

- roadmap.sh: [roadmap.sh](https://roadmap.sh/) — ★★★☆☆
- Linux Documentation Project: [tldp.org](https://tldp.org/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-11

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
