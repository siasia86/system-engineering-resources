# DBA (Database Administrator) 커리어 로드맵

## 목차

| 섹션 |
|------|
| [1. DBA 역할과 SE와의 차이](#1-dba-역할과-se와의-차이) / [2. 필수 기초 지식](#2-필수-기초-지식) / [3. RDBMS 심화](#3-rdbms-심화) |
| [4. 운영 및 모니터링](#4-운영-및-모니터링) / [5. 고가용성 & 확장성](#5-고가용성-확장성) / [6. NoSQL & 클라우드 DB](#6-nosql-클라우드-db) |
| [7. 학습 로드맵](#7-학습-로드맵) / [8. 자격증](#8-자격증) |


---

## 1. DBA 역할과 SE와의 차이

### DBA (Database Administrator)

데이터베이스의 설계, 구축, 운영, 성능 최적화, 보안, 백업/복구를 전담하는 역할.

| 항목 | DBA | SE (System Engineer) |
|------|-----|----------------------|
| 주요 관심사 | 데이터 정합성, 쿼리 성능, 스키마 설계 | 서버 인프라, 네트워크, 운영체제 |
| 핵심 도구 | MySQL, PostgreSQL, Oracle, MongoDB | Linux, Ansible, Terraform, Docker |
| 성능 지표 | QPS, 슬로우 쿼리, 복제 지연 | CPU/메모리/디스크 사용률, 네트워크 |
| 장애 대응 | DB 복구, 데이터 복원, 복제 재구성 | 서버 재시작, 네트워크 복구 |
| 협업 대상 | 개발자, SE, 데이터 엔지니어 | DBA, 네트워크 엔지니어, 보안팀 |

### DBA 유형

| 유형 | 설명 |
|------|------|
| **운영 DBA** | 일상적인 DB 운영, 모니터링, 백업, 패치 |
| **개발 DBA** | 스키마 설계, 쿼리 최적화, 인덱스 설계 |
| **클라우드 DBA** | RDS, Aurora, Cloud SQL 등 관리형 DB 운영 |
| **데이터 아키텍트** | 전사 데이터 모델 설계, 데이터 거버넌스 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 필수 기초 지식

### OS & 인프라

```
Linux 기초
├── 파일 시스템 (ext4, XFS) — DB 데이터 파일 저장
├── I/O 스케줄러 — DB 성능에 직접 영향
├── 메모리 관리 (swap, huge pages)
└── 네트워크 (TCP 튜닝, 소켓 버퍼)
```

### SQL 기초

```
SQL
├── DDL: CREATE, ALTER, DROP
├── DML: SELECT, INSERT, UPDATE, DELETE
├── DCL: GRANT, REVOKE
└── TCL: COMMIT, ROLLBACK, SAVEPOINT
```

### 필수 개념

| 개념 | 설명 | 관련 문서 |
|------|------|-----------|
| 정규화 | 1NF~BCNF, 반정규화 | [rdbms_normalization.md](../09_database/rdbms_normalization.md) |
| 인덱스 | B-Tree, 복합 인덱스 | [rdbms_index.md](../09_database/rdbms_index.md) |
| 트랜잭션 | ACID, 격리 수준 | [rdbms_transaction.md](../09_database/rdbms_transaction.md) |
| 실행 계획 | EXPLAIN 분석 | [rdbms_explain.md](../09_database/rdbms_explain.md) |

[⬆ 목차로 돌아가기](#목차)

---

## 3. RDBMS 심화

### 학습 순서

```
1. 인덱스 설계     → 조회 성능의 핵심
2. 실행 계획 분석  → 슬로우 쿼리 튜닝
3. 트랜잭션/Lock   → 동시성 제어
4. 파티셔닝        → 대용량 테이블 관리
5. 복제            → 고가용성 기반
6. 스키마 마이그레이션 → 무중단 운영
```

### DBMS별 특화 학습

| DBMS | 핵심 학습 포인트 |
|------|-----------------|
| **MySQL InnoDB** | Buffer Pool, Redo/Undo Log, GTID 복제, pt-osc |
| **PostgreSQL** | MVCC, VACUUM, pg_stat_statements, Logical Replication |
| **Oracle** | RAC, ASM, RMAN, AWR/ASH 성능 분석 |
| **MariaDB** | Galera Cluster, Aria 스토리지 엔진 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 운영 및 모니터링

### 일상 운영 체크리스트

```bash
# 복제 지연 확인
SHOW REPLICA STATUS\G  # Seconds_Behind_Source

# 슬로우 쿼리 확인
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY mean_exec_time DESC LIMIT 10;

# 테이블 크기 확인
SELECT table_name, ROUND(data_length/1024/1024, 1) AS data_mb
FROM information_schema.tables
WHERE table_schema = 'mydb'
ORDER BY data_length DESC;

# 현재 실행 중인 쿼리
SHOW PROCESSLIST;
SELECT * FROM information_schema.innodb_trx;
```

### 모니터링 지표

| 지표 | 임계값 기준 | 도구 |
|------|------------|------|
| QPS (Queries Per Second) | 기준선 대비 2배 이상 | Prometheus + mysqld_exporter |
| 복제 지연 | > 30초 경보 | Seconds_Behind_Source |
| Buffer Pool Hit Rate | < 95% 경보 | innodb_buffer_pool_reads |
| 슬로우 쿼리 수 | 급증 시 경보 | slow_query_log |
| 디스크 사용률 | > 80% 경보 | df, iostat |
| Connection 수 | max_connections 80% | Threads_connected |

### 백업 전략

| 방식 | 도구 | 특징 |
|------|------|------|
| 논리 백업 | mysqldump, pg_dump | 이식성 높음, 대용량 느림 |
| 물리 백업 | Percona XtraBackup, pg_basebackup | 빠름, 온라인 가능 |
| 스냅샷 | AWS RDS 스냅샷, LVM snapshot | 즉시 복구 가능 |
| 바이너리 로그 | binlog + 풀백업 | Point-in-Time Recovery |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 고가용성 & 확장성

### 아키텍처 패턴

```
단일 서버
    │
    ▼
Primary + Replica (읽기 분산)
    │
    ▼
Primary + Replica + Failover (자동 전환)
    │
    ▼
Cluster (MySQL InnoDB Cluster / Galera / Patroni)
    │
    ▼
Sharding (수평 확장)
```

### Failover 도구

| 도구 | DBMS | 설명 |
|------|------|------|
| **MHA** | MySQL | Master High Availability Manager |
| **Orchestrator** | MySQL | 복제 토폴로지 관리, 자동 Failover |
| **Patroni** | PostgreSQL | etcd/Consul 기반 HA |
| **ProxySQL** | MySQL | 쿼리 라우팅, 읽기/쓰기 분리 |
| **PgBouncer** | PostgreSQL | 커넥션 풀링 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. NoSQL & 클라우드 DB

### NoSQL 선택 기준

| 요구사항 | 선택 DB |
|----------|---------|
| 유연한 스키마, 문서 저장 | MongoDB |
| 캐시, 세션, 실시간 랭킹 | Redis |
| 전문 검색, 로그 분석 | Elasticsearch |
| 대용량 시계열, IoT | Cassandra, InfluxDB |
| 관계 탐색 (SNS, 추천) | Neo4j |

### 클라우드 관리형 DB

| 서비스 | 설명 |
|--------|------|
| **AWS RDS** | MySQL, PostgreSQL, Oracle, SQL Server 관리형 |
| **AWS Aurora** | MySQL/PostgreSQL 호환, 최대 15 Read Replica |
| **AWS DynamoDB** | 서버리스 NoSQL, 자동 확장 |
| **GCP Cloud SQL** | MySQL, PostgreSQL, SQL Server |
| **Azure SQL** | SQL Server 관리형 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 학습 로드맵

### 단계별 목표

| 단계 | 기간 | 목표 | 핵심 스킬 |
|------|------|------|-----------|
| **입문** | 0~6개월 | SQL 기초, 단일 DB 운영 | SELECT 최적화, 인덱스, 백업 |
| **초급** | 6~18개월 | 복제 구성, 모니터링 | GTID 복제, 슬로우 쿼리 분석 |
| **중급** | 18~36개월 | HA 구성, 대용량 튜닝 | Orchestrator, 파티셔닝, pt-osc |
| **고급** | 36개월+ | 아키텍처 설계, 클라우드 | Sharding, Aurora, 데이터 모델링 |

### 추천 학습 순서 (내부 문서)

```
09_database/
├── rdbms_normalization.md  → 설계 기초
├── rdbms_index.md          → 성능 핵심
├── rdbms_explain.md        → 튜닝 실전
├── rdbms_transaction.md    → 동시성 이해
├── rdbms_lock.md           → 잠금 메커니즘
├── rdbms_replication.md    → HA 기반
├── rdbms_partition.md      → 대용량 관리
└── rdbms_schema_migration.md → 무중단 운영

10_nosql/
├── nosql_mongodb.md
├── nosql_redis.md
└── nosql_elasticsearch.md
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 자격증

| 자격증 | 발급 기관 | 난이도 | 추천 대상 |
|--------|-----------|--------|-----------|
| **MySQL Database Administrator** | Oracle | ★★★☆☆ | MySQL DBA 입문 |
| **Oracle Database Administrator** | Oracle | ★★★★☆ | 엔터프라이즈 환경 |
| **AWS Database Specialty** | AWS | ★★★★☆ | 클라우드 DBA |
| **MongoDB Associate DBA** | MongoDB | ★★★☆☆ | NoSQL DBA |
| **PostgreSQL Professional** | EDB | ★★★☆☆ | PostgreSQL 전문화 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- roadmap.sh DBA: [roadmap.sh/postgresql-dba](https://roadmap.sh/postgresql-dba) — ★★★★★
- Use The Index, Luke: [use-the-index-luke.com](https://use-the-index-luke.com/) — ★★★★★
- Percona Blog: [percona.com/blog](https://www.percona.com/blog/) — ★★★★☆
- Planet MySQL: [planet.mysql.com](https://planet.mysql.com/) — ★★★☆☆
- PostgreSQL Documentation: [postgresql.org/docs](https://www.postgresql.org/docs/current/) — ★★★★☆
- AWS Database Blog: [aws.amazon.com/blogs/database](https://aws.amazon.com/blogs/database/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-30

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
