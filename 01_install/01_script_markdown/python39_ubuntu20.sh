#!/bin/bash
#### This script was created by sjyun on 2026-05-20. version 26.05.20.
#### Python 3.9 설치 — Ubuntu 20.04 (focal)
#### Ansible 2.17+ 호환 (기본 python3.8은 미지원)
#
# 허용 도메인:
#   archive.ubuntu.com - python3.9 패키지 (기본 레포 포함)

[[ $EUID -eq 0 ]] || { echo "root 권한 필요" ; exit 1; }

apt-get update -qq
apt-get install -y python3.9 > /dev/null 2>&1 || { echo "#### filed error code : $? ####" ; exit 1; }

if [[ ! -e /usr/local/bin/python3 ]]; then
    ln -s /usr/bin/python3.9 /usr/local/bin/python3
fi

echo "done: $(python3.9 --version)"
