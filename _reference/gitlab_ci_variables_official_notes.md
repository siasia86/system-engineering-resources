---
name: gitlab-ci-variables-official-notes
description: GitLab CI/CD Variable의 저장·보호·Masking·File 유형과 AWS OIDC 연동 공식 문서 검증 노트.
tags:
  - gitlab
  - ci-cd
  - variables
  - oidc
last_checked: 2026-08-19
sources:
  - https://docs.gitlab.com/ci/variables/
  - https://docs.gitlab.com/ci/variables/variables_troubleshooting/
  - https://docs.gitlab.com/ci/cloud_services/aws/
---

# GitLab CI/CD Variables 공식 문서 참조 노트

## 1. CI/CD Variable

- CI/CD Variable은 Pipeline과 Job의 동작을 제어하고 재사용 값을 전달하는 환경변수입니다.
- 민감한 Token·Password는 `.gitlab-ci.yml`에 저장하지 않고 GitLab 설정의 Variable로 관리합니다.
- Variable은 Project 또는 Group 범위와 Environment Scope를 사용할 수 있습니다.
- Variable 유형에는 일반 Variable과 File Variable이 있습니다.

## 2. Protected와 Masked

- Protected Variable은 Protected Branch 또는 Protected Tag에서 실행되는 Pipeline에만 제공합니다.
- Masked 또는 Masked and hidden은 로그에서 값 노출을 줄이는 기능이며, Job이 값을 파일·Artifact·외부 시스템으로 유출하는 것을 차단하지 않습니다.
- Pipeline에서 `export`, `env`, Debug Trace를 사용하면 변수와 Secret이 노출될 수 있습니다.
- Fork 기반 Pipeline과 Parent Project에서 실행하는 Fork Merge Request Pipeline은 변수 접근 범위를 구분하여 검토해야 합니다.

## 3. AWS OIDC

- GitLab CI Job의 ID Token으로 AWS IAM OIDC Federation을 구성하면 장기 AWS Secret 없이 STS 임시 자격증명을 받을 수 있습니다.
- AWS Role Trust Policy는 GitLab Project·Group·Branch·Tag에 해당하는 조건으로 범위를 제한합니다.
- Self-Managed GitLab은 AWS 조건 키 지원 범위가 GitLab.com과 다를 수 있으므로 `sub`와 `aud` 조건을 공식 문서 기준으로 확인합니다.
- CI Job은 임시 자격증명으로 AWS Secrets Manager 등 필요한 서비스에 최소 권한으로 접근합니다.

## 4. 운영 주의사항

- Secret 값을 `echo`, `env`, `printenv`, Debug Trace로 출력하지 않습니다.
- 보호되지 않은 Runner, 비신뢰 Merge Request, Artifact·Cache에 Secret을 전달하지 않습니다.
- 배포 후 임시 파일을 삭제하고 Job 로그와 Artifact 보존 기간을 관리합니다.
