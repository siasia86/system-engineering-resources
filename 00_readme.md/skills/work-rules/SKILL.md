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
Use sudo when file operations require elevated permissions (e.g., files under /root/, /opt/, /etc/, or any path owned by root).

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

## 15. _reference directory rules

`/root/32_system-engineering-resources/_reference/` is **official-homepage-based reference notes only** directory.

### Storage targets
- Recommended settings, deprecated/removed items, breaking changes, version status collected from official docs
- Only store content directly verified from official homepage (docs.*, official blog, GitHub release notes)
- No personal opinions, guesses, or blog content allowed

### Filename convention
`{tech}_official_notes.md` (e.g., `docker_official_notes.md`, `ansible_official_notes.md`)

### Mandatory procedure before writing .md

When **creating new** or **significantly modifying** a tech-related `.md` file:

1. Check `_reference/INDEX.md` — verify if reference file exists for that technology
2. If exists → read the file directly (check `last_checked` date, re-verify if older than 6 months)
3. If not exists → scan official homepage using methods below, then **create reference first** (before writing `.md`)
   - Regular pages: `lynx -dump <URL>`
   - JS-rendered pages: `curl` + GitHub API / PyPI API / raw.githubusercontent.com direct call
   - Latest version check: `curl -s "https://api.github.com/repos/<owner>/<repo>/releases/latest"`
4. After creation → add entry to `_reference/INDEX.md` table in this format:
   ```
|  | {tech} | `_reference/{tech}_official_notes.md` | {latest_version} | {today_date} |
   ```
5. Write `.md` referencing the `_reference` file

🟡 **Strict order**: create `_reference` → update INDEX → write `.md`. Reverse order prohibited.

### _reference file structure

```markdown
---
name: {tech}-official-notes
last_checked: YYYY-MM-DD
sources:
  - https://official-URL
---

## 1. Version status
## 2. Recommended settings
## 3. deprecated / removed
## 4. breaking changes
## 5. Security recommendations
```

🟡 Register only `INDEX.md` in agent resources. Read individual files on demand (context window savings)

## 16. _reference post-write cross-verification obligation

When **creating new or adding content** to `_reference/` files, the following procedure is mandatory.

### Verification procedure

1. **Version info**: Re-verify actual latest version via GitHub API or PyPI API
   ```bash
   curl -s "https://api.github.com/repos/<owner>/<repo>/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])"
   curl -s "https://pypi.org/pypi/<package>/json" | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   ```
2. **Feature/concept descriptions**: Open official doc URL directly to confirm content actually exists
3. **Suspicious items**: Do not write content unverifiable from official docs, or mark with comment `# unverified — needs verification`

### Prohibited

- Writing content from memory/inference and presenting it as official-doc-based ❌
- Mixing in blog, Stack Overflow, unofficial tutorial content ❌
- Using feature names/parameter names not found in official docs ❌

### When errors are found

When discovering errors in `_reference` files:
1. Immediately verify correct content from official docs
2. Fix the file
3. Update `last_checked` date
4. Update INDEX.md version info
5. Check if the error propagated to other `.md` files referencing that `_reference`

## 17. Python script writing rules

Style reference: `/root/sj_del/ip_mask.py`, `json_mask.py`.

### File structure (strict order)

```
shebang
SAFETY comment
module docstring (including usage)
VERSION constant
import (stdlib one per line, alphabetical)
constants/patterns (# ── section ──... separator)
function definitions
if __name__ == '__main__': try/except
```

### Mandatory items

- **shebang**: `#!/usr/bin/env python3`
- **SAFETY comment**: `#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script`
- **VERSION**: `VERSION = "YY.MM.DD"` (date-based)
- **import**: one per line, stdlib first, alphabetical — `import re, sys` on one line prohibited
- **Module-level pattern compile**: `re.compile()` inside functions prohibited — declare as module-level constants
- **No duplicate imports in functions**: `import re as _re` repeated in functions prohibited
- **argparse mandatory**: direct `sys.argv` parsing prohibited
  - `-h/--help`: argparse auto-provides
  - `-V/--version`: `action='version'`, `version=f'%(prog)s {VERSION}'`
  - `-s/--strict` etc. flags: provide both shorthand + full name
  - `epilog`: include Examples + key option descriptions
