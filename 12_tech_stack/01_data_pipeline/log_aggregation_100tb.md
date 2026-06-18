# 로그 통합 서버 아키텍처 — 100TB/일 규모

감사/분석 목적, 5년 보관, AWS + IDC 혼합 환경 기준 설계입니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 요구사항](#1-요구사항) / [2. 아키텍처 개요](#2-아키텍처-개요) / [3. 컴포넌트 상세](#3-컴포넌트-상세) |
| [4. 스토리지 설계](#4-스토리지-설계) / [5. 비용 추산](#5-비용-추산) / [6. 구축 순서](#6-구축-순서)       |

## 1. 요구사항

| 항목                                  | 월 비용 (USD)   |
|---------------------------------------|-----------------|
| MSK kafka.m5.4xlarge × 6              | ~$8,000         |
| OpenSearch r6g.4xlarge × 9            | ~$15,000        |
| S3 Glacier Instant (누적 ~150PB 기준) | ~$15,000        |
| S3 Standard IA Parquet (18PB)         | ~$5,000         |
| Glue ETL (100TB/일 처리)              | ~$3,000         |
| Snowflake (Medium WH, 분석 사용량)    | ~$5,000         |
| Direct Connect (10Gbps × N회선)       | ~$10,000        |
| Kinesis Firehose                      | ~$2,000         |
| 합계 (5년차 기준)                     | **~$63,000/월** |

## 2. 아키텍처 개요

이 규모에서는 단일 Logstash/OpenSearch로 처리 불가합니다.
Kafka를 중심으로 한 스트리밍 파이프라인과 Snowflake를 장기 분석 레이어로 사용합니다.

```
IDC Servers                          AWS
┌──────────────┐                    ┌──────────────────────────────────────────────┐
│ App / DB     │                    │                                              │
│ OS / Infra   ├──Fluentd/Filebeat─►│  MSK (Kafka)  ◄── AWS Servers Filebeat       │
│              │                    │      │                                       │
└──────────────┘    Direct Connect  │      ├──► Kinesis Firehose ──► S3 (raw)      │
                    or DX + VPN     │      │         │                             │
                                    │      │    Glue ETL (JSON to Parquet)         │
                                    │      │         │                             │
                                    │      │    Snowflake  (archive 5yr)           │
                                    │      │    (Snowpipe auto-ingest)             │
                                    │      │                                       │
                                    │      └──► OpenSearch (hot: 7d)               │
                                    │               │                              │
                                    │           Kibana (ops dashboard)             │
                                    └──────────────────────────────────────────────┘
```

## 3. 컴포넌트 상세

### 수집 계층 — Fluentd / Filebeat

| 항목 | 내용                                              |
|------|---------------------------------------------------|
| IDC  | Fluentd Aggregator x N (IDC 내 중간 집계 후 전송) |
| AWS  | Filebeat -> MSK 직접 전송                         |
| 전송 | Direct Connect (10Gbps 이상) 필수                 |
| 버퍼 | 로컬 디스크 + Kafka 자체 내구성                   |

🟡 100TB/일 = 약 1.16GB/초입니다. Direct Connect 전용 회선 최소 10Gbps 필요합니다.

### 버퍼 계층 — MSK (Managed Kafka)

| 항목       | 내용                                          |
|------------|-----------------------------------------------|
| 역할       | 5년 장기 감사/분석 쿼리                       |
| 적재       | Snowpipe (S3 -> Snowflake 자동 스트리밍 적재) |
| 웨어하우스 | Multi-cluster (분석 부하에 따라 자동 확장)    |
| 파티션     | 날짜 + 소스 기준 클러스터링 키                |
| 장점       | 비정형 쿼리, 복잡한 JOIN, 대용량 집계 최적화  |

### 처리 계층 — Kinesis Firehose + Glue ETL

| 항목   | 내용                                          |
|--------|-----------------------------------------------|
| 역할   | Kafka → S3 raw 적재, Glue로 Parquet 변환      |
| Glue   | Spark 기반 ETL, 시간 단위 파티셔닝            |
| 파티션 | `year=YYYY/month=MM/day=DD/hour=HH/source=XX` |

### 단기 저장 — OpenSearch

| 항목     | 내용                                |
|----------|-------------------------------------|
| 역할     | 최근 7일 핫 데이터 운영 조회        |
| 인스턴스 | r6g.4xlarge.search × 9 (3 AZ × 3)   |
| 스토리지 | gp3 EBS 기준 클러스터 총 100TB 이상 |
| ILM      | 7일 후 S3로 이동                    |

🟡 100TB/일 규모에서 OpenSearch 보관은 7일 이내로 제한합니다. 그 이상은 Snowflake + S3에서 처리합니다.

### 장기 분석 — Snowflake

| 항목       | 내용                                         |
|------------|----------------------------------------------|
| 역할       | 5년 장기 감사/분석 쿼리                      |
| 적재       | Snowpipe (S3 → Snowflake 자동 스트리밍 적재) |
| 웨어하우스 | Multi-cluster (분석 부하에 따라 자동 확장)   |
| 파티션     | 날짜 + 소스 기준 클러스터링 키               |
| 장점       | 비정형 쿼리, 복잡한 JOIN, 대용량 집계 최적화 |

Snowflake가 이 규모에서 선택되는 이유:
- Parquet + S3 External Stage로 스토리지 비용 최소화
- 쿼리 시에만 컴퓨팅 비용 발생 (idle 시 $0)
- 5년 데이터 전체 스캔 쿼리에서 Athena보다 성능 우수

### 장기 저장 — S3

| 항목     | 내용                                                      |
|----------|-----------------------------------------------------------|
| raw 보관 | S3 Standard -> 30일 후 S3 Glacier Instant                 |
| 분석용   | Parquet 변환 후 S3 Standard IA (Snowflake External Stage) |
| 암호화   | SSE-KMS                                                   |
| 무결성   | Object Lock (Compliance mode, 5년)                        |

## 4. 스토리지 설계

```
수집 (원본)
    │
    ├──► MSK 48시간 버퍼
    │
    ├──► S3 raw (JSON) ──► 30일 후 Glacier Instant
    │
    └──► Glue ETL ──► S3 Parquet
                          │
                          ├──► Snowflake External Stage (5년 분석)
                          │
                          └──► OpenSearch (7일 핫 데이터)
```

### 용량 추산

| 구간                 | 압축률       | 일일  | 연간    | 5년   |
|----------------------|--------------|-------|---------|-------|
| 원본 JSON            | -            | 100TB | 36PB    | 180PB |
| Parquet+gzip         | ~10:1        | 10TB  | 3.6PB   | 18PB  |
| OpenSearch (7일)     | ~3:1         | 33TB  | (7일분) | -     |
| Snowflake (External) | Parquet 기준 | 10TB  | 3.6PB   | 18PB  |

## 5. 비용 추산

월 기준 (ap-northeast-2):

| 항목                                  | 월 비용 (USD)   |
|---------------------------------------|-----------------|
| MSK kafka.m5.4xlarge × 6              | ~$8,000         |
| OpenSearch r6g.4xlarge × 9            | ~$15,000        |
| S3 Glacier Instant (누적 ~150PB 기준) | ~$15,000        |
| S3 Standard IA Parquet (18PB)         | ~$5,000         |
| Glue ETL (100TB/일 처리)              | ~$3,000         |
| Snowflake (Medium WH, 분석 사용량)    | ~$5,000         |
| Direct Connect (10Gbps × N회선)       | ~$10,000        |
| Kinesis Firehose                      | ~$2,000         |
| 합계 (5년차 기준)                     | **~$63,000/월** |

🟡 비용의 대부분은 스토리지와 네트워크입니다. S3 Intelligent-Tiering 적용 시 스토리지 비용 추가 절감 가능합니다.

## 6. 구축 순서

| 단계 | 작업                                      | 우선순위 |
|------|-------------------------------------------|----------|
| 1    | S3 버킷 설계 (파티션, Object Lock, KMS)   | 높음     |
| 2    | Direct Connect 회선 증설 (10Gbps 이상)    | 높음     |
| 3    | MSK 클러스터 구성 + 토픽 설계             | 높음     |
| 4    | IDC Fluentd Aggregator 배포               | 높음     |
| 5    | Kinesis Firehose + S3 raw 적재 파이프라인 | 높음     |
| 6    | Glue ETL Job (JSON → Parquet 변환)        | 중간     |
| 7    | OpenSearch 클러스터 구성 + ILM 설정       | 중간     |
| 8    | Snowflake External Stage + Snowpipe 설정  | 중간     |
| 9    | 감사 쿼리 템플릿 작성 (Snowflake SQL)     | 낮음     |
| 10   | Kibana 대시보드 구성                      | 낮음     |

## 참고 자료

- Snowflake Documentation: [docs.snowflake.com](https://docs.snowflake.com/) — ★★★☆☆
- MSK Documentation: [docs.aws.amazon.com/msk](https://docs.aws.amazon.com/msk/latest/developerguide/) — ★★★☆☆
- AWS Glue: [docs.aws.amazon.com/glue](https://docs.aws.amazon.com/glue/latest/dg/) — ★★★☆☆
- Snowpipe: [docs.snowflake.com/en/user-guide/data-load-snowpipe](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro) — ★★★☆☆
- OpenSearch: [opensearch.org/docs](https://opensearch.org/docs/) — ★★★☆☆

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-06-18

© 2026 siasia86. Licensed under CC BY 4.0.
