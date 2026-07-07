# Zero-Downtime Migration

서비스 중단 없이 데이터베이스 스키마 변경, 데이터 이관, 인프라 전환을 수행하는 전략과 패턴입니다.

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 핵심 원칙](#2-핵심-원칙) / [3. DB 스키마 변경](#3-db-스키마-변경)                         |
| [4. 데이터 마이그레이션](#4-데이터-마이그레이션) / [5. 트래픽 전환](#5-트래픽-전환) / [6. 롤백 전략](#6-롤백-전략) |
| [7. 도구](#7-도구) / [8. 체크리스트](#8-체크리스트) / [9. 트러블슈팅](#9-트러블슈팅)                               |

## 1. 개요

| 항목 | 값                                                           |
|------|--------------------------------------------------------------|
| 목적 | 사용자 영향 없이 스키마/데이터/인프라 변경 수행              |
| 핵심 | 단계적 전환 (expand-contract), 듀얼 쓰기, 점진적 트래픽 이동 |
| 위험 | 데이터 불일치, 성능 저하, 롤백 불가 상태                     |
| 전제 | 충분한 테스트 + 롤백 계획 + 모니터링 준비                    |
| 연관 | Change Management (승인), Incident Management (실패 시)      |

## 2. 핵심 원칙

| 원칙                 | 설명                                               |
|----------------------|----------------------------------------------------|
| Expand then Contract | 새 구조 추가 → 이관 → 이전 구조 제거 (3단계)       |
| Backward Compatible  | 모든 중간 단계에서 이전/이후 코드 모두 동작해야 함 |
| Reversible           | 각 단계마다 롤백 가능해야 함                       |
| Incremental          | 빅뱅 전환 금지, 작은 단계로 분리                   |
| Observable           | 각 단계의 성공/실패를 측정할 수 있어야 함          |

### Expand-Contract Pattern

```
Phase 1: Expand
┌─────────────┐     ┌─────────────┐
│ Old Column  │     │ New Column  │   (both exist)
│ (still used)│     │ (populated) │
└─────────────┘     └─────────────┘
       │                   ^
       └── Dual Write ─────┘

Phase 2: Migrate
  - Backfill historical data
  - Verify consistency

Phase 3: Contract
┌────────────────┐
│ New Column     │   (old column removed)
│ (sole source)  │
└────────────────┘
```

## 3. DB 스키마 변경

### 안전한 DDL 작업

| 작업                  | MySQL (InnoDB)          | PostgreSQL                        |
|-----------------------|-------------------------|-----------------------------------|
| ADD COLUMN (nullable) | ✅ INSTANT (8.0.12+)    | ✅ Instant (no rewrite)           |
| ADD COLUMN (default)  | ✅ INSTANT (8.0.12+)    | ✅ Instant (11+, virtual default) |
| DROP COLUMN           | ✅ INPLACE              | ✅ Instant (mark only)            |
| ADD INDEX             | ✅ INPLACE, LOCK=NONE   | ✅ CREATE INDEX CONCURRENTLY      |
| RENAME COLUMN         | ✅ INSTANT              | ✅ Instant                        |
| CHANGE COLUMN TYPE    | ❌ Table rebuild (위험) | ❌ ACCESS EXCLUSIVE lock (위험)   |
| DROP INDEX            | ✅ INSTANT              | ✅ Instant                        |

### 위험한 작업 → 안전한 대안

| 위험한 작업                | 안전한 대안                                     |
|----------------------------|-------------------------------------------------|
| ALTER COLUMN TYPE          | 새 컬럼 추가 → 듀얼 쓰기 → 이전 컬럼 제거       |
| RENAME TABLE               | 새 테이블 생성 → 트리거/CDC → 이전 테이블 제거  |
| ADD NOT NULL (기존 데이터) | ADD NULLABLE → Backfill → ADD CONSTRAINT        |
| Large table ADD INDEX      | CREATE INDEX CONCURRENTLY (PG) / pt-osc (MySQL) |

## 4. 데이터 마이그레이션

### 전략 비교

| 전략                      | 설명                             | 적합 상황             |
|---------------------------|----------------------------------|-----------------------|
| Dual Write                | 양쪽에 동시 쓰기                 | 실시간 전환 필요      |
| CDC (Change Data Capture) | binlog/WAL 스트리밍              | 대용량 + 실시간       |
| Batch + CDC               | 초기 벌크 복사 후 CDC로 따라잡기 | 대용량 초기 데이터    |
| Shadow Traffic            | 읽기만 신규로 복제하여 검증      | 신규 시스템 검증 단계 |

### CDC 기반 마이그레이션 흐름

```
Source DB ──(binlog/WAL)──> CDC Tool ──> Target DB
                                │
                                v
                         Lag Monitor
                         (lag = 0 → cutover ready)
```

### Dual Write 구현 패턴

```
Application
     │
     ├── Write to Old DB (primary)
     │
     └── Write to New DB (secondary, async)
            │
            v
     Consistency Checker (periodic)
            │
            └── Mismatch → Alert + Reconcile
```

## 5. 트래픽 전환

### 전환 전략

| 전략         | 방법                      | 롤백 시간  | 위험도 |
|--------------|---------------------------|------------|--------|
| DNS Switch   | Route 53 Weighted → 0/100 | 수분 (TTL) | 낮음   |
| Blue-Green   | LB target group 전환      | 즉시       | 낮음   |
| Canary       | 1% → 5% → 25% → 100% 점진 | 즉시       | 낮음   |
| Feature Flag | 코드 레벨 분기            | 즉시       | 낮음   |

### Canary 전환 절차

```
Step 1: 1% traffic to new
     │
     ├── Monitor 15min (error rate, latency)
     │
     ├── OK? → Step 2: 10% traffic
     │         │
     │         ├── Monitor 30min
     │         │
     │         ├── OK? → Step 3: 50% traffic
     │         │         │
     │         │         ├── Monitor 1hr
     │         │         │
     │         │         └── OK? → Step 4: 100%
     │         │
     │         └── FAIL? → Rollback to 0%
     │
     └── FAIL? → Rollback to 0%
```

### 전환 판단 기준

| 지표             | Pass 기준         | Fail 기준        |
|------------------|-------------------|------------------|
| Error rate       | < baseline + 0.1% | > baseline + 1%  |
| p99 latency      | < baseline + 20%  | > baseline + 50% |
| Data consistency | mismatch = 0      | mismatch > 0     |
| Replication lag  | < 1s              | > 10s            |

## 6. 롤백 전략

### 롤백 가능성 평가

| 변경 유형              | 롤백 가능? | 방법                      |
|------------------------|------------|---------------------------|
| ADD COLUMN (nullable)  | ✅         | DROP COLUMN               |
| Dual Write (진행 중)   | ✅         | 신규 쓰기 중단            |
| Traffic shift (canary) | ✅         | Weight → 0                |
| DROP COLUMN (완료)     | ❌         | 복구 불가 (백업에서 복원) |
| Data backfill (완료)   | 🟡         | 원본 보존 시에만 가능     |

### 롤백 자동화

```yaml
# rollback criteria (자동 트리거)
rollback_trigger:
  error_rate: "> 5% for 5min"
  latency_p99: "> 3s for 5min"
  data_mismatch: "> 0 records"

rollback_action:
  - revert traffic weight to 0%
  - disable dual-write to new target
  - alert on-call + IC
```

## 7. 도구

| 도구                    | 용도                            | 특징                      |
|-------------------------|---------------------------------|---------------------------|
| gh-ost (GitHub)         | MySQL Online DDL                | Trigger-free, binlog 기반 |
| pt-online-schema-change | MySQL Online DDL                | Trigger 기반, 검증됨      |
| pg_logical replication  | PostgreSQL 이관                 | DDL 수동 복제 필요        |
| AWS DMS                 | Cross-engine/cross-account 이관 | Full load + CDC           |
| Debezium                | CDC (Kafka Connect)             | 다양한 DB 지원            |
| Flyway / Liquibase      | 스키마 버전 관리                | CI/CD 연동                |

## 8. 체크리스트

### 마이그레이션 전

- [ ] 롤백 계획 문서화 (각 단계별)
- [ ] 모니터링 대시보드 준비 (error rate, latency, lag)
- [ ] 스테이징에서 전체 절차 리허설 완료
- [ ] 데이터 검증 쿼리 준비
- [ ] 관련 팀 사전 공지 (변경 윈도우)
- [ ] Backup 확인 (Point-in-time recovery 가능)

### 마이그레이션 중

- [ ] 각 단계 후 검증 (자동 + 수동)
- [ ] Replication lag 실시간 모니터링
- [ ] 롤백 기준 도달 시 즉시 실행
- [ ] 커뮤니케이션 채널 활성 (Slack/Bridge)

### 마이그레이션 후

- [ ] 데이터 정합성 최종 검증
- [ ] 이전 리소스 정리 (보존 기간 후)
- [ ] Postmortem/Review 작성 (lessons learned)
- [ ] 모니터링 임계값 복원

## 9. 트러블슈팅

| 증상                     | 원인                          | 해결                                   |
|--------------------------|-------------------------------|----------------------------------------|
| Dual write 시 성능 저하  | 동기식 이중 쓰기              | 비동기 + 큐 기반으로 전환              |
| 데이터 불일치            | CDC lag 중 전환               | lag=0 확인 후에만 cutover              |
| DDL 중 Lock wait timeout | Long-running transaction 존재 | 트랜잭션 종료 대기 또는 pt-kill 사용   |
| 롤백 후에도 데이터 손실  | Contract 단계 이후 롤백 시도  | Contract 전 충분한 대기 (1주+) 확보    |
| Canary 중 일부만 실패    | Session affinity 미설정       | Sticky session 또는 consistent hashing |

> 무중단 마이그레이션 패턴(Strangler Fig, Blue-Green, Canary)은 Martin Fowler의 "Strangler Fig Application" 패턴(2004)과 AWS의 Migration Strategies(6 Rs)에 기반합니다.
> — https://martinfowler.com/bliki/StranglerFigApplication.html
> — https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-retiring-applications/apg-gloss.html

## 참고 자료

- gh-ost: [github.com/github/gh-ost](https://github.com/github/gh-ost) — ★★★☆☆
- Percona pt-online-schema-change: [docs.percona.com](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html) — ★★★☆☆
- AWS DMS: [docs.aws.amazon.com/dms](https://docs.aws.amazon.com/dms/latest/userguide/) — ★★★☆☆
- Martin Fowler: [Expand-Contract](https://martinfowler.com/bliki/ParallelChange.html) — ★★☆☆☆

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
