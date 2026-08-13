---
name: aws-sts-iam-s3-kms-official-notes
description: AWS STS AssumeRole, IAM role, S3 정책, SSE-KMS 권한의 공식 문서 검증 노트.
tags:
  - aws
  - sts
  - iam
  - s3
  - kms
last_checked: 2026-08-13
sources:
  - https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
  - https://docs.aws.amazon.com/STS/latest/APIReference/API_GetSessionToken.html
  - https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html
  - https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithSAML.html
  - https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html
  - https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_aws-accounts.html
  - https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html
  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-with-s3-actions.html
  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html
  - https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-modifying.html
---

## 1. STS AssumeRole

- `AssumeRole`은 액세스 키 ID, 시크릿 액세스 키, 보안 토큰으로 구성된 임시 자격증명을 반환합니다.
- `DurationSeconds`의 일반 범위는 900초(15분)부터 역할의 `MaxSessionDuration`까지입니다. 역할의 최대 세션 기간은 1시간부터 12시간까지 설정할 수 있으며, 기본 세션 기간은 1시간입니다.
- Role chaining에서는 CLI/API 세션이 최대 1시간으로 제한됩니다.
- `ExternalId`는 API 파라미터상 선택 사항입니다. Trust Policy가 `sts:ExternalId` 조건을 요구하는 경우에만 호출자가 올바른 값을 전달해야 합니다. 주된 용도는 제3자 위임에서 confused deputy 문제를 줄이는 것입니다. AWS는 ExternalId를 시크릿으로 취급하지 않습니다.
- 세션 정책은 역할의 identity-based policy와 교집합으로 적용되며, 역할 정책보다 많은 권한을 부여할 수 없습니다.

## 2. STS 세션 유형

- `AssumeRoleWithWebIdentity`와 `AssumeRoleWithSAML`은 기본 1시간이며, 역할의 최대 세션 기간 설정 범위 내에서 15분부터 최대 12시간까지 요청할 수 있습니다. SAML은 SAML 응답의 `SessionNotOnOrAfter`와 요청 기간 중 더 짧은 값이 적용됩니다.
- `GetSessionToken`은 IAM 사용자 자격증명 기준 15분부터 36시간까지, 계정 자격증명 기준 최대 1시간입니다. MFA는 보호된 API 호출에 필요하도록 구성한 경우 사용합니다.

## 3. Cross-account 역할 위임

- 대상 계정 역할의 Trust Policy는 신뢰 주체를 정의합니다.
- 호출 주체의 계정에는 대상 역할 ARN에 대한 `sts:AssumeRole` identity-based permission이 필요합니다.
- `arn:aws:iam::ACCOUNT_ID:root`는 일반적으로 해당 계정 principal을 의미하며 root 사용자만을 뜻하는 표현으로 설명하면 안 됩니다.

## 4. S3 및 SSE-KMS 권한

- S3 버킷 수준 작업인 `s3:ListBucket`은 버킷 ARN을 사용하고, 객체 수준 작업인 `s3:GetObject`와 `s3:PutObject`는 객체 ARN을 사용합니다.
- SSE-KMS `PutObject`에는 KMS 키의 `kms:GenerateDataKey`, 다운로드에는 `kms:Decrypt`가 필요합니다. multipart upload에는 두 권한이 모두 필요할 수 있습니다.
- Cross-account SSE-KMS에는 customer managed KMS key를 사용해야 합니다. KMS key policy에 대상 principal을 허용하는 것과 별도로, 해당 principal의 계정에 IAM policy 권한도 필요합니다.
- KMS 키는 S3 버킷과 같은 리전에 있어야 합니다.

## 참고 기준

위 내용은 2026-08-13에 `sources`의 AWS 공식 문서를 `lynx -dump`로 직접 확인한 결과입니다. 계정별 SCP, permissions boundary, 명시적 Deny, S3 bucket policy 및 KMS key policy의 기존 문맥에 따라 최종 유효 권한은 달라질 수 있습니다.
