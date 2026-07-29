---
name: git-official-notes
description: Git 공식 문서 기반 핵심 사실, 버전 현황, 객체 모델, 주요 명령어 동작 원리 정리. Git 문서 작성/검토 시 참조.
tags:
  - git
  - version-control
  - vcs
  - cicd
  - distributed
last_checked: 2026-07-29
sources:
  - https://git-scm.com/doc
  - https://git-scm.com/book/en/v2
  - https://git-scm.com/docs
  - https://github.com/git/git/tags
---

# Git 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-07-29)

| 항목      | 버전   | 비고                             |
|-----------|--------|----------------------------------|
| Stable    | 2.55.0 | 출시: 2025, 현행 권장 버전       |
| 이전 안정 | 2.54.0 | -                                |
| 최소 권장 | 2.28+  | `init.defaultBranch` 지원 (2.28) |

> 출처: github.com/git/git/tags (2026-07-29 확인)

## 2. Git 객체 모델 (4가지)

| 객체 타입 | 설명                                | SHA 식별 |
|-----------|-------------------------------------|----------|
| blob      | 파일 내용 (파일명 없음)             | ✅       |
| tree      | 디렉토리 구조 (blob + subtree 참조) | ✅       |
| commit    | tree + parent + author + message    | ✅       |
| tag       | annotated tag — commit + 태거 정보  | ✅       |

```
commit
  └── tree (root)
        ├── blob (README.md 내용)
        ├── blob (main.py 내용)
        └── tree (src/)
              └── blob (auth.py 내용)
```

> 출처: git-scm.com/book/en/v2/Git-Internals-Git-Objects

## 3. SHA 해시

- Git 2.29+: SHA-256 지원 (실험적, 기본은 여전히 SHA-1).
- SHA-1 충돌 방지: `sha1collisiondetection` 라이브러리 내장 (Git 2.13+).
- 오브젝트 ID = SHA-1 40자 또는 SHA-256 64자.

## 4. HEAD, Branch, Tag 정의

| 참조 타입       | 저장 위치                   | 설명                                 |
|-----------------|-----------------------------|--------------------------------------|
| HEAD            | `.git/HEAD`                 | 현재 체크아웃 위치 (브랜치 또는 SHA) |
| branch          | `.git/refs/heads/<name>`    | 최신 커밋 SHA 포인터 (이동함)        |
| remote branch   | `.git/refs/remotes/<r>/<b>` | 원격 브랜치 로컬 캐시                |
| lightweight tag | `.git/refs/tags/<name>`     | 커밋 SHA 포인터 (불변)               |
| annotated tag   | `.git/refs/tags/<name>`     | tag 객체 → 커밋 (서명/메시지 포함)   |

> HEAD가 브랜치를 가리키면 "attached HEAD", SHA를 직접 가리키면 "detached HEAD".

## 5. 핵심 명령어 내부 동작

### `git add`

- 파일을 blob 객체로 저장 (`.git/objects/`)
- Index(Staging Area, `.git/index`)에 blob SHA 기록

### `git commit`

- tree 객체 생성 (Index 기반)
- commit 객체 생성 (tree SHA + parent SHA + 메타데이터)
- 현재 브랜치 포인터를 새 commit SHA로 이동

### `git merge` — 3종류

| 방식              | 조건                           | 결과                              |
|-------------------|--------------------------------|-----------------------------------|
| Fast-forward      | 대상 브랜치가 현재의 직계 조상 | 포인터 이동만 (merge commit 없음) |
| ort (기본, 2.34+) | 공통 조상 1개                  | merge commit 생성 (3-way merge)   |
| Octopus           | 다중 브랜치 병합               | 다중 부모 merge commit            |

> ort = "Ostensibly Recursive's Twin". Git 2.34에서 recursive를 대체하여 기본 전략이 됨.
> 출처: git-scm.com/docs/git-merge

### `git rebase`

- 브랜치의 커밋을 새 base 위에 재적용 (새 SHA 생성).
- **공유된(push된) 브랜치에서 rebase 금지** — SHA 변경으로 히스토리 불일치.
- `--onto`: 특정 범위 커밋만 다른 base로 이동.

### `git fetch` vs `git pull`

| 명령어      | 동작                                      |
|-------------|-------------------------------------------|
| `git fetch` | 원격 변경 로컬 캐시 업데이트만            |
| `git pull`  | fetch + merge (또는 `--rebase` 시 rebase) |

> `git pull --rebase` = fetch + rebase. 선형 이력 유지에 권장.

## 6. 저장소 내부 구조

```
.git/
├── HEAD            # 현재 브랜치 참조
├── config          # 저장소 설정
├── index           # Staging Area (바이너리)
├── objects/        # 모든 객체 (blob, tree, commit, tag)
│   ├── pack/       # packfile (압축 객체)
│   └── info/
├── refs/
│   ├── heads/      # 로컬 브랜치
│   ├── remotes/    # 원격 브랜치 캐시
│   └── tags/       # 태그
├── hooks/          # 훅 스크립트
├── logs/           # reflog 이력
└── COMMIT_EDITMSG  # 마지막 커밋 메시지
```

## 7. Reflog

- `.git/logs/` 에 저장. 브랜치/HEAD의 모든 이동 이력 기록.
- 기본 보존 기간: 90일 (unreachable 객체는 30일).
- `git reset --hard` 후에도 reflog로 복구 가능.

```bash
git reflog           # HEAD 이동 이력
git reflog show main # main 브랜치 이동 이력
```

> 출처: git-scm.com/docs/git-reflog

## 8. Packfile

- `git gc` 또는 일정 loose object 누적 시 자동 생성.
- `.git/objects/pack/*.pack` + `*.idx` (인덱스).
- delta compression: 유사한 객체 간 차분만 저장.
- `git count-objects -v` 로 loose / packed 객체 수 확인.

## 9. 주요 설정

| 설정 키              | 기본값     | 설명                                     |
|----------------------|------------|------------------------------------------|
| `core.autocrlf`      | false      | 줄바꿈 자동 변환 (Windows: true 권장)    |
| `init.defaultBranch` | master     | 2.28+: main 권장                         |
| `pull.rebase`        | false      | true 시 pull = fetch + rebase            |
| `fetch.prune`        | false      | true 시 삭제된 원격 브랜치 자동 정리     |
| `merge.ff`           | true       | false 시 항상 merge commit 생성          |
| `rebase.autoStash`   | false      | true 시 rebase 전 자동 stash/unstash     |
| `core.hooksPath`     | .git/hooks | 훅 디렉토리 경로 변경 가능               |
| `safe.directory`     | -          | 소유자 다른 디렉토리 접근 허용 (2.35.2+) |

> 출처: git-scm.com/docs/git-config

## 10. 주의사항

- `git push --force` 는 원격 이력 덮어씀 — `--force-with-lease` 권장.
- `git reset --hard` 는 Working Directory까지 삭제 — reflog로 복구 가능.
- `git clean -fd` 는 Untracked 파일 삭제 — 복구 불가.
- `git stash drop` / `git stash clear` 는 복구 어려움.
- shallow clone (`--depth N`) 에서 `git log` 는 제한된 이력만 표시.
- `git submodule` 업데이트는 `git pull` 에 포함되지 않음 → `--recurse-submodules` 필요.
