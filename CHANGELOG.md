# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

[⬆ 목차로 돌아가기](#목차)

---

## [3.0.0] - 2026-07-07

### Changed

#### 레포 구조 전면 개편 (BREAKING CHANGE)

기존 13개 최상위 디렉토리 → 6개 섹션 기반 구조로 전환.

| 신규 디렉토리        | 내용                                                                    | 통합 출처           |
|----------------------|-------------------------------------------------------------------------|---------------------|
| `01_fundamentals/`   | linux, networking, cs, programming                                      | 02, 03, 05, 08, 11  |
| `02_infrastructure/` | containers, cicd, iac, monitoring, cloud_aws, data_pipeline, web_server | 01, 07, 12, 13      |
| `03_engineering/`    | reliability, delivery, organization, cost                               | 04/02_operations    |
| `04_security/`       | hardening, cloud, cve, web_cwe                                          | 06                  |
| `05_database/`       | rdbms, operations, nosql, forensics                                     | 09, 10              |
| `06_career/`         | roadmap, legal, ai_tools                                                | 04/01, 04/04, 04/05 |

- git mv 200+ 파일 (history 보존)
- README.md 전면 재작성 (6섹션 레벨 기반 탐색)
- 내부 링크 전수 수정 (md-link-check 0건)
- md-style-check.py FILE_SKIP + EXCLUDE_DIRS 경로 갱신
- md-style-check.py 박스 상/하단 공백 혼입 검출 규칙 추가
- .gitignore: `99_archive/` 통합 (기존 51_siasia, 33_sjyun, 99_ETC 제거)
- 기존 디렉토리 README.md 12개 삭제
- `00_readme.md/`, `90_DELETE/` 삭제

### Removed

- `00_readme.md/` — Kiro 설정 복사본 (불필요)
- `90_DELETE/` — deprecated 파일 2개 (CONTRIBUTING, GITHUB_UPLOAD_GUIDE)
- 기존 디렉토리 README.md 12개 (01_install ~ 12_tech_stack)

## [2.3.0] - 2026-07-07

### Added

#### 12_tech_stack — 신규 문서 3개
- `harness_engineering.md` — AI Harness Engineering (에이전트 환경 설계)
- `vpn_protocol.md` (05_computer_science) — VPN 프로토콜 비교 (PPTP~WireGuard, RFC 대조 검증)
- `zabbix_vs_prometheus.md` — 모니터링 도구 비교 (아키텍처, 수집, 알림, 확장성)

#### _reference — 신규 참조 파일
- `vpn_protocol_official_notes.md` — VPN RFC 기반 참조 노트
- INDEX.md 갱신 (VPN Protocol 항목 추가, 알파벳순 정렬)

#### 03_advanced_linux — 신규 문서 6개
- `ipc.md` — 프로세스 간 통신 (Pipe, Socket, Shared Memory, Message Queue)
- `linux_virtual_fs.md` — VFS 추상화 계층, inode, dentry, superblock
- `namespace.md` — Linux Namespace 7종 (pid, net, mnt, uts, ipc, user, cgroup)
- `netfilter_tc.md` — Netfilter 훅 체인, iptables/nftables, TC 트래픽 제어
- `scheduler.md` — CFS, RT, Deadline 스케줄러, nice, cgroup CPU
- `virtual_memory.md` — 페이지 테이블, TLB, Swap, OOM Killer, NUMA

#### 04_system_engineer/04_ai — 신규 문서 3개
- `kiro_agent_lock.md` — Kiro 에이전트 동시 실행 방지
- `kiro_model_guide.md` — Kiro 모델 선택 가이드
- `kiro_setup_guide.md` — Kiro CLI 초기 설정

#### 05_computer_science — 신규 문서 1개
- `switch_vlan_mode.md` — Access/Trunk/Hybrid 모드, 802.1Q 태깅

#### 06_security — 신규 문서 11개
- `network_attack_glossary.md` — 네트워크 공격 용어 사전 (DDoS, MITM, ARP Spoofing 등)
- `01_cve/` 서브디렉토리 생성 — CVE 5건 + LPE 공격 시나리오
  - `cve_2026_31431_copy_fail.md`, `cve_2026_43284_dirty_frag.md`
  - `cve_2026_43500_dirty_frag.md`, `cve_2026_43503_dirty_clone.md`
  - `cve_2026_46300_fragnesia.md`, `cve_2026_lpe_attack_scenarios.md`
- `02_web_cwe/` 서브디렉토리 생성 — CWE 4건
  - `cwe_022_path_traversal.md`, `cwe_078_command_injection.md`
  - `cwe_200_info_disclosure.md`, `cwe_434_file_upload.md`

#### 08_debugging_linux — 신규 문서 1개
- `oom_hang.md` — OOM Killer 분석, 행 진단, kdump, sysrq

#### 09_database — 신규 문서 7개
- `dbtrail/` 서브디렉토리 생성 — DB 포렌식/복구
  - `architecture.md`, `forensics.md`, `recovery_guide.md`
- `rdbms_index.md`, `rdbms_server_config.md`, `rdbms_slow_query.md`, `rdbms_tuning.md`

#### 11_python — 신규 문서 2개
- `python_file_io.md` — 파일 읽기/쓰기, encoding, pathlib, atomic write
- `python_generators.md` — yield, send, generator expression, itertools

#### 12_tech_stack — 신규 문서 4개
- `01_data_pipeline/` 서브디렉토리 생성
  - `game_log_pipeline.md`, `log_aggregation_100gb.md`, `log_aggregation_100tb.md`
- `github_cli.md` — gh CLI 명령어, PR/Issue 자동화
- `gstack.md` — 게임 인프라 기술 스택 조합
- `loop_engineering.md` — AI 에이전트 루프 설계

#### 13_iac — 신규 문서 1개
- `01_ansible/molecule.md` — Ansible 역할 테스트 프레임워크

#### _reference — 신규 참조 파일 4개
- `cve_security_official_notes.md` — CVE/CWE 공식 출처 참조
- `linux_kernel_official_notes.md` — 커널 릴리즈/기능 참조
- `networking_official_notes.md` — 네트워크 프로토콜 RFC 참조
- `postgresql_official_notes.md` — PostgreSQL 공식 문서 참조

#### 04_system_engineer/02_operations — 시니어급 문서 8개 (신규)
- `incident_management.md` — 장애 등급 분류, IC 역할, 에스컬레이션, State Document
- `slo_error_budget.md` — SLI/SLO/SLA 정의, Error Budget 운영, Burn Rate Alert, OpenSLO
- `capacity_planning.md` — 트래픽 예측, 리소스 산정, Headroom 설계, Load Testing
- `zero_downtime_migration.md` — Expand-Contract, Dual Write, CDC, Canary 전환, 롤백 전략
- `change_management.md` — Standard/Normal/Emergency 변경 등급, CAB, 배포 윈도우
- `postmortem_framework.md` — 5 Whys, Blameless Culture, Action Items 추적, 리뷰 프로세스
- `chaos_engineering.md` — 가설 기반 실험, 폭발 반경 제어, Game Day, 성숙도 모델
- `multi_region_architecture.md` — Active-Active/Passive, RPO/RTO 설계, Failover/Failback
- `platform_engineering.md` — IDP 설계, Golden Path, CNCF Platform WP 기반 성숙도 모델
- `oncall_design.md` — 로테이션, 25% 규칙, 런북, 에스컬레이션, 번아웃 방지
- `team_topology.md` — 4가지 팀 유형, 3가지 상호작용 모드, Conway 법칙 역전
- `tech_debt_management.md` — Fowler Quadrant, 측정 지표, 상환 우선순위 매트릭스
- `vendor_evaluation.md` — PoC 설계, TCO 3년 산정, Lock-in 평가, Weighted Scoring
- `legacy_modernization.md` — Strangler Fig, 6R 전략, 데이터 이중 쓰기, Shadow Mode

#### 12_tech_stack — 신규 문서 1개
- `cloud_cost_optimization.md` — FinOps 6 Principles, RI/SP 전략, Spot 활용, Right-sizing

#### _reference — platform_engineering_official_notes.md 신규
- CNCF Platforms White Paper + Platform Maturity Model 공식 출처 통합

#### _reference — sre_operations_official_notes.md 신규
- Google SRE Book/Workbook, PagerDuty, OpenSLO, ITIL v4, gh-ost, pt-osc 공식 출처 통합

#### .kiro/prompts — fact-check.md 신규
- 기술 사실 검증 전용 프롬프트 (RFC 대조, 할루시네이션 탐지, 비검증 수치 제거)
- md-review.md에서 사실 검증 역할 분리

#### 04_system_engineer/02_operations — 신규 문서 2개
- `s3_object_lock.md` — S3 Object Lock (WORM, Governance/Compliance, 운영)
- `s3_backup_tips.md` — EC2→S3 백업 운영 팁 (비용, 성능, 무결성, DB 백업)

#### 99_ETC/01_AWS_jobs — 신규 문서 1개
- `s3_cross_account_backup.md` — STS AssumeRole Cross-account 백업 (웹+CLI)

#### 01_install — 업데이트
- `postgresql_install.md` — PG18 추가, ICU provider 상세 설명, 최신 마이너 버전 반영

### Changed

#### 12_tech_stack
- `aws_network_firewall.md` — Resource ID placeholder 표준화 (보안 검사 통과)

#### 12_tech_stack
- `harness.md` → `harness_inc.md` 이름 변경 (CI/CD 플랫폼 명시)

#### md-style-check.py
- `_reference` 디렉토리 검사 제외 추가
- `kiro_cli_command_reference.md` FILE_SKIP diagram-kr 예외 추가

#### .kiro/prompts/md-review.md
- `content(tech error)` 제거 → `content(typo,example mismatch,duplication,broken sentence)`
- `@fact-check` 분리 안내 주석 추가
- diagram 항목에 `arrow flow direction logical` 추가

#### 스크립트
- `md-style-check.py` — `_reference` 제외, FILE_SKIP diagram-kr 추가, `--no-*` 옵션 11개
- `md-link-check.py` — 코드블록 파싱 수정 (라인 토글 방식)
- `strip-footer-md.py` — 신규 유틸리티 (푸터 일괄 제거 스크립트)

#### .kiro/skills/work-rules/SKILL.md
- §15 Storage targets에 추론/기억 기반 작성 금지 규칙 상단 배치

### Fixed

#### 다이어그램 한글→영문 (8개 파일 완료)
- `asn_and_cloudflare_ddos.md`, `infra_monorepo_and_boilerplate.md`
- `s3_gateway_endpoint_cross_account.md`, `vpc_peering_inter_region_guide.md`
- `devops_toolchain.md`, `sre_roadmap.md`
- `ai_development_request_template.md`, `ai_markdown_design_patterns.md`

#### 다이어그램 화살표 수정
- `ai_development_request_template.md` — `------->` → `──────>` (Box Drawing 문자)
- `vpn_protocol.md` — 다이어그램 `│`/`v` 위치, 박스 `┐`/`┘` 닫힘, Transport/Tunnel Mode 박스 수정

#### vpn_protocol.md 사실 검증 수정
- 세대 타임라인: OpenVPN 2012→2001, IKEv2 순서 교체
- IPsec AES-GCM-16: SHOULD+ → MUST (RFC 8221)
- OpenVPN TLS: "1.3 기본" → "1.2/1.3 (최상위 지원 버전 자동 선택)"
- L2TP/IPsec 오버헤드: "~20% 증가" → 출처 없는 수치 제거

[⬆ 목차로 돌아가기](#목차)

---

## [2.2.1] - 2026-06-21

### Fixed

#### 01_install — 표 정렬 수정 (5개 파일)
- `nginx_install.md`, `apache_install.md`, `docker_install_and_compose.md`, `ansible_install_and_team_operation.md`, `elasticsearch_install.md`
- 표 내부 파이프(`|`) 미이스케이프로 인한 열 깨짐 수정 (`\|` 이스케이프 적용)
- 불필요한 빈 열 제거 및 display width 기준 패딩 재정렬

#### 02_basic_linux — 표 정렬 + 다이어그램 수정 (4개 파일)
- `bash_file_redirection.md` — 표 패딩 수정, 다이어그램 행 폭 통일, 다이어그램 내부 한글→영문
- `bash_math.md` — 표 열 너비 재정렬 (`\|\|` 이스케이프 포함)
- `root_password_recovery.md` — 표 열 너비 재정렬
- `shell_interactive_mode.md` — 표 전체 자동 정렬

#### 04_system_engineer — 표 정렬 + 구조 수정 (22개 파일)
- 전체 표 display width 기준 자동 정렬
- `kiro_cli_command_reference.md` — 파이프 이스케이프 (`--wrap <always \| never>`)
- `game_infra_kpi_presentation.md` — H1 중복 수정 (`# ubuntu-24.04` → `## ubuntu-24.04`)
- `infra_monorepo_and_boilerplate.md` — 코드블록 시작 태그 누락 수정
- `ai_markdown_design_patterns.md` — 이모지 뒤 공백 추가
- `vpc_peering_inter_region_guide.md` — 반말체→합니다체 수정 (2건)
- 다이어그램 행 폭 패딩 통일

#### 05_computer_science — 표 정렬 + 다이어그램 수정 (19개 파일)
- 전체 표 display width 기준 자동 정렬
- `equivalence_partitioning.md` — 코드블록 닫힘 누락 수정
- `ipv4_addressing_guide.md`, `array.md`, `linked_list.md`, `queue.md`, `integration_testing.md` — 다이어그램 내부 한글→영문
- 다이어그램 행 폭 패딩 통일

---

## [2.2.0] - 2026-05-04

### Added

#### 01_install — 신규 설치 가이드 13개
- `mysql_install.md` — Ubuntu/RHEL 설치, 초기 보안 설정, my.cnf, 복제 계정, 기본 사용법
- `postgresql_install.md` — Ubuntu/RHEL 설치, pg_hba.conf, LOCALE 'C.UTF-8' 이슈 대응, 기본 사용법
- `docker_install_and_compose.md` — Ubuntu/RHEL 설치, daemon.json, Compose 운영, 실무 팁 7가지
- `kubernetes_install.md` — k3s(단일 명령), kubeadm(멀티 노드), kubectl, Deployment/Service YAML
- `nginx_install.md` — 설치, 가상 호스트, 리버스 프록시, upstream LB, SSL/Let's Encrypt
- `apache_install.md` — 설치, MPM(prefork/worker/event) 상세 비교 및 튜닝, SSL
- `redis_install.md` — 설치, requirepass, 위험 명령 비활성화, 자료형 CRUD, Slow Log
- `prometheus_grafana_install.md` — 바이너리/APT 설치, Node Exporter, PromQL, 알림 규칙, Compose
- `elasticsearch_install.md` — ELK 구조, 8.x 보안 설정, ILM, Compose
- `haproxy_install.md` — L4/L7 LB, upstream 알고리즘, SSL 터미네이션, 소켓 런타임 제어
- `vault_install.md` — KV/Database 시크릿 엔진, AppRole, Auto Unseal(AWS KMS), 감사 로그
- `mongodb_install.md` — 8.0 설치, 인증 활성화, CRUD, 인덱스, 프로파일링, 백업
- `jenkins_install.md` — JDK 21, Declarative Pipeline, Shared Library, Compose

#### 09_database — rdbms_replication.md 개선
- MySQL 복제 전체 설정 절차 추가 (Primary 계정 생성, mysqldump 초기 동기화, binlog position 기반 설정)
- 반동기 복제 섹션 추가 (플러그인 설치, ACK 흐름, 상태 확인)
- Failover 섹션 추가 (전통/GTID 수동 Failover, MHA·Orchestrator 자동화 도구 비교)
- 복제 필터링 섹션 추가 (binlog_do_db, replicate_do_table 등)
- PostgreSQL Streaming Replication 전체 설정 추가 (pg_basebackup, pg_stat_replication, 동기 복제, Failover)
- MySQL RDS vs Aurora 비교표 추가

### Changed
- `01_install/README.md` 신규 생성 — 14개 문서 목차
- `09_database/README.md` 목차에 설치 문서 링크 추가 (mysql_install, postgresql_install)
- `README.md` `01_install` 섹션 표에 신규 13개 파일 추가, 문서 트리 업데이트, 마지막 업데이트 갱신
- `README.md` 문서 트리 링크 텍스트 오류 6건 수정 (하이픈 → 언더스코어)
- `/home/sjyun/.kiro/markdown/STYLE.md` 규칙 10 보강 — 반말체 종결어미 금지 패턴 명시 (`~이다.` `~한다.` 등)

### Fixed
- `mysql_install.md` `mysqldump` 명령에 `sudo` 누락 수정 (Ubuntu auth_socket 환경)
- `postgresql_install.md` DB 생성 구문 수정 (`LC_COLLATE 'en_US.UTF-8'` → `LOCALE 'C.UTF-8'`, PostgreSQL 17 + Ubuntu 24.04 ICU 환경)
- `postgresql_install.md` 계정명 대소문자 수정 (`Secureuser123` → `secureuser123`, PostgreSQL 소문자 저장 규칙)
- 전체 `.md` 반말체 종결어미 수정 — `01_install` 8개 파일 19건, `09_database` 8개 파일 30건, 기타 12개 파일 33건 (총 82건)
  - `~이다.` `~한다.` `~된다.` `~있다.` `~없다.` `~않는다.` `~아니다.` → 합니다체 통일

[⬆ 목차로 돌아가기](#목차)

---

## [2.1.0] - 2026-05-01

### Added
- `12_tech_stack/README.md` 신규 생성 — 6개 문서 링크 표, 참고 자료, 푸터
- `10_nosql/README.md` 문서 목록 섹션 추가 (Redis, MongoDB, Elasticsearch 링크 표)
- `11_python/README.md` 목차 섹션 추가
- `06_security/README.md` 목차 섹션 추가
- `02_basic_linux/README.md` 목차 섹션 추가, `shell_interactive_mode.md` 문서 목록 추가
- `09_database/rdbms_partition.md` PostgreSQL Hash 파티셔닝 예제 추가

### Changed
- `07_opensource/` 파일명 앞 숫자 접두사 제거 (`01_docker_...` → `docker_...` 등 4개)
- `08_debugging_linux/` 내부 공유 자료 헤더 제거 (strace, ltrace), 문서 변경 이력/관리자 섹션 제거
- `04_system_engineer/01_roadmap/sre_roadmap.md` 내부 공유 자료 헤더, 실명, 작성자 노트 제거
- 전체 참고 자료 별점 STYLE.md 기준 재적용
  - 공식 문서: ★★★☆☆, 서드파티/블로그: ★★☆☆☆, seminal 도서/PEP: ★★★★☆
  - Use The Index Luke: ★★☆☆☆ (서드파티)
- `09_database/` 다이어그램 내 한글 영문화 (4개 파일)
- `07_opensource/container_architecture.md` 다이어그램 내 한글 영문화, 중복 참고 자료 제거
- `06_security/01_ddos_defense_architecture.md` 다이어그램 내 한글 영문화, 참고 자료 형식 수정
- `02_basic_linux/` 다이어그램 내 한글 영문화 (redirection, vim, shell_interactive_mode)
- `10_nosql/nosql_elasticsearch.md` REST API 코드블록 `bash` 태그 제거, JSON 내 `#` 주석 → `//`
- `n8n_docker_cheatsheet.md` 자격증명 실제값 → 표준 플레이스홀더 적용
- `12_tech_stack/git_guide.md` bare URL → 마크다운 형식 + 별점 추가
- `README.md` `07_opensource` 링크 파일명 수정 (접두사 제거 반영), 마지막 업데이트 갱신

### Fixed
- `09_database/rdbms_lock.md` `information_schema.innodb_lock_waits` MySQL 8.0 제거 반영 (8.0+ 쿼리 우선)
- `09_database/rdbms_join.md` INNER JOIN 다이어그램 값 오류 수정 (`│2│3│` → `│1│3│`)
- `09_database/rdbms_replication.md` RDS MySQL Read Replica 최대 수 수정 (5개 → 15개)
- `09_database/rdbms_partition.md` 이벤트 스케줄러 파티션 이름 충돌 수정 (동적 이름 생성으로 변경)
- `09_database/rdbms_procedure.md` `SQL_CALC_FOUND_ROWS` deprecated 주석 추가
- `09_database/rdbms_transaction.md` `FOR UPDATE` 설명 정정 (일반 SELECT는 MVCC로 허용)
- `08_debugging_linux/strace.md` `strace -b` 오류 수정 (strace에 없는 옵션)
- `02_basic_linux/README.md` 리소스 모니터링 링크 경로 수정 (`04_system_engineer/02_operations/` 누락)
- 전체 README.md 링크 유효성 검증 완료 (12개 파일 전체 OK)

[⬆ 목차로 돌아가기](#목차)

---

## [2.0.0] - 2026-04-30

### Added
- `09_database/` 신규 디렉토리 — RDBMS 11개 문서
  (normalization, join, index, explain, transaction, lock, view, procedure, replication, partition, schema_migration)
- `10_nosql/` 신규 디렉토리 — MongoDB, Redis, Elasticsearch
- `04_system_engineer/01_roadmap/` 서브디렉토리 분리 (SE/SRE/DBA 로드맵)
- `04_system_engineer/02_operations/` ~ `05_legal/` 서브디렉토리 분리
- `license_guide.md` 전면 재작성 (라이선스 역사, 이슈, 법적 근거 추가)
- `12_tech_stack/git_guide.md` 신규 — diff/log/fetch/stash/rebase/safe.directory
- `04_system_engineer/05_legal/drm_guide.md` 신규
- `04_system_engineer/05_legal/ip_ownership_guide.md` 신규
- `04_system_engineer/01_roadmap/dba_roadmap.md` 신규
- 루트 README.md 문서 트리 섹션 추가

### Changed
- 전체 .md 푸터 통일 — stars/forks/watchers 배지, 작성일/마지막업데이트 빈줄 규칙
- 전체 참고 자료 별점 추가 (★★☆☆☆ 기본값 기준)
- 전체 목차 표 형식 통일 — H2만 포함, H3 혼입 제거
- `[⬆ 목차로 돌아가기]` 전체 파일 추가
- `05_computer_science/` 참고 자료 목록 형태 변환 (표 → 목록)
- `se_complete_roadmap_programming_languages.md` 제목 수정 ("완전" 제거)

### Fixed
- `packet_analysis.md` 중복 H2 섹션 제거
- `license_guide.md` `## License` H2 20개+ 중복 제거 (코드블록으로 이동)
- 전체 과장 표현 수정 ("최고 성능" → "높은 성능" 등)

[⬆ 목차로 돌아가기](#목차)

---

## [1.1.0] - 2026-03-25

### Added
- `01_install/` 디렉토리 README.md 목차에 추가 (Ansible 기초, 설치 및 팀 운영 가이드)
- GitHub Actions workflow 추가 (`.github/workflows/update-date.yml`)
  - `main` 브랜치 push 시 변경된 README.md의 마지막 업데이트 날짜 자동 갱신

### Changed
- `07_system_engineer/` → `04_system_engineer/`로 번호 변경 (자주 사용하는 디렉토리 우선 배치)
- `04_opensource/` → `07_opensource/`로 번호 변경 (swap)
- `08_debuggin_linux/` → `08_debugging_linux/`로 오타 수정
- README.md 목차 순서를 디렉토리 번호 순으로 재정렬 (1~10번)
- 모든 하위 디렉토리 README.md 푸터 통일 (통계 배지, 마지막 업데이트, 저작권)

### Fixed
- 문서 내 `debuggin_linux` → `debugging_linux` 오타 수정 (6개 파일)
- 문서 내 `07_system_enginner` → `04_system_engineer` 오타 및 경로 수정 (6개 파일)
- 문서 내 `01_debuggin_linux` → `08_debugging_linux` 잘못된 번호 참조 수정

[⬆ 목차로 돌아가기](#목차)

---

## [1.0.0] - 2026-03-11

### Added
- 초기 릴리스
- Linux 디버깅 도구 가이드 (strace, ltrace, gdb, perf, valgrind, lsof, iotop, tcpdump)
- 기본 Linux 명령어 및 스크립팅 가이드
- Bash trap 가이드
- IP 주소 체계 가이드
- 고급 Linux (bpftrace)
- 오픈소스 도구 (Docker, n8n, 컨테이너 아키텍처)
- 컴퓨터 과학 (TCP, 패킷 분석, 네트워크 헤더, HTTP)
- 보안 (DDoS 방어)
- 시스템 엔지니어 로드맵
- 프로그래밍 언어 비교 (C, C++, C#, Go, Python, Bash)
- Python 가이드 (클래스, 로깅, Magic Attributes)
- 라이선스 가이드
- 각 디렉토리별 README.md
- LICENSE.md

### Documentation
- CC BY 4.0 라이선스 적용 (문서)
- MIT License 적용 (코드 예제)

[⬆ 목차로 돌아가기](#목차)

---

## 변경 사항 기록 방법

### 카테고리
- `Added` - 새로운 기능 추가
- `Changed` - 기존 기능 변경
- `Deprecated` - 곧 제거될 기능
- `Removed` - 제거된 기능
- `Fixed` - 버그 수정
- `Security` - 보안 관련 변경

## 참고 자료

- Keep a Changelog: [keepachangelog.com](https://keepachangelog.com/) — ★★☆☆☆
- Semantic Versioning: [semver.org](https://semver.org/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-11

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.
