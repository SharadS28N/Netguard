"""Tests for WiFi scanner and detection components."""

import platform


def test_wifi_scanner_init():
    """Test WiFi scanner initializes without error."""
    from services.wifi_scanner import WiFiScanner

    scanner = WiFiScanner()
    assert scanner.scan_method in ("netsh", "nmcli", "iwlist", "airport", "mock")


def test_wifi_scanner_platform():
    """Test scanner detects correct platform."""
    from services.wifi_scanner import WiFiScanner

    scanner = WiFiScanner()
    system = platform.system().lower()

    if system == "windows":
        assert scanner.scan_method in ("netsh", "mock")
    elif system == "linux":
        assert scanner.scan_method in ("nmcli", "iwlist", "mock")


def test_wifi_scanner_scan():
    """Test that scan returns a list of networks."""
    from services.wifi_scanner import WiFiScanner

    scanner = WiFiScanner()
    networks = scanner.scan(duration=2)

    assert isinstance(networks, list)
    assert len(networks) > 0  # At least mock data

    # Verify network structure
    for net in networks:
        assert "ssid" in net
        assert "bssid" in net
        assert "signal_strength" in net
        assert "encryption" in net
        assert "vendor" in net


def test_wifi_scanner_mock_data():
    """Test mock scanner returns valid data."""
    from services.wifi_scanner import WiFiScanner

    scanner = WiFiScanner()
    networks = scanner._scan_mock()

    assert len(networks) >= 4
    # Check for evil twin in mock data
    ssids = [n["ssid"] for n in networks]
    assert ssids.count("Home_Network") >= 2  # Evil twin pair


def test_netsh_parser():
    """Test netsh output parsing."""
    from services.wifi_scanner import WiFiScanner

    scanner = WiFiScanner()

    sample_output = """
SSID 1 : TestNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 85%
         Radio type         : 802.11n
         Band               : 2.4 GHz
         Channel            : 6

SSID 2 : OpenWifi
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : 11:22:33:44:55:66
         Signal             : 45%
         Radio type         : 802.11ac
         Band               : 5 GHz
         Channel            : 36
"""
    networks = scanner._parse_netsh_output(sample_output)

    assert len(networks) == 2
    assert networks[0]["ssid"] == "TestNetwork"
    assert networks[0]["encryption"] == "WPA2"
    assert networks[0]["signal_strength"] == -58  # (85/2)-100
    assert networks[0]["channel"] == 6

    assert networks[1]["ssid"] == "OpenWifi"
    assert networks[1]["encryption"] == "Open"


def test_rule_engine():
    """Test rule engine detection."""
    from services.rule_engine import RuleEngine

    engine = RuleEngine()
    networks = [
        {
            "ssid": "TestNet", "bssid": "AA:BB:CC:DD:EE:FF",
            "signal_strength": -45, "channel": 6,
            "encryption": "WPA2", "vendor": "TP-Link", "is_hidden": False,
        },
        {
            "ssid": "TestNet", "bssid": "11:22:33:44:55:66",
            "signal_strength": -40, "channel": 6,
            "encryption": "Open", "vendor": "Unknown", "is_hidden": False,
        },
    ]

    results = engine.detect(networks)
    assert len(results["evil_twins"]) > 0 or len(results["suspicious_networks"]) > 0
    assert len(results["rule_triggers"]) > 0
    assert results["overall_confidence"] > 0


def test_ml_trainer():
    """Test ML training pipeline."""
    from services.ml_trainer import MLTrainer

    trainer = MLTrainer(model_dir="./models")
    X, y = trainer.generate_training_data(num_samples=200)

    assert X.shape == (200, 8)
    assert y.shape == (200,)
    assert set(y.tolist()).issubset({0, 1})

    # Check class distribution (roughly 75/25)
    legit_ratio = (y == 0).sum() / len(y)
    assert 0.6 < legit_ratio < 0.9
