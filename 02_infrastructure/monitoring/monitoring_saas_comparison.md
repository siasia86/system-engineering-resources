# 모니터링 SaaS 비교 (Datadog과 자체 운영)
<!-- reference: _reference/datadog_official_notes.md, _reference/prometheus_official_notes.md, _reference/zabbix_official_notes.md -->

호스트·컨테이너 모니터링을 상용 SaaS(Datadog)에 맡길지, Prometheus·Grafana나 Zabbix로 직접 운영할지 고르는 기준을 정리한 문서입니다. 상용 서비스는 계정·비용 없이 확인할 수 있는 공식 문서·요금 페이지 범위만 다룹니다. 자체 운영 도구의 설치와 검증은 각 문서에 있습니다.

- 기준: 2026-11-23 Datadog 공식 문서·요금 페이지, Prometheus 3.16.0, Zabbix 8.0 LTS
- 예제 시험: Datadog은 미실행(계정과 API 키가 필요). 4절 명령은 공식 Agent 문서와 대조했습니다. 요금은 바뀔 수 있으므로 결정 전에 공식 요금 페이지를 다시 확인합니다

## 목차

| 섹션                                                                                                          |
|---------------------------------------------------------------------------------------------------------------|
| [1. 한눈에 비교](#1-한눈에-비교) / [2. 비용 구조](#2-비용-구조) / [3. 고르는 기준](#3-고르는-기준)            |
| [4. Datadog 에이전트 연결](#4-datadog-에이전트-연결) / [5. 확인 방법](#5-확인-방법) / [함께 보기](#함께-보기) |

---

## 1. 한눈에 비교

| 항목        | Datadog (SaaS)                           | Prometheus + Grafana (자체 운영)       | Zabbix (자체 운영)              |
|-------------|------------------------------------------|----------------------------------------|---------------------------------|
| 운영 주체   | Datadog (서버·저장소·업그레이드)         | 직접                                   | 직접                            |
| 수집        | Datadog Agent가 SaaS로 전송 (push)       | 서버가 대상 `/metrics`를 가져감 (pull) | 에이전트 passive·active, SNMP   |
| 지표 보존   | 15개월 (전 등급)                         | 설정한 기간, 디스크만큼                | Housekeeping 설정 기간          |
| 로그·APM    | 같은 화면에서 제공 (별도 과금)           | Loki·Tempo 등 별도 구성                | 로그 항목 일부, APM 없음        |
| 비용        | 호스트·사용량 단위 구독                  | 소프트웨어 무료, 서버·인력 비용        | 소프트웨어 무료, 서버·인력 비용 |
| 데이터 위치 | 계약한 사이트(미국·EU·일본·호주·영국 등) | 직접 정함                              | 직접 정함                       |
| 외부 연결   | 에이전트에서 SaaS로 나가는 HTTPS 필요    | 없어도 운영 가능                       | 없어도 운영 가능                |

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

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고르는 기준

| 상황                                                      | 후보                                 |
|-----------------------------------------------------------|--------------------------------------|
| 운영 인력이 적고 지표·로그·APM을 한 화면에서 바로 써야 함 | Datadog 같은 SaaS                    |
| 호스트 수가 많아 호스트 단위 구독이 부담됨                | Prometheus + Grafana                 |
| 쿠버네티스·컨테이너 중심, 설정을 Git으로 관리             | Prometheus + Grafana                 |
| SNMP 장비가 많고 웹 화면으로 운영                         | Zabbix                               |
| 외부 연결이 막힌 망, 데이터 반출 금지                     | 자체 운영 (Prometheus 또는 Zabbix)   |
| 우선 SaaS로 시작하고 나중에 옮길 수도 있음                | OpenTelemetry 등 중립 수집 방식 검토 |

다른 SaaS(Grafana Cloud, New Relic 등)도 같은 표로 비교합니다. 확인할 항목은 과금 단위(호스트·데이터량·사용자), 보존 기간, 데이터 위치, 에이전트 방식입니다.

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

## 5. 확인 방법

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
- [CloudWatch Agent·알람](../cloud_aws/cloudwatch_agent_alarms.md) — AWS 관리형 모니터링

---

## 참고 자료

- Datadog Docs: [Getting Started with Datadog Sites](https://docs.datadoghq.com/getting_started/site/) — ★★★☆☆
- Datadog Docs: [Docker Agent](https://docs.datadoghq.com/agent/docker/) · [Agent Commands](https://docs.datadoghq.com/agent/configuration/agent-commands/) — ★★★☆☆
- Datadog Docs: [Data Retention Periods](https://docs.datadoghq.com/data_security/data_retention_periods/) — ★★★☆☆
- Datadog: [Pricing](https://www.datadoghq.com/pricing/) — 2026-11-23 확인 — ★★★☆☆

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
