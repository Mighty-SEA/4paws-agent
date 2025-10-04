# 📚 Environment Files Explained

## 🤔 Mengapa Backend dan Frontend Berbeda?

### Backend: `.env` (Simple)

**NestJS/Express** hanya mengenal **satu file**: `.env`

```
apps/backend/.env  ← Backend membaca file ini saja
```

✅ Simple & straightforward
✅ Tidak peduli production/development
✅ Semua config dalam 1 file

### Frontend: `.env.production` (Next.js System)

**Next.js** punya sistem environment yang lebih kompleks:

```
Next.js Environment Priority:
1. .env.production.local  ← Production + Local overrides
2. .env.local             ← All environments (git-ignored)
3. .env.production        ← Production only ⭐ Agent creates this
4. .env.development       ← Development only
5. .env                   ← Default (all environments)
```

Karena frontend di-build dengan `NODE_ENV=production`, Next.js akan load:
- `.env.production` ← **File utama yang agent buat**
- `.env.local` (jika ada, untuk override)
- `.env` (jika ada, untuk defaults)

## 📁 File Structure

```
4paws-agent/
├── apps/
│   ├── backend/
│   │   └── .env                    ← Backend config (agent auto-creates)
│   │
│   └── frontend/
│       ├── .env.production         ← Frontend production config (agent auto-creates)
│       ├── .env.local              ← Optional: Local overrides (manual, git-ignored)
│       └── .env                    ← Optional: Defaults (manual)
```

## 🎯 Yang Agent Auto-Generate

### 1. Backend: `.env`

```env
DATABASE_URL="mysql://root:@localhost:3307/4paws_db"
JWT_SECRET="4paws-jwt-secret-key-change-in-production"
PORT=3200
NODE_ENV=production
```

**Digunakan untuk:**
- Database connection
- JWT authentication
- Server port
- Environment mode

### 2. Frontend: `.env.production`

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

**Digunakan untuk:**
- Connect ke backend API
- Connect ke agent (untuk updates)
- Server port
- Environment mode

## 🔍 `.env.local` untuk Apa?

### Penjelasan

`.env.local` adalah file **optional** untuk:

✅ **Local overrides** - Override config tanpa ubah file utama
✅ **Git-ignored** - Tidak di-commit (auto-ignored oleh Next.js)
✅ **Developer-specific** - Setiap developer bisa punya config berbeda
✅ **Testing** - Test dengan config berbeda tanpa ubah production

### Kapan Dibutuhkan?

**TIDAK WAJIB!** Agent **TIDAK** auto-create `.env.local`.

Create `.env.local` **hanya jika** kamu butuh:

1. **Test dengan backend port berbeda**
```env
# .env.local
BACKEND_API_URL=http://localhost:4000
```

2. **Test dengan API eksternal**
```env
# .env.local
NEXT_PUBLIC_API_BASE_URL=https://api-staging.example.com
```

3. **Developer-specific config**
```env
# .env.local
NEXT_PUBLIC_DEBUG_MODE=true
NEXT_PUBLIC_DEVELOPER_NAME=John
```

### Cara Membuat `.env.local` (Manual)

**Tidak perlu!** Kecuali untuk testing/override.

Jika perlu, copy dari `.env.production`:

```bash
cd apps/frontend
cp .env.production .env.local
# Edit .env.local sesuai kebutuhan testing
```

## 📊 Priority System (Next.js)

### Scenario 1: Hanya `.env.production`

```
apps/frontend/
└── .env.production    PORT=3100

Next.js loads: PORT=3100 ✅
```

### Scenario 2: `.env.production` + `.env.local`

```
apps/frontend/
├── .env.production    PORT=3100
└── .env.local         PORT=4000

Next.js loads: PORT=4000 ✅ (.env.local wins)
```

### Scenario 3: All files

```
apps/frontend/
├── .env.production         PORT=3100
├── .env.local              PORT=4000
└── .env                    PORT=5000

Next.js loads: PORT=4000 ✅ (.env.local has highest priority)
```

## 🎯 Rekomendasi

### Untuk User Biasa

**Cukup pakai yang agent auto-generate:**

✅ Backend: `.env` (auto-created)
✅ Frontend: `.env.production` (auto-created)

**Jangan** buat file lain kecuali kamu tahu apa yang kamu lakukan.

### Untuk Developer

**Main files:**
- `.env.production` - Production config (agent creates)

**Optional files:**
- `.env.local` - Your personal overrides (create manually, git-ignored)

**Example workflow:**
```bash
# Normal production
npm run start  # Uses .env.production

# Testing dengan override
echo "BACKEND_API_URL=http://localhost:4000" > .env.local
npm run start  # Uses .env.local overrides

# Remove override
rm .env.local
npm run start  # Back to .env.production
```

## 🔐 Git Ignore

Next.js automatically ignores:
- `.env.local`
- `.env*.local`

**Should commit:**
- ✅ `.env.example` (template)
- ✅ `.env.production.example` (template)

**Should NOT commit:**
- ❌ `.env`
- ❌ `.env.local`
- ❌ `.env.production` (contains real values)

## 🛠️ Troubleshooting

### Frontend tidak connect ke backend?

**Check priority:**
```bash
cd apps/frontend

# Check what files exist
ls -la .env*

# If .env.local exists, it might override .env.production
cat .env.local
cat .env.production
```

**Solution:** Remove `.env.local` jika tidak dibutuhkan:
```bash
rm .env.local
```

### Config tidak berubah setelah edit?

**Next.js cache issue:**
```bash
# Restart frontend server
# atau
# Delete .next folder
rm -rf .next
npm run start
```

## 📖 Summary

### Backend (Simple)

```
apps/backend/.env
```
- ✅ Auto-created by agent
- ✅ Contains database, JWT, port config
- ✅ Only file needed

### Frontend (Next.js System)

```
apps/frontend/.env.production  ← Main file (agent creates)
apps/frontend/.env.local       ← Optional override (manual)
```

**Default:**
- ✅ `.env.production` (agent auto-creates)
- ✅ Sudah cukup untuk production use

**Optional:**
- `.env.local` - Jika perlu override untuk testing
- Buat manual, tidak auto-generated
- Git-ignored secara otomatis

## 💡 Key Takeaways

1. **Backend:** 1 file saja (`.env`)
2. **Frontend:** Main file adalah `.env.production`
3. **`.env.local`:** Optional, untuk override, manual create
4. **Agent hanya create yang diperlukan:** `.env` dan `.env.production`
5. **Untuk user biasa:** Cukup pakai default yang agent buat!

Perfect! 🎯

