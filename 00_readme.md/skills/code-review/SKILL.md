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

## Output Format

```
## 코드 리뷰 결과

| # | 심각도 | 위치 | 문제 | 제안 |
|---|--------|------|------|------|
| 1 | 🔴    | L42  | ...  | ...  |
| 2 | ⚠️    | L78  | ...  | ...  |

심각도: 🔴 bug/security | ⚠️ improvement | 💡 suggestion

총평: (1~2문장 요약)
```

## Priority
- 🔴 items: must fix before merge
- ⚠️ items: should fix (technical debt if skipped)
- 💡 items: optional improvement
