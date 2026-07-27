# DDoS 공격 패턴과 방어 전략 가이드

## 목차
1. [Layer 3/4 공격 (네트워크/전송 계층)](#layer-34-공격-네트워크전송-계층)
2. [Layer 7 공격 (애플리케이션 계층)](#layer-7-공격-애플리케이션-계층)
3. [증폭 공격 (Amplification Attacks)](#증폭-공격-amplification-attacks)
4. [분산 공격 (Distributed Attacks)](#분산-공격-distributed-attacks)
5. [고급 공격 기법](#고급-공격-기법)
6. [방어 전략](#방어-전략)
7. [모니터링 및 탐지](#모니터링-및-탐지)
8. [Cloudflare WAF & Rate Limiting](#cloudflare-waf--rate-limiting)
9. [공격 유형별 Cloudflare 서비스 매핑](#공격-유형별-cloudflare-서비스-매핑)
10. [국내 IDC 업체별 DDoS 방어 현황](#국내-idc-업체별-ddos-방어-현황)
11. [결론](#결론)
12. [References](#references)

---

## Layer 3/4 공격 (네트워크/전송 계층)

### 1. UDP Flood

**공격 원리:**
- 대량의 UDP 패킷을 무작위 포트로 전송
- 서버가 각 패킷에 대해 ICMP "Port Unreachable" 응답
- 네트워크 대역폭과 서버 리소스 고갈

**공격 특징:**
```
소스 IP: 위조 가능
대상 포트: 랜덤 또는 특정 포트
패킷 크기: 다양 (64B ~ 1500B)
초당 패킷 수: 수만 ~ 수백만 PPS
```

**방어 전략:**
```bash
# iptables 기반 방어
iptables -A INPUT -p udp -m limit --limit 50/sec --limit-burst 100 -j ACCEPT
iptables -A INPUT -p udp -j DROP

# 특정 포트만 허용
iptables -A INPUT -p udp --dport 53 -j ACCEPT  # DNS
iptables -A INPUT -p udp --dport 123 -j ACCEPT # NTP
iptables -A INPUT -p udp -j DROP

# sysctl 튜닝
echo 'net.ipv4.icmp_ratelimit = 1000' >> /etc/sysctl.conf
echo 'net.ipv4.icmp_ratemask = 6168' >> /etc/sysctl.conf
```

### 2. SYN Flood

**공격 원리:**
- TCP 3-way handshake의 첫 번째 단계만 수행
- 서버의 연결 대기 큐(backlog) 고갈
- 정상 연결 요청 처리 불가

**공격 특징:**
```
TCP Flags: SYN=1, ACK=0
소스 IP: 위조됨
시퀀스 번호: 랜덤
연결 상태: HALF-OPEN으로 유지
```

**방어 전략:**
```bash
# SYN Cookies 활성화
echo 1 > /proc/sys/net/ipv4/tcp_syncookies

# SYN 백로그 크기 증가
echo 4096 > /proc/sys/net/ipv4/tcp_max_syn_backlog

# SYN-ACK 재전송 횟수 감소
echo 1 > /proc/sys/net/ipv4/tcp_synack_retries

# iptables SYN 제한
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# nginx 설정
server {
    listen 80 backlog=4096;
    # ...
}
```

### 3. ICMP Flood (Ping Flood)

**공격 원리:**
- 대량의 ICMP Echo Request 패킷 전송
- 서버가 각각에 Echo Reply로 응답
- 네트워크 대역폭 소모

**공격 특징:**
```
ICMP Type: 8 (Echo Request)
패킷 크기: 최대 65535 바이트
주파수: 초당 수천 ~ 수만 패킷
```

**방어 전략:**
```bash
# ICMP 응답 비활성화
echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all

# ICMP Rate Limiting
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/sec -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

# 큰 ICMP 패킷 차단
iptables -A INPUT -p icmp -m length --length 1000:65535 -j DROP
```

### 4. TCP RST/FIN Flood

**공격 원리:**
- 기존 연결에 RST 또는 FIN 패킷 주입
- 정상 연결 강제 종료
- 서비스 중단 유발

**방어 전략:**
```bash
# 연결 추적 활성화
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -m state --state INVALID -j DROP

# TCP 윈도우 스케일링 비활성화 (필요시)
echo 0 > /proc/sys/net/ipv4/tcp_window_scaling
```

---

## Layer 7 공격 (애플리케이션 계층)

### 1. HTTP Flood

**공격 원리:**
- 정상적인 HTTP 요청을 대량 전송
- 웹 서버 리소스 고갈
- 데이터베이스 과부하 유발

**공격 패턴:**
```http
GET / HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0...

POST /search HTTP/1.1
Host: target.com
Content-Length: 1000
[대량 데이터]
```

**방어 전략:**
```nginx
# nginx rate limiting
http {
    limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;
    
    server {
        location / {
            limit_req zone=one burst=5 nodelay;
            limit_req_status 429;
        }
        
        # 연결 수 제한
        limit_conn_zone $binary_remote_addr zone=addr:10m;
        limit_conn addr 10;
    }
}
```

```apache
# Apache mod_security
SecRule REQUEST_METHOD "@streq GET" \
    "id:1001,phase:1,block,msg:'GET flood detected',\
    ratelimited,setvar:'ip.requests_per_minute=+1',\
    expirevar:'ip.requests_per_minute=60'"

SecRule IP:REQUESTS_PER_MINUTE "@gt 60" \
    "id:1002,phase:1,block,msg:'Rate limit exceeded'"
```

### 2. Slowloris

**공격 원리:**
- HTTP 헤더를 천천히 전송
- 연결을 오래 유지하여 서버 스레드 고갈
- 최소 대역폭으로 최대 피해

**공격 코드 예시:**
```
[의사코드 - 공격 원리 이해용]

1. 대상 서버에 TCP 연결 200개 생성
2. 각 연결에 불완전한 HTTP 헤더 전송 (GET / HTTP/1.1, Host: ...)
3. 무한 반복:
   - 모든 연결에 15초마다 의미없는 헤더 1줄 추가 전송 (X-a: b)
   - 서버는 헤더가 완성될 때까지 연결 유지 → 커넥션 풀 고갈
```

**방어 전략:**
```nginx
# nginx 설정
http {
    client_header_timeout 10s;
    client_body_timeout 10s;
    send_timeout 10s;
    
    # 헤더 크기 제한
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
}
```

```apache
# Apache 설정
Timeout 10
KeepAliveTimeout 5
RequestReadTimeout header=10 body=30

# mod_reqtimeout
LoadModule reqtimeout_module modules/mod_reqtimeout.so
RequestReadTimeout header=10-20,MinRate=500 body=20,MinRate=500
```

### 3. Slow POST

**공격 원리:**
- POST 데이터를 매우 천천히 전송
- Content-Length는 크게 설정
- 서버가 완전한 데이터 수신 대기

**방어 전략:**
```nginx
# nginx 설정
client_body_timeout 10s;
client_max_body_size 1m;

# 업로드 속도 제한
limit_rate 100k;
```

### 4. HTTP Pipelining Attack

**공격 원리:**
- 하나의 연결로 다수의 HTTP 요청 전송
- 서버 처리 능력 초과

**방어 전략:**
```nginx
# HTTP/2 사용 (pipelining 문제 해결)
listen 443 ssl http2;

# 연결당 요청 수 제한
keepalive_requests 100;
```

---

## 증폭 공격 (Amplification Attacks)

### 1. DNS Amplification

**공격 원리:**
- 작은 DNS 쿼리로 큰 응답 유도
- 소스 IP를 피해자로 위조
- 증폭 비율: 1:28 ~ 1:54

**공격 쿼리 예시:**
```bash
# ANY 쿼리 (큰 응답)
dig @open_resolver ANY isc.org

# TXT 레코드 쿼리
dig @open_resolver TXT google.com
```

**방어 전략:**
```bash
# DNS 서버 보안 설정 (BIND)
options {
    recursion no;                    # 재귀 쿼리 비활성화
    allow-recursion { none; };       # 재귀 허용 IP 제한
    rate-limit {
        responses-per-second 5;      # 응답 속도 제한
        window 5;
    };
    
    # ANY 쿼리 제한
    deny-answer-aliases { "." ; };
    minimal-any yes;
};

# iptables DNS 보호
iptables -A INPUT -p udp --dport 53 -m string --string "ANY" --algo bm -j DROP
iptables -A INPUT -p udp --dport 53 -m recent --name DNS --set
iptables -A INPUT -p udp --dport 53 -m recent --name DNS --rcheck --seconds 1 --hitcount 10 -j DROP
```

### 2. NTP Amplification

**공격 원리:**
- NTP monlist 명령 악용
- 증폭 비율: 1:206

**공격 명령:**
```bash
ntpdc -c monlist target_ntp_server
```

**방어 전략:**
```bash
# NTP 서버 설정 (/etc/ntp.conf)
disable monitor                      # monlist 명령 비활성화
restrict default kod nomodify notrap nopeer noquery
restrict -6 default kod nomodify notrap nopeer noquery

# 신뢰할 수 있는 서버만 허용
restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

# iptables NTP 보호
iptables -A INPUT -p udp --dport 123 -m string --string "monlist" --algo bm -j DROP
```

### 3. SNMP Amplification

**공격 원리:**
- SNMP GetBulkRequest 사용
- 증폭 비율: 1:6.3

**방어 전략:**
```bash
# SNMP 보안 설정
# community string 변경
echo "rocommunity mySecretCommunity 192.168.1.0/24" > /etc/snmp/snmpd.conf

# iptables SNMP 보호
iptables -A INPUT -p udp --dport 161 -s ! 192.168.1.0/24 -j DROP
```

### 4. Memcached Amplification

**공격 원리:**
- Memcached stats 명령 악용
- 증폭 비율: 1:10,000 ~ 1:51,000

**방어 전략:**
```bash
# Memcached 보안 설정
memcached -l 127.0.0.1 -p 11211 -U 0  # UDP 비활성화

# iptables 보호
iptables -A INPUT -p tcp --dport 11211 -s ! 127.0.0.1 -j DROP
iptables -A INPUT -p udp --dport 11211 -j DROP
```

---

## 분산 공격 (Distributed Attacks)

### 1. Botnet 기반 공격

**특징:**
- 수천\~수만 대의 감염된 컴퓨터 동원
- 지리적으로 분산된 IP 주소
- 다양한 공격 벡터 동시 사용

**방어 전략:**
```bash
# GeoIP 기반 차단
iptables -A INPUT -m geoip --src-cc CN,RU,KP -j DROP

# 평판 기반 IP 차단 (Fail2ban)
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[http-flood]
enabled = true
filter = http-flood
logpath = /var/log/nginx/access.log
maxretry = 100
findtime = 60
bantime = 3600
```

### 2. Reflection Attack

**공격 원리:**
- 제3자 서버를 반사판으로 이용
- 소스 IP 위조하여 응답을 피해자에게 전송

**방어 전략:**
```bash
# BCP38 구현 (ISP 레벨)
# 소스 IP 검증
iptables -A INPUT -s 10.0.0.0/8 -i eth0 -j DROP      # 사설 IP 차단
iptables -A INPUT -s 172.16.0.0/12 -i eth0 -j DROP
iptables -A INPUT -s 192.168.0.0/16 -i eth0 -j DROP

# Reverse Path Filtering
echo 1 > /proc/sys/net/ipv4/conf/all/rp_filter
```

---

## 고급 공격 기법

### 1. Low and Slow Attacks

**R.U.D.Y (R-U-Dead-Yet):**
```
[의사코드 - 공격 원리 이해용]

1. 대상 서버에 TCP 연결
2. POST 요청 전송, Content-Length를 매우 크게 설정 (예: 1,000,000 바이트)
3. 실제 데이터는 1바이트씩 1초 간격으로 전송
4. 서버는 Content-Length만큼 데이터 수신 대기 → 스레드/커넥션 고갈
```

**방어:**
```nginx
client_body_timeout 10s;
client_header_timeout 10s;
```

### 2. Protocol Exploitation

**TCP Window Attack:**
- TCP 윈도우 크기를 0으로 설정
- 데이터 전송 중단

**방어:**
```bash
# TCP 윈도우 스케일링 조정
echo 'net.ipv4.tcp_window_scaling = 1' >> /etc/sysctl.conf
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
```

---

## 방어 전략

### 1. 네트워크 레벨 방어

**iptables 종합 설정:**
```bash
#!/bin/bash
# DDoS 방어 iptables 스크립트

# 기본 정책
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 루프백 허용
iptables -A INPUT -i lo -j ACCEPT

# 기존 연결 허용
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SYN Flood 방어
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# UDP Flood 방어
iptables -A INPUT -p udp -m limit --limit 50/sec --limit-burst 100 -j ACCEPT
iptables -A INPUT -p udp -j DROP

# ICMP Flood 방어
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/sec -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

# Port Scan 방어
iptables -A INPUT -m recent --name portscan --rcheck --seconds 86400 -j DROP
iptables -A INPUT -m recent --name portscan --remove
iptables -A INPUT -p tcp -m tcp --dport 139 -m recent --name portscan --set -j LOG --log-prefix "portscan:"
iptables -A INPUT -p tcp -m tcp --dport 139 -m recent --name portscan --set -j DROP

# SSH 브루트포스 방어
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set --name SSH
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 --rttl --name SSH -j DROP

# 허용할 서비스
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
```

### 2. 애플리케이션 레벨 방어

**Nginx 종합 설정:**
```nginx
http {
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=global:10m rate=100r/s;
    
    # Connection Limiting
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    # 기본 보안 설정
    client_body_timeout 10s;
    client_header_timeout 10s;
    send_timeout 10s;
    keepalive_timeout 30s;
    
    client_max_body_size 1m;
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    
    server {
        listen 80;
        
        # 전역 rate limiting
        limit_req zone=global burst=200 nodelay;
        limit_conn addr 10;
        
        # 특정 경로 보호
        location /login {
            limit_req zone=login burst=5 nodelay;
        }
        
        location /api/ {
            limit_req zone=api burst=20 nodelay;
        }
        
        # 악성 User-Agent 차단
        if ($http_user_agent ~* (bot|crawler|spider|scraper)) {
            return 403;
        }
        
        # 빈 User-Agent 차단
        if ($http_user_agent = "") {
            return 403;
        }
    }
}
```

### 3. 시스템 레벨 최적화

**sysctl 튜닝:**
```bash
# /etc/sysctl.conf

# TCP 설정
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl = 15

# 네트워크 버퍼
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.netdev_max_backlog = 5000
net.core.somaxconn = 4096

# IP 설정
net.ipv4.ip_forward = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# 파일 디스크립터
fs.file-max = 65536
```

### 4. 클라우드 기반 방어

**AWS Shield + CloudFront:**
```yaml
# CloudFormation 템플릿
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt LoadBalancer.DNSName
            Id: ALB
            CustomOriginConfig:
              HTTPPort: 80
              OriginProtocolPolicy: http-only
        
        DefaultCacheBehavior:
          TargetOriginId: ALB
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # Managed-CachingDisabled
          
        WebACLId: !Ref WebACL
        
  WebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Rules:
        - Name: RateLimitRule
          Priority: 1
          Statement:
            RateBasedStatement:
              Limit: 2000
              AggregateKeyType: IP
          Action:
            Block: {}
```

---

## 모니터링 및 탐지

### 1. 실시간 모니터링

**네트워크 트래픽 모니터링:**
```bash
#!/bin/bash
# DDoS 탐지 스크립트

# 패킷 수 모니터링
while true; do
    PPS=$(cat /proc/net/dev | grep eth0 | awk '{print $2}')
    sleep 1
    PPS_NEW=$(cat /proc/net/dev | grep eth0 | awk '{print $2}')
    PPS_DIFF=$((PPS_NEW - PPS))
    
    if [ $PPS_DIFF -gt 10000 ]; then
        echo "$(date): High PPS detected: $PPS_DIFF" >> /var/log/ddos.log
        # 알림 발송
        curl -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
             -d "chat_id=$CHAT_ID&text=DDoS Alert: $PPS_DIFF PPS"
    fi
done
```

### 2. 로그 분석

**Fail2ban 설정:**
```ini
# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[http-flood]
enabled = true
filter = http-flood
logpath = /var/log/nginx/access.log
maxretry = 100
findtime = 60
bantime = 3600

[slowloris]
enabled = true
filter = slowloris
logpath = /var/log/nginx/access.log
maxretry = 5
findtime = 300
bantime = 7200
```

**필터 정의:**
```ini
# /etc/fail2ban/filter.d/http-flood.conf
[Definition]
failregex = ^<HOST> -.*"(GET|POST).*" (200|404|301|302) .*$
ignoreregex =

# /etc/fail2ban/filter.d/slowloris.conf
[Definition]
failregex = ^<HOST> -.*".*" 408 .*$
ignoreregex =
```

### 3. 자동 대응 시스템

> 🟡 **주의:** 아래 자동 차단 스크립트는 참고용입니다. 운영 환경에서는 오탐으로 정상 트래픽이 차단될 수 있으므로 반드시 화이트리스트 설정과 테스트 후 적용하세요.

**Python 기반 자동 차단:**
```python
#!/usr/bin/env python3
import subprocess
import time
import re
from collections import defaultdict

class DDoSDetector:
    def __init__(self):
        self.ip_counts = defaultdict(int)
        self.blocked_ips = set()
        
    def analyze_logs(self):
        # nginx 로그 분석
        with open('/var/log/nginx/access.log', 'r') as f:
            for line in f.readlines()[-1000:]:  # 최근 1000줄
                ip = re.match(r'^(\d+\.\d+\.\d+\.\d+)', line)
                if ip:
                    self.ip_counts[ip.group(1)] += 1
    
    def block_suspicious_ips(self):
        for ip, count in self.ip_counts.items():
            if count > 100 and ip not in self.blocked_ips:  # 임계값 초과
                subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
                self.blocked_ips.add(ip)
                print(f"Blocked IP: {ip} (requests: {count})")
    
    def run(self):
        while True:
            self.ip_counts.clear()
            self.analyze_logs()
            self.block_suspicious_ips()
            time.sleep(60)

if __name__ == "__main__":
    detector = DDoSDetector()
    detector.run()
```

---

## Cloudflare WAF & Rate Limiting

### WAF (Web Application Firewall)

L7 공격과 웹 취약점 공격을 동시에 방어.

```
┌──────────┐     ┌───────────────────┐     ┌────────────┐
│  Client  │────>│ Cloudflare WAF    │────>│ IDC Server │
└──────────┘     │ - OWASP Rules     │     └────────────┘
                 │ - Custom Rules    │                   
                 │ - Bot Management  │                   
                 │ - Rate Limiting   │                   
                 └───────────────────┘                   
```

| 기능                | Free | Pro ($20/월) | Business ($200/월) | Enterprise |
|---------------------|------|--------------|--------------------|------------|
| Managed Ruleset     | 기본 | ✅           | ✅                 | ✅         |
| OWASP Core Ruleset  | ❌   | ✅           | ✅                 | ✅         |
| Custom WAF Rules    | 5개  | 20개         | 100개              | 무제한     |
| Rate Limiting Rules | 1개  | 2개          | 5개                | 무제한     |
| Bot Management      | 기본 | 기본         | 기본               | 고급       |
| API Shield          | ❌   | ❌           | ❌                 | ✅         |

### Cloudflare Rate Limiting 설정 예시

| 보호 대상      | 규칙 예시         | 임계값         |
|----------------|-------------------|----------------|
| 로그인 페이지  | `/login` URI 매칭 | 5 req/10초/IP  |
| API 엔드포인트 | `/api/*` 패턴     | 100 req/분/IP  |
| 전체 사이트    | 모든 요청         | 1000 req/분/IP |
| 검색 기능      | `/search` URI     | 10 req/분/IP   |

### WAF + DDoS 조합 전략

| 공격 시나리오        | 1차 방어                | 2차 방어                |
|----------------------|-------------------------|-------------------------|
| 대규모 L3/L4 DDoS    | Cloudflare Proxy (자동) | ISP 클린존              |
| HTTP Flood           | Rate Limiting           | WAF Custom Rule (차단)  |
| Slowloris            | Cloudflare Proxy (자동) | 서버 timeout 설정       |
| SQL Injection + DDoS | WAF Managed Rule        | Rate Limiting           |
| Bot 크롤링 공격      | Bot Management          | Rate Limiting           |
| API 남용             | Rate Limiting           | API Shield (Enterprise) |

---

## 공격 유형별 Cloudflare 서비스 매핑

| 공격 유형         | Cloudflare Proxy | Spectrum | Magic Transit | ISP 클린존 | WAF | Rate Limiting |
|-------------------|------------------|----------|---------------|------------|-----|---------------|
| SYN Flood         | ✅               | ✅       | ✅            | ✅         | -   | -             |
| UDP Flood         | -                | ✅       | ✅            | ✅         | -   | -             |
| DNS Amplification | ✅               | ✅       | ✅            | ✅         | -   | -             |
| NTP Amplification | -                | ✅       | ✅            | ✅         | -   | -             |
| HTTP Flood        | ✅               | -        | ✅            | △          | ✅  | ✅            |
| Slowloris         | ✅               | -        | -             | -          | ✅  | -             |
| API Abuse         | ✅               | -        | -             | -          | ✅  | ✅            |
| ICMP Flood        | -                | -        | ✅            | ✅         | -   | -             |

> L3/L4 공격은 대역폭 소모형 → 네트워크 레벨 방어 (Magic Transit, ISP 클린존)
> L7 공격은 애플리케이션 레벨 → WAF + Rate Limiting 필수

---

## 국내 IDC 업체별 DDoS 방어 현황

### ISP 제공 DDoS 방어 서비스

| ISP          | 서비스명         | 기본 방어               | 유료 방어       | 비고                |
|--------------|------------------|-------------------------|-----------------|---------------------|
| KT           | DDoS 방어 서비스 | 회선 기본 포함 (소규모) | ~50만\~200만/월 | IDC 회선 부가서비스 |
| SK브로드밴드 | 클린존           | 기본 탐지               | 별도 협의       | 전용 Scrubbing 센터 |
| LG U+        | DDoS 차단        | 기본 탐지               | 별도 협의       | IDC 고객 대상       |

### IDC 자체 방어

| IDC              | 기본 제공           | 추가 옵션        |
|------------------|---------------------|------------------|
| KINX             | 기본 방어 없음 (IX) | 고객이 직접 구성 |
| 가비아 IDC       | 기본 방어 포함      | 상위 플랜        |
| 카페24 IDC       | 기본 방어 포함      | 트래픽 기반 과금 |
| 코리아서버호스팅 | 기본 방어 포함      | 전용 방어 서비스 |

### ISP 클린존 vs Cloudflare 비교

| 항목      | ISP 클린존                  | Cloudflare                      |
|-----------|-----------------------------|---------------------------------|
| 방어 계층 | L3/L4 위주                  | L3/L4/L7 전체                   |
| 설정      | ISP에 요청                  | 셀프서비스 (대시보드)           |
| 반응 속도 | ISP 대응 시간 의존          | 자동 (수초 이내)                |
| L7 방어   | 제한적                      | WAF + Rate Limiting             |
| 비용      | ~50만\~200만/월             | Free~ (웹), $20\~/월 (Pro)      |
| 장점      | 별도 설정 불필요, 회선 레벨 | 글로벌 PoP, L7 방어, 셀프서비스 |
| 단점      | L7 방어 약함, 커스텀 어려움 | 원본 IP 노출 시 우회 가능       |

### 권장 다층 방어 조합

```
┌────────────────────────────────────────────────┐
│ Recommended DDoS Defense Architecture          │
│────────────────────────────────────────────────│
│ [Layer 1] ISP Clean Zone (L3/L4 basic)         │
│ +                                              │
│ [Layer 2] Cloudflare Proxy (L7 + WAF)          │
│ +                                              │
│ [Layer 3] Host-level (iptables, fail2ban)      │
│                                                │
└────────────────────────────────────────────────┘
```

- 1단계: ISP 회선 부가서비스로 대용량 L3/L4 공격 1차 필터링
- 2단계: Cloudflare로 L7 공격 방어 + WAF + Rate Limiting
- 3단계: 서버에서 최종 방어 (IP 차단, 커넥션 제한 등)

---

## References

### Cloudflare WAF / Rate Limiting

- Cloudflare WAF: <https://www.cloudflare.com/waf/>
- Cloudflare Rate Limiting: <https://www.cloudflare.com/rate-limiting/>
- Cloudflare Bot Management: <https://www.cloudflare.com/products/bot-management/>

### 국내 IDC / ISP

- KT IDC: <https://cloud.kt.com/>
- KINX: <https://www.kinx.net/>
- 가비아 IDC: <https://idc.gabia.com/>

---

## 결론

DDoS 공격은 지속적으로 진화하고 있으며, 효과적인 방어를 위해서는:

1. **다층 방어**: ISP 클린존(L3/L4) + Cloudflare(L7) + 서버 자체 방어
2. **실시간 모니터링**: 공격 패턴의 조기 탐지
3. **자동화된 대응**: 빠른 차단 및 완화 조치
4. **클라우드 서비스 활용**: 대규모 공격에 대한 전문적 방어
5. **정기적인 업데이트**: 새로운 공격 기법에 대한 대응

이 가이드의 설정들을 환경에 맞게 조정하여 사용하시기 바랍니다.
