# S3 Cross-Account 백업 (STS AssumeRole)

A계정 EC2에서 B계정 S3 버킷으로 반복·영구 백업하는 구성 가이드입니다. STS AssumeRole 방식을 사용하여 객체 소유권 문제를 방지하고 B계정이 백업 데이터를 통제합니다.

## 목차

| 섹션                                                                                           |
|------------------------------------------------------------------------------------------------|
| [1. STS 개념](#1-sts-개념) / [2. 아키텍처](#2-아키텍처) / [3. 사전 조건](#3-사전-조건)         |
| [4. B계정 설정](#4-b계정-설정) / [5. A계정 설정](#5-a계정-설정) / [6. 백업 실행](#6-백업-실행) |
| [7. 자동화](#7-자동화) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                   |

---

## 1. STS 개념

### STS (Security Token Service)란

AWS에서 **임시 보안 자격 증명**을 발급하는 서비스입니다. 영구 AccessKey 대신 만료 시간이 있는 임시 토큰을 사용하여 보안을 강화합니다.

### 주요 API

| API                         | 용도                                           |
|-----------------------------|------------------------------------------------|
| `AssumeRole`                | 다른 IAM Role을 임시로 맡기 (Cross-account 등) |
| `GetCallerIdentity`         | 현재 자격 증명 확인 ("나 누구야?")             |
| `GetSessionToken`           | MFA 인증 후 임시 토큰 발급                     |
| `AssumeRoleWithWebIdentity` | OIDC 연동 (GitHub Actions, EKS Pod 등)         |

### 영구키 vs 임시 토큰

| 구분      | IAM User AccessKey | STS 임시 자격 증명              |
|-----------|--------------------|---------------------------------|
| 만료      | 없음 (수동 삭제)   | 있음 (1h~12h)                   |
| 유출 위험 | 높음 (영구 접근)   | 낮음 (만료 후 무효)             |
| 권한 범위 | User에 연결된 정책 | Role에 연결된 정책 (축소 가능)  |
| 감사      | CloudTrail 기록    | CloudTrail + 세션 이름 기록     |
| 회수      | 키 삭제/비활성화   | Trust Policy 수정으로 즉시 차단 |

### Cross-Account에서 STS를 사용하는 이유

1. **B계정에 영구 키를 만들 필요 없음** — A계정 EC2가 B계정 Role을 임시로 맡음
2. **객체 소유권 문제 해결** — B계정 Role로 쓰기 때문에 B계정이 객체 소유자
3. **즉시 차단 가능** — B계정에서 Trust Policy 제거하면 A계정 접근 즉시 불가
4. **감사 추적** — CloudTrail에 AssumeRole 이벤트 + 세션 이름 기록

### 방식 비교

| 방식           | 인증                 | 객체 소유자 | 권한 회수       | 복잡도 |
|----------------|----------------------|-------------|-----------------|--------|
| STS AssumeRole | 임시 토큰 (만료)     | B계정       | Trust 삭제 즉시 | 중간   |
| Bucket Policy  | A계정 영구 자격 증명 | A계정       | 정책 수정 필요  | 낮음   |
| S3 Replication | AWS 내부 (자동)      | B계정       | Rule 삭제       | 높음   |

### STS AssumeRole 장단점 세분화

#### 장점

| 분류      | 장점                | 설명                                                                        |
|-----------|---------------------|-----------------------------------------------------------------------------|
| 키 관리   | 영구 키 불필요      | 파일/환경변수로 키가 존재하지 않아 유출 경로 원천 차단                      |
| 키 관리   | 로테이션 불필요     | 임시 토큰이 자동 만료되므로 90일 교체 작업 없음                             |
| 키 관리   | 퇴사자 위험 없음    | 복사할 영구 키 자체가 없음                                                  |
| 유출 대응 | 자동 만료           | 토큰이 외부로 유출돼도 최대 1h 후 무효화                                    |
| 유출 대응 | 격리 즉시 차단      | EC2 종료/격리하면 새 토큰 갱신 불가                                         |
| 유출 대응 | 단일 지점 차단      | B계정 Trust Policy 제거 한 곳만 수정하면 즉시 차단                          |
| 감사      | 세션 추적           | CloudTrail에 세션 이름(서버명+날짜) 기록 → 누가 언제 어디서 사용했는지 명확 |
| 감사      | AssumeRole 이벤트   | Cross-account 접근 자체가 별도 이벤트로 기록                                |
| 소유권    | 객체 소유자 = B계정 | B계정 Role로 쓰기 때문에 소유권 문제 없음                                   |
| 운영      | 서버 확장 용이      | EC2 10대 추가해도 같은 Role 공유, 키 10개 생성 불필요                       |

#### 단점

| 분류      | 단점                            | 설명                                                            |
|-----------|---------------------------------|-----------------------------------------------------------------|
| 복잡도    | 초기 설정 복잡                  | Trust Policy + Role + Instance Profile 양쪽 계정 설정 필요      |
| 복잡도    | 스크립트에 AssumeRole 로직 필요 | 토큰 발급 → 환경 변수 설정 → 작업 → 정리                        |
| EC2 침해  | 실행 중 방어 못 함              | EC2가 침해된 상태로 돌아가면 계속 갱신 가능 (영구 키와 동일)    |
| EC2 침해  | IMDS 접근 가능                  | 공격자가 EC2 안에 있으면 Instance Profile 토큰 획득 가능        |
| 토큰 만료 | 장시간 작업 주의                | 기본 1h, 대용량 sync 시 중간에 만료 가능 (duration 조정 필요)   |
| 디버깅    | 오류 원인 파악 어려움           | Trust/ExternalId/Policy 중 어디서 Deny인지 CloudTrail 확인 필요 |

#### EC2 침해 시나리오별 비교

| 시나리오                     | 영구 키                   | STS                      |
|------------------------------|---------------------------|--------------------------|
| 키를 외부로 복사해감         | 삭제할 때까지 영구 사용   | 최대 1h 후 만료          |
| EC2 격리/종료 후             | 복사한 키 여전히 유효     | 갱신 불가 → 만료 후 끝   |
| EC2 살아있고 침해 인지 못 함 | 계속 접근                 | 계속 접근 (차이 없음)    |
| git/슬랙에 키 유출           | 발견할 때까지 무제한 접근 | 해당 없음 (키 파일 없음) |
| 퇴사자가 키 보유             | 키 삭제 전까지 접근 가능  | 해당 없음 (키 파일 없음) |

#### 결론

STS의 핵심 가치는 "침해된 EC2를 방어"하는 게 아니라 **영구 키가 존재하지 않아 유출 경로 자체를 제거**하는 것입니다. EC2가 침해된 상태로 방치되면 STS든 영구 키든 차이가 없지만, 현실에서 보안 사고의 대부분은 EC2 침해보다 **키 파일 유출**(git 커밋, 슬랙 공유, 퇴사자 보유)에서 발생합니다.

🟡 이 문서에서는 보안과 소유권 측면에서 적합한 **STS AssumeRole** 방식을 사용합니다.

---

## 2. 아키텍처

```
A Account (Source)                         B Account (Backup Target)
┌──────────────────────────┐               ┌─────────────────────────────────┐
│  EC2 Instance            │               │  IAM Role: backup-writer        │
│  Instance Profile:       │               │    Trust: A Account EC2 Role    │
│    ec2-backup-role       │               │    Policy: S3 PutObject         │
│                          │               │                                 │
│  aws sts assume-role ────│──────────────>│  return: temp credentials       │
│                          │<──────────────│                                 │
│  aws s3 sync ────────────│──────────────>│  s3://backup-bucket/            │
└──────────────────────────┘               └─────────────────────────────────┘

Flow:
  1. EC2 Instance Profile (auto temp credentials)
  2. AssumeRole → get temp token from B-account Role
  3. PutObject to B-account S3 with temp token
  4. Object ownership: B-account (no ownership issue)
```

## 3. 사전 조건

| 항목                 | 값 (예시)            |
|----------------------|----------------------|
| A계정 ID             | <ACCOUNT-ID-1>         |
| B계정 ID             | <ACCOUNT-ID-1>         |
| 리전                 | ap-northeast-2       |
| EC2 Instance Profile | ec2-backup-role      |
| B계정 Role           | backup-writer-role   |
| B계정 S3 버킷        | my-backup-bucket-222 |
| 백업 소스 경로       | /opt/backup/         |

---

## 4. B계정 설정

### 3.1 S3 버킷 생성

#### 웹 콘솔

1. B계정 로그인 → S3 → 버킷 만들기
2. 버킷 이름: `my-backup-bucket-222`
3. 리전: `ap-northeast-2`
4. 객체 소유권: **ACL 비활성화됨 (버킷 소유자 적용)** 선택
5. 퍼블릭 액세스 차단: **모든 퍼블릭 액세스 차단** 활성화
6. 버전 관리: 활성화 (실수 삭제 복원용)
7. 암호화: SSE-S3 또는 SSE-KMS

#### CLI

```bash
# B계정 프로필로 실행
aws s3api create-bucket \
  --bucket my-backup-bucket-222 \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2 \
  --profile b-account

# 버전 관리 활성화
aws s3api put-bucket-versioning \
  --bucket my-backup-bucket-222 \
  --versioning-configuration Status=Enabled \
  --profile b-account

# 퍼블릭 액세스 차단
aws s3api put-public-access-block \
  --bucket my-backup-bucket-222 \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true \
  --profile b-account

# 라이프사이클 (30일 후 Glacier 이동, 영구 보관)
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-backup-bucket-222 \
  --lifecycle-configuration '{
    "Rules": [
      {
        "ID": "backup-lifecycle",
        "Status": "Enabled",
        "Filter": {"Prefix": ""},
        "Transitions": [
          {"Days": 30, "StorageClass": "GLACIER"}
        ]
      }
    ]
  }' \
  --profile b-account
```

### 3.2 IAM Role 생성 (backup-writer-role)

#### 웹 콘솔

1. B계정 IAM → 역할 → 역할 만들기
2. 신뢰할 수 있는 엔터티 유형: **AWS 계정**
3. 다른 AWS 계정: `<ACCOUNT-ID-1>` (A계정 ID) 입력
4. 역할 이름: `backup-writer-role`
5. 권한 정책 → 정책 생성 → JSON 탭에 아래 내용 붙여넣기:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBackupWrite",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<BUCKET-1>",
        "arn:aws:s3:::<BUCKET-1>/*"
      ]
    }
  ]
}
```

6. 신뢰 관계 탭 → 신뢰 정책 편집 → 아래 내용 붙여넣기:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT-ID-1>:role/ec2-backup-role"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "backup-external-id-2026"
        }
      }
    }
  ]
}
```

