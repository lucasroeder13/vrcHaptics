import tkinter as tk
from tkinter import ttk, messagebox

class DevicesTab(ttk.Frame):
    def __init__(self, parent, modules):
        super().__init__(parent)
        self.modules = modules
        self._create_widgets()

    def _create_widgets(self):
        # Title
        ttk.Label(self, text="Available Modules / Devices", font=("Helvetica", 12, "bold")).pack(pady=10)

        # Scrollable container? For now just a frame
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        if not self.modules:
            ttk.Label(self.list_frame, text="No modules found.").pack()
            return

        for name, module in self.modules.items():
            self._create_module_section(name, module)

    def _create_module_section(self, name, module):
        # Main Frame for the Module
        section_frame = ttk.LabelFrame(self.list_frame, text=getattr(module, 'name', name))
        section_frame.pack(fill=tk.X, pady=5, ipadx=5, ipady=5)
        
        # --- Header Row (Controls) ---
        header_frame = ttk.Frame(section_frame)
        header_frame.pack(fill=tk.X)
        
        # Connect/Test Button
        if hasattr(module, 'run'):
            btn_connect = ttk.Button(header_frame, text="Open Interface / Test", command=lambda m=module: self._on_connect(m))
            btn_connect.pack(side=tk.LEFT, padx=5)

        # Scan Devices Button
        if hasattr(module, 'scan'):
            btn_scan = ttk.Button(header_frame, text="Scan Devices", command=lambda m=module, f=section_frame: self._on_scan(m, f))
            btn_scan.pack(side=tk.LEFT, padx=5)

        # --- Device List Container ---
        # We will create a frame specifically to hold the device rows so we can clear it easily
        device_container = ttk.Frame(section_frame)
        device_container.pack(fill=tk.X, expand=True, pady=5)
        
        # Store a reference to the container on the frame so we can find it later (hacky but works)
        section_frame.device_container = device_container
        
        # Initial population if devices already exist
        if hasattr(module, 'devices'):
            self._render_devices(module.devices, device_container)

    def _on_scan(self, module, section_frame):
        try:
            # Call scan() on module
            devices = module.scan()
            # Update UI
            if hasattr(section_frame, 'device_container'):
                self._render_devices(devices, section_frame.device_container)
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {e}")

    def _render_devices(self, devices, container):
        # Clear existing
        for widget in container.winfo_children():
            widget.destroy()

        if not devices:
            ttk.Label(container, text="No devices found.", font=("Arial", 9, "italic")).pack(anchor=tk.W, padx=20)
            return

        # Headers
        header = ttk.Frame(container)
        header.pack(fill=tk.X, padx=20)
        ttk.Label(header, text="ID", width=45, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text="Name", width=20, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text="Status", width=15, font=("Arial", 9, "bold")).pack(side=tk.LEFT)

        # Rows
        for dev in devices:
            row = ttk.Frame(container)
            row.pack(fill=tk.X, padx=20, pady=1)
            
            # Assuming dev is a dict for now: {'id': '...', 'name': '...', 'info': '...'}
            dev_id = dev.get('id', 'Unknown')
            dev_name = dev.get('name', 'Unknown')
            dev_status = dev.get('status', '-')
            
            ttk.Label(row, text=dev_id, width=45).pack(side=tk.LEFT)
            ttk.Label(row, text=dev_name, width=20).pack(side=tk.LEFT)
            ttk.Label(row, text=dev_status, width=15).pack(side=tk.LEFT)

    def _on_connect(self, module):
        try:
            result = module.run()
        except Exception as e:
            messagebox.showerror("Error", f"Module failed: {e}")
