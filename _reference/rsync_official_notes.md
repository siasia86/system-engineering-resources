---
name: rsync-official-notes
description: rsync 공식 문서 기반 전송 보안, daemon hardening, SSH 제한, TLS 설정 참조 노트.
tags:
  - rsync
  - file-transfer
  - backup
  - ssh
  - security
last_checked: 2026-09-14
sources:
  - https://rsync.samba.org/documentation.html
  - https://download.samba.org/pub/rsync/rsync.1
  - https://download.samba.org/pub/rsync/rsyncd.conf.5
  - https://download.samba.org/pub/rsync/rrsync.1
  - https://download.samba.org/pub/rsync/rsync-ssl.1
  - https://github.com/RsyncProject/rsync/releases
  - https://api.github.com/repos/RsyncProject/rsync/releases/latest
  - https://github.com/RsyncProject/rsync/blob/master/SECURITY.md
  - https://man.openbsd.org/sshd
---

# rsync 공식 보안 참조 노트

## 목차

| 섹션                                                   |
|--------------------------------------------------------|
| [1. 버전 현황](#1-버전-현황)                           |
| [2. 전송 방식과 암호화](#2-전송-방식과-암호화)         |
| [3. rsync daemon 보안 설정](#3-rsync-daemon-보안-설정) |
| [4. SSH 기반 제한 전송](#4-ssh-기반-제한-전송)         |
| [5. TLS와 운영 검증](#5-tls와-운영-검증)               |

## 1. 버전 현황

| 항목        | 버전·상태               | 확인일     |
|-------------|-------------------------|------------|
| rsync       | 3.5.0                   | 2026-09-14 |
| 최신 릴리스 | `v3.5.0`, 2026-08-13    | 2026-09-14 |
| 지원 정책   | 현재 릴리스만 적극 지원 | 2026-09-14 |

- 최신 릴리스는 공식 GitHub Releases API에서 확인합니다.
- rsync 공식 보안 정책은 현재 릴리스만 적극적으로 지원한다고 명시합니다.
- 클라이언트와 서버는 공통으로 지원하는 최신 protocol version을 자동 협상합니다.
- `--protocol`로 이전 protocol version을 강제하면 보안 기능과 checksum 동작이 약화될 수 있으므로 호환성 목적 외에는 사용하지 않습니다.
- Protocol version 30 미만의 daemon 연결은 약한 MD4 인증 digest를 사용하게 됩니다.

> Protocol version: rsync 클라이언트와 서버가 파일 목록·checksum·전송 기능의 호환 방식을 협상할 때 사용하는 프로토콜 버전입니다. 전송 암호화를 제공하는 TLS나 SSH와는 별도의 계층입니다.

## 2. 전송 방식과 암호화

rsync는 원격 전송에 remote shell 방식 또는 rsync daemon 직접 연결 방식을 사용합니다.

| 접속 형식                | 전송 방식              | 기본 암호화 | 보안 판단                                |
|--------------------------|------------------------|-------------|------------------------------------------|
| `host:path`              | remote shell, 보통 SSH | 예          | 인증·암호화 전송의 기본 권장 경로        |
| `host::module`           | rsync daemon 직접 연결 | 아니오      | 신뢰할 수 없는 네트워크에 직접 노출 금지 |
| `rsync://host/module`    | rsync daemon 직접 연결 | 아니오      | TLS proxy, `rsync-ssl`, SSH tunnel 필요  |
| `rsync-ssl host::module` | TLS로 감싼 daemon 연결 | 예          | CA chain과 hostname 검증 필수            |

- 단일 콜론(`:`)을 포함한 `host:path`는 remote shell을 사용합니다. rsync 공식 문서는 기본 remote shell이 SSH이며, SSH가 peer 인증과 연결 암호화를 제공한다고 설명합니다.
- 이중 콜론(`::`) 또는 `rsync://`는 TCP 기반 rsync daemon에 직접 연결합니다. daemon protocol은 인증은 제공하지만 전송 데이터 암호화는 제공하지 않습니다.
- 직접 daemon 연결은 일반적으로 TCP `873` 포트를 사용합니다.
- `auth users`와 `secrets file`은 daemon 사용자 인증 설정이며, 데이터 스트림 암호화를 대신하지 않습니다.
- 민감한 데이터는 SSH tunnel 또는 TLS proxy를 사용합니다.

### TLS 적용

공식 `rsync-ssl` helper는 SSL/TLS 지원 daemon에 연결합니다.

- 기본 TLS daemon 포트는 TCP `874`이며, 필요하면 포트를 변경할 수 있습니다.
- `RSYNC_SSL_CA_CERT`를 설정하면 서버 인증서를 CA chain과 연결 hostname에 대해 검증합니다.
- `RSYNC_SSL_CA_CERT`를 빈 값으로 설정하면 암호화만 하고 인증서 검증을 끕니다.
- `RSYNC_SSL_ALLOW_INSECURE_STUNNEL=1`은 stunnel의 인증서 검증 없이 실행하도록 허용하므로 사용하지 않습니다.
- `RSYNC_SSL_SKIP_HOSTNAME_CHECK=1`은 인증서 chain은 검증하지만 hostname 검증을 생략합니다. 현재 공식 helper 문서 기준으로 OpenSSL·stunnel backend에 적용되며, 인증서 이름과 접속 주소가 합법적으로 일치하지 않는 경우에만 제한적으로 사용합니다.
- 서버 측에서는 HAProxy, Nginx stream 등 TLS proxy를 앞에 둘 수 있습니다. backend rsync daemon 포트는 proxy만 접근하도록 제한하고, 같은 호스트라면 `127.0.0.1:873`에만 바인딩하는 구성이 권장됩니다.

## 3. rsync daemon 보안 설정

rsync daemon은 네트워크 클라이언트에 파일시스템 일부를 노출하며, master process가 root 권한으로 실행될 수 있으므로 방어적으로 설정해야 합니다.

### 기본 격리와 권한

| 설정                | 공식 동작·권장 방향                                   |
|---------------------|-------------------------------------------------------|
| `path`              | 각 module을 지정된 디렉터리 트리로 제한               |
| `use chroot = yes`  | module path 안으로 worker process를 격리              |
| `uid`, `gid`        | file transfer worker를 낮은 권한 사용자·그룹으로 실행 |
| `read only = yes`   | 업로드가 필요 없는 module의 기본값                    |
| `write only = yes`  | 수신 전용 보관 module에서 다운로드 차단               |
| `numeric ids = yes` | chroot 내부의 이름 조회와 예기치 않은 매핑 회피       |
| `max connections`   | 동시 연결 수 제한                                     |
| `address`           | daemon이 수신할 로컬 주소 제한                        |
| `hosts allow/deny`  | 접속 client IP 또는 hostname 제한                     |

- `use chroot = yes`는 구현 취약점이나 경로 탈출의 영향을 줄이는 강한 경계입니다.
- chroot를 사용하면 superuser 권한과 chroot 내부의 사용자·그룹 조회 파일이 필요할 수 있습니다.
- `uid`, `gid`를 설정하면 file transfer worker를 낮은 권한 사용자·그룹으로 전환합니다.
- root로 daemon master를 실행하더라도 위 설정을 적용한 module worker는 낮은 권한으로 동작합니다.
- binlog 수신 전용 module은 `write only = yes`를 검토하고, 업로드에 필요한 파일 권한만 부여합니다.
- 수신 전용 module에서는 `refuse options = delete`를 함께 검토하여 client가 보관 파일을 삭제하지 못하게 합니다.
- `hosts allow`와 `hosts deny`만 의존하지 말고 OS firewall과 daemon `address` 제한을 함께 적용합니다.

### 인증과 비밀정보

```ini
[mysql-bin]
    path = /backup/mysql-bin
    use chroot = yes
    uid = lsync
    gid = lsync
    read only = no
    write only = yes
    refuse options = delete
    hosts allow = 192.0.2.10
    hosts deny = *
    auth users = lsync
    secrets file = /etc/rsyncd.secrets
    strict modes = yes
```

- `auth users`를 설정하면 client가 사용자명과 비밀번호를 제시하는 challenge-response 인증을 수행합니다.
- `secrets file`에는 `username:password` 형식의 항목을 저장합니다.
- `strict modes = yes`가 기본값이면 secrets file이 other에게 읽기·쓰기 가능하거나 root daemon에서 root 소유가 아니면 거부됩니다.
- 긴 고엔트로피 비밀값을 사용하고 명령행 인자에 비밀번호를 직접 넣지 않습니다.
- daemon 인증은 전송 암호화가 아니므로 `auth users`만 설정한 채 신뢰할 수 없는 네트워크에 노출하지 않습니다.
- 최신 rsync에서 지원하는 경우 `auth digest`로 약한 인증 digest 협상을 제한할 수 있지만, 민감한 전송은 SSH 또는 인증서 검증 TLS를 함께 사용해야 합니다.

### Symlink와 옵션 제한

> Symlink: 파일 경로 대신 다른 파일이나 디렉터리를 가리키는 파일시스템 객체입니다. 쓰기 가능한 rsync module에서 악의적인 symlink가 생성되면 이후 작업이 module 외부 경로를 가리킬 수 있습니다.

- `munge symlinks` 기본값은 chroot 형태에 따라 다릅니다. module path 자체를 chroot root로 제공하면 기본 비활성화되고, non-chroot 또는 `/./` 내부 경로 module에서는 기본 활성화됩니다.
- 수신 symlink를 저장소에서 따라갈 수 없는 형태로 유지하려면 `munge symlinks = yes`를 명시합니다. 이 설정은 symlink 값에 `/rsyncd-munged/` 접두사를 붙이며, module 안에 해당 경로가 이미 있으면 module 실행이 거부됩니다.
- `insecure links = yes`는 symlink escape와 TOCTOU 방어를 다시 비활성화하므로, 완전히 격리된 단일 테넌트 환경 외에는 사용하지 않습니다.
- `refuse options`로 module에서 필요하지 않은 client 옵션을 거부합니다.
- binlog 보관 module은 삭제·source 제거·device 복사와 같이 보관본에 영향을 줄 수 있는 옵션을 별도로 검토합니다.
- `--copy-links`는 symlink를 실제 대상 파일로 역참조할 수 있으므로, 제한 전송에서는 허용 여부를 확인합니다.

## 4. SSH 기반 제한 전송

rsync 공식 문서는 `host:path` remote-shell 전송이 기본적으로 SSH를 사용하며, SSH가 peer 인증과 연결 암호화를 제공한다고 설명합니다.

### `rrsync` 제한 계정

공식 `rrsync`는 SSH login을 rsync 전송으로 제한하는 스크립트입니다.

```text
command="rrsync -wo -no-del /backup/mysql-bin",no-pty,no-agent-forwarding,no-port-forwarding,no-X11-forwarding,no-user-rc ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... lsync-binlog
```

- `command=`는 사용자가 요청한 command 대신 지정된 command만 실행합니다.
- `rrsync -wo`는 지정된 디렉터리에 쓰기 전용 전송을 허용합니다.
- `-no-del`은 `--delete*`와 `--remove*` 옵션을 제한합니다.
- `rrsync`는 전송 경로가 제한된 디렉터리 내부에 머무르는지 검사하고, 기본적으로 `--copy-links`를 거부합니다.
- `rrsync`는 지원하는 rsync 옵션의 일부만 허용합니다.
- `command=`를 직접 `/usr/bin/rsync`로 지정하고 client argument를 검증 없이 실행하지 않습니다. 공식 `rrsync` 또는 검토된 daemon-over-SSH 구성을 사용합니다.

### `authorized_keys` 옵션

| 옵션                  | 제한 내용                                   |
|-----------------------|---------------------------------------------|
| `from="192.0.2.10"`   | 지정된 client IP 또는 pattern에서만 키 사용 |
| `command="..."`       | forced command 실행, client command 무시    |
| `no-pty`              | TTY 할당 금지                               |
| `no-agent-forwarding` | SSH agent forwarding 금지                   |
| `no-port-forwarding`  | TCP port forwarding 금지                    |
| `no-X11-forwarding`   | X11 forwarding 금지                         |
| `no-user-rc`          | `~/.ssh/rc` 실행 금지                       |
| `restrict`            | 위 제한을 묶어서 적용하는 최신 OpenSSH 옵션 |

OpenSSH의 `command=`가 지정되면 client가 원래 요청한 command는 무시됩니다. 원래 요청은 `SSH_ORIGINAL_COMMAND` 환경 변수로 전달되므로, 제한 스크립트는 이를 검증해야 합니다.

`from=`은 키가 도난되어도 허용된 출발지 외부에서 사용하기 어렵게 만드는 추가 방어입니다. 원본 서버가 NAT나 Bastion을 거치면 백업 서버가 관찰하는 실제 출발지 IP를 사용해야 합니다.

### SSH 키 파일 보호

```bash
chmod 700 /home/lsync/.ssh
chmod 600 /home/lsync/.ssh/authorized_keys
chown -R lsync:lsync /home/lsync/.ssh
```

- 개인키는 원본 서버의 lsync 전용 계정만 읽을 수 있어야 합니다.
- `authorized_keys`의 제한된 공개키와 lsyncd 전용 개인키를 다른 용도와 공유하지 않습니다.
- `rrsync` 실행 파일과 wrapper는 lsync 계정이 수정할 수 없는 소유권·권한으로 보관합니다.
- `restrict` 지원 여부는 실제 OpenSSH 버전에서 확인하고, legacy 환경에서는 명시적 `no-*` 옵션을 사용해 검증합니다.

## 5. TLS와 운영 검증

### 전송 경로 선택

| 요구사항                      | 공식 문서 기준 선택                          |
|-------------------------------|----------------------------------------------|
| SSH 접속과 파일 경로 사용     | `host:path` 또는 `default.rsyncssh`          |
| 기존 daemon module 유지       | TLS proxy 또는 `rsync-ssl`                   |
| 873 daemon을 외부에 직접 노출 | 사용하지 않음                                |
| 수신 전용 binlog 보관         | `write only`, `refuse options = delete` 검토 |
| 키 도난 범위 축소             | `from=`와 forced command, forwarding 차단    |

### 검증 항목

- 원본과 대상의 rsync 버전을 확인하고, 가능하면 현재 지원 릴리스로 통일합니다.
- `host::module` 또는 `rsync://`를 사용하는 경우 TCP `873` 경로가 평문인지 확인합니다.
- TLS를 사용하는 경우 CA chain과 hostname 검증이 실제로 활성화되어 있는지 확인합니다.
- `rsync-ssl`의 `RSYNC_SSL_CA_CERT`가 설정되어 있는지 확인합니다.
- `authorized_keys`의 `from=`, `command=`, forwarding·TTY 제한을 실제 접속으로 검증합니다.
- rsync daemon의 `path`, `uid`, `gid`, `use chroot`, `read only`, `write only`, `hosts allow/deny`, `secrets file` 권한을 점검합니다.
- writable module의 `munge symlinks`와 `insecure links` 설정을 확인합니다.
- 보관 module의 삭제 옵션과 파일 삭제 권한을 별도로 검증합니다.
- 전송 로그, 인증 실패, 연결 수, 전송 지연, 대상 디스크 사용량을 모니터링합니다.
- 전송 성공 여부와 별개로 대상 binlog의 파일 크기, 순서, checksum, 복구 가능성을 검증합니다.

### 공식 문서의 제한사항

- rsync daemon protocol 자체는 데이터 전송 암호화를 제공하지 않습니다.
- daemon 인증은 transport-level peer authentication이나 TLS server identity verification을 대체하지 않습니다.
- `rsync-ssl`에서 인증서 검증을 끄면 TLS는 암호화만 제공하고 중간자 공격 방어는 제공하지 않습니다.
- `use chroot`가 실패하도록 설정된 환경에서는 chroot 경계가 사라질 수 있으므로 daemon 로그와 시작 결과를 확인합니다.
- 최신 rsync의 보안 개선이 구형 배포판 패키지에 존재한다고 가정하지 않습니다. 실제 실행 파일 버전과 지원 옵션을 확인합니다.

## 참고 자료

- rsync Documentation: [rsync.samba.org/documentation.html](https://rsync.samba.org/documentation.html) — ★★★☆☆
- rsync Manual: [download.samba.org/pub/rsync/rsync.1](https://download.samba.org/pub/rsync/rsync.1) — ★★★☆☆
- rsync Daemon Configuration: [download.samba.org/pub/rsync/rsyncd.conf.5](https://download.samba.org/pub/rsync/rsyncd.conf.5) — ★★★☆☆
- rrsync Manual: [download.samba.org/pub/rsync/rrsync.1](https://download.samba.org/pub/rsync/rrsync.1) — ★★★☆☆
- rsync SSL Helper: [download.samba.org/pub/rsync/rsync-ssl.1](https://download.samba.org/pub/rsync/rsync-ssl.1) — ★★★☆☆
- rsync Security Policy: [github.com/RsyncProject/rsync/SECURITY.md](https://github.com/RsyncProject/rsync/blob/master/SECURITY.md) — ★★★☆☆
- OpenSSH `sshd`: [man.openbsd.org/sshd](https://man.openbsd.org/sshd) — ★★★☆☆
