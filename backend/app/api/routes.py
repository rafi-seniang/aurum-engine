from fastapi import APIRouter
from pydantic import BaseModel
from ..services.bot_engine import bot_engine
from ..services.market_feed import market_feed
from ..services.virtual_broker import virtual_broker

router = APIRouter(prefix="/api")

class SettingsPayload(BaseModel):
    risk_percent: float | None = None
    max_daily_drawdown: float | None = None

@router.get("/status")
def get_status():
    return bot_engine.get_full_state()

@router.get("/candles")
def get_candles():
    return {
        "symbol": market_feed.symbol,
        "candles": [c.to_dict() for c in market_feed.candles]
    }

@router.post("/control/pause")
def pause_bot():
    bot_engine.pause()
    return {"success": True, "status": bot_engine.status.value}

@router.post("/control/resume")
def resume_bot():
    bot_engine.resume()
    return {"success": True, "status": bot_engine.status.value}

@router.post("/control/emergency-flatten")
def emergency_flatten():
    bot_engine.emergency_flatten()
    return {"success": True, "status": bot_engine.status.value}

@router.post("/control/reset-demo")
def reset_demo():
    virtual_broker.balance = 100.0
    virtual_broker.equity = 100.0
    virtual_broker.daily_start_equity = 100.0
    virtual_broker.circuit_breaker_tripped = False
    virtual_broker.circuit_breaker_reason = ""
    virtual_broker.open_positions.clear()
    virtual_broker.closed_trades.clear()
    bot_engine.resume()
    bot_engine.log("Demo account reset to $100.00 clean slate.", "INFO")
    return {"success": True, "message": "Demo reset to $100"}
