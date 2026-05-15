# Git 실무 가이드

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 기본 개념](#1-기본-개념) / [2. Stage와 Commit](#2-stage와-commit)                                                                                             |
| 비교 | [3. diff — 변경 내용 확인](#3-diff--변경-내용-확인) / [4. log — 히스토리 조회](#4-log--히스토리-조회)                                                             |
| 원격 | [5. fetch와 pull](#5-fetch와-pull) / [6. remote 관리](#6-remote-관리)                                                                                             |
| 고급 | [7. stash](#7-stash) / [8. rebase vs merge](#8-rebase-vs-merge) / [9. 실무 팁](#9-실무-팁) / [10. safe.directory](#10-safedirectory) |

---

## 1. 기본 개념

### 작업 영역 구조

```
Working Directory    Staging Area (Index)    Local Repo         Remote Repo
      │                      │                   │                   │
      │── git add ──────────>│                   │                   │
      │                      │── git commit ────>│                   │
      │                      │                   │── git push ──────>│
      │<────────────────────────── git checkout ─┤                   │
      │<──────────────────────────────────────────── git pull ───────┤
      │                      │                   │<── git fetch ─────┤
```

### 파일 상태 전이

```
Untracked --> Staged --> Committed --> Modified
    │            ^           │              │
    │            │           v              │
    │         git add    git commit      git add
    │                                       │
    └──────────── git rm --cached <─────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Stage와 Commit

### Staging

```bash
# 특정 파일 스테이징
git add file.txt

# 현재 디렉토리 전체
git add .

# 변경된 파일만 (Untracked 제외)
git add -u

# 대화형 스테이징 (헝크 단위 선택)
git add -p

# 스테이징 취소 (Working Directory 유지)
git restore --staged file.txt
git reset HEAD file.txt        # 구버전 방식
```

### Commit

```bash
# 기본 커밋
git commit -m "feat: add user login"

# 스테이징 + 커밋 (Untracked 제외)
git commit -am "fix: correct typo"

# 마지막 커밋 수정 (미푸시 상태에서만)
git commit --amend --no-edit          # 메시지 유지, 내용만 수정
git commit --amend -m "new message"   # 메시지 변경

# 빈 커밋 (CI 트리거 등)
git commit --allow-empty -m "chore: trigger CI"
```

### 상태 확인

```bash
git status          # 전체 상태
git status -s       # 간략 표시
```

```
M  file1.txt    # Staged (수정)
 M file2.txt    # Modified (미스테이징)
?? file3.txt    # Untracked
A  file4.txt    # Staged (신규)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. diff — 변경 내용 확인

### 비교 대상별 명령어

| 비교 대상                              | 명령어                                      |
|----------------------------------------|---------------------------------------------|
| Working Directory vs Staging           | `git diff`                                  |
| Staging vs 마지막 Commit               | `git diff --staged`                         |
| Working Directory vs 마지막 Commit     | `git diff HEAD`                             |
| 특정 커밋 간 비교                      | `git diff <commit1> <commit2>`              |
| 로컬 브랜치 vs 원격 브랜치             | `git diff main origin/main`                 |
| 브랜치 간 비교                         | `git diff feature/login main`               |
| 특정 파일만                            | `git diff HEAD -- file.txt`                 |

### 로컬 vs Remote 차이 확인 (커밋 전)

```bash
# 1. 원격 최신 정보 가져오기 (merge 없이)
git fetch origin

# 2. 로컬과 원격 브랜치 diff
git diff main origin/main

# 3. 파일 목록만 확인
git diff --name-only main origin/main

# 4. 통계 요약
git diff --stat main origin/main
```

```
 src/app.py   | 12 ++++++------
 src/utils.py |  3 ++-
 2 files changed, 9 insertions(+), 6 deletions(-)
```

### diff 비교 대상 요약

| 명령어 | 비교 대상 | 설명 |
|--------|-----------|------|
| `git diff` | Working Dir vs Staging | `git add` 전 변경사항 |
| `git diff --staged` | Staging vs 마지막 Commit | `git add` 후 커밋 전 변경사항 |
| `git diff HEAD` | Working Dir vs 마지막 Commit | 스테이징 여부 무관 전체 변경사항 |
| `git diff origin/main` | 로컬 브랜치 vs 원격 브랜치 | 로컬이 원격보다 얼마나 앞서 있는지 |

```bash
# -C 옵션: 해당 경로에서 git 명령 실행 (cd 없이)
git -C /path/to/repo diff origin/main

# 위 두 명령은 동일
cd /path/to/repo && git diff origin/main
```


### 유용한 옵션

```bash
# 공백 변경 무시
git diff -w

# 단어 단위 diff
git diff --word-diff

# 변경된 파일 목록만
git diff --name-status HEAD~3 HEAD
```

```
M       src/app.py
A       src/new_feature.py
D       src/old_module.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. log — 히스토리 조회

### 기본 조회

```bash
# 기본 로그
git log

# 한 줄 요약
git log --oneline

# 그래프 + 브랜치 시각화
git log --oneline --graph --all

# 최근 N개
git log -5

# 특정 파일 히스토리
git log --oneline -- src/app.py

# 특정 기간
git log --since="2026-01-01" --until="2026-04-30"

# 특정 작성자
git log --author="sjyun"

# 커밋 메시지 검색
git log --grep="fix"
```

### 포맷 커스터마이징

```bash
git log --pretty=format:"%h %ad %s [%an]" --date=short
```

```
a1b2c3d 2026-04-30 feat: add user login [sjyun]
d4e5f6g 2026-04-29 fix: correct null check [sjyun]
```

### 로컬에만 있는 커밋 확인

```bash
# origin/main에 없고 로컬 main에만 있는 커밋
git log origin/main..main --oneline

# 반대: 원격에만 있고 로컬에 없는 커밋
git log main..origin/main --oneline
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. fetch와 pull

### fetch vs pull 비교

| 구분          | `git fetch`                          | `git pull`                            |
|---------------|--------------------------------------|---------------------------------------|
| 동작          | 원격 정보만 가져옴 (merge 없음)      | fetch + merge (또는 rebase)           |
| Working Dir   | 변경 없음                            | 변경됨                                |
| 안전성        | 높음 (검토 후 merge 가능)            | 낮음 (즉시 반영)                      |
| 권장 상황     | 변경 내용 확인 후 신중하게 반영할 때 | 단순 동기화, 충돌 없을 때             |

### fetch 활용 패턴

```bash
# 원격 정보 갱신
git fetch origin

# 원격 브랜치 목록 확인
git branch -r

# 원격과 차이 확인 후 merge 결정
git diff main origin/main
git log main..origin/main --oneline

# 확인 후 merge
git merge origin/main

# 또는 rebase로 깔끔하게 반영
git rebase origin/main
```

### pull 옵션

```bash
# merge 방식 (기본)
git pull origin main

# rebase 방식 (히스토리 선형 유지)
git pull --rebase origin main

# fast-forward만 허용 (merge commit 생성 안 함)
git pull --ff-only origin main
```

### 원격 삭제된 브랜치 정리

```bash
# 원격에서 삭제된 브랜치를 로컬 추적 목록에서 제거
git fetch --prune
git fetch -p
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. remote 관리

```bash
# 원격 목록 확인
git remote -v

# 원격 추가
git remote add origin https://github.com/user/repo.git

# 원격 URL 변경
git remote set-url origin https://github.com/user/new-repo.git

# 원격 제거
git remote remove origin

# 원격 브랜치 상세 정보
git remote show origin
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. stash

작업 중인 변경사항을 임시 저장하고 Working Directory를 깨끗하게 만든다.

```bash
# 저장 (Staged + Modified)
git stash

# 메시지 포함
git stash push -m "WIP: login feature"

# Untracked 파일도 포함
git stash push -u

# 목록 확인
git stash list
```

```
stash@{0}: WIP: login feature
stash@{1}: On main: hotfix 전 임시 저장
```

```bash
# 적용 (stash 유지)
git stash apply stash@{0}

# 적용 + 삭제
git stash pop

# 특정 stash 삭제
git stash drop stash@{1}

# 전체 삭제
git stash clear

# stash 내용 확인
git stash show -p stash@{0}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. rebase vs merge

### 히스토리 비교

```
-- merge --
main:    A---B---C---M
                    /
feature:     D---E

-- rebase --
main:    A---B---C---D'---E'
feature:             D'---E'
```

| 구분          | merge                          | rebase                          |
|---------------|--------------------------------|---------------------------------|
| 히스토리      | 분기 구조 유지 (merge commit)  | 선형 히스토리                   |
| 충돌 해결     | 1회                            | 커밋마다 발생 가능              |
| 협업 안전성   | 높음 (원본 커밋 유지)          | 낮음 (공유 브랜치에 사용 금지)  |
| 권장 상황     | 팀 공유 브랜치, PR merge       | 로컬 정리, feature → main 전    |

```bash
# merge
git checkout main
git merge feature/login

# rebase (로컬 feature 브랜치 정리)
git checkout feature/login
git rebase main

# 충돌 해결 후 계속
git rebase --continue

# rebase 취소
git rebase --abort

# 대화형 rebase (커밋 squash, 순서 변경)
git rebase -i HEAD~3
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 실무 팁

### Tip 1: 커밋 전 체크리스트

```bash
# 1. 변경 파일 확인
git status -s

# 2. 내용 검토
git diff --staged

# 3. 로컬 vs 원격 차이 확인
git fetch origin && git diff main origin/main --stat

# 4. 커밋
git commit -m "feat: ..."
```

### Tip 2: 실수한 커밋 되돌리기

```bash
# 마지막 커밋 취소 (변경사항 유지, 미푸시 상태)
git reset --soft HEAD~1

# 마지막 커밋 취소 (변경사항도 삭제, 주의)
git reset --hard HEAD~1

# 이미 푸시한 커밋 되돌리기 (revert로 새 커밋 생성)
git revert HEAD
git revert <commit-hash>
```

### Tip 3: 특정 파일만 이전 버전으로 복구

```bash
# 특정 커밋 시점의 파일로 복구
git checkout <commit-hash> -- src/app.py

# 마지막 커밋 상태로 복구
git restore src/app.py
```

### Tip 4: 브랜치 관리

```bash
# 이미 merge된 브랜치 일괄 삭제
git branch --merged main | grep -v "main\|master\|\*" | xargs git branch -d

# 원격 브랜치 삭제
git push origin --delete feature/old-branch

# 로컬 브랜치를 원격과 동기화
git fetch --prune
```

### Tip 5: alias 설정

```bash
git config --global alias.st "status -s"
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.df "diff --staged"
git config --global alias.undo "reset --soft HEAD~1"
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. safe.directory

Git 2.35.2부터 추가된 **소유권 보안 검사** 설정입니다.
현재 사용자와 `.git` 디렉토리 소유자가 다르면 아래 오류가 발생합니다.

```
fatal: detected dubious ownership in repository at '/path/to/repo'
To add an exception for this directory, call:
    git config --global safe.directory /path/to/repo
```

### 발생 상황

| 상황                                        | 예시                              |
|---------------------------------------------|-----------------------------------|
| root로 clone한 repo를 일반 유저가 접근      | sudo git clone 후 일반 유저 사용  |
| Docker 컨테이너 내 마운트된 디렉토리        | CI/CD 파이프라인                  |
| NFS/공유 마운트 디렉토리                    | 팀 공유 서버                      |

### 해결 방법

```bash
# 특정 경로만 허용 (권장)
git config --global safe.directory /root/32_system-engineering-resources

# 모든 경로 허용 (보안 주의, CI 환경에서만 사용)
git config --global safe.directory '*'

# 설정 확인
git config --global --get-all safe.directory

# 설정 파일 위치
cat ~/.gitconfig
```

### 근본적 해결: 소유권 변경

```bash
# 디렉토리 소유자를 현재 유저로 변경
sudo chown -R $(whoami):$(whoami) /path/to/repo
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Git Documentation: [git-scm.com/doc](https://git-scm.com/doc) — ★★★☆☆
- Pro Git Book: [git-scm.com/book](https://git-scm.com/book/ko/v2) — ★★★★☆
- Git safe.directory: [git-scm.com/docs](https://git-scm.com/docs/git-config#Documentation/git-config.txt-safedirectory) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-30

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
