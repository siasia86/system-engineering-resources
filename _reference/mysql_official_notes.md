---
name: mysql-official-notes
description: MySQL Storage Engine 공식 문서 요약. 엔진별 특성, 제한사항, 선택 기준.
tags:
  - mysql
  - storage-engine
  - database
last_checked: 2026-07-10
sources:
  - https://dev.mysql.com/doc/refman/8.4/en/storage-engines.html
  - https://dev.mysql.com/doc/refman/8.4/en/innodb-introduction.html
  - https://dev.mysql.com/doc/refman/8.4/en/myisam-storage-engine.html
  - https://dev.mysql.com/doc/refman/8.4/en/memory-storage-engine.html
  - https://dev.mysql.com/doc/refman/8.4/en/archive-storage-engine.html
  - https://dev.mysql.com/doc/refman/8.4/en/blackhole-storage-engine.html
  - https://dev.mysql.com/doc/refman/8.4/en/merge-storage-engine.html
  - https://dev.mysql.com/doc/refman/8.4/en/federated-storage-engine.html
  - https://dev.mysql.com/doc/refman/8.4/en/csv-storage-engine.html
---

# MySQL Storage Engine 공식 문서 참조 노트

MySQL 8.4 LTS (현재 8.4.10) / MySQL 9.7 LTS 기준.

## 버전 정보

| 항목        | 값                                            |
|-------------|-----------------------------------------------|
| LTS 버전    | 8.4.10 (2026-07 기준)                         |
| LTS (9.x)   | 9.7.1 (2026-07 기준)                          |
| 기본 엔진   | InnoDB                                        |
| 아키텍처    | Pluggable Storage Engine                      |
| 참조 매뉴얼 | Chapter 17 (InnoDB), Chapter 18 (Alternative) |

## Storage Engine Feature Summary (공식 비교표)

출처: Table 18.1 Storage Engines Feature Summary

| Feature             | InnoDB | MyISAM | Memory | Archive | NDB   | CSV   | Blackhole | Merge | Federated |
|---------------------|--------|--------|--------|---------|-------|-------|-----------|-------|-----------|
| B-tree indexes      | Yes    | Yes    | Yes    | No      | No    | No    | Yes*      | Yes   | Yes*      |
| Clustered indexes   | Yes    | No     | No     | No      | No    | No    | No        | No    | No        |
| Compressed data     | Yes    | Yes†   | No     | Yes     | No    | No    | No        | Yes†  | No        |
| Data caches         | Yes    | No     | N/A    | No      | Yes   | No    | No        | No    | No        |
| Foreign key support | Yes    | No     | No     | No      | Yes   | No    | No        | No    | No        |
| Full-text search    | Yes    | Yes    | No     | No      | No    | No    | No        | Yes   | No        |
| Hash indexes        | AHI‡   | No     | Yes    | No      | Yes   | No    | No        | No    | No        |
| Locking granularity | Row    | Table  | Table  | Row     | Row   | Table | Row       | Table | Row       |
| MVCC                | Yes    | No     | No     | No      | No    | No    | No        | No    | No        |
| Storage limits      | 64TB   | 256TB  | RAM    | None    | 384EB | OS    | None      | 256TB | OS        |
| Transactions        | Yes    | No     | No     | No      | Yes   | No    | No        | No    | No        |
| XA transactions     | Yes    | No     | No     | No      | No    | No    | No        | No    | No        |
| Geospatial indexing | Yes    | Yes    | No     | No      | No    | No    | No        | Yes   | No        |

- `†` MyISAM compressed: myisampack으로 압축, read-only
- `‡` InnoDB Adaptive Hash Index: 내부적으로 hash index 자동 생성
- `*` Blackhole/Federated: index 선언 가능하나 실제 데이터 저장 여부와 무관

## 엔진별 핵심 요약

### InnoDB

- MySQL 8.4 기본 엔진, Oracle 권장
- ACID 트랜잭션, commit/rollback/crash-recovery
- Row-level locking (escalation 없음)
- Clustered index (Primary Key 기준 데이터 정렬)
- FOREIGN KEY 제약조건 지원
- MVCC (consistent nonlocking reads)
- Online DDL 지원
- Data-at-rest encryption 지원
- Buffer Pool로 데이터/인덱스 캐싱
- Fulltext index 지원 (5.6+)
- 최대 테이블 크기: 64TB

### MyISAM

