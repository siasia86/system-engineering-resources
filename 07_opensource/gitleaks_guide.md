# gitleaks 가이드

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
| 최신 버전 | v8.30.1 (2026-05 기준)               |
| GitHub    | https://github.com/gitleaks/gitleaks |

### 주요 기능

- git 커밋 히스토리 전체 스캔
- 현재 작업 디렉토리(unstaged) 스캔
- 정규식 기반 커스텀 규칙
- `pre-commit` hook 통합
- SARIF 출력 (GitHub Advanced Security 연동)

[⬆ 목차로 돌아가기](#목차)

## 2. 설치

### 사전 준비: Go 설치

`go install` 방법을 사용하려면 Go가 설치되어 있어야 합니다.

```bash
# Go 최신 버전 확인
curl -s https://go.dev/VERSION?m=text

# 다운로드 및 설치 (예: go1.24.3)
VERSION="go1.24.3"
curl -sSL "https://dl.google.com/go/${VERSION}.linux-amd64.tar.gz" \
  | sudo tar -xz -C /usr/local

# 환경 변수 설정 (~/.bash_aliases)
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

source ~/.bashrc

## link 방식
ln -s /usr/local/go/bin/go /usr/local/bin/

# 설치 확인
go version
```

### 방법 1: 바이너리 직접 설치 (권장)

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

### 방법 2: deb 패키지 (Ubuntu/Debian)

```bash
# GitHub releases에서 deb 패키지 다운로드
VERSION="v8.30.1"
curl -sSLO "https://github.com/gitleaks/gitleaks/releases/download/${VERSION}/gitleaks_${VERSION#v}_linux_amd64.deb"
sudo dpkg -i gitleaks_${VERSION#v}_linux_amd64.deb
```

### 방법 3: go install

```bash
go install github.com/gitleaks/gitleaks/v8@latest
```

### 설치 확인

```bash
gitleaks version
# gitleaks version 8.30.1
```

[⬆ 목차로 돌아가기](#목차)

## 3. 기본 사용법

### 스캔 모드

| 모드      | 명령어                      | 설명                              |
|-----------|-----------------------------|-----------------------------------|
| `detect`  | `gitleaks detect`           | 현재 디렉토리 git 히스토리 스캔   |
| `protect` | `gitleaks protect`          | unstaged 변경사항 스캔            |
| `protect` | `gitleaks protect --staged` | staged 변경사항 스캔 (pre-commit) |
| `dir`     | `gitleaks dir .`            | git 없는 디렉토리 스캔            |

### 기본 실행

```bash
# git 저장소 히스토리 전체 스캔
gitleaks detect

# 현재 디렉토리 (git 없이)
gitleaks dir .

# staged 파일만 (commit 직전)
gitleaks protect --staged

# 특정 커밋 범위
gitleaks detect --log-opts="HEAD~10..HEAD"
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
| `--baseline-path`        | baseline 파일 지정 (오탐 제외)                                 |
| `--config`               | 커스텀 설정 파일 지정                                          |
| `--no-git`               | git 없이 파일 시스템 스캔                                      |
| `--max-target-megabytes` | 스캔 파일 크기 제한 (기본 0 = 무제한)                          |
| `--redact`               | 출력에서 시크릿 값 마스킹                                      |
| `-l, --log-level`        | 로그 레벨 (`trace`, `debug`, `info`, `warn`, `error`, `fatal`) |

```bash
# JSON 리포트 저장
gitleaks detect -r /tmp/gitleaks-report.json -f json

# 시크릿 값 마스킹 출력
gitleaks detect --redact

# 특정 설정 파일 사용
gitleaks detect --config .gitleaks.toml
```

[⬆ 목차로 돌아가기](#목차)

## 4. 설정 파일

`.gitleaks.toml`을 저장소 루트에 배치하면 자동으로 로드됩니다.

### 기본 구조

```toml
# .gitleaks.toml
title = "gitleaks config"

# 기본 규칙은 자동 포함됨 (별도 설정 불필요)
# 외부 config 상속 시:
# [extend]
# path = "/path/to/base-gitleaks.toml"

# 오탐 제외 (allowlist)
[allowlist]
description = "global allowlist"
regexes = [
    # 예시 값 제외
    '''SecurePassword123''',
    '''SecureToken123''',
    # RFC 5737 예제 IP
    '''192\.0\.2\.\d+''',
    '''198\.51\.100\.\d+''',
]
paths = [
    # 특정 파일 제외
    '''security_check\.conf''',
    '''test_.*\.py''',
    '''.*\.map\.json''',
]
commits = [
    # 특정 커밋 제외
    # "a1b2c3d4e5f6",
]

# 커스텀 규칙 추가
[[rules]]
id = "custom-aws-account-id"
description = "AWS Account ID"
regex = '''(?<![0-9])[0-9]{12}(?![0-9])'''
tags = ["aws", "account"]

  [[rules.allowlist]]
  regexes = [
      # 날짜/시간 형태 제외 (YYYYMMDDHHNN)
      '''20[0-9]{2}[01][0-9][0-3][0-9][0-9]{4}''',
  ]
```

### 내장 규칙 확인

```bash
# 적용 중인 규칙 목록 출력
gitleaks rules
```

[⬆ 목차로 돌아가기](#목차)

## 5. git hook 연동

### pre-commit hook 설치

```bash
# 저장소 루트에서 실행
gitleaks protect --staged --install-hook
```

위 명령어는 `.git/hooks/pre-commit`에 아래 내용을 추가합니다:

```bash
#!/bin/bash
gitleaks protect --staged --redact -v
```

### 수동 설치

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
gitleaks protect --staged --redact -v
if [ $? -ne 0 ]; then
    echo "gitleaks: sensitive data detected. Commit aborted."
    exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

### pre-push hook

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
gitleaks detect --redact -v
if [ $? -ne 0 ]; then
    echo "gitleaks: sensitive data detected in history. Push aborted."
    exit 1
fi
EOF
chmod +x .git/hooks/pre-push
```

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
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 전체 히스토리 스캔을 위해 필요

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
gitleaks:
  image: zricethezav/gitleaks:latest
  stage: test
  script:
    - gitleaks detect --source . -v
  allow_failure: false
```

[⬆ 목차로 돌아가기](#목차)

## 7. 운영 팁

### baseline 파일로 오탐 관리

기존 저장소에 처음 도입 시 기존 탐지 결과를 baseline으로 저장하여 신규 추가분만 검사합니다.

```bash
# baseline 생성 (기존 탐지 결과 저장)
gitleaks detect -r baseline.json -f json

# baseline 기준으로 신규 탐지만 검사
gitleaks detect --baseline-path baseline.json
```

### 탐지 결과 분석

```bash
# JSON 리포트 생성
gitleaks detect -r report.json -f json -v

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

⚠️ gitleaks와 기존 스크립트를 함께 사용하면 탐지 범위가 보완됩니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- gitleaks: [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★★★☆
- gitleaks docs: [gitleaks.io](https://gitleaks.io/docs/) — ★★★☆☆

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

**마지막 업데이트**: 2026-05-08

© 2026 siasia86. Licensed under CC BY 4.0.
