import tkinter as tk
from tkinter import Toplevel, Label

class TestModule:
    def __init__(self):
        self.name = "Test Module"
        self.devices = [] # List of dicts: {'id': str, 'name': str, 'status': str}

    def run(self):
        print(f"Running {self.name} logic!")
        self.open_window()
        return "Window Opened"

    def scan(self):
        """Mock scanning for devices"""
        self.devices = [
            {'id': 'dev_01', 'name': 'Haptic Vest', 'status': 'Connected'},
            {'id': 'dev_02', 'name': 'Left Glove', 'status': 'Disconnected'},
            {'id': 'dev_03', 'name': 'Right Glove', 'status': 'Battery Low'}
        ]
        return self.devices

    def open_window(self):
        # Create a new top-level window (popup)
        window = Toplevel()
        window.title(f"{self.name} Interface")
        window.geometry("300x200")
        
        lbl = Label(window, text="This is the Test Module Window!", pady=20)
        lbl.pack()
        
        btn = tk.Button(window, text="Close", command=window.destroy)
        btn.pack(pady=10)

    def handle_event(self, binding, current_intensity):
        print(f"TestModule: Device {binding.device_name} ({binding.device_id}) -> {binding.reaction_type} at {current_intensity:.2f} (Duration: {binding.duration})")
