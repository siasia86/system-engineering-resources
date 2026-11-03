---
name: gitleaks-official-notes
description: Gitleaks 공식 릴리스, CLI, 설정, Hook 및 GitHub Action 검증 노트.
tags:
  - gitleaks
  - secret-scanning
  - security
last_checked: 2026-11-03
sources:
  - https://api.github.com/repos/gitleaks/gitleaks/releases/latest
  - https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md
  - https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml
  - https://github.com/gitleaks/gitleaks-action/blob/master/README.md
  - https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_checksums.txt
---

# Gitleaks Official Notes

## 1. Version status

- 최신 릴리스: `v8.30.1`.
- 공식 GitHub API의 릴리스 게시일: `2026-03-21`.
- v8.30.1 Linux x64 자산명: `gitleaks_8.30.1_linux_x64.tar.gz`.
- 2026-11-03 재확인: GitHub API 최신 릴리스는 여전히 `v8.30.1`입니다(이전 `v8.30.0` 2025-11-26). 저장소는 MIT이며 archive 상태가 아닙니다.
- 체크섬 파일 `gitleaks_8.30.1_checksums.txt`의 linux_x64 SHA-256은 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`이며 내려받은 자산과 `sha256sum -c`로 일치했습니다.
- Docker 이미지 `ghcr.io/gitleaks/gitleaks:v8.30.1`과 `zricethezav/gitleaks:v8.30.1` 태그가 존재합니다(레지스트리 조회 HTTP 200).

## 2. Recommended settings

- 기본 스캔 모드는 `git`, `dir`, `stdin`입니다.
- `detect`와 `protect`는 v8.19.0부터 deprecated 처리되었지만 호환성을 위해 계속 사용할 수 있으며 도움말 목록에서는 숨겨져 있습니다.
- 사용자 설정 파일은 대상 경로의 `.gitleaks.toml`에서 자동 탐색됩니다.
- 사용자 설정은 기본 규칙을 자동 상속하지 않습니다. 기본 규칙을 유지하려면 다음을 명시해야 합니다.

```toml
[extend]
useDefault = true
```

- baseline은 기존 report에 포함된 기존 탐지 결과를 무시하는 용도로 사용합니다.
- CLI 전역 옵션에는 `--baseline-path`, `--config`, `--redact`, `--report-format`, `--report-path`, `--log-level` 등이 있습니다.

### 설정 형식 (v8.30.1 README)

- `[extend]`의 `useDefault`와 `path`는 함께 쓸 수 없습니다. `path`는 기준 설정이 아니라 실행 위치 기준 상대 경로입니다. 상속은 2단계까지이며 같은 ID 규칙은 상속하는 쪽이 우선하고 허용 목록 배열은 합쳐집니다. `disabledRules`로 상속 규칙을 끕니다.
- `[[rules]]` 항목: `id`, `description`, `regex`(Go 정규식, lookahead 미지원), `secretGroup`, `entropy`, `path`, `keywords`(v8.6.0), `tags`, `[[rules.allowlists]]`, `[[rules.required]]`(v8.28.0 composite rule, 실험 기능).
- 허용 목록 항목: `description`, `commits`, `paths`, `regexes`, `regexTarget`(`secret` 기본·`match`·`line`), `stopwords`(v8.8.0), `condition`(`OR` 기본·`AND`), `targetRules`(전역 `[[allowlists]]`, v8.25.0).
- 형식 변경: v8.21.0 `[rules.allowlist]` → `[[rules.allowlists]]`(이전 형식도 동작), v8.25.0 `[allowlist]` → `[[allowlists]]`. 전역 허용 목록이 규칙별 허용 목록보다 우선합니다.
- 추가 예외: 줄 끝 `gitleaks:allow` 주석(`--ignore-gitleaks-allow`로 무시), 저장소 루트 `.gitleaksignore`의 Fingerprint(실험 기능, `-i`로 경로 지정).
- 추가 스캔: `--max-decode-depth`(percent·hex 32자 이상·base64 16자 이상, 기본 0), `--max-archive-depth`(기본 0, 내부 경로는 `!`로 구분).
- 종료 코드: 0 탐지 없음, 1 탐지 또는 오류, 126 알 수 없는 옵션. `--exit-code`로 탐지 시 코드를 바꿉니다.

### 로컬 동작 확인 (2026-11-03, v8.30.1)

- `--exit-code 2`일 때 탐지는 2, 설정 파일 없음 오류는 1, 알 수 없는 옵션은 126을 반환했습니다.
- 전역 `[[allowlists]]`의 `targetRules`에 같은 설정에 없는 규칙 ID를 넣으면 `target rule ID ... does not exist`로 설정 로드에 실패했습니다.
- `gitleaks:allow` 주석 줄은 탐지에서 제외되었고, `dir` 모드 Fingerprint는 `<파일>:<규칙 ID>:<줄>` 형식이며 `.gitleaksignore`에 넣으면 제외되었습니다.
- `stdin` 모드는 표준 입력 내용에서 사용자 정의 규칙을 탐지했습니다.

## 3. Deprecated / removed

- `gitleaks rules`는 v8.30.1의 CLI 명령으로 제공되지 않습니다.
- `gitleaks protect --install-hook`의 `--install-hook` 옵션은 v8.30.1 CLI에 없습니다.
- 공식 README는 pre-commit 연동 방법으로 예제 `pre-commit.py`를 `.git/hooks/`에 복사하는 방법을 안내합니다.

## 4. Breaking changes

- v8.19.0부터 `detect`와 `protect`가 deprecated 명령으로 변경되었습니다. 신규 문서와 스크립트에서는 `git` 및 `dir` 모드를 우선 검토해야 합니다.
- Gitleaks GitHub Action은 v3 예시와 `actions/checkout@v6` 조합을 공식 README에서 안내합니다. Action v3는 Node 24 런타임을 사용합니다.
- Action README 기준: GitHub는 2026-06-02 runner 기본을 Node 24로 바꾸고 2026-09-16 호스트 runner에서 Node 20을 제거하므로 `gitleaks-action@v2`는 동작하지 않습니다. v3는 runner v2.327.1 이상이 필요합니다. 환경 변수는 `GITLEAKS_LICENSE`·`GITLEAKS_CONFIG`·`GITLEAKS_ENABLE_COMMENTS`·`GITLEAKS_ENABLE_UPLOAD_ARTIFACT`·`GITLEAKS_ENABLE_SUMMARY`·`GITLEAKS_NOTIFY_USER_LIST`입니다.

## 5. Security recommendations

- 탐지 결과 출력에는 `--redact`를 사용하여 시크릿 노출을 줄입니다.
- baseline은 기존 finding을 숨기는 기능이므로, 실제 시크릿을 해결한 것으로 간주하지 않습니다. 노출된 자격 증명은 별도로 폐기·교체해야 합니다.
- GitHub Action 조직 계정 사용 시 `GITLEAKS_LICENSE`가 필요할 수 있으므로 공식 Action 문서를 확인합니다.
