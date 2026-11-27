# 서버리스 함수 비교 (AWS Lambda · Azure Functions · Cloud Run functions)
<!-- reference: _reference/serverless_functions_official_notes.md -->

요청·이벤트가 올 때만 코드를 실행하고 실행한 만큼 내는 서버리스 함수 세 가지를 무료 한도, 요금, 실행 제한, 콜드 스타트 대책, 최근 변경으로 비교합니다. 서버를 직접 운영하지 않는 대신 실행 시간·메모리·패키지 크기 제한 안에서 설계해야 합니다.

- 확인일: 2026-11-27, 각 사업자의 공식 요금·제한 문서 기준
- 예제 시험: 계정이 필요해 실행하지 않음. Google Cloud Run functions 요금, Azure Functions 단가, Lambda Arm 단가는 페이지 내용을 읽지 못해 미확인

## 목차

| 섹션                                                                                        |
|---------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 한눈에 비교](#2-한눈에-비교) / [3. AWS Lambda](#3-aws-lambda)      |
| [4. Azure Functions](#4-azure-functions) / [5. Cloud Run functions](#5-cloud-run-functions) |
| [6. 고르는 기준과 주의](#6-고르는-기준과-주의) / [함께 보기](#함께-보기)                    |

---

## 1. 개요

```text
event (HTTP, queue, storage, schedule) --> [platform starts instance if none warm] --> handler(event) --> response
                                              cold start: load runtime + code + init
```

| 용어        | 뜻                                                                                |
|-------------|-----------------------------------------------------------------------------------|
| GB-초(GB-s) | 할당한 메모리(GB) × 실행 시간(초). 대부분의 요금 단위                             |
| 콜드 스타트 | 따뜻한 인스턴스가 없어 런타임·코드를 새로 올리는 지연                             |
| 동시성      | 동시에 처리하는 요청 수. 인스턴스당 1개(Lambda) 또는 여러 개(Cloud Run functions) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 항목              | AWS Lambda                                   | Azure Functions(Flex Consumption)            | Cloud Run functions                                           |
|-------------------|----------------------------------------------|----------------------------------------------|---------------------------------------------------------------|
| 월 무료 한도      | 요청 100만, 40만 GB-s                        | 실행 25만, 10만 GB-s(구독당)                 | 미확인                                                        |
| 요금(예시)        | 요청 100만당 $0.20, x86 GB-s당 $0.0000166667 | 미확인(요금 페이지 금액 미표시)              | 미확인                                                        |
| 최대 실행 시간    | 1,800초(30분, 표준 함수)                     | 기본 30분, 최대 제한 없음(HTTP 응답은 230초) | HTTP 60분, 이벤트 9분                                         |
| 메모리            | 128MB~10,240MB                               | 인스턴스 512MB·2,048MB·4,096MB               | 최대 16GiB·4 vCPU                                             |
| 패키지·이미지     | zip 50MB(풀면 250MB), 컨테이너 이미지 10GB   | 컨테이너 이미지는 미리 보기                  | 소스를 컨테이너로 빌드, 이미지 크기 직접 제한 없음(Cloud Run) |
| 인스턴스당 동시성 | 1                                            | 인스턴스당 최대 동시 실행 수 설정            | 최대 1,000                                                    |
| 콜드 스타트 대책  | Provisioned Concurrency, SnapStart           | always ready 인스턴스(기본 0)                | 최소 인스턴스(미확인)                                         |

- Lambda 표준 함수의 최대 시간은 공식 제한 문서 기준 1,800초(30분)입니다. 예전 자료의 900초(15분)와 다르므로 판을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. AWS Lambda

- 무료: 매월 요청 100만 건, 40만 GB-s. 미국 동부(버지니아 북부) 예시 단가 요청 100만당 $0.20, x86 GB-s당 $0.0000166667.
- 제한: 메모리 128~10,240MB(1MB 단위), 표준 함수 시간 최대 30분, 동기 요청·응답 6MB, `/tmp` 512MB~10,240MB, 리전당 기본 동시 실행 1,000(늘릴 수 있음). 새 계정은 동시성·메모리 할당량이 낮게 시작합니다.
- 패키지: zip 50MB(API 업로드), 풀었을 때 레이어 포함 250MB, 컨테이너 이미지 10GB.
- 콜드 스타트: Provisioned Concurrency는 미리 초기화한 환경을 유지(별도 요금, 무료 한도 미적용). SnapStart는 초기화된 메모리·디스크 상태를 스냅숏으로 캐시해 시작을 줄입니다(캐시는 최소 3시간 과금).

[⬆ 목차로 돌아가기](#목차)

---

## 4. Azure Functions

| 호스팅 플랜      | 상태           | 시간(기본/최대)             | 메모리              | 특징                                       |
|------------------|----------------|-----------------------------|---------------------|--------------------------------------------|
| Flex Consumption | GA, 새 앱 권장 | 30분 / 제한 없음            | 512MB~4GB(인스턴스) | always ready, 인스턴스 최대 1,000          |
| Premium          | GA             | 30분 / 제한 없음            | 3.5~14GB            | 최소 1개 인스턴스 상시, 실행 요금 없음     |
| Dedicated        | GA             | 30분 / 제한 없음(Always On) | 플랜에 따름         | App Service 요금                           |
| Consumption      | legacy         | 5분 / 10분                  | 1.5GB               | Linux는 2028-09-30 종료 예정, 새 기능 없음 |

- Consumption 무료 한도: 구독당 매월 요청 100만, 40만 GB-s. Flex Consumption 무료 한도: 구독당 실행 25만, 10만 GB-s.
- HTTP 트리거 함수는 230초 안에 응답해야 합니다. 긴 작업은 Durable Functions나 큐로 나눕니다.
- 언어(Flex): C#(isolated worker, .NET 8~11), Python 3.10~3.15, Node.js 22·24(26 미리 보기), Go 1.24 이상, Java 8~25, PowerShell 7.4·7.6, 사용자 지정 핸들러. in-process C# 모델은 Flex에서 지원하지 않습니다.
- Linux Consumption의 v3 런타임 앱은 2026-09-30 이후 동작하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Cloud Run functions

- 예전 이름 Cloud Functions(2nd gen)가 Cloud Run functions가 됐고, 1st gen은 "Cloud Run functions (1st gen)"으로 부릅니다. 함수는 컨테이너로 빌드돼 Cloud Run 서비스로 배포됩니다.
- 제한: HTTP 함수 최대 60분, 이벤트 함수(v2 API) 9분, 인스턴스 최대 16GiB·4 vCPU, 인스턴스당 동시 요청 최대 1,000. 1st gen은 9분, 8GB·2 vCPU, 인스턴스당 1요청.
- Cloud Run 할당량: 인스턴스 메모리 최대 32GiB·8 vCPU, 프로젝트·리전당 인스턴스 100개(조정 가능), HTTP/1 요청 32MiB.
- 요금·무료 한도와 최소 인스턴스 설정은 페이지를 읽지 못해 미확인입니다. Google Cloud 요금 페이지에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 고르는 기준과 주의

- 이미 쓰는 클라우드의 이벤트 소스(S3·SQS, Blob·Service Bus, Pub/Sub·Eventarc)와 붙이기 쉬운 쪽을 고릅니다.
- 인스턴스당 동시 처리가 필요한 HTTP API는 Cloud Run functions·Azure Flex의 동시성 설정이 비용에 유리할 수 있고, Lambda는 요청마다 환경이 하나라 동시 요청이 많으면 동시 실행 할당량을 먼저 봅니다.
- 실행 시간이 긴 작업(수십 분 이상)은 함수보다 컨테이너 작업([ECS·Fargate](../containers/managed_container_platforms.md) 등)이 맞는 경우가 많습니다.
- DB 연결 수: 함수 인스턴스가 늘면 DB 연결이 폭증합니다. 연결 풀 프록시(RDS Proxy 등)를 검토합니다.
- 두 번째부터 네 번째 항목은 공식 문서와 따로 대조하지 않은 일반 설계 고려입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [PaaS 비교](./paas_comparison.md) — Cloudflare, Vercel, Netlify, Render, Railway, Heroku
- [관리형 컨테이너 플랫폼 비교](../containers/managed_container_platforms.md) — ECS·Fargate, EKS
- [AWS 개요](./aws_overview.md) — 요금·계정 구조

---

## 참고 자료

- AWS: [Lambda pricing](https://aws.amazon.com/lambda/pricing/) · [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) — ★★★☆☆
- Azure: [Functions pricing](https://azure.microsoft.com/en-us/pricing/details/functions/) · [Hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale) · [Flex Consumption](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan) — ★★★☆☆
- Google Cloud: [Cloud Run functions version comparison](https://docs.cloud.google.com/functions/docs/concepts/version-comparison) · [Cloud Run quotas](https://docs.cloud.google.com/run/quotas) — ★★★☆☆

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
