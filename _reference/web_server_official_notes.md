---
name: web-server-official-notes
description: Nginx, Apache HTTP Server, HAProxy 공식 문서 기반 설정, 보안, 성능 참조 노트. 02_infrastructure/web_server/ 문서 생성/검토 시 참조.
tags:
  - nginx
  - apache
  - httpd
  - web-server
  - reverse-proxy
  - haproxy
  - load-balancer
  - keepalived
  - acme
last_checked: 2026-11-09
sources:
  - https://nginx.org/en/docs/
  - https://httpd.apache.org/docs/2.4/
  - https://ssl-config.mozilla.org/
  - https://www.ssllabs.com/ssltest/
  - https://www.haproxy.org/
  - https://docs.haproxy.org/3.4/configuration.html
  - https://docs.haproxy.org/3.4/management.html
  - https://haproxy.debian.net/
  - https://github.com/acassen/keepalived/blob/v2.4.3/doc/man/man5/keepalived.conf.5.in
  - https://docs.kernel.org/networking/ip-sysctl.html
  - https://github.com/haproxy/wiki/wiki/ACME:--native-haproxy
---

# Web Server 공식 참조 노트

## 1. Nginx

### 버전 (확인일: 2026-07-08)

| 채널     | 버전   | 비고              |
|----------|--------|-------------------|
| Mainline | 1.31.2 | 최신 기능, 개발용 |
| Stable   | 1.30.3 | 프로덕션 권장     |

- 출처: https://nginx.org/en/download.html
- 2026-11-09 확인: Mainline 1.31.8(2026-10-21), Stable 1.30.6(2026-10-14)입니다(nginx.org CHANGES).

### 핵심 설정

| 항목                 | 권장값             | 근거                         |
|----------------------|--------------------|------------------------------|
| worker_processes     | auto               | CPU 코어 수에 맞춤           |
| worker_connections   | 1024~65535         | ulimit -n 과 일치            |
| keepalive_timeout    | 75s (기본값)       | CDN 뒤면 60~65s로 축소 가능  |
| client_max_body_size | 업로드 크기에 맞게 | 기본 1m, 파일 업로드 시 조정 |
| server_tokens        | off                | 버전 정보 노출 방지          |
| proxy_buffering      | on (기본)          | 백엔드 부하 감소             |

- 출처: https://nginx.org/en/docs/http/ngx_http_core_module.html

### 보안 설정

| 항목                               | 설정                        | 근거                                                 |
|------------------------------------|-----------------------------|------------------------------------------------------|
| ssl_protocols                      | TLSv1.2 TLSv1.3             | TLS 1.0/1.1 제거                                     |
| ssl_ciphers                        | Mozilla Intermediate 프로필 | ssl-config.mozilla.org                               |
| ssl_prefer_server_ciphers          | off                         | Mozilla Intermediate 5.7 기준 (TLS 1.3에서는 무의미) |
| add_header X-Frame-Options         | DENY 또는 SAMEORIGIN        | Clickjacking 방지                                    |
| add_header X-Content-Type-Options  | nosniff                     | MIME sniffing 방지                                   |
| add_header X-XSS-Protection        | 0                           | 최신 브라우저에서 deprecated, CSP 사용               |
| add_header Content-Security-Policy | default-src self            | XSS 방지 기본                                        |

- 출처: https://ssl-config.mozilla.org/
- 출처: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

### 디렉토리 보안

```nginx
autoindex off;                              # 디렉토리 리스팅 차단
location ~ /\. { deny all; }               # 숨김 파일(.htaccess 등) 차단
location ~ \.(conf|sql|env)$ { deny all; } # 설정파일 접근 차단
```

### 파일 퍼미션 (ISMS-P 2.6.2, 2.10.3)

| 대상            | 권장 퍼미션 | 소유자      |
|-----------------|-------------|-------------|
| /etc/nginx/     | 750         | root:root   |
| nginx.conf      | 640         | root:root   |
| DocumentRoot    | 755         | root:nginx  |
| 정적 파일       | 644         | root:nginx  |
| 업로드 디렉토리 | 770         | nginx:nginx |
| 로그 디렉토리   | 750         | root:root   |
| SSL 인증서      | 600         | root:root   |

