# EC2 → S3 백업 운영 팁

EC2에서 S3로 백업할 때 비용·성능·보안·무결성 측면의 운영 팁을 정리합니다.

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 비용 최적화](#1-비용-최적화) / [2. 전송 성능](#2-전송-성능) / [3. 무결성 검증](#3-무결성-검증) |
| [4. 보안 강화](#4-보안-강화) / [5. 모니터링](#5-모니터링) / [6. 운영 편의](#6-운영-편의)           |
| [7. DB 백업 특이사항](#7-db-백업-특이사항) / [8. 우선순위 추천](#8-우선순위-추천)                  |

---

## 1. 비용 최적화

### Storage Class 선택

| Class                | 최소 보관 | 검색 비용   | 용도                                |
|----------------------|-----------|-------------|-------------------------------------|
| STANDARD             | 없음      | 없음        | 즉시 접근 필요 (7일 이내 삭제 가능) |
| STANDARD_IA          | 30일      | GB당 과금   | 30일+ 보관, 가끔 접근               |
| Glacier Instant      | 90일      | GB당 과금   | 90일+ 보관, 밀리초 검색             |
| Glacier Flexible     | 90일      | 요청당 과금 | 90일+ 보관, 수 분~수 시간 검색      |
| Glacier Deep Archive | 180일     | 요청당 과금 | 180일+ 보관, 12~48시간 검색         |

### Lifecycle 전환 예시

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-backup-bucket \
  --lifecycle-configuration '{
    "Rules": [
      {
        "ID": "backup-tiering",
        "Status": "Enabled",
        "Filter": {"Prefix": ""},
        "Transitions": [
          {"Days": 30, "StorageClass": "STANDARD_IA"},
          {"Days": 90, "StorageClass": "GLACIER"}
        ]
      }
    ]
  }'
```

### 압축 효과

| 데이터 유형                   | zstd 압축률 | 추가 압축 의미 |
|-------------------------------|-------------|----------------|
| 텍스트 로그                   | 80~95%      | ✅ 필수        |
| JSON/CSV                      | 70~90%      | ✅ 권장        |
| MSSQL .bak (비압축)           | 50~80%      | ✅ 권장        |
| MSSQL .bak (WITH COMPRESSION) | 1~5%        | ❌ 불필요      |
| 이미지/동영상                 | 0~5%        | ❌ 불필요      |
| tar.gz/zip                    | 0~3%        | ❌ 불필요      |

### Multipart Upload

```bash
# 100MB+ 파일은 자동 분할 (기본값)
# 파트 크기 조정: 대용량 파일 시 파트 수 제한(10,000) 대비
aws configure set s3.multipart_threshold 100MB
aws configure set s3.multipart_chunksize 64MB
```

---

## 2. 전송 성능

### S3 Gateway Endpoint (필수)

같은 리전 EC2 → S3 통신을 VPC 내부 경로로 변경합니다. NAT Gateway 비용 제거 + 성능 향상.

```bash
# VPC Endpoint 생성
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-0123456789abcdef0 \
  --service-name com.amazonaws.ap-northeast-2.s3 \
  --route-table-ids rtb-0123456789abcdef0

# 비용 비교 (1TB 전송/월)
# NAT Gateway: $45 (처리 비용) + $45 (데이터 비용) = $90
# Gateway Endpoint: $0
```

### 병렬 전송 설정

```bash
# 동시 업로드 수 (기본 10)
aws configure set s3.max_concurrent_requests 20

# 동시 다운로드 수
aws configure set s3.max_concurrent_requests 30

# sync 시 스레드 수 증가 효과
# 파일 수 많고 개별 크기 작을 때 효과적
```

### Transfer Acceleration

```bash
# 리전 간 전송 시 CloudFront edge 활용
aws s3api put-bucket-accelerate-configuration \
  --bucket my-backup-bucket \
  --accelerate-configuration Status=Enabled

# 사용
aws s3 cp file.tar.zst s3://my-backup-bucket/backup/ --endpoint-url https://s3-accelerate.amazonaws.com
```

🟡 같은 리전이면 Gateway Endpoint가 더 빠르고 무료입니다. Acceleration은 리전 간(Cross-region) 전송에만 사용합니다.

---

## 3. 무결성 검증

### 업로드 시 체크섬

```bash
# SHA256 체크섬 포함 업로드 (S3가 검증 + 저장)
aws s3 cp file.tar.zst s3://my-backup-bucket/backup/ \
  --checksum-algorithm SHA256

# 업로드 후 확인
aws s3api head-object \
  --bucket my-backup-bucket \
  --key backup/file.tar.zst \
  --checksum-mode ENABLED
```

### ETag 비교

```bash
# 단일 파트 업로드: ETag == MD5
LOCAL_MD5=$(md5sum file.tar.zst | awk '{print $1}')
REMOTE_ETAG=$(aws s3api head-object \
  --bucket my-backup-bucket \
  --key backup/file.tar.zst \
  --query 'ETag' --output text | tr -d '"')

if [ "$LOCAL_MD5" = "$REMOTE_ETAG" ]; then
  echo "OK: checksum match"
else
  echo "ERROR: checksum mismatch"
fi
```

🟡 Multipart 업로드 시 ETag는 MD5가 아닙니다 (`etag-N` 형식). 이 경우 `--checksum-algorithm` 사용을 권장합니다.

### 정기 복원 테스트

```bash
# 월 1회: 최신 백업 다운로드 → 무결성 확인
aws s3 cp s3://my-backup-bucket/backup/latest.tar.zst /tmp/restore_test/
tar -I zstd -tf /tmp/restore_test/latest.tar.zst > /dev/null && echo "OK" || echo "CORRUPT"
rm -rf /tmp/restore_test/
```

---

## 4. 보안 강화

### IMDSv2 강제 (SSRF 방지)

EC2 메타데이터 서비스 v1을 비활성화하여 SSRF 공격으로 Instance Profile 토큰 탈취를 방지합니다.

```bash
# 기존 인스턴스에 IMDSv2 강제 적용
aws ec2 modify-instance-metadata-options \
  --instance-id i-0123456789abcdef0 \
  --http-tokens required \
  --http-endpoint enabled
```

### S3 버킷 암호화

```bash
# SSE-S3 (기본, 추가 비용 없음)
aws s3api put-bucket-encryption \
  --bucket my-backup-bucket \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'

# SSE-KMS (키 관리 + 감사 + 키 삭제로 데이터 접근 차단 가능)
aws s3api put-bucket-encryption \
  --bucket my-backup-bucket \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "aws:kms",
          "KMSMasterKeyID": "arn:aws:kms:ap-northeast-2:222222222222:key/key-id"
        }
      }
    ]
  }'
