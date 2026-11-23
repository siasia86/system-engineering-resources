# Linux 네트워크 점검 도구 (ip·ss·dig·curl·mtr·nmap)
<!-- reference: _reference/linux_network_tools_official_notes.md -->

Linux 서버에서 주소·경로 확인, 열린 포트와 연결 확인, DNS 조회, HTTP 응답 시간 측정, 경로상의 손실 확인, 포트 열림 검사를 하는 도구 사용법입니다. 이 문서만으로 설치 → 도구별 사용 → 계층 순서대로 점검 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: iproute2 7.3.0, BIND 9.20(dig), curl 8.23.0, mtr 0.96, Nmap 7.993 (2026-11-23 확인)
- 예제 시험: 2026-11-23, Ubuntu 24.04의 iproute2 6.1.0·dig 9.18·curl 8.5.0·mtr 0.95·nmap 7.94에서 3~8절 명령을 실행해 확인(nmap은 자기 호스트만 검사). 주소는 문서용 예시 대역으로 바꿔 적음

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. ip](#3-ip)                                         |
| [4. ss](#4-ss) / [5. dig](#5-dig) / [6. curl](#6-curl)                                           |
| [7. ping·tracepath·mtr](#7-pingtracepathmtr) / [8. nmap](#8-nmap) / [9. 점검 순서](#9-점검-순서) |
| [10. 검증](#10-검증) / [11. 트러블슈팅](#11-트러블슈팅) / [함께 보기](#함께-보기)                |

---

## 1. 개요

| 확인할 것            | 도구                       | 옛 도구 (net-tools 등) |
|----------------------|----------------------------|------------------------|
| 인터페이스·주소·경로 | `ip`                       | `ifconfig`, `route`    |
| 열린 포트·연결       | `ss`                       | `netstat`              |
| DNS 응답             | `dig`                      | `nslookup`             |
| HTTP 응답·시간       | `curl`                     | -                      |
| 도달·경로·손실       | `ping`, `tracepath`, `mtr` | `traceroute`           |
| 원격 포트 열림       | `nmap`                     | `telnet`               |
| 패킷 내용            | `tcpdump` (함께 보기)      | -                      |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
# Ubuntu / Debian
sudo apt-get install -y iproute2 dnsutils curl mtr-tiny nmap iputils-ping iputils-tracepath

# RHEL 계열
sudo dnf install -y iproute bind-utils curl mtr nmap iputils
```

`ip`·`ss`(iproute2)와 `ping`은 대부분 기본 설치되어 있습니다. `dig`는 Debian 계열의 `dnsutils`(bind9-dnsutils), RHEL 계열의 `bind-utils` 패키지에 들어 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. ip

```bash
ip -br addr                    # 인터페이스별 상태·주소 한 줄 요약
ip -br link                    # 링크 상태와 MAC
ip route                       # 경로 표
ip route get 198.51.100.7      # 이 주소로 갈 때 쓰는 경로·출발 주소
ip neigh                       # ARP·이웃 표
ip -s link show eth0           # 송수신 바이트·오류·드롭 개수
```

```text
lo        UNKNOWN  127.0.0.1/8 ::1/128
eth0      UP       192.0.2.10/24 fe80::1/64
default via 192.0.2.1 dev eth0 proto static
```

`ip addr add`·`ip route add`로 바꾼 설정은 재부팅하면 사라집니다. 계속 쓸 설정은 netplan·NetworkManager·systemd-networkd 설정 파일에 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. ss

```bash
sudo ss -tlnp                  # 대기 중인 TCP 포트와 프로세스
sudo ss -ulnp                  # 대기 중인 UDP 포트
ss -tn state established       # 맺어진 TCP 연결
ss -tn dst 192.0.2.20          # 특정 상대와의 연결
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c   # TCP 상태별 개수
ss -s                          # 전체 요약
```

| 옵션      | 뜻                             |
|-----------|--------------------------------|
| `-t`·`-u` | TCP·UDP                        |
| `-l`      | 대기 중(LISTEN)만              |
| `-a`      | 모든 상태                      |
| `-n`      | 이름 대신 숫자 (빠름)          |
| `-p`      | 소켓을 연 프로세스 (root 필요) |

`127.0.0.1:포트`로 대기하면 그 서버 안에서만, `0.0.0.0:포트`나 `*:포트`면 모든 주소에서 접속을 받습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. dig

```bash
dig example.com                       # A 레코드 전체 응답
dig +short example.com                # 값만
dig example.com AAAA +short           # IPv6 주소
dig example.com MX +short             # 메일 서버
dig @1.1.1.1 example.com +short       # 특정 DNS 서버에 질의
dig -x 192.0.2.10 +short              # 역방향 (PTR)
dig example.com +trace                # 루트부터 위임 경로 추적
dig example.com +noall +answer        # 응답 부분만
```

| 응답에서 볼 것    | 뜻                                                       |
|-------------------|----------------------------------------------------------|
| `status: NOERROR` | 정상. `NXDOMAIN`은 이름 없음, `SERVFAIL`은 서버 오류     |
| `ANSWER SECTION`  | 레코드와 TTL                                             |
| `SERVER:`         | 실제로 응답한 DNS 서버 (systemd-resolved면 `127.0.0.53`) |
| `Query time`      | 응답 시간                                                |

[⬆ 목차로 돌아가기](#목차)

---

## 6. curl

```bash
curl -I https://example.com/                          # 응답 헤더만
curl -sS -o /dev/null -w '%{http_code}\n' https://example.com/   # 상태 코드만
curl -v https://example.com/ 2>&1 | grep -E '^(\*|<|>)' | head   # 연결·TLS·요청·응답 과정
curl --resolve example.com:443:192.0.2.10 https://example.com/   # DNS 대신 지정한 주소로 접속
curl -sS -o /dev/null -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} code=%{http_code}\n' https://example.com/
```

| `-w` 시간 변수       | 시작부터 이 시점까지                 |
|----------------------|--------------------------------------|
| `time_namelookup`    | DNS 조회 끝                          |
| `time_connect`       | TCP 연결 끝                          |
| `time_appconnect`    | TLS 연결 끝                          |
| `time_starttransfer` | 첫 바이트 받음 (서버 처리 시간 포함) |
| `time_total`         | 전체                                 |

`--resolve`는 DNS 변경 전에 새 서버를 시험하거나, 로드밸런서 뒤의 서버 한 대를 직접 시험할 때 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. ping·tracepath·mtr

```bash
ping -c 4 192.0.2.1             # 도달과 왕복 시간
tracepath -n 198.51.100.7       # 경로와 경로 MTU (root 불필요)
mtr -r -w -c 10 -n 198.51.100.7 # 경로상 구간별 손실·지연 보고
```

```text
HOST: server01         Loss%   Snt   Last   Avg  Best  Wrst StDev
  1.|-- 192.0.2.1        0.0%    10    0.4    0.5   0.3    0.9   0.2
  2.|-- 203.0.113.1      0.0%    10    2.1    2.3   1.9    3.0   0.3
  3.|-- 198.51.100.7     0.0%    10    5.2    5.4   5.0    6.1   0.3
```

중간 구간만 손실이 보이고 마지막 구간은 0%면, 그 장비가 ICMP 응답을 낮은 순위로 처리할 뿐 실제 손실이 아닐 수 있습니다. 손실은 마지막 구간까지 이어질 때 의미가 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. nmap

```bash
nmap -sT -p 22,80,443 192.0.2.10       # 지정 포트의 열림 확인 (TCP 연결 스캔, 권한 불필요)
nmap -sT -p- --min-rate 500 192.0.2.10 # 모든 TCP 포트
sudo nmap -sU -p 53,123 192.0.2.10     # UDP (root 필요, 느림)
nmap -sV -p 22,443 192.0.2.10          # 서비스·판 추정
```

| 상태       | 뜻                               |
|------------|----------------------------------|
| `open`     | 접속을 받음                      |
| `closed`   | 도달했지만 대기 중인 서비스 없음 |
| `filtered` | 방화벽 등이 막아 응답 없음       |

nmap은 자신이 관리하거나 허락받은 대상에만 씁니다. 다른 조직의 시스템을 검사하는 것은 정책·법률 위반이 될 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 점검 순서

"서비스에 접속이 안 된다"는 연락을 받았을 때 아래에서 위로 계층 순서대로 확인합니다.

| 단계 | 확인                     | 명령                                          |
|------|--------------------------|-----------------------------------------------|
| 1    | 인터페이스·주소          | `ip -br addr`                                 |
| 2    | 기본 경로                | `ip route`, `ip route get <대상>`             |
| 3    | 게이트웨이·대상 도달     | `ping -c 3 <게이트웨이>`, `ping -c 3 <대상>`  |
| 4    | DNS                      | `dig +short <이름>`, `dig @<다른 DNS> <이름>` |
| 5    | 서버에서 포트 대기       | (서버에서) `sudo ss -tlnp \| grep <포트>`     |
| 6    | 클라이언트에서 포트 도달 | `nmap -sT -p <포트> <대상>`                   |
| 7    | 응용 응답                | `curl -v`, `-w` 시간 측정                     |
| 8    | 경로 손실                | `mtr -r -c 10 <대상>`                         |

5에서 대기 중인데 6에서 `filtered`면 그 사이의 방화벽(서버의 nftables·클라우드 보안 그룹 등)을 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용 | 명령                                                                   | 기대 결과                        |
|------|-----------|------------------------------------------------------------------------|----------------------------------|
| 1    | 도구 설치 | `ip -V`, `dig -v`, `curl --version`, `mtr --version`, `nmap --version` | 판 번호                          |
| 2    | 주소·경로 | `ip -br addr`, `ip route`                                              | 의도한 주소와 기본 경로          |
| 3    | 대기 포트 | `sudo ss -tlnp`                                                        | 의도한 포트·주소·프로세스만 대기 |
| 4    | DNS       | `dig +short example.com`                                               | 주소 출력, `status: NOERROR`     |
| 5    | HTTP      | `curl -sS -o /dev/null -w '%{http_code}\n' https://example.com/`       | `200`                            |
| 6    | 포트 검사 | `nmap -sT -p 22 127.0.0.1`                                             | sshd가 있으면 `open`             |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

| 증상                                     | 원인                                           | 해결 방법                                       |
|------------------------------------------|------------------------------------------------|-------------------------------------------------|
| `ss -p`에 프로세스가 안 나옴             | 다른 사용자의 소켓                             | `sudo ss -tlnp`                                 |
| `dig`는 되는데 프로그램은 이름 해석 실패 | `/etc/hosts`·`nsswitch.conf` 순서, 검색 도메인 | `getent hosts <이름>`으로 시스템 해석 결과 확인 |
| `ping`은 안 되는데 `curl`은 됨           | ICMP 차단                                      | TCP 기준으로 판단 (`nmap -sT`, `curl`)          |
| mtr 중간 구간만 손실                     | 장비의 ICMP 응답 제한                          | 마지막 구간 손실 여부로 판단 (7절)              |
| `ifconfig`·`netstat` 명령 없음           | net-tools 미설치 (기본 제외)                   | `ip`·`ss` 사용                                  |
| curl `SSL certificate problem`           | 인증서 체인·이름 불일치, 시간 오차             | `curl -v`로 인증서 확인, 서버 시간 확인         |
| nmap 결과가 전부 `filtered`              | 중간 방화벽이 응답을 버림                      | 서버 쪽 `ss`, 방화벽 규칙, 보안 그룹 확인       |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [tcpdump](./tcpdump.md) — 패킷 단위 확인
- [iperf3](./iperf3_guide.md) — 대역폭·손실·지터 측정
- [netfilter·tc](./netfilter_tc.md) — 서버 방화벽과 트래픽 제어
- [Windows 네트워크 진단](../windows/windows_network_diagnostics.md) — Windows에서 같은 점검
- [IPv4 주소 체계](../networking/ipv4_addressing_guide.md) — CIDR, 서브넷

---

## 참고 자료

- Linux Foundation: [iproute2](https://wiki.linuxfoundation.org/networking/iproute2) — ★★★☆☆
- Linux man-pages: [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html) · [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html) — ★★★☆☆
- ISC: [BIND 9 Downloads](https://www.isc.org/download/) — ★★★☆☆
- curl: [curl man page](https://curl.se/docs/manpage.html) — ★★★☆☆
- mtr: [traviscross/mtr](https://github.com/traviscross/mtr) — ★★★☆☆
- Nmap: [Nmap Reference Guide](https://nmap.org/book/man.html) — ★★★☆☆

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
