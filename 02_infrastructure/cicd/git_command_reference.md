# Git 명령어 실무 참조
<!-- reference: _reference/git_official_notes.md -->

Git 저장소의 설정, 브랜치, 원격 저장소, 커밋, 병합, 복구 작업에서 자주 사용하는 명령어를 정리합니다. 신규 작업에서는 브랜치 변경에 `git switch`, 파일 복원에 `git restore`를 사용하고, 기존 문서와의 호환이 필요할 때 `git checkout`을 사용합니다.

## 목차

| 단계 | 섹션                                                                                                          |
|------|---------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 설정과 인증](#1-설정과-인증) / [2. 저장소 생성과 원격 설정](#2-저장소-생성과-원격-설정)                   |
| 작업 | [3. 변경사항 스테이징과 커밋](#3-변경사항-스테이징과-커밋) / [4. 브랜치 관리](#4-브랜치-관리)                 |
| 원격 | [5. 원격 저장소와 원격 브랜치](#5-원격-저장소와-원격-브랜치) / [6. 원격 동기화와 병합](#6-원격-동기화와-병합) |
| 복구 | [7. 복구와 정리](#7-복구와-정리) / [8. 실무 이전 절차](#8-실무-이전-절차)                                     |

---

## 1. 설정과 인증

### Git 설정 확인

```bash
# 현재 저장소의 설정 목록
git config --list

# 설정 파일 위치 포함
git config --list --show-origin

# 설정 범위와 설정 파일 위치 포함
git config --list --show-origin --show-scope

# 사용자 정보 확인
git config user.name
git config user.email
```

설정 범위는 `--system`, `--global`, `--local` 순서로 적용되며, 더 좁은 범위의 설정이 우선합니다.

```bash
# 모든 저장소에 적용
git config --global user.name "user_name"
git config --global user.email "user@example.com"

# 현재 저장소에만 적용
git config --local user.name "user_name"
git config --local user.email "user@example.com"
```

### Credential 저장

```bash
# 현재 저장소에 Credential 저장
git config credential.helper store

# 모든 저장소에 Credential 저장
git config --global credential.helper store
```

`store` 방식은 Credential을 일반적으로 `~/.git-credentials`에 평문으로 저장합니다. 서버 운영 환경에서는 패스워드 저장보다 SSH 키, 운영체제 Credential Manager 또는 보안 Credential Helper 사용을 우선합니다.

```bash
# HTTPS 대신 SSH 원격 URL 사용
git remote set-url origin git@github.com:owner/repository.git
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 저장소 생성과 원격 설정

### 저장소 생성·복제

```bash
# 현재 디렉터리에 저장소 생성
git init

# 원격 저장소 복제
git clone git@github.com:owner/repository.git

# 지정한 디렉터리로 복제
git clone git@github.com:owner/repository.git repository
```

### 원격 저장소 관리

```bash
# 원격 저장소 목록과 URL 확인
git remote -v

# origin URL 확인
git remote get-url origin

# 원격 저장소 추가
git remote add upstream git@github.com:owner/repository.git

# 원격 URL 변경
git remote set-url origin git@github.com:owner/new-repository.git

# 원격 저장소 이름 변경
git remote rename origin github

# 원격 저장소 설정 삭제
git remote remove upstream
```

`origin`은 Git이 복제 시 자동으로 지정하는 원격 저장소 별칭입니다. GitHub를 의미하는 고정된 이름이 아니며, `upstream`, `backup`, `gitlab` 등으로 추가할 수 있습니다.

```bash
# 원본 프로젝트의 변경사항을 가져오는 원격 추가
git remote add upstream git@github.com:original-owner/repository.git

# 원본 프로젝트의 원격 참조 갱신
git fetch upstream
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 변경사항 스테이징과 커밋

### 상태와 변경 내용 확인

```bash
git status

git status --short

git diff
git diff --staged
git diff HEAD
```

| 명령어              | 비교 대상                  | 용도                   |
|---------------------|----------------------------|------------------------|
| `git diff`          | 작업 트리와 Staging Area   | `git add` 전 변경 확인 |
| `git diff --staged` | Staging Area와 마지막 커밋 | 커밋 예정 내용 검토    |
| `git diff HEAD`     | 작업 트리와 마지막 커밋    | 전체 변경사항 확인     |

### 스테이징과 커밋

```bash
# 특정 파일 스테이징
git add file_name

# 변경·삭제·신규 파일 전체 스테이징
git add -A

# 스테이징된 변경사항 커밋
git commit -m "commit description"

# 마지막 커밋 수정: 미푸시 커밋에서만 사용
git commit --amend --no-edit
```

스테이징을 취소할 때는 다음 명령을 사용합니다. 파일의 작업 내용은 유지됩니다.

```bash
# 권장 방식
git restore --staged file_name

# 구형 방식
git reset HEAD file_name
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 브랜치 관리

### 브랜치 확인과 이동

```bash
# 로컬 브랜치 목록
git branch

# 원격 추적 브랜치 목록
git branch -r

# 로컬·원격 브랜치 전체 목록
git branch -a

# 브랜치 이동
git switch branch_name

# 신규 브랜치 생성 후 이동
git switch -c feature/login

# 원격 브랜치를 추적하는 로컬 브랜치 생성
git switch --track origin/branch_name
```

`git checkout`은 브랜치 이동, 커밋 이동, 파일 복원 기능을 함께 제공하는 기존 명령입니다. 신규 브랜치 작업에서는 기능이 분리된 `git switch`와 `git restore` 사용을 권장합니다.

```bash
# 기존 문법
git checkout branch_name
git checkout -b feature/login
git checkout -t origin/branch_name

# 특정 커밋으로 이동: detached HEAD 상태
git switch --detach <commit_id>
```

### 브랜치 이름 변경·삭제

```bash
# 현재 브랜치 이름 변경
git branch -m new_branch_name

# 지정한 브랜치 이름 변경
git branch -m old_branch_name new_branch_name

# 병합 완료 브랜치 삭제
git branch -d branch_name

# 병합 여부와 관계없이 강제 삭제
git branch -D branch_name
```

`-D`는 미병합 커밋을 참조하는 로컬 브랜치를 삭제할 수 있으므로, 삭제 전에 `git log branch_name`으로 이력을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 원격 저장소와 원격 브랜치

### 원격 브랜치로 push

```bash
# 현재 브랜치를 원격에 push
git push origin branch_name

# 최초 push와 추적 관계 설정
git push -u origin branch_name

# 모든 로컬 브랜치 push
git push origin --all

# 모든 태그 push
git push origin --tags
```

`-u` 또는 `--set-upstream`을 사용하면 이후 `git push`, `git pull`에서 원격과 브랜치를 생략할 수 있습니다.

```bash
git push -u origin yunli
git push
git pull
```

### 원격 브랜치 삭제

```bash
# 원격 브랜치 삭제
git push origin --delete branch_name

# 예시
git push origin --delete gh-pages
```

`--delete`의 하이픈은 ASCII 하이픈 2개여야 합니다. 유니코드 긴 대시(`—`)나 `-- delete`처럼 옵션을 분리한 표기는 사용할 수 없습니다.

```bash
# 원격에서 삭제된 브랜치 추적 정보 정리
git fetch --prune

# 원격 브랜치 목록 확인
git branch -r
```

로컬 브랜치 삭제와 원격 브랜치 삭제는 별도 작업입니다.

```bash
git branch -d branch_name
git push origin --delete branch_name
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 원격 동기화와 병합

### `fetch`와 `pull`

```bash
# 원격 참조만 갱신: 작업 트리와 현재 브랜치는 변경하지 않음
git fetch origin

# fetch 후 변경 내용 확인
git log HEAD..origin/branch_name --oneline
git diff HEAD origin/branch_name

# 원격 변경사항을 가져와 병합
git pull origin branch_name

# fetch 후 rebase 방식으로 반영
git pull --rebase origin branch_name

# fast-forward 가능한 경우에만 반영
git pull --ff-only origin branch_name
```

`git fetch`는 원격 참조만 갱신하고, `git pull`은 일반적으로 `fetch` 후 `merge` 또는 `rebase`를 수행합니다. 변경 내용을 확인해야 하는 운영 저장소에서는 `fetch` 후 검토하는 방식을 우선합니다.

### Merge

```bash
# 현재 브랜치에 대상 브랜치 병합
git merge branch_name

# 병합 중 충돌 해결을 포기하고 취소
git merge --abort

# 공통 조상이 없는 두 history를 의도적으로 병합
git merge master --allow-unrelated-histories
```

`refusing to merge unrelated histories` 오류는 두 브랜치에 공통 조상 커밋이 없다는 뜻입니다. 새 저장소의 `README.md` 초기 커밋과 기존 저장소의 전체 history를 합치는 경우처럼 의도가 명확할 때만 `--allow-unrelated-histories`를 사용합니다.

### 원격 추적 관계 설정

```bash
# 현재 브랜치의 upstream 설정
git branch --set-upstream-to=origin/branch_name branch_name

# 일반적으로는 push와 동시에 설정
git push -u origin branch_name
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 복구와 정리

### 커밋 되돌리기

```bash
# 마지막 커밋 취소: 변경사항은 Staging Area에 유지
git reset --soft HEAD~1

# 마지막 커밋 취소: 변경사항은 작업 트리에 유지
git reset HEAD~1

# 마지막 커밋과 추적 파일 변경사항 삭제
git reset --hard HEAD~1

# 이미 push한 커밋을 새 커밋으로 되돌림
git revert HEAD
```

공유 브랜치나 이미 원격에 push한 커밋은 `reset`보다 `git revert`를 우선합니다. `reset --hard`는 작업 파일 변경사항도 삭제할 수 있습니다.

### 파일 복원

```bash
# 특정 파일을 마지막 커밋 상태로 복원
git restore file_name

# 특정 커밋의 파일로 복원
git restore --source <commit_id> file_name

# Staging만 취소하고 작업 파일은 유지
git restore --staged file_name
```

### Untracked 파일 정리

```bash
# 삭제 대상 미리 확인
git clean -n
git clean -fdn

# Untracked 파일 삭제
git clean -f

# Untracked 파일과 디렉터리 삭제
git clean -fd

# Ignored 파일까지 삭제: 사용 전 대상 필수 확인
git clean -fdx
```

`git clean`으로 삭제한 파일은 일반적인 Git history나 reflog로 복구되지 않습니다. 먼저 `-n` 또는 `-fdn`으로 삭제 목록을 확인합니다.

### Reflog 확인

```bash
# HEAD 이동 이력 확인
git reflog

# 삭제·reset 전 커밋 확인
git log --oneline --all
```

`git reset --hard` 후에도 커밋 객체가 즉시 삭제되지 않았다면 `reflog`에서 이전 HEAD를 찾아 복구할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 이전 절차

### 기존 작업 디렉터리를 새 경로로 복사

`cp -a`는 작업 파일뿐 아니라 `.git` 디렉터리와 `.git/config`도 복사합니다. 따라서 Git history와 현재 remote 설정을 함께 보존합니다.

```bash
cp -a /path/to/source/. /path/to/destination/
```

복사 후 대상 저장소의 remote를 새 저장소로 변경합니다.

```bash
git -C /path/to/destination remote -v
git -C /path/to/destination remote set-url origin git@github.com:owner/new-repository.git
git -C /path/to/destination remote set-url --push origin git@github.com:owner/new-repository.git
```

### 전체 브랜치와 태그 이전

새 원격 저장소가 비어 있는지 확인한 뒤 실행합니다.

```bash
git -C /path/to/destination push --all origin
git -C /path/to/destination push --tags origin
```

`--all`과 `--tags`는 브랜치와 태그가 가리키는 커밋 history를 함께 전송합니다. 새 원격 저장소에 초기 `README.md` 커밋이 있으면 fast-forward가 거부될 수 있으므로, 바로 `--force`를 사용하지 말고 두 history를 병합할지 먼저 결정합니다.

### 복사·이전 검증

```bash
# 현재 HEAD 비교
git -C /path/to/source rev-parse HEAD
git -C /path/to/destination rev-parse HEAD

# 대상 remote 확인
git -C /path/to/destination remote -v

# 브랜치·태그 확인
git -C /path/to/destination branch -a
git -C /path/to/destination tag
```

🟡 `git push --mirror`는 원격의 참조를 로컬과 완전히 맞추며 원격 브랜치·태그를 삭제하거나 덮어쓸 수 있습니다. 일반적인 저장소 이전에는 `git push --all`과 `git push --tags`를 우선합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Git Documentation: [git-scm.com/docs](https://git-scm.com/docs) — ★★★☆☆
- Pro Git Book: [git-scm.com/book](https://git-scm.com/book/en/v2) — ★★★★☆
- Git Reference: [git-scm.com/docs/git](https://git-scm.com/docs/git) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-24

**마지막 업데이트**: 2026-08-24

© 2026 siasia86. Licensed under CC BY 4.0.
