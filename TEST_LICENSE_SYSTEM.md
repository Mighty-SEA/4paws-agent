# 🧪 Test License System

## Quick Test (Tanpa Google Sheets - 2 Menit)

### Test 1: License Expired Page

**Test halaman expired tanpa setup Google Sheets dulu:**

```bash
# 1. Set expiry ke kemarin (expired)
# Edit .env atau buat .env.test:
echo LICENSE_EXPIRY=2025-01-01 > .env.test

# 2. Backup .env asli (jika ada)
mv .env .env.backup

# 3. Gunakan .env.test
cp .env.test .env

# 4. Start agent
python agent.py stop
python agent.py start

# Expected:
# - License check failed (expired)
# - Browser otomatis buka http://localhost:3100
# - Halaman "License Expired" muncul
# - MariaDB/Backend/Frontend TIDAK jalan
```

**Hasil yang diharapkan:**
```
╔════════════════════════════════════════╗
║   🔒 LICENSE ERROR                     ║
╠════════════════════════════════════════╣
║  License Expired                       ║
║  Your license expired on 2025-01-01    ║
║                                        ║
║  Please contact support:               ║
║  📧 support@4paws.com                   ║
║  📱 +62 812-3456-7890                   ║
╚════════════════════════════════════════╝
```

**Browser:**
- Otomatis buka http://localhost:3100
- Tampil halaman "License Expired" dengan design profesional

---

### Test 2: License Valid

```bash
# 1. Set expiry ke tahun depan (valid)
echo LICENSE_EXPIRY=2026-12-31 > .env

# 2. Restart agent
python agent.py stop
python agent.py start

# Expected:
# - ✅ License valid
# - MariaDB start
# - Backend start
# - Frontend start
# - http://localhost:3100 → Aplikasi normal
```

**Log yang diharapkan:**
```
✅ License valid (expires: 2026-12-31, 700 days remaining)
🗄️  Starting MariaDB...
🔧 Starting Backend API...
🎨 Starting Frontend...
```

---

### Test 3: Restore Configuration

```bash
# Restore .env asli
rm .env
mv .env.backup .env

# Atau buat .env baru:
cp env.example .env

# Edit .env dengan nilai yang sesuai
```

---

## Full Test dengan Google Sheets (10 Menit)

### Prerequisites:
- Google Account
- Browser (untuk setup Apps Script)
- Agent sudah running

---

### Step 1: Setup Google Sheets (5 Menit)

**Ikuti:** `GOOGLE_SHEETS_QUICK_START.md`

**Ringkasan:**
1. Buat Google Sheet baru
2. Copy-paste template dari `GOOGLE_SHEETS_TEMPLATE.txt`
3. Deploy Apps Script
4. Copy URL deployment
5. Update `.env`:
   ```bash
   LICENSE_API_URL=https://script.google.com/macros/s/YOUR_ID/exec
   LICENSE_EXPIRY=2025-12-31
   ```

---

### Step 2: Test Online Check (2 Menit)

```bash
# 1. Test URL dari browser
# Buka: https://script.google.com/macros/s/YOUR_ID/exec

# Expected JSON response:
{
  "status": "active",
  "expiry": "2025-12-31",
  "last_payment": "2025-01-28",
  "notes": "Paid January 2025",
  "timestamp": "2025-01-28T10:30:00.000Z"
}

# 2. Restart agent
python agent.py stop
python agent.py start

# Expected log:
# ✅ License valid (expires: 2025-12-31, 337 days remaining)
# ✅ Online license check successful
```

---

### Step 3: Test Suspend dari Google Sheets (2 Menit)

```bash
# 1. Buka Google Sheet
# 2. Edit Cell A2: active → suspended
# 3. Save

# 4. Restart agent
python agent.py stop
python agent.py start

# Expected:
# - License check failed (suspended)
# - Browser buka http://localhost:3100
# - Halaman: "License Suspended"
# - Apps tidak jalan
```

---

### Step 4: Test Unsuspend (1 Menit)

```bash
# 1. Buka Google Sheet
# 2. Edit Cell A2: suspended → active
# 3. Save

# 4. Restart agent
python agent.py stop
python agent.py start

# Expected:
# - ✅ License valid
# - Apps jalan normal
```

---

### Step 5: Test dari HP (Bonus!)

```bash
# 1. Buka Google Sheets app di HP 📱
# 2. Buka Sheet "4Paws License Manager"
# 3. Tap Cell A2 → Ubah ke "suspended"
# 4. Save

# Di komputer client:
# 5. Restart agent
python agent.py stop
python agent.py start

# Expected:
# - License suspended ❌
# - Halaman expired muncul

# Dari HP lagi:
# 6. Tap Cell A2 → Ubah kembali ke "active"
# 7. Di komputer: Restart agent
# Expected:
# - License active ✅
# - Apps jalan
```

---

### Step 6: Test Offline Mode

```bash
# 1. Dengan license valid & online check sukses
python agent.py start

# Expected log:
# ✅ License valid
# ✅ Online license check successful

# 2. Matikan WiFi (simulate offline)
# 3. Restart agent
python agent.py stop
python agent.py start

# Expected:
# ✅ License valid (using local cache)
# ⚠️  Online check failed (offline mode)
# - Apps tetap jalan (within MAX_OFFLINE_DAYS)

# 4. Nyalakan WiFi lagi
# 5. Restart agent
# Expected:
# ✅ License valid
# ✅ Online license check successful
# - Last online check updated
```

---

### Step 7: Test Offline Too Long (Manual)

