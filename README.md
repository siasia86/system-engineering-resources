# 시스템 엔지니어링 학습 자료 모음

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Linux, 네트워크, 보안, 데이터베이스, 프로그래밍 등 시스템 엔지니어링 관련 학습 자료 저장소.

## 목차

| 단계 | 섹션 |
|------|------|
| 기초 | [1. 설치](#1-설치) / [2. 기본 Linux](#2-기본-linux) / [3. 고급 Linux](#3-고급-linux) |
| 실무 | [4. 시스템 엔지니어링](#4-시스템-엔지니어링) / [5. 컴퓨터 과학](#5-컴퓨터-과학) / [6. 보안](#6-보안) |
| 도구 | [7. 오픈소스](#7-오픈소스) / [8. 디버깅](#8-linux-디버깅) / [9. 데이터베이스](#9-데이터베이스) / [10. NoSQL](#10-nosql) |
| 언어 | [11. Python](#11-python) / [12. 기술 스택](#12-기술-스택) |
| 부록 | [추천 학습 순서](#추천-학습-순서) |

---

## 1. 설치

설치 및 환경 구성 가이드.

| 문서 | 설명 |
|------|------|
| [Ansible 설치 및 팀 운영](01_install/ansible_install_and_team_operation.md) | Ansible 설치, AWX, 팀 운영 가이드 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 기본 Linux

자주 사용하는 Linux 명령어 및 스크립팅.

| 문서 | 설명 |
|------|------|
| [Bash 수학 연산](02_basic_linux/bash_math.md) | 산술 연산, bc, awk |
| [Bash trap 가이드](02_basic_linux/bash_trap_complete_guide.md) | 시그널 처리, 정리 작업 |
| [리다이렉션](02_basic_linux/redirection.md) | stdin/stdout/stderr, 파이프 |
| [Root 패스워드 복구](02_basic_linux/root_password_recovery.md) | 복구 모드, single user mode |
| [Shell 인터랙티브 모드](02_basic_linux/shell_interactive_mode.md) | interactive/non-interactive 차이 |
| [Vim 사용법](02_basic_linux/vim.md) | 기본 명령어, 모드, 설정 |
| [vim-airline](02_basic_linux/vim_airline.md) | 상태바 플러그인 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고급 Linux

고급 Linux 시스템 관리 및 성능 분석.

| 문서 | 설명 |
|------|------|
| [bpftrace](03_advanced_linux/bpftrace.md) | eBPF 기반 동적 추적, 커널 분석 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 시스템 엔지니어링

SE/SRE 로드맵, 실무 운영, 도구 비교, AI 활용.

| 문서 | 설명 |
|------|------|
| [SE 로드맵](04_system_engineer/se_roadmap.md) | 시스템 엔지니어 커리어 경로 |
| [SRE 로드맵](04_system_engineer/sre_roadmap.md) | Site Reliability Engineer 경로 |
| [SE 로드맵 - 언어](04_system_engineer/se_complete_roadmap_programming_languages.md) | 언어별 학습 로드맵 |
| [언어 비교](04_system_engineer/c_cpp_csharp_go_python_bash_comparison.md) | C/C++/C#/Go/Python/Bash 비교 |
| [게임 인프라 KPI](04_system_engineer/game-infra-kpi-presentation.md) | 인프라 운영 핵심 지표 |
| [리소스 모니터링](04_system_engineer/resource_utilization_monitoring.md) | CPU/메모리/디스크/네트워크 |
| [백업 도구 비교](04_system_engineer/backup_tools_comparison.md) | rsync, Bacula, Amanda 등 |
| [인프라 Monorepo](04_system_engineer/infra_monorepo_and_boilerplate.md) | 모노레포 구조, 보일러플레이트 |
| [ASN 및 DDoS 대응](04_system_engineer/asn_and_cloudflare_ddos.md) | ASN 운영, Cloudflare DDoS |
| [CDN/Proxy/Origin IP](04_system_engineer/cdn-proxy-origin-ip.md) | CDN 구조, Origin IP 보호 |
| [ADR 가이드](04_system_engineer/adr_guide.md) | Architecture Decision Record |
| [AI 개발 요청 템플릿](04_system_engineer/ai_development_request_template.md) | AI 활용 개발 요청 양식 |
| [AI Markdown 패턴](04_system_engineer/ai_markdown_design_patterns.md) | AI 에이전트용 문서 패턴 |
| [Kiro CLI 레퍼런스](04_system_engineer/kiro_cli_command_reference.md) | Kiro CLI 명령어 전체 정리 |
| [Kiro 모델 가이드](04_system_engineer/kiro_model_guide.md) | 모델 선택 기준 |
| [LSP 가이드](04_system_engineer/lsp-guide.md) | Language Server Protocol |
| [S3 Gateway Endpoint](04_system_engineer/s3_gateway_endpoint_cross_account.md) | 크로스 계정 S3 접근 |
| [VPC Peering](04_system_engineer/vpc_peering_inter_region_guide.md) | Inter-Region VPC Peering |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 컴퓨터 과학

네트워크 프로토콜, CPU 아키텍처, 자료구조.

| 문서 | 설명 |
|------|------|
| [IPv4 주소 체계](05_computer_science/ipv4_addressing_guide.md) | 서브넷, CIDR, AWS VPC |
| [IPv6 주소 체계](05_computer_science/ipv6_addressing_guide.md) | 주소 구조, 표기법, SLAAC |
| [TCP 상태 전이](05_computer_science/TCP_state.md) | 3/4-Way Handshake, TIME_WAIT |
| [패킷 분석](05_computer_science/packet_analysis.md) | IP/TCP/UDP 헤더, PROXY Protocol |
| [네트워크 헤더](05_computer_science/network_headers.md) | Ethernet, ARP, DNS, TLS, QUIC |
| [HTTP 메서드](05_computer_science/http_methods.md) | GET/POST/PUT/DELETE/PATCH |
| [tcpdump 예제](05_computer_science/tcpdump_examples.md) | 패킷 캡처 실전 예제 |
| [Switch VLAN Mode](05_computer_science/switch_vlan_mode.md) | Access/Trunk/Dynamic, VLAN Hopping |
| [CPU CISC vs RISC](05_computer_science/cpu_cisc_risc.md) | 명령어 집합 아키텍처 비교 |
| [자료구조](05_computer_science/data-structures/) | Array, Stack, Queue, Tree, Graph 등 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 보안

시스템 보안 및 DDoS 방어.

| 문서 | 설명 |
|------|------|
| [DDoS 방어 아키텍처](06_security/01_ddos_defense_architecture.md) | 계층별 방어 전략 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 오픈소스

컨테이너, 자동화, 오픈소스 도구 활용.

| 문서 | 설명 |
|------|------|
| [Docker & Docker Compose](07_opensource/01_docker_docker_compose_cheatsheet.md) | 명령어 치트시트 |
| [n8n Docker Compose](07_opensource/02_n8n_docker_cheatsheet.md) | n8n + MySQL 구성 |
| [컨테이너 아키텍처](07_opensource/03_container_architecture.md) | Namespace, Cgroup, OCI |
| [Percona XtraBackup](07_opensource/04_percona-xtrabackup-guide.md) | MySQL 온라인 백업 |
| [Ansible vs Jenkins](07_opensource/ansible_vs_jenkins.md) | 자동화 도구 비교 |

[⬆ 목차로 돌아가기](#목차)

---

## 8. Linux 디버깅

Linux 시스템 디버깅 및 성능 분석 도구.

| 문서 | 설명 |
|------|------|
| [strace](08_debugging_linux/strace.md) | 시스템 콜 추적 |
| [ltrace](08_debugging_linux/ltrace.md) | 라이브러리 함수 추적 |
| [gdb](08_debugging_linux/gdb.md) | GNU 디버거 |
| [perf](08_debugging_linux/perf.md) | 성능 분석 |
| [valgrind](08_debugging_linux/valgrind.md) | 메모리 디버깅 |
| [lsof](08_debugging_linux/lsof.md) | 열린 파일 확인 |
| [iotop](08_debugging_linux/iotop.md) | I/O 모니터링 |
| [tcpdump](08_debugging_linux/tcpdump.md) | 네트워크 패킷 캡처 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 데이터베이스

RDBMS 설계, 쿼리 최적화, 운영.

| 문서 | 설명 |
|------|------|
| [정규화](09_database/rdbms_normalization.md) | 1NF~BCNF, 반정규화 |
| [JOIN](09_database/rdbms_join.md) | JOIN 종류, 실행 방식 |
| [Index](09_database/rdbms_index.md) | B-Tree, 복합/커버링 인덱스 |
| [EXPLAIN](09_database/rdbms_explain.md) | 실행 계획 분석, 슬로우 쿼리 |
| [Transaction](09_database/rdbms_transaction.md) | ACID, 격리 수준, MVCC |
| [Lock](09_database/rdbms_lock.md) | Row/Gap Lock, 데드락 |
| [View](09_database/rdbms_view.md) | View, Materialized View |
| [Procedure](09_database/rdbms_procedure.md) | 저장 프로시저, 커서 |
| [Replication](09_database/rdbms_replication.md) | binlog, GTID, RDS Read Replica |
| [Partition](09_database/rdbms_partition.md) | Range/List/Hash 파티셔닝 |
| [Schema Migration](09_database/rdbms_schema_migration.md) | pt-osc, gh-ost, 무중단 변경 |

[⬆ 목차로 돌아가기](#목차)

---

## 10. NoSQL

MongoDB, Redis, Elasticsearch.

| 문서 | 설명 |
|------|------|
| [MongoDB](10_nosql/nosql_mongodb.md) | Document DB, Aggregation Pipeline |
| [Redis](10_nosql/nosql_redis.md) | 인메모리, 캐시, 분산 락, 랭킹 |
| [Elasticsearch](10_nosql/nosql_elasticsearch.md) | 전문 검색, 로그 분석, ELK |

[⬆ 목차로 돌아가기](#목차)

---

## 11. Python

Python 프로그래밍 가이드.

| 문서 | 설명 |
|------|------|
| [클래스](11_python/python_class.md) | 클래스 기초 |
| [클래스 구성 요소](11_python/python_class_components.md) | 속성, 메서드, 프로퍼티 |
| [상속](11_python/python_inheritance.md) | 단일/다중 상속, MRO |
| [함수](11_python/python_functions.md) | 정의, 인자, 클로저 |
| [제어문](11_python/python_control_flow.md) | if/for/while/match |
| [예외 처리](11_python/python_exceptions.md) | try/except, 커스텀 예외 |
| [데코레이터](11_python/python_decorators.md) | functools, 클래스 데코레이터 |
| [제너레이터](11_python/python_generators.md) | yield, 이터레이터 |
| [컴프리헨션](11_python/python_comprehensions.md) | list/dict/set/generator |
| [컨텍스트 매니저](11_python/python_context_managers.md) | with, contextlib |
| [파일 입출력](11_python/python_file_io.md) | open, pathlib, shutil |
| [자료구조](11_python/python_data_structures.md) | list, dict, set, tuple |
| [패키지](11_python/python_packages.md) | 모듈, 패키지, pip |
| [가상환경](11_python/python_virtual_env.md) | venv, pip, requirements |
| [로깅](11_python/python_logging.md) | logging 모듈, 핸들러 |
| [정규표현식](11_python/python_regex.md) | re 모듈, 패턴 |
| [문자열](11_python/python_string.md) | 포맷, 메서드, f-string |
| [JSON/YAML](11_python/python_json_yaml.md) | 직렬화/역직렬화 |
| [subprocess](11_python/python_subprocess.md) | 외부 명령 실행 |
| [argparse](11_python/python_argparse.md) | CLI 도구 제작 |
| [os/pathlib](11_python/python_os_pathlib.md) | 파일/디렉토리 조작 |
| [모듈 속성](11_python/python_magic_attributes.md) | `__name__`, `__file__` 등 |
| [print()](11_python/python_print.md) | 출력 포맷, sep/end |

[⬆ 목차로 돌아가기](#목차)

---

## 12. 기술 스택

주요 인프라/DevOps 도구 가이드.

| 문서 | 설명 |
|------|------|
| [Ansible 기초](12_tech_stack/ansible_basic_guide.md) | 인벤토리, 플레이북, 롤 |
| [Ansible Vault](12_tech_stack/ansible_vault.md) | 시크릿 암호화 |
| [Jenkins Pipeline](12_tech_stack/jenkins_pipeline.md) | Declarative/Scripted Pipeline |
| [Apache Airflow](12_tech_stack/airflow.md) | DAG, Operator, 스케줄링 |
| [AWS Step Functions](12_tech_stack/aws_step_functions.md) | 상태 머신, 워크플로우 |
| [Git 실무 가이드](12_tech_stack/git_guide.md) | diff, log, fetch, stash, rebase |

[⬆ 목차로 돌아가기](#목차)

---

## 추천 학습 순서

```
초급 (Linux 입문)
  02_basic_linux → 05_computer_science (IPv4/TCP) → 07_opensource (Docker)

중급 (시스템 관리)
  08_debugging_linux → 09_database (Index/Transaction) → 12_tech_stack

고급 (성능 최적화 & 보안)
  03_advanced_linux → 06_security → 09_database (Replication/Partition)
  → 10_nosql → 04_system_engineer (SE/SRE 로드맵)
```

---

## 참고 자료

- roadmap.sh: [roadmap.sh](https://roadmap.sh/)
- Google SRE Book: [sre.google](https://sre.google/sre-book/table-of-contents/)
- Linux Documentation Project: [tldp.org](https://tldp.org/)

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

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
