---
name: ftp-sftp-official-notes
description: FTP(RFC 959·2428·4217), vsftpd 판·설정, OpenSSH internal-sftp chroot와 컨테이너 확인 결과 정리.
tags:
  - ftp
  - ftps
  - sftp
  - vsftpd
last_checked: 2026-11-23
sources:
  - https://www.rfc-editor.org/rfc/rfc959
  - https://www.rfc-editor.org/rfc/rfc2428
  - https://www.rfc-editor.org/rfc/rfc4217
  - https://security.appspot.com/vsftpd.html
  - https://security.appspot.com/vsftpd/vsftpd_conf.html
  - https://man.openbsd.org/sshd_config
---

# FTP·SFTP 공식 자료 참조 노트

## 1. 기준 문서

| 문서     | 발행    | 제목                             | 요지                                  |
|----------|---------|----------------------------------|---------------------------------------|
| RFC 959  | 1985-10 | File Transfer Protocol           | 제어 연결(21)과 데이터 연결을 따로 둠 |
| RFC 2428 | 1998-09 | FTP Extensions for IPv6 and NATs | EPSV(229 응답)·EPRT                   |
| RFC 4217 | 2005-11 | Securing FTP with TLS            | `AUTH TLS`로 시작하는 명시적 FTPS     |

SFTP는 FTP와 별개로 SSH 위에서 동작하는 파일 전송이며, OpenSSH `sshd_config`의 `Subsystem sftp internal-sftp`, `ChrootDirectory`, `ForceCommand internal-sftp`로 전용 계정을 만듭니다.

## 2. 판 (2026-11-23)

| 항목                  | 판                   | 근거                        |
|-----------------------|----------------------|-----------------------------|
| vsftpd 상위           | 3.0.5                | vsftpd 사이트 다운로드 목록 |
| Ubuntu 24.04 패키지   | 3.0.5-0ubuntu3.1     | `apt-cache policy vsftpd`   |
| Rocky Linux 10 패키지 | vsftpd-3.0.5-13.el10 | `rpm -q vsftpd`             |
| Alpine 3.22 패키지    | vsftpd-3.0.5-r2      | `apk list -I`               |

## 3. 컨테이너 시험 (2026-11-23)

vsftpd 설정: 익명 끔, 로컬 사용자, chroot, passive 30000~30009, `ssl_enable=YES`, `force_local_logins_ssl=YES`, `force_local_data_ssl=YES`.

| 확인                               | Rocky 10 (3.0.5-13.el10)                                                              |
|------------------------------------|---------------------------------------------------------------------------------------|
| TLS 없이 로그인 (`curl ftp://`)    | 종료 코드 67 (로그인 거부)                                                            |
| FTPS 업로드 (`curl --ssl-reqd -T`) | 종료 코드 0                                                                           |
| FTPS 목록                          | 업로드한 파일 보임                                                                    |
| 응답                               | `234 Proceed with negotiation.`, `229 Entering Extended Passive Mode (\|\|\|30004\|)` |
| 반복 접속                          | 정상                                                                                  |

- Rocky 패키지는 `background=NO`를 주지 않으면 데몬으로 빠져 컨테이너의 주 프로세스가 끝났습니다.
- Alpine 3.22 vsftpd-3.0.5-r2는 같은 FTPS 설정에서 첫 TLS 세션 뒤 listener가 종료 코드 139(세그폴트)로 끝났습니다. TLS를 끄면 반복 접속이 정상이었고, `isolate=NO`·`isolate_network=NO`로도 같았습니다. 원인은 확인하지 못했습니다.
- 사용자 홈의 상위 디렉터리가 없으면 `adduser`가 홈을 만들지 못해 로그인이 `530 Login incorrect`로 실패했습니다.

SFTP 전용 서버(Alpine sshd, `Match Group sftponly` + `ChrootDirectory /srv/sftp/%u` + `ForceCommand internal-sftp`):

| 확인                             | 결과                                                |
|----------------------------------|-----------------------------------------------------|
| 키로 `put` 후 `ls`               | `upload/a.txt` 생성, 작업 디렉터리 `/`              |
| `cd /etc`                        | `No such file or directory` (chroot 밖으로 못 나감) |
| 셸 로그인 (`ssh partner@... id`) | `This service allows sftp connections only.`        |
