import logging
from typing import Any

logger = logging.getLogger(__name__)

class MT5GatewayService:
    def __init__(self):
        self.is_connected: bool = False
        self.account_id: int | None = None
        self.broker_server: str = "Exness-MT5Real"
        self.mode: str = "PAPER"  # "PAPER" or "MT5_LIVE"
        self._mt5 = None
        
        try:
            import MetaTrader5 as mt5
            self._mt5 = mt5
        except ImportError:
            self._mt5 = None
            logger.info("MetaTrader5 python package not loaded. Operating in Virtual Paper Engine mode.")

    def initialize(self, login: int | None = None, password: str | None = None, server: str = "Exness-MT5Real") -> bool:
        if not self._mt5:
            logger.warning("MT5 Python package not available. Install via 'pip install MetaTrader5'.")
            return False

        if login and password:
            authorized = self._mt5.initialize(login=login, password=password, server=server)
        else:
            authorized = self._mt5.initialize()

        if authorized:
            self.is_connected = True
            self.broker_server = server
            acc = self._mt5.account_info()
            if acc:
                self.account_id = acc.login
                logger.info(f"Connected to MT5 Server: {server}, Account: {self.account_id}, Balance: ${acc.balance}")
            return True
        else:
            err = self._mt5.last_error()
            logger.error(f"MT5 Initialization failed: {err}")
            self.is_connected = False
            return False

    def send_order(
        self,
        symbol: str,
        order_type: str,  # "BUY" or "SELL"
        lot: float,
        sl_price: float,
        tp_price: float,
        comment: str = "QuantGold OS"
    ) -> dict[str, Any] | None:
        if self.mode != "MT5_LIVE" or not self.is_connected or not self._mt5:
            logger.info(f"[GATEWAY] Simulating order dispatch in PAPER mode: {order_type} {lot}L on {symbol}")
            return {"status": "SIMULATED", "symbol": symbol, "side": order_type, "lot": lot}

        # Live Execution via MetaTrader5 C-API
        symbol_info = self._mt5.symbol_info_tick(symbol)
        if not symbol_info:
            logger.error(f"Failed to get live tick for {symbol}")
            return None

        price = symbol_info.ask if order_type == "BUY" else symbol_info.bid
        action_type = self._mt5.ORDER_TYPE_BUY if order_type == "BUY" else self._mt5.ORDER_TYPE_SELL

        request = {
            "action": self._mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),
            "type": action_type,
            "price": price,
            "sl": float(sl_price),
            "tp": float(tp_price),
            "deviation": 20,  # 20 points slippage tolerance
            "magic": 20261020,
            "comment": comment,
            "type_time": self._mt5.ORDER_TIME_GTC,
            "type_filling": self._mt5.ORDER_FILLING_IOC,
        }

        result = self._mt5.order_send(request)
        if result and result.retcode == self._mt5.TRADE_RETCODE_DONE:
            logger.info(f"MT5 LIVE ORDER FILLED: Ticket #{result.order}, Volume: {result.volume}")
            return {
                "status": "FILLED",
                "ticket": result.order,
                "volume": result.volume,
                "price": result.price
            }
        else:
            err_msg = result.comment if result else str(self._mt5.last_error())
            logger.error(f"MT5 Live Order Failed: {err_msg}")
            return {"status": "FAILED", "error": err_msg}

    def close_all_positions(self, symbol: str = "XAUUSD") -> int:
        if not self.is_connected or not self._mt5:
            return 0

        positions = self._mt5.positions_get(symbol=symbol)
        if not positions:
            return 0

        closed_count = 0
        for pos in positions:
            tick = self._mt5.symbol_info_tick(symbol)
            close_price = tick.bid if pos.type == self._mt5.ORDER_TYPE_BUY else tick.ask
            close_type = self._mt5.ORDER_TYPE_SELL if pos.type == self._mt5.ORDER_TYPE_BUY else self._mt5.ORDER_TYPE_BUY

            req = {
                "action": self._mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "deviation": 30,
                "magic": 20261020,
                "comment": "QuantGold Emergency Close",
                "type_time": self._mt5.ORDER_TIME_GTC,
                "type_filling": self._mt5.ORDER_FILLING_IOC,
            }
            res = self._mt5.order_send(req)
            if res and res.retcode == self._mt5.TRADE_RETCODE_DONE:
                closed_count += 1

        return closed_count

mt5_gateway = MT5GatewayService()
