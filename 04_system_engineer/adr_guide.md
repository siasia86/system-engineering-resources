# ADR (Architecture Decision Record) 가이드

인프라/시스템 엔지니어링 관점에서 ADR을 작성하고 관리하는 방법을 정리합니다.

---

## 1. ADR 이란

ADR은 중요한 기술 결정을 "왜 그렇게 했는지" 기록하는 경량 문서입니다.
무엇을 결정했는지뿐 아니라, 어떤 대안을 검토했고 어떤 트레이드오프를 수용했는지를 남깁니다.

### ADR이 해결하는 문제

| 상황                                    | ADR 없이                      | ADR 있으면                    |
|-----------------------------------------|-------------------------------|-------------------------------|
| "왜 Rocky Linux 선택했지?"              | 담당자 퇴사하면 모름          | ADR-001 읽으면 됨            |
| "왜 zabbix 쓰지 Prometheus 안 쓰지?"   | 회의록 뒤져야 함              | ADR-003에 비교표 있음        |
| 같은 논의 반복                          | 매번 처음부터                 | "ADR-005 참고" 로 종결       |
| 신규 입사자 온보딩                      | 구전으로 전달                 | docs/adr/ 읽으면 됨          |

---

## 2. 디렉토리 구조

```
project/
└── docs/
    └── adr/
        ├── README.md          ← ADR 목록 (인덱스)
        ├── adr-001-os-selection.md
        ├── adr-002-iac-tool.md
        ├── adr-003-monitoring-stack.md
        └── templates/
            └── adr-template.md
```

### README.md (인덱스)

```markdown
# Architecture Decision Records

| ADR     | 제목                          | 상태     | 날짜       |
|---------|-------------------------------|----------|------------|
| ADR-001 | 서버 OS 선택                  | Accepted | 2026-03-01 |
| ADR-002 | IaC 도구 선택                 | Accepted | 2026-03-05 |
| ADR-003 | 모니터링 스택 선택            | Proposed | 2026-03-20 |
```

---

## 3. 템플릿

### 기본 템플릿 (MADR 기반)

```markdown
# ADR-NNN: 제목

- **Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
- **Date**: YYYY-MM-DD
- **Deciders**: 담당자, 참여자
- **Tags**: infra, network, database, monitoring, security, deploy

## Context

왜 이 결정이 필요한가? 현재 상황과 문제점을 기술합니다.

## Decision

무엇을 선택했는가? 핵심 결정 사항을 명확히 기술합니다.

## Alternatives Considered

| 옵션              | 장점                  | 단점                  |
|-------------------|-----------------------|-----------------------|
| Option A          |                       |                       |
| Option B          |                       |                       |
| Option C          |                       |                       |

## Consequences

### 긍정적
-

### 부정적
-

### 리스크
-

## References

- 관련 문서, 링크, 이전 ADR 번호
```

### 상태 흐름

```
Proposed → Accepted → (운영 중)
                   ↘ Deprecated (더 이상 유효하지 않음)
                   ↘ Superseded by ADR-NNN (새 결정으로 대체)
```

---

## 4. ADR 작성 대상

### 작성해야 하는 경우 ✅

| 분류         | 예시                                              |
|--------------|---------------------------------------------------|
| OS/플랫폼   | Rocky Linux vs Ubuntu, 컨테이너 vs VM             |
| 도구 선택   | Ansible vs Puppet, zabbix vs Prometheus            |
| DB 엔진     | MySQL vs PostgreSQL, RDS vs 자체 운영              |
| 네트워크    | VPC 구조, 로드밸런서 선택, CDN 도입                |
| 보안        | 인증 방식, 암호화 정책, 방화벽 구조                |
| 배포        | Blue-Green vs Rolling, CI/CD 파이프라인 구조       |
| 아키텍처    | 마이크로서비스 vs 모놀리스, 이벤트 드리븐 도입     |

### 작성 불필요 ❌

- 패키지 마이너 버전 업데이트
- 일반 버그 수정
- 설정값 미세 조정
- 문서 오타 수정
- 일상적 운영 작업

### 판단 기준

```
다음 중 하나라도 해당하면 ADR 작성:
- [ ] 되돌리기 어려운 결정인가?
- [ ] 여러 팀/서비스에 영향을 주는가?
- [ ] 비용이 크게 달라지는가?
- [ ] 6개월 후 "왜?" 라고 물을 가능성이 있는가?
```

---

## 5. 인프라 ADR 예시

### ADR-001: 서버 OS 선택

```markdown
# ADR-001: 게임 서버 OS 선택

- **Status**: Accepted
- **Date**: 2026-03-01
- **Deciders**: 인프라팀
- **Tags**: infra, os

## Context

신규 게임 프로젝트의 서버 OS를 선정해야 합니다.
기존 CentOS 7 EOL(2024-06)로 대체 OS가 필요합니다.
게임 서버는 RHEL 계열 의존성이 높고, SELinux 정책 운영 경험이 있습니다.

## Decision

Rocky Linux 10을 표준 OS로 선정합니다.

## Alternatives Considered

| 옵션              | 장점                      | 단점                      |
|-------------------|---------------------------|---------------------------|
| Rocky Linux 10    | RHEL 1:1 호환, 무료      | 커뮤니티 역사 짧음        |
| Ubuntu 24.04 LTS  | 넓은 생태계, 문서 풍부   | RHEL 패키지 호환성 문제   |
| AlmaLinux 10      | RHEL 호환, 안정적        | Rocky 대비 커뮤니티 작음  |
| RHEL 10           | 공식 지원                 | 라이선스 비용             |

## Consequences

### 긍정적
- 기존 CentOS 운영 경험 그대로 활용
- SELinux 정책 마이그레이션 최소화
- RHEL 생태계 도구 호환 (rpm, yum/dnf, systemd)

### 부정적
- Ubuntu 대비 최신 패키지 반영 느림
- 일부 개발자 Ubuntu 선호 (개발 환경 차이)

### 리스크
- Rocky Linux 프로젝트 지속성 (CentOS 전례)
  → AlmaLinux를 백업 플랜으로 유지

## References
- CentOS EOL 공지: https://blog.centos.org/
- Rocky Linux 10 릴리스 노트
```

