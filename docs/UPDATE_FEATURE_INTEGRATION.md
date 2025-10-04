# 🔄 Update Feature Integration Guide

## Overview

The update feature allows frontend users to check for and install updates directly from the application. This document explains how the frontend update button integrates with the agent.

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (Port 3100)    │
│                 │
│  UpdateButton   │ ──┐
│  Component      │   │
└─────────────────┘   │
                      │ HTTP + WebSocket
                      │
                      ▼
┌─────────────────────────────┐
│   Agent Web GUI             │
│  (Port 5000)                │
│                             │
│  ✅ /api/update/check       │ ◄─── Check for updates (cached 1h)
│  ✅ /api/update/start       │ ◄─── Start update process
│  ✅ WebSocket: update_status│ ◄─── Real-time progress
└─────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────┐
│   GitHub Releases           │
│                             │
│  • Frontend releases        │
│  • Backend releases         │
└─────────────────────────────┘
```

## 🔧 Configuration Required

### Frontend Environment Variables

**File**: `apps/frontend/.env.production`

```env
# Backend API Configuration
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200

# Agent API Configuration (for updates) ← REQUIRED
NEXT_PUBLIC_AGENT_URL=http://localhost:5000

# Server Configuration
NODE_ENV=production
PORT=3100
```

### Why NEXT_PUBLIC_AGENT_URL?

The frontend `UpdateButton` component uses this to connect to the agent:

```typescript
const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL ?? 'http://localhost:5000';

// Check for updates
const res = await fetch(`${AGENT_URL}/api/update/check`);
```

## 📡 API Endpoints

### 1. Check for Updates

**Endpoint**: `GET /api/update/check`

**Purpose**: Check if updates are available for frontend and backend

**Caching**: Results cached for 1 hour (3600 seconds)

**Response**:
```json
{
  "current": {
    "frontend": "0.0.2",
    "backend": "0.0.5"
  },
  "latest": {
    "frontend": "0.0.3",
    "backend": "0.0.6"
  },
  "has_update": true,
  "details": {
    "frontend": {
      "current": "0.0.2",
      "latest": "0.0.3",
      "has_update": true
    },
    "backend": {
      "current": "0.0.5",
      "latest": "0.0.6",
      "has_update": true
    }
  },
  "cached": false,
  "cache_age": 0,
  "next_check_in": 3600
}
```

### 2. Start Update

**Endpoint**: `POST /api/update/start`

**Purpose**: Start the update process

**Body**:
```json
{
  "component": "all"  // or "frontend" or "backend"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Update started",
  "websocket_channel": "update_progress"
}
```

### 3. WebSocket Updates

**Channel**: `update_status`

**Events**:
```json
// Stopping services
{
  "status": "stopping_services",
  "message": "Stopping services...",
  "progress": 10
}

// Downloading
{
  "status": "downloading",
  "message": "Downloading updates from GitHub...",
  "progress": 30
}

// Extracting
{
  "status": "extracting",
  "message": "Extracting and installing updates...",
  "progress": 50
}

// Setup (dependencies & migrations)
{
  "status": "setup",
  "message": "Installing dependencies and running migrations...",
  "progress": 70
}

// Restarting
{
  "status": "restarting",
  "message": "Starting services...",
  "progress": 90
}

// Complete
{
  "status": "complete",
  "message": "Update completed successfully!",
  "progress": 100
}
```

## 🎨 Frontend Component

### UpdateButton Usage

```tsx
import UpdateButton from '@/components/update/update-button';

// In your layout/topbar
<UpdateButton />
```

### Features

✅ **Auto-check**: Checks for updates on mount
✅ **Periodic check**: Re-checks every 30 minutes
✅ **Visual indicator**: Red dot when updates available
✅ **Modal UI**: Beautiful update modal with progress
✅ **Real-time updates**: WebSocket progress tracking
✅ **Auto-reload**: Page refreshes after update complete

### Component Flow

```
1. Mount → Check for updates
2. If update available → Show red dot indicator
3. User clicks button → Open modal
4. User clicks "Update Now" → POST /api/update/start
5. Connect to WebSocket → Receive progress updates
6. Show progress bar → Update status messages
7. Complete → Auto-refresh page
```

## 🔄 Update Process Flow

### Step-by-Step

```
1. Frontend: Check for updates
   └─ GET /api/update/check
   └─ Agent: Call GitHub API (cached 1h)
   └─ Return: Update info

2. User clicks "Update Now"
   └─ POST /api/update/start
   └─ Agent: Start background update thread

3. Agent: Stop all services
   └─ Stop frontend (port 3100)
   └─ Stop backend (port 3200)
   └─ WebSocket: { status: "stopping_services", progress: 10 }

4. Agent: Start loading servers
   └─ Start loading page on port 3100
   └─ Start loading page on port 3200
   └─ WebSocket: { status: "downloading", progress: 30 }

5. Agent: Download & install updates
   └─ Download from GitHub
   └─ Extract to apps/frontend & apps/backend
   └─ WebSocket: { status: "extracting", progress: 50 }

