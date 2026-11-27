---
name: consul-official-notes
description: Consul v2.1.0 판, BSL 1.1 라이선스(1.17.0 이후), Envoy 기반 서비스 메시, v2.0.0 변경 정리.
tags:
  - consul
  - service-mesh
last_checked: 2026-11-27
sources:
  - https://github.com/hashicorp/consul/releases
  - https://github.com/hashicorp/consul/blob/main/LICENSE
  - https://github.com/hashicorp/consul/releases/tag/v2.0.0
  - https://developer.hashicorp.com/consul/docs/connect
---

# Consul 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- 최신 v2.1.0(2026-10-22), 이전 v2.0.4(09-10), v2.0.3(08-07). v2.0.0 CHANGELOG 표기 2026-05-22(GitHub 릴리스 05-24).

## 2. 라이선스

- Business Source License 1.1, "Licensed Work: Consul Version 1.17.0 or later.", Licensor IBM Corp., Change Date 출시 4년 뒤, Change License MPL 2.0. 운영 사용은 허용, Consul을 경쟁 유료·호스팅 제품으로 제3자에게 제공하는 것은 제한. 1.17.0 이전 판 라이선스는 확인하지 않음.

## 3. 서비스 메시

- "you can use Consul to deploy Envoy sidecar proxies to control traffic between each service and the rest of the network." "Consul includes built-in support for Envoy proxies".
- Consul dataplane 설명은 읽은 쪽에서 찾지 못함.

## 4. v2.0.0 변경 (메시 관련)

- "connect: Upgrade envoy version to 1.37.2 and newer versions."
- HTTP 서버 `read_timeout`·`write_timeout` 기본 15분(이전 30초).
- api-gateway·terminating-gateway 경로 정규화(CVE-2024-10005, L7 intention RBAC 우회 방지).
- terminating gateway 상류 TLS를 SDS로.
- 수동 상태 검사 필드(Consecutive5xx 등) 추가.
- 다중 포트 서비스, 전역 처리율 제한은 Enterprise 전용.
- v2.1 릴리스 노트는 확인하지 않음.

## 5. 시험

- 미실행.
