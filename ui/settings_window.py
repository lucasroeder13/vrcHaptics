import tkinter as tk
from tkinter import ttk, messagebox
from ui.app_settings import AppSettingsTab
from core.config_manager import ConfigManager

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, on_save_callback=None):
        super().__init__(parent)
        self.title("General Settings")
        self.geometry("600x400")
        
        self.on_save_callback = on_save_callback
        
        self._create_widgets()

    def _create_widgets(self):
        # Create Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: App Settings (General)
        cmds = {
            'save_app_settings': self._save_app_settings
        }
        self.app_settings_tab = AppSettingsTab(notebook, cmds)
        notebook.add(self.app_settings_tab, text="General Settings")

    def _save_app_settings(self, settings):
        ConfigManager.save_config(
            app_settings=settings
        )
        messagebox.showinfo("Saved", "Settings saved. Restart application to apply port changes.")
        if self.on_save_callback:
            self.on_save_callback()
