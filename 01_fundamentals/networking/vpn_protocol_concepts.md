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

> AEAD(Authenticated Encryption with Associated Data): 암호화와 무결성 검증을 동시에 수행하는 암호화 방식입니다. AES-GCM, ChaCha20-Poly1305가 대표적이며, 별도의 MAC 계산 없이 단일 패스로 처리합니다.

> HMAC(Hash-based Message Authentication Code): 해시 함수(SHA-256 등)와 비밀 키를 조합하여 메시지 무결성과 인증을 동시에 검증하는 알고리즘입니다. 송신자와 수신자가 동일한 비밀 키를 공유하며, 수신 측은 HMAC 태그를 재계산하여 전송 중 변조 여부를 확인합니다.
| 인증   | 상대방이 신뢰된 피어임을 키 교환/인증서로 검증합니다.         |

### 캡슐화 구체 예시

#### WireGuard 터널 통과 — `curl http://192.0.2.1` 요청

```
─── 원본 패킷 (터널 진입 전) ────────────────────────────────────────
  IP  Src: 10.0.0.2      Dst: 192.0.2.1
  TCP Src: 54321         Dst: 80
  HTTP Payload: "GET / HTTP/1.1\r\nHost: 192.0.2.1"

─── WireGuard 캡슐화 후 (인터넷 구간에 실제로 흐르는 패킷) ──────────
  IP  Src: 192.0.2.100   Dst: 203.0.113.1     <-- 공인 IP만 노출
  UDP Src: 51820         Dst: 51820
  [ WireGuard Header: Type | Receiver ID | Counter ]
  [ ChaCha20-Poly1305 Encrypted {
        IP  Src: 10.0.0.2  Dst: 192.0.2.1     <-- 원본 IP (숨겨짐)
        TCP Src: 54321     Dst: 80
        HTTP: "GET / HTTP/1.1..."              <-- 내용 (숨겨짐)
    }
    Auth Tag (16 bytes)                        <-- 무결성 태그
  ]
```

중간자(ISP, 공유기)가 볼 수 있는 것: `192.0.2.100 → 203.0.113.1 UDP/51820` 뿐
중간자가 볼 수 없는 것: 목적지(`192.0.2.1`), 포트(`80`), 내용(`GET /...`)

#### 프로토콜별 캡슐화 레이어 비교

```
원본: [ IP | TCP | HTTP ]

IPsec (ESP):
  [ Outer IP | ESP Hdr | Encrypted(IP | TCP | HTTP) | ESP Trailer | Auth Tag ]

L2TP/IPsec:
  [ Outer IP | UDP/4500 | ESP | UDP/1701 | L2TP | PPP | IP | TCP | HTTP ]
  └──────────── IPsec 암호화 범위 ──────────────────────────────┘

OpenVPN (UDP):
  [ Outer IP | UDP/1194 | OpenVPN Hdr | HMAC | Encrypted(IP | TCP | HTTP) ]

WireGuard:
  [ Outer IP | UDP/51820 | WG Hdr | ChaCha20(IP | TCP | HTTP) | Auth Tag ]

SoftEther (SSL-VPN):
  [ Outer IP | TCP/443 | TLS Record | Ethernet Frame(IP | TCP | HTTP) ]
  └── HTTPS 트래픽과 동일하게 보임 ──┘
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

일반 HTTPS 트래픽과 구분이 안 됩니다. DPI 장비도 내부 VPN 트래픽 식별이 어렵습니다.

> DPI(Deep Packet Inspection): 방화벽이 패킷 헤더뿐 아니라 페이로드 내용까지 분석하여 특정 애플리케이션이나 프로토콜을 식별·차단하는 기법입니다. 포트만 보는 일반 방화벽과 달리 TLS 핑거프린트나 트래픽 패턴으로 VPN을 탐지합니다.

| 관찰 지점                  | 보이는 것                              | 보이지 않는 것           |
|----------------------------|----------------------------------------|--------------------------|
| `eth0` (인터넷 구간)       | 터널 엔드포인트 IP/포트, 암호화된 길이 | 목적지, 원본 포트, 내용  |
| `wg0` / `tun0` (터널 내부) | 복호화된 원본 패킷 전체                | -                        |
| SoftEther `eth0` (TCP 443) | HTTPS 트래픽과 동일하게 보임           | VPN 여부조차 식별 어려움 |



### NAT-T (NAT Traversal) 원리

IPsec ESP는 IP Protocol 50으로 전송되는데, NAT 장비는 TCP/UDP 포트를 기반으로 변환하므로 ESP 패킷을 처리하지 못합니다. 이를 해결하기 위해 ESP를 UDP로 감싸는 NAT-T(RFC 3947)를 사용합니다.

```
Without NAT-T (ESP blocked by NAT):
Host A ──[ ESP/50 ]──> [NAT] ──X──> VPN Gateway

