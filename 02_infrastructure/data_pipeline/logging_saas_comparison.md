# 로깅 도구 비교 (Splunk·Papertrail과 자체 운영)
<!-- reference: _reference/splunk_official_notes.md, _reference/papertrail_official_notes.md, _reference/elastic_stack_official_notes.md, _reference/loki_official_notes.md, _reference/graylog_official_notes.md -->

로그를 상용 제품(Splunk, Papertrail)에 맡길지, Elastic Stack·Loki·Graylog로 직접 운영할지 고르는 기준을 정리한 문서입니다. 상용 제품은 계정·비용 없이 확인할 수 있는 공식 페이지 범위만 다룹니다. 자체 운영 도구의 설치와 검증은 각 문서에 있습니다.

- 기준: 2026-11-23 각 공식 페이지, Elasticsearch 9.5.6, Loki 3.7.10, Graylog 7.2.2
- 예제 시험: Splunk·Papertrail은 미실행(상용). 자체 운영 도구는 각 문서에서 컨테이너로 시험했습니다. 요금은 바뀔 수 있으므로 결정 전에 공식 페이지를 다시 확인합니다

## 목차

| 섹션                                                                                                  |
|-------------------------------------------------------------------------------------------------------|
| [1. 한눈에 비교](#1-한눈에-비교) / [2. 비용 구조](#2-비용-구조) / [3. 고르는 기준](#3-고르는-기준)    |
| [4. 옮길 때 확인할 것](#4-옮길-때-확인할-것) / [5. 확인 방법](#5-확인-방법) / [함께 보기](#함께-보기) |

---

## 1. 한눈에 비교

| 항목      | Splunk                            | Papertrail                           | Elastic Stack                    | Loki                             | Graylog                   |
|-----------|-----------------------------------|--------------------------------------|----------------------------------|----------------------------------|---------------------------|
| 형태      | 자체 설치(Enterprise)·SaaS(Cloud) | SaaS                                 | 자체 운영 (Elastic Cloud도 있음) | 자체 운영 (Grafana Cloud도 있음) | 자체 운영                 |
| 색인      | 본문 전체                         | 본문 검색                            | 본문 전체                        | 라벨만                           | 본문 전체 (OpenSearch)    |
| 강점      | 검색 언어(SPL), 보안(SIEM) 제품군 | 설정이 간단, syslog 중심             | 검색·분석, 생태계                | 저장 비용, Grafana 연동          | 입력 종류, 화면 중심 운영 |
| 수집      | Forwarder 등                      | syslog, `remote_syslog2`, 라이브러리 | Filebeat·Elastic Agent           | Alloy                            | Syslog·GELF·Beats 입력    |
| 비용 기준 | 수집량·작업량(견적)               | GB당 월 단가                         | 서버·인력                        | 서버·저장소·인력                 | 서버·인력                 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 비용 구조

| 제품       | 공개된 기준 (2026-11-23)                                                                                                                                        |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Splunk     | Enterprise는 수집량 또는 작업량 요금, Cloud Platform은 활동량·수집량·작업량 중 선택. 단가는 견적. Enterprise 60일 체험, 다운로드 페이지에 하루 500 MB 색인 표기 |
| Papertrail | GB당 월 $5부터. 전송량 = 메시지 길이 + 50바이트. 한도를 넘으면 멈추거나 30% 높은 단가로 계속                                                                    |
| 자체 운영  | 소프트웨어는 무료 판이 있고, 서버·디스크·백업·인력이 비용                                                                                                       |

계산 예(Papertrail): 하루 2 GB씩 30일이면 월 60 GB이고, GB당 $5 기준 월 $300부터입니다. 실제 요금제의 포함량과 검색 기간에 따라 달라집니다.

자체 운영의 디스크는 "하루 수집량 × 보존 일수 × 복제 수 × 색인 배율"로 어림합니다. 본문을 색인하는 Elastic·Graylog는 Loki보다 색인 배율이 큽니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고르는 기준

| 상황                                                  | 후보                             |
|-------------------------------------------------------|----------------------------------|
| 서버 몇 대, 운영 인력 없음, 최근 며칠 로그만 자주 봄  | Papertrail 같은 SaaS             |
| 보안 관제(SIEM)까지 한 제품으로, 예산 있음            | Splunk                           |
| 본문 검색·분석이 많고 직접 운영 가능                  | Elastic Stack                    |
| Grafana·Prometheus를 이미 쓰고 로그량이 많음          | Loki                             |
| syslog·네트워크 장비 로그가 많고 화면에서 규칙을 관리 | Graylog                          |
| 외부 반출 금지, 폐쇄망                                | 자체 운영 또는 Splunk Enterprise |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 옮길 때 확인할 것

| 항목      | 확인 내용                                                                     |
|-----------|-------------------------------------------------------------------------------|
| 수집 경로 | syslog·파일 수집기는 대상 주소만 바꾸면 되는지, 전용 에이전트를 바꿔야 하는지 |
| 로그 형식 | JSON 필드 이름이 새 도구의 규칙과 맞는지 (Elastic은 ECS 충돌 주의)            |
| 검색·알림 | 저장된 검색과 알림 조건을 새 검색 언어로 다시 작성                            |
| 과거 로그 | 보관 파일을 새 도구로 다시 넣을지, 옛 도구를 읽기 전용으로 둘지               |
| 보존 기간 | 법·내부 규정의 보존 기간을 새 도구 설정에 반영                                |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 확인 방법

| 순서 | 확인 내용   | 방법                                           | 기대 결과                   |
|------|-------------|------------------------------------------------|-----------------------------|
| 1    | 로그량      | 서버별 하루 로그 크기 측정 (`du`, 수집기 통계) | 하루 수집량 GB              |
| 2    | 비용 비교   | 2절 기준으로 같은 기간(예: 1년) 비용 계산      | 제품별 비용 표              |
| 3    | 검색 기간   | 자주 찾는 로그가 며칠 전 것인지 확인           | 핫 저장·보관 기간 결정      |
| 4    | 시범 수집   | 서버 한 대를 새 도구로 함께 보내 봄            | 같은 로그가 양쪽에서 검색됨 |
| 5    | 데이터 위치 | 저장 위치와 사내 정책 대조                     | 정책 위반 없음              |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Elastic Stack 로그 수집](./elastic_stack.md) · [Grafana Loki](./loki.md) · [Graylog](./graylog.md) — 자체 운영 도구
- [로그 수집 100 GB 규모](./log_aggregation_100gb.md) · [100 TB 규모](./log_aggregation_100tb.md) — 규모별 설계
- [모니터링 SaaS 비교](../monitoring/monitoring_saas_comparison.md) — Datadog과 자체 운영 비교

---

## 참고 자료

- Splunk: [Splunk Enterprise download](https://www.splunk.com/en_us/download/splunk-enterprise.html) · [Pricing](https://www.splunk.com/en_us/products/pricing.html) — 2026-11-23 확인 — ★★★☆☆
- Papertrail: [Plans](https://www.papertrail.com/plans/) · [Help](https://www.papertrail.com/help/) — 2026-11-23 확인 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
