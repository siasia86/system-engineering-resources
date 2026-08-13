# STS AssumeRole 설정 가이드

AWS STS(Security Token Service)를 사용하여 임시 자격증명을 발급하고 Cross-account 접근을 구성하는 방법을 정리합니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개념](#1-개념) / [2. AssumeRole 파라미터](#2-assumerole-파라미터) / [3. 세션 유형](#3-세션-유형)     |
| [4. Trust Policy 설정](#4-trust-policy-설정) / [5. IAM Policy 설정](#5-iam-policy-설정)                  |
| [6. Cross-account S3 + SSE-KMS 설정](#6-cross-account-s3--sse-kms-설정) / [7. 트러블슈팅](#7-트러블슈팅) |

---

## 1. 개념

### STS란

AWS에서 **임시 자격증명**을 발급하는 서비스입니다. IAM 영구 키 대신 유효 기간이 있는 자격증명을 사용하여 키 유출 피해 범위를 줄입니다.

```
AssumeRole flow:

Account-A EC2                 AWS STS                      Account-B
     │                            │                            │
     ├── AssumeRole request ─────>│                            │
     │   (Account-B Role ARN)     │── Trust Policy check ─────>│
     │                            │<── allowed ────────────────┤
     │<── temp credentials ───────┤                            │
     │   (AccessKeyId             │                            │
     │    SecretAccessKey         │                            │
     │    SessionToken)           │                            │
     │                            │                            │
     ├── S3/KMS API call ─────────┼───────────────────────────>│
     │   (using temp credentials) │                            │
```

### IAM 영구 키 vs STS 임시 자격증명

| 항목          | IAM 영구 키                  | STS 임시 자격증명                |
|---------------|------------------------------|----------------------------------|
| 유효 기간     | 만료 없음 (수동 삭제 전까지) | 15분~12시간 (설정 가능)          |
| 키 유출 시    | 즉시 악용 가능               | 만료 후 자동 무효화              |
| 권한 범위     | IAM Policy 전체              | AssumeRole 시점 Policy만         |
| Cross-account | 별도 IAM 사용자 생성 필요    | 역할 위임(Trust Policy)으로 처리 |
| 감사 추적     | CloudTrail: IAM 사용자       | CloudTrail: 역할 + 세션명        |
| 자격증명 개수 | 키 최대 2개                  | 필요 시마다 발급                 |

### 임시 자격증명 구성

AssumeRole 호출 성공 시 아래 4개 값이 반환됩니다.

| 항목            | 내용                                           |
|-----------------|------------------------------------------------|
| AccessKeyId     | 임시 액세스 키 ID                              |
| SecretAccessKey | 임시 시크릿 키                                 |
| SessionToken    | 임시 세션 토큰 (필수, 없으면 인증 실패)        |
| Expiration      | 만료 시각 (AssumeRole 기본 1시간, 최대 12시간) |

🟡 SessionToken은 API 호출 시 반드시 포함해야 합니다. 누락 시 `InvalidClientTokenId` 오류가 발생합니다.

---

## 2. AssumeRole 파라미터

### 주요 파라미터

| 파라미터        | 필수 | 설명                                  | 예시                                    |
|-----------------|------|---------------------------------------|-----------------------------------------|
| RoleArn         | ✅   | 위임받을 역할 ARN                     | arn:aws:iam::B계정ID:role/backup-writer |
| RoleSessionName | ✅   | 세션 식별자 (CloudTrail 추적용)       | ec2-backup-session                      |
| DurationSeconds | ❌   | 유효 기간 초 단위 (900~43200)         | 3600                                    |
| ExternalId      | ❌   | Confused Deputy 방지용 공유 시크릿    | SecureKey123                            |
| Policy          | ❌   | 추가 권한 제한 (역할보다 좁게만 가능) | 인라인 JSON Policy                      |

> ExternalId: B계정이 Trust Policy에 설정한 값으로, A계정이 AssumeRole 호출 시
> 반드시 제시해야 합니다. 공격자가 Role ARN을 알아도 ExternalId 없이는 거부됩니다.

### CLI 예시

```bash
# 기본 AssumeRole
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/backup-writer" \
  --role-session-name "ec2-backup-session" \
  --duration-seconds 3600

# ExternalId 포함
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/backup-writer" \
  --role-session-name "ec2-backup-session" \
  --external-id "SecureKey123"
```

```bash
# 반환값을 환경변수로 설정
CREDS=$(aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/backup-writer" \
  --role-session-name "ec2-backup-session" \
  --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
  --output text)

export AWS_ACCESS_KEY_ID=$(echo $CREDS | awk '{print $1}')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | awk '{print $2}')
export AWS_SESSION_TOKEN=$(echo $CREDS | awk '{print $3}')

# 이후 API 호출은 임시 자격증명 자동 사용
aws s3 ls s3://my-bucket-123456789012-ap-northeast-2/
```

### 권한 범위 제한

Session Policy를 사용하면 역할 권한보다 좁게 제한할 수 있습니다. 역할보다 넓게 확장은 불가합니다.

| 시나리오       | Role Policy  | Session Policy | 실제 권한                  |
|----------------|--------------|----------------|----------------------------|
| 제한 없음      | s3:*, kms:*  | 없음           | s3:*, kms:*                |
| 세션 축소      | s3:*, kms:*  | s3:GetObject   | s3:GetObject만             |
| 세션 확장 시도 | s3:GetObject | s3:*           | s3:GetObject만 (확장 불가) |

---

## 3. 세션 유형

| 유형               | API                       | 최대 유효 기간                   | 주요 용도                 |
|--------------------|---------------------------|----------------------------------|---------------------------|
| 역할 위임          | AssumeRole                | 12시간                           | EC2 → 다른 계정 S3 접근   |
| 웹 자격증명 연동   | AssumeRoleWithWebIdentity | 12시간 (Role MaxSessionDuration) | OIDC(GitHub Actions, EKS) |
| SAML 연동          | AssumeRoleWithSAML        | 12시간 (Role MaxSessionDuration) | 기업 AD/SSO 연동          |
| 임시 보안 자격증명 | GetSessionToken           | 36시간 (IAM 사용자)              | MFA 인증 후 단기 접근     |

---

## 4. Trust Policy 설정

Trust Policy는 **B계정 역할(Role)에 설정**합니다. "누가 이 역할을 위임받을 수 있는가"를 정의합니다.

### 구성 요소

| 요소      | 설명                               | 예시 값                      |
|-----------|------------------------------------|------------------------------|
| Effect    | 허용/거부                          | Allow                        |
| Principal | 역할을 위임할 수 있는 주체         | arn:aws:iam::A계정ID:root    |
| Action    | 허용할 STS 작업                    | sts:AssumeRole               |
| Condition | 추가 조건 (ExternalId, MFA, IP 등) | StringEquals: sts:ExternalId |

### 기본 Trust Policy (A계정 EC2 → B계정 역할)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::A계정ID:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### ExternalId 조건 포함 (권장)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::A계정ID:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "SecureKey123"
        }
      }
    }
  ]
}
```

### EC2 Instance Profile용 Trust Policy

EC2 인스턴스 자체에 역할을 부여할 때 사용합니다.

```json
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
```

---

## 5. IAM Policy 설정

### A계정 — AssumeRole 허용 Policy

A계정 EC2 인스턴스 역할에 부여합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::B계정ID:role/backup-writer"
    }
  ]
}
```

