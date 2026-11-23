# FTP와 SFTP
<!-- reference: _reference/ftp_sftp_official_notes.md -->

파일 전송에 쓰는 FTP(와 TLS를 더한 FTPS), 그리고 SSH 위에서 동작하는 SFTP를 비교하고 설정하는 문서입니다. 이 문서만으로 방식 고르기 → FTP의 연결 구조 이해 → vsftpd로 FTPS 서버 → OpenSSH로 SFTP 전용 계정 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: vsftpd 3.0.5, OpenSSH 10.6p2 (2026-11-23 확인)
- 예제 시험: 2026-11-23 컨테이너에서 실행. 4절은 Rocky Linux 10 패키지(vsftpd-3.0.5-13.el10), 5절은 Alpine 3.22 sshd로 확인. Ubuntu·Debian 패키지는 미실행

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 방식 비교](#1-방식-비교) / [2. FTP 연결 구조](#2-ftp-연결-구조) / [3. 고르는 기준](#3-고르는-기준) |
| [4. vsftpd로 FTPS 서버](#4-vsftpd로-ftps-서버) / [5. SFTP 전용 계정](#5-sftp-전용-계정)                |
| [6. 검증](#6-검증) / [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기)                          |

---

## 1. 방식 비교

| 항목    | FTP (RFC 959)                      | FTPS (RFC 4217)                                              | SFTP                         |
|---------|------------------------------------|--------------------------------------------------------------|------------------------------|
| 암호화  | 없음 (비밀번호도 평문)             | TLS                                                          | SSH                          |
| 포트    | 21 + 데이터용 포트                 | 21 + 데이터용 포트 (명시적 `AUTH TLS`)                       | 22 하나                      |
| 인증    | 사용자·비밀번호                    | 사용자·비밀번호 (+ 클라이언트 인증서)                        | SSH 키 또는 비밀번호         |
| 방화벽  | 데이터 포트 범위를 열어야 함       | FTP와 같고, 암호화 때문에 방화벽의 FTP 도우미가 내용을 못 봄 | 22만 열면 됨                 |
| 쓰는 곳 | 쓰지 않음 (옛 장비·내부 전용 예외) | FTP만 지원하는 상대와 암호화가 필요할 때                     | 새로 만드는 파일 교환의 기본 |

이름이 비슷하지만 SFTP는 FTP에 암호화를 더한 것이 아니라 SSH의 하위 시스템으로 동작하는 다른 프로토콜입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. FTP 연결 구조

FTP는 명령을 주고받는 제어 연결(21)과, 파일·목록을 보내는 데이터 연결을 따로 엽니다.

```text
Passive (클라이언트가 데이터 연결도 엶, 기본)
  클라이언트 ---- 제어 21 ------------------> 서버
  클라이언트 <--- 229 (|||30004|) ----------- 서버    # 이 포트로 접속하라
  클라이언트 ---- 데이터 30004 --------------> 서버

Active (서버가 클라이언트로 데이터 연결을 엶, 옛 방식)
  클라이언트 ---- 제어 21, PORT/EPRT -------> 서버
  클라이언트 <--- 데이터 (서버 20번에서) ---- 서버    # 클라이언트 방화벽·NAT에서 막히기 쉬움
```

- 서버 방화벽은 21과 passive 포트 범위(예: 30000~30009)를 함께 엽니다.
- `229 Entering Extended Passive Mode`는 RFC 2428의 EPSV 응답으로, 포트만 알려 주고 주소는 제어 연결과 같은 주소를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고르는 기준

| 상황                            | 선택                             |
|---------------------------------|----------------------------------|
| 새로 만드는 외부 업체 파일 교환 | SFTP (전용 계정 + chroot, 5절)   |
| 상대 시스템이 FTP만 지원        | FTPS (4절), 평문 FTP는 쓰지 않음 |
| 서버 간 배포·백업               | `rsync`/`scp` over SSH           |
| 공개 다운로드 (읽기 전용)       | HTTPS                            |

[⬆ 목차로 돌아가기](#목차)

---

## 4. vsftpd로 FTPS 서버

로그인과 데이터 모두 TLS를 강제하고, 사용자를 홈 디렉터리 안에 가둡니다.

```bash
sudo dnf install -y vsftpd            # RHEL 계열 (Ubuntu·Debian: apt-get install -y vsftpd)
sudo useradd -m -d /srv/ftp/partner -s /sbin/nologin partner
sudo passwd partner
grep -q '^/sbin/nologin$' /etc/shells || echo /sbin/nologin | sudo tee -a /etc/shells   # vsftpd PAM 검사 통과용
```

```text
# /etc/vsftpd/vsftpd.conf  (Ubuntu·Debian은 /etc/vsftpd.conf)
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
chroot_local_user=YES
allow_writeable_chroot=YES
pasv_enable=YES
pasv_min_port=30000
pasv_max_port=30009
ssl_enable=YES
force_local_logins_ssl=YES
force_local_data_ssl=YES
rsa_cert_file=/etc/vsftpd/tls/fullchain.pem
rsa_private_key_file=/etc/vsftpd/tls/privkey.pem
pam_service_name=vsftpd
```

```bash
sudo systemctl enable --now vsftpd
sudo firewall-cmd --permanent --add-service=ftp --add-port=30000-30009/tcp && sudo firewall-cmd --reload
```

- 컨테이너에서 포그라운드로 띄울 때는 `background=NO`를 더합니다. 없으면 데몬으로 빠져 컨테이너가 바로 끝납니다.
- 서버가 NAT 뒤에 있으면 `pasv_address=<공인 IP>`를 지정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. SFTP 전용 계정

셸 로그인은 막고 SFTP만, 그리고 지정한 디렉터리 밖으로는 못 나가게 합니다.

```bash
sudo groupadd sftponly
sudo useradd -g sftponly -s /sbin/nologin partner
sudo mkdir -p /srv/sftp/partner/upload
sudo chown root:root /srv/sftp/partner && sudo chmod 755 /srv/sftp/partner   # chroot 최상위는 root 소유, 다른 사용자 쓰기 금지
sudo chown partner:sftponly /srv/sftp/partner/upload                         # 쓰기는 하위 디렉터리에
# partner의 공개 키를 /home/partner/.ssh/authorized_keys에 등록 (권한 700/600)
```

```text
# /etc/ssh/sshd_config.d/20-sftp.conf
Subsystem sftp internal-sftp          # 기본 sshd_config의 Subsystem 줄은 주석 처리 (중복 금지)

Match Group sftponly
    ChrootDirectory /srv/sftp/%u
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication no
```

```bash
sudo sshd -t && sudo systemctl reload sshd     # Ubuntu는 ssh
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용     | 명령                                                                                    | 기대 결과                                                               |
|------|---------------|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 1    | 평문 FTP 차단 | `curl -s -u partner:<비밀번호> ftp://ftp.example.com/ -w '%{exitcode}\n' -o /dev/null`  | `67` (로그인 거부)                                                      |
| 2    | FTPS 업로드   | `curl --ssl-reqd -u partner:<비밀번호> -T a.txt ftp://ftp.example.com/`                 | 종료 코드 0                                                             |
| 3    | FTPS 목록     | `curl --ssl-reqd -u partner:<비밀번호> ftp://ftp.example.com/`                          | 업로드한 파일                                                           |
| 4    | passive 포트  | 같은 명령에 `-v`                                                                        | `234 Proceed with negotiation.`, `229 ... (\|\|\|30004\|)` 범위 안 포트 |
| 5    | SFTP 업로드   | `printf 'put a.txt upload/a.txt\nls -l upload\n' \| sftp -b - partner@sftp.example.com` | 파일 보임                                                               |
| 6    | chroot        | `printf 'cd /etc\n' \| sftp -b - partner@sftp.example.com`                              | `No such file or directory`                                             |
| 7    | 셸 차단       | `ssh partner@sftp.example.com id`                                                       | `This service allows sftp connections only.`                            |

curl의 비밀번호 인자는 셸 이력에 남으므로 실제 계정은 `~/.netrc`(권한 600)나 `-u partner`(입력 요청)로 넘깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                                                         | 원인                                                   | 해결 방법                                                |
|------------------------------------------------------------------------------|--------------------------------------------------------|----------------------------------------------------------|
| `530 Login incorrect`                                                        | 비밀번호, 셸이 `/etc/shells`에 없음, 홈 디렉터리 없음  | 4절 `/etc/shells`, `getent passwd`로 홈 확인             |
| 로그인은 되는데 목록·전송에서 멈춤                                           | passive 포트가 방화벽에 막힘, NAT 뒤 주소              | 포트 범위 열기, `pasv_address` 설정                      |
| `500 OOPS: vsftpd: refusing to run with writable root inside chroot()`       | chroot 최상위에 쓰기 권한                              | `allow_writeable_chroot=YES` 또는 쓰기는 하위 디렉터리로 |
| SFTP 접속 직후 끊김, 서버 로그 `bad ownership or modes for chroot directory` | chroot 경로가 root 소유가 아니거나 그룹·기타 쓰기 가능 | 경로의 모든 상위 디렉터리를 root 소유, 755로             |
| 컨테이너의 vsftpd가 바로 끝남                                                | 데몬으로 빠짐                                          | `background=NO`                                          |
| 컨테이너 vsftpd가 TLS 세션 뒤 종료 코드 139                                  | 특정 배포판 빌드 문제 (Alpine 3.22 3.0.5-r2에서 관찰)  | 다른 배포판 패키지 사용, 원인 확인 전 운영에 쓰지 않음   |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [SSH 사용](./ssh.md) — 키, config, scp·sftp 기본
- [ufw·firewalld](../../04_security/hardening/ufw_firewalld.md) — 21·passive 포트·22 열기
- [TLS/SSL 가이드](../../04_security/hardening/tls_ssl_guide.md) — FTPS 인증서 발급

---

## 참고 자료

- IETF: [RFC 959 FTP](https://www.rfc-editor.org/rfc/rfc959) · [RFC 2428](https://www.rfc-editor.org/rfc/rfc2428) · [RFC 4217 FTP over TLS](https://www.rfc-editor.org/rfc/rfc4217) — ★★★★☆
- vsftpd: [vsftpd.conf manual](https://security.appspot.com/vsftpd/vsftpd_conf.html) — ★★★☆☆
- OpenSSH: [sshd_config(5)](https://man.openbsd.org/sshd_config) — ChrootDirectory, ForceCommand — ★★★★☆

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