#### CLI

```bash
# Trust Policy 생성
cat > /tmp/<DOMAIN-1> << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT-ID-1>:role/ec2-backup-role"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "backup-external-id-2026"
        }
      }
    }
  ]
}
EOF

# Role 생성
aws iam create-role \
  --role-name backup-writer-role \
  --assume-role-policy-document file:///tmp/<DOMAIN-1> \
  --description "Cross-account backup writer from A account EC2" \
  --profile b-account

# S3 쓰기 Policy 연결
cat > /tmp/<DOMAIN-2> << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBackupWrite",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<BUCKET-1>",
        "arn:aws:s3:::<BUCKET-1>/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name backup-writer-role \
  --policy-name backup-s3-write \
  --policy-document file:///tmp/<DOMAIN-2> \
  --profile b-account
```

🟡 `ExternalId`는 혼동된 대리인(Confused Deputy) 공격을 방지합니다. A계정이 AssumeRole 호출 시 이 값을 반드시 전달해야 합니다.

---

## 5. A계정 설정

### 4.1 EC2 Instance Profile (ec2-backup-role)

#### 웹 콘솔

1. A계정 IAM → 역할 → 역할 만들기
2. 신뢰할 수 있는 엔터티: **AWS 서비스 → EC2**
3. 역할 이름: `ec2-backup-role`
4. 권한 정책 → 정책 생성 → JSON 탭에 아래 내용 붙여넣기:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAssumeBackupRole",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<ACCOUNT-ID-1>:role/backup-writer-role"
    }
  ]
}
```

5. EC2 인스턴스 → 작업 → 보안 → IAM 역할 수정 → `ec2-backup-role` 선택

#### CLI

```bash
# EC2 Trust Policy
cat > /tmp/<DOMAIN-3> << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Role 생성
aws iam create-role \
  --role-name ec2-backup-role \
  --assume-role-policy-document file:///tmp/<DOMAIN-3> \
  --profile a-account

