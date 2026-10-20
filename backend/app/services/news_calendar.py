import asyncio
from datetime import datetime, timezone
import logging
import time
from typing import Any
import httpx

logger = logging.getLogger(__name__)

class NewsEvent:
    def __init__(self, title: str, country: str, date_str: str, impact: str, forecast: str = "", previous: str = ""):
        self.title = title
        self.country = country
        self.date_str = date_str
        self.impact = impact
        self.forecast = forecast
        self.previous = previous
        self.timestamp: float = 0
        try:
            # Parse ISO 8601 with timezone (e.g. "2026-10-22T08:30:00-04:00")
            dt = datetime.fromisoformat(date_str)
            self.timestamp = dt.astimezone(timezone.utc).timestamp()
        except Exception:
            self.timestamp = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "country": self.country,
            "date": self.date_str,
            "impact": self.impact,
            "forecast": self.forecast,
            "previous": self.previous,
            "timestamp": self.timestamp
        }

class NewsCalendarService:
    def __init__(self):
        self.events: list[NewsEvent] = []
        self.last_fetch_ts: float = 0
        self.is_blackout: bool = False
        self.blackout_reason: str = ""
        self.blackout_remaining_seconds: int = 0
        self.next_event: dict[str, Any] | None = None
        self.seconds_until_next_event: int = 0
        self._client = httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})

    async def fetch_calendar(self) -> bool:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        try:
            resp = await self._client.get(url)
            if resp.status_code != 200:
                logger.warning(f"News calendar returned HTTP {resp.status_code}")
                return False

            raw_events = resp.json()
            parsed_events: list[NewsEvent] = []
            
            for item in raw_events:
                # We focus on USD currency because Gold (XAUUSD) is predominantly moved by US macro news
                country = item.get("country", "")
                impact = item.get("impact", "")
                if country == "USD" and impact in ["High", "Medium"]:
                    parsed_events.append(NewsEvent(
                        title=item.get("title", ""),
                        country=country,
                        date_str=item.get("date", ""),
                        impact=impact,
                        forecast=item.get("forecast", ""),
                        previous=item.get("previous", "")
                    ))

            # Sort chronologically
            parsed_events.sort(key=lambda x: x.timestamp)
            self.events = parsed_events
            self.last_fetch_ts = time.time()
            self.evaluate_blackout_status()
            return True
        except Exception as e:
            logger.error(f"Error fetching news calendar: {e}")
            return False

    def evaluate_blackout_status(self, before_minutes: int = 15, after_minutes: int = 30):
        now = time.time()
        before_sec = before_minutes * 60
        after_sec = after_minutes * 60
        
        self.is_blackout = False
        self.blackout_reason = ""
        self.blackout_remaining_seconds = 0
        self.next_event = None
        self.seconds_until_next_event = 0

        future_events: list[NewsEvent] = []

        for ev in self.events:
            if ev.timestamp <= 0:
                continue

            event_time = ev.timestamp
            start_window = event_time - before_sec
            end_window = event_time + after_sec

            # Check if current time is inside the blackout window
            if start_window <= now <= end_window:
                self.is_blackout = True
                self.blackout_reason = f"{ev.impact.upper()} Impact News: {ev.title}"
                remaining = int(end_window - now)
                if remaining > self.blackout_remaining_seconds:
                    self.blackout_remaining_seconds = remaining

            if event_time > now:
                future_events.append(ev)

        if future_events:
            nxt = future_events[0]
            self.next_event = nxt.to_dict()
            self.seconds_until_next_event = max(0, int(nxt.timestamp - now))

    def get_summary(self) -> dict[str, Any]:
        return {
            "is_blackout": self.is_blackout,
            "blackout_reason": self.blackout_reason,
            "blackout_remaining_seconds": self.blackout_remaining_seconds,
            "next_event": self.next_event,
            "seconds_until_next_event": self.seconds_until_next_event,
            "total_usd_events_tracked": len(self.events),
            "upcoming_events": [ev.to_dict() for ev in self.events if ev.timestamp > time.time()][:5]
        }

news_calendar = NewsCalendarService()
