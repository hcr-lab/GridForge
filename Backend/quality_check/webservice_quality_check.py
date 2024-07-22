from fastapi.responses import JSONResponse
from Backend.quality_check.service_quality_check import filledArea, blackArea

async def computeFilledAreaPercentage():
    filled_pixels, raw_image_size = filledArea()
    
    # Calculate the percentage of the specified color
    color_percentage = filled_pixels / raw_image_size

    return JSONResponse(content={"filled_area_ratio": color_percentage, "raw_image_size": raw_image_size, "filled_pixels": filled_pixels})
        
# use pgm image to compute the percentage of obstacles
async def computePercentageWalls():

    black_pixels, pgm_image_size = blackArea()
    
    # Calculate the percentage of black pixels
    black_pixel_percentage = black_pixels / pgm_image_size
    
    return JSONResponse(content={"wall_ratio": black_pixel_percentage, "pgm_image_size": pgm_image_size, "black_pixels": black_pixels})
        