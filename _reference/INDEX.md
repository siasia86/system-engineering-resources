---
name: reference-index
description: _reference 디렉토리 인덱스. 기술별 공식 문서 참조 노트 위치와 버전 현황. 상세 내용은 각 파일을 직접 읽을 것.
---

# _reference INDEX

문서 작성/검토 시 해당 기술의 참조 파일을 읽어 공식 권장사항을 확인합니다.

| 기술                 | 파일                                                | 최신 버전                     | 확인일     |
|----------------------|-----------------------------------------------------|-------------------------------|------------|
| Ansible              | `_reference/ansible_official_notes.md`              | 13.7.0 (core 2.21.0)          | 2026-05-26 |
| ArgoCD               | `_reference/argocd_official_notes.md`               | v3.4.2                        | 2026-05-26 |
| Docker               | `_reference/docker_official_notes.md`               | Engine 29.5.2, Compose v5.1.4 | 2026-05-22 |
| Grafana              | `_reference/grafana_official_notes.md`              | v13.0.1                       | 2026-05-26 |
| Helm                 | `_reference/helm_official_notes.md`                 | v4.2.0                        | 2026-05-26 |
| Kubernetes           | `_reference/kubernetes_official_notes.md`           | v1.36.1                       | 2026-05-26 |
| Protocol Error Codes | `_reference/protocol_error_codes_official_notes.md` | RFC 9110 / RFC 5321 / RFC 959 | 2026-05-26 |
| Prometheus           | `_reference/prometheus_official_notes.md`           | v3.11.3                       | 2026-05-26 |
| Terraform            | `_reference/terraform_official_notes.md`            | v1.15.4, AWS Provider v6.46.0 | 2026-05-22 |
| Zabbix               | `_reference/zabbix_official_notes.md`               | 7.4 (LTS: 7.0)                | 2026-05-22 |
| YAML Spec            | `_reference/yaml_spec_notes.md`                     | 1.2 (1.1 호환)                | 2026-05-26 |
| GitHub References    | `_reference/github_references.md`                   | -                             | 2026-06-18 |

## 사용 규칙

- `.md` 파일 작성/수정 전 해당 기술의 참조 파일 존재 여부 확인
- 없으면 공식 홈페이지 스캔 후 생성 (`lynx -dump` 또는 GitHub/PyPI API)
- 있으면 `last_checked` 날짜 확인 — 6개월 이상 경과 시 재확인 권장
- 파일 경로: `/root/32_system-engineering-resources/_reference/{기술명}_official_notes.md`
