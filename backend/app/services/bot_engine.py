import asyncio
from datetime import datetime, timezone
from enum import Enum
import logging
import time
from typing import Any

from .market_feed import market_feed
from .news_calendar import news_calendar
from .quant_strategy import quant_strategy
from .virtual_broker import virtual_broker

logger = logging.getLogger(__name__)

class EngineStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NEWS_BLACKOUT = "NEWS_BLACKOUT"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    PAUSED = "PAUSED"
    EMERGENCY_STOP = "EMERGENCY_STOP"

class BotEngine:
    def __init__(self):
        self.status: EngineStatus = EngineStatus.ACTIVE
        self.is_running: bool = False
        self.manual_pause: bool = False
        self.last_loop_ts: float = 0
        self.loop_interval_sec: float = 5.0
        self.engine_logs: list[dict[str, Any]] = []

    def log(self, message: str, level: str = "INFO"):
        entry = {
            "time": time.time(),
            "time_str": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
            "level": level,
            "message": message
        }
        self.engine_logs.append(entry)
        if len(self.engine_logs) > 100:
            self.engine_logs.pop(0)

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.log("QuantGold Engine starting background loop...")
        asyncio.create_task(self._main_loop())

    async def _main_loop(self):
        # Initial warm up
        await market_feed.fetch_live_data()
        await news_calendar.fetch_calendar()
        
        while self.is_running:
            try:
                self.last_loop_ts = time.time()
                
                # 1. Update Market Feed
                await market_feed.fetch_live_data()
                
                # 2. Update Virtual Broker with latest tick
                virtual_broker.update_market_prices(market_feed.bid, market_feed.ask)

                # 3. Periodically refresh economic calendar (every 3 minutes)
                if time.time() - news_calendar.last_fetch_ts > 180:
                    await news_calendar.fetch_calendar()
                else:
                    news_calendar.evaluate_blackout_status()

                # 4. Determine Engine State
                if self.manual_pause:
                    self.status = EngineStatus.PAUSED
                elif virtual_broker.circuit_breaker_tripped:
                    self.status = EngineStatus.CIRCUIT_BREAKER
                elif news_calendar.is_blackout:
                    self.status = EngineStatus.NEWS_BLACKOUT
                else:
                    self.status = EngineStatus.ACTIVE

                # 5. Run Quant Strategy if state is ACTIVE
                if self.status == EngineStatus.ACTIVE:
                    signal = quant_strategy.evaluate(
                        candles=market_feed.candles,
                        bid=market_feed.bid,
                        ask=market_feed.ask,
                        account_balance=virtual_broker.balance
                    )

                    # If valid trade signal and no position open, execute
                    if signal.action in ["BUY", "SELL"] and len(virtual_broker.open_positions) == 0:
                        virtual_broker.open_position(
                            symbol="XAUUSD",
                            side=signal.action,
                            lot=signal.lot,
                            entry_price=signal.entry_price,
                            sl_price=signal.sl_price,
                            tp_price=signal.tp_price,
                            reason=signal.reason
                        )
                        self.log(f"Auto-Executed {signal.action} 0.01 lot at {signal.entry_price}. Reason: {signal.reason}", "ORDER")

            except Exception as e:
                logger.error(f"Error in engine main loop: {e}", exc_info=True)
                self.log(f"Engine Loop Warning: {e}", "ERROR")

            await asyncio.sleep(self.loop_interval_sec)

    def pause(self):
        self.manual_pause = True
        self.status = EngineStatus.PAUSED
        self.log("Engine MANUALLY PAUSED by user via Dashboard.", "WARN")

    def resume(self):
        self.manual_pause = False
        if virtual_broker.circuit_breaker_tripped:
            self.status = EngineStatus.CIRCUIT_BREAKER
        elif news_calendar.is_blackout:
            self.status = EngineStatus.NEWS_BLACKOUT
        else:
            self.status = EngineStatus.ACTIVE
        self.log("Engine RESUMED by user via Dashboard.", "INFO")

    def emergency_flatten(self):
        self.manual_pause = True
        self.status = EngineStatus.EMERGENCY_STOP
        virtual_broker.close_all_positions(market_feed.bid, "Emergency Flatten All by User")
        self.log("EMERGENCY FLATTEN TRIGGERED: All open positions liquidated. Engine paused.", "CRITICAL")

    def get_full_state(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "manual_pause": self.manual_pause,
            "last_heartbeat": self.last_loop_ts,
            "market": market_feed.get_summary(),
            "news": news_calendar.get_summary(),
            "broker": virtual_broker.get_summary(),
            "strategy": quant_strategy.last_signal.to_dict() if quant_strategy.last_signal else None,
            "logs": list(reversed(self.engine_logs))[:20]
        }

bot_engine = BotEngine()
