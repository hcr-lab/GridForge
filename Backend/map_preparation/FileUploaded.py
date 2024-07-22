from typing import Optional
import pydantic

# file for data structures in map preparation
class FileUploaded(pydantic.BaseModel):
    success: bool 
    filename: Optional[str]  
    location: Optional[str] 
    message: Optional[str] 