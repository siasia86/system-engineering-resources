# Apache HTTP Server 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. MPM (Multi-Processing Module)](#4-mpm-multi-processing-module) / [5. 기본 설정](#5-기본-설정) / [6. 가상 호스트 (Virtual Host)](#6-가상-호스트-virtual-host) |
| [7. SSL/TLS (Let's Encrypt)](#7-ssltls-lets-encrypt) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

### Apache vs Nginx 비교

| 항목        | Apache                      | Nginx                           |
|-------------|-----------------------------|---------------------------------|
| 아키텍처    | 프로세스/스레드 기반 (MPM)  | 이벤트 기반 (비동기)            |
| 동적 콘텐츠 | mod_php 등 모듈 내장 처리   | 외부 프로세스(FastCGI) 위임     |
| .htaccess   | ✅ 디렉토리별 설정 가능     | ❌ 미지원                       |
| 모듈 시스템 | 런타임 동적 로드            | 컴파일 타임 포함                |
| 설정 유연성 | 높음                        | 중간                            |
| 권장 상황   | PHP 앱, .htaccess 필요 환경 | 고성능 정적 서빙, 리버스 프록시 |

### 시스템 요구사항

| 항목 | 최소            | 권장                     |
|------|-----------------|--------------------------|
| OS   | Ubuntu 20.04+   | Ubuntu 22.04+ / Rocky 9+ |
| RAM  | 256 MB          | 1 GB 이상                |
| 포트 | 80/tcp, 443/tcp | 80/tcp, 443/tcp          |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치

```bash
sudo apt install apache2 -y
sudo systemctl enable --now apache2
```

### 2-3. 설치 확인

```bash
apache2 -v
sudo systemctl status apache2 --no-pager | head -5
curl -s -o /dev/null -w "%{http_code}" http://localhost/
# 200
```

### 2-4. Ubuntu 버전별 차이

| 항목        | Ubuntu 22.04        | Ubuntu 24.04        |
|-------------|---------------------|---------------------|
| Apache 버전 | 2.4.52              | 2.4.58              |
| 기본 MPM    | event               | event               |
| 설정 경로   | `/etc/apache2/`     | `/etc/apache2/`     |
| 로그 경로   | `/var/log/apache2/` | `/var/log/apache2/` |

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. 설치

```bash
sudo dnf install httpd -y
sudo systemctl enable --now httpd
```

🟡 RHEL 계열에서 패키지명은 `httpd`, 서비스명도 `httpd`입니다. Ubuntu의 `apache2`와 다릅니다.

### 3-3. 방화벽 + SELinux

```bash
# firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# SELinux: 리버스 프록시 사용 시
sudo setsebool -P httpd_can_network_connect 1

# SELinux: 비표준 DocumentRoot 사용 시
sudo semanage fcontext -a -t httpd_sys_content_t "/data/www(/.*)?"
sudo restorecon -Rv /data/www
```

### 3-4. 설치 확인

```bash
httpd -v
sudo systemctl status httpd --no-pager | head -5
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. MPM (Multi-Processing Module)

MPM은 Apache가 요청을 처리하는 방식을 결정하는 핵심 모듈입니다.
동시에 하나의 MPM만 활성화할 수 있습니다.

### Process Forking 개념

`fork()`는 프로세스가 자기 자신을 복제하여 자식 프로세스를 생성하는 시스템 콜입니다.

```
┌──────────┐
│  Parent  │  PID: 1000
│  (httpd) │
└────┬─────┘
     │ fork()
     v
┌──────────┐    ┌──────────┐
│  Parent  │    │  Child   │  PID: 1001 (copy of Parent)
│ PID:1000 │    │ PID:1001 │
└──────────┘    └──────────┘
```

3개 MPM 모두 `fork()`를 사용합니다. 차이는 fork 이후 요청을 어떻게 처리하느냐입니다.

```
┌─────────────────────────────────────────────────────────────┐
│ prefork                                                     │
│                                                             │
│ master ─fork()─┬─ child (1 request)                         │
│                ├─ child (1 request)                         │
│                └─ child (1 request)                         │
├─────────────────────────────────────────────────────────────┤
│ worker / event                                              │
│                                                             │
│ master ─fork()─┬─ child ─┬─ thread (1 request)              │
│                │         ├─ thread (1 request)              │
│                │         └─ thread (1 request)              │
│                └─ child ─┬─ thread (1 request)              │
│                          └─ thread (1 request)              │
└─────────────────────────────────────────────────────────────┘
```

- `fork()` = 프로세스를 만드는 방법 (3개 MPM 공통)
- MPM = 만든 프로세스 안에서 요청을 어떻게 분배하느냐의 차이

| 용어          | 설명                                              |
|---------------|---------------------------------------------------|
| `fork()`      | 현재 프로세스를 메모리째 복제하는 시스템 콜       |
| Copy-on-Write | 실제 쓰기 전까지 부모/자식이 메모리를 공유 (효율) |
| `exec()`      | fork 후 자식의 메모리를 다른 프로그램으로 교체    |

**MPM별 fork 사용 방식:**

| MPM     | 동작                                                          |
|---------|---------------------------------------------------------------|
| prefork | 요청마다 fork된 프로세스가 처리 (프로세스 격리, 메모리 많음)  |
| worker  | fork된 프로세스 안에서 스레드가 요청 처리 (메모리 절약)       |
| event   | worker와 동일 + Keep-Alive를 전용 스레드가 처리 (가장 효율적) |

### MPM 종류 비교

| 항목            | prefork                        | worker            | event                       |
|-----------------|--------------------------------|-------------------|-----------------------------|
| 처리 방식       | 프로세스 기반                  | 프로세스 + 스레드 | 프로세스 + 스레드 + 비동기  |
| Keep-Alive 처리 | 프로세스 점유 (비효율)         | 스레드 점유       | 전용 리스너 스레드 (효율적) |
| 메모리 사용     | 많음 (프로세스당 독립 메모리)  | 중간              | 적음                        |
| 스레드 안전성   | 필요 없음 (프로세스 격리)      | 필요              | 필요                        |
| mod_php 호환    | ✅ (libphp)                    | 🟡 ZTS 빌드 PHP만 | 🟡 ZTS 빌드 PHP만           |
| PHP 권장 방식   | mod_php (libphp)               | PHP-FPM (FastCGI) | PHP-FPM (FastCGI)           |
| 권장 상황       | 레거시 PHP, 비스레드 안전 모듈 | 중간 규모         | ✅ 현대적 환경 기본값       |

### 현재 MPM 확인

```bash
apache2ctl -M | grep mpm
# mpm_event_module (shared)  ← 현재 활성화된 MPM
```

### MPM 전환

```bash
# Ubuntu
sudo a2dismod mpm_event          # 현재 MPM 비활성화
sudo a2enmod  mpm_prefork        # 원하는 MPM 활성화
sudo systemctl restart apache2

# RHEL (/etc/httpd/conf.modules.d/00-mpm.conf 편집)
sudo vi /etc/httpd/conf.modules.d/00-mpm.conf
# LoadModule mpm_prefork_module modules/mod_mpm_prefork.so  ← 주석 해제
# LoadModule mpm_event_module  modules/mod_mpm_event.so    ← 주석 처리
sudo systemctl restart httpd
```

### MPM 설정 튜닝

#### prefork 설정

```apache
# /etc/apache2/mods-available/mpm_prefork.conf (Ubuntu)
# /etc/httpd/conf.modules.d/00-mpm.conf (RHEL)
<IfModule mpm_prefork_module>
    StartServers          5       # 시작 시 생성할 프로세스 수
    MinSpareServers       5       # 최소 유휴 프로세스 수
    MaxSpareServers       10      # 최대 유휴 프로세스 수
    MaxRequestWorkers     150     # 최대 동시 요청 수 (= 최대 프로세스 수)
    MaxConnectionsPerChild 0      # 프로세스당 최대 처리 요청 수 (0=무제한)
</IfModule>
```

#### worker 설정

```apache
<IfModule mpm_worker_module>
    StartServers          2       # 시작 시 생성할 프로세스 수
    MinSpareThreads       25      # 최소 유휴 스레드 수
    MaxSpareThreads       75      # 최대 유휴 스레드 수
    ThreadLimit           64      # 프로세스당 최대 스레드 수 (재시작 없이 변경 불가)
    ThreadsPerChild       25      # 프로세스당 스레드 수
    MaxRequestWorkers     150     # 최대 동시 요청 수 (= 프로세스 수 × ThreadsPerChild)
    MaxConnectionsPerChild 0
</IfModule>
```

#### event 설정

```apache
<IfModule mpm_event_module>
    StartServers          2
    MinSpareThreads       25
    MaxSpareThreads       75
    ThreadLimit           64
    ThreadsPerChild       25
    MaxRequestWorkers     150     # 최대 동시 요청 수
    MaxConnectionsPerChild 0
    # event MPM 전용: Keep-Alive 연결을 리스너 스레드가 처리
    # AsyncRequestWorkerFactor 2  # 비동기 연결 배수 (기본 2)
</IfModule>
```

### MaxRequestWorkers 계산 가이드

```
prefork:
  MaxRequestWorkers = 가용 RAM / 프로세스당 메모리
  예) 4GB RAM, 프로세스당 50MB → 4096 / 50 ≈ 80

worker / event:
  MaxRequestWorkers = 프로세스 수 × ThreadsPerChild
  예) StartServers=4, ThreadsPerChild=25 → 100
