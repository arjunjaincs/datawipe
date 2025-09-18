#!/usr/bin/env python3
"""
DataWipe Pro - Cross-Platform Launch Script
Team: Tejasway

Enhanced launcher with system checks, dependency validation, and professional startup.
Works on both Windows and Ubuntu/Linux.
"""

import os
import sys
import subprocess
import platform
import importlib.util

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("❌ ERROR: DataWipe Pro requires Python 3.8 or higher")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_admin_privileges():
    """Check if script is running with admin privileges (cross-platform)"""
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("❌ ERROR: DataWipe Pro requires administrator privileges on Windows")
                print("   Please run as administrator:")
                print("   Right-click Command Prompt → 'Run as administrator'")
                print(f"   Then run: python {' '.join(sys.argv)}")
                sys.exit(1)
            print("✅ Administrator privileges: Confirmed")
        except Exception:
            print("⚠️  WARNING: Could not verify administrator privileges")
            print("   Some features may not work properly")
    
    elif system in ["Linux", "Darwin"]:  # Darwin is macOS
        try:
            if os.geteuid() != 0:
                print("❌ ERROR: DataWipe Pro requires root privileges on Linux/macOS")
                print("   Please run with sudo:")
                print(f"   sudo python3 {' '.join(sys.argv)}")
                sys.exit(1)
            print("✅ Root privileges: Confirmed")
        except AttributeError:
            print("⚠️  WARNING: Could not verify root privileges")
            print("   Some features may not work properly")
    
    else:
        print(f"⚠️  WARNING: Unsupported system: {system}")
        print("   DataWipe Pro may not work correctly")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('PyQt5', 'PyQt5'),
        ('reportlab', 'reportlab'),
        ('qrcode', 'qrcode'),
        ('cryptography', 'cryptography'),
        ('psutil', 'psutil'),
        ('pyhanko', 'pyhanko'),
        ('jwcrypto', 'jwcrypto')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                missing_packages.append(package_name)
            else:
                print(f"✅ {package_name}: Available")
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ ERROR: Missing required packages: {', '.join(missing_packages)}")
        print("   Install with:")
        print(f"   pip install {' '.join(missing_packages)}")
        sys.exit(1)

def check_system_compatibility():
    """Check system compatibility"""
    system = platform.system()
    print(f"✅ System compatibility: {system} {platform.release()}")
    
    if system == "Windows":
        print("   Windows-specific features enabled")
    elif system in ["Linux", "Darwin"]:
        print("   Unix-specific features enabled")
    else:
        print("   ⚠️  Limited compatibility mode")

def display_banner():
    """Display professional startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                            🛡️  DataWipe Pro v2.0.0                           ║
║                                                                              ║
║                    Military-Grade Secure Data Erasure System                 ║
║                                                                              ║
║                              Team: Tejasway                                  ║
║                                                                              ║
║    🔒 NIST SP 800-88 Compliant  •  🧬 Quantum-Resistant  •  ⚡ AI-Powered    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 Initializing DataWipe Pro...
"""
    print(banner)

def main():
    """Main launcher function"""
    display_banner()
    
    print("🔍 Performing system checks...")
    check_python_version()
    check_admin_privileges()
    check_system_compatibility()
    check_dependencies()
    
    print("\n✅ All system checks passed!")
    print("🚀 Launching DataWipe Pro GUI...")
    print("=" * 80)
    
    # Import and run the GUI
    try:
        from main import main as gui_main
        gui_main()
    except KeyboardInterrupt:
        print("\n\n👋 DataWipe Pro shutdown requested by user")
        print("   Thank you for using DataWipe Pro!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to launch DataWipe Pro: {str(e)}")
        print("   Please check the error message above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