6. Agent: Setup apps
   └─ pnpm install (dependencies)
   └─ Run migrations (database)
   └─ WebSocket: { status: "setup", progress: 70 }

7. Agent: Restart services
   └─ Stop loading servers
   └─ Start frontend (port 3100)
   └─ Start backend (port 3200)
   └─ WebSocket: { status: "restarting", progress: 90 }

8. Complete!
   └─ WebSocket: { status: "complete", progress: 100 }
   └─ Frontend: Auto-reload page
   └─ User sees updated version!
```

## 🛡️ Error Handling

### Frontend Can't Connect to Agent

**Symptom**: Update button doesn't show or fails to check

**Solution**: Verify `NEXT_PUBLIC_AGENT_URL` in `.env.production`

```env
NEXT_PUBLIC_AGENT_URL=http://localhost:5000
```

**Check agent is running**:
```bash
curl http://localhost:5000/api/update/check
```

### Update Check Too Frequent

**Problem**: GitHub API rate limiting

**Solution**: Already implemented! Update checks are cached for 1 hour.

```
First check → GitHub API call
Subsequent checks (within 1h) → Cached result
After 1h → New GitHub API call
```

### Update Fails During Process

**Frontend behavior**:
- Shows error message in modal
- Can retry update
- Services remain in previous state

**Agent logs**:
- Check logs in Web GUI (port 5000)
- Download logs for debugging

## 🔐 Security Considerations

### CORS Configuration

Agent allows requests from frontend:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3100", "http://localhost:3200"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### WebSocket Authentication

Currently: Open (localhost only)

**For production**: Add authentication token

```typescript
const socket = io(AGENT_URL, {
  auth: {
    token: process.env.NEXT_PUBLIC_AGENT_TOKEN
  }
});
```

## 📊 Performance

### Update Check

- **First check**: ~2-3 seconds (GitHub API)
- **Cached checks**: <10ms (instant)
- **Cache duration**: 1 hour
- **Auto-clear**: On update start

### Update Process

- **Download**: 1-2 minutes (depends on internet)
- **Install**: 3-5 minutes (dependencies)
- **Total**: ~5-10 minutes

### GitHub Rate Limits

- **Limit**: 5000 requests/hour (authenticated)
- **Usage**: ~1 request/hour (with caching)
- **Safety**: 99.98% under limit

## 🧪 Testing

### Test Update Check

```bash
# Check for updates
curl http://localhost:5000/api/update/check

# Expected response
{
  "current": { "frontend": "0.0.2", "backend": "0.0.5" },
  "has_update": false,
  "cached": false
}
```

### Test Update Process

1. Open frontend: http://localhost:3100
2. Click update button (top-right)
3. Click "Check for Updates"
4. If available, click "Update Now"
5. Watch progress in modal
6. Wait for completion & auto-reload

### Simulate Update Available

Modify `versions.json`:
```json
{
  "frontend": { "version": "0.0.1", "updated_at": "..." },
  "backend": { "version": "0.0.1", "updated_at": "..." }
}
```

Restart agent → Check for updates → Should show updates available

## 📝 Troubleshooting Checklist

### Update Button Not Visible

- [ ] `NEXT_PUBLIC_AGENT_URL` set in `.env.production`?
- [ ] Frontend rebuilt after adding env var?
- [ ] Agent running on port 5000?

### Can't Check for Updates

- [ ] Agent accessible at http://localhost:5000?
- [ ] CORS configured correctly?
- [ ] GitHub API rate limit not exceeded?
- [ ] Internet connection working?

### Update Fails

- [ ] Agent has write permissions to apps/ folder?
- [ ] Enough disk space available?
- [ ] GitHub releases exist and are downloadable?
- [ ] MariaDB running for migrations?

### Progress Not Updating

- [ ] WebSocket connection established?
- [ ] Browser DevTools shows WebSocket messages?
- [ ] Agent logs show progress updates?

## ✅ Verification

### Check Environment Setup

```bash
# Frontend
cd apps/frontend
grep NEXT_PUBLIC_AGENT_URL .env.production
# Should output: NEXT_PUBLIC_AGENT_URL=http://localhost:5000
```

### Test Full Flow

1. ✅ Frontend loads
2. ✅ Update button visible
3. ✅ Click button → Modal opens
4. ✅ Check updates → Shows status
5. ✅ Update available → Shows versions
6. ✅ Click update → Progress shown
7. ✅ Complete → Auto-reload
8. ✅ New version active

## 🎯 Summary

### Auto-Generated Configuration

Agent automatically creates:
- ✅ `.env.production` with `NEXT_PUBLIC_AGENT_URL=http://localhost:5000`
- ✅ `.env.local` with same configuration
- ✅ Correct ports for all services

### No Manual Setup Required!

Just install apps and everything works:
```bash
# Install
python agent.py install all

# Setup
python agent.py setup-apps

# Start
python agent.py start
```

Frontend update button automatically connects to agent!

Perfect! 🎉

