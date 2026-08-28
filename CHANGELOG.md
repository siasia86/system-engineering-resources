# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

---

## [Unreleased] - 2026-08-27

### Changed

- `iperf3` 공식 reference와 네트워크 통신 품질 측정 가이드 추가.
- `PLAN.md`에 2026-08-28 local baseline, 외부 의존성, 원격 적용 순서를 정리.
- 첫 test target에 root SSH와 임시 HTTPS artifact를 사용해 `0.3.0 install → 0.3.1 update → 0.3.0 rollback`을 검증. 운영 artifact repository와 일반 사용자 Controller `become`은 미완료로 유지.
- `30_sia-scripts`에 GitHub Actions 검증 workflow와 `v*.*.*` tag 전용 versioned artifact 생성을 추가.
- `30_sia-scripts` release manifest에 source commit provenance와 파일별 SHA-256 검증을 추가.
- `01_fundamentals/linux/neovim_guide.md` 추가 및 Neovim 고유 운영 기능·window 분할·LSP·Tree-sitter·headless 사용법 기록.
- `01_fundamentals/linux/tmux_guide.md` 추가 및 session·window·pane 운영과 Neovim window 분할 차이 기록.
- `01_fundamentals/linux/zoxide_guide.md` 추가 및 설치·shell 초기화·query·database 관리·rollback 절차 기록.
- 30 저장소 CI slice commit `e69bcfb`를 `origin/main`에 push하고 로컬 검증을 완료.
- localhost 임시 HTTPS artifact endpoint에서 `0.3.0 install → 0.3.1 update → 0.3.0 rollback`을 실제 로컬 경로에 적용.
- 로컬 `current -> 0.3.0` baseline, root ownership·permission, 비권한 사용자 쓰기 차단을 확인.
- `30_sia-scripts` 공용 검사기·release artifact·Ansible 배포 구조의 migration 상태를 갱신.
- 오류 fixture 4종과 legacy/common 검사기 반환 코드 대조를 완료.
- 일반 계정 Controller의 사용자 소유 `.venv`에서 Ansible syntax check를 완료.
- 최종 검증이 끝난 `/root/30_sia-scripts` 검증 clone을 사용자 승인으로 삭제. 원격 `main`과 사용자 clone을 기준 상태로 사용.
- `ansible-lint==26.8.0`과 `ansible-core==2.20.5` 조합의 lint 통과를 확인.
- 임시 target에서 release install·update·rollback과 root 소유자·권한·entrypoint 동작을 확인.
- 32 저장소 자체 Markdown style·heading·link 검사, gitleaks, `git diff --check`를 재검증해 통과.
- 일반 계정 Controller의 local `become` probe가 password-required sudoers 정책으로 실패함을 확인하고, root harness 적용과 운영 검증 미완료 상태를 기록.

## [3.11.0] - 2026-08-27

### Added

- 30 generic checker의 `file_skip`·`path_skip` contract와 32 policy profile을 추가하고 style·heading·link·inventory parity를 확인.
- 30·32 검증 script 이관 workflow를 시작하고, parity·config·CI consumer 검증 전까지 32 root script 삭제를 보류.
- 저장소별 규칙 체계 `.governance/`와 [저장소 규칙 우선순위 정책](00_governance/01_repository_governance/governance_precedence.md) 추가.
- governance 개선 항목 관리 문서 `governance_todo.md` 추가.
- 작업 템플릿 6종 추가: TODO, CHANGELOG, README, RUNBOOK, GOVERNANCE, VERIFICATION. 기존 PLAN·ISSUE 템플릿을 포함해 8종이 됩니다.
- 헤딩 구조·목차 앵커 검사기 `md-heading-check.py` 추가 (anchor / number / level / duplicate).
- `md-heading-check.py` 예외 설정 `.md-heading-check.toml` 추가 (파일별 검사 항목 제외 지원).
- `md-heading-check.py` 에 목차 완결성 검사(`toc`) 추가. 본문 H2가 목차에 없으면 검출합니다.
- `md-style-check.py --list-skips` 옵션 추가. 파일별 제외 항목과 사유를 출력하고, 사유가 없는 항목이 있으면 종료 코드 1을 반환합니다.
- 검사 도구 작업의 후속 항목을 정리한 임시 문서 `TODO2.md` 추가.
- 압축 알고리즘 문서 `01_fundamentals/cs/compression_algorithms.md` 추가.
- Zircon Windows 빌드 저장소에 `.governance/GOVERNANCE.md` 적용. `.governance/` 체계의 첫 적용 사례입니다.
- Zircon Windows 빌드 저장소에 구성 README와 DevExpress 의존성 문서 작성.
- Ansible 학습·자동화 저장소에 `.governance/GOVERNANCE.md` 와 `.governance/verification.md` 적용.
- `documentation_policy.md` §3.1 경로·식별자 기록 기준 신설. 환경 종속성을 판단 기준으로 정의.

