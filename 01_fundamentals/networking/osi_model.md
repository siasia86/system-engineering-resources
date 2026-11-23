# OSI 모델
<!-- reference: _reference/osi_model_official_notes.md -->

네트워크 통신을 일곱 계층으로 나눠 설명하는 참조 모델입니다. 실제 인터넷 프로토콜은 네 계층(TCP/IP)으로 동작하지만, 장애를 "어느 계층 문제인가"로 좁힐 때 OSI 계층 이름을 공통 언어로 씁니다. 이 문서만으로 계층별 역할과 프로토콜 → TCP/IP 계층과의 대응 → 계층별 진단 명령과 순서까지 따라 할 수 있게 썼습니다.

- 기준: ITU-T X.200 (ISO/IEC 7498-1과 같은 내용), RFC 1122
- 예제 시험: 2026-11-23 컨테이너 두 개(nginx와 `nicolaka/netshoot:v0.16`)를 같은 Docker 네트워크에 두고 4절 명령을 실행해 결과를 확인

## 목차

| 섹션                                                                                     |
|------------------------------------------------------------------------------------------|
| [1. 일곱 계층](#1-일곱-계층) / [2. TCP/IP 계층과의 대응](#2-tcpip-계층과의-대응)         |
| [3. 캡슐화](#3-캡슐화) / [4. 계층별 진단](#4-계층별-진단) / [5. 진단 순서](#5-진단-순서) |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                        |

---

## 1. 일곱 계층

| 번호 | 계층         | 하는 일                              | 데이터 단위 | 예                                   | 장비·구성 요소          |
|------|--------------|--------------------------------------|-------------|--------------------------------------|-------------------------|
| 7    | Application  | 사용자 프로그램이 쓰는 통신 규칙     | 메시지      | HTTP, DNS, SSH, SMTP, FTP            | 웹 서버, L7 로드 밸런서 |
| 6    | Presentation | 데이터 표현·인코딩·암호화            | 메시지      | 문자 인코딩, 압축, (TLS의 일부 역할) | -                       |
| 5    | Session      | 대화의 시작·유지·종료                | 메시지      | (RPC 세션, TLS 세션 재개 등)         | -                       |
| 4    | Transport    | 끝점 간 전달, 포트, 신뢰성·흐름 제어 | 세그먼트    | TCP, UDP, QUIC(UDP 위)               | 방화벽 포트 규칙, L4 LB |
| 3    | Network      | 주소 지정과 경로 선택                | 패킷        | IPv4, IPv6, ICMP                     | 라우터, L3 스위치       |
| 2    | Data Link    | 같은 링크 안의 프레임 전달, MAC 주소 | 프레임      | Ethernet, ARP, VLAN(802.1Q), Wi-Fi   | 스위치, 브리지          |
| 1    | Physical     | 비트를 전기·빛·전파 신호로 전송      | 비트        | 케이블, 광, 무선 신호                | 케이블, 트랜시버, 허브  |

5·6계층은 TCP/IP에서 따로 두지 않아 괄호 안의 예는 "그 역할을 하는 기능"입니다. TLS처럼 한 계층에 딱 맞지 않는 프로토콜이 있으므로 계층 배치는 정확한 분류보다 대응으로 이해합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. TCP/IP 계층과의 대응

RFC 1122는 인터넷 프로토콜을 네 계층으로 정의하고, 인터넷의 애플리케이션 계층이 OSI의 Presentation·Application 기능을 합친 것이라고 설명합니다.

| TCP/IP (RFC 1122) | 대응하는 OSI 계층 | 대표 프로토콜             |
|-------------------|-------------------|---------------------------|
| Application       | 7 · 6 · (5)       | HTTP, DNS, SSH, TLS 위 앱 |
| Transport         | 4                 | TCP, UDP                  |
| Internet          | 3                 | IP, ICMP                  |
| Link              | 2 · 1             | Ethernet, ARP             |

"L4 로드 밸런서", "L7 방화벽"처럼 장비 이름에 붙는 번호는 OSI 번호입니다. L4는 IP·포트까지 보고, L7은 HTTP 경로·헤더까지 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 캡슐화

보내는 쪽은 위 계층의 데이터에 아래 계층의 헤더를 차례로 붙이고, 받는 쪽은 반대로 벗깁니다.

```text
[HTTP 요청]                                         <- 7 Application
[TCP 헤더 | HTTP 요청]                              <- 4 Transport (세그먼트)
[IP 헤더 | TCP 헤더 | HTTP 요청]                    <- 3 Network (패킷)
[Ethernet 헤더 | IP | TCP | HTTP 요청 | FCS]        <- 2 Data Link (프레임)
0101... 신호                                        <- 1 Physical
```

각 헤더의 필드 구조는 [네트워크 헤더](./network_headers.md)에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 계층별 진단

| 계층 | 확인할 것           | 명령                                                      | 정상 결과 예                                 |
|------|---------------------|-----------------------------------------------------------|----------------------------------------------|
| 1·2  | 링크가 올라왔는지   | `ip -br link show eth0`                                   | `UP`, `LOWER_UP`                             |
| 2    | 이웃 MAC을 알았는지 | `ip neigh show`                                           | 대상 IP에 `lladdr ... REACHABLE`             |
| 3    | 주소와 기본 경로    | `ip -br addr`, `ip route show default`                    | 주소 할당, `default via <게이트웨이>`        |
| 3    | 도달 가능한지       | `ping -c1 <대상>`                                         | `0% packet loss`                             |
| 4    | 포트가 열려 있는지  | `nc -zv -w2 <대상> 80`                                    | `succeeded!` (닫혔으면 `Connection refused`) |
| 7    | 서비스가 응답하는지 | `curl -s -o /dev/null -w '%{http_code}\n' http://<대상>/` | `200`                                        |
| 2~4  | 실제 오간 패킷      | `tcpdump -i eth0 -nn -e -c 3 tcp port 80`                 | `Flags [S]`, `[S.]`, `[.]` 3-way handshake   |

시험에서 본 흐름입니다(주소는 예시).

```text
$ ip neigh show                     # ping 전에는 비어 있음
$ ping -c1 web
64 bytes from web (192.0.2.2): icmp_seq=1 ttl=64 time=0.036 ms
$ ip neigh show                     # ping 뒤 ARP로 MAC을 배움
192.0.2.2 dev eth0 lladdr <MAC> REACHABLE
$ nc -zv -w2 web 81
nc: connect to web (192.0.2.2) port 81 (tcp) failed: Connection refused
```

`Connection refused`는 3·4계층까지는 닿았고(상대가 RST로 응답) 그 포트에 서비스가 없다는 뜻입니다. 응답 없이 시간 초과가 나면 경로나 방화벽에서 막혔을 가능성이 큽니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 진단 순서

아래에서 위로 올라가며 처음 실패한 계층을 찾습니다.

| 순서 | 질문                         | 실패하면 볼 곳                                    |
|------|------------------------------|---------------------------------------------------|
| 1    | 링크가 UP인가                | 케이블·NIC·가상 인터페이스, `ip link set eth0 up` |
| 2    | 게이트웨이의 MAC을 아는가    | VLAN, 스위치 포트, ARP 응답 (`ip neigh`)          |
| 3    | IP·경로가 맞고 ping이 되는가 | 주소·서브넷·라우팅, ICMP 차단 여부                |
| 4    | 포트가 열려 있는가           | 서비스 기동, `ss -ltn`, 방화벽·보안 그룹          |
| 5    | 이름이 맞는 주소로 풀리는가  | DNS (`dig`)                                       |
| 6    | TLS가 협상되는가             | 인증서, 프로토콜 판 (`openssl s_client`)          |
| 7    | 앱이 올바른 응답을 주는가    | 앱 로그, 상태 코드, 프록시 설정                   |

ping은 ICMP를 막는 환경이 많아 실패해도 바로 3계층 장애로 단정하지 않고 4계층(포트) 확인으로 함께 판단합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [네트워크 헤더](./network_headers.md) — 계층별 헤더 필드
- [Linux 네트워크 도구](../linux/linux_network_tools.md) — ip·ss·dig·curl·mtr·nmap
- [패킷 분석](./packet_analysis.md) — tcpdump·Wireshark
- [DNS 이름 해석과 장애 진단](./dns_resolution_troubleshooting.md) — 5절 이름 해석 단계

---

## 참고 자료

- ITU-T: [X.200 Basic Reference Model](https://www.itu.int/rec/T-REC-X.200-199407-I/en) — ★★★★☆
- IETF: [RFC 1122 Requirements for Internet Hosts](https://www.rfc-editor.org/rfc/rfc1122) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
