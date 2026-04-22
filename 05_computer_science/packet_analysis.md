# 패킷 분석 (Packet Analysis)

## 목차
1. [IP 헤더 (IPv4)](#ip-헤더-ipv4)
2. [TCP 헤더](#tcp-헤더)
3. [UDP 헤더](#udp-헤더)
4. [PROXY Protocol v2](#proxy-protocol-v2)
5. [패킷 분석 도구](#패킷-분석-도구)

---

## IP 헤더 (IPv4)

### 구조 (20-60 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────┬───────────────┬───────────────────────────────┐
│ Version | IHL │ Type of Svc   │        Total Length           │
├───────────────┴───────────────┼───────────────────────────────┤
│         Identification        │ Flags |   Fragment Offset     │
├───────────────────────────────┼───────────────────────────────┤
│ Time to Live  │   Protocol    │      Header Checksum          │
├───────────────────────────────┴───────────────────────────────┤
│                       Source Address                          │
├───────────────────────────────────────────────────────────────┤
│                    Destination Address                        │
├───────────────────────────────────────────────────────────────┤
│                    Options (if IHL > 5)                       │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                      | 크기    | 설명                                                    |
|---------------------------|---------|---------------------------------------------------------|
| **Version**               | 4 bits  | IP 버전 (IPv4 = 4)                                      |
| **IHL**                   | 4 bits  | 헤더 길이 (Internet Header Length, 5-15, 단위: 4 bytes) |
| **Type of Service (TOS)** | 8 bits  | 서비스 품질 (QoS)                                       |
| **Total Length**          | 16 bits | 전체 패킷 길이 (헤더 + 데이터, 최대 65,535 bytes)       |
| **Identification**        | 16 bits | 패킷 식별자 (단편화 시 재조립용)                        |
| **Flags**                 | 3 bits  | DF(Don't Fragment), MF(More Fragments)                  |
| **Fragment Offset**       | 13 bits | 단편화된 패킷의 위치                                    |
| **Time to Live (TTL)**    | 8 bits  | 패킷 생존 시간 (홉 수, 0이 되면 폐기)                   |
| **Protocol**              | 8 bits  | 상위 프로토콜 (6=TCP, 17=UDP, 1=ICMP)                   |
| **Header Checksum**       | 16 bits | 헤더 오류 검사                                          |
| **Source Address**        | 32 bits | 출발지 IP 주소                                          |
| **Destination Address**   | 32 bits | 목적지 IP 주소                                          |
| **Options**               | 가변    | 선택적 옵션 (보안, 라우팅 등)                           |

### 예시 (Wireshark)

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

```
Internet Protocol Version 4, Src: 192.168.1.100, Dst: 10.0.0.1
    0100 .... = Version: 4
    .... 0101 = Header Length: 20 bytes (5)
    Differentiated Services Field: 0x00
    Total Length: 60
    Identification: 0x1234 (4660)
    Flags: 0x4000, Don't fragment
        0... .... .... .... = Reserved bit: Not set
        .1.. .... .... .... = Don't fragment: Set
        ..0. .... .... .... = More fragments: Not set
    Fragment Offset: 0
    Time to Live: 64
    Protocol: TCP (6)
    Header Checksum: 0xabcd [validation disabled]
    Source Address: 192.168.1.100
    Destination Address: 10.0.0.1
```

---

## TCP 헤더

### 구조 (20-60 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────┬───────────────────────────────┐
│        Source Port            │      Destination Port         │
├───────────────────────────────┴───────────────────────────────┤
│                      Sequence Number                          │
├───────────────────────────────────────────────────────────────┤
│                   Acknowledgment Number                       │
├───────────────────────────────────────────────────────────────┤
│ Data  |       | C E U A P R S F |                             │
│ Offset| Rsrvd | W C R C S S Y I |          Window             │
│       |       | R E G K H T N N |                             │
├───────────────────────────────────────────────────────────────┤
│         Checksum              │       Urgent Pointer          │
├───────────────────────────────┴───────────────────────────────┤
│                Options (if Data Offset > 5)                   │
├───────────────────────────────────────────────────────────────┤
│                            Data                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                      | 크기    | 설명                                     |
|---------------------------|---------|------------------------------------------|
| **Source Port**           | 16 bits | 출발지 포트 번호 (0-65535)               |
| **Destination Port**      | 16 bits | 목적지 포트 번호 (0-65535)               |
| **Sequence Number**       | 32 bits | 순서 번호 (데이터 바이트의 첫 번째 번호) |
| **Acknowledgment Number** | 32 bits | 확인 응답 번호 (다음에 받을 바이트 번호) |
| **Data Offset**           | 4 bits  | TCP 헤더 길이 (5-15, 단위: 4 bytes)      |
| **Reserved**              | 3 bits  | 예약 (0으로 설정)                        |
| **Flags**                 | 9 bits  | 제어 플래그 (아래 참조)                  |
| **Window**                | 16 bits | 수신 윈도우 크기 (흐름 제어)             |
| **Checksum**              | 16 bits | 헤더 + 데이터 오류 검사                  |
| **Urgent Pointer**        | 16 bits | 긴급 데이터 포인터 (URG 플래그 설정 시)  |
| **Options**               | 가변    | 선택적 옵션 (MSS, Window Scale 등)       |

### TCP 플래그 (Flags)

| 플래그  | 이름                      | 설명                 |
|---------|---------------------------|----------------------|
| **FIN** | Finish                    | 연결 종료 요청       |
| **SYN** | Synchronize               | 연결 설정 요청       |
| **RST** | Reset                     | 연결 강제 종료       |
| **PSH** | Push                      | 데이터 즉시 전달     |
| **ACK** | Acknowledge               | 확인 응답            |
| **URG** | Urgent                    | 긴급 데이터          |
| **ECE** | ECN-Echo                  | ECN 지원 (혼잡 제어) |
| **CWR** | Congestion Window Reduced | 혼잡 윈도우 감소     |
| **NS**  | Nonce Sum                 | ECN 보호             |

### 플래그 조합

| 조합          | 의미                              |
|---------------|-----------------------------------|
| **SYN**       | 연결 요청 (3-Way Handshake 1단계) |
| **SYN + ACK** | 연결 수락 (3-Way Handshake 2단계) |
| **ACK**       | 확인 응답 (데이터 전송 중)        |
| **FIN**       | 연결 종료 요청                    |
| **FIN + ACK** | 연결 종료 확인                    |
| **RST**       | 연결 강제 종료                    |
| **PSH + ACK** | 데이터 즉시 전달 + 확인           |


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

### 예시 (Wireshark)

```
Transmission Control Protocol, Src Port: 54321, Dst Port: 80, Seq: 1, Ack: 1
    Source Port: 54321
    Destination Port: 80
    Sequence Number: 1    (relative sequence number)
    Acknowledgment Number: 1    (relative ack number)
    1000 .... = Header Length: 32 bytes (8)
    Flags: 0x018 (PSH, ACK)
        000. .... .... = Reserved: Not set
        ...0 .... .... = Nonce: Not set
        .... 0... .... = Congestion Window Reduced (CWR): Not set
        .... .0.. .... = ECN-Echo: Not set
        .... ..0. .... = Urgent: Not set
        .... ...1 .... = Acknowledgment: Set
        .... .... 1... = Push: Set
        .... .... .0.. = Reset: Not set
        .... .... ..0. = Syn: Not set
        .... .... ...0 = Fin: Not set
    Window: 65535
    Checksum: 0x1234 [unverified]
    Urgent Pointer: 0
    Options: (12 bytes), Maximum segment size, No-Operation (NOP), Window scale
```

---

## UDP 헤더

### 구조 (8 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────┬───────────────────────────────┐
│        Source Port            │      Destination Port         │
├───────────────────────────────┼───────────────────────────────┤
│          Length               │          Checksum             │
├───────────────────────────────┴───────────────────────────────┤
│                            Data                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                 | 크기    | 설명                                  |
|----------------------|---------|---------------------------------------|
| **Source Port**      | 16 bits | 출발지 포트 번호                      |
| **Destination Port** | 16 bits | 목적지 포트 번호                      |
| **Length**           | 16 bits | UDP 헤더 + 데이터 길이 (최소 8 bytes) |
| **Checksum**         | 16 bits | 헤더 + 데이터 오류 검사 (선택적)      |

### TCP vs UDP 비교

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

| 특성          | TCP                             | UDP                     |
|---------------|---------------------------------|-------------------------|
| **연결**      | 연결 지향 (Connection-oriented) | 비연결 (Connectionless) |
| **신뢰성**    | 신뢰성 보장 (재전송, 순서 보장) | 신뢰성 없음             |
| **속도**      | 느림 (오버헤드 큼)              | 빠름 (오버헤드 작음)    |
| **헤더 크기** | 20-60 bytes                     | 8 bytes                 |
| **용도**      | HTTP, FTP, SSH, SMTP            | DNS, DHCP, VoIP, 게임   |

---

## PROXY Protocol v2

### 개요

**목적:**
- 로드밸런서/프록시를 통과할 때 **원본 클라이언트 IP 보존**
- TCP/UDP 연결의 메타데이터 전달

**사용 사례:**
- AWS NLB → 백엔드 서버
- HAProxy → 애플리케이션 서버
- Nginx → 백엔드 서비스

---

### PROXY Protocol v2 헤더 구조

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                   Signature (12 bytes)                        │
│                   0x0D 0x0A 0x0D 0x0A 0x00 0x0D               │
│                   0x0A 0x51 0x55 0x49 0x54 0x0A               │
│                                                               │
├───────────────────────────────────────────────────────────────┘
│ Version | Cmd   |   AF  | Proto |      Address Length       |
├───────────────────────────────────────────────────────────────┐
│                                                               │
│                    Address Block                              │
│                   (variable length)                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

#### 1. Signature (12 bytes)

```
0x0D 0x0A 0x0D 0x0A 0x00 0x0D 0x0A 0x51 0x55 0x49 0x54 0x0A
\r   \n   \r   \n   \0   \r   \n   Q    U    I    T    \n
```

**목적:** PROXY Protocol v2 식별

#### 2. Version and Command (1 byte)

```
7 6 5 4 | 3 2 1 0
Version | Command
```

| 필드        | 값  | 설명                 |
|-------------|-----|----------------------|
| **Version** | 0x2 | PROXY Protocol v2    |
| **Command** | 0x0 | LOCAL (health check) |
|             | 0x1 | PROXY (실제 연결)    |

#### 3. Address Family and Protocol (1 byte)

```
7 6 5 4 | 3 2 1 0
  AF    |  Proto
```

**Address Family (AF):**

| 값  | 설명                |
|-----|---------------------|
| 0x0 | UNSPEC (지정 안 함) |
| 0x1 | INET (IPv4)         |
| 0x2 | INET6 (IPv6)        |
| 0x3 | UNIX (Unix socket)  |

**Protocol:**

| 값  | 설명         |
|-----|--------------|
| 0x0 | UNSPEC       |
| 0x1 | STREAM (TCP) |
| 0x2 | DGRAM (UDP)  |

#### 4. Address Length (2 bytes)

주소 블록의 길이 (bytes)

#### 5. Address Block (가변 길이)

**IPv4 + TCP (12 bytes):**
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────────────────────────────────────┐
│                   Source IPv4 Address                         │
├───────────────────────────────────────────────────────────────┤
│                 Destination IPv4 Address                      │
├───────────────────────────────────────────────────────────────┤
│        Source Port            │      Destination Port         │
└───────────────────────────────┴───────────────────────────────┘
```

**IPv6 + TCP (36 bytes):**
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                   Source IPv6 Address                         │
│                       (16 bytes)                              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                 Destination IPv6 Address                      │
│                       (16 bytes)                              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│        Source Port            │      Destination Port         │
└───────────────────────────────┴───────────────────────────────┘
```

---

### PROXY Protocol v2 예시

#### 예시 1: IPv4 + TCP

```
Hex Dump:
0D 0A 0D 0A 00 0D 0A 51 55 49 54 0A  |  Signature
21                                    |  Version 2, PROXY command
11                                    |  AF=INET, Proto=STREAM
00 0C                                 |  Address length = 12 bytes
C0 A8 01 64                           |  Source IP: 192.168.1.100
0A 00 00 01                           |  Dest IP: 10.0.0.1
D4 31                                 |  Source Port: 54321
00 50                                 |  Dest Port: 80
```

**해석:**
- 클라이언트: 192.168.1.100:54321
- 서버: 10.0.0.1:80
- 프로토콜: TCP (IPv4)

#### 예시 2: IPv6 + TCP

```
Hex Dump:
0D 0A 0D 0A 00 0D 0A 51 55 49 54 0A  |  Signature
21                                    |  Version 2, PROXY command
21                                    |  AF=INET6, Proto=STREAM
00 24                                 |  Address length = 36 bytes
20 01 0D B8 00 00 00 00 00 00 00 00 00 00 00 01  |  Source IPv6
20 01 0D B8 00 00 00 00 00 00 00 00 00 00 00 02  |  Dest IPv6
D4 31                                 |  Source Port: 54321
00 50                                 |  Dest Port: 80
```

---

### PROXY Protocol v1 vs v2


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

# 사용 예시
hex_string = "0d0a0d0a000d0a515549540a2111000cc0a801640a000001d4310050"
hex_data = bytes.fromhex(hex_string)
parse_proxy_v2_from_tcpdump(hex_data)
```
| 특성          | v1                    | v2                   |
|---------------|-----------------------|----------------------|
| **형식**      | 텍스트 (ASCII)        | 바이너리             |
| **크기**      | 가변 (최대 107 bytes) | 고정 (최소 16 bytes) |
| **파싱**      | 느림 (문자열 파싱)    | 빠름 (바이너리)      |
| **확장성**    | 제한적                | TLV 확장 가능        |
| **IPv6 지원** | 제한적                | 완전 지원            |

**PROXY Protocol v1 예시:**
```
PROXY TCP4 192.168.1.100 10.0.0.1 54321 80\r\n
```

---

### 서버 측 구현

#### HAProxy 설정

```bash
# /etc/haproxy/haproxy.cfg

frontend game_frontend
    bind *:27015 accept-proxy  # PROXY Protocol 수신
    mode tcp
    default_backend game_servers

backend game_servers
    mode tcp
    server game1 10.0.1.10:27015 send-proxy-v2  # PROXY Protocol v2 전송
```

#### Nginx 설정

```nginx
# /etc/nginx/nginx.conf

stream {
    server {
        listen 80 proxy_protocol;  # PROXY Protocol 수신
        proxy_pass backend:80;
        
        # 원본 IP 로깅
        proxy_protocol on;
    }
}

http {
    server {
        listen 80 proxy_protocol;
        
        # 원본 IP 사용
        real_ip_header proxy_protocol;
        set_real_ip_from 10.0.0.0/8;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header X-Real-IP $proxy_protocol_addr;
            proxy_set_header X-Forwarded-For $proxy_protocol_addr;
        }
    }
}
```

#### Python 파싱 예시

```python
import struct
import socket

def parse_proxy_v2(data):
    # Signature 확인
    signature = data[:12]
    if signature != b'\x0D\x0A\x0D\x0A\x00\x0D\x0A\x51\x55\x49\x54\x0A':
        raise ValueError("Invalid PROXY Protocol v2 signature")
    
    # Version and Command
    ver_cmd = data[12]
    version = (ver_cmd >> 4) & 0x0F
    command = ver_cmd & 0x0F
    
    if version != 2:
        raise ValueError(f"Unsupported version: {version}")
    
    # Address Family and Protocol
    fam_proto = data[13]
    family = (fam_proto >> 4) & 0x0F
    protocol = fam_proto & 0x0F
    
    # Address Length
    addr_len = struct.unpack('!H', data[14:16])[0]
    
    # Address Block
    addr_block = data[16:16+addr_len]
    
    if family == 0x1 and protocol == 0x1:  # IPv4 + TCP
        src_ip = socket.inet_ntoa(addr_block[0:4])
        dst_ip = socket.inet_ntoa(addr_block[4:8])
        src_port = struct.unpack('!H', addr_block[8:10])[0]
        dst_port = struct.unpack('!H', addr_block[10:12])[0]
        
        return {
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': 'TCP',
            'family': 'IPv4'
        }
    
    # 실제 데이터는 16 + addr_len 이후부터
    return data[16+addr_len:]

# 사용 예시
data = b'\x0D\x0A\x0D\x0A\x00\x0D\x0A\x51\x55\x49\x54\x0A' \
       b'\x21\x11\x00\x0C' \
       b'\xC0\xA8\x01\x64' \
       b'\x0A\x00\x00\x01' \
       b'\xD4\x31\x00\x50' \
       b'GET / HTTP/1.1\r\n...'

info = parse_proxy_v2(data)
print(f"Client: {info['src_ip']}:{info['src_port']}")
print(f"Server: {info['dst_ip']}:{info['dst_port']}")
```

---

## 패킷 분석 도구

### tcpdump

```bash
# 기본 캡처
tcpdump -i eth0

# 특정 포트
tcpdump -i eth0 port 80

# TCP SYN 패킷만
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# 파일로 저장
tcpdump -i eth0 -w capture.pcap

# 16진수 출력
tcpdump -i eth0 -X

# PROXY Protocol 캡처
tcpdump -i eth0 -X 'tcp port 80' | grep -A 20 "0d0a 0d0a 000d"
```

### Wireshark

**필터 예시:**
```
# TCP SYN 패킷
tcp.flags.syn == 1 && tcp.flags.ack == 0

# 특정 IP
ip.addr == 192.168.1.100

# HTTP GET 요청
http.request.method == "GET"

# TCP 재전송
tcp.analysis.retransmission

# PROXY Protocol
tcp contains 0d:0a:0d:0a:00:0d:0a:51:55:49:54:0a
```

### tshark (CLI Wireshark)

```bash
# TCP 플래그 표시
tshark -i eth0 -Y "tcp" -T fields -e ip.src -e tcp.srcport -e tcp.flags

# PROXY Protocol 파싱
tshark -r capture.pcap -Y "tcp" -x | grep -A 5 "0d0a0d0a"
```

### ngrep

```bash
# HTTP 요청 캡처
ngrep -q -W byline "^GET|^POST" tcp port 80

# PROXY Protocol 헤더 확인
ngrep -x -q "" tcp port 80
```

---

## 실전 패킷 분석 예시

### SYN Flood 공격 탐지

```bash
# SYN 패킷 카운트
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0' | wc -l

# 출발지 IP별 SYN 카운트
tcpdump -i eth0 -n 'tcp[tcpflags] & tcp-syn != 0' | \
  awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn
```

### PROXY Protocol 검증

```bash
# PROXY Protocol v2 헤더 확인
tcpdump -i eth0 -X port 80 | grep -A 10 "0d0a 0d0a 000d"

# Python으로 실시간 파싱
tcpdump -i eth0 -w - port 80 | python3 parse_proxy.py
```

### TCP 연결 상태 추적

```bash
# 특정 연결의 전체 흐름
tcpdump -i eth0 -nn 'host 192.168.1.100 and port 80'

# TCP 플래그별 필터
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'     # SYN
tcpdump -i eth0 'tcp[tcpflags] & tcp-fin != 0'     # FIN
tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'     # RST
```

---

## 참고 자료

- RFC 791: Internet Protocol (IPv4)
- RFC 793: Transmission Control Protocol (TCP)
- RFC 768: User Datagram Protocol (UDP)
- PROXY Protocol Specification v2: https://www.haproxy.org/download/2.0/doc/proxy-protocol.txt
- Wireshark User Guide: https://www.wireshark.org/docs/
- tcpdump Manual: https://www.tcpdump.org/manpages/tcpdump.1.html
