import asyncio
import logging
import time
from typing import Any
import httpx

logger = logging.getLogger(__name__)

class Candle:
    def __init__(self, time: int, open: float, high: float, low: float, close: float, volume: float = 0):
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def to_dict(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "open": round(self.open, 2),
            "high": round(self.high, 2),
            "low": round(self.low, 2),
            "close": round(self.close, 2),
            "volume": self.volume
        }

class MarketFeedService:
    def __init__(self):
        self.symbol = "XAUUSD"
        self.latest_price: float = 2650.0  # sensible default before first fetch
        self.bid: float = 2649.92
        self.ask: float = 2650.08
        self.spread_points: int = 16  # ~$0.16 typical on Exness Pro
        self.day_change_percent: float = 0.0
        self.day_high: float = 2660.0
        self.day_low: float = 2640.0
        self.last_update_ts: float = 0
        self.candles: list[Candle] = []
        self._client = httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})

    async def fetch_live_data(self) -> bool:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=5m&range=1d"
        try:
            resp = await self._client.get(url)
            if resp.status_code != 200:
                logger.warning(f"Market feed returned HTTP {resp.status_code}")
                return False

            data = resp.json()
            result = data["chart"]["result"][0]
            meta = result["meta"]
            
            raw_price = meta.get("regularMarketPrice")
            if not raw_price:
                # Fallback to last close
                quote = result["indicators"]["quote"][0]
                closes = [c for c in quote.get("close", []) if c is not None]
                if closes:
                    raw_price = closes[-1]
            
            if raw_price:
                self.latest_price = round(float(raw_price), 2)
                # Model realistic Exness Pro spread (~14-18 points = $0.14 - $0.18)
                spread_val = 0.16
                self.bid = round(self.latest_price - (spread_val / 2), 2)
                self.ask = round(self.latest_price + (spread_val / 2), 2)
                self.spread_points = int(spread_val * 100)
                
                prev_close = meta.get("previousClose") or meta.get("chartPreviousClose") or self.latest_price
                if prev_close > 0:
                    self.day_change_percent = round(((self.latest_price - prev_close) / prev_close) * 100, 2)
                
                self.day_high = round(float(meta.get("regularMarketDayHigh", self.latest_price)), 2)
                self.day_low = round(float(meta.get("regularMarketDayLow", self.latest_price)), 2)
                self.last_update_ts = time.time()

            # Parse 5-minute candles
            timestamps = result.get("timestamp", [])
            indicators = result["indicators"]["quote"][0]
            opens = indicators.get("open", [])
            highs = indicators.get("high", [])
            lows = indicators.get("low", [])
            closes = indicators.get("close", [])
            volumes = indicators.get("volume", [])

            parsed_candles: list[Candle] = []
            for i in range(len(timestamps)):
                t = timestamps[i]
                o = opens[i] if i < len(opens) else None
                h = highs[i] if i < len(highs) else None
                l = lows[i] if i < len(lows) else None
                c = closes[i] if i < len(closes) else None
                v = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
                
                if o is not None and h is not None and l is not None and c is not None:
                    parsed_candles.append(Candle(
                        time=t,
                        open=float(o),
                        high=float(h),
                        low=float(l),
                        close=float(c),
                        volume=float(v)
                    ))

            if parsed_candles:
                self.candles = parsed_candles
            return True
        except Exception as e:
            logger.error(f"Error fetching market feed: {e}")
            return False

    def get_summary(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.latest_price,
            "bid": self.bid,
            "ask": self.ask,
            "spread_points": self.spread_points,
            "day_change_percent": self.day_change_percent,
            "day_high": self.day_high,
            "day_low": self.day_low,
            "last_updated": self.last_update_ts,
            "candle_count": len(self.candles)
        }

market_feed = MarketFeedService()
