# SSH 보안

## 목차

| 섹션 |
|------|
| [1. sshd_config 강화](#1-sshd_config-강화) / [2. 키 기반 인증](#2-키-기반-인증) / [3. fail2ban](#3-fail2ban) |
| [4. 다중 인증 (MFA)](#4-다중-인증-mfa) / [5. SSH 점검 체크리스트](#5-ssh-점검-체크리스트) |

---

## 1. sshd_config 강화

`/etc/ssh/sshd_config` 주요 설정.

```bash
# 포트 변경 (기본 22 → 비표준 포트)
Port 2222

# 루트 로그인 금지
PermitRootLogin no

# 패스워드 인증 비활성화 (키 기반만 허용)
PasswordAuthentication no
KbdInteractiveAuthentication no   # OpenSSH 9.0+, 구버전은 ChallengeResponseAuthentication no
UsePAM yes

# 빈 패스워드 금지
PermitEmptyPasswords no

# X11 포워딩 비활성화
X11Forwarding no

# 허용 사용자/그룹 제한
AllowUsers deploy Secureuser123
# AllowGroups sshusers

# 유휴 세션 타임아웃 (300초 = 5분)
ClientAliveInterval 300
ClientAliveCountMax 2

# 최대 인증 시도 횟수
MaxAuthTries 3

# 로그인 유예 시간
LoginGraceTime 30

# 강력한 암호화 알고리즘만 허용
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
```

```bash
# 설정 검증 및 재시작
sudo sshd -t
sudo systemctl reload sshd
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 키 기반 인증

```bash
# 클라이언트: 키 쌍 생성 (Ed25519 권장)
ssh-keygen -t ed25519 -C "user@example.com" -f ~/.ssh/id_ed25519

# 공개키를 서버에 복사
ssh-copy-id -i ~/.ssh/id_ed25519.pub Secureuser123@192.0.2.1

# 수동 등록 (ssh-copy-id 불가 시)
cat ~/.ssh/id_ed25519.pub | ssh Secureuser123@192.0.2.1 \
    "mkdir -p ~/.ssh && chmod 700 ~/.ssh && \
     cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

```bash
# 서버: authorized_keys 권한 확인
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 특정 키에 명령어 제한 (authorized_keys 옵션)
command="/usr/local/bin/backup.sh",no-pty,no-x11-forwarding ssh-ed25519 AAAA...
```

### ~/.ssh/config (클라이언트)

```ssh-config
Host prod-bastion
    HostName 192.0.2.1
    User Secureuser123
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. fail2ban

SSH brute-force 공격 자동 차단.

```bash
# 설치
sudo apt install fail2ban

# /etc/fail2ban/jail.local
[DEFAULT]
bantime  = 3600     # 차단 시간 (초)
findtime = 600      # 탐지 시간 윈도우
maxretry = 3        # 최대 실패 횟수
banaction = nftables-multiport

[sshd]
enabled = true
port    = 2222
logpath = %(sshd_log)s
backend = %(sshd_backend)s
```

```bash
# 시작 및 상태 확인
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd

# 수동 차단/해제
sudo fail2ban-client set sshd banip 192.0.2.1
sudo fail2ban-client set sshd unbanip 192.0.2.1

# 차단 목록 확인
sudo fail2ban-client status sshd | grep "Banned IP"
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 다중 인증 (MFA)

TOTP 기반 2FA (Google Authenticator).

```bash
# 설치
sudo apt install libpam-google-authenticator

# 사용자별 설정
google-authenticator
# → QR 코드 스캔 후 앱에 등록

# PAM 설정 (/etc/pam.d/sshd 상단에 추가)
auth required pam_google_authenticator.so

# sshd_config 수정
KbdInteractiveAuthentication yes   # OpenSSH 9.0+, 구버전은 ChallengeResponseAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. SSH 점검 체크리스트

| 항목                   | 확인 명령어                                        |
|------------------------|----------------------------------------------------|
| 루트 로그인 비활성화   | `grep PermitRootLogin /etc/ssh/sshd_config`        |
| 패스워드 인증 비활성화 | `grep PasswordAuthentication /etc/ssh/sshd_config` |
| 포트 변경 여부         | `ss -tlnp | grep sshd`                             |
| authorized_keys 권한   | `stat ~/.ssh/authorized_keys`                      |
| fail2ban 동작 여부     | `sudo fail2ban-client status sshd`                 |
| 최근 로그인 실패 기록  | `sudo journalctl -u sshd | grep Failed | tail -20` |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OpenSSH Manual: [man.openbsd.org/sshd_config](https://man.openbsd.org/sshd_config) — ★★★☆☆
- fail2ban Documentation: [fail2ban.org](https://www.fail2ban.org/wiki/index.php/Main_Page) — ★★★☆☆
- Mozilla SSH Guidelines: [infosec.mozilla.org](https://infosec.mozilla.org/guidelines/openssh) — ★★★☆☆
- OpenSSH 9.0 릴리즈 노트 (ChallengeResponseAuthentication deprecated): [openssh.com/releasenotes](https://www.openssh.com/releasenotes.html) — ★★★☆☆
- libpam-google-authenticator: [github.com/google/google-authenticator-libpam](https://github.com/google/google-authenticator-libpam) — ★★☆☆☆

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