With NAT-T (ESP encapsulated in UDP 4500):
Host A ──[ UDP 4500 [ ESP ] ]──> [NAT] ──[ UDP 4500 [ ESP ] ]──> VPN Gateway
```

NAT-T는 IKE 협상 중 양단이 UDP 4500으로 자동 전환하며, RFC 3947/3948에 정의되어 있습니다.

### UDP 터널과 TCP 신뢰성

대부분의 VPN은 내부 TCP 트래픽을 UDP로 감싸서 전송합니다. 신뢰성은 어디서 보장되는지 설명합니다.

#### 계층별 역할 분리

```
Application (curl, ssh, ...)
    │
    v
TCP (신뢰성 담당: ACK, 재전송, 흐름제어, 순서 보장)
    │
    v
IP 패킷
    │
    v  ── VPN 캡슐화 ──
UDP (전송 수단: 비연결, 신뢰성 없음)
    │
    v
Internet
```

VPN은 IP 패킷 전체를 캡슐화하므로 내부 TCP 계층이 그대로 살아 있습니다.
UDP 구간에서 패킷이 유실되면 내부 TCP가 타임아웃 후 자동 재전송합니다.
애플리케이션 입장에서는 VPN 터널의 존재를 알 수 없습니다.

#### VPN이 UDP를 선호하는 이유 — TCP meltdown

VPN 터널 자체를 TCP로 구성하면 내부/외부 두 TCP 재전송 로직이 충돌합니다.

```
[TCP meltdown 발생 시나리오]

외부 TCP: 패킷 유실 감지 → 재전송 대기 (윈도우 축소)
    │
    └─ 내부 TCP: 동시에 타임아웃 감지 → 자체 재전송 시도
                    │
                    └─ 외부 TCP가 아직 대기 중 → 내부 재전송 패킷도 지연
                            │
                            └─ 내부 TCP RTT 급증 → 추가 타임아웃 → 연쇄 재전송
```

외부를 UDP로 쓰면 재전송 판단은 내부 TCP 하나만 합니다.
두 레이어가 독립적으로 동작하여 연쇄 지연이 발생하지 않습니다.

#### 프로토콜별 전송 방식

| VPN           | 기본 전송    | TCP 모드   | TCP meltdown 위험 | 비고                        |
|---------------|--------------|------------|-------------------|-----------------------------|
| WireGuard     | UDP 전용     | ❌ 불가    | 없음              | UDP 차단 환경 사용 불가     |
| IPsec (IKEv2) | UDP 500/4500 | ❌ 불가    | 없음              | NAT-T로 UDP 캡슐화          |
| OpenVPN       | UDP 1194     | ✅ TCP 443 | 🟡 있음           | TCP 모드는 방화벽 우회용    |
| SoftEther     | TCP 443/992  | TCP 기본   | 🟡 있음           | 병렬 TCP 1~32개로 영향 분산 |

🟡 OpenVPN/SoftEther의 TCP 모드는 UDP가 차단된 환경에서의 대안입니다. 성능보다 통과 가능성을 우선할 때 사용하며, 안정적인 네트워크에서는 UDP 모드 대비 처리량이 낮을 수 있습니다.

### 세대별 발전

```
1996        1999           2001        2005        2006       2020
 │           │              │           │           │          │
 v           v              v           v           v          v
PPTP ──> L2TP/IPsec ──> OpenVPN ──> L2TPv3 ──> IKEv2 ──> WireGuard
(dead)   (legacy)       (mature)   (service)   (mobile)   (modern)
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

Point-to-Point Tunneling Protocol. Microsoft가 1996년 개발한 최초의 상용 VPN 프로토콜입니다. RFC 2637(Informational — IETF 비표준)로 등록되어 있으며, 현재는 보안 취약점으로 사용이 금지됩니다.

| 항목   | 값                               |
|--------|----------------------------------|
| 개발사 | Microsoft                        |
| RFC    | RFC 2637 (Informational, 비표준) |
| 포트   | TCP 1723 + GRE (Protocol 47)     |

> GRE(Generic Routing Encapsulation, RFC 2784): IP 패킷을 다른 IP 패킷 안에 캡슐화하는 터널링 프로토콜입니다. TCP/UDP가 아닌 IP Protocol 47번을 사용하므로 NAT 장비가 포트 변환을 할 수 없어 NAT 통과가 어렵습니다.
| 암호화    | MPPE (RC4, 40~128bit)                |

> MPPE(Microsoft Point-to-Point Encryption): PPP 프레임을 RC4 스트림 암호로 암호화하는 Microsoft 독자 규격입니다. MS-CHAPv2에서 파생된 키를 사용하며, MS-CHAPv2가 크랙되면 MPPE 세션 키도 자동으로 노출됩니다.
| 인증      | MS-CHAPv2                            |
| 보안 상태 | ❌ 완전히 크랙됨 (2012년 Moxie 공개) |
| 현재 용도 | 레거시 호환 외 사용 금지             |

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

