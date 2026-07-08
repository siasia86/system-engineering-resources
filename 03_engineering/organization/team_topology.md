# Team Topology

조직 구조가 시스템 아키텍처를 결정한다는 Conway 법칙을 기반으로, 소프트웨어 전달 속도를 최적화하는 팀 설계 프레임워크입니다. Matthew Skelton & Manuel Pais의 "Team Topologies" (2019)를 기반으로 합니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 4가지 팀 유형](#2-4가지-팀-유형) / [3. 3가지 상호작용 모드](#3-3가지-상호작용-모드) |
| [4. Conway 법칙](#4-conway-법칙) / [5. 인지 부하](#5-인지-부하) / [6. 팀 크기](#6-팀-크기)                   |
| [7. 적용 가이드](#7-적용-가이드) / [8. 안티패턴](#8-안티패턴) / [9. 트러블슈팅](#9-트러블슈팅)               |

## 1. 개요

| 항목 | 값                                                       |
|------|----------------------------------------------------------|
| 출처 | Skelton, M. & Pais, M. "Team Topologies" (2019)          |
| 핵심 | 4가지 팀 유형 + 3가지 상호작용 모드                      |
| 원칙 | Conway 법칙의 역전 (Inverse Conway Maneuver)             |
| 목표 | Fast flow of change — 변경의 빠른 흐름                   |
| 연관 | Platform Engineering (Platform Team), SLO (팀 경계 기준) |

## 2. 4가지 팀 유형

### 요약 비교

| 유형                  | 목적                     | 수명      | 예시                  |
|-----------------------|--------------------------|-----------|-----------------------|
| Stream-aligned        | 비즈니스 가치 흐름 전담  | 영구      | 결제팀, 검색팀        |
| Platform              | 셀프서비스 인프라 제공   | 영구      | 인프라팀, DevEx팀     |
| Enabling              | 역량 격차 해소, 코칭     | 임시~영구 | SRE 코치, 보안 지원팀 |
| Complicated-subsystem | 전문 지식 필요 영역 전담 | 영구      | ML 엔진팀, 코덱팀     |

### Stream-aligned Team

| 속성      | 내용                                       |
|-----------|--------------------------------------------|
| 정의      | 단일 가치 흐름(stream of work)에 정렬된 팀 |
| 핵심 역량 | 설계, 개발, 테스트, 배포, 운영을 모두 소유 |
| 목표      | 외부 의존 없이 독립적으로 변경을 배포      |
| 크기      | 5~9명 (Two-pizza team)                     |
| 비율      | 조직 전체 팀의 대다수 (the vast majority)  |

### Platform Team

| 속성      | 내용                                               |
|-----------|----------------------------------------------------|
| 정의      | Stream-aligned 팀의 인지 부하를 줄여주는 내부 제품 |
| 제공 방식 | Self-service API, 템플릿, 문서, Golden Path        |
| 고객      | Stream-aligned 팀 (내부 사용자)                    |
| 핵심 원칙 | "최소한의 인지 부하" — 얇은 레이어, 복잡도 은닉    |

### Enabling Team

| 속성 | 내용                                         |
|------|----------------------------------------------|
| 정의 | 다른 팀이 새로운 역량을 습득하도록 지원      |
| 활동 | 코칭, 페어링, 워크숍, 기술 조사              |
| 수명 | 지원 완료 후 철수 (임시적 관계)              |
| 예시 | CI/CD 전환 지원, 보안 교육, 관측성 도입 코칭 |

### Complicated-subsystem Team

| 속성      | 내용                                          |
|-----------|-----------------------------------------------|
| 정의      | 높은 전문성이 필요한 서브시스템을 전담        |
| 존재 이유 | 해당 지식을 모든 팀에 요구하면 인지 부하 과다 |
| 예시      | 비디오 코덱, ML 추론 엔진, 결제 정산 엔진     |
| 주의      | 남용 금지 — 정말 복잡할 때만 생성             |

## 3. 3가지 상호작용 모드

| 모드           | 정의                          | 기간 | 예시                      |
|----------------|-------------------------------|------|---------------------------|
| Collaboration  | 두 팀이 밀접하게 협업         | 임시 | 신규 기능 공동 개발       |
| X-as-a-Service | 명확한 API 경계로 서비스 제공 | 영구 | Platform → Stream-aligned |
| Facilitating   | 한 팀이 다른 팀의 학습을 촉진 | 임시 | Enabling → Stream-aligned |

### 상호작용 적합성

| 팀 조합                                | 권장 모드              |
|----------------------------------------|------------------------|
| Stream-aligned ↔ Platform              | X-as-a-Service         |
| Stream-aligned ↔ Enabling              | Facilitating           |
| Stream-aligned ↔ Stream-aligned        | Collaboration (제한적) |
| Stream-aligned ↔ Complicated-subsystem | X-as-a-Service         |

## 4. Conway 법칙

### 원문

> "Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure."
> — Conway, Melvin. "How Do Committees Invent?" Datamation, 1968 — Melvin Conway, 1968

### Inverse Conway Maneuver

| 개념           | 설명                                         |
|----------------|----------------------------------------------|
| 전통적 접근    | 조직 구조 → 시스템 아키텍처 (수동적 결과)    |
| Inverse Conway | 원하는 아키텍처 → 팀 구조 설계 (능동적 설계) |
| 핵심           | 팀 경계 = 서비스 경계 = API 경계             |

## 5. 인지 부하

### 3가지 인지 부하 유형

| 유형       | 설명                         | 예시                         |
|------------|------------------------------|------------------------------|
| Intrinsic  | 업무 자체의 본질적 복잡도    | 비즈니스 도메인 로직         |
| Extraneous | 불필요한 환경적 복잡도       | 인프라 설정, 빌드 파이프라인 |
| Germane    | 학습을 통한 가치 있는 복잡도 | 새 기술 습득                 |

### 팀 설계 원칙

- Extraneous load 최소화 → Platform Team이 흡수
- Intrinsic load가 팀 용량 초과 → 도메인 분할 (Stream split)
- Germane load 지원 → Enabling Team 투입

## 6. 팀 크기

### Dunbar 수와 팀 크기

| 크기    | 명칭           | 특성                        |
|---------|----------------|-----------------------------|
| 5~9명   | Single team    | 신뢰 구축, 밀접 협업 가능   |
| 15~20명 | Team of teams  | 상호 인지 가능, 느슨한 협업 |
| 50명    | Tribe/Division | 공유 목적, 약한 연결        |
| 150명   | Dunbar number  | 상호 인식 한계              |

### Two-pizza Rule

- Amazon 기원: 팀이 피자 2판으로 식사할 수 있는 크기
- 실질적 의미: 5~8명, 독립적 의사결정 + 빠른 커뮤니케이션

## 7. 적용 가이드

### 도입 단계

| 단계 | 활동                             | 산출물                 |
|------|----------------------------------|------------------------|
| 1    | 현재 팀 구조 + 의존성 맵핑       | 팀 상호작용 다이어그램 |
| 2    | 원하는 아키텍처 정의 (목표 상태) | 서비스 경계 + 팀 경계  |
| 3    | 인지 부하 평가 (팀별 도메인 수)  | 과부하 팀 식별         |
| 4    | 팀 유형 + 상호작용 모드 할당     | Team Topology 맵       |
| 5    | 점진적 전환 (분기 단위)          | 이전 계획, 인력 이동   |

### 팀 수 산정



## 8. 안티패턴

| 안티패턴              | 문제                       | 올바른 접근                   |
|-----------------------|----------------------------|-------------------------------|
| 팀 이름만 바꿈        | 구조 변경 없이 라벨만 변경 | 실제 책임/권한/의존성 재설계  |
| Platform이 강제       | 사용 강제 → 혁신 억제      | Optional + 가치 증명          |
| Enabling 팀 상주      | 의존 관계 고착             | 기한 설정 + 역량 이전 후 철수 |
| 모든 것이 Complicated | 팀 유형 남발               | 진짜 전문성 필요할 때만 생성  |
| 팀 간 티켓 기반 요청  | 대기 시간 → flow 저하      | API 경계 + Self-service 전환  |

## 9. 트러블슈팅

| 증상                        | 원인                | 해결                                |
|-----------------------------|---------------------|-------------------------------------|
| 배포 속도가 안 빨라짐       | 팀 간 의존성 미해소 | 의존성 맵 재분석 + 팀 경계 재설계   |
| Platform 팀 과부하          | 모든 요청 수동 처리 | Self-service API + 문서 강화        |
| Stream-aligned 팀이 너무 큼 | 도메인 분할 미수행  | 가치 흐름 분석 → 팀 분할            |
| Enabling 팀 효과 없음       | 코칭 아닌 대행      | Facilitating 모드 재확인, 기한 설정 |
| Conway 법칙 역전이 안 됨    | 경영진 미참여       | 아키텍처 목표 + 팀 구조 동시 제안   |

> 4가지 팀 유형(Stream-aligned, Platform, Enabling, Complicated Subsystem)과 3가지 상호작용 모드(Collaboration, X-as-a-Service, Facilitating)는 "Team Topologies" 원서에서 정의합니다.
> — Skelton, Matthew & Pais, Manuel. "Team Topologies" (IT Revolution Press, 2019)

> Conway's Law(1968): "시스템 구조는 조직의 커뮤니케이션 구조를 반영한다." Team Topologies는 이를 역으로 활용합니다 (Inverse Conway Maneuver).
> — Conway, Melvin. "How Do Committees Invent?" (1968)

> Cognitive Load Theory를 팀 설계에 적용: 팀이 담당하는 도메인의 복잡도가 인지 부하 한계를 초과하면 분리가 필요합니다.
> — Skelton & Pais. "Team Topologies" Ch.3 (2019)

> 3가지 상호작용 모드(Collaboration, X-as-a-Service, Facilitating)는 팀 간 의존성을 명시적으로 관리하는 도구입니다.
> — Skelton & Pais. "Team Topologies" Ch.7 (2019)

## 참고 자료

- Skelton, M. & Pais, M. "Team Topologies" (2019) — ★★★★☆
- teamtopologies.com: [teamtopologies.com](https://teamtopologies.com/) — ★★★☆☆
- Conway, M. "How Do Committees Invent?" (1968) — ★★★★☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
