# GitHub CLI (gh)

GitHub 작업을 터미널에서 수행하는 공식 CLI 도구입니다. PR, Issue, Repo, Release, Workflow 등을 브라우저 없이 관리합니다.

## 목차

| 섹션                                                                                                                                       |
|--------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 설치](#1-설치) / [2. 인증](#2-인증) / [3. 저장소 관리](#3-저장소-관리) / [4. PR](#4-pr) / [5. Issue](#5-issue)                         |
| [6. Release](#6-release) / [7. Workflow](#7-workflow) / [8. 고급 활용](#8-고급-활용) / [9. 설정](#9-설정) / [10. Extension](#10-extension) |
| [11. Fine-grained PAT](#11-fine-grained-pat) / [12. 실무 팁](#12-실무-팁) / [13. 트러블슈팅](#13-트러블슈팅)                               |

---

## 1. 설치

### Linux (RHEL/Rocky/Fedora)

```bash
sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### macOS

```bash
brew install gh
```

### 버전 확인

```bash
gh --version
# gh version 2.x.x (2026-xx-xx)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 인증

### 로그인

```bash
# 대화형 (브라우저 인증)
gh auth login

# 토큰 직접 입력
gh auth login --with-token < ~/.github_token

# GitHub Enterprise
gh auth login --hostname github.example.com
```

### 인증 상태 확인

```bash
gh auth status
# ✓ Logged in to github.com as username (token)
# ✓ Token scopes: repo, read:org, workflow
```

### 토큰 관리

```bash
# 현재 토큰 출력
gh auth token

# 로그아웃
gh auth logout

# 토큰 갱신 (scope 추가)
gh auth refresh --scopes write:packages,read:packages
```

### Scope 개념

Scope(범위)는 **토큰이 접근할 수 있는 권한의 범위**입니다. GitHub Personal Access Token(PAT)을 발급할 때 "이 토큰으로 무엇을 할 수 있는가"를 지정합니다.

```
토큰 발급 시:
  "이 토큰에 repo, workflow scope를 부여하겠습니다"
     → PR/Issue 관리 가능, Actions 실행 가능
     → 패키지 관리는 불가 (write:packages 미포함)
```

비유하면:
- 토큰 = 출입증
- Scope = 출입 가능 구역

```
scope: repo               → 코드 저장소 전체 접근 (읽기+쓰기)
scope: repo (read)        → 코드 저장소 읽기만
scope: workflow           → GitHub Actions 실행/관리
scope: write:packages     → 패키지 업로드
scope: read:org           → 조직 멤버 목록 확인
scope: admin:public_key    → SSH 인증 키 등록/삭제
```

### Scope 계층 구조

```
repo (최상위 — private repo 전체 접근)
├── repo:status         커밋 상태 읽기/쓰기
├── repo_deployment     deployment status API 접근
├── public_repo         public repo만 접근
└── repo:invite         초대 관리

write:packages
├── read:packages       패키지 읽기
└── (write)             패키지 업로드/삭제

admin:org
├── write:org           org 설정 변경
└── read:org            org 멤버 목록 읽기

admin:public_key (SSH 인증 키)
├── write:public_key        SSH 인증 키 등록
└── read:public_key         SSH 인증 키 목록 확인

admin:ssh_signing_key (커밋 서명 키)
├── write:ssh_signing_key   커밋 서명용 SSH 키 등록
└── read:ssh_signing_key    커밋 서명용 SSH 키 목록 확인
```

🟡 상위 scope를 부여하면 하위 scope가 자동 포함됩니다. `repo`를 주면 `public_repo`도 포함됩니다.

### 필요 scope 표

| 작업               | 필요 scope              | 설명                                |
|--------------------|-------------------------|-------------------------------------|
| PR/Issue 관리      | `repo`                  | private repo 코드+이슈+PR 전체 접근 |
| public repo만 접근 | `public_repo`           | public repo 한정 (최소 권한)        |
| Workflow 실행      | `workflow`              | Actions .yml 수정 + 수동 실행       |
| 패키지 업로드      | `write:packages`        | GHCR, npm 등 패키지 레지스트리      |
| SSH 인증 키 등록   | `admin:public_key`      | 계정에 SSH 인증 키 추가/삭제        |
| org 멤버 확인      | `read:org`              | 조직 멤버 목록 읽기                 |
| 커밋 서명 키 등록  | `admin:ssh_signing_key` | GPG/SSH 커밋 서명 키 관리           |
| Secret 설정        | `repo` + `workflow`     | Actions secrets 관리                |
| Gist 생성          | `gist`                  | Gist 생성/수정                      |
| 알림 관리          | `notifications`         | 알림 읽기/구독 관리                 |

### 현재 토큰 scope 확인

```bash
# gh가 가진 토큰의 scope 확인
gh auth status
# ✓ Token scopes: repo, read:org, workflow

# scope 부족 시 에러 예시
gh secret set MY_KEY --body "value"
# error: HTTP 403: Resource not accessible by personal access token
# → workflow scope 추가 필요

# scope 추가 (재인증)
gh auth refresh --scopes repo,workflow,write:packages
```

### 최소 권한 원칙

| 용도                 | 권장 scope                 | 이유                       |
|----------------------|----------------------------|----------------------------|
| 일상 작업 (PR/Issue) | `repo, workflow, read:org` | 대부분의 gh 명령 커버      |
| Actions 연동 전용    | `repo, workflow`           | Actions 실행에 필요한 최소 |
| 읽기 전용            | `public_repo, read:org`    | 조회만 (쓰기 불가)         |
| 패키지 push 추가     | `+ write:packages`         | Docker 이미지 push 등      |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 저장소 관리

### 생성

```bash
# 현재 디렉토리로 새 repo 생성
gh repo create my-project --private --source=. --push

# 빈 repo 생성 (clone 포함)
gh repo create org/my-project --public --clone

# 템플릿에서 생성
gh repo create my-app --template org/template-repo --private --clone
```

### 클론

```bash
gh repo clone owner/repo
gh repo clone owner/repo -- --depth 1    # shallow clone
```

### 포크

```bash
gh repo fork owner/repo --clone
```

### 조회

```bash
# 현재 repo 정보
gh repo view

# 웹에서 열기
gh repo view --web

# 목록 (본인 소유)
gh repo list --limit 20

# org 소유 목록
gh repo list my-org --limit 50
```

### 설정 변경

```bash
# 설명 변경
gh repo edit --description "새 설명"

# 기본 브랜치 변경
gh repo edit --default-branch main

# 기능 토글
gh repo edit --enable-issues=false
gh repo edit --enable-wiki=false
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. PR

### 생성

```bash
# 대화형
gh pr create

# 옵션 지정
gh pr create --title "feat: 기능 추가" --body "설명" --base main

# draft PR
gh pr create --draft --title "WIP: 작업 중"

# 리뷰어/라벨 지정
gh pr create --reviewer user1,user2 --label "enhancement"

# 이슈 연결
gh pr create --title "fix: 버그 수정" --body "Closes #123"
```

### 목록 조회

```bash
# 현재 repo의 열린 PR
gh pr list

# 본인이 생성한 PR
gh pr list --author @me

# 리뷰 요청받은 PR
gh pr list --search "review-requested:@me"

# 상태별
gh pr list --state merged --limit 10
```

### 체크아웃

```bash
# PR 번호로 로컬 체크아웃
gh pr checkout 42

# PR 브랜치 정보 확인 후 체크아웃
gh pr view 42
gh pr checkout 42
```

### 리뷰

```bash
# 리뷰 승인
gh pr review 42 --approve

# 코멘트
gh pr review 42 --comment --body "LGTM"

# 변경 요청
gh pr review 42 --request-changes --body "여기 수정 필요"
```

### 머지

```bash
# merge commit
gh pr merge 42 --merge

# squash merge
gh pr merge 42 --squash

# rebase merge
gh pr merge 42 --rebase

# 머지 후 브랜치 삭제
gh pr merge 42 --squash --delete-branch

# auto-merge (required checks 통과 후 자동 머지)
gh pr merge 42 --auto --squash
```

### 상태 확인

```bash
# CI 체크 상태
gh pr checks 42

# diff 확인
gh pr diff 42
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Issue

### 생성

```bash
# 대화형
gh issue create

# 옵션 지정
gh issue create --title "버그: 로그인 실패" --body "재현 방법..." --label "bug"

# 템플릿 사용
gh issue create --template "bug_report.md"

# assignee 지정
gh issue create --title "작업" --assignee @me
```

### 목록

```bash
gh issue list
gh issue list --label "bug" --state open
gh issue list --assignee @me
gh issue list --search "is:open label:bug sort:created-desc"
```

### 조회/수정

```bash
# 상세 보기
gh issue view 123

# 웹에서 열기
gh issue view 123 --web

# 닫기
gh issue close 123

# 재오픈
gh issue reopen 123

# 라벨 추가
gh issue edit 123 --add-label "priority:high"
```

### 코멘트

```bash
gh issue comment 123 --body "진행 중입니다"
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Release

### 생성

```bash
# 태그 + 릴리즈 동시 생성
gh release create v1.0.0 --title "v1.0.0" --notes "첫 릴리즈"

# 자동 릴리즈 노트 (이전 태그 이후 커밋 기반)
gh release create v1.1.0 --generate-notes

# draft 릴리즈
gh release create v2.0.0-rc1 --draft --prerelease

# 파일 첨부
gh release create v1.0.0 ./dist/app.tar.gz ./dist/checksum.txt
```

### 목록/조회

```bash
gh release list
gh release view v1.0.0
```

### 다운로드

```bash
# 최신 릴리즈의 에셋 다운로드
gh release download --pattern "*.tar.gz"

# 특정 버전
gh release download v1.0.0 --pattern "*.tar.gz" --dir ./downloads/
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Workflow

### 목록/상태

```bash
# workflow 목록
gh workflow list

# 최근 실행 목록
gh run list --limit 10

# 특정 workflow 실행 내역
gh run list --workflow=ci.yml
```

### 실행

```bash
# workflow 수동 실행 (workflow_dispatch)
gh workflow run ci.yml

# 브랜치 + 입력값 지정
gh workflow run deploy.yml --ref main -f environment=production

# 실행 상태 실시간 확인
gh run watch
```

### 로그 확인

```bash
# 실행 로그
gh run view 12345678 --log

# 실패한 step만
gh run view 12345678 --log-failed

# 웹에서 열기
gh run view 12345678 --web
```

### 재실행

```bash
# 전체 재실행
gh run rerun 12345678

# 실패한 job만 재실행
gh run rerun 12345678 --failed
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 고급 활용

### API 직접 호출

```bash
# REST API
gh api repos/{owner}/{repo}/branches --jq '.[].name'

# GraphQL
gh api graphql -f query='{ viewer { login } }'

# 페이지네이션 자동 처리
gh api repos/{owner}/{repo}/issues --paginate --jq '.[].title'
```

### JSON 출력 + jq

```bash
# PR 목록 JSON
gh pr list --json number,title,author --jq '.[] | "\(.number) \(.title) (\(.author.login))"'

# 최신 릴리즈 태그
gh release list --json tagName --jq '.[0].tagName'

# 본인 repo 중 private만
gh repo list --json name,isPrivate --jq '.[] | select(.isPrivate) | .name'
```

### 별칭 (alias)

```bash
# 별칭 등록
gh alias set prc 'pr create --draft'
gh alias set prl 'pr list --author @me'
gh alias set co 'pr checkout'

# 사용
gh prc --title "WIP: 기능"
gh prl
gh co 42

# 목록 확인
gh alias list
```

### SSH 키 관리

```bash
# SSH 키 등록
gh ssh-key add ~/.ssh/id_ed25519.pub --title "work-laptop"

# 목록
gh ssh-key list

# 삭제
gh ssh-key delete 12345
```

### Secret 관리 (Actions)

```bash
# secret 설정
gh secret set AWS_ACCESS_KEY_ID --body "AKIA..."

# 파일에서 읽기
gh secret set DEPLOY_KEY < ./deploy_key.pem

# 목록
gh secret list

# 삭제
gh secret delete AWS_ACCESS_KEY_ID

# environment secret
gh secret set DB_PASSWORD --env production
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 설정

### 설정 파일

```bash
# 위치: ~/.config/gh/config.yml

# 현재 설정 확인
gh config list

# 에디터 변경
gh config set editor vim

# 기본 프로토콜 (ssh/https)
gh config set git_protocol ssh

# 기본 브라우저
gh config set browser "firefox"

# 페이저 설정
gh config set pager "less -R"
```

### 유용한 설정 조합

```yaml
# ~/.config/gh/config.yml
git_protocol: ssh
editor: vim
prompt: enabled
pager: less -R
aliases:
  prc: pr create --draft
  prl: pr list --author @me
  co: pr checkout
  rv: pr review --approve
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Extension

gh의 기능을 커뮤니티 확장으로 추가할 수 있습니다.

### 설치/관리

```bash
# 확장 검색
gh extension search dashboard

# 설치
gh extension install dlvhdr/gh-dash
gh extension install github/gh-copilot

# 목록
gh extension list

# 업데이트
gh extension upgrade --all

# 삭제
gh extension remove dlvhdr/gh-dash
```

### 유용한 확장

| 확장                     | 용도                    | 설치                                          |
|--------------------------|-------------------------|-----------------------------------------------|
| `dlvhdr/gh-dash`         | PR/Issue 대시보드 (TUI) | `gh extension install dlvhdr/gh-dash`         |
| `github/gh-copilot`      | CLI에서 Copilot 질의    | `gh extension install github/gh-copilot`      |
| `vilmibm/gh-screensaver` | 터미널 스크린세이버     | `gh extension install vilmibm/gh-screensaver` |
| `mislav/gh-branch`       | 브랜치 관리 강화        | `gh extension install mislav/gh-branch`       |

### 기타 명령어

```bash
# gh status: 본인 관련 PR/Issue/Review 한눈에 보기
gh status

# gh codespace: 원격 개발 환경 (Codespaces 사용 시)
gh codespace list
gh codespace create --repo owner/repo
gh codespace ssh -c <codespace-name>
gh codespace stop -c <codespace-name>

# gh cache: Actions 캐시 관리
gh cache list
gh cache delete --all
gh cache delete <cache-id>
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. Fine-grained PAT

GitHub은 2023년부터 Classic PAT 대신 **Fine-grained PAT**을 권장합니다.

### Classic vs Fine-grained 비교

| 항목        | Classic PAT                                      | Fine-grained PAT                                    |
|-------------|--------------------------------------------------|-----------------------------------------------------|
| 권한 단위   | Scope (broad)                                    | Permission (granular)                               |
| 저장소 범위 | 모든 repo 또는 전체                              | 특정 repo 선택 가능                                 |
| 만료        | 무기한 가능                                      | 최대 1년 (필수 만료)                                |
| org 승인    | 불필요                                           | org 관리자 승인 필요 (설정 가능)                    |
| 감사        | 제한적                                           | 세부 권한별 감사 로그                               |
| 생성 위치   | Settings → Developer settings → Tokens (classic) | Settings → Developer settings → Fine-grained tokens |

### Fine-grained PAT 권한 예시

```
Repository permissions:
  Contents: Read and write        ← 코드 push/pull
  Pull requests: Read and write   ← PR 생성/머지
  Issues: Read and write          ← Issue 관리
  Actions: Read and write         ← Workflow 실행
  Secrets: Read and write         ← Secret 설정

Account permissions:
  SSH signing keys: Read and write  ← SSH 키 관리
```

### gh에서 Fine-grained PAT 사용

```bash
# Fine-grained PAT으로 로그인
echo "github_pat_xxxx" | gh auth login --with-token

# 인증 상태 확인 (Token type 표시)
gh auth status
# ✓ Logged in to github.com as username
# ✓ Token: github_pat_****
# ✓ Token scopes: (fine-grained token - no scopes listed)

# 권한 부족 시 에러
gh pr create
# error: HTTP 403: Resource not accessible by personal access token
# → Fine-grained PAT에 "Pull requests: Write" permission 추가 필요
```

### 마이그레이션 권장

| 용도          | Classic → Fine-grained                               |
|---------------|------------------------------------------------------|
| 일상 작업     | `repo` scope → Contents + PRs + Issues (특정 repo만) |
| Actions 연동  | `repo, workflow` → Contents + Actions (특정 repo만)  |
| org 전체 접근 | 불가 → repo 단위로 분리 필요                         |

🟡 Fine-grained PAT은 repo 단위 접근이므로, 여러 repo에 접근하려면 모든 repo를 선택하거나 여러 토큰을 사용해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 12. 실무 팁

### git merge vs gh pr merge

로컬 `git merge`와 `gh pr merge`는 결과는 같지만(브랜치 합침) **프로세스가 다릅니다.**

| 항목              | `git merge` (로컬) | `gh pr merge` (GitHub)              |
|-------------------|--------------------|-------------------------------------|
| 실행 위치         | 내 PC              | GitHub 서버                         |
| 리뷰/승인         | 없음 (바로 머지)   | PR 리뷰 프로세스 거침               |
| branch protection | 우회됨 (로컬)      | 적용됨 (CI 통과, 리뷰 필수 등)      |
| 기록              | git log에만 남음   | PR #번호 + 코멘트 + 리뷰 이력       |
| CI 확인           | 안 함              | required checks 통과 필수 (설정 시) |
| 알림              | 없음               | 팀원에게 알림 발송                  |
| 롤백              | `git reset`        | GitHub "Revert" 버튼 1클릭          |

```bash
# 로컬 merge (혼자 작업, 빠르게)
git checkout main
git merge yunli
git push origin main

# gh pr merge (팀 협업, 코드 리뷰)
gh pr create --base main --head yunli --title "feat: 기능"
# → 리뷰어 승인 + CI 통과 후
gh pr merge --squash --delete-branch
```

| 상황                    | 추천          |
|-------------------------|---------------|
| 혼자 작업, 빠르게       | `git merge`   |
| 팀 협업, 코드 리뷰 필요 | `gh pr merge` |
| main 보호 설정 있음     | `gh pr merge` |
| 이력 추적 필요          | `gh pr merge` |

### PR 생성 자동화

```bash
# git log에서 PR body 자동 생성
gh pr create --title "feat: 기능" --body "$(git log main..HEAD --oneline)"

# 마지막 커밋 메시지를 PR 제목으로
gh pr create --title "$(git log -1 --format=%s)" --fill

# --fill: 커밋에서 title+body 자동 채움
gh pr create --fill
```

### 반복 작업 자동화

```bash
# 모든 열린 PR의 CI 상태 확인
gh pr list --json number,title,statusCheckRollup --jq   '.[] | "\(.number) \(.title) → \(.statusCheckRollup[0].conclusion // "pending")"'

# 리뷰 대기 중인 PR 수
gh pr list --search "review-requested:@me" --json number --jq 'length'

# 오래된 브랜치 정리 (머지된 PR의 원격 브랜치)
gh pr list --state merged --json headRefName --jq '.[].headRefName' |   xargs -I{} git push origin --delete {}
```

### co-author 추가

```bash
# 커밋에 co-author 포함 후 PR
git commit -m "feat: 기능

Co-authored-by: colleague <colleague@example.com>"
gh pr create --fill
```

### 멀티 repo 일괄 작업

```bash
# org의 모든 repo에서 특정 workflow 실행
gh repo list my-org --json name --jq '.[].name' | while read repo; do
  gh workflow run ci.yml --repo "my-org/$repo" 2>/dev/null && echo "✓ $repo"
done
```

[⬆ 목차로 돌아가기](#목차)

---

## 13. 트러블슈팅

| 에러                                | 원인                       | 해결                                                       |
|-------------------------------------|----------------------------|------------------------------------------------------------|
| `HTTP 401: Bad credentials`         | 토큰 만료 또는 무효        | `gh auth login` 재인증                                     |
| `HTTP 403: Resource not accessible` | scope/permission 부족      | `gh auth refresh --scopes` 또는 Fine-grained PAT 권한 추가 |
| `HTTP 403: secondary rate limit`    | 단시간 과다 요청           | 1~2분 대기 후 재시도, `--paginate` 시 간격 추가            |
| `HTTP 422: Validation Failed`       | PR 제목/body 규칙 위반     | branch protection 규칙 확인                                |
| `could not determine base repo`     | git remote 미설정          | `gh repo set-default owner/repo`                           |
| `GraphQL: Resource not accessible`  | Fine-grained PAT 권한 부족 | 필요 permission 추가 발급                                  |
| 2FA 강제 에러                       | org이 2FA 필수 설정        | `gh auth login` (브라우저 인증 사용)                       |
| proxy 환경 접속 불가                | HTTPS_PROXY 미설정         | `export HTTPS_PROXY=http://proxy:8080`                     |
| SSL certificate error               | 사내 인증서 문제           | `gh config set http_unix_socket ""` 또는 `GH_HOST` 설정    |
| `gh: command not found`             | PATH 미등록                | `which gh` 확인, shell rc 파일에 PATH 추가                 |

### rate limit 확인

```bash
# 현재 API 사용량 확인
gh api rate_limit --jq '.rate | "remaining: \(.remaining)/\(.limit), reset: \(.reset | todate)"'
```

### 디버그 모드

```bash
# 요청/응답 상세 출력 (문제 진단용)
GH_DEBUG=api gh pr list
```

### 인증 초기화

```bash
# 모든 인증 정보 삭제 후 재설정
gh auth logout
rm -rf ~/.config/gh/
gh auth login
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- GitHub CLI Manual: [cli.github.com/manual](https://cli.github.com/manual/) — ★★★☆☆
- GitHub CLI Releases: [github.com/cli/cli/releases](https://github.com/cli/cli/releases) — ★★☆☆☆
- [git_guide.md](./git_guide.md)
- [github_actions.md](./github_actions.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-06

**마지막 업데이트**: 2026-07-06

© 2026 siasia86. Licensed under CC BY 4.0.
