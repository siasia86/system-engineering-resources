# STS AssumeRole 설정 가이드
<!-- reference: _reference/aws_sts_iam_s3_kms_official_notes.md -->

AWS STS(Security Token Service)를 사용하여 임시 자격증명을 발급하고 Cross-account 접근을 구성하는 방법을 정리합니다.

AWS 계정 ID, KMS key ID, 버킷명은 문서용 placeholder입니다. 실행 시 `<ACCOUNT-ID-1>`, `<ACCOUNT-ID-2>`, `<KEY-ID>`, `my-bucket`을 실제 값으로 대체합니다.

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

### GetCallerIdentity란

`GetCallerIdentity`는 현재 AWS 요청에 사용된 자격증명의 주체를 확인하는 STS API입니다. 임시 자격증명을 발급하거나 권한을 추가하지 않고, 다음 식별 정보를 반환합니다.

| 반환 항목 | 설명                                                                                                               |
|-----------|--------------------------------------------------------------------------------------------------------------------|
| Account   | 현재 자격증명을 소유한 AWS 계정 ID                                                                                 |
| Arn       | 호출 주체의 ARN. IAM Role 세션이면 `arn:aws:sts::<ACCOUNT-ID>:assumed-role/<ROLE-NAME>/<SESSION-NAME>` 형식입니다. |
| UserId    | 호출 주체의 고유 식별자                                                                                            |

IAM 권한을 별도로 부여하지 않아도 호출할 수 있으므로, 현재 자격증명이 예상한 계정·역할인지 확인하는 진단 명령으로 사용합니다. 단, 호출 성공은 해당 주체가 S3나 KMS 같은 다른 AWS API를 호출할 권한이 있다는 의미가 아닙니다.

```bash
aws sts get-caller-identity
```

Vault의 AWS auth method에서 IAM 인증을 사용하는 경우에도 이 API가 사용됩니다. 클라이언트가 자신의 AWS 자격증명으로 서명한 `GetCallerIdentity` 요청을 제출하면 Vault가 AWS에 요청을 검증하여 로그인 주체를 확인합니다. 따라서 이 인증 방식을 사용할 때는 Vault 서버의 STS endpoint 접근 경로와 클라이언트가 요청에 서명할 AWS 자격증명을 확인해야 합니다. `GetCallerIdentity`는 `AssumeRole`처럼 임시 자격증명을 발급하는 API가 아닙니다.

### IAM 영구 키 vs AssumeRole 임시 자격증명

| 항목          | IAM 영구 키                    | AssumeRole 임시 자격증명                     |
|---------------|--------------------------------|----------------------------------------------|
| 유효 기간     | 만료 없음 (수동 삭제 전까지)   | 15분~역할 `MaxSessionDuration` (최대 12시간) |
| 키 유출 시    | 즉시 악용 가능                 | 만료 후 자동 무효화                          |
| 권한 범위     | 연결된 정책과 조건에 따라 결정 | 역할 정책과 세션 정책 등의 교집합            |
| Cross-account | 별도 사용자 생성이 필수 아님   | Trust Policy와 호출자 권한으로 위임          |
| 감사 추적     | CloudTrail: IAM 사용자         | CloudTrail: 역할 + 세션명                    |
| 자격증명 개수 | 키 최대 2개                    | 필요 시마다 발급                             |

### STS API별 임시 자격증명 유효 기간

`STS 임시 자격증명`은 호출 API와 호출 주체에 따라 유효 기간이 다릅니다.

| API                       | 호출 주체       | 최소 | 최대      | 기본   |
|---------------------------|-----------------|------|-----------|--------|
| AssumeRole                | IAM 사용자/역할 | 15분 | 역할 설정 | 1시간  |
| AssumeRoleWithSAML        | SAML 사용자     | 15분 | 역할 설정 | 1시간  |
| AssumeRoleWithWebIdentity | OIDC 사용자     | 15분 | 역할 설정 | 1시간  |
| GetFederationToken        | IAM 사용자      | 15분 | 36시간    | 12시간 |
| GetFederationToken        | root 사용자     | 15분 | 1시간     | 1시간  |
| GetSessionToken           | IAM 사용자      | 15분 | 36시간    | 12시간 |
| GetSessionToken           | root 사용자     | 15분 | 1시간     | 1시간  |

`AssumeRole` 계열의 `역할 설정`은 역할의 `MaxSessionDuration`이며, 최대 설정값은 12시간입니다. Role chaining을 사용하면 세션 기간이 최대 1시간으로 제한됩니다. `AssumeRoleWithSAML`은 SAML 응답의 `SessionNotOnOrAfter` 값이 더 짧으면 해당 값이 적용됩니다.

### 임시 자격증명 구성

AssumeRole 호출 성공 시 `Credentials` 객체에 아래 4개 값이 반환됩니다.

