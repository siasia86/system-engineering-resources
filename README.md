# 시스템 엔지니어링 학습 자료 모음

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Linux, 네트워크, 보안, 데이터베이스, 인프라 도구, SRE 프로세스 등 시스템 엔지니어링 관련 학습 자료 저장소.

## 목차

| 섹션                                                                        |
|-----------------------------------------------------------------------------|
| [1. Fundamentals](#1-fundamentals) / [2. Infrastructure](#2-infrastructure) |
| [3. Engineering](#3-engineering) / [4. Security](#4-security)               |
| [5. Database](#5-database) / [6. Career](#6-career)                         |
| [7. AI Transformation](#7-ai-transformation) / [8. Art](#8-art)             |
| [추천 학습 순서](#추천-학습-순서) / [기타 문서](#기타-문서)                 |

---

## 1. Fundamentals

기초 지식 — Linux·Windows 운영체제, 네트워크, 컴퓨터 과학, 수학, 프로그래밍.

### Linux

| 문서                                                                            | 설명                                |
|---------------------------------------------------------------------------------|-------------------------------------|
| [Linux 문서 목차](01_fundamentals/linux/README.md)                              | 주제별 분류, 학습 순서              |
| [저장장치 도구](01_fundamentals/linux/storage_tools.md)                         | 장치·공간·I/O·상태 확인             |
| [Bash 수학 연산](01_fundamentals/linux/bash_math.md)                            | 산술 연산, bc, awk                  |
| [Bash trap 가이드](01_fundamentals/linux/bash_trap_complete_guide.md)           | 시그널 처리, 정리 작업              |
| [리다이렉션](01_fundamentals/linux/bash_file_redirection.md)                    | stdin/stdout/stderr, 파이프         |
| [Bash 스크립트](01_fundamentals/linux/bash_scripting.md)                        | 엄격 모드, getopts, ShellCheck      |
| [텍스트 처리](01_fundamentals/linux/text_processing.md)                         | grep·sed·awk·sort·uniq              |
| [Ubuntu·Debian](01_fundamentals/linux/ubuntu_debian.md)                         | 판·지원 기간, apt                   |
| [RHEL 계열](01_fundamentals/linux/rhel_family.md)                               | Rocky·Alma, dnf, EPEL               |
| [SUSE Linux](01_fundamentals/linux/suse_linux.md)                               | SLES·openSUSE, zypper               |
| [BSD 계열](01_fundamentals/linux/bsd_family.md)                                 | FreeBSD·OpenBSD·NetBSD              |
| [프로세스 모니터링](01_fundamentals/linux/process_monitoring.md)                | ps·top·htop·pgrep, 상태와 load 해석 |
| [sysstat](01_fundamentals/linux/sysstat.md)                                     | sar·mpstat·iostat, 과거 기록        |
| [Linux 네트워크 점검 도구](01_fundamentals/linux/linux_network_tools.md)        | ip·ss·dig·curl·mtr·nmap             |
| [Root 패스워드 복구](01_fundamentals/linux/root_password_recovery.md)           | 복구 모드, single user mode         |
| [Shell 인터랙티브 모드](01_fundamentals/linux/shell_interactive_mode.md)        | interactive/non-interactive         |
| [Vim 사용법](01_fundamentals/linux/vim.md)                                      | 기본 명령어, 모드, 설정             |
| [nano](01_fundamentals/linux/nano.md)                                           | 단축키, nanorc                      |
| [시스템 프로세스](01_fundamentals/linux/linux_system_processes.md)              | init, systemd, 데몬                 |
| [systemd 유닛 관리](01_fundamentals/linux/systemd_unit_management.md)           | 유닛 파일, drop-in, timer           |
| [journalctl·logrotate](01_fundamentals/linux/journald_logrotate_guide.md)       | 저널 조회, 로그 순환                |
| [Namespace](01_fundamentals/linux/namespace_concepts.md)                        | 7종 namespace, 격리                 |
| [Cgroup](01_fundamentals/linux/cgroup_concepts.md)                              | v1/v2, 리소스 제한                  |
| [Scheduler](01_fundamentals/linux/scheduler_concepts.md)                        | CFS, RT, Deadline                   |
| [Virtual Memory](01_fundamentals/linux/virtual_memory_concepts.md)              | 페이지 테이블, TLB, OOM             |
| [VFS](01_fundamentals/linux/linux_virtual_fs.md)                                | inode, dentry, superblock           |
| [sysctl 커널 매개변수](01_fundamentals/linux/sysctl_kernel_parameters.md)       | /proc/sys, sysctl.d                 |
| [POSIX ACL·setfacl](01_fundamentals/linux/acl_setfacl_guide.md)                 | ACL·Default ACL·mask·상속           |
| [IPC](01_fundamentals/linux/ipc_concepts.md)                                    | Pipe, Socket, SHM, MQ               |
| [Netfilter/TC](01_fundamentals/linux/netfilter_tc.md)                           | iptables/nftables, TC               |
| [eBPF](01_fundamentals/linux/ebpf.md)                                           | eBPF 프로그래밍, 맵                 |
| [bpftrace](01_fundamentals/linux/bpftrace.md)                                   | 동적 추적, 커널 분석                |
| [seccomp/Capabilities](01_fundamentals/linux/seccomp_capabilities.md)           | 시스템 콜 필터링                    |
| [Process Lifecycle](01_fundamentals/linux/process_lifecycle.md)                 | fork, exec, zombie, orphan          |
| [strace](01_fundamentals/linux/strace.md)                                       | 시스템 콜 추적                      |
| [ltrace](01_fundamentals/linux/ltrace.md)                                       | 라이브러리 함수 추적                |
| [gdb](01_fundamentals/linux/gdb.md)                                             | GNU 디버거                          |
| [perf](01_fundamentals/linux/perf.md)                                           | 성능 분석                           |
| [valgrind](01_fundamentals/linux/valgrind.md)                                   | 메모리 디버깅                       |
| [lsof](01_fundamentals/linux/lsof.md)                                           | 열린 파일 확인                      |
| [iotop](01_fundamentals/linux/iotop.md)                                         | I/O 모니터링                        |
| [tcpdump](01_fundamentals/linux/tcpdump.md)                                     | 네트워크 패킷 캡처                  |
| [OOM/Hang 진단](01_fundamentals/linux/oom_hang.md)                              | OOM Killer, kdump, sysrq            |
| [vim-airline](01_fundamentals/linux/vim_airline.md)                             | 상태바 플러그인                     |
| [Character Set/Encoding](01_fundamentals/linux/character_set_encoding_guide.md) | UTF-8, BOM, 인코딩 디버깅           |

### Networking

| 문서                                                                                         | 설명                               |
|----------------------------------------------------------------------------------------------|------------------------------------|
| [IPv4 주소 체계](01_fundamentals/networking/ipv4_addressing_guide.md)                        | 서브넷, CIDR, AWS VPC              |
| [IPv6 주소 체계](01_fundamentals/networking/ipv6_addressing_guide.md)                        | 주소 구조, 표기법, SLAAC           |
| [TCP 상태 전이](01_fundamentals/networking/tcp_state_concepts.md)                            | 3/4-Way Handshake, TIME_WAIT       |
| [패킷 분석](01_fundamentals/networking/packet_analysis.md)                                   | IP/TCP/UDP 헤더, PROXY Proto       |
| [네트워크 헤더](01_fundamentals/networking/network_headers.md)                               | Ethernet, ARP, DNS, TLS            |
| [HTTP 메서드](01_fundamentals/networking/http_methods.md)                                    | GET/POST/PUT/DELETE/PATCH          |
| [Switch VLAN Mode](01_fundamentals/networking/switch_vlan_mode.md)                           | Access/Trunk/Hybrid                |
| [VPN Protocol](01_fundamentals/networking/vpn_protocol_concepts.md)                          | PPTP~WireGuard 비교                |
| [에러 코드](01_fundamentals/networking/error_codes.md)                                       | HTTP/SMTP/FTP 상태 코드            |
| [ASN/DDoS 대응](01_fundamentals/networking/asn_and_cloudflare_ddos.md)                       | ASN 운영, Cloudflare               |
| [CDN/Proxy/Origin](01_fundamentals/networking/cdn_proxy_origin_ip.md)                        | CDN 구조, Origin IP 보호           |
| [SoftEther VPN Client](01_fundamentals/networking/softether_vpn_client_guide.md)             | SoftEther 클라이언트 설정          |
| [SoftEther VPN Server](01_fundamentals/networking/softether_vpn_server_guide.md)             | SoftEther 서버 설치·설정           |
| [SoftEther VPN 경유 서버 작업](01_fundamentals/networking/softether_vpn_linux_server_ops.md) | Ubuntu·Rocky, OTP, Split Tunnel    |
| [VPN 프로토콜 선택 가이드](01_fundamentals/networking/vpn_comparison_blog.md)                | 프로토콜 비교·시나리오 선택        |
| [DNS 해석·장애 진단](01_fundamentals/networking/dns_resolution_troubleshooting.md)           | 해석 흐름, TTL, dig 진단           |
| [MTU·MSS·PMTUD](01_fundamentals/networking/mtu_mss_pmtud.md)                                 | 단편화, PMTUD 블랙홀, MSS clamping |
| [OSI 모델](01_fundamentals/networking/osi_model.md)                                          | 7계층, TCP/IP 대응, 계층별 진단    |
| [HTTP와 HTTPS](01_fundamentals/networking/http_https.md)                                     | 판 비교, TLS·ALPN·HSTS             |
| [FTP와 SFTP](01_fundamentals/networking/ftp_sftp.md)                                         | FTPS(vsftpd), SFTP chroot          |
| [SSH 사용](01_fundamentals/networking/ssh.md)                                                | 키, config, ProxyJump, 포워딩      |
| [메일 프로토콜](01_fundamentals/networking/mail_protocols.md)                                | SMTP·IMAP·POP3, Postfix·Dovecot    |

### CS

| 문서                                                             | 설명                              |
|------------------------------------------------------------------|-----------------------------------|
| [CPU CISC vs RISC](01_fundamentals/cs/cpu_cisc_risc_concepts.md) | 명령어 집합 아키텍처 비교         |
| [Git 개념](01_fundamentals/cs/git_concepts.md)                   | 내부 구조, 객체 모델              |
| [버전 관리 개념](01_fundamentals/cs/version_control_concepts.md) | VCS 비교, 브랜치 전략             |
| [압축 알고리즘](01_fundamentals/cs/compression_algorithms.md)    | 허프만, DEFLATE, gzip, ZIP, zstd  |
| [분산 기초](01_fundamentals/cs/distributed_systems_concepts.md)  | CAP·쿼럼·Raft·논리 시계           |
| [수 표현](01_fundamentals/cs/number_representation.md)           | 2의 보수, IEEE 754, 엔디언        |
| [자료구조](01_fundamentals/cs/data_structures/)                  | Tree·Hash·블룸 필터·HLL 등        |
| [테스팅](01_fundamentals/cs/testing/)                            | Black/White Box, 테스트 레벨      |
| [게임 테스트](01_fundamentals/cs/game_testing/)                  | 게임 상태·시나리오·경제·성능      |
| [웹 서버 테스트](01_fundamentals/cs/web_testing/)                | HTTP·프록시·TLS·LB·캐시·보안·관측 |
| [알고리즘](01_fundamentals/cs/algorithms/)                       | 복잡도 계산, 일관된 해싱          |

### Windows

| 문서                                                                                    | 설명                                  |
|-----------------------------------------------------------------------------------------|---------------------------------------|
| [Windows 서버 리소스 분석](01_fundamentals/windows/windows_server_resource_analysis.md) | CPU/메모리/디스크 분석                |
| [Windows 네트워크 진단](01_fundamentals/windows/windows_network_diagnostics.md)         | Test-NetConnection, pktmon            |
| [PowerShell](01_fundamentals/windows/powershell.md)                                     | 설치, 객체 파이프라인, 스크립트, 원격 |

### Math

| 문서                                                               | 설명                       |
|--------------------------------------------------------------------|----------------------------|
| [ε-δ 논법](01_fundamentals/math/epsilon_delta.md)                  | 극한 정의, 증명 구조, 변형 |
| [Little 법칙·대기열](01_fundamentals/math/littles_law_queueing.md) | L=λW, 사용률, 용량 계획    |

### Programming

| 문서                                                                               | 설명                        |
|------------------------------------------------------------------------------------|-----------------------------|
| [Python 가이드](01_fundamentals/programming/python/)                               | 클래스~subprocess (31개)    |
| [uv 가이드](01_fundamentals/programming/python/python_uv.md)                       | uv로 버전·가상환경 관리     |
| [C# 가이드](01_fundamentals/programming/csharp/)                                   | async, LINQ, OOP, 예외 처리 |
| [Rust 가이드](01_fundamentals/programming/rust/)                                   | 소유권, 동시성, 에러 처리   |
| [언어 비교](01_fundamentals/programming/c_cpp_csharp_go_python_bash_comparison.md) | 6개 언어 비교               |
| [Rust SE 로드맵](01_fundamentals/programming/rust_roadmap_for_se.md)               | SE 관점 Rust 학습 경로      |
| [Rust 전환 가이드](01_fundamentals/programming/rust/rust_for_bash_python_se.md)    | bash·python 사용자용 대응표 |
| [Rust 기초 문법](01_fundamentals/programming/rust/rust_basics.md)                  | 변수~모듈, bash·python 비교 |
| [LSP 가이드](01_fundamentals/programming/lsp_guide.md)                             | Language Server Protocol    |
| [GraphQL 가이드](01_fundamentals/programming/graphql_guide_for_se.md)              | SE 관점 GraphQL             |
| [gRPC 가이드](01_fundamentals/programming/grpc_guide_for_se.md)                    | SE 관점 gRPC                |
| [Protocol Buffers 가이드](01_fundamentals/programming/protobuf_guide_for_se.md)    | SE 관점 Protocol Buffers    |
| [REST API 가이드](01_fundamentals/programming/rest_api_guide_for_se.md)            | SE 관점 REST API            |
| [Lean SE 로드맵](01_fundamentals/programming/lean_roadmap_for_se.md)               | SE 관점 Lean 학습 경로      |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Infrastructure

인프라 도구 + 일상 운영 — 컨테이너, CI/CD, IaC, 모니터링, 클라우드.

### Containers

| 문서                                                                                | 설명                              |
|-------------------------------------------------------------------------------------|-----------------------------------|
| [Docker 설치 + 초기 설정](02_infrastructure/containers/docker_install.md)           | 설치, daemon.json, 방화벽         |
| [Docker Compose](02_infrastructure/containers/docker_compose.md)                    | 설치, compose.yaml, 명령, 검증    |
| [Docker 네트워크](02_infrastructure/containers/docker_network.md)                   | bridge, macvlan, 포트 공개        |
| [systemd 포함 컨테이너](02_infrastructure/containers/systemd_container.md)          | privileged, cgroupns, 시험 대상   |
| [Docker 명령 치트시트](02_infrastructure/containers/docker_cheatsheet.md)           | docker 명령 한 줄 정리            |
| [Docker 가이드](02_infrastructure/containers/docker.md)                             | 이미지, 볼륨, cgroup              |
| [Dockerfile 작성과 빌드](02_infrastructure/containers/dockerfile_best_practices.md) | 멀티 스테이지, BuildKit, 캐시     |
| [컨테이너 아키텍처](02_infrastructure/containers/container_architecture.md)         | Namespace, Cgroup, OCI            |
| [Container Runtime](02_infrastructure/containers/container_runtime.md)              | containerd, CRI-O                 |
| [Podman](02_infrastructure/containers/podman.md)                                    | rootless, Quadlet, Pod            |
| [Kubernetes 설치](02_infrastructure/containers/kubernetes_install.md)               | k3s, kubeadm                      |
| [Kubernetes 기본](02_infrastructure/containers/kubernetes_basic.md)                 | Pod, Deployment, Service          |
| [Kubernetes 장애 진단](02_infrastructure/containers/kubernetes_troubleshooting.md)  | Pod 상태별 원인, kubectl debug    |
| [kind](02_infrastructure/containers/kind.md)                                        | Docker 컨테이너 노드 K8s, 시험·CI |
| [k3s](02_infrastructure/containers/k3s.md)                                          | 경량 K8s, SQLite 기반             |
| [Helm](02_infrastructure/containers/helm.md)                                        | Chart, Values, Release            |
| [n8n Docker](02_infrastructure/containers/n8n_docker_cheatsheet.md)                 | n8n 치트시트                      |

### CI/CD

| 문서                                                                                    | 설명                                                  |
|-----------------------------------------------------------------------------------------|-------------------------------------------------------|
| [Jenkins 설치](02_infrastructure/cicd/jenkins_install.md)                               | 설치, 플러그인, 초기 설정                             |
| [Jenkins Pipeline](02_infrastructure/cicd/jenkins_pipeline.md)                          | Declarative/Scripted                                  |
| [GitHub Actions](02_infrastructure/cicd/github_actions.md)                              | 워크플로우, Runner                                    |
| [GitHub CLI 명령어 참조](02_infrastructure/cicd/gh_command_reference.md)                | gh 명령어, PR·Actions 실행                            |
| [GitHub](02_infrastructure/cicd/github.md)                                              | 2FA, SSH 키, PR, 브랜치 보호                          |
| [GitLab CI/CD](02_infrastructure/cicd/gitlab_ci.md)                                     | .gitlab-ci.yml, rules, Runner                         |
| [GitLab](02_infrastructure/cicd/gitlab.md)                                              | Docker 자체 설치, 운영, 백업                          |
| [Git 호스팅 비교](02_infrastructure/cicd/git_hosting_comparison.md)                     | GitHub·GitLab·Bitbucket, 이전                         |
| [Nexus Repository](02_infrastructure/cicd/nexus.md)                                     | 저장소 관리자, Docker·PyPI 프록시                     |
| [아티팩트 저장소 비교](02_infrastructure/cicd/artifact_repository_comparison.md)        | Nexus·Artifactory·Cloudsmith                          |
| [CI/CD 도구 비교](02_infrastructure/cicd/ci_tools_comparison.md)                        | Jenkins·GitLab CI·TeamCity·CircleCI·Buildkite·Octopus |
| [ArgoCD](02_infrastructure/cicd/argocd.md)                                              | GitOps CD, Application                                |
| [FluxCD](02_infrastructure/cicd/fluxcd.md)                                              | GitOps 컨트롤러, Argo CD 비교                         |
| [Harness](02_infrastructure/cicd/harness_inc.md)                                        | CI/CD 플랫폼                                          |
| [Git 가이드](02_infrastructure/cicd/git_guide.md)                                       | diff, log, rebase, stash                              |
| [Git 명령어 참조](02_infrastructure/cicd/git_command_reference.md)                      | 설정, 브랜치, 원격, 복구                              |
| [Airflow](02_infrastructure/cicd/airflow.md)                                            | DAG, Operator, 스케줄링                               |
| [AWS Step Functions](02_infrastructure/cicd/aws_step_functions.md)                      | 상태 머신, 워크플로우                                 |
| [SVN 가이드](02_infrastructure/cicd/svn_guide.md)                                       | Subversion 기본                                       |
| [Ansible vs Jenkins](02_infrastructure/cicd/ansible_vs_jenkins.md)                      | 도구 비교                                             |
| [DevOps Toolchain](02_infrastructure/cicd/devops_toolchain.md)                          | 전체 파이프라인 도구 맵                               |
| [Infra Monorepo](02_infrastructure/cicd/infra_monorepo_and_boilerplate.md)              | 모노레포 구조, 보일러플레이트                         |
| [.gitignore 패턴](02_infrastructure/cicd/gitignore_patterns.md)                         | 언어별 패턴 정리                                      |
| [Git 이력 민감 파일 제거](02_infrastructure/cicd/git_history_sensitive_file_removal.md) | 이력 재작성 런북                                      |

### IaC

| 문서                                                                           | 설명                        |
|--------------------------------------------------------------------------------|-----------------------------|
| [Ansible 기초](02_infrastructure/iac/ansible_basic_guide.md)                   | 인벤토리, 플레이북, 롤      |
| [Ansible 팀 운영](02_infrastructure/iac/ansible_install_and_team_operation.md) | 설치, 팀 운영, 권한 관리    |
| [Ansible Vault](02_infrastructure/iac/ansible_vault.md)                        | 시크릿 암호화               |
| [SOPS](02_infrastructure/iac/sops.md)                                          | 값 단위 암호화, age         |
| [ansible-lint](02_infrastructure/iac/ansible_lint.md)                          | 정적 검사, profile, CI      |
| [Jinja2](02_infrastructure/iac/jinja2.md)                                      | 템플릿 문법, template 모듈  |
| [yamllint](02_infrastructure/iac/yamllint.md)                                  | YAML 형식 검사, CI          |
| [Ansible Playbook Fields](02_infrastructure/iac/ansible_playbook_fields.md)    | 필드 레퍼런스               |
| [Ansible Linux](02_infrastructure/iac/ansible_playbook_linux.md)               | Linux 플레이북              |
| [Ansible Windows](02_infrastructure/iac/ansible_playbook_windows.md)           | Windows 플레이북            |
| [Molecule](02_infrastructure/iac/molecule.md)                                  | 역할 테스트                 |
| [Terraform](02_infrastructure/iac/terraform.md)                                | HCL, State, Module          |
| [Pulumi](02_infrastructure/iac/pulumi.md)                                      | 일반 언어 IaC, 로컬 backend |
| [설정 관리 도구 비교](02_infrastructure/iac/config_management_comparison.md)   | Ansible·Chef·Puppet·Salt    |
| [Packer](02_infrastructure/iac/packer.md)                                      | 이미지 빌드                 |
| [Vagrant](02_infrastructure/iac/vagrant.md)                                    | 개발 환경 프로비저닝        |
| [YAML 문법](02_infrastructure/iac/yaml_syntax.md)                              | YAML 1.2 규칙               |

### Monitoring

| 문서                                                                                     | 설명                                  |
|------------------------------------------------------------------------------------------|---------------------------------------|
| [Prometheus + Grafana](02_infrastructure/monitoring/prometheus_grafana.md)               | PromQL, 대시보드                      |
| [Prometheus 설치](02_infrastructure/monitoring/prometheus_grafana_install.md)            | 설치, Node Exporter                   |
| [node_exporter 운영](02_infrastructure/monitoring/node_exporter_operations.md)           | collector, textfile, 알림             |
| [Zabbix](02_infrastructure/monitoring/zabbix.md)                                         | 8.0 LTS 설치, agent2, 알림            |
| [Zabbix vs Prometheus](02_infrastructure/monitoring/zabbix_vs_prometheus.md)             | 아키텍처 비교                         |
| [모니터링 SaaS 비교](02_infrastructure/monitoring/monitoring_saas_comparison.md)         | Datadog·New Relic·Dynatrace 비교      |
| [OpenTelemetry](02_infrastructure/monitoring/opentelemetry.md)                           | Collector, Python 계측, tail sampling |
| [Jaeger](02_infrastructure/monitoring/jaeger.md)                                         | v2 트레이스 저장, Badger, v3 API      |
| [리소스 모니터링](02_infrastructure/monitoring/resource_utilization_monitoring.md)       | CPU/메모리/디스크                     |
| [게임 인프라 KPI](02_infrastructure/monitoring/game_infra_kpi_presentation.md)           | 운영 핵심 지표                        |
| [Grafana Heatmap](02_infrastructure/monitoring/grafana_gitlab_heatmap.md)                | GitLab 커밋 히트맵                    |
| [GRAID SupremeRAID 점검](02_infrastructure/monitoring/graid_supremeraid_server_check.md) | GPU RAID 점검 가이드                  |
| [gstack](02_infrastructure/monitoring/gstack.md)                                         | Claude Code용 skill 묶음              |

### Cloud (AWS)

| 문서                                                                                    | 설명                       |
|-----------------------------------------------------------------------------------------|----------------------------|
| [S3 버킷 생성 옵션](02_infrastructure/cloud_aws/s3_bucket_create_options.md)            | SSE, 버전관리, Object Lock |
| [S3 Gateway Endpoint](02_infrastructure/cloud_aws/s3_gateway_endpoint_cross_account.md) | 크로스 계정 S3 접근        |
| [S3 Object Lock](02_infrastructure/cloud_aws/s3_object_lock.md)                         | WORM, Compliance           |
| [S3 백업 팁](02_infrastructure/cloud_aws/s3_backup_tips.md)                             | 비용/성능/무결성           |
| [CloudWatch Agent·경보](02_infrastructure/cloud_aws/cloudwatch_agent_alarms.md)         | Agent 설정, 경보 평가      |
| [STS AssumeRole](02_infrastructure/cloud_aws/sts_assume_role.md)                        | 크로스 계정 역할 위임      |
| [클라우드 백업 비용 비교](02_infrastructure/cloud_aws/cloud_backup_cost_comparison.md)  | 백업 도구 리소스·비용 비교 |
| [VPC Peering](02_infrastructure/cloud_aws/vpc_peering_inter_region_guide.md)            | Inter-Region Peering       |
| [AWS Network Firewall](02_infrastructure/cloud_aws/aws_network_firewall.md)             | 관리형 방화벽              |

### Windows Server

| 문서                                                                                           | 설명                           |
|------------------------------------------------------------------------------------------------|--------------------------------|
| [Windows Server 에디션](02_infrastructure/windows_server/windows_server_editions_licensing.md) | 에디션/라이선스 비교           |
| [Windows Server 핵심 개념](02_infrastructure/windows_server/windows_server_key_concepts.md)    | AD, DNS, 역할 서비스           |
| [SCVMM 가이드](02_infrastructure/windows_server/scvmm_guide.md)                                | VM 중앙 관리 플랫폼            |
| [Hyper-V](02_infrastructure/windows_server/hyper_v.md)                                         | 설치, 가상 스위치, Linux VM    |
| [IIS](02_infrastructure/windows_server/iis.md)                                                 | 사이트, 애플리케이션 풀, HTTPS |

### Data Pipeline

| 문서                                                                         | 설명                          |
|------------------------------------------------------------------------------|-------------------------------|
| [Kafka](02_infrastructure/data_pipeline/kafka.md)                            | 분산 메시지 스트리밍          |
| [게임 로그 파이프라인](02_infrastructure/data_pipeline/game_log_pipeline.md) | 수집→저장→분석                |
| [로그 100GB](02_infrastructure/data_pipeline/log_aggregation_100gb.md)       | 중규모 로그 설계              |
| [로그 100TB](02_infrastructure/data_pipeline/log_aggregation_100tb.md)       | 대규모 로그 설계              |
| [Elastic Stack 로그 수집](02_infrastructure/data_pipeline/elastic_stack.md)  | Filebeat, ECS, ILM            |
| [Grafana Loki](02_infrastructure/data_pipeline/loki.md)                      | Alloy, LogQL, 보존            |
| [Graylog](02_infrastructure/data_pipeline/graylog.md)                        | Data Node, GELF, 보존         |
| [로깅 도구 비교](02_infrastructure/data_pipeline/logging_saas_comparison.md) | Splunk·Papertrail과 자체 운영 |

### Storage

| 문서                                                                                          | 설명                       |
|-----------------------------------------------------------------------------------------------|----------------------------|
| [스토리지 아키텍처](02_infrastructure/storage/storage_architecture.md)                        | 스토리지 계층·구성 설계    |
| [SSD 마모 분산과 fio 성능 검수](02_infrastructure/storage/ssd_wear_performance_validation.md) | 마모·쓰기량·시험 판정      |
| [Linux 파일시스템 비교](02_infrastructure/storage/linux_filesystem_comparison.md)             | ext4·XFS·Btrfs·ZFS         |
| [백업 도구 비교](02_infrastructure/storage/backup_tools_comparison.md)                        | 백업 솔루션·도구 비교      |
| [Restic 백업·복구](02_infrastructure/storage/restic_backup.md)                                | 암호화 증분 백업·복구      |
| [MinIO Object Storage](02_infrastructure/storage/minio_object_storage.md)                     | S3 호환 객체 스토리지      |
| [LVM 운영](02_infrastructure/storage/lvm_operations.md)                                       | PV·VG·LV, 확장·스냅샷·Thin |
| [mdadm 소프트웨어 RAID](02_infrastructure/storage/mdadm_software_raid.md)                     | 구성·디스크 교체·scrub     |

### Web Server

| 문서                                                                                 | 설명                              |
|--------------------------------------------------------------------------------------|-----------------------------------|
| [Nginx](02_infrastructure/web_server/nginx_install.md)                               | 가상 호스트, 리버스 프록시        |
| [Nginx GeoIP2 모듈](02_infrastructure/web_server/nginx_geoip2_install.md)            | GeoIP2 동적 모듈 빌드·설정        |
| [Apache](02_infrastructure/web_server/apache_install.md)                             | MPM, SSL                          |
| [Tomcat](02_infrastructure/web_server/tomcat.md)                                     | 판 고르기, WAR 배포, 운영 설정    |
| [Caddy](02_infrastructure/web_server/caddy.md)                                       | 자동 HTTPS, Caddyfile             |
| [Varnish](02_infrastructure/web_server/varnish.md)                                   | HTTP 캐시, VCL, 적중 확인         |
| [Squid](02_infrastructure/web_server/squid.md)                                       | 전달 프록시, 접근 제어            |
| [리버스 프록시 개념](02_infrastructure/web_server/reverse_proxy.md)                  | 역할, Forwarded 헤더, 도구 비교   |
| [HAProxy](02_infrastructure/web_server/haproxy_install.md)                           | L4/L7 LB, SSL 터미네이션          |
| [HAProxy 핵심 개념](02_infrastructure/web_server/haproxy_concepts.md)                | 구조, 분산, 헬스체크, reload      |
| [HAProxy 운영 가이드](02_infrastructure/web_server/haproxy_operations_guide.md)      | 변경 절차, Runtime API, 장애 확인 |
| [HAProxy + Keepalived 이중화](02_infrastructure/web_server/haproxy_keepalived_ha.md) | VRRP VIP 전환, peers 동기화       |
| [HAProxy ACME 자동 갱신](02_infrastructure/web_server/haproxy_acme_guide.md)         | 내장 ACME, 인증서 저장, 갱신 감시 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Engineering

시니어/아키텍트급 — SRE 프로세스, 전략, 조직 설계.

### Reliability

| 문서                                                                       | 설명                                   |
|----------------------------------------------------------------------------|----------------------------------------|
| [Incident Management](03_engineering/reliability/incident_management.md)   | 장애 등급, IC 역할, 에스컬레이션       |
| [SLO/Error Budget](03_engineering/reliability/slo_error_budget.md)         | SLI/SLO/SLA, Burn Rate Alert           |
| [On-Call Design](03_engineering/reliability/oncall_design.md)              | 로테이션, 25% 규칙, 런북               |
| [Postmortem Framework](03_engineering/reliability/postmortem_framework.md) | 5 Whys, Blameless, Action Items        |
| [Chaos Engineering](03_engineering/reliability/chaos_engineering.md)       | 가설 실험, 폭발 반경, Game Day         |
| [Toil 관리](03_engineering/reliability/toil_reduction.md)                  | Toil 판별·측정·자동화 우선순위         |
| [Resilience Patterns](03_engineering/reliability/resilience_patterns.md)   | Timeout, Retry Budget, Circuit Breaker |

### Delivery

| 문서                                                                              | 설명                             |
|-----------------------------------------------------------------------------------|----------------------------------|
| [Change Management](03_engineering/delivery/change_management.md)                 | 변경 등급, CAB, 배포 윈도우      |
| [Zero Downtime Migration](03_engineering/delivery/zero_downtime_migration.md)     | Expand-Contract, CDC, 롤백       |
| [Capacity Planning](03_engineering/delivery/capacity_planning.md)                 | 트래픽 예측, Headroom            |
| [Multi-Region Architecture](03_engineering/delivery/multi_region_architecture.md) | Active-Active, RPO/RTO           |
| [ADR 가이드](03_engineering/delivery/adr_guide.md)                                | 아키텍처 의사결정 기록           |
| [Progressive Delivery](03_engineering/delivery/progressive_delivery.md)           | Rolling, Blue-Green, Canary 분석 |
| [Feature Flag 관리](03_engineering/delivery/feature_flag_management.md)           | 플래그 분류, 수명 주기, 제거     |

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

- [AI Agent 샌드박스 개념](04_security/hardening/ai_agent_sandbox_concepts.md) — OS 권한·승인·실행기와 다층 안전장치 설계.

| 문서                                                                                  | 설명                          |
|---------------------------------------------------------------------------------------|-------------------------------|
| [Linux 서버 보안 강화](04_security/hardening/linux_hardening.md)                      | sysctl, auditd, umask         |
| [방화벽](04_security/hardening/firewall_iptables_nftables.md)                         | iptables/nftables             |
| [ufw·firewalld](04_security/hardening/ufw_firewalld.md)                               | 호스트 방화벽 관리 도구       |
| [메일 인증](04_security/hardening/email_authentication.md)                            | SPF·DKIM·DMARC, 그레이 리스트 |
| [SSH 보안](04_security/hardening/ssh_security.md)                                     | 키 인증, fail2ban             |
| [TLS/SSL](04_security/hardening/tls_ssl_guide.md)                                     | 인증서, Let's Encrypt, mTLS   |
| [시크릿 관리](04_security/hardening/secret_management.md)                             | Vault, AWS Secrets Manager    |
| [취약점 스캔](04_security/hardening/vulnerability_scanning.md)                        | nmap, trivy, lynis            |
| [Gitleaks 가이드](04_security/hardening/gitleaks_guide.md)                            | 민감정보 탐지, pre-commit     |
| [Trivy 가이드](04_security/hardening/trivy_guide.md)                                  | 이미지·IaC 스캔, CI 연동      |
| [TLS 인증서 만료 감시](04_security/hardening/tls_certificate_expiry_monitoring.md)    | 만료 감시, 갱신 점검          |
| [Lynis 서버 감사](04_security/hardening/lynis_audit_guide.md)                         | 서버 감사, 정기 점검·비교     |
| [AIDE 파일 무결성 감시](04_security/hardening/aide_file_integrity_monitoring.md)      | 기준 DB, 정기 점검, 변경 승인 |
| [auditd 규칙과 조회](04_security/hardening/auditd_rules_and_search_guide.md)          | 감사 규칙, ausearch, 보존     |
| [SELinux 거부 분석](04_security/hardening/selinux_troubleshooting_guide.md)           | AVC 해석, fcontext, 불리언    |
| [침해 의심 서버 초동 점검](04_security/hardening/linux_intrusion_triage_checklist.md) | 휘발성 수집, 지속 실행, 격리  |
| [Vault 설치](04_security/hardening/vault_install.md)                                  | HashiCorp Vault 설치·운영     |
| [Windows OpenSSH](04_security/hardening/windows_openssh_install.md)                   | Windows SSH 서버 설치         |
| [Windows 코드 서명](04_security/hardening/windows_code_signing_guide.md)              | 게임 배포, SmartScreen·UAC    |

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
| [CVE 분석](04_security/cve/)        | 커널·PHP CVE 7건  |
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
| [Server Config](05_database/operations/rdbms_server_config.md)           | my.cnf, 메모리별 템플릿 |
| [Slow Query](05_database/operations/rdbms_slow_query.md)                 | 슬로우 쿼리 분석        |
| [Tuning](05_database/operations/rdbms_tuning.md)                         | 버퍼풀, 캐시, I/O       |
| [Percona XtraBackup](05_database/operations/percona_xtrabackup_guide.md) | MySQL 물리 백업·복구    |
| [PostgreSQL 백업·PITR](05_database/operations/postgresql_backup_pitr.md) | pg_dump, WAL 아카이브   |
| [MySQL 논리 백업](05_database/operations/mysql_logical_backup.md)        | mysqldump, binlog PITR  |
| [PostgreSQL VACUUM](05_database/operations/postgresql_vacuum.md)         | autovacuum, 랩어라운드  |
| [PgBouncer](05_database/operations/pgbouncer_connection_pooling.md)      | 연결 풀링, 풀 모드      |

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

| 문서                                                                            | 설명                       |
|---------------------------------------------------------------------------------|----------------------------|
| [SE 로드맵](06_career/roadmap/se_roadmap.md)                                    | 시스템 엔지니어 경로       |
| [SRE 로드맵](06_career/roadmap/sre_roadmap.md)                                  | Site Reliability 경로      |
| [DBA 로드맵](06_career/roadmap/dba_roadmap.md)                                  | DBA 역할, 자격증           |
| [언어별 가이드](06_career/roadmap/se_complete_roadmap_programming_languages.md) | 언어 선택 기준             |
| [인프라 직무 비교](06_career/roadmap/infra_roles_comparison.md)                 | 직무·역할·기술 비교        |
| [SE 기술 면접 준비](06_career/roadmap/se_technical_interview_guide.md)          | 질문 유형, 답변 틀, 점검표 |

### Legal

| 문서                                                                              | 설명                             |
|-----------------------------------------------------------------------------------|----------------------------------|
| [DRM 가이드](06_career/legal/drm_guide.md)                                        | DRM, Tivoization, DMCA           |
| [업무 외 저작물](06_career/legal/ip_ownership_guide.md)                           | 저작권법 제9조, 귀속             |
| [리버스 엔지니어링 법적 기준](06_career/legal/reverse_engineering_legal_guide.md) | 역분석 요건, 보호조치, DMCA 예외 |
| [개인정보 보호 법령](06_career/legal/privacy_law_guide.md)                        | 법령, 감독기관                   |
| [개인정보 보호 개선 체크리스트](06_career/legal/privacy_improvement_checklist.md) | 관리·기술 보호조치 점검          |

### AI Tools

| 문서                                                                                     | 설명                                         |
|------------------------------------------------------------------------------------------|----------------------------------------------|
| [AI 개발 요청 템플릿](06_career/ai_tools/ai_development_request_template.md)             | AI 활용 요청 양식                            |
| [AI Markdown 패턴](06_career/ai_tools/ai_markdown_design_patterns.md)                    | 에이전트용 문서 패턴                         |
| [MCP 프로토콜 가이드](06_career/ai_tools/mcp_protocol_guide.md)                          | 구조, 전송, 인증, 보안 점검                  |
| [AI 작성 인프라 코드 검토](06_career/ai_tools/ai_generated_infra_code_review.md)         | 오류 유형, 자동 검사, 검토 점검표            |
| [AI 코딩 도구 비교](06_career/ai_tools/ai_coding_tools_comparison.md)                    | Kiro·Claude Code·Codex·Cursor·Copilot 비교   |
| [AI 에이전트 운영 도구](06_career/ai_tools/ai_agent_workspace_tools.md)                  | herdr·omp·Orca 등 실행·병렬·관리 도구        |
| [AI 시대 다섯 업무 원형](06_career/ai_tools/ai_work_archetypes.md)                       | Boris Cherny의 역할 구분과 팀 구성           |
| [Aside AI 브라우저](06_career/ai_tools/aside_browser_guide.md)                           | 기능·플랫폼·요금·권한·CLI·MCP                |
| [Harness Engineering](06_career/ai_tools/harness_engineering.md)                         | 에이전트 환경·검증·상태 전달·참고 구현       |
| [Loop Engineering](06_career/ai_tools/loop_engineering.md)                               | 목표·피드백·정지 조건·참고 실행기            |
| [Claude Code 공통 개념](06_career/ai_tools/claude/claude_code_concepts.md)               | 구성 요소, 사용 환경, 권한 모드, 계정과 비용 |
| [Claude Code CLI Linux 가이드](06_career/ai_tools/claude/claude_code_cli_linux_guide.md) | 설치, 인증, 권한 규칙, 비대화형·CI           |
| [Claude Code 기본 사용법](06_career/ai_tools/claude/claude_code_basics_guide.md)         | plan 모드, 컨텍스트 관리, 되돌리기           |
| [Claude Code 데스크톱 앱](06_career/ai_tools/claude/claude_code_desktop_guide.md)        | Code 탭, SSH 세션, 사이드바 정리             |
| [Claude Code의 Projects](06_career/ai_tools/claude/claude_code_projects.md)              | 스레드 조정, 공통 문맥, 사용량, 제한         |
| [Claude Code의 Code Mode](06_career/ai_tools/claude/claude_code_mode.md)                 | 도구 호출을 코드로 묶는 실험 기능, 이름 구분 |
| [Claude Code 확장 기능](06_career/ai_tools/claude/claude_code_extensions_guide.md)       | CLAUDE.md, 설정, Skills, Hooks, MCP          |
| [Claude Code 설정 파일](06_career/ai_tools/claude/claude_code_settings_guide.md)         | 설정 층, 우선순위, 권한 규칙, hook 실패 동작 |
| [Claude 모델 가이드](06_career/ai_tools/claude/claude_models_guide.md)                   | 라인업, 가격, 작업별 선택, 폐기 일정         |
| [Claude 스킬 목록](06_career/ai_tools/claude/claude_skills_catalog.md)                   | 개인 스킬 14개·한 줄 설명·우선순위           |
| [Codex 공통 개념](06_career/ai_tools/codex/codex_concepts.md)                            | 동작 원리, 수정 예시, 설정과 권한            |
| [Codex CLI Linux 가이드](06_career/ai_tools/codex/codex_cli_linux_guide.md)              | TUI, 로컬 작업, 비대화형 실행                |
| [Codex Skills 설정 가이드](06_career/ai_tools/codex/codex_skills_setup_guide.md)         | skill 작성·설치·호출·비활성화, 참고 URL      |
| [Codex 스킬 목록](06_career/ai_tools/codex/codex_skills_catalog.md)                      | 세션 제공 스킬 31개·한 줄 설명·호출 예시     |
| [ASD-STE100과 Codex 소통](06_career/ai_tools/codex/asd_ste100_codex_communication.md)    | 공식 표준·GitHub 후보·한국어 사용 방안       |
| [Codex GUI 가이드](06_career/ai_tools/codex/codex_gui_guide.md)                          | ChatGPT 웹·데스크톱 작업 관리                |
| [Codex IDE 가이드](06_career/ai_tools/codex/codex_ide_guide.md)                          | 편집기 context 기반 수정·리뷰                |
| [Codex API·자동화 가이드](06_career/ai_tools/codex/codex_api_guide.md)                   | SDK, app-server, CI 자동화                   |
| [Kiro CLI 레퍼런스](06_career/ai_tools/kiro/kiro_cli_command_reference.md)               | 명령어 전체 정리                             |
| [Kiro 모델 가이드](06_career/ai_tools/kiro/kiro_model_guide.md)                          | 모델 선택 기준                               |
| [Kiro 설정 가이드](06_career/ai_tools/kiro/kiro_setup_guide.md)                          | CLI 초기 설정                                |
| [Kiro Agent Lock](06_career/ai_tools/kiro/kiro_agent_lock.md)                            | 동시 실행 방지                               |
| [Jev 개념](06_career/ai_tools/jev/jev_concepts.md)                                       | 구조화된 판단, 질문 유형, 확률·신뢰도        |
| [Jev 사용 가이드](06_career/ai_tools/jev/jev_guide.md)                                   | Playground, HTTP API, Python SDK             |

[⬆ 목차로 돌아가기](#목차)

---

## 7. AI Transformation

AX(AI 전환) 환경 구축 참고 자료. 도구와 무관한 환경 구축 방법을 다루며, 특정 도구 사용법은 [6. Career](#6-career)의 AI Tools에 있습니다.

| 문서                                                                                | 설명                                       |
|-------------------------------------------------------------------------------------|--------------------------------------------|
| [AI Transformation 안내](07_ai_transformation/README.md)                            | 나누는 기준과 문서 목록                    |
| [에이전트 설계 원칙](07_ai_transformation/agent_design_principles.md)               | 작업 형태 선택, 지침 수준, 문맥 예산, 도구 |
| [에이전트 보안 위협 점검](07_ai_transformation/agent_security_risks.md)             | OWASP 에이전트 위협 10개와 AX 환경 점검    |
| [에이전트 평가 설계](07_ai_transformation/agent_evaluation_design.md)               | 과제·채점기·pass^k·회귀 평가               |
| [MCP 서버 도입·운영 점검](07_ai_transformation/mcp_server_adoption_checklist.md)    | 전송·권한·도구 안전 점검                   |
| [에이전트 실행 관측과 감사 기록](07_ai_transformation/agent_observability_audit.md) | OpenTelemetry GenAI 규약, 감사 기록        |

[⬆ 목차로 돌아가기](#목차)

---

## 8. Art

3D·그래픽 제작 도구의 설치·조작·제작 흐름. 도구별 폴더로 나눕니다.

| 문서                                                                     | 설명                                        |
|--------------------------------------------------------------------------|---------------------------------------------|
| [Art 안내](08_art/README.md)                                             | 나누는 기준과 문서 목록                     |
| [Blender 설치](08_art/blender/blender_install.md)                        | 판 고르기(LTS·최신), OS별 설치, 설정 폴더   |
| [Blender 화면 구성](08_art/blender/blender_interface.md)                 | 작업 공간, 편집기, 모드, 시점               |
| [Blender 단축키](08_art/blender/blender_shortcuts.md)                    | 초기 설정 기준 상황별 단축키                |
| [Blender 모델링 기초](08_art/blender/blender_modeling.md)                | 메시 구조, Edit 모드 도구, 토폴로지         |
| [Blender 모디파이어](08_art/blender/blender_modifiers.md)                | 스택 순서, 자주 쓰는 6종, 적용 시점         |
| [Blender 재질과 셰이딩](08_art/blender/blender_materials_shading.md)     | Principled BSDF, 텍스처, 색 공간            |
| [Blender UV와 텍스처링](08_art/blender/blender_uv_texturing.md)          | 심, 펼치기, 텍스처 페인팅, 베이크           |
| [Blender 조명과 렌더](08_art/blender/blender_lighting_rendering.md)      | 조명, 카메라, EEVEE·Cycles, 출력            |
| [Blender 스컬프팅](08_art/blender/blender_sculpting.md)                  | 브러시, 복셀 리메시, Multires, 마스크       |
| [Blender 애니메이션과 리깅](08_art/blender/blender_animation_rigging.md) | 키프레임, 그래프 편집기, 뼈대, 스키닝       |
| [Blender 지오메트리 노드](08_art/blender/blender_geometry_nodes.md)      | 필드, 인스턴스, 모디파이어 입력, 존         |
| [Blender 파일 형식](08_art/blender/blender_file_formats.md)              | glTF·FBX·OBJ·USD 내보내기, 왕복 시험        |
| [Blender Python 스크립트](08_art/blender/blender_python_scripting.md)    | bpy 구조, 데이터 API, 문맥, 연산자 등록     |
| [Blender 명령줄과 일괄 렌더](08_art/blender/blender_cli_batch_render.md) | 인수 순서, 프레임 지정, 나눠 렌더, 컨테이너 |
| [Blender 애드온](08_art/blender/blender_addons.md)                       | 확장 manifest, 빌드·설치, 켜기 범위         |
| [Blender 트러블슈팅](08_art/blender/blender_troubleshooting.md)          | 진단 순서, 충돌 로그, 복구, 자동 실행       |

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

| 문서                                                                                                               | 설명                                                                              |
|--------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| [라이선스 가이드](license_guide.md)                                                                                | MIT/Apache/GPL/CC 라이선스 비교, 선택 가이드                                      |
| [유사 레포 비교](97_misc/similar_repos.md)                                                                         | 벤치마킹, 차별화 전략                                                             |
| [모바일 게임 사전 오픈 부하 테스트](03_engineering/delivery/game_service_testing/mobile_game_load_testing_plan.md) | Node.js·C#·Unity 기반 게임 서비스 부하 테스트 계획                                |
| [모바일 게임 기기 테스트 솔루션](97_misc/mobile_game_device_testing_solutions.md)                                  | DeviceFarmer·Appium·Maestro·AWS Device Farm·Firebase Test Lab 비교                |
| [Android ADB 트러블슈팅](97_misc/android_adb_troubleshooting.md)                                                   | 앱 강제 종료·크래시 원인을 ADB 로그로 분석                                        |
| [게임 서버 아키텍처 유형](97_misc/game_server_architecture.md)                                                     | 게임 서비스의 서버 운영 방식 분류                                                 |
| [Kiro 라이선스·비용](97_misc/kiro_license_guide.md)                                                                | Kiro 요금제와 비용 가이드                                                         |
| [IT 레퍼런스 블로그](06_career/it_reference_blogs.md)                                                              | IT 기술 블로그·학습 사이트 모음                                                   |
| [엔지니어 기술 문서 작성](06_career/technical_writing_for_engineers.md)                                            | 런북·작업 계획서·README 작성 규칙                                                 |
| [파닉스 영어 학습법](97_misc/phonics_english.md)                                                                   | 영어 파닉스 학습법(기술 외 개인 자료)                                             |
| [Windows 인시던트 로그 수집](96_scripts/windows/collect_incident_logs.py)                                          | 장애 시 로그 자동 수집 스크립트                                                   |
| [Windows Hosts 관리](96_scripts/windows/win_hosts_manager.py)                                                      | hosts 파일 관리 도구                                                              |
| [공식 참고 문서 인덱스](_reference/INDEX.md)                                                                       | 기술별 공식 문서와 확인일 관리                                                    |
| [31 governances Repository Governance](https://github.com/siasia86/31_governances)                                 | 공통 repository·infrastructure·security policy·작업 템플릿 (2026-08-31 이관 완료) |
| [35 agent-skill](https://github.com/siasia86/35_agent-skill)                                                       | Kiro·Claude agent skill 공개 미러 (2026-08-31 이관 완료)                          |

### 문서 검증

문서 수정 후 다음 검사를 실행합니다.

```bash
sia-md-link-check README.md
sia-md-heading-check README.md
sia-md-style-check README.md
sia-readme-inventory-check README.md
```

- 내부 링크 검사: `sia-md-link-check`.
- 헤딩 구조·목차 앵커 검사: `sia-md-heading-check`.
- 표·푸터·문체 검사: `sia-md-style-check`.
- README에 표기된 문서 수와 실제 파일 수 검사: `sia-readme-inventory-check`.

---

## 참고 자료

- roadmap.sh: [roadmap.sh](https://roadmap.sh/) — ★★☆☆☆
- Linux Documentation Project: [tldp.org](https://tldp.org/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)


<!-- P31-GOVERNANCE-ENTRY BEGIN -->
저장소 관리 문서와 실제 상태 위치는 [.governance 진입](.governance/README.md)에서 확인합니다. 기존 업무 자료·기록은 원래 위치를 유지합니다.
<!-- P31-GOVERNANCE-ENTRY END -->

---

**작성일**: 2026-03-11

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
