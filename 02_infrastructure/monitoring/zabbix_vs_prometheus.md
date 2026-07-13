# Zabbix vs Prometheus

인프라 모니터링 도구인 Zabbix와 Prometheus의 아키텍처, 수집 방식, 확장성, 운영 복잡도를 비교합니다.

## 목차

| 섹션                                                                                                                          |
|-------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 데이터 수집](#3-데이터-수집)                                            |
| [4. 스토리지](#4-스토리지) / [5. 알림](#5-알림) / [6. 시각화](#6-시각화)                                                      |
| [7. 확장성](#7-확장성) / [8. 운영 복잡도](#8-운영-복잡도) / [9. 비교 요약](#9-비교-요약) / [10. 선택 가이드](#10-선택-가이드) |

## 1. 개요

| 항목        | Zabbix                   | Prometheus                      |
|-------------|--------------------------|---------------------------------|
| 유형        | 올인원 모니터링 플랫폼   | 메트릭 수집 + 알림 툴킷         |
| 라이선스    | GPLv2                    | Apache 2.0                      |
| 개발        | Zabbix SIA (라트비아)    | CNCF Graduated Project          |
| 초기 릴리즈 | 2001                     | 2012 (SoundCloud)               |
| 최신 버전   | 7.4 (LTS: 7.0)           | v3.13.0                         |
| 주 언어     | C, PHP, Go (Agent 2)     | Go                              |
| 데이터 모델 | 호스트 → 아이템 → 트리거 | 시계열 (metric + labels)        |
| 수집 방식   | Push (Agent → Server)    | Pull (Server → Target /metrics) |
| 쿼리 언어   | 없음 (GUI 기반 표현식)   | PromQL                          |

## 2. 아키텍처

### Zabbix

```
┌─────────────────────────────────────────────────────────┐
│                     Zabbix Server                       │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Poller  │  │ Trapper  │  │ Alerter  │  │ Escalator│  │
│  └─────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                      │                                  │
│                      v                                  │
│             ┌──────────────────┐                        │
│             │ PostgreSQL/MySQL │                        │
│             └──────────────────┘                        │
└─────────────────────────────────────────────────────────┘
       ^              ^               ^
       │              │               │
 Zabbix Agent   SNMP Device      IPMI/JMX
 (Push data)    (Poll/Trap)      (Poll)
```

- 단일 서버 구성 (Server + DB + Frontend)
- Proxy 추가로 원격 사이트 수집 가능
- DB 의존적 — 모든 설정/이력이 RDBMS에 저장

### Prometheus

```
┌───────────────────────────────────────────┐
│          Prometheus Server                │
│  ┌──────────┐  ┌──────────┐               │
│  │ Scraper  │  │  TSDB    │               │
│  └──────────┘  └──────────┘               │
│       │             │                     │
│       v             v                     │
│  ┌──────────┐  ┌──────────────┐           │
│  │ PromQL   │  │ AlertManager │           │
│  └──────────┘  └──────────────┘           │
└──────┬────────────────────────────────────┘
       │
       │  HTTP GET /metrics (Pull)
       v
  ┌───────────┐  ┌────────────┐  ┌─────────────┐
  │ Exporter  │  │ Exporter   │  │ Pushgateway │
  │(node_exp) │  │(mysqld_exp)│  │(batch jobs) │
  └───────────┘  └────────────┘  └─────────────┘
```

- 각 컴포넌트가 독립적 (Prometheus, AlertManager, Grafana 별도)
- 로컬 TSDB 사용 (외부 DB 불필요)
- Service Discovery로 동적 타겟 관리

## 3. 데이터 수집

| 항목              | Zabbix                      | Prometheus                        |
|-------------------|-----------------------------|-----------------------------------|
| 기본 방식         | Push (Agent → Server)       | Pull (Server → Target)            |
| 에이전트          | Zabbix Agent / Agent 2 (Go) | Exporter (node, mysqld, etc.)     |
| 에이전트리스      | SNMP, IPMI, SSH, HTTP Agent | Blackbox Exporter (probe)         |
| 서비스 디스커버리 | LLD (Low-Level Discovery)   | kubernetes_sd, consul_sd, file_sd |
| 수집 주기         | 최소 1초 (기본 60초)        | 최소 1초 (기본 15초)              |
| 커스텀 메트릭     | UserParameter, Trapper item | Custom Exporter, /metrics 노출    |
| 로그 수집         | ✅ (Log item, Logrt)        | ❌ (Loki 별도 사용)               |
| SNMP              | ✅ 내장 (SNMPv1/v2c/v3)     | ❌ (snmp_exporter 별도)           |
| Windows           | ✅ (Native Agent)           | 🟡 (windows_exporter 커뮤니티)    |

### Push vs Pull 차이

| 관점      | Push (Zabbix)                    | Pull (Prometheus)              |
|-----------|----------------------------------|--------------------------------|
| 방화벽    | Agent → Server (outbound만 필요) | Server → Target (inbound 필요) |
| NAT 환경  | ✅ 유리 (Agent가 나가면 됨)      | 🟡 불리 (Server가 접근해야 함) |
| 타겟 장애 | 데이터 도착 중단 = 장애 감지     | Scrape 실패 = up==0 (명시적)   |
| 동적 환경 | Auto-registration 필요           | Service Discovery 내장         |

## 4. 스토리지

| 항목           | Zabbix                         | Prometheus                                    |
|----------------|--------------------------------|-----------------------------------------------|
| 스토리지 유형  | RDBMS (PostgreSQL, MySQL)      | 로컬 TSDB (커스텀 엔진)                       |
| 장기 보존      | DB에 직접 저장 (파티셔닝 권장) | Remote Write (Thanos, Mimir, VictoriaMetrics) |
| 보존 기간 설정 | Housekeeping (일/주/월/연)     | `--storage.tsdb.retention.time`               |
| 압축           | DB 레벨                        | Gorilla 압축 (1.37 bytes/sample)              |
| HA             | DB Replication + Server HA     | Thanos/Cortex 사용                            |
| 백업           | pg_dump / mysqldump            | snapshot API / 디스크 복사                    |

## 5. 알림

| 항목          | Zabbix                             | Prometheus                         |
|---------------|------------------------------------|------------------------------------|
| 알림 엔진     | 내장 (Trigger + Action)            | AlertManager (별도 컴포넌트)       |
| 조건 정의     | Trigger expression (GUI)           | PromQL alert rules (YAML)          |
| 에스컬레이션  | ✅ 다단계 (시간별 담당자 변경)     | ❌ (외부 도구로 구현)              |
| 의존성 처리   | ✅ Trigger dependency              | ✅ inhibit_rules                   |
| 그룹핑        | ❌                                 | ✅ group_by (AlertManager)         |
| 알림 채널     | Email, Slack, Webhook, SMS, Script | Webhook 기반 (Slack, PagerDuty 등) |
| 유지보수 기간 | ✅ Maintenance period              | ✅ Silence (AlertManager)          |
| 자동 해제     | ✅ Recovery expression             | ✅ for 절 + resolve                |

## 6. 시각화

| 항목          | Zabbix                    | Prometheus                   |
|---------------|---------------------------|------------------------------|
| 내장 대시보드 | ✅ (Zabbix Frontend)      | ❌ (기본 Expression Browser) |
| 그래프        | 내장 (simple/stacked/pie) | Grafana 연동 필수            |
| 맵/토폴로지   | ✅ Network Map            | ❌                           |
| SLA 보고서    | ✅ 내장                   | ❌ (별도 구현)               |
| 커스터마이징  | 제한적 (위젯 기반)        | Grafana에서 자유도 높음      |

## 7. 확장성

| 항목          | Zabbix                        | Prometheus                       |
|---------------|-------------------------------|----------------------------------|
| 수직 확장     | DB 스펙 증설                  | 메모리/디스크 증설               |
| 수평 확장     | Zabbix Proxy (원격 사이트별)  | Federation, Thanos, Mimir        |
| 모니터링 대상 | 공식: 단일 서버 10만+ 메트릭  | 단일 인스턴스 수백만 시계열 가능 |
| 멀티 테넌시   | ❌ (User Group으로 접근 제어) | ✅ (Thanos/Mimir label 기반)     |
| K8s 네이티브  | 🟡 (Helm chart 있지만 비주류) | ✅ (kube-prometheus-stack 표준)  |

## 8. 운영 복잡도

| 항목           | Zabbix                          | Prometheus                       |
|----------------|---------------------------------|----------------------------------|
| 초기 설치      | Server + DB + Frontend (3 tier) | 바이너리 1개 (docker run 가능)   |
| 설정 방식      | GUI (Web UI)                    | YAML 파일 (IaC 친화)             |
| 설정 버전 관리 | DB Export/Import                | Git 관리 (prometheus.yml)        |
| 업그레이드     | DB 마이그레이션 필요            | 바이너리 교체                    |
| 에이전트 배포  | Agent 설치 + Server 등록        | Exporter 설치 (등록 불필요)      |
| 학습 곡선      | GUI 기반 — 초기 진입 쉬움       | PromQL + YAML — 학습 필요        |
| 장애 시 영향   | DB 장애 = 전체 중단             | TSDB 독립 — 부분 장애 가능       |
| 백업/복구      | DB 백업 (설정+이력 통합)        | 설정: Git, 데이터: Snapshot 분리 |

## 9. 비교 요약

| 관점                | Zabbix 우세               | Prometheus 우세                 |
|---------------------|---------------------------|---------------------------------|
| 올인원              | ✅ 단일 제품으로 완결     | ❌ 조합 필요 (Grafana, Loki 등) |
| SNMP/네트워크       | ✅ 내장 SNMP, 네트워크 맵 | ❌ 별도 exporter                |
| 에스컬레이션        | ✅ 다단계 알림            | ❌ 단순                         |
| GUI 운영            | ✅ 클릭으로 설정          | ❌ YAML 수동                    |
| 로그 모니터링       | ✅ 내장                   | ❌ Loki 별도                    |
| 클라우드/K8s        | ❌ 전통 인프라 중심       | ✅ CNCF 표준, Service Discovery |
| 동적 환경           | ❌ 정적 호스트 등록       | ✅ 자동 타겟 발견               |
| 고카디널리티        | ❌ 아이템 수 제한         | ✅ 레이블 기반 다차원 쿼리      |
| IaC/GitOps          | ❌ DB 의존 설정           | ✅ YAML Git 관리                |
| 커뮤니티/에코시스템 | 🟡 상용 지원 강점         | ✅ CNCF, Exporter 수백 개       |

## 10. 선택 가이드

### 용도별 권장

| 환경                           | 권장       | 이유                                       |
|--------------------------------|------------|--------------------------------------------|
| 전통 IDC (물리 서버, 네트워크) | Zabbix     | SNMP, IPMI, 네트워크 맵, 에스컬레이션      |
| Kubernetes / 컨테이너          | Prometheus | kube-prometheus-stack, Service Discovery   |
| 클라우드 네이티브 (AWS/GCP)    | Prometheus | 동적 타겟, IaC 친화, 관리형 서비스 연동    |
| 소규모팀 (5명 이하)            | Zabbix     | 올인원, GUI 운영, 학습 비용 낮음           |
| MSA / 다수 마이크로서비스      | Prometheus | 레이블 기반 고카디널리티 쿼리              |
| 혼합 환경 (IDC + K8s)          | 둘 다 운영 | Zabbix(인프라) + Prometheus(K8s) 역할 분리 |

### 팀 역량별

| 팀 특성                | 권장       | 이유                             |
|------------------------|------------|----------------------------------|
| GUI 선호, YAML 미숙    | Zabbix     | 웹 UI로 모든 설정 가능           |
| DevOps/SRE, IaC 숙련   | Prometheus | YAML + Git + Helm 자동화         |
| 네트워크 엔지니어 포함 | Zabbix     | SNMP 네이티브, 네트워크 토폴로지 |
| 개발자 중심 (SLI/SLO)  | Prometheus | PromQL로 정밀 SLI 정의           |

### 하이브리드 구성 예시

```
┌─────────────────────────────────────────────────────┐
│                   Grafana (Unified Dashboard)       │
│                                                     │
│  ┌─────────────────┐       ┌─────────────────────┐  │
│  │  Zabbix DB      │       │  Prometheus TSDB    │  │
│  │  (infra metrics)│       │  (K8s/app metrics)  │  │
│  └─────────────────┘       └─────────────────────┘  │
│           ^                         ^               │
│           │                         │               │
└───────────│─────────────────────────│───────────────┘
           │                         │
  Physical Servers            Kubernetes Pods
  Network Devices             Microservices
  SNMP/IPMI                   /metrics endpoint
```

## 참고 자료

- Zabbix Documentation: [zabbix.com/documentation](https://www.zabbix.com/documentation/current/) — ★★★☆☆
- Prometheus Documentation: [prometheus.io/docs](https://prometheus.io/docs/introduction/overview/) — ★★★☆☆
- CNCF Landscape: [landscape.cncf.io](https://landscape.cncf.io/) — ★★☆☆☆

---

**작성일**: 2026-07-03

**마지막 업데이트**: 2026-07-03

© 2026 siasia86. Licensed under CC BY 4.0.
