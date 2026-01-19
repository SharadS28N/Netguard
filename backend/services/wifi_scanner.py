#!/usr/bin/env python3
"""
WiFi Network Scanner
Scans for available WiFi networks using nmcli or iwlist
"""

import subprocess
import re
import json
from typing import List, Dict
from datetime import datetime

class WiFiScanner:
    """Real WiFi network scanner"""
    
    def __init__(self):
        self.scan_method = self._detect_scan_method()
    
    def _detect_scan_method(self) -> str:
        """Detect which scanning tool is available"""
        try:
            subprocess.run(['which', 'nmcli'], check=True, capture_output=True)
            return 'nmcli'
        except:
            try:
                subprocess.run(['which', 'iwlist'], check=True, capture_output=True)
                return 'iwlist'
            except:
                return 'mock'
    
    def scan(self, duration: int = 10, interface: str = 'wlan0') -> List[Dict]:
        """
        Scan for WiFi networks
        
        Args:
            duration: Scan duration in seconds
            interface: WiFi interface name
        
        Returns:
            List of network dictionaries
        """
        print(f"[WiFiScanner] Starting scan with {self.scan_method}...")
        
        if self.scan_method == 'nmcli':
            return self._scan_nmcli(duration)
        elif self.scan_method == 'iwlist':
            return self._scan_iwlist(interface)
        else:
            return self._scan_mock()
    
    def _scan_nmcli(self, duration: int) -> List[Dict]:
        """Scan using nmcli (NetworkManager)"""
        try:
            # Rescan networks
            subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], 
                          timeout=duration, 
                          capture_output=True)
            
            # Get network list
            result = subprocess.run(
                ['nmcli', '-f', 'SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY', 
                 'dev', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            networks = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) < 6:
                    continue
                
                try:
                    network = {
                        'ssid': parts[0],
                        'bssid': parts[1],
                        'channel': int(parts[2]),
                        'frequency': int(parts[3]),
                        'signal_strength': int(parts[4]),
                        'encryption': ' '.join(parts[5:]) if len(parts) > 5 else 'Open',
                        'vendor': self._get_vendor_from_mac(parts[1]),
                        'timestamp': datetime.utcnow().isoformat(),
                        'scan_method': 'nmcli'
                    }
                    
                    # Add derived features
                    network['is_encrypted'] = network['encryption'] != 'Open'
                    network['is_hidden'] = network['ssid'] == '--'
                    
                    networks.append(network)
                except (ValueError, IndexError) as e:
                    print(f"[WiFiScanner] Error parsing line: {line} - {e}")
                    continue
            
            print(f"[WiFiScanner] Found {len(networks)} networks")
            return networks
        
        except subprocess.TimeoutExpired:
            print("[WiFiScanner] Scan timeout")
            return []
        except Exception as e:
            print(f"[WiFiScanner] Error: {e}")
            return []
    
    def _scan_iwlist(self, interface: str) -> List[Dict]:
        """Scan using iwlist (older tool)"""
        try:
            result = subprocess.run(
                ['sudo', 'iwlist', interface, 'scan'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            networks = []
            current_network = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'Cell' in line and 'Address:' in line:
                    if current_network:
                        networks.append(current_network)
                    current_network = {
                        'bssid': line.split('Address: ')[1].strip(),
                        'timestamp': datetime.utcnow().isoformat(),
                        'scan_method': 'iwlist'
                    }
                
                elif 'ESSID:' in line:
                    ssid = line.split('ESSID:')[1].strip().strip('"')
                    current_network['ssid'] = ssid if ssid else 'Hidden'
                    current_network['is_hidden'] = not bool(ssid)
                
                elif 'Channel:' in line:
                    try:
                        current_network['channel'] = int(line.split('Channel:')[1].strip())
                    except:
                        current_network['channel'] = 0
                
                elif 'Signal level=' in line:
                    try:
                        signal = re.search(r'Signal level=(-?\d+)', line)
                        if signal:
                            current_network['signal_strength'] = int(signal.group(1))
                    except:
                        current_network['signal_strength'] = -100
                
                elif 'Encryption key:' in line:
                    is_encrypted = 'on' in line.lower()
                    current_network['is_encrypted'] = is_encrypted
                    current_network['encryption'] = 'WPA/WPA2' if is_encrypted else 'Open'
            
            # Add last network
            if current_network:
                networks.append(current_network)
            
            # Add vendor info
            for net in networks:
                net['vendor'] = self._get_vendor_from_mac(net.get('bssid', ''))
            
            print(f"[WiFiScanner] Found {len(networks)} networks")
            return networks
        
        except Exception as e:
            print(f"[WiFiScanner] Error: {e}")
            return []
    
    def _scan_mock(self) -> List[Dict]:
        """Mock scan for testing (when no real scanner available)"""
        print("[WiFiScanner] Using MOCK data (no real scanner found)")
        
        return [
            {
                'ssid': 'Hackathon_WiFi',
                'bssid': 'AA:BB:CC:DD:EE:01',
                'channel': 6,
                'frequency': 2437,
                'signal_strength': -45,
                'encryption': 'WPA2',
                'vendor': 'TP-Link',
                'is_encrypted': True,
                'is_hidden': False,
                'timestamp': datetime.utcnow().isoformat(),
                'scan_method': 'mock'
            },
            {
                'ssid': 'Free_Public_WiFi',
                'bssid': '11:22:33:44:55:66',
                'channel': 6,
                'frequency': 2437,
                'signal_strength': -38,
                'encryption': 'Open',
                'vendor': 'Unknown',
                'is_encrypted': False,
                'is_hidden': False,
                'timestamp': datetime.utcnow().isoformat(),
                'scan_method': 'mock'
            },
            {
                'ssid': 'Hackathon_WiFi',  # Evil twin!
                'bssid': 'FF:EE:DD:CC:BB:AA',
                'channel': 6,
                'frequency': 2437,
                'signal_strength': -42,
                'encryption': 'Open',
                'vendor': 'Unknown',
                'is_encrypted': False,
                'is_hidden': False,
                'timestamp': datetime.utcnow().isoformat(),
                'scan_method': 'mock'
            },
            {
                'ssid': 'Home_Network_5G',
                'bssid': '99:88:77:66:55:44',
                'channel': 149,
                'frequency': 5745,
                'signal_strength': -65,
                'encryption': 'WPA3',
                'vendor': 'Netgear',
                'is_encrypted': True,
                'is_hidden': False,
                'timestamp': datetime.utcnow().isoformat(),
                'scan_method': 'mock'
            }
        ]
    
    def _get_vendor_from_mac(self, mac: str) -> str:
        """Get vendor name from MAC address (simplified)"""
        if not mac or len(mac) < 8:
            return 'Unknown'
        
        # OUI (first 3 octets) to vendor mapping (simplified)
        oui_map = {
            'AA:BB:CC': 'TP-Link',
            '11:22:33': 'Unknown',
            'FF:EE:DD': 'Unknown',
            '99:88:77': 'Netgear',
            '00:0C:29': 'VMware',
            '08:00:27': 'VirtualBox',
            '00:1B:63': 'Apple',
            '00:23:6'
            'C': 'Apple',
            '00:50:56': 'VMware',
            '52:54:00': 'QEMU',
        }
        
        oui = mac[:8].upper()
        return oui_map.get(oui, 'Unknown')

# Test function
if __name__ == "__main__":
    scanner = WiFiScanner()
    print(f"Using scan method: {scanner.scan_method}")
    
    networks = scanner.scan(duration=5)
    print(f"\nFound {len(networks)} networks:\n")
    
    for net in networks:
        print(f"  SSID: {net['ssid']}")
        print(f"  BSSID: {net['bssid']}")
        print(f"  Signal: {net['signal_strength']} dBm")
        print(f"  Encryption: {net['encryption']}")
        print(f"  Vendor: {net['vendor']}")
        print()