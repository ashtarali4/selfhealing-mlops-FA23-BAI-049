"""
Custom Prometheus Exporter for Sentiment API
Polls /api/latest-confidence every 5s and exposes prediction_confidence_score on port 8000
"""

import time
import requests
from prometheus_client import start_http_server, Gauge

# ── Config ──────────────────────────────────────────────────────────────────
APP_URL       = "http://98.82.242.170:32500/api/latest-confidence"
POLL_INTERVAL = 5       # seconds
EXPORTER_PORT = 8000
DEFAULT_CONF  = 1.0     # returned when endpoint is unreachable

# ── Prometheus Metric ────────────────────────────────────────────────────────
prediction_confidence_score = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from the Sentiment API'
)

def poll_confidence():
    """Fetch the latest confidence value from the app and update the gauge."""
    try:
        response = requests.get(APP_URL, timeout=4)
        response.raise_for_status()
        data = response.json()
        confidence = float(data.get("confidence", DEFAULT_CONF))
    except Exception as e:
        print(f"[WARN] Could not reach {APP_URL}: {e}. Using default {DEFAULT_CONF}")
        confidence = DEFAULT_CONF

    prediction_confidence_score.set(confidence)
    print(f"[INFO] prediction_confidence_score = {confidence}")

if __name__ == "__main__":
    print(f"[INFO] Starting exporter on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)

    while True:
        poll_confidence()
        time.sleep(POLL_INTERVAL)
