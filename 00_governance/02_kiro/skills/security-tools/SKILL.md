---
name: security-tools
description: Documents security masking tools (ip_mask.py, json_mask.py, aws-security-check.sh, git-security-check.sh). Use when masking sensitive data, running security checks, or modifying masking scripts.
---

# Security Masking Tools

## 1. Script list

| File                                 | Purpose                                                 | Target                     |
|--------------------------------------|---------------------------------------------------------|----------------------------|
| `/root/sj_del/ip_mask.py`            | Public IP masking and restoration using RFC 5737 ranges | All text files             |
| `/root/sj_del/json_mask.py`          | AWS resource masking with 18 regex rules                | `.json` files              |
| `/root/sj_del/aws_security_check.sh` | AWS sensitive-data detection with 9 checks              | Directory scan             |
| `/root/sj_del/git_security_check.sh` | Pre-commit security check with 5 checks                 | Git working-tree directory |
| `/usr/local/bin/sia-md-style-check`  | Markdown style validation                               | `.md` files                |
| `/root/sj_del/security_check.conf`   | Shared configuration for Bash scripts                   | Configuration file         |

## 2. Common option scheme (`ip_mask.py` / `json_mask.py`)

| Option             | Description                                              |
|--------------------|----------------------------------------------------------|
| `-f` / `--file`    | Process a single file                                    |
| `-D` / `--dir`     | Process a directory recursively                          |
| `-r` / `--restore` | Restore the original content                             |
| `-d` / `--dry-run` | Preview changes without modifying files                  |
| `-v` / `--verbose` | Show changed lines in detail                             |
| `--all`            | Include unchanged files in output (`ip_mask.py`)         |
| `--force`          | Ignore serial mismatches                                 |
| `-V` / `--version` | Print the version                                        |
| `-i` / `--include` | Include only matching extensions                         |
| `-e` / `--exclude` | Exclude matching extensions                              |
| `-q` / `--quiet`   | Minimize log output                                      |
| `-m` / `--map`     | Specify a map file path directly                         |
| `--debug`          | Show pattern debugging information (`json_mask.py` only) |

## 3. Design principles

- Do not delete map files after restoration; they are required for reversibility.
- Verify the source file hash against the map `_meta.serial` value.
- Write atomically by using a temporary file followed by a rename.
- Preserve the original file permissions.
- Guarantee idempotency: re-running a mask operation produces no additional changes.
- Create a `.bak.N` backup before overwriting a map file.
- Keep the `SAFETY` line in `ip_mask.py` available for emergency execution blocking.

## 4. Color rules

| Color  | Usage                                   |
|--------|-----------------------------------------|
| Red    | Masked filename and masked count        |
| Purple | Restored filename and backup path       |
| Yellow | Skipped item, warning, or pre-change IP |
| Green  | Post-change IP or restored count        |
| Gray   | Line numbers such as `L1`               |

## 5. `ip_mask.py` details

- Automatically detects public IP addresses and excludes private, example, and special-purpose addresses.
- Allocates RFC 5737 ranges sequentially: `192.0.2.0/24` → `198.51.100.0/24` → `203.0.113.0/24` (maximum 762 addresses).
- Skips version-like values when an IP is adjacent to `-` or `_`.
- Stores the map at `<source_file>.map.ip.json`.
- Applies `SKIP_EXTS`, `SKIP_FILES`, and `SKIP_TARGETS` exclusions.
- Excludes `.git`, `.ssh`, and `.kiro` directories.
- Always excludes files whose names contain `.map.ip.json`.

## 6. `json_mask.py` details

- Provides 18 regex rules covering 17 resource types: `ACCOUNT-ID`, `BUCKET`, `VPCE-ID`, `VPC-ID`, `SUBNET-ID`, `SG-ID`, `ENI-ID`, `INSTANCE-ID`, `ELB-NAME`, `RDS-EP`, `CF-DIST-ID`, `NAT-GW-ID`, `RTB-ID`, `IGW-ID`, `IP`, and `DOMAIN`.
- Uses placeholders such as `<TYPE-N>`, for example `<IP-1>` and `<ACCOUNT-ID-1>`.
- Stores the map at `<source_file>.map.json`.
- Stores serial, source, and version metadata in the `_meta` block.

## 7. Verification procedure

After modifying masking scripts, run the following checks:

