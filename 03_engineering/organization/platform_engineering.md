# Platform Engineering

내부 개발자 플랫폼(IDP)을 설계하고 운영하여 제품 팀의 인지 부하를 줄이고 셀프서비스 인프라를 제공하는 엔지니어링 분야입니다. CNCF Platforms White Paper를 기반으로 합니다.

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 왜 플랫폼인가](#2-왜-플랫폼인가) / [3. 플랫폼 속성](#3-플랫폼-속성)               |
| [4. 플랫폼 팀](#4-플랫폼-팀) / [5. Golden Path](#5-golden-path) / [6. 셀프서비스 설계](#6-셀프서비스-설계) |
| [7. 성숙도 모델](#7-성숙도-모델) / [8. 도입 전략](#8-도입-전략) / [9. 트러블슈팅](#9-트러블슈팅)           |

## 1. 개요

| 항목 | 값                                                           |
|------|--------------------------------------------------------------|
| 정의 | 내부 사용자의 요구에 맞춰 정의된 통합 역량 컬렉션 (CNCF WP)  |
| 출처 | CNCF Platforms White Paper (TAG App Delivery)                |
| 핵심 | Self-service, Golden Path, Platform as a Product             |
| 목표 | 인지 부하 감소 + 배포 속도 향상 + 거버넌스 내재화            |
| 연관 | Team Topology (팀 구조), SLO (플랫폼 SLI), Capacity Planning |

## 2. 왜 플랫폼인가

### CNCF가 제시하는 5대 가치

| 번호 | 가치               | 설명                                       |
|------|--------------------|--------------------------------------------|
| 1    | 인지 부하 감소     | 제품 팀이 인프라 대신 비즈니스 로직에 집중 |
| 2    | 신뢰성/회복력 향상 | 전문가가 플랫폼 역량을 전담 관리           |
| 3    | 배포 속도 향상     | 도구/지식을 여러 팀에 재사용               |
| 4    | 리스크 감소        | 보안/규정 준수/기능 이슈를 거버넌스로 제어 |
| 5    | 클라우드 비용 효율 | 관리형 서비스 위임 + UX 통제 유지          |

### 플랫폼이 필요하지 않은 경우

| 상황                    | 이유                              |
|-------------------------|-----------------------------------|
| 팀이 3개 미만           | 오버헤드가 가치를 초과            |
| 기술 스택이 완전히 동일 | 공유 라이브러리로 충분            |
| 관리형 PaaS를 이미 사용 | Heroku, Vercel 등이 IDP 역할 수행 |

## 3. 플랫폼 속성

### CNCF 7대 속성

| 번호 | 속성                  | 설명                                        |
|------|-----------------------|---------------------------------------------|
| 1    | Platform as a Product | 사용자 요구 기반 설계, 로드맵 운영          |
| 2    | User Experience       | GUI, API, CLI, IDE, 포탈 등 다중 인터페이스 |
| 3    | Documentation         | Golden Path + 온보딩 문서 + 예제 제공       |
| 4    | Self-service          | 온디맨드, 최소 수동 개입, 자동화            |
| 5    | Cognitive Load 감소   | 구현 세부사항 캡슐화, 복잡도 은닉           |
| 6    | Optional/Composable   | 부분 사용 가능, 팀 자체 역량 허용           |
| 7    | Secure by Default     | 규정 준수/검증을 기본 내장                  |

## 4. 플랫폼 팀

### 책임 (CNCF WP)

| 번호 | 책임                 | 활동 예시                         |
|------|----------------------|-----------------------------------|
| 1    | 사용자 요구사항 조사 | 인터뷰, 해커톤, 이슈 트래커, 설문 |
| 2    | 플랫폼 가치 전파     | 데모, 공지, 피드백 세션           |
| 3    | 인터페이스 개발/관리 | 포탈, API, 문서, 템플릿, CLI      |

### 플랫폼 팀이 하지 않는 것

| 항목                | 설명                                     |
|---------------------|------------------------------------------|
| 인프라 직접 운영    | 관리형 서비스 또는 인프라 팀에 위임      |
| 비즈니스 로직 개발  | 제품 팀 영역                             |
| 모든 도구 자체 구현 | 외부 서비스 활용 + 얇은 UX 레이어만 관리 |

## 5. Golden Path

### 정의

CNCF WP에서의 정의: "a bundle often described as a golden path" — 빌드, 스캔, 테스트, 배포, 관측을 포함하는 재사용 가능한 워크플로우 + 초기 프로젝트 템플릿 + 문서입니다.

### 구성 요소

| 요소             | 예시                                    |
|------------------|-----------------------------------------|
| Project Template | cookiecutter, Backstage scaffolder      |
| CI/CD Pipeline   | 사전 구성된 빌드/테스트/배포 파이프라인 |
| Infra Template   | Terraform module, Helm chart            |
| Observability    | 자동 계측, 표준 대시보드                |
| Documentation    | ADR, 런북, 아키텍처 가이드              |

### Golden Path vs Paved Road

| 용어        | 의미                            |
|-------------|---------------------------------|
| Golden Path | 권장 경로 (Backstage/CNCF 용어) |
| Paved Road  | 같은 개념 (Netflix 용어)        |
| 핵심 차이   | 없음 — 동일 개념의 다른 표현    |

## 6. 셀프서비스 설계

### 셀프서비스 수준

| 수준       | 인터페이스       | 자동화 정도 | 예시                 |
|------------|------------------|-------------|----------------------|
| L1 Wiki    | 문서 + 수동 요청 | 없음        | Confluence 가이드    |
| L2 Ticket  | 티켓 기반 요청   | 부분 자동화 | Jira + Terraform run |
| L3 Portal  | 웹 UI 폼 제출    | 대부분 자동 | Backstage, Port      |
| L4 API/CLI | API 직접 호출    | 전체 자동   | kubectl, CLI tool    |
| L5 GitOps  | PR 기반 선언적   | 전체 자동   | ArgoCD + Crossplane  |

### 주요 IDP 도구

| 도구       | 유형               | 특징                            |
|------------|--------------------|---------------------------------|
| Backstage  | Developer Portal   | Spotify OSS, 플러그인 생태계    |
| Port       | SaaS Portal        | Self-service actions, Scorecard |
| Crossplane | IaC Abstraction    | K8s CRD 기반 인프라 프로비저닝  |
| Kratix     | Platform Framework | Promise 패턴, GitOps 네이티브   |
| Humanitec  | SaaS Platform      | Score 워크로드 명세, 환경 관리  |

## 7. 성숙도 모델

### CNCF Platform Maturity (5 Level)

| 레벨 | 이름        | 역량                                                      |
|------|-------------|-----------------------------------------------------------|
| L1   | Provisional | 개별 역량 온디맨드 프로비저닝 (compute, DB, identity)     |
| L2   | Managed     | 서비스 공간 프로비저닝 (파이프라인, 아티팩트, 텔레메트리) |
| L3   | Scalable    | 서드파티 소프트웨어 + 의존성 자동 프로비저닝              |
| L4   | Optimizing  | 템플릿 기반 전체 환경 프로비저닝 (web dev, MLOps)         |
| L5   | Innovating  | 자동 계측 + 기능/성능/비용 관측                           |

## 8. 도입 전략

### 단계별 접근

| 단계 | 기간     | 목표                                 | 산출물                         |
|------|----------|--------------------------------------|--------------------------------|
| 1    | 0~3개월  | 파일럿 팀 1개 + 핵심 Pain Point 식별 | 사용자 인터뷰, 우선순위 백로그 |
| 2    | 3~6개월  | Golden Path v1 + 셀프서비스 MVP      | Backstage 카탈로그, 템플릿 1종 |
| 3    | 6~12개월 | 3~5개 팀 확장 + 피드백 루프          | SLI/SLO, 만족도 설문           |
| 4    | 12개월+  | 전사 확산 + 거버넌스 내재화          | Scorecard, 비용 대시보드       |

### 성공 측정 (CNCF WP)

| 카테고리          | 지표 예시                        |
|-------------------|----------------------------------|
| User Satisfaction | 개발자 만족도 설문, NPS          |
| Productivity      | Lead time, Deployment frequency  |
| Org Efficiency    | 중복 도구 감소, 온보딩 시간 단축 |
| Feature Delivery  | DORA metrics 개선                |

## 9. 트러블슈팅

| 증상                  | 원인                   | 해결                                 |
|-----------------------|------------------------|--------------------------------------|
| 팀이 플랫폼을 안 씀   | Top-down 강제, UX 불량 | 사용자 피드백 반영, 데모/마케팅 강화 |
| 플랫폼 팀 과부하      | 모든 것을 자체 구현    | 관리형 서비스 위임, 범위 축소        |
| Golden Path가 안 맞음 | 팀 다양성 미반영       | 여러 Path 제공, Composable 설계      |
| 경영진 지원 부족      | 가치 증명 실패         | DORA metrics + 비용 절감 데이터 제시 |
| 셀프서비스가 느림     | 승인 프로세스 과다     | 자동 승인 규칙, Policy as Code       |

> Platform Engineering은 Team Topologies(Skelton & Pais, 2019)의 "Platform Team" 개념에서 발전했습니다. Gartner는 2023년 Top Strategic Technology Trends에 선정했습니다.
> — Skelton, Matthew & Pais, Manuel. "Team Topologies" (2019)
> — https://www.gartner.com/en/articles/gartner-top-10-strategic-technology-trends-for-2023

> Internal Developer Platform(IDP)의 핵심 요소: Self-service, Golden Path, Guardrails.
> — https://platformengineering.org/blog/what-is-platform-engineering

> CNCF Platforms White Paper(2023)에서 Platform Engineering의 정의와 best practice를 공식화했습니다.
> — https://tag-app-delivery.cncf.io/whitepapers/platforms/

> Platform as a Product 접근: 내부 개발자가 고객이며, adoption rate와 developer satisfaction이 핵심 KPI입니다.
> — Skelton & Pais. "Team Topologies" Ch.5 (2019)

## 참고 자료

- CNCF Platforms White Paper: [tag-app-delivery.cncf.io](https://tag-app-delivery.cncf.io/whitepapers/platforms/) — ★★★★☆
- CNCF Platform Maturity Model: [tag-app-delivery.cncf.io](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/) — ★★★★☆
- Backstage: [backstage.io](https://backstage.io/) — ★★★☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
