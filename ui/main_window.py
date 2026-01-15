import tkinter as tk
from tkinter import ttk, messagebox
import logging
import queue
import threading
import time

from .visualizer import VisualizerTab
from .contacts import ContactsTab
from .mappings import MappingsTab
from .devices import DevicesTab
from .debug_tab import DebugTab
from .app_settings import AppSettingsTab
from core.osc_sniffer import OSCSniffer

logger = logging.getLogger(__name__)

class MainWindow(tk.Tk):
    def __init__(self, config_manager, osc_handler):
        super().__init__()

        self.config = config_manager
        self.osc_handler = osc_handler
        
        self.title("vrcHaptics - Main Window")
        self.geometry("1000x700")
        
        # UI Update Queue to prevent freezing
        self.ui_queue = queue.Queue()
        self.visualizer_lock = threading.Lock()
        
        # Start OSC Sniffer (Create early to pass to tabs)
        self.osc_port = self.config.get_app_settings().get("osc_port", 9001)
        self.osc_sniffer = OSCSniffer(port=self.osc_port)
        self.osc_sniffer.add_listener(self._on_osc_message_buffered)
        self.osc_sniffer.start()
        
        # Initialize GUI
        self._init_ui()
        
        # Load Data into Tabs
        if hasattr(self.osc_handler, 'contacts'):
             self.contacts_tab.load_data(self.osc_handler.contacts)
             self.visualizer_tab.update_contacts(self.osc_handler.contacts)
             
        if hasattr(self.osc_handler, 'bindings'):
             # MappingsTab needs valid contacts first, which we just loaded
             self.mappings_tab.load_data(self.osc_handler.bindings)
        
        # Setup window close handler
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start UI Update Loop
        self.after(33, self._ui_update_loop) # ~30fps update rate for UI

    def _init_ui(self):
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize Tabs
        self.visualizer_tab = VisualizerTab(self.notebook)
        
        # Pass osc_sniffer to ContactsTab
        self.contacts_tab = ContactsTab(
            self.notebook, 
            self.osc_sniffer, 
            on_change=self._on_config_changed
        )
        
        # Pass modules and contacts_provider to MappingsTab
        self.mappings_tab = MappingsTab(
            self.notebook, 
            self.osc_handler.loaded_modules, 
            lambda: self.contacts_tab.contacts,
            on_change=self._on_config_changed
        )
        
        self.devices_tab = DevicesTab(self.notebook, self.osc_handler.loaded_modules)
        self.debug_tab = DebugTab(self.notebook)
        
        # Define commands for AppSettingsTab
        settings_commands = {
            'import': self._import_config_dialog,
            'export': self._export_config_dialog,
            'save_app_settings': self._save_app_settings
        }
        self.app_settings_tab = AppSettingsTab(self.notebook, settings_commands)
        
        # Add Tabs
        self.notebook.add(self.visualizer_tab, text="Visualizer")
        self.notebook.add(self.contacts_tab, text="Contacts")
        self.notebook.add(self.mappings_tab, text="Mappings")
        self.notebook.add(self.devices_tab, text="Devices")
        self.notebook.add(self.debug_tab, text="Debug")
        self.notebook.add(self.app_settings_tab, text="Settings")

    def _import_config_dialog(self):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not filepath:
            return
            
        try:
            data = self.config.import_config(filepath)
            
            # Reload Tabs
            if "contacts" in data:
                 self.contacts_tab.load_data(data["contacts"])
                 # Update OSCHandler
                 # Ideally we should reconstruct Contact objects here if config manager returned dicts
                 # But load_data handles dicts now.
                 # The handler needs actual objects.
                 # We can get them back from the tab? 
                 # Or just rely on re-saving logic. 
                 self.visualizer_tab.update_contacts(self.contacts_tab.contacts)

            if "bindings" in data:
                 self.mappings_tab.load_data(data["bindings"])
                 
            # Note: We probably need to explicitly update self.osc_handler's knowledge
            # self.osc_handler.update_config(self.contacts_tab.contacts, self.mappings_tab.bindings)
            # But the tabs manage their own lists. 
            # We should probably have a "Save/Apply" button generally?
            # Or assume import implies load-into-ui-only until saved.
            
            messagebox.showinfo("Import", "Configuration imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _export_config_dialog(self):
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not filepath:
            return
            
        try:
            self.config.export_config(filepath, self.contacts_tab.contacts, self.mappings_tab.bindings)
            messagebox.showinfo("Export", "Configuration exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _save_app_settings(self, new_settings):
        try:
            # Re-save everything including app settings
            self.config.save_config(
                contacts=self.contacts_tab.contacts,
                bindings=self.mappings_tab.bindings,
                app_settings=new_settings
            )
            messagebox.showinfo("Saved", "Settings saved successfully. Restart required for some changes.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _on_config_changed(self):
        """
        Called when contacts or bindings are modified in the UI.
        Updates the background OSC handler so it uses the new rules immediately.
        """
        if hasattr(self.osc_handler, 'update_config'):
             self.osc_handler.update_config(
                 self.contacts_tab.contacts,
                 self.mappings_tab.bindings
             )
        
        # Also update visualizer contacts if needed
        if hasattr(self.visualizer_tab, 'update_contacts'):
             self.visualizer_tab.update_contacts(self.contacts_tab.contacts)

    def _on_osc_message_buffered(self, address, value):
        """
        Callback from the background OSC thread.
        python-osc passes (address, value_tuple).
        We put it in the queue for the main thread.
        """
        self.ui_queue.put((address, value))

    def _ui_update_loop(self):
        """
        Main thread loop to process buffered OSC messages.
        """
        try:
            # Process up to N messages to prevent starving the GUI if flood happens
            count = 0
            while not self.ui_queue.empty() and count < 100:
                address, value = self.ui_queue.get_nowait()
                
                # Update Visualizer (Thread Safe via Loop)
                # value is the tuple of args from python-osc
                if hasattr(self.visualizer_tab, 'process_osc_message'):
                     # visualizer expects (address, args_list)
                     self.visualizer_tab.process_osc_message(address, value)

                # Update Debug Tab
                if hasattr(self.debug_tab, 'log_message'):
                    # debug_tab expects (address, *args)
                    self.debug_tab.log_message(address, *value)
                
                # Process Logic (Bindings/Triggers)
                # osc_handler.map_message expects (address, args_list)
                if hasattr(self.osc_handler, 'map_message'):
                    self.osc_handler.map_message(address, value)
                
                count += 1
                
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error in UI update loop: {e}", exc_info=True)
            print(f"Error in UI update loop: {e}")
        finally:
            # Schedule next update
            self.after(33, self._ui_update_loop)

    def _on_close(self):
        try:
            self.osc_sniffer.stop()
            # Stop any other threads or handlers
            if hasattr(self.osc_handler, 'shutdown'):
                 self.osc_handler.shutdown()
        except Exception as e:
            logger.error(f"Error closing: {e}")
        finally:
            self.destroy()
