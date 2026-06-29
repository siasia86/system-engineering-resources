---
name: vpn-protocol-official-notes
description: VPN 프로토콜(PPTP, L2TP, IPsec, IKEv2, OpenVPN, WireGuard) 공식 RFC/문서 기반 참조 노트.
last_checked: 2026-06-29
sources:
  - https://datatracker.ietf.org/doc/html/rfc2637
  - https://datatracker.ietf.org/doc/html/rfc2661
  - https://datatracker.ietf.org/doc/html/rfc3931
  - https://datatracker.ietf.org/doc/html/rfc4301
  - https://datatracker.ietf.org/doc/html/rfc4303
  - https://datatracker.ietf.org/doc/html/rfc7296
  - https://datatracker.ietf.org/doc/html/rfc4555
  - https://www.wireguard.com/papers/wireguard.pdf
  - https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
---

# VPN Protocol 공식 문서 참조 노트

## 1. PPTP (확인일: 2026-06-29)

출처: RFC 2637 (Informational — 비표준)

| 항목      | 값                                    |
|-----------|---------------------------------------|
| 상태      | Informational (표준 트랙 아님)        |
| 발행일    | 1999-07                               |
| 제어 채널 | TCP 1723                              |
| 데이터    | GRE (IP Protocol 47)                  |
| 암호화    | MPPE (RC4) — RFC 자체에 암호화 미포함 |
| 보안 상태 | MS-CHAPv2 크랙됨, 사용 금지 권고      |

🟡 IETF는 PPTP를 표준으로 채택하지 않았습니다. Informational RFC입니다.

## 2. L2TP (확인일: 2026-06-29)

출처: RFC 2661 (L2TPv2), RFC 3931 (L2TPv3)

| 항목        | L2TPv2 (RFC 2661)     | L2TPv3 (RFC 3931)          |
|-------------|-----------------------|----------------------------|
| 발행일      | 1999-08               | 2005-03                    |
| 상태        | Proposed Standard     | Proposed Standard          |
| 전송        | UDP 1701              | UDP 또는 IP directly       |
| 캡슐화      | PPP only              | PPP, Ethernet, Frame Relay |
| 자체 암호화 | 없음                  | 없음                       |
| 보안        | IPsec 필수 (RFC 3193) | IPsec 권장                 |

## 3. IPsec (확인일: 2026-06-29)

출처: RFC 4301 (아키텍처), RFC 4303 (ESP), RFC 4302 (AH)

| 항목          | 값                                      |
|---------------|-----------------------------------------|
| 아키텍처      | RFC 4301 (Security Architecture for IP) |
| ESP           | RFC 4303 (Protocol 50)                  |
| AH            | RFC 4302 (Protocol 51, 암호화 없음)     |
| IKEv2         | RFC 7296                                |
| NAT Traversal | RFC 3947 (UDP 4500 캡슐화)              |
| 암호화 필수   | ESP: AES-CBC (MUST), AES-GCM-16 (MUST)  |
| 인증 필수     | HMAC-SHA-256 (MUST)                     |
| NULL 암호화   | RFC 4303에서 허용 (인증만 사용 시)      |

### 필수/권장 알고리즘 (RFC 8221, 2017)

| 용도     | MUST                | SHOULD             | MAY          |
|----------|---------------------|--------------------|--------------|
| 암호화   | AES-CBC, AES-GCM-16 | CHACHA20-POLY1305  | AES-CCM-8    |
| 무결성   | HMAC-SHA-256-128    | AES-GMAC           | HMAC-SHA-512 |
| DH Group | Group 14 (2048bit)  | Group 19 (ECP-256) | Group 20     |

## 4. IKEv2 (확인일: 2026-06-29)

출처: RFC 7296 (IKEv2), RFC 4555 (MOBIKE)

| 항목                | 값                                |
|---------------------|-----------------------------------|
| 핸드셰이크          | 4 메시지 (IKE_SA_INIT + IKE_AUTH) |
| 포트                | UDP 500 (기본), UDP 4500 (NAT-T)  |
| MOBIKE              | RFC 4555 — IP 변경 시 SA 유지     |
| EAP 인증            | 지원 (RFC 7296 Sec 2.16)          |
| 다중 SA             | 단일 IKE SA로 여러 Child SA 관리  |
| Dead Peer Detection | RFC 7296 내장 (liveness check)    |
| Redirect            | RFC 5685                          |

## 5. OpenVPN (확인일: 2026-06-29)

출처: openvpn.net Reference Manual (v2.6)

| 항목           | 값                                        |
|----------------|-------------------------------------------|
| 최신 안정 버전 | 2.6.x (Community), 3.x (Access Server)    |
| 제어 채널      | TLS 1.2/1.3 (최상위 지원 버전 자동 협상)  |
| 데이터 채널    | AES-256-GCM (기본), ChaCha20-Poly1305     |
| tls-crypt      | v2 지원 (메타데이터 포함 인증)            |
| 모드           | --dev tun (L3), --dev tap (L2)            |
| 권장 cipher    | AES-256-GCM (data-ciphers 옵션)           |
| 폐기 예정      | BF-CBC, --cipher 옵션 (data-ciphers 대체) |

## 6. WireGuard (확인일: 2026-06-29)

출처: wireguard.com/papers/wireguard.pdf, Linux 커널 소스

| 항목       | 값                                             |
|------------|------------------------------------------------|
| 최신 버전  | 1.0.20260223 (tools), Linux 5.6+ 커널 내장     |
| 핸드셰이크 | Noise IK (1-RTT)                               |
| 대칭 암호  | ChaCha20-Poly1305                              |
| 키 교환    | Curve25519 (ECDH)                              |
| 해시       | BLAKE2s                                        |
| 해시테이블 | SipHash24                                      |
| KDF        | HKDF (RFC 5869)                                |
| 커널 모듈  | ~4,000줄 C                                     |
| 암호 협상  | 없음 (고정 스위트, Crypto Versioning으로 대체) |
| PSK        | 선택적 (양자내성 추가 계층)                    |
| Timer 기반 | REKEY: 2분, KEEPALIVE: 사용자 설정             |

🟡 WireGuard는 암호 스위트를 협상하지 않습니다. 알고리즘 교체 시 프로토콜 버전 자체를 올립니다.