| 항목            | 내용                                                  |
|-----------------|-------------------------------------------------------|
| AccessKeyId     | 임시 액세스 키 ID                                     |
| SecretAccessKey | 임시 시크릿 키                                        |
| SessionToken    | 임시 보안 토큰. 임시 자격증명으로 서명할 때 함께 사용 |
| Expiration      | 만료 시각 (기본 1시간, 역할 설정에 따라 최대 12시간)  |

🟡 임시 자격증명을 사용할 때는 `SessionToken`도 요청에 포함해야 합니다. 누락되거나 잘못된 토큰을 사용하면 인증 오류가 발생합니다.

---

## 2. AssumeRole 파라미터

### 주요 파라미터

| 파라미터        | 필수 | 설명                                              | 예시                                           |
|-----------------|------|---------------------------------------------------|------------------------------------------------|
| RoleArn         | ✅   | 위임받을 역할 ARN                                 | arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer |
| RoleSessionName | ✅   | 세션 식별자 (CloudTrail 추적용)                   | ec2-backup-session                             |
| DurationSeconds | ❌   | 900초~역할 `MaxSessionDuration` (최대 43200초)    | 3600                                           |
| ExternalId      | ❌   | 제3자 위임의 confused deputy 완화용 식별자        | SecureExternalId123                            |
| Policy          | ❌   | 역할 정책보다 좁게 제한하는 inline session policy | 인라인 JSON Policy                             |

> Confused deputy: 권한이 있는 중개자가 요청자의 의도와 다른 대상에게
> 권한을 행사하도록 속이는 문제입니다. `ExternalId`는 제3자 위임에서
> 역할을 요청하는 고객 맥락을 확인하는 조건으로 사용합니다.

> `ExternalId`는 API상 선택 사항입니다. Trust Policy가 `sts:ExternalId` 조건을
> 요구하는 경우에만 AssumeRole 호출에 포함해야 하며, AWS는 이를 시크릿으로
> 취급하지 않습니다. 제3자 위임에서는 사용을 권장합니다.

### CLI 예시

```bash
# 기본 AssumeRole
aws sts assume-role \
  --role-arn "arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer" \
  --role-session-name "ec2-backup-session" \
  --duration-seconds 3600

# ExternalId 포함
aws sts assume-role \
  --role-arn "arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer" \
  --role-session-name "ec2-backup-session" \
  --external-id "SecureKey123"
```

```bash
# 반환값을 환경변수로 설정
CREDS=$(aws sts assume-role \
  --role-arn "arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer" \
  --role-session-name "ec2-backup-session" \
  --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
  --output text)

read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN <<< "$CREDS"
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
unset CREDS

# 이후 API 호출은 임시 자격증명 자동 사용
aws s3 ls s3://my-bucket/
```

### 권한 범위 제한

Session Policy를 사용하면 역할 권한보다 좁게 제한할 수 있습니다. 역할보다 넓게 확장은 불가합니다.

| 시나리오       | Role Policy  | Session Policy | 유효 권한                      |
|----------------|--------------|----------------|--------------------------------|
| 제한 없음      | s3:*, kms:*  | 없음           | 역할 정책과 다른 정책의 교집합 |
| 세션 축소      | s3:*, kms:*  | s3:GetObject   | 허용된 리소스의 s3:GetObject   |
| 세션 확장 시도 | s3:GetObject | s3:*           | s3:GetObject만 (확장 불가)     |

---

## 3. 세션 유형

| 유형               | API                       | 최대 유효 기간                       | 주요 용도                 |
|--------------------|---------------------------|--------------------------------------|---------------------------|
| 역할 위임          | AssumeRole                | 최대 12시간 (role chaining 시 1시간) | EC2 → 다른 계정 S3 접근   |
| 웹 자격증명 연동   | AssumeRoleWithWebIdentity | 역할 설정 기준 최대 12시간           | OIDC(GitHub Actions, EKS) |
| SAML 연동          | AssumeRoleWithSAML        | 역할 설정 기준 최대 12시간           | 기업 AD/SSO 연동          |
| 임시 보안 자격증명 | GetSessionToken           | IAM 사용자 36시간 / 계정 1시간       | MFA 조건 API의 단기 접근  |

---

## 4. Trust Policy 설정

Trust Policy는 **B계정 역할(Role)에 설정**합니다. "누가 이 역할을 위임받을 수 있는가"를 정의합니다.

`arn:aws:iam::<ACCOUNT-ID-1>:root`는 A계정의 account principal을 의미하며, A계정의 root 사용자만을 뜻하지 않습니다. 필요하면 신뢰할 역할 등 더 좁은 principal을 검토합니다.

### 구성 요소

| 요소      | 설명                               | 예시 값                          |
|-----------|------------------------------------|----------------------------------|
| Effect    | 허용/거부                          | Allow                            |
| Principal | 역할을 위임할 수 있는 주체         | arn:aws:iam::<ACCOUNT-ID-1>:root |
| Action    | 허용할 STS 작업                    | sts:AssumeRole                   |
| Condition | 추가 조건 (ExternalId, MFA, IP 등) | StringEquals: sts:ExternalId     |

