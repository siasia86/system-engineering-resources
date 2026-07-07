---
name: sre-operations-official-notes
description: SRE 운영 관련 공식 문서 참조 노트. Incident Management, SLO/Error Budget, Capacity Planning, Change Management, Postmortem.
last_checked: 2026-07-07
sources:
  - https://sre.google/sre-book/table-of-contents/
  - https://sre.google/sre-book/being-on-call/
  - https://sre.google/sre-book/availability-table/
  - https://sre.google/workbook/table-of-contents/
  - https://sre.google/workbook/implementing-slos/
  - https://openslo.com/
  - https://response.pagerduty.com/
  - https://github.com/github/gh-ost
  - https://docs.percona.com/percona-toolkit/pt-online-schema-change.html
---

# SRE Operations 공식 문서 참조 노트

## 1. Incident Management (확인일: 2026-07-07)

출처: Google SRE Book Ch.14 "Managing Incidents"

### Google 정의 — 장애 관리 역할

| 역할                    | 책임                                                |
|-------------------------|-----------------------------------------------------|
| Incident Commander (IC) | 전체 조율, 의사결정, 커뮤니케이션 위임              |
| Operations Lead         | 실제 복구 작업 수행, IC에게 상황 보고               |
| Communications Lead     | 이해관계자 업데이트, 상태 페이지 관리               |
| Planning Lead           | 장기 장애 시 교대/자원 계획                         |

### 장애 관리 원칙 (Google SRE Book)

- Recursive Separation of Responsibilities — 역할 명확 분리
- A recognized command post — IC가 누구인지 모두가 알아야 함
- Live incident state document — 실시간 상태 문서 유지
- Clear, live handoff — 교대 시 명시적 인수인계

### On-Call과 Incident의 관계 (Ch.11)

출처: sre.google/sre-book/being-on-call/

- On-call engineer는 첫 번째 응답자이지 IC가 아님
- 장애 발생 시 IC를 별도 지정하고, 온콜은 Operations Lead로 전환
- 온콜 부하: 25% 이하 유지 권장 (나머지는 프로젝트 작업)

### Incident State Document (Appendix C)

출처: sre.google/sre-book/ Appendix C

필수 필드:
- Incident Commander (이름)
- Status (investigating/identified/monitoring/resolved)
- Summary (1~2문장)
- Impact (영향 서비스, 사용자 수, 지역)
- Timeline (분 단위)
- Next Steps + Owner

### PagerDuty Incident Response 프레임워크

출처: response.pagerduty.com

- Severity 분류: SEV-1 (Critical) ~ SEV-5 (Cosmetic)
- IC rotation: 온콜과 IC를 분리
- Status page update cadence: SEV-1은 15분마다

## 2. SLO / Error Budget (확인일: 2026-07-07)

출처: Google SRE Book Ch.4 "Service Level Objectives"

### 용어 정의 (공식)

| 용어 | Google 정의                                                          |
|------|----------------------------------------------------------------------|
| SLI  | A carefully defined quantitative measure of some aspect of the level of service |
| SLO  | A target value or range of values for a service level that is measured by an SLI |
| SLA  | An explicit or implicit contract with your users that includes consequences of meeting (or missing) the SLOs |

### Error Budget 공식

```
Error Budget = 1 - SLO

Example:
SLO = 99.9% availability
Error Budget = 0.1% = 43.2 minutes/month
```

### Implementing SLOs 절차 (SRE Workbook Ch.2)

출처: sre.google/workbook/implementing-slos/

1. SLI 선정 (availability, latency, throughput, correctness)
2. SLI 측정 방법 결정 (server-side, client-side, synthetic)
3. SLO 수치 설정 (사용자 기대치 기반, 초기에는 현재 성능 기반)
4. Error Budget Policy 수립 (budget 소진 시 feature freeze 등)
5. 대시보드 + 알림 설정
6. 주기적 리뷰 (quarterly SLO review)

### Availability Table (Appendix A)

출처: sre.google/sre-book/availability-table/

| 가용성   | 연간 다운타임 | 월간 다운타임 | 주간 다운타임 |
|----------|---------------|---------------|---------------|
| 99%      | 3.65일        | 7.31시간      | 1.68시간      |
| 99.9%    | 8.77시간      | 43.83분       | 10.08분       |
| 99.95%   | 4.38시간      | 21.92분       | 5.04분        |
| 99.99%   | 52.60분       | 4.38분        | 1.01분        |
| 99.999%  | 5.26분        | 26.30초       | 6.05초        |

