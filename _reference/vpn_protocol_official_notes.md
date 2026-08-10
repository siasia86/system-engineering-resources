---
name: vpn-protocol-official-notes
description: VPN 프로토콜(PPTP, L2TP, IPsec, IKEv2, OpenVPN, WireGuard) 공식 RFC/문서 기반 참조 노트.
tags:
  - vpn
  - wireguard
  - ipsec
  - networking
last_checked: 2026-08-10
sources:
  - https://datatracker.ietf.org/doc/html/rfc2637
  - https://datatracker.ietf.org/doc/html/rfc2661
  - https://datatracker.ietf.org/doc/html/rfc3193
  - https://datatracker.ietf.org/doc/html/rfc3931
  - https://datatracker.ietf.org/doc/html/rfc4301
  - https://datatracker.ietf.org/doc/html/rfc4302
  - https://datatracker.ietf.org/doc/html/rfc4303
  - https://datatracker.ietf.org/doc/html/rfc3947
  - https://datatracker.ietf.org/doc/html/rfc8221
  - https://datatracker.ietf.org/doc/html/rfc7296
  - https://datatracker.ietf.org/doc/html/rfc4555
  - https://www.wireguard.com/papers/wireguard.pdf
  - https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
---

# VPN Protocol 공식 문서 참조 노트

## 1. PPTP (확인일: 2026-08-10)

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

## 2. L2TP (확인일: 2026-08-10)

출처: RFC 2661 (L2TPv2), RFC 3931 (L2TPv3)

| 항목        | L2TPv2 (RFC 2661)                            | L2TPv3 (RFC 3931)          |
|-------------|----------------------------------------------|----------------------------|
| 발행일      | 1999-08                                      | 2005-03                    |
| 상태        | Proposed Standard                            | Proposed Standard          |
| 전송        | UDP 1701                                     | UDP 또는 IP directly       |
| 캡슐화      | PPP only                                     | PPP, Ethernet, Frame Relay |
| 자체 암호화 | 없음                                         | 없음                       |
| 보안        | RFC 3193 보안 프로파일에서는 IPsec 보호 필수 | 별도 보안 계층 필요        |

## 3. IPsec (확인일: 2026-08-10)

출처: RFC 4301 (아키텍처), RFC 4303 (ESP), RFC 4302 (AH)

| 항목            | 값                                                                          |
|-----------------|-----------------------------------------------------------------------------|
| 아키텍처        | RFC 4301 (Security Architecture for IP)                                     |
| ESP             | RFC 4303 (Protocol 50)                                                      |
| AH              | RFC 4302 (Protocol 51, 암호화 없음)                                         |
| IKEv2           | RFC 7296                                                                    |
| NAT Traversal   | RFC 3947 (UDP 4500 캡슐화)                                                  |
| 암호화 알고리즘 | AES-CBC, AES-GCM-16 구현 필수; ChaCha20-Poly1305 권고                       |
| 인증/무결성     | 비-AEAD에서는 HMAC-SHA-256-128 구현 필수; AEAD는 자체 태그 사용             |
| NULL 암호화     | 구현 요구사항에 포함될 수 있으나 기밀성이 없어 일반 데이터 보호에 사용 금지 |

### 필수/권장 알고리즘 (RFC 8221, 2017)

| 용도   | MUST                | SHOULD                       | MAY      |
|--------|---------------------|------------------------------|----------|
| 암호화 | AES-CBC, AES-GCM-16 | CHACHA20-POLY1305, AES-CCM-8 |          |
| 무결성 | HMAC-SHA-256-128    | HMAC-SHA-512-256             | AES-GMAC |
DH 그룹 선택은 ESP 알고리즘 요구사항을 정의하는 RFC 8221이 아니라 IKEv2 알고리즘 지침을 따릅니다.

## 4. IKEv2 (확인일: 2026-08-10)

출처: RFC 7296 (IKEv2), RFC 4555 (MOBIKE)

| 항목                | 값                                      |
|---------------------|-----------------------------------------|
| 핸드셰이크          | 4 메시지 (IKE_SA_INIT + IKE_AUTH)       |
| 포트                | UDP 500 (기본), UDP 4500 (NAT-T)        |
| MOBIKE              | RFC 4555 — 지원 환경에서 주소 변경 대응 |
| EAP 인증            | 지원 (RFC 7296 Sec 2.16)                |
| 다중 SA             | 단일 IKE SA로 여러 Child SA 관리        |
| Dead Peer Detection | RFC 7296 내장 (liveness check)          |
| Redirect            | RFC 5685                                |

## 5. OpenVPN (확인일: 2026-08-10)

출처: openvpn.net Reference Manual (v2.6)

| 항목           | 값                                                                          |
|----------------|-----------------------------------------------------------------------------|
| 문서 기준 버전 | Community 2.6 Reference Manual 기준; 실제 배포 버전은 공식 릴리스 확인 필요 |
| 제어 채널      | TLS 1.2/1.3 범위에서 구성·TLS 라이브러리 지원에 따라 협상                   |
| 데이터 채널    | `data-ciphers` 설정·협상에 따른 cipher (AEAD 권장)                          |
| tls-crypt      | v2 지원 (메타데이터 포함 인증)                                              |
| 모드           | --dev tun (L3), --dev tap (L2)                                              |
| 권장 cipher    | AES-256-GCM (data-ciphers 옵션)                                             |
| 폐기 예정      | BF-CBC, --cipher 옵션 (data-ciphers 대체)                                   |

## 6. WireGuard (확인일: 2026-08-10)

출처: wireguard.com/papers/wireguard.pdf, Linux 커널 소스

| 항목       | 값                                                   |
|------------|------------------------------------------------------|
| 버전       | 구현·배포판별 릴리스 확인 필요; Linux 5.6+ 커널 지원 |
| 핸드셰이크 | Noise IK (1-RTT)                                     |
| 대칭 암호  | ChaCha20-Poly1305                                    |
| 키 교환    | Curve25519 (ECDH)                                    |
| 해시       | BLAKE2s                                              |
| 해시테이블 | SipHash24                                            |
| KDF        | HKDF (RFC 5869)                                      |
| 구현 규모  | 단순하고 감사 가능한 설계를 지향함                   |
| 암호 협상  | 없음 (고정 스위트, Crypto Versioning으로 대체)       |
| PSK        | 선택적 사전 공유 키 추가 계층                        |
| Timer 기반 | REKEY_AFTER_TIME: 2분, KEEPALIVE: 사용자 설정        |

🟡 WireGuard는 암호 스위트를 협상하지 않습니다. 알고리즘 교체 시 프로토콜 버전 자체를 올립니다.

