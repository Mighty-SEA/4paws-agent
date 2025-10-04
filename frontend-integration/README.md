# Frontend Update Integration Files

## 📁 Files in this Directory

1. **UpdateButton.tsx** - Main update button component for topbar
2. **UpdateModal.tsx** - Modal dialog for update process
3. **README.md** - This file

## 🚀 Quick Setup

### 1. Copy Files to Your Frontend

```bash
# From 4paws-agent directory
cp frontend-integration/UpdateButton.tsx ../4paws-frontend/src/components/
cp frontend-integration/UpdateModal.tsx ../4paws-frontend/src/components/
```

### 2. Install Dependencies

```bash
cd ../4paws-frontend
npm install socket.io-client
```

### 3. Add Environment Variable

Create or edit `.env.local`:
```env
NEXT_PUBLIC_AGENT_URL=http://localhost:5000
```

### 4. Add to Your Layout

```typescript
// In your layout or topbar component
import UpdateButton from '@/components/UpdateButton';

<header>
  {/* Your existing topbar content */}
  <UpdateButton />
</header>
```

### 5. Test It

```bash
npm run dev
```

Open http://localhost:3100 and look for the 🔄 icon in your topbar!

## 🎨 Customization

### Change Check Interval

Edit `UpdateButton.tsx`:
```typescript
// Line ~45
const interval = setInterval(checkForUpdates, 30 * 60 * 1000);
// Change 30 to your desired minutes
```

### Change Button Style

Edit the button className in `UpdateButton.tsx`:
```typescript
className={`your-custom-classes ${updateAvailable ? 'your-pulse-class' : ''}`}
```

### Change Modal Animation

Edit `UpdateModal.tsx` animations or add your own Tailwind classes.

## 📦 What's Included

### UpdateButton Component

Features:
- 🔄 Icon that pulses when update available
- 🔴 Red dot indicator
- ⏳ Loading state during check
- 🎯 Click to check or show modal
- ⏰ Auto-check every 30 minutes
- 🔔 Auto-show modal when update available

### UpdateModal Component

Features:
- 🎨 Beautiful gradient design
- 📊 Update details (frontend/backend versions)
- ⚡ Real-time progress via WebSocket
- 📈 Animated progress bar
- ✅ Auto-reload on completion
- ❌ Error handling
- 🚫 Prevent close during update

## 🧪 Testing

### Test Without Real Updates

1. Start agent: `cd ../4paws-agent && python gui_server.py`
2. Start backend: `cd ../4paws-backend && npm run start:dev`
3. Start frontend: `cd ../4paws-frontend && npm run dev`
4. Click update button

### Mock Update Available

In `UpdateButton.tsx`, modify `checkForUpdates`:
```typescript
const data: UpdateInfo = {
  current: { frontend: '0.0.1', backend: '0.0.1' },
  latest: { frontend: '0.0.2', backend: '0.0.2' },
  has_update: true,
  // ... rest of mock data
};
setUpdateInfo(data);
setUpdateAvailable(true);
```

## 📝 TypeScript Types

Both components are fully typed with TypeScript interfaces:
- `UpdateInfo` - Update information structure
- `UpdateStatus` - Progress status structure
- Component props are typed

## 🎯 Features

- ✅ Type-safe with TypeScript
- ✅ Responsive design
- ✅ Dark mode support
- ✅ Accessibility ready
- ✅ Error handling
- ✅ Loading states
- ✅ Real-time WebSocket updates
- ✅ Auto-reload after update

## 🔧 Dependencies

```json
{
  "socket.io-client": "^4.5.0"
}
```

Make sure this is in your `package.json`.

## 🎨 Styling

Components use Tailwind CSS. Make sure your `tailwind.config.js` includes the components directory:

```javascript
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
}
```

## 📞 Need Help?

See the main `UPDATE_INTEGRATION_GUIDE.md` for complete documentation.

---

Happy coding! 🚀

