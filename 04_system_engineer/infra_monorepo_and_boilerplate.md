# 인프라 Monorepo & 보일러플레이트 가이드

인프라 코드, 문서, 설정을 하나의 저장소에서 관리하고
반복 작업을 템플릿화하는 방법을 정리합니다.

---

## 1. Monorepo 구조

### 전체 디렉토리 구조

```
infra-monorepo/
├── docs/
│   ├── adr/                        ← 기술 결정 기록
│   ├── runbooks/                   ← 운영 매뉴얼
│   └── postmortem/                 ← 장애 보고서
├── ansible/
│   ├── ansible.cfg
│   ├── inventories/
│   │   ├── dev/
│   │   ├── qa/
│   │   ├── stg/
│   │   └── prd/
│   ├── playbooks/
│   ├── roles/
│   └── group_vars/
├── terraform/
│   ├── modules/                    ← 재사용 모듈
│   └── environments/
│       ├── dev/
│       ├── stg/
│       └── prd/
├── monitoring/
│   ├── zabbix/
│   └── alerting/
├── scripts/
│   └── common/
├── templates/                      ← 보일러플레이트
│   ├── new-service/
│   ├── new-server/
│   └── new-project/
├── .kiro/
│   ├── agents/
│   └── skills/
├── .gitlab-ci.yml                  ← CI/CD
└── README.md
```

### Monorepo 장단점

| 장점                              | 단점                     |
|-----------------------------------|--------------------------|
| 코드 간 참조/재사용 쉬움          | 저장소 커지면 clone 느림 |
| 변경 영향 범위 한눈에 파악        | 세밀한 권한 분리 어려움  |
| 일관된 CI/CD 파이프라인           | 팀 규모 커지면 충돌 증가 |
| ADR, 문서가 코드와 함께 버전 관리 | 빌드/테스트 시간 증가    |

### Monorepo vs Polyrepo 판단 기준

| 기준                  | Monorepo | Polyrepo |
|-----------------------|----------|----------|
| 인프라팀 5명 이하     | ✅ 추천  |          |
| 인프라팀 10명 이상    |          | ✅ 추천  |
| 환경별 코드 공유 많음 | ✅ 추천  |          |
| 팀별 독립 배포 필요   |          | ✅ 추천  |
| 보안 등급 분리 필요   |          | ✅ 추천  |

---

## 2. Boilerplate (템플릿 자동 생성)

### 템플릿 디렉토리 구조

```
templates/new-service/
├── README.md.tmpl
├── ansible/
│   ├── playbook.yml.tmpl
│   └── inventory.yml.tmpl
├── terraform/
│   ├── main.tf.tmpl
│   └── variables.tf.tmpl
├── monitoring/
│   └── zabbix-template.yml.tmpl
├── docs/
│   └── adr/
│       └── adr-template.md
└── init.sh
```

### init.sh (템플릿 생성 스크립트)

```bash
#!/bin/bash
set -euo pipefail

SERVICE_NAME=$1
ENV=$2
DEST="services/${ENV}-${SERVICE_NAME}"

if [ -d "$DEST" ]; then
  echo "❌ ${DEST} already exists"
  exit 1
fi

cp -r templates/new-service/ "$DEST"
find "$DEST" -name "*.tmpl" | while read f; do
  sed -i "s/{{SERVICE_NAME}}/${SERVICE_NAME}/g
          s/{{ENV}}/${ENV}/g
          s/{{DATE}}/$(date +%Y-%m-%d)/g" "$f"
  mv "$f" "${f%.tmpl}"
done

echo "✅ Created: ${DEST}"
```

```bash
# 사용 예시
./templates/new-service/init.sh app-web prd
# → services/prd-app-web/ 생성 (네이밍 규칙 자동 적용)
```

### 보일러플레이트 종류

| 템플릿         | 용도              | 포함 내용                       |
|----------------|-------------------|---------------------------------|
| `new-service/` | 새 서비스 추가    | playbook, terraform, monitoring |
| `new-server/`  | 새 서버 추가      | inventory, 초기 설정 playbook   |
| `new-project/` | 새 프로젝트 시작  | 전체 디렉토리 구조 + ADR 템플릿 |
| `new-role/`    | Ansible 역할 추가 | role 디렉토리 구조 + defaults   |

---

## 3. Runbook (운영 매뉴얼)

장애 대응, 정기 작업 등 반복되는 운영 절차를 문서화합니다.

### 디렉토리 구조

