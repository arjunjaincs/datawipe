"""
DataWipe Pro - Device Selection Screen
Team: Tejasway

Auto-detected device list with model, capacity, interface details.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QComboBox, QMessageBox,
                            QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class DeviceSelectionScreen(QWidget):
    device_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.detected_drives = []
        self.selected_device = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the device selection screen UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Select Storage Device")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Ubuntu", 24, QFont.Bold))
        title_label.setStyleSheet("color: #19376D; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Choose the device you want to securely wipe")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Ubuntu", 14))
        subtitle_label.setStyleSheet("color: #6C757D; margin-bottom: 20px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Device table
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels([
            "Device", "Model", "Serial", "Capacity", "Interface", "Type"
        ])
        
        # Style the table
        self.device_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                gridline-color: #E9ECEF;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #E9ECEF;
            }
            QTableWidget::item:selected {
                background-color: #345496;
                color: white;
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
        header = self.device_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.device_table.setSelectionMode(QTableWidget.SingleSelection)
        self.device_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.device_table)
        
        # Type correction section
        type_frame = QFrame()
        type_frame.setFrameStyle(QFrame.Box)
        type_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF3CD;
                border: 2px solid #FFEAA7;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        type_layout = QVBoxLayout(type_frame)
        
        type_warning = QLabel("⚠️ Device Type Detection")
        type_warning.setFont(QFont("Ubuntu", 14, QFont.Bold))
        type_warning.setStyleSheet("color: #856404; margin-bottom: 10px;")
        type_layout.addWidget(type_warning)
        
        type_help = QLabel(
            "If external USB bridge shows SSD as HDD, this affects wiping method selection. "
            "SSDs require different secure erase commands than traditional HDDs."
        )
        type_help.setFont(QFont("Ubuntu", 11))
        type_help.setStyleSheet("color: #856404; margin-bottom: 15px;")
        type_help.setWordWrap(True)
        type_layout.addWidget(type_help)
        
        # Type override section
        override_layout = QHBoxLayout()
        
        override_label = QLabel("Override detected type:")
        override_label.setFont(QFont("Ubuntu", 12, QFont.Bold))
        override_label.setStyleSheet("color: #856404;")
        override_layout.addWidget(override_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Auto-Detect", "HDD", "SSD", "NVMe"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #FFEAA7;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 120px;
            }
        """)
        override_layout.addWidget(self.type_combo)
        
        override_layout.addStretch()
        type_layout.addLayout(override_layout)
        
        layout.addWidget(type_frame)
        
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
        
        # Continue button
        self.continue_button = QPushButton("Continue →")
        self.continue_button.setFont(QFont("Ubuntu", 12, QFont.Bold))
        self.continue_button.setMinimumSize(150, 40)
        self.continue_button.setEnabled(False)
        self.continue_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover:enabled {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #CED4DA;
                color: #6C757D;
            }
        """)
        self.continue_button.clicked.connect(self.on_continue_clicked)
        button_layout.addWidget(self.continue_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_drive_list(self, drives):
        """Update the table with detected drives"""
        self.detected_drives = drives
        self.device_table.setRowCount(len(drives))
        
        for row, drive in enumerate(drives):
            # Device path
            device_item = QTableWidgetItem(drive.get('device_path', 'Unknown'))
            device_item.setFlags(device_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 0, device_item)
            
            # Model
            model_item = QTableWidgetItem(drive.get('model', 'Unknown'))
            model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 1, model_item)
            
            # Serial
            serial = drive.get('serial', 'Unknown')
            if len(serial) > 20:
                serial = serial[:17] + "..."
            serial_item = QTableWidgetItem(serial)
            serial_item.setFlags(serial_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 2, serial_item)
            
            # Capacity
            size = drive.get('size', 0)
            if size > 0:
                if size >= 1024**4:  # TB
                    capacity = f"{size / (1024**4):.1f} TB"
                elif size >= 1024**3:  # GB
                    capacity = f"{size / (1024**3):.1f} GB"
                else:
                    capacity = f"{size / (1024**2):.1f} MB"
            else:
                capacity = "Unknown"
            
            capacity_item = QTableWidgetItem(capacity)
            capacity_item.setFlags(capacity_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 3, capacity_item)
            
            # Interface
            interface_item = QTableWidgetItem(drive.get('interface', 'Unknown'))
            interface_item.setFlags(interface_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 4, interface_item)
            
            # Type
            device_type = drive.get('type', 'Unknown')
            type_item = QTableWidgetItem(device_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            
            # Color code by type
            if device_type == 'SSD':
                type_item.setBackground(QColor(220, 248, 198))  # Light green
            elif device_type == 'HDD':
                type_item.setBackground(QColor(179, 229, 252))  # Light blue
            elif device_type == 'NVMe':
                type_item.setBackground(QColor(255, 243, 205))  # Light yellow
            
            self.device_table.setItem(row, 5, type_item)
    
    def on_selection_changed(self):
        """Handle device selection change"""
        selected_rows = self.device_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self.detected_drives):
                self.selected_device = self.detected_drives[row].copy()
                
                # Apply type override if selected
                override_type = self.type_combo.currentText()
                if override_type != "Auto-Detect":
                    self.selected_device['type'] = override_type
                    self.selected_device['type_overridden'] = True
                
                self.continue_button.setEnabled(True)
            else:
                self.selected_device = None
                self.continue_button.setEnabled(False)
        else:
            self.selected_device = None
            self.continue_button.setEnabled(False)
    
    def on_back_clicked(self):
        """Handle back button click"""
        if self.parent:
            self.parent.show_screen('landing')
    
    def on_continue_clicked(self):
        """Handle continue button click"""
        if self.selected_device and self.parent:
            self.parent.set_current_device(self.selected_device)
            self.parent.show_screen('wipe_summary')
