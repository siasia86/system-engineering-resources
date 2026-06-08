# SoftEther VPN Client 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 설치 — Ubuntu](#2-설치-ubuntu) / [3. 설치 — Rocky Linux](#3-설치-rocky-linux) |
| [4. VPN 연결 설정](#4-vpn-연결-설정) / [5. IP 할당 및 확인](#5-ip-할당-및-확인) / [6. systemd 서비스 등록](#6-systemd-서비스-등록) |
| [7. 주요 vpncmd 명령어](#7-주요-vpncmd-명령어) / [8. 트러블슈팅](#8-트러블슈팅) |

---

## 1. 개요

SoftEther VPN은 멀티 프로토콜을 지원하는 오픈소스 VPN 소프트웨어입니다.
이 문서는 Linux 클라이언트(`vpnclient`) 설치 및 연결 방법을 다룹니다.

| 항목      | 내용                                                |
|-----------|-----------------------------------------------------|
| 언어      | C                                                   |
| 라이선스  | Apache 2.0                                          |
| 최신 버전 | v4.43-9799-beta (2026-05 기준)                      |
| GitHub    | https://github.com/SoftEtherVPN/SoftEtherVPN_Stable |

### 바이너리 종류

| 바이너리    | 역할                     |
|-------------|--------------------------|
| `vpnserver` | VPN 서버                 |
| `vpnclient` | VPN 클라이언트 (본 문서) |
| `vpnbridge` | 브리지 모드              |
| `vpncmd`    | CLI 관리 도구            |

[⬆ 목차로 돌아가기](#목차)

## 2. 설치 — Ubuntu

### 의존성 설치

```bash
apt update
apt install -y gcc make libssl-dev libreadline-dev libncurses-dev wget
```

### 소스 다운로드 및 빌드

```bash
wget https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.43-9799-beta/softether-vpnclient-v4.43-9799-beta-2023.08.31-linux-x64-64bit.tar.gz
tar xzf softether-vpnclient-*.tar.gz
cd vpnclient
make
```

> `make` 실행 중 라이선스 동의 프롬프트 3회 → 각각 `1` 입력

### 설치 디렉토리 이동

```bash
mv ~/vpnclient /opt/vpnclient
```

[⬆ 목차로 돌아가기](#목차)

## 3. 설치 — Rocky Linux

### 의존성 설치

```bash
dnf install -y gcc make openssl-devel readline-devel ncurses-devel wget
```

### 소스 다운로드 및 빌드

```bash
wget https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.43-9799-beta/softether-vpnclient-v4.43-9799-beta-2023.08.31-linux-x64-64bit.tar.gz
tar xzf softether-vpnclient-*.tar.gz
cd vpnclient
make
```

> `make` 실행 중 라이선스 동의 프롬프트 3회 → 각각 `1` 입력

### 설치 디렉토리 이동

```bash
mv ~/vpnclient /opt/vpnclient
```

[⬆ 목차로 돌아가기](#목차)

## 4. VPN 연결 설정

### vpnclient 시작 및 vpncmd 진입

```bash
cd /opt/vpnclient
./vpnclient start
./vpncmd
```

```
1. Management of VPN Server or VPN Bridge
2. Management of VPN Client    ← 클라이언트 명령어 (AccountCreate, NicCreate 등)
3. Use of VPN Tools (certificate creation and Network Traffic Speed Test Tool)

Select 1, 2 or 3: 2

Hostname of IP Address of Destination: (Enter 생략 — 로컬 클라이언트 관리)
```

> `AccountCreate` 는 클라이언트에서 실행합니다.
> "이 클라이언트가 어느 서버에, 어떤 계정으로 접속할지" 를 로컬에 등록하는 명령어입니다.
> `/SERVER`, `/USERNAME` 은 서버에 미리 생성된 계정 정보를 클라이언트에 등록하는 것입니다.

### 가상 NIC 생성

```
VPN Client> NicCreate vpn0
```

### 계정 생성

```
VPN Client> AccountCreate myconn /SERVER:192.0.2.1:443 /HUB:VPN /USERNAME:Secureuser123 /NICNAME:vpn0
```

| 파라미터    | 설명                        |
|-------------|-----------------------------|
| `/SERVER`   | VPN 서버 주소:포트          |
| `/HUB`      | 연결할 Virtual Hub 이름     |
| `/USERNAME` | VPN 계정 사용자명           |
| `/NICNAME`  | 연결에 사용할 가상 NIC 이름 |

### 패스워드 설정

```
VPN Client> AccountPasswordSet myconn /PASSWORD:SecurePassword123 /TYPE:standard
```

> `/TYPE` 옵션: `standard` (일반) 또는 `radius` (RADIUS 인증)

### 연결

```
VPN Client> AccountConnect myconn
```

### 연결 상태 확인

```
VPN Client> AccountStatusGet myconn
```

[⬆ 목차로 돌아가기](#목차)

## 5. IP 할당 및 확인

### DHCP로 IP 할당

```bash
# Ubuntu
dhclient vpn_vpn0

# Rocky Linux
dhclient vpn_vpn0
```

> 가상 NIC 이름은 `vpn_` + NicCreate 시 지정한 이름. 예: `vpn_vpn0`

### 연결 확인

```bash
ip addr show vpn_vpn0
ping -c 3 192.0.2.1
```

### 연결 해제

```bash
# vpncmd 에서
VPN Client> AccountDisconnect myconn
```

[⬆ 목차로 돌아가기](#목차)

## 6. systemd 서비스 등록

부팅 시 자동 시작이 필요한 경우 설정합니다.

```bash
cat << 'UNIT' > /etc/systemd/system/vpnclient.service
[Unit]
Description=SoftEther VPN Client
After=network.target

[Service]
Type=forking
ExecStart=/opt/vpnclient/vpnclient start
ExecStop=/opt/vpnclient/vpnclient stop
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now vpnclient
```

### 상태 확인

```bash
systemctl status vpnclient
```

[⬆ 목차로 돌아가기](#목차)

## 7. 주요 vpncmd 명령어

```bash
cd /opt/vpnclient && ./vpncmd
# 진입 후 2 선택 → Hostname Enter 생략
```

### 명령어 목록

| 명령어                          | 설명           |
|---------------------------------|----------------|
| `NicCreate <name>`              | 가상 NIC 생성  |
| `NicList`                       | 가상 NIC 목록  |
| `NicDelete <name>`              | 가상 NIC 삭제  |
| `AccountCreate <name> ...`      | VPN 계정 생성  |
| `AccountList`                   | 계정 목록      |
| `AccountGet <name>`             | 계정 상세 확인 |
| `AccountPasswordSet <name> ...` | 패스워드 설정  |
| `AccountConnect <name>`         | VPN 연결       |
| `AccountDisconnect <name>`      | VPN 연결 해제  |
| `AccountStatusGet <name>`       | 연결 상태 확인 |
| `AccountDelete <name>`          | 계정 삭제      |

### 계정 생성 ~ 삭제 전체 흐름

#### 생성

```
# 가상 NIC 생성 (최초 1회)
VPN Client> NicCreate vpn0

# 계정 생성 (대화형)
VPN Client> AccountCreate my_vpn
Destination VPN Server Host Name and Port Number: vpn.example.com:80
Destination Virtual HUB Name: VPN
Connecting User Name: Secureuser123
Used Virtual Network Adapter Name: vpn0

# 또는 한 줄로
VPN Client> AccountCreate my_vpn /SERVER:vpn.example.com:80 /HUB:VPN /USERNAME:Secureuser123 /NICNAME:vpn0

# 패스워드 설정 (standard: 일반 / radius: RADIUS+OTP)
VPN Client> AccountPasswordSet my_vpn /PASSWORD:SecurePassword123456789 /TYPE:radius
```

#### 확인

```
VPN Client> AccountList
VPN Client> AccountGet my_vpn
```

#### 연결 / 해제

```
VPN Client> AccountConnect my_vpn
VPN Client> AccountStatusGet my_vpn
VPN Client> AccountDisconnect my_vpn
```

#### 수정 (서버 주소 변경 등)

```
# 삭제 후 재생성
VPN Client> AccountDisconnect my_vpn
VPN Client> AccountDelete my_vpn
VPN Client> AccountCreate my_vpn /SERVER:new-server.example.com:443 /HUB:VPN /USERNAME:Secureuser123 /NICNAME:vpn0
VPN Client> AccountPasswordSet my_vpn /PASSWORD:SecurePassword123456789 /TYPE:radius
```

#### 삭제

```
# 연결 중이면 먼저 해제
VPN Client> AccountDisconnect my_vpn
VPN Client> AccountDelete my_vpn

# NIC 도 삭제할 경우
VPN Client> NicDelete vpn0
```

[⬆ 목차로 돌아가기](#목차)

## 8. 트러블슈팅

### vpnclient start 실패

```bash
# 프로세스 확인
ps aux | grep vpnclient

# 로그 확인
ls /opt/vpnclient/packet_log/
```

### 가상 NIC 미생성 (vpn_vpn0 없음)

```bash
# 커널 tun 모듈 로드 확인
lsmod | grep tun

# 없으면 로드
modprobe tun
```

### DHCP IP 미할당

```bash
# 수동 IP 설정
ip addr add 10.0.0.100/24 dev vpn_vpn0
ip link set vpn_vpn0 up
ip route add 10.0.0.0/24 dev vpn_vpn0
```

### 인증 실패

```
VPN Client> AccountPasswordSet myconn /PASSWORD:SecurePassword123 /TYPE:standard
```

> 서버 인증 방식이 RADIUS 인 경우 `/TYPE:radius` 로 변경

### Google OTP (TOTP) 연동 서버 접속

서버가 RADIUS + Google Authenticator 인증을 사용하는 경우,
패스워드를 `고정패스워드 + OTP 6자리` 를 붙여서 입력합니다.

```
VPN Client> AccountPasswordSet my_vpn /PASSWORD:SecurePassword123456789 /TYPE:radius
```

> 예: 고정 패스워드 `SecurePassword123`, OTP `456789` → `SecurePassword123456789`

| 확인 항목     | 내용                                   |
|---------------|----------------------------------------|
| 인증 타입     | `/TYPE:radius`                         |
| 패스워드 형식 | `고정패스워드` + `OTP 6자리` 연속 입력 |
| OTP 유효시간  | 30초 — 만료 전 입력 필요               |

#### 전체 연결 흐름 (Google OTP 서버 기준)

```bash
# 1. 계정 등록 확인
VPN Client> AccountList

# 2. RADIUS 패스워드 설정 (고정패스워드 + OTP 6자리)
VPN Client> AccountPasswordSet my_vpn /PASSWORD:SecurePassword123456789 /TYPE:radius

# 3. 연결
VPN Client> AccountConnect my_vpn

# 4. 연결 상태 확인
VPN Client> AccountStatusGet my_vpn

# 5. vpncmd 종료 후 IP 할당
exit
dhclient vpn_vpn0
ip addr show vpn_vpn0
```

🟡 정확한 패스워드 형식은 서버 관리자에게 확인합니다. 서버 설정에 따라 OTP 단독 입력 방식일 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- SoftEther VPN: [softether.org](https://www.softether.org/) — ★★★☆☆
- GitHub Releases: [github.com/SoftEtherVPN](https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-11

**마지막 업데이트**: 2026-05-11

© 2026 siasia86. Licensed under CC BY 4.0.
