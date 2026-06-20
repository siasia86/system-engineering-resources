# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

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

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
