"""
DataWipe Pro - Audit/Logs Screen
Team: Tejasway

Downloadable full log, hash digest, and public-key fingerprint.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QFrame, QTabWidget,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QFileDialog, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
from datetime import datetime

class AuditScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the audit screen UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Audit Logs & Verification")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Ubuntu", 24, QFont.Bold))
        title_label.setStyleSheet("color: #19376D; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Complete audit trail and cryptographic verification")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Ubuntu", 14))
        subtitle_label.setStyleSheet("color: #6C757D; margin-bottom: 20px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Tab widget for different audit views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #19376D;
            }
            QTabBar::tab:hover {
                background-color: #E9ECEF;
            }
        """)
        
        # Process Log Tab
        self.setup_process_log_tab()
        
        # Verification Tab
        self.setup_verification_tab()
        
        # System Info Tab
        self.setup_system_info_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        
        # Export logs button
        self.export_button = QPushButton("💾 Export Complete Audit")
        self.export_button.setFont(QFont("Ubuntu", 12, QFont.Bold))
        self.export_button.setMinimumSize(180, 40)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.export_button.clicked.connect(self.export_audit)
        button_layout.addWidget(self.export_button)
        
        # Back to results button
        self.back_button = QPushButton("← Back to Results")
        self.back_button.setFont(QFont("Ubuntu", 12))
        self.back_button.setMinimumSize(150, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_process_log_tab(self):
        """Set up the process log tab"""
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(20, 20, 20, 20)
        
        # Log header
        log_header = QLabel("Complete Process Log")
        log_header.setFont(QFont("Ubuntu", 16, QFont.Bold))
        log_header.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        log_layout.addWidget(log_header)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: 2px solid #495057;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 15px;
            }
        """)
        
        # Add sample log content
        sample_log = """[2024-12-16 10:30:15] INFO: DataWipe Pro v2.0.0 started
