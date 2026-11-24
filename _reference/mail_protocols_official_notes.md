---
name: mail-protocols-official-notes
description: SMTP·제출(587·465)·IMAP·POP3 기준 RFC, Postfix·Dovecot 판과 컨테이너 확인 결과 정리.
tags:
  - smtp
  - imap
  - pop3
  - postfix
  - dovecot
  - rfc
last_checked: 2026-11-24
sources:
  - https://www.rfc-editor.org/rfc/rfc5321
  - https://www.rfc-editor.org/rfc/rfc6409
  - https://www.rfc-editor.org/rfc/rfc8314
  - https://www.rfc-editor.org/rfc/rfc3207
  - https://www.rfc-editor.org/rfc/rfc9051
  - https://www.rfc-editor.org/rfc/rfc1939
  - https://www.rfc-editor.org/rfc/rfc2595
  - https://www.rfc-editor.org/rfc/rfc3463
  - https://www.rfc-editor.org/rfc-index.txt
  - https://postfix.cs.utah.edu/announcements.html
  - https://github.com/dovecot/core/releases
---

# 메일 프로토콜 공식 자료 참조 노트

## 1. 기준 RFC (rfc-index.txt, 2026-11-24)

| RFC  | 발행    | 제목                                                    | 관계·상태                                        |
|------|---------|---------------------------------------------------------|--------------------------------------------------|
| 5321 | 2008-10 | Simple Mail Transfer Protocol                           | RFC 2821 대체, Draft Standard                    |
| 6409 | 2011-11 | Message Submission for Mail                             | 제출 포트 587, STD 72                            |
| 8314 | 2018-01 | Cleartext Considered Obsolete (TLS for Email)           | 465·993·995 암시적 TLS 권장, 1939·3501·6409 갱신 |
| 3207 | 2002-02 | SMTP Service Extension for Secure SMTP over TLS         | SMTP `STARTTLS`                                  |
| 9051 | 2021-08 | Internet Message Access Protocol (IMAP) - Version 4rev2 | RFC 3501(IMAP4rev1) 대체                         |
| 1939 | 1996-05 | Post Office Protocol - Version 3                        | STD 53                                           |
| 2595 | 1999-06 | Using TLS with IMAP, POP3 and ACAP                      | IMAP `STARTTLS`, POP3 `STLS`                     |

- RFC 8314 요지: 제출·조회 서버 연결은 STARTTLS보다 암시적 TLS(Implicit TLS)를 우선합니다. 서버 간 중계(25번 포트)는 이 문서의 범위가 아닙니다.
- SMTP 응답 코드는 RFC 5321 4.2절, 확장 상태 코드(`5.7.1` 등)는 RFC 3463이 정의합니다.

## 2. 판 (2026-11-24)

| 항목              | 판                             | 근거                                              |
|-------------------|--------------------------------|---------------------------------------------------|
| Postfix 안정판    | 3.11.8 (2026-11-22)            | 공지 목록 미러 (postfix.org 직접 조회는 HTTP 402) |
| Postfix 이전 계열 | 3.10.15 등 함께 공지           | 같은 공지                                         |
| Dovecot CE        | 2.4.5 (2026-08-28)             | GitHub `dovecot/core` 릴리스                      |
| Debian 13 패키지  | postfix 3.10.13, dovecot 2.4.1 | `apt-cache policy`, 컨테이너 기동 로그            |

- Dovecot 2.4는 2.3 설정과 호환되지 않습니다. 설정 첫머리에 `dovecot_config_version`, `dovecot_storage_version`이 필요합니다.

## 3. 컨테이너 시험 (2026-11-24)

구성: Debian 13 컨테이너 3개(`dns` unbound, `mx` Postfix 3.10.13·Dovecot 2.4.1, `client` swaks·curl·openssl), 자체 서명 P-256 인증서, 시스템 사용자 둘, Maildir.

| 확인                            | 결과                                                              |
|---------------------------------|-------------------------------------------------------------------|
| 25번 EHLO                       | `STARTTLS`는 있고 `AUTH` 없음                                     |
| 587번 EHLO (TLS 전)             | `STARTTLS`만, `AUTH` 없음 (`smtpd_tls_auth_only = yes`)           |
| 587번 STARTTLS 뒤 EHLO          | `TLSv1.3`, `AUTH PLAIN LOGIN`                                     |
| 587번 인증 발송                 | `235 2.7.0`, `250 2.0.0 Ok: queued`, 로그 `sasl_method=PLAIN`     |
| 587번 인증 없이 외부 수신자     | `554 5.7.1 ... Access denied`                                     |
| 465번 (`smtpd_tls_wrappermode`) | 연결 즉시 TLS 1.3, 인증 발송 성공                                 |
| 25번 외부 → 로컬 사용자         | `250`, 로그 `status=sent (delivered to maildir)`                  |
| 25번 외부 → 외부 (중계 시도)    | `454 4.7.1 Relay access denied` (기본 `defer_unauth_destination`) |
| IMAP 143 인사말                 | `STARTTLS LOGINDISABLED`, 평문 LOGIN은 `NO [PRIVACYREQUIRED]`     |
| IMAP 143 STARTTLS 뒤            | `AUTH=PLAIN AUTH=LOGIN` 광고                                      |
| IMAPS 993 (curl)                | `LIST`, `SEARCH 1 2 3`, 헤더 읽기 성공                            |
| POP3 110 평문 `USER`            | `-ERR [AUTH] Cleartext authentication disallowed`                 |
| POP3S 995 (curl)                | 메시지 목록 3개                                                   |
| CA 지정 없이 IMAPS              | curl 종료 코드 60, `self-signed certificate`                      |
| `doveadm mailbox status`        | `INBOX messages=3 unseen=2`                                       |

- Dovecot 2.4.1의 CAPABILITY에는 `IMAP4rev1`만 있고 `IMAP4rev2`는 광고되지 않았습니다.
- 기본 설정에서 `VRFY`가 광고되어, 주소 수집을 막으려면 `disable_vrfy_command = yes`를 둡니다.
