---
name: octopus-deploy-official-notes
description: Octopus Deploy 요금제·핵심 개념(환경·수명 주기·Tentacle·런북·테넌트)·판 공식 자료 정리 (상용 CD 도구, 실행 시험 없음).
tags:
  - octopus-deploy
  - cd
  - deployment
  - pricing
last_checked: 2026-11-26
sources:
  - https://octopus.com/pricing
  - https://octopus.com/docs
  - https://octopus.com/docs/projects
  - https://octopus.com/docs/infrastructure
  - https://octopus.com/docs/releases
  - https://octopus.com/docs/tenants
  - https://octopus.com/docs/runbooks
  - https://octopus.com/downloads
---

# Octopus Deploy 공식 자료 참조 노트

## 1. 위치

- 배포(CD) 전용 플랫폼입니다. 문서 표현: "Octopus takes over where your CI server ends", 원칙 "CI is not CD". 빌드는 GitHub Actions·Jenkins·TeamCity 등이 하고, 패키지를 넘겨받아 릴리스·배포를 맡습니다.
- 내려받기 페이지의 CI 연동: GitHub Actions, TeamCity, Azure DevOps, Jenkins(패키지 올리기·릴리스 만들기·배포).

## 2. 요금제 (pricing, 2026-11-26 확인, 연간 청구만)

| 요금제       | Cloud (연) | Server (연) | 주요 한도·기능                                                          |
|--------------|------------|-------------|-------------------------------------------------------------------------|
| Free         | $0         | $0          | 프로젝트·테넌트·머신·사용자 각 10, 스페이스 1, 동시 작업 5, 기한 없음   |
| Professional | $4,330     | $2,080      | 프로젝트 20~100 선택, 사용자 무제한, 동시 작업 5(최대 20), 8/5 지원     |
| Enterprise   | $24,600    | $15,600     | 프로젝트 100~1,000, 동시 작업 20(최대 160), 24/7 지원, 감사 스트리밍 등 |

- 추가: 테넌트·머신 각 연 $770(10~1,000 선택). 머신은 Tentacle 하나·SSH 연결 하나가 1개.
- Cloud는 Azure(West US 2, West Europe, Australia East)에서 운영.

## 3. 개념

| 개념              | 뜻                                          |
|-------------------|---------------------------------------------|
| Project           | 한 앱·서비스의 배포 절차·릴리스·런북 묶음   |
| Environment       | 목적별 인프라 묶음(Dev·Test·Prod)           |
| Lifecycle         | 운영까지 거치는 환경 순서(Phase)            |
| Deployment target | 서버·플랫폼·서버리스 함수                   |
| Tentacle          | Windows·Linux 대상에 설치하는 경량 에이전트 |
| Release           | 배포 절차와 패키지의 스냅숏                 |
| Tenant            | 한 프로젝트를 고객·지점별로 복제 없이 배포  |
| Runbook           | 배포와 별개인 운영·장애 대응 작업 자동화    |

- Config as Code(OCL 형식으로 Git에 저장) 페이지는 읽지 않아 세부는 미확인입니다.

## 4. 판

- Octopus Server 2026.3.16217 (내려받기 페이지 "latest", 날짜 표시 없음). 설치: MSI, Chocolatey, Docker(`octopusdeploy/octopusdeploy`, SQL Server 2016 이상 필요), Helm.

## 5. 시험

상용 제품이라 실행하지 않았습니다.
