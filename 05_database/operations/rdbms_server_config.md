# RDBMS 서버 설정 (my.cnf)

MySQL/MariaDB 서버 설정 파라미터를 용도별로 정리합니다. 메모리 크기별 권장 값과 설정 변경 방법을 포함합니다.

## 목차

| 섹션                                                                                                                          |
|-------------------------------------------------------------------------------------------------------------------------------|
| [1. 설정 파일 위치](#1-설정-파일-위치) / [2. InnoDB](#2-innodb) / [3. 연결 관리](#3-연결-관리) / [4. 쿼리 캐시](#4-쿼리-캐시) |
| [5. 로깅](#5-로깅) / [6. 복제](#6-복제) / [7. 메모리별 템플릿](#7-메모리별-템플릿) / [8. 변경 방법](#8-변경-방법)             |

---

## 1. 설정 파일 위치

| OS               | 경로                                      |
|------------------|-------------------------------------------|
| RHEL/Rocky       | `/etc/my.cnf`, `/etc/my.cnf.d/`           |
| Ubuntu/Debian    | `/etc/mysql/my.cnf`, `/etc/mysql/conf.d/` |
| macOS (Homebrew) | `/opt/homebrew/etc/my.cnf`                |

```bash
# 현재 읽히는 설정 파일 확인
mysqld --verbose --help 2>/dev/null | grep -A1 "Default options"

# 특정 변수 현재 값
mysql -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size'"
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. InnoDB

🟡 아래 표의 기본값은 MySQL 8.0 기준입니다. 8.4에서는 `innodb_io_capacity`(10000), `innodb_io_capacity_max`(2 × io_capacity), `innodb_flush_method`(Linux: O_DIRECT), `innodb_log_buffer_size`(64M), `innodb_buffer_pool_instances`(자동 계산), `innodb_read_io_threads`(논리 CPU / 2, 최소 4) 기본값이 바뀌었습니다.

### 메모리

| 파라미터                       | 기본값 | 권장            | 설명                           |
|--------------------------------|--------|-----------------|--------------------------------|
| `innodb_buffer_pool_size`      | 128M   | 물리 RAM 70~80% | 데이터+인덱스 캐시 (가장 중요) |
| `innodb_buffer_pool_instances` | 8      | pool_size / 1G  | 동시성 향상 (pool > 1G일 때)   |
| `innodb_log_buffer_size`       | 16M    | 64~128M         | redo log 메모리 버퍼           |

### I/O

| 파라미터                         | 기본값 | 권장                   | 설명                           |
|----------------------------------|--------|------------------------|--------------------------------|
| `innodb_redo_log_capacity`       | 100M   | 2~4G                   | redo log 전체 크기 (쓰기 성능) |
| `innodb_flush_log_at_trx_commit` | 1      | 1 (안전) / 2 (성능)    | 커밋 시 fsync 정책             |
| `innodb_io_capacity`             | 200    | HDD:400, SSD:2000~4000 | I/O 처리 힌트                  |
| `innodb_io_capacity_max`         | 2000   | SSD: 8000~10000        | I/O 최대 처리량                |
| `innodb_read_io_threads`         | 4      | 8~16                   | 읽기 스레드                    |
| `innodb_write_io_threads`        | 4      | 8~16                   | 쓰기 스레드                    |
| `innodb_flush_method`            | fsync  | O_DIRECT               | OS 캐시 우회 (이중 캐시 방지)  |

🟡 `innodb_redo_log_capacity`는 8.0.30부터 `innodb_log_file_size` × `innodb_log_files_in_group`(기본 2)을 대체합니다. 두 옛 변수는 deprecated이며, 8.0.30 이전 MySQL과 MariaDB는 `innodb_log_file_size`를 씁니다.

### 동시성

| 파라미터                    | 기본값 | 권장     | 설명                       |
|-----------------------------|--------|----------|----------------------------|
| `innodb_thread_concurrency` | 0      | 0 (자동) | InnoDB 내부 스레드 수 제한 |
| `innodb_lock_wait_timeout`  | 50     | 10~30    | 행 잠금 대기 타임아웃 (초) |
| `innodb_deadlock_detect`    | ON     | ON       | 데드락 자동 감지           |

### 기타

| 파라미터                  | 기본값 | 권장 | 설명                                |
|---------------------------|--------|------|-------------------------------------|
| `innodb_file_per_table`   | ON     | ON   | 테이블별 파일 (공간 회수 가능)      |
| `innodb_undo_tablespaces` | 2      | -    | 8.0.14+ deprecated, 설정 효과 없음  |
| `innodb_page_size`        | 16K    | 16K  | 페이지 크기 (변경 불가 — 초기 설정) |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 연결 관리

| 파라미터              | 기본값    | 권장                 | 설명                      |
|-----------------------|-----------|----------------------|---------------------------|
| `max_connections`     | 151       | 실제 필요 + 20% 여유 | 최대 동시 접속 수         |
| `max_connect_errors`  | 100       | 1000                 | 호스트 차단 임계값        |
| `wait_timeout`        | 28800     | 300~600              | 비활성 연결 타임아웃 (초) |
| `interactive_timeout` | 28800     | 600                  | 대화형 세션 타임아웃      |
| `thread_cache_size`   | -1 (자동) | 16~64                | 스레드 재사용 캐시        |

### max_connections 결정

```sql
-- 현재 사용량 확인
SHOW GLOBAL STATUS LIKE 'Max_used_connections';
SHOW GLOBAL STATUS LIKE 'Threads_connected';

-- 권장: Max_used_connections × 1.2 (여유 20%)
-- 주의: 연결당 메모리 소비 (sort_buffer + join_buffer + read_buffer 등)
-- max_connections × 연결당 메모리 < 남은 물리 메모리
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 쿼리 캐시

🟡 MySQL 8.0에서 **제거**되었습니다. MySQL은 5.7 이하에서만 해당합니다. MariaDB에는 남아 있지만 기본 OFF이며 사용을 권장하지 않습니다.

| 파라미터           | 5.7 권장 | 8.0+   |
|--------------------|----------|--------|
| `query_cache_type` | OFF      | 제거됨 |
| `query_cache_size` | 0        | 제거됨 |

대안: 애플리케이션 레벨 캐시 (Redis, Memcached) 사용을 권장합니다.

### 임시 테이블/정렬 버퍼

| 파라미터               | 기본값 | 권장    | 설명                                 |
|------------------------|--------|---------|--------------------------------------|
| `tmp_table_size`       | 16M    | 64~256M | 메모리 임시 테이블 최대 크기         |
| `max_heap_table_size`  | 16M    | 64~256M | MEMORY 엔진 테이블 최대 크기         |
| `sort_buffer_size`     | 256K   | 1~2M    | 정렬 버퍼 (연결당)                   |
| `join_buffer_size`     | 256K   | 1~4M    | JOIN 버퍼 (연결당, 인덱스 없는 JOIN) |
| `read_buffer_size`     | 128K   | 256K~1M | 순차 읽기 버퍼 (연결당)              |
| `read_rnd_buffer_size` | 256K   | 512K~2M | 랜덤 읽기 버퍼                       |

🟡 연결당(per-connection) 버퍼는 `max_connections × 버퍼 크기`로 총 메모리가 결정됩니다. 과도한 설정은 OOM을 유발합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 로깅

| 파라미터                        | 권장    | 설명                                    |
|---------------------------------|---------|-----------------------------------------|
| `slow_query_log`                | ON      | 슬로우 쿼리 로그 활성화                 |
| `long_query_time`               | 1       | 기록 임계값 (초)                        |
| `log_queries_not_using_indexes` | ON      | 인덱스 미사용 쿼리 기록                 |
| `general_log`                   | OFF     | 모든 쿼리 기록 (디버깅 시에만 ON)       |
| `binlog_format`                 | ROW     | 바이너리 로그 형식 (8.0.34+ deprecated) |
| `binlog_row_image`              | FULL    | 행 이미지 (dbtrail 등 CDC 도구 필요 시) |
| `expire_logs_days`              | -       | 일 단위 보존 (8.0 deprecated, 8.4 제거) |
| `binlog_expire_logs_seconds`    | 2592000 | 8.0+: 초 단위 binlog 보존               |

> 상세: [rdbms_slow_query.md](./rdbms_slow_query.md)

[⬆ 목차로 돌아가기](#목차)

---

## 6. 복제

| 파라미터                        | 권장    | 설명                            |
|---------------------------------|---------|---------------------------------|
| `server_id`                     | 고유 값 | 복제 서버 식별 (중복 불가)      |
| `log_bin`                       | ON      | 바이너리 로그 활성화            |
| `gtid_mode`                     | ON      | GTID 기반 복제 (권장)           |
| `enforce_gtid_consistency`      | ON      | GTID 호환 트랜잭션 강제         |
| `replica_parallel_workers`      | 4~16    | 병렬 복제 워커 수               |
| `replica_preserve_commit_order` | ON      | 커밋 순서 보장                  |
| `sync_binlog`                   | 1       | 매 커밋마다 binlog fsync (안전) |

> 상세: [rdbms_replication.md](./rdbms_replication.md)

[⬆ 목차로 돌아가기](#목차)

---

## 7. 메모리별 템플릿

### 8GB 서버 (소규모)

```ini
[mysqld]
innodb_buffer_pool_size = 5G
innodb_redo_log_capacity = 1G
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT
innodb_io_capacity = 2000

max_connections = 200
thread_cache_size = 32
tmp_table_size = 64M
max_heap_table_size = 64M
sort_buffer_size = 1M
join_buffer_size = 1M

slow_query_log = 1
long_query_time = 1
```

### 32GB 서버 (중규모)

```ini
[mysqld]
innodb_buffer_pool_size = 24G
innodb_buffer_pool_instances = 24
innodb_redo_log_capacity = 4G
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT
innodb_io_capacity = 4000
innodb_io_capacity_max = 8000
innodb_read_io_threads = 8
innodb_write_io_threads = 8

max_connections = 500
thread_cache_size = 64
tmp_table_size = 128M
max_heap_table_size = 128M
sort_buffer_size = 2M
join_buffer_size = 2M

slow_query_log = 1
long_query_time = 1
```

### 128GB 서버 (대규모)

```ini
[mysqld]
innodb_buffer_pool_size = 96G
innodb_buffer_pool_instances = 64
innodb_redo_log_capacity = 8G
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT
innodb_io_capacity = 8000
innodb_io_capacity_max = 16000
innodb_read_io_threads = 16
innodb_write_io_threads = 16

max_connections = 1000
thread_cache_size = 128
tmp_table_size = 256M
max_heap_table_size = 256M
sort_buffer_size = 2M
join_buffer_size = 4M

slow_query_log = 1
long_query_time = 1
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 변경 방법

### 동적 변경 (재시작 불필요)

```sql
-- 전역에 즉시 적용 (재시작하면 my.cnf 값으로 돌아감)
SET GLOBAL innodb_buffer_pool_size = 24 * 1024 * 1024 * 1024;  -- 24GB
SET GLOBAL max_connections = 500;

-- MySQL 8.0+: 재시작 후에도 유지 (SET PERSIST)
SET PERSIST innodb_io_capacity = 4000;
SET PERSIST max_connections = 500;

-- PERSIST 확인
SELECT * FROM performance_schema.persisted_variables;
```

### 정적 변경 (재시작 필요)

```ini
# /etc/my.cnf 수정 후 재시작
[mysqld]
innodb_page_size = 16384     # 변경 불가 (초기 설정만)
innodb_read_io_threads = 8   # 정적 파라미터
```

```bash
# 설정 검증 (재시작 전)
mysqld --validate-config

# 재시작
sudo systemctl restart mysqld
```

### 동적/정적 구분 확인

```sql
-- VARIABLE_SOURCE는 값을 마지막으로 설정한 출처(COMPILED·GLOBAL·PERSISTED·DYNAMIC 등)이며 동적 여부가 아님
-- 동적/정적 여부는 공식 문서 변수 표의 Dynamic 항목으로 확인 (정적 변수에 SET GLOBAL → ERROR 1238)
SELECT VARIABLE_NAME, VARIABLE_SOURCE
FROM performance_schema.variables_info
WHERE VARIABLE_NAME LIKE 'innodb%'
ORDER BY VARIABLE_NAME;
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [rdbms_tuning.md](./rdbms_tuning.md) — 튜닝 종합
- [rdbms_slow_query.md](./rdbms_slow_query.md) — 슬로우 쿼리
- [rdbms_replication.md](./rdbms_replication.md) — 복제
- MySQL Server Variables: [dev.mysql.com/doc/refman/8.4/en/server-system-variables.html](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html) — ★★★☆☆
- MySQL InnoDB Startup Options and System Variables: [dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html](https://dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html) — ★★★☆☆
- What Is New in MySQL 8.4 since MySQL 8.0: [dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html](https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html) — ★★★☆☆
- Performance Schema variables_info Table: [dev.mysql.com/doc/refman/8.4/en/performance-schema-variables-info-table.html](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-variables-info-table.html) — ★★★☆☆
- MariaDB Query Cache: [mariadb.com/docs](https://mariadb.com/docs/server/ha-and-performance/optimization-and-tuning/buffers-caches-and-threads/query-cache) — ★★★☆☆

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

**마지막 업데이트**: 2026-11-09

© 2026 siasia86. Licensed under CC BY 4.0.