```bash
# Test proteksi offline > 30 hari
# (Tidak perlu benar-benar tunggu 30 hari!)

# 1. Edit data/license.dat:
{
  "last_online_check": "2024-12-25T10:00:00"
}

# 2. Matikan WiFi
# 3. Restart agent
python agent.py stop
python agent.py start

# Expected:
# ❌ Online verification required
# - Last check: ~35 days ago
# - Browser buka halaman expired
# - Message: "Please connect to internet"

# 4. Nyalakan WiFi
# 5. Restart agent
# Expected:
# ✅ License valid
# - Last online check updated
# - Apps jalan
```

---

## Test Checklist

### Basic Tests (Tanpa Google Sheets):
- [ ] Test expired (LICENSE_EXPIRY kemarin)
- [ ] Test valid (LICENSE_EXPIRY tahun depan)
- [ ] Halaman expired tampil di port 3100
- [ ] Contact info benar (email & phone)
- [ ] Apps tidak jalan saat expired
- [ ] Apps jalan saat valid

### Google Sheets Tests:
- [ ] Google Sheet created
- [ ] Apps Script deployed
- [ ] URL works (JSON response)
- [ ] Agent online check success
- [ ] Suspend from Sheets works
- [ ] Unsuspend from Sheets works
- [ ] Update expiry from Sheets works
- [ ] Test from mobile phone works

### Advanced Tests:
- [ ] Offline mode works (< 30 days)
- [ ] Offline too long blocks (> 30 days)
- [ ] Web GUI (port 5000) protected dengan password
- [ ] Web GUI license check works
- [ ] System tray license check works
- [ ] Auto-refresh halaman expired works

---

## Common Issues & Solutions

### Issue 1: "Online check failed"

**Symptoms:**
```
⚠️  Online check failed (offline mode)
```

**Causes:**
- WiFi mati
- Google Sheets URL salah
- Apps Script deployment tidak public

**Solutions:**
```bash
# Test URL di browser:
https://script.google.com/macros/s/YOUR_ID/exec

# Harus return JSON (bukan error 403/404)
# Jika error 403: Re-deploy Apps Script, set "Anyone" access
# Jika error 404: URL salah, copy ulang dari deployment
```

---

### Issue 2: Halaman expired tidak muncul

**Symptoms:**
- Agent stop, tapi tidak ada browser auto-open
- Port 3100 tidak bisa diakses

**Causes:**
- License server failed to start
- Port 3100 sudah dipakai

**Solutions:**
```bash
# Check port 3100:
netstat -ano | findstr :3100

# Jika ada proses lain, kill process tersebut
# Atau ubah port di agent.py (LicenseManager.start_license_page)

# Manual start license server:
python license_server.py
```

---

### Issue 3: Apps tetap jalan padahal expired

**Symptoms:**
- LICENSE_EXPIRY sudah expired
- Tapi apps tetap jalan

**Causes:**
- License check di-bypass (ada bug)
- .env tidak terbaca

**Solutions:**
```bash
# Check apakah .env terbaca:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('LICENSE_EXPIRY'))"

# Pastikan output sesuai
# Jika None: .env tidak terbaca, cek path

# Force stop semua:
python agent.py stop
python agent.py start
```

---

## Performance Tests

### Test 1: License Check Speed

```bash
# Measure license check time
import time
from core.license import LicenseManager

start = time.time()
result = LicenseManager().check_license()
end = time.time()

print(f"License check: {(end - start) * 1000:.2f}ms")
print(f"Result: {result}")

# Expected: < 100ms (local check)
# With online: < 2000ms (network request)
```

---

### Test 2: Startup Time Impact

```bash
# Compare startup time with/without license check

# Without license:
# (comment out check in agent.py)
time python agent.py start

# With license:
time python agent.py start

# Expected difference: < 2 seconds
```

---

## Security Tests

### Test 1: Bypass Protection

**Try to bypass license check:**

```bash
# 1. Delete license.dat
rm data/license.dat

# 2. Set future expiry
echo LICENSE_EXPIRY=2030-12-31 > .env

# 3. Block internet (WiFi off)

# 4. Start agent
python agent.py start

# Expected: Still works (hard expiry not reached)
# This is OK - hard expiry is the ultimate protection
```

---

### Test 2: .env Tampering

```bash
# Client tries to extend expiry manually

# 1. With valid license & Google Sheets
# 2. Client edits .env:
LICENSE_EXPIRY=2030-12-31

# 3. Restart agent
python agent.py start

# Expected behavior:
# - If online: Google Sheets expiry used (2025-12-31)
# - If offline but < 30 days: Local expiry used (2030-12-31) ← Works!
# - If offline > 30 days: Blocked (requires online check)

# Conclusion: MAX_OFFLINE_DAYS protects against this
```

---

## Load Tests

### Test: Multiple License Checks

```python
# Test rapid license checking
import time
from core.license import LicenseManager

manager = LicenseManager()

# 100 checks
start = time.time()
for i in range(100):
    result = manager.check_license()
end = time.time()

print(f"100 checks: {(end - start):.2f}s")
print(f"Average: {((end - start) / 100) * 1000:.2f}ms per check")

# Expected: < 5 seconds total (< 50ms per check)
```

---

## ✅ All Tests Passed?

**Jika semua test OK:**
1. ✅ License system working
2. ✅ Google Sheets integration working
3. ✅ Protection working
4. ✅ Ready to deploy!

**Next:** Deploy ke client! 🚀

---

## 📞 Need Help?

**Jika ada test yang fail:**
- Check `GOOGLE_SHEETS_LICENSE_SETUP.md` (troubleshooting section)
- Check log di `logs/agent.log`
- Verify .env configuration
- Verify Google Sheets setup

**Ready to deploy?**
- See: `README_LICENSE.md` (deployment guide)

