from pydantic import BaseModel
from enum import Enum

class Preparation_type(str, Enum):
    line = "line"
    point = "point"
    square = "square"
    
class Preparation_parameters(BaseModel):
    thickness: int = 3
    preparation_type: Preparation_type = Preparation_type.point
    # add parameters for pencil, line and quader here
    # ensure only one is enabled
