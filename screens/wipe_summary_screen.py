"""
DataWipe Pro - Wipe Summary Screen
Team: Tejasway

Shows selected device, recommended wipe method, time estimate, and options.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QCheckBox, QLineEdit,
                            QComboBox, QTextEdit, QSpacerItem, QSizePolicy,
                            QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

class WipeSummaryScreen(QWidget):
    wipe_started = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_device = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the wipe summary screen UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Wipe Configuration Summary")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Ubuntu", 24, QFont.Bold))
        title_label.setStyleSheet("color: #19376D; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Review settings before starting secure wipe")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Ubuntu", 14))
        subtitle_label.setStyleSheet("color: #6C757D; margin-bottom: 20px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Device info section
        device_frame = QFrame()
        device_frame.setFrameStyle(QFrame.Box)
        device_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        device_layout = QVBoxLayout(device_frame)
        
        device_title = QLabel("Selected Device")
        device_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        device_title.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        device_layout.addWidget(device_title)
        
        # Device details will be populated when device is selected
        self.device_info_layout = QVBoxLayout()
        device_layout.addLayout(self.device_info_layout)
        
        layout.addWidget(device_frame)
        
        # Wipe method section
        method_frame = QFrame()
        method_frame.setFrameStyle(QFrame.Box)
        method_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E8;
                border: 2px solid #28A745;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        method_layout = QVBoxLayout(method_frame)
        
        method_title = QLabel("Recommended Wipe Method")
        method_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        method_title.setStyleSheet("color: #155724; margin-bottom: 15px;")
        method_layout.addWidget(method_title)
        
        # Method selection
        method_selection_layout = QHBoxLayout()
        
        method_label = QLabel("Method:")
        method_label.setFont(QFont("Ubuntu", 12, QFont.Bold))
        method_label.setStyleSheet("color: #155724;")
        method_selection_layout.addWidget(method_label)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "NIST SP 800-88 (7-pass) - Recommended",
            "DoD 5220.22-M (3-pass) - Standard", 
            "Single Pass (Zeros) - Quick",
            "Hardware Secure Erase - Fast"
        ])
        self.method_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #28A745;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 300px;
                font-size: 12px;
            }
        """)
        self.method_combo.currentTextChanged.connect(self.update_time_estimate)
        method_selection_layout.addWidget(self.method_combo)
        
        method_selection_layout.addStretch()
        method_layout.addLayout(method_selection_layout)
        
        # Time estimate
        self.time_estimate_label = QLabel("Estimated Time: 15-20 minutes")
        self.time_estimate_label.setFont(QFont("Ubuntu", 12))
        self.time_estimate_label.setStyleSheet("color: #155724; margin-top: 10px;")
        method_layout.addWidget(self.time_estimate_label)
        
        layout.addWidget(method_frame)
        
        # Options section
        options_frame = QFrame()
        options_frame.setFrameStyle(QFrame.Box)
        options_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        options_layout = QVBoxLayout(options_frame)
        
        options_title = QLabel("Advanced Options")
        options_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        options_title.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        options_layout.addWidget(options_title)
        
        # Checkboxes for options
        self.hpa_checkbox = QCheckBox("Include hidden areas (HPA/DCO)")
        self.hpa_checkbox.setChecked(True)
        self.hpa_checkbox.setFont(QFont("Ubuntu", 12))
        self.hpa_checkbox.setStyleSheet("color: #212529; margin: 5px 0;")
        options_layout.addWidget(self.hpa_checkbox)
        
        self.cert_checkbox = QCheckBox("Generate signed certificate (PDF + JSON)")
        self.cert_checkbox.setChecked(True)
        self.cert_checkbox.setFont(QFont("Ubuntu", 12))
        self.cert_checkbox.setStyleSheet("color: #212529; margin: 5px 0;")
        options_layout.addWidget(self.cert_checkbox)
        
        self.verify_checkbox = QCheckBox("Run forensic verification after wipe")
        self.verify_checkbox.setChecked(True)
        self.verify_checkbox.setFont(QFont("Ubuntu", 12))
        self.verify_checkbox.setStyleSheet("color: #212529; margin: 5px 0;")
        options_layout.addWidget(self.verify_checkbox)
        
        # Operator name field
        operator_layout = QHBoxLayout()
        operator_label = QLabel("Operator Name (optional):")
        operator_label.setFont(QFont("Ubuntu", 12))
        operator_label.setStyleSheet("color: #212529;")
        operator_layout.addWidget(operator_label)
        
        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("Enter operator name for certificate")
        self.operator_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #CED4DA;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #19376D;
            }
        """)
        operator_layout.addWidget(self.operator_input)
        
        options_layout.addLayout(operator_layout)
        
        layout.addWidget(options_frame)
        
        # Warning section
        warning_frame = QFrame()
        warning_frame.setFrameStyle(QFrame.Box)
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #F8D7DA;
                border: 2px solid #DC3545;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        warning_layout = QVBoxLayout(warning_frame)
        
        warning_title = QLabel("⚠️ IMPORTANT WARNING")
        warning_title.setFont(QFont("Ubuntu", 14, QFont.Bold))
        warning_title.setStyleSheet("color: #721C24; margin-bottom: 10px;")
        warning_layout.addWidget(warning_title)
        
        warning_text = QLabel(
            "This operation will PERMANENTLY DESTROY all data on the selected device. "
            "This action cannot be undone. Ensure you have backed up any important data."
        )
        warning_text.setFont(QFont("Ubuntu", 12))
        warning_text.setStyleSheet("color: #721C24;")
        warning_text.setWordWrap(True)
        warning_layout.addWidget(warning_text)
        
        layout.addWidget(warning_frame)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setFont(QFont("Ubuntu", 12))
        self.back_button.setMinimumSize(120, 40)
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
        self.back_button.clicked.connect(self.on_back_clicked)
        button_layout.addWidget(self.back_button)
        
        # Start wipe button
        self.wipe_button = QPushButton("🔥 START WIPE")
        self.wipe_button.setFont(QFont("Ubuntu", 14, QFont.Bold))
        self.wipe_button.setMinimumSize(200, 50)
        self.wipe_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #BD2130;
            }
        """)
        self.wipe_button.clicked.connect(self.on_wipe_clicked)
        button_layout.addWidget(self.wipe_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def showEvent(self, event):
        """Called when screen is shown - update device info"""
        super().showEvent(event)
        if self.parent:
            device = self.parent.get_current_device()
            if device:
                self.update_device_info(device)
    
    def update_device_info(self, device):
        """Update the device information display"""
        self.current_device = device
        
        # Clear existing device info
        for i in reversed(range(self.device_info_layout.count())):
            self.device_info_layout.itemAt(i).widget().setParent(None)
        
        # Add device details
        details = [
            ("Device Path:", device.get('device_path', 'Unknown')),
            ("Model:", device.get('model', 'Unknown')),
            ("Serial Number:", device.get('serial', 'Unknown')),
            ("Capacity:", self.format_size(device.get('size', 0))),
            ("Interface:", device.get('interface', 'Unknown')),
            ("Type:", device.get('type', 'Unknown'))
        ]
        
        for label_text, value_text in details:
            detail_layout = QHBoxLayout()
            
            label = QLabel(label_text)
            label.setFont(QFont("Ubuntu", 12, QFont.Bold))
            label.setStyleSheet("color: #495057;")
            label.setMinimumWidth(120)
            detail_layout.addWidget(label)
            
            value = QLabel(value_text)
            value.setFont(QFont("Ubuntu", 12))
            value.setStyleSheet("color: #212529;")
            detail_layout.addWidget(value)
            
            detail_layout.addStretch()
            self.device_info_layout.addLayout(detail_layout)
        
        # Update recommended method based on device type
        device_type = device.get('type', 'HDD')
        if device_type == 'NVMe':
            self.method_combo.setCurrentIndex(3)  # Hardware Secure Erase
        elif device_type == 'SSD':
            self.method_combo.setCurrentIndex(0)  # NIST 7-pass
        else:
            self.method_combo.setCurrentIndex(1)  # DoD 3-pass
    
    def format_size(self, size_bytes):
        """Format size in bytes to human readable"""
        if size_bytes == 0:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def update_time_estimate(self):
        """Update time estimate based on selected method"""
        method = self.method_combo.currentText()
        
        if "7-pass" in method:
            self.time_estimate_label.setText("Estimated Time: 15-25 minutes")
        elif "3-pass" in method:
            self.time_estimate_label.setText("Estimated Time: 8-12 minutes")
        elif "Single Pass" in method:
            self.time_estimate_label.setText("Estimated Time: 3-5 minutes")
        elif "Hardware" in method:
            self.time_estimate_label.setText("Estimated Time: 1-3 minutes")
    
    def on_back_clicked(self):
        """Handle back button click"""
        if self.parent:
            self.parent.show_screen('device_selection')
    
    def on_wipe_clicked(self):
        """Handle wipe button click with confirmation"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            'Confirm Secure Wipe',
            f'Are you sure you want to permanently wipe all data on:\n\n'
            f'{self.current_device.get("device_path", "Unknown")} '
            f'({self.current_device.get("model", "Unknown")})\n\n'
            f'This action cannot be undone!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Prepare wipe configuration
            wipe_config = {
                'device': self.current_device,
                'method': self.method_combo.currentText(),
                'include_hpa': self.hpa_checkbox.isChecked(),
                'generate_certificate': self.cert_checkbox.isChecked(),
                'run_verification': self.verify_checkbox.isChecked(),
                'operator_name': self.operator_input.text().strip() or 'Unknown'
            }
            
            # Start wipe process
            if self.parent:
                self.parent.start_wipe_process(wipe_config)
