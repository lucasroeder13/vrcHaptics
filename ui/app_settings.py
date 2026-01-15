import tkinter as tk
from tkinter import ttk
from core.config_manager import ConfigManager

class AppSettingsTab(ttk.Frame):
    def __init__(self, parent, commands):
        """
        commands: dict containing callable 'import', 'export', 'save_app_settings'
        """
        super().__init__(parent)
        self.commands = commands
        self.settings = ConfigManager.get_app_settings()
        self._create_widgets()

    def _create_widgets(self):
        # Frame
        frame = ttk.LabelFrame(self, text="General Settings")
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # OSC Port
        ttk.Label(frame, text="OSC Listen Port:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.osc_port_var = tk.IntVar(value=self.settings.get("osc_port", 9001))
        ttk.Entry(frame, textvariable=self.osc_port_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text="(Requires Restart)", font=("Arial", 8, "italic")).grid(row=0, column=2, sticky="w", padx=5)
        
        ttk.Button(frame, text="Save Settings", command=self._save_settings).grid(row=1, column=0, columnspan=2, pady=5)

        # Config Management
        config_frame = ttk.LabelFrame(self, text="Configuration Management")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(config_frame, text="Import JSON", command=self.commands.get('import')).pack(side=tk.LEFT, padx=5, pady=10)
        ttk.Button(config_frame, text="Export JSON", command=self.commands.get('export')).pack(side=tk.LEFT, padx=5, pady=10)

    def _save_settings(self):
        new_settings = {
            "osc_port": self.osc_port_var.get()
        }
        if self.commands.get('save_app_settings'):
            self.commands['save_app_settings'](new_settings)
