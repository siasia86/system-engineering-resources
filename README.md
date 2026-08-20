# 시스템 엔지니어링 학습 자료 모음

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Linux, 네트워크, 보안, 데이터베이스, 인프라 도구, SRE 프로세스 등 시스템 엔지니어링 관련 학습 자료 저장소.

## 목차

| 섹션                                                                        |
|-----------------------------------------------------------------------------|
| [1. Fundamentals](#1-fundamentals) / [2. Infrastructure](#2-infrastructure) |
| [3. Engineering](#3-engineering) / [4. Security](#4-security)               |
| [5. Database](#5-database) / [6. Career](#6-career)                         |
| [추천 학습 순서](#추천-학습-순서) / [기타 문서](#기타-문서)                 |

---

## 1. Fundamentals

기초 지식 — Linux·Windows 운영체제, 네트워크, 컴퓨터 과학, 수학, 프로그래밍.

### Linux

| 문서                                                                            | 설명                        |
|---------------------------------------------------------------------------------|-----------------------------|
| [Linux 문서 목차](01_fundamentals/linux/README.md)                              | 주제별 분류, 학습 순서      |
| [저장장치 도구](01_fundamentals/linux/storage_tools.md)                         | 장치·공간·I/O·상태 확인     |
| [Bash 수학 연산](01_fundamentals/linux/bash_math.md)                            | 산술 연산, bc, awk          |
| [Bash trap 가이드](01_fundamentals/linux/bash_trap_complete_guide.md)           | 시그널 처리, 정리 작업      |
| [리다이렉션](01_fundamentals/linux/bash_file_redirection.md)                    | stdin/stdout/stderr, 파이프 |
| [Root 패스워드 복구](01_fundamentals/linux/root_password_recovery.md)           | 복구 모드, single user mode |
| [Shell 인터랙티브 모드](01_fundamentals/linux/shell_interactive_mode.md)        | interactive/non-interactive |
| [Vim 사용법](01_fundamentals/linux/vim.md)                                      | 기본 명령어, 모드, 설정     |
| [시스템 프로세스](01_fundamentals/linux/linux_system_processes.md)              | init, systemd, 데몬         |
| [Namespace](01_fundamentals/linux/namespace_concepts.md)                        | 7종 namespace, 격리         |
| [Cgroup](01_fundamentals/linux/cgroup_concepts.md)                              | v1/v2, 리소스 제한          |
| [Scheduler](01_fundamentals/linux/scheduler_concepts.md)                        | CFS, RT, Deadline           |
| [Virtual Memory](01_fundamentals/linux/virtual_memory_concepts.md)              | 페이지 테이블, TLB, OOM     |
| [VFS](01_fundamentals/linux/linux_virtual_fs.md)                                | inode, dentry, superblock   |
| [IPC](01_fundamentals/linux/ipc_concepts.md)                                    | Pipe, Socket, SHM, MQ       |
| [Netfilter/TC](01_fundamentals/linux/netfilter_tc.md)                           | iptables/nftables, TC       |
| [eBPF](01_fundamentals/linux/ebpf.md)                                           | eBPF 프로그래밍, 맵         |
| [bpftrace](01_fundamentals/linux/bpftrace.md)                                   | 동적 추적, 커널 분석        |
| [seccomp/Capabilities](01_fundamentals/linux/seccomp_capabilities.md)           | 시스템 콜 필터링            |
| [Process Lifecycle](01_fundamentals/linux/process_lifecycle.md)                 | fork, exec, zombie, orphan  |
| [strace](01_fundamentals/linux/strace.md)                                       | 시스템 콜 추적              |
| [ltrace](01_fundamentals/linux/ltrace.md)                                       | 라이브러리 함수 추적        |
| [gdb](01_fundamentals/linux/gdb.md)                                             | GNU 디버거                  |
| [perf](01_fundamentals/linux/perf.md)                                           | 성능 분석                   |
| [valgrind](01_fundamentals/linux/valgrind.md)                                   | 메모리 디버깅               |
| [lsof](01_fundamentals/linux/lsof.md)                                           | 열린 파일 확인              |
| [iotop](01_fundamentals/linux/iotop.md)                                         | I/O 모니터링                |
| [tcpdump](01_fundamentals/linux/tcpdump.md)                                     | 네트워크 패킷 캡처          |
| [OOM/Hang 진단](01_fundamentals/linux/oom_hang.md)                              | OOM Killer, kdump, sysrq    |
| [vim-airline](01_fundamentals/linux/vim_airline.md)                             | 상태바 플러그인             |
| [Character Set/Encoding](01_fundamentals/linux/character_set_encoding_guide.md) | UTF-8, BOM, 인코딩 디버깅   |

### Networking

| 문서                                                                             | 설명                         |
|----------------------------------------------------------------------------------|------------------------------|
| [IPv4 주소 체계](01_fundamentals/networking/ipv4_addressing_guide.md)            | 서브넷, CIDR, AWS VPC        |
| [IPv6 주소 체계](01_fundamentals/networking/ipv6_addressing_guide.md)            | 주소 구조, 표기법, SLAAC     |
| [TCP 상태 전이](01_fundamentals/networking/tcp_state_concepts.md)                | 3/4-Way Handshake, TIME_WAIT |
| [패킷 분석](01_fundamentals/networking/packet_analysis.md)                       | IP/TCP/UDP 헤더, PROXY Proto |
| [네트워크 헤더](01_fundamentals/networking/network_headers.md)                   | Ethernet, ARP, DNS, TLS      |
| [HTTP 메서드](01_fundamentals/networking/http_methods.md)                        | GET/POST/PUT/DELETE/PATCH    |
| [tcpdump 예제](01_fundamentals/networking/tcpdump_examples.md)                   | 패킷 캡처 실전 예제          |
| [Switch VLAN Mode](01_fundamentals/networking/switch_vlan_mode.md)               | Access/Trunk/Hybrid          |
| [VPN Protocol](01_fundamentals/networking/vpn_protocol_concepts.md)              | PPTP~WireGuard 비교          |
| [에러 코드](01_fundamentals/networking/error_codes.md)                           | HTTP/SMTP/FTP 상태 코드      |
| [ASN/DDoS 대응](01_fundamentals/networking/asn_and_cloudflare_ddos.md)           | ASN 운영, Cloudflare         |
| [CDN/Proxy/Origin](01_fundamentals/networking/cdn_proxy_origin_ip.md)            | CDN 구조, Origin IP 보호     |
| [SoftEther VPN Client](01_fundamentals/networking/softether_vpn_client_guide.md) | SoftEther 클라이언트 설정    |
| [SoftEther VPN Server](01_fundamentals/networking/softether_vpn_server_guide.md) | SoftEther 서버 설치·설정     |
| [VPN 프로토콜 선택 가이드](01_fundamentals/networking/vpn_comparison_blog.md)    | 프로토콜 비교·시나리오 선택  |

### CS

| 문서                                                             | 설명                         |
|------------------------------------------------------------------|------------------------------|
| [CPU CISC vs RISC](01_fundamentals/cs/cpu_cisc_risc_concepts.md) | 명령어 집합 아키텍처 비교    |
| [Git 개념](01_fundamentals/cs/git_concepts.md)                   | 내부 구조, 객체 모델         |
| [버전 관리 개념](01_fundamentals/cs/version_control_concepts.md) | VCS 비교, 브랜치 전략        |
| [자료구조](01_fundamentals/cs/data_structures/)                  | Array, Stack, Queue, Tree 등 |
| [테스팅](01_fundamentals/cs/testing/)                            | Black/White Box, 테스트 레벨 |

### Windows

| 문서                                                                                    | 설명                   |
|-----------------------------------------------------------------------------------------|------------------------|
| [Windows 서버 리소스 분석](01_fundamentals/windows/windows_server_resource_analysis.md) | CPU/메모리/디스크 분석 |

### Math

| 문서                                              | 설명                       |
|---------------------------------------------------|----------------------------|
| [ε-δ 논법](01_fundamentals/math/epsilon_delta.md) | 극한 정의, 증명 구조, 변형 |

### Programming

| 문서                                                                               | 설명                        |
|------------------------------------------------------------------------------------|-----------------------------|
| [Python 가이드](01_fundamentals/programming/python/)                               | 클래스~subprocess (26개)    |
| [C# 가이드](01_fundamentals/programming/csharp/)                                   | async, LINQ, OOP, 예외 처리 |
| [Rust 가이드](01_fundamentals/programming/rust/)                                   | 소유권, 동시성, 에러 처리   |
| [언어 비교](01_fundamentals/programming/c_cpp_csharp_go_python_bash_comparison.md) | 6개 언어 비교               |
| [Rust SE 로드맵](01_fundamentals/programming/rust_roadmap_for_se.md)               | SE 관점 Rust 학습 경로      |
| [LSP 가이드](01_fundamentals/programming/lsp_guide.md)                             | Language Server Protocol    |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Infrastructure

인프라 도구 + 일상 운영 — 컨테이너, CI/CD, IaC, 모니터링, 클라우드.

### Containers

| 문서                                                                                 | 설명                       |
|--------------------------------------------------------------------------------------|----------------------------|
| [Docker 설치 + Compose](02_infrastructure/containers/docker_install_and_compose.md)  | 설치, daemon.json, Compose |
| [Docker Compose 치트시트](02_infrastructure/containers/docker_compose_cheatsheet.md) | 명령어 정리                |
| [Docker 가이드](02_infrastructure/containers/docker.md)                              | 이미지, 네트워크, 볼륨     |
| [컨테이너 아키텍처](02_infrastructure/containers/container_architecture.md)          | Namespace, Cgroup, OCI     |
| [Container Runtime](02_infrastructure/containers/container_runtime.md)               | containerd, CRI-O          |
| [Kubernetes 설치](02_infrastructure/containers/kubernetes_install.md)                | k3s, kubeadm               |
| [Kubernetes 기본](02_infrastructure/containers/kubernetes_basic.md)                  | Pod, Deployment, Service   |
| [k3s](02_infrastructure/containers/k3s.md)                                           | 경량 K8s, SQLite 기반      |
| [Helm](02_infrastructure/containers/helm.md)                                         | Chart, Values, Release     |
| [n8n Docker](02_infrastructure/containers/n8n_docker_cheatsheet.md)                  | n8n 치트시트               |

### CI/CD

| 문서                                                                       | 설명                          |
|----------------------------------------------------------------------------|-------------------------------|
| [Jenkins 설치](02_infrastructure/cicd/jenkins_install.md)                  | 설치, 플러그인, 초기 설정     |
| [Jenkins Pipeline](02_infrastructure/cicd/jenkins_pipeline.md)             | Declarative/Scripted          |
| [GitHub Actions](02_infrastructure/cicd/github_actions.md)                 | 워크플로우, Runner            |
| [GitHub CLI](02_infrastructure/cicd/github_cli.md)                         | gh 명령어, PR/Issue           |
| [ArgoCD](02_infrastructure/cicd/argocd.md)                                 | GitOps CD, Application        |
| [Harness](02_infrastructure/cicd/harness_inc.md)                           | CI/CD 플랫폼                  |
| [Git 가이드](02_infrastructure/cicd/git_guide.md)                          | diff, log, rebase, stash      |
| [Airflow](02_infrastructure/cicd/airflow.md)                               | DAG, Operator, 스케줄링       |
| [AWS Step Functions](02_infrastructure/cicd/aws_step_functions.md)         | 상태 머신, 워크플로우         |
| [SVN 가이드](02_infrastructure/cicd/svn_guide.md)                          | Subversion 기본               |
| [Ansible vs Jenkins](02_infrastructure/cicd/ansible_vs_jenkins.md)         | 도구 비교                     |
| [DevOps Toolchain](02_infrastructure/cicd/devops_toolchain.md)             | 전체 파이프라인 도구 맵       |
| [Infra Monorepo](02_infrastructure/cicd/infra_monorepo_and_boilerplate.md) | 모노레포 구조, 보일러플레이트 |
| [.gitignore 패턴](02_infrastructure/cicd/gitignore_patterns.md)            | 언어별 패턴 정리              |

### IaC

| 문서                                                                           | 설명                     |
|--------------------------------------------------------------------------------|--------------------------|
| [Ansible 기초](02_infrastructure/iac/ansible_basic_guide.md)                   | 인벤토리, 플레이북, 롤   |
| [Ansible 팀 운영](02_infrastructure/iac/ansible_install_and_team_operation.md) | 설치, 팀 운영, 권한 관리 |
| [Ansible Vault](02_infrastructure/iac/ansible_vault.md)                        | 시크릿 암호화            |
| [Ansible Playbook Fields](02_infrastructure/iac/ansible_playbook_fields.md)    | 필드 레퍼런스            |
| [Ansible Linux](02_infrastructure/iac/ansible_playbook_linux.md)               | Linux 플레이북           |
| [Ansible Windows](02_infrastructure/iac/ansible_playbook_windows.md)           | Windows 플레이북         |
| [Molecule](02_infrastructure/iac/molecule.md)                                  | 역할 테스트              |
| [Terraform](02_infrastructure/iac/terraform.md)                                | HCL, State, Module       |
| [Packer](02_infrastructure/iac/packer.md)                                      | 이미지 빌드              |
| [Vagrant](02_infrastructure/iac/vagrant.md)                                    | 개발 환경 프로비저닝     |
| [YAML 문법](02_infrastructure/iac/yaml_syntax.md)                              | YAML 1.2 규칙            |

### Monitoring

| 문서                                                                                     | 설명                 |
|------------------------------------------------------------------------------------------|----------------------|
| [Prometheus + Grafana](02_infrastructure/monitoring/prometheus_grafana.md)               | PromQL, 대시보드     |
| [Prometheus 설치](02_infrastructure/monitoring/prometheus_grafana_install.md)            | 설치, Node Exporter  |
| [Zabbix vs Prometheus](02_infrastructure/monitoring/zabbix_vs_prometheus.md)             | 아키텍처 비교        |
| [리소스 모니터링](02_infrastructure/monitoring/resource_utilization_monitoring.md)       | CPU/메모리/디스크    |
| [게임 인프라 KPI](02_infrastructure/monitoring/game_infra_kpi_presentation.md)           | 운영 핵심 지표       |
| [Grafana Heatmap](02_infrastructure/monitoring/grafana_gitlab_heatmap.md)                | GitLab 커밋 히트맵   |
| [GRAID SupremeRAID 점검](02_infrastructure/monitoring/graid_supremeraid_server_check.md) | GPU RAID 점검 가이드 |
| [Gstack 모니터링](02_infrastructure/monitoring/gstack.md)                                | 통합 모니터링 스택   |

### Cloud (AWS)

| 문서                                                                                    | 설명                       |
|-----------------------------------------------------------------------------------------|----------------------------|
| [S3 버킷 생성 옵션](02_infrastructure/cloud_aws/s3_bucket_create_options.md)            | SSE, 버전관리, Object Lock |
| [S3 Gateway Endpoint](02_infrastructure/cloud_aws/s3_gateway_endpoint_cross_account.md) | 크로스 계정 S3 접근        |
| [S3 Object Lock](02_infrastructure/cloud_aws/s3_object_lock.md)                         | WORM, Compliance           |
| [S3 백업 팁](02_infrastructure/cloud_aws/s3_backup_tips.md)                             | 비용/성능/무결성           |
| [STS AssumeRole](02_infrastructure/cloud_aws/sts_assume_role.md)                        | 크로스 계정 역할 위임      |
| [백업 도구 비교](02_infrastructure/cloud_aws/backup_tools_comparison.md)                | AWS Backup vs 직접 구현    |
| [VPC Peering](02_infrastructure/cloud_aws/vpc_peering_inter_region_guide.md)            | Inter-Region Peering       |
| [AWS Network Firewall](02_infrastructure/cloud_aws/aws_network_firewall.md)             | 관리형 방화벽              |

### Windows Server

| 문서                                                                                           | 설명                 |
|------------------------------------------------------------------------------------------------|----------------------|
| [Windows Server 에디션](02_infrastructure/windows_server/windows_server_editions_licensing.md) | 에디션/라이선스 비교 |
| [Windows Server 핵심 개념](02_infrastructure/windows_server/windows_server_key_concepts.md)    | AD, DNS, 역할 서비스 |

### Data Pipeline

| 문서                                                                         | 설명                 |
|------------------------------------------------------------------------------|----------------------|
| [Kafka](02_infrastructure/data_pipeline/kafka.md)                            | 분산 메시지 스트리밍 |
| [게임 로그 파이프라인](02_infrastructure/data_pipeline/game_log_pipeline.md) | 수집→저장→분석       |
| [로그 100GB](02_infrastructure/data_pipeline/log_aggregation_100gb.md)       | 중규모 로그 설계     |
| [로그 100TB](02_infrastructure/data_pipeline/log_aggregation_100tb.md)       | 대규모 로그 설계     |

### Storage

| 문서                                                                   | 설명                    |
|------------------------------------------------------------------------|-------------------------|
| [스토리지 아키텍처](02_infrastructure/storage/storage_architecture.md) | 스토리지 계층·구성 설계 |

### Web Server

| 문서                                                       | 설명                       |
|------------------------------------------------------------|----------------------------|
| [Nginx](02_infrastructure/web_server/nginx_install.md)     | 가상 호스트, 리버스 프록시 |
| [Apache](02_infrastructure/web_server/apache_install.md)   | MPM, SSL                   |
| [HAProxy](02_infrastructure/web_server/haproxy_install.md) | L4/L7 LB, SSL 터미네이션   |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Engineering

시니어/아키텍트급 — SRE 프로세스, 전략, 조직 설계.

### Reliability

| 문서                                                                       | 설명                             |
|----------------------------------------------------------------------------|----------------------------------|
| [Incident Management](03_engineering/reliability/incident_management.md)   | 장애 등급, IC 역할, 에스컬레이션 |
| [SLO/Error Budget](03_engineering/reliability/slo_error_budget.md)         | SLI/SLO/SLA, Burn Rate Alert     |
| [On-Call Design](03_engineering/reliability/oncall_design.md)              | 로테이션, 25% 규칙, 런북         |
| [Postmortem Framework](03_engineering/reliability/postmortem_framework.md) | 5 Whys, Blameless, Action Items  |
| [Chaos Engineering](03_engineering/reliability/chaos_engineering.md)       | 가설 실험, 폭발 반경, Game Day   |

### Delivery

| 문서                                                                              | 설명                        |
|-----------------------------------------------------------------------------------|-----------------------------|
| [Change Management](03_engineering/delivery/change_management.md)                 | 변경 등급, CAB, 배포 윈도우 |
| [Zero Downtime Migration](03_engineering/delivery/zero_downtime_migration.md)     | Expand-Contract, CDC, 롤백  |
| [Capacity Planning](03_engineering/delivery/capacity_planning.md)                 | 트래픽 예측, Headroom       |
| [Multi-Region Architecture](03_engineering/delivery/multi_region_architecture.md) | Active-Active, RPO/RTO      |
| [ADR 가이드](03_engineering/delivery/adr_guide.md)                                | 아키텍처 의사결정 기록      |

### Organization

| 문서                                                                        | 설명                             |
|-----------------------------------------------------------------------------|----------------------------------|
| [Platform Engineering](03_engineering/organization/platform_engineering.md) | IDP, Golden Path, Self-service   |
| [Team Topology](03_engineering/organization/team_topology.md)               | Stream-aligned/Platform/Enabling |
| [Vendor Evaluation](03_engineering/organization/vendor_evaluation.md)       | PoC, TCO, Lock-in 평가           |
| [Legacy Modernization](03_engineering/organization/legacy_modernization.md) | Strangler Fig, 점진적 전환       |

### Cost

| 문서                                                                      | 설명                      |
|---------------------------------------------------------------------------|---------------------------|
| [Cloud Cost Optimization](03_engineering/cost/cloud_cost_optimization.md) | RI/SP, Spot, FinOps       |
| [Tech Debt Management](03_engineering/cost/tech_debt_management.md)       | 분류, 측정, 상환 우선순위 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. Security

보안 — 서버 강화, 클라우드 보안, 취약점 관리.

### Hardening

| 문서                                                                | 설명                        |
|---------------------------------------------------------------------|-----------------------------|
| [Linux 서버 보안 강화](04_security/hardening/linux_hardening.md)    | sysctl, auditd, umask       |
| [방화벽](04_security/hardening/firewall_iptables_nftables.md)       | iptables/nftables           |
| [SSH 보안](04_security/hardening/ssh_security.md)                   | 키 인증, fail2ban           |
| [TLS/SSL](04_security/hardening/tls_ssl_guide.md)                   | 인증서, Let's Encrypt, mTLS |
| [시크릿 관리](04_security/hardening/secret_management.md)           | Vault, AWS Secrets Manager  |
| [취약점 스캔](04_security/hardening/vulnerability_scanning.md)      | nmap, trivy, lynis          |
| [Gitleaks 가이드](04_security/hardening/gitleaks_guide.md)          | 민감정보 탐지, pre-commit   |
| [Vault 설치](04_security/hardening/vault_install.md)                | HashiCorp Vault 설치·운영   |
| [Windows OpenSSH](04_security/hardening/windows_openssh_install.md) | Windows SSH 서버 설치       |

### Cloud Security

| 문서                                                                    | 설명                     |
|-------------------------------------------------------------------------|--------------------------|
| [AWS 보안](04_security/cloud/aws_security.md)                           | IAM, SG, WAF, GuardDuty  |
| [DDoS 방어 아키텍처](04_security/cloud/ddos_defense_architecture.md)    | XDP/nftables/CrowdSec    |
| [AWS Network Firewall](04_security/cloud/aws_network_firewall_guide.md) | 관리형 방화벽 가이드     |
| [네트워크 공격 용어](04_security/cloud/network_attack_glossary.md)      | DDoS, MITM, ARP Spoofing |

### CVE / CWE

| 문서                                | 설명              |
|-------------------------------------|-------------------|
| [CVE 분석](04_security/cve/)        | 커널 CVE 5건+     |
| [웹 CWE 분석](04_security/web_cwe/) | Path Traversal 등 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. Database

RDBMS, NoSQL, 운영, 포렌식.

### RDBMS Core

| 문서                                                        | 설명                    |
|-------------------------------------------------------------|-------------------------|
| [정규화](05_database/rdbms/rdbms_normalization.md)          | 1NF~BCNF, 반정규화      |
| [JOIN](05_database/rdbms/rdbms_join.md)                     | JOIN 종류, 실행 방식    |
| [Index](05_database/rdbms/rdbms_index.md)                   | B-Tree, 복합/커버링     |
| [EXPLAIN](05_database/rdbms/rdbms_explain.md)               | 실행 계획, 슬로우 쿼리  |
| [Transaction](05_database/rdbms/rdbms_transaction.md)       | ACID, 격리 수준, MVCC   |
| [Lock](05_database/rdbms/rdbms_lock.md)                     | Row/Gap Lock, 데드락    |
| [View](05_database/rdbms/rdbms_view.md)                     | View, Materialized View |
| [Procedure](05_database/rdbms/rdbms_procedure.md)           | 저장 프로시저, 커서     |
| [Storage Engine](05_database/rdbms/mysql_storage_engine.md) | InnoDB, MyISAM 비교     |

### DB Operations

| 문서                                                                     | 설명                    |
|--------------------------------------------------------------------------|-------------------------|
| [MySQL 설치](05_database/operations/mysql_install.md)                    | Ubuntu/RHEL, 초기 보안  |
| [PostgreSQL 설치](05_database/operations/postgresql_install.md)          | pg_hba.conf, ICU        |
| [Replication](05_database/operations/rdbms_replication.md)               | binlog, GTID, Streaming |
| [Partition](05_database/operations/rdbms_partition.md)                   | Range/List/Hash         |
| [Schema Migration](05_database/operations/rdbms_schema_migration.md)     | pt-osc, gh-ost          |
| [Server Config](05_database/operations/rdbms_server_config.md)           | my.cnf, postgresql.conf |
| [Slow Query](05_database/operations/rdbms_slow_query.md)                 | 슬로우 쿼리 분석        |
| [Tuning](05_database/operations/rdbms_tuning.md)                         | 버퍼풀, 캐시, I/O       |
| [Percona XtraBackup](05_database/operations/percona_xtrabackup_guide.md) | MySQL 물리 백업·복구    |

### NoSQL

| 문서                                                             | 설명                     |
|------------------------------------------------------------------|--------------------------|
| [Redis](05_database/nosql/nosql_redis.md)                        | 인메모리, 캐시, 분산 락  |
| [MongoDB](05_database/nosql/nosql_mongodb.md)                    | Document DB, Aggregation |
| [Elasticsearch](05_database/nosql/nosql_elasticsearch.md)        | 전문 검색, ELK           |
| [Redis 설치](05_database/nosql/redis_install.md)                 | requirepass, Slow Log    |
| [MongoDB 설치](05_database/nosql/mongodb_install.md)             | 인증, 백업               |
| [Elasticsearch 설치](05_database/nosql/elasticsearch_install.md) | ELK, ILM, Compose        |

### Forensics

| 문서                                                   | 설명        |
|--------------------------------------------------------|-------------|
| [DB 아키텍처](05_database/forensics/architecture.md)   | 내부 구조   |
| [포렌식](05_database/forensics/forensics.md)           | 데이터 분석 |
| [복구 가이드](05_database/forensics/recovery_guide.md) | 장애 복구   |

[⬆ 목차로 돌아가기](#목차)

---

## 6. Career

커리어 로드맵, 법률, AI 도구.

### Roadmap

| 문서                                                                            | 설명                  |
|---------------------------------------------------------------------------------|-----------------------|
| [SE 로드맵](06_career/roadmap/se_roadmap.md)                                    | 시스템 엔지니어 경로  |
| [SRE 로드맵](06_career/roadmap/sre_roadmap.md)                                  | Site Reliability 경로 |
| [DBA 로드맵](06_career/roadmap/dba_roadmap.md)                                  | DBA 역할, 자격증      |
| [언어별 가이드](06_career/roadmap/se_complete_roadmap_programming_languages.md) | 언어 선택 기준        |
| [인프라 직무 비교](06_career/roadmap/infra_roles_comparison.md)                 | 직무·역할·기술 비교   |

### Legal

| 문서                                                    | 설명                   |
|---------------------------------------------------------|------------------------|
| [DRM 가이드](06_career/legal/drm_guide.md)              | DRM, Tivoization, DMCA |
| [업무 외 저작물](06_career/legal/ip_ownership_guide.md) | 저작권법 제9조, 귀속   |

### AI Tools

| 문서                                                                         | 설명                                       |
|------------------------------------------------------------------------------|--------------------------------------------|
| [Kiro CLI 레퍼런스](06_career/ai_tools/kiro_cli_command_reference.md)        | 명령어 전체 정리                           |
| [Kiro 모델 가이드](06_career/ai_tools/kiro_model_guide.md)                   | 모델 선택 기준                             |
| [Kiro 설정 가이드](06_career/ai_tools/kiro_setup_guide.md)                   | CLI 초기 설정                              |
| [Kiro Agent Lock](06_career/ai_tools/kiro_agent_lock.md)                     | 동시 실행 방지                             |
| [AI 개발 요청 템플릿](06_career/ai_tools/ai_development_request_template.md) | AI 활용 요청 양식                          |
| [AI Markdown 패턴](06_career/ai_tools/ai_markdown_design_patterns.md)        | 에이전트용 문서 패턴                       |
| [AI 코딩 도구 비교](06_career/ai_tools/ai_coding_tools_comparison.md)        | Kiro·Claude Code·Codex·Cursor·Copilot 비교 |
| [Harness Engineering](06_career/ai_tools/harness_engineering.md)             | AI 에이전트 환경 설계                      |
| [Loop Engineering](06_career/ai_tools/loop_engineering.md)                   | AI 루프 설계                               |

[⬆ 목차로 돌아가기](#목차)

---

## 추천 학습 순서

### 초급 (Linux 입문)

[Linux 문서 목차](01_fundamentals/linux/README.md) → [저장장치 도구](01_fundamentals/linux/storage_tools.md) → [IPv4 주소 체계](01_fundamentals/networking/ipv4_addressing_guide.md) → [TCP 상태 전이](01_fundamentals/networking/tcp_state_concepts.md) → [Docker 가이드](02_infrastructure/containers/docker.md)

### 중급 (시스템 관리)

[OOM/Hang 진단](01_fundamentals/linux/oom_hang.md) → [Database](05_database/README.md) → [Infrastructure](02_infrastructure/README.md)

### 고급 (SRE/아키텍트)

[Security](04_security/README.md) → [Engineering](03_engineering/README.md) → [SE 로드맵](06_career/roadmap/se_roadmap.md)

---

## 기타 문서

| 문서                                                                      | 설명                                         |
|---------------------------------------------------------------------------|----------------------------------------------|
| [라이선스 가이드](license_guide.md)                                       | MIT/Apache/GPL/CC 라이선스 비교, 선택 가이드 |
| [유사 레포 비교](97_misc/similar_repos.md)                                | 벤치마킹, 차별화 전략                        |
| [Windows 인시던트 로그 수집](96_scripts/windows/collect_incident_logs.py) | 장애 시 로그 자동 수집 스크립트              |
| [Windows Hosts 관리](96_scripts/windows/win_hosts_manager.py)             | hosts 파일 관리 도구                         |
| [공식 참고 문서 인덱스](_reference/INDEX.md)                              | 기술별 공식 문서와 확인일 관리               |
| [Governance 및 도구 미러](00_governance/README.md)                        | 저장소 정책과 AI 도구 미러 인덱스            |
| [Kiro 운영 문서](00_governance/02_kiro/README.md)                         | Kiro Skill·Hook·운영 자료                    |
| [저장소 운영 정책](00_governance/01_repository_governance/README.md)      | 문서 생명주기·동기화·작업 템플릿             |

### 문서 검증

문서 수정 후 다음 검사를 실행합니다.

```bash
python3 md-link-check.py README.md
python3 md-style-check.py README.md
python3 readme_inventory_check.py README.md
```

- 내부 링크·앵커 검사: `md-link-check.py`.
- 표·푸터·문체 검사: `md-style-check.py`.
- README에 표기된 문서 수와 실제 파일 수 검사: `readme_inventory_check.py`.

---

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

**마지막 업데이트**: 2026-08-20

© 2026 siasia86. Licensed under CC BY 4.0.
