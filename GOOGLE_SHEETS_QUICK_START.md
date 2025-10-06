# 📱 Google Sheets Quick Start (5 Menit!)

## Step 1: Buat Sheet (1 Menit)

1. Buka: https://sheets.google.com
2. New Blank Spreadsheet
3. Copy-paste ini ke Sheet:

```
Status	Expiry	Last Payment	Notes
active	2025-12-31	2025-01-28	Paid January 2025
```

---

## Step 2: Deploy Apps Script (2 Menit)

1. **Extensions** → **Apps Script**

2. **Paste code ini** (hapus semua code lama):

```javascript
function doGet() {
  try {
    var sheet = SpreadsheetApp.getActiveSheet();
    var status = sheet.getRange('A2').getValue();
    var expiry = sheet.getRange('B2').getValue();
    var lastPayment = sheet.getRange('C2').getValue();
    var notes = sheet.getRange('D2').getValue();
    
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
    return ContentService.createTextOutput(
      JSON.stringify({
        'status': 'error',
        'message': error.toString()
      })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
```

3. **Save** (Ctrl+S) → Project name: "4Paws License"

4. **Deploy** → **New deployment**:
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone** ⚠️
   - Deploy

5. **Authorize** → Allow

6. **Copy URL**:
   ```
   https://script.google.com/macros/s/AKfycby.../exec
   ```

---

## Step 3: Update .env (1 Menit)

**Di komputer client:**

```bash
# Buka .env, update ini:

LICENSE_API_URL=https://script.google.com/macros/s/YOUR_URL/exec
LICENSE_EXPIRY=2025-12-31
SUPPORT_EMAIL=your-email@example.com
SUPPORT_PHONE=+62 812-xxx-xxxx
```

---

## Step 4: Test! (1 Menit)

**Test dari browser:**
```
Buka: https://script.google.com/macros/s/YOUR_URL/exec

Harusnya muncul JSON:
{
  "status": "active",
  "expiry": "2025-12-31",
  ...
}
```

**Test dari agent:**
```bash
python agent.py stop
python agent.py start

# Cek log:
# ✅ License valid
# ✅ Online license check successful
```

---

## ✅ Done!

**Sekarang update dari HP (30 detik setiap bulan):**

1. Buka Google Sheets app 📱
2. Tap Cell B2 → Update expiry: `2025-03-31`
3. Tap Cell C2 → Update payment: `2025-02-28`
4. Done!

Client restart aplikasi → License extended! ✅

---

**Lihat guide lengkap:** `GOOGLE_SHEETS_LICENSE_SETUP.md`

