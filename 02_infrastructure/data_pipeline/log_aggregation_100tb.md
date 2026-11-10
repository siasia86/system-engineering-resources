# 로그 통합 서버 아키텍처 — 100TB/일 규모

감사/분석 목적, 5년 보관, AWS + IDC 혼합 환경 기준 설계입니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 요구사항](#1-요구사항) / [2. 아키텍처 개요](#2-아키텍처-개요) / [3. 컴포넌트 상세](#3-컴포넌트-상세) |
| [4. 스토리지 설계](#4-스토리지-설계) / [5. 비용 추산](#5-비용-추산) / [6. 구축 순서](#6-구축-순서)       |

## 1. 요구사항

| 항목          | 요구                                                                  | 관련 절             |
|---------------|-----------------------------------------------------------------------|---------------------|
| 목적·보관     | 감사·분석, 5년 보관                                                   | 서두                |
| 환경          | AWS + IDC 혼합, AWS 서울 리전(ap-northeast-2)                         | 서두, 5절           |
| 수집량        | 원본 JSON 100TB/일 (평균 약 1.16GB/초)                                | 제목, 3절 수집 계층 |
| IDC→AWS 전송  | Direct Connect 10Gbps 이상                                            | 3절 수집 계층       |
| 버퍼          | MSK에 수집 원본 48시간 보관                                           | 4절                 |
| 운영 조회     | OpenSearch 최근 7일, 일일 약 33TB(~3:1)                               | 3절 단기 저장, 4절  |
| 원본 보관     | S3 Standard 30일 → S3 Glacier Instant Retrieval, 5년 누적 180PB       | 3절 장기 저장, 4절  |
| 분석용 데이터 | Glue로 Parquet 변환(~10:1, 일일 10TB) → S3 Standard-IA, 5년 누적 18PB | 3절, 4절            |
| 장기 분석     | Snowflake에서 5년 감사·분석 쿼리                                      | 3절 장기 분석       |
| 보안·무결성   | SSE-KMS 암호화, Object Lock Compliance 모드 5년                       | 3절 장기 저장       |

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
                                    │           OpenSearch Dashboards              │
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

| 항목   | 내용                                                                                    |
|--------|-----------------------------------------------------------------------------------------|
| 역할   | 수집 원본 48시간 버퍼, Firehose·OpenSearch로 분배                                       |
| 브로커 | kafka.m5.4xlarge × 36 (3 AZ × 12)                                                       |
| 복제   | 복제 계수 3, min.insync.replicas 2 (MSK 3 AZ 기본값)                                    |
| 저장   | 100TB × 2일 × 복제 3 = 600TB, 브로커당 약 15.2TiB (최대 16,384GiB)                      |
| 한도   | 브로커 수는 AZ 수의 배수, 기본 한도는 클러스터당 ZooKeeper 30대·KRaft 60대, 계정당 90대 |

🟡 생산자 압축을 쓰지 않은 원본 기준입니다. 압축을 적용하면 저장량과 브로커 수가 압축률만큼 줄어듭니다. 브로커 36대는 ZooKeeper 기반 클러스터의 기본 한도(30대)를 넘으므로 KRaft 기반 클러스터로 구성합니다.

### 처리 계층 — Kinesis Firehose + Glue ETL

| 항목   | 내용                                          |
|--------|-----------------------------------------------|
| 역할   | Kafka → S3 raw 적재, Glue로 Parquet 변환      |
| Glue   | Spark 기반 ETL, 시간 단위 파티셔닝            |
| 파티션 | `year=YYYY/month=MM/day=DD/hour=HH/source=XX` |

### 단기 저장 — OpenSearch

| 항목     | 내용                                          |
|----------|-----------------------------------------------|
| 역할     | 최근 7일 핫 데이터 운영 조회                  |
| 인스턴스 | r6g.4xlarge.search × 48 (3 AZ × 16)           |
| 스토리지 | gp3 EBS 클러스터 약 608TB (노드당 최대 12TiB) |
| ISM      | 7일 후 S3로 이동                              |

🟡 100TB/일 규모에서 OpenSearch 보관은 7일 이내로 제한합니다. 그 이상은 Snowflake + S3에서 처리합니다.

### 장기 분석 — Snowflake

| 항목       | 내용                                         |
|------------|----------------------------------------------|
| 역할       | 5년 장기 감사/분석 쿼리                      |
| 적재       | Snowpipe (S3 → Snowflake 자동 연속 적재)     |
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

월 기준 (ap-northeast-2, 5년차 누적 용량):

| 항목                               | 산식                                                                                        | 월 비용 (USD)                  |
|------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------|
| MSK 브로커 kafka.m5.4xlarge        | 36대 × 730시간 × $2.065                                                                     | $54,268                        |
| MSK 브로커 저장                    | 600TB × $0.114/GB                                                                           | $68,400                        |
| OpenSearch r6g.4xlarge.search      | 48대 × 730시간 × $1.62                                                                      | $56,765                        |
| OpenSearch gp3 EBS                 | 608TB × $0.1391/GB                                                                          | $84,573                        |
| Kinesis Firehose (MSK 원본)        | 3,040TB(100TB × 30.4일), 구간 $0.068·$0.058·$0.050/GB                                       | $173,504                       |
| S3 Standard (raw 30일분)           | 3PB, 구간 $0.025·$0.024·$0.023/GB                                                           | $69,563                        |
| S3 Glacier Instant Retrieval (raw) | 177PB(180PB − 최근 30일 3PB) × $0.005/GB                                                    | $885,000                       |
| S3 Standard-IA (Parquet)           | 18PB × $0.0138/GB                                                                           | $248,400                       |
| Glue ETL                           | DPU-시간 × $0.44 (Glue 6.0 이상 $0.308)                                                     | 사용량에 따라 다름             |
| Snowflake                          | Medium WH 4크레딧/시간 × 가동 시간 + Snowpipe 적재 GB당 크레딧, 크레딧 단가는 에디션·계약별 | 사용량에 따라 다름             |
| Direct Connect 10Gbps              | 회선 수 × 730시간 × $2.25(전용 포트) + 회선 사업자 비용, 수신 전송 $0/GB                    | 회선당 포트 $1,643 + 계약 비용 |
| 합계 (금액을 정한 8개 항목)        |                                                                                             | **~$1,640,000/월**             |

- 브로커 수: 600TB ÷ 브로커당 최대 16,384GiB(약 17.6TB) = 34.1 → AZ 3의 배수로 36대
- OpenSearch 노드 수: 33TB × 7일 × 2(주 + 복제본 1) ÷ 0.95 ÷ 0.8 ≈ 608TB(AWS 저장 용량 산식, 33TB를 인덱스 크기로 보아 인덱싱 오버헤드 제외) ÷ 노드당 gp3 최대 12TiB(약 13.2TB) = 46.1 → 48대
- 단가: AWS Price List API 서울(ap-northeast-2) 온디맨드 파일(MSK 2026-11-10, OpenSearch 2026-11-06, Firehose 2026-11-04, S3 2026-11-09, Glue·Direct Connect 2026-11-08 게시, 2026-11-10 확인), 세금·할인·약정 제외. 1PB = 1,000TB = 1,000,000GB(10진 근사), 월 730시간, 월 수집량은 30.4일로 계산합니다.
- 제외: S3 요청·조회·수명 주기 전환 요청, KMS 요청, AZ 간 전송, OpenSearch 전용 마스터 노드와 기본값을 넘는 gp3 IOPS·처리량, MSK에서 OpenSearch로 적재하는 도구

🟡 금액을 정한 항목의 약 73%가 S3 장기 저장입니다. 저장 등급·보관 기간을 바꾸는 절감안(예: 접근이 드문 Parquet에 S3 Intelligent-Tiering 적용)은 감사 요구와 함께 결정합니다.

## 6. 구축 순서

| 단계 | 작업                                      | 우선순위 |
|------|-------------------------------------------|----------|
| 1    | S3 버킷 설계 (파티션, Object Lock, KMS)   | 높음     |
| 2    | Direct Connect 회선 증설 (10Gbps 이상)    | 높음     |
| 3    | MSK 클러스터 구성 + 토픽 설계             | 높음     |
| 4    | IDC Fluentd Aggregator 배포               | 높음     |
| 5    | Kinesis Firehose + S3 raw 적재 파이프라인 | 높음     |
| 6    | Glue ETL Job (JSON → Parquet 변환)        | 중간     |
| 7    | OpenSearch 클러스터 구성 + ISM 설정       | 중간     |
| 8    | Snowflake External Stage + Snowpipe 설정  | 중간     |
| 9    | 감사 쿼리 템플릿 작성 (Snowflake SQL)     | 낮음     |
| 10   | OpenSearch Dashboards 구성                | 낮음     |

## 참고 자료

- Snowflake Documentation: [docs.snowflake.com](https://docs.snowflake.com/) — ★★★☆☆
- MSK Documentation: [docs.aws.amazon.com/msk](https://docs.aws.amazon.com/msk/latest/developerguide/) — ★★★☆☆
- AWS Glue: [docs.aws.amazon.com/glue](https://docs.aws.amazon.com/glue/latest/dg/) — ★★★☆☆
- Snowpipe: [docs.snowflake.com/en/user-guide/data-load-snowpipe](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro) — ★★★☆☆
- OpenSearch: [opensearch.org/docs](https://opensearch.org/docs/) — ★★★☆☆
- OpenSearch Index State Management: [docs.opensearch.org](https://docs.opensearch.org/latest/im-plugin/ism/index/) — ★★★☆☆
- Amazon OpenSearch Service Dashboards: [docs.aws.amazon.com/opensearch-service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/dashboards.html) — ★★★☆☆
- Amazon MSK 할당량(브로커당 저장·브로커 수): [docs.aws.amazon.com/msk](https://docs.aws.amazon.com/msk/latest/developerguide/limits.html) — ★★★☆☆
- Amazon MSK 기본 구성(복제 계수): [docs.aws.amazon.com/msk](https://docs.aws.amazon.com/msk/latest/developerguide/msk-default-configuration.html) — ★★★☆☆
- Amazon MSK 브로커 수 변경(AZ 배수): [docs.aws.amazon.com/msk](https://docs.aws.amazon.com/msk/latest/developerguide/msk-update-broker-count.html) — ★★★☆☆
- OpenSearch Service 저장 용량 산정: [docs.aws.amazon.com/opensearch-service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp-storage.html) — ★★★☆☆
- OpenSearch Service 할당량(EBS 크기): [docs.aws.amazon.com/opensearch-service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/limits.html) — ★★★☆☆
- Snowflake 웨어하우스 크기와 크레딧: [docs.snowflake.com](https://docs.snowflake.com/en/user-guide/warehouses-overview) — ★★★☆☆
- AWS Price List Bulk API: [docs.aws.amazon.com/awsaccountbilling](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api.html) — ★★★☆☆
- Amazon MSK 요금: [aws.amazon.com/msk/pricing](https://aws.amazon.com/msk/pricing/) — ★★★☆☆
- Amazon OpenSearch Service 요금: [aws.amazon.com/opensearch-service/pricing](https://aws.amazon.com/opensearch-service/pricing/) — ★★★☆☆
- Amazon Data Firehose 요금: [aws.amazon.com/firehose/pricing](https://aws.amazon.com/firehose/pricing/) — ★★★☆☆
- Amazon S3 요금: [aws.amazon.com/s3/pricing](https://aws.amazon.com/s3/pricing/) — ★★★☆☆
- AWS Glue 요금: [aws.amazon.com/glue/pricing](https://aws.amazon.com/glue/pricing/) — ★★★☆☆
- AWS Direct Connect 요금: [aws.amazon.com/directconnect/pricing](https://aws.amazon.com/directconnect/pricing/) — ★★★☆☆

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-11-10

© 2026 siasia86. Licensed under CC BY 4.0.
