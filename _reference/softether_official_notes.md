---
name: softether-official-notes
description: SoftEther VPN 공식 스펙 페이지 및 소스코드 기반 참조 노트. softether_vpn_server_guide.md, softether_vpn_client_guide.md, vpn_comparison_blog.md 작성/검토 시 참조.
tags:
  - vpn
  - softether
  - networking
last_checked: 2026-08-05
sources:
  - https://www.softether.org/3-spec
  - https://github.com/SoftEtherVPN/SoftEtherVPN/blob/master/src/GlobalConst.h
  - https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/blob/master/src/Cedar/Server.h
  - https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/blob/master/src/Cedar/Cedar.h
  - https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/blob/master/src/Cedar/Client.h
---

# SoftEther VPN 공식 참조 노트

## 1. 릴리즈 버전 현황 (확인일: 2026-08-05)

출처: GitHub API (github.com/SoftEtherVPN)

| 계열           | 최신 버전      | 릴리즈일   | repo                |
|----------------|----------------|------------|---------------------|
| v4 안정 (RTM)  | v4.44-9807-rtm | 2025-05-07 | SoftEtherVPN (메인) |
| v4 Stable repo | v4.41-9787-rtm | 2025-05-07 | SoftEtherVPN_Stable |
| v5 개발        | 5.2.5188       | 2025-07-18 | SoftEtherVPN (메인) |

🟡 SoftEtherVPN_Stable repo의 `releases/latest` API는 `v4.41`을 반환합니다. 실제 최신 RTM(`v4.44`)은 메인 repo(SoftEtherVPN)의 releases에 등록되어 있습니다. 두 repo는 코드베이스를 공유하며, Stable repo는 메인 repo의 안정 스냅샷입니다.

---

## 2. 기본 포트 (확인일: 2026-08-05)

출처: `src/GlobalConst.h`, `src/Cedar/Server.h` (소스코드 직접 확인)

| 상수명               | 값   | 용도                              |
|----------------------|------|-----------------------------------|
| `GC_DEFAULT_PORT`    | 5555 | vpncmd 관리 포트 (기본값 정의)    |
| `SERVER_DEF_PORTS_1` | 443  | 기본 리스너 1 (HTTPS 포트 재활용) |
| `SERVER_DEF_PORTS_2` | 992  | 기본 리스너 2 (IANA pop3s 재활용) |
| `SERVER_DEF_PORTS_3` | 1194 | 기본 리스너 3 (OpenVPN 관용 포트) |
| `SERVER_DEF_PORTS_4` | 5555 | 기본 리스너 4 (`GC_DEFAULT_PORT`) |

---

## 3. 서버 한계값 (확인일: 2026-08-05)

출처: `src/Cedar/Server.h`, `src/Cedar/Cedar.h` (소스코드 직접 확인)

| 상수명                                    | 값      | 설명                                       |
|-------------------------------------------|---------|--------------------------------------------|
| `SERVER_MAX_SESSIONS`                     | 4,096   | 최대 동시 VPN 세션 수                      |
| `SERVER_MAX_SESSIONS_FOR_CARRIER_EDITION` | 100,000 | Carrier Edition 최대 세션 수               |
| `MAX_HUBS`                                | 4,096   | 최대 Virtual Hub 수                        |
| `MAX_HUBS_FOR_CARRIER_EDITION`            | 100,000 | Carrier Edition 최대 Hub 수                |
| `MAX_ACCESSLISTS`                         | 32,768  | Hub당 최대 액세스리스트 항목 수 (= 4096×8) |
| `NAT_MAX_SESSIONS`                        | 4,096   | SecureNAT 최대 세션 수                     |
| `NAT_MAX_SESSIONS_KERNEL`                 | 65,536  | 커널 모드 NAT 최대 세션 수                 |
| `MAX_HUB_CERTS`                           | 4,096   | Hub당 최대 루트 CA 수                      |
| `MAX_HUB_LINKS`                           | 1,024   | Hub당 최대 Cascade 연결 수                 |

공식 스펙 페이지(softether.org/3-spec) 수치와 소스코드 상수값 일치 확인:
- Maximum Concurrent VPN Sessions: 4,096 ✅
- Maximum Virtual Hubs: 4,096 ✅
- Maximum Access List Entries: 32,768 ✅

---

## 4. SoftEther VPN 프로토콜 (Ethernet over HTTPS) 스펙 (확인일: 2026-08-05)

출처: softether.org/3-spec

| 항목          | 값                                                                             |
|---------------|--------------------------------------------------------------------------------|
| 페이로드      | Ethernet (IEEE 802.3) 프레임, 최대 1,514 bytes (VLAN 태그 포함 시 1,518 bytes) |
| 하위 전송     | TLS (TCP/IP + UDP/IP 하이브리드, IPv4/IPv6)                                    |
| TLS 버전      | 1.0, 1.1, 1.2, 1.3 지원                                                        |
| 데이터 압축   | zlib                                                                           |
| 병렬 TCP 연결 | 1~32개 (1개의 논리적 VPN 세션 구성)                                            |
| 재연결        | 무한 자동 재연결                                                               |
| Proxy 지원    | HTTP Proxy, SOCKS Proxy                                                        |
| NAT-T         | 기본 활성화 (NAT 뒤 서버에 포트포워딩 불필요)                                  |
| 방화벽 우회   | VPN over ICMP, VPN over DNS                                                    |
| 기반 표준     | RFC 2818 (HTTPS), RFC 5246 (TLS 1.2)                                           |

🟡 병렬 TCP 1~32 및 VPN over ICMP/DNS는 공식 스펙 페이지(softether.org/3-spec) 명시 사항이며, 소스코드 상수 직접 확인은 미완료입니다.

### 지원 인증 방식

