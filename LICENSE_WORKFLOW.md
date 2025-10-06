# 🔄 License System Workflow

## 📊 Visual Workflow Diagram

### Workflow 1: Normal Monthly Payment (Happy Path ✅)

```
┌─────────────────────────────────────────────────────────────────┐
│ Bulan Januari                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │  1. Pakai aplikasi          │                     │        │
│    │─────────────────────►       │                     │        │
│    │                              │                     │        │
│    │  2. Online check            │                     │        │
│    │◄─────────────────────       │                     │        │
│    │  {status: "active",         │                     │        │
│    │   expiry: "2025-01-31"}     │                     │        │
│    │                              │                     │        │
│    │  ✅ License valid            │                     │        │
│    │  Apps running...            │                     │        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Tanggal 28 Januari (Payment Day)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │  3. Transfer payment        │                     │        │
│    │──────────────────────────────────────────────────►│        │
│    │                              │                     │        │
│    │                              │   4. Confirm payment│        │
│    │                              │◄────────────────────│        │
│    │                              │                     │        │
│    │                              │   5. Update Sheet:  │        │
│    │                              │   B2: 2025-02-28    │        │
│    │                              │   C2: 2025-01-28    │        │
│    │                              │◄────────────────────│        │
│    │                              │   (30 seconds)      │        │
│    │                              │                     │        │
│    │  6. WA: "Sudah diperpanjang"│                     │        │
│    │◄─────────────────────────────────────────────────│        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Bulan Februari                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │  7. Restart app             │                     │        │
│    │─────────────────────►       │                     │        │
│    │                              │                     │        │
│    │  8. Online check            │                     │        │
│    │◄─────────────────────       │                     │        │
│    │  {status: "active",         │                     │        │
│    │   expiry: "2025-02-28"}     │  ← Updated!         │        │
│    │                              │                     │        │
│    │  ✅ License extended!        │                     │        │
│    │  Apps running...            │                     │        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘

Total waktu admin: 30 detik! (Update Google Sheets dari HP)
```

---

### Workflow 2: Client Telat Bayar (Suspend & Resume ⚠️)

```
┌─────────────────────────────────────────────────────────────────┐
│ Tanggal 28 Feb (Payment Due) - Client Belum Bayar              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │                              │   1. Reminder WA    │        │
│    │◄─────────────────────────────────────────────────│        │
│    │  "Pak reminder payment..."  │                     │        │
│    │                              │                     │        │
│    │  Belum transfer ❌           │                     │        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Tanggal 5 Mar (Still Not Paid)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │                              │   2. Open Sheets    │        │
│    │                              │   Update A2:        │        │
│    │                              │   "suspended"       │        │
│    │                              │◄────────────────────│        │
│    │                              │   (10 seconds)      │        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Client Coba Buka Aplikasi                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │  3. Start app               │                     │        │
│    │─────────────────────►       │                     │        │
│    │                              │                     │        │
│    │  4. Online check            │                     │        │
│    │◄─────────────────────       │                     │        │
│    │  {status: "suspended"}      │                     │        │
│    │                              │                     │        │
│    │  ❌ License suspended!       │                     │        │
│    │  Browser opens:             │                     │        │
│    │  ┌──────────────────────┐   │                     │        │
│    │  │ 🔒 License Suspended │   │                     │        │
│    │  │ Contact: +62 812-... │   │                     │        │
│    │  └──────────────────────┘   │                     │        │
│    │                              │                     │        │
│    │  5. WA: "Pak mau bayar!"    │                     │        │
│    │──────────────────────────────────────────────────►│        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘

┌─────────────────────────────────────────────────────────────────┐
│ After Payment                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                      Google Sheets         You (Admin)  │
│    │                              │                     │        │
│    │  6. Transfer ✅              │                     │        │
│    │──────────────────────────────────────────────────►│        │
│    │                              │                     │        │
│    │                              │   7. Update Sheets: │        │
│    │                              │   A2: "active"      │        │
│    │                              │   B2: "2025-03-31"  │        │
│    │                              │   C2: "2025-03-05"  │        │
│    │                              │◄────────────────────│        │
│    │                              │   (30 seconds)      │        │
│    │                              │                     │        │
│    │  8. Restart app             │                     │        │
│    │─────────────────────►       │                     │        │
│    │                              │                     │        │
│    │  9. Online check            │                     │        │
│    │◄─────────────────────       │                     │        │
│    │  {status: "active"}         │                     │        │
│    │                              │                     │        │
│    │  ✅ License active again!    │                     │        │
│    │  Apps running...            │                     │        │
│    │                              │                     │        │
└────┴──────────────────────────────┴─────────────────────┴────────┘
```

---

### Workflow 3: Client Offline Lama (Heartbeat Protection 🔒)

