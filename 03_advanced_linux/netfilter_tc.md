# netfilter / tc — 네트워크 제어

Linux 패킷 필터링(netfilter/iptables)과 트래픽 제어(tc)를 정리합니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. netfilter 개요](#1-netfilter-개요) / [2. iptables](#2-iptables) / [3. nftables](#3-nftables) |
| [4. tc — 트래픽 제어](#4-tc--트래픽-제어) / [5. 실무 예시](#5-실무-예시)                         |

---

## 1. netfilter 개요

커널 내 패킷 처리 프레임워크입니다. iptables/nftables/Cilium 모두 netfilter 위에서 동작합니다.

```
packet in
    │
    v
PREROUTING ──> (routing decision) ──> FORWARD ──> POSTROUTING ──> packet out
                    │
                    v
                 INPUT
                    │
                    v
               local process
                    │
                    v
                 OUTPUT
                    │
                    v
              POSTROUTING ──> packet out
```

### 체인과 테이블

| 테이블   | 용도           | 체인                            |
|----------|----------------|---------------------------------|
| `filter` | 패킷 허용/차단 | INPUT, FORWARD, OUTPUT          |
| `nat`    | 주소 변환      | PREROUTING, POSTROUTING, OUTPUT |
| `mangle` | 패킷 헤더 수정 | 모든 체인                       |
| `raw`    | 연결 추적 제외 | PREROUTING, OUTPUT              |

[⬆ 목차로 돌아가기](#목차)

---

## 2. iptables

```bash
# 현재 규칙 확인
iptables -L -n -v
iptables -L -n -v -t nat

# 기본 정책 확인
iptables -L | grep policy

# 규칙 추가
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -j DROP   # 나머지 차단

# 규칙 삽입 (맨 앞)
iptables -I INPUT 1 -s 10.0.0.0/8 -j ACCEPT

# 규칙 삭제
iptables -D INPUT -p tcp --dport 80 -j ACCEPT
iptables -D INPUT 3   # 3번째 규칙 삭제

# 체인 초기화
iptables -F INPUT
iptables -F   # 전체 초기화
```

### NAT 설정

```bash
# SNAT — 내부 → 외부 (IP 마스커레이딩)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# DNAT — 포트 포워딩
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.10:80

# IP 포워딩 활성화
echo 1 > /proc/sys/net/ipv4/ip_forward
```

### conntrack — 연결 상태 추적

```bash
# 현재 연결 상태 확인
conntrack -L
conntrack -L | grep ESTABLISHED | wc -l

# 특정 연결 삭제
conntrack -D -s 1.2.3.4

# conntrack 테이블 크기
cat /proc/sys/net/netfilter/nf_conntrack_max
cat /proc/sys/net/netfilter/nf_conntrack_count  # 현재 사용량
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. nftables

iptables의 현대적 대안입니다. Ubuntu 20.04+, Rocky 9+ 기본.

```bash
# 현재 규칙 확인
nft list ruleset

# 테이블/체인 생성
nft add table inet filter
nft add chain inet filter input { type filter hook input priority 0 \; policy drop \; }

# 규칙 추가
nft add rule inet filter input tcp dport 22 accept
nft add rule inet filter input tcp dport { 80, 443 } accept
nft add rule inet filter input ct state established,related accept

# 규칙 삭제
nft delete rule inet filter input handle <handle_id>

# 영구 저장
nft list ruleset > /etc/nftables.conf
systemctl enable nftables
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. tc — 트래픽 제어

네트워크 대역폭 제한, 지연 추가, 패킷 손실 시뮬레이션에 사용합니다.

### 기본 개념

```
egress queue (qdisc)
┌─────────────────────────────┐
│  root qdisc                 │
│  ├── class 1:1 (total 100M) │
│  │   ├── class 1:10 (web)   │
│  │   └── class 1:20 (db)    │
└─────────────────────────────┘
```

### 대역폭 제한 (TBF)

```bash
# eth0 packet out 10Mbps 제한
tc qdisc add dev eth0 root tbf rate 10mbit burst 32kbit latency 400ms

# 확인
tc qdisc show dev eth0

# 제거
tc qdisc del dev eth0 root

# 수신 제한 (IFB 사용)
modprobe ifb
ip link set ifb0 up
tc qdisc add dev eth0 ingress
tc filter add dev eth0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
tc qdisc add dev ifb0 root tbf rate 10mbit burst 32kbit latency 400ms
```

### 네트워크 장애 시뮬레이션 (netem)

```bash
# 100ms 지연 추가
tc qdisc add dev eth0 root netem delay 100ms

# 지연 + 지터 (100ms ± 20ms)
tc qdisc add dev eth0 root netem delay 100ms 20ms

# 패킷 손실 1%
tc qdisc add dev eth0 root netem loss 1%

# 패킷 손상 0.1%
tc qdisc add dev eth0 root netem corrupt 0.1%

# 패킷 순서 뒤섞기
tc qdisc add dev eth0 root netem reorder 25% delay 10ms

# 복합 적용 (지연 + 손실)
tc qdisc add dev eth0 root netem delay 50ms loss 2%

# 제거
tc qdisc del dev eth0 root
```

### HTB — 계층적 대역폭 분배

```bash
# total 100Mbps, web 60Mbps guaranteed, db 40Mbps guaranteed
tc qdisc add dev eth0 root handle 1: htb default 30
tc class add dev eth0 parent 1: classid 1:1 htb rate 100mbit
tc class add dev eth0 parent 1:1 classid 1:10 htb rate 60mbit ceil 100mbit
tc class add dev eth0 parent 1:1 classid 1:20 htb rate 40mbit ceil 100mbit

# 필터로 트래픽 분류
tc filter add dev eth0 parent 1: protocol ip prio 1 u32 \
  match ip dport 80 0xffff flowid 1:10
tc filter add dev eth0 parent 1: protocol ip prio 1 u32 \
  match ip dport 5432 0xffff flowid 1:20
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실무 예시

### 백업 스크립트 네트워크 제한

```bash
# 백업 실행 전 대역폭 제한
tc qdisc add dev eth0 root tbf rate 50mbit burst 32kbit latency 400ms
rsync -av /data/ backup@remote:/backup/
tc qdisc del dev eth0 root
```

### 네트워크 장애 테스트

```bash
# 스테이징 환경에서 네트워크 불안정 시뮬레이션
tc qdisc add dev eth0 root netem delay 200ms loss 5%
# 애플리케이션 동작 확인
tc qdisc del dev eth0 root
```

### conntrack 고갈 대응

```bash
# conntrack 테이블 고갈 확인
dmesg | grep "nf_conntrack: table full"

# 한도 증가
echo 1000000 > /proc/sys/net/netfilter/nf_conntrack_max
echo "net.netfilter.nf_conntrack_max=1000000" >> /etc/sysctl.conf

# 타임아웃 단축
echo 60 > /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux tc man page: [man7.org/linux/man-pages/man8/tc.8.html](https://man7.org/linux/man-pages/man8/tc.8.html) — ★★★☆☆
- netfilter: [netfilter.org/documentation](https://www.netfilter.org/documentation/) — ★★★☆☆
- [ebpf.md](ebpf.md)

---

**작성일** : 2026-05-21

**마지막 업데이트** : 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
