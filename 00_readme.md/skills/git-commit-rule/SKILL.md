---
name: git-commit-rule
description: Defines git commit message format and conventions. Use when committing changes — Korean description, type prefix, 50 chars max, no period.
---

# Git 커밋 메시지 규칙

## 형식

```
<타입>: <설명>
```

## 타입

| 타입       | 용도                            |
|------------|---------------------------------|
| `docs`     | 문서 추가/수정                  |
| `fix`      | 오타, 깨진 링크, 버그 수정      |
| `feat`     | 새 기능 (Actions, 스크립트 등)  |
| `refactor` | 구조 변경 (디렉토리 이동/정리)  |
| `chore`    | 설정, 유지보수                  |
| `style`    | 포맷팅, 배지, 푸터 등 외형 변경 |

## 규칙
- 한글 설명 사용
- 50자 이내로 간결하게 작성
- 마침표 생략
- 여러 변경 시 가장 주요한 타입 사용

## 예시
```
docs: strace 가이드 추가
fix: README.md 디렉토리 경로 오타 수정
feat: GitHub Actions 날짜 자동 갱신 workflow 추가
refactor: 04/07 디렉토리 번호 swap
chore: .gitignore 업데이트
style: 전체 README 푸터 배지 통일
```
