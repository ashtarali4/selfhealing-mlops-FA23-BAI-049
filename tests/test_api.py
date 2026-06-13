"""
Unit tests for the Sentiment Analysis API.
Run with: pytest tests/test_api.py -v
"""

import os
import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://98.82.242.170:32500")


def test_health_endpoint():
    """GET /health -> HTTP 200; 'status':'healthy' and key 'model_version' present."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("status") == "healthy", f"Expected 'healthy', got {data.get('status')}"
    assert "model_version" in data, "Key 'model_version' not found in response"


def test_predict_returns_label_and_confidence():
    """POST /predict -> HTTP 200; label in [POSITIVE, NEGATIVE]; 0<=confidence<=1; 'model_version' present."""
    payload = {"text": "The food was absolutely delicious and the chef clearly has exceptional skill"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("label") in ["POSITIVE", "NEGATIVE"], \
        f"Label must be POSITIVE or NEGATIVE, got {data.get('label')}"
    confidence = data.get("confidence")
    assert confidence is not None, "confidence key missing from response"
    assert 0 <= confidence <= 1, f"Confidence must be between 0 and 1, got {confidence}"
    assert "model_version" in data, "Key 'model_version' not found in response"


def test_predict_negative_text():
    """POST /predict with negative text -> HTTP 200."""
    payload = {"text": "This is terrible, horrible and absolutely dreadful"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "label" in data, "label key missing from response"
    assert "confidence" in data, "confidence key missing from response"


def test_health_returns_model_version_unstable():
    """GET /health -> model_version == 'unstable-v1' exactly."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("model_version") == "unstable-v1", \
        f"Expected 'unstable-v1', got {data.get('model_version')}"
