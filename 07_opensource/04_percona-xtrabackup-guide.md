# Percona XtraBackup 가이드

MySQL/MariaDB의 물리적 백업 도구인 Percona XtraBackup 사용 가이드입니다.

---

## 목차

1. [XtraBackup 소개](#1-xtrabackup-소개)
2. [설치](#2-설치)
3. [백업 전략](#3-백업-전략)
4. [Full Backup (전체 백업)](#4-full-backup-전체-백업)
5. [Incremental Backup (증분 백업)](#5-incremental-backup-증분-백업)
6. [복원 (Restore)](#6-복원-restore)
7. [자동화 스크립트](#7-자동화-스크립트)
8. [트러블슈팅](#8-트러블슈팅)
9. [베스트 프랙티스](#9-베스트-프랙티스)

---

## 1. XtraBackup 소개

### XtraBackup이란?

Percona XtraBackup은 MySQL/MariaDB의 **물리적 백업(Physical Backup)** 도구입니다.

### 주요 특징

| 특징 | XtraBackup | mysqldump |
|------|------------|-----------|
| 백업 방식 | 물리적 (파일 복사) | 논리적 (SQL 덤프) |
| 백업 속도 | 매우 빠름 | 느림 |
| 복원 속도 | 매우 빠름 | 느림 |
| 서비스 중단 | 불필요 (Hot Backup) | 불필요 |
| 증분 백업 | 지원 ✓ | 미지원 ✗ |
| 특정 DB만 복원 | 어려움 | 쉬움 |
| 대용량 DB | 적합 | 부적합 |

### 백업 방식 비교

```
물리적 백업 (XtraBackup)
- 데이터 파일(.ibd)을 직접 복사
- 빠르지만 특정 테이블만 복원 어려움
- 메타데이터 의존성 있음

논리적 백업 (mysqldump)
- SQL 쿼리문으로 저장
- 느리지만 유연함
- 특정 테이블/DB만 복원 가능
```

### 언제 XtraBackup을 사용해야 하나?

**✅ XtraBackup 권장:**
- 대용량 데이터베이스 (100GB 이상)
- 빠른 백업/복원이 필요한 경우
- 증분 백업이 필요한 경우
- 서비스 중단 없이 백업

**✅ mysqldump 권장:**
- 소규모 데이터베이스
- 특정 테이블/DB만 백업/복원
- 다른 MySQL 버전으로 마이그레이션
- 데이터 검증 및 수정 필요

---

## 2. 설치

### 2.1 환경 확인

```bash
# OS 확인
cat /etc/os-release

# MySQL 버전 확인 (중요!)
mysql --version
# 또는
rpm -qa | grep -i mysql-community-server
```

### 2.2 버전 호환성

**중요**: XtraBackup 버전은 MySQL 버전과 일치해야 합니다!

| MySQL 버전 | XtraBackup 버전 |
|-----------|----------------|
| 5.7.x | percona-xtrabackup-24 |
| 8.0.x | percona-xtrabackup-80 |
| 8.1.x | percona-xtrabackup-81 |

### 2.3 설치 (Amazon Linux 2 / CentOS 7)

```bash
# Percona 저장소 추가
yum install https://repo.percona.com/yum/percona-release-latest.noarch.rpm

# 사용 가능한 버전 확인
yum list percona-xtrabackup-80.x86_64 --showduplicates

# 출력 예시:
# percona-xtrabackup-80.x86_64    8.0.32-26.1.el7    percona-release-x86_64
# percona-xtrabackup-80.x86_64    8.0.33-27.1.el7    percona-release-x86_64
# percona-xtrabackup-80.x86_64    8.0.33-28.1.el7    percona-release-x86_64

# MySQL 버전에 맞춰 설치
# 예: MySQL 8.0.33인 경우
yum install percona-xtrabackup-80-8.0.33-28.1.el7

# 설치 확인
xtrabackup --version
# 출력: xtrabackup version 8.0.33-28 based on MySQL server 8.0.33
```

### 2.4 Ubuntu/Debian 설치

```bash
# Percona 저장소 추가
wget https://repo.percona.com/apt/percona-release_latest.generic_all.deb
dpkg -i percona-release_latest.generic_all.deb
apt-get update

# 설치
apt-get install percona-xtrabackup-80
```

### 2.5 백업 전용 사용자 생성

```sql
-- MySQL 8.0
CREATE USER 'backup'@'localhost' IDENTIFIED BY 'SecurePassword123!';

GRANT BACKUP_ADMIN, PROCESS, RELOAD, LOCK TABLES, REPLICATION CLIENT 
ON *.* TO 'backup'@'localhost';

GRANT SELECT ON performance_schema.log_status TO 'backup'@'localhost';
GRANT SELECT ON performance_schema.keyring_component_status TO 'backup'@'localhost';

FLUSH PRIVILEGES;
```

```sql
-- MySQL 5.7
CREATE USER 'backup'@'localhost' IDENTIFIED BY 'SecurePassword123!';

GRANT RELOAD, LOCK TABLES, PROCESS, REPLICATION CLIENT 
ON *.* TO 'backup'@'localhost';

FLUSH PRIVILEGES;
```

---

## 3. 백업 전략

### 3.1 백업 유형

```
┌─────────────────────────────────────────────────────────┐
│                    백업 전략 예시                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  일요일 00:00  ──→  Full Backup (전체)                   │
│       │                                                  │
│       ├─ 월요일 01:00  ──→  Incremental (증분)          │
│       ├─ 월요일 02:00  ──→  Incremental (증분)          │
│       ├─ 월요일 03:00  ──→  Incremental (증분)          │
│       │        ...                                       │
│       └─ 토요일 23:00  ──→  Incremental (증분)          │
│                                                          │
│  다음 일요일 00:00  ──→  Full Backup (전체)              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 증분 백업 방식

**Incremental (증분 백업)**
- 마지막 Full Backup 이후 변경된 데이터만 백업
- 복원 시 Full + 모든 Incremental 필요
- 백업 용량 작음, 복원 시간 김

```
Full ──→ Inc1 ──→ Inc2 ──→ Inc3
 │        │        │        │
 └────────┴────────┴────────┘
      복원 시 모두 필요
```

**Differential (차등 백업)**
- 각 증분이 이전 증분을 기준으로 백업
- 복원 시 Full + 마지막 Differential만 필요
- 백업 용량 큼, 복원 시간 짧음

```
Full ──→ Diff1
 │   ──→ Diff2
 │   ──→ Diff3
 └───────────┘
   복원 시 Full + Diff3만 필요
```

### 3.3 권장 백업 주기

**소규모 (< 100GB)**
```bash
# 매일 Full Backup
0 2 * * * /path/to/full-backup.sh
```

**중규모 (100GB - 1TB)**
```bash
# 주 1회 Full, 매일 Incremental
0 2 * * 0 /path/to/full-backup.sh      # 일요일
0 2 * * 1-6 /path/to/incremental-backup.sh  # 월-토
```

**대규모 (> 1TB)**
```bash
# 주 1회 Full, 매시간 Incremental
0 0 * * 0 /path/to/full-backup.sh      # 일요일 00시
0 * * * * /path/to/incremental-backup.sh    # 매시간
```

---

## 4. Full Backup (전체 백업)

### 4.1 기본 Full Backup

```bash
# 기본 명령어
xtrabackup \
  --user=backup \
  --password='SecurePassword123!' \
  --backup \
  --target-dir=/backup/full/$(date +%Y%m%d-%H)

# 옵션 설명:
# --backup: 백업 모드
# --target-dir: 백업 저장 경로
```

### 4.2 압축 백업

```bash
# 압축하여 백업 (디스크 공간 절약)
xtrabackup \
  --user=backup \
  --password='SecurePassword123!' \
  --backup \
  --compress \
  --compress-threads=4 \
  --target-dir=/backup/full/$(date +%Y%m%d-%H)
```

### 4.3 병렬 백업

```bash
# 여러 스레드로 빠르게 백업
xtrabackup \
  --user=backup \
  --password='SecurePassword123!' \
  --backup \
  --parallel=4 \
  --target-dir=/backup/full/$(date +%Y%m%d-%H)
```

### 4.4 백업 검증

```bash
# 백업 완료 후 체크섬 확인
BACKUP_DIR="/backup/full/$(date +%Y%m%d-%H)"

# xtrabackup_checkpoints 파일 확인
cat ${BACKUP_DIR}/xtrabackup_checkpoints

# 출력 예시:
# backup_type = full-backuped
# from_lsn = 0
# to_lsn = 123456789
# last_lsn = 123456789
```

**LSN (Log Sequence Number) 이해:**
- `from_lsn = 0`: Full Backup은 항상 0부터 시작
- `to_lsn`: 백업이 완료된 시점의 LSN
- 증분 백업 시 이 값을 기준으로 사용

---

## 5. Incremental Backup (증분 백업)

### 5.1 기본 Incremental Backup

```bash
# Full Backup 기준으로 증분 백업
xtrabackup \
  --user=backup \
  --password='SecurePassword123!' \
  --backup \
  --target-dir=/backup/inc/$(date +%Y%m%d-%H) \
  --incremental-basedir=/backup/full/$(date +%Y%m%d)-00

# --incremental-basedir: 기준이 되는 백업 디렉토리
```

### 5.2 증분 백업 체인

```bash
# 1. Full Backup (일요일 00시)
xtrabackup --backup \
  --target-dir=/backup/full/20240101-00

# 2. 첫 번째 증분 (월요일 01시)
xtrabackup --backup \
  --target-dir=/backup/inc/20240101-01 \
  --incremental-basedir=/backup/full/20240101-00

# 3. 두 번째 증분 (월요일 02시)
xtrabackup --backup \
  --target-dir=/backup/inc/20240101-02 \
  --incremental-basedir=/backup/full/20240101-00

# 주의: 모든 증분이 Full을 기준으로 함 (Differential 방식)
```

### 5.3 LSN 확인

```bash
# Full Backup의 LSN
cat /backup/full/20240101-00/xtrabackup_checkpoints
# to_lsn = 100000

# Incremental Backup의 LSN
cat /backup/inc/20240101-01/xtrabackup_checkpoints
# from_lsn = 100000  (Full의 to_lsn과 일치해야 함)
# to_lsn = 150000
```

**LSN 불일치 시 복원 불가!**

---

## 6. 복원 (Restore)

### 6.1 복원 프로세스

```
1. MySQL 중지
2. 기존 데이터 백업
3. Prepare (Full)
4. Prepare (Incremental)
5. Copy-back
6. 권한 설정
7. MySQL 시작
```

### 6.2 Full Backup만 복원

```bash
# 1. MySQL 중지
systemctl stop mysqld

# 2. 기존 데이터 백업
mv /var/lib/mysql /var/lib/mysql_backup_$(date +%Y%m%d)

# 3. Prepare (트랜잭션 로그 적용)
xtrabackup --prepare \
  --target-dir=/backup/full/20240101-00

# 4. Copy-back (데이터 복사)
xtrabackup --copy-back \
  --target-dir=/backup/full/20240101-00

# 5. 권한 설정
chown -R mysql:mysql /var/lib/mysql

# 6. MySQL 시작
systemctl start mysqld
```

### 6.3 Full + Incremental 복원

```bash
# 1. MySQL 중지
systemctl stop mysqld

# 2. 기존 데이터 백업
mv /var/lib/mysql /var/lib/mysql_backup_$(date +%Y%m%d)

# 3. Full Backup Prepare (--apply-log-only 필수!)
xtrabackup --prepare --apply-log-only \
  --target-dir=/backup/full/20240101-00

# 4. Incremental Prepare (마지막 증분 제외하고 --apply-log-only)
xtrabackup --prepare --apply-log-only \
  --target-dir=/backup/full/20240101-00 \
  --incremental-dir=/backup/inc/20240101-01

# 5. 마지막 Incremental Prepare (--apply-log-only 제거!)
xtrabackup --prepare \
  --target-dir=/backup/full/20240101-00 \
  --incremental-dir=/backup/inc/20240101-02

# 6. Copy-back
xtrabackup --copy-back \
  --target-dir=/backup/full/20240101-00

# 7. 권한 설정
chown -R mysql:mysql /var/lib/mysql

# 8. MySQL 시작
systemctl start mysqld
```

**중요**: 
- 마지막 증분을 제외한 모든 prepare에 `--apply-log-only` 사용
- 마지막 증분에는 `--apply-log-only` 제거

### 6.4 복원 검증

```bash
# MySQL 접속 확인
mysql -u root -p -e "SELECT VERSION();"

# 데이터 확인
mysql -u root -p -e "SHOW DATABASES;"

# 에러 로그 확인
tail -f /var/log/mysqld.log
```

---

## 7. 자동화 스크립트

### 7.1 설정 파일

```bash
# /etc/xtrabackup/backup.conf
cat > /etc/xtrabackup/backup.conf << 'EOF'
# XtraBackup 설정 파일

# 데이터베이스 접속 정보
DB_USER="backup"
DB_PASS_FILE="/etc/xtrabackup/.backup_password"

# 백업 디렉토리
BACKUP_BASE_DIR="/backup"
FULL_BACKUP_DIR="${BACKUP_BASE_DIR}/full"
INC_BACKUP_DIR="${BACKUP_BASE_DIR}/inc"
RESTORE_SCRIPT_DIR="${BACKUP_BASE_DIR}/restore"

# MySQL 데이터 디렉토리
MYSQL_DATA_DIR="/var/lib/mysql"
MYSQL_LOG_DIR="/var/log/mysql"

# 백업 설정
FULL_BACKUP_HOUR="00"  # Full Backup 시간 (00 = 매일 00시)
PARALLEL_THREADS=4
COMPRESS_THREADS=4

# 보관 정책
FULL_RETENTION_DAYS=7
INC_RETENTION_DAYS=7

# 디스크 사용률 임계값 (%)
DISK_THRESHOLD=90

# 로그 파일
LOG_DIR="/var/log/xtrabackup"
FULL_LOG="${LOG_DIR}/full.log"
INC_LOG="${LOG_DIR}/inc.log"
EOF

# 패스워드 파일 생성 (보안)
mkdir -p /etc/xtrabackup
echo "SecurePassword123!" > /etc/xtrabackup/.backup_password
chmod 600 /etc/xtrabackup/.backup_password
```

### 7.2 Full Backup 스크립트

```bash
#!/bin/bash
# /usr/local/bin/xtrabackup-full.sh
# Full Backup Script
# Created: 2024-01-01
# Modified: 2024-01-11

set -euo pipefail

# 설정 파일 로드
source /etc/xtrabackup/backup.conf

# 로그 디렉토리 생성
mkdir -p "${LOG_DIR}"
mkdir -p "${FULL_BACKUP_DIR}"
mkdir -p "${RESTORE_SCRIPT_DIR}"

# 변수 설정
BACKUP_DATE=$(date '+%Y%m%d-%H')
BACKUP_DIR="${FULL_BACKUP_DIR}/${BACKUP_DATE}"
DB_PASS=$(cat "${DB_PASS_FILE}")
LOG_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 로깅 함수
log() {
    echo "[${LOG_DATE}] $*" | tee -a "${FULL_LOG}"
}

# 에러 핸들러
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 디스크 공간 체크
check_disk_space() {
    local usage=$(df -h "${BACKUP_BASE_DIR}" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "${usage}" -ge "${DISK_THRESHOLD}" ]; then
        error_exit "Disk usage ${usage}% exceeds threshold ${DISK_THRESHOLD}%"
    fi
    log "Disk usage: ${usage}%"
}

# 백업 디렉토리 확인
check_backup_dir() {
    if [ -d "${BACKUP_DIR}" ]; then
        log "Backup directory already exists: ${BACKUP_DIR}"
        mv "${BACKUP_DIR}" "${BACKUP_DIR}_OLD_$(date +%Y%m%d%H%M%S)"
    fi
}

# Full Backup 실행
perform_backup() {
    log "Starting full backup to ${BACKUP_DIR}"
    
    xtrabackup \
        --user="${DB_USER}" \
        --password="${DB_PASS}" \
        --backup \
        --parallel="${PARALLEL_THREADS}" \
        --target-dir="${BACKUP_DIR}" \
        >> "${FULL_LOG}" 2>&1
    
    local exit_code=$?
    if [ ${exit_code} -eq 0 ]; then
        log "Full backup completed successfully"
    else
        error_exit "Full backup failed with exit code ${exit_code}"
    fi
}

# 백업 검증
verify_backup() {
    if [ ! -f "${BACKUP_DIR}/xtrabackup_checkpoints" ]; then
        error_exit "Backup verification failed: xtrabackup_checkpoints not found"
    fi
    
    local backup_type=$(grep "backup_type" "${BACKUP_DIR}/xtrabackup_checkpoints" | awk '{print $3}')
    local from_lsn=$(grep "from_lsn" "${BACKUP_DIR}/xtrabackup_checkpoints" | awk '{print $3}')
    
    if [ "${backup_type}" != "full-backuped" ]; then
        error_exit "Backup type mismatch: expected 'full-backuped', got '${backup_type}'"
    fi
    
    if [ "${from_lsn}" != "0" ]; then
        error_exit "Full backup from_lsn should be 0, got ${from_lsn}"
    fi
    
    log "Backup verification passed"
}

# 이전 백업 압축
compress_old_backup() {
    local yesterday=$(date -d '1 day ago' '+%Y%m%d')-00
    local old_backup="${FULL_BACKUP_DIR}/${yesterday}"
    
    if [ -d "${old_backup}" ]; then
        log "Compressing old backup: ${old_backup}"
        tar czf "${old_backup}.tar.gz" -C "${FULL_BACKUP_DIR}" "${yesterday}" \
            && rm -rf "${old_backup}" \
            && log "Old backup compressed successfully"
    fi
}

# 오래된 백업 삭제
cleanup_old_backups() {
    log "Cleaning up backups older than ${FULL_RETENTION_DAYS} days"
    
    find "${FULL_BACKUP_DIR}" -name "*.tar.gz" -type f -mtime +${FULL_RETENTION_DAYS} -delete
    
    log "Cleanup completed"
}

# 복원 스크립트 생성
generate_restore_script() {
    local restore_script="${RESTORE_SCRIPT_DIR}/restore-${BACKUP_DATE}.sh"
    
    cat > "${restore_script}" << 'RESTORE_EOF'
#!/bin/bash
# Auto-generated restore script
# Backup Date: BACKUP_DATE_PLACEHOLDER

set -euo pipefail

# 설정
RESTORE_FULL_DATE="BACKUP_DATE_PLACEHOLDER"
BACKUP_BASE_DIR="/backup"
MYSQL_DATA_DIR="/var/lib/mysql"

# 10초 대기 (취소 가능)
echo "⚠️  WARNING: This will restore MySQL to ${RESTORE_FULL_DATE}"
echo "⚠️  Current data will be backed up to ${MYSQL_DATA_DIR}_backup_$(date +%Y%m%d%H%M%S)"
echo ""
echo "Press Ctrl+C within 10 seconds to cancel..."

for i in {10..1}; do
    echo -n "${i}... "
    sleep 1
done
echo ""
echo "Starting restore..."

# MySQL 중지
systemctl stop mysqld || { echo "Failed to stop MySQL"; exit 1; }

# 기존 데이터 백업
if [ -d "${MYSQL_DATA_DIR}" ]; then
    mv "${MYSQL_DATA_DIR}" "${MYSQL_DATA_DIR}_backup_$(date +%Y%m%d%H%M%S)"
fi

# Prepare
xtrabackup --prepare \
    --target-dir="${BACKUP_BASE_DIR}/full/${RESTORE_FULL_DATE}"

# Copy-back
xtrabackup --copy-back \
    --target-dir="${BACKUP_BASE_DIR}/full/${RESTORE_FULL_DATE}"

# 권한 설정
chown -R mysql:mysql "${MYSQL_DATA_DIR}"

# MySQL 시작
systemctl start mysqld

echo "✅ Restore completed successfully"
RESTORE_EOF

    sed -i "s/BACKUP_DATE_PLACEHOLDER/${BACKUP_DATE}/g" "${restore_script}"
    chmod 700 "${restore_script}"
    
    log "Restore script generated: ${restore_script}"
}

# 메인 실행
main() {
    log "========================================="
    log "Full Backup Started"
    
    check_disk_space
    check_backup_dir
    perform_backup
    verify_backup
    compress_old_backup
    cleanup_old_backups
    generate_restore_script
    
    log "Full Backup Completed Successfully"
    log "========================================="
}

# 실행
main
```

### 7.3 Incremental Backup 스크립트

```bash
#!/bin/bash
# /usr/local/bin/xtrabackup-incremental.sh
# Incremental Backup Script

set -euo pipefail

# 설정 파일 로드
source /etc/xtrabackup/backup.conf

# 로그 디렉토리 생성
mkdir -p "${LOG_DIR}"
mkdir -p "${INC_BACKUP_DIR}"

# 변수 설정
BACKUP_DATE=$(date '+%Y%m%d-%H')
FULL_DATE=$(date '+%Y%m%d')-00
BACKUP_DIR="${INC_BACKUP_DIR}/${BACKUP_DATE}"
BASEDIR="${FULL_BACKUP_DIR}/${FULL_DATE}"
DB_PASS=$(cat "${DB_PASS_FILE}")
LOG_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 로깅 함수
log() {
    echo "[${LOG_DATE}] $*" | tee -a "${INC_LOG}"
}

error_exit() {
    log "ERROR: $1"
    exit 1
}

# Full Backup 존재 확인
check_base_backup() {
    if [ ! -d "${BASEDIR}" ]; then
        error_exit "Base backup not found: ${BASEDIR}"
    fi
    
    if [ ! -f "${BASEDIR}/xtrabackup_checkpoints" ]; then
        error_exit "Base backup checkpoints not found"
    fi
    
    log "Base backup found: ${BASEDIR}"
}

# 디스크 공간 체크
check_disk_space() {
    local usage=$(df -h "${BACKUP_BASE_DIR}" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "${usage}" -ge "${DISK_THRESHOLD}" ]; then
        error_exit "Disk usage ${usage}% exceeds threshold ${DISK_THRESHOLD}%"
    fi
    log "Disk usage: ${usage}%"
}

# Incremental Backup 실행
perform_backup() {
    log "Starting incremental backup to ${BACKUP_DIR}"
    
    xtrabackup \
        --user="${DB_USER}" \
        --password="${DB_PASS}" \
        --backup \
        --parallel="${PARALLEL_THREADS}" \
        --target-dir="${BACKUP_DIR}" \
        --incremental-basedir="${BASEDIR}" \
        >> "${INC_LOG}" 2>&1
    
    local exit_code=$?
    if [ ${exit_code} -eq 0 ]; then
        log "Incremental backup completed successfully"
    else
        error_exit "Incremental backup failed with exit code ${exit_code}"
    fi
}

# LSN 검증
verify_lsn() {
    local base_to_lsn=$(grep "to_lsn" "${BASEDIR}/xtrabackup_checkpoints" | awk '{print $3}')
    local inc_from_lsn=$(grep "from_lsn" "${BACKUP_DIR}/xtrabackup_checkpoints" | awk '{print $3}')
    
    if [ "${base_to_lsn}" != "${inc_from_lsn}" ]; then
        error_exit "LSN mismatch! Base to_lsn: ${base_to_lsn}, Inc from_lsn: ${inc_from_lsn}"
    fi
    
    log "LSN verification passed (LSN: ${base_to_lsn})"
}

# 오래된 증분 백업 삭제
cleanup_old_backups() {
    log "Cleaning up incremental backups older than ${INC_RETENTION_DAYS} days"
    
    find "${INC_BACKUP_DIR}" -type d -mtime +${INC_RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true
    
    log "Cleanup completed"
}

# 복원 스크립트 생성 (Full + Incremental)
generate_restore_script() {
    local restore_script="${RESTORE_SCRIPT_DIR}/restore-${BACKUP_DATE}.sh"
    
    cat > "${restore_script}" << 'RESTORE_EOF'
#!/bin/bash
# Auto-generated restore script (Full + Incremental)
# Backup Date: BACKUP_DATE_PLACEHOLDER

set -euo pipefail

# 설정
RESTORE_DATE="BACKUP_DATE_PLACEHOLDER"
RESTORE_FULL_DATE="FULL_DATE_PLACEHOLDER"
BACKUP_BASE_DIR="/backup"
MYSQL_DATA_DIR="/var/lib/mysql"

echo "⚠️  WARNING: This will restore MySQL to ${RESTORE_DATE}"
echo "⚠️  Using Full: ${RESTORE_FULL_DATE}"
echo "⚠️  Using Incremental: ${RESTORE_DATE}"
echo ""
echo "Press Ctrl+C within 10 seconds to cancel..."

for i in {10..1}; do
    echo -n "${i}... "
    sleep 1
done
echo ""

# MySQL 중지
systemctl stop mysqld || { echo "Failed to stop MySQL"; exit 1; }

# 기존 데이터 백업
if [ -d "${MYSQL_DATA_DIR}" ]; then
    mv "${MYSQL_DATA_DIR}" "${MYSQL_DATA_DIR}_backup_$(date +%Y%m%d%H%M%S)"
fi

# Prepare Full (--apply-log-only)
echo "Preparing full backup..."
xtrabackup --prepare --apply-log-only \
    --target-dir="${BACKUP_BASE_DIR}/full/${RESTORE_FULL_DATE}"

# Prepare Incremental (마지막이므로 --apply-log-only 제거)
echo "Preparing incremental backup..."
xtrabackup --prepare \
    --target-dir="${BACKUP_BASE_DIR}/full/${RESTORE_FULL_DATE}" \
    --incremental-dir="${BACKUP_BASE_DIR}/inc/${RESTORE_DATE}"

# Copy-back
echo "Copying data back..."
xtrabackup --copy-back \
    --target-dir="${BACKUP_BASE_DIR}/full/${RESTORE_FULL_DATE}"

# 권한 설정
chown -R mysql:mysql "${MYSQL_DATA_DIR}"

# MySQL 시작
systemctl start mysqld

echo "✅ Restore completed successfully"
RESTORE_EOF

    sed -i "s/BACKUP_DATE_PLACEHOLDER/${BACKUP_DATE}/g" "${restore_script}"
    sed -i "s/FULL_DATE_PLACEHOLDER/${FULL_DATE}/g" "${restore_script}"
    chmod 700 "${restore_script}"
    
    log "Restore script generated: ${restore_script}"
}

# 메인 실행
main() {
    log "========================================="
    log "Incremental Backup Started"
    
    check_base_backup
    check_disk_space
    perform_backup
    verify_lsn
    cleanup_old_backups
    generate_restore_script
    
    log "Incremental Backup Completed Successfully"
    log "========================================="
}

# 실행
main
```

### 7.4 Cron 설정

```bash
# crontab -e

# Full Backup: 매일 00시
0 0 * * * /usr/local/bin/xtrabackup-full.sh

# Incremental Backup: 매시간 (00시 제외)
0 1-23 * * * /usr/local/bin/xtrabackup-incremental.sh

# 또는 주 1회 Full, 나머지는 Incremental
0 0 * * 0 /usr/local/bin/xtrabackup-full.sh      # 일요일
0 * * * 1-6 /usr/local/bin/xtrabackup-incremental.sh  # 월-토
```

### 7.5 스크립트 설치

```bash
# 스크립트 복사
chmod +x /usr/local/bin/xtrabackup-full.sh
chmod +x /usr/local/bin/xtrabackup-incremental.sh

# 설정 파일 권한
chmod 600 /etc/xtrabackup/backup.conf
chmod 600 /etc/xtrabackup/.backup_password

# 디렉토리 생성
mkdir -p /backup/{full,inc,restore}
mkdir -p /var/log/xtrabackup

# 테스트 실행
/usr/local/bin/xtrabackup-full.sh
```

---

## 8. 트러블슈팅

### 8.1 일반적인 에러

#### 에러: "Failed to connect to MySQL server"

```bash
# 원인: 접속 정보 오류
# 해결:
mysql -u backup -p  # 수동 접속 테스트

# 권한 확인
SHOW GRANTS FOR 'backup'@'localhost';
```

#### 에러: "Cannot create file"

```bash
# 원인: 디스크 공간 부족 또는 권한 문제
# 해결:
df -h  # 디스크 공간 확인
ls -ld /backup  # 권한 확인
```

#### 에러: "LSN mismatch"

```bash
# 원인: Full Backup과 Incremental Backup의 LSN 불일치
# 해결: Full Backup부터 다시 수행

# LSN 확인
cat /backup/full/20240101-00/xtrabackup_checkpoints | grep to_lsn
cat /backup/inc/20240101-01/xtrabackup_checkpoints | grep from_lsn
# 두 값이 일치해야 함
```

#### 에러: "InnoDB: Operating system error number 2"

```bash
# 원인: 파일 또는 디렉토리 없음
# 해결:
# 1. 데이터 디렉토리 확인
ls -la /var/lib/mysql

# 2. my.cnf 확인
cat /etc/my.cnf | grep datadir

# 3. 권한 확인
chown -R mysql:mysql /var/lib/mysql
```

### 8.2 복원 실패 시 대처

```bash
# 1. 에러 로그 확인
tail -100 /var/log/mysqld.log

# 2. 백업 무결성 확인
xtrabackup --prepare --target-dir=/backup/full/20240101-00

# 3. 기존 데이터로 롤백
systemctl stop mysqld
rm -rf /var/lib/mysql
mv /var/lib/mysql_backup_20240101 /var/lib/mysql
systemctl start mysqld
```

### 8.3 binlog 관련 에러

#### 에러: "unknown variable 'default-character-set=utf8mb4'"

```bash
# 원인: mysqlbinlog가 [client] 섹션의 설정을 읽음
# 해결: my.cnf 수정

# /etc/my.cnf
[client]
# default-character-set=utf8mb4  # 주석 처리

[mysql]
default-character-set=utf8mb4  # 여기로 이동
```

### 8.4 성능 문제

#### 백업이 너무 느림

```bash
# 해결 1: 병렬 처리 증가
xtrabackup --backup --parallel=8 --target-dir=/backup/full/...

# 해결 2: 압축 사용
xtrabackup --backup --compress --compress-threads=4 --target-dir=/backup/full/...

# 해결 3: 네트워크 백업 시 대역폭 제한 해제
xtrabackup --backup --throttle=0 --target-dir=/backup/full/...
```

#### 디스크 I/O 과부하

```bash
# 해결: I/O 제한 설정 (MB/s)
xtrabackup --backup --throttle=100 --target-dir=/backup/full/...
```

### 8.5 디버깅

```bash
# 상세 로그 출력
xtrabackup --backup --target-dir=/backup/test --verbose

# 특정 테이블만 백업 (테스트용)
xtrabackup --backup \
    --tables="mydb.mytable" \
    --target-dir=/backup/test

# Dry-run (실제 백업 없이 테스트)
xtrabackup --backup --target-dir=/backup/test --dry-run
```

---

## 9. 베스트 프랙티스

### 9.1 보안

#### 패스워드 관리

```bash
# ❌ 나쁜 예: 평문 패스워드
xtrabackup --user=backup --password='MyPassword123' --backup

# ✅ 좋은 예: 파일로 관리
echo "MyPassword123" > /etc/xtrabackup/.password
chmod 600 /etc/xtrabackup/.password

xtrabackup --user=backup --password=$(cat /etc/xtrabackup/.password) --backup

# ✅ 더 좋은 예: MySQL 설정 파일 사용
# /etc/xtrabackup/my.cnf
[xtrabackup]
user=backup
password=MyPassword123

xtrabackup --defaults-file=/etc/xtrabackup/my.cnf --backup
chmod 600 /etc/xtrabackup/my.cnf
```

#### 백업 파일 암호화

```bash
# 백업 시 암호화
xtrabackup --backup \
    --encrypt=AES256 \
    --encrypt-key-file=/etc/xtrabackup/encryption.key \
    --target-dir=/backup/encrypted

# 복원 시 복호화
xtrabackup --decrypt=AES256 \
    --encrypt-key-file=/etc/xtrabackup/encryption.key \
    --target-dir=/backup/encrypted
```

### 9.2 백업 검증

#### 정기적인 복원 테스트

```bash
#!/bin/bash
# 매주 테스트 서버에서 복원 테스트

# 1. 백업 파일 복사
rsync -av production:/backup/ /backup/

# 2. 테스트 MySQL 인스턴스에 복원
systemctl stop mysqld-test
rm -rf /var/lib/mysql-test/*

xtrabackup --prepare --target-dir=/backup/full/latest
xtrabackup --copy-back --target-dir=/backup/full/latest \
    --datadir=/var/lib/mysql-test

chown -R mysql:mysql /var/lib/mysql-test
systemctl start mysqld-test

# 3. 데이터 검증
mysql -u root -p -e "SELECT COUNT(*) FROM mydb.important_table;"
```

#### 백업 무결성 체크

```bash
# MD5 체크섬 생성
find /backup/full/20240101-00 -type f -exec md5sum {} \; > /backup/full/20240101-00.md5

# 체크섬 검증
cd /backup/full/20240101-00
md5sum -c ../20240101-00.md5
```

### 9.3 모니터링

#### 백업 성공/실패 알림

```bash
#!/bin/bash
# 백업 스크립트에 추가

send_alert() {
    local status=$1
    local message=$2
    
    # 이메일 알림
    echo "${message}" | mail -s "XtraBackup ${status}" admin@example.com
    
    # Slack 알림
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"XtraBackup ${status}: ${message}\"}" \
        https://hooks.slack.com/services/YOUR/WEBHOOK/URL
}

# 백업 실행
if /usr/local/bin/xtrabackup-full.sh; then
    send_alert "SUCCESS" "Full backup completed at $(date)"
else
    send_alert "FAILED" "Full backup failed at $(date)"
fi
```

#### 백업 크기 모니터링

```bash
#!/bin/bash
# 백업 크기 추적

BACKUP_DIR="/backup/full/$(date +%Y%m%d)-00"
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | awk '{print $1}')

echo "$(date '+%Y-%m-%d %H:%M:%S'),${BACKUP_SIZE}" >> /var/log/xtrabackup/backup_size.log

# 그래프 생성 (gnuplot 사용)
gnuplot << EOF
set terminal png size 800,600
set output '/var/www/html/backup_size.png'
set datafile separator ","
set xdata time
set timefmt "%Y-%m-%d %H:%M:%S"
set format x "%m/%d"
set xlabel "Date"
set ylabel "Backup Size"
plot '/var/log/xtrabackup/backup_size.log' using 1:2 with lines title 'Backup Size'
EOF
```

### 9.4 스토리지 최적화

#### 압축 백업

```bash
# 압축 백업 (50-70% 용량 절감)
xtrabackup --backup \
    --compress \
    --compress-threads=4 \
    --target-dir=/backup/compressed

# 압축 해제 (복원 전)
xtrabackup --decompress --target-dir=/backup/compressed
```

#### 증분 백업 전략

```bash
# 시나리오 1: 매시간 증분 (24개 파일/일)
# - 백업 시간: 짧음
# - 복원 시간: 김 (24개 파일 처리)
# - 용량: 작음

# 시나리오 2: 6시간마다 증분 (4개 파일/일)
# - 백업 시간: 중간
# - 복원 시간: 중간 (4개 파일 처리)
# - 용량: 중간

# 권장: 데이터 변경량에 따라 조정
# - 변경량 많음: 자주 백업 (매시간)
# - 변경량 적음: 덜 자주 백업 (6시간)
```

### 9.5 재해 복구 (DR)

#### 원격 백업

```bash
#!/bin/bash
# 백업을 원격 서버로 전송

# 1. 로컬 백업
/usr/local/bin/xtrabackup-full.sh

# 2. 원격 서버로 rsync
rsync -avz --delete \
    /backup/ \
    backup-server:/remote-backup/mysql/ \
    --exclude='*.log'

# 3. S3로 업로드 (선택)
aws s3 sync /backup/ s3://my-backup-bucket/mysql/ \
    --storage-class GLACIER \
    --exclude='*.log'
```

#### 다중 백업 보관

```
┌─────────────────────────────────────────┐
│         백업 보관 전략 (3-2-1 규칙)        │
├─────────────────────────────────────────┤
│                                          │
│  3개의 복사본                             │
│  ├─ 원본 (프로덕션 DB)                    │
│  ├─ 로컬 백업 (/backup)                  │
│  └─ 원격 백업 (백업 서버 또는 S3)          │
│                                          │
│  2개의 다른 미디어                         │
│  ├─ 로컬 디스크                           │
│  └─ 클라우드 스토리지                      │
│                                          │
│  1개는 오프사이트                          │
│  └─ 다른 지역의 S3 또는 백업 서버          │
│                                          │
└─────────────────────────────────────────┘
```

### 9.6 성능 튜닝

#### 백업 성능 최적화

```bash
# 1. 병렬 처리 (CPU 코어 수에 맞춰 조정)
xtrabackup --backup --parallel=8

# 2. 버퍼 크기 증가
xtrabackup --backup --use-memory=4G

# 3. I/O 스레드 증가
xtrabackup --backup --read-threads=4

# 4. 압축 레벨 조정 (1=빠름, 9=높은 압축률)
xtrabackup --backup --compress --compress-level=1

# 종합 예시
xtrabackup --backup \
    --parallel=8 \
    --use-memory=4G \
    --compress \
    --compress-threads=4 \
    --compress-level=3 \
    --target-dir=/backup/optimized
```

#### 복원 성능 최적화

```bash
# 1. 병렬 복원
xtrabackup --copy-back --parallel=8

# 2. 압축 해제 병렬 처리
xtrabackup --decompress --parallel=8

# 3. 메모리 증가
xtrabackup --prepare --use-memory=8G
```

### 9.7 특수 상황 처리

#### 특정 데이터베이스만 백업

```bash
# 백업
xtrabackup --backup \
    --databases="db1 db2 db3" \
    --target-dir=/backup/partial

# 주의: 복원 시 전체 복원 필요
# 특정 DB만 복원은 mysqldump 권장
```

#### 특정 테이블 제외

```bash
# 로그 테이블 제외
xtrabackup --backup \
    --tables-exclude="^mydb\.log_.*" \
    --target-dir=/backup/exclude-logs
```

#### Point-in-Time Recovery (PITR)

```bash
# 1. 백업 복원
xtrabackup --copy-back --target-dir=/backup/full/20240101-00

# 2. MySQL 시작
systemctl start mysqld

# 3. binlog 위치 확인
cat /backup/full/20240101-00/xtrabackup_binlog_info
# mysql-bin.000123    456789

# 4. binlog 적용 (특정 시점까지)
mysqlbinlog --start-position=456789 \
    --stop-datetime="2024-01-01 15:30:00" \
    /var/lib/mysql/mysql-bin.000123 \
    | mysql -u root -p

# 5. 데이터 확인
mysql -u root -p -e "SELECT NOW(), COUNT(*) FROM mydb.mytable;"
```

### 9.8 문서화

#### 백업 정보 기록

```bash
# 백업 메타데이터 저장
cat > /backup/full/20240101-00/backup_info.txt << EOF
Backup Date: $(date)
MySQL Version: $(mysql --version)
XtraBackup Version: $(xtrabackup --version 2>&1 | head -1)
Backup Type: Full
Backup Size: $(du -sh /backup/full/20240101-00 | awk '{print $1}')
LSN: $(grep to_lsn /backup/full/20240101-00/xtrabackup_checkpoints | awk '{print $3}')
Server: $(hostname)
EOF
```

#### 복원 절차 문서

```markdown
# 복원 절차 (긴급 상황)

## 1. 상황 평가
- [ ] 장애 유형 확인
- [ ] 복원 시점 결정
- [ ] 다운타임 공지

## 2. 백업 확인
- [ ] 백업 파일 존재 확인
- [ ] LSN 일치 확인
- [ ] 디스크 공간 확인

## 3. 복원 실행
```bash
# 복원 스크립트 실행
/backup/restore/restore-20240101-05.sh
```

## 4. 검증
- [ ] MySQL 시작 확인
- [ ] 데이터 무결성 확인
- [ ] 애플리케이션 연결 테스트

## 5. 사후 조치
- [ ] 복원 보고서 작성
- [ ] 원인 분석
- [ ] 재발 방지 대책
```

---

## 10. 고급 주제

### 10.1 스트리밍 백업

```bash
# 원격 서버로 직접 스트리밍
xtrabackup --backup --stream=xbstream | \
    ssh backup-server "cat > /backup/stream.xbstream"

# 압축 + 스트리밍
xtrabackup --backup --stream=xbstream --compress | \
    ssh backup-server "cat > /backup/stream-compressed.xbstream"

# 스트림 파일 추출
xbstream -x < /backup/stream.xbstream -C /restore/
```

### 10.2 부분 백업 (Partial Backup)

```bash
# 특정 데이터베이스만 백업
xtrabackup --backup \
    --databases="production_db" \
    --target-dir=/backup/partial

# 특정 테이블만 백업
xtrabackup --backup \
    --tables="^production_db\.users$" \
    --target-dir=/backup/table
```

### 10.3 백업 검증 자동화

```bash
#!/bin/bash
# 백업 자동 검증 스크립트

BACKUP_DIR="/backup/full/$(date +%Y%m%d)-00"

# 1. 파일 존재 확인
if [ ! -f "${BACKUP_DIR}/xtrabackup_checkpoints" ]; then
    echo "ERROR: Checkpoints file not found"
    exit 1
fi

# 2. Prepare 테스트
xtrabackup --prepare --target-dir="${BACKUP_DIR}" 2>&1 | \
    grep -q "completed OK" || {
    echo "ERROR: Prepare failed"
    exit 1
}

# 3. 크기 확인 (너무 작으면 문제)
MIN_SIZE_MB=1000
ACTUAL_SIZE=$(du -sm "${BACKUP_DIR}" | awk '{print $1}')

if [ ${ACTUAL_SIZE} -lt ${MIN_SIZE_MB} ]; then
    echo "ERROR: Backup size too small (${ACTUAL_SIZE}MB < ${MIN_SIZE_MB}MB)"
    exit 1
fi

echo "✅ Backup verification passed"
```

### 10.4 클라우드 통합

#### AWS S3 백업

```bash
#!/bin/bash
# S3로 백업 업로드

BACKUP_DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/full/${BACKUP_DATE}-00"
S3_BUCKET="s3://my-mysql-backups"

# 1. 로컬 백업
xtrabackup --backup --target-dir="${BACKUP_DIR}"

# 2. 압축
tar czf "${BACKUP_DIR}.tar.gz" -C /backup/full "${BACKUP_DATE}-00"

# 3. S3 업로드
aws s3 cp "${BACKUP_DIR}.tar.gz" \
    "${S3_BUCKET}/${BACKUP_DATE}.tar.gz" \
    --storage-class STANDARD_IA

# 4. 로컬 파일 삭제 (선택)
rm -rf "${BACKUP_DIR}" "${BACKUP_DIR}.tar.gz"

# 5. 오래된 S3 백업 삭제 (30일 이상)
aws s3 ls "${S3_BUCKET}/" | \
    awk '{print $4}' | \
    while read file; do
        file_date=$(echo $file | cut -d. -f1)
        if [ $(date -d "${file_date}" +%s) -lt $(date -d '30 days ago' +%s) ]; then
            aws s3 rm "${S3_BUCKET}/${file}"
        fi
    done
```

### 10.5 복제 환경에서의 백업

```bash
# Slave에서 백업 (Master 부하 감소)
xtrabackup --backup \
    --slave-info \
    --safe-slave-backup \
    --target-dir=/backup/slave

# xtrabackup_slave_info 파일 생성됨
# CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000123', MASTER_LOG_POS=456789
```

---

## 11. 체크리스트

### 백업 체크리스트

- [ ] XtraBackup 버전이 MySQL 버전과 일치
- [ ] 백업 전용 사용자 생성 및 권한 부여
- [ ] 백업 디렉토리 생성 및 권한 설정
- [ ] 디스크 공간 충분 (DB 크기의 2배 이상)
- [ ] 백업 스크립트 테스트 완료
- [ ] Cron 작업 등록
- [ ] 로그 로테이션 설정
- [ ] 알림 설정 (이메일/Slack)
- [ ] 백업 검증 스크립트 작성
- [ ] 복원 절차 문서화

### 복원 체크리스트

- [ ] 복원 시점 결정
- [ ] 백업 파일 존재 및 무결성 확인
- [ ] LSN 일치 확인 (증분 백업 시)
- [ ] 디스크 공간 확인
- [ ] 기존 데이터 백업
- [ ] 다운타임 공지
- [ ] 복원 스크립트 실행
- [ ] MySQL 시작 확인
- [ ] 데이터 무결성 검증
- [ ] 애플리케이션 연결 테스트
- [ ] 복원 보고서 작성

---

## 12. 참고 자료

### 공식 문서

- [Percona XtraBackup 공식 문서](https://docs.percona.com/percona-xtrabackup/latest/)
- [MySQL 백업 및 복구](https://dev.mysql.com/doc/refman/8.0/en/backup-and-recovery.html)

### 유용한 명령어

```bash
# XtraBackup 버전 확인
xtrabackup --version

# MySQL 버전 확인
mysql --version

# 백업 크기 확인
du -sh /backup/*

# 백업 로그 확인
tail -f /var/log/xtrabackup/full.log

# LSN 확인
cat /backup/full/*/xtrabackup_checkpoints

# 디스크 사용량 확인
df -h /backup

# 백업 파일 개수
find /backup -type f | wc -l

# 가장 최근 백업
ls -lt /backup/full/ | head -5
```

### 성능 벤치마크

```bash
# 백업 시간 측정
time xtrabackup --backup --target-dir=/backup/test

# 복원 시간 측정
time xtrabackup --copy-back --target-dir=/backup/test

# 압축률 비교
du -sh /backup/uncompressed
du -sh /backup/compressed
```

---

## 요약

### XtraBackup 핵심 포인트

1. **물리적 백업** - 파일 복사 방식으로 빠른 백업/복원
2. **Hot Backup** - 서비스 중단 없이 백업 가능
3. **증분 백업** - 변경된 데이터만 백업하여 용량 절약
4. **LSN 기반** - Log Sequence Number로 일관성 보장
5. **버전 일치** - MySQL 버전과 XtraBackup 버전 일치 필수

### 백업 전략 요약

| 항목 | 권장 사항 |
|------|-----------|
| Full Backup | 주 1회 (일요일 00시) |
| Incremental | 매시간 또는 매일 |
| 보관 기간 | Full: 4주, Inc: 1주 |
| 압축 | 디스크 공간 부족 시 사용 |
| 원격 백업 | 필수 (DR 대비) |
| 복원 테스트 | 월 1회 이상 |

### 명령어 요약

```bash
# Full Backup
xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d)

# Incremental Backup
xtrabackup --backup --target-dir=/backup/inc/$(date +%Y%m%d-%H) \
    --incremental-basedir=/backup/full/$(date +%Y%m%d)

# Prepare (Full only)
xtrabackup --prepare --target-dir=/backup/full/20240101

# Prepare (Full + Inc)
xtrabackup --prepare --apply-log-only --target-dir=/backup/full/20240101
xtrabackup --prepare --target-dir=/backup/full/20240101 \
    --incremental-dir=/backup/inc/20240101-05

# Restore
xtrabackup --copy-back --target-dir=/backup/full/20240101
chown -R mysql:mysql /var/lib/mysql
systemctl start mysqld
```

---

**작성일**: 2024-01-11  
**버전**: 1.0  
**작성자**: Infrastructure Team

---

## 13. 실무 팁 모음

### 💡 Tip 1: 백업 전 데이터베이스 상태 확인

```bash
# 백업 전 체크리스트
mysql -u root -p << 'EOF'
-- 1. 복제 상태 확인 (Slave인 경우)
SHOW SLAVE STATUS\G

-- 2. 실행 중인 긴 쿼리 확인
SELECT * FROM information_schema.processlist 
WHERE TIME > 300 AND COMMAND != 'Sleep';

-- 3. 테이블 잠금 확인
SHOW OPEN TABLES WHERE In_use > 0;

-- 4. InnoDB 상태 확인
SHOW ENGINE INNODB STATUS\G

-- 5. 데이터베이스 크기 확인
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024 / 1024, 2) AS 'Size (GB)'
FROM information_schema.tables
GROUP BY table_schema
ORDER BY SUM(data_length + index_length) DESC;
EOF
```

### 💡 Tip 2: 백업 중 성능 영향 최소화

```bash
# 1. 낮은 우선순위로 실행 (CPU)
nice -n 19 xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d)

# 2. I/O 우선순위 낮추기
ionice -c 3 xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d)

# 3. 둘 다 적용
nice -n 19 ionice -c 3 xtrabackup --backup \
    --throttle=50 \
    --target-dir=/backup/full/$(date +%Y%m%d)

# 4. 특정 시간대에만 실행 (야간)
if [ $(date +%H) -ge 2 ] && [ $(date +%H) -le 5 ]; then
    xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d)
else
    echo "Backup skipped: not in maintenance window"
fi
```

### 💡 Tip 3: 백업 실패 시 자동 재시도

```bash
#!/bin/bash
# 백업 재시도 로직

MAX_RETRIES=3
RETRY_DELAY=300  # 5분

for i in $(seq 1 $MAX_RETRIES); do
    echo "Backup attempt $i of $MAX_RETRIES"
    
    if xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d); then
        echo "Backup succeeded on attempt $i"
        exit 0
    else
        echo "Backup failed on attempt $i"
        
        if [ $i -lt $MAX_RETRIES ]; then
            echo "Retrying in ${RETRY_DELAY} seconds..."
            sleep $RETRY_DELAY
        fi
    fi
done

echo "Backup failed after $MAX_RETRIES attempts"
exit 1
```

### 💡 Tip 4: 백업 파일 무결성 검증

```bash
#!/bin/bash
# 백업 후 자동 검증

BACKUP_DIR="/backup/full/$(date +%Y%m%d)-00"

# 1. 필수 파일 존재 확인
REQUIRED_FILES=(
    "xtrabackup_checkpoints"
    "xtrabackup_info"
    "xtrabackup_logfile"
    "backup-my.cnf"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "${BACKUP_DIR}/${file}" ]; then
        echo "ERROR: Missing required file: ${file}"
        exit 1
    fi
done

# 2. 백업 타입 확인
BACKUP_TYPE=$(grep "backup_type" "${BACKUP_DIR}/xtrabackup_checkpoints" | awk '{print $3}')
echo "Backup type: ${BACKUP_TYPE}"

# 3. LSN 범위 확인
FROM_LSN=$(grep "from_lsn" "${BACKUP_DIR}/xtrabackup_checkpoints" | awk '{print $3}')
TO_LSN=$(grep "to_lsn" "${BACKUP_DIR}/xtrabackup_checkpoints" | awk '{print $3}')
echo "LSN range: ${FROM_LSN} -> ${TO_LSN}"

# 4. 백업 크기 확인
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | awk '{print $1}')
echo "Backup size: ${BACKUP_SIZE}"

# 5. Prepare 테스트 (읽기 전용)
echo "Testing prepare..."
xtrabackup --prepare --apply-log-only --target-dir="${BACKUP_DIR}" 2>&1 | \
    grep -q "completed OK" && echo "✅ Prepare test passed" || echo "❌ Prepare test failed"
```

### 💡 Tip 5: 백업 시간 예측

```bash
#!/bin/bash
# 백업 소요 시간 예측

# 1. 데이터베이스 크기 확인
DB_SIZE_GB=$(mysql -u root -p -NBe "
    SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024 / 1024, 2)
    FROM information_schema.tables;
")

# 2. 이전 백업 시간 확인
LAST_BACKUP_TIME=$(grep "completed OK" /var/log/xtrabackup/full.log | tail -1 | awk '{print $1, $2}')
LAST_BACKUP_DURATION=$(grep "completed OK" /var/log/xtrabackup/full.log | tail -1)

# 3. 예상 시간 계산 (평균 100MB/s 기준)
ESTIMATED_SECONDS=$(echo "${DB_SIZE_GB} * 1024 / 100" | bc)
ESTIMATED_MINUTES=$(echo "${ESTIMATED_SECONDS} / 60" | bc)

echo "Database size: ${DB_SIZE_GB} GB"
echo "Estimated backup time: ${ESTIMATED_MINUTES} minutes"
echo "Last backup: ${LAST_BACKUP_TIME}"
```

### 💡 Tip 6: 증분 백업 체인 시각화

```bash
#!/bin/bash
# 백업 체인 확인 스크립트

FULL_DIR="/backup/full"
INC_DIR="/backup/inc"

echo "=== Backup Chain ==="
echo ""

# Full Backup 정보
for full in $(ls -d ${FULL_DIR}/*-00 2>/dev/null | sort); do
    full_date=$(basename ${full})
    full_lsn=$(grep "to_lsn" ${full}/xtrabackup_checkpoints | awk '{print $3}')
    full_size=$(du -sh ${full} | awk '{print $1}')
    
    echo "📦 Full Backup: ${full_date}"
    echo "   LSN: 0 -> ${full_lsn}"
    echo "   Size: ${full_size}"
    
    # 해당 Full에 연결된 Incremental 찾기
    full_date_prefix=$(echo ${full_date} | cut -d- -f1)
    
    for inc in $(ls -d ${INC_DIR}/${full_date_prefix}-* 2>/dev/null | sort); do
        inc_date=$(basename ${inc})
        inc_from=$(grep "from_lsn" ${inc}/xtrabackup_checkpoints | awk '{print $3}')
        inc_to=$(grep "to_lsn" ${inc}/xtrabackup_checkpoints | awk '{print $3}')
        inc_size=$(du -sh ${inc} | awk '{print $1}')
        
        # LSN 일치 확인
        if [ "${inc_from}" == "${full_lsn}" ]; then
            echo "   └─ 📄 Inc: ${inc_date} (LSN: ${inc_from} -> ${inc_to}, Size: ${inc_size})"
        else
            echo "   └─ ⚠️  Inc: ${inc_date} (LSN MISMATCH!)"
        fi
    done
    
    echo ""
done
```

### 💡 Tip 7: 특정 시점 복원 (PITR) 상세 가이드

```bash
#!/bin/bash
# Point-in-Time Recovery 스크립트

# 시나리오: 2024-01-15 14:30:00에 실수로 데이터 삭제
# 목표: 2024-01-15 14:29:00 시점으로 복원

RESTORE_DATETIME="2024-01-15 14:29:00"
BACKUP_DIR="/backup/full/20240115-00"

echo "=== Point-in-Time Recovery ==="
echo "Target time: ${RESTORE_DATETIME}"
echo ""

# 1. 백업 복원
echo "Step 1: Restoring backup..."
systemctl stop mysqld
rm -rf /var/lib/mysql/*

xtrabackup --prepare --target-dir="${BACKUP_DIR}"
xtrabackup --copy-back --target-dir="${BACKUP_DIR}"
chown -R mysql:mysql /var/lib/mysql

# 2. MySQL 시작
echo "Step 2: Starting MySQL..."
systemctl start mysqld

# 3. binlog 위치 확인
echo "Step 3: Checking binlog position..."
BINLOG_FILE=$(cat ${BACKUP_DIR}/xtrabackup_binlog_info | awk '{print $1}')
BINLOG_POS=$(cat ${BACKUP_DIR}/xtrabackup_binlog_info | awk '{print $2}')

echo "Binlog file: ${BINLOG_FILE}"
echo "Binlog position: ${BINLOG_POS}"

# 4. binlog 적용
echo "Step 4: Applying binlog to ${RESTORE_DATETIME}..."
mysqlbinlog \
    --start-position=${BINLOG_POS} \
    --stop-datetime="${RESTORE_DATETIME}" \
    /var/lib/mysql/${BINLOG_FILE} \
    | mysql -u root -p

echo "✅ Point-in-Time Recovery completed"
echo ""
echo "Verify data:"
echo "mysql -u root -p -e 'SELECT NOW(), COUNT(*) FROM mydb.mytable;'"
```

### 💡 Tip 8: 백업 압축률 비교

```bash
#!/bin/bash
# 다양한 압축 방법 비교

TEST_DIR="/backup/test"
BACKUP_DATE=$(date +%Y%m%d)

echo "=== Compression Comparison ==="
echo ""

# 1. 압축 없음
echo "1. No compression..."
time xtrabackup --backup --target-dir=${TEST_DIR}/no-compress
NO_COMPRESS_SIZE=$(du -sh ${TEST_DIR}/no-compress | awk '{print $1}')
echo "Size: ${NO_COMPRESS_SIZE}"
echo ""

# 2. XtraBackup 압축 (quicklz)
echo "2. XtraBackup compression..."
time xtrabackup --backup --compress --target-dir=${TEST_DIR}/xb-compress
XB_COMPRESS_SIZE=$(du -sh ${TEST_DIR}/xb-compress | awk '{print $1}')
echo "Size: ${XB_COMPRESS_SIZE}"
echo ""

# 3. gzip 압축
echo "3. gzip compression..."
time xtrabackup --backup --stream=xbstream | gzip > ${TEST_DIR}/gzip.xbstream.gz
GZIP_SIZE=$(du -sh ${TEST_DIR}/gzip.xbstream.gz | awk '{print $1}')
echo "Size: ${GZIP_SIZE}"
echo ""

# 4. 결과 요약
echo "=== Summary ==="
echo "No compression:  ${NO_COMPRESS_SIZE}"
echo "XtraBackup:      ${XB_COMPRESS_SIZE}"
echo "gzip:            ${GZIP_SIZE}"
```

### 💡 Tip 9: 백업 중 데이터베이스 변경 감지

```bash
#!/bin/bash
# 백업 중 데이터 변경량 모니터링

BACKUP_START=$(date +%s)

# 백업 시작 전 LSN
BEFORE_LSN=$(mysql -u root -p -NBe "SHOW ENGINE INNODB STATUS\G" | \
    grep "Log sequence number" | awk '{print $4}')

echo "Starting backup at $(date)"
echo "Initial LSN: ${BEFORE_LSN}"

# 백업 실행
xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d) &
BACKUP_PID=$!

# 백업 중 LSN 모니터링
while kill -0 ${BACKUP_PID} 2>/dev/null; do
    CURRENT_LSN=$(mysql -u root -p -NBe "SHOW ENGINE INNODB STATUS\G" | \
        grep "Log sequence number" | awk '{print $4}')
    
    LSN_DIFF=$((CURRENT_LSN - BEFORE_LSN))
    LSN_DIFF_MB=$((LSN_DIFF / 1024 / 1024))
    
    echo "$(date +%H:%M:%S) - LSN: ${CURRENT_LSN} (Changed: ${LSN_DIFF_MB} MB)"
    sleep 10
done

wait ${BACKUP_PID}

BACKUP_END=$(date +%s)
DURATION=$((BACKUP_END - BACKUP_START))

echo "Backup completed in ${DURATION} seconds"
```

### 💡 Tip 10: 백업 파일 암호화 (GPG)

```bash
#!/bin/bash
# GPG를 이용한 백업 암호화

BACKUP_DIR="/backup/full/$(date +%Y%m%d)-00"
ENCRYPTED_FILE="/backup/encrypted/backup-$(date +%Y%m%d).tar.gz.gpg"
GPG_RECIPIENT="backup@example.com"

# 1. 백업 실행
xtrabackup --backup --target-dir="${BACKUP_DIR}"

# 2. 압축 + 암호화
tar czf - -C /backup/full $(basename ${BACKUP_DIR}) | \
    gpg --encrypt --recipient ${GPG_RECIPIENT} \
    --output ${ENCRYPTED_FILE}

echo "Encrypted backup: ${ENCRYPTED_FILE}"

# 복호화 방법:
# gpg --decrypt backup-20240101.tar.gz.gpg | tar xzf -
```

### 💡 Tip 11: 백업 전후 Hook 스크립트

```bash
#!/bin/bash
# 백업 전후 작업 자동화

# Pre-backup hook
pre_backup() {
    echo "Running pre-backup tasks..."
    
    # 1. 임시 테이블 정리
    mysql -u root -p -e "
        SELECT CONCAT('DROP TABLE ', table_schema, '.', table_name, ';')
        FROM information_schema.tables
        WHERE table_name LIKE '%_tmp%' OR table_name LIKE 'tmp_%';
    " | mysql -u root -p
    
    # 2. 테이블 최적화 (선택적)
    # mysql -u root -p -e "OPTIMIZE TABLE mydb.large_table;"
    
    # 3. 통계 정보 업데이트
    mysql -u root -p -e "ANALYZE TABLE mydb.important_table;"
    
    echo "Pre-backup tasks completed"
}

# Post-backup hook
post_backup() {
    local exit_code=$1
    
    echo "Running post-backup tasks..."
    
    if [ ${exit_code} -eq 0 ]; then
        # 성공 시
        echo "Backup succeeded"
        
        # 백업 파일 권한 설정
        chmod 600 /backup/full/$(date +%Y%m%d)-00/*
        
        # 백업 메타데이터 저장
        cat > /backup/full/$(date +%Y%m%d)-00/backup_metadata.txt << EOF
Backup Date: $(date)
Server: $(hostname)
MySQL Version: $(mysql --version)
Database Size: $(du -sh /var/lib/mysql | awk '{print $1}')
Backup Size: $(du -sh /backup/full/$(date +%Y%m%d)-00 | awk '{print $1}')
EOF
    else
        # 실패 시
        echo "Backup failed"
        
        # 불완전한 백업 삭제
        rm -rf /backup/full/$(date +%Y%m%d)-00
    fi
    
    echo "Post-backup tasks completed"
}

# 메인 실행
pre_backup

xtrabackup --backup --target-dir=/backup/full/$(date +%Y%m%d)-00
BACKUP_EXIT_CODE=$?

post_backup ${BACKUP_EXIT_CODE}

exit ${BACKUP_EXIT_CODE}
```

### 💡 Tip 12: 백업 로그 분석

```bash
#!/bin/bash
# 백업 로그 분석 및 리포트 생성

LOG_FILE="/var/log/xtrabackup/full.log"
REPORT_FILE="/var/log/xtrabackup/backup_report_$(date +%Y%m%d).txt"

cat > ${REPORT_FILE} << 'EOF'
=== XtraBackup Report ===
Generated: $(date)

1. Recent Backups (Last 7 days)
EOF

# 최근 백업 성공/실패
echo "" >> ${REPORT_FILE}
echo "Success:" >> ${REPORT_FILE}
grep "completed OK" ${LOG_FILE} | tail -7 >> ${REPORT_FILE}

echo "" >> ${REPORT_FILE}
echo "Failures:" >> ${REPORT_FILE}
grep -i "error\|failed" ${LOG_FILE} | tail -10 >> ${REPORT_FILE}

# 평균 백업 시간
echo "" >> ${REPORT_FILE}
echo "2. Backup Duration Statistics" >> ${REPORT_FILE}
grep "completed OK" ${LOG_FILE} | tail -30 | \
    awk '{print $1, $2}' | \
    while read start end; do
        duration=$(($(date -d "$end" +%s) - $(date -d "$start" +%s)))
        echo "${duration}s"
    done | \
    awk '{sum+=$1; count++} END {print "Average: " sum/count "s"}' >> ${REPORT_FILE}

# 백업 크기 추이
echo "" >> ${REPORT_FILE}
echo "3. Backup Size Trend" >> ${REPORT_FILE}
ls -lh /backup/full/ | tail -7 >> ${REPORT_FILE}

echo "" >> ${REPORT_FILE}
echo "Report saved to: ${REPORT_FILE}"
```

### 💡 Tip 13: 빠른 복원을 위한 준비

```bash
#!/bin/bash
# 복원 시간 단축을 위한 사전 준비

BACKUP_DIR="/backup/full/$(date +%Y%m%d)-00"

# 1. 백업 직후 prepare 실행 (복원 시간 단축)
echo "Pre-preparing backup for faster restore..."
xtrabackup --prepare --target-dir="${BACKUP_DIR}"

# 2. 복원 스크립트 미리 생성 및 테스트
cat > /backup/restore/quick-restore-$(date +%Y%m%d).sh << 'RESTORE_SCRIPT'
#!/bin/bash
# Quick restore script (already prepared)

BACKUP_DIR="/backup/full/BACKUP_DATE"

# MySQL 중지
systemctl stop mysqld

# 데이터 백업
mv /var/lib/mysql /var/lib/mysql_backup_$(date +%Y%m%d%H%M%S)

# Copy-back (prepare 이미 완료됨)
xtrabackup --copy-back --target-dir="${BACKUP_DIR}"

# 권한 설정
chown -R mysql:mysql /var/lib/mysql

# MySQL 시작
systemctl start mysqld

echo "✅ Quick restore completed"
RESTORE_SCRIPT

sed -i "s/BACKUP_DATE/$(date +%Y%m%d)-00/g" /backup/restore/quick-restore-$(date +%Y%m%d).sh
chmod 700 /backup/restore/quick-restore-$(date +%Y%m%d).sh

echo "✅ Backup is ready for quick restore"
```

### 💡 Tip 14: 백업 디스크 공간 자동 관리

```bash
#!/bin/bash
# 디스크 공간 부족 시 자동 정리

BACKUP_DIR="/backup"
THRESHOLD=80  # 80% 이상 사용 시 정리

# 현재 사용률 확인
USAGE=$(df -h ${BACKUP_DIR} | awk 'NR==2 {print $5}' | sed 's/%//')

if [ ${USAGE} -ge ${THRESHOLD} ]; then
    echo "⚠️  Disk usage ${USAGE}% exceeds threshold ${THRESHOLD}%"
    echo "Starting cleanup..."
    
    # 1. 가장 오래된 압축 파일 삭제
    OLDEST_ARCHIVE=$(ls -t ${BACKUP_DIR}/full/*.tar.gz 2>/dev/null | tail -1)
    if [ -n "${OLDEST_ARCHIVE}" ]; then
        echo "Removing: ${OLDEST_ARCHIVE}"
        rm -f "${OLDEST_ARCHIVE}"
    fi
    
    # 2. 7일 이상 된 증분 백업 삭제
    find ${BACKUP_DIR}/inc -type d -mtime +7 -exec rm -rf {} + 2>/dev/null
    
    # 3. 로그 파일 정리
    find /var/log/xtrabackup -name "*.log" -mtime +30 -delete
    
    # 4. 재확인
    NEW_USAGE=$(df -h ${BACKUP_DIR} | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "Disk usage after cleanup: ${NEW_USAGE}%"
    
    if [ ${NEW_USAGE} -ge ${THRESHOLD} ]; then
        echo "❌ Still above threshold! Manual intervention required."
        # 알림 전송
        echo "Disk space critical on $(hostname)" | mail -s "Backup Disk Alert" admin@example.com
    fi
fi
```

### 💡 Tip 15: 백업 성능 벤치마크

```bash
#!/bin/bash
# 다양한 설정으로 백업 성능 테스트

RESULTS_FILE="/tmp/backup_benchmark_$(date +%Y%m%d).txt"

echo "=== XtraBackup Performance Benchmark ===" > ${RESULTS_FILE}
echo "Date: $(date)" >> ${RESULTS_FILE}
echo "" >> ${RESULTS_FILE}

# 테스트 1: 기본 설정
echo "Test 1: Default settings" >> ${RESULTS_FILE}
time xtrabackup --backup --target-dir=/backup/bench/test1 2>&1 | \
    grep "completed OK" >> ${RESULTS_FILE}

# 테스트 2: 병렬 처리
for threads in 2 4 8; do
    echo "" >> ${RESULTS_FILE}
    echo "Test: Parallel=${threads}" >> ${RESULTS_FILE}
    time xtrabackup --backup --parallel=${threads} \
        --target-dir=/backup/bench/test-p${threads} 2>&1 | \
        grep "completed OK" >> ${RESULTS_FILE}
done

# 테스트 3: 압축
echo "" >> ${RESULTS_FILE}
echo "Test: With compression" >> ${RESULTS_FILE}
time xtrabackup --backup --compress --compress-threads=4 \
    --target-dir=/backup/bench/test-compress 2>&1 | \
    grep "completed OK" >> ${RESULTS_FILE}

# 결과 요약
echo "" >> ${RESULTS_FILE}
echo "=== Size Comparison ===" >> ${RESULTS_FILE}
du -sh /backup/bench/* >> ${RESULTS_FILE}

cat ${RESULTS_FILE}
```

---
