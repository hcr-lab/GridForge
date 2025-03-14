from typing import Optional
import pydantic

# file for data structures in map preparation
class FileUploaded(pydantic.BaseModel):
    success: bool 
    filename: Optional[str]  
    location: Optional[str] 
    message: Optional[str] 
    
class LineRequest(pydantic.BaseModel):
    start_point: tuple
    end_point: tuple
    thickness: Optional[int] = None
    
class PointRequest(pydantic.BaseModel):
    x: float
    y: float
    thickness: Optional[int] = None