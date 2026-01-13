import tkinter as tk
from tkinter import ttk
from ui.devices import DevicesTab
from ui.contacts import ContactsTab
from ui.mappings import MappingsTab
from core.config_manager import ConfigManager
from core.osc_sniffer import OSCSniffer
from core.osc_handler import OSCHandler

class MainWindow(tk.Tk):
    def __init__(self, modules):
        super().__init__()
        self.title("VRC Haptics Manager")
        self.geometry("900x600")
        
        self.modules = modules
        
        # Initialize OSC components
        self.osc_sniffer = OSCSniffer(9001)
        self.osc_handler = OSCHandler(self.modules, [], [])
        self.osc_sniffer.start()
        self.osc_sniffer.add_listener(self.osc_handler.map_message)
        
        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        # Create Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Connect Devices / Modules
        self.devices_tab = DevicesTab(notebook, self.modules)
        notebook.add(self.devices_tab, text="Devices & Modules")

        # Tab 2: Contacts & OSC
        # Pass auto-save callback
        self.contacts_tab = ContactsTab(notebook, self.osc_sniffer, on_change=self._auto_save)
        notebook.add(self.contacts_tab, text="Contacts & OSC Setup")

        # Tab 3: Mappings / Bindings
        # We pass a lambda to get the list of contacts dynamically from the contacts tab
        self.mappings_tab = MappingsTab(notebook, self.modules, lambda: self.contacts_tab.contacts, on_change=self._auto_save)
        notebook.add(self.mappings_tab, text="Mappings & Reactivity")

        # Create a status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_config(self):
        data = ConfigManager.load_config()
        self.contacts_tab.load_data(data.get("contacts", []))
        self.mappings_tab.load_data(data.get("bindings", []))
        
        # Update runtime handler
        self.osc_handler.update_config(self.contacts_tab.contacts, self.mappings_tab.bindings)
        
        self.status_var.set("Configuration loaded.")

    def _auto_save(self):
        ConfigManager.save_config(
            contacts=self.contacts_tab.contacts,
            bindings=self.mappings_tab.bindings
        )
        
        # Update runtime handler
        self.osc_handler.update_config(self.contacts_tab.contacts, self.mappings_tab.bindings)
        
        self.status_var.set("Configuration saved.")

    def destroy(self):
        if self.osc_sniffer:
            self.osc_sniffer.stop()
        super().destroy()