GRE 헤더에는 Key(터널 ID)와 Sequence Number가 포함되며, PPP 프레임을 그대로 캡슐화합니다.

> PPP(Point-to-Point Protocol, RFC 1661): 두 노드 간 직렬 링크에서 인증(PAP/CHAP), IP 주소 할당(IPCP), 압축(CCP)을 처리하는 데이터 링크 계층 프로토콜입니다. PPTP/L2TP는 PPP를 터널 안에서 재활용하여 인증과 IP 할당을 처리합니다.

### MS-CHAPv2 크랙 메커니즘

2012년 Moxie Marlinspike와 David Hulton이 MS-CHAPv2가 사실상 단일 DES 키 3개로 분리된다는 점을 이용해 CloudCracker 서비스로 24시간 이내에 100% 해독 가능함을 공개했습니다.

```
MS-CHAPv2 Challenge-Response 구조:
Server Challenge (8 bytes)
       │
       v
Client NTLM Hash (16 bytes)
       │
       v  3개 DES 키로 분할 (7+7+2 bytes)
       ├── DES(key1, challenge) ──> Response_1  (8 bytes)
       ├── DES(key2, challenge) ──> Response_2  (8 bytes)
       └── DES(key3+00000, challenge) ──> Response_3  (8 bytes)

→ 마지막 키가 2 bytes 유효 → 전수조사 65,536가지
→ key3 해독 후 key1, key2도 DES brute-force로 해독
→ NTLM Hash → 원본 패스워드 복구 가능
```

### 보안 취약점 정리

| 취약점            | 영향                                       |
|-------------------|--------------------------------------------|
| MS-CHAPv2 크랙    | 2012년 CloudCracker로 24h 이내 100% 해독   |
| RC4 스트림 암호   | 키 재사용 취약, bit-flipping 공격 가능     |
| GRE 무결성 없음   | ACK 번호 예측으로 패킷 주입/세션 탈취 가능 |
| MPPE 키 파생 취약 | MS-CHAPv2 해독 시 MPPE 세션 키도 자동 노출 |

🟡 PPTP는 어떤 환경에서도 신규 도입하면 안 됩니다. 기존 레거시 시스템에서만 잔존합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. L2TP

Layer 2 Tunneling Protocol. Cisco의 L2F와 Microsoft의 PPTP를 통합하여 IETF가 표준화한 프로토콜입니다. **자체 암호화가 없어** 반드시 IPsec과 조합해야 합니다.

| 항목        | 값                                               |
|-------------|--------------------------------------------------|
| 표준        | RFC 2661 (L2TPv2, 1999), RFC 3931 (L2TPv3, 2005) |
| 포트        | UDP 1701                                         |
| 자체 암호화 | ❌ 없음 — IPsec 조합 필수                        |
| 인증        | 제어 메시지에 선택적 CHAP/HMAC-MD5               |
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
 ├── SCCRQ (Start-Control-Conn Req) ──> │   Tunnel 수립 요청
 │ <── SCCRP (Reply)                ─── │   Tunnel 수립 응답
 ├── SCCCN (Connected)              ──> │   Tunnel 확립
 │                                      │
 ├── ICRQ  (Incoming-Call Req)      ──> │   Session 요청
 │ <── ICRP (Reply)                 ─── │   Session 응답
 ├── ICCN  (Connected)              ──> │   Session 확립
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
원본:  [ IP Hdr(A→B) | TCP | Data ]
결과:  [ IP Hdr(A→B) | ESP Hdr | TCP | Data | ESP Trailer | ESP Auth ]
        (원본 IP 유지)  (암호화 범위: TCP~ESP Trailer)

Tunnel Mode (Gateway-to-Gateway):
원본:  [ IP Hdr(A→B) | TCP | Data ]
결과:  [ New IP Hdr(GW1→GW2) | ESP Hdr | IP Hdr(A→B) | TCP | Data | ESP Trailer | ESP Auth ]
        (게이트웨이 IP)          (암호화 범위: 원본 IP 헤더 포함 전체)
```

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
Outbound 패킷 처리 흐름:

Packet (src:A, dst:B, proto:TCP)
        │
        v
    [SPD 조회] ── 트래픽 셀렉터 매칭
        │
        ├── Bypass  ──> 암호화 없이 전송
        ├── Discard ──> 패킷 폐기
        └── Protect ──> [SAD 조회]
                              │
                        SA 존재? ──No──> IKE 협상 후 SA 생성
                              │
                             Yes
                              │
                              v
                         ESP/AH 적용 후 전송
```

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
Phase 1 — IKE SA 수립 (Main Mode, 6 messages):

Initiator                           Responder
    │── SA (암호화 제안)           ──>  │
    │ <── SA (선택된 제안)         ───  │
    │── KE + Nonce (DH 공개값)    ──>  │
    │ <── KE + Nonce              ───  │
    │  (DH 완료 → 공유 비밀 생성)       │
    │── ID + AUTH (암호화됨)      ──>  │
    │ <── ID + AUTH               ───  │
    │  (ISAKMP SA 확립)                │

