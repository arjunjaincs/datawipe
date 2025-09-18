# DataWipe Pro - Usage Guide

This comprehensive guide covers all aspects of using DataWipe Pro for secure data erasure.

## Table of Contents

1. [Getting Started](#getting-started)
2. [GUI Application](#gui-application)
3. [Command Line Interface](#command-line-interface)
4. [Certificate Management](#certificate-management)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch

1. **Open Terminal** and navigate to the DataWipe Pro directory
2. **Launch the application:**
   \`\`\`bash
   python3 src/main.py --gui
   \`\`\`
3. **Grant permissions** when prompted for drive access

### Understanding the Interface

The DataWipe Pro GUI consists of several sections:

- **Header**: Application title and compliance information
- **System Status**: Current operation status and refresh controls
- **Device List**: Detected storage devices with selection options
- **Action Controls**: Selection management and wipe execution
- **Footer**: Version and team information

## GUI Application

### Drive Detection

#### Automatic Detection
- Drives are automatically detected when the application starts
- The system scans for all connected storage devices
- Detection includes HDDs, SSDs, NVMe drives, and USB devices

#### Manual Refresh
1. Click the **"🔄 Refresh Devices"** button
2. Wait for the scan to complete
3. New devices will appear in the list

#### Drive Information Display
Each detected drive shows:
- **Device Icon**: Visual indicator of drive type (💾 for SSD, 🖴 for HDD)
- **Model and Size**: Drive model name and capacity
- **Type and Interface**: Drive technology and connection type
- **Serial Number**: Unique device identifier
- **Device Path**: System device path (e.g., /dev/sda)

### Selecting Drives for Wiping

#### Individual Selection
1. **Check the box** next to each drive you want to wipe
2. **Review the selection** carefully
3. **Verify** you have backups of important data

#### Select All Option
1. **Check "Select All Devices"** to select all detected drives
2. **Use with extreme caution** - this will wipe ALL drives
3. **Uncheck individual drives** if needed

### Performing Secure Wipe

#### Pre-Wipe Checklist
- [ ] Verify you have selected the correct drives
- [ ] Confirm you have backups of all important data
- [ ] Ensure the system has stable power supply
- [ ] Close other applications to avoid interference

#### Wipe Process
1. **Click "🗑️ WIPE SELECTED DRIVES"**
2. **Read the confirmation dialog** carefully
3. **Verify the list** of drives to be wiped
4. **Click "Yes"** to proceed (THIS CANNOT BE UNDONE)
5. **Wait for completion** - do not interrupt the process

#### Progress Monitoring
During the wipe process:
- Status updates appear in the System Status section
- The wipe button shows "🔄 WIPING IN PROGRESS..."
- Progress messages indicate current operation phase
- Estimated completion time is displayed

### Certificate Generation

After successful wipe completion:

1. **Automatic Generation**: Certificates are created automatically
2. **File Locations**: 
   - PDF Certificate: `certificates/wipe_certificate_YYYYMMDD_HHMMSS.pdf`
   - JSON Data: `certificates/wipe_certificate_YYYYMMDD_HHMMSS.json`
3. **Certificate ID**: Unique identifier for verification
4. **QR Code**: Embedded for quick verification

## Command Line Interface

### Basic Commands

#### Launch GUI
\`\`\`bash
python3 src/main.py --gui
\`\`\`

#### Detect Drives
\`\`\`bash
# Basic detection
python3 src/main.py --detect

# With detailed information (requires sudo)
sudo python3 src/main.py --detect
\`\`\`

#### Generate Sample Certificate
\`\`\`bash
python3 src/main.py --sample-cert
\`\`\`

#### Verify Certificate
\`\`\`bash
python3 src/main.py --verify certificates/certificate.json
\`\`\`

### Advanced CLI Usage

#### Help Information
\`\`\`bash
python3 src/main.py --help
\`\`\`

#### Verbose Output
\`\`\`bash
python3 -v src/main.py --detect
\`\`\`

#### Debug Mode
\`\`\`bash
DATAWIPE_DEBUG=1 python3 src/main.py --gui
\`\`\`

## Certificate Management

### Understanding Certificates

DataWipe Pro generates two types of certificates:

1. **PDF Certificate**: Human-readable document with:
   - Certificate ID and generation timestamp
   - Wiped device details
   - Wipe method and compliance information
   - QR code for verification
   - Digital signature for tamper detection

2. **JSON Certificate**: Machine-readable data with:
   - Structured device information
   - Cryptographic signatures
   - Verification metadata
   - Compliance details

### Certificate Verification

#### Using CLI
\`\`\`bash
python3 src/main.py --verify path/to/certificate.json
\`\`\`

#### Manual Verification
1. **Check Certificate ID**: Ensure it matches expected format
2. **Verify Timestamp**: Confirm generation time is correct
3. **Validate Signature**: Use built-in verification tools
4. **QR Code Scan**: Use mobile device to verify URL

#### Verification Results
- **✅ Valid**: Certificate is authentic and unmodified
- **❌ Invalid**: Certificate has been tampered with or corrupted
- **⚠️ Warning**: Certificate format issues or missing data

### Certificate Storage

#### Default Location
\`\`\`
datawipe-pro/
└── certificates/
    ├── wipe_certificate_20240115_103000.pdf
    ├── wipe_certificate_20240115_103000.json
    └── sample_wipe_certificate.pdf
\`\`\`

#### Custom Storage
\`\`\`bash
# Set custom certificate directory
export DATAWIPE_CERT_PATH=/path/to/certificates
python3 src/main.py --gui
\`\`\`

#### Backup Recommendations
- **Store certificates securely** in multiple locations
- **Keep offline copies** for long-term archival
- **Document certificate IDs** for future reference
- **Maintain access logs** for audit purposes

## Security Best Practices

### Pre-Wipe Security

1. **Data Backup Verification**
   - Verify all backups are complete and accessible
   - Test backup restoration procedures
   - Document backup locations and access methods

2. **Authorization Confirmation**
   - Ensure you have proper authorization to wipe drives
   - Document approval from data owners
   - Follow organizational data handling policies

3. **Physical Security**
   - Secure the work area during wipe operations
   - Prevent unauthorized access to the system
   - Monitor the process continuously

### During Wipe Operations

1. **System Stability**
   - Ensure stable power supply (use UPS if available)
   - Close unnecessary applications
   - Monitor system temperature and performance

2. **Process Integrity**
   - Do not interrupt the wipe process
   - Avoid system hibernation or sleep modes
   - Monitor for error messages or warnings

3. **Documentation**
   - Record start and end times
   - Document any issues or anomalies
   - Maintain chain of custody records

### Post-Wipe Security

1. **Certificate Management**
   - Store certificates in secure locations
   - Implement access controls for certificate files
   - Create backup copies of certificates

2. **Verification Procedures**
   - Verify certificate integrity immediately
   - Test certificate verification processes
   - Document verification results

3. **Audit Trail**
   - Maintain detailed operation logs
   - Record certificate generation and verification
   - Document final disposition of wiped drives

## Troubleshooting

### Common Issues and Solutions

#### "No drives detected"
**Symptoms**: Empty device list, "No devices detected" message

**Solutions**:
1. Run with sudo privileges:
   \`\`\`bash
   sudo python3 src/main.py --detect
   \`\`\`
2. Check drive connections and power
3. Verify drives are recognized by system:
   \`\`\`bash
   lsblk
   sudo fdisk -l
   \`\`\`

#### GUI won't start
**Symptoms**: Error messages, blank window, crashes

**Solutions**:
1. Install GUI dependencies:
   \`\`\`bash
   sudo apt install python3-tk
   \`\`\`
2. Check font installation:
   \`\`\`bash
   sudo apt install fonts-ubuntu fonts-dejavu-core
   \`\`\`
3. Update font cache:
   \`\`\`bash
   sudo fc-cache -fv
   \`\`\`

#### Certificate generation fails
**Symptoms**: Error during certificate creation, missing files

**Solutions**:
1. Check directory permissions:
   \`\`\`bash
   mkdir -p certificates
   chmod 755 certificates
   \`\`\`
2. Verify Python dependencies:
   \`\`\`bash
   pip3 install -r requirements.txt
   \`\`\`
3. Check disk space availability

#### Wipe process hangs
**Symptoms**: Process stops responding, no progress updates

**Solutions**:
1. Check system resources (CPU, memory, disk I/O)
2. Verify drive health with SMART tools:
   \`\`\`bash
   sudo smartctl -H /dev/sdX
   \`\`\`
3. Restart application and retry

### Getting Additional Help

1. **Check System Logs**:
   \`\`\`bash
   journalctl -f
   dmesg | tail
   \`\`\`

2. **Enable Debug Mode**:
   \`\`\`bash
   DATAWIPE_DEBUG=1 python3 src/main.py --gui
   \`\`\`

3. **Verify Installation**:
   \`\`\`bash
   python3 -c "import tkinter, reportlab, qrcode; print('All imports successful')"
   \`\`\`

4. **Test Individual Components**:
   \`\`\`bash
   python3 src/drive_detector.py
   python3 src/certificate_generator.py
   \`\`\`

---

**Team Tejasway** | **DataWipe Pro Usage Guide**