### 버전별 주요 변경사항 (Nginx)

| 버전    | 변경 사항                                        | 영향                                  |
|---------|--------------------------------------------------|---------------------------------------|
| 1.25.1+ | `listen` 줄 `http2` 파라미터 deprecated          | `http2 on;` 별도 디렉티브 사용        |
| 1.25.0+ | `listen ... quic` QUIC/HTTP3 실험적 지원         | `http3 on;` 별도 디렉티브             |
| 1.23.4+ | TLSv1.3 프로토콜 기본 활성화                     | `ssl_protocols` 별도 설정 필요성 감소 |
| 1.15.0+ | `ssl` 디렉티브 deprecated, `listen ... ssl` 사용 | 1.25.1에서 `ssl` 디렉티브 제거        |
| 1.9.0+  | stream 모듈 (TCP/UDP 프록시) 추가                | `stream {}` 블록 사용 가능            |

### 버전별 주요 변경사항 (Apache)

| 버전    | 변경 사항                       | 영향                                |
|---------|---------------------------------|-------------------------------------|
| 2.4.58  | mod_http2 `H2EarlyHint` 추가    | HTTP 103 Early Hints 응답 헤더 지원 |
| 2.4.49  | CVE-2021-41773 (path traversal) | 즉시 패치 필수                      |
| 2.4.19+ | mod_proxy_http2 백엔드 H2 지원  | 리버스 프록시 H2 (실험 모듈)        |
| 2.4+    | event MPM 기본                  | prefork에서 전환 권장               |

## 2. Apache HTTP Server

### 버전 (확인일: 2026-07-08)

| 채널   | 버전   | 비고           |
|--------|--------|----------------|
| Stable | 2.4.68 | 현재 유일 지원 |

- 2.2.x: EOL (2017-12)
- 출처: https://httpd.apache.org/download.cgi
- 2026-11-09 확인: 최신 2.4.70(2026-11-06)입니다(httpd.apache.org).

### 핵심 설정

| 항목            | 권장값                   | 근거                      |
|-----------------|--------------------------|---------------------------|
| ServerTokens    | Prod                     | 최소 정보 노출            |
| ServerSignature | Off                      | 에러 페이지 버전 숨김     |
| TraceEnable     | Off                      | TRACE 메서드 비활성화     |
| Options         | -Indexes -FollowSymLinks | 리스팅 차단, 심볼릭 제한  |
| AllowOverride   | None (프로덕션)          | .htaccess 비활성화 (성능) |

- 출처: https://httpd.apache.org/docs/2.4/misc/security_tips.html

### MPM 선택

| MPM     | 적합 워크로드        | 특징                        |
|---------|----------------------|-----------------------------|
| event   | 일반 웹 (기본, 2.4+) | 비동기 I/O, 커넥션 효율     |
| worker  | 고트래픽 동적 처리   | 멀티스레드                  |
| prefork | mod_php 필수 시      | 프로세스 기반 (메모리 높음) |

- 출처: https://httpd.apache.org/docs/2.4/mpm.html

### 보안 설정

| 항목                       | 설정                       | 근거                   |
|----------------------------|----------------------------|------------------------|
| SSLProtocol                | all -SSLv3 -TLSv1 -TLSv1.1 | TLS 1.2+ 강제          |
| SSLCipherSuite             | Mozilla Intermediate       | ssl-config.mozilla.org |
| Header set X-Frame-Options | DENY                       | Clickjacking 방지      |
| FileETag                   | None                       | inode 정보 노출 방지   |

- 출처: https://httpd.apache.org/docs/2.4/mod/mod_ssl.html

### 파일 퍼미션 (ISMS-P 2.6.2, 2.10.3)

