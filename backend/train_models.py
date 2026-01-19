#!/usr/bin/env python3
"""
Model training script for NetGuard Nepal Evil Twin Detection System
This script trains the ML models using synthetic data and saves them to disk
"""

import os
import sys
from datetime import datetime
from services.ml_trainer import MLTrainer
from models.database import Database
from dotenv import load_dotenv

def main():
    """Main training function"""
    print("=" * 80)
    print("NetGuard Nepal - ML Model Training Pipeline")
    print("=" * 80)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Connect to database
    print("Connecting to MongoDB...")
    if not Database.connect():
        print("ERROR: Could not connect to MongoDB")
        print("Make sure MongoDB is running and MONGODB_URI is set correctly")
        sys.exit(1)
    
    print("✓ Connected to MongoDB\n")
    
    # Initialize trainer
    print("Initializing ML Trainer...")
    trainer = MLTrainer(model_dir="./models")
    print("✓ Trainer initialized\n")
    
    # Start training
    print("Starting model training pipeline...")
    print("-" * 80)
    
    try:
        results = trainer.train_full_pipeline()
        
        print("-" * 80)
        print("\nTraining completed successfully!\n")
        
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
        print("✓ Ready for inference!")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Training failed!")
        print(f"Details: {str(e)}")
        return 1
    
    finally:
        Database.disconnect()

if __name__ == "__main__":
    sys.exit(main())
