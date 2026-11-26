# 모니터링 SaaS 비교 (Datadog·New Relic·Dynatrace와 자체 운영)
<!-- reference: _reference/datadog_official_notes.md, _reference/prometheus_official_notes.md, _reference/zabbix_official_notes.md -->
<!-- reference: _reference/new_relic_official_notes.md, _reference/dynatrace_official_notes.md, _reference/opentelemetry_official_notes.md -->

호스트·컨테이너 모니터링을 상용 SaaS(Datadog·New Relic·Dynatrace)에 맡길지, Prometheus·Grafana나 Zabbix로 직접 운영할지 고르는 기준을 정리한 문서입니다. 상용 서비스는 계정·비용 없이 확인할 수 있는 공식 문서·요금 페이지 범위만 다룹니다. 자체 운영 도구의 설치와 검증은 각 문서에 있습니다.

- 기준: 2026-11-23 Datadog 공식 문서·요금 페이지, 2026-11-26 New Relic·Dynatrace 공식 문서·요금 페이지, Prometheus 3.16.0, Zabbix 8.0 LTS
- 예제 시험: 상용 3종은 미실행(계정과 키가 필요). 4·5절 명령과 주소는 공식 문서와 대조했습니다. 5절의 Collector 설정 형식은 [OpenTelemetry](./opentelemetry.md)에서 자체 Jaeger로 보내 확인한 것과 같습니다. 요금은 바뀔 수 있으므로 결정 전에 공식 요금 페이지를 다시 확인합니다

## 목차

