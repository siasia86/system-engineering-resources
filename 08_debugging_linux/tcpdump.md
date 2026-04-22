# tcpdump - 네트워크 패킷 캡처 도구

## tcpdump란?

**Packet Capture Tool** - 네트워크 인터페이스를 통과하는 패킷을 캡처하고 분석하는 명령줄 도구입니다.

## 주요 기능

- 실시간 패킷 캡처
- 패킷 필터링
- 파일로 저장/읽기
- 프로토콜 분석
- 네트워크 디버깅

## 설치

```bash
# Ubuntu/Debian
sudo apt-get install tcpdump

# CentOS/RHEL
sudo yum install tcpdump

# 버전 확인
tcpdump --version
```

## 기본 사용법

### 인터페이스 확인

```bash
# 사용 가능한 인터페이스 목록
tcpdump -D

# 출력:
# 1.eth0 [Up, Running]
# 2.lo [Up, Running, Loopback]
# 3.any (Pseudo-device that captures on all interfaces)
```

### 기본 캡처

```bash
# 기본 인터페이스에서 캡처
sudo tcpdump

# 특정 인터페이스
sudo tcpdump -i eth0

# 모든 인터페이스
sudo tcpdump -i any

# 개수 제한
sudo tcpdump -c 10  # 10개만
```

## 필터링

### 호스트 필터

```bash
# 특정 호스트
sudo tcpdump host 192.168.1.100

# 소스 호스트
sudo tcpdump src host 192.168.1.100

# 목적지 호스트
sudo tcpdump dst host 192.168.1.100

# 호스트 제외
sudo tcpdump not host 192.168.1.100
```

### 포트 필터

```bash
# 특정 포트
sudo tcpdump port 80

# 소스 포트
sudo tcpdump src port 80

# 목적지 포트
sudo tcpdump dst port 80

# 포트 범위
sudo tcpdump portrange 80-443

# 여러 포트
sudo tcpdump port 80 or port 443
```

### 프로토콜 필터

```bash
# TCP만
sudo tcpdump tcp

# UDP만
sudo tcpdump udp

# ICMP만 (ping)
sudo tcpdump icmp

# ARP만
sudo tcpdump arp
```

### 네트워크 필터

```bash
# 특정 네트워크
sudo tcpdump net 192.168.1.0/24

# 소스 네트워크
sudo tcpdump src net 192.168.1.0/24

# 목적지 네트워크
sudo tcpdump dst net 192.168.1.0/24
```

## 복합 필터

### AND 조건

```bash
# 호스트 AND 포트
sudo tcpdump host 192.168.1.100 and port 80

# TCP AND 포트 80
sudo tcpdump tcp and port 80
```

### OR 조건

```bash
# 포트 80 OR 443
sudo tcpdump port 80 or port 443

# 호스트 OR 호스트
sudo tcpdump host 192.168.1.100 or host 192.168.1.101
```

### NOT 조건

```bash
# 포트 22 제외
sudo tcpdump not port 22

# SSH 제외하고 캡처
sudo tcpdump not port 22 and not port 2222
```

### 복잡한 조건

```bash
# HTTP 트래픽만
sudo tcpdump 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'

# SYN 패킷만
sudo tcpdump 'tcp[tcpflags] & (tcp-syn) != 0'

# HTTP GET 요청
sudo tcpdump -s 0 -A 'tcp dst port 80 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420'
```

## 출력 옵션

### 상세 출력

```bash
# 기본 출력
sudo tcpdump

# 상세 출력 (-v)
sudo tcpdump -v

# 더 상세 (-vv)
sudo tcpdump -vv

# 최대 상세 (-vvv)
sudo tcpdump -vvv
```

### 패킷 내용

```bash
# HEX 출력
sudo tcpdump -x

# HEX + ASCII
sudo tcpdump -X

# ASCII만
sudo tcpdump -A

# 전체 패킷 캡처
sudo tcpdump -s 0
```

### 타임스탬프

```bash
# 절대 시간
sudo tcpdump -tttt

# 상대 시간
sudo tcpdump -ttt

# 마이크로초
sudo tcpdump -tttttt
```

## 파일 저장 및 읽기

### 저장

```bash
# 파일로 저장
sudo tcpdump -w capture.pcap

# 크기 제한 (MB)
sudo tcpdump -w capture.pcap -C 100

# 파일 개수 제한
sudo tcpdump -w capture.pcap -C 100 -W 5

# 압축 저장
sudo tcpdump -w - | gzip > capture.pcap.gz
```

### 읽기

```bash
# 파일 읽기
tcpdump -r capture.pcap

# 필터 적용
tcpdump -r capture.pcap port 80

# 상세 출력
tcpdump -r capture.pcap -vv
```

## 실전 예제

### 예제 1: HTTP 트래픽 캡처

```bash
# HTTP 요청/응답 캡처
sudo tcpdump -i eth0 -A -s 0 'tcp port 80'

# GET 요청만
sudo tcpdump -i eth0 -A -s 0 'tcp port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420)'
```

### 예제 2: DNS 쿼리 모니터링

```bash
# DNS 쿼리 캡처
sudo tcpdump -i eth0 -n port 53

# 특정 도메인
sudo tcpdump -i eth0 -n port 53 | grep google.com
```

### 예제 3: 특정 IP 간 통신

