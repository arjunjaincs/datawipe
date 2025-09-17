"""
DataWipe Pro - Cross-Platform Drive Detection Utility
Team: Tejasway

Detects storage devices and their properties on Windows and Linux/macOS.
"""

import subprocess
import json
import re
import platform
import psutil
from typing import List, Dict, Any

class DriveDetector:
    def __init__(self):
        self.detected_drives = []
        self.system = platform.system()
    
    def detect_drives(self) -> List[Dict[str, Any]]:
        """Detect all storage drives in the system (cross-platform)"""
        drives = []
        
        try:
            if self.system == "Windows":
                drives.extend(self._detect_windows_drives())
            elif self.system in ["Linux", "Darwin"]:
                drives.extend(self._detect_unix_drives())
            else:
                print(f"Unsupported system: {self.system}")
                drives = self._get_mock_drives()
            
        except Exception as e:
            print(f"Drive detection error: {e}")
            # Return mock data for demo
            drives = self._get_mock_drives()
        
        self.detected_drives = drives
        return drives
    
    def get_storage_devices(self) -> List[Dict[str, Any]]:
        """Get storage devices in format expected by GUI"""
        drives = self.detect_drives()
        formatted_drives = []
        
        for drive in drives:
            formatted_drive = {
                'name': drive.get('model', 'Unknown Device'),
                'device_path': drive.get('device_path', 'Unknown'),
                'size': drive.get('size', 0),
                'type': drive.get('type', 'Unknown'),
                'interface': drive.get('interface', 'Unknown'),
                'serial': drive.get('serial', 'Unknown'),
                'model': drive.get('model', 'Unknown Device'),
                'smart_status': 'Available',
                'secure_erase_support': drive.get('type', '').upper() in ['SSD', 'NVME'],
                'sanitize_support': drive.get('type', '').upper() == 'NVME',
                'partitions': [],
                'health_status': 'normal',
                'temperature': None,
                'power_on_hours': None,
                'bus_type': 'USB' if 'usb' in drive.get('interface', '').lower() else 'INTERNAL'
            }
            formatted_drives.append(formatted_drive)
        
        return formatted_drives

    def _detect_windows_drives(self) -> List[Dict[str, Any]]:
        """Detect drives on Windows using wmic and psutil"""
        drives = []
        
        try:
            # Use psutil for cross-platform disk detection
            disk_partitions = psutil.disk_partitions(all=True)
            physical_drives = set()
            
            # Get physical drives
            for partition in disk_partitions:
                if partition.device.startswith('\\\\.\\PHYSICALDRIVE'):
                    physical_drives.add(partition.device)
            
            # Use wmic to get detailed drive information
            try:
                result = subprocess.run([
                    'wmic', 'diskdrive', 'get', 
                    'DeviceID,Model,SerialNumber,Size,InterfaceType',
                    '/format:csv'
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            parts = line.split(',')
                            if len(parts) >= 6:
                                drive_info = {
                                    'device_path': parts[1].strip() if len(parts) > 1 else 'Unknown',
                                    'model': parts[3].strip() if len(parts) > 3 else 'Unknown',
                                    'serial': parts[4].strip() if len(parts) > 4 else 'Unknown',
                                    'size': int(parts[5].strip()) if parts[5].strip().isdigit() else 0,
                                    'interface': parts[2].strip() if len(parts) > 2 else 'Unknown',
                                    'type': self._detect_drive_type_windows(parts[3].strip() if len(parts) > 3 else ''),
                                    'mountpoint': None,
                                    'name': parts[1].strip().split('\\')[-1] if len(parts) > 1 else 'Unknown'
                                }
                                drives.append(drive_info)
            except Exception as e:
                print(f"wmic detection failed: {e}")
                # Fallback to psutil only
                drives = self._detect_with_psutil()
                
        except Exception as e:
            print(f"Windows drive detection failed: {e}")
            drives = self._get_mock_drives()
        
        return drives
    
    def _detect_unix_drives(self) -> List[Dict[str, Any]]:
        """Detect drives on Linux/macOS using lsblk and smartctl"""
        drives = []
        
        try:
            # Use lsblk on Linux
            if self.system == "Linux":
                drives.extend(self._detect_with_lsblk())
            else:
                # macOS fallback
                drives.extend(self._detect_with_psutil())
            
            # Enhance with smartctl information if available
            drives = self._enhance_with_smartctl(drives)
            
        except Exception as e:
            print(f"Unix drive detection failed: {e}")
            drives = self._get_mock_drives()
        
        return drives
    
    def _detect_with_psutil(self) -> List[Dict[str, Any]]:
        """Cross-platform detection using psutil"""
        drives = []
        
        try:
            # Get disk usage for all mounted drives
            disk_partitions = psutil.disk_partitions(all=True)
            processed_devices = set()
            
            for partition in disk_partitions:
                device = partition.device
                
                # Skip already processed devices and non-physical drives
                if device in processed_devices or 'loop' in device or 'ram' in device:
                    continue
                
                processed_devices.add(device)
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drive_info = {
                        'device_path': device,
                        'model': 'Unknown (psutil)',
                        'serial': 'Unknown',
                        'size': usage.total,
                        'interface': 'Unknown',
                        'type': 'Unknown',
                        'mountpoint': partition.mountpoint,
                        'name': device.split('/')[-1] if '/' in device else device
                    }
                    drives.append(drive_info)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"psutil detection failed: {e}")
        
        return drives
    
    def _detect_with_lsblk(self) -> List[Dict[str, Any]]:
        """Use lsblk to detect drives on Linux"""
        try:
            # Run lsblk with JSON output
            result = subprocess.run([
                'lsblk', '-J', '-o', 
                'NAME,SIZE,TYPE,MOUNTPOINT,MODEL,SERIAL,TRAN'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                drives = []
                
                for device in data.get('blockdevices', []):
                    if device.get('type') == 'disk':
                        drive_info = {
                            'device_path': f"/dev/{device['name']}",
                            'model': device.get('model', 'Unknown'),
                            'serial': device.get('serial', 'Unknown'),
                            'size': self._parse_size(device.get('size', '0')),
                            'interface': device.get('tran', 'Unknown'),
                            'type': self._detect_drive_type(device),
                            'mountpoint': device.get('mountpoint'),
                            'name': device['name']
                        }
                        drives.append(drive_info)
                
                return drives
            
        except Exception as e:
            print(f"lsblk detection failed: {e}")
        
        return []
    
    def _enhance_with_smartctl(self, drives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance drive information with smartctl data"""
        enhanced_drives = []
        
        for drive in drives:
            try:
                # Run smartctl to get detailed information
                result = subprocess.run([
                    'smartctl', '-i', drive['device_path']
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    smart_info = self._parse_smartctl_output(result.stdout)
                    drive.update(smart_info)
                
            except Exception as e:
                print(f"smartctl enhancement failed for {drive['device_path']}: {e}")
            
            enhanced_drives.append(drive)
        
        return enhanced_drives
    
    def _parse_smartctl_output(self, output: str) -> Dict[str, Any]:
        """Parse smartctl output for additional drive information"""
        info = {}
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            
            if 'Device Model:' in line:
                info['model'] = line.split(':', 1)[1].strip()
            elif 'Serial Number:' in line:
                info['serial'] = line.split(':', 1)[1].strip()
            elif 'User Capacity:' in line:
                # Extract size from capacity line
                match = re.search(r'\[(.*?)\]', line)
                if match:
                    size_str = match.group(1)
                    info['size'] = self._parse_size(size_str)
            elif 'Rotation Rate:' in line:
                if 'Solid State Device' in line:
                    info['type'] = 'SSD'
                else:
                    info['type'] = 'HDD'
        
        return info
    
    def _detect_drive_type(self, device: Dict[str, Any]) -> str:
        """Detect drive type based on available information"""
        name = device.get('name', '').lower()
        model = device.get('model', '').lower()
        tran = device.get('tran', '').lower()
        
        # NVMe detection
        if 'nvme' in name or 'nvme' in tran:
            return 'NVMe'
        
        # SSD detection patterns
        ssd_patterns = ['ssd', 'solid', 'flash', 'samsung', 'crucial', 'kingston']
        if any(pattern in model for pattern in ssd_patterns):
            return 'SSD'
        
        # Default to HDD
        return 'HDD'
    
    def _detect_drive_type_windows(self, model: str) -> str:
        """Detect drive type on Windows based on model name"""
        model = model.lower()
        
        # NVMe detection
        if 'nvme' in model:
            return 'NVMe'
        
        # SSD detection patterns
        ssd_patterns = ['ssd', 'solid', 'flash', 'samsung', 'crucial', 'kingston', 'intel']
        if any(pattern in model for pattern in ssd_patterns):
            return 'SSD'
        
        # Default to HDD
        return 'HDD'
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        if not size_str or size_str == '0':
            return 0
        
        # Remove any brackets and extra spaces
        size_str = re.sub(r'[^\d.,KMGTPE]', '', size_str.upper())
        
        # Extract number and unit
        match = re.match(r'([\d.,]+)([KMGTPE]?)', size_str)
        if not match:
            return 0
        
        number_str, unit = match.groups()
        
        try:
            number = float(number_str.replace(',', ''))
        except ValueError:
            return 0
        
        # Convert to bytes
        multipliers = {
            '': 1,
            'K': 1024,
            'M': 1024**2,
            'G': 1024**3,
            'T': 1024**4,
            'P': 1024**5,
            'E': 1024**6
        }
        
        return int(number * multipliers.get(unit, 1))
    
    def _get_mock_drives(self) -> List[Dict[str, Any]]:
        """Return mock drive data for demonstration"""
        if self.system == "Windows":
            return [
                {
                    'device_path': '\\\\.\\PHYSICALDRIVE0',
                    'model': 'Samsung SSD 970 EVO Plus',
                    'serial': 'S4EWNX0N123456',
                    'size': 500 * 1024**3,  # 500 GB
                    'interface': 'NVMe',
                    'type': 'NVMe',
                    'mountpoint': None,
                    'name': 'PHYSICALDRIVE0'
                },
                {
                    'device_path': '\\\\.\\PHYSICALDRIVE1',
                    'model': 'CT500BX500SSD1',
                    'serial': 'CT500BX500SSD1_2345',
                    'size': 500 * 1024**3,  # 500 GB
                    'interface': 'SATA',
                    'type': 'SSD',
                    'mountpoint': None,
                    'name': 'PHYSICALDRIVE1'
                }
            ]
        else:
            return [
                {
                    'device_path': '/dev/sda',
                    'model': 'Samsung SSD 970 EVO Plus',
                    'serial': 'S4EWNX0N123456',
                    'size': 500 * 1024**3,  # 500 GB
                    'interface': 'nvme',
                    'type': 'NVMe',
                    'mountpoint': None,
                    'name': 'sda'
                },
                {
                    'device_path': '/dev/sdb',
                    'model': 'CT500BX500SSD1',
                    'serial': 'CT500BX500SSD1_2345',
                    'size': 500 * 1024**3,  # 500 GB
                    'interface': 'sata',
                    'type': 'SSD',
                    'mountpoint': None,
                    'name': 'sdb'
                },
                {
                    'device_path': '/dev/sdc',
                    'model': 'WD Blue 1TB',
                    'serial': 'WD-WCAZAD123456',
                    'size': 1024**4,  # 1 TB
                    'interface': 'sata',
                    'type': 'HDD',
                    'mountpoint': None,
                    'name': 'sdc'
                }
            ]
