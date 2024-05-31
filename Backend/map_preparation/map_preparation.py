import os
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import logging
import cv2

from Backend.map_preparation.data import FileUploaded

app = FastAPI()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploaded_files"
FILENAME = "uploaded_file.jpg"
os.makedirs(UPLOAD_DIR, exist_ok=True)
IMAGE_PATH = os.path.join(UPLOAD_DIR, FILENAME)

@app.get('/text')
def show_text(text: str):
    logging.info('method reached')
    return JSONResponse(content={'header' : text, 
                                 'this is the content': 'content displayed'})

# TODO: provide function to save image as pgm before it is processed 
@app.post('/save')
async def save_file(b: bytes):
    # file is not correctly overwritten

    location = os.path.join(UPLOAD_DIR, FILENAME)
    # Iterate over the files and directories in the specified directory
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the directory and all its contents
        except Exception as e:
            return JSONResponse(content=FileUploaded(success=False,
                                   message=f'Failed to delete {file_path}. Reason: {e}'))
            
    with open(IMAGE_PATH, "wb") as buffer:
        buffer.write(b)

    response_body = FileUploaded(filename=FILENAME,
                           location=location,
                           success=True,
                           message=f'Upload of {FILENAME} in {location} successful')
    return JSONResponse(content=response_body.model_dump()) 
    

@app.get("/image")
async def get_image():
    if os.path.exists(IMAGE_PATH):
        return FileResponse(IMAGE_PATH)
    else:
        raise HTTPException(status_code=404, detail="Image not found")
    
@app.post('/pencil_click')
async def addPoint(x: float, y: float):
    x = int(x)
    y = int(y)
    if x is None or y is None:
        raise HTTPException(status_code=400, detail="Coordinates not provided")

    if not os.path.exists(IMAGE_PATH):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(IMAGE_PATH)

    # Modify the image based on click (e.g., draw a circle at the clicked position)
    cv2.circle(image, (x, y), 3, (0, 0, 0), -1)  # Red circle

    # Save the modified image
    cv2.imwrite(IMAGE_PATH, image)

    return {"message": "Image modified successfully", "x": x, "y": y}

@app.post('/eraser_click')
async def erasePoint(x: float, y: float ):
    x = int(x)
    y = int(y)
    if x is None or y is None:
        raise HTTPException(status_code=400, detail="Coordinates not provided")

    if not os.path.exists(IMAGE_PATH):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(IMAGE_PATH)

    # Modify the image based on click (e.g., draw a circle at the clicked position)
    cv2.circle(image, (x, y), 3, (255, 255, 255), -1)  # Red circle

    # Save the modified image
    cv2.imwrite(IMAGE_PATH, image)

    return {"message": "Image modified successfully", "x": x, "y": y}