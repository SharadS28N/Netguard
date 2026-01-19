"""
Test script for Phase 4 Decision Engine
Validates logic without requiring MongoDB data
"""

from services.phase4_decision_engine import Phase4DecisionEngine

def test_layer_scores():
    """Test layer score computation"""
    engine = Phase4DecisionEngine()
    
    # Sample signals from Phase 3
    test_signals = [
        {
            "layer": "signature",
            "signals": {
                "ssid_reuse": True,
                "encryption_weak": True,
                "vendor_mismatch": False,
                "channel_instability": False
            }
        },
        {
            "layer": "behavior",
            "signals": {
                "signal_variance_high": True,
                "client_spike": False,
                "unstable_presence": True
            }
        },
        {
            "layer": "ml",
            "is_outlier": True,
            "anomaly_score": -0.23
        }
    ]
    
    scores = engine.compute_layer_scores(test_signals)
    print("Layer Scores:")
    print(f"  Signature: {scores['signature']:.4f}")
    print(f"  Behavior: {scores['behavior']:.4f}")
    print(f"  ML: {scores['ml']:.4f}")
    
    # Expected:
    # Signature: 2/4 = 0.5
    # Behavior: 2/3 = 0.667
    # ML: 1.0
    
    assert 0.49 < scores['signature'] < 0.51, f"Signature score incorrect: {scores['signature']}"
    assert 0.66 < scores['behavior'] < 0.68, f"Behavior score incorrect: {scores['behavior']}"
    assert scores['ml'] == 1.0, f"ML score incorrect: {scores['ml']}"
    
    print("✅ Layer scores correct!\n")
    return scores

def test_confidence_computation():
    """Test weighted confidence formula"""
    engine = Phase4DecisionEngine()
    
    layer_scores = {
        "signature": 0.5,
        "behavior": 0.667,
        "ml": 1.0
    }
    
    confidence = engine.compute_confidence(layer_scores)
    print(f"Confidence Score: {confidence:.4f}")
    
    # Expected: (0.5 × 0.4) + (0.667 × 0.3) + (1.0 × 0.3)
    #         = 0.2 + 0.2001 + 0.3 = 0.7001
    expected = 0.7001
    
    assert abs(confidence - expected) < 0.01, f"Confidence incorrect: {confidence}"
    print("✅ Confidence computation correct!\n")
    return confidence

def test_verdict_mapping():
    """Test verdict determination"""
    engine = Phase4DecisionEngine()
    
    test_cases = [
        (0.2, "benign"),
        (0.45, "suspicious"),
        (0.7, "likely_evil_twin"),
        (0.9, "confirmed_evil_twin")
    ]
    
    print("Verdict Mapping:")
    for confidence, expected_verdict in test_cases:
        verdict = engine.determine_verdict(confidence)
        print(f"  Confidence {confidence:.2f} → {verdict}")
        assert verdict == expected_verdict, f"Verdict incorrect for {confidence}"
    
    print("✅ Verdict mapping correct!\n")

def test_explanation_generation():
    """Test explanation generation"""
    engine = Phase4DecisionEngine()
    
    test_signals = [
        {
            "layer": "signature",
            "signals": {
                "ssid_reuse": True,
                "encryption_weak": True,
                "vendor_mismatch": False,
                "channel_instability": False
            }
        },
        {
            "layer": "behavior",
            "signals": {
                "signal_variance_high": True,
                "client_spike": False,
                "unstable_presence": False
            }
        },
        {
            "layer": "ml",
            "is_outlier": True
        }
    ]
    
    explanations = engine.generate_explanation(test_signals)
    print("Generated Explanations:")
    for exp in explanations:
        print(f"  - {exp}")
    
    # Should have 4 explanations
    assert len(explanations) == 4, f"Expected 4 explanations, got {len(explanations)}"
    assert "SSID reused across multiple BSSIDs" in explanations
    assert "Weak or no encryption detected" in explanations
    assert "Unstable signal behavior observed" in explanations
    assert "ML model flagged this AP as anomalous" in explanations
    
    print("✅ Explanation generation correct!\n")

def test_full_decision():
    """Test complete decision-making flow"""
    engine = Phase4DecisionEngine()
    
    network_key = ("FreeWiFi", "aa:bb:cc:dd:ee:ff")
    test_signals = [
        {
            "layer": "signature",
            "signals": {
                "ssid_reuse": True,
                "encryption_weak": True,
                "vendor_mismatch": False,
                "channel_instability": False
            }
        },
        {
            "layer": "behavior",
            "signals": {
                "signal_variance_high": True,
                "client_spike": False,
                "unstable_presence": True
            }
        },
        {
            "layer": "ml",
            "is_outlier": True,
            "anomaly_score": -0.23
        }
    ]
    
    decision = engine.make_decision(network_key, test_signals)
    
    print("Full Decision Output:")
    print(f"  SSID: {decision['ssid']}")
    print(f"  BSSID: {decision['bssid']}")
    print(f"  Verdict: {decision['verdict']}")
    print(f"  Confidence: {decision['confidence']:.4f}")
    print(f"  Threat Level: {decision['threat_level']}")
    print(f"  Explanations: {len(decision['explanation'])} reasons")
    
    # Validate structure
    assert decision['ssid'] == "FreeWiFi"
    assert decision['bssid'] == "aa:bb:cc:dd:ee:ff"
    assert decision['verdict'] == "likely_evil_twin"  # confidence ~0.70
    assert decision['threat_level'] == "high"
    assert len(decision['explanation']) > 0
    assert 'layer_scores' in decision
    assert 'timestamp' in decision
    
    print("✅ Full decision flow correct!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4 Decision Engine - Validation Tests")
    print("=" * 60)
    print()
    
    try:
        test_layer_scores()
        test_confidence_computation()
        test_verdict_mapping()
        test_explanation_generation()
        test_full_decision()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED - Phase 4 logic is CORRECT!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
