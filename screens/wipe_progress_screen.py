"""
DataWipe Pro - Wipe Progress Screen
Team: Tejasway

Shows progress bar per phase with terminal log window and status badges.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QProgressBar, QTextEdit, QFrame,
                            QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

class WipeProgressScreen(QWidget):
    wipe_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.wipe_config = None
        self.current_phase = 0
        self.progress_value = 0
        self.setup_ui()
        
        # Timer for mock progress updates
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_mock_progress)
    
    def setup_ui(self):
        """Set up the wipe progress screen UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Secure Wipe in Progress")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Ubuntu", 24, QFont.Bold))
        title_label.setStyleSheet("color: #19376D; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        self.device_label = QLabel("Device: /dev/sdb")
        self.device_label.setAlignment(Qt.AlignCenter)
        self.device_label.setFont(QFont("Ubuntu", 14))
        self.device_label.setStyleSheet("color: #6C757D; margin-bottom: 20px;")
        header_layout.addWidget(self.device_label)
        
        layout.addLayout(header_layout)
        
        # Overall progress section
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        
        # Overall progress bar
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CED4DA;
                border-radius: 8px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #28A745;
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.overall_progress)
        
        # Current phase label
        self.phase_label = QLabel("Initializing...")
        self.phase_label.setAlignment(Qt.AlignCenter)
        self.phase_label.setFont(QFont("Ubuntu", 14, QFont.Bold))
        self.phase_label.setStyleSheet("color: #19376D; margin: 10px 0;")
        progress_layout.addWidget(self.phase_label)
        
        # Time remaining
        self.time_label = QLabel("Estimated time remaining: Calculating...")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Ubuntu", 12))
        self.time_label.setStyleSheet("color: #6C757D;")
        progress_layout.addWidget(self.time_label)
        
        layout.addWidget(progress_frame)
        
        # Phase status badges
        phases_frame = QFrame()
        phases_frame.setFrameStyle(QFrame.Box)
        phases_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        phases_layout = QVBoxLayout(phases_frame)
        
        phases_title = QLabel("Wipe Phases")
        phases_title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        phases_title.setStyleSheet("color: #19376D; margin-bottom: 15px;")
        phases_layout.addWidget(phases_title)
        
        # Create phase badges grid
        badges_layout = QGridLayout()
        
        self.phase_names = [
            "Detect Device",
            "Unhide HPA/DCO", 
            "Pass 1: Zeros",
            "Pass 2: Ones",
            "Pass 3: Random",
            "Pass 4: Complement",
            "Pass 5: Random",
            "Pass 6: Zeros",
            "Pass 7: Verify",
            "Generate Certificate"
        ]
        
        self.phase_badges = []
        for i, phase_name in enumerate(self.phase_names):
            badge = QLabel(f"○ {phase_name}")
            badge.setFont(QFont("Ubuntu", 11))
            badge.setStyleSheet("color: #6C757D; padding: 5px; margin: 2px;")
            
            row = i // 2
            col = i % 2
            badges_layout.addWidget(badge, row, col)
            self.phase_badges.append(badge)
        
        phases_layout.addLayout(badges_layout)
        layout.addWidget(phases_frame)
        
        # Terminal log section
        log_frame = QFrame()
        log_frame.setFrameStyle(QFrame.Box)
        log_frame.setStyleSheet("""
            QFrame {
                background-color: #212529;
                border: 2px solid #495057;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        log_layout = QVBoxLayout(log_frame)
        
        log_title = QLabel("Live Process Log")
        log_title.setFont(QFont("Ubuntu", 14, QFont.Bold))
        log_title.setStyleSheet("color: #28A745; margin-bottom: 10px;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: 1px solid #495057;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_frame)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.cancel_button = QPushButton("Cancel Wipe")
        self.cancel_button.setFont(QFont("Ubuntu", 12))
        self.cancel_button.setMinimumSize(150, 40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_mock_wipe(self, wipe_config):
        """Start the mock wipe process"""
        self.wipe_config = wipe_config
        device = wipe_config.get('device', {})
        
        # Update device label
        device_path = device.get('device_path', 'Unknown')
        device_model = device.get('model', 'Unknown')
        self.device_label.setText(f"Device: {device_path} ({device_model})")
        
        # Reset progress
        self.current_phase = 0
        self.progress_value = 0
        self.overall_progress.setValue(0)
        
        # Clear log
        self.log_text.clear()
        
        # Add initial log entries
        self.add_log_entry("=== DataWipe Pro - Secure Wipe Started ===")
        self.add_log_entry(f"Device: {device_path}")
        self.add_log_entry(f"Model: {device_model}")
        self.add_log_entry(f"Method: {wipe_config.get('method', 'Unknown')}")
        self.add_log_entry(f"Operator: {wipe_config.get('operator_name', 'Unknown')}")
        self.add_log_entry("")
        
        # Start progress timer
        self.progress_timer.start(500)  # Update every 500ms
    
    def update_mock_progress(self):
        """Update mock progress simulation"""
        # Increment progress
        self.progress_value += 1
        
        # Calculate current phase based on progress
        phase_progress = self.progress_value / 10
        new_phase = min(int(phase_progress), len(self.phase_names) - 1)
        
        # Update phase if changed
        if new_phase != self.current_phase:
            # Mark previous phase as complete
            if self.current_phase < len(self.phase_badges):
                self.phase_badges[self.current_phase].setText(
                    f"✓ {self.phase_names[self.current_phase]}"
                )
                self.phase_badges[self.current_phase].setStyleSheet(
                    "color: #28A745; padding: 5px; margin: 2px; font-weight: bold;"
                )
            
            self.current_phase = new_phase
            
            # Update current phase badge
            if self.current_phase < len(self.phase_badges):
                self.phase_badges[self.current_phase].setText(
                    f"● {self.phase_names[self.current_phase]}"
                )
                self.phase_badges[self.current_phase].setStyleSheet(
                    "color: #FFC107; padding: 5px; margin: 2px; font-weight: bold;"
                )
                
                # Update phase label
                self.phase_label.setText(f"Phase {self.current_phase + 1}: {self.phase_names[self.current_phase]}")
                
                # Add log entry for new phase
                self.add_log_entry(f"[{self.get_timestamp()}] Starting {self.phase_names[self.current_phase]}...")
        
        # Update progress bar
        overall_progress = min(self.progress_value, 100)
        self.overall_progress.setValue(overall_progress)
        
        # Update time remaining
        remaining_time = max(0, 20 - (self.progress_value * 0.2))
        self.time_label.setText(f"Estimated time remaining: {remaining_time:.1f} minutes")
        
        # Add occasional log entries
        if self.progress_value % 5 == 0:
            self.add_log_entry(f"[{self.get_timestamp()}] Progress: {overall_progress}%")
        
        # Complete wipe when progress reaches 100
        if self.progress_value >= 100:
            self.complete_wipe()
    
    def complete_wipe(self):
        """Complete the mock wipe process"""
        self.progress_timer.stop()
        
        # Mark final phase as complete
        if self.current_phase < len(self.phase_badges):
            self.phase_badges[self.current_phase].setText(
                f"✓ {self.phase_names[self.current_phase]}"
            )
            self.phase_badges[self.current_phase].setStyleSheet(
                "color: #28A745; padding: 5px; margin: 2px; font-weight: bold;"
            )
        
        # Update UI
        self.phase_label.setText("Wipe Completed Successfully!")
        self.phase_label.setStyleSheet("color: #28A745; margin: 10px 0; font-weight: bold;")
        self.time_label.setText("Total time: 18.5 minutes")
        
        # Add completion log entries
        self.add_log_entry("")
        self.add_log_entry(f"[{self.get_timestamp()}] === WIPE COMPLETED SUCCESSFULLY ===")
        self.add_log_entry(f"[{self.get_timestamp()}] All data has been securely erased")
        self.add_log_entry(f"[{self.get_timestamp()}] Verification: PASSED")
        self.add_log_entry(f"[{self.get_timestamp()}] Certificate: GENERATED")
        
        # Prepare result data
        result_data = {
            'status': 'completed',
            'completion_time': self.get_timestamp(),
            'total_duration': '18.5 minutes',
            'verification_passed': True,
            'certificate_generated': self.wipe_config.get('generate_certificate', True)
        }
        
        # Navigate to results after a short delay
        QTimer.singleShot(2000, lambda: self.show_results(result_data))
    
    def show_results(self, result_data):
        """Show the results screen"""
        if self.parent:
            self.parent.wipe_completed(result_data)
    
    def add_log_entry(self, message):
        """Add an entry to the log"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def get_timestamp(self):
        """Get current timestamp for log entries"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            'Cancel Wipe',
            'Are you sure you want to cancel the wipe process?\n\n'
            'The device may be left in an inconsistent state.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.progress_timer.stop()
            self.add_log_entry(f"[{self.get_timestamp()}] WIPE CANCELLED BY USER")
            
            if self.parent:
                self.parent.show_screen('device_selection')
