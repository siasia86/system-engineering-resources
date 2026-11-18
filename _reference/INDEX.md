---
name: reference-index
description: _reference 디렉토리 인덱스. 기술별 공식 문서 참조 노트 위치와 버전 현황.
tags:
  - index
  - reference
  - directory
last_checked: 2026-11-16
sources:
  - self (이 파일이 인덱스 역할)
---

# _reference INDEX

문서 작성/검토 시 해당 기술의 참조 파일을 읽어 공식 권장사항을 확인합니다.

## 공통 reference note 정책

하나의 `_reference` 노트는 같은 기술·도메인을 다루는 여러 `.md` 문서에서 공통으로 참조합니다. 문서마다 동일한 공식 내용을 중복하여 별도 reference 파일로 만들지 않습니다.

- `_reference/INDEX.md`에는 공통 reference 노트를 한 번만 등록합니다.
- 각 본문 문서는 H1 바로 아래 `reference` HTML 주석으로 사용하는 공통 노트를 표시합니다.
- 한 문서가 여러 기술 영역을 다루면 여러 reference 파일을 함께 표시합니다.
- 공통 reference 노트의 사실 검증은 2회, 해당 노트를 참조하는 본문 문서 검증은 문서 규칙에 따라 별도로 수행합니다.
- 인덱스용 `README.md`는 기술 주장이 없으면 `N/A (문서 목록용 README)`로 기록하고 reference 생성을 생략합니다.

