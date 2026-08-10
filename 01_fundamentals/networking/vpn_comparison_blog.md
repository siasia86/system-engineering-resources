# VPN 프로토콜 선택 가이드
<!-- reference: _reference/vpn_protocol_official_notes.md -->
<!-- reference: _reference/softether_official_notes.md -->

어떤 VPN을 선택해야 할지 판단하기 위한 실용적 비교 가이드입니다.
이 문서는 프로토콜 내부 동작보다 **"언제 무엇을 써야 하는가"** 에 집중합니다.
비교 대상 중 OpenVPN·SoftEther는 표준 RFC가 없는 소프트웨어 구현체이며, 나머지는 공개 사양 또는 RFC가 존재합니다.
각 프로토콜의 개념 상세는 [VPN 프로토콜 개념](./vpn_protocol_concepts.md)을 참고하세요.

## 목차

| 섹션                                                                                                                                          |
|-----------------------------------------------------------------------------------------------------------------------------------------------|
| [1. VPN 솔루션 한 줄 요약](#1-vpn-솔루션-한-줄-요약) / [2. 보안 수준 비교](#2-보안-수준-비교) / [3. 성능·오버헤드 비교](#3-성능오버헤드-비교) |
| [4. 방화벽·NAT 통과 비교](#4-방화벽nat-통과-비교) / [5. 설정 난이도 비교](#5-설정-난이도-비교) / [6. 시나리오별 선택](#6-시나리오별-선택)     |
| [7. SoftEther 위치](#7-softether-위치) / [8. 선택 플로우차트](#8-선택-플로우차트)                                                             |

---

## 1. VPN 솔루션 한 줄 요약

| VPN 솔루션    | 출시 | 한 줄 요약                                                 | 상태      |
|---------------|------|------------------------------------------------------------|-----------|
| PPTP          | 1999 | RC4 암호화, MS-CHAPv2 크랙됨 — 사용 금지                   | ❌ 폐기   |
| L2TP/IPsec    | 1999 | OS 기본 내장, 안전하지만 설정 복잡하고 NAT 통과 불안정     | 🟡 레거시 |
| IKEv2/IPsec   | 2005 | RFC 표준, 모바일 로밍(MOBIKE) 지원, 넓은 호환성            | ✅ 현역   |
| OpenVPN       | 2001 | TCP 443으로 방화벽 우회 가능, 성숙한 구현, 별도 클라이언트 | ✅ 현역   |
| WireGuard     | 2016 | 커널 내장, 최소 코드, 고성능, 최신 암호 스위트             | ✅ 현역   |
| SoftEther VPN | 2013 | 멀티 프로토콜 서버, Ethernet over HTTPS, 방화벽 우회 강점  | ✅ 현역   |

🟡 OpenVPN·SoftEther VPN은 IETF 표준 프로토콜이 아닌 소프트웨어 구현체입니다. PPTP·L2TP·IPsec·IKEv2·WireGuard는 공개 사양 또는 RFC가 존재합니다.

---

## 2. 보안 수준 비교

출처: `_reference/vpn_protocol_official_notes.md`, `_reference/softether_official_notes.md`

| 항목           | PPTP       | L2TP/IPsec     | IKEv2/IPsec  | OpenVPN     | WireGuard         | SoftEther SSL-VPN |
|----------------|------------|----------------|--------------|-------------|-------------------|-------------------|
| 암호화         | RC4 (취약) | AES-CBC/GCM    | AES-GCM      | AES-256-GCM | ChaCha20-Poly1305 | AES (TLS 1.3)     |
| 키 교환        | 없음       | DH Group 1/2/5 | DH Group 14+ | DH (TLS)    | Curve25519        | TLS 핸드셰이크    |
| PFS            | ❌         | 설정 시 가능   | ✅           | ✅          | ✅ 항상           | ✅ TLS 기반       |
| 인증서 인증    | ❌         | 가능           | ✅           | ✅          | 공개키            | ✅ X.509          |
| 알려진 취약점  | 크랙됨     | DH Group 취약  | 없음         | 없음        | 없음              | L2TP 모드 시 동일 |
| 보안 감사 이력 | -          | -              | RFC 표준     | 20년+ 이력  | 2016 논문 공개    | 제한적            |

🟡 SoftEther의 L2TP/IPsec 모드는 DH Group 1/2/5 (MODP 768~1536, 2048bit 미만)를 사용합니다. SoftEther를 L2TP 모드로 운영할 경우 동일한 취약점이 있습니다. SSL-VPN 모드(TLS 1.3)를 사용하면 이 문제가 없습니다.

---

## 3. 성능·오버헤드 비교

| 항목           | L2TP/IPsec     | IKEv2/IPsec | OpenVPN       | WireGuard | SoftEther SSL-VPN |
|----------------|----------------|-------------|---------------|-----------|-------------------|
| 헤더 오버헤드  | 가변           | 가변        | 가변          | 가변      | 가변 (TLS)        |
| 핸드셰이크 RTT | 구현·인증 의존 | 기본 2 RTT  | TLS 협상 의존 | 1 RTT     | TLS 협상 의존     |
| 커널 공간 처리 | ✅             | ✅          | ❌ 유저       | ✅ 5.6+   | ❌ 유저           |
| CPU 부하       | 보통           | 낮음        | 높음          | 최저      | 보통              |
| 병렬 TCP 연결  | 해당 없음      | 해당 없음   | 단일          | 해당 없음 | 1~32개            |
| 데이터 압축    | 없음           | 없음        | 가능          | 없음      | zlib              |

> SoftEther의 병렬 TCP 1~32개 구성은 공식 스펙 페이지(softether.org/3-spec) 명시 사항입니다.

---

## 4. 방화벽·NAT 통과 비교

방화벽 정책이 엄격한 환경에서의 통과 가능성 비교입니다.

| 환경                 | PPTP | L2TP/IPsec | IKEv2 | OpenVPN    | WireGuard | SoftEther  |
|----------------------|------|------------|-------|------------|-----------|------------|
| 일반 NAT 뒤          | 🟡   | ✅ NAT-T   | ✅    | ✅         | ✅        | ✅ NAT-T   |
| UDP 차단 (TCP only)  | 🟡   | ❌         | ❌    | ✅ TCP 443 | ❌        | ✅ TCP 443 |
| HTTPS(443)만 허용    | ❌   | ❌         | ❌    | ✅         | ❌        | ✅         |
| DPI(패킷 검사) 환경  | ❌   | ❌         | ❌    | 🟡         | 🟡        | ✅         |
| ICMP/DNS만 통과 가능 | ❌   | ❌         | ❌    | ❌         | ❌        | ✅         |

- SoftEther는 VPN over ICMP, VPN over DNS를 지원하여 가장 극단적인 방화벽 환경에서도 통과가 가능합니다.
- OpenVPN(TCP 443)은 HTTPS 트래픽과 구분이 어렵지만, TLS 핑거프린트로 DPI 탐지 가능성이 있습니다.
- WireGuard는 UDP 전용이라 UDP 차단 환경에서는 사용 불가합니다.

---

## 5. 설정 난이도 비교

| 항목               | L2TP/IPsec | IKEv2/IPsec | OpenVPN | WireGuard   | SoftEther        |
|--------------------|------------|-------------|---------|-------------|------------------|
| 서버 설정 난이도   | 높음       | 보통        | 보통    | 낮음        | 보통             |
| 클라이언트 설치    | 불필요     | 불필요      | 필요    | 필요        | 필요 (or 불필요) |
| 인증서 관리        | 선택       | 필수        | 필수    | 공개키 쌍   | 선택             |
| 멀티 프로토콜 지원 | ❌         | ❌          | ❌      | ❌          | ✅               |
| GUI 관리 도구      | ❌         | ❌          | ❌      | 일부        | ✅ Windows GUI   |
| Linux CLI 관리     | strongSwan | strongSwan  | openvpn | wg/wg-quick | vpncmd           |

SoftEther의 클라이언트 설치 여부는 프로토콜에 따라 다릅니다.

| SoftEther 모드 | 클라이언트 설치 여부       | 대상 OS                       |
|----------------|----------------------------|-------------------------------|
| SSL-VPN        | vpnclient 필요             | Windows, Linux                |
| L2TP/IPsec     | 불필요 (OS 기본 내장)      | Windows, macOS, iOS, Android  |
| OpenVPN        | OpenVPN 클라이언트 필요    | Windows, Linux, macOS, 모바일 |
| SSTP           | 불필요 (Windows 기본 내장) | Windows Vista 이상            |

---

## 6. 시나리오별 선택

### 재택근무 (Remote Access)

| 상황                      | 권장                             | 이유                                 |
|---------------------------|----------------------------------|--------------------------------------|
| 사내 서버 접근, 일반 환경 | IKEv2/IPsec                      | OS 기본 내장, 설정 간단              |
| 모바일 Wi-Fi 전환이 잦음  | IKEv2 (MOBIKE) 또는 WireGuard    | IP 변경 시 세션 유지                 |
| 방화벽 우회 필요          | OpenVPN (TCP 443) 또는 SoftEther | HTTPS 포트 사용                      |
| 다수 직원, 중앙 관리 필요 | SoftEther 또는 OpenVPN           | RADIUS 연동, 사용자별 정책 설정 가능 |

### 서버 간 터널 (Site-to-Site)

| 상황                          | 권장                                | 이유                              |
|-------------------------------|-------------------------------------|-----------------------------------|
| IDC ↔ Cloud (AWS, GCP, Azure) | IKEv2/IPsec                         | 클라우드 VPN 게이트웨이 기본 지원 |
| 소규모 서버 간 직접 연결      | WireGuard                           | 설정 단순, 고성능                 |
| Cisco/Juniper 장비 포함       | IKEv2/IPsec                         | 장비 호환성 최상                  |
| L2 브리징 필요 (VLAN 확장)    | SoftEther (L2TP/IPsec 또는 EtherIP) | L2 전달 지원                      |

### 방화벽 우회 / 검열 환경

| 상황                          | 권장                             | 이유                     |
|-------------------------------|----------------------------------|--------------------------|
| HTTPS(443)만 허용             | OpenVPN (TCP 443) 또는 SoftEther | 443 포트 통과 가능       |
| DPI로 VPN 트래픽 탐지·차단    | SoftEther (HTTPS 모방)           | TLS 트래픽과 구분 어려움 |
| 극단적 제한 (ICMP/DNS만 통과) | SoftEther (VPN over ICMP/DNS)    | 최후 수단                |

### 고성능 / 저지연

| 상황                | 권장                       | 이유                                |
|---------------------|----------------------------|-------------------------------------|
| 게임, 스트리밍, P2P | WireGuard                  | 커널 처리, 최소 오버헤드, 최저 지연 |
| 대용량 파일 전송    | WireGuard 또는 IKEv2/IPsec | 커널 공간 처리                      |
| 레거시 호환 필요    | L2TP/IPsec                 | 구형 장비·OS 지원                   |

---

## 7. SoftEther 위치

SoftEther는 단일 서버에서 여러 VPN 프로토콜을 동시에 수신하는 **멀티 프로토콜 VPN 서버**입니다.
독자적인 SSL-VPN 프로토콜 외에 L2TP/IPsec, OpenVPN, SSTP 서버도 내장하고 있어 클라이언트 다양성이 높습니다.

### 강점

- **방화벽 우회**: TCP 443, VPN over ICMP/DNS 지원으로 가장 제한적인 환경에서도 동작합니다.
- **멀티 프로토콜**: 하나의 서버로 OS 기본 클라이언트(L2TP), OpenVPN 클라이언트, 전용 클라이언트를 모두 수용합니다.
- **L2 지원**: Ethernet 프레임을 그대로 터널링하여 L2 브리징, VLAN 확장이 가능합니다.
- **관리 도구**: Windows GUI(`VPN Server Manager`)와 CLI(`vpncmd`) 모두 제공합니다.

### 약점

- **성능**: TLS 기반 유저 공간 처리라 WireGuard 대비 CPU 부하가 높습니다.
- **L2TP 모드 보안**: 내장 L2TP/IPsec은 DH Group 1/2/5 (2048bit 미만)로, 보안 민감 환경에는 부적합합니다.
- **OpenVPN 호환**: OpenVPN 클론 방식이며, BF-CBC 등 취약 cipher 포함 협상 가능성이 있습니다. cipher를 명시적으로 지정해야 합니다.
- **감사 이력**: WireGuard, OpenVPN 대비 독립적인 보안 감사 이력이 적습니다.

### SoftEther vs 다른 솔루션

| 비교 항목     | SoftEther SSL-VPN | OpenVPN       | WireGuard    |
|---------------|-------------------|---------------|--------------|
| 방화벽 우회   | ✅ 우수           | ✅ TCP 443    | ❌ UDP 전용  |
| 성능          | 보통              | 보통          | ✅ 최상      |
| 코드 검증     | 제한적            | ✅ 20년+ 이력 | ✅ 논문 검증 |
| L2 지원       | ✅                | ✅ (tap 모드) | ❌ L3 전용   |
| 멀티 프로토콜 | ✅                | ❌            | ❌           |
| 클라이언트 OS | Windows/Linux     | 전 플랫폼     | 전 플랫폼    |
| 운용 복잡도   | 보통              | 보통          | 낮음         |

---

## 8. 선택 플로우차트

```
보안 요구사항이 높은가?
        |
        +-- No --> PPTP? --> 즉시 사용 중단, IKEv2로 마이그레이션
        |
        +-- Yes
                |
                +-- 방화벽 우회가 필요한가?
                |           |
                |           +-- Yes --> HTTPS(443)만 허용?
                |           |                   |
                |           |                   +-- Yes --> SoftEther 또는 OpenVPN (TCP 443)
                |           |                   |
                |           |                   +-- No  --> OpenVPN (UDP 1194)
                |           |
                |           +-- No
                |                   |
                |                   +-- 고성능 필요?
                |                   |           |
                |                   |           +-- Yes --> WireGuard
                |                   |           |
                |                   |           +-- No
                |                   |                   |
                |                   |                   +-- 모바일 로밍 중요? --> IKEv2
                |                   |                   |
                |                   |                   +-- L2 브리징 필요? ----> SoftEther
                |                   |                   |
                |                   |                   +-- 기본 설치 없이?  ----> IKEv2/L2TP
                |                   |
                |                   +-- Site-to-Site --> IKEv2/IPsec (AWS/GCP/Azure 기본)
                |
                +-- 레거시 장비 호환 필요? --> L2TP/IPsec
```

---

## 참고 자료

- [VPN 프로토콜 개념](./vpn_protocol_concepts.md)
- [SoftEther VPN Client 가이드](./softether_vpn_client_guide.md)
- [SoftEther VPN Server 가이드](./softether_vpn_server_guide.md)
- [SoftEther 공식 참조 노트](../../_reference/softether_official_notes.md)
- [VPN 프로토콜 공식 참조 노트](../../_reference/vpn_protocol_official_notes.md)
- WireGuard: [wireguard.com/papers/wireguard.pdf](https://www.wireguard.com/papers/wireguard.pdf) — ★★★★☆
- OpenVPN Reference Manual: [openvpn.net/community-resources](https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/) — ★★★☆☆
- SoftEther 공식 스펙: [softether.org/3-spec](https://www.softether.org/3-spec) — ★★★☆☆

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-05

**마지막 업데이트**: 2026-08-10

© 2026 siasia86. Licensed under CC BY 4.0.
