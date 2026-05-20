#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.20.
#### Python 3.11 소스 컴파일 설치 — Amazon Linux 2
#### Ansible 2.17+ 호환 (기본 python3.7은 미지원, amazon-linux-extras에 3.8만 있음)
#
# 허용 도메인:
#   www.python.org                          - Python 소스 다운로드
#   mirror.centos.org / amazonlinux.*.amazonaws.com - 빌드 의존성

# ── 변수 ───────────────────────────────────────────────────
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE01="/var/log/$(basename "$0" .sh).log"
PYTHON_VER="3.11.9"
BUILD_DIR="/usr/local/src/python311-build"
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
    log_msg_info 1 "script start — python311_amazonlinux2"

    # 1. root 확인
    [[ $EUID -eq 0 ]] || { log_msg_error 1 "root 권한 필요: sudo bash $0" ; exit 1; }

    # 2. 빌드 의존성 설치
    run_msg_info 2 "yum install -y gcc make tar wget openssl-devel bzip2-devel libffi-devel zlib-devel > /dev/null 2>&1"

    # 3. 소스 다운로드
    mkdir -p "${BUILD_DIR}"
    run_msg_info 3 "wget -q https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz -O ${BUILD_DIR}/Python-${PYTHON_VER}.tgz"

    # 4. 압축 해제
    run_msg_info 4 "tar xzf ${BUILD_DIR}/Python-${PYTHON_VER}.tgz -C ${BUILD_DIR}"

    # 5. 빌드 및 설치
    cd "${BUILD_DIR}/Python-${PYTHON_VER}"
    run_msg_info 5 "./configure --enable-optimizations --quiet 2>/dev/null"
    run_msg_info 6 "make altinstall -j$(nproc) 2>&1 | tail -2"

    # 7. 심볼릭 링크
    if [[ ! -e /usr/local/bin/python3 ]]; then
        ln -s /usr/local/bin/python3.11 /usr/local/bin/python3
        log_msg_info 7 "python3 심볼릭 링크 생성: /usr/local/bin/python3 → python3.11"
    else
        log_msg_info 7 "python3 이미 존재: $(/usr/local/bin/python3 --version 2>&1) — 스킵"
    fi

    # 8. PATH 등록
    PROFILE=/etc/profile.d/python3_local.sh
    if ! grep -q '/usr/local/bin' "${PROFILE}" 2>/dev/null; then
        echo 'export PATH=/usr/local/bin:$PATH' > "${PROFILE}"
        log_msg_info 8 "PATH 등록 완료: ${PROFILE}"
    else
        log_msg_info 8 "PATH 이미 등록됨 — 스킵"
    fi
    export PATH=/usr/local/bin:$PATH

    log_msg_info 9 "script end — $(python3 --version 2>&1)"
}

main "$@"
