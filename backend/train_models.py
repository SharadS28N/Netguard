"""
Netguard — Complete Training & Detection Pipeline
---
Orchestrates the full ML + detection pipeline:
1. Train ML models (research-informed data)
2. Phase 1: WiFi Scanning (Windows netsh / cross-platform)
3. Phase 2: Feature Extraction & Baseline Building
4. Phase 3: Anomaly Detection (Signature + Behavior + ML)
5. Phase 4: Decision Engine (Final verdicts)
"""

import os
import sys
import time
import logging

from dotenv import load_dotenv

logger = logging.getLogger("netguard.pipeline")


def train_models(model_dir: str = "./models") -> bool:
    """
    Train ML models using research-informed synthetic data.

    Returns:
        True if training succeeded
    """
    from services.ml_trainer import MLTrainer

    logger.info("=" * 60)
    logger.info("STEP 1: ML Model Training")
    logger.info("=" * 60)

    try:
        trainer = MLTrainer(model_dir=model_dir)
        results = trainer.train_full_pipeline(num_samples=3000)

        # Log results with safety
        models_data = results.get("models", {})
        for model_type, model_data in models_data.items():
            metrics = model_data.get("metrics", {})
            logger.info(
                "  %s — Acc: %.4f  Prec: %.4f  Rec: %.4f  F1: %.4f",
                model_type.upper(),
                metrics.get("accuracy", 0),
                metrics.get("precision", 0),
                metrics.get("recall", 0),
                metrics.get("f1", 0),
            )

        cv = results.get("cross_validation", {})
        logger.info(
            "  Cross-validation: %.4f ± %.4f",
            cv.get("mean_accuracy", 0), cv.get("std", 0),
        )

        logger.info("Models saved to %s", model_dir)
        return True

    except Exception as exc:
        logger.error("Training failed: %s", exc, exc_info=True)
        return False


def run_detection_pipeline(scan_duration: int = 3) -> bool:
    """
    Run the complete 4-phase detection pipeline.

    Args:
        scan_duration: How long to scan for WiFi networks (seconds)

    Returns:
        True if pipeline completed successfully
    """
    from services.phase1_scanner import Phase1Scanner
    from services.phase2_feature_extractor import Phase2FeatureExtractor
    from services.phase3_anomaly_engine import Phase3AnomalyEngine
    from services.phase4_decision_engine import Phase4DecisionEngine

    try:
        # Phase 1: WiFi Scanning
        logger.info("Phase 1: WiFi Network Scanning (%ds)...", scan_duration)
        scanner = Phase1Scanner(interval=scan_duration)
        scanner.start()
        time.sleep(scan_duration + 1)
        scanner.stop()
        logger.info("Phase 1: Complete")

        # Phase 2: Feature Extraction
        logger.info("Phase 2: Feature Extraction & Baseline...")
        Phase2FeatureExtractor().run()
        logger.info("Phase 2: Complete")

        # Phase 3: Anomaly Detection
        logger.info("Phase 3: Anomaly Detection...")
        Phase3AnomalyEngine().run()
        logger.info("Phase 3: Complete")

        # Phase 4: Decision Engine
        logger.info("Phase 4: Decision & Confidence Engine...")
        Phase4DecisionEngine().run()
        logger.info("Phase 4: Complete")

        return True

    except Exception as exc:
        logger.error("Detection pipeline failed: %s", exc, exc_info=True)
        return False


def main():
    """Main entry point for standalone execution."""
    load_dotenv()

    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    from models.database import Database

    logger.info("=" * 60)
    logger.info("  Netguard — Training & Detection Pipeline")
    logger.info("=" * 60)

    # Connect to database
    logger.info("Connecting to MongoDB...")
    if not Database.connect():
        logger.error("Could not connect to MongoDB. Check .env MONGODB_URI")
        sys.exit(1)

    logger.info("MongoDB connected")

    # Step 1: Train Models
    if not train_models():
        logger.error("Pipeline aborted: training failed")
        Database.disconnect()
        sys.exit(1)

    # Step 2: Run Detection Pipeline
    if not run_detection_pipeline(scan_duration=5):
        logger.error("Pipeline aborted: detection failed")
        Database.disconnect()
        sys.exit(1)

    # Done
    logger.info("=" * 60)
    logger.info("Pipeline complete!")
    logger.info("  - raw_scans: Raw WiFi data")
    logger.info("  - features_baseline: Network profiles")
    logger.info("  - anomaly_signals: Suspicious signals")
    logger.info("  - threats: Final verdicts")
    logger.info("  - detection_logs: Audit trail")
    logger.info("=" * 60)

    Database.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
