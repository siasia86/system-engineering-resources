# PostgreSQL 백업과 PITR
<!-- reference: _reference/postgresql_official_notes.md -->

PostgreSQL의 논리 백업(pg_dump), 물리 백업(pg_basebackup), WAL 아카이빙을 이용한 시점 복구(PITR)를 다룹니다. 설치 문서의 `pg_dump` 기본 사용법을 넘어, 백업 방식 선택 기준과 복구 절차·점검표를 정리합니다. 기준 판은 PostgreSQL 18 문서(18.7, 2026-11-16 확인)입니다.

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 백업 방식 비교](#1-백업-방식-비교) / [2. pg_dump와 pg_restore](#2-pg_dump와-pg_restore)                |
| [3. pg_dumpall과 전역 객체](#3-pg_dumpall과-전역-객체) / [4. WAL 아카이빙 설정](#4-wal-아카이빙-설정)      |
| [5. pg_basebackup](#5-pg_basebackup) / [6. PITR 복구 절차](#6-pitr-복구-절차) / [7. 타임라인](#7-타임라인) |
| [8. 백업 검증과 점검표](#8-백업-검증과-점검표)                                                             |

---

## 1. 백업 방식 비교

PostgreSQL 백업은 크게 세 가지입니다.

- **논리 백업(logical backup)**: SQL 문이나 아카이브 파일로 객체 정의와 데이터를 꺼냅니다. `pg_dump`, `pg_dumpall`이 해당합니다.
- **물리 백업(physical backup)**: 데이터 디렉토리 파일 자체를 복사합니다. `pg_basebackup`이나 저수준 API(`pg_backup_start`/`pg_backup_stop`)를 씁니다.
- **연속 아카이빙(continuous archiving)**: 물리 백업에 WAL(Write-Ahead Log, 변경 기록 로그) 파일을 계속 보관해 두고, 원하는 시점까지 재생합니다. 이것이 PITR(Point-In-Time Recovery, 시점 복구)입니다.

| 항목             | pg_dump                     | pg_basebackup 단독   | pg_basebackup + WAL 아카이브 |
|------------------|-----------------------------|----------------------|------------------------------|
| 단위             | 데이터베이스 1개            | 클러스터 전체        | 클러스터 전체                |
| 복구 시점        | 덤프 시작 시점              | 백업 종료 시점       | 아카이브 범위 안의 임의 시점 |
| 다른 메이저 버전 | 복원 가능 (업그레이드 용도) | 불가 (같은 메이저만) | 불가 (같은 메이저만)         |
| 일부 테이블 복원 | 가능                        | 불가                 | 불가                         |
| 대용량 복원 속도 | 느림 (인덱스 재생성)        | 빠름 (파일 복사)     | 빠름 + WAL 재생 시간         |
| 설정 파일 포함   | 아니오                      | 데이터 디렉토리 안만 | 데이터 디렉토리 안만         |

### 선택 기준

| 상황                                    | 권장                                    |
|-----------------------------------------|-----------------------------------------|
| 수십 GB 이하, 하루 1회 백업으로 충분    | pg_dump (custom 또는 directory 형식)    |
| 메이저 버전 업그레이드·다른 서버로 이관 | pg_dump / pg_restore                    |
| 수백 GB 이상, 복구 시간(RTO)이 중요     | pg_basebackup                           |
| 데이터 손실 허용치(RPO)가 수 분 이하    | pg_basebackup + WAL 아카이빙 (PITR)     |
| 실수로 지운 테이블 하나만 되살리기      | pg_dump 백업 또는 PITR로 별도 서버 복원 |

🟡 주의: 복제(standby)는 백업이 아닙니다. 주 서버에서 실행한 `DROP TABLE`은 standby에도 그대로 반영됩니다. 복제와 별개로 백업을 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. pg_dump와 pg_restore

`pg_dump`는 데이터베이스 하나를 일관된 스냅샷으로 꺼냅니다. 덤프 중에도 다른 세션의 읽기·쓰기를 막지 않습니다.

### 출력 형식

| 형식      | 옵션  | 복원 도구  | 병렬 덤프 `-j` | 병렬 복원 | 기본 압축  |
|-----------|-------|------------|----------------|-----------|------------|
| plain     | `-Fp` | psql       | 아니오         | 아니오    | 없음       |
| custom    | `-Fc` | pg_restore | 아니오         | 예        | 있음       |
| directory | `-Fd` | pg_restore | 예 (유일)      | 예        | 있음       |
| tar       | `-Ft` | pg_restore | 아니오         | 아니오    | 지원 안 함 |

운영 백업은 custom이나 directory 형식을 권장합니다. 복원할 때 객체를 골라낼 수 있고 병렬 복원이 됩니다.

### 기본 명령

```bash
# custom 형식 (단일 파일, 압축)
pg_dump -h 127.0.0.1 -U postgres -Fc -f /backup/appdb_$(date +%Y%m%d).dump appdb

# directory 형식 + 병렬 4개 (연결은 jobs + 1개 사용)
pg_dump -h 127.0.0.1 -U postgres -Fd -j 4 -f /backup/appdb_$(date +%Y%m%d) appdb

# zstd 압축 지정
pg_dump -U postgres -Fd -j 4 -Z zstd:3 -f /backup/appdb_zstd appdb

# 스키마만 / 데이터만
pg_dump -U postgres -s -f appdb_schema.sql appdb
pg_dump -U postgres -a -Fc -f appdb_data.dump appdb

# 특정 테이블 제외, 특정 테이블은 정의만
pg_dump -U postgres -Fc -T 'audit_log*' --exclude-table-data='tmp_*' -f appdb.dump appdb
```

자주 쓰는 옵션은 다음과 같습니다.

| 옵션                      | 의미                                                    |
|---------------------------|---------------------------------------------------------|
| `-n schema` / `-N schema` | 스키마 포함 / 제외                                      |
| `-t table` / `-T table`   | 테이블 포함 / 제외 (패턴 사용 가능, 반복 지정 가능)     |
| `--exclude-table-data`    | 테이블 정의는 남기고 데이터만 제외                      |
| `--section=pre-data`      | pre-data, data, post-data 구간 중 일부만                |
| `-Z method[:level]`       | 압축 방식 gzip, lz4, zstd, none                         |
| `--statistics`            | 옵티마이저 통계도 덤프 (PG18, 기본은 `--no-statistics`) |

### pg_restore

```bash
# 대상 DB를 먼저 만들고 복원
createdb -U postgres -O app appdb_restore
pg_restore -U postgres -d appdb_restore -j 4 /backup/appdb_20261116.dump

# 아카이브 목록 확인 후 일부만 복원
pg_restore -l appdb.dump > toc.list
# toc.list에서 필요 없는 줄 앞에 ; 를 붙여 주석 처리
pg_restore -U postgres -d appdb_restore -L toc.list appdb.dump

# 테이블 하나만 복원
pg_restore -U postgres -d appdb_restore -t orders appdb.dump

# 덤프를 SQL로 풀어 내용 확인 (DB에 적용하지 않음)
pg_restore -f - appdb.dump | less
```

🟡 주의: `pg_restore --clean`은 복원 전에 대상 객체를 DROP합니다. 운영 DB 이름을 `-d`에 잘못 넣으면 데이터가 지워지므로, 먼저 새 DB에 복원해 확인합니다.

### 주의할 점

- `pg_dump`는 롤(role)과 테이블스페이스를 덤프하지 않습니다. 3절의 `pg_dumpall --globals-only`를 함께 받습니다.
- 병렬 덤프는 `max_connections`에 `-j` 값 + 1만큼 여유가 있어야 합니다.
- 덤프 도중 다른 세션이 배타 잠금(예: `ALTER TABLE`)을 요청하면 병렬 덤프가 실패할 수 있습니다.
- 새 판의 `pg_dump`로 옛 판 서버를 덤프할 수 있지만, 옛 판 `pg_dump`로 새 메이저 판 서버는 덤프할 수 없습니다. 업그레이드 이관에는 대상 판의 `pg_dump`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. pg_dumpall과 전역 객체

전역 객체(global object)는 특정 DB에 속하지 않는 롤, 롤 권한, 테이블스페이스 정의입니다.

```bash
# 전역 객체만 (롤 + 테이블스페이스)
pg_dumpall -U postgres --globals-only -f /backup/globals_$(date +%Y%m%d).sql

# 롤만
pg_dumpall -U postgres --roles-only -f /backup/roles.sql

# 클러스터 전체를 plain SQL로 (소규모 클러스터용)
pg_dumpall -U postgres -f /backup/all_$(date +%Y%m%d).sql
```

권장 조합은 "DB별 `pg_dump -Fc` + `pg_dumpall --globals-only`"입니다. `pg_dumpall` 전체 덤프는 plain SQL만 나오므로 병렬 복원과 선택 복원이 어렵습니다.

```bash
#!/usr/bin/env bash
# DB별 덤프 예시 (template0/1 제외)
set -euo pipefail
OUT=/backup/$(date +%Y%m%d)
mkdir -p "$OUT"
pg_dumpall -U postgres --globals-only -f "$OUT/globals.sql"
for db in $(psql -U postgres -Atc "SELECT datname FROM pg_database WHERE datallowconn AND datname <> 'template1'"); do
  pg_dump -U postgres -Fc -f "$OUT/${db}.dump" "$db"
done
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. WAL 아카이빙 설정

PITR을 하려면 기준이 되는 물리 백업과, 그 백업 시작 이후의 WAL 파일이 끊김 없이 있어야 합니다.

### postgresql.conf

```ini
wal_level = replica          # replica 이상 (재시작 필요)
archive_mode = on            # 재시작 필요
archive_command = 'test ! -f /mnt/wal_archive/%f && cp %p /mnt/wal_archive/%f'
archive_timeout = 300        # 초. 트래픽이 적어도 5분마다 세그먼트 전환
```

| 자리 표시자 | 의미                                        |
|-------------|---------------------------------------------|
| `%p`        | 보관할 WAL 파일 경로 (데이터 디렉토리 기준) |
| `%f`        | WAL 파일 이름만                             |
| `%%`        | 문자 `%`                                    |

### archive_command 작성 규칙

- **성공했을 때만 종료 코드 0**을 반환해야 합니다. 0이 아니면 PostgreSQL은 같은 파일을 다시 시도하고, 그 동안 `pg_wal/`에 WAL이 쌓입니다.
- 이미 있는 파일을 덮어쓰지 않도록 `test ! -f`로 막습니다. GNU `cp -i`는 대상이 있어도 0을 반환하므로 대신 쓸 수 없습니다.
- `archive_command`와 `archive_library`는 reload로 바꿀 수 있습니다. 잠시 멈추려면 `archive_command = ''`로 둡니다(WAL은 `pg_wal/`에 쌓입니다).
- 원격 저장소(S3 등)로 보낼 때는 pgBackRest, WAL-G, Barman 같은 전용 도구의 명령을 `archive_command`에 넣는 방식을 많이 씁니다. 이 도구들의 옵션은 각 공식 문서를 따릅니다.

🟡 주의: `pg_wal/`이 있는 파일시스템이 가득 차면 PostgreSQL은 PANIC으로 종료합니다. 아카이브 실패가 이어지면 디스크가 차므로 반드시 감시합니다.

### 아카이브 상태 확인

```sql
-- 마지막 성공·실패 시각과 누적 실패 수
SELECT archived_count, last_archived_wal, last_archived_time,
       failed_count, last_failed_wal, last_failed_time
FROM pg_stat_archiver;

-- 세그먼트를 강제로 전환해 아카이빙 동작 확인
SELECT pg_switch_wal();
```

`failed_count`가 늘고 `last_failed_time`이 `last_archived_time`보다 최근이면 아카이빙이 막힌 상태입니다. 서버 로그의 `archive command failed` 메시지로 원인을 찾습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. pg_basebackup

`pg_basebackup`은 복제 프로토콜로 실행 중인 클러스터 전체를 복사합니다. 접속 사용자는 `REPLICATION` 권한이나 superuser여야 하고, `pg_hba.conf`에 replication 연결 허용 줄이 있어야 합니다.

```text
# pg_hba.conf
host  replication  backup_user  192.0.2.10/32  scram-sha-256
```

```sql
CREATE ROLE backup_user WITH LOGIN REPLICATION PASSWORD '<PASSWORD>';
```

### 주요 옵션

| 옵션                       | 의미                                                |
|----------------------------|-----------------------------------------------------|
| `-D dir`                   | 대상 디렉토리 (비어 있어야 함)                      |
| `-F p` / `-F t`            | plain(기본) / tar                                   |
| `-X stream`                | 백업 중 WAL을 함께 스트리밍 (기본값)                |
| `-z`, `-Z method[:level]`  | 압축 (tar 형식에서 주로 사용)                       |
| `-c fast`                  | 즉시 체크포인트 (기본 spread는 시작이 느릴 수 있음) |
| `-P`                       | 진행률 표시                                         |
| `-R`                       | standby.signal과 접속 설정 생성 (standby 구축용)    |
| `-C -S slot`               | 복제 슬롯을 만들고 사용                             |
| `-i manifest`              | 증분 백업 (서버 17 이상)                            |
| `--manifest-checksums=alg` | 매니페스트 체크섬 (기본 CRC32C)                     |

### 예시

```bash
# tar + gzip 압축, WAL 포함, 진행률 표시
pg_basebackup -h 192.0.2.10 -U backup_user -D /backup/base_$(date +%Y%m%d) \
  -F t -z -X stream -c fast -P

# 백업 검증 (매니페스트 기준)
pg_verifybackup /backup/base_20261116
```

`-X stream`으로 받은 백업은 그 자체로 시작 가능한 독립 백업이지만, 그것만으로는 백업 종료 이후 시점으로 갈 수 없습니다. PITR에는 4절의 WAL 아카이브가 필요합니다.

### 증분 백업 (PG17 이상)

PG17부터 `--incremental`(`-i`)로 이전 백업의 `backup_manifest`를 기준으로 바뀐 블록만 받을 수 있습니다. 서버에서 WAL 요약(`summarize_wal = on`)이 켜져 있어야 하고, 복원할 때는 `pg_combinebackup`으로 전체 백업과 증분 백업들을 합칩니다.

```bash
pg_basebackup -U backup_user -D /backup/incr1 -i /backup/full/backup_manifest -X stream
pg_combinebackup -o /restore/data /backup/full /backup/incr1
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. PITR 복구 절차

예: 2026-11-16 14:30:00(+09:00)에 실수로 `DELETE`가 실행되어, 그 직전 시점으로 되돌립니다. 가능하면 운영 서버가 아닌 별도 서버에 복원해 데이터를 확인한 뒤 필요한 데이터만 옮깁니다.

```text
 base backup           WAL archive                         now
 (02:00)    ---------------------------------------------->|
    |=====>| 000000010000000A000000xx ... 14:29:59 | 14:30 DELETE
                                          ^
                                  recovery_target_time
```

### 단계

1. 서버를 멈춥니다. `systemctl stop postgresql`
2. 공간이 있으면 현재 데이터 디렉토리와 `pg_wal/`을 다른 곳에 보존합니다(아직 아카이브되지 않은 WAL이 있을 수 있음).
3. 데이터 디렉토리를 비우고 기준 백업을 풉니다. 소유자는 `postgres`(root 아님), 권한은 0700입니다.
4. 백업에 들어 있던 `pg_wal/` 안 파일을 지우고, 2단계에서 보존한 미아카이브 WAL이 있으면 복사합니다.
5. 복구 설정을 넣고 빈 `recovery.signal` 파일을 만듭니다.
6. 서버를 시작합니다. WAL 재생이 끝나면 지정한 동작을 합니다.
7. 데이터를 확인합니다. 틀렸으면 1단계부터 다시 합니다.

```bash
# 3단계 예시 (tar 백업)
sudo -u postgres tar -xzf /backup/base_20261116/base.tar.gz -C /var/lib/postgresql/18/main
sudo -u postgres rm -rf /var/lib/postgresql/18/main/pg_wal/*
# 5단계
sudo -u postgres touch /var/lib/postgresql/18/main/recovery.signal
```

🟡 주의: 3단계에서 데이터 디렉토리를 비우는 명령은 되돌릴 수 없습니다. 경로를 두 번 확인하고 2단계 보존을 먼저 끝냅니다.

### 복구 설정 (postgresql.conf 또는 postgresql.auto.conf)

```ini
restore_command = 'cp /mnt/wal_archive/%f %p'
recovery_target_time = '2026-11-16 14:29:59+09'
recovery_target_inclusive = off
recovery_target_action = 'pause'
```

| 파라미터                    | 기본값 | 의미                                                      |
|-----------------------------|--------|-----------------------------------------------------------|
| `restore_command`           | 없음   | 아카이브에서 WAL을 가져오는 명령 (없는 파일은 0 아닌 값)  |
| `recovery_target_time`      | 미설정 | 이 시각까지 재생. 시간대는 숫자 오프셋이나 전체 이름 권장 |
| `recovery_target_xid`       | 미설정 | 이 트랜잭션 ID까지                                        |
| `recovery_target_lsn`       | 미설정 | 이 WAL 위치(LSN)까지                                      |
| `recovery_target_name`      | 미설정 | `pg_create_restore_point()`로 만든 이름까지               |
| `recovery_target`           | 미설정 | `'immediate'`: 일관성 도달 즉시 종료                      |
| `recovery_target_inclusive` | on     | on은 대상 직후, off는 대상 직전에서 멈춤                  |
| `recovery_target_timeline`  | latest | latest, current, 또는 타임라인 ID                         |
| `recovery_target_action`    | pause  | pause, promote, shutdown                                  |

- 대상 파라미터(`recovery_target*` 중 시점 지정용 5개)는 하나만 지정합니다. 둘 이상이면 오류입니다.
- 대상 시점은 기준 백업의 **종료 시각 이후**여야 합니다.
- 대상에 닿기 전에 WAL이 끝나면 서버는 FATAL 오류로 멈춥니다. 아카이브가 빠졌는지 확인합니다.

### pause 상태에서 확인 후 진행

`recovery_target_action = 'pause'`로 두면 대상 시점에서 읽기 전용으로 멈춥니다. 데이터를 조회해 맞으면 승격합니다.

```sql
SELECT pg_is_in_recovery();          -- t
SELECT count(*) FROM orders;         -- 데이터 확인
SELECT pg_promote();                 -- 맞으면 승격 (새 타임라인 시작)
-- 더 진행해야 하면 설정을 바꾸고 재시작
```

### 복원 지점 미리 만들기

배포·대량 변경 직전에 이름 있는 복원 지점을 만들어 두면 시각을 추정하지 않아도 됩니다.

```sql
SELECT pg_create_restore_point('before_release_20261116');
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 타임라인

PITR이나 승격으로 복구가 끝날 때마다 새 **타임라인(timeline)**이 생깁니다. 같은 WAL 위치라도 복구 전 역사와 복구 후 역사를 구분하기 위한 번호입니다.

- WAL 파일 이름 앞 8자리 16진수가 타임라인 ID입니다. 예: `00000002` + `0000000A` + `0000003F`.
- 새 타임라인마다 `00000002.history` 같은 이력 파일이 아카이브에 생깁니다. 작으므로 지우지 말고 계속 보관합니다.
- 기본값 `recovery_target_timeline = latest`는 아카이브에서 가장 최근 타임라인을 따라갑니다. 한 번 복구한 뒤 다시 다른 시점으로 복구할 때는 원하는 타임라인 ID를 지정합니다.
- 기준 백업보다 먼저 갈라진 타임라인으로는 복구할 수 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 백업 검증과 점검표

백업은 복원해 보기 전까지는 성공 여부를 알 수 없습니다.

### 정기 검증

| 주기    | 검증 내용                                                               |
|---------|-------------------------------------------------------------------------|
| 매일    | 백업 작업 종료 코드, 파일 크기 추이, `pg_stat_archiver` 실패 수         |
| 매일    | `pg_verifybackup`으로 물리 백업 매니페스트 검사                         |
| 매주    | `pg_restore -l`로 덤프 목차 읽기, 별도 서버에 덤프 복원 후 행 수 비교   |
| 매월    | 별도 서버에서 PITR 연습 (대상 시각 지정 → 데이터 확인 → 소요 시간 기록) |
| 변경 시 | 테이블스페이스 생성·삭제 후 새 기준 백업 받기                           |

### 점검표

| 점검 항목                                                         | 확인 |
|-------------------------------------------------------------------|------|
| 백업이 DB 서버와 다른 장비·다른 위치에도 있다                     | [ ]  |
| `pg_dumpall --globals-only`를 DB 덤프와 함께 받는다               | [ ]  |
| `postgresql.conf`, `pg_hba.conf`, `pg_ident.conf`를 따로 보관한다 | [ ]  |
| `archive_command`가 실패 시 0이 아닌 값을 반환한다                | [ ]  |
| `pg_stat_archiver.failed_count` 증가를 알림으로 감시한다          | [ ]  |
| WAL 아카이브 보관 기간이 가장 오래된 기준 백업보다 길다           | [ ]  |
| 복구 연습 결과(RTO)를 기록하고 목표와 비교한다                    | [ ]  |
| 백업 파일 접근 권한을 DB 계정·백업 계정으로 제한한다              | [ ]  |

### 흔한 실수

| 실수                                   | 결과                              |
|----------------------------------------|-----------------------------------|
| WAL 아카이브만 남기고 기준 백업을 지움 | 남은 WAL로 복구 불가              |
| 기준 백업보다 오래된 WAL만 남기고 정리 | 백업 이후 재생 불가               |
| `pg_dump`만 받고 롤을 안 받음          | 복원 시 소유자·권한 오류          |
| 설정 파일을 백업하지 않음              | 복원 후 접속 제어·튜닝 값 재작성  |
| 복원을 한 번도 시험하지 않음           | 장애 때 처음 시도, 절차 오류 발견 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [postgresql_install.md](./postgresql_install.md) — 설치와 기본 사용법
- [rdbms_replication.md](./rdbms_replication.md) — Streaming Replication
- [postgresql_vacuum.md](./postgresql_vacuum.md) — VACUUM과 autovacuum
- PostgreSQL Continuous Archiving and PITR: [postgresql.org/docs/current/continuous-archiving.html](https://www.postgresql.org/docs/current/continuous-archiving.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL pg_dump: [postgresql.org/docs/current/app-pgdump.html](https://www.postgresql.org/docs/current/app-pgdump.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL pg_basebackup: [postgresql.org/docs/current/app-pgbasebackup.html](https://www.postgresql.org/docs/current/app-pgbasebackup.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL Recovery Target 설정: [postgresql.org/docs/current/runtime-config-wal.html](https://www.postgresql.org/docs/current/runtime-config-wal.html) — ★★★☆☆ (확인일 2026-11-16)

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
