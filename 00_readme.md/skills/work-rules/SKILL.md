---
name: work-rules
description: Defines operating rules for all agents. Use when executing any task — confirms before action, requires rollback plans for dangerous operations, enforces naming conventions and credential placeholders.
---

# Work Rules

## 1. Confirm before action
Print task summary before execution. format: "수행할 작업: - [item]"

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
Allowed: ✅ ❌ ⚠️ 🟢 🟡 🔴 ★★☆☆☆
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
After creating or modifying any .md file under /root/32_system-engineering-resources, run:

```bash
sudo bash /root/32_system-engineering-resources/md-style-check.sh <path>
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

## 13. _reference 디렉토리 규칙

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
3. 없으면 → 공식 홈페이지를 아래 방법으로 스캔 후 생성
   - 일반 페이지: `lynx -dump <URL>`
   - JS 렌더링 페이지: `curl` + GitHub API / PyPI API / raw.githubusercontent.com 직접 호출
   - 최신 버전 확인: `curl -s "https://api.github.com/repos/<owner>/<repo>/releases/latest"`
4. 생성 후 → `_reference/INDEX.md` 테이블에 아래 형식으로 항목 추가:
   ```
   | {기술명} | `_reference/{기술명}_official_notes.md` | {최신버전} | {오늘날짜} |
   ```
5. `_reference` 파일을 참조하여 `.md` 작성

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

⚠️ agent resources에는 `INDEX.md`만 등록. 개별 파일은 필요 시 직접 읽기 (context window 절약)
