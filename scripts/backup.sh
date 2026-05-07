#!/usr/bin/env bash
# Hermes Daily Backup Script
# Pushes the immortal stack to GitHub every 24 hours
set -e

REPO="$HOME/hermes-immortal"
DATE=$(date -u +"%Y-%m-%d %H:%M UTC")
LOG="$REPO/.backup-log"

cd "$REPO"

# Stage everything except what .gitignore excludes
git add -A

# Check if there are changes
if ! git diff --cached --quiet; then
  # Save a session snapshot to the memory directory
  mkdir -p "$REPO/memory/snapshots"
  cp "$HOME/hermes-knowledge/logs/current-session.md" "$REPO/memory/snapshots/session-$(date -u +%Y%m%d-%H%M%S).md" 2>/dev/null || true
  
  # Commit with timestamp
  git commit -m "Auto-backup: $DATE"
  
  # Push to GitHub (will fail if key not added yet — that's ok)
  if git push origin main 2>&1 | tee -a "$LOG" | tail -3; then
    echo "[$DATE] ✅ Backup pushed successfully" >> "$LOG"
  else
    echo "[$DATE] ⚠️ Push failed — SSH key may not be added to GitHub" >> "$LOG"
    echo "[$DATE] Add this key: $(cat ~/.ssh/id_ed25519.pub)" >> "$LOG"
  fi
else
  echo "[$DATE] No changes to commit" >> "$LOG"
fi

