---
name: buildkite-official-notes
description: Buildkite 하이브리드 구조(SaaS 제어 + 자체 에이전트)·pipeline.yml 단계·요금제·에이전트 판 공식 자료 정리 (SaaS, 실행 시험 없음).
tags:
  - buildkite
  - ci
  - saas
  - pricing
last_checked: 2026-11-26
sources:
  - https://buildkite.com/pricing
  - https://buildkite.com/docs/pipelines
  - https://buildkite.com/docs/pipelines/configure/defining-steps.md
  - https://buildkite.com/docs/agent/v3
  - https://buildkite.com/docs/agent/self-hosted.md
  - https://github.com/buildkite/agent/releases
---

# Buildkite 공식 자료 참조 노트

## 1. 구조

- Buildkite Pipelines는 SaaS 제어 화면이고, 빌드는 자체 인프라의 에이전트에서 돕니다. 에이전트는 Buildkite 에이전트 API를 HTTPS로 폴링하므로 들어오는 포트가 필요 없습니다.
- Buildkite가 관리하는 hosted agent(Linux·macOS·Windows, 일회성)도 있습니다.
- 에이전트는 조직 클러스터에 속한 에이전트 토큰과 self-hosted 큐가 필요합니다(토큰 페이지 세부는 미확인).

## 2. Pipeline

- 정의 파일 `pipeline.yml`(보통 `.buildkite/`), `buildkite-agent pipeline upload`로 올립니다. 빌드 중 단계를 추가로 올리는 동적 Pipeline이 가능합니다.
- 단계 종류: command, wait, block, input, trigger, group. wait로 나누지 않으면 단계는 병렬로 돕니다.

## 3. 요금제 (pricing, 2026-11-26 확인, USD)

| 요금제     | 가격                 | 주요 내용                                                                                 |
|------------|----------------------|-------------------------------------------------------------------------------------------|
| Free       | $0                   | 사용자 5명, 동시 작업 10, Linux vCPU 월 2,000분, 테스트 실행 월 25만                      |
| Pro        | 활성 사용자당 월 $30 | 사용자 50명까지, 에이전트 250개까지(10개 포함, 추가 개당 월 $3.50), Linux vCPU 월 4,000분 |
| Enterprise | 별도 문의            | SSO·SCIM, 로그 자체 저장, 가동률 99.95%, 자체 에이전트 무제한                             |

- hosted agent(Pro, vCPU 분당): Linux $0.004, macOS $0.02, Windows $0.008. 활성 사용자는 그 달에 접속한 고유 사용자.
- 30일 체험(카드 불필요), 오픈소스는 문의.

## 4. 에이전트 판

- 최신 v4.12.0(2026-11-19, 서명된 Job의 산출물 경로 서명·검증 추가, 검증하는 옛 에이전트를 먼저 올리라는 안내). v4.7.0(10-20)은 보안 릴리스(CVE-2026-111943).

## 5. 시험

SaaS라 계정 없이 실행하지 않았습니다.
