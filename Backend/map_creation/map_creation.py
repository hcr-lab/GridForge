from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import FastAPI
import os

from Backend.map_preparation.data import FileUploaded
import logging

app = FastAPI()

UPLOAD_DIR = "uploaded_files"
FILENAME = "uploaded_file.yaml"
YAML_FILE_PATH = os.path.join(UPLOAD_DIR, FILENAME)

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

@app.get("/download_yaml", response_class=JSONResponse)
async def download_yaml(yaml_string: str):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # logging works this way
    processed_string = process_yaml_string(yaml_string)
    logger.info(f"processed yaml string is {processed_string}")    

    with open(YAML_FILE_PATH, "w") as yaml_file:
        yaml_file.write(processed_string)
    
    response_body = FileUploaded(filename=FILENAME,
                           location=YAML_FILE_PATH,
                           success=True,
                           message=f'Upload of {FILENAME} in {YAML_FILE_PATH} successful')
    return JSONResponse(content=response_body.model_dump()) 

def process_yaml_string(yaml_string: str):
    lines = yaml_string.split('\n')
    
    # Create a dictionary to store the parsed values
    data = {}
    
    # Parse the lines into the dictionary
    for line in lines:
        if line.strip():  # Skip any empty lines
            key, value = line.split(': ', 1)
            data[key] = value
    
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
