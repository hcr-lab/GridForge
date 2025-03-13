import os
import shutil
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import numpy as np

from Backend.map_preparation.DataModels import FileUploaded, LineRequest, PointRequest
from Backend.map_preparation.service_map_preparation import cut_image_path, image_path, logger, UPLOAD_DIR, FILENAME
from Backend.global_variables import app

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

@app.post('/save')
async def save_file(file: UploadFile = File(...)) -> JSONResponse:
    """sets the image path and saves the image to uploaded_files

    Args:
        UploadFile: The file to be uploaded

    Returns:
        JSONResponse: FileUploaded with success message and bool
    """
    global image_path
    try:
        # read the bytes of the file 
        b = await file.read()
          
        image_path = os.path.join(UPLOAD_DIR, file.filename)
        logger.info(f'image path set to {image_path}')

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
        
        with open(image_path, "wb") as buffer:
            buffer.write(b)
        
        response_body = FileUploaded(filename=FILENAME,
                            location=image_path,
                            success=True,
                            message=f'Upload of {FILENAME} in {image_path} successful')
        return JSONResponse(content=response_body.model_dump()) 
    except:
        return JSONResponse(content=FileUploaded(success=False,
                            message=f'Failed to save {FILENAME} in {image_path}'))

@app.post('/pencil_point')
async def addPoint(pointRequest: PointRequest) -> JSONResponse:
    """modifies the image by drawing a circle at the specified point.
    Uses the cv2.circle algorithm

    Args:
        pointRequest (PointRequest): x- and y-coordinate of the point and thickness

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    x = int(pointRequest.x)
    y = int(pointRequest.y)
    thickness = pointRequest.thickness if pointRequest.thickness is not None else 3  # Default thickness
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Modify the image based on click (e.g., draw a circle at the clicked position)
    cv2.circle(image, (x, y), thickness, BLACK, -1)  # black circle
        
    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/pencil_line')
async def addLine(lineRequest: LineRequest) -> JSONResponse:
    """Modifying the image by drawing a line between the two points. 
    Uses the cv2.line function

    Args:
        lineRequest (LineRequest): start- and end point of the line and thickness

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    start_point = lineRequest.start_point
    end_point = lineRequest.end_point
    thickness = lineRequest.thickness if lineRequest.thickness is not None else 3  # Default thickness
    
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.line(image, start_point, end_point, BLACK, thickness=thickness)
    
    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/draw_square')
async def drawSquare(lineRequest: LineRequest) -> JSONResponse:
    """Modifies the image by drawing a square between the two points.
    Uses the cv2.rectangle function.

    Args:
        lineRequest (LineRequest): start- and end point of the line 

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    start_point = lineRequest.start_point
    end_point = lineRequest.end_point
    
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.rectangle(image, start_point, end_point, BLACK, -1)

    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/eraser_click')
async def erasePoint(pointRequest: PointRequest) -> JSONResponse:
    """modifies the image by erasing a circle at the specified point.
    Uses the cv2.circle algorithm. Draws a white circle essentially.

    Args:
        pointRequest (PointRequest): x- and y-coordinate of the point and thickness
    
    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    x = int(pointRequest.x)
    y = int(pointRequest.y)
    thickness = pointRequest.thickness if pointRequest.thickness is not None else 3  # Default thickness

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Modify the image based on click (e.g., draw a circle at the clicked position)
    cv2.circle(image, (x, y), thickness, WHITE, -1)  # Red circle

    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully", "x": x, "y": y})

@app.post('/eraser_line')
async def eraseLine(lineRequest: LineRequest) -> JSONResponse:
    """Modifying the image by erasing a line between the two points. 
    Uses the cv2.line function. Draws a while line essentially.

    Args:
        lineRequest (LineRequest): start- and end point of the line and thickness

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    start_point = lineRequest.start_point
    end_point = lineRequest.end_point
    thickness = lineRequest.thickness if lineRequest.thickness is not None else 3  # Default thickness
 
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.line(image, start_point, end_point, WHITE, thickness=thickness)
    
    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/eraser_square')
async def eraseSquare(lineRequest: LineRequest) -> JSONResponse:
    """Modifies the image by erasing a square between the two points.
    Uses the cv2.rectangle function. Draws a white square essentially. 

    Args:
        lineRequest (LineRequest): start- and end point of the line  

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    start_point = lineRequest.start_point
    end_point = lineRequest.end_point
    
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.rectangle(image, start_point, end_point, WHITE, -1)

    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/cut_out')
