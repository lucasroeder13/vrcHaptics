import tkinter as tk
from tkinter import ttk
import time
import threading

class OSCFinderDialog(tk.Toplevel):
    def __init__(self, parent, osc_sniffer, on_select):
        super().__init__(parent)
        self.title("OSC Finder / Scanner")
        self.geometry("600x400")
        
        self.osc_sniffer = osc_sniffer
        self.on_select = on_select
        self.found_addresses = set()
        
        # Buffer
        self.update_lock = threading.Lock()
        self.updates = {} # address -> (val, type, time)
        
        self._create_widgets()
        
        # Start listening
        self.osc_sniffer.add_listener(self._on_osc_message)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start loop
        self._update_loop()

    def _create_widgets(self):
        # Info Label
        ttk.Label(self, text="Listening for OSC messages... Trigger your avatar parameters now.", 
                 font=("Helvetica", 10)).pack(pady=5)
        
        # Columns: Time, Address, Type, Value
        columns = ("time", "address", "type", "value")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("time", text="Time")
        self.tree.column("time", width=80)
        
        self.tree.heading("address", text="OSC Address")
        self.tree.column("address", width=300)
        
        self.tree.heading("type", text="Type")
        self.tree.column("type", width=60)
        
        self.tree.heading("value", text="Value")
        self.tree.column("value", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(btn_frame, text="Use Selected", command=self._use_selected).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=5)

    def _on_osc_message(self, address, *args):
        # Buffer updates
        val = args[0] if args else "None"
        val_type = type(val).__name__
        timestamp = time.strftime("%H:%M:%S")
        
        with self.update_lock:
            self.updates[address] = (val, val_type, timestamp)

    def _update_loop(self):
        to_process = {}
        with self.update_lock:
            to_process = self.updates.copy()
            self.updates.clear()
            
        if to_process:
            self._batch_update(to_process)
            
        self.after(50, self._update_loop)

    def _batch_update(self, data):
        for address, (val, val_type, timestamp) in data.items():
             if address in self.found_addresses:
                  # Update
                  for item in self.tree.get_children():
                       if self.tree.item(item, "values")[1] == address:
                            self.tree.item(item, values=(timestamp, address, val_type, str(val)))
                            break
             else:
                  # Add new
                  self.found_addresses.add(address)
                  self.tree.insert("", 0, values=(timestamp, address, val_type, str(val)))

    def _use_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        address = item["values"][1]
        
        self.on_select(address)
        self._on_close()

    def _clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.found_addresses.clear()

    def _on_close(self):
        self.osc_sniffer.remove_listener(self._on_osc_message)
        self.destroy()
