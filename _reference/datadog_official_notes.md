---
name: datadog-official-notes
description: Datadog 공식 문서·요금 페이지 기반 사이트, 에이전트, 요금 구조, 보존 기간 정리.
tags:
  - datadog
  - monitoring
  - saas
  - observability
last_checked: 2026-11-23
sources:
  - https://docs.datadoghq.com/getting_started/site/
  - https://docs.datadoghq.com/agent/
  - https://docs.datadoghq.com/agent/docker/
  - https://docs.datadoghq.com/agent/configuration/agent-commands/
  - https://docs.datadoghq.com/data_security/data_retention_periods/
  - https://www.datadoghq.com/pricing/
  - https://github.com/DataDog/datadog-agent/releases
---

# Datadog 공식 문서 참조 노트

상용 SaaS라 계정 없이 확인할 수 있는 공식 문서·요금 페이지 범위만 기록합니다. 에이전트 실행과 데이터 전송은 시험하지 않았습니다.

## 1. 판과 확인 (2026-11-23)

| 항목            | 내용                                                                                                                                   | 근거                |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| 에이전트 판     | 7.85.5 (2026-11-19)                                                                                                                    | GitHub releases     |
| 메이저 판       | Agent 7이 최신 메이저                                                                                                                  | Agent 문서 Versions |
| 컨테이너 이미지 | `registry.datadoghq.com/agent:7` (Docker 문서 예), `gcr.io/datadoghq` 등 미러                                                          | Docker Agent 문서   |
| 설치 스크립트   | `https://install.datadoghq.com/scripts/install_script_agent7.sh` (HTTP 200, 스크립트 판 1.49.0), `DD_API_KEY`·`DD_SITE` 환경 변수 사용 | 직접 조회           |
| 설정 파일       | `/etc/datadog-agent/datadog.yaml`                                                                                                      | Ubuntu Agent 문서   |
| 상태 확인       | Linux `sudo datadog-agent status`, Docker `docker exec -it <이름> agent status`                                                        | Agent Commands      |

## 2. 사이트 (데이터 위치)

계정은 하나의 사이트에 만들어지고, 에이전트의 `DD_SITE`는 그 사이트 값과 같아야 합니다.

| 사이트  | 접속 주소                   | `DD_SITE` 값        | 위치      |
|---------|-----------------------------|---------------------|-----------|
| US1     | `https://app.datadoghq.com` | `datadoghq.com`     | 미국      |
| US3     | `https://us3.datadoghq.com` | `us3.datadoghq.com` | 미국      |
| US5     | `https://us5.datadoghq.com` | `us5.datadoghq.com` | 미국      |
| EU1     | `https://app.datadoghq.eu`  | `datadoghq.eu`      | 독일      |
| AP1     | `https://ap1.datadoghq.com` | `ap1.datadoghq.com` | 일본      |
| AP2     | `https://ap2.datadoghq.com` | `ap2.datadoghq.com` | 호주      |
| UK1     | `https://uk1.datadoghq.com` | `uk1.datadoghq.com` | 영국      |
| US1-FED | `https://app.ddog-gov.com`  | `ddog-gov.com`      | 미국 정부 |
| US2-FED | `https://us2.ddog-gov.com`  | `us2.ddog-gov.com`  | 미국 정부 |

## 3. 요금 구조 (Infrastructure Monitoring, 2026-11-23 요금 페이지)

| 등급       | 연간 계약 기준 월 단가 | 주문형(on-demand) | 포함 항목 (요금 페이지 표)                        |
|------------|------------------------|-------------------|---------------------------------------------------|
| Basic      | 영업 문의              | -                 | 핵심 시스템 지표, 기본 대시보드                   |
| Pro        | 호스트당 $15부터       | $18               | 컨테이너 호스트당 5개, 사용자 지표 호스트당 100개 |
| Enterprise | 호스트당 $23부터       | $27               | 컨테이너 10개, 사용자 지표 200개, ML 기반 알림    |

- 세 등급 모두 전체 해상도 지표 보존은 15개월입니다.
- 로그는 별도 과금입니다. 수집(Ingest)은 GB당 $0.10부터, 색인·보존 기간은 요금제에 따라 정해집니다.
- APM, 사용자 지표 초과분, 로그 색인 등은 따로 과금되므로 실제 비용은 사용량으로 계산합니다. 요금은 바뀔 수 있어 결정 전에 다시 확인합니다.

## 4. 보존 기간 (Data Retention Periods 문서)

| 데이터         | 기본 보존                    |
|----------------|------------------------------|
| 지표 태그와 값 | 15개월                       |
| 로그           | 고객 요금제에 따라 정해짐    |
| APM 색인 span  | 요금제에 따라 15일 또는 30일 |
| Audit Trail    | 켰을 때 90일, 껐을 때 7일    |

## 5. 확인하지 못한 것

- 에이전트 설치·전송 실제 동작 (계정과 API 키가 필요해 미실행)
- Basic 등급 단가 (요금 페이지가 영업 문의로 표시)
- 지원 OS 전체 목록 (supported platforms 문서 조회 실패)
