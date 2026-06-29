# VPN Protocol

VPN(Virtual Private Network) 터널링 프로토콜의 개념, 동작 원리, 보안 수준을 비교합니다. PPTP부터 WireGuard까지 세대별 발전 흐름을 다룹니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. PPTP](#2-pptp) / [3. L2TP](#3-l2tp) / [4. IPsec](#4-ipsec)                      |
| [5. L2TP/IPsec](#5-l2tpipsec) / [6. IKEv2](#6-ikev2) / [7. OpenVPN](#7-openvpn)                          |
| [8. WireGuard](#8-wireguard) / [9. 프로토콜 비교](#9-프로토콜-비교) / [10. 선택 가이드](#10-선택-가이드) |

## 1. 개요

### VPN 터널링 원리

```
┌───────────────────────────────────────────────────────────────┐
│                       Public Network                          │
│                                                               │
│  Host A                                           Host B      │
│  ┌──────┐   Encrypted Tunnel (VPN)    ┌──────┐                │
│  │      │ ═════════════════════════>  │      │                │
│  │      │ <═════════════════════════  │      │                │
│  └──────┘                             └──────┘                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 세대별 발전

```
1996        1999         2001        2005        2020
 │           │            │           │           │
 v           v            v           v           v
PPTP ──> L2TP/IPsec ──> OpenVPN ──> IKEv2 ──> WireGuard
(dead)   (legacy)       (mature)   (mobile)   (modern)
```

### OSI 계층별 동작 위치

| 프로토콜    | 동작 계층   | 캡슐화 대상    |
|-------------|-------------|----------------|
| PPTP        | Layer 2     | PPP 프레임     |
| L2TP        | Layer 2     | PPP 프레임     |
| IPsec       | Layer 3     | IP 패킷        |
| L2TP/IPsec  | Layer 2 + 3 | PPP over IPsec |
| IKEv2/IPsec | Layer 3     | IP 패킷        |
| OpenVPN     | Layer 2/3   | TLS 위 터널    |
| WireGuard   | Layer 3     | IP 패킷 (UDP)  |

## 2. PPTP

Point-to-Point Tunneling Protocol. Microsoft가 1996년에 개발한 최초의 VPN 프로토콜입니다.

| 항목      | 값                                   |
|-----------|--------------------------------------|
| 개발사    | Microsoft                            |
| RFC       | RFC 2637 (Informational, 비표준)     |
| 포트      | TCP 1723 + GRE (Protocol 47)         |
| 암호화    | MPPE (RC4, 40~128bit)                |
| 인증      | MS-CHAPv2                            |
| 보안 상태 | ❌ 완전히 크랙됨 (2012년 Moxie 공개) |
| 현재 용도 | 레거시 호환 외 사용 금지             |

### 동작 구조

```
┌─────────────────────────────────────────────────────┐
│ IP Header │ GRE Header │ PPP Header │ PPP Payload   │
└─────────────────────────┬───────────────────────────┘
                          │
                          v
        TCP 1723: Control Channel (tunnel setup)
        GRE:      Data Channel (encrypted PPP)
```

### 보안 취약점

| 취약점          | 영향                                 |
|-----------------|--------------------------------------|
| MS-CHAPv2 크랙  | 2012년 CloudCracker로 100% 해독 가능 |
| RC4 스트림 암호 | 키 재사용 취약, bit-flipping 공격    |
| GRE 비인증      | 패킷 주입 가능                       |

🟡 PPTP는 어떤 환경에서도 신규 도입하면 안 됩니다. 기존 레거시 시스템에서만 잔존합니다.

## 3. L2TP

Layer 2 Tunneling Protocol. Cisco L2F + Microsoft PPTP를 결합한 IETF 표준입니다.

| 항목        | 값                                               |
|-------------|--------------------------------------------------|
| 표준        | RFC 2661 (L2TPv2, 1999), RFC 3931 (L2TPv3, 2005) |
| 포트        | UDP 1701                                         |
| 자체 암호화 | ❌ 없음                                          |
| 인증        | Control 메시지에 선택적 pre-shared secret        |
| 구성 요소   | LAC (Access Concentrator) + LNS (Network Server) |

### 동작 구조

```
┌─────────────────────────────────────────────────────────────────┐
│ IP Header │ UDP 1701 │ L2TP Header │ PPP Header │ PPP Payload   │
└─────────────────────────────────────────────────────────────────┘
```

### 핵심 개념

| 용어    | 의미                                     |
|---------|------------------------------------------|
| LAC     | L2TP Access Concentrator (클라이언트 측) |
| LNS     | L2TP Network Server (서버 측)            |
| Tunnel  | LAC-LNS 간 제어 연결                     |
| Session | 터널 내 개별 PPP 세션                    |

🟡 L2TP 단독으로는 암호화가 없어 평문 전송됩니다. 반드시 IPsec과 조합해야 합니다.

## 4. IPsec

Internet Protocol Security. IETF 표준 IP 계층 보안 프로토콜 스위트입니다.

| 항목          | 값                                                    |
|---------------|-------------------------------------------------------|
| 표준          | RFC 4301 (아키텍처), RFC 4303 (ESP), RFC 7296 (IKEv2) |
| 동작 계층     | Network Layer (Layer 3)                               |
| 프로토콜 번호 | ESP=50, AH=51                                         |
| 키 교환       | IKE (UDP 500), NAT-T (UDP 4500)                       |
| 모드          | Transport Mode / Tunnel Mode                          |

### 핵심 프로토콜

| 프로토콜 | 역할                           | 제공하는 보안               |
|----------|--------------------------------|-----------------------------|
| ESP      | Encapsulating Security Payload | 기밀성 + 무결성 + 인증      |
| AH       | Authentication Header          | 무결성 + 인증 (암호화 없음) |
| IKE      | Internet Key Exchange          | SA 협상, 키 교환            |

### 동작 모드

```
Transport Mode:
┌──────────────────────────────────────────────────────────────┐
│ IP Header │ ESP Header │ TCP/UDP │ Payload │ ESP Trailer     │
└──────────────────────────────────────────────────────────────┘
  (Original)              (Encrypted)

Tunnel Mode:
┌──────────────────────────────────────────────────────────────────────┐
│ New IP Header │ ESP Header │ Original IP │ Payload │ ESP Trailer     │
└──────────────────────────────────────────────────────────────────────┘
  (Gateway)                  (All Encrypted)
```

- **Transport Mode**: 호스트 간 통신 보호. IP 헤더는 원본 유지합니다.
- **Tunnel Mode**: 게이트웨이 간 통신. 원본 IP 패킷 전체를 암호화합니다.

### IKE Phase 1 / Phase 2

| Phase   | 목적                                 | 결과물                      |
|---------|--------------------------------------|-----------------------------|
| Phase 1 | 보안 채널 수립 (IKEv1: ISAKMP SA)    | IKE SA (암호화된 제어 채널) |
| Phase 2 | 데이터 보호 협상 (IKEv1: Quick Mode) | IPsec SA (ESP/AH 파라미터)  |

### SA (Security Association)

| 필드      | 설명                             |
|-----------|----------------------------------|
| SPI       | Security Parameter Index (32bit) |
| Protocol  | ESP 또는 AH                      |
| Algorithm | 암호화 + 해시 알고리즘 조합      |
| Lifetime  | SA 유효 시간 또는 바이트 수      |

## 5. L2TP/IPsec

L2TP 터널을 IPsec ESP Tunnel Mode로 감싸는 조합입니다. Windows/macOS에 기본 내장되어 있습니다.

| 항목         | 값                                                 |
|--------------|----------------------------------------------------|
| 포트         | UDP 500 (IKE) + UDP 4500 (NAT-T) + UDP 1701 (L2TP) |
| 암호화       | IPsec ESP (AES-256 등)                             |
| 인증         | IKE PSK 또는 인증서                                |
| 이중 캡슐화  | ✅ (오버헤드 큼)                                   |
| NAT 통과     | NAT-T (UDP 4500) 필수                              |
| OS 기본 지원 | Windows, macOS, iOS, Android                       |

### 패킷 구조

```
┌──────────────────────────────────────────────────────────────────────┐
│ IP │ UDP 4500 │ ESP │ UDP 1701 │ L2TP │ PPP │ IP │ Payload │ ESP Pad │
└──────────────────────────────────────────────────────────────────────┘
  ^                 ^                             ^
  │                 │                             └── Original data     
  │                 └── IPsec encryption boundary                       
  └── Outer IP (NAT-T)                                                  
```

### 장단점

| 장점                          | 단점                           |
|-------------------------------|--------------------------------|
| OS 기본 지원 (추가 설치 없음) | 이중 캡슐화로 오버헤드 증가    |
| IPsec 수준의 강력한 암호화    | UDP 500/4500 차단 시 연결 불가 |
| 20년+ 검증된 안정성           | NAT 환경에서 설정 복잡         |

## 6. IKEv2

Internet Key Exchange version 2. IPsec 키 교환 프로토콜의 현대 버전입니다.

| 항목         | 값                                             |
|--------------|------------------------------------------------|
| 표준         | RFC 7296 (2014)                                |
| 포트         | UDP 500 + UDP 4500 (NAT-T)                     |
| 암호화       | IPsec ESP (AES-GCM, ChaCha20 등)               |
| 특징         | MOBIKE (RFC 4555) — 네트워크 전환 시 세션 유지 |
| OS 기본 지원 | Windows 7+, macOS, iOS, Android 11+            |
| 핵심 강점    | 모바일 로밍, 빠른 재연결 (< 1초)               |

### IKEv1 vs IKEv2

| 항목        | IKEv1           | IKEv2                 |
|-------------|-----------------|-----------------------|
| 메시지 수   | 6~9 (Main Mode) | 4 (Initial + Auth)    |
| NAT 감지    | 별도 확장       | 내장                  |
| 모바일 지원 | ❌              | ✅ MOBIKE             |
| DPD         | 별도 RFC        | 내장 (Liveness Check) |
| 복잡도      | 높음            | 낮음                  |

### MOBIKE (Mobile IKE)

Wi-Fi → LTE 전환, IP 변경 시에도 VPN 세션이 유지됩니다.

```
Phone (Wi-Fi: 192.168.1.10)
     │
     │ ── IPsec Tunnel ──────────> VPN Gateway
     │
     │  (move to LTE)
     v
Phone (LTE: 10.0.0.50)
     │
     │ ── UPDATE_SA_ADDRESSES ──> VPN Gateway
     │
     └── Same tunnel, no re-auth
```

## 7. OpenVPN

SSL/TLS 기반 오픈소스 VPN. TCP/UDP 선택 가능하며, 방화벽 우회에 강합니다.

| 항목      | 값                                 |
|-----------|------------------------------------|
| 라이선스  | GPLv2                              |
| 포트      | UDP 1194 (기본) 또는 TCP 443 위장  |
| 암호화    | OpenSSL (AES-256-GCM, TLS 1.2/1.3) |
| 인증      | 인증서, PSK, LDAP, RADIUS          |
| 모드      | TUN (Layer 3) / TAP (Layer 2)      |
| 코드 규모 | ~100,000줄 (WireGuard 대비 대규모) |

### 동작 구조

```
┌──────────────────────────────────────────────────────────┐
│ IP │ UDP 1194 │ OpenVPN Header │ TLS Record │ Payload    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             v
              TLS Handshake (Control Channel)
              HMAC + AES (Data Channel)
```

### 장단점

| 장점                           | 단점                          |
|--------------------------------|-------------------------------|
| TCP 443 사용으로 방화벽 우회   | 커널 공간이 아닌 유저스페이스 |
| 모든 OS 지원 (클라이언트 필요) | 설정 복잡 (PKI 인프라 필요)   |
| 20년+ 보안 감사 이력           | WireGuard 대비 처리량 낮음    |
| 유연한 인증 연동               | TCP 모드 시 TCP-over-TCP 문제 |

## 8. WireGuard

현대적 VPN 프로토콜. 2020년 Linux 커널 5.6에 통합되었습니다.

| 항목      | 값                                      |
|-----------|-----------------------------------------|
| 개발자    | Jason A. Donenfeld                      |
| 라이선스  | GPLv2 (Linux), MIT (Go userspace)       |
| 포트      | UDP 단일 포트 (기본 51820)              |
| 암호화    | ChaCha20, Poly1305, Curve25519, BLAKE2s |
| 코드 규모 | ~4,000줄 (커널 모듈)                    |
| 커널 통합 | Linux 5.6+, FreeBSD, Windows, macOS     |
| 키 교환   | Noise Protocol Framework (IK pattern)   |

### 동작 구조

```
┌──────────────────────────────────────────┐
│ IP │ UDP 51820 │ WireGuard │ Payload     │
└───────────────────┬──────────────────────┘
                    │
                    v
      Noise IK Handshake (1-RTT)
      ChaCha20-Poly1305 (Data)
```

### Cryptokey Routing

WireGuard는 전통적 라우팅 테이블 대신 **공개키 ↔ 허용 IP 매핑**으로 라우팅합니다.

```
[Interface]
PrivateKey = <client-private-key>
Address = 10.0.0.2/24

[Peer]
PublicKey = <server-public-key>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0        # All traffic via VPN
```

### 장단점

| 장점                         | 단점                                 |
|------------------------------|--------------------------------------|
| 4,000줄 — 감사 용이          | 고정 암호화 스위트 (협상 불가)       |
| 커널 공간 — 최상 성능        | UDP only — 일부 방화벽 차단          |
| 1-RTT 핸드셰이크 — 즉시 연결 | 동적 IP 할당 미지원 (별도 도구 필요) |
| Roaming 지원 (IP 변경 허용)  | TCP 443 위장 불가 (obfuscation 없음) |

## 9. 프로토콜 비교

| 항목         | PPTP      | L2TP/IPsec | IKEv2/IPsec | OpenVPN       | WireGuard   |
|--------------|-----------|------------|-------------|---------------|-------------|
| 보안         | ❌ 크랙됨 | ✅ 강력    | ✅ 강력     | ✅ 강력       | ✅ 최신     |
| 속도         | 빠름      | 보통       | 빠름        | 보통          | 최상        |
| NAT 통과     | 어려움    | NAT-T 필요 | 내장        | TCP 443 가능  | UDP 단일    |
| 모바일       | ❌        | 보통       | ✅ MOBIKE   | 보통          | ✅          |
| 방화벽 우회  | 어려움    | 어려움     | 보통        | ✅ TCP 443    | ❌ UDP only |
| 코드 복잡도  | 낮음      | 높음       | 중간        | 높음          | 매우 낮음   |
| OS 기본 지원 | Windows   | 대부분     | 대부분      | ❌ 클라이언트 | Linux 5.6+  |
| 상태         | 폐기      | 레거시     | 현역        | 현역          | 현역        |

### 포트/프로토콜 요약

| VPN 프로토콜 | 필요 포트                       | 방화벽 규칙   |
|--------------|---------------------------------|---------------|
| PPTP         | TCP 1723 + GRE (IP Protocol 47) | GRE 허용 필요 |
| L2TP/IPsec   | UDP 500, 4500, 1701             | 3개 포트 오픈 |
| IKEv2        | UDP 500, 4500                   | 2개 포트      |
| OpenVPN      | UDP 1194 또는 TCP 443           | 단일 포트     |
| WireGuard    | UDP 51820 (변경 가능)           | 단일 포트     |

## 10. 선택 가이드

### 용도별 권장 프로토콜

| 용도                      | 권장 프로토콜        | 이유                          |
|---------------------------|----------------------|-------------------------------|
| Site-to-Site (IDC/Cloud)  | IKEv2/IPsec          | AWS/GCP VPN 기본, 장비 호환성 |
| 모바일 Remote Access      | IKEv2 또는 WireGuard | MOBIKE/Roaming, 빠른 재연결   |
| 검열 우회                 | OpenVPN (TCP 443)    | HTTPS 위장, DPI 회피          |
| 고성능 (게임, 스트리밍)   | WireGuard            | 최소 오버헤드, 커널 처리      |
| 클라이언트 설치 불가 환경 | IKEv2/IPsec          | OS 기본 지원, 추가 설치 없음  |
| 레거시 장비 호환          | L2TP/IPsec           | 구형 라우터/방화벽 지원       |

### AWS VPN 연동 시

| AWS 서비스       | 지원 프로토콜         |
|------------------|-----------------------|
| Site-to-Site VPN | IKEv1/IKEv2 + IPsec   |
| Client VPN       | OpenVPN (mutualauth)  |
| EC2 자체 구축    | WireGuard, OpenVPN 등 |

## 참고 자료

- RFC 2637: Point-to-Point Tunneling Protocol (PPTP)
- RFC 2661: Layer Two Tunneling Protocol "L2TP"
- RFC 3931: Layer Two Tunneling Protocol - Version 3 (L2TPv3)
- RFC 4301: Security Architecture for the Internet Protocol (IPsec)
- RFC 4303: IP Encapsulating Security Payload (ESP)
- RFC 7296: Internet Key Exchange Protocol Version 2 (IKEv2)
- RFC 4555: IKEv2 Mobility and Multihoming Protocol (MOBIKE)
- WireGuard: [wireguard.com](https://www.wireguard.com/) — ★★★☆☆
- OpenVPN: [openvpn.net](https://openvpn.net/) — ★★★☆☆
- Wikipedia: [IPsec](https://en.wikipedia.org/wiki/IPsec) — ★★☆☆☆
- Wikipedia: [L2TP](https://en.wikipedia.org/wiki/Layer_2_Tunneling_Protocol) — ★★☆☆☆

---

**작성일**: 2026-06-29

**마지막 업데이트**: 2026-06-29

© 2026 siasia86. Licensed under CC BY 4.0.
