# gitleaks 가이드
<!-- reference: _reference/gitleaks_official_notes.md -->

## 목차

| 섹션                                                                       |
|----------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 기본 사용법](#3-기본-사용법) |
| [4. 설정 파일](#4-설정-파일) / [5. git hook 연동](#5-git-hook-연동)        |
| [6. CI/CD 연동](#6-cicd-연동) / [7. 운영 팁](#7-운영-팁)                   |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

gitleaks는 git 저장소에서 API 키, 패스워드, 토큰 등 민감 정보를 탐지하는 오픈소스 도구입니다.

| 항목      | 내용                                 |
|-----------|--------------------------------------|
| 언어      | Go                                   |
| 라이선스  | MIT                                  |
| 최신 버전 | v8.30.1 (2026-08-19 확인)            |
| GitHub    | https://github.com/gitleaks/gitleaks |

### 주요 기능

- git 커밋 히스토리 전체 스캔
- 현재 작업 디렉토리(unstaged) 스캔
- 정규식 기반 커스텀 규칙
- `pre-commit` hook 통합
- SARIF 출력 (GitHub Advanced Security 연동)

[⬆ 목차로 돌아가기](#목차)

## 2. 설치

### 바이너리 직접 설치 (권장)

```bash
# 최신 버전 확인
curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest \
  | grep '"tag_name"' | cut -d'"' -f4

# 다운로드 및 설치 (v8.30.1 기준)
VERSION="v8.30.1"
curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/${VERSION}/gitleaks_${VERSION#v}_linux_x64.tar.gz" \
  | sudo tar -xz -C /usr/local/bin gitleaks

# 실행 권한 확인
gitleaks version
```

### 설치 확인

```bash
gitleaks version
# v8.30.1
```

[⬆ 목차로 돌아가기](#목차)

## 3. 기본 사용법

### 스캔 모드

| 모드  | 명령어                      | 설명                              |
|-------|-----------------------------|-----------------------------------|
| `git` | `gitleaks git`              | 현재 디렉토리 git 히스토리 스캔   |
| `git` | `gitleaks git --pre-commit` | 추적 중인 unstaged 변경사항 스캔  |
| `git` | `gitleaks git --staged`     | staged 변경사항 스캔 (pre-commit) |
| `dir` | `gitleaks dir .`            | git 없는 디렉토리 스캔            |

🟡 v8.19.0부터 `detect`와 `protect`는 deprecated입니다. 기존 명령과의 호환성을 위해 동작하지만, 신규 구성에서는 `git`, `dir`, `stdin` 모드를 우선 사용합니다.

### 기본 실행

```bash
# git 저장소 히스토리 전체 스캔
gitleaks git

# 현재 디렉토리 (git 없이)
gitleaks dir .

# staged 파일만 (commit 직전)
gitleaks git --staged

# 특정 커밋 범위
gitleaks git --log-opts="HEAD~10..HEAD"
```

### 출력 예시

```
○
    │╲
    │ ○
    ○ ░
    ░    gitleaks

Finding:     AKIAIOSFODNN7EXAMPLE
Secret:      AKIAIOSFODNN7EXAMPLE
RuleID:      aws-access-token
Entropy:     3.08
File:        config/aws.json
Line:        5
Commit:      a1b2c3d4
Author:      user@example.com
Date:        2026-05-07T10:00:00Z
Fingerprint: a1b2c3d4:config/aws.json:aws-access-token:5

1 leak(s) detected
```

### 주요 옵션

| 옵션                     | 설명                                                           |
|--------------------------|----------------------------------------------------------------|
| `-v, --verbose`          | 상세 출력                                                      |
| `-r, --report-path`      | 결과 파일 저장 경로                                            |
| `-f, --report-format`    | 출력 형식 (`json`, `csv`, `sarif`, `junit`)                    |
| `--baseline-path`        | baseline 파일 지정 (기존 탐지 결과 제외)                       |
| `--config`               | 커스텀 설정 파일 지정                                          |
| `--max-target-megabytes` | 스캔 파일 크기 제한                                            |
| `--redact`               | 출력에서 시크릿 값 마스킹                                      |
| `-l, --log-level`        | 로그 레벨 (`trace`, `debug`, `info`, `warn`, `error`, `fatal`) |

```bash
# JSON 리포트 저장
gitleaks git --redact -r /tmp/gitleaks-report.json -f json

# 시크릿 값 마스킹 출력
gitleaks git --redact

# 특정 설정 파일 사용
gitleaks git --config .gitleaks.toml
```

[⬆ 목차로 돌아가기](#목차)

## 4. 설정 파일

`.gitleaks.toml`을 저장소 루트에 배치하면 대상 경로 기준으로 자동 로드됩니다. 설정 파일을 명시하면 저장소 루트의 설정 대신 지정한 파일을 사용합니다.

### 설정 로드 우선순위

| 순위 | 설정 방법                    | 설명                                |
|------|------------------------------|-------------------------------------|
| 1    | `--config` 또는 `-c`         | 명령행에서 지정한 설정 파일         |
| 2    | `GITLEAKS_CONFIG`            | 설정 파일 경로를 지정하는 환경 변수 |
| 3    | `GITLEAKS_CONFIG_TOML`       | TOML 내용을 직접 전달하는 환경 변수 |
| 4    | 대상 경로의 `.gitleaks.toml` | 저장소 또는 스캔 대상의 설정 파일   |
| 5    | 바이너리 기본 설정           | 위 설정이 모두 없을 때 사용         |

### 기본 구조

현재 프로젝트에서 사용하는 설정은 다음 구조입니다.

```toml
# .gitleaks.toml
title = "gitleaks config"
minVersion = "v8.30.1"

[extend]
useDefault = true

[[allowlists]]
description = "global allowlist"
regexes = [
    # placeholder values
    '''Secureuser123''',
    '''SecurePassword123''',
    '''SecureKey123''',
    '''SecureToken123''',
    '''SecureDbName123''',
    '''sk-1234567890abcdef''',
    # RFC 5737 documentation IP ranges
    '''192\.0\.2\.\d+''',
    '''198\.51\.100\.\d+''',
    '''203\.0\.113\.\d+''',
    # 코드 예시 전화번호
    '''010-1234-5678''',
]
paths = [
    '''12_tech_stack/kubernetes_basic\.md''',
    '''.*_test\.py''',
    '''.*\.example''',
    '''.*\.sample''',
    '''.*_example\..*''',
]

# 한국 휴대폰 번호
[[rules]]
id = "korean-phone-number"
description = "Korean mobile phone number"
regex = '''010[-\s]?[0-9]{3,4}[-\s]?[0-9]{4}'''
tags = ["pii", "phone"]
[[rules.allowlists]]
regexes = [
    '''01000000000''',
    '''01012345678''',
    '''010-1234-5678''',
]

# Slack Webhook URL
[[rules]]
id = "slack-webhook"
description = "Slack Webhook URL"
regex = '''hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+'''
tags = ["webhook", "slack"]

# 외부 IP 대역
[[rules]]
id = "company-external-ip"
description = "Company external IP range (112.x.x.x)"
regex = '''112\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'''
tags = ["network", "external"]
```

`[extend] useDefault = true`는 AWS Access Key, GitHub PAT, Slack Token 등 Gitleaks 기본 규칙을 상속합니다. 사용자 정의 `[[rules]]`는 기본 규칙과 함께 적용됩니다.

- `[[allowlists]]`: 모든 탐지 규칙에 적용되는 전역 예외입니다.
- `[[rules.allowlists]]`: 해당 `[[rules]]`에만 적용되는 규칙별 예외입니다.
- `minVersion`: 설정 기능을 지원하는 최소 Gitleaks 버전입니다. 정확한 버전 고정은 설치 스크립트와 CI에서 별도로 관리합니다.

🟡 `company-external-ip`는 `112.x.x.x` 전체를 탐지하므로 오탐 가능성이 높습니다. 실제 회사 IP 대역을 확인한 뒤 범위를 좁히거나 별도 네트워크 검사로 분리합니다.

### 설정 검증

```bash
gitleaks dir \
  --config .gitleaks.toml \
  --redact \
  --no-banner \
  .

# Git 이력 스캔
gitleaks git \
  --config .gitleaks.toml \
  --redact \
  --no-banner \
  .
```

### 내장 규칙 확인

v8.30.1에는 `gitleaks rules` 명령이 없습니다. 공식 기본 규칙은 다음 파일에서 확인합니다.

```bash
curl -fsSL https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml
```

[⬆ 목차로 돌아가기](#목차)

## 5. git hook 연동

Git Hook은 Git 명령 실행 시점에 자동으로 호출되는 로컬 실행 스크립트입니다. Git이 `pre-commit`, `pre-push` 같은 정확한 이름의 Hook을 실행하고, 해당 스크립트가 외부 도구인 Gitleaks를 호출하여 민감정보를 검사합니다.

### Hook 동작 범위

| Hook         | 실행 시점         | 검사 대상               | 실패 시     |
|--------------|-------------------|-------------------------|-------------|
| `pre-commit` | `git commit` 직전 | staged 변경사항         | commit 차단 |
| `pre-push`   | `git push` 직전   | remote에 없는 신규 커밋 | push 차단   |

`pre-commit`은 작업 트리 전체가 아니라 `git add`로 staged 상태가 된 내용만 검사합니다. `pre-push`는 Git이 표준 입력으로 전달하는 로컬 커밋과 원격 커밋의 SHA를 사용하여 전송 대상 범위를 결정합니다.

### 현재 프로젝트 구성

현재 프로젝트는 Hook을 저장소에 포함할 수 있도록 추적 가능한 `.githooks/` 디렉터리를 사용합니다.

```text
.githooks/
├── pre-commit
└── pre-push
```

다음 설정을 실행하면 현재 저장소에서 `.git/hooks/` 대신 `.githooks/`를 Hook 경로로 사용합니다.

```bash
git config --local core.hooksPath .githooks
```

설정과 실행 권한을 확인합니다.

```bash
git config --local --get core.hooksPath
ls -l .githooks/pre-commit .githooks/pre-push
```

`core.hooksPath`는 `.git/config`에 저장되는 로컬 설정이므로 push되지 않습니다. `.githooks/`의 Hook 파일은 일반 작업 트리 파일이므로 push되지만, 새로 clone한 사용자는 다음 명령을 한 번 실행해야 합니다.

```bash
git config --local core.hooksPath .githooks
```

`v8.30.1` CLI에는 `--install-hook` 옵션이 없습니다. Hook 파일을 저장소에 배치한 뒤 `core.hooksPath`를 설정하는 방식으로 설치합니다.

### pre-commit Hook

`pre-commit`은 커밋 직전에 `gitleaks git --staged --redact -v`로 staged 변경사항을 검사합니다. Gitleaks가 설치되지 않았거나 탐지 결과가 있으면 `exit 1`을 반환하여 커밋을 차단합니다.

#### 처리 흐름

1. `gitleaks` 설치 여부를 확인합니다.
2. staged 변경사항을 검사합니다.
3. 탐지 결과 또는 실행 오류가 있으면 커밋을 차단합니다.
4. 검사를 통과하면 커밋을 계속 진행합니다.

### pre-push Hook

`pre-push`는 커밋이 생성된 뒤 push 직전에 실행됩니다. 현재 브랜치 전체가 아니라 원격에 아직 없는 커밋 범위만 검사하므로 이미 원격에 존재하는 이전 커밋은 반복 검사하지 않습니다.

Git은 `pre-push` Hook의 표준 입력으로 다음 네 필드를 전달합니다.

| 필드         | 의미                                 |
|--------------|--------------------------------------|
| `local_ref`  | push할 로컬 브랜치 또는 태그         |
| `local_sha`  | push할 로컬 커밋 SHA                 |
| `remote_ref` | 원격 브랜치 또는 태그                |
| `remote_sha` | 원격에 이미 존재하는 마지막 커밋 SHA |

커밋 범위는 다음과 같이 결정됩니다.

- 일반 push: `${remote_sha}..${local_sha}`를 검사합니다.
- 신규 브랜치: `${local_sha} --not --remotes`로 원격 추적 브랜치에 없는 전체 커밋을 검사합니다.
- 원격 추적 브랜치가 없는 최초 push: `${local_sha}`부터 전체 이력을 검사합니다.
- 브랜치 삭제 push: `local_sha`가 0으로 채워지므로 검사를 건너뜁니다.

### Hook 검증

```bash
# Hook 관련 Git 설정 빠르게 확인
git config --list | grep -i hooks

# 설정 출처와 core.hooksPath 확인
git config --show-origin --get core.hooksPath

# Git이 실제로 사용하는 Hook 디렉터리 확인
git rev-parse --git-path hooks

# Hook Bash 문법 검사
bash -n .githooks/pre-commit
bash -n .githooks/pre-push

# Hook 파일과 실행 권한 확인
ls -l "$(git rev-parse --git-path hooks)"/pre-commit \
      "$(git rev-parse --git-path hooks)"/pre-push

# pre-commit 직접 실행
.githooks/pre-commit

# pre-push 범위 입력 형식 테스트
BRANCH=$(git symbolic-ref --short HEAD)
HEAD_SHA=$(git rev-parse HEAD)
printf 'refs/heads/%s %s refs/remotes/origin/%s %s\n' \
  "${BRANCH}" "${HEAD_SHA}" "${BRANCH}" "${HEAD_SHA}" \
  | .githooks/pre-push
```

### 운영 및 복구

`.git/hooks/`는 Git이 추적하지 않는 로컬 디렉터리이므로 팀 공유 Hook으로 사용하지 않습니다. 팀 공용 Hook은 `.githooks/`에 저장하고, clone 후 `core.hooksPath`를 설정합니다.

기존 `.git/hooks/`를 사용하던 환경에서 전환할 때는 활성 Hook을 먼저 백업한 뒤 제거합니다. `.githooks/`의 검증이 끝나기 전에 기존 Hook을 삭제하지 않습니다.

```bash
BACKUP_SUFFIX=$(date +%Y%m%d-%H%M%S)
for hook in pre-commit pre-push; do
    if [ -f ".git/hooks/${hook}" ]; then
        cp ".git/hooks/${hook}" ".git/hooks/${hook}.before-${BACKUP_SUFFIX}"
        rm ".git/hooks/${hook}"
    fi
done
git config --local core.hooksPath .githooks
```

기본 경로인 `.git/hooks/`로 되돌리려면 다음을 실행합니다.

```bash
git config --local --unset core.hooksPath
```

🟡 Hook은 `--no-verify` 옵션으로 우회할 수 있습니다. 중요한 보호 기능은 CI/CD 또는 서버 측 검사에서도 전체 이력이나 push 범위를 검사해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. CI/CD 연동

### GitHub Actions

```yaml
# .github/workflows/gitleaks.yml
name: gitleaks

on:
  push:
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6.1.0
        with:
          fetch-depth: 0  # 전체 히스토리 스캔을 위해 필요

      - uses: gitleaks/gitleaks-action@v3.0.0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_VERSION: 8.30.1
          # 조직 계정에서만 필요
          # GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
gitleaks:
  image: zricethezav/gitleaks:v8.30.1
  stage: test
  script:
    - gitleaks git --redact --no-banner -v .
  allow_failure: false
```

[⬆ 목차로 돌아가기](#목차)

## 7. 운영 팁

### baseline 파일로 기존 탐지 결과 관리

기존 저장소에 처음 도입 시 기존 탐지 결과를 baseline으로 저장하여 신규 추가분만 검사합니다.

🟡 v8.30.1의 baseline 비교는 finding의 `Match`와 `Secret` 필드에 의존할 수 있습니다. baseline 파일에는 민감정보가 포함될 수 있으므로 저장소에 commit하지 않고, 접근 권한을 제한한 별도 경로에서 관리합니다. baseline은 기존 탐지를 숨길 뿐 실제 자격증명을 폐기·교체하지 않습니다.

```bash
# baseline 생성 (기존 탐지 결과 저장)
gitleaks git -r baseline.json -f json
chmod 600 baseline.json

# baseline 기준으로 신규 탐지만 검사
gitleaks git --baseline-path baseline.json
```

### 탐지 결과 분석

```bash
# JSON 리포트 생성
gitleaks git --redact -r report.json -f json -v

# 탐지된 규칙 ID 목록
cat report.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
rules = sorted(set(r['RuleID'] for r in data))
for r in rules: print(r)
"
```

### 현재 스크립트와 역할 분담

| 항목                  | gitleaks         | `aws_security_check.sh`      |
|-----------------------|------------------|------------------------------|
| AWS 키/토큰 탐지      | ✅ 내장 규칙     | ✅                           |
| git 히스토리 스캔     | ✅               | ❌                           |
| AWS 리소스 ID 탐지    | 커스텀 규칙 필요 | ✅ (VPC, SG, ENI 등)         |
| S3 버킷명 탐지        | 커스텀 규칙 필요 | ✅                           |
| 대용량 파일 탐지      | ❌               | ✅ (`git_security_check.sh`) |
| `.map.json` 누락 검사 | ❌               | ✅                           |
| CI/CD 통합            | ✅ 내장          | 수동 설정                    |

🟡 gitleaks와 기존 스크립트를 함께 사용하면 탐지 범위가 보완됩니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- gitleaks: [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★★★☆
- Gitleaks 공식 README: [github.com/gitleaks/gitleaks#readme](https://github.com/gitleaks/gitleaks#readme) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-08

**마지막 업데이트**: 2026-08-19

© 2026 siasia86. Licensed under CC BY 4.0.
