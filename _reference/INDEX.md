---
name: reference-index
description: _reference 디렉토리 인덱스. 기술별 공식 문서 참조 노트 위치와 버전 현황.
tags:
  - index
  - reference
  - directory
last_checked: 2026-07-08
sources:
  - self (이 파일이 인덱스 역할)
---

# _reference INDEX

문서 작성/검토 시 해당 기술의 참조 파일을 읽어 공식 권장사항을 확인합니다.

| 기술                 | 파일                                                | 최신 버전                          | 확인일     |
|----------------------|-----------------------------------------------------|------------------------------------|------------|
| Ansible              | `_reference/ansible_official_notes.md`              | 14.1.0 (core 2.21.1)               | 2026-07-03 |
| ArgoCD               | `_reference/argocd_official_notes.md`               | v3.4.4                             | 2026-07-03 |
| Chaos/FinOps         | `_reference/chaos_finops_official_notes.md`         | principlesofchaos.org / finops.org | 2026-07-07 |
| Charset/Encoding     | `_reference/charset_encoding_official_notes.md`     | RFC 3629, Unicode 16.0             | 2026-07-07 |
| CVE/Security         | `_reference/cve_security_official_notes.md`         | NVD API 2.0, CISA KEV              | 2026-06-29 |
| Docker               | `_reference/docker_official_notes.md`               | Engine 29.6.1, Compose v5.3.0      | 2026-07-03 |
| GitHub References    | `_reference/github_references.md`                   | -                                  | 2026-06-18 |
| Grafana              | `_reference/grafana_official_notes.md`              | v13.1.0                            | 2026-07-03 |
| Helm                 | `_reference/helm_official_notes.md`                 | v4.2.2                             | 2026-07-03 |
| ISMS-P               | `_reference/isms_p_official_notes.md`               | KISA 인증기준 안내서 2023          | 2026-07-08 |
| Kubernetes           | `_reference/kubernetes_official_notes.md`           | v1.36.2                            | 2026-07-03 |
| Linux Kernel         | `_reference/linux_kernel_official_notes.md`         | namespace, cgroup, scheduler       | 2026-07-03 |
| MySQL                | `_reference/mysql_official_notes.md`                | 8.4.10 LTS, 9.7.1 Innovation       | 2026-07-10 |
| Networking           | `_reference/networking_official_notes.md`           | BGP, DDoS, CDN, VPC                | 2026-07-03 |
| Platform Engineering | `_reference/platform_engineering_official_notes.md` | CNCF Platforms WP                  | 2026-07-07 |
| PostgreSQL           | `_reference/postgresql_official_notes.md`           | 18.4 (EOL 2030-11)                 | 2026-07-07 |
| Prometheus           | `_reference/prometheus_official_notes.md`           | v3.13.0                            | 2026-07-03 |
| Protocol Error Codes | `_reference/protocol_error_codes_official_notes.md` | RFC 9110 / RFC 5321 / RFC 959      | 2026-05-26 |
| SRE Operations       | `_reference/sre_operations_official_notes.md`       | Google SRE Book / ITIL v4          | 2026-07-07 |
| Terraform            | `_reference/terraform_official_notes.md`            | v1.15.7, AWS Provider v6.46.0      | 2026-07-03 |
| VPN Protocol         | `_reference/vpn_protocol_official_notes.md`         | RFC 7296 / WireGuard 1.0           | 2026-06-29 |
| Web Server           | `_reference/web_server_official_notes.md`           | Nginx 1.30.3, Apache 2.4.68        | 2026-07-08 |
| YAML Spec            | `_reference/yaml_spec_notes.md`                     | 1.2 (1.1 호환)                     | 2026-05-26 |
| Zabbix               | `_reference/zabbix_official_notes.md`               | 7.4.11 (LTS: 7.0)                  | 2026-07-03 |

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
