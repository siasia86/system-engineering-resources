# TODO

레포 구조 개편 및 잔여 이슈 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 완료 사항](#1-완료-사항) / [2. 잔여 이슈](#2-잔여-이슈) / [3. 구조 개편](#3-구조-개편) |

---

## 1. 완료 사항

- ✅ 다이어그램 한글→영문 (CHANGELOG [2.3.0] 참조)
- ✅ 시니어급 문서 15개 작성 완료 (§4 전체, CHANGELOG [2.3.0] 참조)
- ✅ `00_readme.md/` 삭제
- ✅ `90_DELETE/` 삭제

---

## 2. 잔여 이슈

| 파일                                                     | 이슈 유형       | 설명                              |
|----------------------------------------------------------|-----------------|-----------------------------------|
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | _reference 규칙 | frontmatter 없음 (FILE_SKIP 예외) |

### 검사 예외 파일

| 파일                                                     | 사유                                   |
|----------------------------------------------------------|----------------------------------------|
| `02_basic_linux/vim_airline.md`                          | 외부 프로젝트(vim-airline) README 원본 |
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | Kiro CLI 문서 (다이어그램 한글 의도적) |

---

## 3. 구조 개편

### 목표 구조 (안 C: 역할 x 단계 하이브리드)

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
├── 99_archive/                  (.gitignore, GitHub 미push)
│   ├── 01_sjyun/                (기존 33_sjyun_32_readme.md)
│   ├── 02_siasia/               (기존 51_siasia)
│   └── 03_aws_jobs/             (기존 99_ETC)
├── _reference/                  (유지)
├── .github/                     (유지)
├── README.md                    (루트 유지)
├── TODO.md                      (루트 유지)
├── CHANGELOG.md                 (루트 유지)
├── LICENSE / LICENSE.md         (루트 유지)
├── license_guide.md             (루트 유지)
├── md-style-check.py            (루트 유지)
├── md-link-check.py             (루트 유지)
└── strip-footer-md.py           (루트 유지)
```

### 마이그레이션 계획

| 단계 | 작업                                     | 검증                 |
|------|------------------------------------------|----------------------|
| 1    | 매핑 테이블 작성 (현재 경로 → 신규 경로) | 파일 수 일치         |
| 2    | 디렉토리 생성                            | tree 확인            |
| 3    | git mv 실행 (history 보존)               | git status clean     |
| 4    | README.md 전면 재작성 (6섹션, 루트 유지) | md-style-check 0건   |
| 5    | 내부 링크 전수 수정 (문서 간 상대경로)   | md-link-check.py 0건 |
| 6    | CHANGELOG.md [3.0.0] 항목 추가           | md-style-check 0건   |
| 7    | _reference/INDEX.md 경로 미사용 확인     | 변경 불필요          |
| 8    | GitHub Actions workflow 경로 확인        | push 후 green        |

### 스크립트/설정 수정 사항

| 대상                                  | 수정 내용                                                                                      |
|---------------------------------------|------------------------------------------------------------------------------------------------|
| md-style-check.py                     | `FILE_SKIP` 5개 항목 경로 패턴 갱신                                                            |
| .gitignore                            | `51_siasia/`, `33_sjyun_32_readme.md/`, `#00_readme.md/`, `#99_ETC/` 제거 → `99_archive/` 추가 |
| ~/.kiro/skills/testing-guide/SKILL.md | `05_computer_science/02_testing/` → `01_fundamentals/cs/testing/`                              |
| ~/.kiro/markdown/STYLE.md L466        | `../05_computer_science/TCP_state.md` → `../01_fundamentals/networking/TCP_state.md`           |

### 수정 불필요 확인

| 대상                               | 이유                            |
|------------------------------------|---------------------------------|
| md-link-check.py                   | 상대경로 기반 동작              |
| strip-footer-md.py                 | 경로 하드코딩 없음              |
| md-style-check.py README 제외 로직 | README.md 루트 유지             |
| ~/.kiro/agents/*.json              | `_reference/INDEX.md` 루트 유지 |
| ~/.kiro/prompts/*.md               | 경로 참조 없음                  |
| _reference/                        | 루트 유지, 내부 경로 참조 없음  |

### 주의사항

- git mv 사용 필수 (history 보존)
- 단계별 커밋 (롤백 가능하도록)
- 이전 경로로의 리다이렉트/심볼릭 링크는 만들지 않음
- 98_image/ 루트 유지 (이동 안 함) — 문서 depth 변경 시 상대경로만 조정
- `__pycache__/` — 마이그레이션 전 삭제 (자동 재생성)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
