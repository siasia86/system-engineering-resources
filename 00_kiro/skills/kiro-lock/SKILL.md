---
name: kiro-lock
description: Prevents concurrent work in shared directories. Checks/acquires lock before file modifications, releases after completion.
---

# Kiro Lock

## 1. Before starting work (mandatory)

Execute before any file modification task.

```bash
if [ -f .kiro-lock ]; then
    cat .kiro-lock 2>/dev/null || echo "⚠️ lock file unreadable — abort"
fi
```

- File exists + readable → show content + "Another task is in progress." + **abort immediately**
- File exists + unreadable → permission issue notice + **abort immediately**
- File absent → proceed to Lock acquisition

## 2. Lock acquisition

```bash
printf "user: $(whoami)\nhost: $(hostname)\nstarted: $(date -Iseconds)\nsession: $(date +%s)\ntask: <task summary>\n" > .kiro-lock
```

## 3. After work completion (mandatory)

Delete on both normal completion and error.

```bash
rm -f .kiro-lock
```

## 4. Rules

- Lock file path: `.kiro-lock` in **project root** (directory containing `.git`)
- No files shall be modified without acquiring lock
- Lock must be deleted even when errors occur during work
- Re-verify `.kiro-lock` ownership before each `fs_write`/write command (when 10+ minutes elapsed or after context compaction)
- Adding `.kiro-lock` to `.gitignore` is recommended

## 5. Stale lock handling

When `started` timestamp is 30+ minutes old:
1. Display confirmation request to the user
2. If user explicitly requests "release the lock", delete and proceed

## 6. Edge cases

### Own lock detection

When lock file `user` and `host` match current `$(whoami)`/`$(hostname)`:
- If `session` value matches current session → own lock (proceed normally)
- If `session` value differs → stale lock from previous session, ask "Previous session lock remains. Delete?" then proceed

### Corrupted lock file

When lock file exists but `user`/`started` fields cannot be parsed:
- Treat as stale lock
- Ask user "Lock file is corrupted. Delete?" then proceed

### Read-only operations

The following require no lock check/acquisition:
- `fs_read`, `grep`, `glob` and other read-only tools
- `git status`, `git log`, `git diff` and other query commands
- Status checks (`cat`, `ls`, `find`)

### Lock creation failure

When permission error occurs creating `.kiro-lock`:
1. Display error message
2. Do not proceed with work
3. Advise "Check project directory write permissions"

### Delegate invocations

When orchestrator (system-engineer) holds the lock and invokes sub-agents via delegate:
- Sub-agents do not re-check the lock (already acquired)
- Lock release is performed by orchestrator upon final work completion

## 7. Hook on/off

The preToolUse hook (`~/.kiro/hooks/kiro-lock.sh`) can be toggled without editing agent JSON.

```bash
# off
touch ~/.kiro/hooks/kiro-lock.disabled

# on
rm ~/.kiro/hooks/kiro-lock.disabled

# status
ls ~/.kiro/hooks/kiro-lock.disabled 2>/dev/null && echo "OFF" || echo "ON"
```

When disabled, the hook exits immediately (exit 0) — manual lock checks in SKILL.md §1–3 still apply.
