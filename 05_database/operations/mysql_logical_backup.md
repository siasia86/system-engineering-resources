# MySQL 논리 백업과 binlog 시점 복구
<!-- reference: _reference/mysql_official_notes.md -->

MySQL의 논리 백업 도구(mysqldump, MySQL Shell dump 유틸리티)와 바이너리 로그(binlog)를 이용한 시점 복구(PITR)를 다룹니다. 물리 백업은 [Percona XtraBackup 가이드](./percona_xtrabackup_guide.md)를 봅니다. 기준 판은 MySQL 8.4 LTS(2026-11-09 기준 8.4.13, 저장소 reference 노트 기록)와 MySQL Shell 문서(2026-11-16 확인)입니다.

## 목차

| 섹션                                                                                                          |
|---------------------------------------------------------------------------------------------------------------|
| [1. 백업 도구 선택](#1-백업-도구-선택) / [2. mysqldump 기본](#2-mysqldump-기본)                               |
| [3. 일관성과 복제 좌표](#3-일관성과-복제-좌표) / [4. MySQL Shell dump 유틸리티](#4-mysql-shell-dump-유틸리티) |
| [5. 복원](#5-복원) / [6. binlog 시점 복구](#6-binlog-시점-복구) / [7. binlog 보관](#7-binlog-보관)            |
| [8. 점검표](#8-점검표)                                                                                        |

---

## 1. 백업 도구 선택

| 도구                      | 형태                        | 병렬 처리     | 일관성 방식             | 비고                    |
|---------------------------|-----------------------------|---------------|-------------------------|-------------------------|
| mysqldump                 | SQL 텍스트 1개              | 없음          | `--single-transaction`  | 서버 패키지에 기본 포함 |
| MySQL Shell dump 유틸리티 | 청크 단위 파일 + 메타데이터 | 있음 (기본 4) | 백업 잠금 + 일관 스냅샷 | `mysqlsh` 별도 설치     |
| mydumper / myloader       | 테이블·청크 단위 파일       | 있음          | 일관 스냅샷             | 오픈소스 외부 도구      |
| Percona XtraBackup        | 데이터 파일 복사 (물리)     | 있음          | redo 로그 적용          | 대용량·빠른 복원        |

- **mysqlpump**는 MySQL 8.1.0에서 deprecated되고 **8.4.0에서 제거**되었습니다. 8.4 릴리스 노트는 대신 mysqldump나 MySQL Shell dump 유틸리티를 쓰라고 안내합니다. 옛 스크립트에 `mysqlpump`가 남아 있으면 바꿔야 합니다.
- 논리 백업은 메이저 판 이관, 일부 스키마·테이블만 꺼내기, 다른 엔진·클라우드로 옮기기에 적합합니다. 수백 GB 이상에서 복구 시간이 중요하면 물리 백업을 함께 둡니다.

| 상황                           | 권장                              |
|--------------------------------|-----------------------------------|
| 수 GB 이하, 단순 구성          | mysqldump                         |
| 수십~수백 GB, 논리 백업이 필요 | MySQL Shell `util.dumpInstance()` |
| 대용량, 복구 시간(RTO) 우선    | XtraBackup + binlog               |
| 특정 시점으로 되돌리기         | 전체 백업 + binlog 재생 (6절)     |

[⬆ 목차로 돌아가기](#목차)

---

## 2. mysqldump 기본

### 백업 계정 권한

공식 문서 기준으로 mysqldump는 덤프 대상 테이블의 `SELECT`, 뷰의 `SHOW VIEW`, 트리거의 `TRIGGER` 권한이 필요합니다. `--single-transaction`을 쓰지 않으면 `LOCK TABLES`, `--no-tablespaces`를 쓰지 않으면 `PROCESS`가 필요하고, `--source-data`는 `RELOAD`를 요구합니다.

```sql
CREATE USER 'backup'@'localhost' IDENTIFIED BY '<PASSWORD>';
GRANT SELECT, SHOW VIEW, TRIGGER, EVENT, PROCESS, RELOAD,
      REPLICATION CLIENT, LOCK TABLES ON *.* TO 'backup'@'localhost';
```

`EVENT`는 `--events`, `REPLICATION CLIENT`는 binlog 좌표 조회용입니다. 필요 없는 권한은 빼고 운영 환경에 맞게 줄입니다.

### 비밀번호를 명령줄에 쓰지 않기

`-p<비밀번호>`는 프로세스 목록과 셸 기록에 남습니다. 옵션 파일이나 `mysql_config_editor`를 씁니다.

```ini
# /root/.my.backup.cnf  (chmod 600)
[client]
user=backup
password=<PASSWORD>
```

```bash
mysqldump --defaults-extra-file=/root/.my.backup.cnf ...
```

`--defaults-extra-file`은 다른 옵션보다 먼저, 첫 번째 인자로 써야 합니다.

### 자주 쓰는 명령

```bash
# InnoDB DB 하나, 루틴·이벤트 포함
mysqldump --defaults-extra-file=/root/.my.backup.cnf \
  --single-transaction --routines --events --triggers \
  --hex-blob --databases appdb > appdb_$(date +%Y%m%d).sql

# 전체 DB + 복제 좌표(주석) + 압축
mysqldump --defaults-extra-file=/root/.my.backup.cnf \
  --single-transaction --routines --events \
  --source-data=2 --all-databases | gzip > all_$(date +%Y%m%d).sql.gz

# 스키마만 / 데이터만
mysqldump --no-data --routines --events --databases appdb > appdb_schema.sql
mysqldump --no-create-info --single-transaction appdb orders > orders_data.sql

# 특정 테이블 제외
mysqldump --single-transaction --ignore-table=appdb.audit_log appdb > appdb.sql
```

| 옵션                      | 의미                                                      |
|---------------------------|-----------------------------------------------------------|
| `--single-transaction`    | InnoDB 일관 스냅샷으로 잠금 없이 덤프                     |
| `--routines` / `--events` | 저장 프로시저·함수 / 이벤트 포함 (기본은 제외)            |
| `--triggers`              | 트리거 포함 (`--skip-triggers`로 끔)                      |
| `--databases db1 db2`     | `CREATE DATABASE`, `USE` 문 포함                          |
| `--all-databases`         | 모든 DB (`mysql` 시스템 스키마 포함)                      |
| `--hex-blob`              | BLOB·BINARY 값을 16진 리터럴로 기록                       |
| `--quick`                 | 행을 하나씩 가져와 메모리 사용 억제 (`--opt`로 기본 켜짐) |
| `--source-data=1/2`       | binlog 좌표를 실행문(1) / 주석(2)으로 기록                |
| `--set-gtid-purged=...`   | AUTO(기본), ON, OFF, COMMENTED                            |
| `--flush-logs`            | 덤프 시작 전 로그 플러시 (새 binlog 파일 시작)            |
| `--ignore-table=db.tbl`   | 테이블 제외 (반복 지정)                                   |

`--source-data`는 deprecated된 `--master-data`를 대체하는 옵션입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 일관성과 복제 좌표

### --single-transaction

덤프 시작 때 일관 스냅샷 트랜잭션을 열고, 그 시점 기준으로 InnoDB 테이블을 읽습니다. 다른 세션의 DML은 막지 않습니다.

- 일관성은 **트랜잭션 엔진(InnoDB) 테이블에만** 보장됩니다. MyISAM 테이블이 섞여 있으면 그 테이블은 덤프 중 바뀔 수 있습니다.
- 덤프 중 `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE`, `RENAME TABLE`, `TRUNCATE TABLE` 같은 DDL이 같은 테이블에 실행되면 덤프가 실패하거나 일관성이 깨질 수 있습니다. 백업 시간대에는 스키마 변경을 피합니다.
- 긴 덤프는 오래 열린 트랜잭션이 되어 undo 로그(history list)가 커집니다. 업무 부하가 적은 시간에 실행합니다.

### 복제 좌표와 GTID

덤프로 복제 Replica를 만들거나 binlog PITR의 시작점을 알려면 덤프 시점의 binlog 위치가 필요합니다.

```bash
mysqldump --single-transaction --source-data=2 --all-databases > full.sql
head -n 50 full.sql | grep -E 'CHANGE REPLICATION SOURCE|GTID_PURGED'
```

```text
-- CHANGE REPLICATION SOURCE TO SOURCE_LOG_FILE='binlog.000123', SOURCE_LOG_POS=4567;
```

| `--set-gtid-purged` | 동작                                               | 쓰임                           |
|---------------------|----------------------------------------------------|--------------------------------|
| AUTO (기본)         | GTID가 켜져 있으면 `SET @@GLOBAL.gtid_purged` 기록 | 일반                           |
| ON                  | 항상 기록, GTID가 꺼져 있으면 오류                 | GTID Replica 구축              |
| OFF                 | 기록하지 않음                                      | 다른 독립 서버로 데이터만 이관 |
| COMMENTED           | 주석으로 기록                                      | 좌표만 참고                    |

🟡 주의: `gtid_purged`가 들어 있는 덤프를 이미 GTID 기록이 있는 서버에 넣으면 오류가 날 수 있습니다. 복원 대상이 새 서버인지 기존 서버인지에 따라 값을 고릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. MySQL Shell dump 유틸리티

MySQL Shell(`mysqlsh`)의 dump 유틸리티는 여러 스레드로 테이블을 청크 단위로 나눠 내보내고, `util.loadDump()`로 병렬 적재합니다.

| 함수                                                    | 범위                                  |
|---------------------------------------------------------|---------------------------------------|
| `util.dumpInstance(outputUrl[, options])`               | 인스턴스 전체 (사용자·권한 기본 포함) |
| `util.dumpSchemas(schemas, outputUrl[, options])`       | 지정 스키마 (사용자 미포함)           |
| `util.dumpTables(schema, tables, outputUrl[, options])` | 지정 테이블 (사용자 미포함)           |
| `util.loadDump(url[, options])`                         | 위 덤프 적재                          |

### 주요 옵션 기본값

| 옵션          | 기본값         | 의미                                     |
|---------------|----------------|------------------------------------------|
| `threads`     | 4              | 병렬 스레드 수 (스레드마다 연결 1개)     |
| `consistent`  | true           | 백업 잠금으로 일관된 덤프                |
| `compression` | zstd (level 1) | 압축 방식                                |
| `users`       | true           | 사용자·롤·권한 포함 (`dumpInstance`만)   |
| `dryRun`      | false          | 실제 덤프 없이 대상과 호환성 문제만 출력 |

```bash
# 대상 디렉토리는 비어 있어야 합니다
mysqlsh backup@localhost:3306 -- util dump-instance /backup/inst_20261116 --threads=8
```

```javascript
// mysqlsh JS 모드
util.dumpInstance("/backup/inst_20261116", {threads: 8, dryRun: true})
util.dumpInstance("/backup/inst_20261116", {threads: 8})
util.dumpSchemas(["appdb"], "/backup/appdb_20261116")
```

### 적재

`util.loadDump()`는 내부적으로 `LOAD DATA LOCAL INFILE`을 쓰므로 대상 서버에 `local_infile = ON`이 필요합니다. 꺼져 있으면 오류 53025로 실패합니다.

```sql
SET GLOBAL local_infile = ON;   -- 적재 동안만
```

```javascript
util.loadDump("/backup/appdb_20261116", {dryRun: true})
util.loadDump("/backup/appdb_20261116", {threads: 8})
// 사용자·권한까지 적재하려면 (기본 false)
util.loadDump("/backup/inst_20261116", {loadUsers: true})
```

- 적재 진행 상태는 덤프 디렉토리의 `load-progress-<server-uuid>.json`에 기록되어, 중단 후 다시 실행하면 이어서 진행합니다.
- 처음부터 다시 하려면 `resetProgress: true`를 주되, 이미 적재된 객체를 먼저 지워야 합니다.
- 적재가 끝나면 `local_infile`을 원래 값으로 되돌립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 복원

```bash
# mysqldump 파일 복원
mysql --defaults-extra-file=/root/.my.admin.cnf < appdb_20261116.sql

# 압축 파일
gunzip -c all_20261116.sql.gz | mysql --defaults-extra-file=/root/.my.admin.cnf

# 다른 이름의 DB로 복원 (--databases 없이 받은 덤프만 가능)
mysql -e "CREATE DATABASE appdb_restore"
mysql appdb_restore < orders_data.sql
```

🟡 주의: `--databases`나 `--all-databases`로 받은 덤프에는 `USE appdb` 문이 있어 원래 이름의 DB에 씁니다. `--add-drop-database`나 `--add-drop-table`이 들어간 덤프는 기존 객체를 DROP합니다. 운영 서버에 적용하기 전에 파일 머리 부분을 확인하거나 별도 서버에 먼저 복원합니다.

### 복원 속도 높이기

| 방법                                      | 효과·주의                                          |
|-------------------------------------------|----------------------------------------------------|
| 복원 세션에서 `SET SESSION sql_log_bin=0` | binlog 기록 생략. Replica에 전파되지 않으므로 주의 |
| 대형 테이블은 MySQL Shell로 병렬 적재     | 스레드 수만큼 병렬                                 |
| `innodb_buffer_pool_size` 여유 확보       | 인덱스 생성 단계 단축                              |
| 복원 서버를 운영 서버와 분리              | 운영 부하 영향 없음                                |

[⬆ 목차로 돌아가기](#목차)

---

## 6. binlog 시점 복구

전체 백업 시점부터 사고 직전까지의 binlog를 재생해 원하는 시점으로 되돌립니다. MySQL 8.4는 binlog가 기본으로 켜져 있습니다.

```text
 full backup (binlog.000123:4567)            DROP TABLE (binlog.000125 # at 232)
     |------------------------------------------------|---->
     restore dump  -> replay 000123:4567 ... 000125:232 (stop before)
```

### 1단계: 백업 복원과 시작 위치 확인

전체 백업을 복원하고, 백업에 기록된 binlog 좌표(3절)를 시작 위치로 씁니다. 공식 문서는 InnoDB가 재시작 후 보여 주는 위치는 믿을 수 없으니 백업·복원 도구가 남긴 위치를 쓰라고 안내합니다.

### 2단계: 사고 이벤트 위치 찾기

```sql
SHOW BINARY LOGS;
SHOW BINARY LOG STATUS;
```

```bash
mysqlbinlog --start-datetime="2026-11-16 14:25:00" --stop-datetime="2026-11-16 14:35:00" \
  --base64-output=DECODE-ROWS --verbose /var/lib/mysql/binlog.000125 | grep -n -C 10 "DROP TABLE"
```

출력의 `# at 232` 다음에 `DROP TABLE`이 있고 그 뒤가 `# at 355`라면, 사고 이벤트는 232에서 시작합니다.

공식 문서는 `--start-datetime`/`--stop-datetime`을 **위치를 찾는 용도로만** 쓰고, 실제 재생 범위는 `--start-position`/`--stop-position`으로 지정하라고 권합니다. 시각 기준은 같은 초에 여러 이벤트가 있을 때 빠뜨릴 위험이 있습니다.

`--base64-output=DECODE-ROWS`는 확인용입니다. 재생할 때는 기본값(AUTO)으로 둡니다.

### 3단계: 재생

```bash
# 시작 파일은 백업 위치부터, 마지막 파일은 사고 직전 위치까지
mysqlbinlog --start-position=4567 /var/lib/mysql/binlog.000123 > replay.sql
mysqlbinlog /var/lib/mysql/binlog.000124 >> replay.sql
mysqlbinlog --stop-position=232 /var/lib/mysql/binlog.000125 >> replay.sql

# 내용 확인 후 적용
less replay.sql
mysql --defaults-extra-file=/root/.my.admin.cnf < replay.sql
```

여러 파일을 각각 따로 `mysql`에 넘기면 파일 경계의 임시 테이블 등이 끊길 수 있어, 공식 문서는 한 연결에서 처리하도록 파일을 이어 붙이거나 한 번에 넘기는 방법을 보여 줍니다. 로그에 `\0` 문자가 있으면 `mysql --binary-mode`를 씁니다.

### 4단계(선택): 사고 이후 정상 변경 재적용

```bash
mysqlbinlog --start-position=355 /var/lib/mysql/binlog.000125 | mysql --defaults-extra-file=/root/.my.admin.cnf
```

### GTID 환경

- 같은 서버에 이미 실행된 GTID는 다시 적용되지 않고 건너뜁니다. 별도 복구 서버에 복원하면 이 문제를 피하기 쉽습니다.
- `--exclude-gtids=<gtid_set>`으로 사고 트랜잭션 하나만 빼고 재생할 수 있습니다.
- `--skip-gtids`는 GTID를 빼고 새 트랜잭션처럼 적용하는 옵션인데, 공식 문서는 운영·복구에서는 보통 쓰지 말라고 경고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. binlog 보관

PITR 가능 범위는 "가장 오래된 전체 백업"부터 "남아 있는 마지막 binlog"까지입니다.

```sql
-- 보관 기간 (초). 8.4 기본값은 2592000초(30일)
SHOW VARIABLES LIKE 'binlog_expire_logs_seconds';
SHOW VARIABLES LIKE 'log_bin%';
```

🟡 주의: `PURGE BINARY LOGS`는 되돌릴 수 없습니다. Replica가 아직 읽지 않은 binlog를 지우면 복제가 끊기므로, 각 Replica의 위치를 확인한 뒤 실행합니다.

### 원격 실시간 보관

`mysqlbinlog --read-from-remote-server --raw --stop-never`로 다른 서버에 binlog를 원본 형식 그대로 계속 받아 둘 수 있습니다. DB 서버 디스크가 손상돼도 binlog가 남습니다. 접속 계정에는 `REPLICATION SLAVE` 권한이 필요합니다.

```bash
mysqlbinlog --read-from-remote-server --host=192.0.2.10 --user=binlog_backup -p \
  --raw --stop-never --result-file=/backup/binlog/ binlog.000123
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 점검표

| 점검 항목                                                   | 확인 |
|-------------------------------------------------------------|------|
| 백업 스크립트에 `mysqlpump`가 남아 있지 않다 (8.4에서 제거) | [ ]  |
| 비밀번호를 명령줄 대신 권한 600 옵션 파일로 넘긴다          | [ ]  |
| `--single-transaction`과 `--routines --events`를 함께 쓴다  | [ ]  |
| 덤프에 binlog 좌표나 GTID 정보가 기록된다                   | [ ]  |
| binlog 보관 기간이 전체 백업 주기보다 길다                  | [ ]  |
| binlog를 DB 서버 밖에도 보관한다                            | [ ]  |
| 별도 서버에서 복원과 binlog 재생을 정기적으로 연습한다      | [ ]  |
| MyISAM 테이블이 있다면 일관성 보장 범위를 알고 있다         | [ ]  |
| 백업 시간대에 DDL 작업이 겹치지 않는다                      | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [percona_xtrabackup_guide.md](./percona_xtrabackup_guide.md) — 물리 백업
- [mysql_install.md](./mysql_install.md) — 설치와 기본 사용법
- [rdbms_replication.md](./rdbms_replication.md) — binlog, GTID 복제
- MySQL 8.4 mysqldump: [dev.mysql.com/doc/refman/8.4/en/mysqldump.html](https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html) — ★★★☆☆ (확인일 2026-11-16)
- MySQL 8.4 Point-in-Time Recovery Using Event Positions: [dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery-positions.html](https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery-positions.html) — ★★★☆☆ (확인일 2026-11-16)
- MySQL 8.4 mysqlbinlog: [dev.mysql.com/doc/refman/8.4/en/mysqlbinlog.html](https://dev.mysql.com/doc/refman/8.4/en/mysqlbinlog.html) — ★★★☆☆ (확인일 2026-11-16)
- MySQL 8.4 Binary Logging Options (binlog_expire_logs_seconds): [dev.mysql.com/doc/refman/8.4/en/replication-options-binary-log.html](https://dev.mysql.com/doc/refman/8.4/en/replication-options-binary-log.html) — ★★★☆☆ (확인일 2026-11-16)
- MySQL 8.4.0 Release Notes (mysqlpump 제거): [dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html](https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html) — ★★★☆☆ (확인일 2026-11-16)
- MySQL Shell Instance/Schema/Table Dump Utilities: [dev.mysql.com/doc/mysql-shell/8.4/en/mysql-shell-utilities-dump-instance-schema.html](https://dev.mysql.com/doc/mysql-shell/8.4/en/mysql-shell-utilities-dump-instance-schema.html) — ★★★☆☆ (확인일 2026-11-16)
- MySQL Shell Dump Loading Utility: [dev.mysql.com/doc/mysql-shell/8.4/en/mysql-shell-utilities-load-dump.html](https://dev.mysql.com/doc/mysql-shell/8.4/en/mysql-shell-utilities-load-dump.html) — ★★★☆☆ (확인일 2026-11-16)
- mydumper: [github.com/mydumper/mydumper](https://github.com/mydumper/mydumper) — ★★★☆☆ (확인일 2026-11-16)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
