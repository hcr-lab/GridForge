import logging
import os
import cv2
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import numpy as np


UPLOAD_DIR = "uploaded_files"

# paths to the files in the upload dir
pgm = None
pic = None
yaml = None
filled = None

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

# get image names and extensions and write them to constants
def getImageNamesInDir():
    global filled, yaml, pic, pgm
    logger.info('method reached')
    try:
        # get all files and directories in UPLOAD DIR
        files_and_dirs = os.listdir(UPLOAD_DIR)
        
        extensions = {'.pgm', '.yaml', '.jpg', '.png'}
        
        # Filter out directories and keep only files with specific extensions
        files = [
            os.path.join(UPLOAD_DIR, f) 
            for f in files_and_dirs 
            if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and os.path.splitext(f)[1].lower() in extensions
        ]
        logger.info(f'files in directory: \n {files}')
        # adjust paths wrt extensions
        for file in files:
            name, extension = os.path.splitext(file)
            # logger.info(f'name is {name}')
            # logger.info(f'extension is {extension}')
            
            filled_name = os.path.join(UPLOAD_DIR, 'filled_image')
            logger.info(f'filled name is {filled_name}')
            if name == filled_name:
                filled = file
                logger.info(f'File used for filled Image quality metrics: {filled}')
            elif (extension.lower() == '.jpg' or extension.lower() == '.png') and name.lower() != filled_name:
                pic = file
                logger.info(f'File used for processed Image quality metrics: {pic}')
            elif extension.lower() == '.pgm':
                pgm = file
                logger.info(f'File used for map pgm image quality metrics: {pgm}')
            elif extension.lower() == '.yaml':
                yaml = file
                logger.info(f'File used for yaml quality metrics: {yaml}')
            else:
                logger.warning('Wrong file in directory')            
        
    except FileNotFoundError:
        return f"Directory {UPLOAD_DIR} not found."
    except PermissionError:
        return f"Permission denied for accessing {UPLOAD_DIR}."
    except Exception as e:
        return f"An error occurred: {e}"    


async def computeFilledAreaPercentage():
    global filled
    if filled == None:
        getImageNamesInDir()

    if not os.path.exists(filled):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(filled)

    if image is None:
        raise HTTPException(status_code=404, detail="Failed to load image")
    
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the color range for the mask
    # lower_bound = np.array(lower_bound, dtype="uint8")
    # upper_bound = np.array(upper_bound, dtype="uint8")

    color = (0, 0, 255)
    
    # Create a mask for the specified color range
    mask = cv2.inRange(hsv_image, color, color)

    # Calculate the total number of pixels
    total_pixels = image.shape[0] * image.shape[1]

    # Calculate the number of pixels within the specified color range
    color_pixels = cv2.countNonZero(mask)
    logger.info(f'total pixels is {total_pixels}')
    logger.info(f'color pixels: {color_pixels}')
    # Calculate the percentage of the specified color
    color_percentage = color_pixels / total_pixels

    # convert to json later
    # return JSONResponse(content={"color_percentage": color_percentage})

    return color_percentage
    
# use pgm image to compute the percentage of obstacles
async def computePercentageWalls():
    if not os.path.exists(pgm):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(pgm)
    pass