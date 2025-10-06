# 📱 Google Sheets License Setup Guide

## 🎯 Keuntungan Google Sheets

✅ **Update dari HP** (30 detik setiap bulan)  
✅ **Tidak perlu remote desktop** ke komputer client  
✅ **Real-time** - langsung efek saat client online  
✅ **Gratis** - tidak perlu server berbayar  
✅ **Suspend instant** - jika client nakal/belum bayar  

---

## 📋 Setup (5 Menit - Sekali Aja!)

### Step 1: Buat Google Sheet Baru

1. **Buka Google Sheets** (dari HP/Laptop)
   - Link: https://sheets.google.com
   
2. **Buat Sheet Baru** → Blank Spreadsheet

3. **Rename Sheet** → "4Paws License Manager"

4. **Setup Table:**

| Column A | Column B   | Column C     | Column D          |
|----------|------------|--------------|-------------------|
| Status   | Expiry     | Last Payment | Notes            |
| active   | 2025-12-31 | 2025-01-28   | Paid January 2025 |

**Copy-paste ini ke Sheet:**
```
Status	Expiry	Last Payment	Notes
active	2025-12-31	2025-01-28	Paid January 2025
```

---

### Step 2: Deploy as Web App (Apps Script)

1. **Klik Extensions** → **Apps Script**

2. **Hapus semua code default**, paste ini:

```javascript
function doGet() {
  try {
    // Get active sheet
    var sheet = SpreadsheetApp.getActiveSheet();
    
    // Read data from row 2 (data row, row 1 is header)
    var status = sheet.getRange('A2').getValue();
    var expiry = sheet.getRange('B2').getValue();
    var lastPayment = sheet.getRange('C2').getValue();
    var notes = sheet.getRange('D2').getValue();
    
    // Return JSON response
    return ContentService.createTextOutput(
      JSON.stringify({
        'status': status,
        'expiry': expiry,
        'last_payment': lastPayment,
        'notes': notes,
        'timestamp': new Date().toISOString()
      })
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    // Return error response
    return ContentService.createTextOutput(
      JSON.stringify({
        'status': 'error',
        'message': error.toString()
      })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

// Test function (for debugging)
function testGet() {
  var result = doGet();
  Logger.log(result.getContent());
}
```

3. **Save** (Ctrl+S):
   - Project name: "4Paws License API"

4. **Deploy**:
   - Klik **Deploy** → **New deployment**
   - Type: **Web app**
   - Description: "4Paws License Checker"
   - Execute as: **Me**
   - Who has access: **Anyone** ⚠️ PENTING!
   - Klik **Deploy**

5. **Authorize**:
   - Klik account Google Anda
   - Klik **Advanced** → **Go to ... (unsafe)**
   - Klik **Allow**

6. **Copy URL**:
   ```
   https://script.google.com/macros/s/AKfycby.../exec
   ```
   ⚠️ **SIMPAN URL INI!** Akan dipakai di Step 3

---

### Step 3: Update .env File

**Di komputer client** (atau kirim via WA ke client):

1. **Buka file** `.env` di folder `4paws-agent`

2. **Update/Tambahkan:**

```bash
# ============================================================================
# LICENSE CONFIGURATION (Google Sheets)
# ============================================================================

# Google Sheets API URL (dari Apps Script deployment)
LICENSE_API_URL=https://script.google.com/macros/s/AKfycby.../exec

# Hard expiry date (fallback jika offline)
LICENSE_EXPIRY=2025-12-31

# Max offline days (client harus online minimal 1x setiap 30 hari)
MAX_OFFLINE_DAYS=30

# Support contact info (tampil di halaman expired)
SUPPORT_EMAIL=support@4paws.com
SUPPORT_PHONE=+62 812-3456-7890
```

3. **Save** file

4. **Restart agent**

---

### Step 4: Test!

**Test dari Browser:**

