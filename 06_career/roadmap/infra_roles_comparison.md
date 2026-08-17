# 인프라 직군 비교 — DevOps, Cloud, SRE, SE, Platform, MLOps

인프라/운영 관련 직군의 역할, 도구, 커리어 경로를 비교합니다.

## 목차

| 섹션                                                                                 |
|--------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 직군 비교](#2-직군-비교) / [3. 영역별 분류](#3-영역별-분류) |
| [4. 최근 등장 역할](#4-최근-등장-역할) / [5. 도구 비교](#5-도구-비교)                |
| [6. SysAdmin vs SRE](#6-sysadmin-vs-sre) / [7. 한국 채용 시장](#7-한국-채용-시장)    |
| [8. 커리어 전환 경로](#8-커리어-전환-경로)                                           |

---

## 1. 개요

인프라 직군은 서비스의 설계·구축·배포·운영 전 과정에 걸쳐 있습니다. 클라우드 전환, 컨테이너화, AI/ML 확산에 따라 역할이 세분화되고 있으며, 각 직군의 경계는 회사 규모와 조직 문화에 따라 다릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 직군 비교

### 핵심 역할 비교

| 직군                        | 핵심 역할                 | 주요 키워드                               |
|-----------------------------|---------------------------|-------------------------------------------|
| System Engineer (SE)        | 서버/OS 설계/구축         | HW 사이징, OS, 미들웨어, SI               |
| Network Engineer (NE)       | 네트워크 설계/운영        | L2/L3, 방화벽, VPN, BGP, SD-WAN           |
| Storage Engineer            | 스토리지/백업 설계/운영   | SAN, NAS, RAID, 복제, DR                  |
| Database Administrator(DBA) | DB 설계/운영/튜닝         | 쿼리 최적화, HA, 백업/복구                |
| Security Engineer           | 보안 설계/운영            | WAF, IDS/IPS, 취약점, 컴플라이언스        |
| Cloud Engineer              | 클라우드 인프라 설계/운영 | AWS, Azure, GCP, IaC                      |
| DevOps Engineer             | CI/CD, 배포 자동화        | Jenkins, ArgoCD, GitOps                   |
| SRE                         | 서비스 안정성 엔지니어링  | SLO, 에러 버짓, On-call, Observability    |
| SysAdmin                    | 서버/인프라 일상 운영     | 패치, 백업, 모니터링, 장애 대응           |
| Platform Engineer           | 개발자용 내부 플랫폼 구축 | IDP, K8s, Self-service, Golden Path       |
| FinOps Engineer             | 클라우드 비용 최적화      | 비용 가시화, RI/SP, 태깅, Chargeback      |
| MLOps Engineer              | ML 모델 배포/운영 자동화  | ML Pipeline, Feature Store, Model Serving |
| Virtualization Engineer     | 가상화 인프라 설계/운영   | VMware, Hyper-V, Proxmox                  |
| IT Operations (ITOM)        | ITSM 기반 운영 관리       | ITIL, 변경관리, 인시던트, CMDB            |


### System Engineer 상세

IT System Engineer는 서버/네트워크/스토리지 등 인프라를 설계·구축하는 역할입니다. INCOSE가 정의하는 Systems Engineering(복합 시스템의 수명주기 전반을 관리하는 학제간 분야)과는 구분됩니다.

| 항목        | 내용                                                       |
|-------------|------------------------------------------------------------|
| 정의        | 서버/OS/미들웨어 인프라를 설계·구축·인수인계하는 엔지니어  |
| 관여 시점   | 프로젝트 초기(설계) ~ 구축 완료(인수인계)                  |
| 주요 업무   | HW 사이징, OS 설치/hardening, 미들웨어 구성, HA/DR 설계    |
| 성능 업무   | 벤치마크, 부하 테스트, 커널/DB 파라미터 튜닝               |
| 인수인계    | 운영팀(SysAdmin)에 구축 결과물 전달, 운영 매뉴얼 작성      |
| 주요 자격증 | RHCE, LPIC-2/3, VCP, AWS SAA/SAP, MCSE (legacy)            |
| 경력 경로   | SE → Cloud Architect, SE → SRE, SE → Pre-sales Engineer    |
| 한국 현실   | SI 프로젝트 구축 인력, MSP 마이그레이션 담당으로 가장 많음 |

### 목표/초점 비교 (주요 5개 직군)

| 구분        | DevOps                     | Cloud                     | SRE                            | SE                    | Platform                  |
|-------------|----------------------------|---------------------------|--------------------------------|-----------------------|---------------------------|
| 핵심 목표   | 개발↔운영 사이클 자동화    | 클라우드 인프라 설계/운영 | 안정성 + 가용성 보장           | 인프라 설계/구축      | 개발자 생산성 향상        |
| 주요 초점   | CI/CD, 배포 속도           | 아키텍처, 비용 최적화     | SLO, 장애 대응, 용량 계획      | HW/OS/미들웨어 설계   | Self-service, Golden Path |
| 자동화 대상 | 빌드/테스트/배포           | 인프라 프로비저닝 (IaC)   | toil elimination               | 구축 자동화 (Ansible) | 개발자 워크플로우 전체    |
| 코드 비중   | 높음                       | 중간                      | 중~높음                        | 낮~중간               | 높음                      |
| 장애 대응   | 배포 롤백, 파이프라인 복구 | 인프라 레벨 장애 대응     | On-call, 포스트모템, 에러 버짓 | 구축 단계 이슈 해결   | 플랫폼 장애 대응          |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영역별 분류

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Infra Role Categories                          │
├──────────────────┬───────────────────┬───────────────────────────────┤
│  Physical Layer  │  Platform Layer   │        Service Layer          │
│                  │                   │                               │
│ System Engineer  │ Cloud Engineer    │ DevOps Engineer               │
│ Network Engineer │ Platform Engineer │ SRE                           │
│ Storage Engineer │ Virtualization    │ FinOps Engineer               │
│                  │ DBA               │ MLOps Engineer                │
│                  │ Security Engineer │ IT Operations                 │
└──────────────────┴───────────────────┴───────────────────────────────┘
```

### 서비스 라이프사이클 기준

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Service Lifecycle                              │
├─────────────┬────────────────────┬───────────────────────────────────┤
│   Design    │      Deploy        │            Operate                │
│             │                    │                                   │
│  SE / NE    │  DevOps Engineer   │  SRE / SysAdmin                   │
│  Cloud Eng  │  Cloud Engineer    │  FinOps                           │
│  DBA        │  Platform Eng      │  IT Operations                    │
│             │  MLOps             │                                   │
└─────────────┴────────────────────┴───────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 최근 등장 역할

### 2020년 이후 성장 역할

🟡 검증 불가 — 출처 필요: 아래 성장 시기와 Gartner 선정 여부는 공식 출처 링크가 없어 확인할 수 없습니다.

| 직군                    | 등장 배경                             | 성장 시기 | 비고                       |
|-------------------------|---------------------------------------|-----------|----------------------------|
| Platform Engineer       | DevOps 성숙 → 셀프서비스 플랫폼 필요  | 2022~현재 | Gartner 2024 Top 10 선정   |
| FinOps Engineer         | 클라우드 비용 폭증 → 전문 최적화 필요 | 2021~현재 | FinOps Foundation 설립     |
| MLOps Engineer          | ML 모델 배포/운영 자동화 필요         | 2020~현재 | AI 인프라 전담             |
| Edge/IoT Infra Engineer | 엣지 컴퓨팅, 5G, IoT 디바이스 인프라  | 2021~현재 | 제조/통신 분야             |
| Chaos Engineer          | 장애 주입으로 안정성 검증             | 2019~현재 | SRE 확장, Netflix 기원     |
| GitOps Engineer         | Git 기반 인프라/배포 선언적 관리      | 2020~현재 | DevOps 세분화, ArgoCD/Flux |

### MLOps Engineer 상세

| 항목        | 내용                                                    |
|-------------|---------------------------------------------------------|
| 핵심 역할   | ML 모델의 학습/배포/모니터링 파이프라인 자동화          |
| 주요 도구   | MLflow, Kubeflow, SageMaker, Vertex AI, Airflow         |
| 필요 기술   | Python, K8s, CI/CD, ML 기초, 데이터 파이프라인          |
| DevOps 차이 | 배포 대상이 코드가 아닌 **모델** (버전관리, A/B 테스트) |
| 인프라 요소 | GPU 클러스터, Feature Store, Model Registry             |

### Platform Engineer 상세

| 항목        | 내용                                                     |
|-------------|----------------------------------------------------------|
| 핵심 역할   | 내부 개발자 플랫폼(IDP) 구축 및 운영                     |
| 주요 도구   | Backstage, Crossplane, K8s, Terraform, ArgoCD            |
| 필요 기술   | K8s, IaC, API 설계, UX 관점                              |
| DevOps 차이 | DevOps "팀마다 직접" → Platform "셀프서비스 제공"        |
| 산출물      | Golden Path, 내부 포털, 템플릿, 자동화된 환경 프로비저닝 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 도구 비교

| 영역     | DevOps                  | Cloud                | SRE                     | Platform              | MLOps                |
|----------|-------------------------|----------------------|-------------------------|-----------------------|----------------------|
| IaC      | Terraform (연동)        | Terraform, CFn       | Terraform, Ansible      | Crossplane, Terraform | Terraform (GPU)      |
| CI/CD    | Jenkins, GitHub Actions | CodePipeline         | 배포 검증               | ArgoCD, Tekton        | Kubeflow Pipelines   |
| 모니터링 | DORA 메트릭             | CloudWatch, Cost Exp | Prometheus, Grafana, PD | 플랫폼 메트릭         | MLflow, Evidently    |
| 컨테이너 | Docker, K8s 배포        | EKS/ECS 설계         | K8s 운영, 노드 관리     | K8s 추상화            | K8s + GPU scheduling |
| 스크립팅 | Python, Bash, Groovy    | Python, Bash         | Python, Bash, Go        | Go, Python            | Python               |

[⬆ 목차로 돌아가기](#목차)

---

## 6. SysAdmin vs SRE

| 구분      | 전통 SysAdmin          | SRE (Google 방식)                  |
|-----------|------------------------|------------------------------------|
| 철학      | "안정적으로 유지"      | "소프트웨어로 운영 문제 해결"      |
| 장애 대응 | 수동 복구, 경험 기반   | 에러 버짓, 포스트모템, 자동 복구   |
| 확장 방식 | 인력 추가              | 자동화로 toil 제거                 |
| 변경 태도 | 보수적 (변경 = 리스크) | 에러 버짓 내 변경 허용             |
| 코드      | 스크립트 위주          | 프로덕션 수준 자동화 코드          |
| 지표      | 가동률 (uptime %)      | SLI/SLO/에러 버짓                  |
| 배포 참여 | 별도 (운영만)          | 배포 파이프라인 공동 소유          |
| On-call   | 무한 대응              | toil 50% 상한, 초과 시 개발팀 이관 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 한국 채용 시장

### 채용 빈도 (2024~2026 기준)

🟡 검증 불가 — 출처 필요: 아래 한국 채용 빈도는 채용 데이터 출처가 없어 확인할 수 없습니다.

| 빈도      | 직군                                              |
|-----------|---------------------------------------------------|
| 매우 많음 | System Engineer, Network Engineer, Cloud Engineer |
| 많음      | DBA, DevOps, Security Engineer, SysAdmin          |
| 보통      | SRE, Storage Engineer, Virtualization             |
| 소수      | Platform Engineer, FinOps, MLOps, Chaos Engineer  |

### 직군별 주요 채용처

| 직군              | 주요 채용처                                |
|-------------------|--------------------------------------------|
| System Engineer   | SI (삼성SDS, LG CNS), MSP (메가존, 베스핀) |
| Network Engineer  | 통신사 (KT, SKB), IDC, 대기업 전산실       |
| Cloud Engineer    | MSP, SaaS 기업, 금융/게임사                |
| DevOps            | 스타트업, 테크 기업, SaaS                  |
| SRE               | 네이버, 카카오, 쿠팡, 배달의민족           |
| DBA               | 금융, 게임, SI                             |
| Platform Engineer | 대형 테크 기업 (소수)                      |
| MLOps             | AI 스타트업, 네이버/카카오 AI 조직         |

### 회사 규모별 역할 배분

| 회사 규모 | 현실                                                   |
|-----------|--------------------------------------------------------|
| 스타트업  | 한 명이 DevOps + Cloud + SRE 전부 수행                 |
| 중견      | DevOps/Cloud 합쳐서 "인프라팀", SRE는 별도 또는 미분리 |
| 대기업    | 각 역할 명확 분리, 전담팀 운영                         |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 커리어 전환 경로

### 일반적 전환 흐름

```
System Engineer ──→ Cloud Engineer ──→ SRE / Platform Engineer
                                   └─→ FinOps Engineer

Network Engineer ──→ Cloud Engineer (networking)
                 └─→ Security Engineer

SysAdmin ──→ DevOps Engineer ──→ SRE
         └─→ Cloud Engineer

DBA ──→ Cloud DBA ──→ Data Engineer

DevOps Engineer ──→ Platform Engineer
                └─→ SRE

ML Engineer ──→ MLOps Engineer
```

### 전환 시 필요 기술

| 전환 경로         | 추가 학습 필요 영역                        |
|-------------------|--------------------------------------------|
| SE → Cloud        | IaC (Terraform), 클라우드 서비스, 네트워킹 |
| SysAdmin → DevOps | CI/CD, Git, 컨테이너, 스크립팅 심화        |
| DevOps → SRE      | SLO 설계, Observability, 포스트모템 문화   |
| DevOps → Platform | API 설계, UX 관점, Backstage/Crossplane    |
| Cloud → FinOps    | 비용 분석, 태깅 전략, 예약 인스턴스 최적화 |
| DevOps → MLOps    | ML 기초, 모델 서빙, Feature Store          |

### 공통 기반 기술

모든 인프라 직군에서 공통으로 요구되는 기술입니다.

| 기술              | 중요도 |
|-------------------|--------|
| Linux             | ★★★★★  |
| Networking 기초   | ★★★★☆  |
| IaC (Terraform)   | ★★★★☆  |
| 컨테이너 (Docker) | ★★★★☆  |
| 스크립팅 (Python) | ★★★★☆  |
| Git               | ★★★★☆  |
| 모니터링/로깅     | ★★★☆☆  |
| 클라우드 1개 이상 | ★★★★☆  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Google SRE Book: [sre.google/sre-book](https://sre.google/sre-book/table-of-contents/) — ★★★★☆
- Platform Engineering: [platformengineering.org](https://platformengineering.org/) — ★★☆☆☆
- FinOps Foundation: [finops.org](https://www.finops.org/) — ★★☆☆☆
- MLOps Community: [mlops.community](https://mlops.community/) — ★★☆☆☆
- Gartner Top Strategic Technology Trends 2024 — Platform Engineering
- [se_roadmap.md](./se_roadmap.md)
- [sre_roadmap.md](./sre_roadmap.md)
- [dba_roadmap.md](./dba_roadmap.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-24

**마지막 업데이트**: 2026-07-24

© 2026 siasia86. Licensed under CC BY 4.0.
