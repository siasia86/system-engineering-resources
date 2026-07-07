# Security

보안 강화와 취약점 관리. 서버 하드닝, 클라우드 보안, CVE 분석, 웹 취약점을 다룹니다.

## 구조

| 디렉토리                   | 설명                                                      | 문서 수 |
|----------------------------|-----------------------------------------------------------|---------|
| [hardening/](./hardening/) | 서버 강화 — iptables/nftables, SSH, 시크릿 관리, gitleaks | 9       |
| [cloud/](./cloud/)         | 클라우드 보안 — AWS Security, DDoS 방어, Network Firewall | 4       |
| [cve/](./cve/)             | CVE 분석 — 2026년 Linux 커널 취약점 (Dirty Frag, LPE 등)  | 7       |
| [web_cwe/](./web_cwe/)     | 웹 취약점 — CWE-022, CWE-078, CWE-200, CWE-434            | 4       |

## 주요 문서

- [linux_hardening.md](./hardening/linux_hardening.md) — CIS 벤치마크 기반 강화
- [ssh_security.md](./hardening/ssh_security.md) — SSH 키 관리, 2FA, 포트 변경
- [ddos_defense_architecture.md](./cloud/ddos_defense_architecture.md) — 다층 DDoS 방어 아키텍처
- [secret_management.md](./hardening/secret_management.md) — Vault, SOPS, AWS SSM 비교
- [cve_2026_43284_dirty_frag.md](./cve/cve_2026_43284_dirty_frag.md) — CVE-2026-43284 분석

## 추천 학습 순서

`hardening (서버 기본)` → `cloud (클라우드 보안)` → `cve (취약점 분석)` → `web_cwe (웹 보안)`

## 전제 조건

[01_fundamentals/linux/](../01_fundamentals/linux/) 필수. 네트워크 기초 권장.

## 관련 섹션

- Linux 기초: [01_fundamentals/linux/](../01_fundamentals/linux/)
- 네트워크 지식: [01_fundamentals/networking/](../01_fundamentals/networking/)
- AWS 인프라: [02_infrastructure/cloud_aws/](../02_infrastructure/cloud_aws/)

[⬆ 루트 README로 돌아가기](../README.md)

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
