# rsync 보안·튜닝 운영 가이드
<!-- reference: _reference/rsync_official_notes.md -->

rsync를 서버 간 백업·배포에 사용할 때 필요한 전송 방식 선택, SSH 제한 계정, rsync daemon hardening, TLS 적용, 성능 튜닝, 검증과 롤백 절차를 정리합니다.

이 문서는 rsync 자체가 백업 일관성·스냅샷·암호화를 모두 제공한다고 가정하지 않습니다. 데이터베이스는 별도 백업 도구 또는 스냅샷으로 일관된 시점을 확보한 뒤 rsync로 전송합니다.

## 목차

| 섹션                                                                                                                               |
|------------------------------------------------------------------------------------------------------------------------------------|
| [1. 운영 기준](#1-운영-기준) / [2. 전송 방식 선택](#2-전송-방식-선택) / [3. SSH 제한 전송](#3-ssh-제한-전송)                       |
| [4. rsync daemon hardening](#4-rsync-daemon-hardening) / [5. TLS 적용](#5-tls-적용) / [6. 성능 튜닝](#6-성능-튜닝)                 |
| [7. 안전한 실행 절차](#7-안전한-실행-절차) / [8. 검증과 모니터링](#8-검증과-모니터링) / [9. 장애 대응과 롤백](#9-장애-대응과-롤백) |
| [10. 운영 체크리스트](#10-운영-체크리스트) / [참고 자료](#참고-자료)                                                               |

## 1. 운영 기준

### 보안 우선순위

1. 신뢰할 수 없는 네트워크에서는 SSH 또는 인증서 검증 TLS를 사용합니다.
2. 백업 수신 계정·module은 필요한 경로와 동작만 허용합니다.
3. 삭제 옵션은 기본값으로 사용하지 않고 dry-run 결과를 검토한 뒤 승인합니다.
4. rsync daemon을 사용하면 `path`, `uid`, `gid`, `use chroot`, 접근 제어, 인증, 파일 권한을 함께 설정합니다.
5. 성능 튜닝은 전송량만 보지 않고 CPU, 디스크 I/O, 임시 공간, 복원 가능성을 함께 측정합니다.

### 권장 선택 기준

| 상황                       | 기본 선택                                  | 피해야 할 구성                         |
|----------------------------|--------------------------------------------|----------------------------------------|
| 서버 간 백업 push          | SSH + `rrsync -wo`                         | 일반 shell 계정에 개인키만 배포        |
| SSH pull 또는 일반 동기화  | SSH + 제한된 service account               | 패스워드 인증과 광범위한 sudo 권한     |
| 기존 daemon module 유지    | 사설망 daemon 또는 `rsync-ssl`/TLS proxy   | TCP `873`을 인터넷에 직접 노출         |
| 수신 전용 로그·binlog 보관 | write-only module 또는 `rrsync -wo`        | 수신 계정의 목록 조회·삭제 허용        |
| 대용량 파일 전송           | 측정 후 `--partial-dir`, `--delay-updates` | 무조건 `--inplace`                     |
| WAN 구간                   | 인증된 TLS/SSH + 압축·대역폭 제한 측정     | 암호화되지 않은 daemon 인증만으로 보호 |

> `rrsync`: SSH의 `authorized_keys`에서 허용 경로와 rsync 옵션을 제한하는 rsync 공식 제공 스크립트입니다. 일반 shell 명령 실행을 허용하지 않는 백업 전용 키에 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 전송 방식 선택

| 접속 형식                | 암호화 여부                 | 기본 포트 | 사용 판단                                    |
|--------------------------|-----------------------------|-----------|----------------------------------------------|
| `host:path`              | SSH 사용 시 암호화          | TCP `22`  | 일반적인 기본 선택                           |
| `host::module`           | daemon protocol 자체는 평문 | TCP `873` | 사설망 또는 별도 보호 구간에서만 사용        |
| `rsync://host/module`    | daemon protocol 자체는 평문 | TCP `873` | TLS proxy 또는 SSH tunnel 없이 사용하지 않음 |
| `rsync-ssl host::module` | TLS                         | TCP `874` | CA chain·hostname 검증을 활성화한 경우 사용  |

단일 콜론 형식은 remote shell을 사용합니다. 원격 shell의 기본값은 SSH이며, 실제 암호화 여부는 SSH 설정과 접속 경로를 함께 확인합니다.

이중 콜론 또는 `rsync://` 형식의 daemon 연결은 `auth users`와 `secrets file`을 설정해도 데이터 스트림이 암호화되지 않습니다. 인증과 전송 암호화는 별도 요구사항입니다.

### SSH 기본 실행 예시

처음에는 삭제 없이 dry-run으로 변경 목록을 검토합니다.

```bash
rsync -a --dry-run --itemize-changes \
    -e 'ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes' \
    /srv/app/ Secureuser123@192.0.2.1:/srv/backup/app/
```

검토 결과가 예상과 일치할 때만 실제 전송을 실행합니다.

```bash
rsync -a --itemize-changes \
    -e 'ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes' \
    /srv/app/ Secureuser123@192.0.2.1:/srv/backup/app/
```

`StrictHostKeyChecking=yes`를 사용하려면 사전에 검증한 서버 키를 백업 계정의 `known_hosts`에 배포해야 합니다. 자동화 환경에서 `StrictHostKeyChecking=no`로 우회하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 3. SSH 제한 전송

SSH 기반 push 백업은 수신 계정의 키에 forced command를 지정하고, `rrsync`로 경로·옵션을 제한하는 구성이 기본입니다.

### 수신 서버 디렉터리와 계정

```bash
sudo install -d -o lsync -g lsync -m 0750 /srv/rsync/incoming
sudo install -d -o lsync -g lsync -m 0700 /home/lsync/.ssh
sudo touch /home/lsync/.ssh/authorized_keys
sudo chown lsync:lsync /home/lsync/.ssh/authorized_keys
sudo chmod 0600 /home/lsync/.ssh/authorized_keys
```

`lsync`는 문서용 계정명입니다. 실제 운영에서는 전송 목적별로 별도 계정을 만들고, 다른 서비스와 홈 디렉터리·개인키를 공유하지 않습니다.

`rrsync` 공식 문서는 login shell이 Bash이면 forced command보다 먼저 사용자 Bash 시작 파일이 실행될 수 있다고 경고합니다. `/bin/dash` 같은 단순 shell을 사용하거나, 계정이 홈 디렉터리와 시작 파일을 변경할 수 없고 제한 경로 밖으로 파일을 쓸 수 없도록 보장합니다. `rrsync` 실행 파일과 wrapper도 전송 계정이 수정할 수 없어야 합니다.

### `authorized_keys` 제한 예시

`rrsync` 설치 경로는 배포판과 설치 방법에 따라 다르므로 `command -v rrsync`로 확인합니다.

```text
from="192.0.2.10",command="/usr/local/bin/rrsync -wo -munge -no-del /srv/rsync/incoming",no-pty,no-agent-forwarding,no-port-forwarding,no-X11-forwarding,no-user-rc ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... lsync-backup
```

각 제한의 목적은 다음과 같습니다.

| 제한                  | 목적                                          |
|-----------------------|-----------------------------------------------|
| `from="192.0.2.10"`   | 지정된 원본 서버 또는 pattern에서만 키 허용   |
| `command="..."`       | 요청된 shell command 대신 forced command 실행 |
| `rrsync -wo`          | 지정 경로에 write-only 전송                   |
| `-munge`              | 수신 symlink를 따라갈 수 없는 형태로 저장     |
| `-no-del`             | `--delete*`, `--remove*` 옵션 거부            |
| `no-pty`              | TTY 할당 차단                                 |
| `no-agent-forwarding` | SSH agent forwarding 차단                     |
| `no-port-forwarding`  | TCP port forwarding 차단                      |
| `no-X11-forwarding`   | X11 forwarding 차단                           |
| `no-user-rc`          | `~/.ssh/rc` 실행 차단                         |

OpenSSH가 `restrict`를 지원하면 forwarding, agent, X11, PTY, user rc 제한을 묶어 적용할 수 있습니다. 레거시 호환성이 중요하면 위와 같이 명시적인 `no-*` 옵션을 사용하고 실제 접속으로 검증합니다.

`from=`의 주소는 NAT 또는 Bastion을 거친 경우 백업 서버가 관찰하는 실제 출발지 주소를 기준으로 합니다. IP가 변경되는 환경에서는 CIDR 또는 관리되는 hostname pattern을 사용하되, 허용 범위를 불필요하게 넓히지 않습니다.

`rrsync`는 기본적으로 restricted directory의 절대 경로를 전송 인자로 허용하지 않습니다. 아래 예시처럼 제한 루트 기준 상대 경로를 사용합니다. 절대 경로 호환이 반드시 필요하면 forced command에 `-absolute`를 추가할 수 있지만, 먼저 상대 경로로 표준화합니다. 또한 기본 single-run lock 때문에 동일 계정의 동시 전송은 거부될 수 있으므로 작업을 직렬화하거나 목적별 계정을 분리합니다.

### 원본 서버 실행 예시

```bash
install -m 0700 -d ~/.ssh
install -m 0600 /secure/path/lsync_backup_ed25519 ~/.ssh/lsync_backup_ed25519

rsync -a --partial --delay-updates \
    -e 'ssh -i ~/.ssh/lsync_backup_ed25519 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes' \
    /var/log/app/ lsync@192.0.2.1:app/
```

`-no-del`을 사용한 수신 키에서는 client의 `--delete`나 `--remove-source-files`가 거부됩니다. 보관본 삭제가 필요한 운영 정책이라면 별도 관리 절차와 삭제 전 승인 흐름을 사용하고, 백업 전송 키에 삭제 권한을 추가하지 않습니다.

`-munge`는 저장된 symlink 값에 접두사를 붙여 디스크에서 따라갈 수 없게 합니다. 복원에는 별도의 `rrsync -ro -munge` 제한 키 또는 공식 `munge-symlinks` 지원 도구를 사용하고, symlink가 원래 값으로 복구되는지 복원 테스트에 포함합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. rsync daemon hardening

daemon은 네트워크 클라이언트에 module 경로를 노출합니다. 직접 사용할 때는 사설 인터페이스·방화벽·module 권한을 함께 제한합니다. 아래 예시는 수신 전용 module입니다.

### `/etc/rsyncd.conf` 예시

```ini
uid = rsync
gid = rsync
use chroot = yes
max connections = 8
address = 192.0.2.1

[backup-in]
    path = /srv/rsync/incoming
    read only = no
    write only = yes
    numeric ids = yes
    hosts allow = 192.0.2.10
    hosts deny = *
    auth users = rsync-in
    secrets file = /etc/rsyncd.secrets
    strict modes = yes
    auth digest = sha256
    munge symlinks = yes
    insecure links = no
    refuse options = delete
```

운영 시 다음을 확인합니다.

- `uid`, `gid`를 설정해 transfer worker가 root로 파일을 처리하지 않게 합니다.
- 업로드가 필요 없는 module은 `read only = yes`를 유지합니다.
- 수신 전용 module은 `write only = yes`로 다운로드를 차단합니다.
- `use chroot = yes`를 유지하고, chroot 실패를 허용하는 배포판 기본 동작에 의존하지 않습니다.
- `hosts allow/deny`, daemon `address`, host firewall을 모두 적용합니다.
- plain chroot module은 chroot 자체가 탈출을 막으므로 `munge symlinks` 기본값이 `no`입니다. 예시는 수신 symlink를 저장소에서 사용할 수 없는 형태로 유지하도록 `yes`를 명시하며, module 안에 `/rsyncd-munged/` 경로가 없어야 합니다.
- `insecure links = no`를 유지하여 daemon의 symlink race 방어를 사용합니다. `yes`는 symlink escape·TOCTOU 방어를 비활성화하므로 사용하지 않습니다.
- `refuse options = delete`는 write-only 보관 module에서 client 삭제 옵션을 제한하는 방어층입니다.

### secrets file 보호

```bash
sudo install -o root -g root -m 0600 /dev/null /etc/rsyncd.secrets
printf '%s\n' 'rsync-in:SecurePassword123' | sudo tee /etc/rsyncd.secrets >/dev/null
```

`SecurePassword123`은 문서용 placeholder입니다. 운영 비밀값은 명령행·Git·일반 로그에 남기지 않고 별도 시크릿 관리 절차로 주입합니다. `strict modes = yes`에서는 other 읽기·쓰기 권한과 root daemon의 소유권 조건을 확인합니다. `auth digest = sha256`은 SHA-256 이상을 요구하므로 rsync `3.2.0` 미만 client와 호환되지 않으며, 양단의 `rsync --version` 출력에서 지원 알고리즘을 확인합니다.

daemon 인증은 전송 암호화가 아닙니다. TCP `873` 경로가 신뢰할 수 없는 네트워크를 통과하면 SSH tunnel 또는 인증서 검증 TLS를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. TLS 적용

기존 rsync daemon module을 유지해야 하고 SSH remote-shell로 전환하기 어려운 경우 `rsync-ssl` 또는 TLS proxy를 사용합니다.

### `rsync-ssl` client 예시

```bash
export RSYNC_SSL_CA_CERT=/etc/ssl/certs/backup-ca-chain.pem

rsync-ssl -a --dry-run --itemize-changes \
    rsync://backup.example.com:874/backup-in/ \
    /srv/restore-test/
```

`RSYNC_SSL_CA_CERT`를 설정하면 서버 인증서의 CA chain과 접속 hostname을 검증합니다. 다음 설정은 암호화만 사용하고 peer 인증을 약화하므로 운영 환경에서 사용하지 않습니다.

```bash
# 사용 금지: 인증서 검증 전체 해제
export RSYNC_SSL_CA_CERT=

# 사용 금지: stunnel 인증서 검증 없이 실행
export RSYNC_SSL_ALLOW_INSECURE_STUNNEL=1

# 예외적으로만 사용: OpenSSL·stunnel backend의 hostname 검사 생략
export RSYNC_SSL_SKIP_HOSTNAME_CHECK=1
```

hostname 검사 생략은 인증서 이름과 실제 접속 주소가 합법적으로 일치하지 않는 경우에만 임시 예외로 사용합니다. 가능하면 DNS 이름을 인증서 SAN(Subject Alternative Name)에 맞추고 이 예외를 제거합니다.

> SAN(Subject Alternative Name): TLS 인증서가 유효한 DNS 이름·IP 주소 등을 나열하는 확장 필드입니다. 일반적인 hostname 검증은 접속한 이름이 SAN에 포함되는지 확인합니다.

### TLS proxy 구조

```text
backup client ── TLS :874 ──> HAProxy/Nginx ── rsync :873 ──> local daemon
                                  │
                                  └── backend :873은 proxy만 접근
```

같은 호스트에 proxy와 daemon을 배치하면 daemon을 loopback에만 바인딩하고, 다른 호스트라면 backend port에 proxy source만 접근하도록 firewall을 설정합니다. TLS proxy의 인증서 개인키는 proxy 계정과 운영 관리자만 읽을 수 있어야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 성능 튜닝

튜닝은 한 번에 여러 옵션을 켜지 말고, 동일한 데이터셋으로 baseline과 변경 결과를 비교합니다. 전송률만 높이고 CPU·디스크·복원 안정성을 악화시키면 운영상 개선이 아닙니다.

### 주요 옵션과 trade-off

| 옵션                           | 효과                                       | 주의사항                                          |
|--------------------------------|--------------------------------------------|---------------------------------------------------|
| `--compress-choice=zstd`       | WAN에서 전송량 감소                        | CPU 사용량과 양단 지원 버전 확인                  |
| `--skip-compress=LIST`         | 이미 압축된 확장자 재압축 방지             | 데이터 유형별 목록 검증 필요                      |
| `--bwlimit=RATE`               | socket I/O 대역폭 제한                     | 백업 완료 시간이 늘어날 수 있음                   |
| `--whole-file`                 | delta 계산 없이 전체 파일 전송             | 대역폭을 더 사용하며 대용량 변경 파일에 주의      |
| `--no-whole-file`              | local transfer의 whole-file 기본 동작 해제 | 보통 더 느리며 측정 후 사용                       |
| `--partial-dir=.rsync-partial` | 중단 파일을 별도 staging 영역에 보관       | 잔여 파일 정리·권한·디스크 여유 필요              |
| `--delay-updates`              | 완료된 갱신 파일을 마지막에 연속 배치      | 전체 목록 메모리·추가 공간 필요, 전체 원자성 없음 |
| `--inplace`                    | 대상 파일 갱신 방식                        | 중단 시 부분 상태 노출, 원자 교체 아님            |
| `--numeric-ids`                | 이름 조회 없이 UID/GID 숫자 유지           | 양단의 ID 정책을 사전에 확인                      |
| `--timeout=SECONDS`            | 데이터 I/O 무응답 시간 제한                | 느린 회선을 실패로 오판하지 않도록 설정           |
| `--contimeout=SECONDS`         | daemon 연결 수립 시간 제한                 | SSH remote-shell에는 동일하게 적용되지 않음       |

### 환경별 시작점

| 환경                     | 시작 설정                                                                |
|--------------------------|--------------------------------------------------------------------------|
| 같은 LAN, 작은 파일 다수 | 압축 없이 baseline 측정, `--info=progress2,stats2`, 디스크 I/O 관찰      |
| WAN, 텍스트·로그 중심    | `--compress-choice=zstd`, 보수적인 `--bwlimit`, `--partial-dir` 검토     |
| 이미 압축된 백업 파일    | 압축 비활성화 또는 `--skip-compress` 목록으로 CPU 절약                   |
| 대용량 파일, 공간 부족   | `--partial-dir`와 디스크 여유 확인, `--inplace`는 복원 정책 검토 후 사용 |
| 갱신 파일 노출 시점 단축 | `--delay-updates`, 추가 공간과 동일 파일시스템 rename 가능 여부 확인     |

`--inplace`는 대상 파일을 전송 중 직접 변경하므로 웹 콘텐츠·설정 파일·복원 대상 파일에는 기본값으로 사용하지 않습니다. 중단 시 대상 파일이 갱신 중 상태로 남을 수 있으므로, 노출 시점을 줄여야 하면 `--delay-updates` 같은 staging 방식을 우선 검토합니다.

`--delay-updates`는 완료된 임시 파일을 전송 마지막에 빠르게 하나씩 rename하여 갱신 시점을 가깝게 만들 뿐, 파일 집합 전체를 하나의 트랜잭션으로 교체하지 않습니다. 전체 파일 목록을 메모리에 유지하고 모든 갱신 파일의 추가 사본을 저장할 공간이 필요하며, 다른 파일시스템으로는 rename할 수 없습니다.

`--checksum`은 파일의 빠른 크기·mtime 비교보다 더 많은 I/O와 CPU를 사용할 수 있습니다. 정기적인 무결성 점검이나 메타데이터가 신뢰되지 않는 구간에 한정하고, 매 실행의 기본값으로 만들기 전에 비용을 측정합니다.

### 측정 명령 예시

```bash
# 변경 목록 사전 확인
rsync -a --dry-run --itemize-changes \
    -e 'ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes' \
    /srv/test-data/ Secureuser123@192.0.2.1:/srv/backup-test/data/

# staging 경로에서 실제 전송 측정
/usr/bin/time -v rsync -a --info=progress2,stats2 --bwlimit=50m \
    -e 'ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes' \
    /srv/test-data/ Secureuser123@192.0.2.1:/srv/backup-test/data/
```

`--dry-run`은 실제 파일 데이터를 보내지 않으므로 bytes sent/received, literal/matched data, speedup을 처리량 baseline으로 사용하지 않습니다. 실제 측정은 staging에서 동일한 source와 동일한 초기 destination 상태로 반복하고 CPU time, elapsed time, bytes sent/received, 디스크 사용량을 비교합니다. `--bwlimit` 값은 네트워크 전체 대역폭이 아니라 rsync socket I/O 제한값으로 취급합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 안전한 실행 절차

### 사전 점검

```bash
rsync --version
ssh -G -o BatchMode=yes Secureuser123@192.0.2.1 | grep -Ei 'hostname|user|port|identityfile|stricthostkeychecking'
df -h /srv/data /srv/backup
df -i /srv/data /srv/backup
ss -tnp | grep -E ':22|:873|:874' || true
```

- 양단 rsync 버전과 지원 option을 확인합니다.
- source가 데이터베이스의 live data인지 확인하고, 필요하면 DB native backup·snapshot 결과를 전송합니다.
- destination의 inode, 디스크 여유, 임시 공간을 확인합니다.
- SSH host key와 `authorized_keys` 제한을 사전 배포합니다.
- daemon을 사용하면 TCP `873`이 허용된 네트워크 범위를 확인합니다.

### 삭제가 포함된 동기화

`--delete`는 source에 없는 destination 파일을 삭제합니다. 다음 순서를 강제합니다.

```bash
# 1. 삭제 대상 확인
rsync -a --dry-run --itemize-changes --delete \
    /srv/app/ Secureuser123@192.0.2.1:/srv/app/

# 2. 결과를 보관·검토한 뒤 승인된 경우에만 실행
rsync -a --itemize-changes --delete \
    /srv/app/ Secureuser123@192.0.2.1:/srv/app/
```

수신 전용 backup module은 `write only`와 `refuse options = delete` 또는 `rrsync -no-del`로 client 삭제를 차단하는 구성을 우선합니다. 삭제가 필요한 미러 운영은 보관 정책·dry-run 승인·복원 테스트를 별도로 갖춥니다.

### 실패와 재실행

- 자동화에서는 `BatchMode=yes`를 사용해 패스워드 prompt로 작업이 멈추지 않게 합니다.
- 네트워크 중단을 고려하면 `--partial-dir`을 검토하되, staging 디렉터리의 소유권과 정리 정책을 명시합니다.
- `--delay-updates`를 사용하면 전송 중 대상 파일이 부분 상태로 노출되는 시간을 줄일 수 있지만 임시 공간이 필요합니다.
- 성공 로그만 남기지 말고 exit code, bytes sent/received, 변경 파일 수, 대상 디스크 사용량을 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 검증과 모니터링

### 보안 설정 검증

```bash
# SSH 수신 서버
sudo stat -c '%A %U:%G %n' /home/lsync/.ssh /home/lsync/.ssh/authorized_keys
sudo grep -nE 'from=|command=|no-pty|no-agent-forwarding|no-port-forwarding|no-X11-forwarding|no-user-rc' \
    /home/lsync/.ssh/authorized_keys

# daemon listening 범위
sudo ss -ltnp | grep -E ':873|:874'

# daemon 설정·인증 실패 로그는 배포판 경로에 맞게 확인
sudo journalctl -u rsync -u rsyncd --since '1 hour ago' --no-pager
```

`authorized_keys`와 secrets file의 실제 비밀값을 로그나 보고서에 복사하지 않습니다. 출력은 권한·소유자·제한 옵션만 확인하는 범위로 제한합니다.

### 기능 검증

```bash
# 제한 계정이 일반 shell을 얻지 못하는지 확인
ssh -i ~/.ssh/lsync_backup_ed25519 \
    -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes \
    lsync@192.0.2.1 'uname -a'

# 허용된 rsync 전송만 dry-run
rsync -a --dry-run --itemize-changes \
    -e 'ssh -i ~/.ssh/lsync_backup_ed25519 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes' \
    /srv/test-data/ lsync@192.0.2.1:test-data/
```

첫 번째 명령은 forced command가 동작하는지 확인하는 negative test입니다. `uname -a`가 실행되면 즉시 키 제한을 수정합니다. 실제 운영 데이터 대신 별도 staging 디렉터리에서 검증합니다.

### 무결성·복원 검증

- 전송 exit code가 0인지 확인합니다.
- `--itemize-changes`, `--stats` 결과를 작업 ID와 함께 보관합니다.
- 대상 파일 수·크기·mtime 또는 별도 checksum을 source와 비교합니다.
- 월 1회 이상 별도 복원 디렉터리로 샘플 또는 전체 복원을 수행합니다.
- 데이터베이스는 rsync 파일 복사 성공과 데이터베이스 복구 가능성을 동일하게 취급하지 않습니다.

### 모니터링 항목

| 항목                 | 경보 기준 예시                                |
|----------------------|-----------------------------------------------|
| SSH/daemon 인증 실패 | 평소보다 급증하거나 허용되지 않은 source 발생 |
| 전송 실패율          | 연속 실패, exit code 23/30/35 증가            |
| 전송 지연            | 정해진 백업 창을 초과                         |
| 대상 디스크          | 여유 공간·inode 임계치 미만                   |
| 변경량               | 평소 범위를 벗어난 대량 추가·삭제             |
| 복원 테스트          | checksum·파일 수·애플리케이션 검증 실패       |

[⬆ 목차로 돌아가기](#목차)

## 9. 장애 대응과 롤백

### 증상별 1차 확인

| 증상                       | 우선 확인 항목                                         |
|----------------------------|--------------------------------------------------------|
| `Connection refused`       | listener address·port, firewall, service 상태          |
| `Permission denied`        | source/destination 소유권, `uid/gid`, 경로 권한        |
| SSH key가 거부됨           | `from=`, `known_hosts`, key mode, 서버 로그            |
| forced command 오류        | `rrsync` 경로, 허용 경로, client option                |
| daemon authentication 실패 | username, secrets file 소유권·mode, `auth digest`      |
| TLS hostname 오류          | 접속 hostname, 인증서 SAN, `RSYNC_SSL_CA_CERT`         |
| 전송 속도 저하             | 압축 CPU, disk I/O, `--bwlimit`, RTT, 변경량           |
| 삭제가 거부됨              | `-no-del`, `refuse options = delete`가 의도된 동작인지 |

### 설정 변경 롤백

1. 변경 전 `/etc/rsyncd.conf`, `/etc/rsyncd.secrets`, `authorized_keys`, TLS proxy 설정을 별도 root-only 위치에 백업합니다.
2. 새 설정은 staging host 또는 별도 port에서 먼저 검증합니다.
3. daemon·proxy를 reload한 뒤 listener, 로그, dry-run 전송을 확인합니다.
4. 장애가 발생하면 직전 설정을 복원하고 서비스를 reload합니다.
5. 롤백 후 새 설정의 문제와 복원된 설정의 검증 결과를 작업 기록에 남깁니다.

SSH 키 교체는 기존 키를 먼저 삭제하지 않습니다. 새 제한 키를 추가하고 dry-run 전송 및 negative test를 통과시킨 뒤 이전 키를 제거합니다. 이 순서를 지켜야 백업 창에 접근이 끊기는 사고를 피할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 10. 운영 체크리스트

### 배포 전

- [ ] 전송 경로가 SSH 또는 인증서 검증 TLS인지 확인.
- [ ] 일반 shell 계정 대신 목적별 제한 계정 사용.
- [ ] `from=`, `command=`, `no-pty`, forwarding 제한 적용.
- [ ] 수신 전용이면 `rrsync -wo -munge -no-del` 또는 `write only`와 symlink 정책 적용.
- [ ] daemon이면 `use chroot`, `uid/gid`, `hosts allow/deny`, `address`, firewall 적용.
- [ ] `secrets file` mode·소유권과 placeholder 제거 여부 확인.
- [ ] writable module의 symlink 보호와 `refuse options` 확인.
- [ ] source·destination 디스크·inode·임시 공간 확인.

### 실행 중

- [ ] 첫 실행은 `--dry-run --itemize-changes`로 검토.
- [ ] `--delete`, `--inplace`, `--checksum` 사용 근거 기록.
- [ ] CPU·메모리·disk I/O·네트워크·전송량 측정.
- [ ] exit code와 전송 통계를 중앙 로그에 기록.
- [ ] 예상하지 못한 대량 변경·삭제가 있으면 작업 중지.

### 실행 후

- [ ] 대상 파일 수·크기·checksum 또는 애플리케이션 검증 수행.
- [ ] partial 파일과 임시 디렉터리 정리 정책 확인.
- [ ] 샘플 복원 또는 정기 복원 테스트 결과 기록.
- [ ] 키·인증서·secrets file의 만료·교체 일정 확인.
- [ ] 설정 변경 시 rollback 지점과 검증 결과 보관.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- [rsync 공식 보안 참조 노트](../../_reference/rsync_official_notes.md)
- rsync Documentation: [rsync.samba.org/documentation.html](https://rsync.samba.org/documentation.html) — ★★★☆☆
- rsync Manual: [download.samba.org/pub/rsync/rsync.1](https://download.samba.org/pub/rsync/rsync.1) — ★★★☆☆
- rsync Daemon Configuration: [download.samba.org/pub/rsync/rsyncd.conf.5](https://download.samba.org/pub/rsync/rsyncd.conf.5) — ★★★☆☆
- rrsync Manual: [download.samba.org/pub/rsync/rrsync.1](https://download.samba.org/pub/rsync/rrsync.1) — ★★★☆☆
- rsync SSL Helper: [download.samba.org/pub/rsync/rsync-ssl.1](https://download.samba.org/pub/rsync/rsync-ssl.1) — ★★★☆☆
- OpenSSH `sshd(8)`: [man.openbsd.org/sshd](https://man.openbsd.org/sshd) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-14

**마지막 업데이트**: 2026-09-14

© 2026 siasia86. Licensed under CC BY 4.0.
