from typing import List, Dict, Any, Optional
import math
from schemas.bindings import Binding
from schemas.contacts import Contact

class OSCHandler:
    def __init__(self, loaded_modules: Dict[str, Any], contacts: List[Contact], bindings: List[Binding]):
        self.loaded_modules = loaded_modules
        self.contacts = contacts
        self.bindings = bindings

    def update_config(self, contacts: List[Contact], bindings: List[Binding]):
        self.contacts = contacts
        self.bindings = bindings

    def update_modules(self, loaded_modules: Dict[str, Any]):
        self.loaded_modules = loaded_modules

    def map_message(self, address: str, args: List[Any]):
        """
        Called by the OSC Sniffer when a message is received.
        address: The OSC address (e.g. /avatar/parameters/MyContact)
        args: List of arguments (values)
        """
        if not args:
            return
        print(f"Received OSC message: {address} with args {args}")
        # Assuming single value for most VRC parameters
        raw_value = args[0]
        
        matched_contact = self._find_contact(address)
        if not matched_contact:
            # Optional: Debug print for unmapped addresses
            # print(f"Unmapped OSC address: {address}")
            return

        # Find bindings associated with this contact
        active_bindings = [b for b in self.bindings if b.contact_id == matched_contact.id]
        
        for binding in active_bindings:
            self._trigger_binding(binding, raw_value)

    def _find_contact(self, address: str) -> Optional[Contact]:
        for contact in self.contacts:
            # Check configured OSC path (exact match)
            if contact.osc_path and contact.osc_path == address:
                return contact
            
            # Check common VRChat parameter patterns
            # e.g. /avatar/parameters/ContactName matches id="ContactName"
            if address.endswith(f"/{contact.id}"):
                return contact
                
        return None

    def _trigger_binding(self, binding: Binding, raw_value: Any):
        module = self.loaded_modules.get(binding.module_name)
        if not module:
            print(f"Module '{binding.module_name}' not found for binding.")
            return

        # Calculate the effective intensity or value
        payload_value = self._calculate_payload(binding, raw_value)
        
        # Function name corresponds to reaction_type (e.g. vibrate, shock)
        func_name = binding.reaction_type
        
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            try:
                # We expect the module method signature to accept (binding, intensity)
                func(binding, payload_value)
            except Exception as e:
                print(f"Error executing '{func_name}' in module '{binding.module_name}': {e}")
        else:
             # Fallback if specific reaction function is missing but a generic handler exists
            if hasattr(module, "handle_event"):
                try:
                    module.handle_event(binding, payload_value)
                except Exception as e:
                    print(f"Error executing 'handle_event' in module '{binding.module_name}': {e}")
            else:
                print(f"Module '{binding.module_name}' does not implement '{func_name}'")

    def _calculate_payload(self, binding: Binding, raw_value: Any) -> float:
        # Handle Boolean
        if isinstance(raw_value, bool):
            return binding.intensity if raw_value else 0.0
            
        try:
            val = float(raw_value)
        except (ValueError, TypeError):
            return 0.0

        if not binding.use_mapping:
            # Default behavior: input * intensity
            return val * binding.intensity

        # Advanced Mapping
        in_min = binding.input_min
        in_max = binding.input_max
        out_min = binding.output_min
        out_max = binding.output_max
        
        # Clamp input
        if val < in_min: val = in_min
        elif val > in_max: val = in_max
        
        # Normalize (0.0 to 1.0)
        rng = in_max - in_min
        if rng == 0:
            norm = 0.0
        else:
            norm = (val - in_min) / rng
            
        # Curve
        if binding.curve_type == "exponential":
            norm = norm * norm
        elif binding.curve_type == "logarithmic":
            norm = math.pow(norm, 0.5)
        elif binding.curve_type == "threshold":
            norm = 1.0 if norm >= 0.5 else 0.0
            
        # Scale to Output
        result = out_min + (norm * (out_max - out_min))
        
        return result
