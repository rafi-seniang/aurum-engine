# aurum-engine

> **Disclaimer**: Ini adalah proyek eksperimental sistem trading kuantitatif XAUUSD (Gold) yang dibuat khusus atas request teman (Jibran) yang pengen punya tools trading berbasis aturan statistik dan risk management yang jelas, bukan sekadar tebak-tebakan atau sinyal telegram yang bikin rungkad.

---

## Latar Belakang

Proyek ini berawal dari obrolan santai soal trading emas (XAUUSD). Banyak trader retail yang loss bukan karena salah arah, tapi karena **overtrading, emosi, spread broker pas news, dan manajemen risiko yang berantakan**.

Tujuan proyek ini simpel:
1. **Memisahkan emosi dari eksekusi**: Biar kodingan dan matematika yang jalanin aturan mainnya.
2. **Strict Risk First**: Kalau kondisi market lagi kacau (misal ada rilis CPI atau NFP), sistem otomatis istirahat (lockout).
3. **Remote Cockpit**: Engine jalan di server/laptop, tapi bisa dipantau dan dikontrol langsung lewat HP (PWA / Android).

---

## Fitur Utama

- **Live Market Data**: Integrasi live tick & candle data M5 untuk XAUUSD.
- **Automated Economic News Blackout**: Otomatis berhenti trading 15 menit sebelum dan 30 menit sesudah rilis berita US high impact (CPI, NFP, FOMC) via Forex Factory calendar feed.
- **Statistical Volatility Strategy**: Menggunakan kalkulasi ATR (*Average True Range*) & dynamic channel breakout, disaring dengan filter likuiditas sesi market (London & New York session).
- **Virtual Realistic Broker (Paper Trading)**: Mensimulasikan kondisi broker real (spread Exness Pro ~15-16 pts, slippage, lot mikro 0.01, dan circuit breaker max drawdown 2% per hari).
- **Bridging Ready**: Tersedia layer abstraction untuk dicolok ke MetaTrader 5 (MT5) akun live sewaktu-waktu.
- **Mobile Control Cockpit**: Web app responsif (React + Tailwind + TradingView Lightweight Charts) yang bisa diinstall di HP via PWA atau Android APK untuk pause, resume, pantau posisi, dan panic liquidation.

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pandas, Pydantic, Pytest
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, TradingView Lightweight Charts, Lucide Icons
- **Mobile Wrapper**: Capacitor Android / PWA
- **Tunneling**: Cloudflare Quick Tunnels

---

## Cara Menjalankan

### 1. Backend Engine
```bash
# Masuk ke direktori backend
cd backend

# Install dependencies (disarankan pakai venv atau uv)
pip install -r requirements.txt

# Jalankan server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend
```bash
# Masuk ke direktori frontend
cd frontend

# Install package
npm install

# Jalankan dev server
npm run dev
```

### 3. Testing
Untuk memastikan seluruh logika matematika strategi, risk management, news filter, dan API endpoint berfungsi normal:
```bash
pytest backend/tests/ -v
```

---

## Catatan

Proyek ini dibangun untuk tujuan edukasi, riset kuantitatif, dan hobi semata. Perdagangan aset dengan leverage (CFD/Forex/Gold) memiliki risiko kerugian modal yang signifikan. Selalu gunakan akun demo/paper trading terlebih dahulu.