```

```bash
# 현재 Apache 메모리 사용량 확인
ps aux | grep apache2 | awk '{sum += $6} END {print sum/1024 " MB"}'
```

### PHP와 MPM 선택

```bash
# PHP-FPM 사용 시 (worker/event 권장)
sudo apt install php-fpm -y
sudo a2enmod proxy_fcgi setenvif
sudo a2enconf php8.3-fpm
sudo systemctl restart apache2

# mod_php 사용 시 (prefork 필요)
sudo apt install libapache2-mod-php -y
sudo a2dismod mpm_event
sudo a2enmod  mpm_prefork
sudo systemctl restart apache2
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 설정

### 디렉토리 구조 (Ubuntu)

```
/etc/apache2/
├── apache2.conf          # 메인 설정
├── ports.conf            # 리스닝 포트
├── envvars               # 환경 변수 (APACHE_RUN_USER 등)
├── mods-available/       # 사용 가능한 모듈 (.load, .conf)
├── mods-enabled/         # 활성화된 모듈 (심볼릭 링크)
├── sites-available/      # 가상 호스트 정의
├── sites-enabled/        # 활성화된 가상 호스트 (심볼릭 링크)
└── conf-available/       # 추가 설정
```

### apache2.conf 핵심 설정

```apache
# /etc/apache2/apache2.conf
ServerName localhost          # FQDN 경고 제거
Timeout 300
KeepAlive On
MaxKeepAliveRequests 100
KeepAliveTimeout 5

# 보안: 서버 정보 노출 최소화
ServerTokens Prod             # "Apache" 만 표시
ServerSignature Off           # 에러 페이지 서버 정보 제거

# 디렉토리 기본 설정
<Directory /var/www/>
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

### 모듈 관리

```bash
# 모듈 활성화 / 비활성화 (Ubuntu)
sudo a2enmod  rewrite ssl headers deflate
sudo a2dismod status