```
┌─────────────────────────────────────────────────────────────────┐
│ Day 1-30: Normal Offline Mode                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client Device           Local Cache (license.dat)             │
│    │                              │                             │
│    │  WiFi OFF 📵                │                             │
│    │                              │                             │
│    │  Start app                  │                             │
│    │─────────────────────►       │                             │
│    │                              │                             │
│    │  Check local cache          │                             │
│    │◄─────────────────────       │                             │
│    │  {last_online_check:        │                             │
│    │   "2025-02-01",             │                             │
│    │   days_offline: 15}         │                             │
│    │                              │                             │
│    │  ✅ Still OK (< 30 days)     │                             │
│    │  Apps running...            │                             │
│    │                              │                             │
└────┴──────────────────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Day 34: Offline Too Long (> MAX_OFFLINE_DAYS)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client Device           Local Cache (license.dat)             │
│    │                              │                             │
│    │  WiFi still OFF 📵           │                             │
│    │                              │                             │
│    │  Start app                  │                             │
│    │─────────────────────►       │                             │
│    │                              │                             │
│    │  Check local cache          │                             │
│    │◄─────────────────────       │                             │
│    │  {last_online_check:        │                             │
│    │   "2025-02-01",             │                             │
│    │   days_offline: 34}         │  ← > 30 days!              │
│    │                              │                             │
│    │  ❌ Online verification      │                             │
│    │     required!               │                             │
│    │                              │                             │
│    │  Browser opens:             │                             │
│    │  ┌──────────────────────────┐│                            │
│    │  │ 🔒 Online Check Required ││                            │
│    │  │ Last check: 34 days ago  ││                            │
│    │  │ Please connect to WiFi   ││                            │
│    │  └──────────────────────────┘│                            │
│    │                              │                             │
└────┴──────────────────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Client Connects to Internet                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                   Google Sheets      Local Cache        │
│    │                          │                   │             │
│    │  WiFi ON ✅              │                   │             │
│    │                          │                   │             │
│    │  Restart app            │                   │             │
│    │                          │                   │             │
│    │  Online check           │                   │             │
│    │─────────────────────►   │                   │             │
│    │◄─────────────────────   │                   │             │
│    │  {status: "active"}     │                   │             │
│    │                          │                   │             │
│    │  Update local cache     │                   │             │
│    │──────────────────────────────────────────►  │             │
│    │  {last_online_check:    │                   │             │
│    │   "2025-03-06"}         │    ← Reset!       │             │
│    │                          │                   │             │
│    │  ✅ License verified!    │                   │             │
│    │  Apps running...        │                   │             │
│    │  Can go offline again   │                   │             │
│    │  for another 30 days    │                   │             │
│    │                          │                   │             │
└────┴──────────────────────────┴───────────────────┴─────────────┘
```

---

## 🔐 3-Layer Protection Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Layer 1: HARD EXPIRY (Cannot Bypass)                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  ┌─────────────────────────────────────────────┐               │
│  │ .env file                                   │               │
│  │ LICENSE_EXPIRY=2025-12-31                   │               │
│  │                                             │               │
│  │ Hard-coded limit ✅                          │               │
│  │ Even if client hacks, cannot bypass        │               │
│  └─────────────────────────────────────────────┘               │
│                                                                 │
│  ▼ IF PASSED ▼                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 2: ONLINE HEARTBEAT (Anti Permanent Offline)            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  ┌─────────────────────────────────────────────┐               │
│  │ data/license.dat                            │               │
│  │ {                                           │               │
│  │   "last_online_check": "2025-02-01"         │               │
│  │ }                                           │               │
│  │                                             │               │
│  │ Check: (now - last_check) <= 30 days       │               │
│  │                                             │               │
│  │ ✅ Prevents client from staying offline     │               │
│  │    forever to avoid expiry                 │               │
│  └─────────────────────────────────────────────┘               │
│                                                                 │
│  ▼ IF PASSED ▼                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 3: REMOTE KILL SWITCH (Instant Control)                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  ┌─────────────────────────────────────────────┐               │
│  │ Google Sheets (Your Phone)                  │               │
│  │                                             │               │
│  │ Status: active / suspended                  │               │
│  │ Expiry: 2025-12-31                          │               │
│  │                                             │               │
│  │ ✅ You control from phone (30 seconds)      │               │
│  │ ✅ Instant suspend if client doesn't pay    │               │
│  │ ✅ Easy extend every month                  │               │
│  └─────────────────────────────────────────────┘               │
│                                                                 │
│  ▼ ALL PASSED ▼                                                │
│                                                                 │
│         ✅ LICENSE VALID → START APPS                           │
│                                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  ❌ ANY LAYER FAILED → SHOW LICENSE EXPIRED PAGE (Port 3100)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📱 Admin Control Panel (Your Phone!)

```
┌─────────────────────────────────────────────────┐
│  Google Sheets Mobile App                      │
│                                                 │
│  📊 4Paws License Manager                       │
│  ┌───────────────────────────────────────────┐ │
│  │ Status  │ Expiry     │ Last Payment      │ │
│  ├───────────────────────────────────────────┤ │
│  │ active  │ 2025-12-31 │ 2025-01-28       │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Actions:                                       │
│  ┌─────────────────────────────────────┐       │
│  │ 📅 Extend License (Monthly)         │       │
│  │    Tap B2 → Change date +1 month    │       │
│  │    Time: 30 seconds                 │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ 🔒 Suspend (Client didn't pay)      │       │
│  │    Tap A2 → Change to "suspended"   │       │
│  │    Time: 10 seconds                 │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │ ✅ Unsuspend (After payment)         │       │
│  │    Tap A2 → Change to "active"      │       │
│  │    Tap B2 → Extend expiry           │       │
│  │    Time: 30 seconds                 │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  Total management time per month: 30 sec! 🚀   │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Summary

| Scenario | Time Required | Tools Needed | Location |
|----------|---------------|--------------|----------|
| **Monthly extend** | 30 seconds | Phone 📱 | Anywhere (Google Sheets app) |
| **Suspend client** | 10 seconds | Phone 📱 | Anywhere |
| **Unsuspend after payment** | 30 seconds | Phone 📱 | Anywhere |
| **Check status** | 5 seconds | Phone 📱 | Anywhere |

**No more:**
- ❌ Remote desktop to client PC
- ❌ Manual .env editing
- ❌ Rebuilding/redeploying agent
- ❌ SSH/FTP file transfers

**Just:**
- ✅ Open Google Sheets on phone
- ✅ Update 1-2 cells
- ✅ Done in 30 seconds!

---

**Ready to setup? See:** `GOOGLE_SHEETS_QUICK_START.md` (5 minutes!)

