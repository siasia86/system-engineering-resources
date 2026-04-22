# IPv6 주소 체계 가이드

## 목차

| 단계 | 섹션                                                                      |
|------|---------------------------------------------------------------------------|
| 기초 | [1. IPv6 개요](#1-ipv6-개요) / [2. 주소 구조](#2-주소-구조)               |
| 중급 | [3. 주소 표기법](#3-주소-표기법) / [4. 주요 주소 대역](#4-주요-주소-대역) |
| 고급 | [5. 서브넷](#5-서브넷) / [6. AWS VPC에서 IPv6](#6-aws-vpc에서-ipv6)       |
| 실전 | [7. IPv4와 비교](#7-ipv4와-비교) / [8. 실전 예시](#8-실전-예시)           |

---

## 1. IPv6 개요

IPv4 주소 고갈 문제를 해결하기 위해 설계된 차세대 인터넷 프로토콜.

| 항목          | IPv4           | IPv6                     |
|---------------|----------------|--------------------------|
| 주소 길이     | 32비트         | 128비트                  |
| 전체 주소 수  | 약 43억 개     | 약 3.4 × 10³⁸ 개         |
| 표기법        | 10진수 점 구분 | 16진수 콜론 구분         |
| NAT 필요 여부 | 필요           | 불필요                   |
| 브로드캐스트  | 있음           | 없음 (멀티캐스트로 대체) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 주소 구조

### 128비트 구성

```
2001:0db8:0000:0000:0000:0000:0000:0001

┌──────────────────────────┬──────────────────────────┐
│     Network Prefix       │      Interface ID        │
│        64 bits           │        64 bits           │
├──────────────────────────┼──────────────────────────┤
│  2001:0db8:0000:0000     │  0000:0000:0000:0001     │
└──────────────────────────┴──────────────────────────┘
```

- 16비트씩 8개 블록, 콜론(`:`)으로 구분
- 각 블록은 16진수 4자리

### 비트 구조 (/48 사이트, /64 서브넷 기준)

```
┌──────────────┬──────────┬──────────────────────────┐
│ Global Prefix│ Subnet ID│      Interface ID        │
│   48 bits    │ 16 bits  │        64 bits           │
└──────────────┴──────────┴──────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 주소 표기법

### 축약 규칙

```
Original:  2001:0db8:0000:0000:0000:0000:0000:0001

Rule 1: 각 블록 앞의 0 생략
        2001:db8:0:0:0:0:0:1

Rule 2: 연속된 0 블록을 :: 로 축약 (1회만 사용 가능)
        2001:db8::1
```

### 축약 예시

```
Full:      fe80:0000:0000:0000:0202:b3ff:fe1e:8329
No zeros:  fe80:0:0:0:202:b3ff:fe1e:8329
Shortened: fe80::202:b3ff:fe1e:8329
```

### 주의사항

```
:: 는 한 주소에 1번만 사용 가능

❌ 잘못된 예: 2001::db8::1
✅ 올바른 예: 2001:0:0:db8::1
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 주소 대역

```
2000::/3    → Global Unicast     (인터넷 공인 주소)
fc00::/7    → Unique Local       (IPv4 사설 IP와 유사)
fe80::/10   → Link-Local         (IPv4의 169.254.x.x)
::1/128     → Loopback           (IPv4의 127.0.0.1)
ff00::/8    → Multicast          (IPv4 브로드캐스트 대체)
::/128      → Unspecified
```

### 글로벌 유니캐스트 (2000::/3)

인터넷에서 직접 라우팅 가능한 공인 주소.

| 대역            | 용도                                     |
|-----------------|------------------------------------------|
| `2001:db8::/32` | 문서/예시용 예약 (RFC 3849), 실사용 불가 |
| `2001:4860::`   | Google                                   |
| `2400:cb00::`   | Cloudflare (아시아)                      |
| `240b::`        | KT (한국)                                |

### 고유 로컬 주소 (fc00::/7)

```
Range: fc00:: ~ fdff::...
Typical: fd00::/8

IPv4 사설 IP(10.x.x.x, 192.168.x.x)와 동일한 역할
인터넷 라우팅 불가, 조직 내부 전용
```

### 링크 로컬 (fe80::/10)

```
Range: fe80:: ~ febf::...

- 네트워크 인터페이스 활성화 시 자동 생성
- 동일 L2 세그먼트 내에서만 통신 가능
- 라우터 통과 불가
- IPv6 필수 주소 (항상 존재)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 서브넷

### 프리픽스 길이

| 프리픽스 | 용도               | 서브넷/호스트 수        |
|----------|--------------------|-------------------------|
| `/32`    | ISP 할당 단위      | -                       |
| `/48`    | 기업/사이트 단위   | 65,536개 서브넷         |
| `/56`    | 가정용 ISP 할당    | 256개 서브넷            |
| `/64`    | 단일 서브넷 (표준) | 2⁶⁴ ≈ 1.8 × 10¹⁹ 호스트 |
| `/128`   | 단일 호스트        | 1                       |

### /64가 표준인 이유

```
Interface ID (64 bits) = MAC address based auto-generation (EUI-64)
→ DHCP 없이도 IP 자동 설정 가능 (SLAAC)
→ /64보다 작으면 SLAAC 동작 불가
```

### EUI-64 (인터페이스 ID 자동 생성)

```
MAC: 00:02:b3:1e:83:29

Step 1: Insert ff:fe in the middle
        00:02:b3:ff:fe:1e:83:29

Step 2: Flip 7th bit of 1st byte (00 → 02)
        02:02:b3:ff:fe:1e:83:29

Interface ID: 0202:b3ff:fe1e:8329
Result IPv6:  fe80::202:b3ff:fe1e:8329/64
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. AWS VPC에서 IPv6

### 할당 구조

```
AWS → VPC:    /56 블록 할당
VPC → Subnet: /64 블록 할당 (고정, 변경 불가)

Example:
VPC:      2600:1f14:1234:5600::/56
Subnet 0: 2600:1f14:1234:5600::/64
Subnet 1: 2600:1f14:1234:5601::/64
...
Subnet N: 2600:1f14:1234:56ff::/64  (max 256 subnets)
```

### IPv4와 차이점

| 항목        | IPv4                      | IPv6                     |
|-------------|---------------------------|--------------------------|
| VPC 할당    | 자유롭게 지정             | AWS가 /56 자동 할당      |
| 서브넷 크기 | 자유 (/28~/16 등)         | /64 고정                 |
| 예약 IP     | 5개                       | 없음                     |
| 인터넷 통신 | IGW + 공인 IP 또는 NAT GW | IGW 또는 Egress-only IGW |

### Egress-only Internet Gateway

```
IPv4: Private Subnet → NAT Gateway → Internet (outbound only)
IPv6: Private Subnet → Egress-only IGW → Internet (outbound only)

이유: IPv6는 공인 주소이므로 인바운드 차단을 위해 별도 게이트웨이 필요
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. IPv4와 비교

| 항목         | IPv4               | IPv6                   |
|--------------|--------------------|------------------------|
| 주소 고갈    | 고갈됨             | 사실상 무한            |
| NAT          | 필수               | 불필요                 |
| 브로드캐스트 | 있음               | 없음 (멀티캐스트 대체) |
| 헤더 크기    | 20~60바이트 (가변) | 40바이트 (고정)        |
| 자동 설정    | DHCP 필요          | SLAAC 지원             |
| 보안         | IPSec 선택         | IPSec 기본 지원        |
| 서브넷 표준  | /24 일반적         | /64 표준               |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실전 예시

### 주소 판별

```
fe80::1               → Link-Local (자동 생성, 로컬 전용)
::1                   → Loopback (localhost)
fd00::1               → Unique Local (사설 IP)
2001:db8::1           → 문서용 예약 (실사용 불가)
2001:4860:4860::8888  → Google DNS (공인)
```

### Linux 명령어

```bash
# IPv6 주소 확인
ip -6 addr show

# IPv6 라우팅 테이블
ip -6 route show

# IPv6 ping
ping6 ::1
ping6 2001:4860:4860::8888
```

### Python 스크립트

```python
import ipaddress

network = ipaddress.ip_network('2001:db8::/48')
print(f"Network:    {network.network_address}")
print(f"Prefix:     {network.prefixlen}")
print(f"Total IPs:  {network.num_addresses:,}")

subnets = list(network.subnets(new_prefix=64))
print(f"/64 subnets: {len(subnets):,}")
print(f"First:       {subnets[0]}")
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

| RFC      | 내용                                           |
|----------|------------------------------------------------|
| RFC 4291 | IPv6 Addressing Architecture                   |
| RFC 3849 | IPv6 Address Prefix Reserved for Documentation |
| RFC 4193 | Unique Local IPv6 Unicast Addresses            |
| RFC 4862 | IPv6 SLAAC                                     |
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
