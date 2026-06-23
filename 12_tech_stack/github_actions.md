# GitHub Actions

## 목차

| 섹션                                                                                                                    |
|-------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념)                                          |
| [4. 워크플로우 문법](#4-워크플로우-문법) / [5. 트리거](#5-트리거) / [6. Jobs & Steps](#6-jobs--steps)                   |
| [7. 환경변수 & 시크릿](#7-환경변수--시크릿) / [8. 재사용 워크플로우](#8-재사용-워크플로우) / [9. AWS 연동](#9-aws-연동) |
| [10. 실전 예시](#10-실전-예시) / [11. Tips](#11-tips)                                                                   |

---

## 1. 개요

GitHub Actions는 GitHub에 내장된 CI/CD 플랫폼. 저장소 이벤트(push, PR, schedule 등)에 반응하여 워크플로우를 자동 실행합니다.

```
┌──────────────────────────────────────────────────────────────┐
│                  GitHub Actions Flow                         │
│                                                              │
│  Event (push/PR) -> Workflow -> Job -> Step -> Action        │
│                                                              │
│  .github/workflows/*.yml -> Runner -> Execute                │
└──────────────────────────────────────────────────────────────┘
```

- Jenkins 대비 별도 서버 불필요, GitHub 저장소와 네이티브 통합
- Public 저장소: 무료 / Private 저장소: 월 2,000분 무료 (GitHub Free 기준)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                      GitHub                                  │
│                                                              │
│  Repository ──> Events ──> Workflow Dispatcher               │
│                                  │                           │
│                                  v                           │
│                         ┌────────────────┐                   │
│                         │  Job Queue     │                   │
│                         └────────────────┘                   │
└──────────────────────────────────────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              v                    v                    v
   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
   │  GitHub-hosted   │  │  GitHub-hosted   │  │  Self-hosted     │
   │  Runner          │  │  Runner          │  │  Runner          │
   │  (ubuntu-latest) │  │  (windows-latest)│  │  (on-premises)   │
   └──────────────────┘  └──────────────────┘  └──────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념        | 설명                                                          |
|-------------|---------------------------------------------------------------|
| Workflow    | 자동화 프로세스 정의 파일 (`.github/workflows/*.yml`)         |
| Event       | 워크플로우를 트리거하는 GitHub 이벤트 (push, pull_request 등) |
| Job         | Runner에서 실행되는 작업 단위. 기본적으로 병렬 실행           |
| Step        | Job 내 순차 실행 단위. shell 명령어 또는 Action               |
| Action      | 재사용 가능한 Step 단위 패키지 (Marketplace에서 공유)         |
| Runner      | 워크플로우를 실행하는 서버 (GitHub-hosted 또는 Self-hosted)   |
| Secret      | 암호화된 환경변수 (토큰, 비밀번호 등)                         |
| Environment | 배포 환경 (dev/stg/prod). 보호 규칙 및 시크릿 범위 설정 가능  |
| Matrix      | 여러 OS/버전 조합으로 Job을 병렬 실행                         |
| Artifact    | Job 간 또는 워크플로우 실행 결과 파일 공유                    |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 워크플로우 문법

### 기본 구조

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Setup Node.js
        uses: actions/setup-node@v6
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

### 디렉토리 구조

```
.github/
└── workflows/
    ├── ci.yml          # PR 검증
    ├── cd.yml          # 배포
    └── scheduled.yml   # 정기 실행
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 트리거

```yaml
on:
  # 브랜치 push
  push:
    branches: [main, 'release/**']
    paths:
      - 'src/**'
      - '!docs/**'   # 제외

  # PR
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

  # 스케줄 (cron)
  schedule:
    - cron: '0 2 * * *'   # 매일 02:00 UTC

  # 수동 실행
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deploy environment'
        required: true
        default: 'dev'
        type: choice
        options: [dev, stg, prod]

  # 다른 워크플로우에서 호출
  workflow_call:
    inputs:
      image_tag:
        required: true
        type: string

  # 릴리즈
  release:
    types: [published]
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Jobs & Steps

### Job 의존성 & 병렬 실행

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm test

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm run lint

  build:
    runs-on: ubuntu-latest
    needs: [test, lint]   # test, lint 완료 후 실행
    steps:
      - uses: actions/checkout@v6
      - run: npm run build

  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'   # 조건부 실행
    steps:
      - run: echo "Deploying..."
```

### Matrix 전략

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: ['18', '20']
        exclude:
          - os: windows-latest
            node: '18'
      fail-fast: false   # 하나 실패해도 나머지 계속 실행

    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

### Artifact 공유

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build
      - uses: actions/upload-artifact@v7
        with:
          name: build-output
          path: dist/
          retention-days: 7

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/
      - run: ./deploy.sh
```

### 캐시

```yaml
- uses: actions/cache@v5
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 환경변수 & 시크릿

### 시크릿 설정

```
GitHub Repository → Settings → Secrets and variables → Actions
→ New repository secret
```

### 시크릿 사용

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production   # Environment 시크릿 사용 시

    env:
      APP_ENV: production

    steps:
      - name: Deploy
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          # 🟡 장기 키 방식 — OIDC 사용 불가한 경우에만 사용 (섹션 9 OIDC 권장)
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: ./deploy.sh
```

### 기본 제공 컨텍스트 변수

```yaml
steps:
  - run: |
      echo "Repo: ${{ github.repository }}"
      echo "Branch: ${{ github.ref_name }}"
      echo "SHA: ${{ github.sha }}"
      echo "Actor: ${{ github.actor }}"
      echo "Event: ${{ github.event_name }}"
      echo "Run ID: ${{ github.run_id }}"
```

### Environment 보호 규칙

```
Settings → Environments → production
→ Required reviewers: 승인자 지정
→ Wait timer: 배포 전 대기 시간
→ Deployment branches: main만 허용
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 재사용 워크플로우

### 재사용 가능한 워크플로우 정의

```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image_tag:
        required: true
        type: string
    secrets:
      AWS_ROLE_ARN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ap-northeast-1

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ inputs.environment }}-cluster \
            --service my-app \
            --force-new-deployment
```

### 재사용 워크플로우 호출

```yaml
# .github/workflows/cd.yml
jobs:
  deploy-stg:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: stg
      image_tag: ${{ needs.build.outputs.image_tag }}
    secrets:
      AWS_ROLE_ARN: ${{ secrets.STG_AWS_ROLE_ARN }}

  deploy-prod:
    needs: deploy-stg
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: prod
      image_tag: ${{ needs.build.outputs.image_tag }}
    secrets:
      AWS_ROLE_ARN: ${{ secrets.PROD_AWS_ROLE_ARN }}
```

### Composite Action

```yaml
# .github/actions/setup-app/action.yml
name: 'Setup Application'
description: 'Install dependencies and cache'

inputs:
  node-version:
    description: 'Node.js version'
    default: '20'

runs:
  using: 'composite'
  steps:
    - uses: actions/setup-node@v6
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'
    - run: npm ci
      shell: bash
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. AWS 연동

### OIDC (권장, 장기 자격증명 불필요)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # OIDC 토큰 발급 필수
      contents: read

    steps:
      - uses: actions/checkout@v6

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-role
          aws-region: ap-northeast-1

      - name: AWS CLI 사용 가능
        run: aws s3 ls
```

```json
// IAM Role Trust Policy (GitHub OIDC)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:*"
        }
      }
    }
  ]
}
```

### ECR + ECS 배포

```yaml
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    env:
      AWS_REGION: ap-northeast-1
      ECR_REPOSITORY: my-app
      ECS_CLUSTER: prod-cluster
      ECS_SERVICE: my-app-service

    steps:
      - uses: actions/checkout@v6

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 실전 예시

