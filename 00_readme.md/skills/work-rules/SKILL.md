---
name: work-rules
description: Defines operating rules for all agents. Use when executing any task — confirms before action, requires rollback plans for dangerous operations, enforces naming conventions and credential placeholders.
---

# Work Rules

## 1. Confirm before action
Print task summary before execution. format: "수행할 작업: - [item]"
This applies to **destructive or irreversible** operations only (§ 2, § 3).
For routine tasks (file edits, status checks, builds), proceed without confirmation.

## 1-1. Long-running command timeout handling

For commands that may block (vagrant up, packer build, apt install, docker pull, etc.):

1. **Never use polling loops inside a single tool call** (e.g., `for i in ...; do sleep 30; check; done`) — blocks the session and appears frozen.
2. **Always use `timeout N <command>`** with a short limit (e.g., `timeout 15` for SSH checks).
3. **For background tasks** (Task Scheduler, nohup, etc.):
   - Launch with a single non-blocking command, then immediately move on to the next independent task.
   - Check status in subsequent separate tool calls — never in a polling loop within one call.
4. **If a command times out or hangs**: kill it, diagnose from logs, fix and retry autonomously.
5. **Retry limit**: after 2 failed attempts with the same approach, switch to a fundamentally different method.
6. **Never pause mid-task** for confirmation. The user will Ctrl+C if something is wrong.


## 2. Dangerous operations
terraform apply, infra changes, service restart, deploy → ask "진행할까요?" before execution

For complex infra changes, use `skill://spec-driven-infra` → `skill://planning-and-breakdown` → `skill://incremental-change` workflow.

## 3. Delete operations
List targets → show impact → confirm before proceeding

## 4. Markdown rules
- tree: use `├──`, `└──`, `│` style
- table: align columns considering Korean character width (vi vertical alignment)
  - Korean char = 2 width, ASCII = 1 width
  - pad each cell so all rows have equal column display width
  - separator line `|---|` length = max column width + 2 (one space each side)
- Detailed rules: see `file://~/.kiro/markdown/STYLE.md`
- output language: Korean

## 5. Naming convention
format: `[env]-[category]-[service]-[detail]`
env: dev / qa / stg / prd
ex: prd-app-web-frontend, dev-db-rds-postgresql

## 6. Symbols
Allowed: ✅ ❌ 🟡 🟢 🔴 ★★☆☆☆
No other emojis allowed (no decorative emojis)

## 7. sudo
Use sudo for file operations under /root/

## 8. Code changes
- Minimal change principle (modify only requested scope)
- Write test code only when explicitly requested
- Never hardcode secret keys

## 9. Response style
- Concise and direct answers
- Skip unnecessary praise/agreement
- Politely correct wrong information

## 10. Example credentials (placeholder only)
Use the following standard placeholders for example passwords/keys in code and docs:
- username:  `Secureuser123`
- password:  `SecurePassword123`
- key/secret: `SecureKey123`
- token:     `SecureToken123`
- db name:   `SecureDbName123`
- domain:    `example.com` / `db.example.com`
- email:     `user@example.com`
- IP:        `192.0.2.1` (RFC 5737 documentation range)
- S3 bucket: `my-bucket`

Add the following to `.gitleaks.toml` to suppress false positives from placeholder values:

```toml
[allowlist]
description = "global allowlist"
regexes = [
    # placeholder values
    '''Secureuser123''',
    '''SecurePassword123''',
    '''SecureKey123''',
    '''SecureToken123''',
    '''SecureDbName123''',
    # RFC 5737 documentation IP ranges
    '''192\.0\.2\.\d+''',
    '''198\.51\.100\.\d+''',
    '''203\.0\.113\.\d+''',
]
```

## 11. Markdown style check (after writing/editing .md)
After creating or modifying any .md file under /root/32_system-engineering-resources or /opt/00_chobo_ansible, run:

```bash
sudo python3 /root/32_system-engineering-resources/md-style-check.py <path>
```

