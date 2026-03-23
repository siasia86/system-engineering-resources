# 백업 도구 완벽 비교 가이드

클라우드 및 로컬 백업을 위한 주요 도구들의 리소스 사용량, 비용, 장단점 비교

---

## 목차
- [도구 개요](#도구-개요)
- [리소스 사용량 비교](#리소스-사용량-비교)
- [비용 비교](#비용-비교)
- [상세 비교](#상세-비교)
- [기능 비교표](#기능-비교표)
- [시나리오별 추천](#시나리오별-추천)
- [비용 최적화 전략](#비용-최적화-전략)
- [리소스 최적화 팁](#리소스-최적화-팁)
- [모니터링 및 알림](#모니터링-및-알림)
- [복원 시간 비교](#복원-시간-비교)
- [최종 추천 요약](#최종-추천-요약)
- [실전 구성 예시](#실전-구성-예시)
- [주의사항 및 베스트 프랙티스](#주의사항-및-베스트-프랙티스)
- [자주 묻는 질문 (FAQ)](#자주-묻는-질문-faq)
- [트러블슈팅](#트러블슈팅)
- [성능 튜닝](#성능-튜닝)
- [보안 체크리스트](#보안-체크리스트)

---

## 도구 개요

| 도구 | 타입 | 주요 용도 | 플랫폼 |
|------|------|-----------|--------|
| **Restic** | 백업 | 클라우드 백업 | Linux, macOS, Windows |
| **BorgBackup** | 백업 | 로컬/SSH 백업 | Linux, macOS |
| **Rclone** | 동기화 | 클라우드 동기화 | Linux, macOS, Windows |
| **AWS CLI** | 전송 | AWS S3 전송 | Linux, macOS, Windows |
| **Duplicity** | 백업 | 암호화 백업 | Linux, macOS |
| **rsync** | 동기화 | 로컬/SSH 동기화 | Linux, macOS |

---

## 리소스 사용량 비교

### 50GB 데이터 백업 기준

| 도구 | CPU 사용률 | 메모리 사용량 | 디스크 I/O | 네트워크 효율 |
|------|-----------|--------------|-----------|--------------|
| **AWS CLI** | 5-10% | 50MB | 낮음 | 보통 (압축 없음) |
| **Restic** | 30-50% | 200-500MB | 중간 | 높음 (중복 제거) |
| **BorgBackup** | 40-60% | 100-300MB | 높음 | 매우 높음 |
| **Rclone** | 10-20% | 100-200MB | 낮음 | 보통 |
| **Duplicity** | 50-70% | 300-600MB | 높음 | 높음 (압축) |
| **rsync** | 5-15% | 30-100MB | 낮음 | 높음 (델타 전송) |

### 증분 백업 시 (5GB 변경)

| 도구 | CPU | 메모리 | 실제 전송량 | 백업 시간 |
|------|-----|--------|------------|----------|
| **AWS CLI** | 5% | 50MB | 5GB (파일 단위) | 5분 |
| **Restic** | 20-30% | 200MB | 500MB (블록 단위) | 2분 |
| **BorgBackup** | 30-40% | 150MB | 300MB (최적화) | 1분 |
| **Rclone** | 10% | 100MB | 5GB (파일 단위) | 5분 |
| **Duplicity** | 40-50% | 400MB | 1GB (압축) | 3분 |
| **rsync** | 10% | 50MB | 500MB (델타) | 2분 |

---

## 비용 비교

### 시나리오: 일 50GB 로그, 30일 보관, AWS S3 서울 리전

#### 스토리지 비용 (월)

| 도구 | 중복 제거 | 압축 | 실제 저장량 | 월 비용 |
|------|----------|------|------------|---------|
| **AWS CLI** | ❌ | ❌ | 1,500GB | $37.50 |
| **Restic** | ✅ | 제한적 | 200GB | $5.00 |
| **BorgBackup** | ✅ | ✅ | 150GB | $3.75 |
| **Rclone** | ❌ | ❌ | 1,500GB | $37.50 |
| **Duplicity** | ✅ | ✅ | 180GB | $4.50 |
| **rsync + tar.gz** | ❌ | ✅ | 500GB | $12.50 |

*S3 Standard 기준 $0.025/GB*

#### 네트워크 비용 (월)

| 도구 | 업로드 (IN) | 다운로드 (OUT) | 복원 비용 (전체) |
|------|------------|---------------|-----------------|
| **모든 도구** | $0 (무료) | $0.126/GB | $189 (1.5TB) |

*첫 100GB 무료, 이후 $0.126/GB*

#### 운영 비용

| 도구 | 인프라 필요 | 관리 복잡도 | 예상 인건비 |
|------|-----------|------------|-----------|
| **AWS CLI** | ❌ | 낮음 | 낮음 |
| **Restic** | ⚠️ 선택적 | 중간 | 중간 |
| **BorgBackup** | ✅ (SSH 서버) | 높음 | 높음 |
| **Rclone** | ❌ | 낮음 | 낮음 |
| **Duplicity** | ⚠️ 선택적 | 높음 | 높음 |
| **rsync** | ✅ (SSH 서버) | 중간 | 중간 |

---

## 상세 비교

### 1. AWS CLI (aws s3 sync/cp)

#### 장점
- ✅ **최소 리소스** (CPU 5%, 메모리 50MB)
- ✅ **설정 간단** (AWS 자격증명만)
- ✅ **안정적** (AWS 공식 도구)
- ✅ **추가 인프라 불필요**

#### 단점
- ❌ **스냅샷 없음** (시점 복원 불가)
- ❌ **중복 제거 없음** (스토리지 비용 높음)
- ❌ **파일 단위 전송** (부분 변경 비효율)
- ❌ **클라이언트 암호화 없음**

#### 적합한 경우
```bash
# 단순 동기화
aws s3 sync /var/log s3://bucket/logs

# 정적 파일 배포
aws s3 sync ./dist s3://website --delete

# 일회성 전송
aws s3 cp large-file.zip s3://bucket/
```

#### 리소스 프로파일
```
CPU: ████░░░░░░ 5%
메모리: ██░░░░░░░░ 50MB
네트워크: 원본 크기 그대로
```

---

### 2. Restic

#### 장점
- ✅ **스냅샷 기반** (여러 시점 복원)
- ✅ **중복 제거** (블록 단위, 80-90% 절약)
- ✅ **클라이언트 암호화** (AES-256)
- ✅ **다양한 백엔드** (S3, B2, Azure, GCS, SFTP)
- ✅ **자동 검증** (데이터 무결성)
- ✅ **크로스 플랫폼** (Windows 지원)

#### 단점
- ⚠️ **CPU 사용 높음** (30-50%, 암호화/중복 제거)
- ⚠️ **메모리 사용** (200-500MB, 인덱스 로드)
- ⚠️ **BorgBackup보다 느림**
- ⚠️ **압축 제한적**

#### 적합한 경우
```bash
# 클라우드 백업
restic -r s3:bucket backup /data

# 멀티 클라우드
restic -r b2:backup backup /data

# 정책 기반 정리
restic forget --keep-daily 7 --keep-weekly 4 --prune
```

#### 리소스 프로파일
```
CPU: ████████████████░░░░ 40%
메모리: ████████░░ 300MB
네트워크: 중복 제거 후 10-20%
```

#### 비용 절감 예시
```
원본: 1.5TB/월
Restic 후: 200GB/월
절감: $32.5/월 (87%)
```

---

### 3. BorgBackup

#### 장점
- ✅ **최고 성능** (가장 빠른 백업/복원)
- ✅ **최고 중복 제거** (chunk-level)
- ✅ **강력한 압축** (lz4, zstd, lzma)
- ✅ **암호화 + 압축** 동시 지원
- ✅ **원자적 백업** (중단되어도 안전)
- ✅ **낮은 메모리** (Restic보다 효율적)

#### 단점
- ❌ **클라우드 직접 미지원** (SSH 또는 rclone mount 필요)
- ❌ **Windows 미지원**
- ❌ **설정 복잡**
- ❌ **학습 곡선 높음**

#### 적합한 경우
```bash
# 로컬 백업
borg create /mnt/backup::daily-{now} /data

# SSH 백업
borg create user@server:/backup::daily /data

# S3 백업 (rclone mount)
rclone mount s3:bucket /mnt/s3 &
borg create /mnt/s3::daily /data
```

#### 리소스 프로파일
```
CPU: ████████████████████░░░░ 50%
메모리: ██████░░░░ 150MB
네트워크: 압축+중복 제거 후 5-10%
```

#### 성능 비교
```
50GB 백업:
- Restic: 45분
- BorgBackup: 25분 (1.8배 빠름)
```

---

### 4. Rclone

#### 장점
- ✅ **70+ 클라우드 지원** (최다)
- ✅ **낮은 리소스** (CPU 10-20%)
- ✅ **양방향 동기화**
- ✅ **마운트 기능** (클라우드를 로컬처럼)
- ✅ **대역폭 제어** (세밀한 네트워크 옵션)
- ✅ **GUI 제공**

#### 단점
- ❌ **스냅샷 없음** (단순 동기화)
- ❌ **중복 제거 없음**
- ❌ **압축 없음**
- ❌ **백업보다는 동기화 도구**

#### 적합한 경우
```bash
# 클라우드 간 이동
rclone sync gdrive:folder s3:bucket

# 클라우드 마운트
rclone mount s3:bucket /mnt/cloud

# 암호화 동기화
rclone sync /data crypt-remote:encrypted
```

#### 리소스 프로파일
```
CPU: ████████░░ 15%
메모리: ████░░░░░░ 150MB
네트워크: 원본 크기 그대로
```

---

### 5. Duplicity

#### 장점
- ✅ **강력한 암호화** (GPG)
- ✅ **압축 지원**
- ✅ **증분 백업**
- ✅ **다양한 백엔드**

#### 단점
- ❌ **매우 높은 CPU** (50-70%, GPG 암호화)
- ❌ **높은 메모리** (300-600MB)
- ❌ **느린 속도**
- ❌ **복잡한 복원**
- ❌ **개발 활발하지 않음**

#### 적합한 경우
```bash
# GPG 암호화 필수 시
duplicity /data s3://bucket

# 규제 준수 (강력한 암호화)
```

#### 리소스 프로파일
```
CPU: ██████████████████████░░ 60%
메모리: ████████████░░ 450MB
네트워크: 압축 후 30-50%
```

---

### 6. rsync

#### 장점
- ✅ **매우 낮은 리소스** (CPU 5-15%)
- ✅ **델타 전송** (변경 부분만)
- ✅ **안정적** (오래된 검증된 도구)
- ✅ **SSH 통합**

#### 단점
- ❌ **클라우드 미지원** (로컬/SSH만)
- ❌ **암호화 없음** (SSH 의존)
- ❌ **스냅샷 없음**
- ❌ **압축 제한적**

#### 적합한 경우
```bash
# 로컬 동기화
rsync -av /source/ /backup/

# SSH 백업
rsync -avz /data/ user@server:/backup/

# 증분 백업 (hardlink)
rsync -av --link-dest=/backup/prev /data/ /backup/new/
```

#### 리소스 프로파일
```
CPU: ██████░░░░ 10%
메모리: ██░░░░░░░░ 50MB
네트워크: 델타 전송 (효율적)
```

---

### 7. 전문 로그 수집기 (Fluent Bit, Fluentd)

#### 장점
- ✅ **비동기 전송** (애플리케이션 블로킹 없음)
- ✅ **버퍼링** (네트워크 장애 대응)
- ✅ **낮은 리소스** (CPU 5-10%, 메모리 100MB)
- ✅ **실시간 스트리밍**
- ✅ **파싱/필터링** 내장
- ✅ **다양한 출력** (S3, Elasticsearch, Kafka 등)

#### 단점
- ❌ **스냅샷 없음** (백업 도구 아님)
- ❌ **설정 복잡** (YAML/conf 파일)
- ❌ **별도 백업 필요**

#### 적합한 경우
```yaml
# Fluent Bit 설정
[OUTPUT]
    Name s3
    Match *
    bucket game-logs
    region ap-northeast-2
    total_file_size 50M
    upload_timeout 1m
    compression gzip

# 게임 서버 실시간 로그 전송
# CPU: 5-10%
# 메모리: 100MB
# 게임 영향: 없음
```

#### 리소스 프로파일
```
CPU: ██████░░░░ 8%
메모리: ████░░░░░░ 100MB
네트워크: 압축 후 전송
```

#### 게임 서버 최적 구성
```
게임 로그 → Fluent Bit → S3 (실시간)
                      ↓
                   Elasticsearch (모니터링)

+ 새벽 Restic 백업 (장기 보관)
```

---

## 기능 비교표

| 기능 | AWS CLI | Restic | BorgBackup | Rclone | Duplicity | rsync | Fluent Bit |
|------|---------|--------|------------|--------|-----------|-------|------------|
| **스냅샷** | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **중복 제거** | ❌ | ✅ | ✅ 최고 | ❌ | ❌ | ❌ | ❌ |
| **압축** | ❌ | 제한적 | ✅ 강력 | ❌ | ✅ | 제한적 | ✅ |
| **암호화** | 서버측 | ✅ | ✅ | ✅ | ✅ GPG | SSH | TLS |
| **클라우드** | S3만 | ✅ | ❌ | ✅ 최다 | ✅ | ❌ | ✅ |
| **Windows** | ✅ | ✅ | ❌ | ✅ | ⚠️ | ⚠️ | ✅ |
| **리소스** | 최저 | 중간 | 중간 | 낮음 | 높음 | 최저 | 낮음 |
| **속도** | 보통 | 보통 | 빠름 | 빠름 | 느림 | 빠름 | 빠름 |
| **설정** | 쉬움 | 쉬움 | 어려움 | 보통 | 어려움 | 쉬움 | 보통 |
| **실시간** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **버퍼링** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 시나리오별 추천

### 1. 게임 서버 로그 백업 (일 50GB)

#### 실시간 전송
```bash
# 1순위: Fluent Bit (전문 로그 수집기)
# 2순위: AWS CLI (경량)
aws s3 sync /var/log s3://bucket/realtime/

# 리소스: CPU 5%, 메모리 50MB
# 게임 영향: 거의 없음
```

#### 장기 백업
```bash
# 새벽 시간대 Restic
0 4 * * * nice -n 19 restic backup /var/log

# 리소스: CPU 30% (한가할 때)
# 비용: $5/월 (vs AWS CLI $37.5/월)
```

---

### 2. IDC → AWS 백업

#### 대용량 (TB 단위)
```bash
# BorgBackup + rclone mount
rclone mount s3:bucket /mnt/s3 &
borg create /mnt/s3::backup-{now} /data

# 최고 압축률 + 중복 제거
# 비용 절감: 90%+
```

#### 중소 규모 (GB 단위)
```bash
# Restic (간편함)
restic -r s3:bucket backup /data

# 설정 간단 + 충분한 기능
```

---

### 3. 로컬 NAS 백업

#### 최고 성능 필요
```bash
# BorgBackup
borg create /mnt/nas/backup::daily-{now} /home

# 가장 빠른 속도
# 최고 압축률
```

#### 간단한 백업
```bash
# rsync + hardlink
rsync -av --link-dest=/nas/prev /home/ /nas/new/

# 최소 리소스
# 증분 백업
```

---

### 4. 멀티 클라우드 전략

#### 동기화
```bash
# Rclone
rclone sync s3:primary b2:backup
rclone sync s3:primary gdrive:backup

# 70+ 클라우드 지원
```

#### 백업
```bash
# Restic (여러 백엔드)
restic -r s3:primary backup /data
restic -r b2:secondary backup /data

# 스냅샷 + 암호화
```

---

### 5. 규제 준수 (금융, 의료)

#### 강력한 암호화
```bash
# Restic (클라이언트 암호화)
restic -r s3:bucket backup /sensitive-data

# 또는 Duplicity (GPG)
duplicity /sensitive-data s3://bucket
```

#### 감사 추적
```bash
# Restic (검증 가능)
restic check
restic check --read-data

# 무결성 증명
```

---

### 6. 개발자 워크스테이션

#### 간단한 백업
```bash
# Restic (크로스 플랫폼)
restic -r /mnt/backup backup ~

# Windows/Mac/Linux 모두 지원
```

#### 빠른 로컬 백업
```bash
# BorgBackup (Linux/Mac)
borg create /mnt/backup::dev-{now} ~

# 최고 속도
```

---

## 비용 최적화 전략

### 1. 중복 제거 활용
```
AWS CLI: 1.5TB × $0.025 = $37.5/월
Restic: 200GB × $0.025 = $5/월
절감: $32.5/월 (87%)
```

### 2. 압축 활용
```
원본: 50GB/일 (텍스트 로그)
BorgBackup (lz4): 20GB/일
절감: 60%
```

### 3. Lifecycle 정책
```bash
# S3 Lifecycle
# 30일 후 Glacier ($0.004/GB)
# 90일 후 Deep Archive ($0.00099/GB)

# 1.5TB 기준:
# Standard: $37.5/월
# Glacier: $6/월
# Deep Archive: $1.5/월
```

### 4. 하이브리드 전략
```bash
# 최근 7일: S3 Standard (빠른 복원)
# 8-30일: S3 Glacier (저렴)
# 31일+: Deep Archive (장기 보관)

# Restic + Lifecycle
restic forget --keep-daily 7
# + S3 Lifecycle 정책
```

---

## 리소스 최적화 팁

### 1. CPU 제한
```bash
# nice (우선순위 낮춤)
nice -n 19 restic backup /data

# cgroups (CPU 할당량)
systemd-run --scope -p CPUQuota=20% restic backup /data
```

### 2. I/O 제한
```bash
# ionice (I/O 우선순위)
ionice -c 3 borg create /backup::data /data

# idle class (다른 I/O 없을 때만)
```

### 3. 네트워크 제한
```bash
# Restic
restic backup /data --limit-upload 10240  # 10MB/s

# Rclone
rclone sync /data remote: --bwlimit 10M

# BorgBackup (SSH)
borg create --remote-ratelimit 10240 /backup::data /data
```

### 4. 시간대 분리
```bash
# 업무 시간: 경량 도구
0-23 * * * aws s3 sync /data s3://bucket

# 새벽: 무거운 백업
0 4 * * * borg create /backup::daily /data
```

---

## 모니터링 및 알림

### Restic
```bash
# 상태 확인
restic stats
restic check

# 실패 알림
if ! restic backup /data; then
  curl -X POST https://hooks.slack.com/... \
    -d '{"text":"Backup failed!"}'
fi
```

### BorgBackup
```bash
# 상태
borg info /backup::latest
borg list /backup

# 검증
borg check /backup
```

### AWS CLI
```bash
# CloudWatch 메트릭
aws cloudwatch put-metric-data \
  --namespace Backup \
  --metric-name Success \
  --value 1
```

---

## 복원 시간 비교 (50GB 전체 복원)

| 도구 | 복원 시간 | 네트워크 | 비고 |
|------|----------|---------|------|
| **AWS CLI** | 30분 | 50GB | 단순 다운로드 |
| **Restic** | 40분 | 50GB | 복호화 오버헤드 |
| **BorgBackup** | 25분 | 15GB | 압축+중복 제거 |
| **Rclone** | 30분 | 50GB | 단순 다운로드 |
| **Duplicity** | 60분 | 20GB | GPG 복호화 느림 |
| **rsync** | 30분 | 50GB | 로컬/SSH만 |

---

## 최종 추천 요약

### 용도별 1순위

| 용도 | 추천 도구 | 이유 |
|------|----------|------|
| **클라우드 백업** | Restic | 기능 + 편의성 균형 |
| **로컬 백업** | BorgBackup | 최고 성능 |
| **클라우드 동기화** | Rclone | 최다 지원 |
| **단순 전송** | AWS CLI | 최소 리소스 |
| **게임 서버** | AWS CLI + Restic | 하이브리드 |
| **규제 준수** | Restic/Duplicity | 강력한 암호화 |

### 리소스별 선택

```
리소스 최소화: AWS CLI > rsync > Rclone
비용 최소화: BorgBackup > Restic > Duplicity
속도 최우선: BorgBackup > rsync > Rclone
편의성 최우선: Restic > AWS CLI > Rclone
```

---

## 실전 구성 예시

### 소규모 (개인/스타트업)
```bash
# Restic으로 통합
restic -r s3:bucket backup /data
restic forget --keep-daily 7 --prune
```

### 중규모 (중소기업)
```bash
# 실시간: Rclone
rclone sync /data s3:realtime

# 백업: Restic
restic -r s3:backup backup /data
```

### 대규모 (엔터프라이즈)
```bash
# 실시간: Fluent Bit → S3
# 백업: AWS Backup 또는 자체 시스템
# 아카이브: S3 Lifecycle → Glacier
```

---

## 주의사항 및 베스트 프랙티스

### 1. 백업 검증 필수
```bash
# 정기적 검증 (월 1회 이상)
restic check --read-data
borg check --verify-data

# 복원 테스트 (분기 1회)
restic restore latest --target /tmp/test
```

### 2. 3-2-1 백업 규칙
- **3개 복사본**: 원본 + 백업 2개
- **2개 다른 매체**: 로컬 + 클라우드
- **1개 오프사이트**: 다른 지역/클라우드

```bash
# 예시
원본: /data
백업1: 로컬 NAS (BorgBackup)
백업2: AWS S3 서울 (Restic)
백업3: AWS S3 도쿄 (Cross-Region Replication)
```

### 3. 암호화 키 관리
```bash
# Restic 비밀번호 백업
# - 비밀번호 분실 시 복원 불가능
# - 안전한 곳에 별도 보관 (1Password, Vault 등)

# 키 백업
restic key list
restic key add  # 추가 키 생성
```

### 4. 네트워크 장애 대응
```bash
# 재시도 설정
restic backup /data \
  --option s3.max-retries=10

# 타임아웃 설정
rclone sync /data remote: \
  --timeout 1h \
  --retries 10
```

### 5. 로그 보관
```bash
# 백업 로그 기록
restic backup /data 2>&1 | tee -a /var/log/backup.log

# 로그 로테이션
logrotate /etc/logrotate.d/backup
```

---

## 자주 묻는 질문 (FAQ)

### Q1. Restic과 BorgBackup 중 어떤 걸 선택해야 하나요?
**A:** 
- **클라우드 백업**: Restic (네이티브 지원)
- **로컬/NAS 백업**: BorgBackup (더 빠르고 효율적)
- **Windows 필요**: Restic (BorgBackup은 미지원)

### Q2. 게임 서버에서 Restic을 실시간으로 돌려도 되나요?
**A:** 권장하지 않습니다. CPU 30-50% 사용으로 게임 성능 저하 가능. 대신:
- 실시간: AWS CLI 또는 Fluent Bit (경량)
- 백업: Restic (새벽 시간대, nice 적용)

### Q3. 중복 제거율은 어느 정도인가요?
**A:** 데이터 타입에 따라 다름:
- **텍스트 로그**: 80-95% (변경 적음)
- **데이터베이스**: 50-70% (변경 많음)
- **미디어 파일**: 10-20% (이미 압축됨)
- **소스 코드**: 70-90% (변경 적음)

### Q4. S3 Glacier로 바로 백업할 수 있나요?
**A:** 
- Restic: Glacier 직접 지원 안 함 (Standard → Lifecycle 사용)
- AWS CLI: Glacier 직접 업로드 가능하지만 복원 느림 (3-5시간)
- 권장: Standard → Lifecycle 자동 이관

### Q5. 백업 중 파일이 변경되면 어떻게 되나요?
**A:**
- **Restic/BorgBackup**: 백업 시작 시점 기준 (일관성 보장)
- **AWS CLI/rsync**: 변경된 파일 재전송 (일관성 보장 안 됨)
- **권장**: 백업 전 스냅샷 생성 (LVM, ZFS 등)

### Q6. 여러 서버를 하나의 저장소에 백업할 수 있나요?
**A:** 가능합니다.
```bash
# Restic (서버별 태그)
server1$ restic backup /data --tag server1
server2$ restic backup /data --tag server2

# 복원 시 필터링
restic snapshots --tag server1
```

### Q7. 백업 속도를 높이려면?
**A:**
- 병렬 전송 증가: `--option s3.connections=10`
- 압축 레벨 낮춤: `borg create --compression lz4`
- 네트워크 대역폭 확인: Direct Connect/VPN 사용
- 증분 백업 활용: 첫 백업만 느림

### Q8. 비용을 더 줄이려면?
**A:**
1. S3 Intelligent-Tiering 사용 (자동 최적화)
2. Lifecycle 정책 (Glacier/Deep Archive)
3. 중복 제거 도구 사용 (Restic/BorgBackup)
4. 압축 활성화
5. 불필요한 파일 제외 (`--exclude`)

---

## 트러블슈팅

### Restic

#### 문제: "repository is already locked"
```bash
# 해결: 잠금 해제 (이전 백업 실패 시)
restic unlock

# 예방: 타임아웃 설정
timeout 2h restic backup /data
```

#### 문제: 메모리 부족
```bash
# 해결: 캐시 크기 제한
restic backup /data --cache-dir /tmp/restic-cache

# 또는 캐시 비활성화
restic backup /data --no-cache
```

### BorgBackup

#### 문제: "Failed to create/acquire the lock"
```bash
# 해결: 잠금 해제
borg break-lock /backup

# 예방: 타임아웃 설정
borg create --lock-wait 300 /backup::data /data
```

#### 문제: 저장소 손상
```bash
# 복구 시도
borg check --repair /backup
```

### AWS CLI

#### 문제: "Connection timeout"
```bash
# 해결: 재시도 및 타임아웃 설정
aws configure set s3.max_concurrent_requests 10
aws configure set s3.max_bandwidth 50MB/s
aws configure set s3.multipart_threshold 64MB
```

#### 문제: 대용량 파일 업로드 실패
```bash
# 해결: 멀티파트 업로드 크기 조정
aws s3 cp large-file.zip s3://bucket/ \
  --multipart-chunk-size-mb 100
```

---

## 성능 튜닝

### Restic
```bash
# S3 연결 수 증가
restic backup /data --option s3.connections=10

# 캐시 디렉토리 SSD로
export RESTIC_CACHE_DIR=/ssd/restic-cache
```

### BorgBackup
```bash
# 압축 알고리즘 선택
borg create --compression lz4 /backup::data /data      # 빠름
borg create --compression zstd,3 /backup::data /data   # 균형
borg create --compression lzma,6 /backup::data /data   # 최고 압축

# SSH 압축 비활성화 (이미 압축된 경우)
borg create -e ssh user@server:/backup::data /data
```

### Rclone
```bash
# 전송 수 증가
rclone sync /data remote: --transfers 16

# 체크섬 스킵 (속도 우선)
rclone sync /data remote: --checksum=false

# 버퍼 크기 증가
rclone sync /data remote: --buffer-size 256M
```

---

## 보안 체크리스트

- [ ] 암호화 활성화 (전송 중 + 저장 시)
- [ ] 강력한 비밀번호 사용 (16자 이상)
- [ ] 비밀번호 안전하게 보관
- [ ] IAM 권한 최소화 (S3 버킷만)
- [ ] MFA 활성화 (AWS 계정)
- [ ] 백업 로그 모니터링
- [ ] 정기적 복원 테스트
- [ ] 백업 무결성 검증
- [ ] 네트워크 암호화 (VPN/TLS)
- [ ] 접근 로그 기록

---

## 참고 자료

### 공식 문서
- [Restic 공식 문서](https://restic.readthedocs.io/)
- [BorgBackup 공식 문서](https://borgbackup.readthedocs.io/)
- [Rclone 공식 문서](https://rclone.org/docs/)
- [AWS CLI S3 명령어](https://docs.aws.amazon.com/cli/latest/reference/s3/)

### 커뮤니티
- [Restic Forum](https://forum.restic.net/)
- [BorgBackup GitHub](https://github.com/borgbackup/borg)
- [Rclone Forum](https://forum.rclone.org/)

### 관련 도구
- [Fluent Bit](https://fluentbit.io/) - 로그 수집기
- [Autorestic](https://autorestic.vercel.app/) - Restic 래퍼
- [Borgmatic](https://torsion.org/borgmatic/) - BorgBackup 래퍼

---

© 2026. Licensed under CC BY 4.0.
