"""
DataWipe Pro - Landing Screen
Team: Tejasway

Clean, professional dark theme landing screen.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

class LandingScreen(QWidget):
    start_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the clean dark landing screen UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Add top spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(15)
        
        # Logo
        logo_label = QLabel("🛡️")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 64px; margin: 15px 0;")
        header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("DataWipe Pro")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 36, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin: 10px 0;")
        header_layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_font = QFont("Arial", 12)
        version_label.setFont(version_font)
        version_label.setStyleSheet("""
            color: #888888; 
            background-color: #2a2a2a;
            border: 1px solid #444444;
            border-radius: 12px;
            padding: 6px 16px;
            margin: 8px 0;
        """)
        header_layout.addWidget(version_label)
        
        # Subtitle
        subtitle_label = QLabel("Military-Grade Secure Data Erasure")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #00bfff; margin: 15px 0;")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Features section
        features_frame = QFrame()
        features_frame.setFrameStyle(QFrame.NoFrame)
        features_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 15px;
            }
        """)
        
        features_layout = QVBoxLayout(features_frame)
        features_layout.setSpacing(12)
        features_layout.setContentsMargins(30, 25, 30, 25)
        
        features_title = QLabel("Key Features")
        features_title.setAlignment(Qt.AlignCenter)
        features_title.setFont(QFont("Arial", 16, QFont.Bold))
        features_title.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        features_layout.addWidget(features_title)
        
        features = [
            "✓ NIST SP 800-88 Compliant",
            "✓ Military-Grade 7-Pass Wiping", 
            "✓ Tamper-Proof Certificates",
            "✓ Blockchain Verification",
            "✓ Government-Approved Security"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Arial", 12))
            feature_label.setStyleSheet("""
                color: #cccccc; 
                padding: 6px 0;
                border-bottom: 1px solid #3a3a3a;
            """)
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_frame)
        
        # Start button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.start_button = QPushButton("Start Secure Wipe")
        self.start_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.start_button.setMinimumSize(300, 60)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #00bfff;
                color: #ffffff;
                border: none;
                border-radius: 30px;
                padding: 18px 35px;
            }
            QPushButton:hover {
                background-color: #0099cc;
            }
            QPushButton:pressed {
                background-color: #007399;
            }
        """)
        
        self.start_button.clicked.connect(self.on_start_clicked)
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
        
        # Add bottom spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Footer
        footer_label = QLabel("Team Tejasway • Securing India's Digital Future")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Arial", 11))
        footer_label.setStyleSheet("color: #666666; margin-top: 15px;")
        layout.addWidget(footer_label)
        
        self.setLayout(layout)
    
    def on_start_clicked(self):
        """Handle start button click"""
        if self.parent:
            self.parent.show_screen('device_selection')
