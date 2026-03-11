# DDoS 방어 아키텍처

## 전체 구조도

```
인터넷
  ↓
+-------------------------------------------------------------+
|                     글로벌 DNS 레이어                       |
+-------------------------------------------------------------+
Route 53 (DNS)
|- Health Check
|- Failover Routing
+- Geo Routing

  ↓
+-------------------------------------------------------------+
|                  VPC 경계 방어 레이어                       |
+-------------------------------------------------------------+
AWS Network Firewall (Suricata 기반 IPS/IDS)
|- DDoS 패턴 탐지
|- 악성 트래픽 차단
|- 상태 기반 검사
|- 지리적 차단 (GeoIP)
+- CloudWatch Logs 연동

  ↓
+-------------------------------------------------------------+
|                  로드밸런싱 레이어                          |
+-------------------------------------------------------------+
NLB (Network Load Balancer)
|- Cross-AZ 고가용성
|- Connection Tracking
|- Health Check
+- PROXY Protocol v2 전송

  ↓
+-------------------------------------------------------------+
|         Linux Proxy 레이어 (Auto Scaling Group)             |
+-------------------------------------------------------------+
Linux Proxy (3-5대, Auto Scaling)
|
|- [L2 레이어] XDP/eBPF (커널 진입 전)
|  |- 초고속 패킷 드롭 (수백만 pps)
|  |- Redis 동기화 (10초) -------------+
|  |- BPF Map (메모리 기반)            |
|  +- 멀티코어 병렬 처리               |
|                                      |
|- [L3/L4 레이어] nftables (커널)      |
|  |- CrowdSec Bouncer 연동 ------+    |
|  |- 상태 기반 방화벽            |    |
|  |- Rate Limiting               |    |
|  |- Connection Tracking         |    |
|  +- 해시 테이블 (O(1) 조회)     |    |
|                                 |    |
|- [커널 레벨] Kernel Tuning      |    |
|  |- TCP SYN Cookies             |    |
|  |- TCP/IP Stack 최적화         |    |
|  |- Connection Backlog 증가     |    |
|  +- File Descriptor 제한 해제   |    |
|                                 |    |
|- [탐지 레이어] CrowdSec Agent   |    |
|  |- 로그 분석 (실시간)          |    |
|  |- 시나리오 기반 탐지          |    |
|  |- LAPI 연동 ------------------┼----┼--+
|  +- 자동 차단 결정              |    |  |
|                                 |    |  |
|- [L7 레이어] HAProxy            |    |  |
|  |- 백엔드 로드밸런싱           |    |  |
|  |- Health Check                |    |  |
|  |- Connection Pooling          |    |  |
|  |- PROXY Protocol v2 파싱      |    |  |
|  +- 세션 관리                   |    |  |
|                                 |    |  |
+- [모니터링] Zabbix Agent        |    |  |
   |- CPU/메모리/네트워크 --------┼----┼--┼--+
   |- XDP/nftables 통계           |    |  |  |
   |- CrowdSec 메트릭             |    |  |  |
   +- HAProxy 상태                |    |  |  |
                                  |    |  |  |
  ↓                               |    |  |  |
+-------------------------------------------------------------+
|                  백엔드 애플리케이션                        |
+-------------------------------------------------------------+
Windows 게임서버 (Auto Scaling)
|- 게임 로직
|- 플레이어 세션 관리
+- 데이터베이스 연동


===============================================================
                    중앙 관리 레이어 (별도)
===============================================================

+-------------------------------------+    |    |  |  |
|  CrowdSec LAPI Server               |    |    |  |  |
|  (별도 EC2 t3.micro)                | <--+    |  |  |
|  |- MySQL/PostgreSQL (RDS)          |         |  |  |
|  |- AI 기반 탐지 엔진               |         |  |  |
|  |- 커뮤니티 블랙리스트             |         |  |  |
|  +- 차단 결정 관리                  |         |  |  |
+-------------------------------------+         |  |  |
                                                |  |  |
+-------------------------------------+         |  |  |
|  Redis (ElastiCache)                | <-------+  |  |
|  |- XDP BPF Map 동기화              |            |  |
|  |- 실시간 차단 IP 공유             |            |  |
|  +- 10초 주기 업데이트              |            |  |
+-------------------------------------+            |  |
                                                   |  |
+-------------------------------------+            |  |
|  Zabbix Server (중앙 모니터링)      | <----------+  |
|  |- 실시간 대시보드                 |               |
|  |- 알람 (Slack/Email)              |               |
|  |- 트래픽 그래프                   |               |
|  +- 공격 패턴 분석                  |               |
+-------------------------------------+               |
                                                      |
+-------------------------------------+               |
|  CloudWatch                         | <-------------+
|  |- Network Firewall 로그           |
|  |- NLB 메트릭                      |
|  |- Auto Scaling 이벤트             |
|  +- Lambda 트리거                   |
+-------------------------------------+

+-------------------------------------+
|  S3 (로그 저장소)                   |
|  |- Network Firewall 로그           |
|  |- VPC Flow Logs                   |
|  |- HAProxy 액세스 로그             |
|  +- 장기 보관 (Glacier)             |
+-------------------------------------+
```

