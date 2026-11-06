# HAProxy 운영 가이드
<!-- reference: _reference/web_server_official_notes.md -->

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 버전 선택과 설치 소스](#2-버전-선택과-설치-소스)                  |
| [3. 설정 파일 배치](#3-설정-파일-배치) / [4. 기본 설정 템플릿](#4-기본-설정-템플릿)        |
| [5. 설정 변경 절차](#5-설정-변경-절차) / [6. 배포 중 서버 빼기](#6-배포-중-서버-빼기)      |
| [7. 헬스체크 설계](#7-헬스체크-설계) / [8. TLS 종료](#8-tls-종료)                          |
| [9. 요청 속도 제한](#9-요청-속도-제한) / [10. 관측: 로그·통계·지표](#10-관측-로그통계지표) |
| [11. 장애 확인](#11-장애-확인) / [12. 보안 점검 목록](#12-보안-점검-목록)                  |
| [13. 업그레이드](#13-업그레이드)                                                           |

---

## 1. 개요

운영 중인 HAProxy의 설정을 안전하게 바꾸고, 서버를 무중단으로 넣고 빼고, 장애를 확인하는 절차를 정리합니다. 개념은 [HAProxy 핵심 개념](./haproxy_concepts.md), 첫 설치는 [HAProxy 설치 가이드](./haproxy_install.md)를 봅니다.

| 항목      | 내용                                                         |
|-----------|--------------------------------------------------------------|
| 기준 버전 | HAProxy 3.4 LTS(3.4.7), 2.8·3.0·3.2와 다른 점은 본문에 표시  |
| 기준 OS   | Ubuntu 24.04·26.04 (RHEL 계열은 패키지·경로 차이만 확인)     |
| 확인일    | 2026-11-06                                                   |
| 전제      | systemd로 실행(`-Ws` master-worker), Runtime API socket 사용 |

🟡 이 문서의 설정과 명령은 HAProxy 3.4 공식 문서(configuration·management)와 공식 systemd unit을 읽고 정리했으며, 작성 시 HAProxy를 설치·실행하지 않았습니다. 적용 전에 시험 서버에서 `haproxy -c`로 검사합니다. 확인 범위는 [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy)에 기록했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 버전 선택과 설치 소스

| 설치 소스                      | 제공 분기(2026-11-06)      | 맞는 경우                              |
|--------------------------------|----------------------------|----------------------------------------|
| Ubuntu 24.04 기본 저장소       | 2.8.30 (2.8 분기)          | 배포판 보안 업데이트만으로 충분할 때   |
| Debian/Ubuntu 패키지 팀 저장소 | 분기별 선택(마법사로 안내) | 3.x LTS가 필요할 때                    |
| RHEL 계열 기본 저장소          | 배포판 버전에 따름(미확인) | 배포판 지원 범위 안에서 운영할 때      |
| 소스 빌드                      | 모든 분기                  | PROMEX·AWS-LC 등 빌드 옵션이 필요할 때 |

- Debian·Ubuntu용 3.x 패키지는 [haproxy.debian.net](https://haproxy.debian.net/) 마법사에서 OS와 분기를 골라 나오는 저장소 줄을 씁니다. 분기·OS 조합마다 저장소가 다르므로 이 문서에 고정 명령을 적지 않습니다.
- 🟡 2.9 분기는 2025-Q1에 지원이 끝났습니다. `ppa:vbernat/haproxy-2.9`로 설치한 서버는 LTS 분기(3.2·3.4)로 옮깁니다.
- 분기를 고르는 기준은 [개념 문서 10절](./haproxy_concepts.md#10-버전-정책)을 봅니다. 운영에는 LTS를 쓰고, 같은 분기 안의 최신 수정판을 유지합니다.

설치 뒤 확인:

```bash
# 버전과 빌드 옵션(스레드 수, TLS 라이브러리, PROMEX 포함 여부)
haproxy -vv | head -40

# 실행 중인 unit의 실제 시작 명령
systemctl cat haproxy
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설정 파일 배치

설정을 한 파일에 몰지 않고 역할별로 나누면 변경 범위가 작아집니다. `-f`에 디렉터리를 주면 그 안의 `.cfg` 파일을 이름순(숨김 파일 제외)으로 읽습니다.

```
/etc/haproxy/
├── haproxy.cfg            # global + defaults
├── conf.d/
│   ├── 10-frontend.cfg    # frontend sections
│   ├── 20-be-app.cfg      # backend per service
│   └── 90-stats.cfg       # stats / metrics listen
├── certs/                 # PEM (cert + key), mode 600
└── maps/                  # host -> backend maps
```

- HAProxy 3.4 공식 systemd unit은 `-f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d`로 실행합니다. 배포판 패키지 unit은 다를 수 있으므로 `systemctl cat haproxy`로 확인하고, 없으면 drop-in(`systemctl edit haproxy`)으로 `-f` 디렉터리를 더합니다.
- 각 파일은 `frontend`·`backend` 같은 section 키워드로 시작해야 합니다. 서버 목록만 담은 파일은 읽지 못합니다.
- 숫자 접두어로 읽는 순서를 정합니다. `defaults`는 뒤따르는 section에만 적용되므로 `haproxy.cfg`에 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 기본 설정 템플릿

```
global
    log /dev/log local0
    chroot /var/lib/haproxy
    user haproxy
    group haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    # 오래 남는 이전 worker의 상한 (WebSocket, TCP 프록시가 있을 때)
    hard-stop-after 30m
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option redispatch
    retries 3
    timeout connect          5s
    timeout client           30s
    timeout server           30s
    timeout http-request     10s
    timeout http-keep-alive  10s
    timeout queue            30s
    timeout tunnel           1h
```

| 설정                           | 이유                                                              |
|--------------------------------|-------------------------------------------------------------------|
| `stats socket ... level admin` | Runtime API. 권한 660, 그룹을 운영자로 제한                       |
| `hard-stop-after`              | reload 뒤 이전 worker가 무한히 남지 않게 상한                     |
| `ssl-min-ver TLSv1.2`          | 3.4 기본값과 같지만 명시해 이전 분기·다른 설정 파일과 차이를 없앰 |
| `option redispatch`            | 세션 유지 대상 서버가 죽었을 때 다른 서버로 재시도                |
| `timeout http-request`         | 헤더를 천천히 보내는 공격 방어. 없으면 `timeout client`가 쓰임    |
| `timeout tunnel`               | WebSocket 유휴 허용 시간. 없으면 client·server timeout으로 끊김   |

- `maxconn`은 처음에 쓰지 않고 자동 계산값(FD 한도 기반)을 `show info`의 `Maxconn`으로 확인한 뒤 필요할 때 정합니다.
- `balance`는 backend마다 명시합니다. 3.3부터 기본값이 `random`으로 바뀌었기 때문입니다.
- `option http-server-close`는 keep-alive를 지원하지 않는 서버가 있을 때만 씁니다. 기본 keep-alive가 서버 연결 재사용에 유리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 설정 변경 절차

```
edit --> haproxy -c --> reload --> verify --> (fail) rollback
```

```bash
# 1. 바꾸기 전 백업
sudo cp -a /etc/haproxy /etc/haproxy.bak.$(date +%Y%m%d%H%M)

# 2. 문법 검사: 실제 unit과 같은 -f 순서로
sudo haproxy -c -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d

# 3. reload (unit의 ExecReload가 다시 -c 검사 후 SIGUSR2 전송)
sudo systemctl reload haproxy

# 4. 결과 확인
systemctl status haproxy --no-pager | head -15
sudo journalctl -u haproxy --since "5 min ago" --no-pager | tail -30
```

master CLI가 열려 있으면 reload 결과를 바로 받을 수 있습니다(공식 unit은 `-S /run/haproxy-master.sock`).

```bash
# socat 기본 timeout(0.5s)보다 길게
echo "reload" | sudo socat -t300 /run/haproxy-master.sock stdin
# Success=1 이면 새 worker 적용
```

- `haproxy -c`의 경고(warning)도 읽습니다. timeout을 빠뜨리면 경고만 내고 무제한 timeout으로 동작합니다.
- 새 worker가 뜨지 못하면 이전 worker가 계속 동작합니다. 바뀐 설정이 적용됐는지 결과로 확인하고, 실패하면 백업으로 되돌린 뒤 다시 reload합니다.
- `systemctl restart`는 모든 연결을 끊습니다. 바이너리 업그레이드처럼 꼭 필요할 때만 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 배포 중 서버 빼기

Runtime API로 설정 파일을 고치지 않고 서버 상태를 바꿉니다.

```bash
SOCK=/run/haproxy/admin.sock
api() { echo "$*" | sudo socat stdio "$SOCK"; }

# 1. drain: 새 요청 분산에서 제외 (헬스체크·세션 유지 연결은 유지)
api "set server be_app/app1 state drain"

# 2. 남은 연결이 0이 될 때까지 확인 (scur = 현재 세션 수)
api "show stat be_app 4 -1" | cut -d, -f1,2,5,18

# 3. maint: 트래픽과 헬스체크 모두 중단 → 배포 작업
api "set server be_app/app1 state maint"

# 4. 배포 후 복귀 (헬스체크가 rise 횟수만큼 성공하면 UP)
api "set server be_app/app1 state ready"
```

| 상황                 | 명령                                     |
|----------------------|------------------------------------------|
| 일부 트래픽만 보내기 | `set server be_app/app1 weight 10%`      |
| 전체 서버 상태 보기  | `show servers state be_app`              |
| 서버 주소 바꾸기     | `set server be_app/app1 addr 192.0.2.21` |

- 🟡 Runtime API로 바꾼 상태·가중치는 설정 파일에 남지 않습니다. reload 뒤에도 유지하려면 `server-state-file`을 쓰거나 설정 파일에도 반영합니다.
- 서버를 영구히 추가·삭제하는 것은 설정 파일로 합니다. `add server`·`del server`(3.4는 `add backend`도 가능)는 자동화 도구가 쓰는 동적 구성용입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 헬스체크 설계

```
backend be_app
    balance random
    option httpchk
    http-check send meth GET uri /healthz ver HTTP/1.1 hdr Host app.example.com
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 slowstart 30s
    server app1 192.0.2.11:8080 check
    server app2 192.0.2.12:8080 check
```

| 결정                   | 권장                                                                            |
|------------------------|---------------------------------------------------------------------------------|
| 검사 경로              | 의존 서비스까지 보지 않는 가벼운 경로. DB 장애 때 모든 서버가 DOWN 되는 것 방지 |
| HTTP 버전·Host         | `ver HTTP/1.1`이면 `Host` 헤더 필수                                             |
| 장애 감지 시간         | `inter × fall`. 기본(2s × 3)은 약 6초                                           |
| 복구 직후 부하         | `slowstart`로 가중치를 천천히 올림                                              |
| 같은 서버 여러 backend | `track`으로 한 번만 검사하고 상태를 공유                                        |

- `option httpchk`만 쓰면 `OPTIONS / HTTP/1.0`을 보냅니다. 애플리케이션이 OPTIONS를 막으면 모든 서버가 DOWN이 되므로 메서드와 경로를 명시합니다.
- TCP 서비스는 `option tcp-check`와 `tcp-check send`·`tcp-check expect`로 프로토콜 응답을 봅니다. MySQL·Redis는 `option mysql-check`·`option redis-check`도 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. TLS 종료

```bash
# 인증서와 키를 PEM 하나로 (HAProxy는 같은 파일에서 둘 다 읽음)
sudo install -d -m 700 /etc/haproxy/certs
cat fullchain.pem privkey.pem | sudo tee /etc/haproxy/certs/example.com.pem >/dev/null
sudo chmod 600 /etc/haproxy/certs/example.com.pem
```

```
frontend fe_web
    bind :80
    bind :443 ssl crt /etc/haproxy/certs/ alpn h2,http/1.1
    http-request redirect scheme https code 301 unless { ssl_fc }
    http-request set-header X-Forwarded-Proto https if { ssl_fc }
    http-response set-header Strict-Transport-Security "max-age=31536000"
    option forwardfor
    default_backend be_app
```

- `crt`에 디렉터리를 주면 안의 인증서를 모두 읽고 SNI로 고릅니다.
- 3.4 기본 `ssl-min-ver`는 TLSv1.2입니다. 암호 목록은 [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)의 HAProxy 항목을 기준으로 합니다.
- `option forwardfor`는 `X-Forwarded-For`를 붙입니다. 앞에 CDN·다른 프록시가 있으면 신뢰할 대역만 받아들이도록 서버 쪽 설정도 맞춥니다([CDN·프록시와 원본 IP](../../01_fundamentals/networking/cdn_proxy_origin_ip.md)).
- 인증서 교체는 파일을 바꾸고 reload합니다. 만료 감시는 [TLS 인증서 만료 감시](../../04_security/hardening/tls_certificate_expiry_monitoring.md)를 봅니다. 3.2부터 있는 내장 ACME 자동 갱신은 [HAProxy ACME 가이드](./haproxy_acme_guide.md)에서 다룹니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 요청 속도 제한

stick-table로 클라이언트 IP별 요청 수를 세고, 기준을 넘으면 429로 거절합니다.

```
frontend fe_web
    bind :443 ssl crt /etc/haproxy/certs/
    stick-table type ip size 1m expire 10m store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
    default_backend be_app
```

| 항목                 | 뜻                                |
|----------------------|-----------------------------------|
| `size 1m`            | 최대 100만 개 키(IP)              |
| `expire 10m`         | 10분 동안 요청이 없으면 항목 삭제 |
| `http_req_rate(10s)` | 최근 10초 요청 수                 |
| `gt 100`             | 10초에 100회 초과면 거절          |

```bash
# 현재 표 내용과 상위 사용자 확인
echo "show table fe_web" | sudo socat stdio /run/haproxy/admin.sock | head -20
```

- 앞에 CDN·LB가 있으면 `src`가 모두 같은 주소입니다. 신뢰할 수 있는 헤더에서 원래 IP를 꺼내 키로 씁니다.
- 처음에는 `deny` 대신 `http-request set-var`나 로그로 기준을 넘는 요청 수를 먼저 관찰하고 기준을 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 관측: 로그·통계·지표

### 로그

`option httplog`의 한 줄에는 요청이 지나간 단계별 시간과 종료 상태가 들어 있습니다.

| 필드                  | 예                        | 읽는 법                                                      |
|-----------------------|---------------------------|--------------------------------------------------------------|
| 시간 `TR/Tw/Tc/Tr/Ta` | `0/0/1/45/46`             | 요청 수신/큐 대기/서버 연결/서버 응답/전체(ms)               |
| 종료 상태             | `----`, `sH--`, `cD--`    | 첫 글자 C·c는 클라이언트, S·s는 서버 쪽 원인, 두 번째는 단계 |
| 연결 수               | `actconn/feconn/...`      | 당시 전체·frontend·backend·서버 연결 수                      |
| 큐                    | `srv_queue/backend_queue` | 0이 아니면 서버 maxconn 도달                                 |

- 컨테이너에서는 `log stdout format raw local0`으로 표준 출력에 냅니다.
- 시간 값 중 `Tw`(큐 대기)가 크면 서버 수·maxconn, `Tc`가 크면 네트워크·서버 accept, `Tr`이 크면 애플리케이션을 봅니다.

### 통계 화면과 Prometheus 지표

```
frontend fe_stats
    bind 10.0.0.5:8404
    http-request use-service prometheus-exporter if { path /metrics }
    stats enable
    stats uri /stats
    stats refresh 10s
    stats hide-version
    http-request deny unless { src 10.0.0.0/8 }
```

- 통계 화면과 지표는 내부 주소에만 bind하고 접근 대역을 제한합니다. `stats auth`의 비밀번호는 설정 파일에 평문으로 남으므로 공개 저장소에 올리지 않습니다.
- 🟡 Prometheus exporter(PROMEX)는 기본 빌드에 포함되지 않습니다. `haproxy -vv`에 `Built with the Prometheus exporter as a service`가 있는지 먼저 확인합니다. 없으면 `use-service prometheus-exporter` 줄이 설정 오류가 됩니다.
- 지표 수집 구성은 [Prometheus·Grafana](../monitoring/prometheus_grafana.md) 문서를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 장애 확인

```bash
SOCK=/run/haproxy/admin.sock
api() { echo "$*" | sudo socat stdio "$SOCK"; }

api "show info" | grep -E 'Version|Uptime|Maxconn|CurrConns|Idle_pct'
api "show stat" | cut -d, -f1,2,5,18,37 | column -s, -t   # 서버별 현재 세션, 상태, 마지막 검사
api "show servers state"
api "show errors"        # 거부된 비정상 요청·응답의 원문
api "show sess"          # 현재 세션 목록 (많으면 주의)
```

| 증상                | 먼저 볼 것                                   | 흔한 원인                                       |
|---------------------|----------------------------------------------|-------------------------------------------------|
| 503                 | `show stat`의 서버 상태                      | backend 서버 모두 DOWN, 헬스체크 경로·Host 오류 |
| 504                 | 로그 `Tr`, 종료 상태 `sH`                    | `timeout server`보다 느린 애플리케이션          |
| 408                 | 로그 종료 상태 `cR`                          | `timeout http-request` 안에 헤더 미도착         |
| 응답이 느림         | 로그 `Tw`, `show info`의 `Idle_pct`          | 서버 maxconn 큐 대기, HAProxy CPU 포화          |
| reload 후 변화 없음 | `journalctl -u haproxy`, master CLI `reload` | 설정 오류로 새 worker 미적용                    |
| 메모리 계속 증가    | `ps`로 worker 수                             | 이전 worker가 남음, `hard-stop-after` 없음      |
| 400·502 간헐 발생   | `show errors`                                | 규격에 맞지 않는 요청·응답 헤더                 |

- `Idle_pct`가 0에 가까우면 HAProxy CPU가 포화된 것입니다. 공식 문서는 swap, CPU 공유, 과도한 스레드 수를 먼저 의심하라고 설명합니다.
- 패킷 수준 확인은 [tcpdump 예제](../../01_fundamentals/networking/tcpdump_examples.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 12. 보안 점검 목록

| 점검                                     | 확인 방법                                                      |
|------------------------------------------|----------------------------------------------------------------|
| 지원 중인 분기·최신 수정판인가           | `haproxy -v`와 [haproxy.org](https://www.haproxy.org/) 표 비교 |
| Runtime API socket 권한이 제한되었나     | `ls -l /run/haproxy/admin.sock` (660, 운영 그룹)               |
| master CLI socket이 외부에 열리지 않았나 | `systemctl cat haproxy`의 `-S` 경로                            |
| 통계·지표가 내부 주소에만 열렸나         | `ss -ltnp` 의 haproxy 줄                                       |
| 인증서 파일 권한                         | `stat -c '%a %U' /etc/haproxy/certs/*`                         |
| timeout이 모두 설정되었나                | `haproxy -c` 경고 없음                                         |
| 요청 속도 제한·관리 경로 차단이 있나     | frontend 규칙 검토                                             |
| 버전 노출을 막았나                       | `stats hide-version`, 오류 페이지                              |

- 🔵 2026-02-12 공지된 QUIC 파싱 취약점(CVE-2026-26081은 3.0 이상, CVE-2026-26080은 3.2 이상)은 조작된 패킷으로 프로세스가 중단될 수 있습니다. 수정판은 3.0.12, 3.1.14, 3.2.12, 3.3.3 이상입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 13. 업그레이드

1. 대상 분기의 변경 사항을 읽습니다. 공식 공지에서 기본값 변경과 제거된 키워드를 확인합니다.
2. 시험 서버에 새 버전을 설치하고 운영 설정으로 `haproxy -c`를 실행해 오류·경고를 없앱니다.
3. 운영 서버는 LB 이중화([HAProxy + Keepalived 이중화](./haproxy_keepalived_ha.md))가 있으면 한 대씩 빼고 올립니다. 바이너리 교체는 reload가 아니라 restart가 필요할 수 있으므로 트래픽을 다른 노드로 넘긴 뒤 합니다.
4. `show info`의 Version, 로그 오류율, 응답 시간을 이전과 비교합니다.

| 올릴 때 확인할 기본값 변경          | 영향                                            |
|-------------------------------------|-------------------------------------------------|
| 3.3: `balance` 기본값 `random`      | 알고리즘을 쓰지 않은 backend의 분산 방식이 바뀜 |
| 3.3: 오래 폐기 예정이던 키워드 제거 | `haproxy -c` 오류로 드러남                      |
| 3.4: OpenTracing 폐기 예정          | OpenTelemetry filter로 옮길 계획 필요           |
| 3.4: 공식 unit에 `conf.d` 추가      | 배포판 unit과 `-f` 순서 차이 확인               |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HAProxy 3.4 Configuration Manual: [docs.haproxy.org/3.4/configuration.html](https://docs.haproxy.org/3.4/configuration.html) — ★★★★★
- HAProxy 3.4 Management Guide: [docs.haproxy.org/3.4/management.html](https://docs.haproxy.org/3.4/management.html) — ★★★★☆
- HAProxy 공식 사이트(버전·공지): [haproxy.org](https://www.haproxy.org/) — ★★★★☆
- Debian/Ubuntu HAProxy 패키지: [haproxy.debian.net](https://haproxy.debian.net/) — ★★★★☆
- Mozilla SSL Configuration Generator: [ssl-config.mozilla.org](https://ssl-config.mozilla.org/) — ★★★★☆
- 확인 기록: [웹 서버 참조 노트 3절](../../_reference/web_server_official_notes.md#3-haproxy)
- 관련 문서: [HAProxy 핵심 개념](./haproxy_concepts.md), [HAProxy 설치 가이드](./haproxy_install.md), [HAProxy + Keepalived 이중화](./haproxy_keepalived_ha.md), [HAProxy ACME 가이드](./haproxy_acme_guide.md), [로드 밸런서 테스트](../../01_fundamentals/cs/web_testing/load_balancer_testing.md), [graceful reload 테스트](../../01_fundamentals/cs/web_testing/graceful_reload_testing.md)

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