async def cutOut(lineRequest: LineRequest) -> JSONResponse:
    """Cuts the image defined by start- and end point

    Args:
        lineRequest (LineRequest): start- and end point of the line  

    Raises:
        HTTPException: 404 if image is not found
        HTTPEXception: 400 if coordinates are invalid

    Returns:
        JSONResponse: message if modified successfully
    """
    start_point = lineRequest.start_point
    end_point = lineRequest.end_point
    
    global cut_image_path
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)


    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))

    # Calculate the center and size of the rectangle
    center_x = (start_point[0] + end_point[0]) / 2
    center_y = (start_point[1] + end_point[1]) / 2
    width = abs(end_point[0] - start_point[0])
    height = abs(end_point[1] - start_point[1])

    # Ensure the coordinates are within the image bounds
    height_img, width_img = image.shape[:2]
    center_x = max(0, min(width_img, center_x))
    center_y = max(0, min(height_img, center_y))
    width = max(0, min(width_img, width))
    height = max(0, min(height_img, height))

    logger.info(f'center_x = {center_x}')
    logger.info(f'center_y = {center_y}')
    logger.info(f'width = {width}')
    logger.info(f'height = {height}')
    
    if width == 0 or height == 0:
        raise HTTPException(status_code=400, detail="Invalid coordinates: width or height cannot be zero.")

    # Extract the rectangle region
    cut_image = cv2.getRectSubPix(image, (int(width), int(height)), (center_x, center_y))

    # Save the modified image
    cut_image_path = os.path.join(UPLOAD_DIR, 'cut_image.jpg')
    cv2.imwrite(cut_image_path, cut_image)
        
    return JSONResponse(content={"message": "Image modified successfully"})

        
@app.post('/fill_area')
async def fillArea(pointRequest: PointRequest) -> JSONResponse:
    """Creates an image where the area defined by the point is filled with red color.
    Uses the floodfill algorithm of cv2

    Args:
        pointRequest (PointRequest): x- and y-coordinate of the point

    Raises:
        HTTPException: 404 if image is not found or not properly loaded

    Returns:
        JSONResponse: success message if successful with image path  
    """
    
    x = int(pointRequest.x)
    y = int(pointRequest.y)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise HTTPException(status_code=404, detail="Failed to load image")

    # Flood fill
    # gets the image size in height and width. 
    # Channels of the picture are not necessary, hence the slicing
    h, w = image.shape[:2]
    # flood fill requires a mask which is two pixels bigger in h and w dimension
    mask = np.zeros((h+2, w+2), np.uint8)
    flood_fill_color = (0, 0, 255)  # Fill color (red)
    seed_point = (x, y)
    lo_diff = (10, 10, 10)  # Lower brightness/color difference
    up_diff = (10, 10, 10)  # Upper brightness/color difference
    
    cv2.floodFill(image, mask, seed_point, flood_fill_color, lo_diff, up_diff)

    # Save the modified image
    _, extension = os.path.splitext(image_path)
    filled_image_path = os.path.join(UPLOAD_DIR, 'filled_image' + extension)
    cv2.imwrite(filled_image_path, image)

    return JSONResponse(content={"message": "Image modified successfully", "image_path": filled_image_path})

@app.post('/copyCutImage')
def copyCutImage() -> None:
    """If it exists, writes the cutted image to the image path to overwrite the original image with the cutted one
    """
    if os.path.exists(cut_image_path):
        image = cv2.imread(cut_image_path)
        cv2.imwrite(image_path, image)