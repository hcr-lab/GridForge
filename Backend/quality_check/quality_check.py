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

raw_image_size = None
pgm_image_size = None
filled_pixels = None
black_pixels = None

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
    global filled, raw_image_size, filled_pixels
    if filled == None:
        getImageNamesInDir()

    # if filled is still None after calling getImagesInDir,
    # then fill function was never called and UI should respond accordingly without raising an exception
    if filled == None:
        return JSONResponse(status_code=400, content = {"filled_area_ratio": 0.0})
        # raise HTTPException(status_code=404, detail="Image not found")
    else:
        # Load the image
        image = cv2.imread(filled)

        if image is None:
            raise HTTPException(status_code=404, detail="Failed to load image")
        
        # Convert the image to the HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the color range for red in HSV
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        # Create masks for the red color range
        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)

        # Combine the masks
        mask = cv2.bitwise_or(mask1, mask2)

        # write mask for debugging purposes
        # cv2.imwrite(os.path.join(UPLOAD_DIR, 'mask.jpg'), mask)
        
        # Calculate the total number of pixels
        raw_image_size = image.shape[0] * image.shape[1]

        # Calculate the number of pixels within the specified color range
        filled_pixels = cv2.countNonZero(mask)

        # Calculate the percentage of the specified color
        color_percentage = filled_pixels / raw_image_size

        return JSONResponse(content={"filled_area_ratio": color_percentage, "raw_image_size": raw_image_size, "filled_pixels": filled_pixels})
        
# use pgm image to compute the percentage of obstacles
async def computePercentageWalls():
    global pgm, pgm_image_size, black_pixels
    if pgm == None:
        getImageNamesInDir()

    # if pgm is still None after calling getImagesInDir,
    # then the createPGM function was never called and UI should respond accordingly without raising an exception
    if pgm == None:
        return JSONResponse(status_code=400, content = {"filled_area_ratio": 0.0})
        # raise HTTPException(status_code=404, detail="Image not found")
    else:
        # Load the image
        image = cv2.imread(pgm, cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise HTTPException(status_code=404, detail="Failed to load image")
        
    # Define the threshold under which a pixel is detected as fully black
    threshold = 50

    # Apply the threshold to classify pixels as black or not
    _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # cv2.imwrite(os.path.join(UPLOAD_DIR, 'mask.pgm'), binary_image)
    
    # Ensure the binary image is single-channel
    if len(binary_image.shape) != 2:
        raise HTTPException(status_code=400, detail="Binary image is not a single-channel image")

    # Calculate the total number of pixels
    pgm_image_size = image.size

    # Calculate the number of black pixels
    black_pixels = cv2.countNonZero(binary_image)

    # Calculate the percentage of black pixels
    black_pixel_percentage = black_pixels / pgm_image_size
    
    return JSONResponse(content={"wall_ratio": black_pixel_percentage, "pgm_image_size": pgm_image_size, "black_pixels": black_pixels})
        