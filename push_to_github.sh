#!/bin/bash
# Push AICL changes to GitHub
# Usage: GITHUB_TOKEN=your_token_here ./push_to_github.sh

set -e

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Usage: GITHUB_TOKEN=ghp_xxxxx ./push_to_github.sh"
    echo ""
    echo "To create a token:"
    echo "  1. Go to https://github.com/settings/tokens"
    echo "  2. Generate new token (classic)"
    echo "  3. Select 'repo' scope"
    echo "  4. Copy the token and run:"
    echo "     GITHUB_TOKEN=ghp_xxxxx ./push_to_github.sh"
    exit 1
fi

cd /home/z/my-project

# Configure git credential helper for this push
export GIT_ASKPASS=/tmp/git-askpass.sh
export GITHUB_TOKEN

echo "Pushing 18 commits to GitHub..."
git push https://AFKmoney:${GITHUB_TOKEN}@github.com/AFKmoney/AICL.git main

echo "Push complete!"
