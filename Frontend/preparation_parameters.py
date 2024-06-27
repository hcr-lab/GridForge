from pydantic import BaseModel
from enum import Enum

class Preparation_type(str, Enum):
    line = "line"
    point = "point"
    square = "square"
    fill = "fill"
    cut = "cut"
    
class Preparation_parameters(BaseModel):
    thickness: int = 3
    preparation_type: Preparation_type = Preparation_type.point
    length: float = 1
    pixels: float = 1
    # only between 0 and 255! 
    pgm_threshold: int = 155
