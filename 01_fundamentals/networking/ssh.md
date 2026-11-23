# SSH 사용
<!-- reference: _reference/openssh_official_notes.md -->

원격 서버에 암호화된 연결로 접속하고 파일을 옮기는 SSH를 클라이언트 쪽 사용법 중심으로 정리한 문서입니다. 이 문서만으로 설치 → 키 만들기와 등록 → `~/.ssh/config`로 접속 정리 → 점프 호스트(ProxyJump)와 포트 포워딩 → 파일 전송 → 검증까지 따라 할 수 있게 썼습니다. 서버 보안 강화(sshd_config, fail2ban, MFA)는 함께 보기의 SSH 보안 문서에 있습니다.

- 기준 판: OpenSSH 10.6p2 (2026-11-23 확인). 배포판 패키지는 판이 낮을 수 있음 (Ubuntu 24.04는 9.6p1)
- 예제 시험: 2026-11-23 Alpine 3.22(OpenSSH 10.0p2) 컨테이너로 점프 호스트·내부 서버·웹 서버를 나눠 4~7절 명령을 실행해 확인

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 키 만들기와 등록](#3-키-만들기와-등록)                   |
| [4. ~/.ssh/config](#4-sshconfig) / [5. 점프 호스트](#5-점프-호스트) / [6. 포트 포워딩](#6-포트-포워딩) |
| [7. 파일 전송](#7-파일-전송) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                     |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                      |

---

## 1. 개요

| 구성 요소            | 역할                                              |
|----------------------|---------------------------------------------------|
| `ssh`                | 원격 셸 접속, 원격 명령 실행, 포트 포워딩         |
| `sshd`               | 서버 데몬 (기본 TCP 22)                           |
| `ssh-keygen`         | 키 생성, 지문 확인, `known_hosts` 관리            |
| `ssh-agent`          | 개인 키를 메모리에 두고 비밀문구 입력을 한 번으로 |
| `scp`, `sftp`        | 파일 복사, 대화형·일괄 파일 전송 (SSH 위)         |
| `~/.ssh/known_hosts` | 접속했던 서버의 호스트 키. 바뀌면 경고            |

인증은 비밀번호보다 공개 키를 씁니다. 서버는 `~/.ssh/authorized_keys`에 등록된 공개 키로 클라이언트를 확인하고, 클라이언트는 `known_hosts`로 서버가 바뀌지 않았는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
ssh -V                                    # 클라이언트 판
sudo apt-get install -y openssh-client openssh-server    # Ubuntu / Debian
sudo dnf install -y openssh-clients openssh-server       # RHEL 계열
sudo systemctl enable --now ssh           # Ubuntu (RHEL 계열은 sshd)
sudo sshd -t                              # 서버 설정 문법 검사 (출력 없으면 정상)
```

Windows는 기본 포함된 OpenSSH 클라이언트를 쓰고, 서버 설치는 [Windows OpenSSH 설치](../../04_security/hardening/windows_openssh_install.md)를 따릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 키 만들기와 등록

```bash
ssh-keygen -t ed25519 -C "ops@laptop"         # 비밀문구(passphrase)를 넣는 것을 권장
ssh-keygen -lf ~/.ssh/id_ed25519.pub          # 지문 확인: 256 SHA256:... (ED25519)
ssh-copy-id -i ~/.ssh/id_ed25519.pub ops@server.example.com   # 서버 authorized_keys에 추가

eval "$(ssh-agent -s)"                        # 에이전트 시작
ssh-add ~/.ssh/id_ed25519                     # 비밀문구는 여기서 한 번만
ssh-add -l                                    # 올라간 키 확인
```

`ssh-copy-id`가 없으면 공개 키 내용을 서버의 `~/.ssh/authorized_keys`에 한 줄로 붙입니다. 권한은 `~/.ssh` 700, `authorized_keys` 600이어야 합니다. 개인 키(`id_ed25519`)는 어디에도 복사하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. ~/.ssh/config

자주 쓰는 접속 정보를 이름으로 묶습니다. 처음 찾은 값을 쓰므로 구체적인 `Host`를 위에, `Host *`를 맨 아래에 둡니다.

```text
# ~/.ssh/config  (권한 600)
Host bastion
    HostName bastion.example.com
    User ops
    IdentityFile ~/.ssh/id_ed25519

Host app
    HostName 10.0.1.20
    User ops
    ProxyJump bastion

Host *
    StrictHostKeyChecking accept-new
    ServerAliveInterval 30
```

```bash
ssh app                       # 위 설정대로 bastion을 거쳐 접속
ssh -G app | grep -E '^(user|hostname|proxyjump) '    # 접속하지 않고 적용될 값 확인
# user ops
# hostname 10.0.1.20
# proxyjump bastion
```

`StrictHostKeyChecking accept-new`는 처음 보는 서버 키만 자동으로 받아들이고, 이미 아는 서버의 키가 바뀌면 거부합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 점프 호스트

내부 서버에 직접 닿지 않을 때 점프 호스트(bastion)를 거칩니다.

```bash
ssh -J ops@bastion.example.com ops@10.0.1.20      # 설정 파일 없이 한 번만
ssh app                                           # 4절 ProxyJump 설정을 쓰는 경우
ssh -o ProxyJump=none app                         # 경유를 끄고 직접 접속해 보기
```

`ProxyJump`는 점프 호스트에 개인 키를 두지 않고 클라이언트의 키로 내부 서버까지 인증합니다. 점프 호스트에서 `ssh-agent` 전달(`ForwardAgent yes`)을 켜는 방식보다 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 포트 포워딩

| 종류        | 옵션                     | 쓰임                                                            |
|-------------|--------------------------|-----------------------------------------------------------------|
| 로컬        | `-L 18080:web:80`        | 내 PC의 18080 → (SSH 서버에서 본) `web:80`. 내부 관리 화면 보기 |
| 원격        | `-R 9000:localhost:3000` | SSH 서버의 9000 → 내 PC의 3000                                  |
| 동적(SOCKS) | `-D 1080`                | 내 PC의 1080을 SOCKS 프록시로                                   |

```bash
ssh -f -N -L 18080:web:80 app      # -f 백그라운드, -N 명령 없이 포워딩만
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18080/     # 200
pkill -f 'ssh -f -N -L 18080'      # 끝나면 정리
```

서버에서 `AllowTcpForwarding no`이면 포워딩이 거부됩니다. 운영 서버는 필요한 사용자에게만 허용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 파일 전송

```bash
scp ./app.conf app:/tmp/app.conf                 # 복사 (config의 Host 이름 사용 가능)
scp -r app:/var/log/app ./logs                   # 디렉터리 가져오기
rsync -avz -e ssh ./site/ app:/srv/site/         # 바뀐 부분만 전송

printf 'put ./app.conf /tmp/app.conf\nls -l /tmp/app.conf\n' | sftp -b - app   # 일괄 실행
```

여러 파일·큰 디렉터리는 중단 뒤 이어받기가 되는 `rsync`가 편합니다. SFTP 전용 계정과 chroot는 [FTP와 SFTP](./ftp_sftp.md)에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용     | 명령                                                                                                | 기대 결과                            |
|------|---------------|-----------------------------------------------------------------------------------------------------|--------------------------------------|
| 1    | 키 인증       | `ssh bastion 'id -un'`                                                                              | 비밀번호 묻지 않고 사용자 이름 출력  |
| 2    | 경유 접속     | `ssh app hostname`                                                                                  | 내부 서버 이름                       |
| 3    | 적용 설정     | `ssh -G app`                                                                                        | 의도한 `user`·`hostname`·`proxyjump` |
| 4    | 비밀번호 차단 | `ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password -o BatchMode=yes bastion true` | `Permission denied (publickey).`     |
| 5    | 포워딩        | 6절 curl                                                                                            | `200`                                |
| 6    | 파일 전송     | `scp` 후 `ssh app cat <파일>`                                                                       | 내용 일치                            |
| 7    | 서버 설정     | `sudo sshd -t`                                                                                      | 출력 없음                            |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                                          | 원인                                      | 해결 방법                                                     |
|---------------------------------------------------------------|-------------------------------------------|---------------------------------------------------------------|
| `Permission denied (publickey).`                              | 키 미등록, 권한 문제, 다른 키를 씀        | `ssh -v`로 시도한 키 확인, `~/.ssh` 700·`authorized_keys` 600 |
| `REMOTE HOST IDENTIFICATION HAS CHANGED!`                     | 서버 재설치·주소 재사용, 또는 중간자 공격 | 서버 관리자에게 새 지문 확인 후 `ssh-keygen -R <호스트>`      |
| `Could not resolve hostname`                                  | 이름 해석 실패, 경유가 필요한 내부 주소   | DNS 확인, `ProxyJump` 설정                                    |
| `Connection timed out`                                        | 방화벽·보안 그룹, sshd 미기동             | 4계층 확인(`nc -zv host 22`), 서버 `ss -ltn`                  |
| 포워딩 `channel ... open failed: administratively prohibited` | 서버 `AllowTcpForwarding no`              | 서버 정책 확인                                                |
| 접속이 몇 분 뒤 끊김                                          | 중간 장비의 유휴 연결 정리                | `ServerAliveInterval 30`                                      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [SSH 보안](../../04_security/hardening/ssh_security.md) — sshd_config 강화, fail2ban, MFA
- [FTP와 SFTP](./ftp_sftp.md) — SFTP 전용 계정, chroot
- [rsync 보안·튜닝](../../04_security/hardening/rsync_security_tuning_guide.md) — 바뀐 부분만 전송

---

## 참고 자료

- OpenSSH: [ssh(1)](https://man.openbsd.org/ssh) · [ssh_config(5)](https://man.openbsd.org/ssh_config) · [ssh-keygen(1)](https://man.openbsd.org/ssh-keygen) · [sftp(1)](https://man.openbsd.org/sftp) — ★★★★☆
- OpenSSH: [Release notes](https://www.openssh.com/releasenotes.html) — 10.6p2 확인 2026-11-23 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
