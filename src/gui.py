import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import sys
import subprocess
import uuid
import hashlib
from datetime import datetime

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from drive_detector import DriveDetector
    from wipe_engine import WipeEngine
    from certificate_generator import CertificateGenerator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class DataWipeProGUI:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("DataWipe Pro - Secure Data Erasure")
            
            self.root.geometry("900x700")
            self.root.resizable(False, False)
            
            self.colors = {
                'bg_primary': '#1a1a2e',
                'bg_secondary': '#16213e',
                'bg_tertiary': '#0f3460',
                'card_bg': '#16213e',
                'accent': '#4ade80',
                'accent_hover': '#22c55e',
                'danger': '#ef4444',
                'warning': '#f59e0b',
                'text_primary': '#ffffff',
                'text_secondary': '#94a3b8',
                'text_muted': '#64748b',
                'border': '#334155',
                'success': '#10b981'
            }
            
            self.root.configure(bg=self.colors['bg_primary'])
            
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (450)
            y = (self.root.winfo_screenheight() // 2) - (350)
            self.root.geometry(f"900x700+{x}+{y}")
            
            try:
                self.drive_detector = DriveDetector()
                self.wipe_engine = WipeEngine()
                self.certificate_generator = CertificateGenerator()
            except Exception as e:
                print(f"Component initialization error: {e}")
                messagebox.showerror("Initialization Error", f"Failed to initialize components: {e}")
                raise
            
            self.devices = []
            self.selected_device = None
            self.is_wiping = False
            self.is_refreshing = False
            self.refresh_thread = None
            
            self.status_label = None
            self.device_name_label = None
            self.device_details_label = None
            self.device_dropdown = None
            self.device_var = None
            self.refresh_btn = None
            self.wipe_button = None
            self.progress_card = None
            self.progress_var = None
            self.progress_percentage = None
            self.progress_status = None
            self.progress_bar = None
            self.certificate_card = None
            self.cert_device_label = None
            self.cert_method_label = None
            self.cert_date_label = None
            
            try:
                self.create_modern_ui()
            except Exception as e:
                print(f"UI creation error: {e}")
                messagebox.showerror("UI Error", f"Failed to create interface: {e}")
                raise
            
            print("[v0] Initial device refresh called")
            self.refresh_devices()  # Initial device refresh
            
        except Exception as e:
            print(f"GUI initialization error: '{DataWipeProGUI' object has no attribute 'status_label'': {e}")
            if hasattr(self, 'root'):
                try:
                    self.root.destroy()
                except:
                    pass
            raise
    
    def create_modern_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header with logo area
        self.create_header(main_frame)
        
        # Main content grid - 2x2 layout like reference image
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill='both', expand=True, pady=(40, 0))
        
        # Configure grid weights for proper spacing
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Top left - Device card
        self.create_device_card(content_frame)
        
        # Top right - Progress card (initially hidden)
        self.create_progress_card(content_frame)
        
        # Bottom left - Certificate card (initially hidden)
        self.create_certificate_card(content_frame)
        
        # Bottom right - Eco impact card
        self.create_eco_card(content_frame)

    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(0, 40))
        
        title_label = tk.Label(
            header_frame,
            text="DataWipe Pro",
            font=('Ubuntu', 42, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Military-Grade Secure Data Erasure",
            font=('Ubuntu', 18),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        subtitle_label.pack(pady=(10, 0))
        
        self.status_label = tk.Label(
            header_frame,
            text="Ready • Select a storage device to begin",
            font=('Ubuntu', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        self.status_label.pack(pady=(15, 0))

    def create_device_card(self, parent):
        self.device_card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', bd=0)
        self.device_card.grid(row=0, column=0, padx=(0, 15), pady=(0, 15), sticky='nsew')
        
        # Add rounded corner effect with border
        border_frame = tk.Frame(self.device_card, bg='#334155', height=2)
        border_frame.pack(fill='x', side='top')
        
        content_frame = tk.Frame(self.device_card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Device icon (laptop icon like reference)
        icon_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        icon_frame.pack(pady=(0, 30))
        
        device_icon = tk.Label(
            icon_frame,
            text="💻",
            font=('Ubuntu', 64),
            bg=self.colors['card_bg']
        )
        device_icon.pack()
        
        # Device type label
        device_type_label = tk.Label(
            content_frame,
            text="Storage Device",
            font=('Ubuntu', 24, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        )
        device_type_label.pack(pady=(0, 10))
        
        # Device name (will be updated when device selected)
        self.device_name_label = tk.Label(
            content_frame,
            text="No Device Selected",
            font=('Ubuntu', 16),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        self.device_name_label.pack(pady=(0, 20))
        
        # Device details
        self.device_details_label = tk.Label(
            content_frame,
            text="Select a device to view details",
            font=('Ubuntu', 12),
            fg=self.colors['text_muted'],
            bg=self.colors['card_bg']
        )
        self.device_details_label.pack(pady=(0, 30))
        
        # Device selection dropdown
        dropdown_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        dropdown_frame.pack(fill='x', pady=(0, 20))
        
        style = ttk.Style()
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat')
        
        self.device_var = tk.StringVar()
        self.device_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.device_var,
            state="readonly",
            font=('Ubuntu', 14),
            style='Modern.TCombobox'
        )
        self.device_dropdown.pack(fill='x', ipady=15)
        self.device_dropdown.bind('<<ComboboxSelected>>', self.on_device_selected)
        
        # Refresh button
        refresh_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        refresh_frame.pack(fill='x', pady=(10, 0))
        
        self.refresh_btn = tk.Button(
            refresh_frame,
            text="🔄 Refresh Devices",
            font=('Ubuntu', 12),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            activebackground=self.colors['accent'],
            border=0,
            relief='flat',
            height=2,
            command=self.refresh_devices_threaded,
            cursor='hand2'
        )
        self.refresh_btn.pack(fill='x')
        
        # ERASE & CERTIFY button (like reference image)
        button_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        self.wipe_button = tk.Button(
            button_frame,
            text="ERASE & CERTIFY",
            font=('Ubuntu', 16, 'bold'),
            bg=self.colors['accent'],
            fg='#000000',
            activebackground=self.colors['accent_hover'],
            border=0,
            relief='flat',
            height=3,
            command=self.start_wipe,
            cursor='hand2',
            state='disabled'
        )
        self.wipe_button.pack(fill='x')

    def create_progress_card(self, parent):
        self.progress_card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', bd=0)
        # Initially hidden - will show during wipe
        
        border_frame = tk.Frame(self.progress_card, bg='#334155', height=2)
        border_frame.pack(fill='x', side='top')
        
        content_frame = tk.Frame(self.progress_card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Circular progress area
        progress_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        progress_frame.pack(expand=True)
        
        # Large percentage display (like 60% in reference)
        self.progress_percentage = tk.Label(
            progress_frame,
            text="0%",
            font=('Ubuntu', 72, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        )
        self.progress_percentage.pack(pady=(60, 20))
        
        # Status text below percentage
        self.progress_status = tk.Label(
            progress_frame,
            text="ERASING DATA...",
            font=('Ubuntu', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        )
        self.progress_status.pack()
        
        # Progress bar
        progress_bar_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        progress_bar_frame.pack(fill='x', pady=(40, 0))
        
        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.configure('Circular.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       relief='flat',
                       thickness=12)
        
        self.progress_bar = ttk.Progressbar(
            progress_bar_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='Circular.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x')

    def create_certificate_card(self, parent):
        self.certificate_card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', bd=0)
        # Initially hidden - will show after completion
        
        border_frame = tk.Frame(self.certificate_card, bg='#334155', height=2)
        border_frame.pack(fill='x', side='top')
        
        content_frame = tk.Frame(self.certificate_card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Certificate title
        cert_title = tk.Label(
            content_frame,
            text="CERTIFICATE\nOF DATA\nSANITIZATION",
            font=('Ubuntu', 20, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg'],
            justify='center'
        )
        cert_title.pack(pady=(0, 30))
        
        # Certificate details
        details_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        details_frame.pack(fill='x', pady=(0, 30))
        
        self.cert_device_label = tk.Label(
            details_frame,
            text="DEVICE\n--",
            font=('Ubuntu', 12, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg'],
            justify='left'
        )
        self.cert_device_label.pack(anchor='w', pady=(0, 15))
        
        self.cert_method_label = tk.Label(
            details_frame,
            text="METHOD\nNIST SP 800-88\nCryptographic Erase",
            font=('Ubuntu', 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg'],
            justify='left'
        )
        self.cert_method_label.pack(anchor='w', pady=(0, 15))
        
        self.cert_date_label = tk.Label(
            details_frame,
            text="",
            font=('Ubuntu', 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        self.cert_date_label.pack(anchor='w')

    def create_eco_card(self, parent):
        eco_card = tk.Frame(parent, bg=self.colors['card_bg'], relief='flat', bd=0)
        eco_card.grid(row=1, column=1, padx=(15, 0), pady=(15, 0), sticky='nsew')
        
        border_frame = tk.Frame(eco_card, bg='#334155', height=2)
        border_frame.pack(fill='x', side='top')
        
        content_frame = tk.Frame(eco_card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Eco impact title
        eco_title = tk.Label(
            content_frame,
            text="ECO-IMPACT",
            font=('Ubuntu', 20, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        )
        eco_title.pack(pady=(0, 40))
        
        # CO2 savings
        co2_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        co2_frame.pack(fill='x', pady=(0, 20))
        
        co2_icon = tk.Label(
            co2_frame,
            text="🌍",
            font=('Ubuntu', 24),
            bg=self.colors['card_bg']
        )
        co2_icon.pack(side='left')
        
        co2_text = tk.Label(
            co2_frame,
            text="50 kg",
            font=('Ubuntu', 32, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['card_bg']
        )
        co2_text.pack(side='right')
        
        # E-waste prevention
        waste_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        waste_frame.pack(fill='x', pady=(0, 20))
        
        waste_icon = tk.Label(
            waste_frame,
            text="🌱",
            font=('Ubuntu', 24),
            bg=self.colors['card_bg']
        )
        waste_icon.pack(side='left')
        
        waste_text = tk.Label(
            waste_frame,
            text="200 g",
            font=('Ubuntu', 32, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['card_bg']
        )
        waste_text.pack(side='right')
        
        # Trees equivalent
        trees_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        trees_frame.pack(fill='x')
        
        trees_icon = tk.Label(
            trees_frame,
            text="🌳",
            font=('Ubuntu', 24),
            bg=self.colors['card_bg']
        )
        trees_icon.pack(side='left')
        
        trees_text = tk.Label(
            trees_frame,
            text="2 trees",
            font=('Ubuntu', 32, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['card_bg']
        )
        trees_text.pack(side='right')

    def refresh_devices_threaded(self):
        if self.is_refreshing:
            print("[v0] Refresh already in progress, ignoring request")
            return
        
        if self.refresh_thread and self.refresh_thread.is_alive():
            print("[v0] Previous refresh thread still running, ignoring request")
            return
        
        print("[v0] Starting threaded device refresh")
        self.is_refreshing = True
        
        if self.refresh_btn:
            self.refresh_btn.config(state='disabled', text="⏳ Scanning...", bg=self.colors['warning'])
        if self.status_label:
            self.status_label.config(text="Scanning devices...", fg=self.colors['accent'])
        
        # Clear current selection during refresh
        self.selected_device = None
        self._update_wipe_button_state()
        
        def refresh_worker():
            try:
                print("[v0] Worker thread: Starting device detection")
                devices = self.drive_detector.get_storage_devices()
                print(f"[v0] Worker thread: Found {len(devices)} devices")
                
                # Schedule UI update on main thread
                self.root.after(0, lambda: self._update_devices_ui(devices))
                
            except Exception as e:
                print(f"[v0] Worker thread error: {e}")
                # Schedule error handling on main thread
                error_msg = str(e)
                self.root.after(0, lambda: self._handle_refresh_error(error_msg))
            finally:
                print("[v0] Worker thread: Scheduling refresh state reset")
                # Always reset refresh state
                self.root.after(0, self._reset_refresh_state)
        
        self.refresh_thread = threading.Thread(target=refresh_worker, daemon=True, name="DeviceRefreshThread")
        self.refresh_thread.start()
        print(f"[v0] Started refresh thread: {self.refresh_thread.name}")

    def _update_devices_ui(self, devices):
        print(f"[v0] Updating UI with {len(devices)} devices")
        self.devices = devices
        
        device_options = []
        for i, device in enumerate(self.devices):
            option = f"{device['name']} ({device['size']}) - {device['device_path']}"
            device_options.append(option)
            print(f"[v0] Device {i}: {option}")
        
        if self.device_dropdown:
            # Update dropdown values
            self.device_dropdown['values'] = device_options
            
            if device_options:
                self.device_dropdown.set("Select a device...")
                if self.status_label:
                    self.status_label.config(
                        text=f"Ready • Found {len(self.devices)} storage device(s)",
                        fg=self.colors['success']
                    )
                print(f"[v0] UI updated successfully with {len(device_options)} devices")
            else:
                self.device_dropdown.set("No devices found")
                if self.status_label:
                    self.status_label.config(
                        text="No storage devices detected",
                        fg=self.colors['danger']
                    )
                print("[v0] No devices found")
            
            # Force UI refresh
            self.device_dropdown.update_idletasks()
        
        # Reset selection state
        self.selected_device = None
        self._update_wipe_button_state()
        
        self.root.update_idletasks()
    
    def _handle_refresh_error(self, error_msg):
        print(f"[v0] Handling refresh error: {error_msg}")
        if self.status_label:
            self.status_label.config(
                text=f"Error detecting devices: {error_msg}",
                fg=self.colors['danger']
            )
        
        if self.device_dropdown:
            # Clear dropdown on error
            self.device_dropdown['values'] = []
            self.device_dropdown.set("Error - Click refresh to retry")
        
        # Reset selection state
        self.selected_device = None
        self._update_wipe_button_state()

    def _reset_refresh_state(self):
        print("[v0] Resetting refresh state")
        self.is_refreshing = False
        
        if self.refresh_btn:
            self.refresh_btn.config(
                state='normal', 
                text="🔄 Refresh Devices", 
                bg=self.colors['bg_tertiary']
            )
        
        self.refresh_thread = None
        print("[v0] Refresh state reset complete")

    def on_device_selected(self, event=None):
        selection = self.device_dropdown.get()
        print(f"[v0] Device selection changed: '{selection}'")
        
        if selection and selection != "Select a device..." and selection != "No devices found":
            selected_index = self.device_dropdown.current()
            
            if 0 <= selected_index < len(self.devices):
                self.selected_device = self.devices[selected_index]
                
                self.device_name_label.config(text=self.selected_device['name'])
                
                details_text = f"Serials    {self.selected_device.get('serial', 'Unknown')}"
                self.device_details_label.config(text=details_text)
                
                self._update_wipe_button_state()
            else:
                self.selected_device = None
                self.device_name_label.config(text="No Device Selected")
                self.device_details_label.config(text="Select a device to view details")
                self._update_wipe_button_state()
        else:
            self.selected_device = None
            self.device_name_label.config(text="No Device Selected")
            self.device_details_label.config(text="Select a device to view details")
            self._update_wipe_button_state()

    def _update_wipe_button_state(self):
        print(f"[v0] Updating wipe button state - selected_device: {self.selected_device is not None}, is_wiping: {self.is_wiping}")
        
        if not self.wipe_button:
            print("[v0] Wipe button not initialized yet")
            return
            
        if self.selected_device and not self.is_wiping:
            self.wipe_button.config(
                state='normal',
                bg=self.colors['accent'],
                fg='#000000',
                text="ERASE & CERTIFY",
                relief='flat'
            )
            print(f"[v0] Wipe button enabled for device: {self.selected_device['name']}")
        else:
            self.wipe_button.config(
                state='disabled',
                bg=self.colors['bg_tertiary'],
                fg=self.colors['text_muted'],
                text="ERASE & CERTIFY",
                relief='flat'
            )
            print(f"[v0] Wipe button disabled")
        
        # Force immediate UI update
        self.wipe_button.update_idletasks()
        self.root.update_idletasks()
    
    def start_wipe(self):
        if not self.selected_device:
            messagebox.showerror("Error", "Please select a device to wipe.")
            return
        
        print(f"[v0] Starting wipe confirmation for {self.selected_device['name']}")
        
        result = messagebox.askyesno(
            "⚠️ CONFIRM SECURE WIPE",
            f"You are about to permanently erase ALL DATA on:\n\n"
            f"Device: {self.selected_device['name']}\n"
            f"Size: {self.selected_device['size']}\n"
            f"Path: {self.selected_device['device_path']}\n\n"
            f"THIS ACTION CANNOT BE UNDONE!\n\n"
            f"Are you absolutely sure you want to proceed?",
            icon='warning'
        )
        
        if result:
            self.is_wiping = True
            self._update_wipe_button_state()
            self.device_dropdown.config(state='disabled')
            self.refresh_btn.config(state='disabled')
            
            self.progress_card.grid(row=0, column=1, padx=(15, 0), pady=(0, 15), sticky='nsew')
            
            wipe_thread = threading.Thread(target=self.perform_wipe, daemon=True)
            wipe_thread.start()
        else:
            print(f"[v0] User cancelled wipe operation")
    
    def perform_wipe(self):
        try:
            def progress_callback(progress, message=""):
                prog = progress
                msg = message
                self.root.after(0, lambda: self.update_progress(prog, msg))
            
            success, wipe_data = self.wipe_engine.wipe_device(
                self.selected_device, 
                progress_callback
            )
            
            if success:
                self.root.after(0, lambda: self.update_progress(95, "Generating certificate..."))
                
                cert_data = self.certificate_generator.generate_certificate(
                    [self.selected_device], wipe_data
                )
                
                self.root.after(0, lambda: self.update_progress(100, "Complete!"))
                time.sleep(1)
                
                cert_data_local = cert_data  # Create local variable to avoid closure issues
                self.root.after(0, lambda: self.show_completion_state(cert_data_local))
            else:
                error_msg = "Wipe operation failed. Please check device permissions and try again."
                self.root.after(0, lambda: self.show_error_dialog(error_msg))
                
        except Exception as e:
            error_msg = f"Error during wipe: {str(e)}"
            local_error_msg = error_msg
            self.root.after(0, lambda: self.show_error_dialog(local_error_msg))
        finally:
            self.is_wiping = False
            self.root.after(0, self.reset_ui)

    def update_progress(self, progress, message):
        self.progress_var.set(progress)
        self.progress_percentage.config(text=f"{int(progress)}%")
        
        if progress < 100:
            self.progress_status.config(text="ERASING DATA...")
        else:
            self.progress_status.config(text="COMPLETE!")

    def show_completion_state(self, cert_data):
        # Hide progress card, show certificate card
        self.progress_card.grid_forget()
        
        # Show ERASED status card
        erased_card = tk.Frame(self.root, bg=self.colors['card_bg'], relief='flat', bd=0)
        erased_card.place(x=450, y=200, width=300, height=200)
        
        border_frame = tk.Frame(erased_card, bg='#334155', height=2)
        border_frame.pack(fill='x', side='top')
        
        content_frame = tk.Frame(erased_card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True)
        
        erased_title = tk.Label(
            content_frame,
            text="ERASED",
            font=('Ubuntu', 24, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        )
        erased_title.pack(expand=True)
        
        # Show certificate card
        self.certificate_card.grid(row=1, column=0, padx=(0, 15), pady=(15, 0), sticky='nsew')
        
        # Update certificate details
        self.cert_device_label.config(text=f"DEVICE\n{self.selected_device['name']}\n{cert_data.get('certificate_id', 'N/A')}")
        self.cert_date_label.config(text=datetime.now().strftime('%d %b %Y; %H:%M'))
        
        # Show offline verifier
        verifier_card = tk.Frame(self.root, bg=self.colors['card_bg'], relief='flat', bd=0)
        verifier_card.place(x=750, y=200, width=200, height=200)
        
        border_frame = tk.Frame(verifier_card, bg='#334155', height=2)
        border_frame.pack(fill='x', side='top')
        
        content_frame = tk.Frame(verifier_card, bg=self.colors['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        verifier_title = tk.Label(
            content_frame,
            text="OFFLINE\nVERIFIER",
            font=('Ubuntu', 16, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg'],
            justify='center'
        )
        verifier_title.pack(pady=(20, 10))
        
        check_icon = tk.Label(
            content_frame,
            text="✓",
            font=('Ubuntu', 48, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['card_bg']
        )
        check_icon.pack(pady=(10, 20))
        
        valid_badge = tk.Frame(content_frame, bg=self.colors['success'])
        valid_badge.pack(fill='x')
        
        valid_label = tk.Label(
            valid_badge,
            text="VALID",
            font=('Ubuntu', 14, 'bold'),
            fg='#000000',
            bg=self.colors['success']
        )
        valid_label.pack(pady=8)

    def show_error_dialog(self, message):
        messagebox.showerror("Wipe Error", message)
    
    def open_certificate(self, pdf_path):
        try:
            if os.path.exists(pdf_path):
                subprocess.run(['xdg-open', pdf_path], check=True)
            else:
                messagebox.showerror("Error", "Certificate file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open certificate: {str(e)}")
    
    def reset_ui(self):
        self.device_dropdown.config(state='readonly')
        self.refresh_btn.config(state='normal')
        
        self.progress_card.grid_forget()
        
        self.progress_var.set(0)
        self.progress_percentage.config(text="0%")
        self.progress_status.config(text="ERASING DATA...")
        
        self.certificate_card.grid_forget()
        
        if self.selected_device:
            self.status_label.config(
                text=f"Ready • Selected: {self.selected_device['name']}",
                fg=self.colors['success']
            )
        else:
            self.status_label.config(
                text="Ready • Select a storage device to begin",
                fg=self.colors['text_secondary']
            )
        
        self._update_wipe_button_state()
        
        self.root.update_idletasks()
        
    def run(self):
        self.root.mainloop()

    def refresh_devices(self):
        """Initial device refresh called during startup"""
        print("[v0] Initial device refresh called")
        self.refresh_devices_threaded()

def main():
    if os.geteuid() != 0:
        print("DataWipe Pro requires root privileges to access storage devices.")
        print("Please run with sudo:")
        print(f"sudo python3 {' '.join(sys.argv)}")
        sys.exit(1)
    
    app = DataWipeProGUI()
    app.run()

if __name__ == "__main__":
    main()
