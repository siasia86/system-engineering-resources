# TLS/SSL 가이드

## 목차

| 섹션 |
|------|
| [1. 인증서 구조](#1-인증서-구조) / [2. openssl 명령어](#2-openssl-명령어) / [3. Let's Encrypt](#3-lets-encrypt) |
| [4. Nginx TLS 설정](#4-nginx-tls-설정) / [5. mTLS](#5-mtls) / [6. 인증서 점검](#6-인증서-점검) |

---

## 1. 인증서 구조

```
Root CA (자체 서명)
    └── Intermediate CA (Root CA가 서명)
            └── Server Certificate (Intermediate CA가 서명)
                    ├── Subject: CN=example.com
                    ├── SAN: DNS:example.com, DNS:www.example.com
                    ├── Public Key
                    └── Validity: 90일 (Let's Encrypt) / 1년
```

### TLS Handshake (TLS 1.3)

```
Client                          Server
  │                               │
  ├── ClientHello ──────────────> │  (지원 cipher, random)
  │                               │
  │ <────────────── ServerHello ──┤  (선택 cipher, random)
  │ <──────────── Certificate ────┤  (서버 인증서)
  │ <──────── CertificateVerify ──┤  (서명)
  │ <──────────────── Finished ───┤
  │                               │
  ├── Finished ─────────────────> │
  │                               │
  └──── 암호화 통신 시작 ─────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. openssl 명령어

```bash
# 개인키 생성 (RSA 4096)
openssl genrsa -out server.key 4096

# 개인키 생성 (ECDSA P-256, 권장)
openssl ecparam -name prime256v1 -genkey -noout -out server.key

# CSR 생성
openssl req -new -key server.key -out server.csr \
    -subj "/C=KR/ST=Seoul/O=Example/CN=example.com"

# 자체 서명 인증서 생성 (테스트용, 365일)
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt \
    -days 365 -nodes -subj "/CN=example.com"

# 인증서 정보 확인
openssl x509 -in server.crt -text -noout

# 만료일 확인
openssl x509 -in server.crt -noout -enddate

# 원격 서버 인증서 확인
openssl s_client -connect example.com:443 -servername example.com </dev/null \
    | openssl x509 -noout -dates

# PEM ↔ PFX 변환
openssl pkcs12 -export -out server.pfx -inkey server.key -in server.crt
openssl pkcs12 -in server.pfx -out server.pem -nodes
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Let's Encrypt

Certbot을 사용한 무료 인증서 발급 (90일, 자동 갱신).

```bash
# 설치 (Ubuntu)
sudo apt install certbot python3-certbot-nginx

# 발급 (Nginx)
sudo certbot --nginx -d example.com -d www.example.com

# 발급 (Standalone, 포트 80 사용)
sudo certbot certonly --standalone -d example.com

# 발급 (DNS Challenge, 와일드카드)
sudo certbot certonly --manual --preferred-challenges dns \
    -d "*.example.com" -d example.com

# 갱신 테스트
sudo certbot renew --dry-run

# 자동 갱신 (cron)
0 3 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
```

```
인증서 경로:
/etc/letsencrypt/live/example.com/
├── cert.pem        ← 서버 인증서
├── chain.pem       ← 중간 CA 체인
├── fullchain.pem   ← cert.pem + chain.pem (Nginx에서 사용)
└── privkey.pem     ← 개인키
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. Nginx TLS 설정

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # TLS 버전 (1.2 이상만 허용)
    ssl_protocols TLSv1.2 TLSv1.3;

    # 강력한 Cipher Suite
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

    # HSTS (6개월)
    add_header Strict-Transport-Security "max-age=15768000; includeSubDomains" always;

    # 세션 캐시
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
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

## 5. mTLS

클라이언트도 인증서로 인증하는 양방향 TLS. 서비스 간 통신(MSA, API) 보안에 사용.

```bash
# CA 키/인증서 생성
openssl genrsa -out ca.key 4096
openssl req -x509 -new -key ca.key -out ca.crt -days 3650 -subj "/CN=My CA"

# 클라이언트 키/CSR 생성
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=client"

# CA로 클라이언트 인증서 서명
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out client.crt -days 365
```

```nginx
# Nginx mTLS 설정
server {
    listen 443 ssl;

    ssl_certificate     /etc/ssl/server.crt;
    ssl_certificate_key /etc/ssl/server.key;

    # 클라이언트 인증서 검증
    ssl_client_certificate /etc/ssl/ca.crt;
    ssl_verify_client on;

    # 클라이언트 CN을 헤더로 전달
    proxy_set_header X-Client-Cert-CN $ssl_client_s_dn_cn;
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 인증서 점검

```bash
# 만료 임박 인증서 일괄 확인 (30일 이내)
for cert in /etc/letsencrypt/live/*/cert.pem; do
    domain=$(echo $cert | cut -d/ -f6)
    expiry=$(openssl x509 -in $cert -noout -enddate | cut -d= -f2)
    days=$(( ( $(date -d "$expiry" +%s) - $(date +%s) ) / 86400 ))
    [ $days -lt 30 ] && echo "🟡  $domain: $days 일 남음"
done

# SSL Labs 등급 확인 (외부)
# https://www.ssllabs.com/ssltest/

# 로컬 TLS 설정 점검 (testssl.sh — apt 패키지 아님, GitHub에서 직접 설치)
git clone --depth 1 https://github.com/drwetter/testssl.sh.git
./testssl.sh/testssl.sh example.com
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Let's Encrypt Documentation: [letsencrypt.org/docs](https://letsencrypt.org/docs/) — ★★★☆☆
- Mozilla SSL Configuration Generator: [ssl-config.mozilla.org](https://ssl-config.mozilla.org/) — ★★☆☆☆
- RFC 8446: TLS 1.3 — ★★★★☆
- RFC 6066: TLS Extensions (OCSP Stapling §8) — ★★★★☆
- RFC 6797: HTTP Strict Transport Security (HSTS) — ★★★★☆
- testssl.sh: [github.com/drwetter/testssl.sh](https://github.com/drwetter/testssl.sh) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-03

**마지막 업데이트**: 2026-05-03

© 2026 siasia86. Licensed under CC BY 4.0.
