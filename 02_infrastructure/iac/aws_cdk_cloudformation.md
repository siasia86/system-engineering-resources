# AWS CDK와 CloudFormation
<!-- reference: _reference/aws_cdk_official_notes.md, _reference/cloudformation_official_notes.md -->

CloudFormation은 AWS 리소스를 JSON·YAML 템플릿으로 선언하고 스택 단위로 만들고 바꾸는 AWS의 IaC 서비스입니다. AWS CDK는 TypeScript·Python 같은 일반 언어로 인프라를 쓰면 CloudFormation 템플릿을 만들어(synth) 배포하는 도구입니다. 이 문서는 템플릿 구조, cfn-lint 검사, CDK 프로젝트 만들기와 synth를 로컬에서 따라 하고, 배포 흐름을 정리합니다.

- 기준 판: AWS CDK CLI(`aws-cdk`) 2.1149.0, CDK 라이브러리(`aws-cdk-lib`) 2.278.0 (2026-11-20), cfn-lint 1.61.0 (2026-11-19) (2026-11-27 확인)
- 예제 시험: 2026-11-27 2~5절을 컨테이너(Node.js 24, Python 3)에서 실행해 cfn-lint 오류 탐지, `cdk init`·`cdk synth`·`cdk ls`, 자격 증명 없는 `cdk diff` 실패를 확인. AWS 계정이 필요한 `cdk bootstrap`·`cdk deploy`·`aws cloudformation deploy`, 변경 세트, drift 감지는 미실행

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. CloudFormation 템플릿](#2-cloudformation-템플릿) / [3. cfn-lint](#3-cfn-lint) |
| [4. CDK 프로젝트](#4-cdk-프로젝트) / [5. synth와 배포 흐름](#5-synth와-배포-흐름) / [6. 비교](#6-비교) |
| [7. 검증](#7-검증) / [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기)                          |

---

## 1. 개요

```text
CDK app (TypeScript/Python)
    │  cdk synth
    v
CloudFormation template (JSON) + assets ---- cfn-lint (static check)
    │  cdk deploy / aws cloudformation deploy
    v
CloudFormation stack (create / update / rollback) --> AWS resources
```

| 항목   | CloudFormation                           | CDK                                        |
|--------|------------------------------------------|--------------------------------------------|
| 작성   | JSON·YAML 템플릿                         | 일반 언어 코드(construct 조합)             |
| 상태   | AWS가 스택으로 관리(별도 상태 파일 없음) | 같음(결국 CloudFormation 스택)             |
| 추상화 | 리소스 하나씩                            | 여러 리소스를 묶은 construct(L2·L3)        |
| 준비   | AWS CLI                                  | Node.js + CDK CLI, 계정·리전마다 bootstrap |

[⬆ 목차로 돌아가기](#목차)

---

## 2. CloudFormation 템플릿

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: S3 bucket with versioning
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prd]
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      VersioningConfiguration: { Status: Enabled }
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      Tags:
        - { Key: env, Value: !Ref Env }
Outputs:
  BucketArn:
    Value: !GetAtt Bucket.Arn
```

| 절                                      | 뜻                                                 |
|-----------------------------------------|----------------------------------------------------|
| `Parameters`                            | 배포할 때 넣는 값                                  |
| `Resources`                             | 만들 리소스(필수). 논리 ID와 `Type`, `Properties`  |
| `Outputs`                               | 다른 스택·사람에게 넘길 값                         |
| `!Ref`, `!GetAtt`                       | 파라미터·리소스 참조, 리소스 속성(ARN 등) 가져오기 |
| `DeletionPolicy`, `UpdateReplacePolicy` | 스택 삭제·교체 때 실제 리소스를 남길지(`Retain`)   |

- 데이터가 든 리소스(S3, RDS, DynamoDB)는 `DeletionPolicy: Retain`으로 스택을 지워도 남게 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. cfn-lint

AWS가 관리하는 CloudFormation 템플릿 정적 검사 도구입니다. 리소스 속성 이름·값 범위·참조를 리소스 명세와 대조합니다.

```bash
pip install cfn-lint==1.61.0
cfn-lint template.yaml        # 문제 없으면 출력 없이 종료 코드 0
```

시험에서 일부러 틀린 템플릿을 검사한 결과입니다(종료 코드 2).

```text
E3002 Additional properties are not allowed ('BucketNmae' was unexpected. Did you mean 'BucketName'?)
/w/bad.yaml:6:7
E3034 999999 is greater than the maximum of 43200
/w/bad.yaml:10:7
E6101 'Nothing' is not one of ['Bucket', 'Queue']
/w/bad.yaml:13:5
```

- 속성 오탈자, SQS `VisibilityTimeout` 최대값(43200초) 초과, 없는 리소스 참조를 배포 전에 잡았습니다.
- 2절의 정상 템플릿과 CDK가 만든 템플릿은 출력 없이 종료 코드 0이었습니다.
- CI에서는 템플릿이 바뀐 커밋마다 돌립니다. 배포해야 알 수 있는 오류(권한, 이름 중복, 할당량)는 잡지 못합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. CDK 프로젝트

```bash
npm install -g aws-cdk@2.1149.0      # CLI
mkdir app && cd app
cdk init app --language typescript   # bin/, lib/, cdk.json, package.json 생성
npm install
```

- CLI(`aws-cdk`)와 라이브러리(`aws-cdk-lib`)는 판 번호가 따로입니다. GitHub `aws/aws-cdk`의 v2.278.0은 라이브러리 판이고, `npm install -g aws-cdk@2.278.0`은 `No matching version found`로 실패했습니다. CLI 최신은 2.1149.0이었습니다.
- 시험에서 `cdk init`이 만든 `package.json`의 라이브러리 범위는 `"aws-cdk-lib": "^2.277.0"`였습니다.

`lib/app-stack.ts` 예시(S3 버킷과 SQS 큐):

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';

export class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const bucket = new s3.Bucket(this, 'Logs', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
    const q = new sqs.Queue(this, 'Jobs', { visibilityTimeout: cdk.Duration.seconds(300) });
    new cdk.CfnOutput(this, 'BucketName', { value: bucket.bucketName });
    new cdk.CfnOutput(this, 'QueueUrl', { value: q.queueUrl });
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. synth와 배포 흐름

```bash
cdk synth            # cdk.out/AppStack.template.json 생성 (자격 증명 없이 가능)
cdk ls               # 스택 목록
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>   # 계정·리전마다 한 번 (미실행)
cdk diff             # 배포된 스택과 비교 (자격 증명 필요)
cdk deploy           # 변경 적용 (미실행)
```

- 시험한 synth 결과 리소스: `AWS::S3::Bucket`, `AWS::S3::BucketPolicy`, `AWS::SQS::Queue`, `AWS::CDK::Metadata`. `enforceSSL: true` 한 줄로 HTTPS만 허용하는 버킷 정책이 따로 만들어졌고, 템플릿에 `BootstrapVersion` 파라미터가 붙었습니다.
- `cdk.out`에는 템플릿 외에 `manifest.json`, `tree.json`, `AppStack.assets.json`, `validation-report.json`이 생겼습니다.
- `bin/app.ts`에 `env: { account, region }`을 적어도 synth는 자격 증명 없이 됐지만, `cdk diff`는 `Need to perform AWS calls for account 111111111111, but no credentials have been configured`로 실패했습니다.
- CloudFormation 템플릿을 직접 배포할 때는 `aws cloudformation deploy --template-file template.yaml --stack-name <이름> --parameter-overrides Env=dev`를 씁니다(미실행).
- 운영 스택은 변경 세트(change set)로 바뀔 리소스, 특히 교체(Replacement)되는 리소스를 먼저 확인합니다(미실행).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 비교

| 항목      | CloudFormation | CDK                              | [Terraform](./terraform.md) | [Pulumi](./pulumi.md)          |
|-----------|----------------|----------------------------------|-----------------------------|--------------------------------|
| 대상      | AWS            | AWS(CloudFormation으로 배포)     | 여러 클라우드               | 여러 클라우드                  |
| 언어      | JSON·YAML      | TypeScript, Python, Java, C#, Go | HCL                         | 일반 언어, YAML                |
| 상태      | AWS 스택       | AWS 스택                         | 상태 파일(원격 backend)     | Pulumi Cloud 또는 자체 backend |
| 로컬 검사 | cfn-lint       | synth + cfn-lint                 | `terraform validate`·`plan` | `pulumi preview`               |

- AWS만 쓰고 AWS가 상태를 관리해 주길 원하면 CloudFormation·CDK, 여러 클라우드나 SaaS를 함께 다루면 Terraform·Pulumi가 맞습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 검증

| 순서 | 확인 내용   | 방법                                  | 기대 결과                           |
|------|-------------|---------------------------------------|-------------------------------------|
| 1    | CLI         | `cdk --version`, `cfn-lint --version` | 2.1149.0, 1.61.0                    |
| 2    | 템플릿      | `cfn-lint template.yaml`              | 출력 없음, 종료 코드 0              |
| 3    | synth       | `cdk synth`                           | `cdk.out/<스택>.template.json` 생성 |
| 4    | 생성 리소스 | 템플릿의 `Resources` 타입 목록        | 코드에서 의도한 리소스              |
| 5    | 변경 확인   | `cdk diff`(계정 필요)                 | 바뀔 리소스와 교체 여부             |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                                      | 원인                          | 조치                                                     |
|---------------------------------------------------------------------------|-------------------------------|----------------------------------------------------------|
| `No matching version found for aws-cdk@2.278.0`                           | 라이브러리 판을 CLI 판으로 씀 | CLI는 `aws-cdk@2.1xxx`, 라이브러리는 `aws-cdk-lib@2.2xx` |
| `--app is required either in command-line, in cdk.json or in ~/.cdk.json` | CDK 프로젝트 폴더 밖에서 실행 | `cdk.json`이 있는 폴더에서 실행                          |
| `Need to perform AWS calls ... no credentials have been configured`       | diff·deploy에 자격 증명 없음  | `aws configure sso` 등으로 자격 증명 설정                |
| `E3002 Additional properties are not allowed`                             | 속성 이름 오탈자              | 제안된 이름으로 수정                                     |
| 스택 삭제 뒤 데이터도 사라짐                                              | `DeletionPolicy` 미지정       | 데이터 리소스에 `Retain`, CDK는 `RemovalPolicy.RETAIN`   |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Terraform](./terraform.md) — 여러 클라우드 IaC
- [Pulumi](./pulumi.md) — 일반 언어 IaC, 자체 backend
- [AWS 개요](../cloud_aws/aws_overview.md) — 계정·리전·서비스 지도

---

## 참고 자료

- AWS CDK: [Developer Guide](https://docs.aws.amazon.com/cdk/v2/guide/home.html) · [aws/aws-cdk releases](https://github.com/aws/aws-cdk/releases) · [npm aws-cdk](https://www.npmjs.com/package/aws-cdk) — ★★★☆☆
- CloudFormation: [User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) · [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
