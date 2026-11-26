# Jenkins 설치 가이드
<!-- reference: _reference/jenkins_official_notes.md -->

- 기준 판: Jenkins 2.580.3 LTS (2026-11-25 출시, 2026-11-26 확인), Java 21
- 예제 시험: 2026-11-26, `jenkins/jenkins:2.580.3-jdk21` 기반 이미지에 플러그인을 미리 설치하고 JCasC로 관리자·권한·Pipeline 작업을 만든 뒤 REST API로 빌드 3회 실행, `JENKINS_HOME` 백업을 새 볼륨 2개에 복원(`master.key` 유무 비교)해 확인. 2~3절 패키지 설치, nginx 앞단, 에이전트 연결은 시험하지 않았음

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치)                                      |
| [4. 초기 설정](#4-초기-설정) / [5. 기본 사용법](#5-기본-사용법) / [6. Pipeline 예시](#6-pipeline-예시)                              |
| [7. Docker로 구성](#7-docker로-구성) / [8. 플러그인 미리 설치와 JCasC](#8-플러그인-미리-설치와-jcasc)                               |
| [9. 백업과 복원](#9-백업과-복원) / [10. 업그레이드](#10-업그레이드) / [11. 실무 팁](#11-실무-팁) / [12. 트러블슈팅](#12-트러블슈팅) |

---

## 1. 개요

### 판 고르기

| 계열         | 주기       | 2026-11 기준         | 쓰는 곳      |
|--------------|------------|----------------------|--------------|
| LTS          | 약 4주마다 | 2.580.3 (2026-11-25) | 운영 서버    |
| 주간(Weekly) | 매주       | -                    | 새 기능 시험 |

- Docker 이미지 `jenkins/jenkins`의 `latest` 태그는 주간판입니다. 운영은 `lts-jdk21` 또는 판을 고정한 `2.580.3-jdk21`을 씁니다.
- LTS 2.580.x 직전은 2.568.3(2026-09-02)입니다. LTS는 기준판(예: 2.580)을 정해 `.1`·`.2`·`.3` 수정판을 냅니다.

| Java | 지원 시작 LTS           | 지원 끝(예정) |
|------|-------------------------|---------------|
| 25   | 2.541.1 (2026-01)       | 2029-09       |
| 21   | 2.479.1 (2024-10)       | 2027-09       |
| 17   | 지원 끝(마지막 2.541.3) | -             |

- 2.555.1(2026-04-15)부터 Java 21 이상이 필요합니다. Java 17로는 기동하지 않습니다.

### 시스템 요구사항

| 항목   | 최소     | 권장           |
|--------|----------|----------------|
| CPU    | 1 core   | 4 core 이상    |
| RAM    | 256 MB   | 4 GB 이상      |
| 디스크 | 1 GB     | SSD 50 GB 이상 |
| JDK    | JDK 21+  | JDK 21/25      |
| 포트   | 8080/tcp | 8080/tcp       |

### Jenkins vs GitHub Actions 비교

| 항목       | Jenkins                       | GitHub Actions                   |
|------------|-------------------------------|----------------------------------|
| 호스팅     | 자체 서버                     | GitHub 관리형                    |
| 비용       | 서버 비용만                   | 무료 (공개) / 분당 과금 (비공개) |
| 플러그인   | 1,800+ 플러그인               | Marketplace Actions              |
| 온프레미스 | ✅                            | Self-hosted runner 필요          |
| 권장 상황  | 온프레미스, 복잡한 파이프라인 | GitHub 연동, 클라우드 네이티브   |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. JDK 설치

```bash
sudo apt update
sudo apt install fontconfig openjdk-21-jre -y
java -version
```

### 2-2. Jenkins 공식 저장소 추가

```bash
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
    https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key

echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] \
    https://pkg.jenkins.io/debian-stable binary/" \
    | sudo tee /etc/apt/sources.list.d/jenkins.list

sudo apt update
sudo apt install jenkins -y
sudo systemctl enable --now jenkins
```

### 2-3. 설치 확인

```bash
sudo systemctl status jenkins --no-pager | head -5
# 접속: http://SERVER_IP:8080
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. JDK 설치

```bash
sudo dnf install fontconfig java-21-openjdk -y
java -version
```

### 3-2. Jenkins 공식 저장소 추가

```bash
# 저장소 파일의 gpgkey 항목으로 서명 키를 가져오므로 별도 rpm --import가 필요 없음
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/rpm-stable/jenkins.repo

sudo dnf install jenkins -y
sudo systemctl enable --now jenkins
```

### 3-3. 방화벽 설정

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 설정

### 4-1. 초기 관리자 패스워드 확인

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### 4-2. 웹 UI 초기 설정

```
1. http://SERVER_IP:8080 접속
2. 초기 패스워드 입력
3. "Install suggested plugins" 선택
4. 관리자 계정 생성
5. Jenkins URL 설정
```

### 4-3. nginx 리버스 프록시 설정 (선택)

```nginx
# /etc/nginx/sites-available/jenkins
server {
    listen 80;
    server_name jenkins.example.com;

    location / {
        proxy_pass         http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 90s;
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 사용법

### 주요 개념

| 개념       | 설명                                   |
|------------|----------------------------------------|
| Job        | 빌드/배포 작업 단위                    |
| Pipeline   | 코드로 정의한 CI/CD 흐름 (Jenkinsfile) |
| Stage      | Pipeline의 단계 (Build, Test, Deploy)  |
| Agent      | 빌드를 실행하는 노드                   |
| Credential | 패스워드, SSH 키 등 민감 정보 저장소   |

### Credential 등록

```
Jenkins → Manage Jenkins → Credentials → System → Global credentials
→ Add Credentials
  - Kind: Username with password / SSH Username with private key
  - ID: my-git-cred (파이프라인에서 참조할 ID)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Pipeline 예시

### 기본 Declarative Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        APP_NAME = 'myapp'
        DOCKER_IMAGE = "myregistry/${APP_NAME}:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'my-git-cred',
                    url: 'https://github.com/example/myapp.git'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm ${DOCKER_IMAGE} npm test'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'registry-cred',
                    usernameVariable: 'REGISTRY_USER',
                    passwordVariable: 'REGISTRY_PASS'
                )]) {
                    sh '''
                        printf '%s' "$REGISTRY_PASS" | docker login -u "$REGISTRY_USER" --password-stdin myregistry
                        docker push ${DOCKER_IMAGE}
                    '''
                }
                sh 'docker compose -f /opt/myapp/compose.yaml up -d --no-deps app'
            }
        }
    }

    post {
        success { echo "Build #${BUILD_NUMBER} succeeded" }
        failure { echo "Build #${BUILD_NUMBER} failed" }
        always  { sh 'docker image prune -f' }
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Docker로 구성

```yaml
# compose.yaml
services:
  jenkins:
    image: jenkins/jenkins:2.580.3-jdk21   # 판 고정. lts-jdk21은 새 LTS로 바뀜
    ports:
      - "8080:8080"
      - "50000:50000"   # 인바운드 에이전트용(WebSocket 에이전트만 쓰면 불필요)
    volumes:
      - jenkins_home:/var/jenkins_home
    environment:
      JAVA_OPTS: "-Xmx1g"
    restart: unless-stopped

volumes:
  jenkins_home:
```

```bash
docker compose up -d
docker compose logs -f jenkins | grep -m1 "fully up and running"

# 초기 패스워드 확인 (설치 마법사를 쓸 때만 생김)
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

- 공식 이미지에는 Docker CLI가 없습니다. 빌드에서 Docker를 쓰려면 공식 문서의 Docker-in-Docker(`docker:dind` 사이드카, TLS) 구성이나 Docker를 가진 별도 에이전트를 씁니다.
- 호스트 `/var/run/docker.sock`을 넘기는 방식은 Jenkins가 호스트 Docker 전체(사실상 root)를 제어하게 됩니다. 공식 설치 문서는 이 방식을 안내하지 않습니다.
- 시험: 기동 시작부터 "Jenkins is fully up and running"까지 수 초였고, Java는 21.0.13이었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 플러그인 미리 설치와 JCasC

설치 마법사와 화면 설정 대신 이미지와 YAML로 Jenkins를 만들면 같은 서버를 다시 만들 수 있습니다.

```text
jenkins-image/
├── Dockerfile
├── plugins.txt     설치할 플러그인 목록
└── casc.yaml       Jenkins 설정(JCasC)
```

```dockerfile
FROM jenkins/jenkins:2.580.3-jdk21
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc.yaml
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
COPY --chown=jenkins:jenkins casc.yaml /var/jenkins_home/casc.yaml
```

```text
# plugins.txt (이름 또는 이름:판)
workflow-aggregator
configuration-as-code
job-dsl
git
```

```yaml
# casc.yaml
jenkins:
  systemMessage: "Configured by JCasC"
  numExecutors: 2
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${ADMIN_PW}"          # 컨테이너 환경 변수에서 읽음
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false
unclassified:
  location:
    url: "https://jenkins.example.com/"
jobs:
  - script: |
      pipelineJob('hello') {
        definition {
          cps {
            sandbox(true)
            script('''
              pipeline {
                agent any
                parameters { string(name: 'WHO', defaultValue: 'world') }
                stages {
                  stage('Build') {
                    steps {
                      sh 'echo build ^${BUILD_NUMBER}'
                      writeFile file: 'out.txt', text: "hello ^${params.WHO}"
                      archiveArtifacts artifacts: 'out.txt'
                    }
                  }
                }
              }
            '''.stripIndent())
          }
        }
      }
```

```bash
docker build -t my-jenkins:2.580.3 jenkins-image/
docker run -d --name jenkins -p 8080:8080 -v jenkins_home:/var/jenkins_home \
  --env-file jenkins.env my-jenkins:2.580.3     # jenkins.env에 ADMIN_PW=... (권한 600, 저장소에 넣지 않음)
```

시험 결과(2.580.3):

| 확인                                   | 결과                                                                                         |
|----------------------------------------|----------------------------------------------------------------------------------------------|
| 플러그인                               | 4개 지정 → 의존성 포함 63개 설치(`configuration-as-code` 2150.v9cb_6a_756737e, `git` 5.11.0) |
| 설치 마법사                            | 건너뜀, `initialAdminPassword` 파일 없음                                                     |
| 익명 / 관리자 / 틀린 비밀번호 API 호출 | 403 / 200 / 401                                                                              |
| `jobs:`(Job DSL)                       | `hello` Pipeline 작업 생성                                                                   |
| 설정 다시 읽기                         | `POST /configuration-as-code/reload`(crumb 필요)                                             |
| 현재 설정 내보내기                     | `POST /configuration-as-code/export`                                                         |

- JCasC는 YAML 안의 `${이름}`을 환경 변수로 바꿉니다. Pipeline 스크립트 안의 `${BUILD_NUMBER}`·`${params.WHO}`도 바뀌어 빈 값이 됩니다. 시험에서 이스케이프 없이 넣자 저장된 스크립트에서 변수가 모두 지워졌고, `^${...}`로 쓰자 그대로 남아 `build 4`, `hello world`가 출력되었습니다.
- Pipeline 스크립트가 길면 YAML에 넣지 말고 `cpsScm`으로 저장소의 `Jenkinsfile`을 가리키게 합니다. 이스케이프 문제도 피할 수 있습니다.
- 비밀번호·토큰은 YAML에 쓰지 않고 환경 변수나 비밀 파일(Docker secret 등)로 넘깁니다.
- 내보내기 결과는 지금 설정을 YAML로 옮길 때 출발점으로 씁니다. 그대로 다시 넣으면 오류가 나는 항목도 있어 필요한 부분만 골라 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 백업과 복원

모든 상태는 `JENKINS_HOME`(컨테이너는 `/var/jenkins_home`)에 있습니다.

| 대상                            | 백업  | 이유                                                                             |
|---------------------------------|-------|----------------------------------------------------------------------------------|
| `*.xml`, `jobs/`, `users/`      | 함    | 설정, 작업 정의·빌드 기록, 사용자                                                |
| `plugins/*.jpi`                 | 함    | 같은 판으로 되돌리기 위해. 풀린 `plugins/<이름>/` 폴더는 재시작 때 다시 만들어짐 |
| `secrets/` (`master.key` 제외)  | 함    | 암호화된 비밀값(`hudson.util.Secret` 등)                                         |
| `secrets/master.key`            | 따로  | 공식 문서: 백업에 넣지 말고 안전한 곳에 따로 보관                                |
| `war/`, `caches/`, `workspace/` | 안 함 | 다시 만들어짐                                                                    |
| `builds/archive`                | 선택  | 산출물을 오래 보관해야 할 때만(크기 큼)                                          |

```bash
# 컨테이너에서 백업 (master.key는 따로)
docker exec jenkins sh -c 'cd /var/jenkins_home && tar \
  --exclude=./war --exclude=./workspace --exclude=./caches \
  --exclude=./secrets/master.key -czf /tmp/jenkins-home.tgz .'
docker cp jenkins:/tmp/jenkins-home.tgz ./jenkins-home-$(date +%F).tgz
docker cp jenkins:/var/jenkins_home/secrets/master.key ./master.key   # 별도 보관소로 옮기고 권한 600
```

시험 결과(작업 1개, 빌드 4회, 플러그인 63개):

| 항목                              | 결과                                                                                                                    |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `JENKINS_HOME` 크기               | 약 211MB, 위 제외 규칙으로 만든 tar.gz 약 111MB(대부분 플러그인)                                                        |
| 새 볼륨에 복원, `master.key` 없음 | 기동은 됨, 빌드 기록 4개 복원. 로그에 `identity.key.enc is corrupted` SEVERE와 `BadPaddingException`, 식별 키 새로 생성 |
| 새 볼륨에 복원, `master.key` 함께 | 오류 없이 기동, 빌드 기록 4개 복원                                                                                      |

- `master.key`가 없으면 저장된 자격 증명·비밀값을 풀 수 없습니다. 시험에서는 인스턴스 식별 키가 깨진 것으로 확인했습니다. 복원할 때는 tar와 `master.key`를 함께 씁니다.
- 백업 파일과 `master.key`를 같은 곳에 두면 백업이 유출될 때 비밀값도 함께 풀립니다.
- 복원 뒤 Jenkins를 띄우기 전에 파일 소유자를 컨테이너 사용자(UID 1000)로 맞춥니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 업그레이드

1. 9절대로 백업합니다(`master.key` 포함 확인).
2. LTS 변경 기록(changelog-stable)과 업그레이드 안내에서 건너뛰는 판 사이의 주의 사항을 읽습니다.
3. 이미지 태그를 다음 LTS로 바꾸고 다시 만듭니다. 패키지 설치는 `apt upgrade jenkins`·`dnf upgrade jenkins`.
4. 기동 뒤 `Manage Jenkins`의 경고, 플러그인 업데이트, 시스템 로그를 확인합니다.
5. 플러그인은 스테이징에서 먼저 올려 보고, `plugins.txt`에 판을 고정해 운영과 맞춥니다.

- Java 판 요구가 바뀌는 LTS(예: 2.555.1의 Java 21 요구)는 Java부터 올립니다.
- 이 절의 판 올리기는 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 실무 팁

### Tip 1: 빌드 이력 보존 기간 설정

```groovy
// Jenkinsfile
options {
    buildDiscarder(logRotator(numToKeepStr: '30', daysToKeepStr: '90'))
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
}
```

### Tip 2: 공유 라이브러리 (Shared Library)

반복되는 파이프라인 코드를 라이브러리로 분리합니다.

```
Jenkins → Manage Jenkins → System → Global Pipeline Libraries
→ Name: my-shared-lib
→ Source: Git repository URL
```

```groovy
// Jenkinsfile에서 사용
@Library('my-shared-lib') _
deployToK8s(image: 'myapp:latest', namespace: 'prod')
```

### Tip 3: 에이전트 분리 (Controller/Agent)

빌드 부하를 Controller에서 분리합니다.

```
Jenkins → Manage Jenkins → Nodes → New Node
→ Permanent Agent
→ Remote root directory: /home/jenkins
→ Launch method: SSH
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 트러블슈팅

| 증상                                    | 원인                                    | 해결 방법                                                              |
|-----------------------------------------|-----------------------------------------|------------------------------------------------------------------------|
| 웹 UI 접속 불가                         | 서비스 미실행 또는 포트 차단            | `systemctl status jenkins`, 방화벽 확인                                |
| 플러그인 설치 실패                      | 네트워크 또는 프록시 문제               | Manage Jenkins → Plugin Manager → Advanced → 프록시 설정               |
| 빌드 `Permission denied`                | jenkins 사용자 권한 부족                | `usermod -aG docker jenkins` 후 재시작                                 |
| `OutOfMemoryError`                      | JVM 힙 부족                             | `systemctl edit jenkins`로 `JAVA_OPTS` 조정                            |
| Git checkout 실패                       | Credential 오류                         | Credential ID 확인, 토큰 만료 여부 확인                                |
| Java 17에서 기동 안 됨                  | 2.555.1부터 Java 21 이상 필요           | Java 21·25로 올림                                                      |
| JCasC Pipeline 변수가 빈 값             | YAML의 `${...}`를 환경 변수로 치환      | `^${...}`로 이스케이프, 또는 `cpsScm`으로 `Jenkinsfile` 사용           |
| `buildWithParameters` 400               | 선언형 `parameters`는 첫 실행 뒤 등록됨 | 처음 한 번 `/build`로 실행                                             |
| API POST 403                            | CSRF crumb 없음                         | `/crumbIssuer/api/json`의 crumb를 같은 세션으로 보내거나 API 토큰 사용 |
| 복원 뒤 `identity.key.enc is corrupted` | `master.key` 없이 복원                  | 백업 때 따로 보관한 `master.key`를 `secrets/`에 넣고 재기동            |

```bash
# 로그 확인
sudo journalctl -u jenkins -f
# systemd 기반 패키지는 로그를 systemd-journald로 보내며 별도 jenkins.log 파일을 만들지 않음
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Jenkins Documentation: [jenkins.io/doc](https://www.jenkins.io/doc/) — ★★★☆☆
- Jenkins Pipeline: [jenkins.io/doc/book/pipeline](https://www.jenkins.io/doc/book/pipeline/) — ★★★☆☆
- Jenkins Linux 설치: [jenkins.io/doc/book/installing/linux](https://www.jenkins.io/doc/book/installing/linux/) — ★★★☆☆
- Jenkins systemd 서비스 관리: [jenkins.io/doc/book/system-administration/systemd-services](https://www.jenkins.io/doc/book/system-administration/systemd-services/) — ★★★☆☆
- Jenkins Docker 설치: [jenkins.io/doc/book/installing/docker](https://www.jenkins.io/doc/book/installing/docker/) · [jenkinsci/docker README](https://github.com/jenkinsci/docker/blob/master/README.md) — ★★★☆☆
- Configuration as Code: [jenkins.io/doc/book/managing/casc](https://www.jenkins.io/doc/book/managing/casc/) — ★★★☆☆
- 백업: [jenkins.io/doc/book/system-administration/backing-up](https://www.jenkins.io/doc/book/system-administration/backing-up/) — ★★★☆☆
- Java 지원 정책: [jenkins.io/doc/book/platform-information/support-policy-java](https://www.jenkins.io/doc/book/platform-information/support-policy-java/) · [LTS 변경 기록](https://www.jenkins.io/changelog-stable/) — ★★★☆☆
- [jenkins_pipeline.md](./jenkins_pipeline.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
