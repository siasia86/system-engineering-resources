---
name: readme-template
description: Defines the mandatory footer template for all .md files — GitHub badges, dates, and license. Use when creating or modifying any markdown document.
---

# README 템플릿 규칙

## 모든 .md 파일 생성/수정 시 필수 푸터

모든 .md 파일 맨 아래에 반드시 다음 형식을 포함할 것:

```markdown
---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---
**작성일**: YYYY-MM-DD

**마지막 업데이트**: YYYY-MM-DD

© 2026 siasia86. Licensed under CC BY 4.0.
```

## 규칙
- `YYYY-MM-DD`는 작성/수정 당일 날짜로 기입
- README.md, CHANGELOG.md, LICENSE.md, CONTRIBUTING.md 및 모든 .md 파일에 동일 푸터 적용
- GitHub Actions가 main push 시 날짜를 자동 갱신함