### B계정 — backup-writer Role Policy (S3 + KMS)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket-B계정ID-ap-northeast-2",
        "arn:aws:s3:::my-bucket-B계정ID-ap-northeast-2/*"
      ]
    }
  ]
}
```

### B계정 — KMS Key Policy (SSE-KMS 버킷 사용 시 필수)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::B계정ID:role/backup-writer"
      },
      "Action": [
        "kms:GenerateDataKey",
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:ap-northeast-2:B계정ID:key/KEY-ID"
    }
  ]
}
```

🟡 S3 Policy와 KMS Key Policy를 모두 설정해야 합니다. 어느 한쪽만 설정하면 `AccessDenied`가 발생합니다.

---

## 6. Cross-account S3 + SSE-KMS 설정

### 전체 구성도

```
Account-A                                    Account-B
┌─────────────────────────┐                 ┌────────────────────────────────────┐
│ EC2 Instance            │                 │ Role: backup-writer                │
│  Instance Profile       │                 │  Trust Policy: allow Account-A     │
│   └ sts:AssumeRole      │──AssumeRole────>│  Role Policy: s3:Put/Get           │
│                         │<─temp creds──── │                                    │
│                         │                 │ S3 Bucket (SSE-KMS)                │
│  s3 sync ───────────────│─────────────────│──> s3:PutObject                    │
│                         │                 │       └ KMS Key Policy check       │
│  (no DeleteObject)      │                 │           └ kms:GenerateDataKey    │
└─────────────────────────┘                 └────────────────────────────────────┘
```

### 권한 체크포인트 (누락 시 증상)

| 계층 | 위치          | 설정 내용                        | 누락 시 증상        |
|------|---------------|----------------------------------|---------------------|
| 1    | A계정 IAM     | sts:AssumeRole 허용              | AssumeRole API 실패 |
| 2    | B계정 Role    | Trust Policy에 A계정 허용        | AccessDenied (STS)  |
| 3    | B계정 Role    | s3:PutObject, s3:GetObject       | AccessDenied (S3)   |
| 4    | B계정 KMS Key | kms:GenerateDataKey, kms:Decrypt | AccessDenied (KMS)  |

### CLI로 전체 검증

```bash
# 1. AssumeRole 동작 확인
aws sts assume-role \
  --role-arn "arn:aws:iam::B계정ID:role/backup-writer" \
  --role-session-name "test-session"

# 2. 임시 자격증명 설정
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# 3. S3 접근 확인
aws s3 ls s3://my-bucket-B계정ID-ap-northeast-2/

# 4. 업로드 확인 (SSE-KMS 포함)
aws s3 cp test.txt s3://my-bucket-B계정ID-ap-northeast-2/test.txt

# 5. 현재 자격증명 확인
aws sts get-caller-identity
```

---

## 7. 트러블슈팅

| 오류                         | 원인                            | 해결                                 |
|------------------------------|---------------------------------|--------------------------------------|
| `AccessDenied` on AssumeRole | Trust Policy에 Principal 미등록 | B계정 Role Trust Policy에 A계정 추가 |
| `InvalidClientTokenId`       | SessionToken 누락               | AWS_SESSION_TOKEN 환경변수 확인      |
| `AccessDenied` on s3:Put     | Role Policy에 s3:PutObject 없음 | backup-writer Role Policy 확인       |
| `AccessDenied` on kms:*      | KMS Key Policy에 Role 미등록    | B계정 KMS Key Policy에 Role ARN 추가 |
| `ExpiredTokenException`      | 임시 자격증명 만료              | AssumeRole 재호출하여 갱신           |
| `AccessDenied` + ExternalId  | ExternalId 불일치               | Trust Policy Condition 값 확인       |

---

## 참고 자료

- AWS Documentation: [STS AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html) — ★★★☆☆
- AWS Documentation: [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) — ★★★☆☆
- [s3_bucket_create_options.md](s3_bucket_create_options.md)
- [s3_object_lock.md](s3_object_lock.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-12

**마지막 업데이트**: 2026-08-12

© 2026 siasia86. Licensed under CC BY 4.0.
