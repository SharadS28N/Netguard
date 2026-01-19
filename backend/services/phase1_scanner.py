"""
Phase 1: Passive Baseline Collection
-----------------------------------
This service is responsible ONLY for collecting raw Wi-Fi scan data
using Windows netsh and storing it in MongoDB.

STRICT RULES:
- No ML
- No anomaly detection
- No labeling
- No aggregation
- Append-only storage
"""

import subprocess
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional

from models.database import Database


class Phase1Scanner:
    """
    Phase 1 Scanner
    Runs passive Wi-Fi scans using netsh and stores raw results.
    """

    def __init__(self, interval: int = 20):
        """
        :param interval: Scan interval in seconds
        """
        self.interval = interval
        self.running = False
        self.thread: Optional[threading.Thread] = None

        self.db = Database.get_db()
        self.collection = self.db["raw_scans"]

    # -------------------------
    # Core control methods
    # -------------------------

    def start(self):
        """
        Start the background scanning loop.
        """
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stop the background scanning loop.
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def is_running(self) -> bool:
        """
        Check whether the scanner is running.
        """
        return self.running

    # -------------------------
    # Internal loop
    # -------------------------

    def _scan_loop(self):
        """
        Continuous scanning loop.
        """
        while self.running:
            try:
                raw_output = self.scan()
                parsed_records = self.parse_output(raw_output)

                for record in parsed_records:
                    self.save_scan(record)

            except Exception as e:
                # Phase 1 must NEVER crash the system
                print(f"[Phase1Scanner] Error: {e}")

            time.sleep(self.interval)

    # -------------------------
    # Scanning & parsing
    # -------------------------

    def scan(self) -> str:
        """
        Run netsh command and return raw output as string.
        """
        command = ["netsh", "wlan", "show", "networks", "mode=bssid"]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=False
        )

        return result.stdout

    def parse_output(self, output: str) -> List[Dict]:
        """
        Parse raw netsh output into structured records.

        IMPORTANT:
        - Parsing only
        - No interpretation
        - No scoring
        """
        records: List[Dict] = []
        current_ssid: Optional[str] = None

        lines = output.splitlines()
        timestamp = datetime.utcnow().isoformat()

        for line in lines:
            line = line.strip()

            if line.startswith("SSID"):
                parts = line.split(":", 1)
                current_ssid = parts[1].strip() if len(parts) > 1 else ""

            elif line.startswith("BSSID"):
                # Start a new BSSID record
                parts = line.split(":", 1)
                bssid = parts[1].strip()

                record = {
                    "ssid": current_ssid,
                    "bssid": bssid,
                    "timestamp": timestamp,
                }

                records.append(record)

            elif records:
                # Attach fields to the most recent BSSID
                last = records[-1]

                if line.startswith("Signal"):
                    last["signal"] = line.split(":", 1)[1].strip()

                elif line.startswith("Channel"):
                    last["channel"] = line.split(":", 1)[1].strip()

                elif line.startswith("Band"):
                    last["band"] = line.split(":", 1)[1].strip()

                elif line.startswith("Authentication"):
                    last["authentication"] = line.split(":", 1)[1].strip()

                elif line.startswith("Encryption"):
                    last["encryption"] = line.split(":", 1)[1].strip()

                elif line.startswith("Radio type"):
                    last["radio_type"] = line.split(":", 1)[1].strip()

                elif line.startswith("Connected Stations"):
                    last["connected_stations"] = line.split(":", 1)[1].strip()

                elif line.startswith("Channel Utilization"):
                    last["channel_utilization"] = line.split(":", 1)[1].strip()

        return records

    # -------------------------
    # Persistence
    # -------------------------

    def save_scan(self, data: Dict):
        """+
        Save raw scan record to MongoDB.

        RULE:
        - Insert only
        - Never update
        """
        self.collection.insert_one(data)
