#!/usr/bin/env bash
set -euo pipefail

# rename_to_main.sh
# Usage: run this from anywhere inside the git repository. It will:
#  - prompt for a commit message and commit any staged/unstaged changes
#  - rename the current branch to 'main' (if not already)
#  - add an 'origin' remote if missing (prompts for URL)
#  - push 'main' to origin and set upstream
#  - delete remote 'master' if it exists
#  - update the remote HEAD locally

print() { printf '%s\n' "$*"; }

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  print "Error: not inside a git repository." >&2
  exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

print "Repository: $REPO_ROOT"

read -rp "Commit message (leave empty to skip commit): " COMMIT_MSG

if [ -n "$COMMIT_MSG" ]; then
  # Check for changes (staged or unstaged)
  if git status --porcelain | grep -q .; then
    print "Staging all changes and committing..."
    git add -A
    git commit -m "$COMMIT_MSG"
  else
    print "No changes to commit. Skipping commit step."
  fi
else
  print "No commit message provided. Skipping commit step."
fi

# Ensure an 'origin' remote exists
if ! git remote | grep -q '^origin$'; then
  read -rp "No 'origin' remote found. Enter remote URL to add as 'origin' (leave empty to skip push): " REMOTE_URL
  if [ -n "$REMOTE_URL" ]; then
    git remote add origin "$REMOTE_URL"
    print "Added remote origin -> $REMOTE_URL"
  else
    print "No remote configured. Local rename only."
  fi
fi

CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
print "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" = "main" ]; then
  print "Already on 'main'."
  if git remote | grep -q '^origin$'; then
    print "Pushing 'main' to origin and setting upstream..."
    git push -u origin main
    git remote set-head origin main || true
  fi
  print "Done."
  exit 0
fi

print "Renaming branch '$CURRENT_BRANCH' -> 'main'..."
git branch -m main

if git remote | grep -q '^origin$'; then
  print "Pushing 'main' to origin and setting upstream..."
  git push -u origin main

  # If remote has a master branch, delete it (best-effort)
  if git ls-remote --exit-code --heads origin master >/dev/null 2>&1; then
    print "Remote branch 'master' exists. Deleting remote 'master'..."
    git push origin --delete master || print "Failed to delete remote 'master' (you may not have permissions)."
  fi

  # Update remote HEAD locally
  git remote set-head origin main || true
else
  print "No remote 'origin' configured; renamed local branch to 'main' only."
fi

print "Rename to 'main' complete."
print "Note: Changing the default branch on GitHub may require a web UI or API call; this script updates branches and remote HEAD locally." 
