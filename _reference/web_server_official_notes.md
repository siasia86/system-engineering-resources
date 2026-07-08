---
name: web-server-official-notes
description: Nginx, Apache HTTP Server 공식 문서 기반 설정, 보안, 성능 참조 노트. 02_infrastructure/web_server/ 문서 생성/검토 시 참조.
tags:
  - nginx
  - apache
  - httpd
  - web-server
  - reverse-proxy
last_checked: 2026-07-08
sources:
  - https://nginx.org/en/docs/
  - https://httpd.apache.org/docs/2.4/
  - https://ssl-config.mozilla.org/
  - https://www.ssllabs.com/ssltest/
---

# Web Server 공식 참조 노트

## 1. Nginx

### 버전 (확인일: 2026-07-08)

| 채널     | 버전   | 비고              |
|----------|--------|-------------------|
| Mainline | 1.31.2 | 최신 기능, 개발용 |
| Stable   | 1.30.3 | 프로덕션 권장     |

- 출처: https://nginx.org/en/download.html

### 핵심 설정

| 항목                 | 권장값             | 근거                         |
|----------------------|--------------------|------------------------------|
| worker_processes     | auto               | CPU 코어 수에 맞춤           |
| worker_connections   | 1024~65535         | ulimit -n 과 일치            |
| keepalive_timeout    | 65                 | 기본값, CDN 뒤면 축소 가능   |
| client_max_body_size | 업로드 크기에 맞게 | 기본 1m, 파일 업로드 시 조정 |
| server_tokens        | off                | 버전 정보 노출 방지          |
| proxy_buffering      | on (기본)          | 백엔드 부하 감소             |

- 출처: https://nginx.org/en/docs/http/ngx_http_core_module.html

### 보안 설정

| 항목                               | 설정                        | 근거                                   |
|------------------------------------|-----------------------------|----------------------------------------|
| ssl_protocols                      | TLSv1.2 TLSv1.3             | TLS 1.0/1.1 제거                       |
| ssl_ciphers                        | Mozilla Intermediate 프로필 | ssl-config.mozilla.org                 |
| ssl_prefer_server_ciphers          | on                          | 서버 측 암호 선택                      |
| add_header X-Frame-Options         | DENY 또는 SAMEORIGIN        | Clickjacking 방지                      |
| add_header X-Content-Type-Options  | nosniff                     | MIME sniffing 방지                     |
| add_header X-XSS-Protection        | 0                           | 최신 브라우저에서 deprecated, CSP 사용 |
| add_header Content-Security-Policy | default-src self            | XSS 방지 기본                          |

- 출처: https://ssl-config.mozilla.org/
- 출처: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

### 디렉토리 보안

| 설정                         | 목적                         |                     |                    |
|------------------------------|------------------------------|---------------------|--------------------|
| autoindex off                | 디렉토리 리스팅 차단         |                     |                    |
| location ~ /\. { deny all; } | 숨김 파일(.htaccess 등) 차단 |                     |                    |
| location ~ \.(conf           | sql                          | env)$ { deny all; } | 설정파일 접근 차단 |

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

## 2. Apache HTTP Server

### 버전 (확인일: 2026-07-08)

| 채널   | 버전   | 비고           |
|--------|--------|----------------|
| Stable | 2.4.68 | 현재 유일 지원 |

- 2.2.x: EOL (2017-12)
- 출처: https://httpd.apache.org/download.cgi

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

### 버전

| 채널 | 버전 | LTS 종료 |
|------|------|----------|
| LTS  | 2.8  | 2028-Q2  |
| LTS  | 3.0  | 2029-Q2  |

- 출처: https://www.haproxy.org/

### 핵심 설정

| 항목            | 권장                  | 근거             |
|-----------------|-----------------------|------------------|
| maxconn         | 시스템 FD 기반 산정   | ulimit -n 연동   |
| timeout connect | 5s                    | 백엔드 연결 대기 |
| timeout client  | 30s                   | 클라이언트 유휴  |
| timeout server  | 30s                   | 백엔드 응답 대기 |
| stats socket    | /var/run/haproxy.sock | 런타임 API       |

- 출처: https://docs.haproxy.org/

## 4. TLS 설정 공통 (Mozilla SSL Configuration Generator)

| 프로필       | 대상            | 최소 TLS | 암호 강도 |
|--------------|-----------------|----------|-----------|
| Modern       | 최신 클라이언트 | TLS 1.3  | 높음      |
| Intermediate | 범용 (권장)     | TLS 1.2  | 중간      |
| Old          | 레거시 호환     | TLS 1.0  | 낮음      |

- 프로덕션 권장: Intermediate
- 출처: https://ssl-config.mozilla.org/
- 검증: https://www.ssllabs.com/ssltest/ (A+ 목표)
