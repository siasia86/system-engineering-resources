#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.20.
#### nginx geoip2 모듈 설치 — Ubuntu 22.04 (jammy), nginx 공식 stable 레포 (1.30.x)
#### 사용법: sudo bash nginx_geoip2_install.sh [nginx_version]
#
# 허용 도메인:
#   nginx.org                   - nginx 패키지 레포 및 소스 다운로드
#   github.com                  - ngx_http_geoip2_module 소스 클론
#   objects.githubusercontent.com - GitHub 파일 다운로드
#   www.maxmind.com             - GeoLite2 DB 다운로드 (수동 단계)
#   archive.ubuntu.com          - 빌드 의존성 패키지
#
# nginx_geoip2_install.md 를 확인하고 script 를 수정 한 뒤에 사용 할것
exit 0

# ── 변수 ───────────────────────────────────────────────────
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE01="/var/log/$(basename "$0" .sh).log"
NGINX_VER="${1:-1.30.1}"
BUILD_DIR="/usr/local/src/nginx-geoip2-build"
MODULE_SRC="https://github.com/leev/ngx_http_geoip2_module.git"
backup_status_log_dir="/var/log/sj_scripts"

# ── 로그 디렉토리 초기화 ───────────────────────────────────
mkdir -p "$(dirname "${LOG_FILE01}")"
mkdir -p "${backup_status_log_dir}"
exec >> "${LOG_FILE01}" 2>&1

# ── 로깅 함수 ──────────────────────────────────────────────
run_msg_info() {
    local info_code=$1
    local info_msg=$2
    local status

    eval "${info_msg}"
    status=$?

    if [ "${status}" -eq 0 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') sj_scripts [info] code:${info_code} success. ${info_msg}"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') sj_scripts [error] code:${info_code} failed with status ${status}. ${info_msg}"
    fi
}

log_msg_info() {
    local info_code=$1
    local info_msg=$2
    echo "$(date '+%Y-%m-%d %H:%M:%S') sj_scripts [info] code:${info_code} ${info_msg}"
}

log_msg_error() {
    local err_code=$1
    local err_msg=$2
    echo "$(date '+%Y-%m-%d %H:%M:%S') sj_scripts [error] code:${err_code} ${err_msg}"
    if [ -n "${backup_status_log_dir:-}" ]; then
        echo "${err_code}" > "${backup_status_log_dir}/backup.status"
    fi
}

# ── 메인 ───────────────────────────────────────────────────
main() {
    log_msg_info 1 "script start — nginx_geoip2_install (nginx ${NGINX_VER})"

    # 1. root 확인
    [[ $EUID -eq 0 ]] || { log_msg_error 1 "root 권한 필요: sudo bash $0" ; exit 1; }

    # 2. 기본 도구 설치
    run_msg_info 2 "apt-get update -qq > /dev/null 2>&1"
    run_msg_info 3 "apt-get install -y curl gnupg2 git lsb-release ca-certificates > /dev/null 2>&1"

    # 4. nginx 레포 추가 (중복 방지)
    if ls /etc/apt/sources.list.d/nginx*.list > /dev/null 2>&1; then
        log_msg_info 4 "nginx 레포 이미 존재 — 스킵"
    else
        run_msg_info 4 "curl -sSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/nginx.gpg"
        echo "deb https://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" \
          > /etc/apt/sources.list.d/nginx-stable.list
    fi
    run_msg_info 5 "apt-get update -qq"

    # 6. nginx 설치
    run_msg_info 6 "apt-get install -y nginx=${NGINX_VER}-1~$(lsb_release -cs)"

    # 7. 빌드 의존성
    run_msg_info 7 "apt-get install -y libmaxminddb-dev build-essential libpcre3-dev libssl-dev zlib1g-dev > /dev/null 2>&1"

    # 8. 소스 준비
    mkdir -p "${BUILD_DIR}"
    cd "${BUILD_DIR}"
    run_msg_info 8 "curl -sO https://nginx.org/download/nginx-${NGINX_VER}.tar.gz"
    run_msg_info 9 "tar xzf nginx-${NGINX_VER}.tar.gz"
    run_msg_info 10 "git clone --depth=1 ${MODULE_SRC} ngx_http_geoip2_module 2>&1 | tail -1"

    # 11. 모듈 빌드
    cd "nginx-${NGINX_VER}"
    run_msg_info 11 "./configure --with-compat --add-dynamic-module=../ngx_http_geoip2_module > /dev/null 2>&1"
    run_msg_info 12 "make modules 2>&1 | tail -3"

    # 13. 모듈 설치
    cp objs/ngx_http_geoip2_module.so /usr/lib/nginx/modules/
    chmod 644 /usr/lib/nginx/modules/ngx_http_geoip2_module.so
    log_msg_info 13 "모듈 복사 완료: /usr/lib/nginx/modules/ngx_http_geoip2_module.so"

    # 14. load_module 설정
    mkdir -p /etc/nginx/modules-enabled
    echo 'load_module modules/ngx_http_geoip2_module.so;' \
      > /etc/nginx/modules-enabled/50-mod-http-geoip2.conf
    grep -q 'modules-enabled' /etc/nginx/nginx.conf || \
      sed -i '1s/^/include \/etc\/nginx\/modules-enabled\/*.conf;\n/' /etc/nginx/nginx.conf
    log_msg_info 14 "load_module 설정 완료"

    # 15. 검증
    run_msg_info 15 "nginx -t"

    log_msg_info 16 "script end — nginx geoip2 설치 완료"
}

main "$@"