### Changed

- 헤딩 구조 검사를 CI 필수 검사로 등록.
- 스타일 검사 대상에 `02_kiro/` 미러와 저장소 메타 문서(`CHANGELOG.md`, `LICENSE.md`, `TODO.md`, `license_guide.md`)를 포함 (323개 → 367개).
- `md-style-check.py` 의 파일별 제외 항목을 `(검사 집합, 사유, 재검토 시점)` 구조로 변경. 사유 없는 제외를 남기지 않도록 했습니다.
- 검사 제외 항목 전수 점검. 근거가 사라진 2건 제거, 범위가 과도한 1건 축소, 사유 미확인 6건 해소 (11건 → 9건).
- PLAN·ISSUE 템플릿에 비가역 작업, 임시 조치, 재발 방지 섹션 추가.
- 템플릿 8종의 목차·번호 체계와 민감정보 기록 금지 항목을 통일.
- `README.md` 저장소 profile 설명을 `.governance/` 체계 기준으로 갱신.
- 날짜 갱신 workflow의 커밋 생성 job을 단일 branch로 제한.
- 날짜 갱신 workflow에서 `02_kiro/` 미러를 제외. 봇 커밋과 동기화가 서로 덮어쓰던 문제 해결.
- Kiro 미러 allowlist에서 원문 보존본과 미러 전용 파일을 제외.
- `documentation_policy.md`와 `governance_precedence.md`의 역할을 상호 참조로 명확히 함.
- `skip_checks`를 저장소 전체 검사 예외의 실행 설정으로 정의하고, `.governance/`에 사유·범위·재검토 시점을 기록하도록 정리.
- `03_claude/`는 원본·allowlist·검증 절차를 확정하기 전까지 예약 영역으로 유지하도록 활성화 조건을 정의.
- 도구 중립 규칙은 `01_repository_governance/`, 도구 종속 자료는 각 도구 영역에 배치하는 분리 기준을 정의.
- 이관 저장소의 템플릿 사용 실태를 측정하고, 현재 사용 형식과 미사용 문서의 재검토 조건을 기록.
- Zircon Windows 후속 작업을 `/root/22_github_private/12_zircon_win/TODO.md`로 이관하고 `TODO2.md`에서 관련 블록을 정리.
- Ansible 저장소의 `.governance/` 병행 검증을 완료하고 중앙 `chobo_ansible` profile과 관련 활성 참조를 제거.
- `TODO2.md`의 Ansible profile 정리 항목을 완료하고 임시 TODO 문서를 삭제.
- `TODO.md`에서 완료된 작업과 해소된 검사 예외를 제거하고, 실제 미완료 fact-check와 유효한 검사 예외만 유지.
- `kiro_cli_command_reference.md`의 frontmatter TODO를 종료. 일반 문서에는 `_reference/` 전용 frontmatter 규칙을 적용하지 않음.
- 신규 저장소의 기본 작업 문서 위치를 `.governance/ISSUE.md`, `.governance/TODO.md`, `.governance/PLAN.md`로 정의하고, 기존 루트 문서는 legacy로 허용. 관련 템플릿과 작업 skill 탐색 경로를 갱신.
- `md-style-check.py --list-skips`를 CI에 등록하여 사유 없는 검사 예외를 차단.
- `TODO2.md`에 분산되어 있던 완료 기록을 CHANGELOG의 Added·Changed·Fixed 항목으로 통합하고, TODO2에는 미완료 작업만 남김.
- Ansible 저장소 후속 검증에서 `terraform fmt` 2건, 헤딩 레벨 건너뜀 4건, 목차 앵커 불일치 1건과 목차 누락 1건을 수정.

