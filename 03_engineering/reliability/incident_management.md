# Incident Management

장애 발생 시 영향을 최소화하고 신속하게 복구하기 위한 체계적 대응 프레임워크입니다. Google SRE Book Ch.14와 PagerDuty Incident Response를 기반으로 합니다.

## 목차

| 섹션                                                                                                                     |
|--------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 장애 등급](#2-장애-등급) / [3. 역할 체계](#3-역할-체계)                                         |
| [4. 대응 프로세스](#4-대응-프로세스) / [5. 커뮤니케이션](#5-커뮤니케이션) / [6. 에스컬레이션](#6-에스컬레이션)           |
| [7. Incident State Document](#7-incident-state-document) / [8. 온콜 연계](#8-온콜-연계) / [9. 트러블슈팅](#9-트러블슈팅) |

## 1. 개요

| 항목      | 값                                                       |
|-----------|----------------------------------------------------------|
| 목적      | 장애 영향 최소화 + 빠른 복구 + 재발 방지                 |
| 출처      | Google SRE Book Ch.14, PagerDuty Incident Response       |
| 핵심      | 역할 분리, 명시적 커뮤니케이션, 실시간 상태 문서         |
| 전제      | 사전에 역할/프로세스/도구가 정의되어 있어야 함           |
| 연관 문서 | Postmortem (장애 후), SLO/Error Budget (임계값), On-Call |

### 핵심 원칙 (Google SRE Book)

| 원칙                         | 설명                                       |
|------------------------------|--------------------------------------------|
| Recursive Separation         | 역할을 명확히 분리하여 병렬 작업           |
| Recognized Command Post      | IC가 누구인지 모두가 알아야 함             |
| Live Incident State Document | 실시간 상태 문서 유지 (단일 진실 소스)     |
| Clear, Live Handoff          | 교대 시 명시적 인수인계 (암묵적 전달 금지) |

> Google SRE Book Ch.14 "Managing Incidents" — 위 4원칙은 FEMA ICS(Incident Command System)를 소프트웨어 운영에 적용한 것입니다.
> — https://sre.google/sre-book/managing-incidents/

## 2. 장애 등급

### Severity 분류

| 등급  | 이름     | 기준                               | 대응 시간 | 업데이트 주기 |
|-------|----------|------------------------------------|-----------|---------------|
| SEV-1 | Critical | 서비스 전체 장애, 데이터 손실 위험 | 즉시      | 15분          |
| SEV-2 | Major    | 주요 기능 불가, 다수 사용자 영향   | 15분 이내 | 30분          |
| SEV-3 | Minor    | 부분 기능 저하, 우회 가능          | 1시간     | 2시간         |
| SEV-4 | Low      | 경미한 이슈, 소수 영향             | 업무 시간 | 일 1회        |
| SEV-5 | Cosmetic | UI 결함, 오타, 성능 미미한 저하    | 백로그    | 불필요        |

> PagerDuty의 5-level severity model을 기반으로 합니다. 조직마다 3~5단계로 조정합니다.
> — https://response.pagerduty.com/before/severity_levels/

### 등급 판단 기준

```
Is the service completely down?
     │
     ├── Yes ──> SEV-1
     │
     └── No
          │
          ├── Major feature broken + many users? ──> SEV-2
          │
          ├── Partial degradation + workaround exists? ──> SEV-3
          │
          └── Minor issue + few users? ──> SEV-4/5
```

### 자동 등급 산정 기준 (예시)

| 지표                  | SEV-1    | SEV-2  | SEV-3  |
|-----------------------|----------|--------|--------|
| Error rate            | > 50%    | > 10%  | > 1%   |
| Latency p99           | > 30s    | > 5s   | > 2s   |
| Affected users        | > 50%    | > 10%  | > 1%   |
| Revenue impact (분당) | > $1,000 | > $100 | < $100 |
| Data loss             | 확인됨   | 가능성 | 없음   |

## 3. 역할 체계

### 필수 역할

| 역할                    | 책임                                            | 누가              |
|-------------------------|-------------------------------------------------|-------------------|
| Incident Commander (IC) | 전체 조율, 의사결정 위임, 우선순위 결정         | 시니어 엔지니어   |
| Operations Lead         | 실제 복구 작업 수행, IC에게 상황 보고           | 온콜 엔지니어     |
| Communications Lead     | 이해관계자 업데이트, 상태 페이지, 타임라인 기록 | PM 또는 별도 지정 |
| Planning Lead           | 장기 장애 시 교대 계획, 자원 확보               | 매니저            |

### 역할 전환 흐름

```
Alert Fired
     │
     v
On-Call Engineer (초기 대응)
     │
     ├── SEV-3 이하: 단독 처리
     │
     └── SEV-2 이상: IC 선언
              │
              v
         IC 지정 (On-Call 또는 시니어)
              │
              ├── Operations Lead 지정
              ├── Communications Lead 지정
              └── (장기화 시) Planning Lead 지정
```

### IC의 핵심 행동

- 복구 작업을 직접 하지 않음 (Operations Lead에게 위임)
- 상황 인식 유지 + 의사결정에 집중
- 5분마다 상황 요약: "현재 상태, 다음 조치, 예상 복구 시간"
- 교대 시 명시적 선언: "IC를 [이름]에게 넘깁니다"

> IC 역할은 미국 FEMA의 National Incident Management System(NIMS)에서 유래합니다. Google SRE가 이를 IT 운영에 도입했습니다.
> — https://www.fema.gov/emergency-managers/nims

## 4. 대응 프로세스

### 5단계 프레임워크

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Detect   │──>│ Triage   │──>│ Mitigate │──>│ Resolve  │──>│ Follow-up│
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
  Alert          Severity       Reduce          Root cause     Postmortem
  Monitor        IC assign      impact          fix            Action items
```

### 단계별 상세

| 단계      | 목표                  | 주요 행동                          | 시간 목표     |
|-----------|-----------------------|------------------------------------|---------------|
| Detect    | 장애 인지             | 알림 수신, 모니터링 확인           | < 5분         |
| Triage    | 등급 판정 + 역할 배정 | SEV 결정, IC 선언, 채널 개설       | < 10분        |
| Mitigate  | 영향 범위 축소        | 롤백, 트래픽 전환, 격리            | < 30분 (목표) |
| Resolve   | 근본 원인 해결        | 수정 배포, 검증                    | 가변          |
| Follow-up | 재발 방지             | Postmortem 작성, Action items 등록 | 48시간 이내   |

### Mitigate 우선 원칙

> "Restore first, investigate later."

- 원인 분석보다 **영향 축소**를 먼저 수행합니다
- 일반적인 Mitigate 순서:
  1. 최근 변경 롤백 (배포, 설정 변경)
  2. 트래픽 드레인 (문제 서버/리전 제외)
  3. 스케일 업/아웃 (부하 분산)
  4. 기능 비활성화 (feature flag off)

> "Reduce the impact first. Investigate the root cause after the incident is mitigated." — Google SRE Book Ch.14
> — https://sre.google/sre-book/managing-incidents/

## 5. 커뮤니케이션

### 채널 구성

| 채널            | 용도                   | 참여자                 |
|-----------------|------------------------|------------------------|
| #incident-war   | 기술 대응 (Operations) | IC, Ops Lead, 엔지니어 |
| #incident-comms | 이해관계자 업데이트    | Comms Lead, PM, 경영진 |
| Status Page     | 외부 사용자 공지       | Comms Lead             |
| Bridge Call     | SEV-1 음성 통화 (선택) | IC + 핵심 인원         |

### 업데이트 템플릿

```
[HH:MM] Status: investigating/identified/monitoring/resolved
Impact: [영향 범위]
Current action: [현재 진행 중인 조치]
Next update: [다음 업데이트 시간]
IC: [이름]
```

### 커뮤니케이션 실수 방지

| 하지 말 것              | 해야 할 것                       |
|-------------------------|----------------------------------|
| "곧 고쳐질 것 같습니다" | "현재 조사 중, 30분 후 업데이트" |
| 여러 채널에 분산된 정보 | 단일 State Document에 집중       |
| 원인 확정 전 공개 발표  | "조사 중"으로 표현, 확인 후 공유 |
| 비난/책임 추궁          | 사실 위주, 다음 조치 중심        |

## 6. 에스컬레이션

### 에스컬레이션 기준

| 조건                        | 행동                                |
|-----------------------------|-------------------------------------|
| 15분 내 원인 미파악 (SEV-1) | 추가 엔지니어 호출                  |
| 30분 내 Mitigate 실패       | 상위 매니저 + 아키텍트 에스컬레이션 |
| 1시간 내 복구 불가          | VP/CTO 보고, 외부 벤더 지원 요청    |
| 데이터 손실 확인            | 즉시 경영진 보고                    |

### 에스컬레이션 체인

```
On-Call Engineer
     │
     v (15min)
Team Lead / Senior Engineer
     │
     v (30min)
Engineering Manager + Architect
     │
     v (1hr)
Director / VP
     │
     v (data loss / security breach)
CTO / CEO
```

## 7. Incident State Document

### 필수 필드

```markdown
# Incident: [제목]

## Status: investigating / identified / monitoring / resolved

## Summary
[1~2문장 요약]

## Impact
- 서비스: [영향받는 서비스]
- 사용자: [영향 범위/수]
- 시작: [HH:MM UTC]
- 지속: [현재 진행 중 / N분간]

## Roles
- IC: [이름]
- Operations: [이름]
- Communications: [이름]

## Timeline
| 시간 (UTC) | 이벤트                      |
|------------|-----------------------------|
| HH:MM      | Alert fired                 |
| HH:MM      | IC declared, SEV-N assigned |
| HH:MM      | Rollback initiated          |
| HH:MM      | Service restored            |

## Root Cause
[확인 후 작성]

## Action Items
| ID | 항목        | 담당   | 기한       | 상태 |
|----|-------------|--------|------------|------|
| 1  | [조치 내용] | [이름] | YYYY-MM-DD | ⬜   |

## Lessons Learned
- What went well:
- What went wrong:
- Where we got lucky:
```

## 8. 온콜 연계

### 온콜 → 장애 대응 전환

| 온콜 상태             | 행동                               |
|-----------------------|------------------------------------|
| 단순 알림 (SEV-4/5)   | 온콜 엔지니어 단독 처리            |
| 복합 알림 (SEV-3)     | 온콜이 1차 대응, 필요 시 팀원 호출 |
| 대규모 장애 (SEV-1/2) | 온콜이 IC 선언 후 역할 분배        |

### 온콜 부하 관리 (Google 권장)

- 온콜 시간: 전체 업무의 25% 이하
- 월 2회 이하 야간 호출 (번아웃 방지)
- 장애 대응 후 다음 시프트 면제 (피로 관리)
- 온콜 중 프로젝트 작업: 중단 가능한 것만 배정

> Google SRE Book Ch.11 "Being On-Call": 온콜 업무 비중 25% 이하, 최소 2인 로테이션 권장.
> — https://sre.google/sre-book/being-on-call/

## 9. 트러블슈팅

| 증상                         | 원인                          | 해결                                     |
|------------------------------|-------------------------------|------------------------------------------|
| 장애 중 아무도 리드하지 않음 | IC 미지정, 역할 불명확        | 즉시 IC 선언 + 역할 배정                 |
| 정보가 여러 채널에 분산      | State Document 미사용         | 단일 문서로 집중, 링크 공유              |
| 복구 후 같은 장애 반복       | Postmortem 미작성 또는 미이행 | 48시간 내 Postmortem + Action Items 추적 |
| 에스컬레이션 지연            | 기준 불명확                   | Severity별 시간 기준 사전 정의           |
| 커뮤니케이션 부재            | Comms Lead 미지정             | SEV-2 이상 시 반드시 Comms Lead 배정     |

## 참고 자료

- Google SRE Book Ch.14: [Managing Incidents](https://sre.google/sre-book/managing-incidents/) — ★★★★☆
- Google SRE Book Ch.11: [Being On-Call](https://sre.google/sre-book/being-on-call/) — ★★★★☆
- PagerDuty: [Incident Response](https://response.pagerduty.com/) — ★★★☆☆
- Atlassian: [Incident Management](https://www.atlassian.com/incident-management) — ★★☆☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
