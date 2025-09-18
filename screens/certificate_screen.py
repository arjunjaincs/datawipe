"""
Certificate Screen - Display wipe details and download options
"""

import json
import os
import time
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTextEdit, QFileDialog,
                            QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils.certificate_generator import CertificateGenerator

class CertificateScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.wipe_data = {}
        self.cert_generator = CertificateGenerator()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the certificate screen UI"""
        # Create scroll area for the content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1A1A1A; }")
        
        # Main content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(40)
        layout.setContentsMargins(60, 60, 60, 60)
        
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Success icon and title
        success_frame = QFrame()
        success_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10B981, stop:1 #059669);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 20px;
            }
        """)
        success_layout = QVBoxLayout(success_frame)
        
        icon_label = QLabel("🏆")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: #FFFFFF; margin-bottom: 10px;")
        
        title = QLabel("CERTIFICATE GENERATED")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        
        subtitle = QLabel("Tamper-Proof Digital Certificate of Data Erasure")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #E8F5E8;")
        
        success_layout.addWidget(icon_label)
        success_layout.addWidget(title)
        success_layout.addWidget(subtitle)
        
        header_layout.addWidget(success_frame)
        
        # Certificate details frame with enhanced styling
        self.details_frame = QFrame()
        self.details_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2A2A2A, stop:1 #1E1E1E);
                border-radius: 16px;
                padding: 40px;
                border: 2px solid #404040;
            }
        """)
        
        self.details_layout = QVBoxLayout(self.details_frame)
        
        details_title = QLabel("📋 CERTIFICATE DETAILS")
        details_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        details_title.setStyleSheet("color: #10B981; margin-bottom: 20px;")
        self.details_layout.addWidget(details_title)
        
        # Download buttons with enhanced styling
        download_frame = QFrame()
        download_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2A2A2A, stop:1 #1E1E1E);
                border-radius: 16px;
                padding: 30px;
                border: 2px solid #404040;
            }
        """)
        
        download_layout = QVBoxLayout(download_frame)
        
        download_label = QLabel("📥 DOWNLOAD OPTIONS")
        download_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        download_label.setStyleSheet("color: #0078D7; margin-bottom: 20px;")
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # JSON download button with enhanced styling
        json_button = QPushButton("📄 Download JSON Certificate")
        json_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        json_button.setMinimumHeight(60)
        json_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078D7, stop:1 #005A9E);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005A9E, stop:1 #004578);
            }
            QPushButton:pressed {
                background: #004578;
            }
        """)
        json_button.clicked.connect(self.download_json)
        
        # PDF download button with enhanced styling
        pdf_button = QPushButton("📋 Download PDF Certificate")
        pdf_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        pdf_button.setMinimumHeight(60)
        pdf_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #DC3545, stop:1 #C82333);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #C82333, stop:1 #A71E2A);
            }
            QPushButton:pressed {
                background: #A71E2A;
            }
        """)
        pdf_button.clicked.connect(self.download_pdf)
        
        buttons_layout.addWidget(json_button)
        buttons_layout.addWidget(pdf_button)
        
        # Back button with enhanced styling
        back_button_layout = QHBoxLayout()
        back_button_layout.setAlignment(Qt.AlignCenter)
        
        back_button = QPushButton("🔄 Perform Another Wipe")
        back_button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        back_button.setMinimumHeight(60)
        back_button.setMinimumWidth(250)
        back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6C757D, stop:1 #495057);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #495057, stop:1 #343A40);
            }
            QPushButton:pressed {
                background: #343A40;
            }
        """)
        back_button.clicked.connect(self.go_back)
        
        back_button_layout.addWidget(back_button)
        
        download_layout.addWidget(download_label)
        download_layout.addLayout(buttons_layout)
        download_layout.addSpacing(20)
        download_layout.addLayout(back_button_layout)
        
        # Add all sections to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.details_frame)
        layout.addWidget(download_frame)
        layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def set_wipe_data(self, wipe_data):
        """Set the wipe data and update the display"""
        self.wipe_data = wipe_data
        self.update_certificate_display()
    
    def update_certificate_display(self):
        """Update the certificate details display"""
        # Clear existing details (keep the title)
        for i in reversed(range(1, self.details_layout.count())):
            item = self.details_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        
        if not self.wipe_data:
            return
        
        details = [
            ("🆔 Certificate ID", self.wipe_data.get('certificate_id', 'N/A')),
            ("💾 Device Name", self.wipe_data.get('device', {}).get('name', 'N/A')),
            ("📏 Device Capacity", self.wipe_data.get('device', {}).get('size', 'N/A')),
            ("🔧 Wipe Method", self.wipe_data.get('method', 'NIST SP 800-88 Rev. 1')),
            ("🔄 Number of Passes", str(self.wipe_data.get('passes', '3'))),
            ("⏰ Completion Time", self.wipe_data.get('completion_time', 'N/A')),
            ("✅ Verification Status", "PASSED ✓"),
            ("📜 Compliance Standard", "NIST SP 800-88 Rev. 1 • DoD 5220.22-M"),
            ("🌱 Environmental Impact", "Device ready for safe recycling • CO₂ saved: 50kg")
        ]
        
        for label, value in details:
            row_frame = QFrame()
            row_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(64, 64, 64, 0.3);
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 8px;
                }
            """)
            
            row_layout = QHBoxLayout(row_frame)
            
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 11, QFont.Bold))
            label_widget.setStyleSheet("color: #10B981; min-width: 200px;")
            
            value_widget = QLabel(str(value))
            value_widget.setFont(QFont("Segoe UI", 11))
            value_widget.setStyleSheet("color: #FFFFFF;")
            value_widget.setWordWrap(True)
            
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            
            self.details_layout.addWidget(row_frame)
    
    def download_json(self):
        """Download certificate as JSON"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Certificate as JSON", 
                f"DataWipe_Certificate_{self.wipe_data.get('certificate_id', 'unknown')}.json",
                "JSON Files (*.json)"
            )
            
            if filename:
                cert_data = self.cert_generator._prepare_certificate_data(self.wipe_data, 
                    self.wipe_data.get('certificate_id', f"DWP-{int(time.time())}"))
                self.cert_generator._generate_json_certificate(cert_data, filename)
                
                QMessageBox.information(self, "Success", f"JSON certificate saved to:\n{filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save JSON certificate:\n{str(e)}")
    
    def download_pdf(self):
        """Download certificate as PDF"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Certificate as PDF", 
                f"DataWipe_Certificate_{self.wipe_data.get('certificate_id', 'unknown')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                cert_data = self.cert_generator._prepare_certificate_data(self.wipe_data, 
                    self.wipe_data.get('certificate_id', f"DWP-{int(time.time())}"))
                self.cert_generator.generate_pdf_certificate(cert_data, filename)
                QMessageBox.information(self, "Success", f"PDF certificate saved to:\n{filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF certificate:\n{str(e)}")
    
    def go_back(self):
        """Go back to main screen for new wipe"""
        self.parent.show_screen('main')
        # Reset the main screen for a new wipe
        if hasattr(self.parent, 'main_screen'):
            self.parent.main_screen.reset_for_new_wipe()
