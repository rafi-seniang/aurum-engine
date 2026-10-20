import time
from app.services.news_calendar import NewsCalendarService, NewsEvent

def test_news_event_timestamp_parsing():
    ev = NewsEvent(
        title="US CPI Inflation",
        country="USD",
        date_str="2026-10-22T08:30:00-04:00",
        impact="High"
    )
    assert ev.timestamp > 0
    assert ev.impact == "High"

def test_blackout_window_detection():
    service = NewsCalendarService()
    now = time.time()
    
    # Event happening in 5 minutes (within the 15-minute before window)
    event_soon = NewsEvent("Fed Interest Rate Decision", "USD", "", "High")
    event_soon.timestamp = now + 300
    service.events = [event_soon]
    
    service.evaluate_blackout_status(before_minutes=15, after_minutes=30)
    assert service.is_blackout is True
    assert "Fed Interest Rate Decision" in service.blackout_reason
    assert service.blackout_remaining_seconds > 0

def test_safe_corridor_when_no_nearby_news():
    service = NewsCalendarService()
    now = time.time()
    
    # Event happening tomorrow (outside window)
    event_far = NewsEvent("Retail Sales", "USD", "", "Medium")
    event_far.timestamp = now + 86400
    service.events = [event_far]
    
    service.evaluate_blackout_status(before_minutes=15, after_minutes=30)
    assert service.is_blackout is False
    assert service.next_event is not None
    assert service.seconds_until_next_event > 80000
