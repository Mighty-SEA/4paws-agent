# 🔧 Environment Configuration Guide

## Overview

Agent automatically generates environment files for both frontend and backend applications.

## 📦 Backend Configuration

### File: `.env`

**Auto-generated** by agent when backend is installed.

```env
DATABASE_URL="mysql://root:@localhost:3307/4paws_db"
JWT_SECRET="4paws-jwt-secret-key-change-in-production"
PORT=3200
NODE_ENV=production
```

### Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `mysql://root:@localhost:3307/4paws_db` | MariaDB connection string |
| `JWT_SECRET` | Auto-generated | JWT token secret (change in production) |
| `PORT` | `3200` | Backend API port |
| `NODE_ENV` | `production` | Environment mode |

### Location
```
apps/backend/.env
```

## 🎨 Frontend Configuration

### File 1: `.env.production`

**Auto-generated** by agent for production builds.

```env
# Backend API Configuration
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200

# Agent API Configuration (for updates)
NEXT_PUBLIC_AGENT_URL=http://localhost:5000

# Server Configuration
NODE_ENV=production
PORT=3100
```

### File 2: `.env.local` (Optional)

**Auto-generated** for development.

```env
# Backend API Configuration (Development)
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200

# Agent API Configuration (for updates)
NEXT_PUBLIC_AGENT_URL=http://localhost:5000

# Server Configuration
PORT=3100
```

### Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_API_URL` | `http://localhost:3200` | Backend API endpoint (server-side) |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:3200` | Backend API endpoint (client-side) |
| `NEXT_PUBLIC_AGENT_URL` | `http://localhost:5000` | Agent API endpoint (for updates) |
| `NODE_ENV` | `production` | Environment mode |
| `PORT` | `3100` | Frontend server port |

### Location
```
apps/frontend/.env.production    # Production config
apps/frontend/.env.local          # Development config (optional)
```

## 🤖 Automatic Generation

### When Files Are Created

1. **Backend `.env`**
   - Created during: `install backend` or `setup-apps backend`
   - Triggered by: `AppManager.setup_env(backend_dir, "backend")`

2. **Frontend `.env.production`**
   - Created during: `install frontend` or `setup-apps frontend`
   - Triggered by: `AppManager.setup_env(frontend_dir, "frontend")`

3. **Frontend `.env.local`**
   - Created during: Same as `.env.production`
   - Optional development override

### Generation Logic

```python
if app_type == "backend":
    # Create .env
    env_content = f"""DATABASE_URL="mysql://..."
JWT_SECRET="..."
PORT={Config.BACKEND_PORT}
NODE_ENV=production
"""
else:
    # Create .env.production
    env_prod_content = f"""BACKEND_API_URL=http://localhost:{Config.BACKEND_PORT}
NEXT_PUBLIC_API_BASE_URL=http://localhost:{Config.BACKEND_PORT}
NODE_ENV=production
PORT={Config.FRONTEND_PORT}
"""
    
    # Also create .env.local
    env_local_content = f"""BACKEND_API_URL=http://localhost:{Config.BACKEND_PORT}
NEXT_PUBLIC_API_BASE_URL=http://localhost:{Config.BACKEND_PORT}
PORT={Config.FRONTEND_PORT}
"""
```

## 🔄 File Priority (Frontend)

Next.js loads environment files in this order:

1. `.env.production` (production builds)
2. `.env.local` (all environments, overrides)
3. `.env` (default)

**Agent generates:**
- ✅ `.env.production` - Production configuration
- ✅ `.env.local` - Development/local overrides

## 📝 Manual Customization

### Backend

Edit `apps/backend/.env`:
```env
DATABASE_URL="mysql://root:@localhost:3307/4paws_db"
JWT_SECRET="your-custom-secret-here"  # Change this!
PORT=3200
NODE_ENV=production

# Add custom variables
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Frontend

Edit `apps/frontend/.env.production`:
```env
# Backend API
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200

