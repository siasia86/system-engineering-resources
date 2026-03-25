# 보안 - DDoS 방어 및 시스템 보안

시스템 보안, DDoS 공격 방어, 보안 아키텍처에 대한 문서입니다.

## 문서 목록

### DDoS 방어
- **[DDoS 방어 아키텍처](01_ddos_defense_architecture.md)** - DDoS 공격 유형 및 방어 전략

---

## 보안 기초

### 보안의 3요소 (CIA Triad)

- **기밀성 (Confidentiality)** - 인가된 사용자만 접근
- **무결성 (Integrity)** - 데이터 변조 방지
- **가용성 (Availability)** - 서비스 지속성 보장

### DDoS 공격 유형

1. **Volume-based** - 대역폭 소진 (UDP Flood, ICMP Flood)
2. **Protocol-based** - 프로토콜 취약점 (SYN Flood, Ping of Death)
3. **Application-based** - 애플리케이션 리소스 소진 (HTTP Flood, Slowloris)

---

## 방어 전략

### 기본 방어

```bash
# SYN Flood 방어
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_max_syn_backlog=2048

# Rate Limiting (iptables)
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
```

### 고급 방어

- CDN 사용 (Cloudflare, AWS CloudFront)
- WAF (Web Application Firewall)
- Load Balancer
- Auto Scaling

---

## 관련 문서

- [네트워크 기초](../05_computer_science/)
- [시스템 엔지니어링](../04_system_engineer/)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-03-25

© 2026 siasia86. Licensed under CC BY 4.0.