### PR 검증 워크플로우

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm test -- --coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v7
        with:
          name: coverage
          path: coverage/
```

### 릴리즈 태그 기반 배포

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.version }}

    steps:
      - uses: actions/checkout@v6

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/my-app
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        run: |
          docker build -t ${{ steps.meta.outputs.tags }} .
          docker push ${{ steps.meta.outputs.tags }}
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. Tips

### 주요 공식 Action

| Action                                     | 용도               |
|--------------------------------------------|--------------------|
| `actions/checkout@v6`                      | 코드 체크아웃      |
| `actions/setup-node@v6`                    | Node.js 설치       |
| `actions/setup-python@v5`                  | Python 설치        |
| `actions/cache@v5`                         | 의존성 캐시        |
| `actions/upload-artifact@v7`               | 아티팩트 업로드    |
| `actions/download-artifact@v4`             | 아티팩트 다운로드  |
| `aws-actions/configure-aws-credentials@v4` | AWS 자격증명 설정  |
| `aws-actions/amazon-ecr-login@v2`          | ECR 로그인         |
| `docker/build-push-action@v5`              | Docker 빌드 & 푸시 |

### 디버깅

```yaml
# 디버그 로그 활성화
# Repository → Settings → Secrets → ACTIONS_STEP_DEBUG = true

steps:
  - name: Debug context
    run: |
      echo '${{ toJSON(github) }}'
      echo '${{ toJSON(env) }}'
      echo '${{ toJSON(job) }}'
```

### 주의사항

🟡 `secrets.GITHUB_TOKEN`은 자동 제공되지만 권한 범위를 최소화합니다. `permissions` 키로 명시적 선언을 권장합니다.

🟡 Self-hosted Runner는 Public 저장소에서 사용 시 보안 위험이 있습니다. Fork PR이 악성 코드를 실행할 수 있으므로 Private 저장소에서만 사용합니다.

🟡 AWS 자격증명은 장기 키(Access Key) 대신 OIDC를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- GitHub Actions Documentation: [docs.github.com/actions](https://docs.github.com/en/actions) — ★★★☆☆
- GitHub Actions Marketplace: [github.com/marketplace](https://github.com/marketplace?type=actions) — ★★☆☆☆
- AWS GitHub Actions: [github.com/aws-actions](https://github.com/aws-actions) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-10

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.
