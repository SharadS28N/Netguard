"""
WiFi Network Scanner — Cross-Platform
---
Scans for WiFi networks using the best available tool:
  Windows: netsh wlan show networks mode=bssid
  Linux:   nmcli dev wifi list
  macOS:   airport -s
  Fallback: Mock data for environments without WiFi adapters
"""

import subprocess
import re
import platform
import logging
from typing import List, Dict
from datetime import datetime, timezone

logger = logging.getLogger("netguard.wifi_scanner")

# ─── OUI Vendor Database ────────────────────────────────────

OUI_VENDORS = {
    "00:05:4E": "Philips", "00:09:5B": "Netgear", "00:0B:85": "Cisco",
    "00:0C:29": "VMware", "00:0D:93": "Apple", "00:0F:B5": "Netgear",
    "00:13:10": "Cisco-Linksys", "00:14:6C": "Netgear", "00:17:C4": "Quanta",
    "00:18:4D": "Netgear", "00:1A:2B": "Ayecom", "00:1B:63": "Apple",
    "00:1E:E5": "Cisco-Linksys", "00:1F:33": "Netgear", "00:22:6B": "Cisco-Linksys",
    "00:23:6C": "Apple", "00:24:B2": "Netgear", "00:25:5A": "Apple",
    "00:26:F2": "Netgear", "00:50:56": "VMware", "00:50:F2": "Microsoft",
    "08:00:27": "VirtualBox", "08:55:31": "Huawei", "08:86:3B": "Belkin",
    "10:0B:A9": "Intel", "10:6F:3F": "Buffalo", "14:CC:20": "Xiaomi",
    "14:CF:92": "TP-Link", "18:D6:C7": "TP-Link", "1C:87:2C": "ASUSTek",
    "20:CF:30": "ASUSTek", "24:05:0F": "Intel", "28:E0:2C": "ASUS",
    "2C:F0:5D": "Micro-Star", "30:85:A9": "ASUSTek", "34:97:F6": "ASUSTek",
    "38:D5:47": "ASUSTek", "3C:37:86": "Netgear", "40:8D:5C": "Google",
    "44:D9:E7": "Ubiquiti", "48:EE:0C": "TP-Link", "4C:ED:FB": "ASUSTek",
    "50:46:5D": "ASUSTek", "50:C7:BF": "TP-Link", "52:54:00": "QEMU",
    "54:B8:0A": "Xiaomi", "58:D9:D5": "Tenda", "60:38:E0": "Belkin",
    "64:70:02": "TP-Link", "68:FF:7B": "TP-Link", "6C:72:20": "D-Link",
    "70:4D:7B": "ASUSTek", "74:DA:38": "D-Link", "78:44:76": "TP-Link",
    "7C:8B:CA": "TP-Link", "80:2A:A8": "Ubiquiti", "84:16:F9": "TP-Link",
    "88:71:B1": "TP-Link", "8C:3B:AD": "TP-Link", "90:F6:52": "TP-Link",
    "94:0C:6D": "TP-Link", "98:DA:C4": "TP-Link", "9C:A2:F4": "Intel",
    "A0:F3:C1": "TP-Link", "A4:2B:B0": "TP-Link", "A8:5E:45": "ASUSTek",
    "AC:84:C6": "TP-Link", "B0:4E:26": "TP-Link", "B4:B0:24": "D-Link",
    "B8:27:EB": "Raspberry Pi", "BC:46:99": "TP-Link", "C0:25:E9": "TP-Link",
    "C4:6E:1F": "TP-Link", "C8:3A:35": "Tenda", "CC:32:E5": "TP-Link",
    "D0:6F:4A": "Huawei", "D4:6E:0E": "TP-Link", "D8:0D:17": "TP-Link",
    "DC:FE:07": "ASUSTek", "E0:05:C5": "TP-Link", "E4:F0:42": "Google",
    "E8:48:B8": "TP-Link", "EC:08:6B": "TP-Link", "F0:9F:C2": "Ubiquiti",
    "F4:F2:6D": "TP-Link", "F8:1A:67": "TP-Link", "FC:EC:DA": "Ubiquiti",
}


