import cv2
import os
import logging

UPLOAD_DIR = "uploaded_files"
file_name = "uploaded_file.yaml"
yaml_file_path = os.path.join(UPLOAD_DIR, file_name)
data = {}
image_path = os.path.join(UPLOAD_DIR, 'uploaded_file.jpg')

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

# since the Yaml_parameter class is not in the correct format, 
# it needs to be processed into the correct format
def process_yaml_string(yaml_string: str) -> str:
    """Builds the content of the yaml file based on the input received from the frontend

    Args:
        yaml_string (str): The string containing the parameter data from the frontend

    Returns:
        _type_: A string representing the parameters in a format which is ready to write it into the yaml file
    """
    global file_name, yaml_file_path, data, image_path

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
    logger.info(f'name of yaml file set to {file_name}')
 
    setImagePath(base_name)
   
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


    
def setImagePath(basename: str) -> None:
    """Sets the image path based on the basename

    Args:
        basename (str): _description_
    """
    global image_path
    for ext in ['.jpg', '.png']:
        name = "".join([basename, ext])
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(path):
            logger.info(f'image path set to {path}')
            image_path = path
            
def convertWithoutNegate(thresh) -> None:
    """converts the uploaded jpg or png picture into a pgm picture. Used if negate is false

    Args:
        thresh (_type_): The threshold used by cv2.threshold function. 
        Ranges from 0 to 255. The higher, the more pixels are converted to black pixels
        
    Returns:
        bool: True if creation was successful, False otherwise 
    """
    input_file = data.get('image')
    base_name, _ = os.path.splitext(data.get('image'))
    output_file = base_name + '.pgm'
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) 
    logger.info(f'Image read from imread: {img is not None}')
    
    if img is None:
        logger.error(f"Failed to load image {input_file}")
        return
    
    # Save the image in PGM format
    output_path = os.path.join(UPLOAD_DIR, output_file)
    logger.info(f'Attempting to write image to {output_path}')
    
    # Apply binary threshold
    _, binary_img = cv2.threshold(img, thresh=thresh, maxval=255, type=cv2.THRESH_BINARY)

    # TODO: Check if pgm needs to be processed wrt mode and negate or if this happens directly in ros!
    success = cv2.imwrite(output_path, binary_img)
    
    if success:
        logger.info(f'Successfully wrote image to {output_path}')
        return True
    else:
        logger.error(f'Failed to write image to {output_path}')
        return False