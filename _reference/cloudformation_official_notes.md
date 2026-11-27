---
name: cloudformation-official-notes
description: CloudFormation 템플릿 구조와 cfn-lint 1.61.0 판, 오류 코드 시험 결과 정리.
tags:
  - cloudformation
  - cfn-lint
  - aws
last_checked: 2026-11-27
sources:
  - https://github.com/aws-cloudformation/cfn-lint/releases
  - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html
---

# CloudFormation 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- cfn-lint 최신 v1.61.0(2026-11-19), 이전 v1.60.1(11-12), v1.60.0(11-05). PyPI 설치 `cfn-lint==1.61.0`.
- AWS CLI 최신 태그 2.42.4.

## 2. cfn-lint 시험 (2026-11-27, Python 3, Debian 12)

- 틀린 템플릿(종료 코드 2):
  - `E3002 Additional properties are not allowed ('BucketNmae' was unexpected. Did you mean 'BucketName'?)`
  - `E3034 999999 is greater than the maximum of 43200` (SQS VisibilityTimeout)
  - `E6101 'Nothing' is not one of ['Bucket', 'Queue']` (`!GetAtt` 대상 없음)
- 정상 템플릿(Parameters·Retain·PublicAccessBlock·Outputs): 출력 없음, 종료 코드 0.
- 없는 파일 경로: `E0003 ... could not be processed by glob.glob`, 종료 코드 2.

## 3. 미실행

- `aws cloudformation deploy`, 변경 세트, drift 감지, 스택 정책(계정 필요).
