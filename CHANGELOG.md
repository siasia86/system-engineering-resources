# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

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

**마지막 업데이트**: 2026-03-25

© 2026 siasia86. Licensed under CC BY 4.0.
