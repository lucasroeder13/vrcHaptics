import os
import importlib.util
import inspect

class Loader:
    def __init__(self, modules_dir="modules"):
        # Set absolute path relative to the project root (parent of this file's folder)
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.modules_dir = os.path.join(project_root, modules_dir)
        self.loaded_modules = {}

    def load_modules(self):
        """
        Loads all .py modules from the modules directory.
        Returns a dictionary {module_name: module_instance_or_module}.
        It attempts to instantiate a class if found (heuristic: named {filename}Module or just the first class found).
        """
        self.loaded_modules = {}
        
        if not os.path.exists(self.modules_dir):
            print(f"Warning: Directory '{self.modules_dir}' does not exist.")
            return {}

        for filename in os.listdir(self.modules_dir):
            file_path = os.path.join(self.modules_dir, filename)
            module_name = filename
            spec = None

            # Case A: Directory Module (e.g., modules/TestModule/__init__.py)
            if os.path.isdir(file_path):
                # Check for __init__.py
                init_path = os.path.join(file_path, "__init__.py")
                if os.path.exists(init_path):
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, init_path)
                    except Exception:
                        pass
            
            # Case B: Single File Module (e.g. modules/test.py)
            elif filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                except Exception:
                    pass

            # Load if spec found
            if spec and spec.loader:
                try:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Try to find a primary class to instantiate
                    # Heuristic: Match 'test' -> 'testModule' or 'TestModule' or 'Test'
                    instance = self._instantiate_module_class(module, module_name)
                    
                    if instance:
                        self.loaded_modules[module_name] = instance
                    else:
                        # Fallback: just store the raw module
                        self.loaded_modules[module_name] = module
                        
                except Exception as e:
                    print(f"Failed to load module {module_name}: {e}")

        return self.loaded_modules

    def _instantiate_module_class(self, module, module_name):
        """Helper to find and instantiate the main class in the module."""
        # 1. Look for class named {ModuleName}Module (case insensitive)
        target_names = [
            f"{module_name}Module".lower(), 
            module_name.lower(),
            "module" # Generic 'Module' class
        ]
        
        candidates = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                candidates.append((name, obj))
        
        # Strategy A: Exact Name Match (case-insensitive)
        for name, obj in candidates:
            if name.lower() in target_names:
                try:
                    return obj()
                except Exception as e:
                    print(f"Error instantiating {name} in {module_name}: {e}")
                    return None

        # Strategy B: If only one class exists, assume it's the main one
        if len(candidates) == 1:
            try:
                return candidates[0][1]()
            except Exception as e:
                print(f"Error instantiating {candidates[0][0]} in {module_name}: {e}")
                return None
                
        return None