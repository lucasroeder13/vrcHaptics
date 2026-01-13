from core.loader import Loader
from ui.main_window import MainWindow

class mainApp:
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
        
    def run_all_modules(self):
        print(f"Loaded {len(self.modules)} modules.")
        for name, module in self.modules.items():
            print(f"Executing module: {name}")
            if hasattr(module, 'run'):
                # module.run() # Don't run automatically on start anymore, let UI do it
                pass
            else:
                print(f"Module {name} does not have a run() method.")

if __name__ == "__main__":  
    app = mainApp()
    
    print("Starting Main Window...")
    gui = MainWindow(app.modules)
    gui.mainloop()
    