1. Buka URL Apps Script:
   ```
   https://script.google.com/macros/s/YOUR_ID/exec
   ```

2. **Harusnya muncul JSON:**
   ```json
   {
     "status": "active",
     "expiry": "2025-12-31",
     "last_payment": "2025-01-28",
     "notes": "Paid January 2025",
     "timestamp": "2025-01-28T10:30:00.000Z"
   }
   ```

**Test dari Agent:**

```bash
# Stop agent jika jalan
python agent.py stop

# Start agent
python agent.py start

# Cek log - harusnya ada:
# ✅ License valid (expires: 2025-12-31, 337 days remaining)
# ✅ Online license check successful
```

---

## 🔄 Cara Pakai (Setiap Bulan)

### Client Bayar → Extend License (30 Detik!)

**Dari HP:**

1. **Buka Google Sheets App** 📱
   
2. **Buka "4Paws License Manager"**

3. **Tap Cell B2** (Expiry):
   - Current: `2025-02-28`
   - Update: `2025-03-31` ← Tambah 1 bulan

4. **Tap Cell C2** (Last Payment):
   - Update: `2025-02-28` ← Tanggal bayar

5. **Tap Cell D2** (Notes):
   - Update: `Paid February 2025`

6. **Done!** ✅

**Client:**

7. **Client restart aplikasi**:
   - Close dari System Tray
   - Start lagi

8. **Aplikasi otomatis baca expiry baru** dari Google Sheets ✅

---

### Client Belum Bayar → Suspend License (10 Detik!)

**Dari HP:**

1. **Buka Google Sheets App** 📱

2. **Tap Cell A2** (Status):
   - Current: `active`
   - Update: `suspended`

3. **Save**

**Client:**

4. **Client restart aplikasi** → Keluar halaman:
   ```
   ╔════════════════════════════════════╗
   ║  🔒 License Suspended              ║
   ║  Please contact support            ║
   ╚════════════════════════════════════╝
   ```

5. **Client WA Anda** → Bayar

6. **Anda ubah status kembali** → `active`

7. **Client restart** → ✅ Jalan lagi!

---

## 🔒 Proteksi Berlapis (Hybrid System)

### Layer 1: Hard Expiry (Offline Protection)
```
File: .env
LICENSE_EXPIRY=2025-12-31

✅ Tetap berlaku walau offline
❌ Tidak bisa di-bypass (hard-coded)
```

### Layer 2: Online Heartbeat (Anti Permanent Offline)
```
File: data/license.dat
last_online_check: 2025-01-28

⚠️ Client harus online minimal 1x setiap 30 hari
⚠️ Jika >30 hari offline → Block!
```

### Layer 3: Remote Kill Switch (Google Sheets)
```
Google Sheets Cell A2:
- active → ✅ Jalan
- suspended → ❌ Block!

✅ Real-time control dari HP
✅ Instant suspend/unsuspend
```

---

## 🎯 Skenario Lengkap

### Skenario 1: Client Normal (Bayar Tiap Bulan)

```
Tanggal 1-28 Feb:
├─ Client pakai aplikasi normal ✅
├─ Aplikasi online check → Google Sheets: "active" ✅
└─ Last online check: 2025-02-15

Tanggal 28 Feb (Hari Bayar):
├─ Client transfer payment
├─ Client WA konfirmasi
├─ Anda buka Google Sheets (HP)
├─ Update Expiry: 2025-02-28 → 2025-03-31
├─ Update Last Payment: 2025-02-28
└─ Done! (30 detik)

Tanggal 1 Mar:
├─ Client jalankan aplikasi
├─ Online check → Expiry: 2025-03-31 ✅
├─ License valid → Aplikasi jalan
└─ Client pakai aplikasi normal lagi ✅
```

---

### Skenario 2: Client Telat Bayar

