# RDBMS 스키마 마이그레이션 (Schema Migration)

## 목차

| 단계 | 섹션                                                                                                                                                                        |
|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 스키마 마이그레이션 개념](#1-스키마-마이그레이션-개념) / [2. 온라인 DDL](#2-온라인-ddl)                                                                                  |
| 도구 | [3. pt-online-schema-change](#3-pt-online-schema-change) / [4. gh-ost](#4-gh-ost)                                                                                           |
| 전략 | [5. 무중단 마이그레이션 패턴](#5-무중단-마이그레이션-패턴) / [6. 롤백 전략](#6-롤백-전략) / [7. 실무 팁](#7-실무-팁) |

---

## 1. 스키마 마이그레이션 개념

운영 중인 데이터베이스의 스키마(테이블 구조)를 변경하는 작업.

### 위험 요소

| 위험 | 설명 |
|------|------|
| **테이블 잠금** | DDL 실행 중 DML 차단 → 서비스 중단 |
| **대용량 테이블** | 수억 건 테이블 ALTER는 수 시간 소요 |
| **복제 지연** | Primary DDL이 Replica에 전파되며 지연 발생 |
| **롤백 불가** | 일부 DDL은 되돌리기 어려움 |

### MySQL Online DDL 지원 여부

| 작업 | In-Place | 잠금 |
|------|----------|------|
| 컬럼 추가 (마지막) | ✅ | 없음 |
| 컬럼 추가 (중간) | ✅ | 없음 |
| 컬럼 삭제 | ✅ | 없음 |
| 컬럼 타입 변경 | ❌ (일부 예외) | 전체 잠금 (VARCHAR 확장 등 일부는 INPLACE 가능) |
| 인덱스 추가 | ✅ | 없음 |
| PK 변경 | ❌ | 전체 잠금 |
| 컬럼명 변경 | ✅ | 없음 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 온라인 DDL

### MySQL ALGORITHM, LOCK 옵션

```sql
-- 잠금 없이 인덱스 추가
ALTER TABLE orders
    ADD INDEX idx_status (status),
    ALGORITHM=INPLACE,
    LOCK=NONE;

-- 컬럼 추가 (잠금 없음)
ALTER TABLE orders
    ADD COLUMN note TEXT,
    ALGORITHM=INPLACE,
    LOCK=NONE;

-- 타입 변경 (잠금 필요 — 주의)
ALTER TABLE orders
    MODIFY COLUMN amount BIGINT,
    ALGORITHM=COPY,
    LOCK=SHARED;
```

### PostgreSQL 온라인 DDL

```sql
-- 인덱스 잠금 없이 생성
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);

-- 컬럼 추가 (NULL 허용 시 즉시 완료)
ALTER TABLE orders ADD COLUMN note TEXT;

-- NOT NULL 컬럼 추가 (기본값 있으면 즉시 완료, PostgreSQL 11+)
ALTER TABLE orders ADD COLUMN priority INT NOT NULL DEFAULT 0;
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. pt-online-schema-change

Percona Toolkit의 무중단 스키마 변경 도구.

### 동작 원리

```
1. 새 테이블(_new) 생성 (변경된 스키마)
2. 트리거 설치 (INSERT/UPDATE/DELETE를 _new에도 반영)
3. 기존 데이터를 청크 단위로 복사
4. 복사 완료 후 테이블 이름 교체 (RENAME)
5. 트리거 및 임시 테이블 삭제
```

### 사용법

```bash
# 컬럼 추가
pt-online-schema-change \
    --alter "ADD COLUMN note TEXT" \
    --host=localhost \
    --user=root \
    --password=SecurePassword123 \
    --database=mydb \
    --table=orders \
    --execute

# 인덱스 추가
pt-online-schema-change \
    --alter "ADD INDEX idx_status (status)" \
    D=mydb,t=orders \
    --execute

# 주요 옵션
# --chunk-size=1000       청크 크기 (기본 1000행)
# --max-load=Threads_running:25  부하 임계값
# --critical-load=Threads_running:50  중단 임계값
# --dry-run              실제 실행 없이 검증만
```

### 제약사항

- 외래키 있는 테이블: `--alter-foreign-keys-method=rebuild_constraints`
- 트리거 있는 테이블: MySQL 5.7 이하에서 불가

[⬆ 목차로 돌아가기](#목차)

---

## 4. gh-ost

GitHub이 개발한 트리거 없는 무중단 스키마 변경 도구.

### pt-osc vs gh-ost 비교

| 항목 | pt-osc | gh-ost |
|------|--------|--------|
| 방식 | 트리거 기반 | binlog 기반 |
| 트리거 부하 | 있음 | 없음 |
| 기존 트리거 | 충돌 가능 | 무관 |
| 일시 중지 | 불가 | 가능 |
| 진행 상황 | 제한적 | 상세 |
| 복잡도 | 낮음 | 높음 |

### 동작 원리

```
1. Ghost 테이블(_ghc) 생성
2. binlog 스트리밍으로 변경사항 실시간 반영
3. 기존 데이터 청크 복사
4. 완료 후 cutover (원자적 RENAME)
```

### 사용법

```bash
gh-ost \
    --user=root \
    --password=SecurePassword123 \
    --host=localhost \
    --database=mydb \
    --table=orders \
    --alter="ADD COLUMN note TEXT" \
    --allow-on-master \
    --execute

# 주요 옵션
# --chunk-size=1000
# --max-load=Threads_running=25
# --throttle-control-replicas=replica1:3306
# --postpone-cut-over-flag-file=/tmp/gh-ost.postpone
# --panic-flag-file=/tmp/gh-ost.panic
```

### 일시 중지 및 재개

```bash
# 소켓 파일로 제어
echo "throttle" | nc -U /tmp/gh-ost.mydb.orders.sock
echo "no-throttle" | nc -U /tmp/gh-ost.mydb.orders.sock
echo "status" | nc -U /tmp/gh-ost.mydb.orders.sock
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 무중단 마이그레이션 패턴

### 패턴 1: Expand-Contract (확장-축소)

컬럼 이름 변경, 타입 변경 등 호환성 없는 변경에 사용.

```
Step 1 (Expand): 새 컬럼 추가, 양쪽 모두 쓰기
ALTER TABLE users ADD COLUMN email_new VARCHAR(200);

Step 2: 애플리케이션 배포 (old/new 모두 읽기)

Step 3: 데이터 마이그레이션
UPDATE users SET email_new = email WHERE email_new IS NULL;

Step 4 (Contract): 구 컬럼 제거
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN email_new TO email;
```

### 패턴 2: 새 테이블 + 이중 쓰기

```
1. 새 스키마 테이블 생성
2. 애플리케이션: 구/신 테이블 모두 쓰기
3. 기존 데이터 백필(backfill)
4. 애플리케이션: 신 테이블만 읽기
5. 구 테이블 제거
```

### 패턴 3: Blue-Green 마이그레이션

```
Blue (Current)            Green (New Schema)
┌─────────────┐           ┌─────────────┐
│  DB v1      │ ─ repl ─> │  DB v2      │
│  (old)      │           │  (new)      │
└─────────────┘           └─────────────┘
        │                         │
        └──── traffic switch ─────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 롤백 전략

### 즉시 롤백 가능한 작업

```sql
-- 컬럼 추가 → 컬럼 삭제로 롤백
ALTER TABLE orders ADD COLUMN note TEXT;
-- 롤백
ALTER TABLE orders DROP COLUMN note;

-- 인덱스 추가 → 인덱스 삭제로 롤백
CREATE INDEX idx_status ON orders (status);
-- 롤백
DROP INDEX idx_status ON orders;
```

### 롤백 어려운 작업

```sql
-- 컬럼 타입 변경 (데이터 손실 가능)
ALTER TABLE orders MODIFY COLUMN amount BIGINT;
-- 롤백 전 반드시 백업 필요

-- 컬럼 삭제 (데이터 영구 삭제)
ALTER TABLE orders DROP COLUMN old_field;
-- 롤백 불가 → 삭제 전 백업 필수
```

### 마이그레이션 전 체크리스트

```bash
# 1. 백업 확인
mysqldump mydb orders > orders_backup_$(date +%Y%m%d).sql

# 2. Dry-run 실행
pt-online-schema-change --dry-run ...

# 3. Replica 지연 확인
SHOW REPLICA STATUS\G  # Seconds_Behind_Source = 0

# 4. 슬로우 쿼리 없는지 확인
SHOW PROCESSLIST;

# 5. 롤백 스크립트 준비
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: 마이그레이션 도구 선택 기준

| 상황 | 권장 도구 |
|------|-----------|
| 단순 컬럼 추가/삭제 | MySQL Online DDL |
| 트리거 있는 테이블 | gh-ost |
| 외래키 있는 테이블 | pt-osc (--alter-foreign-keys-method) |
| 대용량 + 안전 우선 | gh-ost |
| 빠른 적용 필요 | pt-osc |

### Tip 2: 청크 크기 조정

```bash
# 부하 모니터링하며 청크 크기 조정
# Threads_running이 높으면 청크 크기 줄이기
pt-online-schema-change \
    --chunk-size=500 \
    --max-load=Threads_running:20 \
    ...
```

### Tip 3: 마이그레이션 시간 예측

```sql
-- 테이블 행 수 확인
SELECT table_rows, data_length/1024/1024 AS data_mb
FROM information_schema.tables
WHERE table_name = 'orders';

-- 예상 시간 = 행 수 / (청크 크기 × 초당 처리 청크 수)
-- 1억 건, 청크 1000, 초당 10청크 = 10,000초 ≈ 2.8시간
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Percona pt-online-schema-change: [percona.com](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html) — ★★☆☆☆
- gh-ost GitHub: [gh-ost](https://github.com/github/gh-ost) — ★★☆☆☆
- MySQL Documentation: [Online DDL Operations](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html) — ★★★☆☆

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
