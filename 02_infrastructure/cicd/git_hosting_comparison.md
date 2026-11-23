# Git 호스팅 비교 (GitHub·GitLab·Bitbucket)
<!-- reference: _reference/github_official_notes.md, _reference/gitlab_official_notes.md, _reference/bitbucket_official_notes.md -->

Git 저장소 호스팅 서비스 세 가지를 운영 관점에서 비교하고 고르는 기준을 정리한 문서입니다. 상용 서비스는 계정·비용 없이 확인할 수 있는 공식 자료 범위만 다룹니다. GitHub와 GitLab은 각각의 문서에서 설정과 검증 절차를 다루고, Bitbucket은 이 문서의 비교와 이전 시 확인 사항만 둡니다.

- 기준: 2026-11-23 각 공식 사이트·문서
- 예제 시험: 해당 없음(비교 문서). 요금은 바뀔 수 있으므로 결정 전에 공식 요금 페이지를 다시 확인합니다

## 목차

| 섹션                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| [1. 한눈에 비교](#1-한눈에-비교) / [2. 기능 비교](#2-기능-비교) / [3. 고르는 기준](#3-고르는-기준)        |
| [4. 이전할 때 확인할 것](#4-이전할-때-확인할-것) / [5. 확인 방법](#5-확인-방법) / [함께 보기](#함께-보기) |

---

## 1. 한눈에 비교

| 항목                | GitHub                         | GitLab                         | Bitbucket                               |
|---------------------|--------------------------------|--------------------------------|-----------------------------------------|
| 운영사              | GitHub (Microsoft)             | GitLab                         | Atlassian                               |
| SaaS                | GitHub.com                     | GitLab.com                     | Bitbucket Cloud (Free는 사용자 5명까지) |
| 자체 설치           | GitHub Enterprise Server(유료) | Self-Managed (CE 무료, EE)     | Data Center (유료, 영업 문의)           |
| 코드 검토 단위      | Pull Request                   | Merge Request                  | Pull Request                            |
| CI/CD               | GitHub Actions                 | GitLab CI/CD                   | Bitbucket Pipelines                     |
| 함께 쓰기 좋은 도구 | GitHub 생태계, 오픈소스        | 하나의 제품에 계획·CI·보안까지 | Jira·Confluence                         |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 기능 비교

| 기능                | GitHub                         | GitLab                         | Bitbucket                 |
|---------------------|--------------------------------|--------------------------------|---------------------------|
| 브랜치 보호         | Rulesets, branch protection    | Protected branches             | Branch restrictions       |
| CI 정의 파일        | `.github/workflows/*.yml`      | `.gitlab-ci.yml`               | `bitbucket-pipelines.yml` |
| 자체 러너           | Self-hosted runner             | GitLab Runner                  | Runners                   |
| 컨테이너 레지스트리 | GitHub Packages (ghcr.io)      | Container Registry             | Bitbucket Packages        |
| CLI                 | `gh`                           | `glab`                         | -                         |
| 2단계 인증          | 코드 기여자 의무 (2023-03부터) | 사용자·그룹 설정으로 강제 가능 | 계정 설정                 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 고르는 기준

| 상황                                            | 후보                                                                  |
|-------------------------------------------------|-----------------------------------------------------------------------|
| 오픈소스, 외부 기여자, 넓은 Actions·통합 생태계 | GitHub                                                                |
| 사내망에서 무료로 자체 설치, CI까지 한 제품으로 | GitLab CE (Self-Managed)                                              |
| 이미 Jira·Confluence 중심으로 일하는 팀         | Bitbucket Cloud                                                       |
| 데이터 위치·외부 연결 제한이 엄격함             | 자체 설치형 (GitLab, GitHub Enterprise Server, Bitbucket Data Center) |
| 운영 인력이 적음                                | SaaS (자체 설치는 백업·업그레이드를 직접 해야 함)                     |

자체 설치형은 서버 비용뿐 아니라 백업, 업그레이드, 보안 패치, 장애 대응 인력까지 비용에 넣어 비교합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 이전할 때 확인할 것

| 항목         | 확인 내용                                                                     |
|--------------|-------------------------------------------------------------------------------|
| 저장소 이력  | `git clone --mirror` 후 새 원격에 `git push --mirror`로 모든 브랜치·태그 이전 |
| 대용량 파일  | Git LFS 객체는 따로 옮겨야 함 (`git lfs fetch --all`, `git lfs push --all`)   |
| 이슈·PR·위키 | 서비스마다 가져오기 도구가 다르고 일부 정보는 옮겨지지 않을 수 있음           |
| CI 정의      | 정의 파일 형식이 달라 다시 작성 (2절 표)                                      |
| 비밀값       | CI 변수·토큰은 옮겨지지 않으므로 새 서비스에서 다시 등록                      |
| 연동         | 웹훅, 배포 키, 외부 서비스 연결 다시 설정                                     |

```bash
git clone --mirror git@old.example.com:team/app.git
cd app.git
git remote set-url --push origin git@new.example.com:team/app.git
git push --mirror
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 확인 방법

| 순서 | 확인 내용      | 방법                                                | 기대 결과                     |
|------|----------------|-----------------------------------------------------|-------------------------------|
| 1    | 요금·사용자 수 | 각 서비스 공식 요금 페이지                          | 팀 규모에서의 월 비용         |
| 2    | 필수 기능      | 2절 표를 팀 요구 사항과 대조                        | 빠진 기능 없음                |
| 3    | 이전 결과      | 새 원격에서 `git ls-remote --heads --tags`          | 옛 원격과 같은 브랜치·태그 수 |
| 4    | CI             | 새 서비스에서 파이프라인 한 번 실행                 | 성공                          |
| 5    | 권한           | 새 서비스에서 일반 사용자가 보호 브랜치에 직접 push | 거부됨                        |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [GitHub](./github.md) — 계정 보안, SSH, Pull Request, 브랜치 보호
- [GitLab](./gitlab.md) — 자체 설치와 운영
- [GitHub Actions](./github_actions.md) · [GitLab CI/CD](./gitlab_ci.md) — CI 정의 파일
- [Git 명령 참조](./git_command_reference.md) — mirror, remote 명령

---

## 참고 자료

- GitHub Docs: [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) — ★★★☆☆
- GitLab Docs: [Installation requirements](https://docs.gitlab.com/install/requirements/) — ★★★☆☆
- Atlassian: [Bitbucket pricing](https://www.atlassian.com/software/bitbucket/pricing) · [Bitbucket Data Center](https://www.atlassian.com/software/bitbucket/enterprise) — ★★★☆☆

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
