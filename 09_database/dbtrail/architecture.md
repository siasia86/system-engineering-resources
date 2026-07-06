# dbtrail 아키텍처

dbtrail 내부 동작 원리, 데이터 흐름, 저장 구조를 상세히 설명합니다.

## 목차

| 섹션                                                                                         |
|----------------------------------------------------------------------------------------------|
| [1. 전체 흐름](#1-전체-흐름) / [2. 스트리밍](#2-스트리밍) / [3. 저장 구조](#3-저장-구조)     |
| [4. 인덱싱](#4-인덱싱) / [5. 스키마 스냅샷](#5-스키마-스냅샷) / [6. 용량 계획](#6-용량-계획) |

---

## 1. 전체 흐름

```
Source MySQL                    bintrail                        Storage
┌──────────────┐               ┌──────────────────┐            ┌──────────┐
│ binlog_format│               │                  │            │          │
│ = ROW        │──replication─>│ bintrail stream  │──Parquet──>│ S3       │
│ binlog_row   │  protocol     │                  │            │          │
│ _image=FULL  │               │  schema snapshot │            └────┬─────┘
└──────────────┘               │  gap detection   │                 │      
                               │  rotation        │                 v      
                               └──────────────────┘            ┌──────────┐
                                                               │ DuckDB   │
                                                               │ (index)  │
                                                               └────┬─────┘
                                                                    │      
                                              ┌─────────────────────┼──────
                                              v                     v         v
                                        query/recover       reconstruct   verify
```

### 동작 순서

1. `bintrail doctor` — MySQL 설정 점검 (binlog_format, binlog_row_image)
2. `bintrail stream` — 복제 프로토콜(`COM_BINLOG_DUMP`)로 binlog 이벤트 수신
3. 이벤트를 Parquet 파일로 변환 → S3 업로드
4. `bintrail index` — Parquet → DuckDB 인덱싱
5. 사용자가 query/recover/reconstruct 명령으로 데이터 조회·복구

### 프로토콜 레벨

```
MySQL                           bintrail
  │                                │
  │<── COM_REGISTER_SLAVE ─────────│  (replica register)
  │                                │
  │<── COM_BINLOG_DUMP_GTID ───────│  (start streaming)
  │                                │
  │─── ROTATE_EVENT ──────────────>│
  │─── TABLE_MAP_EVENT ───────────>│  (table ID mapping)
  │─── WRITE_ROWS_EVENT ─────────>│  (INSERT)
  │─── UPDATE_ROWS_EVENT ────────>│  (UPDATE: before+after)
  │─── DELETE_ROWS_EVENT ────────>│  (DELETE: before image)
  │─── GTID_LOG_EVENT ───────────>│  (transaction ID)
  │─── XID_EVENT ─────────────────>│  (commit)
  │                                │
  │   (continuous stream, connection stays open)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 스트리밍

### MySQL 사용자 권한

```sql
CREATE USER 'dbtrail'@'%' IDENTIFIED BY 'SecurePassword123';
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'dbtrail'@'%';
```

| 권한                 | 용도                                                       |
|----------------------|------------------------------------------------------------|
| `REPLICATION SLAVE`  | binlog 이벤트 스트림 수신 (`COM_BINLOG_DUMP`)              |
| `REPLICATION CLIENT` | 시작 위치 탐색 (`SHOW BINARY LOG STATUS`, `@@gtid_purged`) |
| `SELECT`             | information_schema에서 스키마 스냅샷 (컬럼 타입, PK, FK)   |

🟡 dbtrail은 소스 DB에 **쓰기를 하지 않으며 잠금도 걸지 않습니다.** `RELOAD`, `LOCK TABLES`, `PROCESS` 권한이 불필요합니다.

### 최소 권한 (스키마 제한)

```sql
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'dbtrail'@'%';
GRANT SELECT ON shop.* TO 'dbtrail'@'%';  -- 모니터링할 스키마만
```

### 갭 탐지

스트리밍 중단 후 재개 시 GTID 기반으로 누락 구간을 자동 감지합니다.

```bash
bintrail status
# stream: 2026-07-06 17:30:00 (lag: 2s, gaps: 0)
#                                         ^^^^
#                                         0이어야 복구 가능
```

갭이 발생하면 `bintrail status`에 경고가 표시되며, 해당 구간의 행 복구는 불가합니다.

### 관리형 DB (RDS, Cloud SQL)

| 플랫폼           | 추가 설정                                                      |
|------------------|----------------------------------------------------------------|
| Amazon RDS       | 파라미터 그룹에서 `binlog_format=ROW`, `binlog_row_image=FULL` |
| Amazon Aurora    | 클러스터 파라미터 그룹 동일                                    |
| Google Cloud SQL | `cloudsql.enable_bin_log=ON`, 플래그 설정                      |

복제 프로토콜로 접속하므로 binlog 파일 직접 접근이 불필요합니다. 관리형 DB에서도 동작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 저장 구조

### Parquet 파일 구조

```
s3://bucket/dbtrail/
├── server-id/
│   ├── 2026/07/06/
│   │   ├── 14/
│   │   │   ├── events_1720270800_000.parquet
│   │   │   ├── events_1720270800_001.parquet
│   │   │   └── ...
│   │   └── 15/
│   │       └── events_1720274400_000.parquet
│   └── ...
└── baselines/
    └── shop.orders_20260706_140000.parquet
```

### 이벤트당 저장 데이터

| 필드            | 설명                                                  |
|-----------------|-------------------------------------------------------|
| event_id        | 고유 ID                                               |
| event_timestamp | 변경 시각                                             |
| event_type      | INSERT / UPDATE / DELETE                              |
| schema          | 데이터베이스 이름                                     |
| table           | 테이블 이름                                           |
| pk_values       | 기본키 값 (JSON)                                      |
| pk_hash         | PK의 SHA-256 해시 (빠른 조회용)                       |
| row_before      | 변경 전 행 전체 (JSON)                                |
| row_after       | 변경 후 행 전체 (JSON)                                |
| changed_columns | 변경된 컬럼 목록 (UPDATE 시)                          |
| gtid            | 트랜잭션 GTID                                         |
| connection_id   | MySQL 연결 ID (Forensics용)                           |
| query_text      | 원본 SQL (선택, `binlog_rows_query_log_events=ON` 시) |

### 이벤트 타입별 저장

| 타입   | row_before  | row_after   | 비용                         |
|--------|-------------|-------------|------------------------------|
| INSERT | —           | 전체 이미지 | floor + 1 이미지             |
| DELETE | 전체 이미지 | —           | floor + 1 이미지             |
| UPDATE | 전체 이미지 | 전체 이미지 | floor + 2 이미지 (가장 비쌈) |

### Parquet vs 다른 포맷

| 포맷    | 압축률 | 컬럼 선택 읽기 | 스키마 내장 | 분석 도구 호환             |
|---------|--------|----------------|-------------|----------------------------|
| CSV     | 낮음   | ❌             | ❌          | 제한적                     |
| JSON    | 낮음   | ❌             | ❌          | 제한적                     |
| Avro    | 중간   | ❌ (행 기반)   | ✅          | 중간                       |
| Parquet | 높음   | ✅             | ✅          | ✅ (DuckDB, Athena, Spark) |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 인덱싱

### DuckDB 역할

S3에 저장된 Parquet 파일을 DuckDB가 인덱싱하여 빠른 조회를 제공합니다.

```bash
# Parquet → DuckDB 인덱싱
bintrail index

# 인덱스 위치
/var/lib/bintrail/index/
```

### 쿼리 경로

```
bintrail query --table orders --pk 123
    │
    v
DuckDB: pk_hash 기반 검색 → 해당 Parquet 파일만 스캔
    │
    v
결과: [{event_type: DELETE, timestamp: ..., row_before: {...}}]
```

### Live + Archive 병합

최근 데이터는 Index MySQL(또는 DuckDB)에서, 오래된 데이터는 S3 Parquet에서 읽어 자동 병합합니다.

```
query --since '30 days ago'
    │
    ├── 최근 7일 → Index (빠름)
    └── 7~30일 → S3 Parquet 직접 쿼리 (약간 느림)
    │
    v
    결과 병합 (시간순 정렬)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 스키마 스냅샷

### 왜 필요한가

MySQL binlog는 행을 **위치 배열**(`[1, "Alice", 42]`)로 기록합니다. 컬럼 이름이 없습니다. 스키마 스냅샷이 있어야 "첫 번째 값은 id, 두 번째는 name"을 알 수 있습니다.

### 생성

```bash
bintrail snapshot --schema shop
# → information_schema.COLUMNS + KEY_COLUMN_USAGE + REFERENTIAL_CONSTRAINTS 캡처
```

### DDL 변경 시 주의

| 상황                               | 동작                                          |
|------------------------------------|-----------------------------------------------|
| ALTER TABLE 후 컬럼 수 변경        | 해당 테이블 이벤트 skip + 경고                |
| 컬럼 이름 변경 (수 동일)           | 잘못된 이름으로 인덱싱 가능 (위험)            |
| `binlog_row_metadata=FULL` 설정 시 | TABLE_MAP에 컬럼 이름 포함 → 불일치 즉시 에러 |

🟡 `binlog_row_metadata=FULL` 설정을 권장합니다 (MySQL 8.0+):

```sql
SET PERSIST binlog_row_metadata = 'FULL';
```

이렇게 하면 스키마 변경을 자동 감지하여 corrupt 데이터 인덱싱을 방지합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 용량 계획

### 이벤트당 크기 (측정값, InnoDB)

| 소스 행 형태                       | INSERT/DELETE | UPDATE  |
|------------------------------------|---------------|---------|
| Narrow (4컬럼, 60B 이미지)         | ~0.85 KB      | ~1.0 KB |
| Typical OLTP (15컬럼, 380B 이미지) | ~1.2 KB       | ~1.6 KB |
| Wide (40컬럼, 1.5KB 텍스트 포함)   | ~3.8 KB       | ~8.7 KB |

### 용량 추정 공식

```
일일 저장량 = 일일 변경 이벤트 수 × 이벤트당 크기

예시: OLTP 서버, 일 500만 이벤트 (70% UPDATE, 20% INSERT, 10% DELETE)
  UPDATE: 3,500,000 × 1.6 KB = 5.6 GB
  INSERT: 1,000,000 × 1.2 KB = 1.2 GB
  DELETE:   500,000 × 1.2 KB = 0.6 GB
  합계: ~7.4 GB/일 → ~222 GB/월

Parquet 압축 후 (S3): ~50~70% 절감 → ~66~111 GB/월
```

### 비용 요소

| 항목                  | 내용                                              |
|-----------------------|---------------------------------------------------|
| `query_text` 저장     | 모든 행 이벤트에 SQL 복사 → 대량 DML 시 비용 증가 |
| Wide 테이블           | 컬럼 40개 + 긴 TEXT → UPDATE당 8.7KB              |
| binlog_row_image=FULL | 모든 컬럼 포함 (MINIMAL 대비 크지만 필수)         |

### 용량 모니터링

```bash
bintrail doctor --capacity
# index disk: 45.2 GB used / 100 GB total (45%)
# estimated growth: 7.4 GB/day
# days until full: 7.4 days ← 디스크 증설 필요
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [README.md](./README.md)
- [recovery_guide.md](./recovery_guide.md)
- dbtrail Streaming docs: [github.com/dbtrail/dbtrail/blob/main/docs/streaming.md](https://github.com/dbtrail/dbtrail/blob/main/docs/streaming.md) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-06

**마지막 업데이트**: 2026-07-06

© 2026 siasia86. Licensed under CC BY 4.0.
