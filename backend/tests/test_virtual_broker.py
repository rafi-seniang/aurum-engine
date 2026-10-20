import pytest
from app.services.virtual_broker import VirtualBrokerService

def test_initial_broker_state():
    broker = VirtualBrokerService(initial_balance=100.0, max_daily_drawdown_pct=2.0)
    assert broker.balance == 100.0
    assert broker.equity == 100.0
    assert broker.margin == 0.0
    assert broker.free_margin == 100.0
    assert broker.circuit_breaker_tripped is False

def test_open_position_and_margin():
    broker = VirtualBrokerService(initial_balance=100.0)
    pos = broker.open_position(
        symbol="XAUUSD",
        side="BUY",
        lot=0.01,
        entry_price=2650.0,
        sl_price=2645.0,
        tp_price=2659.0,
        reason="Test breakout"
    )
    assert pos is not None
    assert pos.lot == 0.01
    assert len(broker.open_positions) == 1
    # 0.01 lot XAUUSD margin at 1:200 is approx $13.25
    assert broker.margin > 10.0
    assert broker.free_margin < broker.equity

def test_single_position_limit():
    broker = VirtualBrokerService(initial_balance=100.0)
    p1 = broker.open_position("XAUUSD", "BUY", 0.01, 2650.0, 2645.0, 2660.0, "p1")
    assert p1 is not None
    # Second position should be rejected
    p2 = broker.open_position("XAUUSD", "BUY", 0.01, 2651.0, 2646.0, 2661.0, "p2")
    assert p2 is None
    assert len(broker.open_positions) == 1

def test_floating_pnl_calculation():
    broker = VirtualBrokerService(initial_balance=100.0)
    pos = broker.open_position("XAUUSD", "BUY", 0.01, 2650.0, 2640.0, 2670.0, "test")
    # Gold rises by $2.00 (Bid 2652.00)
    broker.update_market_prices(bid=2652.0, ask=2652.16)
    # 0.01 lot * 100 oz = 1 oz. $2.00 price increase = +$2.00 floating PnL
    assert pos.floating_pnl == 2.0
    assert broker.equity == 102.0

def test_stop_loss_hit():
    broker = VirtualBrokerService(initial_balance=100.0)
    broker.open_position("XAUUSD", "BUY", 0.01, 2650.0, 2645.0, 2660.0, "test")
    # Gold plunges past SL to 2644.00
    broker.update_market_prices(bid=2644.0, ask=2644.16)
    assert len(broker.open_positions) == 0
    assert len(broker.closed_trades) == 1
    trade = broker.closed_trades[0]
    assert trade.pnl < 0
    assert "Stop Loss" in trade.close_reason

def test_circuit_breaker_trigger():
    broker = VirtualBrokerService(initial_balance=100.0, max_daily_drawdown_pct=2.0)
    broker.open_position("XAUUSD", "BUY", 0.01, 2650.0, 2640.0, 2660.0, "test")
    # Drop price so loss exceeds 2% ($2.00 on $100) -> drop price by $2.50
    broker.update_market_prices(bid=2647.50, ask=2647.66)
    assert broker.circuit_breaker_tripped is True
    assert "Daily loss reached" in broker.circuit_breaker_reason
    # Once tripped, new orders are blocked
    p_blocked = broker.open_position("XAUUSD", "BUY", 0.01, 2648.0, 2640.0, 2660.0, "blocked")
    assert p_blocked is None