# AssumeRole 권한 부여 (B계정 Role을 맡을 수 있는 권한)
cat > /tmp/<DOMAIN-4> << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAssumeBackupRole",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<ACCOUNT-ID-1>:role/backup-writer-role"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name ec2-backup-role \
  --policy-name allow-assume-backup-role \
  --policy-document file:///tmp/<DOMAIN-4> \
  --profile a-account

# Instance Profile 생성 + Role 연결
aws iam create-instance-profile \
  --instance-profile-name ec2-backup-role \
  --profile a-account

aws iam add-role-to-instance-profile \
  --instance-profile-name ec2-backup-role \
  --role-name ec2-backup-role \
  --profile a-account

# EC2에 Instance Profile 연결
aws ec2 associate-iam-instance-profile \
  --instance-id <INSTANCE-ID-1> \
  --iam-instance-profile Name=ec2-backup-role \
  --profile a-account
```

---

## 6. 백업 실행

### 5.1 수동 실행 (테스트)

```bash
# 1. B계정 Role AssumeRole
CREDENTIALS=$(aws sts assume-role \
  --role-arn "arn:aws:iam::<ACCOUNT-ID-1>:role/backup-writer-role" \
  --role-session-name "backup-session-$(date +%Y%m%d)" \
  --external-id "backup-external-id-2026" \
  --duration-seconds 3600 \
  --output json)

