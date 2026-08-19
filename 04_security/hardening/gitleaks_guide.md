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
# 8.30.1
```

[⬆ 목차로 돌아가기](#목차)

## 3. 기본 사용법

### 스캔 모드

| 모드  | 명령어                      | 설명                              |
|-------|-----------------------------|-----------------------------------|
| `git` | `gitleaks git`              | 현재 디렉토리 git 히스토리 스캔   |
| `git` | `gitleaks git --pre-commit` | unstaged 변경사항 스캔            |
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
| `--no-git`               | git 없이 파일 시스템 스캔                                      |
| `--max-target-megabytes` | 스캔 파일 크기 제한                                            |
| `--redact`               | 출력에서 시크릿 값 마스킹                                      |
| `-l, --log-level`        | 로그 레벨 (`trace`, `debug`, `info`, `warn`, `error`, `fatal`) |

```bash
# JSON 리포트 저장
gitleaks git -r /tmp/gitleaks-report.json -f json

# 시크릿 값 마스킹 출력
gitleaks git --redact

# 특정 설정 파일 사용
gitleaks git --config .gitleaks.toml
```

[⬆ 목차로 돌아가기](#목차)

## 4. 설정 파일

`.gitleaks.toml`을 저장소 루트에 배치하면 자동으로 로드됩니다.

### 기본 구조

```toml
# .gitleaks.toml
title = "gitleaks config"

# 기본 규칙을 사용하려면 명시적으로 상속합니다.
[extend]
useDefault = true
# 외부 config 상속 시 `useDefault` 대신 다음을 사용합니다.
# path = "/path/to/base-gitleaks.toml"

# 오탐 제외 (allowlist)
[allowlist]
description = "global allowlist"
regexes = [
    # 문서 플레이스홀더 값 제외
    '''Secureuser123''',
    '''SecurePassword123''',
    '''SecureKey123''',
    '''SecureToken123''',
    '''SecureDbName123''',
    # RFC 5737 예제 IP
    '''192\.0\.2\.\d+''',
    '''198\.51\.100\.\d+''',
    '''203\.0\.113\.\d+''',
]
paths = [
    # 특정 파일 제외
    '''12_tech_stack/kubernetes_basic\.md''',
    '''.*_test\.py''',
    '''.*\.example''',
    '''.*\.sample''',
]
commits = [
    # 특정 커밋 제외
    # "a1b2c3d4e5f6",
]

# 커스텀 규칙 추가 예시 (실제 적용 전 충분한 테스트 필요)
# 주의: Go regex는 lookahead/lookbehind 미지원
# 아래 예시는 동작하지만 오탐 가능성이 높으므로 allowlist 설정 필수
# [[rules]]
# id = "custom-aws-account-id"
# description = "AWS Account ID (12-digit)"
# regex = '''["'\s][0-9]{12}["'\s]'''
# tags = ["aws", "account"]
# [rules.allowlist]
# regexes = [
#     '''20[0-9]{2}[01][0-9][0-3][0-9][0-9]{4}''',
# ]
```

### 내장 규칙 확인

v8.30.1에는 `gitleaks rules` 명령이 없습니다. 공식 기본 규칙은 다음 파일에서 확인합니다.

```bash
curl -fsSL https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml
```

[⬆ 목차로 돌아가기](#목차)

## 5. git hook 연동

Git Hook은 Git 명령 실행 시점에 자동으로 호출되는 로컬 스크립트입니다. Gitleaks를 Hook에 연결하면 커밋과 push 직전에 민감정보를 검사할 수 있습니다.

### Hook 동작 범위

| Hook         | 실행 시점         | 검사 대상               | 실패 시     |
|--------------|-------------------|-------------------------|-------------|
| `pre-commit` | `git commit` 직전 | staged 변경사항         | commit 차단 |
| `pre-push`   | `git push` 직전   | remote에 없는 신규 커밋 | push 차단   |

`pre-commit`은 작업 트리 전체가 아니라 `git add`로 staged 상태가 된 내용만 검사합니다. `pre-push`는 Git이 표준 입력으로 전달하는 로컬 커밋과 원격 커밋의 SHA를 사용하여 전송 대상 범위를 결정합니다.

### pre-commit hook 설치

`pre-commit`은 커밋 직전에 `git --staged` 모드로 staged 변경사항을 검사합니다. 시크릿이 탐지되거나 Gitleaks 실행에 실패하면 `exit 1`을 반환하여 커밋을 차단합니다.


v8.30.1 CLI에는 `--install-hook` 옵션이 없습니다. 저장소 루트에서 아래 수동 설치 방법을 사용합니다.

### 수동 설치

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# ============================================
# pre-commit hook - 민감정보 검사
# ============================================

if ! command -v gitleaks &> /dev/null; then
    echo ""
    echo "⚠️  gitleaks가 설치되지 않았습니다."
    echo "설치 방법:"
    echo "  - 바이너리: https://github.com/gitleaks/gitleaks/releases"
    echo "  - macOS: brew install gitleaks"
    echo ""
    exit 1
fi

gitleaks git --staged --redact -v
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "❌ 민감정보가 탐지되어 커밋이 차단되었습니다."
    echo "민감정보를 제거한 후 다시 커밋하세요."
    exit 1
fi

echo "✅ gitleaks 검사 통과"
exit 0
EOF
chmod +x .git/hooks/pre-commit
```

