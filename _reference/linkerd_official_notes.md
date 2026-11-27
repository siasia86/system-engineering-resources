---
name: linkerd-official-notes
description: Linkerd edge 판과 안정 판 배포 정책(2024-02 이후 벤더 배포), Rust 프록시, Buoyant Enterprise 무료 조건 정리.
tags:
  - linkerd
  - service-mesh
last_checked: 2026-11-27
sources:
  - https://github.com/linkerd/linkerd2/releases
  - https://linkerd.io/releases/
  - https://linkerd.io/2-edge/overview/
  - https://buoyant.io/pricing
---

# Linkerd 공식 자료 참조 노트

## 1. 판과 배포 (2026-11-27 확인)

- GitHub 최신 edge-26.11.2(2026-11-13), 이전 edge-26.11.1(11-02).
- "As of February 2024, the Linkerd open source project itself no longer provides stable release artifacts." "Instead, the vendor community around Linkerd is responsible for creating stable release artifacts."
- edge: "published on a weekly or near-weekly basis as part of the open source project."
- Linkerd 2.20 발표 2026-06-23, 배포판 예 Buoyant Enterprise for Linkerd 2.20.

## 2. 구조와 라이선스

- "micro-proxies are written in Rust and specialized for Linkerd."(linkerd2-proxy, Envoy 아님).
- "Linkerd is fully open source, licensed under Apache v2." CNCF 졸업.

## 3. Buoyant Enterprise for Linkerd

- "Companies with fewer than 50 employees can also run BEL for production use, at any scale." "always free to try". Premium·Strategic 가격 비공개.

## 4. 시험

- 클러스터 시험 미실행. 지원 Kubernetes 판은 확인하지 않음.
