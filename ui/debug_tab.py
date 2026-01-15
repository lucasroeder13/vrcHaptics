import tkinter as tk
from tkinter import ttk
import datetime

class DebugTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.paused = False
        self._create_widgets()

    def _create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Button(toolbar, text="Clear", command=self._clear_log).pack(side=tk.LEFT, padx=2)
        self.pause_btn = ttk.Button(toolbar, text="Pause", command=self._toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        # Log Area (Treeview for structured data)
        columns = ("time", "address", "value")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("time", text="Time")
        self.tree.heading("address", text="OSC Address")
        self.tree.heading("value", text="Value")
        
        self.tree.column("time", width=100, stretch=False)
        self.tree.column("address", width=400)
        self.tree.column("value", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")

    def _clear_log(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def log_message(self, address, *args):
        if self.paused:
            return
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        value = str(args[0]) if args else "None"
        
        # Insert at top
        self.tree.insert("", 0, values=(timestamp, address, value))
        
        # Limit size
        if len(self.tree.get_children()) > 200:
            last = self.tree.get_children()[-1]
            self.tree.delete(last)
