from datetime import datetime, timezone
import logging
from typing import Any
from .market_feed import Candle

logger = logging.getLogger(__name__)

class SignalResult:
    def __init__(
        self,
        action: str,  # "BUY", "SELL", or "HOLD"
        confidence_pct: int,
        lot: float,
        entry_price: float,
        sl_price: float,
        tp_price: float,
        reason: str,
        indicators: dict[str, Any]
    ):
        self.action = action
        self.confidence_pct = confidence_pct
        self.lot = lot
        self.entry_price = entry_price
        self.sl_price = sl_price
        self.tp_price = tp_price
        self.reason = reason
        self.indicators = indicators

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "confidence_pct": self.confidence_pct,
            "lot": self.lot,
            "entry_price": self.entry_price,
            "sl_price": self.sl_price,
            "tp_price": self.tp_price,
            "reason": self.reason,
            "indicators": self.indicators
        }

class QuantStrategyEngine:
    def __init__(self, risk_percent: float = 0.5):
        self.risk_percent = risk_percent
        self.last_signal: SignalResult | None = None

    def compute_atr(self, candles: list[Candle], period: int = 14) -> float:
        if len(candles) < period + 1:
            return 2.50

        tr_list: list[float] = []
        for i in range(1, len(candles)):
            curr = candles[i]
            prev = candles[i - 1]
            tr = max(
                curr.high - curr.low,
                abs(curr.high - prev.close),
                abs(curr.low - prev.close)
            )
            tr_list.append(tr)

        if not tr_list:
            return 2.50

        recent_tr = tr_list[-period:]
        return round(sum(recent_tr) / len(recent_tr), 2)

    def compute_ema(self, values: list[float], period: int) -> float:
        if not values or len(values) < period:
            return values[-1] if values else 0.0

        multiplier = 2.0 / (period + 1.0)
        ema = values[0]
        for val in values[1:]:
            ema = (val - ema) * multiplier + ema
        return round(ema, 2)

    def get_current_session(self) -> tuple[str, bool]:
        utc_hour = datetime.now(timezone.utc).hour
        # London & London/NY Overlap (07:00 to 17:59 UTC): Prime institutional liquidity
        if 7 <= utc_hour < 18:
            return ("LONDON_NY_EXPANSION", True)
        # Asian session (00:00 to 06:59 UTC): Low volume range-bound consolidation
        elif 0 <= utc_hour < 7:
            return ("ASIAN_CONSOLIDATION", False)
        # Late NY / rollover (18:00 to 23:59 UTC): Liquidity slowdown & spread widening
        else:
            return ("LATE_SESSION_SLOWDOWN", False)

    def evaluate(
        self,
        candles: list[Candle],
        bid: float,
        ask: float,
        account_balance: float
    ) -> SignalResult:
        if len(candles) < 30:
            res = SignalResult(
                action="HOLD",
                confidence_pct=0,
                lot=0.01,
                entry_price=ask,
                sl_price=0.0,
                tp_price=0.0,
                reason="Collecting market bars (sample size < 30 bars)...",
                indicators={}
            )
            self.last_signal = res
            return res

        session_name, is_session_tradeable = self.get_current_session()

        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]

        # 1. Volatility calculation (ATR 14)
        atr = self.compute_atr(candles, period=14)
        
        # 2. Multi-tier EMAs
        ema_fast = self.compute_ema(closes[-25:], period=9)
        ema_mid = self.compute_ema(closes[-35:], period=21)
        ema_trend = self.compute_ema(closes[-60:], period=50)

        # 3. Donchian 20-period channels
        donchian_high = max(highs[-21:-1])
        donchian_low = min(lows[-21:-1])

        current_close = closes[-1]
        
        indicators = {
            "atr_14": atr,
            "ema_9": ema_fast,
            "ema_21": ema_mid,
            "ema_50": ema_trend,
            "donchian_high": round(donchian_high, 2),
            "donchian_low": round(donchian_low, 2),
            "session": session_name
        }

        # Session Gate: Suppress breakout orders during Asian consolidation (00:00-07:00 UTC)
        # unless specifically configured, to avoid false breakout whipsaws.
        if not is_session_tradeable:
            res = SignalResult(
                action="HOLD",
                confidence_pct=30,
                lot=0.01,
                entry_price=ask,
                sl_price=0,
                tp_price=0,
                reason=f"Session Filter Active [{session_name}]. Range framing phase; breakout entries held until London Open (07:00 UTC).",
                indicators=indicators
            )
            self.last_signal = res
            return res

        # Volatility Gates
        if atr < 0.80:
            res = SignalResult("HOLD", 20, 0.01, ask, 0, 0, "Volatility below minimum threshold (ATR < $0.80).", indicators)
            self.last_signal = res
            return res
        if atr > 15.00:
            res = SignalResult("HOLD", 10, 0.01, ask, 0, 0, "Abnormal volatility expansion detected (ATR > $15.00).", indicators)
            self.last_signal = res
            return res

        # Sizing and Risk Calculation
        sl_distance = max(1.80, round(atr * 1.5, 2))
        tp_distance = round(sl_distance * 1.8, 2)
        lot = 0.01

        # BUY Signal:
        # Close > EMA 50, EMA 9 > EMA 21, Close breaks Donchian High
        if current_close > ema_trend and ema_fast > ema_mid and current_close >= donchian_high:
            entry = ask
            sl = round(entry - sl_distance, 2)
            tp = round(entry + tp_distance, 2)
            res = SignalResult(
                action="BUY",
                confidence_pct=88,
                lot=lot,
                entry_price=entry,
                sl_price=sl,
                tp_price=tp,
                reason=f"Bullish Donchian Breakout above {donchian_high} with EMA50 ({ema_trend}) Alignment [{session_name}]",
                indicators=indicators
            )
            self.last_signal = res
            return res

        # SELL Signal:
        # Close < EMA 50, EMA 9 < EMA 21, Close breaks Donchian Low
        if current_close < ema_trend and ema_fast < ema_mid and current_close <= donchian_low:
            entry = bid
            sl = round(entry + sl_distance, 2)
            tp = round(entry - tp_distance, 2)
            res = SignalResult(
                action="SELL",
                confidence_pct=88,
                lot=lot,
                entry_price=entry,
                sl_price=sl,
                tp_price=tp,
                reason=f"Bearish Donchian Breakdown below {donchian_low} with EMA50 ({ema_trend}) Alignment [{session_name}]",
                indicators=indicators
            )
            self.last_signal = res
            return res

        res = SignalResult(
            action="HOLD",
            confidence_pct=50,
            lot=0.01,
            entry_price=ask,
            sl_price=0,
            tp_price=0,
            reason=f"Consolidation inside channel ({donchian_low} - {donchian_high}). Awaiting directional breakout.",
            indicators=indicators
        )
        self.last_signal = res
        return res

quant_strategy = QuantStrategyEngine()