# 2. 임시 자격 증명 추출
export AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDENTIALS | jq -r '.Credentials.SessionToken')

# 3. S3 sync 실행
aws s3 sync /opt/backup/ s3://my-backup-bucket-222/$(hostname)/$(date +%Y-%m-%d)/ \
  --region ap-northeast-2 \
  --storage-class STANDARD_IA \
  --exclude "*.tmp" \
  --exclude "*.log"

# 4. 환경 변수 정리
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
```

### 5.2 백업 스크립트

```bash
#!/bin/bash
# /opt/scripts/s3_backup.sh
# Cross-account S3 backup via STS AssumeRole

set -euo pipefail

ROLE_ARN="arn:aws:iam::<ACCOUNT-ID-1>:role/backup-writer-role"
EXTERNAL_ID="backup-external-id-2026"
BUCKET="my-backup-bucket-222"
SOURCE_DIR="/opt/backup"
REGION="ap-northeast-2"
DATE=$(date +%Y-%m-%d)
HOSTNAME=$(hostname)
LOG="/var/log/<DOMAIN-5>"

echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] backup start" >> "$LOG"

# AssumeRole
CREDENTIALS=$(aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "backup-${HOSTNAME}-${DATE}" \
  --external-id "$EXTERNAL_ID" \
  --duration-seconds 3600 \
  --output json 2>> "$LOG")

if [ $? -ne 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] assume-role failed" >> "$LOG"
  exit 1
fi

export AWS_ACCESS_KEY_ID=$(echo "$CREDENTIALS" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDENTIALS" | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$CREDENTIALS" | jq -r '.Credentials.SessionToken')

# S3 sync
aws s3 sync "$SOURCE_DIR" "s3://${BUCKET}/${HOSTNAME}/${DATE}/" \
  --region "$REGION" \
  --storage-class STANDARD_IA \
  --exclude "*.tmp" \
  --exclude "*.log" \
  >> "$LOG" 2>&1

STATUS=$?
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

if [ $STATUS -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] backup done: s3://${BUCKET}/${HOSTNAME}/${DATE}/" >> "$LOG"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] s3 sync failed (exit=$STATUS)" >> "$LOG"
  exit $STATUS
