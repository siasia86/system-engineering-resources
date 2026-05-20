#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.20.
#### Python 3.9 설치 — Ubuntu 20.04 (focal)
#### Ansible 2.17+ 호환 (기본 python3.8은 미지원)
#
# 허용 도메인:
#   archive.ubuntu.com - python3.9 패키지 (기본 레포 포함)

# ── 변수 ───────────────────────────────────────────────────
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE01="/var/log/$(basename "$0" .sh).log"
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
    log_msg_info 1 "script start — python39_ubuntu20"

    # 1. root 확인
    [[ $EUID -eq 0 ]] || { log_msg_error 1 "root 권한 필요: sudo bash $0" ; exit 1; }

    # 2. 패키지 목록 업데이트
    run_msg_info 2 "apt-get update -qq"

    # 3. Python 3.9 설치
    run_msg_info 3 "apt-get install -y python3.9 > /dev/null 2>&1"

    # 4. 심볼릭 링크
    if [[ ! -e /usr/local/bin/python3 ]]; then
        ln -s /usr/bin/python3.9 /usr/local/bin/python3
        log_msg_info 4 "python3 심볼릭 링크 생성: /usr/local/bin/python3 → python3.9"
    else
        log_msg_info 4 "python3 이미 존재: $(/usr/local/bin/python3 --version 2>&1) — 스킵"
    fi

    log_msg_info 5 "script end — $(python3.9 --version 2>&1)"
}

main "$@"
