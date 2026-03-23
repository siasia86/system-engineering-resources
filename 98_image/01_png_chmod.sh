#!/usr/bin/env bash

find /root/32_system-engineering-resources/98_image/ -type d -exec chmod 755 {} \;
find /root/32_system-engineering-resources/98_image/ -type f -exec chmod 644 {} \;
chown sjyun:sjyun /root/32_system-engineering-resources/ -R
