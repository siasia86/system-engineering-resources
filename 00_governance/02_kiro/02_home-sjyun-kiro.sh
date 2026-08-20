#!/usr/bin/env bash
#### This script was created by sjyun on 2026-08-20. version 26.08.20.
#### Kiro public allowlist mirror synchronization.

set -euo pipefail

VERSION="26.08.20"
SCRIPT_NAME="$(basename "$0")"
SOURCE_ROOT="${KIRO_SOURCE_ROOT:-}"
MANIFEST_PATH=""
TARGET_NAME="central"
TARGET_PATH=""
APPLY=0
VERBOSE=0
CHECK_ONLY=0
CLEAN_MANIFEST=""

# ── logging ───────────────────────────────────────────────────────────────────
log_info() {
    printf '%s [info] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

log_error() {
    printf '%s [error] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

die() {
    log_error "$*"
    exit 1
}

# ── cleanup ───────────────────────────────────────────────────────────────────
cleanup() {
    if [ -n "${CLEAN_MANIFEST:-}" ] && [ -f "$CLEAN_MANIFEST" ]; then
        rm -f "$CLEAN_MANIFEST"
    fi
}

trap cleanup EXIT

# ── arguments ─────────────────────────────────────────────────────────────────
usage() {
    cat <<EOF
Usage:
  $SCRIPT_NAME [options]

Options:
  --target NAME       Target name: central or default (default: central)
  --target-path PATH  Explicit target directory
  --manifest FILE     Manifest override
  --dry-run           Preview changes only (default)
  --apply             Apply the allowlist mirror
  --check             Validate source and manifest only
  --verbose           Show verbose rsync output
  -V, --version       Show version
  -h, --help          Show this help

Examples:
  $SCRIPT_NAME --target central --dry-run
  $SCRIPT_NAME --target central --apply
  $SCRIPT_NAME --check --verbose
EOF
}

parse_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --target)
                [ "$#" -ge 2 ] || die "--target requires a value"
                TARGET_NAME=$2
                shift 2
                ;;
            --target-path)
                [ "$#" -ge 2 ] || die "--target-path requires a value"
                TARGET_PATH=$2
                shift 2
                ;;
            --manifest)
                [ "$#" -ge 2 ] || die "--manifest requires a value"
                MANIFEST_PATH=$2
                shift 2
                ;;
            --dry-run)
                APPLY=0
                shift
                ;;
            --apply)
                APPLY=1
                shift
                ;;
            --check)
                CHECK_ONLY=1
                shift
                ;;
            --verbose)
                VERBOSE=1
                shift
                ;;
            -V|--version)
                printf '%s %s\n' "$SCRIPT_NAME" "$VERSION"
                exit 0
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                die "unknown option: $1"
                ;;
        esac
    done
}

# ── path resolution ───────────────────────────────────────────────────────────
resolve_paths() {
    if [ -z "$SOURCE_ROOT" ]; then
        if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != root ]; then
            SOURCE_ROOT="/home/${SUDO_USER}/.kiro"
        else
            SOURCE_ROOT="${HOME}/.kiro"
        fi
    fi

    if [ -z "$MANIFEST_PATH" ]; then
        MANIFEST_PATH="${SOURCE_ROOT}/manifests/kiro_files.txt"
    fi

    if [ -n "$TARGET_PATH" ]; then
        return
    fi

    case "$TARGET_NAME" in
        central)
            TARGET_PATH="/root/32_system-engineering-resources/00_governance/02_kiro"
            ;;
        default)
            TARGET_PATH="/root/sj_del/00_default/.kiro"
            ;;
        *)
            die "unsupported target: $TARGET_NAME"
            ;;
    esac
}

# ── manifest validation ───────────────────────────────────────────────────────
prepare_manifest() {
    command -v rsync >/dev/null 2>&1 || die "rsync is required"
    [ -d "$SOURCE_ROOT" ] || die "source directory not found: $SOURCE_ROOT"
    [ -f "$MANIFEST_PATH" ] || die "manifest not found: $MANIFEST_PATH"

    CLEAN_MANIFEST=$(mktemp "${TMPDIR:-/tmp}/kiro-manifest.XXXXXX")
    awk '
        /^[[:space:]]*#/ { next }
        /^[[:space:]]*$/ { next }
        { print $1 }
    ' "$MANIFEST_PATH" > "$CLEAN_MANIFEST"

    [ -s "$CLEAN_MANIFEST" ] || die "manifest is empty: $MANIFEST_PATH"
    grep -qxF "manifests/kiro_files.txt" "$CLEAN_MANIFEST" \
        || die "manifest must include itself"

    while IFS= read -r path; do
        case "$path" in
            /*|../*|*/../*)
                die "invalid manifest path: $path"
                ;;
            .local|.local/*|memory.md|memory_private.md|sessions|sessions/*|settings|settings/*|.cli_bash_history)
                die "private path in manifest: $path"
                ;;
        esac

        [[ "$path" != *[[:space:]]* ]] \
            || die "whitespace is not allowed in manifest path: $path"
        [ -f "$SOURCE_ROOT/$path" ] \
            || die "manifest file not found under source: $path"
    done < "$CLEAN_MANIFEST"
}

# ── synchronization ───────────────────────────────────────────────────────────
sync_kiro() {
    [ -d "$TARGET_PATH" ] || die "target directory not found: $TARGET_PATH"

    local -a rsync_args
    rsync_args=(
        --recursive
        --links
        --times
        --perms
        --no-owner
        --no-group
        --human-readable
        --itemize-changes
        --files-from="$CLEAN_MANIFEST"
        --exclude=.local
        --exclude=memory.md
        --exclude=memory_private.md
        --exclude=sessions/
        --exclude=settings/
        --exclude=.cli_bash_history
        --exclude=.kiro-lock
    )

    if [ "$VERBOSE" -eq 1 ]; then
        rsync_args+=(--verbose)
    fi
    if [ "$APPLY" -eq 0 ]; then
        rsync_args+=(--dry-run)
        log_info "dry-run: $SOURCE_ROOT -> $TARGET_PATH"
    else
        log_info "apply: $SOURCE_ROOT -> $TARGET_PATH"
    fi

    rsync "${rsync_args[@]}" "$SOURCE_ROOT/" "$TARGET_PATH/"
}

# ── main ──────────────────────────────────────────────────────────────────────
main() {
    parse_args "$@"
    [ "$APPLY" -eq 0 ] || [ "$CHECK_ONLY" -eq 0 ] \
        || die "--check and --apply cannot be combined"
    resolve_paths
    prepare_manifest
    log_info "manifest validated: $MANIFEST_PATH"

    if [ "$CHECK_ONLY" -eq 1 ]; then
        log_info "check complete"
        return 0
    fi

    sync_kiro
}

main "$@"
