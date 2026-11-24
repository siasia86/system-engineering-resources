# 메일 프로토콜 (SMTP · IMAP · POP3)
<!-- reference: _reference/mail_protocols_official_notes.md -->

메일이 보내는 사람에게서 받는 사람의 메일함까지 가는 경로와, 그 구간마다 쓰는 프로토콜(SMTP, IMAP, POP3)과 포트를 정리한 문서입니다. 이 문서만으로 흐름 이해 → 포트 고르기 → Postfix(발송·수신)와 Dovecot(메일함 조회) 기본 서버 → swaks·curl·openssl로 검증까지 따라 할 수 있게 썼습니다.

- 기준: RFC 5321(SMTP), 6409(제출), 8314(TLS 권고), 9051(IMAP4rev2), 1939(POP3). 판은 Postfix 3.11.8, Dovecot 2.4.5 (2026-11-24 확인)
- 예제 시험: 2026-11-24 Debian 13 컨테이너(postfix 3.10.13, dovecot 2.4.1)에서 5·6절 실행. Dovecot 2.3 설정(Ubuntu 24.04 등)과 RHEL 계열 패키지는 미실행

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 메일이 가는 길](#1-메일이-가는-길) / [2. 포트와 TLS](#2-포트와-tls) / [3. SMTP 대화](#3-smtp-대화) |
| [4. IMAP과 POP3](#4-imap과-pop3) / [5. Postfix와 Dovecot 기본 서버](#5-postfix와-dovecot-기본-서버)    |
| [6. 검증](#6-검증) / [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기)                          |

---

## 1. 메일이 가는 길

```text
 보내는 사람                                                       받는 사람
 [메일 프로그램] --587/465 SMTP--> [발송 서버] --25 SMTP--> [수신 서버] --IMAP 993/POP3 995--> [메일 프로그램]
   (MUA)          제출(인증)       (MSA/MTA)   MX 조회 후    (MTA → MDA)   메일함 조회(인증)       (MUA)
                                               서버 간 중계    메일함에 저장
```

| 구성 요소 | 하는 일                                               | 예                                |
|-----------|-------------------------------------------------------|-----------------------------------|
| MUA       | 사용자가 메일을 쓰고 읽는 프로그램                    | Thunderbird, Outlook, 휴대폰 앱   |
| MSA       | 사용자 메일을 인증 후 받아들이는 제출 서버 (RFC 6409) | Postfix `submission` 서비스       |
| MTA       | 다른 서버로 메일을 중계하고 받는 서버 (RFC 5321)      | Postfix, Exim, Microsoft Exchange |
| MDA       | 받은 메일을 메일함(Maildir 등)에 저장                 | Postfix `local`, Dovecot LMTP     |
| IMAP/POP3 | 사용자가 메일함을 읽는 서버                           | Dovecot                           |

- 발송 서버는 받는 사람 도메인의 MX 레코드를 조회해 수신 서버를 찾습니다(`dig MX example.com +short`).
- SMTP는 보내는(넣는) 프로토콜이고, 메일함을 읽는 것은 IMAP이나 POP3입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 포트와 TLS

| 포트 | 용도                | TLS 방식                        | 인증           | 기준 RFC   |
|------|---------------------|---------------------------------|----------------|------------|
| 25   | 서버 간 중계 (수신) | STARTTLS (선택, 상대가 지원 시) | 보통 받지 않음 | 5321, 3207 |
| 587  | 사용자 메일 제출    | STARTTLS (필수로 설정)          | 필수           | 6409       |
| 465  | 사용자 메일 제출    | 암시적 TLS (연결 즉시)          | 필수           | 8314       |
| 143  | IMAP                | STARTTLS                        | 필수           | 9051       |
| 993  | IMAPS               | 암시적 TLS                      | 필수           | 8314       |
| 110  | POP3                | STLS                            | 필수           | 1939, 2595 |
| 995  | POP3S               | 암시적 TLS                      | 필수           | 8314       |

- RFC 8314는 제출과 조회에 STARTTLS보다 암시적 TLS(465, 993, 995)를 권장합니다. STARTTLS는 평문으로 시작하므로 중간에서 `STARTTLS` 광고를 지우는 공격(다운그레이드)에 약합니다.
- 25번은 서버 간 중계라 상대 서버가 TLS를 지원하지 않을 수 있어 보통 "가능하면 TLS"(`may`)로 둡니다. 서버 간 TLS 강제는 MTA-STS(RFC 8461)나 DANE이 다룹니다.
- 클라우드·가정용 회선은 25번 발신을 막는 경우가 많아 사용자는 587·465로 제출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. SMTP 대화

SMTP는 명령과 세 자리 응답 코드를 주고받는 텍스트 프로토콜입니다.

```text
S: 220 mail.example.com ESMTP
C: EHLO client.example.net
S: 250-mail.example.com
S: 250-STARTTLS
S: 250 SMTPUTF8
C: MAIL FROM:<alice@example.net>       <- 봉투 발신자 (반송 주소, SPF 검사 대상)
S: 250 2.1.0 Ok
C: RCPT TO:<bob@example.com>           <- 봉투 수신자 (실제 배달 대상)
S: 250 2.1.5 Ok
C: DATA
S: 354 End data with <CR><LF>.<CR><LF>
C: From: Alice <alice@example.net>     <- 헤더 From (사용자에게 보이는 주소, DMARC 기준)
C: To: Bob <bob@example.com>
C: Subject: hello
C:
C: 본문
C: .
S: 250 2.0.0 Ok: queued as 4D4D81D14B1AC
C: QUIT
```

- 봉투(`MAIL FROM`, `RCPT TO`)와 헤더(`From:`, `To:`)는 서로 다를 수 있습니다. 메일링 리스트·숨은 참조(BCC)가 이 차이로 동작하고, 위조도 같은 차이를 이용합니다. 그래서 SPF·DKIM·DMARC로 발신 도메인을 확인합니다.
- 응답 코드 첫 자리: `2`는 성공, `4`는 임시 실패(나중에 재시도), `5`는 영구 실패. 자세한 코드는 [에러 코드](./error_codes.md)에 있습니다.
- 서버가 `EHLO` 응답에 광고한 기능(`STARTTLS`, `AUTH`, `SIZE` 등)만 쓸 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. IMAP과 POP3

| 항목             | IMAP                                     | POP3                                      |
|------------------|------------------------------------------|-------------------------------------------|
| 메일 위치        | 서버에 두고 여러 기기에서 같은 상태로 봄 | 내려받아 보관 (서버에서 지우는 것이 기본) |
| 폴더             | 서버 폴더 지원                           | 받은편지함 하나                           |
| 읽음 표시 동기화 | 됨                                       | 안 됨                                     |
| 서버 저장 공간   | 많이 씀                                  | 적게 씀                                   |
| 쓰는 곳          | 대부분의 현재 메일 환경                  | 한 기기에서만 받는 단순 수신, 보관 전용   |

- 현재 IMAP 표준은 IMAP4rev2(RFC 9051)이며 IMAP4rev1(RFC 3501)을 대체합니다. 서버가 실제로 어느 판을 지원하는지는 `CAPABILITY` 응답으로 확인합니다. 시험한 Dovecot 2.4.1은 `IMAP4rev1`만 광고했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Postfix와 Dovecot 기본 서버

목표: 도메인 `example.com`의 메일을 받아 시스템 사용자의 `~/Maildir`에 저장하고, 사용자는 587·465로 보내고 993·995로 읽습니다. 사용자 인증은 Dovecot이 하고 Postfix는 Dovecot에 인증을 맡깁니다(SASL).

### 5.1 설치 (Debian·Ubuntu)

```bash
sudo apt install postfix dovecot-imapd dovecot-pop3d
postconf -h mail_version      # Postfix 판
dovecot --version             # Dovecot 판 (2.4와 2.3은 설정 문법이 다름)
```

설치 중 Postfix 질문에는 `Internet Site`와 메일 이름(`example.com`)을 고릅니다. 인증서는 실제 운영에서는 공인 인증서([TLS 인증서](../../04_security/hardening/tls_ssl_guide.md))를 쓰고, 아래 예는 `/etc/ssl/mail/cert.pem`, `key.pem` 경로를 가정합니다.

### 5.2 Postfix (main.cf · master.cf)

```bash
sudo postconf -e "myhostname = mail.example.com" \
  "mydomain = example.com" \
  "myorigin = \$mydomain" \
  "mydestination = \$myhostname, \$mydomain, localhost" \
  "mynetworks = 127.0.0.0/8" \
  "home_mailbox = Maildir/" \
  "smtpd_tls_cert_file = /etc/ssl/mail/cert.pem" \
  "smtpd_tls_key_file = /etc/ssl/mail/key.pem" \
  "smtpd_tls_security_level = may" \
  "smtpd_tls_auth_only = yes" \
  "smtpd_sasl_type = dovecot" \
  "smtpd_sasl_path = private/auth" \
  "disable_vrfy_command = yes"
```

| 설정                             | 뜻                                                          |
|----------------------------------|-------------------------------------------------------------|
| `mydestination`                  | 이 서버가 최종 목적지인 도메인 (로컬 배달)                  |
| `mynetworks`                     | 인증 없이 중계를 허용할 주소. 로컬만 둡니다                 |
| `smtpd_tls_security_level = may` | 25번: 상대가 원하면 TLS                                     |
| `smtpd_tls_auth_only = yes`      | TLS 전에는 `AUTH`를 광고하지 않음 (비밀번호 평문 전송 방지) |
| `smtpd_sasl_type = dovecot`      | 사용자 인증을 Dovecot 소켓에 맡김                           |
| `disable_vrfy_command = yes`     | `VRFY`로 계정 존재 여부를 알아내는 것을 막음                |

제출 포트(587, 465)는 `master.cf`에 서비스를 추가하고 그 서비스에서만 인증과 TLS를 강제합니다.

```bash
sudo postconf -M "submission/inet=submission inet n - y - - smtpd"
sudo postconf -P "submission/inet/syslog_name=postfix/submission" \
  "submission/inet/smtpd_tls_security_level=encrypt" \
  "submission/inet/smtpd_sasl_auth_enable=yes" \
  "submission/inet/smtpd_relay_restrictions=permit_sasl_authenticated,reject"
sudo postconf -M "submissions/inet=submissions inet n - y - - smtpd"
sudo postconf -P "submissions/inet/syslog_name=postfix/submissions" \
  "submissions/inet/smtpd_tls_wrappermode=yes" \
  "submissions/inet/smtpd_sasl_auth_enable=yes" \
  "submissions/inet/smtpd_relay_restrictions=permit_sasl_authenticated,reject"
sudo postfix check && sudo systemctl reload postfix
```

`smtpd_tls_wrappermode=yes`가 465번의 암시적 TLS입니다. 25번에는 `smtpd_sasl_auth_enable`을 켜지 않아 인증 시도 자체를 받지 않습니다.

### 5.3 Dovecot 2.4 (dovecot.conf)

```text
dovecot_config_version = 2.4.1
dovecot_storage_version = 2.4.1

protocols = imap pop3
mail_driver = maildir
mail_path = ~/Maildir

ssl = required
ssl_server_cert_file = /etc/ssl/mail/cert.pem
ssl_server_key_file = /etc/ssl/mail/key.pem
ssl_min_protocol = TLSv1.2

auth_mechanisms = plain login
passdb pam {
}
userdb passwd {
}

service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0660
    user = postfix
    group = postfix
  }
}
```

- `ssl = required`: TLS 없이는 비밀번호 인증을 거부합니다. 143·110에 평문으로 접속하면 `LOGINDISABLED`가 보이고 로그인이 거절됩니다.
- `service auth`의 소켓 경로가 Postfix의 `smtpd_sasl_path = private/auth`와 맞아야 합니다(Postfix는 `/var/spool/postfix` 기준 상대 경로).
- 배포판 기본 설정은 `conf.d/` 아래에 나뉘어 있습니다. 위 내용은 필요한 값만 모은 것이며, 기존 파일을 고칠 때는 같은 이름의 설정을 찾아 바꿉니다.

Dovecot 2.3(Ubuntu 24.04 등)은 이름이 다릅니다(미실행, 2.4 이전 문법).

| 2.4                        | 2.3                                  |
|----------------------------|--------------------------------------|
| `mail_driver`, `mail_path` | `mail_location = maildir:~/Maildir`  |
| `ssl_server_cert_file`     | `ssl_cert = </etc/ssl/mail/cert.pem` |
| `ssl_server_key_file`      | `ssl_key = </etc/ssl/mail/key.pem`   |
| `passdb pam { }`           | `passdb { driver = pam }`            |
| `dovecot_config_version`   | 없음                                 |

```bash
sudo doveconf -n               # 문법 확인과 실제 적용 값
sudo systemctl restart dovecot
```

### 5.4 방화벽

열 포트는 25, 587, 465, 993, 995입니다(143·110은 쓰지 않으면 닫습니다). 명령은 [ufw와 firewalld](../../04_security/hardening/ufw_firewalld.md)에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

`swaks`(SMTP 시험 도구), `curl`, `openssl`을 씁니다. 비밀번호는 명령에 적지 않고 물어볼 때 입력합니다.

```bash
# 25번: STARTTLS는 있고 AUTH는 없어야 함
swaks -s mail.example.com -p 25 --quit-after EHLO

# 587번: TLS 전 AUTH 없음, STARTTLS 뒤에 AUTH 광고
swaks -s mail.example.com -p 587 --quit-after EHLO
swaks -s mail.example.com -p 587 -tls --quit-after EHLO

# 587번 인증 발송 (비밀번호는 물어봄)
swaks -s mail.example.com -p 587 -tls -a PLAIN -au alice \
  -f alice@example.com -t bob@example.com --h-Subject "submission test"

# 465번 암시적 TLS
swaks -s mail.example.com -p 465 --tlsc -a PLAIN -au alice -t bob@example.com

# 외부 중계가 막혔는지 (다른 주소에서 25번으로)
swaks -s mail.example.com -p 25 -f someone@example.net -t user@example.org

# IMAPS·POP3S (-u 사용자만 주면 비밀번호를 물어봄)
curl -u bob "imaps://mail.example.com/"
curl -u bob "imaps://mail.example.com/INBOX" -X "SEARCH ALL"
curl -u bob "pop3s://mail.example.com/"

# 143번 STARTTLS와 인증서 확인
openssl s_client -starttls imap -connect mail.example.com:143 -servername mail.example.com
```

시험에서 본 결과입니다.

| 확인                   | 결과                                                              |
|------------------------|-------------------------------------------------------------------|
| 25번 EHLO              | `250-STARTTLS`, `AUTH` 없음                                       |
| 587번 STARTTLS 뒤 EHLO | `TLSv1.3`, `250-AUTH PLAIN LOGIN`                                 |
| 587번 인증 발송        | `235 2.7.0 Authentication successful`, `250 2.0.0 Ok: queued`     |
| 587번 인증 없이 외부로 | `554 5.7.1 <user@...>: Recipient address rejected: Access denied` |
| 25번 중계 시도         | `454 4.7.1 <user@...>: Relay access denied`                       |
| IMAP 143 평문 로그인   | `NO [PRIVACYREQUIRED] Cleartext authentication disallowed`        |
| IMAPS `SEARCH ALL`     | `* SEARCH 1 2 3`                                                  |
| POP3S 목록             | 메시지 번호와 크기 목록                                           |

서버 쪽에서는 로그와 큐로 확인합니다.

```bash
sudo postqueue -p                                  # 대기 큐 (비었으면 Mail queue is empty)
sudo journalctl -u postfix -n 50                   # 또는 /var/log/mail.log
sudo doveadm mailbox status -u bob "messages unseen" INBOX
```

정상 배달 로그는 `status=sent (delivered to maildir)`, 인증 제출 로그는 `sasl_method=PLAIN, sasl_username=alice`입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                                  | 원인                                         | 해결                                               |
|-------------------------------------------------------|----------------------------------------------|----------------------------------------------------|
| 메일 프로그램에서 인증 방법이 없다고 나옴             | TLS 전에 인증을 시도 (`smtpd_tls_auth_only`) | 587은 STARTTLS, 465는 SSL/TLS로 설정               |
| `454 4.7.1 Relay access denied`                       | 인증 없이 외부 도메인으로 보냄               | 25번이 아니라 587·465로 인증 후 제출               |
| `warning: SASL: Connect to private/auth failed`       | Dovecot 인증 소켓 경로·권한 불일치           | `service auth` 소켓 경로와 `user = postfix` 확인   |
| `NO [PRIVACYREQUIRED]`, `-ERR [AUTH] Cleartext ...`   | 143·110 평문 로그인                          | 993·995 또는 STARTTLS·STLS 사용                    |
| curl 종료 코드 60                                     | 인증서를 신뢰할 수 없음                      | 공인 인증서 사용, 시험이면 `--cacert`로 CA 지정    |
| 외부로 보낸 메일이 큐에 쌓임 (`Connection timed out`) | 25번 발신 차단                               | 회선·클라우드 정책 확인, 중계 서버(smarthost) 사용 |
| 받는 쪽에서 스팸 처리·거부                            | SPF·DKIM·DMARC, 역방향 DNS 미설정            | 도메인 인증 설정, PTR 레코드를 `myhostname`과 맞춤 |
| Dovecot이 2.3 설정으로 기동 실패                      | 2.4와 설정 문법이 다름                       | 5.3절 대응표로 바꾸고 `doveconf -n`으로 확인       |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [에러 코드](./error_codes.md) — SMTP 응답 코드
- [DNS 이름 해석과 장애 진단](./dns_resolution_troubleshooting.md) — MX·PTR 조회
- [TLS/SSL 가이드](../../04_security/hardening/tls_ssl_guide.md) — 인증서 발급·확인
- [ufw와 firewalld](../../04_security/hardening/ufw_firewalld.md) — 메일 포트 열기

---

## 참고 자료

- IETF: [RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321) — ★★★★☆
- IETF: [RFC 6409 Message Submission for Mail](https://www.rfc-editor.org/rfc/rfc6409) — ★★★★☆
- IETF: [RFC 8314 Cleartext Considered Obsolete](https://www.rfc-editor.org/rfc/rfc8314) — ★★★★☆
- IETF: [RFC 9051 IMAP4rev2](https://www.rfc-editor.org/rfc/rfc9051) — ★★★★☆
- IETF: [RFC 1939 POP3](https://www.rfc-editor.org/rfc/rfc1939) — ★★★☆☆
- Postfix: [TLS Support](https://www.postfix.org/TLS_README.html), [SASL Howto](https://www.postfix.org/SASL_README.html) — ★★★★☆
- Dovecot: [Documentation](https://doc.dovecot.org/) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-24

**마지막 업데이트**: 2026-11-24

© 2026 siasia86. Licensed under CC BY 4.0.
