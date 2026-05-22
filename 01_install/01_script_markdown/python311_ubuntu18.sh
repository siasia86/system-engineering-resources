#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.20.
#### Python 3.11 소스 컴파일 설치 — Ubuntu 18.04 (bionic)
#### Ansible 2.17+ 호환 (Python 3.9+ 필요)
#
# 허용 도메인:
#   www.python.org      - Python 소스 다운로드
#   archive.ubuntu.com  - 빌드 의존성 패키지

PYTHON_VER="3.11.9"
BUILD_DIR="/usr/local/src/python311-build"

[[ $EUID -eq 0 ]] || { echo "root 권한 필요" ; exit 1; }

apt-get update -qq
apt-get install -y gcc make wget libssl-dev libbz2-dev libffi-dev zlib1g-dev > /dev/null 2>&1 || { echo "#### filed error code : $? ####" ; exit 1; }

mkdir -p "${BUILD_DIR}"
wget -q "https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz" -O "${BUILD_DIR}/Python-${PYTHON_VER}.tgz" || { echo "#### filed error code : $? ####" ; exit 2; }
tar xzf "${BUILD_DIR}/Python-${PYTHON_VER}.tgz" -C "${BUILD_DIR}"

cd "${BUILD_DIR}/Python-${PYTHON_VER}"
./configure --quiet 2>/dev/null
make altinstall -j"$(nproc)" || { echo "#### filed error code : $? ####" ; exit 3; }

if [[ ! -e /usr/local/bin/python3 ]]; then
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3
fi

PROFILE=/etc/profile.d/python3_local.sh
if ! grep -q '/usr/local/bin' "${PROFILE}" 2>/dev/null; then
    echo 'export PATH=/usr/local/bin:$PATH' > "${PROFILE}"
fi

echo "done: $(/usr/local/bin/python3.11 --version)"
