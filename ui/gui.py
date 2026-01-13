import tkinter as tk
from tkinter import ttk, messagebox
from schemas.contacts import Contact
import json

class ContactManagerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact OSC Manager")
        self.geometry("600x400")
        
        self.contacts = [] # List of Contact objects
        self.selected_contact_index = None

        self._create_widgets()
        self._load_dummy_data()

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
        self.osc_path_var = tk.StringVar()
        self.osc_path_entry = ttk.Entry(right_frame, textvariable=self.osc_path_var)
        self.osc_path_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # Input Type (Bool, Int, Float)
        ttk.Label(right_frame, text="Input Type:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.input_type_var = tk.StringVar(value="float")
        type_options = ["bool", "int", "float"]
        self.input_type_menu = ttk.OptionMenu(right_frame, self.input_type_var, "float", *type_options)
        self.input_type_menu.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # Save Button
        save_btn = ttk.Button(right_frame, text="Save Changes to Contact", command=self._save_changes)
        save_btn.grid(row=row, column=0, columnspan=2, pady=10)
        
        right_frame.columnconfigure(1, weight=1)
        main_paned.add(right_frame)

    def _load_dummy_data(self):
        # Just for testing
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
        # Add a placeholder
        new_c = Contact(name="New Contact", id="new_id", type=0, input_type="float")
        self.contacts.append(new_c)
        self._refresh_list()
        self.contact_listbox.selection_clear(0, tk.END)
        self.contact_listbox.selection_set(tk.END)
        self._on_contact_select(None)

    def _save_changes(self):
        if self.selected_contact_index is None:
            messagebox.showwarning("Warning", "No contact selected")
            return
            
        try:
            # Update the contact object from vars
            c = self.contacts[self.selected_contact_index]
            c.name = self.name_var.get()
            c.id = self.id_var.get()
            c.type = self.type_var.get()
            c.osc_path = self.osc_path_var.get()
            c.input_type = self.input_type_var.get()
            
            # Re-validate with Pydantic if needed (assigning fields directly validates if configured, 
            # but usually constructing new one is safer to trigger validation)
            validated_contact = Contact(**c.model_dump())
            self.contacts[self.selected_contact_index] = validated_contact
            
            self._refresh_list()
            messagebox.showinfo("Success", f"Updated {c.name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid data: {e}")

if __name__ == "__main__":
    app = ContactManagerUI()
    app.mainloop()