```

### VPC Endpoint Policy (특정 버킷만 허용)

```bash
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-0123456789abcdef0 \
  --policy-document '{
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": "*",
        "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
        "Resource": [
          "arn:aws:s3:::my-backup-bucket",
          "arn:aws:s3:::my-backup-bucket/*"
        ]
      }
    ]
  }'
```

### Bucket Policy (VPC 외부 접근 거부)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyNonVPC",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-backup-bucket",
        "arn:aws:s3:::my-backup-bucket/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:sourceVpc": "vpc-0123456789abcdef0"
        }
      }
    }
  ]
}
```

---

## 5. 모니터링

### CloudWatch S3 Metrics

```bash
# 버킷 크기 추이 확인 (일 단위, 1주일)
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=my-backup-bucket Name=StorageType,Value=StandardStorage \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average \
  --output table
```

### EventBridge 알림 (업로드 실패 감지)

```bash
# S3 이벤트 → SNS 알림 (PutObject 실패 등)
aws s3api put-bucket-notification-configuration \
  --bucket my-backup-bucket \
  --notification-configuration '{
    "EventBridgeConfiguration": {}
  }'
```

### backup.status 모니터링

```bash
# Zabbix/Prometheus에서 상태 코드 수집
# 0=정상, 1~8=에러 (코드별 원인 즉시 파악)
cat /path/to/logs/backup.status

# 간단 알림 (cron으로 체크)
STATUS=$(cat /path/to/logs/backup.status 2>/dev/null || echo "9")
if [ "$STATUS" != "0" ]; then
  echo "BACKUP ALERT: status=$STATUS" | mail -s "Backup Failed" admin@example.com
fi
```

### S3 Storage Lens

계정 전체 S3 사용량·비용 대시보드입니다. 콘솔에서 활성화하면 버킷별·prefix별 용량 추이를 확인할 수 있습니다.

---

## 6. 운영 편의

### Prefix 설계

```
s3://backup-bucket/
  └── {product_name}/
      └── {year}/
          └── {server_ip}-{hostname}/
              └── {filename}.tar.zst

Example:
  game-server/2026/10.200.101.50-web01/access_log_20260701_3files.tar.zst
```

| 설계 원칙      | 이유                                     |
|----------------|------------------------------------------|
| product 최상위 | 서비스별 비용 분리, IAM 정책 prefix 제한 |
| year 2단계     | Lifecycle Rule prefix 적용, 연도별 조회  |
| server 3단계   | 장애 시 특정 서버 데이터 빠른 복원       |
| 파일명에 날짜  | ls 정렬 시 시계열 확인                   |

### 태그 기반 관리