출처: softether.org/3-spec

| 인증 방식                        | 설명                     |
|----------------------------------|--------------------------|
| Anonymous                        | 인증 없음                |
| Standard Password Authentication | 내부 사용자 DB 패스워드  |
| RADIUS Password Authentication   | 외부 RADIUS 서버         |
| NT Domain / Active Directory     | Windows 도메인 인증      |
| X.509 RSA PKI (파일)             | 키 파일 기반 인증서 인증 |
| X.509 RSA PKI (PKCS#11)          | 스마트카드 / USB 토큰    |

---

## 5. 지원 VPN 프로토콜 (확인일: 2026-08-05)

출처: softether.org/3-spec

| 프로토콜                | 모드              | 호환 클라이언트                              |
|-------------------------|-------------------|----------------------------------------------|
| SoftEther VPN (SSL-VPN) | L2 (Ethernet)     | SoftEther VPN Client (Windows/Linux)         |
| OpenVPN                 | L2 및 L3          | OpenVPN for Windows/Linux/Mac/iOS/Android    |
| L2TP/IPsec              | L2                | Windows/Mac/iOS/Android 기본 내장 클라이언트 |
| MS-SSTP                 | L2                | Windows Vista/7/8/10/11 기본 내장            |
| L2TPv3/IPsec            | L2 (Site-to-Site) | Cisco IOS                                    |
| EtherIP/IPsec           | L2 (Site-to-Site) | EtherIP 호환 OS                              |

---

## 6. L2TP/IPsec 서버 스펙 (확인일: 2026-08-05)

출처: softether.org/3-spec

| 항목          | 값                                                           |
|---------------|--------------------------------------------------------------|
| 사용자 인증   | PAP, MS-CHAPv2                                               |
| NAT-T         | RFC 3947 (IPsec over UDP 캡슐화)                             |
| UDP 포트      | UDP 500, UDP 4500                                            |
| 지원 해시     | MD5, SHA-1                                                   |
| 지원 DH Group | MODP 768 (Group 1), MODP 1024 (Group 2), MODP 1536 (Group 5) |

🟡 SoftEther의 L2TP/IPsec DH Group은 MODP 768/1024/1536 (Group 1/2/5)으로 모두 2048bit 미만입니다. NIST SP 800-56A Rev.3은 Group 14 (MODP 2048) 이상을 권장합니다. 보안 민감 환경에서는 SoftEther VPN 프로토콜(TLS 1.3) 또는 OpenVPN(AES-256-GCM) 사용을 권장합니다.

---

## 7. OpenVPN 서버 스펙 (확인일: 2026-08-05)

출처: softether.org/3-spec

| 항목        | 값                                                                                                                                                |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| 기본 포트   | TCP 443, 992, 5555 / UDP 1194                                                                                                                     |
| 동작 모드   | L2 (Bridging), L3 (Routing)                                                                                                                       |
| 지원 cipher | AES-128-CBC, AES-192-CBC, AES-256-CBC, BF-CBC, CAST-CBC, CAST5-CBC, DES-CBC, DES-EDE-CBC, DES-EDE3-CBC, DESX-CBC, RC2-40-CBC, RC2-64-CBC, RC2-CBC |
| 지원 해시   | SHA, SHA1, MD5, MD4, RMD160                                                                                                                       |
| 클론 방식   | OpenVPN Technologies Inc. 구현체와 호환                                                                                                           |

🟡 BF-CBC, DES 계열, RC2 계열은 취약한 cipher입니다. OpenVPN 2.5+ 공식 클라이언트는 BF-CBC를 기본에서 제거했습니다. 실사용 시 AES-256-CBC 또는 AES-256-GCM 사용을 권장합니다.

---

## 8. SSTP 서버 스펙 (확인일: 2026-08-05)

출처: softether.org/3-spec

| 항목            | 값                                                             |
|-----------------|----------------------------------------------------------------|
| 클론 방식       | Microsoft Windows Server 2008 R2/2012 SSTP-VPN 서버 클론       |
| 사용자 인증     | PAP, MS-CHAPv2                                                 |
| TLS             | TLS 1.3 기반 강력 cipher                                       |
| 호환 클라이언트 | Windows Vista/7/8/10/11/RT, Server 2008/2008 R2/2012 기본 내장 |
| VPN 토폴로지    | Remote-access VPN 전용                                         |

---

## 9. 지원 OS / CPU (확인일: 2026-08-05)

출처: softether.org/3-spec

| OS      | 아키텍처                                               |
|---------|--------------------------------------------------------|
| Windows | x86 (32bit), x64 (64bit) — Win98 ~ Server 2025, Win11  |
| Linux   | x86, x64, PowerPC, ARM EABI, ARM64, MIPS Little-Endian |
| macOS   | x86, x64, PowerPC — Mac OS X 10.4 Tiger 이상           |
| FreeBSD | x86, x64 (Stable Edition: Server/Bridge only)          |
| Solaris | x86, x64, SPARC (Server/Bridge only)                   |
| NetBSD  | x86, x64 (Developer Edition only)                      |
| OpenBSD | x86, x64 (Developer Edition only)                      |

### 하드웨어 최소 요구사항

출처: softether.org/3-spec

| 컴포넌트   | 최소 RAM                        | 권장 RAM                         | 디스크                 |
|------------|---------------------------------|----------------------------------|------------------------|
| VPN Server | 32 MB + 0.5 MB × (동시 세션 수) | 128 MB + 0.5 MB × (동시 세션 수) | 최소 100 MB, 권장 2 GB |
| VPN Client | 16 MB                           | 32 MB                            | -                      |

---

**작성일**: 2026-08-05

**마지막 업데이트**: 2026-08-05

© 2026 siasia86. Licensed under CC BY 4.0.
