---
name: gitleaks-official-notes
description: Gitleaks 공식 릴리스, CLI, 설정, Hook 및 GitHub Action 검증 노트.
tags:
  - gitleaks
  - secret-scanning
  - security
last_checked: 2026-08-19
sources:
  - https://api.github.com/repos/gitleaks/gitleaks/releases/latest
  - https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md
  - https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml
  - https://github.com/gitleaks/gitleaks-action/blob/master/README.md
---

# Gitleaks Official Notes

## 1. Version status

- 최신 릴리스: `v8.30.1`.
- 공식 GitHub API의 릴리스 게시일: `2026-03-21`.
- v8.30.1 Linux x64 자산명: `gitleaks_8.30.1_linux_x64.tar.gz`.

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

## 3. Deprecated / removed

- `gitleaks rules`는 v8.30.1의 CLI 명령으로 제공되지 않습니다.
- `gitleaks protect --install-hook`의 `--install-hook` 옵션은 v8.30.1 CLI에 없습니다.
- 공식 README는 pre-commit 연동 방법으로 예제 `pre-commit.py`를 `.git/hooks/`에 복사하는 방법을 안내합니다.

## 4. Breaking changes

- v8.19.0부터 `detect`와 `protect`가 deprecated 명령으로 변경되었습니다. 신규 문서와 스크립트에서는 `git` 및 `dir` 모드를 우선 검토해야 합니다.
- Gitleaks GitHub Action은 v3 예시와 `actions/checkout@v6` 조합을 공식 README에서 안내합니다. Action v3는 Node 24 런타임을 사용합니다.

## 5. Security recommendations

- 탐지 결과 출력에는 `--redact`를 사용하여 시크릿 노출을 줄입니다.
- baseline은 기존 finding을 숨기는 기능이므로, 실제 시크릿을 해결한 것으로 간주하지 않습니다. 노출된 자격 증명은 별도로 폐기·교체해야 합니다.
- GitHub Action 조직 계정 사용 시 `GITLEAKS_LICENSE`가 필요할 수 있으므로 공식 Action 문서를 확인합니다.
