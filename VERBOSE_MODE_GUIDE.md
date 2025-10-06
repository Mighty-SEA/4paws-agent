# 🔊 Verbose Mode - Usage Guide

## Overview
Verbose mode menampilkan output real-time dari pnpm saat instalasi dependencies, berguna untuk troubleshooting dan monitoring progress.

---

## 🚀 Cara Mengaktifkan

### **Metode 1: Gunakan Script Khusus**

#### Windows:
```cmd
start-verbose.bat start
```

#### Linux/Mac:
```bash
chmod +x start-verbose.sh
./start-verbose.sh start
```

### **Metode 2: Set Environment Variable**

#### Windows CMD:
```cmd
set PNPM_VERBOSE=1
python agent.py start
```

#### Windows PowerShell:
```powershell
$env:PNPM_VERBOSE=1
python agent.py start
```

#### Linux/Mac:
```bash
export PNPM_VERBOSE=1
python agent.py start
```

### **Metode 3: Inline Command**

#### Windows:
```cmd
set PNPM_VERBOSE=1 && python agent.py setup-apps
```

#### Linux/Mac:
```bash
PNPM_VERBOSE=1 python agent.py setup-apps
```

---

## 📋 Output Examples

### **Normal Mode (Default)**
```
📦 Installing dependencies...
⏳ This may take 2-5 minutes on slow connections, please wait...
   ⏳ Still installing frontend dependencies... (15s elapsed)
   ⏳ Still installing frontend dependencies... (30s elapsed)
   ⏳ Still installing frontend dependencies... (45s elapsed)
✅ Dependencies installed
```

### **Verbose Mode**
```
📦 Installing dependencies...
📋 Verbose mode enabled - showing pnpm output...
⏳ This may take 2-5 minutes on slow connections, please wait...
   🔄 progress: Resolving 1234 packages...
   🔄 progress: Fetched 123 of 1234 packages
   📥 downloading react@18.2.0
   📥 fetching lodash@4.17.21
   ✅ reused 890 packages
   ✅ added 344 packages in 2m 15s
   ⚠️  deprecated package: old-package@1.0.0
✅ Dependencies installed
```

---

## 🎯 Kapan Menggunakan Verbose Mode?

### ✅ **Gunakan Saat:**

1. **Troubleshooting instalasi lambat**
   - Lihat package mana yang lama di-download
   - Identifikasi bottleneck

2. **Debugging installation errors**
   - Lihat exact error message dari pnpm
   - Package mana yang bermasalah

3. **Monitoring progress detail**
   - Berapa packages sudah di-download
   - Berapa yang di-reuse dari cache

4. **First-time setup di koneksi lambat**
   - Pastikan instalasi berjalan (bukan hang)
   - Estimasi waktu tersisa

### ❌ **Jangan Gunakan Saat:**

1. **Production server** - Log terlalu banyak
2. **Automated scripts** - Bisa memperlambat
3. **Instalasi normal** - Default mode sudah cukup

---

## 📊 Log Symbols & Meanings

| Symbol | Meaning | Example |
|--------|---------|---------|
| 🔄 | Progress update | `Resolving packages...` |
| 📥 | Downloading | `downloading react@18.2.0` |
| ✅ | Success/Added | `added 344 packages` |
| ⚠️ | Warning | `deprecated package` |
| ❌ | Error | `failed to fetch` |
| 📦 | General info | `lockfile generated` |

---

## 🔧 Advanced Configuration

### Custom Timeout dengan Verbose Mode
```bash
# Windows
set PNPM_VERBOSE=1
set PNPM_TIMEOUT=900
python agent.py setup-apps

# Linux/Mac
PNPM_VERBOSE=1 PNPM_TIMEOUT=900 python agent.py setup-apps
```

### Verbose Mode + Custom Registry
```bash
# Windows
set PNPM_VERBOSE=1
pnpm config set registry https://registry.npmmirror.com/
python agent.py setup-apps

# Linux/Mac
export PNPM_VERBOSE=1
pnpm config set registry https://registry.npmmirror.com/
python agent.py setup-apps
```

---

## 📝 Log File Location

Verbose output juga disimpan di:
```
logs/agent.log          # Full log dengan verbose output
logs/backend.log        # Backend runtime logs
logs/frontend.log       # Frontend runtime logs
logs/mariadb.log        # MariaDB server logs
```

---

## 🐛 Troubleshooting

### Verbose Mode Tidak Aktif?

1. **Cek environment variable:**
   ```cmd
   # Windows
   echo %PNPM_VERBOSE%
   
   # Linux/Mac
   echo $PNPM_VERBOSE
   ```
   
   Harus menampilkan: `1`

2. **Gunakan script khusus:**
   ```cmd
   start-verbose.bat start
   ```

3. **Cek version agent:**
   ```cmd
   python agent.py --version
   ```
   
   Harus versi 1.1 atau lebih baru

### Log Terlalu Banyak / Spam?

Verbose mode sudah di-filter untuk hanya menampilkan:
- Progress updates
- Download status
- Packages added/reused
- Warnings & errors

Jika masih terlalu banyak, gunakan normal mode:
```cmd
# Unset variable
set PNPM_VERBOSE=
python agent.py start
```

### Performance Impact?

Verbose mode menambah:
- **CPU**: +1-2% (minimal)
- **Memory**: +10-20MB (buffering output)
- **Time**: +5-10s (processing logs)

**Total Impact**: Negligible untuk troubleshooting

---

## 📖 Command Reference

### Semua Command dengan Verbose Mode

```bash
# Setup tools dengan verbose
PNPM_VERBOSE=1 python agent.py setup

# Install apps dengan verbose
PNPM_VERBOSE=1 python agent.py install all

# Setup apps dengan verbose (RECOMMENDED untuk troubleshooting)
PNPM_VERBOSE=1 python agent.py setup-apps

# Start dengan verbose
PNPM_VERBOSE=1 python agent.py start

# Update dengan verbose
PNPM_VERBOSE=1 python agent.py update
```

---

## 💡 Tips & Best Practices

1. **Gunakan verbose mode saat first-time installation**
   - Lebih jelas apa yang sedang terjadi
   - Early detection jika ada masalah

2. **Save log output untuk debugging**
   ```cmd
   PNPM_VERBOSE=1 python agent.py setup-apps > installation.log 2>&1
   ```

3. **Kombinasi dengan tail untuk monitoring**
   ```bash
   # Terminal 1: Run installation
   PNPM_VERBOSE=1 python agent.py setup-apps
   
   # Terminal 2: Monitor logs
   tail -f logs/agent.log
   ```

4. **Matikan verbose setelah troubleshooting**
   ```cmd
   set PNPM_VERBOSE=
   ```

---

## 🆘 Support

Jika masih ada masalah setelah menggunakan verbose mode:

1. **Copy full log output**
2. **Share installation.log** (jika ada)
3. **Sertakan informasi:**
   - OS & version
   - Internet speed
   - Disk space available
   - Antivirus software

---

**Created**: October 5, 2025
**Version**: 1.1.0
**Last Updated**: October 5, 2025