- Run on the specific file or directory modified (not the entire repo unless requested)
- Fix all reported issues before presenting the result
- Use `--strict` / `-s` flag to check without whitelist (for full review)

## 12. Post-change verification
After any infrastructure or code change, verify in order:
1. Syntax/lint pass (terraform validate, shellcheck, ansible --syntax-check)
2. Dry-run clean (terraform plan, ansible --check)
3. Service health (curl health endpoint, aws describe-*)
4. Monitoring normal (no new alarms)

Skip verification only if explicitly told by user.

## 13. Multi-step task plan format
For tasks with 3+ steps, state the plan before starting:
```
1. [step] → verify: [check]
2. [step] → verify: [check]
3. [step] → verify: [check]
```

## 14. Code cleanup scope
When editing code:
- Remove only imports/variables/functions that YOUR changes made unused
- Do not remove pre-existing dead code — mention it instead
- Do not refactor adjacent code that isn't broken

## 15. _reference 디렉토리 규칙

`/root/32_system-engineering-resources/_reference/` 는 **공식 홈페이지 기반 참조 노트 전용** 디렉토리입니다.

### 저장 대상
- 공식 문서에서 수집한 권장 설정, deprecated/removed 항목, breaking changes, 버전 현황
- 반드시 공식 홈페이지(docs.*, official blog, GitHub release notes)를 직접 확인한 내용만 저장
- 개인 의견, 추정, 블로그 내용 혼입 금지

### 파일명 규칙
`{기술명}_official_notes.md` (예: `docker_official_notes.md`, `ansible_official_notes.md`)

### .md 작성 전 필수 절차

기술 관련 `.md` 파일을 **새로 작성**하거나 **기존 파일을 대폭 수정**할 때:

1. `_reference/INDEX.md` 확인 — 해당 기술 참조 파일 존재 여부 확인
2. 있으면 → 해당 파일 직접 읽기 (`last_checked` 날짜 확인, 6개월 이상 경과 시 재확인)
3. 없으면 → 공식 홈페이지를 아래 방법으로 스캔 후 **먼저 생성** (`.md` 작성 전에)
   - 일반 페이지: `lynx -dump <URL>`
   - JS 렌더링 페이지: `curl` + GitHub API / PyPI API / raw.githubusercontent.com 직접 호출
   - 최신 버전 확인: `curl -s "https://api.github.com/repos/<owner>/<repo>/releases/latest"`
4. 생성 후 → `_reference/INDEX.md` 테이블에 아래 형식으로 항목 추가:
   ```
   | {기술명} | `_reference/{기술명}_official_notes.md` | {최신버전} | {오늘날짜} |
   ```
5. `_reference` 파일을 참조하여 `.md` 작성

🟡 **순서 엄수**: `_reference` 생성 → INDEX 업데이트 → `.md` 작성. 역순 금지.

### _reference 파일 구조

```markdown
---
name: {기술명}-official-notes
last_checked: YYYY-MM-DD
sources:
  - https://공식URL
---

## 1. 버전 현황
## 2. 권장 설정
## 3. deprecated / removed
## 4. breaking changes
## 5. 보안 권장사항
```

🟡 agent resources에는 `INDEX.md`만 등록. 개별 파일은 필요 시 직접 읽기 (context window 절약)

## 16. _reference 작성 후 교차 검증 의무

`_reference/` 파일을 **신규 생성하거나 내용을 추가**한 경우, 반드시 아래 절차를 수행합니다.

### 검증 절차

1. **버전 정보**: GitHub API 또는 PyPI API로 실제 최신 버전 재확인
   ```bash
   curl -s "https://api.github.com/repos/<owner>/<repo>/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])"
   curl -s "https://pypi.org/pypi/<package>/json" | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   ```