1. Verify Python syntax with `py_compile`.
2. Run the script against an isolated temporary directory.
3. Verify a mask → restore round trip.
4. Check compatibility with existing map files.
5. Restore the `SAFETY` line to its original state after testing.

The `SAFETY` line is normally commented and therefore allows execution. To block execution temporarily, uncomment the line below; restore the comment before normal use.

```python
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable the script
```

```bash
sudo python3 -c "import py_compile; py_compile.compile('/root/sj_del/ip_mask.py', doraise=True); print('OK')"
sudo python3 -c "import py_compile; py_compile.compile('/root/sj_del/json_mask.py', doraise=True); print('OK')"
```

## 8. `aws_security_check.sh` details

- Performs 9 checks: access keys, secret keys, account IDs, ARNs, VPCE IDs, public IPs, AWS resource IDs, S3 buckets, and tracked `.map.json` files.
- Dynamically loads `EXCLUDE_IPS` and `EXCLUDE_BUCKETS` from `/root/sj_del/security_check.conf`.
- Excludes version-like values when an IP is followed or preceded by `-`.
- Excludes `0x` hexadecimal addresses.
- Excludes `ami-` resource IDs from generic resource-ID detection.
- Uses fallback defaults when `/root/sj_del/security_check.conf` is unavailable.

## 9. `git_security_check.sh` details

- Performs 5 checks: sensitive IPs, passwords and keys, AWS account IDs, large files, and sensitive filenames.
- Scans files under `SCAN_DIR` (default: `.`); run it from the repository root when Git status output is required.
- Uses Git tracking information only for the tracked `.map.json` check.
- Dynamically loads `EXCLUDE_PASSWORDS`, `EXCLUDE_KEYWORDS`, and `EXCLUDE_ACCOUNTS` from `/root/sj_del/security_check.conf`.
- Excludes `0x` hexadecimal values, `ULL` C literals, and date-like values to reduce account-ID false positives.
- Applies `EXCLUDE_DIRS` and `EXCLUDE_FILES` while searching.
- Uses `printf`-style ANSI color output for portability.

## 10. Bash script common rules

- Use the output format `[N/M] check_name` followed by `✓`, `✗`, or `⚠`.
- Run `bash -n` after modifying either Bash script.
- Load shared settings from `/root/sj_del/security_check.conf`.
- Exclude the `.kiro` directory from scans.

## 11. Related configuration files

- `/root/sj_del/security_check.conf` — `EXCLUDE_IPS`, `EXCLUDE_PASSWORDS`, `EXCLUDE_KEYWORDS`, `EXCLUDE_ACCOUNTS`, `EXCLUDE_BUCKETS`, `EXCLUDE_DIRS`, and `EXCLUDE_FILES`.
- `/root/sj_del/ip_mask.toml` — Legacy configuration; currently unused.

## 12. AWS account ID and resource placeholders

Do not use real numeric AWS account IDs in documentation or examples. Security scanners treat 12-digit numbers as potential account IDs, so use the following placeholders:

- Account IDs: `<ACCOUNT-ID-1>`, `<ACCOUNT-ID-2>`
- IAM ARN: `arn:aws:iam::<ACCOUNT-ID-1>:root`, `arn:aws:iam::<ACCOUNT-ID-2>:role/backup-writer`
- KMS key ARN: `arn:aws:kms:ap-northeast-2:<ACCOUNT-ID-2>:key/<KEY-ID>`
- S3 bucket: `my-bucket`

Executable command examples must include the following replacement note:

```text
Replace <ACCOUNT-ID-1>, <ACCOUNT-ID-2>, <KEY-ID>, and my-bucket with actual values before execution.
```

- `123456789012` is retained only for compatibility with existing tests and `security_check.conf`; do not add it to new documentation or code.
- Do not add real account IDs to `EXCLUDE_ACCOUNTS` to hide scanner findings. Use that list only for reproducible test fixtures.
- Prefer the `<ACCOUNT-ID-N>` placeholders supported by `json_mask.py`; keep original account IDs separately with their map files.

## 13. Dockerfile / container security check

Manual inspection items not covered by the listed scripts:

- Pin image tags in `FROM`; do not use `:latest`.
- Do not run as `USER root`; specify a non-root user.
- Avoid unnecessary packages; use `--no-install-recommends` where applicable.
- Do not bake secrets into image layers; use a multi-stage build or `--secret`.
- Minimize the `COPY` scope and provide a `.dockerignore` file.
- Define a `HEALTHCHECK` instruction.
