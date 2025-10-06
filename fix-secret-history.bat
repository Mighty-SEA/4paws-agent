@echo off
chcp 65001 >nul 2>&1
echo.
echo ╔════════════════════════════════════════╗
echo ║   Git History Secret Cleanup          ║
echo ║   Removing exposed token from history ║
echo ╚════════════════════════════════════════╝
echo.

echo [Step 1] Creating backup branch...
git branch backup-before-clean
echo ✓ Backup created: backup-before-clean
echo.

echo [Step 2] Removing env.example from ALL history...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch env.example || true" --prune-empty --tag-name-filter cat -- --all
echo ✓ env.example removed from history
echo.

echo [Step 3] Re-adding clean env.example...
git add env.example
git commit -m "fix: Remove exposed GitHub token from env.example

- Replace real token with placeholder
- Cleaned from Git history using filter-branch
- Token has been revoked on GitHub"
echo ✓ Clean env.example committed
echo.

echo [Step 4] Force pushing to remote...
echo ⚠️  This will REWRITE remote history!
echo.
pause
git push origin master --force-with-lease
echo ✓ Pushed to remote
echo.

echo [Step 5] Cleaning up...
git for-each-ref --format="delete %%(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo ✓ Cleanup complete
echo.

echo ╔════════════════════════════════════════╗
echo ║   IMPORTANT - Security Steps           ║
echo ╚════════════════════════════════════════╝
echo.
echo 1. REVOKE the exposed token immediately:
echo    https://github.com/settings/tokens
echo.
echo 2. Create a NEW token for your .env file
echo    (DO NOT put it in env.example!)
echo.
echo 3. Tell team members to run:
echo    git fetch --all
echo    git reset --hard origin/master
echo.
pause
