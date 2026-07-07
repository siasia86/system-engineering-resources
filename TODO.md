# TODO

md-style-check 잔여 이슈 및 신규 문서 작성 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 다이어그램 한글→영문](#1-다이어그램-한글영문) / [2. 기타 잔여 이슈](#2-기타-잔여-이슈) / [3. 검사 예외 파일](#3-검사-예외-파일) |
| [4. 신규 문서 — 시니어급 (20년차+)](#4-신규-문서--시니어급-20년차)                                                                  |

---

## 1. 다이어그램 한글→영문

✅ 완료 — CHANGELOG.md [2.3.0] Fixed 참조.

---

## 2. 기타 잔여 이슈

| 파일                                                     | 이슈 유형       | 설명                              |
|----------------------------------------------------------|-----------------|-----------------------------------|
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | _reference 규칙 | frontmatter 없음 (FILE_SKIP 예외) |

## 3. 검사 예외 파일

md-style-check 검사 대상에서 제외하는 파일입니다.

| 파일                                                     | 사유                                   |
|----------------------------------------------------------|----------------------------------------|
| `02_basic_linux/vim_airline.md`                          | 외부 프로젝트(vim-airline) README 원본 |
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | Kiro CLI 문서 (다이어그램 한글 의도적) |

---

## 4. 신규 문서 — 시니어급 (20년차+)

현재 레포는 SE 2~3년차(중급)가 메인 타겟입니다. 아래 문서를 추가하여 시니어/아키텍트급 콘텐츠를 보강합니다.

### 우선순위

| 순위 | 파일명                       | 카테고리           | 내용                                                    | 상태 |
|------|------------------------------|--------------------|---------------------------------------------------------|------|
| 1    | `incident_management.md`     | 04_system_engineer | 장애 등급 분류, 에스컬레이션, 커뮤니케이션, 지휘 체계   | ✅   |
| 2    | `slo_error_budget.md`        | 04_system_engineer | SLI 정의 → SLO 설정 → Error Budget 운영 → 의사결정 연동 | ✅   |
| 3    | `capacity_planning.md`       | 04_system_engineer | 트래픽 예측 → 서버 산정 → 비용 계산 프레임워크          | ✅   |
| 4    | `zero_downtime_migration.md` | 04_system_engineer | DB expand-contract, 트래픽 전환, 롤백 판단              | ✅   |
| 5    | `change_management.md`       | 04_system_engineer | 변경 등급, CAB, 배포 윈도우, 긴급 변경 프로세스         | ✅   |

### 후속 (우선순위 6~15)

| 순위 | 파일명                         | 카테고리           | 내용                                               | 상태 |
|------|--------------------------------|--------------------|----------------------------------------------------|------|
| 6    | `postmortem_framework.md`      | 04_system_engineer | 타임라인, 5 Whys, Contributing Factors, 재발 방지  | ✅   |
| 7    | `chaos_engineering.md`         | 04_system_engineer | 가설 → 실험 → 폭발 반경 제한 → 자동 롤백           | ✅   |
| 8    | `multi_region_architecture.md` | 04_system_engineer | Active-Active/Standby, RPO/RTO 설계                | ✅   |
| 9    | `platform_engineering.md`      | 04_system_engineer | IDP 설계, Golden Path, Self-service 인프라         | ✅   |
| 10   | `oncall_design.md`             | 04_system_engineer | 로테이션, 보상, 번아웃 방지, 런북, 핸드오프        | ✅   |
| 11   | `team_topology.md`             | 04_system_engineer | Stream-aligned/Platform/Enabling/Complicated 팀    | ✅   |
| 12   | `tech_debt_management.md`      | 04_system_engineer | 기술 부채 분류, 측정, 상환 우선순위                | ✅   |
| 13   | `cloud_cost_optimization.md`   | 12_tech_stack      | RI/SP 전략, Spot 활용, FinOps 프레임워크           | ✅   |
| 14   | `vendor_evaluation.md`         | 04_system_engineer | 도구/서비스 선정 기준, PoC 설계, TCO, Lock-in 평가 | ✅   |
| 15   | `legacy_modernization.md`      | 04_system_engineer | Strangler Fig, 단계별 분리, 데이터 이중 쓰기       | ✅   |

### 다음 세션: 레포 구조 전면 개편

§4 시니어 문서 15개 전부 완료. 다음 작업은 디렉토리 구조 마이그레이션입니다.

#### 목표 구조 (안 C: 역할×단계 하이브리드)



#### 변경 후 예상 tree

```
32_system-engineering-resources/
├── 01_fundamentals/
│   ├── linux/                    (28 files: basics+advanced+debugging)
│   ├── networking/               (12 files: protocols+infra)
│   ├── cs/
│   │   ├── cpu_cisc_risc.md
│   │   ├── data_structures/     (8 files)
│   │   └── testing/             (12 files, 4 subdirs)
│   └── programming/
│       ├── python/              (25 files)
│       └── c_cpp_csharp_go_python_bash_comparison.md
├── 02_infrastructure/
│   ├── containers/              (9 files: docker, k8s, helm)
│   ├── cicd/                    (8 files: jenkins, argocd, github)
│   ├── iac/                     (10 files: ansible, terraform, packer)
│   ├── monitoring/              (6 files: prometheus, zabbix, grafana)
│   ├── cloud_aws/               (5 files: s3, vpc, firewall)
│   ├── data_pipeline/           (4 files: kafka, log aggregation)
│   └── web_server/              (3 files: nginx, apache, haproxy)
├── 03_engineering/
│   ├── reliability/             (5: incident, slo, oncall, postmortem, chaos)
│   ├── delivery/                (4: change, zero_downtime, capacity, multi_region)
│   ├── organization/            (4: team_topology, platform, vendor, legacy)
│   └── cost/                    (2: cloud_cost, tech_debt)
├── 04_security/
│   ├── hardening/               (6: firewall, ssh, tls, hardening, secret, vuln)
│   ├── cloud/                   (4: aws_security, ddos, network_fw, attack_glossary)
│   ├── cve/                     (6+ files)
│   └── web_cwe/                 (4+ files)
├── 05_database/
│   ├── rdbms/                   (8: join, index, lock, explain, normalize, view, proc, tx)
│   ├── operations/              (8: install, replication, partition, migration, tuning)
│   ├── nosql/                   (6: redis, mongo, es + installs)
│   └── forensics/               (3: architecture, forensics, recovery)
├── 06_career/
│   ├── roadmap/                 (4: se, sre, dba, languages)
│   ├── legal/                   (2: drm, ip_ownership)
│   └── ai_tools/                (8: kiro_*, ai_patterns, harness, loop)
├── 98_image/                    (루트 유지, 이동 안 함)
├── _reference/                  (유지)
└── _meta/
    ├── README.md
    ├── TODO.md
    ├── CHANGELOG.md
    ├── LICENSE.md
    ├── license_guide.md
    ├── md-style-check.py
    ├── md-link-check.py
    └── strip-footer-md.py
```

#### 마이그레이션 계획

| 단계 | 작업                                     | 검증                 |
|------|------------------------------------------|----------------------|
| 1    | 매핑 테이블 작성 (현재 경로 → 신규 경로) | 파일 수 일치         |
| 2    | 디렉토리 생성                            | tree 확인            |
| 3    | git mv 실행 (history 보존)               | git status clean     |
| 4    | README.md 전면 재작성 (6섹션)            | md-style-check 0건   |
| 5    | 내부 링크 전수 수정 (문서 간 상대경로)   | md-link-check.py 0건 |
| 6    | CHANGELOG.md [3.0.0] 항목 추가           | md-style-check 0건   |
| 7    | _reference/INDEX.md 경로 미사용 확인     | 변경 불필요          |
| 8    | GitHub Actions workflow 경로 확인        | push 후 green        |

#### 주의사항

- git mv 사용 필수 (history 보존)
- 단계별 커밋 (롤백 가능하도록)
- 이전 경로로의 리다이렉트/심볼릭 링크는 만들지 않음
- 98_image/ 루트 유지 (이동 안 함) — 문서 depth 변경 시 상대경로(`../../98_image/`)만 조정
- md-style-check.py 수정 필요:
  - `FILE_SKIP` 5개 항목 경로 패턴 갱신
  - README.md를 `_meta/`로 이동 시 루트 README 제외 로직 조정 검토
- md-link-check.py: 상대경로 기반이므로 수정 불필요
- strip-footer-md.py: 수정 불필요 (경로 하드코딩 없음)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
