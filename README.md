# 시스템 엔지니어링 학습 자료 모음

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Linux, 네트워크, 보안, 프로그래밍 등 시스템 엔지니어링 관련 학습 자료를 정리한 저장소입니다.

## 목차

### 1. [Linux 디버깅 도구](01_debuggin_linux/)
Linux 시스템 디버깅 및 성능 분석 도구 가이드
- `strace` - 시스템 콜 추적
- `ltrace` - 라이브러리 호출 추적
- `gdb` - GNU 디버거
- `perf` - 성능 분석
- `valgrind` - 메모리 디버깅
- `lsof` - 열린 파일 확인
- `iotop` - I/O 모니터링
- `tcpdump` - 네트워크 패킷 캡처

### 2. [기본 Linux 명령어](02_basic_linux_command/)
자주 사용하는 Linux 명령어 및 스크립팅
- Bash 수학 연산
- Bash trap 가이드
- IP 주소 체계
- 리소스 모니터링
- tcpdump 예제
- Vim 사용법

### 3. [고급 Linux](03_advanced_linux/)
고급 Linux 시스템 관리 및 성능 튜닝
- `bpftrace` - eBPF 기반 추적

### 4. [오픈소스 도구](04_opensource/)
컨테이너 및 오픈소스 도구 활용
- Docker & Docker Compose
- n8n (워크플로우 자동화)
- 컨테이너 아키텍처

### 5. [컴퓨터 과학](05_computer_science/)
네트워크 및 프로토콜 이론
- TCP 상태 다이어그램
- 패킷 분석
- 네트워크 헤더 구조
- HTTP 메서드

### 6. [보안](06_security/)
시스템 보안 및 DDoS 방어
- DDoS 방어 아키텍처

### 7. [시스템 엔지니어링](07_system_enginner/)
시스템 엔지니어 로드맵 및 프로그래밍 언어 비교
- SE/SRE 로드맵
- 프로그래밍 언어 비교 (C, C++, C#, Go, Python, Bash)

### 8. [Python](11_python/)
Python 프로그래밍 가이드
- 클래스 사용법
- 로깅
- Magic Attributes
- Print 함수

### 9. [라이선스 가이드](license_guide.md)
오픈소스 라이선스 선택 및 사용 가이드

---

## 빠른 시작

### 추천 학습 순서

#### 초급 (Linux 입문)
1. [기본 Linux 명령어](02_basic_linux_command/)
2. [Vim 사용법](02_basic_linux_command/vim.md)
3. [IP 주소 체계](02_basic_linux_command/ip_addressing_guide.md)

#### 중급 (시스템 관리)
1. [Linux 디버깅 도구](01_debuggin_linux/)
2. [Docker & 컨테이너](04_opensource/)
3. [네트워크 기초](05_computer_science/)

#### 고급 (성능 최적화 & 보안)
1. [고급 Linux](03_advanced_linux/)
2. [보안](06_security/)
3. [시스템 엔지니어 로드맵](07_system_enginner/)

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

## 기여하기

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
- 단어 구분은 언더스코어(`_`)
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

- **작성자**: sj_del
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

---

**마지막 업데이트**: 2026-03-11

© 2026 sj_del. Licensed under CC BY 4.0.
