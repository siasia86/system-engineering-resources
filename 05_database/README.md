# Database

RDBMS와 NoSQL 운영. 쿼리 최적화, 복제, 백업, 장애 복구를 다룹니다.

## 구조

| 디렉토리                     | 설명                                                                      | 문서 수 |
|------------------------------|---------------------------------------------------------------------------|---------|
| [rdbms/](./rdbms/)           | RDBMS 이론 — Index, Join, Lock, 정규화, Storage Engine                    | 9       |
| [operations/](./operations/) | DB 운영 — 설치, 복제, 파티션, 백업(pg·mysqldump·Xtrabackup), VACUUM, 풀링 | 13      |
| [nosql/](./nosql/)           | NoSQL — Redis, MongoDB, Elasticsearch 설치 및 운영                        | 6       |
| [forensics/](./forensics/)   | DB 포렌식 — 아키텍처 분석, 장애 복구 가이드                               | 3       |

## 주요 문서

- [mysql_storage_engine.md](./rdbms/mysql_storage_engine.md) — InnoDB, MyISAM, Storage Engine 비교
- [rdbms_index.md](./rdbms/rdbms_index.md) — B-Tree, 커버링 인덱스, 실행 계획
- [rdbms_replication.md](./operations/rdbms_replication.md) — Primary-Replica, GTID, 지연 감시
- [percona_xtrabackup_guide.md](./operations/percona_xtrabackup_guide.md) — 무중단 물리 백업
- [postgresql_backup_pitr.md](./operations/postgresql_backup_pitr.md) — pg_dump, pg_basebackup, WAL 아카이빙 PITR
- [mysql_logical_backup.md](./operations/mysql_logical_backup.md) — mysqldump, MySQL Shell dump, binlog PITR
- [postgresql_vacuum.md](./operations/postgresql_vacuum.md) — autovacuum 튜닝, XID 랩어라운드
- [pgbouncer_connection_pooling.md](./operations/pgbouncer_connection_pooling.md) — 풀 모드, 인증, 무중단 작업
- [nosql_redis.md](./nosql/nosql_redis.md) — Redis 자료구조, Cluster, Sentinel
- [recovery_guide.md](./forensics/recovery_guide.md) — 장애 유형별 복구 절차

## 추천 학습 순서

`rdbms (이론)` → `operations (설치/운영)` → `nosql (Redis/ES)` → `forensics (장애 복구)`

## 전제 조건

SQL 기본 문법. [01_fundamentals/linux/](../01_fundamentals/linux/) 파일시스템 이해 권장.

## 관련 섹션

- 로그 파이프라인: [02_infrastructure/data_pipeline/](../02_infrastructure/data_pipeline/)
- DBA 로드맵: [06_career/roadmap/dba_roadmap.md](../06_career/roadmap/dba_roadmap.md)

[⬆ 루트 README로 돌아가기](../README.md)

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
