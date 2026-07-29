---
name: reference-index
description: _reference 디렉토리 인덱스. 기술별 공식 문서 참조 노트 위치와 버전 현황.
tags:
  - index
  - reference
  - directory
last_checked: 2026-07-14
sources:
  - self (이 파일이 인덱스 역할)
---

# _reference INDEX

문서 작성/검토 시 해당 기술의 참조 파일을 읽어 공식 권장사항을 확인합니다.

| 기술                 | 파일                                                | 최신 버전                          | 확인일     | 참조 |
|----------------------|-----------------------------------------------------|------------------------------------|------------|------|
| Ansible              | `_reference/ansible_official_notes.md`              | 14.1.0 (core 2.21.1)               | 2026-07-03 | X    |
| ArgoCD               | `_reference/argocd_official_notes.md`               | v3.4.4                             | 2026-07-03 | O    |
| Chaos/FinOps         | `_reference/chaos_finops_official_notes.md`         | principlesofchaos.org / finops.org | 2026-07-07 | X    |
| Charset/Encoding     | `_reference/charset_encoding_official_notes.md`     | RFC 3629, Unicode 16.0             | 2026-07-07 | O    |
| CVE/Security         | `_reference/cve_security_official_notes.md`         | NVD API 2.0, CISA KEV              | 2026-06-29 | O    |
| Docker               | `_reference/docker_official_notes.md`               | Engine 29.6.1, Compose v5.3.0      | 2026-07-03 | O    |
| Epsilon-Delta (Math) | `_reference/epsilon_delta_math_notes.md`            | Rudin Ch.4, Weierstrass            | 2026-07-14 | O    |
| GitHub References    | `_reference/github_references.md`                   | -                                  | 2026-06-18 | O    |
| Grafana              | `_reference/grafana_official_notes.md`              | v13.1.0                            | 2026-07-03 | O    |
| Helm                 | `_reference/helm_official_notes.md`                 | v4.2.2                             | 2026-07-03 | O    |
| ISMS-P               | `_reference/isms_p_official_notes.md`               | KISA 인증기준 안내서 2023          | 2026-07-08 | X    |
| Kubernetes           | `_reference/kubernetes_official_notes.md`           | v1.36.2                            | 2026-07-03 | O    |
| Linux Kernel         | `_reference/linux_kernel_official_notes.md`         | namespace, cgroup, scheduler       | 2026-07-03 | O    |
| MySQL                | `_reference/mysql_official_notes.md`                | 8.4.10 LTS, 9.7.1 Innovation       | 2026-07-10 | O    |
| GRAID SupremeRAID    | `_reference/graid_supremeraid_official_notes.md`    | 1.5.0, 2.0.0 (Linux)               | 2026-07-10 | O    |
| Networking           | `_reference/networking_official_notes.md`           | BGP, DDoS, CDN, VPC                | 2026-07-03 | X    |
| Platform Engineering | `_reference/platform_engineering_official_notes.md` | CNCF Platforms WP                  | 2026-07-07 | X    |
| PostgreSQL           | `_reference/postgresql_official_notes.md`           | 18.4 (EOL 2030-11)                 | 2026-07-07 | X    |
| Prometheus           | `_reference/prometheus_official_notes.md`           | v3.13.0                            | 2026-07-03 | O    |
| Protocol Error Codes | `_reference/protocol_error_codes_official_notes.md` | RFC 9110 / RFC 5321 / RFC 959      | 2026-05-26 | O    |
| SRE Operations       | `_reference/sre_operations_official_notes.md`       | Google SRE Book / ITIL v4          | 2026-07-07 | X    |
| Terraform            | `_reference/terraform_official_notes.md`            | v1.15.7, AWS Provider v6.46.0      | 2026-07-03 | O    |
| VPN Protocol         | `_reference/vpn_protocol_official_notes.md`         | RFC 7296 / WireGuard 1.0           | 2026-06-29 | O    |
| Web Server           | `_reference/web_server_official_notes.md`           | Nginx 1.30.3, Apache 2.4.68        | 2026-07-08 | O    |
| YAML Spec            | `_reference/yaml_spec_notes.md`                     | 1.2 (1.1 호환)                     | 2026-05-26 | O    |
| Zabbix               | `_reference/zabbix_official_notes.md`               | 7.4.11 (LTS: 7.0)                  | 2026-07-03 | O    |
| e4fsprogs (CentOS 5)  | `_reference/e4fsprogs_centos5_notes.md`             | 1.41.12-4.el5_10, fsck.ext4    | 2026-07-22 | O    |
| Android ADB          | `_reference/android_adb_official_notes.md`          | platform-tools 37.0.1, logcat    | 2026-07-16 | O    |
| Windows Server 2022 Monitoring | `_reference/windows_server_2022_monitoring_notes.md` | Get-Counter, 카운터, 임계치 | 2026-07-23 | O    |
| Linux Filesystem     | `_reference/linux_filesystem_official_notes.md`     | ext4, XFS, Btrfs, VFS               | 2026-07-17 | O    |
| AI 코딩 도구         | `_reference/ai_coding_tools_official_notes.md`      | 가격·모델·벤치마크 (2026-07-27)     | 2026-07-27 | O    |
| Rust                 | `_reference/rust_official_notes.md`                 | 1.97.1, Edition 2021, 주요 크레이트 | 2026-07-29 | O    |


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
