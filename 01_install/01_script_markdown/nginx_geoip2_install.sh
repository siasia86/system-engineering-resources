#!/usr/bin/env bash
# nginx geoip2 모듈 설치 스크립트
# 대상: Ubuntu 22.04 (jammy), nginx 공식 stable 레포 (1.30.x)
# 사용법: sudo bash nginx_geoip2_install.sh [nginx_version]
#         nginx_version 미지정 시 1.30.1 사용

# ── 허용 도메인 (방화벽/프록시 화이트리스트) ──────────────────────
# nginx.org          - nginx 패키지 레포 및 소스 다운로드
# github.com         - ngx_http_geoip2_module 소스 클론
# objects.githubusercontent.com - GitHub raw 파일 다운로드
# www.maxmind.com    - GeoLite2 DB 다운로드 (수동 단계)
# ──────────────────────────────────────────────────────────────────
exit 0
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!!
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!!
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!!
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!!
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것 !!!!!!!!!!!!
exit 0

set -euo pipefail

NGINX_VER="${1:-1.30.1}"
BUILD_DIR="/usr/local/src/nginx-geoip2-build"
MODULE_SRC="https://github.com/leev/ngx_http_geoip2_module.git"

# ── 색상 출력 ──────────────────────────────────────────────
info()  { echo "[INFO]  $*"; }
ok()    { echo "[OK]    $*"; }
err()   { echo "[ERROR] $*" >&2; exit 1; }

# ── root 확인 ──────────────────────────────────────────────
[[ $EUID -eq 0 ]] || err "root 권한 필요: sudo bash $0"

# ── 0. 기본 도구 설치 ─────────────────────────────────────
apt-get update -qq > /dev/null 2>&1
apt-get install -y curl gnupg2 git lsb-release ca-certificates > /dev/null 2>&1

# ── 1. nginx 공식 stable 레포 추가 (중복 방지) ────────────
info "nginx stable 레포 추가 (nginx.org/packages)"
if ls /etc/apt/sources.list.d/nginx*.list > /dev/null 2>&1; then
  info "nginx 레포 이미 존재 — 레포 추가 스킵"
else
  curl -sSL https://nginx.org/keys/nginx_signing.key \
    | gpg --dearmor -o /etc/apt/trusted.gpg.d/nginx.gpg
  echo "deb https://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" \
    > /etc/apt/sources.list.d/nginx-stable.list
fi
apt-get update -qq

# ── 2. nginx 설치 ──────────────────────────────────────────
info "nginx ${NGINX_VER} 설치"
apt-get install -y "nginx=${NGINX_VER}-1~$(lsb_release -cs)"
ok "nginx $(nginx -v 2>&1 | grep -oP '[\d.]+')"

# ── 3. 빌드 의존성 ─────────────────────────────────────────
info "빌드 의존성 설치"
apt-get install -y \
  libmaxminddb-dev build-essential git \
  libpcre3-dev libssl-dev zlib1g-dev > /dev/null 2>&1

# ── 4. 소스 준비 ───────────────────────────────────────────
info "빌드 디렉토리: ${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

info "nginx ${NGINX_VER} 소스 다운로드"
curl -sO "https://nginx.org/download/nginx-${NGINX_VER}.tar.gz"
tar xzf "nginx-${NGINX_VER}.tar.gz"

info "ngx_http_geoip2_module 소스 클론"
git clone --depth=1 "${MODULE_SRC}" ngx_http_geoip2_module 2>&1 | tail -1

# ── 5. 모듈 빌드 ───────────────────────────────────────────
info "모듈 빌드 (--with-compat)"
cd "nginx-${NGINX_VER}"
./configure --with-compat \
  --add-dynamic-module=../ngx_http_geoip2_module > /dev/null 2>&1
make modules 2>&1 | tail -3

# ── 6. 모듈 설치 ───────────────────────────────────────────
info "모듈 설치: /usr/lib/nginx/modules/"
cp objs/ngx_http_geoip2_module.so /usr/lib/nginx/modules/
chmod 644 /usr/lib/nginx/modules/ngx_http_geoip2_module.so

# ── 7. 모듈 로드 설정 ──────────────────────────────────────
info "load_module 설정"
mkdir -p /etc/nginx/modules-enabled
echo 'load_module modules/ngx_http_geoip2_module.so;' \
  > /etc/nginx/modules-enabled/50-mod-http-geoip2.conf

grep -q 'modules-enabled' /etc/nginx/nginx.conf || \
  sed -i '1s/^/include \/etc\/nginx\/modules-enabled\/*.conf;\n/' \
  /etc/nginx/nginx.conf

# ── 8. 검증 ───────────────────────────────────────────────
info "nginx -t 검증"
nginx -t

ok "설치 완료"
echo ""
echo "  [확인 방법]"
echo "  $ ls /usr/lib/nginx/modules/ | grep geoip2"
echo "  $ cat /etc/nginx/modules-enabled/50-mod-http-geoip2.conf"
echo "  $ nginx -t"
echo "  ※ nginx -V 에는 dynamic module 미표시 (정상)"
echo ""
echo "  모듈 파일: /usr/lib/nginx/modules/ngx_http_geoip2_module.so"
echo "  로드 설정: /etc/nginx/modules-enabled/50-mod-http-geoip2.conf"
echo "  다음 단계: MaxMind GeoLite2 DB를 /etc/nginx/geoip/ 에 배치"
echo "             https://www.maxmind.com/en/geolite2/signup"

