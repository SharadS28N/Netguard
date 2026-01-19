import scapy.all as scapy
from scapy.arch import get_if_hwaddr, get_if_list
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeReq, Dot11ProbeResp
import threading
import time
from datetime import datetime
from typing import Dict, List
import subprocess
import sys
import platform
import struct
import socket

class NetworkScanner:
    """Real network scanner using Scapy for WiFi/802.11 networks"""

    def __init__(self, interface=None):
        self.interface = interface
        self.networks = {}
        self.scanning = False
        self.clients = {}
        self.packets_captured = 0

    def get_available_interfaces(self) -> List[str]:
        """Get available network interfaces"""
        try:
            interfaces = scapy.get_windows_if_list() if sys.platform == 'win32' else scapy.conf.ifaces.data.keys()
            return list(interfaces)
        except Exception as e:
            print(f"Error getting interfaces: {e}")
            return []

    def get_monitor_mode_interface(self) -> str:
        """Find interface in monitor mode"""
        try:
            if sys.platform == 'linux' or sys.platform == 'linux2':
                # Check for monitor mode on Linux
                result = subprocess.run(['iwconfig'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Monitor' in line:
                        return line.split()[0]
            elif sys.platform == 'darwin':
                # macOS
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'monitor' in line.lower():
                        return line.split()[0]
        except Exception as e:
            print(f"Error finding monitor mode interface: {e}")
        return None

    def enable_monitor_mode(self, interface: str) -> bool:
        """Enable monitor mode on interface"""
        try:
            if sys.platform == 'linux' or sys.platform == 'linux2':
                subprocess.run(['sudo', 'airmon-ng', 'start', interface], check=True)
                return True
            elif sys.platform == 'darwin':
                subprocess.run(['sudo', 'airport', '-z'], check=False)
                subprocess.run(['sudo', 'airport', f'{interface}', 'sniff'], check=False)
                return True
        except Exception as e:
            print(f"Error enabling monitor mode: {e}")
        return False

    def parse_beacon(self, packet) -> Dict:
        """Parse WiFi beacon packet"""
        try:
            if packet.haslayer(Dot11Beacon):
                bssid = packet[Dot11].addr2
                ssid = packet[Dot11Elt].info.decode() if packet[Dot11Elt].info else ""
                
                # Get channel
                channel = None
                if Dot11Elt in packet:
                    for elt in packet.getlayer(Dot11Elt).chain:
                        if elt.ID == 3:  # DS Parameter Set
                            channel = struct.unpack('B', elt.info)[0]
                
                # Get signal strength
                signal_strength = packet.dBm_AntSignal if hasattr(packet, 'dBm_AntSignal') else -100
                
                # Encryption type
                encryption = self._get_encryption_type(packet)
                
                # Check if hidden
                is_hidden = len(ssid) == 0
                
                return {
                    "bssid": bssid,
                    "ssid": ssid if not is_hidden else "[Hidden]",
                    "channel": channel,
                    "signal_strength": signal_strength,
                    "encryption": encryption,
                    "is_hidden": is_hidden,
                    "timestamp": datetime.utcnow().isoformat(),
                    "vendor": self._get_vendor_from_mac(bssid)
                }
        except Exception as e:
            print(f"Error parsing beacon: {e}")
        return None

    def _get_encryption_type(self, packet) -> str:
        """Get encryption type from beacon"""
        try:
            if packet[Dot11Beacon].cap.privacy:
                if packet.haslayer(Dot11Elt):
                    for elt in packet.getlayer(Dot11Elt).chain:
                        if elt.ID == 48:  # RSN
                            return "WPA2"
                        elif elt.ID == 221 and elt.info.startswith(b'\x00\x50\xf2'):
                            return "WPA"
                return "WEP"
        except:
            pass
        return "Open"

    def _get_vendor_from_mac(self, mac: str) -> str:
        """Get vendor from MAC address (simplified OUI lookup)"""
        oui_map = {
            "00:05:4E": "Linksys",
            "00:0B:85": "Netgear",
            "00:1A:2B": "Apple",
            "00:1E:E5": "TP-Link",
            "00:25:5A": "Apple",
            "00:50:F2": "Microsoft",
            "08:55:31": "Huawei",
            "14:CC:20": "Xiaomi",
            "28:E0:2C": "ASUS",
        }
        mac_prefix = mac[:8].upper()
        for prefix, vendor in oui_map.items():
            if mac_prefix.startswith(prefix):
                return vendor
        return "Unknown"

    def packet_handler(self, packet):
        """Handle captured packets"""
        if packet.haslayer(Dot11):
            self.packets_captured += 1
            
            # Parse beacon frames
            if packet.haslayer(Dot11Beacon):
                network_info = self.parse_beacon(packet)
                if network_info:
                    bssid = network_info["bssid"]
                    if bssid not in self.networks:
                        self.networks[bssid] = network_info
                        self.networks[bssid]["client_count"] = 0
                    self.networks[bssid]["signal_strength"] = network_info["signal_strength"]
            
            # Track clients (Data frames from stations)
            elif packet.haslayer(Dot11) and packet[Dot11].type == 2:
                src = packet[Dot11].addr2
                dst = packet[Dot11].addr1
                bssid = packet[Dot11].addr3
                
                if bssid not in self.clients:
                    self.clients[bssid] = set()
                self.clients[bssid].add(src)

    def start_scan(self, interface: str = None, duration: int = 30, channels: List[int] = None):
        """Start passive WiFi scan"""
        if interface is None:
            interface = self.interface
        
        if interface is None:
            raise ValueError("No interface specified")
        
        self.networks = {}
        self.clients = {}
        self.packets_captured = 0
        self.scanning = True
        
        try:
            print(f"Starting scan on {interface} for {duration} seconds...")
            
            # Use channel hopping if no specific channels given
            if channels is None:
                channels = list(range(1, 14))  # WiFi channels 1-13 (valid worldwide)
            
            # Simple passive scan without channel hopping
            scapy.sniff(
                iface=interface,
                prn=self.packet_handler,
                timeout=duration,
                store=False
            )
            
            self.scanning = False
            print(f"Scan completed. Found {len(self.networks)} networks.")
            
        except PermissionError:
            print("Error: Root/Admin privileges required for WiFi scanning")
            self.scanning = False
        except Exception as e:
            print(f"Scan error: {e}")
            self.scanning = False
        
        return self.get_results()

    def start_active_scan(self, interface: str = None, duration: int = 15):
        """Start active WiFi scan with probe requests"""
        if interface is None:
            interface = self.interface
        
        self.networks = {}
        self.scanning = True
        
        try:
            print(f"Starting active scan on {interface} for {duration} seconds...")
            
            # Send probe requests
            probe_req = (
                scapy.Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=get_if_hwaddr(interface), addr3="ff:ff:ff:ff:ff:ff") /
                Dot11ProbeReq() /
                scapy.Dot11Elt(ID="SSID", info="")
            )
            
            def send_probes():
                start_time = time.time()
                while time.time() - start_time < duration:
                    scapy.send(probe_req, iface=interface, verbose=False)
                    time.sleep(1)
            
            # Send probes in background
            probe_thread = threading.Thread(target=send_probes, daemon=True)
            probe_thread.start()
            
            # Capture responses
            scapy.sniff(
                iface=interface,
                prn=self.packet_handler,
                timeout=duration,
                store=False
            )
            
            self.scanning = False
            
        except Exception as e:
            print(f"Active scan error: {e}")
            self.scanning = False
        
        return self.get_results()

    def get_results(self) -> Dict:
        """Get scan results"""
        results = {
            "networks": [],
            "clients": {},
            "total_packets": self.packets_captured,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for bssid, network_info in self.networks.items():
            network_data = network_info.copy()
            network_data["client_count"] = len(self.clients.get(bssid, set()))
            results["networks"].append(network_data)
            results["clients"][bssid] = list(self.clients.get(bssid, set()))
        
        return results

    def analyze_for_threats(self, networks: List[Dict]) -> List[Dict]:
        """Analyze networks for potential evil twins and threats"""
        threats = []
        
        # Check for duplicate SSIDs (potential evil twin)
        ssid_map = {}
        for network in networks:
            ssid = network.get("ssid")
            if ssid and not network.get("is_hidden"):
                if ssid not in ssid_map:
                    ssid_map[ssid] = []
                ssid_map[ssid].append(network)
        
        # Flag networks with same SSID as potential evil twins
        for ssid, nets in ssid_map.items():
            if len(nets) > 1:
                # Multiple networks with same SSID - potential evil twin
                for net in nets:
                    threats.append({
                        "bssid": net["bssid"],
                        "ssid": ssid,
                        "threat_type": "evil_twin",
                        "confidence": 0.7,
                        "threat_level": "high",
                        "reason": f"Duplicate SSID detected ({len(nets)} networks)"
                    })
        
        # Check for weak encryption
        for network in networks:
            if network.get("encryption") in ["WEP", "Open"]:
                threats.append({
                    "bssid": network["bssid"],
                    "ssid": network.get("ssid"),
                    "threat_type": "weak_encryption",
                    "confidence": 0.8,
                    "threat_level": "medium",
                    "reason": f"Weak encryption: {network['encryption']}"
                })
        
        return threats
