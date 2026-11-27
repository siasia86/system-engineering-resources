---
name: cloud-design-patterns-official-notes
description: Azure Architecture Center 클라우드 설계 패턴 카탈로그 44개와 Well-Architected 기둥 표기, 2014년판 8개 문제 영역 정리.
tags:
  - design-patterns
  - architecture
  - reliability
last_checked: 2026-11-27
sources:
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/
  - https://learn.microsoft.com/en-us/azure/well-architected/reliability/design-patterns
  - https://learn.microsoft.com/en-us/previous-versions/msp-n-p/dn568099(v=pandp.10)
  - https://learn.microsoft.com/en-us/previous-versions/msp-n-p/dn589772(v=pandp.10)
---

# 클라우드 설계 패턴 공식 자료 참조 노트

## 1. 현재 카탈로그 (2026-11-27 확인, 페이지 갱신 2026-11-24)

- 표 열: Pattern | Summary | Well-Architected Framework pillars. 영역 제목 없음. 기둥: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency.
- 패턴 44개: Ambassador, Anti-Corruption Layer, Asynchronous Request-Reply, Backends for Frontends, Bulkhead, Cache-Aside, Choreography, Circuit Breaker, Claim Check, Compensating Transaction, Competing Consumers, Compute Resource Consolidation, CQRS, Deployment Stamps, Event Sourcing, External Configuration Store, Federated Identity, Gatekeeper, Gateway Aggregation, Gateway Offloading, Gateway Routing, Geode, Health Endpoint Monitoring, Idempotent Consumer, Index Table, Leader Election, Materialized View, Messaging Bridge, Pipes and Filters, Priority Queue, Publisher-Subscriber, Quarantine, Queue-Based Load Leveling, Rate Limiting, Retry, Saga, Scheduler Agent Supervisor, Sequential Convoy, Sharding, Sidecar, Static Content Hosting, Strangler Fig, Throttling, Valet Key.
- 페이지에 Combine patterns, Antipatterns, AI agent orchestration patterns 절이 있음.
- 옛 주소 `patterns/category/availability`는 Well-Architected "Architecture design patterns that support reliability" 문서(canonical `well-architected/reliability/design-patterns`)를 보여 줌.

## 2. 2014년판 (보관 문서)

- 홈(2014-01): "twenty-four design patterns and ten related guidance topics". Bulkhead, Geode, Deployment Stamps, Strangler Fig, Sidecar, Ambassador, Anti-Corruption Layer, Backends for Frontends, Gateway 패턴은 그때 목록에 없음.
- "Problem Areas in the Cloud": "we identified the following eight categories" — Availability, Data Management, Design and Implementation, Messaging, Management and Monitoring, Performance and Scalability, Resiliency, Security.

## 3. 시험

- 개념 문서라 실행하지 않음.