```bash
aws s3api put-object-tagging \
  --bucket my-backup-bucket \
  --key game-server/2026/10.200.101.50-web01/data.tar.zst \
  --tagging '{
    "TagSet": [
      {"Key": "backup-source", "Value": "i-0123456789abcdef0"},
      {"Key": "retention", "Value": "30d"},
      {"Key": "environment", "Value": "production"}
    ]
  }'

# 태그 기반 비용 분석: Cost Explorer에서 S3 태그별 필터
```

### 실패 시 재시도 패턴

```python
def upload_with_retry(local_path, s3_key, retries=2, backoff=5):
    """Exponential backoff retry."""
    for attempt in range(retries + 1):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return True
        if attempt < retries:
            wait = backoff * (2 ** attempt)  # 5, 10, 20...
            logger.warning(f"retry {attempt+1}/{retries} in {wait}s")
            time.sleep(wait)
    return False
```

---

## 7. DB 백업 특이사항

### MSSQL .bak 파일

| 백업 옵션          | 파일 상태   | 추가 압축(tar.zst) | 추천                |
|--------------------|-------------|--------------------|---------------------|
| `WITH COMPRESSION` | 이미 압축됨 | ❌ (1~5% 추가)     | 그대로 업로드       |
| 압축 없음 (기본)   | 비압축      | ✅ (50~80% 감소)   | zstd 압축 후 업로드 |
| Express Edition    | 압축 미지원 | ✅ 필수            | zstd 압축 후 업로드 |

#### 압축 여부 확인 (SQL)

```sql
SELECT
    bs.database_name,
    bs.backup_size / 1024 / 1024 AS original_mb,
    bs.compressed_backup_size / 1024 / 1024 AS compressed_mb,
    CASE
      WHEN bs.compressed_backup_size < bs.backup_size THEN 'COMPRESSED'
      ELSE 'UNCOMPRESSED'
    END AS status
FROM msdb.dbo.backupset bs
ORDER BY bs.backup_finish_date DESC;
```

#### config 분기 예시

```toml
# MSSQL WITH COMPRESSION 사용 시: 압축 skip, 바로 업로드
FILE_EXTENSIONS = [".bak"]
UPLOAD_EXTENSIONS = [".bak"]

# MSSQL 비압축 시: zstd 압축 후 업로드
FILE_EXTENSIONS = [".bak"]
UPLOAD_EXTENSIONS = [".tar.zst"]
```

### MySQL/PostgreSQL

| DB         | 백업 명령               | 출력               | 추가 압축 |
|------------|-------------------------|--------------------|-----------|
| MySQL      | `mysqldump`             | 텍스트 SQL         | ✅ 80~95% |
| MySQL      | `xtrabackup --compress` | 이미 압축          | ❌        |
| PostgreSQL | `pg_dump -Fc`           | 커스텀 포맷 (압축) | ❌        |
| PostgreSQL | `pg_dump -Fp`           | 텍스트 SQL         | ✅ 80~95% |
| PostgreSQL | `pg_basebackup`         | 바이너리 (비압축)  | ✅ 40~60% |

### 공통 주의사항

| 항목                | 내용                                             |
|---------------------|--------------------------------------------------|
| 백업 중 업로드 금지 | .bak/.sql 작성 완료 후 업로드 (stability wait)   |
| 파일 잠금 체크      | 프로세스가 사용 중인 파일 skip                   |
| 대용량 단일 파일    | 5TB S3 제한, Multipart 필수                      |
| 복원 테스트         | 월 1회 다운로드 → 실제 복원 → 데이터 정합성 확인 |

### 무결성 검증 방법 (DB별)

#### MSSQL

```sql
-- 1. 빠른 검증 (복원 없이, 매일 자동)
RESTORE VERIFYONLY
FROM DISK = 'D:\backup\game_db_20260701.bak'
WITH CHECKSUM;
-- "The backup set on file 1 is valid."

-- 2. 정밀 검증 (별도 DB로 복원, 월 1회)
RESTORE DATABASE [game_db_verify]
FROM DISK = 'D:\backup\game_db_20260701.bak'
WITH MOVE 'game_db' TO 'D:\verify\game_db.mdf',
     MOVE 'game_db_log' TO 'D:\verify\game_db_log.ldf',
     RECOVERY, REPLACE;

DBCC CHECKDB ([game_db_verify]) WITH NO_INFOMSGS;
-- "CHECKDB found 0 allocation errors and 0 consistency errors."

DROP DATABASE [game_db_verify];
```

#### MySQL

