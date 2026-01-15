import json
import os
from typing import List, Dict, Any
from schemas.contacts import Contact
from schemas.bindings import Binding

CONFIG_FILE = "user_config.json"

class ConfigManager:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FILE):
            return {"contacts": [], "bindings": []}
            
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                
            # validations / conversions could happen here if needed, 
            # but currently we just return dicts and let pydantic parse them later
            return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"contacts": [], "bindings": []}

    @staticmethod
    def save_config(contacts: List[Contact] = None, bindings: List[Binding] = None, app_settings: Dict[str, Any] = None):
        # Load existing manually to preserve other keys (like "modules")
        current_data = {}
        if os.path.exists(CONFIG_FILE):
             try:
                with open(CONFIG_FILE, 'r') as f:
                    current_data = json.load(f)
             except:
                 pass

        if contacts is not None:
            current_data["contacts"] = [c.model_dump() for c in contacts]
        
        if bindings is not None:
            current_data["bindings"] = [b.model_dump() for b in bindings]
        
        if app_settings is not None:
            current_data["app_settings"] = app_settings
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(current_data, f, indent=4)
            print("Config saved.")
        except Exception as e:
            print(f"Error saving config: {e}")

    @staticmethod
    def get_app_settings() -> Dict[str, Any]:
        data = ConfigManager.load_config()
        return data.get("app_settings", {"osc_port": 9001})

    @staticmethod
    def export_config(filepath: str, contacts: List[Contact], bindings: List[Binding]):
        if not filepath:
            return
        
        data = {
            "contacts": [c.model_dump() for c in contacts],
            "bindings": [b.model_dump() for b in bindings],
            # We could include modules config here too if requested, but for now just contacts/bindings
        }
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Config exported to {filepath}")
        except Exception as e:
            print(f"Error exporting config: {e}")

    @staticmethod
    def import_config(filepath: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {}
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error importing config: {e}")
            return {}

    @staticmethod
    def get_module_config(module_name: str) -> Dict[str, Any]:
        data = ConfigManager.load_config()
        return data.get("modules", {}).get(module_name, {})

    @staticmethod
    def set_module_config(module_name: str, config: Dict[str, Any]):
        data = ConfigManager.load_config()
        if "modules" not in data:
            data["modules"] = {}
        
        data["modules"][module_name] = config
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Module config for {module_name} saved.")
        except Exception as e:
            print(f"Error saving module config: {e}")
