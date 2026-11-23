---
name: github-official-notes
description: GitHub의 계정 보안(2FA), SSH 키 연결, 저장소 보호(ruleset·branch protection), gh CLI의 공식 문서 기준 사실 정리.
tags:
  - git
  - github
last_checked: 2026-11-23
sources:
  - https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication
  - https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
  - https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection
  - https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
  - https://github.com/cli/cli/releases
---

# GitHub 공식 참조 노트

## 1. 공식 소스

| 소스                | URL                                                                                                                                          | 용도             |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| Mandatory 2FA       | https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication | 2FA 의무화       |
| SSH key 생성        | https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent              | 키 생성 명령     |
| SSH 연결 시험       | https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection                                          | 연결 확인        |
| Rulesets            | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets                  | 브랜치·태그 보호 |
| GitHub CLI releases | https://github.com/cli/cli/releases                                                                                                          | gh 판            |

## 2. 검증된 사실 (2026-11-23)

| 항목           | 값                                                                                               | 출처          |
|----------------|--------------------------------------------------------------------------------------------------|---------------|
| 2FA 의무화     | 2023년 3월부터 GitHub.com에 코드를 기여하는 모든 사용자에게 2FA 요구                             | Mandatory 2FA |
| SSH 키 생성    | `ssh-keygen -t ed25519 -C "메일"`. Ed25519를 못 쓰는 옛 시스템은 `-t rsa -b 4096`                | SSH key 생성  |
| SSH 연결 시험  | `ssh -T git@github.com` → "successfully authenticated, but GitHub does not provide shell access" | SSH 연결 시험 |
| Rulesets       | 브랜치·태그에 대한 동작을 제어. branch protection 규칙과 함께 적용되며 해당 규칙이 모두 적용됨   | Rulesets      |
| gh CLI 최신 판 | v2.105.0 (2026-11-18)                                                                            | cli releases  |

## 3. 검증 기록

- 1차: docs.github.com 문서와 cli/cli release에서 확인했습니다.
- 2차: 같은 사실을 SSH 연결 시험 문서의 예상 출력, rulesets 문서의 "branch protection과 함께" 문구로 다시 대조했습니다. GitHub는 계정이 필요한 서비스라 이 세션 계정으로 실행 시험은 하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
