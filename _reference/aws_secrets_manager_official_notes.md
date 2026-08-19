---
name: aws-secrets-manager-official-notes
description: AWS Secrets Manager의 Secret 수명주기·Rotation·IAM 접근제어 공식 문서 검증 노트.
tags:
  - aws
  - secrets-manager
  - iam
  - rotation
last_checked: 2026-08-19
sources:
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_iam-policies.html
---

# AWS Secrets Manager 공식 문서 참조 노트

## 1. 서비스 목적

- AWS Secrets Manager는 데이터베이스 자격증명, 애플리케이션 자격증명, OAuth 토큰, API 키 등 Secret의 관리·조회·Rotation을 지원합니다.
- 애플리케이션 코드에 자격증명을 하드코딩하지 않고 실행 시점에 동적으로 조회하는 방식으로 사용할 수 있습니다.
- AWS 자격증명은 IAM, 암호화 키는 AWS KMS, private key와 인증서는 AWS Certificate Manager 사용을 권장합니다.

## 2. Rotation

- Rotation은 Secret과 연결된 데이터베이스 또는 서비스의 자격증명을 함께 갱신하는 절차입니다.
- Managed rotation은 지원되는 관리형 Secret에 대해 AWS 서비스가 구성·관리합니다.
- 그 외 유형은 Lambda Rotation Function으로 Secret과 연결된 시스템을 함께 갱신할 수 있습니다.
- Secret Rotation은 KMS Key Rotation과 다른 개념입니다.

## 3. 접근제어

- IAM Identity-based Policy 또는 Secret Resource-based Policy로 Secret별 접근을 제한합니다.
- EC2 Instance Profile, ECS Task Role, Lambda Execution Role 등 애플리케이션 Role에 필요한 Secret의 `secretsmanager:GetSecretValue`만 부여합니다.
- Customer managed KMS Key로 암호화한 Secret을 읽을 때는 대상 Secret의 `secretsmanager:GetSecretValue`와 KMS Key의 `kms:Decrypt` 권한을 함께 검토합니다.
- Secret ARN의 이름 패턴 wildcard는 삭제 후 동일 이름으로 재생성된 Secret까지 권한이 이어질 수 있으므로 범위를 신중히 설정합니다.

## 4. 비용·감사

- Secret 저장 및 API 사용량에 따라 비용이 발생하며, 자동 Rotation에 Lambda를 사용하면 Lambda 비용이 추가될 수 있습니다.
- AWS CloudTrail을 활성화하면 Secrets Manager API 호출을 감사할 수 있습니다.
- 최신 가격과 리전별 조건은 공식 가격 문서에서 재확인합니다.