| 대상            | 권장 퍼미션 | 소유자        |
|-----------------|-------------|---------------|
| /etc/httpd/     | 750         | root:root     |
| httpd.conf      | 640         | root:root     |
| DocumentRoot    | 755         | root:apache   |
| 정적 파일       | 644         | root:apache   |
| CGI 디렉토리    | 750         | root:apache   |
| 업로드 디렉토리 | 770         | apache:apache |
| 로그 디렉토리   | 750         | root:root     |
| SSL 인증서      | 600         | root:root     |

## 3. HAProxy

### 확인 범위 (확인일: 2026-11-06)

2026-11-06에 haproxy.org 첫 화면, haproxy-3.4 git 저장소의 `doc/intro.txt`·`doc/configuration.txt`(version 3.4, 2026/10/14)·`doc/management.txt`, `admin/systemd/haproxy.service.in`, `addons/promex/README`, Launchpad API, 작업 서버의 `apt-cache policy haproxy`를 읽었습니다. HAProxy를 설치·실행하지 않았습니다.

### Version status

| 분기 | 최신   | 상태                | 지원 종료 |
|------|--------|---------------------|-----------|
| 3.5  | dev11  | 개발                | 2028-Q1   |
| 3.4  | 3.4.7  | LTS                 | 2031-Q2   |
| 3.3  | 3.3.17 | stable              | 2027-Q1   |
| 3.2  | 3.2.26 | LTS                 | 2030-Q2   |
| 3.1  | 3.1.17 | 지원 종료           | 2026-Q1   |
| 3.0  | 3.0.30 | LTS                 | 2029-Q2   |
| 2.9  | 2.9.15 | 지원 종료           | 2025-Q1   |
| 2.8  | 2.8.31 | critical fixes only | 2028-Q2   |
| 2.6  | 2.6.35 | critical fixes only | 2027-Q2   |

- 짝수 분기는 LTS(5년), 홀수 분기는 stable(짧은 지원)입니다.
- 3.4.0 배포 2026-06-03: CLI로 backend 생성·게시·삭제, HTTP/2 flood 제한, ACME DNS-01·dns-persist-01, systemd unit의 `conf.d` 디렉터리, OpenTelemetry filter(OpenTracing은 폐기 예정).
- 3.3.0 배포 2025-11-26: 기본 분산 알고리즘이 `random(2)`로 바뀜, reload 후에도 통계 유지, KTLS.
- 2026-02-12 공지: QUIC 파싱 취약점 CVE-2026-26081(3.0 이상)·CVE-2026-26080(3.2 이상), 조작된 패킷으로 프로세스 중단 위험. 수정판 3.0.12, 3.1.14, 3.2.12, 3.3.3.
- 작업 서버(Ubuntu 24.04) 기본 저장소 후보 `2.8.30-0ubuntu0.24.04.2`.
- Launchpad `~vbernat/haproxy-3.4` PPA의 게시 원본은 `3.4.7-1ppa1~resolute`(Ubuntu 26.04) 1건만 확인했습니다. 다른 Ubuntu 버전용 게시 여부는 확인하지 않았습니다.

### 동작 구조 (intro.txt 3.1·3.2)

- 하는 일: TCP proxy, HTTP reverse proxy, TLS 종료·시작, TCP·HTTP 정규화, 헤더 수정, 내용 기반 분기, 분산, 속도 제한, 남용 방지, 압축, 메모리 캐시, FastCGI gateway.
- 하지 않는 일: 브라우저용 forward proxy, 본문 변경, 정적 웹 서버(chroot 후 파일 접근 안 함), 패킷 기반 LB(NAT·DSR 없음, IPVS 영역).
- event-driven non-blocking 엔진 + 우선순위 기반 멀티스레드 스케줄러. 처리 시간 대부분은 커널(TCP·HTTP close 15:85, keep-alive 30:70).
- 서버는 swap을 쓰면 안 되고 CPU를 쪼개 할당하거나 계산 작업과 공유하지 말 것. 성능 문제의 첫 조치가 CPU 수를 줄이는 것인 경우가 많음.
- 시작 시 설정을 모두 읽고 listen socket을 모두 bind한 뒤에야 시작하며, 실패하면 시작하지 않음.
- 시작 후 하는 일 3가지: 연결 처리, 헬스체크, 다른 노드와 정보 교환(peers).
- 요청 처리 9단계: frontend 수신 → frontend 규칙 → backend 전달 → backend 규칙 → 서버 선택 → backend 응답 규칙 → frontend 응답 규칙 → 로그 → HTTP면 다음 요청 대기.
- TCP 모드는 연결 단위로, HTTP 모드는 요청 단위로 분산을 결정.