> ISAKMP(Internet Security Association and Key Management Protocol, RFC 2408): IKE의 메시지 형식과 SA 협상 절차를 정의하는 프레임워크입니다. IKEv1/v2 모두 ISAKMP 메시지 구조를 기반으로 동작합니다.

Phase 2 — IPsec SA 수립 (Quick Mode, 3 messages):

    │── SA + Nonce + ID (암호화)  ──>  │
    │ <── SA + Nonce + ID         ───  │
    │── Hash (확인)               ──>  │
    │  (Child SA = ESP/AH SA 확립)     │
```

### 필수 암호 알고리즘 (RFC 8221, 2017)

| 용도   | MUST                | SHOULD             | MAY              |
|--------|---------------------|--------------------|------------------|
| 암호화 | AES-CBC, AES-GCM-16 | ChaCha20-Poly1305  | AES-CCM-8        |
| 무결성 | HMAC-SHA-256-128    | AES-GMAC           | HMAC-SHA-512-256 |
| DH     | Group 14 (2048bit)  | Group 19 (ECP-256) | Group 20         |

[⬆ 목차로 돌아가기](#목차)


---

## 5. L2TP/IPsec

L2TP 터널을 IPsec ESP Tunnel Mode로 감싸는 조합입니다. L2TP가 PPP 세션을 제공하고, IPsec이 암호화를 담당합니다. Windows/macOS/iOS에 기본 내장되어 있어 별도 클라이언트 없이 사용 가능합니다.

| 항목         | 값                                                 |
|--------------|----------------------------------------------------|
| 포트         | UDP 500 (IKE) + UDP 4500 (NAT-T) + UDP 1701 (L2TP) |
| 암호화       | IPsec ESP (AES-256 권장)                           |
| 인증         | IKE PSK 또는 X.509 인증서                          |
| 이중 캡슐화  | ✅ (L2TP over IPsec)                               |
| NAT 통과     | NAT-T (UDP 4500) 필수                              |
| OS 기본 지원 | Windows, macOS, iOS, Android                       |

### 연결 수립 순서

L2TP/IPsec은 IPsec이 먼저 수립된 후 그 안에서 L2TP가 동작합니다.

```
1. IKE Phase 1 (UDP 500 → 4500)
   Client ── IKE_SA_INIT ──> Server
   (IPsec 보안 채널 수립)

2. IKE Phase 2 (UDP 4500, ESP Tunnel Mode)
   Client ── IKE_AUTH ──> Server
   (IPsec SA 수립 → 이후 UDP 1701 트래픽을 ESP로 보호)

3. L2TP Tunnel 수립 (UDP 1701, IPsec 내부)
   Client ── SCCRQ ──> Server
   Client ── ICRQ  ──> Server
   (L2TP Session 확립)

4. PPP 협상 (L2TP 내부)
   LCP → Authentication → NCP (IP 주소 할당)

> LCP(Link Control Protocol): PPP 링크 파라미터(MRU, 인증 방식)를 협상하는 제어 프로토콜입니다. NCP(Network Control Protocol)는 상위 네트워크 프로토콜 설정을 담당하며, IP 주소 할당은 NCP의 일종인 IPCP(IP Control Protocol)가 처리합니다.
   (VPN IP 획득)
```

### 패킷 구조 및 오버헤드

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Outer IP │ UDP 4500 │ ESP Hdr │ UDP 1701 │ L2TP │ PPP │ Inner IP │ Payload │
└────────────────────────────────────────────────────────────────────────────┘
  20 bytes   8 bytes   8 bytes   8 bytes   8 bytes 4 bytes  20 bytes
  └── NAT-T ──┘  └────────── IPsec encryption range ────────────────────────┘
```

오버헤드 합계: 약 **76 bytes** (NAT-T 환경 기준). WireGuard 32 bytes 대비 2배 이상입니다.

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

> MOBIKE(IKEv2 Mobility and Multihoming, RFC 4555): IKE SA를 재협상 없이 유지한 채 IP 주소가 변경되어도 세션을 지속하는 기능입니다. Wi-Fi ↔ LTE 전환 시 VPN 연결이 끊기지 않는 핵심 메커니즘입니다.

| 항목         | 값                                         |
|--------------|--------------------------------------------|
| 표준         | RFC 7296 (2014), RFC 4555 (MOBIKE)         |
| 포트         | UDP 500 + UDP 4500 (NAT-T)                 |
| 암호화       | IPsec ESP (AES-GCM, ChaCha20-Poly1305 등)  |
| 특징         | MOBIKE — 네트워크 전환 시 세션 유지        |
| OS 기본 지원 | Windows 7+, macOS 10.11+, iOS, Android 11+ |
| 핵심 강점    | 모바일 로밍, 빠른 재연결                   |

