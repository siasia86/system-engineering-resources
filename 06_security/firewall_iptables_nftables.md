# 방화벽 - iptables / nftables

## 목차

| 섹션 |
|------|
| [1. iptables 기초](#1-iptables-기초) / [2. iptables 실전 룰셋](#2-iptables-실전-룰셋) / [3. nftables 기초](#3-nftables-기초) |
| [4. nftables 실전 룰셋](#4-nftables-실전-룰셋) / [5. iptables vs nftables 비교](#5-iptables-vs-nftables-비교) |

---

## 1. iptables 기초

### 체인 구조

```
패킷 수신
    │
    v
PREROUTING (nat)
    │
    ├─ 로컬 프로세스 대상 ──> INPUT ──> 로컬 프로세스
    │
    └─ 포워딩 대상 ──> FORWARD ──> POSTROUTING ──> 송신
                                        ^
로컬 프로세스 ──> OUTPUT ──────────────┘
```

### 기본 명령어

```bash
# 규칙 목록 (번호 포함)
sudo iptables -L -n -v --line-numbers

# 규칙 추가 (끝에)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 규칙 삽입 (앞에)
sudo iptables -I INPUT 1 -p tcp --dport 22 -j ACCEPT

# 규칙 삭제 (번호로)
sudo iptables -D INPUT 3

# 체인 기본 정책 설정
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# 규칙 저장 (Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. iptables 실전 룰셋

```bash
#!/bin/bash
# 기본 서버 방화벽 룰셋

IPT="sudo iptables"

# 기존 규칙 초기화
$IPT -F
$IPT -X
$IPT -Z

# 기본 정책: 모두 차단
$IPT -P INPUT DROP
$IPT -P FORWARD DROP
$IPT -P OUTPUT ACCEPT

# loopback 허용
$IPT -A INPUT -i lo -j ACCEPT

# 기존 연결 허용 (Stateful)
$IPT -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# ICMP (ping) 허용
$IPT -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT

# SSH (Rate Limiting 포함)
$IPT -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW \
    -m recent --set --name SSH
$IPT -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW \
    -m recent --update --seconds 60 --hitcount 4 --name SSH -j DROP
$IPT -A INPUT -p tcp --dport 22 -j ACCEPT

# HTTP/HTTPS
$IPT -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT

# 나머지 차단 및 로깅
$IPT -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-DROP: "
$IPT -A INPUT -j DROP
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. nftables 기초

iptables 후속. 단일 프레임워크로 IPv4/IPv6/ARP 통합 관리.

```bash
# 설치 및 활성화
sudo apt install nftables
sudo systemctl enable --now nftables

# 현재 규칙 확인
sudo nft list ruleset

# 규칙 파일 적용
sudo nft -f /etc/nftables.conf

# 규칙 저장
sudo nft list ruleset > /etc/nftables.conf
```

### 기본 구조

```nft
table <family> <name> {
    chain <name> {
        type <type> hook <hook> priority <priority>; policy <policy>;
        <rule>
    }
}
```

| 항목     | 값                                                            |
|----------|---------------------------------------------------------------|
| family   | `ip` / `ip6` / `inet` (IPv4+IPv6) / `arp`                     |
| type     | `filter` / `nat` / `route`                                    |
| hook     | `prerouting` / `input` / `forward` / `output` / `postrouting` |
| priority | 숫자 (낮을수록 먼저 처리), `filter`=0                         |

[⬆ 목차로 돌아가기](#목차)

---

## 4. nftables 실전 룰셋

```bash
# /etc/nftables.conf

flush ruleset

table inet filter {

    # 차단 IP 집합 (동적 관리)
    set blocklist {
        type ipv4_addr
        flags dynamic, timeout
        timeout 1h
    }

    chain input {
        type filter hook input priority filter; policy drop;

        # loopback
        iif lo accept

        # 기존 연결
        ct state established,related accept

        # blocklist 차단
        ip saddr @blocklist drop

        # ICMP
        ip protocol icmp icmp type echo-request limit rate 1/second accept

        # SSH (brute-force 방어 — meter 사용, 버전 호환성 높음)
        tcp dport 22 ct state new meter ssh-meter { ip saddr limit rate over 3/minute } drop
        tcp dport 22 accept

        # HTTP/HTTPS
        tcp dport { 80, 443 } accept

        # 로깅 후 차단
        limit rate 5/minute log prefix "nft-DROP: "
        drop
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

```bash
# 동적 blocklist 관리
sudo nft add element inet filter blocklist { 192.0.2.1 }
sudo nft delete element inet filter blocklist { 192.0.2.1 }
sudo nft list set inet filter blocklist
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. iptables vs nftables 비교

| 구분         | iptables                  | nftables                       |
|--------------|---------------------------|--------------------------------|
| IPv4/IPv6    | 별도 명령어 (`ip6tables`) | `inet` family로 통합           |
| 성능         | 선형 탐색                 | 해시/집합 기반, 빠름           |
| 동적 집합    | ipset 별도 설치 필요      | 내장 (`set`, `map`)            |
| 문법         | 명령어 기반               | 선언형 설정 파일               |
| 커널 지원    | 3.x~                      | 3.13~ (권장 4.x~)              |
| 마이그레이션 | -                         | `iptables-translate` 변환 도구 |

```bash
# iptables 규칙을 nftables 문법으로 변환
iptables-translate -A INPUT -p tcp --dport 22 -j ACCEPT
# 출력: nft add rule ip filter INPUT tcp dport 22 counter accept
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- nftables Wiki: [wiki.nftables.org](https://wiki.nftables.org/) — ★★★☆☆
- iptables man page: [netfilter.org](https://www.netfilter.org/documentation/) — ★★★☆☆
- nftables meters (rate limiting): [wiki.nftables.org/wiki-nftables/index.php/Meters](https://wiki.nftables.org/wiki-nftables/index.php/Meters) — ★★★☆☆
- Netfilter conntrack: [conntrack-tools.netfilter.org](https://conntrack-tools.netfilter.org/) — ★★★☆☆

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