2. **기능/개념 설명**: 공식 문서 URL을 직접 열어 해당 내용이 실제로 존재하는지 확인
3. **의심 항목 표시**: 공식 문서에서 확인하지 못한 내용은 작성하지 않거나, 주석으로 `# 미확인 — 검증 필요` 표시

### 금지 사항

- 기억이나 추론으로 작성한 내용을 공식 문서 기반인 것처럼 저장 ❌
- 블로그, Stack Overflow, 비공식 튜토리얼 내용 혼입 ❌
- 공식 문서에 없는 기능명·파라미터명 사용 ❌

### 오류 발견 시

`_reference` 파일에서 오류를 발견하면:
1. 즉시 공식 문서에서 정확한 내용 확인
2. 해당 파일 수정
3. `last_checked` 날짜 업데이트
4. INDEX.md 버전 정보 업데이트
5. 해당 `_reference`를 참조해 작성된 다른 `.md` 파일에도 오류가 전파됐는지 확인

## 17. Python 스크립트 작성 규칙

`/root/sj_del/ip_mask.py`, `json_mask.py` 스타일 기준.

### 파일 구조 (순서 엄수)

```
shebang
SAFETY 주석
모듈 docstring (사용법 포함)
VERSION 상수
import (stdlib 한 줄씩, 알파벳 순)
상수/패턴 (# ── 섹션명 ──... 구분)
함수 정의
if __name__ == '__main__': try/except
```

### 필수 항목

- **shebang**: `#!/usr/bin/env python3`
- **SAFETY 주석**: `#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script`
- **VERSION**: `VERSION = "YY.MM.DD"` (날짜 기반)
- **import**: 한 줄씩, stdlib 먼저, 알파벳 순 — `import re, sys` 한 줄 금지
- **모듈 상단 패턴 컴파일**: 함수 내 `re.compile()` 반복 금지 — 모듈 레벨 상수로 선언
- **함수 내 중복 import 금지**: `import re as _re` 함수 내 반복 금지
- **argparse 필수**: `sys.argv` 직접 파싱 금지
  - `-h/--help`: argparse 자동 제공
  - `-V/--version`: `action='version'`, `version=f'%(prog)s {VERSION}'`
  - `-s/--strict` 등 플래그: 단축키 + 풀네임 모두 제공
  - `epilog`: Examples + 주요 옵션 설명 포함
- **`parse_args()` 분리**: `main()` 내 인라인 금지, 별도 함수로 분리
- **`if __name__` try/except**:
  ```python
  if __name__ == '__main__':
      try:
          main()
      except KeyboardInterrupt:
          sys.exit(130)
  ```

### 섹션 구분 주석

```python
# ── 컬러 ──────────────────────────────────────────────────────────────────────
# ── 상수 ──────────────────────────────────────────────────────────────────────
# ── 유틸 ──────────────────────────────────────────────────────────────────────
# ── 검사 함수 ─────────────────────────────────────────────────────────────────
# ── 진입점 ────────────────────────────────────────────────────────────────────
```

### 함수 docstring

한 줄 요약 필수. 긴 설명은 두 번째 줄부터.

```python
def process_file(filepath, dry_run=False):
    """파일 내 IP 치환 (해당 패턴 없으면 스킵)."""
```

## 18. Windows PowerShell via SSH

SSH로 Windows PowerShell 명령 실행 시 한글 출력이 깨지는 것을 방지하려면 반드시 아래 패턴을 사용합니다.

```bash
# 올바른 패턴 — cmd로 chcp 65001 설정 후 powershell 실행
ssh user@host "cmd /c \"chcp 65001 > nul && powershell -Command \"\"<명령어>\"\"\""

# 잘못된 패턴 — PowerShell 내에서 chcp는 동작하지 않음
ssh user@host "powershell -Command \"chcp 65001 >nul; <명령어>\""
```

- `chcp 65001`: Windows 코드 페이지를 UTF-8로 변경
- `cmd /c` 래핑 필수: PowerShell 단독 실행 시 `>nul` 리다이렉션이 파일로 처리됨
