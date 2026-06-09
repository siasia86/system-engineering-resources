---
name: code-review
description: Provides a structured code review checklist. Use when reviewing code, scripts, or IaC files. Covers correctness, security, error handling, performance, and infrastructure as code.
---

# Code Review

Apply when: "리뷰", "review", "검토", "코드 리뷰"

## Checklist

### 1. Correctness
- Logic matches requirements
- Boundary handling (off-by-one, min/max, empty input)
- Missing exception/error handling
- Type mismatch, None/null reference
- Return value correctness (all paths return expected type)

### 2. Security
- Hardcoded secrets/keys/passwords
- SQL/Command injection (use parameterized queries)
- Missing input validation (user input untrusted)
- Missing authorization/authentication check
- Sensitive data in logs or error messages
- Path traversal (user-controlled file paths)

### 3. Error Handling
- Bare except (`except:` → `except Exception:`)
- Silent error swallowing (pass in except)
- Useful error messages (include context for debugging)
- Resource cleanup (finally, context manager, try-with)
- Graceful degradation on external service failure

### 4. Performance
- Unnecessary loops (N+1 query, nested loops on large data)
- Memory: loading entire file/dataset into memory
- Unclosed connections/file handles/cursors
- Cacheable repeated computation
- Blocking I/O in async context

### 5. Concurrency (if applicable)
- Race condition (shared mutable state)
- Deadlock potential (lock ordering)
- Thread safety of shared resources
- Atomic operations where needed

### 6. Readability / Maintainability
- Clear naming (functions, variables, classes)
- Function length (>50 lines → consider splitting)
- DRY violation (duplicated code → extract)
- Magic numbers/strings → named constants
- Comments: missing where complex, unnecessary where obvious
- Consistent code style with project

### 7. Test Adequacy (if tests exist)
- Happy path covered
- Error/exception cases covered
- Boundary values (BVA): min-1, min, max, max+1
- Equivalence partitions: all groups represented
- Branch coverage: both if/else paths tested
- Mock usage appropriate (external deps only)

### 8. Compatibility
- Python version compatibility (f-string 3.6+, match 3.10+, etc.)
- OS-specific code (path separators, commands)
- Dependency version constraints

### 9. Infrastructure as Code (Terraform / Ansible)
- Hardcoded values → variables or locals
- Missing `description` on variables/outputs
- Resource naming convention (`[env]-[category]-[service]-[detail]`)
- Missing tags (Name, Environment, Owner, ManagedBy)
- Overly permissive IAM (`*` actions or resources)
- Security Group `0.0.0.0/0` inbound without justification
- Missing encryption (S3, EBS, RDS `storage_encrypted`)
- No lifecycle/prevent_destroy on stateful resources
- Ansible: missing `become`, handler not notified, no `changed_when`
- State drift risk: manual console changes not reflected in code

### 10. Shell / Bash Scripts
- Missing `set -euo pipefail` (fail-fast + undefined var detection)
- Unquoted variables (`$VAR` → `"$VAR"`, prevents word splitting)
- Missing input validation (argument count, file existence)
- Hardcoded paths → variables or config file
- No cleanup trap (`trap cleanup EXIT`)
- Using `echo` for errors → `>&2` (stderr)
- Parsing command output instead of using proper tools (awk/jq)
- Missing `shellcheck` compliance
- Race condition in temp file creation → `mktemp`
- Excessive use of `sudo` without justification

## Output Format

```
## 코드 리뷰 결과

| # | 심각도 | 위치 | 문제 | 제안 |
|---|--------|------|------|------|
| 1 | 🔴     | L42  | ...  | ...  |
| 2 | 🟡     | L78  | ...  | ...  |

심각도: 🔴 bug/security | 🟡 improvement | 💡 suggestion

총평: (1~2문장 요약)
```

## Priority
- 🔴 items: must fix before merge
- 🟡 items: should fix (technical debt if skipped)
- 💡 items: optional improvement

## Red Flags

- 리뷰 없이 merge/apply 진행
- 🔴 항목을 무시하고 진행
- "나중에 고치겠습니다"로 보안 이슈 보류
- 리뷰 범위를 임의로 축소 (요청된 파일 일부만 검토)
- 변경 의도를 이해하지 않고 형식만 검토
