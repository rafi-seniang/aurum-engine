# aurum-engine

An algorithmic trading engine and mobile monitoring cockpit for XAUUSD (Gold), built upon a friend's request to explore systematic risk-first trading instead of emotional manual execution.

---

## Overview

The system decouples strategy execution from monitoring. The backend runs on a desktop/server environment handling market feeds, statistical signal generation, risk filters, and broker communication. The frontend provides a responsive mobile cockpit (PWA / Android via Capacitor) for remote monitoring, telemetry, and emergency controls.

---

## Core Capabilities

- **Market Data Feed**: Real-time tick ingestion and M5 candle generation for XAUUSD.
- **Economic Calendar Guard**: Automated news blackout window (halting execution 15m before and 30m after high-impact USD events like CPI, NFP, and FOMC via Forex Factory).
- **Statistical Strategy**: ATR(14) dynamic volatility breakout with Donchian channel tracking, gated by London & New York session liquidity filters.
- **Realistic Paper Broker**: Simulates realistic retail broker conditions (Exness Pro 15-16 pts spread, slippage, micro lots, and a hard 2% daily drawdown circuit breaker).
- **MetaTrader 5 Bridge**: Decoupled interface ready for live MT5 execution when switched from paper mode.
- **Remote Mobile Cockpit**: Real-time TradingView Lightweight Charts, position monitoring, and one-tap emergency liquidation controls.

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pandas, Pydantic, Pytest
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, TradingView Lightweight Charts, Lucide Icons
- **Mobile**: Capacitor Android & PWA
- **Tunneling**: Cloudflare Quick Tunnels

---

## Getting Started

### 1. Backend Engine

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Cockpit

```bash
cd frontend
npm install
npm run dev
```

### 3. Unit Tests

Run the test suite (verifying indicator math, risk rules, news parser, and endpoints):

```bash
pytest
```

---

## Disclaimer

This software is for educational, research, and simulation purposes only. Trading leveraged financial instruments carries substantial risk of capital loss.
