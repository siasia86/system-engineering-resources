# 네트워크 헤더 구조 (Network Headers)

## 목차

| 단계  | 섹션                                                                                                                                    |
|-------|-----------------------------------------------------------------------------------------------------------------------------------------|
| L2/L3 | [1. Ethernet 헤더](#1-ethernet-헤더-layer-2) / [2. ARP 헤더](#2-arp-헤더) / [3. IPv6 헤더](#3-ipv6-헤더) / [4. ICMP 헤더](#4-icmp-헤더) |
| 응용  | [5. DNS 헤더](#5-dns-헤더) / [6. HTTP 헤더](#6-http-헤더) / [7. TLS/SSL 헤더](#7-tlsssl-헤더)                                           |
| 터널  | [8. GRE 헤더](#8-gre-헤더) / [9. VXLAN 헤더](#9-vxlan-헤더) / [10. QUIC 헤더](#10-quic-헤더)                                            |
| 실전  | [11. 패킷 캡슐화 예시](#11-패킷-캡슐화-예시) / [12. 패킷 분석 명령어](#12-패킷-분석-명령어)                                             |

[⬆ 목차로 돌아가기](#목차)

---

## 1. Ethernet 헤더 (Layer 2)

### 구조 (14-18 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                  Destination MAC Address                      │
│                       (6 bytes)                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                    Source MAC Address                         │
│                       (6 bytes)                               │
├───────────────────────────────────────────────────────────────┤
│         EtherType             │                               │
├───────────────────────────────┘                               │
│                    Payload (46-1500 bytes)                    │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                | 크기    | 설명                                     |
|---------------------|---------|------------------------------------------|
| **Destination MAC** | 48 bits | 목적지 MAC 주소                          |
| **Source MAC**      | 48 bits | 출발지 MAC 주소                          |
| **EtherType**       | 16 bits | 상위 프로토콜 (0x0800=IPv4, 0x86DD=IPv6) |
| **Payload**         | 46-1500 | 상위 계층 데이터                         |

### EtherType 값

| 값     | 프로토콜                   |
|--------|----------------------------|
| 0x0800 | IPv4                       |
| 0x0806 | ARP                        |
| 0x86DD | IPv6                       |
| 0x8100 | VLAN-tagged frame (802.1Q) |
| 0x8847 | MPLS unicast               |
| 0x8848 | MPLS multicast             |

### VLAN 태그 (802.1Q)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────────────────────────────────────┐
│                  Destination MAC Address                      │
├───────────────────────────────────────────────────────────────┤
│                    Source MAC Address                         │
├───────────────────────────┬───────────────────────────────────┤
│    TPID (0x8100)          │  TCI (PCP│DEI│VLAN ID)            │
├───────────────────────────┴───┬───────────────────────────────┤
│         EtherType             │          Payload              │
└───────────────────────────────┴───────────────────────────────┘
```

**TCI (Tag Control Information):**
- **PCP** (3 bits): Priority Code Point (QoS 우선순위)
- **DEI** (1 bit): Drop Eligible Indicator
- **VLAN ID** (12 bits): VLAN 식별자 (0-4095)

### 예시 (tcpdump)

```
14:30:15.123456 aa:bb:cc:dd:ee:ff > 00:11:22:33:44:55, ethertype IPv4 (0x0800)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. ARP 헤더

### 구조 (28 bytes for IPv4)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────┬───────────────────────────────┐
│       Hardware Type           │       Protocol Type           │
├─────────────┬─────────────────┼───────────────────────────────┤
│ HW Addr Len │ Proto Addr Len  │          Operation            │
├─────────────┴─────────────────┴───────────────────────────────┤
│                                                               │
│                  Sender Hardware Address                      │
│                       (6 bytes)                               │
├───────────────────────────────────────────────────────────────┤
│                   Sender Protocol Address                     │
│                       (4 bytes)                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                  Target Hardware Address                      │
│                       (6 bytes)                               │
├───────────────────────────────────────────────────────────────┤
│                   Target Protocol Address                     │
│                       (4 bytes)                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                        | 크기    | 설명                         |
|-----------------------------|---------|------------------------------|
| **Hardware Type**           | 16 bits | 하드웨어 타입 (1=Ethernet)   |
| **Protocol Type**           | 16 bits | 프로토콜 타입 (0x0800=IPv4)  |
| **HW Address Length**       | 8 bits  | MAC 주소 길이 (6 bytes)      |
| **Protocol Address Length** | 8 bits  | IP 주소 길이 (4 bytes)       |
| **Operation**               | 16 bits | 동작 (1=Request, 2=Reply)    |
| **Sender Hardware Address** | 48 bits | 송신자 MAC 주소              |
| **Sender Protocol Address** | 32 bits | 송신자 IP 주소               |
| **Target Hardware Address** | 48 bits | 대상 MAC 주소 (Request 시 0) |
| **Target Protocol Address** | 32 bits | 대상 IP 주소                 |

### ARP 동작

**ARP Request:**
```
Who has 192.168.1.1? Tell 192.168.1.100
Sender MAC: aa:bb:cc:dd:ee:ff
Sender IP: 192.168.1.100
Target MAC: 00:00:00:00:00:00 (unknown)
Target IP: 192.168.1.1
```

**ARP Reply:**
```
192.168.1.1 is at 11:22:33:44:55:66
Sender MAC: 11:22:33:44:55:66
Sender IP: 192.168.1.1
Target MAC: aa:bb:cc:dd:ee:ff
Target IP: 192.168.1.100
```

### ARP Spoofing 공격

```
공격자가 가짜 ARP Reply 전송:
"192.168.1.1 is at [공격자 MAC]"

결과: 피해자의 트래픽이 공격자를 거쳐감 (MITM)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. IPv6 헤더

### 구조 (40 bytes, 고정)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌─────────┬───────────────┬─────────────────────────────────────┐
│ Version │ Traffic Class │           Flow Label                │
├─────────┴───────────────┴─────┬───────────────┬───────────────┤
│       Payload Length          │ Next Header   │  Hop Limit    │
├───────────────────────────────┴───────────────┴───────────────┤
│                                                               │
│                                                               │
│                      Source Address                           │
│                       (128 bits)                              │
│                                                               │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                                                               │
│                   Destination Address                         │
│                       (128 bits)                              │
│                                                               │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                    | 크기     | 설명                                      |
|-------------------------|----------|-------------------------------------------|
| **Version**             | 4 bits   | IP 버전 (6)                               |
| **Traffic Class**       | 8 bits   | QoS 우선순위                              |
| **Flow Label**          | 20 bits  | 플로우 식별자                             |
| **Payload Length**      | 16 bits  | 페이로드 길이 (최대 65,535 bytes)         |
| **Next Header**         | 8 bits   | 다음 헤더 타입 (6=TCP, 17=UDP, 58=ICMPv6) |
| **Hop Limit**           | 8 bits   | TTL과 동일 (홉 수 제한)                   |
| **Source Address**      | 128 bits | 출발지 IPv6 주소                          |
| **Destination Address** | 128 bits | 목적지 IPv6 주소                          |

### IPv4 vs IPv6 비교

| 특성              | IPv4            | IPv6             |
|-------------------|-----------------|------------------|
| **주소 길이**     | 32 bits         | 128 bits         |
| **헤더 크기**     | 20-60 bytes     | 40 bytes (고정)  |
| **주소 개수**     | 약 43억 개      | 약 340간 개      |
| **Checksum**      | 있음            | 없음 (상위 계층) |
| **Fragmentation** | 라우터에서 가능 | 송신자만 가능    |
| **주소 표기**     | 192.168.1.1     | 2001:db8::1      |

### IPv6 주소 예시

```
전체 표기:
2001:0db8:0000:0000:0000:0000:0000:0001

축약 표기:
2001:db8::1

링크 로컬:
fe80::1

멀티캐스트:
ff02::1 (모든 노드)
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. ICMP 헤더

### 구조 (8+ bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────┬───────────────┬───────────────────────────────┐
│      Type     │      Code     │          Checksum             │
├───────────────┴───────────────┴───────────────────────────────┤
│                         Rest of Header                        │
│                       (Depends on Type)                       │
├───────────────────────────────────────────────────────────────┤
│                            Data                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드               | 크기    | 설명                 |
|--------------------|---------|----------------------|
| **Type**           | 8 bits  | ICMP 메시지 타입     |
| **Code**           | 8 bits  | 세부 코드            |
| **Checksum**       | 16 bits | 헤더 + 데이터 체크섬 |
| **Rest of Header** | 32 bits | Type에 따라 다름     |

### ICMP 타입

| Type | 이름                    | 설명                  |
|------|-------------------------|-----------------------|
| 0    | Echo Reply              | ping 응답             |
| 3    | Destination Unreachable | 목적지 도달 불가      |
| 5    | Redirect                | 경로 재지정           |
| 8    | Echo Request            | ping 요청             |
| 11   | Time Exceeded           | TTL 초과 (traceroute) |
| 30   | Traceroute              | 경로 추적             |

### Echo Request/Reply (ping)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────┬───────────────┬───────────────────────────────┐
│  Type (8/0)   │   Code (0)    │          Checksum             │
├───────────────┴───────────────┼───────────────────────────────┤
│         Identifier            │       Sequence Number         │
├───────────────────────────────┴───────────────────────────────┤
│                            Data                               │
└───────────────────────────────────────────────────────────────┘
```

### Destination Unreachable (Type 3)

**Code 값:**

| Code | 의미                 |
|------|----------------------|
| 0    | Network Unreachable  |
| 1    | Host Unreachable     |
| 2    | Protocol Unreachable |
| 3    | Port Unreachable     |
| 4    | Fragmentation Needed |

### ICMP Flood 공격

```
공격자 → 대량의 ICMP Echo Request → 피해자

방어:
# Rate limiting
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. DNS 헤더

### 구조 (12+ bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────┬───────────────────────────────┐
│         Transaction ID        │            Flags              │
├───────────────────────────────┼───────────────────────────────┤
│         Questions             │        Answer RRs             │
├───────────────────────────────┼───────────────────────────────┤
│       Authority RRs           │       Additional RRs          │
├───────────────────────────────┴───────────────────────────────┤
│                          Queries                              │
├───────────────────────────────────────────────────────────────┤
│                          Answers                              │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드               | 크기    | 설명                                 |
|--------------------|---------|--------------------------------------|
| **Transaction ID** | 16 bits | 쿼리/응답 매칭용 ID                  |
| **Flags**          | 16 bits | QR, Opcode, AA, TC, RD, RA, Z, RCODE |
| **Questions**      | 16 bits | 질의 개수                            |
| **Answer RRs**     | 16 bits | 응답 레코드 개수                     |
| **Authority RRs**  | 16 bits | 권한 레코드 개수                     |
| **Additional RRs** | 16 bits | 추가 레코드 개수                     |

### Flags 상세

```
 0  1 2 3 4  5  6  7  8  9  0  1  2 3 4 5
┌──┬────────┬──┬──┬──┬──┬──┬──┬──┬────────┐
│QR│ Opcode │AA│TC│RD│RA│AD│CD│Z │ RCODE  │
└──┴────────┴──┴──┴──┴──┴──┴──┴──┴────────┘
```

| 필드       | 크기   | 설명                                     |
|------------|--------|------------------------------------------|
| **QR**     | 1 bit  | 0=Query, 1=Response                      |
| **Opcode** | 4 bits | 0=Standard Query, 1=Inverse Query        |
| **AA**     | 1 bit  | Authoritative Answer                     |
| **TC**     | 1 bit  | Truncated                                |
| **RD**     | 1 bit  | Recursion Desired                        |
| **RA**     | 1 bit  | Recursion Available                      |
| **AD**     | 1 bit  | Authenticated Data (DNSSEC, RFC 4035)    |
| **CD**     | 1 bit  | Checking Disabled (DNSSEC, RFC 4035)     |
| **Z**      | 1 bit  | Reserved (must be 0)                     |
| **RCODE**  | 4 bits | Response Code (0=No Error, 3=Name Error) |

### DNS 레코드 타입

| Type | 이름  | 설명                  |
|------|-------|-----------------------|
| 1    | A     | IPv4 주소             |
| 2    | NS    | Name Server           |
| 5    | CNAME | Canonical Name (별칭) |
| 6    | SOA   | Start of Authority    |
| 15   | MX    | Mail Exchange         |
| 16   | TXT   | Text                  |
| 28   | AAAA  | IPv6 주소             |

### DNS 쿼리 예시

```
Query:
Transaction ID: 0x1234
Flags: 0x0100 (Standard query, Recursion desired)
Questions: 1
Question: www.example.com, Type A, Class IN

Response:
Transaction ID: 0x1234
Flags: 0x8180 (Standard response, No error)
Answers: 1
Answer: www.example.com, Type A, Class IN, TTL 300, Address 93.184.216.34
```

### DNS 터널링 탐지

```
# 비정상적으로 긴 도메인 이름
suspicious-long-subdomain-with-encoded-data.example.com

# 높은 쿼리 빈도
tcpdump -i eth0 -n port 53 | awk '{print $5}' | cut -d. -f1-4 | sort | uniq -c | sort -rn
```


[⬆ 목차로 돌아가기](#목차)

---

## 6. HTTP 헤더

### 구조 (텍스트 기반)

```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Connection: keep-alive
X-Forwarded-For: 192.168.1.100
X-Real-IP: 192.168.1.100

[Body]
```

### 주요 헤더

| 헤더               | 설명                               |
|--------------------|------------------------------------|
| **Host**           | 요청 대상 호스트                   |
| **User-Agent**     | 클라이언트 정보                    |
| **Accept**         | 수락 가능한 콘텐츠 타입            |
| **Content-Type**   | 본문 데이터 타입                   |
| **Content-Length** | 본문 길이                          |
| **Connection**     | 연결 유지 여부 (keep-alive, close) |
| **Cookie**         | 쿠키 데이터                        |
| **Authorization**  | 인증 정보                          |

### 프록시 관련 헤더

| 헤더                  | 설명                             |
|-----------------------|----------------------------------|
| **X-Forwarded-For**   | 원본 클라이언트 IP (프록시 체인) |
| **X-Real-IP**         | 실제 클라이언트 IP               |
| **X-Forwarded-Proto** | 원본 프로토콜 (http/https)       |
| **X-Forwarded-Host**  | 원본 호스트                      |
| **X-Forwarded-Port**  | 원본 포트                        |
| **Forwarded**         | RFC 7239 표준 헤더               |

### X-Forwarded-For 예시

```
Client     (1.2.3.4) → Proxy1 (10.0.0.1) → Proxy2 (10.0.0.2) → Server

Server가 받는 헤더:
X-Forwarded-For: 1.2.3.4, 10.0.0.1
```

### HTTP/2 vs HTTP/1.1

| 특성           | HTTP/1.1   | HTTP/2               |
|----------------|------------|----------------------|
| **형식**       | 텍스트     | 바이너리             |
| **멀티플렉싱** | 불가능     | 가능                 |
| **헤더 압축**  | 없음       | HPACK                |
| **서버 푸시**  | 불가능     | 가능                 |
| **연결**       | 요청당 1개 | 1개 연결로 다중 요청 |

### 보안 헤더

| 헤더                          | 설명              |
|-------------------------------|-------------------|
| **Strict-Transport-Security** | HTTPS 강제 (HSTS) |
| **Content-Security-Policy**   | XSS 방어          |
| **X-Frame-Options**           | 클릭재킹 방어     |
| **X-Content-Type-Options**    | MIME 스니핑 방지  |

[⬆ 목차로 돌아가기](#목차)

---

## 7. TLS/SSL 헤더

### TLS Handshake 구조

```
Client                                              Server
    │                                                  │
    ├── ClientHello ═══════════════════════════▶       │
    │   - TLS Version                                  │
    │   - Supported Cipher Suites                      │
    │   - Random Data                                  │
    │                                                  │
    │       ◀═══════════════════ ServerHello ──────────┤
    │         - Selected Cipher Suite                  │
    │         - Server Certificate                     │
    │         - Random Data                            │
    │                                                  │
    ├── ClientKeyExchange ════════════════════▶        │
    ├── ChangeCipherSpec ═════════════════════▶        │
    ├── Finished ═════════════════════════════▶        │
    │                                                  │
    │       ◀═══════════════ ChangeCipherSpec ─────────┤
    │       ◀═══════════════════════ Finished ─────────┤
    │                                                  │
    └── Encrypted Communication Start ─────────────────┘
```

### TLS Record 헤더 (5 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────┬───────────────┬───┬───────────────────────────┐
│ Content Type  │  Version (Major)  │  Version (Minor)          │
├───────────────┴───────────────┬───┴───────────────────────────┤
│            Length             │                               │
├───────────────────────────────┘                               │
│                         Payload                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드             | 크기    | 설명                                                        |
|------------------|---------|-------------------------------------------------------------|
| **Content Type** | 8 bits  | 20=ChangeCipherSpec, 21=Alert, 22=Handshake, 23=Application |
| **Version**      | 16 bits | TLS 버전 (0x0303=TLS 1.2, 0x0304=TLS 1.3)                   |
| **Length**       | 16 bits | 페이로드 길이                                               |

### TLS 버전

| 버전    | 값     | 특징                      |
|---------|--------|---------------------------|
| SSL 3.0 | 0x0300 | 더 이상 사용 안 함 (취약) |
| TLS 1.0 | 0x0301 | 레거시                    |
| TLS 1.1 | 0x0302 | 레거시                    |
| TLS 1.2 | 0x0303 | 현재 표준                 |
| TLS 1.3 | 0x0304 | 최신 (더 빠르고 안전)     |

### SNI (Server Name Indication)

```
ClientHello 확장:
Extension: server_name
    Server Name: www.example.com
```

**용도:**
- 하나의 IP에 여러 도메인 호스팅
- 프록시/방화벽에서 도메인 기반 필터링

[⬆ 목차로 돌아가기](#목차)

---

## 8. GRE 헤더

### 구조 (4-16 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌─┬─┬─┬─┬─┬─────┬─────────┬─────┬───────────────────────────────┐
│C│R│K│S│s│Recur│  Flags  │ Ver │       Protocol Type           │
├─┴─┴─┴─┴─┴─────┴─────────┴─────┼───────────────────────────────┤
│      Checksum (optional)      │       Reserved1 (optional)    │
├───────────────────────────────┴───────────────────────────────┤
│                         Key (optional)                        │
├───────────────────────────────────────────────────────────────┤
│                   Sequence Number (optional)                  │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드                | 크기    | 설명                                         |
|---------------------|---------|----------------------------------------------|
| **C (Checksum)**    | 1 bit   | 1=Checksum 필드 존재                         |
| **R (Routing)**     | 1 bit   | 1=Routing 정보 존재 (deprecated)             |
| **K (Key)**         | 1 bit   | 1=Key 필드 존재                              |
| **S (Sequence)**    | 1 bit   | 1=Sequence Number 필드 존재                  |
| **s (Strict)**      | 1 bit   | Strict Source Route (deprecated)             |
| **Recur**           | 3 bits  | Recursion Control (deprecated, must be 0)    |
| **Flags**           | 5 bits  | Reserved flags (must be 0)                   |
| **Ver (Version)**   | 3 bits  | GRE 버전 (0=GRE, 1=PPTP 등)                  |
| **Protocol Type**   | 16 bits | 캡슐화된 프로토콜 (0x0800=IPv4, 0x86DD=IPv6) |
| **Checksum**        | 16 bits | 선택적 체크섬 (C=1일 때 존재)                |
| **Reserved1**       | 16 bits | 예약 필드 (C=1일 때 존재, must be 0)         |
| **Key**             | 32 bits | 터널 식별자 (K=1일 때 존재)                  |
| **Sequence Number** | 32 bits | 패킷 순서 번호 (S=1일 때 존재)               |

### 사용 사례

**VPN 터널:**
```
원본 패킷: [IP][TCP][Data]
GRE 캡슐화: [외부 IP][GRE][원본 IP][TCP][Data]
```

**AWS Direct Connect:**
```
온프레미스 ←→ GRE 터널 ←→ AWS VPC
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. VXLAN 헤더

### 구조 (8 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌───────────────────────────────┬───────────────────────────────┐
│R│R│R│R│I│R│R│R│            Reserved                           │
├───────────────────────────────┬───────────────────────────────┤
│                VXLAN Network Identifier (VNI) │   Reserved    │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드         | 크기    | 설명                                    |
|--------------|---------|-----------------------------------------|
| **Flags**    | 8 bits  | I=1 (VNI 유효), 나머지 Reserved         |
| **Reserved** | 24 bits | 예약 (0)                                |
| **VNI**      | 24 bits | VXLAN Network Identifier (0-16,777,215) |
| **Reserved** | 8 bits  | 예약 (0)                                |

### VXLAN 캡슐화

```
원본 프레임:
[Ethernet][IP][TCP][Data]

VXLAN 캡슐화:
[외부 Ethernet][외부 IP][UDP 4789][VXLAN][원본 Ethernet][원본 IP][TCP][Data]
```

### 사용 사례

**AWS VPC:**
```
EC2 인스턴스 간 통신:
- VNI로 VPC 격리
- 오버레이 네트워크
```

**멀티 테넌트:**
```
VNI 100: 고객 A 네트워크
VNI 200: 고객 B 네트워크
VNI 300: 고객 C 네트워크
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. QUIC 헤더

### 구조 (Long Header)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
┌─┬───────┬───────────┬─────────┬───────────────────────────────┐
│1│  Type │  Reserved │ PKN Len │          Version              │
├─┴───────┴─┬─────────┴─────────┴───────────────────────────────┤
│ DCID Len  │   Destination Connection ID (0-160 bits)          │
├───────────┼───────────────────────────────────────────────────┤
│ SCID Len  │   Source Connection ID (0-160 bits)               │
├───────────┴───────────────────────────────────────────────────┤
│                       Packet Number                           │
├───────────────────────────────────────────────────────────────┤
│                         Payload                               │
└───────────────────────────────────────────────────────────────┘
```

### 필드 설명

| 필드              | 크기    | 설명                                         |
|-------------------|---------|----------------------------------------------|
| **Header Form**   | 1 bit   | 1=Long Header, 0=Short Header                |
| **Type**          | 2 bits  | 패킷 타입 (Initial, 0-RTT, Handshake, Retry) |
| **Version**       | 32 bits | QUIC 버전                                    |
| **DCID**          | 가변    | Destination Connection ID                    |
| **SCID**          | 가변    | Source Connection ID                         |
| **Packet Number** | 가변    | 패킷 번호                                    |

### QUIC 특징

| 특성                  | TCP + TLS       | QUIC                 |
|-----------------------|-----------------|----------------------|
| **전송 계층**         | TCP             | UDP                  |
| **Handshake**         | 2-RTT (TCP+TLS) | 0-1 RTT              |
| **Head-of-line**      | 블로킹 있음     | 블로킹 없음          |
| **연결 마이그레이션** | 불가능          | 가능 (Connection ID) |
| **암호화**            | TLS 별도        | 내장                 |

### HTTP/3 스택

```
HTTP/3
    ↓
QUIC (전송 + 암호화)
    ↓
UDP
    ↓
IP
```

### 0-RTT 연결

```
Client                                              Server
    │                                                  │
    ├── ClientHello + Data ────────────────────▶       │
    │   (Reuse previous session)                       │
    │                                                  │
    │       ◀──────────────────── ServerHello + Data ──┤
    │                                                  │
    └── Immediate Data Transfer ───────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 패킷 캡슐화 예시

### 일반 웹 트래픽

```
[Ethernet][IP][TCP][HTTP][Data]
```

### VPN 터널 (GRE)

```
[Ethernet][외부 IP][GRE][원본 IP][TCP][HTTP][Data]
```

### VXLAN 오버레이

```
[Ethernet][외부 IP][UDP 4789][VXLAN][원본 Ethernet][원본 IP][TCP][Data]
```

### QUIC (HTTP/3)

```
[Ethernet][IP][UDP][QUIC][HTTP/3][Data]
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 패킷 분석 명령어

### 특정 헤더 필터링

```bash
# Ethernet
tcpdump -i eth0 -e

# ARP
tcpdump -i eth0 arp

# IPv6
tcpdump -i eth0 ip6

# ICMP
tcpdump -i eth0 icmp

# DNS
tcpdump -i eth0 port 53

# HTTP
tcpdump -i eth0 -A 'tcp port 80'

# TLS ClientHello
tcpdump -i eth0 -X 'tcp port 443' | grep -A 10 "Client Hello"

# GRE
tcpdump -i eth0 proto gre

# VXLAN
tcpdump -i eth0 port 4789

# QUIC
tcpdump -i eth0 udp port 443
```

### Wireshark 필터

```
# Ethernet
eth.addr == aa:bb:cc:dd:ee:ff

# ARP
arp.opcode == 1  # Request
arp.opcode == 2  # Reply

# IPv6
ipv6.addr == 2001:db8::1

# ICMP
icmp.type == 8  # Echo Request

# DNS
dns.qry.name == "example.com"

# HTTP
http.request.method == "GET"
http.response.code == 200

# TLS
ssl.handshake.type == 1  # ClientHello
ssl.handshake.extensions_server_name == "example.com"

# GRE
gre

# VXLAN
vxlan.vni == 100

# QUIC
quic
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

| RFC      | 내용     |
|----------|----------|
| RFC 894  | Ethernet |
| RFC 826  | ARP      |
| RFC 2460 | IPv6     |
| RFC 792  | ICMP     |
| RFC 1035 | DNS      |
| RFC 2616 | HTTP/1.1 |
| RFC 7540 | HTTP/2   |
| RFC 8446 | TLS 1.3  |
| RFC 2784 | GRE      |
| RFC 7348 | VXLAN    |
| RFC 9000 | QUIC     |

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---
**작성일**: 2026-04-22
**마지막 업데이트**: 2026-04-22

© 2026 siasia86. Licensed under CC BY 4.0.
