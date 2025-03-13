from fastapi.responses import JSONResponse
import os

from Backend.map_preparation.FileUploaded import FileUploaded
from Backend.map_creation.service_map_creation import process_yaml_string, convertWithoutNegate
from Backend.map_creation.service_map_creation import logger
import Backend.global_variables as globals
from Backend.global_variables import app

@app.get("/download_files", response_class=JSONResponse)
async def write_yaml(yaml_string: str) -> JSONResponse:
    """Pushes the content of the yaml string to a file and writes it to the directory.

    Args:
        yaml_string (str): The string representing the content of the yaml file. Directly created by the frontend

    Returns:
        JSONResponse: FileUploaded as body with name, path, success bool and message
    """
    # global yaml_file_path
    
    os.makedirs(globals.UPLOAD_DIR, exist_ok=True)
    # logging works this way
    processed_string = process_yaml_string(yaml_string)
    logger.info(f"processed yaml string is {processed_string}")    
    logger.info(f"file path is {globals.yaml_file_path}")    

    # create the yaml file in the uploaded_files-directory
    with open(globals.yaml_file_path, "w") as yaml_file:
        yaml_file.write(processed_string)
    
    response_body = FileUploaded(filename=globals.file_name,
                           location=globals.yaml_file_path,
                           success=True,
                           message=f'Upload of {globals.file_name} in {globals.yaml_file_path} successful')
    return JSONResponse(content=response_body.model_dump()) 

@app.post("/convertToPgm")
async def convert_to_pgm(thresh: int, yaml_string: str) -> JSONResponse:
    """Converts the uploaded image to a pgm file based on the Negate-Flag in the data

    Args:
        thresh (int): threshold for the creation of the pgm file
        yaml_string (str): The string representing the content of the yaml file. Directly created by the frontend

    Returns:
        JSONResponse: message if successful
    """
    # get the name of the uploaded image from the data of the processed yaml file
    # and the basename for adding the pgm extension
    process_yaml_string(yaml_string)

    logger.info(f'threshold uses: {thresh}')
    negate = int(globals.data.get('negate'))
    if negate == 0:
        if convertWithoutNegate(thresh):
            return JSONResponse(content={"message": "PGM created successful"})
        else:
            return JSONResponse(content={"message": "Error while creation"})
    else: 
        logger.info('negate is True')
        # invert image if necessary, not yet implemented. Maybe not necessary. 
        pass