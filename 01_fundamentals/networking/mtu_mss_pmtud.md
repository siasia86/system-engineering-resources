# MTU·MSS와 Path MTU Discovery

MTU(Maximum Transmission Unit, 한 링크가 한 번에 실어 나를 수 있는 IP 패킷 최대 크기)가 경로 중간에서 작아질 때 생기는 장애를 이해하고 진단하는 방법을 정리합니다. 터널·VPN·오버레이 네트워크에서 "ping은 되는데 큰 응답만 멈춘다"는 증상의 대부분이 여기에 속합니다.

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. 용어와 크기 계산](#1-용어와-크기-계산) / [2. 단편화](#2-단편화) / [3. Path MTU Discovery](#3-path-mtu-discovery) |
| [4. PMTUD 블랙홀](#4-pmtud-블랙홀) / [5. 캡슐화 오버헤드](#5-캡슐화-오버헤드) / [6. 진단 명령](#6-진단-명령)         |
| [7. 대응 방법](#7-대응-방법) / [8. 점검표](#8-점검표)                                                                |

---

## 1. 용어와 크기 계산

| 용어            | 의미                                                                              |
|-----------------|-----------------------------------------------------------------------------------|
| MTU             | 링크가 전달하는 IP 패킷(IP 헤더 포함)의 최대 바이트 수. 일반 Ethernet은 1500      |
| Path MTU (PMTU) | 출발지에서 목적지까지 경로에 있는 모든 링크 MTU 중 가장 작은 값                   |
| MSS             | TCP Maximum Segment Size. TCP가 한 세그먼트에 담는 데이터(payload) 최대 크기      |
| Jumbo frame     | 1500보다 큰 MTU(흔히 9000 전후). 경로의 모든 장비가 같은 값을 지원해야 함         |
| DF 비트         | IPv4 헤더의 Don't Fragment 플래그. 켜져 있으면 중간 라우터가 단편화하지 않고 버림 |

Ethernet 1500 MTU 기준 크기 계산:

```text
Ethernet frame (on wire, without preamble/FCS) = 14 + 1500 = 1514 bytes
 +----------+---------------------------------------------+
 | Eth hdr  | IP packet = MTU 1500                        |
 | 14 bytes | +--------+--------+------------------------+ |
 |          | | IPv4   | TCP    | TCP payload = MSS      | |
 |          | | 20     | 20     | 1460                   | |
 |          | +--------+--------+------------------------+ |
 +----------+---------------------------------------------+
```

| 경우                         | MSS 계산                    | 결과 |
|------------------------------|-----------------------------|------|
| IPv4, 옵션 없음              | 1500 - 20(IPv4) - 20(TCP)   | 1460 |
| IPv6, 확장 헤더 없음         | 1500 - 40(IPv6) - 20(TCP)   | 1440 |
| ICMP echo 최대 payload, IPv4 | 1500 - 20(IPv4) - 8(ICMP)   | 1472 |
| ICMPv6 echo 최대 payload     | 1500 - 40(IPv6) - 8(ICMPv6) | 1452 |

TCP 타임스탬프 같은 옵션이 붙으면 실제로 한 세그먼트에 담기는 데이터는 MSS보다 조금 작아집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 단편화

단편화(fragmentation)는 MTU보다 큰 IP 패킷을 여러 조각으로 나누어 보내고 목적지에서 다시 합치는 동작입니다.

| 항목          | IPv4 (RFC 791)                                       | IPv6 (RFC 8200)                               |
|---------------|------------------------------------------------------|-----------------------------------------------|
| 누가 나누는가 | 출발지와 중간 라우터 모두 가능(DF=0일 때)            | 출발지만 가능. 라우터는 나누지 않음           |
| 최소 링크 MTU | 모든 모듈은 68옥텟을 단편화 없이 전달할 수 있어야 함 | 모든 링크는 1280옥텟 이상이어야 함            |
| 너무 클 때    | DF=1이면 버리고 ICMP Type 3 Code 4를 돌려줌          | 버리고 ICMPv6 Packet Too Big(Type 2)을 돌려줌 |

단편화를 피하려는 이유:

- 조각 하나만 잃어도 전체 패킷을 다시 보내야 합니다.
- 방화벽·NAT·로드밸런서가 첫 조각 외에는 포트 정보를 볼 수 없어 뒤 조각을 버리는 경우가 있습니다.
- 재조립에 메모리와 시간이 들고, 조각 처리 경로는 장비에서 느린 경로로 처리되기도 합니다.

그래서 현대 TCP 스택은 기본으로 DF를 켜고 Path MTU Discovery로 크기를 맞춥니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Path MTU Discovery

PMTUD(RFC 1191 IPv4, RFC 8201 IPv6)는 ICMP 오류 메시지를 이용해 경로의 최소 MTU를 알아내는 방식입니다.

```text
Host A (MTU 1500)          Router R (next link MTU 1400)          Host B
     |  TCP 1500 bytes, DF=1   |                                     |
     |------------------------>|  too big for 1400 link -> drop      |
     |  ICMP type 3 code 4     |                                     |
     |  next-hop MTU = 1400    |                                     |
     |<------------------------|                                     |
     |  cache PMTU=1400 for B, resend 1400 bytes                     |
     |-------------------------------------------------------------->|
```

| 단계 | 동작                                                                             |
|------|----------------------------------------------------------------------------------|
| 1    | 출발지는 DF=1로 링크 MTU 크기의 패킷을 보냄                                      |
| 2    | 더 작은 MTU 링크 앞 라우터가 패킷을 버리고 ICMP 오류에 다음 링크 MTU를 실어 보냄 |
| 3    | 출발지 커널은 목적지별 PMTU를 캐시하고 TCP는 세그먼트 크기를 줄여 다시 보냄      |
| 4    | 캐시는 일정 시간 후 만료되어 더 큰 크기를 다시 시도함(Linux `mtu_expires`)       |

Linux 커널 관련 sysctl(ip-sysctl 문서 기준):

| sysctl                        | 의미                                        |
|-------------------------------|---------------------------------------------|
| `net.ipv4.ip_no_pmtu_disc`    | PMTUD 끄기. 기본 0(사용)                    |
| `net.ipv4.route.min_pmtu`     | PMTU 하한. 기본 552                         |
| `net.ipv4.route.mtu_expires`  | 캐시한 PMTU 정보를 유지하는 초              |
| `net.ipv4.tcp_mtu_probing`    | 0 끔, 1 블랙홀을 감지하면 사용, 2 항상 사용 |
| `net.ipv4.tcp_base_mss`       | MTU probing 시작 시 탐색 하한으로 쓰는 MSS  |
| `net.ipv4.tcp_probe_interval` | 재탐색 간격. 기본 10분(RFC 4821)            |

`tcp_mtu_probing`은 RFC 4821의 PLPMTUD(Packetization Layer PMTUD) 구현으로, ICMP에 의존하지 않고 TCP가 직접 크기를 시험해 보는 방식입니다. 현재 값은 `sysctl net.ipv4.tcp_mtu_probing`으로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. PMTUD 블랙홀

PMTUD는 ICMP 오류가 출발지까지 돌아와야 동작합니다. 경로의 방화벽이 ICMP를 모두 막으면 출발지는 패킷이 왜 사라졌는지 알 수 없습니다. 이를 PMTUD 블랙홀(RFC 2923)이라고 합니다.

전형적인 증상:

| 증상                                          | 이유                                     |
|-----------------------------------------------|------------------------------------------|
| ping, TCP 연결 수립(SYN/SYN-ACK)은 정상       | 작은 패킷이라 MTU를 넘지 않음            |
| SSH 접속 후 로그인 배너나 큰 출력에서 멈춤    | 큰 세그먼트부터 버려짐                   |
| HTTPS가 TLS 핸드셰이크 중 멈춤                | 인증서 체인이 담긴 큰 서버 응답이 버려짐 |
| 작은 API 응답은 되고 큰 파일 다운로드만 멈춤  | 크기에 따라 결과가 갈림                  |
| 같은 서버도 특정 경로(VPN 경유 등)에서만 문제 | 그 경로에만 작은 MTU 링크가 있음         |

🟡 주의: 보안 정책으로 ICMP를 막을 때도 IPv4 Type 3 Code 4와 ICMPv6 Type 2(Packet Too Big)는 허용해야 PMTUD가 동작합니다. IPv6는 라우터가 단편화하지 않으므로 Packet Too Big을 막으면 큰 패킷이 모두 실패합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 캡슐화 오버헤드

터널은 원래 패킷 앞에 헤더를 더 붙이므로, 바깥 링크 MTU가 1500이면 안쪽 MTU는 그만큼 작아져야 합니다.

| 캡슐화           | 추가되는 헤더(바깥 IPv4 기준)             | 오버헤드 | 안쪽 MTU(바깥 1500) |
|------------------|-------------------------------------------|----------|---------------------|
| 802.1Q VLAN 태그 | Ethernet 안 4바이트(IP MTU에는 영향 없음) | 0        | 1500                |
| GRE (기본 헤더)  | IPv4 20 + GRE 4                           | 24       | 1476                |
| IP-in-IP         | IPv4 20                                   | 20       | 1480                |
| VXLAN            | IPv4 20 + UDP 8 + VXLAN 8 + 안쪽 Eth 14   | 50       | 1450                |
| PPPoE            | PPPoE 6 + PPP 2                           | 8        | 1492                |
| WireGuard        | 바깥 IPv6 기준 40 + UDP 8 + WG 32         | 80       | 1420                |
| IPsec ESP        | 암호·모드·패딩에 따라 달라짐              | 가변     | 장비 문서로 확인    |

WireGuard는 바깥이 IPv6일 수 있는 경우를 가정해 80바이트를 빼므로 흔히 1420을 씁니다. IPsec·OpenVPN처럼 오버헤드가 설정에 따라 바뀌는 경우는 표 값으로 단정하지 말고 6절의 방법으로 실제 PMTU를 측정합니다. 헤더 구조는 [network_headers.md](./network_headers.md)의 GRE·VXLAN 절을 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 진단 명령

### 6.1 인터페이스 MTU 확인

```bash
ip link show                        # 각 인터페이스의 mtu 값
ip route get 192.0.2.10             # 해당 목적지로 나가는 인터페이스, 캐시된 mtu 표시
ip -s link show dev eth0            # 오류·드롭 카운터
```

### 6.2 DF를 켠 ping으로 최대 크기 찾기

`ping -s`는 ICMP payload 크기입니다. IPv4는 여기에 28바이트(IP 20 + ICMP 8)를 더한 값이 IP 패킷 크기입니다.

```bash
# Linux (iputils): -M do = 단편화 금지(DF=1)
ping -M do -s 1472 -c 3 192.0.2.10   # 1500 경로면 성공
ping -M do -s 1473 -c 3 192.0.2.10   # 실패: 로컬 MTU 초과면 "message too long", 경로 중간이면 "Frag needed" 또는 무응답

# IPv6: 헤더 40 + ICMPv6 8 = 48
ping -6 -M do -s 1452 -c 3 2001:db8::10
```

```powershell
# Windows: -f = DF 설정, -l = payload 크기
ping -f -l 1472 192.0.2.10
```

응답이 없을 때 크기를 줄여 가며 성공하는 최대값을 찾으면 그 값 + 28이 IPv4 PMTU입니다. ICMP echo 자체를 막는 경로에서는 이 방법을 쓸 수 없으므로 tracepath나 TCP 기반 확인을 함께 씁니다.

### 6.3 tracepath

`tracepath`는 root 권한 없이 hop별 PMTU를 보여 줍니다.

```bash
tracepath -n 192.0.2.10
#  1?: [LOCALHOST]                      pmtu 1500
#  1:  198.51.100.1                     0.512ms
#  2:  198.51.100.9                     1.104ms pmtu 1400
#  ...
#      Resume: pmtu 1400 hops 6 back 6
```

마지막 `Resume` 줄의 `pmtu`가 측정한 Path MTU입니다.

### 6.4 패킷 캡처로 확인

```bash
# ICMP "fragmentation needed"(type 3 code 4)만 보기
sudo tcpdump -ni any 'icmp[icmptype] == icmp-unreach and icmp[icmpcode] == 4'

# ICMPv6 Packet Too Big(type 2)
sudo tcpdump -ni any 'icmp6 and ip6[40] == 2'

# SYN의 MSS 옵션 확인
sudo tcpdump -ni eth0 'tcp[tcpflags] & tcp-syn != 0' -v
```

`ip6[40]`은 확장 헤더가 없는 경우에만 ICMPv6 타입 위치와 맞습니다. 캡처 결과 읽는 법은 [tcpdump_examples.md](./tcpdump_examples.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 대응 방법

| 방법                       | 내용                                              | 고려 사항                                           |
|----------------------------|---------------------------------------------------|-----------------------------------------------------|
| ICMP 오류 허용             | Type 3 Code 4, ICMPv6 Type 2를 방화벽에서 허용    | 근본 대책. 경로 장비를 내가 관리하지 못할 수 있음   |
| 터널 인터페이스 MTU 낮추기 | 터널 MTU를 오버헤드만큼 낮게 설정                 | 그 터널을 지나는 모든 트래픽에 적용됨               |
| MSS clamping               | 라우터·방화벽이 SYN의 MSS 옵션을 경로에 맞게 줄임 | TCP에만 효과. UDP(DNS, QUIC 등)는 해결 안 됨        |
| TCP MTU probing            | `net.ipv4.tcp_mtu_probing=1`                      | 호스트 단위, 블랙홀 감지 후 동작하므로 첫 지연 있음 |
| 경로 MTU 통일              | Jumbo frame을 쓰는 경우 경로 전체 MTU를 같게      | 스위치·하이퍼바이저·NIC까지 모두 확인               |

MTU 변경 예시:

```bash
# 일시 변경(재부팅 시 원복). 원격 접속 중인 인터페이스는 연결이 끊길 수 있음
sudo ip link set dev wg0 mtu 1420
```

🟡 주의: 원격 접속에 쓰는 인터페이스의 MTU를 바꾸면 세션이 끊길 수 있습니다. 콘솔 접근 수단을 확보한 뒤 작업하고, 영구 설정은 배포판의 네트워크 관리 도구(netplan, NetworkManager 등) 설정 파일에 반영합니다.

MSS clamping 예시(nftables, 포워딩하는 라우터에서):

```bash
# PMTU에 맞춰 SYN의 MSS를 줄임 (inet filter forward 체인이 이미 있다고 가정)
sudo nft add rule inet filter forward tcp flags syn tcp option maxseg size set rt mtu
```

```bash
# iptables 환경
sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
```

방화벽 규칙 구조는 [04_security/hardening/firewall_iptables_nftables.md](../../04_security/hardening/firewall_iptables_nftables.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 점검표

| 번호 | 점검 항목                                                 | 확인 방법                        |
|------|-----------------------------------------------------------|----------------------------------|
| 1    | 증상이 크기에 따라 갈리는가(작은 요청 성공, 큰 응답 실패) | curl로 작은·큰 응답 비교         |
| 2    | 양쪽 호스트와 터널 인터페이스의 MTU                       | `ip link show`                   |
| 3    | 경로 PMTU                                                 | `tracepath -n`, `ping -M do -s`  |
| 4    | ICMP Type 3 Code 4 / ICMPv6 Type 2가 돌아오는가           | tcpdump                          |
| 5    | SYN·SYN-ACK의 MSS 값이 경로에 맞는가                      | tcpdump `-v`로 MSS 옵션 확인     |
| 6    | 방화벽·보안그룹이 위 ICMP를 허용하는가                    | 규칙 목록                        |
| 7    | UDP 서비스(DNS, QUIC, VPN)도 영향을 받는가                | `dig +bufsize=1232`, 서비스 로그 |
| 8    | 변경 후 같은 측정으로 재확인했는가                        | 2~5 반복                         |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [RFC 791 — Internet Protocol](https://www.rfc-editor.org/rfc/rfc791) — ★★★★☆ (확인일 2026-11-16)
- [RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification](https://www.rfc-editor.org/rfc/rfc8200) — ★★★★☆ (확인일 2026-11-16)
- [RFC 1191 — Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc1191) — ★★★★☆ (확인일 2026-11-16)
- [RFC 8201 — Path MTU Discovery for IP version 6](https://www.rfc-editor.org/rfc/rfc8201) — ★★★★☆ (확인일 2026-11-16)
- [RFC 2923 — TCP Problems with Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc2923) — ★★★★☆ (확인일 2026-11-16)
- [RFC 4821 — Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821) — ★★★★☆ (확인일 2026-11-16)
- [Linux kernel — IP Sysctl](https://docs.kernel.org/networking/ip-sysctl.html) — ★★★☆☆ (확인일 2026-11-16)
- [tracepath(8) — Linux manual page](https://man7.org/linux/man-pages/man8/tracepath.8.html) — ★★★☆☆ (확인일 2026-11-16)
- [ping(8) — Linux manual page](https://man7.org/linux/man-pages/man8/ping.8.html) — ★★★☆☆ (확인일 2026-11-16)
- [nftables wiki — Mangling packet headers](https://wiki.nftables.org/wiki-nftables/index.php/Mangling_packet_headers) — ★★★☆☆ (확인일 2026-11-16)
- [WireGuard mailing list — Header / MTU sizes for Wireguard (2017-12)](https://lists.zx2c4.com/pipermail/wireguard/2017-December/002201.html) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
