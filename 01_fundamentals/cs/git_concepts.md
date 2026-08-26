# Git 개념
<!-- reference: _reference/git_official_notes.md -->

## 목차

| 섹션                                                                                                           |
|----------------------------------------------------------------------------------------------------------------|
| [1. Git이란](#1-git이란) / [2. 분산형 VCS 아키텍처](#2-분산형-vcs-아키텍처) / [3. 객체 모델](#3-객체-모델)     |
| [4. 참조 시스템](#4-참조-시스템) / [5. 작업 영역 구조](#5-작업-영역-구조) / [6. 브랜치 전략](#6-브랜치-전략)   |
| [7. merge vs rebase](#7-merge-vs-rebase) / [8. 원격 저장소](#8-원격-저장소) / [9. 훅과 자동화](#9-훅과-자동화) |
| [10. 인프라에서의 Git 활용](#10-인프라에서의-git-활용)                                                         |

---

## 1. Git이란

Git은 분산 버전 관리 시스템(DVCS)으로, 2005년 리누스 토르발즈가 Linux 커널 개발을 위해 작성했습니다.

### 핵심 설계 원칙

- **분산형** — 모든 클론이 전체 이력을 보유. 서버 없이도 커밋/브랜치/병합 가능.
- **스냅샷 기반** — 파일 변경 차분(diff)이 아닌 전체 트리 스냅샷을 저장.
- **무결성** — 모든 객체가 SHA-1(또는 SHA-256) 해시로 식별. 임의 변조 감지 가능.
- **빠른 브랜치** — 브랜치 = SHA 포인터 파일(41 bytes). 생성/전환이 O(1).

### Git 데이터 흐름

```
Working Directory   Staging Area (Index)   Local Repo    Remote Repo
      │                     │                   │               │
      │── git add ─────────>│                   │               │
      │                     │── git commit ────>│               │
      │                     │                   │── git push ──>│
      │<─────────────────────── git checkout ───┤               │
      │<─────────────────────── git reset ──────┤               │
      │<────────────────────────────────────────── git pull ────┤
      │                     │                   │<── git fetch ─┤
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 객체 모델

Git의 모든 데이터는 4가지 객체 타입으로 구성됩니다. 각 객체는 SHA 해시로 식별되며 `.git/objects/`에 저장됩니다.

### 4가지 객체 타입

| 객체 타입 | 설명                                | 비고                 |
|-----------|-------------------------------------|----------------------|
| blob      | 파일 내용 (파일명 없음)             | 내용 동일 = 동일 SHA |
| tree      | 디렉토리 구조 (blob + subtree 참조) | 계층 구조 표현       |
| commit    | tree + parent + author + message    | DAG의 노드           |
| tag       | annotated tag — commit + 태거 정보  | 서명/메시지 포함     |

### 객체 관계도

```
commit C3
  │  author: sjyun
  │  message: "feat: add auth"
  │  parent: C2
  └── tree T3
        ├── blob B1 (README.md)
        ├── blob B4 (main.py)      <- B4: 이번 커밋에서 변경
        └── tree T_src
              ├── blob B2 (auth.py)
              └── blob B3 (utils.py)

commit C2
  └── tree T2
        ├── blob B1 (README.md)   <- B1: 변경 없음 = 동일 SHA 재사용
        └── blob B5 (main.py)     <- 이전 버전
```

**스냅샷 기반의 효율성:** 변경되지 않은 파일은 동일한 blob SHA를 참조하므로 중복 저장 없음.

### DAG (Directed Acyclic Graph)

커밋 이력은 방향성 비순환 그래프(DAG)입니다.

```
C1 <- C2 <- C3 <- C4  (main)
              ^
               \
                C5 <- C6  (feature)
```

- 각 커밋은 parent를 가리킴 (방향: 자식 → 부모)
- merge commit은 부모가 2개 (또는 그 이상)
- 순환 없음 (비순환) — 과거를 변경하면 새 SHA 생성

[⬆ 목차로 돌아가기](#목차)

---

## 4. 참조 시스템

### 참조 타입

| 참조 타입       | 저장 위치                   | 설명                          |
|-----------------|-----------------------------|-------------------------------|
| HEAD            | `.git/HEAD`                 | 현재 체크아웃 위치            |
| branch          | `.git/refs/heads/<name>`    | 최신 커밋 SHA 포인터 (이동함) |
| remote branch   | `.git/refs/remotes/<r>/<b>` | 원격 브랜치 로컬 캐시         |
| lightweight tag | `.git/refs/tags/<name>`     | 커밋 SHA 포인터 (불변)        |
| annotated tag   | `.git/refs/tags/<name>`     | tag 객체 → 커밋               |

### HEAD 상태

```
Attached HEAD (정상):
  .git/HEAD = "ref: refs/heads/main"
  -> main 브랜치를 가리킴
  -> 커밋 시 main 포인터가 이동

Detached HEAD (분리된 상태):
  .git/HEAD = "a1b2c3d4..."  (SHA 직접 참조)
  -> 특정 커밋/태그 체크아웃 시 발생
  -> 커밋은 가능하지만 브랜치에 연결되지 않음
  -> 브랜치 생성 없이 이탈하면 해당 커밋 참조 없어짐
```

### Reflog

모든 HEAD 이동 이력을 `.git/logs/`에 기록합니다. `git reset --hard` 후 복구에 사용합니다.

```bash
git reflog           # HEAD 이동 이력 (기본 90일 보존)
git checkout HEAD@{3}  # 3번째 이전 HEAD 위치로 이동
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 작업 영역 구조

### 3가지 영역

```
┌──────────────────────────────────────────────────────────┐
│  Working Directory  |  Staging Area  |  Local Repo       │
│  (actual files)     |  (.git/index)  |  (.git/)          │
└──────────────────────────────────────────────────────────┘
```

| 영역              | 설명                                      |
|-------------------|-------------------------------------------|
| Working Directory | 실제 파일이 존재하는 작업 공간            |
| Staging Area      | 다음 커밋에 포함할 변경 선택 공간 (Index) |
| Local Repo        | 커밋 이력 저장소 (`.git/` 디렉토리)       |

### 파일 상태 전이

```
Untracked ──git add──> Staged ──git commit──> Committed
    ^                                              │
    │                                              │ edit file
    │                                              v
    │                                           Modified
    │                                              │
    └──── git rm --cached ───────── git add <──────┘
```

| 상태      | 설명                              |
|-----------|-----------------------------------|
| Untracked | Git이 추적하지 않는 새 파일       |
| Staged    | `git add` 후 Index에 등록된 상태  |
| Committed | 저장소에 기록된 상태              |
| Modified  | Committed 이후 변경된 상태        |
| Ignored   | `.gitignore`에 의해 무시되는 파일 |

### `git reset` 3가지 모드

| 옵션      | HEAD | Index | Working Dir | 용도                                 |
|-----------|------|-------|-------------|--------------------------------------|
| `--soft`  | 이동 | 유지  | 유지        | 커밋만 취소, 변경 스테이징 상태 유지 |
| `--mixed` | 이동 | 리셋  | 유지        | 커밋+스테이징 취소 (기본값)          |
| `--hard`  | 이동 | 리셋  | 리셋        | 모든 변경 삭제 (복구 주의)           |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 브랜치 전략

### Git 브랜치의 특성

- 브랜치 = SHA 해시를 담은 41바이트 파일 → 생성/삭제/전환 O(1)
- 브랜치 전환 시 Working Directory가 해당 커밋의 트리로 교체됨
- 삭제된 브랜치도 커밋 SHA를 알면 `git checkout -b <name> <SHA>`로 복구 가능

### 주요 브랜치 전략

| 전략        | 특징                                    | 적합 규모                 |
|-------------|-----------------------------------------|---------------------------|
| Trunk-based | main 직접 커밋, 짧은 수명 브랜치        | 소규모/고숙련 팀          |
| GitHub Flow | main + feature branch + PR              | 웹서비스 지속 배포        |
| GitFlow     | main + develop + feature/release/hotfix | 릴리스 주기 있는 프로젝트 |
| Forking     | 기여자별 fork + PR                      | 오픈소스                  |

### GitFlow 레이아웃

```
main       ─────────────────────────────────── v1.0 ── v2.0
                                                 ^        ^
develop    ──────────────────────────────────────┤        │
              ^             ^                    │        │
feature/A  ───┘   feature/B─┘                    │        │
                                                 │        │
release/1.0 ─────────────────────────────────────┘        │
                                                          │
hotfix/1.1 ───────────────────────────────────────────────┘
```

### PR(Pull Request) 병합 방식

| 방식         | 이력 형태           | 언제 사용                    |
|--------------|---------------------|------------------------------|
| Merge commit | 비선형 (merge 노드) | 브랜치 이력 보존 필요 시     |
| Squash merge | 선형 (단일 커밋)    | 기능 단위 커밋 정리 시 권장  |
| Rebase merge | 선형 (커밋 재적용)  | 커밋 단위 이력 보존 + 선형화 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. merge vs rebase

### 동작 비교

```
Before:
  main:    A <- B <- C
  feature:         ^ <- D <- E

After git merge main (from feature):       <- ort 전략 (3-way merge, Git 2.34+ 기본)
  feature: A <- B <- C <- D <- E <- M  (M: merge commit, parent=C,E)

After git rebase main (from feature):
  feature: A <- B <- C <- D' <- E'     (D',E': 새 SHA, C 위에 재적용)
```

🟡 Git 2.34+에서 기본 merge 전략은 `ort`(Ostensibly Recursive's Twin)입니다. `recursive`의 drop-in 대체를 목표로 설계되었습니다.

### 선택 기준

| 상황                       | 권장   | 이유                                 |
|----------------------------|--------|--------------------------------------|
| 기능 브랜치 → main 통합    | merge  | 브랜치 이력 보존, 안전               |
| main 변경을 feature에 반영 | rebase | 선형 이력 유지, 충돌 조기 해결       |
| 공유된(push된) 브랜치      | merge  | rebase는 SHA 변경 → 팀원 이력 불일치 |
| 로컬 커밋 정리 후 push 전  | rebase | 깔끔한 커밋 이력                     |

### Interactive Rebase (`git rebase -i`)

```bash
git rebase -i HEAD~3   # 최근 3개 커밋 편집

# 편집기에서:
pick a1b2c3 feat: add login
squash b2c3d4 fix: typo in login    <- 이전 커밋에 합침
reword c3d4e5 feat: add logout      <- 메시지 수정
```

🟡 `git rebase -i`는 로컬 미push 커밋에만 사용합니다. push 후 rebase는 `--force-with-lease`가 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 원격 저장소

### 원격 참조 구조

```
origin/main  ──────────────>  Remote (GitHub/GitLab)
    │                              main 브랜치
    │ (로컬 캐시, git fetch로 갱신)
    │
    v
.git/refs/remotes/origin/main
```

### fetch vs pull vs push

```bash
git fetch origin          # 원격 변경을 로컬 캐시에 반영 (Working Dir 불변)
git pull origin main      # fetch + merge
git pull --rebase origin main  # fetch + rebase (선형 이력 선호 시)
git push origin main      # 로컬 커밋을 원격에 반영
git push --force-with-lease   # 강제 push (원격이 예상과 다르면 실패)
```

### 원격 관리

```bash
git remote -v                           # 원격 목록
git remote add upstream <URL>           # upstream 추가 (fork 워크플로우)
git remote set-url origin <NEW_URL>     # URL 변경
git fetch --prune                       # 삭제된 원격 브랜치 캐시 정리
```

### Upstream vs Origin

```
Upstream (원본 저장소)
    │
    │ fork
    v
Origin (내 fork)
    │
    │ clone
    v
Local Repo
```

- `origin`: 내가 push/pull하는 원격 (fork 또는 직접 저장소)
- `upstream`: fork의 원본 저장소 (PR 대상)

[⬆ 목차로 돌아가기](#목차)

---

## 9. 훅과 자동화

Git 훅은 특정 이벤트 발생 시 실행되는 스크립트입니다. `.git/hooks/` 에 위치하며, 팀 공유가 필요하면 `core.hooksPath`로 별도 디렉토리를 지정합니다.

### 클라이언트 훅

| 훅           | 실행 시점           | 용도                          |
|--------------|---------------------|-------------------------------|
| `pre-commit` | 커밋 직전           | lint, 테스트, 포맷 검사       |
| `commit-msg` | 커밋 메시지 작성 후 | 메시지 형식 강제              |
| `pre-push`   | push 직전           | 테스트 실행, 금지 브랜치 검사 |
| `post-merge` | merge 완료 후       | 의존성 설치 자동화            |

### 서버 훅

| 훅             | 실행 시점         | 용도                 |
|----------------|-------------------|----------------------|
| `pre-receive`  | 서버 수신 직전    | 서버측 강제 정책     |
| `post-receive` | 서버 수신 완료 후 | CI 트리거, 배포 알림 |

### pre-commit 훅 예시

```bash
#!/bin/bash
# .git/hooks/pre-commit (또는 core.hooksPath 경로)

# Python 파일 lint 검사
if git diff --cached --name-only | grep -q '\.py$'; then
    git stash -q --keep-index
    python3 -m flake8 $(git diff --cached --name-only | grep '\.py$')
    status=$?
    git stash pop -q
    [ $status -ne 0 ] && echo "flake8 실패. 커밋 중단." && exit 1
fi

# 시크릿 패턴 검사
if git diff --cached | grep -qE '(password|secret|key)\s*=\s*["\x27][^"\x27]{8,}'; then
    echo "시크릿 패턴 감지. 커밋 중단." && exit 1
fi

exit 0
```

### `core.hooksPath` — 팀 공유 훅

```bash
# 저장소 루트에 hooks/ 디렉토리 생성 후
git config core.hooksPath hooks/
```

이 설정은 `.git/config`에 저장되므로 각 팀원이 설정해야 합니다. `husky` 같은 도구로 자동화 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 인프라에서의 Git 활용

### GitOps 개념

```
Git Repository (IaC 소스)
       │
       │ PR merge (main)
       v
  ArgoCD / Flux
  (변경 감지)
       │
       │ 자동 적용
       v
  Kubernetes Cluster
  (실제 상태 = Git 상태)
```

GitOps 원칙: **Git = 단일 진실 공급원(Single Source of Truth)**.
클러스터 상태를 직접 변경하지 않고, Git 커밋으로만 변경합니다.

### IaC 저장소 규칙

| 항목            | 권장 설정                               |
|-----------------|-----------------------------------------|
| `.tfstate` 파일 | `.gitignore`에 반드시 제외              |
| 시크릿/자격증명 | 절대 커밋 금지 — gitleaks pre-commit 훅 |
| 브랜치 전략     | Trunk-based 또는 GitHub Flow            |
| PR 병합 방식    | Squash merge 권장 (이력 간결화)         |
| 태그            | 릴리스마다 annotated tag 생성           |

### `.gitignore` IaC 필수 패턴

```gitignore
# Terraform
*.tfstate
*.tfstate.*
.terraform/
*.tfvars         # 시크릿 포함 가능성

# Ansible
*.retry
vault_password_file
*.vault

# 공통
.env
*.pem
*.key
*_rsa
*_ed25519
```

### 저장소 용량 관리

```bash
# 큰 파일 목록 확인
git rev-list --objects --all | \
    git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
    grep '^blob' | sort -k3 -rn | head -20

# BFG Repo Cleaner로 대용량/시크릿 파일 이력에서 제거
bfg --delete-files '*.pem' --no-blob-protection .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

🟡 이력 재작성 후에는 모든 팀원이 `git clone`을 새로 해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Pro Git Book: [git-scm.com/book](https://git-scm.com/book/ko/v2) — ★★★★☆
- Git Reference: [git-scm.com/docs](https://git-scm.com/docs) — ★★★☆☆
- Git Internals: [git-scm.com/book/en/v2/Git-Internals-Git-Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) — ★★★★☆
- [git_guide.md](../../02_infrastructure/cicd/git_guide.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-29

**마지막 업데이트**: 2026-07-29

© 2026 siasia86. Licensed under CC BY 4.0.
