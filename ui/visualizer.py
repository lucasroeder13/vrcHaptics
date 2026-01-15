import tkinter as tk
from tkinter import ttk

class VisualizerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.bars = {}
        self.contacts_map = {} # Path -> ID map
        self.contact_widgets = {} # ID -> (Label, ProgressBar, ValueLabel)
        
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        ttk.Label(self.scrollable_frame, text="Active Inputs Visualizer", font=("Helvetica", 12, "bold")).pack(pady=10)

    def update_contacts(self, contacts):
        # Clear existing
        for w in self.scrollable_frame.winfo_children():
            if w.winfo_class() == 'TLabel' and w.cget("text") == "Active Inputs Visualizer":
                continue
            w.destroy()
            
        self.bars = {}
        self.contacts_map = {}
        self.contact_widgets = {}

        if not contacts:
            ttk.Label(self.scrollable_frame, text="No contacts configured.").pack(padx=20)
            return

        for contact in contacts:
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            ttk.Label(frame, text=contact.name, width=20).pack(side=tk.LEFT)
            
            pb = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
            pb.pack(side=tk.LEFT, padx=10)
            
            val_lbl = ttk.Label(frame, text="0.0")
            val_lbl.pack(side=tk.LEFT)
            
            # Map OSC path to this widget set
            self.contacts_map[contact.osc_path] = contact.name # Or use ID
            self.contact_widgets[contact.osc_path] = (pb, val_lbl)

    def process_osc_message(self, address, args):
        if address in self.contact_widgets:
            pb, val_lbl = self.contact_widgets[address]
            
            val = 0.0
            display_text = "0.0"
            percent = 0.0

            if args:
                raw_val = args[0]
                
                if isinstance(raw_val, bool):
                     val = 1.0 if raw_val else 0.0
                     display_text = "True" if raw_val else "False"
                     percent = val * 100
                elif isinstance(raw_val, int):
                     val = float(raw_val)
                     display_text = str(raw_val)
                     # Attempt to normalize if it looks like a byte (0-255) vs just 0-1
                     # But most importantly clamp for progressbar
                     if val > 1.0: 
                         # Maybe it's 0-255?
                         percent = (val / 255.0) * 100
                     else:
                         percent = val * 100
                elif isinstance(raw_val, float):
                     val = raw_val
                     display_text = f"{val:.2f}"
                     percent = val * 100
                else:
                     display_text = str(raw_val)

            # Update UI in thread-safe way (usually run in main thread, but OSC might be threaded)
            # Tkinter is not thread safe, but if process_osc_message is called from main loop it's fine.
            # OSCSniffer likely callbacks in its thread.
            
            try:
                # Clamp percent
                if percent > 100: percent = 100
                if percent < 0: percent = 0
                
                pb['value'] = percent
                val_lbl['text'] = display_text
            except:
                pass 
