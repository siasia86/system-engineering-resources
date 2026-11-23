# 32 `system-engineering-resources` 문서 repository 계획

32 repository는 Linux·네트워크·보안·데이터베이스·인프라·SRE 등 시스템 엔지니어링 학습 자료를 구조화하고 검증하는 문서 repository입니다. 30 `sia_scripts`는 공용 Markdown checker와 release artifact를 제공하고, 31 `governances`는 공통 repository·infrastructure·security policy를 관리하며, 32는 문서 내용과 checker consumer profile을 관리합니다. Kiro·Claude 공개 mirror는 35 `agent-skill`에서 관리합니다.

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. Repository 목적](#1-repository-목적) / [2. 30 통합 역할](#2-30-통합-역할) / [3. 관리 범위](#3-관리-범위)     |
| [4. 현재 상태](#4-현재-상태) / [5. 문서 운영 계획](#5-문서-운영-계획) / [6. 검증과 rollback](#6-검증과-rollback) |
| [7. DO-07 DevOps 주제 문서](#7-do-07-devops-주제-문서)                                                           |

---

## 1. Repository 목적

32는 다음 목적의 system engineering 문서 repository입니다.

- Linux·Windows 운영체제와 시스템 내부 구조 학습.
- 네트워크·보안·데이터베이스·인프라 도구 학습.
- Ansible·Docker·Kubernetes·CI/CD·Cloud·Monitoring 운영 문서 관리.
- SRE·debugging·testing·incident 대응 절차 정리.
- 문서 간 링크·헤딩·표·README inventory 품질 유지.

주요 영역은 다음과 같습니다.

```text
01_fundamentals
02_infrastructure
03_engineering
04_security
05_database
06_career
96_scripts
97_misc
98_image
```

각 문서는 학습·운영 목적과 대상 독자가 명확해야 하며, 특정 도구 전환 기록이 repository 전체 구조를 대표하지 않도록 합니다.

## 2. 30 통합 역할

30과 32의 책임 경계는 다음과 같습니다.

```text
30 sia_scripts
  공용 checker source·test·release·CI·Ansible 운영
          |
          v
32 system-engineering-resources
  학습 문서·checker profile·30 release consumer
```

### 30에서 관리

- `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check` source.
- unit test와 regression fixture.
- release builder·manifest·SHA-256 checksum.
- GitHub Actions source·security·release 검증.
- 공용 설치·CI·rollback contract.

### 32에서 관리

- 학습 문서 source와 문서 taxonomy.
- `.md-style-check.sia_scripts.toml` repository-local checker profile.
- 30 release version·checksum을 사용하는 consumer workflow.
- 문서별 예외와 repository-local 검증 결과.
- README inventory와 문서 간 연결성.

32 checker exception을 30 source에 하드코딩하지 않습니다. 30은 contract를 제공하고 32는 실제 profile을 유지합니다. 공통 governance policy는 31에서 참조하고, Kiro·Claude mirror는 35에서 참조합니다.

## 3. 관리 범위

### 포함

- 문서 신규 작성·수정·분류·목차 갱신.
- 기술 내용의 source·version·환경 전제 확인.
- 문서 간 내부 링크와 README inventory 유지.
- 30 release consumer version·checksum 갱신.
- 32 checker profile과 workflow 유지.
- 문서 변경의 rollback과 변경 이력 기록.

### 제외

- 30 checker source·test·release builder의 직접 수정.
- 32 repository에 checker source를 복사해 별도 유지하는 방식.
- 32 문서 내용을 특정 도구 전환 작업의 부속 문서로 취급하는 방식.
- 실제 대상 host 배포를 일반 문서 변경에 포함하는 방식.
- 승인되지 않은 artifact 또는 credential을 문서에 기록하는 방식.

## 4. 현재 상태

### 문서 repository

32는 system engineering 학습 자료 영역·하위 README·문서 inventory·Markdown 품질 검증 기준을 유지합니다. 완료 이력은 `CHANGELOG.md`에서 관리합니다.

### 30 consumer

완료된 30 consumer 전환·검증 이력은 `CHANGELOG.md`의 `[4.0.0]`에 기록합니다.

현재 승인된 consumer baseline은 다음과 같습니다. 2026-11-21에 [검사 workflow](../.github/workflows/update-date.yml)의 고정 값과 대조했습니다.

```text
repository: siasia86/30_sia-scripts
release:    v0.7.0
artifact:   sia_scripts_0.7.0.tar.gz
sha256:     53749376656bc4e638cece58b001fa83de29fd18dcdef17bcb110f9b73a01a2d
```

판을 바꾼 경과는 `CHANGELOG.md`의 "검사 도구 고정 판" 항목(0.6.0은 2026-11-17, 0.7.0은 2026-11-21)에 있습니다. 다음 고정 판 갱신도 31·32·35를 함께 바꾸는 일괄 결정을 따르며, 바꿀 때는 workflow의 판·checksum, [검증 기준](verification.md)의 판, 이 절을 같은 변경에서 고칩니다.

## 5. 문서 운영 계획

### 문서 작성·수정

- 새 문서는 적절한 영역과 파일명 규칙에 맞게 배치합니다.
- 문서 첫 등장 기술 용어와 약어를 설명합니다.
- 명령어·설정·경로는 실제 실행 가능성을 확인합니다.
- 예시 credential은 표준 placeholder를 사용합니다.
- 내부 링크와 목차를 같은 변경에서 갱신합니다.
- 실행 결과와 검증 날짜를 필요한 범위로 기록합니다.
- 기술 문서는 한 문서에 한 기술을 다루고, 그 문서만으로 설치 → 기본 사용 → 검증을 따라 할 수 있게 씁니다. 다른 기술은 "함께 보기"로 연결합니다.
- 기존 문서의 내용을 다른 문서로 옮기면 원래 자리에는 안내만 남겨 본문을 중복하지 않습니다. 파일 경로를 바꿀 때는 [옮김 기록](MOVED.md)을 따릅니다.
- 본문은 특정 작업 PC나 시험 환경에 묶지 않고 범용으로 씁니다. 기준 판, 확인 날짜, 실행하지 못한 범위는 문서 머리말에 둡니다.

### 문서 품질

- Markdown style·heading·link 검사를 통과합니다.
- README inventory를 갱신합니다.
- 문서 변경 시 gitleaks와 `git diff --check`를 실행합니다.
- 저장소 policy exception은 `.md-style-check.sia_scripts.toml`에 최소 범위로 기록합니다.
- 30 release 변경 시 consumer version·checksum을 함께 검토합니다.

### Consumer workflow

32 workflow는 다음 순서로 동작해야 합니다.

```text
30 private release download
          |
          v
SHA-256 checksum verification
          |
          v
manifest + embedded file hash verification
          |
          v
32 checker profile + sia-* wrapper
```

artifact 검증에 실패하면 문서 검사를 실행하지 않습니다. token·private key·password는 workflow YAML·commit·log에 기록하지 않습니다.

## 6. 검증과 rollback

### 검증 명령

검증된 30 release wrapper를 사용하는 환경에서는 다음 순서를 적용합니다.

```bash
R32="$HOME/32_system-engineering-resources"

sia-md-link-check "$R32"
sia-md-style-check \
  --config "$R32/.md-style-check.sia_scripts.toml" \
  "$R32"
sia-md-heading-check "$R32"
sia-readme-inventory-check "$R32/README.md"
gitleaks detect --source "$R32" --no-git --no-banner
git -C "$R32" diff --check
```

local 환경에 wrapper가 없으면 승인된 30 artifact를 먼저 설치합니다. 도구가 없는 상태를 통과로 처리하지 않습니다.

### Rollback

- 문서 내용 오류: 변경 commit을 revert합니다.
- checker profile 오류: 이전 승인 profile을 복구합니다.
- 30 release consumer 오류: 이전 승인 version·checksum으로 pin을 되돌립니다.
- root checker cleanup 오류: cleanup commit `fe4a9d6d48aba374645542cec812eda583487057`를 revert합니다.
- 실제 host 배포 오류: 30 installation guide의 이전 release rollback 절차를 따릅니다.

기존 release tag와 artifact를 force update하거나 삭제하지 않습니다.

32 문서 repository 운영의 다음 작업 목록은 30 `.governance/PLAN.md`의 "32 system-engineering-resources 후속 작업" 섹션에서 관리합니다. 이 문서와 중복 기록하지 않습니다.

---

## 7. DO-07 DevOps 주제 문서

00 세션의 직접 요청 DO-07(2026-11-23, 05 D169 경로)로 roadmap.sh DevOps 하위 주제 108개의 문서를 씁니다. 요청 목록의 우선순위를 따르되 문서 단위와 순서는 32가 정합니다. 1순위 37개 주제를 먼저 등록하고, 2·3순위는 1순위가 끝나기 전에 같은 방식으로 이 절에 더합니다.

### 처리 원칙

- 기술 하나에 독립 문서 하나를 둡니다. 요청의 개념·가이드·설정·설치 유형은 문서 하나 안의 개요 → 설치 → 사용 → 검증 절로 합칩니다(5절 작성 원칙).
- 공식 자료 요약은 `_reference/<주제>_official_notes.md`에 `sources`·`last_checked` frontmatter와 함께 둡니다. 이미 있으면 새로 쓰지 않고 확인일만 갱신합니다.
- 기존 문서가 있으면 새로 쓰기 전에 본문을 읽고 보강과 신규 중에서 고릅니다. 내용을 옮기면 원래 자리에는 안내만 남깁니다.
- 상용·SaaS(Datadog, Splunk, Papertrail, Bitbucket)는 계정·비용 없이 확인할 수 있는 공식 자료 범위에서 `_reference`와 무료·로컬 도구와의 비교 문서만 씁니다.
- 예제는 컨테이너나 시험 디렉터리에서 실행해 확인하고, 실행하지 못한 범위는 문서 머리말에 적습니다. 호스트에 설치하지 않습니다.
- 묶음마다 문서 단위로 commit하고, 이 세션 사용자 확인 뒤 push합니다. 묶음 결과는 요청 세션에 보냅니다.

### 1순위 묶음과 문서

| 묶음 | 주제                       | 32 문서 계획                                                                                                                                               | 비고                                                                    |
|------|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| B1   | Text Manipulation          | `_reference` 신규, `01_fundamentals/linux/text_processing.md` 신규 (grep·sed·awk·cut·sort·uniq·tr)                                                         | 첫 묶음                                                                 |
| B2   | Ubuntu / Debian            | `_reference` 신규, `01_fundamentals/linux/ubuntu_debian.md` 신규 (릴리스, apt, 업그레이드)                                                                 |                                                                         |
| B2   | RHEL / Derivatives         | `_reference` 신규, `01_fundamentals/linux/rhel_family.md` 신규 (RHEL·Rocky·Alma, dnf, 업그레이드)                                                          |                                                                         |
| B2   | SUSE Linux                 | `_reference` 신규, `01_fundamentals/linux/suse_linux.md` 신규 (SLES·openSUSE, zypper)                                                                      | 요청대로 개념 중심                                                      |
| B2   | Windows                    | 보강 불필요로 판단 (2026-11-23). 기존 네트워크 진단·리소스 분석·에디션·핵심 개념 문서 4개가 서버 운영 범위를 다룸                                          | B5 PowerShell 문서에서 연결                                             |
| B3   | FreeBSD · OpenBSD · NetBSD | `_reference` 3개 신규, `01_fundamentals/linux/bsd_family.md` 신규 (세 OS 개념과 차이)                                                                      | 개념만이라 계열 문서 하나로 묶음, 가이드·설치 제외                      |
| B4   | Process Monitoring         | `_reference` 신규(procps), `01_fundamentals/linux/process_monitoring.md` 신규 (ps·top·htop·pgrep)                                                          | 기존 `linux_process_official_notes`는 시스템 호출 범위라 별도 노트를 둠 |
| B4   | Performance Monitoring     | `_reference` 신규(sysstat), `01_fundamentals/linux/sysstat.md` 신규 (sar·mpstat·vmstat)                                                                    | perf·iostat·nmon 등 기존 문서는 함께 보기                               |
| B4   | Networking Tools           | `_reference` 신규, `01_fundamentals/linux/linux_network_tools.md` 신규 (ip·ss·dig·curl·mtr·nmap)                                                           | tcpdump·iperf3는 기존 문서 함께 보기                                    |
| B5   | Bash                       | `01_fundamentals/linux/bash_scripting.md` 신규 (기존 bash 문서는 리다이렉션·산술·trap 등 좁은 주제라 스크립트 기본 문서를 따로 둠), 기존 `_reference` 보강 |                                                                         |
| B5   | Power Shell                | `_reference` 신규, `01_fundamentals/windows/powershell.md` 신규 (Linux·Windows 설치, 기본, 원격)                                                           |                                                                         |
| B5   | Vim / Nano / Emacs         | `vim.md` 보강(설치·설정 파일·검증), `01_fundamentals/linux/nano.md`·`_reference` 신규                                                                      | Emacs 제외: 서버 운영 편집 용도가 드물고 vim·nano로 대체                |
| B6   | Git                        | 기존 git 문서 보강 검토 (설치, `git config` 초기 설정)                                                                                                     | 기존 `_reference` 사용                                                  |
| B6   | GitHub                     | `02_infrastructure/cicd/github.md` 신규 (계정 보안, SSH 키, PR 흐름)                                                                                       | `_reference`는 기존 `github_references` 확인                            |
| B6   | GitLab                     | `_reference` 신규, `02_infrastructure/cicd/gitlab.md` 신규 (Docker로 설치, 기본, 검증)                                                                     | 기존 `gitlab_ci.md`는 함께 보기                                         |
| B6   | Bitbucket                  | `_reference` 신규, `02_infrastructure/cicd/git_hosting_comparison.md` 신규 (GitHub·GitLab·Bitbucket 비교)                                                  | 가이드·설치 제외: Cloud는 계정, Data Center는 유료                      |
| B7   | Nginx                      | `_reference` 신규, 기존 `nginx_install.md` 보강 또는 `nginx.md` 신규                                                                                       | 본문 검토 뒤 정함                                                       |
| B7   | Apache                     | `_reference` 신규, 기존 `apache_install.md` 보강 또는 `apache.md` 신규                                                                                     | 본문 검토 뒤 정함                                                       |
| B7   | Tomcat                     | `_reference` 신규, `02_infrastructure/web_server/tomcat.md` 신규                                                                                           |                                                                         |
| B7   | Caddy                      | `_reference` 신규, `02_infrastructure/web_server/caddy.md` 신규                                                                                            |                                                                         |
| B7   | IIS                        | `_reference` 신규, `02_infrastructure/windows_server/iis.md` 신규                                                                                          | Linux 작성 환경이라 실행 시험 없음                                      |
| B8   | Forward Proxy              | `_reference` 신규(Squid), `02_infrastructure/web_server/squid.md` 신규                                                                                     |                                                                         |
| B8   | Reverse Proxy              | `_reference` 신규, `02_infrastructure/web_server/reverse_proxy.md` 신규 (개념과 구현 비교)                                                                 | `reverse_proxy_testing.md`는 함께 보기                                  |
| B8   | Caching Server             | `_reference` 신규(Varnish), `02_infrastructure/web_server/varnish.md` 신규                                                                                 | `cache_cdn_testing.md`는 함께 보기                                      |
| B8   | Load Balancer              | `_reference` 신규(HAProxy), 기존 haproxy 문서 보강 검토                                                                                                    | haproxy 문서 6개가 이미 있음                                            |
| B8   | Firewall                   | `_reference` 신규, `04_security/hardening/ufw_firewalld.md` 신규                                                                                           | `firewall_iptables_nftables.md`는 함께 보기                             |
| B9   | Prometheus · Grafana       | 기존 `prometheus_grafana*.md` 보강 검토 (독립 문서로 나눌지 판단)                                                                                          | 기존 `_reference` 사용                                                  |
| B9   | Zabbix                     | `02_infrastructure/monitoring/zabbix.md` 신규 (Docker로 설치, 에이전트, 검증)                                                                              | 기존 `_reference` 사용                                                  |
| B9   | Datadog                    | `_reference` 신규, `02_infrastructure/monitoring/monitoring_saas_comparison.md` 신규                                                                       | 상용이라 비교만                                                         |
| B10  | Elastic Stack              | `_reference` 신규, `02_infrastructure/data_pipeline/elastic_stack.md` 신규 (Elasticsearch·Kibana·수집기)                                                   | 기존 elasticsearch 문서는 함께 보기                                     |
| B10  | Loki                       | `_reference` 신규, `02_infrastructure/data_pipeline/loki.md` 신규                                                                                          |                                                                         |
| B10  | Graylog                    | `_reference` 신규, `02_infrastructure/data_pipeline/graylog.md` 신규                                                                                       |                                                                         |
| B10  | Splunk · Papertrail        | `_reference` 2개 신규, `02_infrastructure/data_pipeline/logging_saas_comparison.md` 신규                                                                   | 상용이라 비교만                                                         |

37개 주제 가운데 계열·제품군으로 묶은 것은 BSD 3개, Prometheus·Grafana, Splunk·Papertrail입니다. 하지 않는 항목은 Emacs 문서, BSD·SUSE의 가이드·설치, 상용 도구의 개별 가이드·설치이며 사유는 표의 비고에 있습니다.

### 2·3순위

2순위 32개(네트워킹·프로토콜 등)와 3순위 39개(kind·클라우드 선행 주제 등)는 요청 목록에 있습니다. 1순위 B10에 들어가기 전에 같은 원칙으로 묶음 표를 이 절에 더하고 [TODO](TODO.md)의 대기 항목을 갱신합니다.

---

## 참고 자료

- 30 installation guide: [30 `sia_scripts` installation guide](https://github.com/siasia86/30_sia-scripts/blob/main/docs/installation_guide.md) — ★★★☆☆
- 30 CI guide: [30 `sia_scripts` CI guide](https://github.com/siasia86/30_sia-scripts/blob/main/docs/ci_guide.md) — ★★★☆☆

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
