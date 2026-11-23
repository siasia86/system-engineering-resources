# GitLab
<!-- reference: _reference/gitlab_official_notes.md -->

Git 저장소, Merge Request, CI/CD, 이슈 관리를 한 제품으로 제공하는 플랫폼입니다. GitLab.com(SaaS)과 자체 설치(Self-Managed)로 쓸 수 있고, 이 문서는 자체 설치를 중심으로 합니다. 이 문서만으로 요구 사항 확인 → Docker로 설치 → 첫 로그인과 저장소 → 검증까지 따라 할 수 있게 썼습니다. CI 파이프라인 작성은 함께 보기의 GitLab CI 문서에 있습니다.

- 기준 판: GitLab CE 19.5 (`gitlab/gitlab-ce:19.5.8-ce.0`, 2026-11-23 확인)
- 예제 시험: 미실행. 작성 환경의 메모리가 공식 권장(단일 노드 16 GB)에 못 미쳐 컨테이너를 띄우지 않았고, 명령은 docs.gitlab.com 설치 문서와 대조했습니다

## 목차

| 섹션                                                                                     |
|------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 요구 사항](#2-요구-사항) / [3. Docker로 설치](#3-docker로-설치) |
| [4. 첫 로그인과 저장소](#4-첫-로그인과-저장소) / [5. 운영](#5-운영) / [6. 검증](#6-검증) |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)       |

---

## 1. 개요

| 항목      | GitLab.com (SaaS)        | Self-Managed (자체 설치)                |
|-----------|--------------------------|-----------------------------------------|
| 운영 주체 | GitLab                   | 직접 설치·백업·업그레이드               |
| 판        | 요금제별 기능            | CE(`gitlab-ce` 이미지), EE(`gitlab-ee`) |
| 맞는 경우 | 운영 부담 없이 바로 사용 | 사내망·데이터 위치 요구, 외부 연결 제한 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 요구 사항

| 항목   | 기준                                                                      |
|--------|---------------------------------------------------------------------------|
| 메모리 | 단일 노드 16 GB가 기준. 메모리 제약 환경 설정을 하면 8 GB에서도 운영 가능 |
| 스왑   | 가능하면 끔 (켜 두면 성능이 크게 떨어질 수 있음)                          |
| 디스크 | 저장소·CI 산출물·백업 크기에 맞춰 여유 있게, 데이터는 별도 볼륨           |
| 포트   | 80·443(웹), 22(SSH clone). 호스트 sshd와 겹치면 다른 포트로 공개          |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Docker로 설치

```bash
export GITLAB_HOME=/srv/gitlab
sudo mkdir -p $GITLAB_HOME/{config,logs,data}

docker run --detach \
  --hostname gitlab.example.com \
  --env GITLAB_OMNIBUS_CONFIG="external_url 'http://gitlab.example.com'" \
  --publish 443:443 --publish 80:80 --publish 2222:22 \
  --name gitlab \
  --restart always \
  --volume $GITLAB_HOME/config:/etc/gitlab \
  --volume $GITLAB_HOME/logs:/var/log/gitlab \
  --volume $GITLAB_HOME/data:/var/opt/gitlab \
  --shm-size 256m \
  gitlab/gitlab-ce:19.5.8-ce.0

docker logs -f gitlab          # 첫 기동은 몇 분 걸림
docker ps --filter name=gitlab # STATUS가 (healthy)가 될 때까지 기다림
```

- `external_url`은 사용자가 접속할 주소입니다. clone 주소와 메일 링크에 쓰이므로 처음부터 정확히 정합니다.
- 호스트의 22번은 서버 관리용 sshd가 쓰므로 GitLab SSH는 2222로 공개했습니다. 이때 `gitlab_rails['gitlab_shell_ssh_port'] = 2222`를 `GITLAB_OMNIBUS_CONFIG`에 더하면 화면의 clone 주소에도 반영됩니다.
- 이미지 태그는 `latest` 대신 판을 고정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 첫 로그인과 저장소

```bash
sudo docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

1. 브라우저로 `external_url`에 접속해 `root`와 위 비밀번호로 로그인합니다. 이 파일은 24시간 뒤 첫 재시작 때 자동으로 지워지므로 바로 비밀번호를 바꿉니다.
2. Admin Area에서 가입 허용(Sign-up)을 끄고, 일반 사용자 계정을 만들어 그 계정으로 작업합니다.
3. 사용자 설정에 SSH 공개 키를 등록하고 프로젝트를 만듭니다.

```bash
git clone ssh://git@gitlab.example.com:2222/<그룹>/<프로젝트>.git
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 운영

| 작업       | 명령·방법                                                                                                  |
|------------|------------------------------------------------------------------------------------------------------------|
| 상태 확인  | `docker exec gitlab gitlab-ctl status`                                                                     |
| 설정 반영  | `/srv/gitlab/config/gitlab.rb` 수정 후 `docker exec gitlab gitlab-ctl reconfigure`                         |
| 백업       | `docker exec -t gitlab gitlab-backup create` + `/etc/gitlab`의 `gitlab.rb`·`gitlab-secrets.json` 별도 보관 |
| 업그레이드 | 공식 업그레이드 경로를 따라 판을 단계적으로 올림 (중간 판 건너뛰기 주의)                                   |
| 상태 점검  | `docker exec gitlab gitlab-rake gitlab:check SANITIZE=true`                                                |

`gitlab-secrets.json`이 없으면 백업을 복원해도 암호화된 값(CI 변수 등)을 읽지 못하므로 백업과 함께 보관합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용     | 명령                                                                               | 기대 결과                     |
|------|---------------|------------------------------------------------------------------------------------|-------------------------------|
| 1    | 컨테이너 상태 | `docker ps --filter name=gitlab`                                                   | `(healthy)`                   |
| 2    | 서비스 상태   | `docker exec gitlab gitlab-ctl status`                                             | 모든 서비스 `run:`            |
| 3    | 웹 응답       | `curl -s -o /dev/null -w '%{http_code}\n' http://gitlab.example.com/users/sign_in` | `200`                         |
| 4    | SSH clone     | `ssh -T -p 2222 git@gitlab.example.com`                                            | `Welcome to GitLab, @사용자!` |
| 5    | 점검 작업     | `gitlab-rake gitlab:check`                                                         | 실패 항목 없음                |
| 6    | 백업          | `gitlab-backup create` 후 백업 파일 확인                                           | 백업 tar 파일 생성            |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                            | 원인                         | 해결 방법                                                                               |
|---------------------------------|------------------------------|-----------------------------------------------------------------------------------------|
| 웹 접속 시 502                  | 기동 중, 메모리 부족         | `docker logs gitlab`, 메모리·스왑 확인 (2절)                                            |
| 초기 비밀번호 파일이 없음       | 24시간 뒤 재시작으로 삭제됨  | `docker exec -it gitlab gitlab-rake "gitlab:password:reset"`(사용자 이름 입력)로 재설정 |
| clone 주소의 호스트·포트가 틀림 | `external_url`·SSH 포트 설정 | `gitlab.rb` 수정 후 `gitlab-ctl reconfigure`                                            |
| 포트 22 충돌로 컨테이너가 안 뜸 | 호스트 sshd가 22 사용        | 다른 포트로 공개 (3절)                                                                  |
| 복원 뒤 CI 변수 오류            | `gitlab-secrets.json` 누락   | 원래 서버의 secrets 파일 복원                                                           |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [GitLab CI/CD](./gitlab_ci.md) — `.gitlab-ci.yml`, Runner
- [Git 가이드](./git_guide.md) — Git 자체 사용법
- [Docker Compose](../containers/docker_compose.md) — 같은 설치를 compose.yaml로 관리

---

## 참고 자료

- GitLab Docs: [Install GitLab in a Docker container](https://docs.gitlab.com/install/docker/installation/) — ★★★☆☆
- GitLab Docs: [Installation requirements](https://docs.gitlab.com/install/requirements/) — ★★★☆☆
- Docker Hub: [gitlab/gitlab-ce tags](https://hub.docker.com/r/gitlab/gitlab-ce/tags) — 19.5.8 확인 2026-11-23 — ★★★☆☆

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
