"""
DataWipe Pro - Mock API for Prototype
Team: Tejasway

Provides mock API responses for demonstration.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any

class MockAPI:
    def __init__(self):
        self.mock_delay = 0.5  # Simulate network delay
    
    def detect_drives(self) -> Dict[str, Any]:
        """Mock /detect endpoint"""
        time.sleep(self.mock_delay)
        
        return {
            "status": "success",
            "drives": [
                {
                    "device": "/dev/sda",
                    "model": "Samsung SSD 970 EVO Plus",
                    "capacity": "500 GB",
                    "interface": "NVMe",
                    "type": "SSD"
                },
                {
                    "device": "/dev/sdb", 
                    "model": "CT500BX500SSD1",
                    "capacity": "500 GB",
                    "interface": "SATA",
                    "type": "SSD"
                }
            ]
        }
    
    def start_wipe(self, device: str, method: str) -> Dict[str, Any]:
        """Mock /wipe endpoint"""
        time.sleep(self.mock_delay)
        
        return {
            "status": "started",
            "wipe_id": str(uuid.uuid4()),
            "device": device,
            "method": method,
            "estimated_time": "15 minutes"
        }
    
    def get_wipe_progress(self, wipe_id: str) -> Dict[str, Any]:
        """Mock wipe progress"""
        time.sleep(self.mock_delay)
        
        # Simulate different progress states
        import random
        progress = random.randint(0, 100)
        
        phases = [
            "Detecting device",
            "Unhiding HPA/DCO sectors", 
            "Pass 1: Writing zeros",
            "Pass 2: Writing ones",
            "Pass 3: Random pattern",
            "Pass 4: Complement pattern",
            "Pass 5: Random pattern",
            "Pass 6: Zeros",
            "Pass 7: Random verification",
            "Verification complete"
        ]
        
        current_phase = min(int(progress / 10), len(phases) - 1)
        
        return {
            "status": "in_progress" if progress < 100 else "completed",
            "progress": progress,
            "current_phase": phases[current_phase],
            "phases_completed": current_phase,
            "total_phases": len(phases),
            "estimated_remaining": f"{max(0, 15 - int(progress * 0.15))} minutes"
        }
    
    def verify_wipe(self, wipe_id: str) -> Dict[str, Any]:
        """Mock /verify endpoint"""
        time.sleep(self.mock_delay)
        
        return {
            "status": "verified",
            "wipe_id": wipe_id,
            "verification_hash": "sha256:a1b2c3d4e5f6...",
            "forensic_check": "passed",
            "recovery_attempts": 0,
            "confidence": "100%"
        }
    
    def generate_certificate(self, wipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock /sign endpoint"""
        time.sleep(self.mock_delay)
        
        cert_id = f"DWP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        return {
            "status": "signed",
            "certificate_id": cert_id,
            "pdf_url": f"/certificates/{cert_id}.pdf",
            "json_url": f"/certificates/{cert_id}.json",
            "qr_code": f"https://verify.datawipe.pro/{cert_id}",
            "blockchain_hash": f"0x{uuid.uuid4().hex[:32]}",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_sample_logs(self) -> list:
        """Get sample wipe logs"""
        return [
            "[2024-12-16 10:30:15] INFO: Starting secure wipe process",
            "[2024-12-16 10:30:16] INFO: Device: /dev/sdb (CT500BX500SSD1)",
            "[2024-12-16 10:30:16] INFO: Method: NIST SP 800-88 (7-pass)",
            "[2024-12-16 10:30:17] INFO: Unmounting all partitions",
            "[2024-12-16 10:30:18] INFO: Starting Pass 1: Writing zeros",
            "[2024-12-16 10:32:45] INFO: Pass 1 completed (2m 27s)",
            "[2024-12-16 10:32:46] INFO: Starting Pass 2: Writing ones", 
            "[2024-12-16 10:35:12] INFO: Pass 2 completed (2m 26s)",
            "[2024-12-16 10:35:13] INFO: Starting Pass 3: Random pattern",
            "[2024-12-16 10:37:41] INFO: Pass 3 completed (2m 28s)",
            "[2024-12-16 10:37:42] INFO: Starting Pass 4: Complement pattern",
            "[2024-12-16 10:40:08] INFO: Pass 4 completed (2m 26s)",
            "[2024-12-16 10:40:09] INFO: Starting Pass 5: Random pattern",
            "[2024-12-16 10:42:37] INFO: Pass 5 completed (2m 28s)",
            "[2024-12-16 10:42:38] INFO: Starting Pass 6: Writing zeros",
            "[2024-12-16 10:45:04] INFO: Pass 6 completed (2m 26s)",
            "[2024-12-16 10:45:05] INFO: Starting Pass 7: Random verification",
            "[2024-12-16 10:47:33] INFO: Pass 7 completed (2m 28s)",
            "[2024-12-16 10:47:34] INFO: Starting verification phase",
            "[2024-12-16 10:48:15] INFO: Verification completed successfully",
            "[2024-12-16 10:48:16] SUCCESS: Secure wipe completed",
            "[2024-12-16 10:48:17] INFO: Generating certificate...",
            "[2024-12-16 10:48:20] INFO: Certificate generated: DWP-20241216-A1B2C3D4"
        ]
