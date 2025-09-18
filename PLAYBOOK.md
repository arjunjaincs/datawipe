# DataWipe Pro - Quick Start Playbook

## 🚀 Quick Start Commands

### Method 1: Automated Script (Recommended)
\`\`\`bash
# Make script executable
chmod +x start_gui.sh

# Launch GUI (will handle everything automatically)
sudo ./start_gui.sh
\`\`\`

### Method 2: Manual Setup
\`\`\`bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3-tk fonts-ubuntu fonts-dejavu-core

# 4. Launch GUI with root privileges
sudo python3 src/main.py --gui
\`\`\`

## 📋 Step-by-Step Demo Guide

### For SIH Presentation

1. **Setup (Before Demo)**
   \`\`\`bash
   chmod +x start_gui.sh
   sudo ./start_gui.sh
   \`\`\`

2. **Demo Flow**
   - GUI opens with clean, professional interface
   - Click "🔄" to refresh and detect storage devices
   - Select device from dropdown (shows device info)
   - Click "🗑️ SECURE WIPE" button
   - Confirm wipe operation
   - Watch progress bar and status updates
   - Certificate generation completes
   - View beautiful PDF certificate with QR code

3. **Key Features to Highlight**
   - NIST SP 800-88 compliance
   - MAC address tracking for audit trails
   - Blockchain-style verification chains
   - Temperature monitoring during wipe
   - Tamper-evident certificates
   - Professional UI design

## 🛠️ Troubleshooting

### Permission Errors
\`\`\`bash
# If you get permission denied errors:
sudo python3 src/main.py --gui
\`\`\`

### Font Issues
\`\`\`bash
# Install additional fonts:
sudo apt install fonts-liberation fonts-dejavu-extra
\`\`\`

### Virtual Environment Issues
\`\`\`bash
# Reset virtual environment:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## 🎯 Demo Script

**Opening:** "DataWipe Pro is a NIST-compliant secure data erasure solution designed for IT asset recycling and data security compliance."

**Features:**
1. "Professional interface with device detection"
2. "One-click secure wiping with real-time progress"
3. "Tamper-proof certificate generation with blockchain verification"
4. "Complete audit trail with MAC address tracking"

**Innovation:** "Our unique breadcrumb strategy ensures that even if someone attempts data recovery, they only find evidence that the device was properly wiped."

## 📁 Project Structure
\`\`\`
DataWipe Pro/
├── src/
│   ├── gui.py              # Modern GUI interface
│   ├── main.py             # Main application entry
│   ├── drive_detector.py   # Device detection
│   ├── wipe_engine.py      # Secure wiping logic
│   └── certificate_generator.py  # Certificate creation
├── start_gui.sh            # Quick start script
├── requirements.txt        # Python dependencies
├── PLAYBOOK.md            # This file
└── README.md              # Full documentation
\`\`\`

## 🏆 Success Metrics
- Clean, professional UI suitable for enterprise use
- Sub-5-second device detection
- Real-time progress tracking
- Tamper-proof certificate generation
- Full NIST SP 800-88 compliance
