---
name: openssh-official-notes
description: OpenSSH 판, 클라이언트 설정(ssh_config)·ProxyJump·포워딩·scp·sftp 동작과 컨테이너 확인 결과 정리.
tags:
  - ssh
  - openssh
  - networking
  - security
last_checked: 2026-11-23
sources:
  - https://www.openssh.com/releasenotes.html
  - https://github.com/openssh/openssh-portable/tags
  - https://man.openbsd.org/ssh
  - https://man.openbsd.org/ssh_config
  - https://man.openbsd.org/ssh-keygen
  - https://man.openbsd.org/sftp
---

# OpenSSH 공식 자료 참조 노트

## 1. 판 (2026-11-23)

| 항목                | 판                                     | 근거                                 |
|---------------------|----------------------------------------|--------------------------------------|
| OpenSSH 최신        | 10.6p2 (2026-11-05), 10.6 (2026-10-06) | 릴리스 노트, GitHub 태그 `V_10_6_P2` |
| Ubuntu 24.04 패키지 | 1:9.6p1-3ubuntu13.20                   | `apt-cache policy openssh-server`    |
| Alpine 3.22 패키지  | OpenSSH_10.0p2                         | 컨테이너 `ssh -V`                    |

배포판 패키지는 상위 판보다 낮아도 보안 수정이 역이식되므로 판 번호만으로 취약 여부를 판단하지 않습니다.

## 2. 클라이언트 동작 (man 페이지)

- `ssh_config`는 처음 찾은 값을 씁니다. 그래서 구체적인 `Host` 블록을 위에, `Host *` 기본값을 아래에 둡니다.
- `ProxyJump`(`-J`)는 지정한 호스트를 거쳐 대상에 접속합니다. `ProxyJump none`은 경유를 끕니다.
- `ssh -G <호스트>`는 접속하지 않고 적용될 설정을 출력합니다.
- `StrictHostKeyChecking accept-new`는 처음 보는 호스트 키만 자동 등록하고, 바뀐 키는 거부합니다.
- `-L 로컬포트:대상:포트`는 로컬 포워딩, `-R`은 원격 포워딩, `-D`는 SOCKS 프록시, `-N`은 명령 없이 포워딩만, `-f`는 백그라운드.
- `sftp -b -`는 표준 입력의 명령을 일괄 실행합니다.

## 3. 컨테이너 시험 (2026-11-23)

구성: 클라이언트·`bastion`이 있는 front 네트워크, `bastion`·`app`·`web(nginx)`이 있는 back 네트워크. 서버는 Alpine 3.22 sshd(비밀번호 인증 끔, root 로그인 금지), 키는 ed25519.

| 확인                                    | 결과                                                            |
|-----------------------------------------|-----------------------------------------------------------------|
| `ssh bastion`                           | 처음 접속 때 `Permanently added 'bastion' (ED25519)`, 접속 성공 |
| `ssh app` (`ProxyJump bastion`)         | 성공                                                            |
| `ssh -o ProxyJump=none app`             | `Could not resolve hostname app` (front에서 닿지 않음)          |
| `ssh -G app`                            | `user ops`, `hostname app`, `proxyjump bastion`                 |
| 비밀번호만으로 시도 (`BatchMode=yes`)   | `Permission denied (publickey).`                                |
| `ssh -f -N -L 18080:web:80 app` 후 curl | `200`                                                           |
| `scp` 후 원격 `cat`                     | 내용 일치                                                       |
| `sftp -b -` (`put`, `ls -l`)            | 파일 생성 확인                                                  |
| `sshd -t`                               | 설정 문법 오류 없음 (기동 성공)                                 |
