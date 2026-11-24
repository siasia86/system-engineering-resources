# 아티팩트 저장소 비교 (Nexus · Artifactory · Cloudsmith)
<!-- reference: _reference/nexus_official_notes.md, _reference/artifactory_official_notes.md, _reference/cloudsmith_official_notes.md -->

빌드 결과물과 외부 패키지 캐시를 맡길 저장소를 고르는 기준을 정리한 문서입니다. 자체 운영하는 Nexus Repository, 상용 JFrog Artifactory, SaaS 전용 Cloudsmith를 중심으로 비교하고, Git 호스팅·클라우드에 딸린 저장소도 함께 봅니다. 상용 서비스는 계정·비용 없이 확인할 수 있는 공식 문서·요금 페이지 범위만 다룹니다.

- 기준: 2026-11-24 각 공식 문서·요금 페이지, Nexus 3.98.3, Artifactory 7.173.21
- 예제 시험: Nexus는 [Nexus 문서](./nexus.md)에서 컨테이너로 시험했습니다. Artifactory·Cloudsmith는 미실행(계정과 사용권이 필요). 요금은 바뀔 수 있으므로 결정 전에 공식 요금 페이지를 다시 확인합니다

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 왜 필요한가](#1-왜-필요한가) / [2. 한눈에 비교](#2-한눈에-비교) / [3. 비용 구조](#3-비용-구조) |
| [4. 그 밖의 선택지](#4-그-밖의-선택지) / [5. 고르는 기준](#5-고르는-기준)                          |
| [6. 도입 전 확인](#6-도입-전-확인) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)             |

---

## 1. 왜 필요한가

| 문제                                       | 저장소가 하는 일                                   |
|--------------------------------------------|----------------------------------------------------|
| 같은 커밋을 다시 빌드해도 결과가 달라짐    | 한 번 빌드한 결과물을 판 번호로 보관해 그대로 배포 |
| 외부 저장소 장애·요청 제한으로 빌드가 멈춤 | 외부 패키지를 캐시해 두 번째부터는 내부에서 제공   |
| 사내 패키지 이름이 공개 저장소와 겹침      | 내부 저장소를 먼저 조회하도록 순서 고정            |
| 어떤 판이 어디에 배포됐는지 추적 어려움    | 결과물·메타데이터·다운로드 기록을 한곳에 모음      |

세 제품은 같은 개념을 다른 이름으로 부릅니다.

| 개념                | Nexus  | Artifactory | Cloudsmith                       |
|---------------------|--------|-------------|----------------------------------|
| 직접 올린 결과물    | hosted | local       | 저장소 (repository)              |
| 외부 저장소 캐시    | proxy  | remote      | 업스트림 (upstream)              |
| 여러 저장소 한 주소 | group  | virtual     | 저장소 하나에 여러 형식·업스트림 |
| 사이트 간 동기화    | 없음   | federated   | 해당 없음 (SaaS 엣지 배포)       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 항목        | Nexus Repository                                                | JFrog Artifactory                      | Cloudsmith                               |
|-------------|-----------------------------------------------------------------|----------------------------------------|------------------------------------------|
| 운영 형태   | 자체 호스팅 (Pro는 Cloud 배포도 있음)                           | SaaS 또는 자체 관리                    | SaaS 전용                                |
| 무료 판     | Community Edition (컴포넌트 40,000개, 하루 요청 100,000건 한도) | OSS, Container Registry(온프레미스)    | Core 요금제, 오픈소스 저장소 무료 허용량 |
| 지원 형식   | 27개 (Maven·npm·PyPI·Docker·APT·Yum 등)                         | 60개 이상 (제품 페이지 표기)           | 34개                                     |
| 캐시 프록시 | proxy 저장소                                                    | remote 저장소                          | 업스트림 (24개 형식 캐시)                |
| 다중 사이트 | Pro 이상 HA, CE 없음                                            | federated (Enterprise X 이상, 7.18.3+) | 엣지 캐시로 전 세계 배포                 |
| DB          | H2(소규모) 또는 PostgreSQL                                      | 자체 관리 시 직접 준비                 | 해당 없음                                |
| 외부 배포   | 익명·사용자 권한으로 공개 가능                                  | 권한·토큰                              | 엔타이틀먼트 토큰(고객별 읽기 토큰)      |
| 운영 부담   | 서버·DB·백업·업그레이드 직접                                    | SaaS는 낮음, 자체 관리는 직접          | 낮음 (서버 없음)                         |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 비용 구조

| 제품                  | 과금 방식                                        | 확인한 가격 (2026-11-24)                                                       |
|-----------------------|--------------------------------------------------|--------------------------------------------------------------------------------|
| Nexus CE              | 무료 (사용량 한도 안에서)                        | 서버·DB·인력 비용만                                                            |
| Nexus Pro 이상        | 사용량 기반 계약                                 | 금액은 확인하지 않음                                                           |
| Artifactory SaaS      | 월 구독 + 기본 사용량 초과분                     | Pro 월 $50 (기간 한정, 정가 $150, 25GB 포함), Enterprise X 월 $950부터 (125GB) |
| Artifactory 자체 관리 | 연 계약 (서버 수 기준)                           | Pro X 연 $27,000부터 (서버 1대), Enterprise X 연 $51,000부터 (서버 3대)        |
| Cloudsmith            | 요금제(Core·Pro·Ultra·Enterprise) + 초과 GB 과금 | Core 무료. 유료 요금제 가격은 미확인(요금 페이지 접속 실패)                    |

계산할 때는 같은 기간(예: 1년)으로 맞춥니다.

| 자체 운영에 더할 항목 | 내용                                                   |
|-----------------------|--------------------------------------------------------|
| 서버·저장 공간        | 결과물은 계속 늘어남. 정리 정책 없이는 디스크가 한계   |
| DB                    | PostgreSQL 운영·백업 (Nexus 운영 구성)                 |
| 이중화                | 저장소가 멈추면 모든 빌드가 멈춤                       |
| 인력                  | 업그레이드, 보안 패치, 백업 복원 시험                  |
| 네트워크              | SaaS는 전송량 과금. 자체 운영은 사내망이면 전송비 없음 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 그 밖의 선택지

| 선택지                  | 특징                                                                    | 맞는 곳                                 |
|-------------------------|-------------------------------------------------------------------------|-----------------------------------------|
| GitHub Packages         | npm·RubyGems·Maven/Gradle·NuGet·컨테이너 레지스트리, 저장소 권한과 연동 | 코드와 CI가 GitHub에 있음               |
| GitLab Package Registry | Maven·npm·PyPI·NuGet·Helm·Generic 등, 프로젝트 권한과 연동              | GitLab 사용, 별도 서버를 두기 싫음      |
| AWS CodeArtifact        | 관리형, 저장소 하나에 여러 형식, 공개 저장소 외부 연결                  | AWS 중심, IAM으로 권한 관리             |
| Harbor                  | 컨테이너·OCI 전용 레지스트리 (CNCF 졸업 프로젝트)                       | 이미지만 다루고 취약점 검사·복제가 필요 |

Git 호스팅에 딸린 저장소는 따로 운영할 것이 없지만, 형식과 외부 캐시 기능이 전용 제품보다 좁습니다. 형식별 지원 상태는 각 공식 문서에서 다시 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 고르는 기준

| 상황                                                | 후보                                        |
|-----------------------------------------------------|---------------------------------------------|
| 비용 없이 시작, 사내망, 결과물 수가 많지 않음       | Nexus CE (운영은 PostgreSQL)                |
| 외부 연결이 막힌 망, 데이터 반출 금지               | Nexus 또는 Artifactory 자체 관리            |
| 여러 지역 사이트가 같은 결과물을 동기화해야 함      | Artifactory Enterprise X 이상 (federated)   |
| 고객에게 패키지를 배포, 운영 인력 없음              | Cloudsmith 같은 SaaS (엔타이틀먼트 토큰)    |
| 오픈소스 패키지를 공개 배포                         | Cloudsmith 오픈소스 저장소, GitHub Packages |
| 코드·CI가 이미 GitHub·GitLab에 있고 형식이 몇 개뿐  | 플랫폼 내장 레지스트리                      |
| 컨테이너 이미지만 다룸                              | Harbor, 클라우드 레지스트리                 |
| CE 한도(컴포넌트 40,000개, 하루 100,000건)에 가까움 | 정리 정책 먼저, 이후 Nexus Pro·다른 제품    |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 도입 전 확인

| 순서 | 확인 내용   | 방법                                                               | 기대 결과                              |
|------|-------------|--------------------------------------------------------------------|----------------------------------------|
| 1    | 필요한 형식 | 사용하는 패키지 관리자 목록을 만들고 각 제품 형식 문서와 대조      | 빠진 형식 없음                         |
| 2    | 사용량      | 결과물 개수·총용량·하루 요청 수 추정 (CI 실행 수 × 받는 패키지 수) | 무료 한도·요금제 허용량과 비교한 표    |
| 3    | 비용        | 3절 표에 같은 기간으로 계산                                        | 자체 운영과 SaaS 비용 비교             |
| 4    | 데이터 위치 | SaaS 리전과 사내 데이터 정책 대조                                  | 정책 위반 없음                         |
| 5    | 인증 연동   | 필요한 SSO(SAML·OIDC)·LDAP와 등급별 제공 여부 확인                 | 필요한 등급 확정 (Nexus CE는 SSO 없음) |
| 6    | 시범 운영   | 프로젝트 하나를 연결해 올리기·받기·캐시·정리를 확인                | 빌드 시간·실패율이 기존과 같거나 나음  |
| 7    | 나가는 경로 | 결과물·설정을 내보낼 수 있는지 확인 (REST, 표준 형식 그대로 받기)  | 옮길 때 다시 만들 범위를 파악          |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Nexus Repository](./nexus.md) — 설치, 저장소 만들기, 백업, 검증
- [Git 호스팅 비교](./git_hosting_comparison.md) — GitHub·GitLab·Bitbucket
- [DevOps Toolchain](./devops_toolchain.md) — 파이프라인 전체에서 저장소의 위치

---

## 참고 자료

- Sonatype Help: [Tiers and Feature Availability](https://help.sonatype.com/en/nexus-repository-tiers-and-feature-availability.html) · [Community Edition Onboarding](https://help.sonatype.com/en/ce-onboarding.html) · [Formats](https://help.sonatype.com/en/formats.html) — ★★★☆☆
- JFrog: [Pricing](https://jfrog.com/pricing/) — 2026-11-24 확인 · [Federated Repositories](https://docs.jfrog.com/artifactory/docs/federated-repositories) · [Repository Management](https://docs.jfrog.com/artifactory/docs/repository-management-overview) — ★★★☆☆
- JFrog: [Artifactory Self-Managed Releases](https://docs.jfrog.com/releases/docs/artifactory-self-managed-releases) · [Container Registry](https://jfrog.com/container-registry/) — ★★★☆☆
- Cloudsmith Docs: [Formats](https://docs.cloudsmith.com/formats) · [Upstreams](https://docs.cloudsmith.com/repositories/upstreams) · [Entitlement Tokens](https://docs.cloudsmith.com/software-distribution/entitlement-tokens) — ★★★☆☆
- Cloudsmith Docs: [Billing](https://docs.cloudsmith.com/support/billing) · [Open-Source Hosting Policy](https://docs.cloudsmith.com/resources/open-source-hosting-policy) — ★★★☆☆
- GitHub Docs: [Introduction to GitHub Packages](https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages) · GitLab Docs: [Package Registry](https://docs.gitlab.com/user/packages/package_registry/) — ★★★☆☆
- AWS: [What is CodeArtifact?](https://docs.aws.amazon.com/codeartifact/latest/ug/welcome.html) · CNCF: [Harbor](https://www.cncf.io/projects/harbor/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-24

**마지막 업데이트**: 2026-11-24

© 2026 siasia86. Licensed under CC BY 4.0.
