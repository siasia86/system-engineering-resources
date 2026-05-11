# Linux 서버 보안 강화

## 목차

| 섹션 |
|------|
| [1. sysctl 보안 파라미터](#1-sysctl-보안-파라미터) / [2. 불필요 서비스 제거](#2-불필요-서비스-제거) / [3. 파일 권한 및 umask](#3-파일-권한-및-umask) |
| [4. auditd 감사 로그](#4-auditd-감사-로그) / [5. PAM 및 계정 정책](#5-pam-및-계정-정책) / [6. SELinux / AppArmor](#6-selinux--apparmor) |

---

## 1. sysctl 보안 파라미터

네트워크 및 커널 보안 파라미터. `/etc/sysctl.d/99-security.conf` 에 적용.

```bash
# 네트워크 보안
net.ipv4.tcp_syncookies = 1          # SYN Flood 방어
net.ipv4.conf.all.rp_filter = 1      # IP Spoofing 방어
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1

# IPv6 비활성화 (사용하지 않는 경우)
net.ipv6.conf.all.disable_ipv6 = 1

# 커널 보안
kernel.randomize_va_space = 2        # ASLR 활성화
kernel.dmesg_restrict = 1            # 일반 사용자 dmesg 제한
kernel.kptr_restrict = 2             # 커널 포인터 노출 제한
fs.suid_dumpable = 0                 # SUID 프로세스 core dump 비활성화
```

```bash
# 즉시 적용 (/etc/sysctl.d/ 하위 파일은 --system으로 적용)
sudo sysctl --system

# 확인
sudo sysctl net.ipv4.tcp_syncookies
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 불필요 서비스 제거

```bash
# 실행 중인 서비스 목록
systemctl list-units --type=service --state=running

# 불필요 서비스 비활성화 예시
sudo systemctl disable --now avahi-daemon
sudo systemctl disable --now cups
sudo systemctl disable --now bluetooth
sudo systemctl disable --now rpcbind

# 설치된 불필요 패키지 제거 (Ubuntu)
sudo apt purge telnet rsh-client rsh-redone-client nis talk
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 파일 권한 및 umask

```bash
# umask 설정 (기본값 022 → 027 권장)
# /etc/profile 또는 /etc/bash.bashrc 에 추가
umask 027

# 중요 파일 권한 확인
stat /etc/passwd    # 644
stat /etc/shadow    # 640 또는 000
stat /etc/sudoers   # 440

# SUID/SGID 파일 목록 확인
find / -perm /4000 -o -perm /2000 2>/dev/null | grep -v proc

# world-writable 파일 확인
find / -perm -002 -not -path "/proc/*" -not -path "/sys/*" 2>/dev/null
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. auditd 감사 로그

```bash
# 설치
sudo apt install auditd audispd-plugins   # Ubuntu
sudo yum install audit                    # RHEL/CentOS

# 주요 감사 규칙 (/etc/audit/rules.d/audit.rules)
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /var/log/auth.log -p wa -k auth_log
-a always,exit -F arch=b64 -S execve -k exec_commands
-a always,exit -F arch=b64 -S open -F exit=-EACCES -k access_denied
```

```bash
# 적용 및 확인
sudo augenrules --load
sudo auditctl -l

# 로그 조회
sudo ausearch -k identity -ts today
sudo aureport --summary
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. PAM 및 계정 정책

```bash
# 패스워드 정책 (/etc/security/pwquality.conf)
minlen = 12
minclass = 3        # 대/소문자, 숫자, 특수문자 중 3종류
maxrepeat = 3
dcredit = -1
ucredit = -1
lcredit = -1
ocredit = -1

# 계정 잠금 정책 (/etc/pam.d/common-auth 상단에 추가)
auth required pam_faillock.so preauth silent deny=5 unlock_time=900
auth required pam_faillock.so authfail deny=5 unlock_time=900

# 잠긴 계정 확인 및 해제
sudo faillock --user Secureuser123
sudo faillock --user Secureuser123 --reset
```

```bash
# 비활성 계정 잠금 (90일 미사용 시)
sudo useradd -D -f 90

# 만료된 계정 확인
sudo passwd -S -a | grep -v "P "
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. SELinux / AppArmor

### SELinux (RHEL/CentOS)

```bash
# 상태 확인
getenforce          # Enforcing / Permissive / Disabled
sestatus

# 모드 변경 (즉시)
sudo setenforce 1   # Enforcing
sudo setenforce 0   # Permissive (디버깅용)

# 영구 설정 (/etc/selinux/config)
SELINUX=enforcing

# 거부 로그 확인
sudo ausearch -m avc -ts today
sudo sealert -a /var/log/audit/audit.log
```

### AppArmor (Ubuntu/Debian)

```bash
# 상태 확인
sudo aa-status

# 프로파일 모드 변경
sudo aa-enforce /etc/apparmor.d/usr.sbin.nginx    # enforce
sudo aa-complain /etc/apparmor.d/usr.sbin.nginx   # complain (로그만)

# 거부 로그 확인
sudo journalctl -k | grep apparmor | grep DENIED
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- CIS Benchmarks: [cisecurity.org/cis-benchmarks](https://www.cisecurity.org/cis-benchmarks) — ★★★☆☆
- Linux Audit Documentation: [linux-audit.com](https://linux-audit.com/) — ★★☆☆☆
- NSA RHEL Hardening Guide: [media.defense.gov](https://media.defense.gov/) — ★★★☆☆
- Linux kernel sysctl 파라미터 레퍼런스: [kernel.org/doc/html/latest/admin-guide/sysctl](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/) — ★★★☆☆
- Linux-PAM System Administrator's Guide: [linux-pam.org](https://www.linux-pam.org/Linux-PAM-html/Linux-PAM_SAG.html) — ★★★☆☆
- Red Hat SELinux Guide: [access.redhat.com/documentation/selinux](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/using_selinux/) — ★★★☆☆
- Ubuntu AppArmor Documentation: [ubuntu.com/server/docs/apparmor](https://ubuntu.com/server/docs/apparmor) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-03

**마지막 업데이트**: 2026-05-03

© 2026 siasia86. Licensed under CC BY 4.0.