# 활성화된 모듈 목록
apache2ctl -M

# 설정 반영
sudo apache2ctl configtest && sudo systemctl reload apache2
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 가상 호스트 (Virtual Host)

### 정적 사이트

```bash
sudo vi /etc/apache2/sites-available/example.com.conf
```

```apache
<VirtualHost *:80>
    ServerName   example.com
    ServerAlias  www.example.com
    DocumentRoot /var/www/example.com

    <Directory /var/www/example.com>
        Options -Indexes +FollowSymLinks
        AllowOverride All          # .htaccess 허용
        Require all granted
    </Directory>

    ErrorLog  ${APACHE_LOG_DIR}/example.com.error.log
    CustomLog ${APACHE_LOG_DIR}/example.com.access.log combined
</VirtualHost>
```

```bash
sudo mkdir -p /var/www/example.com
sudo a2ensite example.com.conf
sudo apache2ctl configtest && sudo systemctl reload apache2
```

### 리버스 프록시

```bash
sudo a2enmod proxy proxy_http
```

```apache
<VirtualHost *:80>
    ServerName app.example.com

    ProxyPreserveHost On
    ProxyPass        / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/

    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Real-IP %{REMOTE_ADDR}s
</VirtualHost>
```

### URL 리다이렉트 / Rewrite

```apache
# mod_rewrite 활성화 필요: sudo a2enmod rewrite

<VirtualHost *:80>
    ServerName example.com

    # HTTP → HTTPS 리다이렉트
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. SSL/TLS (Let's Encrypt)

```bash
# Ubuntu
sudo apt install certbot python3-certbot-apache -y

