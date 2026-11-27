---
name: istio-official-notes
description: Istio 1.32.0 판, 지원 Kubernetes 판, 지원 기간 정책, sidecar·ambient 데이터 플레인 상태 정리.
tags:
  - istio
  - service-mesh
last_checked: 2026-11-27
sources:
  - https://github.com/istio/istio/releases
  - https://istio.io/latest/news/releases/1.32.x/announcing-1.32/
  - https://istio.io/latest/docs/releases/supported-releases/
  - https://istio.io/latest/docs/ambient/overview/
  - https://istio.io/latest/docs/overview/dataplane-modes/
---

# Istio 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- 최신 1.32.0(2026-11-09). 같은 시기 patch 1.31.4·1.30.8(2026-11-06).
- "Istio 1.32.0 is officially supported on Kubernetes versions 1.33 to 1.37."
- 지원 기간(요약 근거): N+2 minor 출시 뒤 6주까지. 1.32 예상 종료 2027-06(페이지 추정치).
- 라이선스 Apache 2.0(GitHub LICENSE).

## 2. 데이터 플레인

- dataplane-modes(요약 근거): ambient "As of Istio 1.22, it is production-ready for single cluster use cases.", 표에 ambient "Stable, only single-cluster", sidecar "Stable, including multi-cluster". ambient 여러 네트워크 다중 클러스터 1.29 Beta. ambient GA 판 표기는 찾지 못함.
- ambient overview(요약 근거): ztunnel은 L3·L4(mTLS, 인증, L4 권한, 지표)만, 워크로드 HTTP를 종료·해석하지 않음. waypoint는 namespace 단위 선택 배치, L7 기능 담당, "a deployment of the Envoy proxy".

## 3. 시험

- 클러스터 시험 미실행.
