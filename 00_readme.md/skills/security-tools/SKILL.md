---
name: security-tools
description: Documents security masking tools (ip_mask.py, json_mask.py, aws-security-check.sh, git-security-check.sh). Use when masking sensitive data, running security checks, or modifying masking scripts.
---

# Security Masking Tools

## 1. Script list

| File                                 | Purpose                                | Target           |
|--------------------------------------|----------------------------------------|------------------|
| `/root/sj_del/ip_mask.py`            | Public IP → RFC 5737                   | All text files   |
| `/root/sj_del/json_mask.py`          | AWS resource masking (18 types)        | `.json` files    |
| `/root/sj_del/aws-security-check.sh` | AWS sensitive data detection (9 types) | Directory scan   |
| `/root/sj_del/git-security-check.sh` | Pre-commit security check (5 types)    | Git staged files |
| `/root/sj_del/md-style-check.sh`     | Markdown style check                   | `.md` files      |
| `/root/sj_del/security-check.conf`   | Shared config for bash scripts         | conf             |

## 2. Common option scheme (ip_mask.py / json_mask.py)

| Option             | Description                                  |
|--------------------|----------------------------------------------|
| `-f` / `--file`    | Single file target                           |
| `-D` / `--dir`     | Recursive directory processing               |
| `-r` / `--restore` | Restore original                             |
| `-d` / `--dry-run` | No file modification, preview only           |
| `-v` / `--verbose` | Show changed lines in detail                 |
| `--all`            | Include skipped files in output (ip_mask.py) |
| `--force`          | Ignore serial mismatch                       |
| `-V` / `--version` | Print version                                |
| `-i` / `--include` | Include extension filter                     |
| `-e` / `--exclude` | Exclude extension filter                     |
| `-q` / `--quiet`   | Minimize log output                          |
| `-m` / `--map`     | Specify map file path directly               |
| `--debug`          | Pattern debugging (json_mask.py only)        |

## 3. Design principles

- Map file deletion prohibited (retain even after restore)
- Serial verification: file hash ↔ map `_meta.serial` match check
- Atomic write: temp file → rename (original preserved on mid-failure)
- Permission preservation: maintain original file permissions
- Idempotency: re-running on already-masked file produces no changes
- `.bak.N` backup: auto-backup before map overwrite
- SAFETY line: `ip_mask.py` top `import sys; sys.exit(0)` retained (intentionally disabled)

## 4. Color rules

| Color  | Usage                          |
|--------|--------------------------------|
| Red    | mask filename, masked count    |
| Purple | restore filename, backup path  |
| Yellow | skip/warning, pre-change IP    |
| Green  | post-change IP, restored count |
| Gray   | line numbers (`L1`, `L2`)      |

## 5. ip_mask.py details

- Auto-detect public IPs (excludes private/example/special IPs)
- RFC 5737 sequential allocation: `192.0.2.0/24` → `198.51.100.0/24` → `203.0.113.0/24` (max 762)
- Version number exclusion: skip if IP has `-` or `_` adjacent
- Map file: `<source_file>.map.ip.json`
- Exclusions: `SKIP_EXTS` (binary), `SKIP_FILES` (self, etc.), `SKIP_TARGETS` (specific filenames)
- Excluded directories: `.git`, `.ssh`, `.kiro`
- Files containing `.map.ip.json` in name unconditionally excluded

## 6. json_mask.py details

- 18 pattern types: ACCOUNT-ID, BUCKET, VPCE-ID, VPC-ID, SUBNET-ID, SG-ID, ENI-ID, INSTANCE-ID, ELB-NAME, RDS-EP, CF-DIST-ID, NAT-GW-ID, RTB-ID, IGW-ID, IP, DOMAIN
- Placeholder format: `<TYPE-N>` (e.g., `<IP-1>`, `<ACCOUNT-ID-1>`)
- Map file: `<source_file>.map.json`
- `_meta` block: serial, source, version

## 7. Verification procedure

After code changes, always:
1. `py_compile` syntax verification
2. Temporarily disable SAFETY line, run execution test
3. mask → restore round-trip confirmation
4. Compatibility check with existing map files

```bash
sudo python3 -c "import py_compile; py_compile.compile('/root/sj_del/ip_mask.py', doraise=True); print('OK')"
sudo python3 -c "import py_compile; py_compile.compile('/root/sj_del/json_mask.py', doraise=True); print('OK')"
```

## 8. aws-security-check.sh details

- 9 check types: Access Keys, Secret Keys, Account IDs, ARNs, VPCE, Public IPs, Resource IDs, S3 Buckets, .map.json tracking
- Dynamic load EXCLUDE_IPS, EXCLUDE_BUCKETS from `security-check.conf`
- Version number pattern exclusion (skip if IP followed by `-`)
- `0x` hex address exclusion
- `ami-` prefix exclusion (Resource IDs)
- Fallback defaults if conf missing

## 9. git-security-check.sh details

- 5 check types: Sensitive IPs, Passwords/Keys, AWS Account IDs, Large Files, Sensitive Filenames
- All checks pass → `✓` output
- Dynamic filtering via `security-check.conf` EXCLUDE_PASSWORDS, EXCLUDE_KEYWORDS
- `0x` hex, `ULL` C literal, date pattern exclusion (Account ID false positive prevention)
- EXCLUDE_DIRS/EXCLUDE_FILES based find exclusion
- printf-style ANSI color (avoids echo -e compatibility issues)

## 10. Bash script common rules

- Output format: `[N/M] check_name` + result (`✓` / `✗` / `⚠`)
- `bash -n` syntax verification mandatory
- `security-check.conf` shared (source-loaded)
- `.kiro` directory excluded

## 11. Related config files

- `/root/sj_del/security-check.conf` — EXCLUDE_IPS, EXCLUDE_PASSWORDS, EXCLUDE_KEYWORDS, EXCLUDE_BUCKETS, EXCLUDE_DIRS, EXCLUDE_FILES
- `/root/sj_del/ip_mask.toml` — Legacy config (unused, can be deleted)

## 12. Dockerfile / Container security check

Manual inspection items (no script coverage):

- Pin image tags in `FROM` (`:latest` prohibited)
- Do not run as `USER root` (specify non-root user)
- No unnecessary packages (`--no-install-recommends`)
- Secrets not baked into layers (multi-stage build or `--secret`)
- Minimize `COPY` scope (use `.dockerignore`)
- Define health check (`HEALTHCHECK` instruction)
