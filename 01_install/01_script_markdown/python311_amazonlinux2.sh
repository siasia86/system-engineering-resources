#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.22.
#### Python 3.11 소스 컴파일 설치 — Amazon Linux 2
#### Ansible 2.17+ 호환 (기본 python3.7은 미지원)
#### OpenSSL 1.1.1을 /usr/local/openssl11에 소스 컴파일 — 기존 패키지 무변경
#
# 허용 도메인:
#   www.python.org                          - Python 소스 다운로드
#   www.openssl.org                         - OpenSSL 소스 다운로드
#   mirror.centos.org / amazonlinux.*.amazonaws.com - 빌드 의존성

PYTHON_VER="3.11.9"
OPENSSL_VER="1.1.1w"
BUILD_DIR="/usr/local/src/python311-build"
OPENSSL_PREFIX="/usr/local/openssl11"

[[ $EUID -eq 0 ]] || { echo "root 권한 필요" ; exit 1; }

yum install -y gcc make tar wget openssl-devel bzip2-devel libffi-devel zlib-devel perl-core > /dev/null 2>&1 || { echo "#### filed error code : $? ####" ; exit 1; }

mkdir -p "${BUILD_DIR}"

# ── OpenSSL 1.1.1 소스 컴파일 ─────────────────────────────────
if [[ ! -f "${OPENSSL_PREFIX}/lib/libssl.so.1.1" ]]; then
    wget -q "https://www.openssl.org/source/openssl-${OPENSSL_VER}.tar.gz" \
        -O "${BUILD_DIR}/openssl-${OPENSSL_VER}.tar.gz" || { echo "#### filed error code : $? ####" ; exit 2; }
    tar xzf "${BUILD_DIR}/openssl-${OPENSSL_VER}.tar.gz" -C "${BUILD_DIR}"
    cd "${BUILD_DIR}/openssl-${OPENSSL_VER}"
    ./config --prefix="${OPENSSL_PREFIX}" --openssldir="${OPENSSL_PREFIX}" shared zlib
    make -j"$(nproc)" > /dev/null 2>&1 || { echo "#### filed error code : $? ####" ; exit 2; }
    make install_sw > /dev/null 2>&1 || { echo "#### filed error code : $? ####" ; exit 2; }
fi

# ── Python 3.11 소스 컴파일 ───────────────────────────────────
wget -q "https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz" \
    -O "${BUILD_DIR}/Python-${PYTHON_VER}.tgz" || { echo "#### filed error code : $? ####" ; exit 2; }
tar xzf "${BUILD_DIR}/Python-${PYTHON_VER}.tgz" -C "${BUILD_DIR}"

cd "${BUILD_DIR}/Python-${PYTHON_VER}"
./configure --quiet \
    --with-openssl="${OPENSSL_PREFIX}" \
    --with-openssl-rpath=auto \
    2>/dev/null
make altinstall -j"$(nproc)" || { echo "#### filed error code : $? ####" ; exit 3; }

if [[ ! -f /usr/local/bin/python3.11 ]]; then
    echo "#### filed error code : python3.11 binary not found ####" ; exit 3
fi
if [[ ! -e /usr/local/bin/python3 ]]; then
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3
fi

PROFILE=/etc/profile.d/python3_local.sh
if ! grep -q '/usr/local/bin' "${PROFILE}" 2>/dev/null; then
    echo 'export PATH=/usr/local/bin:$PATH' > "${PROFILE}"
fi

echo "done: $(/usr/local/bin/python3.11 --version)"
