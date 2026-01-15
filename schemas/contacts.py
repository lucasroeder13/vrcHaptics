from pydantic import BaseModel
from typing import Literal, Optional


class Contact(BaseModel):
    name: str
    id: str
    type: int
    osc_path: Optional[str] = None
    input_type: Literal["bool", "int", "float"] = "float"
    cooldown: float = 0.0


class EventContact(BaseModel):
    name: str
    id: str
    contactId: str
    type: int # 0 = stop, 1 = vibrate, 2 = sound, 3 = shock
    intensity: float
    duration: float
    