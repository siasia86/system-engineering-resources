---
sources:
  - https://www.postgresql.org/support/versioning/
  - https://www.postgresql.org/docs/current/runtime-config.html
  - https://www.postgresql.org/docs/current/auth-password.html
  - https://wiki.postgresql.org/wiki/Apt
  - https://www.postgresql.org/download/linux/redhat/
last_checked: 2026-07-07
---

# PostgreSQL Official Notes

공식 문서에서 확인한 팩트를 기록합니다. 문서 작성/검증 시 참조용입니다.

## 버전 현황 (2026-07-07 확인)

| 버전 | 현재 마이너 | 지원 | 최초 릴리즈 | EOL        |
|------|-------------|------|-------------|------------|
| 18   | 18.4        | ✅   | 2025-09-25  | 2030-11-14 |
| 17   | 17.10       | ✅   | 2024-09-26  | 2029-11-08 |
| 16   | 16.14       | ✅   | 2023-09-14  | 2028-11-09 |
| 15   | 15.18       | ✅   | 2022-10-13  | 2027-11-11 |
| 14   | 14.23       | ✅   | 2021-09-30  | 2026-11-12 |
| 13   | 13.23       | ❌   | 2020-09-24  | 2025-11-13 |

- PostgreSQL 19 Beta 1: 2026-06-04 출시
- 메이저 버전 지원 기간: 최초 릴리즈 후 5년

## 설정 기본값 (PG18 기준)

### 메모리

| 파라미터             | 기본값    | 권장                           | 비고                           |
|----------------------|-----------|--------------------------------|--------------------------------|
| shared_buffers       | 128MB     | RAM 25%                        | initdb 시 자동 조정 가능       |
| effective_cache_size | 4GB       | RAM 75%                        | 플래너 힌트 (메모리 할당 아님) |
| work_mem             | 4MB       | 쿼리 복잡도에 따라             | 연결당 × 정렬 수만큼 사용      |
| maintenance_work_mem | 64MB      | 512MB~1GB                      | VACUUM, CREATE INDEX           |
| wal_buffers          | -1 (자동) | shared_buffers 1/32, 최대 16MB | 명시 설정 시 override          |
| huge_pages           | try       | try (기본)                     | on으로 강제 가능               |

### WAL / 내구성

| 파라미터                     | 기본값  | 비고                               |
|------------------------------|---------|------------------------------------|
| wal_level                    | replica | logical 복제 시 logical            |
| synchronous_commit           | on      | off 시 성능 향상, 데이터 손실 가능 |
| checkpoint_completion_target | 0.9     | PG14+에서 기본값 0.9 (이전 0.5)    |
| max_wal_size                 | 1GB     | 체크포인트 간격 제어               |
| min_wal_size                 | 80MB    | WAL 파일 최소 유지                 |

### 연결

| 파라미터         | 기본값    | 비고                         |
|------------------|-----------|------------------------------|
| max_connections  | 100       | 연결당 메모리 주의           |
| listen_addresses | localhost | '*'로 변경 시 원격 접속 허용 |
| port             | 5432      |                              |

### 쿼리 최적화

| 파라미터                 | 기본값 | SSD 권장 | 비고                        |
|--------------------------|--------|----------|-----------------------------|
| random_page_cost         | 4.0    | 1.1      | SSD에서 순차/랜덤 차이 작음 |
| effective_io_concurrency | 1      | 200      | SSD 병렬 I/O                |
| seq_page_cost            | 1.0    | 1.0      | 기준값                      |

## 인증

| 버전      | password_encryption 기본 | pg_hba 기본 METHOD | 비고                |
|-----------|--------------------------|--------------------|---------------------|
| PG13 이하 | md5                      | md5                |                     |
| PG14+     | scram-sha-256            | scram-sha-256      | md5 deprecated 예고 |

- MD5 암호화 패스워드 지원은 deprecated (향후 제거 예정)
- pg_hba.conf에 md5 지정해도 서버 패스워드가 SCRAM이면 SCRAM으로 자동 전환

## ICU / Locale 변경사항

| 버전 | 변경                                                                       |
|------|----------------------------------------------------------------------------|
| PG15 | ICU collation provider 도입 (선택)                                         |
| PG16 | ICU provider를 기본 선택 가능, LOCALE_PROVIDER 파라미터 추가               |
| PG17 | template0/template1이 ICU provider 사용 가능, initdb --locale-provider=icu |
| PG18 | ICU가 initdb 기본 provider (glibc 대신) — 빌드 시 ICU 필수                 |

- `CREATE DATABASE ... LOCALE 'C.UTF-8'`: libc provider 사용
- `CREATE DATABASE ... LOCALE_PROVIDER 'icu' ICU_LOCALE 'en-US'`: ICU 사용
- `LC_COLLATE 'en_US.UTF-8'`: 해당 locale 설치 시 여전히 동작 (libc)

## PGDG 저장소

### APT (Ubuntu/Debian)

```
키: https://www.postgresql.org/media/keys/ACCC4CF8.asc
저장소: https://apt.postgresql.org/pub/repos/apt {codename}-pgdg main
지원: jammy (22.04), noble (24.04), questing (25.10 amd64 only)
```

### YUM/DNF (RHEL 계열)

```
EL-9: https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
EL-8: https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
주의: dnf module disable postgresql 필수 (AppStream 충돌)
```

## 설치 경로

| 항목     | Ubuntu (PGDG)                | RHEL 계열 (PGDG)            |
|----------|------------------------------|-----------------------------|
| 바이너리 | /usr/lib/postgresql/18/bin/  | /usr/pgsql-18/bin/          |
| 데이터   | /var/lib/postgresql/18/main/ | /var/lib/pgsql/18/data/     |
| 설정     | /etc/postgresql/18/main/     | /var/lib/pgsql/18/data/     |
| 로그     | /var/log/postgresql/         | /var/lib/pgsql/18/data/log/ |
| 서비스   | postgresql                   | postgresql-18               |

## 주요 변경 이력

| 버전 | 주요 변경                                                 |
|------|-----------------------------------------------------------|
| PG14 | scram-sha-256 기본, REINDEX CONCURRENTLY 개선             |
| PG15 | MERGE 문, ICU collation provider, pg_stat_statements 개선 |
| PG16 | 논리 복제 개선, pg_stat_io, 병렬 쿼리 확장                |
| PG17 | COPY 성능 개선, JSON_TABLE, vacuum 개선                   |
| PG18 | ICU 기본 provider, async I/O, NUMA 지원 개선              |

## 미확인 — 검증 필요

- PG18 ICU가 initdb 기본 provider인지 여부 (논의됐으나 GA 확정 미확인)
- PG18 async I/O 세부 동작 (공식 릴리즈 노트 미확인)
- PG19 예상 기능 (Beta 단계, 변경 가능)
