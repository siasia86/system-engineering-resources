# DDoS 방어 아키텍처

## 목차

| 섹션 |
|------|
| [전체 구조도](#전체-구조도) |
| [데이터 플로우](#데이터-플로우) |
| [네트워크 구성](#네트워크-구성) |
| [레이어별 역할](#레이어별-역할) |
| [차단 IP 추가 방법](#차단-ip-추가-방법) |
| [모니터링](#모니터링) |
| [비용 (월간 예상)](#비용-월간-예상) |
| [성능 지표](#성능-지표) |
| [관리 명령어](#관리-명령어) |

---

## 전체 구조도

```
인터넷
  v
┌─────────────────────────────────────────────────────────────┐
│                     Global DNS Layer                        │
└─────────────────────────────────────────────────────────────┘
Route 53 (DNS)
├─ Health Check
├─ Failover Routing
└─ Geo Routing

  v
┌─────────────────────────────────────────────────────────────┐
│                  VPC Border Defense Layer                   │
└─────────────────────────────────────────────────────────────┘
AWS Network Firewall (Suricata 기반 IPS/IDS)
├─ DDoS pattern detection
├─ Malicious traffic blocking
├─ Stateful inspection
├─ Geo blocking (GeoIP)
└─ CloudWatch Logs integration

  v
┌─────────────────────────────────────────────────────────────┐
│                  Load Balancing Layer                       │
└─────────────────────────────────────────────────────────────┘
NLB (Network Load Balancer)
├─ Cross-AZ high availability
├─ Connection Tracking
├─ Health Check
└─ PROXY Protocol v2 forwarding

  v
┌─────────────────────────────────────────────────────────────┐
│         Linux Proxy Layer (Auto Scaling Group)              │
└─────────────────────────────────────────────────────────────┘
Linux Proxy (3-5대, Auto Scaling)
│
├─ [Pre-kernel] XDP/eBPF
│  ├─ Ultra-fast packet drop (millions pps)
│  ├─ Redis sync (10s interval) ──────────────────────────────────────┐
│  ├─ BPF Map (memory-based)                                          │
│  └─ Multi-core parallel processing                                  │
│                                                                     │
├─ [L3/L4] nftables (kernel)                                          │
│  ├─ CrowdSec Bouncer ───────────────────────────────────────┐       │
│  ├─ Stateful firewall                                       │       │
│  ├─ Rate Limiting                                           │       │
│  ├─ Connection Tracking                                     │       │
│  └─ Hash table (O(1) lookup)                                │       │
│                                                             │       │
├─ [Kernel] Kernel Tuning                                     │       │
│  ├─ TCP SYN Cookies                                         │       │
│  ├─ TCP/IP Stack optimization                               │       │
│  ├─ Connection Backlog increase                             │       │
│  └─ File Descriptor limit increase                          │       │
│                                                             │       │
├─ [Detection] CrowdSec Agent                                 │       │
│  ├─ Log analysis (realtime)                                 │       │
│  ├─ Scenario-based detection                                │       │
│  ├─ LAPI integration ───────────────────────────────────────┼───┐   │
│  └─ Auto block decision                                     │   │   │
│                                                             │   │   │
├─ [L7] HAProxy                                               │   │   │
│  ├─ Backend load balancing                                  │   │   │
│  ├─ Health Check                                            │   │   │
│  ├─ Connection Pooling                                      │   │   │
│  ├─ PROXY Protocol v2 parsing                               │   │   │
│  └─ Session management                                      │   │   │
│                                                             │   │   │
└─ [Monitoring] Zabbix Agent                                  │   │   │
   ├─ CPU/Memory/Network ─────────────────────────────────────┼───┼───┼──┐
   ├─ XDP/nftables stats                                      │   │   │  │
   ├─ CrowdSec metrics                                        │   │   │  │
   └─ HAProxy status                                          │   │   │  │
                                                              │   │   │  │
  v                                                           │   │   │  │
┌─────────────────────────────────────────────────────────────┐   │   │  │
│                  Backend Application                        │   │   │  │
└─────────────────────────────────────────────────────────────┘   │   │  │
Windows Game Server (Auto Scaling)                                │   │  │
├─ Game logic                                                     │   │  │
├─ Player session management                                      │   │  │
└─ Database integration                                           │   │  │
                                                                  │   │  │
===============================================================   │   │  │
                    Central Management Layer (Separate)           │   │  │
===============================================================   │   │  │
                                                                  │   │  │
┌─────────────────────────────────────┐                           │   │  │
│  CrowdSec LAPI Server               │ <─────────────────────────┘   │  │
│  ├─ MySQL/PostgreSQL (RDS)          │                               │  │
│  ├─ AI-based detection engine       │                               │  │
│  ├─ Community blocklist             │                               │  │
│  └─ Block decision management       │                               │  │
└─────────────────────────────────────┘                               │  │
                                                                      │  │
┌─────────────────────────────────────┐                               │  │
│  Redis (ElastiCache)                │ <─────────────────────────────┘  │
│  ├─ XDP BPF Map sync                │                                  │
│  ├─ Realtime blocked IP sharing     │                                  │
│  └─ 10s interval update             │                                  │
└─────────────────────────────────────┘                                  │
                                                                         │
┌─────────────────────────────────────┐                                  │
│  Zabbix Server (Central Monitoring) │ <────────────────────────────────┘
│  ├─ Realtime dashboard              │
│  ├─ Alert (Slack/Email)             │
│  ├─ Traffic graph                   │
│  └─ Attack pattern analysis         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  CloudWatch                         │
│  ├─ Network Firewall logs           │
│  ├─ NLB metrics                     │
│  ├─ Auto Scaling events             │
│  └─ Lambda triggers                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  S3 (Log storage)                   │
│  ├─ Network Firewall logs           │
│  ├─ VPC Flow Logs                   │
│  ├─ HAProxy access logs             │
│  └─ Long-term storage (Glacier)     │
└─────────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 데이터 플로우

### 정상 트래픽 (메인 플로우)

```
Client
  v
Route 53 (DNS 조회)
  v
AWS Network Firewall (검사 통과)
  v
NLB (로드밸런싱)
  v
Linux Proxy
  ├─ XDP (pass)
  ├─ nftables (pass)
  ├─ CrowdSec (log analysis)
  └─ HAProxy (backend forward)
  v
Windows Game Server
```

### 공격 트래픽 (차단 플로우)

```
Attacker
  v
Route 53
  v
AWS Network Firewall (일부 차단)
  v
NLB
  v
Linux Proxy
  ├─ XDP (check Redis blocklist) → DROP
  ├─ nftables (CrowdSec blocklist) → DROP
  └─ CrowdSec (realtime detection) → learn new attack
  v
Blocked
```

### 관리 플로우 (별도)

```
Linux Proxy (CrowdSec Agent)
  v (Block decision request)
CrowdSec LAPI Server
  v (Blocked IP list response)
Linux Proxy (nftables 업데이트)

Linux Proxy (XDP 동기화 스크립트)
  v (Blocked IP query)
Redis (ElastiCache)
  v (Blocked IP list response)
Linux Proxy (XDP BPF Map 업데이트)

Linux Proxy (Zabbix Agent)
  v (Metrics push)
Zabbix Server
  v (Alert sent)
Admin
```

[⬆ 목차로 돌아가기](#목차)

---

## 네트워크 구성

### VPC 구조

```
VPC (10.0.0.0/16)
│
├─ Public Subnet (10.0.1.0/24)
│  ├─ NLB
│  └─ NAT Gateway
│
├─ Private Subnet - Proxy (10.0.10.0/24)
│  └─ Linux Proxy (Auto Scaling)
│
├─ Private Subnet - Backend (10.0.20.0/24)
│  └─ Windows Game Server
│
└─ Private Subnet - Management (10.0.100.0/24)
   ├─ CrowdSec LAPI Server
   ├─ Redis (ElastiCache)
   ├─ Zabbix Server
   └─ RDS (MySQL/PostgreSQL)
```

### 보안 그룹

**NLB → Linux Proxy:**
```
Source: 0.0.0.0/0
Port: 27015 (게임 포트)
Protocol: TCP/UDP
```

**Linux Proxy → CrowdSec LAPI:**
```
Source: 10.0.10.0/24 (Proxy Subnet)
Port: 8080
Protocol: TCP
```

**Linux Proxy → Redis:**
```
Source: 10.0.10.0/24
Port: 6379
Protocol: TCP
```

**Linux Proxy → Zabbix:**
```
Source: 10.0.10.0/24
Port: 10051
Protocol: TCP
```

**Linux Proxy → 게임서버:**
```
Source: 10.0.10.0/24
Port: 27015
Protocol: TCP/UDP
```

[⬆ 목차로 돌아가기](#목차)

---

## 레이어별 역할

### L2 레이어 (XDP)

**역할:**
- 커널 진입 전 초고속 차단
- 대량 공격 IP 처리

**동기화:**
- Redis (ElastiCache) ← 10초 주기

**성능:**
- 처리량: 10M pps
- 지연시간: < 1μs

---

### L3/L4 레이어 (nftables)

**역할:**
- Stateful firewall
- Rate Limiting
- Connection Tracking

**동기화:**
- CrowdSec LAPI ← 10초 주기

**성능:**
- 처리량: 5M pps
- 지연시간: < 10μs

---

### 탐지 레이어 (CrowdSec)

**역할:**
- 실시간 로그 분석
- AI 기반 공격 탐지
- Auto block decision

**연동:**
- LAPI Server (중앙 관리)
- Firewall Bouncer (nftables)

---

### L7 레이어 (HAProxy)

**역할:**
- Backend load balancing
- Health Check
- PROXY Protocol v2 파싱

**성능:**
- 처리량: 100K conn/s
- 지연시간: < 1ms

[⬆ 목차로 돌아가기](#목차)

---

## 차단 IP 추가 방법

### CrowdSec을 통한 차단 (권장)

```bash
# LAPI 서버에서 실행
sudo cscli decisions add --ip 1.2.3.4 --duration 4h --reason "DDoS attack"

# 10초 후 자동 반영:
# - 모든 Linux Proxy의 nftables
```

### Redis를 통한 XDP 차단 (초고속)

```bash
# Redis에 직접 추가
redis-cli -h redis.xxxxx.cache.amazonaws.com SADD blocked_ips "1.2.3.4"

# 10초 후 자동 반영:
# - 모든 Linux Proxy의 XDP BPF Map
```

### 대량 IP 차단

```bash
# 파일에서 일괄 추가
cat blocked_ips.txt | while read ip; do
  redis-cli -h redis.xxxxx.cache.amazonaws.com SADD blocked_ips "$ip"
done
```

[⬆ 목차로 돌아가기](#목차)

---

## 모니터링

### Zabbix 대시보드

```
Realtime metrics:
├─ Packets per second (pps)
├─ XDP block stats
├─ nftables block stats
├─ CrowdSec detection count
├─ HAProxy connection count
└─ Game server status
```

### CloudWatch 알람

```
Alert conditions:
├─ NLB Unhealthy Host > 1
├─ Network Firewall blocks > 10000/min
├─ CPU usage > 80%
└─ Network In > 1Gbps
```

### 로그 분석

```bash
# S3에 저장된 로그 분석
aws s3 cp s3://logs/network-firewall/ - | grep "DROP"

# 공격 IP Top 10
aws s3 cp s3://logs/haproxy/ - | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
```

[⬆ 목차로 돌아가기](#목차)

---

## 비용 (월간 예상)

| 항목                 | 구성                       | 비용        |
|----------------------|----------------------------|-------------|
| **Route 53**         | Hosted Zone + 쿼리         | $1          |
| **Network Firewall** | 엔드포인트 + 데이터        | $350        |
| **NLB**              | 로드밸런서 + 데이터        | $20         |
| **Linux Proxy**      | EC2 t3.medium × 3          | $90         |
| **CrowdSec LAPI**    | EC2 t3.micro               | $10         |
| **MySQL**            | RDS db.t3.micro            | $17         |
| **Redis**            | ElastiCache cache.t3.micro | $15         |
| **Zabbix Server**    | EC2 t3.small               | $15         |
| **CloudWatch**       | 로그 + 메트릭              | $10         |
| **S3**               | 로그 저장                  | $5          |
| **총계**             |                            | **$533/월** |

[⬆ 목차로 돌아가기](#목차)

---

## 성능 지표

### 처리 용량

| 레이어       | 처리량      | 지연시간 |
|--------------|-------------|----------|
| **XDP**      | 10M pps     | < 1μs    |
| **nftables** | 5M pps      | < 10μs   |
| **HAProxy**  | 100K conn/s | < 1ms    |
| **전체**     | 10M pps     | < 2ms    |

### 차단 속도

| 방법                    | 동기화 시간 | 차단 위치          |
|-------------------------|-------------|--------------------|
| **XDP (Redis)**         | 10초        | 커널 진입 전       |
| **nftables (CrowdSec)** | 10초        | 커널 네트워크 스택 |
| **Network Firewall**    | 실시간      | VPC 경계           |

[⬆ 목차로 돌아가기](#목차)

---

## 관리 명령어

### 상태 확인

```bash
# XDP 통계
bpftool map dump name blocked_ips | wc -l
ip -s link show dev eth0

# nftables 통계
nft list set inet crowdsec crowdsec-blacklists
nft list chain inet filter input -a

# CrowdSec 상태
sudo cscli metrics
sudo cscli decisions list

# HAProxy 상태
echo "show stat" | socat stdio /var/run/haproxy.sock
echo "show info" | socat stdio /var/run/haproxy.sock
```

### 차단 IP 관리

```bash
# CrowdSec 차단 추가
sudo cscli decisions add --ip 1.2.3.4 --duration 4h

# CrowdSec 차단 해제
sudo cscli decisions delete --ip 1.2.3.4

# Redis 차단 추가
redis-cli -h redis.xxxxx.cache.amazonaws.com SADD blocked_ips "1.2.3.4"

# Redis 차단 해제
redis-cli -h redis.xxxxx.cache.amazonaws.com SREM blocked_ips "1.2.3.4"

# Redis 전체 목록
redis-cli -h redis.xxxxx.cache.amazonaws.com SMEMBERS blocked_ips
```

---

## 참고 자료

- AWS Network Firewall: [docs.aws.amazon.com](https://docs.aws.amazon.com/network-firewall/) — ★★★☆☆
- CrowdSec Documentation: [docs.crowdsec.net](https://docs.crowdsec.net/) — ★★★☆☆
- XDP Tutorial: [github.com/xdp-project](https://github.com/xdp-project/xdp-tutorial) — ★★☆☆☆
- nftables Wiki: [wiki.nftables.org](https://wiki.nftables.org/) — ★★★☆☆
- HAProxy Documentation: [haproxy.org](https://www.haproxy.org/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-11

**마지막 업데이트**: 2026-03-11

© 2026 siasia86. Licensed under CC BY 4.0.
