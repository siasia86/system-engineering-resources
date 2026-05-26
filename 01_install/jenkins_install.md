# Jenkins 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 설정](#4-초기-설정) / [5. 기본 사용법](#5-기본-사용법) / [6. Pipeline 예시](#6-pipeline-예시) |
| [7. Docker Compose로 구성](#7-docker-compose로-구성) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

### 시스템 요구사항

| 항목   | 최소     | 권장           |
|--------|----------|----------------|
| CPU    | 1 core   | 4 core 이상    |
| RAM    | 1 GB     | 4 GB 이상      |
| 디스크 | 10 GB    | SSD 50 GB 이상 |
| JDK    | JDK 17+  | JDK 21         |
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
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
    https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key

echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
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
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

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
                        docker login -u $REGISTRY_USER -p $REGISTRY_PASS myregistry
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

## 7. Docker Compose로 구성

```yaml
# compose.yaml
services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    ports:
      - "8080:8080"
      - "50000:50000"   # Agent 연결 포트
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock  # Docker in Docker
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    restart: unless-stopped

volumes:
  jenkins_home:
```

```bash
docker compose up -d

# 초기 패스워드 확인
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

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

## 9. 트러블슈팅

| 증상                     | 원인                         | 해결 방법                                                |
|--------------------------|------------------------------|----------------------------------------------------------|
| 웹 UI 접속 불가          | 서비스 미실행 또는 포트 차단 | `systemctl status jenkins`, 방화벽 확인                  |
| 플러그인 설치 실패       | 네트워크 또는 프록시 문제    | Manage Jenkins → Plugin Manager → Advanced → 프록시 설정 |
| 빌드 `Permission denied` | jenkins 사용자 권한 부족     | `usermod -aG docker jenkins` 후 재시작                   |
| `OutOfMemoryError`       | JVM 힙 부족                  | `/etc/default/jenkins` 에서 `JAVA_ARGS` 조정             |
| Git checkout 실패        | Credential 오류              | Credential ID 확인, 토큰 만료 여부 확인                  |

```bash
# 로그 확인
sudo journalctl -u jenkins -f
sudo tail -100 /var/log/jenkins/jenkins.log
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Jenkins Documentation: [jenkins.io/doc](https://www.jenkins.io/doc/) — ★★★☆☆
- Jenkins Pipeline: [jenkins.io/doc/book/pipeline](https://www.jenkins.io/doc/book/pipeline/) — ★★★☆☆
- [jenkins_pipeline.md](../12_tech_stack/jenkins_pipeline.md)

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

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
