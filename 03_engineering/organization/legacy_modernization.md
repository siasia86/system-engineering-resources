# Legacy Modernization

레거시 시스템을 점진적으로 현대화하여 비즈니스 중단 없이 새로운 아키텍처로 전환하는 전략과 패턴입니다. Martin Fowler의 Strangler Fig Pattern을 핵심으로 합니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 현대화 전략](#2-현대화-전략) / [3. Strangler Fig Pattern](#3-strangler-fig-pattern) |
| [4. 데이터 이중 쓰기](#4-데이터-이중-쓰기) / [5. 단계별 분리](#5-단계별-분리) / [6. 검증](#6-검증)           |
| [7. 조직 고려사항](#7-조직-고려사항) / [8. 안티패턴](#8-안티패턴) / [9. 트러블슈팅](#9-트러블슈팅)           |

## 1. 개요

| 항목 | 값                                                             |
|------|----------------------------------------------------------------|
| 정의 | 레거시 시스템을 점진적으로 교체하여 리스크를 최소화하는 접근법 |
| 출처 | Martin Fowler "StranglerFigApplication" (2004)                 |
| 핵심 | Big Bang 재작성 금지 — 점진적 교체                             |
| 전제 | 레거시가 동작 중이고 비즈니스 가치를 제공하는 상태             |
| 연관 | Zero Downtime Migration (전환 기법), Tech Debt (동기)          |

### 현대화가 필요한 신호

| 신호                       | 영향                 |
|----------------------------|----------------------|
| 배포 주기 > 1개월          | 시장 대응 속도 저하  |
| 변경 실패율 > 30%          | 품질 신뢰 하락       |
| 핵심 인력 이탈/은퇴 위험   | 유지보수 불가 리스크 |
| 보안 패치 불가 (EOL 스택)  | 컴플라이언스 위반    |
| 확장 불가 (수직 확장 한계) | 비즈니스 성장 제약   |

> 배포 주기와 변경 실패율은 DORA metrics 기준으로 측정합니다.
> Low performer: 배포 주기 월 1회 미만, 변경 실패율 46~60%.
> — https://dora.dev/

## 2. 현대화 전략

### 6R 전략 (AWS)

🟡 AWS는 2022년 이후 Relocate(VMware → AWS 이전)를 추가하여 7R로 확장했습니다. 기존 6R도 여전히 널리 사용됩니다.

| 전략       | 설명                           | 적합 상황               |
|------------|--------------------------------|-------------------------|
| Rehost     | Lift & Shift (변경 없이 이전)  | 빠른 클라우드 이전 필요 |
| Replatform | Lift & Reshape (약간의 최적화) | 관리형 서비스 활용      |
| Refactor   | Re-architect (재설계)          | 클라우드 네이티브 전환  |
| Repurchase | SaaS로 교체                    | 자체 운영 부담 제거     |
| Retire     | 폐기                           | 사용되지 않는 시스템    |
| Retain     | 유지 (현재 상태)               | 변경 불필요 또는 불가   |

### 전략 선택 기준

| 기준               | Rehost | Replatform | Refactor |
|--------------------|--------|------------|----------|
| 속도               | 빠름   | 중간       | 느림     |
| 비용 (초기)        | 낮음   | 중간       | 높음     |
| 비용 (장기)        | 높음   | 중간       | 낮음     |
| 클라우드 이점 활용 | 최소   | 부분       | 최대     |
| 기술 부채 해소     | 없음   | 부분       | 대폭     |

## 3. Strangler Fig Pattern

### 개념

Martin Fowler (2004): 교살 무화과(Strangler Fig)가 숙주 나무를 서서히 감싸며 대체하듯, 레거시 시스템을 점진적으로 새 시스템으로 교체합니다.

### 구현 단계

| 단계 | 활동                            | 상태                       |
|------|---------------------------------|----------------------------|
| 1    | Facade/Proxy 배치 (라우터 역할) | 100% 트래픽 → 레거시       |
| 2    | 첫 기능 신규 서비스로 구현      | 일부 트래픽 → 신규         |
| 3    | 기능별 점진적 이전              | 점점 더 많은 트래픽 → 신규 |
| 4    | 레거시 기능 0% 도달             | 레거시 폐기                |

### Facade 패턴 구현



### 라우팅 전략

| 전략         | 방법                  | 적합 상황       |
|--------------|-----------------------|-----------------|
| Path-based   | URL 경로별 라우팅     | REST API 분리   |
| Header-based | 요청 헤더 기반 라우팅 | Canary 전환     |
| User-based   | 사용자 ID/그룹 기반   | 점진적 롤아웃   |
| Feature flag | 기능 플래그 기반      | A/B 테스트 병행 |

## 4. 데이터 이중 쓰기

### 전략 비교

| 전략                      | 정합성   | 복잡도 | 적합 상황             |
|---------------------------|----------|--------|-----------------------|
| Dual Write                | Eventual | 높음   | 양쪽 시스템 동시 운영 |
| CDC (Change Data Capture) | Eventual | 중간   | DB 레벨 동기화        |
| Event Sourcing            | Strong   | 높음   | 이벤트 기반 아키텍처  |
| ETL Batch                 | Delayed  | 낮음   | 실시간 불필요         |

### Dual Write 주의사항

- 양쪽 쓰기 실패 시 불일치 발생 가능
- 보상 트랜잭션(Saga) 또는 Outbox 패턴 필수
- 전환 완료 후 즉시 제거 (기술 부채화 방지)

## 5. 단계별 분리

### 모놀리스 → 마이크로서비스 분리 순서

| 단계 | 대상 선정 기준             | 활동                      |
|------|----------------------------|---------------------------|
| 1    | 변경 빈도 높은 도메인      | 비즈니스 경계 식별        |
| 2    | 외부 의존성 적은 모듈      | 데이터 소유권 정의        |
| 3    | 팀 경계와 일치하는 기능    | API 계약 설계             |
| 4    | 성능/확장 요구가 다른 기능 | 독립 배포 파이프라인 구축 |

### 분리 시 데이터 처리

| 패턴                   | 설명                                  |
|------------------------|---------------------------------------|
| Database per Service   | 서비스별 독립 DB (목표 상태)          |
| Shared Database (임시) | 전환기에 DB 공유 허용 (기한 설정)     |
| API Composition        | 여러 서비스 데이터 조합 (BFF/Gateway) |
| Event-driven Sync      | 이벤트로 데이터 동기화 (Eventual)     |

## 6. 검증

### 전환 검증 체크리스트

| 항목          | 검증 방법                      |
|---------------|--------------------------------|
| 기능 동등성   | 기존 API 테스트 슈트 재실행    |
| 성능 동등성   | 부하 테스트 비교 (p99 latency) |
| 데이터 정합성 | Shadow mode + 결과 비교        |
| 롤백 가능성   | Facade에서 즉시 레거시 복귀    |
| 모니터링      | 신규 서비스 SLI/SLO 동일 적용  |

### Shadow Mode (Dark Launch)

- 신규 시스템에 트래픽 복제 (응답은 레거시만 반환)
- 신규 시스템 응답과 레거시 응답 비교 (diff)
- 불일치 0% 달성 후 전환 결정

## 7. 조직 고려사항

### 팀 구성

| 역할               | 책임                                   |
|--------------------|----------------------------------------|
| Modernization Lead | 전환 로드맵, 우선순위, 이해관계자 관리 |
| Platform Team      | Facade/라우팅/인프라 제공              |
| Feature Team       | 개별 기능 마이그레이션 수행            |
| QA/Validation      | Shadow mode 비교, 회귀 테스트          |

### 성공 측정

| 지표               | 목표                       |
|--------------------|----------------------------|
| 레거시 트래픽 비율 | 분기별 감소 (목표: 0%)     |
| 배포 빈도 (신규)   | 주 1회+ (레거시 대비 개선) |
| 장애 발생률        | 레거시 대비 동일 또는 감소 |
| 개발자 만족도      | 분기별 설문 개선           |

## 8. 안티패턴

| 안티패턴                 | 문제                       | 올바른 접근                        |
|--------------------------|----------------------------|------------------------------------|
| Big Bang 재작성          | 높은 리스크, 비즈니스 중단 | Strangler Fig 점진적 전환          |
| 레거시 방치 (전환 안 함) | 기술 부채 이자 복리 증가   | 정량적 비용 분석 후 계획 수립      |
| 과도한 범위 (한번에 다)  | 프로젝트 실패              | 작은 단위부터, 성공 증명 후 확장   |
| 데이터 이중 쓰기 영구화  | 기술 부채                  | 전환 완료 후 즉시 제거             |
| 레거시 팀/신규 팀 분리   | 사일로, 지식 단절          | 같은 팀이 양쪽 담당 (context 유지) |

## 9. 트러블슈팅

| 증상                      | 원인                   | 해결                               |
|---------------------------|------------------------|------------------------------------|
| 전환 속도가 너무 느림     | 범위 과대, 의존성 복잡 | 가장 독립적인 기능부터 시작        |
| 신규 서비스 장애 빈번     | 검증 부족              | Shadow mode 충분 기간 + 자동 비교  |
| 레거시 트래픽이 안 줄어듦 | 사용자/팀 미이전       | 강제 기한 설정, 레거시 기능 동결   |
| 데이터 불일치 발생        | Dual write 실패        | Outbox 패턴 + 보상 로직 + 모니터링 |
| 경영진 지지 상실          | 가시적 성과 부족       | 초기 성공 사례 빠르게 확보 후 공유 |

> 레거시 현대화 전략(Retire, Retain, Rehost, Replatform, Refactor, Repurchase)은 AWS의 6R 마이그레이션 전략에 기반합니다. Strangler Fig 패턴은 Martin Fowler(2004)가 제안했습니다.
> — https://aws.amazon.com/blogs/enterprise-strategy/6-strategies-for-migrating-applications-to-the-cloud/
> — https://martinfowler.com/bliki/StranglerFigApplication.html

> AWS 6R 마이그레이션 전략: Retire, Retain, Rehost, Replatform, Refactor, Repurchase. AWS가 2016년 블로그에서 6R을 정립했습니다.
> — https://aws.amazon.com/blogs/enterprise-strategy/6-strategies-for-migrating-applications-to-the-cloud/

> Strangler Fig Pattern은 기존 시스템을 점진적으로 교체하는 패턴입니다. 핵심: 새 기능은 새 시스템에, 기존 기능은 점진적 이관.
> — https://martinfowler.com/bliki/StranglerFigApplication.html

> Anti-Corruption Layer(ACL)는 Domain-Driven Design(Eric Evans, 2003)에서 유래한 패턴으로, 레거시와 신규 시스템 간 변환 계층입니다.
> — Evans, Eric. "Domain-Driven Design" Ch.14 (Addison-Wesley, 2003)

## 참고 자료

- Martin Fowler: [StranglerFigApplication](https://martinfowler.com/bliki/StranglerFigApplication.html) — ★★☆☆☆
- AWS Migration Strategies: [docs.aws.amazon.com](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html) — ★★★☆☆
- Sam Newman. "Monolith to Microservices" (2019) — ★★★★☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
