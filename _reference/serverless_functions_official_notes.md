---
name: serverless-functions-official-notes
description: AWS Lambda·Azure Functions·Cloud Run functions의 무료 한도, 요금, 실행 제한, 호스팅 플랜 변경을 공식 문서 기준으로 정리, 미확인 표시.
tags:
  - aws-lambda
  - azure-functions
  - cloud-run-functions
  - serverless
last_checked: 2026-11-27
sources:
  - https://aws.amazon.com/lambda/pricing/
  - https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html
  - https://azure.microsoft.com/en-us/pricing/details/functions/
  - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
  - https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan
  - https://docs.cloud.google.com/functions/docs/concepts/version-comparison
  - https://docs.cloud.google.com/run/quotas
---

# 서버리스 함수 공식 자료 참조 노트

## 1. AWS Lambda (2026-11-27)

- 무료: "The free tier includes one million requests and 400,000 GB-seconds per month." 미국 동부 예시 요청 100만당 $0.20, x86 GB-s당 $0.0000166667. 표준 함수 Arm 단가는 표가 렌더링되지 않아 미확인.
- Provisioned Concurrency GB-s $0.0000041667(용량) + $0.0000097222(실행), 무료 한도 미적용. SnapStart 캐시는 최소 3시간 과금.
- 제한: 시간 "1,800 seconds (30 minutes)"(표준), 메모리 "128 MB to 10,240 MB, in 1-MB increments", zip 50MB(API), 풀면 250MB, 컨테이너 이미지 10GB, 동기 페이로드 6MB, 동시 실행 기본 1,000(리전), 함수당 10초마다 1,000 환경 확장, `/tmp` 512~10,240MB. "New AWS accounts have reduced concurrency and memory quotas".
- INIT 단계 과금 변경은 요금 페이지에서 찾지 못함.

## 2. Azure Functions

- Consumption 무료: "1 million requests and 400,000 GB-s of resource consumption per month per subscription". Flex Consumption 무료: "250,000 executions and 100,000 GB-s". 단가는 `$-`로 표시돼 미확인. Premium은 실행 요금 없음, 최소 1개 인스턴스.
- 플랜(2026-11-17 갱신): Flex Consumption·Premium·Dedicated·Container Apps GA, Consumption legacy(Windows GA, Linux Retired 표기). 시간: Flex·Premium·Dedicated 기본 30분·최대 제한 없음, Consumption 5분·10분. HTTP 응답 최대 230초. 요청 최대 210MB.
- Flex: 인스턴스 512MB(0.25 CPU)·2048MB(1 CPU)·4096MB(2 CPU), always ready 기본 0, 지역 할당 250 코어, 컨테이너 이미지 미리 보기, 언어 C# isolated(.NET 8~11)·Python 3.10~3.15·Node.js 22·24(26 미리 보기)·Go 1.24+·Java 8~25·PowerShell 7.4·7.6·custom handler.
- "The option to host function apps on Linux in a Consumption plan is retiring on 30 September 2028." Linux Consumption v3 런타임은 2026-09-30 이후 중지.

## 3. Cloud Run functions

- 2nd gen이 Cloud Run functions, 1st gen은 "Cloud Run functions (1st gen)". 2024-08부터 Cloud Run Admin API로 관리 가능. 컨테이너로 빌드돼 Cloud Run 서비스로 배포.
- HTTP 최대 60분, 이벤트(v2 API) 9분, 최대 16GiB·4 vCPU, 인스턴스당 동시 요청 1,000. 1st gen 9분, 8GB·2 vCPU, 동시 1.
- Cloud Run 할당량: 32GiB·8 vCPU, 프로젝트·리전당 인스턴스 100, 요청 최대 60분, HTTP/1 요청 32MiB, 이미지 크기 직접 제한 없음.
- 요금 페이지(functions·run pricing)는 제목만 읽혀 무료 한도·단가 미확인. 최소 인스턴스 문서 404.
