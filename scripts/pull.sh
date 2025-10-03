#!/usr/bin/env bash
set -euo pipefail

# pull.sh
# Usage: run this in a clone of the repository on another machine. It will:
#  - ensure 'origin' remote exists
#  - fetch origin
#  - create and checkout 'main' tracking 'origin/main' if needed
#  - pull the latest changes

print() { printf '%s\n' "$*"; }

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  print "Error: not inside a git repository." >&2
  exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

print "Repository: $REPO_ROOT"

if ! git remote | grep -q '^origin$'; then
  read -rp "No 'origin' remote found. Enter remote URL to add as 'origin': " REMOTE_URL
  if [ -n "$REMOTE_URL" ]; then
    git remote add origin "$REMOTE_URL"
    print "Added remote origin -> $REMOTE_URL"
  else
    print "No remote configured. Aborting."
    exit 1
  fi
fi

print "Fetching from origin..."
git fetch origin --prune

# If origin/main exists, create a local main that tracks it, else create main from current branch
if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  if git show-ref --verify --quiet refs/heads/main; then
    print "Local 'main' exists. Checking out and pulling..."
    git checkout main
    git pull --rebase origin main
  else
    print "Creating local 'main' to track origin/main..."
    git checkout -b main origin/main
  fi
else
  print "Remote 'origin/main' not found. Creating local 'main' from current branch and pushing..."
  CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
  git checkout -b main
  git push -u origin main
fi

print "Pull complete. You're on branch '$(git symbolic-ref --short HEAD)' with the latest from origin."
