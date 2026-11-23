---
name: ufw-firewalld-official-notes
description: Linux 호스트 방화벽 관리 도구 ufw(Ubuntu)와 firewalld(RHEL 계열)의 판, 기본 개념, 명령의 공식 출처 기준 사실 정리.
tags:
  - firewall
  - ufw
  - firewalld
  - security
last_checked: 2026-11-23
sources:
  - https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html
  - https://firewalld.org/documentation/
  - https://github.com/firewalld/firewalld/releases
---

# ufw·firewalld 공식 참조 노트

| 항목                  | 값                                                                                                                                                              | 출처                              |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| ufw 판 (Ubuntu 24.04) | 0.36.2                                                                                                                                                          | 컨테이너 `ufw version`            |
| ufw 기본 명령         | `ufw default deny incoming`, `ufw allow 22/tcp`, `ufw allow from <대역> to any port <포트> proto tcp`, `ufw enable`, `ufw status numbered`, `ufw delete <번호>` | ufw(8), 컨테이너                  |
| firewalld 최신 판     | 2.5.2 (2026-09-17). Rocky 10 패키지는 2.4.3                                                                                                                     | releases, 컨테이너                |
| firewalld 개념        | zone(신뢰 수준별 규칙 묶음), service(포트 묶음 이름), runtime과 permanent 설정 구분                                                                             | firewalld documentation           |
| firewalld 명령        | `firewall-cmd --add-service=http --permanent`, `--reload`, `--list-all`, 데몬 없이 `firewall-offline-cmd`                                                       | firewalld documentation, 컨테이너 |
| 기본 zone (Rocky 10)  | `public` (기본 허용 서비스: cockpit, dhcpv6-client, ssh)                                                                                                        | 컨테이너                          |

검증: 1차 ufw(8) man 페이지와 firewalld 문서·release, 2차 `ubuntu:24.04`(NET_ADMIN 권한)에서 ufw 규칙·활성화, `rockylinux/rockylinux:10`에서 `firewall-offline-cmd`를 실행해 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
