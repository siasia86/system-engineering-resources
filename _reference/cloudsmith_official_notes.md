---
name: cloudsmith-official-notes
description: Cloudsmith(SaaS 패키지 저장소) 형식·업스트림·엔타이틀먼트 토큰·보존 규칙·요금제 공식 자료 정리 (상용, 실행 시험 없음).
tags:
  - cloudsmith
  - artifact-repository
  - saas
  - pricing
last_checked: 2026-11-24
sources:
  - https://docs.cloudsmith.com/formats
  - https://docs.cloudsmith.com/repositories/upstreams
  - https://docs.cloudsmith.com/software-distribution/entitlement-tokens
  - https://docs.cloudsmith.com/artifact-management/retention-rules
  - https://docs.cloudsmith.com/support/billing
  - https://docs.cloudsmith.com/resources/open-source-hosting-policy
  - https://cloudsmith.com/solutions/global-software-distribution
  - https://pypi.org/pypi/cloudsmith-cli/json
---

# Cloudsmith 공식 자료 참조 노트

## 1. 개요 (2026-11-24)

- 완전 관리형 SaaS로, 직접 운영할 서버가 없습니다(공식 소개). 자체 호스팅판이 없다는 명시 문장은 따로 확인하지 못했습니다.
- 배포는 엣지 캐시(공급사 표기 600개 이상 PoP)를 거칩니다.
- CLI: `cloudsmith-cli` 1.31.4 (PyPI 2026-11-23 업로드, Python 3.11 이상).

## 2. 기능

| 항목              | 내용                                                                                                       | 근거                        |
|-------------------|------------------------------------------------------------------------------------------------------------|-----------------------------|
| 형식              | 34개 (Alpine, Cargo, Debian, Docker, Go, Helm, Maven, npm, NuGet, OCI, Python, Raw, Red Hat, Terraform 등) | formats 문서                |
| 업스트림          | Proxy only, Cache and proxy, Cache only(strict) 세 방식. 캐시는 24개 형식                                  | upstreams 문서              |
| 엔타이틀먼트 토큰 | 사용자·고객이 파일을 받을 때 쓰는 읽기 전용 토큰                                                           | entitlement-tokens          |
| 보존 규칙         | 개수·크기·일수 기준, 저장소당 규칙 1개, 올리기·동기화 때 실행, 한 번에 최대 1,000건 삭제, 기본 꺼짐        | retention-rules (검색 요약) |

## 3. 요금제

- 요금제: Core(무료, 작은 데이터·전송 허용량), Pro, Ultra, Enterprise. 유료 요금제는 허용량을 넘으면 GB 단위로 과금하고, Ultra는 연간 청구서 결제를 고를 수 있습니다(billing 문서).
- 오픈소스 저장소: 모든 오픈소스 저장소를 합쳐 최소 50GB 저장과 200GB 전송이 무료이며, 따로 요금제에 가입하지 않고 오픈소스 저장소를 만들면 됩니다. 자유·오픈소스 프로젝트이고 관리자여야 합니다(open-source hosting policy).
- 요금제별 월 가격과 허용량은 미확인입니다. 가격 페이지(https://cloudsmith.com/pricing)가 두 번 모두 HTTP 429로 열리지 않았습니다.

## 4. 시험

상용 SaaS라 계정 없이 실행하지 않았습니다.