# Rocky
sudo dnf install certbot python3-certbot-apache -y

# 인증서 발급 + Apache 자동 설정
sudo certbot --apache -d example.com -d www.example.com \
    --email user@example.com --agree-tos --non-interactive

# 자동 갱신 확인
sudo certbot renew --dry-run
```

### SSL 가상 호스트 (수동)

```apache
<VirtualHost *:443>
    ServerName example.com

    SSLEngine on
    SSLCertificateFile    /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

    SSLProtocol           all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite        HIGH:!aNULL:!MD5
    SSLHonorCipherOrder   on

    Header always set Strict-Transport-Security "max-age=31536000"

    DocumentRoot /var/www/example.com
</VirtualHost>
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: server-status로 실시간 모니터링

```bash
sudo a2enmod status
```

```apache
# /etc/apache2/conf-available/server-status.conf
<Location /server-status>
    SetHandler server-status
    Require ip 127.0.0.1 10.0.1.0/24   # 내부 IP만 허용
</Location>
```

```bash
sudo a2enconf server-status
sudo systemctl reload apache2

# 텍스트 형식으로 확인
curl -s http://localhost/server-status?auto
```

### Tip 2: 로그 분석

```bash
# 상위 접속 IP
sudo awk '{print $1}' /var/log/apache2/access.log | sort | uniq -c | sort -rn | head -10

# 상태 코드별 집계
sudo awk '{print $9}' /var/log/apache2/access.log | sort | uniq -c | sort -rn

# 슬로우 요청 확인 (응답 시간 기록 시)
sudo awk '{print $NF, $7}' /var/log/apache2/access.log | sort -rn | head -10
```

### Tip 3: 보안 헤더 설정

```bash
sudo a2enmod headers
```

```apache
# /etc/apache2/conf-available/security-headers.conf
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

```bash
sudo a2enconf security-headers
sudo systemctl reload apache2
```

### Tip 4: 무중단 설정 반영

```bash
# 설정 검증 후 reload (graceful — 기존 연결 유지)
sudo apache2ctl configtest && sudo systemctl reload apache2

# 완전 재시작 (기존 연결 끊김)
sudo systemctl restart apache2
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                | 원인                             | 해결 방법                                                     |               |
|-------------------------------------|----------------------------------|---------------------------------------------------------------|---------------|
| `apache2ctl configtest` 실패        | 설정 문법 오류                   | 오류 메시지 라인 확인 후 수정                                 |               |
| 403 Forbidden                       | 파일 권한 또는 `Require` 설정    | `chmod`, `chown` 확인 / `Require all granted` 추가            |               |
| 404 Not Found                       | DocumentRoot 또는 파일 경로 오류 | `DocumentRoot` 경로 확인                                      |               |
| 500 Internal Server Error           | PHP 오류 또는 .htaccess 문제     | `error.log` 확인                                              |               |
| `bind() to 0.0.0.0:80 failed`       | 포트 충돌                        | `ss -tlnp \                                                   | grep 80` 확인 |
| mod_php + event MPM 충돌            | libphp는 prefork 전용            | `a2dismod mpm_event && a2enmod mpm_prefork` 또는 PHP-FPM 사용 |               |
| RHEL: DocumentRoot 접근 거부        | SELinux 컨텍스트 불일치          | `semanage fcontext` + `restorecon`                            |               |
| `Could not reliably determine FQDN` | ServerName 미설정                | `apache2.conf` 에 `ServerName localhost` 추가                 |               |

```bash
# 에러 로그 확인
sudo tail -50 /var/log/apache2/error.log    # Ubuntu
sudo tail -50 /var/log/httpd/error_log      # RHEL

# 프로세스 확인
ps aux | grep apache2
apache2ctl status 2>/dev/null || curl -s http://localhost/server-status?auto
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Apache Documentation: [httpd.apache.org/docs](https://httpd.apache.org/docs/2.4/) — ★★★☆☆
- Apache MPM: [httpd.apache.org/docs/2.4/mpm](https://httpd.apache.org/docs/2.4/mpm.html) — ★★★☆☆
- Apache SSL/TLS: [httpd.apache.org/docs/2.4/ssl](https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html) — ★★★☆☆

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

**마지막 업데이트**: 2026-05-15

© 2026 siasia86. Licensed under CC BY 4.0.
