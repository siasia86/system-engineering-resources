---
name: aws-cdk-official-notes
description: AWS CDK CLI 2.1149.0과 라이브러리 2.278.0의 판 분리, init·synth 시험 결과, 자격 증명 필요 명령 정리.
tags:
  - aws-cdk
  - iac
  - aws
last_checked: 2026-11-27
sources:
  - https://github.com/aws/aws-cdk/releases
  - https://www.npmjs.com/package/aws-cdk
  - https://docs.aws.amazon.com/cdk/v2/guide/home.html
---

# AWS CDK 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- GitHub `aws/aws-cdk` 릴리스 v2.278.0(2026-11-20), v2.277.0(11-13), v2.276.0(11-10): 라이브러리 `aws-cdk-lib` 판.
- npm `aws-cdk`(CLI) dist-tags: latest 2.1149.0, latest-1 1.204.0. `npm install -g aws-cdk@2.278.0`은 `No matching version found`.

## 2. 컨테이너 시험 (2026-11-27, node:24-bookworm)

- `cdk --version` → `2.1149.0 (build c3b0413)`.
- `cdk init app --language typescript --generate-only` 뒤 `npm install`: `bin`, `lib`, `test`, `cdk.json`, `package.json`(`"aws-cdk-lib": "^2.277.0"`), `AGENTS.md` 등 생성. constructs 10.8.1.
- S3 Bucket(versioned, S3_MANAGED, BLOCK_ALL, enforceSSL, RETAIN) + SQS Queue 스택 `cdk synth`: 리소스 `AWS::CDK::Metadata`, `AWS::S3::Bucket`, `AWS::S3::BucketPolicy`, `AWS::SQS::Queue`, 파라미터 `BootstrapVersion`, 출력 2개. `cdk.out`에 `manifest.json`, `tree.json`, `AppStack.assets.json`, `AppStack.metadata.json`, `validation-report.json`.
- 경고 `1 feature flags are not configured. Run 'cdk flags --unstable=flags' to learn more.`
- `env`에 계정·리전 지정해도 synth 성공. `cdk diff`: `Need to perform AWS calls for account 111111111111, but no credentials have been configured`.
- 프로젝트 밖 실행: `--app is required either in command-line, in cdk.json or in ~/.cdk.json`.
- synth 결과 템플릿 cfn-lint 1.61.0 통과(종료 코드 0).
- 미실행: bootstrap, deploy, Python 등 다른 언어.
