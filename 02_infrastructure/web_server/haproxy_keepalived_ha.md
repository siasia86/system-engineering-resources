# HAProxy + Keepalived 이중화 가이드
<!-- reference: _reference/web_server_official_notes.md -->

## 목차

| 섹션                                                                               |
|------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 구성](#2-구성) / [3. VRRP 동작 원리](#3-vrrp-동작-원리)   |
| [4. 사전 준비](#4-사전-준비) / [5. Keepalived 설정](#5-keepalived-설정)            |
| [6. HAProxy peers 설정](#6-haproxy-peers-설정) / [7. 전환 시험](#7-전환-시험)      |
| [8. 운영 절차](#8-운영-절차) / [9. 장애 사례](#9-장애-사례) / [10. 한계](#10-한계) |

---

## 1. 개요

HAProxy를 한 대만 두면 그 서버가 멈출 때 뒤의 서버가 모두 정상이어도 서비스가 멈춥니다. 이 문서는 HAProxy 두 대를 active-standby로 두고, Keepalived가 VRRP로 가상 IP(VIP)를 정상 노드로 옮기는 구성을 다룹니다. 두 노드의 stick-table(속도 제한 카운터·세션 유지 정보)은 HAProxy peers로 맞춥니다.

| 항목       | 내용                                                                             |
|------------|----------------------------------------------------------------------------------|
| 대상       | 같은 L2 네트워크(같은 VLAN)에 있는 온프레미스·가상화 서버 2대                    |
| HAProxy    | 3.4 LTS 기준, peers는 2.8 이상 공통 기능                                         |
| Keepalived | 최신 v2.4.3(2026-07-20 태그), Ubuntu 24.04 기본 저장소 2.2.8                     |
| 확인일     | 2026-11-06                                                                       |
| 관련 문서  | [핵심 개념](./haproxy_concepts.md), [운영 가이드](./haproxy_operations_guide.md) |

🟡 이 문서의 설정은 Keepalived `keepalived.conf(5)` man 문서(v2.4.3 태그와 v2.2.8 태그), HAProxy 3.4 설정·관리 문서, Linux 커널 ip-sysctl 문서를 읽고 정리했으며 작성 시 설치·실행하지 않았습니다. 시험 환경에서 7절의 전환 시험을 거친 뒤 운영에 적용합니다. 확인 범위는 [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy)에 기록했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 구성

```
                    clients
                       |
                 VIP 192.0.2.100
                       |
        +--------------+--------------+
        |                             |
+---------------+  VRRP adverts  +---------------+
|    lb1        | <------------> |    lb2        |
|  MASTER       |                |  BACKUP       |
|  prio 150     |   peers sync   |  prio 100     |
|  haproxy      | <------------> |  haproxy      |
|  192.0.2.11   |   tcp/10000    |  192.0.2.12   |
+---------------+                +---------------+
        |                             |
        +--------------+--------------+
                       |
          app1 192.0.2.21 / app2 192.0.2.22
```

| 구성 요소  | 역할                                                                     |
|------------|--------------------------------------------------------------------------|
| VIP        | 클라이언트가 접속하는 주소. MASTER 노드의 인터페이스에만 붙음            |
| Keepalived | VRRP로 MASTER를 정하고 VIP를 붙이거나 뗌. HAProxy 상태를 스크립트로 감시 |
| HAProxy    | 두 노드 모두 같은 설정으로 실행. VIP가 있는 노드만 트래픽을 받음         |
| peers      | 두 HAProxy가 stick-table 항목을 서로 보냄. 전환 뒤에도 카운터 유지       |

- active-standby에서는 HAProxy 한 대가 전체 트래픽을 감당해야 합니다. 두 노드의 사양을 같게 둡니다.
- 두 VIP를 두고 노드마다 MASTER를 하나씩 맡기는 active-active도 가능하지만, 장애 시 한 노드가 두 배 부하를 받으므로 같은 용량 계산이 필요합니다. 이 문서는 active-standby만 다룹니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. VRRP 동작 원리

VRRP(RFC 5798)는 여러 라우터·서버 중 하나를 MASTER로 정해 가상 IP를 맡기는 프로토콜입니다.

| 단계      | 동작                                                                                |
|-----------|-------------------------------------------------------------------------------------|
| 선출      | `priority`가 가장 높은 노드가 MASTER. 같은 `virtual_router_id`를 쓰는 노드끼리 경쟁 |
| 광고      | MASTER가 `advert_int`(예: 1초)마다 VRRP 광고를 보냄                                 |
| 장애 감지 | BACKUP이 광고를 일정 시간 못 받으면 MASTER가 됨                                     |
| 주소 이전 | 새 MASTER가 VIP를 인터페이스에 붙이고 gratuitous ARP로 이웃의 ARP 표를 갱신         |
| 상태 감시 | `vrrp_script` 실패 시 FAULT 상태로 가거나 priority를 낮춰 MASTER를 넘김             |

- 광고를 못 받은 뒤 넘어가기까지의 시간은 `3 × advert_int + skew_time`입니다. man 문서 예시로 `advert_int 1`, priority 128이면 약 3.5초입니다.
- **선점(preempt):** 기본은 priority가 높은 노드가 돌아오면 MASTER를 다시 가져갑니다. VIP가 한 번 더 옮겨 가므로 짧은 끊김이 한 번 더 생깁니다. `nopreempt`를 쓰면 돌아온 노드가 BACKUP으로 남습니다(이때 초기 `state`는 MASTER가 아니어야 함).
- man 문서는 MASTER가 될 노드의 priority를 다른 노드보다 50 높게, 모든 노드의 priority를 서로 다르게 두라고 권합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 사전 준비

### 4-1. 패키지

```bash
# Ubuntu (24.04 기본 저장소: keepalived 2.2.8)
sudo apt install keepalived

# RHEL 계열
sudo dnf install keepalived

keepalived --version
```

HAProxy 설치와 버전 선택은 [운영 가이드 2절](./haproxy_operations_guide.md#2-버전-선택과-설치-소스)을 따릅니다. 두 노드는 같은 HAProxy 버전을 씁니다.

### 4-2. VIP bind 허용

BACKUP 노드에는 VIP가 없으므로 HAProxy가 `bind 192.0.2.100:443`으로 시작하면 실패합니다. 두 가지 방법 중 하나를 씁니다.

| 방법                       | 설정                                 | 특징                                             |
|----------------------------|--------------------------------------|--------------------------------------------------|
| 모든 주소에 bind           | `bind :443`                          | 설정이 단순. 노드의 다른 주소로도 접속 가능      |
| 로컬에 없는 주소 bind 허용 | 커널 `net.ipv4.ip_nonlocal_bind = 1` | VIP로만 받음. 노드 전체의 다른 프로그램에도 적용 |

```bash
# 방법 2를 쓰는 경우
echo 'net.ipv4.ip_nonlocal_bind = 1' | sudo tee /etc/sysctl.d/90-haproxy-vip.conf
sudo sysctl --system
```

🟡 커널 문서는 `ip_nonlocal_bind`가 "유용하지만 일부 애플리케이션을 깨뜨릴 수 있다"고 설명합니다. HAProxy 전용 노드에서만 켭니다.

### 4-3. 방화벽

| 트래픽        | 프로토콜·포트                                        | 방향       |
|---------------|------------------------------------------------------|------------|
| VRRP 광고     | IP 프로토콜 112 (멀티캐스트 224.0.0.18 또는 unicast) | lb1 ↔ lb2  |
| HAProxy peers | TCP 10000 (아래 예시 포트)                           | lb1 ↔ lb2  |
| 서비스        | TCP 80·443                                           | 외부 → VIP |

```bash
# firewalld 예시: 상대 노드에서 오는 VRRP·peers만 허용
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.0.2.12" protocol value="vrrp" accept'
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.0.2.12" port port="10000" protocol="tcp" accept'
sudo firewall-cmd --reload
```

VRRP 광고가 막히면 두 노드가 모두 MASTER가 되어 VIP가 두 곳에 붙습니다(9절 split-brain).

[⬆ 목차로 돌아가기](#목차)

---

## 5. Keepalived 설정

### 5-1. HAProxy 감시 스크립트

```bash
sudo tee /etc/keepalived/check_haproxy.sh >/dev/null <<'EOF'
#!/bin/sh
# exit 0 = healthy, non-zero = failed
systemctl is-active --quiet haproxy
EOF
sudo chmod 755 /etc/keepalived/check_haproxy.sh
sudo chown root:root /etc/keepalived/check_haproxy.sh
```

- 스크립트를 실행할 사용자는 `script_user`로 정합니다. 지정하지 않으면 `keepalived_script` 사용자가 있으면 그 사용자, 없으면 Keepalived를 실행한 사용자(보통 root)입니다.
- `enable_script_security`를 켜면 경로 중 일부라도 root가 아닌 사용자가 쓸 수 있는 스크립트는 root로 실행하지 않습니다. 스크립트와 디렉터리 소유자를 root로 둡니다.

### 5-2. lb1 (MASTER)

```
# /etc/keepalived/keepalived.conf (lb1)
global_defs {
    router_id lb1
    enable_script_security
    script_user root
}

vrrp_script chk_haproxy {
    script "/etc/keepalived/check_haproxy.sh"
    interval 2
    fall 2
    rise 2
}

vrrp_instance VI_WEB {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 150
    advert_int 1

    unicast_src_ip 192.0.2.11
    unicast_peer {
        192.0.2.12
    }

    virtual_ipaddress {
        192.0.2.100/24 dev eth0
    }

    track_script {
        chk_haproxy
    }
}
```

### 5-3. lb2 (BACKUP)

lb1과 다른 줄만 바꿉니다.

```
global_defs {
    router_id lb2
    ...
}

vrrp_instance VI_WEB {
    state BACKUP
    priority 100
    unicast_src_ip 192.0.2.12
    unicast_peer {
        192.0.2.11
    }
    ...
}
```

### 5-4. 설정 항목

| 항목                   | 값·뜻                                                                   |
|------------------------|-------------------------------------------------------------------------|
| `vrrp_script interval` | 스크립트 실행 간격(초). 기본 1초                                        |
| `fall` / `rise`        | 연속 실패 횟수로 실패 판정, 연속 성공 횟수로 복구 판정                  |
| `weight`               | 기본 0이면 실패 시 FAULT 상태(VIP 해제). 음수면 실패 시 priority에서 뺌 |
| `virtual_router_id`    | 같은 네트워크의 다른 VRRP 묶음과 겹치지 않는 1~255 값                   |
| `priority`             | 1~255. 높은 쪽이 MASTER. 255는 주소 소유자 뜻이라 쓰지 않음             |
| `unicast_peer`         | 멀티캐스트 대신 상대 주소로 광고. 멀티캐스트를 막는 네트워크에서 사용   |
| `track_script`         | 이 인스턴스가 감시할 스크립트                                           |

- `weight`를 음수로 쓰면 HAProxy가 죽어도 FAULT가 아니라 priority만 내려갑니다. 위 예에서 `weight -60`이면 lb1이 150 → 90이 되어 lb2(100)가 MASTER가 됩니다. 기본값(0, FAULT 전환)이 동작을 이해하기 쉽습니다.
- `authentication` 블록은 VRRPv2 규격(RFC 3768)에서 2004년에 빠졌고, man 문서는 unicast가 아니면 쓰지 말라고 안내합니다. 광고 위조 방지는 v2.4 계열의 `auth_hmac`이 있으나 Ubuntu 24.04 패키지(2.2.8) man 문서에는 없습니다.

```bash
# 설정 검사 후 시작
sudo keepalived --config-test   # 오류가 있으면 0이 아닌 종료 코드
sudo systemctl enable --now keepalived
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. HAProxy peers 설정

peers 없이 전환하면 새 MASTER의 stick-table이 비어 있으므로, 속도 제한 카운터가 0부터 다시 시작하고 stick-table 기반 세션 유지 정보가 사라집니다.

```
# 두 노드에 똑같이 두는 설정
peers lb_peers
    peer lb1 192.0.2.11:10000
    peer lb2 192.0.2.12:10000
    table rate type ip size 1m expire 10m store http_req_rate(10s)

frontend fe_web
    bind :443 ssl crt /etc/haproxy/certs/
    http-request track-sc0 src table lb_peers/rate
    http-request deny deny_status 429 if { sc_http_req_rate(0,lb_peers/rate) gt 100 }
    default_backend be_app
```

| 규칙                 | 공식 문서 설명                                                                      |
|----------------------|-------------------------------------------------------------------------------------|
| 로컬 peer 이름       | 기본은 hostname. 다르면 `localpeer` 전역 설정이나 `-L` 옵션으로 맞춤                |
| 같은 peers 선언      | 모든 노드에 똑같은 peers 선언을 두고 로컬 이름만 `localpeer`로 바꾸기를 강하게 권장 |
| `peers` 안의 `table` | 이름 앞에 section 이름이 붙음. 다른 곳에서는 `lb_peers/rate`처럼 참조               |
| 서버 ID              | 원격 노드에서 서버를 ID로 식별하므로 backend 서버 순서·ID를 두 노드에서 같게 유지   |
| `conn_cur`           | 기본으로 peers에서 받지 않음(각 노드의 현재 연결 수라서)                            |
| reload               | 이전 worker가 새 worker에 모든 항목을 먼저 보냄. 큰 표도 보통 1초 안쪽              |

```bash
# 동기화 상태 확인
echo "show peers lb_peers" | sudo socat stdio /run/haproxy/admin.sock
echo "show table lb_peers/rate" | sudo socat stdio /run/haproxy/admin.sock | head
```

- hostname이 `lb1`·`lb2`가 아니면 `global`에 `localpeer lb1`(lb2 노드는 `localpeer lb2`)을 넣습니다. 이 한 줄만 노드마다 다르게 둡니다.
- 쿠키 기반 세션 유지(`cookie SRV insert`)는 쿠키에 서버 이름이 있으므로 peers 없이도 전환 뒤 유지됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 전환 시험

운영 적용 전에 시험 환경에서 아래 순서를 모두 확인합니다.

```bash
# 0. 클라이언트에서 끊김 측정 루프 (별도 터미널)
while true; do
  printf '%s ' "$(date +%T)"
  curl -s -o /dev/null -w '%{http_code}\n' --max-time 2 http://192.0.2.100/healthz
  sleep 0.5
done

# 1. 현재 VIP 위치
ip -br addr show eth0          # lb1에 192.0.2.100 이 보여야 함

# 2. lb1의 HAProxy 중지 → VIP가 lb2로
sudo systemctl stop haproxy    # on lb1
sudo journalctl -u keepalived -n 20 --no-pager   # FAULT / BACKUP 전환 기록

# 3. lb1 복구 → 선점이면 VIP가 lb1로 돌아옴
sudo systemctl start haproxy   # on lb1

# 4. lb1의 Keepalived 중지(노드 전체 장애 흉내)
sudo systemctl stop keepalived # on lb1
```

| 시험            | 기대 결과                                  | 기록할 것               |
|-----------------|--------------------------------------------|-------------------------|
| HAProxy 중지    | `fall × interval`(예: 4초) 뒤 VIP가 lb2로  | 실패 응답 수, 전환 시간 |
| HAProxy 복구    | 선점 설정이면 VIP가 lb1로 돌아옴           | 두 번째 끊김 길이       |
| Keepalived 중지 | lb2가 MASTER가 되고 VIP가 lb2로            | 전환 시간               |
| VRRP 차단       | 두 노드 모두 MASTER(split-brain) 재현 여부 | 감시 경보가 울리는지    |
| peers           | 전환 뒤 `show table`의 카운터가 이어짐     | 항목 수 비교            |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 운영 절차

### 계획된 전환(유지보수)

```bash
# lb1 작업 전: Keepalived만 멈춰 VIP를 lb2로 넘김 (HAProxy는 그대로)
sudo systemctl stop keepalived   # on lb1
ip -br addr show eth0            # on lb2: VIP 확인

# lb1 작업 (OS 패치, HAProxy 업그레이드 등)

# 복구
sudo systemctl start keepalived  # on lb1
```

- VIP가 넘어가면 VIP로 lb1에 붙어 있던 연결은 끊깁니다. 트래픽이 적은 시간에 하고, 넘긴 뒤 lb1의 `show info`에서 `CurrConns`가 0에 가까운지 확인하고 작업합니다.
- 업그레이드는 BACKUP 노드부터 하고, 전환 후 남은 노드를 합니다.

### 설정 동기화

두 노드의 HAProxy 설정은 `localpeer` 줄을 빼고 같아야 합니다. 한쪽만 고치면 전환 순간 동작이 바뀝니다.

```bash
# lb1 기준으로 비교 (localpeer 줄은 다를 수 있음)
diff <(ssh lb1 'sudo cat /etc/haproxy/haproxy.cfg /etc/haproxy/conf.d/*.cfg') \
     <(ssh lb2 'sudo cat /etc/haproxy/haproxy.cfg /etc/haproxy/conf.d/*.cfg')
```

설정 배포는 Ansible 같은 도구로 두 노드에 같은 파일을 보내고, 노드마다 [운영 가이드 5절](./haproxy_operations_guide.md#5-설정-변경-절차)의 `haproxy -c` → reload 순서를 지킵니다. Ansible 운영은 [Ansible 기초](../iac/ansible_basic_guide.md)를 봅니다.

### 감시

| 감시 대상            | 방법                                                                          |
|----------------------|-------------------------------------------------------------------------------|
| VIP 위치             | 두 노드의 `ip -br addr`. VIP가 0곳 또는 2곳이면 경보                          |
| Keepalived 상태 변화 | `notify_master`·`notify_backup`·`notify_fault` 스크립트로 알림                |
| HAProxy 상태         | [운영 가이드 10절](./haproxy_operations_guide.md#10-관측-로그통계지표)의 지표 |
| peers 연결           | `show peers` 출력의 연결 상태                                                 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 장애 사례

| 증상                                | 원인                                                     | 확인·조치                                               |
|-------------------------------------|----------------------------------------------------------|---------------------------------------------------------|
| 두 노드 모두 MASTER (split-brain)   | VRRP 광고 차단(방화벽, 멀티캐스트 차단, 다른 VLAN)       | `tcpdump -ni eth0 vrrp`로 광고 수신 확인, 방화벽 규칙   |
| HAProxy가 죽어도 VIP가 안 옮겨 감   | 스크립트 실행 권한, `enable_script_security`로 실행 거부 | `journalctl -u keepalived`의 스크립트 오류, 소유자·권한 |
| BACKUP에서 HAProxy 시작 실패        | VIP에 bind (`cannot bind socket`)                        | 4-2절 `bind :443` 또는 `ip_nonlocal_bind`               |
| VIP가 반복해서 오감(flapping)       | 스크립트 `fall`·`rise`가 너무 작음, 선점 반복            | 횟수 늘리기, `nopreempt` 검토                           |
| 전환 뒤 일부 클라이언트만 접속 불가 | 스위치·라우터 ARP 캐시가 옛 MAC을 가리킴                 | gratuitous ARP 수신 여부, 장비 ARP 표                   |
| 전환 뒤 속도 제한 카운터 초기화     | peers 미설정, peer 이름 불일치                           | `show peers`, `localpeer`                               |
| 다른 서비스 VIP와 충돌              | 같은 네트워크에서 `virtual_router_id` 중복               | 네트워크 단위로 ID 대장 관리                            |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 한계

- **클라우드:** VRRP와 gratuitous ARP로 IP를 옮기는 방식은 같은 L2 네트워크를 전제로 합니다. 퍼블릭 클라우드 VPC에서는 보통 그대로 동작하지 않으며, 제공자의 부하 분산 서비스나 API로 IP를 옮기는 방식을 씁니다. 이 문서는 다루지 않습니다.
- **전환 중 끊김:** VIP가 옮겨 가는 몇 초 동안 새 연결은 실패하고, 이전 노드에 있던 TCP 연결은 끊깁니다. 연결 손실이 생기므로 클라이언트 재시도가 필요합니다.
- **버전 차이:** 배포판 Keepalived(2.2.8)와 최신(2.4.3)은 지원 설정이 다릅니다. 설정 전에 설치된 버전의 `man keepalived.conf`를 확인합니다.
- 이 문서의 설정은 실제 장비에서 실행·검사하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Keepalived 설정 man 문서: [github.com/acassen/keepalived](https://github.com/acassen/keepalived/blob/v2.4.3/doc/man/man5/keepalived.conf.5.in) — ★★★★☆
- Keepalived 공식 사이트: [keepalived.org](https://www.keepalived.org/) — ★★★☆☆
- RFC 5798 VRRP Version 3: [rfc-editor.org/rfc/rfc5798](https://www.rfc-editor.org/rfc/rfc5798) — ★★★★★
- HAProxy 3.4 Configuration Manual 11.2 Peers: [docs.haproxy.org/3.4/configuration.html](https://docs.haproxy.org/3.4/configuration.html) — ★★★★★
- Linux 커널 ip-sysctl: [docs.kernel.org/networking/ip-sysctl.html](https://docs.kernel.org/networking/ip-sysctl.html) — ★★★★☆
- 확인 기록: [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy)
- 관련 문서: [HAProxy 핵심 개념](./haproxy_concepts.md), [HAProxy 운영 가이드](./haproxy_operations_guide.md), [로드 밸런서 테스트](../../01_fundamentals/cs/web_testing/load_balancer_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-06

**마지막 업데이트**: 2026-11-06

© 2026 siasia86. Licensed under CC BY 4.0.