- ISAM 기반, 현재는 레거시
- Table-level locking → read/write 동시성 제한
- 트랜잭션/FK 미지원
- Concurrent inserts 지원 (빈 블록 없을 때)
- 파일 구조: .MYD (데이터), .MYI (인덱스)
- myisampack으로 압축 가능 (read-only)
- Fulltext index 지원
- 최대 인덱스 64개, 키 최대 1000 bytes
- 최대 행 수: (2^32)^2 = 1.844E+19
- MySQL 8.4에서 파티셔닝 미지원
- 최대 테이블 크기: 256TB

### MEMORY (HEAP)

- 모든 데이터 RAM 저장 (서버 재시작 시 소멸)
- Table-level locking
- Hash index 기본, B-tree 선택 가능
- 트랜잭션/FK 미지원
- BLOB/TEXT 미지원
- 용도: 임시 작업 영역, read-only 캐시
- InnoDB buffer pool이 대부분의 사용 사례를 대체
- 파티셔닝 미지원

### ARCHIVE

- 대량 비인덱스 데이터를 작은 풋프린트로 저장
- zlib 압축 (insert 시 자동 압축)
- Row-level locking
- INSERT/REPLACE/SELECT 지원 (DELETE/UPDATE 불가)
- AUTO_INCREMENT 열에만 인덱스 가능
- 용도: 감사 로그, 히스토리 데이터 아카이빙
- 파티셔닝 미지원
- 최대 크기 제한 없음

### BLACKHOLE

- 데이터 수신하지만 저장하지 않음 (/dev/null)
- SELECT 항상 빈 결과
- binary log에는 기록됨 → replication 필터/리피터 용도
- 모든 종류의 인덱스 선언 가능 (저장은 안 됨)
- 최대 키 길이: 3072 bytes
- 파티셔닝 미지원

### CSV

- 데이터를 CSV 텍스트 파일로 저장 (.CSV 확장자)
- 인덱스 미지원
- 모든 컬럼 NOT NULL 필수
- 외부 스크립트/스프레드시트와 데이터 교환 용도
- 서버에 항상 컴파일되어 포함
- 메타파일: .CSM (상태 + 행 수)

### MERGE (MRG_MyISAM)

- 동일한 구조의 MyISAM 테이블을 하나로 논리적 결합
- VLDB/데이터 웨어하우스 환경에 적합
- UNION=(table_list)로 구성
- INSERT_METHOD: FIRST/LAST/NO
- DROP TABLE 시 MERGE 정의만 삭제 (하위 테이블 유지)
- 대안: 파티셔닝 (동일 기능을 더 효율적으로 제공)

### FEDERATED

- 원격 MySQL 서버 데이터에 접근 (로컬에 데이터 없음)
- Replication/Cluster 없이 분산 데이터 접근
- 기본 비활성, --federated 옵션으로 활성화 필요
- CONNECTION 또는 CREATE SERVER로 원격 테이블 연결
- 용도: 분산 환경, 데이터 마트

### NDB (NDBCLUSTER)

- 클러스터 데이터베이스 엔진
- 99.999% 가용성 목표
- Row-level locking
- 트랜잭션 지원
- Shared-nothing 아키텍처
- 자동 데이터 분산
- 최대 384EB
- 별도 매뉴얼: Chapter 25 MySQL NDB Cluster 8.4

## 엔진 선택 기준 (공식 권장)

| 사용 사례                    | 권장 엔진    |
|------------------------------|--------------|
| 범용 (기본)                  | InnoDB       |
| 트랜잭션 필요                | InnoDB / NDB |
| Read-only / Read-mostly      | MyISAM       |
| 임시 조회/캐시 (비영속)      | MEMORY       |
| CSV import/export            | CSV          |
| 감사 로그 / 대용량 아카이브  | ARCHIVE      |
| Replication 필터             | BLACKHOLE    |
| 동일 MyISAM 테이블 논리 결합 | MERGE        |
| 원격 MySQL 서버 데이터 접근  | FEDERATED    |
| 고가용성 (99.999%)           | NDB          |

## 주요 명령어

```sql
-- 지원 엔진 확인
SHOW ENGINES;

-- 특정 테이블 엔진 확인
SHOW TABLE STATUS WHERE Name = 'table_name';

-- 엔진 지정하여 테이블 생성
CREATE TABLE t (id INT PRIMARY KEY) ENGINE = InnoDB;

-- 엔진 변경
ALTER TABLE t ENGINE = InnoDB;
```

## 주의사항

- 동일 스키마 내에서 테이블별 다른 엔진 사용 가능
- InnoDB 외 엔진 사용 시 FK, 트랜잭션 미지원 확인 필수
- MySQL 8.4에서 시스템 테이블은 모두 InnoDB (MyISAM 시스템 테이블 제거됨)
- MEMORY 엔진은 InnoDB buffer pool로 대부분 대체 가능
- MERGE 엔진은 파티셔닝으로 대체 권장
