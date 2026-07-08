# Tech Debt Management

기술 부채를 체계적으로 분류, 측정, 상환하여 장기적 시스템 건강성을 유지하는 프레임워크입니다. Ward Cunningham의 원래 메타포(1992)와 Martin Fowler의 분류를 기반으로 합니다.

## 목차

| 섹션                                                                                           |
|------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 분류](#2-분류) / [3. 측정](#3-측정)                                   |
| [4. 상환 우선순위](#4-상환-우선순위) / [5. 예방](#5-예방) / [6. 커뮤니케이션](#6-커뮤니케이션) |
| [7. 도구](#7-도구) / [8. 안티패턴](#8-안티패턴) / [9. 트러블슈팅](#9-트러블슈팅)               |

## 1. 개요

| 항목 | 값                                                                   |
|------|----------------------------------------------------------------------|
| 정의 | 빠른 배포를 위해 선택한 차선책이 누적되어 발생하는 유지보수 비용     |
| 출처 | Ward Cunningham (1992 OOPSLA), Martin Fowler Technical Debt Quadrant |
| 핵심 | 부채는 피할 수 없음 — 관리가 목표                                    |
| 비유 | 금융 부채와 동일: 원금(코드) + 이자(유지비용)                        |
| 연관 | Change Management (변경 비용), Platform Engineering (표준화)         |

## 2. 분류

### Fowler의 Tech Debt Quadrant

| 구분            | Deliberate (의도적)         | Inadvertent (비의도적)         |
|-----------------|-----------------------------|--------------------------------|
| Reckless (무모) | "시간 없으니 설계 생략"     | "계층화가 뭔지 몰랐음"         |
| Prudent (신중)  | "지금 출시하고 나중에 개선" | "이제야 더 나은 방법을 알겠음" |

> Martin Fowler의 Technical Debt Quadrant(2009)에서 정의한 2x2 매트릭스입니다.
> — https://martinfowler.com/bliki/TechnicalDebtQuadrant.html

### 부채 유형별 분류

| 유형                | 예시                              | 영향           |
|---------------------|-----------------------------------|----------------|
| Code Debt           | 중복 코드, 긴 메서드, 네이밍 불량 | 변경 속도 저하 |
| Architecture Debt   | 모놀리스 고착, 순환 의존성        | 확장성 제한    |
| Test Debt           | 테스트 커버리지 부족, 깨진 테스트 | 회귀 버그 증가 |
| Documentation Debt  | 문서 부재/미갱신                  | 온보딩 지연    |
| Infrastructure Debt | EOL OS, 패치 미적용               | 보안 취약점    |
| Dependency Debt     | 오래된 라이브러리, 취약 버전      | CVE 노출       |

## 3. 측정

### 정량적 지표

| 지표                       | 측정 방법                | 도구                   |
|----------------------------|--------------------------|------------------------|
| Code Coverage              | 테스트 라인 커버리지 %   | SonarQube, Codecov     |
| Cyclomatic Complexity      | 분기 수 기반 복잡도      | SonarQube, CodeClimate |
| Dependency Age             | 최신 버전 대비 경과 기간 | Renovate, Dependabot   |
| MTTR (Mean Time to Repair) | 변경 후 복구까지 시간    | DORA metrics           |
| Lead Time for Changes      | 커밋~배포 시간           | DORA metrics           |

> DORA 4 Key Metrics(Deployment Frequency, Lead Time, Change Failure Rate, MTTR)는 "Accelerate" 연구(2018)에서 정립되었습니다.
> — https://dora.dev/guides/dora-metrics-four-keys/

### 정성적 지표

| 지표                   | 측정 방법                  |
|------------------------|----------------------------|
| Developer Satisfaction | 분기별 설문 (1~5점)        |
| Cognitive Load         | 팀별 담당 도메인 수        |
| On-boarding Time       | 신규 입사자 첫 PR까지 일수 |
| Change Failure Rate    | 배포 중 롤백/핫픽스 비율   |

## 4. 상환 우선순위

### 우선순위 매트릭스

| 기준          | 높음                   | 낮음          |
|---------------|------------------------|---------------|
| 변경 빈도     | 자주 수정하는 코드     | 안정된 레거시 |
| 비즈니스 영향 | 수익 직결 서비스       | 내부 도구     |
| 보안 위험     | CVE 노출, 인증 관련    | 스타일 이슈   |
| 팀 고통       | 매번 작업 시 고통 유발 | 가끔 불편     |

### 상환 전략

| 전략              | 적용 시점              | 예시                      |
|-------------------|------------------------|---------------------------|
| Boy Scout Rule    | 매 커밋 시 (작은 개선) | 리네이밍, 중복 제거       |
| 20% Time          | 스프린트 내 고정 할당  | 매주 금요일 부채 상환     |
| Dedicated Sprint  | 분기별 1스프린트       | 대규모 리팩토링           |
| Strangler Pattern | 점진적 교체            | 모놀리스 → 마이크로서비스 |

> Strangler Fig Pattern은 Martin Fowler(2004)가 제안했습니다. "20% Time"은 Google의 엔지니어링 문화에서 유래한 개념입니다.
> — https://martinfowler.com/bliki/StranglerFigApplication.html

### 상환하지 말아야 할 경우

- 곧 폐기될 시스템
- 변경 빈도가 0에 가까운 코드
- 상환 비용 > 잔여 이자 총합

## 5. 예방

### 예방 활동

| 활동                               | 주기          | 효과                        |
|------------------------------------|---------------|-----------------------------|
| Code Review                        | 매 PR         | Reckless debt 유입 차단     |
| Architecture Review                | 분기          | Architecture debt 조기 발견 |
| Dependency Update                  | 주간          | Dependency debt 누적 방지   |
| Lint/SAST                          | CI 파이프라인 | Code debt 자동 탐지         |
| ADR (Architecture Decision Record) | 변경 시       | 의사결정 맥락 보존          |

> Thoughtworks Technology Radar에서 Lightweight ADR을 "Adopt"로 선정(2016)했습니다. CI 파이프라인의 SAST/Lint gate는 OWASP DevSecOps Guideline의 핵심 실천입니다.
> — https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records

## 6. 커뮤니케이션

### 경영진 보고 방법

| 항목      | 표현 방법                                      |
|-----------|------------------------------------------------|
| 부채 규모 | "현재 변경 시간의 30%가 기존 부채 대응에 소모" |
| 이자 비용 | "월 N시간의 엔지니어링 시간 = 약 "             |
| 상환 계획 | "분기당 1스프린트 투자 → 6개월 후 30% 감소"    |
| 리스크    | "미상환 시 보안 사고 확률 증가"                |

### Tech Debt Register (부채 장부)

| 필드     | 설명                                    |
|----------|-----------------------------------------|
| ID       | 고유 식별자                             |
| Title    | 부채 제목                               |
| Type     | Code/Architecture/Test/Infra/Dependency |
| Impact   | High/Medium/Low                         |
| Interest | 월간 추가 비용 (시간)                   |
| Payoff   | 상환 예상 비용 (시간)                   |
| Owner    | 담당 팀                                 |
| Priority | 상환 우선순위                           |

## 7. 도구

| 도구                   | 유형        | 특징                           |
|------------------------|-------------|--------------------------------|
| SonarQube              | 코드 품질   | 복잡도, 중복, 커버리지, 취약점 |
| CodeClimate            | 코드 품질   | Maintainability Index, GPA     |
| Renovate               | 의존성 관리 | 자동 PR 생성, 그룹핑           |
| Dependabot             | 의존성 관리 | GitHub 네이티브, 보안 알림     |
| Backstage TechInsights | 스코어카드  | 팀별 표준 준수 점수            |

> SonarQube의 "Technical Debt" 메트릭은 수정에 필요한 예상 시간(effort)으로 측정됩니다. Backstage는 Spotify가 개발한 CNCF Incubating 프로젝트입니다.
> — https://docs.sonarsource.com/sonarqube/latest/user-guide/metric-definitions/
> — https://www.cncf.io/projects/backstage/

## 8. 안티패턴

| 안티패턴                    | 문제                       | 올바른 접근             |
|-----------------------------|----------------------------|-------------------------|
| "나중에 하자" (무기한 연기) | 이자 복리 증가             | 정기 상환 스프린트 예약 |
| Big Bang 리팩토링           | 리스크 높음, 비즈니스 중단 | 점진적 Strangler 패턴   |
| 부채 무시 (측정 안 함)      | 보이지 않아 악화           | 정량 측정 + 대시보드    |
| 부채 = 나쁜 것 (죄악시)     | 의도적 부채도 필요         | Prudent/Deliberate 구분 |
| 상환만 하고 예방 안 함      | 유입 속도 > 상환 속도      | CI gate + review 강화   |

## 9. 트러블슈팅

| 증상                      | 원인                 | 해결                                     |
|---------------------------|----------------------|------------------------------------------|
| 배포 속도 계속 저하       | 코드 복잡도 누적     | 복잡도 임계값 설정 + CI gate             |
| 신규 입사자 온보딩 3개월+ | 문서 부재, 코드 난해 | Documentation debt 우선 상환             |
| 같은 버그 반복 발생       | Test debt            | 커버리지 목표 설정 + 회귀 테스트 추가    |
| 보안 취약점 반복 보고     | Dependency debt      | Renovate/Dependabot 도입 + 주간 업데이트 |
| 상환 시간 확보 불가       | 경영진 이해 부족     | 이자 비용 정량화 + 비즈니스 영향 보고    |

> 기술 부채(Technical Debt) 개념은 Ward Cunningham(1992)이 최초 제안했습니다. Martin Fowler의 Technical Debt Quadrant(2009)가 분류 체계로 널리 사용됩니다.
> — https://martinfowler.com/bliki/TechnicalDebtQuadrant.html
> — Cunningham, Ward. "The WyCash Portfolio Management System" (OOPSLA 1992)

## 참고 자료

- Martin Fowler: [TechnicalDebt](https://martinfowler.com/bliki/TechnicalDebt.html) — ★★☆☆☆
- Martin Fowler: [TechnicalDebtQuadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html) — ★★☆☆☆
- Cunningham, W. "The WyCash Portfolio Management System" (1992 OOPSLA)
- DORA: [dora.dev](https://dora.dev/) — ★★★☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