### 설정 기본값 (configuration.txt)

| 항목                       | 기본값·내용                                                                        |
|----------------------------|------------------------------------------------------------------------------------|
| `balance`                  | 다른 알고리즘·mode·option이 없으면 `random`, draw 기본 2                           |
| `roundrobin`               | 동적(가중치 실시간 변경 가능), backend당 활성 서버 4095개 한도                     |
| `source`·`uri`·`hash`      | 기본 정적(map-based), `hash-type consistent`로 변경 가능                           |
| `inter`·`rise`·`fall`      | 2000ms·2·3                                                                         |
| `option httpchk`           | 지정이 없으면 `OPTIONS / HTTP/1.0`, 새 방식은 `http-check send meth … uri … ver …` |
| HTTP 연결 모드             | 기본 keep-alive, `option http-server-close`는 서버 쪽만 닫음                       |
| `timeout http-request`     | 없으면 `timeout client`가 적용, 설정 시 초과 시 408                                |
| `timeout http-keep-alive`  | 없으면 `timeout http-request` 사용                                                 |
| `timeout queue`            | 없으면 `timeout connect` 사용                                                      |
| `timeout tunnel`           | WebSocket·CONNECT 전환 뒤 적용, 예시 `1h`                                          |
| `retries`                  | 기본은 새 연결 시도에만 적용, 재시도 전 min(timeout connect, 1s) 대기              |
| `maxconn`(global)          | 없으면 `ulimit -nH` 등 FD 한도에서 자동 계산                                       |
| `nbthread`                 | CPU affinity를 지원하면 사용 가능한 CPU 수, `haproxy -vv`에 표시                   |
| `ssl-min-ver`              | 기본 TLSv1.2                                                                       |
| `master-worker` 키워드     | deprecated, `-W` 또는 `-Ws` 사용                                                   |
| `http-request use-service` | 예: `prometheus-exporter if { path /metrics }`                                     |

- stick-table 예시: `stick-table type ip size 1m expire 5m store http_req_rate(10s)`와 `track-sc`, `sc_http_req_rate`.

### 관리 (management.txt, systemd unit)

- `-f <dir>`은 디렉터리 안의 `.cfg` 파일만, 숨김 파일을 빼고, 이름순(LC_COLLATE=C)으로 읽음. 파일마다 section 경계(`global`, `defaults`, `frontend` 등)로 시작해야 함.
- master-worker: master가 worker를 관리하고 `SIGUSR2`로 reload. 새 worker를 띄우고 이전 worker는 진행 중인 작업이 끝날 때까지 유지. master-worker 모드에서는 `expose-fd listeners` 없이 socket을 넘김.
- master CLI `reload`: `kill -USR2`와 같고 결과(`Success=1`)를 돌려줌. socat 기본 timeout 0.5s라 `-t300` 예시. `hard-reload` 별도.
- Runtime API: `set server <b>/<s> state ready|drain|maint`(drain은 분산에서 빼되 헬스체크·persistent 연결 유지, maint는 트래픽·헬스체크 모두 중단), `set server … weight`, `show stat`, `show info`, `show servers state`, `show errors`, `show sess`, `show table`, `clear table`, `add server`·`del server`, 3.4의 `add backend`·`publish backend`.
- 3.4 systemd unit: `-Ws -f $CONFIG -f $CFGDIR -p $PIDFILE -S /run/haproxy-master.sock`, `CFGDIR=/etc/haproxy/conf.d`, `ExecReload`는 `-c` 검사 뒤 `kill -USR2`, `Type=notify`, `Restart=always`. 배포판 패키지 unit은 다를 수 있음.
- Prometheus exporter(PROMEX)는 기본 빌드에 포함되지 않음(`USE_PROMEX=1`). 포함되면 `haproxy -vv`에 `Built with the Prometheus exporter as a service`.

