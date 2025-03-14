from fastapi import FastAPI
from fastapi.responses import JSONResponse
from Backend.quality_check.service_quality_check import filledArea, blackArea
from Backend.global_variables import app

@app.get("/filledAreaPercentage")
async def computeFilledAreaPercentage():
    """Computes the percentage of the red pixels which represent the drivable of the map.

    Returns:
        JSONResponse: Response with the percentage, the number of pixels of the image and the number of red pixels
    """
    filled_pixels, raw_image_size = filledArea()
    
    # Calculate the percentage of the specified color
    color_percentage = filled_pixels / raw_image_size

    return JSONResponse(content={"filled_area_ratio": color_percentage, "raw_image_size": raw_image_size, "filled_pixels": filled_pixels})
        
# use pgm image to compute the percentage of obstacles
@app.get("/blackPixelPercentage")
async def computePercentageWalls() -> JSONResponse:
    """Computes the percentage of the black pixels which represent the walls of the map.

    Returns:
        JSONResponse: Response with the percentage, the number of pixels of the pgm image and the number of black pixels
    """
    black_pixels, pgm_image_size = blackArea()
    
    # Calculate the percentage of black pixels
    black_pixel_percentage = black_pixels / pgm_image_size
    
    return JSONResponse(content={"wall_ratio": black_pixel_percentage, "pgm_image_size": pgm_image_size, "black_pixels": black_pixels})
        