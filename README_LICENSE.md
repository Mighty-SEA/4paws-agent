# 📱 Google Sheets License System

Sistem license yang bisa di-manage dari **HP dalam 30 detik** setiap bulan!

---

## 🚀 Quick Start

### Untuk Setup Pertama Kali (5 Menit):

📖 **Baca:** [`GOOGLE_SHEETS_QUICK_START.md`](GOOGLE_SHEETS_QUICK_START.md)

**Steps:**
1. Buat Google Sheet (1 menit)
2. Deploy Apps Script (2 menit)
3. Update `.env` file (1 menit)
4. Test (1 menit)

✅ **Done!** Setup sekali, pakai selamanya!

---

## 📚 Dokumentasi Lengkap

| File | Untuk Apa | Waktu Baca |
|------|-----------|------------|
| **GOOGLE_SHEETS_QUICK_START.md** | Setup cepat (step-by-step) | 2 menit |
| **GOOGLE_SHEETS_LICENSE_SETUP.md** | Guide lengkap + troubleshooting | 10 menit |
| **GOOGLE_SHEETS_TEMPLATE.txt** | Template copy-paste untuk Sheet | 1 menit |
| **LICENSE_WORKFLOW.md** | Visual diagram workflow sistem | 5 menit |
| **LICENSE_SYSTEM_GUIDE.md** | Technical guide (developer) | 10 menit |

---

## 💡 Cara Pakai (Setelah Setup)

### Update License Tiap Bulan (30 Detik dari HP):

```
1. Buka Google Sheets app 📱
2. Tap cell Expiry → Ganti tanggal +1 bulan
3. Tap cell Last Payment → Ganti ke tanggal hari ini
4. Done! ✅

Client restart aplikasi → License extended otomatis!
```

**Contoh:**
```
Before: Expiry = 2025-02-28
After:  Expiry = 2025-03-31  ← Tambah 1 bulan

Client restart → Aplikasi jalan lagi! ✅
```

---

### Suspend Client (10 Detik dari HP):

```
1. Buka Google Sheets app 📱
2. Tap cell Status → Ganti ke "suspended"
3. Done! ❌

Client restart aplikasi → Keluar halaman "License Expired"
```

---

### Unsuspend Setelah Bayar (30 Detik dari HP):

```
Client bayar:
1. Buka Google Sheets app 📱
2. Tap cell Status → Ganti ke "active"
3. Tap cell Expiry → Extend +1 bulan
4. Done! ✅

Client restart → Aplikasi jalan lagi!
```

---

## 🔐 Proteksi Berlapis (Hybrid System)

| Layer | Fungsi | Bisa Di-Bypass? |
|-------|--------|-----------------|
| **Hard Expiry** | Batas akhir di `.env` | ❌ Tidak |
| **Online Heartbeat** | Harus online tiap 30 hari | ❌ Tidak |
| **Remote Kill Switch** | Control dari Google Sheets | ❌ Tidak |

**Result:** Client **TIDAK BISA** pakai aplikasi jika:
- ❌ Tanggal lewat dari expiry
- ❌ Offline > 30 hari
- ❌ Status di Google Sheets = "suspended"

---

## 📱 Keuntungan Google Sheets

| Fitur | Tanpa Google Sheets | Dengan Google Sheets |
|-------|---------------------|----------------------|
| **Update expiry** | Remote desktop (10 menit) | HP (30 detik) ✅ |
| **Suspend instant** | Rebuild agent (1 jam) | HP (10 detik) ✅ |
| **Location** | Harus di laptop | Dari mana saja ✅ |
| **Tools** | Remote desktop, FTP | Google Sheets app ✅ |
| **Complexity** | High | Low ✅ |

---

## 🎯 Skenario Lengkap

### Scenario 1: Normal Monthly Payment

```
28 Feb - Client bayar
├─ Client WA: "Sudah transfer pak"
├─ Anda cek rekening: ✅ Masuk
├─ Buka Google Sheets (HP) 📱
├─ Update Expiry: 2025-03-31
├─ Update Last Payment: 2025-02-28
├─ WA client: "Sudah diperpanjang" ✅
└─ Done! (Total: 1 menit)

Client restart aplikasi → License extended! ✅
```

---

### Scenario 2: Client Telat Bayar

