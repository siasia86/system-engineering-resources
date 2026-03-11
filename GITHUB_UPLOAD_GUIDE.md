# GitHub 업로드 가이드

이 저장소를 GitHub에 업로드하는 방법입니다.

## 업로드 전 체크리스트

- [ ] 민감한 정보 제거 확인 (IP, 패스워드, 회사 정보)
- [ ] `.gitignore` 확인
- [ ] 모든 README.md 파일 확인
- [ ] LICENSE.md 확인
- [ ] 개인 정보 수정 (이름, 이메일)

---

## GitHub 업로드 방법

### 1. GitHub에서 저장소 생성

1. GitHub 로그인
2. 우측 상단 `+` → `New repository`
3. Repository name: `system-engineering-resources` (또는 원하는 이름)
4. Description: `System Engineering Learning Resources`
5. Public 선택
6. **라이선스 선택 안함** (이미 LICENSE.md 있음)
7. `Create repository`

### 2. 로컬에서 Git 초기화

```bash
cd /home/sjyun/32_readme.md

# Git 초기화
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: System Engineering Learning Resources"
```

### 3. GitHub에 푸시

```bash
# 원격 저장소 연결
git remote add origin https://github.com/siasia86/system-engineering-resources.git

# 푸시
git branch -M main
git push -u origin main
```

---

## 업로드 전 수정 사항

### 1. 개인 정보 수정

다음 파일들에서 `sj_del`, `siasia.linux@gmail.com`, `@siasia86`을 실제 정보로 변경:

```bash
# 일괄 변경
find . -name "*.md" -type f -exec sed -i 's/\[Your Name\]/홍길동/g' {} +
find . -name "*.md" -type f -exec sed -i 's/siasia.linux@gmail.com/your-real-email@example.com/g' {} +
find . -name "*.md" -type f -exec sed -i 's/@siasia86/@your-github-username/g' {} +
```

**수정할 파일:**
- `README.md`
- `CONTRIBUTING.md`
- `LICENSE.md`
- 각 디렉토리의 `README.md`

### 2. 민감한 정보 확인

```bash
# IP 주소 검색
grep -r "10\." --include="*.md" .
grep -r "192\.168\." --include="*.md" .

# 패스워드 검색
grep -ri "password" --include="*.md" .
grep -ri "passwd" --include="*.md" .

# 회사 정보 검색
grep -ri "siasia" --include="*.md" .
```

### 3. 불필요한 디렉토리 제거

```bash
# .gitignore에 이미 포함되어 있지만, 완전히 삭제하려면:
rm -rf 51_siasia/
rm -rf 33_sjyun_32_readme.md/
rm -rf 00_readme.md/
rm -rf 99_ETC/
```

---

## 업로드 후 작업

### 1. GitHub 저장소 설정

**About 섹션 설정:**
1. 저장소 페이지에서 우측 상단 ⚙️ (Settings) 클릭
2. Description 추가: `System Engineering Learning Resources - Linux, Network, Security, Programming`
3. Website 추가 (있다면)
4. Topics 추가: `linux`, `networking`, `security`, `devops`, `sre`, `system-engineering`

**README 배지 추가:**

루트 `README.md`에 다음 추가:

```markdown
![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
```

### 2. GitHub Pages 활성화 (선택사항)

1. Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main` / `/ (root)`
4. Save

이제 `https://siasia86.github.io/system-engineering-resources/`에서 접근 가능

### 3. 소셜 미디어 공유

- LinkedIn, Twitter 등에 공유
- 관련 커뮤니티에 소개 (Reddit, 개발자 커뮤니티)

---

## 유지보수 팁

### 정기적인 업데이트

```bash
# 변경 사항 확인
git status

# 변경 사항 추가
git add .

# 커밋
git commit -m "Update: bash trap guide"

# 푸시
git push origin main
```

### 이슈 및 PR 관리

- Issue 템플릿 생성 (`.github/ISSUE_TEMPLATE/`)
- PR 템플릿 생성 (`.github/PULL_REQUEST_TEMPLATE.md`)

### GitHub Actions (선택사항)

마크다운 링크 체크, 맞춤법 검사 등 자동화

```yaml
# .github/workflows/markdown-check.yml
name: Markdown Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check Markdown links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
```

---

## 참고 자료

- [GitHub Docs](https://docs.github.com/)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Pages](https://pages.github.com/)

---

## 문제 해결

### 푸시 실패 시

```bash
# 원격 저장소 확인
git remote -v

# 원격 저장소 재설정
git remote remove origin
git remote add origin https://github.com/siasia86/repo.git

# 강제 푸시 (주의!)
git push -f origin main
```

### 대용량 파일 경고

```bash
# 100MB 이상 파일 찾기
find . -type f -size +100M

# Git LFS 사용 (필요시)
git lfs install
git lfs track "*.zip"
git add .gitattributes
```

---

**준비 완료!** 

이제 GitHub에 업로드할 준비가 되었습니다!