```bash
# 두 호스트 간 통신
sudo tcpdump host 192.168.1.100 and host 192.168.1.101

# 파일로 저장
sudo tcpdump -w comm.pcap host 192.168.1.100 and host 192.168.1.101
```

### 예제 4: SYN Flood 감지

```bash
# SYN 패킷 모니터링
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0'

# 개수 세기
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0' | wc -l
```

### 예제 5: 느린 연결 디버깅

```bash
# 재전송 패킷 확인
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0'

# RTT 측정
sudo tcpdump -i eth0 -ttt host 192.168.1.100
```

## 고급 사용법

### 패킷 크기 필터

```bash
# 큰 패킷만 (1000바이트 이상)
sudo tcpdump 'ip[2:2] > 1000'

# 작은 패킷만
sudo tcpdump 'ip[2:2] < 100'
```

### TCP 플래그 필터

```bash
# SYN 패킷
sudo tcpdump 'tcp[tcpflags] & tcp-syn != 0'

# FIN 패킷
sudo tcpdump 'tcp[tcpflags] & tcp-fin != 0'

# RST 패킷
sudo tcpdump 'tcp[tcpflags] & tcp-rst != 0'

# SYN-ACK 패킷
sudo tcpdump 'tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)'
```

### VLAN 필터

```bash
# VLAN 100
sudo tcpdump vlan 100

# VLAN 100의 HTTP
sudo tcpdump vlan 100 and port 80
```

## 실무 활용

### 1. 네트워크 문제 진단

```bash
# 연결 문제 확인
sudo tcpdump -i eth0 host 192.168.1.100 and port 80

# 패킷 손실 확인
sudo tcpdump -i eth0 -c 1000 | grep -c "dup ack"
```

### 2. 보안 감사

```bash
# 의심스러운 포트 스캔
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0' | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn

# 외부 연결 모니터링
sudo tcpdump -i eth0 'not src net 192.168.0.0/16'
```

### 3. 성능 분석

```bash
# 대역폭 사용량
sudo tcpdump -i eth0 -w - | pv > /dev/null

# 패킷 크기 분포
sudo tcpdump -i eth0 -nn | awk '{print $NF}' | sort | uniq -c
```

### 4. 애플리케이션 디버깅

```bash
# API 호출 추적
sudo tcpdump -i eth0 -A -s 0 'host api.example.com and port 443'

# 데이터베이스 쿼리
sudo tcpdump -i lo -A -s 0 'port 3306'
```

### 5. 실시간 모니터링

```bash
# 실시간 통계
sudo tcpdump -i eth0 -nn | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn

# 대시보드
watch -n 1 'sudo tcpdump -i eth0 -c 100 -nn 2>/dev/null | tail -20'
```

## 스크립트 예제

### 자동 캡처 스크립트

```bash
#!/bin/bash
# auto_capture.sh

INTERFACE="eth0"
DURATION=60
OUTPUT="capture_$(date +%Y%m%d_%H%M%S).pcap"

echo "Capturing on $INTERFACE for $DURATION seconds..."
sudo timeout $DURATION tcpdump -i $INTERFACE -w $OUTPUT

echo "Capture saved to $OUTPUT"
ls -lh $OUTPUT
```

### 트래픽 분석 스크립트

```bash
#!/bin/bash
# analyze_traffic.sh

PCAP_FILE=$1

echo "=== Top Talkers ==="
tcpdump -r $PCAP_FILE -nn | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -10

echo ""
echo "=== Top Ports ==="
tcpdump -r $PCAP_FILE -nn | awk '{print $5}' | cut -d. -f5 | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
```

## 트러블슈팅

### 문제 1: "Permission denied"

```bash
# 해결: sudo 사용
sudo tcpdump

# 또는 권한 부여
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
```

### 문제 2: "No suitable device found"

```bash
# 인터페이스 확인
ip link show

# 올바른 인터페이스 지정
sudo tcpdump -i eth0
```

### 문제 3: 출력이 너무 많음

```bash
# 필터 사용
sudo tcpdump port 80

# 개수 제한
sudo tcpdump -c 100

# 파일로 저장
sudo tcpdump -w capture.pcap
```

## 성능 최적화

```bash
# 버퍼 크기 증가
sudo tcpdump -B 4096

# 즉시 쓰기 비활성화
sudo tcpdump -U

# 패킷 크기 제한
sudo tcpdump -s 96  # 헤더만
```

## Wireshark와 연동

```bash
# tcpdump로 캡처, Wireshark로 분석
sudo tcpdump -i eth0 -w - | wireshark -k -i -

# 파일 변환
sudo tcpdump -r capture.pcap -w capture.pcapng
```

## 관련 도구

| 도구          | 용도              |
|---------------|-------------------|
| **tcpdump**   | 패킷 캡처 (CLI)   |
| **wireshark** | 패킷 분석 (GUI)   |
| **tshark**    | Wireshark CLI     |
| **ngrep**     | 네트워크 grep     |
| **tcpflow**   | TCP 스트림 재구성 |

## 요약

**tcpdump의 강점:**
- 실시간 패킷 캡처
- 강력한 필터링
- 낮은 리소스 사용
- 스크립트 자동화

**주요 옵션:**
- `-i` - 인터페이스
- `-w` - 파일 저장
- `-r` - 파일 읽기
- `-c` - 개수 제한
- `-A` - ASCII 출력

**언제 사용?**
- 네트워크 문제 진단
- 보안 감사
- 성능 분석
- 프로토콜 디버깅
