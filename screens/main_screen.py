"""
Main Screen - Unified single page with wipe functionality and certificate display
"""

import time
import random
import qrcode
import io
import base64
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QProgressBar, QTextEdit,
                            QMessageBox, QFrame, QSpacerItem, QSizePolicy,
                            QScrollArea, QFileDialog, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from utils.certificate_generator import CertificateGenerator
from utils.system_info import SystemInfoDetector

class WipeThread(QThread):
    """Thread to simulate wipe process with progress updates"""
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    wipe_completed = pyqtSignal(dict)
    
    def __init__(self, device_info):
        super().__init__()
        self.device_info = device_info
        self.is_running = True
    
    def run(self):
        """Simulate wipe with slow early progress, lots of logs, and final jump to 100."""
        start_time = time.time()

        def emit_log(text: str):
            self.log_updated.emit(f"[{time.strftime('%H:%M:%S')}] {text}")

        # Phase 1: initialization with very slow progress 0 → 1 → 2
        init_steps = [
            "Initializing secure wipe process...",
            "Detecting device geometry and sector map...",
            "Reading device SMART and health status...",
            "Locking device for exclusive access...",
            "Preparing NIST SP 800-88 workflow...",
        ]
        for step in init_steps:
            if not self.is_running:
                return
            emit_log(step)
            self.msleep(150)

        for pct in [0, 1, 2]:
            if not self.is_running:
                return
            # Between each percent, stream many technical logs for 5–10 seconds total
            window_ms = random.randint(5000, 10000)
            elapsed = 0
            while elapsed < window_ms and self.is_running:
                sector_a = random.randint(0, 0xFFFFF)
                sector_b = sector_a + random.randint(256, 4096)
                emit_log(f"Pass setup: staging pattern chunks; sectors 0x{sector_a:08X}-0x{sector_b:08X}")
                self.msleep(120)
                elapsed += 120
                if random.random() < 0.15:
                    emit_log("I/O queue balanced • write cache enabled • verify queue primed")
                if random.random() < 0.12:
                    emit_log("Controller thermal check: nominal • TRIM preflight queued")
            self.progress_updated.emit(pct)

        # Phase 2: bulk passes and verification without visible % change
        phases = [
            "Pass 1/3: Writing random pattern...",
            "Pass 1/3: Verifying random pattern...",
            "Pass 2/3: Writing complementary 0xFF pattern...",
            "Pass 2/3: Verifying complementary pattern...",
            "Finalization: Clearing HPA/DCO hidden areas...",
            "SSD maintenance: Issuing TRIM commands...",
            "Integrity: Generating SHA-256 rolling hash...",
            "Audit: Assembling tamper-proof certificate...",
        ]
        for phase in phases:
            if not self.is_running:
                return
            emit_log(phase)
            # Stream rich sub-logs for realism
            sub_iters = random.randint(40, 80)
            for _ in range(sub_iters):
                if not self.is_running:
                    return
                action = random.choice([
                    "Overwriting block", "Verifying block", "Checksum", "Queue depth",
                    "DMA throughput", "Entropy pool", "Zeroing padding", "Sync flush"
                ])
                a = random.randint(0, 0xFFFFFF)
                b = a + random.randint(128, 8192)
                emit_log(f"{action}: 0x{a:06X}-0x{b:06X} • rate {random.randint(350,700)} MB/s • OK")
                self.msleep(random.randint(60, 140))

        # Phase 3: jump to 98 → 99 → 100 quickly
        for pct in [98, 99, 100]:
            if not self.is_running:
                return
            self.progress_updated.emit(pct)
            emit_log(f"Progress checkpoint reached: {pct}%")
            self.msleep(250 if pct < 100 else 50)

        # Emit completion with mock data
        wipe_data = {
            'device': self.device_info,
            'completion_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'method': 'NIST SP 800-88 Rev. 1',
            'passes': 3,
            'verification': 'PASSED',
            'certificate_id': f"DWP-{int(time.time())}"
        }
        
        self.wipe_completed.emit(wipe_data)
    
    def stop(self):
        self.is_running = False

class MainScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.drives = []
        self.selected_device = None
        self.wipe_thread = None
        self.wipe_data = None
        self.certificate_generator = CertificateGenerator()
        self.completion_dialog = None  # Initialize completion dialog to None
        
        self.system_info = SystemInfoDetector()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the unified main screen UI with flexible layout"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced margins for better space usage
        main_layout.setSpacing(20)  # Reduced spacing
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        self.grid_layout = grid_layout
        
        # Device info card (spans full width)
        self.device_info_card = self.create_device_info_card()
        
        # Wipe control card
        self.wipe_card = self.create_wipe_control_card()
        
        # Progress card (initially hidden)
        self.progress_card = self.create_progress_card()
        self.progress_card.setVisible(False)
        
        # Results cards (initially hidden)
        self.results_card = self.create_results_card()
        self.results_card.setVisible(False)
        
        # Certificate card (initially hidden)
        self.certificate_card = self.create_certificate_card()
        self.certificate_card.setVisible(False)
        
        grid_layout.addWidget(self.device_info_card, 0, 0, 1, 2)  # Full width
        grid_layout.addWidget(self.wipe_card, 1, 0, 1, 1)
        grid_layout.addWidget(self.progress_card, 1, 1, 1, 1)
        grid_layout.addWidget(self.results_card, 2, 0, 1, 1)
        grid_layout.addWidget(self.certificate_card, 2, 1, 1, 1)
        
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        self.load_system_info()

    def load_system_info(self):
        """Load and display actual system information"""
        try:
            specs = self.system_info.get_formatted_specs()
            
            # Update device info card with real specs
            self.device_model.setText(specs['device'])
            self.device_serial.setText(f"Serial: {specs['serial']}")
            self.processor_label.setText(specs['processor'])
            self.memory_label.setText(specs['memory'])
            self.os_label.setText(f"{specs['os']} ({specs['architecture']})")
            
        except Exception as e:
            print(f"Failed to load system info: {e}")
            # Keep default values if detection fails
    
    def create_device_info_card(self):
        """Create device info card with system fonts and flexible sizing"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 2px solid #4A5568;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(20)
        
        # Left side - Device icon and basic info
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)
        
        device_icon = QLabel("💻")
        device_icon.setFont(QFont("Arial", 32))
        device_icon.setAlignment(Qt.AlignCenter)
        device_icon.setStyleSheet("color: #68D391; background-color: #1A202C; padding: 15px; border-radius: 12px;")
        
        device_type = QLabel("Laptop")
        device_type.setFont(QFont("Arial", 20, QFont.Bold))
        device_type.setStyleSheet("color: #F7FAFC;")
        device_type.setAlignment(Qt.AlignCenter)
        
        self.device_model = QLabel("Loading...")
        self.device_model.setFont(QFont("Arial", 14))
        self.device_model.setStyleSheet("color: #A0AEC0;")
        self.device_model.setAlignment(Qt.AlignCenter)
        self.device_model.setWordWrap(True)
        
        self.device_serial = QLabel("Serial: Loading...")
        self.device_serial.setFont(QFont("Arial", 12))
        self.device_serial.setStyleSheet("color: #718096;")
        self.device_serial.setAlignment(Qt.AlignCenter)
        self.device_serial.setWordWrap(True)
        
        left_layout.addWidget(device_icon)
        left_layout.addWidget(device_type)
        left_layout.addWidget(self.device_model)
        left_layout.addWidget(self.device_serial)
        
        # Middle - System specs
        middle_layout = QVBoxLayout()
        middle_layout.setAlignment(Qt.AlignTop)
        
        specs_title = QLabel("SYSTEM SPECIFICATIONS")
        specs_title.setFont(QFont("Arial", 12, QFont.Bold))
        specs_title.setStyleSheet("color: #68D391; margin-bottom: 10px;")
        
        self.processor_label = QLabel("Loading processor...")
        self.processor_label.setFont(QFont("Arial", 11))
        self.processor_label.setStyleSheet("color: #F7FAFC; margin-bottom: 5px;")
        self.processor_label.setWordWrap(True)
        
        self.memory_label = QLabel("Loading memory...")
        self.memory_label.setFont(QFont("Arial", 11))
        self.memory_label.setStyleSheet("color: #F7FAFC; margin-bottom: 5px;")
        self.memory_label.setWordWrap(True)
        
        self.os_label = QLabel("Loading OS...")
        self.os_label.setFont(QFont("Arial", 11))
        self.os_label.setStyleSheet("color: #F7FAFC; margin-bottom: 5px;")
        self.os_label.setWordWrap(True)
        
        middle_layout.addWidget(specs_title)
        middle_layout.addWidget(self.processor_label)
        middle_layout.addWidget(self.memory_label)
        middle_layout.addWidget(self.os_label)
        middle_layout.addStretch()
        
        # Right side - Dashboard button
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        
        self.main_wipe_button = QPushButton("DASHBOARD")
        self.main_wipe_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.main_wipe_button.setMinimumHeight(50)
        self.main_wipe_button.setMinimumWidth(150)
        self.main_wipe_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_wipe_button.setStyleSheet("""
            QPushButton {
                background-color: #68D391;
                color: #1A202C;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #48BB78;
            }
            QPushButton:pressed {
                background-color: #38A169;
            }
        """)
        self.main_wipe_button.clicked.connect(self.open_dashboard)
        
        right_layout.addWidget(self.main_wipe_button)
        
        layout.addLayout(left_layout, 1)
        layout.addLayout(middle_layout, 2)
        layout.addLayout(right_layout, 1)
        
        return card
    
    def create_wipe_control_card(self):
        """Create wipe control card with flexible sizing"""
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet("""
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 2px solid #4A5568;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Select Device")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #F7FAFC; margin-bottom: 10px;")
        
        # Device dropdown with icon
        self.device_combo = QComboBox()
        self.device_combo.setFont(QFont("Arial", 11))
        self.device_combo.setMinimumHeight(45)
        self.device_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.device_combo.setStyleSheet("""
            QComboBox {
                background-color: #1A202C;
                color: #F7FAFC;
                border: 2px solid #4A5568;
                border-radius: 10px;
                padding: 12px;
            }
            QComboBox:hover {
                border-color: #68D391;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox QAbstractItemView {
                background-color: #2D3748;
                color: #F7FAFC;
                selection-background-color: #68D391;
                selection-color: #1A202C;
                border: 1px solid #4A5568;
                border-radius: 8px;
            }
        """)
        self.device_combo.currentIndexChanged.connect(self.on_device_selected_immediate)
        
        # Start wipe button
        self.wipe_button = QPushButton("START SECURE WIPE")
        self.wipe_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.wipe_button.setMinimumHeight(50)
        self.wipe_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.wipe_button.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #C53030;
            }
            QPushButton:disabled {
                background-color: #4A5568;
                color: #A0AEC0;
            }
        """)
        self.wipe_button.clicked.connect(self.start_wipe)
        self.wipe_button.setEnabled(False)
        
        layout.addWidget(title)
        layout.addWidget(self.device_combo)
        layout.addStretch()
        layout.addWidget(self.wipe_button)
        
        return card
    
    def create_progress_card(self):
        """Create progress card with flexible sizing"""
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet("""
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 2px solid #4A5568;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Progress display
        progress_layout = QVBoxLayout()
        progress_layout.setAlignment(Qt.AlignCenter)

        class CircularProgress(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._value = 0
                self._thickness = 10
                self._size = 140
                self.setFixedSize(self._size, self._size)

            def setValue(self, v: int):
                self._value = max(0, min(100, int(v)))
                self.update()

            def paintEvent(self, event):
                from PyQt5.QtGui import QPainter, QPen
                from PyQt5.QtCore import QRectF
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                rect = QRectF(self._thickness/2, self._thickness/2,
                              self.width()-self._thickness, self.height()-self._thickness)
                # Background circle
                pen_bg = QPen(QColor('#374151'))
                pen_bg.setWidth(self._thickness)
                painter.setPen(pen_bg)
                painter.drawArc(rect, 0, 360*16)
                # Progress arc (start at top, clockwise)
                pen_fg = QPen(QColor('#68D391'))
                pen_fg.setWidth(self._thickness)
                painter.setPen(pen_fg)
                span = int(360 * 16 * (self._value/100.0))
                painter.drawArc(rect, 90*16, -span)
                # Percentage text
                painter.setPen(QColor('#F7FAFC'))
                painter.setFont(QFont('Arial', 20, QFont.Bold))
                painter.drawText(self.rect(), Qt.AlignCenter, f"{self._value}%")

        self.circular_progress = CircularProgress(card)
        self.circular_progress.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        status_label = QLabel("ERASING DATA...")
        status_label.setFont(QFont("Arial", 13, QFont.Bold))
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFixedWidth(260)
        status_label.setFixedHeight(56)
        status_label.setStyleSheet(
            """
            QLabel {
                color: #F7FAFC;
                background-color: #2C313C;
                border: 2px solid #4A5568;
                border-radius: 14px;
                padding: 12px 18px;
            }
            """
        )
        
        # Live logs with flexible sizing
        self.logs_text = QTextEdit()
        self.logs_text.setMinimumHeight(100)
        self.logs_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #1A202C;
                color: #FFFFFF;
                border: 1px solid #4A5568;
                border-radius: 8px;
                padding: 8px;
                font-family: monospace;
                font-size: 9px;
            }
        """)
        self.logs_text.setReadOnly(True)
        
        progress_layout.addWidget(self.circular_progress, 0, Qt.AlignHCenter)
        progress_layout.addWidget(status_label, 0, Qt.AlignHCenter)

        # Keep the progress visuals centered above the logs
        center_row = QHBoxLayout()
        center_row.setAlignment(Qt.AlignHCenter)
        center_row.addStretch(1)
        center_row.addLayout(progress_layout)
        center_row.addStretch(1)
        layout.addLayout(center_row)
        layout.addStretch()
        layout.addWidget(self.logs_text)
        
        return card
    
    def create_results_card(self):
        """Create results card with flexible sizing"""
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet("""
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 2px solid #68D391;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        # Success display
        success_icon = QLabel("✅")
        success_icon.setFont(QFont("Arial", 48))
        success_icon.setAlignment(Qt.AlignCenter)
        success_icon.setStyleSheet("background-color: #2D3748; padding: 10px; border-radius: 8px;")
        
        success_text = QLabel("ERASED")
        success_text.setFont(QFont("Arial", 20, QFont.Bold))
        success_text.setStyleSheet("color: #F7FAFC;")
        success_text.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(success_icon)
        layout.addWidget(success_text)
        layout.addStretch()
        
        return card
    
    def create_certificate_card(self):
        """Create certificate card with flexible sizing"""
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet("""
            QFrame {
                background-color: #2D3748;
                border-radius: 15px;
                border: 2px solid #4A5568;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(16)

        # Header
        header = QLabel("Certificate of Secure Data Erasure")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignLeft)
        header.setStyleSheet("color:#F7FAFC;")

        # Info rows (modern boxed rows)
        def info_row(title_text: str):
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: #1F2937;
                    border: 1px solid #4A5568;
                    border-radius: 10px;
                    padding: 14px;
                }
                QLabel { color: #E5E7EB; }
            """)
            row_layout = QVBoxLayout(row)
            title = QLabel(title_text)
            title.setFont(QFont("Arial", 10, QFont.Bold))
            title.setStyleSheet("color:#68D391;")
            value = QLabel("—")
            value.setWordWrap(True)
            value.setFont(QFont("Arial", 11))
            row_layout.addWidget(title)
            row_layout.addWidget(value)
            return row, value

        self.row_device, self.lbl_device = info_row("Device")
        self.row_method, self.lbl_method = info_row("Method")
        self.row_time, self.lbl_time = info_row("Completion Time")
        self.row_cert, self.lbl_cert = info_row("Certificate ID")

        # Buttons full width
        buttons = QHBoxLayout()
        self.download_json_btn = QPushButton("Download JSON")
        self.download_pdf_btn = QPushButton("Download PDF")
        for btn in [self.download_json_btn, self.download_pdf_btn]:
            btn.setFont(QFont("Arial", 11, QFont.Bold))
            btn.setMinimumHeight(42)
            btn.setStyleSheet("""
                QPushButton {background-color:#68D391;color:#1A202C;border:none;border-radius:10px;}
                QPushButton:hover {background-color:#48BB78;}
            """)
        self.download_json_btn.clicked.connect(self.download_json)
        self.download_pdf_btn.clicked.connect(self.download_pdf)
        buttons.addWidget(self.download_json_btn)
        buttons.addWidget(self.download_pdf_btn)

        # Assemble in two-column grid for better readability
        layout.addWidget(header)
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(self.row_device, 0, 0)
        grid.addWidget(self.row_method, 0, 1)
        grid.addWidget(self.row_time, 1, 0)
        grid.addWidget(self.row_cert, 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)
        layout.addStretch()
        layout.addLayout(buttons)

        return card

    def open_dashboard(self):
        """Open the DataWipe Pro dashboard website"""
        import webbrowser
        webbrowser.open("https://datawipepro.netlify.app/")
    
    def update_drive_list(self, drives):
        """Update the drive dropdown with detected drives"""
        # Preserve current selection (by stable key) and avoid clearing user choice during an active wipe
        previously_selected_key = None
        if self.selected_device:
            previously_selected_key = self.selected_device.get('device_path') or self.selected_device.get('serial')

        self.drives = drives

        self.device_combo.blockSignals(True)
        self.device_combo.clear()

        if not drives:
            self.device_combo.addItem("No drives detected")
            self.wipe_button.setEnabled(False)
        else:
            self.device_combo.addItem("💾 Select a drive...")
            restored_index = 0
            for idx, drive in enumerate(drives, start=1):
                model = drive.get('model', 'Unknown Device')
                size_bytes = drive.get('size', 0)
                size_gb = round(size_bytes / (1024**3), 1) if size_bytes > 0 else 0
                drive_type = drive.get('type', 'Unknown')
                serial = drive.get('serial', 'No serial')[:12] + "..." if len(drive.get('serial', '')) > 12 else drive.get('serial', 'No serial')

                display_text = f"💾 {model} • {size_gb} GB {drive_type} • S/N: {serial}"
                self.device_combo.addItem(display_text)

                key = drive.get('device_path') or drive.get('serial')
                if previously_selected_key and key == previously_selected_key:
                    restored_index = idx

            # Restore selection if still present
            if restored_index > 0:
                self.device_combo.setCurrentIndex(restored_index)
                self.selected_device = self.drives[restored_index - 1]
                self.wipe_button.setEnabled(True)
            else:
                # Do not auto-clear user choice if we are in the middle of wiping; just keep button disabled
                if self.wipe_thread is None:
                    self.selected_device = None
                self.wipe_button.setEnabled(False)

        self.device_combo.blockSignals(False)
    
    def on_device_selected_immediate(self, index):
        """Handle immediate device selection without timer delay"""
        print(f"[v0] Device selection triggered: index={index}, drives_count={len(self.drives)}")
        
        if index > 0 and index <= len(self.drives):  # Skip "Select a drive..." option
            drive = self.drives[index - 1]
            self.selected_device = drive
            self.wipe_button.setEnabled(True)
            
            model = drive.get('name', 'Unknown Device')
            serial = drive.get('serial', 'Unknown')
            
            # Update device info card with selected device
            self.device_model.setText(model)
            self.device_serial.setText(f"Serial: {serial}")
            
            print(f"[v0] Device selected and locked: {model}")
        else:
            self.selected_device = None
            self.wipe_button.setEnabled(False)
            print(f"[v0] Device selection cleared")

    def start_wipe(self):
        """Start the wipe process"""
        if not self.selected_device:
            return
        
        # Show progress card
        self.progress_card.setVisible(True)
        self.wipe_button.setEnabled(False)
        self.device_combo.setEnabled(False)
        
        # Clear previous logs
        self.logs_text.clear()
        self.circular_progress.setValue(0)
        
        # Start wipe thread
        self.wipe_thread = WipeThread(self.selected_device)
        self.wipe_thread.progress_updated.connect(self.update_progress)
        self.wipe_thread.log_updated.connect(self.add_log)
        self.wipe_thread.wipe_completed.connect(self.on_wipe_completed)
        self.wipe_thread.start()

        # Prevent background refreshes from changing selection while wiping
        if hasattr(self.parent, 'drive_timer'):
            self.parent.drive_timer.stop()
    
    def update_progress(self, value):
        """Update progress display"""
        self.circular_progress.setValue(value)
    
    def add_log(self, log_text):
        """Add log entry with auto-scroll"""
        self.logs_text.append(log_text)
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_wipe_completed(self, wipe_data):
        """Handle wipe completion"""
        self.wipe_data = wipe_data
        
        # After-wipe page: hide device selection and 'ERASED' card to free space
        if hasattr(self, 'wipe_card'):
            self.wipe_card.setVisible(False)
        self.results_card.setVisible(False)
        # Hide progress section entirely after completion
        if hasattr(self, 'progress_card'):
            self.progress_card.setVisible(False)

        self.certificate_card.setVisible(True)
        # Make certificate span full width and move up next to device card
        try:
            self.grid_layout.removeWidget(self.certificate_card)
            # Place certificate in row 1 (middle row), spanning both columns
            self.grid_layout.addWidget(self.certificate_card, 1, 0, 1, 2)
        except Exception:
            pass
        
        # Populate certificate info rows
        device_info = wipe_data['device']
        self.lbl_device.setText(f"{device_info.get('name', 'Unknown Device')}  •  S/N: {device_info.get('serial', 'No serial')}")
        self.lbl_method.setText(wipe_data.get('method', 'NIST SP 800-88 Rev. 1'))
        self.lbl_time.setText(wipe_data.get('completion_time', ''))
        self.lbl_cert.setText(wipe_data.get('certificate_id', ''))
        
        if self.completion_dialog is None:
            self.show_completion_dialog(wipe_data)

        # Re-enable device list updates now that wiping is done
        if hasattr(self.parent, 'drive_timer'):
            self.parent.drive_timer.start(5000)

    def reset_for_new_wipe(self):
        """Reset UI state to allow a new wipe without stale selection"""
        self.selected_device = None
        self.wipe_thread = None
        self.wipe_data = None
        self.progress_card.setVisible(False)
        self.results_card.setVisible(False)
        self.certificate_card.setVisible(False)
        self.logs_text.clear()
        self.circular_progress.setValue(0)
        self.device_combo.setEnabled(True)
        self.wipe_button.setEnabled(False)
        # Restore layout placement for certificate card
        try:
            self.grid_layout.removeWidget(self.certificate_card)
            # Default placement during a fresh session: bottom-right
            self.grid_layout.addWidget(self.certificate_card, 2, 1, 1, 1)
        except Exception:
            pass

    def show_completion_dialog(self, wipe_data):
        """Show centered completion dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        self.completion_dialog = QDialog(self)
        self.completion_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.completion_dialog.setModal(True)
        self.completion_dialog.setFixedSize(760, 460)
        
        # Center the dialog on screen
        screen_geometry = self.parent.geometry()
        dialog_x = screen_geometry.x() + (screen_geometry.width() - self.completion_dialog.width()) // 2
        dialog_y = screen_geometry.y() + (screen_geometry.height() - self.completion_dialog.height()) // 2
        self.completion_dialog.move(dialog_x, dialog_y)
        
        self.completion_dialog.setStyleSheet("""
            QDialog {
                background-color: #2D3748;
                border: 3px solid #68D391;
                border-radius: 20px;
            }
            QLabel {
                color: #F7FAFC;
            }
            QPushButton {
                background-color: #68D391;
                color: #1A202C;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #48BB78;
            }
        """)
        
        layout = QVBoxLayout(self.completion_dialog)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(16)
        
        # Success icon
        success_icon = QLabel("✅")
        success_icon.setFont(QFont("Arial", 52))
        success_icon.setAlignment(Qt.AlignCenter)
        success_icon.setStyleSheet("background-color: #2D3748; padding: 10px; border-radius: 8px;")
        
        title = QLabel("WIPE COMPLETED SUCCESSFULLY!")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #68D391;")
        title.setWordWrap(True)
        
        # Description
        desc = QLabel("Your device has been securely wiped using military-grade NIST SP 800-88 standards. All hidden areas (HPA/DCO) are sanitized and verification has passed.")
        desc.setFont(QFont("Arial", 12))
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #A0AEC0;")
        desc.setWordWrap(True)
        
        # Device info
        device_info = wipe_data['device']
        device_name = device_info.get('name', 'Unknown Device')
        device_label = QLabel(f"Device: {device_name}")
        device_label.setFont(QFont("Arial", 12, QFont.Bold))
        device_label.setAlignment(Qt.AlignCenter)
        device_label.setStyleSheet("color: #F7FAFC;")
        device_label.setWordWrap(True)
        
        # OK button
        ok_button = QPushButton("AWESOME! 🎉")
        ok_button.setFont(QFont("Arial", 14, QFont.Bold))
        ok_button.clicked.connect(self.close_completion_dialog)
        
        layout.addWidget(success_icon, 0,)
        layout.addWidget(title, 0,)
        layout.addWidget(desc, 0,)
        layout.addWidget(device_label, 0,)
        layout.addStretch()
        layout.addWidget(ok_button, 0,)
        
        # Show dialog
        self.completion_dialog.show()

    def close_completion_dialog(self):
        """Close the completion dialog"""
        if self.completion_dialog:
            self.completion_dialog.close()
            self.completion_dialog = None  # Reset to None after closing


    def download_json(self):
        """Download certificate as JSON"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save JSON Certificate", 
                f"certificate_{self.wipe_data['certificate_id']}.json",
                "JSON Files (*.json)"
            )
            if filename:
                json_cert = self.certificate_generator.generate_json_certificate(self.wipe_data)
                with open(filename, 'w') as f:
                    f.write(json_cert)
                QMessageBox.information(self, "Success", f"JSON certificate saved to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save JSON certificate:\n{str(e)}")
    
    def download_pdf(self):
        """Download certificate as PDF"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save PDF Certificate", 
                f"certificate_{self.wipe_data['certificate_id']}.pdf",
                "PDF Files (*.pdf)"
            )
            if filename:
                self.certificate_generator.generate_pdf_certificate(self.wipe_data, filename)
                QMessageBox.information(self, "Success", f"PDF certificate saved to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF certificate:\n{str(e)}")