### IKEv2 4개 메시지 교환 흐름

IKEv2는 IKEv1의 9개 메시지를 4개로 압축했습니다.

```
Initiator                                       Responder
    │                                               │
    │── IKE_SA_INIT (1) ─────────────────────────>  │
    │   SAi1 (암호화 제안)                           │
    │   KEi (DH 공개값)                              │
    │   Ni (Nonce)                                   │
    │                                               │
    │ <── IKE_SA_INIT (2) ────────────────────────  │
    │     SAr1 (선택된 제안)                         │
    │     KEr (DH 공개값)                            │
    │     Nr (Nonce)                                 │
    │     (여기서 DH 완료 → SK_d, SK_a, SK_e 파생)  │
    │                                               │
    │── IKE_AUTH (3) ───────────────────────────>   │  [암호화]
    │   IDi (Initiator ID)                          │
    │   AUTH (서명 또는 PSK 증명)                   │
    │   SAi2 (Child SA 제안)                        │
    │   TSi, TSr (트래픽 셀렉터)                    │
    │                                               │
    │ <── IKE_AUTH (4) ─────────────────────────    │  [암호화]
    │     IDr (Responder ID)                        │
    │     AUTH                                      │
    │     SAr2 (Child SA 선택)                      │
    │     TSi, TSr                                  │
    │     (IKE SA + Child SA 확립 완료)             │
```

IKE_SA_INIT에서 DH 키 교환이 완료되므로, IKE_AUTH부터는 모든 페이로드가 암호화됩니다.

### IKEv1 vs IKEv2

| 항목           | IKEv1 (Main Mode)             | IKEv2                        |
|----------------|-------------------------------|------------------------------|
| 메시지 수      | Phase 1: 6 + Phase 2: 3 = 9   | 4개 (IKE_SA_INIT + IKE_AUTH) |
| NAT 감지       | 별도 확장 필요                | IKE_SA_INIT에 내장           |
| 모바일 지원    | ❌                            | ✅ MOBIKE (RFC 4555)         |
| Dead Peer 감지 | 별도 RFC (RFC 3706)           | 내장 Liveness Check          |
| EAP 인증       | 제한적                        | 완전 지원 (RFC 7296 §2.16)   |
| 취약점         | Aggressive Mode PSK 노출 위험 | 없음                         |

### MOBIKE (RFC 4555) — 모바일 네트워크 전환

클라이언트 IP가 변경될 때 VPN 세션을 재인증 없이 유지합니다. Wi-Fi → LTE 전환 시에도 끊김 없이 동작합니다.

```
Phone (Wi-Fi 192.168.1.10)
     │
     │─── IKE SA established ─────────────────> VPN Gateway (1.2.3.4)
     │    Child SA: ESP Tunnel
     │
     │  (Wi-Fi 해제 → LTE 연결 → IP 변경)
     │
Phone (LTE 10.20.30.50)
     │
     │─── INFORMATIONAL [ UPDATE_SA_ADDRESSES ] ─> VPN Gateway
     │    (새 IP 주소 통보, 재인증 없음)
     │
     │─── IKE SA 유지 (동일 SPI, 동일 세션) ────> VPN Gateway
```

MOBIKE 동작 조건: 양단이 RFC 4555를 지원해야 하며, IKE_AUTH에서 MOBIKE_SUPPORTED 알림을 교환합니다.

### CREATE_CHILD_SA — SA 갱신

IKE SA 또는 Child SA의 수명이 만료되기 전에 새 SA를 협상하여 끊김 없이 갱신합니다.

```
Initiator ── CREATE_CHILD_SA (새 DH 포함) ──> Responder
Initiator <── CREATE_CHILD_SA (응답)       ─── Responder
(기존 SA와 새 SA 동시 존재 → 기존 SA 삭제)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. OpenVPN

SSL/TLS 기반 오픈소스 VPN입니다. 유저스페이스에서 동작하며 TLS 위에 Control Channel과 Data Channel을 분리하여 운용합니다. TCP 443 사용으로 방화벽/DPI 우회에 강점이 있습니다.

| 항목      | 값                                 |
|-----------|------------------------------------|
| 라이선스  | GPLv2                              |
| 포트      | UDP 1194 (기본) 또는 TCP 443 위장  |
| 암호화    | OpenSSL (AES-256-GCM, TLS 1.2/1.3) |
| 인증      | X.509 인증서, PSK, LDAP, RADIUS    |
| 모드      | TUN (Layer 3) / TAP (Layer 2)      |
| 코드 규모 | ~100,000줄 (WireGuard 대비 25배)   |

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
   TLS 1.2/1.3 handshake                     AES-256-GCM + HMAC
   Cert exchange, session key negotiation     Actual VPN traffic
   Periodic renegotiation                     Encrypt-then-MAC
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
평문 패킷
    │
    v
AES-256-GCM 암호화
    │
    v
암호문 + GCM Auth Tag (16 bytes)
    │
    v   (tls-auth 사용 시 추가 HMAC)
OpenVPN Data Header (Packet ID + Key ID)
    │
    v
UDP/TCP 전송
```

