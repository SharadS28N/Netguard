# backend/scripts/run_full_pipeline.py

import time
from services.phase1_scanner import Phase1Scanner
from services.phase2_feature_extractor import Phase2FeatureExtractor
from services.phase3_anomaly_engine import Phase3AnomalyEngine
from services.phase4_decision_engine import Phase4DecisionEngine

def main():
    print("[PIPELINE] Starting full NetGuard pipeline")

    # Phase 1
    scanner = Phase1Scanner()
    scanner.start()
    print("[PIPELINE] Phase 1 running (60 seconds)")
    time.sleep(60)
    scanner.stop()

    # Phase 2
    print("[PIPELINE] Phase 2: Feature extraction")
    Phase2FeatureExtractor().run()

    # Phase 3
    print("[PIPELINE] Phase 3: Anomaly detection")
    Phase3AnomalyEngine().run()

    # Phase 4
    print("[PIPELINE] Phase 4: Decision engine")
    Phase4DecisionEngine().run()

    print("[PIPELINE] Pipeline complete")

if __name__ == "__main__":
    main()