#### pre-commit 처리 흐름

1. `gitleaks` 설치 여부를 확인합니다.
2. `gitleaks git --staged --redact -v`로 staged 변경사항을 검사합니다.
3. 탐지 결과가 있거나 명령이 실패하면 `exit 1`로 커밋을 차단합니다.
4. 검사를 통과하면 `exit 0`으로 커밋을 계속 진행합니다.

### pre-push hook

`pre-push`는 커밋이 생성된 뒤 push 직전에 실행됩니다. 현재 브랜치 전체가 아니라 원격에 아직 없는 커밋 범위만 검사하므로, 이미 원격에 존재하는 이전 커밋은 반복 검사하지 않습니다.

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# ============================================
# pre-push hook - 신규 커밋 민감정보 검사
# ============================================

if ! command -v gitleaks &> /dev/null; then
    echo ""
    echo "⚠️  gitleaks가 설치되지 않았습니다."
    echo "설치 방법:"
    echo "  - 바이너리: https://github.com/gitleaks/gitleaks/releases"
    echo "  - macOS: brew install gitleaks"
    echo ""
    exit 1
fi

# stdin에서 push 대상 정보 읽기
# 형식: <local_ref> <local_sha> <remote_ref> <remote_sha>
while read -r local_ref local_sha remote_ref remote_sha; do
    # 브랜치 삭제 push는 스킵
    if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi

    # 신규 브랜치 (remote에 없음) → 직전 커밋까지만 스캔
    if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
        if git rev-parse "${local_sha}^" >/dev/null 2>&1; then
            LOG_OPTS="${local_sha}~1..${local_sha}"
        else
            # root commit은 부모가 없으므로 해당 커밋 자체를 스캔합니다.
            LOG_OPTS="${local_sha}"
        fi
    else
        LOG_OPTS="${remote_sha}..${local_sha}"
    fi

    gitleaks git --redact -v --log-opts "$LOG_OPTS"
    exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "❌ 민감정보가 탐지되어 push가 차단되었습니다."
        echo "위 내용을 확인하고 민감정보를 제거한 후 다시 push하세요."
        exit 1
    fi
done

echo "✅ gitleaks 검사 통과"
exit 0
EOF
chmod +x .git/hooks/pre-push
```

#### pre-push 입력과 커밋 범위

Git은 `pre-push` Hook의 표준 입력으로 다음 네 필드를 전달합니다.

| 필드         | 의미                                 |
|--------------|--------------------------------------|
| `local_ref`  | push할 로컬 브랜치 또는 태그         |
| `local_sha`  | push할 로컬 커밋 SHA                 |
| `remote_ref` | 원격 브랜치 또는 태그                |
| `remote_sha` | 원격에 이미 존재하는 마지막 커밋 SHA |

커밋 범위는 다음과 같이 결정됩니다.

- 일반 push: `${remote_sha}..${local_sha}`를 검사합니다.
- 신규 브랜치: 부모 커밋이 있으면 `${local_sha}~1..${local_sha}`를 검사합니다.
- 최초 커밋: 부모가 없으므로 `${local_sha}` 자체를 검사합니다.
- 브랜치 삭제 push: `local_sha`가 0으로 채워지므로 검사를 건너뜁니다.

### 주의사항 — hook의 git 미추적

`.git/hooks/`는 git이 추적하지 않는 디렉토리입니다. 저장소를 새로 clone하면 hook이 사라지므로 재설치가 필요합니다.

| 상황                       | 영향                                  | 대응                                         |
|----------------------------|---------------------------------------|----------------------------------------------|
| 저장소 신규 clone          | hook 없음 → 자동 스캔 미동작          | clone 후 hook 수동 재설치                    |
| 팀원 공유 필요             | 각자 재설치 필요                      | `scripts/install-hooks.sh` 스크립트로 자동화 |
| pre-commit 프레임워크 사용 | `.pre-commit-config.yaml`으로 팀 공유 | `pre-commit install` 한 번으로 자동 설치     |

#### hook 자동 설치 스크립트 예시

저장소에 `scripts/install-hooks.sh`를 추가하면 clone 후 한 번만 실행하면 됩니다.

```bash
#!/bin/bash
# scripts/install-hooks.sh
# clone 후 실행: bash scripts/install-hooks.sh

