#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.20.
#### nginx geoip2 모듈 설치 — Ubuntu 22.04 (jammy), nginx 공식 stable 레포 (1.30.x)
#### 사용법: sudo bash nginx_geoip2_install.sh [nginx_version]
####         nginx_version 미지정 시 1.30.1 사용
#
# 허용 도메인:
#   nginx.org                   - nginx 패키지 레포 및 소스 다운로드
#   github.com                  - ngx_http_geoip2_module 소스 클론
#   objects.githubusercontent.com - GitHub 파일 다운로드
#   www.maxmind.com             - GeoLite2 DB 다운로드 (수동 단계)
#   archive.ubuntu.com          - 빌드 의존성 패키지
#
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!
exit 0

# ── 변수 ───────────────────────────────────────────────────
NGINX_VER="${1:-1.30.1}"
BUILD_DIR="/usr/local/src/nginx-geoip2-build"
MODULE_SRC="https://github.com/leev/ngx_http_geoip2_module.git"

# ── root 확인 ──────────────────────────────────────────────
[[ $EUID -eq 0 ]] || { echo "root 권한 필요" ; exit 1; }


# ── 1. 기본 도구 설치 ─────────────────────────────────────
echo "[1] 기본 도구 설치"
apt-get update -qq > /dev/null 2>&1
apt-get install -y curl gnupg2 git lsb-release ca-certificates > /dev/null 2>&1 \
  || { echo "#### filed error code : $? ####" ; exit 1; }


# ── 2. nginx 공식 stable 레포 추가 (중복 방지) ────────────
echo "[2] nginx stable 레포 추가"
if ls /etc/apt/sources.list.d/nginx*.list > /dev/null 2>&1; then
  echo "    nginx 레포 이미 존재 — 스킵"
else
  curl -sSL https://nginx.org/keys/nginx_signing.key \
    | gpg --dearmor -o /etc/apt/trusted.gpg.d/nginx.gpg
  echo "deb https://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" \
    > /etc/apt/sources.list.d/nginx-stable.list
fi
apt-get update -qq


# ── 3. nginx 설치 ─────────────────────────────────────────
echo "[3] nginx ${NGINX_VER} 설치"
apt-get install -y "nginx=${NGINX_VER}-1~$(lsb_release -cs)" \
  || { echo "#### filed error code : $? ####" ; exit 2; }
echo "    $(nginx -v 2>&1)"


# ── 4. 빌드 의존성 ────────────────────────────────────────
echo "[4] 빌드 의존성 설치"
apt-get install -y \
  libmaxminddb-dev build-essential \
  libpcre3-dev libssl-dev zlib1g-dev > /dev/null 2>&1 \
  || { echo "#### filed error code : $? ####" ; exit 3; }


# ── 5. nginx 소스 다운로드 ─────────────────────────────────
echo "[5] nginx ${NGINX_VER} 소스 다운로드"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"
curl -sO "https://nginx.org/download/nginx-${NGINX_VER}.tar.gz" \
  || { echo "#### filed error code : $? ####" ; exit 4; }
tar xzf "nginx-${NGINX_VER}.tar.gz"


# ── 6. geoip2 모듈 소스 클론 ──────────────────────────────
echo "[6] ngx_http_geoip2_module 소스 클론"
git clone --depth=1 "${MODULE_SRC}" ngx_http_geoip2_module 2>&1 | tail -1 \
  || { echo "#### filed error code : $? ####" ; exit 5; }


# ── 7. 모듈 빌드 ──────────────────────────────────────────
echo "[7] 모듈 빌드 (--with-compat)"
cd "nginx-${NGINX_VER}"
./configure --with-compat \
  --add-dynamic-module=../ngx_http_geoip2_module > /dev/null 2>&1 \
  || { echo "#### filed error code : $? ####" ; exit 6; }
make modules 2>&1 | tail -3 \
  || { echo "#### filed error code : $? ####" ; exit 7; }


# ── 8. 모듈 설치 ──────────────────────────────────────────
echo "[8] 모듈 설치: /usr/lib/nginx/modules/"
cp objs/ngx_http_geoip2_module.so /usr/lib/nginx/modules/
chmod 644 /usr/lib/nginx/modules/ngx_http_geoip2_module.so


# ── 9. load_module 설정 ────────────────────────────────────
echo "[9] load_module 설정"
mkdir -p /etc/nginx/modules-enabled
echo 'load_module modules/ngx_http_geoip2_module.so;' \
  > /etc/nginx/modules-enabled/50-mod-http-geoip2.conf

grep -q 'modules-enabled' /etc/nginx/nginx.conf || \
  sed -i '1s/^/include \/etc\/nginx\/modules-enabled\/*.conf;\n/' \
  /etc/nginx/nginx.conf


# ── 10. 검증 ──────────────────────────────────────────────
echo "[10] nginx -t 검증"
nginx -t || { echo "#### filed error code : $? ####" ; exit 8; }


# ── 완료 ──────────────────────────────────────────────────
echo ""
echo "==== 설치 완료 ===="
echo ""
echo "  [확인 방법]"
echo "  $ ls /usr/lib/nginx/modules/ | grep geoip2"
echo "  $ cat /etc/nginx/modules-enabled/50-mod-http-geoip2.conf"
echo "  $ nginx -t"
echo "  ※ nginx -V 에는 dynamic module 미표시 (정상)"
echo ""
echo "  모듈 파일: /usr/lib/nginx/modules/ngx_http_geoip2_module.so"
echo "  로드 설정: /etc/nginx/modules-enabled/50-mod-http-geoip2.conf"
echo "  빌드 소스: ${BUILD_DIR}"
echo ""
echo "  다음 단계: MaxMind GeoLite2 DB를 /etc/nginx/geoip/ 에 배치"
echo "             https://www.maxmind.com/en/geolite2/signup"

# ── nginx.conf 설정 예시 (참고용) ─────────────────────────
# http 블록 안에 추가:
#
# geoip2 /etc/nginx/geoip/GeoLite2-Country.mmdb {
#     $geoip2_country_code country iso_code;
#     $geoip2_country_name country names en;
# }
#
# server 블록 안에 추가:
#
# location /test-geoip {
#     return 200 "country_code=$geoip2_country_code\n";
# }
