---
name: envoy-official-notes
description: Envoy v1.40.2 판과 지원 정책, v1.40.0 호환되지 않는 변경, 상태 검사 no_traffic_interval 기본값, 컨테이너 시험 결과 정리.
tags:
  - envoy
  - proxy
  - service-mesh
last_checked: 2026-11-27
sources:
  - https://github.com/envoyproxy/envoy/releases
  - https://github.com/envoyproxy/envoy/blob/main/RELEASES.md
  - https://www.envoyproxy.io/docs/envoy/latest/version_history/v1.40/v1.40.0
  - https://github.com/envoyproxy/envoy/blob/v1.40.2/api/envoy/config/core/v3/health_check.proto
---

# Envoy 공식 자료 참조 노트

## 1. 판과 지원 (2026-11-27 확인)

- 최신 v1.40.2(2026-10-27). 같은 날 전후 v1.39.6, v1.38.9, v1.37.11. v1.40.0 첫 출시 2026-10-13.
- RELEASES.md: 메이저는 분기마다, 안정 판 수정은 최근 12개월 안에 나온 판 대상. 표에 v1.40.0 지원 종료 2027-10-13, v1.41.0 예정 2027-01-19.

## 2. v1.40.0 변경 (버전 기록 앞부분 원문 기준, 뒷부분 미확인)

- 호환되지 않는 변경: Bazel `WORKSPACE` → bzlmod, wasm·engine 빌드 플래그 교체, mcp_router가 `authorization` 헤더를 기본으로 넘기지 않음, AWS-LC 제거, 로컬 처리율 제한 shadow 모드 우회 수정("Requests that were previously allowed by this bypass may now be rate limited."), on-demand VHDS 스트림 재생성 안 함, Rust dynamic module SDK 시그니처 변경, Clang 22.
- 작은 동작 변경: QUIC/HTTP/3 alpha → stable, 외부 요청의 `x-envoy-upstream-stream-duration-ms` 제거, RBAC 경로 매개변수 수정(CVE-2026-73553), 기본 ECDH 곡선에 `X25519MLKEM768`, Redis RESP 파싱 엄격화.

## 3. 설정 원본

- `health_check.proto`: "The default value for "no traffic interval" is 60 seconds." `no_traffic_healthy_interval`은 트래픽 없는 cluster에서 healthy 호스트에 쓰는 간격.

## 4. 컨테이너 시험 (2026-11-27, envoyproxy/envoy:v1.40.2, traefik/whoami 4개)

- `--mode validate`: 정상은 `configuration '/etc/envoy/envoy.yaml' OK`, 잘못된 포트 값은 `Unable to parse JSON as proto (INVALID_ARGUMENT: ...`.
- `/server_info` 판 `b2d89e0.../1.40.2/Clean/RELEASE/Boring...`. 컨테이너 PID 1 사용자 `envoy`.
- `/api` ROUND_ROBIN 6회 3:3, `weighted_clusters` 80:20은 200회 중 154:46.
- 능동 상태 검사(interval 2s): `no_traffic_interval` 미지정 시 30초 동안 attempt 2, 멈춘 백엔드도 healthy. 2s 지정 시 5초 안에 `/failed_active_hc/active_hc_timeout`, 30초 뒤 attempt 28·failure 10, membership_healthy 1, 요청 6회 모두 200.
- local_ratelimit 60초에 20개: 25회 중 200 20회, 429 5회. 버킷이 listener 전체에 걸려 다른 경로 요청도 막힘.
- `/config_dump` 타입: Bootstrap, Clusters, Listeners, Routes, ScopedRoutes, Secrets.
- 미실행: TLS, xDS, HTTP/3, 외부 인증·처리율 제한.
