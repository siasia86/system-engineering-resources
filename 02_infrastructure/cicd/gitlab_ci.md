# GitLab CI/CD
<!-- reference: _reference/gitlab_ci_variables_official_notes.md -->
<!-- reference: _reference/gitlab_official_notes.md -->

GitLab CI/CD는 저장소 루트의 `.gitlab-ci.yml` 파일에 정의한 Pipeline을 GitLab Runner가 실행하는 구조입니다.
이 문서는 시스템 엔지니어가 Pipeline을 읽고, 고치고, Runner를 운영할 때 필요한 문법·실행 규칙·점검 기준을 정리합니다.

- 기준 판: GitLab 19.6.2, GitLab Runner 19.6.1 (2026-11-26 확인)
- 예제 시험: 2026-11-26, `gitlab/gitlab-runner:latest`(19.6.1) 컨테이너에서 명령 목록, `register` 옵션, `exec` 명령 유무, `config.toml` 검사(`lint`)를 확인. GitLab 서버에 Runner를 등록해 Pipeline을 실행하지는 않았음

## 목차

| 섹션                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 구성 요소](#2-구성-요소) / [3. 기본 문법](#3-기본-문법) / [4. 실행 조건 rules](#4-실행-조건-rules) |
| [5. 순서와 의존성](#5-순서와-의존성) / [6. 캐시와 아티팩트](#6-캐시와-아티팩트) / [7. 재사용](#7-재사용)                    |
| [8. Runner 설치와 등록](#8-runner-설치와-등록) / [9. 컨테이너 이미지 빌드](#9-컨테이너-이미지-빌드)                         |
| [10. 변수와 보안](#10-변수와-보안) / [11. 검증과 문제 해결](#11-검증과-문제-해결)                                           |

---

## 1. 개요

GitLab CI/CD는 GitLab에 내장된 CI/CD(지속적 통합·지속적 배포) 기능입니다. 별도 CI 서버 없이 저장소에 YAML 파일을 두면 push·Merge Request·tag·일정 같은 사건마다 Pipeline이 만들어집니다.

| 비교 항목 | GitLab CI/CD                         | GitHub Actions                     | Jenkins                 |
|-----------|--------------------------------------|------------------------------------|-------------------------|
| 정의 파일 | `.gitlab-ci.yml` (저장소 루트)       | `.github/workflows/*.yml`          | `Jenkinsfile` (Groovy)  |
| 실행 단위 | Pipeline → Stage → Job               | Workflow → Job → Step              | Pipeline → Stage → Step |
| 실행기    | GitLab Runner                        | GitHub-hosted / self-hosted runner | Agent(Node)             |
| 재사용    | `include`, `extends`, CI/CD 컴포넌트 | 재사용 워크플로우, Action          | Shared Library          |

같은 저장소의 [GitHub Actions](./github_actions.md), [Jenkins Pipeline](./jenkins_pipeline.md) 문서와 개념을 대응해 보면 이해가 빠릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 구성 요소

```text
 push / MR / tag / schedule
            |
            v
 +---------------------+        +---------------------------+
 | GitLab              |  poll  | GitLab Runner             |
 |  - .gitlab-ci.yml   |<-------|  - config.toml            |
 |  - Pipeline         |        |  - executor (docker, k8s, |
 |    Stage > Job      |------->|    shell, ...)            |
 |  - Variables        |  job   |  - cache                  |
 +---------------------+        +---------------------------+
            ^                              |
            |      logs, artifacts         |
            +------------------------------+
```

| 용어     | 설명                                                                                   |
|----------|----------------------------------------------------------------------------------------|
| Pipeline | 한 번의 실행 전체. Stage와 Job의 묶음입니다                                            |
| Stage    | Job을 묶는 단계. 같은 Stage의 Job은 병렬로 실행되고 Stage는 나열한 순서대로 진행합니다 |
| Job      | 실제 명령(`script`)을 실행하는 최소 단위입니다                                         |
| Runner   | GitLab에서 Job을 받아 실행하는 에이전트 프로그램입니다                                 |
| Executor | Runner가 Job을 실행하는 방식(Docker 컨테이너, Kubernetes Pod, 호스트 셸 등)입니다      |
| Artifact | Job 결과 파일. GitLab에 저장되어 다음 Stage와 다운로드에 쓰입니다                      |
| Cache    | 의존성 같은 재사용 파일. Runner 쪽에 저장되며 항상 있다고 보장되지 않습니다            |

Stage를 따로 정하지 않으면 기본값은 `.pre`, `build`, `test`, `deploy`, `.post`이고 `stage`가 없는 Job은 `test`에 들어갑니다. `.pre`와 `.post` Job만 있는 Pipeline은 실행되지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 문법

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

default:
  image: python:3.12-slim       # Job이 image를 정하지 않으면 사용
  retry: 1                      # 0, 1, 2만 허용
  timeout: 30 minutes

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

build:
  stage: build
  script:
    - pip install -r requirements.txt
    - python -m compileall src

unit-test:
  stage: test
  script:
    - pip install -r requirements.txt pytest
    - pytest -q

deploy-prod:
  stage: deploy
  script:
    - ./deploy.sh production
  environment:
    name: production
    url: https://app.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

| 키워드                         | 위치     | 설명                                                                               |
|--------------------------------|----------|------------------------------------------------------------------------------------|
| `stages`                       | 전역     | Stage 이름과 순서                                                                  |
| `default`                      | 전역     | Job 키워드의 기본값. Job에 같은 키워드가 있으면 Job 값이 대신 쓰입니다(병합 안 함) |
| `variables`                    | 전역/Job | 환경변수. Job 값이 전역 값을 덮어씁니다                                            |
| `workflow`                     | 전역     | Pipeline 자체를 만들지 결정                                                        |
| `include`                      | 전역     | 다른 YAML 파일 가져오기                                                            |
| `script`                       | Job      | 실행할 명령. trigger Job을 빼고 필수입니다                                         |
| `before_script`/`after_script` | Job      | `script` 앞뒤에 실행할 명령                                                        |
| `image`/`services`             | Job      | Job 컨테이너 이미지와 함께 띄울 보조 컨테이너(DB 등)                               |
| `tags`                         | Job      | 이 태그를 모두 가진 Runner만 Job을 가져갑니다(대소문자 구분)                       |
| `timeout`                      | Job      | Job 제한 시간. Runner 최대값은 넘을 수 없습니다                                    |
| `environment`                  | Job      | 배포 대상 환경 이름·URL. 배포 이력이 환경별로 남습니다                             |

🟡 `default`의 `image`, `services`, `tags`는 Job에서 다시 지정하면 병합되지 않고 통째로 바뀝니다. `tags: []`처럼 빈 배열을 주면 상속된 태그가 지워집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 실행 조건 rules

`rules`는 Job을 Pipeline에 넣을지 Pipeline 생성 시점에 위에서부터 차례로 평가합니다. 처음 맞는 규칙에서 평가가 끝나고, 어느 규칙도 맞지 않으면 Job은 추가되지 않습니다.

| 하위 키         | 설명                                                       |
|-----------------|------------------------------------------------------------|
| `if`            | CI/CD 변수 식. `==`, `!=`, `=~`(정규식), `&&`, `\|\|` 사용 |
| `changes`       | 지정 경로·glob 중 하나라도 바뀌면 참                       |
| `exists`        | 지정 파일·디렉터리가 저장소에 있으면 참                    |
| `when`          | 규칙이 맞을 때 실행 방식. Job 수준 `when`보다 우선합니다   |
| `allow_failure` | 규칙이 맞을 때만 Job의 `allow_failure`를 덮어씁니다        |
| `variables`     | 규칙이 맞을 때만 적용할 변수                               |

`when` 값은 다음과 같습니다.

| 값           | 의미                                                    |
|--------------|---------------------------------------------------------|
| `on_success` | 기본값. 앞 Stage Job이 모두 성공했을 때 실행            |
| `on_failure` | 앞 Stage Job이 하나라도 실패했을 때 실행                |
| `always`     | 앞 Stage 결과와 관계없이 실행                           |
| `manual`     | 사람이 UI에서 실행 버튼을 눌러야 실행                   |
| `delayed`    | `start_in` 시간만큼 기다린 뒤 실행(1초~1주)             |
| `never`      | 실행하지 않음. `rules`·`workflow:rules`에서만 사용 가능 |

```yaml
lint-terraform:
  script:
    - terraform fmt -check -recursive
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - "terraform/**/*.tf"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### workflow:rules로 중복 Pipeline 막기

Merge Request가 열린 브랜치에 push하면 브랜치 Pipeline과 MR Pipeline이 함께 만들어질 수 있습니다. 공식 문서의 다음 패턴은 MR이 열려 있으면 MR Pipeline만, 아니면 브랜치 Pipeline만 만듭니다.

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

`workflow:rules`의 `when`에는 `always`와 `never`만 쓸 수 있고, 맞는 규칙이 없으면 Pipeline이 만들어지지 않습니다. 위 예시는 tag Pipeline을 만들지 않으므로 tag 배포가 필요하면 `- if: $CI_COMMIT_TAG` 규칙을 추가합니다.

🟡 `only`/`except`는 예전 문법입니다. 새 설정은 `rules`로 쓰고, 한 Job 안에서 두 방식을 섞지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 순서와 의존성

기본 실행 순서는 Stage 순서입니다. `needs`를 쓰면 Stage와 관계없이 지정한 Job이 끝나는 즉시 시작하는 DAG(방향 비순환 그래프) 실행이 됩니다.

```yaml
build-api:
  stage: build
  script: [make api]

build-web:
  stage: build
  script: [make web]

test-api:
  stage: test
  needs: ["build-api"]      # build-web을 기다리지 않음
  script: [make test-api]

check-docs:
  stage: test
  needs: []                 # Pipeline 생성 즉시 시작
  script: [make docs-lint]
```

| 키워드            | 설명                                                                                     |
|-------------------|------------------------------------------------------------------------------------------|
| `needs`           | 먼저 끝나야 하는 Job 목록. GitLab.com 최대 50개(자체 관리형은 기본 50, 관리자 변경 가능) |
| `needs:artifacts` | `false`면 그 Job의 아티팩트를 내려받지 않음                                              |
| `dependencies`    | 아티팩트를 받을 앞 Job 제한. 같은 Job에서 `needs`와 함께 쓰지 않습니다                   |
| `parallel`        | 같은 Job을 1~200개 복제 실행                                                             |
| `parallel:matrix` | 변수 조합별 Job 생성(조합 수 최대 200)                                                   |
| `resource_group`  | 같은 그룹 Job은 Pipeline이 달라도 한 번에 하나만 실행(배포 중복 방지)                    |
| `interruptible`   | 새 커밋이 오면 취소해도 되는 Job 표시. 자동 취소 설정이 켜져 있어야 동작                 |
| `trigger`         | 자식 Pipeline(`trigger:include`) 또는 다른 프로젝트 Pipeline 시작                        |

```yaml
deploy:
  stage: deploy
  resource_group: production   # 동시에 두 배포가 실행되지 않음
  script: [./deploy.sh]

test-matrix:
  parallel:
    matrix:
      - PYTHON: ["3.11", "3.12"]
        DB: ["postgres", "mysql"]
  image: python:${PYTHON}-slim
  script: [./run-tests.sh "$DB"]
```

`interruptible` Job을 실제로 취소하는 규칙은 `workflow:auto_cancel`로 정합니다.

```yaml
workflow:
  auto_cancel:
    on_new_commit: interruptible   # conservative(초기값) | interruptible | none
    on_job_failure: all            # all | none: Job 하나가 실패하면 나머지 취소
```

`trigger:strategy: mirror`를 주면 trigger Job이 하위 Pipeline의 상태를 그대로 따르고 다음 Stage는 하위 Pipeline이 끝날 때까지 기다립니다. 지정하지 않으면 하위 Pipeline이 만들어지는 순간 trigger Job은 성공으로 끝납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 캐시와 아티팩트

| 구분        | Cache                                  | Artifact                                        |
|-------------|----------------------------------------|-------------------------------------------------|
| 목적        | 의존성 재다운로드 줄이기(패키지 등)    | 빌드 결과를 다음 Stage로 넘기고 보관            |
| 저장 위치   | Runner 호스트(분산 캐시 설정 시 S3 등) | GitLab 서버                                     |
| 보장        | 없음. 없으면 다시 만들도록 작성        | Job 성공 시 업로드(만료 전까지 유지)            |
| 보관 기간   | Runner 정리 정책에 따름                | `expire_in`, 기본 30일(인스턴스 설정 따라 다름) |
| 프로젝트 간 | 공유 불가                              | API·`needs:project`로 가져오기 가능             |

```yaml
install:
  stage: build
  image: node:22-slim
  cache:
    key:
      files:
        - package-lock.json     # 잠금 파일이 바뀌면 새 캐시
    paths:
      - node_modules/
    policy: pull-push           # 기본값. 읽기만 하는 Job은 pull
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
    when: on_success
```

| `cache:policy` | 동작                                    |
|----------------|-----------------------------------------|
| `pull-push`    | 시작할 때 내려받고 끝날 때 올림(기본값) |
| `pull`         | 내려받기만 함. 테스트 Job에 적합        |
| `push`         | 올리기만 함. 캐시를 만드는 Job에 적합   |

🟡 비밀값이 들어간 파일(`.env`, kubeconfig)을 `artifacts:paths`에 넣지 않습니다. 아티팩트는 프로젝트 접근 권한이 있는 사용자가 내려받을 수 있습니다. 필요하면 `artifacts:access`로 다운로드 권한을 좁힙니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 재사용

| 방법                | 설명                                                               |
|---------------------|--------------------------------------------------------------------|
| `include:local`     | 같은 저장소의 다른 YAML 파일                                       |
| `include:project`   | 다른 프로젝트의 파일(공통 템플릿 저장소)                           |
| `include:remote`    | URL로 가져오기. `integrity`로 SHA256 검증 가능                     |
| `include:template`  | GitLab이 제공하는 템플릿                                           |
| `include:component` | CI/CD 컴포넌트(입력값 `inputs`을 받는 재사용 단위)                 |
| `extends`           | 다른 Job·숨김 Job(`.`으로 시작)의 설정을 상속. 키 단위로 깊게 병합 |
| YAML 앵커           | `&name`/`*name`/`<<:`. 같은 파일 안에서만 동작                     |

```yaml
include:
  - project: "platform/ci-templates"
    ref: "v1.4.0"                # 브랜치 대신 tag·커밋 고정 권장
    file: "/templates/python.yml"

.deploy-base:
  image: alpine:3.20
  before_script:
    - apk add --no-cache openssh-client
  resource_group: $CI_ENVIRONMENT_NAME

deploy-stg:
  extends: .deploy-base
  environment: { name: staging }
  script: [./deploy.sh staging]
```

CI/CD 컴포넌트는 입력값을 받는 재사용 단위입니다. 컴포넌트 파일 맨 위에 `spec:inputs`로 입력을 선언하고 `---` 아래에 Job을 둡니다.

```yaml
# 컴포넌트 저장소의 templates/python-test.yml
spec:
  inputs:
    stage:
      default: test
    python_version:
      default: "3.12"
---
python-test:
  stage: $[[ inputs.stage ]]
  image: python:$[[ inputs.python_version ]]-slim
  script: [pytest -q]
```

```yaml
# 사용하는 프로젝트의 .gitlab-ci.yml
include:
  - component: $CI_SERVER_FQDN/platform/ci-components/python-test@1.2.0
    inputs:
      python_version: "3.13"
```

- 컴포넌트 주소는 `<도메인>/<프로젝트 경로>/<컴포넌트 이름>@<판>` 형식이고, 판은 tag로 고정합니다.
- `include:inputs`는 GitLab 17.0에서 정식 기능이 되었고, 한 Pipeline의 include는 기본 150개까지입니다(공식 문서 확인 2026-11-26).
- 위 두 YAML은 공식 문법 예시를 옮긴 것이며 GitLab 서버에서 실행하지 않았습니다.

`extends`는 상속 단계를 최대 11단계까지 허용하지만 공식 문서는 3단계를 넘기지 않도록 권합니다. 공통 템플릿을 브랜치 이름으로 참조하면 템플릿 저장소의 변경이 모든 프로젝트에 바로 퍼지므로, 운영 Pipeline은 tag나 커밋으로 고정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Runner 설치와 등록

### 설치(Linux 패키지 저장소)

```bash
# Debian/Ubuntu: 스크립트를 내려받아 내용을 확인한 뒤 실행
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" -o script.deb.sh
less script.deb.sh
sudo bash script.deb.sh
sudo apt install gitlab-runner

# RHEL 계열
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh" -o script.rpm.sh
less script.rpm.sh
sudo bash script.rpm.sh
sudo dnf install gitlab-runner
```

### 등록

현재 등록 방식은 GitLab UI(프로젝트·그룹·인스턴스의 Runner 설정)에서 Runner를 먼저 만들고, 그때 받은 Runner 인증 토큰(`glrt-`로 시작)으로 등록하는 것입니다. 예전 등록 토큰(registration token) 방식은 지원 중단(deprecated) 상태이고 GitLab 20.0에서 없앨 예정입니다. Runner 19.6.1의 `register --help`에도 `--registration-token`이 "deprecated, use --token"으로 표시됩니다.

```bash
sudo gitlab-runner register --non-interactive \
  --url "https://gitlab.example.com" \
  --token "<RUNNER_AUTH_TOKEN>" \
  --executor "docker" \
  --docker-image "alpine:3.20" \
  --name "build-runner-01"

sudo gitlab-runner list        # 등록된 Runner 확인
sudo gitlab-runner verify      # GitLab과 연결 확인
sudo systemctl status gitlab-runner
```

설정 파일은 root로 실행하면 `/etc/gitlab-runner/config.toml`, 일반 사용자로 실행하면 `~/.gitlab-runner/config.toml`입니다.

```toml
concurrent = 4                 # 이 Runner 프로세스 전체 동시 Job 수 (0은 허용 안 됨)

[[runners]]
  name = "build-runner-01"
  url = "https://gitlab.example.com"
  executor = "docker"
  limit = 2                    # 이 [[runners]] 항목의 동시 Job 수 (0 = 제한 없음)
  [runners.docker]
    image = "alpine:3.20"
    privileged = false         # true는 컨테이너에 모든 capability를 줌
    volumes = ["/cache"]
```

### 컨테이너로 실행

Runner 자체를 컨테이너로 돌리고 설정 파일만 볼륨에 둘 수 있습니다.

```bash
# 등록 (config.toml이 볼륨에 만들어짐)
docker run --rm -it -v gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner:latest register

# 실행 (docker executor가 호스트 Docker로 Job 컨테이너를 만듦)
docker run -d --name gitlab-runner --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v gitlab-runner-config:/etc/gitlab-runner \
  gitlab/gitlab-runner:latest
```

- 설정을 바꾼 뒤에는 컨테이너를 다시 시작합니다. 컨테이너 안에서 `gitlab-runner restart`를 쓰면 새 프로세스가 하나 더 뜹니다(공식 문서).
- Docker 소켓을 넘기면 Runner 컨테이너가 호스트 Docker 전체를 제어할 수 있습니다. 신뢰하는 프로젝트의 Job만 받게 합니다.

### config.toml 검사

```bash
gitlab-runner lint     # 기본 설정 파일 경로를 검사하고 Runner는 시작하지 않음
```

- 시험(19.6.1): 정상 파일은 "Configuration file is valid.", `image = 5`처럼 형식이 틀리면 "toml: line 6 (last key "runners.docker.image"): incompatible types" 오류로 끝났습니다.
- 예전에 Job을 로컬에서 돌려 보던 `gitlab-runner exec`는 19.6.1에 없습니다("Command exec not found"). `.gitlab-ci.yml` 검사는 11절의 Pipeline editor·CI lint API를 씁니다.

### Executor 선택

| Executor          | 적합한 경우                                  | 비고                             |
|-------------------|----------------------------------------------|----------------------------------|
| Docker            | 일반 빌드·테스트. Job마다 깨끗한 컨테이너    | 오토스케일 없이 가장 무난한 선택 |
| Docker Autoscaler | 클라우드 VM을 필요할 때 늘리고 줄임          | fleeting 플러그인 사용           |
| Instance          | 호스트 전체 접근이 필요한 Job의 오토스케일   | fleeting 플러그인 사용           |
| Kubernetes        | 이미 운영 중인 클러스터에서 Job마다 Pod 생성 | 클라우드 네이티브 환경           |
| Shell             | 호스트에서 직접 명령 실행                    | 유지보수 모드. Job 간 격리 없음  |
| SSH·VirtualBox 등 | 기존 환경 유지                               | 유지보수 모드(보안 수정만 제공)  |

Docker Machine Executor는 지원 중단 상태이므로 새로 구성하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 컨테이너 이미지 빌드

GitLab Container Registry가 켜져 있으면 Job 안에서 `CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` 변수를 쓸 수 있습니다. `CI_REGISTRY_PASSWORD`는 Job이 실행되는 동안만 유효합니다.

Docker-in-Docker(dind)는 Job마다 별도 Docker 데몬을 서비스 컨테이너로 띄우는 방식이며 Runner에 `privileged = true`가 필요합니다.

```yaml
build-image:
  stage: build
  image: docker:24.0.5-cli
  services:
    - docker:24.0.5-dind
  variables:
    DOCKER_HOST: tcp://docker:2376
    DOCKER_TLS_CERTDIR: "/certs"
  tags:
    - tls-docker-runner        # privileged Runner에만 보내기
  script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
```

Runner 쪽에는 `[runners.docker]`에 `privileged = true`와 `volumes = ["/certs/client", "/cache"]`가 필요합니다. 위 이미지 판(24.0.5)은 공식 예시 값이며 실제 사용 시 현재 지원 판으로 바꿉니다.

| 방식                        | 장점                    | 주의                                             |
|-----------------------------|-------------------------|--------------------------------------------------|
| Docker-in-Docker            | Job별 독립 데몬         | privileged 필요. 전용 Runner·태그로 분리         |
| Docker 소켓 바인딩          | privileged 불필요, 빠름 | 호스트 Docker 전체 제어 가능. 컨테이너 탈출 위험 |
| Shell + docker 그룹         | 설정 단순               | `docker` 그룹 = 사실상 root 권한                 |
| BuildKit rootless / Buildah | 데몬 없이 빌드          | 이미지·설정 준비 필요                            |

Dockerfile 자체를 작게·안전하게 쓰는 방법은 [Dockerfile 작성과 이미지 빌드](../containers/dockerfile_best_practices.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 변수와 보안

변수의 저장 위치·Protected·Masked 속성 세부는 위 reference 노트에 정리되어 있습니다. 여기서는 Pipeline 작성 때 자주 쓰는 사전 정의 변수와 점검 항목만 다룹니다.

| 변수                   | 의미                                                         |
|------------------------|--------------------------------------------------------------|
| `CI_PIPELINE_SOURCE`   | Pipeline을 만든 사건(push, merge_request_event, schedule 등) |
| `CI_COMMIT_BRANCH`     | 브랜치 Pipeline의 브랜치 이름. MR·tag Pipeline에는 없음      |
| `CI_COMMIT_TAG`        | tag Pipeline의 tag 이름                                      |
| `CI_DEFAULT_BRANCH`    | 프로젝트 기본 브랜치 이름                                    |
| `CI_COMMIT_SHORT_SHA`  | 커밋 SHA 앞 8자                                              |
| `CI_MERGE_REQUEST_IID` | MR 번호(프로젝트 안에서 고유)                                |
| `CI_PROJECT_DIR`       | 저장소가 clone된 Job 작업 경로                               |
| `CI_JOB_TOKEN`         | Job 실행 중에만 유효한 API 인증 토큰                         |

보안 점검표:

- [ ] 비밀값은 `.gitlab-ci.yml`이 아니라 프로젝트·그룹 CI/CD 변수에 두고, 운영 배포 값은 Protected로 설정했는가
- [ ] Masked는 로그 노출만 줄인다는 점을 알고, `env`·`set -x`·디버그 로그로 값을 출력하지 않는가
- [ ] 운영 배포 Job은 보호 브랜치·tag에서만 실행되도록 `rules`와 `environment`를 지정했는가
- [ ] privileged Runner는 신뢰한 프로젝트 전용으로 두고 `tags`로 분리했는가
- [ ] Fork MR Pipeline이 부모 프로젝트 변수·Runner를 쓰는 조건을 검토했는가
- [ ] 클라우드 배포는 장기 접근 키 대신 OIDC(ID 토큰) 연동을 검토했는가

[⬆ 목차로 돌아가기](#목차)

---

## 11. 검증과 문제 해결

### 설정 검증

- UI: 프로젝트 → **Build** → **Pipeline editor** → **Validate** 탭에서 문법을 검사합니다. 기본 브랜치 push를 가정한 Pipeline 생성 시뮬레이션을 켜면 `needs`·`rules` 오류까지 찾을 수 있습니다.
- CLI: GitLab CLI `glab`의 `glab ci lint` 명령으로 검사할 수 있습니다.
- API: CI lint API 엔드포인트로 자동 검사에 붙일 수 있습니다.

```bash
# 프로젝트 문맥으로 검사 (include·변수 해석 포함). 토큰은 api 범위 필요
jq -n --rawfile c .gitlab-ci.yml '{content: $c, dry_run: true}' \
  | curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" --header "Content-Type: application/json" \
         --data @- "https://gitlab.example.com/api/v4/projects/<프로젝트 ID>/ci/lint" \
  | jq '{valid, errors, warnings}'
```

- `POST /projects/:id/ci/lint`는 `content`(필수)와 `dry_run`·`include_jobs`·`ref`를 받습니다. 저장소의 파일을 그대로 검사하는 `GET /projects/:id/ci/lint`도 있고, 19.6에서 이 GET 요청에 인증을 요구하는 설정(`ci_lint_api_require_authentication`)이 추가되었습니다(공식 문서 확인 2026-11-26, 실행하지 않음).

### 자주 만나는 증상

| 증상                                           | 확인할 것                                                                      |
|------------------------------------------------|--------------------------------------------------------------------------------|
| Pipeline이 아예 만들어지지 않음                | `workflow:rules`에 맞는 규칙이 있는지, 모든 Job이 `rules`로 빠지지 않았는지    |
| Job이 `pending`에서 멈춤                       | Job `tags`를 모두 가진 온라인 Runner가 있는지, Runner `concurrent`/`limit`     |
| 같은 커밋에 Pipeline이 두 개                   | 브랜치·MR Pipeline 중복. 4절 `workflow:rules` 패턴 적용                        |
| 다음 Job에서 파일이 없음                       | 캐시에 의존했는지. 결과물은 `artifacts`로 넘기고 `needs:artifacts` 확인        |
| 보호 변수 값이 비어 있음                       | 보호되지 않은 브랜치·tag에서 실행했는지                                        |
| dind에서 `Cannot connect to the Docker daemon` | Runner `privileged`, `DOCKER_HOST`, `DOCKER_TLS_CERTDIR`, `/certs/client` 볼륨 |
| 배포 Job이 동시에 두 번 실행                   | `resource_group` 지정 여부                                                     |

```bash
# Runner 쪽 확인
sudo gitlab-runner status
sudo journalctl -u gitlab-runner --since "30 min ago"
sudo gitlab-runner --debug run      # 서비스를 멈춘 상태에서 전경 실행해 상세 로그 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- GitLab CI/CD YAML 문법 참조: [docs.gitlab.com/ci/yaml](https://docs.gitlab.com/ci/yaml/) — ★★★☆☆ (확인일 2026-11-16)
- workflow:rules 예시: [docs.gitlab.com/ci/yaml/workflow](https://docs.gitlab.com/ci/yaml/workflow/) — ★★★☆☆ (확인일 2026-11-16)
- Merge request pipelines: [docs.gitlab.com/ci/pipelines/merge_request_pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/) — ★★★☆☆ (확인일 2026-11-16)
- 캐시: [docs.gitlab.com/ci/caching](https://docs.gitlab.com/ci/caching/) — ★★★☆☆ (확인일 2026-11-16)
- 사전 정의 변수: [docs.gitlab.com/ci/variables/predefined_variables](https://docs.gitlab.com/ci/variables/predefined_variables/) — ★★★☆☆ (확인일 2026-11-16)
- CI Lint: [docs.gitlab.com/ci/yaml/lint](https://docs.gitlab.com/ci/yaml/lint/) — ★★★☆☆ (확인일 2026-11-16)
- Runner 설치: [docs.gitlab.com/runner/install/linux-repository](https://docs.gitlab.com/runner/install/linux-repository/) — ★★★☆☆ (확인일 2026-11-16)
- Runner Executor: [docs.gitlab.com/runner/executors](https://docs.gitlab.com/runner/executors/) — ★★★☆☆ (확인일 2026-11-16)
- Runner 고급 설정(config.toml): [docs.gitlab.com/runner/configuration/advanced-configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/) — ★★★☆☆ (확인일 2026-11-16)
- Runner 자동 등록 예시: [docs.gitlab.com/tutorials/automate_runner_creation](https://docs.gitlab.com/tutorials/automate_runner_creation/) — ★★★☆☆ (확인일 2026-11-16)
- Docker로 이미지 빌드: [docs.gitlab.com/ci/docker/using_docker_build](https://docs.gitlab.com/ci/docker/using_docker_build/) — ★★★☆☆ (확인일 2026-11-16)
- Docker-in-Docker: [docs.gitlab.com/ci/docker/docker_in_docker](https://docs.gitlab.com/ci/docker/docker_in_docker/) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
