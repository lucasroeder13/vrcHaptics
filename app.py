import sys
import os

from core.loader import Loader
from core.config_manager import ConfigManager
from core.osc_handler import OSCHandler
from ui.main_window import MainWindow
from schemas.contacts import Contact
from schemas.bindings import Binding

class MainApp:
    def __init__(self):
        self.loader = Loader()
        self.modules = self.loader.load_modules()
        self._scan_all_modules()

    def _scan_all_modules(self):
        for name, module in self.modules.items():
            if hasattr(module, 'scan'):
                print(f"Auto-scanning devices for module: {name}")
                try:
                    module.scan()
                except Exception as e:
                    print(f"Error during auto-scan for module '{name}': {e}")

if __name__ == "__main__":
    app = MainApp()
    
    print("Loading Configuration...")
    config_data = ConfigManager.load_config()
    
    # Parse Contacts and Bindings
    contacts = []
    if "contacts" in config_data:
        for c in config_data["contacts"]:
            try:
                # Ensure it's a dict
                if isinstance(c, dict):
                    contacts.append(Contact(**c))
            except Exception as e:
                print(f"Error parsing contact: {e}")
                
    bindings = []
    if "bindings" in config_data:
        for b in config_data["bindings"]:
            try:
                if isinstance(b, dict):
                    bindings.append(Binding(**b))
            except Exception as e:
                print(f"Error parsing binding: {e}")

    print(f"Loaded {len(contacts)} contacts and {len(bindings)} bindings.")

    print("Initializing OSC Handler...")
    osc_handler = OSCHandler(app.modules, contacts, bindings)
    
    print("Starting Main Window...")
    # Pass ConfigManager class and the handler
    gui = MainWindow(ConfigManager, osc_handler)
    gui.mainloop()
    
    # Cleanup on exit
    print("Shutting down...")
    osc_handler.shutdown()