OpenVPN은 Encrypt-then-MAC 방식을 사용합니다. 암호화 후 MAC을 계산하므로, MAC 검증 실패 시 복호화 전에 패킷을 폐기합니다. (RFC 7366)

### 장단점

| 장점                         | 단점                                      |
|------------------------------|-------------------------------------------|
| TCP 443 사용으로 방화벽 우회 | 유저스페이스 동작 — 커널 대비 처리량 낮음 |
| 모든 OS 지원                 | 클라이언트 소프트웨어 설치 필요           |
| 20년+ 보안 감사 이력         | 설정 복잡 (PKI 인프라 필요)               |
| 유연한 인증 연동             | TCP 모드 시 TCP-over-TCP 문제             |
| tls-crypt으로 서버 은닉 가능 | 코드 규모 크고 공격 표면 넓음             |

🟡 TCP 모드(TCP 443)는 방화벽 우회에 유효하지만, TCP-over-TCP로 인한 성능 저하가 발생합니다. 가능하면 UDP 모드를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. WireGuard

Jason A. Donenfeld이 설계한 현대적 VPN 프로토콜입니다. 2020년 Linux 커널 5.6에 공식 통합되었습니다. Noise Protocol Framework 기반의 단순한 설계와 최소한의 암호 프리미티브가 특징입니다.

| 항목      | 값                                      |
|-----------|-----------------------------------------|
| 개발자    | Jason A. Donenfeld                      |
| 라이선스  | GPLv2 (Linux), MIT (Go userspace)       |
| 포트      | UDP 단일 포트 (기본 51820)              |
| 암호화    | ChaCha20, Poly1305, Curve25519, BLAKE2s |
| 코드 규모 | ~4,000줄 (커널 모듈)                    |
| 커널 통합 | Linux 5.6+, FreeBSD, Windows, macOS     |
| 키 교환   | Noise Protocol Framework (IK pattern)   |

### 암호 프리미티브

WireGuard는 알고리즘 협상 없이 고정된 최신 암호화 스위트를 사용합니다.

| 역할         | 알고리즘        | 표준     |
|--------------|-----------------|----------|
| 대칭 암호화  | ChaCha20        | RFC 8439 |
| 인증 태그    | Poly1305 (AEAD) | RFC 8439 |
| ECDH 키 교환 | Curve25519      | RFC 7748 |

> Curve25519: Daniel J. Bernstein이 설계한 타원 곡선 Diffie-Hellman 키 교환 알고리즘(RFC 7748)입니다. 128비트 보안 수준을 제공하며, 타이밍 공격에 강하고 구현이 단순합니다. WireGuard의 키 교환과 정적 키 인증에 모두 사용됩니다.
| 해싱/MAC      | BLAKE2s         | RFC 7693 |
| 해시테이블 키 | SipHash24       | —        |
| 키 파생       | HKDF            | RFC 5869 |

> HKDF(HMAC-based Key Derivation Function, RFC 5869): 마스터 시크릿에서 여러 개의 암호화 키를 안전하게 파생하는 함수입니다. Extract 단계에서 엔트로피를 정규화하고 Expand 단계에서 필요한 길이의 키를 생성합니다.

협상 없이 고정 스위트를 사용하는 이유: 취약한 알고리즘 선택 공격(downgrade attack)을 원천 차단합니다.

### Noise IK 핸드셰이크 (1-RTT)

> Noise Protocol Framework: Jason Donenfeld가 WireGuard 설계에 채택한 암호화 핸드셰이크 프레임워크입니다. IK 패턴은 Initiator의 임시 키(I)와 Responder의 정적 키(K)를 사용하는 1-RTT 방식으로, TLS 1.3 핸드셰이크보다 단순하고 검증이 용이합니다.

WireGuard는 Noise Protocol Framework의 IK 패턴을 사용합니다. "I"는 Initiator의 정적 키가 첫 메시지에 포함(Identity), "K"는 Responder의 키가 미리 알려져 있다(Known)는 의미입니다.

```
Initiator                                      Responder
    │                                              │
    │── Handshake Initiation ─────────────────>    │
    │   ephemeral public key (Ei)                  │
    │   encrypted static public key (Si, AEAD)     │
    │   encrypted timestamp (AEAD)                 │
    │   (Curve25519 DH: Ei*Sr, Si*Sr)              │
    │                                              │
    │ <── Handshake Response ──────────────────    │
    │     ephemeral public key (Er)                │
    │     empty AEAD (confirm)                     │
    │     (DH: Er*Ei, Er*Si → session keys 파생)   │
    │                                              │
    │  (핸드셰이크 완료 — 1 RTT)                   │
    │                                              │
    │── Data Packet ─────────────────────────>     │
    │   Counter + ChaCha20-Poly1305(Payload)       │
```

