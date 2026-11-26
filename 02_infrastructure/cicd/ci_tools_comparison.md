# CI/CD 도구 비교
<!-- reference: _reference/jenkins_official_notes.md -->
<!-- reference: _reference/gitlab_official_notes.md -->
<!-- reference: _reference/teamcity_official_notes.md -->
<!-- reference: _reference/circleci_official_notes.md -->
<!-- reference: _reference/buildkite_official_notes.md -->
<!-- reference: _reference/octopus_deploy_official_notes.md -->

빌드·테스트를 자동으로 돌리는 CI 도구와 배포를 맡는 CD 도구를 비교합니다. Jenkins·GitLab CI는 자체 설치를 시험한 문서가 따로 있고, TeamCity·CircleCI·Buildkite·Octopus Deploy는 공식 문서와 요금 페이지를 대조했습니다.

- 기준: 2026-11-26 공식 문서·요금 페이지 확인. Jenkins 2.580.3과 GitLab Runner 19.6.1은 컨테이너로 확인, 나머지는 실행하지 않았음
- 가격은 확인일 기준이며 자주 바뀝니다. 도입 전에 요금 페이지를 다시 확인합니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 나누는 기준](#1-나누는-기준) / [2. 비교 표](#2-비교-표) / [3. 비용](#3-비용)                     |
| [4. 설정 방식](#4-설정-방식) / [5. 고르는 기준](#5-고르는-기준) / [6. 도입 전 확인](#6-도입-전-확인) |

---

## 1. 나누는 기준

| 구분               | 하는 일                                          | 도구                                     |
|--------------------|--------------------------------------------------|------------------------------------------|
| CI 서버(자체 설치) | 빌드 서버·에이전트를 직접 운영                   | Jenkins, TeamCity                        |
| 저장소 내장 CI     | 코드 저장소 서비스에 CI가 붙어 있음              | GitLab CI/CD, GitHub Actions             |
| SaaS CI            | 제어 화면은 SaaS, 실행은 SaaS 또는 자체 에이전트 | CircleCI, Buildkite                      |
| CD 전용            | 빌드 결과를 받아 환경별 배포·승인·롤백           | Octopus Deploy, Argo CD(GitOps), Harness |

```text
코드 push ──▶ [CI: 빌드·테스트·패키지] ──산출물──▶ [저장소: Nexus 등] ──▶ [CD: 환경별 배포]
               Jenkins / GitLab CI /                                    Octopus / Argo CD /
               GitHub Actions / CircleCI ...                            CI 도구의 배포 단계
```

- 작은 팀은 CI 도구 하나로 배포까지 하고, 환경·고객이 많아지면 CD 도구를 따로 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 비교 표

| 항목      | Jenkins                  | GitLab CI/CD                 | TeamCity                                   | CircleCI                                         | Buildkite                       | Octopus Deploy        |
|-----------|--------------------------|------------------------------|--------------------------------------------|--------------------------------------------------|---------------------------------|-----------------------|
| 형태      | 자체 설치, 오픈소스      | GitLab 내장(SaaS·자체)       | 자체 설치(+ Cloud)                         | SaaS(+ Server)                                   | SaaS 제어 + 자체 에이전트       | CD 전용, Cloud·Server |
| 확인한 판 | 2.580.3 LTS              | GitLab 19.6.2, Runner 19.6.1 | 2026.2                                     | -                                                | 에이전트 v4.12.0                | Server 2026.3         |
| 설정 파일 | `Jenkinsfile`(Groovy)    | `.gitlab-ci.yml`             | `.teamcity/settings.kts`(Kotlin) 또는 화면 | `.circleci/config.yml`                           | `.buildkite/pipeline.yml`       | OCL(Git) 또는 화면    |
| 실행기    | 에이전트(노드)           | GitLab Runner                | 빌드 에이전트                              | Docker·machine·macOS·Windows, self-hosted runner | 에이전트(폴링, 인바운드 불필요) | Tentacle·SSH 대상     |
| 재사용    | Shared Library, 플러그인 | include, 컴포넌트(inputs)    | 템플릿, Kotlin 코드                        | orbs, commands                                   | 플러그인, 동적 Pipeline         | 단계 템플릿, 런북     |
| 무료 범위 | 전부(서버 비용만)        | Free: 월 400 compute 분      | Professional: 구성 100·에이전트 3          | 월 30,000 크레딧·사용자 5                        | 사용자 5·동시 10                | 프로젝트·머신 각 10   |
| 강점      | 플러그인 생태계, 자유도  | 저장소·MR·레지스트리 통합    | 빌드 체인·JetBrains 도구 연동              | 설정 쉬움, macOS 빌드                            | 대규모 병렬, 자체 인프라 활용   | 환경·테넌트·승인·롤백 |
| 부담      | 서버·플러그인 운영       | GitLab에 묶임                | 상용 라이선스(구성 많을 때)                | 크레딧 소비 예측                                 | 에이전트 운영                   | CI 도구가 따로 필요   |

- GitHub Actions는 [GitHub Actions](./github_actions.md) 문서를 봅니다. 이 비교의 확인 범위에 넣지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 비용

2026-11-26 공식 요금 페이지 기준(USD, 세금 별도).

| 도구           | 무료                                       | 유료(시작 가격)                                                        |
|----------------|--------------------------------------------|------------------------------------------------------------------------|
| Jenkins        | 소프트웨어 무료                            | 서버·에이전트 인프라와 운영 인력                                       |
| GitLab.com     | Free $0, compute 월 400분, 비공개 그룹 5명 | Premium 사용자당 월 $29(연간), compute 월 10,000분. Ultimate 별도 문의 |
| TeamCity       | Professional 무료(구성 100, 에이전트 3)    | Enterprise 가격 미확인(구매 페이지 조회 실패)                          |
| CircleCI       | Free: 월 30,000 크레딧, 사용자 5           | Performance 월 $15부터, 추가 25,000 크레딧 $15                         |
| Buildkite      | Free: 사용자 5, Linux vCPU 월 2,000분      | Pro 활성 사용자당 월 $30, 에이전트 10개 초과분 개당 월 $3.50           |
| Octopus Deploy | Free: 프로젝트·머신·사용자 각 10           | Professional 연 $4,330(Cloud)·$2,080(Server)                           |

- GitLab compute 분이 모자라면 1,000분을 $10에 추가하거나 자체 Runner를 붙입니다.
- SaaS CI는 사용량(분·크레딧)으로 비용이 늘어납니다. 자체 에이전트·runner를 쓰면 실행 비용은 자기 인프라로 옮겨집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설정 방식

같은 일(테스트 후 산출물 보관)을 각 도구로 쓰면 다음과 같습니다. 문법 대조용 예시이며 Jenkins만 실행해 확인했습니다.

```groovy
// Jenkinsfile
pipeline {
  agent any
  stages {
    stage('Test')    { steps { sh 'make test' } }
    stage('Archive') { steps { archiveArtifacts artifacts: 'dist/*' } }
  }
}
```

```yaml
# .gitlab-ci.yml
test:
  script: [make test]
  artifacts:
    paths: [dist/]
```

```yaml
# .circleci/config.yml
version: 2.1
jobs:
  test:
    docker: [{ image: cimg/base:current }]
    steps:
      - checkout
      - run: make test
      - store_artifacts: { path: dist }
workflows:
  main: { jobs: [test] }
```

```yaml
# .buildkite/pipeline.yml
steps:
  - label: "test"
    command: "make test"
    artifact_paths: "dist/*"
```

- TeamCity는 Kotlin DSL(`settings.kts`)이나 화면으로, Octopus는 배포 절차를 화면이나 OCL로 정의합니다.
- CircleCI·Buildkite 예시의 키(`store_artifacts`, `artifact_paths`)는 각 문서의 일반 문법이며 이 문서에서 실행하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 고르는 기준

| 상황                                      | 우선 검토                     |
|-------------------------------------------|-------------------------------|
| 이미 GitLab을 쓴다                        | GitLab CI/CD + 자체 Runner    |
| 이미 GitHub를 쓴다                        | GitHub Actions                |
| 폐쇄망·온프레미스, 플러그인으로 맞춤 구성 | Jenkins (JCasC로 설정 코드화) |
| JetBrains IDE·.NET·대형 빌드 체인         | TeamCity                      |
| 서버 운영 없이 빠르게, macOS 빌드 필요    | CircleCI                      |
| 대규모 병렬, 빌드는 자기 인프라에서       | Buildkite                     |
| 환경·고객(테넌트)별 배포와 승인이 많음    | Octopus Deploy (CI는 따로)    |
| Kubernetes에 GitOps 방식 배포             | [Argo CD](./argocd.md)        |

- 한 도구로 모든 것을 하려 하기보다 "CI는 저장소 내장, 배포는 CD 도구"처럼 나누는 구성도 흔합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 도입 전 확인

1. 코드 저장소 위치(GitLab·GitHub·자체 Git)와 연동 방식(Webhook·내장).
2. 실행 위치: SaaS 실행기 허용 여부, 폐쇄망이면 자체 에이전트·runner 필수.
3. 비밀값 관리: 도구 내장 저장소, 외부 비밀 관리자(Vault 등) 연동.
4. 비용 모델: 사용자 수, 실행 분·크레딧, 에이전트 수, 연간 계약 여부.
5. 설정 코드화: 설정 파일을 저장소에서 검토·되돌릴 수 있는지.
6. 감사·권한: SSO, 역할별 권한, 감사 기록(유료 등급에만 있는 경우가 많음).
7. 이전 비용: 기존 Pipeline 수와 플러그인·스크립트 의존도.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Jenkins 설치](./jenkins_install.md) — Docker·JCasC·백업 시험
- [GitLab CI/CD](./gitlab_ci.md) — Runner 등록과 검증
- [Harness](./harness_inc.md) — CD 플랫폼
- [아티팩트 저장소 비교](./artifact_repository_comparison.md) — CI와 CD 사이의 저장소

---

## 참고 자료

- Jenkins: [changelog-stable](https://www.jenkins.io/changelog-stable/) — ★★★☆☆
- GitLab: [pricing](https://about.gitlab.com/pricing/) · [Runner](https://docs.gitlab.com/runner/) — ★★★☆☆
- TeamCity: [Licensing Policy](https://www.jetbrains.com/help/teamcity/licensing-policy.html) · [Kotlin DSL](https://www.jetbrains.com/help/teamcity/kotlin-dsl.html) — ★★★☆☆
- CircleCI: [Pricing](https://circleci.com/pricing/) · [Configuration Reference](https://circleci.com/docs/reference/configuration-reference/) — ★★★☆☆
- Buildkite: [Pricing](https://buildkite.com/pricing) · [Pipelines](https://buildkite.com/docs/pipelines) — ★★★☆☆
- Octopus Deploy: [Pricing](https://octopus.com/pricing) · [Docs](https://octopus.com/docs) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-26

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
