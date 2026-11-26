---
name: teamcity-official-notes
description: JetBrains TeamCity 판·라이선스(무료 Professional 한도)·Kotlin DSL·Docker 이미지 공식 자료 정리 (상용, 실행 시험 없음).
tags:
  - teamcity
  - jetbrains
  - ci
  - kotlin-dsl
last_checked: 2026-11-26
sources:
  - https://www.jetbrains.com/help/teamcity/teamcity-documentation.html
  - https://www.jetbrains.com/help/teamcity/teamcity-2026-2-release-notes.html
  - https://www.jetbrains.com/help/teamcity/licensing-policy.html
  - https://www.jetbrains.com/help/teamcity/kotlin-dsl.html
  - https://hub.docker.com/r/jetbrains/teamcity-server
  - https://hub.docker.com/r/jetbrains/teamcity-agent
  - https://www.jetbrains.com/teamcity/buy/
---

# TeamCity 공식 자료 참조 노트

## 1. 판 (2026-11-26)

- 문서 판: 2026.2. 2026.2 릴리스 노트 "Build 238924, 2 September 2026".
- 2026.2.1 릴리스 노트 페이지가 링크되어 있으나 읽지 않아 날짜는 미확인입니다.
- 내려받기·구매 페이지는 자동 조회에서 메뉴만 읽혀 판·가격을 확인하지 못했습니다.

## 2. 라이선스 (licensing-policy, 2026-05-27 수정)

| 판              | 내용                                                                                                                                                                               |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Professional    | 무료. 빌드 에이전트 3개 포함(추가 구매 가능), 빌드 구성 100개·파이프라인 10개까지(보관 포함). 에이전트 라이선스 1개마다 빌드 구성 10개 추가. 지원은 커뮤니티 포럼·공개 이슈 트래커 |
| Enterprise      | 유료 라이선스 키. 빌드 구성·파이프라인 무제한, 1년 업그레이드 구독, 우선 지원                                                                                                      |
| Enterprise Plus | 분기별 정산(true-up) 에이전트                                                                                                                                                      |

- Enterprise·Cloud 가격은 미확인입니다.

## 3. 설정과 설치

- Kotlin DSL: 프로젝트의 versioned settings를 켜고 형식을 Kotlin으로 고르면 TeamCity가 `.teamcity/settings.kts`(전체 설정)와 `pom.xml`을 저장소에 커밋합니다. 로컬 생성 `mvn teamcity-configs:generate`.
- Docker: `jetbrains/teamcity-server`(포트 8111, 데이터 `/data/teamcity_server/datadir`), `jetbrains/teamcity-agent`(`SERVER_URL` 환경 변수), `jetbrains/teamcity-minimal-agent`.

## 4. 시험

상용 제품이라 실행하지 않았습니다. 무료 Professional로 자체 설치해 시험할 수 있으나 이번 범위에서 제외했습니다.