```bash
# 1. xtrabackup 검증 (바이너리 백업, 매일 자동)
xtrabackup --prepare --target-dir=/backup/xtra_20260701/
# "completed OK!"

# 2. mysqldump 검증 (SQL 복원, 월 1회)
mysql -e "CREATE DATABASE game_db_verify;"
mysql game_db_verify < /backup/game_db_20260701.sql
mysqlcheck --check --databases game_db_verify
# game_db_verify.users     OK
mysql -e "DROP DATABASE game_db_verify;"
```

#### 검증 수준 비교

| DB         | 방법                               | 소요 시간       | 검증 수준          | 빈도   |
|------------|------------------------------------|-----------------|--------------------|--------|
| MSSQL      | `RESTORE VERIFYONLY WITH CHECKSUM` | 수 분           | 파일 구조 + 체크섬 | 매일   |
| MSSQL      | `RESTORE` + `DBCC CHECKDB`         | 수십 분~수 시간 | 데이터 일관성      | 월 1회 |
| MySQL      | `xtrabackup --prepare`             | 수 분           | 바이너리 일관성    | 매일   |
| MySQL      | 복원 + `mysqlcheck`                | 수십 분         | 테이블 일관성      | 월 1회 |
| PostgreSQL | `pg_restore --list` (목록 확인)    | 수 초           | 아카이브 구조      | 매일   |
| PostgreSQL | 복원 + `pg_catalog` 조회           | 수십 분         | 데이터 일관성      | 월 1회 |

### 검증 서버 구성

Live DB 서버에서 검증하면 성능 영향 + 사고 위험이 있으므로 별도 서버를 사용합니다.

#### 구성 옵션

| 옵션                       | 비용   | 속도              | 자동화    | 보안                |
|----------------------------|--------|-------------------|-----------|---------------------|
| 같은 리전 EC2 (월 2h 가동) | ~$8/월 | 빠름 (S3 전송 $0) | ✅ 스케줄 | IAM Role (키 없음)  |
| 사무실 PC                  | $0     | 회선 의존         | 수동      | 자격 증명 저장 필요 |

#### EC2 방식 흐름

```bash
# 1. EventBridge → EC2 시작 (월 1회)
aws ec2 start-instances --instance-ids i-verify-server

# 2. SSM Run Command로 검증 실행
#    S3 다운로드 → RESTORE VERIFYONLY → DBCC CHECKDB → 알림

# 3. EC2 중지
aws ec2 stop-instances --instance-ids i-verify-server
```

#### 사무실 PC 방식 주의점

| 항목          | 내용                                   |
|---------------|----------------------------------------|
| S3 전송 비용  | $0.126/GB (서울 리전, 인터넷 경유)     |
| 손익 분기     | 50GB 이상이면 EC2가 저렴               |
| 다운로드 시간 | 100Mbps 회선 → 50GB에 ~70분            |
| 자격 증명     | SSO 임시 토큰 또는 STS AssumeRole 권장 |
| 적합 상황     | 백업 < 50GB, 수동 월 1회 검증 OK       |

🟡 `RESTORE VERIFYONLY`는 Live 서버에서 실행해도 부하가 낮습니다 (디스크 읽기만). 정밀 검증(`DBCC CHECKDB`)만 별도 서버에서 실행하면 충분합니다.

---

## 8. 우선순위 추천

| 순위 | 항목                | 이유                                     | 난이도 |
|------|---------------------|------------------------------------------|--------|
| 1    | S3 Gateway Endpoint | NAT 비용 $0 + 성능 향상 (같은 리전 필수) | 낮음   |
| 2    | IMDSv2 강제         | SSRF 방지 (명령어 한 줄)                 | 낮음   |
| 3    | SSE-S3 암호화       | 저장 암호화 기본 적용 (비용 $0)          | 낮음   |
| 4    | Lifecycle 전환      | 30d IA → 90d Glacier (비용 50%+ 절감)    | 낮음   |
| 5    | 체크섬 검증         | 무결성 보장 (--checksum-algorithm 추가)  | 낮음   |
| 6    | Storage Lens + 알림 | 비용 폭증·실패 조기 감지                 | 중간   |
| 7    | VPC Endpoint Policy | 허용 버킷 제한 (보안 심화)               | 중간   |
| 8    | 정기 복원 테스트    | 백업 유효성 입증 (감사 대응)             | 중간   |

---

## 참고 자료

- AWS S3 User Guide: [docs.aws.amazon.com/AmazonS3/latest/userguide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/) — ★★★☆☆
- AWS S3 Pricing: [aws.amazon.com/s3/pricing](https://aws.amazon.com/s3/pricing/) — ★★★☆☆
- [s3_object_lock.md](s3_object_lock.md)
- [s3_cross_account_backup.md](../../99_ETC/01_AWS_jobs/s3_cross_account_backup.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-01

**마지막 업데이트**: 2026-07-01

© 2026 siasia86. Licensed under CC BY 4.0.
