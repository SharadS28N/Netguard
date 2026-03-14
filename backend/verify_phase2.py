import os

from dotenv import load_dotenv
from models.database import Database
from services.phase2_feature_extractor import Phase2FeatureExtractor

# Load environment
load_dotenv()

# Connect DB
Database.connect()

# Run Phase 2
print("Running Phase 2 Feature Extraction...")
extractor = Phase2FeatureExtractor()
extractor.run()
print("Phase 2 Execution Complete.")

# Verify Findings
db = Database.get_db()
count = db.features_baseline.count_documents({})
print(f"Features Baseline Document Count: {count}")

if count > 0:
    sample = db.features_baseline.find_one()
    print("Sample Feature Vector:")
    print(sample)
else:
    print("No features generated. Did you run Phase 1 first?")
