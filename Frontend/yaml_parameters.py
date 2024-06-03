
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

# use enum to make sure only these three strings are used
class Mode_Enum(str, Enum):
    trinary = "trinary"
    scale = "scale"
    raw = "raw"
    
# refer to https://wiki.ros.org/map_server
class Yaml_parameters(BaseModel):
    image: str = 'uploaded_file.pgm'
    resolution: float = 0.05
    origin_x: float = 0.0
    origin_y: float = 0.0
    origin_yaw: float = 0.0
    negate: bool = False
    occupied_thresh: float = 0.7
    free_thresh: float = 0.2
    mode: Optional[Mode_Enum] = Mode_Enum.trinary # trinary(default), scale or raw



