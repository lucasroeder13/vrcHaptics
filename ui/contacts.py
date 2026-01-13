import tkinter as tk
from tkinter import ttk, messagebox
from schemas.contacts import Contact
# from core.osc_sniffer import OSCSniffer

class ContactsTab(ttk.Frame):
    def __init__(self, parent, osc_sniffer, on_change=None):
        super().__init__(parent)
        
        self.on_change = on_change
        self.contacts = [] # List of Contact objects
        self.selected_contact_index = None
        self.sniffer = osc_sniffer 
        self.sniffing = False

        self._create_widgets()
        # self._load_dummy_data() # Removed in favor of proper loading

    def load_data(self, contacts_data):
        self.contacts = []
        for c_dict in contacts_data:
            try:
                self.contacts.append(Contact(**c_dict))
            except Exception as e:
                print(f"Skipping invalid contact: {e}")
        self._refresh_list()
        
    def _notify_change(self):
        if self.on_change:
            self.on_change()

    def _create_widgets(self):
        # Main layout: Left (List), Right (Details)
        main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Left Side: Contact List ---
        left_frame = ttk.Frame(main_paned)
        self.contact_listbox = tk.Listbox(left_frame)
        self.contact_listbox.pack(fill=tk.BOTH, expand=True)
        self.contact_listbox.bind('<<ListboxSelect>>', self._on_contact_select)
        
        # Add Contact Button
        add_btn = ttk.Button(left_frame, text="Add Contact", command=self._add_contact)
        add_btn.pack(fill=tk.X, pady=2)
        
        main_paned.add(left_frame, minsize=200)

        # --- Right Side: Details Form ---
        right_frame = ttk.LabelFrame(main_paned, text="Contact Details")
        
        # Grid layout for form
        row = 0
        
        # Name
        ttk.Label(right_frame, text="Name:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(right_frame, textvariable=self.name_var)
        self.name_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # ID
        ttk.Label(right_frame, text="ID:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(right_frame, textvariable=self.id_var)
        self.id_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # Type (Internal Type)
        ttk.Label(right_frame, text="Contact Type (Int):").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.type_var = tk.IntVar(value=0)
        self.type_entry = ttk.Entry(right_frame, textvariable=self.type_var)
        self.type_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # OSC Path
        ttk.Label(right_frame, text="OSC Path:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        path_frame = ttk.Frame(right_frame)
        path_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        
        self.osc_path_var = tk.StringVar()
        self.osc_path_entry = ttk.Entry(path_frame, textvariable=self.osc_path_var)
        self.osc_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sniff_btn = ttk.Button(path_frame, text="Find/Scan", command=self._toggle_sniff)
        self.sniff_btn.pack(side=tk.RIGHT, padx=5)
        
        row += 1

        # Input Type (Bool, Int, Float)
        ttk.Label(right_frame, text="Input Type:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.input_type_var = tk.StringVar(value="float")
        type_options = ["bool", "int", "float"]
        self.input_type_menu = ttk.OptionMenu(right_frame, self.input_type_var, "float", *type_options)
        self.input_type_menu.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # Save Button
        save_btn = ttk.Button(right_frame, text="Save Changes", command=self._save_changes)
        save_btn.grid(row=row, column=0, columnspan=2, pady=10)
        
        right_frame.columnconfigure(1, weight=1)
        main_paned.add(right_frame)

    def _load_dummy_data(self):
        # Just for testing / placeholder
        c1 = Contact(name="Left Hand", id="lh_tact", type=1, osc_path="/avatar/parameters/LeftHandHaptic", input_type="float")
        c2 = Contact(name="Right Hand", id="rh_tact", type=1, osc_path="/avatar/parameters/RightHandHaptic", input_type="bool")
        self.contacts = [c1, c2]
        self._refresh_list()

    def _refresh_list(self):
        self.contact_listbox.delete(0, tk.END)
        for contact in self.contacts:
            self.contact_listbox.insert(tk.END, contact.name)

    def _on_contact_select(self, event):
        selection = self.contact_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.selected_contact_index = index
        contact = self.contacts[index]
        
        self.name_var.set(contact.name)
        self.id_var.set(contact.id)
        self.type_var.set(contact.type)
        self.osc_path_var.set(contact.osc_path if contact.osc_path else "")
        self.input_type_var.set(contact.input_type)

    def _add_contact(self):
        new_c = Contact(name="New Contact", id="new_id", type=0, input_type="float")
        self.contacts.append(new_c)
        self._refresh_list()
        self.contact_listbox.selection_clear(0, tk.END)
        self.contact_listbox.selection_set(tk.END)
        self._on_contact_select(None)
        self._notify_change()

    def _save_changes(self):
        if self.selected_contact_index is None:
            messagebox.showwarning("Warning", "No contact selected")
            return
            
        try:
            c = self.contacts[self.selected_contact_index]
            c.name = self.name_var.get()
            c.id = self.id_var.get()
            c.type = self.type_var.get()
            c.osc_path = self.osc_path_var.get()
            c.input_type = self.input_type_var.get()
            
            validated_contact = Contact(**c.model_dump())
            self.contacts[self.selected_contact_index] = validated_contact
            
            self._refresh_list()
            messagebox.showinfo("Success", f"Updated {c.name}")
            self._notify_change()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid data: {e}")

    def _toggle_sniff(self):
        if not self.sniffing:
            self.sniffing = True
            self.sniff_btn.config(text="Listening...")
            self.sniffer.add_listener(self._on_osc_message)
        else:
            self.sniffing = False
            self.sniff_btn.config(text="Find/Scan")
            # Don't fully stop the sniffing thread, just ignore or unbind callback
            self.sniffer.remove_listener(self._on_osc_message)

    def _on_osc_message(self, address, args):
        # This runs on a separate thread, need to schedule update on main thread
        self.after(0, lambda: self._update_path_from_osc(address))

    def _update_path_from_osc(self, address):
        if self.sniffing:
            self.osc_path_var.set(address)
            self.sniffing = False
            self.sniff_btn.config(text="Find/Scan")
            self.sniffer.remove_listener(self._on_osc_message)
            messagebox.showinfo("OSC Found", f"Found path: {address}")

    def destroy(self):
        # Cleanup
        if self.sniffer:
            self.sniffer.remove_listener(self._on_osc_message)
        super().destroy()
