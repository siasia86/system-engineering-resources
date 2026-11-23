# GitHub
<!-- reference: _reference/github_official_notes.md -->

Git 저장소를 호스팅하고 Pull Request로 코드 검토와 병합을 하는 서비스입니다. 이 문서만으로 계정 보안 설정 → SSH 키 연결 → 저장소 만들기와 Pull Request 흐름 → 브랜치 보호 → 검증까지 따라 할 수 있게 썼습니다. 자동화(Actions)와 gh 명령 상세는 함께 보기 문서에 있습니다.

- 기준: GitHub.com, GitHub CLI v2.105.0 (2026-11-23 확인)
- 예제 시험: 미실행(계정이 필요한 서비스). 명령과 예상 출력은 docs.github.com과 대조했습니다

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 계정 보안](#2-계정-보안) / [3. SSH 키 연결](#3-ssh-키-연결)                         |
| [4. 저장소와 Pull Request](#4-저장소와-pull-request) / [5. 브랜치 보호](#5-브랜치-보호) / [6. 토큰](#6-토큰) |
| [7. 검증](#7-검증) / [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기)                                |

---

## 1. 개요

| 기능            | 내용                                            |
|-----------------|-------------------------------------------------|
| 저장소          | 공개·비공개 Git 저장소                          |
| Pull Request    | 브랜치 변경을 검토·토론한 뒤 병합               |
| Issues·Projects | 작업 추적                                       |
| Actions         | CI/CD 워크플로 실행                             |
| 보안 기능       | 비밀값 탐지, 의존성 경고(Dependabot), 코드 스캔 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 계정 보안

- 2FA: 2023년 3월부터 코드를 기여하는 모든 사용자에게 2단계 인증이 요구됩니다. 인증 앱(TOTP)이나 보안 키(패스키)를 쓰고, 복구 코드를 안전한 곳에 보관합니다.
- 조직 계정이면 조직 설정에서 구성원 2FA를 강제합니다.
- 개인 PC가 아닌 서버에서는 개인 계정 키 대신 저장소 단위 배포 키(Deploy key)나 GitHub App을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. SSH 키 연결

```bash
ssh-keygen -t ed25519 -C "you@example.com"      # 옛 시스템은 -t rsa -b 4096
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub                       # 이 공개 키를 Settings > SSH and GPG keys에 등록
ssh -T git@github.com
# Hi <사용자>! You've successfully authenticated, but GitHub does not provide shell access.
```

GitHub CLI로 로그인하면 키 등록까지 한 번에 할 수 있습니다.

```bash
gh auth login             # GitHub.com → SSH → 키 선택·업로드 → 브라우저 인증
gh auth status
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 저장소와 Pull Request

```bash
gh repo create myapp --private --clone       # 저장소 만들고 내려받기
cd myapp
git switch -c feature/login                  # 작업 브랜치
# ... 수정 ...
git add -A && git commit -m "feat: 로그인 추가"
git push -u origin feature/login
gh pr create --fill --base main              # Pull Request 만들기 (제목·본문은 commit에서)
gh pr checks                                 # Actions 결과
gh pr merge --squash --delete-branch         # 검토가 끝나면 병합
```

| 병합 방식    | 결과                                       |
|--------------|--------------------------------------------|
| Merge commit | 브랜치 이력을 그대로 두고 병합 commit 추가 |
| Squash       | 브랜치 변경을 commit 하나로 합침           |
| Rebase       | 브랜치 commit을 main 위에 다시 쌓음        |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 브랜치 보호

저장소 Settings > Rules > Rulesets(또는 Branches의 branch protection)에서 `main`에 다음을 걸어 둡니다. Rulesets와 branch protection은 함께 적용되며, 해당하는 규칙이 모두 적용됩니다.

| 규칙                   | 효과                             |
|------------------------|----------------------------------|
| Require a pull request | main에 직접 push 금지, 검토 필수 |
| Required approvals     | 승인 수                          |
| Require status checks  | Actions 등 검사 통과 후 병합     |
| Block force pushes     | 이력 덮어쓰기 금지               |
| Restrict deletions     | 브랜치 삭제 금지                 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 토큰

HTTPS나 API 자동화에는 비밀번호 대신 토큰을 씁니다.

| 종류                               | 쓰는 곳                                       |
|------------------------------------|-----------------------------------------------|
| Fine-grained personal access token | 저장소·권한·만료일을 좁혀 발급 (권장)         |
| Actions의 `GITHUB_TOKEN`           | 워크플로 안에서 자동 발급, 실행이 끝나면 만료 |
| Deploy key                         | 서버가 저장소 하나만 읽고 쓸 때 (SSH)         |

토큰은 저장소·로그에 남기지 않고, 필요한 최소 권한과 짧은 만료일로 발급합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 검증

| 순서 | 확인 내용   | 명령                          | 기대 결과                              |
|------|-------------|-------------------------------|----------------------------------------|
| 1    | SSH 연결    | `ssh -T git@github.com`       | `successfully authenticated` 메시지    |
| 2    | CLI 로그인  | `gh auth status`              | 로그인한 계정과 범위                   |
| 3    | 원격 주소   | `git remote -v`               | `git@github.com:<소유자>/<저장소>.git` |
| 4    | push        | `git push -u origin <브랜치>` | 오류 없음                              |
| 5    | PR 검사     | `gh pr checks`                | 모든 검사 pass                         |
| 6    | 브랜치 보호 | main에 직접 `git push`        | 규칙 위반으로 거부됨                   |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                      | 원인                          | 해결 방법                                         |
|-------------------------------------------|-------------------------------|---------------------------------------------------|
| `Permission denied (publickey)`           | 키 미등록, 에이전트에 키 없음 | `ssh-add -l` 확인, 공개 키 등록, `ssh -vT`로 진단 |
| HTTPS push에서 비밀번호 거부              | 비밀번호 인증 미지원          | 토큰 또는 SSH 사용                                |
| `protected branch hook declined`          | 브랜치 보호 규칙              | 브랜치를 만들어 Pull Request로 병합               |
| `gh: command not found`                   | GitHub CLI 미설치             | 공식 저장소 패키지로 설치                         |
| 서버에서 개인 키를 쓰다 퇴사·교체 시 문제 | 개인 계정에 묶인 키           | Deploy key·GitHub App으로 전환                    |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Git 가이드](./git_guide.md) · [Git 명령 참조](./git_command_reference.md) — Git 자체 사용법
- [GitHub CLI 명령 참조](./gh_command_reference.md) — gh 명령 상세
- [GitHub Actions](./github_actions.md) — 워크플로 작성
- [GitLab](./gitlab.md) · [Git 호스팅 비교](./git_hosting_comparison.md) — 다른 호스팅 서비스
- [Git 이력 민감 파일 제거](./git_history_sensitive_file_removal.md) — 실수로 올린 비밀값 대응

---

## 참고 자료

- GitHub Docs: [About mandatory two-factor authentication](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication) — ★★★☆☆
- GitHub Docs: [Generating a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) · [Testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection) — ★★★☆☆
- GitHub Docs: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) — ★★★☆☆
- GitHub: [GitHub CLI releases](https://github.com/cli/cli/releases) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
