---
name: circleci-official-notes
description: CircleCI 요금제(크레딧)·설정 파일 구조·self-hosted runner 공식 자료 정리 (SaaS, 실행 시험 없음).
tags:
  - circleci
  - ci
  - saas
  - pricing
last_checked: 2026-11-26
sources:
  - https://circleci.com/pricing/
  - https://circleci.com/docs/reference/configuration-reference/
  - https://circleci.com/docs/runner/runner-overview/
  - https://circleci.com/docs/llms.txt
---

# CircleCI 공식 자료 참조 노트

## 1. 요금제 (pricing, 2026-11-26 확인, 세금 별도)

| 요금제      | 가격                 | 크레딧                                            | 사용자          | 동시 실행 |
|-------------|----------------------|---------------------------------------------------|-----------------|-----------|
| Free        | 월 $0                | 월 30,000 (매달 소멸)                             | 활성 사용자 5명 | 30        |
| Performance | 월 $15부터           | 30,000 포함, 25,000 추가마다 $15(구매분 1년 유효) | 5명 포함        | 80        |
| Scale       | 연간 청구, 별도 문의 | 협의                                              | 협의            | 무제한    |

- Performance 추가 사용자 비용은 페이지 안에서 "$15/month"와 "사용자당 25,000 크레딧"이 함께 보여 어느 쪽인지 미확인입니다.

## 2. 설정 (configuration-reference)

- 파일 `.circleci/config.yml`, `version`은 `2`·`2.0`·`2.1`(예시는 2.1).
- 최상위 키: `orbs`(재사용 패키지, 예 `circleci/node@x.y`), `executors`, `commands`, `parameters`, `jobs`, `workflows`.
- 실행 환경: `docker`, `machine`, `macos`, `windows`. Job마다 하나.

## 3. Self-hosted runner (runner-overview, 2026-11-13 수정)

- 종류: container runner(Kubernetes), machine runner(VM·물리), Machine Runner Orchestrator(KubeVirt 기반 자동 확장).
- 동작: runner가 `circleci.com`을 폴링해 작업을 가져오고 로그·산출물을 돌려보냄. `runner.circleci.com`으로 나가는 HTTPS만 필요, 들어오는 연결 불필요.
- 동시 실행: Free 5, Performance 20, Scale 무제한. 저장·네트워크용으로 크레딧이 최소 1 필요.

## 4. CircleCI Server

- 자체 호스팅판(GCP·AWS의 Kubernetes에 설치)은 llms.txt 요약에 "4.10", 최신 4.10.3으로 나오나 원문 페이지를 읽지 않아 미확인입니다.

## 5. 시험

SaaS라 계정 없이 실행하지 않았습니다.
