# Engineering

시니어/아키텍트급 엔지니어링 주제. SRE 프로세스, 배포 전략, 조직 설계, 비용 최적화를 다룹니다.

## 구조

| 디렉토리                         | 설명                                                           | 문서 수 |
|----------------------------------|----------------------------------------------------------------|---------|
| [reliability/](./reliability/)   | 신뢰성 — Chaos Engineering, Incident 관리, On-Call, Postmortem | 6       |
| [delivery/](./delivery/)         | 딜리버리 — ADR, 용량 계획, 변경 관리, 무중단 마이그레이션      | 5       |
| [organization/](./organization/) | 조직 설계 — Platform Engineering, Team Topology, 레거시 현대화 | 4       |
| [cost/](./cost/)                 | 비용 — 클라우드 비용 최적화, 기술 부채 관리                    | 2       |

## 주요 문서

- [incident_management.md](./reliability/incident_management.md) — 장애 대응 프로세스 (SEV 1~4)
- [postmortem_framework.md](./reliability/postmortem_framework.md) — 포스트모텀 작성 프레임워크
- [capacity_planning.md](./delivery/capacity_planning.md) — 용량 산정, 스케일링 전략
- [platform_engineering.md](./organization/platform_engineering.md) — 플랫폼 팀 구축 가이드
- [cloud_cost_optimization.md](./cost/cloud_cost_optimization.md) — RI/Spot/Savings Plan 전략

## 추천 학습 순서

`reliability (SRE 기초)` → `delivery (배포 전략)` → `organization (팀 설계)` → `cost (최적화)`

## 전제 조건

[02_infrastructure/](../02_infrastructure/) 전반 이해. 실무 운영 경험 3년+ 권장.

## 관련 섹션

- 인프라 도구: [02_infrastructure/](../02_infrastructure/)
- 보안 아키텍처: [04_security/cloud/](../04_security/cloud/)
- SRE 로드맵: [06_career/roadmap/sre_roadmap.md](../06_career/roadmap/sre_roadmap.md)

[⬆ 루트 README로 돌아가기](../README.md)

---

**작성일**: 2026-07-07

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
