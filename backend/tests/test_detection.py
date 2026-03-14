"""Tests for the detection pipeline components."""


def test_evil_twin_detector_import():
    """Test that EvilTwinDetector imports without error (rule_engine exists now)."""
    from services.evil_twin_detector import EvilTwinDetector

    detector = EvilTwinDetector()
    assert detector is not None


def test_evil_twin_detector_empty():
    """Test detector with empty network list."""
    from services.evil_twin_detector import EvilTwinDetector

    detector = EvilTwinDetector()
    result = detector.detect([])

    assert result["networks_scanned"] == 0
    assert result["threat_level"] == "safe"


def test_evil_twin_detector_with_networks(mock_networks):
    """Test detector with mock networks including evil twin."""
    from services.evil_twin_detector import EvilTwinDetector

    detector = EvilTwinDetector()
    result = detector.detect(mock_networks)

    assert result["networks_scanned"] == 3
    assert result["threat_level"] in ("safe", "suspicious", "danger")


def test_feature_extractor():
    """Test feature extraction."""
    from services.feature_extractor import FeatureExtractor

    extractor = FeatureExtractor()
    networks = [
        {
            "ssid": "Test", "bssid": "AA:BB:CC:DD:EE:FF",
            "signal_strength": -45, "channel": 6, "encryption": "WPA2",
            "vendor": "TP-Link", "is_hidden": False, "frequency": 2437,
        },
    ]

    features = extractor.extract_features_batch(networks)
    assert features.shape == (1, 10)


def test_ml_inference():
    """Test ML inference engine initialization."""
    from services.ml_inference import MLInference

    engine = MLInference()
    info = engine.get_model_info()

    assert "models_loaded" in info
    assert "models_directory" in info
