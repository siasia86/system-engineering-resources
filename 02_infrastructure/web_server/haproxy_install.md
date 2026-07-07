# HAProxy 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 기본 설정 (haproxy.cfg)](#4-기본-설정-haproxycfg) / [5. L4 로드 밸런서](#5-l4-로드-밸런서) / [6. L7 로드 밸런서](#6-l7-로드-밸런서) |
| [7. SSL/TLS 터미네이션](#7-ssltls-터미네이션) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

### HAProxy vs Nginx 로드 밸런서 비교

| 항목          | HAProxy              | Nginx                   |
|---------------|----------------------|-------------------------|
| 주 용도       | 로드 밸런서 전용     | 웹 서버 + 리버스 프록시 |
| L4 (TCP)      | ✅ 강력              | ✅ stream 모듈          |
| L7 (HTTP)     | ✅                   | ✅                      |
| 헬스체크      | 정교한 다중 방식     | 기본적                  |
| 통계 대시보드 | 내장                 | 별도 모듈 필요          |
| 성능          | 매우 높음            | 높음                    |
| 권장 상황     | 고성능 LB, DB 프록시 | 웹 서버 겸용            |

### 시스템 요구사항

| 항목 | 최소          | 권장                     |
|------|---------------|--------------------------|
| OS   | Ubuntu 20.04+ | Ubuntu 22.04+ / Rocky 9+ |
| RAM  | 256 MB        | 1 GB 이상                |
| 포트 | 80, 443       | 80/tcp, 443/tcp          |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치 방법 A: APT (Ubuntu 기본 저장소)

```bash
sudo apt install haproxy -y
sudo systemctl enable --now haproxy
```

### 2-3. 설치 방법 B: PPA (최신 버전)

```bash
sudo add-apt-repository ppa:vbernat/haproxy-2.9 -y
sudo apt update
sudo apt install haproxy=2.9.\* -y
sudo systemctl enable --now haproxy
```

### 2-4. 설치 확인

```bash
haproxy -v
sudo systemctl status haproxy --no-pager | head -5
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. DNF 설치

```bash
sudo dnf install haproxy -y
sudo systemctl enable --now haproxy
```

### 3-3. 방화벽 + SELinux

```bash
# firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# SELinux: 포트 바인딩 허용
sudo setsebool -P haproxy_connect_any 1
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 기본 설정 (haproxy.cfg)

```bash
sudo vi /etc/haproxy/haproxy.cfg
```

```
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    maxconn 50000
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    option  forwardfor
    option  http-server-close
    timeout connect  5s
    timeout client   30s
    timeout server   30s
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 503 /etc/haproxy/errors/503.http
```

```bash
# 설정 문법 검사
sudo haproxy -c -f /etc/haproxy/haproxy.cfg

# 무중단 설정 반영
sudo systemctl reload haproxy
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. L4 로드 밸런서

TCP 레벨에서 분산. MySQL, Redis 등 DB 프록시에 사용.

```
# /etc/haproxy/haproxy.cfg 에 추가

frontend mysql_front
    bind *:3306
    mode tcp
    default_backend mysql_back

backend mysql_back
    mode tcp
    balance roundrobin
    option tcp-check
    server db1 10.0.1.11:3306 check
    server db2 10.0.1.12:3306 check backup
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. L7 로드 밸런서

HTTP 헤더, URL 경로 기반 분산.

```
frontend http_front
    bind *:80
    mode http
    option forwardfor

    # URL 경로 기반 라우팅
    acl is_api  path_beg /api/
    acl is_static path_beg /static/

    use_backend api_back    if is_api
    use_backend static_back if is_static
    default_backend web_back

backend web_back
    mode http
    balance leastconn
    option httpchk GET /health
    http-check expect status 200
    server web1 10.0.1.11:8080 check inter 5s rise 2 fall 3
    server web2 10.0.1.12:8080 check inter 5s rise 2 fall 3
    server web3 10.0.1.13:8080 check inter 5s rise 2 fall 3

backend api_back
    mode http
    balance roundrobin
    server api1 10.0.1.21:8080 check
    server api2 10.0.1.22:8080 check

backend static_back
    mode http
    server static1 10.0.1.31:80 check
```

### 분산 알고리즘

| 알고리즘    | 설정         | 설명                    |
|-------------|--------------|-------------------------|
| Round Robin | `roundrobin` | 순서대로 분산 (기본)    |
| Least Conn  | `leastconn`  | 연결 수 적은 서버 우선  |
| Source IP   | `source`     | 클라이언트 IP 기반 고정 |
| URI         | `uri`        | 요청 URI 기반 고정      |

[⬆ 목차로 돌아가기](#목차)

---

## 7. SSL/TLS 터미네이션

```bash
# 인증서 + 키를 하나의 PEM 파일로 합치기
sudo cat /etc/letsencrypt/live/example.com/fullchain.pem \
         /etc/letsencrypt/live/example.com/privkey.pem \
    | sudo tee /etc/haproxy/certs/example.com.pem
sudo chmod 600 /etc/haproxy/certs/example.com.pem
```

```
frontend https_front
    bind *:443 ssl crt /etc/haproxy/certs/example.com.pem
    bind *:80
    mode http
    http-request redirect scheme https unless { ssl_fc }

    # HSTS
    http-response set-header Strict-Transport-Security "max-age=31536000"

    default_backend web_back
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: 통계 대시보드 활성화

```
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats auth admin:SecurePassword123
    stats hide-version
```

```bash
# 접속: http://SERVER_IP:8404/stats
```

### Tip 2: 헬스체크 세부 설정

```
backend web_back
    option httpchk GET /health HTTP/1.1\r\nHost:\ example.com
    http-check expect status 200
    server web1 10.0.1.11:8080 check inter 5s rise 2 fall 3
    # inter: 체크 간격, rise: 복구 판정 횟수, fall: 장애 판정 횟수
```

### Tip 3: 소켓으로 런타임 제어

```bash
# 서버 일시 비활성화 (배포 시)
echo "disable server web_back/web1" | sudo socat stdio /run/haproxy/admin.sock

# 서버 재활성화
echo "enable server web_back/web1" | sudo socat stdio /run/haproxy/admin.sock

# 현재 상태 확인
echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d',' -f1,2,18
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                    | 원인                  | 해결 방법                            |
|-------------------------|-----------------------|--------------------------------------|
| `haproxy -c` 실패       | 설정 문법 오류        | 오류 메시지 라인 확인                |
| 503 Service Unavailable | 모든 백엔드 서버 다운 | `show stat` 으로 서버 상태 확인      |
| 백엔드 헬스체크 실패    | 헬스체크 경로 없음    | `/health` 엔드포인트 확인            |
| SSL 인증서 오류         | PEM 파일 형식 오류    | cert + key 순서 확인                 |
| RHEL: 포트 바인딩 실패  | SELinux 차단          | `setsebool -P haproxy_connect_any 1` |

```bash
# 에러 로그 확인
sudo journalctl -u haproxy -f
sudo tail -50 /var/log/haproxy.log
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- HAProxy Documentation: [docs.haproxy.org](https://docs.haproxy.org/) — ★★★☆☆
- HAProxy Configuration Manual: [cbonte.github.io/haproxy-dconv](https://cbonte.github.io/haproxy-dconv/2.9/configuration.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