class WiFiScanner:
    """Cross-platform WiFi network scanner."""

    def __init__(self):
        self.scan_method = self._detect_scan_method()
        logger.info("WiFi scanner initialized: method=%s", self.scan_method)

    def _detect_scan_method(self) -> str:
        """Detect the best available scanning tool for this platform."""
        system = platform.system().lower()

        if system == "windows":
            try:
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    return "netsh"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        elif system == "linux":
            try:
                subprocess.run(
                    ["which", "nmcli"], check=True,
                    capture_output=True, timeout=3,
                )
                return "nmcli"
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                try:
                    subprocess.run(
                        ["which", "iwlist"], check=True,
                        capture_output=True, timeout=3,
                    )
                    return "iwlist"
                except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass

        elif system == "darwin":
            airport_path = (
                "/System/Library/PrivateFrameworks/"
                "Apple80211.framework/Resources/airport"
            )
            if subprocess.run(
                ["test", "-f", airport_path],
                capture_output=True
            ).returncode == 0:
                return "airport"

        logger.warning(
            "No WiFi scanning tool found for %s. Using mock data.", system
        )
        return "mock"

    # ─── Public API ──────────────────────────────────────────

    def scan(self, duration: int = 10, interface: str = "wlan0") -> List[Dict]:
        """
        Scan for WiFi networks using the best available method.

        Args:
            duration: Scan duration in seconds (used for nmcli rescan)
            interface: Network interface (used for iwlist)

        Returns:
            List of network dictionaries
        """
        logger.info("Starting WiFi scan (method=%s)...", self.scan_method)

        try:
            if self.scan_method == "netsh":
                networks = self._scan_netsh()
            elif self.scan_method == "nmcli":
                networks = self._scan_nmcli(duration)
            elif self.scan_method == "iwlist":
                networks = self._scan_iwlist(interface)
            elif self.scan_method == "airport":
                networks = self._scan_airport()
            else:
                networks = self._scan_mock()

            logger.info("Scan complete: found %d networks", len(networks))
            return networks

        except Exception as exc:
            logger.error("Scan failed: %s", exc)
            return self._scan_mock()

    # ─── Windows: netsh ──────────────────────────────────────

    def _scan_netsh(self) -> List[Dict]:
        """Scan using Windows netsh command."""
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True, text=True, timeout=15, shell=False,
        )

        if result.returncode != 0:
            logger.warning("netsh returned %d", result.returncode)
            return []

        return self._parse_netsh_output(result.stdout)

    def _parse_netsh_output(self, output: str) -> List[Dict]:
        """Parse netsh wlan output into structured network records."""
        networks: List[Dict] = []
        current_ssid = None
        current_network: Dict = {}

        for raw_line in output.splitlines():
            line = raw_line.strip()

            # SSID line (not BSSID)
            if line.startswith("SSID") and "BSSID" not in line:
                parts = line.split(":", 1)
                current_ssid = parts[1].strip() if len(parts) > 1 else ""

            elif line.startswith("BSSID"):
                # Save previous network if exists
                if current_network and "bssid" in current_network:
                    networks.append(self._finalize_network(current_network))

                parts = line.split(":", 1)
                bssid_raw = parts[1].strip() if len(parts) > 1 else ""
                current_network = {
                    "ssid": current_ssid or "",
                    "bssid": bssid_raw,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "scan_method": "netsh",
                }

            elif current_network:
                if line.startswith("Signal"):
                    signal_str = line.split(":", 1)[1].strip().replace("%", "")
                    try:
                        quality = int(signal_str)
                        # Convert Windows percentage to approximate dBm
                        current_network["signal_strength"] = int(
                            (quality / 2) - 100
                        )
                    except ValueError:
                        current_network["signal_strength"] = -80

                elif line.startswith("Channel"):
                    try:
                        current_network["channel"] = int(
                            line.split(":", 1)[1].strip()
                        )
                    except ValueError:
                        current_network["channel"] = 0

                elif line.startswith("Band"):
                    band = line.split(":", 1)[1].strip()
                    current_network["band"] = band
                    if "5" in band:
                        current_network["frequency"] = 5000
                    else:
                        current_network["frequency"] = 2400

                elif line.startswith("Authentication"):
                    auth = line.split(":", 1)[1].strip()
                    current_network["encryption"] = self._map_auth_to_encryption(auth)

                elif line.startswith("Radio type"):
                    current_network["radio_type"] = line.split(":", 1)[1].strip()

                elif line.startswith("Encryption"):
                    # Keep the raw encryption type
                    current_network["cipher"] = line.split(":", 1)[1].strip()

        # Don't forget the last network
        if current_network and "bssid" in current_network:
            networks.append(self._finalize_network(current_network))

        return networks

    @staticmethod
    def _map_auth_to_encryption(auth: str) -> str:
        """Map Windows authentication type to standard encryption name."""
        auth_lower = auth.lower()
        if "wpa3" in auth_lower:
            return "WPA3"
        elif "wpa2" in auth_lower:
            return "WPA2"
        elif "wpa" in auth_lower:
            return "WPA"
        elif "wep" in auth_lower:
            return "WEP"
        elif "open" in auth_lower:
            return "Open"
        return auth

    def _finalize_network(self, network: Dict) -> Dict:
        """Add vendor information and clean up network data."""
        bssid = network.get("bssid", "").upper()
        if bssid and bssid != "00:00:00:00:00:00":
            # Lookup vendor by OUI (first 3 octets)
            oui = ":".join(bssid.split(":")[:3])
            network["vendor"] = OUI_VENDORS.get(oui, "Unknown")
        else:
            network["vendor"] = "Unknown"

        # Ensure all required fields exist
        network.setdefault("ssid", "<HIDDEN>")
        network.setdefault("signal_dbm", network.get("signal_strength", -100))
        network.setdefault("security", "UNKNOWN")
        network.setdefault("channel", 0)

        return network

    # ─── Linux: nmcli ────────────────────────────────────────

    def _scan_nmcli(self, duration: int) -> List[Dict]:
        """Scan using Linux nmcli command."""
        # Force a rescan first
        subprocess.run(["nmcli", "dev", "wifi", "rescan"], capture_output=True)
        
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,SECURITY,CHAN", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            return []

        networks = []
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 5:
                # nmcli escapes colons in BSSID with backslash, fix it
                bssid = ":".join(parts[1:7]).replace("\\", "")
                networks.append(self._finalize_network({
                    "ssid": parts[0],
                    "bssid": bssid,
                    "signal_dbm": int(parts[7]) if len(parts) > 7 else -80,
                    "security": parts[8] if len(parts) > 8 else "OPEN",
                    "channel": int(parts[9]) if len(parts) > 9 else 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "scan_method": "nmcli"
                }))
        return networks

    # ─── Linux: iwlist ───────────────────────────────────────

    def _scan_iwlist(self, interface: str) -> List[Dict]:
        """Scan using iwlist (older Linux tool)."""
        result = subprocess.run(
            ["sudo", "iwlist", interface, "scan"],
            capture_output=True, text=True, timeout=15,
        )

        networks = []
        current: Dict = {}

        for raw_line in result.stdout.split("\n"):
            line = raw_line.strip()

            if "Cell" in line and "Address:" in line:
                if current and "bssid" in current:
                    networks.append(self._finalize_network(current))
                current = {
                    "bssid": line.split("Address: ")[1].strip(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "scan_method": "iwlist",
                }

            elif "ESSID:" in line:
                ssid = line.split('ESSID:')[1].strip().strip('"')
                current["ssid"] = ssid

            elif "Channel:" in line:
                try:
                    current["channel"] = int(line.split("Channel:")[1].strip())
                except ValueError:
                    current["channel"] = 0

            elif "Signal level=" in line:
                match = re.search(r"Signal level=(-?\d+)", line)
                if match:
                    current["signal_strength"] = int(match.group(1))

            elif "Encryption key:" in line:
                is_enc = "on" in line.lower()
                current["encryption"] = "WPA/WPA2" if is_enc else "Open"

        if current and "bssid" in current:
            networks.append(self._finalize_network(current))

        return networks

    # ─── macOS: airport ──────────────────────────────────────

    def _scan_airport(self) -> List[Dict]:
        """Scan using macOS airport utility."""
        airport = (
            "/System/Library/PrivateFrameworks/"
            "Apple80211.framework/Resources/airport"
        )
        result = subprocess.run(
            [airport, "-s"], capture_output=True, text=True, timeout=10,
        )

        networks = []
        for line in result.stdout.strip().split("\n")[1:]:  # skip header
            parts = line.split()
            if len(parts) < 7:
                continue
            try:
                networks.append(self._finalize_network({
                    "ssid": parts[0],
                    "bssid": parts[1],
                    "signal_strength": int(parts[2]),
                    "channel": int(parts[3].split(",")[0]),
                    "encryption": parts[6] if len(parts) > 6 else "Unknown",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "scan_method": "airport",
                }))
            except (ValueError, IndexError):
                continue

        return networks

    # ─── Mock Fallback ───────────────────────────────────────

    def _scan_mock(self) -> List[Dict]:
        """Return mock data for development environments."""
        logger.debug("Generating mock WiFi data")
        return [
            {
                "ssid": "Home-WiFi",
                "bssid": "00:11:22:33:44:55",
                "signal_dbm": -45,
                "security": "WPA2-PSK",
                "channel": 6,
                "vendor": "Netgear",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "ssid": "Public-Library",
                "bssid": "AA:BB:CC:DD:EE:FF",
                "signal_dbm": -70,
                "security": "OPEN",
                "channel": 11,
                "vendor": "Cisco",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "ssid": "Home-WiFi", # Duplicate SSID (Evil Twin Simulation)
                "bssid": "DE:AD:BE:EF:00:01",
                "signal_dbm": -30,
                "security": "OPEN",
                "channel": 6,
                "vendor": "Unknown",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]

    # ─── Vendor Lookup ───────────────────────────────────────

    @staticmethod
    def _get_vendor(mac: str) -> str:
        """Look up vendor from MAC address OUI prefix."""
        if not mac or len(mac) < 8:
            return "Unknown"
        oui = mac[:8].upper()
        return OUI_VENDORS.get(oui, "Unknown")