```
Tanggal 28 Feb (Hari Bayar):
├─ Client belum transfer ❌
└─ Anda tunggu 3 hari

Tanggal 3 Mar (Reminder):
├─ Anda WA client: "Reminder payment"
└─ Client: "Besok ya"

Tanggal 5 Mar (Masih Belum Bayar):
├─ Anda buka Google Sheets (HP) 📱
├─ Cell A2: active → suspended
├─ Save
└─ Done! (10 detik)

Tanggal 6 Mar (Client Buka Aplikasi):
├─ Aplikasi start
├─ Online check → Status: "suspended" ❌
├─ Browser otomatis buka halaman:
│   ╔════════════════════════════════════╗
│   ║  🔒 License Suspended              ║
│   ║  Contact: +62 812-3456-7890        ║
│   ╚════════════════════════════════════╝
└─ Client WA Anda: "Pak mau bayar!"

Tanggal 6 Mar (Setelah Transfer):
├─ Client transfer ✅
├─ Anda cek rekening → Masuk ✅
├─ Anda buka Google Sheets (HP)
├─ Cell A2: suspended → active
├─ Cell B2: 2025-03-31 (extend 1 bulan)
├─ Cell C2: 2025-03-06
├─ Save
└─ Done! (30 detik)

Client:
├─ Restart aplikasi
├─ Online check → Status: "active" ✅
└─ Aplikasi jalan normal lagi! ✅
```

---

### Skenario 3: Client Offline Lama

```
Tanggal 1 Feb:
├─ Client pakai aplikasi normal ✅
├─ Online check → Last check: 2025-02-01
└─ License saved to: data/license.dat

Tanggal 1-28 Feb:
├─ Client WiFi mati (offline permanent)
├─ Aplikasi tetap jalan ✅ (max 30 hari offline)
└─ Hard expiry: 2025-12-31 masih jauh

Tanggal 5 Mar (34 hari offline):
├─ Client jalankan aplikasi
├─ Last online check: 2025-02-01 (34 hari lalu)
├─ MAX_OFFLINE_DAYS: 30 ❌
├─ Browser otomatis buka halaman:
│   ╔════════════════════════════════════╗
│   ║  🔒 Online Verification Required   ║
│   ║  Last check: 34 days ago           ║
│   ║  Please connect to internet        ║
│   ╚════════════════════════════════════╝
└─ Aplikasi tidak jalan ❌

Client (Nyalakan WiFi):
├─ Connect WiFi
├─ Restart aplikasi
├─ Online check → Google Sheets: "active" ✅
├─ Last online check updated: 2025-03-05
└─ Aplikasi jalan normal! ✅
```

---

## 📱 Google Sheets Template

**Copy-paste ini ke Sheet Anda:**

### Simple Version (1 Client):

```
Status	Expiry	Last Payment	Notes
active	2025-12-31	2025-01-28	Paid January 2025
```

### Extended Version (Track History):

| Status  | Expiry     | Last Payment | Amount  | Notes              | Payment Method |
|---------|------------|--------------|---------|-------------------|----------------|
| active  | 2025-12-31 | 2025-01-28   | 500000  | Paid January 2025 | Transfer BCA   |

---

### Optional: Payment History Sheet

**Sheet 2 - Payment History:**

| Date       | Amount  | Expiry Extended To | Payment Method | Notes        |
|------------|---------|-------------------|----------------|--------------|
| 2024-12-28 | 500000  | 2025-01-31        | Transfer BCA   | First month  |
| 2025-01-28 | 500000  | 2025-02-28        | Transfer BCA   | Renewal      |
| 2025-02-28 | 500000  | 2025-03-31        | Transfer BCA   | Renewal      |

---

## 🛡️ Security & Privacy

### ✅ Aman:
- URL Apps Script **sulit ditebak** (random string)
- Read-only access (client tidak bisa edit)
- No sensitive data (hanya status & expiry)

### ⚠️ Catatan:
- Jangan share URL Apps Script ke orang lain
- Set Sheet ke **Private** (only you can edit)

---