세션 키는 핸드셰이크마다 새로 파생되어 **Perfect Forward Secrecy**를 보장합니다. 핸드셰이크는 기본 **3분마다 자동 갱신**됩니다.

### Cryptokey Routing

WireGuard는 IP 라우팅 테이블 대신 **공개키 ↔ AllowedIPs 매핑**으로 패킷을 라우팅합니다.

```
송신 시 (Outbound):
패킷의 목적지 IP ── AllowedIPs 매핑 조회 ──> Peer의 공개키 결정
                                              ──> 해당 Peer의 세션 키로 암호화

수신 시 (Inbound):
복호화 후 패킷 소스 IP ── 해당 Peer의 AllowedIPs에 포함? ──> 허용/폐기
```

설정 예시:

```ini
[Interface]
PrivateKey = <client-private-key>
Address    = 10.0.0.2/24

[Peer]
PublicKey  = <server-public-key>
Endpoint   = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0   # 모든 트래픽을 VPN으로
```

AllowedIPs = `0.0.0.0/0`이면 모든 트래픽이 VPN을 통과하고, 특정 CIDR만 지정하면 Split Tunnel로 동작합니다.

### Silent Peer / Roaming

WireGuard는 명시적 세션 개념이 없습니다. 패킷을 수신하면 소스 IP와 포트를 자동으로 Endpoint로 갱신합니다. 이를 통해 클라이언트 IP가 변경되어도 자동으로 Roaming이 지원됩니다.

```
Client (IP: 1.2.3.4) ── Data Packet ──> Server
Server: "Peer X의 Endpoint = 1.2.3.4:12345 로 기록"

Client (IP: 5.6.7.8 로 변경) ── Data Packet ──> Server
Server: "Peer X의 Endpoint = 5.6.7.8:54321 로 자동 갱신"
```

### DoS 방어 — Cookie 메커니즘

핸드셰이크 요청이 과도할 때 Responder는 CPU 집약적인 DH 연산 전에 Cookie(MAC 기반 챌린지)를 요청합니다.

```
과부하 상태:
Initiator ── Handshake Initiation ──> Responder
Initiator <── Cookie Reply (MAC2 챌린지) ─── Responder
Initiator ── Handshake Initiation (with MAC2) ──> Responder
(MAC2 검증 후에만 DH 연산 수행)
```

### 장단점

| 장점                       | 단점                                   |
|----------------------------|----------------------------------------|
| 4,000줄 — 코드 감사 용이   | 고정 암호 스위트 (알고리즘 선택 불가)  |
| 커널 공간 처리 — 높은 성능 | UDP only — 일부 방화벽/DPI 차단 가능   |
| 1-RTT 핸드셰이크           | 동적 IP 할당 미내장 (wg-quick 등 별도) |
| Roaming 지원               | TCP 443 위장 불가                      |
| PFS 자동 보장 (3분 갱신)   | 연결 상태 없음 — 로깅/감사 어려움      |

