import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any
from schemas.bindings import Binding

class MappingsTab(ttk.Frame):
    def __init__(self, parent, modules, contacts_provider, on_change=None):
        """
        contacts_provider: A function or object that returns the current list of contacts.
                           Since ContactsTab holds the state, we can pass a lambda accessing it.
        """
        super().__init__(parent)
        self.modules = modules
        self.get_contacts = contacts_provider
        self.on_change = on_change
        self.bindings: List[Binding] = []
        self.selected_binding_index = None

        self._create_widgets()

    def load_data(self, bindings_data):
        self.bindings = []
        for b_dict in bindings_data:
            try:
                self.bindings.append(Binding(**b_dict))
            except Exception as e:
                print(f"Skipping invalid binding: {e}")
        self._refresh_list()

    def _notify_change(self):
        if self.on_change:
            self.on_change()

    def _create_widgets(self):
        # Layout: Left (List of Bindings), Right (Edit Form)
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Left: List ---
        left_frame = ttk.Frame(paned)
        ttk.Label(left_frame, text="Active Mappings").pack(pady=5)
        
        self.bindings_listbox = tk.Listbox(left_frame)
        self.bindings_listbox.pack(fill=tk.BOTH, expand=True)
        self.bindings_listbox.bind('<<ListboxSelect>>', self._on_select)

        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="New Mapping", command=self._new_binding).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Delete", command=self._delete_binding).pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        paned.add(left_frame, minsize=200)

        # --- Right: Editor ---
        right_frame = ttk.LabelFrame(paned, text="Mapping Configuration")
        self.editor_frame = right_frame
        
        row = 0
        
        # 1. Select Contact
        ttk.Label(right_frame, text="Trigger (Contact):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.contact_combobox = ttk.Combobox(right_frame, state="readonly")
        self.contact_combobox.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        # Bind popup event to refresh list
        self.contact_combobox.bind('<Button-1>', self._refresh_contacts_combo)
        row += 1

        # 2. Select Module & Device
        ttk.Label(right_frame, text="Target (Device):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.device_combobox = ttk.Combobox(right_frame, state="readonly")
        self.device_combobox.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        # Bind popup event to refresh list (devices might be scanned any time)
        self.device_combobox.bind('<Button-1>', self._refresh_devices_combo)
        row += 1

        # 3. Settings
        ttk.Label(right_frame, text="Reaction Type:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.reaction_var = tk.StringVar(value="vibrate")
        self.reaction_combo = ttk.Combobox(right_frame, textvariable=self.reaction_var, values=["vibrate", "shock", "sound"], state="readonly")
        self.reaction_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        ttk.Label(right_frame, text="Intensity (0.0 - 1.0):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.intensity_var = tk.DoubleVar(value=1.0)
        self.intensity_scale = ttk.Scale(right_frame, from_=0.0, to=1.0, variable=self.intensity_var, orient=tk.HORIZONTAL)
        self.intensity_scale.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        ttk.Label(right_frame, text="Duration (sec):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.duration_var = tk.DoubleVar(value=0.5)
        self.duration_entry = ttk.Entry(right_frame, textvariable=self.duration_var)
        self.duration_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # --- Advanced Mapping (Collapsible or just separated) ---
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        ttk.Label(right_frame, text="Value Mapping (Float/Int Inputs)", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1

        # Use Mapping Checkbox
        self.use_mapping_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_frame, text="Enable Input Mapping", variable=self.use_mapping_var, command=self._toggle_mapping_fields).grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1

        # Mapping Fields Container
        self.mapping_frame = ttk.Frame(right_frame)
        self.mapping_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10)
        row += 1

        # Input Range
        ttk.Label(self.mapping_frame, text="Input Range (Min -> Max):").grid(row=0, column=0, sticky="w")
        self.input_min_var = tk.DoubleVar(value=0.0)
        self.input_max_var = tk.DoubleVar(value=1.0)
        entry_frame_in = ttk.Frame(self.mapping_frame)
        entry_frame_in.grid(row=0, column=1, sticky="w")
        ttk.Entry(entry_frame_in, textvariable=self.input_min_var, width=8).pack(side=tk.LEFT)
        ttk.Label(entry_frame_in, text=" -> ").pack(side=tk.LEFT)
        ttk.Entry(entry_frame_in, textvariable=self.input_max_var, width=8).pack(side=tk.LEFT)

        # Output Range
        ttk.Label(self.mapping_frame, text="Output Intensity (Min -> Max):").grid(row=1, column=0, sticky="w")
        self.output_min_var = tk.DoubleVar(value=0.0)
        self.output_max_var = tk.DoubleVar(value=1.0)
        entry_frame_out = ttk.Frame(self.mapping_frame)
        entry_frame_out.grid(row=1, column=1, sticky="w")
        ttk.Entry(entry_frame_out, textvariable=self.output_min_var, width=8).pack(side=tk.LEFT)
        ttk.Label(entry_frame_out, text=" -> ").pack(side=tk.LEFT)
        ttk.Entry(entry_frame_out, textvariable=self.output_max_var, width=8).pack(side=tk.LEFT)

        # Curve Type
        ttk.Label(self.mapping_frame, text="Curve Type:").grid(row=2, column=0, sticky="w", pady=5)
        self.curve_var = tk.StringVar(value="linear")
        self.curve_combo = ttk.Combobox(self.mapping_frame, textvariable=self.curve_var, values=["linear", "exponential", "logarithmic", "threshold"], state="readonly")
        self.curve_combo.grid(row=2, column=1, sticky="w", pady=5)
        
        self._toggle_mapping_fields() # Initial State

        # Save Button
        ttk.Button(right_frame, text="Save Mapping", command=self._save_binding).grid(row=row, column=0, columnspan=2, pady=20)
        
        right_frame.columnconfigure(1, weight=1)
        paned.add(right_frame)

    def _toggle_mapping_fields(self):
        if self.use_mapping_var.get():
            for child in self.mapping_frame.winfo_children():
                child.state(['!disabled'])
        else:
            for child in self.mapping_frame.winfo_children():
                child.state(['disabled'])

    def _refresh_contacts_combo(self, event=None):
        contacts = self.get_contacts()
        values = [f"{c.name} ({c.id})" for c in contacts]
        self.contact_combobox['values'] = values

    def _refresh_devices_combo(self, event=None):
        # Aggregate all devices from all modules
        device_list = []
        for mod_name, module in self.modules.items():
            if hasattr(module, 'devices') and module.devices:
                for dev in module.devices:
                    # Format: "ModuleName : DeviceName (ID)"
                    display = f"{mod_name} : {dev.get('name', 'Unknown')} ({dev.get('id', '?')})"
                    device_list.append(display)
        
        if not device_list:
            device_list = ["No devices found (Try scanning in Devices tab)"]
            
        self.device_combobox['values'] = device_list

    def _new_binding(self):
        self.selected_binding_index = None
        self.bindings_listbox.selection_clear(0, tk.END)
        self._clear_form()

    def _clear_form(self):
        self.contact_combobox.set('')
        self.device_combobox.set('')
        self.reaction_var.set('vibrate')
        self.intensity_var.set(1.0)
        self.duration_var.set(0.5)
        
        self.use_mapping_var.set(False)
        self.input_min_var.set(0.0)
        self.input_max_var.set(1.0)
        self.output_min_var.set(0.0)
        self.output_max_var.set(1.0)
        self.curve_var.set('linear')
        self._toggle_mapping_fields()

    def _on_select(self, event):
        sel = self.bindings_listbox.curselection()
        if not sel:
            return
        
        index = sel[0]
        self.selected_binding_index = index
        binding = self.bindings[index]

        # Populate form
        # We need to match the combo strings
        self.contact_combobox.set(f"{binding.contact_name} ({binding.contact_id})")
        self.device_combobox.set(f"{binding.module_name} : {binding.device_name} ({binding.device_id})")
        self.reaction_var.set(binding.reaction_type)
        self.intensity_var.set(binding.intensity)
        self.duration_var.set(binding.duration)
        
        # Mapping fields
        self.use_mapping_var.set(getattr(binding, 'use_mapping', False))
        self.input_min_var.set(getattr(binding, 'input_min', 0.0))
        self.input_max_var.set(getattr(binding, 'input_max', 1.0))
        self.output_min_var.set(getattr(binding, 'output_min', 0.0))
        self.output_max_var.set(getattr(binding, 'output_max', 1.0))
        self.curve_var.set(getattr(binding, 'curve_type', 'linear'))
        self._toggle_mapping_fields()

    def _save_binding(self):
        # Parse Contact
        c_str = self.contact_combobox.get()
        if not c_str:
            messagebox.showwarning("Missing Info", "Please select a contact.")
            return
        # Parse like "Name (ID)"
        try:
            c_name = c_str.rsplit(' (', 1)[0]
            c_id = c_str.rsplit(' (', 1)[1][:-1]
        except:
            messagebox.showerror("Error", "Invalid contact format selected.")
            return

        # Parse Device
        d_str = self.device_combobox.get()
        if not d_str or "No devices found" in d_str:
            messagebox.showwarning("Missing Info", "Please select a device.")
            return
        # Format: "Module : Device (ID)"
        try:
            parts = d_str.split(' : ')
            mod_name = parts[0]
            rest = parts[1]
            d_name = rest.rsplit(' (', 1)[0]
            d_id = rest.rsplit(' (', 1)[1][:-1]
        except:
            messagebox.showerror("Error", "Invalid device format selected.")
            return

        binding = Binding(
            contact_id=c_id,
            contact_name=c_name,
            module_name=mod_name,
            device_id=d_id,
            device_name=d_name,
            reaction_type=self.reaction_var.get(),
            intensity=self.intensity_var.get(),
            duration=self.duration_var.get(),
            # Mapping fields
            use_mapping=self.use_mapping_var.get(),
            input_min=self.input_min_var.get(),
            input_max=self.input_max_var.get(),
            output_min=self.output_min_var.get(),
            output_max=self.output_max_var.get(),
            curve_type=self.curve_var.get()
        )

        if self.selected_binding_index is not None:
            self.bindings[self.selected_binding_index] = binding
        else:
            self.bindings.append(binding)
            
        self._refresh_list()
        self._new_binding() # Reset selection
        messagebox.showinfo("Saved", "Mapping saved!")
        self._notify_change()

    def _delete_binding(self):
        sel = self.bindings_listbox.curselection()
        if not sel:
            return
        del self.bindings[sel[0]]
        self._refresh_list()
        self._new_binding()
        self._notify_change()

    def _refresh_list(self):
        self.bindings_listbox.delete(0, tk.END)
        for b in self.bindings:
            self.bindings_listbox.insert(tk.END, f"{b.contact_name} -> {b.device_name} ({b.reaction_type})")