# Custom variables
NODE_ENV=production
PORT=3100
NEXT_PUBLIC_APP_NAME=4Paws Pet Management
```

## 🚀 Production Deployment

### Change These Values

**Backend `.env`:**
```env
DATABASE_URL="mysql://user:password@your-db-host:3306/4paws_db"
JWT_SECRET="use-a-strong-random-secret-here"
PORT=3200
NODE_ENV=production
```

**Frontend `.env.production`:**
```env
BACKEND_API_URL=https://api.yourservice.com
NEXT_PUBLIC_API_BASE_URL=https://api.yourservice.com
NEXT_PUBLIC_AGENT_URL=https://agent.yourservice.com  # Or localhost:5000 if local
NODE_ENV=production
PORT=3100
```

## 🔒 Security Notes

### ⚠️ Important

1. **Never commit** `.env` files to Git
2. **Change JWT_SECRET** in production
3. **Use HTTPS** for production API URLs
4. **Strong passwords** for database

### .gitignore

Make sure these are ignored:
```gitignore
.env
.env.local
.env.production
.env.development
```

## 🛠️ Troubleshooting

### Backend Can't Connect to Database

**Check**: `DATABASE_URL` in `apps/backend/.env`

```env
# Should match MariaDB configuration
DATABASE_URL="mysql://root:@localhost:3307/4paws_db"
```

### Frontend Can't Connect to Backend

**Check**: API URLs in `apps/frontend/.env.production`

```env
# Should match backend PORT
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200
NEXT_PUBLIC_AGENT_URL=http://localhost:5000
```

### Port Already in Use

**Change**: Ports in both files

**Backend `.env`:**
```env
PORT=3201  # Changed from 3200
```

**Frontend `.env.production`:**
```env
BACKEND_API_URL=http://localhost:3201  # Updated
NEXT_PUBLIC_API_BASE_URL=http://localhost:3201
PORT=3101  # Changed from 3100
```

**Update Agent Config** (`agent.py`):
```python
class Config:
    BACKEND_PORT = 3201  # Updated
    FRONTEND_PORT = 3101  # Updated
```

## 📖 Environment Variables Explained

### Why Multiple API URLs in Frontend?

```env
BACKEND_API_URL=http://localhost:3200              # Server-side (SSR)
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200     # Client-side (Browser)
NEXT_PUBLIC_AGENT_URL=http://localhost:5000        # Agent API (Updates)
```

- **`BACKEND_API_URL`**: Used by Next.js server (SSR, API routes)
- **`NEXT_PUBLIC_API_BASE_URL`**: Used by browser (client-side fetches)
- **`NEXT_PUBLIC_AGENT_URL`**: Used by update button to check/trigger updates

### Why `.env.production` vs `.env`?

- **`.env`**: Default environment (all modes)
- **`.env.production`**: Production-specific overrides
- **`.env.local`**: Local development overrides

**Agent creates** `.env.production` so production builds have correct configuration automatically.

## ✅ Verification

### Check Backend Config

```bash
cd apps/backend
cat .env
```

Should see:
```env
DATABASE_URL="mysql://root:@localhost:3307/4paws_db"
JWT_SECRET="4paws-jwt-secret-key-change-in-production"
PORT=3200
NODE_ENV=production
```

### Check Frontend Config

```bash
cd apps/frontend
cat .env.production
```

Should see:
```env
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200
NEXT_PUBLIC_AGENT_URL=http://localhost:5000
NODE_ENV=production
PORT=3100
```

## 🎯 Summary

### What Agent Does

✅ Auto-generates `.env` for backend
✅ Auto-generates `.env.production` for frontend
✅ Auto-generates `.env.local` for frontend
✅ Configures correct ports and URLs
✅ Sets production environment

### What You Should Do

✅ Review generated files
✅ Change `JWT_SECRET` for production
✅ Update API URLs for production deployment
✅ Add custom variables as needed
✅ Keep files secure (don't commit to Git)

Perfect! 🎉