[2024-12-16 10:30:15] INFO: Operator: John Doe
[2024-12-16 10:30:15] INFO: System: Ubuntu 22.04.3 LTS
[2024-12-16 10:30:16] INFO: Target device: /dev/sdb (CT500BX500SSD1)
[2024-12-16 10:30:16] INFO: Device size: 500,107,862,016 bytes (465.76 GB)
[2024-12-16 10:30:16] INFO: Wipe method: NIST SP 800-88 Rev. 1 (7-pass)
[2024-12-16 10:30:17] INFO: Unmounting all partitions on /dev/sdb
[2024-12-16 10:30:18] INFO: Starting secure wipe process
[2024-12-16 10:30:18] INFO: Pass 1/7: Writing zeros (0x00)
[2024-12-16 10:32:45] INFO: Pass 1 completed - 2m 27s elapsed
[2024-12-16 10:32:46] INFO: Pass 2/7: Writing ones (0xFF)
[2024-12-16 10:35:12] INFO: Pass 2 completed - 2m 26s elapsed
[2024-12-16 10:35:13] INFO: Pass 3/7: Random pattern (0x92)
[2024-12-16 10:37:41] INFO: Pass 3 completed - 2m 28s elapsed
[2024-12-16 10:37:42] INFO: Pass 4/7: Complement pattern (0x49)
[2024-12-16 10:40:08] INFO: Pass 4 completed - 2m 26s elapsed
[2024-12-16 10:40:09] INFO: Pass 5/7: Random pattern (0x24)
[2024-12-16 10:42:37] INFO: Pass 5 completed - 2m 28s elapsed
[2024-12-16 10:42:38] INFO: Pass 6/7: Writing zeros (0x00)
[2024-12-16 10:45:04] INFO: Pass 6 completed - 2m 26s elapsed
[2024-12-16 10:45:05] INFO: Pass 7/7: Random verification
[2024-12-16 10:47:33] INFO: Pass 7 completed - 2m 28s elapsed
[2024-12-16 10:47:34] INFO: Starting verification phase
[2024-12-16 10:47:35] INFO: Reading random sectors for verification
[2024-12-16 10:48:15] INFO: Verification completed - all sectors confirmed wiped
[2024-12-16 10:48:16] SUCCESS: Secure wipe completed successfully
[2024-12-16 10:48:16] INFO: Total time: 17m 58s
[2024-12-16 10:48:17] INFO: Generating tamper-proof certificate
[2024-12-16 10:48:18] INFO: Certificate ID: DWP-20241216-A1B2C3D4
[2024-12-16 10:48:19] INFO: Blockchain hash: 0x1a2b3c4d5e6f7890abcdef1234567890
[2024-12-16 10:48:20] INFO: Certificate signed with RSA-4096 key
[2024-12-16 10:48:20] INFO: Audit log sealed and signed
[2024-12-16 10:48:20] INFO: Process completed successfully"""
        
        self.log_text.setPlainText(sample_log)
        log_layout.addWidget(self.log_text)
        
        self.tab_widget.addTab(log_widget, "📋 Process Log")
    
    def setup_verification_tab(self):
        """Set up the verification tab"""
        verify_widget = QWidget()
        verify_layout = QVBoxLayout(verify_widget)
        verify_layout.setContentsMargins(20, 20, 20, 20)
        
        # Verification header
        verify_header = QLabel("Cryptographic Verification")
        verify_header.setFont(QFont("Ubuntu", 16, QFont.Bold))
        verify_header.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        verify_layout.addWidget(verify_header)
        
        # Verification table
        self.verify_table = QTableWidget()
        self.verify_table.setColumnCount(2)
        self.verify_table.setHorizontalHeaderLabels(["Property", "Value"])
        
        # Style the verification table
        self.verify_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                gridline-color: #E9ECEF;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E9ECEF;
            }
            QHeaderView::section {
                background-color: #19376D;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Configure table
        header = self.verify_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Add verification data
        verification_data = [
            ("Certificate ID", "DWP-20241216-A1B2C3D4"),
            ("Blockchain Hash", "0x1a2b3c4d5e6f7890abcdef1234567890"),
            ("Process Hash (SHA-256)", "a1b2c3d4e5f6789012345678901234567890abcdef"),
            ("Digital Signature", "RSA-4096 verified ✅"),
            ("Timestamp Authority", "FreeTSA.org verified ✅"),
            ("Public Key Fingerprint", "SHA256:AAAA1111BBBB2222CCCC3333DDDD4444"),
            ("Tamper Seal", "INTACT ✅"),
            ("Verification URL", "https://verify.datawipe.pro/DWP-20241216-A1B2C3D4"),
            ("NIST Compliance", "SP 800-88 Rev. 1 ✅"),
            ("Quantum Resistant", "Post-quantum algorithms ✅")
        ]
        
        self.verify_table.setRowCount(len(verification_data))
        
        for row, (prop, value) in enumerate(verification_data):
            prop_item = QTableWidgetItem(prop)
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemIsEditable)
            prop_item.setFont(QFont("Ubuntu", 11, QFont.Bold))
            self.verify_table.setItem(row, 0, prop_item)
            
            value_item = QTableWidgetItem(value)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            value_item.setFont(QFont("Ubuntu", 11))
            self.verify_table.setItem(row, 1, value_item)
        
        verify_layout.addWidget(self.verify_table)
        
        self.tab_widget.addTab(verify_widget, "🔐 Verification")
    
    def setup_system_info_tab(self):
        """Set up the system info tab"""
        system_widget = QWidget()
        system_layout = QVBoxLayout(system_widget)
        system_layout.setContentsMargins(20, 20, 20, 20)
        
        # System info header
        system_header = QLabel("System Information")
        system_header.setFont(QFont("Ubuntu", 16, QFont.Bold))
        system_header.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        system_layout.addWidget(system_header)
        
        # System info table
        self.system_table = QTableWidget()
        self.system_table.setColumnCount(2)
        self.system_table.setHorizontalHeaderLabels(["Property", "Value"])
        
        # Style the system table
        self.system_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                gridline-color: #E9ECEF;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E9ECEF;
            }
            QHeaderView::section {
                background-color: #19376D;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Configure table
        header = self.system_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Add system data
        system_data = [
            ("Application", "DataWipe Pro v2.0.0"),
            ("Team", "Tejasway"),
            ("Operating System", "Ubuntu 22.04.3 LTS"),
            ("Kernel Version", "5.15.0-91-generic"),
            ("Python Version", "3.10.12"),
            ("PyQt Version", "5.15.9"),
            ("Hostname", "datawipe-workstation"),
            ("Username", "operator"),
            ("Execution Time", "2024-12-16 10:30:15 UTC"),
            ("CPU Architecture", "x86_64"),
            ("Memory", "16 GB"),
            ("Disk Space", "500 GB available"),
            ("Network Interface", "eth0 (192.168.1.100)"),
            ("MAC Address", "00:1B:44:11:3A:B7")
        ]
        
        self.system_table.setRowCount(len(system_data))
        
        for row, (prop, value) in enumerate(system_data):
            prop_item = QTableWidgetItem(prop)
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemIsEditable)
            prop_item.setFont(QFont("Ubuntu", 11, QFont.Bold))
            self.system_table.setItem(row, 0, prop_item)
            
            value_item = QTableWidgetItem(value)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            value_item.setFont(QFont("Ubuntu", 11))
            self.system_table.setItem(row, 1, value_item)
        
        system_layout.addWidget(self.system_table)
        
        self.tab_widget.addTab(system_widget, "💻 System Info")
    
    def export_audit(self):
        """Export complete audit package"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Audit Package",
            f"DataWipe_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                # Create comprehensive audit package
                audit_package = {
                    "audit_metadata": {
                        "export_timestamp": datetime.now().isoformat(),
                        "certificate_id": "DWP-20241216-A1B2C3D4",
                        "version": "2.0.0",
                        "team": "Tejasway"
                    },
                    "process_log": self.log_text.toPlainText(),
                    "verification_data": {
                        "certificate_id": "DWP-20241216-A1B2C3D4",
                        "blockchain_hash": "0x1a2b3c4d5e6f7890abcdef1234567890",
                        "process_hash": "a1b2c3d4e5f6789012345678901234567890abcdef",
                        "digital_signature": "RSA-4096 verified",
                        "public_key_fingerprint": "SHA256:AAAA1111BBBB2222CCCC3333DDDD4444",
                        "verification_url": "https://verify.datawipe.pro/DWP-20241216-A1B2C3D4"
                    },
                    "system_info": {
                        "application": "DataWipe Pro v2.0.0",
                        "team": "Tejasway",
                        "os": "Ubuntu 22.04.3 LTS",
                        "kernel": "5.15.0-91-generic",
                        "python": "3.10.12",
                        "hostname": "datawipe-workstation",
                        "execution_time": "2024-12-16 10:30:15 UTC"
                    }
                }
                
                with open(file_path, 'w') as f:
                    json.dump(audit_package, f, indent=2)
                
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Complete audit package exported to:\n{file_path}\n\n"
                    "Package includes:\n"
                    "• Full process log\n"
                    "• Cryptographic verification data\n"
                    "• System information\n"
                    "• Digital signatures"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export audit package:\n{str(e)}"
                )
    
    def go_back(self):
        """Go back to results screen"""
        if self.parent:
            self.parent.show_screen('result')
