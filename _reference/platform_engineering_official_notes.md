---
name: platform-engineering-official-notes
description: Platform Engineering 문서 작성 시 참조할 공식 소스. CNCF Platforms White Paper, Maturity Model 기반.
tags:
  - platform-engineering
  - idp
  - cncf
  - team-topologies
last_checked: 2026-07-07
sources:
  - https://tag-app-delivery.cncf.io/whitepapers/platforms/
  - https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/
---

# Platform Engineering 공식 참조 노트

## 1. 출처

| 출처                                | URL                                                                       | 유형          |
|-------------------------------------|---------------------------------------------------------------------------|---------------|
| CNCF Platforms White Paper          | https://tag-app-delivery.cncf.io/whitepapers/platforms/                   | CNCF TAG 공식 |
| Platform Engineering Maturity Model | https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/ | CNCF TAG 공식 |

## 2. 핵심 정의 (CNCF WP 원문)

### Platform 정의

> "A platform for cloud-native computing is an integrated collection of capabilities defined and presented according to the needs of the platform users. It is a cross-cutting layer that ensures a consistent experience for acquiring and integrating typical capabilities and services for a broad set of applications and use cases."

### Why Platforms (5대 가치)

1. Reduce cognitive load on product teams → accelerate development
2. Improve reliability/resiliency by dedicating experts to platform capabilities
3. Accelerate delivery by reusing platform tools/knowledge across teams
4. Reduce risk (security, regulatory, functional) through governance
5. Enable cost-effective use of cloud services while maintaining UX control

## 3. Platform Attributes (7가지, CNCF WP)

1. Platform as a product
2. User experience (GUI, API, CLI, IDE, portal)
3. Documentation and onboarding (Golden Path)
4. Self-service (on-demand, minimal manual intervention)
5. Reduced cognitive load for users
6. Optional and composable
7. Secure by default

## 4. Platform Team 책임 (CNCF WP)

1. Research platform user requirements and plan feature roadmap
2. Market, evangelize and advocate for platform values
3. Manage/develop interfaces (portals, APIs, docs, templates, CLI tools)

## 5. Platform Maturity Levels (CNCF WP)

1. Provision capabilities on demand (compute, storage, databases, identities)
2. Provision service spaces (pipelines, artifact stores, telemetry)
3. Third-party software provisioning with dependencies
4. Complete environments from templates (web dev, MLOps)
5. Observe functionality, performance, cost through automatic instrumentation

## 6. Challenges (CNCF WP)

1. Must treat platform as product — develop with users
2. Must choose priorities and initial partner app teams carefully
3. Must seek enterprise leadership support and show value stream impact

## 7. Golden Path

CNCF WP에서 사용한 정의:
- "a bundle often described as a golden path" — reusable supply chain workflow (build, scan, test, deploy, observe) + initial project template + documentation
- Backstage (Spotify)가 대표적 Golden Path 구현체

## 8. Internal Developer Platform (IDP)

Martin Fowler/Evan Bottcher 정의 (CNCF WP에서 인용):
> "a digital platform is a foundation of self-service APIs, tools, services, knowledge and support which are arranged as a compelling internal product. Autonomous delivery teams can make use of the platform to deliver product features at a higher pace, with reduced coordination."
