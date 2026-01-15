from pydantic import BaseModel
from typing import Optional, Literal

class Binding(BaseModel):
    contact_id: str
    contact_name: str
    module_name: str
    device_id: str
    device_name: str
    reaction_type: str = "vibrate" # vibrate, shock, etc.
    intensity: float = 1.0
    duration: float = 0.5
    
    # Advanced Mapping for Float/Int Inputs
    use_mapping: bool = False
    input_min: float = 0.0
    input_max: float = 1.0
    output_min: float = 0.0
    output_max: float = 1.0
    curve_type: Literal["linear", "exponential", "logarithmic", "threshold"] = "linear"
    is_continuous: bool = False

