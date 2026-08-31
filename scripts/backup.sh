#!/usr/bin/env bash
# Hermes Daily Backup Script
# Captures the current session, commits repository changes, and pushes them.
set -euo pipefail

REPO="${HERMES_BACKUP_REPO:-$HOME/hermes-immortal}"
SESSION_SOURCE="${HERMES_SESSION_SOURCE:-$HOME/hermes-knowledge/logs/current-session.md}"
STATE_DIR="${HERMES_BACKUP_STATE_DIR:-$HOME/.local/state/hermes-immortal}"
RECEIPT="$STATE_DIR/backup.log"
DRY_RUN=false

usage() {
  printf 'Usage: %s [--dry-run]\n' "${0##*/}"
}

case "${1:-}" in
  '') ;;
  --dry-run) DRY_RUN=true ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

if (($# > 1)); then
  usage >&2
  exit 2
fi

DATE="$(date -u +'%Y-%m-%d %H:%M UTC')"
SNAPSHOT_STAMP="$(date -u +%Y%m%d-%H%M%S)"
SNAPSHOT="$REPO/memory/snapshots/session-$SNAPSHOT_STAMP.md"

receipt() {
  local message=$1
  mkdir -p "$STATE_DIR"
  printf '[%s] %s\n' "$DATE" "$message" >> "$RECEIPT"
}

on_error() {
  local status=$?
  local line=$1
  trap - ERR
  receipt "Backup failed at script line $line (status $status)" || true
  exit "$status"
}

if [[ ! -d "$REPO/.git" ]] && ! git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  printf 'Backup repository is not a Git worktree: %s\n' "$REPO" >&2
  exit 1
fi

if "$DRY_RUN"; then
  printf 'DRY RUN: repository=%s\n' "$REPO"
  if [[ -f "$SESSION_SOURCE" ]]; then
    printf 'DRY RUN: would copy session snapshot to %s before staging\n' "$SNAPSHOT"
  else
    printf 'DRY RUN: session source absent; no snapshot would be created\n'
  fi
  printf 'DRY RUN: would stage repository content and commit changes if present\n'
  printf 'DRY RUN: would push origin main only after a successful commit\n'
  printf 'DRY RUN: no files, index, commits, receipts, or network state changed\n'
  exit 0
fi

trap 'on_error "$LINENO"' ERR

cd "$REPO"

# Capture the session before staging so a newly created snapshot is committed.
if [[ -f "$SESSION_SOURCE" ]]; then
  mkdir -p "$(dirname "$SNAPSHOT")"
  cp -- "$SESSION_SOURCE" "$SNAPSHOT"
else
  receipt "Session source absent; continuing without a new snapshot"
fi

git add -A

if git diff --cached --quiet; then
  receipt "No changes to commit"
  exit 0
fi

git commit -m "Auto-backup: $DATE"

if git push origin main; then
  receipt "Backup pushed successfully"
else
  receipt "Push failed; inspect Git remote authentication and connectivity"
  trap - ERR
  exit 1
fi
