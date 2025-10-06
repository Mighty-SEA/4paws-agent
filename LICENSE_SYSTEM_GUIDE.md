# 🔐 License System Guide

## 📱 Quick Start (For Google Sheets Setup)

**Want to manage license from your phone in 30 seconds?**

👉 **See: `GOOGLE_SHEETS_QUICK_START.md`** (5-minute setup, one-time only!)

Once setup, you can update client license from phone every month without remote desktop! 🚀

---

## Overview

Sistem license dengan halaman expired di port 3100 (mirip first-time installation page).

---

## 📋 Fitur

### Saat License Valid:
- ✅ MariaDB start
- ✅ Backend start  
- ✅ Frontend start
- ✅ Client akses http://localhost:3100 → Aplikasi normal

### Saat License Expired:
- ❌ MariaDB TIDAK start
- ❌ Backend TIDAK start
- ❌ Frontend TIDAK start
- ✅ License server start di port 3100
- 🔒 Client akses http://localhost:3100 → Halaman "License Expired"

---

## 🚀 Test License Server

### Test Manual (Standalone):

```bash
python license_server.py
```

Buka browser: http://localhost:3100

**Tampilan:**
```
╔════════════════════════════════════╗
║  🔒 License Expired                ║
║                                    ║
║  Your license has expired          ║
║  Please contact support to renew   ║
║                                    ║
║  📋 License Information             ║
║  Status: Expired                   ║
║  Expired On: 2025-01-31            ║
║                                    ║
║  📞 Contact Support                 ║
║  📧 support@yourcompany.com         ║
║  📱 +62 xxx-xxx-xxxx                ║
╚════════════════════════════════════╝
```

---

## 🔧 Integration dengan Agent (TODO)

### File yang Perlu Dimodifikasi:

**1. core/license.py** (Create New):

```python
from datetime import datetime
import os
import requests

class LicenseManager:
    """Manage license checking"""
    
    # Google Sheets API URL
    API_URL = "https://script.google.com/macros/s/YOUR_ID/exec"
    
    def check_license(self):
        """Check if license is valid"""
        # 1. Hard expiry check
        expiry = datetime.fromisoformat(
            os.getenv('LICENSE_EXPIRY', '2025-01-31')
        )
        
        if datetime.now() > expiry:
            return {
                'valid': False,
                'reason': 'License Expired',
                'expiry': str(expiry.date()),
                'message': f'Your license expired on {expiry.date()}'
            }
        
        # 2. Online check (Google Sheets)
        try:
            response = requests.get(self.API_URL, timeout=5)
            data = response.json()
            
            if data['status'] == 'suspended':
                return {
                    'valid': False,
                    'reason': 'License Suspended',
                    'expiry': data.get('expiry'),
                    'message': 'License suspended by administrator'
                }
                
        except Exception as e:
            pass  # Offline OK
        
        return {'valid': True}
```

**2. agent.py - Update start_all:**

```python
def start_all(self, skip_setup: bool = False):
    """Start all services (with optional auto-setup)"""
    logger.info("🚀 Starting all services...")
    
    # Check license
    from core.license import LicenseManager
    license = LicenseManager().check_license()
    
    if not license['valid']:
        # License invalid - show expired page
        logger.error("╔════════════════════════════════════════╗")
        logger.error("║   🔒 LICENSE EXPIRED                   ║")
        logger.error("╠════════════════════════════════════════╣")
        logger.error(f"║  {license['message']:<38} ║")
        logger.error("║                                        ║")
        logger.error("║  Starting license page on port 3100... ║")
        logger.error("╚════════════════════════════════════════╝")
        
        # Start license server instead of apps
        from license_server import start_license_server
        start_license_server(port=3100, license_data=license)
        
        # Open browser
        import webbrowser
        webbrowser.open("http://localhost:3100")
        
        return False
    
    # License valid - continue normal start
    logger.info("✅ License valid")
    self.start_mariadb()
    self.start_backend()
    self.start_frontend()
```

---

## 📱 Workflow Client

