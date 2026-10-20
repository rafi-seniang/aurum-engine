import logging
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

class Position:
    def __init__(
        self,
        symbol: str,
        side: str,  # "BUY" or "SELL"
        lot: float,
        entry_price: float,
        sl_price: float,
        tp_price: float,
        reason: str
    ):
        self.id = str(uuid.uuid4())[:8]
        self.symbol = symbol
        self.side = side.upper()
        self.lot = round(lot, 2)
        self.entry_price = round(entry_price, 2)
        self.sl_price = round(sl_price, 2)
        self.tp_price = round(tp_price, 2)
        self.reason = reason
        self.open_time = time.time()
        self.current_price = self.entry_price
        self.floating_pnl = 0.0

    def update_price(self, bid: float, ask: float):
        # For BUY: exit at Bid; for SELL: exit at Ask
        if self.side == "BUY":
            self.current_price = bid
            # 1 lot = 100 oz. 0.01 lot = 1 oz. PnL = (current - entry) * lot * 100
            diff = self.current_price - self.entry_price
            self.floating_pnl = round(diff * self.lot * 100.0, 2)
        else:
            self.current_price = ask
            diff = self.entry_price - self.current_price
            self.floating_pnl = round(diff * self.lot * 100.0, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "lot": self.lot,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "sl_price": self.sl_price,
            "tp_price": self.tp_price,
            "floating_pnl": self.floating_pnl,
            "open_time": self.open_time,
            "reason": self.reason
        }

class TradeRecord:
    def __init__(
        self,
        id: str,
        symbol: str,
        side: str,
        lot: float,
        entry_price: float,
        exit_price: float,
        pnl: float,
        open_time: float,
        close_time: float,
        close_reason: str
    ):
        self.id = id
        self.symbol = symbol
        self.side = side
        self.lot = lot
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.pnl = round(pnl, 2)
        self.open_time = open_time
        self.close_time = close_time
        self.close_reason = close_reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "lot": self.lot,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "pnl": self.pnl,
            "open_time": self.open_time,
            "close_time": self.close_time,
            "close_reason": self.close_reason
        }

