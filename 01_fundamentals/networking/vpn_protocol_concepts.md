# VPN Protocol
<!-- reference: _reference/vpn_protocol_official_notes.md -->

VPN(Virtual Private Network) 터널링 프로토콜의 개념, 동작 원리, 보안 수준을 비교합니다. PPTP부터 WireGuard까지 세대별 발전 흐름과 각 프로토콜의 내부 동작을 다룹니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. PPTP](#2-pptp) / [3. L2TP](#3-l2tp) / [4. IPsec](#4-ipsec)                      |
| [5. L2TP/IPsec](#5-l2tpipsec) / [6. IKEv2](#6-ikev2) / [7. OpenVPN](#7-openvpn)                          |
| [8. WireGuard](#8-wireguard) / [9. 프로토콜 비교](#9-프로토콜-비교) / [10. 선택 가이드](#10-선택-가이드) |

---

## 1. 개요

### VPN 터널링 원리

VPN 터널링이란 원본 패킷을 새로운 패킷으로 **캡슐화(encapsulation)** 하여 공개 네트워크를 통해 전달하는 기법입니다. 수신 측에서는 외부 헤더를 제거하고 원본 패킷을 복원합니다.

```
Sender (Host A)
┌──────────────────────────────────────────────────────────┐
│  Original Packet                                         │
│  [ IP Header | TCP Header | Payload ]                    │
│         │                                                │
│         v  Encapsulate + Encrypt                         │
│  [ Outer IP | VPN Header | Encrypted(IP|TCP|Payload) ]   │
└──────────────────────────────────────────────────────────┘
              │
              │  Public Network (Internet)
              v
Receiver (Host B)
┌──────────────────────────────────────────────────────────┐
│  [ Outer IP | VPN Header | Encrypted(IP|TCP|Payload) ]   │
│         │                                                │
│         v  Decrypt + Decapsulate                         │
│  [ IP Header | TCP Header | Payload ]  (Original)        │
└──────────────────────────────────────────────────────────┘
```

캡슐화로 달성하는 3가지 목표:

| 목표   | 설명                                                          |
|--------|---------------------------------------------------------------|
| 기밀성 | 원본 페이로드를 암호화하여 중간자가 내용을 알 수 없게 합니다. |
| 무결성 | HMAC/AEAD 태그로 전송 중 변조를 탐지합니다.                   |
| 인증   | 상대방이 신뢰된 피어임을 키 교환/인증서로 검증합니다.         |

> AEAD(Authenticated Encryption with Associated Data): 암호화와 무결성 검증을 동시에 수행하는 암호화 방식입니다. AES-GCM, ChaCha20-Poly1305가 대표적이며, 별도의 MAC 계산 없이 단일 패스로 처리합니다.

> HMAC(Hash-based Message Authentication Code): 해시 함수(SHA-256 등)와 비밀 키를 조합하여 메시지 무결성과 데이터 출처 인증을 검증하는 알고리즘입니다. 송신자와 수신자가 동일한 비밀 키를 공유하며, 수신 측은 HMAC 태그를 재계산하여 전송 중 변조 여부를 확인합니다. HMAC만으로는 사용자 신원이나 공개키 기반의 비부인성을 보장하지 않습니다.

### 캡슐화 구체 예시

#### WireGuard 터널 통과 — `curl http://192.0.2.1` 요청

```
─── Original Packet (before tunnel entry) ──────────────────────────
  IP  Src: 10.0.0.2      Dst: 192.0.2.1
  TCP Src: 54321         Dst: 80
  HTTP Payload: "GET / HTTP/1.1\r\nHost: 192.0.2.1"

─── After WireGuard Encapsulation (actual packet on Internet) ───────
  IP  Src: 192.0.2.100   Dst: 203.0.113.1     <-- only public IP visible
  UDP Src: 51820         Dst: 51820
  [ WireGuard Header: Type | Receiver ID | Counter ]
  [ ChaCha20-Poly1305 Encrypted {
        IP  Src: 10.0.0.2  Dst: 192.0.2.1     <-- original IP (hidden)
        TCP Src: 54321     Dst: 80
        HTTP: "GET / HTTP/1.1..."              <-- payload (hidden)
    }
    Auth Tag (16 bytes)                        <-- integrity tag
  ]
```

중간자(ISP, 공유기)가 볼 수 있는 것: `192.0.2.100 → 203.0.113.1 UDP/51820` 뿐
중간자가 볼 수 없는 것: 목적지(`192.0.2.1`), 포트(`80`), 내용(`GET /...`)

#### 프로토콜별 캡슐화 레이어 비교

```
Original: [ IP | TCP | HTTP ]

IPsec (ESP):
  [ Outer IP | ESP Hdr | Encrypted(IP | TCP | HTTP) | ESP Trailer | Auth Tag ]

L2TP/IPsec:
  [ Outer IP | UDP/4500 | ESP | UDP/1701 | L2TP | PPP | IP | TCP | HTTP ]
  └─────────── IPsec encryption scope ──────────────────────────┘

OpenVPN (UDP):
  [ Outer IP | UDP/1194 | OpenVPN Hdr | Authenticated encrypted VPN payload ]

WireGuard:
  [ Outer IP | UDP/51820 | WG Hdr | ChaCha20(IP | TCP | HTTP) | Auth Tag ]

SoftEther (SSL-VPN):
  [ Outer IP | TCP/443 | SSL-VPN stream | Encrypted VPN payload ]
  └── TCP 443 사용이 HTTPS와의 완전한 동일성을 보장하지 않음 ─┘
```

#### tcpdump로 본 캡슐화 전/후

터널 없이 직접 연결 시 — 내용이 그대로 노출됩니다.

```
$ tcpdump -i eth0 -n port 80

12:00:01.001 IP 10.0.0.2.54321 > 192.0.2.1.80: Flags [S]
12:00:01.002 IP 192.0.2.1.80 > 10.0.0.2.54321: Flags [S.] ack 1
12:00:01.003 IP 10.0.0.2.54321 > 192.0.2.1.80: Flags [P.] length 77
    GET / HTTP/1.1
    Host: 192.0.2.1
```

WireGuard 터널 통과 시 — 인터넷 구간(`eth0`)에서 관찰합니다.

```
$ tcpdump -i eth0 -n udp port 51820

12:00:01.001 IP 192.0.2.100.51820 > 203.0.113.1.51820: UDP, length 148
12:00:01.002 IP 203.0.113.1.51820 > 192.0.2.100.51820: UDP, length 92
12:00:01.003 IP 192.0.2.100.51820 > 203.0.113.1.51820: UDP, length 148
```

`192.0.2.100 ↔ 203.0.113.1 UDP` 트래픽만 보이고 내부 목적지·포트·내용은 전혀 보이지 않습니다.

WireGuard 터널 내부 — 서버 측 `wg0` 인터페이스에서 관찰합니다.

```
$ tcpdump -i wg0 -n

12:00:01.001 IP 10.0.0.2.54321 > 192.0.2.1.80: Flags [S]
12:00:01.002 IP 192.0.2.1.80 > 10.0.0.2.54321: Flags [S.]
12:00:01.003 IP 10.0.0.2.54321 > 192.0.2.1.80: Flags [P.] GET / HTTP/1.1
```

복호화된 원본 패킷이 그대로 보입니다.

SoftEther SSL-VPN 터널 통과 시 — 인터넷 구간(`eth0`)에서 관찰합니다.

```
$ tcpdump -i eth0 -n tcp port 443

12:00:01.001 IP 192.0.2.100.52341 > 203.0.113.1.443: Flags [P.] length 183
12:00:01.002 IP 203.0.113.1.443 > 192.0.2.100.52341: Flags [P.] length 91
```

TCP 443으로 전달되더라도 TLS 지문, 트래픽 패턴, 서버 동작 특성으로 VPN 트래픽이 식별될 수 있습니다.

| 관찰 지점                  | 보이는 것                              | 보이지 않는 것          |
|----------------------------|----------------------------------------|-------------------------|
| `eth0` (인터넷 구간)       | 터널 엔드포인트 IP/포트, 암호화된 길이 | 목적지, 원본 포트, 내용 |
| `wg0` / `tun0` (터널 내부) | 복호화된 원본 패킷 전체                | -                       |
| SoftEther `eth0` (TCP 443) | 암호화된 TCP 443 트래픽과 VPN 패턴     | 내부 목적지·내용        |

> DPI(Deep Packet Inspection): 방화벽이 패킷 헤더뿐 아니라 페이로드 내용까지 분석하여 특정 애플리케이션이나 프로토콜을 식별·차단하는 기법입니다. 포트만 보는 일반 방화벽과 달리 TLS 핑거프린트나 트래픽 패턴으로 VPN을 탐지합니다.



### NAT-T (NAT Traversal) 원리

IPsec ESP는 IP Protocol 50으로 전송됩니다. 일부 NAT 장비는 ESP를 일반적인 TCP/UDP 흐름처럼 처리하지 못하므로, NAT 환경에서는 ESP를 UDP로 감싸는 NAT-T(RFC 3947)를 사용합니다.

```
Without NAT-T (ESP blocked by NAT):
Host A ──[ ESP/50 ]──> [NAT] ──X──> VPN Gateway

With NAT-T (ESP encapsulated in UDP 4500):
Host A ──[ UDP 4500 [ ESP ] ]──> [NAT] ──[ UDP 4500 [ ESP ] ]──> VPN Gateway
```

NAT-T는 IKE 협상 중 양단이 UDP 4500으로 자동 전환하며, RFC 3947/3948에 정의되어 있습니다.

### UDP 터널과 TCP 신뢰성

UDP 기반 VPN은 내부 IP 패킷을 UDP 데이터그램으로 감싸서 전송합니다. 내부 TCP 트래픽의 신뢰성이 어느 계층에서 보장되는지 설명합니다.

#### 계층별 역할 분리

```
Application (curl, ssh, ...)
    │
    v
TCP (reliability: ACK, retransmit, flow control, ordering)
    │
    v
IP Packet
    │
    v  ── VPN Encapsulation ──
UDP (transport: connectionless, no reliability)
    │
    v
Internet
```

VPN은 IP 패킷 전체를 캡슐화하므로 내부 TCP 계층이 그대로 살아 있습니다.
UDP 구간에서 패킷이 유실되면 내부 TCP가 이를 감지하여 타임아웃 후 재전송할 수 있습니다. 내부 UDP 트래픽에는 이와 같은 재전송 보장이 없으며, 애플리케이션은 일반적으로 VPN 터널의 존재를 직접 알지 못합니다.
VPN 터널은 일반적으로 애플리케이션에 투명하게 동작합니다.

#### VPN이 UDP를 선호하는 이유 — TCP meltdown

VPN 터널 자체를 TCP로 구성하면 내부/외부 TCP가 손실·혼잡을 각각 제어하여 Head-of-Line Blocking과 혼잡 제어 상호작용이 발생할 수 있습니다.

```
[TCP meltdown scenario]

Outer TCP: loss detected -> retransmit wait (window shrink)
    │
    └─ Inner TCP: timeout simultaneously -> retransmit attempt
                    │
                    └─ Outer TCP still waiting -> inner retransmit also delayed
                            │
                            └─ Inner TCP RTT spike -> more timeouts -> cascade
```

외부를 UDP로 사용하면 신뢰성 있는 전송 계층이 중복되지 않아 이런 TCP-over-TCP 상호작용을 줄일 수 있습니다. 단, 내부 UDP 트래픽의 신뢰성까지 자동으로 추가되는 것은 아닙니다.

#### 프로토콜별 전송 방식

| VPN           | 기본 전송    | TCP 모드   | TCP meltdown 위험 | 비고                                 |
|---------------|--------------|------------|-------------------|--------------------------------------|
| WireGuard     | UDP 전용     | ❌ 불가    | 없음              | UDP 차단 환경 사용 불가              |
| IPsec (IKEv2) | UDP 500/4500 | ❌ 불가    | 없음              | NAT-T로 UDP 캡슐화                   |
| OpenVPN       | UDP 1194     | ✅ TCP 443 | 🟡 있음           | TCP 모드는 방화벽 우회용             |
| SoftEther     | TCP 443/992  | TCP 기본   | 🟡 있음           | 여러 TCP 연결 사용 시 영향 완화 가능 |

🟡 OpenVPN/SoftEther의 TCP 모드는 UDP가 차단된 환경에서의 대안입니다. 성능보다 통과 가능성을 우선할 때 사용하며, 안정적인 네트워크에서는 UDP 모드 대비 처리량이 낮을 수 있습니다.

### 세대별 발전

```
주요 등장·표준화 시점(대략)

1996        1999           2001        2005        2014       2020
 │           │              │           │           │          │
 v           v              v           v           v          v
PPTP ──> L2TPv2/IPsec ──> OpenVPN ──> L2TPv3 ──> IKEv2 ──> WireGuard
(legacy)  (legacy)       (mature)   (L2 service) (RFC 7296) (Linux 5.6)
```

### OSI 계층별 동작 위치

| 프로토콜    | 동작 계층   | 캡슐화 대상    | 전송 프로토콜        |
|-------------|-------------|----------------|----------------------|
| PPTP        | Layer 2     | PPP 프레임     | GRE (IP Protocol 47) |
| L2TP        | Layer 2     | PPP 프레임     | UDP 1701             |
| IPsec       | Layer 3     | IP 패킷        | ESP/AH (IP 50/51)    |
| L2TP/IPsec  | Layer 2 + 3 | PPP over IPsec | UDP 4500 (NAT-T)     |
| IKEv2/IPsec | Layer 3     | IP 패킷        | UDP 500 / 4500       |
| OpenVPN     | Layer 2/3   | TLS 위 터널    | UDP 1194 / TCP 443   |
| WireGuard   | Layer 3     | IP 패킷        | UDP 51820            |

[⬆ 목차로 돌아가기](#목차)

---

## 2. PPTP

Point-to-Point Tunneling Protocol. Microsoft와 협력사들이 1990년대에 개발한 VPN 프로토콜입니다. RFC 2637(Informational — IETF 비표준)로 등록되어 있으며, 현재는 알려진 취약점 때문에 신규 사용을 피해야 합니다.

| 항목      | 값                               |
|-----------|----------------------------------|
| 개발사    | Microsoft 및 협력사              |
| RFC       | RFC 2637 (Informational, 비표준) |
| 포트      | TCP 1723 + GRE (Protocol 47)     |
| 암호화    | MPPE (레거시 RC4 기반)           |
| 인증      | MS-CHAPv2                        |
| 보안 상태 | ❌ 취약 — 신규 사용 금지         |
| 현재 용도 | 레거시 호환 외 사용 금지         |

> GRE(Generic Routing Encapsulation, RFC 2784): IP 패킷을 다른 IP 패킷 안에 캡슐화하는 터널링 프로토콜입니다. TCP/UDP가 아닌 IP Protocol 47번을 사용하므로 NAT 장비가 포트 변환을 할 수 없어 NAT 통과가 어렵습니다.

> MPPE(Microsoft Point-to-Point Encryption): PPP 프레임을 RC4 스트림 암호로 암호화하는 Microsoft 독자 규격입니다. MS-CHAPv2에서 파생된 키를 사용하며, MS-CHAPv2가 크랙되면 MPPE 세션 키도 자동으로 노출됩니다.

### 동작 구조

PPTP는 제어 채널(TCP 1723)과 데이터 채널(GRE)을 분리하여 운용합니다.

```
[Control Channel]  TCP 1723
   Client ─── Start-Control-Connection-Request ──> Server
   Client <── Start-Control-Connection-Reply   ─── Server
   Client ─── Outgoing-Call-Request            ──> Server
   Client <── Outgoing-Call-Reply              ─── Server
         (Tunnel Established)

[Data Channel]  GRE (IP Protocol 47)
┌───────────────────────────────────────────────────────────┐
│ Outer IP │ GRE Header │ PPP Header │ MPPE(RC4) Payload    │
└───────────────────────────────────────────────────────────┘
```

PPTP의 확장 GRE 헤더에는 협상된 플래그에 따라 Key, Sequence Number, Acknowledgment Number 필드가 포함될 수 있으며, PPP 프레임을 캡슐화합니다.

> PPP(Point-to-Point Protocol, RFC 1661): 두 노드 간 직렬 링크에서 인증(PAP/CHAP), IP 주소 할당(IPCP), 압축(CCP)을 처리하는 데이터 링크 계층 프로토콜입니다. PPTP/L2TP는 PPP를 터널 안에서 재활용하여 인증과 IP 할당을 처리합니다.

### MS-CHAPv2 크랙 메커니즘

2012년 공개된 공격은 MS-CHAPv2 응답이 사실상 세 개의 DES 키로 구성된다는 점을 이용했습니다. 마지막 키의 유효 엔트로피가 작아 실용적인 오프라인 크래킹이 가능하므로, MS-CHAPv2는 안전한 VPN 인증 방식으로 사용할 수 없습니다.

```
MS-CHAPv2 Challenge-Response structure:
Server Challenge (8 bytes)
       │
       v
Client NTLM Hash (16 bytes)
       │
       v  split into 3 DES keys (7+7+7 bytes, zero-padded to 21)
       ├── DES(Hash[0..6],          challenge) ──> Response_1  (8 bytes)
       ├── DES(Hash[7..13],         challenge) ──> Response_2  (8 bytes)
       └── DES(Hash[14..15]+0x00×5, challenge) ──> Response_3  (8 bytes)

-> 3rd key: Hash[14..15] (2 effective bytes) + 5 zero bytes -> brute-force: 65,536 (2^16)
-> once key3 cracked, key1 & key2 via DES brute-force
-> NTLM Hash 획득 가능 -> 원문 패스워드 복구 여부는 패스워드 강도와 사전 공격에 좌우됨
```

> NT Hash(NT LAN Manager Hash): Windows 패스워드에서 파생되는 MD4 기반 해시 값입니다. MS-CHAPv2 공격으로 NT Hash를 얻을 수 있지만, 원문 패스워드 복구는 패스워드 강도와 공격자의 사전·무차별 대입 능력에 따라 달라집니다.

### 보안 취약점 정리

| 취약점          | 영향                                       |
|-----------------|--------------------------------------------|
| MS-CHAPv2 취약  | 실용적인 오프라인 크래킹 공격에 취약       |
| RC4 기반 MPPE   | 현재 보안 요구사항에 부적합한 레거시 암호  |
| GRE 무결성 없음 | 암호학적 무결성 보호가 없어 변조 위험      |
| MPPE 키 파생    | 인증 키가 노출되면 세션 보호도 영향을 받음 |

🟡 PPTP는 어떤 환경에서도 신규 도입하면 안 됩니다. 기존 레거시 시스템에서만 잔존합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. L2TP

Layer 2 Tunneling Protocol. Cisco의 L2F와 Microsoft의 PPTP를 통합하여 IETF가 표준화한 프로토콜입니다. **자체 암호화가 없어**, 보안 통신에는 IPsec과 조합해야 합니다.

| 항목        | 값                                               |
|-------------|--------------------------------------------------|
| 표준        | RFC 2661 (L2TPv2, 1999), RFC 3931 (L2TPv3, 2005) |
| 포트        | UDP 1701                                         |
| 자체 암호화 | ❌ 없음 — IPsec 조합 필수                        |
| 인증        | PPP 인증(PAP/CHAP 등); L2TP 자체만으로 보안 부족 |
| 구성 요소   | LAC (Access Concentrator) + LNS (Network Server) |

### 핵심 구성 요소

| 용어    | 역할                                                           |
|---------|----------------------------------------------------------------|
| LAC     | L2TP Access Concentrator — 클라이언트 측 종단점, PPP 세션 시작 |
| LNS     | L2TP Network Server — 서버 측 종단점, PPP 세션 종료            |
| Tunnel  | LAC-LNS 간 하나의 UDP 연결 (다수 세션 수용)                    |
| Session | 터널 내 개별 PPP 연결 (1개 터널에 N개 세션 가능)               |

### 제어/데이터 채널 교환 흐름

```
LAC                                    LNS
 │                                      │
 ├── SCCRQ (Start-Control-Conn Req) ──> │   Tunnel setup request
 │ <── SCCRP (Reply)                ─── │   Tunnel setup response
 ├── SCCCN (Connected)              ──> │   Tunnel established
 │                                      │
 ├── ICRQ  (Incoming-Call Req)      ──> │   Session request
 │ <── ICRP (Reply)                 ─── │   Session response
 ├── ICCN  (Connected)              ──> │   Session established
 │                                      │
 │  [PPP data via L2TP Data Channel]    │
 ├──────────────────────────────────>   │
 │ <────────────────────────────────    │
```

### 패킷 구조

```
┌────────────────────────────────────────────────────────────────┐
│ IP Header │ UDP 1701 │ L2TP Header │ PPP Header │ PPP Payload  │
└────────────────────────────────────────────────────────────────┘
                        │
                        └─ Tunnel ID (16bit) + Session ID (16bit)
                           Ns (Sequence) + Nr (Next Received)
```

### L2TPv2 vs L2TPv3

| 항목        | L2TPv2 (RFC 2661) | L2TPv3 (RFC 3931)          |
|-------------|-------------------|----------------------------|
| 발행        | 1999-08           | 2005-03                    |
| 전송        | UDP 1701          | UDP 또는 IP Protocol 115   |
| 캡슐화      | PPP only          | PPP, Ethernet, Frame Relay |
| 용도        | Remote Access VPN | L2 서비스 확장 (Carrier)   |
| 자체 암호화 | 없음              | 없음                       |

🟡 L2TP 단독으로는 암호화가 없어 평문 전송됩니다. 반드시 IPsec과 조합해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. IPsec

Internet Protocol Security. IETF가 정의한 IP 계층 보안 프로토콜 스위트입니다. VPN 터널 자체를 구현하거나(Tunnel Mode) 호스트 간 통신을 보호(Transport Mode)하는 데 사용됩니다.

| 항목          | 값                                                    |
|---------------|-------------------------------------------------------|
| 표준          | RFC 4301 (아키텍처), RFC 4303 (ESP), RFC 7296 (IKEv2) |
| 동작 계층     | Network Layer (Layer 3)                               |
| 프로토콜 번호 | ESP = IP Protocol 50, AH = IP Protocol 51             |
| 키 교환       | IKE v1/v2 (UDP 500), NAT-T (UDP 4500)                 |
| 모드          | Transport Mode / Tunnel Mode                          |

### 핵심 프로토콜

| 프로토콜 | 역할                           | 제공하는 보안               | IP Protocol |
|----------|--------------------------------|-----------------------------|-------------|
| ESP      | Encapsulating Security Payload | 기밀성 + 무결성 + 인증      | 50          |
| AH       | Authentication Header          | 무결성 + 인증 (암호화 없음) | 51          |
| IKE      | Internet Key Exchange          | SA 협상, 키 교환            | UDP 500     |

실무에서는 AH 단독 사용은 거의 없으며, 기밀성까지 제공하는 **ESP를 기본**으로 사용합니다.

> ESP(Encapsulating Security Payload, RFC 4303): IPsec에서 암호화·무결성·인증을 제공하는 핵심 프로토콜(IP Protocol 50)입니다. AH(Authentication Header, IP Protocol 51)는 암호화 없이 무결성만 제공하며 현재 실무에서는 거의 사용하지 않습니다.

### Transport Mode vs Tunnel Mode

```
Transport Mode (Host-to-Host):
Original: [ IP Hdr(A->B) | TCP | Data ]
Result:   [ IP Hdr(A->B) | ESP Hdr | TCP | Data | ESP Trailer | ESP Auth ]
          (original IP kept) (encrypted: TCP to ESP Trailer)

Tunnel Mode (Gateway-to-Gateway):
Original: [ IP Hdr(A->B) | TCP | Data ]
Result:   [ New IP Hdr(GW1->GW2) | ESP Hdr | IP Hdr(A->B) | TCP | Data | ESP Trailer | ESP Auth ]
          (gateway IP)           (encrypted: entire original packet incl. inner IP)
```

> Tunnel Mode에서 원본 IP 헤더 전체가 암호화되므로 통신 당사자의 IP 주소가 외부에 노출되지 않습니다. Site-to-Site VPN에서 게이트웨이(GW1↔GW2) 간 터널을 구성할 때 사용합니다.

- **Transport Mode**: 호스트 간 직접 암호화. 원본 IP 헤더 노출. 주로 호스트-호스트 보안에 사용됩니다.
- **Tunnel Mode**: 게이트웨이가 원본 패킷 전체를 새 IP 패킷으로 감쌉니다. Site-to-Site VPN의 표준 방식입니다.

### SPD / SAD 개념

IPsec은 두 개의 데이터베이스로 정책과 세션을 관리합니다.

| DB  | 이름                          | 역할                                                   |
|-----|-------------------------------|--------------------------------------------------------|
| SPD | Security Policy Database      | 트래픽별 IPsec 적용 여부 결정 (Protect/Bypass/Discard) |
| SAD | Security Association Database | 실제 암호화 파라미터 저장 (SPI, 알고리즘, 키, 수명)    |

> SPI(Security Parameter Index): 32비트 값으로 수신 측이 어떤 SA(Security Association)를 사용하여 패킷을 처리할지 식별하는 인덱스입니다. 발신자가 패킷 헤더에 포함시켜 전송하면, 수신자는 SPI로 SAD를 조회하여 복호화 파라미터를 찾습니다.

```
Outbound packet processing flow:

Packet (src:A, dst:B, proto:TCP)
        │
        v
    [SPD lookup] ── traffic selector matching
        │
        ├── Bypass  ──> forward without encryption
        ├── Discard ──> drop packet
        └── Protect ──> [SAD lookup]
                              │
                        SA exists? ──No──> trigger IKE, create SA
                              │
                             Yes
                              │
                              v
                         apply ESP/AH, then forward
```

> Traffic Selector: 출발지/목적지 IP·포트·프로토콜 범위를 정의하여 어떤 트래픽에 IPsec을 적용할지 결정하는 필터입니다. IKEv2에서 TSi(Initiator), TSr(Responder) 쌍으로 협상합니다.

SA (Security Association) 주요 필드:

| 필드      | 설명                                        |
|-----------|---------------------------------------------|
| SPI       | Security Parameter Index — 32bit, SA 식별자 |
| Protocol  | ESP(50) 또는 AH(51)                         |
| Algorithm | 암호화 알고리즘 + 무결성 알고리즘 조합      |
| Key       | 협상된 세션 키 (IKE가 파생)                 |
| Lifetime  | SA 유효 시간(초) 또는 처리 바이트 수        |
| Mode      | Transport / Tunnel                          |

### IKEv1 Phase 1 / Phase 2 협상 흐름

IKEv1은 두 단계로 SA를 협상합니다.

```
Phase 1 — IKE SA establishment (Main Mode, 6 messages):

Initiator                               Responder
    │── SA (cipher proposal)        ──>  │
    │ <── SA (chosen proposal)      ───  │
    │── KE + Nonce (DH pubkey)      ──>  │
    │ <── KE + Nonce                ───  │
    │  (DH done -> shared secret)        │
    │── ID + AUTH (encrypted)       ──>  │
    │ <── ID + AUTH                 ───  │
    │  (ISAKMP SA established)           │

Phase 2 — IPsec SA establishment (Quick Mode, 3 messages):

    │── SA + Nonce + ID (encrypted) ──>  │
    │ <── SA + Nonce + ID           ───  │
    │── Hash (confirm)              ──>  │
    │  (Child SA = ESP/AH SA established)│
```

> ISAKMP(Internet Security Association and Key Management Protocol, RFC 2408): IKEv1에서 사용된 SA 관리 프레임워크와 메시지 형식을 정의합니다. IKEv2는 별도의 메시지 형식과 교환 절차를 정의하므로 IKEv1과 동일한 ISAKMP 구조로 설명하면 안 됩니다.

### 필수 암호 알고리즘 (RFC 8221, 2017)

| 용도    | MUST                     | SHOULD                       | MAY      |
|---------|--------------------------|------------------------------|----------|
| 암호화  | AES-CBC, AES-GCM-16      | ChaCha20-Poly1305, AES-CCM-8 |          |
| 무결성  | HMAC-SHA-256-128*        | HMAC-SHA-512-256             | AES-GMAC |
| DH 그룹 | 별도 IKEv2 지침에서 결정 |                              |          |

* AEAD cipher(AES-GCM, ChaCha20-Poly1305) 사용 시 `AUTH_NONE`은 **MUST**입니다(RFC 8221 — AEAD-only 조건).
  non-AEAD cipher 사용 시 `AUTH_NONE`은 **MUST NOT**이며, `HMAC-SHA-256-128`(MUST) 같은 별도 무결성 알고리즘이 필요합니다.

[⬆ 목차로 돌아가기](#목차)


---

## 5. L2TP/IPsec

L2TP 터널을 IPsec ESP로 보호하는 조합입니다. RFC 3193에서는 Transport Mode를 반드시 지원하고 Tunnel Mode를 선택 사항으로 둡니다. L2TP가 PPP 세션을 제공하고 IPsec이 보호를 담당합니다. 주요 운영체제에 기본 지원이 있지만 버전·정책에 따라 차이가 있습니다.

| 항목         | 값                                                     |
|--------------|--------------------------------------------------------|
| 포트         | UDP 500 (IKE), UDP 4500 (NAT-T), UDP 1701 (IPsec 내부) |
| 암호화       | IPsec ESP (운영 정책에 따른 AEAD 권장)                 |
| 인증         | IKE PSK 또는 X.509 인증서                              |
| 이중 캡슐화  | ✅ (L2TP over IPsec)                                   |
| NAT 통과     | NAT 환경에서 UDP 4500 사용                             |
| OS 기본 지원 | 운영체제·버전에 따라 다름                              |

### 연결 수립 순서

L2TP/IPsec은 IPsec이 먼저 수립된 후 그 안에서 L2TP가 동작합니다.

```
1. IKE_SA_INIT (UDP 500, NAT 감지 후 필요 시 UDP 4500)
   Client ── IKE_SA_INIT ──> Server
   (암호 알고리즘·DH·Nonce 협상)

2. IKE_AUTH (암호화된 IKE 메시지)
   Client ── IKE_AUTH ──> Server
   (IKE SA와 Child SA 인증·수립)

3. L2TP over protected IPsec (UDP 1701)
   Client ── SCCRQ / ICRQ ──> Server
   (L2TP Session established)

4. PPP negotiation (inside L2TP)
   LCP -> Authentication -> NCP (IP address assignment)
   (VPN IP acquired)
```

> LCP(Link Control Protocol): PPP 링크 파라미터(MRU, 인증 방식)를 협상하는 제어 프로토콜입니다. NCP(Network Control Protocol)는 상위 네트워크 프로토콜 설정을 담당하며, IP 주소 할당은 NCP의 일종인 IPCP(IP Control Protocol)가 처리합니다.

### 패킷 구조 및 오버헤드

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Outer IP │ UDP 4500 │ ESP Hdr │ UDP 1701 │ L2TP │ PPP │ Inner IP │ Payload │
└────────────────────────────────────────────────────────────────────────────┘
  IPv4/UDP/ESP headers, IV/Nonce (cipher에 따라 다름), padding, ICV, and L2TP/PPP headers vary by implementation, cipher, and MTU.
  └── UDP 1701 onward is protected by ESP ───────────────────────────────────┘
```

오버헤드는 고정된 단일 값이 아니므로, 실제 MTU는 선택한 ESP 알고리즘과 NAT-T 여부를 기준으로 계산해야 합니다.

### 장단점

| 장점                          | 단점                           |
|-------------------------------|--------------------------------|
| OS 기본 지원 (추가 설치 없음) | 이중 캡슐화로 오버헤드 증가    |
| IPsec 수준의 암호화           | UDP 500/4500 차단 시 연결 불가 |
| 20년+ 검증된 안정성           | NAT 환경에서 설정 복잡         |
| PSK 방식으로 간편 배포 가능   | 연결 수립 시간 길음 (3단계)    |

[⬆ 목차로 돌아가기](#목차)

---

## 6. IKEv2

Internet Key Exchange version 2. RFC 7296(2014)에 정의된 IPsec 키 교환 프로토콜입니다. IKEv1의 복잡성을 줄이고 모바일 환경 지원(MOBIKE)을 추가했습니다.

| 항목         | 값                                             |
|--------------|------------------------------------------------|
| 표준         | RFC 7296 (2014), RFC 4555 (MOBIKE)             |
| 포트         | UDP 500 + UDP 4500 (NAT-T)                     |
| 암호화       | IPsec ESP (AES-GCM, ChaCha20-Poly1305 등)      |
| 특징         | MOBIKE — 네트워크 전환 시 세션 유지            |
| OS 기본 지원 | Windows/macOS/iOS/Android 등(버전·정책별 차이) |
| 핵심 강점    | 모바일 로밍, 빠른 재연결                       |

> MOBIKE(IKEv2 Mobility and Multihoming, RFC 4555): 양단과 네트워크가 지원하는 경우 IKE SA를 재협상하지 않고 주소 변경에 대응하여 세션을 지속할 수 있는 기능입니다. Wi-Fi ↔ LTE 전환 시 연결 유지를 지원하지만, 구현·정책·네트워크 상태에 따라 재연결이 필요할 수 있습니다.

### IKEv2 4개 메시지 교환 흐름

IKEv2는 기본 케이스에서 IKEv1의 9개 메시지를 4개로 압축했습니다(EAP 인증 사용 시 IKE_AUTH 내 추가 교환 발생).

```
Initiator                                       Responder
    │                                               │
    │── IKE_SA_INIT (1) ─────────────────────────>  │
    │   SAi1 (cipher proposal)                      │
    │   KEi (DH pubkey)                             │
    │   Ni (Nonce)                                  │
    │                                               │
    │ <── IKE_SA_INIT (2) ────────────────────────  │
    │     SAr1 (chosen proposal)                    │
    │     KEr (DH pubkey)                           │
    │     Nr (Nonce)                                │
    │     (DH done -> SK_d, SK_a, SK_e derived)     │
    │                                               │
    │── IKE_AUTH (3) ───────────────────────────>   │  [encrypted]
    │   IDi (Initiator ID)                          │
    │   AUTH (signature or PSK proof)               │
    │   SAi2 (Child SA proposal)                    │
    │   TSi, TSr (traffic selectors)                │
    │                                               │
    │ <── IKE_AUTH (4) ─────────────────────────    │  [encrypted]
    │     IDr (Responder ID)                        │
    │     AUTH                                      │
    │     SAr2 (Child SA selected)                  │
    │     TSi, TSr                                  │
    │     (IKE SA + Child SA established)           │
```

IKE_SA_INIT에서 DH 키 교환이 완료되므로, IKE_AUTH부터는 모든 페이로드가 암호화됩니다.

### IKEv1 vs IKEv2

| 항목           | IKEv1 (Main Mode)             | IKEv2                        |
|----------------|-------------------------------|------------------------------|
| 메시지 수      | Phase 1: 6 + Phase 2: 3 = 9   | 4개 (IKE_SA_INIT + IKE_AUTH) |
| NAT 감지       | 별도 확장 필요                | IKE_SA_INIT에 내장           |
| 모바일 지원    | ❌                            | ✅ MOBIKE (RFC 4555)         |
| Dead Peer 감지 | 별도 RFC (RFC 3706)           | 내장 Liveness Check          |
| EAP 인증       | 제한적                        | 지원 (RFC 7296 §2.16)        |
| 취약점         | Aggressive Mode PSK 노출 위험 | 구현·구성 취약점은 별도 검토 |

### MOBIKE (RFC 4555) — 모바일 네트워크 전환

클라이언트 IP가 변경될 때 IKE SA를 유지하면서 VPN 세션을 지속할 수 있습니다. Wi-Fi → LTE 전환 시에도 연결 유지를 지원하지만, 구현·네트워크 상태에 따라 재연결이 필요할 수 있습니다.

```
Phone (Wi-Fi 192.168.1.10)
     │
     │─── IKE SA established ─────────────────> VPN Gateway (1.2.3.4)
     │    Child SA: ESP Tunnel
     │
     │  (Wi-Fi down -> LTE up -> IP changed)
     │
Phone (LTE 10.20.30.50)
     │
     │─── INFORMATIONAL [ UPDATE_SA_ADDRESSES ] ─> VPN Gateway
     │    (notify new IP, no re-authentication)
     │
     │─── IKE SA maintained (same SPI, same session) ──> VPN Gateway
```

MOBIKE 동작 조건: 양단이 RFC 4555를 지원해야 하며, IKE_AUTH에서 MOBIKE_SUPPORTED 알림을 교환합니다.

### CREATE_CHILD_SA — SA 갱신

IKE SA 또는 Child SA의 수명이 만료되기 전에 새 SA를 협상하여 끊김 없이 갱신합니다.

```
Initiator ── CREATE_CHILD_SA (optional KE for PFS) ──> Responder
Initiator <── CREATE_CHILD_SA (response)   ─── Responder
(old SA and new SA coexist -> old SA deleted)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. OpenVPN

SSL/TLS 기반 오픈소스 VPN입니다. 일반적으로 유저스페이스에서 동작하며 Control Channel과 Data Channel을 분리합니다. TCP 443을 사용할 수 있어 일부 방화벽 환경에서 도달성이 좋아질 수 있지만, HTTPS와 동일하거나 DPI를 항상 우회하는 것은 아닙니다.

| 항목      | 값                                                       |
|-----------|----------------------------------------------------------|
| 라이선스  | GPLv2                                                    |
| 포트      | UDP 1194 (일반적 기본값) 또는 TCP 443                    |
| 암호화    | OpenSSL 기반, 설정한 TLS·data cipher                     |
| 인증      | X.509, 사용자명/비밀번호, LDAP/RADIUS, 레거시 static key |
| 모드      | TUN (Layer 3) / TAP (Layer 2)                            |
| 구현 규모 | 버전·빌드·구성에 따라 다름                               |

### Control Channel / Data Channel 분리 구조

OpenVPN의 핵심 설계는 Control Channel과 Data Channel의 분리입니다.

```
OpenVPN Packet Structure:
┌──────────────────────────────────────────────────────────────────┐
│ IP Hdr │ UDP 1194 │ OpenVPN Hdr (Op+Key) │ Payload               │
└──────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
   [Control Channel]                          [Data Channel]
   TLS 1.2/1.3 handshake                     Actual VPN traffic
   Cert exchange, session key negotiation     AEAD or cipher + HMAC
   Periodic renegotiation                     Data key management
   tls-auth / tls-crypt protection available
```

### tls-auth vs tls-crypt

Control Channel에 추가 보호 레이어를 적용하는 두 가지 방식입니다.

| 항목     | tls-auth                         | tls-crypt (권장)              |
|----------|----------------------------------|-------------------------------|
| 동작     | TLS 패킷에 HMAC 서명 추가        | TLS 패킷 전체를 암호화 + HMAC |
| 목적     | 인증되지 않은 TLS 패킷 거부      | Control Channel 내용 은닉     |
| DoS 방어 | ✅ HMAC 불일치 시 패킷 즉시 폐기 | ✅ 동일 + 서버 존재 자체 은닉 |
| 구현     | `--tls-auth ta.key 0/1`          | `--tls-crypt tc.key`          |

### TUN vs TAP 모드

| 항목     | TUN (Layer 3)            | TAP (Layer 2)              |
|----------|--------------------------|----------------------------|
| 캡슐화   | IP 패킷                  | Ethernet 프레임            |
| 브리징   | ❌                       | ✅ (VM, 게임, L2 프로토콜) |
| 오버헤드 | 낮음                     | 높음 (브로드캐스트 포함)   |
| 주 용도  | 일반 VPN (Remote Access) | 원격 네트워크 브리징       |

### Data Channel 암호화 흐름

```
Plaintext packet
    │
    v
Configured AEAD cipher encryption
    │
    v
Ciphertext + GCM Auth Tag (16 bytes)
    │
    v
OpenVPN Data Header (Packet ID + Key ID)
    │
    v
UDP/TCP transmission
```

> tls-auth: OpenVPN 제어 채널 패킷에 HMAC 서명을 추가하는 기능입니다. HMAC 불일치 패킷은 TLS 핸드셰이크 전에 즉시 폐기되어 DoS/포트 스캔 방어 효과가 있습니다. tls-crypt는 HMAC 인증을 적용하면서 제어 채널 전체를 암호화하여 내용을 숨깁니다.

OpenVPN 2.6 문서 기준으로 비-AEAD data cipher는 Encrypt-then-MAC을 사용합니다. AES-GCM 같은 AEAD cipher에서는 cipher 자체의 인증 태그를 사용하며 별도 `--auth` HMAC은 data channel에 적용되지 않습니다.

### 장단점

| 장점                                       | 단점                                          |
|--------------------------------------------|-----------------------------------------------|
| TCP 443 사용으로 일부 환경에서 도달성 개선 | 유저스페이스 동작 — 처리량은 구성·플랫폼 의존 |
| 다양한 OS 지원                             | 클라이언트 소프트웨어 설치 필요               |
| 유연한 인증 연동                           | TCP 모드 시 TCP-over-TCP 문제                 |
| tls-crypt으로 제어 채널 보호               | 설정과 구현 범위가 커질 수 있음               |

🟡 TCP 모드(TCP 443)는 일부 네트워크에서 연결 가능성을 높일 수 있지만 HTTPS와 동일한 위장을 보장하지 않습니다. TCP-over-TCP로 성능 저하가 발생할 수 있으므로, 정책상 허용되는 안정적인 네트워크에서는 UDP 모드를 우선 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. WireGuard

Jason A. Donenfeld이 설계한 현대적 VPN 프로토콜입니다. 2020년 Linux 커널 5.6에 공식 통합되었습니다. Noise Protocol Framework 기반의 단순한 설계와 최소한의 암호 프리미티브가 특징입니다.

| 항목      | 값                                          |
|-----------|---------------------------------------------|
| 개발자    | Jason A. Donenfeld                          |
| 라이선스  | GPLv2 (Linux), MIT (Go userspace)           |
| 포트      | UDP 단일 포트 (기본 51820)                  |
| 암호화    | ChaCha20, Poly1305, Curve25519, BLAKE2s     |
| 구현 규모 | 작고 단순한 설계를 지향함                   |
| 지원 구현 | Linux kernel, FreeBSD 및 Windows/macOS 구현 |
| 키 교환   | Noise Protocol Framework (IK pattern)       |

### 암호 프리미티브

WireGuard는 알고리즘 협상 없이 고정된 최신 암호화 스위트를 사용합니다.

| 역할          | 알고리즘        | 표준     |
|---------------|-----------------|----------|
| 대칭 암호화   | ChaCha20        | RFC 8439 |
| 인증 태그     | Poly1305 (AEAD) | RFC 8439 |
| ECDH 키 교환  | Curve25519      | RFC 7748 |
| 해싱/MAC      | BLAKE2s         | RFC 7693 |
| 해시테이블 키 | SipHash24       | —        |
| 키 파생       | HKDF            | RFC 5869 |

> Curve25519: Daniel J. Bernstein이 설계한 타원 곡선 Diffie-Hellman 키 교환 알고리즘(RFC 7748)입니다. 128비트 보안 수준을 제공하며, 타이밍 공격에 강하고 구현이 단순합니다. WireGuard의 키 교환과 정적 키 인증에 모두 사용됩니다.

> HKDF(HMAC-based Key Derivation Function, RFC 5869): 마스터 시크릿에서 여러 개의 암호화 키를 안전하게 파생하는 함수입니다. Extract 단계에서 엔트로피를 정규화하고 Expand 단계에서 필요한 길이의 키를 생성합니다.

협상 없이 고정 스위트를 사용하는 이유: 취약한 알고리즘 선택 공격(downgrade attack)을 원천 차단합니다.

### Noise IK 핸드셰이크 (1-RTT)

> Noise Protocol Framework: Jason Donenfeld가 WireGuard 설계에 채택한 암호화 핸드셰이크 프레임워크입니다. IK 패턴에서 I는 Initiator가 자신의 정적 키를 전송함을, K는 Responder의 정적 키가 사전에 알려짐(Known)을 의미합니다. 1-RTT로 상호 인증과 키 교환을 완료합니다.

```
Initiator                                      Responder
    │                                               │
    │── Handshake Initiation ─────────────────>     │
    │   ephemeral public key (Ei)                   │
    │   encrypted static public key (Si, AEAD)      │
    │   encrypted timestamp (AEAD)                  │
    │   (Curve25519 DH: Ei*Sr, Si*Sr)               │
    │                                               │
    │ <── Handshake Response ──────────────────     │
    │     ephemeral public key (Er)                 │
    │     empty AEAD (confirm)                      │
    │     (DH: Er*Ei, Er*Si -> session keys derived)│
    │                                               │
    │  (handshake complete — 1 RTT)                 │
    │                                               │
    │── Data Packet ─────────────────────────>      │
    │   Counter + ChaCha20-Poly1305(Payload)        │
```

세션 키는 핸드셰이크마다 새로 파생되어 **Perfect Forward Secrecy**를 제공합니다. WireGuard의 `REKEY_AFTER_TIME` 기본값은 120초(2분)이며, 메시지 수명·트래픽·재키 조건에 따라 핸드셰이크가 수행됩니다.

### Cryptokey Routing

WireGuard는 IP 라우팅 테이블 대신 **공개키 ↔ AllowedIPs 매핑**으로 패킷을 라우팅합니다.

```
Outbound:
Dst IP ── AllowedIPs lookup ──> Peer public key determined
                              ──> encrypt with that peer's session key

Inbound:
decrypt -> check source IP against peer's AllowedIPs ──> allow/drop
```

설정 예시:

```ini
[Interface]
PrivateKey = <client-private-key>
Address    = 10.0.0.2/24

[Peer]
PublicKey  = <server-public-key>
Endpoint   = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0   # route all traffic through VPN
```

AllowedIPs = `0.0.0.0/0`이면 모든 트래픽이 VPN을 통과하고, 특정 CIDR만 지정하면 Split Tunnel로 동작합니다.

### Silent Peer / Roaming

WireGuard는 명시적 세션 개념이 없습니다. 패킷을 수신하면 소스 IP와 포트를 자동으로 Endpoint로 갱신합니다. 이를 통해 클라이언트 IP가 변경되어도 자동으로 Roaming이 지원됩니다.

```
Client (IP: 1.2.3.4) ── Data Packet ──> Server
Server: "record Peer X endpoint = 1.2.3.4:12345"

Client (IP changed to 5.6.7.8) ── Data Packet ──> Server
Server: "auto-update Peer X endpoint = 5.6.7.8:54321"
```

### DoS 방어 — Cookie 메커니즘

핸드셰이크 요청이 과도할 때 Responder는 CPU 집약적인 DH 연산 전에 Cookie(MAC 기반 챌린지)를 요청합니다.

```
Under load:
Initiator ── Handshake Initiation ──> Responder
Initiator <── Cookie Reply (MAC2 challenge) ─── Responder
Initiator ── Handshake Initiation (with MAC2) ──> Responder
(DH computation only after MAC2 verified)
```

> WireGuard Cookie 메커니즘: 과부하 시 Responder가 MAC2 챌린지를 전송하여, Initiator가 올바른 MAC2를 포함한 메시지를 재전송할 때만 DH 연산을 수행합니다. 이로써 IP 위조 기반 DH 연산 소모 공격(DDoS)을 방어합니다.

### 장단점

| 장점                       | 단점                                   |
|----------------------------|----------------------------------------|
| 단순한 설계                | 고정 암호 스위트 (알고리즘 선택 불가)  |
| 커널 공간 처리 — 높은 성능 | UDP only — 일부 방화벽/DPI 차단 가능   |
| 1-RTT 핸드셰이크           | 동적 IP 할당 미내장 (wg-quick 등 별도) |
| Roaming 지원               | TCP 443 위장 불가                      |
| PFS 자동 보장 (세션 재키)  | 연결 상태 없음 — 로깅/감사 어려움      |

[⬆ 목차로 돌아가기](#목차)


---

## 9. 프로토콜 비교

### 보안 / 성능 / 운용성 종합 비교

| 항목            | PPTP                         | L2TP/IPsec       | IKEv2/IPsec      | OpenVPN          | WireGuard             |
|-----------------|------------------------------|------------------|------------------|------------------|-----------------------|
| 보안            | ❌ 취약                      | 구성에 따라 다름 | 구성에 따라 다름 | 구성에 따라 다름 | 구성에 따라 다름      |
| 암호화 알고리즘 | RC4 (취약)                   | AES-CBC/GCM      | AES-GCM          | 설정한 cipher    | ChaCha20              |
| PFS             | ❌                           | 설정 시 가능     | 설정 시 가능     | 구성에 따름      | 세션 재키             |
| 속도            | 환경 의존                    | 환경 의존        | 환경 의존        | 환경 의존        | 환경 의존             |
| 오버헤드        | 구현·암호화 방식에 따라 가변 | 가변             | 가변             | 가변             | 데이터 패킷 기준 가변 |
| NAT 통과        | 어려움                       | NAT-T 사용       | NAT-T 사용       | TCP/UDP 선택     | UDP 단일              |
| 모바일 로밍     | ❌                           | 제한적           | ✅ MOBIKE        | 구현·구성 의존   | ✅ Endpoint 갱신      |
| 방화벽 도달성   | 낮음                         | 낮음             | 보통             | TCP 443 가능     | UDP 정책 의존         |
| 구현 규모       | 레거시                       | 구현별 상이      | 구현별 상이      | 구현별 상이      | 단순한 설계           |
| OS 기본 지원    | Windows                      | 운영체제별 상이  | 운영체제별 상이  | 클라이언트 필요  | 다양한 구현           |
| 표준 / RFC      | RFC 2637                     | RFC 2661+4301    | RFC 7296         | 비표준           | 비표준                |
| 상태            | 폐기                         | 레거시           | 현역             | 현역             | 현역                  |

> PFS(Perfect Forward Secrecy): 세션 키가 노출되더라도 과거의 다른 세션 키는 영향을 받지 않도록 매 세션마다 독립적인 키를 생성하는 특성입니다. Diffie-Hellman 임시 키 교환(Ephemeral DH)으로 구현하며, 장기 키 탈취 시 과거 통신 내용을 보호합니다.

### 포트 / 프로토콜 요약

| VPN 프로토콜 | 필요 포트 / 프로토콜             | 방화벽 규칙                                   |
|--------------|----------------------------------|-----------------------------------------------|
| PPTP         | TCP 1723 + GRE (IP Protocol 47)  | GRE 허용 필요 — NAT 통과 어려움               |
| L2TP/IPsec   | UDP 500, 4500; 1701은 IPsec 내부 | NAT 환경에서 500/4500 허용                    |
| IKEv2        | UDP 500, 4500                    | 2개 포트 허용                                 |
| OpenVPN      | UDP 1194 또는 TCP 443            | 단일 포트 (TCP 443이 HTTPS와 동일하지는 않음) |
| WireGuard    | UDP 51820 (변경 가능)            | 단일 UDP 포트 허용                            |

### 핸드셰이크 메시지 수 비교

| 프로토콜        | 대표 교환              | RTT/메시지 특성                     | 비고                                |
|-----------------|------------------------|-------------------------------------|-------------------------------------|
| PPTP            | TCP + 제어 채널 + PPP  | 구현·인증 협상에 따라 다름          | GRE data channel                    |
| IKEv1 Main Mode | Main Mode + Quick Mode | Main 6개, Quick 3개 메시지          | 구성에 따라 달라짐                  |
| L2TP/IPsec      | IKE + L2TP + PPP       | 각 단계와 인증 방식에 따라 다름     | 고정 RTT로 비교하기 어려움          |
| IKEv2           | IKE_SA_INIT + IKE_AUTH | 기본 4개 메시지, 보통 2 RTT         | EAP 사용 시 추가 교환 가능          |
| OpenVPN         | TLS + VPN control      | TLS 버전·구성·재개 여부에 따라 다름 | 0-RTT를 일반 동작으로 간주하지 않음 |
| WireGuard       | Initiation + Response  | 기본 2개 메시지, 1 RTT              | Noise IK                            |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 선택 가이드

### 용도별 권장 프로토콜

| 용도                      | 권장 프로토콜        | 이유                                           |
|---------------------------|----------------------|------------------------------------------------|
| Site-to-Site (IDC/Cloud)  | IKEv2/IPsec          | AWS/GCP/Azure에서 표준 지원, 장비 호환성 우수  |
| 모바일 Remote Access      | IKEv2 또는 WireGuard | MOBIKE/Roaming으로 네트워크 전환 시 연결 유지  |
| 제한된 방화벽 환경        | OpenVPN (TCP 443)    | 일부 환경에서 도달성 개선; 식별 불가 보장 없음 |
| 고성능 (게임, 스트리밍)   | WireGuard            | 최소 오버헤드, 커널 공간 처리                  |
| 클라이언트 설치 불가 환경 | IKEv2/IPsec          | OS 기본 내장, 추가 설치 없음                   |
| 레거시 장비 호환          | L2TP/IPsec           | 구형 라우터/방화벽 지원                        |
| ❌ 사용 금지              | PPTP                 | 알려진 취약점으로 신규 사용 금지               |

### 환경별 판단 기준

```
New deployment?
      │
      ├── Yes
      │       │
      │       ├── Mobile/roaming critical? ──> IKEv2 or WireGuard
      │       │
      │       ├── Firewall bypass needed? ───> OpenVPN (TCP 443)
      │       │
      │       ├── Site-to-Site? ──────────────> IKEv2/IPsec
      │       │
      │       └── High-perf P2P? ─────────────> WireGuard
      │
      └── No (legacy maintenance)
              │
              ├── PPTP? ─────────────────────> plan migration immediately
              │
              └── L2TP/IPsec? ───────────────> consider migrating to IKEv2
```

### AWS VPN 연동

| AWS 서비스       | 지원 프로토콜                   | 비고                               |
|------------------|---------------------------------|------------------------------------|
| Site-to-Site VPN | IKEv1/IKEv2 + IPsec             | BGP 또는 Static 라우팅             |
| Client VPN       | OpenVPN 기반                    | 인증서·사용자 인증 등 구성 지원    |
| EC2 자체 구축    | WireGuard, OpenVPN 등           | AMI에 직접 설치, SG 포트 허용 필요 |
| Transit Gateway  | VPN attachment 또는 TGW Connect | VPN은 IPsec, Connect는 GRE/BGP     |

### 보안 수준 요약

```
Security assessment:

WireGuard         ── 고정된 현대적 암호 조합, 세션 재키
IKEv2/IPsec       ── 표준 기반, 알고리즘·구성·구현 검토 필요
OpenVPN           ── TLS와 data cipher 구성 및 인증 방식 검토 필요
L2TP/IPsec        ── IPsec 구성에 의존, 레거시 호환성 중심
─────────────────────────────────────────────────────
PPTP              ── ❌ 신규 사용 금지
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- RFC 2637: Point-to-Point Tunneling Protocol (PPTP)
- RFC 2661: Layer Two Tunneling Protocol "L2TP"
- RFC 3931: Layer Two Tunneling Protocol - Version 3 (L2TPv3)
- RFC 4301: Security Architecture for the Internet Protocol (IPsec)
- RFC 4303: IP Encapsulating Security Payload (ESP)
- RFC 7296: Internet Key Exchange Protocol Version 2 (IKEv2)
- RFC 4555: IKEv2 Mobility and Multihoming Protocol (MOBIKE)
- RFC 3947: Negotiation of NAT-Traversal in the IKE
- RFC 8221: Cryptographic Algorithm Implementation Requirements for ESP and AH (2017)
- RFC 7693: The BLAKE2 Cryptographic Hash and Message Authentication Code
- RFC 7748: Elliptic Curves for Diffie-Hellman Key Agreement (Curve25519)
- WireGuard: [wireguard.com/protocol](https://www.wireguard.com/protocol/) — ★★★☆☆
- WireGuard Whitepaper: [wireguard.com/papers](https://www.wireguard.com/papers/wireguard.pdf) — ★★★★☆
- OpenVPN: [openvpn.net/community-resources](https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/) — ★★★☆☆
- Noise Protocol: [noiseprotocol.org](https://noiseprotocol.org/noise.html) — ★★★☆☆

---

**작성일**: 2026-06-29

**마지막 업데이트**: 2026-08-10

© 2026 siasia86. Licensed under CC BY 4.0.