### License Valid (Normal):
```
Client jalankan aplikasi:
├─ Agent check license → VALID ✅
├─ Start MariaDB
├─ Start Backend
├─ Start Frontend
└─ http://localhost:3100 → Aplikasi normal
```

### License Expired:
```
Client jalankan aplikasi:
├─ Agent check license → EXPIRED ❌
├─ Start license server di port 3100
├─ Browser auto-open → Halaman expired
└─ Client lihat pesan: "Contact support"

Client hubungi Anda:
├─ Client transfer payment
├─ Anda update Google Sheets (30 detik)
├─ Client restart aplikasi
└─ ✅ License valid → Aplikasi jalan normal
```

### License Suspended:
```
Client bandel/belum bayar:
├─ Anda buka Google Sheets di HP
├─ Ubah status: "suspended"
├─ Save

Client restart aplikasi:
├─ Agent check → SUSPENDED ❌
├─ Halaman expired muncul
└─ "License suspended. Contact support."
```

---

## 🎨 Customize Halaman Expired

### Edit license_expired.html:

**Contact Info:**
```javascript
// Line ~160
'support_email': 'your-email@example.com',  ← Ganti ini
'support_phone': '+62 xxx-xxx-xxxx'         ← Ganti ini
```

**Design:**
- Warna: Edit CSS di bagian `<style>`
- Icon: Ubah emoji di `<div class="icon">`
- Text: Edit HTML content

---

## 🧪 Testing

### Test 1: License Expired (Hard Expiry)

```bash
# Set expiry ke kemarin
echo "LICENSE_EXPIRY=2025-01-01" > .env

# Start agent
python agent.py start

# Expected:
# - License server start di 3100
# - Browser buka halaman expired
# - Apps tidak jalan
```

### Test 2: License Suspended (Online)

```bash
# Update Google Sheets:
# Cell B1: suspended

# Start agent
python agent.py start

# Expected:
# - License server start
# - Halaman: "License Suspended"
```

### Test 3: License Valid

```bash
# Set expiry ke bulan depan
echo "LICENSE_EXPIRY=2025-12-31" > .env

# Google Sheets:
# Cell B1: active

# Start agent
python agent.py start

# Expected:
# - Apps start normal
# - http://localhost:3100 → Aplikasi
```

---

## 🔄 Auto-Refresh Feature

Halaman license expired punya **auto-refresh** setiap 5 detik:
- Check license status via API
- Jika valid → Auto-redirect ke aplikasi
- User tidak perlu manual refresh!

**Flow:**
```
1. License expired → Halaman expired muncul
2. Admin update Google Sheets → License valid
3. Halaman otomatis detect (5 detik)
4. Auto-redirect ke aplikasi ✅
```

---

## 📊 File Structure

```
4paws-agent/
├── license_expired.html      ← Halaman HTML
├── license_server.py          ← Python HTTP server
├── core/
│   └── license.py            ← License manager (TODO)
├── agent.py                   ← Main agent (integrate)
└── .env
    └── LICENSE_EXPIRY=...    ← Expiry date
```

---

## ✅ Next Steps

1. ✅ HTML page created
2. ✅ License server created
3. ⏳ Create `core/license.py`
4. ⏳ Integrate ke `agent.py`
5. ⏳ Setup Google Sheets API
6. ⏳ Test end-to-end

---

## 🎯 Benefits

| Feature | Benefit |
|---------|---------|
| **Visual Page** | Client tahu kenapa tidak bisa akses |
| **Professional** | Seperti software enterprise |
| **Clear Message** | Contact info jelas |
| **Auto-Refresh** | Otomatis redirect saat valid |
| **No Port Conflict** | Pakai port 3100 (port frontend) |
| **Simple** | Mudah customize |

---

## 💡 Tips

1. **Customize branding** di HTML (logo, warna, text)
2. **Update contact info** di license_server.py
3. **Set expiry date** sesuai payment cycle
4. **Monitor Google Sheets** untuk track client
5. **Test** sebelum deploy ke client

---

**License system siap digunakan!** 🚀