### OpenSLO Spec (확인일: 2026-07-07)

출처: openslo.com

```yaml
apiVersion: openslo/v1
kind: SLO
metadata:
  name: api-availability
spec:
  service: my-api
  indicator:
    metadata:
      name: api-success-rate
    spec:
      ratioMetric:
        good:
          metricSource: prometheus
          spec: http_requests_total{code=~"2.."}
        total:
          metricSource: prometheus
          spec: http_requests_total
  objectives:
    - target: 0.999
      timeWindow:
        - duration: 30d
          isRolling: true
```

## 3. Capacity Planning (확인일: 2026-07-07)

출처: Google SRE Workbook Ch.11 "Managing Load"

### Google의 Capacity Planning 원칙

- "Plan to fail" — N+2 capacity (N+1은 불충분)
- Demand forecasting: linear regression 부족 → seasonal decomposition 사용
- Load testing: 실제 트래픽의 2x~3x로 stress test
- Headroom: 항상 50% headroom 유지 권장 (burst 대비)

### AWS Well-Architected — Performance Efficiency Pillar

출처: docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/

- PERF 1: How do you select the best performing architecture?
- PERF 2: How do you select your compute solution?
- PERF 4: How do you monitor your resources to ensure they are performing?

## 4. Change Management (확인일: 2026-07-07)

출처: Google SRE Book Ch.8 "Release Engineering", SRE Workbook Ch.6 "Eliminating Toil"

### 변경의 70% 법칙 (Google)

> "roughly 70% of outages are due to changes in a live system"
> — Google SRE Book, Chapter 8

### 변경 등급 (ITIL v4 기반)

| 등급      | 승인           | 예시                           |
|-----------|----------------|--------------------------------|
| Standard  | 사전 승인      | 패치 적용, 설정 변경           |
| Normal    | CAB 승인       | 새 서비스 배포, DB 마이그레이션 |
| Emergency | 긴급 승인 (1인) | SEV-1 핫픽스, 보안 패치        |

## 5. Postmortem (확인일: 2026-07-07)

출처: Google SRE Book Ch.15 "Postmortem Culture: Learning from Failure"

### Google Postmortem 원칙

- Blameless — 개인이 아닌 시스템 실패로 접근
- 모든 SEV-1/SEV-2 장애에 대해 작성 필수
- Action items는 버그 트래커에 등록, 담당자/기한 명시
- Postmortem 리뷰 미팅 필수 (작성만으로는 불충분)

### 필수 포함 항목

- Impact (영향 범위, 기간, 사용자 수)
- Root Cause (진짜 원인, 5 Whys)
- Timeline (분 단위 이벤트 기록)
- Action Items (preventive, not just corrective)
- Lessons Learned (what went well, what went wrong)

## 6. Zero-downtime Migration (확인일: 2026-07-07)

출처: 각 DB 공식 문서 + AWS DMS

### PostgreSQL Online Migration

- pg_logical replication (PG 10+) — DDL은 수동 복제 필요
- Expand-contract pattern: 새 컬럼 추가 → 듀얼 쓰기 → 이전 컬럼 제거

### MySQL Online DDL

- `ALTER TABLE ... ALGORITHM=INPLACE, LOCK=NONE` (InnoDB 5.6+)
- pt-online-schema-change (Percona) — 트리거 기반 복제
- gh-ost (GitHub) — binlog 기반 복제

### gh-ost (GitHub Online Schema Migrations)

출처: github.com/github/gh-ost

- Trigger-free: binlog stream 직접 파싱
- 원본 테이블에 트리거 설치 없음 (Percona pt-osc와 차이점)
- Throttle 지원: replication lag, CPU load 기반 자동 조절
- 테스트 모드: 

### Percona pt-online-schema-change

출처: docs.percona.com/percona-toolkit/pt-online-schema-change.html

- Trigger 기반: INSERT/UPDATE/DELETE 트리거로 변경 추적
- 검증된 안정성 (10년+ 프로덕션 사용)
- 제한: Foreign Key 있는 테이블에서 주의 필요

### AWS Database Migration Service

- Full load + CDC (Change Data Capture)
- 소스 중단 없이 대상으로 지속 복제
- 전환 시점: replication lag = 0 확인 후 DNS cutover