### Fixed

- `CHANGELOG.md`와 `LICENSE.md`에서 존재하지 않는 `#목차`를 참조하던 복귀 링크 11건 제거.
- `STYLE.md`의 중첩 코드블록 오류 수정. §5~§7, §10, §11 이 코드블록으로 렌더링되던 문제 해결.
- `STYLE.md`의 중복된 `## 14.` 섹션 번호를 14/15/16 으로 재정렬.
- 헤딩 레벨 건너뜀 1건, 중복 앵커 2건 수정.
- `git_concepts.md` 의 목차가 존재하지 않는 섹션을 링크하던 문제 수정 (섹션 번호 재부여).
- 목차 앵커 불일치 7건 수정. em dash·슬래시·`+` 가 앵커에서 제거되며 발생한 불일치.
- `license_guide.md` 표 정렬 26건 수정.
- `md-heading-check.py` 앵커 생성 규칙을 github-slugger 문자 집합으로 교체.
- `md-heading-check.py` 펜스 판정을 CommonMark 규칙으로 교체하고 범위·하위 절 번호 표기 지원.
- `md-heading-check.py` 의 H2 번호 패턴이 이중 이스케이프로 작성되어 `number` 검사가 동작하지 않던 문제 수정.
- `md-heading-check.py` 의 앵커 링크 패턴이 링크 텍스트의 중첩 대괄호를 처리하지 못하던 문제 수정.
- 목차에서 빠져 있던 섹션 5건 추가.
- `git_official_notes.md`, `git_guide.md`, `git_concepts.md`의 사실 오류 12건 수정.
- `privacy_law_guide.md` 개요 표의 소관 기관을 풀네임 병기로 정정.
- 추적되던 구버전 백업 파일 제거 및 `.gitignore` 패턴 보강.
- Kiro 동기화 스크립트가 존재하지 않는 파일을 allowlist에서 요구해 검증 단계에서 중단되던 문제 수정.
- Kiro 미러의 계정·내부 IP·사용자 홈 경로 기록 3건 제거.
- 원본 에이전트 JSON 8개의 파일 끝 개행 누락 수정.

---

## [3.10.0] - 2026-08-20

### Added

- `00_governance/`를 저장소 운영 정책과 AI 도구 미러의 공통 상위 디렉토리로 추가.
- 향후 Claude 자료를 위한 `00_governance/03_claude/` 예약 영역 추가.
- 도구별 동기화를 위한 `manifests/kiro_files.txt` 구조 추가.
- 민감정보와 환경 정보를 제외한 `profiles/chobo_ansible.md` 저장소 profile 추가.
- Kiro 동기화 스크립트와 `.gitignore`에 로컬 전용 `.local/` 제외 규칙 추가.

### Changed

- `00_repository_governance/`를 `00_governance/01_repository_governance/`로 이동.
- `00_kiro/`를 `00_governance/02_kiro/`로 이동.
- README, 검사 설정, 유사 레포 비교 문서의 활성 경로를 새 구조로 갱신.

---

## [3.9.0] - 2026-08-20

### Added

- `00_readme.md/`를 Kiro 실행 자료 미러임을 명시하는 `00_kiro/`로 rename.
- `00_repository_governance/` 추가.
- 문서 운영 정책, Kiro 동기화 정책, `PLAN.md`·`ISSUE.md` 템플릿 추가.
- `sync_files.txt`로 Kiro 공개 동기화 허용 목록 추가.
- 루트 `README.md`에 Kiro 운영 문서와 저장소 운영 정책 링크 추가.

### Changed

- `md-style-check.py`, `.md-style-check.toml`, 유사 레포 비교 문서의 Kiro 디렉토리 경로를 `00_kiro/`로 갱신.
- `CHANGELOG.md`의 마지막 업데이트 날짜를 `2026-08-20`으로 갱신.

---

## [3.8.0] - 2026-08-20

### Added

- `.md-style-check.toml`로 Markdown 검사 제외 디렉토리·파일 설정을 분리.
- GitHub Actions에 `main`·`yunli` push와 Pull Request 대상 Markdown 검증 추가.
- CI에서 `md-link-check.py`, `md-style-check.py`, `readme_inventory_check.py` 실행.

