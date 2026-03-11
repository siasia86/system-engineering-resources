# Contributing to System Engineering Learning Resources

이 프로젝트에 기여해주셔서 감사합니다! 

## 기여 방법

### 1. Fork & Clone

```bash
# Fork this repository on GitHub
# Then clone your fork
git clone https://github.com/siasia86/repo.git
cd repo
```

### 2. 브랜치 생성

```bash
git checkout -b feature/your-feature-name
```

### 3. 변경 사항 작성

#### 문서 작성 가이드

**파일명 규칙:**
- 소문자 사용
- 단어 구분은 언더스코어 (`_`)
- 예: `bash_trap_guide.md`

**문서 구조:**
```markdown
# 제목

간단한 설명

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

## 참고 자료
- [링크](URL)
```

**코드 예제:**
- 실행 가능한 코드 작성
- 주석으로 설명 추가
- 출력 결과 포함 (가능한 경우)

### 4. 커밋

```bash
git add .
git commit -m "Add: bash trap guide"
```

**커밋 메시지 규칙:**
- `Add:` - 새 문서 추가
- `Update:` - 기존 문서 수정
- `Fix:` - 오타 또는 에러 수정
- `Docs:` - README 등 문서 수정

### 5. Push & Pull Request

```bash
git push origin feature/your-feature-name
```

GitHub에서 Pull Request 생성

---

## 기여 가이드라인

### 좋은 기여

- 명확하고 이해하기 쉬운 설명
- 실행 가능한 예제 코드
- 실전에서 유용한 팁
- 트러블슈팅 섹션
- 참고 자료 링크

### 피해야 할 것

- 복사-붙여넣기만 한 내용
- 실행되지 않는 코드
- 너무 짧거나 불완전한 설명
- 출처 없는 내용

---

## 문서 카테고리

새 문서를 추가할 때 적절한 디렉토리를 선택하세요:

- `01_debuggin_linux/` - Linux 디버깅 도구
- `02_basic_linux_command/` - 기본 명령어 및 스크립팅
- `03_advanced_linux/` - 고급 시스템 관리
- `04_opensource/` - 오픈소스 도구
- `05_computer_science/` - 네트워크 및 프로토콜
- `06_security/` - 보안
- `07_system_enginner/` - 시스템 엔지니어링
- `11_python/` - Python 프로그래밍

새 카테고리가 필요하면 Issue를 열어주세요.

---

## 라이선스 동의

기여함으로써 다음에 동의합니다:

- 문서는 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 라이선스를 따릅니다
- 코드 예제는 [MIT License](https://opensource.org/licenses/MIT)를 따릅니다

---

## 질문이 있나요?

- Issue를 열어주세요
- 또는 이메일: siasia.linux@gmail.com

---

감사합니다! 