fi
```

---

## 7. 자동화

### cron 등록

```bash
# 매일 03:00 실행
echo "0 3 * * * root /opt/scripts/s3_backup.sh" > /etc/cron.d/s3-backup
chmod 644 /etc/cron.d/s3-backup
```

### SystemD Timer (대안)

```bash
# /etc/systemd/system/<DOMAIN-6>
cat > /etc/systemd/system/<DOMAIN-6> << 'EOF'
[Unit]
Description=S3 Cross-Account Backup
After=<DOMAIN-7>

[Service]
Type=oneshot
ExecStart=/opt/scripts/s3_backup.sh
StandardOutput=journal
StandardError=journal
EOF

# /etc/systemd/system/<DOMAIN-8>
cat > /etc/systemd/system/<DOMAIN-8> << 'EOF'
[Unit]
Description=Daily S3 Backup Timer

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=<DOMAIN-9>
EOF

systemctl daemon-reload
systemctl enable --now <DOMAIN-8>
```

---

## 8. 검증

### 7.1 AssumeRole 테스트

```bash
# EC2에서 실행
aws sts assume-role \
  --role-arn "arn:aws:iam::<ACCOUNT-ID-1>:role/backup-writer-role" \
  --role-session-name "test-session" \
  --external-id "backup-external-id-2026" \
  --query 'Credentials.Expiration' \
  --output text

# 성공 시 만료 시간 출력 (예: 2026-07-01T13:30:00+00:00)
```

### 7.2 S3 쓰기 테스트

```bash
# 임시 토큰 설정 후
echo "test" > /tmp/<DOMAIN-10>
aws s3 cp /tmp/<DOMAIN-10> s3://my-backup-bucket-222/test/ --region ap-northeast-2

# B계정에서 확인
aws s3 ls s3://my-backup-bucket-222/test/ --profile b-account
```

### 7.3 객체 소유권 확인

```bash
# B계정에서 실행 — 소유자가 B계정인지 확인
aws s3api get-object-acl \
  --bucket my-backup-bucket-222 \
  --key test/<DOMAIN-10> \
  --profile b-account
```

---

## 9. 트러블슈팅

| 에러                              | 원인                                 | 해결                                          |
|-----------------------------------|--------------------------------------|-----------------------------------------------|
| `AccessDenied` on AssumeRole      | Trust Policy에 A계정 Role ARN 미등록 | B계정 Role Trust 확인                         |
| `AccessDenied` on S3 PutObject    | B계정 Role에 S3 권한 부족            | `backup-s3-write` 정책 확인                   |
| `InvalidIdentityToken`            | ExternalId 불일치                    | 양쪽 ExternalId 값 동기화                     |
| `ExpiredTokenException`           | 임시 토큰 만료 (기본 1h)             | `--duration-seconds` 늘리기 (최대 3600~43200) |
| `The security token is not valid` | EC2에 Instance Profile 미연결        | `aws sts get-caller-identity`로 확인          |
| S3 sync 느림                      | 리전 간 전송 or 파일 수 과다         | 같은 리전 확인, `--exclude` 최적화            |

### 보안 점검 목록

- [ ] B계정 Role Trust에 ExternalId 조건 설정
- [ ] B계정 S3 버킷 퍼블릭 액세스 차단
- [ ] B계정 S3 버전 관리 활성화
- [ ] A계정 EC2 Role에 최소 권한 (AssumeRole만)
- [ ] 백업 스크립트에서 환경 변수 사용 후 즉시 unset
- [ ] CloudTrail에서 AssumeRole 이벤트 모니터링
- [ ] Object Lock 적용 검토 (삭제 방지)

> Object Lock 상세는 [s3_object_lock.md](../../04_system_engineer/02_operations/s3_object_lock.md) 참고

---

## 통계

![GitHub stars](https://<DOMAIN-11>/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://<DOMAIN-11>/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://<DOMAIN-11>/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://<DOMAIN-11>/github/last-commit/siasia86/system-engineering-resources)
![License](https://<DOMAIN-11>/github/license/siasia86/system-engineering-resources)
![Actions](https://<DOMAIN-11>/github/actions/workflow/status/siasia86/system-engineering-resources/<DOMAIN-12>)

---

**작성일**: 2026-07-01

**마지막 업데이트**: 2026-07-01

© 2026 siasia86. Licensed under CC BY 4.0.
