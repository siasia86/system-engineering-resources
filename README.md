# 시스템 엔지니어링 학습 자료 모음

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Linux, 네트워크, 보안, 프로그래밍 등 시스템 엔지니어링 관련 학습 자료를 정리한 저장소입니다.

## 목차

### 1. [설치 가이드](01_install/)
설치 및 환경 구성 가이드
- [Ansible 기초 가이드](01_install/ansible_basic_guide.md)
- [Ansible 설치 및 팀 운영 가이드](01_install/ansible_install_and_team_operation.md)

### 2. [기본 Linux 명령어](02_basic_linux_command/)
자주 사용하는 Linux 명령어 및 스크립팅
- [Bash 수학 연산](02_basic_linux_command/bash_math.md)
- [Bash trap 가이드](02_basic_linux_command/bash_trap_complete_guide.md)
- [Root 패스워드 복구](02_basic_linux_command/root_password_recovery.md)
- [Vim 사용법](02_basic_linux_command/vim.md)

### 3. [고급 Linux](03_advanced_linux/)
고급 Linux 시스템 관리 및 성능 튜닝
- [bpftrace - eBPF 기반 추적](03_advanced_linux/bpftrace.md)

### 4. [시스템 엔지니어링](04_system_engineer/)
시스템 엔지니어를 위한 로드맵부터 실무 운영, 도구 비교, AI 활용까지 정리한 문서 모음
- [SE 로드맵](04_system_engineer/se_roadmap.md)
- [SRE 로드맵](04_system_engineer/sre_roadmap.md)
- [SE 완전 로드맵 - 프로그래밍 언어](04_system_engineer/se_complete_roadmap_programming_languages.md)
- [언어 비교 (C, C++, C#, Go, Python, Bash)](04_system_engineer/c_cpp_csharp_go_python_bash_comparison.md)
- [게임 인프라 KPI](04_system_engineer/game-infra-kpi-presentation.md)
- [리소스 모니터링](04_system_engineer/resource_utilization_monitoring.md)
- [백업 도구 비교](04_system_engineer/backup_tools_comparison.md)
- [인프라 Monorepo](04_system_engineer/infra_monorepo_and_boilerplate.md)
- [ASN 및 DDoS 대응](04_system_engineer/asn_and_cloudflare_ddos.md)
- [CDN, Proxy, Origin IP](04_system_engineer/cdn-proxy-origin-ip.md)
- [ADR 가이드](04_system_engineer/adr_guide.md)
- [AI 개발 요청 템플릿](04_system_engineer/ai_development_request_template.md)
- [AI Markdown 디자인 패턴](04_system_engineer/ai_markdown_design_patterns.md)
- [Kiro CLI 레퍼런스](04_system_engineer/kiro_cli_command_reference.md)

### 5. [컴퓨터 과학](05_computer_science/)
네트워크 및 프로토콜 이론
- [IP 주소 체계](05_computer_science/ip_addressing_guide.md)
- [TCP 상태 전이](05_computer_science/TCP_state.md)
- [패킷 분석](05_computer_science/packet_analysis.md)
- [tcpdump 예제](05_computer_science/tcpdump_examples.md)
- [네트워크 헤더 구조](05_computer_science/network_headers.md)
- [HTTP 메서드](05_computer_science/http_methods.md)

### 6. [보안](06_security/)
시스템 보안 및 DDoS 방어
- [DDoS 방어 아키텍처](06_security/01_ddos_defense_architecture.md)

### 7. [오픈소스 도구](07_opensource/)
컨테이너 및 오픈소스 도구 활용
- [Docker & Docker Compose](07_opensource/01_docker_docker_compose_cheatsheet.md)
- [n8n + MySQL Docker Compose](07_opensource/02_n8n_docker_cheatsheet.md)
- [컨테이너 아키텍처](07_opensource/03_container_architecture.md)
- [Percona XtraBackup 가이드](07_opensource/04_percona-xtrabackup-guide.md)
- [Ansible vs Jenkins 비교](07_opensource/ansible_vs_jenkins.md)

### 8. [Linux 디버깅 도구](08_debugging_linux/)
Linux 시스템 디버깅 및 성능 분석 도구 가이드
- [strace - 시스템 콜 추적](08_debugging_linux/strace.md)
- [ltrace - 라이브러리 호출 추적](08_debugging_linux/ltrace.md)
- [gdb - GNU 디버거](08_debugging_linux/gdb.md)
- [perf - 성능 분석](08_debugging_linux/perf.md)
- [valgrind - 메모리 디버깅](08_debugging_linux/valgrind.md)
- [lsof - 열린 파일 확인](08_debugging_linux/lsof.md)
- [iotop - I/O 모니터링](08_debugging_linux/iotop.md)
- [tcpdump - 네트워크 패킷 캡처](08_debugging_linux/tcpdump.md)

### 9. [Python](11_python/)
Python 프로그래밍 가이드
- [클래스 튜토리얼](11_python/python_class.md)
- [클래스 구성 요소](11_python/python_class_components.md)
- [상속](11_python/python_inheritance.md)
- [함수](11_python/python_functions.md)
- [제어문](11_python/python_control_flow.md)
- [예외 처리](11_python/python_exceptions.md)
- [데코레이터](11_python/python_decorators.md)
- [제너레이터](11_python/python_generators.md)
- [컴프리헨션](11_python/python_comprehensions.md)
- [리스트 컴프리헨션](11_python/python_list_comprehension.md)
- [컨텍스트 매니저](11_python/python_context_managers.md)
- [파일 입출력](11_python/python_file_io.md)
- [패키지](11_python/python_packages.md)
- [로깅](11_python/python_logging.md)
- [모듈 속성](11_python/python_magic_attributes.md)
- [print() 함수](11_python/python_print.md)

### 10. [라이선스 가이드](license_guide.md)
오픈소스 라이선스 선택 및 사용 가이드

---

## 빠른 시작

### 추천 학습 순서

#### 초급 (Linux 입문)
1. [기본 Linux 명령어](02_basic_linux_command/)
2. [Vim 사용법](02_basic_linux_command/vim.md)
3. [IP 주소 체계](05_computer_science/ip_addressing_guide.md)

#### 중급 (시스템 관리)
1. [Linux 디버깅 도구](08_debugging_linux/)
2. [Docker & 컨테이너](07_opensource/)
3. [네트워크 기초](05_computer_science/)

#### 고급 (성능 최적화 & 보안)
1. [고급 Linux](03_advanced_linux/)
2. [보안](06_security/)
3. [시스템 엔지니어 로드맵](04_system_engineer/)

---

## 사용 방법

### 특정 주제 찾기

```bash
# 예: strace 관련 문서 찾기
find . -name "*strace*"

# 예: 네트워크 관련 문서 찾기
grep -r "network" --include="*.md"
```

### 로컬에서 보기

```bash
# 저장소 클론
git clone https://github.com/siasia86/system-engineering-resources.git
cd repo

# 마크다운 뷰어로 보기 (VS Code 추천)
code .
```

---

## 기여하기 (예정 / 2026-03-25 지원하지 않음)

이 저장소는 학습 자료 공유를 목적으로 합니다.

### 기여 방법 
1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingGuide`)
3. Commit your changes (`git commit -m 'Add some AmazingGuide'`)
4. Push to the branch (`git push origin feature/AmazingGuide`)
5. Open a Pull Request

### 기여 가이드라인
- 명확하고 이해하기 쉬운 설명
- 실행 가능한 예제 코드 포함
- 한글 또는 영어 (혼용 가능)
- 마크다운 포맷 준수

---

## 문서 작성 가이드

### 문서 구조
```markdown
# 제목

## 목차
1. 개요
2. 설치/설정
3. 기본 사용법
4. 고급 기능
5. 실전 예제
6. 트러블슈팅
7. 참고 자료

## 개요
...

## 예제
\`\`\`bash
# 실행 가능한 코드
\`\`\`
```

### 파일명 규칙
- 소문자 사용
- 단어 구분은 언더스코어(`_`) (권장)
- 예: `bash_trap_guide.md`

---

## License

### 문서 라이선스
이 저장소의 모든 문서는 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 라이선스를 따릅니다.

**출처를 표시하면 자유롭게:**
- 복사 및 재배포
- 수정 및 변형
- 상업적 사용

### 코드 예제 라이선스
문서 내 코드 예제는 [MIT License](https://opensource.org/licenses/MIT)를 따릅니다.

자세한 내용은 [라이선스 가이드](license_guide.md)를 참조하세요.

---

## Contact

- **작성자**: siasia86
- **이메일**: siasia.linux@gmail.com
- **GitHub**: [@siasia86](https://github.com/siasia86)

---

## Acknowledgments

이 자료는 다양한 오픈소스 프로젝트와 커뮤니티의 도움을 받아 작성되었습니다.

- Linux Documentation Project
- ArchWiki
- Stack Overflow Community
- 그 외 많은 오픈소스 기여자들

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-14

© 2026 siasia86. Licensed under CC BY 4.0.