### 이중화: peers와 Keepalived (확인일: 2026-11-06)

- HAProxy peers(configuration.txt 11.2): stick-table 항목을 TCP로 multi-master 전파, 값은 합산 없이 덮어씀. `conn_cur`는 기본으로 받지 않음(`recv-only` 표 예외). reload 때 이전 worker가 새 worker에 전체 항목을 먼저 보냄. 서버는 ID로 식별하므로 노드 간 설정을 같게 유지. 로컬 peer 이름은 hostname, `localpeer`나 `-L`로 지정하고 모든 노드에 같은 peers 선언을 권장. `peers` 안의 `table`은 `<section>/<table>`로 참조. CLI `show peers`.
- Keepalived 태그: v2.4.3(2026-07-20), v2.4.0(2026-06-22), v2.3.4(2025-06-10). GitHub 릴리스 항목은 없음. 작업 서버(Ubuntu 24.04) 후보 `1:2.2.8-1build2`.
- `keepalived.conf(5)` v2.4.3: `vrrp_script`의 `interval` 기본 1초, `weight` 기본 0(실패 시 FAULT), `-253..253`. `priority` 1~255(255는 주소 소유자), MASTER는 50 높게 권장. 넘어가기 시간 `3 × advert_int + skew_time`(advert 1·priority 128이면 약 3.5초). `nopreempt`는 초기 state가 MASTER가 아니어야 동작. `authentication`은 RFC 3768에서 제거, unicast 외 사용 비권장. `script_user` 기본 `keepalived_script`(없으면 실행 사용자), `enable_script_security`는 쓰기 가능한 경로의 root 실행 거부.
- v2.2.8 man 문서: `unicast_peer`, `unicast_fault_no_peer`, `check_unicast_src`, `enable_script_security`, `nopreempt` 있음. `auth_hmac` 없음.
- `keepalived(8)`: `-t, --config-test[=FILE]`, 오류 시 0이 아닌 종료 코드.
- Linux 커널 ip-sysctl: `ip_nonlocal_bind`는 로컬에 없는 IP bind 허용, 일부 애플리케이션을 깨뜨릴 수 있다고 명시.

### ACME (확인일: 2026-11-06)

- configuration.txt 12.8: 실험 기능(`expose-experimental-directives` 필요). challenge는 http-01(기본)·dns-01·dns-persist-01. dns 계열은 Data Plane API 등 외부 도구 필요, dns-persist-01은 `_validation-persist.<domain>` TXT를 한 번만 설정. 인증서·키는 메모리에만 있고 `dump ssl cert`나 `admin/cli/haproxy-dump-certs`로 저장. 스케줄러는 시작 시와 12시간마다 확인하고 `notAfter - (notAfter - notBefore)/12` 이후 갱신(notBefore 없으면 7일 전). `directory` 기본값 없음. 기본 키 ECDSA P-384, RSA는 2048비트. `account-key` 없으면 `<section>.account.key`. `challenge-ready` 기본 dns-01 `cli`, dns-persist-01 `dns,delay`. `dns-delay` 30초, `dns-timeout` 600초. `profile`(draft-ietf-acme-profiles), EAB(`eab-key-id`·`eab-mac-key`·`eab-mac-alg` 기본 HS256).
- configuration.txt 12.7: `crt-store`의 `load crt ... acme <section> domains "<a>,<b>"`이면 파일 없이 임시 키 쌍으로 시작. 첫 도메인이 CN.
- management.txt: `acme renew <crt>`, `acme status`(인증서·section·Running/Scheduled/Stopped·만료·예정 시각), `dump ssl cert`(admin 권한).
- 3.4 문서에서 ARI(renewalInfo)나 갱신 시점 조정 설정은 찾지 못함.
- haproxy-dump-certs(3.4 소스): 실험 스크립트, 지문이 같으면 건너뜀, 키 쌍 불일치면 저장 안 함, 이전 파일을 `.old.<시각>`으로 이동. `-S`, `-s`, `-p`, `-n`.
- 공식 wiki ACME 안내: 3.2부터 실험 기능, 3.3부터 crt-store로 파일 없이 시작, reload 시 저장하지 않으면 재발급되어 CA 발급 제한 위험, systemd `ExecStop`·`ExecReload`에 저장 스크립트 추가 예시. wiki는 기본 키를 RSA2048로 적었지만 3.2·3.3·3.4 configuration.txt의 `keytype` 기본값은 ECDSA P-384(EC384)입니다(2026-11-09 확인).
- haproxy.org 공지: 3.3에서 Data Plane API 경유 DNS-01, 3.4에서 DNS-01·dns-persist-01·EAB·발급 프로필.
- Let's Encrypt directory(운영·staging) 응답에 `renewalInfo` 항목과 프로필 `classic`·`shortlived`·`tlsserver`가 있음.

