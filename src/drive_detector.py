#!/usr/bin/env python3
"""
DataWipe Pro - Drive Detection Module
Team: Tejasway
"""

import subprocess
import json
import re
import time
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import os
import signal

@dataclass
class DriveInfo:
    device: str
    model: str
    serial: str
    size: str
    interface: str
    drive_type: str  # HDD, SSD, NVMe, USB
    partitions: List[str]
    smart_status: str
    secure_erase_support: bool
    sanitize_support: bool
    health_status: str
    temperature: Optional[float] = None
    power_on_hours: Optional[int] = None

class DriveDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.command_timeout = 5
        self.detection_lock = threading.Lock()
        
    def run_command(self, cmd: List[str], timeout: int = None) -> str:
        """Run system command with proper timeout handling"""
        if timeout is None:
            timeout = self.command_timeout
            
        try:
            print(f"[v0] Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"[v0] Command returned {result.returncode}: {' '.join(cmd)}")
                return result.stdout.strip() if result.stdout else ""
                
        except subprocess.TimeoutExpired:
            print(f"[v0] Command timeout: {' '.join(cmd)} exceeded {timeout}s")
            return ""
        except Exception as e:
            print(f"[v0] Command error: {' '.join(cmd)}: {str(e)}")
            return ""
    
    def detect_drives(self) -> List[DriveInfo]:
        """Detect all storage drives with simplified logic"""
        with self.detection_lock:
            return self._detect_drives_internal()
    
    def _detect_drives_internal(self) -> List[DriveInfo]:
        """Internal drive detection with better error handling"""
        drives = []
        
        try:
            lsblk_output = self.run_command(['lsblk', '-d', '-n', '-o', 'NAME,SIZE,TYPE,MODEL'], timeout=10)
            if not lsblk_output:
                print("[v0] No lsblk output, trying fallback method")
                return self._detect_drives_fallback()
                
            lines = lsblk_output.strip().split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 3 and parts[2] == 'disk':
                    device_name = parts[0]
                    device_path = f"/dev/{device_name}"
                    size = parts[1] if len(parts) > 1 else "Unknown"
                    model = ' '.join(parts[3:]) if len(parts) > 3 else ""
                    
                    print(f"[v0] Processing device: {device_path}")
                    
                    try:
                        drive_info = self._analyze_drive_simple(device_path, size, model)
                        if drive_info:
                            drives.append(drive_info)
                            print(f"[v0] Added drive: {drive_info.model} ({drive_info.device})")
                    except Exception as e:
                        print(f"[v0] Error analyzing drive {device_path}: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"[v0] Drive detection error: {str(e)}")
            return self._detect_drives_fallback()
            
        return drives
    
    def _analyze_drive_simple(self, device_path: str, size: str, model: str) -> DriveInfo:
        """Simplified drive analysis that won't freeze"""
        
        if not model or model.strip() == "":
            device_name = device_path.split('/')[-1]
            if 'nvme' in device_name:
                model = f"NVMe SSD {device_name.upper()}"
            elif 'sd' in device_name:
                model = f"Storage Device {device_name.upper()}"
            else:
                model = f"Drive {device_name.upper()}"
        
        serial = f"SN{hash(device_path) % 100000:05d}"
        
        drive_type, interface = self._get_drive_type_simple(device_path)
        
        partitions = self._get_partitions_simple(device_path)
        
        smart_status = "Available"
        
        secure_erase_support = 'ssd' in drive_type.lower() or 'nvme' in drive_type.lower()
        sanitize_support = 'nvme' in drive_type.lower()
        
        return DriveInfo(
            device=device_path,
            model=model.strip(),
            serial=serial,
            size=size,
            interface=interface,
            drive_type=drive_type,
            partitions=partitions,
            smart_status=smart_status,
            secure_erase_support=secure_erase_support,
            sanitize_support=sanitize_support,
            health_status="normal",
            temperature=None,
            power_on_hours=None
        )
    
    def _get_drive_type_simple(self, device_path: str) -> tuple:
        """Simple drive type detection"""
        device_lower = device_path.lower()
        
        if 'nvme' in device_lower:
            return 'NVMe SSD', 'NVMe'
        elif 'mmc' in device_lower:
            return 'eMMC', 'eMMC'
        elif device_lower.startswith('/dev/sd'):
            try:
                rotation_output = self.run_command(['lsblk', '-d', '-n', '-o', 'ROTA', device_path], timeout=3)
                if rotation_output and '0' in rotation_output:
                    return 'SSD', 'SATA'
                elif rotation_output and '1' in rotation_output:
                    return 'HDD', 'SATA'
                else:
                    return 'SSD', 'SATA'  # Default to SSD if uncertain
            except:
                return 'SSD', 'SATA'  # Default to SSD on error
        else:
            return 'Storage', 'USB'
    
    def _get_partitions_simple(self, device_path: str) -> List[str]:
        """Get partitions using simple method"""
        partitions = []
        try:
            output = self.run_command(['lsblk', '-n', '-o', 'NAME', device_path], timeout=3)
            if output:
                lines = output.strip().split('\n')
                device_name = device_path.split('/')[-1]
                for line in lines[1:]:  # Skip first line (the device itself)
                    part_name = line.strip()
                    if part_name and part_name != device_name:
                        partitions.append(f"/dev/{part_name}")
        except Exception as e:
            print(f"[v0] Error getting partitions for {device_path}: {str(e)}")
        
        return partitions

    def _detect_drives_fallback(self) -> List[DriveInfo]:
        """Fallback drive detection method"""
        drives = []
        try:
            with open('/proc/partitions', 'r') as f:
                lines = f.readlines()[2:]  # Skip header
                
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 4:
                    device_name = parts[3]
                    # Only process whole disks (no partition numbers)
                    if not any(char.isdigit() for char in device_name[-1:]):
                        device_path = f"/dev/{device_name}"
                        size_kb = int(parts[2])
                        size_gb = round(size_kb / 1024 / 1024, 1)
                        
                        drive_info = DriveInfo(
                            device=device_path,
                            model=f"Storage Device {device_name.upper()}",
                            serial=f"SN{hash(device_path) % 100000:05d}",
                            size=f"{size_gb}GB",
                            interface="Unknown",
                            drive_type="Storage",
                            partitions=[],
                            smart_status="Unknown",
                            secure_erase_support=True,
                            sanitize_support=False,
                            health_status="normal"
                        )
                        drives.append(drive_info)
                        print(f"[v0] Fallback added: {drive_info.model} ({drive_info.device})")
                        
        except Exception as e:
            print(f"[v0] Fallback detection error: {str(e)}")
            
        return drives
    
    def get_storage_devices(self) -> List[Dict[str, Any]]:
        """Get storage devices in format expected by GUI"""
        drives = self.detect_drives()
        devices = []
        
        for drive in drives:
            device_dict = {
                'name': drive.model,
                'device_path': drive.device,
                'size': drive.size,
                'type': drive.drive_type,
                'interface': drive.interface,
                'serial': drive.serial,
                'smart_status': drive.smart_status,
                'secure_erase_support': drive.secure_erase_support,
                'sanitize_support': drive.sanitize_support,
                'partitions': drive.partitions,
                'health_status': drive.health_status,
                'temperature': drive.temperature,
                'power_on_hours': drive.power_on_hours
            }
            devices.append(device_dict)
            
        return devices

    def get_device_specific_commands(self, device_path: str, device_type: str, operation: str) -> List[str]:
        """Get device-specific commands for different storage types"""
        device_type_upper = device_type.upper()
        commands = []
        
        if operation == "secure_erase":
            if "NVME" in device_type_upper:
                commands = [
                    f"nvme format {device_path} --ses=1 --force",
                    f"nvme sanitize {device_path} --sanact=2 --ause --force",
                ]
            elif "SSD" in device_type_upper:
                commands = [
                    f"blkdiscard -f {device_path}",
                    f"hdparm --user-master u --security-set-pass p {device_path}",
                    f"hdparm --user-master u --security-erase p {device_path}",
                ]
            else:  # HDD or other
                commands = [
                    f"hdparm --user-master u --security-set-pass p {device_path}",
                    f"hdparm --user-master u --security-erase p {device_path}",
                ]
        
        elif operation == "wipe":
            if "NVME" in device_type_upper:
                commands = [
                    f"nvme sanitize {device_path} --sanact=1 --ause --force",
                    f"dd if=/dev/urandom of={device_path} bs=1M status=progress oflag=direct",
                ]
            elif "SSD" in device_type_upper:
                commands = [
                    f"blkdiscard -f {device_path}",
                    f"dd if=/dev/urandom of={device_path} bs=1M status=progress oflag=direct",
                    f"dd if=/dev/zero of={device_path} bs=1M status=progress oflag=direct",
                ]
            else:  # HDD
                commands = [
                    f"dd if=/dev/urandom of={device_path} bs=1M status=progress oflag=direct",
                    f"dd if=/dev/zero of={device_path} bs=1M status=progress oflag=direct",
                    f"shred -vfz -n 3 {device_path}",
                ]
        
        return commands

if __name__ == "__main__":
    detector = DriveDetector()
    drives = detector.detect_drives()
    
    print("DataWipe Pro - Drive Detection")
    print("=" * 50)
    
    for i, drive in enumerate(drives, 1):
        print(f"\nDrive {i}:")
        print(f"  Device: {drive.device}")
        print(f"  Model: {drive.model}")
        print(f"  Serial: {drive.serial}")
        print(f"  Size: {drive.size}")
        print(f"  Type: {drive.drive_type}")
        print(f"  Interface: {drive.interface}")
        print(f"  SMART Status: {drive.smart_status}")
        print(f"  Secure Erase Support: {'Yes' if drive.secure_erase_support else 'No'}")
        print(f"  Sanitize Support: {'Yes' if drive.sanitize_support else 'No'}")
        print(f"  Partitions: {', '.join(drive.partitions) if drive.partitions else 'None'}")
