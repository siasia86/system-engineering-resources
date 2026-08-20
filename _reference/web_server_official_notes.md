---
name: web-server-official-notes
description: Nginx, Apache HTTP Server 공식 문서 기반 설정, 보안, 성능 참조 노트. 02_infrastructure/web_server/ 문서 생성/검토 시 참조.
tags:
  - nginx
  - apache
  - httpd
  - web-server
  - reverse-proxy
last_checked: 2026-08-20
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
| 1.25.1+ | `listen ... quic` QUIC/HTTP3 실험적 지원         | `http3 on;` 별도 디렉티브             |
| 1.23.4+ | TLSv1.3 프로토콜 기본 활성화                     | `ssl_protocols` 별도 설정 필요성 감소 |
| 1.15.0+ | `ssl` 디렉티브 deprecated, `listen ... ssl` 사용 | HTTPS 활성화 방식 명확화              |
| 1.9.0+  | stream 모듈 (TCP/UDP 프록시) 추가                | `stream {}` 블록 사용 가능            |

### 버전별 주요 변경사항 (Apache)

| 버전    | 변경 사항                       | 영향                                |
|---------|---------------------------------|-------------------------------------|
| 2.4.58  | mod_http2 `H2EarlyHint` 추가    | HTTP 103 Early Hints 응답 헤더 지원 |
| 2.4.49  | CVE-2021-41773 (path traversal) | 즉시 패치 필수                      |
| 2.4.52+ | mod_proxy_http2 백엔드 H2 지원  | 리버스 프록시 H2 pass-through       |
| 2.4+    | event MPM 기본                  | prefork에서 전환 권장               |

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

| 채널 | 버전 | LTS 종료                 |
|------|------|--------------------------|
| LTS  | 3.4  | 2031-Q2                  |
| LTS  | 3.2  | 2030-Q2                  |
| LTS  | 3.0  | 2029-Q2                  |
| LTS  | 2.8  | 2028-Q2 (critical fixes) |

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

- 출처: https://ssl-config.mozilla.org/guidelines/5.7.json (v5.7, 확인일: 2026-07-14)
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
