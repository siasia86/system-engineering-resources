# dbtrail Forensics — 누가 변경했나

변경 이벤트를 DB 사용자, 호스트, 클라이언트 프로그램까지 추적하는 감사 기능을 상세히 설명합니다.

## 목차

| 섹션                                                                                                            |
|-----------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 추적 방법](#2-추적-방법) / [3. Audit Plugin](#3-audit-plugin) / [4. 사용법](#4-사용법) |

---

## 1. 개요

### binlog의 한계

MySQL binlog는 **connection_id(연결 번호)**만 기록합니다. "누가"는 기록하지 않습니다.

```
binlog 이벤트:
  connection_id: 42
  event_type: DELETE
  table: orders
  row_before: {id: 123, amount: 50000}

  → "42번 연결이 삭제했다" — 하지만 42번이 누군지는?
```

dbtrail Forensics는 이 connection_id를 **이름으로 변환**합니다.

### 추적 가능 정보

| 정보                | 출처              | 예시                               |
|---------------------|-------------------|------------------------------------|
| DB 사용자           | `USER()`          | `admin@10.200.90.155`              |
| 클라이언트 프로그램 | `program_name`    | `python3`, `mysql-cli`             |
| 호스트 IP           | `HOST`            | `10.200.90.155`                    |
| 원본 SQL            | `query_text`      | `DELETE FROM orders WHERE id=123`  |
| 실행 시각           | `event_timestamp` | `2026-07-06 14:32:11`              |
| 신뢰도              | confidence label  | `exact`, `corroborated`, `unknown` |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 추적 방법

### 세 가지 모드

| 모드              | 구성                                     | 정확도 | 세션 종료 후         |
|-------------------|------------------------------------------|--------|----------------------|
| A: Plain capture  | `bintrail stream`만                      | 낮음   | ❌ 추적 불가         |
| B: Identity cache | `bintrail up` / `bintrail-console watch` | 중간   | ✅ 캐시 내 (24h)     |
| C: Audit plugin   | MySQL audit plugin 설치                  | 높음   | ✅ 로그 보존 기간 내 |

### 모드별 추적 가능 범위

| 상황                 | A: plain       | B: + cache     | C: + audit |
|----------------------|----------------|----------------|------------|
| 세션이 아직 연결 중  | ✅             | ✅             | ✅         |
| 세션이 이미 종료됨   | ❌             | ✅ (캐시 내)   | ✅         |
| 며칠 전 변경         | ❌             | ❌ (24h 초과)  | ✅         |
| 0.5초 미만 짧은 세션 | ❌             | ⚠️ 누락 가능   | ✅         |
| 원본 SQL 문          | ✅ (별도 설정) | ✅ (별도 설정) | ✅         |

### Identity Cache 동작

```
bintrail up / console watch:
  매 0.5초마다 MySQL PROCESSLIST 폴링
  → connection_id → user, host, program 매핑 저장
  → 세션 종료 후에도 24시간 캐시 유지

한계: 폴링 간격(0.5초) 사이에 연결+변경+종료하면 누락
```

### Confidence 라벨

| 라벨           | 의미       | 근거                                          |
|----------------|------------|-----------------------------------------------|
| `exact`        | 확실       | audit plugin CONNECT/DISCONNECT 기록으로 증명 |
| `corroborated` | 높은 확률  | identity cache에서 해당 시점에 연결 확인      |
| `unknown`      | 알 수 없음 | 연결 정보 없음 (세션 종료 + 캐시 만료)        |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Audit Plugin

### 지원 플러그인

| 플러그인               | 대상             | 특징                |
|------------------------|------------------|---------------------|
| Percona Audit Log      | Percona Server   | JSON/CSV 포맷, 경량 |
| MariaDB Audit Plugin   | MariaDB          | MariaDB 내장        |
| MySQL Enterprise Audit | MySQL Enterprise | 상용 라이선스 필요  |
| AWS RDS Audit          | RDS/Aurora       | CloudWatch 연동     |

### Percona Audit Log 설정

```sql
-- 플러그인 설치
INSTALL PLUGIN audit_log SONAME 'audit_log.so';

-- 설정 (my.cnf)
[mysqld]
audit_log_format = JSON
audit_log_policy = LOGINS    -- CONNECT/DISCONNECT만 (경량)
audit_log_file = /var/log/mysql/audit.log
```

### RDS Audit 설정

```
파라미터 그룹:
  server_audit_logging = ON
  server_audit_events = CONNECT,QUERY_DML

CloudWatch:
  /aws/rds/audit → dbtrail이 자동 수집
```

### bintrail doctor 확인

```bash
bintrail doctor --host 192.0.2.1 --user dbtrail --password SecurePassword123
# ...
# [forensics] audit plugin: percona audit_log (JSON)
# [forensics] audit log path: /var/log/mysql/audit.log
# [forensics] recommendation: ✓ full forensics available
```

audit plugin이 없으면:

```
# [forensics] audit plugin: NOT INSTALLED
# [forensics] recommendation: install percona audit_log for full "who changed" attribution
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 사용법

### whochanged (특정 행 변경자 추적)

```bash
bintrail whochanged --schema shop --table orders --pk 123

# 출력:
# ┌─────────────────────┬────────┬──────────────────────────┬──────────────┬─────────────┐
# │ timestamp           │ type   │ user                     │ program      │ confidence  │
# ├─────────────────────┼────────┼──────────────────────────┼──────────────┼─────────────┤
# │ 2026-07-06 14:32:11 │ UPDATE │ admin@10.200.90.155      │ python3      │ corroborated│
# │ 2026-07-06 10:15:03 │ UPDATE │ app_user@10.200.101.50   │ java         │ exact       │
# │ 2026-07-01 09:00:00 │ INSERT │ migration@localhost      │ mysql-cli    │ exact       │
# └─────────────────────┴────────┴──────────────────────────┴──────────────┴─────────────┘
```

### query + user 필터

```bash
# 특정 사용자의 모든 변경
bintrail query --user admin --since '2026-07-06'

# 특정 호스트에서의 DELETE만
bintrail query --table orders --event-type DELETE \
  --column-eq _meta_host=10.200.90.155
```

### 원본 SQL 확인

`binlog_rows_query_log_events=ON` 설정 시 query_text가 저장됩니다.

```bash
bintrail query --schema shop --table orders --pk 123 --format json | jq '.query_text'
# "UPDATE orders SET amount=0 WHERE id=123"
```

### 활성화 (MySQL)

```sql
-- 동적 설정 (재시작 불필요)
SET PERSIST binlog_rows_query_log_events = ON;
```

### 웹 콘솔에서 확인

1. http://127.0.0.1:8090 → Forensics 탭
2. 테이블/PK 입력 → 변경 이력 + 사용자 정보 표시
3. confidence 라벨로 추적 정확도 확인

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [README.md](./README.md)
- [recovery_guide.md](./recovery_guide.md)
- dbtrail Forensics: [github.com/dbtrail/dbtrail/blob/main/docs/forensics.md](https://github.com/dbtrail/dbtrail/blob/main/docs/forensics.md) — ★★☆☆☆

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
