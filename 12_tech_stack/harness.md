# Harness

CI/CD 및 소프트웨어 딜리버리 플랫폼입니다. AI 기반 배포 검증과 클라우드 비용 관리를 통합 제공합니다.

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 핵심 모듈](#2-핵심-모듈) / [3. 아키텍처](#3-아키텍처)                                     |
| [4. CD 배포 전략](#4-cd-배포-전략) / [5. 타 도구 비교](#5-타-도구-비교) / [6. 파이프라인 구성](#6-파이프라인-구성) |

## 1. 개요

| 항목     | 값                                                    |
|----------|-------------------------------------------------------|
| 제공사   | Harness Inc.                                          |
| 유형     | 상용 SaaS / Self-Managed (On-Prem 가능)               |
| 대상     | 대규모 DevOps팀, 배포 빈도 높은 환경                  |
| 핵심     | AI 기반 배포 검증 (Continuous Verification)           |
| 가격     | Free Tier 있음, Enterprise는 사용량 기반 과금         |
| 경쟁제품 | Jenkins, GitHub Actions, GitLab CI, ArgoCD, Spinnaker |

## 2. 핵심 모듈

| 모듈                        | 기능                                              |
|-----------------------------|---------------------------------------------------|
| CD (Continuous Delivery)    | K8s/ECS/Lambda/VM 배포, Canary/Blue-Green/Rolling |
| CI (Continuous Integration) | 빌드/테스트, 컨테이너 기반 실행                   |
| Feature Flags               | 기능 플래그 관리 (A/B 테스트, 점진적 롤아웃)      |
| Cloud Cost Management       | AWS/GCP/Azure 비용 분석, 유휴 리소스 탐지         |
| STO (Security Testing)      | SAST/DAST/SCA 보안 스캔 통합                      |
| Chaos Engineering           | 장애 주입 테스트 (Litmus 기반)                    |
| Service Reliability         | SLO/SLI 모니터링, Error Budget 추적               |

## 3. 아키텍처

```
Developer
  │
  ▼
Git Push ──► Harness CI (Build/Test)
                │
                ▼
         Harness CD (Deploy)
                │
                ├──► Canary / Blue-Green / Rolling
                │
                ▼
         Continuous Verification (AI)
                │
                ├── Metrics (Prometheus/Datadog/CloudWatch)
                ├── Logs (ELK/Splunk/Loki)
                └── Health Check
                │
                ▼
         Auto Rollback (이상 감지 시 자동 롤백)
```

### Delegate (핵심 컴포넌트)

Harness는 SaaS이지만 실제 배포는 사용자 환경에 설치된 **Delegate**가 수행합니다.

```
Harness SaaS (Manager)
       │
       │ (HTTPS outbound only)
       ▼
Delegate (K8s Pod / Docker / VM)
       │
       ├──► kubectl apply (K8s)
       ├──► aws ecs (ECS)
       ├──► terraform apply (IaC)
       └──► ssh/script (VM)
```

- Delegate는 outbound HTTPS만 사용합니다 (방화벽 인바운드 오픈 불필요).
- VPC/IDC 내부에 설치하여 프라이빗 리소스에 접근합니다.

## 4. CD 배포 전략

### Canary 배포

```yaml
# Harness Pipeline YAML 예시
stages:
  - stage:
      name: Canary
      spec:
        execution:
          steps:
            - step:
                type: CanaryDeploy
                spec:
                  instanceCount: 1  # 1대만 먼저 배포
            - step:
                type: Verify
                spec:
                  duration: 5m       # 5분간 메트릭 검증
            - step:
                type: CanaryDeploy
                spec:
                  instanceCount: 100%  # 전체 배포
```

### Blue-Green 배포

```yaml
stages:
  - stage:
      name: BlueGreen
      spec:
        execution:
          steps:
            - step:
                type: K8sBlueGreenDeploy
            - step:
                type: Verify
                spec:
                  duration: 10m
            - step:
                type: K8sBlueGreenSwapServices
```

### Continuous Verification (AI 검증)

배포 후 자동으로 메트릭/로그를 분석하여 이상 감지 시 롤백합니다.

| 데이터 소스 | 지원                     |
|-------------|--------------------------|
| Prometheus  | ✅                       |
| Datadog     | ✅                       |
| CloudWatch  | ✅                       |
| New Relic   | ✅                       |
| ELK/Splunk  | ✅ (로그 기반 이상 감지) |

## 5. 타 도구 비교

| 기준         | Harness      | Jenkins       | GitHub Actions | ArgoCD      | Spinnaker    |
|--------------|--------------|---------------|----------------|-------------|--------------|
| 유형         | 상용 SaaS    | 오픈소스      | SaaS           | 오픈소스    | 오픈소스     |
| CI           | ✅           | ✅            | ✅             | ❌          | ❌           |
| CD           | ✅           | 플러그인 조합 | ✅ (제한적)    | ✅ (GitOps) | ✅           |
| AI 배포 검증 | ✅           | ❌            | ❌             | ❌          | ❌           |
| 자동 롤백    | ✅ (AI 기반) | 수동 구현     | 수동 구현      | Git revert  | ✅ (룰 기반) |
| K8s 지원     | ✅           | 플러그인      | ✅             | ✅ (전문)   | ✅           |
| VM/SSH 배포  | ✅           | ✅            | ✅             | ❌          | ✅           |
| 비용 관리    | ✅           | ❌            | ❌             | ❌          | ❌           |
| 러닝커브     | 중간         | 높음          | 낮음           | 중간        | 높음         |
| 가격         | 유료         | 무료          | 무료+유료      | 무료        | 무료         |

### 선택 기준

- 소규모팀 / 단순 CI/CD → **GitHub Actions**
- K8s GitOps 전문 → **ArgoCD**
- 대규모 / AI 검증 / 자동 롤백 필요 → **Harness**
- 커스터마이징 극대화 → **Jenkins**
- 멀티클라우드 대규모 배포 → **Spinnaker**

## 6. 파이프라인 구성

### 기본 구조

```
Pipeline
  └── Stage (CI Build)
        └── Step: Run (빌드)
        └── Step: Run (테스트)
        └── Step: Build and Push (이미지 빌드)
  └── Stage (CD Deploy)
        └── Step: K8s Apply / ECS Deploy / SSH Script
        └── Step: Verify (AI 검증)
        └── Step: Rollback (실패 시)
```

### YAML 기반 파이프라인 (Pipeline-as-Code)

```yaml
pipeline:
  name: my-service-deploy
  stages:
    - stage:
        name: Build
        type: CI
        spec:
          steps:
            - step:
                type: Run
                spec:
                  command: |
                    mvn clean package
                    docker build -t my-app:${BUILD_NUMBER} .
            - step:
                type: BuildAndPushDockerRegistry
                spec:
                  repo: my-ecr-repo/my-app
                  tags:
                    - ${BUILD_NUMBER}
    - stage:
        name: Deploy
        type: Deployment
        spec:
          steps:
            - step:
                type: K8sRollingDeploy
            - step:
                type: Verify
                spec:
                  type: Canary
                  duration: 10m
                  sensitivity: MEDIUM
```

## 참고 자료

- Harness Documentation: [developer.harness.io/docs](https://developer.harness.io/docs/) — ★★★☆☆
- Harness CD Concepts: [developer.harness.io/docs/continuous-delivery](https://developer.harness.io/docs/continuous-delivery/) — ★★★☆☆
- Harness vs Jenkins: [harness.io/blog/harness-vs-jenkins](https://www.harness.io/blog/harness-vs-jenkins) — ★★☆☆☆

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-06-18

© 2026 siasia86. Licensed under CC BY 4.0.
