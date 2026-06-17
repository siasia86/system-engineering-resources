# .gitignore 패턴 문법

`.gitignore` 파일에서 사용하는 패턴 매칭 규칙을 정리합니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 기본 규칙](#1-기본-규칙) / [2. 와일드카드](#2-와일드카드) / [3. 디렉토리 패턴](#3-디렉토리-패턴) |
| [4. 부정 패턴](#4-부정-패턴) / [5. 실전 예제](#5-실전-예제) / [6. 우선순위](#6-우선순위)             |

---

## 1. 기본 규칙

| 패턴        | 의미                        |
|-------------|-----------------------------|
| `file.txt`  | 모든 깊이의 `file.txt` 무시 |
| `/file.txt` | 루트의 `file.txt`만 무시    |
| `#`         | 주석                        |
| `\#`        | `#`으로 시작하는 파일명     |
| 빈 줄       | 무시 (구분용)               |
| `\!`        | `!`로 시작하는 파일명       |

### 선행 슬래시(`/`)

```gitignore
# 루트에 있는 build만 무시 (하위 디렉토리의 build는 추적)
/build

# 모든 곳의 build 무시
build
```

---

## 2. 와일드카드

| 패턴    | 의미                             | 매칭 예시                        |
|---------|----------------------------------|----------------------------------|
| `*`     | 슬래시 제외 모든 문자 (0개 이상) | `*.log` → `app.log`, `error.log` |
| `?`     | 슬래시 제외 단일 문자            | `file?.txt` → `file1.txt`        |
| `[abc]` | 괄호 내 한 문자                  | `file[0-9].txt` → `file3.txt`    |
| `**`    | 0개 이상의 디렉토리              | `**/logs` → `a/b/logs`           |

### `*` vs `**` 차이

```gitignore
logs/*          # logs/ 1단계 아래만 (logs/a.log ✅, logs/sub/b.log ❌)
logs/**         # logs/ 모든 깊이    (logs/a.log ✅, logs/sub/b.log ✅)
```

```gitignore
**/logs         # 어느 위치든 logs라는 이름의 파일/디렉토리 매칭
                # src/logs ✅, a/b/logs ✅
```

---

## 3. 디렉토리 패턴

가장 혼동이 많은 부분입니다.

### `dir/` vs `dir/*` vs `dir/**`

```
project/
├── dir/
│   ├── file.txt
│   └── sub/
│       └── nested.txt
```

| 패턴     | `dir/` 자체 | `dir/file.txt` | `dir/sub/nested.txt` | 예외 가능 |
|----------|-------------|----------------|----------------------|-----------|
| `dir/`   | ✅ 무시     | ✅ 무시        | ✅ 무시              | ❌        |
| `dir/*`  | 추적        | ✅ 무시        | ❌ 추적              | ✅        |
| `dir/**` | 추적        | ✅ 무시        | ✅ 무시              | ✅        |

### 핵심 차이

```gitignore
# 디렉토리 전체를 무시 — 내부 예외 불가
dir/

# 내용물만 무시 — 예외 설정 가능
dir/**
!dir/README.md        # ← dir/ 패턴에서는 이 예외가 동작하지 않음
```

### 트레일링 슬래시의 의미

```gitignore
logs      # "logs"라는 이름의 파일 + 디렉토리 모두 매칭
logs/     # "logs" 디렉토리만 매칭 (동명의 파일은 추적)
```

---

## 4. 부정 패턴 (`!`)

이미 무시된 파일을 다시 추적합니다.

```gitignore
# 모든 .env 무시하되 예제만 추적
*.env
!.env.example
```

### 부정 패턴이 동작하지 않는 경우

```gitignore
# ❌ 동작 안 함 — 부모 디렉토리가 무시되면 하위 예외 불가
build/
!build/important.txt     # 무시됨 (부모가 이미 ignore)

# ✅ 동작함 — /** 사용
build/**
!build/important.txt     # 추적됨
```

🟡 **규칙**: 부모 디렉토리가 `dir/` 형태로 무시되면 그 안의 `!` 예외는 동작하지 않습니다. `dir/**`로 변경해야 합니다.

---

## 5. 실전 예제

### Python 프로젝트

```gitignore
__pycache__/
*.py[cod]
*.so
.venv/
dist/
*.egg-info/
.env
```

### Node.js 프로젝트

```gitignore
node_modules/
dist/
.env
*.log
```

### Terraform

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfvars
!example.tfvars
```

### 시크릿 관리

```gitignore
# 전체 무시 후 예외
secrets/**
!secrets/.gitkeep
!secrets/README.md

# 키/인증서
*.key
*.pem
*.p12
!public.key
```

### GitLab 설정 디렉토리

```gitignore
# 설정 전체 무시, README만 추적
12_config_gitlab/**
!12_config_gitlab/README.md
```

---

## 6. 우선순위

`.gitignore`가 여러 곳에 존재할 때 우선순위입니다.

| 순위       | 위치                                        | 범위                   |
|------------|---------------------------------------------|------------------------|
| 1 (최우선) | 커맨드라인 (`-x` 옵션)                      | 일시적                 |
| 2          | 해당 디렉토리의 `.gitignore`                | 해당 디렉토리 이하     |
| 3          | 상위 디렉토리의 `.gitignore`                | 계층적 상속            |
| 4          | `$GIT_DIR/info/exclude`                     | 로컬 전용 (공유 안 됨) |
| 5          | `core.excludesFile` (`~/.gitignore_global`) | 전역                   |

같은 파일 내에서는 **나중 규칙이 우선**합니다:

```gitignore
*.log          # 먼저: 모든 .log 무시
!important.log # 나중: important.log는 추적 (이 규칙이 이김)
```

---

## 참고: 디버깅

```bash
# 특정 파일이 왜 무시되는지 확인
git check-ignore -v path/to/file

# 무시되는 파일 전체 목록
git status --ignored

# .gitignore 변경 후 캐시 초기화 (이미 추적 중인 파일 제거)
git rm -r --cached .
git add .
git commit -m "apply .gitignore changes"
```

🟡 `git rm --cached`는 원격에서도 파일이 삭제됩니다. 로컬에만 유지하려면 팀원에게 사전 공유합니다.

---

## 참고 자료

- Git Documentation: [git-scm.com/docs/gitignore](https://git-scm.com/docs/gitignore) — ★★★☆☆
- GitHub gitignore templates: [github.com/github/gitignore](https://github.com/github/gitignore) — ★★★☆☆

---

**작성일**: 2026-06-17

**마지막 업데이트**: 2026-06-17

© 2026 siasia86. Licensed under CC BY 4.0.
