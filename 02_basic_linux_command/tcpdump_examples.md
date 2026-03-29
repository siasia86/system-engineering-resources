# IP 헤더에 tcpdump 예시 추가

## IP 헤더 tcpdump 예시 추가 내용:

### tcpdump 예시

```bash
# 기본 IP 패킷 캡처
tcpdump -i eth0 -n ip

# 특정 출발지 IP
tcpdump -i eth0 src 192.168.1.100

# 특정 목적지 IP
tcpdump -i eth0 dst 10.0.0.1

# TTL 값 확인 (16진수 출력)
tcpdump -i eth0 -X ip

# IP 단편화 패킷만
tcpdump -i eth0 'ip[6:2] & 0x1fff != 0'

# DF(Don't Fragment) 플래그 설정된 패킷
tcpdump -i eth0 'ip[6] & 0x40 != 0'
```

**출력 예시:**
```
15:30:45.123456 IP 192.168.1.100.54321 > 10.0.0.1.80: Flags [S], seq 1234567890, win 65535, length 0
    0x0000:  4500 003c 1234 4000 4006 abcd c0a8 0164  E..<.4@.@......d
    0x0010:  0a00 0001 d431 0050 499602d2 0000 0000  .....1.PI.......
```

---

# TCP 헤더에 tcpdump 예시 추가

## TCP 헤더 tcpdump 예시 추가 내용:

### tcpdump 예시

```bash
# TCP 패킷 캡처
tcpdump -i eth0 tcp

# SYN 패킷만
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# SYN+ACK 패킷
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)'

# FIN 패킷
tcpdump -i eth0 'tcp[tcpflags] & tcp-fin != 0'

# RST 패킷
tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'

# PSH+ACK 패킷 (데이터 전송)
tcpdump -i eth0 'tcp[tcpflags] & (tcp-push|tcp-ack) == (tcp-push|tcp-ack)'

# 특정 포트
tcpdump -i eth0 'tcp port 80'

# Sequence/Ack 번호 표시
tcpdump -i eth0 -S tcp

# 16진수 + ASCII 출력
tcpdump -i eth0 -X tcp port 80
```

**출력 예시:**
```
# SYN 패킷
15:30:45.123456 IP 192.168.1.100.54321 > 10.0.0.1.80: Flags [S], seq 1234567890, win 65535, options [mss 1460], length 0

# SYN+ACK 패킷
15:30:45.124567 IP 10.0.0.1.80 > 192.168.1.100.54321: Flags [S.], seq 9876543210, ack 1234567891, win 65535, options [mss 1460], length 0

# ACK 패킷
15:30:45.125678 IP 192.168.1.100.54321 > 10.0.0.1.80: Flags [.], ack 1, win 65535, length 0

# PSH+ACK (데이터)
15:30:45.126789 IP 192.168.1.100.54321 > 10.0.0.1.80: Flags [P.], seq 1:100, ack 1, win 65535, length 99
```

---

# UDP 헤더에 tcpdump 예시 추가

## UDP 헤더 tcpdump 예시 추가 내용:

### tcpdump 예시

```bash
# UDP 패킷 캡처
tcpdump -i eth0 udp

# 특정 포트
tcpdump -i eth0 'udp port 53'

# DNS 쿼리 (UDP 53)
tcpdump -i eth0 -n 'udp port 53'

# DHCP (UDP 67/68)
tcpdump -i eth0 'udp port 67 or udp port 68'

# 16진수 출력
tcpdump -i eth0 -X 'udp port 53'

# 길이 확인
tcpdump -i eth0 -v udp
```

**출력 예시:**
```
15:30:45.123456 IP 192.168.1.100.12345 > 8.8.8.8.53: 12345+ A? www.example.com. (33)
    0x0000:  4500 003d 1234 0000 4011 abcd c0a8 0164  E..=.4..@......d
    0x0010:  0808 0808 3039 0035 0029 1234 3039 0100  ....09.5.).409..
    0x0020:  0001 0000 0000 0000 0377 7777 0765 7861  .........www.exa
    0x0030:  6d70 6c65 0363 6f6d 0000 0100 01         mple.com.....

15:30:45.234567 IP 8.8.8.8.53 > 192.168.1.100.12345: 12345 1/0/0 A 93.184.216.34 (49)
```

---

# PROXY Protocol v2에 tcpdump 예시 추가

## PROXY Protocol v2 tcpdump 예시 추가 내용:

### tcpdump 예시