set -euo pipefail

# gitleaks 설치 여부 확인
if ! command -v gitleaks &> /dev/null; then
    echo "⚠️  gitleaks가 설치되지 않았습니다. 먼저 설치 후 실행하세요."
    echo "  - 바이너리: https://github.com/gitleaks/gitleaks/releases"
    exit 1
fi

HOOKS_DIR=".git/hooks"
BACKUP_SUFFIX=$(date +%Y%m%d-%H%M%S)

# 기존 hook 백업
for hook in pre-commit pre-push; do
    if [ -f "${HOOKS_DIR}/${hook}" ]; then
        backup_path="${HOOKS_DIR}/${hook}.bak.${BACKUP_SUFFIX}"
        cp "${HOOKS_DIR}/${hook}" "${backup_path}"
        echo "기존 ${hook} hook 백업: ${backup_path}"
    fi
done

cat > "${HOOKS_DIR}/pre-commit" << 'HOOK'
#!/bin/bash
if ! command -v gitleaks &> /dev/null; then
    echo "⚠️  gitleaks가 설치되지 않았습니다."
    exit 1
fi
gitleaks git --staged --redact -v
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "❌ 민감정보가 탐지되어 커밋이 차단되었습니다."
    exit 1
fi
echo "✅ gitleaks 검사 통과"
exit 0
HOOK

cat > "${HOOKS_DIR}/pre-push" << 'HOOK'
#!/bin/bash
if ! command -v gitleaks &> /dev/null; then
    echo "⚠️  gitleaks가 설치되지 않았습니다."
    exit 1
fi
while read -r local_ref local_sha remote_ref remote_sha; do
    if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi
    if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
        if git rev-parse "${local_sha}^" >/dev/null 2>&1; then
            LOG_OPTS="${local_sha}~1..${local_sha}"
        else
            # root commit은 부모가 없으므로 해당 커밋 자체를 스캔합니다.
            LOG_OPTS="${local_sha}"
        fi
    else
        LOG_OPTS="${remote_sha}..${local_sha}"
    fi
    gitleaks git --redact -v --log-opts "$LOG_OPTS"
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "❌ 민감정보가 탐지되어 push가 차단되었습니다."
        exit 1
    fi
done
echo "✅ gitleaks 검사 통과"
exit 0
HOOK

chmod +x "${HOOKS_DIR}/pre-commit" "${HOOKS_DIR}/pre-push"
echo "gitleaks hooks installed: pre-commit, pre-push"
```

#### Hook 검증

```bash
# Hook Bash 문법 검사
bash -n .git/hooks/pre-commit
bash -n .git/hooks/pre-push

# pre-commit 직접 실행
.git/hooks/pre-commit

# 현재 커밋 범위의 pre-push 검사
HEAD_SHA=$(git rev-parse HEAD)
printf 'refs/heads/main %s refs/remotes/origin/main %s\n' \
  "${HEAD_SHA}" "${HEAD_SHA}" \
  | .git/hooks/pre-push
```

🟡 Hook은 `--no-verify` 옵션으로 우회할 수 있습니다. CI/CD에서는 `--ignore-gitleaks-allow`와 전체 이력 또는 push 범위 검사를 병행해야 합니다.

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
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0  # 전체 히스토리 스캔을 위해 필요

      - uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # 조직 계정에서만 필요
          # GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
gitleaks:
  image: zricethezav/gitleaks:latest
  stage: test
  script:
    - gitleaks git -v .
  allow_failure: false
```

[⬆ 목차로 돌아가기](#목차)

## 7. 운영 팁

### baseline 파일로 기존 탐지 결과 관리

기존 저장소에 처음 도입 시 기존 탐지 결과를 baseline으로 저장하여 신규 추가분만 검사합니다.

```bash
# baseline 생성 (기존 탐지 결과 저장)
gitleaks git -r baseline.json -f json

# baseline 기준으로 신규 탐지만 검사
gitleaks git --baseline-path baseline.json
```

### 탐지 결과 분석

```bash
# JSON 리포트 생성
gitleaks git -r report.json -f json -v

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

**마지막 업데이트**: 2026-08-19

© 2026 siasia86. Licensed under CC BY 4.0.
