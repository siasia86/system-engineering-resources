# RDBMS 튜닝

데이터베이스 성능 최적화의 체계적 접근 방법입니다. 설계 → 쿼리 → 서버 설정 → 인프라 순서로 효과가 큰 계층부터 다룹니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 튜닝 계층](#1-튜닝-계층) / [2. 튜닝 순서](#2-튜닝-순서) / [3. 설계 튜닝](#3-설계-튜닝)               |
| [4. 쿼리 튜닝](#4-쿼리-튜닝) / [5. 서버 설정 튜닝](#5-서버-설정-튜닝) / [6. 인프라 튜닝](#6-인프라-튜닝) |
| [7. 튜닝 전후 측정](#7-튜닝-전후-측정) / [8. 안티패턴](#8-안티패턴)                                      |

---

## 1. 튜닝 계층

```
효과 큼
  │
  │  ┌───────────────────────────────────────────┐
  │  │ 1. 설계 (Design)                          │
  │  │    정규화/반정규화, 파티션, 테이블 분리    │
  │  ├───────────────────────────────────────────┤
  │  │ 2. 쿼리 (SQL)                             │
  │  │    인덱스, EXPLAIN, JOIN, 서브쿼리        │
  │  ├───────────────────────────────────────────┤
  │  │ 3. 서버 설정 (Configuration)              │
  │  │    buffer pool, connections, log           │
  │  ├───────────────────────────────────────────┤
  │  │ 4. 인프라 (Infrastructure)                │
  │  │    SSD, 메모리, CPU, 네트워크             │
  │  └───────────────────────────────────────────┘
  v
효과 작음
```

| 계층      | 효과  | 비용                 | 빈도                      |
|-----------|-------|----------------------|---------------------------|
| 설계      | ★★★★★ | 높음 (스키마 변경)   | 초기 또는 대규모 리팩토링 |
| 쿼리      | ★★★★☆ | 낮음 (코드 수정)     | 매우 자주                 |
| 서버 설정 | ★★★☆☆ | 낮음 (재시작)        | 초기 + 주기적             |
| 인프라    | ★★☆☆☆ | 높음 (하드웨어 비용) | 마지막 수단               |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 튜닝 순서

### 실무 흐름

```bash
# 1. 문제 식별: 어디가 느린가?
mysqladmin extended-status | grep -i 'slow\|threads\|connections'
SHOW GLOBAL STATUS LIKE 'Slow_queries';

# 2. 슬로우 쿼리 분석: 왜 느린가?
mysqldumpslow -s t /var/log/mysql/slow.log | head -20

# 3. 실행 계획 확인
EXPLAIN ANALYZE SELECT ...;

# 4. 인덱스 추가/수정
CREATE INDEX ...;

# 5. 효과 측정
# 쿼리 실행 시간 비교 (전 vs 후)
```

### 튜닝 판단 기준

| 지표                 | 정상    | 주의     | 위험  |
|----------------------|---------|----------|-------|
| 쿼리 응답 시간       | < 100ms | 100ms~1s | > 1s  |
| 슬로우 쿼리 비율     | < 1%    | 1~5%     | > 5%  |
| Buffer Pool Hit Rate | > 99%   | 95~99%   | < 95% |
| Threads_running      | < 10    | 10~30    | > 30  |
| Lock Wait            | < 1s    | 1~5s     | > 5s  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설계 튜닝

### 반정규화

| 상황                 | 정규화 (3NF)            | 반정규화                    |
|----------------------|-------------------------|-----------------------------|
| JOIN 3개 테이블 매번 | 데이터 무결성 ✅ , 느림 | 컬럼 복사로 JOIN 제거, 빠름 |
| 집계 쿼리 매번 COUNT | 정확함, 느림            | summary 테이블, 빠름        |

```sql
-- 정규화: 매번 JOIN
SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id;

-- 반정규화: orders에 customer_name 복사
SELECT id, customer_name, amount FROM orders WHERE id = 123;
-- JOIN 제거 → 속도 향상, but 데이터 동기화 필요
```

### 파티셔닝

```sql
-- 날짜 기준 RANGE 파티션 (1억 행 → 월별 분할)
ALTER TABLE orders PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202601 VALUES LESS THAN (202602),
    PARTITION p202602 VALUES LESS THAN (202603),
    PARTITION p202607 VALUES LESS THAN (202608)
);

-- 효과: WHERE created_at >= '2026-07-01' → p202607만 스캔 (partition pruning)
```

### 테이블 분리

| 전략      | 방법                           | 효과                            |
|-----------|--------------------------------|---------------------------------|
| 수직 분리 | 자주 쓰는 컬럼 / 큰 TEXT 분리  | 행 크기 감소 → buffer pool 효율 |
| 수평 분리 | 날짜/ID 기준 테이블 분할       | 테이블 크기 제한                |
| 아카이브  | 오래된 데이터 별도 테이블 이동 | 활성 테이블 크기 유지           |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 쿼리 튜닝

### EXPLAIN 확인

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 456 AND status = 'active';

-- 핵심 지표:
-- type: ALL (풀스캔 → 나쁨) / ref (인덱스 → 좋음) / const (PK → 최고)
-- rows: 스캔 예상 행 수 (적을수록 좋음)
-- Extra: Using filesort (정렬 부하), Using temporary (임시 테이블)
```

### 인덱스 추가

```sql
-- 복합 인덱스 (WHERE + ORDER BY 커버)
CREATE INDEX idx_customer_status_date
ON orders(customer_id, status, created_at DESC);

-- 커버링 인덱스 (SELECT 컬럼까지 포함 → 테이블 접근 제거)
CREATE INDEX idx_cover
ON orders(customer_id, status, amount, created_at);
```

### 쿼리 리팩토링

| 느린 패턴                  | 빠른 패턴           |
|----------------------------|---------------------|
| `SELECT *`                 | 필요 컬럼만 명시    |
| `IN (SELECT ...)` 서브쿼리 | `JOIN`              |
| `OR` 조건                  | `UNION ALL`         |
| `LIKE '%keyword%'`         | Full-Text Index     |
| `ORDER BY RAND()`          | 사전 랜덤 ID 테이블 |
| `COUNT(*)` 매번            | summary 테이블 캐시 |

```sql
-- 느림: 상관 서브쿼리 (N+1)
SELECT * FROM orders
WHERE customer_id IN (SELECT id FROM customers WHERE grade = 'vip');

-- 빠름: JOIN
SELECT o.* FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE c.grade = 'vip';
```

> 상세: [rdbms_explain.md](./rdbms_explain.md), [rdbms_index.md](./rdbms_index.md)

[⬆ 목차로 돌아가기](#목차)

---

## 5. 서버 설정 튜닝

> 상세: [rdbms_server_config.md](./rdbms_server_config.md)

### 핵심 파라미터

| 파라미터                         | 기본값 | 권장                | 설명                         |
|----------------------------------|--------|---------------------|------------------------------|
| `innodb_buffer_pool_size`        | 128M   | 물리 메모리 70~80%  | 데이터+인덱스 캐시           |
| `innodb_log_file_size`           | 48M    | 1~2G                | redo log 크기 (쓰기 성능)    |
| `innodb_flush_log_at_trx_commit` | 1      | 1 (안전) / 2 (성능) | fsync 빈도                   |
| `max_connections`                | 151    | 실제 필요 + 여유    | 동시 접속 수                 |
| `innodb_io_capacity`             | 200    | SSD: 2000~4000      | I/O 처리량 힌트              |
| `innodb_read_io_threads`         | 4      | 8~16                | 읽기 I/O 스레드 수           |
| `innodb_write_io_threads`        | 4      | 8~16                | 쓰기 I/O 스레드 수           |
| `tmp_table_size`                 | 16M    | 64~256M             | 메모리 임시 테이블 크기      |
| `join_buffer_size`               | 256K   | 1~4M                | JOIN 버퍼 (인덱스 없는 JOIN) |
| `sort_buffer_size`               | 256K   | 1~2M                | 정렬 버퍼                    |

### Buffer Pool 크기 결정

```sql
-- 현재 사용량 확인
SELECT
    ROUND(@@innodb_buffer_pool_size / 1024 / 1024 / 1024, 1) AS pool_gb,
    ROUND((SELECT VARIABLE_VALUE FROM performance_schema.global_status
           WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests') /
          (SELECT VARIABLE_VALUE FROM performance_schema.global_status
           WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') , 1) AS hit_ratio;

-- hit_ratio < 99 → buffer pool 증가 필요
```

### 쓰기 성능 vs 안정성

| `innodb_flush_log_at_trx_commit` | 동작                             | 성능 | 안정성                |
|----------------------------------|----------------------------------|------|-----------------------|
| 1                                | 매 커밋마다 fsync                | 느림 | ✅ (크래시 시 0 손실) |
| 2                                | 매 커밋마다 write, 1초마다 fsync | 중간 | 최대 1초 손실         |
| 0                                | 1초마다 write+fsync              | 빠름 | 최대 1초 손실         |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 인프라 튜닝

### 디스크 I/O

| 항목      | HDD      | SSD (SATA) | NVMe       |
|-----------|----------|------------|------------|
| 랜덤 IOPS | 150      | 50,000     | 500,000+   |
| 순차 읽기 | 150 MB/s | 500 MB/s   | 3,500 MB/s |
| DB 적합도 | ❌       | ✅         | ✅ ✅      |

### 메모리

```
원칙: 활성 데이터셋(working set)이 메모리에 들어가야 함

데이터 50GB + 인덱스 20GB = 70GB
→ buffer pool 56GB (80%) + OS 14GB
→ 물리 메모리: 72~80GB 필요
```

### OS 튜닝 (Linux)

```bash
# /etc/sysctl.conf
vm.swappiness = 1               # swap 최소화 (DB는 swap 사용 금지)
vm.dirty_ratio = 15             # dirty page 비율 제한
vm.dirty_background_ratio = 5   # background flush 시작점
net.core.somaxconn = 4096       # 연결 대기 큐

# I/O 스케줄러 (SSD)
echo none > /sys/block/sda/queue/scheduler

# 파일 디스크립터
ulimit -n 65535
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 튜닝 전후 측정

### 측정 방법

```sql
-- 쿼리 실행 시간 (MySQL 8.0+)
SET profiling = 1;
SELECT ...;
SHOW PROFILES;

-- performance_schema
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;
```

### 보고서 형식

```
튜닝 대상: orders 테이블 조회 (customer_id 검색)
변경 내용: idx_customer_status 인덱스 추가
측정 환경: 500만 행, MySQL 8.0, 32GB RAM

| 지표           | Before  | After | 개선율 |
|----------------|---------|-------|--------|
| 실행 시간      | 2,340ms | 12ms  | 99.5%  |
| 스캔 행 수     | 5M      | 47    | 99.9%  |
| type (EXPLAIN) | ALL     | ref   | -      |
| 디스크 I/O     | 1,200   | 2     | 99.8%  |
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 안티패턴

| 안티패턴                | 문제                        | 올바른 방법                     |
|-------------------------|-----------------------------|---------------------------------|
| 인덱스 과다 (10개+)     | 쓰기 성능 저하, 디스크 낭비 | 실제 쿼리 패턴 기반 필요한 것만 |
| `SELECT *` 남용         | 불필요한 데이터 전송        | 필요 컬럼만 명시                |
| N+1 쿼리 (ORM)          | 1000행 → 1001번 쿼리        | JOIN 또는 IN으로 일괄 조회      |
| 큰 트랜잭션             | Lock 장시간 보유            | 배치 분할 (1000건씩 COMMIT)     |
| 튜닝 없이 하드웨어 증설 | 비용 낭비                   | 쿼리/인덱스 먼저 확인           |
| 운영 중 DDL             | 테이블 잠금                 | pt-online-schema-change 사용    |
| 일괄 DELETE 100만 행    | binlog 폭발 + Lock          | LIMIT 1000씩 반복 삭제          |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [rdbms_explain.md](./rdbms_explain.md) — 실행 계획 분석
- [rdbms_index.md](./rdbms_index.md) — 인덱스 설계
- [rdbms_partition.md](./rdbms_partition.md) — 파티셔닝
- [rdbms_lock.md](./rdbms_lock.md) — 잠금/동시성
- [rdbms_slow_query.md](./rdbms_slow_query.md) — 슬로우 쿼리 분석
- [rdbms_server_config.md](./rdbms_server_config.md) — 서버 설정

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
