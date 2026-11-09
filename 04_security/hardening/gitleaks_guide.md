# gitleaks 가이드
<!-- reference: _reference/gitleaks_official_notes.md -->

## 목차

| 섹션                                                                       |
|----------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 기본 사용법](#3-기본-사용법) |
| [4. 설정 파일](#4-설정-파일) / [5. git hook 연동](#5-git-hook-연동)        |
| [6. CI/CD 연동](#6-cicd-연동) / [7. 운영 팁](#7-운영-팁)                   |
| [8. 탐지 후 대응](#8-탐지-후-대응)                                         |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

gitleaks는 git 저장소에서 API 키, 패스워드, 토큰 등 민감 정보를 탐지하는 오픈소스 도구입니다.

| 항목      | 내용                                 |
|-----------|--------------------------------------|
| 언어      | Go                                   |
| 라이선스  | MIT                                  |
| 최신 버전 | v8.30.1 (2026-11-03 확인)            |
| GitHub    | https://github.com/gitleaks/gitleaks |

### 주요 기능

- git 커밋 히스토리 전체 스캔
- 디렉토리·파일 스캔(`dir`)과 표준 입력 스캔(`stdin`)
- 정규식 기반 커스텀 규칙과 기본 규칙 상속
- 인코딩된 값 디코딩(percent·hex·base64)과 압축 파일 내부 스캔
- `pre-commit` hook 통합
- SARIF 출력 (GitHub Advanced Security 연동)

[⬆ 목차로 돌아가기](#목차)

## 2. 설치

### 바이너리 직접 설치 (권장)

릴리스에 함께 올라오는 `gitleaks_<버전>_checksums.txt`로 SHA-256을 확인한 뒤 설치합니다. 내려받은 파일을 바로 `sudo tar`로 풀지 않습니다.

```bash
# 최신 버전 확인
curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest \
  | grep '"tag_name"' | cut -d'"' -f4

# 다운로드 (v8.30.1 기준)
VERSION="v8.30.1"
BASE="https://github.com/gitleaks/gitleaks/releases/download/${VERSION}"
ASSET="gitleaks_${VERSION#v}_linux_x64.tar.gz"
WORK=$(mktemp -d)
curl -fsSL -o "${WORK}/${ASSET}" "${BASE}/${ASSET}"
curl -fsSL -o "${WORK}/checksums.txt" "${BASE}/gitleaks_${VERSION#v}_checksums.txt"

# 체크섬 확인 (OK가 나와야 다음 단계 진행)
(cd "${WORK}" && grep " ${ASSET}\$" checksums.txt | sha256sum -c -)

# 설치
sudo tar -xzf "${WORK}/${ASSET}" -C /usr/local/bin gitleaks
rm -rf "${WORK}"
```

### 다른 설치 방법

| 방법               | 명령                                                                           |
|--------------------|--------------------------------------------------------------------------------|
| Homebrew (macOS)   | `brew install gitleaks`                                                        |
| Docker (ghcr.io)   | `docker run --rm -v "$PWD":/path ghcr.io/gitleaks/gitleaks:v8.30.1 dir /path`  |
| Docker (DockerHub) | `docker run --rm -v "$PWD":/path zricethezav/gitleaks:v8.30.1 dir /path`       |
| 소스 빌드          | `git clone https://github.com/gitleaks/gitleaks.git` 후 `make build` (Go 필요) |

🟡 공식 README의 Docker 예시는 `latest` 태그를 씁니다. 운영 환경에서는 버전 태그를 고정해 결과가 바뀌지 않도록 합니다.

### 설치 확인

```bash
gitleaks version
# v8.30.1
```

[⬆ 목차로 돌아가기](#목차)

## 3. 기본 사용법

### 스캔 모드

| 모드    | 명령어                       | 설명                              |
|---------|------------------------------|-----------------------------------|
| `git`   | `gitleaks git`               | 현재 디렉토리 git 히스토리 스캔   |
| `git`   | `gitleaks git --pre-commit`  | 추적 중인 unstaged 변경사항 스캔  |
| `git`   | `gitleaks git --staged`      | staged 변경사항 스캔 (pre-commit) |
| `dir`   | `gitleaks dir .`             | git 없는 디렉토리 스캔            |
| `stdin` | `cat file \| gitleaks stdin` | 표준 입력으로 받은 내용 스캔      |

`git` 모드는 내부적으로 `git log -p`의 patch를 검사하므로 이력에 추가된 내용만 봅니다. 현재 파일 내용 전체를 보려면 `dir` 모드를 함께 사용합니다. `dir`은 `file`, `directory` 별칭도 받으며 기본적으로 symlink를 따라가지 않습니다(`--follow-symlinks`로 변경).

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

# 모든 branch의 이력
gitleaks git --log-opts="--all"

# 명령 출력이나 파일 한 개를 표준 입력으로 검사
cat app.env | gitleaks stdin --redact
```

### 출력 예시

탐지 항목별 상세는 `-v`를 붙였을 때 출력되며, `-v`가 없으면 배너와 마지막 요약 줄만 나옵니다.

```
    ○
    │╲
    │ ○
    ○ ░
    ░    gitleaks

Finding:     AKIAIOSFODNN7EXAMPLE
Secret:      AKIAIOSFODNN7EXAMPLE
RuleID:      aws-access-token
Entropy:     3.684184
File:        config/aws.json
Line:        5
Commit:      a1b2c3d4
Author:      user
Email:       user@example.com
Date:        2026-05-07T10:00:00Z
Fingerprint: a1b2c3d4:config/aws.json:aws-access-token:5

4:33PM INF 1 commits scanned.
4:33PM INF scanned ~125 bytes (125 bytes) in 25.3ms
4:33PM WRN leaks found: 1
```

🟡 위 값은 형식 설명용입니다. 실제 기본 규칙 `aws-access-token`은 `EXAMPLE`로 끝나는 값을 규칙별 허용 목록(`.+EXAMPLE$`)으로 제외하므로 이 값은 탐지되지 않습니다.

### 주요 옵션

| 옵션                         | 설명                                                           |
|------------------------------|----------------------------------------------------------------|
| `-v, --verbose`              | 상세 출력                                                      |
| `-r, --report-path`          | 결과 파일 저장 경로                                            |
| `-f, --report-format`        | 출력 형식 (`json`, `csv`, `sarif`, `junit`, `template`)        |
| `--baseline-path`            | baseline 파일 지정 (기존 탐지 결과 제외)                       |
| `--config`                   | 커스텀 설정 파일 지정                                          |
| `--max-target-megabytes`     | 스캔 파일 크기 제한                                            |
| `--redact`                   | 출력에서 시크릿 값 마스킹 (기본 100%, `--redact=20`은 일부만)  |
| `-l, --log-level`            | 로그 레벨 (`trace`, `debug`, `info`, `warn`, `error`, `fatal`) |
| `--no-banner`                | 시작 배너 생략                                                 |
| `--exit-code`                | 탐지 시 종료 코드 지정 (기본 1)                                |
| `--enable-rule`              | 지정한 규칙 ID만 실행                                          |
| `-i, --gitleaks-ignore-path` | `.gitleaksignore` 파일 또는 그 파일이 있는 폴더 지정           |
| `--max-decode-depth`         | 인코딩된 값 재귀 디코딩 깊이 (기본 5, 0이면 사용 안 함)        |
| `--max-archive-depth`        | 압축 파일 내부 재귀 스캔 깊이 (기본 0, 사용 안 함)             |
| `--timeout`                  | 명령 제한 시간(초, 기본 0은 제한 없음)                         |

```bash
# JSON 리포트 저장
gitleaks git --redact -r /tmp/gitleaks-report.json -f json

# 시크릿 값 마스킹 출력
gitleaks git --redact

# 특정 설정 파일 사용
gitleaks git --config .gitleaks.toml

# base64·hex·percent 인코딩 값의 재귀 디코딩 깊이 지정 (v8.30.0부터 기본 5, 0이면 끔)
gitleaks dir --max-decode-depth 2 --redact .

# zip·tar 등 압축 파일 내부까지 검사
gitleaks dir --max-archive-depth 2 --redact .
```

디코딩으로 찾은 결과에는 `decoded:<인코딩>`, `decode-depth:<깊이>` 태그가 붙습니다. 압축 파일 안에서 찾은 결과의 `File`은 `bundle.tar.gz!inner/.env`처럼 `!`로 내부 경로를 구분합니다.

### 종료 코드

| 코드  | 의미                     |
|-------|--------------------------|
| `0`   | 탐지 없음                |
| `1`   | 탐지 있음 또는 실행 오류 |
| `126` | 알 수 없는 옵션          |

탐지와 실행 오류가 모두 `1`이므로 스크립트에서 둘을 구분하려면 `--exit-code`로 탐지 코드를 바꿉니다. 예를 들어 `--exit-code 2`로 실행하면 `2`는 탐지, `1`은 오류로 볼 수 있습니다.

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

현재 프로젝트에서 사용하는 설정을 한 덩어리로 줄이면 다음 구조입니다. 실제 [.gitleaks.toml](../../.gitleaks.toml)은 중앙 공통 허용 목록과 `BEGIN/END CONSUMER LOCAL` 사이의 현장 허용 목록·규칙으로 나뉘어 있습니다.

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
    '''02_infrastructure/containers/kubernetes_basic\.md''',
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

### 설정 항목

최상위·`[extend]` 항목입니다.

| 항목                     | 설명                                                                       |
|--------------------------|----------------------------------------------------------------------------|
| `title`                  | 설정 이름(표시용)                                                          |
| `minVersion`             | 이 설정이 요구하는 최소 Gitleaks 버전                                      |
| `[extend] useDefault`    | 바이너리에 내장된 기본 설정 상속                                           |
| `[extend] path`          | 다른 설정 파일 상속. 경로는 기준 설정이 아니라 gitleaks를 실행한 위치 기준 |
| `[extend] disabledRules` | 상속한 규칙 중 끌 규칙 ID 목록 (예: `["generic-api-key"]`)                 |

🟡 `useDefault`와 `path`는 함께 쓸 수 없습니다. 상속은 2단계까지 이어 붙일 수 있고, 같은 ID의 규칙은 상속하는 쪽(현재 파일) 값이 우선합니다. 허용 목록 배열은 합쳐집니다.

`[[rules]]` 항목입니다.

| 항목          | 설명                                                                        |
|---------------|-----------------------------------------------------------------------------|
| `id`          | 규칙 고유 ID. 기본 규칙과 같은 ID를 쓰면 그 규칙을 덮어쓰거나 보완          |
| `description` | 규칙 설명                                                                   |
| `regex`       | 탐지 정규식. Go 정규식이라 lookahead·lookbehind를 지원하지 않음             |
| `secretGroup` | 정규식에서 시크릿으로 볼 capture group 번호(엔트로피 검사 대상)             |
| `entropy`     | 시크릿으로 인정할 최소 Shannon 엔트로피(예: `3.5`). 낮은 값의 오탐을 거름   |
| `path`        | 파일 경로 정규식. 단독(파일 존재 자체 탐지) 또는 `regex`와 함께 사용        |
| `keywords`    | 정규식 실행 전 빠른 문자열 필터. 이 단어가 없는 내용은 정규식 검사를 건너뜀 |
| `tags`        | 보고서용 메타데이터                                                         |

`[[allowlists]]`(전역)와 `[[rules.allowlists]]`(규칙별) 항목입니다.

| 항목          | 설명                                                                                    |
|---------------|-----------------------------------------------------------------------------------------|
| `description` | 예외 설명                                                                               |
| `commits`     | 제외할 commit SHA                                                                       |
| `paths`       | 제외할 파일 경로 정규식                                                                 |
| `regexes`     | 제외할 값의 정규식                                                                      |
| `regexTarget` | `regexes`를 대조할 대상. `secret`(기본), `match`(정규식 전체 일치), `line`(줄 전체)     |
| `stopwords`   | 추출된 시크릿에 이 단어가 들어 있으면 제외                                              |
| `condition`   | 여러 조건의 결합. `OR`(기본, 하나만 맞아도 제외) 또는 `AND`(모두 맞아야 제외)           |
| `targetRules` | 전역 `[[allowlists]]`를 지정한 규칙 ID에만 적용 (v8.25.0부터). 없는 ID면 설정 로드 실패 |

🟡 v8.25.0에서 전역 `[allowlist]`가 `[[allowlists]]`로, v8.21.0에서 `[rules.allowlist]`가 `[[rules.allowlists]]`로 바뀌었습니다. 오래된 예시를 옮길 때 형식을 맞춥니다. 전역 허용 목록이 규칙별 허용 목록보다 먼저 적용됩니다.

다음은 자주 쓰는 설정 조합입니다.

```toml
[extend]
useDefault = true
# 오탐이 많은 기본 규칙 끄기
disabledRules = ["generic-api-key"]

# 기본 규칙(gitlab-pat)을 같은 ID로 보완: 나머지 속성은 상속
[[rules]]
id = "gitlab-pat"
    [[rules.allowlists]]
    regexTarget = "line"
    regexes = ['''EXAMPLE-glpat-''']

# 테스트 자료 경로는 지정한 규칙에서만 제외
[[allowlists]]
targetRules = ["internal-api-token"]
description = "test fixtures"
paths = ['''tests/fixtures/.*\.json$''']

# 경로와 값이 모두 맞을 때만 제외
[[rules]]
id = "internal-api-token"
description = "Internal API token"
regex = '''itk_[A-Za-z0-9]{32}'''
keywords = ["itk_"]
entropy = 3.5
    [[rules.allowlists]]
    condition = "AND"
    paths = ['''docs/.*\.md''']
    regexes = ['''itk_0{32}''']
```

v8.28.0부터는 주 규칙 근처에 보조 규칙이 함께 있을 때만 탐지하는 `[[rules.required]]`(composite rule, `withinLines`·`withinColumns`)도 있습니다. 공식 README가 실험 기능으로 표시하므로 운영 규칙에는 신중히 사용합니다.

### 예외 처리 방법 선택

| 방법                   | 범위                            | 사용 시점                                      |
|------------------------|---------------------------------|------------------------------------------------|
| `[[allowlists]]`       | 경로·값·commit 단위의 반복 예외 | 예시 값·테스트 자료처럼 계속 나오는 오탐       |
| `[[rules.allowlists]]` | 특정 규칙에서만 예외            | 한 규칙의 오탐만 줄일 때                       |
| 줄 끝 `gitleaks:allow` | 해당 줄 하나                    | 의도적으로 넣은 테스트 값 한 줄                |
| `.gitleaksignore`      | 탐지 결과 하나(`Fingerprint`)   | 이미 이력에 남은 특정 탐지 하나를 제외할 때    |
| baseline               | 기존 보고서 전체                | 도입 초기에 기존 탐지를 두고 신규만 볼 때(7절) |

- `gitleaks:allow`는 주석 형태로 줄 끝에 붙입니다(예: `token = "SecureToken123"  # gitleaks:allow`). `--ignore-gitleaks-allow`로 실행하면 이 주석을 무시합니다.
- `.gitleaksignore`는 저장소 루트에 두고 보고서의 `Fingerprint` 값을 한 줄에 하나씩 적습니다. Fingerprint는 `git` 모드에서 `<commit>:<파일>:<규칙 ID>:<줄>`, `dir` 모드에서 `<파일>:<규칙 ID>:<줄>` 형식입니다. 공식 README는 실험 기능으로 표시합니다.
- 어떤 방법이든 실제 자격증명을 숨기는 용도로 쓰지 않습니다. 실제 값이면 [8절](#8-탐지-후-대응)의 대응을 먼저 합니다.

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

### pre-commit 프레임워크 사용 (대안)

[pre-commit](https://pre-commit.com/) 프레임워크를 이미 쓰는 저장소는 공식 hook ID `gitleaks`를 등록할 수 있습니다. Docker로 실행하려면 ID `gitleaks-docker`를 씁니다.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

```bash
pre-commit install
```

🟡 pre-commit 프레임워크는 기본 Hook 경로에 설치하므로 `core.hooksPath`를 설정한 저장소에서는 설치가 거부되거나 한쪽 Hook만 동작합니다. 두 방식 중 하나만 씁니다. 이 프로젝트는 `.githooks/` 방식을 사용합니다. 프레임워크에서는 `SKIP=gitleaks git commit ...`으로 검사를 건너뛸 수 있으므로 CI 검사를 함께 둡니다.

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
printf 'refs/heads/%s %s refs/heads/%s %s\n' \
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
      - uses: actions/checkout@v6.1.0  # 2026-11 기준 최신 메이저는 v7(v7.0.1), 갱신 시 릴리스 노트 확인
        with:
          fetch-depth: 0  # 전체 히스토리 스캔을 위해 필요

      - uses: gitleaks/gitleaks-action@v3.0.0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_VERSION: 8.30.1
          # 조직 계정에서만 필요
          # GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

🟡 `gitleaks-action@v2`는 Node 20 런타임이라 2026-09-16 GitHub 호스트 runner에서 Node 20이 제거된 뒤 동작하지 않습니다. v3(Node 24)로 올리고 `actions/checkout`도 v6 이상으로 맞춥니다. v3는 runner v2.327.1 이상이 필요하므로 self-hosted runner는 먼저 갱신합니다.

| 환경 변수                         | 설명                                                      |
|-----------------------------------|-----------------------------------------------------------|
| `GITLEAKS_LICENSE`                | 조직 계정 저장소에서 필요한 라이선스 키(개인 계정 불필요) |
| `GITLEAKS_CONFIG`                 | 사용할 설정 파일 경로                                     |
| `GITLEAKS_ENABLE_COMMENTS`        | PR 주석 작성 여부 (기본 `true`)                           |
| `GITLEAKS_ENABLE_UPLOAD_ARTIFACT` | 탐지 시 SARIF artifact 업로드 여부 (기본 `true`)          |
| `GITLEAKS_ENABLE_SUMMARY`         | job summary 표시 여부 (기본 `true`)                       |
| `GITLEAKS_NOTIFY_USER_LIST`       | 탐지 시 알릴 GitHub 계정 (`@user1,@user2`)                |

조직 라이선스 없이 실행하려면 Action 대신 2절의 체크섬 확인 방식으로 바이너리를 받아 `gitleaks git --redact --no-banner -v .`를 직접 실행합니다.

### GitLab CI

```yaml
# .gitlab-ci.yml
gitleaks:
  image:
    name: zricethezav/gitleaks:v8.30.1
    entrypoint: [""]  # 이미지 ENTRYPOINT가 gitleaks라 script 실행을 위해 비움
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

## 8. 탐지 후 대응

탐지 결과가 실제 자격증명이면 예외로 등록하기 전에 다음 순서로 처리합니다. push 여부와 관계없이 노출된 것으로 봅니다.

1. 결과를 `--redact`로만 공유하고 시크릿 값을 채팅·이슈·로그에 붙여 넣지 않습니다.
2. 해당 키·토큰·패스워드를 발급처에서 폐기하거나 교체합니다. 이력 삭제보다 먼저 합니다.
3. 접근 기록에서 노출 기간의 사용 흔적을 확인합니다.
4. 코드에서는 값을 환경 변수나 시크릿 저장소로 옮깁니다([시크릿 관리](./secret_management.md)).
5. 필요하면 이력에서 제거합니다([Git 이력의 민감 파일 제거](../../02_infrastructure/cicd/git_history_sensitive_file_removal.md)). 이미 clone·fork된 사본에는 남을 수 있으므로 2번을 대신하지 못합니다.
6. 오탐이면 4절의 예외 처리 방법 중 가장 좁은 것을 골라 등록하고 사유를 남깁니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- gitleaks: [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★★☆☆
- Gitleaks 공식 README: [github.com/gitleaks/gitleaks#readme](https://github.com/gitleaks/gitleaks#readme) — ★★★☆☆
- Gitleaks 기본 규칙: [config/gitleaks.toml](https://github.com/gitleaks/gitleaks/blob/v8.30.1/config/gitleaks.toml) — ★★★☆☆
- Gitleaks GitHub Action: [github.com/gitleaks/gitleaks-action](https://github.com/gitleaks/gitleaks-action) — ★★★☆☆
- Gitleaks v8.30.0 릴리스(디코딩 기본 깊이 0→5): [releases/tag/v8.30.0](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.0) — ★★★☆☆
- GitLab CI 이미지 entrypoint 재정의: [docs.gitlab.com/ci/docker/using_docker_images](https://docs.gitlab.com/ci/docker/using_docker_images/) — ★★★☆☆
- Git pre-push 입력 형식: [git-scm.com/docs/githooks](https://git-scm.com/docs/githooks#_pre_push) — ★★★☆☆
- actions/checkout 릴리스(v7.0.1): [github.com/actions/checkout/releases](https://github.com/actions/checkout/releases) — ★★★☆☆
- 확인 기록: [Gitleaks 참조 노트](../../_reference/gitleaks_official_notes.md)

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

**마지막 업데이트**: 2026-11-09

© 2026 siasia86. Licensed under CC BY 4.0.
