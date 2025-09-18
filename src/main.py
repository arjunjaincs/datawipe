#!/usr/bin/env python3
"""
DataWipe Pro - Main Application
Team: Tejasway
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drive_detector import DriveDetector
from certificate_generator import CertificateGenerator

class DataWipePro:
    def __init__(self):
        self.detector = DriveDetector()
        self.cert_generator = CertificateGenerator()
    
    def detect_drives(self):
        """Detect and display all drives"""
        print("DataWipe Pro - Drive Detection")
        print("=" * 60)
        print("Team: Tejasway")
        print("Version: 1.0.0")
        print("=" * 60)
        
        drives = self.detector.detect_drives()
        
        if not drives:
            print("No drives detected. Make sure you have proper permissions.")
            print("Try running with: sudo python3 src/main.py --detect")
            return
        
        print(f"\nFound {len(drives)} storage device(s):\n")
        
        for i, drive in enumerate(drives, 1):
            print(f"Drive {i}: {drive.device}")
            print(f"   Model: {drive.model}")
            print(f"   Serial: {drive.serial}")
            print(f"   Size: {drive.size}")
            print(f"   Type: {drive.drive_type} ({drive.interface})")
            print(f"   SMART: {drive.smart_status}")
            
            # Security capabilities
            security_features = []
            if drive.secure_erase_support:
                security_features.append("Secure Erase")
            if drive.sanitize_support:
                security_features.append("Sanitize")
            
            if security_features:
                print(f"   Security: {', '.join(security_features)}")
            else:
                print(f"   Security: Limited (basic overwrite only)")
            
            if drive.partitions:
                print(f"   Partitions: {', '.join(drive.partitions)}")
            else:
                print(f"   Partitions: None")
            
            print()
        
        print("IMPORTANT: Wiping functionality will be implemented in next phase")
        print("All wipes will be NIST SP 800-88 compliant with tamper-proof certificates")
    
    def generate_sample_certificate(self):
        """Generate a sample certificate for demonstration"""
        print("Generating sample wipe certificate...")
        
        sample_wipe_data = {
            "devices": [{
                "device": "/dev/sda",
                "model": "Samsung SSD 970 EVO (500GB)",
                "serial": "S5H2NS0N123456",
                "size": "500GB",
                "type": "NVMe SSD",
                "interface": "NVMe"
            }],
            "method": "NIST SP 800-88 Rev. 1 - Clear/Purge",
            "passes": 3,
            "duration": "00:45:32",
            "status": "COMPLETED",
            "timestamp": "2024-01-15T10:30:00Z",
            "compliance_standard": "NIST SP 800-88",
            "verification": "PASSED"
        }
        
        os.makedirs("certificates", exist_ok=True)
        
        result = self.cert_generator.generate_certificate(
            sample_wipe_data, 
            "certificates/sample_wipe_certificate"
        )
        
        print(f"Certificate generated:")
        print(f"   PDF: {result['pdf_path']}")
        print(f"   JSON: {result['json_path']}")
        print(f"   ID: {result['certificate_id']}")
    
    def verify_certificate(self, cert_path: str):
        """Verify a certificate"""
        print(f"Verifying certificate: {cert_path}")
        
        if self.cert_generator.verify_certificate(cert_path):
            print("Certificate is valid and tamper-proof")
        else:
            print("Certificate verification failed")
    
    def launch_gui(self):
        """Launch the GUI application with root privilege check"""
        if os.geteuid() != 0:
            print("=" * 60)
            print("DataWipe Pro requires root privileges to access storage devices.")
            print("=" * 60)
            print("Please run with sudo:")
            print(f"sudo python3 {' '.join(sys.argv)}")
            print("\nAlternatively, use the quick start script:")
            print("sudo ./start_gui.sh")
            print("=" * 60)
            sys.exit(1)
        
        try:
            from gui import DataWipeProGUI
            print("Launching DataWipe Pro GUI...")
            app = DataWipeProGUI()
            app.run()
        except ImportError as e:
            print(f"GUI dependencies not available: {e}")
            print("Install required packages:")
            print("  sudo apt update")
            print("  sudo apt install python3-tk fonts-ubuntu fonts-dejavu-core")
            print("  pip3 install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            print(f"Failed to launch GUI: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="DataWipe Pro - Secure Data Wiping Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 src/main.py --gui          Launch GUI application
  sudo python3 src/main.py --detect       Detect drives (CLI mode)
  python3 src/main.py --sample-cert       Generate sample certificate
  python3 src/main.py --verify cert.json  Verify certificate

For drive operations, run with sudo for proper permissions.
        """
    )
    parser.add_argument('--detect', action='store_true', help='Detect connected drives')
    parser.add_argument('--sample-cert', action='store_true', help='Generate sample certificate')
    parser.add_argument('--verify', type=str, help='Verify certificate file')
    parser.add_argument('--gui', action='store_true', help='Launch GUI application')
    
    args = parser.parse_args()
    
    # Check if running as root for drive detection
    if args.detect and os.geteuid() != 0:
        print("Warning: Running without root privileges. Some drive information may be limited.")
        print("For complete drive information, run: sudo python3 src/main.py --detect")
    
    app = DataWipePro()
    
    if args.gui:
        app.launch_gui()
    elif args.detect:
        app.detect_drives()
    elif args.sample_cert:
        app.generate_sample_certificate()
    elif args.verify:
        app.verify_certificate(args.verify)
    else:
        print("DataWipe Pro - Secure Data Wiping Tool")
        print("Team: Tejasway | Version: 1.0.0")
        print("\nUsage:")
        print("  --gui          Launch GUI application (default)")
        print("  --detect       Detect drives (CLI mode)")
        print("  --sample-cert  Generate sample certificate")
        print("  --verify FILE  Verify certificate")
        print("\nLaunching GUI...")
        app.launch_gui()

if __name__ == "__main__":
    main()
