import cv2
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import FastAPI
import os

from Backend.map_preparation.data import FileUploaded
import logging

app = FastAPI()

UPLOAD_DIR = "uploaded_files"
file_name = "uploaded_file.yaml"
yaml_file_path = os.path.join(UPLOAD_DIR, file_name)
data = {}

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

@app.get("/download_files", response_class=JSONResponse)
async def download_files(yaml_string: str):
    global yaml_file_path
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # logging works this way
    processed_string = process_yaml_string(yaml_string)
    logger.info(f"processed yaml string is {processed_string}")    
    logger.info(f"file path is {yaml_file_path}")    

    # create the yaml file in the uploaded_files-directory
    with open(yaml_file_path, "w") as yaml_file:
        yaml_file.write(processed_string)
    
    convert_to_pgm()
    
    response_body = FileUploaded(filename=file_name,
                           location=yaml_file_path,
                           success=True,
                           message=f'Upload of {file_name} in {yaml_file_path} successful')
    return JSONResponse(content=response_body.model_dump()) 

# since the Yaml_parameter class is not in the correct format, 
# it needs to be processed into the correct format
def process_yaml_string(yaml_string: str):
    global file_name
    global yaml_file_path
    global data
    
    lines = yaml_string.split('\n')
    
    # Parse the lines into the dictionary
    for line in lines:
        if line.strip():  # Skip any empty lines
            key, value = line.split(': ', 1)
            data[key] = value
    
    # change image name to yaml file 
    base_name, _ = os.path.splitext(data.get('image'))
    yaml_file = base_name + '.yaml'
    yaml_file_path = os.path.join(UPLOAD_DIR, yaml_file)
    logger.info(f'name of file set to {file_name}')
    
    # Modify the values as needed
    if 'negate' in data:
        data['negate'] = '0' if data['negate'].lower() == 'false' else '1'
    
    # Create the origin list
    origin = [data.pop('origin_x', '0.0'), data.pop('origin_y', '0.0'), data.pop('origin_yaw', '0.0')]
    data['origin'] = f"[{', '.join(origin)}]"
    
    # Construct the output string
    output_lines = []
    for key in ['free_thresh', 'image', 'mode', 'negate', 'occupied_thresh', 'origin', 'resolution']:
        if key in data:
            output_lines.append(f"{key}: {data[key]}")
    
    return '\n'.join(output_lines)

def convert_to_pgm():
    # get the name of the uploaded image from the data of the processed yaml file
    # and the basename for adding the pgm extension
    input_file = data.get('image')
    base_name, _ = os.path.splitext(data.get('image'))
    output_file = base_name + '.pgm'

    negate = int(data.get('negate'))
    if negate == 0:
        img = cv2.imread(os.path.join(UPLOAD_DIR, input_file), cv2.IMREAD_GRAYSCALE) 
        logger.info(f'Image read from imread: {img is not None}')
        
        if img is None:
            logger.error(f"Failed to load image {input_file}")
            return
        
        # Save the image in PGM format
        output_path = os.path.join(UPLOAD_DIR, output_file)
        logger.info(f'Attempting to write image to {output_path}')
        success = cv2.imwrite(output_path, img)
        
        if success:
            logger.info(f'Successfully wrote image to {output_path}')
        else:
            logger.error(f'Failed to write image to {output_path}')
    else: 
        logger.info('negate is True')
        pass