[⬆ 목차로 돌아가기](#목차)


---

## 9. 프로토콜 비교

### 보안 / 성능 / 운용성 종합 비교

| 항목            | PPTP       | L2TP/IPsec   | IKEv2/IPsec | OpenVPN     | WireGuard |
|-----------------|------------|--------------|-------------|-------------|-----------|
| 보안            | ❌ 크랙됨  | ✅ 강력      | ✅ 강력     | ✅ 강력     | ✅ 최신   |
| 암호화 알고리즘 | RC4 (취약) | AES-CBC/GCM  | AES-GCM     | AES-256-GCM | ChaCha20  |
| PFS             | ❌         | 설정 시 가능 | ✅          | ✅          | ✅ 항상   |

> PFS(Perfect Forward Secrecy): 세션 키가 노출되더라도 과거의 다른 세션 키는 영향을 받지 않도록 매 세션마다 독립적인 키를 생성하는 특성입니다. Diffie-Hellman 임시 키 교환(Ephemeral DH)으로 구현하며, 장기 키 탈취 시 과거 통신 내용을 보호합니다.
| 속도            | 빠름       | 보통          | 빠름        | 보통          | 최상        |
| 오버헤드        | ~8 bytes   | ~76 bytes     | ~58 bytes   | ~30 bytes     | ~32 bytes   |
| NAT 통과        | 어려움     | NAT-T 필수    | 내장        | TCP 443 가능  | UDP 단일    |
| 모바일 로밍     | ❌         | 보통          | ✅ MOBIKE   | 보통          | ✅ 자동     |
| 방화벽 우회     | 어려움     | 어려움        | 보통        | ✅ TCP 443    | ❌ UDP only |
| 코드 규모       | 소         | 대            | 중          | 대 (~100K줄)  | 소 (~4K줄)  |
| OS 기본 지원    | Windows    | 대부분        | 대부분      | ❌ 클라이언트 | Linux 5.6+  |
| 표준 / RFC      | RFC 2637   | RFC 2661+4301 | RFC 7296    | 비표준        | 비표준      |
| 상태            | 폐기       | 레거시        | 현역        | 현역          | 현역        |

### 포트 / 프로토콜 요약

| VPN 프로토콜 | 필요 포트 / 프로토콜            | 방화벽 규칙                        |
|--------------|---------------------------------|------------------------------------|
| PPTP         | TCP 1723 + GRE (IP Protocol 47) | GRE 허용 필요 — NAT 통과 어려움    |
| L2TP/IPsec   | UDP 500, 4500, 1701             | 3개 포트 허용                      |
| IKEv2        | UDP 500, 4500                   | 2개 포트 허용                      |
| OpenVPN      | UDP 1194 또는 TCP 443           | 단일 포트 (TCP 443은 HTTPS와 동일) |
| WireGuard    | UDP 51820 (변경 가능)           | 단일 UDP 포트 허용                 |

### 핸드셰이크 메시지 수 비교

| 프로토콜        | 메시지 수 | RTT 수 | 비고                            |
|-----------------|-----------|--------|---------------------------------|
| PPTP            | 10+       | 5+     | TCP + PPP 협상 포함             |
| IKEv1 Main Mode | 9         | 4.5    | Phase 1(6) + Phase 2(3)         |
| L2TP/IPsec      | 15+       | 7+     | IKE + L2TP + PPP 전체           |
| IKEv2           | 4         | 2      | IKE_SA_INIT(2) + IKE_AUTH(2)    |
| OpenVPN         | TLS 1.3   | 1      | TLS 1.3 0-RTT 가능              |
| WireGuard       | 2         | 1      | Noise IK: Initiation + Response |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 선택 가이드

### 용도별 권장 프로토콜

| 용도                      | 권장 프로토콜        | 이유                                     |
|---------------------------|----------------------|------------------------------------------|
| Site-to-Site (IDC/Cloud)  | IKEv2/IPsec          | AWS/GCP/Azure VPN 기본, 장비 호환성 최상 |
| 모바일 Remote Access      | IKEv2 또는 WireGuard | MOBIKE/Roaming으로 끊김 없는 전환        |
| 검열 우회 / DPI 회피      | OpenVPN (TCP 443)    | HTTPS 트래픽과 구분 불가                 |
| 고성능 (게임, 스트리밍)   | WireGuard            | 최소 오버헤드, 커널 공간 처리            |
| 클라이언트 설치 불가 환경 | IKEv2/IPsec          | OS 기본 내장, 추가 설치 없음             |
| 레거시 장비 호환          | L2TP/IPsec           | 구형 라우터/방화벽 지원                  |
| ❌ 사용 금지              | PPTP                 | 2012년 크랙됨 — 사용 금지                |

### 환경별 판단 기준

```
신규 구축인가?
      │
      ├── Yes
      │       │
      │       ├── 모바일/로밍 중요? ────────> IKEv2 또는 WireGuard
      │       │
      │       ├── 방화벽 우회 필요? ─────────> OpenVPN (TCP 443)
      │       │
      │       ├── Site-to-Site? ──────────────> IKEv2/IPsec
      │       │
      │       └── 고성능 P2P? ────────────────> WireGuard
      │
      └── No (레거시 유지)
              │
              ├── PPTP? ─────────────────────> 즉시 마이그레이션 계획 수립
              │
              └── L2TP/IPsec? ───────────────> IKEv2로 마이그레이션 검토
```

### AWS VPN 연동

| AWS 서비스       | 지원 프로토콜         | 비고                               |
|------------------|-----------------------|------------------------------------|
| Site-to-Site VPN | IKEv1/IKEv2 + IPsec   | BGP 또는 Static 라우팅             |
| Client VPN       | OpenVPN (mutual auth) | ACM 인증서 기반                    |
| EC2 자체 구축    | WireGuard, OpenVPN 등 | AMI에 직접 설치, SG 포트 허용 필요 |
| Transit Gateway  | IPsec (IKEv2 권장)    | 다중 VPC/계정 연결                 |

### 보안 수준 요약

```
보안 강도 (높음 → 낮음):

WireGuard         ── 최신 암호, 코드 최소, PFS 항상 보장
IKEv2/IPsec (AES-GCM) ── RFC 표준, AEAD, 넓은 호환성
OpenVPN (TLS 1.3) ── 성숙한 구현, 20년+ 감사 이력
L2TP/IPsec        ── IPsec 수준이나 이중 캡슐화 오버헤드
─────────────────────────────────────────────────────
PPTP              ── ❌ 사용 금지 (2012년 완전 해독)
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

**마지막 업데이트**: 2026-08-05

© 2026 siasia86. Licensed under CC BY 4.0.