## 🔧 Troubleshooting

### Problem: "Online check failed"

**Penyebab:**
- WiFi client mati
- Google Sheets API URL salah
- Apps Script deployment tidak public

**Solusi:**
```bash
# Check URL di browser:
https://script.google.com/macros/s/YOUR_ID/exec

# Harusnya return JSON ✅
# Jika error 403 → Deployment tidak public
# Jika error 404 → URL salah
```

---

### Problem: "License suspended" padahal status "active"

**Penyebab:**
- Cache di `data/license.dat` masih old data

**Solusi:**
```bash
# Hapus cache:
rm data/license.dat

# Restart agent:
python agent.py stop
python agent.py start

# Online check akan refresh data ✅
```

---

### Problem: "Online verification required" padahal baru online

**Penyebab:**
- `last_online_check` di `data/license.dat` corrupt

**Solusi:**
```bash
# Hapus license.dat:
rm data/license.dat

# Restart agent:
python agent.py start

# Akan create new license.dat ✅
```

---

## 📊 Monitoring

### Dari Google Sheets (HP):

**Data yang bisa dimonitor:**
- ✅ Status license (active/suspended)
- ✅ Expiry date
- ✅ Last payment date
- ✅ Payment history (jika pakai Sheet 2)

**Tambahan (Optional):**

Bisa tambah kolom untuk track:
- Total payment amount
- Outstanding balance
- Payment method
- Client contact info

---

## 💡 Tips & Best Practices

### 1. Backup Google Sheets URL
```bash
# Simpan di tempat aman:
- Notes app
- Password manager
- Email ke diri sendiri
```

### 2. Set Reminder Payment
```bash
# Di Google Calendar:
Tanggal 25 setiap bulan → "4Paws payment reminder"
```

### 3. Template WA Message
```
Halo Pak/Bu,

Reminder pembayaran aplikasi 4Paws:
📅 Jatuh tempo: 28 Feb 2025
💰 Jumlah: Rp 500.000
🏦 BCA: 1234567890 a.n. Your Name

Terima kasih! 🙏
```

### 4. Quick Suspend Template
```
Status: active → suspended

Client WA: "Pak aplikasi tidak bisa dibuka"
Anda: "Mohon maaf, pembayaran bulan ini belum masuk. 
       Silakan transfer terlebih dahulu. 
       Setelah transfer aplikasi akan langsung aktif kembali."
```

### 5. Quick Extend Template
```
Setelah dapat bukti transfer:
1. Check rekening ✅
2. Google Sheets → Expiry +1 bulan
3. Status → active (jika sebelumnya suspended)
4. WA client: "Sudah kami aktivasi, silakan restart aplikasi. Terima kasih! 🙏"
```

---

## ✅ Checklist Setup

- [ ] Buat Google Sheet
- [ ] Setup table (Status, Expiry, Last Payment, Notes)
- [ ] Deploy Apps Script
- [ ] Authorize access
- [ ] Copy deployment URL
- [ ] Update `.env` file (LICENSE_API_URL)
- [ ] Update contact info (SUPPORT_EMAIL, SUPPORT_PHONE)
- [ ] Test dari browser (JSON response)
- [ ] Test dari agent (online check)
- [ ] Save backup URL di Notes

---

## 🎉 Done!

**Sekarang Anda bisa:**
- ✅ Update license dari HP (30 detik)
- ✅ Suspend/unsuspend instant
- ✅ Monitor payment history
- ✅ No need remote desktop
- ✅ Professional license system!

**Total setup time: 5 menit (sekali aja)**  
**Monthly management: 30 detik per client** 📱

---

## 📞 Need Help?

Jika ada masalah saat setup, cek:
1. Apps Script deployment settings (must be "Anyone")
2. URL sudah benar (ada `/exec` di akhir)
3. Sheet format (kolom A-D sesuai)
4. `.env` file syntax (no typo)

---

**Happy managing! 🚀**