### 기본 Trust Policy (A계정 EC2 → B계정 역할)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT-ID-1>:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### ExternalId 조건 포함 (제3자 위임 시 권장)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT-ID-1>:root"
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
      "Resource": "arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer"
    }
  ]
}
```

### B계정 — backup-writer Role Policy (S3 + KMS)

실제 다른 계정의 IAM principal이 SSE-KMS 객체를 공유받는 Cross-account 구성에서는 customer managed KMS key를 사용해야 합니다. 이 문서처럼 A계정의 EC2가 B계정 역할을 AssumeRole한 뒤 B계정 리소스에 접근하는 구성에서는 호출 principal이 B계정 역할이므로 AWS managed key 사용 가능 여부가 달라집니다. 여기서는 customer managed KMS key를 명시하는 구성을 기준으로 설명합니다. Role Policy에는 S3 권한과 KMS 키 사용 권한을 부여하고, KMS Key Policy는 해당 역할을 직접 허용하거나 계정의 IAM 정책 위임을 허용해야 합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListTargetBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    },
    {
      "Sid": "ReadWriteObjects",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Sid": "UseSseKmsKey",
      "Effect": "Allow",
      "Action": [
        "kms:GenerateDataKey",
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:ap-northeast-2:<ACCOUNT-ID-2>:key/<KEY-ID>"
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
        "AWS": "arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer"
      },
      "Action": [
        "kms:GenerateDataKey",
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:ap-northeast-2:<ACCOUNT-ID-2>:key/<KEY-ID>"
    }
  ]
}
```

🟡 SSE-KMS를 사용할 때는 S3 Role Policy, KMS Role Policy, KMS Key Policy의 허용 조건을 모두 충족해야 합니다. customer managed KMS key를 사용하고, 키와 버킷을 같은 리전에 배치해야 합니다. 어느 한쪽의 권한이나 리소스 ARN이 맞지 않으면 `AccessDenied`가 발생할 수 있습니다.

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

| 계층 | 위치                 | 설정 내용                      | 누락 시 증상        |
|------|----------------------|--------------------------------|---------------------|
| 1    | A계정 IAM            | sts:AssumeRole 허용            | AssumeRole API 실패 |
| 2    | B계정 Role           | Trust Policy에 A계정 허용      | AccessDenied (STS)  |
| 3    | B계정 Role           | S3 권한과 올바른 버킷/객체 ARN | AccessDenied (S3)   |
| 4    | B계정 Role + KMS Key | KMS IAM/Key Policy와 키 ARN    | AccessDenied (KMS)  |

### CLI로 전체 검증

```bash
# 1. AssumeRole 동작 확인
aws sts assume-role \
  --role-arn "arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer" \
  --role-session-name "test-session"

# 2. 임시 자격증명 설정
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# 3. S3 접근 확인
aws s3 ls s3://my-bucket/

# 4. 업로드 확인 (SSE-KMS 명시)
aws s3 cp test.txt \
  s3://my-bucket/test.txt \
  --sse aws:kms \
  --sse-kms-key-id "arn:aws:kms:ap-northeast-2:<ACCOUNT-ID-2>:key/<KEY-ID>"

# 5. 현재 자격증명 확인
aws sts get-caller-identity
```

---

## 7. 트러블슈팅

| 오류                         | 원인                                | 해결                                 |
|------------------------------|-------------------------------------|--------------------------------------|
| `AccessDenied` on AssumeRole | Trust Policy에 Principal 미등록     | B계정 Role Trust Policy에 A계정 추가 |
| `InvalidClientTokenId`       | SessionToken 누락 또는 잘못된 값    | AWS_SESSION_TOKEN 환경변수 확인      |
| `AccessDenied` on s3:Put     | S3 PutObject 또는 KMS 권한/ARN 오류 | Role Policy와 KMS 권한 확인          |
| `AccessDenied` on kms:*      | KMS IAM/Key Policy 또는 키 ARN 오류 | Role과 KMS Key Policy 모두 확인      |
| `ExpiredTokenException`      | 임시 자격증명 만료                  | AssumeRole 재호출하여 갱신           |
| `AccessDenied` + ExternalId  | Trust Policy 조건과 값 불일치       | ExternalId 조건과 호출값 확인        |

---

## 참고 자료

- AWS Documentation: [STS AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html) — ★★★☆☆
- AWS Documentation: [STS GetSessionToken](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetSessionToken.html) — ★★★☆☆
- AWS Documentation: [STS GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html) — ★★★☆☆
- AWS Documentation: [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) — ★★★☆☆
- AWS Documentation: [SSE-KMS](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html) — ★★★☆☆
- AWS official verification notes: [_reference/aws_sts_iam_s3_kms_official_notes.md](../../_reference/aws_sts_iam_s3_kms_official_notes.md)
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

**마지막 업데이트**: 2026-08-14

© 2026 siasia86. Licensed under CC BY 4.0.
