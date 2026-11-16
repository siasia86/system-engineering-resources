# PostgreSQL VACUUM과 autovacuum 운영
<!-- reference: _reference/postgresql_official_notes.md -->

PostgreSQL의 MVCC 구조에서 생기는 죽은 튜플(dead tuple)과 테이블 비대(bloat), 트랜잭션 ID 랩어라운드(wraparound)를 관리하는 VACUUM과 autovacuum을 다룹니다. 기준 판은 PostgreSQL 18 문서(18.7, 2026-11-16 확인)입니다.

## 목차

| 섹션                                                                                                |
|-----------------------------------------------------------------------------------------------------|
| [1. 왜 VACUUM이 필요한가](#1-왜-vacuum이-필요한가) / [2. VACUUM 종류와 잠금](#2-vacuum-종류와-잠금) |
| [3. autovacuum 동작과 임계값](#3-autovacuum-동작과-임계값) / [4. 파라미터 튜닝](#4-파라미터-튜닝)   |
| [5. 트랜잭션 ID 랩어라운드](#5-트랜잭션-id-랩어라운드) / [6. 모니터링 쿼리](#6-모니터링-쿼리)       |
| [7. VACUUM이 진행되지 않는 원인](#7-vacuum이-진행되지-않는-원인) / [8. 운영 점검표](#8-운영-점검표) |

---

## 1. 왜 VACUUM이 필요한가

PostgreSQL은 MVCC(Multi-Version Concurrency Control, 다중 버전 동시성 제어)로 동작합니다. `UPDATE`는 기존 행을 고치지 않고 새 버전을 쓰며, 옛 버전은 "죽은 튜플"로 남습니다. `DELETE`도 행을 바로 지우지 않고 삭제 표시만 합니다.

```text
UPDATE orders SET status='paid' WHERE id=1;

 page:  [ v1 id=1 status=new  (dead after commit) ]
        [ v2 id=1 status=paid (live)              ]
```

공식 문서가 정리한 VACUUM의 목적은 네 가지입니다.

| 목적            | 설명                                                                  |
|-----------------|-----------------------------------------------------------------------|
| 공간 재사용     | 죽은 튜플이 차지한 공간을 다시 쓸 수 있게 표시                        |
| 통계 갱신       | `ANALYZE`로 플래너 통계 갱신 (VACUUM과 함께 또는 단독)                |
| 가시성 맵 갱신  | visibility map을 갱신해 index-only scan이 힙 접근을 줄이게 함         |
| 랩어라운드 방지 | 오래된 트랜잭션 ID를 동결(freeze)해 ID 순환으로 인한 데이터 손실 방지 |

VACUUM이 따라가지 못하면 다음이 생깁니다.

- 테이블·인덱스 크기가 실제 데이터보다 커지는 **bloat**(비대)
- 순차 스캔·인덱스 스캔이 죽은 튜플까지 읽어 느려짐
- 통계가 낡아 잘못된 실행 계획 선택
- 최악의 경우 랩어라운드 보호로 쓰기 트랜잭션 거부

[⬆ 목차로 돌아가기](#목차)

---

## 2. VACUUM 종류와 잠금

| 항목        | VACUUM                                   | VACUUM FULL                         |
|-------------|------------------------------------------|-------------------------------------|
| 동작        | 죽은 튜플 공간을 재사용 가능으로 표시    | 테이블을 새로 써서 압축             |
| OS로 반환   | 보통 반환하지 않음 (끝 페이지만 잘라냄)  | 반환                                |
| 잠금        | SHARE UPDATE EXCLUSIVE (DML과 동시 실행) | ACCESS EXCLUSIVE (조회까지 차단)    |
| 추가 디스크 | 거의 없음                                | 테이블 크기만큼 새 복사본 공간 필요 |
| 속도        | 빠름                                     | 느림                                |

```sql
VACUUM orders;                      -- 기본
VACUUM (VERBOSE, ANALYZE) orders;   -- 진행 내용 출력 + 통계 갱신
ANALYZE orders;                     -- 통계만
VACUUM (FREEZE) orders;             -- 적극적 동결
VACUUM (INDEX_CLEANUP OFF) orders;  -- 인덱스 정리 생략 (긴급 랩어라운드 대응용)
VACUUM (PARALLEL 4) orders;         -- 인덱스 정리 병렬화
```

🟡 주의: `VACUUM FULL`은 테이블 전체를 ACCESS EXCLUSIVE로 잠가 `SELECT`도 막습니다. 운영 중에는 쓰지 않고, 비대가 심하면 점검 시간에 실행하거나 `pg_repack` 같은 온라인 재구성 도구를 검토합니다(`pg_repack`은 PostgreSQL 본체가 아닌 확장 도구이므로 그 저장소 문서를 따릅니다).

[⬆ 목차로 돌아가기](#목차)

---

## 3. autovacuum 동작과 임계값

autovacuum은 VACUUM과 ANALYZE를 자동으로 실행하는 백그라운드 프로세스입니다.

```text
 autovacuum launcher
   |  every autovacuum_naptime / N(databases)
   v
 worker (max: autovacuum_max_workers)
   -> check pg_stat_* counters per table
   -> VACUUM / ANALYZE if threshold exceeded
```

- 런처(launcher)는 각 DB에 대략 `autovacuum_naptime`마다 워커를 하나씩 보냅니다. DB가 N개면 `naptime / N`초마다 새 워커가 시작됩니다.
- 워커 수는 `autovacuum_max_workers`로 제한하며, 워커는 `max_connections`에 포함되지 않습니다.
- 다른 세션이 충돌하는 잠금을 요청하면 일반 autovacuum은 스스로 중단합니다. 단, 랩어라운드 방지 실행은 중단되지 않으며 `pg_stat_activity`에 `(to prevent wraparound)`로 표시됩니다.
- 파티션 부모 테이블은 autovacuum이 ANALYZE하지 않으므로, 부모 수준 통계가 필요하면 수동 `ANALYZE`를 합니다. 임시 테이블도 처리하지 않습니다.

### 실행 임계값 공식

```text
vacuum threshold  = MIN(autovacuum_vacuum_max_threshold,
                        autovacuum_vacuum_threshold
                        + autovacuum_vacuum_scale_factor * reltuples)

insert threshold  = autovacuum_vacuum_insert_threshold
                    + autovacuum_vacuum_insert_scale_factor * reltuples * (1 - relallfrozen/relpages)

analyze threshold = autovacuum_analyze_threshold
                    + autovacuum_analyze_scale_factor * reltuples
```

죽은 튜플 수(또는 마지막 VACUUM 이후 삽입 수, 마지막 ANALYZE 이후 변경 수)가 각 임계값을 넘으면 실행합니다.

### 기본값 (PG18)

| 파라미터                                | 기본값                        | 재시작 필요        |
|-----------------------------------------|-------------------------------|--------------------|
| `autovacuum`                            | on                            | 아니오             |
| `autovacuum_worker_slots`               | 16 (보통)                     | 예 (PG18 신규)     |
| `autovacuum_max_workers`                | 3                             | 아니오             |
| `autovacuum_naptime`                    | 1min                          | 아니오             |
| `autovacuum_vacuum_threshold`           | 50                            | 아니오             |
| `autovacuum_vacuum_scale_factor`        | 0.2                           | 아니오             |
| `autovacuum_vacuum_max_threshold`       | 100000000                     | 아니오 (PG18 신규) |
| `autovacuum_vacuum_insert_threshold`    | 1000                          | 아니오             |
| `autovacuum_vacuum_insert_scale_factor` | 0.2                           | 아니오             |
| `autovacuum_analyze_threshold`          | 50                            | 아니오             |
| `autovacuum_analyze_scale_factor`       | 0.1                           | 아니오             |
| `autovacuum_freeze_max_age`             | 200000000                     | 예                 |
| `autovacuum_multixact_freeze_max_age`   | 400000000                     | 예                 |
| `autovacuum_vacuum_cost_delay`          | 2ms                           | 아니오             |
| `autovacuum_vacuum_cost_limit`          | -1 (`vacuum_cost_limit` 사용) | 아니오             |

재시작 필요 여부는 공식 문서에 "server start에서만 설정"으로 적힌 항목만 "예"로 표시했습니다. 나머지는 설정 파일 reload로 반영되는지 `pg_settings.context`(값이 `sighup`이면 reload)로 확인합니다.

```sql
SELECT name, setting, unit, context
FROM pg_settings WHERE name LIKE 'autovacuum%' ORDER BY name;
```

### 기본값의 한계

`scale_factor = 0.2`는 행 1억 개 테이블에서 죽은 튜플이 약 2천만 개 쌓여야 VACUUM이 돈다는 뜻입니다. PG18의 `autovacuum_vacuum_max_threshold`(기본 1억)가 상한을 두지만, 대형 테이블은 여전히 테이블별 설정이 필요한 경우가 많습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 파라미터 튜닝

### 테이블별 설정 (권장 시작점)

전역 값을 크게 바꾸기보다 변경이 많은 대형 테이블에만 낮은 비율을 줍니다.

```sql
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.01,   -- 1% 변경 시 VACUUM
  autovacuum_vacuum_threshold    = 1000,
  autovacuum_analyze_scale_factor = 0.02
);

-- 설정 확인
SELECT relname, reloptions FROM pg_class WHERE relname = 'orders';

-- 되돌리기
ALTER TABLE orders RESET (autovacuum_vacuum_scale_factor,
                          autovacuum_vacuum_threshold,
                          autovacuum_analyze_scale_factor);
```

### 속도(비용 기반 지연)

VACUUM은 I/O 비용을 점수로 계산해 `cost_limit`에 닿으면 `cost_delay`만큼 쉽니다. 워커가 여러 개면 `cost_limit`을 나눠 씁니다.

| 증상                                     | 조정 방향                                              |
|------------------------------------------|--------------------------------------------------------|
| 죽은 튜플이 계속 늘고 VACUUM이 오래 걸림 | `autovacuum_vacuum_cost_limit` 상향 (예: 1000~2000)    |
| VACUUM 때문에 디스크 I/O가 포화          | `cost_limit` 하향 또는 `cost_delay` 상향               |
| 대형 테이블 여러 개가 동시에 밀림        | `autovacuum_max_workers` 상향 (cost_limit도 같이)      |
| 인덱스 정리 단계가 오래 걸림             | `maintenance_work_mem` 또는 `autovacuum_work_mem` 상향 |

`autovacuum_max_workers`만 늘리면 같은 `cost_limit`을 더 많은 워커가 나눠 쓰므로 전체 속도가 빨라지지 않을 수 있습니다.

### 로그로 실행 내역 보기

```ini
# postgresql.conf
log_autovacuum_min_duration = '10s'   # 10초 이상 걸린 autovacuum 기록
```

로그에는 테이블명, 제거한 튜플 수, 남은 죽은 튜플 수, I/O 시간이 남습니다. "dead but not yet removable"(제거 불가) 수가 크면 7절의 원인을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 트랜잭션 ID 랩어라운드

트랜잭션 ID(XID)는 32비트이고 2^32를 기준으로 순환 비교합니다. 어떤 행의 XID가 현재보다 약 20억 이상 오래되면 "미래"로 보여 사라진 것처럼 됩니다. 이를 막으려고 VACUUM은 오래된 행을 **동결(frozen)** 상태로 바꿉니다. 모든 테이블은 적어도 20억 트랜잭션마다 한 번은 VACUUM되어야 합니다.

| 파라미터                    | 의미                                                                      |
|-----------------------------|---------------------------------------------------------------------------|
| `vacuum_freeze_min_age`     | 이 나이보다 오래된 XID를 가진 행을 동결                                   |
| `vacuum_freeze_table_age`   | 테이블 나이가 이 값을 넘으면 적극적(aggressive) VACUUM으로 전체 검사      |
| `autovacuum_freeze_max_age` | 테이블 나이가 이 값(기본 2억)을 넘으면 autovacuum이 꺼져 있어도 강제 실행 |

### 서버의 경고 단계

| 남은 XID   | 서버 동작                                                        |
|------------|------------------------------------------------------------------|
| 4천만 이하 | 경고 로그: `database "x" must be vacuumed within N transactions` |
| 3백만 이하 | 새 XID 할당 거부. 읽기 전용 트랜잭션만 가능                      |

### 쓰기가 거부됐을 때 대응 (공식 문서 순서)

1. 오래된 prepared transaction을 정리합니다(`pg_prepared_xacts`).
2. 오래 실행 중인 트랜잭션을 끝냅니다(`pg_stat_activity`, `pg_terminate_backend`).
3. 쓰지 않는 복제 슬롯을 삭제합니다(`pg_replication_slots`).
4. superuser로 해당 DB 전체에 `VACUUM`을 실행합니다. `VACUUM FULL`이나 `VACUUM FREEZE`는 쓰지 않습니다.
5. autovacuum 설정을 다시 확인합니다.

공식 문서는 이 상황에서 postmaster를 멈추거나 단일 사용자 모드로 들어갈 필요가 없다고 설명합니다. 단일 사용자 모드는 랩어라운드 보호 장치를 끄므로 더 위험합니다.

### 나이 확인

```sql
-- DB별 나이
SELECT datname, age(datfrozenxid) AS xid_age,
       round(100.0 * age(datfrozenxid) / 2000000000, 1) AS pct_to_limit
FROM pg_database ORDER BY xid_age DESC;

-- 테이블별 나이 (TOAST 포함)
SELECT c.oid::regclass AS table_name,
       greatest(age(c.relfrozenxid), age(t.relfrozenxid)) AS xid_age
FROM pg_class c
LEFT JOIN pg_class t ON c.reltoastrelid = t.oid
WHERE c.relkind IN ('r', 'm')
ORDER BY xid_age DESC LIMIT 20;
```

`xid_age`가 `autovacuum_freeze_max_age`(2억)를 꾸준히 넘어 있으면 강제 VACUUM이 따라가지 못하는 상태입니다. 알림 기준 예: 5억 경고, 10억 긴급.

MultiXact(여러 트랜잭션이 같은 행을 잠글 때 쓰는 ID)도 같은 구조로 순환하며, `age(datminmxid)` 대신 `mxid_age(datminmxid)`로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 모니터링 쿼리

### 죽은 튜플이 많은 테이블

```sql
SELECT relname,
       n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       last_vacuum, last_autovacuum, last_analyze, last_autoanalyze,
       autovacuum_count
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 20;
```

### 실행 중인 VACUUM 진행률

```sql
SELECT p.pid, p.relid::regclass AS table_name, p.phase,
       p.heap_blks_total, p.heap_blks_scanned, p.heap_blks_vacuumed,
       a.query_start, a.query
FROM pg_stat_progress_vacuum p
JOIN pg_stat_activity a USING (pid);
```

`phase`가 `vacuuming indexes`에서 오래 머물면 인덱스가 크거나 `maintenance_work_mem`이 작아 인덱스를 여러 번 훑는 경우입니다.

### 판단 기준 (예시)

| 지표                                   | 확인할 상황                               |
|----------------------------------------|-------------------------------------------|
| `dead_pct`가 20% 이상인 대형 테이블    | 테이블별 scale_factor 낮추기              |
| `last_autovacuum`이 며칠째 비어 있음   | 임계값 미달 또는 autovacuum이 계속 중단됨 |
| `n_dead_tup`이 VACUUM 후에도 안 줄어듦 | 7절 원인 (오래된 트랜잭션·슬롯)           |
| 테이블 크기만 계속 증가, 행 수는 일정  | bloat 의심 → `pgstattuple` 확장으로 측정  |

[⬆ 목차로 돌아가기](#목차)

---

## 7. VACUUM이 진행되지 않는 원인

VACUUM은 "아직 누군가 볼 수 있는" 옛 버전을 지울 수 없습니다. 가장 오래된 스냅샷이 기준선(xmin horizon)을 붙잡고 있으면 죽은 튜플이 쌓입니다.

| 원인                                  | 확인 쿼리·뷰                                      | 조치                                       |
|---------------------------------------|---------------------------------------------------|--------------------------------------------|
| 오래 열린 트랜잭션                    | `pg_stat_activity`의 `xact_start`, `backend_xmin` | 애플리케이션 수정, 종료                    |
| `idle in transaction` 세션            | `state = 'idle in transaction'`                   | `idle_in_transaction_session_timeout`      |
| 버려진 복제 슬롯                      | `pg_replication_slots`의 `active`, `xmin`         | 사용하지 않으면 `pg_drop_replication_slot` |
| standby의 `hot_standby_feedback = on` | standby의 긴 조회                                 | standby 쿼리 시간 제한                     |
| 오래된 prepared transaction           | `pg_prepared_xacts`                               | `COMMIT PREPARED` / `ROLLBACK PREPARED`    |

```sql
-- xmin을 붙잡고 있는 세션
SELECT pid, usename, state, xact_start, backend_xmin, left(query, 60) AS query
FROM pg_stat_activity
WHERE backend_xmin IS NOT NULL
ORDER BY age(backend_xmin) DESC LIMIT 10;

-- 복제 슬롯
SELECT slot_name, slot_type, active, xmin, catalog_xmin, restart_lsn
FROM pg_replication_slots;
```

🟡 주의: `pg_terminate_backend(pid)`는 해당 세션의 진행 중 트랜잭션을 롤백합니다. 배치 작업인지 확인한 뒤 실행합니다. `pg_drop_replication_slot`은 그 슬롯을 쓰는 standby나 CDC 도구가 다시 따라오지 못하게 만들 수 있습니다.

```ini
# 유휴 트랜잭션 자동 종료 (postgresql.conf, 값은 서비스 특성에 맞게)
idle_in_transaction_session_timeout = '10min'
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 운영 점검표

| 점검 항목                                                       | 확인 |
|-----------------------------------------------------------------|------|
| `autovacuum = on`이고 `track_counts = on`이다                   | [ ]  |
| `log_autovacuum_min_duration`으로 오래 걸린 실행이 기록된다     | [ ]  |
| DB별 `age(datfrozenxid)`를 감시하고 알림 기준이 있다            | [ ]  |
| `n_dead_tup` 상위 테이블을 주기적으로 본다                      | [ ]  |
| 변경이 많은 대형 테이블에 테이블별 autovacuum 설정이 있다       | [ ]  |
| `idle in transaction` 세션 제한 시간이 설정돼 있다              | [ ]  |
| 비활성 복제 슬롯을 감시한다                                     | [ ]  |
| 대량 적재·대량 삭제 후 수동 `VACUUM ANALYZE`를 실행한다         | [ ]  |
| 파티션 부모 테이블은 수동 `ANALYZE` 일정이 있다                 | [ ]  |
| `VACUUM FULL`은 점검 시간에만, 디스크 여유를 확인한 뒤 실행한다 | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [postgresql_install.md](./postgresql_install.md) — 설치와 postgresql.conf 기본 설정
- [rdbms_tuning.md](./rdbms_tuning.md) — 튜닝 종합
- [rdbms_transaction.md](../rdbms/rdbms_transaction.md) — 트랜잭션과 MVCC
- [rdbms_lock.md](../rdbms/rdbms_lock.md) — 잠금
- PostgreSQL Routine Vacuuming: [postgresql.org/docs/current/routine-vacuuming.html](https://www.postgresql.org/docs/current/routine-vacuuming.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL Automatic Vacuuming 설정: [postgresql.org/docs/current/runtime-config-autovacuum.html](https://www.postgresql.org/docs/current/runtime-config-autovacuum.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL VACUUM: [postgresql.org/docs/current/sql-vacuum.html](https://www.postgresql.org/docs/current/sql-vacuum.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL Progress Reporting: [postgresql.org/docs/current/progress-reporting.html](https://www.postgresql.org/docs/current/progress-reporting.html) — ★★★☆☆ (확인일 2026-11-16)

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
