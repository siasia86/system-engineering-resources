---
name: gitlab-official-notes
description: GitLab(자체 설치)의 판, Docker 설치 절차, 하드웨어 요구 사항, 초기 root 비밀번호의 공식 문서 기준 사실 정리.
tags:
  - git
  - gitlab
last_checked: 2026-11-23
sources:
  - https://docs.gitlab.com/install/docker/installation/
  - https://docs.gitlab.com/install/requirements/
  - https://hub.docker.com/r/gitlab/gitlab-ce/tags
---

# GitLab 공식 참조 노트

## 1. 공식 소스

| 소스                      | URL                                                  | 용도                         |
|---------------------------|------------------------------------------------------|------------------------------|
| Install with Docker       | https://docs.gitlab.com/install/docker/installation/ | 컨테이너 설치, 초기 비밀번호 |
| Installation requirements | https://docs.gitlab.com/install/requirements/        | 메모리·CPU 요구 사항         |
| gitlab-ce 이미지 태그     | https://hub.docker.com/r/gitlab/gitlab-ce/tags       | CE 판                        |

## 2. 검증된 사실 (2026-11-23)

| 항목               | 값                                                                                          | 출처             |
|--------------------|---------------------------------------------------------------------------------------------|------------------|
| CE 최신 이미지     | `gitlab/gitlab-ce:19.5.8-ce.0` (이전 계열 19.4.10)                                          | Docker Hub 태그  |
| 메모리             | 단일 노드 16 GB가 기준. 메모리 제약 환경 설정으로 8 GB에서도 운영 가능                      | requirements     |
| 스왑               | 가능하면 끔 (성능 저하)                                                                     | requirements     |
| Docker 실행        | `GITLAB_HOME`(예: `/srv/gitlab`) 아래 config·logs·data를 볼륨으로, `--shm-size 256m`        | Docker 설치 문서 |
| 초기 root 비밀번호 | `/etc/gitlab/initial_root_password`의 `Password:` 줄. 24시간 뒤 첫 재시작 때 파일 자동 삭제 | Docker 설치 문서 |
| 판 종류            | CE(`gitlab-ce`)와 EE(`gitlab-ee`) 이미지가 따로 있음                                        | Docker 설치 문서 |

## 3. 검증 기록

- 1차: docs.gitlab.com 설치·요구 사항 문서와 Docker Hub 태그에서 확인했습니다.
- 2차: Docker 설치 문서의 실행 명령(`--shm-size`, 볼륨, 비밀번호 확인 명령)을 요구 사항 문서와 함께 다시 대조했습니다. 단일 노드 권장 메모리(16 GB)에 못 미치는 작성 환경이라 컨테이너 실행 시험은 하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
