# dbtrail

MySQL 바이너리 로그를 실시간 스트리밍하여 행 단위 시점 복구(PITR) + 변경 추적(CDC) + 감사(Forensics)를 제공하는 오픈소스 도구입니다. 기존 백업을 대체하지 않고 보완합니다.

## 목차

| 섹션                                                                                                              |
|-------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 설치](#3-설치) / [4. 핵심 기능](#4-핵심-기능)               |
| [5. CLI 명령어](#5-cli-명령어) / [6. 운영](#6-운영) / [7. 기존 도구 비교](#7-기존-도구-비교) / [8. 제약](#8-제약) |

---

## 1. 개요

| 항목     | 내용                                                                           |
|----------|--------------------------------------------------------------------------------|
| 이름     | dbtrail (CLI: `bintrail`)                                                      |
| 언어     | Go                                                                             |
| 라이선스 | Apache-2.0                                                                     |
| 지원 DB  | MySQL 8.0+, Percona, Aurora MySQL, Cloud SQL, MariaDB(alpha), PostgreSQL(beta) |
| 저장     | S3 (Parquet 포맷)                                                              |
| 인덱싱   | DuckDB                                                                         |
| 배포     | Docker Compose, systemd, goreleaser                                            |
| GitHub   | [github.com/dbtrail/dbtrail](https://github.com/dbtrail/dbtrail)               |

### 포지셔닝

| 분류                          | 해당 |
|-------------------------------|------|
| 전체 DB 백업/복원 (재해 복구) | ❌   |
| 행 단위 시점 복구 (PITR)      | ✅   |
| 변경 데이터 캡처 (CDC)        | ✅   |
| 감사/모니터링 (Forensics)     | ✅   |

```
전통 백업 ────────────── dbtrail ────────────── 모니터링/감사
(mysqldump)             (행 단위 복구+추적)     (Audit Log)

전통 백업: "어제 02시로 전체 DB 돌려줘"
dbtrail:   "5분 전에 삭제된 주문 3건만 복구해줘" + "누가 삭제했어?"
```

### 요구사항

| 항목             | 조건                                    |
|------------------|-----------------------------------------|
| MySQL 버전       | 8.0+                                    |
| binlog_format    | ROW (필수)                              |
| binlog_row_image | FULL (필수)                             |
| 접속 방식        | 복제 프로토콜 (binlog 파일 접근 불필요) |
| 확인 명령        | `bintrail doctor` (설정 자동 점검)      |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

### 데이터 흐름

```
MySQL binlog
    │
    │  replication protocol (no lock, no schema change)
    v
bintrail stream ──> Parquet files ──> S3 (object storage)
                                       │
                                       v
                                   DuckDB index
                                       │
                   ┌───────────────────┼───────────────────┐
                   v                   v                   v
             Time-Travel         Recovery SQL         Forensics
             (AS OF query)    (row-level undo)   (who changed what)
```

### 컴포넌트

| 컴포넌트           | 역할                                        |
|--------------------|---------------------------------------------|
| `bintrail stream`  | binlog 실시간 수신 → Parquet 변환 → S3 저장 |
| `bintrail index`   | S3의 Parquet → DuckDB 인덱싱                |
| `bintrail-console` | 웹 UI (모니터링, 복구, 서버 관리)           |
| `bintrail-mcp`     | MCP 서버 (AI 에이전트 연동)                 |
| ProxySQL (선택)    | Time-Travel SQL (`AS OF`) 프록시            |

### Parquet을 쓰는 이유

| 이점        | 설명                                          |
|-------------|-----------------------------------------------|
| 압축률      | 컬럼 단위 압축 → CSV 대비 50~80% 절감         |
| 쿼리 속도   | 필요한 컬럼만 읽음 → 10~100x 빠름             |
| 호환성      | DuckDB, Athena, Spark, BigQuery 네이티브 지원 |
| 스키마 내장 | 타입 정보 포함 → 파싱 에러 없음               |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설치

### Docker Compose (권장)

```bash
curl -fsSL https://raw.githubusercontent.com/dbtrail/dbtrail/main/install.sh | sh
```

실행 후:
1. http://127.0.0.1:8090 접속 → 계정 생성
2. "+ Add server" → MySQL 접속 정보 입력
3. preflight check → 인덱스 생성 → 스트리밍 시작

### 데모 (30초 체험)

```bash
docker run --rm -p 6033:6033 ghcr.io/dbtrail/bintrail-demo
```

### 바이너리 설치

```bash
# goreleaser로 빌드된 바이너리
gh release download --repo dbtrail/dbtrail --pattern "*linux_amd64*"
tar xzf bintrail_*_linux_amd64.tar.gz
sudo mv bintrail /usr/local/bin/
```

### 초기 설정 확인

```bash
# MySQL 설정 점검 (binlog_format, binlog_row_image 등)
bintrail doctor --host 192.0.2.1 --user dbtrail --password SecurePassword123
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 핵심 기능

### 4.1 Time-Travel (시점 조회)

특정 시점의 데이터를 조회합니다. 전체 복원 없이 "그때 이 행이 어땠는지" 확인합니다.

```sql
-- ProxySQL 경유 시 SQL 인터페이스
SELECT * FROM orders WHERE id = 123 AS OF '2026-07-01 14:00:00'

-- CLI
bintrail reconstruct --table orders --pk 123 --at '2026-07-01 14:00:00'
```

### 4.2 Row-Level Recovery (행 단위 복구)

삭제/변경된 특정 행만 복원 SQL을 생성합니다.

```bash
# 삭제된 행 복구 SQL 생성
bintrail recover --table orders --pk 123 --at '2026-07-01 14:00:00'
# 출력: INSERT INTO orders (id, customer, amount, ...) VALUES (123, 'kim', 50000, ...);

# 변경 이전 값으로 되돌리기
bintrail recover --table orders --pk 123 --before '2026-07-01 15:00:00'
# 출력: UPDATE orders SET amount=50000 WHERE id=123;
```

### 4.3 Cascade Recovery

`ON DELETE CASCADE`로 자식 테이블에서 삭제된 행까지 재구성합니다. InnoDB가 binlog 아래에서 처리하므로 일반 도구로는 복구 불가한 데이터를 복원합니다.

```bash
bintrail recover-cascade --table customers --pk 456
# → customers 행 + 연관된 orders, payments 자식 행까지 복구 SQL 생성
```

### 4.4 Forensics (감사 추적)

"누가, 언제, 어떤 행을 변경했는가"를 추적합니다.

```bash
# 특정 행의 변경 이력
bintrail query --table orders --pk 123

# "이 행을 변경한 사용자" 추적
bintrail whochanged --table orders --pk 123
# 출력: user=admin@10.200.90.155, program=python3, time=2026-07-01 14:32:11

# 특정 사용자의 모든 변경 조회
bintrail query --user admin --since '2026-07-01'
```

### 4.5 Verify (복구 검증)

복구 결과가 실제 원본과 일치하는지 오프라인에서 검증합니다.

```bash
# baseline(스냅샷) + binlog 변경 적용 결과 vs 현재 DB 비교
bintrail verify --table orders
# ✓ 0 mismatches, 0 gaps

# 스트리밍 갭 확인
bintrail status
# stream: 2026-07-06 17:30:00 (lag: 2s, gaps: 0)
```

### 4.6 Web Console

브라우저에서 변경 이력 조회, 복구 실행, 서버 상태 모니터링을 수행합니다.

- http://127.0.0.1:8090
- 기능: 서버 추가, 변경 이력 검색, 복구 SQL 생성, baseline 관리

### 4.7 MCP Server (AI 연동)

Claude 등 MCP 지원 AI 에이전트에서 변경 이력 검색 + 복구 SQL 생성을 요청할 수 있습니다.

```json
{
  "mcpServers": {
    "dbtrail": {
      "command": "bintrail-mcp",
      "args": ["--config", "/etc/bintrail/config.yaml"]
    }
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. CLI 명령어

### 주요 명령어

| 명령어                     | 용도                               |
|----------------------------|------------------------------------|
| `bintrail doctor`          | MySQL 설정 점검 (binlog_format 등) |
| `bintrail stream`          | binlog 실시간 스트리밍 시작        |
| `bintrail index`           | S3 Parquet → DuckDB 인덱싱         |
| `bintrail status`          | 스트리밍 상태, 갭, 지연 확인       |
| `bintrail query`           | 변경 이력 조회                     |
| `bintrail reconstruct`     | 특정 시점 테이블/행 재구성         |
| `bintrail recover`         | 복구 SQL 생성                      |
| `bintrail recover-cascade` | CASCADE 삭제 포함 복구             |
| `bintrail whochanged`      | 변경 사용자 추적                   |
| `bintrail verify`          | 복구 무결성 검증                   |
| `bintrail baseline`        | 스냅샷 기준점 생성                 |
| `bintrail rotate`          | Parquet 파일 로테이션              |
| `bintrail upload`          | 로컬 Parquet → S3 업로드           |
| `bintrail dump`            | baseline 덤프 (mydumper 호환)      |

### 설정 파일

```yaml
# /etc/bintrail/config.yaml (또는 --config 지정)
mysql:
  host: 192.0.2.1
  port: 3306
  user: dbtrail
  password: SecurePassword123

storage:
  type: s3
  bucket: my-bucket
  prefix: dbtrail/
  region: ap-northeast-2

index:
  path: /var/lib/bintrail/index
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영

### 스트리밍 시작/관리

```bash
# systemd 서비스로 실행
sudo systemctl enable --now bintrail-agent

# 상태 확인
bintrail status
# server: mysql-prod (10.200.101.50)
# stream: 2026-07-06 17:30:00 (lag: 2s, gaps: 0)
# index:  2026-07-06 17:29:55 (5s behind stream)
# storage: s3://my-bucket/dbtrail/ (12.5 GB)
```

### 모니터링

| 항목          | 확인 방법                                     |
|---------------|-----------------------------------------------|
| 스트리밍 지연 | `bintrail status` → lag                       |
| 갭 (누락)     | `bintrail status` → gaps (0이어야 정상)       |
| 디스크 용량   | `bintrail doctor` → capacity check            |
| S3 저장량     | 웹 콘솔 Storage 탭                            |
| Prometheus    | `/metrics` 엔드포인트 (Grafana 대시보드 제공) |

### 로테이션

```bash
# Parquet 파일 로테이션 (기본: 시간 단위)
bintrail rotate

# 오래된 인덱스 정리
bintrail archive --retain 30d
```

### 복구 실무 흐름

```
1. 사고 인지: "주문 테이블에서 데이터 삭제됨"

2. 갭 확인
   bintrail status  → gaps: 0 (복구 가능 확인)

3. 삭제 시점 특정
   bintrail query --table orders --since '2026-07-06 14:00' --type DELETE

4. 복구 SQL 생성
   bintrail recover --table orders --pk 123,456,789 --at '2026-07-06 14:30'

5. 검증 (dry-run)
   bintrail verify --table orders

6. 복구 적용
   mysql -h prod < recover.sql
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 기존 도구 비교

| 항목         | mysqldump                   | xtrabackup  | binlog 수동 | dbtrail          |
|--------------|-----------------------------|-------------|-------------|------------------|
| 복구 단위    | DB 전체                     | DB 전체     | 트랜잭션    | 행 단위          |
| 복구 시간    | 수 시간 (대형 DB)           | 수십 분     | 수동 파싱   | 수 초 (SQL 생성) |
| 잠금         | 있음 (--single-transaction) | 없음        | 없음        | 없음             |
| CASCADE 복구 | 불가                        | 불가        | 수동        | ✅ 자동          |
| 변경 추적    | 불가                        | 불가        | 수동 파싱   | ✅ 자동          |
| "누가 변경?" | 불가                        | 불가        | 어려움      | ✅ Forensics     |
| 실시간       | ❌ (스냅샷)                 | ❌ (스냅샷) | ❌ (수동)   | ✅ 실시간        |
| 재해 복구    | ✅                          | ✅          | 부분적      | ❌               |
| 난이도       | 낮음                        | 중간        | 높음        | 중간             |

### 조합 권장

```
재해 복구 (전체 DB 손실):
  → xtrabackup (물리 백업) + binlog relay

행 단위 실수 복구 + 감사:
  → dbtrail

운영 조합:
  xtrabackup (매일 전체 백업) + dbtrail (실시간 행 추적)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 제약

| 제약             | 설명                                                        |
|------------------|-------------------------------------------------------------|
| 전체 복원 불가   | DB 전체가 날아가면 dbtrail만으로 복구 불가 (기존 백업 필요) |
| MySQL 8.0+       | 5.7 이하 미지원                                             |
| ROW 포맷 필수    | STATEMENT/MIXED 포맷에서는 행 변경 추적 불가                |
| FULL 이미지 필수 | `binlog_row_image=MINIMAL`이면 before 이미지 없음           |
| 복제 프로토콜    | 관리형 DB(RDS 등)에서는 복제 권한 설정 필요                 |
| 저장 비용        | 모든 변경을 저장하므로 쓰기 빈도 높은 DB는 S3 비용 증가     |
| ProxySQL 필요    | `AS OF` SQL 인터페이스 사용 시 필수                         |
| DDL 추적 제한    | 스키마 변경 추적은 부분적 (ALTER TABLE 등)                  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- dbtrail GitHub: [github.com/dbtrail/dbtrail](https://github.com/dbtrail/dbtrail) — ★★☆☆☆
- dbtrail Docs: [github.com/dbtrail/dbtrail/tree/main/docs](https://github.com/dbtrail/dbtrail/tree/main/docs) — ★★☆☆☆
- [architecture.md](./architecture.md) — 내부 동작, 스트리밍, 저장 구조, 용량 계획
- [recovery_guide.md](./recovery_guide.md) — 시나리오별 복구 방법 상세
- [forensics.md](./forensics.md) — 감사 추적 (누가 변경했나)
- [../rdbms_replication.md](../rdbms_replication.md)

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
