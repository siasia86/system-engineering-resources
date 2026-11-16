# DNS 이름 해석 원리와 장애 진단

DNS(Domain Name System)가 이름을 주소로 바꾸는 과정과 캐시·TTL·전송 방식을 정리하고, `dig`·`resolvectl`로 장애 위치를 좁히는 순서를 다룹니다. 헤더 구조는 [network_headers.md](./network_headers.md), 응답 코드 목록은 [error_codes.md](./error_codes.md)를 함께 보면 됩니다.

## 목차

| 섹션                                                                                                                                         |
|----------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 구성 요소와 역할](#1-구성-요소와-역할) / [2. 이름 해석 흐름](#2-이름-해석-흐름) / [3. 주요 레코드 타입](#3-주요-레코드-타입)             |
| [4. TTL과 캐시](#4-ttl과-캐시) / [5. 전송 방식 UDP·TCP·EDNS](#5-전송-방식-udptcpedns) / [6. Linux 클라이언트 설정](#6-linux-클라이언트-설정) |
| [7. dig로 진단하기](#7-dig로-진단하기) / [8. 증상별 진단 순서](#8-증상별-진단-순서) / [9. 변경 작업 점검표](#9-변경-작업-점검표)             |

---

## 1. 구성 요소와 역할

DNS는 하나의 서버가 아니라 역할이 다른 여러 구성 요소가 나누어 일하는 분산 데이터베이스입니다.

| 구성 요소                        | 역할                                                                 | 예                                        |
|----------------------------------|----------------------------------------------------------------------|-------------------------------------------|
| Stub resolver (스텁 리졸버)      | 애플리케이션 대신 질의를 보내는 OS 라이브러리. 재귀 해석은 하지 않음 | glibc `getaddrinfo()`, Windows DNS Client |
| Recursive resolver (재귀 리졸버) | 루트부터 차례로 물어 최종 답을 찾고 캐시함                           | Unbound, BIND, 공용 리졸버                |
| Forwarder (전달자)               | 직접 재귀하지 않고 다른 리졸버로 질의를 넘김                         | systemd-resolved, dnsmasq                 |
| Authoritative server (권한 서버) | 자기 영역(zone)의 원본 데이터를 답함. 응답에 AA 비트를 켬            | 도메인의 NS 레코드가 가리키는 서버        |
| Root / TLD server                | 다음 단계 권한 서버를 알려 줌(위임, referral)                        | `.` 루트, `com.` TLD                      |

용어 정리:

- **Zone(영역)**: 한 관리 주체가 원본을 갖는 이름 공간의 단위입니다. `example.com` zone이 `dev.example.com`을 다른 서버에 위임하면 그 하위는 별도 zone이 됩니다.
- **Delegation(위임)**: 상위 zone이 하위 zone의 NS 레코드를 실어 "이 이름은 저 서버에 물어보라"고 알려 주는 것입니다.
- **Glue record**: 위임받은 NS의 이름이 그 하위 zone 안에 있을 때(예: `ns1.example.com`), 상위 zone이 함께 주는 A/AAAA 레코드입니다. 없으면 순환 참조가 생깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 이름 해석 흐름

캐시가 비어 있을 때 `www.example.com`의 A 레코드를 찾는 과정입니다.

```text
App --getaddrinfo()--> Stub resolver
                          |
                          | (1) query www.example.com A, RD=1
                          v
                    Recursive resolver --(2)--> Root server     : referral to com. NS
                          |            --(3)--> com. TLD server : referral to example.com NS (+glue)
                          |            --(4)--> example.com NS  : answer A 192.0.2.10 (AA=1)
                          |
                          | (5) answer + cache for TTL
                          v
                     Stub resolver --> App
```

| 단계 | 핵심                                                                            |
|------|---------------------------------------------------------------------------------|
| (1)  | 스텁 리졸버는 RD(Recursion Desired) 비트를 켜고 설정된 리졸버 하나에 묻습니다   |
| (2)  | 재귀 리졸버는 내장 root hints로 루트 서버를 찾고 `com.` 위임을 받습니다         |
| (3)  | TLD 서버는 `example.com`의 NS와 glue를 돌려줍니다                               |
| (4)  | 권한 서버가 최종 답을 주며 AA(Authoritative Answer) 비트를 켭니다               |
| (5)  | 재귀 리졸버는 각 레코드를 TTL 동안 캐시하고, 다음 질의는 캐시에서 바로 답합니다 |

이름 해석 전에 OS는 `/etc/hosts`나 Windows `hosts` 파일을 먼저 볼 수 있습니다. Linux에서 순서는 `/etc/nsswitch.conf`의 `hosts:` 줄이 정합니다. 그래서 `dig`(DNS만 질의)와 `getent hosts`(OS 해석 경로 전체)의 결과가 다를 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 주요 레코드 타입

| 타입  | 번호 | 용도                                        | 운영 주의                                                         |
|-------|------|---------------------------------------------|-------------------------------------------------------------------|
| A     | 1    | 이름 → IPv4 주소                            | 여러 개를 두면 클라이언트가 순서를 바꿔 가며 사용할 수 있음       |
| AAAA  | 28   | 이름 → IPv6 주소                            | IPv6 경로가 깨져 있으면 연결 지연의 원인이 됨                     |
| CNAME | 5    | 별칭 → 정식 이름                            | 같은 이름에 다른 레코드와 함께 둘 수 없음. zone apex에 못 둠      |
| NS    | 2    | zone의 권한 서버                            | 상위 zone의 위임 NS와 하위 zone의 NS가 일치해야 함                |
| SOA   | 6    | zone 시작 정보(serial, refresh, minimum 등) | serial을 올리지 않으면 secondary가 갱신하지 않음                  |
| MX    | 15   | 메일 수신 서버와 우선순위                   | 대상은 CNAME이 아닌 A/AAAA를 가진 이름이어야 함                   |
| TXT   | 16   | 임의 문자열(SPF, 도메인 소유 확인 등)       | 255바이트 문자열 여러 개로 나뉠 수 있음                           |
| PTR   | 12   | IP → 이름(역방향)                           | 역방향 zone은 IP 대역 소유자(ISP·클라우드)가 관리하는 경우가 많음 |
| SRV   | 33   | 서비스 위치(우선순위·가중치·포트·대상)      | `_service._proto.name` 형식                                       |
| CAA   | 257  | 인증서를 발급할 수 있는 CA 지정             | 잘못 넣으면 인증서 갱신이 실패함                                  |

레코드 타입 번호는 IANA DNS Parameters 레지스트리에서 확인할 수 있습니다. 이름 길이 제한은 RFC 1035 기준으로 label 63옥텟, 전체 이름 255옥텟입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. TTL과 캐시

TTL(Time To Live)은 리졸버가 레코드를 캐시해도 되는 초 단위 시간입니다. 캐시된 답의 TTL은 시간이 지날수록 줄어들어 0이 되면 다시 묻습니다.

### 4.1 양성 캐시와 음성 캐시

| 구분                      | 내용                                                                                                |
|---------------------------|-----------------------------------------------------------------------------------------------------|
| 양성 캐시                 | 찾은 레코드를 그 레코드의 TTL 동안 보관                                                             |
| 음성 캐시(negative cache) | "없다"는 답도 캐시. TTL은 응답 authority 절에 실린 SOA의 TTL과 SOA MINIMUM 중 작은 값(RFC 2308 5절) |
| NXDOMAIN                  | 이름 자체가 없음(RCODE 3)                                                                           |
| NODATA                    | 이름은 있으나 요청한 타입의 레코드가 없음. 별도 RCODE가 없고 NOERROR + 빈 answer로 판단             |

RFC 2308은 리졸버 쪽 음성 캐시 상한으로 1~3시간이 잘 동작했고 하루를 넘는 값은 문제가 있었다고 적습니다. 새 이름을 만들기 전에 누군가 그 이름을 조회했다면, 음성 캐시가 만료될 때까지 "없음"이 보일 수 있습니다.

### 4.2 TTL 운영 판단 기준

| 상황                           | 권장 행동                                                                                    |
|--------------------------------|----------------------------------------------------------------------------------------------|
| IP 변경·이전이 예정됨          | 변경 전에 TTL을 낮추고, 기존 TTL만큼 기다린 뒤 실제 값을 바꿈                                |
| 변경 완료 후 안정화            | TTL을 다시 올려 질의량과 권한 서버 의존도를 줄임                                             |
| 장애 조치(failover)를 DNS로 함 | 짧은 TTL이 필요하지만, 일부 클라이언트·런타임이 TTL을 따르지 않고 오래 캐시할 수 있음을 고려 |
| NS 레코드 변경                 | 상위 zone(레지스트리)의 위임 TTL이 길 수 있으므로 이전 NS를 일정 기간 함께 운영              |

🟡 주의: TTL을 낮추는 변경 자체도 기존 TTL이 지나야 퍼집니다. 3600초 TTL 레코드를 바꾸기 직전에 TTL을 60초로 낮추면, 이미 캐시한 리졸버는 여전히 최대 3600초 동안 옛 값을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 전송 방식 UDP·TCP·EDNS

| 항목           | 내용                                                                                                       |
|----------------|------------------------------------------------------------------------------------------------------------|
| 기본 포트      | UDP/TCP 53                                                                                                 |
| UDP 512바이트  | RFC 1035의 원래 UDP 메시지 상한. 넘으면 TC(Truncated) 비트를 켜고 잘린 응답을 보냄                         |
| TCP 재시도     | TC=1을 받은 클라이언트는 TCP로 다시 질의. RFC 7766은 일반 DNS 구현이 UDP와 TCP를 모두 지원해야 한다고 정함 |
| EDNS(0)        | RFC 6891. OPT 의사 레코드로 더 큰 UDP 버퍼 크기, DNSSEC OK(DO) 비트 등을 알림                              |
| 권장 버퍼 1232 | DNS Flag Day 2020 권고. IPv6 최소 MTU 1280에서 IPv6·UDP 헤더 48바이트를 뺀 값으로 단편화를 피하기 위함     |

진단에서 의미:

- 방화벽이 TCP 53을 막으면 작은 응답은 성공하고 큰 응답(DNSSEC, TXT가 많은 이름, 레코드가 많은 이름)만 실패합니다.
- UDP 단편화가 경로에서 버려지면 EDNS 버퍼를 크게 잡은 질의만 시간 초과됩니다. MTU 문제는 [mtu_mss_pmtud.md](./mtu_mss_pmtud.md)를 봅니다.

```bash
# TCP로만 질의해 TCP 53 경로를 확인
dig +tcp example.com A @192.0.2.53

# EDNS 버퍼를 줄이거나 끄고 차이를 비교
dig +bufsize=1232 example.com TXT @192.0.2.53
dig +noedns example.com A @192.0.2.53
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Linux 클라이언트 설정

### 6.1 /etc/resolv.conf

| 지시자 / 옵션            | 의미                                           | 기본값·상한 (resolv.conf(5))  |
|--------------------------|------------------------------------------------|-------------------------------|
| `nameserver`             | 질의할 리졸버 주소                             | 최대 3개(MAXNS)               |
| `search`                 | 짧은 이름 뒤에 붙여 볼 도메인 목록             | glibc 2.26부터 개수 제한 없음 |
| `options ndots:n`        | 점이 n개 미만인 이름은 search 목록을 먼저 붙임 | 기본 1, 상한 15               |
| `options timeout:n`      | 서버 하나의 응답 대기 시간(초)                 | 기본 5, 상한 30               |
| `options attempts:n`     | 서버 목록 전체를 다시 도는 횟수                | 기본 2, 상한 5                |
| `options rotate`         | nameserver를 돌아가며 사용                     | 기본 꺼짐                     |
| `options edns0`          | EDNS 사용                                      | glibc 2.6부터                 |
| `options single-request` | A와 AAAA 질의를 순차로 보냄                    | glibc 2.10부터                |
| `options use-vc`         | TCP로 질의                                     | glibc 2.14부터                |

첫 nameserver가 응답하지 않으면 `timeout`만큼 기다린 뒤 다음 서버로 넘어갑니다. 기본값이면 첫 서버 장애 하나로 이름 해석마다 수 초씩 늦어질 수 있습니다.

`ndots`가 크면(Kubernetes Pod 기본 `ndots:5` 등) 외부 이름 하나에 search 도메인 수만큼 실패 질의가 먼저 나갑니다. 자주 쓰는 외부 이름은 끝에 점을 붙인 FQDN(`api.example.com.`)으로 쓰면 search를 건너뜁니다.

### 6.2 systemd-resolved

systemd-resolved를 쓰는 배포판은 `/etc/resolv.conf`가 `127.0.0.53`을 가리키는 stub 파일인 경우가 많습니다. 실제 상위 리졸버는 아래로 확인합니다.

```bash
ls -l /etc/resolv.conf          # 어떤 파일로 링크되어 있는지
resolvectl status               # 링크별 DNS 서버, search 도메인
resolvectl query example.com    # resolved 경로로 해석
resolvectl statistics           # 캐시 적중 등 통계
sudo resolvectl flush-caches    # resolved 캐시 비우기
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. dig로 진단하기

`dig`는 BIND 배포에 포함된 질의 도구이며 `/etc/hosts`를 보지 않고 DNS만 질의합니다.

### 7.1 자주 쓰는 형식

```bash
dig example.com                    # 기본 A 질의, resolv.conf의 서버 사용
dig example.com AAAA +short        # 값만 출력
dig @192.0.2.53 example.com MX     # 특정 서버에 질의
dig -x 192.0.2.10                  # 역방향(PTR) 질의
dig example.com +trace             # 루트부터 위임을 직접 따라감(로컬 캐시 우회)
dig example.com NS +norecurse @ns1.example.com   # 권한 서버에 비재귀 질의
dig example.com SOA +multiline     # SOA 필드를 읽기 쉽게
dig example.com +dnssec            # DO 비트를 켜고 RRSIG 함께 받기
```

### 7.2 출력에서 볼 곳

```text
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; ANSWER SECTION:
example.com.        2875    IN  A   192.0.2.10

;; Query time: 12 msec
;; SERVER: 192.0.2.53#53(192.0.2.53) (UDP)
```

| 위치         | 확인할 것                                                             |
|--------------|-----------------------------------------------------------------------|
| `status`     | NOERROR, NXDOMAIN, SERVFAIL, REFUSED 중 무엇인지                      |
| `flags`      | `aa` 있으면 권한 서버의 답, `ra` 없으면 그 서버가 재귀를 해 주지 않음 |
| ANSWER 개수  | NOERROR인데 0이면 NODATA                                              |
| TTL 열       | 캐시에서 나온 답이면 질의할 때마다 줄어듦                             |
| `Query time` | 수백 ms 이상이면 상위 재귀가 느리거나 캐시 미스                       |
| `SERVER`     | 실제로 답한 서버가 의도한 서버인지                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 증상별 진단 순서

### 8.1 계층별로 좁히기

```text
[1] getent hosts NAME        -> OS path (hosts file + DNS)
[2] dig NAME                 -> default resolver only
[3] dig @OTHER_RESOLVER NAME -> is it this resolver's problem?
[4] dig NAME +trace          -> delegation chain from root
[5] dig @AUTH_NS NAME +norecurse -> authoritative data itself
```

1에서 실패하고 2에서 성공하면 `/etc/hosts`나 `nsswitch.conf`, 애플리케이션 캐시를 봅니다. 2에서 실패하고 3에서 성공하면 기본 리졸버 문제입니다. 4와 5에서 실패하면 zone 데이터나 위임 문제입니다.

### 8.2 증상과 원인 후보

| 증상                            | 원인 후보                                             | 확인 명령                                      |
|---------------------------------|-------------------------------------------------------|------------------------------------------------|
| NXDOMAIN인데 레코드를 방금 만듦 | 음성 캐시, 다른 zone에 만듦, 위임 불일치              | `dig NAME SOA`, `dig NAME +trace`              |
| SERVFAIL                        | 권한 서버 무응답, DNSSEC 검증 실패, lame delegation   | `dig NAME +cd`(검증 끄고 비교), `+trace`       |
| 일부 리졸버만 옛 값             | TTL이 남은 캐시                                       | 각 리졸버에 `dig`, TTL 열 비교                 |
| 첫 연결만 5초 늦음              | 첫 nameserver 무응답, AAAA 질의 지연                  | `strace -e trace=network`, `resolvectl status` |
| 큰 응답만 실패                  | TCP 53 차단, UDP 단편 손실                            | `dig +tcp`, `dig +bufsize=1232`                |
| 내부 이름이 외부 이름으로 풀림  | search 도메인과 ndots, split-horizon 설정             | `dig NAME.`(끝 점), `resolv.conf` 확인         |
| REFUSED                         | 그 서버가 해당 클라이언트의 재귀 질의를 허용하지 않음 | 허용 대역(ACL) 설정 확인                       |

용어:

- **Lame delegation**: 상위 zone이 NS로 지정한 서버가 그 zone에 권한 답을 주지 않는 상태입니다.
- **Split-horizon(분할 DNS)**: 같은 이름에 질의자 위치(내부·외부)에 따라 다른 답을 주는 구성입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 변경 작업 점검표

| 단계    | 점검 항목                                                      |
|---------|----------------------------------------------------------------|
| 변경 전 | 현재 값과 TTL 기록(`dig NAME +noall +answer`)                  |
| 변경 전 | 이전이면 TTL을 미리 낮추고 기존 TTL 이상 대기                  |
| 변경 전 | 권한 서버 전체(NS 모두)에 같은 SOA serial이 보이는지           |
| 변경    | zone 파일 문법 검사(BIND는 `named-checkzone`), serial 증가     |
| 변경 후 | 각 권한 서버에 `+norecurse`로 새 값 확인                       |
| 변경 후 | 주요 리졸버(사내·공용)에서 새 값 확인, 옛 값이면 남은 TTL 기록 |
| 변경 후 | CNAME·MX·CAA 등 연관 레코드와 인증서 갱신 경로 영향 확인       |
| 안정화  | TTL 원복, 이전 대상 서버는 옛 TTL이 모두 지난 뒤 정리          |

```bash
# 모든 권한 서버의 SOA serial 비교
for ns in $(dig +short example.com NS); do
  printf '%s ' "$ns"; dig +short @"$ns" example.com SOA | awk '{print $3}'
done
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [RFC 1034 — Domain Names: Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034) — ★★★★☆ (확인일 2026-11-16)
- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035) — ★★★★☆ (확인일 2026-11-16)
- [RFC 2308 — Negative Caching of DNS Queries](https://www.rfc-editor.org/rfc/rfc2308) — ★★★★☆ (확인일 2026-11-16)
- [RFC 6891 — Extension Mechanisms for DNS (EDNS(0))](https://www.rfc-editor.org/rfc/rfc6891) — ★★★★☆ (확인일 2026-11-16)
- [RFC 7766 — DNS Transport over TCP](https://www.rfc-editor.org/rfc/rfc7766) — ★★★★☆ (확인일 2026-11-16)
- [DNS Flag Day 2020](https://www.dnsflagday.net/2020/) — ★★★☆☆ (확인일 2026-11-16)
- [IANA Domain Name System (DNS) Parameters](https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml) — ★★★☆☆ (확인일 2026-11-16)
- [resolv.conf(5) — Linux manual page](https://man7.org/linux/man-pages/man5/resolv.conf.5.html) — ★★★☆☆ (확인일 2026-11-16)
- [resolvectl(1) — systemd](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html) — ★★★☆☆ (확인일 2026-11-16)
- [BIND 9 Administrator Reference Manual — dig](https://bind9.readthedocs.io/en/latest/manpages.html) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
