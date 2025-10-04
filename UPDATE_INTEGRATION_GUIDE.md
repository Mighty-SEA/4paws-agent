# 🔄 4Paws Update Integration Guide

Complete guide for integrating auto-update system between Agent and your 4Paws application.

---

## 📋 Overview

The update system allows users to:
1. ✅ Check for updates from the application topbar
2. ✅ Receive notification when updates are available
3. ✅ Update with one click directly from the application
4. ✅ See real-time update progress
5. ✅ Auto-reload after update completes

### Architecture

```
Frontend (Port 3100)  ←→  Backend (Port 3200)  ←→  Agent (Port 5000)
        │                       │                         │
        │  Check Update         │  Forward to Agent       │
        ├──────────────────────>├────────────────────────>│
        │                       │                         │ Check GitHub
        │  Update Info          │  Return Data            │
        │<──────────────────────┤<────────────────────────┤
        │                       │                         │
        │  Start Update         │  Trigger Update         │
        ├──────────────────────>├────────────────────────>│
        │                       │                         │
        │  WebSocket Connection                           │
        │<────────────────────────────────────────────────┤
        │  (Real-time progress updates)                   │
```

---

## 🚀 Implementation Steps

### 1. **Agent Side** (Already Implemented ✅)

The agent now has these endpoints:

#### API Endpoints

**`GET /api/update/check`**
- Returns current versions and available updates
- Response:
  ```json
  {
    "current": {
      "frontend": "0.0.1",
      "backend": "0.0.1"
    },
    "latest": {
      "frontend": "0.0.2",
      "backend": "0.0.2"
    },
    "has_update": true,
    "details": {
      "frontend": {
        "current": "0.0.1",
        "latest": "0.0.2",
        "has_update": true
      },
      "backend": {
        "current": "0.0.1",
        "latest": "0.0.2",
        "has_update": true
      }
    }
  }
  ```

**`POST /api/update/start`**
- Starts the update process in background
- Request body:
  ```json
  {
    "component": "all"  // or "frontend" or "backend"
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "message": "Update started",
    "websocket_channel": "update_progress"
  }
  ```

**WebSocket Events: `update_status`**
- Real-time progress updates during update
- Event data:
  ```json
  {
    "status": "downloading",
    "message": "Downloading updates from GitHub...",
    "progress": 30
  }
  ```
- Status values:
  - `stopping_services` (10%)
  - `downloading` (30%)
  - `extracting` (50%)
  - `migrating` (70%)
  - `restarting` (85%)
  - `completed` (100%)
  - `failed` (0%)

---

### 2. **Backend Integration** (NestJS)

#### A. Install Dependencies

```bash
cd 4paws-backend
npm install socket.io-client
```

#### B. Create Update Module

```bash
nest g module update
```

#### C. Add Files

Copy these files to your backend:
- `update.controller.ts` → `src/update/update.controller.ts`
- `update.module.ts` → `src/update/update.module.ts`

#### D. Update App Module

```typescript
// src/app.module.ts
import { UpdateModule } from './update/update.module';

@Module({
  imports: [
    // ... other imports
    UpdateModule, // Add this
  ],
})
export class AppModule {}
```

#### E. Environment Variables

Add to `.env`:
```env
AGENT_URL=http://localhost:5000
```

#### F. Test Endpoints

```bash
# Check for updates
curl http://localhost:3200/update/check

# Start update
curl -X POST http://localhost:3200/update/start

# Get status
curl http://localhost:3200/update/status
```

---

### 3. **Frontend Integration** (Next.js)

#### A. Install Dependencies

```bash
cd 4paws-frontend
npm install socket.io-client
```

#### B. Add Components

Copy these files to your frontend:
- `UpdateButton.tsx` → `src/components/UpdateButton.tsx`
- `UpdateModal.tsx` → `src/components/UpdateModal.tsx`

#### C. Environment Variables

Add to `.env.local`:
```env
NEXT_PUBLIC_AGENT_URL=http://localhost:5000
```

#### D. Add to Layout/Topbar

```typescript
// app/layout.tsx or components/Topbar.tsx
import UpdateButton from '@/components/UpdateButton';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <header className="topbar">
          {/* Your existing topbar content */}
          
          {/* Add Update Button */}
          <UpdateButton />
        </header>
        
        {children}
      </body>
    </html>
  );
}
```

#### E. Styling (TailwindCSS)

Make sure your `tailwind.config.js` includes:
```javascript
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  // ...
}
```

---

## 🎨 UI/UX Flow

### User Experience

1. **Initial State**
   - Update button (🔄) in topbar
   - No indicator

2. **Update Available**
   - Button turns orange and pulses
   - Red dot appears on icon
   - Auto-show modal after 3 seconds

3. **User Clicks "Update Now"**
   - Modal shows progress
   - Real-time status updates via WebSocket
   - Progress bar animates