```bash
# PROXY Protocol 헤더 캡처
tcpdump -i eth0 -X 'tcp port 80'

# Signature 확인 (0x0d0a0d0a000d0a515549540a)
tcpdump -i eth0 -X 'tcp port 80' | grep -A 20 "0d0a 0d0a 000d"

# HAProxy에서 전송되는 패킷
tcpdump -i eth0 -X 'tcp port 80 and src 10.0.1.1'

# 16진수 전체 출력
tcpdump -i eth0 -XX 'tcp port 80' -c 1

# 파일로 저장 후 분석
tcpdump -i eth0 -w proxy.pcap 'tcp port 80'
tcpdump -r proxy.pcap -X | grep -A 30 "0d0a 0d0a"
```

**출력 예시:**
```
15:30:45.123456 IP 10.0.1.1.54321 > 10.0.2.1.80: Flags [P.], seq 1:100, ack 1, win 65535, length 99
    0x0000:  4500 0087 1234 4000 4006 abcd 0a00 0101  E....4@.@.......
    0x0010:  0a00 0201 d431 0050 1234 5678 9abc def0  .....1.P.4Vx....
    0x0020:  5018 ffff 1234 0000 0d0a 0d0a 000d 0a51  P....4.........Q
    0x0030:  5549 540a 2111 000c c0a8 0164 0a00 0001  UIT.!......d....
    0x0040:  d431 0050 4745 5420 2f20 4854 5450 2f31  .1.PGET./.HTTP/1
    0x0050:  2e31 0d0a 486f 7374 3a20 7777 772e 6578  .1..Host:.www.ex
    0x0060:  616d 706c 652e 636f 6d0d 0a0d 0a         ample.com....

해석:
0x0020: 0d0a 0d0a 000d 0a51 5549 540a  <- PROXY Protocol v2 Signature
0x0030: 21                              <- Version 2, PROXY command
0x0030:   11                            <- AF=INET, Proto=STREAM
0x0030:     000c                        <- Address length = 12 bytes
0x0034: c0a8 0164                       <- Source IP: 192.168.1.100
0x0038: 0a00 0001                       <- Dest IP: 10.0.0.1
0x003c: d431                            <- Source Port: 54321
0x003e: 0050                            <- Dest Port: 80
0x0040: 4745 5420...                    <- HTTP GET 요청 시작
```

### Python으로 PROXY Protocol 파싱

```python
#!/usr/bin/env python3
import socket
import struct

def parse_proxy_v2_from_tcpdump(hex_data):
    """
    tcpdump 16진수 출력에서 PROXY Protocol v2 파싱
    """
    # Signature 확인
    signature = bytes.fromhex('0d0a0d0a000d0a515549540a')
    
    if hex_data[:12] != signature:
        print("Not a PROXY Protocol v2 packet")
        return
    
    # Version and Command
    ver_cmd = hex_data[12]
    version = (ver_cmd >> 4) & 0x0F
    command = ver_cmd & 0x0F
    
    print(f"Version: {version}")
    print(f"Command: {'PROXY' if command == 1 else 'LOCAL'}")
    
    # Address Family and Protocol
    fam_proto = hex_data[13]
    family = (fam_proto >> 4) & 0x0F
    protocol = fam_proto & 0x0F
    
    family_str = {0x1: 'IPv4', 0x2: 'IPv6'}.get(family, 'Unknown')
    proto_str = {0x1: 'TCP', 0x2: 'UDP'}.get(protocol, 'Unknown')
    
    print(f"Family: {family_str}")
    print(f"Protocol: {proto_str}")
    
    # Address Length
    addr_len = struct.unpack('!H', hex_data[14:16])[0]
    print(f"Address Length: {addr_len} bytes")
    
    # IPv4 + TCP
    if family == 0x1 and protocol == 0x1:
        src_ip = socket.inet_ntoa(hex_data[16:20])
        dst_ip = socket.inet_ntoa(hex_data[20:24])
        src_port = struct.unpack('!H', hex_data[24:26])[0]
        dst_port = struct.unpack('!H', hex_data[26:28])[0]
        
        print(f"\nClient: {src_ip}:{src_port}")
        print(f"Server: {dst_ip}:{dst_port}")
        
        # 실제 데이터 시작 위치
        data_start = 16 + addr_len
        print(f"\nPayload starts at byte {data_start}")
        print(f"Payload: {hex_data[data_start:data_start+50]}")

# 사용 예시
hex_string = "0d0a0d0a000d0a515549540a2111000cc0a801640a000001d4310050"
hex_data = bytes.fromhex(hex_string)
parse_proxy_v2_from_tcpdump(hex_data)
```



---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-03-29

© 2026 siasia86. Licensed under CC BY 4.0.
