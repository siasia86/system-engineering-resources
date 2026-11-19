# SoftEther VPN 경유 Linux 서버 작업 가이드
<!-- reference: _reference/softether_official_notes.md -->

## 목차

| 섹션                                                                                                                                     |
|------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Ubuntu와 Rocky Linux 차이](#2-ubuntu와-rocky-linux-차이) / [3. 작업 전 점검](#3-작업-전-점검)                   |
| [4. OTP 계정 연결](#4-otp-계정-연결) / [5. IP 할당](#5-ip-할당) / [6. 라우팅](#6-라우팅) / [7. DNS](#7-dns)                              |
| [8. 방화벽·SELinux·rp_filter](#8-방화벽selinuxrp_filter) / [9. VPN 너머 작업](#9-vpn-너머-작업) / [10. 작업 스크립트](#10-작업-스크립트) |
| [11. 작업 종료](#11-작업-종료) / [12. 트러블슈팅](#12-트러블슈팅)                                                                        |

---

## 1. 개요

Ubuntu·Rocky Linux 서버가 SoftEther VPN Client(`vpnclient`)로 VPN에 붙어 사내망 자원에 접근하거나, VPN 쪽에서 그 서버에 들어와 작업하는 절차를 다룹니다. 설치와 vpncmd 기본 명령은 다른 문서에 있으므로 이 문서는 연결된 뒤의 운영 작업에 집중합니다.

| 선행 문서                                                      | 다루는 내용                                                    |
|----------------------------------------------------------------|----------------------------------------------------------------|
| [SoftEther VPN Server 가이드](./softether_vpn_server_guide.md) | 서버 설치, Virtual Hub, SecureNAT, 방화벽                      |
| [SoftEther VPN Client 가이드](./softether_vpn_client_guide.md) | 클라이언트 설치(Ubuntu·Rocky), 가상 NIC·계정 생성, vpncmd 명령 |

### 전제

| 항목                | 이 문서의 예시 값                                        |
|---------------------|----------------------------------------------------------|
| VPN 서버 공인 주소  | `192.0.2.1:443`                                          |
| Virtual Hub / 계정  | `VPN` / `work_vpn` (RADIUS + OTP 인증)                   |
| 가상 NIC            | `vpn0` → 커널 인터페이스 `vpn_vpn0`                      |
| VPN 안 주소         | `192.168.30.50/24` (서버 관리자가 정한 고정 IP라고 가정) |
| 사내망 대역         | `10.20.0.0/16`, 사내 DNS `10.20.0.53`                    |
| 작업자 접속 원본 IP | `198.51.100.25` (공인 IP로 서버에 SSH 접속 중)           |

- `vpnclient`는 `/opt/vpnclient`에 설치되어 있고 NIC은 클라이언트 가이드 4절대로 만들어 두었다고 가정합니다. 계정 생성은 [4절](#계정-생성과-최초-1회-설정)에 있습니다.
- 서버가 443이 아닌 포트로 열려 있으면 계정의 `/SERVER:주소:포트`에 그 포트를 적습니다.
- 명령은 root 권한으로 실행합니다. 일반 계정이면 앞에 `sudo`를 붙입니다.

### 구성

```
작업자 PC ── SSH(공인 IP) ──> 작업 대상 서버 (Ubuntu / Rocky)
                              ├── eth0     : 공인망, 기본 경로 유지
                              └── vpn_vpn0 : vpnclient TAP NIC
                                     |
                                     | Ethernet over HTTPS (TCP 443)
                                     v
                              SoftEther VPN Server (192.0.2.1)
                                     |
                              Virtual Hub ── 사내망 10.20.0.0/16
```

핵심 원칙은 두 가지입니다.

1. 원격 서버의 기본 경로는 바꾸지 않습니다. 사내망 대역만 `vpn_vpn0`으로 보냅니다(Split Tunnel).
2. OTP 계정은 한 번 쓴 패스워드로 다시 접속할 수 없습니다. 자동 재연결·부팅 시 자동 연결을 쓰지 않고, 작업할 때 올리고 끝나면 내립니다.

[⬆ 목차로 돌아가기](#목차)

## 2. Ubuntu와 Rocky Linux 차이

| 항목                 | Ubuntu Server                                                                    | Rocky Linux                                                              |
|----------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 패키지 관리          | `apt`                                                                            | `dnf`                                                                    |
| 기본 네트워크 관리   | netplan + systemd-networkd                                                       | NetworkManager                                                           |
| 수동 DHCP 클라이언트 | 24.04 Server: `dhcpcd`(dhcpcd-base) 기본 설치, `dhclient` 없음. 다른 판은 미확인 | 8·9: `dhclient`(`dhcp-client` 패키지). 10: `dhclient` 제거(RHEL 10 기준) |
| DNS 설정             | systemd-resolved(`resolvectl`)                                                   | NetworkManager가 `/etc/resolv.conf` 관리                                 |
| 방화벽               | ufw (서버 설치 기본 비활성)                                                      | firewalld (기본 활성)                                                    |
| 강제 접근 제어       | AppArmor                                                                         | SELinux (기본 enforcing)                                                 |
| 빌드 의존성          | 클라이언트 가이드 2절                                                            | 클라이언트 가이드 3절                                                    |

- `vpn_vpn0`은 vpnclient가 만드는 TAP 인터페이스라 netplan·NetworkManager 설정 파일에 없습니다. 주소·경로는 `ip` 명령으로 직접 다룹니다.
- Rocky에서 NetworkManager가 `vpn_vpn0`을 관리 대상으로 잡아 주소를 지우거나 바꾸면 관리 대상에서 뺍니다.

```bash
nmcli device status | grep vpn_vpn0
nmcli device set vpn_vpn0 managed no
```

[⬆ 목차로 돌아가기](#목차)

## 3. 작업 전 점검

원격 서버에서 경로를 잘못 건드리면 SSH가 끊기고, OTP 계정이라 VPN도 바로 다시 올릴 수 없습니다. 시작 전에 아래를 확인합니다.

| 점검 항목              | 확인 방법                            | 이유                                                      |
|------------------------|--------------------------------------|-----------------------------------------------------------|
| 콘솔 접근              | 클라우드 콘솔, IPMI·iDRAC 등         | SSH가 끊겼을 때 복구 경로                                 |
| 현재 경로 저장         | `ip route show > /root/route.before` | 원복 기준                                                 |
| 공인망 기본 게이트웨이 | `ip route show default`              | 기본 경로가 `eth0`에 있는지 확인                          |
| 내 SSH 접속 원본       | `echo "$SSH_CLIENT"`                 | 첫 값이 작업자 원본 IP                                    |
| 시간 동기화            | `timedatectl`                        | 로그 대조. OTP 코드 자체는 휴대폰과 RADIUS 서버 시각 기준 |
| tmux·screen            | `tmux new -s work`                   | SSH가 끊겨도 작업 유지                                    |

### 자동 원복 타이머

경로 변경이 잘못되어 접속이 끊길 때를 대비해, 일정 시간 뒤 VPN과 경로를 되돌리는 일회성 타이머를 먼저 걸어 둡니다. [10절 스크립트](#10-작업-스크립트)의 `down`을 호출하는 예입니다.

```bash
# 15분 뒤 VPN 연결 해제와 경로 원복 예약
systemd-run --on-active=15min --unit=vpn-rollback /usr/local/sbin/vpn-work.sh down

# 정상 동작을 확인했으면 예약 취소
systemctl stop vpn-rollback.timer
```

[⬆ 목차로 돌아가기](#목차)

## 4. OTP 계정 연결

서버가 RADIUS + Google Authenticator(TOTP)로 인증하면 패스워드 칸에 `고정 패스워드 + OTP 6자리`를 붙여 넣습니다. 형식은 [클라이언트 가이드의 Google OTP 절](./softether_vpn_client_guide.md#google-otp-totp-연동-서버-접속)과 같습니다.

### OTP 계정에서 달라지는 점

| 기능                                    | 일반 패스워드 계정 | OTP 계정                                                                        |
|-----------------------------------------|--------------------|---------------------------------------------------------------------------------|
| 자동 재연결 (`AccountRetrySet`)         | 무한 재시도 권장   | `/NUM:0` 권장. 저장된 패스워드의 OTP가 이미 만료되어 재시도가 모두 실패         |
| 부팅 시 자동 연결 (`AccountStartupSet`) | 사용 가능          | 사용하지 않음 (같은 이유)                                                       |
| 끊긴 뒤 복구                            | 자동               | 새 OTP로 패스워드를 다시 설정한 뒤 연결                                         |
| 무인 운영                               | 가능               | 사실상 불가. 상시 연결이 필요하면 인증서 인증 등 별도 계정을 서버 관리자와 협의 |
| 같은 계정 동시 접속                     | 서버 정책에 따름   | 같음. 다른 PC에서 같은 계정이 연결 중이면 거부될 수 있음(트러블슈팅 code 20)    |

🟡 실패한 재시도가 반복되면 RADIUS 서버 정책에 따라 계정이 잠길 수 있습니다. 잠금 기준은 서버 관리자에게 확인합니다.

### 계정 생성과 최초 1회 설정

vpncmd 대화 모드로 들어갑니다. 패스워드는 이 단계에서 넣지 않습니다.

```bash
/opt/vpnclient/vpncmd localhost /CLIENT
```

```
VPN Client> AccountCreate work_vpn /SERVER:192.0.2.1:443 /HUB:VPN /USERNAME:otpuser /NICNAME:vpn0
VPN Client> AccountRetrySet work_vpn /NUM:0 /INTERVAL:15
VPN Client> AccountStartupRemove work_vpn
VPN Client> RemoteDisable
```

- `AccountStartupRemove`는 시작 연결로 지정되지 않은 계정이면 오류를 내며, 이 경우 그대로 두면 됩니다.
- `RemoteDisable`은 다른 호스트에서 이 vpnclient를 관리하지 못하게 합니다.

### 서버 인증서 검증

`AccountCreate`로 만든 계정은 서버 인증서 검증이 꺼져 있습니다(`AccountGet`의 `Verify Server Certificate`가 `Disable`). 이 상태에서는 중간에서 서버를 흉내 내도 알 수 없으므로, 서버 인증서를 받아 등록하고 검증을 켭니다. 인증서는 서버 관리자에게 받거나, 이미 연결되는 Windows 클라이언트의 연결 상태 창에서 `Server Certificate`를 열어 파일로 내보냅니다.

```
VPN Client> AccountServerCertSet work_vpn /LOADCERT:/root/vpnserver.cer
VPN Client> AccountServerCertEnable work_vpn
```

### 설정 확인

| 확인 위치                                | 항목                                                                | 기대값                      |
|------------------------------------------|---------------------------------------------------------------------|-----------------------------|
| `AccountGet work_vpn`                    | `Destination VPN Server Host Name`·`Port Number`·`Virtual Hub Name` | 서버 관리자가 준 값         |
| `AccountGet work_vpn`                    | `Authentication Type`                                               | `RADIUS or NT Domain ...`   |
| `AccountGet work_vpn`                    | `Device Name Used for Connection`                                   | `vpn0`                      |
| `AccountGet work_vpn`                    | `Verify Server Certificate`                                         | `Enable`                    |
| `/opt/vpnclient/vpn_client.config`       | `StartupAccount` / `NumRetry` / `AllowRemoteConfig`                 | `false` / `0` / `false`     |
| `ls -l /opt/vpnclient/vpn_client.config` | 권한                                                                | `-rw-------` root           |
| `ss -ltnp`                               | vpnclient 관리 포트 9930                                            | `127.0.0.1:9930`에서만 대기 |

### 연결

```
VPN Client> AccountPasswordSet work_vpn /PASSWORD:SecurePassword123456789 /TYPE:radius
VPN Client> AccountConnect work_vpn
VPN Client> AccountStatusGet work_vpn
```

- OTP 6자리는 유효 시간(30초)이 짧으므로, 새 코드가 뜬 직후 패스워드 설정과 연결을 이어서 실행합니다.
- 같은 계정을 Windows 등 다른 PC에서 쓰고 있으면 그쪽 연결을 먼저 끊습니다. 서버가 같은 사용자의 세션 수를 제한하면 두 번째 연결은 인증 뒤 거부됩니다.
- 패스워드를 셸 명령 인수(`vpncmd ... /CMD AccountPasswordSet ... /PASSWORD:...`)로 넘기면 셸 기록과 프로세스 목록에 남습니다. vpncmd 대화 모드에서 입력하거나 [10절](#10-작업-스크립트)처럼 메모리 파일을 거칩니다.
- vpnclient는 계정 설정을 설치 디렉토리의 `vpn_client.config`에 저장합니다. 파일 권한이 root 전용(`600`)인지 확인합니다.

### 상태 확인 (대화 없이)

vpncmd는 `vpncmd [host] /CLIENT /CMD <명령>` 형식으로 명령 하나를 실행하고 끝납니다(공식 문서 6.2절의 형식을 클라이언트 관리 모드에 적용).

```bash
/opt/vpnclient/vpncmd localhost /CLIENT /CMD AccountStatusGet work_vpn
/opt/vpnclient/vpncmd localhost /CLIENT /CMD AccountList
```

[⬆ 목차로 돌아가기](#목차)

## 5. IP 할당

### 고정 IP (원격 서버 권장)

SecureNAT나 사내 DHCP가 보내는 기본 게이트웨이 옵션을 받으면 `vpn_vpn0`으로 기본 경로가 추가되어, 공인 IP로 들어온 SSH의 응답이 VPN 쪽으로 나가며 끊길 수 있습니다. 원격 서버는 서버 관리자에게 VPN 안 주소를 받아 게이트웨이 없이 설정합니다.

```bash
ip addr add 192.168.30.50/24 dev vpn_vpn0
ip link set vpn_vpn0 up
```

### DHCP

DHCP를 써야 하면 [자동 원복 타이머](#자동-원복-타이머)를 걸어 둔 상태에서 실행하고, 받은 직후 기본 경로를 확인합니다.

| 배포판    | 명령                                       | 비고                                                                |
|-----------|--------------------------------------------|---------------------------------------------------------------------|
| Ubuntu    | `dhcpcd vpn_vpn0` 또는 `dhclient vpn_vpn0` | 없으면 `apt install dhcpcd-base` 또는 `apt install isc-dhcp-client` |
| Rocky 8·9 | `dhclient vpn_vpn0`                        | 없으면 `dnf install dhcp-client`                                    |
| Rocky 10  | 고정 IP 사용                               | `dhclient` 제거. 대체 DHCP 클라이언트의 패키지 저장소는 미확인      |

`dhcpcd`는 옵션을 주지 않으면 기본 경로와 DNS·hostname·시간 서버 설정까지 바꿉니다. 원격 서버에서는 주소만 받도록 실행합니다.

```bash
# 기본 경로(-G)와 DNS·hostname·NTP 훅(-C)을 쓰지 않음
dhcpcd -4 -G -t 30 -C resolv.conf -C hostname -C ntp.conf -C timesyncd.conf vpn_vpn0

# 받은 값 확인 (서버가 보낸 경로 옵션 포함)
dhcpcd -4 -U vpn_vpn0

# VPN 쪽 기본 경로가 생겼는지 확인, 생겼으면 그것만 제거 (eth0 기본 경로는 유지)
ip route show default
ip route del default dev vpn_vpn0

# 작업 끝: 주소 반납과 dhcpcd 종료
dhcpcd -k vpn_vpn0
```

### 서버가 내려 주는 경로

VPN 쪽 DHCP 서버(SecureNAT 등)는 사내 대역 경로를 classless static route로 보낼 수 있습니다. 형식은 RFC 3442(`classless_static_routes`, option 121)와 Microsoft(`ms_classless_static_routes`, option 249) 두 가지이며, 서버가 둘 중 하나나 둘 다를 보내면 dhcpcd는 받은 경로를 `vpn_vpn0`에 추가합니다. `dhcpcd -U` 출력에 `classless_static_routes=` 줄이 있으면 받은 것입니다.

| 상황                                          | 처리                                                                                                               |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| 받은 대역이 작업 대상이고 서버 대역과 안 겹침 | 그대로 사용                                                                                                        |
| 받은 대역이 서버의 기존 대역·관리 경로와 겹침 | `-O classless_static_routes -O ms_classless_static_routes`를 붙여 받지 않고, 필요한 대역만 [6절](#6-라우팅)로 추가 |

- 서버가 두 형식을 모두 보내면 하나만 막아도 다른 형식으로 같은 경로가 들어오므로 둘 다 막습니다.
- 🟡 dhcpcd가 이미 그 인터페이스에서 실행 중일 때 시험 모드(`dhcpcd -T vpn_vpn0`)를 실행하면 기존 주소와 경로가 지워질 수 있습니다. 실행 중인 dhcpcd가 있으면 `dhcpcd -U`로 값을 보고, 주소가 지워졌으면 `dhcpcd -n vpn_vpn0`으로 다시 받습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 라우팅

### Split Tunnel

사내망 대역만 VPN으로 보냅니다. 대역을 더 넓히지 말고 실제 작업에 필요한 범위만 추가합니다.

```bash
ip route add 10.20.0.0/16 dev vpn_vpn0
```

VPN 안에 게이트웨이가 따로 있으면 경유지를 지정합니다.

```bash
ip route add 10.20.0.0/16 via 192.168.30.1 dev vpn_vpn0
```

### 확인

```bash
ip route get 10.20.0.10        # dev vpn_vpn0 이어야 함
ip route get 198.51.100.25     # 작업자 원본 IP: dev eth0 이어야 함
```

### Full Tunnel이 필요한 경우

모든 트래픽을 VPN으로 보내야 하면, 기본 경로를 바꾸기 전에 VPN 서버와 작업자 원본 IP를 기존 게이트웨이로 고정합니다. 하나라도 빠지면 VPN 또는 SSH가 끊깁니다.

```bash
GW=$(ip route show default | awk '/via/{print $3; exit}')
ip route add 192.0.2.1/32 via "$GW"          # VPN 서버
ip route add 198.51.100.25/32 via "$GW"      # 작업자 원본 IP (SSH 유지)
ip route replace default dev vpn_vpn0
```

🟡 다른 관리 경로(모니터링, 백업, 배포 서버)도 공인망으로 들어오면 같은 방식으로 고정해야 합니다. 원격 서버에서는 Split Tunnel을 우선합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. DNS

사내 호스트 이름을 써야 할 때만 설정합니다.

### Ubuntu (systemd-resolved)

사내 도메인만 사내 DNS로 보내고 나머지는 기존 DNS를 씁니다. 연결을 내리면 설정도 사라집니다.

```bash
resolvectl dns vpn_vpn0 10.20.0.53
resolvectl domain vpn_vpn0 '~corp.example'
resolvectl status vpn_vpn0
```

### Rocky Linux

NetworkManager가 `/etc/resolv.conf`를 관리하므로 직접 고치면 덮어써집니다. 작업 범위가 좁으면 아래 방법 중 하나를 씁니다.

| 방법         | 예                                  | 비고         |
|--------------|-------------------------------------|--------------|
| 직접 질의    | `dig @10.20.0.53 db01.corp.example` | 이름 확인용  |
| `/etc/hosts` | `10.20.0.21 db01.corp.example`      | 작업 후 삭제 |
| IP로 접속    | `ssh 10.20.0.21`                    | 가장 단순    |

[⬆ 목차로 돌아가기](#목차)

## 8. 방화벽·SELinux·rp_filter

vpnclient가 서버로 나가는 연결(TCP 443 등)은 보통 기본 정책에서 허용됩니다. 막히는 것은 주로 VPN 쪽에서 이 서버로 들어오는 연결입니다.

### Ubuntu (ufw)

```bash
ufw status verbose
# VPN 쪽에서 SSH만 허용
ufw allow in on vpn_vpn0 to any port 22 proto tcp
```

### Rocky Linux (firewalld)

`vpn_vpn0`을 SSH만 여는 전용 zone에 넣습니다. `trusted` zone은 모든 연결을 허용하므로 쓰지 않습니다.

```bash
firewall-cmd --permanent --new-zone=vpn
firewall-cmd --permanent --zone=vpn --add-service=ssh
firewall-cmd --permanent --zone=vpn --add-interface=vpn_vpn0
firewall-cmd --reload
firewall-cmd --get-active-zones
```

### SELinux (Rocky)

`/opt/vpnclient`의 바이너리를 systemd나 root 셸에서 실행하면 보통 차단되지 않습니다. 연결이나 NIC 생성이 원인 없이 실패하면 거부 기록을 먼저 확인합니다.

```bash
getenforce
ausearch -m avc -ts recent | grep -i vpn
```

### rp_filter

엄격 모드(`1`)에서는 들어온 인터페이스와 그 원본으로 가는 경로가 다르면 패킷을 버립니다. Split Tunnel에서 VPN 쪽 원본 대역에 경로가 없으면 요청이 조용히 사라집니다. 기본값은 배포판과 판마다 다르므로 실제 값을 확인합니다.

```bash
sysctl net.ipv4.conf.all.rp_filter net.ipv4.conf.vpn_vpn0.rp_filter

# 해당 원본 대역을 vpn_vpn0 경로로 추가하는 것이 우선. 불가하면 vpn_vpn0만 느슨한 모드(2)
sysctl -w net.ipv4.conf.vpn_vpn0.rp_filter=2
```

커널은 `all`과 인터페이스 값 중 큰 값을 적용하므로, `all`이 `1`이고 인터페이스가 `2`이면 `2`가 적용됩니다.

### ARP 응답 범위

Linux 기본값(`arp_ignore=0`)은 어느 인터페이스로 들어온 ARP 요청이든 자기 주소면 답합니다. VPN 쪽 장비가 서버의 `eth0` 주소를 물으면 `vpn_vpn0`으로 답해, VPN 쪽에 서버의 공인망 주소가 알려지고 응답이 터널로 돌아올 수 있습니다. `vpn_vpn0`에서는 자기 주소에 대한 요청에만 답하게 합니다.

```bash
sysctl net.ipv4.conf.all.arp_ignore net.ipv4.conf.vpn_vpn0.arp_ignore

# vpn_vpn0: 그 인터페이스 주소에 대한 요청만 응답, 보낼 때도 그 인터페이스 주소 사용
sysctl -w net.ipv4.conf.vpn_vpn0.arp_ignore=1
sysctl -w net.ipv4.conf.vpn_vpn0.arp_announce=2
```

`arp_ignore`·`arp_announce`도 `all`과 인터페이스 값 중 큰 값을 씁니다. vpnclient를 다시 시작하거나 NIC을 다시 만들면 `vpn_vpn0` 값이 초기화될 수 있으므로 [작업 스크립트](#10-작업-스크립트)에서 연결할 때마다 설정합니다.

### UDP 가속

vpnclient는 TCP로 연결한 뒤 서버와 UDP 가속을 시도하며, 서버가 알려 준 다른 주소(서버의 사설 주소 등)로도 UDP를 보낼 수 있습니다. 서버가 내려 준 경로에 그 주소가 들어 있으면 이 UDP가 서버의 `eth0` 원본 주소를 단 채 터널로 들어갑니다. `AccountStatusGet`의 `UDP Acceleration is Active`가 `No`이면 TCP로만 동작하는 것이며 연결 자체에는 문제가 없습니다. vpncmd에는 이 기능을 끄는 명령이 없고, 설정 파일의 `NoUdpAcceleration` 항목을 바꾸는 방법은 이 문서에서 확인하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

## 9. VPN 너머 작업

### SSH

OTP 계정은 끊기면 바로 다시 붙지 못하므로, VPN 너머 서버에서도 tmux·screen 안에서 작업합니다.

```bash
ssh -o ServerAliveInterval=30 admin@10.20.0.21
```

여러 단계를 거치면 `~/.ssh/config`에 경유지를 둡니다.

```
Host corp-bastion
    HostName 10.20.0.10
    User admin

Host corp-db01
    HostName 10.20.0.21
    User admin
    ProxyJump corp-bastion
```

SSH 설정 강화는 [SSH 보안](../../04_security/hardening/ssh_security.md)을 참고합니다.

### 파일 전송

끊겨도 이어받을 수 있게 `rsync`를 씁니다.

```bash
rsync -avP --partial ./release.tar.gz admin@10.20.0.21:/srv/deploy/
```

### 사내 패키지 저장소·프록시

사내 미러나 프록시를 VPN으로만 쓸 수 있으면 작업 동안만 설정하고 끝나면 지웁니다.

| 배포판 | 설정 파일                         | 내용                                             |
|--------|-----------------------------------|--------------------------------------------------|
| Ubuntu | `/etc/apt/apt.conf.d/95vpn-proxy` | `Acquire::http::Proxy "http://10.20.0.30:3128";` |
| Rocky  | `/etc/dnf/dnf.conf` (`[main]`)    | `proxy=http://10.20.0.30:3128`                   |

### MTU

ping은 되는데 SSH 로그인 직후나 큰 파일 전송에서 멈추면 캡슐화로 경로 MTU가 줄어든 경우가 많습니다. DF를 켠 ping으로 최대 크기를 찾고([MTU·MSS·PMTUD 6.2절](./mtu_mss_pmtud.md#62-df를-켠-ping으로-최대-크기-찾기)), 필요하면 `vpn_vpn0`의 MTU를 낮춥니다.

```bash
ping -M do -s 1372 -c 3 10.20.0.21     # 1372 + 28 = 1400
ip link set vpn_vpn0 mtu 1400
```

[⬆ 목차로 돌아가기](#목차)

## 10. 작업 스크립트

연결 올리기·내리기·확인을 한 스크립트로 묶은 예입니다. OTP는 실행할 때 입력받고, 패스워드는 셸 기록·프로세스 인수에 남지 않도록 메모리 파일(`/dev/shm`)을 거쳐 vpncmd `/IN`으로 넘긴 뒤 바로 지웁니다.

```bash
#!/usr/bin/env bash
# vpn-work.sh — OTP 계정으로 SoftEther VPN 작업 연결을 올리고 내림
# 사용: vpn-work.sh up | down | status
set -euo pipefail

VPNCMD=/opt/vpnclient/vpncmd
ACCOUNT=work_vpn
NIC=vpn_vpn0
VPN_ADDR=192.168.30.50/24       # 서버 관리자에게 받은 고정 IP, DHCP면 dhcp
ROUTES=(10.20.0.0/16)           # VPN으로 보낼 대역
# DHCP: 기본 경로·DNS·hostname·NTP를 받지 않음
# 서버가 내려 주는 경로도 막으려면 -O classless_static_routes -O ms_classless_static_routes 추가
DHCPCD_OPTS=(-4 -G -t 30 -C resolv.conf -C hostname -C ntp.conf -C timesyncd.conf)
TMP_IN=""

trap 'rm -f "${TMP_IN}"' EXIT

log() { printf '%s %s\n' "$(date '+%F %T')" "$*"; }
vcmd() { "${VPNCMD}" localhost /CLIENT /CMD "$@"; }

up() {
    local fixed otp i
    read -rsp '고정 패스워드: ' fixed; echo
    read -rsp 'OTP 6자리: ' otp; echo

    TMP_IN=$(mktemp -p /dev/shm vpnin.XXXXXX)   # 권한 600, 메모리에만 기록
    printf 'AccountPasswordSet %s /PASSWORD:%s /TYPE:radius\nAccountConnect %s\n' \
        "${ACCOUNT}" "${fixed}${otp}" "${ACCOUNT}" > "${TMP_IN}"
    unset fixed otp
    "${VPNCMD}" localhost /CLIENT /IN:"${TMP_IN}" > /dev/null
    rm -f "${TMP_IN}"

    for i in $(seq 1 30); do
        if vcmd AccountStatusGet "${ACCOUNT}" | grep -q 'Session Established'; then
            break
        fi
        if [[ ${i} -eq 30 ]]; then
            log "연결 실패: AccountStatusGet 확인"; exit 1
        fi
        sleep 1
    done

    sysctl -qw "net.ipv4.conf.${NIC}.arp_ignore=1" "net.ipv4.conf.${NIC}.arp_announce=2"
    ip link set "${NIC}" up
    if [[ "${VPN_ADDR}" == dhcp ]]; then
        dhcpcd "${DHCPCD_OPTS[@]}" "${NIC}" || { log "DHCP 주소 받기 실패"; exit 1; }
        ip route del default dev "${NIC}" 2> /dev/null || true   # 안전장치
    else
        ip addr replace "${VPN_ADDR}" dev "${NIC}"
    fi
    ip -brief addr show "${NIC}"
    for r in "${ROUTES[@]}"; do
        ip route replace "${r}" dev "${NIC}"
    done
    log "연결 완료"
    ip route show dev "${NIC}"
}

down() {
    if [[ "${VPN_ADDR}" == dhcp ]]; then
        dhcpcd -k "${NIC}" > /dev/null 2>&1 || true
    fi
    vcmd AccountDisconnect "${ACCOUNT}" > /dev/null || true
    for r in "${ROUTES[@]}"; do
        ip route del "${r}" dev "${NIC}" 2> /dev/null || true
    done
    ip addr flush dev "${NIC}" 2> /dev/null || true
    log "연결 해제"
}

status() {
    vcmd AccountStatusGet "${ACCOUNT}" | grep -E 'Status|Server Name|Port' || true
    ip -brief addr show "${NIC}" || true
    ip route show dev "${NIC}" || true
}

case "${1:-}" in
    up) up ;;
    down) down ;;
    status) status ;;
    *) echo "사용: $0 up|down|status" >&2; exit 2 ;;
esac
```

```bash
install -m 700 vpn-work.sh /usr/local/sbin/vpn-work.sh
vpn-work.sh up
```

- `Session Established`는 `AccountStatusGet` 출력의 세션 상태 문자열입니다. 4.44 Build 9807에서는 `Connection Completed (Session Established)`로 나옵니다. 판에 따라 문구가 다르면 실제 출력에 맞춰 고칩니다.
- `VPN_ADDR=dhcp`이면 `dhcpcd`가 주소를 받고 `down`에서 반납합니다. 처음에는 `ROUTES`를 VPN 대역(예: `192.168.30.0/24`)만 두고, 서버가 내려 준 경로를 [5절](#서버가-내려-주는-경로)대로 확인한 뒤 필요한 대역을 더합니다.
- 고정 IP·대역 값을 정하기 전에는 실행되지 않게, 설치할 때 두 값을 `CHANGE_ME`로 두고 `case` 앞에서 그 값이면 종료하는 검사를 넣어 두면 안전합니다.
- `/dev/shm` 파일도 실행 중에는 root가 읽을 수 있습니다. 공용 서버라면 vpncmd 대화 모드에서 직접 입력하는 편이 낫습니다.
- `vpnclient` 서비스 자체는 [클라이언트 가이드 6절](./softether_vpn_client_guide.md#6-systemd-서비스-등록)처럼 systemd로 띄워 두고, 이 스크립트는 계정 연결만 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 11. 작업 종료

연결을 내리는 것만으로는 경로·DNS·프록시 설정이 남을 수 있습니다. 아래 순서로 원상태를 확인합니다.

```bash
vpn-work.sh down                         # 또는 vpncmd에서 AccountDisconnect work_vpn
systemctl stop vpn-rollback.timer 2> /dev/null || true

ip route show > /root/route.after
diff /root/route.before /root/route.after   # 차이가 없어야 함
pgrep -a dhcpcd                             # DHCP를 썼다면 vpn_vpn0용 dhcpcd가 없어야 함
```

| 확인 항목     | 원상태                                                         |
|---------------|----------------------------------------------------------------|
| 경로          | `route.before`와 같음                                          |
| DNS (Ubuntu)  | `resolvectl status vpn_vpn0`에 사내 DNS 없음                   |
| `/etc/hosts`  | 작업 중 추가한 줄 삭제                                         |
| 패키지 프록시 | `95vpn-proxy` 삭제, `dnf.conf`의 `proxy=` 삭제                 |
| 방화벽        | 상시 VPN 접속이 필요 없으면 ufw 규칙·firewalld `vpn` zone 정리 |
| 셸 기록       | 패스워드가 남지 않았는지 `history` 확인                        |

[⬆ 목차로 돌아가기](#목차)

## 12. 트러블슈팅

| 증상                                                  | 원인                                         | 조치                                                                                                      |
|-------------------------------------------------------|----------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| 연결 직후 공인 IP로 들어온 SSH가 끊김                 | DHCP가 `vpn_vpn0`으로 기본 경로를 추가       | 콘솔에서 `ip route del default dev vpn_vpn0`, 이후 고정 IP 사용                                           |
| 처음 연결에서 인증 실패                               | OTP 만료, 형식 오류, `/TYPE:standard` 사용   | 새 코드로 즉시 재설정, `/TYPE:radius` 확인, 형식은 서버 관리자에게 확인                                   |
| 로그에 `too many sessions by the same user (code 20)` | 같은 계정이 다른 PC(예: Windows)에서 연결 중 | 그쪽 연결을 끊고 새 OTP로 다시 연결. 동시 사용이 필요하면 서버 관리자에게 세션 수 조정이나 별도 계정 요청 |
| 연결 뒤 예상하지 않은 대역 경로가 생김                | DHCP classless static route 수신             | `dhcpcd -4 -U vpn_vpn0`로 확인, [5절](#서버가-내려-주는-경로)                                             |
| `dhcpcd -T` 뒤 `vpn_vpn0` 주소가 사라짐               | 실행 중인 dhcpcd와 시험 모드 충돌            | `dhcpcd -n vpn_vpn0`으로 다시 받기                                                                        |
| 끊긴 뒤 재연결이 계속 실패, 계정 잠김                 | 만료된 OTP로 자동 재시도 반복                | `AccountRetrySet /NUM:0`, 잠금 해제는 서버 관리자에게 요청                                                |
| 재부팅 후 혼자 연결을 시도하다 실패                   | `AccountStartupSet` 남아 있음                | `AccountStartupRemove work_vpn`                                                                           |
| `dhclient: command not found`                         | Rocky 10 제거, Ubuntu 미설치                 | 고정 IP 사용 또는 [5절](#5-ip-할당) 표대로 설치                                                           |
| 주소를 넣었는데 곧 사라짐 (Rocky)                     | NetworkManager가 인터페이스 관리             | `nmcli device set vpn_vpn0 managed no`                                                                    |
| 사내 호스트 이름 해석 안 됨                           | DNS 미설정                                   | [7절](#7-dns)                                                                                             |
| VPN 쪽에서 이 서버로 SSH 안 됨 (Rocky)                | firewalld zone 미지정                        | [8절](#rocky-linux-firewalld) `vpn` zone                                                                  |
| 요청은 들어오는데 응답이 없음                         | rp_filter 엄격 모드와 비대칭 경로            | 원본 대역 경로 추가 또는 `vpn_vpn0` rp_filter `2`                                                         |
| ping은 되는데 SSH·scp가 멈춤                          | 경로 MTU 감소                                | [9절 MTU](#mtu)                                                                                           |
| vpncmd 접속 불가                                      | vpnclient 미실행                             | `systemctl status vpnclient`, 클라이언트 가이드 8절                                                       |

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- vpncmd 일반 사용법(명령줄 형식, `/CLIENT`·`/IN`·`/CMD`): [softether.org 6.2](https://www.softether.org/4-docs/1-manual/6._Command_Line_Management_Utility_Manual/6.2_General_Usage_of_vpncmd) — ★★★☆☆
- vpncmd VPN Client 명령 레퍼런스(`AccountStartupSet`·`AccountStartupRemove`·`AccountRetrySet`): [softether.org 6.5](https://www.softether.org/4-docs/1-manual/6._Command_Line_Management_Utility_Manual/6.5_VPN_Client_Management_Command_Reference) — ★★★☆☆
- RHEL 10 `dhclient` 제거: [Considerations in adopting RHEL 10 — Networking](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/considerations_in_adopting_rhel_10/networking) — ★★★☆☆
- Ubuntu DHCP 클라이언트 전환 논의: [Launchpad bug 2024164](https://bugs.launchpad.net/bugs/2024164) — ★★☆☆☆
- rp_filter 동작: [Linux kernel ip-sysctl](https://docs.kernel.org/networking/ip-sysctl.html) — ★★★☆☆
- systemd-run 타이머: [systemd-run(1)](https://www.freedesktop.org/software/systemd/man/latest/systemd-run.html) — ★★★☆☆

확인일: 2026-11-18. 이 문서의 명령은 공식 문서 대조로 작성했으며 실제 Ubuntu·Rocky 서버에서 실행해 보지는 않았습니다.

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-18

**마지막 업데이트**: 2026-11-19

© 2026 siasia86. Licensed under CC BY 4.0.