- **Separate `parse_args()`**: no inline in `main()`, extract to separate function
- **`if __name__` try/except**:
  ```python
  if __name__ == '__main__':
      try:
          main()
      except KeyboardInterrupt:
          sys.exit(130)
  ```

### Section separator comments

```python
# ── colors ────────────────────────────────────────────────────────────────────
# ── constants ─────────────────────────────────────────────────────────────────
# ── utilities ─────────────────────────────────────────────────────────────────
# ── check functions ───────────────────────────────────────────────────────────
# ── entry point ───────────────────────────────────────────────────────────────
```

### Function docstring

One-line summary mandatory. Longer description from second line onward.

```python
def process_file(filepath, dry_run=False):
    """Replace IPs in file (skip if no matching pattern)."""
```

## 18. Windows PowerShell via SSH

To prevent Korean/UTF-8 output corruption when executing Windows PowerShell commands via SSH, always use the following pattern.

```bash
# Correct pattern — set chcp 65001 via cmd then execute powershell
ssh user@host "cmd /c \"chcp 65001 > nul && powershell -Command \"\"<command>\"\"\""

# Wrong pattern — chcp does not work inside PowerShell
ssh user@host "powershell -Command \"chcp 65001 >nul; <command>\""
```

- `chcp 65001`: Changes Windows code page to UTF-8
- `cmd /c` wrapping mandatory: PowerShell standalone treats `>nul` redirection as file output

## 19. Post-replacement immediate verification

After modifying file content with `sed`, `python replace`, `str_replace`, etc., always perform the following.

### Mandatory procedure

1. **Confirm replacement applied**: Print target lines with `grep` or `sed -n` to verify intended changes
2. **Check for remnants**: Run `grep -rn "old_value"` to ensure previous value doesn't remain in same file or project-wide
3. **Check impact scope**: If changed value (IP, path, hostname, etc.) exists in other files, scan project-wide (`grep -rn`)

### Additional rules for global value changes

When changing values used across **multiple files** (IP addresses, file paths, hostnames, etc.):

```bash
# Before change: identify all affected files
grep -rn "old_value" /project_root/ | grep -v ".log|.git"

# After change: confirm 0 remnants
grep -rn "old_value" /project_root/ | grep -v ".log|.git"
```

- **Identify all target files first**, then batch-change
- Partial change with "rest later" pattern prohibited — complete all at once or mark TODO

### Prohibited

- Proceeding to next task without verifying replacement result ❌
- Ignoring `replace()` matching failure (0 replacements) silently ❌
- Changing only some files when same value exists in multiple files, missing the rest ❌

### Python replace safe pattern

```python
# ❌ Dangerous — proceeds silently on match failure
content = content.replace(old, new)

# ✅ Safe — detects match failure immediately
if old not in content:
    print(f"WARNING: '{old[:50]}...' not found in {path}")
else:
    content = content.replace(old, new)
    print(f"✓ replaced in {path}")
```

### sed safe pattern

```bash
# ❌ Dangerous — exit 0 even with 0 matches
sed -i 's/old/new/g' file.txt

# ✅ Safe — verify change applied
sed -i 's/old/new/g' file.txt
grep -q "new" file.txt && echo "✓ applied" || echo "⚠️ not found"
```

## 20. VM deletion confirmation mandatory

VM deletion (Remove-VM, vagrant destroy, Stop-VM -Force, etc.) must **always list targets first and get user confirmation before proceeding**.

```
1. Display current VM list
2. Ask "These VMs will be deleted. Proceed?"
3. Execute deletion only after user approval
```

- Same rule applies to single VM deletion
- Recreation (delete → recreate) also requires confirmation before deletion

## 21. Zombie SSH process cleanup at session start

SSH/scp processes left over from previous sessions interrupted with Ctrl+C can exhaust the remote host's SSH MaxSessions, blocking new connections.

Run at session start or when SSH is unresponsive.

```bash
# Generic pattern — replace <target> with actual SSH target hostname or IP
ps -ef | grep -E "ssh.*<target>|timeout.*ssh" | grep -v grep

# Cleanup
sudo kill -9 $(ps -ef | grep -E "ssh.*<target>|timeout.*ssh" | grep -v grep | awk '{print $2}') 2>/dev/null
```

