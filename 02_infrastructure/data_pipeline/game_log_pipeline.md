# 게임 서버 로그 파이프라인 패턴

게임 서버 이벤트 로그 수집부터 분석까지의 표준 파이프라인 패턴을 정리합니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 기본 구조](#1-기본-구조) / [2. 단계별 상세](#2-단계별-상세) / [3. Flink vs Spark](#3-flink-vs-spark) |
| [4. Snowflake vs Athena](#4-snowflake-vs-athena) / [5. 실무 확장 패턴](#5-실무-확장-패턴)                |

## 1. 기본 구조

```
게임 서버
  │  (이벤트: 로그인, 구매, 전투, 오류 등)
  ▼
Kafka (버퍼/내구성)
  │
  ├──► Flink       (실시간 가공/집계, 수초 지연)
  │      ▼
  │    Redis / DynamoDB  (실시간 대시보드)
  │
  └──► Spark       (배치 ETL, 시간/일 단위)
         ▼
       Parquet (S3)
           │
           ├──► Athena     (임시 쿼리, 소규모 분석)
           └──► Snowflake  (정기 리포트, 대규모 분석)
```

Kafka가 중심 버퍼 역할을 하며 실시간(Flink)과 배치(Spark) 두 레인으로 분기합니다.

### raw 원본 보관 레인 (필수)

```
Kafka
  │
  └──► Kinesis Firehose ──► S3 raw (JSON 원본)
                                   │
                            Parquet 변환 로직에 버그 발생 시
                            raw에서 재처리 가능
```

Parquet 변환 전 JSON 원본을 S3에 따로 저장합니다.
Flink/Spark 로직 버그 발생 시 원본에서 재처리할 수 있습니다.

## 2. 단계별 상세

### 수집 — 게임 서버 → Kafka

| 항목     | 내용                                              |
|----------|---------------------------------------------------|
| 프로토콜 | Kafka Producer SDK (Java/C++/Go)                  |
| 포맷     | JSON (수집) → Parquet (저장)                      |
| 파티션   | 이벤트 타입별 토픽 분리 (login, purchase, battle) |
| 내구성   | acks=all, replication.factor=3                    |

### 버퍼 — Kafka (MSK)

| 항목       | 내용                                     |
|------------|------------------------------------------|
| 역할       | 속도 완충, 재처리 보장, 다운스트림 분리  |
| 보관       | 48시간 (장애 시 재처리 대비)             |
| AWS 관리형 | Amazon MSK (Managed Streaming for Kafka) |

### 가공 — Flink / Spark

Flink와 Spark는 용도가 다르며 병행 운영이 일반적입니다.
([§3 상세 비교](#3-flink-vs-spark) 참고)

### 저장 — Parquet + S3

| 항목      | 내용                                                  |
|-----------|-------------------------------------------------------|
| 포맷      | Parquet + gzip/snappy (원본 대비 ~10:1 압축)          |
| 파티션    | `year=YYYY/month=MM/day=DD/hour=HH/event_type=XX`     |
| 압축 효과 | 100GB/일 원본 → 약 10GB/일 Parquet                    |
| 이유      | Athena/Snowflake 쿼리 시 파티션 pruning으로 비용 절감 |

### 분석 — Snowflake / Athena

([§4 상세 비교](#4-snowflake-vs-athena) 참고)

## 3. Flink vs Spark

| 기준        | Flink                         | Spark (Structured Streaming) |
|-------------|-------------------------------|------------------------------|
| 처리 방식   | 진정한 스트리밍 (이벤트 단위) | 마이크로 배치 (시간 단위)    |
| 지연        | 밀리초~초                     | 수십초~분                    |
| 주 용도     | 실시간 알람, 세션 추적        | 배치 ETL, 복잡한 집계        |
| 상태 관리   | RocksDB 기반 강력한 상태 관리 | 제한적                       |
| SQL 친화도  | 낮음                          | 높음 (Spark SQL)             |
| AWS 관리형  | Amazon Managed Flink          | EMR / AWS Glue               |
| 운영 복잡도 | 높음                          | 낮음                         |

**게임 서버 적용 예시:**

Flink 적합:
- 동시 접속자 실시간 집계
- 이상 거래 감지 (초 단위 반응)
- 세션 타임아웃 감지

Spark 적합:
- 일별 매출 집계
- 사용자 행동 분석 리포트
- ML 피처 생성 (배치)

## 4. Snowflake vs Athena

| 기준        | Snowflake                       | Athena                     |
|-------------|---------------------------------|----------------------------|
| 쿼리 성능   | 빠름 (클러스터링, 캐시, 컴파일) | S3 스캔 속도에 종속        |
| 비용 구조   | 컴퓨팅 시간 과금 (idle시 $0)    | 스캔 데이터량 $5/TB        |
| 동시 사용자 | Multi-cluster로 자동 확장       | 제한적                     |
| 관리        | 관리형 SaaS (DBA 최소화)        | 서버리스                   |
| 데이터 적재 | Snowpipe (S3 → Snowflake 자동)  | S3 직접 참조 (적재 불필요) |
| 적합 규모   | TB~PB, 정기 분석                | GB~TB, 임시 쿼리           |

**선택 기준:**

- 분석팀이 있고 정기 리포트가 필요하면 → **Snowflake**
- 쿼리가 가끔이고 비용 최소화가 목적이면 → **Athena**
- 100TB/일 이상 규모 → **Snowflake** (Athena는 쿼리 비용 폭증)

## 5. 실무 확장 패턴

### 전체 확장 아키텍처

```
게임 서버 (다수 리전)
  │
  ▼
Kafka (MSK, per region)
  │
  ├──► Firehose ──► S3 raw JSON  (원본 보관, 재처리용)
  │
  ├──► Flink ──► Redis/DynamoDB  (실시간: DAU, 매출 현황)
  │         └──► SNS/PagerDuty  (이상 감지 알람)
  │
  └──► Spark (Glue/EMR)
         │
         ▼
       S3 Parquet (partitioned)
           │
           ├──► Athena      (임시 쿼리, 감사 로그 검색)
           ├──► Snowflake   (정기 분석, BI 대시보드)
           └──► SageMaker   (ML: 이탈 예측, 추천)
```

### 장애 대응

| 장애 유형      | 대응                                      |
|----------------|-------------------------------------------|
| Flink 장애     | Kafka offset 재처리 (48시간 이내)         |
| Spark ETL 버그 | S3 raw JSON에서 재처리                    |
| Snowflake 장애 | Athena로 임시 대체 (같은 S3 Parquet 참조) |
| Kafka 장애     | 게임 서버 로컬 스풀 후 복구 시 재전송     |

### 비용 최적화

```bash
# S3 Lifecycle 정책 예시
raw JSON:    Standard 30일 → Glacier Instant
Parquet:     Standard 90일 → Standard-IA → Glacier Instant (5년)
```

- Parquet 파티션을 촘촘하게 설계하면 Athena 스캔 비용이 크게 줄어듭니다.
- Snowflake는 쿼리 없는 시간에 Warehouse를 Auto-suspend하면 비용이 절감됩니다.

## 참고 자료

- Apache Flink: [flink.apache.org/docs](https://flink.apache.org/docs/) — ★★★☆☆
- Apache Spark: [spark.apache.org/docs](https://spark.apache.org/docs/latest/) — ★★★☆☆
- Amazon MSK: [docs.aws.amazon.com/msk](https://docs.aws.amazon.com/msk/latest/developerguide/) — ★★★☆☆
- Snowflake Architecture: [docs.snowflake.com/en/user-guide/intro-key-concepts](https://docs.snowflake.com/en/user-guide/intro-key-concepts) — ★★★☆☆
- [100GB/일 설계](./log_aggregation_100gb.md)
- [100TB/일 설계](./log_aggregation_100tb.md)

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-06-18

© 2026 siasia86. Licensed under CC BY 4.0.
