#!/usr/bin/env python3
"""
NetGuard Nepal - Complete Training & Detection Pipeline
This script:
1. Trains ML models using synthetic data
2. Runs Phase 1: WiFi Scanning
3. Runs Phase 2: Feature Extraction
4. Runs Phase 3: Anomaly Detection
5. Runs Phase 4: Decision Engine
"""

import os
import sys
import time
from datetime import datetime
from services.ml_trainer import MLTrainer
from services.phase1_scanner import Phase1Scanner
from services.phase2_feature_extractor import Phase2FeatureExtractor
from services.phase3_anomaly_engine import Phase3AnomalyEngine
from services.phase4_decision_engine import Phase4DecisionEngine
from models.database import Database
from dotenv import load_dotenv

def train_models():
    """Train ML models"""
    print("=" * 80)
    print("STEP 1: ML Model Training")
    print("=" * 80)
    print()
    
    # Initialize trainer
    print("Initializing ML Trainer...")
    trainer = MLTrainer(model_dir="./models")
    print("✓ Trainer initialized\n")
    
    # Start training
    print("Starting model training...")
    print("-" * 80)
    
    try:
        results = trainer.train_full_pipeline()
        
        print("-" * 80)
        print("\n✓ Training completed successfully!\n")
        
        # Display results
        print("Training Results:")
        print(f"  Timestamp: {results['timestamp']}")
        print(f"  Training Samples: {results['training_samples']}")
        print(f"  Test Samples: {results['test_samples']}")
        print()
        
        for model_type, model_data in results['models'].items():
            print(f"{model_type.upper()} Model:")
            metrics = model_data.get('metrics', {})
            print(f"  ├─ Accuracy:  {metrics.get('accuracy', 0):.4f}")
            print(f"  ├─ Precision: {metrics.get('precision', 0):.4f}")
            print(f"  ├─ Recall:    {metrics.get('recall', 0):.4f}")
            print(f"  ├─ F1-Score:  {metrics.get('f1_score', 0):.4f}")
            print(f"  └─ Path: {model_data.get('path', 'N/A')}")
            
            if model_data.get('feature_importance'):
                print(f"\n  Top Features:")
                features = model_data['feature_importance']
                sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)[:3]
                for feat, importance in sorted_features:
                    print(f"    ├─ {feat}: {importance:.4f}")
            print()
        
        print("=" * 80)
        print("✓ Models saved to ./models/ directory")
        print("=" * 80)
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Training failed!")
        print(f"Details: {str(e)}")
        return False

def run_detection_pipeline():
    """Run the complete 4-phase detection pipeline"""
    print("=" * 80)
    print("STEP 2: Running Detection Pipeline")
    print("=" * 80)
    print()
    
    try:
        # Phase 1: WiFi Scanning
        print("=" * 80)
        print("Phase 1: WiFi Network Scanning")
        print("=" * 80)
        scanner = Phase1Scanner()
        scanner.start()
        print("⏳ Scanning for 10 seconds...")
        time.sleep(10)  # Scan for 10 seconds (reduced from 60 for faster testing)
        scanner.stop()
        print("✓ Phase 1 Complete\n")
        
        # Phase 2: Feature Extraction
        print("=" * 80)
        print("Phase 2: Feature Extraction & Baseline Building")
        print("=" * 80)
        Phase2FeatureExtractor().run()
        print("✓ Phase 2 Complete\n")
        
        # Phase 3: Anomaly Detection
        print("=" * 80)
        print("Phase 3: Anomaly Detection")
        print("=" * 80)
        Phase3AnomalyEngine().run()
        print("✓ Phase 3 Complete\n")
        
        # Phase 4: Decision Engine
        print("=" * 80)
        print("Phase 4: Decision & Confidence Engine")
        print("=" * 80)
        Phase4DecisionEngine().run()
        print("✓ Phase 4 Complete\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Pipeline failed!")
        print(f"Details: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    print("\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  NetGuard Nepal - Complete Training & Detection Pipeline".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    print("\n")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to database
    print("Connecting to MongoDB...")
    if not Database.connect():
        print("❌ ERROR: Could not connect to MongoDB")
        print("Make sure MongoDB is running and MONGODB_URI is set correctly")
        sys.exit(1)
    
    print("✓ Connected to MongoDB\n")
    
    # Step 1: Train Models
    if not train_models():
        print("\n❌ Pipeline aborted due to training failure")
        Database.disconnect()
        sys.exit(1)
    
    # Step 2: Run Detection Pipeline
    if not run_detection_pipeline():
        print("\n❌ Pipeline aborted due to detection failure")
        Database.disconnect()
        sys.exit(1)
    
    # Success!
    print("=" * 80)
    print(" PIPELINE COMPLETE!")
    print("=" * 80)
    print()
    print("✅ ML models trained and saved")
    print("✅ WiFi networks scanned")
    print("✅ Behavioral baselines created")
    print("✅ Anomalies detected")
    print("✅ Threat decisions made")
    print()
    print("📊 Check MongoDB Compass:")
    print("   - raw_scans: Raw WiFi data")
    print("   - features_baseline: Network profiles")
    print("   - anomaly_signals: Suspicious signals")
    print("   - threats: Final verdicts (PASS/FAIL)")
    print("   - detection_logs: Audit trail")
    print()
    print("=" * 80)
    
    Database.disconnect()
    return 0

if __name__ == "__main__":
    sys.exit(main())