For the `ansibleuser@10.200.101.101` (Windows Hyper-V host) environment:

```bash
sudo kill -9 $(ps -ef | grep -E "ssh.*ansibleuser|timeout.*ssh" | grep -v grep | awk '{print $2}') 2>/dev/null
```

## 22. Kiro Lock (concurrent work prevention)

> 🟡 Currently **disabled** (`~/.kiro/hooks/kiro-lock.disabled` exists). Skip this rule until re-enabled.

When enabled: before any file modification, follow `skill://kiro-lock` §1–3:

1. Check `.kiro-lock` in the project root (`.git` directory parent)
2. If absent → create lock file
3. After work → `rm -f .kiro-lock`

```bash
# Enable
rm ~/.kiro/hooks/kiro-lock.disabled

# Disable
touch ~/.kiro/hooks/kiro-lock.disabled
```

## 23. Immediate PLAN.md issue logging

When working in a project that has a PLAN.md (e.g., `/opt/00_chobo_ansible/05_vagrant/PLAN.md`), log any unexpected errors, escape issues, script bugs, or significant fixes **immediately after resolving them** — before moving on to the next task.

### When to log

Log to PLAN.md when any of the following occur during non-PLAN.md work:

- Script execution fails (non-trivial error)
- Escape/quoting issue discovered (`$`, `\n`, `\\`, shell vs Python string)
- Code modification causes IndentationError or silent fail
- VM/infrastructure behavior differs from expectation **and root cause required >5 minutes to identify**
- Workaround applied **that is non-obvious or environment-specific**

🟡 **Exception**: Editing PLAN.md itself does not trigger this rule (no loop).
🟡 **Exception**: If no PLAN.md exists in the project, skip this rule — do not create one automatically.
🟡 **Dedup**: Before adding a new issue, check if the same symptom already exists in PLAN.md. If so, append to the existing entry rather than creating a duplicate.
🟡 **Scope**: Only log issues that required non-trivial investigation or had non-obvious root causes. Skip simple retries, typos, or one-liner fixes with no learning value.
🟡 **Collaboration**: When working collaboratively, re-enable kiro-lock (§ 22) before logging to PLAN.md to prevent concurrent modification conflicts.

### What to log

Use the issue template in PLAN.md `## 이슈 기록`. Use the next sequential number after the last existing issue (check existing `#### 이슈 N:` entries to determine N):

```markdown
#### 이슈 N: 제목

- 증상: (what happened)
- 원인: (why it happened)
- 해결:
  ```bash/python/powershell
  (fix code)
  ```
- 재현 방법: (optional — how to reproduce)
  ```bash
  (reproduction command)
  ```
```

### Timing rule

- ✅ Log **immediately after fix** — same tool call or the very next one
- ❌ "I'll log it later" → always forgotten

### How to find PLAN.md

Look for `PLAN.md` starting from the current working directory, searching up to 4 levels deep:

```bash
find "$(pwd)" -maxdepth 4 -name "PLAN.md" 2>/dev/null
# or from project root (git root)
git rev-parse --show-toplevel 2>/dev/null | xargs -I{} find {} -maxdepth 3 -name "PLAN.md"
```

## 24. GitHub reference auto-append

When referencing a GitHub repository during work, automatically append the URL to `_reference/github_references.md`.

### Conditions

- Verify repository existence via GitHub API before adding:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/<owner>/<repo>
  # 200 = exists, 404 = not found
  ```
- Do not add if the same URL already exists in the file:
  ```bash
  grep -q "github.com/<owner>/<repo>" /root/32_system-engineering-resources/_reference/github_references.md
  # exit 0 = duplicate, skip
  ```
- Do not add temporary references (example-only, comparison-purpose).

### Classification rules

- URL or description contains `agent`, `ai`, `llm`, `prompt` → `## 1. AI/Agent`
- URL or description contains `packer`, `terraform`, `ansible`, `vagrant` → `## 2. Packer/IaC`
- Otherwise → `## 3. 도구`

### Entry format

```markdown
- [repo-name]: [github.com/owner/repo](https://github.com/owner/repo) — ★★☆☆☆
```

### Target file

```
/root/32_system-engineering-resources/_reference/github_references.md
```
