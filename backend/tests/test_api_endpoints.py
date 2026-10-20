import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_status_endpoint():
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "market" in data
    assert "news" in data
    assert "broker" in data

def test_api_candles_endpoint():
    resp = client.get("/api/candles")
    assert resp.status_code == 200
    data = resp.json()
    assert "symbol" in data
    assert "candles" in data

def test_api_pause_and_resume():
    r_pause = client.post("/api/control/pause")
    assert r_pause.status_code == 200
    assert r_pause.json()["status"] == "PAUSED"

    r_resume = client.post("/api/control/resume")
    assert r_resume.status_code == 200
    assert r_resume.json()["status"] in ["ACTIVE", "NEWS_BLACKOUT", "CIRCUIT_BREAKER"]

def test_api_emergency_flatten():
    r_flatten = client.post("/api/control/emergency-flatten")
    assert r_flatten.status_code == 200
    assert r_flatten.json()["status"] == "EMERGENCY_STOP"

def test_api_reset_demo():
    r_reset = client.post("/api/control/reset-demo")
    assert r_reset.status_code == 200
    assert r_reset.json()["success"] is True
