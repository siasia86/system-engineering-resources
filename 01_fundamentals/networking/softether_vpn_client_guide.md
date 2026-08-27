# SoftEther VPN Client 가이드

## 목차

| 섹션                                                                                                                                                 |
|------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 — Ubuntu](#2-설치--ubuntu) / [3. 설치 — Rocky Linux](#3-설치--rocky-linux)                                             |
| [4. VPN 연결 설정](#4-vpn-연결-설정) / [5. IP 할당 및 확인](#5-ip-할당-및-확인) / [6. systemd 서비스 등록](#6-systemd-서비스-등록)                   |
| [7. 주요 vpncmd 명령어](#7-주요-vpncmd-명령어) / [8. 트러블슈팅](#8-트러블슈팅) / [9. 타 VPN 클라이언트](#9-타-vpn-클라이언트로-softether-서버-접속) |

---

## 1. 개요

SoftEther VPN은 멀티 프로토콜을 지원하는 오픈소스 VPN 소프트웨어입니다.
이 문서는 Linux 클라이언트(`vpnclient`) 설치 및 연결 방법을 다룹니다.

| 항목      | 내용                                                |
|-----------|-----------------------------------------------------|
| 언어      | C                                                   |
| 라이선스  | Apache 2.0                                          |
| 최신 버전 | v4.44-9807-rtm (2026-08 기준)                       |
| GitHub    | https://github.com/SoftEtherVPN/SoftEtherVPN_Stable |

### 동작 원리

SoftEther VPN은 커널 가상 NIC(`tun`)와 Virtual Hub(소프트웨어 스위치)를 결합하여 Ethernet over HTTPS 터널을 구성합니다.

```
Linux Host
┌──────────────────────────────────────────────────────────────────┐
│  App (curl, ssh, ...)                                            │
│       |                                                          │
│  Kernel Routing Table                                            │
│       |                                                          │
│  [vpn_vpn0] TUN NIC  <---- vpnclient daemon (Ethernet/HTTPS) ───>│
│                              (Ethernet over HTTPS)               │
└──────────────────────────────────────────────────────────────────┘
```

```
                                      |
                              SoftEther VPN Server
                     ┌───────────────────────────────────────┐
                     │  Virtual Hub (software L2 switch)     │
                     │  ┌────────────┐  ┌────────────┐       │
                     │  │   NIC 1    │  │   NIC 2    │       │
                     │  └────────────┘  └────────────┘       │
                     └───────────────────────────────────────┘
```

- vpnclient 데몬이 서버와 TCP(443/992/1194) 연결을 맺고 Ethernet 프레임을 캡슐화합니다.
- 커널에 `vpn_<nicname>` TUN 인터페이스가 생성되며, IP 할당 후 트래픽이 흐릅니다.
- Virtual Hub는 소프트웨어 L2 스위치로, 연결된 클라이언트 간 Ethernet 프레임을 교환합니다.

### 서버 지원 프로토콜 및 포트

SoftEther Server는 단일 프로세스로 여러 프로토콜을 동시에 수신합니다.

| 프로토콜          | 기본 포트     | 클라이언트                              |
|-------------------|---------------|-----------------------------------------|
| SoftEther SSL-VPN | TCP 443, 992  | vpnclient (본 문서)                     |
| OpenVPN           | TCP/UDP 1194  | OpenVPN 클라이언트                      |
| L2TP/IPsec        | UDP 500, 4500 | Windows/iOS/Android 기본 VPN 클라이언트 |
| MS-SSTP           | TCP 443       | Windows 기본 VPN 클라이언트             |
| EtherIP/IPsec     | UDP 500, 4500 | Cisco 라우터 등                         |
| 관리 (vpncmd)     | TCP 5555      | vpncmd 원격 관리                        |

🟡 992 포트는 IANA pop3s 번호를 재활용합니다. 443이 차단된 방화벽 환경에서 대체 포트로 사용합니다.

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
wget https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.44-9807-rtm/softether-vpnclient-v4.44-9807-rtm-2025.04.16-linux-x64-64bit.tar.gz
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
wget https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.44-9807-rtm/softether-vpnclient-v4.44-9807-rtm-2025.04.16-linux-x64-64bit.tar.gz
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

### 인증 방식 3종

SoftEther 클라이언트는 3가지 인증 방식을 지원합니다.

| 인증 방식         | 명령어                | TYPE 옵션  | 비고                            |
|-------------------|-----------------------|------------|---------------------------------|
| 패스워드          | `AccountPasswordSet`  | `standard` | 일반 사용자명 + 패스워드        |
| RADIUS            | `AccountPasswordSet`  | `radius`   | RADIUS 서버 위임, OTP 연동 가능 |
| 클라이언트 인증서 | `AccountCertSet`      | —          | 인증서 파일(.pfx/.p12) 지정     |
| 익명              | `AccountAnonymousSet` | —          | 인증 없음, 테스트용             |

#### 패스워드 인증 (standard / radius)

```
VPN Client> AccountPasswordSet myconn /PASSWORD:SecurePassword123 /TYPE:standard
```

#### 클라이언트 인증서 인증

```
# 인증서(.pfx) 파일을 vpnclient가 읽을 수 있는 경로에 배치
VPN Client> AccountCertSet myconn /LOADCERT:/etc/vpn/client.crt /LOADKEY:/etc/vpn/client.key
```

#### 서버 인증서 검증 활성화

서버 인증서를 검증하면 MITM 공격을 방어할 수 있습니다.

```
# 서버 CA 인증서 등록
VPN Client> AccountServerCertSet myconn /LOADCERT:/etc/vpn/server-ca.crt

# 검증 활성화
VPN Client> AccountServerCertEnable myconn

# 검증 비활성화 (자체 서명 인증서 환경)
VPN Client> AccountServerCertDisable myconn
```

### Proxy 경유 연결

방화벽이 직접 TCP 443 연결을 차단하는 경우 HTTP/SOCKS 프록시를 경유합니다.

#### HTTP Proxy

```
VPN Client> AccountProxyHttp myconn /SERVER:proxy.example.com:8080
```

#### SOCKS Proxy

```
VPN Client> AccountProxySocks myconn /SERVER:proxy.example.com:1080
```

#### Proxy 해제

```
VPN Client> AccountProxyNone myconn
```

### 재연결 설정

연결 끊김 시 자동 재시도 횟수와 간격을 설정합니다.

```
# NUM: 재시도 횟수 (0 = 무한), INTERVAL: 재시도 간격(초)
VPN Client> AccountRetrySet myconn /NUM:0 /INTERVAL:15
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

### Full Tunnel 라우팅

모든 트래픽(0.0.0.0/0)을 VPN을 통해 라우팅합니다.

```bash
# 기존 기본 경로 확인
ip route show default

# VPN 서버 IP(192.0.2.1)만 현재 게이트웨이로 유지 (VPN 연결 유지용)
GW=$(ip route show default | awk '/via/{print $3; exit}')
ip route add 192.0.2.1 via "$GW"

# 기본 경로를 VPN NIC으로 변경
ip route del default
ip route add default dev vpn_vpn0
```

🟡 Full Tunnel 적용 시 VPN 서버 IP 경로를 먼저 추가하지 않으면 VPN 연결이 끊깁니다.

### Split Tunnel 라우팅

특정 대역만 VPN으로 라우팅하고 나머지는 기존 경로를 유지합니다.

```bash
# 사내망(10.0.0.0/8)만 VPN으로 라우팅
ip route add 10.0.0.0/8 dev vpn_vpn0

# 여러 대역 추가
ip route add 172.16.0.0/12 dev vpn_vpn0
ip route add 192.168.0.0/16 dev vpn_vpn0
```

### 라우팅 확인

```bash
ip route show
ip route get 10.0.0.1      # 10.0.0.1 패킷이 어느 인터페이스로 나가는지 확인
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

#### 가상 NIC 관리

| 명령어                 | 설명               |
|------------------------|--------------------|
| `NicCreate <name>`     | 가상 NIC 생성      |
| `NicList`              | 가상 NIC 목록 확인 |
| `NicDelete <name>`     | 가상 NIC 삭제      |
| `NicEnable <name>`     | 가상 NIC 활성화    |
| `NicDisable <name>`    | 가상 NIC 비활성화  |
| `NicGetSetting <name>` | 가상 NIC 설정 확인 |

#### 계정 관리

| 명령어                                  | 설명                   |
|-----------------------------------------|------------------------|
| `AccountCreate <name> ...`              | VPN 계정 생성          |
| `AccountList`                           | 계정 목록 확인         |
| `AccountGet <name>`                     | 계정 상세 확인         |
| `AccountSet <name> ...`                 | 계정 기본 정보 수정    |
| `AccountRename <name> /NEWNAME:<new>`   | 계정 이름 변경         |
| `AccountDelete <name>`                  | 계정 삭제              |
| `AccountExport <name> /SAVEPATH:<path>` | 계정 설정 내보내기     |
| `AccountImport /LOADPATH:<path>`        | 계정 설정 가져오기     |
| `AccountStartupSet <name>`              | 부팅 시 자동 연결 등록 |
| `AccountStartupRemove <name>`           | 자동 연결 해제         |

#### 인증 설정

| 명령어                                          | 설명                   |
|-------------------------------------------------|------------------------|
| `AccountPasswordSet <name> /PASSWORD:x /TYPE:y` | 패스워드 인증 설정     |
| `AccountAnonymousSet <name>`                    | 익명 인증 설정         |
| `AccountCertSet <name> /LOADCERT:x /LOADKEY:y`  | 클라이언트 인증서 설정 |
| `AccountCertGet <name>`                         | 클라이언트 인증서 확인 |
| `AccountUsernameSet <name> /USERNAME:x`         | 사용자명 변경          |

#### 서버 인증서 검증

| 명령어                                         | 설명                      |
|------------------------------------------------|---------------------------|
| `AccountServerCertEnable <name>`               | 서버 인증서 검증 활성화   |
| `AccountServerCertDisable <name>`              | 서버 인증서 검증 비활성화 |
| `AccountServerCertSet <name> /LOADCERT:<path>` | 서버 CA 인증서 등록       |
| `AccountServerCertGet <name>`                  | 서버 CA 인증서 확인       |
| `AccountServerCertDelete <name>`               | 서버 CA 인증서 삭제       |

#### 연결 제어

| 명령어                                      | 설명                  |
|---------------------------------------------|-----------------------|
| `AccountConnect <name>`                     | VPN 연결              |
| `AccountDisconnect <name>`                  | VPN 연결 해제         |
| `AccountStatusGet <name>`                   | 연결 상태 확인        |
| `AccountRetrySet <name> /NUM:n /INTERVAL:s` | 재연결 횟수·간격 설정 |

#### 프록시 설정

| 명령어                                           | 설명              |
|--------------------------------------------------|-------------------|
| `AccountProxyNone <name>`                        | 직접 연결 (기본)  |
| `AccountProxyHttp <name> /SERVER:<host>:<port>`  | HTTP 프록시 경유  |
| `AccountProxySocks <name> /SERVER:<host>:<port>` | SOCKS 프록시 경유 |

#### 기타

| 명령어         | 설명                |
|----------------|---------------------|
| `VersionGet`   | vpnclient 버전 확인 |
| `PasswordSet`  | 관리 비밀번호 설정  |
| `RemoteEnable` | 원격 관리 허용      |
| `KeepEnable`   | Keep-Alive 활성화   |

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

### 연결이 반복적으로 끊기는 경우

```bash
# 1. AccountStatusGet으로 연결 상태 확인
VPN Client> AccountStatusGet myconn

# 2. 재연결 설정 확인 — 무한 재시도 설정
VPN Client> AccountRetrySet myconn /NUM:0 /INTERVAL:15

# 3. Keep-Alive 활성화
VPN Client> KeepEnable
VPN Client> KeepSet /HOST:8.8.8.8 /PORT:80 /INTERVAL:50 /PROTOCOL:tcp
```

### 방화벽이 443을 차단하는 경우

SoftEther Server의 리스너 포트 우선순위 순서로 시도합니다.

```
# 443 차단 → 992 시도
VPN Client> AccountCreate myconn /SERVER:192.0.2.1:992 /HUB:VPN /USERNAME:Secureuser123 /NICNAME:vpn0

# 992 차단 → 1194 시도
VPN Client> AccountCreate myconn /SERVER:192.0.2.1:1194 /HUB:VPN /USERNAME:Secureuser123 /NICNAME:vpn0
```

🟡 포트 변경은 서버가 해당 포트에 리스너를 열어 두고 있는 경우에만 동작합니다.

### 라우팅 충돌 (VPN 연결 후 인터넷 불통)

Full Tunnel 설정 시 VPN 서버 IP 경로를 미리 추가하지 않아 발생합니다.

```bash
# 현재 기본 경로 확인
ip route show default

# VPN 서버 IP 직접 경로 추가 (VPN 연결용)
GW=$(ip route show default | awk '/via/{print $3; exit}')
ip route add 192.0.2.1 via "$GW"

# 기본 경로를 VPN NIC으로 변경
ip route del default
ip route add default dev vpn_vpn0
```

### vpncmd 접속 불가 (Connection refused)

```bash
# vpnclient 프로세스 확인
ps aux | grep vpnclient

# 재시작
cd /opt/vpnclient
./vpnclient stop
sleep 2
./vpnclient start

# 관리 포트(5555) 리스닝 확인
ss -tlnp | grep 5555
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 타 VPN 클라이언트로 SoftEther 서버 접속

SoftEther VPN Server는 vpnclient 외에도 OS 기본 VPN 클라이언트로 접속할 수 있습니다.

### L2TP/IPsec (Windows / iOS / Android)

SoftEther Server에서 L2TP 활성화 후, 각 OS 기본 VPN 클라이언트로 접속합니다.

| 항목              | 값                |
|-------------------|-------------------|
| VPN 종류          | L2TP/IPsec        |
| 서버 주소         | SoftEther 서버 IP |
| 사전 공유 키(PSK) | 서버 설정 값      |
| 사용자명          | VPN 계정 사용자명 |
| 패스워드          | VPN 계정 패스워드 |

```bash
# Linux에서 strongSwan으로 L2TP/IPsec 접속 예시
apt install -y strongswan xl2tpd

# /etc/ipsec.conf
cat << 'IPSEC' > /etc/ipsec.conf
conn softether-l2tp
  authby=secret
  auto=start
  keyexchange=ikev1
  left=%defaultroute
  right=192.0.2.1
  type=transport
  esp=aes128-sha1-modp1024!
  ike=aes128-sha1-modp1024!
  ikelifetime=8h
  keylife=1h
IPSEC

# /etc/ipsec.secrets
echo ": PSK "SecureKey123"" > /etc/ipsec.secrets
```

### OpenVPN 클라이언트로 접속

SoftEther Server에서 OpenVPN 구성 파일(.ovpn)을 받아 사용합니다.

```bash
apt install -y openvpn

# 서버 관리자에게 받은 .ovpn 파일로 연결
openvpn --config softether-server.ovpn --daemon

# 연결 상태 확인
ip addr show tun0
```

### 프로토콜별 접속 방법 비교

| 클라이언트          | 프로토콜       | 포트         | 장점                       | 단점                           |
|---------------------|----------------|--------------|----------------------------|--------------------------------|
| vpnclient (본 문서) | SoftEther 독자 | TCP 443/992  | 방화벽 우회, 고성능        | SoftEther 클라이언트 설치 필요 |
| OS 기본 VPN         | L2TP/IPsec     | UDP 500/4500 | 설치 불필요                | NAT 환경 제약                  |
| OpenVPN 클라이언트  | OpenVPN        | TCP/UDP 1194 | 오픈소스, 광범위한 OS 지원 | 클라이언트 설치 필요           |
| Windows 기본 VPN    | MS-SSTP        | TCP 443      | Windows 내장               | Windows 전용                   |

> 관련 프로토콜 상세: [vpn_protocol_concepts.md](./vpn_protocol_concepts.md)

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

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.
