# RDBMS 슬로우 쿼리 분석

슬로우 쿼리 로그 설정, 분석 도구, 개선 방법을 다룹니다. 성능 문제의 80%는 상위 10개 슬로우 쿼리에서 발생합니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 설정](#1-설정) / [2. 로그 분석](#2-로그-분석) / [3. 분석 도구](#3-분석-도구)                         |
| [4. 개선 흐름](#4-개선-흐름) / [5. performance_schema](#5-performance_schema) / [6. 운영 팁](#6-운영-팁) |

---

## 1. 설정

### MySQL 슬로우 쿼리 로그 활성화

```sql
-- 동적 설정 (재시작 불필요)
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;         -- 1초 이상 쿼리 기록
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
SET GLOBAL log_queries_not_using_indexes = ON;  -- 인덱스 미사용 쿼리도 기록

-- 영구 설정 (my.cnf)
[mysqld]
slow_query_log = 1
long_query_time = 1
slow_query_log_file = /var/log/mysql/slow.log
log_queries_not_using_indexes = 1
```

### 설정 확인

```sql
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';
SHOW GLOBAL STATUS LIKE 'Slow_queries';
```

### long_query_time 권장 값

| 환경        | 권장  | 이유                      |
|-------------|-------|---------------------------|
| 개발/테스트 | 0.1초 | 작은 문제도 감지          |
| 일반 운영   | 1초   | 사용자 체감 기준          |
| 대용량/배치 | 5초   | 배치 쿼리 제외            |
| 최초 분석   | 0     | 모든 쿼리 기록 (단기간만) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 로그 분석

### 슬로우 쿼리 로그 형식

```
# Time: 2026-07-06T14:32:11.123456Z
# User@Host: app_user[app_user] @ [10.200.101.50]  Id: 12345
# Query_time: 3.456789  Lock_time: 0.000123  Rows_sent: 1  Rows_examined: 5000000
SET timestamp=1720274331;
SELECT * FROM orders WHERE customer_id = 456 AND status = 'active';
```

### 핵심 지표

| 필드          | 의미           | 주의 기준                        |
|---------------|----------------|----------------------------------|
| Query_time    | 총 실행 시간   | > 1s                             |
| Lock_time     | 잠금 대기 시간 | > 0.1s                           |
| Rows_sent     | 반환 행 수     | sent << examined이면 인덱스 문제 |
| Rows_examined | 스캔 행 수     | 많을수록 비효율                  |

### 핵심 비율

```
효율 = Rows_sent / Rows_examined

예시: sent=1, examined=5,000,000
→ 효율 = 0.0000002 → 인덱스 필요

예시: sent=100, examined=105
→ 효율 = 0.95 → 정상
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 분석 도구

### mysqldumpslow (MySQL 내장)

```bash
# 실행 시간순 상위 10개
mysqldumpslow -s t /var/log/mysql/slow.log | head -40

# 호출 횟수순
mysqldumpslow -s c /var/log/mysql/slow.log | head -20

# 스캔 행 수순
mysqldumpslow -s r /var/log/mysql/slow.log | head -20

# 특정 테이블만
mysqldumpslow -t 10 -g "orders" /var/log/mysql/slow.log
```

### pt-query-digest (Percona Toolkit)

```bash
# 설치
sudo dnf install percona-toolkit

# 분석 (가장 상세)
pt-query-digest /var/log/mysql/slow.log > report.txt

# 최근 1시간만
pt-query-digest --since '1h' /var/log/mysql/slow.log

# 특정 사용자만
pt-query-digest --filter '$event->{user} eq "app_user"' /var/log/mysql/slow.log
```

### pt-query-digest 출력 예시

```
# Profile
# Rank Query ID                       Response time  Calls R/Call
# ==== ============================== ============== ===== ======
#    1 0xABC123... SELECT orders WHERE   45.2% 340.5s  2341  0.15
#    2 0xDEF456... SELECT users JOIN      22.1% 166.3s   891  0.19
#    3 0x789ABC... UPDATE orders SET      15.3% 115.0s  4521  0.03
```

| 도구               | 장점                    | 단점                         |
|--------------------|-------------------------|------------------------------|
| mysqldumpslow      | 설치 불필요 (내장)      | 간략, 그룹핑 약함            |
| pt-query-digest    | 상세 분석, 정규화, 통계 | 별도 설치 필요               |
| performance_schema | 실시간, 설치 불필요     | 쿼리 레벨이 아닌 digest 레벨 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 개선 흐름

### 단계별 대응

```
1. pt-query-digest → 상위 3개 쿼리 식별
      │
2. EXPLAIN ANALYZE → 실행 계획 확인
      │
      ├── type: ALL → 인덱스 추가
      ├── Using filesort → ORDER BY 인덱스 포함
      ├── Using temporary → 쿼리 리팩토링
      └── rows: 과다 → WHERE 조건 개선
      │
3. 인덱스 추가 또는 쿼리 수정
      │
4. 효과 측정 (Query_time 비교)
```

### 예시: 슬로우 쿼리 → 해결

```sql
-- 슬로우 쿼리 (3.4초)
-- Rows_examined: 5,000,000
SELECT id, amount, created_at FROM orders
WHERE customer_id = 456 AND status = 'active'
ORDER BY created_at DESC LIMIT 10;

-- EXPLAIN 결과
-- type: ALL, rows: 5000000, Extra: Using where; Using filesort

-- 해결: 복합 인덱스
CREATE INDEX idx_cust_status_date ON orders(customer_id, status, created_at DESC);

-- 개선 후 EXPLAIN
-- type: ref, rows: 12, Extra: Using index

-- 결과: 3.4초 → 2ms
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. performance_schema

### 실시간 슬로우 쿼리 (로그 없이)

```sql
-- 가장 느린 쿼리 패턴 TOP 10
SELECT
    DIGEST_TEXT,
    COUNT_STAR AS calls,
    ROUND(SUM_TIMER_WAIT / 1e12, 2) AS total_sec,
    ROUND(AVG_TIMER_WAIT / 1e12, 4) AS avg_sec,
    SUM_ROWS_EXAMINED AS rows_examined,
    SUM_ROWS_SENT AS rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

### 현재 실행 중인 느린 쿼리

```sql
SELECT
    PROCESSLIST_ID,
    PROCESSLIST_USER,
    PROCESSLIST_HOST,
    PROCESSLIST_TIME,
    PROCESSLIST_INFO
FROM performance_schema.threads
WHERE PROCESSLIST_COMMAND = 'Query'
  AND PROCESSLIST_TIME > 5
ORDER BY PROCESSLIST_TIME DESC;
```

### 인덱스 미사용 테이블

```sql
SELECT
    OBJECT_SCHEMA,
    OBJECT_NAME,
    COUNT_READ AS reads_without_index
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE INDEX_NAME IS NULL
  AND COUNT_READ > 1000
ORDER BY COUNT_READ DESC;
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영 팁

### 로그 로테이션

```bash
# logrotate 설정
cat > /etc/logrotate.d/mysql-slow << 'CONF'
/var/log/mysql/slow.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    postrotate
        mysqladmin flush-logs
    endscript
}
CONF
```

### 알림 설정 (Zabbix/Prometheus)

```bash
# Slow_queries 카운터 증가율 모니터링
# Prometheus: rate(mysql_global_status_slow_queries[5m]) > 10
# → 5분간 슬로우 쿼리 10개 이상이면 알림
```

### 정기 분석 루틴

| 주기 | 작업                                          |
|------|-----------------------------------------------|
| 매일 | `SHOW GLOBAL STATUS LIKE 'Slow_queries'` 확인 |
| 매주 | `pt-query-digest --since '7d'` 리포트         |
| 매월 | 상위 10 쿼리 튜닝 검토 + 인덱스 정리          |
| 분기 | performance_schema 기반 전체 분석             |

### 주의사항

| 항목                            | 내용                                             |
|---------------------------------|--------------------------------------------------|
| `long_query_time = 0`           | 모든 쿼리 기록 → 디스크 I/O 부하 (단기간만 사용) |
| 로그 파일 크기                  | 무제한 증가 → logrotate 필수                     |
| `log_queries_not_using_indexes` | 의도된 풀스캔(소규모 테이블)도 기록됨 → 노이즈   |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [rdbms_tuning.md](./rdbms_tuning.md) — 튜닝 종합
- [rdbms_explain.md](../rdbms/rdbms_explain.md) — 실행 계획 분석
- [rdbms_index.md](../rdbms/rdbms_index.md) — 인덱스 설계
- MySQL Slow Query Log: [dev.mysql.com/doc/refman/8.0/en/slow-query-log.html](https://dev.mysql.com/doc/refman/8.0/en/slow-query-log.html) — ★★★☆☆

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
