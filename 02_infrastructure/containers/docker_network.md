# Docker 네트워크

Docker 컨테이너가 서로, 그리고 호스트·외부와 통신하는 방식(네트워크 드라이버)을 다룹니다. 이 문서만으로 드라이버 선택 → 네트워크 만들기 → 연결 확인까지 따라 할 수 있게 썼고, 많이 쓰는 bridge와 macvlan을 중심으로 합니다.

- 기준 판: Docker Engine 29.x
- 예제 시험: 2026-11-23, Docker Engine 29.8.1에서 3·4·5절과 9절 1~6번을 실행해 결과를 확인. 7절 macvlan은 호스트 네트워크 인터페이스를 바꾸므로 시험하지 않았고 공식 문서와 대조

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 준비](#2-준비) / [3. bridge](#3-bridge)                                                 |
| [4. 네트워크 명령](#4-네트워크-명령) / [5. 포트 공개](#5-포트-공개) / [6. Compose에서 쓰기](#6-compose에서-쓰기) |
| [7. macvlan](#7-macvlan) / [8. 그 밖의 드라이버](#8-그-밖의-드라이버) / [9. 검증](#9-검증)                       |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                             |

---

## 1. 개요

| 드라이버  | 컨테이너 IP               | 외부 → 컨테이너      | 호스트 → 컨테이너 | 주 용도                                  |
|-----------|---------------------------|----------------------|-------------------|------------------------------------------|
| `bridge`  | 내부 사설 대역 (NAT)      | 포트 공개(`-p`) 필요 | 가능              | 기본값. 한 호스트 안의 서비스            |
| `host`    | 호스트 IP를 그대로 사용   | 호스트 포트로 바로   | 가능              | 성능 우선, 포트 격리 불필요              |
| `none`    | 없음 (`lo`만)             | 불가                 | 불가              | 완전 격리, 일괄 처리 작업                |
| `macvlan` | 물리 네트워크 대역 IP     | 컨테이너 IP로 바로   | 기본 불가 (7-5)   | 컨테이너를 물리 네트워크의 장비처럼 노출 |
| `ipvlan`  | 물리 네트워크 대역 IP     | 컨테이너 IP로 바로   | 기본 불가         | MAC 수가 제한된 환경 (클라우드 VM 등)    |
| `overlay` | 여러 호스트에 걸친 가상망 | 포트 공개 필요       | 가능              | Swarm 등 여러 호스트 클러스터            |

고르는 기준:

- 한 호스트 안에서 서비스끼리 통신하고 일부 포트만 열면 된다 → 사용자 정의 `bridge` (3절)
- 외부 PC가 컨테이너를 별도 IP로 직접 접속해야 한다 → `macvlan` (7절), MAC 제한이 있으면 `ipvlan`
- 네트워크가 아예 필요 없다 → `none`

[⬆ 목차로 돌아가기](#목차)

---

## 2. 준비

Docker Engine만 있으면 되며 따로 설치할 것은 없습니다. 설치 직후에는 기본 네트워크 3개가 있습니다.

```bash
docker network ls
# NETWORK ID     NAME      DRIVER    SCOPE
# ...            bridge    bridge    local
# ...            host      host      local
# ...            none      null      local
```

macvlan을 쓰려면 호스트의 물리 인터페이스 이름(예: `eth0`, `ens18`)과 그 네트워크의 대역·게이트웨이를 알아야 합니다.

```bash
ip -br addr          # 인터페이스 이름과 IP
ip route | grep default   # 기본 게이트웨이
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. bridge

### 3-1. 기본 bridge와 사용자 정의 bridge

`--network`를 지정하지 않은 컨테이너는 기본 `bridge`에 붙습니다. 기본 bridge에서는 컨테이너 이름으로 서로 찾을 수 없으므로, 서비스끼리 통신할 때는 사용자 정의 bridge를 만듭니다.

| 항목              | 기본 `bridge`                      | 사용자 정의 bridge                    |
|-------------------|------------------------------------|---------------------------------------|
| 만드는 방법       | 자동                               | `docker network create <이름>`        |
| 이름으로 찾기     | 불가 (`bad address`)               | 컨테이너 이름·별칭으로 가능           |
| DNS               | 호스트의 resolv.conf 복사          | 내장 DNS `127.0.0.11`                 |
| 격리              | 기본 bridge의 모든 컨테이너        | 같은 네트워크에 붙은 컨테이너끼리만   |
| 실행 중 연결·해제 | 떼려면 컨테이너를 다시 만들어야 함 | `docker network connect`·`disconnect` |

### 3-2. 따라 하기

```bash
docker network create appnet

docker run -d --name web --network appnet nginx:1.29-alpine
docker run --rm --network appnet busybox:1.37 ping -c 1 web    # 이름으로 응답

docker run -d --name lone busybox:1.37 sleep 300                # 기본 bridge
docker run --rm busybox:1.37 ping -c 1 lone                     # ping: bad address 'lone'
```

### 3-3. 대역 지정과 내부 전용 네트워크

```bash
# 대역·게이트웨이 지정 (사내 대역과 겹치지 않게)
docker network create --subnet 172.30.0.0/24 --gateway 172.30.0.1 appnet2

# 외부로 나가지 못하는 내부 전용 네트워크 (DB 등)
docker network create --internal backend
docker run --rm --network backend busybox:1.37 ping -c 1 1.1.1.1
# ping: sendto: Network is unreachable
```

Docker가 자동으로 고르는 `172.17.0.0/16` 이후 대역이 사내망·VPN 대역과 겹치면 통신이 끊깁니다. 이때는 대역을 직접 지정하거나 `/etc/docker/daemon.json`의 `default-address-pools`로 자동 대역을 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 네트워크 명령

| 목적             | 명령                                                                                             |
|------------------|--------------------------------------------------------------------------------------------------|
| 목록             | `docker network ls`                                                                              |
| 만들기           | `docker network create [-d 드라이버] <이름>`                                                     |
| 상세 (대역·연결) | `docker network inspect <이름>`                                                                  |
| 대역만 보기      | `docker network inspect <이름> --format '{{range .IPAM.Config}}{{.Subnet}} {{.Gateway}}{{end}}'` |
| 실행 중 연결     | `docker network connect <네트워크> <컨테이너>`                                                   |
| 별칭을 붙여 연결 | `docker network connect --alias db <네트워크> <컨테이너>`                                        |
| 연결 해제        | `docker network disconnect <네트워크> <컨테이너>`                                                |
| 지우기           | `docker network rm <이름>` (연결된 컨테이너가 없어야 함)                                         |
| 안 쓰는 것 정리  | `docker network prune`                                                                           |
| 실행 시 지정     | `docker run --network <이름> --network-alias <별칭> ...`                                         |

컨테이너 하나를 여러 네트워크에 붙일 수 있습니다. 예를 들어 웹 서버를 `frontend`와 `backend` 둘 다에 붙이고 DB는 `backend`에만 두면, 외부에서 DB로 가는 길이 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 포트 공개

bridge 네트워크의 컨테이너는 포트를 공개해야 외부에서 접속할 수 있습니다.

| 표기                    | 열리는 곳                              |
|-------------------------|----------------------------------------|
| `-p 8080:80`            | 호스트의 모든 주소 8080 → 컨테이너 80  |
| `-p 127.0.0.1:8080:80`  | 호스트 자신만 (외부 접속 불가)         |
| `-p 192.0.2.10:8080:80` | 지정한 호스트 주소만                   |
| `-p 8080:80/udp`        | UDP                                    |
| `-P`                    | Dockerfile `EXPOSE` 포트를 임의 포트로 |

```bash
docker run -d --name web2 -p 127.0.0.1:8080:80 nginx:1.29-alpine
docker port web2          # 80/tcp -> 127.0.0.1:8080
ss -tlnp | grep 8080      # 127.0.0.1:8080 에서만 대기
```

Docker는 포트를 공개할 때 iptables(nftables) 규칙을 직접 넣으므로, ufw·firewalld로 막아 둔 포트도 `-p`로 공개하면 열릴 수 있습니다. 외부에 열 필요가 없는 포트는 공개하지 않거나 `127.0.0.1:`을 붙입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Compose에서 쓰기

Compose는 프로젝트마다 `<프로젝트>_default` 사용자 정의 bridge를 만들어 서비스를 붙이므로, 서비스 이름으로 서로 찾습니다. 네트워크를 나누거나 대역·고정 IP가 필요할 때 `networks:`를 씁니다.

```yaml
services:
  web:
    image: nginx:1.29-alpine
    ports:
      - "80:80"
    networks: [frontend, backend]
  db:
    image: postgres:17-alpine
    networks:
      backend:
        ipv4_address: 172.30.1.10      # 고정 IP (ipam 대역 안)

networks:
  frontend: {}
  backend:
    internal: true                     # 외부로 나가지 못함
    ipam:
      config:
        - subnet: 172.30.1.0/24
          gateway: 172.30.1.1
```

```bash
docker network ls --filter name=<프로젝트>          # <프로젝트>_frontend, <프로젝트>_backend
docker network inspect <프로젝트>_backend           # 연결된 컨테이너와 IP
docker compose up -d --force-recreate               # 네트워크 설정을 바꾼 뒤 다시 만듦
```

Compose 자체의 사용법은 [함께 보기](#함께-보기)의 Docker Compose 문서에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. macvlan

### 7-1. 개념

컨테이너마다 고유한 MAC 주소를 주고 호스트의 물리 인터페이스에 직접 붙입니다. 외부 PC는 포트 공개 없이 컨테이너 IP로 바로 접속합니다.

```
physical switch (gateway 192.0.2.1)
    │
    eth0 (host IP: 192.0.2.10)
    │
    macvlan
    ├── container-a  192.0.2.151     ← reachable directly from external PCs
    ├── container-b  192.0.2.152
    └── container-c  192.0.2.153
```

호스트 `eth0`와 컨테이너는 같은 물리 대역(`192.0.2.0/24`)에 있습니다.

### 7-2. 사전 조건

| 항목            | 내용                                                                     |
|-----------------|--------------------------------------------------------------------------|
| 스위치·네트워크 | 한 포트에 여러 MAC을 허용해야 함 (포트 보안으로 MAC 수를 제한하면 실패)  |
| 가상 머신       | 하이퍼바이저에서 MAC 주소 변경(스푸핑) 허용 필요                         |
| IP 대역         | DHCP 서버가 나눠 주는 범위와 겹치지 않는 범위를 컨테이너용으로 따로 비움 |
| 클라우드 VM     | 대부분 등록되지 않은 MAC을 막으므로 macvlan 대신 ipvlan 검토             |

Hyper-V 가상 머신이면 Hyper-V 호스트의 PowerShell(관리자)에서 MAC 스푸핑을 켭니다.

```powershell
Get-VMNetworkAdapter -VMName "<VM 이름>" | Set-VMNetworkAdapter -MacAddressSpoofing On
Get-VMNetworkAdapter -VMName "<VM 이름>" | Select-Object VMName, MacAddressSpoofing
```

### 7-3. 만들기

```bash
docker network create -d macvlan \
  --subnet 192.0.2.0/24 \
  --gateway 192.0.2.1 \
  --ip-range 192.0.2.144/29 \
  -o parent=eth0 \
  lan

docker run -d --name app --network lan --ip 192.0.2.151 nginx:1.29-alpine
```

Compose로 쓸 때:

```yaml
services:
  app:
    image: nginx:1.29-alpine
    networks:
      lan:
        ipv4_address: 192.0.2.151

networks:
  lan:
    driver: macvlan
    driver_opts:
      parent: eth0                 # 호스트 물리 인터페이스
    ipam:
      config:
        - subnet: 192.0.2.0/24
          gateway: 192.0.2.1
          ip_range: 192.0.2.144/29 # 자동 할당 범위
```

### 7-4. ip_range 계산

`ip_range`는 CIDR 블록이어야 하므로 시작 주소가 블록 크기의 배수여야 합니다.

| 원하는 범위 | ip_range         | 개수 |
|-------------|------------------|------|
| .144 ~ .151 | `192.0.2.144/29` | 8    |
| .144 ~ .159 | `192.0.2.144/28` | 16   |
| .160 ~ .175 | `192.0.2.160/28` | 16   |
| .128 ~ .159 | `192.0.2.128/27` | 32   |

`--ip`·`ipv4_address`로 고정한 주소는 `ip_range` 밖이어도 `subnet` 안이면 됩니다. 다만 다른 장비와 겹치지 않는지는 직접 확인해야 합니다.

### 7-5. 호스트에서 컨테이너로 접속하기

macvlan에서는 호스트 자신이 자기 macvlan 컨테이너에 접속하지 못합니다(외부 PC는 가능). 호스트에서도 접속해야 하면 호스트에 macvlan 인터페이스를 하나 더 만들어 그 경로로 보냅니다.

```bash
sudo ip link add lan-shim link eth0 type macvlan mode bridge
sudo ip addr add 192.0.2.200/32 dev lan-shim       # 컨테이너 범위 밖의 빈 주소
sudo ip link set lan-shim up
sudo ip route add 192.0.2.144/29 dev lan-shim      # 컨테이너 범위로 가는 경로
```

이 설정은 재부팅하면 사라집니다. 계속 쓰려면 netplan·NetworkManager·systemd-networkd 설정에 같은 내용을 넣습니다. 호스트에서 컨테이너 안 명령만 실행하면 된다면 `docker exec`(Ansible은 `community.docker.docker` 연결)로 충분하므로 이 설정이 필요 없습니다.

### 7-6. macvlan과 ipvlan

| 항목            | macvlan                          | ipvlan (L2 모드)           |
|-----------------|----------------------------------|----------------------------|
| MAC 주소        | 컨테이너마다 고유                | 호스트 MAC 공유            |
| VM MAC 스푸핑   | 필요                             | 불필요                     |
| 스위치 MAC 제한 | 걸릴 수 있음                     | 걸리지 않음                |
| DHCP 예약       | MAC 기준 예약 가능               | MAC이 같아 구분 어려움     |
| 권장 환경       | 물리 서버, 스푸핑 허용 가능한 VM | 클라우드 VM, MAC 제한 환경 |

ipvlan은 `-d ipvlan -o ipvlan_mode=l2`로 만들며 나머지 옵션은 macvlan과 같습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 그 밖의 드라이버

```bash
docker run --rm --network host busybox:1.37 ip -o link    # 호스트와 같은 인터페이스가 보임
docker run --rm --network none busybox:1.37 ip -o link    # lo 만 보임
```

- `host`: 포트 공개(`-p`)가 무시되고 컨테이너 프로세스가 호스트 포트를 바로 씁니다. 같은 포트를 쓰는 컨테이너를 둘 띄울 수 없습니다.
- `none`: 네트워크 없이 파일 처리 같은 작업만 할 때 씁니다.
- `overlay`: Docker Swarm에서 여러 호스트의 컨테이너를 한 네트워크로 묶습니다. Kubernetes에서는 CNI 플러그인이 이 역할을 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용              | 명령                                                              | 기대 결과                                                |
|------|------------------------|-------------------------------------------------------------------|----------------------------------------------------------|
| 1    | 네트워크 존재·드라이버 | `docker network ls`                                               | 만든 네트워크와 드라이버                                 |
| 2    | 대역·게이트웨이        | `docker network inspect <이름>`                                   | 의도한 `Subnet`, `Gateway`                               |
| 3    | 붙은 컨테이너와 IP     | `docker network inspect <이름>`의 `Containers`                    | 의도한 컨테이너와 IP                                     |
| 4    | 이름 해석              | `docker run --rm --network <이름> busybox:1.37 nslookup <서비스>` | 서비스 IP 응답                                           |
| 5    | 서비스 간 통신         | `docker exec <a> ping -c 1 <b>`                                   | 응답                                                     |
| 6    | 공개 범위              | `docker port <컨테이너>`, `ss -tlnp`                              | 의도한 주소·포트에서만 대기                              |
| 7    | 내부 전용 차단         | internal 네트워크에서 외부 주소 `ping`                            | `Network is unreachable`                                 |
| 8    | macvlan 외부 접속      | 같은 대역의 다른 PC에서 `ping 192.0.2.151`, `curl`                | 응답                                                     |
| 9    | macvlan MAC 확인       | 다른 PC에서 `ip neigh` 또는 `arp -a`                              | 컨테이너 IP에 `docker inspect`의 `MacAddress`와 같은 MAC |
| 10   | 정리                   | `docker network rm <이름>`, `docker network prune`                | 남은 시험 네트워크 없음                                  |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                                 | 원인                                        | 해결 방법                                                       |
|------------------------------------------------------|---------------------------------------------|-----------------------------------------------------------------|
| `ping: bad address '<이름>'`                         | 기본 bridge에 붙어 있음, 또는 다른 네트워크 | 사용자 정의 bridge에 같이 붙임 (3-1)                            |
| 컨테이너를 띄운 뒤 사내망·VPN 일부가 끊김            | Docker 대역이 사내 대역과 겹침              | `--subnet` 지정, `default-address-pools` 변경 (3-3)             |
| `Pool overlaps with other one on this address space` | 이미 같은 대역의 네트워크가 있음            | `docker network inspect`로 찾아 대역 변경                       |
| 방화벽으로 막았는데 포트가 열림                      | Docker가 방화벽 규칙을 직접 넣음            | 공개하지 않거나 `127.0.0.1:` 지정 (5절)                         |
| macvlan 컨테이너에 외부에서 접속 안 됨               | VM MAC 스푸핑 꺼짐, 스위치 포트 보안        | 7-2 사전 조건 확인                                              |
| 호스트에서만 macvlan 컨테이너 접속 안 됨             | macvlan의 정상 동작                         | 7-5 shim 인터페이스, 또는 `docker exec` 사용                    |
| macvlan 컨테이너 IP가 다른 장비와 충돌               | DHCP 범위와 겹침                            | 컨테이너용 범위를 DHCP 범위 밖으로 (`ip_range`)                 |
| `network has active endpoints`로 삭제 실패           | 연결된 컨테이너가 남아 있음                 | `docker network inspect`로 찾아 `disconnect` 또는 컨테이너 삭제 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Docker 가이드](./docker.md) — 이미지, 컨테이너, 볼륨, cgroup
- [Docker Compose](./docker_compose.md) — `networks:`를 쓰는 compose.yaml
- [Docker 설치와 초기 설정](./docker_install.md) — daemon.json, 방화벽
- [Podman](./podman.md) — rootless 컨테이너 네트워크
- [IPv4 주소 체계](../../01_fundamentals/networking/ipv4_addressing_guide.md) — CIDR, 서브넷 계산
- [Linux namespace 개념](../../01_fundamentals/linux/namespace_concepts.md) — 네트워크 namespace

---

## 참고 자료

- Docker Documentation: [Networking overview](https://docs.docker.com/engine/network/) — ★★★☆☆
- Docker Documentation: [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/) — ★★★☆☆
- Docker Documentation: [Macvlan network driver](https://docs.docker.com/engine/network/drivers/macvlan/) — ★★★☆☆
- Docker Documentation: [IPvlan network driver](https://docs.docker.com/engine/network/drivers/ipvlan/) — ★★★☆☆
- Docker Documentation: [Port publishing and mapping](https://docs.docker.com/engine/network/port-publishing/) — ★★★☆☆
- Docker Documentation: [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/) — ★★★☆☆
- Microsoft Learn: [Set-VMNetworkAdapter](https://learn.microsoft.com/powershell/module/hyper-v/set-vmnetworkadapter) — ★★★☆☆

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
