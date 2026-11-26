---
name: jaeger-official-notes
description: Jaeger v2 판·마지막 v1 판, v1 HTTP 경로 제거(v2.21.0), Badger 저장소 설정과 컨테이너 시험 결과 정리.
tags:
  - jaeger
  - tracing
  - opentelemetry
last_checked: 2026-11-26
sources:
  - https://github.com/jaegertracing/jaeger/releases
  - https://github.com/jaegertracing/jaeger/blob/main/CHANGELOG.md
  - https://github.com/jaegertracing/jaeger/tree/main/cmd/jaeger
  - https://www.jaegertracing.io/docs/latest/getting-started/
---

# Jaeger 공식 자료 참조 노트

## 1. 판 (2026-11-26 확인)

- 최신 v2.23.0(GitHub 릴리스 2026-11-05, CHANGELOG 표기 2026-11-04). 이전 v2.22.0(10-06), v2.21.0(09-14), v2.20.0(07-20).
- 마지막 v1: v1.76.0(2025-12-03). 그 뒤 v1 릴리스 없음.
- v2.23.0은 내부적으로 Collector v0.163.0 기반(시작 로그 `service@v0.163.0`).
- v2.23.0 breaking: ClickHouse feature gate 제거, 스키마 생성 때 table engine 명시 필요, auth extension 참조 해석 변경, gemini sidecar 제거.
- v2.23.0 기능: v3 API로 저장소 검색 기능 제공, SQL 형태 조회 표면, MCP 관련 기능.

## 2. API

- v2.21.0 CHANGELOG: "remove v1 http endpoints the ui no longer calls". v2.23.0: "move the last v1 trace callers to the v3 api".
- v2.23.0 시험: `/api/v3/services`·`/api/v3/operations?service=`·`/api/v3/traces/<id>` 200, `/api/traces/<id>` 200, `/api/services`·`/api/traces?service=` 404.

## 3. 설정

- 저장소 `cmd/jaeger/`에 예시: `config.yaml`, `config-badger.yaml`, `config-elasticsearch*.yaml`, `config-opensearch*.yaml`, `config-cassandra.yaml`, `config-clickhouse.yaml`, `config-kafka-*.yaml`, `config-query.yaml`, `config-tail-sampling-*.yaml` 등.
- 구조: `jaeger_storage`(backends), `jaeger_query`(storage.traces), `jaeger_storage_exporter`(trace_storage) extension·exporter와 `otlp` receiver.
- Badger 예시: `directories.keys/values`, `ephemeral: false`, `ttl.spans`.

## 4. 컨테이너 시험 (2026-11-26)

- 이미지 사용자 `10001:10001`, 크기 180MB.
- 인수 없이 실행: 메모리 저장소로 기동.
- Badger + 이름 있는 볼륨(소유자 10001): 트레이스 저장 뒤 재시작해도 조회 200.
- 볼륨 소유자 root: `Error Creating Dir: "/badger/keys" err: mkdir /badger/keys: permission denied`, 종료 코드 1.
- 미실행: Elasticsearch·OpenSearch·Cassandra·ClickHouse, Kafka, TTL 경과 뒤 삭제, 웹 화면.
