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

---

## Branch 규칙

| 리포지토리                              | 사용 branch | 금지 branch        |
|-----------------------------------------|-------------|--------------------|
| `/root/32_system-engineering-resources` | `yunli`     | `main`, `kiro`     |
| `/root/sj_del`                          | `yunli`     | `main`, `kiro` 외 |

- commit/push 전 반드시 현재 branch 확인
- `main` branch push 절대 금지
- `git add .` 지양 — 변경 파일 명시적 지정

## Commit & Push 절차

작업 완료 후 아래 순서를 반드시 따릅니다.

```
1. branch 확인
   git -C <repo> branch --show-current
   → yunli 아니면: git -C <repo> checkout yunli

2. 변경 파일 확인
   git -C <repo> status --short
   → 의도치 않은 파일 포함 여부 검토

3. Markdown 검사 0건 확인 (변경 .md 파일에 한해)
   BASE=/root/32_system-engineering-resources
   sudo python3 $BASE/md-style-check.py <path>
   sudo python3 $BASE/md-heading-check.py <path>
   sudo python3 $BASE/md-link-check.py <path>

4. stage (명시적 파일 지정)
   git -C <repo> add <file1> <file2> ...

5. commit
   git -C <repo> commit -m "<type>: <한글 설명>"

6. push
   git -C <repo> push origin yunli

7. 결과 확인
   git -C <repo> log --oneline -3
```

## 금지 사항

```
git push origin main          ❌
git push origin HEAD          ❌ (현재 branch가 main일 경우)
git add .                     ❌ (비관련 파일 혼입 위험)
git commit --amend --no-edit  ❌ (push된 커밋은 amend 금지)
git push --force              ❌ (명시적 허가 없으면 금지)
```
