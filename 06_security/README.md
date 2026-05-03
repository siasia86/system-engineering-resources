# 보안

시스템 보안, 방화벽, 인증, 취약점 관리 문서 모음.

## 목차

| 섹션 |
|------|
| [1. 문서 목록](#1-문서-목록) / [2. 상황별 선택 가이드](#2-상황별-선택-가이드) |

---

## 1. 문서 목록

| 문서                                                          | 설명                                              |
|---------------------------------------------------------------|---------------------------------------------------|
| [DDoS 방어 아키텍처](ddos_defense_architecture.md)           | XDP/nftables/CrowdSec/HAProxy 계층별 방어 전략   |
| [Linux 서버 보안 강화](linux_hardening.md)                   | sysctl, auditd, 불필요 서비스 제거, umask         |
| [방화벽 - iptables/nftables](firewall_iptables_nftables.md)  | 체인/규칙, nftables 문법, 실전 룰셋               |
| [SSH 보안](ssh_security.md)                                   | 키 기반 인증, sshd_config 강화, fail2ban          |
| [TLS/SSL 가이드](tls_ssl_guide.md)                           | 인증서 구조, Let's Encrypt, openssl, mTLS         |
| [시크릿 관리](secret_management.md)                          | Ansible Vault, AWS Secrets Manager, Vault 비교    |
| [AWS 보안](aws_security.md)                                   | IAM, Security Group, WAF, GuardDuty, CloudTrail   |
| [취약점 스캔](vulnerability_scanning.md)                     | nmap, trivy, lynis, CVE 대응 흐름                 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 상황별 선택 가이드

| 상황                          | 문서                                                                              |
|-------------------------------|-----------------------------------------------------------------------------------|
| 대규모 DDoS 공격 대응         | [DDoS 방어 아키텍처](ddos_defense_architecture.md)                               |
| 신규 서버 보안 기본 설정      | [Linux 서버 보안 강화](linux_hardening.md)                                       |
| 방화벽 규칙 작성              | [방화벽 - iptables/nftables](firewall_iptables_nftables.md)                      |
| SSH 접근 제어 강화            | [SSH 보안](ssh_security.md)                                                       |
| HTTPS/인증서 설정             | [TLS/SSL 가이드](tls_ssl_guide.md)                                               |
| 패스워드/키 안전하게 관리     | [시크릿 관리](secret_management.md)                                              |
| AWS 인프라 보안 점검          | [AWS 보안](aws_security.md)                                                       |
| 서버/컨테이너 취약점 점검     | [취약점 스캔](vulnerability_scanning.md)                                         |

[⬆ 목차로 돌아가기](#목차)

---

[문서 전체 로드맵](../README.md)

---

## 참고 자료

- OWASP: [owasp.org](https://owasp.org/) — ★★★☆☆
- CIS Benchmarks: [cisecurity.org/cis-benchmarks](https://www.cisecurity.org/cis-benchmarks) — ★★★☆☆
- Cloudflare DDoS Protection: [cloudflare.com/ddos](https://www.cloudflare.com/ddos/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-03

**마지막 업데이트**: 2026-05-03

© 2026 siasia86. Licensed under CC BY 4.0.