class VirtualBrokerService:
    def __init__(self, initial_balance: float = 100.0, max_daily_drawdown_pct: float = 2.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.margin = 0.0
        self.free_margin = initial_balance
        self.daily_start_equity = initial_balance
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        
        self.open_positions: list[Position] = []
        self.closed_trades: list[TradeRecord] = []
        
        self.circuit_breaker_tripped: bool = False
        self.circuit_breaker_reason: str = ""

    def update_market_prices(self, bid: float, ask: float):
        total_floating = 0.0
        positions_to_close: list[tuple[Position, str, float]] = []

        for pos in self.open_positions:
            pos.update_price(bid, ask)
            total_floating += pos.floating_pnl

            # Check Stop Loss & Take Profit hit
            if pos.side == "BUY":
                if pos.current_price <= pos.sl_price:
                    positions_to_close.append((pos, "Stop Loss Hit", pos.current_price))
                elif pos.current_price >= pos.tp_price:
                    positions_to_close.append((pos, "Take Profit Hit", pos.current_price))
            else:  # SELL
                if pos.current_price >= pos.sl_price:
                    positions_to_close.append((pos, "Stop Loss Hit", pos.current_price))
                elif pos.current_price <= pos.tp_price:
                    positions_to_close.append((pos, "Take Profit Hit", pos.current_price))

        for pos, reason, exit_price in positions_to_close:
            self.close_position(pos.id, exit_price, reason)

        self.equity = round(self.balance + total_floating, 2)
        self.free_margin = max(0.0, round(self.equity - self.margin, 2))
        
        # Check Daily Circuit Breaker (loss from day's start)
        daily_loss_pct = ((self.daily_start_equity - self.equity) / self.daily_start_equity) * 100.0
        if daily_loss_pct >= self.max_daily_drawdown_pct and not self.circuit_breaker_tripped:
            self.circuit_breaker_tripped = True
            self.circuit_breaker_reason = f"Daily loss reached {round(daily_loss_pct, 2)}% (limit: {self.max_daily_drawdown_pct}%). Trading paused until UTC midnight."
            logger.warning(f"CIRCUIT BREAKER ACTIVATED: {self.circuit_breaker_reason}")
            # Emergency flatten open positions to lock in capital
            self.close_all_positions(bid if pos.side == 'BUY' else ask, "Circuit Breaker Emergency Exit")

    def open_position(
        self,
        symbol: str,
        side: str,
        lot: float,
        entry_price: float,
        sl_price: float,
        tp_price: float,
        reason: str
    ) -> Position | None:
        if self.circuit_breaker_tripped:
            logger.warning("Rejected order: Circuit breaker active.")
            return None

        if len(self.open_positions) >= 1:
            logger.info("Rejected order: Max concurrent position reached (1).")
            return None

        # Exness 1:200 leverage on XAUUSD margin requirement for 0.01 lot is approx $13.25
        est_margin = round((lot * 100.0 * entry_price) / 200.0, 2)
        if self.free_margin < est_margin:
            logger.warning(f"Rejected order: Insufficient free margin. Need ${est_margin}, have ${self.free_margin}")
            return None

        pos = Position(
            symbol=symbol,
            side=side,
            lot=lot,
            entry_price=entry_price,
            sl_price=sl_price,
            tp_price=tp_price,
            reason=reason
        )
        self.open_positions.append(pos)
        self.margin = est_margin
        self.free_margin = max(0.0, round(self.equity - self.margin, 2))
        logger.info(f"Opened {side} {lot} lot {symbol} at {entry_price}. SL: {sl_price}, TP: {tp_price}")
        return pos

    def close_position(self, pos_id: str, exit_price: float, reason: str) -> TradeRecord | None:
        target_pos = None
        for pos in self.open_positions:
            if pos.id == pos_id:
                target_pos = pos
                break

        if not target_pos:
            return None

        self.open_positions.remove(target_pos)
        
        # Calculate realized PnL
        if target_pos.side == "BUY":
            diff = exit_price - target_pos.entry_price
        else:
            diff = target_pos.entry_price - exit_price

        realized_pnl = round(diff * target_pos.lot * 100.0, 2)
        self.balance = round(self.balance + realized_pnl, 2)
        self.equity = self.balance
        self.margin = 0.0
        self.free_margin = self.balance

        record = TradeRecord(
            id=target_pos.id,
            symbol=target_pos.symbol,
            side=target_pos.side,
            lot=target_pos.lot,
            entry_price=target_pos.entry_price,
            exit_price=exit_price,
            pnl=realized_pnl,
            open_time=target_pos.open_time,
            close_time=time.time(),
            close_reason=reason
        )
        self.closed_trades.append(record)
        logger.info(f"Closed {record.side} {record.id}: PnL=${realized_pnl} ({reason})")
        return record

    def close_all_positions(self, current_price: float, reason: str):
        pos_ids = [p.id for p in self.open_positions]
        for pid in pos_ids:
            self.close_position(pid, current_price, reason)

    def get_summary(self) -> dict[str, Any]:
        wins = [t for t in self.closed_trades if t.pnl > 0]
        losses = [t for t in self.closed_trades if t.pnl <= 0]
        win_rate = round((len(wins) / len(self.closed_trades)) * 100.0, 1) if self.closed_trades else 0.0
        
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (round(gross_profit, 2) if gross_profit > 0 else 1.0)
        
        daily_pnl = round(self.equity - self.daily_start_equity, 2)
        daily_pnl_pct = round((daily_pnl / self.daily_start_equity) * 100.0, 2) if self.daily_start_equity > 0 else 0.0

        return {
            "balance": self.balance,
            "equity": self.equity,
            "margin": self.margin,
            "free_margin": self.free_margin,
            "daily_pnl": daily_pnl,
            "daily_pnl_pct": daily_pnl_pct,
            "circuit_breaker_tripped": self.circuit_breaker_tripped,
            "circuit_breaker_reason": self.circuit_breaker_reason,
            "open_positions": [p.to_dict() for p in self.open_positions],
            "total_trades": len(self.closed_trades),
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "recent_trades": [t.to_dict() for t in reversed(self.closed_trades)][:10]
        }

virtual_broker = VirtualBrokerService()
