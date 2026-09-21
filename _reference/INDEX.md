---
name: reference-index
description: _reference 디렉토리 인덱스. 기술별 공식 문서 참조 노트 위치와 버전 현황.
tags:
  - index
  - reference
  - directory
last_checked: 2026-09-15
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

| 기술                           | 파일                                                    | 최신 버전                                               | 확인일     | 참조 |
|--------------------------------|---------------------------------------------------------|---------------------------------------------------------|------------|------|
| POSIX ACL / setfacl            | `_reference/acl_setfacl_official_notes.md`              | acl 2.4.0·setfacl·getfacl·Default ACL·mask              | 2026-09-16 | O    |
| Ansible                        | `_reference/ansible_official_notes.md`                  | 14.1.0 (core 2.21.1)                                    | 2026-07-03 | X    |
| API Styles                     | `_reference/api_styles_official_notes.md`               | REST·GraphQL·gRPC·SOAP·WebSocket·Webhook·JSON-RPC·SSE   | 2026-08-21 | O    |
| GraphQL                        | `_reference/graphql_official_notes.md`                  | September2025, GraphQL over HTTP draft                  | 2026-09-14 | O    |
| gRPC                           | `_reference/grpc_official_notes.md`                     | v1.84.0, HTTP/2 RPC·streaming·deadline·status·TLS       | 2026-09-11 | O    |
| Protobuf                       | `_reference/protobuf_official_notes.md`                 | v36.1, Editions·schema·wire format·호환성               | 2026-09-11 | O    |
| REST API                       | `_reference/rest_api_official_notes.md`                 | RFC 9110·9457·5789, OpenAPI 3.2.0                       | 2026-09-11 | O    |
| AWS STS/IAM/S3/KMS             | `_reference/aws_sts_iam_s3_kms_official_notes.md`       | AssumeRole, session, cross-account 권한                 | 2026-08-13 | O    |
| AWS Secrets Manager            | `_reference/aws_secrets_manager_official_notes.md`      | Secret lifecycle·Rotation·IAM                           | 2026-08-19 | O    |
| ArgoCD                         | `_reference/argocd_official_notes.md`                   | v3.4.4                                                  | 2026-07-03 | O    |
| Chaos/FinOps                   | `_reference/chaos_finops_official_notes.md`             | principlesofchaos.org / finops.org                      | 2026-07-07 | X    |
| CPU 시스템 운영                | `_reference/cpu_system_engineering_official_notes.md`   | NUMA·스케줄링·가상화·CPU 호환성                         | 2026-08-21 | O    |
| Charset/Encoding               | `_reference/charset_encoding_official_notes.md`         | RFC 3629, Unicode 16.0                                  | 2026-07-07 | O    |
| Codex CLI                      | `_reference/codex_cli_official_notes.md`                | v0.154.0, Linux·install·auth·sandbox·exec               | 2026-09-14 | O    |
| CVE/Security                   | `_reference/cve_security_official_notes.md`             | NVD API 2.0, CISA KEV                                   | 2026-06-29 | O    |
| Docker                         | `_reference/docker_official_notes.md`                   | Engine 29.6.1, Compose v5.3.0                           | 2026-07-03 | O    |
| Epsilon-Delta (Math)           | `_reference/epsilon_delta_math_notes.md`                | Rudin Ch.4, Weierstrass                                 | 2026-07-14 | O    |
| GitHub References              | `_reference/github_references.md`                       | -                                                       | 2026-06-18 | O    |
| HashiCorp Vault                | `_reference/hashicorp_vault_official_notes.md`          | KV·Database Dynamic Secret·라이선스                     | 2026-08-19 | O    |
| GitLab CI/CD Variables         | `_reference/gitlab_ci_variables_official_notes.md`      | Protected·Masked·File·AWS OIDC                          | 2026-08-19 | O    |
| Gitleaks                       | `_reference/gitleaks_official_notes.md`                 | v8.30.1                                                 | 2026-08-19 | O    |
| Grafana                        | `_reference/grafana_official_notes.md`                  | v13.1.0                                                 | 2026-07-03 | O    |
| Helm                           | `_reference/helm_official_notes.md`                     | v4.2.2                                                  | 2026-07-03 | O    |
| ISMS-P                         | `_reference/isms_p_official_notes.md`                   | KISA 인증기준 안내서 2023                               | 2026-07-08 | X    |
| Kubernetes                     | `_reference/kubernetes_official_notes.md`               | v1.36.2                                                 | 2026-07-03 | O    |
| Linux Kernel                   | `_reference/linux_kernel_official_notes.md`             | namespace, cgroup, scheduler                            | 2026-07-03 | O    |
| Time Complexity / Algorithms   | `_reference/time_complexity_official_notes.md`          | MIT OCW 6.006·Python 3.14.7, asymptotic·cost model      | 2026-09-14 | O    |
| Merkle Tree / Git Objects      | `_reference/merkle_tree_official_notes.md`              | RFC 9162·Git 2.55.0, inclusion proof·Merkle DAG         | 2026-09-14 | O    |
| Mobile Device Testing          | `_reference/mobile_device_testing_official_notes.md`    | DeviceFarmer·Appium·Maestro·AWS Device Farm·Test Lab    | 2026-09-15 | O    |
| Software Testing               | `_reference/software_testing_official_notes.md`         | ISTQB CTFL v4.0·테스트 용어·설계·테스트 레벨            | 2026-09-15 | O    |
| Advanced Testing               | `_reference/advanced_testing_official_notes.md`         | Hypothesis·PIT·Property-based·Mutation Testing          | 2026-09-15 | O    |
| Game Testing                   | `_reference/game_testing_official_notes.md`             | Unity Test Framework·Firebase Game Loop                 | 2026-09-15 | O    |
| Load Testing                   | `_reference/load_testing_official_notes.md`             | k6 테스트 유형·Google SRE Managing Load                 | 2026-09-15 | O    |
| Lean                           | `_reference/lean_official_notes.md`                     | v4.33.1, theorem proving, Lake, Elan                    | 2026-09-11 | O    |
| MySQL                          | `_reference/mysql_official_notes.md`                    | 8.4.10 LTS, 9.7.1 Innovation                            | 2026-07-10 | O    |
| GRAID SupremeRAID              | `_reference/graid_supremeraid_official_notes.md`        | 1.5.0, 2.0.0 (Linux)                                    | 2026-07-10 | O    |
| Networking                     | `_reference/networking_official_notes.md`               | BGP, DDoS, CDN, VPC                                     | 2026-07-03 | X    |
| iperf3                         | `_reference/iperf3_official_notes.md`                   | 3.21, TCP·UDP·SCTP throughput                           | 2026-08-28 | O    |
| OpenZFS                        | `_reference/openzfs_official_notes.md`                  | COW·checksum·Snapshot·RAIDZ·복제·압축·암호화            | 2026-09-21 | O    |
| Platform Engineering           | `_reference/platform_engineering_official_notes.md`     | CNCF Platforms WP                                       | 2026-07-07 | X    |
| PostgreSQL                     | `_reference/postgresql_official_notes.md`               | 18.4 (EOL 2030-11)                                      | 2026-07-07 | X    |
| Prometheus                     | `_reference/prometheus_official_notes.md`               | v3.13.0                                                 | 2026-07-03 | O    |
| Protocol Error Codes           | `_reference/protocol_error_codes_official_notes.md`     | RFC 9110 / RFC 5321 / RFC 959                           | 2026-05-26 | O    |
| Rsync                          | `_reference/rsync_official_notes.md`                    | 3.5.0, daemon·SSH·TLS·rrsync 보안                       | 2026-09-14 | O    |
| Restic                         | `_reference/restic_official_notes.md`                   | v0.19.1, Snapshot·암호화·중복 제거·S3·무결성 검사       | 2026-09-21 | O    |
| Backup Tools                   | `_reference/backup_tools_official_notes.md`             | rsnapshot·lsyncd·Bacula·Borg·Duplicity·Amanda·Bareos    | 2026-09-21 | O    |
| SRE Operations                 | `_reference/sre_operations_official_notes.md`           | Google SRE Book / ITIL v4                               | 2026-07-07 | X    |
| Terraform                      | `_reference/terraform_official_notes.md`                | v1.15.7, AWS Provider v6.46.0                           | 2026-07-03 | O    |
| VPN Protocol                   | `_reference/vpn_protocol_official_notes.md`             | RFC 7296 / WireGuard protocol                           | 2026-08-10 | O    |
| Web Server                     | `_reference/web_server_official_notes.md`               | Nginx 1.30.3, Apache 2.4.68                             | 2026-08-20 | O    |
| YAML Spec                      | `_reference/yaml_spec_notes.md`                         | 1.2 (1.1 호환)                                          | 2026-05-26 | O    |
| Zabbix                         | `_reference/zabbix_official_notes.md`                   | 7.4.11 (LTS: 7.0)                                       | 2026-07-03 | O    |
| e4fsprogs (CentOS 5)           | `_reference/e4fsprogs_centos5_notes.md`                 | 1.41.12-4.el5_10, fsck.ext4                             | 2026-07-22 | O    |
| Android ADB                    | `_reference/android_adb_official_notes.md`              | platform-tools 37.0.1, logcat                           | 2026-07-16 | O    |
| Windows Server 2022 Monitoring | `_reference/windows_server_2022_monitoring_notes.md`    | Get-Counter, 카운터, 임계치                             | 2026-07-23 | O    |
| Linux Filesystem               | `_reference/linux_filesystem_official_notes.md`         | ext4, XFS, Btrfs, VFS                                   | 2026-07-17 | O    |
| MinIO                          | `_reference/minio_official_notes.md`                    | AGPLv3·S3-compatible·Versioning·Object Lock·Replication | 2026-09-21 | O    |
| Storage Tools                  | `_reference/storage_tools_official_notes.md`            | 15개 도구·공식 매뉴얼 범위                              | 2026-08-18 | O    |
| AI 코딩 도구                   | `_reference/ai_coding_tools_official_notes.md`          | 가격·모델·벤치마크 (2026-07-27)                         | 2026-07-27 | O    |
| Rust                           | `_reference/rust_official_notes.md`                     | 1.97.1, Edition 2021, 주요 크레이트                     | 2026-07-29 | O    |
| Windows Server 에디션/라이선스 | `_reference/windows_server_editions_licensing_notes.md` | Standard vs Datacenter, KMS/MAK/AVMA                    | 2026-07-29 | O    |
| Windows Server Concepts        | `_reference/windows_server_concepts_notes.md`           | Hyper-V, S2D, Failover Cluster, Shielded VM, SDN        | 2026-07-29 | O    |
| SCVMM                          | `_reference/scvmm_official_notes.md`                    | System Center 2025, 호스트 관리·베어메탈·Arc            | 2026-08-21 | O    |
| SVN (Subversion)               | `_reference/svn_official_notes.md`                      | 1.14.5 (LTS)                                            | 2026-07-29 | O    |
| Git                            | `_reference/git_official_notes.md`                      | 2.55.0                                                  | 2026-07-29 | O    |
| eBPF / bpftrace                | `_reference/ebpf_bpftrace_official_notes.md`            | libbpf v1.7.0, bpftrace v0.26.1                         | 2026-08-01 | O    |
| Linux Process / Memory / IPC   | `_reference/linux_process_official_notes.md`            | fork/exec/wait, mmap, OOM, pipe/shm/mq                  | 2026-08-01 | O    |
| GDB                            | `_reference/gdb_official_notes.md`                      | 17.2, breakpoint/watchpoint/bt, ptrace attach           | 2026-08-01 | O    |
| strace                         | `_reference/strace_official_notes.md`                   | v7.1, syscall/signal 추적, -e trace 필터                | 2026-08-01 | O    |
| ltrace                         | `_reference/ltrace_official_notes.md`                   | 0.8.1, 동적 라이브러리 함수 추적                        | 2026-08-01 | O    |
| Valgrind                       | `_reference/valgrind_official_notes.md`                 | 3.27.1, Memcheck/Callgrind/Helgrind/Massif              | 2026-08-01 | O    |
| perf                           | `_reference/perf_official_notes.md`                     | stat/record/report/top/trace 서브커맨드                 | 2026-08-01 | O    |
| lsof                           | `_reference/lsof_official_notes.md`                     | 4.99.7, FD/TYPE 필드, -i/-p/-u/-a 필터                  | 2026-08-01 | O    |
| iotop                          | `_reference/iotop_official_notes.md`                    | v1.31, I/O 모니터링, --only/--batch/--processes         | 2026-08-01 | O    |
| tcpdump                        | `_reference/tcpdump_official_notes.md`                  | 4.99.6, BPF 필터, -w pcap, -n/-nn/-X 옵션               | 2026-08-01 | O    |
| Bash Shell                     | `_reference/bash_shell_official_notes.md`               | 5.3, interactive/non-interactive, 리다이렉션            | 2026-08-01 | O    |
| Vim                            | `_reference/vim_official_notes.md`                      | 9.2, Normal/Insert/Visual/Command 모드                  | 2026-08-01 | O    |
| C# / .NET                      | `_reference/csharp_official_notes.md`                   | .NET 10 LTS/C# 14, async/await, NRT, dotnet CLI         | 2026-08-02 | O    |


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