### Fixed

- `md-style-check.py`의 4-backtick·인용구 코드 fence 처리를 fence 길이 기준으로 정정.
- 코드블록 반복 제거 결과를 캐시하고, 중첩 박스 다이어그램을 depth 기준으로 검사.
- 출력 패턴·skip 옵션 매핑을 목록과 사전으로 분리.
- 날짜 자동화 workflow의 staged 상태 검사 순서를 수정하여 실제 commit·push가 실행되도록 보강.

---

## [3.7.0] - 2026-08-20

### Fixed

#### `_reference/web_server_official_notes.md` fact-check

- Nginx `ssl_protocols` TLSv1.3 기본 활성화 시점을 `1.19.0`에서 `1.23.4`로 정정.
- Nginx stream 모듈 도입 시점을 `1.9.5`에서 `1.9.0`으로 정정.
- Nginx `ssl_certificate` 설명을 `ssl` 디렉티브 deprecated 및 `listen ... ssl` 사용 기준으로 정정.
- Apache 2.4.58 `mod_http2` 기능을 TLS 1.3 early data가 아닌 HTTP 103 Early Hints로 정정.
- 공식 출처: [Nginx CHANGES](https://nginx.org/en/CHANGES), [Nginx SSL module](https://nginx.org/en/docs/http/ngx_http_ssl_module.html), [Apache mod_http2](https://httpd.apache.org/docs/2.4/mod/mod_http2.html), [Apache 2.4.58 CHANGES](https://archive.apache.org/dist/httpd/CHANGES_2.4.58).

---

## [3.6.0] - 2026-08-05

### Added

#### VPN 문서 3종 신규 추가

| 파일                                                       | 내용                                                                                           |
|------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `01_fundamentals/networking/softether_vpn_server_guide.md` | SoftEther VPN Server 설치·초기설정·L2TP/IPsec·OpenVPN·방화벽·systemd·명령어·트러블슈팅         |
| `01_fundamentals/networking/vpn_comparison_blog.md`        | VPN 프로토콜 선택 가이드 — 보안·성능·방화벽 통과·시나리오별 선택·플로우차트                    |
| `_reference/softether_official_notes.md`                   | SoftEther 공식 스펙 및 소스코드 기반 참조 노트 (GlobalConst.h, Server.h, softether.org/3-spec) |

#### fact-check 수정

- `01_fundamentals/networking/vpn_comparison_blog.md` — WireGuard 연도 2018 → 2016 (ePrint 2016/914 기준)

### Removed

- `TODO2.md` — T1/T2 작업 완료 확인 후 삭제

---

## [3.5.0] - 2026-08-05

### Changed

#### 파일명 변경 — 개념 문서 _concepts 접미어 통일 (8개)

| 구 파일명                    | 신 파일명                             |
|------------------------------|---------------------------------------|
| `linux/ipc.md`               | `linux/ipc_concepts.md`               |
| `linux/virtual_memory.md`    | `linux/virtual_memory_concepts.md`    |
| `linux/scheduler.md`         | `linux/scheduler_concepts.md`         |
| `linux/namespace.md`         | `linux/namespace_concepts.md`         |
| `linux/cgroup.md`            | `linux/cgroup_concepts.md`            |
| `networking/TCP_state.md`    | `networking/tcp_state_concepts.md`    |
| `networking/vpn_protocol.md` | `networking/vpn_protocol_concepts.md` |
| `cs/cpu_cisc_risc.md`        | `cs/cpu_cisc_risc_concepts.md`        |

- 내부 참조 링크 12개 파일 일괄 수정 (README.md, CHANGELOG.md, TODO2.md, STYLE.md 등)
- `TODO2.md` 작업 전체 완료 (Batch 1~4 ✅ ) → 파일 삭제

### Fixed

#### fact-check 수정 (02_infrastructure)
- `devops_toolchain.md` — Terraform/Ansible/Docker/Compose/K8s/Helm/ArgoCD/Prometheus/Grafana 버전 갱신
- `container_runtime.md` — containerd 1.x 비호환 시점 v1.37 → v1.38
- `zabbix_vs_prometheus.md` — Prometheus v3.13.0 → v3.13.2
- `prometheus_grafana.md` — Prometheus/Alertmanager/Grafana/node-exporter 이미지 버전 갱신
- `airflow.md` — Airflow 3.2.1 → 3.3.0

#### fact-check 수정 (01_fundamentals)
- `softether_vpn_client_guide.md` — v4.43-9799-beta → v4.44-9807-rtm (2026-08 기준)
- `crates_ecosystem.md` — tokio version 1.40 → 1.53
- `TCP_state.md` (→ tcp_state_concepts.md) — tcp_fin_timeout이 FIN_WAIT_2 타이머임을 명확히 수정, tcp_tw_recycle 제거 커널 버전(4.12) 명시

---

## [3.4.0] - 2026-08-02

### Added

#### _reference — 신규 참조 파일 1개
- `csharp_official_notes.md` — .NET 10 LTS/C# 14, LTS/STS/EOL 버전 대응표, 타입 시스템, async/await, 언어 기능 (C# 3~14), dotnet CLI/NuGet/msbuild-props, deprecated (releases-index.json/Language-Version-History.md 기반, fact-check 완료)

#### 01_fundamentals/programming/csharp — 신규 디렉토리 및 문서 5개
- `README.md` — 학습 순서, 빠른 참조, 주요 개념 요약
- `csharp_key_concepts.md` — 타입 시스템, 값/참조 형식, struct vs class, record, nullable, NRT, null 연산자, pattern matching, primary constructor, required, global using, .NET 버전 대응표
- `csharp_oop.md` — 클래스 구성 요소, 접근 제한자, 상속, 인터페이스(default members C# 8+), 추상 클래스, 다형성, 제네릭 제약
- `csharp_async.md` — async/await 기초, 반환 타입(Task/ValueTask/void), 병렬 실행, ConfigureAwait, async 스트림(C# 8+), CancellationToken, 안티패턴
- `csharp_linq.md` — 람다, Func/Action/Predicate, 쿼리/메서드 문법, 연산자(필터/변환/집계/정렬/그룹화/조인), 지연/즉시 실행, ToLookup/Zip
- `csharp_dotnet_cli.md` — dotnet new/build/run/test/publish, .csproj PropertyGroup, NuGet 관리, self-contained/AOT 게시, xUnit/NUnit/MSTest 구조

---

## [3.3.0] - 2026-08-01

### Added

#### _reference — 신규 참조 파일 8개 (Batch 1~4)
- `gdb_official_notes.md` — GDB 17.2, break/run/bt/step/next, -p attach, --batch, 약어 규칙 (gdb.1/GNU FTP)
- `strace_official_notes.md` — strace v7.1, syscall/signal 추적, -e trace 필터, --seccomp-bpf (strace.1/GitHub)
- `ltrace_official_notes.md` — ltrace 0.8.1, 동적 라이브러리 함수 추적, -e/-l/-x 필터, --demangle (ltrace.1/GitLab)
- `valgrind_official_notes.md` — Valgrind 3.27.1, Memcheck(definitely/indirectly/possibly lost), Callgrind/Helgrind/Massif (valgrind.org)
- `perf_official_notes.md` — perf stat/record/report/top/trace/probe 서브커맨드, --list-cmds/-vv (perf.1/kernel wiki)
- `lsof_official_notes.md` — lsof 4.99.7, FD/TYPE 필드, -p/-i/-u/-a/-n/-P/-t 옵션 (lsof.8/GitHub)
- `iotop_official_notes.md` — iotop v1.31, Linux 2.6.20+, --only/--batch/--processes, Total vs Current (iotop.8/GitHub)
- `tcpdump_official_notes.md` — tcpdump 4.99.6, BPF 필터 문법, -w pcap/-r/-n/-nn/-X/-Q (tcpdump.1)
- `bash_shell_official_notes.md` — Bash 5.3, interactive/non-interactive §6.3, PS1/BASH_ENV, 리다이렉션 §3.6 (bash manual)
- `vim_official_notes.md` — Vim 9.2, Normal/Insert/Visual/Command/Replace 모드, 주요 명령어 (vimhelp.org/vim.1)

#### _reference/INDEX.md — 항목 추가
- Batch 1~4 신규 10개 항목 등록

### Fixed

#### 01_fundamentals/linux — `<!-- reference:` 연결 추가
- `gdb.md` → `gdb_official_notes.md`
- `strace.md` → `strace_official_notes.md`
- `ltrace.md` → `ltrace_official_notes.md`
- `valgrind.md` → `valgrind_official_notes.md`
- `perf.md` → `perf_official_notes.md`
- `lsof.md` → `lsof_official_notes.md`
- `iotop.md` → `iotop_official_notes.md`
- `tcpdump.md` → `tcpdump_official_notes.md`
- `shell_interactive_mode.md` → `bash_shell_official_notes.md`
- `vim.md` → `vim_official_notes.md`
- `vim_airline.md` → `vim_official_notes.md`
- `bash_file_redirection.md` — reference 병기 추가 (kernel + bash_shell)
- `bash_math.md` — reference 병기 추가 (kernel + bash_shell)
- `bash_trap_complete_guide.md` — reference 병기 추가 (kernel + bash_shell)
- `vim_airline.md` — H1 12개 → H2로 변환 (문서 구조 정규화)
- `root_password_recovery.md` — 절차 문서 확인 (_reference 불필요)

---

## [3.2.0] - 2026-08-01

### Added

#### _reference — 신규 참조 파일 2개
- `ebpf_bpftrace_official_notes.md` — eBPF 개요, BPF Map 타입(bpf.2 기반), bpftrace 프로브 타입, 활용 도구(Cilium/Falco/Katran), CAP_BPF(Linux 5.8+), libbpf v1.7.0, bpftrace v0.26.1
- `linux_process_official_notes.md` — Process Lifecycle(fork/execve/wait man page 기반), Virtual Memory(mmap.2/MM concepts), OOM killer(oom_score_adj, overcommit_memory), IPC(pipe/shmget/mq_overview), 시스템 프로세스(PID0/1/2)

#### _reference/INDEX.md — 항목 추가
- eBPF / bpftrace — libbpf v1.7.0, bpftrace v0.26.1
- Linux Process / Memory / IPC — fork/exec/wait, mmap, OOM, pipe/shm/mq

### Fixed

#### 01_fundamentals/linux — `<!-- reference:` 연결 15개 추가
- `linux_filesystem.md`, `linux_virtual_fs.md` → `linux_filesystem_official_notes.md`
- `scheduler_concepts.md`, `netfilter_tc.md`, `seccomp_capabilities.md` → `linux_kernel_official_notes.md`
- `bash_file_redirection.md`, `bash_math.md`, `bash_trap_complete_guide.md` → `linux_kernel_official_notes.md`
- `ebpf.md`, `bpftrace.md` → `ebpf_bpftrace_official_notes.md` (기존 kernel_notes에서 교체)
- `process_lifecycle.md`, `linux_system_processes.md` → `linux_process_official_notes.md` (기존 kernel_notes에서 교체)
- `virtual_memory_concepts.md` → `linux_process_official_notes.md` (기존 kernel_notes에서 교체)
- `ipc_concepts.md`, `oom_hang.md` → `linux_kernel_official_notes.md` + `linux_process_official_notes.md` (병기)

#### _reference — fact-check 수정
- `linux_process_official_notes.md` — `overcommit_memory` 출처 `MM concepts` → `proc_sys_vm.5` 교체 (직접 접근 가능한 man page 기반)

---

## [3.1.0] - 2026-07-29

### Added

> 3.0.0 구조 개편(git mv) 이후 mtime 초기화로 인해
> 이번 세션 신규 작성 파일만 기재. 이전(migrated) 파일은 제외.

#### 01_fundamentals/cs — 신규 문서 2개
- `version_control_concepts.md` — VCS 3세대 분류, 중앙집중형 vs 분산형 아키텍처, SVN 저장소/Working Copy 구조, 리비전 모델, 브랜치 전략, 병합 원리, 잠금 모델, 인프라 활용(hooks/백업)
- `git_concepts.md` — Git 객체 모델(blob/tree/commit/tag), DAG 구조, 참조 시스템(HEAD/branch/tag), 작업 영역 3단계, reset 3종류, 브랜치 전략(Trunk-based/GitHub Flow/GitFlow), merge vs rebase, 원격 저장소, 훅 자동화, GitOps + IaC 활용

#### 02_infrastructure/cicd — 신규 문서 1개
- `svn_guide.md` — SVN CLI 실무 가이드 (checkout/update/commit/diff/log/branch/merge/충돌해결/속성/잠금/externals/서버설정/실무팁 전 명령어)

#### _reference — 신규 참조 파일 2개
- `svn_official_notes.md` — Apache Subversion 1.14.5 버전 현황, FSFS 포맷, 프로토콜, 잠금 모델, svn:* 속성, svnadmin 명령어, Git 비교
- `git_official_notes.md` — Git 2.55.0 버전 현황, 4가지 객체 모델, SHA-1/SHA-256, HEAD/branch/tag 참조 구조, merge 전략(ort 2.34+ 기본), reflog, packfile, 주요 설정값

#### _reference/INDEX.md — 항목 추가
- SVN (Subversion) 1.14.5 (LTS)
- Git 2.55.0

### Fixed

#### _reference — 팩트체크 수정
- `rust_official_notes.md` — `last_checked` 2026-07-29 갱신, "fully enabling" 직역 → "전체 활성화" (과장 표현 검사 통과)
- `git_official_notes.md` — merge 기본 전략 `Recursive` → `ort (Git 2.34+)` 수정
- `git_concepts.md` — §7 merge vs rebase 다이어그램에 ort 관련 주석 추가
- `ai_coding_tools_official_notes.md` — "최고" 표현 → "1위" / "속도 1위(Fastest measured)" 수정
- `charset_encoding_official_notes.md` — "ASCII 하위 호환 (U+0000~U+007F는 1바이트, 값 동일)"으로 수정 (RFC 3629 원문 기반, 과장 표현 제거)
- `svn_official_notes.md` — 다이어그램 내부 한글(`개발자`) → 영문(`Dev A/B/C`) 수정

#### _reference — 표 정렬 일괄 수정 (14개 파일)
- `INDEX.md`, `android_adb_official_notes.md`, `chaos_finops_official_notes.md`
- `charset_encoding_official_notes.md`, `e4fsprogs_centos5_notes.md`, `github_references.md`
- `hyperv_centos5_io_contention_notes.md`, `hyperv_version_comparison_notes.md`
- `linux_filesystem_official_notes.md`, `linux_kernel_official_notes.md`
- `platform_engineering_official_notes.md`, `sre_operations_official_notes.md`
- `web_server_official_notes.md`, `ai_coding_tools_official_notes.md`
- md-style-check `_reference/` 37개 파일 0건 통과

### Removed

- `01_fundamentals/programming/rust/temp_factcheck_20260729.md` — 임시 팩트체크 메모 파일 삭제

---

## [3.0.3] - 2026-07-28

### Added

#### 01_fundamentals/programming/rust — 신규 문서 11개
- `01_ownership_borrowing.md`, `02_error_handling.md`, `03_traits_generics.md`
- `04_concurrency.md`, `05_system_programming.md`, `06_networking.md`
- `07_cli_tools.md`, `08_crates_ecosystem.md`, `09_testing.md`
- `10_practical_examples.md`, `rust_roadmap_for_se.md`

### Fixed

#### 표 정렬 일괄 수정 (~90개 파일)
- `01_fundamentals/` (linux, networking, cs, programming/python) — 표 display width 기준 재정렬
- `02_infrastructure/` (cicd, containers, iac, monitoring, web_server)
- `04_security/` (cloud, cve, hardening)
- `05_database/nosql`, `05_database/operations`, `97_misc/`

### Removed

#### 97_misc → 99_archive/05_centos5_legacy 이동 (6개 파일)
- `centos5_aws_migration_assessment.md`, `centos5_ext4_fsck_guide.md`
- `centos5_gamedb_hyperv_host_compatibility.md`, `hyperv_io_contention_legacy_vm.md`
- `hyperv_myisam_io_timeout_incident_20260715.md`, `hyperv_version_centos5_compatibility.md`

---

## [3.0.2] - 2026-07-27

### Changed

- `06_career/ai_tools/ai_coding_tools_comparison.md` — AI 코딩 도구 비교 내용 갱신
- `97_misc/similar_repos.md` — 유사 저장소 목록 갱신

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

### Fixed

- `02_infrastructure/cloud_aws/vpc_peering_inter_region_guide.md` — 다이어그램 좌우 박스 비대칭 수정, fence 홀수 수정, 한글→영문
- `02_infrastructure/cicd/infra_monorepo_and_boilerplate.md` — 중첩 코드블록 4-backtick 전환

### Removed

- `00_readme.md/` — Kiro 설정 복사본 (불필요)
- `90_DELETE/` — deprecated 파일 2개 (CONTRIBUTING, GITHUB_UPLOAD_GUIDE)
- 기존 디렉토리 README.md 12개 (01_install ~ 12_tech_stack)

## [2.3.0] - 2026-07-07

### Added

#### 12_tech_stack — 신규 문서 3개
- `harness_engineering.md` — AI Harness Engineering (에이전트 환경 설계)
- `vpn_protocol_concepts.md` (05_computer_science) — VPN 프로토콜 비교 (PPTP~WireGuard, RFC 대조 검증)
- `zabbix_vs_prometheus.md` — 모니터링 도구 비교 (아키텍처, 수집, 알림, 확장성)

#### _reference — 신규 참조 파일
- `vpn_protocol_official_notes.md` — VPN RFC 기반 참조 노트
- INDEX.md 갱신 (VPN Protocol 항목 추가, 알파벳순 정렬)

#### 03_advanced_linux — 신규 문서 6개
- `ipc_concepts.md` — 프로세스 간 통신 (Pipe, Socket, Shared Memory, Message Queue)
- `linux_virtual_fs.md` — VFS 추상화 계층, inode, dentry, superblock
- `namespace_concepts.md` — Linux Namespace 7종 (pid, net, mnt, uts, ipc, user, cgroup)
- `netfilter_tc.md` — Netfilter 훅 체인, iptables/nftables, TC 트래픽 제어
- `scheduler_concepts.md` — CFS, RT, Deadline 스케줄러, nice, cgroup CPU
- `virtual_memory_concepts.md` — 페이지 테이블, TLB, Swap, OOM Killer, NUMA

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
- `vpn_protocol_concepts.md` — 다이어그램 `│`/`v` 위치, 박스 `┐`/`┘` 닫힘, Transport/Tunnel Mode 박스 수정

#### vpn_protocol_concepts.md 사실 검증 수정
- 세대 타임라인: OpenVPN 2012→2001, IKEv2 순서 교체
- IPsec AES-GCM-16: SHOULD+ → MUST (RFC 8221)
- OpenVPN TLS: "1.3 기본" → "1.2/1.3 (최상위 지원 버전 자동 선택)"
- L2TP/IPsec 오버헤드: "~20% 증가" → 출처 없는 수치 제거

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
- CC BY 4.0 라이선스 적용 (문서)
- MIT License 적용 (코드 예제)

---

## 변경 사항 기록 방법

### 카테고리

- `Added` - 새로운 기능 추가
- `Changed` - 기존 기능 변경
- `Deprecated` - 곧 제거될 기능
- `Removed` - 제거된 기능
- `Fixed` - 버그 수정
- `Security` - 보안 관련 변경

위 6종 외의 카테고리는 사용하지 않습니다.

### 버전 번호

| 자리  | 올리는 기준                                 | 예                  |
|-------|---------------------------------------------|---------------------|
| major | 저장소 구조 개편, 최상위 디렉토리 체계 변경 | `2.0.0`, `3.0.0`    |
| minor | 문서 추가, 검사 도구 기능 추가, 정책 도입   | `3.10.0` → `3.11.0` |
| patch | 오류 수정과 서식 정정만 포함                | `3.0.2`, `3.0.3`    |

문서 저장소이므로 Semantic Versioning 의 하위 호환 개념은 그대로 적용되지 않습니다. 위 기준으로 해석합니다.

- 릴리스는 날짜 단위가 아니라 작업 단위입니다. 같은 날 여러 버전이 올라갈 수 있습니다.
- 항목은 최신 버전이 위로 오도록 내림차순으로 배치합니다.
- 한 릴리스 안에서 중간 상태는 기록하지 않습니다. 최종 결과만 남깁니다.

🟡 `3.0.1` 은 존재하지 않습니다. 번호를 건너뛴 것으로, 누락된 변경 내역은 없습니다.

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

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.
