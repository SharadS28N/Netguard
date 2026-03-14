"""
Pytest configuration and fixtures for Netguard tests.
"""

import os
import sys
import pytest

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def app():
    """Create application for testing."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["MONGODB_URI"] = os.environ.get(
        "MONGODB_URI", "mongodb://localhost:27017"
    )
    os.environ["MONGODB_DB"] = "netguard_test"

    from app import create_app
    from config import TestingConfig

    application = create_app(config=TestingConfig())
    yield application


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_networks():
    """Provide sample network data for testing."""
    return [
        {
            "ssid": "TestNet_Legit",
            "bssid": "AA:BB:CC:DD:EE:01",
            "signal_strength": -45,
            "channel": 6,
            "encryption": "WPA2",
            "vendor": "TP-Link",
            "is_hidden": False,
            "frequency": 2437,
        },
        {
            "ssid": "TestNet_Legit",  # Evil twin
            "bssid": "11:22:33:44:55:66",
            "signal_strength": -40,
            "channel": 6,
            "encryption": "Open",
            "vendor": "Unknown",
            "is_hidden": False,
            "frequency": 2437,
        },
        {
            "ssid": "Secure_Office_5G",
            "bssid": "99:88:77:66:55:44",
            "signal_strength": -65,
            "channel": 149,
            "encryption": "WPA3",
            "vendor": "Ubiquiti",
            "is_hidden": False,
            "frequency": 5745,
        },
    ]
