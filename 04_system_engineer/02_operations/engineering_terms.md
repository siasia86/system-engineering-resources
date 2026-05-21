# 엔지니어링 실무 용어

개발/운영 현장에서 자주 사용하는 용어를 정리합니다.

## 목차

| 섹션 |
|------|
| [1. 버그 및 장애](#1-버그-및-장애) / [2. 동시성](#2-동시성) / [3. 설계 및 코드](#3-설계-및-코드) |
| [4. 운영 및 SRE](#4-운영-및-sre) / [5. 성능](#5-성능) / [6. 보안](#6-보안) |
| [7. 협업 및 프로세스](#7-협업-및-프로세스) |

---

## 1. 버그 및 장애

| 용어 | 발음/약어 | 의미 |
|------|-----------|------|
| Edge case | 엣지 케이스 | 경계값·극단 입력 상황 |
| Corner case | 코너 케이스 | 여러 엣지 조건이 동시에 발생 |
| Off-by-one | 오프바이원 | 반복문 경계 1 차이 버그 |
| Regression | 리그레션 | 수정 후 기존 기능이 깨짐 |
| Flaky test | 플레이키 테스트 | 가끔 실패하는 불안정한 테스트 |
| Hotfix | 핫픽스 | 긴급 패치 |
| Workaround | 워크어라운드 | 근본 해결 전 임시 우회 방법 |
| Root cause | 루트 코즈 | 장애의 근본 원인 |
| Cascading failure | 캐스케이딩 장애 | 한 곳 장애가 연쇄적으로 전파 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 동시성

| 용어 | 의미 |
|------|------|
| Race condition | 타이밍에 따라 결과가 달라지는 동시성 버그 |
| Deadlock | 두 프로세스가 서로 대기하며 영구 멈춤 |
| Livelock | 서로 양보하며 진행 못 하는 상태 (CPU는 소모) |
| Starvation | 특정 프로세스가 자원을 계속 못 받는 상태 |
| Mutex | 상호 배제 락 — 한 번에 하나만 접근 |
| Semaphore | 동시 접근 수를 제한하는 카운터 |
| Atomic operation | 중간에 끊기지 않는 단일 연산 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설계 및 코드

| 용어 | 의미 |
|------|------|
| Technical debt | 빠른 개발로 쌓인 나중에 갚아야 할 부채 |
| Idempotent | 여러 번 실행해도 결과가 같음 |
| Single point of failure (SPOF) | 하나 죽으면 전체 죽는 구조 |
| Graceful degradation | 일부 실패해도 전체는 동작 유지 |
| Graceful shutdown | 진행 중인 요청 완료 후 종료 |
| Backward compatibility | 이전 버전과 호환 유지 |
| Abstraction | 복잡한 내부를 숨기고 인터페이스만 노출 |
| Coupling | 모듈 간 의존도 (낮을수록 좋음) |
| Cohesion | 모듈 내부 응집도 (높을수록 좋음) |
| DRY | Don't Repeat Yourself — 중복 제거 원칙 |
| YAGNI | You Aren't Gonna Need It — 필요할 때 만들기 |
| KISS | Keep It Simple, Stupid — 단순하게 유지 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 운영 및 SRE

| 용어 | 약어 | 의미 |
|------|------|------|
| Postmortem | - | 장애 후 원인 분석 문서 (비난 없이) |
| Runbook | - | 반복 작업 절차서 |
| Playbook | - | 장애 대응 시나리오별 절차서 |
| Toil | - | 자동화 안 된 반복 수작업 |
| On-call | - | 장애 대응 당번 |
| Blast radius | - | 장애 발생 시 영향 범위 |
| Service Level Objective | SLO | 내부 서비스 목표 수준 (예: 가용성 99.9%) |
| Service Level Agreement | SLA | 고객과의 서비스 수준 계약 |
| Service Level Indicator | SLI | SLO 측정 지표 (예: 응답 시간) |
| Mean Time To Recovery | MTTR | 평균 복구 시간 |
| Mean Time Between Failures | MTBF | 평균 장애 간격 |
| Change Management | - | 변경 사항 검토·승인·배포 프로세스 |
| Canary deployment | - | 일부 트래픽에만 먼저 배포해서 검증 |
| Blue-Green deployment | - | 구버전/신버전 환경을 동시에 유지하며 전환 |
| Feature flag | - | 코드 배포 없이 기능 ON/OFF |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 성능

| 용어 | 의미 |
|------|------|
| Bottleneck | 전체 성능을 제한하는 병목 지점 |
| Latency | 요청~응답까지 걸리는 시간 |
| Throughput | 단위 시간당 처리량 |
| P99 / P95 | 상위 1% / 5% 응답 시간 (꼬리 지연) |
| Cache hit/miss | 캐시에서 찾음 / 못 찾아 원본 조회 |
| Thundering herd | 캐시 만료 시 다수 요청이 동시에 DB 직접 조회 |
| Hot spot | 특정 키/노드에 요청이 집중되는 현상 |
| Backpressure | 처리 속도 초과 시 상위에 속도 조절 신호 전달 |
| Jitter | 지연 시간의 변동폭 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안

| 용어 | 의미 |
|------|------|
| Least privilege | 최소 권한 원칙 — 필요한 권한만 부여 |
| Defense in depth | 다층 방어 — 여러 보안 레이어 적용 |
| Attack surface | 공격 가능한 노출 영역 |
| Zero trust | 내부 네트워크도 신뢰하지 않는 보안 모델 |
| CVE | Common Vulnerabilities and Exposures — 공개 취약점 번호 |
| CVSS | 취약점 심각도 점수 (0~10) |
| Hardening | 불필요한 기능 제거·설정 강화로 공격면 축소 |
| Secrets management | 패스워드·키·토큰을 안전하게 저장·배포 |
| Supply chain attack | 의존성(라이브러리·패키지)을 통한 공격 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 협업 및 프로세스

| 용어 | 의미 |
|------|------|
| RFC | Request for Comments — 변경 제안 문서 |
| ADR | Architecture Decision Record — 아키텍처 결정 기록 |
| Spike | 불확실한 기술을 검증하기 위한 시간 제한 탐색 |
| Bikeshedding | 중요하지 않은 사소한 것에 과도하게 논쟁 |
| Rubber duck debugging | 문제를 소리 내어 설명하며 스스로 해결 |
| Bus factor | 몇 명이 빠지면 프로젝트가 멈추는지 나타내는 수 |
| Yak shaving | 본 작업 전에 연쇄적으로 생기는 사전 작업들 |
| Dogfooding | 자사 제품을 직접 사용해서 검증 |
| Greenfield | 기존 코드 없이 처음부터 시작하는 프로젝트 |
| Brownfield | 기존 레거시 위에서 작업하는 프로젝트 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Google SRE Book: [sre.google/sre-book/table-of-contents](https://sre.google/sre-book/table-of-contents/) — ★★★★☆
- The Twelve-Factor App: [12factor.net](https://12factor.net/) — ★★★☆☆

---

**작성일**: 2026-05-21

**마지막 업데이트**: 2026-05-21

© 2026 siasia86. Licensed under CC BY 4.0.
