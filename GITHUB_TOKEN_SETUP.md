# 🔑 GitHub Token Setup Guide

## Why Do You Need This?

GitHub limits API requests to **60 per hour** without authentication. When checking for updates frequently, you'll hit this limit and see errors like:

```
❌ Failed to fetch release info: 403 Client Error: rate limit exceeded
```

With a Personal Access Token, the limit increases to **5,000 requests/hour**!

---

## 📋 Step-by-Step Guide

### 1. Go to GitHub Settings

Visit: **https://github.com/settings/tokens**

Or navigate manually:
1. Click your profile picture (top-right)
2. Settings
3. Developer settings (bottom-left)
4. Personal access tokens → Tokens (classic)

### 2. Generate New Token

1. Click **"Generate new token (classic)"**
2. **Note**: `4Paws Agent API Access` (or any description)
3. **Expiration**: Choose your preference (e.g., 90 days, 1 year, or no expiration)
4. **Select scopes**:
   - ✅ Check **`public_repo`** only
   - This gives read-only access to public repositories
   - No other permissions needed!

### 3. Generate and Copy Token

1. Click **"Generate token"** at the bottom
2. Copy the token immediately (it looks like: `ghp_xxxxxxxxxxxxxxxxxxxx`)
3. ⚠️ **Important**: You won't see it again! Save it somewhere safe.

### 4. Add Token to Agent

Create or edit `.env` file in `4paws-agent/`:

```bash
GITHUB_TOKEN=ghp_your_token_here_1234567890abcdef
```

**Example:**
```bash
GITHUB_TOKEN=ghp_s3cr3tT0k3nH3r3X7Y9Z
```

### 5. Restart Agent

If agent is running, restart it to load the new token:

```bash
# Stop services
python agent.py stop

# Start again
python agent.py start
```

Or restart the GUI/Tray app.

---

## ✅ Verification

Check the agent logs after restart. You should see:

```
🔑 Using GitHub token for API requests
```

Now you can check for updates as many times as you want without hitting rate limits!

---

## 🔒 Security Notes

1. ⚠️ **Never commit `.env` to Git** (it's already in `.gitignore`)
2. The token only has read access to public repos
3. You can revoke the token anytime at: https://github.com/settings/tokens
4. If token is compromised, simply delete it and generate a new one

---

## 🆘 Troubleshooting

### Still getting rate limit errors?

1. Check if `.env` file exists in `4paws-agent/` folder
2. Verify token is correct (no extra spaces, quotes, or newlines)
3. Check agent logs for `🔑 Using GitHub token` message
4. Restart the agent

### Token not working?

1. Make sure scope `public_repo` is selected
2. Token might be expired - check at https://github.com/settings/tokens
3. Regenerate a new token if needed

### Don't want to use token?

That's fine! The agent will work without it, but:
- Limited to 60 requests/hour
- You may see "rate limit exceeded" during frequent checks
- Wait 1 hour for rate limit to reset

---

**Happy updating! 🚀**

