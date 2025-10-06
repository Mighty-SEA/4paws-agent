# 📦 4Paws Agent Portable Guide

## ✅ Portability Features

4Paws Agent dirancang untuk **portable** - bisa di-copy ke komputer lain tanpa instalasi ulang!

### 🎯 Apa yang Portable?

| Komponen | Status | Catatan |
|----------|--------|---------|
| ✅ Node.js | 100% Portable | Standalone binary |
| ✅ pnpm | 100% Portable | Standalone binary |
| ✅ MariaDB | 99% Portable | Data directory portable dalam Windows |
| ✅ Frontend Build | 100% Portable | Static build |
| ✅ Backend Build | 95% Portable | Perlu regenerate Prisma client jika beda OS/arch |
| ✅ Database Data | 99% Portable | Portable dalam OS yang sama |
| ✅ Logs | 100% Portable | Text files |

---

## 📋 Cara Copy ke Komputer Lain

### Langkah 1: Copy Folder
Copy **seluruh folder** aplikasi ke komputer baru:
```
📁 4PawsAgent/
├── 📁 tools/           ← Copy semua
├── 📁 apps/            ← Copy semua
├── 📁 data/            ← Copy semua (database)
├── 📁 logs/            ← Optional (bisa skip)
├── 📁 core/            ← Copy semua
├── agent.py            ← Copy
├── gui_server.py       ← Copy
├── validate-portable.py ← Copy
└── ... (semua file .py dan .bat)
```

### Langkah 2: Validasi Installation
Setelah copy, jalankan script validasi:

```bash
python validate-portable.py
```

Script ini akan:
- ✅ Check apakah semua tools ada
- ✅ Check apakah apps ada
- ✅ Auto-regenerate Prisma client jika perlu
- ✅ Check database

### Langkah 3: Start Aplikasi
Jika validasi OK, langsung start:

```bash
# Via GUI
python gui_server.py

# Atau via CLI
python agent.py start
```

---

## ⚠️ Kondisi yang Memerlukan Setup Ulang

### 1. **Beda Sistem Operasi**
- ❌ Windows → Linux
- ❌ Linux → Windows
- ❌ Windows → macOS

**Solusi:** Install ulang dari scratch

### 2. **Beda Architecture**
- ❌ x64 → ARM
- ❌ 32-bit → 64-bit

**Solusi:** Regenerate Prisma client:
```bash
cd apps/backend
pnpm prisma generate
```

### 3. **Beda Versi MariaDB**
Jika di komputer baru sudah ada MariaDB dengan versi berbeda.

**Solusi:** Export-import database:
```bash
# Di komputer lama
mysqldump -u root -P 3307 4paws_db > backup.sql

# Di komputer baru (setelah setup MariaDB)
mysql -u root -P 3307 4paws_db < backup.sql
```

---

## 🔧 Manual Fix (Jika Auto-Fix Gagal)

### Fix 1: Regenerate Prisma Client
```bash
cd apps/backend
pnpm prisma generate
```

### Fix 2: Reinstall Backend Dependencies
```bash
python agent.py setup backend
```

### Fix 3: Reinitialize MariaDB
```bash
# Backup database dulu!
# Kemudian hapus data directory
rm -rf data/mariadb

# Initialize ulang
python agent.py setup
```

---

## 📝 Checklist Sebelum Copy

Sebelum copy folder ke komputer lain, pastikan:

- [ ] ✅ Semua services sudah **stop** (jangan copy saat running!)
- [ ] ✅ Folder `tools/` ada dan lengkap
- [ ] ✅ Folder `apps/` ada dan lengkap
- [ ] ✅ Folder `data/mariadb/` ada (jika ingin copy database)
- [ ] ✅ File `versions.json` ada (tracking versi)

**Optional:**
- [ ] Bersihkan `logs/` sebelum copy (tidak penting)
- [ ] Export database ke `.sql` file sebagai backup

---

## 🎯 Best Practice

### Untuk Development/Testing
Copy **tanpa** database:
```
📁 4PawsAgent/
├── 📁 tools/      ← Copy
├── 📁 apps/       ← Copy
├── ❌ data/       ← SKIP (biarkan kosong)
└── ... files
```

Setelah copy, jalankan:
```bash
python agent.py setup      # Initialize MariaDB
python validate-portable.py # Validate & fix
python agent.py start      # Start
```

Database akan fresh install dengan seed data default.

### Untuk Production/Migration
Copy **dengan** database:
```
📁 4PawsAgent/
├── 📁 tools/      ← Copy
├── 📁 apps/       ← Copy
├── 📁 data/       ← Copy (database ada di sini)
└── ... files
```

Jalankan:
```bash
python validate-portable.py # Validate & fix
python agent.py start       # Start
```

Database akan terbawa dengan semua data yang ada.

---

## 💡 Tips & Tricks

### 1. Compress sebelum transfer
```bash
# Buat archive
7z a 4PawsAgent-Portable.7z 4PawsAgent/

# Di komputer baru
7z x 4PawsAgent-Portable.7z
```

### 2. Exclude logs saat compress
```bash
7z a 4PawsAgent-Portable.7z 4PawsAgent/ -x!logs/*
```

### 3. Buat portable shortcut
Create `START.bat`:
```batch
@echo off
cd /d "%~dp0"
python gui_server.py
pause
```

---

## ❓ FAQ

### Q: Apakah perlu install Python di komputer baru?
**A:** YA! Python harus installed. Atau gunakan PyInstaller untuk create `.exe` standalone.

### Q: Apakah bisa copy hanya folder `apps/`?
**A:** TIDAK. `tools/` juga harus di-copy karena berisi Node.js & MariaDB portable.

### Q: Database MariaDB bisa rusak saat copy?
**A:** Sangat jarang, tapi bisa terjadi jika:
- Copy saat MariaDB sedang running
- Path terlalu panjang (>260 karakter di Windows)
- Disk corruption

**Solusi:** Selalu backup database ke `.sql` file sebelum copy!

### Q: Apakah `node_modules/` perlu di-copy?
**A:** YA! `node_modules/` berisi dependencies yang sudah terinstall. Jika tidak di-copy, perlu `pnpm install` ulang (lama!).

---

## 🚀 Quick Start (After Copy)

```bash
# 1. Validate
python validate-portable.py

# 2. Start
python agent.py start

# 3. Access
# Frontend: http://localhost:3100
# Backend: http://localhost:3200
# Web GUI: http://localhost:5000
```

---

## 📞 Troubleshooting

### Issue: "Prisma client missing"
```bash
cd apps/backend
pnpm prisma generate
```

### Issue: "MariaDB failed to start"
```bash
# Check log
cat logs/mariadb.log

# Common fix: Reinitialize
python agent.py setup
```

### Issue: "Port already in use"
```bash
# Kill processes on ports
python agent.py stop
```

---

## ✅ Conclusion

4Paws Agent adalah **highly portable** dengan beberapa catatan kecil. Untuk hasil terbaik:

1. ✅ Copy semua folder
2. ✅ Run `validate-portable.py` di komputer baru
3. ✅ Backup database sebelum copy (safety first!)
4. ✅ Test di komputer baru sebelum hapus di komputer lama

**Happy portable deployment! 🎉**

