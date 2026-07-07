# SLO & Error Budget

서비스 신뢰성 목표(SLO)를 정의하고 Error Budget을 운영하여 배포 속도와 안정성의 균형을 잡는 프레임워크입니다. Google SRE Book Ch.4와 SRE Workbook Ch.2를 기반으로 합니다.

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 용어 정의](#2-용어-정의) / [3. SLI 설계](#3-sli-설계)                                     |
| [4. SLO 설정](#4-slo-설정) / [5. Error Budget](#5-error-budget) / [6. Error Budget Policy](#6-error-budget-policy) |
| [7. 구현](#7-구현) / [8. 운영 주기](#8-운영-주기) / [9. 트러블슈팅](#9-트러블슈팅)                                 |

## 1. 개요

| 항목      | 값                                                          |
|-----------|-------------------------------------------------------------|
| 목적      | 신뢰성 목표를 정량화하여 의사결정 기준으로 활용             |
| 출처      | Google SRE Book Ch.4, SRE Workbook Ch.2, OpenSLO            |
| 핵심 질문 | "얼마나 신뢰할 수 있어야 하는가?"                           |
| 전제      | 100% 가용성은 불가능하며, 목표 이상의 신뢰성은 낭비         |
| 연관 문서 | Incident Management (SLO 위반 시), Capacity Planning (여유) |

## 2. 용어 정의

| 용어 | 정의 (Google 공식)                                                                                      |
|------|---------------------------------------------------------------------------------------------------------|
| SLI  | A carefully defined quantitative measure of some aspect of the level of service                         |
| SLO  | A target value or range of values for a service level that is measured by an SLI                        |
| SLA  | An explicit or implicit contract with users that includes consequences of meeting (or missing) the SLOs |

### 관계도

```
SLI (measurement) ──> SLO (target) ──> SLA (contract)
  "what we measure"    "what we aim"    "what we promise"
       99.95%              99.9%             99.5%
    (actual)           (internal)        (external)
```

- SLI > SLO: 정상 운영 (Error Budget 남음)
- SLI < SLO: Error Budget 소진 중
- SLI < SLA: 계약 위반 (비용 발생)

## 3. SLI 설계

### SLI 유형

| SLI 유형     | 측정 대상        | 계산 방식                                     |
|--------------|------------------|-----------------------------------------------|
| Availability | 요청 성공 비율   | (good requests / total requests) * 100        |
| Latency      | 응답 시간 분포   | (requests < threshold / total requests) * 100 |
| Throughput   | 처리량           | requests per second (good only)               |
| Correctness  | 정확한 응답 비율 | (correct responses / total responses) * 100   |

### SLI 측정 위치

| 위치          | 장점                       | 단점                 | 예시                |
|---------------|----------------------------|----------------------|---------------------|
| Client-side   | 사용자 체감과 가장 가까움  | 계측 어려움          | RUM, Mobile SDK     |
| Load Balancer | 인프라 변경 없이 측정 가능 | 내부 지연 미포함     | ALB Access Log      |
| Server-side   | 구현 쉬움                  | 네트워크 지연 미포함 | Application Metrics |
| Synthetic     | 일관된 측정 환경           | 실제 트래픽 미반영   | Blackbox Exporter   |

### SLI 설계 원칙

- 사용자가 체감하는 지표를 선택합니다
- 내부 시스템 지표(CPU, 메모리)는 SLI가 아닙니다
- SLI는 비율(ratio)로 표현합니다 (0~100%)
- 서비스당 SLI는 3~5개 이하로 유지합니다

## 4. SLO 설정

### Availability Table

| SLO     | 연간 다운타임 | 월간 다운타임 | 주간 다운타임 |
|---------|---------------|---------------|---------------|
| 99%     | 3.65일        | 7.31시간      | 1.68시간      |
| 99.9%   | 8.77시간      | 43.83분       | 10.08분       |
| 99.95%  | 4.38시간      | 21.92분       | 5.04분        |
| 99.99%  | 52.60분       | 4.38분        | 1.01분        |
| 99.999% | 5.26분        | 26.30초       | 6.05초        |

### SLO 설정 절차

```
1. 현재 SLI 측정 (baseline)
     │
     v
2. 사용자 기대치 파악
     │
     v
3. SLO 초안 설정 (현재 성능보다 약간 낮게)
     │
     v
4. 4주간 시범 운영 (SLO 위반 빈도 관찰)
     │
     v
5. 조정 + 공식 적용
     │
     v
6. Quarterly Review (분기별 재평가)
```

### SLO 설정 기준

| 서비스 유형       | 권장 SLO          | 근거                     |
|-------------------|-------------------|--------------------------|
| 사용자 대면 API   | 99.9% ~ 99.95%    | 사용자 이탈 임계값       |
| 내부 API          | 99.5% ~ 99.9%     | 재시도 가능, 비동기 처리 |
| 배치 처리         | 99% ~ 99.5%       | 일정 지연 허용           |
| 데이터 파이프라인 | 99.9% (freshness) | 비즈니스 결정에 영향     |

## 5. Error Budget

### 계산

```
Error Budget = 1 - SLO

Example:
  SLO = 99.9%
  Error Budget = 0.1% = 43.83 minutes/month

  Month starts: 43.83 min available
  After incident (15 min): 28.83 min remaining
  After deploy rollback (5 min): 23.83 min remaining
```

### Error Budget 소진 추적

```
100% ┬───────────────────────────────────────── Budget Start
     │\
     │ \  Incident #1 (15 min)
     │  \___________________________________
65%  │   \
     │    \  Bad Deploy (5 min)
     │     \_______________________________
54%  │                                      
     │         Normal operation
     │         (gradual degradation)
20%  │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  Warning (20%)
     │
 0%  └───────────────────────────────────────── Budget Exhausted
     Day 1                                Month End
```

## 6. Error Budget Policy

### Budget 상태별 행동

| Budget 잔여 | 상태     | 행동                                            |
|-------------|----------|-------------------------------------------------|
| > 50%       | Healthy  | 정상 배포, Feature 개발 우선                    |
| 20% ~ 50%   | Warning  | 리스크 높은 변경 자제, 안정성 작업 병행         |
| < 20%       | Critical | Feature freeze, 안정성 작업만 허용              |
| 0% (소진)   | Frozen   | 모든 비필수 변경 중단, Postmortem + 개선만 진행 |

### Policy 예시 (YAML)

```yaml
error_budget_policy:
  service: payment-api
  slo: 99.95%
  window: 30d rolling

  actions:
    healthy:  # > 50%
      - normal deployments allowed
      - feature work prioritized
    warning:  # 20-50%
      - risky changes require extra review
      - reliability work added to sprint
    critical:  # < 20%
      - feature freeze
      - only bug fixes and reliability improvements
    exhausted:  # 0%
      - all non-essential changes halted
      - postmortem required for budget consumers
      - management escalation
```

## 7. 구현

### Prometheus + Grafana 예시

```yaml
# prometheus/rules/slo.yml
groups:
  - name: slo-api
    rules:
      - record: sli:availability:ratio_rate30d
        expr: |
          sum(rate(http_requests_total{code=~"2.."}[30d]))
          /
          sum(rate(http_requests_total[30d]))

      - alert: ErrorBudgetBurnRateHigh
        expr: |
          1 - sli:availability:ratio_rate1h > 14.4 * (1 - 0.999)
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error budget burn rate is 14.4x normal"
```

### Burn Rate Alert (Multi-window)

| Window | Burn Rate | Budget 소진 예상 | Alert 의미           |
|--------|-----------|------------------|----------------------|
| 1h     | 14.4x     | 2%/hour          | 빠른 소진, 즉시 대응 |
| 6h     | 6x        | 5%/6hours        | 중간 속도 소진       |
| 3d     | 1x        | 10%/3days        | 느린 소진, 모니터링  |

### OpenSLO 정의

```yaml
apiVersion: openslo/v1
kind: SLO
metadata:
  name: payment-api-availability
spec:
  service: payment-api
  indicator:
    metadata:
      name: success-rate
    spec:
      ratioMetric:
        good:
          metricSource:
            type: prometheus
            spec:
              query: http_requests_total{service="payment",code=~"2.."}
        total:
          metricSource:
            type: prometheus
            spec:
              query: http_requests_total{service="payment"}
  objectives:
    - target: 0.999
      timeWindow:
        - duration: 30d
          isRolling: true
```

## 8. 운영 주기

### SLO Review Cycle

| 주기      | 활동                              | 참여자        |
|-----------|-----------------------------------|---------------|
| Daily     | Error Budget 대시보드 확인        | 온콜 엔지니어 |
| Weekly    | Budget 소진 추세 리뷰             | 팀 리드       |
| Monthly   | SLO 달성률 보고, Policy 적용 판단 | 팀 + PM       |
| Quarterly | SLO 수치 재평가, SLI 적절성 검토  | 팀 + 경영진   |

### SLO 재조정 기준

| 상황                             | 조정 방향                 |
|----------------------------------|---------------------------|
| 3개월 연속 Budget 100% 잔여      | SLO 상향 검토             |
| 매월 Budget 소진                 | SLO 하향 또는 안정성 투자 |
| 사용자 불만 증가 but SLO 달성 중 | SLI 재설계 필요           |
| 비즈니스 요구사항 변경           | SLO 전면 재설정           |

## 9. 트러블슈팅

| 증상                          | 원인                          | 해결                                 |
|-------------------------------|-------------------------------|--------------------------------------|
| SLO 항상 달성 (Budget 100%)   | SLO가 너무 낮음               | 현재 성능 대비 SLO 상향              |
| Budget 매월 소진              | SLO가 너무 높거나 안정성 부족 | SLO 하향 또는 안정성 투자 증대       |
| SLI가 사용자 불만을 반영 못함 | SLI 설계 오류                 | Client-side 측정 추가, SLI 재설계    |
| Error Budget Policy 무시      | 조직 합의 부재                | 경영진 포함 Policy 재승인            |
| Alert fatigue (과다 알림)     | Burn rate 임계값 부적절       | Multi-window alert 적용, 임계값 조정 |

> SLO/SLI/Error Budget 개념은 Google SRE Book Ch.4 "Service Level Objectives"에서 최초 정립되었습니다. Error Budget Policy는 Google SRE Workbook Ch.2에서 상세히 다룹니다.
> — https://sre.google/sre-book/service-level-objectives/
> — https://sre.google/workbook/error-budget-policy/

## 참고 자료

- Google SRE Book Ch.4: [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — ★★★★☆
- Google SRE Workbook Ch.2: [Implementing SLOs](https://sre.google/workbook/implementing-slos/) — ★★★★☆
- Google SRE Book Appendix A: [Availability Table](https://sre.google/sre-book/availability-table/) — ★★★★☆
- OpenSLO: [openslo.com](https://openslo.com/) — ★★★☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