### ADR-002: IaC 도구 선택

```markdown
# ADR-002: Configuration Management 도구 선택

- **Status**: Accepted
- **Date**: 2026-03-05
- **Deciders**: 인프라팀
- **Tags**: infra, automation

## Context

수십 대 서버의 설정 관리를 수동으로 하고 있어
일관성 유지가 어렵고 휴먼 에러가 발생합니다.

## Decision

Ansible을 Configuration Management 도구로 선정합니다.

## Alternatives Considered

| 옵션              | 장점                      | 단점                      |
|-------------------|---------------------------|---------------------------|
| Ansible           | 에이전트리스, YAML, 낮은 진입장벽 | 대규모 시 느림     |
| Puppet            | 선언적, 대규모 안정적     | Ruby DSL 학습 비용        |
| Chef              | 유연한 Ruby 기반          | 복잡도 높음, 에이전트 필요|
| Salt              | 빠른 실행, 이벤트 드리븐  | 커뮤니티 축소 추세        |

## Consequences

### 긍정적
- SSH 기반으로 에이전트 설치 불필요
- YAML 기반으로 팀 학습 비용 낮음
- AWX/Semaphore로 웹 UI 확장 가능

### 부정적
- 수백 대 이상 시 실행 속도 저하 가능
- 상태 관리(drift detection) 약함

### 리스크
- 규모 확장 시 성능 → Mitogen 플러그인 또는 AWX 분산 실행

## References
- ADR-001 (Rocky Linux 선정 → RHEL 계열 Ansible 호환성 확인)
- Ansible 공식 문서: https://docs.ansible.com/
```

---

## 6. 작성 규칙

### 필수 규칙

| 규칙                              | 이유                                          |
|-----------------------------------|-----------------------------------------------|
| 번호는 순차 (ADR-001, 002...)     | 참조 용이, 시간순 추적                        |
| 한 번 Accepted 되면 수정하지 않음 | 결정 시점의 맥락 보존 (불변성)                |
| 대체 시 Superseded 처리           | 이전 결정 이력 유지                           |
| 대안을 반드시 기록                | "왜 다른 걸 안 했는지"가 핵심                 |
| 짧게 작성 (1~2 페이지)           | 길면 안 읽음                                  |

### 안티패턴

| 안티패턴                          | 문제점                                        |
|-----------------------------------|-----------------------------------------------|
| 결정만 쓰고 대안 생략             | "왜?" 에 답할 수 없음                         |
| 너무 상세하게 작성                | 유지보수 부담, 안 읽게 됨                     |
| 사후에 몰아서 작성                | 결정 당시 맥락 왜곡                           |
| Status 업데이트 안 함             | 현재 유효한 결정을 알 수 없음                 |
| 모든 결정을 ADR로 작성            | 노이즈 증가, 중요한 결정이 묻힘               |

---

## 7. 팀 운영

### Git 워크플로우

```bash
# 새 ADR 작성
cp docs/adr/templates/adr-template.md docs/adr/adr-004-cdn-selection.md
vi docs/adr/adr-004-cdn-selection.md

# PR로 리뷰
git checkout -b adr/004-cdn-selection
git add docs/adr/adr-004-cdn-selection.md
git commit -m "ADR-004: CDN 선택"
git push origin adr/004-cdn-selection
# → PR 생성 → 팀 리뷰 → Merge 시 Accepted
```

### 리뷰 체크리스트

```
PR 리뷰 시 확인 사항:
- [ ] Context가 현재 상황을 정확히 반영하는가?
- [ ] 대안이 2개 이상 검토되었는가?
- [ ] 각 대안의 장단점이 공정하게 기술되었는가?
- [ ] Consequences에 리스크가 포함되었는가?
- [ ] 관련 ADR 참조가 있는가?
```

### ADR 도입 순서

```
1. templates/ 에 팀 템플릿 생성
2. 기존 주요 결정 3~5개를 ADR로 소급 작성 (팀 연습)
3. 이후 새 결정부터 ADR 필수화
4. PR 리뷰 프로세스에 포함
5. 분기별 ADR 인덱스 정리
```

---

## 8. AI 에이전트와 ADR

### ADR을 AI 스킬로 등록

```markdown
<!-- ~/.kiro/skills/adr/SKILL.md -->
---
name: adr-writer
description: >
  Create and review Architecture Decision Records.
  Use when user discusses technology selection, infrastructure
  changes, or asks to document a technical decision.
---

# ADR Writer

## When triggered
- User compares technology options
- User asks "why did we choose X?"
- User requests decision documentation

## Workflow
1. Ask for context and constraints
2. List alternatives with pros/cons table
3. Generate ADR in MADR template format
4. Save to docs/adr/adr-NNN-title.md
```

### AI에게 ADR 작성 요청 예시

```
"Rocky Linux vs Ubuntu 비교해서 ADR 작성해줘"
"현재 모니터링 도구 선택 과정을 ADR로 정리해줘"
"ADR-001 참고해서 DB 선택 ADR 만들어줘"
```

AI가 기존 ADR을 참조하면 일관된 형식과 맥락을 유지할 수 있습니다.


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-11

© 2026 siasia86. Licensed under CC BY 4.0.
