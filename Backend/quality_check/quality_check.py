import os
import cv2
from fastapi import HTTPException


UPLOAD_DIR = "uploaded_files"

# paths to the files in the upload dir
PGM: str
PIC: str
YAML: str
FILLED: str

# get image names and extensions and write them to constants
def getImageNamesInDir():
    pass


async def computeFilledAreaPercentage():
    if not os.path.exists(FILLED):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(FILLED)


# use pgm image to compute the percentage of obstacles
async def computePercentageWalls():
    if not os.path.exists(PGM):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(PGM)
    pass