---

## 데이터 플로우

### 정상 트래픽 (메인 플로우)

```
클라이언트
  ↓
Route 53 (DNS 조회)
  ↓
AWS Network Firewall (검사 통과)
  ↓
NLB (로드밸런싱)
  ↓
Linux Proxy
  |- XDP (통과)
  |- nftables (통과)
  |- CrowdSec (로그 분석)
  +- HAProxy (백엔드 전달)
  ↓
Windows 게임서버
```

### 공격 트래픽 (차단 플로우)

```
공격자
  ↓
Route 53
  ↓
AWS Network Firewall (일부 차단)
  ↓
NLB
  ↓
Linux Proxy
  |- XDP (Redis 차단 목록 확인) → DROP
  |- nftables (CrowdSec 차단 목록) → DROP
  +- CrowdSec (실시간 탐지) → 새 공격 학습
  ↓
차단 완료
```

### 관리 플로우 (별도)

```
Linux Proxy (CrowdSec Agent)
  ↓ (차단 결정 요청)
CrowdSec LAPI Server
  ↓ (차단 IP 목록 응답)
Linux Proxy (nftables 업데이트)

Linux Proxy (XDP 동기화 스크립트)
  ↓ (차단 IP 조회)
Redis (ElastiCache)
  ↓ (차단 IP 목록 응답)
Linux Proxy (XDP BPF Map 업데이트)

Linux Proxy (Zabbix Agent)
  ↓ (메트릭 전송)
Zabbix Server
  ↓ (알람 발송)
관리자
```

---

## 네트워크 구성

### VPC 구조

```
VPC (10.0.0.0/16)
|
|- Public Subnet (10.0.1.0/24)
|  |- NLB
|  +- NAT Gateway
|
|- Private Subnet - Proxy (10.0.10.0/24)
|  +- Linux Proxy (Auto Scaling)
|
|- Private Subnet - Backend (10.0.20.0/24)
|  +- Windows 게임서버
|
+- Private Subnet - Management (10.0.100.0/24)
   |- CrowdSec LAPI Server
   |- Redis (ElastiCache)
   |- Zabbix Server
   +- RDS (MySQL/PostgreSQL)
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
- 상태 기반 방화벽
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
- 자동 차단 결정

**연동:**
- LAPI Server (중앙 관리)
- Firewall Bouncer (nftables)

---

### L7 레이어 (HAProxy)

**역할:**
- 백엔드 로드밸런싱
- Health Check
- PROXY Protocol v2 파싱

**성능:**
- 처리량: 100K conn/s
- 지연시간: < 1ms

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

---

## 모니터링

### Zabbix 대시보드

```
실시간 메트릭:
|- 초당 패킷 수 (pps)
|- XDP 차단 통계
|- nftables 차단 통계
|- CrowdSec 탐지 건수
|- HAProxy 연결 수
+- 게임서버 상태
```

### CloudWatch 알람

```
알람 조건:
|- NLB Unhealthy Host > 1
|- Network Firewall 차단 > 10000/min
|- CPU 사용률 > 80%
+- 네트워크 In > 1Gbps
```

### 로그 분석

```bash
# S3에 저장된 로그 분석
aws s3 cp s3://logs/network-firewall/ - | grep "DROP"

# 공격 IP Top 10
aws s3 cp s3://logs/haproxy/ - | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
```

---

## 비용 (월간 예상)

| 항목 | 구성 | 비용 |
|------|------|------|
| **Route 53** | Hosted Zone + 쿼리 | $1 |
| **Network Firewall** | 엔드포인트 + 데이터 | $350 |
| **NLB** | 로드밸런서 + 데이터 | $20 |
| **Linux Proxy** | EC2 t3.medium × 3 | $90 |
| **CrowdSec LAPI** | EC2 t3.micro | $10 |
| **MySQL** | RDS db.t3.micro | $17 |
| **Redis** | ElastiCache cache.t3.micro | $15 |
| **Zabbix Server** | EC2 t3.small | $15 |
| **CloudWatch** | 로그 + 메트릭 | $10 |
| **S3** | 로그 저장 | $5 |
| **총계** | | **$533/월** |

---

## 성능 지표

### 처리 용량

| 레이어 | 처리량 | 지연시간 |
|--------|--------|----------|
| **XDP** | 10M pps | < 1μs |
| **nftables** | 5M pps | < 10μs |
| **HAProxy** | 100K conn/s | < 1ms |
| **전체** | 10M pps | < 2ms |

### 차단 속도

| 방법 | 동기화 시간 | 차단 위치 |
|------|------------|----------|
| **XDP (Redis)** | 10초 | 커널 진입 전 |
| **nftables (CrowdSec)** | 10초 | 커널 네트워크 스택 |
| **Network Firewall** | 실시간 | VPC 경계 |

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

- AWS Network Firewall: https://docs.aws.amazon.com/network-firewall/
- CrowdSec Documentation: https://docs.crowdsec.net/
- XDP Tutorial: https://github.com/xdp-project/xdp-tutorial
- nftables Wiki: https://wiki.nftables.org/
- HAProxy Documentation: https://www.haproxy.org/
