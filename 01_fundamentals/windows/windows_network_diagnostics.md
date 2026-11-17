# Windows 네트워크 진단 명령

Windows Server에서 연결 장애를 계층별로 좁히는 명령을 정리합니다. PowerShell의 NetTCPIP·DnsClient 모듈 cmdlet을 중심으로, 기존 `ipconfig`·`netstat`과의 대응과 내장 패킷 캡처 도구 `pktmon`까지 다룹니다. 리소스(CPU·메모리·디스크) 분석은 [windows_server_resource_analysis.md](./windows_server_resource_analysis.md)를 봅니다.

## 목차

| 섹션                                                                                                                                           |
|------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 진단 순서와 명령 대응표](#1-진단-순서와-명령-대응표) / [2. 인터페이스와 주소](#2-인터페이스와-주소) / [3. 라우팅과 이웃](#3-라우팅과-이웃) |
| [4. DNS 확인](#4-dns-확인) / [5. 연결 시험 Test-NetConnection](#5-연결-시험-test-netconnection) / [6. 소켓과 포트](#6-소켓과-포트)             |
| [7. 방화벽 확인](#7-방화벽-확인) / [8. 패킷 캡처 pktmon](#8-패킷-캡처-pktmon) / [9. 증상별 점검표](#9-증상별-점검표)                           |

---

## 1. 진단 순서와 명령 대응표

장애를 아래 계층 순서로 확인하면 원인 범위를 빠르게 좁힐 수 있습니다.

```text
[1] Link / IP config   -> is the adapter up, does it have the right IP?
[2] Route / Neighbor   -> which interface and gateway, is ARP resolved?
[3] Name resolution    -> does the name resolve to the expected IP?
[4] Reachability       -> ICMP / TCP port reachable?
[5] Local socket       -> is the service listening, which process?
[6] Firewall           -> is a rule blocking it?
[7] Packet capture     -> where is the packet dropped?
```

| 목적                | 기존 명령                        | PowerShell cmdlet                | Linux 대응              |
|---------------------|----------------------------------|----------------------------------|-------------------------|
| 주소·게이트웨이·DNS | `ipconfig /all`                  | `Get-NetIPConfiguration`         | `ip addr`, `resolvectl` |
| 어댑터 상태         | `netsh interface show interface` | `Get-NetAdapter`                 | `ip link`               |
| 라우팅 표           | `route print`                    | `Get-NetRoute`                   | `ip route`              |
| ARP / NDP 표        | `arp -a`                         | `Get-NetNeighbor`                | `ip neigh`              |
| DNS 질의            | `nslookup`                       | `Resolve-DnsName`                | `dig`                   |
| DNS 캐시            | `ipconfig /displaydns`           | `Get-DnsClientCache`             | `resolvectl statistics` |
| 포트 연결 시험      | `telnet host port`               | `Test-NetConnection -Port`       | `nc -zv`                |
| 경로 추적           | `tracert`, `pathping`            | `Test-NetConnection -TraceRoute` | `traceroute`, `mtr`     |
| TCP 연결·리슨 목록  | `netstat -ano`                   | `Get-NetTCPConnection`           | `ss -tanp`              |
| UDP 리슨 목록       | `netstat -ano -p udp`            | `Get-NetUDPEndpoint`             | `ss -uanp`              |
| 패킷 캡처           | `netsh trace`                    | `pktmon`(실행 파일)              | `tcpdump`               |

PowerShell cmdlet은 객체를 돌려주므로 `Where-Object`, `Select-Object`, `Group-Object`로 걸러 내고 집계하기 쉽습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 인터페이스와 주소

```powershell
# 어댑터 상태, 링크 속도
Get-NetAdapter | Format-Table Name, InterfaceDescription, Status, LinkSpeed, MacAddress

# 인터페이스별 IP, 게이트웨이, DNS 서버를 한 번에
Get-NetIPConfiguration -Detailed

# IPv4 주소만, 출처(수동/DHCP) 포함
Get-NetIPAddress -AddressFamily IPv4 | Format-Table InterfaceAlias, IPAddress, PrefixLength, PrefixOrigin

# 인터페이스별 MTU(NlMtu)와 메트릭
Get-NetIPInterface | Format-Table InterfaceAlias, AddressFamily, NlMtu, InterfaceMetric, Dhcp

# 송수신 통계, 오류·폐기 카운터 확인용
Get-NetAdapterStatistics
```

확인 기준:

| 항목                    | 정상 기대                   | 이상 시 의심                             |
|-------------------------|-----------------------------|------------------------------------------|
| `Status`                | Up                          | 케이블·가상 스위치·드라이버              |
| IPv4 주소가 169.254.x.x | 나오면 안 됨                | DHCP 응답 없음(APIPA 자동 주소)          |
| `PrefixOrigin`          | 의도한 값(Manual 또는 Dhcp) | 정적 IP 서버가 DHCP로 바뀌었는지         |
| `NlMtu`                 | 경로와 맞는 값(일반 1500)   | VPN·터널 환경의 MTU 문제                 |
| `InterfaceMetric`       | 주 인터페이스가 가장 낮음   | 의도하지 않은 인터페이스로 트래픽이 나감 |

MTU 문제의 원리는 [mtu_mss_pmtud.md](../networking/mtu_mss_pmtud.md)를 봅니다. Windows에서는 `ping -f -l <크기>`로 DF를 켠 시험을 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 라우팅과 이웃

```powershell
# 기본 경로(0.0.0.0/0)와 다음 hop
Get-NetRoute -DestinationPrefix 0.0.0.0/0 | Format-Table ifIndex, InterfaceAlias, NextHop, RouteMetric

# 특정 목적지로 갈 때 실제로 선택되는 경로와 출발지 주소
Find-NetRoute -RemoteIPAddress 192.0.2.10

# ARP(IPv4) / NDP(IPv6) 이웃 표
Get-NetNeighbor -AddressFamily IPv4 | Where-Object State -ne 'Unreachable'
```

`Find-NetRoute`는 여러 경로 중 실제로 고른 경로와 출발지 IP를 함께 보여 주므로, 인터페이스가 여러 개인 서버(관리망·서비스망 분리)에서 "응답이 엉뚱한 인터페이스로 나간다"는 문제를 확인할 때 씁니다. 같은 정보를 `Test-NetConnection -DiagnoseRouting`으로도 볼 수 있습니다(5절).

🟡 주의: `route add`, `New-NetRoute`, `Remove-NetRoute`는 원격 접속 경로를 끊을 수 있습니다. 콘솔(하이퍼바이저 콘솔, iLO·iDRAC 등) 접근을 확보한 뒤 실행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. DNS 확인

```powershell
# 기본 질의(A와 AAAA 모두)
Resolve-DnsName www.example.com

# 특정 서버에, 특정 타입으로
Resolve-DnsName www.example.com -Type A -Server 192.0.2.53

# hosts 파일을 건너뛰고 DNS만 사용(LLMNR·NetBIOS 제외)
Resolve-DnsName www.example.com -DnsOnly -NoHostsFile

# TCP로만 질의(TCP 53 경로 확인)
Resolve-DnsName www.example.com -TcpOnly

# 클라이언트 캐시 확인과 비우기
Get-DnsClientCache | Where-Object Entry -like '*example.com*'
Clear-DnsClientCache

# 인터페이스별 DNS 서버 설정
Get-DnsClientServerAddress -AddressFamily IPv4
```

| 매개변수       | 의미                                           |
|----------------|------------------------------------------------|
| `-Type`        | 질의 타입. 기본은 A_AAAA(A와 AAAA 모두)        |
| `-Server`      | 질의할 DNS 서버. 생략하면 인터페이스 설정 서버 |
| `-DnsOnly`     | DNS 프로토콜만 사용(LLMNR·NetBIOS 질의 안 함)  |
| `-NoHostsFile` | hosts 파일을 보지 않음                         |
| `-CacheOnly`   | 로컬 캐시만으로 답함                           |
| `-NoRecursion` | 서버에 재귀하지 말라고 요청                    |
| `-TcpOnly`     | TCP만 사용                                     |
| `-DnssecOk`    | DNSSEC OK 비트 설정                            |

hosts 파일 위치는 `C:\Windows\System32\drivers\etc\hosts`입니다. `Resolve-DnsName`과 `-DnsOnly -NoHostsFile` 결과가 다르면 hosts 파일이나 LLMNR·NetBIOS 응답이 끼어든 것입니다. DNS 동작 원리는 [dns_resolution_troubleshooting.md](../networking/dns_resolution_troubleshooting.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 연결 시험 Test-NetConnection

`Test-NetConnection`(별칭 `tnc`)은 ping, TCP 포트 시험, 경로 추적, 경로 선택 진단을 한 cmdlet으로 합니다. 대상을 생략하면 Microsoft가 정한 기본 대상(문서 예시 기준 `internetbeacon.msedge.net`)에 시험합니다.

```powershell
# ICMP ping
Test-NetConnection 192.0.2.10

# TCP 포트 연결 시험
Test-NetConnection 192.0.2.10 -Port 443

# 자주 쓰는 포트 이름: HTTP, RDP, SMB, WINRM
Test-NetConnection 192.0.2.10 -CommonTCPPort RDP

# 결과를 True/False만 받아 스크립트에서 사용
Test-NetConnection 192.0.2.10 -Port 5985 -InformationLevel Quiet

# 경로 추적(최대 hop 지정)
Test-NetConnection 192.0.2.10 -TraceRoute -Hops 20

# 경로·출발지 주소 선택 이유
Test-NetConnection 192.0.2.10 -DiagnoseRouting -InformationLevel Detailed
```

결과 읽기:

| 속성                 | 의미                                       |
|----------------------|--------------------------------------------|
| `RemoteAddress`      | 이름을 해석한 결과 실제 시험한 IP          |
| `SourceAddress`      | 이 서버에서 사용한 출발지 IP               |
| `InterfaceAlias`     | 나간 인터페이스                            |
| `PingSucceeded`      | ICMP echo 응답 여부                        |
| `TcpTestSucceeded`   | TCP 3-way handshake 성공 여부              |
| `NetRoute (NextHop)` | `-InformationLevel Detailed`일 때 다음 hop |

판단 기준:

- `PingSucceeded=False`, `TcpTestSucceeded=True`: 경로는 정상이고 ICMP만 막혀 있습니다.
- `TcpTestSucceeded=False`가 오래 걸린 뒤 실패: 중간에서 패킷이 버려집니다(방화벽 drop, 경로 없음).
- `TcpTestSucceeded=False`가 즉시 실패: 상대가 RST로 거부했을 가능성이 큽니다(리슨 없음, 방화벽 reject).

`Test-NetConnection`은 TCP만 시험합니다. UDP 서비스는 서비스 자체의 클라이언트로 확인하거나 8절의 패킷 캡처로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 소켓과 포트

```powershell
# 리슨 중인 포트와 소유 프로세스
Get-NetTCPConnection -State Listen |
  Select-Object LocalAddress, LocalPort, OwningProcess,
    @{n='Process';e={(Get-Process -Id $_.OwningProcess).ProcessName}} |
  Sort-Object LocalPort

# 특정 포트로 들어온 연결 수
(Get-NetTCPConnection -LocalPort 443 -State Established).Count

# 상태별 연결 수 집계(TIME_WAIT, CLOSE_WAIT 확인)
Get-NetTCPConnection | Group-Object State | Sort-Object Count -Descending |
  Select-Object Count, Name

# 원격 주소별 연결 수 상위 10
Get-NetTCPConnection -State Established | Group-Object RemoteAddress |
  Sort-Object Count -Descending | Select-Object -First 10 Count, Name

# UDP 리슨
Get-NetUDPEndpoint | Sort-Object LocalPort | Select-Object LocalAddress, LocalPort, OwningProcess
```

`-State`에 쓸 수 있는 값은 Bound, Closed, CloseWait, Closing, DeleteTCB, Established, FinWait1, FinWait2, LastAck, Listen, SynReceived, SynSent, TimeWait입니다. 상태의 의미는 [tcp_state_concepts.md](../networking/tcp_state_concepts.md)를 봅니다.

### 6.1 동적 포트 범위

Windows Vista·Server 2008 이후 아웃바운드 연결에 쓰는 동적(임시) 포트 기본 범위는 49152~65535입니다. 다른 서버로 연결을 많이 여는 서버(프록시, 배치 작업)에서 TIME_WAIT가 쌓이면 이 범위를 다 써서 새 연결이 실패할 수 있습니다.

```powershell
netsh int ipv4 show dynamicport tcp
netsh int ipv4 show dynamicport udp
```

범위 변경은 `netsh int ipv4 set dynamicport tcp start=<시작> num=<개수>` 형식이며, Microsoft 문서 기준 최소 개수는 255, 최소 시작 포트는 1025입니다. 🟡 주의: 범위를 바꾸면 그 범위와 겹치는 포트로 리슨하는 서비스나 방화벽 규칙(RPC 등)에 영향을 줄 수 있으므로 변경 전 영향 범위를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 방화벽 확인

```powershell
# 프로필(Domain/Private/Public)별 사용 여부와 기본 동작
Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction

# 현재 네트워크 연결이 어떤 프로필인지
Get-NetConnectionProfile

# 특정 포트를 허용하는 인바운드 규칙 찾기
Get-NetFirewallPortFilter -Protocol TCP |
  Where-Object LocalPort -eq 443 |
  Get-NetFirewallRule |
  Where-Object { $_.Enabled -eq 'True' -and $_.Direction -eq 'Inbound' } |
  Format-Table DisplayName, Profile, Action
```

자주 보는 원인:

| 원인                                         | 확인 방법                                          |
|----------------------------------------------|----------------------------------------------------|
| 연결 프로필이 Public으로 잡혀 규칙이 안 맞음 | `Get-NetConnectionProfile`의 `NetworkCategory`     |
| 규칙이 특정 프로필에만 적용됨                | 규칙의 `Profile` 열                                |
| 규칙이 특정 프로그램에만 적용됨              | `Get-NetFirewallApplicationFilter`로 프로그램 경로 |
| 그룹 정책(GPO)이 로컬 규칙을 덮음            | `gpresult /r`, 규칙의 `PolicyStoreSource`          |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 패킷 캡처 pktmon

`pktmon`(Packet Monitor)은 Windows 10과 Windows Server 2019(버전 1809) 이후 기본 포함된 패킷 캡처·드롭 감지 도구입니다. 네트워크 스택의 여러 구성 요소(NIC, 필터 드라이버, 가상 스위치, 프로토콜)에서 패킷을 보고, 어느 구성 요소에서 왜 버렸는지(drop reason)를 기록합니다. 관리자 권한으로 실행합니다.

```powershell
# 1. 필터 설정(필터 없이 캡처하면 양이 많아 분석이 어려움)
pktmon filter remove
pktmon filter add -i 192.0.2.10 -p 443
pktmon filter list

# 2. 캡처 시작(-c = 패킷 캡처). NIC 구성 요소만 보려면 --comp nics
pktmon start -c

# 3. 문제 재현 후 카운터로 흐름 확인
pktmon counters

# 4. 중지(현재 폴더에 PktMon.etl 생성)
pktmon stop

# 5. 변환: 텍스트 또는 Wireshark용 pcapng
pktmon etl2txt PktMon.etl
pktmon etl2pcap PktMon.etl --out capture.pcapng
pktmon etl2pcap PktMon.etl --drop-only --out drops.pcapng
```

| 명령 / 옵션                | 의미                                                   |
|----------------------------|--------------------------------------------------------|
| `filter add -i IP -p PORT` | IP·포트 조건. 출발지·목적지를 구분하지 않음. 최대 32개 |
| `filter add -t tcp syn`    | 프로토콜과 TCP 플래그 조건                             |
| `start -c --type drop`     | 버려진 패킷만 기록                                     |
| `start -c --comp nics`     | NIC 구성 요소에서만 캡처                               |
| `counters`                 | 구성 요소별 송수신·드롭 수                             |
| `list`                     | 네트워크 스택 구성 요소와 ID                           |
| `etl2pcap --drop-only`     | 드롭된 패킷만 pcapng로 변환                            |

🟡 주의: 기본 기록 방식은 순환(circular)이라 파일 크기 상한에 닿으면 오래된 패킷을 덮어씁니다. 기본 캡처 길이는 패킷당 128바이트로 헤더 분석에는 충분하지만 payload 전체가 필요하면 `--pkt-size 0`을 지정합니다. 캡처 파일에는 실제 통신 내용이 들어 있으므로 외부 공유 전에 민감 정보를 확인합니다.

pcapng 변환 시에는 드롭 정보와 구성 요소 정보가 빠집니다. 드롭 원인을 보려면 `etl2txt` 결과나 `pktmon counters`를 함께 봅니다. Linux 쪽 패킷 분석은 [packet_analysis.md](../networking/packet_analysis.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 증상별 점검표

| 증상                              | 먼저 볼 명령                                                              | 판단                                   |
|-----------------------------------|---------------------------------------------------------------------------|----------------------------------------|
| 아무 곳에도 연결 안 됨            | `Get-NetAdapter`, `Get-NetIPConfiguration`                                | 링크 다운, APIPA 주소, 게이트웨이 없음 |
| 이름으로만 안 됨                  | `Resolve-DnsName`, `Test-NetConnection IP -Port`                          | IP로는 되면 DNS 문제                   |
| 특정 포트만 안 됨                 | `Test-NetConnection -Port`, 대상에서 `Get-NetTCPConnection -State Listen` | 리슨 없음 또는 방화벽                  |
| 들어오는 연결만 안 됨             | `Get-NetFirewallProfile`, `Get-NetConnectionProfile`                      | Public 프로필, 인바운드 규칙 누락      |
| 응답이 다른 인터페이스로 나감     | `Find-NetRoute`, `Test-NetConnection -DiagnoseRouting`                    | 인터페이스 메트릭, 경로 설정           |
| 큰 전송만 멈춤                    | `Get-NetIPInterface`의 NlMtu, `ping -f -l`                                | MTU / PMTUD 문제                       |
| 아웃바운드 연결이 간헐적으로 실패 | `Get-NetTCPConnection` 상태 집계, `netsh int ipv4 show dynamicport tcp`   | TIME_WAIT 누적으로 동적 포트 고갈      |
| 패킷이 어디서 사라지는지 모름     | `pktmon start -c --type drop`, `pktmon counters`                          | 드롭 구성 요소와 drop reason 확인      |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [Test-NetConnection (NetTCPIP) — Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection) — ★★★☆☆ (확인일 2026-11-16)
- [Get-NetTCPConnection (NetTCPIP) — Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection) — ★★★☆☆ (확인일 2026-11-16)
- [Resolve-DnsName (DnsClient) — Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/dnsclient/resolve-dnsname) — ★★★☆☆ (확인일 2026-11-16)
- [Packet Monitor (Pktmon) — Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/networking/technologies/pktmon/pktmon) — ★★★☆☆ (확인일 2026-11-16)
- [Pktmon command formatting — Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/networking/technologies/pktmon/pktmon-syntax) — ★★★☆☆ (확인일 2026-11-16)
- [pktmon etl2pcap — Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/pktmon-etl2pcap) — ★★★☆☆ (확인일 2026-11-16)
- [The default dynamic port range for TCP/IP has changed — Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/default-dynamic-port-range-tcpip-chang) — ★★★☆☆ (확인일 2026-11-16)
- [NetSecurity module (Get-NetFirewallRule 등) — Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/netsecurity/) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
