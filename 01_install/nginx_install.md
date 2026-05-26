# Nginx 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 기본 설정](#4-기본-설정) / [5. 가상 호스트 (Server Block)](#5-가상-호스트-server-block) / [6. 리버스 프록시](#6-리버스-프록시) |
| [7. SSL/TLS (Let's Encrypt)](#7-ssltls-lets-encrypt) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

### 시스템 요구사항

| 항목 | 최소            | 권장                     |
|------|-----------------|--------------------------|
| OS   | Ubuntu 20.04+   | Ubuntu 22.04+ / Rocky 9+ |
| RAM  | 256 MB          | 1 GB 이상                |
| 포트 | 80/tcp, 443/tcp | 80/tcp, 443/tcp          |

### 주요 용도

| 용도           | 설명                             |
|----------------|----------------------------------|
| 웹 서버        | 정적 파일 서빙                   |
| 리버스 프록시  | 앱 서버(Node, Python, Java) 앞단 |
| 로드 밸런서    | upstream 그룹으로 트래픽 분산    |
| SSL 터미네이션 | HTTPS 처리 후 HTTP로 백엔드 전달 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치 방법 A: APT (Ubuntu 기본 저장소)

```bash
sudo apt install nginx -y
sudo systemctl enable --now nginx
```

### 2-3. 설치 방법 B: Nginx 공식 저장소 (최신 stable)

```bash
sudo apt install curl gnupg2 ca-certificates lsb-release -y
curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor \
    | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] \
    http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" \
    | sudo tee /etc/apt/sources.list.d/nginx.list

sudo apt update
sudo apt install nginx -y
sudo systemctl enable --now nginx
```

### 2-4. 설치 확인

```bash
nginx -v
sudo systemctl status nginx --no-pager | head -5
curl -s -o /dev/null -w "%{http_code}" http://localhost/
# 200
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. 설치 방법 A: DNF (AppStream)

```bash
sudo dnf install nginx -y
sudo systemctl enable --now nginx
```

### 3-3. 설치 방법 B: Nginx 공식 저장소

```bash
sudo tee /etc/yum.repos.d/nginx.repo << 'EOF'
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/rhel/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
EOF

sudo dnf install nginx -y
sudo systemctl enable --now nginx
```

### 3-4. 방화벽 + SELinux

```bash
# firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# SELinux: 리버스 프록시 사용 시 네트워크 연결 허용
sudo setsebool -P httpd_can_network_connect 1
```

### 3-5. 설치 확인

```bash
nginx -v
sudo systemctl status nginx --no-pager | head -5
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 기본 설정

### 디렉토리 구조

```
/etc/nginx/
├── nginx.conf              # 메인 설정
├── conf.d/                 # 추가 설정 (include)
├── sites-available/        # 가상 호스트 정의 (Ubuntu)
├── sites-enabled/          # 활성화된 가상 호스트 심볼릭 링크
└── snippets/               # 재사용 설정 조각
```

### nginx.conf 핵심 설정

```nginx
# /etc/nginx/nginx.conf
user www-data;
worker_processes auto;          # CPU 코어 수에 맞게 자동 설정
pid /run/nginx.pid;

events {
    worker_connections 1024;    # 워커당 최대 연결 수
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;          # nginx 버전 노출 방지

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 로그
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';
    access_log /var/log/nginx/access.log main;
    error_log  /var/log/nginx/error.log warn;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;   # Ubuntu
}
```

```bash
# 설정 문법 검사
sudo nginx -t

# 무중단 설정 반영
sudo nginx -s reload
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 가상 호스트 (Server Block)

### 정적 사이트

```bash
sudo vi /etc/nginx/sites-available/example.com
```

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/example.com;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    access_log /var/log/nginx/example.com.access.log;
    error_log  /var/log/nginx/example.com.error.log;
}
```

```bash
# 활성화
sudo ln -s /etc/nginx/sites-available/example.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 리버스 프록시

### 단일 앱 서버

```nginx
# /etc/nginx/sites-available/app
server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass         http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_set_header   Upgrade           $http_upgrade;
        proxy_set_header   Connection        "upgrade";  # WebSocket 지원
        proxy_read_timeout 60s;
    }
}
```

### 로드 밸런서 (upstream)

```nginx
upstream backend {
    least_conn;                         # 최소 연결 수 기준 분산
    server 10.0.1.11:3000 weight=3;
    server 10.0.1.12:3000 weight=1;
    server 10.0.1.13:3000 backup;      # 나머지 모두 다운 시 사용
    keepalive 32;
}

server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
    }
}
```

### upstream 분산 방식

| 방식        | 설정         | 설명                    |
|-------------|--------------|-------------------------|
| Round Robin | (기본값)     | 순서대로 분산           |
| Least Conn  | `least_conn` | 연결 수 적은 서버 우선  |
| IP Hash     | `ip_hash`    | 클라이언트 IP 기반 고정 |
| Weight      | `weight=N`   | 가중치 비율 분산        |

[⬆ 목차로 돌아가기](#목차)

---

## 7. SSL/TLS (Let's Encrypt)

### Certbot 설치 및 인증서 발급

```bash
# Ubuntu
sudo apt install certbot python3-certbot-nginx -y

# Rocky
sudo dnf install certbot python3-certbot-nginx -y

# 인증서 발급 + nginx 자동 설정
sudo certbot --nginx -d example.com -d www.example.com \
    --email user@example.com --agree-tos --non-interactive

# 자동 갱신 확인
sudo certbot renew --dry-run
```

### SSL 설정 (수동)

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://127.0.0.1:3000;
    }
}

# HTTP → HTTPS 리다이렉트
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: 설정 파일 분리

```bash
# 공통 proxy 헤더를 snippet으로 분리
sudo tee /etc/nginx/snippets/proxy-params.conf << 'EOF'
proxy_http_version 1.1;
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
EOF

# 사용
# include snippets/proxy-params.conf;
```

### Tip 2: 접속 제한

```nginx
# IP 허용/차단
location /admin {
    allow 10.0.1.0/24;
    deny all;
}

# Rate Limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

### Tip 3: 로그 분석

```bash
# 상위 접속 IP
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# 상태 코드별 집계
sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# 실시간 로그
sudo tail -f /var/log/nginx/access.log
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                          | 원인                     | 해결 방법                                                       |               |
|-------------------------------|--------------------------|-----------------------------------------------------------------|---------------|
| `nginx -t` 실패               | 설정 문법 오류           | 오류 메시지 라인 확인 후 수정                                   |               |
| 502 Bad Gateway               | 백엔드 서버 다운         | 백엔드 프로세스 상태 확인                                       |               |
| 504 Gateway Timeout           | 백엔드 응답 지연         | `proxy_read_timeout` 값 증가                                    |               |
| 403 Forbidden                 | 파일 권한 또는 SELinux   | `chmod`, `chown` 확인 / `setsebool httpd_can_network_connect 1` |               |
| `bind() to 0.0.0.0:80 failed` | 포트 충돌 또는 권한 부족 | `ss -tlnp \                                                     | grep 80` 확인 |
| 설정 반영 안 됨               | reload 미실행            | `sudo nginx -s reload`                                          |               |

```bash
# 에러 로그 확인
sudo tail -50 /var/log/nginx/error.log

# 프로세스 확인
ps aux | grep nginx
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Nginx Documentation: [nginx.org/en/docs](https://nginx.org/en/docs/) — ★★★☆☆
- Nginx Beginner's Guide: [nginx.org/en/docs/beginners_guide](https://nginx.org/en/docs/beginners_guide.html) — ★★☆☆☆

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
