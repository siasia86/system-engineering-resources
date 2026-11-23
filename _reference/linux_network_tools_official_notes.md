---
name: linux-network-tools-official-notes
description: Linux 네트워크 점검 도구(iproute2 ip·ss, dig, curl, mtr, nmap, tracepath)의 판과 핵심 옵션의 공식 출처 기준 사실 정리.
tags:
  - linux
  - network
  - iproute2
  - dig
  - curl
last_checked: 2026-11-23
sources:
  - https://wiki.linuxfoundation.org/networking/iproute2
  - https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/
  - https://man7.org/linux/man-pages/man8/ip.8.html
  - https://man7.org/linux/man-pages/man8/ss.8.html
  - https://www.isc.org/download/
  - https://curl.se/docs/manpage.html
  - https://github.com/traviscross/mtr
  - https://nmap.org/book/man.html
---

# Linux 네트워크 도구 공식 참조 노트

## 1. 공식 소스

| 소스           | URL                                                           | 용도                    |
|----------------|---------------------------------------------------------------|-------------------------|
| iproute2       | https://wiki.linuxfoundation.org/networking/iproute2          | ip·ss 프로젝트          |
| iproute2 배포  | https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/ | 최신 판                 |
| ip(8)·ss(8)    | https://man7.org/linux/man-pages/man8/ip.8.html, ss.8.html    | 옵션                    |
| BIND 9 (dig)   | https://www.isc.org/download/                                 | dig가 들어 있는 BIND 판 |
| curl manpage   | https://curl.se/docs/manpage.html                             | `-w` 변수, 옵션         |
| mtr            | https://github.com/traviscross/mtr                            | 판, 보고 모드           |
| Nmap Reference | https://nmap.org/book/man.html                                | 스캔 종류               |

## 2. 검증된 사실 (2026-11-23)

| 항목               | 값                                                                                              | 출처              |
|--------------------|-------------------------------------------------------------------------------------------------|-------------------|
| iproute2 최신 판   | 7.3.0                                                                                           | kernel.org 배포   |
| BIND 9 판          | 안정 9.20.31, 개발 9.21.28 (`dig`는 bind9-dnsutils 등에 포함)                                   | isc.org           |
| curl 최신 판       | 8.23.0 (2026-10-14)                                                                             | curl releases     |
| mtr 최신 태그      | v0.96                                                                                           | mtr 저장소        |
| Nmap 최신 안정판   | 7.993                                                                                           | nmap.org download |
| ip 요약 출력       | `-br`(brief)로 인터페이스·주소를 한 줄씩                                                        | ip(8)             |
| ss 주요 옵션       | `-t` TCP, `-u` UDP, `-l` 대기 중, `-n` 숫자 그대로, `-p` 프로세스, `-s` 요약                    | ss(8)             |
| curl 시간 측정     | `-w`의 `time_namelookup`, `time_connect`, `time_appconnect`, `time_starttransfer`, `time_total` | curl manpage      |
| mtr 보고 모드      | `-r` 보고, `-w` 넓은 출력, `-c` 횟수, `-n` 이름 해석 안 함                                      | mtr(8)            |
| nmap TCP 연결 스캔 | `-sT`(권한 없이 가능한 connect 스캔), `-p` 포트 지정                                            | Nmap Reference    |
| 옛 도구            | `ifconfig`·`netstat`·`route`(net-tools)는 `ip`·`ss`로 대체                                      | iproute2          |

## 3. 검증 기록

- 1차: 각 프로젝트의 배포처·release·man 페이지에서 판과 옵션을 확인했습니다.
- 2차: Ubuntu 24.04의 iproute2 6.1.0, dig 9.18.39, curl 8.5.0, mtr 0.95, nmap 7.94SVN에서 명령을 실행해 출력을 대조했습니다(nmap은 자기 호스트 127.0.0.1만 검사).

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