```
28 Feb - Jatuh tempo (Client belum bayar)
├─ 1 Mar: WA reminder
├─ 3 Mar: WA reminder ke-2
└─ 5 Mar: Masih belum bayar ❌

5 Mar - Suspend
├─ Buka Google Sheets (HP) 📱
├─ Status: active → suspended
└─ Done! (10 detik)

Client buka aplikasi:
├─ Halaman: "License Suspended"
└─ Client WA: "Pak mau bayar!"

After payment:
├─ Buka Google Sheets (HP) 📱
├─ Status: suspended → active
├─ Expiry: 2025-03-31
└─ Done! (30 detik)

Client restart → Jalan lagi! ✅
```

---

### Scenario 3: Client Offline Lama

```
Feb - Client WiFi mati (30 hari)
├─ Aplikasi tetap jalan ✅
└─ Pakai cache lokal

Mar - Client masih offline (34 hari)
├─ Aplikasi cek: > 30 hari offline ❌
├─ Halaman: "Please connect to internet"
└─ Apps tidak jalan

Client nyalakan WiFi:
├─ Restart aplikasi
├─ Online check → Google Sheets ✅
├─ Update cache lokal
└─ Aplikasi jalan lagi! ✅
```

---

## ⚙️ File Configuration

### `.env` File (One-time Setup):

```bash
# License Configuration
LICENSE_API_URL=https://script.google.com/macros/s/YOUR_ID/exec
LICENSE_EXPIRY=2025-12-31
MAX_OFFLINE_DAYS=30

# Contact Info
SUPPORT_EMAIL=support@4paws.com
SUPPORT_PHONE=+62 812-3456-7890
```

### Google Sheets (Monthly Update):

```
| Status  | Expiry     | Last Payment | Notes              |
|---------|------------|--------------|-------------------|
| active  | 2025-12-31 | 2025-01-28   | Paid January 2025 |
```

---

## 🔧 Troubleshooting

### Problem: "Online check failed"

**Solution:**
```bash
# Check URL di browser:
https://script.google.com/macros/s/YOUR_ID/exec

# Harus return JSON ✅
```

---

### Problem: License masih expired padahal sudah update Sheets

**Solution:**
```bash
# Hapus cache:
rm data/license.dat

# Restart agent:
python agent.py stop
python agent.py start
```

---

### Problem: Lupa Apps Script URL

**Solution:**
1. Buka Google Sheet
2. Extensions → Apps Script
3. Deploy → Manage deployments
4. Copy URL

---

## 📞 Need Help?

**Setup Issues:**
- Baca: `GOOGLE_SHEETS_LICENSE_SETUP.md` (troubleshooting section)

**Technical Details:**
- Baca: `LICENSE_SYSTEM_GUIDE.md` (developer guide)

**Visual Workflow:**
- Baca: `LICENSE_WORKFLOW.md` (diagram lengkap)

---

## ✅ Checklist

**Sebelum Deploy ke Client:**

- [ ] Google Sheet sudah dibuat
- [ ] Apps Script sudah deployed
- [ ] URL Apps Script sudah disimpan
- [ ] `.env` sudah diupdate (LICENSE_API_URL)
- [ ] Contact info sudah diupdate (email & phone)
- [ ] Test dari browser (JSON response OK)
- [ ] Test dari agent (license check OK)
- [ ] Backup URL di Notes app

**Setelah Setup:**

- [ ] Set reminder di Google Calendar (tanggal 25 tiap bulan)
- [ ] Save template WA reminder payment
- [ ] Buat Sheet "Payment History" (optional)

---

## 🎉 Benefits

| Before Google Sheets | After Google Sheets |
|---------------------|---------------------|
| Remote desktop 10 menit | HP 30 detik ✅ |
| Edit file manual | Tap cell ✅ |
| Harus di laptop | Dari mana saja ✅ |
| Ribet & repot ❌ | Simple & cepat ✅ |

---

## 💰 ROI (Return on Investment)

**Setup time:** 5 menit (sekali aja)  
**Monthly time:** 30 detik per client  

**Savings per month:**
- Manual .env edit: 10 menit
- Remote desktop setup: 5 menit
- Total saved: **15 menit/bulan**

**Annual savings:** 15 menit × 12 bulan = **3 jam/tahun** per client! 🚀

---

## 🚀 Ready to Start?

**Next step:** Baca [`GOOGLE_SHEETS_QUICK_START.md`](GOOGLE_SHEETS_QUICK_START.md)

**Total setup time:** 5 menit  
**Monthly management:** 30 detik  

**Let's go! 🎉**