### 적용 범위와 제한

- 설정 예시는 위 문서를 근거로 썼으며 `haproxy -c`로 검사하지 않았습니다.
- 배포판 패키지(Ubuntu·RHEL)의 unit 파일, PROMEX 포함 여부, 기본 `haproxy.cfg`는 확인하지 않았습니다.

## 4. TLS 설정 공통 (Mozilla SSL Configuration Generator)

- 출처: https://ssl-config.mozilla.org/guidelines/5.7.json (v5.7, 확인일: 2026-07-14)
- 2026-11-09 확인: 최신판은 6.0(`guidelines/latest.json`)이며, 이 노트와 본문은 5.7 기준입니다.
- 검증: https://www.ssllabs.com/ssltest/ (A+ 목표)

### 프로필 비교

| 프로필       | 대상            | 최소 TLS | 대상 클라이언트                       |
|--------------|-----------------|----------|---------------------------------------|
| Modern       | 최신 클라이언트 | TLS 1.3  | Firefox 63+, Chrome 70+, Safari 12.1+ |
| Intermediate | 범용 (권장)     | TLS 1.2  | Firefox 27+, Chrome 31+, IE 11/Win7   |
| Old          | 레거시 호환     | TLS 1.0  | 매우 오래된 클라이언트 (비권장)       |

### Intermediate 프로필 상세 (프로덕션 권장)

| 항목                      | 값                |
|---------------------------|-------------------|
| ssl_protocols             | TLSv1.2 TLSv1.3   |
| ssl_prefer_server_ciphers | off               |
| HSTS max-age              | 63072000 (2년)    |
| DH param size             | 2048bit           |
| RSA key size              | 2048bit           |
| OCSP Stapling             | on                |
| 인증서 최대 수명          | 366일 (권장 90일) |

### Intermediate ssl_ciphers (OpenSSL 표기)

```
ECDHE-ECDSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-GCM-SHA256
ECDHE-ECDSA-AES256-GCM-SHA384
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-ECDSA-CHACHA20-POLY1305
ECDHE-RSA-CHACHA20-POLY1305
DHE-RSA-AES128-GCM-SHA256
DHE-RSA-AES256-GCM-SHA384
DHE-RSA-CHACHA20-POLY1305
```

### Nginx 적용 예시

```nginx
ssl_protocols       TLSv1.2 TLSv1.3;
ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache   shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling        on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=63072000" always;
```

### Apache 적용 예시

```apache
SSLProtocol             all -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite          ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305
SSLHonorCipherOrder     off
SSLSessionTickets       off
SSLUseStapling On
SSLStaplingCache "shmcb:logs/ssl_stapling(32768)"
Header always set Strict-Transport-Security "max-age=63072000"
```

### 주의사항

- `HIGH:!aNULL:!MD5`는 구식 표현. 현재 권장되지 않음 (약한 cipher 포함 가능)
- `ssl_prefer_server_ciphers off`: TLS 1.3에서는 서버 순서가 무의미, 1.2에서도 모든 cipher가 강력하므로 off 권장
- Nginx 1.25.1+에서 `listen 443 ssl http2;`의 `http2`는 deprecated → `http2 on;` 별도 디렉티브 사용
