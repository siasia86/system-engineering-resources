# ufw·firewalld (호스트 방화벽 관리)
<!-- reference: _reference/ufw_firewalld_official_notes.md -->

Linux 커널 방화벽(nftables·iptables)을 쉬운 명령으로 다루는 관리 도구입니다. Ubuntu는 ufw, RHEL 계열은 firewalld를 기본으로 씁니다. 이 문서만으로 기본 정책 → 포트·출발지 허용 → 영구 적용 → 검증까지 따라 할 수 있게 썼습니다. 규칙의 바탕인 nftables·iptables는 함께 보기 문서에 있습니다.

- 기준 판: ufw 0.36.2(Ubuntu 24.04), firewalld 2.5.2(최신)·2.4.3(Rocky 10)
- 예제 시험: 2026-11-23, `ubuntu:24.04` 컨테이너(NET_ADMIN 권한)에서 ufw 규칙·활성화, `rockylinux/rockylinux:10` 컨테이너에서 `firewall-offline-cmd`로 firewalld 설정을 확인. 실제 서버의 원격 접속 상태에서는 시험하지 않았음

## 목차

| 섹션                                                                                 |
|--------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 시작 전 주의](#2-시작-전-주의) / [3. ufw](#3-ufw)           |
| [4. firewalld](#4-firewalld) / [5. 명령 대응표](#5-명령-대응표) / [6. 검증](#6-검증) |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)   |

---

## 1. 개요

| 항목        | ufw                             | firewalld                                 |
|-------------|---------------------------------|-------------------------------------------|
| 기본 배포판 | Ubuntu                          | RHEL·Rocky·Alma, Fedora, SUSE             |
| 개념        | 기본 정책 + 허용·거부 규칙 목록 | zone(신뢰 수준) + service(포트 묶음)      |
| 적용        | 명령 즉시 적용·저장             | runtime(즉시)과 permanent(재부팅 후) 구분 |
| 바탕        | nftables·iptables               | nftables                                  |

한 서버에서 두 도구를 함께 켜지 않습니다. 규칙이 서로 덮어써 예상과 다르게 동작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 시작 전 주의

원격(SSH)으로 작업할 때 SSH 허용 규칙보다 기본 거부를 먼저 켜면 접속이 끊깁니다.

1. SSH 포트 허용 규칙을 먼저 넣습니다.
2. 콘솔 접속 수단(클라우드 콘솔, IPMI)을 확인해 둡니다.
3. 활성화한 뒤 새 SSH 세션을 열어 접속되는지 확인하고, 기존 세션은 닫지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. ufw

```bash
sudo apt-get install -y ufw
sudo ufw default deny incoming          # 들어오는 연결 기본 거부
sudo ufw default allow outgoing         # 나가는 연결 기본 허용
sudo ufw allow 22/tcp                   # SSH (가장 먼저)
sudo ufw allow 80,443/tcp               # 웹
sudo ufw allow from 192.0.2.0/24 to any port 5432 proto tcp   # DB는 특정 대역만
sudo ufw enable
sudo ufw status numbered
sudo ufw delete 3                       # 3번 규칙 삭제
sudo ufw logging on                     # 차단 기록 (/var/log/ufw.log)
```

```text
     To                         Action      From
[ 1] 22/tcp                     ALLOW IN    Anywhere
[ 2] 5432/tcp                   ALLOW IN    192.0.2.0/24
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. firewalld

```bash
sudo dnf install -y firewalld
sudo systemctl enable --now firewalld
firewall-cmd --get-default-zone                          # public
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --zone=public --add-port=8080/tcp --permanent
sudo firewall-cmd --zone=public --add-rich-rule='rule family=ipv4 source address=192.0.2.0/24 port port=5432 protocol=tcp accept' --permanent
sudo firewall-cmd --reload                               # permanent 설정을 runtime에 반영
sudo firewall-cmd --zone=public --list-all
```

| 개념          | 설명                                                                                      |
|---------------|-------------------------------------------------------------------------------------------|
| zone          | `public`, `internal`, `trusted` 등 신뢰 수준별 규칙 묶음. 인터페이스·출발지를 zone에 연결 |
| service       | `http`, `ssh`처럼 포트를 이름으로 묶은 것 (`firewall-cmd --get-services`)                 |
| `--permanent` | 붙이면 설정 파일에 저장(재부팅 후 유지), `--reload` 전까지 runtime엔 없음                 |
| rich rule     | 출발지·포트·동작을 함께 지정하는 세밀한 규칙                                              |

`--permanent` 없이 넣은 규칙은 즉시 적용되지만 재시작하면 사라집니다. 시험할 때는 runtime으로 넣고, 확인한 뒤 `--runtime-to-permanent`로 저장할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 명령 대응표

| 작업             | ufw                           | firewalld                                       |
|------------------|-------------------------------|-------------------------------------------------|
| 상태             | `ufw status verbose`          | `firewall-cmd --state`, `--list-all`            |
| 포트 허용        | `ufw allow 8080/tcp`          | `firewall-cmd --add-port=8080/tcp --permanent`  |
| 서비스 허용      | `ufw allow OpenSSH`           | `firewall-cmd --add-service=ssh --permanent`    |
| 특정 출발지 허용 | `ufw allow from 192.0.2.0/24` | rich rule 또는 `--zone=trusted --add-source=`   |
| 규칙 삭제        | `ufw delete <번호>`           | `--remove-port`·`--remove-service` + `--reload` |
| 끄기             | `ufw disable`                 | `systemctl stop firewalld`                      |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용      | 명령                                                 | 기대 결과            |
|------|----------------|------------------------------------------------------|----------------------|
| 1    | 활성 상태      | `ufw status` / `firewall-cmd --state`                | `active` / `running` |
| 2    | 규칙 목록      | `ufw status numbered` / `firewall-cmd --list-all`    | 의도한 포트·출발지만 |
| 3    | 재부팅 후 유지 | 재부팅 뒤 2번 다시 실행                              | 같은 규칙            |
| 4    | 허용 포트 도달 | 다른 PC에서 `nmap -sT -p 22,80 <서버>`               | `open`               |
| 5    | 차단 포트      | 다른 PC에서 `nmap -sT -p 5432 <서버>` (허용 대역 밖) | `filtered`           |
| 6    | 새 SSH 세션    | 활성화 뒤 새 터미널로 `ssh`                          | 접속됨               |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                     | 원인                                          | 해결 방법                                                 |
|------------------------------------------|-----------------------------------------------|-----------------------------------------------------------|
| 활성화 직후 SSH 끊김                     | SSH 허용 전에 기본 거부 적용                  | 콘솔로 접속해 SSH 허용 후 다시 활성화 (2절)               |
| Docker로 공개한 포트가 ufw로 막히지 않음 | Docker가 방화벽 규칙을 직접 추가              | `127.0.0.1:`로 공개하거나 Docker 문서의 방화벽 연동 확인  |
| firewalld 규칙이 재부팅 후 사라짐        | `--permanent` 없이 추가                       | `--permanent` + `--reload`, 또는 `--runtime-to-permanent` |
| `--permanent`로 넣었는데 적용 안 됨      | runtime에 반영 안 됨                          | `firewall-cmd --reload`                                   |
| 규칙이 예상과 다르게 동작                | ufw와 firewalld를 함께 사용, 다른 도구의 규칙 | 한 도구만 사용, `nft list ruleset`으로 실제 규칙 확인     |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [방화벽 iptables·nftables](./firewall_iptables_nftables.md) — 규칙의 바탕
- [Docker 네트워크](../../02_infrastructure/containers/docker_network.md) — Docker 포트 공개와 방화벽
- [SSH 보안](./ssh_security.md) — SSH 접근 제한
- [Linux 네트워크 점검 도구](../../01_fundamentals/linux/linux_network_tools.md) — nmap·ss로 확인

---

## 참고 자료

- Ubuntu: [ufw(8)](https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html) — ★★★☆☆
- firewalld: [Documentation](https://firewalld.org/documentation/) — ★★★☆☆
- GitHub: [firewalld releases](https://github.com/firewalld/firewalld/releases) — 2.5.2 확인 2026-11-23 — ★★★☆☆

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
