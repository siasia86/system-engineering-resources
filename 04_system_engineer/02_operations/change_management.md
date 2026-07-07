# Change Management

인프라/서비스 변경을 체계적으로 관리하여 장애를 예방하고 추적 가능성을 확보하는 프로세스입니다. Google SRE Book과 ITIL v4를 기반으로 합니다.

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 변경 등급](#2-변경-등급) / [3. 변경 프로세스](#3-변경-프로세스)           |
| [4. 배포 윈도우](#4-배포-윈도우) / [5. 승인 체계](#5-승인-체계) / [6. 긴급 변경](#6-긴급-변경)     |
| [7. 변경 추적](#7-변경-추적) / [8. 실패 시 대응](#8-실패-시-대응) / [9. 트러블슈팅](#9-트러블슈팅) |

## 1. 개요

| 항목 | 값                                                          |
|------|-------------------------------------------------------------|
| 목적 | 변경으로 인한 장애 최소화 + 감사 추적 확보                  |
| 출처 | Google SRE Book Ch.8, ITIL v4 Change Enablement             |
| 핵심 | 대부분의 장애가 변경에서 기인 → 체계적 관리로 위험 감소     |
| 범위 | 코드 배포, 인프라 변경, 설정 변경, DB 스키마 변경           |
| 연관 | Incident Management (변경 실패 시), Zero-Downtime Migration |

### 70% 법칙 (Google)

> "most outages are caused by changes to a running system"
> — Google SRE (commonly cited statistic from SRE talks)

## 2. 변경 등급

### ITIL v4 기반 분류

| 등급      | 승인             | 리드 타임  | 예시                                        |
|-----------|------------------|------------|---------------------------------------------|
| Standard  | 사전 승인 (자동) | 즉시       | 패치 적용, 로그 레벨 변경, 인스턴스 교체    |
| Normal    | CAB 승인         | 1~5 영업일 | 신규 서비스 배포, DB 마이그레이션, VPC 변경 |
| Emergency | 긴급 승인 (1인)  | 즉시       | SEV-1 핫픽스, 보안 패치, 데이터 복구        |

### Standard Change 기준

Standard로 분류되려면 다음을 모두 충족해야 합니다:

- 절차가 문서화되어 있음
- 위험이 낮고 잘 이해됨
- 이전에 여러 번 성공적으로 수행됨
- 자동 롤백이 가능함

### 변경 위험도 매트릭스

| 영향 범위      | 롤백 가능 | 롤백 불가 |
|----------------|-----------|-----------|
| 단일 서비스    | Low       | Medium    |
| 다수 서비스    | Medium    | High      |
| 전체 인프라/DB | High      | Critical  |

## 3. 변경 프로세스

### Normal Change 플로우

```
Request ──> Review ──> Approve ──> Schedule ──> Execute ──> Verify ──> Close
   │          │          │           │           │           │          │
   v          v          v           v           v           v          v
 RFC 작성   기술 검토   CAB 승인   윈도우 배정  변경 수행  검증 완료  기록 종료
```

### RFC (Request for Change) 필수 항목

| 필드                | 내용                                |
|---------------------|-------------------------------------|
| Summary             | 변경 내용 1줄 요약                  |
| Justification       | 왜 필요한가 (비즈니스/기술 근거)    |
| Impact Assessment   | 영향 범위, 관련 서비스, 사용자 영향 |
| Risk Level          | Low / Medium / High / Critical      |
| Implementation Plan | 단계별 실행 계획                    |
| Rollback Plan       | 실패 시 복구 절차 (시간 포함)       |
| Test Evidence       | 스테이징 테스트 결과                |
| Schedule            | 희망 실행 일시                      |
| Approvers           | 필요한 승인자 목록                  |

## 4. 배포 윈도우

### 윈도우 정의

| 윈도우 유형 | 시간대             | 허용 변경 유형   | 근거                   |
|-------------|--------------------|------------------|------------------------|
| Standard    | 화~목 10:00~16:00  | Normal, Standard | 근무 시간 내 대응 가능 |
| Extended    | 화~목 22:00~06:00  | High-risk Normal | 저트래픽 시간대        |
| Freeze      | 금~월, 공휴일 전후 | Emergency only   | 대응 인력 부족         |
| Blackout    | 대규모 이벤트 기간 | 변경 불가        | 최대 트래픽 구간       |

### 금요일 배포 금지 원칙

| 이유           | 상세                                 |
|----------------|--------------------------------------|
| 대응 인력 부족 | 주말 온콜만으로는 복잡한 롤백 어려움 |
| 모니터링 지연  | 서서히 드러나는 문제를 월요일에 발견 |
| 비용 증가      | 주말 긴급 대응 = 초과 근무           |

## 5. 승인 체계

### CAB (Change Advisory Board)

| 항목      | 값                                  |
|-----------|-------------------------------------|
| 구성      | 기술 리드 + PM + 보안 + 인프라 + QA |
| 회의 주기 | 주 1회 (화요일 오전)                |
| 의사결정  | 승인 / 조건부 승인 / 거부 / 연기    |
| 기록      | 회의록 + 결정 사유 문서화           |

### 승인 레벨

| 변경 위험도 | 승인자                    |
|-------------|---------------------------|
| Low         | 팀 리드 (자동 승인 가능)  |
| Medium      | 팀 리드 + 시니어 엔지니어 |
| High        | CAB 승인                  |
| Critical    | CAB + VP/Director 승인    |

## 6. 긴급 변경

### Emergency Change 기준

다음 중 하나 이상 해당 시:
- SEV-1/SEV-2 장애 복구를 위한 변경
- 활발히 공격받는 보안 취약점 패치
- 법적/규제 요구사항 즉시 충족

### Emergency Change 절차

```
Incident ──> IC Approval ──> Execute ──> Verify ──> Post-change Review
                │
                v
         단일 시니어 승인
         (CAB 사후 보고)
```

### 긴급 변경 후 의무

| 시간   | 행동                                      |
|--------|-------------------------------------------|
| 즉시   | 변경 기록 작성 (무엇을, 왜, 누가)         |
| 24시간 | CAB에 사후 보고 (Emergency Change Report) |
| 48시간 | Standard Change로 전환 가능 여부 검토     |
| 1주    | 근본 원인에 대한 Normal Change RFC 제출   |

## 7. 변경 추적

### 추적 항목

| 항목      | 내용                                   |
|-----------|----------------------------------------|
| Change ID | 고유 식별자 (자동 채번)                |
| Timestamp | 요청/승인/실행/완료 시각               |
| Operator  | 실행자 (who)                           |
| Artifact  | 변경 대상 (commit SHA, Terraform plan) |
| Result    | 성공 / 실패 / 부분 성공                |
| Rollback  | 롤백 여부 + 사유                       |

### 추적 도구 연동

| 도구        | 역할                             |
|-------------|----------------------------------|
| Git         | 코드 변경 이력 (commit + PR)     |
| Terraform   | 인프라 변경 (plan + state)       |
| CI/CD       | 배포 이력 (pipeline run)         |
| ITSM 도구   | RFC 승인 흐름 (Jira, ServiceNow) |
| Slack/Teams | 변경 알림 (배포 시작/완료 통보)  |

## 8. 실패 시 대응

### 변경 실패 판정 기준

| 지표          | 성공       | 실패             |
|---------------|------------|------------------|
| Error rate    | < baseline | > baseline + 1%  |
| Latency p99   | < baseline | > baseline + 50% |
| Health check  | All pass   | Any fail         |
| Smoke test    | All pass   | Any fail         |
| Rollback 필요 | No         | Yes              |

### 실패 시 행동

```
Change Failed
     │
     ├── Automatic rollback configured?
     │         │
     │         ├── Yes ──> Auto-rollback ──> Verify ──> Incident report
     │         │
     │         └── No ──> Manual rollback ──> Verify ──> Incident report
     │
     └── Rollback impossible?
              │
              └── Forward-fix ──> Emergency Change process
```

## 9. 트러블슈팅

| 증상                 | 원인                     | 해결                                       |
|----------------------|--------------------------|--------------------------------------------|
| 변경 후 장애 반복    | 테스트 부족, 롤백 미준비 | RFC에 Test evidence + Rollback plan 필수화 |
| CAB 병목 (승인 지연) | 모든 변경이 CAB 통과     | Standard Change 기준 확대, 자동 승인       |
| 긴급 변경 남용       | Emergency 기준 불명확    | 기준 문서화 + 사후 감사 강화               |
| 변경 기록 누락       | 수동 기록 의존           | CI/CD + ITSM 자동 연동                     |
| 금요일 배포 장애     | 배포 윈도우 미준수       | Pipeline에 윈도우 체크 gate 추가           |

## 참고 자료

- Google SRE Book Ch.8: [Release Engineering](https://sre.google/sre-book/release-engineering/) — ★★★★☆
- ITIL v4: Change Enablement Practice — ★★★☆☆
- Google: "most outages due to changes" (SRE talks, commonly cited) — ★★☆☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
