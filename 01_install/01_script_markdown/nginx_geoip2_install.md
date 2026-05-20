# nginx geoip2 모듈 설치

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 환경별 설치 방법](#2-환경별-설치-방법) / [3. 설정](#3-설정) |
| [4. 검증](#4-검증) / [5. 트러블슈팅](#5-트러블슈팅) |

---

## 1. 개요

nginx에서 클라이언트 IP 기반 국가/도시 정보를 조회하는 모듈입니다.
MaxMind GeoLite2/GeoIP2 DB를 사용합니다.

| 항목          | 내용                                              |
|---------------|---------------------------------------------------|
| 모듈          | `ngx_http_geoip2_module`                          |
| 의존성        | `libmaxminddb`                                    |
| DB            | MaxMind GeoLite2-Country / GeoLite2-City          |
| 소스          | https://github.com/leev/ngx_http_geoip2_module    |

### nginx 버전별 설치 방법 비교

| nginx 버전 | 레포                     | geoip2 설치 방법 |
|------------|--------------------------|------------------|
| 1.18.x     | Ubuntu 기본 레포         | 패키지 (`apt`)   |
| 1.30.x     | nginx 공식 stable 레포   | 모듈 소스 컴파일 |
| 1.31.x+    | nginx 공식 mainline 레포 | 모듈 소스 컴파일 |

### 허용 도메인 (방화벽/프록시 화이트리스트)

| 도메인                          | 용도                                   |
|---------------------------------|----------------------------------------|
| `nginx.org`                     | nginx 패키지 레포 및 소스 다운로드     |
| `github.com`                    | geoip2 모듈 소스 클론                  |
| `objects.githubusercontent.com` | GitHub 파일 다운로드                   |
| `archive.ubuntu.com`            | 빌드 의존성 패키지                     |
| `www.maxmind.com`               | GeoLite2 DB 다운로드 (수동 단계/선택)  |

---

## 2. 환경별 설치 방법

### Ubuntu 22.04 — nginx 1.18 (패키지) // 1.30.x 로 진행 할것 

```bash
apt-get update
apt-get install -y nginx libnginx-mod-http-geoip2
```

모듈이 `/etc/nginx/modules-enabled/50-mod-http-geoip2.conf`에 자동 등록됩니다.

### Ubuntu 22.04 — nginx 1.30.x (공식 stable 레포 + 모듈 컴파일)

스크립트 사용:

```bash
sudo bash nginx_geoip2_install.sh          # 기본 1.30.1
sudo bash nginx_geoip2_install.sh 1.30.0   # 버전 지정
```

수동 설치:

```bash
# 0. 기본 도구 설치
apt-get update
apt-get install -y curl gnupg2 git lsb-release ca-certificates

# 1. nginx 공식 stable 레포 추가
curl -sSL https://nginx.org/keys/nginx_signing.key \
  | gpg --dearmor -o /etc/apt/trusted.gpg.d/nginx.gpg
echo "deb https://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" \
  > /etc/apt/sources.list.d/nginx-stable.list
apt-get update

# 2. nginx 설치
apt-get install -y nginx=1.30.1-1~jammy

# 3. 빌드 의존성
apt-get install -y libmaxminddb-dev build-essential libpcre3-dev libssl-dev zlib1g-dev

# 4. nginx 소스 (설치 버전과 동일)
NGINX_VER=$(nginx -v 2>&1 | grep -oP '[\d.]+')
curl -O https://nginx.org/download/nginx-${NGINX_VER}.tar.gz
tar xzf nginx-${NGINX_VER}.tar.gz

# 5. geoip2 모듈 소스
git clone --depth=1 https://github.com/leev/ngx_http_geoip2_module.git

# 6. 모듈 빌드
cd nginx-${NGINX_VER}
./configure --with-compat --add-dynamic-module=../ngx_http_geoip2_module
make modules

# 7. 모듈 설치
cp objs/ngx_http_geoip2_module.so /usr/lib/nginx/modules/
chmod 644 /usr/lib/nginx/modules/ngx_http_geoip2_module.so

# 8. 모듈 로드 설정
mkdir -p /etc/nginx/modules-enabled
echo 'load_module modules/ngx_http_geoip2_module.so;' \
  > /etc/nginx/modules-enabled/50-mod-http-geoip2.conf

grep -q 'modules-enabled' /etc/nginx/nginx.conf || \
  sed -i '1s/^/include \/etc\/nginx\/modules-enabled\/*.conf;\n/' /etc/nginx/nginx.conf

nginx -t && nginx -s reload
```

---

## 3. 설정

### MaxMind DB 다운로드

MaxMind 계정 필요 (https://www.maxmind.com/en/geolite2/signup).

```bash
mkdir -p /etc/nginx/geoip
# GeoLite2-Country.mmdb, GeoLite2-City.mmdb 복사
```

### nginx.conf 설정 예시

```nginx
# http 블록 안
geoip2 /etc/nginx/geoip/GeoLite2-Country.mmdb {
    $geoip2_country_code country iso_code;
}

server {
    location / {
        # 한국 외 차단 예시
        if ($geoip2_country_code != "KR") {
            return 403;
        }
    }
}
```

---

## 4. 검증

```bash
# 모듈 파일 확인
ls /usr/lib/nginx/modules/ | grep geoip2

# 모듈 로드 설정 확인
cat /etc/nginx/modules-enabled/50-mod-http-geoip2.conf

# 설정 문법 확인
nginx -t
```

---

## 5. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `rc` 상태 (`dpkg -l`) | nginx 버전과 모듈 버전 불일치 | 버전 맞춰 재설치 또는 컴파일 |
| `make modules` 실패 | PCRE/SSL/zlib 헤더 없음 | `apt install libpcre3-dev libssl-dev zlib1g-dev` |
| `nginx -t` 실패 | `modules-enabled` include 없음 | nginx.conf 첫 줄에 `include` 추가 |
| `curl: command not found` | 기본 도구 미설치 | `apt install curl gnupg2 git lsb-release` |
| DB 파일 없음 | mmdb 미배치 | MaxMind에서 다운로드 후 경로 지정 |

---

## 참고 자료

- ngx_http_geoip2_module: [github.com/leev/ngx_http_geoip2_module](https://github.com/leev/ngx_http_geoip2_module) — ★★★☆☆
- MaxMind GeoLite2: [maxmind.com](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) — ★★★☆☆
- nginx 공식 레포: [nginx.org/packages](https://nginx.org/packages/ubuntu/pool/nginx/n/nginx/) — ★★★☆☆

---

**작성일**: 2026-05-20

**마지막 업데이트**: 2026-05-20

© 2026 siasia86. Licensed under CC BY 4.0.
