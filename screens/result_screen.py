"""
DataWipe Pro - Result/Certificate Screen
Team: Tejasway

Shows JSON summary, certificate download options, QR verification, and forensic verification.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTextEdit, QGridLayout,
                            QSpacerItem, QSizePolicy, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
import json
import qrcode
from io import BytesIO

class ResultScreen(QWidget):
    forensic_verification_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.wipe_data = {}
        self.certificate_data = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the result screen UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with success indicator
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Success icon
        success_icon = QLabel("✅")
        success_icon.setAlignment(Qt.AlignCenter)
        success_icon.setStyleSheet("font-size: 48px; margin-bottom: 10px;")
        header_layout.addWidget(success_icon)
        
        title_label = QLabel("Secure Wipe Completed Successfully")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Ubuntu", 24, QFont.Bold))
        title_label.setStyleSheet("color: #28A745; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        self.completion_time_label = QLabel("Completed at: --:--:--")
        self.completion_time_label.setAlignment(Qt.AlignCenter)
        self.completion_time_label.setFont(QFont("Ubuntu", 14))
        self.completion_time_label.setStyleSheet("color: #6C757D; margin-bottom: 20px;")
        header_layout.addWidget(self.completion_time_label)
        
        layout.addLayout(header_layout)
        
        # Main content area with two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left column - Certificate and QR
        left_column = QVBoxLayout()
        
        # Certificate section
        cert_frame = QFrame()
        cert_frame.setFrameStyle(QFrame.Box)
        cert_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E8;
                border: 2px solid #28A745;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        cert_layout = QVBoxLayout(cert_frame)
        
        cert_title = QLabel("🏆 Wipe Certificate Generated")
        cert_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        cert_title.setStyleSheet("color: #155724; margin-bottom: 15px;")
        cert_layout.addWidget(cert_title)
        
        # Certificate details
        self.cert_id_label = QLabel("Certificate ID: DWP-20241216-A1B2C3D4")
        self.cert_id_label.setFont(QFont("Ubuntu", 12))
        self.cert_id_label.setStyleSheet("color: #155724; margin: 5px 0;")
        cert_layout.addWidget(self.cert_id_label)
        
        self.blockchain_hash_label = QLabel("Blockchain Hash: 0x1a2b3c4d...")
        self.blockchain_hash_label.setFont(QFont("Ubuntu", 12))
        self.blockchain_hash_label.setStyleSheet("color: #155724; margin: 5px 0;")
        cert_layout.addWidget(self.blockchain_hash_label)
        
        # Download buttons
        download_layout = QHBoxLayout()
        
        self.download_pdf_button = QPushButton("📄 Download PDF")
        self.download_pdf_button.setFont(QFont("Ubuntu", 11))
        self.download_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.download_pdf_button.clicked.connect(self.download_pdf)
        download_layout.addWidget(self.download_pdf_button)
        
        self.download_json_button = QPushButton("📋 Download JSON")
        self.download_json_button.setFont(QFont("Ubuntu", 11))
        self.download_json_button.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.download_json_button.clicked.connect(self.download_json)
        download_layout.addWidget(self.download_json_button)
        
        cert_layout.addLayout(download_layout)
        left_column.addWidget(cert_frame)
        
        # QR Code section
        qr_frame = QFrame()
        qr_frame.setFrameStyle(QFrame.Box)
        qr_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        qr_layout = QVBoxLayout(qr_frame)
        
        qr_title = QLabel("📱 Verification QR Code")
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setFont(QFont("Ubuntu", 14, QFont.Bold))
        qr_title.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        qr_layout.addWidget(qr_title)
        
        # QR Code placeholder
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumSize(200, 200)
        self.qr_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #CED4DA;
                border-radius: 8px;
                background-color: #F8F9FA;
            }
        """)
        qr_layout.addWidget(self.qr_label)
        
        qr_info = QLabel("Scan to verify certificate authenticity")
        qr_info.setAlignment(Qt.AlignCenter)
        qr_info.setFont(QFont("Ubuntu", 10))
        qr_info.setStyleSheet("color: #6C757D; margin-top: 10px;")
        qr_layout.addWidget(qr_info)
        
        left_column.addWidget(qr_frame)
        
        content_layout.addLayout(left_column)
        
        # Right column - Summary and verification
        right_column = QVBoxLayout()
        
        # Wipe summary
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Box)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("📊 Wipe Summary")
        summary_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        summary_title.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        summary_layout.addWidget(summary_title)
        
        # Summary details will be populated dynamically
        self.summary_layout = QVBoxLayout()
        summary_layout.addLayout(self.summary_layout)
        
        right_column.addWidget(summary_frame)
        
        # Forensic verification section
        forensic_frame = QFrame()
        forensic_frame.setFrameStyle(QFrame.Box)
        forensic_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF3CD;
                border: 2px solid #FFEAA7;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        forensic_layout = QVBoxLayout(forensic_frame)
        
        forensic_title = QLabel("🔍 Forensic Verification")
        forensic_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        forensic_title.setStyleSheet("color: #856404; margin-bottom: 15px;")
        forensic_layout.addWidget(forensic_title)
        
        forensic_desc = QLabel(
            "Run additional forensic verification using fdisk, testdisk, and photorec "
            "to confirm data is completely unrecoverable."
        )
        forensic_desc.setFont(QFont("Ubuntu", 12))
        forensic_desc.setStyleSheet("color: #856404; margin-bottom: 15px;")
        forensic_desc.setWordWrap(True)
        forensic_layout.addWidget(forensic_desc)
        
        self.forensic_button = QPushButton("🔬 Run Forensic Verification")
        self.forensic_button.setFont(QFont("Ubuntu", 12, QFont.Bold))
        self.forensic_button.setMinimumHeight(40)
        self.forensic_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #E0A800;
            }
        """)
        self.forensic_button.clicked.connect(self.run_forensic_verification)
        forensic_layout.addWidget(self.forensic_button)
        
        right_column.addWidget(forensic_frame)
        
        content_layout.addLayout(right_column)
        layout.addWidget(QFrame())  # Spacer frame
        layout.addLayout(content_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        
        # View audit logs button
        self.audit_button = QPushButton("📋 View Audit Logs")
        self.audit_button.setFont(QFont("Ubuntu", 12))
        self.audit_button.setMinimumSize(150, 40)
        self.audit_button.setStyleSheet("""
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
        self.audit_button.clicked.connect(self.view_audit_logs)
        button_layout.addWidget(self.audit_button)
        
        # New wipe button
        self.new_wipe_button = QPushButton("🔄 Start New Wipe")
        self.new_wipe_button.setFont(QFont("Ubuntu", 12, QFont.Bold))
        self.new_wipe_button.setMinimumSize(150, 40)
        self.new_wipe_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.new_wipe_button.clicked.connect(self.start_new_wipe)
        button_layout.addWidget(self.new_wipe_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def display_results(self, wipe_data):
        """Display the wipe results"""
        self.wipe_data = wipe_data
        
        # Update completion time
        completion_time = wipe_data.get('completion_time', 'Unknown')
        self.completion_time_label.setText(f"Completed at: {completion_time}")
        
        # Generate mock certificate data
        self.certificate_data = {
            'certificate_id': 'DWP-20241216-A1B2C3D4',
            'blockchain_hash': '0x1a2b3c4d5e6f7890abcdef1234567890',
            'verification_url': 'https://verify.datawipe.pro/DWP-20241216-A1B2C3D4'
        }
        
        # Update certificate labels
        self.cert_id_label.setText(f"Certificate ID: {self.certificate_data['certificate_id']}")
        self.blockchain_hash_label.setText(f"Blockchain Hash: {self.certificate_data['blockchain_hash'][:20]}...")
        
        # Generate QR code
        self.generate_qr_code()
        
        # Update summary
        self.update_summary()
    
    def generate_qr_code(self):
        """Generate and display QR code for verification"""
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(self.certificate_data['verification_url'])
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to QPixmap
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            # Scale to fit label
            scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"QR code generation failed: {e}")
            self.qr_label.setText("QR Code\nGeneration\nFailed")
            self.qr_label.setAlignment(Qt.AlignCenter)
    
    def update_summary(self):
        """Update the wipe summary display"""
        # Clear existing summary
        for i in reversed(range(self.summary_layout.count())):
            self.summary_layout.itemAt(i).widget().setParent(None)
        
        # Add summary items
        device = self.wipe_data.get('device', {})
        summary_items = [
            ("Device:", device.get('device_path', 'Unknown')),
            ("Model:", device.get('model', 'Unknown')),
            ("Method:", self.wipe_data.get('method', 'Unknown')),
            ("Duration:", self.wipe_data.get('total_duration', 'Unknown')),
            ("Status:", "✅ SUCCESS" if self.wipe_data.get('status') == 'completed' else "❌ FAILED"),
            ("Verification:", "✅ PASSED" if self.wipe_data.get('verification_passed') else "❌ FAILED")
        ]
        
        for label_text, value_text in summary_items:
            item_layout = QHBoxLayout()
            
            label = QLabel(label_text)
            label.setFont(QFont("Ubuntu", 11, QFont.Bold))
            label.setStyleSheet("color: #495057;")
            label.setMinimumWidth(80)
            item_layout.addWidget(label)
            
            value = QLabel(value_text)
            value.setFont(QFont("Ubuntu", 11))
            value.setStyleSheet("color: #212529;")
            item_layout.addWidget(value)
            
            item_layout.addStretch()
            self.summary_layout.addLayout(item_layout)
    
    def download_pdf(self):
        """Handle PDF download"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Certificate PDF",
            f"DataWipe_Certificate_{self.certificate_data['certificate_id']}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            # Mock PDF generation
            QMessageBox.information(
                self,
                "Download Complete",
                f"Certificate PDF saved to:\n{file_path}\n\n"
                "Note: This is a prototype - actual PDF would be generated here."
            )
    
    def download_json(self):
        """Handle JSON download"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Certificate JSON", 
            f"DataWipe_Certificate_{self.certificate_data['certificate_id']}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                # Create mock certificate JSON
                cert_json = {
                    "certificate_id": self.certificate_data['certificate_id'],
                    "blockchain_hash": self.certificate_data['blockchain_hash'],
                    "verification_url": self.certificate_data['verification_url'],
                    "wipe_data": self.wipe_data,
                    "generated_at": "2024-12-16T10:48:20Z",
                    "signature": "mock_signature_here"
                }
                
                with open(file_path, 'w') as f:
                    json.dump(cert_json, f, indent=2)
                
                QMessageBox.information(
                    self,
                    "Download Complete", 
                    f"Certificate JSON saved to:\n{file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Download Failed",
                    f"Failed to save JSON file:\n{str(e)}"
                )
    
    def run_forensic_verification(self):
        """Run mock forensic verification"""
        self.forensic_button.setText("🔬 Running Verification...")
        self.forensic_button.setEnabled(False)
        
        # Simulate verification delay
        QTimer.singleShot(3000, self.forensic_verification_complete)
    
    def forensic_verification_complete(self):
        """Complete forensic verification"""
        self.forensic_button.setText("✅ Verification Complete")
        self.forensic_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
        """)
        
        QMessageBox.information(
            self,
            "Forensic Verification Complete",
            "✅ Forensic verification completed successfully!\n\n"
            "Results:\n"
            "• fdisk: No partition table found\n"
            "• testdisk: No recoverable data detected\n" 
            "• photorec: 0 files recovered\n\n"
            "Data is completely unrecoverable."
        )
    
    def view_audit_logs(self):
        """View audit logs"""
        if self.parent:
            self.parent.show_screen('audit')
    
    def start_new_wipe(self):
        """Start a new wipe process"""
        if self.parent:
            self.parent.show_screen('landing')
