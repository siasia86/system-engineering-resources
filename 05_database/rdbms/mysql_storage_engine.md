# MySQL Storage Engine

MySQL의 Pluggable Storage Engine 아키텍처와 각 엔진의 상세 특성을 정리합니다.

## 목차

| 섹션                                                                                                                       |
|----------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. InnoDB](#3-innodb)                                                   |
| [4. MyISAM](#4-myisam) / [5. MEMORY (HEAP)](#5-memory-heap) / [6. ARCHIVE](#6-archive)                                     |
| [7. CSV](#7-csv) / [8. BLACKHOLE](#8-blackhole) / [9. MERGE (MRG_MyISAM)](#9-merge-mrg_myisam)                             |
| [10. FEDERATED](#10-federated) / [11. NDB (NDBCLUSTER)](#11-ndb-ndbcluster) / [12. 엔진 비교 종합표](#12-엔진-비교-종합표) |
| [13. 엔진 선택 가이드](#13-엔진-선택-가이드) / [14. 엔진 변환 실무](#14-엔진-변환-실무) / [15. 실무 Tip](#15-실무-tip)     |

---

## 1. 개요

MySQL은 Pluggable Storage Engine 아키텍처를 사용합니다. SQL 파서, 옵티마이저, 캐시는 공통 서버 레이어에서 처리하고, 실제 데이터 저장/조회는 각 Storage Engine이 담당합니다.

하나의 데이터베이스 내에서 테이블별로 다른 엔진을 사용할 수 있습니다.

```sql
-- 서버에서 지원하는 엔진 목록 확인
SHOW ENGINES;
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

### Pluggable Storage Engine 구조

```
┌───────────────────────────────────────────────────────┐
│         MySQL Server (Common Layer)                   │
│  SQL Parser / Optimizer / Query Cache (removed 8.0)   │
├───────────────────────────────────────────────────────┤
│         Storage Engine API                            │
├──────────┬──────────┬─────────┬─────────┬─────────────┤
│  InnoDB  │  MyISAM  │ Memory  │ Archive │  NDB / ...  │
└──────────┴──────────┴─────────┴─────────┴─────────────┘
```

### 서버 레이어 vs 엔진 레이어

| 처리 레이어        | 담당 기능                                                |
|--------------------|----------------------------------------------------------|
| 서버 레이어 (공통) | 연결 관리, SQL 파싱, 옵티마이저, 권한 검사, 로깅         |
| 엔진 레이어        | 데이터 저장, 인덱스 관리, 트랜잭션, 잠금, crash recovery |

[⬆ 목차로 돌아가기](#목차)

---

## 3. InnoDB

### 개요

MySQL 8.4 기본 Storage Engine. ACID 트랜잭션을 완벽히 지원하며, 범용 OLTP 워크로드에 최적화되어 있습니다.

### 핵심 특성

| 항목             | 내용                                              |
|------------------|---------------------------------------------------|
| 트랜잭션         | ACID 완전 지원 (commit, rollback, crash-recovery) |
| 잠금 수준        | Row-level locking (escalation 없음)               |
| 동시성 제어      | MVCC (Multi-Version Concurrency Control)          |
| 인덱스 구조      | Clustered Index (PK 기준 B+Tree)                  |
| FK 제약          | 지원                                              |
| Fulltext         | 지원 (MySQL 5.6+)                                 |
| 최대 테이블 크기 | 64 TB                                             |
| Online DDL       | 지원                                              |
| 데이터 암호화    | Data-at-rest encryption 지원                      |

### 내부 구조

```
┌──────────────────────────────────────────────────┐ 
│                 InnoDB Architecture              │ 
│                                                  │ 
│  ┌──────────────────────────────────────┐        │ 
│  │         Buffer Pool (Memory)         │        │ 
│  │  ┌──────────┐  ┌──────────────────┐  │        │ 
│  │  │Data Pages│  │ Change Buffer    │  │        │ 
│  │  └──────────┘  └──────────────────┘  │        │ 
│  │  ┌──────────┐  ┌──────────────────┐  │        │ 
│  │  │Adaptive  │  │ Log Buffer       │  │        │ 
│  │  │Hash Index│  │                  │  │        │ 
│  │  └──────────┘  └──────────────────┘  │        │ 
│  └──────────────────────────────────────┘        │ 
│                                                  │ 
│  ┌──────────────────────────────────────┐        │ 
│  │            Disk (Storage)            │        │ 
│  │  ┌────────────┐  ┌────────────────┐  │        │ 
│  │  │ Tablespace │  │ Redo Log       │  │        │ 
│  │  │(.ibd files)│  │(ib_logfile0/1) │  │        │ 
│  │  └────────────┘  └────────────────┘  │        │ 
│  │  ┌────────────┐  ┌────────────────┐  │        │ 
│  │  │ Undo Log   │  │ Doublewrite    │  │        │ 
│  │  │            │  │ Buffer         │  │        │ 
│  │  └────────────┘  └────────────────┘  │        │ 
│  └──────────────────────────────────────┘        │ 
└──────────────────────────────────────────────────┘ 
```

### Clustered Index

InnoDB는 Primary Key를 기준으로 데이터를 물리적으로 정렬 저장합니다.

```
Clustered Index (Primary Key):                 
┌─────────────────────────────────────────┐    
│             B+Tree Root                 │    
│          ┌────┬────┬────┐               │    
│          │ 10 │ 50 │100 │               │    
│          └─┬──┴─┬──┴─┬──┘               │    
│            v    v    v                  │    
│  ┌──────┐ ┌──────┐ ┌──────┐             │    
│  │Leaf: │ │Leaf: │ │Leaf: │             │    
│  │PK+Row│ │PK+Row│ │PK+Row│  ← data     │    
│  │ Data │ │ Data │ │ Data │    stored   │    
│  └──────┘ └──────┘ └──────┘    in leaf  │    
└─────────────────────────────────────────┘    
                                               
Secondary Index:                               
  Leaf Node → stores PK value (not row pointer)
  → requires PK lookup to get actual data      
```

- PK가 없으면 UNIQUE NOT NULL 컬럼 사용
- 그것도 없으면 내부 6바이트 row ID 자동 생성

### MVCC 동작 원리

```
Transaction A (READ):          Transaction B (WRITE):
  BEGIN;                         BEGIN;
  SELECT * FROM t               UPDATE t SET val=200
    WHERE id=1;                   WHERE id=1;
       |                              |
       v                              v
  Undo Log에서                   현재 행을 수정
  이전 버전 읽기                 이전 버전 → Undo Log
  (consistent read)              COMMIT;
       |
       v
  val=100 (old version)          val=200 (new version)
```

- 각 행에 트랜잭션 ID (DB_TRX_ID) + roll pointer 저장
- READ COMMITTED: 매 쿼리마다 최신 스냅샷
- REPEATABLE READ: 트랜잭션 시작 시점 스냅샷 유지 (기본)

### Redo Log와 Crash Recovery

```
1. Transaction COMMIT
       |
       v
2. Redo Log (WAL) flush to disk  ← durability 보장
       |
       v
3. Buffer Pool의 dirty page는 비동기로 flush
       |
       v
4. Crash 발생 시 → Redo Log replay로 복구
```

### 주요 설정 파라미터

| 파라미터                         | 기본값   | 설명                                  |
|----------------------------------|----------|---------------------------------------|
| `innodb_buffer_pool_size`        | 128MB    | 버퍼 풀 크기 (총 RAM의 70~80% 권장)   |
| `innodb_log_file_size`           | 48MB     | Redo Log 파일 크기                    |
| `innodb_flush_log_at_trx_commit` | 1        | 1=ACID 보장, 2=1초 지연, 0=OS 의존    |
| `innodb_file_per_table`          | ON       | 테이블별 .ibd 파일 분리               |
| `innodb_io_capacity`             | 10000    | 백그라운드 I/O 처리량 (IOPS 기준)     |
| `innodb_flush_method`            | O_DIRECT | Linux 기본값 (8.4+), 이중 버퍼링 방지 |

### 적합한 워크로드

- OLTP (온라인 트랜잭션 처리)
- 높은 동시성 read/write
- 데이터 무결성이 중요한 시스템
- 범용 웹 애플리케이션

[⬆ 목차로 돌아가기](#목차)

---

## 4. MyISAM

### 개요

MySQL의 과거 기본 엔진 (5.5 이전). 현재는 레거시로 분류되며, read-only 또는 read-mostly 워크로드에서만 권장됩니다.

### 핵심 특성

| 항목             | 내용                     |
|------------------|--------------------------|
| 트랜잭션         | 미지원                   |
| 잠금 수준        | Table-level locking      |
| FK 제약          | 미지원                   |
| Fulltext         | 지원                     |
| 압축             | myisampack (read-only)   |
| 최대 테이블 크기 | 256 TB                   |
| 최대 인덱스 수   | 64개/테이블              |
| 최대 키 길이     | 1000 bytes               |
| 최대 행 수       | (2^32)^2 ≈ 1.844 × 10^19 |
| 파티셔닝         | MySQL 8.4에서 미지원     |

### 파일 구조

```
테이블 "orders":
  orders.MYD   ← 데이터 파일 (MYData)
  orders.MYI   ← 인덱스 파일 (MYIndex)
  (테이블 정의는 Data Dictionary에 저장)
```

### 저장 형식

| 형식       | 특징                                    | 용도              |
|------------|-----------------------------------------|-------------------|
| Static     | 고정 길이 행, 빠른 접근, 공간 낭비 가능 | CHAR 컬럼 위주    |
| Dynamic    | 가변 길이 행, 공간 절약, 단편화 발생    | VARCHAR/TEXT 포함 |
| Compressed | myisampack으로 압축, read-only          | 아카이브/배포용   |

### Concurrent Inserts

MyISAM은 Table Lock이지만, 제한된 조건에서 concurrent insert를 지원합니다.

```
조건: 데이터 파일 중간에 빈 블록(hole)이 없을 때
  → 다른 스레드가 SELECT하는 동안 테이블 끝에 INSERT 가능

concurrent_insert 설정:
  0 = 비활성
  1 = hole 없을 때만 허용 (기본)
  2 = hole 있어도 테이블 끝에 항상 허용
```

### 유지보수 도구

| 도구         | 용도                           |
|--------------|--------------------------------|
| `myisamchk`  | 테이블 검사/복구 (오프라인)    |
| `mysqlcheck` | 테이블 검사/복구 (온라인)      |
| `myisampack` | 테이블 압축 (read-only로 전환) |
| `myisamlog`  | MyISAM 로그 분석               |

### 적합한 워크로드

- Read-only / Read-mostly 환경
- 데이터 웨어하우스 (조회 위주)
- 트랜잭션 불필요한 로그 테이블 (ARCHIVE 대안 검토)

### 비권장 사유

- Table Lock으로 인한 동시성 병목
- crash-safe 미보장 (crash 시 데이터 손실 가능)
- MySQL 8.4에서 시스템 테이블 MyISAM 제거

[⬆ 목차로 돌아가기](#목차)

---

## 5. MEMORY (HEAP)

### 개요

모든 데이터를 메모리에 저장하는 엔진. 서버 재시작/crash 시 데이터가 소멸됩니다. 임시 작업이나 read-only 캐시 용도로 사용합니다.

### 핵심 특성

| 항목      | 내용                                     |
|-----------|------------------------------------------|
| 저장 위치 | RAM (휘발성)                             |
| 트랜잭션  | 미지원                                   |
| 잠금 수준 | Table-level locking                      |
| 인덱스    | Hash (기본), B-tree (선택)               |
| BLOB/TEXT | 미지원                                   |
| 최대 크기 | `max_heap_table_size` 시스템 변수로 제한 |
| FK 제약   | 미지원                                   |
| 파티셔닝  | 미지원                                   |

### Hash vs B-tree Index

```sql
-- Hash index (기본) - 등호 검색에 최적
CREATE TABLE lookup (
    id INT NOT NULL,
    val VARCHAR(50),
    INDEX USING HASH (id)
) ENGINE = MEMORY;

-- B-tree index - 범위 검색에 필요
CREATE TABLE range_lookup (
    id INT NOT NULL,
    val VARCHAR(50),
    INDEX USING BTREE (id)
) ENGINE = MEMORY;
```

| 인덱스 | 등호 검색 | 범위 검색 | ORDER BY | 기본값 |
|--------|-----------|-----------|----------|--------|
| Hash   | O(1)      | 불가      | 불가     | ✅     |
| B-tree | O(log n)  | 가능      | 가능     | ❌     |

### 제한사항

- 서버 재시작 시 테이블 구조는 유지, 데이터는 소멸
- Table Lock으로 write 동시성 제한
- VARCHAR도 CHAR처럼 고정 길이로 저장 (메모리 낭비)
- BLOB, TEXT, GEOMETRY 타입 미지원
- AUTO_INCREMENT 지원하나 행 삭제 시 값 재사용하지 않음

### InnoDB Buffer Pool과 비교

| 항목          | MEMORY 엔진      | InnoDB Buffer Pool |
|---------------|------------------|--------------------|
| 영속성        | 없음 (휘발성)    | 있음 (디스크 백업) |
| 동시성        | Table Lock       | Row Lock + MVCC    |
| 자동 관리     | 수동 크기 설정   | 자동 LRU 관리      |
| 적합 워크로드 | 임시 조회 테이블 | 범용               |

🟡 Oracle은 대부분의 MEMORY 엔진 사용 사례에서 InnoDB를 권장합니다.

### 적합한 워크로드

- 임시 조회 테이블/세션 데이터
- 빈번하게 참조하는 코드 테이블 캐시
- 비영속 데이터가 허용되는 환경

[⬆ 목차로 돌아가기](#목차)

---

## 6. ARCHIVE

### 개요

대용량 데이터를 최소 디스크 공간으로 저장하는 엔진. zlib 압축을 사용하며, INSERT와 SELECT만 지원합니다.

### 핵심 특성

| 항목       | 내용                       |
|------------|----------------------------|
| 압축       | zlib 자동 압축 (insert 시) |
| 지원 DML   | INSERT, SELECT, REPLACE    |
| 미지원 DML | DELETE, UPDATE             |
| 잠금 수준  | Row-level locking          |
| 인덱스     | AUTO_INCREMENT 열에만 가능 |
| 최대 크기  | 제한 없음                  |
| 트랜잭션   | 미지원                     |
| 파티셔닝   | 미지원                     |

### 파일 구조

```
테이블 "audit_log":
  audit_log.ARZ   ← 압축 데이터 파일
  audit_log.ARN   ← OPTIMIZE TABLE 중 임시 파일
```

### 동작 방식

```
INSERT → compression buffer에 추가
           → buffer가 차면 flush (zlib 압축 후 .ARZ에 기록)

SELECT → flush 강제 실행 후 읽기 (최신 데이터 보장)

OPTIMIZE TABLE → 전체 재압축 (최적 압축률 달성)
```

### 적합한 워크로드

- 감사 로그 (audit log)
- 보안 이벤트 저장
- 히스토리 / 아카이브 데이터
- 거의 참조하지 않는 대용량 데이터

[⬆ 목차로 돌아가기](#목차)

---

## 7. CSV

### 개요

데이터를 쉼표 구분 텍스트 파일(CSV) 형식으로 저장합니다. 인덱스를 지원하지 않으며, 외부 도구와 데이터 교환 시 사용합니다.

### 핵심 특성

| 항목      | 내용                          |
|-----------|-------------------------------|
| 저장 형식 | 텍스트 CSV 파일 (.CSV 확장자) |
| 인덱스    | 미지원                        |
| 컬럼 제약 | 모든 컬럼 NOT NULL 필수       |
| 트랜잭션  | 미지원                        |
| 잠금 수준 | Table-level locking           |

### 파일 구조

```
테이블 "export_data":
  export_data.CSV   ← 데이터 (쉼표 구분 텍스트)
  export_data.CSM   ← 메타데이터 (테이블 상태, 행 수)
```

### 사용 예시

```sql
CREATE TABLE export_data (
    id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    value DECIMAL(10,2) NOT NULL
) ENGINE = CSV;

INSERT INTO export_data VALUES (1, 'item_a', 100.50);
```

파일 내용:
```
"1","item_a","100.50"
```

### 적합한 워크로드

- 외부 시스템과 CSV 형식 데이터 교환
- 스프레드시트 import/export
- 일반 운영 중에는 InnoDB 사용, import/export 단계에서만 CSV 사용

[⬆ 목차로 돌아가기](#목차)

---

## 8. BLACKHOLE

### 개요

데이터를 수신하지만 저장하지 않는 엔진 (`/dev/null`과 유사). Binary Log에는 기록되므로 replication 필터/리피터 용도로 사용합니다.

### 핵심 특성

| 항목         | 내용                             |
|--------------|----------------------------------|
| 데이터 저장  | 하지 않음                        |
| SELECT 결과  | 항상 빈 결과 (empty set)         |
| Binary Log   | 기록됨 (statement-based logging) |
| 인덱스 선언  | 가능 (저장은 안 됨)              |
| 최대 키 길이 | 3072 bytes                       |
| 잠금 수준    | Row-level                        |
| 파티셔닝     | 미지원                           |

### Replication 필터 구성

```
Source Server                 Blackhole "Dummy"     Replica
┌──────────┐  binlog   ┌──────────────┐ filtered  ┌──────────┐   
│  mysqld  │ ────────> │mysqld        │ ────────> │  mysqld  │   
│ (source) │           │(BLACKHOLE    │           │(replica) │   
│          │           │ default eng) │           │          │   
└──────────┘           └──────────────┘           └──────────┘   
                       replicate-do-table=db.t1                  
                       (filtered forwarding)                     
```

- 전체 binlog를 replica에 전송하면 트래픽 과다
- BLACKHOLE 중간 서버에서 필터링 후 필요한 것만 전달

### 적합한 워크로드

- Replication 토폴로지에서 필터/리피터
- DML 문 로깅 (binlog) 용도
- 벤치마크 시 스토리지 오버헤드 제거

[⬆ 목차로 돌아가기](#목차)

---

## 9. MERGE (MRG_MyISAM)

### 개요

동일한 구조의 여러 MyISAM 테이블을 하나의 논리적 테이블로 결합합니다. VLDB 환경에서 데이터를 시간/범위별로 분리 관리할 때 사용합니다.

### 핵심 특성

| 항목        | 내용                                |
|-------------|-------------------------------------|
| 하위 테이블 | MyISAM만 가능 (동일 구조 필수)      |
| 지원 DML    | SELECT, DELETE, UPDATE, INSERT      |
| INSERT 정책 | INSERT_METHOD: FIRST / LAST / NO    |
| DROP 동작   | MERGE 정의만 삭제, 하위 테이블 유지 |
| 잠금 수준   | Table-level (MyISAM 동일)           |
| 파일        | .MRG (하위 테이블 목록)             |

### 사용 예시

```sql
-- 하위 MyISAM 테이블 생성
CREATE TABLE log_2024 (ts DATETIME, msg TEXT) ENGINE=MyISAM;
CREATE TABLE log_2025 (ts DATETIME, msg TEXT) ENGINE=MyISAM;

-- MERGE 테이블로 결합
CREATE TABLE log_all (ts DATETIME, msg TEXT)
    ENGINE=MERGE UNION=(log_2024, log_2025) INSERT_METHOD=LAST;

-- 하나의 테이블처럼 조회
SELECT * FROM log_all WHERE ts >= '2025-01-01';
```

### 대안: 파티셔닝

MySQL 공식 문서는 MERGE 대신 파티셔닝 사용을 권장합니다.

| 비교 항목   | MERGE                 | 파티셔닝 (InnoDB)        |
|-------------|-----------------------|--------------------------|
| 하위 엔진   | MyISAM만              | InnoDB 등 다양           |
| 트랜잭션    | 미지원                | 지원                     |
| 파티션 제거 | 불가                  | 가능 (partition pruning) |
| 관리        | 수동 테이블 추가/제거 | 자동                     |

[⬆ 목차로 돌아가기](#목차)

---

## 10. FEDERATED

### 개요

원격 MySQL 서버의 테이블에 접근합니다. 로컬에는 데이터를 저장하지 않으며, 모든 쿼리가 원격 서버로 전달됩니다.

### 핵심 특성

| 항목        | 내용                                  |
|-------------|---------------------------------------|
| 데이터 저장 | 로컬에 없음 (원격 서버에만 존재)      |
| 활성화      | `--federated` 옵션 필요 (기본 비활성) |
| 연결 방식   | CONNECTION 문자열 또는 CREATE SERVER  |
| 트랜잭션    | 미지원                                |
| 잠금        | Row-level (원격 서버 의존)            |

### 사용 예시

```sql
-- 원격 서버 정의
CREATE SERVER remote_db
    FOREIGN DATA WRAPPER mysql
    OPTIONS (
        HOST '192.0.2.1',
        DATABASE 'production',
        USER 'Secureuser123',
        PASSWORD 'SecurePassword123',
        PORT 3306
    );

-- FEDERATED 테이블 생성
CREATE TABLE remote_orders (
    id INT PRIMARY KEY,
    customer VARCHAR(100),
    total DECIMAL(10,2)
) ENGINE=FEDERATED
  CONNECTION='remote_db/orders';
```

### 제한사항

- 네트워크 지연이 쿼리 성능에 직접 영향
- JOIN 시 전체 데이터를 로컬로 가져온 후 처리 (비효율)
- 원격 서버 장애 시 로컬 쿼리도 실패
- DDL 제한 (ALTER TABLE 등 일부 미지원)

### 적합한 워크로드

- 분산 데이터 마트 조회
- 원격 참조 테이블 읽기
- Replication 없이 간단한 분산 접근

[⬆ 목차로 돌아가기](#목차)

---

## 11. NDB (NDBCLUSTER)

### 개요

MySQL NDB Cluster의 Storage Engine. 99.999% 가용성을 목표로 하며, shared-nothing 아키텍처로 자동 데이터 분산을 제공합니다.

### 핵심 특성

| 항목        | 내용                                     |
|-------------|------------------------------------------|
| 트랜잭션    | 지원 (ACID)                              |
| 잠금 수준   | Row-level locking                        |
| 아키텍처    | Shared-nothing (각 노드 독립 저장)       |
| 데이터 분산 | 자동 (해시 파티셔닝)                     |
| 최대 크기   | 384 EB                                   |
| 가용성 목표 | 99.999%                                  |
| FK 제약     | 지원                                     |
| 디스크 백업 | 선택 (인메모리 + 디스크 하이브리드 가능) |

### 클러스터 구성

```
┌─────────────┐  ┌─────────────┐                
│ SQL Node    │  │ SQL Node    │  ← mysqld (API)
│ (mysqld)    │  │ (mysqld)    │                
└──────┬──────┘  └──────┬──────┘                
       │                │                      
       v                v                      
┌─────────────┐  ┌─────────────┐                
│ Data Node 1 │  │ Data Node 2 │  ← ndbd/ndbmtd 
│ (Partition) │  │ (Replica)   │                
└──────┬──────┘  └──────┬──────┘                
       │                │                      
       v                v                      
┌─────────────────────────────────┐             
│       Management Node           │  ← ndb_mgmd 
│       (ndb_mgmd)                │             
└─────────────────────────────────┘             
```

### InnoDB와 비교

| 비교 항목   | InnoDB          | NDB Cluster               |
|-------------|-----------------|---------------------------|
| 가용성      | 단일 서버 의존  | 자동 failover (99.999%)   |
| 데이터 분산 | 수동 (sharding) | 자동 (hash partitioning)  |
| 메모리 의존 | Buffer Pool     | 전체 데이터 메모리 상주   |
| 적합 규모   | 단일~Replica    | 대규모 분산 시스템        |
| 복잡도      | 낮음            | 높음 (별도 클러스터 관리) |

### 적합한 워크로드

- 통신사/금융 등 극도의 가용성 요구
- 실시간 Key-Value 조회 (대규모)
- 자동 failover가 필수인 환경

[⬆ 목차로 돌아가기](#목차)

---

## 12. 엔진 비교 종합표

| 엔진      | 트랜잭션 | 잠금  | FK | Fulltext | 압축 | 최대 크기 | 주요 용도        |
|-----------|----------|-------|----|----------|------|-----------|------------------|
| InnoDB    | ✅       | Row   | ✅ | ✅       | ✅   | 64 TB     | 범용 OLTP        |
| MyISAM    | ❌       | Table | ❌ | ✅       | ✅ † | 256 TB    | Read-only 조회   |
| MEMORY    | ❌       | Table | ❌ | ❌       | ❌   | RAM       | 임시 캐시        |
| ARCHIVE   | ❌       | Row   | ❌ | ❌       | ✅   | 무제한    | 로그 아카이브    |
| CSV       | ❌       | Table | ❌ | ❌       | ❌   | OS        | 데이터 교환      |
| BLACKHOLE | ❌       | Row   | ❌ | ❌       | ❌   | 무제한    | Replication 필터 |
| MERGE     | ❌       | Table | ❌ | ✅       | ✅ † | 256 TB    | MyISAM 논리 결합 |
| FEDERATED | ❌       | Row   | ❌ | ❌       | ❌   | OS        | 원격 접근        |
| NDB       | ✅       | Row   | ✅ | ❌       | ❌   | 384 EB    | 고가용 클러스터  |

- `†` myisampack 압축 (read-only)

[⬆ 목차로 돌아가기](#목차)

---

## 13. 엔진 선택 가이드

### 의사결정 흐름

```
트랜잭션 필요?                                                         
├── Yes → 고가용 클러스터 필요?                                        
│         ├── Yes → NDB                                                
│         └── No  → InnoDB (기본)                                      
└── No  → 데이터 영속성 필요?                                          
          ├── No  → MEMORY                                             
          └── Yes → 용도별 분기                                        
                    ├── 조회 위주       → MyISAM (레거시) / InnoDB 권장
                    ├── 로그 아카이브   → ARCHIVE                      
                    ├── CSV 교환        → CSV                          
                    ├── Replication 필터 → BLACKHOLE                   
                    ├── 원격 테이블     → FEDERATED                    
                    └── MyISAM 결합     → MERGE (파티셔닝 권장)        
```

### 실무 권장

| 상황                            | 권장                       |
|---------------------------------|----------------------------|
| 신규 프로젝트                   | InnoDB (무조건)            |
| 레거시 MyISAM 테이블 존재       | InnoDB로 전환 계획 수립    |
| 감사 로그 (INSERT only, 대용량) | ARCHIVE                    |
| 외부 시스템 데이터 교환         | CSV (임시) → InnoDB (운영) |
| 복제 토폴로지 최적화            | BLACKHOLE (중간 필터)      |

[⬆ 목차로 돌아가기](#목차)

---

## 14. 엔진 변환 실무

### MyISAM → InnoDB 전환

```sql
-- 단일 테이블 변환
ALTER TABLE old_table ENGINE = InnoDB;

-- 대용량 테이블 변환 시 주의사항:
-- 1. 변환 중 테이블 잠금 발생 (Online DDL로 최소화)
-- 2. 디스크 공간 2배 필요 (원본 + 새 테이블)
-- 3. FK 관계 테이블은 순서 주의

-- 전체 MyISAM 테이블 목록 확인
SELECT table_schema, table_name, engine
FROM information_schema.tables
WHERE engine = 'MyISAM'
  AND table_schema NOT IN ('mysql', 'information_schema', 'performance_schema');
```

### 변환 시 체크리스트

| 항목                | 확인 내용                              |
|---------------------|----------------------------------------|
| Fulltext Index      | InnoDB도 지원 (5.6+), 구문 동일        |
| 공간 인덱스         | InnoDB도 지원 (5.7+)                   |
| COUNT(*) 성능       | MyISAM: O(1), InnoDB: full scan 필요   |
| AUTO_INCREMENT 동작 | InnoDB는 서버 재시작 시 MAX+1로 재계산 |
| 디스크 공간         | InnoDB는 일반적으로 더 많은 공간 사용  |
| key_buffer_size     | MyISAM 전용, 전환 후 축소 가능         |

[⬆ 목차로 돌아가기](#목차)

---

## 15. 실무 Tip

### Tip 1 — 엔진 확인 쿼리

```sql
-- 특정 DB의 모든 테이블 엔진 확인
SELECT table_name, engine, table_rows, data_length, index_length
FROM information_schema.tables
WHERE table_schema = 'my_database'
ORDER BY data_length DESC;
```

### Tip 2 — InnoDB Buffer Pool 모니터링

```sql
-- Buffer Pool 적중률 확인
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_%';

-- 적중률 계산
SELECT
    (1 - (reads / read_requests)) * 100 AS hit_ratio_pct
FROM (
    SELECT
        VARIABLE_VALUE AS reads
    FROM performance_schema.global_status
    WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads'
) r,
(
    SELECT
        VARIABLE_VALUE AS read_requests
    FROM performance_schema.global_status
    WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests'
) rr;
```

### Tip 3 — ARCHIVE 테이블 생성 패턴

```sql
-- 감사 로그 테이블
CREATE TABLE audit_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    detail TEXT,
    PRIMARY KEY (id)
) ENGINE = ARCHIVE;
```

### Tip 4 — 혼합 엔진 사용 시 주의

```sql
-- InnoDB 테이블에서 MyISAM 테이블을 JOIN하면:
-- - MyISAM 테이블에 Table Lock 발생
-- - InnoDB 트랜잭션이 MyISAM에는 적용 안 됨
-- - ROLLBACK 시 MyISAM 변경은 취소 불가

-- 권장: 트랜잭션 내에서 동일 엔진 사용
```

### Tip 5 — 엔진 변환 속도 향상

```sql
-- 대용량 테이블 변환 시 (InnoDB → InnoDB 재구성도 동일)
SET GLOBAL innodb_io_capacity = 20000;       -- SSD 기준 (기본 10000)
SET GLOBAL innodb_io_capacity_max = 40000;
SET SESSION sort_buffer_size = 64 * 1024 * 1024;

ALTER TABLE large_table ENGINE = InnoDB;

-- 완료 후 원복
SET GLOBAL innodb_io_capacity = 10000;
SET GLOBAL innodb_io_capacity_max = 20000;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL 8.4 Reference Manual — Storage Engines: [dev.mysql.com/doc/refman/8.4/en/storage-engines.html](https://dev.mysql.com/doc/refman/8.4/en/storage-engines.html) — ★★★☆☆
- MySQL 8.4 Reference Manual — InnoDB: [dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html](https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html) — ★★★☆☆
- Schwartz, Baron et al. "High Performance MySQL, 4th Edition"

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-10

**마지막 업데이트**: 2026-07-10

© 2026 siasia86. Licensed under CC BY 4.0.