| 기술                           | 파일                                                    | 최신 버전                                               | 확인일     |
|--------------------------------|---------------------------------------------------------|---------------------------------------------------------|------------|
| POSIX ACL / setfacl            | `_reference/acl_setfacl_official_notes.md`              | acl 2.4.0·setfacl·getfacl·Default ACL·mask              | 2026-11-16 |
| Ansible                        | `_reference/ansible_official_notes.md`                  | 14.6.0 (core 2.21.6)                                    | 2026-11-16 |
| API Styles                     | `_reference/api_styles_official_notes.md`               | REST·GraphQL·gRPC·SOAP·WebSocket·Webhook·JSON-RPC·SSE   | 2026-08-21 |
| GraphQL                        | `_reference/graphql_official_notes.md`                  | September2025, GraphQL over HTTP draft                  | 2026-09-14 |
| gRPC                           | `_reference/grpc_official_notes.md`                     | v1.85.1, HTTP/2 RPC·streaming·deadline·status·TLS       | 2026-11-09 |
| Protobuf                       | `_reference/protobuf_official_notes.md`                 | v36.2, Editions·schema·wire format·호환성               | 2026-11-09 |
| REST API                       | `_reference/rest_api_official_notes.md`                 | RFC 9110·9457·5789, OpenAPI 3.2.1                       | 2026-11-09 |
| AWS STS/IAM/S3/KMS             | `_reference/aws_sts_iam_s3_kms_official_notes.md`       | AssumeRole, session, cross-account 권한                 | 2026-08-13 |
| AWS Secrets Manager            | `_reference/aws_secrets_manager_official_notes.md`      | Secret lifecycle·Rotation·IAM                           | 2026-08-19 |
| ArgoCD                         | `_reference/argocd_official_notes.md`                   | v3.6.1                                                  | 2026-11-16 |
| Chaos/FinOps                   | `_reference/chaos_finops_official_notes.md`             | principlesofchaos.org / finops.org                      | 2026-11-16 |
| CPU 시스템 운영                | `_reference/cpu_system_engineering_official_notes.md`   | NUMA·스케줄링·가상화·CPU 호환성                         | 2026-08-21 |
| Charset/Encoding               | `_reference/charset_encoding_official_notes.md`         | RFC 3629, Unicode 18.0                                  | 2026-11-09 |
| Claude Code                    | `_reference/claude_code_official_notes.md`              | v2.1.325·모델 5.5/Fable 5.1·권한·설정·확장·headless·앱  | 2026-11-16 |
| Codex CLI                      | `_reference/codex_cli_official_notes.md`                | Skills 설정·plugin; v0.167.0 (로컬 도움말 v0.164.0)     | 2026-11-09 |
| 에이전트 지침 파일             | `_reference/agent_instruction_files_official_notes.md`  | AGENTS.md·Codex·Claude Code 비교, 버전 표기 없음        | 2026-11-13 |
| Agent Skills 규격              | `_reference/agent_skills_spec_official_notes.md`        | SKILL.md 필드·폴더·단계적 로딩, 버전 표기 없음          | 2026-11-13 |
| Jev                            | `_reference/jev_official_notes.md`                      | jev-1.14.0·Choice·Score·HTTP·Python SDK                 | 2026-11-16 |
| CVE/Security                   | `_reference/cve_security_official_notes.md`             | NVD API 2.0, CISA KEV                                   | 2026-11-09 |
| Docker                         | `_reference/docker_official_notes.md`                   | Engine 29.9.3, Compose v5.7.1                           | 2026-11-16 |
| Epsilon-Delta (Math)           | `_reference/epsilon_delta_math_notes.md`                | Rudin Ch.4, Weierstrass                                 | 2026-11-16 |
| GitHub References              | `_reference/github_references.md`                       | Codex Skills·Harness/Loop·개발 절차·명세·탐색 목록      | 2026-10-03 |
| HashiCorp Vault                | `_reference/hashicorp_vault_official_notes.md`          | KV·Database Dynamic Secret·라이선스                     | 2026-08-20 |
| GitLab CI/CD Variables         | `_reference/gitlab_ci_variables_official_notes.md`      | Protected·Masked·File·AWS OIDC                          | 2026-08-19 |
| Gitleaks                       | `_reference/gitleaks_official_notes.md`                 | v8.30.1                                                 | 2026-11-09 |
| Trivy                          | `_reference/trivy_official_notes.md`                    | v0.76.2·GHSA-69fq 공급망 사고·action v0.36.0            | 2026-11-10 |
| TLS 인증서 수명 주기           | `_reference/tls_cert_lifecycle_official_notes.md`       | BR v2.3.1·LE 45일·RFC 9773·blackbox v0.29.1             | 2026-11-09 |
| Lynis                          | `_reference/lynis_official_notes.md`                    | 3.1.7·GPG 서명·프로필·보고서 형식·Hardening index       | 2026-11-05 |
| Grafana                        | `_reference/grafana_official_notes.md`                  | v13.3.0                                                 | 2026-11-05 |
| Helm                           | `_reference/helm_official_notes.md`                     | v4.3.2                                                  | 2026-11-16 |
| ISMS-P                         | `_reference/isms_p_official_notes.md`                   | 고시 제2024-30호, isms-p.or.kr                          | 2026-11-09 |
| Kubernetes                     | `_reference/kubernetes_official_notes.md`               | v1.37.2                                                 | 2026-11-16 |
| Linux Kernel                   | `_reference/linux_kernel_official_notes.md`             | namespace, cgroup, scheduler                            | 2026-07-03 |
| Time Complexity / Algorithms   | `_reference/time_complexity_official_notes.md`          | MIT OCW 6.006·Python 3.14.7, asymptotic·cost model      | 2026-09-14 |
| Merkle Tree / Git Objects      | `_reference/merkle_tree_official_notes.md`              | RFC 9162·Git 2.55.0, inclusion proof·Merkle DAG         | 2026-09-14 |
| Mobile Device Testing          | `_reference/mobile_device_testing_official_notes.md`    | DeviceFarmer·Appium·Maestro·AWS Device Farm·Test Lab    | 2026-11-09 |
| Software Testing               | `_reference/software_testing_official_notes.md`         | ISTQB CTFL v4.0·테스트 용어·설계·테스트 레벨            | 2026-09-15 |
| Advanced Testing               | `_reference/advanced_testing_official_notes.md`         | Hypothesis·PIT·Property-based·Mutation Testing          | 2026-09-15 |
| Game Testing                   | `_reference/game_testing_official_notes.md`             | Unity Test Framework·Firebase Game Loop                 | 2026-11-10 |
| Load Testing                   | `_reference/load_testing_official_notes.md`             | k6 테스트 유형·Google SRE Managing Load                 | 2026-09-15 |
| Web Testing                    | `_reference/web_testing_official_notes.md`              | RFC 9110·9111·nginx·HAProxy 3.2·Trace Context·OWASP     | 2026-11-09 |
| Lean                           | `_reference/lean_official_notes.md`                     | v4.35.0, theorem proving, Lake, Elan                    | 2026-11-09 |
| MySQL                          | `_reference/mysql_official_notes.md`                    | 8.4.13 LTS, 9.7.4 LTS                                   | 2026-11-16 |
| GRAID SupremeRAID              | `_reference/graid_supremeraid_official_notes.md`        | 1.5.0, 2.0.1 Update 262 (Linux)                         | 2026-11-16 |
| Networking                     | `_reference/networking_official_notes.md`               | BGP, DDoS, CDN, VPC                                     | 2026-11-09 |
| iperf3                         | `_reference/iperf3_official_notes.md`                   | 3.22, TCP·UDP·SCTP throughput                           | 2026-11-09 |
| OpenZFS                        | `_reference/openzfs_official_notes.md`                  | COW·checksum·Snapshot·RAIDZ·복제·압축·암호화            | 2026-09-21 |
| Platform Engineering           | `_reference/platform_engineering_official_notes.md`     | CNCF Platforms WP                                       | 2026-11-16 |
| PostgreSQL                     | `_reference/postgresql_official_notes.md`               | 18.7 (EOL 2030-11)                                      | 2026-11-16 |
| Prometheus                     | `_reference/prometheus_official_notes.md`               | v3.16.0 (LTS 3.13.5)                                    | 2026-11-09 |
| Protocol Error Codes           | `_reference/protocol_error_codes_official_notes.md`     | RFC 9110 / RFC 5321 / RFC 959                           | 2026-11-09 |
| Rsync                          | `_reference/rsync_official_notes.md`                    | 3.5.2, daemon·SSH·TLS·rrsync 보안                       | 2026-11-16 |
| Restic                         | `_reference/restic_official_notes.md`                   | v0.19.1, Snapshot·암호화·중복 제거·S3·무결성 검사       | 2026-11-09 |
| Backup Tools                   | `_reference/backup_tools_official_notes.md`             | rsnapshot·lsyncd·Bacula·Borg·Duplicity·Amanda·Bareos    | 2026-09-21 |
| SRE Operations                 | `_reference/sre_operations_official_notes.md`           | Google SRE Book / ITIL v4                               | 2026-11-16 |
| Terraform                      | `_reference/terraform_official_notes.md`                | v1.17.1, AWS Provider v6.72.0                           | 2026-11-09 |
| VPN Protocol                   | `_reference/vpn_protocol_official_notes.md`             | RFC 7296 / WireGuard protocol                           | 2026-11-10 |
| SoftEther VPN                  | `_reference/softether_official_notes.md`                | v4.44-9807-rtm (Stable), 5.2.5188 (개발)                | 2026-11-16 |
| Web Server                     | `_reference/web_server_official_notes.md`               | Nginx 1.30.6, Apache 2.4.70, HAProxy 3.4.7 LTS          | 2026-11-16 |
| YAML Spec                      | `_reference/yaml_spec_notes.md`                         | 1.2 (1.1 호환)                                          | 2026-11-09 |
| Zabbix                         | `_reference/zabbix_official_notes.md`                   | 8.0 LTS (2026-11-05), 7.4 Standard                      | 2026-11-09 |
| e4fsprogs (CentOS 5)           | `_reference/e4fsprogs_centos5_notes.md`                 | 1.41.12-4.el5_10, fsck.ext4                             | 2026-07-22 |
| Hyper-V I/O 경합               | `_reference/hyperv_io_contention_notes.md`              | Storage Stack·Storage QoS·성능 카운터                   | 2026-11-16 |
| Hyper-V I/O 경합 (CentOS 5)    | `_reference/hyperv_centos5_io_contention_notes.md`      | Storage QoS·LIS 지원 범위·CentOS 5.11                   | 2026-11-09 |
| Hyper-V 버전 비교              | `_reference/hyperv_version_comparison_notes.md`         | Windows Server 2008·2008 R2·2012, CentOS 5.x 호환       | 2026-11-16 |
| Android ADB                    | `_reference/android_adb_official_notes.md`              | platform-tools 37.0.1, logcat                           | 2026-11-16 |
| Windows Server 2022 Monitoring | `_reference/windows_server_2022_monitoring_notes.md`    | Get-Counter, 카운터, 임계치                             | 2026-11-16 |
| Linux Filesystem               | `_reference/linux_filesystem_official_notes.md`         | ext4, XFS, Btrfs, VFS                                   | 2026-11-09 |
| MinIO                          | `_reference/minio_official_notes.md`                    | AGPLv3·S3-compatible·Versioning·Object Lock·Replication | 2026-11-09 |
| Storage Tools                  | `_reference/storage_tools_official_notes.md`            | 15개 도구·공식 매뉴얼 범위                              | 2026-11-09 |
| AI 코딩 도구                   | `_reference/ai_coding_tools_official_notes.md`          | 가격·모델·벤치마크 (2026-11-18), Windsurf→Devin Desktop | 2026-11-18 |
| AI 에이전트 운영 도구          | `_reference/ai_agent_workspace_tools_official_notes.md` | herdr·omp·Orca·pi·OpenCode·cmux 등                      | 2026-10-27 |
| AI 업무 원형                   | `_reference/ai_work_archetypes_notes.md`                | Boris Cherny 제안·전재 대조·원문 직접 열람 제한         | 2026-11-09 |
| Aside AI 브라우저              | `_reference/aside_browser_official_notes.md`            | v1.0.1116.1·플랫폼·요금·권한·데이터 처리·CLI·MCP        | 2026-11-16 |
| ASD-STE100                     | `_reference/asd_ste100_official_notes.md`               | Issue 9 공식 설명·GitHub 5개·Codex 적용 근거            | 2026-10-09 |
| Rust                           | `_reference/rust_official_notes.md`                     | 1.100.0, Edition 2024, 주요 크레이트                    | 2026-11-18 |
| Windows Server 에디션/라이선스 | `_reference/windows_server_editions_licensing_notes.md` | Standard vs Datacenter, KMS/MAK/AVMA                    | 2026-11-16 |
| Windows Server Concepts        | `_reference/windows_server_concepts_notes.md`           | Hyper-V, S2D, Failover Cluster, Shielded VM, SDN        | 2026-11-09 |
| Windows 코드 서명              | `_reference/windows_code_signing_official_notes.md`     | Authenticode·SmartScreen·Artifact Signing·CSBR 3.11.0   | 2026-11-18 |
| SCVMM                          | `_reference/scvmm_official_notes.md`                    | System Center 2025, 호스트 관리·베어메탈·Arc            | 2026-11-09 |
| SVN (Subversion)               | `_reference/svn_official_notes.md`                      | 1.15.0                                                  | 2026-11-09 |
| Git                            | `_reference/git_official_notes.md`                      | 2.56.1                                                  | 2026-11-16 |
| eBPF / bpftrace                | `_reference/ebpf_bpftrace_official_notes.md`            | libbpf v1.8.0, bpftrace v0.27.1                         | 2026-11-09 |
| Linux Process / Memory / IPC   | `_reference/linux_process_official_notes.md`            | fork/exec/wait, mmap, OOM, pipe/shm/mq                  | 2026-11-09 |
| GDB                            | `_reference/gdb_official_notes.md`                      | 18.1, breakpoint/watchpoint/bt, ptrace attach           | 2026-11-09 |
| strace                         | `_reference/strace_official_notes.md`                   | v7.3, syscall/signal 추적, -e trace 필터                | 2026-11-16 |
| ltrace                         | `_reference/ltrace_official_notes.md`                   | 0.8.1, 동적 라이브러리 함수 추적                        | 2026-11-09 |
| Valgrind                       | `_reference/valgrind_official_notes.md`                 | 3.28.0, Memcheck/Callgrind/Helgrind/Massif              | 2026-11-16 |
| perf                           | `_reference/perf_official_notes.md`                     | stat/record/report/top/trace 서브커맨드                 | 2026-11-16 |
| lsof                           | `_reference/lsof_official_notes.md`                     | 4.99.7, FD/TYPE 필드, -i/-p/-u/-a 필터                  | 2026-08-01 |
| iotop                          | `_reference/iotop_official_notes.md`                    | v1.33, I/O 모니터링, --only/--batch/--processes         | 2026-11-09 |
| tcpdump                        | `_reference/tcpdump_official_notes.md`                  | 4.99.7, BPF 필터, -w pcap, -n/-nn/-X 옵션               | 2026-11-09 |
| Bash Shell                     | `_reference/bash_shell_official_notes.md`               | 5.3, interactive/non-interactive, 리다이렉션            | 2026-11-09 |
| Vim                            | `_reference/vim_official_notes.md`                      | 9.2, Normal/Insert/Visual/Command 모드                  | 2026-11-09 |
| C# / .NET                      | `_reference/csharp_official_notes.md`                   | .NET 11 STS/C# 15, .NET 10 LTS, async/await, NRT, CLI   | 2026-11-16 |


## 사용 규칙

- `.md` 파일 작성/수정 전 해당 기술의 참조 파일 존재 여부 확인
- 없으면 공식 홈페이지 스캔 후 생성 (`lynx -dump` 또는 GitHub/PyPI API)
- 있으면 `last_checked` 날짜 확인 — 6개월 이상 경과 시 재확인 권장
- 파일 경로: `_reference/{기술명}_official_notes.md`

## frontmatter 양식

```yaml
---
name: <kebab-case>
description: <한 줄 설명>
tags:
  - <keyword1>
  - <keyword2>
last_checked: YYYY-MM-DD
sources:
  - https://...
---
```

---

**작성일**: 2026-05-22

**마지막 업데이트**: 2026-11-18

© 2026 siasia86. Licensed under CC BY 4.0.
