#!/usr/bin/env python3
"""
DataWipe Pro - Sleek Professional UI
Team: Tejasway

Modern dark-themed application with professional design matching the reference UI.
"""

import sys
import os
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Import our screen modules
from screens.main_screen import MainScreen
from screens.certificate_screen import CertificateScreen
from utils.drive_detector import DriveDetector
from utils.mock_api import MockAPI

class DataWipeProApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataWipe Pro - Military-Grade Secure Data Erasure")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Initialize components
        self.drive_detector = DriveDetector()
        self.mock_api = MockAPI()
        self.current_device = None
        self.wipe_data = {}
        
        # Set up the UI
        self.setup_modern_theme()
        self.setup_ui()
        
        # Start drive detection
        self.start_drive_detection()
    
    def setup_modern_theme(self):
        """Apply sleek modern dark theme matching the reference design"""
        font = QFont("Arial", 10)  # Use Arial instead of Inter for better compatibility
        font.setWeight(QFont.Medium)
        self.setFont(font)
        
        # High DPI attributes are set before QApplication is created in main()
        
        palette = QPalette()
        
        # Professional dark theme colors matching reference
        navy_bg = QColor(15, 23, 42)          # #0F172A - Dark navy background
        darker_navy = QColor(8, 15, 31)       # #080F1F - Darker navy for cards
        card_bg = QColor(30, 41, 59)          # #1E293B - Card backgrounds
        light_text = QColor(248, 250, 252)    # #F8FAFC - Primary text
        gray_text = QColor(148, 163, 184)     # #94A3B8 - Secondary text
        green_accent = QColor(34, 197, 94)    # #22C55E - Green accent
        blue_accent = QColor(59, 130, 246)    # #3B82F6 - Blue accent
        
        palette.setColor(QPalette.Window, navy_bg)
        palette.setColor(QPalette.WindowText, light_text)
        palette.setColor(QPalette.Base, darker_navy)
        palette.setColor(QPalette.AlternateBase, card_bg)
        palette.setColor(QPalette.ToolTipBase, darker_navy)
        palette.setColor(QPalette.ToolTipText, light_text)
        palette.setColor(QPalette.Text, light_text)
        palette.setColor(QPalette.Button, card_bg)
        palette.setColor(QPalette.ButtonText, light_text)
        palette.setColor(QPalette.BrightText, light_text)
        palette.setColor(QPalette.Link, blue_accent)
        palette.setColor(QPalette.Highlight, green_accent)
        palette.setColor(QPalette.HighlightedText, navy_bg)
        
        self.setPalette(palette)
        
        # Store colors for use in screens
        self.colors = {
            'navy_bg': navy_bg,
            'darker_navy': darker_navy,
            'card_bg': card_bg,
            'light_text': light_text,
            'gray_text': gray_text,
            'green_accent': green_accent,
            'blue_accent': blue_accent
        }
        
        # Apply modern window styling with custom title bar
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A, stop:1 #1E293B);
                border: 2px solid #374151;
                border-radius: 15px;
            }
        """)
    
    def setup_ui(self):
        """Set up the modern UI with custom title bar"""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E293B, stop:1 #334155);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                border-bottom: 1px solid #475569;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 10, 0)
        
        # App title and icon
        title_label = QLabel("🛡️ DataWipe Pro - Military-Grade Secure Data Erasure")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))  # Use Arial instead of Inter for better compatibility
        title_label.setStyleSheet("color: #F8FAFC;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Window controls
        minimize_btn = QPushButton("−")
        maximize_btn = QPushButton("□")
        close_btn = QPushButton("×")
        
        for btn in [minimize_btn, maximize_btn, close_btn]:
            btn.setFixedSize(35, 35)
            btn.setFont(QFont("Arial", 14, QFont.Bold))  # Use Arial instead of Inter for better compatibility
            
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #374151;
                color: #F8FAFC;
            }
        """)
        
        maximize_btn.setStyleSheet(minimize_btn.styleSheet())
        
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: white;
            }
        """)
        
        minimize_btn.clicked.connect(self.showMinimized)
        maximize_btn.clicked.connect(self.toggle_maximize)
        close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(minimize_btn)
        title_layout.addWidget(maximize_btn)
        title_layout.addWidget(close_btn)
        
        # Content area
        self.stacked_widget = QStackedWidget()
        
        # Create screens with modern styling
        self.main_screen = MainScreen(self)
        self.certificate_screen = CertificateScreen(self)
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.main_screen)        # Index 0
        self.stacked_widget.addWidget(self.certificate_screen) # Index 1
        
        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.stacked_widget)
        
        # Start with main screen
        self.show_screen('main')
        
        # Enable dragging
        self.drag_position = None
        title_bar.mousePressEvent = self.mouse_press_event
        title_bar.mouseMoveEvent = self.mouse_move_event
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def mouse_press_event(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouse_move_event(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def start_drive_detection(self):
        """Start background drive detection"""
        self.drive_timer = QTimer()
        self.drive_timer.timeout.connect(self.refresh_drives)
        self.drive_timer.start(5000)  # Refresh every 5 seconds
        
        # Initial detection
        self.refresh_drives()
    
    def refresh_drives(self):
        """Refresh the list of detected drives"""
        try:
            drives = self.drive_detector.get_storage_devices()
            # Update main screen with new drives
            if hasattr(self, 'main_screen'):
                self.main_screen.update_drive_list(drives)
        except Exception as e:
            print(f"Drive detection error: {e}")
    
    def show_screen(self, screen_name):
        """Navigate between the 2 screens"""
        screen_map = {
            'main': 0,
            'certificate': 1
        }
        
        if screen_name in screen_map:
            self.stacked_widget.setCurrentIndex(screen_map[screen_name])

    def wipe_completed(self, wipe_data):
        """Handle wipe completion and show certificate screen"""
        self.wipe_data = wipe_data
        self.certificate_screen.set_wipe_data(wipe_data)
        self.show_screen('certificate')

def main():
    """Main application entry point"""
    # Set application attributes BEFORE constructing QApplication (fixes terminal warning)
    from PyQt5.QtCore import Qt
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    
    
    # Set application properties
    app.setApplicationName("DataWipe Pro")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Team Tejasway")
    
    window = DataWipeProApp()
    window.showMaximized()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
