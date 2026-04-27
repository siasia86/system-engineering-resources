# Jenkins Pipeline

## 목차

| 단계   | 섹션                                                                                                                                                          |
|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기본   | [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. Pipeline 유형](#3-pipeline-유형)                               |
| 실전   | [4. Declarative Pipeline](#4-declarative-pipeline) / [5. Scripted Pipeline](#5-scripted-pipeline)                    |
| 고급   | [6. 공유 라이브러리](#6-공유-라이브러리) / [7. 에이전트/노드](#7-에이전트노드) / [8. 플러그인](#8-플러그인)          |
| 운영   | [9. 보안](#9-보안) / [10. 모니터링](#10-모니터링) / [11. Tips](#11-tips)                                                                                     |
| 확장   | [12. 멀티브랜치 Pipeline](#12-멀티브랜치-pipeline) / [13. Docker 빌드/ECR](#13-docker-빌드--ecr) / [14. 테스트 리포트/아티팩트](#14-테스트-리포트--아티팩트) |

---

## 1. 개요

Jenkins는 오픈소스 CI/CD 자동화 서버. **Jenkinsfile**로 빌드/테스트/배포 파이프라인을 코드로 정의합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                    Jenkins Pipeline Flow                     │
│                                                              │
│  SCM (Git) -> Checkout -> Build -> Test -> Deploy -> Notify  │
│                                                              │
│  Controller ──> Agent (Node) ──> Workspace ──> Steps         │
└──────────────────────────────────────────────────────────────┘
```

- SCM에서 코드를 Checkout → Build → Test → Deploy → Notify 순서로 실행
- Controller가 Agent(Node)에 작업을 위임하여 Workspace에서 Steps를 실행

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────┐        ┌──────────────────────────────┐
│ Jenkins         │        │ Agents                       │
│ Controller      │        │                              │
│                 │ JNLP/  │  ┌──────────┐ ┌──────────┐   │
│  - Job Mgmt     │ SSH    │  │ Agent 01 │ │ Agent 02 │   │
│  - Scheduling   │ ──────>│  │ (Linux)  │ │ (Docker) │   │
│  - UI/API       │        │  └──────────┘ └──────────┘   │
│  - Plugins      │        │                              │
└─────────────────┘        └──────────────────────────────┘
         │
         v
  Metadata/Config
  (JENKINS_HOME)
```

- Controller: 파이프라인 오케스트레이션(Job 관리, 스케줄링, UI/API, 플러그인). 실제 빌드 작업은 Agent에서 실행.
- Agent: 실제 빌드/테스트/배포 실행 노드. Docker, SSH, JNLP 방식으로 연결.
- Workspace: Agent에서 각 Job이 사용하는 작업 디렉토리.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Pipeline 유형

| 유형                   | 특징                                     | 권장 여부      |
|------------------------|------------------------------------------|----------------|
| Declarative Pipeline   | 구조화된 문법, 검증 용이, 가독성 높음    | ✅ 권장        |
| Scripted Pipeline      | Groovy 전체 문법 사용, 유연성 높음       | 복잡한 로직용  |
| Freestyle Job          | UI 기반 설정, 코드 관리 불가             | ❌ 비권장      |

[⬆ 목차로 돌아가기](#목차)

---

## 4. Declarative Pipeline

### 기본 구조

```groovy
pipeline {
    agent any                          // 실행 노드 지정

    environment {
        APP_NAME = 'my-app'
        DEPLOY_ENV = 'production'
    }

    options {
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    triggers {
        cron('H 2 * * *')             // 매일 02:xx (H = 해시 기반 분산)
        pollSCM('H/5 * * * *')        // 5분마다 SCM 폴링
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'make build'
            }
        }

        stage('Test') {
            parallel {
                stage('Unit Test') {
                    steps { sh 'make test-unit' }
                }
                stage('Integration Test') {
                    steps { sh 'make test-integration' }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
                environment name: 'DEPLOY_ENV', value: 'production'
            }
            steps {
                sh 'make deploy'
            }
        }
    }

    post {
        always {
            cleanWs()                  // 워크스페이스 정리
        }
        success {
            slackSend color: 'good', message: "Build #${BUILD_NUMBER} succeeded"
        }
        failure {
            slackSend color: 'danger', message: "Build #${BUILD_NUMBER} failed"
            emailext to: 'team@example.com', subject: 'Build Failed', body: '${BUILD_LOG}'
        }
    }
}
```

### when 조건

```groovy
when {
    branch 'main'                          // 브랜치 조건
    tag 'v*'                               // 태그 조건
    environment name: 'ENV', value: 'prod' // 환경변수 조건
    expression { return params.DEPLOY }    // Groovy 표현식
    not { branch 'develop' }               // 부정
    anyOf {                                // OR 조건
        branch 'main'
        branch 'release/*'
    }
    allOf {                                // AND 조건
        branch 'main'
        environment name: 'ENV', value: 'prod'
    }
}
```

### 자격증명 사용

```groovy
steps {
    withCredentials([
        usernamePassword(
            credentialsId: 'docker-hub',
            usernameVariable: 'DOCKER_USER',
            passwordVariable: 'DOCKER_PASS'
        )
    ]) {
        sh 'docker login -u $DOCKER_USER -p $DOCKER_PASS'
    }

    // AWS 자격증명
    withAWS(credentials: 'aws-prod', region: 'ap-northeast-1') {
        sh 'aws s3 sync ./dist s3://my-bucket/'
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Scripted Pipeline

복잡한 로직이 필요할 때 Groovy 전체 문법 사용.

```groovy
node('linux') {
    try {
        stage('Checkout') {
            checkout scm
        }

        stage('Build') {
            def version = sh(script: 'git describe --tags', returnStdout: true).trim()
            env.VERSION = version
            sh "docker build -t myapp:${version} ."
        }

        stage('Deploy') {
            if (env.BRANCH_NAME == 'main') {
                sh "kubectl set image deployment/myapp myapp=myapp:${env.VERSION}"
            } else {
                echo "Skipping deploy for branch: ${env.BRANCH_NAME}"
            }
        }

    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        cleanWs()
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 공유 라이브러리

여러 파이프라인에서 공통 코드 재사용.

### 디렉토리 구조

```
jenkins-shared-library/
├── vars/
│   ├── deployToK8s.groovy     # 전역 함수
│   └── notifySlack.groovy
└── src/
    └── com/example/
        └── Utils.groovy       # 클래스
```

### vars/deployToK8s.groovy

```groovy
def call(String appName, String version, String namespace = 'default') {
    sh """
        kubectl set image deployment/${appName} \
          ${appName}=${appName}:${version} \
          -n ${namespace}
        kubectl rollout status deployment/${appName} -n ${namespace}
    """
}
```

### Jenkinsfile에서 사용

```groovy
@Library('jenkins-shared-library') _

pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                deployToK8s('my-app', '1.2.3', 'production')
            }
        }
    }
}
```

Jenkins 관리 → System → Global Pipeline Libraries에서 라이브러리 등록 필요.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 에이전트/노드

### 에이전트 유형

```groovy
// 모든 노드
agent any

// 특정 레이블
agent { label 'linux && docker' }

// Docker 컨테이너
agent {
    docker {
        image 'node:20-alpine'
        args '-v /tmp:/tmp'
    }
}

// Kubernetes Pod
agent {
    kubernetes {
        yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: build
    image: maven:3.9-eclipse-temurin-17
    command: [sleep, infinity]
'''
        defaultContainer 'build'
    }
}

// 없음 (stage별 지정)
agent none
```

### Stage별 에이전트 지정

```groovy
pipeline {
    agent none
    stages {
        stage('Build') {
            agent { label 'linux' }
            steps { sh 'make build' }
        }
        stage('Deploy') {
            agent { label 'deploy-server' }
            steps { sh 'make deploy' }
        }
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 플러그인

### 필수 플러그인

| 플러그인              | 용도                         |
|-----------------------|------------------------------|
| Pipeline              | 파이프라인 기본 기능         |
| Git                   | Git 연동                     |
| Credentials Binding   | 자격증명 주입                |
| Blue Ocean            | 파이프라인 시각화 UI         |
| Slack Notification    | Slack 알림                   |
| Docker Pipeline       | Docker 빌드/실행             |
| Kubernetes            | K8s 동적 에이전트            |
| AWS Steps             | AWS CLI 래퍼                 |
| JUnit                 | 테스트 결과 리포트           |
| HTML Publisher        | HTML 리포트 게시             |
| Timestamper           | 로그에 타임스탬프 추가       |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 보안

### 필수 설정

```groovy
// Groovy 스크립트 승인 (Script Security)
// 관리 -> In-process Script Approval 에서 승인

// 자격증명은 반드시 Credentials Store 사용
// 환경변수에 직접 비밀번호 하드코딩 금지
environment {
    // 잘못된 예
    // DB_PASS = 'hardcoded-password'

    // 올바른 예
    DB_PASS = credentials('db-password-id')
}
```

### 권한 관리

- Role-Based Access Control (RBAC) 플러그인 사용
- 프로젝트별 권한 분리
- API Token 사용 (비밀번호 대신)

```bash
# API Token으로 빌드 트리거
curl -X POST \
  "https://jenkins.example.com/job/my-job/build" \
  --user "username:api-token"
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 모니터링

### 빌드 상태 확인

```bash
# Jenkins CLI
java -jar jenkins-cli.jar -s http://localhost:8080 \
  -auth user:token list-jobs

# API로 빌드 상태 조회
curl -s "http://localhost:8080/job/my-job/lastBuild/api/json" \
  --user user:token | jq '.result'
```

### 주요 모니터링 지표

| 지표               | 확인 방법                           |
|--------------------|-------------------------------------|
| 빌드 성공률        | Build History, Blue Ocean           |
| 빌드 시간 추이     | Build Time Trend 플러그인           |
| 큐 대기 시간       | Manage Jenkins -> Load Statistics   |
| 에이전트 상태      | Manage Jenkins -> Nodes             |
| 디스크 사용량      | JENKINS_HOME 모니터링 필수          |

### Prometheus 연동

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'jenkins'
    metrics_path: '/prometheus'
    static_configs:
      - targets: ['jenkins:8080']
```

Prometheus 플러그인 설치 필요.

[⬆ 목차로 돌아가기](#목차)

---

## 11. Tips

### 설계

- Declarative Pipeline 우선 사용: 문법 검증, 가독성, 재사용성 모두 우수.
- `agent none` + stage별 에이전트: 불필요한 노드 점유 방지.
- `disableConcurrentBuilds()`: 동일 Job 중복 실행 방지. 배포 Job에 필수.
- `timeout` 옵션 필수: 무한 대기 방지.

### 성능

- 공유 라이브러리로 중복 코드 제거.
- Docker 에이전트 사용 시 이미지 캐싱 전략 수립.
- `stash`/`unstash`로 stage 간 파일 전달 (대용량 파일은 S3 사용):

```groovy
stage('Build') {
    steps {
        sh 'make build'
        stash name: 'build-artifacts', includes: 'dist/**'
    }
}
stage('Deploy') {
    steps {
        unstash 'build-artifacts'
        sh 'make deploy'
    }
}
```

### 운영

- JENKINS_HOME 정기 백업 필수 (jobs/, credentials.xml, config.xml).
- 오래된 빌드 자동 삭제: `buildDiscarder(logRotator(numToKeepStr: '30'))`.
- 플러그인 업데이트는 스테이징 환경에서 먼저 검증.
- Jenkinsfile을 SCM에 저장: 파이프라인 변경 이력 관리.

### 디버깅

```groovy
// 환경변수 전체 출력
steps {
    sh 'env | sort'
}

// Groovy 변수 출력
steps {
    script {
        echo "version: ${env.VERSION}"
        echo "workspace: ${env.WORKSPACE}"
    }
}

// 단계별 실행 시간 측정
steps {
    timestamps {
        sh 'make build'
    }
}
```

⚠️ `sh` 명령어에서 비밀번호가 포함된 명령은 `set +x`로 echo 비활성화:

```groovy
sh '''
    set +x
    echo $SECRET_VAR | docker login --password-stdin
    set -x
'''
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 멀티브랜치 Pipeline

### 개념

SCM 저장소의 브랜치/PR을 자동으로 감지하여 각각 독립적인 파이프라인을 생성합니다.

```
GitHub Repository
├── main          → Jenkins Job: my-app/main
├── develop       → Jenkins Job: my-app/develop
├── feature/login → Jenkins Job: my-app/feature%2Flogin
└── PR #42        → Jenkins Job: my-app/PR-42
```

### 설정 (Jenkins UI)

```
New Item → Multibranch Pipeline
→ Branch Sources: GitHub / GitLab
→ Discover Branches: All branches
→ Discover Pull Requests: Merge with target branch
→ Build Configuration: by Jenkinsfile (경로: Jenkinsfile)
→ Scan Multibranch Pipeline Triggers: 1분마다 또는 Webhook
```

### Jenkinsfile 브랜치 분기 패턴

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }

        stage('Test') {
            steps {
                sh 'make test'
            }
        }

        stage('Deploy Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh 'make deploy-staging'
            }
        }

        stage('Deploy Production') {
            when {
                branch 'main'
            }
            steps {
                input message: '운영 배포 승인', ok: '배포'
                sh 'make deploy-prod'
            }
        }

        stage('PR Check') {
            when {
                changeRequest()   // PR일 때만 실행
            }
            steps {
                sh 'make lint && make test-coverage'
            }
        }
    }
}
```

### GitHub Webhook 설정

```
GitHub Repository → Settings → Webhooks → Add webhook
Payload URL: https://jenkins.example.com/github-webhook/
Content type: application/json
Events: Push, Pull requests
```

```groovy
// Jenkinsfile에서 webhook 트리거 활성화
properties([
    pipelineTriggers([githubPush()])
])
```

### 브랜치별 배포 환경 분기

```groovy
def deployEnv = [
    'main'   : 'production',
    'develop': 'staging',
].get(env.BRANCH_NAME, 'dev')

echo "Deploy target: ${deployEnv}"
```

[⬆ 목차로 돌아가기](#목차)

---

## 13. Docker 빌드 / ECR

### ECR 로그인 + 이미지 빌드 + 푸시

```groovy
pipeline {
    agent any

    environment {
        AWS_REGION     = 'ap-northeast-1'
        AWS_ACCOUNT_ID = '123456789012'
        ECR_REPO       = 'my-app'
        IMAGE_TAG      = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
        ECR_URI        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
    }

    stages {
        stage('ECR Login') {
            steps {
                withAWS(credentials: 'aws-ecr', region: "${AWS_REGION}") {
                    sh 'aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com'
                }
            }
        }

        stage('Build') {
            steps {
                sh "docker build --cache-from ${ECR_URI}:latest -t ${ECR_URI}:${IMAGE_TAG} -t ${ECR_URI}:latest ."
            }
        }

        stage('Push') {
            steps {
                sh "docker push ${ECR_URI}:${IMAGE_TAG} && docker push ${ECR_URI}:latest"
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                withAWS(credentials: 'aws-ecr', region: "${AWS_REGION}") {
                    sh "aws ecs update-service --cluster prod-cluster --service my-app --force-new-deployment"
                }
            }
        }
    }

    post {
        always {
            sh "docker rmi ${ECR_URI}:${IMAGE_TAG} || true"
        }
    }
}
```

### 태그 전략

| 태그 패턴                   | 용도                          |
|-----------------------------|-------------------------------|
| `latest`                    | 최신 main 브랜치 이미지       |
| `main-42` (브랜치-빌드번호) | 재현 가능한 특정 빌드         |
| `v1.2.3` (Git 태그)         | 릴리즈 버전                   |
| `sha-a1b2c3d` (커밋 해시)   | 정확한 소스 추적              |

```groovy
// Git 태그 기반 이미지 태그
def gitTag = sh(script: 'git describe --tags --exact-match 2>/dev/null || echo ""', returnStdout: true).trim()
def imageTag = gitTag ?: "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
```

### 멀티스테이지 빌드 캐시 활용

```groovy
stage('Build') {
    steps {
        script {
            sh "docker pull ${ECR_URI}:builder || true"
            sh "docker build --target builder --cache-from ${ECR_URI}:builder -t ${ECR_URI}:builder ."
            sh "docker build --cache-from ${ECR_URI}:builder --cache-from ${ECR_URI}:latest -t ${ECR_URI}:${IMAGE_TAG} ."
            sh "docker push ${ECR_URI}:builder"
        }
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 14. 테스트 리포트 / 아티팩트

### JUnit 테스트 리포트

```groovy
stage('Test') {
    steps {
        sh 'make test'   // JUnit XML 생성: test-results/*.xml
    }
    post {
        always {
            junit(
                testResults: 'test-results/**/*.xml',
                allowEmptyResults: true
            )
        }
    }
}
```

### 코드 커버리지 (Cobertura)

```groovy
post {
    always {
        cobertura(
            coberturaReportFile: 'coverage.xml',
            failUnhealthy: true,
            lineCoverageTargets: '80, 70, 60'   // healthy, unhealthy, failing
        )
    }
}
```

### HTML 리포트 게시

```groovy
post {
    always {
        publishHTML(target: [
            allowMissing         : false,
            alwaysLinkToLastBuild: true,
            keepAll              : true,
            reportDir            : 'reports/html',
            reportFiles          : 'index.html',
            reportName           : 'Test Report'
        ])
    }
}
```

### 아티팩트 보관

```groovy
post {
    success {
        archiveArtifacts(
            artifacts: 'dist/**/*.jar, dist/**/*.war',
            fingerprint: true,
            allowEmptyArchive: false
        )
    }
}
```

### stash / unstash (다른 노드 간 파일 전달)

```groovy
stage('Build') {
    steps {
        sh 'make build'
        stash name: 'build-artifacts', includes: 'dist/**'
    }
}

stage('Integration Test') {
    agent { label 'test-server' }
    steps {
        unstash 'build-artifacts'
        sh 'make integration-test'
        junit 'test-results/*.xml'
    }
}
```

### 빌드 상태 배지 (README)

```markdown
[![Build Status](https://jenkins.example.com/buildStatus/icon?job=my-app%2Fmain)](https://jenkins.example.com/job/my-app/job/main/)
```

[⬆ 목차로 돌아가기](#목차)
