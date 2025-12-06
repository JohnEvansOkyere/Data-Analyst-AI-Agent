#!/bin/bash
# Git commands to remove documentation files from repository
# Run these commands in order

echo "🗑️  Removing documentation files from git (keeping README.md)..."

# Remove documentation files from git tracking (but keep them locally)
git rm --cached FUTURE_UPDATES.md 2>/dev/null
git rm --cached QUICK_START.md 2>/dev/null
git rm --cached MODERN_UI_GUIDE.md 2>/dev/null
git rm --cached IMPROVEMENTS_SUMMARY.md 2>/dev/null
git rm --cached NEW_FEATURES_GUIDE.md 2>/dev/null
git rm --cached LATEST_UPDATES.md 2>/dev/null
git rm --cached PROJECT_SUMMARY.md 2>/dev/null
git rm --cached START_HERE.md 2>/dev/null
git rm --cached TODO.md 2>/dev/null
git rm --cached LINKEDIN.md 2>/dev/null
git rm --cached FILE_LIST.txt 2>/dev/null

echo "✅ Documentation files removed from git tracking"
echo "📝 Files are still on your local machine but won't be pushed to GitHub"
echo ""
echo "Next steps:"
echo "1. Run: git status (to verify changes)"
echo "2. Run: git add .gitignore (to add updated .gitignore)"
echo "3. Run: git commit -m 'Remove documentation files from repo, keep only README.md'"
echo "4. Run: git push origin main"
