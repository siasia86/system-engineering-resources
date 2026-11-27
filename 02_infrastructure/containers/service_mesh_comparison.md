# 서비스 메시 비교 (Istio · Linkerd · Consul)
<!-- reference: _reference/istio_official_notes.md, _reference/linkerd_official_notes.md, _reference/consul_official_notes.md -->

Kubernetes 안의 서비스 사이 통신에 mTLS 암호화, 재시도·타임아웃, 트래픽 분할, 관측(지표·트레이스)을 앱 코드 수정 없이 더하는 서비스 메시 세 가지를 비교합니다. 데이터 플레인(실제 트래픽을 처리하는 프록시) 구조, 배포·라이선스 조건, 판 지원을 정리했습니다. 도구를 고를 때 보는 문서이며 설치 가이드가 아닙니다.

- 기준 판: Istio 1.32.0 (2026-11-09), Linkerd edge-26.11.2 (2026-11-13, 안정 판은 벤더 배포), Consul v2.1.0 (2026-10-22) (2026-11-27 확인)
- 예제 시험: 클러스터 시험은 하지 않음. 각 프로젝트의 공식 문서·라이선스·릴리스 노트와 대조. 데이터 플레인 프록시인 Envoy의 단독 동작은 [Envoy](../web_server/envoy.md) 문서에서 컨테이너로 시험

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 한눈에 비교](#2-한눈에-비교) / [3. 데이터 플레인 구조](#3-데이터-플레인-구조)           |
| [4. 배포와 라이선스](#4-배포와-라이선스) / [5. 고르는 기준](#5-고르는-기준) / [6. 도입 전 확인](#6-도입-전-확인) |
| [함께 보기](#함께-보기)                                                                                          |

---

## 1. 개요

```text
without mesh:  [app A] --------- plain HTTP ---------> [app B]

with mesh:     [app A]-[proxy] ====== mTLS ======> [proxy]-[app B]
                          ^                           ^
                          └──── control plane ────────┘
                         (certs, routing rules, policy)
```

| 기능        | 내용                                                         |
|-------------|--------------------------------------------------------------|
| mTLS        | 서비스 사이 자동 암호화와 서비스 신원 확인, 인증서 자동 교체 |
| 트래픽 관리 | 재시도, 타임아웃, 가중치 분할(카나리), 장애 주입             |
| 권한 정책   | 어느 서비스가 어느 서비스를 부를 수 있는지                   |
| 관측        | 요청 수·오류율·지연 지표, 분산 트레이스 연결                 |

- 서비스 수가 적거나 Ingress 하나로 충분하면 메시 없이 [리버스 프록시](../web_server/reverse_proxy.md)와 앱 라이브러리로도 됩니다. 메시는 프록시·컨트롤 플레인 운영 부담과 지연이 더해집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 항목            | Istio                                                      | Linkerd                                       | Consul                                        |
|-----------------|------------------------------------------------------------|-----------------------------------------------|-----------------------------------------------|
| 데이터 플레인   | Envoy(sidecar), ambient는 ztunnel(L4) + Envoy waypoint(L7) | Rust로 만든 전용 micro-proxy(linkerd2-proxy)  | Envoy sidecar                                 |
| 대상 환경       | Kubernetes                                                 | Kubernetes                                    | Kubernetes, VM, 여러 플랫폼(서비스 탐색 포함) |
| 라이선스        | Apache 2.0                                                 | Apache 2.0                                    | BSL 1.1(1.17.0 이후)                          |
| 안정 판 배포    | 프로젝트가 배포                                            | 2024-02부터 프로젝트는 edge만, 안정 판은 벤더 | HashiCorp(IBM)가 배포                         |
| 최신 판         | 1.32.0(2026-11-09)                                         | edge-26.11.2, 벤더 안정 판 2.20               | v2.1.0(2026-10-22)                            |
| 지원 Kubernetes | 1.33~1.37(1.32 기준)                                       | 미확인                                        | 미확인                                        |
| 판 지원 기간    | N+2 minor 출시 뒤 6주까지(1.32는 2027-06 예상)             | 벤더 정책                                     | 미확인                                        |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 데이터 플레인 구조

### 3.1 Istio: sidecar와 ambient

| 모드    | 구조                                                                                             | 상태(공식 문서)                                                             |
|---------|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| sidecar | pod마다 Envoy를 붙임                                                                             | Stable, 여러 클러스터 포함                                                  |
| ambient | 노드마다 ztunnel이 L4(mTLS, 인증, L4 권한, 지표) 처리, L7이 필요한 namespace에만 waypoint(Envoy) | 1.22부터 단일 클러스터 운영 가능, 여러 네트워크 다중 클러스터는 1.29에 Beta |

- ztunnel은 워크로드의 HTTP를 해석하지 않습니다. 재시도·헤더 기반 라우팅 같은 L7 기능은 waypoint가 있어야 합니다.

### 3.2 Linkerd

- 프록시는 Envoy가 아니라 Linkerd 전용으로 Rust로 만든 micro-proxy입니다. 기능 범위를 좁혀 가볍게 만든 대신, Envoy 확장 기능은 쓸 수 없습니다.
- pod마다 sidecar로 붙는 구조입니다.

### 3.3 Consul

- Consul이 Envoy sidecar를 배포하고 설정을 내려줍니다. Consul의 서비스 탐색(catalog)과 같은 제품이라 Kubernetes 밖의 VM 서비스까지 한 메시로 묶을 수 있습니다.
- v2.0.0(2026-05-22)에서 Envoy 1.37.2 이상으로 올렸고, HTTP 서버 기본 타임아웃(read·write)이 30초에서 15분으로 바뀌었으며, api-gateway·terminating-gateway의 경로 정규화로 L7 권한 우회(CVE-2024-10005)를 막았습니다. 다중 포트 서비스와 전역 처리율 제한은 Enterprise 전용입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 배포와 라이선스

- Istio: Apache 2.0, 프로젝트가 안정 판을 냅니다. 지원은 다음다음 minor(N+2)가 나온 뒤 6주까지라 대략 반년 남짓입니다.
- Linkerd: 소스는 Apache 2.0이지만 "As of February 2024, the Linkerd open source project itself no longer provides stable release artifacts." 프로젝트는 주간 edge 판만 내고, 안정 판은 벤더가 냅니다. 대표 배포판 Buoyant Enterprise for Linkerd는 "Companies with fewer than 50 employees can also run BEL for production use, at any scale."이고, 그 밖의 운영 사용은 유료 계획(가격 비공개)입니다. edge 판을 직접 운영할 수도 있지만 매주 바뀌는 판을 따라가야 합니다.
- Consul: 1.17.0 이후 BSL 1.1입니다. 운영 사용은 허용되지만 Consul을 경쟁 유료·호스팅 제품으로 제3자에게 제공하는 것은 제한되고, 각 판은 출시 4년 뒤 MPL 2.0으로 바뀝니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 고르는 기준

| 상황                                                     | 먼저 볼 것                   | 이유                                              |
|----------------------------------------------------------|------------------------------|---------------------------------------------------|
| L7 기능(헤더 라우팅, 장애 주입, 세밀한 권한)이 많이 필요 | Istio                        | Envoy 기능 전체, 생태계가 큼                      |
| pod마다 프록시를 두는 부담을 줄이고 싶음                 | Istio ambient                | 노드 단위 ztunnel, L7은 필요한 곳만               |
| mTLS와 기본 지표만 가볍게, 운영 단순                     | Linkerd                      | 전용 경량 프록시. 안정 판 조건(벤더·인원 수) 확인 |
| Kubernetes와 VM이 섞여 있고 서비스 탐색도 필요           | Consul                       | 서비스 catalog와 메시가 한 제품. BSL 조건 확인    |
| 서비스 몇 개, 외부 진입만 관리                           | 메시 없이 Ingress·게이트웨이 | 운영 부담 대비 이득이 적음                        |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 도입 전 확인

이번에 공식 문서와 대조하지 않은 일반 점검 목록입니다.

- 지연과 자원: 프록시가 요청마다 한 번 더 거칩니다. 시범 서비스에서 p99 지연과 프록시 CPU·메모리를 먼저 잽니다.
- 인증서: 메시 CA의 루트 인증서 보관·교체 절차를 정합니다.
- 업그레이드: 컨트롤 플레인과 데이터 플레인을 함께 올려야 하는 경우가 많습니다. 판 지원 기간이 짧은 Istio는 반년 안팎마다 올릴 계획이 필요합니다.
- 장애 영향: 메시 컨트롤 플레인이 멈추면 새 인증서 발급·설정 배포가 멈춥니다. 데이터 플레인은 마지막 설정으로 계속 동작하는지 시범 환경에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Envoy](../web_server/envoy.md) — Istio·Consul의 데이터 플레인 프록시
- [Kubernetes 기초](./kubernetes_basic.md) — 메시가 올라가는 바탕
- [관리형 컨테이너 플랫폼 비교](./managed_container_platforms.md) — EKS·GKE·AKS

---

## 참고 자료

- Istio: [Announcing 1.32](https://istio.io/latest/news/releases/1.32.x/announcing-1.32/) · [Supported releases](https://istio.io/latest/docs/releases/supported-releases/) · [Ambient overview](https://istio.io/latest/docs/ambient/overview/) · [Data plane modes](https://istio.io/latest/docs/overview/dataplane-modes/) — ★★★☆☆
- Linkerd: [Releases](https://linkerd.io/releases/) · [Overview](https://linkerd.io/2-edge/overview/) · [Buoyant pricing](https://buoyant.io/pricing) — ★★★☆☆
- Consul: [Service mesh](https://developer.hashicorp.com/consul/docs/connect) · [LICENSE](https://github.com/hashicorp/consul/blob/main/LICENSE) · [v2.0.0 release](https://github.com/hashicorp/consul/releases/tag/v2.0.0) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