```
docs/runbooks/
├── incident-response.md        ← 장애 대응 절차
├── server-add.md               ← 서버 추가 절차
├── deploy-rollback.md          ← 배포/롤백 절차
├── db-failover.md              ← DB 페일오버
├── certificate-renewal.md      ← 인증서 갱신
└── on-call-guide.md            ← 당직 가이드
```

### Runbook 템플릿

```markdown
# Runbook: [작업명]

- **최종 수정**: YYYY-MM-DD
- **담당**: 인프라팀
- **예상 소요**: N분
- **영향 범위**: [서비스/환경]

## 사전 조건
- [ ] 조건 1
- [ ] 조건 2

## 절차

### Step 1: [단계명]
```bash
command here
```

**확인**: 예상 결과

### Step 2: [단계명]
...

## 롤백 절차
1. ...
2. ...

## 트러블슈팅
| 증상 | 원인 | 해결 |
|------|------|------|
|      |      |      |
```

### Runbook vs ADR 차이

| 항목 | ADR                    | Runbook             |
|------|------------------------|---------------------|
| 목적 | "왜" 이렇게 결정했는가 | "어떻게" 실행하는가 |
| 변경 | 불변 (Superseded 처리) | 수시 업데이트       |
| 대상 | 기술 결정              | 운영 절차           |
| 독자 | 미래의 의사결정자      | 현재의 운영자       |


## 3-1. Checklist (작업 체크리스트)

인프라 작업 시 단계별로 확인하는 체크리스트입니다.
Runbook 내에 포함하거나 독립 문서로 관리합니다.

### 작업 단계별 체크리스트

```
Pre-flight (작업 전) → Execution (작업 중) → Post-flight (작업 후)
```

| 단계        | 확인 내용                                       |
|-------------|-------------------------------------------------|
| Pre-flight  | 백업 완료, 롤백 계획, 영향 범위, 공지, 승인     |
| Execution   | 단계별 실행 확인, 중간 검증, 로그 확인          |
| Post-flight | 서비스 정상, 모니터링 확인, 문서 업데이트, 공지 |

### 작업 유형별 체크리스트

#### 서버 신규 구축

```
Pre-flight:
- [ ] 서버 스펙 확정 (CPU, Memory, Disk)
- [ ] 네이밍 규칙 확인 ([env]-[category]-[service]-[detail])
- [ ] IP/네트워크 대역 할당

Execution:
- [ ] OS 설치 (Rocky Linux 10, Golden Path 기준)
- [ ] 초기 설정 playbook 실행 (ansible-playbook site.yml)
- [ ] SSH 키 배포 확인
- [ ] 방화벽 설정 (firewalld)
- [ ] SELinux enforcing 확인
- [ ] NTP 동기화 확인
- [ ] 모니터링 에이전트 설치 (zabbix agent2)

Post-flight:
- [ ] zabbix 호스트 등록 + 데이터 수신 확인
- [ ] 백업 스케줄 등록
- [ ] inventory 파일 업데이트
- [ ] 문서 업데이트 (서버 목록)
```

#### 배포/릴리스

```
Pre-flight:
- [ ] 빌드 성공 확인
- [ ] stg 환경 테스트 완료
- [ ] 롤백 절차 확인
- [ ] 배포 공지 (팀/관련자)

Execution:
- [ ] 배포 실행
- [ ] 헬스체크 통과 확인
- [ ] 로그 에러 없음 확인

Post-flight:
- [ ] 모니터링 지표 정상 확인 (5분 관찰)
- [ ] 배포 완료 공지
- [ ] 배포 이력 기록
```

#### DB 작업

```
Pre-flight:
- [ ] 풀 백업 완료 + 복구 테스트
- [ ] 쿼리 리뷰 (실행 계획 확인)
- [ ] 락 영향 범위 확인
- [ ] 점검 시간 공지

Execution:
- [ ] 쿼리 실행
- [ ] 결과 검증

Post-flight:
- [ ] 서비스 정상 확인
- [ ] 슬로우 쿼리 모니터링
- [ ] 작업 완료 공지
```

#### 네트워크 변경

```
Pre-flight:
- [ ] 영향 받는 서비스 목록 확인
- [ ] 방화벽 규칙 변경 내역 정리
- [ ] 롤백 규칙 준비

Execution:
- [ ] 규칙 적용
- [ ] 통신 테스트 (telnet, curl, ping)

Post-flight:
- [ ] 전체 서비스 통신 정상 확인
- [ ] 방화벽 규칙 문서 업데이트
```

### 환경별 Gate (승인 수준)

