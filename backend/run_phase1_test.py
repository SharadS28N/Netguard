from services.phase1_scanner import Phase1Scanner
from models.database import Database
import time
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Connect DB
Database.connect()

print("Running Phase 1 Scanner for 30 seconds...")
scanner = Phase1Scanner(interval=5)
scanner.start()

# Let it run
try:
    for i in range(6):
        print(f"Scanning... {i*5}s")
        time.sleep(5)
finally:
    scanner.stop()
    print("Scanner stopped.")

# Check count
db = Database.get_db()
count = db.raw_scans.count_documents({})
print(f"Raw Scans Collected: {count}")
