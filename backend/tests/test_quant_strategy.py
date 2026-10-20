import pytest
from app.services.market_feed import Candle
from app.services.quant_strategy import quant_strategy, QuantStrategyEngine

def make_candle(t: int, o: float, h: float, l: float, c: float) -> Candle:
    return Candle(time=t, open=o, high=h, low=l, close=c)

def test_atr_computation():
    engine = QuantStrategyEngine()
    # Create 20 synthetic candles with steady $2.00 range
    candles = [make_candle(i * 300, 2600.0, 2602.0, 2600.0, 2601.0) for i in range(25)]
    atr = engine.compute_atr(candles, period=14)
    assert atr > 0
    assert 1.0 <= atr <= 3.0

def test_ema_computation():
    engine = QuantStrategyEngine()
    values = [10.0] * 30
    ema = engine.compute_ema(values, period=10)
    assert ema == 10.0

def test_insufficient_candles_holds():
    engine = QuantStrategyEngine()
    candles = [make_candle(i * 300, 2600.0, 2601.0, 2599.0, 2600.0) for i in range(10)]
    signal = engine.evaluate(candles, bid=2600.0, ask=2600.16, account_balance=100.0)
    assert signal.action == "HOLD"
    assert "sample size" in signal.reason

def test_session_filter_mapping():
    engine = QuantStrategyEngine()
    session_name, is_tradeable = engine.get_current_session()
    assert session_name in ["LONDON_NY_EXPANSION", "ASIAN_CONSOLIDATION", "LATE_SESSION_SLOWDOWN"]
    assert isinstance(is_tradeable, bool)
