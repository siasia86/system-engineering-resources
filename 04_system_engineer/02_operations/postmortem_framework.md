# Postmortem Framework

장애 발생 후 근본 원인을 분석하고 재발을 방지하기 위한 구조화된 회고 프레임워크입니다. Google SRE Book Ch.15를 기반으로 합니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원칙](#2-원칙) / [3. 작성 기준](#3-작성-기준)                                 |
| [4. 템플릿](#4-템플릿) / [5. 근본 원인 분석](#5-근본-원인-분석) / [6. Action Items](#6-action-items)   |
| [7. 리뷰 프로세스](#7-리뷰-프로세스) / [8. 안티패턴](#8-안티패턴) / [9. 트러블슈팅](#9-트러블슈팅)    |

## 1. 개요

| 항목       | 값                                                    |
|------------|-------------------------------------------------------|
| 목적       | 장애로부터 학습하여 동일/유사 장애 재발 방지          |
| 출처       | Google SRE Book Ch.15 "Postmortem Culture"            |
| 핵심       | Blameless (비난 없는), 시스템 관점, Action 추적       |
| 작성 시한  | 장애 종료 후 48시간 이내                              |
| 리뷰 시한  | 작성 후 1주 이내 리뷰 미팅                            |
| 연관 문서  | Incident Management (장애 중), Change Management (예방) |

## 2. 원칙

### Blameless Culture

| 원칙                    | 설명                                                  |
|-------------------------|-------------------------------------------------------|
| 개인이 아닌 시스템      | "누가 실수했는가"가 아닌 "왜 시스템이 허용했는가"     |
| 심리적 안전             | 솔직한 보고를 처벌하면 은폐가 발생함                  |
| 학습 목적               | 처벌이 아닌 개선을 위한 과정                          |
| 투명성                  | Postmortem은 조직 전체에 공유                         |

### Google 원칙 (SRE Book Ch.15)

- 모든 SEV-1/SEV-2 장애에 대해 Postmortem 작성 필수
- Action items는 버그 트래커에 등록, 담당자/기한 명시
- Postmortem 리뷰 미팅 필수 (작성만으로는 불충분)
- "Blameless" 하지만 "Accountable" — 개선 책임은 존재

## 3. 작성 기준

### Postmortem 작성 트리거

| 조건                              | 필수 작성 | 선택 작성 |
|-----------------------------------|-----------|-----------|
| SEV-1 (서비스 전체 장애)          | ✅        |           |
| SEV-2 (주요 기능 불가)            | ✅        |           |
| SEV-3 (부분 저하, 학습 가치 있음) |           | ✅        |
| 데이터 손실 발생                  | ✅        |           |
| 온콜이 수동 개입해야 복구         | ✅        |           |
| 동일 유형 장애 반복 (2회+)        | ✅        |           |
| 고객 영향 없지만 아슬아슬한 상황  |           | ✅        |

## 4. 템플릿

```markdown
# Postmortem: [제목]

**Date**: YYYY-MM-DD
**Authors**: [작성자]
**Status**: Draft / In Review / Approved
**Severity**: SEV-N

## Summary
[1~3문장으로 무슨 일이 있었는지]

## Impact
- Duration: HH:MM ~ HH:MM (N minutes)
- Users affected: [수 또는 비율]
- Revenue impact: [있으면 기재]
- Data loss: Yes/No

## Timeline (UTC)
| Time  | Event                              |
|-------|------------------------------------|
| HH:MM | [이벤트]                           |

## Root Cause
[근본 원인 설명 — 기술적 세부사항]

## Contributing Factors
- [원인 1: 예) 모니터링 부재]
- [원인 2: 예) 테스트 미비]
- [원인 3: 예) 문서화 부족]

## Detection
- How: [어떻게 발견했는지]
- Time to detect: [N minutes]
- Could we have detected earlier? [Yes/No, how]

## Response
- What we did: [대응 내용]
- Time to mitigate: [N minutes]
- What slowed us down: [지연 요인]

## Action Items
| ID | Type       | Action              | Owner  | Due        | Status |
|----|------------|---------------------|--------|------------|--------|
| 1  | Prevent    | [재발 방지 조치]    | [이름] | YYYY-MM-DD | ⬜     |
| 2  | Detect     | [탐지 개선]         | [이름] | YYYY-MM-DD | ⬜     |
| 3  | Mitigate   | [복구 속도 개선]    | [이름] | YYYY-MM-DD | ⬜     |

## Lessons Learned
### What went well
- [잘된 점]

### What went wrong
- [잘못된 점]

### Where we got lucky
- [운이 좋았던 부분 — 다음엔 운에 의존하면 안 됨]
```

## 5. 근본 원인 분석

### 5 Whys

```
Problem: API server returned 500 errors for 30 minutes

Why 1: Database connection pool exhausted
Why 2: Connection leak in new feature code
Why 3: Code review did not catch missing connection.close()
Why 4: No static analysis rule for connection leak patterns
Why 5: Static analysis tooling not updated for new DB library

Root Cause: Tooling gap — static analysis not covering new library
```

### Contributing Factor Categories

| 카테고리      | 예시                                          |
|---------------|-----------------------------------------------|
| Process       | 변경 절차 미준수, 리뷰 누락                   |
| Tooling       | 모니터링 부재, 자동화 미비                    |
| Architecture  | 단일 장애점, 용량 부족                        |
| Communication | 인수인계 실패, 문서 부재                      |
| Testing       | 테스트 미비, 환경 차이                        |

### Root Cause vs Trigger

| 구분    | 설명                              | 예시                        |
|---------|-----------------------------------|-----------------------------|
| Trigger | 장애를 촉발한 직접 이벤트         | 배포, 설정 변경, 트래픽 급증 |
| Root Cause | 시스템이 trigger에 취약한 이유 | 롤백 미준비, 모니터링 부재   |

## 6. Action Items

### Action 유형

| 유형     | 목적              | 예시                                    |
|----------|-------------------|-----------------------------------------|
| Prevent  | 재발 방지         | 입력 검증 추가, 아키텍처 개선           |
| Detect   | 조기 탐지         | 알림 추가, 대시보드 개선                |
| Mitigate | 복구 속도 개선    | 자동 롤백, 런북 작성                    |
| Process  | 프로세스 개선     | 배포 절차 변경, 리뷰 기준 강화          |

### 좋은 Action Item 기준

| 속성       | 좋은 예                            | 나쁜 예                     |
|------------|------------------------------------|-----------------------------|
| Specific   | "connection pool alert 추가"       | "모니터링 개선"             |
| Measurable | "p99 latency alert < 3s"          | "성능 좋게"                 |
| Assignable | "홍길동, 2026-07-14까지"          | "팀에서 처리"               |
| Realistic  | "이번 스프린트에 린터 규칙 추가"   | "전체 아키텍처 재설계"      |
| Trackable  | "Jira INFRA-1234"                  | "나중에 하자"               |

## 7. 리뷰 프로세스

### 리뷰 미팅 구조

| 단계       | 시간    | 내용                              |
|------------|---------|-----------------------------------|
| Timeline   | 10분    | 타임라인 공유 (사실 확인)         |
| Root Cause | 15분    | 원인 분석 토론 (5 Whys 검증)      |
| Actions    | 15분    | Action items 검토/추가/우선순위   |
| Lessons    | 10분    | 학습 포인트 공유                  |
| Follow-up  | 5분     | 담당자/기한 확정                  |

### 리뷰 체크리스트

- [ ] Timeline이 사실에 기반하는가 (로그/메트릭으로 검증)
- [ ] Root Cause가 trigger와 구분되는가
- [ ] Action items가 SMART 기준을 충족하는가
- [ ] "Where we got lucky"가 식별되었는가
- [ ] 유사 서비스에 동일 위험이 없는지 확인했는가

## 8. 안티패턴

| 안티패턴                        | 문제                              | 올바른 접근                       |
|---------------------------------|-----------------------------------|-----------------------------------|
| "누구 잘못이다" (Blame)         | 은폐 유발, 학습 방해              | 시스템 관점으로 분석              |
| "다시는 안 할게요" (Promise)    | 구조적 개선 없음                  | 시스템적 방지 장치 설계           |
| Action items 미추적             | 재발 방치                         | 버그 트래커 등록 + 기한 추적      |
| 작성만 하고 리뷰 안 함          | 학습 공유 실패                    | 1주 내 리뷰 미팅 필수             |
| 지나치게 길고 상세              | 아무도 안 읽음                    | 2~3페이지 이내, 핵심 중심         |

## 9. 트러블슈팅

| 증상                           | 원인                      | 해결                                  |
|--------------------------------|---------------------------|---------------------------------------|
| Postmortem 작성률 낮음         | 문화 부재, 시간 부족      | 템플릿 제공, 48시간 규칙, 경영진 지원 |
| Action items 완료율 낮음       | 추적 미비, 우선순위 밀림  | 스프린트에 포함, 주간 리뷰            |
| 같은 장애 반복                 | Root cause 미식별         | 5 Whys 재수행, 외부 시각 참여         |
| 비난 문화 지속                 | 리더십 불일치             | 경영진부터 blameless 선언, 모범 사례  |
| Postmortem이 형식적            | 학습 동기 부족            | 우수 Postmortem 시상, 공유 세션       |

## 참고 자료

- Google SRE Book Ch.15: [Postmortem Culture](https://sre.google/sre-book/postmortem-culture/) — ★★★★☆
- Google SRE Book Appendix D: [Example Postmortem](https://sre.google/sre-book/example-postmortem/) — ★★★★☆
- PagerDuty: [Postmortem Guide](https://postmortems.pagerduty.com/) — ★★★☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
