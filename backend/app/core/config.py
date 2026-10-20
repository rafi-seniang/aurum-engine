import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "aurum-engine"
    app_version: str = "1.0.0"
    symbol: str = "XAUUSD"
    
    # Risk Parameters
    initial_balance: float = 100.0  # US$100 default as Jibran requested
    risk_percent_per_trade: float = 0.5  # 0.5% risk default
    max_daily_drawdown_percent: float = 2.0  # Circuit breaker threshold
    max_open_positions: int = 1
    
    # Broker Cost Simulation (Exness Pro standards)
    simulated_spread_points: int = 15  # 15 points = $0.15 on Gold
    simulated_slippage_points: int = 2  # 2 points
    
    # News Blackout Window (Minutes)
    blackout_minutes_before: int = 15
    blackout_minutes_after: int = 30
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]

settings = Settings()
