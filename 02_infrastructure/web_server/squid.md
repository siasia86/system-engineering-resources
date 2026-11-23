# Squid (전달 프록시)
<!-- reference: _reference/squid_official_notes.md -->

내부 서버·PC가 외부 웹에 나갈 때 거쳐 가는 전달(forward) 프록시입니다. 외부 접속을 한곳으로 모아 허용 대상만 내보내고 접속 기록을 남길 때 씁니다. 이 문서만으로 설치 → 접근 제어 설정 → 클라이언트 설정 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Squid 7.8 (2026-11-23 확인)
- 예제 시험: 2026-11-23, `ubuntu/squid` 컨테이너(6.13)에서 3절 설정과 6절 1~3번을 실행해 확인

## 목차

| 섹션                                                                               |
|------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 기본 설정](#3-기본-설정)             |
| [4. 클라이언트 설정](#4-클라이언트-설정) / [5. 운영](#5-운영) / [6. 검증](#6-검증) |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료) |

---

## 1. 개요

| 구분           | 전달 프록시 (이 문서)          | 리버스 프록시           |
|----------------|--------------------------------|-------------------------|
| 누구 앞에 있나 | 내부 클라이언트 앞 (나가는 길) | 서버 앞 (들어오는 길)   |
| 목적           | 외부 접속 통제·기록·캐시       | 부하 분산·TLS 종료·보호 |
| 예             | Squid                          | Nginx, HAProxy, Caddy   |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
sudo apt-get install -y squid        # Ubuntu / Debian
sudo dnf install -y squid            # RHEL 계열
squid -v | head -1
sudo systemctl enable --now squid
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 설정

`/etc/squid/squid.conf`의 핵심 부분입니다. `http_access`는 위에서부터 처음 맞는 규칙이 적용됩니다.

```text
http_port 3128

acl localnet src 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
acl SSL_ports port 443
acl Safe_ports port 80 443

http_access deny !Safe_ports           # 80·443 외 포트로 나가지 못하게
http_access deny CONNECT !SSL_ports    # HTTPS 터널은 443만
http_access allow localnet             # 내부망만 허용
http_access deny all                   # 나머지 거부 (마지막에 둠)
```

허용 도메인만 내보내려면 `allow localnet` 앞에 도메인 목록을 둡니다.

```text
acl allowed_sites dstdomain .ubuntu.com .github.com
http_access deny !allowed_sites
```

```bash
sudo squid -k parse          # 문법 검사
sudo squid -k reconfigure    # 무중단 반영
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 클라이언트 설정

```bash
export http_proxy=http://proxy.example.com:3128
export https_proxy=http://proxy.example.com:3128
export no_proxy=localhost,127.0.0.1,.internal.example
curl -sI https://example.com/        # 프록시를 거쳐 응답
```

apt는 `/etc/apt/apt.conf.d/95proxy`에 `Acquire::http::Proxy "http://proxy.example.com:3128";`, dnf는 `/etc/dnf/dnf.conf`에 `proxy=http://proxy.example.com:3128`를 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 운영

| 항목      | 내용                                                              |
|-----------|-------------------------------------------------------------------|
| 접근 기록 | `/var/log/squid/access.log` (클라이언트, 대상, 결과 코드)         |
| 포트 노출 | 3128은 내부망에만 열고 인터넷에 열지 않음 (열린 프록시 악용 방지) |
| HTTPS     | 기본은 CONNECT 터널이라 내용은 보지 않고 대상 호스트만 기록       |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용 | 명령                                                                   | 기대 결과                |
|------|-----------|------------------------------------------------------------------------|--------------------------|
| 1    | 판        | `squid -v`                                                             | 판 번호                  |
| 2    | 설정 문법 | `squid -k parse`                                                       | 오류 없음                |
| 3    | 허용 요청 | 내부 클라이언트에서 `curl -x http://<프록시>:3128 http://example.com/` | `200`                    |
| 4    | 거부 요청 | 허용 목록 밖 도메인으로 같은 요청                                      | `403`                    |
| 5    | 외부 노출 | 외부에서 `nmap -sT -p 3128 <프록시 공인 주소>`                         | `filtered` 또는 `closed` |
| 6    | 기록      | `tail /var/log/squid/access.log`                                       | 요청 기록                |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                       | 원인                                 | 해결 방법                                      |
|----------------------------|--------------------------------------|------------------------------------------------|
| 모든 요청 403              | `deny all`이 허용 규칙보다 위에 있음 | 규칙 순서 확인 (3절)                           |
| HTTPS만 실패               | CONNECT 포트 제한                    | `SSL_ports`에 필요한 포트 포함 여부 확인       |
| 일부 명령만 프록시를 안 씀 | 프로그램마다 프록시 설정 방식이 다름 | 환경 변수 대소문자(`HTTPS_PROXY`), 도구별 설정 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Varnish](./varnish.md) — 서버 앞단 캐시
- [Nginx 설치](./nginx_install.md) — 리버스 프록시
- [Linux 네트워크 점검 도구](../../01_fundamentals/linux/linux_network_tools.md) — curl·nmap 점검

---

## 참고 자료

- Squid: [http_access](https://www.squid-cache.org/Doc/config/http_access/) · [acl](https://www.squid-cache.org/Doc/config/acl/) — ★★★☆☆
- GitHub: [squid-cache/squid releases](https://github.com/squid-cache/squid/releases) — 7.8 확인 2026-11-23 — ★★★☆☆

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