4. **Update Stages**
   ```
   ⏹️  Stopping services...     (10%)
   📥 Downloading updates...    (30%)
   📦 Extracting files...       (50%)
   🗄️  Running migrations...    (70%)
   🔄 Restarting services...    (85%)
   ✅ Update complete!          (100%)
   ```

5. **Completion**
   - Show success message
   - Auto-reload page after 2 seconds

---

## 🧪 Testing

### Test Update Flow

1. **Start Agent**
   ```bash
   cd 4paws-agent
   python gui_server.py
   ```

2. **Start Backend**
   ```bash
   cd 4paws-backend
   npm run start:dev
   ```

3. **Start Frontend**
   ```bash
   cd 4paws-frontend
   npm run dev
   ```

4. **Test Update Button**
   - Open http://localhost:3100
   - Look for update button in topbar
   - Click to check for updates

### Mock Update Test

To test without actual updates, modify agent temporarily:

```python
# In gui_server.py - api_update_check()
# Force return update available
return jsonify({
    'current': {
        'frontend': '0.0.1',
        'backend': '0.0.1'
    },
    'latest': {
        'frontend': '0.0.2',
        'backend': '0.0.2'
    },
    'has_update': True,
    # ...
})
```

---

## 🔧 Customization

### Change Update Check Interval

```typescript
// In UpdateButton.tsx
const interval = setInterval(checkForUpdates, 30 * 60 * 1000); // 30 minutes
// Change to: 60 * 60 * 1000 for 1 hour
```

### Disable Auto-Show Modal

```typescript
// In UpdateButton.tsx
// Comment out or remove this useEffect:
useEffect(() => {
  if (updateAvailable && updateInfo && !updating) {
    const timer = setTimeout(() => {
      setShowModal(true);  // Remove this
    }, 3000);
    return () => clearTimeout(timer);
  }
}, [updateAvailable, updateInfo, updating]);
```

### Change Update Progress Steps

```python
# In gui_server.py - perform_update_with_notifications()
# Modify the steps and progress percentages
socketio.emit('update_status', {
    'status': 'custom_step',
    'message': 'Doing custom thing...',
    'progress': 40
})
```

### Add Custom Status Icons

```typescript
// In UpdateModal.tsx - UpdateProgress component
const statusConfig: Record<string, { icon: string; color: string }> = {
  // Add your custom statuses
  custom_step: { icon: '⚙️', color: 'text-purple-500' },
  // ...
};
```

---

## 🚨 Troubleshooting

### Update Button Not Showing

1. Check if `NEXT_PUBLIC_AGENT_URL` is set
2. Verify agent is running on port 5000
3. Check browser console for errors

### "Agent Not Available" Error

1. Make sure agent is running: `python gui_server.py`
2. Check firewall/network settings
3. Verify AGENT_URL in backend `.env`

### WebSocket Not Connecting

1. Check Socket.IO version compatibility
2. Verify CORS settings in agent
3. Check browser console for connection errors

### Update Fails

1. Check agent logs: `logs/agent.log`
2. Verify GitHub releases exist
3. Check network connectivity
4. Ensure MariaDB is running

---

## 📊 API Reference

### Agent Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/update/check` | GET | Check for available updates |
| `/api/update/start` | POST | Start update process |
| `/api/status` | GET | Get services status |

### Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/update/check` | GET | Proxy to agent check |
| `/update/start` | POST | Proxy to agent start |
| `/update/status` | GET | Get current versions |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `update_status` | Agent → Frontend | Update progress notification |
| `connect` | Frontend → Agent | WebSocket connection |

---

## 🎯 Features

- ✅ One-click update from application
- ✅ Real-time progress tracking
- ✅ Auto-reload after update
- ✅ Visual indicators (pulsing icon, red dot)
- ✅ Modal with update details
- ✅ WebSocket real-time communication
- ✅ Error handling and recovery
- ✅ Non-blocking background updates
- ✅ Auto-check every 30 minutes
- ✅ Auto-show modal when update available

---

## 📝 Notes

1. **Port Configuration**
   - Agent: 5000
   - Backend: 3200
   - Frontend: 3100

2. **Update Process**
   - Total time: ~2-5 minutes
   - Downtime: ~10-30 seconds (during restart)
   - Auto-recovery if fails

3. **Requirements**
   - Agent must be running
   - GitHub releases must exist
   - Internet connection required

---

## 🔐 Security

1. **Agent Access**
   - Currently localhost only
   - Add authentication if exposed

2. **Update Verification**
   - Downloads from GitHub releases
   - Verifies package structure

3. **Rollback**
   - Old versions backed up
   - Manual rollback available

---

## 📞 Support

For issues or questions:
- Check agent logs: `logs/agent.log`
- Check browser console
- Review GitHub releases

---

**Last Updated:** October 2025  
**Version:** 1.0.0

Happy Updating! 🚀