| 섹션                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|
| [1. 한눈에 비교](#1-한눈에-비교) / [2. 비용 구조](#2-비용-구조) / [3. 고르는 기준](#3-고르는-기준)                          |
| [4. Datadog 에이전트 연결](#4-datadog-에이전트-연결) / [5. OpenTelemetry로 SaaS에 보내기](#5-opentelemetry로-saas에-보내기) |
| [6. 확인 방법](#6-확인-방법) / [함께 보기](#함께-보기)                                                                      |

---

## 1. 한눈에 비교

| 항목        | Datadog (SaaS)                           | New Relic (SaaS)                         | Dynatrace (SaaS·Managed)                      | Prometheus + Grafana (자체 운영)             | Zabbix (자체 운영)            |
|-------------|------------------------------------------|------------------------------------------|-----------------------------------------------|----------------------------------------------|-------------------------------|
| 운영 주체   | Datadog (서버·저장소·업그레이드)         | New Relic                                | Dynatrace (Managed는 자체 설치)               | 직접                                         | 직접                          |
| 수집        | Datadog Agent가 SaaS로 전송 (push)       | Infrastructure agent, APM 에이전트, OTLP | OneAgent(자동 계측), ActiveGate, OTLP         | 서버가 대상 `/metrics`를 가져감 (pull)       | 에이전트 passive·active, SNMP |
| 과금 단위   | 호스트·사용량                            | 사용자 + 데이터 GB                       | 호스트 메모리·시간, 데이터 GiB (소비형 약정)  | 없음 (서버·인력)                             | 없음 (서버·인력)              |
| 지표 보존   | 15개월 (전 등급)                         | 기본 8일 이상, Data Plus 최대 90일 추가  | 지표 15개월 포함, 트레이스 10일 포함          | 설정한 기간, 디스크만큼                      | Housekeeping 설정 기간        |
| 로그·APM    | 같은 화면에서 제공 (별도 과금)           | 같은 화면, 데이터량에 포함               | 같은 화면, 항목별 단가                        | Loki·Tempo 등 별도 구성                      | 로그 항목 일부, APM 없음      |
| OTLP 수신   | 이번 확인 범위 밖                        | gRPC·HTTP                                | HTTP만 (gRPC 미지원)                          | 이번 확인 범위 밖 (트레이스는 Jaeger로 확인) | 이번 확인 범위 밖             |
| 데이터 위치 | 계약한 사이트(미국·EU·일본·호주·영국 등) | US, EU, JP                               | 계약한 환경 (Managed는 자체)                  | 직접 정함                                    | 직접 정함                     |
| 외부 연결   | 에이전트에서 SaaS로 나가는 HTTPS 필요    | 나가는 HTTPS 필요                        | 나가는 HTTPS 필요 (ActiveGate로 모을 수 있음) | 없어도 운영 가능                             | 없어도 운영 가능              |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 비용 구조

Datadog Infrastructure Monitoring은 호스트 단위 월 구독입니다(2026-11-23 요금 페이지).

| 등급       | 연간 계약 기준 | 주문형 | 포함 (호스트당)                           |
|------------|----------------|--------|-------------------------------------------|
| Basic      | 영업 문의      | -      | 핵심 시스템 지표                          |
| Pro        | $15부터        | $18    | 컨테이너 5개, 사용자 지표 100개           |
| Enterprise | $23부터        | $27    | 컨테이너 10개, 사용자 지표 200개, ML 알림 |

계산 예(호스트 50대, Pro, 연간 계약): 50 × $15 = 월 $750부터입니다. 여기에 로그 수집(GB당 $0.10부터)과 색인, APM, 포함량을 넘는 사용자 지표·컨테이너가 더해집니다.

자체 운영은 다음을 비용에 넣어 비교합니다.

| 항목        | 내용                                             |
|-------------|--------------------------------------------------|
| 서버        | 수집 서버, 저장소, 이중화·백업 공간              |
| 인력        | 설치, 업그레이드, 저장소 증설, 장애 대응         |
| 감시의 감시 | 모니터링 서버 자체가 멈췄을 때 알려 줄 별도 경로 |
| 학습        | PromQL·템플릿·대시보드 작성                      |

New Relic(2026-11-26 요금 페이지)은 사용자와 데이터량으로 과금합니다.

| 항목                 | Standard                           | Pro                                 |
|----------------------|------------------------------------|-------------------------------------|
| Full platform 사용자 | 첫 사용자 $10, 추가 $99 (최대 5명) | $349 (연간 약정), $418.80 (월 종량) |
| Core 사용자          | $49                                | $49                                 |
| Basic 사용자         | 무료·무제한                        | 무료·무제한                         |
| 데이터               | 월 100GB 무료, 초과 GB당 $0.40     | 같음 (Data Plus는 $0.60)            |

Dynatrace(2026-11-26 단가표)는 연간 약정 안에서 쓴 만큼 차감하는 소비형입니다.

| 항목                      | 단가                    | 월 환산(요금 페이지) |
|---------------------------|-------------------------|----------------------|
| Full-Stack Monitoring     | 메모리 GiB-시간당 $0.01 | 8GiB 호스트 $58      |
| Infrastructure Monitoring | 호스트-시간당 $0.04     | 호스트 $29           |
| Log 수집·처리             | GiB당 $0.20             | -                    |
| Traces 수집               | GiB당 $0.20             | 10일 보존 포함       |

계산 예(호스트 50대, 각 16GiB):

| 도구      | 계산                                                                               | 월 비용 (시작 가격)  |
|-----------|------------------------------------------------------------------------------------|----------------------|
| Datadog   | Pro 연간 50 × $15                                                                  | $750 + 로그·APM      |
| Dynatrace | Full-Stack 16GiB × $0.01 × 730시간 × 50 = 약 $5,840, Infrastructure만이면 50 × $29 | $1,450~$5,840 + 로그 |
| New Relic | 호스트 수와 무관. Pro 사용자 3명 $1,047 + 데이터 500GB 중 400GB × $0.40            | 약 $1,207            |

- 과금 기준이 달라 같은 조건으로 바로 비교되지 않습니다. 호스트가 많고 보는 사람이 적으면 New Relic 방식이, 사용자가 많고 호스트가 적으면 호스트 단위 방식이 유리한 경향입니다.
- 각 도구의 포함량·할인·약정 조건으로 실제 금액은 달라집니다. 견적은 영업 문의로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고르는 기준

| 상황                                                      | 후보                                 |
|-----------------------------------------------------------|--------------------------------------|
| 운영 인력이 적고 지표·로그·APM을 한 화면에서 바로 써야 함 | Datadog 같은 SaaS                    |
| 호스트는 많고 화면을 보는 사람은 적음                     | New Relic (사용자·데이터량 과금)     |
| 코드 수정 없이 자동 계측, 온프레미스 설치판도 필요        | Dynatrace (OneAgent, Managed)        |
| 호스트 수가 많아 호스트 단위 구독이 부담됨                | Prometheus + Grafana                 |
| 쿠버네티스·컨테이너 중심, 설정을 Git으로 관리             | Prometheus + Grafana                 |
| SNMP 장비가 많고 웹 화면으로 운영                         | Zabbix                               |
| 외부 연결이 막힌 망, 데이터 반출 금지                     | 자체 운영 (Prometheus 또는 Zabbix)   |
| 우선 SaaS로 시작하고 나중에 옮길 수도 있음                | OpenTelemetry 등 중립 수집 방식 검토 |

다른 SaaS(Grafana Cloud 등)도 같은 표로 비교합니다. 확인할 항목은 과금 단위(호스트·데이터량·사용자), 보존 기간, 데이터 위치, 에이전트 방식입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Datadog 에이전트 연결

계정을 만든 뒤 Organization Settings에서 API 키를 발급하고, 계정 사이트에 맞는 `DD_SITE` 값을 씁니다(US1은 `datadoghq.com`, EU1은 `datadoghq.eu`, AP1은 `ap1.datadoghq.com`).

```bash
# Linux 호스트 (공식 설치 스크립트, 실행 전에 내용을 확인)
curl -fsSL -o install_script_agent7.sh https://install.datadoghq.com/scripts/install_script_agent7.sh
less install_script_agent7.sh
sudo DD_API_KEY="<API_KEY>" DD_SITE="datadoghq.com" bash install_script_agent7.sh
```

```bash
# Docker 호스트 (공식 Docker Agent 문서 예)
docker run -d --cgroupns host --pid host --name dd-agent \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /proc/:/host/proc/:ro \
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
  -e DD_SITE="datadoghq.com" \
  -e DD_API_KEY="<API_KEY>" \
  registry.datadoghq.com/agent:7
```

- API 키는 셸 이력·저장소에 남기지 않고, 비밀값 관리 도구나 권한을 좁힌 환경 파일로 넘깁니다.
- 설정 파일은 `/etc/datadog-agent/datadog.yaml`입니다.
- 에이전트는 사이트로 나가는 HTTPS(443)가 필요합니다. 프록시를 거치면 `datadog.yaml`의 proxy 설정을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. OpenTelemetry로 SaaS에 보내기

앱을 OpenTelemetry SDK로 계측하고 Collector에서 보낼 곳만 바꾸면, SaaS를 옮겨도 앱을 다시 계측하지 않습니다. Collector 기본 구성은 [OpenTelemetry](./opentelemetry.md) 3절을 봅니다.

| SaaS      | OTLP 주소 (예)                                          | 프로토콜        | 인증 헤더                             |
|-----------|---------------------------------------------------------|-----------------|---------------------------------------|
| New Relic | `https://otlp.nr-data.net` (EU `otlp.eu01.nr-data.net`) | gRPC·HTTP       | `api-key: <라이선스 키>`              |
| Dynatrace | `https://<환경 ID>.live.dynatrace.com/api/v2/otlp`      | HTTP/protobuf만 | `Authorization: Bearer <플랫폼 토큰>` |

```yaml
# Collector exporter 예 (키는 환경 변수에서 읽음)
exporters:
  otlp_http/newrelic:
    endpoint: https://otlp.nr-data.net
    headers:
      api-key: ${env:NEW_RELIC_LICENSE_KEY}
  otlp_http/dynatrace:
    endpoint: https://${env:DT_ENV_ID}.live.dynatrace.com/api/v2/otlp
    headers:
      Authorization: "Bearer ${env:DT_PLATFORM_TOKEN}"
```

- Dynatrace 토큰에는 `openpipeline:traces:ingest`(지표·로그도 보내면 `metrics`·`logs`) 권한이 필요합니다. 브라우저 주소의 환경 ID에 붙은 `.apps`는 빼고 씁니다.
- New Relic은 속성 값 4,095자, 요청 1MB 같은 제한이 있어 넘는 값은 잘립니다.
- 위 exporter는 계정이 없어 실제로 보내 보지 않았습니다. `validate`로 설정 문법만 확인했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 확인 방법

| 순서 | 확인 내용     | 방법                                                                              | 기대 결과                                |
|------|---------------|-----------------------------------------------------------------------------------|------------------------------------------|
| 1    | 비용 추정     | 호스트 수 × 등급 단가 + 로그·APM 예상량 (2절)                                     | 자체 운영 비용과 같은 기간으로 비교한 표 |
| 2    | 데이터 위치   | 계약할 사이트와 사내 데이터 정책 대조                                             | 정책 위반 없음                           |
| 3    | 에이전트 상태 | Linux `sudo datadog-agent status`, Docker `docker exec -it dd-agent agent status` | API 키 검증 성공, 수집 항목 오류 없음    |
| 4    | 수신 확인     | Datadog 화면 Infrastructure 목록                                                  | 호스트가 보이고 지표가 들어옴            |
| 5    | 이전 가능성   | 대시보드·알림을 코드로 내보낼 수 있는지 확인                                      | 옮길 때 다시 만들 범위를 파악            |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Prometheus + Grafana](./prometheus_grafana.md) · [Prometheus 설치](./prometheus_grafana_install.md) — 자체 운영 지표 수집
- [Zabbix](./zabbix.md) · [Zabbix vs Prometheus](./zabbix_vs_prometheus.md) — 에이전트·SNMP 중심 자체 운영
- [OpenTelemetry](./opentelemetry.md) · [Jaeger](./jaeger.md) — 업체 중립 계측과 자체 트레이스 저장
- [CloudWatch Agent·알람](../cloud_aws/cloudwatch_agent_alarms.md) — AWS 관리형 모니터링

---

## 참고 자료

- Datadog Docs: [Getting Started with Datadog Sites](https://docs.datadoghq.com/getting_started/site/) — ★★★☆☆
- Datadog Docs: [Docker Agent](https://docs.datadoghq.com/agent/docker/) · [Agent Commands](https://docs.datadoghq.com/agent/configuration/agent-commands/) — ★★★☆☆
- Datadog Docs: [Data Retention Periods](https://docs.datadoghq.com/data_security/data_retention_periods/) — ★★★☆☆
- Datadog: [Pricing](https://www.datadoghq.com/pricing/) — 2026-11-23 확인 — ★★★☆☆
- New Relic: [Pricing](https://newrelic.com/pricing) · [OTLP endpoint](https://docs.newrelic.com/docs/opentelemetry/best-practices/opentelemetry-otlp/) — 2026-11-26 확인 — ★★★☆☆
- Dynatrace: [Rate card](https://www.dynatrace.com/pricing/rate-card/) · [OTLP API endpoints](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api) — 2026-11-26 확인 — ★★★☆☆

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

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.
