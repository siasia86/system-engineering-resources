# SoftEther VPN Server 가이드

## 목차

| 섹션                                                                                                                                               |
|----------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 — Ubuntu](#2-설치--ubuntu) / [3. 설치 — Rocky Linux](#3-설치--rocky-linux)                                           |
| [4. 초기 설정](#4-초기-설정-vpncmd) / [5. L2TP/IPsec 활성화](#5-l2tpipsec-활성화) / [6. OpenVPN 활성화](#6-openvpn-활성화)                         |
| [7. 방화벽 및 NAT 설정](#7-방화벽-및-nat-설정) / [8. systemd 서비스 등록](#8-systemd-서비스-등록) / [9. 주요 vpncmd 명령어](#9-주요-vpncmd-명령어) |
| [10. 트러블슈팅](#10-트러블슈팅)                                                                                                                   |

---

## 1. 개요

SoftEther VPN Server(`vpnserver`)는 단일 프로세스로 여러 VPN 프로토콜을 동시에 수신하는 멀티 프로토콜 VPN 서버입니다.

| 항목      | 내용                                                |
|-----------|-----------------------------------------------------|
| 언어      | C                                                   |
| 라이선스  | Apache 2.0                                          |
| 최신 버전 | v4.44-9807-rtm (2025-05-07)                         |
| GitHub    | https://github.com/SoftEtherVPN/SoftEtherVPN_Stable |

### 아키텍처

```
                    Internet
                        |
            ┌───────────────────────┐
            │   vpnserver daemon    │
            │                       │
            │  ┌─────────────────┐  │
            │  │  Virtual Hub    │  │
            │  │  (L2 switch)    │  │
            │  │  ┌────┐ ┌────┐  │  │
            │  │  │NIC1│ │NIC2│  │  │
            │  │  └────┘ └────┘  │  │
            │  └─────────────────┘  │
            │                       │
            │  Listeners:           │
            │  TCP 443/992/1194     │
            │  TCP 5555 (vpncmd)    │
            │  UDP 500/4500 (L2TP)  │
            └───────────────────────┘
```

- Virtual Hub는 소프트웨어 L2 스위치로, 연결된 클라이언트 간 Ethernet 프레임을 교환합니다.
- 단일 서버에서 SSL-VPN, L2TP/IPsec, OpenVPN, SSTP를 동시에 수신합니다.
- 최대 4,096개 동시 VPN 세션, 최대 4,096개 Virtual Hub를 지원합니다.

### 바이너리 종류

| 바이너리    | 역할                                 |
|-------------|--------------------------------------|
| `vpnserver` | VPN 서버 (본 문서)                   |
| `vpnclient` | VPN 클라이언트                       |
| `vpnbridge` | 브리지 모드                          |
| `vpncmd`    | CLI 관리 도구 (서버/클라이언트 공용) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치 — Ubuntu

### 의존성 설치

```bash
apt update
apt install -y gcc make libssl-dev libreadline-dev libncurses-dev wget
```

### 소스 다운로드 및 빌드

```bash
wget https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.44-9807-rtm/softether-vpnserver-v4.44-9807-rtm-2025.04.16-linux-x64-64bit.tar.gz
tar xzf softether-vpnserver-*.tar.gz
cd vpnserver
make
```

> `make` 실행 중 라이선스 동의 프롬프트 3회 → 각각 `1` 입력

### 설치 디렉토리 이동

```bash
mv ~/vpnserver /opt/vpnserver
chmod 600 /opt/vpnserver/*
chmod 700 /opt/vpnserver/vpnserver
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설치 — Rocky Linux

### 의존성 설치

```bash
dnf install -y gcc make openssl-devel readline-devel ncurses-devel wget
```

### 소스 다운로드 및 빌드

```bash
wget https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.44-9807-rtm/softether-vpnserver-v4.44-9807-rtm-2025.04.16-linux-x64-64bit.tar.gz
tar xzf softether-vpnserver-*.tar.gz
cd vpnserver
make
```

> `make` 실행 중 라이선스 동의 프롬프트 3회 → 각각 `1` 입력

### 설치 디렉토리 이동

```bash
mv ~/vpnserver /opt/vpnserver
chmod 600 /opt/vpnserver/*
chmod 700 /opt/vpnserver/vpnserver
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 설정 (vpncmd)

### vpnserver 시작

```bash
/opt/vpnserver/vpnserver start
```

### vpncmd 접속

```bash
/opt/vpnserver/vpncmd 127.0.0.1 /SERVER
```

처음 접속 시 패스워드 미설정 상태이므로 빈 칸으로 Enter.

### 서버 관리자 패스워드 설정

```
VPN Server> ServerPasswordSet
```

### Virtual Hub 생성

```
VPN Server> HubCreate VPN
```

> Hub 이름은 임의 지정 가능. 이하 예시에서 Hub 이름은 `VPN`을 사용합니다.

### Hub 전환 및 사용자 생성

```
VPN Server> Hub VPN
VPN Server/VPN> UserCreate Secureuser123
VPN Server/VPN> UserPasswordSet Secureuser123
```

> 패스워드 입력 프롬프트 2회 → 동일 값 입력

### SecureNAT 활성화

SecureNAT는 별도 브리지 없이 Virtual Hub 내부에서 NAT와 DHCP를 처리합니다.
인터넷에 연결된 서버에서 클라이언트에게 IP를 할당하고 트래픽을 라우팅합니다.

```
VPN Server/VPN> SecureNatEnable
```

활성화 확인:

```
VPN Server/VPN> SecureNatStatusGet
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. L2TP/IPsec 활성화

Windows, iOS, Android 기본 내장 VPN 클라이언트와 호환됩니다.

### vpncmd에서 활성화

```
VPN Server> IPsecEnable
```

프롬프트 응답:

```
Enable L2TP over IPsec Server Function (yes/no): yes
Enable Raw L2TP Server Function (yes/no): no
Enable EtherIP / L2TPv3 over IPsec Server Function (yes/no): no
Pre Shared Key for IPsec (Input 9 characters): SecureKey123
Default Virtual HUB in a case of omitting the HUB on the Username: VPN
```

> IPsec 사전 공유키(PSK)는 9자 이상 권장합니다.

### 방화벽 포트 허용 (별도 적용 필요)

| 포트     | 프로토콜 | 용도          |
|----------|----------|---------------|
| UDP 500  | UDP      | IKE           |
| UDP 4500 | UDP      | NAT-T (IPsec) |
| UDP 1701 | UDP      | L2TP          |

🟡 SoftEther의 L2TP/IPsec DH Group은 MODP 768/1024/1536 (2048bit 미만)입니다. 보안 민감 환경에서는 SoftEther SSL-VPN 또는 OpenVPN 사용을 권장합니다. 상세 내용은 [`_reference/softether_official_notes.md`](../../_reference/softether_official_notes.md) §6 참고.

### 클라이언트 연결 정보

| 항목      | 값                  |
|-----------|---------------------|
| 서버 주소 | 서버 IP 또는 도메인 |
| 계정 이름 | `Secureuser123@VPN` |
| 패스워드  | 설정한 패스워드     |
| IPsec PSK | 설정한 사전 공유키  |
| VPN 종류  | L2TP/IPsec          |

> 사용자명 형식: `<username>@<HubName>`. Hub 이름 생략 시 `IPsecEnable`에서 설정한 기본 Hub로 연결됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. OpenVPN 활성화

### .ovpn 설정 파일 생성

```
VPN Server> OpenVpnEnable yes /PORTS:1194
VPN Server> OpenVpnMakeConfig /home/user/openvpn_config.zip
```

> 생성된 zip 파일 안에 OS별 `.ovpn` 파일이 포함됩니다.

### zip 압축 해제 및 배포

```bash
unzip /home/user/openvpn_config.zip -d /home/user/openvpn_config/
```

클라이언트에 `*.ovpn` 파일을 전달합니다.

### 방화벽 포트 허용

| 포트     | 프로토콜 | 용도    |
|----------|----------|---------|
| UDP 1194 | UDP      | OpenVPN |

🟡 SoftEther의 OpenVPN은 AES-256-CBC를 지원하지만 기본 협상 cipher에 BF-CBC 등 취약 cipher가 포함됩니다. 클라이언트 측 `.ovpn`에 `cipher AES-256-GCM`을 명시적으로 추가하는 것을 권장합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 방화벽 및 NAT 설정

### iptables — 포트 허용

```bash
# SoftEther SSL-VPN
iptables -A INPUT -p tcp --dport 443  -j ACCEPT
iptables -A INPUT -p tcp --dport 992  -j ACCEPT
iptables -A INPUT -p tcp --dport 1194 -j ACCEPT
iptables -A INPUT -p tcp --dport 5555 -j ACCEPT

# L2TP/IPsec
iptables -A INPUT -p udp --dport 500  -j ACCEPT
iptables -A INPUT -p udp --dport 4500 -j ACCEPT
iptables -A INPUT -p udp --dport 1701 -j ACCEPT

# OpenVPN
iptables -A INPUT -p udp --dport 1194 -j ACCEPT
```

### iptables — NAT 설정 (SecureNAT 미사용 시)

SecureNAT를 사용하지 않고 OS 레벨 NAT를 사용하는 경우:

```bash
# IP 포워딩 활성화
echo 1 > /proc/sys/net/ipv4/ip_forward
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf

# MASQUERADE (eth0 = 외부 인터페이스)
iptables -t nat -A POSTROUTING -s 192.168.30.0/24 -o eth0 -j MASQUERADE
```

> `192.168.30.0/24`는 SecureNAT DHCP가 할당하는 기본 대역입니다. 변경한 경우 맞춰서 수정합니다.

### iptables 규칙 영구 저장

```bash
# Ubuntu
apt install -y iptables-persistent
netfilter-persistent save

# Rocky Linux
dnf install -y iptables-services
service iptables save
systemctl enable iptables
```

### firewalld 사용 시 (Rocky Linux)

```bash
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=992/tcp
firewall-cmd --permanent --add-port=1194/tcp
firewall-cmd --permanent --add-port=5555/tcp
firewall-cmd --permanent --add-port=500/udp
firewall-cmd --permanent --add-port=4500/udp
firewall-cmd --permanent --add-port=1194/udp
firewall-cmd --reload
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. systemd 서비스 등록

```bash
cat > /etc/systemd/system/vpnserver.service << 'EOF'
[Unit]
Description=SoftEther VPN Server
After=network.target

[Service]
Type=forking
ExecStart=/opt/vpnserver/vpnserver start
ExecStop=/opt/vpnserver/vpnserver stop
WorkingDirectory=/opt/vpnserver
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vpnserver
systemctl start vpnserver
systemctl status vpnserver
```

### 동작 확인

```bash
# 리스너 포트 확인
ss -tlnp | grep -E '443|992|1194|5555'

# 프로세스 확인
ps aux | grep vpnserver
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 주요 vpncmd 명령어

vpncmd를 서버 모드로 접속:

```bash
/opt/vpnserver/vpncmd 127.0.0.1 /SERVER
```

Hub 모드로 전환:

```
VPN Server> Hub <HubName>
```

### 서버 전체 관리

| 명령어              | 설명                                     |
|---------------------|------------------------------------------|
| `ServerPasswordSet` | 서버 관리자 패스워드 설정                |
| `ServerInfo`        | 서버 버전 및 기본 정보 조회              |
| `ServerStatus`      | 현재 세션 수, 트래픽 통계 조회           |
| `ListenerList`      | 리스너 포트 목록 조회                    |
| `ListenerCreate`    | 리스너 포트 추가                         |
| `ListenerDelete`    | 리스너 포트 삭제                         |
| `HubCreate`         | Virtual Hub 생성                         |
| `HubDelete`         | Virtual Hub 삭제                         |
| `HubList`           | Virtual Hub 목록 조회                    |
| `IPsecEnable`       | L2TP/IPsec 서버 기능 활성화              |
| `IPsecGet`          | L2TP/IPsec 설정 조회                     |
| `OpenVpnEnable`     | OpenVPN 서버 기능 활성화                 |
| `OpenVpnMakeConfig` | OpenVPN 클라이언트 설정 파일(.ovpn) 생성 |
| `SstpEnable`        | SSTP 서버 기능 활성화                    |
| `Keep`              | Keep-alive 설정 조회                     |
| `Flush`             | 설정 파일 즉시 저장                      |

### Hub 관리

| 명령어               | 설명                     |
|----------------------|--------------------------|
| `Hub <name>`         | 대상 Hub 전환            |
| `HubCreate`          | Hub 생성                 |
| `HubDelete`          | Hub 삭제                 |
| `HubList`            | Hub 목록                 |
| `UserCreate`         | 사용자 생성              |
| `UserDelete`         | 사용자 삭제              |
| `UserList`           | 사용자 목록              |
| `UserPasswordSet`    | 사용자 패스워드 설정     |
| `UserGet`            | 사용자 정보 조회         |
| `GroupCreate`        | 그룹 생성                |
| `SessionList`        | 현재 세션 목록           |
| `SessionGet`         | 세션 상세 정보           |
| `SessionDisconnect`  | 세션 강제 종료           |
| `AccessAdd`          | 액세스 리스트 규칙 추가  |
| `AccessList`         | 액세스 리스트 조회       |
| `SecureNatEnable`    | SecureNAT 활성화         |
| `SecureNatDisable`   | SecureNAT 비활성화       |
| `SecureNatStatusGet` | SecureNAT 상태 조회      |
| `DhcpGet`            | SecureNAT DHCP 설정 조회 |
| `DhcpSet`            | SecureNAT DHCP 설정 변경 |
| `BridgeCreate`       | 로컬 브리지 생성         |
| `BridgeList`         | 로컬 브리지 목록         |
| `BridgeDelete`       | 로컬 브리지 삭제         |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

### vpnserver 시작 실패

```bash
# 로그 확인
tail -f /opt/vpnserver/server_log/vpn_*.log

# 포트 충돌 확인 (443이 다른 프로세스에서 사용 중인 경우)
ss -tlnp | grep 443
```

443 포트가 nginx/apache와 충돌하는 경우 443 리스너를 삭제하고 992로 운영합니다:

```
VPN Server> ListenerDelete 443
VPN Server> ListenerCreate 992
```

---

### L2TP/IPsec 클라이언트 연결 실패

확인 순서:

1. UDP 500, 4500 방화벽 허용 여부 확인
2. `IPsecGet`으로 PSK 및 기본 Hub 설정 확인
3. 사용자명 형식 확인 — `username@HubName`
4. 클라우드 환경이면 보안 그룹(Security Group)에서 UDP 500/4500 추가

```bash
# UDP 포트 수신 확인
ss -ulnp | grep -E '500|4500'
```

---

### SecureNAT IP 할당 안 됨

```
VPN Server/VPN> SecureNatStatusGet
VPN Server/VPN> DhcpGet
```

DHCP 대역이 서버 로컬 네트워크와 충돌하면 `DhcpSet`으로 대역 변경:

```
VPN Server/VPN> DhcpSet
```

---

### vpncmd 원격 접속 불가

```bash
# 5555 포트 수신 여부 확인
ss -tlnp | grep 5555
```

5555가 없으면 vpnserver가 미실행 중이거나 리스너가 삭제된 상태입니다:

```bash
/opt/vpnserver/vpnserver start
```

```
VPN Server> ListenerCreate 5555
```

---

### 설정 변경 후 즉시 반영

vpncmd에서 설정 변경 후 파일을 즉시 저장합니다:

```
VPN Server> Flush
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- SoftEther VPN 공식 레퍼런스: [softether.org/4-docs/1-manual](https://www.softether.org/4-docs/1-manual) — ★★★☆☆
- SoftEther How-to 가이드: [softether.org/4-docs/2-howto](https://www.softether.org/4-docs/2-howto) — ★★★☆☆
- linuxbabe.com Ubuntu 24.04 가이드: [linuxbabe.com/ubuntu/set-up-softether-vpn-server-ubuntu-24-04](https://www.linuxbabe.com/ubuntu/set-up-softether-vpn-server-ubuntu-24-04) — ★★☆☆☆
- [SoftEther VPN Client 가이드](./softether_vpn_client_guide.md)
- [VPN 프로토콜 개념](./vpn_protocol_concepts.md)
- [SoftEther 공식 참조 노트](../../_reference/softether_official_notes.md)

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-05

**마지막 업데이트**: 2026-08-05

© 2026 siasia86. Licensed under CC BY 4.0.
