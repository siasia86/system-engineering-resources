# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

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
- CONTRIBUTING.md
- LICENSE.md

### Documentation
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

### 예시

```markdown
## [1.1.0] - 2026-04-01

### Added
- Kubernetes 가이드 추가
- Ansible 플레이북 예제

### Changed
- Docker 가이드 업데이트 (Docker Compose v2)

### Fixed
- Bash trap 가이드 오타 수정
```

---

[1.1.0]: https://github.com/siasia86/system-engineering-resources/releases/tag/v1.1.0
[1.0.0]: https://github.com/siasia86/system-engineering-resources/releases/tag/v1.0.0

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-03-25

© 2026 siasia86. Licensed under CC BY 4.0.