| 환경 | Pre-flight      | 승인           | Post-flight      |
|------|-----------------|----------------|------------------|
| dev  | 기본 체크       | 불필요         | 기본 확인        |
| qa   | 기본 체크       | 팀 내 공유     | 기본 확인        |
| stg  | 전체 체크리스트 | 팀 리드 승인   | 전체 확인        |
| prd  | 전체 체크리스트 | 팀 리드 + 승인 | 전체 확인 + 관찰 |

---

## 4. Postmortem (장애 보고서)

장애 발생 후 원인 분석과 재발 방지를 기록합니다.

### 템플릿

```markdown
# Postmortem: [장애 제목]

- **날짜**: YYYY-MM-DD HH:MM ~ HH:MM (KST)
- **영향**: [서비스명], [사용자 수/영향 범위]
- **심각도**: P1 | P2 | P3 | P4
- **작성자**: 담당자

## 타임라인

| 시각 (KST)  | 이벤트                              |
|-------------|-------------------------------------|
| 14:00       | 알림 발생                           |
| 14:05       | 담당자 확인 시작                    |
| 14:15       | 원인 파악                           |
| 14:30       | 조치 완료                           |
| 14:45       | 정상 확인                           |

## 원인 분석

### 직접 원인
-

### 근본 원인
-

## 조치 내용
-

## 재발 방지

| 항목                    | 담당   | 기한       | 상태     |
|-------------------------|--------|------------|----------|
| 모니터링 알림 추가      | OOO    | YYYY-MM-DD | 미완료   |
| Runbook 업데이트        | OOO    | YYYY-MM-DD | 미완료   |

## 교훈
-
```

### 심각도 기준

| 등급 | 기준             | 예시                   |
|------|------------------|------------------------|
| P1   | 서비스 전체 중단 | 게임 서버 전체 다운    |
| P2   | 주요 기능 장애   | 결제 불가, 로그인 불가 |
| P3   | 부분 기능 장애   | 일부 채널 접속 불가    |
| P4   | 경미한 영향      | 로그 수집 지연         |

---

## 5. Golden Path (표준 경로)

팀이 권장하는 "기본 선택지"를 정의합니다.
새 프로젝트/서비스 시작 시 고민 없이 따를 수 있는 표준입니다.

### Golden Path 문서 예시

```markdown
# Golden Path: 게임 서버 인프라

## OS
- **표준**: Rocky Linux 10 (ADR-001)
- **예외**: 컨테이너 워크로드 → Ubuntu 24.04

## Configuration Management
- **표준**: Ansible (ADR-002)
- **예외**: 없음

## Monitoring
- **표준**: zabbix 7.0 (ADR-003)
- **메트릭 수집**: zabbix agent2
- **알림**: zabbix → Slack webhook

## 네이밍
- **형식**: [env]-[category]-[service]-[detail]
- **환경**: dev / qa / stg / prd

## 배포
- **표준**: Ansible playbook + GitLab CI
- **전략**: Rolling update (기본), Blue-Green (대규모)

## 보안
- **SSH**: 키 인증만, 패스워드 비활성화
- **방화벽**: firewalld 기본 활성화
- **SELinux**: enforcing 모드
```

### Golden Path vs ADR 관계

```
ADR-001 (OS 선택)       ──┐
ADR-002 (IaC 선택)      ──┼──▶ Golden Path (표준 경로 요약)
ADR-003 (모니터링 선택) ──┘
```

ADR은 개별 결정의 "왜", Golden Path는 결정들의 "요약본"입니다.

---

## 6. 전체 문서 체계

```
┌──────────────────────────────────────────────────┐
│  infra-monorepo                                  │
│                                                  │
│  docs/                                           │
│  ├── adr/          ← "왜" 이렇게 결정했는가      │
│  ├── runbooks/     ← "어떻게" 실행하는가         │
│  ├── postmortem/   ← "무엇이" 잘못되었는가       │
│  └── golden-path/  ← "무엇을" 기본으로 쓰는가    │
│                                                  │
│  templates/        ← 보일러플레이트 (자동화)     │
│  .kiro/skills/     ← AI 에이전트 규칙            │
└──────────────────────────────────────────────────┘
```

| 문서 유형   | 질문             | 변경 빈도 | 독자                 |
|-------------|------------------|-----------|----------------------|
| ADR         | 왜?              | 불변      | 미래 의사결정자      |
| Runbook     | 어떻게?          | 수시      | 현재 운영자          |
| Postmortem  | 무엇이 잘못?     | 장애 후   | 전체 팀              |
| Golden Path | 무엇을 기본으로? | 분기별    | 신규 프로젝트 담당자 |
| Boilerplate | (자동 생성)      | 필요 시   | 프로젝트 시작자      |


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
